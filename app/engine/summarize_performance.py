"""
summarize_performance — métricas de desempenho do ipub.db + padrões de fraqueza da memória.

Limitações documentadas:
- medhub_memory.db é local-only (não commitado). Se ausente, padroes retorna [].
- LangGraph NÃO é ativado em nenhum path desta função.
"""

from __future__ import annotations

from typing import Optional

import app.utils.db as db


def summarize_performance(area: Optional[str] = None) -> dict:
    """Retorna métricas de desempenho e padrões de fraqueza.

    Args:
        area: Filtro opcional por área (ex: "Clínica Médica", "GO"). None agrega todas.

    Returns:
        dict com chaves:
            total_erros (int): total de erros registrados em questoes_erros
                (filtrado por área se area fornecida).
            taxa_acerto (float): percentual de acerto (questoes_acertadas /
                questoes_realizadas) na área. 0.0 se sem dados.
            padroes (list[dict]): padrões de fraqueza de medhub_memory.db.
                Cada item: area (str), especialidade (str), pattern (str),
                error_count (int). Retorna [] se medhub_memory.db ausente.
    """
    result: dict = {
        "total_erros": 0,
        "taxa_acerto": 0.0,
        "padroes": [],
    }

    # 1. Métricas de ipub.db
    try:
        metrics = db.get_db_metrics()
        df = metrics.get("df_areas")
        if df is not None and not df.empty:
            if area:
                filtro = area.lower()
                df_f = df[df["Área"].str.lower().str.contains(filtro, na=False)]
            else:
                df_f = df
            if not df_f.empty:
                total = int(df_f["Total"].sum())
                acertos = int(df_f["Acertos"].sum())
                result["taxa_acerto"] = round(acertos / total * 100, 1) if total > 0 else 0.0
    except Exception:
        pass

    try:
        erros = db.get_erros_resumidos()
        if not erros.empty:
            if area:
                filtro = area.lower()
                erros_f = erros[erros["TemaFull"].str.lower().str.contains(filtro, na=False)]
            else:
                erros_f = erros
            result["total_erros"] = int(len(erros_f))
    except Exception:
        pass

    # 2. Padrões de fraqueza da memória longa (sem LangGraph)
    try:
        from app.memory import get_store
        store = get_store()
        items = store.search(("medhub", "weak_areas"), limit=100)
        filtro_lower = area.lower() if area else None
        for item in items:
            val = item.value
            if val.get("kind") != "WeakArea":
                continue
            content = val.get("content", {})
            if filtro_lower:
                area_val = content.get("area", "").lower()
                esp_val = content.get("especialidade", "").lower()
                if filtro_lower not in area_val and filtro_lower not in esp_val:
                    continue
            result["padroes"].append({
                "area": content.get("area", ""),
                "especialidade": content.get("especialidade", ""),
                "pattern": content.get("pattern", ""),
                "error_count": content.get("error_count", 0),
            })
    except Exception:
        pass

    return result
