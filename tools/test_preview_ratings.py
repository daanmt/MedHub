"""test_preview_ratings.py — preview dos 4 intervalos (P3 part-3).

Read-only comprovado (zero escrita), paridade com o scheduler determinístico,
card novo (sem linha FSRS) coberto. Pytest-nativo + standalone.
"""
import contextlib
import io
import os
import sqlite3
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.utils import db  # noqa: E402
from app.utils.fsrs import FSRS  # noqa: E402

_DDL = """
CREATE TABLE flashcards (id INTEGER PRIMARY KEY, tipo TEXT,
    frente_pergunta TEXT, verso_resposta TEXT, card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due DATETIME,
    stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
    elapsed_days INTEGER DEFAULT 0, scheduled_days INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME);
CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER,
    rating INTEGER, state INTEGER, due DATETIME, stability REAL, difficulty REAL,
    elapsed_days INTEGER, last_elapsed_days INTEGER, scheduled_days INTEGER,
    review_time DATETIME DEFAULT CURRENT_TIMESTAMP);
"""


def _com_db(fn, com_estado=True):
    fd, tmp = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(tmp)
    con.executescript(_DDL)
    con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta) "
                "VALUES (1, 'conteudo', 'P?', 'R.')")
    if com_estado:
        con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (1, 0, ?)",
                    (datetime.now(),))
    con.commit()
    con.close()
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        return fn(tmp)
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def _snapshot(tmp):
    con = sqlite3.connect(tmp)
    s = (con.execute("SELECT COUNT(*) FROM fsrs_revlog").fetchone()[0],
         con.execute("SELECT COALESCE(SUM(reps),0), MAX(due) FROM fsrs_cards").fetchone())
    con.close()
    return s


def test_preview_read_only_e_shape():
    def corpo(tmp):
        antes = _snapshot(tmp)
        p = db.preview_ratings(1)
        assert set(p) == {"again", "hard", "good", "easy"}
        for r in p.values():
            assert {"scheduled_days", "due", "rotulo", "balanceado_apos_record"} <= set(r)
        assert _snapshot(tmp) == antes, "preview NAO escreve nada"
        assert p["easy"]["scheduled_days"] >= p["good"]["scheduled_days"] >= \
            p["hard"]["scheduled_days"] >= p["again"]["scheduled_days"], \
            "monotonicidade dos intervalos"
    _com_db(corpo)


def test_paridade_com_scheduler():
    def corpo(tmp):
        con = sqlite3.connect(tmp)
        import pandas as pd
        estado = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = 1", con).iloc[0].to_dict()
        con.close()
        p = db.preview_ratings(1)
        for rating, nome in db.ROTULOS_RATING.items():
            m = FSRS().evaluate(dict(estado), rating)
            assert p[nome]["scheduled_days"] == int(m["scheduled_days"]), \
                f"preview[{nome}] diverge do evaluate (scheduler e deterministico)"
    _com_db(corpo)


def test_card_sem_linha_fsrs():
    def corpo(tmp):
        p = db.preview_ratings(1)  # sem fsrs_cards: init_card
        assert set(p) == {"again", "hard", "good", "easy"}
        assert _snapshot(tmp)[0] == 0, "nenhuma linha criada"
    _com_db(corpo, com_estado=False)


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
    print("TODOS OS TESTES PASSARAM (P3 part-3)")
