"""Testes do check de auto-suficiencia de flashcard (spec Part 1).

Cobre 1 fixture por anti-padrao + card-controle limpo (nao dispara) +
aplicacao por campo certo + robustez defensiva. Roda standalone (exit != 0
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

import card_self_sufficiency as css


def card(**kw):
    base = {"id": 1, "frente_contexto": None, "frente_pergunta": None,
            "verso_regra_mestre": None, "verso_armadilha": None,
            "area": "Area", "tema": "Tema"}
    base.update(kw)
    return base


class TestCardSelfSufficiency(unittest.TestCase):
    def _padroes(self, cards):
        return {a["padrao"] for a in css.run_checks(cards=cards)}

    def test_opcao_anaforico_front(self):
        """Front que cita 'por que a alternativa X esta errada' -> opcao-anaforico."""
        c = card(frente_pergunta="Por que a opcao 'proliferativa com C3 alto' esta errada?")
        self.assertIn("opcao-anaforico", self._padroes([c]))

    def test_enunciado_negativo_front(self):
        """'enunciado negativo' / 'afirmacao falsa' no front -> opcao-anaforico."""
        c = card(frente_contexto="Questao de enunciado negativo sobre antimalaricos.",
                 frente_pergunta="Qual a afirmacao falsa?")
        self.assertIn("opcao-anaforico", self._padroes([c]))

    def test_deitico_front(self):
        """Front que aponta 'neste caso/acima' -> deitico."""
        c = card(frente_contexto="Neste caso, no paciente acima descrito...",
                 frente_pergunta="Qual a conduta?")
        self.assertIn("deitico", self._padroes([c]))

    def test_pct_fake_verso(self):
        """Percentual fabricado no verso -> pct-fake."""
        c = card(frente_pergunta="Qual principio da Lei 8.080 e ferido?",
                 verso_armadilha="Marcar universalidade (61% caem) -- mas ha uma distincao.")
        self.assertIn("pct-fake", self._padroes([c]))

    def test_card_limpo_nao_dispara(self):
        """Vignette clinico auto-suficiente NAO dispara nenhum padrao."""
        c = card(frente_contexto="Homem jovem com poliartrite e purpura palpavel nas pernas.",
                 frente_pergunta="Qual o diagnostico mais provavel?",
                 verso_regra_mestre="Purpura palpavel + artrite sugere vasculite.",
                 verso_armadilha="Nao confundir com PTI, que cursa com plaquetas baixas.")
        self.assertEqual(self._padroes([c]), set())

    def test_padrao_so_no_campo_certo(self):
        """'acima' no VERSO (nao no front) nao pode disparar deitico (front-only)."""
        c = card(frente_pergunta="Qual o valor de referencia do potassio?",
                 verso_regra_mestre="Valores acima de 5,5 mEq/L definem hipercalemia.")
        self.assertNotIn("deitico", self._padroes([c]))

    def test_opcao_enumerada_dispara(self):
        """Rotulo de opcao embutido '(A) ...' no front -> opcao-anaforico."""
        c = card(frente_contexto="Crianca com PTI: (A) plaquetas 35.000 com sangramento.",
                 frente_pergunta="Qual a conduta?")
        self.assertIn("opcao-anaforico", self._padroes([c]))

    def test_alternativa_terapeutica_nao_dispara(self):
        """'alternativa AO metronidazol' e alternativa terapeutica, nao MCQ."""
        c = card(frente_pergunta="Qual a alternativa ao metronidazol nas vulvovaginites?")
        self.assertNotIn("opcao-anaforico", self._padroes([c]))

    def test_opcao_tratamento_nao_dispara(self):
        """'melhor opcao de profilaxia' e escolha terapeutica, nao MCQ."""
        c = card(frente_pergunta="Qual a melhor opcao de profilaxia da enxaqueca?")
        self.assertNotIn("opcao-anaforico", self._padroes([c]))

    def test_esta_correto_clinico_nao_dispara(self):
        """'o grupo esta correto?' e juizo clinico, nao gabarito de prova."""
        c = card(frente_pergunta="O grupo sanguineo esta correto? Identifique o erro.")
        self.assertNotIn("opcao-anaforico", self._padroes([c]))

    def test_acima_comparador_nao_dispara(self):
        """'acima' como comparador de valor (PA/idade/nivel) nao e deitico."""
        for perg in ("Paciente com PA acima de 160/110. Qual a conduta?",
                     "Lactente ja acima dos 3-6 meses. Qual a peculiaridade?",
                     "Lesao medular acima do nivel T6. Qual o risco?"):
            c = card(frente_pergunta=perg)
            self.assertNotIn("deitico", self._padroes([c]), perg)

    def test_substring_citad_nao_dispara(self):
        """'ressuscitada' contem 'citad' mas nao e referencia deitica (\\b)."""
        c = card(frente_contexto="Bolsa ressuscitada que passa a sangrar.",
                 frente_pergunta="Qual o proximo passo?")
        self.assertNotIn("deitico", self._padroes([c]))

    def test_defensivo_sem_crash(self):
        """Campos None e card vazio nao lancam e nao produzem achado."""
        self.assertEqual(css.run_checks(cards=[card(), {}]), [])

    def test_um_card_pode_ter_multiplos_padroes(self):
        """Front deitico + verso com %-fake -> dois achados no mesmo card."""
        c = card(id=99,
                 frente_pergunta="Neste caso, qual a alternativa correta?",
                 verso_armadilha="Muitos erram (55% marcam) a opcao B.")
        padroes = self._padroes([c])
        self.assertIn("deitico", padroes)
        self.assertIn("opcao-anaforico", padroes)
        self.assertIn("pct-fake", padroes)


if __name__ == "__main__":
    unittest.main()
