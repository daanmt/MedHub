"""
Pydantic schemas for MedHub long-term memory namespaces.

Each class maps to one LangMem namespace under ("medhub", <namespace>).
"""

from pydantic import BaseModel


class UserProfile(BaseModel):
    """Persistent preferences and goals of the user.
    Namespace: ("medhub", "profile")
    """
    exam_target: str = ""       # "USP", "ENARE", "FMUSP", etc.
    study_pace: str = ""        # "intensivo", "regular", "revisao"
    preferred_format: str = ""  # "conciso", "detalhado", "tabular"
    notes: str = ""             # freeform observations


class WeakArea(BaseModel):
    """Persistent weakness pattern for a given area/especialidade.
    Namespace: ("medhub", "weak_areas")
    One entry per (area, especialidade) pair.
    """
    area: str               # e.g. "Clínica Médica"
    especialidade: str      # e.g. "Cardiologia"
    pattern: str            # human-readable description of the recurring mistake
    error_count: int = 0    # cumulative errors in this area (from ipub.db)
    last_updated: str = ""  # ISO date string of last update


class WorkflowRule(BaseModel):
    """Procedural rule learned during a session about the MedHub workflow.
    Namespace: ("medhub", "workflow_rules")
    These complement (never duplicate) AGENTE.md.
    """
    rule: str          # concise imperative statement
    context: str       # when/where the rule applies
    learned_in: str    # session identifier, e.g. "session_046"


class SessionInsight(BaseModel):
    """Memorable insight from a specific session.
    Namespace: ("medhub", "session_insights")
    Not the full log (that lives in history/session_NNN.md).
    """
    session_id: str    # "session_046"
    insight: str       # the key learning worth remembering across sessions
    area: str          # medical area or "arquitetura" / "workflow"
