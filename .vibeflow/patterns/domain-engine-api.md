---
tags: [engine, domain-api, agent-interface, rag, flashcards, typed-api]
modules: [app/engine/, tools/]
applies_to: [services, commands, agents]
confidence: inferred
status: active
canonical_source: app/engine/__init__.py + app/engine/rag.py; AGENTE.md §6 for the export count
last_verified: 2026-08-25
---
# Pattern: Domain Engine API

<!-- vibeflow:auto:start -->
## What
`app/engine/` is a typed, side-effect-free domain library exposing the system's state to external agents (Claude Code, Cursor, external scripts). It sits above `app/utils/db.py` and wraps DB queries + RAG search into stable, well-documented function signatures. Pages and agents call `app.engine` — never `app.utils.db` directly from agent code.

## Where
- `app/engine/__init__.py` — public API surface (1 re-export estável)
- `app/engine/get_topic_context.py` — combined DB + RAG context lookup
- `app/engine/rag.py` — semantic search over resumos/ via ChromaDB + Ollama (Multi-Query + HyDE — módulo interno, importar como `from app.engine.rag import search`)

**Removed 2026-08-25 (dead — files no longer exist on disk):** `get_review_queue.py`,
`summarize_performance.py`, `analyze_error.py`, `generate_flashcards.py`. Per `AGENTE.md:153`,
`summarize_performance()` "foi removido junto com a UI Streamlit -- performance sai pela skill
`/performance` + CLIs." Performance/weakness analysis is no longer an `app.engine` concern.

## The Pattern

**Public API (1 stable re-export from `app.engine`):**
```python
from app.engine import get_topic_context
# dict with resumo + erros + cards + weak_areas + rag chunks
```

**Typical agent workflow:**
```python
from app.engine import get_topic_context

ctx = get_topic_context("Sepse Neonatal", area="Pediatria")
# ctx = {
#   "resumo_path": "resumos/Pediatria/Sepse Neonatal.md",
#   "resumo_content": "---\n...",
#   "erros_recentes": [...],
#   "cards_ativos": 3,
#   "weak_areas": [{"area": "Pediatria", "pattern": "...", "error_count": 4}],
#   "relevant_chunks": [{"text": "...", "metadata": {...}, "distance": 0.12}],
# }
```
For performance/weakness metrics, use the `/performance` skill or the underlying `tools/` CLIs — not `app.engine`.

**get_topic_context — rich context object:**
```python
ctx = get_topic_context("Cardiologia", area="Clínica Médica")
# Returns:
# {
#   "resumo_path": "resumos/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md",
#   "resumo_content": "---\n...",
#   "erros_recentes": [{"id": 5, "titulo": "...", "tipo_erro": "...", ...}],
#   "cards_ativos": 3,
#   "weak_areas": [{"area": "Clínica Médica", "pattern": "...", "error_count": 4}],
#   "relevant_chunks": [{"text": "...", "metadata": {...}, "distance": 0.12}],
# }
```

**RAG search — Multi-Query with HyDE:**
```python
# search() internally runs two queries: raw query + HyDE hypothetical doc
# Results are merged, deduplicated (by text), filtered by max_distance, sorted by distance
results = search(
    "quando intubar RN prematuro",
    n_results=5,
    area="Pediatria",    # optional ChromaDB where-filter
    use_hyde=True,       # default; generates hypothetical doc via Haiku → Ollama → raw fallback
    max_distance=0.35,   # cosine cutoff — hits above this are expelled
)
# Returns: list[dict] with keys: text, metadata (source, section, area, especialidade), distance
```

**Context propagation in indexing:**
```python
# Each chunk is stored with a global context prefix:
# "[{tema}{alias_str} > {header}]\n{chunk_text}"
# This ensures nomic-embed-text captures the document topic even in isolated paragraphs.
# Example: "[Sepse Neonatal (sepse, RN) > Diagnóstico]\nSIRS não se aplica..."
```

**Flashcard quality:** cards are authored by the agent directly (`--cards-file` on
`tools/insert_questao.py`, see `error-insertion-pipeline.md`) — there is no in-engine LLM
card-generation step anymore. `quality_source` values on `flashcards` still distinguish
provenance; see `app/utils/db.py` module docstring and `AGENTE.md §5.2`.

## Rules
- `app/engine/` functions NEVER raise exceptions — all errors are caught and return safe defaults (`[]`, `{}`, `None`)
- Resumo lookup uses fuzzy matching (`difflib.get_close_matches`, cutoff=0.6) — aliases in frontmatter expand the match surface
- `search()` is safe to call unconditionally — returns `[]` when chromadb is absent or Ollama is offline
- `_CHROMA_AVAILABLE` flag is set at import time and can be checked for early-exit logic (avoids even calling `search()`)
- Engine functions do NOT write to the DB — write operations belong to `tools/insert_questao.py`
- The resumo index is lazy-loaded and in-process cached — new resumos added during a session won't be found without process restart
- HyDE document generation order: Anthropic Haiku → Ollama llama3 → raw query (graceful cascade)

## Examples from this codebase

File: `app/engine/rag.py` — Multi-Query search + context propagation in indexing
```python
# Indexing: context prefix injected into every chunk
def index_resumo(path: Path, collection=None) -> int:
    content = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(path)
    chunks = _chunk_by_headers(content)
    tema = path.stem
    aliases = fm.get("aliases", [])
    alias_str = f" ({', '.join(aliases)})" if aliases else ""
    contexto_global = f"[{tema}{alias_str} > "
    for i, chunk in enumerate(chunks):
        texto_enriquecido = f"{contexto_global}{chunk['header']}]\n{chunk['text']}"
        collection.upsert(
            ids=[f"{path.stem}::{i}"],
            documents=[texto_enriquecido],
            metadatas=[{"source": str(path), "section": chunk["header"],
                        "area": fm.get("area", ""), "especialidade": fm.get("especialidade", "")}],
        )
    return len(chunks)

# Search: Multi-Query with HyDE, dedup, distance threshold
def search(query, n_results=5, area=None, use_hyde=True, max_distance=0.35):
    if not _CHROMA_AVAILABLE:
        return []
    query_texts = [query]
    if use_hyde:
        query_texts.append(_generate_hypothetical_document(query))  # Haiku → Ollama → raw
    results = collection.query(query_texts=query_texts, n_results=max(n_results * 2, 5), where=where)
    combined = []
    seen_texts = set()
    for docs_series, metas_series, dists_series in zip(...):
        for doc, meta, dist in zip(...):
            if dist > max_distance or doc in seen_texts:
                continue
            seen_texts.add(doc)
            combined.append({"text": doc, "metadata": meta, "distance": dist})
    return sorted(combined, key=lambda x: x["distance"])[:n_results]
```
<!-- vibeflow:auto:end -->

## Anti-patterns
- Importing `app.utils.db` directly from agent workflows — use `app.engine` functions which handle errors gracefully
- Calling `rag.search()` without checking `_CHROMA_AVAILABLE` first — will raise ImportError if chromadb not installed
- Assuming resumo index is up-to-date during a long session — index is built once per process; restart if resumos were added
- Renaming `.md` files without re-running `tools/index_resumos.py` — leaves orphan chunks in ChromaDB with deterministic `{stem}::N` IDs
