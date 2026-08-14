"""test_event_log_efficacy.py — eventos + eficácia + fim do bypass (P3 part-4).

Cobre: event_log grava/lê e nunca levanta; insert gera evento generation SÓ
após commit (rollback = zero eventos); update_flashcard_fields ganha gate;
learning_efficacy agrega fixture com proveniência. Pytest-nativo + standalone.
"""
import contextlib
import io
import json
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import event_log  # noqa: E402
import insert_questao as iq  # noqa: E402
import learning_efficacy as le  # noqa: E402
from app.utils import db  # noqa: E402
from test_insert_questao import _DDL, _base_kwargs  # noqa: E402  (fixture compartilhada)


def _log_temp():
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    os.remove(path)
    return path


def test_registrar_e_ler():
    log = _log_temp()
    try:
        assert event_log.registrar("generation", {"questao_id": 1, "n_cards": 2}, log_path=log)
        assert event_log.registrar("reincidencia", {"questao_id": 1, "hits": 3}, log_path=log)
        evs = event_log.eventos(log_path=log)
        assert len(evs) == 2 and evs[0]["tipo"] == "generation" and "ts" in evs[0]
        assert len(event_log.eventos("reincidencia", log_path=log)) == 1
    finally:
        os.remove(log)


def test_falha_de_log_nunca_levanta():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        ok = event_log.registrar("generation", {"x": 1},
                                 log_path="Z:/caminho/impossivel/log.jsonl")
    assert ok is False and "EVENT_LOG" in out.getvalue(), "WARN visivel, sem excecao"


def _com_db_e_log(fn):
    fd, tmp = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(tmp)
    con.executescript(_DDL)
    con.commit()
    con.close()
    log = _log_temp()
    orig_iq, orig_db, orig_log = iq.DB_PATH, db.DB_PATH, event_log.LOG_PATH
    iq.DB_PATH, db.DB_PATH, event_log.LOG_PATH = tmp, tmp, log
    try:
        return fn(tmp, log)
    finally:
        iq.DB_PATH, db.DB_PATH, event_log.LOG_PATH = orig_iq, orig_db, orig_log
        os.remove(tmp)
        if os.path.exists(log):
            os.remove(log)


def test_insert_gera_evento_pos_commit_e_falha_gera_zero():
    def corpo(tmp, log):
        cards = [{"frente_pergunta": "Qual o criterio da sindrome ficticia?",
                  "verso_resposta": "Criterio Y."}]
        with contextlib.redirect_stdout(io.StringIO()):
            assert iq.insert_questao(**_base_kwargs(cards=cards)) is True
        evs = event_log.eventos("generation", log_path=log)
        assert len(evs) == 1 and evs[0]["n_cards"] == 1, f"evento pos-commit (got {evs})"
        assert not any("frente" in k or "verso" in k for k in evs[0]), \
            "evento nunca carrega texto clinico"
        # insert que FALHA (sem cards) -> nenhum evento novo
        with contextlib.redirect_stdout(io.StringIO()):
            assert iq.insert_questao(**_base_kwargs()) is False
        assert len(event_log.eventos(log_path=log)) == 1, "rollback = zero eventos novos"
    _com_db_e_log(corpo)


def _semear_card(tmp):
    con = sqlite3.connect(tmp)
    con.execute("INSERT INTO taxonomia_cronograma (area, tema) VALUES ('A', 'T')")
    con.execute("INSERT INTO questoes_erros (tema_id, titulo) VALUES (1, 'caso')")
    con.execute("INSERT INTO flashcards (questao_id, tema_id, tipo, frente_pergunta, "
                "verso_resposta, quality_source, card_version) "
                "VALUES (1, 1, 'conteudo', 'P?', 'R.', 'heuristic', 1)")
    con.commit()
    con.close()


def test_update_flashcard_fields_gate_fecha_bypass():
    def corpo(tmp, log):
        _semear_card(tmp)
        try:
            db.update_flashcard_fields(1, {"frente_pergunta": "X: qual a conduta/criterio correto?"})
            raise AssertionError("template deveria ser recusado pelo gate")
        except ValueError as e:
            assert "estilo-flashcard" in str(e)
        con = sqlite3.connect(tmp)
        ver = con.execute("SELECT card_version FROM flashcards WHERE id=1").fetchone()[0]
        con.close()
        assert ver == 1, "reescrita reprovada nao incrementa versao"
        assert db.update_flashcard_fields(1, {"frente_pergunta": "Qual o criterio da sindrome?"}) is True
        con = sqlite3.connect(tmp)
        ver2, fp = con.execute("SELECT card_version, frente_pergunta FROM flashcards WHERE id=1").fetchone()
        con.close()
        assert ver2 == 2 and fp == "Qual o criterio da sindrome?", "caminho valido intacto"
    _com_db_e_log(corpo)


def test_efficacy_agrega_proveniencia():
    def corpo(tmp, log):
        _semear_card(tmp)
        con = sqlite3.connect(tmp)
        # o _DDL compartilhado nao tem revlog — cria ja com as colunas P3
        con.execute("CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "card_id INTEGER, rating INTEGER, card_version INTEGER, "
                    "selection_reason TEXT)")
        dados = [(1, 1, 1, "fresh_error"), (1, 3, 1, "fresh_error"),
                 (1, 3, 2, "vencido"), (1, 3, None, None)]  # ultima = pre-P3
        for cid, rating, ver, mot in dados:
            con.execute("INSERT INTO fsrs_revlog (card_id, rating, card_version, "
                        "selection_reason) VALUES (?, ?, ?, ?)", (cid, rating, ver, mot))
        con.commit()
        con.close()
        event_log.registrar("generation", {"questao_id": 1, "n_cards": 1}, log_path=log)
        event_log.registrar("reincidencia", {"questao_id": 2, "hits": 1}, log_path=log)
        r = le.compute(db_path=tmp, log_path=log)
        assert r["card_version"]["1"]["total"] == 2 and r["card_version"]["1"]["again_rate"] == 0.5
        assert r["card_version"]["2"]["again_rate"] == 0.0
        assert r["selection_reason"]["pre-P3"]["total"] == 1, "linhas antigas agrupam como pre-P3"
        assert r["reincidencia"] == {"geracoes": 1, "reincidencias": 1, "taxa": 1.0,
                                     "nota": r["reincidencia"]["nota"]}
    _com_db_e_log(corpo)


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
    print("TODOS OS TESTES PASSARAM (P3 part-4)")
