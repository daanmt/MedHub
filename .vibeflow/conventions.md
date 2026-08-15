# Conventions: MedHub

> Hand-reconciled: 2026-08-14 (consolidacao part-5). **Update by hand** — `analyze`
> re-invents subsystems that were deleted. Mechanical guard: `python tools/doc_drift.py`.

<!-- vibeflow:auto:start -->

## Language
- All user-facing text, comments, variable names, and UI labels: **Portuguese (pt-BR)**
- Code identifiers (function names, column names, class names): pt-BR or English, both acceptable
- All agent workflow/skill/contract files: pt-BR

## File naming
- tools/scripts: `snake_case.py` — e.g. `insert_questao.py`, `card_checks.py`
- Tests: `tools/test_<alvo>.py`, and the filename must be added to `python_files` in `pytest.ini` to be collected
- Resumos (clinical summaries): `Título em Sentence Case.md` under `resumos/<Especialidade>/[Subarea/]`
- Session logs: `history/session_NNN.md` (zero-padded 3-digit number)
- Agent skills: `.claude/commands/<slug>.md`; mirrors are `.agents/skills/source-command-<slug>/SKILL.md`
- Frontmatter fields `type`, `area`, `especialidade`, `status`, `aliases` on all resumo files (see AGENTE.md §5.2)

## Database access
- **Only `app/utils/db.py` may use `import sqlite3`** — no other module in `app/`
- All queries go through functions in `db.py` that return `pd.DataFrame` or plain dicts
- DB path resolved relative to repo root: `os.path.join(os.path.dirname(...), 'ipub.db')`
- Always close connections: explicit `conn.close()` after every `pd.read_sql` or cursor block
- Use `conn.commit()` before `conn.close()` on write operations
- Exception: standalone CLIs in `tools/` open their own connection directly

## Agent norms (the product surface)
- `.claude/commands/<slug>.md` is the **single source of truth** for a skill. Never hand-edit
  `.agents/skills/source-command-<slug>/SKILL.md` — it is a build artifact
- After editing any command: `python tools/sync_skills.py`, then `--check` must exit 0
- Each CLI has its canonical signature in exactly ONE skill; workflows reference it, never copy it (AGENTE.md §7.2)
- A norm must describe the system that exists. If a subsystem dies, the clause that names it
  either becomes accurate or is deleted — a stale clause burns tool calls and, at worst, destroys data
- Never instruct a tool name (`mcp__<server>__<tool>`) whose server is absent from `.mcp.json`
- Never require binary bytes over MCP in a boot step — if a read needs bytes, it belongs to the
  user's local ritual, not the agent (`cronograma-contract.md` Cláusula 5b)

## Sensors (WARN-first)
- Sensors DETECT and report; they never correct, never block, never write
- `tools/doc_drift.py` runs two modes: `drift-check` annotations over the 4 state docs, and a
  dead-reference scan over `.claude/commands/`, `.claude/agents/`, `.agents/workflows/`, `core/contracts/`
- A sensor that cannot judge something stays silent about it (out-of-repo refs, globs, placeholders) —
  honest silence beats fake coverage, and false positives are how a sensor gets ignored
- A line that asserts an absence ("foi removido") is a tombstone, not a lie — the scan skips it

## Flashcard schema
- Structured fields: `frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`
- **The `frente`/`verso` fallback is gone** — there is no UI to fall back to; structured fields are mandatory
- Provenance: `quality_source`, `card_version`, `needs_qualitative`, `questao_id` on `flashcards`;
  `card_version` + `selection_reason` on `fsrs_revlog`
- Card types: `tipo` = `elo_quebrado` | `armadilha` | scaffold degrees (`base`, `mecanismo`, …)
- **Every write passes `tools/card_checks.py::validar_card()`** — `erros` block the write, `avisos` warn
- `card_version` bumps only on a real field change; FSRS state is always preserved across recuration

## FSRS
- The scheduler is the reference library `py-fsrs` (`fsrs>=6.3.1`) — **not** a hand-rolled v4
- `app/utils/fsrs.py` is a thin adapter (`Scheduler(desired_retention=0.9, learning_steps=(), enable_fuzzing=False)`)
- Never write `fsrs_revlog` twice for the same card in one session (anti-duplo-registro; dedup lives in the agent)
- Review queue order is fixed: `atrasados` → `erros_frescos` → `hoje` → `novos` (`get_cards_by_bucket`)

## CLI tools (tools/)
- All scripts are invokable as `python tools/<script>.py --arg value`
- Use `argparse` with explicit `required=True` for mandatory args
- DB path: `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`
- Print human-readable success/error to stdout; return bool from the main insert function
- `finally: if conn: conn.close()` — always close on exception
- Destructive tools need a `--dry-run` and must be idempotent

## Clinical summaries (resumos/)
- Mandatory spec: `.claude/commands/estilo-resumo.md`
- Emojis: `⭐` (fundamental), `⚠️ Padrão de prova:` (exam trap inline), `🔴 Armadilha:` (armadilhas section only)
- **No emojis in H1/H2/H3 headers**
- **No `✅`/`❌` bullets** — use plain text or `⭐`
- Armadilhas section is **cumulative** — never delete, only add/refine
- Benchmark: 80% assertiveness (condutas, scores, criteria) / 20% clinical didactics
- Frontmatter: `type`, `area`, `especialidade`, `status`, `aliases` fields required

## PDF retention (s086 — replaces the old "Zero PDF")
- 🔴 **Source PDFs from EMED are RETAINED** (gitignored). They feed
  `tools/cobertura_conhecimento.py` and the ballast gate `insert_questao.py::_tem_lastro`,
  and they are non-reconstructible source IP
- Only the temporary `.txt` files from extraction are cleaned automatically
- Deleting a PDF is an explicit user act, never an agent default

## Agent sessions
- Boot: read `AGENTE.md` first, then `ESTADO.md`. The day-plan is injected by the `SessionStart`
  hook — **do not re-run `tools/day_plan.py` by hand**
- Closure: update `ESTADO.md` + create `history/session_NNN.md` + git commit
- SSOT rule: the error goes to `ipub.db` (via `insert_questao.py`), the lesson goes to `resumos/`
- `ESTADO.md` narrative fields are **1 line** by contract — accumulated prose belongs in `history/`

## Git / commits
- Session commits: `sessao NNN: <one-line description>`
- Tool commits: `chore: <description>`
- `ipub.db`: NOT committed (local only, in .gitignore)
- `medhub_memory.db`: NOT committed
- Source PDFs: NOT committed (gitignored, but retained on disk)

## RAG (busca semântica sobre resumos)
- **Single engine:** `app/engine/rag.py` + ChromaDB in `data/chroma/`
  - Corpus: `resumos/**/*.md`, **gold-only**, single collection `resumos`, chunked by H2/H3
  - Embedding: `nomic-embed-text` via local Ollama (`http://localhost:11434`)
  - Interface: `from app.engine.rag import search, index_all`
  - Safe fallback: if ChromaDB or Ollama is offline, `search()` degrades to a textual fallback
  - Reindex after adding/renaming a resumo: `python tools/index_resumos.py` (`--clear` after renames)
- **There is no second index.** The `obsidian-notes-rag` MCP was decommissioned 2026-07-12 and
  removed from `.mcp.json`; `search_two_tier()`/`pdf_raw` were removed in consolidacao part-2
- **`data/chroma/` is gitignored** — local only

## Don'ts
- Do NOT use `import sqlite3` outside `app/utils/db.py` (only exception: standalone CLIs in `tools/`)
- Do NOT hand-edit anything under `.agents/skills/` — regenerate with `tools/sync_skills.py`
- Do NOT reference an MCP server that is not in `.mcp.json` (today only `pubmedmcp`)
- Do NOT delete source PDFs — the "Zero PDF" policy was reverted in s086
- Do NOT add emojis to H1/H2/H3 headers in resumo files
- Do NOT use `✅`/`❌` as bullet markers in resumos
- Do NOT write `estilo:` field in resumo frontmatter
- Do NOT add editorial footers to resumo files
- Do NOT commit `ipub.db` or `medhub_memory.db`
- Do NOT delete armadilhas from the cumulative section in resumos — only add/refine
- Do NOT read from `caderno_erros.md` as SSOT — it's archived; SSOT is `ipub.db`
- Do NOT use `flashcards_cache.json` for anything — it's archived to `artifacts/legacy/`
- Do NOT re-run `tools/day_plan.py` at boot — the hook already did it

<!-- vibeflow:auto:end -->
