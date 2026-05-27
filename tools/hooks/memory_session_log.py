#!/usr/bin/env python3
"""
PostToolUse(Write) hook: detecta criação de session log e automatiza fechamento.
Consolida memória longa via manager.py (background) + reindexia RAG (inline).
"""
import json
import os
import re
import subprocess
import sys
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

# Consolidação em background (Haiku: ~30–60s, não bloqueia)
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
    messages.append(f"[Memory v1] Erro ao iniciar consolidacao: {e}")

# RAG reindex inline (Ollama local: ~10–15s, aceitável no hook)
env = {
    **os.environ,
    "OBSIDIAN_RAG_PROVIDER": "ollama",
    "OBSIDIAN_RAG_MODEL": "nomic-embed-text:latest",
    "OBSIDIAN_RAG_VAULT": str(PROJECT_ROOT),
    "OBSIDIAN_RAG_DATA": str(Path.home() / "AppData/Local/obsidian-notes-rag/medhub"),
}
try:
    result = subprocess.run(
        ["uvx", "obsidian-notes-rag", "index"],
        cwd=str(PROJECT_ROOT), env=env,
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode == 0:
        messages.append("[Memory v2] RAG reindexado.")
    else:
        messages.append(f"[Memory v2] Reindex falhou: {result.stderr[:80]}")
except subprocess.TimeoutExpired:
    messages.append("[Memory v2] Reindex timeout — sera feito na proxima sessao.")
except Exception as e:
    messages.append(f"[Memory v2] Reindex erro: {e}")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "\n".join(messages)
    }
}))
