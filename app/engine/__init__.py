"""
MedHub Study Engine — biblioteca de domínio para leitura de estado do sistema.

Expõe três funções de consulta estáveis, tipadas e sem efeitos colaterais,
consumíveis por agentes externos (Claude Code, Cursor, Antigravity) sem
necessidade de conhecer o schema interno do ipub.db ou medhub_memory.db.

Uso:
    from app.engine import get_topic_context, get_review_queue, summarize_performance

    ctx = get_topic_context("Cardiologia")
    queue = get_review_queue()
    perf = summarize_performance(area="Clínica Médica")
"""

from app.engine.get_topic_context import get_topic_context
from app.engine.get_review_queue import get_review_queue
from app.engine.summarize_performance import summarize_performance
from app.engine.generate_flashcards import generate_contextual_cards
from app.engine.analyze_error import analyze_error

__all__ = [
    "get_topic_context",
    "get_review_queue",
    "summarize_performance",
    "generate_contextual_cards",
    "analyze_error",
]
