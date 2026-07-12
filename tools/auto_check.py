import os
import re
import sys
import subprocess
from pathlib import Path

# Garante compatibilidade nativa de encoding em terminais Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()

# Ledger-of-self (degrau 2 -- spec ledger-auto-instrumentacao): os WARNs dos
# checks viram memoria estruturada. Import resiliente: sem o modulo, a
# deteccao segue intacta (so a memoria se perde).
try:
    from ledger_self import record as _ledger_record
except Exception:
    def _ledger_record(check, findings, root=None):
        pass


def _git_files(args):
    """Roda `git -c core.quotepath=false <args>` (com -z) e devolve lista de paths.

    quotepath=false + split por NUL garante que caminhos acentuados (ex.:
    'resumos/Clínica Médica/...') e com espaços cheguem inteiros, sem aspas
    literais nem escapes octais que fariam o Path().exists() falhar em silêncio.
    """
    cmd = ["git", "-c", "core.quotepath=false"] + args
    try:
        res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True,
                             encoding="utf-8", check=False)
    except Exception as e:
        print(f"[WARN] Falha ao consultar o git ({e}).")
        return None
    if res.returncode != 0:
        return None
    return [p for p in res.stdout.split("\0") if p.strip()]


def get_changed_files():
    """Modificados (working tree vs HEAD) + untracked. Quotepath-safe.

    Usado pelo modo --changed (Reflexo Autônomo do agente: valida a árvore).
    """
    diff = _git_files(["diff", "--name-only", "-z", "HEAD"])
    if diff is None:
        return None
    untracked = _git_files(["ls-files", "--others", "--exclude-standard", "-z"])
    if untracked is None:
        return None
    return sorted(set(diff) | set(untracked))


def get_staged_files():
    """Apenas o que está staged para o commit (ACMR). Quotepath-safe.

    Usado pelo modo --staged (git pre-commit hook: valida só o que será selado).
    --diff-filter=ACMR exclui deleções (D) para não auditar arquivo removido.
    """
    staged = _git_files(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"])
    if staged is None:
        return None
    return sorted(set(staged))

def run_command(cmd_list, desc, capture=False):
    print(f"\n[AUTO-CHECK] Executando: {desc}")
    print(f"            $ {' '.join(cmd_list)}")
    if capture:
        # Captura + eco: preserva a saída na tela E devolve o texto para que o
        # relatório final possa distinguir WARN de BLOCK (sem reimplementar a regra).
        res = subprocess.run(cmd_list, cwd=ROOT_DIR, capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        if res.stdout:
            print(res.stdout, end="" if res.stdout.endswith("\n") else "\n")
        if res.stderr:
            print(res.stderr, end="" if res.stderr.endswith("\n") else "\n")
        return res.returncode == 0, res.stdout or ""
    res = subprocess.run(cmd_list, cwd=ROOT_DIR)
    return res.returncode == 0, ""


def _warn_total(output):
    """Extrai WARN_TOTAL da linha machine-readable do audit_resumos. 0 se ausente."""
    m = re.search(r"WARN_TOTAL=(\d+)", output)
    return int(m.group(1)) if m else 0


def check_session_pointer(handoff_path=None, history_dir=None):
    """Invariante F1 (AUDITORIA_MEDHUB): o ponteiro de sessao do HANDOFF nunca
    excede max(history/session_NNN) + 1. Renumeracao antecipada (+1) e legitima;
    acima disso ha sessao anunciada sem log selado.

    O ponteiro e o maior sNN citado nas linhas-ancora do HANDOFF (header
    "*Atualizado:" e heading "Proximo passo") -- nao no arquivo inteiro, para
    nao capturar mencoes historicas em prosa. Parse defensivo: sem match ou
    sem dados -> None (check silencioso, nunca falso-positivo barulhento).

    Retorna (pointer, max_sess) em drift; None quando coerente ou sem dados.
    """
    handoff = Path(handoff_path) if handoff_path else ROOT_DIR / "HANDOFF.md"
    history = Path(history_dir) if history_dir else ROOT_DIR / "history"
    if not handoff.exists() or not history.is_dir():
        return None
    try:
        text = handoff.read_text(encoding="utf-8")
    except Exception:
        return None
    nums = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("*Atualizado") or (
                s.startswith("#") and re.search(r"pr[oó]ximo passo", s, re.IGNORECASE)):
            nums += [int(n) for n in re.findall(r"\bs(\d{2,3})\b", s)]
    if not nums:
        return None
    sessions = []
    for p in history.rglob("session_*.md"):
        m = re.fullmatch(r"session_(\d+)", p.stem)
        if m:
            sessions.append(int(m.group(1)))
    if not sessions:
        return None
    pointer, max_sess = max(nums), max(sessions)
    if pointer > max_sess + 1:
        return (pointer, max_sess)
    return None


def check_posicao_drift(handoff_path=None, db_path=None):
    """Invariante POSICAO_DRIFT (op-3 / PRD orquestracao part-1): a semana de
    conteudo citada nas linhas-ancora do HANDOFF nao pode divergir da posicao
    SSOT do db (preparacao_estado). Ancoras: header "*Atualizado", heading
    "Proximo passo" e a linha derivada "- **Posicao:**". Semana = S maiusculo
    + 1-2 digitos (sessoes usam s minusculo + 3 digitos; nao colidem).

    Parse defensivo: sem posicao no db, sem HANDOFF ou sem mencao de semana
    nas ancoras -> None (silencio, nunca falso-positivo barulhento).
    Retorna (semana_handoff, semana_db) em drift; None quando coerente.
    """
    handoff = Path(handoff_path) if handoff_path else ROOT_DIR / "HANDOFF.md"
    dbp = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
    if not handoff.exists() or not dbp.exists():
        return None
    con = None
    try:
        import sqlite3
        con = sqlite3.connect(str(dbp))
        row = con.execute(
            "SELECT valor FROM preparacao_estado WHERE chave='semana_conteudo'"
        ).fetchone()
    except Exception:
        return None
    finally:
        if con is not None:
            con.close()
    if not row:
        return None
    try:
        semana_db = int(row[0])
    except (TypeError, ValueError):
        return None
    try:
        text = handoff.read_text(encoding="utf-8")
    except Exception:
        return None
    mencoes = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- **Posicao:**"):
            # linha derivada cita conteudo E nominal -- so a semana de conteudo conta
            mencoes += [int(n) for n in re.findall(r"conteudo\s+S(\d{1,2})\b", s)]
        elif s.startswith("*Atualizado") or (
                s.startswith("#") and re.search(r"pr[oó]ximo passo", s, re.IGNORECASE)):
            mencoes += [int(n) for n in re.findall(r"\bS(\d{1,2})\b", s)]
    if not mencoes:
        return None
    divergentes = [m for m in mencoes if m != semana_db]
    if divergentes:
        return (divergentes[0], semana_db)
    return None

def main():
    mode = "--changed"
    if len(sys.argv) > 1 and sys.argv[1] in ("--all", "-a"):
        mode = "--all"
    elif len(sys.argv) > 1 and sys.argv[1] in ("--staged", "-s"):
        mode = "--staged"
    elif len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Uso: python tools/auto_check.py [--changed | --staged | --all]")
        print("  --changed (padrão): Audita os arquivos modificados/novos na árvore (Reflexo Autônomo do agente).")
        print("  --staged          : Audita apenas os arquivos staged para commit (git pre-commit hook).")
        print("  --all             : Roda auditoria completa (todos os resumos e testes centrais).")
        return 0

    print("=" * 60)
    print("🤖 MEDHUB AUTONOMOUS HARNESS & PROACTIVE LINTER")
    print("=" * 60)

    resumos_to_check = []
    tools_to_check = []
    changed_files = None
    parity_relevant = (mode == "--all")
    pointer_relevant = (mode == "--all")
    doc_drift_relevant = (mode == "--all")

    if mode in ("--changed", "--staged"):
        changed_files = get_staged_files() if mode == "--staged" else get_changed_files()
        if changed_files is None:
            mode = "--all"
            parity_relevant = True
            pointer_relevant = True
            doc_drift_relevant = True
        else:
            origem = "staged para commit" if mode == "--staged" else "modificado(s)/untracked na sessão"
            print(f"🔍 Detectados {len(changed_files)} arquivo(s) {origem}.")
            for f in changed_files:
                fp = f.replace("\\", "/")
                # Paridade command<->skill: relevante se o canônico OU o espelho mudou.
                if fp.startswith(".claude/commands/") or fp.startswith(".agents/skills/"):
                    parity_relevant = True
                # Invariante de ponteiro (F1): relevante se HANDOFF ou history/ mudou
                # (checado antes do exists() para pegar também deleções de logs).
                if fp == "HANDOFF.md" or fp.startswith("history/"):
                    pointer_relevant = True
                # Sensor doc-vs-codigo (check 7): relevante se um doc-alvo mudou.
                if fp in ("ROADMAP.md", "HANDOFF.md", "ESTADO.md", "AUDITORIA_MEDHUB.md"):
                    doc_drift_relevant = True
                path_obj = ROOT_DIR / f
                if not path_obj.exists():
                    continue
                # Classificar
                if fp.startswith("resumos/") and f.endswith(".md"):
                    resumos_to_check.append(f)
                elif (fp.startswith("tools/") or fp.startswith("core/")) and f.endswith(".py"):
                    tools_to_check.append(f)

            if (not resumos_to_check and not tools_to_check and not parity_relevant
                    and not pointer_relevant and not doc_drift_relevant):
                print("\n✅ Nenhum arquivo crítico (resumos/*.md ou scripts python estruturais) foi alterado.")
                print("   O harness não exige execução de suítes de teste para esta mudança. Aprovado!")
                print("=" * 60)
                return 0

            print(f"   ↳ Resumos para auditar: {len(resumos_to_check)}")
            print(f"   ↳ Scripts estruturais para testar: {len(tools_to_check)}")

    all_passed = True
    results_summary = []

    # 1. Auditar Resumos
    if mode == "--all" or resumos_to_check:
        cmd = [sys.executable, "tools/audit_resumos.py"]
        if mode == "--changed" and resumos_to_check:
            cmd.extend(resumos_to_check)
        
        desc = "Linter de Qualidade de Resumos" + (" (Global)" if mode == "--all" else f" ({len(resumos_to_check)} arquivos)")
        success, out = run_command(cmd, desc, capture=True)
        all_passed = all_passed and success
        results_summary.append((desc, success, _warn_total(out)))

    # 2. Auditar Motor Python / Testes de Calibração
    if mode == "--all" or tools_to_check:
        cmd_test = [sys.executable, "tools/test_revisao_calibrada.py"]
        desc = "Suíte Central de Testes (Revisão Calibrada e D10)"
        success, _ = run_command(cmd_test, desc)
        all_passed = all_passed and success
        results_summary.append((desc, success, 0))

        # Se houver teste específico de autonomia
        test_autonomia_path = ROOT_DIR / "tools" / "test_autonomia_hooks.py"
        if test_autonomia_path.exists() and (mode == "--all" or any("autonomia" in f or "hooks" in f for f in tools_to_check)):
            cmd_auto = [sys.executable, "tools/test_autonomia_hooks.py"]
            desc_auto = "Suíte de Testes do Harness de Autonomia e Hooks"
            success_auto, _ = run_command(cmd_auto, desc_auto)
            all_passed = all_passed and success_auto
            results_summary.append((desc_auto, success_auto, 0))

    # 3. Paridade command<->skill (Parte 3). WARN, não bloqueia (warning-first):
    #    a regra de "em sync" mora no gerador; o auto_check só orquestra o --check.
    if parity_relevant:
        ok_parity, out_parity = run_command(
            [sys.executable, "tools/sync_skills.py", "--check"],
            "Paridade command<->skill (sync_skills --check)", capture=True)
        desc_parity = "Paridade command<->skill"
        if ok_parity:
            results_summary.append((desc_parity, True, 0))
            _ledger_record("parity", [])
        else:
            n_drift = out_parity.count("PARITY_DRIFT")
            # success=True: WARN não rebaixa o veredito (não altera all_passed).
            results_summary.append((desc_parity, True, n_drift))
            _ledger_record("parity", [{"alvo": "command<->skill",
                                       "payload": {"n_drift": n_drift}}])

    # 4. Invariante de ponteiro de sessao (F1 -- AUDITORIA_MEDHUB). WARN, não bloqueia:
    #    nasce advertindo (política s106/107) e só endurece quando a base zerar.
    if pointer_relevant:
        drift = check_session_pointer()
        desc_pointer = "Invariante de ponteiro de sessão (F1)"
        if drift:
            print(f"\n[WARN] SESSION_POINTER_DRIFT: HANDOFF aponta s{drift[0]}, mas o log "
                  f"mais recente é history/session_{drift[1]:03d}.md (limite = max + 1). "
                  f"Selar a sessão pendente antes de avançar o ponteiro.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_pointer, True, 1 if drift else 0))
        _ledger_record("session_pointer",
                       [{"alvo": "HANDOFF.md", "payload":
                         {"pointer": drift[0], "max_sess": drift[1]}}] if drift else [])

    # 5. Invariante de posicao SSOT (op-3 -- PRD orquestracao part-1). WARN, não bloqueia:
    #    mesma janela de relevância do ponteiro (HANDOFF no diff ou --all).
    if pointer_relevant:
        pdrift = check_posicao_drift()
        desc_posicao = "Invariante de posição SSOT (POSICAO_DRIFT)"
        if pdrift:
            print(f"\n[WARN] POSICAO_DRIFT: HANDOFF cita S{pdrift[0]}, mas a posição SSOT "
                  f"(preparacao_estado) é S{pdrift[1]}. Corrigir o texto ou atualizar via "
                  f"tools/preparacao.py --set-semana.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_posicao, True, 1 if pdrift else 0))
        _ledger_record("posicao_ssot",
                       [{"alvo": "HANDOFF.md", "payload":
                         {"semana_handoff": pdrift[0], "semana_db": pdrift[1]}}]
                       if pdrift else [])

    # 6. Cobertura de conhecimento -- tema da semana corrente (spec mecanismo-conhecimento
    #    part-3). WARN, não bloqueia: torna visível o tema da semana sem .md canônico.
    #    Silencioso quando coberto ou grade indisponível (degrada, nunca falso-positivo).
    if mode == "--all":
        desc_cob = "Cobertura de conhecimento (tema da semana)"
        try:
            from cobertura_conhecimento import semana_orfaos_correntes
            orfaos_sem, semana_n = semana_orfaos_correntes(str(ROOT_DIR / "resumos"))
        except Exception:
            orfaos_sem, semana_n = [], 0
        if orfaos_sem:
            nomes = ", ".join(x["stem"] for x in orfaos_sem[:5])
            print(f"\n[WARN] COBERTURA_SEMANA: {len(orfaos_sem)} tema(s) da semana S{semana_n} "
                  f"sem .md canônico ({nomes}). Priorizar autoria — fila em "
                  f"tools/cobertura_conhecimento.py.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_cob, True, len(orfaos_sem)))
        _ledger_record("cobertura_semana",
                       [{"alvo": x["stem"], "payload": {"semana": semana_n}}
                        for x in orfaos_sem])

    # 7. Sensor de drift doc-vs-codigo (degrau 1 -- spec sensor-drift-doc-codigo).
    #    WARN, não bloqueia: compara anotacoes drift-check dos docs de estado com
    #    a realidade (codigo/schema/paths). A regra mora em tools/doc_drift.py;
    #    o auto_check só orquestra. Sensor indisponível = WARN visível (nunca
    #    silêncio que mascare sensor quebrado).
    if doc_drift_relevant:
        desc_drift = "Sensor de drift doc-vs-código (DOC_DRIFT)"
        try:
            from doc_drift import run_checks as doc_drift_run
            achados_drift = doc_drift_run(str(ROOT_DIR))
        except Exception as e:
            print(f"\n[WARN] DOC_DRIFT_SENSOR: sensor indisponível ({e}).")
            achados_drift = [{"tipo": "sensor"}]
        for a in achados_drift:
            if a["tipo"] == "sensor":
                continue
            tag = "DOC_DRIFT" if a["tipo"] == "drift" else "DOC_DRIFT_SYNTAX"
            print(f"\n[WARN] {tag}: {a['doc']}:{a['linha']} -- {a['msg']} "
                  f"(regra: {a['regra']}). Reconciliar o doc ou corrigir a anotação.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_drift, True, len(achados_drift)))
        _ledger_record("doc_drift",
                       [{"alvo": f"{a['doc']}:{a['regra']}",
                         "payload": {"tipo": a["tipo"], "msg": a["msg"]}}
                        for a in achados_drift if a["tipo"] != "sensor"])

    # Resumo Final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DO HARNESS AUTÔNOMO")
    print("=" * 60)
    for desc, success, warns in results_summary:
        icon = "✅ PASSED" if success else "❌ FAILED"
        badge = f"  ⚠️ {warns} WARN (não bloqueia)" if warns else ""
        print(f"  {icon} - {desc}{badge}")
    print("=" * 60)

    if all_passed:
        print("\n🎉 Todos os checks passaram! Trabalho validado autônoma e independentemente.")
        return 0
    else:
        print("\n🛑 FALHA DETECTADA! Corrija as inconsistências acima antes de considerar a entrega concluída.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
