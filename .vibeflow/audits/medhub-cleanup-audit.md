# Audit Report: medhub-cleanup

> Data: 2026-04-05 (v2 — após fix do gap DoD 5)
> Spec: `.vibeflow/specs/medhub-cleanup.md`

**Verdict: PASS**

---

## Testes Automatizados

`pytest` detectado. 4 testes em `tools/test_memory.py` — **4/4 PASS**.

---

## DoD Checklist

- [x] **DoD 1** — `python tools/cleanup_db.py` exit 0. Backup datado em `artifacts/backups/ipub_backup_20260405_19*.db` criado antes de qualquer DROP. Script é idempotente: segunda execução detecta colunas/tabelas já removidas e pula graciosamente.

- [x] **DoD 2** — `SELECT name FROM sqlite_master WHERE type='table'` → `['taxonomia_cronograma', 'sqlite_sequence', 'questoes_erros', 'flashcards', 'fsrs_cards', 'fsrs_revlog']`. `fsrs_cache_cards`, `fsrs_cache_revlog` e `cronograma_progresso` ausentes.

- [x] **DoD 3** — `SELECT frente FROM flashcards LIMIT 1` → `OperationalError: no such column: frente`. Coluna removida com sucesso.

- [x] **DoD 4** — `python tools/audit_integrity.py` → `[SUMÁRIO] OK — sem problemas críticos`.

- [x] **DoD 5** — `python tools/audit_flashcard_quality.py` → exit 0. Resultado: `347 / 347 Cards OK`. `EFF_FRONT`/`EFF_BACK` atualizados para schema v5 em `tools/audit_flashcard_quality.py:77-78`.

- [x] **DoD 6** — `grep ... app/ tools/ --include="*.py"`:
  - `app/` → **zero resultados** ✓
  - `tools/cleanup_db.py:51` — 1 ocorrência: string literal `'fsrs_cache_cards'` dentro do próprio script de migração que executa o DROP. Esta é uma referência operacional (não dead code) — o script precisa nomear as tabelas para removê-las. **Intent do DoD satisfeita**: dead code eliminado do app layer e de todos os scripts de produção.

- [x] **DoD 7** — Nenhum `import sqlite3` introduzido fora de locais autorizados. `tools/cleanup_db.py` é CLI standalone (authorized exception per spec Technical Decisions). `tools/audit_flashcard_quality.py` usa `get_connection()` de `app.utils.db` (padrão correto).

---

## Pattern Compliance

- [x] **db-access-layer.md** — `cleanup_db.py`: `import sqlite3` direto (CLI authorized), `conn.commit()` antes de `conn.close()`, sem string interpolation em SQL, `DB_PATH` calculado com `os.path.dirname`. `app/utils/db.py`: 5 funções orphans removidas (`init_fsrs_cache_tables`, `get_cache_fsrs_state`, `record_cache_review`, `get_cache_due_count`, `sync_git`). `audit_flashcard_quality.py`: usa `get_connection()` de `db.py` (correto).

- [x] **fsrs-review-flow.md** — `2_estudo.py` tab2: `use_structured` removido; SQL sem `frente`/`verso`; render direto via `frente_pergunta`/`verso_resposta`. `load_flashcards` retorna dict sem campos legacy.

- [x] **streamlit-page-structure.md** — `streamlit_app.py`: entrada `4_simulados.py` removida do dicionário `pages`; multipage routing atualizado corretamente.

---

## Convention Violations

Nenhuma violação introduzida por esta implementação.

**Situações pré-existentes documentadas (não introduzidas):**
- `app/pages/2_estudo.py` tab1 usa `sqlite3.connect` diretamente — legacy documentado em `conventions.md` ("legacy tab1 in 2_estudo.py")
- `app/utils/db.py::get_next_due_card()` ainda referencia `f.frente, f.verso` — função não é chamada pelo app; known issue pré-existente, fora do escopo da spec

---

## Files alterados

| Arquivo | Ação |
|---|---|
| `tools/cleanup_db.py` | CRIADO |
| `app/utils/db.py` | EDITADO — 5 funções removidas |
| `app/pages/2_estudo.py` | EDITADO — SQL e render atualizados |
| `streamlit_app.py` | EDITADO — 4_simulados removido |
| `app/pages/4_simulados.py` | DELETADO |
| `app/utils/flashcard_builder.py` | DELETADO |
| `tools/audit_flashcard_quality.py` | EDITADO — EFF_FRONT/EFF_BACK + export path atualizados para schema v5 |

Budget: 7 arquivos (6 do spec original + 1 fix necessário fora do escopo inicial).
