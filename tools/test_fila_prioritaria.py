"""test_fila_prioritaria.py — banda prioritária no dreno padrão (P3 part-2).

Ordem servida: vencidos → erros_frescos (janela/cap) → agendados → novos FIFO;
sem duplicata entre buckets; card-base fresco (sem questao_id) NÃO fura a fila;
selection_reason em todo card. Tudo em db temp. Pytest-nativo + standalone.
"""
import io
import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.utils import db  # noqa: E402

_DDL = """
CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT);
CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY, tema_id INTEGER, titulo TEXT);
CREATE TABLE flashcards (id INTEGER PRIMARY KEY, questao_id INTEGER,
    tema_id INTEGER, tipo TEXT, frente_contexto TEXT, frente_pergunta TEXT,
    verso_resposta TEXT, verso_regra_mestre TEXT, verso_armadilha TEXT,
    quality_source TEXT DEFAULT 'qualitative', card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due DATETIME);
"""


def _import_fsrs_queue():
    """fsrs_queue troca sys.stdout no import — protege o capture do pytest."""
    orig = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        import fsrs_queue
        return fsrs_queue
    finally:
        sys.stdout = orig


def _semear(con, cid, state, due, questao_id=None):
    con.execute("INSERT INTO flashcards (id, questao_id, tema_id, tipo, "
                "frente_pergunta, verso_resposta) VALUES (?, ?, 1, 'conteudo', 'P?', 'R.')",
                (cid, questao_id))
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, ?, ?)",
                (cid, state, due))


def _fixture():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    con.execute("INSERT INTO taxonomia_cronograma VALUES (1, 'Cirurgia', 'Apendicite Aguda')")
    con.execute("INSERT INTO questoes_erros VALUES (1, 1, 'caso')")
    agora = datetime.now()
    _semear(con, 1, 2, agora - timedelta(days=2))                    # vencido
    _semear(con, 2, 0, agora - timedelta(hours=1), questao_id=1)     # erro fresco
    _semear(con, 3, 2, agora)                                        # agendado hoje
    _semear(con, 4, 0, agora - timedelta(days=10), questao_id=1)     # novo velho (fora da janela)
    _semear(con, 5, 0, agora - timedelta(hours=2))                   # base fresco SEM questao -> novo
    con.commit()
    con.close()
    return path


def _com_db(fn):
    tmp = _fixture()
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        return fn(tmp)
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def test_buckets_e_reasons():
    def corpo(tmp):
        b = db.get_cards_by_bucket(new_limit=10)
        ids = {k: [c["card_id"] for c in v] for k, v in b.items()}
        assert ids["atrasados"] == [1] and ids["hoje"] == [3]
        assert ids["erros_frescos"] == [2], f"so erro fresco COM questao fura (got {ids})"
        assert ids["novos"] == [4, 5], f"novo velho + base fresco ficam no FIFO (got {ids})"
        reasons = {c["card_id"]: c["selection_reason"] for v in b.values() for c in v}
        assert reasons == {1: "vencido", 2: "fresh_error", 3: "agendado",
                           4: "novo", 5: "novo"}, reasons
    _com_db(corpo)


def test_sem_duplicata_entre_buckets():
    def corpo(tmp):
        b = db.get_cards_by_bucket(new_limit=10)
        todos = [c["card_id"] for v in b.values() for c in v]
        assert len(todos) == len(set(todos)), f"card em 2 buckets: {sorted(todos)}"
    _com_db(corpo)


def test_ordem_servida_na_fila():
    def corpo(tmp):
        fq = _import_fsrs_queue()
        ordem = [c["card_id"] for c in fq._ordered_queue(new_limit=10)]
        assert ordem == [1, 2, 3, 4, 5], f"vencido->fresco->hoje->novos (got {ordem})"
        buckets = [c["bucket"] for c in fq._ordered_queue(new_limit=10)]
        assert buckets == ["atrasados", "erros_frescos", "hoje", "novos", "novos"]
    _com_db(corpo)


def test_cap_da_banda():
    def corpo(tmp):
        con = sqlite3.connect(tmp)
        agora = datetime.now()
        for i in range(10, 10 + db.CAP_FRESH + 4):  # 12 frescos extras
            _semear(con, i, 0, agora - timedelta(minutes=i), questao_id=1)
        con.commit()
        con.close()
        b = db.get_cards_by_bucket(new_limit=50)
        assert len(b["erros_frescos"]) == db.CAP_FRESH, \
            f"cap {db.CAP_FRESH} respeitado (got {len(b['erros_frescos'])})"
        ids_frescos = {c["card_id"] for c in b["erros_frescos"]}
        ids_novos = {c["card_id"] for c in b["novos"]}
        assert not (ids_frescos & ids_novos), "excedente do cap volta ao FIFO sem duplicar"
    _com_db(corpo)


def test_aposentado_fora_de_todos_os_buckets():
    def corpo(tmp):
        con = sqlite3.connect(tmp)
        con.execute("UPDATE flashcards SET needs_qualitative = 2 WHERE id = 2")
        con.commit()
        con.close()
        b = db.get_cards_by_bucket(new_limit=10)
        todos = {c["card_id"] for v in b.values() for c in v}
        assert 2 not in todos, "aposentado nao aparece em bucket nenhum (ativo canonico)"
    _com_db(corpo)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    falhas = 0
    for fn in fns:
        try:
            fn()
            print("  OK  " + fn.__name__)
        except AssertionError as e:
            falhas += 1
            print("  XX  %s: %s" % (fn.__name__, e))
    print()
    if falhas:
        print("FALHOU: %d teste(s)" % falhas)
        sys.exit(1)
    print("TODOS OS TESTES PASSARAM (P3 part-2)")
