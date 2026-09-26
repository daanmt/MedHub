"""test_insert_questao_vinculo.py -- elo questoes -> cards (s199): o erro nasce LIGADO.

Antes, `questoes_erros` nao sabia de qual bloco veio (`sessoes_bulk`) nem de qual
resposta da aba Questoes (`emed_respostas.questao_erro_id` existia e ninguem escrevia).
Agora `insert_questao.py` aceita `--sessao ID` (id da LINHA de `sessoes_bulk`) e
`--emed LISTA_NUM` (o doc id da Bancada/hub, ex.: `t40_7`), no modo single e no lote,
dentro da MESMA transacao do erro: vinculo invalido = nada gravado.

Tudo em db temp (monkeypatch DB_PATH); o ipub.db real nunca e tocado. Pytest-nativo +
standalone.
"""
import contextlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
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

# questoes_erros SEM `sessao_bulk_id` de proposito: o ALTER idempotente e parte do contrato.
_DDL = """
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
CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, sessao_num INTEGER,
    area TEXT, questoes_feitas INTEGER, questoes_acertadas INTEGER,
    data_sessao TEXT, observacoes TEXT);
"""


def _db_temp():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    db._ensure_emed_tables(con)
    con.execute("INSERT INTO sessoes_bulk (id, sessao_num, area, questoes_feitas, "
                "questoes_acertadas, data_sessao) VALUES (7, 199, 'Obstetrícia', 33, 25, "
                "'2026-09-26')")
    for num, letra, conf, correta in ((3, "B", "solida", 0), (4, "C", "chute", 1),
                                      (5, "A", "solida", 1), (6, "D", "duvida", 0)):
        con.execute("INSERT INTO emed_respostas (lista, tarefa_id, num, letra, confianca, "
                    "correta, gabarito, respondido_em) VALUES ('t40', 40, ?, ?, ?, ?, 'A', "
                    "'2026-09-26T12:00:00Z')", (num, letra, conf, correta))
    con.commit()
    con.close()
    return path


def _kw(n=1, **overrides):
    kw = dict(area="Obstetrícia", tema="Diabetes na Gestação",
              enunciado=f"Caso {n} com detalhes suficientes.", correta="A",
              chamada="B", erro="Conceitual", elo=f"elo do caso {n} sobre rastreio",
              armadilha=f"armadilha {n}", titulo=f"Caso {n}",
              cards=[{"tipo": "conteudo",
                      "frente_pergunta": f"Qual o rastreio no caso {n}?",
                      "verso_resposta": f"Resposta {n}."}])
    kw.update(overrides)
    return kw


def _com_db(fn):
    tmp = _db_temp()
    orig_iq, orig_db = iq.DB_PATH, db.DB_PATH
    iq.DB_PATH, db.DB_PATH = tmp, tmp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return fn(tmp)
    finally:
        iq.DB_PATH, db.DB_PATH = orig_iq, orig_db
        os.remove(tmp)


def _linha(tmp, sql, args=()):
    con = sqlite3.connect(tmp)
    try:
        return con.execute(sql, args).fetchone()
    finally:
        con.close()


def _n_erros(tmp):
    return _linha(tmp, "SELECT COUNT(*) FROM questoes_erros")[0]


def _elo_emed(tmp, num):
    return _linha(tmp, "SELECT questao_erro_id FROM emed_respostas "
                       "WHERE lista = 't40' AND num = ?", (num,))[0]


# ------------------------------------------------------------------ --sessao

def test_sessao_grava_o_vinculo():
    def corpo(tmp):
        assert iq.insert_questao(**_kw(sessao=7)) is True
        assert _linha(tmp, "SELECT sessao_bulk_id FROM questoes_erros")[0] == 7
    _com_db(corpo)


def test_sem_sessao_coluna_existe_e_fica_nula():
    def corpo(tmp):
        assert iq.insert_questao(**_kw()) is True
        assert _linha(tmp, "SELECT sessao_bulk_id FROM questoes_erros")[0] is None
    _com_db(corpo)


def test_sessao_inexistente_nada_gravado():
    def corpo(tmp):
        assert iq.insert_questao(**_kw(sessao=999)) is False
        assert _n_erros(tmp) == 0
        assert _linha(tmp, "SELECT COUNT(*) FROM flashcards")[0] == 0
    _com_db(corpo)


# ------------------------------------------------------------------ --emed

def test_emed_liga_a_resposta_ao_erro():
    def corpo(tmp):
        assert iq.insert_questao(**_kw(emed="t40_3", sessao=7)) is True
        qid = _linha(tmp, "SELECT id FROM questoes_erros")[0]
        assert _elo_emed(tmp, 3) == qid
    _com_db(corpo)


def test_emed_chute_certo_aceito():
    # chute certo e `incerteza`: pode render card, entao pode ligar
    def corpo(tmp):
        assert iq.insert_questao(**_kw(emed="t40_4")) is True
        assert _elo_emed(tmp, 4) is not None
    _com_db(corpo)


def test_emed_resposta_inexistente_nada_gravado():
    def corpo(tmp):
        assert iq.insert_questao(**_kw(emed="t40_99")) is False
        assert _n_erros(tmp) == 0
    _com_db(corpo)


def test_emed_ja_ligada_recusa_o_segundo():
    def corpo(tmp):
        assert iq.insert_questao(**_kw(1, emed="t40_3")) is True
        primeiro = _elo_emed(tmp, 3)
        assert iq.insert_questao(**_kw(2, emed="t40_3")) is False
        assert _n_erros(tmp) == 1 and _elo_emed(tmp, 3) == primeiro
    _com_db(corpo)


def test_emed_certa_e_solida_nao_e_erro():
    def corpo(tmp):
        assert iq.insert_questao(**_kw(emed="t40_5")) is False
        assert _n_erros(tmp) == 0 and _elo_emed(tmp, 5) is None
    _com_db(corpo)


def test_emed_chave_malformada():
    for ruim in ("t40-3", "t40_", "_3", "t40_x", ""):
        try:
            db.emed_chave(ruim)
        except ValueError:
            continue
        raise AssertionError(f"chave {ruim!r} deveria ser recusada")
    assert db.emed_chave(" t40_3 ") == ("t40", 3)
    assert db.emed_chave("t1797_12") == ("t1797", 12)


# ------------------------------------------------------------------ lote

def _item(n, **overrides):
    k = _kw(n)
    k["marcada"] = k.pop("chamada")
    k.update(overrides)
    return k


def _lote(itens):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(itens, fh, ensure_ascii=False)
    return path


def test_lote_leva_sessao_e_emed():
    def corpo(tmp):
        lote = _lote([_item(1, sessao=7, emed="t40_3"), _item(2, sessao=7, emed="t40_6")])
        try:
            assert iq.insert_batch(lote) is True
        finally:
            os.remove(lote)
        assert _n_erros(tmp) == 2
        assert _linha(tmp, "SELECT COUNT(*) FROM questoes_erros "
                           "WHERE sessao_bulk_id = 7")[0] == 2
        assert _elo_emed(tmp, 3) is not None and _elo_emed(tmp, 6) is not None
    _com_db(corpo)


def test_lote_vinculo_ruim_no_meio_rollback_total():
    def corpo(tmp):
        lote = _lote([_item(1, emed="t40_3"), _item(2, emed="t40_99")])
        try:
            assert iq.insert_batch(lote) is False
        finally:
            os.remove(lote)
        assert _n_erros(tmp) == 0 and _elo_emed(tmp, 3) is None
    _com_db(corpo)


def test_lote_emed_malformado_recusado_antes_da_transacao():
    def corpo(tmp):
        lote = _lote([_item(1, emed="t40-3")])
        try:
            assert iq.insert_batch(lote) is False
        finally:
            os.remove(lote)
        assert _n_erros(tmp) == 0
    _com_db(corpo)


# ------------------------------------------------------------------ CLI

def test_cli_aceita_sessao_e_emed():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(d, "tools"))
        shutil.copy(os.path.join(raiz, "tools", "insert_questao.py"),
                    os.path.join(d, "tools", "insert_questao.py"))
        shutil.copytree(os.path.join(raiz, "app"), os.path.join(d, "app"),
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        os.makedirs(os.path.join(d, "core"))
        shutil.copy(os.path.join(raiz, "core", "areas.json"),
                    os.path.join(d, "core", "areas.json"))
        shutil.move(_db_temp(), os.path.join(d, "ipub.db"))
        cf = os.path.join(d, "cards.json")
        with open(cf, "w", encoding="utf-8") as fh:
            json.dump(_kw()["cards"], fh, ensure_ascii=False)
        r = subprocess.run(
            [sys.executable, "-X", "utf8", os.path.join(d, "tools", "insert_questao.py"),
             "--area", "Obstetrícia", "--tema", "Diabetes na Gestação",
             "--enunciado", "Caso valido com detalhes suficientes.",
             "--correta", "A", "--marcada", "B", "--erro", "Conceitual",
             "--elo", "elo sobre rastreio", "--armadilha", "distrator X",
             "--cards-file", cf, "--sessao", "7", "--emed", "t40_3"],
            capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stdout + r.stderr
        con = sqlite3.connect(os.path.join(d, "ipub.db"))
        try:
            qid, sid = con.execute("SELECT id, sessao_bulk_id FROM questoes_erros").fetchone()
            ligado = con.execute("SELECT questao_erro_id FROM emed_respostas "
                                 "WHERE lista='t40' AND num=3").fetchone()[0]
        finally:
            con.close()
        assert sid == 7 and ligado == qid
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
    print("TODOS OS TESTES PASSARAM (vinculo erro -> sessao/EMED)")
