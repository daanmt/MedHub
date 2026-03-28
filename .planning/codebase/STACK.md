# Technology Stack

**Analysis Date:** 2026-03-28

## Languages

**Primary:**
- Python 3.14.0 — all application code, tooling, and data processing

**Secondary:**
- SQL (SQLite dialect) — schema definitions and queries in `tools/init_db.py` and `app/utils/db.py`
- Markdown — primary content format for resumos, history, and knowledge base (`Temas/`, `history/`)

## Runtime

**Environment:**
- Python 3.14.0 (local)
- Streamlit Cloud (remote, production)

**Package Manager:**
- pip (inferred from `requirements.txt`)
- Lockfile: not present (only `requirements.txt` with `>=` version pins)

## Frameworks

**Core:**
- Streamlit `>=1.35.0` — full UI framework; entry point `streamlit_app.py`; pages under `app/pages/`
- LangGraph `>=0.3.0` — agent graph orchestration; used in `app/memory/` for session checkpointing
- LangMem `>=0.0.30` — long-term memory management; `create_memory_store_manager` in `app/memory/manager.py`

**Data:**
- Pandas `>=2.0.0` — DataFrame operations for all SQLite query results in `app/utils/db.py`
- Plotly `>=5.20.0` — interactive charts in `app/pages/1_dashboard.py`

**LLM Clients:**
- `langchain-anthropic` — `ChatAnthropic` wrapper used in `app/memory/manager.py`
- `requests` (stdlib-style HTTP) — direct Anthropic REST calls in `app/utils/flashcard_builder.py`

**PDF Processing:**
- pdfplumber `>=0.11.0` — primary PDF text extraction; used via `tools/extract_pdfs.py`
- PyPDF2 `>=3.0.0` — fallback PDF reader

**Spreadsheet / ETL:**
- openpyxl `>=3.1.0` — Excel import; used by `Tools/import_performance_excel.py` ETL

**Filesystem Watcher:**
- watchdog `>=4.0.0` — monitors file changes (Streamlit dev mode)

**Validation:**
- Pydantic — schema definitions for LangMem memory types in `app/memory/schemas.py`

## Key Dependencies

**Critical:**
- `streamlit>=1.35.0` — entire UI layer; without it nothing runs
- `langgraph>=0.3.0` + `langgraph-checkpoint-sqlite>=3.0.0` — memory graph + SQLite checkpointer (`app/memory/checkpointer.py`)
- `langmem>=0.0.30` — `create_memory_store_manager`; session consolidation pipeline in `app/memory/manager.py`
- `pandas>=2.0.0` — all database reads return DataFrames; used across every page and `app/utils/db.py`

**Infrastructure:**
- SQLite (stdlib `sqlite3`) — two databases: `ipub.db` (study data) and `medhub_memory.db` (agent memory)
- `requests` — direct HTTP to Anthropic Messages API in `app/utils/flashcard_builder.py`

## Configuration

**Streamlit Theme:**
- `.streamlit/config.toml` — dark theme, `primaryColor=#2F6BFF`, `backgroundColor=#05070A`, Inter font

**Environment Variables:**
- `ANTHROPIC_API_KEY` — required for LLM features; app degrades gracefully when absent
- No `.env` file present; variable must be set in the OS environment or Streamlit Cloud secrets

**Build:**
- No build step; Streamlit serves Python files directly

## FSRS Algorithm

**Implementation:** Custom simplified FSRS v4 — `app/utils/fsrs.py`

- 17-weight parameter set (`DEFAULT_W`)
- States: 0=New, 1=Learning, 2=Review, 3=Relearning
- Target retention: 90% (`next_interval` formula)
- Ratings: 1=Again, 2=Hard, 3=Good, 4=Easy

## Platform Requirements

**Development:**
- Python 3.14+
- `ANTHROPIC_API_KEY` env var for flashcard generation and memory consolidation
- Local SQLite files (`ipub.db`, `medhub_memory.db`) — not committed to git

**Production (Streamlit Cloud):**
- Stateless filesystem — SQLite writes do not persist across deploys
- `flashcards_cache.json` is committed to git and serves as the cloud-safe content store
- `ANTHROPIC_API_KEY` configured via Streamlit Cloud secrets UI

---

*Stack analysis: 2026-03-28*
