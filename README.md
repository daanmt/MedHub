# MedHub

> Personal study system for Brazilian medical-residency preparation. Closes the loop between a wrong answer, a structured error log, a clinical-summary refinement, and a spaced-repetition card.

**Status:** operational personal project, in active use. Single-user. No external deployment, no auth, no multi-user support.

---

## What it is

MedHub turns a failed practice question into a durable learning artifact. A single CLI invocation records the error with diagnostic metadata in a local SQLite database, generates a heuristic flashcard, and schedules a card in a simplified FSRS scheduler. A markdown knowledge base (`resumos/`) is then progressively refined through use. A Streamlit app sits on top for review, dashboards, and library browsing.

The knowledge base is local by default — embeddings are computed by Ollama against summaries on disk and stored in a local ChromaDB. The Anthropic API is called only for three optional capabilities (HyDE query expansion, LLM-quality flashcard generation, and agent-memory session consolidation); each gracefully degrades to a local fallback or a heuristic when the key is absent.

---

## How it works

```
Wrong answer on a practice question
        │
        ▼
tools/insert_questao.py (CLI)
        │
        ├─► questoes_erros          (structured error + metadata)
        ├─► flashcards              (heuristic card from elo_quebrado)
        ├─► fsrs_cards              (scheduled in spaced repetition)
        └─► taxonomia_cronograma    (curriculum tracking updated)
                │
                ▼
        app/engine/rag.py
        ChromaDB + nomic-embed-text (Ollama, local)
        + optional HyDE via Anthropic claude-haiku-4-5-20251001,
          falling back to Ollama llama3, then to raw query
                │
                ▼
        Streamlit app (3 pages: dashboard, study, library)
```

Retrieval is multi-query: the raw query and (when enabled) a HyDE-generated hypothetical answer are queried in parallel against a ChromaDB collection of H2/H3-chunked summaries. Results are deduplicated and filtered by a hard cosine-distance threshold (`0.35`). A BM25 hybrid rerank is implemented (`_bm25_rerank` in `app/engine/rag.py`) but disabled in code: re-enabling it regressed retrieval on this corpus.

**Retrieval is measured by a reproducible eval** at `tools/eval/` — 18 (query, expected_resumo) pairs mined from session logs, runnable as `python tools/eval/run_eval.py --both` (requires Ollama + ChromaDB). Current baseline (file-level): Recall@5 = 0.778 / MRR@10 = 0.657 with HyDE on; 0.500 / 0.425 without. See `tools/eval/REPORT.md` for per-query detail and `tools/eval/README.md` for honest caveats (n=18 → ~22pp CI; file-level not section-level; not an end-to-end retrieval→generation eval).

---

## Stack

- **Language / app:** Python 3.10+, Streamlit (multipage via `st.navigation`)
- **Storage:** SQLite — `ipub.db` for study state, `medhub_memory.db` for agent memory.
- **Retrieval:** ChromaDB persistent client + `nomic-embed-text` via Ollama at `http://localhost:11434`. Chroma collection persisted at `data/chroma/`.
- **LLM (optional):** Anthropic SDK (`claude-haiku-4-5-20251001`), used in three places: HyDE query expansion (`app/engine/rag.py`), LLM-quality flashcard generation (`app/engine/generate_flashcards.py`), and agent-memory session consolidation (`app/memory/manager.py`, via `langchain-anthropic`). Each call site falls back when `ANTHROPIC_API_KEY` is unset.
- **Reranking:** `rank-bm25` (implemented, disabled — see `rag.py`).
- **Spaced repetition:** FSRS-inspired simplified scheduler (`app/utils/fsrs.py`, ~75 LOC). The 17-weight default vector is the canonical FSRS v4 `DEFAULT_W`, but `evaluate()` applies a single linear difficulty update and one stability formula — not faithful FSRS v4.
- **Agent-memory scaffolding:** LangGraph `SqliteSaver` checkpointer + LangMem-backed store on a separate `medhub_memory.db`. Only `consolidate_session` (triggered by a PostToolUse hook) and two read paths (`weak_areas` in `get_topic_context` and `summarize_performance`) are exercised; the checkpointer and `tools.py` exports are scaffold for an agent that does not live in this repo.
- **PDF extraction:** pdfplumber, PyPDF2 (delete-after-extract policy — `tools/extract_pdfs.py`).
- **Dashboards:** Plotly, pandas.

---

## Repository structure

```
MedHub/
├── streamlit_app.py             # entry point (page registry only)
├── app/
│   ├── pages/                   # 3 Streamlit pages: dashboard, study, library
│   ├── engine/                  # 2-function read-only domain API
│   │   ├── rag.py               # ChromaDB + Ollama + HyDE + dormant BM25
│   │   ├── get_topic_context.py # bundles resumo + recent errors + weak_areas
│   │   └── summarize_performance.py
│   ├── memory/                  # LangGraph SqliteSaver + LangMem store
│   │   ├── checkpointer.py
│   │   ├── store.py             # SQLiteMemoryStore(BaseStore)
│   │   ├── manager.py           # consolidate_session (ChatAnthropic)
│   │   ├── schemas.py           # pydantic models
│   │   └── inspect.py           # introspection CLI
│   └── utils/
│       ├── db.py                # primary sqlite3 access layer
│       ├── fsrs.py              # FSRS-inspired simplified scheduler
│       └── styles.py            # design tokens
├── tools/                       # ~18 active CLIs: insert_questao, index_resumos,
│                                # init_db, audits, performance, regenerate_cards, ...
│                                # plus tools/_archive/migrations/ (6 one-shots, kept for history)
│                                # plus tools/eval/ (retrieval eval — queries.json + run_eval.py)
├── resumos/                     # clinical-knowledge markdown, 5 areas
├── .agents/workflows/           # markdown task protocols
├── .claude/commands/            # slash-command specs
├── history/                     # session logs
├── requirements.txt
├── LICENSE                      # MIT
└── .gitignore                   # ipub.db, .env, data/chroma/ are local-only
```

`app/engine/` exports two functions: `summarize_performance` (consumed by the dashboard) and `get_topic_context` (which internally calls `rag.search`, consumed by the library page). Both are read-only and side-effect-free.

The `import sqlite3` convention is "primary access via `app/utils/db.py`". It is currently also imported by `app/memory/{manager,store,inspect}.py` (separate `medhub_memory.db`) and by `app/pages/{1_dashboard,2_estudo}.py` (known tech debt). CLIs under `tools/` use `sqlite3` directly by design.

---

## How to run

Requirements: **Python 3.10+**, Ollama running locally with `nomic-embed-text` pulled (for RAG), ChromaDB installable.

```bash
# 1. Clone and create a virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1                 # Windows PowerShell
# source .venv/bin/activate                  # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure environment
#    .env (gitignored) may set ANTHROPIC_API_KEY for HyDE / LLM cards.
#    Absence triggers Ollama llama3 / heuristic fallback paths.

# 4. Initialise the SQLite store (must be run from repo root)
python tools/init_db.py

# 5. (Optional) Pull the embedding model and index resumos for RAG
ollama pull nomic-embed-text
python tools/index_resumos.py

# 6. Launch the app
streamlit run streamlit_app.py
```

`ANTHROPIC_API_KEY` is the only env var consumed by the codebase. Other paths (`OLLAMA_URL`, `CHROMA_PATH=data/chroma`, `DB_PATH=ipub.db`, `medhub_memory.db`) are currently hardcoded.

The dashboard boots cleanly on a fresh, empty database created by `init_db.py`; it will display zero data until errors or sessions are recorded.

---

## Status and limitations

**What works**
- End-to-end loop: error CLI → SQLite → flashcard → FSRS scheduling → review in the Streamlit app.
- Local RAG over the markdown knowledge base via Ollama embeddings and ChromaDB.
- Multi-query retrieval with optional HyDE (Anthropic → Ollama → identity fallback chain).
- FSRS-inspired review flow with state in SQLite.
- Graceful degradation: app boots without `chromadb`, without Ollama, and without `ANTHROPIC_API_KEY`.

**What is partial or known-fragile**
- BM25 hybrid rerank is implemented and dormant; re-enabling regressed retrieval on this corpus (see comment in `app/engine/rag.py`).
- The eval at `tools/eval/` measures file-level retrieval on 18 queries (n=18 → ~22pp 95% CI). It does not measure section-level retrieval, retrieval→generation end-to-end, or latency/cost. Older internal docs cite Recall@5 ≈ 0.90 / MRR ≈ 0.708 from an unrecoverable procedure — the committed baseline (0.778 / 0.657) supersedes them.
- The FSRS scheduler is a simplified single-formula implementation, not a faithful FSRS v4.
- `ipub.db` was tracked early on and removed via `git rm --cached`; the blob remains in git history. It is gitignored going forward.
- Historical commits also contain a transcribed UMED study schedule (`data/cronograma_umed.csv`) and the author's own EMED performance log (`Dashboard EMED 2026.xlsx`); both have been removed from the current tree.
- Test coverage is effectively zero (`tools/test_memory.py` only); no `pytest.ini`, no CI.

**Out of scope**
- No multi-user, no auth, no deployment. Single-machine study environment.

---

## License

MIT — see [`LICENSE`](LICENSE). Covers both the code and the clinical content under `resumos/`.
