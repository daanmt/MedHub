"""test_selo_suite.py -- F136: o HANDOFF nao sela com numero de suite velho nem com suite vermelha.

O defeito (s200 -> s201): o selo reescreveu o HANDOFF depois da ultima suite; commit so de doc nao
rodava o pytest no pre-commit, e a consistencia no hook e WARN -- a sessao fechou 1119/1120 com o
HANDOFF dizendo "suite **1120**". Remedio de MECANISMO (veredito do /ai-eng, 26/09): HANDOFF staged
dispara a suite completa no hook, e o numero declarado tem de ser o medido ali.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import auto_check  # noqa: E402


def test_handoff_staged_dispara_a_suite():
    assert auto_check.dispara_suite_por_selo(["HANDOFF.md"]) is True
    assert auto_check.dispara_suite_por_selo(["AUDITORIA_MEDHUB.md", "history/session_201.md"]) is False
    assert auto_check.dispara_suite_por_selo([]) is False


def test_contagem_do_resumo_do_pytest():
    assert auto_check.contagem_pytest("1142 passed, 309 warnings, 8 subtests passed in 75.45s") == (1142, 0)
    assert auto_check.contagem_pytest(
        "FAILED tools/x.py::t - Ass...\n1 failed, 1119 passed, 310 warnings in 96.58s") == (1119, 1)
    assert auto_check.contagem_pytest("2 failed, 3 errors, 10 passed in 1s") == (10, 5)
    assert auto_check.contagem_pytest("sem resumo") is None


def test_handoff_com_o_numero_medido_passa():
    txt = "- **Engenharia:** suite **1142** (s201); outra coisa"
    assert auto_check.divergencia_suite_handoff(txt, (1142, 0)) is None
    assert auto_check.divergencia_suite_handoff("sem numero de suite", (1142, 0)) is None


def test_numero_velho_no_handoff_bloqueia():
    msg = auto_check.divergencia_suite_handoff("suite **1120** (s200)", (1119, 1))
    assert msg and "1120" in msg and "1119" in msg
    assert auto_check.divergencia_suite_handoff("suite **1120** (s200)", (1142, 0))


def test_suite_vermelha_declarada_como_tal_passa_e_verde_declarada_nao():
    assert auto_check.divergencia_suite_handoff("SUITE VERMELHA 1119/1120 -- falha: x", (1119, 1)) is None
    assert auto_check.divergencia_suite_handoff("suite **1120**", (1119, 1))
    assert auto_check.divergencia_suite_handoff("SUITE VERMELHA 1100/1120", (1119, 1))
