"""test_batch_insert.py -- testes da part-4 (errors-file transacional + status F26).

Atomicidade (rollback total), dedupe por conteudo, anulada sem card + gate de
evidencia. Tudo em db temp (monkeypatch DB_PATH). Pytest-nativo + standalone.
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

import insert_questao as iq  # noqa: E402


def _db_temp():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0,
            questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0,
            ultima_revisao TEXT);
        CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema_id INTEGER, titulo TEXT, complexidade TEXT, enunciado TEXT,
            alternativa_correta TEXT, alternativa_marcada TEXT, tipo_erro TEXT,
            habilidades_sequenciais TEXT, o_que_faltou TEXT, explicacao_correta TEXT,
            armadilha_prova TEXT, data_registro TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT,
            questao_id INTEGER, tema_id INTEGER, tipo TEXT, frente_contexto TEXT,
            frente_pergunta TEXT, verso_resposta TEXT, verso_regra_mestre TEXT,
            verso_armadilha TEXT, quality_source TEXT, needs_qualitative INTEGER);
        CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due TIMESTAMP);
    """)
    con.commit()
    con.close()
    return path


def _item(n, **overrides):
    base = dict(
        area="Cirurgia", tema="Apendicite Aguda",
        enunciado=f"Enunciado do caso {n} com detalhes suficientes.",
        correta=f"Conduta correta {n}", marcada=f"Conduta errada {n}",
        erro="Conceitual", elo=f"elo do caso {n} sobre conduta cirurgica",
        armadilha=f"armadilha {n}", titulo=f"Caso {n}",
    )
    base.update(overrides)
    return base


def _lote_file(itens):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(itens, fh, ensure_ascii=False)
    return path


def _counts(db_path):
    con = sqlite3.connect(db_path)
    q = con.execute("SELECT COUNT(*) FROM questoes_erros").fetchone()[0]
    c = con.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    con.close()
    return q, c


def test_lote_valido_transacao_unica():
    tmp, orig = _db_temp(), iq.DB_PATH
    iq.DB_PATH = tmp
    lote = _lote_file([_item(1), _item(2), _item(3)])
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_batch(lote)
        q, c = _counts(tmp)
        assert ok is True and q == 3, f"3 erros inseridos (got ok={ok}, q={q})"
        assert c >= 3, f"cards cunhados por item (got {c})"
        assert "3 erro(s) inserido(s)" in out.getvalue(), "resumo do lote"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)
        os.remove(lote)


def test_item_invalido_nada_inserido():
    tmp, orig = _db_temp(), iq.DB_PATH
    iq.DB_PATH = tmp
    lote = _lote_file([_item(1), _item(2, correta=""), _item(3)])
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_batch(lote)
        assert ok is False, "lote invalido recusado"
        assert _counts(tmp) == (0, 0), "pre-validacao: ZERO inserido"
        assert "item 1" in out.getvalue() and "correta" in out.getvalue(), \
            "erro aponta item e campo"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)
        os.remove(lote)


def test_excecao_no_meio_rollback_total():
    tmp, orig = _db_temp(), iq.DB_PATH
    iq.DB_PATH = tmp
    # item 3 passa a pre-validacao mas explode DENTRO da transacao
    # (cards sem frente_pergunta -> ValueError no insert_questao)
    lote = _lote_file([_item(1), _item(2), _item(3, cards=[{"tipo": "conteudo"}])])
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_batch(lote)
        assert ok is False, "lote abortado"
        assert _counts(tmp) == (0, 0), \
            f"ROLLBACK TOTAL: itens 1-2 nao persistem (got {_counts(tmp)})"
        assert "ROLLBACK TOTAL" in out.getvalue()
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)
        os.remove(lote)


def test_dedupe_reexecucao_nao_duplica():
    tmp, orig = _db_temp(), iq.DB_PATH
    iq.DB_PATH = tmp
    lote = _lote_file([_item(1), _item(2)])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            assert iq.insert_batch(lote) is True
        q1, c1 = _counts(tmp)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok2 = iq.insert_batch(lote)
        assert ok2 is True, "re-execucao nao e erro"
        assert _counts(tmp) == (q1, c1), "nada duplicado"
        assert "2 pulado(s)" in out.getvalue() and "[SKIP]" in out.getvalue(), \
            "itens pulados avisados"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)
        os.remove(lote)


def test_status_anulada_sem_card_com_gate():
    tmp, orig = _db_temp(), iq.DB_PATH
    iq.DB_PATH = tmp
    lote = _lote_file([_item(1, status="banca-divergente"), _item(2)])
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_batch(lote)
        texto = out.getvalue()
        assert ok is True
        con = sqlite3.connect(tmp)
        st = con.execute("SELECT status FROM questoes_erros WHERE titulo='Caso 1'").fetchone()[0]
        cards_q1 = con.execute(
            "SELECT COUNT(*) FROM flashcards f JOIN questoes_erros q ON q.id=f.questao_id "
            "WHERE q.titulo='Caso 1'").fetchone()[0]
        cards_q2 = con.execute(
            "SELECT COUNT(*) FROM flashcards f JOIN questoes_erros q ON q.id=f.questao_id "
            "WHERE q.titulo='Caso 2'").fetchone()[0]
        con.close()
        assert st == "banca-divergente", f"status persistido (got {st})"
        assert cards_q1 == 0, "anulada/divergente NAO cunha card"
        assert cards_q2 >= 1, "item valido do mesmo lote cunha normalmente"
        assert "[GATE-EVIDENCIA]" in texto, "marcada p/ gate de evidencia"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)
        os.remove(lote)


def test_single_com_status_anulada():
    tmp, orig = _db_temp(), iq.DB_PATH
    iq.DB_PATH = tmp
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_questao(
                area="Cirurgia", tema="Apendicite Aguda",
                enunciado="Q10: gabarito oficial A x EMED C.",
                correta="C (EMED)", chamada="C", erro="Banca",
                elo="sinal de McBurney nao existe, e PONTO",
                armadilha="gabarito divergente", status="banca-divergente")
        assert ok is True and "[GATE-EVIDENCIA]" in out.getvalue()
        assert _counts(tmp)[1] == 0, "sem card no modo single tambem"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)


if __name__ == "__main__":
    fns = [test_lote_valido_transacao_unica, test_item_invalido_nada_inserido,
           test_excecao_no_meio_rollback_total, test_dedupe_reexecucao_nao_duplica,
           test_status_anulada_sem_card_com_gate, test_single_com_status_anulada]
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
    print("TODOS OS TESTES PASSARAM (part-4)")
