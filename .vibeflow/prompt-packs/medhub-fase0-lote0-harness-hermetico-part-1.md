> You are only seeing this prompt; there is no context outside it.

# Prompt-pack — medhub Fase 0 · Lote 0 · Part 1: hooks e pre-commit não escrevem nem pulam

Repo: `C:/Users/daanm/medhub` (Python 3.12 do sistema, SQLite `ipub.db` local, Windows + Git Bash). Você é o agente de implementação deste repo e roda o loop vibeflow (`implement` → `audit`). Spec de origem (ai-eng): `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-1.md`. Todos os trechos abaixo foram copiados do código em 2026-10-10 (`6d0239a`). Releia cada arquivo no disco antes de editar: outro agente commita neste repo em paralelo (o tique do hub).

---

## 1. Objective + Definition of Done

**Objective.** O boot deixa de regravar o plano do dia já gravado, o pre-commit roda a suíte em todo commit que toca código, dado versionado ou norma (e nunca pula os checks "sempre"), e nenhum arquivo que o harness escreve fica rastreado pelo git.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: o boot que apaga a intenção declarada do dia, o commit que sai "Aprovado!" sem suíte e o resíduo de log que suja a árvore a cada commit. Nenhuma fricção virtuosa é tocada.

**DoD** (testes 1–4 no arquivo novo `tools/test_harness_hermetico.py`, escritos ANTES do fix e vistos vermelhos):

1. [ ] **Boot grava no máximo uma vez por dia.** `test_boot_nao_regrava_plano_do_dia`: com `ipub.db` sintético em `tmp_path` cuja `plano_dia` tem linha de `date.today().isoformat()`, o argv que o hook passa ao `subprocess.run` do day_plan contém `--no-persist`; sem linha de hoje, não contém; banco ausente ou sem a tabela → contém.
2. [ ] **Gatilho por prefixo.** `test_gatilho_da_suite_por_prefixo` sobre a função pura nova `auto_check.dispara_suite_por_caminho(arquivos)`: `True` para `core/hub_quadro.json`, `core/templates/hub.html`, `artifacts/aula-rd-x.html`, `app/utils/areas.py`, `.claude/commands/revisar.md`, `.agents/workflows/curar-cards.md`, `tools/x.py`, `pytest.ini`, `conftest.py`, `requirements.txt`; `False` para `history/session_223.md`, `.vibeflow/specs/x.md`, `docs/x.md`, `resumos/GO/X.md`, `ROADMAP.md` e `[]`.
3. [ ] **`main()` usa o gatilho, conta deleções e nunca pula os "sempre".** `test_staged_core_json_roda_a_suite` (in-process; monkeypatch em `auto_check.run_command`, `auto_check.get_staged_files`, no leitor novo de deletados, `auto_check._ledger_record`, `auto_check.card_watermark_mudou`, `auto_check.card_watermark_selar`): staged = `["core/hub_quadro.json"]` → `run_command` recebe `[sys.executable, "-m", "pytest", "tools/", "-q"]`; só a deleção staged de `tools/x.py` → idem; staged = `["docs/x.md"]` → a suíte NÃO roda, a saída não contém `Nenhum arquivo crítico` e o relatório final lista `Assinatura canonica de CLI (D5)` e `Clausula normativa com terminal (1.10)`.
4. [ ] **Runtime do harness fora do git.** `test_runtime_do_harness_fora_do_git`: para os 2 caminhos de `ledger_self._paths()` e para `state_utils.WATERMARK_PATH`, `git ls-files --error-unmatch -- <p>` sai ≠ 0 e `git check-ignore -q -- <p>` sai 0. `history/ledger_self.jsonl` e `history/card_watermark.json` saem do índice com `git rm --cached` (conteúdo fica no disco).
5. [ ] **Verificação contra o artefato real** (read-only, cole a saída no audit): (a) logo depois do commit desta parte, `git status --porcelain` não lista `history/ledger_self.jsonl` nem `history/card_watermark.json`; (b) num dia que já tem plano, `SELECT COUNT(*), MAX(criado_em) FROM plano_dia WHERE data = date('now','localtime')` (conexão `mode=ro`) devolve o mesmo par antes e depois de `python tools/hooks/memory_boot.py`.
6. [ ] **Suíte completa verde:** `python -m pytest tools/ -q`; o número (1509 + novos) é o que o pre-commit mede no selo (F136), nunca digitado.
7. [ ] **Craftsmanship:** nenhuma violação dos Don'ts de `.vibeflow/conventions.md` (seção 4 abaixo); `test_harness_hermetico.py` no `python_files` do `pytest.ini` com parágrafo de justificativa; texto que descrevia o mecanismo antigo diz a verdade (`ledger_self.py` docstring "versionado" → local; comentário da linha 63 do `.gitignore`; comentário do gatilho do check 4 no `auto_check.py`); o docstring do teste 4 declara o limite ("prova os 3 caminhos conhecidos; não prova que não exista um 4º escritor — o DoD 5a cobre isso empiricamente").

---

## 2. Anti-scope

- Não mexer em `tools/day_plan.py` (nem flag nova, nem `persistir_plano`). A decisão "gravar ou não" mora no hook.
- Nada que mude conteúdo clínico (`resumos/`, cards, questões), FSRS (`app/utils/fsrs*.py`, `record_review`, `fsrs_revlog`) ou o hub publicado (`core/templates/*`, Artifact).
- Não mudar a severidade de nenhum check (BLOCK/WARN) — é outra parte.
- Não mexer em `tools/reachability_check.py` (outra parte), nem em `selo.py`, `setup_hooks.py` ou no hook instalado em `.git/hooks/`.
- Não isolar ledger/watermark dentro da suíte via `conftest.py` — outra parte.
- Não des-rastrear `history/exchange-log.jsonl` nem `history/generation_log.jsonl` (escritos por hooks de sessão e writers, não pelo commit).
- Não reescrever histórico do git. Não escrever fora do repo medhub.

## 3. Budget

**Máximo 6 arquivos editados/criados:** `tools/hooks/memory_boot.py`, `tools/auto_check.py`, `tools/ledger_self.py` (só docstring), `.gitignore`, `tools/test_harness_hermetico.py` (novo), `pytest.ini`. **Mais 2 des-rastreados** por `git rm --cached` (`history/ledger_self.jsonl`, `history/card_watermark.json`), conteúdo intacto no disco.

---

## 4. Project patterns to follow

### 4.1 `.vibeflow/conventions.md` (linhas copiadas verbatim; seções aparadas ao que vale para esta parte)

```markdown
## Language
- All user-facing text, comments, variable names, and UI labels: **Portuguese (pt-BR)**
- Code identifiers (function names, column names, class names): pt-BR or English, both acceptable
- All agent workflow/skill/contract files: pt-BR

## File naming
- tools/scripts: `snake_case.py` — e.g. `insert_questao.py`, `card_checks.py`
- Tests: `tools/test_<alvo>.py`, and the filename must be added to `python_files` in `pytest.ini` to be collected

## Database access
- **Only `app/utils/db.py` may use `import sqlite3`** — no other module in `app/`
- All queries go through functions in `db.py` that return `pd.DataFrame` or plain dicts
- DB path resolved relative to repo root: `os.path.join(os.path.dirname(...), 'ipub.db')`
- Always close connections: explicit `conn.close()` after every `pd.read_sql` or cursor block
- Use `conn.commit()` before `conn.close()` on write operations
- Exception: standalone CLIs in `tools/` open their own connection directly

## Sensors (WARN-first)
- Sensors DETECT and report; they never correct, never block, never write
- A sensor that cannot judge something stays silent about it (out-of-repo refs, globs, placeholders) —
  honest silence beats fake coverage, and false positives are how a sensor gets ignored

## CLI tools (tools/)
- All scripts are invokable as `python tools/<script>.py --arg value`
- `finally: if conn: conn.close()` — always close on exception
- Destructive tools need a `--dry-run` and must be idempotent

## Agent sessions
- Boot: read `AGENTE.md` first, then `ESTADO.md`. The day-plan is injected by the `SessionStart`
  hook — **do not re-run `tools/day_plan.py` by hand**

## Git / commits
- Session commits: `sessao NNN: <one-line description>`
- Tool commits: `chore: <description>`
- `ipub.db`: NOT committed (local only, in .gitignore)

## Don'ts
- Do NOT use `import sqlite3` outside `app/utils/db.py` (only exception: standalone CLIs in `tools/`)
- Do NOT hand-edit anything under `.agents/skills/` — regenerate with `tools/sync_skills.py`
- Do NOT reference an MCP server that is not in `.mcp.json` (today only `pubmedmcp`)
- Do NOT delete source PDFs — the "Zero PDF" policy was reverted in s086
- Do NOT commit `ipub.db` or `medhub_memory.db`
- Do NOT re-run `tools/day_plan.py` at boot — the hook already did it

## Hotfix traces — what `reproduction` and `status` mean here (decided s177, 2026-09-11)
- **`reproduction`** records how the RED test was reproduced. In MedHub `synthetic` is the
  **rule, not a weakness**: suites never touch the real `ipub.db` (the writer-allowlist discipline,
  F49 — a suite that writes to the production db is itself a defect, see F96 for the same lesson
  about production logs).
- **`status`** records whether the fix is verified. `verified` requires all three:
  1. a regression test written **before** the fix, red then green;
  2. the full suite green and the harness gate clean;
  3. **post-fix verification against the real artifact**, read-only, written into the `DoD`.

## Pergunta obrigatória em toda spec (F110, s185)
> **Que fricção esta spec remove -- e ela é virtuosa ou viciosa?**
```

### 4.2 `.vibeflow/patterns/warn-first-check.md` (trecho)

```markdown
1. **A regra mora num módulo próprio, testável** (`doc_drift.py`, `ledger_self.py`,
   função `check_*` pura) — o `auto_check` só orquestra.
3. **Parse/execução defensivos**: sem dados → silêncio (nunca falso-positivo
   barulhento); entrada malformada → WARN de sintaxe, nunca crash; sensor
   indisponível → WARN visível (nunca silêncio que mascare sensor quebrado).
## Anti-patterns
- Swallow silencioso de exceção do próprio sensor (falsa segurança).
- Lógica da regra dentro do `auto_check` (deve morar no módulo/gerador).
```

### 4.3 `AGENTE.md` (régua que vale aqui)

- §10.1 **Reler antes de escrever** — releia `.gitignore`, `pytest.ini` e `auto_check.py` no disco antes de editar; o outro agente pode ter commitado no meio.
- §10.6 **Régua do hotfix** — defeito reproduzível = teste de regressão escrito ANTES do fix, visto vermelho, depois verde.
- §3.1 **Número só com o comando** — o `suite **N**` do HANDOFF é o que o pre-commit mede no commit do selo (F136); nunca digitar.

### 4.4 Precedentes de teste deste repo (copiar o estilo)

Teste de função pura de gatilho — `tools/test_selo_suite.py:8-21`:
```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import auto_check  # noqa: E402


def test_handoff_staged_dispara_a_suite():
    assert auto_check.dispara_suite_por_selo(["HANDOFF.md"]) is True
    assert auto_check.dispara_suite_por_selo(["AUDITORIA_MEDHUB.md", "history/session_201.md"]) is False
    assert auto_check.dispara_suite_por_selo([]) is False
```

Carregar o hook de boot por caminho — `tools/test_plano_dia.py:328-337`:
```python
def _hook_de_boot():
    """O hook nao e pacote importavel: carrega por path (mesmo padrao do F102)."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "memory_boot_s189", Path(day_plan.__file__).parent / "hooks" / "memory_boot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
```
(Atenção: o módulo do hook faz `os.chdir(PROJECT_ROOT)` no import — use `monkeypatch.chdir` ou restaure o cwd se o seu teste depender dele. No seu arquivo, troque `Path(day_plan.__file__).parent` por `ROOT / "tools"`.)

Monkeypatch de função do hook — `tools/test_plano_dia.py` (`test_boot_entrega_o_panorama`):
```python
    mb = _hook_de_boot()
    monkeypatch.setattr(mb, "_memory_context", lambda: "")
    monkeypatch.setattr(mb, "_day_plan_summary", lambda: "- plano")
```

Invariante "está no .gitignore" — `tools/test_emed_api.py:400-402`:
```python
def test_token_do_repo_esta_no_gitignore():
    r = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", ".emed_token"])
    assert r.returncode == 0
```

Importar o `auto_check` e silenciar stdout — `tools/test_auto_check_watermark.py:17-23,45-47`:
```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_check as ac  # noqa: E402

def _silencioso(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)
```

### 4.5 Formato do `pytest.ini` (cabeçalho + uma entrada vizinha)

```ini
[pytest]
; Harness minimo (F12, engenharia-ledger part-4).
...
testpaths = tools
...
; test_selo_suite (s201, F136): HANDOFF staged dispara a suite completa no pre-commit e o numero
;   declarado (`suite **N**` / `SUITE VERMELHA P/T`) tem de ser o medido ali -- a s200 selou 1119/1120
;   com o HANDOFF dizendo 1120. Funcoes puras do auto_check; sem banco.
...
python_files = test_hub_pendencias.py test_dia_logico.py test_selo_rotacao.py ...
```
Regra: um parágrafo `; test_<nome> (<origem>): <o que trava>` antes da linha `python_files`, e o nome do arquivo acrescentado à lista `python_files` (linha única; os mais novos entram no começo).

---

## 5. References (o que casar)

- Gatilho puro existente — `tools/auto_check.py:381-383`:
```python
def dispara_suite_por_selo(arquivos):
    """HANDOFF no recorte = commit de selo -> suite completa (F136). PURA."""
    return any(f.replace("\\", "/") == "HANDOFF.md" for f in arquivos)
```
  A função nova `dispara_suite_por_caminho(arquivos)` segue o mesmo formato (PURA, normaliza `\\` → `/`).
- Leitura `sqlite3` read-only dentro de `tools/` — `tools/utils/state_utils.py:31-47`:
```python
def card_watermark_atual(db_path=None):
    """Tripla do estado atual do dado, ou None se o banco esta inacessivel."""
    import sqlite3
    dbp = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
    try:
        con = sqlite3.connect(f"file:{dbp.as_posix()}?mode=ro", uri=True)
        try:
            row = con.execute(
                "SELECT COALESCE(MAX(id), 0), COUNT(*), COALESCE(MAX(card_version), 0) "
                "FROM flashcards").fetchone()
        finally:
            con.close()
        return {"max_id": row[0], "count": row[1], "max_version": row[2]}
    except Exception as e:
        ...
        return None
```
  Atenção: `sqlite3.connect("file:...?mode=ro", uri=True)` sobre arquivo inexistente levanta erro (não cria o banco) — é o comportamento desejado para "banco ausente → `--no-persist`".
- Schema de `plano_dia` (para o banco sintético do teste 1) — `tools/day_plan.py:1275-1288` (igual em `tools/init_db.py:198-210`):
```sql
CREATE TABLE IF NOT EXISTS plano_dia (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    data               TEXT NOT NULL,
    ordem              INTEGER NOT NULL,
    task_tipo          TEXT NOT NULL,
    alvo_tema          TEXT,
    volume_planejado   INTEGER NOT NULL DEFAULT 0,
    tempo_h            REAL,
    energia            TEXT,
    defaults_assumidos INTEGER NOT NULL DEFAULT 0,
    criado_em          TEXT NOT NULL
)
```
- Por que o boot não pode virar `--no-persist` sempre — `tools/day_plan.py:25-29` (docstring) e `:1617-1626`:
```python
"""...
Escritas (únicas, ambas de metadado de processo): a condição declarada do dia
(condicao_dia via db.registrar_condicao_dia) e o PLANO recomendado do dia
(plano_dia via persistir_plano — spec telemetria-estudo-part-1; o realizado já
vive em fsrs_revlog/review_log/sessoes_bulk, o planejado agora sobrevive para a
aderência planejado×real). Todo o resto permanece read-only; --no-persist simula.
"""
...
    p = build(tempo_h=args.tempo, energia=args.energia)
    # Persistência SÓ no caminho que renderiza o plano do dia (default/--json):
    # os modos de relatório (--handoff-block/--review-plan/--difficulty) retornam
    # antes e NÃO regravam — o handoff-block no fechamento rodaria com defaults e
    # sobrescreveria a intenção declarada de manhã (--tempo/--energia), corrompendo
    # a série de aderência da part-2.
    if not args.no_persist:
        persistir_plano(p)
```
  `build()` usa `hoje = date.today()` (`day_plan.py:894`) e grava `"data": hoje.isoformat()` — o hook usa o mesmo `date.today()`.

---

## 6. Where to work

### 6.1 `tools/hooks/memory_boot.py` (trechos atuais)

```python
# Navega para project root: tools/hooks/memory_boot.py → tools/hooks → tools → MedHub/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

_DAY_PLAN_TIMEOUT = 8   # segundos; o boot nunca depende da saúde do day_plan
_DAY_PLAN_MAX_LINES = 40     # s190: era 8 -- as métricas do panorama moram depois da 8a linha
_PANORAMA_MAX_LINES = 30
_CMD_DAY_PLAN = "python tools/day_plan.py --no-persist"
_CMD_PANORAMA = "python tools/plano.py --panorama"
...
def _day_plan_summary() -> str:
    """Resumo do Plano do Dia por subprocess isolado; fallback silencioso."""
    try:
        r = subprocess.run(
            [sys.executable, "tools/day_plan.py"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=_DAY_PLAN_TIMEOUT, cwd=str(PROJECT_ROOT),
        )
        if r.returncode != 0:
            return ""
        return _resumir_plano(r.stdout, _DAY_PLAN_MAX_LINES)
    except Exception:
        return ""
```
O que fazer: acrescentar `_plano_de_hoje_existe(db_path=None) -> bool` (consulta `SELECT 1 FROM plano_dia WHERE data = ? LIMIT 1` com `date.today().isoformat()`, `mode=ro`; qualquer exceção → trate como "existe", para cair em `--no-persist`) e montar o argv do day_plan a partir dele (função pequena e testável, ex. `_argv_day_plan(db_path=None) -> list`). `_day_plan_summary` passa a usar esse argv. Comentário no helper: "mesmo `date.today()` de `day_plan.build()` (day_plan.py:894); se o build migrar para o dia lógico, acompanhar". Não mexer no resto do hook (`_CONTRATO`, panorama, memória, drift).

### 6.2 `tools/auto_check.py` (trechos atuais)

Imports — linhas 17-31:
```python
sys.path.insert(0, str(ROOT_DIR))
from tools.utils.git_utils import get_changed_files, get_staged_files
from tools.utils.state_utils import (
    _ledger_record,
    _warn_total,
    card_watermark_atual,
    card_watermark_mudou,
    card_watermark_selar,
    check_session_pointer,
    ...
)
```

Classificação e early-return — linhas 507-589:
```python
    if mode in ("--changed", "--staged"):
        changed_files = get_staged_files() if mode == "--staged" else get_changed_files()
        if changed_files is None:
            mode = "--all"
            ...
        else:
            origem = "staged para commit" if mode == "--staged" else "modificado(s)/untracked na sessão"
            print(f"🔍 Detectados {len(changed_files)} arquivo(s) {origem}.")
            selo_relevant = dispara_suite_por_selo(changed_files)
            for f in changed_files:
                fp = f.replace("\\", "/")
                ...
                # F44 (s159): SUBSTRATO COMPARTILHADO. ...
                if (fp.startswith("tools/utils/") or fp.startswith("core/contracts/")
                        or fp in ("pytest.ini", "conftest.py")):
                    substrato_relevant = True
                # Load balancer FSRS (check 2c): ...
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

            # part-6: gatilho por WATERMARK DE DADO — ...
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
```

Check 4 — linhas 636-655:
```python
    #     Gatilho: --all, qualquer .py de tools/core tocado, substrato
    #     compartilhado (tools/utils/, core/contracts/, pytest.ini, conftest.py)
    #     ou fsrs_relevant (F61: cobre a revisao-calibrada via bridge e a
    #     autonomia via coleta nativa — as execuções diretas morreram).
    #     Custo medido: ~17s. Barato demais para continuar sendo opcional.
    if mode == "--all" or tools_to_check or substrato_relevant or fsrs_relevant or selo_relevant:
        desc_pytest = "Suíte completa (pytest — inclui revisão-calibrada via bridge e autonomia)"
        ...
        success_pt, out_pt = run_command([sys.executable, "-m", "pytest", "tools/", "-q"],
                                         desc_pytest, capture=selo_relevant)
```

Selo do watermark — linhas 910-913 (gravação em arquivo rastreado hoje):
```python
    # part-6: sela o marco SO depois que os checks de card rodaram — uma
    # corrida interrompida antes daqui nao avanca o watermark.
    if card_relevant:
        card_watermark_selar(card_watermark_atual())
```

Um check "sempre" (para você saber o que fica depois do antigo early-return) — linhas 989-1004:
```python
    desc_f38 = "Persistencia de erro analisado (F38)"
    orfaos = check_erros_orfaos()
    ...
    results_summary.append((desc_f38, True, len(orfaos) if orfaos else 0))
    _ledger_record("erros_orfaos",
                   [{"alvo": d, "payload": {"erros_esperados": n}} for d, n in (orfaos or [])])
```
O relatório final (linhas ~1281-1299) imprime cada `desc` de `results_summary` — os nomes `Assinatura canonica de CLI (D5)` e `Clausula normativa com terminal (1.10)` são os `desc` dos checks 26 e 29.

O que fazer: (i) `dispara_suite_por_caminho(arquivos)` PURA ao lado de `dispara_suite_por_selo`, com as constantes de prefixo/arquivos num lugar só e um docstring que declara o limite (resumos/docs/.vibeflow/history não disparam); (ii) um leitor de deletados staged, ex. `_staged_deletados()` usando `git_utils._git_files(["diff", "--cached", "--name-only", "-z", "--diff-filter=D"])`, chamado só no modo `--staged`; (iii) no bloco de classificação, calcule `suite_por_caminho = dispara_suite_por_caminho(changed_files + deletados)` e some à condição do check 4; (iv) troque o early-return por uma linha verdadeira (ex.: `↳ Suíte não exigida para este recorte (sem código, dado versionado ou norma); checks "sempre" seguem.`) **sem `return`**; (v) atualize o comentário do check 4.

### 6.3 `tools/utils/git_utils.py` (não editar; só usar)

```python
def _git_files(args):
    """Roda `git -c core.quotepath=false <args>` (com -z) e devolve lista de paths. ..."""
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

def get_staged_files():
    """Apenas o que esta staged para o commit (ACMR). Quotepath-safe.
    --diff-filter=ACMR exclui delecoes (D) para nao auditar arquivo removido.
    """
    staged = _git_files(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"])
    ...
```

### 6.4 Quem grava em arquivo rastreado no commit (não editar código; só des-rastrear)

`tools/utils/state_utils.py:8-17,66-75`:
```python
# Ledger-of-self: import resiliente — sem o modulo, a deteccao segue intacta.
try:
    sys.path.insert(0, str(ROOT_DIR / "tools"))
    from ledger_self import record as _ledger_record
except Exception:
    def _ledger_record(check, findings, root=None):
        pass

# --- Constantes de path ---
WATERMARK_PATH = ROOT_DIR / "history" / "card_watermark.json"
...
def card_watermark_selar(atual, marco_path=None):
    """Persiste o marco — chamar SO depois que os checks de card rodaram."""
    ...
    mp = Path(marco_path) if marco_path else WATERMARK_PATH
    ...
        mp.write_text(json.dumps(atual), encoding="utf-8")
```

`tools/ledger_self.py:1-17,32-40,65-68` (docstring a corrigir nas linhas 5-9):
```python
"""Ledger-of-self: memoria estruturada dos WARNs do harness (degrau 2 da auto-evolucao).

Os checks do auto_check ja DETECTAM inconsistencias; este modulo faz os achados
sobreviverem ao stdout: cada um vira evento com fingerprint, recorrencia e ciclo
de vida (opened -> resolved -> reopened). Dois artefatos, contratos distintos:

  history/ledger_self.jsonl        -- eventos de TRANSICAO, append-only, versionado
  history/ledger_self_state.json   -- estado corrente DERIVADO (occurrences,
                                      last_seen), reescrito a cada run; nao versionado
...
"""
ROOT_DIR = Path(__file__).parent.parent.resolve()
JSONL_NAME = "ledger_self.jsonl"
STATE_NAME = "ledger_self_state.json"


def _paths(root=None):
    root = Path(root).resolve() if root else ROOT_DIR
    hist = root / "history"
    return hist / JSONL_NAME, hist / STATE_NAME
...
def _append_event(jsonl_path, evento):
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
```

`.gitignore:55-74` (atual):
```gitignore
# Artefatos — backups e runs LLM (binários e JSONs grandes)
artifacts/backups/
artifacts/llm_runs/
artifacts/audits/
...
# ledger-of-self: estado DERIVADO (reconstruivel); o .jsonl de eventos e versionado
history/ledger_self_state.json
# sink de falha da consolidacao de memoria (AGENTE.md §8): log de RUNTIME, nao artefato.
# O painel de DIVIDA le o arquivo no disco -- versionar so propagaria ruido de maquina.
history/memory_errors.log
...
```
O que fazer: acrescentar `history/ledger_self.jsonl` e `history/card_watermark.json` no bloco do ledger-of-self, com o comentário corrigido ("runtime do harness: local, fora do git — gravado DEPOIS do stage, sujava a árvore a cada commit"); depois `git rm --cached history/ledger_self.jsonl history/card_watermark.json` no mesmo commit.

### 6.5 O hook instalado (contexto; não editar)

`.git/hooks/pre-commit` = `HOOK_CONTENT` de `tools/setup_hooks.py:18-32`:
```sh
#!/bin/sh
...
python -X utf8 tools/auto_check.py --staged
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ COMMIT BLOQUEADO pelo Harness Autônomo!"
    ...
    exit 1
fi
echo "✅ Validação autônoma pré-commit aprovada!"
exit 0
```

---

## 7. Directional guidance

Deliver what the spec asks, at the scope it defines. Make routine judgment calls yourself; check in only when different readings would lead to materially different work. If the spec seems mistaken, say so in a sentence and continue as specified. Finish the whole task, and stop short of changes clearly beyond it.

Notas de execução:
- Ordem: escreva os 4 testes, rode e veja-os vermelhos (`python -m pytest tools/test_harness_hermetico.py -q`), só então o fix.
- No teste 3, o `main()` lê `sys.argv` — use `monkeypatch.setattr(sys, "argv", ["auto_check.py", "--staged"])`. `run_command` substituído deve devolver `(True, "")`. Os sensores "sempre" rodam de verdade sobre o repo, em leitura; o que grava (`_ledger_record`, `card_watermark_selar`) tem de estar substituído no namespace do `auto_check`.
- Se, ao reler, algum trecho acima não bater com o disco (o tique commita em paralelo), siga o disco e diga em uma frase no audit.

## 8. How to run and test

## How to validate
1. Run tests:
   - `python -m pytest tools/test_harness_hermetico.py -q` (vermelho antes do fix, verde depois)
   - `python -m pytest tools/test_selo_suite.py tools/test_plano_dia.py tools/test_auto_check_watermark.py tools/test_ledger_self.py tools/test_memory_boot_drift.py -q`
   - `python -m pytest tools/ -q` (suíte completa; ~210 s)
2. Verify manually:
   - `git ls-files history/ledger_self.jsonl history/card_watermark.json` → vazio; `git check-ignore -v history/ledger_self.jsonl history/card_watermark.json` → as duas regras.
   - Faça o commit desta parte (o pre-commit roda a suíte porque o recorte tem `tools/`); logo depois, `git status --porcelain` → nenhum dos dois arquivos aparece.
   - Num dia que já tem plano: `python -c "import sqlite3;c=sqlite3.connect('file:ipub.db?mode=ro',uri=True);print(c.execute(\"SELECT COUNT(*),MAX(criado_em) FROM plano_dia WHERE data=date('now','localtime')\").fetchone())"` antes e depois de `python tools/hooks/memory_boot.py > NUL` → mesmo par.

## 9. Docs to update

- `pytest.ini`: parágrafo `; test_harness_hermetico (Fase 0 Lote 0 part-1, /ai-eng 10/10): ...` + nome no `python_files`.
- `tools/ledger_self.py`: docstring (o `.jsonl` deixa de ser versionado).
- `.gitignore`: comentário do bloco ledger-of-self.
- `tools/auto_check.py`: comentário do check 4 (gatilho por prefixo + deleção) e a linha que substitui o early-return.
- `HANDOFF.md`: o `suite **N**` novo vem do pre-commit no selo (F136), não digitado.
- Depois do audit PASS (fora do budget desta parte): registrar em `.vibeflow/conventions.md` (via `/vibeflow:teach`) que o runtime do harness (`history/ledger_self*.json*`, `history/card_watermark.json`) é local e fica fora do git.
