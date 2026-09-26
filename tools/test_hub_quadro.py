"""test_hub_quadro.py -- s194/s195: a aba Aulas como QUADRO e o tique que republica quando a PROJECAO muda.

Pedido do operador (23/09): Aulas como backlog em que ele RISCA o que ja fez; o painel conversando
com a aba Cards; o hub em sync sem esperar o lote drenar. Pedido de 24/09 (s195): o quadro
SEPARADO POR SEMANAS, cada bloco de tarefa com a quantidade de questoes; aula concluida arquivada
e fora do hub. O que esta suite trava:

1. **Registro versionado** `core/hub_quadro.json`: tipo por slug; slug desconhecido = `aula` + WARN
   no build (nunca silencioso); tipo invalido ou `tarefas` malformada falha alto.
2. **Quadro por semanas**: "Atrasadas" primeiro, depois "Semana N · dd/mm–dd/mm" ate a semana da
   prova; cabecalho com tarefas e questoes; cada tarefa um bloco com peso, questoes e acao; aula
   ligada DENTRO do bloco; aula sem tarefa em "Outras aulas"; tarefa de lista sem botao "feito";
   o feito no `db` sai RISCADO em "Concluidas" ja no build; sem `db`, o controle nasce desabilitado.
3. **Projecao**: `--precisa-publicar` diz sim/nao e a acao -- `nova_fila` (lote drenado),
   `mesmo_lote` (so painel/quadro mudou: MESMO `sessao`, MESMOS cards), `nada`. O carimbo de hora
   do painel nao conta.
4. **Tarefa de aula**: aula feita com `tarefa_id` pendente vira pendencia RELATADA (o
   `plano.py --concluir --leitura` e do tique; o hub nao grava o plano).

Repo sintetico em tmp_path; o `ipub.db` nunca e tocado (o plano e o calendario entram injetados).
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import hub  # noqa: E402
from tools.fsrs_queue import TEMPLATE_PLAYER  # noqa: E402

AGORA = datetime(2026, 9, 23, 20, 0, 0)
TEMPLATE_HUB_REAL = hub.TEMPLATE_HUB.read_text(encoding="utf-8")
TEMPLATE_PLAYER_REAL = TEMPLATE_PLAYER.read_text(encoding="utf-8")
QUADRO = {"hernias": {"tipo": "aula", "titulo": "A Escada das Hernias", "tarefas": [49]},
          "autopsia": {"tipo": "analise", "titulo": "Autopsia UERJ 2023"},
          "bayes": {"tipo": "aula", "titulo": "A Escada de Bayes", "tarefa_id": 877},
          "rd-renal": {"tipo": "revisao", "titulo": "Revisao direcionada renal"}}
#: Calendario da trilha (a mesma regua do `plano.panorama`): AGORA cai na semana 2.
CAL = {1: (date(2026, 9, 14), date(2026, 9, 20)), 2: (date(2026, 9, 21), date(2026, 9, 27)),
       3: (date(2026, 9, 28), date(2026, 10, 4))}
URL = "https://med.estrategia.com/cadernos/x/?per_page=20"


def _t(id_, semana, tema, q=0, url=None, fonte="rf", status="pendente", bloco="GO"):
    return {"id": id_, "semana_plano": semana, "tema": tema, "q_previstas": float(q),
            "url_lista": url, "fonte": fonte, "status": status, "bloco": bloco, "ordem": id_}


PLANO = [_t(26, 1, "Diabetes na Gestacao", 19, URL),
         _t(877, 1, "Raciocinio diagnostico", 0, None, fonte="custom", bloco="MFC"),
         _t(49, 2, "Hernias da Parede Abdominal", 21, URL, bloco="CIR"),
         _t(875, 2, "Prevencao Quaternaria", 0, None, fonte="custom", bloco="MFC"),
         _t(1793, 2, "UERJ 2021 -- prova inteira", 60, "simulados/uerj/2021.pdf", bloco="Simulado"),
         _t(68, 3, "Doencas Glomerulares", 21, URL, bloco="CM"),
         _t(900, 9, "Fase 2 -- fora do quadro", 40, URL),
         _t(901, None, "Reserva -- sem semana", 40, URL),
         _t(902, 2, "Cortada", 40, URL, status="cortada"),
         _t(903, 2, "Ja feita", 40, URL, status="feita")]
PAINEL = ('<!DOCTYPE html><title>Painel</title><p class="atualizado"><!--gerado-->'
          '<span data-gerado="%s">agora</span><!--/gerado--></p><p>%s</p>')


def _lote(sessao="2026-09-23a", n=3):
    cards = [{"card_id": 500 + i, "frente_pergunta": "P%d?" % i, "verso_resposta": "R",
              "bucket": "hoje"} for i in range(n)]
    return {"sessao": sessao, "gerado_em": "2026-09-23T19:00:00", "total": n, "cards": cards}


def _repo(tmp_path, slugs=("hernias", "autopsia", "bayes", "rd-renal"), painel="S2: 21 tarefas"):
    art = tmp_path / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    for i, slug in enumerate(slugs):
        (art / ("aula-%s.html" % slug)).write_text("<title>%s</title><p>x</p>" % slug,
                                                    encoding="utf-8")
    (art / "painel.html").write_text(PAINEL % ("2026-09-23T19:00:00", painel), encoding="utf-8")
    return tmp_path, _repo_datas(tmp_path)


def _construir(raiz, data_fn, lote=None, quadro=None, estado=None, plano=None, cal=None):
    return hub.construir(lote or _lote(), raiz=raiz, out=raiz / "tmp" / "hub", agora=AGORA,
                         data_fn=data_fn, template_hub=TEMPLATE_HUB_REAL,
                         template_player=TEMPLATE_PLAYER_REAL,
                         quadro=QUADRO if quadro is None else quadro, estado_quadro=estado,
                         plano_linhas=PLANO if plano is None else plano,
                         calendario=CAL if cal is None else cal)


def _index(raiz):
    return (raiz / "tmp" / "hub" / "index.html").read_text(encoding="utf-8")


def _decidir(raiz, lote=None, notas=(), estado=None, plano=None):
    return hub.decidir(lote or _lote(), raiz / "tmp" / "hub", raiz=raiz, notas=list(notas),
                       estado_quadro=estado or {}, quadro=QUADRO,
                       data_fn=_repo_datas(raiz), plano_linhas=PLANO if plano is None else list(plano),
                       calendario=CAL, agora=AGORA)


def _repo_datas(raiz):
    def data_fn(p, _r):
        nomes = sorted(x.name for x in (Path(raiz) / "artifacts").glob("aula-*.html"))
        return "2026-09-%02d" % (10 + nomes.index(Path(p).name)), None
    return data_fn


def _secoes(pagina):
    """[(chave, titulo, [ids de tarefa | slugs])] na ordem da pagina."""
    saida = []
    for m in re.finditer(r'<section class="qd-sem" data-secao="([^"]+)"[^>]*aria-label="([^"]+)"[^>]*>'
                         r'(.*?)</section>', pagina, re.S):
        itens = re.findall(r'<li class="qd-item[^"]*"[^>]*?(?:data-tarefa="(\d+)"|data-slug="([\w-]+)")',
                           m.group(3))
        saida.append((m.group(1), m.group(2), [a or b for a, b in itens]))
    return saida


def _item(pagina, seletor):
    return re.search(r'<li class="qd-item[^"]*"[^>]*%s[^>]*>.*?</li>' % seletor, pagina, re.S).group(0)


# --------------------------------------------------------------------------
# 1. Registro versionado
# --------------------------------------------------------------------------

def test_registro_real_so_com_as_aulas_em_aberto_e_ligadas_ao_plano():
    """s195: s17, cancer-de-mama, hernias e autopsia foram para artifacts/arquivo/ e sairam do
    registro; as tres em aberto (ped, dmg, mfc) ligam-se as tarefas do plano."""
    reg = hub.ler_quadro(ROOT / hub.QUADRO_REG)
    assert set(reg) == {"dmg", "raciocinio-diagnostico", "topicos-pediatria"}
    assert reg["raciocinio-diagnostico"]["tarefa_id"] == 877
    assert reg["dmg"]["tarefas"] == [26, 40] and reg["topicos-pediatria"]["tarefas"] == [96, 100]
    reais = {hub.slug_de(p.name) for p in (ROOT / "artifacts").glob("aula-*.html")}
    assert reais == set(reg), "aula real sem tipo no registro (ou registro de aula arquivada)"
    for nome in ("aula-s17", "aula-cancer-de-mama", "aula-hernias", "aula-autopsia-uerj-2023"):
        assert (ROOT / "artifacts" / "arquivo" / (nome + ".html")).is_file(), nome


def test_slug_desconhecido_entra_como_aula_e_avisa(tmp_path):
    raiz, data_fn = _repo(tmp_path, slugs=("hernias", "nova-aula"))
    _m, problemas, avisos = _construir(raiz, data_fn)
    assert problemas == []
    assert any("nova-aula" in a and "sem tipo" in a for a in avisos), avisos
    assert re.search(r'data-slug="nova-aula" data-tipo="aula"', _index(raiz))


def test_registro_sem_arquivo_avisa_uma_vez(tmp_path):
    raiz, data_fn = _repo(tmp_path, slugs=("hernias",))
    _m, _p, avisos = hub.construir(_lote(), raiz=raiz, out=raiz / "tmp" / "hub", agora=AGORA,
                                   data_fn=data_fn, template_hub=TEMPLATE_HUB_REAL,
                                   template_player=TEMPLATE_PLAYER_REAL, plano_linhas=[],
                                   calendario={})
    assert any("registro do quadro ausente" in a for a in avisos)


def test_tipo_invalido_ou_tarefas_malformadas_falham_alto(tmp_path):
    arq = tmp_path / "q.json"
    arq.write_text(json.dumps({"itens": {"x": {"tipo": "palestra"}}}), encoding="utf-8")
    with pytest.raises(ValueError, match="palestra"):
        hub.ler_quadro(arq)
    arq.write_text(json.dumps({"itens": {"x": {"tipo": "aula", "tarefas": "26"}}}), encoding="utf-8")
    with pytest.raises(ValueError, match="tarefas"):
        hub.ler_quadro(arq)


# --------------------------------------------------------------------------
# 2. O quadro por semanas no index
# --------------------------------------------------------------------------

def test_secoes_atrasadas_primeiro_depois_semanas_ate_a_prova_e_outras_por_ultimo(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    secoes = _secoes(_index(raiz))
    assert [s[0] for s in secoes] == ["atrasadas", "2", "3", "outras"]
    assert [s[1] for s in secoes] == ["Atrasadas", "Semana 2 · 21/09–27/09", "Semana 3 · 28/09–04/10",
                                      "Outras aulas"]
    assert secoes[0][2] == ["26", "877"], "semana 1 < atual = atrasada, na ordem do plano"
    assert secoes[1][2] == ["49", "875", "1793"] and secoes[2][2] == ["68"]
    assert secoes[3][2] == ["rd-renal", "autopsia"], "aula sem tarefa vai para Outras aulas"
    pagina = _index(raiz)
    for tid in (900, 901, 902, 903):
        assert 'data-tarefa="%d"' % tid not in pagina, "fase 2, reserva, cortada e feita ficam fora"


def test_cabecalho_da_semana_conta_tarefas_e_questoes(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    cab = re.findall(r'<h3 class="qd-titulo">([^<]+) <span class="qd-n">(.*?)</span></h3>', pagina)
    contagem = {t: re.sub(r"<[^>]+>", "", c) for t, c in cab}
    assert contagem["Atrasadas"] == "2 tarefas · 19 questões"
    assert contagem["Semana 2 · 21/09–27/09"] == "3 tarefas · 81 questões"
    assert contagem["Semana 3 · 28/09–04/10"] == "1 tarefa · 21 questões"
    assert contagem["Outras aulas"] == "2 aulas"


def test_bloco_da_tarefa_tem_tema_peso_questoes_e_acao(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    lista = _item(pagina, 'data-tarefa="26"')
    assert '<p class="qd-tema">Diabetes na Gestacao</p>' in lista
    # prazo (s195, pedido dele): atrasada diz a semana e quando venceu; a corrente diz "ate dd/mm"
    venceu = "semana 1" + (" · venceu %s" % CAL[1][1].strftime("%d/%m") if 1 in CAL else "")
    assert ('<span class="qd-bl">GO</span><span>19 questões</span><span class="qd-atraso">%s</span>'
            % venceu) in lista
    assert 'href="%s" rel="noopener noreferrer">abrir lista</a>' % URL in lista
    assert "qd-atrasada" in lista and "qd-feito" not in lista, "tarefa de lista nao tem botao feito"
    assert "qd-sem-botao" not in lista, "s195: todo bloco tem a mesma largura; o botao mora dentro"
    hernias = _item(pagina, 'data-tarefa="49"')
    assert '<a class="hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias">abrir aula</a>' \
        in hernias, "aula que PREPARA a tarefa (tarefas: [49]) entra no bloco dela"
    assert "abrir lista" in hernias and "qd-feito" not in hernias
    assert '<span class="qd-prazo">até %s</span>' % CAL[2][1].strftime("%d/%m") in hernias
    preparar = _item(pagina, 'data-tarefa="875"')
    assert '<span class="tenue">aula a preparar</span>' in preparar and '<span>aula</span>' in preparar
    simulado = _item(pagina, 'data-tarefa="1793"')
    assert "prova em PDF no computador" in simulado and "simulados/uerj" not in simulado, \
        "caminho local nunca vira link (morre na pagina publicada)"


def test_aula_que_cumpre_tarefa_de_aula_tem_o_botao_feito_no_bloco(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    bayes = _item(_index(raiz), 'data-tarefa="877"')
    assert 'data-slug="bayes" data-tipo="aula" data-titulo="A Escada de Bayes"' in bayes
    assert '<div class="qd-bloco"><button type="button" class="qd-feito" aria-pressed="false"' in bayes, \
        "s195: o botao fica DENTRO do bloco (fora, o bloco com botao saia 54 px mais estreito)"
    assert 'aria-label="Marcar A Escada de Bayes como feita"' in bayes
    assert '<a class="hub-aula" href="aulas/bayes.html" data-titulo="A Escada de Bayes">abrir aula</a>' in bayes
    assert '<span class="qd-bl">MFC</span><span>aula</span>' in bayes


def test_feito_sai_riscado_em_concluidas_no_build(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn, estado={"bayes": {"feito": True, "ts": "x"},
                                      "rd-renal": {"feito": True, "ts": "y"},
                                      "autopsia": {"feito": False, "ts": "z"}})
    pagina = _index(raiz)
    secoes, feitas = pagina.split('id="hub-quadro-feitas"', 1)
    assert 'data-tarefa="877"' not in secoes and 'data-slug="rd-renal"' not in secoes
    bayes = _item(feitas, 'data-tarefa="877"')
    assert 'data-feito="1"' in bayes and 'aria-pressed="true"' in bayes and 'data-secao="atrasadas"' in bayes
    assert 'data-slug="rd-renal"' in feitas and 'id="hub-quadro-nfeitas">2<' in feitas
    assert 'data-slug="autopsia"' in secoes, "desmarcado fica na secao"
    assert ".qd-item[data-feito] .qd-tema{text-decoration:line-through" in pagina
    assert _secoes(pagina)[0][2] == ["26"], "Atrasadas perde o Bayes feito"


def test_sem_plano_tudo_vai_para_outras_aulas_e_sem_aula_nem_plano_diz(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn, plano=[], cal={})
    secoes = _secoes(_index(raiz))
    assert [s[0] for s in secoes] == ["outras"]
    assert secoes[0][2] == ["rd-renal", "hernias", "bayes", "autopsia"], "mais nova primeiro"
    assert hub.html_aulas([]) == '<p class="hub-vazio">Nada no quadro ainda: nem tarefa pendente, nem aula.</p>'


def test_aula_ligada_so_a_tarefa_concluida_avisa_candidata_a_arquivo(tmp_path):
    raiz, data_fn = _repo(tmp_path, slugs=("hernias",))
    plano = [_t(49, 2, "Hernias", 21, URL, status="feita")]
    _m, _p, avisos = _construir(raiz, data_fn, plano=plano)
    assert any("hernias" in a and "candidata a arquivo" in a for a in avisos), avisos
    assert _secoes(_index(raiz))[-1][2] == ["hernias"]


def test_plano_indisponivel_degrada_declarado(tmp_path, monkeypatch):
    def quebra():
        raise RuntimeError("banco trancado")
    monkeypatch.setattr(hub.db, "plano_listar", quebra)
    raiz, data_fn = _repo(tmp_path, slugs=("hernias",))
    _m, problemas, avisos = hub.construir(
        _lote(), raiz=raiz, out=raiz / "tmp" / "hub", agora=AGORA, data_fn=data_fn,
        template_hub=TEMPLATE_HUB_REAL, template_player=TEMPLATE_PLAYER_REAL, quadro=QUADRO,
        calendario={})
    assert problemas == []
    assert any("plano indisponivel" in a and "banco trancado" in a for a in avisos), avisos
    assert [s[0] for s in _secoes(_index(raiz))] == ["outras"]


def test_sem_db_controle_nasce_desabilitado_com_frase_curta(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    botoes = re.findall(r'<button type="button" class="qd-feito"[^>]*>', pagina)
    assert len(botoes) == 3 and all(" disabled" in b for b in botoes), "bayes + 2 aulas avulsas"
    aviso = re.search(r'<p class="qd-aviso" id="hub-quadro-aviso" hidden>([^<]+)</p>', pagina)
    assert aviso and len(aviso.group(1)) <= 80
    js = pagina.split("function iniciarQuadro()", 1)[1]
    assert 'db.collection("quadro")' in js and "semArmazenamento" in js
    assert ".set({feito: novo, ts: new Date().toISOString()})" in js
    assert 'querySelectorAll(".qd-item[data-slug]")' in js, "so item com botao entra no controle"
    assert '.qd-sem[data-secao="' in js, "o item desmarcado volta para a SUA secao"


def test_quadro_celular_alvo_de_toque_e_grid_item_encolhe(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert "sticky" not in pagina.lower() and "nowrap" not in pagina.lower()
    assert "width:44px;height:44px" in re.search(r"\.qd-feito\{([^}]*)\}", pagina).group(1)
    for regra in (r"\.qd-sem\{([^}]*)\}", r"\.qd-item\{([^}]*)\}", r"\.qd-bloco\{([^}]*)\}",
                  r"\.qd-tema\{([^}]*)\}"):
        assert "min-width:0" in re.search(regra, pagina).group(1), regra
    assert "min-height:44px" in re.search(r"\.qd-acao a,\.qd-acao \.tenue\{([^}]*)\}", pagina).group(1)
    assert "prefers-reduced-motion" in pagina


def test_ler_estado_do_dump_do_artifactdata(tmp_path):
    d = tmp_path / "db" / "quadro"
    d.mkdir(parents=True)
    (d / "hernias.json").write_text('{"feito": true, "ts": "2026-09-23T10:00:00Z"}',
                                    encoding="utf-8")
    (d / "dmg.json").write_text('{"feito": false}', encoding="utf-8")
    assert hub.ler_estado_quadro(tmp_path / "db") == {
        "hernias": {"feito": True, "ts": "2026-09-23T10:00:00Z"},
        "dmg": {"feito": False, "ts": None}}
    arq = tmp_path / "e.json"
    arq.write_text('[{"id": "x", "data": {"feito": true}}]', encoding="utf-8")
    assert hub.ler_estado_quadro(arq) == {"x": {"feito": True, "ts": None}}
    assert hub.ler_estado_quadro(None) == {} and hub.ler_estado_quadro(tmp_path / "nada") == {}


def test_painel_fala_com_as_abas():
    """O "Ir para os cards" e o "abrir aula" do painel sao interceptados pelo hub."""
    assert 'querySelectorAll("a[data-hub-aba], a[data-hub-aula]")' in TEMPLATE_HUB_REAL
    assert "abrirAula(alvo)" in TEMPLATE_HUB_REAL


def test_declaracao_de_capabilities_documentada_nos_portadores():
    """A regra nova `quadro` e a declaracao COMPLETA (non-empty = full set: esquecer `sessoes`
    revogaria a escrita das notas)."""
    # s197: + as 4 colecoes do EMED da aba Questoes, fechadas ao dono (o hub e compartilhado por link)
    decl = ('{db: {rules: [{path: "", read: "view", write: "admin"}, {path: "sessoes", '
            'write: "interact"}, {path: "quadro", write: "interact"}, '
            '{path: "listas", read: "admin", write: "admin"}, '
            '{path: "questoes", read: "admin", write: "admin"}, '
            '{path: "respostas", read: "admin", write: "admin"}, '
            '{path: "analises", read: "admin", write: "admin"}]}}')
    for portador in (".claude/commands/revisar.md", ".claude/commands/hub-backend.md"):
        assert decl in (ROOT / portador).read_text(encoding="utf-8"), portador


# --------------------------------------------------------------------------
# 3. Projecao e --precisa-publicar
# --------------------------------------------------------------------------

def _publicado(raiz, data_fn, **kw):
    _construir(raiz, data_fn, **kw)
    hub.confirmar(raiz / "tmp" / "hub", agora=AGORA)


def test_sem_registro_publica_mesmo_lote(tmp_path):
    raiz, _ = _repo(tmp_path)
    d = _decidir(raiz)
    assert d["publicar"] and d["acao"] == "mesmo_lote"
    assert "sem projecao confirmada" in d["motivos"][0]


def test_nada_mudou_nao_publica(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    d = _decidir(raiz, notas=[500])
    assert d == {"publicar": False, "acao": "nada", "motivos": [d["motivos"][0]],
                 "drenado": False, "notas": 1, "total": 3, "concluir": []}


def test_so_o_carimbo_do_painel_mudou_nao_publica(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    (raiz / "artifacts" / "painel.html").write_text(PAINEL % ("2026-09-23T19:20:00",
                                                              "S2: 21 tarefas"), encoding="utf-8")
    assert _decidir(raiz)["acao"] == "nada"


def test_painel_mudou_com_lote_em_curso_republica_o_mesmo_lote(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    (raiz / "artifacts" / "painel.html").write_text(PAINEL % ("2026-09-23T19:20:00",
                                                              "S2: 20 tarefas"), encoding="utf-8")
    d = _decidir(raiz, notas=[500, 501])
    assert d["publicar"] and d["acao"] == "mesmo_lote" and d["motivos"] == ["painel mudou"]


def test_quadro_mudou_republica_o_mesmo_lote(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    d = _decidir(raiz, estado={"autopsia": {"feito": True}})
    assert d["acao"] == "mesmo_lote" and d["motivos"] == ["quadro de aulas mudou"]


def test_plano_mudou_republica_o_mesmo_lote(tmp_path):
    """s195: tarefa concluida (ou nova) muda o quadro, logo a projecao -- sem lote novo."""
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    plano = [dict(l) for l in PLANO]
    plano[0]["status"] = "feita"
    d = _decidir(raiz, plano=plano)
    assert d["acao"] == "mesmo_lote" and d["motivos"] == ["quadro de aulas mudou"]


def test_lote_drenado_pede_nova_fila(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    d = _decidir(raiz, notas=[500, 501, 502])
    assert d["publicar"] and d["acao"] == "nova_fila" and d["drenado"]
    assert d["motivos"][0] == "lote drenado (3/3)"


def test_lote_mantido_quando_so_o_painel_mudou(tmp_path):
    """🔴 Lote em curso NAO e trocado: republica com o MESMO sessao e os MESMOS cards (as notas
    ja dadas voltam do db, colecao sessoes/<sessao>/notas, no reload)."""
    raiz, data_fn = _repo(tmp_path)
    lote = _lote()
    _publicado(raiz, data_fn, lote=lote)
    (raiz / "artifacts" / "painel.html").write_text(PAINEL % ("x", "mudou"), encoding="utf-8")
    assert _decidir(raiz, lote=lote, notas=[500])["acao"] == "mesmo_lote"
    manifesto, problemas, _ = _construir(raiz, data_fn, lote=lote)
    assert problemas == [] and manifesto["sessao"] == lote["sessao"]
    assert hub.extrair_lote(_index(raiz)) == lote
    assert _decidir(raiz, lote=lote, notas=[500])["acao"] == "mesmo_lote", \
        "so o --confirmar move o registro"
    hub.confirmar(raiz / "tmp" / "hub", agora=AGORA)
    assert _decidir(raiz, lote=lote, notas=[500])["acao"] == "nada"


def test_player_restaura_as_notas_do_db_no_reload():
    """O reload do celular depois do republish nao perde nota: o player relê a colecao do lote."""
    player = TEMPLATE_PLAYER_REAL
    assert 'db.collection("sessoes/" + LOTE.sessao + "/notas")' in player
    assert "var docs = snap.docs || [];" in player and "restaurar(docs);" in player
    assert "restaurarLocal();" in player, "s195: o espelho local volta antes do db"
    assert "return reenviarPendentes(docs);" in player, "s195: o que o db nao tem e reenviado"


def test_ids_com_nota_le_o_dump_por_arquivo(tmp_path):
    d = tmp_path / "notas"
    d.mkdir()
    (d / "500.json").write_text('{"card_id": 500, "rating_primeira": 3}', encoding="utf-8")
    (d / "501.json").write_text('{"card_id": 501, "defeito": true}', encoding="utf-8")
    assert hub.ids_com_nota(d) == {500, 501}
    assert hub.ids_com_nota(None) == set()


def test_cli_precisa_publicar_sim_e_nao(tmp_path, capsys, monkeypatch):
    raiz, data_fn = _repo(tmp_path)
    monkeypatch.setattr(hub.db, "plano_listar", lambda: list(PLANO))
    monkeypatch.setattr(hub, "calendario_trilha", lambda: dict(CAL))
    monkeypatch.setattr(hub.db, "agora", lambda: AGORA)
    _publicado(raiz, data_fn)
    arq_lote = tmp_path / "lote.json"
    arq_lote.write_text(json.dumps(_lote()), encoding="utf-8")
    monkeypatch.setattr(hub, "RAIZ", raiz)
    monkeypatch.setattr(hub, "QUADRO_REG", "q.json")
    (raiz / "q.json").write_text(json.dumps({"itens": QUADRO}), encoding="utf-8")
    monkeypatch.setattr(hub, "data_de_criacao", _repo_datas(raiz))
    args = ["--precisa-publicar", "--lote", str(arq_lote), "--out", str(raiz / "tmp" / "hub")]
    assert hub.main(args) == 0
    assert "precisa publicar: nao -- nada" in capsys.readouterr().out
    (raiz / "artifacts" / "painel.html").write_text(PAINEL % ("x", "outro"), encoding="utf-8")
    assert hub.main(args + ["--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["publicar"] is True and saida["acao"] == "mesmo_lote"


# --------------------------------------------------------------------------
# 4. Aula feita com tarefa do plano
# --------------------------------------------------------------------------

def test_aula_feita_com_tarefa_pendente_vira_pendencia_relatada(tmp_path):
    raiz, _ = _repo(tmp_path)
    plano = [{"id": 877, "status": "pendente", "tema": "Raciocinio diagnostico"}]
    d = _decidir(raiz, estado={"bayes": {"feito": True}, "hernias": {"feito": True}}, plano=plano)
    assert d["concluir"] == [{"slug": "bayes", "tarefa_id": 877, "tema": "Raciocinio diagnostico"}]
    plano[0]["status"] = "feita"
    assert _decidir(raiz, estado={"bayes": {"feito": True}}, plano=plano)["concluir"] == []


def test_hub_nao_conclui_tarefa_sozinho():
    """O `plano.py --concluir` e ato do tique; o hub so relata, nunca grava o plano -- do
    `tools.plano` entram so leitores puros (calendario, classe da tarefa, semanas da Fase 1)."""
    fonte = Path(hub.__file__).read_text(encoding="utf-8")
    assert "plano_set_status" not in fonte and "import plano" not in fonte
    assert "plano_upsert" not in fonte and "plano_mover" not in fonte


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
