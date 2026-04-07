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


def _generate_hypothetical_document(query: str) -> str:
    """Usa Anthropic (Haiku 4.5) ou Ollama para gerar uma resposta hipotética à query (HyDE)."""
    import os
    import json
    import urllib.request
    from dotenv import load_dotenv
    load_dotenv()
    
    prompt = f"Escreva um fato clínico objetivo (máximo 3 linhas) abordando o seguinte tema/assunto: {query}"
    
    # Tentativa 1: Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                system="Você é um assistente médico. Responda com um fato clínico objetivo que seria encontrado em um livro-texto, sem saudações.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception:
            pass

    # Tentativa 2: Ollama (Fallback)
    try:
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "llama3", 
            "prompt": prompt,
            "stream": False,
            "system": "Você é um assistente médico. Responda com um fato clínico objetivo que seria encontrado em um livro-texto, sem saudações."
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode())
            return res.get("response", query).strip()
    except Exception:
        pass
    
    # Fallback final
    return query


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

    ids = []
    docs = []
    metas = []
    
    # Extrair título e alias para contexto semântico global
    tema = path.stem
    aliases = fm.get("aliases", [])
    alias_str = f" ({', '.join(aliases)})" if aliases else ""
    contexto_global = f"[{tema}{alias_str} > "
    
    for i, chunk in enumerate(chunks):
        ids.append(f"{path.stem}::{i}")
        
        # Propagação massiva de contexto: Injeta o título do documento no topo do texto
        # para que o modelo nomic capture a essência semântica mesmo em parágrafos isolados.
        texto_enriquecido = f"{contexto_global}{chunk['header']}]\n{chunk['text']}"
        docs.append(texto_enriquecido)
        
        metas.append({
            "source": str(path),
            "section": chunk["header"],
            "area": fm.get("area", ""),
            "especialidade": fm.get("especialidade", ""),
        })

    if docs:
        collection.upsert(
            ids=ids,
            documents=docs,
            metadatas=metas,
        )

    return len(chunks)


def index_all(resumos_dir: str = "resumos", clear: bool = False) -> dict[str, int]:
    """Indexa todos os resumos em resumos/**/*.md.

    Args:
        resumos_dir: Diretório com arquivos .md
        clear: Se True, exclui toda a collection antes de indexar

    Returns:
        dict {filename: chunk_count}
    """
    if clear:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
            
    collection = get_collection()
    results: dict[str, int] = {}
    for path in sorted(Path(resumos_dir).rglob("*.md")):
        if path.name == "INDEX.md":
            continue
        count = index_resumo(path, collection)
        results[path.name] = count
    return results


def search(query: str, n_results: int = 5, area: Optional[str] = None, use_hyde: bool = True, max_distance: float = 0.35) -> list[dict]:
    """Busca semântica sobre os resumos indexados usando Multi-Query (HyDE + Raw).

    Retorna [] quando ChromaDB indisponível ou Ollama offline.

    Args:
        query: Texto da consulta (ex: elo_quebrado, pergunta clínica).
        n_results: Número máximo de chunks a retornar (default: 5).
        area: Filtro opcional por área (ex: "Clínica Médica").
        use_hyde: Se True, gera documento hipotético e usa busca combinada.
        max_distance: Cossenóide máximo admissível. Distâncias maiores são expurgadas (default: 0.35).

    Returns:
        list[dict] com chaves: text, metadata (source, section, area, especialidade), distance.
    """
    if not _CHROMA_AVAILABLE:
        return []
    try:
        query_texts = [query]
        if use_hyde:
            query_texts.append(_generate_hypothetical_document(query))

        collection = get_collection()
        where = {"area": area} if area else None
        
        # Puxa margem extra para ter folga contra deduplicados ou hits ruins
        fetch_k = max(n_results * 2, 5)
        results = collection.query(
            query_texts=query_texts,
            n_results=fetch_k,
            where=where,
        )

        combined = []
        seen_texts = set()

        for docs_series, metas_series, dists_series in zip(results["documents"], results["metadatas"], results["distances"]):
            for doc, meta, dist in zip(docs_series, metas_series, dists_series):
                if dist > max_distance:
                    continue
                if doc not in seen_texts:
                    seen_texts.add(doc)
                    combined.append({
                        "text": doc,
                        "metadata": meta,
                        "distance": dist,
                    })

        combined.sort(key=lambda x: x["distance"])
        return combined[:n_results]
    except Exception:
        return []
