"""test_audit_card_atomicity.py — suíte própria do detector de atomicidade (part-5).

O detector está no harness automático (check 9) desde s128 SEM suíte — os
falsos-positivos do docstring (cópula, 'entre X e Y') eram validados só
manualmente. Um caso por regra ativa + um por guarda de precisão + fixture de
db p/ run_checks. Pytest-nativo + standalone.
"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import audit_card_atomicity as aca  # noqa: E402


# --- checar_front: assinaturas de duplo-ask -----------------------------------

def test_front_duas_interrogacoes():
    assert aca.checar_front("Qual o criterio? E qual a conduta?") == \
        "duplo-ask/duas-interrogacoes"


def test_front_conectivo():
    assert aca.checar_front("Qual o agente etiologico e como tratar a forma grave") == \
        "duplo-ask/conectivo"


def test_front_segundo_nucleo():
    assert aca.checar_front("Qual o criterio diagnostico e a conduta inicial indicada") == \
        "duplo-ask/segundo-nucleo"


def test_front_guarda_copula_nao_dispara():
    # 'qual e a' = copula (corpus sem acento), nao 2a demanda
    assert aca.checar_front("Qual e a unica vacina contraindicada nesse cenario") is None


def test_front_guarda_entre_nao_dispara():
    # 'entre X e Y' fecha um par, nao abre 2a demanda
    assert aca.checar_front("Qual o intervalo minimo entre a transfusao e a vacina") is None


def test_front_limpo():
    assert aca.checar_front("Qual o criterio diagnostico da sindrome ficticia") is None


# --- checar_verso: resposta-multifato -----------------------------------------

def test_verso_paragrafo():
    txt = "x" * (aca.LIMITE_CHARS + 1)
    assert aca.checar_verso(txt) == "resposta-multifato/paragrafo"


def test_verso_multi_frase():
    assert aca.checar_verso("Primeira frase. Segunda frase. Terceira frase.") == \
        "resposta-multifato/multi-frase"


def test_verso_limpo():
    assert aca.checar_verso("Uma resposta curta e direta.") is None


# --- run_checks sobre fixture de db (definicao canonica de ativo) -------------

def test_run_checks_fixture_db():
    fd, tmp = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(tmp)
    con.executescript("""
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT);
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY, tema_id INTEGER,
            tipo TEXT, frente_pergunta TEXT, verso_resposta TEXT,
            needs_qualitative INTEGER DEFAULT 0);
        INSERT INTO taxonomia_cronograma VALUES (1, 'A', 'T');
        -- ativo com duplo-ask: deve aparecer
        INSERT INTO flashcards VALUES (1, 1, 'conteudo',
            'Qual o criterio? E qual a conduta?', 'R.', 0);
        -- aposentado com o MESMO defeito: NAO deve aparecer (ativo canonico)
        INSERT INTO flashcards VALUES (2, 1, 'conteudo',
            'Qual o criterio? E qual a conduta?', 'R.', 2);
        -- ativo limpo: NAO deve aparecer
        INSERT INTO flashcards VALUES (3, 1, 'conteudo',
            'Qual o criterio diagnostico da sindrome ficticia', 'Criterio Y.', 0);
    """)
    con.commit()
    con.close()
    try:
        achados = aca.run_checks(db_path=tmp)
        ids = {a["id"] for a in achados}
        assert ids == {1}, f"so o ativo defeituoso aparece (got {ids})"
    finally:
        os.remove(tmp)


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
    print("TODOS OS TESTES PASSARAM (flashcards-integridade part-5 / atomicity)")
