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

# Utilitários extraídos para coesão (Graphify Missão 3)
sys.path.insert(0, str(ROOT_DIR))
from tools.utils.git_utils import get_changed_files, get_staged_files
from tools.utils.state_utils import (
    _ledger_record,
    _warn_total,
    card_watermark_atual,
    card_watermark_mudou,
    card_watermark_selar,
    check_session_pointer,
    check_posicao_drift,
    check_handoff_len,
    check_erros_orfaos,
    check_suites_orfas
)
def run_command(cmd_list, desc, capture=False):
    # part-1 (P1): tempo por bloco IMPRESSO -- o SLO do harness e informativo e medido,
    # nao um gate flaky por tempo. E o que habilita podar custo com dado (F61 foi achado assim).
    import time as _time
    t0 = _time.monotonic()
    print(f"\\n[AUTO-CHECK] Executando: {desc}")
    print(f"            $ {' '.join(cmd_list)}")
    if capture:
        # Captura + eco: preserva a saída na tela E devolve o texto para que o
        # relatório final possa distinguir WARN de BLOCK (sem reimplementar a regra).
        res = subprocess.run(cmd_list, cwd=ROOT_DIR, capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        if res.stdout:
            print(res.stdout, end="" if res.stdout.endswith("\\n") else "\\n")
        if res.stderr:
            print(res.stderr, end="" if res.stderr.endswith("\\n") else "\\n")
        print(f"            [{_time.monotonic() - t0:.1f}s] {desc}")
        return res.returncode == 0, res.stdout or ""
    res = subprocess.run(cmd_list, cwd=ROOT_DIR)
    print(f"            [{_time.monotonic() - t0:.1f}s] {desc}")
    return res.returncode == 0, ""


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
    handoff_relevant = (mode == "--all")
    doc_drift_relevant = (mode == "--all")
    card_relevant = (mode == "--all")
    fsrs_relevant = (mode == "--all")
    substrato_relevant = (mode == "--all")

    if mode in ("--changed", "--staged"):
        changed_files = get_staged_files() if mode == "--staged" else get_changed_files()
        if changed_files is None:
            mode = "--all"
            parity_relevant = True
            pointer_relevant = True
            handoff_relevant = True
            doc_drift_relevant = True
            card_relevant = True
            fsrs_relevant = True
            substrato_relevant = True
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
                # Condicao B1 (BLOCKING): so o proprio HANDOFF muda o tamanho dele.
                if fp == "HANDOFF.md":
                    handoff_relevant = True
                # Sensor doc-vs-codigo (check 7): relevante se um doc-alvo mudou.
                if fp in ("ROADMAP.md", "HANDOFF.md", "ESTADO.md", "AUDITORIA_MEDHUB.md"):
                    doc_drift_relevant = True
                # Auto-suficiencia de card (check 8): cards vivem no ipub.db (fora
                # do git), entao o gatilho e a maquinaria de autoria/deteccao mudar.
                if fp in ("tools/insert_questao.py", "tools/insert_card_base.py",
                          "tools/card_self_sufficiency.py", "tools/test_card_self_sufficiency.py",
                          "tools/audit_flashcard_quality.py", "tools/audit_card_atomicity.py",
                          "tools/insert_card_extra.py", "tools/recurate_cards.py",
                          "tools/check_fk_orphans.py",
                          ".claude/commands/estilo-flashcard.md"):
                    card_relevant = True
                # F44 (s159): SUBSTRATO COMPARTILHADO. Modulo de utils, contrato
                # ou config de teste nao tem consumidor local -- por definicao
                # quem depende deles vive noutro arquivo, e o seletor por path
                # nunca alcanca. Foi assim que a s156 moveu LIMITE_HANDOFF para
                # tools/utils/ e quebrou a coleta de test_handoff_teto por 3
                # sessoes com o harness reportando PASSED. Substrato mexeu ->
                # suite COMPLETA, sem tentar adivinhar o consumidor.
                if (fp.startswith("tools/utils/") or fp.startswith("core/contracts/")
                        or fp in ("pytest.ini", "conftest.py")):
                    substrato_relevant = True
                # Load balancer FSRS (check 2c): o caminho de escrita vive em
                # app/, que a classificação abaixo não varre -- daí a flag.
                if fp in ("app/utils/fsrs_balance.py", "app/utils/fsrs.py",
                          "app/utils/db.py", "tools/test_fsrs_balance.py",
                          "tools/fsrs_load.py", "tools/fsrs_queue.py"):
                    fsrs_relevant = True
                path_obj = ROOT_DIR / f
                if not path_obj.exists():
                    continue
                # Classificar
                if fp.startswith("resumos/") and f.endswith(".md"):
                    resumos_to_check.append(f)
                elif (fp.startswith("tools/") or fp.startswith("core/")) and f.endswith(".py"):
                    tools_to_check.append(f)

            # part-6: gatilho por WATERMARK DE DADO — mesmo com zero arquivos
            # staged relevantes, se o ipub.db avancou desde o ultimo check de
            # card, os checks 8/9 ligam. O dado passa a ter gate, nao so o codigo.
            if not card_relevant:
                wm_mudou, _ = card_watermark_mudou()
                if wm_mudou:
                    card_relevant = True
                    print("   ↳ Watermark de dado: ipub.db mudou desde o último check de card — checks de card ligados.")

            if (not resumos_to_check and not tools_to_check and not parity_relevant
                    and not pointer_relevant and not doc_drift_relevant
                    and not card_relevant and not fsrs_relevant
                    and not substrato_relevant):
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

    # 2. Motor Python / Calibração — F61 (descolar part-1): test_revisao_calibrada e
    #    test_autonomia_hooks rodavam DUAS vezes por run (execução direta aqui + de novo
    #    dentro do pytest 2d: a calibrada via test_pytest_bridge, a autonomia por coleta
    #    nativa do pytest.ini). As execuções diretas morreram; a cobertura é do 2d, cujo
    #    gatilho foi AMPLIADO com fsrs_relevant (o gatilho que era só desta seção).
    if mode == "--all" or tools_to_check or fsrs_relevant:
        # 2c. Load balancer do agendamento FSRS (s128). BLOCKING: mexe no
        #     caminho único de escrita do FSRS, então regressão aqui corrompe
        #     a curva. Suíte pura (não depende do db vivo). Fora do pytest.ini
        #     (F43: registro = aqui) -> execução direta é a ÚNICA, não é dupla.
        test_bal = ROOT_DIR / "tools" / "test_fsrs_balance.py"
        if test_bal.exists() and (mode == "--all" or fsrs_relevant):
            desc_bal = "Suíte do load balancer FSRS"
            success_bal, _ = run_command([sys.executable, "tools/test_fsrs_balance.py"], desc_bal)
            all_passed = all_passed and success_bal
            results_summary.append((desc_bal, success_bal, 0))

        # Suíte de telemetria de fila (Part 2): roda quando day_plan mudou (ou --all).
        # Fora do pytest.ini (F43: registro = aqui) -> execução única.
        test_telemetria_path = ROOT_DIR / "tools" / "test_day_plan_telemetria.py"
        if test_telemetria_path.exists() and (mode == "--all" or any("day_plan" in f for f in tools_to_check)):
            cmd_tel = [sys.executable, "tools/test_day_plan_telemetria.py"]
            desc_tel = "Suíte de telemetria de fila (pool x dívida)"
            success_tel, _ = run_command(cmd_tel, desc_tel)
            all_passed = all_passed and success_tel
            results_summary.append((desc_tel, success_tel, 0))

    # 2d. SUITE COMPLETA DO PYTEST (F44, s159). 🔴 BLOCKING.
    #     Ate aqui o harness NUNCA invocava o pytest: rodava ~6 suites
    #     script-style nomeadas a mao e mais nada. Os 300+ testes coletados pelo
    #     `pytest.ini` so executavam se um humano digitasse `pytest` -- ou seja,
    #     o hook de pre-commit deixava passar commit com suite vermelha, e foi
    #     exatamente assim que a quebra de coleta da s156 sobreviveu 3 sessoes
    #     com o relatorio dizendo "Todos os checks passaram".
    #     Gatilho: --all, qualquer .py de tools/core tocado, substrato
    #     compartilhado (tools/utils/, core/contracts/, pytest.ini, conftest.py)
    #     ou fsrs_relevant (F61: cobre a revisao-calibrada via bridge e a
    #     autonomia via coleta nativa — as execuções diretas morreram).
    #     Custo medido: ~17s. Barato demais para continuar sendo opcional.
    if mode == "--all" or tools_to_check or substrato_relevant or fsrs_relevant:
        desc_pytest = "Suíte completa (pytest — inclui revisão-calibrada via bridge e autonomia)"
        motivo = "substrato compartilhado" if substrato_relevant and mode != "--all" else None
        if motivo:
            print(f"   ↳ {motivo} tocado -> suíte completa (o consumidor vive noutro arquivo).")
        success_pt, _ = run_command([sys.executable, "-m", "pytest", "tools/", "-q"],
                                    desc_pytest)
        all_passed = all_passed and success_pt
        results_summary.append((desc_pytest, success_pt, 0))

    # 2b. Suíte do check de auto-suficiência de card (Part 1). BLOCKING como
    #     todo teste de código: valida os detectores por fixtures (não depende
    #     do db vivo). Gate = maquinaria de card mudou (ou --all).
    if card_relevant:
        cmd_css_test = [sys.executable, "tools/test_card_self_sufficiency.py"]
        desc_css_test = "Suíte do check de auto-suficiência de card"
        success_css_test, _ = run_command(cmd_css_test, desc_css_test)
        all_passed = all_passed and success_css_test
        results_summary.append((desc_css_test, success_css_test, 0))

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
            # 'ref' = referência morta em norma viva (modo refs, part-5): o
            # conserto é a norma, não a anotação -- por isso a ação difere.
            tag = {"drift": "DOC_DRIFT", "ref": "DOC_REF"}.get(
                a["tipo"], "DOC_DRIFT_SYNTAX")
            acao = ("Corrigir a norma (ou remover a seção morta)."
                    if a["tipo"] == "ref"
                    else "Reconciliar o doc ou corrigir a anotação.")
            print(f"\n[WARN] {tag}: {a['doc']}:{a['linha']} -- {a['msg']} "
                  f"(regra: {a['regra']}). {acao}")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_drift, True, len(achados_drift)))
        _ledger_record("doc_drift",
                       [{"alvo": f"{a['doc']}:{a['regra']}",
                         "payload": {"tipo": a["tipo"], "msg": a["msg"]}}
                        for a in achados_drift if a["tipo"] != "sensor"])

    # 8. Auto-suficiencia de card (spec auto-suficiencia-card-e-telemetria-fila
    #    Part 1). WARN, não bloqueia: detecta cards não-respondíveis-a-frio
    #    (opcao-anaforico/deitico/pct-fake). A regra mora em card_self_sufficiency.py;
    #    o auto_check só orquestra. Sensor indisponível = WARN visível (nunca
    #    silêncio que mascare sensor quebrado).
    if card_relevant:
        desc_css = "Auto-suficiência de card (CARD_AUTOSUFICIENCIA)"
        try:
            from card_self_sufficiency import run_checks as css_run
            achados_css = css_run()
            sensor_ok = True
        except Exception as e:
            print(f"\n[WARN] CARD_AUTOSUFICIENCIA_SENSOR: sensor indisponível ({e}).")
            achados_css, sensor_ok = [], False
        if achados_css:
            from collections import Counter
            por_padrao = Counter(a["padrao"] for a in achados_css)
            resumo = ", ".join(f"{p}: {n}" for p, n in por_padrao.most_common())
            print(f"\n[WARN] CARD_AUTOSUFICIENCIA: {len(achados_css)} card(s) não "
                  f"auto-suficiente(s) [{resumo}]. Worklist de reforja: "
                  f"python tools/card_self_sufficiency.py --json.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_css, True, len(achados_css) if sensor_ok else 1))
        _ledger_record("card_autosuficiencia",
                       [{"alvo": f"card#{a['id']}", "payload":
                         {"padrao": a["padrao"], "tema": a["tema"]}}
                        for a in achados_css] if sensor_ok
                       else [{"alvo": "sensor", "payload": {}}])

    # 9. Atomicidade de card (s128). WARN, não bloqueia: detecta violação do
    #    minimum information principle -- duplo-ask (a frente cobra duas
    #    respostas, o que torna a nota FSRS ininterpretável) e resposta-multifato
    #    (o verso responde em parágrafo). Mesmo gate do check 8: a maquinaria de
    #    autoria de card mudou. Regra nova nasce WARN (política s106/107).
    if card_relevant:
        desc_atom = "Atomicidade de card (CARD_ATOMICIDADE)"
        try:
            from audit_card_atomicity import run_checks as atom_run
            achados_atom = atom_run()
            sensor_atom_ok = True
        except Exception as e:
            print(f"\n[WARN] CARD_ATOMICIDADE_SENSOR: sensor indisponível ({e}).")
            achados_atom, sensor_atom_ok = [], False
        if achados_atom:
            from collections import Counter
            por_padrao_atom = Counter(a["padrao"] for a in achados_atom)
            resumo_atom = ", ".join(f"{p}: {n}" for p, n in por_padrao_atom.most_common())
            n_cards_atom = len({a["id"] for a in achados_atom})
            print(f"\n[WARN] CARD_ATOMICIDADE: {n_cards_atom} card(s) não atômico(s) "
                  f"[{resumo_atom}]. Worklist: python tools/audit_card_atomicity.py --json. "
                  f"Triar por CRITÉRIOS DE ACERTO (card discriminador é falso-positivo conhecido).")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_atom, True,
                                len(achados_atom) if sensor_atom_ok else 1))
        _ledger_record("card_atomicidade",
                       [{"alvo": f"card#{a['id']}", "payload":
                         {"padrao": a["padrao"], "tema": a["tema"]}}
                        for a in achados_atom] if sensor_atom_ok
                       else [{"alvo": "sensor", "payload": {}}])

    # 10. Integridade referencial + schema do ipub.db (consolidacao part-6).
    #     WARN, não bloqueia: o script existia desde a part-1 mas nunca foi
    #     conectado a harness nenhum (achado D4, "construído-e-nunca-conectado").
    #     Mesmo gate dos checks 8/9 (maquinaria de card mudou OU watermark de
    #     dado avancou): órfão de FK e coluna faltando são defeitos de DADO, e
    #     dado muda fora do git. A regra mora em check_fk_orphans.py (que desde
    #     a part-6 absorveu o schema-check do falecido audit_integrity.py);
    #     o auto_check só orquestra. Sensor indisponível = WARN visível.
    if card_relevant:
        desc_fk = "Integridade referencial + schema (FK_ORPHANS)"
        try:
            from check_fk_orphans import run_checks as fk_run, _detalhe as fk_detalhe
            achados_fk = fk_run()
            sensor_fk_ok = True
        except Exception as e:
            print(f"\n[WARN] FK_ORPHANS_SENSOR: sensor indisponível ({e}).")
            achados_fk, sensor_fk_ok = [], False
        for a in achados_fk:
            print(f"\n[WARN] FK_ORPHANS: {a['alvo']} -- {fk_detalhe(a['payload'])}. "
                  f"Conserto e decisao do operador; o check nao escreve.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_fk, True,
                                len(achados_fk) if sensor_fk_ok else 1))
        _ledger_record("fk_orphans",
                       achados_fk if sensor_fk_ok
                       else [{"alvo": "sensor", "payload": {}}])

    # part-6: sela o marco SO depois que os checks de card rodaram — uma
    # corrida interrompida antes daqui nao avanca o watermark.
    if card_relevant:
        card_watermark_selar(card_watermark_atual())

    # 11. Condicao B1 do reconcile (HANDOFF > 60 linhas). 🔴 BLOCKING de fato
    #     (spec consolidacao-part-4): o contrato ja declarava BLOCKING desde a
    #     s075, mas nao havia check -- excecao deliberada a politica "regra nova
    #     nasce WARN", porque esta regra nao e nova, e a implementacao tardia de
    #     uma regra existente que estava sendo violada sem consequencia (D3/s144).
    if handoff_relevant:
        desc_b1 = "Teto do HANDOFF (B1 do reconcile)"
        estouro = check_handoff_len()
        if estouro:
            print(f"\n[BLOCK] HANDOFF_LONGO (B1): HANDOFF.md tem {estouro[0]} linhas "
                  f"(teto {estouro[1]}). Migrar o excedente narrativo para "
                  f"history/session_NNN.md -- nada se perde, muda de endereco. "
                  f"Norma: core/contracts/reconcile-contract.md B1.")
            all_passed = False
        results_summary.append((desc_b1, not estouro, 0))
        _ledger_record("handoff_teto",
                       [{"alvo": "HANDOFF.md", "payload":
                         {"linhas": estouro[0], "limite": estouro[1]}}] if estouro else [])

    # 12. Alcancabilidade (consolidacao part-6). WARN, não bloqueia. SÓ no --all:
    #     varre o repo inteiro (~90 alvos x ~200 referenciadores) e a pergunta
    #     que ele faz -- "alguem chega aqui?" -- é sobre a ESTRUTURA do repo, que
    #     não muda a cada arquivo tocado. Rodar no --changed seria custo por
    #     ruído. Órfão = construído-e-nunca-conectado (achado D4): código que não
    #     dá erro, só não acontece. Regra em tools/reachability_check.py.
    if mode == "--all":
        desc_reach = "Alcançabilidade de código (REACHABILITY)"
        try:
            from reachability_check import run_checks as reach_run
            achados_reach = reach_run()
            sensor_reach_ok = True
        except Exception as e:
            print(f"\n[WARN] REACHABILITY_SENSOR: sensor indisponível ({e}).")
            achados_reach, sensor_reach_ok = [], False
        if achados_reach:
            nomes = ", ".join(a["alvo"] for a in achados_reach[:5])
            print(f"\n[WARN] REACHABILITY: {len(achados_reach)} arquivo(s) sem "
                  f"referenciador vivo ({nomes}"
                  f"{', ...' if len(achados_reach) > 5 else ''}). "
                  f"Conectar ou aposentar: python tools/reachability_check.py.")
        # success=True: WARN não rebaixa o veredito (não altera all_passed).
        results_summary.append((desc_reach, True,
                                len(achados_reach) if sensor_reach_ok else 1))
        _ledger_record("reachability",
                       achados_reach if sensor_reach_ok
                       else [{"alvo": "sensor", "payload": {}}])

    # 13. Invariante F38 (AUDITORIA_MEDHUB): erro analisado tem que PERSISTIR.
    #     WARN, nao bloqueia. Roda SEMPRE (nao so no --all): o defeito nasce de
    #     uma escrita no db, nao de um arquivo tocado, entao nenhuma heuristica
    #     de relevancia por path o alcanca -- e a varredura e barata (dezenas de
    #     dias-bloco). Guarda de REGRESSAO: nao recupera analise perdida, so
    #     impede que a proxima evapore em silencio como a de 18/06 evaporou.
    desc_f38 = "Persistencia de erro analisado (F38)"
    orfaos = check_erros_orfaos()
    if orfaos:
        amostra = ", ".join(f"{d} ({n} erros)" for d, n in orfaos[:3])
        print()
        print(f"[WARN] ERROS_ORFAOS (F38): {len(orfaos)} dia(s)-bloco com erros em "
              f"sessoes_bulk e ZERO linhas em questoes_erros: {amostra}"
              f"{', ...' if len(orfaos) > 3 else ''}. "
              f"`habilidades.py --add` COMPLEMENTA `insert_questao.py`, nunca o "
              f"substitui -- sem a linha de erro os cards nascem sem ancora "
              f"(questao_id=NULL) e a analise so existe em prosa. "
              f"Norma: AUDITORIA_MEDHUB.md F38.")
    # success=True: WARN nao rebaixa o veredito (nao altera all_passed).
    results_summary.append((desc_f38, True, len(orfaos) if orfaos else 0))
    _ledger_record("erros_orfaos",
                   [{"alvo": d, "payload": {"erros_esperados": n}} for d, n in (orfaos or [])])

    # 14b. Import-dangling nos CLIs (descolar part-2, classe F50): `autopsia_simulados`
    #      ficou 852 linhas QUEBRADO por 5 dias importando módulo deletado, mascarado por
    #      .pyc órfão. AST-only (utf-8-sig — lição do BOM/F51), NUNCA executa os CLIs.
    #      WARN (nasce advertindo, política s106/107); roda sempre — é barato (dezenas de arquivos).
    desc_imp = "Imports internos resolvem (IMPORT_DANGLING)"
    import ast as _ast
    dangling = []
    try:
        for f_py in sorted((ROOT_DIR / "tools").glob("*.py")):
            try:
                tree = _ast.parse(f_py.read_text(encoding="utf-8-sig", errors="replace"))
            except SyntaxError as se:
                dangling.append((f_py.name, f"syntax: {se.msg} (linha {se.lineno})"))
                continue
            for node in _ast.walk(tree):
                mods = []
                if isinstance(node, _ast.Import):
                    mods = [a.name for a in node.names]
                elif isinstance(node, _ast.ImportFrom) and node.module and node.level == 0:
                    mods = [node.module]
                for mod in mods:
                    if not (mod == "tools" or mod.startswith("tools.")):
                        continue
                    sub = mod.split(".", 1)[1] if "." in mod else ""
                    alvo_py = ROOT_DIR / (mod.replace(".", "/") + ".py")
                    alvo_pkg = ROOT_DIR / mod.replace(".", "/")
                    if sub and not alvo_py.exists() and not alvo_pkg.exists():
                        dangling.append((f_py.name, f"import {mod} (módulo inexistente)"))
    except Exception as e:  # noqa: BLE001 -- sensor indisponível é WARN visível
        print(f"\n[WARN] IMPORT_DANGLING_SENSOR: sensor indisponível ({e}).")
        dangling = [("sensor", str(e))]
    if dangling:
        amostra = "; ".join(f"{a}: {b}" for a, b in dangling[:4])
        print(f"\n[WARN] IMPORT_DANGLING: {len(dangling)} problema(s) de import em tools/ "
              f"({amostra}{'; ...' if len(dangling) > 4 else ''}). Morto-que-parece-vivo "
              f"(classe F50): conectar, corrigir ou deletar com lápide.")
    results_summary.append((desc_imp, True, len(dangling)))
    _ledger_record("import_dangling",
                   [{"alvo": a, "payload": {"detalhe": b}} for a, b in dangling])

    # 14. Invariante F43: suite que existe tem que estar em algum registro de
    #     execucao. "Quais testes rodam" e mantido em TRES lugares (pytest.ini,
    #     auto_check, test_pytest_bridge) e nenhum sabe do outro -- uma suite
    #     fora dos tres existe, passa no review e nunca executa. WARN.
    desc_f43 = "Registro de suite de teste (F43)"
    suites_orfas = check_suites_orfas()
    if suites_orfas:
        print()
        print(f"[WARN] SUITES_ORFAS (F43): {len(suites_orfas)} suite(s) em tools/ fora de "
              f"TODOS os registros de execucao ({', '.join(suites_orfas[:4])}"
              f"{', ...' if len(suites_orfas) > 4 else ''}). "
              f"Inscrever em pytest.ini (python_files), no auto_check ou no "
              f"test_pytest_bridge -- existir nao e o mesmo que rodar.")
    results_summary.append((desc_f43, True, len(suites_orfas) if suites_orfas else 0))
    _ledger_record("suites_orfas",
                   [{"alvo": n, "payload": {}} for n in (suites_orfas or [])])

    # PAINEL DE DÍVIDA (descolar part-1, F54/P5): o leitor obrigatório. Imprime SEMPRE
    # (dívida invisível em run verde é exatamente o modo de falha F54). Sensor: detecta
    # e reporta; a drenagem e a promoção WARN->BLOCK seguem a política s106/107 (base zera).
    try:
        from ledger_self import painel_divida
        print()
        for linha in painel_divida():
            print(linha)
    except Exception as e:  # noqa: BLE001 -- painel nunca derruba o harness
        print(f"\n[WARN] PAINEL_DIVIDA: indisponível ({e}).")

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
