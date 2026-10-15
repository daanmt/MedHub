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
              3: (date(2026, 9, 28), date(2026, 10, 4)),
              4: (date(2026, 10, 5), date(2026, 10, 11))}

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
    # s213: a S4 com duas pendentes e uma feita -- a rota passa a ter 2 semanas (S3 e S4)
    (4, "Pediatria", "Bronquiolite", "pendente", 25.0, "rf", "https://exemplo/10"),
    (4, "Pediatria", "Puericultura", "pendente", 0.0, "custom", None),
    (4, "Pediatria", "Imunizacoes", "feita", 30.0, "rf", "https://exemplo/12"),
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
    # s216 (part-5): os lotes do player (regra P09) saem de tmp/ -- aqui um tmp/ vazio, nunca o real
    import day_plan
    monkeypatch.setattr(day_plan, "RAIZ_LOTES", tmp_path / "sem-lotes")
    # s213: {tarefa: [aulas]} -- a #7 tem a aula que a CUMPRE; a #10 (lista), uma que a PREPARA
    monkeypatch.setattr(painel, "_aulas_por_tarefa", lambda: {
        7: [{"slug": "raciocinio-diagnostico", "titulo": "Raciocinio"}],
        10: [{"slug": "bronquiolite", "titulo": "A Escada da Bronquiolite"}]})
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

def test_coletar_traz_os_quatro_blocos_fixos_e_o_de_documentacao(db_sintetico):
    """Era `test_coletar_traz_os_quatro_blocos`. s213 (D4-5): a s212 trouxe o 5o bloco,
    Documentacao (`docs`), que so aparece na pagina com documento -- por isso ele mora em
    `BLOCO_DOCS`, fora de `BLOCOS` (os 4 que a pagina sempre desenha), e o contrato o traz sempre,
    lista vazia quando nao ha nenhum."""
    d = painel.coletar()
    for chave in painel.BLOCOS:
        assert chave in d, "bloco %s ausente do contrato" % chave
    assert painel.BLOCO_DOCS not in painel.BLOCOS
    assert isinstance(d[painel.BLOCO_DOCS], list)
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


# ------------------------------------------ s213: a rota inteira da Fase 1

def test_rota_concorda_com_o_panorama(db_sintetico, capsys):
    """A rota (semanas seguintes ate a S7) sai do `plano.panorama`, a MESMA regua do boot: mesmas
    semanas, mesmos ids na mesma ordem, mesmas questoes."""
    import plano
    assert plano.main(["--panorama", "--json"]) == 0
    pan = json.loads(capsys.readouterr().out)
    rota = painel.coletar()["semana"]["rota"]
    assert [r["semana"] for r in rota] == [r["semana"] for r in pan["rota"]] == [3, 4]
    for meu, dele in zip(rota, pan["rota"]):
        assert [t["id"] for t in meu["tarefas"]] == [t["id"] for t in dele["tarefas"]]
        assert (meu["q"], meu["feitas"], meu["total"]) == (dele["q"], dele["feitas"], dele["total"])
    assert [t["id"] for t in rota[1]["tarefas"]] == [10, 11], "feita fica fora"
    assert (rota[1]["inicio"], rota[1]["fim"]) == ("2026-10-05", "2026-10-11")


def test_rota_concorda_com_a_aba_aulas(db_sintetico):
    """🔴 Sentinela contra DUAS reguas de semana: a aba Teoria (`hub.secoes_do_quadro`, com a copia
    `hub.semana_atual`) e o Painel tem de pôr as tarefas nas MESMAS semanas futuras. s216 (part-1):
    a Teoria mostra so tarefa de aula (e tarefa com aula ligada), entao a igualdade vira INCLUSAO --
    toda tarefa de aula da rota existe na Teoria, na secao da mesma semana, e nada na Teoria fica
    fora da rota."""
    from tools import hub
    from app.utils import db as dbmod
    secoes, _c, _a = hub.secoes_do_quadro([], plano_linhas=dbmod.plano_listar(),
                                          calendario=dict(CALENDARIO), hoje=HOJE)
    s = painel.coletar()["semana"]
    futuras = {int(x["chave"]): [i["id"] for i in x["itens"]] for x in secoes
               if x["chave"].isdigit() and int(x["chave"]) > s["semana"]}
    rota = {r["semana"]: [t["id"] for t in r["tarefas"]] for r in s["rota"]}
    de_aula = {sem: [t["id"] for t in r["tarefas"] if t["classe"] == "aula"]
               for sem, r in ((r["semana"], r) for r in s["rota"])}
    assert any(de_aula.values()), "o cenario tem de ter tarefa de aula na rota (a Puericultura, S4)"
    for sem, ids in de_aula.items():
        assert [i for i in futuras.get(sem, []) if i in ids] == ids, (sem, ids, futuras)
    for sem, ids in futuras.items():
        assert set(ids) <= set(rota.get(sem, [])), "a Teoria nao inventa tarefa fora da rota"
    # audit R1 (s213): o filtro acima so trava o ALCANCE da rota; a semana corrente das duas
    # reguas tambem tem de ser a mesma, senao a copia do hub diverge sem ninguem ver.
    pendentes = [l for l in dbmod.plano_listar() if l.get("status") == "pendente"]
    assert hub.semana_atual(dict(CALENDARIO), HOJE, pendentes) == s["semana"]


def test_semana_corrente_sem_pendencia_nao_desenha_lista_vazia():
    """s213 (audit R2): semana corrente sem tarefa em aberto (a S3 em 04/10/2026) dizia
    "0 tarefa(s) em aberto" sobre um <ol> vazio, acima da rota."""
    d = {"semana": 3, "inicio": "2026-09-28", "fim": "2026-10-04", "dias": 1, "tarefas": [],
         "total": 0, "q": 0, "atrasadas": 0, "proxima": None, "rota": []}
    pagina = painel._html_semana(d)
    assert "Sem tarefa em aberto nesta semana." in pagina
    assert "0 tarefa(s)" not in pagina and '<ol class="tarefas"></ol>' not in pagina


def test_rota_semana_futura_recolhida_e_corrente_aberta(db_sintetico):
    pagina = _pagina()
    sems = re.findall(r'<details class="rota-sem"[^>]*>', pagina)
    assert len(sems) == 2 and not any("open" in x for x in sems), "semana futura nasce fechada"
    corrente = pagina.split('class="rota"')[0]
    assert "<details" not in corrente.split('data-bloco="semana"')[1].split("Ver as outras")[0], \
        "a semana corrente fica aberta, fora de details"
    assert "Semana 4 · 05/10 a 11/10" in pagina and "2&nbsp;tarefas · 25&nbsp;questões" in pagina
    assert '<p class="nota prox">Depois:' not in pagina, "com rota, a linha Depois sai"


def test_rota_usa_o_mesmo_li_da_semana(db_sintetico):
    pagina = _pagina()
    sem4 = re.search(r'<details class="rota-sem"[^>]*><summary>[^<]*<span class="rota-tit">Semana 4'
                     r'.*?</details>', pagina, re.S).group(0)
    # s216 (part-2): o `li` carrega o id do plano (`data-tarefa`), o mesmo na semana e na rota
    # s229: o cartao -- meta (chip + contagem) em cima, o tema, os botoes no pe
    lis = re.findall(r'<li class="tarefa" data-tarefa="\d+"><i class="t-faixa"[^>]*></i><p class="t-meta">.*?</p><p class="t-tema">([^<]+)</p>'
                     r'(?:<p class="t-acao">.*?</p>)?</li>', sem4, re.S)
    assert lis == ["Bronquiolite", "Puericultura"]
    assert 'href="https://exemplo/10"' in sem4


def test_tarefa_de_lista_com_aula_que_prepara_tem_os_dois_links(db_sintetico):
    """D4-2: a aula que PREPARA a tarefa (`tarefas: [...]` no registro) aparece no Painel como na
    aba Aulas: a lista E a aula. s216 (part-2): o link leva o titulo da aula (`data-titulo`), que o
    hub mostra no leitor sem procurar o link na Teoria."""
    pagina = _pagina()
    li = re.search(r'<li class="tarefa" data-tarefa="10">.*?</li>', pagina, re.S).group(0)
    assert "<p class=\"t-tema\">Bronquiolite</p>" in li and ">Abrir lista</a>" in li
    assert ('<a class="t-btn" href="aulas/bronquiolite.html" data-hub-aula="bronquiolite" '
            'data-titulo="A Escada da Bronquiolite">Abrir aula</a>') in li


def test_tarefa_do_painel_carrega_o_id_do_plano(db_sintetico):
    """s216 (hub-integracao part-2): o `li.tarefa` do Painel carrega `data-tarefa` (o id do plano) --
    e por ele que a pagina pinta, sem publish, a lista resolvida na aba Listas. A Documentacao nao e
    tarefa do plano: fica sem `data-tarefa` (o seletor da pagina e `li.tarefa[data-tarefa]`)."""
    pagina = _pagina()
    s = painel.coletar()["semana"]
    esperado = [t["id"] for t in s["tarefas"]] + [t["id"] for r in s["rota"] for t in r["tarefas"]]
    plano = pagina.split('data-bloco="docs"')[0]
    ids = [int(i) for i in re.findall(r'<li class="tarefa[^"]*" data-tarefa="(\d+)">', plano)]
    assert ids == esperado and len(ids) == plano.count('<li class="tarefa')
    docs = painel._html_docs([{"slug": "dossie", "titulo": "Dossiê da banca"}])
    assert "data-tarefa" not in docs
    assert 'href="aulas/dossie.html" data-hub-aula="dossie" data-titulo="Dossiê da banca">' in docs


def test_aulas_por_tarefa_le_quem_cumpre_e_quem_prepara(tmp_path, monkeypatch):
    """Mesma semantica de `hub.ligacoes_do_quadro`: `tarefa_id` (cumpre) E `tarefas` (prepara); so
    aula com arquivo no disco (sem arquivo, o atalho abriria nada)."""
    import json as _json
    for slug in ("dmg", "pq"):
        (tmp_path / ("aula-%s.html" % slug)).write_text("<title>x</title>", encoding="utf-8")
    reg = tmp_path / "quadro.json"
    reg.write_text(_json.dumps({"itens": {
        "dmg": {"tipo": "aula", "titulo": "A Escada do DMG", "tarefas": [26, 40]},
        "pq": {"tipo": "aula", "titulo": "PQ", "tarefa_id": 875},
        "sumiu": {"tipo": "aula", "titulo": "Sumiu", "tarefas": [40]}}}), encoding="utf-8")
    monkeypatch.setattr(painel, "QUADRO", reg)
    monkeypatch.setattr(painel, "ARTIFATOS", tmp_path)
    # s229: `cumpre` = a aula e o `tarefa_id` da tarefa (da o titulo dela no Painel)
    assert painel._aulas_por_tarefa() == {
        26: [{"slug": "dmg", "titulo": "A Escada do DMG", "cumpre": False}],
        40: [{"slug": "dmg", "titulo": "A Escada do DMG", "cumpre": False}],
        875: [{"slug": "pq", "titulo": "PQ", "cumpre": True}]}


def test_sem_rota_mantem_a_linha_depois():
    """Sem rota (ex.: fora do calendario, ou a S7 corrente), a linha "Depois" segue como era."""
    d = {"semana": 7, "inicio": None, "fim": None, "dias": None, "tarefas": [], "total": 0,
         "q": 0, "atrasadas": 0, "rota": [],
         "proxima": {"semana": 8, "inicio": None, "fim": None, "tarefas": 3, "q": 90}}
    html_ = painel._html_semana(d)
    assert '<p class="nota prox">Depois: semana 8, 3 tarefa(s), 90 questões.</p>' in html_
    assert "rota-sem" not in html_


def test_lista_no_banco_do_hub_abre_a_aba_listas_e_nao_o_emed():
    """D4-1 (decisao do operador, 25/09: "nao sair do medhub"): tarefa com questoes no banco do hub
    abre a aba Listas -- modo Questoes para lista, Simulados para simulado -- e o link do EMED some.
    Fora do banco, "abrir lista" externo segue como era."""
    base = {"classe": "lista", "url_lista": "https://exemplo/40", "area": "Endocrinologia"}
    no_hub = _li(**dict(base, no_hub=True))
    # s229: o botao "Resolver" abre a aba Listas JA na lista da tarefa (`data-hub-tarefa`)
    assert ('<a class="t-btn t-btn-prim" href="#questoes" data-hub-aba="questoes" data-hub-modo="questoes" '
            'data-hub-tarefa="9">Resolver</a>') in no_hub
    assert "exemplo/40" not in no_hub and "Abrir lista" not in no_hub and "t-alvo" not in no_hub
    sim = _li(**dict(base, area="Simulado", no_hub=True))
    assert 'data-hub-modo="simulados"' in sim
    assert painel._acao(base) == ('<a class="t-btn t-btn-prim" href="https://exemplo/40" rel="noopener noreferrer">'
                                  'Abrir lista</a>')


def test_questoes_do_dia_sao_o_ritmo_da_meta_e_nao_uma_cota_de_semana(db_sintetico):
    """s203 (decisao do operador em 27/09): a unica meta e 01/11 (10.000). O "Hoje" das questoes
    e o ritmo DELA (`performance.volume_vs_marco`, o mesmo do boot). ⚰️ *Era a cota da semana de
    calendario (`day_plan.cota_do_dia`), que no domingo despejava a semana inteira: ~474q/dia.*"""
    import performance
    from app.utils import db as dbmod
    con = dbmod.get_connection()
    try:
        vm = performance.volume_vs_marco(con, HOJE)
    finally:
        con.close()
    q = painel.coletar()["dia"]["questoes"]
    assert q["alvo_dia"] == vm["ritmo_alvo"] and q["meta"] == vm["meta"] == performance.MARCOS[0][1]
    assert q["faltam"] == vm["faltam"] and q["dias"] == vm["dias"]
    assert "cota" not in q


def test_painel_diz_um_so_por_dia_e_nenhuma_cota(db_sintetico):
    """Um alvo por dia na pagina inteira: o da meta. A Fase 1 aparece como cobertura (onde o
    acumulado chega fechando o plano), sem ritmo proprio; o Ciclo 2026 saiu."""
    html = painel.render_html(painel.coletar())
    corpo = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", html, flags=re.S)
    assert "cota" not in corpo.lower(), "a cota da semana saiu do painel"
    assert "Para fechar as listas da Fase 1" not in corpo
    assert "Ciclo 2026" not in corpo and "12.500" not in corpo
    assert "10.000" in corpo, "a meta aparece com o numero dela"


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


def test_painel_nao_conta_o_lote_de_ontem_no_saldo_de_hoje(db_sintetico, tmp_path, monkeypatch):
    """s216 (hub-integracao part-5, regra P09): um lote comecado ONTEM (1a nota as 23h40 de 22/09) e
    gravado depois da meia-noite nao come o teto de hoje -- o Painel mostra o consumo LOGICO sobre o
    teto; o cabecalho "Hoje, <data>" segue pelo relogio."""
    import day_plan
    from datetime import timezone
    brt = timezone(timedelta(hours=-3))
    _cards(db_sintetico)                                  # 2 revisoes de hoje (cards 6 e 7, 10h)
    con = sqlite3.connect(db_sintetico)
    for cid in (1, 2):                                    # o lote de ontem: 2 notas depois da meia-noite
        con.execute("INSERT INTO fsrs_revlog (card_id, rating, review_time, regua_versao) VALUES (?, 3, ?, 2)",
                    (cid, "2026-09-23 00:2%d:00" % cid))
    con.commit()
    con.close()
    sessao = "2026-09-22a"
    (tmp_path / "tmp" / "hub").mkdir(parents=True)
    (tmp_path / "tmp" / "hub" / "ultima_gravacao_hub.json").write_text(json.dumps({"sessao": sessao}), encoding="utf-8")
    notas = tmp_path / "tmp" / ("player_%s_db" % sessao) / "sessoes" / sessao / "notas"
    notas.mkdir(parents=True)
    for cid, ts in ((3, "2026-09-23T02:40:00.000Z"), (1, "2026-09-23T03:21:00.000Z"), (2, "2026-09-23T03:22:00.000Z")):
        (notas / ("%d.json" % cid)).write_text(json.dumps({"card_id": cid, "rating_primeira": 3, "ts": ts}),
                                               encoding="utf-8")
    monkeypatch.setattr(day_plan, "RAIZ_LOTES", tmp_path)
    monkeypatch.setattr(day_plan, "FUSO_LOTES", brt)
    d = painel.coletar()
    c = d["dia"]["cards"]
    assert c["consumo_hoje"] == 2, "so as 2 revisoes do dia; as 2 do lote de ontem ficam com ontem"
    assert c["restantes"] == max(0, c["teto"] - 2)
    pagina = painel.render_html(d)
    assert "Hoje, quarta 23/09" in pagina, "o cabecalho segue o relogio"


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
    # s229 (rodada 5): a MESMA agenda + `sessao` por dia (o que entrou pela ultima sessao)
    assert {**ag, "dias": [{k: v for k, v in x.items() if k != "sessao"} for x in ag["dias"]]} == esperado
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
    cron = day_plan._cronograma_hoje(vm["total"], HOJE)
    assert "alvo_fase1" not in r, "s203: a Fase 1 nao e um 2o ritmo"
    assert r["fase1_q"] == cron["restante_q"] and r["fase1_simulados_q"] == cron["simulados_q"]
    assert r["fechando_q"] == cron["fechando_q"] == vm["total"] + cron["restante_q"]
    assert r["sprint"] is None, "banco sem dia_plano: a frase segue a da Fase 1"


def _ritmo(sprint=None):
    return {"alvo_marco": 100.0, "real_7d": 50.0, "real_14d": 40.0, "faltam": 2000, "meta": 10000,
            "acerto": 80.0, "acumulado": 8000, "fase1_q": 2500, "fase1_simulados_q": 300,
            "fechando_q": 10500, "fim_fase1": "2026-11-01", "sprint": sprint}


def test_ritmo_sem_legenda_em_prosa():
    """s226 (pedido dele, 13/10): o Ritmo e o Por bloco perdem a legenda em prosa (a frase do sprint/Fase 1 e o
    'Fora da tabela'); a cobertura do sprint vai para o dashboard do topo. ⚰️ Era
    `test_ritmo_com_sprint_conta_o_sprint_e_declara_o_fora` (part-5 da sprint-final-uerj)."""
    sp = {"q": 1500, "simulados_q": 300, "fechando_q": 9500, "fim": "2026-10-31", "fora": 37, "q_fora": 997}
    for html in (painel._html_ritmo(_ritmo(sp)), painel._html_ritmo(_ritmo())):
        assert 'class="nota"' not in html and "Cumprindo o sprint" not in html and "Fechando tudo" not in html


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
    # s225: a cor vem do core/templates/tema.css embutido (fonte unica, docs/UI.md): escuro por padrao,
    # claro so por escolha explicita (data-theme) -- o painel nao repete paleta propria
    assert '<style id="medhub-tema">' in pagina
    assert ':root:not([data-theme="light"])' in pagina
    assert ':root[data-theme="dark"]' in pagina and ':root[data-theme="light"]' in pagina
    css_painel = pagina[pagina.index("<style>"):pagina.index('<style id="medhub-tema">')]
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", css_painel), "cor literal no painel: ela mora no tema.css"
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
    # s216 (part-6): o numero publicado leva a ancora do "Hoje ao vivo" (`data-vivo`/`data-base`)
    assert re.search(r"<b[^>]*>%d</b>\s*de %d" % (c["consumo_hoje"], c["teto"]), pagina)
    # ⚰️ *Ate 13/10 travava tambem a linha "faltam N" sob o anel: as legendas do dashboard sairam a pedido
    # dele ("gostaria de remover ... as legendas do dashboard"); o "X de 150" diz o saldo sozinho.*
    assert "faltam %d" % c["restantes"] not in _dash(pagina)


def test_link_da_lista_e_da_aula(db_sintetico):
    """⚰️ *Era `test_link_da_lista_e_da_aula_e_atalho_para_os_cards`: o anel Cards levava o atalho "Ir para os
    cards" (`data-hub-aba="cards"`); saiu a pedido dele em 13/10 ("gostaria de remover esse 'Ir para os
    cards'") -- a aba Cards segue no menu do hub.*"""
    pagina = _pagina()
    assert 'href="https://exemplo/5"' in pagina
    assert 'data-hub-aula="raciocinio-diagnostico"' in pagina
    assert 'data-hub-aba="cards"' not in pagina and "Ir para os cards" not in pagina
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
    modo Simulados); caminho local sem questoes segue texto, nunca link para o disco.
    s213: o modo sai da AREA (Simulado -> simulados; o resto -> questoes), por isso a `area`."""
    base = {"classe": "lista", "url_lista": "simulados/uerj/uerj_ad_2021_a.pdf", "area": "Simulado"}
    assert 'data-hub-aba="questoes" data-hub-modo="simulados" data-hub-tarefa="9">Resolver</a>' in _li(**dict(base, no_hub=True))
    assert painel._acao(dict(base, no_hub=True)).count("<a ") == 1, "no hub, so o Resolver"
    assert painel._acao(base) == '<span class="tenue">prova em PDF no computador</span>'


def test_documentacao_sai_do_painel_e_fica_no_json(db_sintetico, tmp_path, monkeypatch):
    """s229 (pedido dele, 15/10): o bloco Documentacao SAI do Painel -- as analises moram num eixo proprio da
    Biblioteca da Teoria (`hub.EIXO_DOC`). O JSON segue listando-as (o contrato do --json nao perde dado).
    ⚰️ *s212-s228: a secao "Documentação" do Painel, com "abrir documento".*"""
    import json as _json
    (tmp_path / "aula-dossie.html").write_text("<title>x</title>", encoding="utf-8")
    reg = tmp_path / "quadro.json"
    reg.write_text(_json.dumps({"itens": {
        "dossie": {"tipo": "analise", "titulo": "Dossiê da banca"},
        "sem-arquivo": {"tipo": "analise", "titulo": "Fantasma"},
        "aula-comum": {"tipo": "aula", "titulo": "Aula"}}}), encoding="utf-8")
    monkeypatch.setattr(painel, "QUADRO", reg)
    monkeypatch.setattr(painel, "ARTIFATOS", tmp_path)
    assert painel.coletar()["docs"] == [{"slug": "dossie", "titulo": "Dossiê da banca"}]
    pagina = painel.render_html(painel.coletar())
    assert 'data-bloco="docs"' not in pagina and "Documentação" not in pagina and "dossie" not in pagina


# ------------------------------------------ s216 (hub-integracao part-6, P08 v0): ancoras do "Hoje ao vivo"

def test_hoje_tem_ancoras_para_o_ao_vivo(db_sintetico, tmp_path, monkeypatch):
    """O Painel e foto do publish; a pagina soma ao lado dele o que gravou depois ("+K"). Para isso o
    numero publicado ganha ancora (`data-vivo` + `data-base`), o bloco Hoje diz QUAL lote ja esta no
    numero (`data-sessao-gravada`, do marcador do tique; vazio sem ele) e o carimbo ISO vai DENTRO do
    trecho que o hub ignora ao comparar a projecao (A14)."""
    _cards(db_sintetico)
    marcador = tmp_path / "ultima_gravacao_hub.json"
    marcador.write_text(json.dumps({"sessao": "2026-09-23a", "gravado_em": "x"}), encoding="utf-8")
    monkeypatch.setattr(painel, "MARCADOR_GRAVACAO", marcador)
    d = painel.coletar()
    pagina = painel.render_html(d)
    c, q = d["dia"]["cards"], d["dia"]["questoes"]
    assert '<b data-vivo="cards" data-base="%d">%d</b>' % (c["consumo_hoje"], c["consumo_hoje"]) in pagina
    assert '<b data-vivo="questoes" data-base="%d">%d</b>' % (q["feitas_hoje"], q["feitas_hoje"]) in pagina
    assert pagina.count('data-sessao-gravada="2026-09-23a"') == 1
    gerado = pagina.split(painel.MARCA_GERADO_ABRE, 1)[1].split(painel.MARCA_GERADO_FECHA, 1)[0]
    assert 'data-gerado-iso="%s"' % d["gerado_em"] in gerado, "o carimbo ISO mora no trecho ignorado"
    assert pagina.count("data-gerado-iso=") == 1
    monkeypatch.setattr(painel, "MARCADOR_GRAVACAO", tmp_path / "nao-existe.json")
    assert 'data-sessao-gravada=""' in painel.render_html(painel.coletar()), "sem marcador: vazio"


def test_hash_do_painel_ignora_o_carimbo_iso(db_sintetico):
    """A14: regenerar o painel a cada tique so com o carimbo novo NAO pode virar `mesmo_lote`."""
    from tools import hub
    d = painel.coletar()
    a = painel.render_html(d)
    b = painel.render_html(dict(d, gerado_em="2026-09-23T18:47:00"))
    assert a != b and hub.hash_painel(a) == hub.hash_painel(b)


# ------------------------------------------ P20 (s219): a tarefa na tela, uma regra com a Teoria

#: questoes no banco do hub (`emed_questoes`) por tarefa do cenario: a #7 (Raciocinio, custom de aula,
#: `q_previstas` 0) ganhou caderno de 15; a #5 (HAS, 60 previstas) tem 55 no hub + 2 spoilers UERJ 2022
#: (ficam no banco, fora do hub); a #11 (Puericultura, S4, 0 previstas) ganhou 12.
HUPE = "RJ - Universidade do Estado do Rio de Janeiro - UERJ (Hospital Universitário Pedro Ernesto - HUPE)"
NO_BANCO = [(7, 15, "SES-DF 2024"), (5, 55, "SES-DF 2024"), (5, 2, HUPE + ", 2022"), (11, 12, "SES-DF 2024")]


def _com_banco(caminho):
    con = sqlite3.connect(caminho)
    con.execute("CREATE TABLE emed_questoes (id INTEGER PRIMARY KEY AUTOINCREMENT, lista TEXT, tarefa_id INTEGER,"
                " num INTEGER, banca TEXT, executor TEXT)")
    nums = {}
    for tarefa, n, banca in NO_BANCO:
        for _ in range(n):
            nums[tarefa] = nums.get(tarefa, 0) + 1
            con.execute("INSERT INTO emed_questoes (lista, tarefa_id, num, banca, executor) VALUES (?,?,?,?,?)",
                        ("t%d" % tarefa, tarefa, nums[tarefa], banca, "emed_api"))
    con.commit()
    con.close()


def test_teoria_painel_e_boot_contam_o_banco_do_hub(db_sintetico, capsys, monkeypatch):
    """P20 item 6 (s219): 26 tarefas ganharam caderno no hub com `q_previstas` 0 (ou 20/60), e o
    "Questoes da semana" da Teoria e o Painel contavam menos que a aba Listas. Uma funcao so
    (`plano.q_da_tarefa` sobre `plano.com_q_hub`): a contagem do banco -- pelo criterio do
    `--exportar`, sem o spoiler -- quando a tarefa tem questoes la; senao `q_previstas`. A Teoria, o
    Painel, o boot (`plano.py --panorama`) e a Fase 1 do `day_plan` dizem o MESMO numero."""
    import day_plan
    import emed_api
    import plano
    from tools import hub
    # ⚰️ o filtro spoiler UERJ foi revogado em 15/10/2026 (s229); religado aqui so para o cenario
    monkeypatch.setattr(emed_api, "ANOS_SPOILER_UERJ", frozenset(range(2022, 2027)))
    _com_banco(db_sintetico)
    d = painel.coletar()
    s = d["semana"]
    t = {x["id"]: x for x in s["tarefas"]}
    assert (t[5]["q"], t[7]["q"], t[1]["q"]) == (55, 15, 32), "banco sem spoiler; fora do banco, o previsto"
    assert t[7]["no_hub"] and t[5]["no_hub"] and not t[1]["no_hub"]
    assert s["q"] == 32 + 40 + 55 + 60 + 15
    assert {r["semana"]: r["q"] for r in s["rota"]} == {3: 45, 4: 25 + 12}
    # o boot
    assert plano.main(["--panorama", "--json"]) == 0
    pan = json.loads(capsys.readouterr().out)
    assert pan["q_abertas"] == s["q"] and [r["q"] for r in pan["rota"]] == [r["q"] for r in s["rota"]]
    cron = day_plan._cronograma_hoje(0, HOJE)
    assert cron["restante_q"] == pan["fase1"]["q"] == d["ritmo"]["fase1_q"], "a Fase 1 do boot e do Painel"
    # a Teoria: a MESMA leitura do plano (`hub._ler_plano`) e a MESMA regua
    linhas, aviso = hub._ler_plano()
    assert aviso is None
    secoes, _b, _a = hub.secoes_do_quadro([], plano_linhas=linhas, calendario=dict(CALENDARIO), hoje=HOJE)
    q = {x["chave"]: (x["q_plano"], x["q_com_atrasadas"]) for x in secoes}
    assert q["2"][1] == s["q"] and q["4"][0] == 37, "a S3 so tem lista sem aula: fora da Teoria"
    teoria = {i["id"]: i["q"] for x in secoes for i in x["itens"]}
    assert teoria[7] == t[7]["q"] == 15 and teoria[11] == 12
    pagina = painel.render_html(d)
    li7 = re.search(r'<li class="tarefa" data-tarefa="7">.*?</li>', pagina, re.S).group(0)
    assert '<span class="t-n">15 questões</span>' in li7 and ">Resolver</a>" in li7 and ">Abrir aula</a>" in li7


def test_meta_e_acao_da_tarefa_no_painel_seguem_a_regra_da_teoria():
    """P20 item 3/4: o Painel e a Teoria falam a MESMA lingua (`plano.meta_da_tarefa`): N questoes
    quando ha questoes; a classe so sem acao nenhuma, em texto apagado da meta -- nunca na coluna de
    acao. s229: o cartao -- a meta (chip + contagem) em cima, os botoes no pe; sem acao, sem pe."""
    def t(**kw):
        base = {"id": 9, "semana": 4, "atrasada": False, "tema": "Tema", "q": 0, "classe": "sem_lista",
                "url_lista": None, "area": "Cirurgia", "rotulo": "CIR", "aula": None, "aulas": [],
                "no_hub": False}
        base.update(kw)
        return painel._html_tarefa(base)
    sem_nada = t()
    assert '<p class="t-meta"><span class="t-rot">CIR</span><span class="t-n">sem lista ainda</span></p>' in sem_nada
    assert "t-acao" not in sem_nada and "tenue" not in sem_nada
    aula = t(classe="aula")
    assert '<span class="t-n">aula a preparar</span>' in aula and "t-acao" not in aula
    remit = t(q=20, no_hub=True, aula="remit", aulas=[{"slug": "remit", "titulo": "REMIT"}],
              tema="Resposta Endócrino- | Metabólica-Inflamatória ao Trauma | Cicatrização de Feridas")
    assert '<span class="t-n">20 questões</span>' in remit and "sem lista" not in remit
    assert ('<p class="t-acao"><a class="t-btn t-btn-prim" href="#questoes" data-hub-aba="questoes" '
            'data-hub-modo="questoes" data-hub-tarefa="9">Resolver</a><a class="t-btn" href="aulas/remit.html" '
            'data-hub-aula="remit" data-titulo="REMIT">Abrir aula</a></p></li>') in remit
    assert '<p class="t-tema">Resposta Endócrino-Metabólica-Inflamatória ao Trauma · Cicatrização de Feridas</p>' in remit
    caderno = t(classe="caderno", q=43)
    assert '<span class="t-n">43 questões</span><span class="t-n">caderno a montar</span>' in caderno
    assert "t-acao" not in caderno, "a classe nunca mais na coluna de acao"


# ------------------------------------------ s226 (part-3): a Semana no padrao da Teoria (P21)

def _li(**kw):
    base = {"id": 9, "semana": 4, "atrasada": False, "tema": "Tema", "q": 20, "classe": "lista",
            "url_lista": None, "area": "Cirurgia", "rotulo": "CIR", "aula": None, "aulas": [],
            "no_hub": False}
    base.update(kw)
    return painel._html_tarefa(base)


def _semana(tarefas):
    return painel._html_semana({"semana": 4, "inicio": None, "fim": None, "dias": None, "tarefas": tarefas,
                                "total": len(tarefas), "q": 0, "atrasadas": sum(t["atrasada"] for t in tarefas),
                                "rota": [], "proxima": None})


def _t(i, **kw):
    base = {"id": i, "semana": 4, "atrasada": False, "tema": "Tema %d" % i, "q": 20, "classe": "lista",
            "url_lista": None, "area": "Cirurgia", "rotulo": "CIR", "aula": None, "aulas": [], "no_hub": True}
    base.update(kw)
    return base


def test_cartao_da_tarefa_tem_resolver_e_abrir_aula():
    """s229 (pedido dele, 15/10): a seta ">" (a linha inteira como alvo das Listas, P21) vira o BOTAO "Resolver"
    (primario, ciano cheio) que abre a aba Listas JA na lista da tarefa; o link "abrir aula" vira o botao
    "Abrir aula" (contorno ciano) que leva a Teoria ja naquela aula. O `<li>` segue a raiz com `data-tarefa`."""
    html_ = _semana([_t(1, aulas=[{"slug": "remit", "titulo": "REMIT"}]), _t(2),
                     _t(3, no_hub=False, url_lista="https://exemplo/3")])
    assert "t-alvo" not in html_ and "resolver no hub" not in html_
    li1 = re.search(r'<li class="tarefa[^"]*" data-tarefa="1">(.*?)</li>', html_, re.S).group(1)
    assert li1 == ('<i class="t-faixa" data-area="CIR" aria-hidden="true"></i><p class="t-meta"><span class="t-rot">CIR</span><span class="t-n">20 questões</span></p>'
                   '<p class="t-tema">Tema 1</p><p class="t-acao"><a class="t-btn t-btn-prim" href="#questoes" '
                   'data-hub-aba="questoes" data-hub-modo="questoes" data-hub-tarefa="1">Resolver</a>'
                   '<a class="t-btn" href="aulas/remit.html" data-hub-aula="remit" data-titulo="REMIT">Abrir aula</a></p>')
    li3 = re.search(r'<li class="tarefa[^"]*" data-tarefa="3">(.*?)</li>', html_, re.S).group(1)
    assert '<a class="t-btn t-btn-prim" href="https://exemplo/3" rel="noopener noreferrer">Abrir lista</a>' in li3
    assert ([int(i) for i in re.findall(r'<li class="tarefa[^"]*" data-tarefa="(\d+)">', html_)] == [1, 2, 3])
    css = painel.CSS
    assert "min-height:44px" in re.search(r"\n\.t-btn\{([^}]*)\}", css).group(1)
    assert ".t-alvo" not in css and "content:\"›\"" not in css, "a seta saiu"


def test_atrasadas_sob_subtitulo_unico():
    """P21: o atraso aparece UMA vez, no subtitulo "Atrasadas · N"; nenhuma linha diz "da semana N"
    e o resumo nao repete. As da semana vem depois, sob o proprio subtitulo; ordem do plano intacta."""
    html_ = _semana([_t(1, semana=2, atrasada=True), _t(2, semana=3, atrasada=True), _t(3), _t(4)])
    assert html_.count("Atrasadas · 2") == 1
    assert "da semana" not in html_ and "t-atraso" not in html_ and "vêm atrasadas" not in html_
    assert html_.index("Atrasadas · 2") < html_.index('data-tarefa="1"') < html_.index("Desta semana · 2") \
        < html_.index('data-tarefa="3"')
    sem_atraso = _semana([_t(3), _t(4)])
    assert "Atrasadas" not in sem_atraso and "Desta semana" not in sem_atraso
    # a vista: todas as atrasadas e as primeiras da semana ate VISIVEIS_SEMANA; o resto recolhido
    muitas = _semana([_t(i, atrasada=i < 3) for i in range(1, 12)])
    vista = muitas.split('<details class="mais">')[0]
    assert vista.count('<li class="tarefa') == painel.VISIVEIS_SEMANA
    assert 'Ver as outras %d' % (11 - painel.VISIVEIS_SEMANA) in muitas
    assert 'start="%d"' % (painel.VISIVEIS_SEMANA - 2 + 1) in muitas


def test_proxima_so_pelo_rotulo_sem_botao_cheio(db_sintetico):
    """P21: a Proxima e a 1a tarefa da semana e se distingue pelo rotulo "Proxima" -- os botoes sao os mesmos
    das outras (s229: o "Resolver" e cheio em TODA tarefa, nao so na Proxima)."""
    html_ = _semana([_t(1, semana=2, atrasada=True), _t(2), _t(3)])
    assert re.findall(r'<li class="([^"]*)" data-tarefa="(\d+)">', html_) == [
        ("tarefa atrasada proxima", "1"), ("tarefa", "2"), ("tarefa", "3")]
    css = painel.CSS
    assert ".tarefa.proxima .t-tema::before{content:\"Próxima\"" in css
    assert ":first-child .t-acao" not in css and ".proxima .t-btn" not in css, "so a Proxima com botao cheio"
    pagina = _pagina()
    assert pagina.count('class="tarefa proxima"') + pagina.count('class="tarefa atrasada proxima"') == 1


# ------------------------------- s226 (sprint-final-uerj part-3): Hoje · Proximos dias · Fora do sprint

def _com_sprint(caminho):
    """O banco sintetico com o sprint gravado: a #1 de ontem (rolou), a #3 hoje, a #5 amanha, o
    simulado (#6) depois de amanha, a #8 fora com o motivo; a #2 (feita) com dia nao entra."""
    con = sqlite3.connect(caminho)
    con.execute("ALTER TABLE plano_tarefas ADD COLUMN dia_plano TEXT")
    for tid, dia in ((1, "2026-09-22"), (3, "2026-09-23"), (5, "2026-09-24"), (6, "2026-09-25"),
                     (2, "2026-09-23")):
        con.execute("UPDATE plano_tarefas SET dia_plano = ? WHERE id = ?", (dia, tid))
    con.execute("UPDATE plano_tarefas SET nota = 'sprint: fora (sem vaga ate 31/10 (80 q/dia))' WHERE id = 8")
    con.commit()
    con.close()


def test_painel_sprint_sem_semana(db_sintetico, tmp_path, monkeypatch):
    """DoD 2-4 + s229 (pedido dele, 15/10: "'Plano de hoje' + 'Proximos dias' vira 'Roadmap': todos os dias
    expandidos"): com sprint, o bloco da semana vira o ROADMAP -- Hoje (rolada + a de hoje) e cada dia seguinte,
    um bloco SEMPRE aberto com a contagem; Fora do sprint segue recolhido, com o motivo. Some a semana, as
    atrasadas e a rota; o `li.tarefa[data-tarefa]` segue (o hub pinta por ele)."""
    monkeypatch.setattr(painel, "QUADRO", tmp_path / "nao-existe.json")
    _com_sprint(db_sintetico)
    d = painel.coletar()
    s = d["sprint"]
    assert [t["id"] for t in s["hoje"]] == [1, 3] and s["q_hoje"] == 72
    assert [p["data"] for p in s["proximos"]] == ["2026-09-24", "2026-09-25"]
    assert [(t["id"], t["motivo"]) for t in s["fora"]] == [(8, "sem vaga ate 31/10 (80 q/dia)")]
    pagina = painel.render_html(d)
    for proibido in ("Atrasadas", "Desta semana", "Semana ", "Até a prova", 'class="tarefa atrasada',
                     'class="t-grupo atrasadas"', "Plano de hoje", "Próximos dias"):
        assert proibido not in pagina, proibido
    i = pagina.index('data-bloco="semana"')
    bloco = pagina[i:pagina.index("</section>\n", pagina.index("Fora do sprint", i))]
    assert "<h2>Cronograma</h2>" in bloco
    assert re.search(r'<p class="sub">Hoje: 2&nbsp;tarefas · 72&nbsp;questões( \+ \d+&nbsp;cards?)?\.</p>', bloco)
    hoje_html = bloco[bloco.index('<section class="rm-dia hoje">'):]
    hoje_html = hoje_html[:hoje_html.index("</section>")]
    assert '<span class="rm-d">Hoje · qua 23/09</span> <span class="rm-n">2&nbsp;listas · 72&nbsp;q</span>' in hoje_html
    assert re.findall(r'<li class="([^"]*)" data-tarefa="(\d+)">', hoje_html) == [
        ("tarefa proxima", "1"), ("tarefa", "3")], "a rolada sem rotulo de atraso"
    assert '<span class="rm-d">qui 24/09</span> <span class="rm-n">1&nbsp;lista · 60&nbsp;q</span>' in bloco
    assert '<span class="rm-d">sex 25/09</span> <span class="rm-n">1&nbsp;simulado · 60&nbsp;q</span>' in bloco
    assert bloco.count('<section class="rm-dia') == 3, "Hoje e os dois dias, um bloco cada"
    assert '<details class="rota-sem"' not in bloco, "nenhum dia recolhido"
    assert '<details class="rota-sem fora"><summary><span class="rota-tit">Fora do sprint · 1</span>' in bloco
    assert "sem vaga até 31/10 (80 q/dia) · 1" in bloco
    assert 'data-tarefa="8"' in bloco and "<details open" not in bloco, "fora recolhido"


def test_hoje_do_sprint_soma_os_cards_do_dia_e_a_rd_nao_assinada(db_sintetico, tmp_path, monkeypatch):
    """O Hoje diz "+ N cards" (o que falta da dose do dia) e traz a RD NAO assinada mais antiga, a
    linha inteira abrindo o leitor; a assinada (estado do quadro) e a sem arquivo nao entram."""
    _com_sprint(db_sintetico)
    reg = tmp_path / "quadro.json"
    reg.write_text(json.dumps({"itens": {
        "rd-velha": {"tipo": "revisao", "titulo": "RD velha"},
        "rd-nova": {"tipo": "revisao", "titulo": "RD nova"},
        "rd-lida": {"tipo": "revisao", "titulo": "RD lida"},
        "rd-sem-arquivo": {"tipo": "revisao", "titulo": "Sem arquivo"},
        "aula-x": {"tipo": "aula", "titulo": "Aula"}}}), encoding="utf-8")
    for slug in ("rd-velha", "rd-nova", "rd-lida", "aula-x"):
        (tmp_path / ("aula-%s.html" % slug)).write_text("<title>x</title>", encoding="utf-8")
    estado = tmp_path / "estado"
    estado.mkdir()
    (estado / "rd-lida.json").write_text('{"feito": true}', encoding="utf-8")
    datas = {"rd-velha": "2026-09-01", "rd-nova": "2026-09-20", "rd-lida": "2026-08-01", "aula-x": "2026-07-01"}
    monkeypatch.setattr(painel, "QUADRO", reg)
    monkeypatch.setattr(painel, "ARTIFATOS", tmp_path)
    monkeypatch.setattr(painel, "QUADRO_ESTADO", estado)
    monkeypatch.setattr(painel, "_datas_das_aulas", lambda ps: {p: datas[Path(p).stem[5:]] for p in ps})
    d = painel.coletar()
    assert d["sprint"]["rd"] == {"slug": "rd-velha", "titulo": "RD velha", "data": "2026-09-01"}
    bloco = painel._html_sprint(d["sprint"], {"consumo_hoje": 10, "restantes": 40, "teto": 50})
    assert "72&nbsp;questões + 40&nbsp;cards." in bloco
    # s229: o cartao da RD -- o estado num span SO (`t-rd-st`, que o hub reescreve ao vivo) e o botao
    assert ('<li class="tarefa rd"><i class="t-faixa" data-area="RD" aria-hidden="true"></i><p class="t-meta"><span class="t-rot">RD</span><span class="t-rd-st">revisão '
            'direcionada ainda não assinada</span></p><p class="t-tema">RD velha</p><p class="t-acao"><a class="t-btn" '
            'href="aulas/rd-velha.html" data-hub-aula="rd-velha" data-titulo="RD velha">Abrir aula</a></p></li>') in bloco
    sem_contador = painel._html_sprint(dict(d["sprint"], rd=None), {"consumo_hoje": None, "restantes": None,
                                                                   "teto": 100})
    assert "+ 100&nbsp;cards." in sem_contador and "tarefa rd" not in sem_contador
    assert "cards" not in painel._html_sprint(d["sprint"], {"consumo_hoje": 50, "restantes": 0, "teto": 50})


def test_sem_estado_do_quadro_o_painel_nao_afirma_rd_nao_assinada(tmp_path, monkeypatch):
    """s226 (part-4, audit da part-3): sem a pasta do estado do quadro, a assinatura e DESCONHECIDA --
    o Hoje nao mostra RD nenhuma (antes, toda RD com arquivo virava "nao assinada")."""
    reg = tmp_path / "quadro.json"
    reg.write_text(json.dumps({"itens": {"rd-a": {"tipo": "revisao", "titulo": "RD A"}}}), encoding="utf-8")
    (tmp_path / "aula-rd-a.html").write_text("<title>x</title>", encoding="utf-8")
    monkeypatch.setattr(painel, "QUADRO", reg)
    monkeypatch.setattr(painel, "ARTIFATOS", tmp_path)
    monkeypatch.setattr(painel, "QUADRO_ESTADO", tmp_path / "nao-existe")
    monkeypatch.setattr(painel, "_datas_das_aulas", lambda ps: {p: "2026-09-01" for p in ps})
    assert painel._rd_nao_assinada() is None
    estado = tmp_path / "estado"
    estado.mkdir()
    monkeypatch.setattr(painel, "QUADRO_ESTADO", estado)
    assert painel._rd_nao_assinada()["slug"] == "rd-a", "com o estado (vazio), a RD e nao assinada"


def test_datas_das_aulas_numa_chamada_so_de_git(tmp_path, monkeypatch):
    """s226 (part-4): as datas das candidatas saem de UM `git log` (era um `--follow` por aula); a
    1a entrada no git (a mais velha) vence; fora do log, a data do arquivo."""
    chamadas = []

    class Saida:
        returncode = 0
        stdout = "@@2026-09-20\n\nartifacts/aula-b.html\n@@2026-09-01\n\nartifacts/aula-a.html\nartifacts/aula-b.html\n"

    def falso(cmd, **kw):
        chamadas.append(cmd)
        return Saida()
    monkeypatch.setattr(painel, "ROOT", tmp_path)
    monkeypatch.setattr(painel.subprocess, "run", falso)
    (tmp_path / "artifacts").mkdir()
    arqs = [tmp_path / "artifacts" / n for n in ("aula-a.html", "aula-b.html", "aula-c.html")]
    for a in arqs:
        a.write_text("x", encoding="utf-8")
    datas = painel._datas_das_aulas(arqs)
    assert len(chamadas) == 1 and "--follow" not in chamadas[0]
    assert datas[arqs[0]] == "2026-09-01" and datas[arqs[1]] == "2026-09-01"
    assert datas[arqs[2]] == date.today().isoformat(), "fora do log = a data do arquivo"


def test_sem_sprint_o_painel_mostra_a_semana_antiga(db_sintetico):
    """Degradacao declarada: `dia_plano` todo NULL (ou banco sem a coluna) = o bloco antigo."""
    d = painel.coletar()
    assert d["sprint"] is None
    assert "Semana 2 do plano" in painel.render_html(d)


# ------------------------------- s226 (painel-dashboard-sprint part-1): dashboard no topo, uma meta na tela

def _dash(pagina):
    """O dashboard: a secao `data-bloco="dia"` inteira (Hoje, Ritmo, Ate 01/11, Por bloco, Revisoes)."""
    i = pagina.index('data-bloco="dia"')
    return pagina[i:pagina.index("</section>", i)]


def _visivel(trecho):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", trecho))


def test_dashboard_questoes_usa_o_q_hoje_do_sprint(db_sintetico, tmp_path, monkeypatch):
    """DoD 2: com sprint, o tile Questoes = feitas de `q_hoje` (o MESMO `plano.agenda_sprint` do Plano de
    hoje e do boot) e o Ritmo compara o real de 7 dias com a `capacidade_q` do sprint; "por dia ate a
    prova" e o `alvo_marco` nao aparecem; nenhuma legenda em prosa (`p.nota`) no dashboard.
    s227 (tema v4 part-5): o anel do Ritmo herdou o `data-bloco="ritmo"`; ⚰️ *o grafico de previsao se
    chamava "Revisões nos próximos 7 dias" e a meta aparecia como o alvo da barra de projecao* -- agora
    "Flashcards da semana" e a meta, uma vez, no valor do anel Ate 01/11."""
    import plano
    monkeypatch.setattr(painel, "QUADRO", tmp_path / "nao-existe.json")
    monkeypatch.setattr(plano, "ler_sprint", lambda caminho=None: {"capacidade_q": 80, "fim": "2026-10-31"})
    _com_sprint(db_sintetico)
    d = painel.coletar()
    from app.utils import db as dbmod
    ag = plano.agenda_sprint(plano.linhas_com_q_hub(dbmod.plano_listar()), HOJE)
    assert d["dia"]["questoes"]["q_hoje"] == d["sprint"]["q_hoje"] == ag["q_hoje"] == 72
    assert d["ritmo"]["sprint"]["capacidade_q"] == 80
    pagina = painel.render_html(d)
    dash = _dash(pagina)
    feitas = d["dia"]["questoes"]["feitas_hoje"]
    assert '<b data-vivo="questoes" data-base="%d">%s</b> de 72</p>' % (feitas, painel._n(feitas)) in dash
    assert "por dia até a" not in pagina and "~" not in _visivel(dash)
    assert painel._n(d["ritmo"]["alvo_marco"], 1) not in _visivel(dash), "o por-dia da meta sumiu da tela"
    rotulo = "abaixo de 80/dia" if d["ritmo"]["real_7d"] < 80 else "em dia"
    assert rotulo in dash
    assert 'class="nota"' not in dash
    for chave in ("ritmo", "blocos"):
        assert 'data-bloco="%s"' % chave in dash, "Ritmo e Por bloco moram dentro do dashboard"
    assert "Flashcards da semana" in dash and 'class="ag-barras"' in dash
    assert _visivel(dash).count("10.000") == 1, "a meta aparece UMA vez, no valor do anel Ate 01/11"


def test_dashboard_sem_sprint_volta_a_meta(db_sintetico):
    """DoD 2 (sem sprint): o comportamento de antes -- Questoes contra o ritmo da meta, o Ritmo com o
    por-dia ate a prova; sem o 2o arco do sprint; e ainda sem `p.nota` dentro do dashboard."""
    import math
    d = painel.coletar()
    assert d["sprint"] is None and d["dia"]["questoes"]["q_hoje"] is None
    dash = _dash(painel.render_html(d))
    alvo = d["dia"]["questoes"]["alvo_dia"]
    assert "de ~%s" % painel._n(math.ceil(alvo)) in dash
    # s227 (sem legendas, 13/10): o necessario por dia vai no valor do Ritmo ("X de N por dia") e no aria-label;
    # ⚰️ *era a linha "N por dia até a prova de 01/11" sob o anel*
    assert "de %s por dia" % painel._n(d["ritmo"]["alvo_marco"], 1) in _visivel(dash)
    assert "necessário até a prova: %s/dia" % painel._n(d["ritmo"]["alvo_marco"], 1) in dash
    assert "por dia até a prova de 01/11" not in dash
    assert "proj-barra" not in dash and "an-sp" not in dash and 'class="nota"' not in dash


def _r_aneis(real_7d=35.4, capacidade=80, sprint=True, acumulado=7817, fechando=9306):
    """O `ritmo` do coletar (o que os aneis Ritmo e Ate 01/11 leem), com os numeros de 13/10."""
    sp = ({"q": 1489, "simulados_q": 297, "fechando_q": fechando, "fim": "2026-10-31", "fora": 37, "q_fora": 997,
           "capacidade_q": capacidade} if sprint else None)
    return {"real_7d": real_7d, "real_14d": 23.5, "alvo_marco": 114.9, "faltam": 10000 - acumulado,
            "dias_marco": 19, "meta": 10000, "acerto": 78.4, "acumulado": acumulado, "sprint": sp}


#: um arco do anel: classe, o % no `stroke-dasharray` (`pathLength="100"`)
RE_ARCO = (r'<circle class="an-arco (an-[a-z]+)" cx="60" cy="60" r="%d" pathLength="100" '
           r'stroke-dasharray="(\d+) 100" transform="rotate\(-90 60 60\)"><title>' % painel.ANEL_R)


def _centro(html_):
    return re.search(r'<text class="an-pct"[^>]*>(\d+|--)', html_).group(1)


def test_ate_01_11_anel_com_projecao_do_sprint():
    """DoD 2 (s227, tema v4 part-5): o Ate 01/11 e um anel em `--roxo` -- o feito contra a meta, com um 2o arco
    MAIS CLARO no mesmo anel, por baixo, ate onde o acumulado chega cumprindo o sprint; o % do feito no
    centro; a meta 10.000 UMA vez, no valor "7.817 de 10.000"; o 9.306 e o fora 997 na dica do 2o arco e no
    texto alternativo. ⚰️ *Era `test_barra_de_projecao_feito_sprint_meta`: a placa "Até 01/11" com a barra
    `.proj-barra` (feito | cumprindo o sprint | fora do sprint) -- saiu no pedido dele de 13/10 ("Esses 4
    blocos deveriam aparecer junto no topo, através desses anéis com percentual").* ⚰️ *Ate 13/10 (part-5)
    travava tambem a legenda "cumprindo o sprint: 9.306 · fora: 997 q" (com a bolinha `.sw-sp`) sob o valor:
    saiu com as legendas do dashboard (pedido dele, 13/10).*"""
    html_ = painel._html_ate(_r_aneis(), "2026-11-01")
    assert "<h3>Até 01/11</h3>" in html_
    assert re.findall(RE_ARCO, html_) == [("an-sp", "93"), ("an-meta", "78")], "o 2o arco por BAIXO do feito"
    assert _centro(html_) == "78"
    vis = _visivel(html_)
    assert "7.817 de 10.000" in vis and vis.count("10.000") == 1
    assert html_.endswith('<h3>Até 01/11</h3><p class="an-val"><b>7.817</b> de 10.000</p></div>\n'), "so o valor"
    assert "<title>cumprindo o sprint até 31/10: 9.306</title>" in html_, "a dica do 2o arco"
    alt = re.search(r'role="img" aria-label="([^"]+)"', html_).group(1)
    for n in ("7.817", "10.000", "9.306", "997"):
        assert n in alt, n
    assert "sw-sp" not in html_ and "kpi-r" not in html_ and "fora: 997 q" not in vis
    css = painel.CSS
    assert ".sw-sp" not in css and ".kpi-r" not in css
    assert ".an-arco.an-meta{stroke:var(--roxo)}" in css
    assert ".an-arco.an-sp{stroke:var(--roxo);stroke-opacity:.5}" in css, "o mesmo roxo, mais claro"
    assert "horizonte" not in css, "o --horizonte nao vira cor de dado"
    for morto in (".proj-barra", ".p-fora", ".p-sprint", ".rb{", ".rb-"):
        assert morto not in css, morto
    # o sprint passa da meta: o 2o arco fecha o anel; o centro segue o feito
    passa = painel._html_ate(_r_aneis(fechando=10200), "2026-11-01")
    assert re.findall(RE_ARCO, passa) == [("an-sp", "100"), ("an-meta", "78")]
    # sem sprint: so o feito e o que falta (o por-dia mora no Ritmo)
    sem = painel._html_ate(_r_aneis(sprint=False), "2026-11-01")
    assert re.findall(RE_ARCO, sem) == [("an-meta", "78")] and "sw-sp" not in sem
    assert "faltam 2.183 em 19 dias" not in _visivel(sem), "sem legenda"
    assert "faltam 2.183 em 19 dias" in re.search(r'aria-label="([^"]+)"', sem).group(1), "o que falta, no alt"


def test_por_bloco_em_linhas_com_barra_e_o_mais_fraco_rotulado():
    """DoD 4: uma linha por bloco com a barra de acerto (0-100%) e feitas/total; o de MENOR acerto leva
    "mais fraco" (nao so a cor); Simulados na ultima linha e fora da disputa; a `<table>` some e a nota
    "Fora da tabela" nao volta."""
    b = {"blocos": {"CIR": {"tarefas": 102, "feitas": 26, "q_feitas": 937, "acerto": 77.9},
                    "CM": {"tarefas": 351, "feitas": 67, "q_feitas": 2585, "acerto": 77.2},
                    "PED": {"tarefas": 117, "feitas": 31, "q_feitas": 926, "acerto": None}},
         "simulados": {"tarefas": 9, "feitas": 3, "q_feitas": 1150, "acerto": 69.1}, "sem_bloco": {}}
    html = painel._html_blocos(b)
    assert "<table" not in html and "Fora da tabela" not in html
    linhas = re.findall(r'<li class="(bl[^"]*)"[^>]*><span class="bl-nome">([^<]+)', html)
    assert linhas == [("bl", "CIR"), ("bl fraco", "CM"), ("bl", "PED"), ("bl sim", "Simulados")]
    assert html.count("mais fraco") == 1 and '<span class="bl-tag">mais fraco</span>' in html
    assert '<i style="width:77.2%"></i></span><span class="bl-pct">77,2%</span><span class="bl-t">67/351</span>' in html
    assert '<span class="bl-pct">--</span><span class="bl-t">31/117</span>' in html, "sem questao: sem acerto"


# ------------------------------- s227 (hub-tema-v4 part-5): o Painel compacto, quatro aneis no topo

def _dia_aneis(feitas=31, q_hoje=76, consumo=52, teto=150):
    return {"questoes": {"feitas_hoje": feitas, "alvo_dia": 114.9, "meta": 10000, "faltam": 2183, "dias": 19,
                         "data_meta": "2026-11-01", "q_hoje": q_hoje},
            "cards": {"vencidos": 176, "novos": 733, "teto": teto, "consumo_hoje": consumo,
                      "restantes": None if consumo is None else max(0, teto - consumo),
                      "retencao_7d": {"retencao": 0.891}}, "sessao_gravada": ""}


def _itens(html_):
    """Os aneis do topo: (data-bloco, aria-label, miolo do SVG, rotulo, valor). s227 (13/10): o anel FECHA logo
    depois do valor (`</p></div>`) -- nenhuma legenda nem link sob ele."""
    return re.findall(r'<div class="an4"( data-bloco="[a-z]+")?><svg class="anel" viewBox="0 0 120 120" role="img" '
                      r'aria-label="([^"]+)">(.*?)</svg><h3>([^<]+)</h3><p class="an-val">((?:(?!</p>).)*)</p></div>\n',
                      html_, re.S)


def test_topo_quatro_aneis():
    """DoD 2 (s227, tema v4 part-5, pedido dele: "o 'Painel' ainda está muito disperso. Esses 4 blocos deveriam
    aparecer junto no topo, através desses anéis com percentual"): UMA placa "Hoje, <dia>" com QUATRO aneis em
    SVG inline -- Questoes (`--acento`), Cards (`--rosa`), Ritmo (cor de estado) e Ate 01/11 (`--roxo`) --, cada
    um com trilho `--trilho`, `pathLength="100"`, o % no centro e, abaixo, o rotulo e o valor; `role="img"` com
    os numeros no `aria-label`. Cada anel contra a PROPRIA meta: nenhum numero soma unidades. As ancoras do
    "Hoje ao vivo" ficam nos valores de Questoes e Cards (o anel fica no publicado); o `data-bloco="ritmo"` vai
    para o anel do Ritmo. 2 x 2 no celular, 4 em linha a partir de 760 px (ja de 600). Sem o ritmo, so os dois
    do dia. ⚰️ *Era `test_hoje_dois_aneis_sem_soma` (part-2): dois aneis concentricos (questoes por fora, cards
    por dentro, o dia no centro), com o Ritmo e o Ate 01/11 em placas proprias abaixo.*
    s227 (pedido dele, 13/10: "gostaria de remover esse 'Ir para os cards', bem como as legendas do dashboard"):
    sob cada anel so o rotulo e UMA linha de valor -- 31 de 76, 52 de 150, 35,4 de 80 por dia, 7.817 de 10.000.
    ⚰️ *Ate 13/10 travava as linhas `kpi-r` ("faltam 45", "faltam 98", "176 vencidos · 733 novos", "retenção
    89,1%", "abaixo de 80/dia", "23,5 em 14 dias · 78,4% de acerto", "cumprindo o sprint: 9.306 · fora: 997 q")
    e o link "Ir para os cards".*"""
    html_ = painel._html_dia(_dia_aneis(), "2026-10-13", _r_aneis())
    assert html_.startswith('<div class="placa dash-hoje">\n<h2>Hoje, terça 13/10</h2>\n<div class="aneis4" '
                            'data-sessao-gravada="">')
    itens = _itens(html_)
    assert [i[3] for i in itens] == ["Questões", "Cards", "Ritmo em 7 dias", "Até 01/11"]
    assert [i[0] for i in itens] == ["", "", ' data-bloco="ritmo"', ""], "o Ritmo herdou o data-bloco"
    assert [re.findall(RE_ARCO, i[2]) for i in itens] == [
        [("an-q", "40")], [("an-c", "34")], [("an-abaixo", "44")], [("an-sp", "93"), ("an-meta", "78")]]
    assert [_centro(i[2]) for i in itens] == ["40", "34", "44", "78"]
    assert all(i[2].count('<circle class="an-trilho" cx="60" cy="60" r="%d"/>' % painel.ANEL_R) == 1 for i in itens)
    assert [i[1] for i in itens[:2]] == ["Questões: 31 de 76 (40%).", "Cards: 52 de 150 (34%)."]
    # os valores: X de Y, com as ancoras do ao vivo (o hub poe o "+K" ao lado; o anel fica no publicado)
    assert itens[0][4] == '<b data-vivo="questoes" data-base="31">31</b> de 76'
    assert itens[1][4] == '<b data-vivo="cards" data-base="52">52</b> de 150'
    assert html_.count("data-vivo=") == 2 and not any("data-vivo" in i[2] for i in itens)
    assert [i[4] for i in itens[2:]] == ["<b>35,4</b> de 80 por dia", "<b>7.817</b> de 10.000"]
    assert html_.count('<div class="an4"') == 4 == len(itens), "cada anel fecha logo depois do valor"
    vis = _visivel(html_)
    for morto in ("faltam", "vencidos", "novos", "retenção", "Ir para os cards", "em 14 dias", "de acerto",
                  "fora: 997"):
        assert morto not in vis, morto
    for morto in ("kpi-r", "an-estado", "sw-sp", 'class="ir"', "data-hub-aba", "<a "):
        assert morto not in html_, morto
    assert vis.count("10.000") == 1, "a meta uma vez, no valor do anel Ate 01/11"
    numeros = set(re.findall(r"\d+", vis.replace(".", "")))
    for soma in ("226", "83", "10150"):         # 76+150, 31+52, 10.000+150: nada soma unidades
        assert soma not in numeros, soma
    # 0% = so o trilho e "0%" no centro; sem contador de cards, o trilho e "--"
    zero = _itens(painel._html_dia(_dia_aneis(feitas=0, consumo=0), "2026-10-13", _r_aneis()))
    assert "an-arco" not in zero[0][2] + zero[1][2] and [_centro(i[2]) for i in zero[:2]] == ["0", "0"]
    sem = _itens(painel._html_dia(_dia_aneis(consumo=None), "2026-10-13", _r_aneis()))
    assert "an-arco" not in sem[1][2] and _centro(sem[1][2]) == "--"
    assert sem[1][1] == "Cards: não consegui contar as revisões de hoje."
    # sem o ritmo (quem so tem o dia), os dois do dia
    assert [i[3] for i in _itens(painel._html_dia(_dia_aneis(), "2026-10-13"))] == ["Questões", "Cards"]
    css = painel.CSS
    for regra in (".aneis4{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))",
                  ".an-trilho{stroke:var(--trilho)}", ".an-arco{stroke-linecap:round}",
                  ".an-arco.an-q{stroke:var(--acento)}", ".an-arco.an-c{stroke:var(--rosa)}"):
        assert regra in css, regra
    quatro = re.search(r"@media \(min-width:(\d+)px\)\{\n  \.aneis4\{grid-template-columns:repeat\(4,minmax\(0,1fr\)\)\}",
                       css)
    assert quatro and int(quatro.group(1)) <= 760, "4 em linha a partir de 760 px"
    for brilho in ("drop-shadow", "box-shadow", "filter:", "glow"):
        assert brilho not in css, "sem brilho: %s" % brilho
    for morto in (".kpi-r", ".an-estado", ".sw-sp", ".ir{", ".ir a"):
        assert morto not in css, "CSS da legenda que saiu: %s" % morto


def test_ritmo_anel_contra_o_sprint_com_a_cor_e_o_texto():
    """DoD 2: o anel do Ritmo = o real de 7 dias contra a capacidade do sprint (sem sprint, o necessario por dia
    da meta). O estado nunca fica so na cor: o VALOR diz a comparacao ("35,4 de 80 por dia") e o `aria-label`
    e a dica do arco dizem "abaixo de 80/dia" / "em dia" -- abaixo = `--aviso`, em dia = `--ok`. Sem
    referencia, so o trilho, "--" e "35,4 por dia".
    ⚰️ *Era `test_ritmo_barra_com_marca_do_sprint` (part-2): a barra `.rb` contra a marca vertical dos 80/dia,
    na placa "Ritmo de questões" -- o conteudo subiu para o anel no topo (pedido dele, 13/10).*
    ⚰️ *Ate 13/10 (part-5) o texto do estado era a linha `p.kpi-r.an-estado` ("abaixo de 80/dia" em ambar,
    "em dia ✓" em verde) e embaixo "23,5 em 14 dias · 78,4% de acerto": as legendas do dashboard sairam a
    pedido dele ("gostaria de remover ... as legendas do dashboard"); o estado foi para o valor e o alt.*"""
    def alt(h):
        return re.search(r'role="img" aria-label="([^"]+)"', h).group(1)

    def titulo(h):
        return re.search(r"<title>([^<]+)</title>", h).group(1)

    abaixo = painel._html_ritmo(_r_aneis())                                 # 35,4 contra 80
    assert abaixo.startswith('<div class="an4" data-bloco="ritmo">')
    assert re.findall(RE_ARCO, abaixo) == [("an-abaixo", "44")] and _centro(abaixo) == "44"
    assert abaixo.endswith('<h3>Ritmo em 7 dias</h3><p class="an-val"><b>35,4</b> de 80 por dia</p></div>\n')
    assert alt(abaixo) == "Ritmo: 35,4 por dia nos últimos 7 dias, abaixo de 80/dia."
    assert titulo(abaixo) == "35,4 por dia nos últimos 7 dias, abaixo de 80/dia"
    em_dia = painel._html_ritmo(_r_aneis(real_7d=90.0))                     # 90 contra 80: o anel fecha
    assert re.findall(RE_ARCO, em_dia) == [("an-emdia", "100")] and _centro(em_dia) == "112"
    assert '<p class="an-val"><b>90,0</b> de 80 por dia</p>' in em_dia
    assert alt(em_dia) == "Ritmo: 90,0 por dia nos últimos 7 dias, em dia com 80/dia."
    sem_sprint = painel._html_ritmo(_r_aneis(sprint=False))                 # 35,4 contra 114,9
    assert re.findall(RE_ARCO, sem_sprint) == [("an-abaixo", "30")]
    assert '<p class="an-val"><b>35,4</b> de 114,9 por dia</p>' in sem_sprint
    assert alt(sem_sprint) == "Ritmo: 35,4 por dia nos últimos 7 dias, abaixo do necessário até a prova: 114,9/dia."
    sem_config = painel._html_ritmo(_r_aneis(capacidade=None))
    assert "an-arco" not in sem_config and _centro(sem_config) == "--", "sem referencia, sem %"
    assert '<p class="an-val"><b>35,4</b> por dia</p>' in sem_config
    for html_ in (abaixo, em_dia, sem_sprint, sem_config):
        assert "em 14 dias" not in html_ and "de acerto" not in html_ and "kpi-r" not in html_
        assert html_.count("<p") == 1, "so a linha do valor"
        assert html_.count("<svg") == 1 and "gauge" not in html_ and 'class="rb' not in html_
    css = painel.CSS
    assert ".an-arco.an-abaixo{stroke:var(--aviso)}" in css and ".an-arco.an-emdia{stroke:var(--ok)}" in css
    assert ".an-estado" not in css


def test_flashcards_da_semana_renomeado(db_sintetico):
    """DoD 4 (pedido dele, 13/10: "'Revisões nos próximos 7 dias', que deveria ser renomeado para 'Flashcards da
    semana'"): o MESMO grafico de barras da `db.agenda_revisoes`, com o titulo novo e a dica por barra; o nome
    antigo some da pagina."""
    html_ = painel._html_agenda({"dias": [{"data": "2026-10-14", "n": 30}, {"data": "2026-10-15", "n": 1}]})
    assert html_.startswith('<div class="placa dash-sec agenda"><div class="ag-cab"><h3>Flashcards da semana</h3>')
    assert '<li title="qua 14/10: 30 cards (pico da semana)" class="pico"><span class="ag-n">30</span>' in html_
    assert '<li title="qui 15/10: 1 card">' in html_
    pagina = _pagina()
    assert "Flashcards da semana" in _dash(pagina) and "Revisões nos próximos" not in pagina


def test_dashboard_em_placas_e_a_grade(db_sintetico, tmp_path, monkeypatch):
    """DoD 3 e 4 (s227, part-5): o dashboard sao TRES `.placa` na secao `data-bloco="dia"`, que e a GRADE -- o
    Hoje com os quatro aneis (inteiro), Por bloco e Flashcards da semana (lado a lado a partir de 760 px, a
    mesma altura pela linha da grade; empilhados no celular); o Plano de hoje e a Documentacao sao placas
    tambem. O CSS: `.wrap` na `--largura`; o mesmo vao entre placas e entre secoes; nenhum filete entre secoes;
    a `.placa` do tema e composta, nunca redefinida aqui. ⚰️ *Ate 13/10 (part-2) eram cinco placas: Hoje |
    Ritmo, Ate 01/11 inteira, Por bloco | Revisoes -- as placas Ritmo e Ate 01/11 viraram aneis no topo.*"""
    import plano
    monkeypatch.setattr(plano, "ler_sprint", lambda caminho=None: {"capacidade_q": 80, "fim": "2026-10-31"})
    _com_sprint(db_sintetico)
    (tmp_path / "aula-dossie.html").write_text("<title>x</title>", encoding="utf-8")
    reg = tmp_path / "quadro.json"
    reg.write_text(json.dumps({"itens": {"dossie": {"tipo": "analise", "titulo": "Dossiê"}}}), encoding="utf-8")
    monkeypatch.setattr(painel, "QUADRO", reg)
    monkeypatch.setattr(painel, "ARTIFATOS", tmp_path)
    pagina = painel.render_html(painel.coletar())
    assert '<section class="bloco dia dash" data-bloco="dia">' in pagina
    dash = _dash(pagina)
    partes = re.findall(r'<div class="placa ([^"]+)"( data-bloco="[a-z]+")?>', dash)
    assert partes == [("dash-hoje", ""), ("dash-sec", ' data-bloco="blocos"'), ("dash-sec agenda", "")], partes
    assert len(_itens(dash)) == 4 and '<div class="an4" data-bloco="ritmo">' in dash
    for morto in ("Ritmo de questões", "proj-barra", 'class="rb', "dash-sec proj"):
        assert morto not in dash, morto
    assert "<section" not in dash[1:], "as placas sao filhas da grade, sem secao dentro"
    assert '<section class="bloco semana placa" data-bloco="semana">' in pagina
    assert 'data-bloco="docs"' not in pagina, "s229: a Documentacao mora na Teoria"
    i = pagina.index('data-bloco="semana"')
    plano_html = pagina[i:pagina.index("</section>\n", pagina.index("Fora do sprint", i))]
    assert plano_html.count('<section class="rm-dia') >= 2 and "<details open" not in plano_html
    css = painel.CSS
    assert ".wrap{max-width:var(--largura)" in css
    assert ".dash{display:grid;grid-template-columns:minmax(0,1fr);gap:var(--esp-4)}" in css
    assert ".bloco + .bloco{margin-top:var(--esp-4)}" in css, "entre secoes, o mesmo vao da grade"
    grade = css.split("@media (min-width:760px){", 1)[1].split("\n}", 1)[0]
    assert ".dash{grid-template-columns:repeat(2,minmax(0,1fr))}" in grade
    assert ".dash > .dash-hoje{grid-column:1 / -1}" in grade, "o Hoje inteiro; Por bloco | Flashcards"
    assert ".agenda{display:flex;flex-direction:column}" in css and "flex:1 1 auto;min-height:112px" in css, \
        "o grafico de barras ocupa a altura da linha (a do Por bloco ao lado)"
    assert not re.search(r"\.(bloco|dash-sec)\{[^}]*border-top", css), "filete entre secoes voltou"
    assert not re.search(r"(^|[}\s,])\.placa\s*\{", css), "a .placa e do tema: aqui so se compoe"
    assert pagina.count("max-width") <= 2


def test_flashcards_da_semana_total_pico_e_paleta_propria():
    """s228 (pedido dele: "melhorar a estetica do bloco de flashcards da semana, ate com liberdade para rever a
    paleta"): o total no cabecalho, o pico em barra cheia (rotulo na dica, nunca so a cor), a paleta `--fc*` do
    tema; semana vazia sem pico. E a barra de Simulados no roxo do anel Ate 01/11 (o mesmo token)."""
    h = painel._html_agenda({"dias": [{"data": "2026-10-14", "n": 30}, {"data": "2026-10-15", "n": 70}]})
    assert '<p class="ag-total"><b>100</b> em 7 dias</p>' in h
    assert h.count('class="pico"') == 1 and 'title="qui 15/10: 70 cards (pico da semana)" class="pico"' in h
    vazio = painel._html_agenda({"dias": [{"data": "2026-10-14", "n": 0}]})
    assert "pico" not in vazio and "<b>0</b>" in vazio
    css = painel.CSS
    assert ".ag-barras .pico i{background:var(--fc)}" in css and "background:var(--fc-fraco)" in css
    assert "--roxo-fraco" not in css.split("Flashcards da semana", 1)[1].split("Tarefas", 1)[0]
    assert ".bl.sim .bl-barra i{background:var(--roxo)}" in css
    assert ".an-arco.an-meta{stroke:var(--roxo)}" in css, "o mesmo token do anel"


# ------------------------------------------------ s229 (front, pedido dele em 15/10)

def test_rd_lida_pela_assinatura_doc_sai_do_hoje(tmp_path, monkeypatch):
    """Item 1: a RD assinada (ou absorvida) em `analises/pendencias/itens/doc_<slug>` sai do "Hoje" mesmo com o
    snapshot do `quadro/` sem ela -- a MESMA fonte que o hub le ao vivo; nunca "nao assinada" para o que ele assinou."""
    reg = tmp_path / "quadro.json"
    reg.write_text(json.dumps({"itens": {"rd-a": {"tipo": "revisao", "titulo": "A"},
                                         "rd-b": {"tipo": "revisao", "titulo": "B"}}}), encoding="utf-8")
    for slug in ("rd-a", "rd-b"):
        (tmp_path / ("aula-%s.html" % slug)).write_text("<title>x</title>", encoding="utf-8")
    estado = tmp_path / "estado"
    estado.mkdir()
    pend = tmp_path / "pend"
    pend.mkdir()
    (pend / "doc_rd-a.json").write_text(json.dumps({"origem": "rd-a", "status": "absorvida"}), encoding="utf-8")
    monkeypatch.setattr(painel, "QUADRO", reg)
    monkeypatch.setattr(painel, "ARTIFATOS", tmp_path)
    monkeypatch.setattr(painel, "QUADRO_ESTADO", estado)
    monkeypatch.setattr(painel, "PEND_ESTADO", pend)
    monkeypatch.setattr(painel, "_datas_das_aulas", lambda ps: {p: "2026-10-01" for p in ps})
    assert painel._rd_nao_assinada()["slug"] == "rd-b"
    (pend / "doc_rd-b.json").write_text(json.dumps({"origem": "rd-b", "status": "assinado"}), encoding="utf-8")
    assert painel._rd_nao_assinada() is None
    (pend / "doc_rd-b.json").write_text(json.dumps({"origem": "rd-b", "status": "pendente"}), encoding="utf-8")
    assert painel._rd_nao_assinada()["slug"] == "rd-b", "so assinado/absorvida contam como lida"


def test_tarefa_cumprida_por_aula_mostra_o_titulo_da_aula():
    """Item 1: a #5426 seguia "Revisao final por banca (LEITURA)..." com a aula "UERJ de Bolso" no ar -- a aula que
    CUMPRE a tarefa (`tarefa_id`) da o titulo; a que so PREPARA nao troca o tema."""
    t = {"id": 5426, "semana": 7, "atrasada": False, "tema": "Revisão final por banca (LEITURA)", "q": 0,
         "classe": "aula", "url_lista": None, "area": "Preventiva", "bloco": "MFC"}
    cumpre = {5426: [{"slug": "uerj-de-bolso-mfc", "titulo": "UERJ de Bolso: MFC e a banca", "cumpre": True}]}
    prepara = {5426: [{"slug": "x", "titulo": "Outra", "cumpre": False}]}
    assert painel._tarefa(t, cumpre, set())["tema"] == "UERJ de Bolso: MFC e a banca"
    assert painel._tarefa(t, prepara, set())["tema"] == "Revisão final por banca (LEITURA)"


def test_cronograma_em_barras_horizontais_com_a_cor_da_area():
    """s229 (rodada 3, pedido dele): "Roadmap" -> "Cronograma"; cada tarefa e uma barra na largura toda (1 coluna),
    a faixa e o fundo tingido pela area (o chip segue com o nome), botoes a direita; no celular quebram."""
    css = painel.CSS
    assert ".tarefas{list-style:none;margin:0;padding:0;display:grid;gap:var(--esp-2);grid-template-columns:minmax(0,1fr)}" in css
    assert 'grid-template-areas:"meta acao" "tema acao"' in css and "auto-fill" not in css
    for area, tok in (("CM", "acento"), ("CIR", "rosa"), ("PED", "roxo"), ("GO", "amarelo")):
        assert '.tarefa:has(> .t-faixa[data-area="%s"]){--area:var(--%s)}' % (area, tok) in css
    assert '<i class="t-faixa" data-area="CIR" aria-hidden="true"></i>' in _li()


def test_tarefa_com_aula_lida_sai_do_cronograma(tmp_path, monkeypatch):
    """s229 (rodada 4): a tarefa cuja aula que a CUMPRE ja foi lida (quadro `feito` ou `doc_<slug>`) sai do
    Cronograma; a aula que so PREPARA a lista nao a tira. O botao da aula que cumpre leva `data-cumpre` (o hub
    esconde a barra ao vivo quando ele assina)."""
    estado = tmp_path / "estado"
    estado.mkdir()
    (estado / "a1.json").write_text('{"feito": true}', encoding="utf-8")
    monkeypatch.setattr(painel, "QUADRO_ESTADO", estado)
    monkeypatch.setattr(painel, "PEND_ESTADO", tmp_path / "nada")
    assert painel._aulas_lidas() == {"a1"}
    li = _li(aulas=[{"slug": "a1", "titulo": "A", "cumpre": True}])
    assert 'data-hub-aula="a1" data-titulo="A" data-cumpre="1">Abrir aula</a>' in li
    assert ".tarefa[hidden]{display:none}" in painel.CSS


def test_flashcards_da_semana_empilha_os_da_ultima_sessao():
    """s229 (rodada 5): por dia, os que ja estavam agendados (rosa) e os que ENTRARAM pela ultima sessao (ciano, no
    topo), o total em cima e o "+k" pequeno; a dica diz os dois."""
    ag = {"dias": [{"data": "2026-10-16", "n": 10, "sessao": 4}, {"data": "2026-10-17", "n": 5, "sessao": 0}]}
    html_ = painel._html_agenda(ag)
    assert '<span class="ag-n">10<small class="ag-mais">+4</small></span>' in html_
    assert '<b class="ag-sessao" style="height:40%"></b>' in html_ and html_.count("ag-sessao") == 1
    assert "10 cards, 4 da última sessão (pico da semana)" in html_
    assert ".ag-sessao{display:block;width:100%;background:var(--acento)}" in painel.CSS


def test_agenda_com_sessao_conta_pela_ultima_revisao(db_sintetico):
    """A contagem vem do banco (fsrs_revlog/fsrs_cards, sem tabela nova): nunca passa do total do dia."""
    ag = painel._agenda_com_sessao({"dias": [{"data": "2026-09-24", "n": 1}]})
    assert set(ag["dias"][0]) == {"data", "n", "sessao"} and 0 <= ag["dias"][0]["sessao"] <= 1
