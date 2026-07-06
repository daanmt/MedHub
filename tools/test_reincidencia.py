"""test_reincidencia.py -- testes da part-3 (pre-bloco + detector F25).

Positivo = caso REAL da s109 (Q4/Q8/Q11 reincidiram no elo do card 730 em horas).
Inserts em db temp via monkeypatch de DB_PATH; smoke do --pre-bloco por subprocess
(read-only sobre o db real). Pytest-nativo + standalone.
"""
import contextlib
import io
import json
import os
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    # seed: tema Apendicite + card 730 (o elo real da s109), sem questao vinculada
    con.execute("INSERT INTO taxonomia_cronograma (id, area, tema) VALUES "
                "(1, 'Cirurgia', 'Apendicite Aguda')")
    con.execute("INSERT INTO flashcards (id, questao_id, tema_id, tipo, frente_pergunta, "
                "verso_resposta, verso_regra_mestre) VALUES (730, NULL, 1, 'elo_quebrado', "
                "'No caso classico de apendicite em jovem, <48h, qual a conduta?', "
                "'OPERAR direto - nao pedir imagem', "
                "'Quadro classico jovem com menos de 48h de evolucao = operar; "
                "US/TC so em duvida diagnostica, idoso ou suspeita de complicacao')")
    con.commit()
    con.close()
    return path


def _insert_q4(**overrides):
    kwargs = dict(
        area="Cirurgia", tema="Apendicite Aguda",
        enunciado="Jovem 22a, dor migratoria FID, 36h de evolucao, quadro classico.",
        correta="Apendicectomia", chamada="Solicitar US de abdome",
        erro="Reflexo de confirmacao",
        elo="no quadro classico jovem com menos de 48h pediu US imagem em vez de operar direto",
        armadilha="Ruido urinario induz a pedir exame",
        faltou="operar sem imagem no quadro classico",
    )
    kwargs.update(overrides)
    return iq.insert_questao(**kwargs)


def test_reincidencia_caso_real_s109():
    tmp = _db_temp()
    orig = iq.DB_PATH
    iq.DB_PATH = tmp
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = _insert_q4()
        texto = out.getvalue()
        assert ok is True, "insert passa normalmente"
        assert "[REINCIDENCIA]" in texto, f"flag emitida (got: {texto!r})"
        assert "card 730" in texto, f"aponta o card real (got: {texto!r})"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)


def test_reincidencia_negativo_nao_dispara():
    tmp = _db_temp()
    orig = iq.DB_PATH
    iq.DB_PATH = tmp
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ok = _insert_q4(
                elo="dose de vancomicina na sepse grave exige ajuste pela funcao renal",
                faltou="farmacologia de antibioticos",
                enunciado="Sepse grave em UTI.", correta="Vancomicina ajustada",
                chamada="Dose plena", erro="Conceitual",
                armadilha="Esquecer o ajuste renal")
        texto = out.getvalue()
        assert ok is True
        assert "[REINCIDENCIA]" not in texto, f"elo sem relacao nao dispara (got: {texto!r})"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)


def test_matcher_nunca_bloqueia():
    # mesmo com hit, o insert retorna True e o exit path e o normal
    tmp = _db_temp()
    orig = iq.DB_PATH
    iq.DB_PATH = tmp
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            assert _insert_q4() is True
            # segunda insercao identica: agora ha erro + cards previos -> mais hits
            assert _insert_q4() is True, "reincidencia multipla continua nao-bloqueante"
    finally:
        iq.DB_PATH = orig
        os.remove(tmp)


def test_tokens_normaliza():
    t = iq._tokens("No caso CLASSICO, de paciente jovem: <48h — operar!")
    assert "classico" in t and "jovem" in t and "operar" in t
    assert "caso" not in t and "paciente" not in t, "stopwords minimas fora"
    assert not any(len(x) < 4 for x in t), "tokens curtos fora"


def test_pre_bloco_cli():
    # smoke read-only contra o repo real: JSON valido; lista => bucket='pre-bloco'
    res = subprocess.run(
        [sys.executable, os.path.join("tools", "fsrs_queue.py"),
         "--pre-bloco", "Apendicite", "--janela-horas", "96"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert res.returncode == 0, f"CLI falhou: {res.stderr[-500:]}"
    data = json.loads(res.stdout)
    if isinstance(data, list):
        assert data and all(c.get("bucket") == "pre-bloco" for c in data)
    else:
        assert data.get("empty") is True and data.get("pre_bloco")


def test_list_sem_flag_regressao():
    res = subprocess.run(
        [sys.executable, os.path.join("tools", "fsrs_queue.py"), "--list", "--limit", "2"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert res.returncode == 0, f"--list regrediu: {res.stderr[-500:]}"
    data = json.loads(res.stdout)
    assert isinstance(data, list), "fila sem flags novas segue emitindo array JSON"


if __name__ == "__main__":
    fns = [test_reincidencia_caso_real_s109, test_reincidencia_negativo_nao_dispara,
           test_matcher_nunca_bloqueia, test_tokens_normaliza,
           test_pre_bloco_cli, test_list_sem_flag_regressao]
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
    print("TODOS OS TESTES PASSARAM (part-3)")
