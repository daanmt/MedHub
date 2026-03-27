#!/usr/bin/env python3
"""
SessionStart hook: injeta contexto de memória longa no início da sessão.
Sem este hook, o agente precisa lembrar de chamar inspect.py --context manualmente.
"""
import json
import os
import sys
from pathlib import Path

# Navega para project root: Tools/hooks/memory_boot.py → Tools/hooks → Tools → MedHub/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

output = []
try:
    import io
    import contextlib
    from app.memory.inspect import load_context

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        load_context()
    output.append(buf.getvalue().strip())
except FileNotFoundError:
    output.append("[Memory v1] medhub_memory.db ainda não existe — primeira sessão.")
except Exception as e:
    output.append(f"[Memory v1] Aviso: {e}")

context_text = "\n".join(output) if output else ""
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context_text
    }
}))
