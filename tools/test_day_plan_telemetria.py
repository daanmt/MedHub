"""Testes da telemetria de fila FSRS (spec Part 2): pool x divida.

Valida a rotulacao canonica (telemetria_fila) e que os renderizadores nao
apresentam mais o pool como 'backlog' agregado. Roda standalone (exit != 0
em falha) e e invocado pelo auto_check.
"""
import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR / "tools"))

import day_plan


def _p_fixture():
    """p minimo suficiente para render_handoff_block (nao toca o db)."""
    return {
        "volume": {"total": 5026, "acertos": 3976, "hoje": 18,
                   "alvo_enamed": 10000, "ritmo_alvo": 82.9, "dias_ate_marco": 60},
        "fsrs": {"atrasados": 22, "hoje": 4, "backlog_novos": 425},
        "divida": {"teto_efetivo": 30, "regime_divida": False, "teto_base": 30},
        "cronograma": None,
    }


class TestTelemetriaFila(unittest.TestCase):
    def test_separa_divida_hoje_pool(self):
        """telemetria_fila mapeia atrasados->divida, backlog_novos->pool, teto."""
        t = day_plan.telemetria_fila(
            {"atrasados": 22, "hoje": 4, "backlog_novos": 425},
            {"teto_efetivo": 30, "regime_divida": False})
        self.assertEqual(t["divida"], 22)
        self.assertEqual(t["hoje"], 4)
        self.assertEqual(t["pool"], 425)
        self.assertEqual(t["teto"], 30)
        self.assertFalse(t["regime_divida"])

    def test_handoff_block_sem_backlog_agregado(self):
        """O bloco do handoff separa pool e divida, sem o termo 'backlog'."""
        bloco = day_plan.render_handoff_block(_p_fixture()).lower()
        self.assertIn("pool", bloco)
        self.assertIn("divida", bloco)
        self.assertIn("425", bloco)   # pool
        self.assertIn("22", bloco)    # divida
        self.assertNotIn("backlog", bloco)

    def test_header_distingue_pool_divida(self):
        """O cabecalho do plano distingue pool x divida (via build sobre db vivo)."""
        if not (ROOT_DIR / "ipub.db").exists():
            self.skipTest("ipub.db ausente")
        header = day_plan.render(day_plan.build()).lower()
        self.assertIn("pool", header)
        self.assertIn("nunca introduzidos", header)
        # o antigo rotulo enganoso 'novos (backlog)' nao pode reaparecer
        self.assertNotIn("(backlog)", header)


if __name__ == "__main__":
    unittest.main()
