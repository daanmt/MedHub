"""
get_review_queue — retorna a fila de revisão FSRS dividida em buckets temporais.
"""

from __future__ import annotations

import app.utils.db as db


def get_review_queue() -> dict:
    """Retorna a fila de revisão FSRS do dia, dividida em três buckets.

    Returns:
        dict com chaves:
            atrasados (list[dict]): cards com due anterior a hoje (state > 0).
            hoje (list[dict]): cards que vencem hoje (state > 0).
            novos (list[dict]): cards nunca revisados (state == 0), máximo 10.
        Cada item de cada lista contém:
            card_id (int), frente_pergunta (str), verso_resposta (str),
            due (datetime | str), area (str), tema (str).
        Retorna buckets vazios (listas []) em caso de falha.
    """
    empty: dict = {"atrasados": [], "hoje": [], "novos": []}
    try:
        return db.get_cards_by_bucket()
    except Exception:
        return empty
