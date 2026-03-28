# Code Conventions

**Analysis Date:** 2026-03-28

## Style Guide

**Linting/Formatting:**
- No `.flake8`, `pyproject.toml`, `.pylintrc`, or `setup.cfg` found at project root.
- No `black`, `ruff`, or `isort` configuration detected.
- Code style is informal and unenforced — formatting is manually maintained.

**General rules observed in practice:**
- 4-space indentation throughout
- Lines generally kept under ~120 characters
- Single blank line between top-level functions; double blank line rare
- f-strings used universally for string formatting (no `%` or `.format()`)
- `encoding='utf-8'` explicitly passed to all file I/O calls

**Module-level docstrings:**
- Present in well-structured modules: `app/memory/store.py`, `app/memory/manager.py`, `tools/extract_pdfs.py`, `app/memory/schemas.py`
- Absent in utility modules: `app/utils/db.py`, `app/utils/parser.py`, `app/utils/styles.py`
- Pattern when present: triple-quoted string at top of file explaining purpose, usage examples, and key functions

## Naming Conventions

**Files:**
- Streamlit pages: numeric prefix + snake_case — `1_dashboard.py`, `2_estudo.py`
- Utility modules: snake_case — `file_io.py`, `flashcard_builder.py`, `styles.py`
- Tool scripts: snake_case verb phrases — `insert_questao.py`, `extract_pdfs.py`, `audit_resumos.py`
- All filenames lowercase (enforced in sessao 059 path standardization)

**Functions:**
- Public functions: `snake_case` — `parse_caderno_erros()`, `build_flashcard_via_llm()`, `record_cache_review()`
- Private/internal functions: leading underscore `_snake_case` — `_make_store()`, `_extract_key_term()`, `_invert_elo_to_question()`, `_llm_consolidate()`, `_fallback_consolidate()`
- Streamlit page-local helpers: leading underscore — `_avancar()` in `2_estudo.py`

**Variables:**
- snake_case throughout — `card_data`, `tema_id`, `erro_origem`, `session_num`
- Constants: SCREAMING_SNAKE_CASE — `DB_PATH`, `CACHE_PATH`, `BASE_DIR`, `COLORS`, `DEFAULT_W`, `GLOBAL_STYLES`
- Loop variables: single letter for simple cases (`e`, `r`, `f`), descriptive for complex (`entry`, `card`, `item`)

**Classes:**
- PascalCase — `FSRS`, `SQLiteMemoryStore`, `UserProfile`, `WeakArea`, `SessionInsight`

**Database/schema fields:**
- snake_case for Python variable names mapping to DB columns
- Portuguese names in DB columns: `area`, `tema`, `questoes_realizadas`, `elo_quebrado`, `armadilha_prova`

## Documentation Patterns

**Function docstrings:**
- Present inconsistently — roughly 60% of public functions have docstrings
- Format: single-line triple-quoted strings for simple functions; multi-line with Args/returns only in `app/memory/manager.py`

Examples of documented functions:
```python
def parse_caderno_erros(rel_path="caderno_erros.md") -> list[dict]:
    """Parse estruturado e robusto do caderno de erros (Reforma v3.0 Stateful)"""

def consolidate_session(
    session_num: int,
    store: SQLiteMemoryStore | None = None,
    db_path: str = "medhub_memory.db",
) -> None:
    """Entry point principal — consolida sessão na memória longa.

    Args:
        session_num: Número da sessão (ex: 54)
        store: Store opcional; se None, cria a partir de db_path
        db_path: Caminho para medhub_memory.db
    """
```

**Inline comments:**
- Used frequently for intent annotation, especially in complex logic sections
- Comments in Portuguese when describing business/domain logic
- Comments in English when describing technical/architectural rationale
- Version tags used in comments: `(Reforma v3.0 Stateful)`, `(v2.0 Fix)`, `(Plan v2.0 Fix)`

**Section separators:**
- Used in long page files and some tools: `# ── SECTION NAME ──────────`
- Dashed separators in `store.py`: `# ------------------------------------------------------------------`
- `# ---------------------------------------------------------------------------` blocks label test functions in `test_memory.py`

## Type Annotations

**Usage pattern:**
- Type hints applied consistently in `app/memory/` (newer, higher-quality code)
- Type hints sparse or absent in `app/utils/` and `app/pages/` (older code)
- `from __future__ import annotations` used in all `app/memory/` modules for forward-compatible annotations

Examples from well-annotated code (`app/memory/store.py`, `app/memory/manager.py`):
```python
def put(self, namespace: tuple[str, ...], key: str, value: dict[str, Any]) -> None:
def get(self, namespace: tuple[str, ...], key: str) -> Optional[Item]:
def _read_session_log(session_num: int) -> str | None:
def _extract_areas_from_log(log_text: str) -> list[str]:
```

Partially annotated (return types only) in `app/utils/`:
```python
def parse_caderno_erros(rel_path="caderno_erros.md") -> list[dict]:
def get_cache_fsrs_state(erro_origem: int) -> dict:
def record_cache_review(erro_origem: int, rating: int) -> dict:
```

No annotations in `app/pages/` files.

## Import Organization

**Order observed (informal, not enforced):**
1. Standard library (`os`, `sys`, `re`, `json`, `math`, `sqlite3`, `pathlib`, `datetime`)
2. Third-party (`streamlit`, `pandas`, `plotly`, `langmem`, `langgraph`, `pydantic`)
3. Internal (`from app.utils.db import ...`, `from app.memory.store import ...`)

**Path manipulation for imports in pages:**
- `app/pages/` files use explicit `sys.path.insert(0, ...)` to resolve project root:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
```
- `app/memory/` uses clean relative imports: `from app.memory.store import SQLiteMemoryStore`

## Error Handling

**Dominant pattern: broad `except Exception` with print/continue:**
```python
try:
    card = build_flashcard_via_llm(entry)
except Exception as e:
    print(f"Erro ao gerar card para erro #{entry_id}: {e}")
    continue
```

**Fallback pattern for DB queries (cloud compatibility):**
```python
try:
    df = pd.read_sql_query("SELECT ... full schema ...", conn)
except Exception as e1:
    try:
        df = pd.read_sql_query("SELECT * FROM ...", conn)  # fallback
    except Exception as e2:
        st.error("Erro Fatal no Banco de Dados.")
```

**Silent fallback for optional features:**
```python
def get_cache_due_count() -> int:
    try:
        ...
    except Exception:
        return 0  # never crash the UI for metrics
```

**26 bare/broad except clauses** across 14 project files — intentional pattern for UI resilience.

## Constants and Configuration

**Module-level constants** define paths and config:
```python
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')
CACHE_PATH = BASE_DIR / "flashcards_cache.json"
ROOT_DIR = Path(__file__).parent.parent.parent
```

**Design tokens** centralized in `app/utils/styles.py`:
```python
COLORS = {
    "background": "#05070A",
    "primary": "#2F6BFF",
    "success": "#1FA971",
    ...
}
```

**Hardcoded model names** in source (no config file):
- `_HAIKU_MODEL = "claude-haiku-4-5-20251001"` in `app/memory/manager.py`
- `"claude-3-5-sonnet-20240620"` in `app/utils/flashcard_builder.py`

## Git Conventions

**Commit message format:**
```
sessao NNN: <brief description in Portuguese>
```

Examples from recent history:
- `sessao 059: padronização de caminhos (lowercase) e remoção de PDF folders`
- `sessao 058: fechamento de faxina — consistencia e aposentadoria do HANDOFF`
- `sessao 057b: refatoracao qualidade flashcards — fases 1-4`
- `pancreatite + asma` (content-only commits use topic name directly)

**Patterns:**
- Session-scoped commits: prefix `sessao NNN:` for infrastructure/workflow work
- Content commits: no prefix, just topic — `pancreatite + asma`
- Portuguese throughout commit messages
- Em dash `—` used as separator for multi-part descriptions

**Files committed vs. gitignored:**
- `flashcards_cache.json`: committed (SSOT for cloud)
- `ipub.db`: gitignored (binary, local only)
- `.venv/`: gitignored

---

*Convention analysis: 2026-03-28*
