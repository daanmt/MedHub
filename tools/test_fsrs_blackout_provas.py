"""Regressao F71 (hotfix 2026-09-09, sessao de engenharia s174): o balanceador de carga
do FSRS tem de conhecer o calendario de provas.

Caso real (s166): #381 e #823 tinham `due` no dia do ENAMED (pico) e o balanceador os
empurrou para o dia SEGUINTE a prova -- o primeiro dia em que a revisao ja nao serve.
Regra acordada com o /ai-eng (D71, 09/09): (i) blackout lido de `core/provas.json`, nunca
data no codigo; (ii) card deslocado pelo blackout vai para ANTES da prova, nunca depois;
sem vaga antes = fica no alvo e vira OVERFLOW reportado, nao empurrado em silencio.

Fixtures 100% sinteticas: datas fake, `provas.json` em tmp_path, banco em tmp. O `ipub.db`
real nunca e tocado. Dados do caso real entram MINIMIZADOS: mantem-se a propriedade que
dispara o defeito (pico no dia da prova, dia seguinte mais vazio); ids e conteudo clinico
foram retirados.
"""
import contextlib
import io
import json
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.utils import db  # noqa: E402
from app.utils import fsrs_balance as fb  # noqa: E402
from app.utils.fsrs_balance import escolher_dia  # noqa: E402

HOJE = date(2026, 1, 10)            # data sintetica de referencia
PROVA = date(2026, 1, 20)           # prova sintetica (dia +10)
D = lambda k: PROVA + timedelta(days=k)   # noqa: E731  -- dia relativo a prova


# --------------------------------------------------------------------------
# Regra pura (fsrs_balance)
# --------------------------------------------------------------------------

def test_blackout_de_cobre_prova_e_dia_seguinte():
    """(i)+(ii): o blackout de uma prova e o dia dela e o seguinte; 'grade' nao entra."""
    assert fb.blackout_de([PROVA]) == {PROVA, D(1)}
    assert fb.blackout_de([]) == set()


def test_caso_real_pico_na_prova_vai_para_antes_e_nunca_depois():
    """Caso #381/#823 minimizado: alvo = dia da prova (pico), dia seguinte mais vazio.

    Sem o fix, 'menor carga' escolhe o dia seguinte a prova. Com o fix, o card vai para
    ANTES da prova mesmo que la haja MAIS carga que depois."""
    carga = {D(-1): 25, D(0): 24, D(1): 19}
    dia, desloc = escolher_dia(D(0), 8, carga, HOJE, dias_evitar={D(0), D(1)})
    assert dia == D(-1), f"esperado dia anterior a prova {D(-1)}, veio {dia}"
    assert desloc == -1


def test_alvo_no_dia_seguinte_a_prova_tambem_volta_para_antes():
    """Alvo = prova+1 com folga 2: os candidatos {+1, 0, +2, -1, +3}; 0 e +1 sao blackout,
    +2/+3 estao DEPOIS -> tem de ir para -1 (unico candidato antes da prova)."""
    carga = {D(-1): 40, D(2): 0, D(3): 0}
    dia, _ = escolher_dia(D(1), 40, carga, HOJE, dias_evitar={D(0), D(1)})
    assert dia == D(-1), f"veio {dia}"


def test_sem_vaga_antes_da_prova_fica_no_alvo_overflow():
    """Alvo = prova+1 com folga 1: candidatos {+1, 0, +2}; nenhum e anterior a prova.
    Regra do /ai-eng: NAO empurrar para depois em silencio -> fica no alvo (desloc 0).
    O caller detecta o overflow por `dia in dias_evitar`."""
    carga = {D(1): 30, D(0): 30, D(2): 0}
    dia, desloc = escolher_dia(D(1), 8, carga, HOJE, dias_evitar={D(0), D(1)})
    assert (dia, desloc) == (D(1), 0), f"veio {(dia, desloc)}"
    assert dia in {D(0), D(1)}     # e assim que o caller reconhece o overflow


def test_alvo_antes_da_prova_nunca_cruza_para_depois():
    """Alvo = prova-1, folga 3 (intervalo 60): a janela alcanca +2 (depois da prova), que
    esta vazio. Cruzar a prova nao e folga: o balanceador fica do lado de ca."""
    carga = {D(-1): 30, D(-2): 20, D(-3): 20, D(-4): 25, D(2): 0}
    dia, _ = escolher_dia(D(-1), 60, carga, HOJE, dias_evitar={D(0), D(1)})
    assert dia < PROVA, f"cruzou a prova: {dia}"
    assert dia in (D(-2), D(-3))


def test_nunca_pousa_em_dia_de_blackout():
    """Alvo = prova-1, folga 1: candidatos {-1, -2, 0}; 0 e o mais vazio mas e a prova."""
    carga = {D(-1): 30, D(-2): 30, D(0): 0}
    dia, _ = escolher_dia(D(-1), 10, carga, HOJE, dias_evitar={D(0), D(1)})
    assert dia != D(0)


def test_sem_blackout_comportamento_identico_ao_anterior():
    """Preservacao: `dias_evitar=None` == regra do s128 (menor carga, empate no alvo)."""
    carga = {D(0): 50, D(-1): 3, D(1): 40}
    assert escolher_dia(D(0), 10, carga, HOJE) == (D(-1), -1)
    assert escolher_dia(D(0), 10, carga, HOJE, dias_evitar=set()) == (D(-1), -1)
    plana = {D(0): 5, D(-1): 5, D(1): 5}
    assert escolher_dia(D(0), 10, plana, HOJE, dias_evitar={D(5)}) == (D(0), 0)


def test_nenhuma_data_de_prova_no_codigo():
    """(i) G4: o blackout vem de core/provas.json; nenhuma data de prova REAL vive no
    codigo (regra pura nem caller). Le o arquivo real so para saber o que procurar."""
    real = Path(db.PROVAS_PATH)
    if not real.exists():
        pytest.skip("core/provas.json ausente neste checkout")
    datas = [str(i.get("data")) for i in json.loads(real.read_text(encoding="utf-8"))
             if isinstance(i, dict) and i.get("data")]
    assert datas, "provas.json real sem datas -- o guarda nao teria o que procurar"
    for mod in (fb, db):
        fonte = Path(mod.__file__).read_text(encoding="utf-8")
        for d in datas:
            assert d not in fonte, f"data de prova {d} hardcoded em {mod.__name__}"


# --------------------------------------------------------------------------
# Caller (db._balancear_due) le core/provas.json
# --------------------------------------------------------------------------

_DDL = """
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT, questao_id INTEGER, tema_id INTEGER,
    tipo TEXT, frente_contexto TEXT, frente_pergunta TEXT, verso_resposta TEXT,
    verso_regra_mestre TEXT, verso_armadilha TEXT, quality_source TEXT DEFAULT 'legacy',
    card_version INTEGER DEFAULT 1, needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (
    card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0, due DATETIME,
    stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0, elapsed_days INTEGER DEFAULT 0,
    scheduled_days INTEGER DEFAULT 0, reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0,
    last_review DATETIME);
"""


def _db_com_carga(tmp_path, carga):
    """Banco temporario com `carga[dia]` cards de revisao agendados em cada dia."""
    path = tmp_path / "fsrs.db"
    con = sqlite3.connect(path)
    con.executescript(_DDL)
    i = 1
    for dia, n in carga.items():
        for _ in range(n):
            con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta, "
                        "quality_source) VALUES (?, 'conteudo', 'P?', 'R.', 'qualitative')", (i,))
            con.execute("INSERT INTO fsrs_cards (card_id, state, due, scheduled_days) "
                        "VALUES (?, 2, ?, 30)", (i, datetime.combine(dia, datetime.min.time())))
            i += 1
    con.commit()
    return con


def _provas(tmp_path, itens):
    p = tmp_path / "provas.json"
    p.write_text(json.dumps(itens), encoding="utf-8")
    return str(p)


def _capturar(fn):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        r = fn()
    return r, out.getvalue(), err.getvalue()


def test_blackout_provas_le_o_arquivo_e_ignora_tipo_grade(tmp_path):
    p = _provas(tmp_path, [
        {"nome": "PROVA-X", "data": PROVA.isoformat(), "tipo": "prova"},
        {"nome": "fim-grade", "data": D(30).isoformat(), "tipo": "grade"},
        {"nome": "quebrado", "data": "nao-e-data", "tipo": "prova"},
    ])
    assert db.blackout_provas(p) == {PROVA, D(1)}


def test_blackout_provas_tolerante_a_arquivo_ausente(tmp_path):
    _, out, err = _capturar(lambda: db.blackout_provas(str(tmp_path / "nao-existe.json")))
    assert db.blackout_provas(str(tmp_path / "nao-existe.json")) == set()
    assert out == ""            # contrato JSON do fsrs_queue --record


def test_balancear_due_le_provas_json_e_evita_o_dia_seguinte(tmp_path, monkeypatch):
    """Integracao: o caller deriva o blackout do arquivo e o card do dia da prova vai
    para o dia ANTERIOR, embora o seguinte esteja mais vazio."""
    monkeypatch.setattr(db, "PROVAS_PATH", _provas(tmp_path, [
        {"nome": "PROVA-X", "data": PROVA.isoformat(), "tipo": "prova"}]))
    con = _db_com_carga(tmp_path, {D(-1): 6, D(0): 8, D(1): 1})
    metrics = {"due": datetime.combine(D(0), datetime.min.time()),
               "scheduled_days": 8, "state": 2}
    novo, out, err = _capturar(lambda: db._balancear_due(con.cursor(), metrics, hoje=HOJE))
    con.close()
    assert novo["due"].date() == D(-1), f"veio {novo['due']}"
    assert novo["scheduled_days"] == 7
    assert out == ""


def test_balancear_due_overflow_mantem_alvo_e_reporta(tmp_path, monkeypatch):
    """Sem vaga antes da prova na folga: due fica no alvo e stderr carrega OVERFLOW."""
    monkeypatch.setattr(db, "PROVAS_PATH", _provas(tmp_path, [
        {"nome": "PROVA-X", "data": PROVA.isoformat(), "tipo": "prova"}]))
    con = _db_com_carga(tmp_path, {D(0): 5, D(1): 5, D(2): 0})
    metrics = {"due": datetime.combine(D(1), datetime.min.time()),
               "scheduled_days": 8, "state": 2}
    novo, out, err = _capturar(lambda: db._balancear_due(con.cursor(), metrics, hoje=HOJE))
    con.close()
    assert novo["due"].date() == D(1), f"empurrou em silencio: {novo['due']}"
    assert "OVERFLOW" in err, f"overflow nao reportado; stderr={err!r}"
    assert out == ""


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


# --------------------------------------------------------------------------
# Re-rodada sobre a fila existente (iii do veredito): dry-run + COUNT-ASSERT (§10.7)
# --------------------------------------------------------------------------

def _due_de(con, card_id):
    return con.execute("SELECT due, scheduled_days, stability FROM fsrs_cards "
                       "WHERE card_id = ?", (card_id,)).fetchone()


def test_rebalancear_dry_run_declara_diff_e_nao_escreve(tmp_path):
    """3 cards no dia da prova (folga 1), 1 no dia seguinte sem vaga antes (overflow),
    1 fora do blackout (intocado). Dry-run: diff declarado por (de -> para), COUNT bate,
    banco identico antes e depois."""
    con = _db_com_carga(tmp_path, {D(-1): 2, D(0): 3, D(1): 1, D(5): 1})
    # cards 3,4,5 = dia da prova (intervalo 30 -> folga 2 alcanca -1 e -2); card 6 = dia
    # seguinte com intervalo curto de 8 (folga 1: candidatos {+1, 0, +2} -> overflow)
    con.execute("UPDATE fsrs_cards SET scheduled_days = 8 WHERE card_id = 6")
    con.commit()
    antes = {i: _due_de(con, i) for i in range(1, 8)}
    r = db.rebalancear_blackout(con, hoje=HOJE, dias_evitar={D(0), D(1)}, aplicar=False)
    assert r["aplicado"] is False
    assert len(r["movidos"]) == 3 and {m["card_id"] for m in r["movidos"]} == {3, 4, 5}
    assert all(m["para"] < PROVA for m in r["movidos"])
    assert [o["card_id"] for o in r["overflow"]] == [6]
    assert sum(r["resumo"].values()) == 3            # COUNT declarado
    assert {i: _due_de(con, i) for i in range(1, 8)} == antes, "dry-run escreveu"
    con.close()


def test_rebalancear_apply_escreve_exatamente_o_count_declarado(tmp_path):
    con = _db_com_carga(tmp_path, {D(-1): 2, D(0): 3, D(1): 1, D(5): 1})
    con.execute("UPDATE fsrs_cards SET scheduled_days = 8, stability = 7.5 WHERE card_id = 6")
    con.execute("UPDATE fsrs_cards SET stability = 12.25 WHERE card_id = 3")
    con.commit()
    dry = db.rebalancear_blackout(con, hoje=HOJE, dias_evitar={D(0), D(1)}, aplicar=False)
    r = db.rebalancear_blackout(con, hoje=HOJE, dias_evitar={D(0), D(1)}, aplicar=True)
    assert r["aplicado"] is True
    assert r["escritos"] == len(dry["movidos"]) == 3    # COUNT-ASSERT
    for m in r["movidos"]:
        due, sd, _ = _due_de(con, m["card_id"])
        assert datetime.fromisoformat(str(due)).date() == m["para"]
        assert sd == 30 + m["deslocamento"]
    assert _due_de(con, 3)[2] == 12.25, "stability tem de ficar intocada"
    assert datetime.fromisoformat(str(_due_de(con, 6)[0])).date() == D(1), "overflow movido"
    assert datetime.fromisoformat(str(_due_de(con, 7)[0])).date() == D(5), "fora do blackout tocado"
    # 2a rodada: nada resta a mover alem do overflow -- idempotente
    r2 = db.rebalancear_blackout(con, hoje=HOJE, dias_evitar={D(0), D(1)}, aplicar=True)
    assert r2["movidos"] == [] and r2["escritos"] == 0
    con.close()


def test_rebalancear_sem_blackout_nao_toca_nada(tmp_path):
    con = _db_com_carga(tmp_path, {D(0): 3})
    r = db.rebalancear_blackout(con, hoje=HOJE, dias_evitar=set(), aplicar=True)
    assert r["movidos"] == [] and r["escritos"] == 0
    con.close()
