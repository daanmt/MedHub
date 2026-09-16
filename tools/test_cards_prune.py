"""Testes de tools/cards_prune.py (spec plano-ssot-e-cards-v2-part-5, DoD 4).

Banco sintetico em tmp_path com as 4 tabelas reais (colunas minimas do schema do ipub.db).
Fixtures: 1 aposentado sem historico (alvo), 1 aposentado com revlog (fica), 1 aposentado com
marca de reforja (fica), 1 ativo (fica). Backup e um stub injetado -- a poda nunca roda sem
`backup_fn`, e o CLI real injeta o backup_db.py.
"""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cards_prune  # noqa: E402

SCHEMA = """
CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT, questao_id INTEGER, tema_id INTEGER,
  tipo TEXT, frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT, verso_regra_mestre TEXT,
  verso_armadilha TEXT, quality_source TEXT DEFAULT 'legacy', card_version INTEGER DEFAULT 1,
  needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0, due DATETIME,
  stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0, elapsed_days INTEGER DEFAULT 0,
  scheduled_days INTEGER DEFAULT 0, reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME);
CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER, rating INTEGER,
  state INTEGER, due DATETIME, stability REAL, difficulty REAL, elapsed_days INTEGER,
  last_elapsed_days INTEGER, scheduled_days INTEGER, review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  card_version INTEGER, selection_reason TEXT, reason_servido TEXT);
CREATE TABLE reforja_marks (id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER NOT NULL,
  evento TEXT NOT NULL, motivo TEXT NOT NULL, evidencia TEXT, origem TEXT, criado_em DATETIME);
"""


def _db(tmp_path):
    conn = sqlite3.connect(tmp_path / "t.db")
    conn.executescript(SCHEMA)
    cards = [
        (1, "aposentado sem historico", 2),
        (2, "aposentado com revlog", 2),
        (3, "aposentado com marca de reforja", 2),
        (4, "ativo", 0),
    ]
    for cid, frente, nq in cards:
        conn.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, needs_qualitative) "
                     "VALUES (?, 'conteudo', ?, 'v', ?)", (cid, frente, nq))
        conn.execute("INSERT INTO fsrs_cards (card_id, state) VALUES (?, 0)", (cid,))
    conn.execute("INSERT INTO fsrs_revlog (card_id, rating, state) VALUES (2, 3, 2)")
    conn.execute("INSERT INTO fsrs_revlog (card_id, rating, state) VALUES (4, 4, 2)")
    conn.execute("INSERT INTO reforja_marks (card_id, evento, motivo) VALUES (3, 'marcada', 'teste')")
    conn.commit()
    return conn


def _contagens(conn):
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t, _ in cards_prune.TABELAS}


def _orfaos(conn):
    a = conn.execute("SELECT COUNT(*) FROM fsrs_cards fc LEFT JOIN flashcards f ON f.id=fc.card_id "
                     "WHERE f.id IS NULL").fetchone()[0]
    b = conn.execute("SELECT COUNT(*) FROM fsrs_revlog r LEFT JOIN fsrs_cards fc ON fc.card_id=r.card_id "
                     "WHERE fc.card_id IS NULL").fetchone()[0]
    c = conn.execute("SELECT COUNT(*) FROM reforja_marks m LEFT JOIN flashcards f ON f.id=m.card_id "
                     "WHERE f.id IS NULL").fetchone()[0]
    return a + b + c


def test_criterio_seleciona_so_aposentado_sem_historico(tmp_path):
    conn = _db(tmp_path)
    assert cards_prune.selecionar(conn, "aposentados-sem-historico") == [1]


def test_ids_explicitos_ignoram_inexistentes(tmp_path):
    conn = _db(tmp_path)
    assert cards_prune.selecionar(conn, ids=[4, 999]) == [4]


def test_dry_run_nao_escreve(tmp_path):
    conn = _db(tmp_path)
    antes = _contagens(conn)
    code, alvo, caminho = cards_prune.executar(conn, "aposentados-sem-historico", apply=False,
                                               backup_fn=lambda: "stub", export_dir=tmp_path, out=lambda *_: None)
    assert code == 0 and alvo == [1] and caminho is None
    assert _contagens(conn) == antes


def test_apply_recusa_expect_errado(tmp_path):
    conn = _db(tmp_path)
    antes = _contagens(conn)
    chamadas = []
    code, _, caminho = cards_prune.executar(conn, "aposentados-sem-historico", apply=True, expect=7,
                                            backup_fn=lambda: chamadas.append(1) or "stub",
                                            export_dir=tmp_path, out=lambda *_: None)
    assert code == 2 and caminho is None
    assert chamadas == [], "recusa por --expect nao pode nem rodar o backup"
    assert _contagens(conn) == antes


def test_apply_remove_exatamente_n_com_export_e_backup(tmp_path):
    conn = _db(tmp_path)
    antes = _contagens(conn)
    chamadas = []
    code, alvo, caminho = cards_prune.executar(conn, "aposentados-sem-historico", apply=True, expect=1,
                                               backup_fn=lambda: chamadas.append(1) or "stub",
                                               export_dir=tmp_path, out=lambda *_: None)
    assert code == 0 and alvo == [1]
    assert chamadas == [1], "backup roda exatamente uma vez antes de apagar"
    depois = _contagens(conn)
    assert depois["flashcards"] == antes["flashcards"] - 1
    assert depois["fsrs_cards"] == antes["fsrs_cards"] - 1
    assert depois["fsrs_revlog"] == antes["fsrs_revlog"]      # o alvo nao tinha revlog
    assert depois["reforja_marks"] == antes["reforja_marks"]  # nem marca
    assert conn.execute("SELECT COUNT(*) FROM flashcards WHERE id=1").fetchone()[0] == 0
    # os que ficam, ficam inteiros
    assert [r[0] for r in conn.execute("SELECT id FROM flashcards ORDER BY id")] == [2, 3, 4]
    assert _orfaos(conn) == 0
    # export: N entradas, linhas do alvo presentes
    snap = json.loads(Path(caminho).read_text(encoding="utf-8"))
    assert snap["n"] == 1 and snap["ids"] == [1]
    assert [r["id"] for r in snap["linhas"]["flashcards"]] == [1]
    assert [r["card_id"] for r in snap["linhas"]["fsrs_cards"]] == [1]


def test_apply_por_ids_apaga_historico_junto(tmp_path):
    """Lote triado a mao pode incluir card COM revlog: as 4 tabelas vao juntas, zero orfao."""
    conn = _db(tmp_path)
    code, _, caminho = cards_prune.executar(conn, ids=[2], apply=True, expect=1,
                                            backup_fn=lambda: "stub", export_dir=tmp_path, out=lambda *_: None)
    assert code == 0
    assert conn.execute("SELECT COUNT(*) FROM fsrs_revlog WHERE card_id=2").fetchone()[0] == 0
    assert _orfaos(conn) == 0
    snap = json.loads(Path(caminho).read_text(encoding="utf-8"))
    assert len(snap["linhas"]["fsrs_revlog"]) == 1
