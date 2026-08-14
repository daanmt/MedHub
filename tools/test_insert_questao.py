"""test_insert_questao.py — contrato de cunhagem da part-1 (flashcards-integridade).

Cobre: fallback heurístico removido (sem cards = falha alta, zero linhas),
cards=[] recusado, caminho qualitativo íntegro, flags individuais convergindo,
PRAGMA foreign_keys imposto, filtro de aposentados em get_fresh_error_cards e
definição canônica de ativo na regen queue. Tudo em db temp — o ipub.db real
NUNCA é tocado. Pytest-nativo + standalone.
"""
import contextlib
import io
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
from app.utils import db  # noqa: E402


def _import_crq():
    """cards_regen_queue substitui sys.stdout no import (wrapper sobre .buffer).
    Damos a ele um BytesIO descartável — o wrapper que ele cria (e depois fecha
    no GC) nunca toca o capture do pytest — e restauramos o stdout original."""
    orig = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        import cards_regen_queue as crq
        return crq
    finally:
        sys.stdout = orig

# DDL fiel ao sqlite_master real (2026-08-14) — inclui as cláusulas REFERENCES
# para o teste de enforcement do PRAGMA.
_DDL = """
CREATE TABLE taxonomia_cronograma (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL, tema TEXT NOT NULL,
    questoes_realizadas INTEGER DEFAULT 0, questoes_acertadas INTEGER DEFAULT 0,
    percentual_acertos REAL DEFAULT 0.0, ultima_revisao DATE,
    dificuldade INTEGER, dificuldade_fonte TEXT, dificuldade_at TIMESTAMP);
CREATE TABLE questoes_erros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema_id INTEGER, titulo TEXT, complexidade TEXT, enunciado TEXT,
    alternativa_correta TEXT, alternativa_marcada TEXT, tipo_erro TEXT,
    habilidades_sequenciais TEXT, o_que_faltou TEXT, explicacao_correta TEXT,
    armadilha_prova TEXT, data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT NULL,
    FOREIGN KEY (tema_id) REFERENCES taxonomia_cronograma(id));
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT,
    frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
    verso_regra_mestre TEXT, verso_armadilha TEXT,
    quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
    needs_qualitative INTEGER DEFAULT 0,
    FOREIGN KEY (questao_id) REFERENCES questoes_erros(id),
    FOREIGN KEY (tema_id) REFERENCES taxonomia_cronograma(id));
CREATE TABLE fsrs_cards (
    card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0, due DATETIME,
    stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
    elapsed_days INTEGER DEFAULT 0, scheduled_days INTEGER DEFAULT 0,
    reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME,
    FOREIGN KEY (card_id) REFERENCES flashcards(id));
"""


def _db_temp():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    con.commit()
    con.close()
    return path


def _counts(db_path):
    con = sqlite3.connect(db_path)
    q = con.execute("SELECT COUNT(*) FROM questoes_erros").fetchone()[0]
    c = con.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    con.close()
    return q, c


def _base_kwargs(**overrides):
    kw = dict(area="Cirurgia", tema="Apendicite Aguda",
              enunciado="Caso com detalhes suficientes.", correta="Apendicectomia",
              chamada="Antibiotico isolado", erro="Conceitual",
              elo="indicacao cirurgica na apendicite", armadilha="melhora parcial com ATB")
    kw.update(overrides)
    return kw


def _com_db_temp(fn):
    """Roda fn(tmp_path) com iq.DB_PATH E db.DB_PATH apontando pro temp."""
    tmp = _db_temp()
    orig_iq, orig_db = iq.DB_PATH, db.DB_PATH
    iq.DB_PATH, db.DB_PATH = tmp, tmp
    try:
        return fn(tmp)
    finally:
        iq.DB_PATH, db.DB_PATH = orig_iq, orig_db
        os.remove(tmp)


def test_sem_cards_falha_alto_zero_linhas():
    def corpo(tmp):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_questao(**_base_kwargs())  # sem cards, sem par, sem status
        assert ok is False, "sem cards deve falhar (fallback heuristico removido)"
        assert _counts(tmp) == (0, 0), f"ZERO linhas gravadas (got {_counts(tmp)})"
        assert "estilo-flashcard" in out.getvalue(), "erro cita a regua de autoria"
    _com_db_temp(corpo)


def test_cards_lista_vazia_recusada():
    def corpo(tmp):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = iq.insert_questao(**_base_kwargs(cards=[]))
        assert ok is False and _counts(tmp) == (0, 0), "cards=[] = mesmo erro alto"
    _com_db_temp(corpo)


def test_caminho_qualitativo_integro():
    def corpo(tmp):
        cards = [{"tipo": "conteudo", "frente_pergunta": "Qual a conduta na apendicite nao complicada?",
                  "verso_resposta": "Apendicectomia."}]
        with contextlib.redirect_stdout(io.StringIO()):
            ok = iq.insert_questao(**_base_kwargs(cards=cards))
        assert ok is True
        con = sqlite3.connect(tmp)
        qs, nq = con.execute("SELECT quality_source, needs_qualitative FROM flashcards").fetchone()
        st = con.execute("SELECT state FROM fsrs_cards").fetchone()[0]
        con.close()
        assert qs == "qualitative" and nq == 0, f"sempre qualitativo/ativo (got {qs}/{nq})"
        assert st == 0, "estado FSRS inicializado como novo"
    _com_db_temp(corpo)


def test_flags_individuais_convergem():
    def corpo(tmp):
        with contextlib.redirect_stdout(io.StringIO()):
            ok = iq.insert_questao(**_base_kwargs(
                frente_pergunta="Qual a conduta na apendicite nao complicada?",
                verso_resposta="Apendicectomia."))
        assert ok is True
        con = sqlite3.connect(tmp)
        n, tipo, qs = con.execute(
            "SELECT COUNT(*), MAX(tipo), MAX(quality_source) FROM flashcards").fetchone()
        con.close()
        assert (n, tipo, qs) == (1, "elo_quebrado", "qualitative"), \
            f"par de flags vira 1 card qualitativo (got {(n, tipo, qs)})"
    _com_db_temp(corpo)


def test_pragma_fk_ligado_na_fabrica():
    def corpo(tmp):
        conn = db.get_connection()
        try:
            assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1, \
                "get_connection deve ligar PRAGMA foreign_keys"
        finally:
            conn.close()
    _com_db_temp(corpo)


def test_fk_imposta_em_insert_orfao():
    def corpo(tmp):
        conn = db.get_connection()
        try:
            try:
                conn.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (999, 0, '2026-01-01')")
                conn.commit()
                raise AssertionError("INSERT orfao deveria falhar com FK imposta")
            except sqlite3.IntegrityError:
                pass  # comportamento esperado
        finally:
            conn.close()
    _com_db_temp(corpo)


def _semear_fresh(tmp, nq):
    """Insere 1 tema + 1 questao + 1 card state=0 due=agora com nq dado; retorna card_id."""
    con = sqlite3.connect(tmp)
    con.execute("INSERT INTO taxonomia_cronograma (area, tema) VALUES ('Cirurgia', 'Apendicite Aguda')")
    tid = con.execute("SELECT id FROM taxonomia_cronograma").fetchone()[0]
    con.execute("INSERT INTO questoes_erros (tema_id, titulo) VALUES (?, 'caso')", (tid,))
    qid = con.execute("SELECT MAX(id) FROM questoes_erros").fetchone()[0]
    con.execute("INSERT INTO flashcards (questao_id, tema_id, tipo, frente_pergunta, verso_resposta, "
                "quality_source, needs_qualitative) VALUES (?, ?, 'conteudo', 'P?', 'R.', 'qualitative', ?)",
                (qid, tid, nq))
    cid = con.execute("SELECT MAX(id) FROM flashcards").fetchone()[0]
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, datetime('now'))", (cid,))
    con.commit()
    con.close()
    return cid


def test_fresh_error_cards_filtra_aposentado():
    def corpo(tmp):
        cid_ativo = _semear_fresh(tmp, nq=0)
        cid_aposentado = _semear_fresh(tmp, nq=2)
        ids = {c["id"] for c in db.get_fresh_error_cards(janela_horas=48)}
        assert cid_ativo in ids, "card ativo fresco deve aparecer"
        assert cid_aposentado not in ids, "aposentado NAO vaza pela janela de frescor"
    _com_db_temp(corpo)


def test_regen_queue_definicao_canonica_de_ativo():
    def corpo(tmp):
        con = sqlite3.connect(tmp)
        con.execute("INSERT INTO taxonomia_cronograma (area, tema) VALUES ('Cirurgia', 'Apendicite Aguda')")
        con.execute("INSERT INTO questoes_erros (tema_id, titulo) VALUES (1, 'caso')")
        # heuristico nq=0 (ativo, entra) e nq=3 (aposentado por outra via, NAO entra)
        con.execute("INSERT INTO flashcards (questao_id, tema_id, tipo, frente_pergunta, verso_resposta, "
                    "quality_source, needs_qualitative) VALUES (1, 1, 'conteudo', 'P?', 'R.', 'heuristic', 0)")
        con.execute("INSERT INTO flashcards (questao_id, tema_id, tipo, frente_pergunta, verso_resposta, "
                    "quality_source, needs_qualitative) VALUES (1, 1, 'conteudo', 'P2?', 'R2.', 'heuristic', 3)")
        con.commit()
        con.close()
        fila = _import_crq().fetch_regen_queue()
        assert len(fila) == 1, "questao com heuristico ativo entra 1x"
        nqs = {c["needs_qualitative"] for c in fila[0]["cards_atuais"]}
        assert 0 in nqs, "card ativo presente na fila"
    _com_db_temp(corpo)


def test_batch_sem_cards_nada_inserido():
    def corpo(tmp):
        import json
        fd, lote = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(lote, "w", encoding="utf-8") as fh:
            json.dump([dict(_base_kwargs(), marcada="Antibiotico isolado", titulo="Caso 1")], fh)
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                ok = iq.insert_batch(lote)
            assert ok is False, "lote sem cards recusado na pre-validacao"
            assert _counts(tmp) == (0, 0), "NADA inserido"
            assert "estilo-flashcard" in out.getvalue(), "mensagem cita a regua"
        finally:
            os.remove(lote)
    _com_db_temp(corpo)


if __name__ == "__main__":
    fns = [test_sem_cards_falha_alto_zero_linhas, test_cards_lista_vazia_recusada,
           test_caminho_qualitativo_integro, test_flags_individuais_convergem,
           test_pragma_fk_ligado_na_fabrica, test_fk_imposta_em_insert_orfao,
           test_fresh_error_cards_filtra_aposentado,
           test_regen_queue_definicao_canonica_de_ativo,
           test_batch_sem_cards_nada_inserido]
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
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-1)")
