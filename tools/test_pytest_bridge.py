"""Bridge pytest -> suites script-style (F12, engenharia-ledger part-4).

Os suites test_fsrs / test_memory / test_revisao_calibrada sao scripts com
checks impressos + exit code (0=passou). Coleta-los crus pelo pytest daria
verde decorativo (funcao sem assert passa mesmo com check falhando).
Este bridge roda cada um por subprocess -- execucao identica a manual --
e asserta o exit code. cwd = raiz do repo (test_revisao_calibrada e
cwd-sensivel) e PYTHONIOENCODING=utf-8 (test_memory imprime U+2192 e quebra
em pipe cp1252 sem isso; ver decisions.md 2026-04-23).

test_autonomia_hooks.py e unittest nativo e o pytest o coleta direto.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_suite(script):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, os.path.join("tools", script)],
        cwd=ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def test_suite_revisao_calibrada():
    res = _run_suite("test_revisao_calibrada.py")
    assert res.returncode == 0, f"test_revisao_calibrada falhou:\n{res.stdout[-2000:]}"


def test_suite_fsrs():
    res = _run_suite("test_fsrs.py")
    assert res.returncode == 0, f"test_fsrs falhou:\n{res.stdout[-2000:]}"


def test_suite_memory():
    res = _run_suite("test_memory.py")
    assert res.returncode == 0, f"test_memory falhou:\n{res.stdout[-2000:]}"
