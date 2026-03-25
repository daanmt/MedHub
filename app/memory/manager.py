"""
Background memory consolidation for MedHub.

Called at session close (via registrar-sessao.md workflow) to:
  1. Read history/session_NNN.md
  2. Extract areas worked + weakness patterns
  3. Update ("medhub", "weak_areas") namespace
  4. Create entry in ("medhub", "session_insights")
  5. Deduplicate existing weak_area entries

Uses create_memory_store_manager with claude-haiku-4-5 (low cost).
Graceful fallback if ANTHROPIC_API_KEY is absent.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from app.memory.store import SQLiteMemoryStore


_HISTORY_DIR = Path("history")
_HAIKU_MODEL = "claude-haiku-4-5-20251001"


def _read_session_log(session_num: int) -> str | None:
    """Return the text of history/session_NNN.md, or None if missing."""
    path = _HISTORY_DIR / f"session_{session_num:03d}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _extract_areas_from_log(log_text: str) -> list[str]:
    """Heuristically extract medical areas mentioned in session log."""
    known_areas = [
        "Clínica Médica", "Cardiologia", "Pneumologia", "Nefrologia",
        "Gastroenterologia", "Endocrinologia", "Reumatologia", "Neurologia",
        "Hematologia", "Infectologia",
        "GO", "Ginecologia", "Obstetrícia",
        "Pediatria", "Neonatologia",
        "Cirurgia", "Ortopedia", "Neurocirurgia",
        "Preventiva", "Saúde Pública", "Epidemiologia",
        "Psiquiatria", "Dermatologia", "Oftalmologia", "Otorrinolaringologia",
        "Urologia", "Oncologia",
    ]
    found = []
    for area in known_areas:
        if area.lower() in log_text.lower():
            found.append(area)
    return found


def _llm_consolidate(
    session_log: str,
    session_id: str,
    store: SQLiteMemoryStore,
) -> None:
    """Use LangMem's memory store manager to extract + persist insights."""
    try:
        from langmem import create_memory_store_manager
        from langchain_anthropic import ChatAnthropic
        from app.memory.schemas import SessionInsight, WeakArea

        llm = ChatAnthropic(model=_HAIKU_MODEL, api_key=os.environ["ANTHROPIC_API_KEY"])

        manager = create_memory_store_manager(
            llm,  # positional-only nesta versão do LangMem
            schemas=[SessionInsight, WeakArea],
            store=store,
            namespace=("medhub", "session_insights"),
            instructions=(
                "You are analyzing a MedHub study session log. "
                "Extract: (1) memorable clinical insights worth remembering across sessions, "
                "(2) recurring weakness patterns in specific medical areas. "
                "Be concise and specific. Do NOT extract workflow/infrastructure notes."
            ),
        )

        manager.invoke(
            {"messages": [{"role": "user", "content": session_log}]},
            config={"configurable": {"thread_id": session_id}},
        )

    except Exception as e:
        print(f"[memory/manager] LLM consolidation skipped: {e}")




def _fallback_consolidate(
    session_log: str,
    session_id: str,
    store: SQLiteMemoryStore,
) -> None:
    """Simple heuristic consolidation when no API key / LLM available."""
    areas = _extract_areas_from_log(session_log)
    if not areas:
        return

    # Store a basic session insight listing areas covered
    insight_key = session_id
    store.put(
        ("medhub", "session_insights"),
        insight_key,
        {
            "session_id": session_id,
            "insight": f"Áreas trabalhadas: {', '.join(areas)}",
            "area": areas[0] if areas else "Geral",
        },
    )
    print(f"[memory/manager] Fallback insight salvo para {session_id}: {areas}")


def consolidate_session(
    session_num: int,
    store: SQLiteMemoryStore | None = None,
    db_path: str = "medhub_memory.db",
) -> None:
    """Main entry point — consolidate a session into long-term memory.

    Args:
        session_num: Session number (e.g., 46)
        store: Optional pre-built store; if None, creates one from db_path
        db_path: Path to medhub_memory.db (default: current directory)
    """
    if store is None:
        store = SQLiteMemoryStore(db_path)

    session_id = f"session_{session_num:03d}"
    log_text = _read_session_log(session_num)

    if log_text is None:
        print(f"[memory/manager] Sessão {session_id} não encontrada em history/. Pulando consolidação.")
        return

    print(f"[memory/manager] Consolidando {session_id}...")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        _llm_consolidate(log_text, session_id, store)
    else:
        _fallback_consolidate(log_text, session_id, store)

    print(f"[memory/manager] {session_id} consolidado.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m app.memory.manager <session_num>")
        sys.exit(1)

    consolidate_session(int(sys.argv[1]))
