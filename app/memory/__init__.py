"""
MedHub Memory — LangMem persistence layer.

Two-layer model:
  Camada 1: Canonical repo (AGENTE.md, ESTADO.md, ipub.db, resumos/)
  Camada 3: Long-term / cross-thread (LangMem + SQLiteMemoryStore → medhub_memory.db::memory_store)

Quick start:
    from app.memory import get_store

    store = get_store()
    items = store.search(("medhub", "weak_areas"))
"""

from __future__ import annotations

from app.memory.store import SQLiteMemoryStore


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
    "SQLiteMemoryStore",
]
