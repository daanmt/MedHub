"""Regressão do F107: `insert_questao --errors-file` não tinha pré-check.

Escrito ANTES do fix (AGENTE.md 10.6). O defeito medido na s184: um lote de 25
itens abortou DUAS vezes com ROLLBACK TOTAL no gate `resposta-embutida`, porque
o autor do lote não tinha como rodar os predicados antes de abrir a transação --
o gate só existia DENTRO do writer. Custo medido: 2 execuções perdidas (~2 min
cada) + 1 tentativa com assinatura errada de pré-check.

O remédio é `--dry-run`: roda os MESMOS predicados sobre o lote inteiro, relata
TUDO de uma vez e não abre transação. A prova de que é o mesmo gate (e não um
segundo sensor divergente -- o defeito de classe do F95/F102) é
`test_dry_run_e_writer_dao_o_mesmo_veredito`.

LIMITE DECLARADO: o dry-run nao consulta o banco (e esse e o ponto), logo nao
modela o **dedupe por conteudo** `(area, tema, enunciado)` que o writer aplica
ANTES do gate. Um item que o writer PULARIA por ja estar registrado ainda e
avaliado aqui. E falso positivo conservador -- o card ruim continua ruim -- e
fica declarado em vez de virar divergencia silenciosa entre os dois caminhos.
"""

import json
import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import insert_questao as iq  # noqa: E402

AREA, TEMA = "Pediatria", "Arboviroses"

# Frente que repete um run >= RUN_MIN (6) tokens do titulo da questao-mae.
TITULO_RUIM = "Dengue grupo C exige hidratacao venosa imediata em ambiente hospitalar"
CARD_RUIM = {
    "tipo": "elo_quebrado",
    "frente_pergunta": TITULO_RUIM + "?",
    "verso_resposta": "Sim, por 48 horas.",
}
CARD_BOM = {
    "tipo": "elo_quebrado",
    "frente_pergunta": "Que achado promove dengue do grupo B para o grupo C?",
    "verso_resposta": "Extravasamento plasmatico com hipotensao postural.",
}


def _item(titulo, cards, enunciado=None):
    # enunciado DISTINTO por item: o dedupe por conteudo (area, tema, enunciado)
    # roda ANTES do gate no writer, e itens homonimos seriam PULADOS sem nunca
    # chegar ao predicado -- mascarando exatamente o que este arquivo mede.
    return {"area": AREA, "tema": TEMA,
            "enunciado": enunciado or ("Caso clinico de 7 anos -- " + titulo),
            "correta": "B", "marcada": "C", "erro": "ancoragem no numero",
            "elo": "nao converteu o dado em conduta", "armadilha": "grupo C x D",
            "titulo": titulo, "cards": cards}


class DryRunF107(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self._db_orig = iq.DB_PATH

    def tearDown(self):
        iq.DB_PATH = self._db_orig
        self._tmp.cleanup()

    def _lote(self, *itens):
        p = os.path.join(self.dir, "lote.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(list(itens), fh, ensure_ascii=False)
        return p

    def _db_inexistente(self):
        """DB_PATH para arquivo AUSENTE: se abrir transacao, sqlite3 o CRIA."""
        p = os.path.join(self.dir, "nao-deve-nascer.db")
        iq.DB_PATH = p
        return p

    _seq = 0

    def _db_real(self):
        # nome unico por chamada: subtests criam bancos independentes
        DryRunF107._seq += 1
        p = os.path.join(self.dir, f"ipub{DryRunF107._seq}.db")
        con = sqlite3.connect(p)
        con.executescript("""
            CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0,
                questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0,
                ultima_revisao TEXT, UNIQUE(area, tema));
            CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY AUTOINCREMENT,
                tema_id INTEGER, titulo TEXT, complexidade TEXT, enunciado TEXT,
                alternativa_correta TEXT, alternativa_marcada TEXT, tipo_erro TEXT,
                habilidades_sequenciais TEXT, o_que_faltou TEXT, explicacao_correta TEXT,
                armadilha_prova TEXT, data_registro TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT,
                questao_id INTEGER, tema_id INTEGER, tipo TEXT, frente_contexto TEXT,
                frente_pergunta TEXT, verso_resposta TEXT, verso_regra_mestre TEXT,
                verso_armadilha TEXT, quality_source TEXT, needs_qualitative INTEGER);
            CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER,
                due TIMESTAMP);
        """)
        con.commit()
        con.close()
        iq.DB_PATH = p
        return p

    @staticmethod
    def _contar(path, tabela):
        con = sqlite3.connect(path)
        try:
            return con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        finally:
            con.close()

    # ---- o caso literal do F107 -------------------------------------------

    def test_dry_run_acusa_sem_abrir_transacao(self):
        alvo = self._db_inexistente()
        lote = self._lote(_item(TITULO_RUIM, [CARD_RUIM]))
        self.assertFalse(iq.insert_batch(lote, dry_run=True))
        self.assertFalse(os.path.exists(alvo),
                         "F107: o dry-run abriu conexao e criou o banco")

    def test_dry_run_relata_TODOS_os_itens_ruins_de_uma_vez(self):
        """A dor medida: 2 rollbacks sequenciais, um por item ruim."""
        self._db_inexistente()
        lote = self._lote(_item(TITULO_RUIM, [CARD_RUIM], enunciado="Caso A"),
                          _item("Titulo sadio de controle", [CARD_BOM], enunciado="Caso B"),
                          _item(TITULO_RUIM, [CARD_RUIM], enunciado="Caso C"))
        achados = iq.checar_lote(lote)
        indices = {a["item"] for a in achados}
        self.assertEqual(indices, {0, 2},
                         f"dry-run deve relatar itens 0 e 2 juntos; veio {achados}")

    def test_dry_run_pega_campo_obrigatorio_ausente(self):
        self._db_inexistente()
        mau = _item("Falta campo", [CARD_BOM])
        del mau["erro"]
        self.assertFalse(iq.insert_batch(self._lote(mau), dry_run=True))

    def test_dry_run_aprova_lote_valido_sem_gravar(self):
        alvo = self._db_real()
        antes = self._contar(alvo, "questoes_erros")
        lote = self._lote(_item("Promocao de grupo na dengue", [CARD_BOM]))
        self.assertTrue(iq.insert_batch(lote, dry_run=True))
        self.assertEqual(self._contar(alvo, "questoes_erros"), antes,
                         "dry-run gravou no banco")

    # ---- uma regra, dois chamadores ---------------------------------------

    def test_dry_run_e_writer_dao_o_mesmo_veredito(self):
        """Anti-F95: o pre-check nao pode ser um segundo sensor divergente."""
        for cards, titulo in ((CARD_RUIM, TITULO_RUIM),
                              (CARD_BOM, "Promocao de grupo na dengue")):
            with self.subTest(titulo=titulo[:30]):
                alvo = self._db_real()
                lote = self._lote(_item(titulo, [cards]))
                seco = iq.insert_batch(lote, dry_run=True)
                molhado = iq.insert_batch(lote)
                self.assertEqual(seco, molhado)
                if not seco:
                    self.assertEqual(self._contar(alvo, "questoes_erros"), 0,
                                     "reprovado no dry-run mas o writer gravou")

    def test_writer_sem_dry_run_segue_com_rollback_total(self):
        """O comportamento antigo nao muda: lote ruim continua abortando inteiro."""
        alvo = self._db_real()
        lote = self._lote(_item("Promocao de grupo na dengue", [CARD_BOM]),
                          _item(TITULO_RUIM, [CARD_RUIM]))
        self.assertFalse(iq.insert_batch(lote))
        self.assertEqual(self._contar(alvo, "questoes_erros"), 0,
                         "rollback total deixou insercao parcial")


if __name__ == "__main__":
    unittest.main()
