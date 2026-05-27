"""
MedHub Study Engine — biblioteca de domínio para leitura de estado do sistema.

Expõe duas funções de consulta estáveis, tipadas e sem efeitos colaterais.

Uso:
    from app.engine import get_topic_context, summarize_performance

    ctx = get_topic_context("Cardiologia")
    perf = summarize_performance(area="Clínica Médica")
"""

from app.engine.get_topic_context import get_topic_context
from app.engine.summarize_performance import summarize_performance

__all__ = [
    "get_topic_context",
    "summarize_performance",
]
