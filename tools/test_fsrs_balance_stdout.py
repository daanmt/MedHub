"""Regressao (hotfix 2026-09-06, s166): o balanceador de carga do FSRS nao pode
escrever em stdout.

`tools/fsrs_queue.py --record` tem contrato de saida JSON pura em stdout
(skill /revisar). `_balancear_due` imprimia `[FSRS_BALANCE] due X -> Y` e o
fallback de excecao imprimia `[WARN] FSRS_BALANCE ...` via print() simples,
contaminando o stdout e quebrando `json.load` no consumidor (3 de 14 records
do sub-bloco 1.1 da s166). Informacao de operador vai para stderr.

Fixtures sinteticas (tmp), nada toca o ipub.db real.
"""
import contextlib
import io
import os
import sqlite3
import sys
import tempfile
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


def _db_temp(n_no_alvo, alvo):
    """Banco com `n_no_alvo` cards de revisao agendados no dia-alvo e nenhum
    nos vizinhos -- garante que o balanceador DESLOQUE o due."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    for i in range(1, n_no_alvo + 2):
        con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                    "quality_source) VALUES (?, 'conteudo', 'P?', 'R.', 'qualitative')", (i,))
    for i in range(2, n_no_alvo + 2):
        con.execute("INSERT INTO fsrs_cards (card_id, state, due, scheduled_days) "
                    "VALUES (?, 2, ?, 30)", (i, datetime.combine(alvo, datetime.min.time())))
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (1, 2, datetime('now'))")
    con.commit()
    con.close()
    return path


def _capturar(fn):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        r = fn()
    return r, out.getvalue(), err.getvalue()


def test_info_do_balanceador_nao_vai_para_stdout():
    alvo = date.today() + timedelta(days=30)
    tmp = _db_temp(n_no_alvo=5, alvo=alvo)
    try:
        con = sqlite3.connect(tmp)
        cur = con.cursor()
        metrics = {"due": datetime.combine(alvo, datetime.min.time()),
                   "scheduled_days": 30, "state": 2}
        novo, out, err = _capturar(lambda: db._balancear_due(cur, metrics))
        con.close()
    finally:
        os.remove(tmp)
    assert novo["due"].date() != alvo, "cenario invalido: o balanceador nao deslocou"
    assert out == "", f"stdout deveria ser vazio (contrato JSON do CLI); veio: {out!r}"
    assert "[FSRS_BALANCE]" in err, "a informacao do deslocamento tem que seguir visivel em stderr"


def test_warn_de_balanceamento_pulado_nao_vai_para_stdout(monkeypatch):
    alvo = date.today() + timedelta(days=30)
    tmp = _db_temp(n_no_alvo=1, alvo=alvo)
    orig = db.DB_PATH
    db.DB_PATH = tmp

    def _explode(cursor, metrics):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(db, "_balancear_due", _explode)
    try:
        _, out, err = _capturar(lambda: db.record_review(1, 3))
        con = sqlite3.connect(tmp)
        n = con.execute("SELECT COUNT(1) FROM fsrs_revlog WHERE card_id = 1").fetchone()[0]
        con.close()
    finally:
        db.DB_PATH = orig
        os.remove(tmp)
    assert n == 1, "a revisao tem que ser gravada mesmo com o balanceamento pulado"
    assert out == "", f"stdout deveria ser vazio; veio: {out!r}"
    assert "[WARN] FSRS_BALANCE" in err
