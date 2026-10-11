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
- Tests: `tools/test_<alvo>.py`, and the filename must be added to `python_files` in `pytest.ini` to be collected (`tools/test_suites_orfas.py` falha se uma suíte não estiver em nenhum registro de execução)
- Resumos (clinical summaries): `Título em Sentence Case.md` under `resumos/<Especialidade>/[Subarea/]`
- Session logs: `history/session_NNN.md` (zero-padded 3-digit number)
- Agent skills: `.claude/commands/<slug>.md`; mirrors are `.agents/skills/source-command-<slug>/SKILL.md`
- Frontmatter fields `type`, `area`, `especialidade`, `status`, `aliases` on all resumo files (see AGENTE.md §5.2)

## Database access
- **Only `app/utils/db.py` may use `import sqlite3`** — no other module in `app/`
  - Conflito (regra x código): `app/memory/store.py` (backend do `medhub_memory.db`, não do `ipub.db`) e `app/memory/manager.py` (abre o `ipub.db` só em `mode=ro`) também importam `sqlite3`. O `store.py` já consta da allowlist de escrita como backend separado (`AGENTE.md` §8).
- All queries go through functions in `db.py` that return `pd.DataFrame` or plain dicts
- DB path resolved relative to repo root: `os.path.join(os.path.dirname(...), 'ipub.db')`
- Conexão por `get_connection()`: liga `PRAGMA foreign_keys = ON` (o PRAGMA é por conexão) e garante a VIEW `flashcards_ativos`. CLI com conexão própria liga o mesmo PRAGMA
- Sempre fechar a conexão; o idioma atual é `try: ... finally: conn.close()`
- Use `conn.commit()` before `conn.close()` on write operations
- Carimbo de tempo só por `db.agora()` / `db.carimbo()` / `db.hoje()` (hora LOCAL naive, F80), chamados pelo atributo do módulo para o teste poder congelar o relógio; nunca pelo `DEFAULT CURRENT_TIMESTAMP` (UTC). Trava: `tools/test_fuso_unico.py`
- Toda tabela escrita existe no schema do `tools/init_db.py` ou tem DDL preguiçosa idempotente (`_ensure_<tabela>_table`, `ALTER ... ADD COLUMN` condicional). Trava: `tools/test_schema_escrita.py`
- "Card ativo" tem definição única: `db.ATIVO_WHERE` / `db.ativo_where(alias)` / VIEW `flashcards_ativos` / `db.ativos()`
- Exception: standalone CLIs in `tools/` open their own connection directly. O perímetro arquivo -> tabelas de cada writer está em `tools/test_writer_allowlist.py::ALLOWLIST`; writer novo = editar a allowlist de propósito. CLI novo prefere a camada fina (escrever por um writer do `db.py`, como `tools/plano.py`, `tools/reforja.py`, `tools/emed_banco.py`)
- Testes nunca tocam o `ipub.db` real: `monkeypatch.setattr(db, "DB_PATH", <tmp_path>)`

## Agent norms (the product surface)
- `.claude/commands/<slug>.md` is the **single source of truth** for a skill. Never hand-edit
  `.agents/skills/source-command-<slug>/SKILL.md` — it is a build artifact
- After editing any command: `python tools/sync_skills.py`, then `--check` must exit 0
- Each CLI has its canonical signature in exactly ONE skill; workflows reference it, never copy it (AGENTE.md §7.2)
- A norm must describe the system that exists. If a subsystem dies, the clause that names it
  either becomes accurate or is deleted — a stale clause burns tool calls and, at worst, destroys data
- Nunca instruir uma tool (`mcp__<server>__<tool>`) cujo server não esteja declarado. Hoje o `.mcp.json` (gitignored) está vazio e o único MCP de projeto vem de plugin habilitado em `.claude/settings.json`: `pubmed@life-sciences` (server `plugin_pubmed_PubMed`). As tools `mcp__pubmedmcp__*` morreram na s169
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
- **Todo INSERT de card passa por `app/utils/card_checks.py::validar_card()`** (`insert_questao`, `insert_card_base`, `insert_card_extra`) — `erros` bloqueiam a escrita, `avisos` só avisam. A EDIÇÃO (`tools/recurate_cards.py`, `db.update_flashcard_fields`) roda os mesmos predicados do `card_checks` um a um, mais o ratchet de verso de `app/utils/card_atomicity.py`
- `card_version` bumps only on a real field change; FSRS state is always preserved across recuration

## FSRS
- The scheduler is the reference library `py-fsrs` (`fsrs>=6.3.2`) — **not** a hand-rolled v4
- `app/utils/fsrs.py` is a thin adapter (`Scheduler(desired_retention=0.9, learning_steps=(), relearning_steps=(), enable_fuzzing=False)`); the kwargs live in ONE place, `app.utils.fsrs.KWARGS_BASE`, and `tools/fsrs_optimize.py` builds its replay Scheduler from it
- No rating brings a card back on the same day (F140, s204): same-day relearning belongs to the player's re-drill, which never records. `state` 3 is legacy data, not something the adapter produces
- Never write `fsrs_revlog` twice for the same card in one session (anti-duplo-registro). In the chat `/revisar` the dedup lives in the agent; in the player/hub path it lives in the writer (s193): `fsrs_queue --record-lote` is idempotent by revlog EQUALITY (`app/utils/notas_player.situacao`: same `review_time` = already recorded; a newer review without the equal one = out of order, reported, never written)
- Player notes are recorded on the REVIEW clock, not the recording clock: `record_review(..., quando=...)` / `FSRS.evaluate(..., quando=...)` take the note's `ts` converted by the single helper `notas_player.relogio` (ISO UTC -> local naive, truncated to the second); `quando` in the future or not after the card's last review -> `ValueError`, nothing written (py-fsrs does NOT refuse a `review_datetime` before `last_review` -- it silently treats it as short-term)
- The page's `db` is untrusted input and the shared account makes every viewer OWNER: the writer quarantines strange docs (`notas_player.validar_nota`), reports each with its reason and records the valid ones
- Review queue order is fixed: `atrasados` → `erros_frescos` → `hoje` → `novos` (`get_cards_by_bucket`)

## CLI tools (tools/)
- All scripts are invokable as `python tools/<script>.py --arg value`
- Use `argparse` with explicit `required=True` for mandatory args (exceção: o `insert_questao.py` valida os obrigatórios à mão, porque `--errors-file` os dispensa no modo lote)
- DB path: `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`
- Print human-readable success/error to stdout; return bool from the main insert function
- `finally: if conn: conn.close()` — always close on exception
- Ferramenta destrutiva ou de lote: dry-run POR PADRÃO, grava só com `--apply --expect N` (COUNT-ASSERT: o N medido no dry-run), e é idempotente. Ex.: `tools/plano.py --semear`, `tools/selo.py --rotacionar`, `tools/backup_db.py --desfixar-lote`

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
- Boot (`AGENTE.md` §2): `AGENTE.md` antes de qualquer ação; depois `HANDOFF.md` PRIMEIRO, `ESTADO.md`, o check de reconcile e o Plano do Dia. O Plano do Dia é injetado pelo hook `SessionStart` — **do not re-run `tools/day_plan.py` by hand**
- Fechamento (`AGENTE.md` §3): `HANDOFF.md` sempre (números por `tools/day_plan.py --handoff-block`); `ESTADO.md` só se o macro mudou; `history/session_NNN.md` + linha em `history/INDEX.md`; `tools/selo.py --rotacionar`; commit semântico + push
- SSOT rule: the error goes to `ipub.db` (via `insert_questao.py`), the lesson goes to `resumos/`
- `ESTADO.md` narrative fields are **1 line** by contract — accumulated prose belongs in `history/`

## Git / commits
- Selo de sessão: `sessao NNN: <descrição>`, com tag opcional (`sessao NNN (hub-backend): ...`)
- Engenharia: `feat|fix|docs|chore|refactor(sNNN): <descrição>` (ex.: `fix(s176): F91 -- ...`)
- Reforma: `fase N lote N part-X: <descrição>`
- `ipub.db`: NOT committed (local only, in .gitignore)
- `medhub_memory.db`: NOT committed
- Source PDFs: NOT committed (gitignored, but retained on disk)

## RAG (busca semântica sobre resumos)
- **Single engine:** `app/engine/rag.py` + ChromaDB in `data/chroma/`
  - Corpus: `resumos/**/*.md`, **gold-only**, single collection `resumos`, chunked by H2/H3
  - Embedding: `nomic-embed-text` via local Ollama (`http://localhost:11434`)
  - Interface: `from app.engine.rag import search, index_all`
  - Degradação declarada (F91): com ChromaDB/Ollama fora, `search()` cai no fallback léxico (hits com `metadata['source'] == 'fallback_textual'`) e, se nada casar, levanta `RagIndisponivel` — nunca devolve `[]` mudo
  - Reindex after adding/renaming a resumo: `python tools/index_resumos.py` (`--clear` after renames)
- **There is no second index.** The `obsidian-notes-rag` MCP was decommissioned 2026-07-12 and
  removed from `.mcp.json`; `search_two_tier()`/`pdf_raw` were removed in consolidacao part-2
- **`data/chroma/` is gitignored** — local only

## Don'ts
- Do NOT use `import sqlite3` outside `app/utils/db.py` (only exception: standalone CLIs in `tools/`)
- Do NOT hand-edit anything under `.agents/skills/` — regenerate with `tools/sync_skills.py`
- Do NOT referenciar MCP server não declarado: o `.mcp.json` está vazio; o PubMed vem do plugin `pubmed@life-sciences` (as tools `mcp__pubmedmcp__*` não existem mais)
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
- Do NOT carimbar pelo `DEFAULT CURRENT_TIMESTAMP` do SQLite (UTC) — usar `db.carimbo()` / `db.agora()` (F80)
- Do NOT escrever em tabela que não existe no schema nem tem DDL preguiçosa — dentro de `try/except` a escrita falha calada; trava `tools/test_schema_escrita.py`
- Do NOT reimplementar o filtro de card ativo — usar `db.ATIVO_WHERE` / `db.ativos()`
- Do NOT registrar erro sem card cunhado (exceto `--status anulada|banca-divergente`) — o fallback heurístico do `insert_questao.py` foi removido
- Do NOT ler `[]`/`RagIndisponivel` do RAG como "o tema não existe" — honest-negative (`core/contracts/evidence-governance.md`)

<!-- vibeflow:auto:end -->

## Hotfix traces — what `reproduction` and `status` mean here (decided s177, 2026-09-11)

These two fields were being conflated, and the cost was real: two traces from 2026-09-06
(`cronograma-pdf-path`, `fsrs-balance-stdout`) sat at `status: partial` for five days with
red-before-green tests, green suites, clean gates **and** post-fix verification against the real
artifact — parked in the consolidation debt list forever, for no defect. That is claim-aging of
status, the same class the G14 check exists to catch one level up.

**They measure different things. Keep them apart.**

- **`reproduction`** records how the RED test was reproduced. In MedHub `synthetic` is the
  **rule, not a weakness**: suites never touch the real `ipub.db` (the writer-allowlist discipline,
  F49 — a suite that writes to the production db is itself a defect, see F96 for the same lesson
  about production logs). Writing `reproduction: real` to avoid a downgrade would be lying about
  the fixture.
- **`status`** records whether the fix is verified. `verified` requires all three:
  1. a regression test written **before** the fix, red then green;
  2. the full suite green and the harness gate clean;
  3. **post-fix verification against the real artifact**, read-only, written into the `DoD`.
- `status: partial` is for a fix whose **DoD is genuinely incomplete** — a half-measure, a deferred
  branch, a known case left uncovered. It is not a penalty for a synthetic fixture.

🔴 **Corollary:** `reproduction: synthetic` + the three conditions above = **`verified`**. If a
trace cannot show condition 3, it stays `partial` and says which artifact was not exercised.

## Pergunta obrigatória em toda spec (F110, s185)

Toda spec deste projeto responde, em **uma linha**, antes do Definition of Done:

> **Que fricção esta spec remove -- e ela é virtuosa ou viciosa?**

Fricção **viciosa** (automatizar): copiar id à mão, descobrir defeito de lote um por vez, dado sem
porta de consulta. Fricção **virtuosa** (proteger): recall antes do verso, recall a frio, nota
honesta, relearning até o critério, racional declarado, triagem humana de card.

Norma: `core/contracts/revisao-calibrada-contract.md` Cláusula 13. Ledger das fricções:
`docs/FUNDAMENTOS-APRENDIZAGEM.md`. Spec que remove fricção virtuosa é regressão pedagógica com
cara de melhoria de produto -- e nenhum gate pega, porque o código fica mais limpo.

## Manual Corrections

**2026-10-10 (M-127, fecho do Lote 0 da Fase 0):** o write-gate de card mora em
`app/utils/card_checks.py::validar_card()`. Ele saiu de `tools/` em `98148fa` (s186, 1.9a: `app/`
para de alcançar `tools/`). A linha da região gerada acima que ainda põe o módulo em `tools/` está
desatualizada; o próximo `analyze` deve absorver esta correção.
