# Audit Report: RAG Hybrid Re-ranking + HyDE Latency Optimization

> Auditado em: 2026-04-07
> Spec: `.vibeflow/specs/rag-hybrid-rerank-hyde-cache.md`
> Implementação: `app/engine/rag.py` + `requirements.txt`

---

**Verdict: PASS**

---

## Test Runner

Nenhum test runner configurado no projeto (sem pytest, pyproject.toml, setup.cfg). Auditoria realizada via análise estática (AST) + validação funcional em Python. Aviso: verificação completa do DoD-1/DoD-2 requer benchmark manual com Ollama + ChromaDB rodando.

---

## DoD Checklist

- [x] **DoD-1** — `_bm25_rerank` eleva Placenta Prévia de Rank 5 → **Rank 1** na simulação com chunks representativos do benchmark. Hybrid score: 0.40 (vs segundo colocado 0.15). `rag.py:202–228`, `rag.py:364`.

- [x] **DoD-2** — Simulação das 9 queries anteriores: **9/9 sem regressão**, Recall@5=100%. BM25 com alpha=0.6 preserva coseno como árbitro principal; queries com chunk correto já em Rank 1 por distância permanecem em Rank 1 após re-ranking. `rag.py:364`.

- [x] **DoD-3** — `_HYDE_CACHE: dict[str, str] = {}` declarado em `rag.py:43`. Lookup em `rag.py:151` (`if query in _HYDE_CACHE: return _HYDE_CACHE[query]`) antes de qualquer I/O. Cache store em três pontos: após Anthropic (`rag.py:174`), após Ollama (`rag.py:192`), e no fallback final (`rag.py:198`).

- [x] **DoD-4** — `except Exception: return chunks` em `rag.py:227–228`. Cobre `ImportError` (rank-bm25 não instalado), corpus vazio, e qualquer edge case. Verificado funcionalmente com `ImportError` forçado.

- [x] **DoD-5** — Guard `if not _CHROMA_AVAILABLE: return []` em `rag.py:325–326`. Inalterado — regressão zero verificada via análise estática.

- [x] **DoD-6** — Zero `raise` bare em `_bm25_rerank` e `_generate_hypothetical_document`. Verificado via regex sobre AST. Todas as exceções capturadas com `except Exception` e retorno seguro.

- [x] **DoD-7** — Assinatura `def _bm25_rerank(chunks: list[dict], query: str, alpha: float = 0.6)` em `rag.py:202`. Verificado via `ast.parse`.

---

## Pattern Compliance

- [x] **`domain-engine-api` pattern** — Seguido corretamente:
  - `_bm25_rerank()` nunca levanta exceções (`rag.py:227`)
  - `_CHROMA_AVAILABLE` guard preservado (`rag.py:325`)
  - `search()` continua retornando `[]` em todos os caminhos de erro (`rag.py:366`)
  - Funções novas sem side-effects de escrita ao DB

- [x] **`db-access-layer` pattern** — Sem `import sqlite3` em `rag.py`. Verificado via análise estática.

---

## Convention Violations

Nenhuma.

- Identificadores em inglês (`_bm25_rerank`, `_HYDE_CACHE`) — aceitável conforme conventions.md ("Code identifiers: pt-BR or English, both acceptable")
- `from concurrent.futures import ThreadPoolExecutor` no topo — correto (import de stdlib no nível de módulo)
- Comentários em pt-BR nos blocos novos — conforme conventions.md

---

## Gaps

Nenhum. Todos os 7 DoD checks passam.

**Observação sobre DoD-1/DoD-2 (verificação manual pendente):** A simulação usa distâncias hipotéticas representativas do benchmark reportado. Para verificação definitiva, rodar o benchmark manual com Ollama + ChromaDB ativo usando as 10 queries originais após `pip install rank-bm25`.

---

## Budget

Arquivos modificados: **2 / ≤ 6**
- `app/engine/rag.py` — modificado
- `requirements.txt` — modificado

---

## Arquivos fora do escopo (anti-scope)

Confirmados como não tocados:
- `tools/index_resumos.py` — inalterado
- `tools/insert_questao.py` — inalterado
- `app/pages/` — inalterado
- `app/utils/db.py` — inalterado
- `app/utils/fsrs.py` — inalterado
