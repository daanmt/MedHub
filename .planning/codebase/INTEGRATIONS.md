# Integrations

**Analysis Date:** 2026-03-28

## External APIs

**Anthropic Claude API:**
- Purpose: flashcard generation (front/back from broken-link errors) and session memory consolidation
- Two distinct call patterns:
  1. Direct REST via `requests.post` — `app/utils/flashcard_builder.py`, model `claude-3-5-sonnet-20240620`, endpoint `https://api.anthropic.com/v1/messages`
  2. LangChain wrapper `ChatAnthropic` — `app/memory/manager.py`, model `claude-haiku-4-5-20251001` (low-cost consolidation)
- Auth: `ANTHROPIC_API_KEY` env var; app has graceful fallback path when key is absent
- API version header: `anthropic-version: 2023-06-01`

**Ollama (local LLM — optional):**
- Purpose: on-demand question generation for "Simulados RAG" feature (`app/pages/4_simulados.py`)
- Endpoint: `http://localhost:11434/api/generate` (local only)
- Model: `llama3` (user-installed; not a project dependency)
- Fallback: feature shows error if Ollama is not running; no cloud fallback

## Databases

**`ipub.db` — Primary Study Database (SQLite, local only):**
- Not committed to git; local only
- Path resolved relative to project root
- Tables:
  - `taxonomia_cronograma` — EMED performance metrics by area/tema (populated via ETL)
  - `questoes_erros` — structured error entries (populated via `tools/insert_questao.py`)
  - `flashcards` — front/back flashcard pairs linked to errors
  - `fsrs_cards` — FSRS memory state per flashcard (state, stability, difficulty, due date)
  - `fsrs_revlog` — full review history log
  - `fsrs_cache_cards` — FSRS state for cards sourced from `flashcards_cache.json`
  - `fsrs_cache_revlog` — review log for cache-sourced cards
- Client: stdlib `sqlite3` + Pandas `read_sql` — accessed only through `app/utils/db.py`
- ETL source: `Tools/import_performance_excel.py` imports EMED Excel exports into `taxonomia_cronograma`

**`medhub_memory.db` — Agent Long-term Memory (SQLite, local only):**
- Not committed to git; local only
- Path default: `medhub_memory.db` (project root)
- Tables:
  - `memory_store` — namespaced key-value JSON store (implements LangGraph `BaseStore`)
  - LangGraph checkpoint tables (created by `langgraph-checkpoint-sqlite`)
- Namespaces used:
  - `medhub/session_insights` — clinical insights extracted per session
  - `medhub/weak_areas` — recurring error patterns by medical area
  - `medhub/profile` — user preferences (exam target, study pace)
  - `medhub/workflow_rules` — procedural rules learned during sessions
- Client: `app/memory/store.py` (`SQLiteMemoryStore` — custom `BaseStore` implementation)
- Checkpointer: `app/memory/checkpointer.py` (`SqliteSaver` from `langgraph-checkpoint-sqlite`)

## File-based Storage

**`flashcards_cache.json` — LLM Flashcard Cache (committed to git):**
- Location: project root
- Purpose: persists Claude-generated flashcard content across environments; serves as cloud-safe SSOT for card content
- Format: JSON array of card objects keyed by `erro_origem` (integer)
- Written by: `app/utils/flashcard_builder.py` (`load_or_generate_flashcards`)
- Read by: `app/pages/2_estudo.py` via `flashcard_builder`

**`Temas/` — Medical Knowledge Base (committed to git):**
- Markdown files with YAML frontmatter (`type`, `area`, `especialidade`, `status`, `aliases`)
- 38 topics indexed at `Temas/INDEX.md`
- Read-only from application perspective; authored by Claude sessions

**`history/session_NNN.md` — Session Audit Trail (committed to git):**
- One file per study session
- Input to `app/memory/manager.py` for LLM consolidation

## Cloud / Hosting

**Streamlit Cloud:**
- Hosts the production UI at a public Streamlit Cloud URL
- Reads `.md` and `.json` files from the git repo directly
- Filesystem is ephemeral: SQLite databases (`ipub.db`, `medhub_memory.db`) do not persist
- Secrets configured via Streamlit Cloud secrets UI (mapped to env vars)
- No custom domain or CI/CD pipeline detected

**Git (GitHub):**
- Primary mechanism for syncing content to Streamlit Cloud (push = deploy)
- `flashcards_cache.json` and `Temas/` committed and readable by cloud app
- `ipub.db` excluded from git (local only)
- `sync_git()` function exists in `app/utils/db.py` but is documented as non-functional on Streamlit Cloud

## Authentication

- No user authentication layer
- Single-user local application
- `ANTHROPIC_API_KEY` is the only secret; controls access to Claude API features

## Claude Code Hooks

**`tools/hooks/memory_boot.py`:**
- `SessionStart` hook — runs at Claude Code session start
- Calls `app/memory/inspect.load_context()` to inject long-term memory into context

**`tools/hooks/memory_session_log.py`:**
- Logs session activity for later consolidation

## Monitoring & Observability

- No external error tracking (e.g., Sentry) detected
- Logging: Python `print()` statements throughout `app/memory/` with `[memory/manager]` prefix tags
- No structured logging framework

---

*Integration audit: 2026-03-28*
