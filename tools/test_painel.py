"""Painel gerado do banco (part-7, s186) -- spec `plano-ssot-e-cards-v2-part-7`.

O `--json` e o CONTRATO e e o que se testa; o HTML e render, provado por
marcadores `data-bloco` e pelas regras de forma que a memoria s151 fixou (UM
`.wrap`, `max-width` <= 2, sem scroll horizontal por tabela solta).

🔴 O teste central deste arquivo nao e de soma -- e da **escolha de fonte**. O
part-6 entregou o elo `sessoes_bulk.tarefa_id`, mas medido em 18/09/2026 o
backfill casa **1 de 126 sessoes**; um painel alimentado so pelo elo mostraria
~0 questoes feitas em todo bloco com o operador tendo feito 7.326. Por isso o
volume vem de `sessoes_bulk` agregado por AREA -- pelo portador que ja existe
(`db.bloco_de`, `areas.AREAS_AGREGADAS`, `areas.area_valida`), nunca por uma
copia do mapa -- e o elo aparece como camada fina declarada.
`test_volume_nao_desaparece_quando_o_elo_esta_vazio` e a sentinela disso.

Banco sintetico em tmp_path com `DB_PATH` monkeypatchado -- o `ipub.db` de
producao nunca e tocado (F49).
"""
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import painel  # noqa: E402

SCHEMA = """
-- `bloco` NAO e coluna: e derivada de `area` por `db.bloco_de` (portador unico).
CREATE TABLE plano_tarefas (
  id INTEGER PRIMARY KEY AUTOINCREMENT, fonte TEXT, ref_semana_fonte INTEGER,
  tarefa_fonte TEXT, semana_plano INTEGER, ordem INTEGER, area TEXT, tema TEXT,
  tipo TEXT, tipo_norm TEXT, url_lista TEXT, q_previstas REAL, status TEXT,
  data_conclusao TEXT, sessao_bulk_id INTEGER, origem_conclusao TEXT,
  nota TEXT, criado_em TEXT, atualizado_em TEXT);
CREATE TABLE sessoes_bulk (
  id INTEGER PRIMARY KEY AUTOINCREMENT, sessao_num INTEGER, area TEXT,
  questoes_feitas INTEGER, questoes_acertadas INTEGER, data_sessao TEXT,
  observacoes TEXT, tarefa_id INTEGER);
CREATE TABLE flashcards (id INTEGER PRIMARY KEY AUTOINCREMENT, questao_id INTEGER,
  tipo TEXT, frente_pergunta TEXT, verso_resposta TEXT, needs_qualitative INTEGER DEFAULT 0);
CREATE TABLE fsrs_cards (card_id INTEGER PRIMARY KEY, state INTEGER DEFAULT 0,
  due DATETIME, stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
  elapsed_days INTEGER DEFAULT 0, scheduled_days INTEGER DEFAULT 0,
  reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0, last_review DATETIME);
CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER,
  rating INTEGER, state INTEGER, due DATETIME, stability REAL, difficulty REAL,
  elapsed_days INTEGER, last_elapsed_days INTEGER, scheduled_days INTEGER,
  review_time DATETIME, regua_versao INTEGER);
"""

#: (area, tema, status, q_previstas). O bloco sai de `db.bloco_de(area)`:
#: Preventiva -> MFC, Cirurgia -> CIR, Cardiologia -> CM (fallback).
TAREFAS = [
    ("Preventiva", "Saude do Idoso", "pendente", 32.0),
    ("Preventiva", "APS", "feita", 50.0),
    ("Cirurgia", "Apendicite", "pendente", 40.0),
    ("Cirurgia", "Colecistite", "cortada", 30.0),
    ("Cardiologia", "HAS", "pendente", 60.0),
]

#: (area, feitas, acertos)
SESSOES = [
    ("Preventiva", 100, 85),
    ("Cirurgia", 200, 150),
    ("Cardiologia", 50, 40),
    ("Simulado", 120, 90),          # fora dos blocos, por regra
    ("GO", 10, 5),                  # area FANTASMA (F89) -> nunca vira CM
]


@pytest.fixture
def db_sintetico(tmp_path, monkeypatch):
    caminho = tmp_path / "ipub.db"
    con = sqlite3.connect(caminho)
    con.executescript(SCHEMA)
    for i, (area, tema, status, q) in enumerate(TAREFAS, start=1):
        con.execute("INSERT INTO plano_tarefas (id, fonte, ref_semana_fonte, "
                    "tarefa_fonte, semana_plano, ordem, area, tema, tipo, tipo_norm, "
                    "status, url_lista, q_previstas) "
                    "VALUES (?,'rf',?,?,?,?,?,?,'Revisao','revisao',?,?,?)",
                    (i, i, "t%d" % i, 1 if i < 4 else 2, i, area, tema, status,
                     "https://exemplo/%d" % i, q))
    for j, (area, f, a) in enumerate(SESSOES, start=1):
        con.execute("INSERT INTO sessoes_bulk (id, sessao_num, area, questoes_feitas, "
                    "questoes_acertadas, data_sessao, observacoes, tarefa_id) "
                    "VALUES (?,?,?,?,?,'2026-09-01','obs',NULL)", (j, j, area, f, a))
    con.commit()
    con.close()
    from app.utils import db as dbmod
    monkeypatch.setattr(dbmod, "DB_PATH", str(caminho))
    return caminho


# ------------------------------------------ as tres cestas do volume

def test_volume_usa_o_portador_canonico_do_bloco():
    """`db.bloco_de` e o mapa; o painel nao pode ter uma copia (licao do F89)."""
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    assert "db.bloco_de(" in fonte
    for copia in ('"MFC": (', "'MFC': (", 'BLOCOS_UERJ ='):
        assert copia not in fonte, "segundo vocabulario de bloco no painel: %r" % copia


def test_simulado_e_agregada_e_nunca_entra_num_bloco():
    """🔴 `bloco_de('Simulado')` devolve CM por FALLBACK. O termometro vale ~13%
    do volume: dobrado em CM, inflaria o bloco em um oitavo. `AREAS_AGREGADAS`
    ja marca isso no vocabulario -- o painel le de la, nao decide sozinho."""
    from app.utils import areas
    import app.utils.db as dbmod
    assert "Simulado" in areas.AREAS_AGREGADAS
    assert dbmod.bloco_de("Simulado") == "CM"      # o fallback que NAO pode valer
    bloco, agreg, _f = painel._volume_por_bloco(
        [{"area": "Simulado", "questoes_feitas": 5, "questoes_acertadas": 3}])
    assert bloco == {} and agreg == {"Simulado": {"feitas": 5, "acertos": 3}}


def test_area_fantasma_nao_vira_CM_por_fallback():
    """F89: `GO` solto nao esta em `core/areas.json`. `bloco_de` devolveria CM --
    o painel prefere nomear a divida a somar num bloco que ela nao e."""
    from app.utils import areas
    assert not areas.area_valida("GO")
    bloco, _a, fant = painel._volume_por_bloco(
        [{"area": "GO", "questoes_feitas": 7, "questoes_acertadas": 4}])
    assert bloco == {} and fant == {"GO": {"feitas": 7, "acertos": 4}}


def test_volume_por_bloco_separa_as_tres_cestas_sem_perder_questao():
    sessoes = [{"area": "Preventiva", "questoes_feitas": 10, "questoes_acertadas": 8},
               {"area": "Simulado", "questoes_feitas": 5, "questoes_acertadas": 3},
               {"area": "GO", "questoes_feitas": 2, "questoes_acertadas": 1}]
    bloco, agreg, fant = painel._volume_por_bloco(sessoes)
    assert bloco == {"MFC": {"feitas": 10, "acertos": 8}}
    assert agreg == {"Simulado": {"feitas": 5, "acertos": 3}}
    assert fant == {"GO": {"feitas": 2, "acertos": 1}}
    total = sum(v["feitas"] for c in (bloco, agreg, fant) for v in c.values())
    assert total == 17, "questao sumiu entre as cestas"


# ------------------------------------------------------- os 5 blocos (JSON)

def test_coletar_traz_os_cinco_blocos(db_sintetico):
    d = painel.coletar(hoje=date(2026, 9, 18))
    for chave in painel.BLOCOS:
        assert chave in d, "bloco %s ausente do contrato" % chave
    assert set(d["fontes"]) == set(painel.BLOCOS)


def test_progresso_por_bloco_conta_tarefa_e_questao(db_sintetico):
    d = painel.coletar(hoje=date(2026, 9, 18))
    blocos = d["plano"]["blocos"]
    assert blocos["MFC"]["tarefas"] == 2
    assert blocos["MFC"]["feitas"] == 1 and blocos["MFC"]["pendentes"] == 1
    assert blocos["CIR"]["cortadas"] == 1
    assert blocos["MFC"]["q_previstas"] == 82.0
    assert blocos["MFC"]["q_feitas"] == 100       # de sessoes_bulk, por area
    assert blocos["MFC"]["pct_acerto"] == 85.0
    assert d["plano"]["fora_de_bloco"] == {"Simulado": {"feitas": 120, "acertos": 90}}
    assert d["plano"]["areas_sem_mapa"] == {"GO": {"feitas": 10, "acertos": 5}}


def test_volume_nao_desaparece_quando_o_elo_esta_vazio(db_sintetico):
    """🔴 SENTINELA DO PART-7. Nenhuma sessao do fixture tem `tarefa_id` -- e o
    estado real do banco (o backfill casa 1 de 126). Se alguem reescrever o
    painel para ler o volume PELO ELO, todo bloco zera e o painel passa a mentir
    por omissao para um operador que fez 7.326 questoes."""
    d = painel.coletar(hoje=date(2026, 9, 18))
    assert d["plano"]["elo_por_tarefa"]["sessoes_sem_vinculo"] == len(SESSOES)
    somado = sum(b["q_feitas"] for b in d["plano"]["blocos"].values())
    assert somado == 350, "volume por bloco sumiu com o elo vazio: %d" % somado
    for b in d["plano"]["blocos"].values():
        assert b["q_feitas_por_elo"] == 0      # a camada fina ESTA vazia, e admite


def test_semana_corrente_e_a_menor_com_pendencia(db_sintetico):
    d = painel.coletar(hoje=date(2026, 9, 18))
    assert d["semana_corrente"] == 1
    assert d["semana"]["semana"] == 1
    assert all(t["bloco"] in ("MFC", "CIR") for t in d["semana"]["tarefas"])
    assert d["semana"]["tarefas"], "semana 1 tem pendentes e veio vazia"


def test_fsrs_traz_vencidos_teto_e_retencao(db_sintetico):
    d = painel.coletar(hoje=date(2026, 9, 18))
    f = d["fsrs"]
    assert f["vencidos"] == f["atrasados"] + f["hoje"]     # F64, um contador so
    assert f["teto_do_dia"] >= 60
    assert f["retencao_7d"]["retencao"] is None            # fixture sem revisao
    assert f["retencao_7d"]["revisoes"] == 0


def test_projecao_tem_marco_datado_e_DECLARA_o_enamed_2027(db_sintetico):
    """A spec pedia projecao ate ENAMED 2027. A data nao existe em SSOT nenhum
    (`core/provas.json` vai ate 01/11/2026; `performance.MARCOS` nao a tem).
    Declarar e o certo; estimar a partir de data inventada seria o defeito."""
    d = painel.coletar(hoje=date(2026, 9, 18))
    p = d["projecao"]
    assert p["marcos"] and all(m["data"] for m in p["marcos"])
    assert p["enamed_2027"]["projecao"] is None
    assert "sem ancora" in p["enamed_2027"]["motivo"]


def test_proximas_sete_respeitam_a_ordem_do_plano(db_sintetico):
    d = painel.coletar(hoje=date(2026, 9, 18))
    prox = d["proximas"]["tarefas"]
    assert len(prox) <= 7
    semanas = [t["semana"] for t in prox]
    assert semanas == sorted(semanas), "proximas fora da ordem do plano"
    assert all(t["id"] for t in prox)


# ----------------------------------------------- retencao pela regua (F112)

def test_retencao_conta_o_2_da_regua_v1_como_LAPSO(db_sintetico):
    """🔴 O F112 numa superficie nova. Sob a regua v1 a nota 2 era 'sem o alvo'
    -- falha de recuperacao. Contar por limiar fixo de `rating` inflaria a
    retencao exatamente como inflava o agendamento."""
    from app.utils import db as dbmod
    con = sqlite3.connect(db_sintetico)
    agora = dbmod.agora().strftime("%Y-%m-%d %H:%M:%S")
    for rating, regua in ((2, 1), (2, 2), (3, 1), (1, 1)):
        con.execute("INSERT INTO fsrs_revlog (card_id, rating, review_time, regua_versao) "
                    "VALUES (1, ?, ?, ?)", (rating, agora, regua))
    con.commit()
    con.close()
    r = dbmod.get_retencao_revlog(dias=7)
    assert r["revisoes"] == 4
    # lapsos = o 2 sob v1 + o 1; acertos = o 2 sob v2 + o 3
    assert r["lapsos"] == 2 and r["acertos"] == 2
    assert r["retencao"] == 0.5
    assert r["por_regua"] == {"1": 3, "2": 1}


def test_retencao_sem_revisao_e_None_nao_zero(db_sintetico):
    """0.0 seria lido como 'errou tudo'; a ausencia de dado tem nome proprio."""
    from app.utils import db as dbmod
    r = dbmod.get_retencao_revlog(dias=7)
    assert r["retencao"] is None and r["revisoes"] == 0


# ------------------------------------------------------------ HTML (render)

def test_html_tem_os_cinco_marcadores(db_sintetico):
    pagina = painel.render_html(painel.coletar(hoje=date(2026, 9, 18)))
    for chave in painel.BLOCOS:
        assert 'data-bloco="%s"' % chave in pagina


def test_html_obedece_o_contrato_de_render(db_sintetico):
    """Memoria s151: UM `.wrap` unico e `max-width` <= 2 -- width que nao alinha
    entre blocos foi defeito reincidente o bastante para virar regra."""
    pagina = painel.render_html(painel.coletar(hoje=date(2026, 9, 18)))
    assert pagina.count('class="wrap"') == 1
    assert pagina.count("max-width") <= 2
    assert "<title>Painel MedHub</title>" in pagina
    assert 'prefers-color-scheme: dark' in pagina
    assert ':root:not([data-theme="light"])' in pagina
    assert ':root[data-theme="dark"]' in pagina
    assert "background:var(--papel)" in pagina


def test_html_sem_latex_seta_unicode_ou_travessao(db_sintetico):
    """AGENTE.md §4.5 -- governa notacao e pontuacao (nunca ortografia, F113)."""
    pagina = painel.render_html(painel.coletar(hoje=date(2026, 9, 18)))
    for proibido in ("→", "—", "–", "$$", "\\rightarrow", "&mdash;"):
        assert proibido not in pagina, "caractere proibido na pagina: %r" % proibido


def test_link_relativo_nao_vira_ancora():
    """🔴 Achado de LEITURA A OLHO (s186), nao de gate. O plano guarda tambem
    caminho LOCAL -- `simulados/uerj/uerj_ad_2026_prova.pdf` na tarefa #890 --
    e ele resolve na maquina do operador e MORRE numa pagina publicada. Link
    quebrado e pior que texto simples, porque promete navegacao. Vira teste
    porque nenhum gate media isso."""
    assert "<a href=" in painel._link("https://exemplo.com/lista")
    local = painel._link("simulados/uerj/prova.pdf")
    assert "<a href=" not in local
    assert "simulados/uerj/prova.pdf" in local      # o caminho aparece, sem virar link
    assert "sem lista" in painel._link(None)
    assert "--" in painel._link("", vazio="--")


def test_tile_de_retencao_nao_aninha_negrito(db_sintetico):
    """Outro achado a olho: `<div class="m"><b>` ja e o negrito do numero; o
    texto do tile trazia um `<b>` proprio e nascia `<b><b>`."""
    pagina = painel.render_html(painel.coletar(hoje=date(2026, 9, 18)))
    assert "<b><b>" not in pagina


def test_html_nao_publica_nada(db_sintetico, tmp_path):
    """O CLI grava arquivo; quem publica e o agente no fechamento (spec)."""
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    for proibido in ("claude.ai", "Artifact", "requests.post", "urllib"):
        assert proibido not in fonte, "o painel nao fala com API nenhuma: %r" % proibido


def test_cli_grava_no_out_pedido(db_sintetico, tmp_path, capsys):
    destino = tmp_path / "sub" / "painel.html"
    assert painel.main(["--html", "--out", str(destino)]) == 0
    assert destino.is_file() and destino.stat().st_size > 2000
    saida = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert saida["blocos"] == list(painel.BLOCOS)


def test_cli_exige_um_modo(db_sintetico):
    with pytest.raises(SystemExit):
        painel.main([])


# ----------------------------------------------------------- craftsmanship

def test_painel_e_read_only():
    """Nenhum verbo de escrita no fonte, e fora da allowlist de writers (F49)."""
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    import re
    for verbo in (r"\bINSERT\s+INTO\b", r"\bUPDATE\s+\w+\s+SET\b", r"\bDELETE\s+FROM\b",
                  r"\bALTER\s+TABLE\b", r"\bCREATE\s+TABLE\b"):
        assert not re.search(verbo, fonte, re.I), "verbo de escrita no painel: %s" % verbo
    assert "import sqlite3" not in fonte, "painel nao abre sqlite3 proprio (AGENTE §6)"
    allow = (ROOT / "tools" / "test_writer_allowlist.py").read_text(encoding="utf-8")
    assert "tools/painel.py" not in allow, "painel entrou na allowlist de writers"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
