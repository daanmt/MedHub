# Architecture

**Analysis Date:** 2026-03-28

## Pattern Overview

**Overall:** Dual-layer study platform — a Streamlit multi-page UI consuming a local SQLite database (`ipub.db`), operated by an AI agent (Antigravity/Claude Code) acting as the primary data-entry controller.

**Key Characteristics:**
- The agent (Claude Code) is a first-class architectural actor, not a peripheral tool. It drives data writes via CLI scripts in `tools/`.
- UI is strictly read-only with respect to the primary data store (`ipub.db`). Writes happen through `tools/insert_questao.py`.
- A second SQLite database (`medhub_memory.db`) stores long-term agent memory via a LangMem/LangGraph store, fully separate from performance data.
- Cloud deployment (Streamlit Cloud) runs in a degraded mode: no SQLite writes, no FSRS persistence, no LLM flashcard generation.

## Layers

**Entry Point / Router:**
- Purpose: Configures Streamlit app and declares all pages
- Location: `streamlit_app.py`
- Contains: `st.navigation()` page routing, `st.set_page_config()`
- Depends on: `app/pages/`
- Used by: Streamlit runtime

**UI Pages Layer:**
- Purpose: Renders all user-facing views; reads from `ipub.db` and JSON cache
- Location: `app/pages/`
- Contains: `1_dashboard.py`, `2_estudo.py`, `3_biblioteca.py`, `4_simulados.py`
- Depends on: `app/utils/db.py`, `app/utils/styles.py`
- Used by: Streamlit router

**Utility / Service Layer:**
- Purpose: All reusable logic — database access, file I/O, FSRS algorithm, LLM flashcard generation, Markdown parsing
- Location: `app/utils/`
- Contains: `db.py`, `fsrs.py`, `flashcard_builder.py`, `parser.py`, `file_io.py`, `styles.py`
- Depends on: `ipub.db`, `flashcards_cache.json`, `ANTHROPIC_API_KEY` env var
- Used by: pages, tools

**Agent Memory Layer:**
- Purpose: Long-term semantic memory for the AI agent; extracts clinical insights and weakness patterns from session logs
- Location: `app/memory/`
- Contains: `store.py` (SQLiteMemoryStore), `manager.py` (consolidation logic), `schemas.py` (Pydantic models), `checkpointer.py`, `inspect.py`, `tools.py`
- Depends on: `medhub_memory.db`, `langmem`, `langchain_anthropic`, `ANTHROPIC_API_KEY`
- Used by: agent workflows at session close; not used by UI pages

**CLI Tools Layer:**
- Purpose: Agent-operated scripts for data ingestion, DB initialization, auditing, migration, and review
- Location: `tools/`
- Contains: `insert_questao.py`, `init_db.py`, `extract_pdfs.py`, `audit_*.py`, `backup_db.py`, `sync_flashcards.py`, `review_cli.py`, and others
- Depends on: `ipub.db`, `app/utils/`
- Used by: Claude Code agent directly via CLI; never imported by UI

**Agent Workflow Layer:**
- Purpose: Markdown-based instruction files that define agent workflows (not code)
- Location: `.agents/workflows/`, `.claude/commands/`
- Contains: `criar-resumo.md`, `analisar-questoes.md`, `registrar-sessao.md`, `gerar-reforco.md`, `estilo-resumo.md`, `analisar-questao.md`, `extrair-pdf.md`, `auditar-resumos.md`
- Used by: Claude Code agent as procedural context

**Content Layer:**
- Purpose: Markdown medical summaries used for reference, RAG search, and Biblioteca page display
- Location: `resumos/`
- Contains: specialty-organized `.md` files (Clínica Médica, GO, Cirurgia, Pediatria, Preventiva, etc.)
- Used by: `app/pages/3_biblioteca.py`, Obsidian RAG MCP tool

## Data Flow

**Primary error ingestion flow:**
1. Agent (Claude Code) analyzes a wrong question during a session
2. Agent calls `tools/insert_questao.py` with structured fields (area, tema, elo, armadilha, etc.)
3. `insert_questao.py` upserts `taxonomia_cronograma`, inserts into `questoes_erros`, generates 1-2 flashcard rows in `flashcards`, and initializes FSRS state in `fsrs_cards`
4. All data lands in `ipub.db` (local only, never committed to git)

**FSRS review flow:**
1. `app/pages/2_estudo.py` queries `flashcards JOIN fsrs_cards` for due cards
2. User rates card (1=Again / 2=Hard / 3=Good / 4=Easy)
3. `app/utils/db.py::record_review()` applies `app/utils/fsrs.py::FSRS.evaluate()` and updates `fsrs_cards` + appends to `fsrs_revlog`
4. Page re-queries after full queue completion

**LLM flashcard generation flow (legacy / tools path):**
1. `app/utils/flashcard_builder.py::build_flashcard_via_llm()` reads an error entry dict
2. Calls Anthropic Messages API (`claude-3-5-sonnet-20240620`) with structured prompt
3. Returns structured JSON (frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha)
4. Result cached in `flashcards_cache.json` (committed to git)

**Agent memory consolidation flow:**
1. At session close, agent invokes `python -m app.memory.manager <session_num>`
2. `manager.py` reads `history/session_NNN.md`
3. If `ANTHROPIC_API_KEY` present: calls `langmem::create_memory_store_manager` with `claude-haiku-4-5` to extract `SessionInsight` and `WeakArea` objects
4. If no API key: heuristic fallback writes area list to store
5. Writes to `medhub_memory.db` via `SQLiteMemoryStore`
6. Syncs `WeakArea.error_count` from `ipub.db` performance data

**Dashboard display flow:**
1. `app/pages/1_dashboard.py` queries `taxonomia_cronograma` directly via `sqlite3`
2. Computes per-area performance, renders Plotly bar chart
3. Applies heuristic "fator_risco" formula (days_since_review + performance penalty) to surface critical themes

## State Management

- UI session state managed via `st.session_state` (ephemeral, per-browser session)
- Flashcard queue order and index stored in `st.session_state.fc_order`, `fc_idx`, `fc_verso`
- Persistent state lives in `ipub.db` (performance + FSRS) and `medhub_memory.db` (agent memory)

## Key Abstractions

**FSRS class:**
- Purpose: Simplified FSRS v4 spaced-repetition algorithm
- Location: `app/utils/fsrs.py`
- Pattern: Stateless calculator — takes card dict + rating int, returns new state dict. No DB calls inside.

**SQLiteMemoryStore:**
- Purpose: LangGraph `BaseStore` implementation over SQLite for agent long-term memory
- Location: `app/memory/store.py`
- Pattern: Namespace-keyed key-value store with per-operation connection open/close (Windows file-lock safe).

**insert_questao():**
- Purpose: Atomic multi-table write that ingests one wrong question and auto-generates flashcards + FSRS state
- Location: `tools/insert_questao.py`
- Pattern: Single transaction across `taxonomia_cronograma`, `questoes_erros`, `flashcards`, `fsrs_cards`. Auto-upserts taxonomy if tema is new.

**parse_caderno_erros():**
- Purpose: Stateful line-by-line parser for legacy `caderno_erros.md` format
- Location: `app/utils/parser.py`
- Pattern: Tracks `current_area` / `current_tema` as mutable state across `##` / `###` headers. Currently only used for legacy compatibility — canonical data is now in `ipub.db`.

## Entry Points

| Entry Point | Location | Trigger |
|---|---|---|
| Streamlit UI | `streamlit_app.py` | `streamlit run streamlit_app.py` |
| Error ingestion CLI | `tools/insert_questao.py` | `python tools/insert_questao.py` with argparse flags |
| DB initialization | `tools/init_db.py` | `python tools/init_db.py` (one-time setup) |
| Memory consolidation | `app/memory/manager.py` | `python -m app.memory.manager <session_num>` at session close |

## Error Handling

**Strategy:** Defensive at UI layer; bare exceptions at tools/CLI layer.

**Patterns:**
- Pages wrap DB calls in `try/except` with fallback queries and `st.error()` display
- `get_cache_due_count()` in `db.py` silently returns `0` on any exception
- `flashcard_builder.py` prints errors per-entry and continues iteration
- `insert_questao.py` wraps full transaction in `try/except`, always closes connection in `finally`
- `SQLiteMemoryStore` uses `contextmanager` that always closes connection regardless of exception

## Cross-Cutting Concerns

**Logging:** `print()` statements only — no structured logging framework. Agent tools use `[module/function]` prefix convention.

**Validation:** None at runtime boundary. Pydantic used only for LangMem schemas (`app/memory/schemas.py`). UI input is unvalidated.

**Authentication:** None. Application is single-user, local-only by design.

**DB Path Resolution:** Two patterns exist — `os.path.dirname` chain (pages, `insert_questao.py`) and `Path(__file__).parent.parent.parent` (utils). Both resolve to repo root. The constant `DB_PATH = 'ipub.db'` (relative) is also used in some pages, which requires the process to be launched from repo root.
