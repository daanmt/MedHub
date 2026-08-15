"""test_init_db_schema.py — fusao (c) da consolidacao part-6.

`migrate_dificuldade.py` era uma migracao one-shot que adicionava 3 colunas
(`dificuldade`, `dificuldade_fonte`, `dificuldade_at`) a `taxonomia_cronograma`.
Ela ja tinha rodado no `ipub.db` vivo -- mas a `CREATE TABLE` do `init_db.py`
NUNCA foi atualizada. Consequencia: um banco recriado do zero nascia QUEBRADO
para a revisao calibrada, e ninguem descobria ate o primeiro SELECT falhar.

Este teste e a prova da absorcao: cria o schema em tmp e confere por PRAGMA
que as colunas nascem com a tabela. Alem disso, confere que o check 10
(`check_fk_orphans.checar_schema`) aprova um banco recem-criado -- a rede que
pega um db anterior a mudanca que nunca foi migrado.

Pytest-nativo + standalone.
"""
import importlib
import io
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

COLUNAS_DIFICULDADE = {"dificuldade", "dificuldade_fonte", "dificuldade_at"}


def _criar_schema_em_tmp():
    """Roda init_db() contra um caminho temporario. Devolve o path do db."""
    import init_db as mod
    importlib.reload(mod)
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)  # init_db cria do zero
    orig, orig_stdout = mod.DB_PATH, sys.stdout
    mod.DB_PATH = path
    sys.stdout = io.StringIO()          # init_db e falante; nao poluir o capture
    try:
        mod.init_db()
    finally:
        mod.DB_PATH = orig
        sys.stdout = orig_stdout
    return path


def _colunas(db, tabela):
    con = sqlite3.connect(db)
    try:
        return {r[1] for r in con.execute(f"PRAGMA table_info({tabela})")}
    finally:
        con.close()


def test_db_novo_nasce_com_colunas_dificuldade():
    db = _criar_schema_em_tmp()
    try:
        cols = _colunas(db, "taxonomia_cronograma")
        faltando = COLUNAS_DIFICULDADE - cols
        assert not faltando, (
            f"db recriado do zero nasce quebrado: colunas faltando {sorted(faltando)} "
            f"-- a fusao (c) nao absorveu o migrate_dificuldade")
    finally:
        os.remove(db)


def test_colunas_dificuldade_sao_gravaveis():
    """Coluna que existe no PRAGMA mas nao aceita escrita nao serve de nada."""
    db = _criar_schema_em_tmp()
    try:
        con = sqlite3.connect(db)
        con.execute("INSERT INTO taxonomia_cronograma (area, tema, dificuldade, "
                    "dificuldade_fonte, dificuldade_at) VALUES (?,?,?,?,?)",
                    ("Area X", "Tema Y", 7, "agente_inferida", "2026-08-14T00:00:00"))
        con.commit()
        row = con.execute("SELECT dificuldade, dificuldade_fonte FROM "
                          "taxonomia_cronograma WHERE tema='Tema Y'").fetchone()
        con.close()
        assert row == (7, "agente_inferida")
    finally:
        os.remove(db)


def test_check_10_aprova_schema_recem_criado():
    """Fusao (b) x fusao (c): o schema-check herdado do audit_integrity aprova
    um db criado pelo init_db atual (nenhum achado de schema)."""
    import check_fk_orphans as cfo
    db = _criar_schema_em_tmp()
    try:
        con = sqlite3.connect(db)
        achados = cfo.checar_schema(con)
        con.close()
        assert achados == [], f"schema recem-criado nao deveria acusar nada: {achados}"
    finally:
        os.remove(db)


def test_check_10_pega_coluna_faltando():
    """A rede funciona: db sem as colunas dificuldade* vira achado de schema
    (e o achado nomeia as colunas, para o conserto ser obvio)."""
    import check_fk_orphans as cfo
    fd, db = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        con = sqlite3.connect(db)
        con.executescript(
            "CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT);"
            "CREATE TABLE flashcards (id INTEGER PRIMARY KEY, frente_pergunta TEXT,"
            " verso_resposta TEXT, verso_regra_mestre TEXT, verso_armadilha TEXT,"
            " frente_contexto TEXT, quality_source TEXT, card_version INTEGER,"
            " needs_qualitative INTEGER);")
        con.commit()
        achados = cfo.checar_schema(con)
        con.close()
        alvos = {a["alvo"] for a in achados}
        assert "schema:taxonomia_cronograma" in alvos, achados
        assert "schema:flashcards" not in alvos, "flashcards estava completo"
        payload = [a for a in achados if a["alvo"] == "schema:taxonomia_cronograma"][0]
        assert set(payload["payload"]["colunas_faltando"]) == COLUNAS_DIFICULDADE
    finally:
        os.remove(db)


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
    print("TODOS OS TESTES PASSARAM (consolidacao part-6, fusoes b+c)")
