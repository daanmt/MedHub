# Technical Concerns

**Analysis Date:** 2026-03-28

## High Priority

### 1. Direct `sqlite3` in UI pages (violates architecture rule)
- **Files:** `app/pages/1_dashboard.py`, `app/pages/2_estudo.py`, `app/pages/4_simulados.py`
- **Rule:** All DB calls must go through `app/utils/db.py` — no `import sqlite3` in pages
- **Risk:** DB path inconsistency, harder to maintain, bypasses centralized error handling

### 2. Inconsistent `ipub.db` path resolution
- **Patterns found:** CWD-relative `'ipub.db'` (some pages) vs `__file__`-based resolution (utils)
- **Risk:** App silently creates a second empty `ipub.db` if not launched from repo root
- **Fix:** Standardize all callers to use `Path(__file__).parent...` resolution

### 3. Missing table in `init_db.py` schema
- **Table:** `cronograma_progresso` — queried by `1_dashboard.py`, absent from `tools/init_db.py`
- **Risk:** Fresh DB init produces a broken dashboard; silent failure for new installs

### 4. `tools/sync_flashcards.py` is broken
- **Issue:** Calls `sync_from_errors()` which is undefined; script cannot run
- **Risk:** Silent data drift between `flashcards_cache.json` and `flashcards` table if anyone tries to use it

## Medium Priority

### 5. FSRS algorithm is a simplified approximation
- **File:** `app/utils/fsrs.py`
- **Issue:** Deviates from FSRS v4 spec in stability/difficulty update formulas
- **Risk:** Suboptimal spaced repetition scheduling — low impact for study use case

### 6. FSRS doesn't persist on Streamlit Cloud
- **Issue:** Structural limitation — filesystem is ephemeral on Streamlit Cloud
- **Status:** Documented, accepted; FSRS is local-only by design
- **Risk:** Users reviewing on cloud get no benefit from spaced repetition

### 7. `app/utils/styles.py` design system is entirely unused
- **Issue:** `inject_styles()` is never called from any page
- **Risk:** CSS design system (COLORS, GLOBAL_STYLES) has zero effect on rendered UI

### 8. `app/components/sidebar.py` is dead code
- **Issue:** `render_sidebar()` is never imported or called anywhere
- **Risk:** False impression that sidebar is dynamic; `ESTADO.md` preview never rendered

### 9. `flashcard_builder.py` uses raw HTTP instead of Anthropic SDK
- **File:** `app/utils/flashcard_builder.py`
- **Issue:** Makes raw `requests.post()` calls to Anthropic API; model pinned to `claude-3-5-sonnet-20240620` (deprecated snapshot)
- **Risk:** Silent breakage when deprecated model is removed

### 10. Missing dependencies in `requirements.txt`
- **Missing:** `anthropic`, `langchain-anthropic`, `requests`
- **Risk:** Fresh installs fail for memory subsystem and flashcard generation

### 11. Bare `except:` clauses silently swallow errors
- **Files:** `app/utils/db.py`, `app/utils/flashcard_builder.py`, `tools/insert_questao.py`
- **Risk:** Operational failures are invisible; debugging requires adding print statements

### 12. `4_simulados.py` blocks 30s on missing Ollama
- **Issue:** No timeout or fallback — page hangs for 30 seconds if Ollama is not running
- **Risk:** Poor UX for users without local Ollama installation

## Low Priority / Nice-to-fix

- No structured logging — `print()` only, no timestamps, no log levels
- No input validation at UI boundaries (Simulados question generation)
- `app/utils/parser.py` is legacy-only but still imported in some paths — could be removed
- Mixed Portuguese/English in code comments and variable names (cosmetic)
- `tools/fix_taxonomy_bridge.py` is a one-off repair script with no guard against re-running

## Known Limitations

- **Dual-environment gap:** Local and Streamlit Cloud diverge on every FSRS review, DB write, and LLM call. No sync mechanism exists and none is planned.
- **Single-user only:** No authentication, no multi-user support. By design.
- **Windows file-locking:** `SQLiteMemoryStore` opens/closes connection per operation to avoid Windows SQLite lock issues — this is intentional but limits throughput.
- **Agent as write controller:** All meaningful data writes require Claude Code session. No self-service data entry via UI.

## Deprecated / Dead Code

| Item | Location | Status |
|---|---|---|
| `sync_git()` | `app/utils/db.py` | Documented broken, no callers — safe to delete |
| `flashcard_builder.py` (v1 pipeline) | `app/utils/flashcard_builder.py` | No callers; cache file retired — safe to delete |
| `save_new_error()` | `app/utils/file_io.py` | Writes to archived `caderno_erros.md`; no callers — safe to delete |
| `render_sidebar()` | `app/components/sidebar.py` | Never imported — safe to delete |
| `tools/sync_flashcards.py` | `tools/sync_flashcards.py` | Broken + superseded by `insert_questao.py` — safe to delete |
| `app/utils/parser.py` | `app/utils/parser.py` | Legacy caderno_erros parser; data now in `ipub.db` — evaluate for removal |
| `medhub-ui-refresh-main/` | repo root | React/Lovable prototype, abandoned by user decision — safe to delete |
