# Testing

## Test Infrastructure

- No pytest config or `pytest.ini` / `setup.cfg` / `pyproject.toml` test section
- Single test file: `tools/test_memory.py`, run manually via `python tools/test_memory.py`
- No test runner automation or watch mode

## Test Coverage

### Covered
- `SQLiteMemoryStore` (in `tools/test_memory.py`): CRUD operations on the memory SQLite store

### Not Covered
- `app/utils/parser.py` — stateful caderno_erros parser
- `app/utils/db.py` — all SQLite queries, FSRS cache functions
- `app/utils/fsrs.py` — FSRS v4 algorithm
- `tools/insert_questao.py` — question ingestion CLI
- All Streamlit pages (`pages/`)
- `tools/extract_pdfs.py`

## Testing Patterns

- Boolean-returning test functions (return True/False)
- Isolated temp databases per test run
- Module patching for integration tests
- API key removal for offline testing
- Print-based pass/fail reporting (no assertions framework)

## Audit Scripts (Manual Quality Checks)

- `tools/audit_resumos.py` — lints study notes in `Temas/`
- `tools/audit_flashcard_quality.py` — checks flashcard quality
- `tools/audit_integrity.py` — checks data integrity across caderno_erros + ipub.db

## CI/CD

- None configured
- No `.github/workflows/` directory
- All validation is manual
