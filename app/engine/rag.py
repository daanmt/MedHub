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
from concurrent.futures import ThreadPoolExecutor
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

_HYDE_CACHE: dict[str, str] = {}  # cache de sessão: query → hypothetical_doc; TTL = processo


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
    """Usa Anthropic (Haiku 4.5) ou Ollama para gerar uma resposta hipotética à query (HyDE).

    Resultado é cacheado em _HYDE_CACHE por TTL de sessão — queries repetidas não
    re-chamam a API.
    """
    if query in _HYDE_CACHE:
        return _HYDE_CACHE[query]

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
            doc = response.content[0].text.strip()
            _HYDE_CACHE[query] = doc
            return doc
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
            doc = res.get("response", query).strip()
            _HYDE_CACHE[query] = doc
            return doc
    except Exception:
        pass

    # Fallback final: cacheamos a própria query para evitar re-tentativas em sessão
    _HYDE_CACHE[query] = query
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


def _textual_fallback(query: str, n_results: int = 5, area: Optional[str] = None) -> list[dict]:
    """Fallback léxico quando o RAG semântico está indisponível (Chroma/Ollama offline).

    Reusa o índice de `get_topic_context` (`_find_resumo`) para localizar o resumo mais
    próximo do query e o chunker canônico `_chunk_by_headers` para fatiá-lo em seções
    H2/H3. Retorna no mesmo shape de search(), com `metadata['source'] == 'fallback_textual'`
    (marca de proveniência análoga ao `pdf_raw` do two-tier) e `distance = None` — o
    consumidor distingue o resultado degradado do semântico curado. `[]` se nada casar.

    O import de get_topic_context é lazy: evita ciclo de import (get_topic_context importa rag).
    """
    try:
        from app.engine.get_topic_context import _find_resumo, _parse_frontmatter
        path = _find_resumo(query)
        if not path or not path.exists():
            return []
        fm = _parse_frontmatter(path)
        if area and fm.get("area") and fm["area"].lower() != area.lower():
            return []
        chunks = _chunk_by_headers(path.read_text(encoding="utf-8"))
        out = []
        for c in chunks[:n_results]:
            out.append({
                "text": c["text"],
                "metadata": {
                    "source": "fallback_textual",
                    "resumo_path": str(path),
                    "section": c["header"],
                    "area": fm.get("area", ""),
                    "especialidade": fm.get("especialidade", ""),
                },
                "distance": None,
            })
        return out
    except Exception:
        return []


def search(query: str, n_results: int = 5, area: Optional[str] = None, use_hyde: bool = True, max_distance: float = 0.35) -> list[dict]:
    """Busca semântica sobre os resumos indexados usando Multi-Query (HyDE + Raw).

    Quando ChromaDB/Ollama estão indisponíveis, degrada para `_textual_fallback`
    (busca léxica marcada `source=fallback_textual`) em vez de retornar []. O caminho
    semântico (infra viva) é inalterado — o fallback só ativa em falha de infra.

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
        return _textual_fallback(query, n_results, area)
    try:
        query_texts = [query]
        if use_hyde:
            # HyDE e get_collection() rodam em paralelo: latência = max(ambos), não soma
            with ThreadPoolExecutor(max_workers=2) as ex:
                f_hyde = ex.submit(_generate_hypothetical_document, query)
                f_coll = ex.submit(get_collection)
                collection = f_coll.result()
                query_texts.append(f_hyde.result())
        else:
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
        return _textual_fallback(query, n_results, area)


# ---------------------------------------------------------------------------
# Tier bruto (pdf_raw) -- F17. ADITIVO: o gold (collection `resumos`, search,
# index_all, get_collection) NAO muda. Epistemologia two-tier do ai-eng
# (ADR-002): o PDF nunca vira canon por existir; o `.md` cunhado sombrea o PDF
# do mesmo tema. `data/chroma/` continua local-only; nenhum PDF e deletado.
# ---------------------------------------------------------------------------

PDF_COLLECTION_NAME = "pdf_raw"


def get_pdf_collection():
    """Collection do tier bruto (`pdf_raw`), isolada do gold (`resumos`).

    Isolamento fisico: `--clear` do bruto nao arrisca o gold, e o gold-primeiro
    e uma consulta ordenada de duas collections, nao um filtro dentro de uma.
    """
    ef = OllamaEmbeddingFunction(url=OLLAMA_URL, model_name=EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=PDF_COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def _norm_tema(nome: str) -> str:
    """Normaliza um stem/tema para a chave de sombreamento (local ao modulo).

    Remove prefixo numerico EMED, acentos, case e pontuacao. Espelha a
    normalizacao da Parte 1 mas mantida local para a Parte 2 nao depender dela.
    """
    import unicodedata
    s = re.sub(r"^\s*\d+\s*[-.)_]*\s*", "", nome or "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _chunk_plain(text: str, max_chars: int = _MAX_CHUNK_CHARS) -> list[str]:
    """Chunk de texto plano (PDF extraido) por acumulo de paragrafos.

    O texto de PDF nao tem estrutura de header confiavel (o gold usa H2/H3),
    entao agrupamos paragrafos (separados por linha em branco) em janelas
    <= max_chars; paragrafos gigantes sao fatiados no limite. Chunks < 50 chars
    sao descartados.
    """
    brutos = re.split(r"\n\s*\n", text or "")
    paras: list[str] = []
    for p in brutos:
        p = p.strip()
        while len(p) > max_chars:
            paras.append(p[:max_chars])
            p = p[max_chars:]
        if p:
            paras.append(p)

    chunks: list[str] = []
    buf = ""
    for p in paras:
        if buf and len(buf) + len(p) + 2 > max_chars:
            chunks.append(buf)
            buf = p
        else:
            buf = (buf + "\n\n" + p) if buf else p
    if buf:
        chunks.append(buf)
    return [c for c in chunks if len(c) >= 50]


def _extract_via_temp(pdf_path: str) -> Optional[str]:
    """Extrai texto de um PDF reusando tools/extract_pdfs.extract_pdf.

    Cria arquivo temp, le o conteudo e remove o temp (NAO o PDF). Retorna None
    em qualquer falha (PDF sem texto extraivel e pulado, nao quebra a indexacao).
    """
    import os
    import sys as _sys
    try:
        root = str(Path(__file__).resolve().parent.parent.parent)
        if root not in _sys.path:
            _sys.path.insert(0, root)
        from tools.extract_pdfs import extract_pdf
    except Exception:
        return None
    tmp = None
    try:
        tmp = extract_pdf(pdf_path)
        if not tmp:
            return None
        with open(tmp, encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return None
    finally:
        if tmp:
            try:
                os.remove(tmp)
            except Exception:
                pass


def index_pdf(path: Path, collection=None, extractor=None) -> int:
    """Extrai, chunka e indexa UM PDF no tier bruto. Incremental por mtime.

    Args:
        path: caminho do .pdf.
        collection: collection pdf_raw (reutilizar se ja instanciada).
        extractor: callable(str)->str|None (injetavel em teste). Default:
            extracao real via arquivo temp.

    Returns:
        Numero de chunks indexados. 0 se pulado (mtime inalterado) ou sem texto.
    """
    if collection is None:
        collection = get_pdf_collection()

    mtime = str(int(path.stat().st_mtime))
    origem = str(path)

    # Incremental: ja indexado com o mesmo mtime -> pula (custo zero).
    try:
        existing = collection.get(where={"origem": origem}, limit=1, include=["metadatas"])
        metas_ex = existing.get("metadatas") or []
        if metas_ex and metas_ex[0].get("mtime") == mtime:
            return 0
    except Exception:
        pass

    texto = extractor(origem) if extractor else _extract_via_temp(origem)
    if not texto or not texto.strip():
        return 0
    chunks = _chunk_plain(texto)
    if not chunks:
        return 0

    # mtime mudou -> limpa chunks antigos deste PDF antes de reinserir.
    try:
        collection.delete(where={"origem": origem})
    except Exception:
        pass

    import hashlib
    h = hashlib.md5(origem.encode("utf-8")).hexdigest()[:8]
    tema = path.stem
    ids = [f"{h}::{i}" for i in range(len(chunks))]
    metas = [{"source": "pdf_raw", "origem": origem, "tema": tema, "mtime": mtime}
             for _ in chunks]
    collection.upsert(ids=ids, documents=chunks, metadatas=metas)
    return len(chunks)


def index_pdfs_raw(resumos_dir: str = "resumos", clear: bool = False) -> dict[str, int]:
    """Indexa o tier bruto de todos os PDFs em resumos_dir (incremental).

    Args:
        resumos_dir: raiz dos PDFs-fonte.
        clear: se True, deleta SOMENTE a collection pdf_raw antes (gold intocado).

    Returns:
        dict {pdf_path: chunk_count}.
    """
    if clear:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            client.delete_collection(name=PDF_COLLECTION_NAME)
        except Exception:
            pass

    collection = get_pdf_collection()
    results: dict[str, int] = {}
    for path in sorted(p for p in Path(resumos_dir).rglob("*") if p.suffix.lower() == ".pdf"):
        results[str(path)] = index_pdf(path, collection)
    return results


def _tema_norm_de_hit(hit: dict) -> str:
    """Chave de tema normalizada de um hit (gold ou pdf_raw), para sombreamento."""
    meta = hit.get("metadata", {}) or {}
    if meta.get("source") == "pdf_raw":
        return _norm_tema(meta.get("tema", ""))
    return _norm_tema(Path(meta.get("source", "")).stem)


def _aplica_sombreamento(raw_hits, temas_gold, max_distance, faltam):
    """Filtra hits do tier bruto: descarta > max_distance, temas ja no gold e
    duplicatas de texto. Retorna ate `faltam` hits ordenados por distancia.

    Funcao pura (sem Chroma/Ollama) -- alvo direto do teste de sombreamento.
    """
    out = []
    seen = set()
    for hit in raw_hits:
        if hit["distance"] > max_distance:
            continue
        if _tema_norm_de_hit(hit) in temas_gold:
            continue
        if hit["text"] in seen:
            continue
        seen.add(hit["text"])
        out.append(hit)
    out.sort(key=lambda x: x["distance"])
    return out[:faltam]


def search_two_tier(query: str, n_results: int = 5, area: Optional[str] = None,
                    use_hyde: bool = True, max_distance: float = 0.35) -> list[dict]:
    """Busca gold-primeiro com fallback MARCADO no tier bruto (pdf_raw).

    O gold (`search`) responde primeiro; o tier bruto so complementa ate
    n_results quando o gold nao preenche. Hits do bruto trazem
    `metadata['source'] == 'pdf_raw'` (o agente os trata como nao-curados).
    Sombreamento: temas ja cobertos pelo gold NAO trazem pdf_raw do mesmo tema.
    Se ChromaDB/Ollama offline, retorna o fallback lexico do gold
    (`search` -> `_textual_fallback`, marcado `source=fallback_textual`).
    """
    gold = search(query, n_results=n_results, area=area, use_hyde=use_hyde,
                  max_distance=max_distance)
    if len(gold) >= n_results or not _CHROMA_AVAILABLE:
        return gold

    temas_gold = {_tema_norm_de_hit(h) for h in gold}
    faltam = n_results - len(gold)
    try:
        coll = get_pdf_collection()
        res = coll.query(query_texts=[query], n_results=max(faltam * 3, 5))
        raw_hits = []
        for docs, metas, dists in zip(res["documents"], res["metadatas"], res["distances"]):
            for doc, meta, dist in zip(docs, metas, dists):
                raw_hits.append({"text": doc, "metadata": meta, "distance": dist})
        bruto = _aplica_sombreamento(raw_hits, temas_gold, max_distance, faltam)
        return gold + bruto
    except Exception:
        return gold
