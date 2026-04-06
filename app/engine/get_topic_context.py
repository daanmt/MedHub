"""
get_topic_context — consulta o estado completo de um tema clínico.

Limitações documentadas:
- O índice de resumos é construído no primeiro acesso e cacheado em memória do processo.
  Novos resumos adicionados durante uma sessão Python não serão indexados sem reinicializar.
- medhub_memory.db é local-only (não commitado). Se ausente, weak_areas retorna [].
"""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Optional

import app.utils.db as db


# Índice lazy-loaded: {termo_lower → path_str}
_resumo_index: dict[str, str] | None = None


def _parse_frontmatter(path: Path) -> dict:
    """Extrai campos do frontmatter YAML simples de um arquivo .md."""
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return {}
    if not text.startswith('---'):
        return {}
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}
    result: dict = {}
    for line in parts[1].splitlines():
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        key = key.strip()
        val = val.strip()
        if val.startswith('[') and val.endswith(']'):
            items = [v.strip().strip('"\'') for v in val[1:-1].split(',') if v.strip()]
            result[key] = items
        else:
            result[key] = val
    return result


def _build_index() -> dict[str, str]:
    """Constrói índice {termo_lower → path} a partir do frontmatter de resumos/."""
    index: dict[str, str] = {}
    for path in Path("resumos").rglob("*.md"):
        if path.name == "INDEX.md":
            continue
        fm = _parse_frontmatter(path)
        if not fm:
            continue
        if esp := fm.get("especialidade"):
            index[esp.lower()] = str(path)
        if area := fm.get("area"):
            index[area.lower()] = str(path)
        for alias in fm.get("aliases", []):
            if alias:
                index[alias.lower()] = str(path)
    return index


def _get_or_build_index() -> dict[str, str]:
    global _resumo_index
    if _resumo_index is None:
        _resumo_index = _build_index()
    return _resumo_index


def _find_resumo(tema: str) -> Path | None:
    """Localiza o arquivo .md mais relevante para o tema. Exact match primeiro, fuzzy fallback."""
    index = _get_or_build_index()
    termo = tema.lower()
    if hit := index.get(termo):
        return Path(hit)
    matches = difflib.get_close_matches(termo, index.keys(), n=1, cutoff=0.6)
    return Path(index[matches[0]]) if matches else None


def get_topic_context(tema: str, area: Optional[str] = None) -> dict:
    """Retorna contexto completo de um tema para uso por agentes.

    Args:
        tema: Nome do tema, especialidade ou alias (ex: "Cardiologia", "IC", "Trauma").
        area: Filtro opcional por área para refinar weak_areas (ex: "Clínica Médica").

    Returns:
        dict com chaves:
            resumo_path (str | None): caminho relativo ao arquivo .md do resumo.
            resumo_content (str | None): conteúdo completo do arquivo .md.
            erros_recentes (list[dict]): últimos 20 erros de questoes_erros filtrados
                pelo tema. Cada item: id, titulo, tipo_erro, habilidades_sequenciais,
                armadilha_prova, explicacao_correta, area, tema.
            cards_ativos (int): número de flashcards com state > 0 vinculados ao tema.
            weak_areas (list[dict]): padrões de fraqueza de medhub_memory.db filtrados
                pelo tema/area. Cada item: area, especialidade, pattern, error_count.
                Retorna [] se medhub_memory.db estiver ausente ou vazio.
    """
    result: dict = {
        "resumo_path": None,
        "resumo_content": None,
        "erros_recentes": [],
        "cards_ativos": 0,
        "weak_areas": [],
        "relevant_chunks": [],
    }

    # 1. Resumo
    try:
        resumo_path = _find_resumo(tema)
        if resumo_path and resumo_path.exists():
            result["resumo_path"] = str(resumo_path)
            result["resumo_content"] = resumo_path.read_text(encoding='utf-8')
    except Exception:
        pass

    # 2. Erros recentes
    try:
        result["erros_recentes"] = db.get_erros_por_tema(tema)
    except Exception:
        pass

    # 3. Cards ativos (state > 0) vinculados ao tema
    try:
        queue = db.get_cards_by_bucket()
        termo_lower = tema.lower()
        result["cards_ativos"] = sum(
            1 for c in queue["atrasados"] + queue["hoje"]
            if termo_lower in (str(c.get("tema", "")) + " " + str(c.get("area", ""))).lower()
        )
    except Exception:
        pass

    # 4. Weak areas da memória longa (sem LangGraph)
    try:
        from app.memory import get_store
        store = get_store()
        items = store.search(("medhub", "weak_areas"), limit=100)
        filtro = (area or tema).lower()
        for item in items:
            val = item.value
            if val.get("kind") != "WeakArea":
                continue
            content = val.get("content", {})
            area_val = content.get("area", "").lower()
            esp_val = content.get("especialidade", "").lower()
            if filtro in area_val or filtro in esp_val or area_val in filtro or esp_val in filtro:
                result["weak_areas"].append({
                    "area": content.get("area", ""),
                    "especialidade": content.get("especialidade", ""),
                    "pattern": content.get("pattern", ""),
                    "error_count": content.get("error_count", 0),
                })
    except Exception:
        pass

    # 5. RAG chunks — busca semântica sobre resumos indexados
    try:
        from app.engine.rag import search as rag_search
        result["relevant_chunks"] = rag_search(tema, n_results=3)
    except Exception:
        pass

    return result
