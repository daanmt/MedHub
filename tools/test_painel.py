"""Painel gerado do banco -- part-7 (s186), refeito na s194 (auditoria de fidelidade de 23/09).

O `--json` e o CONTRATO e e o que se testa; o HTML e render, provado por marcadores `data-bloco`
e pelas regras de forma do projeto (UM `.wrap`, `max-width` <= 2, sem scroll horizontal).

🔴 O que a s194 trava, achado a achado da auditoria (`painel` x `panorama` x `day_plan`):
- **semana**: o painel usava a MENOR semana com pendencia; o boot usa a de CALENDARIO. Agora os dois
  saem da MESMA funcao (`plano.panorama`) -- `test_concordancia_painel_x_panorama` e a sentinela;
- **saldo de cards**: o painel mostrava vencidos e teto, sem o consumo do dia -- quem lia entendia
  "faltam 83" com o saldo zerado. Agora `consumo/teto (restantes)` pelos leitores do `day_plan`;
- **agenda de 7 dias**: `db.agenda_revisoes`, o MESMO leitor da tela de fim da aba Cards;
- **ritmo**: real (7 e 14 dias, `db.get_ritmo_real`) ao lado do alvo (`volume_vs_marco` e a Fase 1
  do `day_plan`);
- **fora**: "do previsto", o 126 fixo, o 2760 e o simulado contado como tarefa de CM.

Cada numero da pagina tem aqui um teste que o amarra ao leitor-fonte. Banco sintetico em tmp_path
com `DB_PATH` monkeypatchado e calendario e relogio congelados -- o `ipub.db` nunca e tocado (F49).
"""
import json
import re
import sqlite3
import sys
from datetime import date, datetime, timedelta
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

HOJE = date(2026, 9, 23)
#: O calendario da trilha como ele e hoje (S1 = 19-20/09, S2 = 21-27/09), congelado.
CALENDARIO = {1: (date(2026, 9, 19), date(2026, 9, 20)),
              2: (date(2026, 9, 21), date(2026, 9, 27)),
              3: (date(2026, 9, 28), date(2026, 10, 4))}

#: (semana, area, tema, status, q_previstas, fonte, url). O bloco sai de `db.bloco_de(area)`:
#: Preventiva -> MFC, Cirurgia -> CIR, Cardiologia -> CM (fallback), Simulado -> CM (fallback!).
TAREFAS = [
    (1, "Preventiva", "Saude do Idoso", "pendente", 32.0, "rf", "https://exemplo/1"),
    (1, "Preventiva", "APS", "feita", 50.0, "rf", "https://exemplo/2"),
    (1, "Cirurgia", "Apendicite", "pendente", 40.0, "rf", "https://exemplo/3"),
    (2, "Cirurgia", "Colecistite", "cortada", 30.0, "rf", "https://exemplo/4"),
    (2, "Cardiologia", "HAS", "pendente", 60.0, "rf", "https://exemplo/5"),
    (2, "Simulado", "UERJ 2021 -- prova INTEIRA", "pendente", 60.0, "custom",
     "simulados/uerj/uerj_2021.pdf"),
    (2, "Preventiva", "Raciocinio diagnostico", "pendente", 0.0, "custom", None),
    (3, "Cardiologia", "IC", "pendente", 45.0, "rf", "https://exemplo/8"),
    (None, "Cardiologia", "Reserva", "pendente", 20.0, "rf", None),
]

#: (area, feitas, acertos, dias atras)
SESSOES = [
    ("Preventiva", 100, 85, 1),
    ("Cirurgia", 200, 150, 3),
    ("Cardiologia", 50, 40, 10),
    ("Simulado", 120, 90, 0),        # fora dos blocos, por regra
    ("GO", 10, 5, 30),               # area FANTASMA (F89) -> nunca vira CM
]


@pytest.fixture
def db_sintetico(tmp_path, monkeypatch):
    caminho = tmp_path / "ipub.db"
    con = sqlite3.connect(caminho)
    con.executescript(SCHEMA)
    for i, (sem, area, tema, status, q, fonte, url) in enumerate(TAREFAS, start=1):
        con.execute("INSERT INTO plano_tarefas (id, fonte, ref_semana_fonte, "
                    "tarefa_fonte, semana_plano, ordem, area, tema, tipo, tipo_norm, "
                    "status, url_lista, q_previstas) "
                    "VALUES (?,?,?,?,?,?,?,?,'Revisao','revisao',?,?,?)",
                    (i, fonte, i, "t%d" % i, sem, i, area, tema, status, url, q))
    for j, (area, f, a, atras) in enumerate(SESSOES, start=1):
        dia = (HOJE - timedelta(days=atras)).isoformat()
        con.execute("INSERT INTO sessoes_bulk (id, sessao_num, area, questoes_feitas, "
                    "questoes_acertadas, data_sessao, observacoes, tarefa_id) "
                    "VALUES (?,?,?,?,?,?,'obs',NULL)", (j, j, area, f, a, dia))
    con.commit()
    con.close()
    from app.utils import db as dbmod
    import plano
    monkeypatch.setattr(dbmod, "DB_PATH", str(caminho))
    monkeypatch.setattr(dbmod, "agora", lambda: datetime(2026, 9, 23, 18, 0, 0))
    monkeypatch.setattr(dbmod, "hoje", lambda: HOJE)
    monkeypatch.setattr(plano, "calendario_trilha", lambda trilha=None: dict(CALENDARIO))
    monkeypatch.setattr(painel, "_aulas_por_tarefa", lambda: {7: "raciocinio-diagnostico"})
    return caminho


def _cards(caminho, agora=None):
    """3 cards vencidos (2 atrasados, 1 hoje), 2 novos, 1 que vence amanha, 1 daqui a 3 dias; e 2
    revisoes gravadas hoje no revlog."""
    agora = agora or datetime.now()
    con = sqlite3.connect(caminho)
    linhas = [
        (1, 2, agora - timedelta(days=3)), (2, 2, agora - timedelta(days=1)),
        (3, 2, agora.replace(hour=0, minute=0, second=1)),
        (4, 0, agora), (5, 0, agora),
        (6, 2, agora + timedelta(days=1)), (7, 2, agora + timedelta(days=3)),
    ]
    for cid, state, due in linhas:
        con.execute("INSERT INTO flashcards (id, tipo, frente_pergunta, verso_resposta) "
                    "VALUES (?, 'x', 'p', 'r')", (cid,))
        con.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?,?,?)",
                    (cid, state, due.strftime("%Y-%m-%d %H:%M:%S")))
    for cid in (6, 7):
        con.execute("INSERT INTO fsrs_revlog (card_id, rating, review_time, regua_versao) "
                    "VALUES (?, 3, ?, 2)", (cid, HOJE.isoformat() + " 10:00:00"))
    con.commit()
    con.close()


# ------------------------------------------ as tres cestas do volume

def test_volume_usa_o_portador_canonico_do_bloco():
    """`db.bloco_de` e o mapa; o painel nao pode ter uma copia (licao do F89)."""
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    assert "db.bloco_de(" in fonte
    for copia in ('"MFC": (', "'MFC': (", 'BLOCOS_UERJ ='):
        assert copia not in fonte, "segundo vocabulario de bloco no painel: %r" % copia


def test_simulado_e_agregada_e_nunca_entra_num_bloco():
    """🔴 `bloco_de('Simulado')` devolve CM por FALLBACK. O painel le `AREAS_AGREGADAS`."""
    from app.utils import areas
    import app.utils.db as dbmod
    assert "Simulado" in areas.AREAS_AGREGADAS
    assert dbmod.bloco_de("Simulado") == "CM"      # o fallback que NAO pode valer
    bloco, agreg, _f = painel._volume_por_bloco(
        [{"area": "Simulado", "questoes_feitas": 5, "questoes_acertadas": 3}])
    assert bloco == {} and agreg == {"Simulado": {"feitas": 5, "acertos": 3}}


def test_area_fantasma_nao_vira_CM_por_fallback():
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


# ------------------------------------------------------- o contrato (JSON)

def test_coletar_traz_os_quatro_blocos(db_sintetico):
    d = painel.coletar()
    for chave in painel.BLOCOS:
        assert chave in d, "bloco %s ausente do contrato" % chave
    assert d["data"] == HOJE.isoformat()


def test_semana_e_a_do_calendario_e_nao_a_menor_com_pendencia(db_sintetico):
    """🔴 Achado 1 da auditoria. A S1 tem pendencia, mas hoje (23/09) o calendario esta na S2:
    a semana e 2, e as pendentes da S1 entram como ATRASADAS."""
    s = painel.coletar()["semana"]
    assert s["semana"] == 2
    assert s["inicio"] == "2026-09-21" and s["fim"] == "2026-09-27"
    assert s["atrasadas"] == 2
    atrasadas = [t["id"] for t in s["tarefas"] if t["atrasada"]]
    assert atrasadas == [1, 3]


def test_concordancia_painel_x_panorama(db_sintetico, capsys):
    """🔴 SENTINELA DA S194. O boot le `plano.py --panorama`; o painel tem de dizer a MESMA semana,
    o MESMO numero de tarefas e de questoes, na MESMA ordem -- pela mesma funcao, nunca por copia."""
    import plano
    assert plano.main(["--panorama", "--json"]) == 0
    pan = json.loads(capsys.readouterr().out)
    s = painel.coletar()["semana"]
    assert s["semana"] == pan["semana"]
    assert s["total"] == len(pan["abertas"])
    assert s["q"] == pan["q_abertas"]
    assert s["atrasadas"] == pan["atrasadas"]
    assert [t["id"] for t in s["tarefas"]] == [t["id"] for t in pan["abertas"]]
    assert s["proxima"]["tarefas"] == pan["proxima"]["tarefas"]


def test_painel_le_a_semana_pelo_panorama_e_nao_tem_regra_propria():
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    assert "plano.panorama(" in fonte
    assert "_semana_corrente" not in fonte, "segunda regra de semana no painel"


def test_cada_tarefa_diz_o_que_fazer(db_sintetico):
    t = {x["id"]: x for x in painel.coletar()["semana"]["tarefas"]}
    assert t[5]["classe"] == "lista" and t[5]["url_lista"] == "https://exemplo/5"
    assert t[7]["classe"] == "aula" and t[7]["aula"] == "raciocinio-diagnostico"
    assert t[6]["rotulo"] == "Simulado", "simulado nao se apresenta como CM"


def test_cota_de_questoes_e_a_do_day_plan(db_sintetico):
    import day_plan
    from app.utils import db as dbmod
    pend = [l for l in dbmod.plano_listar() if l.get("status") == "pendente"]
    esperado = day_plan.cota_do_dia(pend, CALENDARIO, HOJE)
    q = painel.coletar()["dia"]["questoes"]
    assert q["cota"] == esperado["cota"] and q["q_restantes"] == esperado["q_restantes"]
    assert q["fim"] == esperado["fim"]


def test_questoes_feitas_hoje_contam_todo_o_volume_do_dia(db_sintetico):
    """Mesma conta do `q_hoje` do boot (`day_plan.build`): simulado CONTA (s126)."""
    assert painel.coletar()["dia"]["questoes"]["feitas_hoje"] == 120


def test_saldo_de_cards_e_consumo_sobre_teto(db_sintetico):
    """🔴 Achado 3 da auditoria: sem o consumo, "vencidos 83" se lia como "faltam 83" com o saldo
    zerado. Leitores do `day_plan`: `_fsrs_counts`, `_teto_efetivo`, `realizado_do_dia`."""
    import day_plan
    _cards(db_sintetico)
    from app.utils import db as dbmod
    con = dbmod.get_connection()
    try:
        cont = day_plan._fsrs_counts(con)
        consumo = day_plan.realizado_do_dia(con, HOJE.isoformat())["cards"]
    finally:
        con.close()
    teto = day_plan._teto_efetivo(day_plan.vencidos_de(cont))
    c = painel.coletar()["dia"]["cards"]
    assert c["consumo_hoje"] == consumo == 2
    assert c["teto"] == teto
    assert c["restantes"] == max(0, teto - consumo)
    assert c["vencidos"] == cont["atrasados"] + cont["hoje"] == 3
    assert c["novos"] == cont["backlog_novos"] == 2


def test_saldo_nunca_negativo(db_sintetico, monkeypatch):
    import day_plan
    monkeypatch.setattr(day_plan, "realizado_do_dia",
                        lambda con, d: {"questoes": 0, "simulado": 0, "cards": 500})
    c = painel.coletar()["dia"]["cards"]
    assert c["consumo_hoje"] == 500 and c["restantes"] == 0


def test_agenda_de_sete_dias_e_a_mesma_da_tela_de_fim_dos_cards(db_sintetico):
    """A aba Cards desenha a agenda de `db.agenda_revisoes` (export do player); o painel tambem."""
    _cards(db_sintetico)
    from app.utils import db as dbmod
    esperado = dbmod.agenda_revisoes(dias=7)
    ag = painel.coletar()["dia"]["agenda"]
    assert ag == esperado
    assert len(ag["dias"]) == 7


def test_ritmo_real_e_alvo_pelos_leitores_fonte(db_sintetico):
    import day_plan
    import performance
    from app.utils import db as dbmod
    r = painel.coletar()["ritmo"]
    assert r["real_7d"] == dbmod.get_ritmo_real(7)
    assert r["real_14d"] == dbmod.get_ritmo_real(14)
    con = dbmod.get_connection()
    try:
        vm = performance.volume_vs_marco(con, HOJE)
    finally:
        con.close()
    assert r["alvo_marco"] == vm["ritmo_alvo"] and r["marco"] == vm["marco"]
    assert r["acumulado"] == vm["total"]
    assert r["acerto"] == round(vm["acertos"] / vm["total"] * 100, 1)
    cron = day_plan._cronograma_hoje(vm["total"], HOJE, calendario=CALENDARIO)
    assert r["alvo_fase1"] == cron["ritmo_cronograma"]
    assert r["fase1_q"] == cron["restante_q"]


def test_simulado_fora_das_tarefas_por_bloco(db_sintetico):
    """🔴 Achado: 11 simulados (940q) contados como tarefas de CM. `bloco_de('Simulado')` = CM
    por fallback; a tarefa de simulado vai para a linha propria."""
    b = painel.coletar()["blocos"]
    assert b["blocos"]["CM"]["tarefas"] == 3        # HAS, IC, Reserva -- sem o simulado
    assert b["simulados"]["tarefas"] == 1 and b["simulados"]["feitas"] == 0
    assert b["simulados"]["q_feitas"] == 120
    assert b["blocos"]["CIR"]["tarefas"] == 1, "cortada nao conta"
    assert b["blocos"]["MFC"]["feitas"] == 1 and b["blocos"]["MFC"]["tarefas"] == 3
    assert b["blocos"]["MFC"]["q_feitas"] == 100 and b["blocos"]["MFC"]["acerto"] == 85.0
    assert b["sem_bloco"] == {"GO": {"feitas": 10, "acertos": 5}}


def test_sem_do_previsto_sem_constante_2760_sem_126_fixo(db_sintetico):
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    for morto in ("2760", "126 -", "pct_questoes", "do previsto", "orcamento_fase1"):
        assert morto not in fonte, "sobrou no painel: %r" % morto
    pagina = painel.render_html(painel.coletar())
    assert "do previsto" not in pagina and "Orcamento" not in pagina


# ----------------------------------------------- retencao pela regua (F112)

def test_retencao_conta_o_2_da_regua_v1_como_LAPSO(db_sintetico):
    from app.utils import db as dbmod
    con = sqlite3.connect(db_sintetico)
    agora = dbmod.agora().strftime("%Y-%m-%d %H:%M:%S")
    for rating, regua in ((2, 1), (2, 2), (3, 1), (1, 1)):
        con.execute("INSERT INTO fsrs_revlog (card_id, rating, review_time, regua_versao) "
                    "VALUES (1, ?, ?, ?)", (rating, agora, regua))
    con.commit()
    con.close()
    r = dbmod.get_retencao_revlog(dias=7)
    assert r["revisoes"] == 4 and r["lapsos"] == 2 and r["retencao"] == 0.5
    assert painel.coletar()["dia"]["cards"]["retencao_7d"] == r


def test_retencao_sem_revisao_e_None_nao_zero(db_sintetico):
    from app.utils import db as dbmod
    r = dbmod.get_retencao_revlog(dias=7)
    assert r["retencao"] is None and r["revisoes"] == 0


# ------------------------------------------------------------ HTML (render)

def _pagina():
    return painel.render_html(painel.coletar())


def test_html_tem_os_marcadores_dos_blocos(db_sintetico):
    pagina = _pagina()
    for chave in painel.BLOCOS:
        assert 'data-bloco="%s"' % chave in pagina


def test_html_obedece_o_contrato_de_render(db_sintetico):
    pagina = _pagina()
    assert pagina.count('class="wrap"') == 1
    assert pagina.count("max-width") <= 2
    assert "<title>Painel MedHub</title>" in pagina
    assert 'prefers-color-scheme: dark' in pagina
    assert ':root:not([data-theme="light"])' in pagina
    assert ':root[data-theme="dark"]' in pagina
    assert "background:var(--papel)" in pagina


def test_celular_sem_sticky_sem_nowrap_e_grid_item_encolhe(db_sintetico):
    pagina = _pagina().lower()
    assert "sticky" not in pagina and "nowrap" not in pagina
    assert "min-width:0" in pagina


#: Bastidor que nao aparece para o operador (pedido de 23/09): CLI, tabela, marcador de backoffice.
JARGAO = ("tools/", "plano_tarefas", "sessoes_bulk", "data-backoffice", "regua_versao", "day_plan",
          "fsrs_", "backfill", "elo por", "--json", "REGIME DE DIVIDA")


def test_html_sem_jargao(db_sintetico):
    _cards(db_sintetico)
    pagina = _pagina()
    achados = [j for j in JARGAO if j in pagina]
    assert not achados, "jargao na tela: %s" % achados


def test_um_unico_atualizado_ha_discreto(db_sintetico):
    """Um so carimbo, entre os marcadores que o hub ignora ao comparar a projecao (a hora muda a
    cada geracao; o conteudo, nao)."""
    pagina = _pagina()
    assert pagina.count("data-gerado=") == 1
    assert pagina.count(painel.MARCA_GERADO_ABRE) == 1 and pagina.count(painel.MARCA_GERADO_FECHA) == 1
    assert "gerado em" not in pagina


def test_saldo_aparece_como_consumo_sobre_teto(db_sintetico):
    _cards(db_sintetico)
    d = painel.coletar()
    pagina = painel.render_html(d)
    c = d["dia"]["cards"]
    assert re.search(r"<b>%d</b>\s*de %d" % (c["consumo_hoje"], c["teto"]), pagina)
    assert "faltam %d" % c["restantes"] in pagina


def test_link_da_lista_e_da_aula_e_atalho_para_os_cards(db_sintetico):
    pagina = _pagina()
    assert 'href="https://exemplo/5"' in pagina
    assert 'data-hub-aula="raciocinio-diagnostico"' in pagina
    assert 'data-hub-aba="cards"' in pagina
    assert 'href="simulados/uerj/uerj_2021.pdf"' not in pagina, "caminho local nao vira link"


def test_html_sem_latex_seta_unicode_ou_travessao(db_sintetico):
    pagina = _pagina()
    for proibido in ("→", "—", "–", "$$", "\\rightarrow", "&mdash;"):
        assert proibido not in pagina, "caractere proibido na pagina: %r" % proibido


def test_link_relativo_nao_vira_ancora():
    assert "<a href=" in painel._link("https://exemplo.com/lista", "abrir lista")
    local = painel._link("simulados/uerj/prova.pdf", "abrir lista")
    assert "<a href=" not in local


def test_html_nao_publica_nada():
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    for proibido in ("claude.ai", "Artifact", "requests.post", "urllib"):
        assert proibido not in fonte, "o painel nao fala com API nenhuma: %r" % proibido


def test_cli_grava_no_out_pedido(db_sintetico, tmp_path, capsys):
    destino = tmp_path / "sub" / "painel.html"
    assert painel.main(["--html", "--out", str(destino)]) == 0
    assert destino.is_file() and destino.stat().st_size > 2000
    saida = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert saida["blocos"] == list(painel.BLOCOS) and saida["semana"] == 2


def test_cli_exige_um_modo(db_sintetico):
    with pytest.raises(SystemExit):
        painel.main([])


def test_painel_e_read_only():
    fonte = Path(painel.__file__).read_text(encoding="utf-8")
    for verbo in (r"\bINSERT\s+INTO\b", r"\bUPDATE\s+\w+\s+SET\b", r"\bDELETE\s+FROM\b",
                  r"\bALTER\s+TABLE\b", r"\bCREATE\s+TABLE\b"):
        assert not re.search(verbo, fonte, re.I), "verbo de escrita no painel: %s" % verbo
    assert "import sqlite3" not in fonte, "painel nao abre sqlite3 proprio (AGENTE §6)"
    allow = (ROOT / "tools" / "test_writer_allowlist.py").read_text(encoding="utf-8")
    assert "tools/painel.py" not in allow, "painel entrou na allowlist de writers"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_acao_do_simulado_no_hub_e_atalho_e_fora_dele_e_texto():
    """s201: a tarefa de simulado com questoes no banco ganha 'resolver no hub' (aba Listas,
    modo Simulados); caminho local sem questoes segue texto, nunca link para o disco."""
    base = {"classe": "lista", "url_lista": "simulados/uerj/uerj_ad_2021_a.pdf"}
    assert 'data-hub-aba="questoes" data-hub-modo="simulados">resolver no hub</a>' in painel._acao(dict(base, no_hub=True))
    assert painel._acao(base) == '<span class="tenue">prova em PDF no computador</span>'
