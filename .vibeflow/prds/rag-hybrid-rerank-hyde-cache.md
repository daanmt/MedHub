# PRD: RAG Hybrid Re-ranking + HyDE Latency Optimization

> Generated via /vibeflow:discover on 2026-04-07

## Problem

O RAG atual (ChromaDB + nomic-embed-text + Multi-Query + HyDE) atinge 90% Recall@5 e MRR 0.708 no benchmark de 10 queries médicas reais. O caso de falha documentado — "Diferença clínica de placenta prévia de DPP" — não retornou `[OBS] Sangramentos da Segunda Metade.md` no Top 5, porque embeddings densos confundem o campo semântico de "sangramento obstétrico" entre resumos de primeira e segunda metade da gestação.

O padrão de falha é estrutural e vai se repetir: qualquer par de resumos com vocabulário clínico sobreposto (termos como "sangramento", "sepse", "hipertensão", "RN") vai causar confusão de escopo no espaço vetorial. Metadata filtering (`where=especialidade`) resolve o caso pontual mas não o padrão geral — não escala.

Além disso, a latência atual de 6.31s (HyDE Haiku + embed + query + dedup) é aceitável, mas o gargalo do HyDE é síncrono: a geração do documento hipotético bloqueia o embed bruto da query original, adicionando ~2-3s desnecessários em queries já vistas na sessão.

## Target Audience

Sistema interno — o próprio RAG pipeline (`app/engine/rag.py`) que alimenta `get_topic_context`, `analyze_error`, e a página `3_biblioteca.py`. Impacto direto na qualidade de flashcards gerados e no contexto enviado ao agente de análise de erros.

## Proposed Solution

Duas melhorias independentes, mesma fase:

**1. BM25 Post-Chroma Re-ranker**
Após a query ao ChromaDB retornar `k*2` chunks (já implementado no `search()`), aplicar re-ranking BM25 (`rank_bm25`) sobre esses chunks como segunda etapa de ordenação. O score final é uma combinação linear de distância coseno (normalizada) e score BM25 (normalizado). Não há índice paralelo — BM25 opera em tempo de query sobre os documentos já recuperados do Chroma.

**2. HyDE Session Cache + Async Dispatch**
- Cache em memória (dict `query → hypothetical_doc`) com TTL de sessão — queries repetidas na mesma instância Streamlit não re-chamam o Haiku.
- Dispatch assíncrono: geração do documento hipotético e embed bruto da query original rodam em paralelo via `asyncio` (ou `ThreadPoolExecutor` se o Streamlit blocking model não suportar asyncio limpo). O TTFT cai pela latência do maior dos dois, não pela soma.

## Success Criteria

1. A query "Diferença clínica de placenta prévia de DPP" retorna `[OBS] Sangramentos da Segunda Metade.md` em Rank ≤ 3 no benchmark atual de 10 queries.
2. Nenhum acerto existente regride (9 queries que já passavam continuam passando — Recall@5 ≥ 90%, MRR ≥ 0.708).
3. Latência em query com HyDE e cache hit (segunda chamada à mesma query) ≤ 4.0s (redução ≥ 35% sobre os 6.31s atuais).

## Scope v0

- `app/engine/rag.py`: adicionar função `_bm25_rerank(chunks, query)` e integrá-la no final do pipeline `search()` (pós-dedup, pré-slice `[:n_results]`)
- `app/engine/rag.py`: adicionar `_HYDE_CACHE: dict[str, str]` em módulo-level e lookup no `_generate_hypothetical_document()`
- `app/engine/rag.py`: paralelizar chamada HyDE + embed bruto com `concurrent.futures.ThreadPoolExecutor` (compatível com Streamlit's sync context)
- Adicionar `rank-bm25` a `requirements.txt`
- Rodar benchmark manual das 10 queries após implementação e registrar Rank do caso de falha

## Anti-scope

- Não criar harness de avaliação formal (pytest fixtures com ground truth) — sprint futura
- Não construir índice BM25 paralelo ou persistido — apenas re-ranking in-memory dos chunks Chroma
- Não expandir para 30+ queries de teste nesta fase
- Não alterar a lógica de indexação (`tools/index_resumos.py`) — context propagation prefix permanece como está
- Não adicionar metadata filtering como mecanismo de re-ranking (resolve pontualmente, não o padrão)
- Não substituir ChromaDB — continua como retriever primário; BM25 é segunda camada
- Não tocar em `tools/insert_questao.py`, FSRS, ou qualquer módulo fora de `app/engine/rag.py` + `requirements.txt`

## Technical Context

**Pipeline atual em `app/engine/rag.py`:**
```
query
  → [HyDE] _generate_hypothetical_document() → Haiku → Ollama llama3 → raw fallback
  → collection.query([query, hyde_doc], n_results=k*2, where=where)
  → dedup por texto + filtro max_distance (0.35)
  → sorted(by distance)[:n_results]   ← BM25 entra aqui, antes do slice
```

**BM25 re-ranking (abordagem):**
```python
from rank_bm25 import BM25Okapi

def _bm25_rerank(chunks: list[dict], query: str, alpha: float = 0.5) -> list[dict]:
    corpus = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(corpus)
    bm25_scores = bm25.get_scores(query.lower().split())
    # Normalizar scores para [0,1]
    max_bm25 = max(bm25_scores) or 1.0
    for i, chunk in enumerate(chunks):
        norm_bm25 = bm25_scores[i] / max_bm25
        norm_cosine = 1.0 - (chunk["distance"] / 0.35)  # inverte: menor dist = maior score
        chunk["_hybrid_score"] = alpha * norm_cosine + (1 - alpha) * norm_bm25
    return sorted(chunks, key=lambda x: x["_hybrid_score"], reverse=True)
```
O `alpha=0.5` é ajustável — começar com 0.5, ajustar empiricamente se o benchmark indicar dominância de um lado.

**HyDE cache (abordagem):**
```python
_HYDE_CACHE: dict[str, str] = {}  # module-level, TTL = processo

def _generate_hypothetical_document(query: str) -> str:
    if query in _HYDE_CACHE:
        return _HYDE_CACHE[query]
    doc = _call_haiku_or_ollama(query)
    _HYDE_CACHE[query] = doc
    return doc
```

**Parallelização (abordagem):**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as ex:
    f_hyde = ex.submit(_generate_hypothetical_document, query)
    f_embed = ex.submit(lambda: query)  # embed bruto é no-op aqui, ChromaDB aceita texto direto
    hyde_doc = f_hyde.result()
    # Ambos prontos — montar query_texts = [query, hyde_doc]
```
Nota: ChromaDB aceita `query_texts` (strings) direto — o embed é feito internamente. O ganho real do parallelismo é quando HyDE usa API externa (Haiku): a latência de rede não bloqueia mais o pipeline.

**Arquivos afetados:** apenas `app/engine/rag.py` + `requirements.txt`. Budget ≤ 2 arquivos.

**Padrões a seguir:**
- `app/engine/` functions NEVER raise — todos os erros em BM25/cache devem ter fallback gracioso (retornar chunks sem re-rank se `rank_bm25` falhar)
- `_CHROMA_AVAILABLE` flag já existente — verificar antes de qualquer operação
- Nenhum `import sqlite3` fora de `app/utils/db.py`

## Open Questions

Nenhuma.
