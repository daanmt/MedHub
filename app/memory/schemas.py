"""
Pydantic schema for MedHub long-term memory.

Namespace único: ("medhub", "weak_areas") — o único com writer real e o
único lido no boot (`inspect.load_context`). Os schemas de namespaces
fantasma (UserProfile/profile, WorkflowRule/workflow_rules) e o write-only
SessionInsight/session_insights foram removidos em consolidacao-part-3:
zero linhas desde março (fantasmas) ou zero leitores (write-only).
"""

from pydantic import BaseModel


class WeakArea(BaseModel):
    """Persistent weakness pattern for a given area/especialidade.
    Namespace: ("medhub", "weak_areas")
    One entry per (area, especialidade) pair.

    Contrato de contagem (manager._sync_error_counts): o par
    (area, especialidade) casa por match EXATO com o par
    (taxonomia_cronograma.area, taxonomia_cronograma.tema) do ipub.db —
    `area` é a área da taxonomia e `especialidade` é o tema/sub-tema.
    Sem par correspondente, error_count = 0 (nunca o total da área).
    """
    area: str               # área da taxonomia ipub, e.g. "Cirurgia"
    especialidade: str      # tema/sub-tema da taxonomia ipub, e.g. "Trauma - Choque"
    pattern: str            # human-readable description of the recurring mistake
    error_count: int = 0    # errors in this (area, tema) pair (from ipub.db)
    last_updated: str = ""  # ISO date string of last update
