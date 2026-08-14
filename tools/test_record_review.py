"""test_record_review.py — trava técnica da Invariante C (part-2, flashcards-integridade).

Cobre: fluxo normal intacto, lock otimista (2ª aplicação do MESMO estado lido
falha e NÃO loga), upsert do caso sem linha FSRS (revisão não se perde mais),
last_elapsed_days populado. Tudo em db temp — ipub.db real NUNCA é tocado.
Pytest-nativo + standalone.
"""
import contextlib
import io
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd  # noqa: E402
from app.utils import db  # noqa: E402

_DDL = """
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT,
    frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
    verso_regra_mestre TEXT, verso_armadilha TEXT,
    quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (
    card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0, due DATETIME,
    stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
    elapsed_days INTEGER DEFAULT 0, scheduled_days INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME,
    FOREIGN KEY (card_id) REFERENCES flashcards(id));
CREATE TABLE fsrs_revlog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER, rating INTEGER, state INTEGER, due DATETIME,
    stability REAL, difficulty REAL, elapsed_days INTEGER,
    last_elapsed_days INTEGER, scheduled_days INTEGER,
    review_time DATETIME DEFAULT CURRENT_TIMESTAMP);
"""


def _db_temp(com_estado_fsrs=True):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                "quality_source) VALUES (1, 'conteudo', 'P?', 'R.', 'qualitative')")
    if com_estado_fsrs:
        con.execute("INSERT INTO fsrs_cards (card_id, state, due) "
                    "VALUES (1, 0, datetime('now'))")
    con.commit()
    con.close()
    return path


def _com_db(fn, **kw):
    tmp = _db_temp(**kw)
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        return fn(tmp)
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def _revlog(tmp):
    con = sqlite3.connect(tmp)
    rows = con.execute("SELECT card_id, rating, last_elapsed_days FROM fsrs_revlog").fetchall()
    con.close()
    return rows


def _ler_estado(conn, card_id=1):
    df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn, params=(card_id,))
    return df.iloc[0].to_dict()


def test_fluxo_normal_intacto():
    def corpo(tmp):
        with contextlib.redirect_stdout(io.StringIO()):
            m = db.record_review(1, 3)
        assert m["reps"] == 1 and m["state"] in (1, 2, 3), f"metrics coerentes (got {m})"
        assert len(_revlog(tmp)) == 1, "1 revisao = 1 linha de log"
        con = sqlite3.connect(tmp)
        lr = con.execute("SELECT last_review FROM fsrs_cards WHERE card_id=1").fetchone()[0]
        con.close()
        assert lr, "estado gravado (last_review preenchido)"
    _com_db(corpo)


def test_corrida_segunda_aplicacao_falha_sem_log():
    def corpo(tmp):
        conn1 = db.get_connection()
        estado_lido = _ler_estado(conn1)
        conn1.close()
        # 1ª aplicação do estado lido: passa
        conn_a = db.get_connection()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                db._aplicar_review(conn_a, dict(estado_lido), 3)
        finally:
            conn_a.close()
        # 2ª aplicação do MESMO estado lido: corrida -> falha, revlog intacto
        conn_b = db.get_connection()
        try:
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    db._aplicar_review(conn_b, dict(estado_lido), 4)
                raise AssertionError("2a aplicacao do mesmo estado deveria falhar")
            except db.ConcurrentReviewError:
                pass  # comportamento esperado
        finally:
            conn_b.close()
        rows = _revlog(tmp)
        assert len(rows) == 1, f"revlog NAO ganha linha na corrida (got {len(rows)})"
        assert rows[0][1] == 3, "estado final = resultado da 1a aplicacao"
    _com_db(corpo)


def test_card_sem_linha_fsrs_ganha_insert():
    def corpo(tmp):
        with contextlib.redirect_stdout(io.StringIO()):
            m = db.record_review(1, 3)
        con = sqlite3.connect(tmp)
        n = con.execute("SELECT COUNT(*) FROM fsrs_cards WHERE card_id=1").fetchone()[0]
        con.close()
        assert n == 1, "linha FSRS criada (antes: UPDATE fantasma perdia a revisao)"
        assert m["reps"] == 1
        assert len(_revlog(tmp)) == 1
    _com_db(corpo, com_estado_fsrs=False)


def test_last_elapsed_days_populado():
    def corpo(tmp):
        con = sqlite3.connect(tmp)
        con.execute("UPDATE fsrs_cards SET elapsed_days = 5 WHERE card_id = 1")
        con.commit()
        con.close()
        with contextlib.redirect_stdout(io.StringIO()):
            db.record_review(1, 3)
        rows = _revlog(tmp)
        assert rows[0][2] == 5, f"last_elapsed_days = elapsed anterior (got {rows[0][2]})"
    _com_db(corpo)


if __name__ == "__main__":
    fns = [test_fluxo_normal_intacto, test_corrida_segunda_aplicacao_falha_sem_log,
           test_card_sem_linha_fsrs_ganha_insert, test_last_elapsed_days_populado]
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
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-2)")
