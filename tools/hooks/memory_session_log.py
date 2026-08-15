#!/usr/bin/env python3
"""
PostToolUse(Write) hook: detecta criação de session log e automatiza fechamento.
Consolida memória longa via manager.py (background).
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Lê tool input do stdin
try:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)

# Só processa history/session_NNN.md
match = re.search(r'[/\\]session_(\d+)\.md$', file_path)
if not match or "history" not in file_path.replace("\\", "/"):
    sys.exit(0)

session_num = int(match.group(1))
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
messages = []

def _log_error(context, exc):
    """Append 1 linha em history/memory_errors.log — mesma superficie usada
    pelo processo filho (app/memory/manager.py). Nunca levanta."""
    try:
        log = PROJECT_ROOT / "history" / "memory_errors.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        short = str(exc).replace("\n", " ")[:300]
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now().isoformat(timespec='seconds')}\t{context}\t{type(exc).__name__}: {short}\n")
    except Exception:
        pass


# Consolidação em background (Haiku: ~30–60s, não bloqueia).
# Fire-and-forget de proposito: o filho tem try/except global e registra
# a propria falha em history/memory_errors.log (stdout/stderr = DEVNULL).
try:
    flags = subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
    subprocess.Popen(
        [sys.executable, "-m", "app.memory.manager", str(session_num)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    messages.append(f"[Memory v1] Consolidacao da sessao {session_num:03d} iniciada em background.")
except Exception as e:
    _log_error(f"spawn/session_{session_num:03d}", e)
    messages.append(f"[Memory v1] Erro ao iniciar consolidacao: {e}")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "\n".join(messages)
    }
}))
