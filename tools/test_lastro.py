"""F103/F106: lastro de tema clínico medido por SEÇÃO, não por nome de arquivo.

Escrito ANTES do fix (AGENTE.md 10.6). O `[SEM-LASTRO]` do `insert_questao` casava
o tema contra o **nome do arquivo** (exato + fuzzy de stem). Resumo guarda-chuva --
um `.md` que cobre vários temas em seções -- ficava invisível, e a pendência
"criar resumo" que isso gera produziria um **duplicado**.

🔴 O QUE ESTA SUÍTE FIXA, e que o ledger errou nos dois sentidos (medido em 17/09/2026):

  - `Esquistossomose` NÃO tem lastro. O F106 afirmou que "vive em Parasitoses.md";
    medido, há **uma única linha** (`Parasitoses.md:43`), uma armadilha sobre a forma
    hepatoesplênica dentro de um diferencial de cirrose. Menção solta não é cobertura,
    e o `[SEM-LASTRO]` original estava CERTO. Esta é a fixture anti-inflação: uma regra
    de lastro por conteúdo solto daria True aqui e inflaria a cobertura -- o mesmo
    defeito de "string presente != coberto" que o `cli_signature_check` declara.

  - `Rede de Atenção Psicossocial (RAPS)` TEM lastro, e o ledger o registrou como o
    controle verdadeiro ("REAL, zero lastro"). Medido: `Psiquiatria Social e Reforma
    Psiquiátrica.md` traz `## 4. Rede de Atenção Psicossocial (RAPS)`, as modalidades
    CAPS, a Resolução 32/2017 e a mudança de paradigma -- e `RAPS` está nos `aliases`
    do frontmatter. Estava na fila como tarefa de criar resumo: seria duplicado.

  - `Polipos e Neoplasias Intestinais` TEM lastro (F103, este o ledger acertou).
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))


class LastroPorSecao(unittest.TestCase):

    def setUp(self):
        from tools.utils import lastro
        self.lastro = lastro

    # ---- os tres casos medidos ------------------------------------------

    def test_tema_com_secao_dedicada_tem_lastro(self):
        """F103: `##` dedicado num resumo guarda-chuva conta como lastro."""
        ok, motivo = self.lastro.tem_lastro("Polipos e Neoplasias Intestinais")
        self.assertTrue(ok, f"F103: secao dedicada nao foi vista (motivo={motivo})")

    def test_alias_do_frontmatter_conta(self):
        """RAPS: o `aliases:` do frontmatter e sinal que o projeto ja mantem."""
        ok, motivo = self.lastro.tem_lastro("Rede de Atenção Psicossocial (RAPS)")
        self.assertTrue(ok, f"RAPS: alias/secao nao foi visto (motivo={motivo})")

    def test_mencao_solta_no_corpo_NAO_e_lastro(self):
        """🔴 Fixture anti-inflacao. 1 linha citando o tema num diferencial de
        outra doenca nao e cobertura -- e o `[SEM-LASTRO]` original estava certo."""
        ok, motivo = self.lastro.tem_lastro("Esquistossomose")
        self.assertFalse(
            ok, f"inflou a cobertura: 1 mencao em corpo virou lastro (motivo={motivo})")

    # ---- o que ja funcionava nao pode regredir ---------------------------

    def test_nome_de_arquivo_exato_continua_valendo(self):
        ok, _ = self.lastro.tem_lastro("Polipose Intestinal e Câncer Colorretal")
        self.assertTrue(ok)

    def test_tema_inexistente_nao_tem_lastro(self):
        ok, _ = self.lastro.tem_lastro("Balneoterapia Quantica de Marte")
        self.assertFalse(ok)

    # ---- contrato da funcao ----------------------------------------------

    def test_devolve_motivo_nomeado(self):
        """O motivo e o que torna o veredito auditavel -- bool sozinho nao serve."""
        ok, motivo = self.lastro.tem_lastro("Polipos e Neoplasias Intestinais")
        self.assertTrue(ok)
        self.assertTrue(motivo, "veredito positivo sem motivo nomeado")
        self.assertRegex(motivo, r"(arquivo|pdf|secao|alias|mapa)")

    def test_conservador_quando_nao_consegue_checar(self):
        """Nunca acusar ausencia por falha de leitura (regra herdada do F31)."""
        ok, motivo = self.lastro.tem_lastro("Qualquer Tema", raiz="/caminho/inexistente")
        self.assertTrue(ok)
        self.assertIn("indeterminado", motivo)

    def test_uma_regra_um_lugar(self):
        """`insert_questao._tem_lastro` delega -- nao reimplementa (anti-F95)."""
        import insert_questao as iq
        for tema in ("Polipos e Neoplasias Intestinais",
                     "Rede de Atenção Psicossocial (RAPS)",
                     "Esquistossomose"):
            with self.subTest(tema=tema):
                self.assertEqual(iq._tem_lastro(tema),
                                 self.lastro.tem_lastro(tema)[0])


if __name__ == "__main__":
    unittest.main()
