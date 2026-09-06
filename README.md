# MedHub

> Agent-first study system for Brazilian medical-residency exams. A wrong answer becomes a structured error record, atomic flashcards, an FSRS schedule and a refined clinical summary. There is no application UI: the agent that boots from `AGENTE.md` is the interface, and the code is the deterministic substrate underneath it.

**Status:** operational personal project, in active use. Single user, single machine. No deployment, no auth, no multi-user support.

---

## What it is

MedHub splits the system in two: **the agent is the brain, the code is the deterministic substrate**. Any harness that reads [`AGENTE.md`](AGENTE.md) can drive it (Claude Code is the primary one; [`AGENTS.md`](AGENTS.md) exists so tools that look for that filename by convention find the same entry point). The agent reads the governance documents, runs the CLIs in `tools/`, and conducts the study session in conversation.

The code owns only what has to be deterministic:

- **State** -- a local SQLite database, `ipub.db`, holding the curriculum taxonomy, structured errors, flashcards, FSRS card state and revlog, bulk session volume, theme-level review timestamps, the day plan, and the skills tables (schema in `tools/init_db.py`).
- **Scheduling** -- `app/utils/fsrs.py` is a thin adapter over `py-fsrs` (`fsrs>=6.3.1`), the reference FSRS implementation, at `REQUEST_RETENTION = 0.9`. `app/utils/fsrs_balance.py` is a pure module that flattens calendar load inside the free slack around an interval (+/-5%, floor 1 day, cap 10, review cards with interval >= 4 days only) without ever touching `stability` or `difficulty`.
- **Retrieval** -- `app/engine/rag.py`: a ChromaDB collection (`resumos`) over `resumos/**/*.md` chunked by H2/H3 headers, embedded with `nomic-embed-text` through a local Ollama, queried multi-query (raw plus an optional HyDE document) and filtered by a hard cosine-distance ceiling (`max_distance = 0.35`). When ChromaDB or Ollama are unavailable, `search()` degrades to a lexical fallback tagged `source = fallback_textual`.
- **Harness** -- `tools/auto_check.py`, a warning-first linter and test runner wired into a git pre-commit hook, plus a pytest suite (365 tests collected).

The Anthropic API is optional and used in exactly two places: HyDE query expansion in `app/engine/rag.py` and long-term memory consolidation in `app/memory/manager.py`, both `claude-haiku-4-5-20251001`. Without `ANTHROPIC_API_KEY`, HyDE falls back to the raw query and memory consolidation runs only the error-count sync.

---

## How it works

```
Wrong answer on a practice question
        |
        v
python tools/insert_questao.py       (one atomic 4-step transaction)
        |
        +-- taxonomia_cronograma      (area + theme, created if missing)
        +-- questoes_erros            (structured error + broken-link metadata)
        +-- flashcards                (N atomic cards authored by the agent)
        +-- fsrs_cards                (initial FSRS state per card)
        |
        v
python tools/fsrs_queue.py --list    (due queue as JSON)
        |
        v
/revisar  -- the agent presents card by card, grades 1-4,
             and writes back through fsrs_queue.py --record
        |
        v
app/utils/db.record_review           (single FSRS write path)
        -> py-fsrs schedules, fsrs_balance shifts the due date
           inside its slack, fsrs_revlog keeps the audit trail
```

Two curves run in parallel. The **card-level** curve is FSRS, described above. The **theme-level** forgetting curve is separate: `tools/review_radar.py` ranks dormant themes, `tools/dormant_refresh.py --stamp --kind {dormant_refresh,directed_review}` records a thematic review in `review_log`, and the hard boundary is that this path never touches FSRS. The `/revisar` skill is the single review competence and carries both sub-modes: PREPARAR (calibrated re-teaching, FSRS read-only) and DRENAR (the card-by-card FSRS player).

Two derived planning inputs sit next to it. `tools/cronograma.py` parses the EMED study schedule PDF (gitignored; looked up at the repo root, then `data/`) into the versioned, text-free `core/cronograma/grade.json` (30 weeks, 352 tasks, 10,218 planned questions) and is read-only against `ipub.db`. `core/cronograma/prevalencia_enamed.json` is a manual prevalence signal (89 themes, 5 sources, 35 exam-board patterns) that `tools/fsrs_queue.py --prevalencia` uses, opt-in, to reorder the never-introduced bucket of the queue.

`tools/day_plan.py` composes all of this into the day plan the session boots with.

---

## Architecture

**Governance layer.** [`AGENTE.md`](AGENTE.md) is the single governance document: boot sequence, closing protocol, conventions, non-reversible decisions, the skill/workflow/CLI contract, and the memory model. [`HANDOFF.md`](HANDOFF.md) is the short operational state (next immediate step, state per front). [`ESTADO.md`](ESTADO.md) is the macro snapshot (goals, indicator, milestones). Nine normative contracts in `core/contracts/` bind the behaviour: `cronograma`, `estado`, `evidence-governance`, `forgetting-curve`, `fsrs-management`, `handoff`, `orquestracao`, `reconcile`, `revisao-calibrada`.

**Skills and workflows.** `.claude/commands/*.md` is the single canonical source of skills (12 files: 11 canonical plus `/refrescar`, a deprecated redirect stub). `.agents/skills/source-command-*/SKILL.md` are generated build artifacts produced by `tools/sync_skills.py` and are never edited by hand; `sync_skills.py --check` reports parity drift. `.agents/workflows/*.md` holds imperative task protocols (`analisar-questoes`, `criar-resumo`, `curar-cards`, `gerar-reforco`, `registrar-sessao`, plus `graphify`). The contract in `AGENTE.md` section 7.2: skills are atomic reference, workflows are orchestration and never restate skill content, and each CLI has its canonical signature in exactly one skill.

**Code.** `app/engine/` exposes one stable surface to agents, `get_topic_context()`, built on `rag.py`. `app/memory/` is a LangMem-backed long-term store on a separate `medhub_memory.db` with a single live namespace, `("medhub", "weak_areas")`. `app/utils/db.py` is the only `import sqlite3` in `app/` and holds the canonical definition of an active card. CLIs under `tools/` use `sqlite3` directly by design.

**Harness.** `tools/setup_hooks.py` installs a git pre-commit hook that runs `python -X utf8 tools/auto_check.py --staged`; the agent runs `--changed` before reporting any task done. `auto_check` has around 20 numbered checks with two severities: BLOCK (exit 1) and WARN (exit 0, aggregated) -- a new rule is born WARN. It runs the resumo linter, the full pytest suite, the FSRS load-balancer suite, skill/mirror parity, session-pointer and HANDOFF-length invariants, doc-vs-code drift, card self-sufficiency and atomicity, `ipub.db` referential integrity, reachability, and RAG index staleness.

**SSOTs** (`AGENTE.md` section 5.5):

| Domain | SSOT | Committed |
|---|---|---|
| Errors, FSRS, schedule, thematic review (`review_log`) | `ipub.db` | No (local only) |
| Clinical knowledge | `resumos/**/*.md` | Yes |
| Project state | `ESTADO.md` | Yes |
| Workflows | `.agents/workflows/` | Yes |
| Agent long-term memory | `medhub_memory.db` | No (local only) |
| API keys | `.env` | No (gitignored) |

---

## Repository structure

```
medhub/
|-- AGENTE.md                  -- governance doc; every session boots here
|-- AGENTS.md                  -- same entry point, conventional filename
|-- CLAUDE.md                  -- pointer stub to AGENTE.md
|-- HANDOFF.md                 -- short operational state, next step
|-- ESTADO.md                  -- macro snapshot (goals, indicator, milestones)
|-- ROADMAP.md                 -- evolutionary direction, no dates
|-- AUDITORIA_MEDHUB.md        -- engineering findings ledger (F-numbered)
|-- app/
|   |-- engine/
|   |   |-- rag.py                  -- ChromaDB + Ollama + optional HyDE
|   |   `-- get_topic_context.py    -- resumo + recent errors + weak_areas
|   |-- memory/                     -- LangMem long-term store
|   |   |-- store.py                -- SQLiteMemoryStore
|   |   |-- manager.py              -- consolidate_session (ChatAnthropic)
|   |   |-- schemas.py
|   |   `-- inspect.py              -- introspection CLI
|   `-- utils/
|       |-- db.py                   -- only `import sqlite3` in app/
|       |-- fsrs.py                 -- adapter over py-fsrs
|       `-- fsrs_balance.py         -- pure calendar load balancer
|-- core/
|   |-- contracts/                  -- 9 normative contracts
|   |-- cronograma/
|   |   |-- grade.json              -- derived from the schedule PDF, 30 weeks
|   |   `-- prevalencia_enamed.json -- manual prevalence signal, 89 themes
|   |-- simulados/                  -- mock-exam fixtures and guides
|   `-- provas.json                 -- exam dates (countdown source)
|-- tools/                          -- 43 non-test modules (CLIs + shared libs)
|   |-- hooks/                      -- SessionStart / PostToolUse hook scripts
|   |-- utils/                      -- git_utils, state_utils
|   |-- eval/                       -- retrieval eval: queries.json, run_eval.py
|   |-- test_*.py                   -- 46 test files
|   `-- _archive/migrations/        -- one-shot migrations, do not re-run
|-- resumos/                        -- 127 clinical summaries in 6 areas + INDEX.md
|-- history/                        -- 124 session logs, INDEX.md, ledgers
|-- docs/                           -- exam-execution playbook + plans
|-- .claude/
|   |-- commands/                   -- 12 skills (canonical source)
|   `-- settings.json               -- SessionStart + PostToolUse hooks
|-- .agents/
|   |-- skills/                     -- generated mirrors (build artifacts)
|   |-- workflows/                  -- imperative task protocols
|   `-- rules/
|-- .vibeflow/                      -- specs, PRDs, audits, patterns, decisions
|-- conftest.py
|-- pytest.ini
|-- requirements.txt
|-- LICENSE                         -- MIT
`-- .gitignore
```

Local-only, never committed: `ipub.db`, `medhub_memory.db`, `data/chroma/`, `.env`, every `*.pdf` (the EMED source PDFs are deliberately kept on disk inside `resumos/` and `data/` to feed the RAG, but they are the publisher's IP), `tmp/`, `scratch/`, `graphify-out/`.

---

## How to run

Requirements: **Python 3.10+**. Ollama with `nomic-embed-text` pulled is needed only for the semantic RAG path.

```bash
# 1. Create a virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1                 # Windows PowerShell
# source .venv/bin/activate                  # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the SQLite schema (idempotent; path resolved from __file__)
python -X utf8 tools/init_db.py

# 4. (Optional) Index the knowledge base for semantic retrieval
ollama pull nomic-embed-text
python -X utf8 tools/index_resumos.py        # run from the repo root

# 5. Install the git pre-commit harness hook
python -X utf8 tools/setup_hooks.py

# 6. (Optional) .env, gitignored, may set ANTHROPIC_API_KEY
#    for HyDE and long-term memory consolidation.
```

On Windows, prefix Python invocations with `-X utf8`; the repo assumes UTF-8 output.

**Starting a session:** open the repo in Claude Code. The `SessionStart` hook in `.claude/settings.json` runs `tools/hooks/memory_boot.py`, which injects the top weaknesses from long-term memory, a summary of `tools/day_plan.py`, a HANDOFF-vs-history drift flag and the "next immediate step" from `HANDOFF.md` before the first turn. The agent then follows the boot sequence in `AGENTE.md` section 2. A `PostToolUse(Write)` hook fires `tools/hooks/memory_session_log.py` when a new `history/session_NNN.md` is written, which consolidates the session into long-term memory in a detached process.

Main CLIs (canonical signatures live in the matching skill under `.claude/commands/`):

| CLI | What it does |
|---|---|
| `tools/day_plan.py` | day plan for the proactive boot; `--handoff-block`, `--difficulty`, `--tempo/--energia`, `--aderencia` |
| `tools/fsrs_queue.py` | FSRS due queue as JSON; `--next`, `--list`, `--record`, `--cluster`, `--prevalencia` |
| `tools/insert_questao.py` | canonical writer for a wrong answer: taxonomy, error, cards and FSRS state in one transaction |
| `tools/performance.py` | accumulated volume, monthly target, cost per question, weak areas (read-only) |
| `tools/cronograma.py` | read-only derivation of the schedule PDF into `grade.json`, crossed with performance and FSRS |
| `tools/auto_check.py` | autonomous harness: `--changed` (working tree), `--staged` (pre-commit), `--all` |

---

## Status and limitations

**What works**

- The full loop: error CLI -> SQLite -> atomic cards -> FSRS scheduling -> conversational review with the ratings written back through a single write path.
- Faithful FSRS via `py-fsrs`, with calendar load balancing that provably does not touch the memory model.
- Local RAG over the markdown knowledge base, with an explicit lexical fallback when ChromaDB or Ollama are down.
- A real harness: 46 test files, 388 test functions, 365 tests collected by `pytest`, run in full by `auto_check` and blocked at commit time by the pre-commit hook.

**What is partial or known-fragile**

- **Single user, local only.** `ipub.db` and `medhub_memory.db` are gitignored, so cloning this repo gives you the code, the contracts and the clinical summaries -- not the study state.
- **The retrieval eval is small and stale.** `tools/eval/` measures file-level retrieval on 18 (query, expected resumo) pairs; the committed `REPORT.md` (2026-08-14) reads Recall@5 = 0.889 / MRR@10 = 0.685 with HyDE on and 0.444 / 0.409 without. At n = 18 the 95% CI is roughly 22pp. The report also documents up to 17pp run-to-run swing caused by a non-deterministic HyDE call; `temperature=0` was added to that call afterwards, so the baseline predates the fix and should be re-run. The runner still matches the current `rag.py` API (`search`, `_CHROMA_AVAILABLE`).
- **Schedule truth is split across sources.** `grade.json` is derived from the PDF, but completion and ordering live in spreadsheets the owner edits by hand, so the derived grade can disagree with reality. By contract that divergence is management information, never corruption -- the reconcile checks for it are non-blocking.
- **Open engineering debt is tracked, not fixed.** `AUDITORIA_MEDHUB.md` carries F-numbered findings; `ESTADO.md` and `HANDOFF.md` name the currently open ones (duplicated taxonomy rows splitting FSRS and dormancy, prevalent themes with no taxonomy row, bulk buckets invisible to the dormancy radar, summaries lagging new guidelines).
- **Two CLIs in `tools/` are not reachable from any live reference** (`audit_fsrs.py`, `calibrate_card_checks.py`), per the generated table in `AGENTE.md` section 7.4. Some modules still have no docstring, which that table reports as a gap.
- **History:** `ipub.db` was tracked early and removed with `git rm --cached`; the blob remains in git history. Historical commits also contain a transcribed study schedule and the author's own performance spreadsheet, both removed from the current tree.

**History of the UI:** MedHub used to ship a Streamlit app. The agent-first pivot (session 074, 2026-06-03) shrank it, the residual pages and `summarize_performance` were deleted in the code-death consolidation of 2026-08-14, and the agent -- Claude Code, or any harness that boots from `AGENTE.md` -- has been the interface since.

**Out of scope:** no multi-user, no auth, no deployment. Single-machine study environment. No patient data of any kind: the corpus is exam questions and the owner's own performance on them.

---

## License

MIT -- see [`LICENSE`](LICENSE). Covers both the code and the clinical content under `resumos/`.
