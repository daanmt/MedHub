## Audit Report: autogovernanca-proativa-part-1

**Verdict: PASS**

Auditado em 2026-07-04 contra `.vibeflow/specs/autogovernanca-proativa-part-1.md`.
Testes: 5/5 verdes. Critical Gate: limpo (1 WARNING autorizado pela spec).

### DoD Checklist
- [x] **1 — Unwrap do envelope** — `app/memory/inspect.py:136` (`_unwrap`) desembrulha `{"kind","content"}` com fallback plano (`value.get("content", value)`), aplicado a `weak_areas` (`inspect.py:195`) e `workflow_rules` (`inspect.py:203`). Rodado contra o `medhub_memory.db` real: 8 fraquezas com valores reais (`[Cirurgia / Cirurgia Infantil] …`), **zero `[? / ?]`** (verificado via `Select-String`).
- [x] **2 — Dedup + ranking read-side** — `_rank_weak_areas` (`inspect.py:146`): 1 linha por par `(area, especialidade)` via dict `best`; ordenação estável em 3 passos (par asc → `last_updated` desc → `error_count` desc); top-N=8. Duas execuções seguidas → hash idêntico (`DETERMINISTICO: OK`); `n_fraquezas=8`.
- [x] **3 — Boot compacto (memory_boot.py v2)** — `build_context()` (`memory_boot.py:113`) injeta: (a) `_day_plan_summary()` via `subprocess.run` com `timeout=8` + `except` → `""` (fallback silencioso), truncado a 8 linhas; (b) `_drift_flag()` comparando `s NNN` do HANDOFF com o maior `history/session_NNN.md`; (c) `_proximo_passo()` da seção "Próximo passo imediato" do HANDOFF. Confirmado no output end-to-end do hook.
- [x] **4 — Texto-contrato Presença→Expansão** — `_CONTRATO` (`memory_boot.py:100`) é a última seção: manda "abrir OFERECENDO o próximo ato — 'Próximo ato: X — sigo nele salvo redireção'" e devolver o turno, sem executar a sessão. Sempre anexado em `build_context()`.
- [x] **5 — Craftsmanship** — nenhum `import sqlite3` novo no diff (grep `+import sqlite3` → vazio; o único em `inspect.py:73` é pré-existente em `cmd_threads`, fora do diff). `except FileNotFoundError` preservado em `_memory_context()` (`memory_boot.py:35`). Smoke test novo `test_context_unwrap` (`test_memory.py:178`) valida unwrap sobre store temporário e assere ausência de `[? / ?]`. `python tools/test_memory.py` → 5/5.

### Pattern Compliance
- [x] **db-access-layer** — segue corretamente. Acesso a `medhub_memory.db` só via `SQLiteMemoryStore` (`inspect.py:16`); o hook consome `inspect.load_context` + `subprocess` do `day_plan.py`, sem `sqlite3` cru. Evidência: diff sem `+import sqlite3`.
- [x] **agent-workflow-protocol** — segue. O texto-contrato reforça a sequência de boot (OFERECE o próximo ato) sem duplicar a doutrina do AGENTE.md; a fronteira humana (§1.1(c) da spec) é preservada.

### Convention Violations
Nenhuma. Idioma pt-BR nos comentários/labels; funções privadas em `snake_case`; `try/except` com default seguro (`""`/plano) conforme padrão de degradação graciosa das convenções.

### Critical Gate
- 🟡 WARNING [SEC108] `tools/hooks/memory_boot.py:47` — `subprocess.run` (dynamic exec). **Resolvido como override:** comando é literal fixo `[sys.executable, "tools/day_plan.py"]` (sem `shell=True`, sem input do usuário) e é **decisão de arquitetura explícita** na spec ("day_plan por subprocess com timeout, não import direto" — Technical Decisions), para isolar o boot da saúde do FSRS. Não rebaixa o veredito.
- ✅ Sem operações destrutivas de banco, remoção de auth, secrets hardcoded ou exposição de PII no diff.

### Próximos passos
**Ready to ship.** Sugestão: commitar a Parte 1 e seguir para a Parte 2 do PRD de Autogovernança.
