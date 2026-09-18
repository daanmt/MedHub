"""test_preparacao.py -- testes da part-1 (PRD orquestracao-preparacao).

Cobre: posicao SSOT (roundtrip db), registro acumulativo (F22, delta-only na
taxonomia) e invariante POSICAO_DRIFT.

⚰️ **Os dois testes do resolver de semana de conteudo sairam em 17/09/2026**
(plano-ssot-e-cards-v2 Parte 4): `day_plan._resolver_semana_conteudo` e
`_semana_conteudo` foram REMOVIDOS junto do ramo calendario -- o boot nao le mais
a posicao nem do `preparacao_estado` nem do texto do HANDOFF/ESTADO. A chave
`semana_conteudo` sobrevive com UM leitor vivo (`tools/cobertura_conhecimento.py`),
e por isso o roundtrip do db continua testado aqui. O POSICAO_DRIFT passou a
comparar o HANDOFF com `plano_tarefas`.

Pytest-nativo (coletado direto pela raiz, precedente test_autonomia_hooks);
standalone: python tools/test_preparacao.py. Todos os writes em db/arquivos
TEMPORARIOS -- o ipub.db real nunca e tocado.
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

import app.utils.db as db            # noqa: E402
import auto_check as ac              # noqa: E402
import registrar_sessao_bulk as rsb  # noqa: E402


def _tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return path


def test_posicao_roundtrip():
    tmp = _tmp_db()
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        assert db.get_semana_conteudo() is None, "db vazio deve retornar None"
        db.set_preparacao("semana_conteudo", 12, fonte="teste")
        assert db.get_semana_conteudo() == 12, "roundtrip set->get"
        item = db.get_preparacao("semana_conteudo")
        assert item["fonte"] == "teste" and item["atualizado_em"], "metadados gravados"
        db.set_preparacao("semana_conteudo", 13, fonte="teste2")
        assert db.get_semana_conteudo() == 13, "upsert atualiza"
        # leitura por conexao nova (simula processo novo: nada em memoria)
        con = sqlite3.connect(tmp)
        raw = con.execute(
            "SELECT valor FROM preparacao_estado WHERE chave='semana_conteudo'").fetchone()
        con.close()
        assert raw and int(raw[0]) == 13, "posicao persiste no arquivo"
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def test_acumular_f22():
    tmp = _tmp_db()
    con = sqlite3.connect(tmp)
    con.execute("""
        CREATE TABLE taxonomia_cronograma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT, tema TEXT,
            questoes_realizadas INTEGER DEFAULT 0,
            questoes_acertadas  INTEGER DEFAULT 0,
            percentual_acertos  REAL DEFAULT 0,
            ultima_revisao TEXT
        )
    """)
    con.commit()
    con.close()
    orig = rsb.DB_PATH
    rsb.DB_PATH = tmp
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok1 = rsb.registrar(109, "Cirurgia", 18, 13)
            ok2 = rsb.registrar(109, "Cirurgia", 42, 31)                  # sem flag: recusa
            ok3 = rsb.registrar(109, "Cirurgia", 42, 31, acumular=True)   # F22: soma
        assert ok1 is True and ok3 is True, "1o bloco e acumulo devem passar"
        assert ok2 is False, "sem --acumular a guarda anti-duplo permanece"
        assert "[AVISO]" in out.getvalue(), "aviso anti-duplo preservado"
        con = sqlite3.connect(tmp)
        rows = con.execute(
            "SELECT questoes_feitas, questoes_acertadas FROM sessoes_bulk "
            "WHERE sessao_num=109 AND area='Cirurgia'").fetchall()
        tax = con.execute(
            "SELECT questoes_realizadas, questoes_acertadas FROM taxonomia_cronograma "
            "WHERE area='Cirurgia'").fetchone()
        con.close()
        assert len(rows) == 1, f"1 linha por (sessao, area) (got {len(rows)})"
        assert rows[0] == (60, 44), f"bulk somado 18+42/13+31 (got {rows[0]})"
        assert tax == (60, 44), f"taxonomia delta-only, sem dupla contagem (got {tax})"
    finally:
        rsb.DB_PATH = orig
        os.remove(tmp)


def test_registrar_semana_no_ato():
    tmp = _tmp_db()
    con = sqlite3.connect(tmp)
    con.execute("CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0, "
                "questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0, "
                "ultima_revisao TEXT)")
    con.commit()
    con.close()
    orig = rsb.DB_PATH
    rsb.DB_PATH = tmp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rsb.registrar(110, "Pediatria", 20, 15, semana=13)
        con = sqlite3.connect(tmp)
        row = con.execute(
            "SELECT valor, fonte FROM preparacao_estado WHERE chave='semana_conteudo'").fetchone()
        con.close()
        assert row and int(row[0]) == 13, f"--semana grava posicao (got {row})"
        assert row[1] == "registro-volume", "fonte do registro no ato"
    finally:
        rsb.DB_PATH = orig
        os.remove(tmp)


def _handoff_tmp(texto):
    fd, path = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(texto)
    return path


def _db_com_plano(linhas):
    """db temporario com `plano_tarefas` minimo: linhas = [(semana, status), ...]."""
    tmp = _tmp_db()
    con = sqlite3.connect(tmp)
    con.execute("CREATE TABLE plano_tarefas (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "semana_plano INTEGER, status TEXT NOT NULL DEFAULT 'pendente')")
    con.executemany("INSERT INTO plano_tarefas (semana_plano, status) VALUES (?, ?)", linhas)
    con.commit()
    con.close()
    return tmp


def test_posicao_drift():
    """POSICAO_DRIFT compara o HANDOFF com `plano_tarefas` (Parte 4), nao mais com
    `preparacao_estado.semana_conteudo` -- a fonte que deixou de governar o boot."""
    # semana corrente do plano = 3 (menor semana_plano PENDENTE; a 2 ja fechou)
    tmp = _db_com_plano([(2, "feita"), (3, "pendente"), (4, "pendente"), (3, "feita")])
    divergente = _handoff_tmp(
        "*Atualizado: 2026-09-17 -- s184 fechada*\n"
        "## > Proximo passo imediato -- s185\n"
        "- **Posicao:** plano semana 4 (fase 1) · 0/6 tarefas da semana feitas "
        "[derivado: plano_tarefas]\n"
        "- corpo em prosa cita S99 fora de ancora e sessao s108\n")
    coerente = _handoff_tmp(
        "*Atualizado: 2026-09-17 -- s184 fechada*\n"
        "- **Posicao:** plano semana 3 (fase 1) · 1/2 tarefas da semana feitas "
        "[derivado: plano_tarefas]\n")
    sem_mencao = _handoff_tmp("*Atualizado: 2026-09-17*\ncorpo sem semana\n")
    try:
        drift = ac.check_posicao_drift(handoff_path=divergente, db_path=tmp)
        assert drift == (4, 3), f"drift detectado (got {drift})"
        assert ac.check_posicao_drift(handoff_path=coerente, db_path=tmp) is None, \
            "coerente = silencio"
        assert ac.check_posicao_drift(handoff_path=sem_mencao, db_path=tmp) is None, \
            "sem mencao de semana = silencio"
        # 🔴 tabela AUSENTE = silencio (nunca falso-positivo -- F1/POSICAO/B1)
        vazio = _tmp_db()
        try:
            assert ac.check_posicao_drift(handoff_path=divergente, db_path=vazio) is None
        finally:
            os.remove(vazio)
        # 🔴 tabela VAZIA e plano 100% fechado = silencio pelo mesmo motivo
        for linhas in ([], [(3, "feita"), (4, "cortada")]):
            outro = _db_com_plano(linhas)
            try:
                assert ac.check_posicao_drift(handoff_path=divergente, db_path=outro) is None, \
                    f"plano sem pendencia nao pode acusar drift (linhas={linhas})"
            finally:
                os.remove(outro)
    finally:
        for p in (divergente, coerente, sem_mencao):
            os.remove(p)
        os.remove(tmp)


if __name__ == "__main__":
    fns = [test_posicao_roundtrip, test_resolver_fonte_db, test_resolver_fonte_texto_warn,
           test_acumular_f22, test_registrar_semana_no_ato, test_posicao_drift]
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
    print("TODOS OS TESTES PASSARAM (part-1)")
