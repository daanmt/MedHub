"""test_evidencias_quarentena.py -- o evidence-bank aplicado no MedHub (s236, 30/10/2026).

Lei: ADR `ai-eng:artifacts/adr-banco-evidencias-clinicas-medhub-2026-10-30.md` v1.1 (Adendo 2 R2)
+ `core/contracts/evidence-governance.md` v1.5 §7; ordem de aplicação em
`ai-eng:artifacts/2026-10-30-evidence-bank-aplicacao-medhub.md` (passos 4 e 5).

Trava:
  - `db.quarentena_sql`/`db.PONTES_DDL` = cópia literal do pacote (o dono do fragmento);
  - sem `evidencias.db` pareado, "ativo" é a definição de antes (fixture, clone novo, suíte);
  - com ele, card acima do watermark sem ponte `ativa` sai da view `flashcards_ativos`, do
    `ativo_where` e do `get_fresh_error_cards` (serviço); o legado abaixo do watermark segue;
  - `insert_card_base`/`insert_questao` põem o card sem evidência em QUARENTENA + fila e não
    recusam; com `evidencias: [ev-...]` ativa, ponte `ativa` e card servido; recusa só por forma.

Tudo em tmp_path (fixture `db_sintetico` + `evidencias.db` próprio via `MEDHUB_EVIDENCIAS_DB`);
o ipub.db real nunca é tocado. Os testes que precisam do pacote pulam com motivo se o
`../evidence-bank` não estiver na máquina.
"""
import contextlib
import importlib
import io
import json
import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.utils import db  # noqa: E402
from app.utils import evidencias_ponte as ponte  # noqa: E402

AREA, TEMA = "Cirurgia", "Apendicite Aguda"   # o tema 1 que o `db_sintetico` semeia


def _pacote():
    try:
        return ponte.carregar_pacote()
    except RuntimeError as e:
        pytest.skip(f"evidence-bank ausente: {e}")


def _banco(tmp_path, monkeypatch, ipub, com_pacote=True, watermark=None):
    """Cria o `evidencias.db` do teste e o pareia (`MEDHUB_EVIDENCIAS_DB`). Com o pacote, pelo
    `init --ipub` real (watermark = max(flashcards.id) e pontes no ipub); sem ele, só a `meta`."""
    caminho = str(tmp_path / "evidencias.db")
    if com_pacote:
        _pacote().init(caminho, ipub=ipub)
    else:
        con = sqlite3.connect(caminho)
        con.execute("CREATE TABLE meta (chave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
        con.execute("INSERT INTO meta VALUES ('watermark_flashcards', ?)", (str(watermark),))
        con.commit()
        con.close()
    monkeypatch.setenv(db.EVIDENCIAS_ENV, caminho)
    return caminho


def _novo_card(ipub, pergunta, nq=0):
    con = sqlite3.connect(ipub)
    cur = con.execute("INSERT INTO flashcards (tema_id, tipo, frente_pergunta, verso_resposta, "
                      "needs_qualitative) VALUES (1, 'conteudo', ?, 'R.', ?)", (pergunta, nq))
    cid = cur.lastrowid
    con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, ?)",
                (cid, db.carimbo()))
    con.commit()
    con.close()
    return cid


def _ids_ativos():
    conn = db.get_connection()
    try:
        view = {r[0] for r in conn.execute("SELECT id FROM flashcards_ativos")}
        inline = {r[0] for r in conn.execute(
            f"SELECT f.id FROM flashcards f WHERE {db.ativo_where('f.')}")}
        sem_alias = conn.execute(
            f"SELECT COUNT(*) FROM flashcards WHERE {db.ATIVO_WHERE}").fetchone()[0]
    finally:
        conn.close()
    assert view == inline and sem_alias == len(view), (view, inline, sem_alias)
    return view


def _importar(nome):
    """Writers antigos mexem em sys.stdout no import -- protege o capture."""
    orig = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        return importlib.import_module(nome)
    finally:
        sys.stdout = orig


def _rodar_card_base(monkeypatch, ipub, tmp_path, cards, *extra):
    icb = _importar("insert_card_base")
    lote = tmp_path / "lote.json"
    lote.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(icb, "DB_PATH", ipub)
    monkeypatch.setattr(sys, "argv", ["insert_card_base.py", "--area", AREA, "--tema", TEMA,
                                      "--from", str(lote), *extra])
    out, code = io.StringIO(), 0
    with contextlib.redirect_stdout(out):
        try:
            icb.main()
        except SystemExit as e:
            code = int(e.code or 0)
    return code, out.getvalue()


def _fila(caminho):
    con = sqlite3.connect(caminho)
    try:
        return con.execute("SELECT id, origem, afirmacao, area, estado, tipo_json FROM ("
                           "SELECT id, origem, afirmacao, area, estado, "
                           "json_extract(pesquisa_json, '$.tipo') AS tipo_json FROM fila) "
                           "ORDER BY id").fetchall()
    finally:
        con.close()


def _pontes(ipub):
    con = sqlite3.connect(ipub)
    try:
        return con.execute("SELECT flashcard_id, evidencia_id, estado, fila_id FROM card_evidencia "
                           "ORDER BY flashcard_id, fila_id").fetchall()
    finally:
        con.close()


def _n(ipub, tabela):
    con = sqlite3.connect(ipub)
    try:
        return con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
    finally:
        con.close()


CARD_A = {"frente_pergunta": "Qual o criterio diagnostico da sindrome ficticia alfa?",
          "verso_resposta": "Criterio Y maior que limiar Z.",
          "verso_regra_mestre": "Limiar Z define a sindrome alfa. [Fonte: SBC 2020, Diretriz de HAS]"}
CARD_B = {"frente_pergunta": "Qual o criterio diagnostico da sindrome ficticia beta?",
          "verso_resposta": "Criterio W maior que limiar V.",
          "afirmacoes": ["Limiar V define a sindrome beta.",
                         {"afirmacao": "Limiar V vale 10 unidades.", "tipo": "cutoff"}]}


# --------------------------------------------------------------------------- definição única

def test_quarentena_sql_e_pontes_sao_copia_literal_do_pacote():
    _pacote()
    mh = importlib.import_module("adapters.medhub")
    for alias in ("", "f.", "l."):
        for wm in (None, 0, 2274):
            assert db.quarentena_sql(alias, wm) == mh.quarentena_sql(alias, wm)
    assert db.PONTES_DDL == mh.PONTES_DDL


def test_sem_banco_pareado_ativo_e_a_definicao_de_antes():
    # o conftest aponta MEDHUB_EVIDENCIAS_DB para um caminho vazio em todo teste
    assert db.watermark_flashcards() is None
    assert db.ativo_where("f.") == "COALESCE(f.needs_qualitative, 0) < 2"
    assert db.ATIVO_WHERE == "COALESCE(needs_qualitative, 0) < 2"


def test_card_acima_do_watermark_sem_ponte_ativa_nao_e_ativo(db_sintetico, tmp_path, monkeypatch):
    legado = _novo_card(db_sintetico, "Legado?")
    _banco(tmp_path, monkeypatch, db_sintetico, com_pacote=False, watermark=legado)
    sem_ponte = _novo_card(db_sintetico, "Sem ponte?")
    com_fila = _novo_card(db_sintetico, "Ponte fila?")
    com_ativa = _novo_card(db_sintetico, "Ponte ativa?")
    aposentado = _novo_card(db_sintetico, "Aposentado com ponte ativa?", nq=2)
    conn = db.get_connection()   # watermark presente: cria a card_evidencia que falta + recria a view
    try:
        db.ponte_evidencia_gravar(conn, "card", com_fila, "ev-000000000001", "fila", 7)
        db.ponte_evidencia_gravar(conn, "card", com_ativa, "ev-000000000002", "ativa")
        db.ponte_evidencia_gravar(conn, "card", aposentado, "ev-000000000003", "ativa")
        conn.commit()
        sql_view = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'flashcards_ativos'"
                                ).fetchone()[0]
    finally:
        conn.close()
    assert "card_evidencia" in sql_view, "a view foi recriada com a conjuncao de quarentena"
    assert _ids_ativos() == {legado, com_ativa}
    assert sem_ponte not in _ids_ativos() and com_fila not in _ids_ativos()


def test_get_fresh_error_cards_nao_serve_card_em_quarentena(db_sintetico, tmp_path, monkeypatch):
    _banco(tmp_path, monkeypatch, db_sintetico, com_pacote=False, watermark=0)
    cid = _novo_card(db_sintetico, "Card novo em quarentena?")
    assert cid not in {c["id"] for c in db.get_fresh_error_cards()}
    conn = db.get_connection()
    try:
        db.ponte_evidencia_gravar(conn, "card", cid, "ev-000000000009", "fila", 1)
        db.ponte_evidencia_gravar(conn, "card", cid, "ev-000000000009", "ativa")  # a decisão
        conn.commit()
    finally:
        conn.close()
    assert cid in {c["id"] for c in db.get_fresh_error_cards()}


# --------------------------------------------------------------------------- writers

def test_insert_card_base_poe_card_sem_evidencia_em_quarentena_e_nao_recusa(
        db_sintetico, tmp_path, monkeypatch):
    eb = _pacote()
    caminho = _banco(tmp_path, monkeypatch, db_sintetico)
    code, out = _rodar_card_base(monkeypatch, db_sintetico, tmp_path, [CARD_A, CARD_B])
    assert code == 0, out
    assert _n(db_sintetico, "flashcards") == 2, "nunca recusado por falta de evidencia"
    assert "2 em QUARENTENA" in out and "3 item(ns) na fila" in out
    fila = _fila(caminho)
    assert len(fila) == 3 and {f[4] for f in fila} == {"aberta"}
    assert all("[Fonte:" not in f[2] for f in fila), "o colchete sai da afirmacao"
    assert {f[5] for f in fila} == {"conduta", "cutoff"}
    pontes = _pontes(db_sintetico)
    assert len(pontes) == 3 and {p[2] for p in pontes} == {"fila"}
    # a ponte nasce com o id da evidência FUTURA: a decisão `incluir` faz o upsert fila -> ativa
    esperado = {(int(f[1].split(":")[1]), eb.evidencia_id(f[3], f[2]), f[0]) for f in fila}
    assert {(p[0], p[1], p[3]) for p in pontes} == esperado
    assert _ids_ativos() == set(), "card em quarentena nao e servido"


def test_insert_card_base_com_evidencia_ativa_liga_ponte_ativa_e_serve(
        db_sintetico, tmp_path, monkeypatch):
    eb = _pacote()
    caminho = _banco(tmp_path, monkeypatch, db_sintetico)
    afirmacao = "Limiar Z define a sindrome alfa."
    with eb.open_db(caminho) as b:
        b.add_fonte("SBC 2020 Diretriz de HAS", tier=1, origem="BR")
        b.fila_add({"agente": "operador", "itens": [{
            "afirmacao": afirmacao, "tipo": "criterio", "area": AREA, "origem": "operador",
            "fontes": [{"rotulo": "SBC 2020 Diretriz de HAS", "tier": 1, "origem": "BR",
                        "papel": "sustenta"}]}]})
        b.triar()
        b.decidir(1, "incluir", por="Teste")
    ev = eb.evidencia_id(AREA, afirmacao)
    code, out = _rodar_card_base(monkeypatch, db_sintetico, tmp_path,
                                 [dict(CARD_A, evidencias=[ev, "ev-ffffffffffff"])])
    assert code == 0, out
    assert "1 card(s) com evidencia ativa; 0 em QUARENTENA" in out
    assert "ev-ffffffffffff" in out, "evidencia inexistente vira aviso, nao ponte"
    (cid, ev_ponte, estado, fila_id), = _pontes(db_sintetico)
    assert (ev_ponte, estado, fila_id) == (ev, "ativa", None)
    assert _ids_ativos() == {cid}
    assert len(_fila(caminho)) == 1, "nada novo na fila"


def test_insert_card_base_dry_run_conta_quarentena_e_fila_sem_gravar(
        db_sintetico, tmp_path, monkeypatch):
    caminho = _banco(tmp_path, monkeypatch, db_sintetico)
    code, out = _rodar_card_base(monkeypatch, db_sintetico, tmp_path, [CARD_A, CARD_B],
                                 "--dry-run")
    assert code == 0, out
    assert "2 em QUARENTENA" in out and "3 item(ns) na fila" in out
    assert _n(db_sintetico, "flashcards") == 0 and _fila(caminho) == []


def test_lote_da_fila_com_forma_invalida_derruba_o_insert_inteiro(
        db_sintetico, tmp_path, monkeypatch):
    caminho = _banco(tmp_path, monkeypatch, db_sintetico)
    code, out = _rodar_card_base(monkeypatch, db_sintetico, tmp_path,
                                 [CARD_A, dict(CARD_B, afirmacoes=["   "])])
    assert code == 1 and "NADA gravado" in out
    assert _n(db_sintetico, "flashcards") == 0 and _fila(caminho) == []
    assert _pontes(db_sintetico) == []


def test_insert_card_extra_card_de_consolidacao_entra_em_quarentena(
        db_sintetico, tmp_path, monkeypatch):
    """O 3º writer de card (consolidação pós-simulado): mesma ponte, senão o card nasceria em
    quarentena SEM item na fila -- fora do FSRS e fora da folha, em silêncio."""
    _pacote()
    caminho = _banco(tmp_path, monkeypatch, db_sintetico)
    con = sqlite3.connect(db_sintetico)
    qid = con.execute("INSERT INTO questoes_erros (tema_id, titulo) VALUES (1, 'Erro de origem')"
                      ).lastrowid
    con.commit()
    con.close()
    ice = _importar("insert_card_extra")
    lote = tmp_path / "extra.json"
    lote.write_text(json.dumps([dict(CARD_A, tema_id=1, questao_id=qid)], ensure_ascii=False),
                    encoding="utf-8")
    monkeypatch.setattr(ice, "DB_PATH", db_sintetico)
    monkeypatch.setattr(sys, "argv", ["insert_card_extra.py", "--from", str(lote), "--apply"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            ice.main()
        except SystemExit as e:
            assert not e.code, out.getvalue()
    assert "1 em QUARENTENA" in out.getvalue()
    (cid, _, estado, fila_id), = _pontes(db_sintetico)
    (fid, origem, afirmacao, *_), = _fila(caminho)
    assert (estado, fila_id, origem) == ("fila", fid, f"card:{cid}")
    assert afirmacao == "Limiar Z define a sindrome alfa."
    assert cid not in _ids_ativos()


def test_insert_questao_card_sem_evidencia_entra_em_quarentena(db_sintetico, tmp_path, monkeypatch):
    _pacote()
    caminho = _banco(tmp_path, monkeypatch, db_sintetico)
    iq = _importar("insert_questao")
    monkeypatch.setattr(iq, "DB_PATH", db_sintetico)
    with contextlib.redirect_stdout(io.StringIO()) as out:
        ok = iq.insert_questao(
            area=AREA, tema=TEMA, enunciado="Caso com detalhes suficientes.",
            correta="Apendicectomia", chamada="Antibiotico isolado", erro="Conceitual",
            elo="indicacao cirurgica na apendicite", armadilha="melhora parcial com ATB",
            cards=[dict(CARD_A)])
    assert ok, out.getvalue()
    (cid, _, estado, fila_id), = _pontes(db_sintetico)
    assert estado == "fila" and fila_id is not None
    (fid, origem, *_), = _fila(caminho)
    assert (origem, fid) == (f"card:{cid}", fila_id)
    assert cid not in _ids_ativos()
    assert iq._EVIDENCIA_PENDENTE == []
