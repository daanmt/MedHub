# Spec: MedHub RAG Layer — Part 1: Engine Core

> Generated via /vibeflow:gen-spec on 2026-04-05
> PRD: .vibeflow/prds/medhub-rag-layer.md

## Objective

Criar a camada RAG local sobre `resumos/**/*.md` — ChromaDB + nomic-embed-text via Ollama — e expor `relevant_chunks` no contrato de `get_topic_context()` sem quebrar callers existentes.

## Context

Hoje `_find_resumo()` em `get_topic_context.py` usa `difflib.get_close_matches` com cutoff 0.6. Falha em queries semânticas sem overlap léxico (ex: "intubar RN prematuro" → "Reanimação Neonatal"). Não existe indexação vetorial no projeto. O `obsidian-notes-rag` MCP está listado como dependência no `index.md` mas foi explicitamente descartado nas specs anteriores por não funcionar na prática.

`generate_flashcards.py` já tem `_extract_relevant_section()` que faz keyword match em H3 headers — funciona como fallback, mas será substituído por RAG na Part 2.

## Definition of Done

1. `app/engine/rag.py` existe com `get_collection()`, `index_resumo(path)`, `index_all()`, `search(query, n_results, area)` — importável sem erro mesmo com ChromaDB ausente do ambiente (ImportError capturado no topo do módulo)
2. `_chunk_by_headers(content)` implementa as três regras: split em `## ` e `### `; merge de chunk resultante < 100 chars no chunk anterior; split de chunk > 1500 chars no `\n\n` mais próximo do ponto médio — retorna `list[dict]` com chaves `header` e `text`
3. `tools/index_resumos.py` indexa todos os resumos em `resumos/**/*.md` via `index_all()`, imprime contagem de chunks por arquivo, termina com exit 0
4. `get_topic_context()` retorna `relevant_chunks: list[dict]` como 6ª chave — cada item com `text`, `metadata` (source, section, area, especialidade), `distance`; defaults a `[]` quando ChromaDB ou Ollama indisponível; nenhuma exceção propaga para o caller
5. `data/chroma/` adicionado ao `.gitignore`
6. **Quality gate:** `app/engine/rag.py` não contém `import sqlite3`; nenhum `import chromadb` fora de `app/engine/rag.py` e `tools/index_resumos.py`; sem violações dos Don'ts de `conventions.md`

## Scope

- **`app/engine/rag.py`** (novo) — módulo RAG completo
- **`tools/index_resumos.py`** (novo) — CLI de indexação
- **`app/engine/get_topic_context.py`** (modificar) — adicionar `relevant_chunks` ao dict de retorno
- **`.gitignore`** (modificar) — adicionar `data/chroma/`

## Anti-scope

- Não indexar `ipub.db` nem `questoes_erros` — RAG é só para resumos
- Não expor métricas de recall ou latência no UI
- Não substituir `_find_resumo()` — mantê-la como fallback (a RAG complementa)
- Não modificar `generate_flashcards.py` — isso é Part 2
- Não modificar `3_biblioteca.py` — isso é Part 2
- Não adicionar busca híbrida (BM25 + vetorial)
- Não usar `text-embedding-3-small` nem qualquer embedding pago

## Technical Decisions

### ChromaDB + OllamaEmbeddingFunction
```python
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "resumos"

def get_collection():
    import chromadb
    ef = OllamaEmbeddingFunction(url=OLLAMA_URL, model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
```
**Rationale:** ChromaDB PersistentClient persiste em disco como SQLite faz — zero infra, local only, coerente com o padrão do projeto. nomic-embed-text via Ollama é gratuito e já está no stack (Ollama roda localmente para simulados).

### Guarda de importação
```python
try:
    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False
```
`search()` retorna `[]` quando `_CHROMA_AVAILABLE is False`. Isso garante que o engine não quebra em ambientes sem ChromaDB instalado (ex: Streamlit Cloud).

### Algoritmo de chunking `_chunk_by_headers()`

**Input:** conteúdo completo do `.md` (com frontmatter).

**Passos:**
1. Remover o bloco frontmatter (entre `---` iniciais) antes de processar
2. Split nas linhas que começam com `## ` ou `### ` — cada header abre um novo chunk
3. Conteúdo antes do primeiro header → chunk com `header="preamble"` (descartado se < 100 chars após merge rule)
4. **Merge rule:** se `len(chunk["text"]) < 100` → concatenar ao chunk anterior (não criar chunk novo). Se for o primeiro chunk, descartar.
5. **Split rule:** se `len(chunk["text"]) > 1500` → encontrar `\n\n` mais próximo do índice `len//2`; dividir em dois chunks, o segundo herda o mesmo `header` com sufixo ` (cont.)`
6. Chunk mínimo resultante após todas as regras: 50 chars (chunks menores são descartados)

**Retorno:** `list[dict]` com `{"header": str, "text": str}`

**Rationale do merge/split:** Com 44 resumos e média de 5-8 seções H2/H3 por resumo, esperamos ~250-300 chunks. Seções H3 curtas (2-3 bullets) têm 60-80 chars — vetores ruidosos que poluem o índice. Seções H2 longas (>1500 chars) misturam sub-temas e reduzem precision. O merge+split mantém densidade semântica por chunk. Isso é auditável em entrevista: você pode plotar a distribuição de tamanhos de chunk antes e depois das regras.

### `index_resumo()` com upsert
```python
def index_resumo(path: Path, collection=None) -> int:
    """Indexa um resumo. Retorna número de chunks indexados."""
    collection = collection or get_collection()
    content = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    chunks = _chunk_by_headers(content)
    for i, chunk in enumerate(chunks):
        doc_id = f"{path.stem}::{i}"
        collection.upsert(
            ids=[doc_id],
            documents=[chunk["text"]],
            metadatas=[{
                "source": str(path),
                "section": chunk["header"],
                "area": fm.get("area", ""),
                "especialidade": fm.get("especialidade", ""),
            }],
        )
    return len(chunks)
```
**upsert** em vez de add: permite reindexar sem apagar o collection inteiro. IDs determinísticos (`{stem}::{i}`) garantem idempotência.

**`_parse_frontmatter()`:** reusar a implementação já existente em `get_topic_context.py` — não duplicar. Importar diretamente: `from app.engine.get_topic_context import _parse_frontmatter`.

### Integração em `get_topic_context()`
```python
# Adicionar após o bloco "# 1. Resumo":
result["relevant_chunks"] = []  # inicializar no dict de result

# Adicionar como bloco "# 5. RAG chunks":
try:
    from app.engine.rag import search as rag_search
    if _CHROMA_AVAILABLE:  # importado de rag
        result["relevant_chunks"] = rag_search(tema, n_results=3)
except Exception:
    pass
```
Import lazy (dentro do try) para evitar ImportError circular se chromadb ausente.

## Applicable Patterns

- **`db-access-layer.md`** — analogia de arquitetura: ChromaDB em `app/engine/rag.py` segue o mesmo princípio de isolamento que SQLite em `app/utils/db.py`. Nenhuma página importa chromadb diretamente.
- **`error-insertion-pipeline.md`** — `tools/index_resumos.py` segue o mesmo padrão de CLI standalone que `tools/insert_questao.py`: argparse, print human-readable, finally-close equivalente.
- **`agent-workflow-protocol.md`** — novo padrão de indexação deve ser documentado no protocolo de sessão (ao criar novo resumo, rodar `python tools/index_resumos.py`)

**Novo padrão introduzido:** `rag-retrieval-layer.md` (documenta chunking, embedding function, collection setup — a criar após implementação).

## Risks

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Ollama offline quando `search()` é chamado | Média | `try/except` no `search()` retorna `[]`; engine continua funcionando via `resumo_content` |
| `nomic-embed-text` não instalado no Ollama | Baixa | `tools/index_resumos.py` falha com mensagem clara: "Run: ollama pull nomic-embed-text" |
| Chunk IDs colidem ao reindexar após renomear arquivo | Baixa | upsert com `{stem}::{i}` — renomear arquivo cria novos IDs e deixa órfãos. Aceitável para v0; `index_all()` pode fazer `delete_where source=<old_path>` antes do upsert na v1 |
| Chunks muito curtos após merge ainda gerando ruído | Baixa | Threshold de 100 chars cobre a maioria dos H3 curtos; ajustar para 150 se recall baixar |
| ChromaDB ausente no Streamlit Cloud | Alta | `_CHROMA_AVAILABLE = False` → `search()` → `[]`; app não quebra |
