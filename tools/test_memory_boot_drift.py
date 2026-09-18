"""Regressão do F102: o hook de boot tinha parser PRÓPRIO de ponteiro de sessão.

Escrito ANTES do fix (AGENTE.md 10.6: defeito reproduzível -> teste de regressão
antes do remédio). O defeito medido em 17/09/2026, contra o código então vigente:

    HANDOFF em forma de s181  ->  `_handoff_session` devolveu 179
    regra canônica (state_utils.check_session_pointer)  ->  180

Três defeitos no mesmo parser, todos ausentes do gêmeo canônico:
  1. `re.search(r"\\bs(\\d{2,3})\\b", handoff)` é case-sensitive: o cabeçalho real
     grafa "S180" e o parser não via;
  2. lê a PRIMEIRA ocorrência do texto INTEIRO: qualquer menção a sessão anterior
     no corpo (ex.: "a regra da s179") sequestra o ponteiro;
  3. `_drift_flag` acusava sempre que `cited != latest`, mas `cited == latest + 1`
     é legítimo pela condição B2 do reconcile-contract (a sessão em curso, cujo
     log só nasce no fechamento).

Classe: F95 um nível abaixo -- dois sensores para a mesma condição, com regras
diferentes. O remédio é reuso, não um segundo parser corrigido.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _carregar_hook():
    """Carrega o hook por path (não é pacote importável)."""
    spec = importlib.util.spec_from_file_location(
        "memory_boot_f102", ROOT / "tools" / "hooks" / "memory_boot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DriftPonteiroF102(unittest.TestCase):

    def setUp(self):
        self.mb = _carregar_hook()
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        self.hist = self.raiz / "history"
        self.hist.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _handoff(self, texto):
        p = self.raiz / "HANDOFF.md"
        p.write_text(texto, encoding="utf-8")
        return p

    def _logs(self, *nums):
        for n in nums:
            (self.hist / f"session_{n:03d}.md").write_text("x", encoding="utf-8")

    def _flag(self, hp):
        return self.mb._drift_flag("", handoff_path=hp, history_dir=self.hist)

    # ---- o caso literal do F102 -------------------------------------------

    def test_cabecalho_maiusculo_nao_produz_drift_falso(self):
        """s181: cabeçalho grafa 'S180' e o corpo cita 's179' ANTES dele."""
        hp = self._handoff(
            "# HANDOFF.md\n"
            "*Atualizado: 2026-09-11 -- **S180 (SESSAO)**: aplica a regra da s179.*\n")
        self._logs(179, 180)
        self.assertEqual(
            self._flag(hp), "",
            "F102: 'S180' no cabeçalho + 's179' no corpo produziu drift falso")

    def test_mencao_incidental_nao_sequestra_o_ponteiro(self):
        """Menção a sessão antiga fora das linhas-âncora é ruído, não ponteiro."""
        hp = self._handoff(
            "*Atualizado: 2026-09-17 -- **s184**.*\n\n"
            "Ver a decisão da s099 e o bug medido na s101.\n")
        self._logs(184)
        self.assertEqual(self._flag(hp), "")

    # ---- a regra B2 que o hook ignorava -----------------------------------

    def test_sessao_em_curso_max_mais_um_nao_e_drift(self):
        """B2: ponteiro == max+1 é a sessão em curso; o log nasce no fechamento."""
        hp = self._handoff("*Atualizado: 2026-09-17 -- **s185**: sessão em curso.*\n")
        self._logs(184)
        self.assertEqual(self._flag(hp), "")

    # ---- o sensor não pode ficar cego -------------------------------------

    def test_drift_real_ainda_acusa(self):
        hp = self._handoff("*Atualizado: 2026-09-17 -- **s190**.*\n")
        self._logs(184)
        self.assertIn("190", self._flag(hp))

    def test_arquivo_ausente_ainda_acusa(self):
        """Ponteiro <= max mas sem o arquivo: o log referido não existe."""
        hp = self._handoff("*Atualizado: 2026-09-17 -- **s182**.*\n")
        self._logs(181, 184)
        self.assertNotEqual(self._flag(hp), "")

    # ---- uma regra, um lugar ----------------------------------------------

    def test_hook_e_auto_check_concordam(self):
        """F95 um nível abaixo: os dois sensores têm de dar o mesmo veredito."""
        from tools.utils.state_utils import check_session_pointer
        casos = [
            ("*Atualizado: 2026-09-11 -- **S180**: a regra da s179.*\n", (179, 180)),
            ("*Atualizado: 2026-09-17 -- **s185**.*\n", (184,)),
            ("*Atualizado: 2026-09-17 -- **s190**.*\n", (184,)),
        ]
        for texto, logs in casos:
            with self.subTest(texto=texto[:40]):
                for f in self.hist.glob("session_*.md"):
                    f.unlink()
                hp = self._handoff(texto)
                self._logs(*logs)
                canonico = check_session_pointer(handoff_path=hp, history_dir=self.hist)
                self.assertEqual(canonico is None, self._flag(hp) == "")

    def test_hook_nunca_derruba_o_boot(self):
        """Falha na dependência degrada para silêncio, nunca para exceção."""
        self.assertEqual(
            self.mb._drift_flag("", handoff_path=self.raiz / "nao-existe.md",
                                history_dir=self.hist), "")


if __name__ == "__main__":
    unittest.main()
