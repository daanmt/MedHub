# Codebase Structure

**Analysis Date:** 2026-03-28

## Directory Layout

```
MedHub/                         # Repo root — also Streamlit working directory
├── streamlit_app.py            # Entry point: page config + navigation router
├── ipub.db                     # SQLite: performance data + flashcards + FSRS (local only, not committed)
├── medhub_memory.db            # SQLite: LangMem agent long-term memory (local only, not committed)
├── flashcards_cache.json       # LLM-generated flashcard cache (committed to git)
├── requirements.txt            # Python dependencies
├── AGENTE.md                   # Agent boot protocol and session close procedure
├── CLAUDE.md                   # Claude Code project instructions
├── ESTADO.md                   # Canonical project state — single source of truth for session context
├── ROADMAP.md                  # Feature roadmap
├── README.md                   # Project overview
│
├── app/                        # Application package
│   ├── pages/                  # Streamlit pages (loaded by navigation router)
│   │   ├── 1_dashboard.py      # Dashboard: EMED metrics + critical theme alert
│   │   ├── 2_estudo.py         # Error notebook (query view) + FSRS flashcard player
│   │   ├── 3_biblioteca.py     # Library: resumos/*.md browser + PDF listing
│   │   └── 4_simulados.py      # AI-generated practice questions via Ollama
│   ├── components/
│   │   └── sidebar.py          # Sidebar renderer (reads ESTADO.md preview)
│   ├── utils/                  # Shared utilities
│   │   ├── db.py               # All SQLite access: metrics, errors, flashcards, FSRS
│   │   ├── fsrs.py             # FSRS v4 simplified algorithm
│   │   ├── flashcard_builder.py # LLM flashcard generation + JSON cache management
│   │   ├── parser.py           # Stateful Markdown parser for caderno_erros.md (legacy)
│   │   ├── file_io.py          # Safe read/write/append for .md files with .bak backup
│   │   └── styles.py           # Design system: COLORS dict, GLOBAL_STYLES CSS, inject_styles()
│   └── memory/                 # Agent long-term memory subsystem
│       ├── store.py            # SQLiteMemoryStore (LangGraph BaseStore over medhub_memory.db)
│       ├── manager.py          # Session consolidation: LLM or heuristic fallback
│       ├── schemas.py          # Pydantic schemas: UserProfile, WeakArea, WorkflowRule, SessionInsight
│       ├── checkpointer.py     # LangGraph checkpointer (SQLite-backed)
│       ├── inspect.py          # CLI: inspect memory store contents
│       └── tools.py            # LangMem memory tools wrappers
│
├── tools/                      # Agent-operated CLI scripts (never imported by UI)
│   ├── insert_questao.py       # PRIMARY: atomic multi-table write for one wrong question
│   ├── init_db.py              # One-time DB schema creation
│   ├── extract_pdfs.py         # PDF text extraction (Zero PDF policy)
│   ├── backup_db.py            # Manual DB backup utility
│   ├── sync_flashcards.py      # Sync flashcards_cache.json ↔ flashcards table
│   ├── review_cli.py           # Terminal FSRS review session
│   ├── migrate_flashcards.py   # Schema migration for flashcards table
│   ├── migrate_memory.py       # Memory DB migration
│   ├── regenerate_cards.py     # Batch flashcard regeneration (heuristic)
│   ├── regenerate_cards_llm.py # Batch flashcard regeneration (LLM)
│   ├── fix_taxonomy_bridge.py  # One-off taxonomy repair script
│   ├── audit_cards.py          # Flashcard quality audit
│   ├── audit_flashcard_quality.py # Detailed flashcard quality checks
│   ├── audit_fsrs.py           # FSRS state audit
│   ├── audit_integrity.py      # DB referential integrity audit
│   ├── audit_resumos.py        # resumos/ Markdown quality lint
│   ├── test_memory.py          # Memory subsystem tests
│   ├── KNOWLEDGE_ARCHITECTURE.md  # Hard rules for the knowledge environment
│   └── MEMORY_ARCHITECTURE.md  # Documentation for memory subsystem design
│
├── resumos/                    # Medical content summaries (Markdown, committed)
│   ├── Clínica Médica/         (Cardiologia, Dermatologia, Endocrinologia, Gastroenterologia,
│   │                            Hematologia, Hepatologia, Infectologia, Nefrologia,
│   │                            Neurologia, Pneumologia, Psiquiatria, Reumatologia)
│   ├── GO/
│   ├── Cirurgia/
│   ├── Pediatria/
│   └── Preventiva/
│
├── history/                    # Session logs (session_NNN.md, committed)
│
├── artifacts/                  # Non-committed working files
│   ├── backups/                # DB backups
│   ├── legacy/                 # Retired files (caderno_erros.md archive, etc.)
│   └── llm_runs/               # LLM output scratch files per session
│
├── .agents/workflows/          # Agent workflow instruction files (Markdown)
│   ├── criar-resumo.md
│   ├── analisar-questoes.md
│   ├── registrar-sessao.md
│   └── gerar-reforco.md
│
├── .claude/commands/           # Claude Code skill files (Markdown)
│   ├── estilo-resumo.md
│   ├── analisar-questao.md
│   ├── extrair-pdf.md
│   └── auditar-resumos.md
│
├── .planning/codebase/         # GSD mapper output
├── .streamlit/config.toml      # Streamlit theme (dark, primary=#2F6BFF)
├── .obsidian/                  # Obsidian vault config (userIgnoreFilters set)
└── .venv/                      # Python virtual environment (not committed)
```

## Key Directories

| Directory | Purpose | Committed? |
|---|---|---|
| `app/pages/` | Streamlit UI pages | Yes |
| `app/utils/` | Shared backend logic | Yes |
| `app/memory/` | Agent LangMem subsystem | Yes |
| `tools/` | Agent CLI scripts (never imported by UI) | Yes |
| `resumos/` | Medical Markdown summaries | Yes |
| `history/` | Session logs | Yes |
| `artifacts/legacy/` | Archived retired files | Yes |
| `artifacts/backups/` | DB backups | No |
| `artifacts/llm_runs/` | LLM scratch output | No |
| `.agents/workflows/` | Agent procedure definitions | Yes |
| `.claude/commands/` | Claude Code skill specs | Yes |

## File Naming Conventions

| Category | Pattern | Example |
|---|---|---|
| Pages | `N_lowercase.py` | `1_dashboard.py` |
| Utils | `lowercase_snake.py` | `flashcard_builder.py` |
| Tools | `verb_noun.py` or `audit_noun.py` | `insert_questao.py`, `audit_resumos.py` |
| Session logs | `session_NNN.md` (3-digit zero-padded) | `session_059.md` |
| Resumos | Title-case matching medical topic | `Assistência ao Parto.md` |
| Resumo dirs | Title-case matching specialty | `Clínica Médica/`, `GO/` |

## Where to Add New Code

| New thing | Location | Notes |
|---|---|---|
| Streamlit page | `app/pages/N_name.py` + register in `streamlit_app.py` | Use `st.Page()` entry |
| DB query/write | `app/utils/db.py` | No raw `sqlite3` in pages |
| CLI maintenance script | `tools/new_script.py` | Follow `insert_questao.py` pattern |
| Medical summary | `resumos/<Area>/<Specialty>/<Tema>.md` | Requires frontmatter (see `KNOWLEDGE_ARCHITECTURE.md`) |
| Agent workflow | `.agents/workflows/new-workflow.md` + register in `CLAUDE.md` | |
| Agent skill | `.claude/commands/new-skill.md` + register in `CLAUDE.md` | |
| Memory schema | `app/memory/schemas.py` + wire in `manager.py` | Use Pydantic class + namespace |
