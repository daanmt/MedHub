"""
rag — camada de busca semântica sobre resumos/**/*.md via ChromaDB + nomic-embed-text.

Uso:
    from app.engine.rag import search, index_all, _CHROMA_AVAILABLE

    if _CHROMA_AVAILABLE:
        results = search("quando intubar RN prematuro", n_results=3)

Limitações documentadas:
    - Requer Ollama rodando localmente com nomic-embed-text disponível.
    - ChromaDB ausente do ambiente: _CHROMA_AVAILABLE = False, search() retorna [].
    - Ollama offline: search() captura a exceção e retorna [].
    - IDs determinísticos {stem}::{i}: renomear arquivo deixa chunks órfãos no índice.
      Solução: rodar tools/index_resumos.py novamente após renomear.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

try:
    import chromadb
    from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False

# Reusar parser de frontmatter existente — não duplicar
from app.engine.get_topic_context import _parse_frontmatter  # noqa: E402

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "resumos"

_MIN_CHUNK_CHARS = 100
_MAX_CHUNK_CHARS = 1500


def get_collection():
    """Retorna a collection ChromaDB com OllamaEmbeddingFunction configurada."""
    ef = OllamaEmbeddingFunction(url=OLLAMA_URL, model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def _strip_frontmatter(content: str) -> str:
    """Remove o bloco frontmatter YAML (entre --- iniciais) do conteúdo."""
    if not content.startswith("---"):
        return content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    return parts[2].lstrip("\n")


def _chunk_by_headers(content: str) -> list[dict]:
    """Split do conteúdo markdown em chunks por seções H2/H3.

    Regras aplicadas em ordem:
    1. Split em linhas começando com '## ' ou '### '
    2. Merge de chunk < _MIN_CHUNK_CHARS no chunk anterior
    3. Split de chunk > _MAX_CHUNK_CHARS no \\n\\n mais próximo do ponto médio

    Retorna list[dict] com chaves 'header' (str) e 'text' (str).
    Chunks < 50 chars após todas as regras são descartados.
    """
    body = _strip_frontmatter(content)
    lines = body.splitlines(keepends=True)

    # Passo 1: split por H2/H3
    raw_chunks: list[dict] = []
    current_header = "preamble"
    current_lines: list[str] = []

    for line in lines:
        if re.match(r"^#{2,3} ", line):
            if current_lines:
                raw_chunks.append({
                    "header": current_header,
                    "text": "".join(current_lines).strip(),
                })
            current_header = line.strip().lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        raw_chunks.append({
            "header": current_header,
            "text": "".join(current_lines).strip(),
        })

    # Passo 2: merge de chunks < _MIN_CHUNK_CHARS no anterior
    merged: list[dict] = []
    for chunk in raw_chunks:
        if len(chunk["text"]) < _MIN_CHUNK_CHARS:
            if merged:
                merged[-1]["text"] = merged[-1]["text"] + "\n\n" + chunk["text"]
            # primeiro chunk curto (preamble curto): descartar
        else:
            merged.append({"header": chunk["header"], "text": chunk["text"]})

    # Passo 3: split de chunks > _MAX_CHUNK_CHARS no parágrafo mais próximo do meio
    final: list[dict] = []
    for chunk in merged:
        if len(chunk["text"]) <= _MAX_CHUNK_CHARS:
            final.append(chunk)
        else:
            text = chunk["text"]
            mid = len(text) // 2
            left = text.rfind("\n\n", 0, mid)
            right = text.find("\n\n", mid)

            if left == -1 and right == -1:
                split_pos = mid
            elif left == -1:
                split_pos = right
            elif right == -1:
                split_pos = left
            else:
                split_pos = left if (mid - left) <= (right - mid) else right

            part1 = text[:split_pos].strip()
            part2 = text[split_pos:].strip()

            if len(part1) >= 50:
                final.append({"header": chunk["header"], "text": part1})
            if len(part2) >= 50:
                final.append({"header": chunk["header"] + " (cont.)", "text": part2})

    return [c for c in final if len(c["text"]) >= 50]


def index_resumo(path: Path, collection=None) -> int:
    """Chunka e indexa um resumo no ChromaDB via upsert.

    Args:
        path: Caminho para o arquivo .md do resumo.
        collection: Collection ChromaDB (reutilizar se já instanciada).

    Returns:
        Número de chunks indexados.
    """
    if collection is None:
        collection = get_collection()

    content = path.read_text(encoding="utf-8")
    fm = _parse_frontmatter(path)
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


def index_all(resumos_dir: str = "resumos") -> dict[str, int]:
    """Indexa todos os resumos em resumos/**/*.md.

    Returns:
        dict {filename: chunk_count}
    """
    collection = get_collection()
    results: dict[str, int] = {}
    for path in sorted(Path(resumos_dir).rglob("*.md")):
        if path.name == "INDEX.md":
            continue
        count = index_resumo(path, collection)
        results[path.name] = count
    return results


def search(query: str, n_results: int = 3, area: Optional[str] = None) -> list[dict]:
    """Busca semântica sobre os resumos indexados.

    Retorna [] quando ChromaDB indisponível ou Ollama offline.

    Args:
        query: Texto da consulta (ex: elo_quebrado, pergunta clínica).
        n_results: Número máximo de chunks a retornar.
        area: Filtro opcional por área (ex: "Clínica Médica").

    Returns:
        list[dict] com chaves: text, metadata (source, section, area, especialidade), distance.
    """
    if not _CHROMA_AVAILABLE:
        return []
    try:
        collection = get_collection()
        where = {"area": area} if area else None
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )
        return [
            {
                "text": doc,
                "metadata": meta,
                "distance": dist,
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
    except Exception:
        return []
