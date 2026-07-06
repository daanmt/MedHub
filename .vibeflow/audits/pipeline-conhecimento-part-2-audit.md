# Audit Report: pipeline-conhecimento-part-2 (RAG two-tier / F17)

**Verdict: PASS**

> Auditado 2026-07-06. Spec: `.vibeflow/specs/pipeline-conhecimento-part-2.md`.
> Tests: 48 passed (era 41; +7 de test_rag_two_tier, inclui 1 live end-to-end com
> Ollama+ChromaDB). Critical Gate: limpo. Gold real intocado (1048 chunks).

### DoD Checklist
- [x] **1 — Collection `pdf_raw` separada, `source=pdf_raw`+origem, gold byte-identico.**
  `app/engine/rag.py`: `get_pdf_collection` (collection isolada), `index_pdf` grava
  `metadata={source:'pdf_raw', origem:<path>, tema, mtime}`. Gold verificado: `get_collection`,
  `search`, `index_all`, `index_resumo`, `_chunk_by_headers` NAO editados; collection `resumos`
  segue com 1048 chunks pos-mudanca. Live test confirma o marcador `source=pdf_raw`.
- [x] **2 — Incremental por mtime + `--clear` so pdf_raw.** `index_pdf` pula quando o mtime
  bate (`test_index_pdf_incremental_skip`) e reindexa quando muda
  (`test_index_pdf_reindex_on_mtime_change`, deleta chunks stale do source antes de reinserir).
  `index_pdfs_raw(clear=True)` faz `delete_collection(PDF_COLLECTION_NAME)` -- so o bruto.
- [x] **3 — Gold-primeiro, fallback marcado, sombreamento.** `search_two_tier`: gold via
  `search` primeiro; so complementa ate n_results pelo bruto quando o gold nao preenche; hits
  do bruto marcados `source=pdf_raw`. `_aplica_sombreamento` descarta temas ja no gold, dups e
  hits > max_distance (`test_aplica_sombreamento`). Live: tema orfao (Meckel) -> hit pdf_raw;
  tema com gold (Apendicite) -> pdf_raw do mesmo tema NAO vaza.
- [x] **4 — Testes 3 casos + fallback offline.** `tools/test_rag_two_tier.py` (7 testes):
  logica pura (chunk/norm/sombreamento/incremental) sempre roda; `test_two_tier_live` cobre
  orfao+sombreamento com Ollama e da SKIP gracioso se offline. `search_two_tier` retorna gold
  (`[]`) se Chroma/Ollama offline (nunca raise).
- [x] **5 — Craftsmanship (aditivo).** 234 linhas SO de adicao em rag.py; assinaturas publicas
  `search`/`index_all`/`_CHROMA_AVAILABLE` inalteradas; sem dependencia nova (reusa
  chromadb/nomic + `extract_pdfs.extract_pdf`); fallback silencioso preservado; adicoes
  ASCII-limpas (em-dash e "Nº" corrigidos).
- [x] **6 — `data/chroma` local-only, PDF nao deletado.** `_extract_via_temp` remove SO o
  arquivo temp (`os.remove(tmp)`), nunca o PDF; nenhuma escrita fora de `data/chroma`.

### Pattern Compliance
- [x] **domain-engine-api** — RAG via engine; `search_two_tier` e nova superficie estavel;
  fallback seguro (`[]`) mantido.
- [x] **index_resumos.py (padrao CLI)** — `index_pdf_raw.py` espelha argparse/`--dir`/`--clear`,
  deteccao de Ollama offline, exit codes e tabela de saida.
- [x] **Two-tier ai-eng (ADR-002)** — o PDF nunca vira canon por existir; o `.md` sombrea o
  PDF do mesmo tema no fallback (`_aplica_sombreamento`).

### Convention Violations
Nenhuma.

### Critical Gate
Clean — no destructive operations detected.
- `app/engine/rag.py`: adicoes puras. `delete_collection(PDF_COLLECTION_NAME)` (linha ~541) e
  o `--clear` ESCOPADO ao tier bruto -- documentado na spec (DoD #2), gold intocado, tratado
  como override. `collection.delete(where={origem})` (~514) e reindex incremental escopado por
  PDF. `os.remove(tmp)` (~473) remove so o temp. Nenhum keyword de mass-delete
  (`delete_all`/`purge`/`bulk_delete`), nenhum `DROP`/`DELETE FROM` (arquivo .py, nao SQL),
  nenhum exec dinamico/secret hardcoded.

### Budget
4 / <=6 arquivos: modifica `app/engine/rag.py` (+234, aditivo) e `pytest.ini` (+allowlist);
cria `tools/index_pdf_raw.py` e `tools/test_rag_two_tier.py`.

### Anti-scope
Respeitado: chunking/collection/qualidade do gold intocados; sem embeddings/modelo/dep nova;
PDF nao promovido a canon; sem UI; PDF nao deletado.

### Nota operacional (nao bloqueia)
A 1a indexacao real do `pdf_raw` (333 PDFs) ainda NAO foi executada -- o mecanismo esta
verificado (live test em corpus temp), mas o corpus real de PDFs so entra na busca apos rodar
`python tools/index_pdf_raw.py` (custo one-shot, incremental depois). Alinhado a "Perguntas em
aberto" da spec (volume da 1a indexacao). Deixado como passo operacional do operador.
