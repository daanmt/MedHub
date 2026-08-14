"""test_writer_gates.py — gate de qualidade nos writers restantes (part-4).

Cobre: insert_card_base e insert_card_extra recusando lote com defeito (zero
linhas) e gravando lote valido; recurate_cards rejeitando item vazio (fim do
no-op disfarcado: card_version NAO incrementa) e item reprovado no gate.
Tudo em db temp. Pytest-nativo + standalone.
"""
import contextlib
import importlib
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

_DDL = """
CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0,
    questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0,
    ultima_revisao TEXT);
CREATE TABLE questoes_erros (id INTEGER PRIMARY KEY AUTOINCREMENT,
    tema_id INTEGER, titulo TEXT);
CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT,
    questao_id INTEGER, tema_id INTEGER, tipo TEXT, frente_contexto TEXT,
    frente_pergunta TEXT, verso_resposta TEXT, verso_regra_mestre TEXT,
    verso_armadilha TEXT, quality_source TEXT DEFAULT 'legacy',
    card_version INTEGER DEFAULT 1, needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER, due TIMESTAMP);
"""


def _import_writer(nome):
    """Writers antigos mexem em sys.stdout no import — protege o capture."""
    orig = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        return importlib.import_module(nome)
    finally:
        sys.stdout = orig


def _db_temp():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    con.commit()
    con.close()
    return path


def _json_temp(payload):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    return path


def _rodar(mod, argv, db_path):
    """Roda mod.main() com argv/db patchados. Retorna (exit_code, stdout)."""
    orig_argv, orig_db = sys.argv, mod.DB_PATH
    sys.argv, mod.DB_PATH = argv, db_path
    out = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(out):
            try:
                mod.main()
            except SystemExit as e:
                code = int(e.code or 0)
    finally:
        sys.argv, mod.DB_PATH = orig_argv, orig_db
    return code, out.getvalue()


def _count(db, tabela="flashcards"):
    con = sqlite3.connect(db)
    n = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    con.close()
    return n


CARD_OK = {"frente_pergunta": "Qual o criterio diagnostico da sindrome ficticia?",
           "verso_resposta": "Criterio Y maior que limiar Z."}
CARD_TEMPLATE = {"frente_pergunta": "Tema Generico: qual a conduta/criterio correto?",
                 "verso_resposta": "Resposta qualquer."}
CARD_ENCODING = {"frente_pergunta": "Qual a sequencia da via ficticia?",
                 "verso_resposta": "A → B em duas etapas."}


def test_base_gate_reprova_e_nada_grava():
    icb = _import_writer("insert_card_base")
    db, lote = _db_temp(), _json_temp([CARD_OK, CARD_TEMPLATE])
    try:
        code, out = _rodar(icb, ["insert_card_base.py", "--area", "A", "--tema", "T",
                                 "--from", lote], db)
        assert code == 1, f"gate reprovado deve sair 1 (got {code})"
        assert _count(db) == 0, "all-or-nothing: NADA gravado"
        assert "template-conduta-criterio" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_base_grava_lote_valido():
    icb = _import_writer("insert_card_base")
    db, lote = _db_temp(), _json_temp([CARD_OK])
    try:
        code, _ = _rodar(icb, ["insert_card_base.py", "--area", "A", "--tema", "T",
                               "--from", lote], db)
        assert code == 0
        assert _count(db) == 1 and _count(db, "fsrs_cards") == 1
    finally:
        os.remove(db)
        os.remove(lote)


def test_extra_gate_reprova_encoding():
    ice = _import_writer("insert_card_extra")
    db = _db_temp()
    lote = _json_temp([dict(CARD_ENCODING, questao_id=1, tema_id=1)])
    try:
        code, out = _rodar(ice, ["insert_card_extra.py", "--from", lote, "--apply"], db)
        assert code == 1 and _count(db) == 0
        assert "seta Unicode" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_extra_grava_valido():
    ice = _import_writer("insert_card_extra")
    db = _db_temp()
    con = sqlite3.connect(db)
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES (1, 'A', 'T')")
    con.execute("INSERT INTO questoes_erros (id, tema_id, titulo) VALUES (1, 1, 'caso')")
    con.commit()
    con.close()
    lote = _json_temp([dict(CARD_OK, questao_id=1, tema_id=1)])
    try:
        code, _ = _rodar(ice, ["insert_card_extra.py", "--from", lote, "--apply"], db)
        assert code == 0 and _count(db) == 1
    finally:
        os.remove(db)
        os.remove(lote)


def _db_com_card():
    db = _db_temp()
    con = sqlite3.connect(db)
    con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                "quality_source, card_version) VALUES (1, 'conteudo', 'P?', 'R.', 'heuristic', 1)")
    con.commit()
    con.close()
    return db


def _card1(db):
    con = sqlite3.connect(db)
    row = con.execute("SELECT card_version, quality_source, frente_pergunta "
                      "FROM flashcards WHERE id=1").fetchone()
    con.close()
    return row


def test_recurate_item_vazio_rejeitado_sem_noop():
    rc = _import_writer("recurate_cards")
    db, lote = _db_com_card(), _json_temp([{"card_id": 1}])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote], db)
        assert code == 1, "item vazio -> exit 1"
        assert _card1(db) == (1, "heuristic", "P?"), \
            "no-op NAO incrementa versao nem flipa quality_source"
        assert "nenhum campo valido" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_gate_rejeita_template():
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    lote = _json_temp([{"card_id": 1, "pergunta": "X: qual a conduta/criterio correto?"}])
    try:
        code, out = _rodar(rc, ["recurate_cards.py", "--from", lote], db)
        assert code == 1 and _card1(db)[0] == 1, "reprovado nao aplica"
        assert "template-conduta-criterio" in out
    finally:
        os.remove(db)
        os.remove(lote)


def test_recurate_valido_aplica():
    rc = _import_writer("recurate_cards")
    db = _db_com_card()
    lote = _json_temp([{"card_id": 1, "pergunta": "Qual o criterio da sindrome ficticia?"}])
    try:
        code, _ = _rodar(rc, ["recurate_cards.py", "--from", lote], db)
        ver, qs, fp = _card1(db)
        assert code == 0 and ver == 2 and qs == "qualitative"
        assert fp == "Qual o criterio da sindrome ficticia?"
    finally:
        os.remove(db)
        os.remove(lote)


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
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-4)")
