"""conftest raiz (F12, engenharia-ledger part-4).

Garante que `import app.utils...` e `import tools...` resolvam a partir da
raiz do repo quando o pytest roda de qualquer cwd. Os suites script-style
continuam executaveis standalone (python tools/test_X.py) -- este arquivo
nao os altera.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
