"""
analyze_error — ponto de entrada para agentes externos após inserção de erro.

NÃO gera flashcards. Retorna contexto estruturado + sinalizadores de pré-condições
para geração contextual. O agente chama tools/insert_questao.py diretamente;
esta função é chamada a seguir para obter o contexto completo sobre o tema.

Uso:
    from app.engine import analyze_error

    resultado = analyze_error("Sepse Neonatal", area="Pediatria")
    if resultado["can_generate_cards"]:
        cards = generate_contextual_cards(
            tema="Sepse Neonatal",
            elo_quebrado="...",
            resumo_content=resultado["context"]["resumo_content"],
        )
"""
from __future__ import annotations

from typing import Optional

from app.engine.get_topic_context import get_topic_context


def analyze_error(tema: str, area: Optional[str] = None) -> dict:
    """Retorna contexto e sinalizadores após análise de erro.

    Para agentes externos: fornece o "what happened" após a inserção via insert_questao.py.
    NÃO gera cards — use generate_contextual_cards() separadamente se necessário.
    Nunca lança exceção se o tema não for encontrado.

    Args:
        tema: Nome do tema clínico do erro analisado.
        area: Filtro opcional por área (ex: "Clínica Médica", "GO").

    Returns:
        dict com chaves:
            context (dict): saída completa de get_topic_context() com chaves
                resumo_path, resumo_content, erros_recentes, cards_ativos, weak_areas.
            resumo_available (bool): True se resumo clínico foi encontrado para o tema.
            can_generate_cards (bool): True se há resumo disponível para geração contextual.
    """
    try:
        ctx = get_topic_context(tema, area)
    except Exception:
        ctx = {
            "resumo_path": None,
            "resumo_content": None,
            "erros_recentes": [],
            "cards_ativos": 0,
            "weak_areas": [],
        }

    resumo_available = ctx.get("resumo_path") is not None
    return {
        "context": ctx,
        "resumo_available": resumo_available,
        "can_generate_cards": resumo_available,
    }
