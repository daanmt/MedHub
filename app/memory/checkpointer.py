"""
LangGraph SqliteSaver helpers for MedHub.

Thread model: thread_id = "session_{NNN:03d}"
Maps 1:1 with history/session_NNN.md audit trail.
Cross-session continuity lives in the long-term store (app/memory/store.py).
"""

from __future__ import annotations

from typing import Iterator

from langgraph.checkpoint.sqlite import SqliteSaver


_DEFAULT_DB = "medhub_memory.db"


def get_checkpointer(db_path: str = _DEFAULT_DB) -> SqliteSaver:
    """Return a SqliteSaver connected to medhub_memory.db.

    Usage (as context manager):
        with get_checkpointer() as cp:
            graph.invoke(state, config=get_thread_config(46), checkpointer=cp)
    """
    return SqliteSaver.from_conn_string(db_path)


def get_thread_config(session_num: int) -> dict:
    """Return LangGraph config dict for a given session number.

    Example:
        get_thread_config(46) → {"configurable": {"thread_id": "session_046"}}
    """
    return {"configurable": {"thread_id": f"session_{session_num:03d}"}}


def get_session_history(checkpointer: SqliteSaver, thread_id: str) -> list[dict]:
    """List all checkpoints for a given thread_id.

    Returns a list of checkpoint metadata dicts, newest first.
    """
    history = []
    try:
        for checkpoint_tuple in checkpointer.list({"configurable": {"thread_id": thread_id}}):
            history.append(
                {
                    "thread_id": thread_id,
                    "checkpoint_id": checkpoint_tuple.config.get("configurable", {}).get(
                        "checkpoint_id", "unknown"
                    ),
                    "step": checkpoint_tuple.metadata.get("step", -1),
                    "ts": checkpoint_tuple.checkpoint.get("ts", ""),
                }
            )
    except Exception:
        pass
    return history
