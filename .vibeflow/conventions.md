# Conventions: MedHub

<!-- vibeflow:auto:start -->

## Language
- All user-facing text, comments, variable names, and UI labels: **Portuguese (pt-BR)**
- Code identifiers (function names, column names, class names): pt-BR or English, both acceptable
- All agent workflow/skill files: pt-BR

## File naming
- Pages: `N_nome_da_pagina.py` (number prefix, snake_case) — e.g. `1_dashboard.py`, `2_estudo.py`
- Tools/scripts: `snake_case.py` — e.g. `insert_questao.py`, `extract_pdfs.py`
- Resumos (clinical summaries): `Título em Sentence Case.md` under `resumos/<Especialidade>/[Subarea/]`
- Session logs: `history/session_NNN.md` (zero-padded 3-digit number)
- Frontmatter field `type`, `area`, `especialidade`, `status`, `aliases` on all resumo files (via KNOWLEDGE_ARCHITECTURE.md)

## Database access
- **Only `app/utils/db.py` may use `import sqlite3`** — no pages, no other utilities
- All queries go through functions in `db.py` that return `pd.DataFrame` or plain dicts
- DB path resolved relative to repo root: `os.path.join(os.path.dirname(...), 'ipub.db')`
- Always close connections: explicit `conn.close()` after every `pd.read_sql` or cursor block
- Pattern: `conn = get_connection()` → `pd.read_sql(...)` → `conn.close()`
- Use `conn.commit()` before `conn.close()` on write operations
- Exception: `tools/insert_questao.py` is a standalone CLI, so it opens its own connection directly

## Streamlit pages
- Every page calls `inject_styles()` from `app.utils.styles` at the top (after `st.set_page_config`)
- Use `st.tabs([...])` for major page sections — not nested st.expander at top level
- Filters via `st.multiselect(..., placeholder="Todas")` — never radio buttons for specialty filters
- Session state keys: short, descriptive, snake_case — e.g. `fc_idx`, `fc_verso`, `fc_order`
- `@st.cache_data(ttl=60)` for DB load functions inside pages
- Cache clear on user action: `st.cache_data.clear()` + `st.rerun()`
- Pages connect to DB directly via `sqlite3.connect(DB_PATH)` only as last resort (legacy tab1 in 2_estudo.py); prefer db.py functions (via KNOWLEDGE_ARCHITECTURE.md)

## Design system
- Import: `from app.utils.styles import inject_styles, COLORS, metric_card, content_card, flashcard_front, flashcard_back`
- CSS class prefix: `medhub-*` (e.g. `medhub-card`, `medhub-metric-label`)
- **No gradients, no backdrop-filter, no shadows** — flat design only
- **Sentence case everywhere** — no ALL CAPS in labels, no text-transform: uppercase
- Font: Inter (Google Fonts CDN import in GLOBAL_STYLES)
- Colors from `COLORS` dict — never hardcode hex values in pages
- FSRS rating buttons: 4 columns, nth-child CSS targeting (already in GLOBAL_STYLES)

## Flashcard schema (v5.0)
- Structured fields: `frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`
- Legacy fields: `frente`, `verso` (kept for UI fallback only)
- Quality tracking: `quality_source` ('heuristic' | 'qualitative'), `needs_qualitative` (0=approved, 1=pending, 2=retired)
- Card types: `tipo` = 'elo_quebrado' | 'armadilha'
- Render check in UI: `use_structured = bool(frente_pergunta.strip() and verso_resposta.strip())`

## CLI tools (tools/)
- All scripts are invokable as `python tools/<script>.py --arg value`
- Use `argparse` with explicit `required=True` for mandatory args
- DB path: `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`
- Print human-readable success/error to stdout
- Return bool from main insert function (True/False)
- `finally: if conn: conn.close()` — always close on exception

## Clinical summaries (resumos/)
- Mandatory spec: `.claude/commands/estilo-resumo.md`
- Emojis: `⭐` (fundamental), `⚠️ Padrão de prova:` (exam trap inline), `🔴 Armadilha:` (armadilhas section only)
- **No emojis in H1/H2/H3 headers**
- **No `✅`/`❌` bullets** — use plain text or `⭐`
- Armadilhas section is **cumulative** — never delete, only add/refine
- Benchmark: 80% assertiveness (condutas, scores, criteria) / 20% clinical didactics
- Frontmatter: `type`, `area`, `especialidade`, `status`, `aliases` fields required (via CLAUDE.md)

## Agent sessions
- Boot: always read `AGENTE.md` first, then `ESTADO.md`
- Closure: update `ESTADO.md` + create `history/session_NNN.md` + git commit
- SSOT rule: error goes to `ipub.db` (via `insert_questao.py`), lesson goes to `resumos/`
- Zero PDF policy: extract → summarize → delete PDF + temp files

## Git / commits
- Session commits: `sessao NNN: <one-line description>`
- Tool commits: `chore: <description>`
- `ipub.db`: NOT committed (local only, in .gitignore)
- `medhub_memory.db`: NOT committed
- `flashcards_cache.json`: committed (archived to artifacts/legacy/, no longer active)

## RAG (busca semântica sobre resumos)

- **Sistema canônico:** `app/engine/rag.py` + ChromaDB em `data/chroma/`
  - Corpus: `resumos/**/*.md` (44 resumos clínicos, chunking por H2/H3)
  - Embedding: `nomic-embed-text` via Ollama local (`http://localhost:11434`)
  - Interface: `from app.engine.rag import search, index_all, _CHROMA_AVAILABLE`
  - Fallback seguro: se ChromaDB ou Ollama offline, `search()` retorna `[]` silenciosamente
  - Reindexar após adicionar/renomear resumo: `python tools/index_resumos.py`

- **Sistema auxiliar (MCP):** `obsidian-notes-rag` — corpus = vault completo (147 arquivos)
  - Usado apenas por agentes externos que precisam buscar qualquer nota do vault
  - **Bug conhecido:** sobe sem `--provider ollama` em sessões Antigravity → falha com `OPENAI_API_KEY not set`
  - O `.mcp.json` do repositório está correto; precisa restart do servidor MCP para herdar a configuração

- **Os dois sistemas não se interferem** — paths físicos distintos, clients ChromaDB independentes
- **Para código do engine/páginas:** sempre usar `app/engine/rag.py` (import direto, sem MCP)
- **Para reindexação:** `python tools/index_resumos.py` (CLI com argparse)
- **`data/chroma/` está no `.gitignore`** — local only, não commitar

## Don'ts
- Do NOT use `import sqlite3` in Streamlit pages or any file outside `app/utils/db.py` (only exception: `tools/insert_questao.py` as standalone CLI)
- Do NOT use treemaps or session history charts in the dashboard (via MEMORY.md)
- Do NOT add gradients, `backdrop-filter`, or `box-shadow` to UI components — flat design only
- Do NOT add emojis to H1/H2/H3 headers in resumo files
- Do NOT use `✅`/`❌` as bullet markers in resumos
- Do NOT write `estilo:` field in resumo frontmatter
- Do NOT add editorial footers to resumo files
- Do NOT commit `ipub.db` or `medhub_memory.db`
- Do NOT call `sync_git()` from `db.py` — it's broken on Streamlit Cloud, ignore it
- Do NOT delete armadilhas from the cumulative section in resumos — only add/refine
- Do NOT read from `caderno_erros.md` as SSOT — it's archived; SSOT is `ipub.db`
- Do NOT use `flashcards_cache.json` for anything — it's archived to `artifacts/legacy/`
- Do NOT modify `medhub-ui-refresh-main/` — abandoned React prototype

<!-- vibeflow:auto:end -->
