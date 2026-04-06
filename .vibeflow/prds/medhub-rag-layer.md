# PRD: MedHub RAG Layer

> Generated via /vibeflow:discover on 2026-04-05

## Problem

`get_topic_context()` localiza resumos por fuzzy match em strings (`difflib.get_close_matches`). Funciona quando a query é próxima do nome do arquivo, mas falha em três cenários recorrentes:

1. **Query semântica sem overlap léxico** — "quando intubar RN prematuro" não bate em "Reanimação Neonatal"
2. **Trecho específico enterrado num resumo longo** — "confundi SIRS com qSOFA" precisa de 3 parágrafos de Sepse, não dos 4000 caracteres do arquivo inteiro
3. **Geração de flashcard sem contexto cirúrgico** — `generate_contextual_cards()` injeta o resumo completo no prompt; o LLM gera cards genéricos em vez de ancorar no trecho exato do erro

O `obsidian-notes-rag` MCP existe como dependência mas está explicitamente em anti-scope nas specs anteriores (não funciona adequadamente na prática).

## Target Audience

Daniel (único usuário) — estudante de residência médica usando o MedHub diariamente para revisar erros, gerar flashcards e navegar resumos clínicos.

## Proposed Solution

Camada RAG local sobre `resumos/**/*.md`:

- **Indexação:** cada resumo é chunkado por seção H2/H3, cada chunk vira um vetor via `nomic-embed-text` (Ollama, local, gratuito), armazenado num ChromaDB persistente em `data/chroma/`
- **Retrieval:** queries do engine (tema, elo_quebrado, pergunta) são transformadas em vetor e recuperam top-k chunks por similaridade cosseno
- **Integração cirúrgica no engine:** `get_topic_context()` adiciona chave `relevant_chunks` sem quebrar o contrato existente; `generate_contextual_cards()` usa chunks em vez do resumo inteiro
- **UI na Biblioteca:** caixa de busca semântica na tab "Resumos RAG" da `3_biblioteca.py`, mostrando chunks relevantes com link pro resumo de origem

## Success Criteria

1. `rag_search("quando intubar neonato")` retorna chunk de `Reanimação Neonatal.md` no top-3
2. `rag_search("SIRS qSOFA diferença")` retorna trecho específico de `Sepse.md` no top-3
3. Latência de retrieval < 200ms (ChromaDB local com ~44 resumos)
4. `generate_contextual_cards()` usa `relevant_chunks` ao invés do resumo completo — cards com referência direta ao trecho do erro
5. Caixa de busca na Biblioteca retorna resultados em < 1s

## Scope v0

- `app/engine/rag.py` — módulo com `index_resumo()`, `index_all()`, `search()`, `get_collection()`
- `tools/index_resumos.py` — CLI para (re)indexar todos os resumos; invocado manualmente ou ao adicionar novo resumo
- Integração em `get_topic_context()` — adiciona `relevant_chunks: list[dict]` ao dict retornado (safe default: `[]` se ChromaDB ausente)
- Integração em `generate_contextual_cards()` — usa `relevant_chunks` quando disponível
- `3_biblioteca.py` tab1 — `st.text_input` de busca semântica + renderização dos chunks com expansor por resultado
- `data/chroma/` no `.gitignore`
- Embedding model: `nomic-embed-text` via Ollama (ChromaDB `OllamaEmbeddingFunction`)

## Anti-scope

- **Sem indexar `ipub.db`** — erros já estão em `questoes_erros` e são acessados via `db.get_erros_por_tema()`; RAG é para o corpus de conhecimento (resumos), não para os erros
- **Sem busca híbrida (vetorial + keyword)** — ChromaDB puro com cosine; não usar Weaviate nem BM25
- **Sem reranking** — retornar top-k direto do ChromaDB sem segundo modelo de ranqueamento
- **Sem substituir `_find_resumo()`** — manter fuzzy match como fallback; RAG complementa, não substitui
- **Sem expor métricas de recall no UI** — avaliação offline via script separado, fora do app Streamlit
- **Sem auto-indexação ao salvar resumo** — reindexação é manual via CLI
- **Sem Pinecone, pgvector ou qualquer serviço cloud** — local only

## Technical Context

**Engine existente (`app/engine/`):**
- `get_topic_context()` retorna dict com 5 chaves; adicionar `relevant_chunks` como 6ª sem alterar as 5 existentes
- `generate_contextual_cards()` consome `resumo_content` hoje; passará a preferir `relevant_chunks` se presente
- Integração deve ser wrapped em `try/except` — ChromaDB ausente não pode quebrar o engine

**ChromaDB com Ollama:**
```python
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
ef = OllamaEmbeddingFunction(url="http://localhost:11434/api/embeddings", model_name="nomic-embed-text")
collection = client.get_or_create_collection("resumos", embedding_function=ef, metadata={"hnsw:space": "cosine"})
```

**Chunking:** split por `## ` e `### ` preservando header como metadata. Chunk mínimo: 50 chars. Chunk máximo: ~1500 chars (evitar tokens demais por chunk no prompt).

**Biblioteca (`3_biblioteca.py`):** já tem tab1 "Resumos RAG" com `os.walk`. Adicionar `st.text_input("Busca semântica")` + chamada ao `rag.search()` acima da lista de resumos existente.

**Convenções a seguir:**
- `import sqlite3` só em `app/utils/db.py` — ChromaDB não é sqlite3, pode ficar em `app/engine/rag.py`
- `data/chroma/` como diretório persistente (similar a `ipub.db` — local only)
- CLI em `tools/` com `argparse` e `finally: conn.close()` equivalente (ChromaDB não tem conn.close mas `client` deve ser instanciado por chamada no CLI)

## Open Questions

Nenhuma. Decisões tomadas na sessão de discovery:
- Embedding: `nomic-embed-text` via Ollama (não OpenAI)
- Biblioteca: entra no escopo
- Chunking: por H2/H3
- Persistência: ChromaDB local em `data/chroma/`
