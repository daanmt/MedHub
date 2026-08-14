"""test_auto_check_watermark.py — watermark de dado dos cards (part-6).

O harness deixa de ser cego ao dado: a tripla (MAX(id), COUNT(*),
MAX(card_version)) detecta insert, delete e reforja in-place no ipub.db —
mesmo com zero arquivos staged. Cobre tambem os modos defensivos (banco
inacessivel, marco corrompido) e a regra de selar-so-depois. Pytest-nativo +
standalone.
"""
import contextlib
import io
import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_check as ac  # noqa: E402


def _db_temp():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "frente_pergunta TEXT, card_version INTEGER DEFAULT 1)")
    con.execute("INSERT INTO flashcards (frente_pergunta) VALUES ('P?')")
    con.commit()
    con.close()
    return path


def _marco_temp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.remove(path)  # comeca inexistente
    return path


def _silencioso(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **kw)


def test_sem_marco_dispara_e_selar_estabiliza():
    db, marco = _db_temp(), _marco_temp()
    try:
        mudou, atual = _silencioso(ac.card_watermark_mudou, db, marco)
        assert mudou is True, "sem marco = 'mudou' (primeira corrida)"
        ac.card_watermark_selar(atual, marco)
        mudou2, _ = _silencioso(ac.card_watermark_mudou, db, marco)
        assert mudou2 is False, "marco selado + dado igual = nao dispara"
    finally:
        os.remove(db)
        if os.path.exists(marco):
            os.remove(marco)


def test_insert_dispara():
    db, marco = _db_temp(), _marco_temp()
    try:
        _, atual = _silencioso(ac.card_watermark_mudou, db, marco)
        ac.card_watermark_selar(atual, marco)
        con = sqlite3.connect(db)
        con.execute("INSERT INTO flashcards (frente_pergunta) VALUES ('P2?')")
        con.commit()
        con.close()
        mudou, _ = _silencioso(ac.card_watermark_mudou, db, marco)
        assert mudou is True, "INSERT no banco dispara o gatilho"
    finally:
        os.remove(db)
        os.remove(marco)


def test_reforja_in_place_dispara():
    # UPDATE que so incrementa card_version: MAX(id) e COUNT nao mudam.
    db, marco = _db_temp(), _marco_temp()
    try:
        _, atual = _silencioso(ac.card_watermark_mudou, db, marco)
        ac.card_watermark_selar(atual, marco)
        con = sqlite3.connect(db)
        con.execute("UPDATE flashcards SET card_version = 2 WHERE id = 1")
        con.commit()
        con.close()
        mudou, _ = _silencioso(ac.card_watermark_mudou, db, marco)
        assert mudou is True, "reforja in-place (card_version++) dispara"
    finally:
        os.remove(db)
        os.remove(marco)


def test_marco_corrompido_dispara_com_warn():
    db, marco = _db_temp(), _marco_temp()
    try:
        with open(marco, "w", encoding="utf-8") as fh:
            fh.write("{nao-e-json")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            mudou, _ = ac.card_watermark_mudou(db, marco)
        assert mudou is True, "marco ilegivel = fail-open"
        assert "CARD_WATERMARK" in out.getvalue(), "WARN visivel (sensor nunca silencia)"
    finally:
        os.remove(db)
        os.remove(marco)


def test_banco_inacessivel_dispara_com_warn():
    marco = _marco_temp()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        mudou, atual = ac.card_watermark_mudou("Z:/caminho/inexistente/x.db", marco)
    assert mudou is True and atual is None, "banco inacessivel = fail-open"
    assert "CARD_WATERMARK" in out.getvalue()
    # selar com None e no-op (nao cria marco falso)
    ac.card_watermark_selar(None, marco)
    assert not os.path.exists(marco), "marco NAO avanca sem leitura real do banco"


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
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-6)")
