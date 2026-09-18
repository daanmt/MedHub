"""Testes do ledger de listas (spec plano-ssot-e-cards-v2-part-6).

Banco sintetico em `tmp_path` (padrao do `test_plano.py`): `db.DB_PATH` e o
`DB_PATH` do `registrar_sessao_bulk` sao monkeypatchados, o `ipub.db` real NUNCA e
tocado -- nem por leitura.

O que estes testes protegem, em ordem de dano:
  1. **o backfill nao chuta** -- os 3 desfechos existem de verdade (casa / ambigua /
     sem match) e so a inequivoca e gravada. Colar volume de uma lista na tarefa
     errada e pior do que deixar a sessao sem lista: o painel fica verde mentindo.
  2. **gate de area** -- sessao e tarefa de areas diferentes nao se vinculam, e a
     recusa acontece ANTES de o volume ser gravado no caminho do `--tarefa`.
  3. **COUNT-ASSERT** (AGENTE.md secao 10.7) -- `--expect` errado nao grava nada.
  4. **coluna nova em tabela SSOT** -- ALTER idempotente para o banco que ja existe E
     db do zero nascendo com a coluna (o Risk declarado da spec).
  5. **craftsmanship** -- `tools/listas.py` sem `sqlite3` e sem escrita propria.
"""
import ast
import importlib
import io
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import listas  # noqa: E402
import registrar_sessao_bulk as rsb  # noqa: E402


# ------------------------------------------------------------------- fixtures

def _usar_db(tmp_path, monkeypatch, com_schema=True):
    """Aponta os dois modulos de escrita para um banco novo em tmp."""
    caminho = str(tmp_path / "listas.db")
    monkeypatch.setattr(db, "DB_PATH", caminho)
    monkeypatch.setattr(rsb, "DB_PATH", caminho)
    if com_schema:
        import init_db as mod
        importlib.reload(mod)
        mod.DB_PATH = caminho
        stdout, sys.stdout = sys.stdout, io.StringIO()   # init_db e falante
        try:
            mod.init_db()
        finally:
            sys.stdout = stdout
    return caminho


TAREFAS = [
    # (fonte, ref_semana, tarefa_fonte, semana_plano, area, tema, tipo_norm, url, q)
    ("rf", 17, 1, 1, "Pediatria", "Diarreia Aguda", "revisao", "http://l/1", 22.0),
    ("rf", 17, 2, 1, "Cirurgia", "Urologia", "teoria", "http://l/2", 33.0),
    ("rf", 18, 1, 2, "Pneumo", "Pneumonias Bacterianas", "teoria", "http://l/3", 16.0),
    ("extensivo", 21, 5, 2, "Pneumo", "Pneumonias Bacterianas", "revisao", "http://l/4", 40.0),
    ("custom", 0, 1, 3, "Preventiva", "Etica Medica", "teoria", None, 20.0),
    ("rf", 19, 9, 9, "Preventiva", "Financiamento do SUS", "revisao", "http://l/5", 50.0),
]


def _semear(tarefas=None):
    linhas = []
    for fonte, ref, tf, semana, area, tema, tipo_norm, url, q in (tarefas or TAREFAS):
        linhas.append({"fonte": fonte, "ref_semana_fonte": ref, "tarefa_fonte": tf,
                       "semana_plano": semana, "ordem": tf, "area": area, "tema": tema,
                       "tipo": tipo_norm, "tipo_norm": tipo_norm, "url_lista": url,
                       "q_previstas": q, "status": "pendente"})
    return db.plano_upsert_tarefas(linhas)


def _ids_por_tema():
    return {(t["area"], t["tema"], t["tipo_norm"]): t["id"] for t in db.plano_listar()}


def _sessao(num, area, feitas, acertos, obs, data="2026-09-09", tarefa=None):
    stdout, sys.stdout = sys.stdout, io.StringIO()
    try:
        ok = rsb.registrar(num, area, feitas, acertos, data=data, obs=obs, tarefa=tarefa)
    finally:
        texto = sys.stdout.getvalue()
        sys.stdout = stdout
    return ok, texto


def _sessoes_padrao():
    """Uma sessao por desfecho do backfill:
      - Pediatria/Diarreia   -> casa (1 candidata);
      - Pneumo/Pneumonias    -> AMBIGUA (rf teoria + extensivo revisao, mesmo tema);
      - Preventiva/RAPS      -> sem match (tema que nao existe no plano);
      - Simulado             -> termometro (nao entra no casamento).
    """
    _sessao(200, "Pediatria", 41, 34, "Lista de REVISAO de Diarreia Aguda (EMED)")
    _sessao(201, "Pneumo", 16, 13, "Lista Pneumonias Bacterianas T I (EMED)")
    _sessao(202, "Preventiva", 20, 18, "Bloco RAPS na APS")
    _sessao(203, "Simulado", 100, 75, "ENAMED 2026 (prova real)")


def _colunas(caminho, tabela):
    con = sqlite3.connect(caminho)
    try:
        return {r[1] for r in con.execute(f"PRAGMA table_info({tabela})")}
    finally:
        con.close()


def _vinculos(caminho):
    con = sqlite3.connect(caminho)
    try:
        return {r[0]: r[1] for r in con.execute(
            "SELECT sessao_num, tarefa_id FROM sessoes_bulk")}
    finally:
        con.close()


# ---------------------------------------------- DoD 1: coluna + gate de area

def test_db_do_zero_nasce_com_a_coluna(tmp_path, monkeypatch):
    """O Risk declarado da spec: `sessoes_bulk` e SSOT volumetrica, e um banco
    recriado do zero tem que nascer integro (nao depender do ALTER)."""
    caminho = _usar_db(tmp_path, monkeypatch)
    assert "tarefa_id" in _colunas(caminho, "sessoes_bulk")


def test_ensure_coluna_e_idempotente(tmp_path, monkeypatch):
    """Banco ANTERIOR a esta parte (tabela sem a coluna): o ALTER roda uma vez e a
    2a chamada e no-op -- mesmo padrao de `_ensure_revlog_columns`."""
    caminho = _usar_db(tmp_path, monkeypatch, com_schema=False)
    con = sqlite3.connect(caminho)
    con.execute("CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "sessao_num INTEGER, area TEXT NOT NULL, questoes_feitas INTEGER, "
                "questoes_acertadas INTEGER, data_sessao DATE, observacoes TEXT)")
    con.commit()
    assert "tarefa_id" not in _colunas(caminho, "sessoes_bulk")
    for _ in range(2):
        db._ensure_sessoes_bulk_tarefa_id(con)
        con.commit()
    con.close()
    cols = [r[1] for r in sqlite3.connect(caminho).execute("PRAGMA table_info(sessoes_bulk)")]
    assert cols.count("tarefa_id") == 1, cols


def test_banco_legado_ganha_a_coluna_no_primeiro_vinculo(tmp_path, monkeypatch):
    """A ponte real: o `ipub.db` vivo tem `sessoes_bulk` SEM a coluna. O primeiro
    vinculo roda o ALTER e grava -- sem migracao manual e sem UPDATE direto."""
    caminho = _usar_db(tmp_path, monkeypatch, com_schema=False)
    con = sqlite3.connect(caminho)
    con.executescript(
        "CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "sessao_num INTEGER, area TEXT NOT NULL, questoes_feitas INTEGER, "
        "questoes_acertadas INTEGER, data_sessao DATE, observacoes TEXT);"
        "CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0, "
        "questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0, "
        "ultima_revisao TEXT);")
    con.commit()
    con.close()
    _semear()
    alvo = _ids_por_tema()[("Pediatria", "Diarreia Aguda", "revisao")]
    ok, _texto = _sessao(280, "Pediatria", 41, 34, "Lista Diarreia", tarefa=alvo)
    assert ok
    assert "tarefa_id" in _colunas(caminho, "sessoes_bulk")
    assert _vinculos(caminho)[280] == alvo


def test_ensure_coluna_sem_tabela_e_no_op(tmp_path, monkeypatch):
    """Tabela inexistente: quem cria `sessoes_bulk` e o writer de volume, nao este."""
    caminho = _usar_db(tmp_path, monkeypatch, com_schema=False)
    con = sqlite3.connect(caminho)
    db._ensure_sessoes_bulk_tarefa_id(con)     # nao explode
    assert con.execute("SELECT name FROM sqlite_master WHERE name='sessoes_bulk'"
                       ).fetchone() is None
    con.close()


def test_vincular_recusa_area_divergente(tmp_path, monkeypatch):
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessao(210, "Pediatria", 10, 8, "Bloco qualquer")
    alvo = _ids_por_tema()[("Cirurgia", "Urologia", "teoria")]
    sid = sqlite3.connect(caminho).execute(
        "SELECT id FROM sessoes_bulk WHERE sessao_num=210").fetchone()[0]
    try:
        db.vincular_sessao_tarefa(sid, alvo)
        assert False, "vinculo Pediatria -> Cirurgia deveria ser recusado"
    except db.VinculoAreaDivergente as e:
        assert "Pediatria" in str(e) and "Cirurgia" in str(e), str(e)
    assert _vinculos(caminho)[210] is None


def test_vincular_recusa_tarefa_sem_area(tmp_path, monkeypatch):
    """`area` NULL (o `Multi` declarado da part-2) tambem e recusada: sem area nao ha
    o que conferir, e o vinculo nasceria sem gate."""
    caminho = _usar_db(tmp_path, monkeypatch)
    db.plano_upsert_tarefas([{"fonte": "extensivo", "ref_semana_fonte": 22,
                              "tarefa_fonte": 1, "semana_plano": 2, "area": None,
                              "tema": "Radiografia do Torax", "tipo_norm": "teoria"}])
    _sessao(211, "Pediatria", 10, 8, "Radiografia do Torax")
    sid = sqlite3.connect(caminho).execute(
        "SELECT id FROM sessoes_bulk WHERE sessao_num=211").fetchone()[0]
    tid = db.plano_listar()[0]["id"]
    try:
        db.vincular_sessao_tarefa(sid, tid)
        assert False, "tarefa sem area deveria ser recusada"
    except db.VinculoAreaDivergente as e:
        assert "sem area" in str(e), str(e)


def test_vincular_recusa_ids_inexistentes(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    tid = db.plano_listar()[0]["id"]
    for args, marca in (((9999, tid), "sessao_bulk"), ((1, 999999), "plano_tarefas")):
        if marca == "plano_tarefas":
            _sessao(212, "Pediatria", 5, 5, "x")
        try:
            db.vincular_sessao_tarefa(*args)
            assert False, f"id inexistente ({marca}) deveria recusar"
        except ValueError as e:
            assert marca in str(e), str(e)


def test_vincular_devolve_o_vinculo_anterior(tmp_path, monkeypatch):
    """Re-vincular e visivel, nunca silencioso: `antes` e a trilha de auditoria."""
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessao(213, "Pneumo", 16, 13, "Pneumonias Bacterianas")
    sid = sqlite3.connect(caminho).execute(
        "SELECT id FROM sessoes_bulk WHERE sessao_num=213").fetchone()[0]
    ids = _ids_por_tema()
    a = ids[("Pneumo", "Pneumonias Bacterianas", "teoria")]
    b = ids[("Pneumo", "Pneumonias Bacterianas", "revisao")]
    assert db.vincular_sessao_tarefa(sid, a)["antes"] is None
    assert db.vincular_sessao_tarefa(sid, b)["antes"] == a


# ------------------------------------- DoD 2: --tarefa e --vincular no registrar

def test_registrar_com_tarefa_grava_o_vinculo(tmp_path, monkeypatch):
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    alvo = _ids_por_tema()[("Pediatria", "Diarreia Aguda", "revisao")]
    ok, texto = _sessao(220, "Pediatria", 41, 34, "Lista Diarreia", tarefa=alvo)
    assert ok and "Lista do plano: tarefa #%d" % alvo in texto
    assert _vinculos(caminho)[220] == alvo


def test_registrar_com_tarefa_divergente_nao_grava_NADA(tmp_path, monkeypatch):
    """Meia operacao (volume gravado + vinculo recusado) e a falha que ninguem ve:
    o gate roda antes da escrita."""
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    alvo = _ids_por_tema()[("Cirurgia", "Urologia", "teoria")]
    ok, texto = _sessao(221, "Pediatria", 41, 34, "Lista Diarreia", tarefa=alvo)
    assert ok is False and "Area divergente" in texto
    con = sqlite3.connect(caminho)
    assert con.execute("SELECT COUNT(*) FROM sessoes_bulk WHERE sessao_num=221"
                       ).fetchone()[0] == 0
    con.close()


def test_registrar_com_tarefa_inexistente_nao_grava(tmp_path, monkeypatch):
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    ok, texto = _sessao(222, "Pediatria", 41, 34, "Lista Diarreia", tarefa=999999)
    assert ok is False and "nao existe" in texto
    con = sqlite3.connect(caminho)
    assert con.execute("SELECT COUNT(*) FROM sessoes_bulk").fetchone()[0] == 0
    con.close()


def test_registrar_sem_tarefa_continua_identico(tmp_path, monkeypatch):
    """Anti-scope: `--tarefa` e opcional e SO adiciona o vinculo -- idempotencia e
    fan-out de taxonomia continuam iguais."""
    caminho = _usar_db(tmp_path, monkeypatch)
    ok1, _ = _sessao(223, "Pediatria", 41, 34, "Bloco")
    ok2, texto = _sessao(223, "Pediatria", 10, 9, "Bloco de novo")
    assert ok1 is True and ok2 is False and "ja existe" in texto
    con = sqlite3.connect(caminho)
    assert con.execute("SELECT questoes_feitas FROM sessoes_bulk WHERE sessao_num=223"
                       ).fetchone()[0] == 41
    assert con.execute("SELECT questoes_realizadas FROM taxonomia_cronograma "
                       "WHERE tema='[bulk] Pediatria'").fetchone()[0] == 41
    con.close()
    assert _vinculos(caminho)[223] is None


def test_modo_vincular_conserta_sessao_antiga(tmp_path, monkeypatch):
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessao(224, "Preventiva", 20, 20, "Etica Medica -- lista completa")
    sid = sqlite3.connect(caminho).execute(
        "SELECT id FROM sessoes_bulk WHERE sessao_num=224").fetchone()[0]
    alvo = _ids_por_tema()[("Preventiva", "Etica Medica", "teoria")]
    stdout, sys.stdout = sys.stdout, io.StringIO()
    try:
        ok = rsb.vincular(sid, alvo)
    finally:
        texto = sys.stdout.getvalue()
        sys.stdout = stdout
    assert ok and "tarefa #%d" % alvo in texto
    assert _vinculos(caminho)[224] == alvo
    assert rsb.vincular(sid, 999999) is False


# --------------------------------------------------- DoD 3: backfill sem chute

def test_casa_tema_exige_fronteira_de_palavra():
    """Funcao pura. Acento e caixa somem; substring no MEIO de palavra nao conta --
    sem isso um tema curto casaria dentro de outra palavra."""
    assert listas.casa_tema("Lista de REVISAO de Diarreia Aguda (EMED)", "Diarreia Aguda")
    assert listas.casa_tema("Disturbios Acido-Base hoje", "Distúrbios Ácido- Base")
    assert not listas.casa_tema("Bloco de Asma na infancia", "Asmatico")
    assert not listas.casa_tema("Bloco SUA (sprint)", "UA")
    assert not listas.casa_tema("", "Diarreia")
    assert not listas.casa_tema("Lista X", "")


def test_backfill_cobre_os_tres_desfechos(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessoes_padrao()
    code, r = listas.backfill()
    assert code == 0
    assert len(r["casadas"]) == 1, r["casadas"]
    assert len(r["ambiguas"]) == 1 and len(r["ambiguas"][0][1]) == 2
    assert len(r["sem_match"]) == 1
    assert len(r["termometros"]) == 1
    texto = capsys.readouterr().out
    assert "1 casadas / 1 ambiguas (2+ candidatas) / 1 sem match" in texto
    assert "DRY-RUN" in texto


def test_backfill_dry_run_nao_grava(tmp_path, monkeypatch, capsys):
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessoes_padrao()
    listas.backfill(apply=False)
    capsys.readouterr()
    assert set(_vinculos(caminho).values()) == {None}


def test_expect_errado_nao_grava(tmp_path, monkeypatch, capsys):
    """COUNT-ASSERT da AGENTE.md secao 10.7: o numero e declarado ANTES e conferido
    contra o medido na hora."""
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessoes_padrao()
    code, _ = listas.backfill(apply=True, expect=3)
    texto = capsys.readouterr().out
    assert code == 2 and "RECUSADO" in texto
    assert set(_vinculos(caminho).values()) == {None}


def test_apply_grava_so_as_inequivocas(tmp_path, monkeypatch, capsys):
    caminho = _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessoes_padrao()
    code, _ = listas.backfill(apply=True, expect=1)
    capsys.readouterr()
    assert code == 0
    vinc = _vinculos(caminho)
    esperado = _ids_por_tema()[("Pediatria", "Diarreia Aguda", "revisao")]
    assert vinc[200] == esperado
    assert vinc[201] is None and vinc[202] is None and vinc[203] is None


def test_backfill_nao_repisa_sessao_ja_vinculada(tmp_path, monkeypatch, capsys):
    """2a passada = 0 casadas (a sessao ja tem elo): o backfill so preenche NULL."""
    _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessoes_padrao()
    listas.backfill(apply=True, expect=1)
    _code, r = listas.backfill()
    capsys.readouterr()
    assert r["casadas"] == []


def test_simulado_nunca_entra_no_casamento(tmp_path, monkeypatch, capsys):
    """Risk da spec: sessao de simulado e termometro, fica NULL por regra -- e nao
    polui a lista de 'sem match', que e worklist do humano."""
    _usar_db(tmp_path, monkeypatch)
    db.plano_upsert_tarefas([{"fonte": "custom", "ref_semana_fonte": 0, "tarefa_fonte": 7,
                              "semana_plano": 1, "area": "Simulado",
                              "tema": "ENAMED 2026", "tipo_norm": "revisao"}])
    _sessao(230, "Simulado", 100, 75, "ENAMED 2026 (prova real)")
    _code, r = listas.backfill()
    capsys.readouterr()
    assert [s["sessao_num"] for s in r["termometros"]] == [230]
    assert r["casadas"] == [] and r["sem_match"] == []


# ----------------------------------------------- DoD 4: progresso e pendentes

def test_progresso_soma_so_sessoes_vinculadas(tmp_path, monkeypatch, capsys):
    """A sessao SEM vinculo nao entra em tarefa nenhuma -- e nao some: sai na linha
    de volume sem lista."""
    _usar_db(tmp_path, monkeypatch)
    _semear()
    _sessoes_padrao()
    listas.backfill(apply=True, expect=1)
    _code, p = listas.progresso()
    capsys.readouterr()
    assert [l["id"] for l in p["tarefas"]] == [
        _ids_por_tema()[("Pediatria", "Diarreia Aguda", "revisao")]]
    linha = p["tarefas"][0]
    assert (linha["feitas"], linha["acertos"], linha["pct"]) == (41, 34, 82.9)
    assert linha["url_lista"] == "http://l/1" and linha["q_previstas"] == 22.0
    assert p["blocos"]["PED"]["feitas"] == 41
    assert p["sem_vinculo"] == {"sessoes": 3, "questoes": 136}


def test_progresso_soma_duas_sessoes_na_mesma_tarefa(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    alvo = _ids_por_tema()[("Pediatria", "Diarreia Aguda", "revisao")]
    _sessao(240, "Pediatria", 20, 15, "parte 1", data="2026-09-01", tarefa=alvo)
    _sessao(241, "Pediatria", 21, 19, "parte 2", data="2026-09-02", tarefa=alvo)
    _code, p = listas.progresso()
    capsys.readouterr()
    assert (p["tarefas"][0]["feitas"], p["tarefas"][0]["acertos"]) == (41, 34)


def test_progresso_filtra_por_bloco_e_semana(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    ids = _ids_por_tema()
    _sessao(250, "Pediatria", 20, 15, "a", tarefa=ids[("Pediatria", "Diarreia Aguda",
                                                       "revisao")])
    _sessao(251, "Cirurgia", 33, 28, "b", tarefa=ids[("Cirurgia", "Urologia", "teoria")])
    _code, so_ped = listas.progresso(bloco="PED")
    _code, so_s1 = listas.progresso(semana=1)
    _code, so_s2 = listas.progresso(semana=2)
    capsys.readouterr()
    assert [l["bloco"] for l in so_ped["tarefas"]] == ["PED"]
    assert len(so_s1["tarefas"]) == 2 and so_s2["tarefas"] == []


def test_orcamento_fase1_ignora_semanas_fora_da_fase(tmp_path, monkeypatch, capsys):
    """O orcamento e da Fase 1 (semanas 1-7): volume de semana 9 nao pode abate-lo."""
    _usar_db(tmp_path, monkeypatch)
    _semear()
    ids = _ids_por_tema()
    _sessao(260, "Preventiva", 30, 25, "a", tarefa=ids[("Preventiva", "Etica Medica",
                                                        "teoria")])
    _sessao(261, "Preventiva", 50, 40, "b", data="2026-09-10",
            tarefa=ids[("Preventiva", "Financiamento do SUS", "revisao")])
    _code, p = listas.progresso()
    capsys.readouterr()
    o = p["orcamento_fase1"]
    assert o["orcamento"] == listas.ORCAMENTO_FASE1
    assert o["feitas"] == 30 and o["falta"] == listas.ORCAMENTO_FASE1 - 30


def test_pendentes_lista_previstas_sem_volume(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    ids = _ids_por_tema()
    alvo = ids[("Pediatria", "Diarreia Aguda", "revisao")]
    _sessao(270, "Pediatria", 41, 34, "a", tarefa=alvo)
    _code, p = listas.pendentes()
    capsys.readouterr()
    pend = {l["id"] for l in p["tarefas"]}
    assert alvo not in pend and len(pend) == len(TAREFAS) - 1
    assert p["blocos"]["MFC"]["tarefas"] == 2


def test_pendentes_marca_feita_sem_volume_e_ignora_cortada(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    ids = _ids_por_tema()
    db.plano_set_status(ids[("Cirurgia", "Urologia", "teoria")], "cortada",
                        origem_conclusao=db.ORIGEM_USUARIO)
    db.plano_set_status(ids[("Preventiva", "Etica Medica", "teoria")], "feita",
                        origem_conclusao=db.ORIGEM_APROXIMADA)
    _code, p = listas.pendentes()
    capsys.readouterr()
    assert ids[("Cirurgia", "Urologia", "teoria")] not in {l["id"] for l in p["tarefas"]}
    assert p["feitas_sem_volume"] == [ids[("Preventiva", "Etica Medica", "teoria")]]


def test_json_serializa_nos_dois_modos(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _semear()
    assert listas.main(["--progresso", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["modo"] == "progresso"
    assert listas.main(["--pendentes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["modo"] == "pendentes"


def test_leitor_nao_cria_coluna_nem_tabela(tmp_path, monkeypatch, capsys):
    """Banco anterior a esta parte: o leitor devolve `tarefa_id=None` e NAO roda DDL
    para se consertar (a licao do dry-run da part-2: 'nao grava' inclui DDL)."""
    caminho = _usar_db(tmp_path, monkeypatch, com_schema=False)
    con = sqlite3.connect(caminho)
    con.execute("CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "sessao_num INTEGER, area TEXT NOT NULL, questoes_feitas INTEGER, "
                "questoes_acertadas INTEGER, data_sessao DATE, observacoes TEXT)")
    con.execute("INSERT INTO sessoes_bulk (sessao_num, area, questoes_feitas, "
                "questoes_acertadas, data_sessao, observacoes) VALUES (9,'Pediatria',5,4,"
                "'2026-09-09','x')")
    con.commit()
    con.close()
    linhas = db.sessoes_bulk_listar()
    assert len(linhas) == 1 and linhas[0]["tarefa_id"] is None
    assert "tarefa_id" not in _colunas(caminho, "sessoes_bulk")
    assert db.sessoes_bulk_listar(vinculadas=True) == []


def test_cli_exige_exatamente_um_modo(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    for argv in ([], ["--progresso", "--pendentes"], ["--backfill", "--progresso"]):
        try:
            listas.main(argv)
            assert False, f"{argv} deveria recusar"
        except SystemExit as e:
            assert e.code == 2


def test_cli_apply_sem_expect_e_erro(tmp_path, monkeypatch):
    _usar_db(tmp_path, monkeypatch)
    for argv in (["--backfill", "--apply"], ["--backfill", "--apply", "--dry-run"]):
        try:
            listas.main(argv)
            assert False, f"{argv} deveria recusar"
        except SystemExit as e:
            assert e.code == 2


# --------------------------------------------------------- DoD 6: craftsmanship

def test_listas_nao_importa_sqlite3_nem_escreve():
    """O CLI e camada fina: zero `sqlite3`, zero SQL de escrita. A allowlist do F49
    (`tools/test_writer_allowlist.py`) tem que continuar SEM entrada para ele."""
    fonte = (ROOT / "tools" / "listas.py").read_text(encoding="utf-8-sig")
    arvore = ast.parse(fonte)
    importados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados.update(a.name.split(".")[0] for a in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            importados.add(no.module.split(".")[0])
    assert "sqlite3" not in importados, sorted(importados)
    import test_writer_allowlist as wal
    assert wal.tabelas_escritas(fonte) == set(), "listas.py nao pode ter SQL de escrita"
    assert "tools/listas.py" not in wal.ALLOWLIST


def test_db_e_o_writer_declarado_de_sessoes_bulk():
    """A contrapartida: `app/utils/db.py` PRECISA declarar `sessoes_bulk` na allowlist
    -- e onde o unico writer do vinculo mora."""
    import test_writer_allowlist as wal
    assert "sessoes_bulk" in wal.ALLOWLIST["app/utils/db.py"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
