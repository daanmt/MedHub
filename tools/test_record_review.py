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
from datetime import datetime, timedelta

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


@contextlib.contextmanager
def _relogio(instante):
    """`db.agora` congelado (o relogio unico, F80) -- a recusa de futuro usa ele."""
    orig = db.agora
    db.agora = lambda: instante
    try:
        yield
    finally:
        db.agora = orig


def _linha_fsrs(tmp, card_id=1):
    con = sqlite3.connect(tmp)
    linha = con.execute("SELECT due, last_review, scheduled_days FROM fsrs_cards "
                        "WHERE card_id = ?", (card_id,)).fetchone()
    con.close()
    return linha


def test_record_review_com_quando_grava_no_relogio_da_revisao():
    """s193 (medhub-hub-v0-part-2): a nota das 07:17 gravada as 20:00 entra no revlog
    as 07:17 e o intervalo conta de 07:17 -- em 22/09 o relogio da gravacao deslocou o
    `due` do #92 em 12h."""
    quando = datetime(2026, 9, 22, 7, 17, 50)

    def corpo(tmp):
        with _relogio(datetime(2026, 9, 22, 20, 0, 0)), \
                contextlib.redirect_stdout(io.StringIO()):
            db.record_review(1, 3, quando=quando)
        con = sqlite3.connect(tmp)
        rt = con.execute("SELECT review_time FROM fsrs_revlog").fetchone()[0]
        con.close()
        assert rt == "2026-09-22 07:17:50", f"review_time = quando (got {rt})"
        due, last_review, dias = _linha_fsrs(tmp)
        assert last_review == "2026-09-22 07:17:50", f"last_review = quando (got {last_review})"
        assert datetime.fromisoformat(due) == quando + timedelta(days=dias), (
            f"due calculado a partir de quando: {due} != {quando} + {dias}d")
    _com_db(corpo)


def test_record_review_recusa_quando_no_futuro_sem_gravar():
    def corpo(tmp):
        agora = datetime(2026, 9, 22, 20, 0, 0)
        with _relogio(agora):
            try:
                db.record_review(1, 3, quando=agora + timedelta(seconds=1))
                raise AssertionError("quando no futuro deveria ser recusado")
            except ValueError as e:
                assert "futuro" in str(e)
        assert _revlog(tmp) == [], "revlog intacto"
        assert _linha_fsrs(tmp)[1] is None, "estado FSRS intacto"
    _com_db(corpo)


def test_record_review_recusa_revisao_que_nao_e_posterior_a_ultima():
    """O py-fsrs NAO recusa um review_datetime anterior ao last_review: calcula
    `days < 1` e trata como curto prazo, em silencio. A guarda e do adapter."""
    def corpo(tmp):
        with _relogio(datetime(2026, 9, 22, 20, 0, 0)), \
                contextlib.redirect_stdout(io.StringIO()):
            db.record_review(1, 3, quando=datetime(2026, 9, 21, 10, 30, 0))
            for anterior in (datetime(2026, 9, 20, 7, 0, 0), datetime(2026, 9, 21, 10, 30, 0)):
                try:
                    db.record_review(1, 2, quando=anterior)
                    raise AssertionError(f"{anterior} nao e posterior a ultima revisao")
                except ValueError as e:
                    assert "posterior" in str(e)
        assert len(_revlog(tmp)) == 1, "so a 1a revisao gravou"
    _com_db(corpo)


def test_proveniencia_e_a_do_instante_da_revisao():
    """F76 com o relogio da revisao: card com due 22/09 06:00 respondido as 07:17 era
    'agendado'; gravado no dia seguinte, recomputar no relogio de parede daria 'vencido'
    e plantaria uma divergencia falsa no contador de gate-miss (B1)."""
    def corpo(tmp):
        con = sqlite3.connect(tmp)
        con.execute("UPDATE fsrs_cards SET state = 2, stability = 5.0, difficulty = 5.0, "
                    "due = '2026-09-22 06:00:00', last_review = '2026-09-17 06:00:00', "
                    "reps = 1 WHERE card_id = 1")
        con.commit()
        con.close()
        with _relogio(datetime(2026, 9, 23, 10, 0, 0)), \
                contextlib.redirect_stdout(io.StringIO()):
            m = db.record_review(1, 3, selection_reason="agendado",
                                 quando=datetime(2026, 9, 22, 7, 17, 50))
        assert m["reason_servido"] == "agendado", m["reason_servido"]
        assert m["reason_divergente"] is False
    _com_db(corpo)


def test_pyfsrs_aceita_revisao_retroativa_em_silencio():
    """FATO DE BIBLIOTECA, com versao (s193; contrato `fsrs-management` v1.5): o py-fsrs
    6.3.1 NAO recusa `review_datetime` anterior ao `last_review` -- calcula `days < 1`,
    trata como revisao de curto prazo e segue, sem erro. E por isso que a guarda de ordem
    mora no adapter (`FSRS.evaluate(quando)`). Se a lib mudar de versao ou de
    comportamento, este teste avisa: reconferir o fato no contrato e a guarda."""
    from datetime import timezone
    from importlib.metadata import version
    from fsrs import Card, Rating, Scheduler
    assert version("fsrs") == "6.3.1", (
        "py-fsrs mudou de versao (%s): reconferir o fato no contrato fsrs-management "
        "(revisao retroativa aceita em silencio) e a guarda do adapter" % version("fsrs"))
    s = Scheduler(learning_steps=(), enable_fuzzing=False)
    depois = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)
    card, _ = s.review_card(Card(), Rating.Good, depois)
    antes = depois - timedelta(days=2)
    retro, _ = s.review_card(card, Rating.Good, antes)          # nao levanta
    assert retro.last_review == antes, "a lib aceita e grava a revisao no passado"


def test_proveniencia_card_version_e_reason():
    """P3 part-1: revlog registra a versao VISTA e o motivo de servico; pos-
    reforja (card_version 1->2), a nova revisao registra 2 — 'v2 > v1?' vira
    pergunta respondivel."""
    def corpo(tmp):
        with contextlib.redirect_stdout(io.StringIO()):
            db.record_review(1, 3, selection_reason="vencido")
        con = sqlite3.connect(tmp)
        v1 = con.execute("SELECT card_version, selection_reason FROM fsrs_revlog "
                         "ORDER BY id DESC LIMIT 1").fetchone()
        con.execute("UPDATE flashcards SET card_version = 2 WHERE id = 1")
        con.commit()
        con.close()
        with contextlib.redirect_stdout(io.StringIO()):
            db.record_review(1, 3)  # sem reason: NULL (retro-compativel)
        con = sqlite3.connect(tmp)
        v2 = con.execute("SELECT card_version, selection_reason FROM fsrs_revlog "
                         "ORDER BY id DESC LIMIT 1").fetchone()
        con.close()
        assert v1 == (1, "vencido"), f"1a revisao: versao vista=1 + reason (got {v1})"
        assert v2 == (2, None), f"pos-reforja: versao vista=2, reason NULL (got {v2})"
    _com_db(corpo)


if __name__ == "__main__":
    fns = [test_fluxo_normal_intacto, test_corrida_segunda_aplicacao_falha_sem_log,
           test_card_sem_linha_fsrs_ganha_insert, test_last_elapsed_days_populado,
           test_record_review_com_quando_grava_no_relogio_da_revisao,
           test_record_review_recusa_quando_no_futuro_sem_gravar,
           test_record_review_recusa_revisao_que_nao_e_posterior_a_ultima,
           test_proveniencia_e_a_do_instante_da_revisao,
           test_pyfsrs_aceita_revisao_retroativa_em_silencio,
           test_proveniencia_card_version_e_reason]
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
