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
`app/engine/` é a biblioteca de domínio de LEITURA para agentes: expõe uma função estável, `get_topic_context()`, que junta resumo, erros, cards, fraquezas da memória longa e trechos do RAG sobre `resumos/`. Não escreve no banco. Desde o F91 (s176), a degradação do RAG é declarada, nunca um `[]` mudo: a busca que não aconteceu é distinguível da busca que não achou nada.

## Where
- `app/engine/__init__.py` — superfície pública: 1 reexport (`get_topic_context`).
- `app/engine/get_topic_context.py` — contexto combinado (resumo + `db.get_erros_por_tema` + `db.get_cards_by_bucket` + `("medhub", "weak_areas")` + RAG).
- `app/engine/rag.py` — busca semântica sobre `resumos/` (ChromaDB `PersistentClient` em `data/chroma/`, coleção única `resumos`, embeddings `nomic-embed-text` via Ollama). Módulo interno: `from app.engine.rag import search, index_all`.
- `tools/index_resumos.py` — (re)indexação; `--clear` depois de renomear resumo.
- Performance e fraquezas NÃO são assunto do engine: skill `/performance` e os CLIs de `tools/`.

## The Pattern

**API pública:**
```python
from app.engine import get_topic_context

ctx = get_topic_context("Sepse Neonatal", area="Pediatria")
# chaves sempre presentes: resumo_path, resumo_content, erros_recentes,
#   cards_ativos, weak_areas, relevant_chunks
# chave extra quando o RAG degradou: rag_degradado (str com o motivo)
```

**Degradação declarada no payload (`get_topic_context`, trecho):**
```python
    try:
        result["relevant_chunks"] = rag_search(tema, n_results=3)
    except RagIndisponivel as e:
        result["relevant_chunks"] = []
        result["rag_degradado"] = str(e)
        print(f"[WARN] get_topic_context: {e}", file=sys.stderr)
```

**`search()`: semântico -> fallback léxico marcado -> `RagIndisponivel` (`rag.py`, trecho):**
```python
    if not _CHROMA_AVAILABLE:
        return _degradar(query, n_results, area, motivo="ChromaDB ausente do ambiente")
    try:
        query_texts = [query]
        if use_hyde:
            # HyDE e get_collection() rodam em paralelo: latência = max(ambos), não soma
            with ThreadPoolExecutor(max_workers=2) as ex:
                f_hyde = ex.submit(_generate_hypothetical_document, query)
                f_coll = ex.submit(get_collection)
                collection = f_coll.result()
                query_texts.append(f_hyde.result())
        ...
        combined.sort(key=lambda x: x["distance"])
        # 🔴 F91: ESTE e o unico `[]` honesto de search() -- o motor rodou, consultou o
        # indice e nao achou nada acima do corte. Fail-loud nao pode virar fail-sempre.
        return combined[:n_results]
    except RagIndisponivel:
        raise
    except Exception as e:
        return _degradar(query, n_results, area, motivo=f"{type(e).__name__}: {e}")
```
`_degradar()` avisa em stderr, tenta `_textual_fallback()` (hits com `metadata['source'] == 'fallback_textual'` e `distance = None`) e, se nada casar, levanta `RagIndisponivel`.

**Indexação com contexto propagado e poda de cauda (`index_resumo`, trecho):**
```python
    tema = path.stem
    aliases = fm.get("aliases", [])
    alias_str = f" ({', '.join(aliases)})" if aliases else ""
    contexto_global = f"[{tema}{alias_str} > "
    for i, chunk in enumerate(chunks):
        ids.append(f"{path.stem}::{i}")
        texto_enriquecido = f"{contexto_global}{chunk['header']}]\n{chunk['text']}"
        ...
        # F48 (descolar part-5): resumo que ENCOLHEU deixava cauda {stem}::N órfã no índice,
        # servindo texto desatualizado (6 chunks stale medidos na s160). Deleta o excedente.
```
`index_all()` grava o carimbo `data/chroma/index_meta.json` (`gravar_carimbo_indexacao`), que o sensor `RAG_STALE` do `auto_check` lê (`tools/utils/state_utils.py::check_rag_staleness`, WARN).

## Rules
- `get_topic_context()` não levanta: cada bloco tem `try/except` com default seguro; a falha do RAG vira `rag_degradado` + `[WARN]` em stderr.
- `search()` PODE levantar `RagIndisponivel`. Quem a chama direto captura e reporta "não consegui buscar", nunca "não existe" (honest-negative, `core/contracts/evidence-governance.md`).
- `[]` de `search()` só significa "o motor rodou e nada passou do corte" (`max_distance=0.35`).
- Hit degradado é marcado `source='fallback_textual'`; o consumidor separa o degradado do semântico.
- HyDE: Anthropic Haiku (timeout 30 s, `temperature=0`) -> a própria query. O tier Ollama/llama3 foi removido em 2026-08-14. Cache de sessão em `_HYDE_CACHE`.
- Busca de resumo: match exato no índice e depois `difflib.get_close_matches(..., cutoff=0.6)`; o `path.stem` tem precedência, `aliases`/`especialidade`/`area` do frontmatter são apontadores fracos.
- O índice de resumos é lazy e fica em cache no processo: resumo novo só aparece depois de reiniciar o processo.
- IDs determinísticos `{stem}::N`: o encolhimento é podado na indexação (F48); a renomeação ainda deixa órfãos -> `python tools/index_resumos.py --clear`.
- O engine não escreve no `ipub.db`.

## Examples from this codebase
- `app/engine/get_topic_context.py::get_topic_context` — os 5 blocos e a degradação declarada.
- `app/engine/get_topic_context.py::_find_resumo` — match exato + fuzzy.
- `app/engine/rag.py::search`, `_degradar`, `_textual_fallback`, `RagIndisponivel` — fail-loud (F91).
- `app/engine/rag.py::index_resumo`, `caudas_orfas`, `index_all` — indexação e poda (F48).
- Testes: `tools/test_rag_fail_loud.py`, `tools/test_rag_sensores.py`.
<!-- vibeflow:auto:end -->

## Anti-patterns
- Importing `app.utils.db` directly from agent workflows — use `app.engine` functions which handle errors gracefully
- Calling `rag.search()` without checking `_CHROMA_AVAILABLE` first — will raise ImportError if chromadb not installed
- Assuming resumo index is up-to-date during a long session — index is built once per process; restart if resumos were added
- Renaming `.md` files without re-running `tools/index_resumos.py` — leaves orphan chunks in ChromaDB with deterministic `{stem}::N` IDs
