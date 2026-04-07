# Spec: RAG Hybrid Re-ranking + HyDE Latency Optimization

> Generated via /vibeflow:gen-spec on 2026-04-07
> PRD: `.vibeflow/prds/rag-hybrid-rerank-hyde-cache.md`
> Budget: ≤ 6 files (project default) — this spec touches 2 files only

---

## Objective

Adicionar BM25 como camada de re-ranking pós-ChromaDB no `search()` e reduzir latência do HyDE via cache de sessão + paralelismo `ThreadPoolExecutor`, de forma que o caso de falha documentado (Placenta Prévia/DPP) passe para Rank ≤ 3 sem regredir os 9 acertos existentes.

---

## Context

**O que existe hoje em `app/engine/rag.py`:**

Pipeline em `search()`:
```
query
  → if use_hyde: _generate_hypothetical_document(query)   # síncrono — bloqueia
  → get_collection()                                       # síncrono — bloqueia
  → collection.query([query, hyde_doc], n_results=k*2)
  → dedup por texto + filtro max_distance (0.35)
  → combined.sort(key=lambda x: x["distance"])            # ← BM25 entra aqui
  → return combined[:n_results]
```

Problema 1 (qualidade): `combined.sort()` ordena só por distância coseno. Para pares com vocabulário sobreposto ("sangramento obstétrico" em Primeira vs Segunda Metade), o embedding denso não consegue separar por tópico — BM25 adiciona sinal léxico que penaliza chunks fora do escopo exacto da query.

Problema 2 (latência): `_generate_hypothetical_document()` e `get_collection()` rodam sequencialmente. A chamada ao Haiku (~2-3s de rede) bloqueia a inicialização do client ChromaDB que poderia ocorrer em paralelo.

**Por que agora:** corpus de 44 resumos está crescendo e o padrão de falha (vocabulário sobreposto entre especialidades de obstetrícia) vai se repetir com pré-eclâmpsia/eclâmpsia, RN precoce/tardio, etc.

---

## Definition of Done

Todos os checks abaixo devem passar (pass/fail, sem ambiguidade):

- [ ] **DoD-1 (falha documentada):** A query `"Diferença clínica de placenta prévia de DPP"` retorna um chunk de `[OBS] Sangramentos da Segunda Metade.md` como Rank 1, 2 ou 3 no resultado de `search()`.

- [ ] **DoD-2 (regressão zero):** As 9 queries que passavam no benchmark anterior continuam com o chunk correto em Rank ≤ 5 (Recall@5 ≥ 90%, MRR ≥ 0.708). Verificar manualmente rodando as 10 queries após implementação.

- [ ] **DoD-3 (cache funcional):** Segunda chamada a `search("Diferença clínica de placenta prévia de DPP")` na mesma sessão Python não chama `_generate_hypothetical_document()` novamente — verificável via log ou mock em teste manual.

- [ ] **DoD-4 (fallback BM25):** Se `rank_bm25` não estiver instalado (ou scores todos-zero), `search()` retorna os chunks ordenados por distância coseno sem lançar exceção. O fallback é silencioso.

- [ ] **DoD-5 (fallback seguro preservado):** `search()` continua retornando `[]` quando `_CHROMA_AVAILABLE = False` — regressão zero no caminho de fallback existente.

- [ ] **DoD-6 (sem raises em engine):** Nenhuma função nova ou modificada em `app/engine/rag.py` lança exceção para fora do módulo. Todos os blocos novos têm `try/except` com retorno seguro. Conforme `domain-engine-api` pattern e `conventions.md Don'ts`.

- [ ] **DoD-7 (alpha correto):** `_bm25_rerank()` usa `alpha=0.6` como default — coseno com 60% de peso, BM25 com 40%. Confirmado na assinatura da função.

---

## Scope

Apenas `app/engine/rag.py` e `requirements.txt`.

**Mudanças em `app/engine/rag.py`:**

1. **`_HYDE_CACHE`** — dict module-level:
   ```python
   _HYDE_CACHE: dict[str, str] = {}
   ```
   Inserido após as constantes existentes (`_MIN_CHUNK_CHARS`, `_MAX_CHUNK_CHARS`).

2. **`_generate_hypothetical_document()`** — lookup de cache no início da função, antes de qualquer chamada de rede:
   ```python
   if query in _HYDE_CACHE:
       return _HYDE_CACHE[query]
   # ... lógica existente ...
   _HYDE_CACHE[query] = resultado
   return resultado
   ```

3. **`_bm25_rerank(chunks, query, alpha=0.6)`** — nova função privada:
   ```python
   def _bm25_rerank(chunks: list[dict], query: str, alpha: float = 0.6) -> list[dict]:
       try:
           from rank_bm25 import BM25Okapi
           corpus = [c["text"].lower().split() for c in chunks]
           bm25 = BM25Okapi(corpus)
           scores = bm25.get_scores(query.lower().split())
           max_score = max(scores) if max(scores) > 0 else 1.0
           max_dist = max((c["distance"] for c in chunks), default=0.35) or 0.35
           for i, chunk in enumerate(chunks):
               norm_bm25 = scores[i] / max_score
               norm_cosine = 1.0 - (chunk["distance"] / max_dist)
               chunk["_hybrid_score"] = alpha * norm_cosine + (1 - alpha) * norm_bm25
           return sorted(chunks, key=lambda x: x["_hybrid_score"], reverse=True)
       except Exception:
           return chunks  # fallback: ordem coseno original
   ```
   Nota: `max_dist` calculado sobre os chunks reais (não hardcoded 0.35) — mais robusto para chamadas com `max_distance` customizado.

4. **`search()`** — duas modificações:

   a. Paralelizar HyDE + `get_collection()` com `ThreadPoolExecutor`:
   ```python
   from concurrent.futures import ThreadPoolExecutor

   # Substitui o bloco atual:
   # query_texts = [query]
   # if use_hyde:
   #     query_texts.append(_generate_hypothetical_document(query))
   # collection = get_collection()

   # Por:
   query_texts = [query]
   if use_hyde:
       with ThreadPoolExecutor(max_workers=2) as ex:
           f_hyde = ex.submit(_generate_hypothetical_document, query)
           f_coll = ex.submit(get_collection)
           collection = f_coll.result()
           query_texts.append(f_hyde.result())
   else:
       collection = get_collection()
   ```

   b. Substituir `combined.sort()` por `_bm25_rerank()` (pré-slice):
   ```python
   # Substitui:
   # combined.sort(key=lambda x: x["distance"])
   # return combined[:n_results]

   # Por:
   combined = _bm25_rerank(combined, query)
   return combined[:n_results]
   ```

**Mudança em `requirements.txt`:**
- Adicionar linha: `rank-bm25`

---

## Anti-scope

- **Sem índice BM25 persistido** — BM25 opera em tempo de query sobre os chunks já recuperados do Chroma. Sem `bm25s`, sem serialização, sem cache de corpus.
- **Sem metadata filtering** como mecanismo de re-ranking (`where=especialidade`).
- **Sem harness de avaliação formal** (pytest com ground truth) — validação é manual com as 10 queries do benchmark.
- **Sem alterações em `tools/index_resumos.py`** — context propagation prefix inalterado.
- **Sem alterações fora de `app/engine/rag.py` + `requirements.txt`** — `insert_questao.py`, FSRS, páginas Streamlit, `db.py`: todos intocados.
- **Sem substituição do ChromaDB** — continua como retriever primário; BM25 é segunda camada.
- **Sem ajuste automático de `alpha`** — `alpha=0.6` fixo nesta fase; ajuste empírico fica para sprint futura se o benchmark indicar dominância excessiva de um lado.
- **Sem LRU ou TTL temporal no `_HYDE_CACHE`** — corpus é estável por sessão; invalidação manual via restart do processo.

---

## Technical Decisions

| Decisão | Escolha | Justificativa |
|---|---|---|
| Re-ranker | `BM25Okapi` (rank-bm25) | Lib pura Python, sem infraestrutura. Opera sobre strings já em memória — zero latência de I/O. |
| `alpha` default | `0.6` (coseno dominante) | Vocabulário clínico denso → semântica ainda é o árbitro principal. BM25 entra para desempate léxico. Ajustar se benchmark regredir. |
| Normalização coseno | `1.0 - dist / max_dist_real` | `max_dist` calculado sobre os chunks reais (não hardcoded 0.35) — correto quando `max_distance` é passado como argumento. |
| Parallelismo | `ThreadPoolExecutor(max_workers=2)` | Compatível com Streamlit sync context (sem asyncio event loop). Paraleliza HyDE (I/O de rede) com `get_collection()` (I/O de disco). |
| O que paralelizar | `_generate_hypothetical_document` + `get_collection()` | Esses são os dois blocos de latência real. O "embed bruto" não é uma etapa separada — ChromaDB embeds internamente via `query_texts`. |
| Cache HyDE | `dict[str, str]` module-level | TTL = processo. Sem lock explícito — write atômico em CPython (GIL). Worst case em multithread = duplicata de chamada, não corrupção. |
| Fallback BM25 | `except Exception: return chunks` | Cobre `ImportError` (rank-bm25 não instalado), `ValueError` (corpus vazio), e qualquer edge case. Retorna ordem coseno original silenciosamente. |

---

## Applicable Patterns

- **`domain-engine-api` pattern** (`app/engine/rag.py`): funções NEVER raise, fallback gracioso, `_CHROMA_AVAILABLE` verificado antes de qualquer operação. `_bm25_rerank()` deve seguir o mesmo contrato.
- **`db-access-layer` pattern**: nenhum `import sqlite3` adicionado — BM25 não toca no banco.

**Novo padrão introduzido (documentar em `.vibeflow/patterns/domain-engine-api.md` após implementação):**
- BM25 post-Chroma re-ranking: `_bm25_rerank(chunks, query, alpha)` como estágio final antes do slice `[:n_results]`. Alpha = 0.6 para corpus médico (coseno dominante).

---

## Risks

| Risco | Probabilidade | Mitigação |
|---|---|---|
| `max(scores) == 0` (query sem overlap lexical com corpus) | Baixa — vocabulário clínico sempre tem algum overlap | `max_score = max(scores) if max(scores) > 0 else 1.0` |
| ThreadPoolExecutor overhead em queries com Ollama offline (cache hit rápido) | Média — executor cria threads mesmo para work rápido | Overhead de `ThreadPoolExecutor` em work < 1ms é ~0.1ms. Aceitável. Alternativa: só parallelizar se estimativa de latência > threshold — over-engineering para este caso. |
| BM25 favorece termos raros de forma excessiva no corpus de 44 docs (IDF muito alto para termos únicos) | Média | `alpha=0.6` limita influência do BM25. Caso regrida em benchmark: baixar para `alpha=0.7`. |
| Race condition em `_HYDE_CACHE` sob Streamlit multi-usuário | Baixa — instância local, single-user | Sem lock por ora. Revisitar se migrar para servidor multi-user. |

---

## Dependencies

Nenhuma. Spec auto-contida, opera apenas em `app/engine/rag.py`.
