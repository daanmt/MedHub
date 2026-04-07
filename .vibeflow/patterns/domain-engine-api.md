---
tags: [engine, domain-api, agent-interface, rag, flashcards, typed-api]
modules: [app/engine/, tools/]
applies_to: [services, commands, agents]
confidence: inferred
---
# Pattern: Domain Engine API

<!-- vibeflow:auto:start -->
## What
`app/engine/` is a typed, side-effect-free domain library exposing the system's state to external agents (Claude Code, Cursor, external scripts). It sits above `app/utils/db.py` and wraps DB queries + RAG search into stable, well-documented function signatures. Pages and agents call `app.engine` — never `app.utils.db` directly from agent code.

## Where
- `app/engine/__init__.py` — public API surface (5 exports)
- `app/engine/get_topic_context.py` — combined DB + RAG context lookup
- `app/engine/get_review_queue.py` — FSRS bucket query
- `app/engine/summarize_performance.py` — metrics + weakness patterns
- `app/engine/analyze_error.py` — post-insertion context synthesis
- `app/engine/generate_flashcards.py` — contextual LLM card generation (Claude Haiku)
- `app/engine/rag.py` — semantic search over resumos/ via ChromaDB + Ollama (Multi-Query + HyDE)

## The Pattern

**Public API (5 stable exports from `app.engine`):**
```python
from app.engine import (
    get_topic_context,       # dict with resumo + erros + cards + weak_areas + rag chunks
    get_review_queue,        # FSRS buckets: atrasados / hoje / novos
    summarize_performance,   # total_erros + taxa_acerto + padroes (weakness)
    generate_contextual_cards,  # list[dict] flashcards v5 (contextual or heuristic)
    analyze_error,           # post-insertion context + can_generate_cards flag
)
```

**Typical agent workflow (after `insert_questao.py` call):**
```python
from app.engine import analyze_error, generate_contextual_cards

resultado = analyze_error("Sepse Neonatal", area="Pediatria")
# resultado = {
#   "context": {resumo_path, resumo_content, erros_recentes, cards_ativos, weak_areas, relevant_chunks},
#   "resumo_available": True,
#   "can_generate_cards": True,
# }

if resultado["can_generate_cards"]:
    cards = generate_contextual_cards(
        tema="Sepse Neonatal",
        elo_quebrado="critério de SIRS em neonatos",
        armadilha="SIRS não se aplica igual a adultos",
        resumo_content=resultado["context"]["resumo_content"],
        relevant_chunks=resultado["context"]["relevant_chunks"],  # RAG-prioritized
    )
```

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

**Flashcard quality tiers:**
```python
# Tier 1: contextual (LLM-generated from resumo chunk — highest quality)
#   quality_source='contextual', needs_qualitative=0
# Tier 2: heuristic (rule-based inversion of elo_quebrado — fast fallback)
#   quality_source='heuristic', needs_qualitative=1
```

## Rules
- `app/engine/` functions NEVER raise exceptions — all errors are caught and return safe defaults (`[]`, `{}`, `None`)
- Resumo lookup uses fuzzy matching (`difflib.get_close_matches`, cutoff=0.6) — aliases in frontmatter expand the match surface
- RAG chunks (`relevant_chunks`) take priority over keyword-matched `resumo_content` for flashcard generation
- `generate_contextual_cards` calls `load_dotenv()` then checks `ANTHROPIC_API_KEY`; falls back to heuristic on any failure
- `search()` is safe to call unconditionally — returns `[]` when chromadb is absent or Ollama is offline
- `_CHROMA_AVAILABLE` flag is set at import time and can be checked for early-exit logic (avoids even calling `search()`)
- Engine functions do NOT write to the DB — write operations belong to `tools/insert_questao.py`
- The resumo index is lazy-loaded and in-process cached — new resumos added during a session won't be found without process restart
- HyDE document generation order: Anthropic Haiku → Ollama llama3 → raw query (graceful cascade)

## Examples from this codebase

File: `app/engine/analyze_error.py`
```python
def analyze_error(tema: str, area: Optional[str] = None) -> dict:
    try:
        ctx = get_topic_context(tema, area)
    except Exception:
        ctx = {"resumo_path": None, "resumo_content": None,
               "erros_recentes": [], "cards_ativos": 0, "weak_areas": []}
    resumo_available = ctx.get("resumo_path") is not None
    return {
        "context": ctx,
        "resumo_available": resumo_available,
        "can_generate_cards": resumo_available,
    }
```

File: `app/engine/generate_flashcards.py` — quality routing with dotenv
```python
def generate_contextual_cards(tema, elo_quebrado, armadilha=None,
                               resumo_content=None, relevant_chunks=None):
    if relevant_chunks:
        trecho = relevant_chunks[0]["text"]   # RAG wins
    elif resumo_content:
        trecho = _extract_relevant_section(resumo_content, elo_quebrado)  # keyword fallback
    else:
        return _heuristic_generate(elo_quebrado, armadilha)  # no resumo at all

    try:
        from dotenv import load_dotenv
        load_dotenv()
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY não definida")
        cards = _llm_generate(elo_quebrado, armadilha, trecho)
        for c in cards:
            c["quality_source"] = "contextual"
            c["needs_qualitative"] = 0
        return cards
    except Exception:
        return _heuristic_generate(elo_quebrado, armadilha)
```

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
- Using `generate_contextual_cards` without passing `relevant_chunks` from `get_topic_context()` — loses precision of RAG-targeted chunks
- Assuming resumo index is up-to-date during a long session — index is built once per process; restart if resumos were added
- Renaming `.md` files without re-running `tools/index_resumos.py` — leaves orphan chunks in ChromaDB with deterministic `{stem}::N` IDs
