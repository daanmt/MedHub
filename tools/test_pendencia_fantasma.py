"""F101: pendência do HANDOFF que o banco já desmente ("pendência-fantasma").

Escrito ANTES do fix (AGENTE.md 10.6). O caso medido: o HANDOFF da s179 e da s180
cobrou *"`registrar_sessao_bulk` da lista de Diarreia de 09/09 -- 3a sessão seguida
sem feitas/acertos"*. O registro EXISTIA desde a s175 (`175 | Pediatria | 41 | 34 |
2026-09-09`): a s179 herdou o texto do 1º ato da s175, escrito ANTES do registro, e a
s180 copiou. Custo evitado no fio: **+41 questões duplicadas** no SSOT volumétrico.

Classe: claim que envelhece sem re-medição (AGENTE 10.9, "número sem data é claim que
envelhece"). O gate que faltava: uma pendência que cita registro VERIFICÁVEL (data) é
checável contra `sessoes_bulk`, e ninguém checava.

⚠️ LIMITE DECLARADO, e ele é grande: o check só alcança pendência com **forma
reconhecível** -- palavra-chave de registro faltante MAIS uma data. Pendência escrita
em prosa livre ("falta lançar o bloco de ontem") é invisível para ele, e isso fica dito
em vez de maquiado. É WARN por nascimento (AGENTE 6, regra nova nasce warn-first).
"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import consistencia_check as cc  # noqa: E402

# shape do leitor: (data_sessao, area, feitas). O registro real da s175 era
# `175 | Pediatria | 41 | 34 | 2026-09-09`.
REGISTROS = [("2026-09-09", "Pediatria", 41)]


class PendenciaFantasma(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _handoff(self, corpo):
        p = os.path.join(self.raiz, "HANDOFF.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(corpo)
        return p

    def _check(self, corpo, registros=REGISTROS):
        self._handoff(corpo)
        return cc.check_pendencia_fantasma(root=self.raiz, _registros=registros)

    # ---- o caso literal do F101 ------------------------------------------

    def test_pendencia_desmentida_pelo_banco_e_achado(self):
        achados = self._check(
            "## Pendencias\n"
            "- `registrar_sessao_bulk` da lista de Diarreia de 09/09/2026 -- "
            "3a sessao seguida sem feitas/acertos\n")
        self.assertEqual(len(achados), 1, f"deveria acusar 1 fantasma; veio {achados}")
        self.assertIn("2026-09-09", str(achados[0]))

    def test_data_curta_ddmm_tambem_e_reconhecida(self):
        """O HANDOFF real escreve `09/09`, sem o ano."""
        achados = self._check(
            "- falta registrar o bloco de 09/09 -- sem feitas/acertos ainda\n")
        self.assertEqual(len(achados), 1)

    # ---- o que NAO pode virar achado --------------------------------------

    def test_pendencia_verdadeira_fica_quieta(self):
        """Data sem registro no banco = pendencia REAL. Silencio."""
        achados = self._check(
            "- `registrar_sessao_bulk` do bloco de 16/09/2026 -- sem feitas/acertos\n")
        self.assertEqual(achados, [])

    def test_linha_sem_data_nao_e_alcancavel(self):
        """LIMITE DECLARADO: prosa livre sem data e invisivel -- e isso e dito."""
        achados = self._check("- falta lancar o bloco de ontem, sem feitas/acertos\n")
        self.assertEqual(achados, [])

    def test_data_sem_palavra_de_registro_nao_dispara(self):
        """Mencionar uma data nao e cobrar registro. Sem isso o check vira ruido."""
        achados = self._check("- prova UERJ em 01/11/2026; inscricao feita em 09/09/2026\n")
        self.assertEqual(achados, [])

    def test_sem_handoff_nao_inventa_achado(self):
        achados = cc.check_pendencia_fantasma(root=self.raiz, _registros=REGISTROS)
        self.assertEqual(achados, [])

    def test_leitor_sem_dado_degrada_para_silencio(self):
        """Nao acusar por nao conseguir checar (regra herdada do F31).

        Lista vazia = o leitor de volume nao devolveu nada (banco ausente, tabela
        vazia, import quebrado). `None` e outra coisa -- significa "use o leitor
        real" -- e por isso este teste passa `[]`, nao `None`.
        """
        achados = self._check(
            "- `registrar_sessao_bulk` de 09/09/2026 sem feitas/acertos\n", registros=[])
        self.assertEqual(achados, [])

    # ---- registro no harness ----------------------------------------------

    def test_check_esta_no_registro_do_modulo(self):
        self.assertIn("fantasma", cc.CHECKS)
        rotulo, fn = cc.CHECKS["fantasma"]
        self.assertTrue(rotulo)
        self.assertIs(fn, cc.check_pendencia_fantasma)


if __name__ == "__main__":
    unittest.main()
