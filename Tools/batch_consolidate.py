"""
Batch consolidation of all existing session logs into LangMem memory.
Runs manager.consolidate_session() for each session_NNN.md found in history/.

Usage:
    python Tools/batch_consolidate.py

Skips session_048 (already consolidated). Prints progress per session.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.memory.store import SQLiteMemoryStore
from app.memory.manager import consolidate_session

HISTORY_DIR = Path("history")
SKIP_SESSIONS = {48}  # already consolidated


def main() -> None:
    store = SQLiteMemoryStore("medhub_memory.db")

    session_files = sorted(HISTORY_DIR.glob("session_*.md"))
    sessions = []
    for f in session_files:
        m = re.match(r"session_(\d+)\.md", f.name)
        if m:
            n = int(m.group(1))
            if n not in SKIP_SESSIONS:
                sessions.append(n)

    total = len(sessions)
    print(f"[batch] {total} sessões para consolidar (pulando: {SKIP_SESSIONS})\n")

    for i, num in enumerate(sessions, 1):
        print(f"[{i}/{total}] Consolidando sessão {num:03d}...")
        consolidate_session(num, store=store)

    print(f"\n[batch] Concluído. {total} sessões injetadas na memória longa.")


if __name__ == "__main__":
    main()
