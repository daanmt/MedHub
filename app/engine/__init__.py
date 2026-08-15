"""
MedHub Study Engine — biblioteca de domínio para leitura de estado do sistema.

Expõe uma função de consulta estável, tipada e sem efeitos colaterais.

Uso:
    from app.engine import get_topic_context

    ctx = get_topic_context("Cardiologia")
"""

from app.engine.get_topic_context import get_topic_context

__all__ = [
    "get_topic_context",
]
