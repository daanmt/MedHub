"""test_cards_rendimento.py -- o card que consome revisao sem reter (s187).

O harness mede FORMA de card; nada media RENDIMENTO. Medido em 18/09/2026: **#70 tem 11
revisoes e stability de 0,67 dia** -- onze passagens compraram menos de um dia.

🔴 O corte e DERIVADO do baralho, nao importado: o limiar classico do Anki (8 lapsos)
acharia ZERO aqui, porque o maximo do baralho e 4. Ancora = `lapses >= 2` E
`stability < mediana`, com a mediana RE-MEDIDA a cada execucao.

LIMITE DECLARADO: isto NAO fecha o F87. Aquele eixo e triagem na AUTORIA, e os 13 cards
que o operador cortou nunca entraram no baralho -- nao tem reps nem stability, entao
nenhum sinal do FSRS os alcanca. Este sensor mede o eixo irmao (entre os que existem,
quais nao pagam aluguel), e dizer o contrario seria cobertura aparente.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import cards_rendimento as cr                                   # noqa: E402


def _db(tmp_path, linhas):
    """linhas = [(card_id, reps, lapses, stability, needs_qualitative)]"""
    p = tmp_path / "t.db"
    con = sqlite3.connect(p)
    con.executescript("""
        CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY, area TEXT, tema TEXT);
        CREATE TABLE flashcards (id INTEGER PRIMARY KEY, tema_id INTEGER, needs_qualitative INTEGER);
        CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, reps INTEGER, lapses INTEGER, stability REAL);
        INSERT INTO taxonomia_cronograma VALUES (1,'Gastro','Polipos');
    """)
    for cid, reps, laps, stab, nq in linhas:
        con.execute("INSERT INTO flashcards VALUES (?,1,?)", (cid, nq))
        con.execute("INSERT INTO fsrs_cards VALUES (?,?,?,?)", (cid, reps, laps, stab))
    con.commit(); con.close()
    return str(p)


def test_pega_o_card_que_consome_e_nao_retem(tmp_path):
    """O caso real: #70 com 11 reps e stability 0,67d."""
    db = _db(tmp_path, [(70, 11, 4, 0.67, 0), (1, 3, 0, 90.0, 0), (2, 3, 0, 80.0, 0)])
    cand, res = cr.medir(db)
    assert [c["card_id"] for c in cand] == [70]
    assert cand[0]["custo_por_dia"] and cand[0]["custo_por_dia"] > 10


def test_lapso_isolado_NAO_e_candidato(tmp_path):
    """`lapses >= 2` e deliberado: um tropeco nao e padrao."""
    db = _db(tmp_path, [(10, 5, 1, 1.0, 0), (1, 3, 0, 90.0, 0), (2, 3, 0, 80.0, 0)])
    cand, _ = cr.medir(db)
    assert cand == []


def test_lapsos_com_stability_ALTA_nao_e_candidato(tmp_path):
    """Card que falhou e depois consolidou esta pagando aluguel -- o eixo e a
    conjuncao, nunca o lapso sozinho."""
    db = _db(tmp_path, [(10, 8, 3, 200.0, 0), (1, 3, 0, 50.0, 0), (2, 3, 0, 40.0, 0)])
    cand, _ = cr.medir(db)
    assert cand == []


def test_aposentado_fica_de_fora(tmp_path):
    db = _db(tmp_path, [(10, 9, 4, 0.5, 2), (1, 3, 0, 90.0, 0), (2, 3, 0, 80.0, 0)])
    cand, _ = cr.medir(db)
    assert cand == []


def test_a_mediana_e_RE_MEDIDA_nao_constante(tmp_path):
    """O corte acompanha o baralho. O mesmo card e candidato num baralho maduro e
    nao e num baralho jovem -- e isso e correto, nao instabilidade."""
    alvo = (10, 6, 2, 20.0, 0)
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    maduro = _db(tmp_path / "a", [alvo, (1, 3, 0, 200.0, 0), (2, 3, 0, 300.0, 0)])
    jovem = _db(tmp_path / "b", [alvo, (1, 3, 0, 5.0, 0), (2, 3, 0, 6.0, 0)])
    assert [c["card_id"] for c in cr.medir(maduro)[0]] == [10], "mediana alta -> e candidato"
    assert cr.medir(jovem)[0] == [], "mediana baixa -> deixa de ser candidato"


def test_e_READ_ONLY(tmp_path):
    """Abre em modo ro: um sensor que escrevesse no FSRS ao medir seria o
    Invariante A por outra porta."""
    db = _db(tmp_path, [(70, 11, 4, 0.67, 0), (1, 3, 0, 90.0, 0)])
    con = sqlite3.connect(db)
    antes = con.execute("SELECT * FROM fsrs_cards ORDER BY card_id").fetchall()
    con.close()
    cr.medir(db)
    con = sqlite3.connect(db)
    depois = con.execute("SELECT * FROM fsrs_cards ORDER BY card_id").fetchall()
    con.close()
    assert antes == depois


def test_populacao_viva_tem_a_forma_esperada():
    """Re-mede o baralho real. Ratchet frouxo: o sensor nao pode zerar em silencio
    (seria sensor desligado passando por limpo) nem acusar meio baralho."""
    try:
        cand, res = cr.medir()
    except Exception as e:                                       # pragma: no cover
        print(f"  [SKIP] ipub.db indisponivel: {e}")
        return
    if not res["revisados"]:                                     # pragma: no cover
        return
    print(f"  populacao: {res['candidatos']}/{res['revisados']} ({res['pct']}%), "
          f"mediana {res['mediana_stability']}d")
    assert 0 < res["pct"] <= 20, res


def test_o_limite_do_F87_esta_declarado():
    """O ponto que impede cobertura aparente: este sensor NAO fecha o F87."""
    doc = (cr.__doc__ or "").lower()
    assert "nao fecha o f87" in doc
    assert "nunca entraram no baralho" in doc
