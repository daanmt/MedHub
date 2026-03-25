"""
MedHub Memory v1 — LangGraph + LangMem persistence layer.

Three-layer model:
  Camada 1: Canonical repo (AGENTE.md, ESTADO.md, ipub.db, Temas/)
  Camada 2: Short-term / thread-scoped (SqliteSaver → medhub_memory.db::checkpoints)
  Camada 3: Long-term / cross-thread (LangMem + SQLiteMemoryStore → medhub_memory.db::memory_store)

Quick start:
    from app.memory import get_store, get_checkpointer, get_memory_tools

    store = get_store()
    tools = get_memory_tools(store)

    with get_checkpointer() as cp:
        config = get_thread_config(46)
        # pass cp and config to your LangGraph graph
"""

from __future__ import annotations

from app.memory.store import SQLiteMemoryStore
from app.memory.checkpointer import get_checkpointer, get_thread_config, get_session_history
from app.memory.tools import get_memory_tools


_DEFAULT_DB = "medhub_memory.db"
_store_singleton: SQLiteMemoryStore | None = None


def get_store(db_path: str = _DEFAULT_DB) -> SQLiteMemoryStore:
    """Return the (cached) SQLiteMemoryStore instance."""
    global _store_singleton
    if _store_singleton is None or _store_singleton.db_path != db_path:
        _store_singleton = SQLiteMemoryStore(db_path)
    return _store_singleton


__all__ = [
    "get_store",
    "get_checkpointer",
    "get_thread_config",
    "get_session_history",
    "get_memory_tools",
    "SQLiteMemoryStore",
]
