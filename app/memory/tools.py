"""
LangMem tool wrappers for MedHub memory namespaces.

Returns a list of tools compatible with LangGraph agents.
Hot-path tools (used during conversation) vs background tools
(used by manager.py at session close) are documented per namespace.
"""

from __future__ import annotations

from langmem import create_manage_memory_tool, create_search_memory_tool

from app.memory.schemas import WeakArea, WorkflowRule, SessionInsight
from app.memory.store import SQLiteMemoryStore


def get_memory_tools(store: SQLiteMemoryStore) -> list:
    """Return all LangMem tools bound to the given store.

    Hot-path namespaces (used during conversation):
      - profile: exam target, study pace, format preferences
      - workflow_rules: procedural discoveries
      - study_preferences: response style, verbosity

    Background namespaces (written at session close by manager.py):
      - weak_areas: aggregated weakness patterns
      - session_insights: episodic memorable insights
    """
    return [
        # Hot-path
        create_manage_memory_tool(
            namespace=("medhub", "profile"),
            store=store,
            name="manage_profile",
            description="Store or update the user's exam target, study pace, and format preferences.",
        ),
        create_manage_memory_tool(
            namespace=("medhub", "workflow_rules"),
            store=store,
            schema=WorkflowRule,
            name="manage_workflow_rules",
            description="Record procedural rules discovered during this session about the MedHub workflow.",
        ),
        create_manage_memory_tool(
            namespace=("medhub", "study_preferences"),
            store=store,
            name="manage_study_preferences",
            description="Store preferences about response format, verbosity, or study style.",
        ),
        # Background (also accessible hot-path if needed)
        create_manage_memory_tool(
            namespace=("medhub", "weak_areas"),
            store=store,
            schema=WeakArea,
            name="manage_weak_areas",
            description="Record or update a weakness pattern for a medical area/especialidade.",
        ),
        create_manage_memory_tool(
            namespace=("medhub", "session_insights"),
            store=store,
            schema=SessionInsight,
            name="manage_session_insights",
            description="Store a memorable insight from the current session.",
        ),
        # Cross-namespace search
        create_search_memory_tool(
            namespace=("medhub",),
            store=store,
            name="search_memory",
            description="Search across all MedHub memory namespaces (profile, weak_areas, workflow_rules, insights).",
        ),
    ]
