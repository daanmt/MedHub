# Project: MedHub
> Analyzed: 2026-04-07
> Stack: Python 3, Streamlit (multipage), SQLite (ipub.db), LangGraph/LangMem, Anthropic Claude API, Ollama, pdfplumber, obsidian-notes-rag MCP
> Type: Medical study platform — CLI tools + Streamlit UI + AI agent workflows
> Suggested budget: ≤ 6 files per task

## Structure
Single-repo medical residency prep platform. Three layers:
1. **CLI tools** (`tools/`) — data ingestion, auditing, maintenance scripts
2. **Streamlit UI** (`app/`) — 4-page app for study, review, library, simulated exams
3. **Agent workflows** (`.agents/workflows/` + `.claude/commands/`) — portable markdown protocols for human+LLM collaboration

All persistent data lives in `ipub.db` (SQLite, local only). Clinical knowledge lives in `resumos/**/*.md`. Project state snapshot in `ESTADO.md`.

## Structural Units

| Unit | Path | Description |
|------|------|-------------|
| Dashboard | `app/pages/1_dashboard.py` | KPI metrics, performance by specialty, forgetting risk |
| Study/FSRS | `app/pages/2_estudo.py` | Error notebook (caderno) + FSRS flashcard player |
| Library | `app/pages/3_biblioteca.py` | Resumos RAG browser + PDF index |
| Simulados | `app/pages/4_simulados.py` | AI-generated practice MCQs via Ollama |
| Core Utils | `app/utils/` | styles, parser, db, fsrs, flashcard_builder, file_io |
| Engine API | `app/engine/` | Domain API layer: get_topic_context, analyze_error, generate_contextual_cards, RAG search |
| Memory | `app/memory/` | LangGraph + LangMem cross-session memory (SQLiteMemoryStore) |
| Tools/CLI | `tools/` | insert_questao, extract_pdfs, review_cli, index_resumos, audit/cleanup scripts |
| Workflows | `.agents/workflows/` | Portable agent protocols (analisar, criar, gerar, registrar) |
| Skills | `.claude/commands/` | Claude-specific specs (estilo-resumo, analisar-questao, etc.) |
| Knowledge Base | `resumos/` | 44 clinical summaries organized by specialty |

## Pattern Registry

<!-- vibeflow:patterns:start -->
patterns:
  - file: patterns/clinical-summary-format.md
    tags: [clinical-writing, resumo, formatting, markdown, exam-prep]
    modules: [resumos/, .claude/commands/]
  - file: patterns/error-insertion-pipeline.md
    tags: [error-tracking, sqlite, flashcards, cli, data-ingestion]
    modules: [tools/, app/utils/, app/engine/]
  - file: patterns/fsrs-review-flow.md
    tags: [fsrs, spaced-repetition, flashcards, streamlit, sqlite]
    modules: [app/pages/, app/utils/]
  - file: patterns/streamlit-page-structure.md
    tags: [streamlit, ui, pages, tabs, components]
    modules: [app/pages/, app/utils/styles.py]
  - file: patterns/db-access-layer.md
    tags: [sqlite, db, data-access, ipub, queries, pandas]
    modules: [app/utils/db.py, tools/, app/engine/]
  - file: patterns/agent-workflow-protocol.md
    tags: [agent, workflow, boot, closure, protocol, session]
    modules: [.agents/workflows/, AGENTE.md]
  - file: patterns/design-system-usage.md
    tags: [design-system, styles, css, streamlit, dark-theme]
    modules: [app/utils/styles.py, app/pages/]
  - file: patterns/domain-engine-api.md
    tags: [engine, domain-api, agent-interface, rag, flashcards, typed-api, hyde, multi-query]
    modules: [app/engine/, tools/]
<!-- vibeflow:patterns:end -->

## Pattern Docs Available

- [clinical-summary-format.md](patterns/clinical-summary-format.md) — Mandatory structure and formatting rules for all `resumos/` markdown files
- [error-insertion-pipeline.md](patterns/error-insertion-pipeline.md) — Full pipeline from wrong answer → SQLite + flashcard generation
- [fsrs-review-flow.md](patterns/fsrs-review-flow.md) — FSRS v4 algorithm, due-date query, 4-button rating, review recording
- [streamlit-page-structure.md](patterns/streamlit-page-structure.md) — How Streamlit pages are composed (tabs, cards, inject_styles, queries)
- [db-access-layer.md](patterns/db-access-layer.md) — SQLite access via db.py only; never direct sqlite3 in UI pages
- [agent-workflow-protocol.md](patterns/agent-workflow-protocol.md) — Boot/closure protocol every agent session must follow
- [design-system-usage.md](patterns/design-system-usage.md) — Flat dark design system: COLORS, inject_styles(), metric_card(), flashcard components
- [domain-engine-api.md](patterns/domain-engine-api.md) — Typed domain API for agents: get_topic_context, analyze_error, generate_contextual_cards, RAG (ChromaDB + Ollama)

## Key Files

| File | Role |
|------|------|
| `AGENTE.md` | Boot protocol — MUST read before any session action |
| `ESTADO.md` | Canonical state snapshot (SSOT for docs) |
| `ipub.db` | SQLite SSOT: errors, flashcards, FSRS state, taxonomy |
| `streamlit_app.py` | Entry point, calls `inject_styles()`, routes pages |
| `app/utils/db.py` | ALL database access — the only file allowed to use sqlite3 |
| `app/utils/styles.py` | Complete design system (COLORS, CSS injection, card components) |
| `app/utils/fsrs.py` | FSRS v4 algorithm (stability, difficulty, scheduling) |
| `app/engine/__init__.py` | Domain API surface — 5 stable exports for agents and pages |
| `app/engine/rag.py` | Semantic search over resumos/ via ChromaDB + nomic-embed-text (Ollama) |
| `app/utils/flashcard_builder.py` | LLM-based flashcard generation via Claude API |
| `tools/insert_questao.py` | CLI: inserts error + generates flashcards → ipub.db |
| `tools/index_resumos.py` | CLI: (re)indexes all resumos/ into ChromaDB for RAG search |
| `tools/extract_pdfs.py` | PDF → .txt extraction (Zero PDF policy) |
| `tools/review_cli.py` | FSRS CLI review interface |
| `.agents/workflows/analisar-questoes.md` | Canonical error-analysis workflow |
| `.claude/commands/estilo-resumo.md` | Mandatory formatting spec for clinical summaries |
| `resumos/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md` | Gold standard resumo example |

## Dependencies (critical only)

| Dep | Rationale |
|-----|-----------|
| `streamlit` | UI framework — multipage app |
| `anthropic` (via Claude API) | LLM for flashcard qualitative rewrite + simulated exams |
| `langgraph` + `langmem` | Cross-session memory (medhub_memory.db) |
| `pdfplumber` | PDF text extraction (primary) |
| `obsidian-notes-rag` MCP | Semantic RAG search over `resumos/` (Ollama/nomic-embed-text) |
| `fsrs` (custom in fsrs.py) | Spaced repetition scheduling — custom FSRS v4 implementation |

## Known Issues / Tech Debt

- `app/utils/parser.py` — legacy caderno_erros.md parser kept for backward compat; SSOT is now ipub.db
- `flashcards_cache.json` — deprecated v1, archived to `artifacts/legacy/`; no longer used
- `app/utils/db.py::sync_git()` — non-functional on Streamlit Cloud, ignore
- `medhub-ui-refresh-main/` — React/Lovable prototype, abandoned; ignored in .obsidian graph
- FSRS state does NOT persist on Streamlit Cloud (ephemeral filesystem)
- `4_simulados.py` logs weakness silently to DB; actual logging implementation needs verification
- `app/engine/rag.py`: ChromaDB index at `data/chroma/` — orphan chunks accumulate when resumos are renamed (IDs are `{stem}::N`); fix by re-running `tools/index_resumos.py --clear`. Context propagation prefix (`[tema > header]`) means index must be rebuilt after any alias changes too.
- Resumo index (`get_topic_context`) is in-process cached; new resumos in a live session won't be found without process restart
- `resumos/Clínica Médica/Neurologia/Demências.md` uses legacy frontmatter (`type: resumo`, `status: ativo`) — correct on next edit
