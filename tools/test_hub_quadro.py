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
5. **O quadro conclui sozinho** (s214, hotfix `2026-10-04-assinar-nao-conclui`): assinar a leitura no
   rodape do leitor marca `quadro/<slug>` feito pelo mesmo caminho do botao (nunca desmarca, nao
   regrava); tarefa de lista com `listas/t<N>.status == "resolvida"` vai para Concluidas com a marca
   "resolvida · registro pendente", sem gravar nada; sem leitura de `listas`, fica o build.

Repo sintetico em tmp_path; o `ipub.db` nunca e tocado (o plano e o calendario entram injetados).
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import hub  # noqa: E402
from tools.fsrs_queue import TEMPLATE_PLAYER  # noqa: E402
from tools.test_hub_render import NODE, extrair_funcao  # noqa: E402

AGORA = datetime(2026, 9, 23, 20, 0, 0)
TEMPLATE_HUB_REAL = hub.TEMPLATE_HUB.read_text(encoding="utf-8")
TEMPLATE_PLAYER_REAL = TEMPLATE_PLAYER.read_text(encoding="utf-8")
QUADRO = {"hernias": {"tipo": "aula", "titulo": "A Escada das Hernias", "tarefas": [49]},
          "autopsia": {"tipo": "analise", "titulo": "Autopsia UERJ 2023"},
          "bayes": {"tipo": "aula", "titulo": "A Escada de Bayes", "tarefa_id": 877},
          "rd-renal": {"tipo": "revisao", "titulo": "Revisao direcionada renal", "bloco": "CM"}}
#: Calendario da trilha (a mesma regua do `plano.panorama`): AGORA cai na semana 2.
CAL = {1: (date(2026, 9, 14), date(2026, 9, 20)), 2: (date(2026, 9, 21), date(2026, 9, 27)),
       3: (date(2026, 9, 28), date(2026, 10, 4))}
URL = "https://med.estrategia.com/cadernos/x/?per_page=20"


def _t(id_, semana, tema, q=0, url=None, fonte="rf", status="pendente", bloco="GO", area=None):
    return {"id": id_, "semana_plano": semana, "tema": tema, "q_previstas": float(q),
            "url_lista": url, "fonte": fonte, "status": status, "bloco": bloco, "ordem": id_,
            "area": area}


PLANO = [_t(26, 1, "Diabetes na Gestacao", 19, URL),
         _t(877, 1, "Raciocinio diagnostico", 0, None, fonte="custom", bloco="MFC"),
         _t(49, 2, "Hernias da Parede Abdominal", 21, URL, bloco="CIR"),
         _t(875, 2, "Prevencao Quaternaria", 0, None, fonte="custom", bloco="MFC"),
         _t(1793, 2, "UERJ 2021 -- prova inteira", 60, "simulados/uerj/2021.pdf", bloco="Simulado",
            area="Simulado"),
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


def _biblioteca(pagina):
    """[ids de tarefa | slugs] da Biblioteca (s216, part-3; s218: a `<section id="hub-quadro-feitas">`, o
    corpo da aba), em ordem de pagina (a RD de varias disciplinas aparece uma vez em cada)."""
    feitas = pagina.split('id="hub-quadro-feitas"', 1)[1].split("</section>", 1)[0]
    return [a or b for a, b in re.findall(
        r'<li class="qd-item[^"]*"[^>]*?(?:data-tarefa="(\d+)"|data-slug="([\w-]+)")', feitas)]


def _item(pagina, seletor):
    return re.search(r'<li class="qd-item[^"]*"[^>]*%s[^>]*>.*?</li>' % seletor, pagina, re.S).group(0)


# --------------------------------------------------------------------------
# 1. Registro versionado
# --------------------------------------------------------------------------

#: O banco que o vivo das RDs mede para o plano (part-2b). Constante de módulo para o teste de skip
#: apontá-la para um arquivo inexistente.
REAL_DB = ROOT / "ipub.db"


def _defeitos_do_registro(raiz):
    """(registro, defeitos) do `core/hub_quadro.json` de `raiz` contra as aulas de `raiz/artifacts/` --
    a FORMA (part-2b), nunca o conjunto de slugs. Lido por `hub.ler_quadro`, que já falha ALTO em tipo,
    `tarefas`, `bloco`, `disciplinas` e `resumos` malformados. [] = ok. O vivo e o gêmeo passam por aqui."""
    raiz = Path(raiz)
    reg = hub.ler_quadro(raiz / hub.QUADRO_REG)
    reais = {hub.slug_de(p.name) for p in (raiz / "artifacts").glob(hub.PADRAO_AULAS)}
    defeitos = []
    # Aula SEM tarefa nao e defeito: e estado previsto pelo hub ("Outras aulas", docstring do topo).
    # O audit da part-2b (10/10/2026) tirou a regra "toda aula liga a tarefa", que poria a suite
    # vermelha num registro legitimo -- a classe que esta part remove.
    for slug, v in sorted(reg.items()):
        tid = v.get("tarefa_id")
        if tid is not None and (isinstance(tid, bool) or not isinstance(tid, int)):
            defeitos.append("`tarefa_id` não inteiro em %s: %r" % (slug, tid))
        if v["tipo"] == "revisao" and not slug.startswith("rd-"):
            defeitos.append("revisão fora do padrão rd-*: %s" % slug)              # s210
    defeitos += ["aula real sem tipo no registro: %s" % s for s in sorted(reais - set(reg))]
    defeitos += ["registro de aula sem arquivo em artifacts/: %s" % s for s in sorted(set(reg) - reais)]
    return reg, defeitos


@pytest.mark.vivo
def test_registro_real_so_com_as_aulas_em_aberto_e_ligadas_ao_plano():
    """O registro REAL tem a forma de `_defeitos_do_registro`: `tarefa_id` (a tarefa que a aula CUMPRE),
    quando existe, é inteiro; revisão = slug rd-* (s210); registro
    e disco concordam (toda aula de `artifacts/` tem tipo; nenhum registro de aula que saiu). Sem o
    conjunto de slugs (part-2b): registrar RD ou aula nova não derruba a suíte.

    ⚰️ 10/10/2026 (part-2b): o conjunto exato de slugs por tipo e os `tarefa_id`/`tarefas` de 15 aulas,
    re-escritos a cada sessão que registrava ou arquivava aula (s195, s204, s206, s212, s213, s214,
    s217, s219) -- era o conjunto do dado real, não forma. Contagem é relatório (o print).

    Pula com motivo (`VIVO:`) sem o registro ou sem aula em `artifacts/`."""
    if not (ROOT / hub.QUADRO_REG).is_file():
        pytest.skip("VIVO: %s ausente -- forma do registro real não medida" % hub.QUADRO_REG)
    if not list((ROOT / "artifacts").glob(hub.PADRAO_AULAS)):
        pytest.skip("VIVO: artifacts/aula-*.html ausentes -- registro x disco não medido")
    reg, defeitos = _defeitos_do_registro(ROOT)
    por_tipo = {t: sum(v["tipo"] == t for v in reg.values()) for t, _r in hub.TIPOS_QUADRO}
    print(f"  registro: {len(reg)} itens {por_tipo}")
    assert defeitos == [], defeitos
    # s216 (part-3, decisao do operador em 05/10): daqui em diante nada vai para artifacts/arquivo/ -- a
    # aula concluida fica na Biblioteca da Teoria; as 5 ja arquivadas voltam sob pedido, uma a uma


def test_gemeo_hermetico_do_registro_acusa_cada_forma_plantada(tmp_path):
    """Gêmeo hermético do vivo acima (part-2b): o MESMO `_defeitos_do_registro` sobre um repo sintético
    com um defeito plantado de cada -- `tarefa_id` em texto, revisão fora de `rd-*`, aula do disco sem
    registro e registro sem arquivo. Os bem-formados (RD, aula que cumpre, aula que prepara, aula SEM
    tarefa -- "Outras aulas" --, análise) não são acusados. Tipo inválido e `tarefas` malformada falham ALTO já na leitura:
    `test_tipo_invalido_ou_tarefas_malformadas_falham_alto`; a aula nova no build:
    `test_slug_desconhecido_entra_como_aula_e_avisa`."""
    itens = {"rd-ok": {"tipo": "revisao", "disciplinas": ["Cirurgia"]},
             "revisao-solta": {"tipo": "revisao", "disciplinas": ["Cirurgia"]},
             "aula-cumpre": {"tipo": "aula", "tarefa_id": 26},
             "aula-prepara": {"tipo": "aula", "tarefas": [49]},
             "aula-solta": {"tipo": "aula"},
             "aula-texto": {"tipo": "aula", "tarefa_id": "26"},
             "doc": {"tipo": "analise"},
             "arquivada": {"tipo": "aula", "tarefa_id": 40}}
    (tmp_path / "core").mkdir()
    (tmp_path / hub.QUADRO_REG).write_text(json.dumps({"itens": itens}), encoding="utf-8")
    _repo(tmp_path, slugs=[s for s in itens if s != "arquivada"] + ["nova"])
    _reg, defeitos = _defeitos_do_registro(tmp_path)
    assert defeitos == [
        "`tarefa_id` não inteiro em aula-texto: '26'",
        "revisão fora do padrão rd-*: revisao-solta",
        "aula real sem tipo no registro: nova",
        "registro de aula sem arquivo em artifacts/: arquivada"], defeitos


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

def test_secoes_atrasadas_primeiro_depois_semanas_ate_a_prova_e_biblioteca_por_ultimo(tmp_path):
    """s216 (part-1): a Teoria so mostra tarefa de aula e tarefa com aula ligada -- a lista sem aula
    (26, 1793, 68) mora no Painel; semana sem nada a mostrar (a 3) sai, a corrente fica. s216
    (part-3): "Outras aulas" virou a Biblioteca, no fim (e vazia aqui: a analise mora no Painel)."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    secoes = _secoes(pagina)
    # s218: ⚰️ a secao "Revisoes direcionadas" do topo -- a RD mora so na Biblioteca
    assert [s[0] for s in secoes] == ["atrasadas", "2"]
    assert [s[1] for s in secoes] == ["Atrasadas", "Semana 2 · 21/09 a 27/09"]
    assert secoes[0][2] == ["877"], "semana 1 < atual = atrasada, na ordem do plano"
    assert secoes[1][2] == ["49", "875"]
    assert _biblioteca(pagina) == ["rd-renal"], "a RD na Biblioteca; a analise (autopsia) so no Painel"
    assert pagina.index('id="hub-quadro-feitas"') > pagina.index('data-secao="2"'), "a Biblioteca vem por ultimo"
    pagina = _index(raiz)
    for tid in (900, 901, 902, 903):
        assert 'data-tarefa="%d"' % tid not in pagina, "fase 2, reserva, cortada e feita ficam fora"


def test_teoria_so_com_tarefas_de_aula_ou_com_aula_ligada(tmp_path):
    """s216 (hub-integracao part-1, pedido do operador em 05/10): o plano inteiro aparecia
    duas vezes (92 tarefas no Painel e as mesmas 92 em Aulas; so 12 de aula). A Teoria fica com a
    tarefa de aula (`classe == "aula"`) e a tarefa de QUALQUER classe com aula ligada (prepara ou
    cumpre); a analise sai de toda secao, inclusive de Concluidas. O filtro e de EXIBICAO: a semana
    de hoje continua saindo de TODOS os pendentes (A2)."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn, estado={"autopsia": {"feito": True, "ts": "x"}})
    pagina = _index(raiz)
    quadro = pagina.split('id="hub-quadro"', 1)[1]
    ids = set(re.findall(r'data-tarefa="(\d+)"', quadro))
    assert ids == {"877", "49", "875"}, ids
    assert {"26", "1793", "68"}.isdisjoint(ids), "lista sem aula ligada nao aparece na Teoria"
    assert 'data-slug="autopsia"' not in quadro, "analise nem em secao nem em Concluidas"
    # A2: com o filtro antes da regua, a semana de hoje viraria a 2 (a 1a com tarefa de aula)
    plano = [_t(26, 1, "Lista sem aula", 19, URL), _t(877, 2, "Raciocinio", 0, None, fonte="custom")]
    secoes, _c, _a = hub.secoes_do_quadro([], plano_linhas=plano, calendario={}, hoje=date(2026, 9, 1))
    assert [(s["chave"], [i["id"] for i in s["itens"]]) for s in secoes if s["chave"].isdigit()] == \
        [("1", []), ("2", [877])], \
        "semana corrente = a 1, de TODOS os pendentes; fica fixa e vazia"
    assert not [i for s in secoes for i in s["itens"] if i.get("atrasada")]
    for proibido in ("–", "—", "→", "$$", "\\rightarrow"):
        assert proibido not in quadro, "caractere proibido na Teoria: %r" % proibido


def test_revisao_direcionada_mora_na_biblioteca_nova_ate_ser_lida(tmp_path):
    """s210 (01/10) a RD ganhou bloco proprio no topo da aba; s218 (pedido do operador em 07/10: "as
    revisoes podem entrar na biblioteca ... com a taxonomia correta") ⚰️ esse bloco: a RD mora SO na
    Biblioteca; a ainda nao lida leva "nova" (classe 0, topo da disciplina) e o cabecalho conta as novas;
    lida (assinada no leitor), perde a etiqueta e fica no lugar (classe 3), sem secao de origem. P20 (s219):
    sem o quadrado 'feito' -- o `data-slug` (a chave do `quadro/<slug>` que a assinatura grava) segue."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert 'data-secao="revisoes"' not in pagina and "Revisões direcionadas" not in pagina
    item = _item(pagina, 'data-slug="rd-renal"')
    assert "qd-feito" not in item and 'data-secao="biblioteca"' in item and 'data-bib="0"' in item
    assert '<span class="qd-nova">nova</span>' in item
    assert '<span class="qd-novas" id="hub-quadro-novas" data-novas>1 nova</span>' in pagina
    _construir(raiz, data_fn, estado={"rd-renal": {"feito": True, "ts": "x"}})
    pagina = _index(raiz)
    item = _item(pagina, 'data-slug="rd-renal"')
    assert 'data-feito="1"' in item and 'data-bib="3"' in item and "qd-nova" not in item
    assert '<span class="qd-novas" id="hub-quadro-novas" data-novas hidden></span>' in pagina


def test_cabecalho_da_semana_conta_tarefas_e_questoes(tmp_path):
    """s218 (07/10, o "69 questoes" que ele estranhou): o cabecalho somava so as questoes das tarefas
    MOSTRADAS. Agora ele conta o que a Teoria mostra (tarefas; resumos quando ha) e, dentro, UMA linha
    com o total REAL de questoes pendentes da semana no plano -- inclusive a lista sem aula, que mora no
    Painel -- com atalho para a aba Listas."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    cab = re.findall(r'<h3 class="qd-titulo">([^<]+) <span class="qd-n">(.*?)</span></h3>', pagina)
    contagem = {t: re.sub(r"<[^>]+>", "", c) for t, c in cab}
    assert contagem["Atrasadas"] == "1 tarefa"
    assert contagem["Semana 2 · 21/09 a 27/09"] == "2 tarefas", "a soma parcial (21) saiu do cabecalho"
    assert "Semana 3 · 28/09 a 04/10" not in contagem, "semana futura sem tarefa de aula nao aparece"
    assert "Revisões direcionadas" not in contagem and "Outras aulas" not in contagem
    sec = dict((k, v) for k, v, _i in _secoes(pagina))
    atalho = ', na <a href="#questoes" data-hub-aba="questoes" data-hub-modo="questoes">aba Listas</a></p>'
    sem2 = re.search(r'data-secao="2".*?</section>', pagina, re.S).group(0)
    # 49 (21) + 875 (0) + 1793 (60, simulado sem aula); a cortada (902) e a feita (903) fora
    assert '<p class="qd-qsem">Questões da semana: <b>81</b> · com as atrasadas: <b>100</b>' + atalho in sem2,         "a corrente diz tambem o numero do Painel (`q_abertas` inclui as atrasadas)"
    atr = re.search(r'data-secao="atrasadas".*?</section>', pagina, re.S).group(0)
    assert '<p class="qd-qsem">Questões atrasadas: <b>19</b>' + atalho in atr, "26 (19) + 877 (0)"
    assert sec and '<h3 class="qd-bib-tit" id="hub-bib-tit">Biblioteca <span class="qd-n" id="hub-quadro-nfeitas">1</span>' in pagina


def test_bloco_da_tarefa_tem_tema_peso_questoes_e_acao(tmp_path):
    # s216 (part-1): lista so aparece na Teoria com aula ligada -- a aula das hernias prepara 26 e 1793
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn, quadro=dict(QUADRO, hernias=dict(QUADRO["hernias"], tarefas=[26, 49, 1793])))
    pagina = _index(raiz)
    lista = _item(pagina, 'data-tarefa="26"')
    assert '<p class="qd-tema">Diabetes na Gestacao</p>' in lista
    # prazo (s195, pedido dele): atrasada diz a semana e quando venceu; a corrente diz "ate dd/mm"
    venceu = "semana 1" + (" · venceu %s" % CAL[1][1].strftime("%d/%m") if 1 in CAL else "")
    assert ('<span class="qd-bl">GO</span><span>19 questões</span><span class="qd-atraso">%s</span>'
            % venceu) in lista
    # P21 (s220): na Teoria o cartao E a aula -- a lista do EMED mora no Painel e as questoes na aba Listas
    assert lista.count("<a ") == 1 and '<a class="qd-bloco qd-alvo hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias"><p class="qd-tema">' in lista
    assert "abrir lista" not in lista and URL not in lista and "qd-acao" not in lista
    assert "qd-atrasada" in lista and "qd-feito" not in lista, "tarefa de lista nao tem botao feito"
    assert "qd-sem-botao" not in lista, "s195: todo bloco tem a mesma largura; o botao mora dentro"
    hernias = _item(pagina, 'data-tarefa="49"')
    assert '<a class="qd-bloco qd-alvo hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias">' in hernias, \
        "aula que PREPARA a tarefa (tarefas: [49]): o toque no cartao a abre (P21)"
    assert "abrir lista" not in hernias and "abrir aula" not in hernias and "qd-feito" not in hernias
    assert '<span class="qd-prazo">até %s</span>' % CAL[2][1].strftime("%d/%m") in hernias
    preparar = _item(pagina, 'data-tarefa="875"')
    # P20 (s219): sem questoes, sem lista e sem aula, a classe e o ultimo recurso -- texto da META (apagada),
    # nunca no lugar de um link; a linha de acao nem existe
    assert ('<p class="qd-meta"><span class="qd-bl">MFC</span><span>aula a preparar</span>'
            '<span class="qd-prazo">até %s</span></p>' % CAL[2][1].strftime("%d/%m")) in preparar
    assert "qd-acao" not in preparar and "tenue" not in preparar and "<span>aula</span>" not in preparar
    assert 'class="qd-item qd-sem-aula"' in preparar and "<a " not in preparar, "P21: sem aula, cartao sem acao"
    simulado = _item(pagina, 'data-tarefa="1793"')
    # P21: a prova em PDF (texto, nunca link: morre na pagina publicada) mora no Painel; na Teoria, a aula
    assert "prova em PDF no computador" not in simulado and "simulados/uerj" not in simulado
    assert '<a class="qd-bloco qd-alvo hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias">' in simulado


def test_aula_que_cumpre_tarefa_de_aula_leva_o_slug_e_nao_o_botao(tmp_path):
    """P20 (s219, print de 07/10: "alguns blocos tendo checkbox, outros nao (pode ate ser removido...,
    considerando que assinar resolve automaticamente)"): o quadrado so existia na tarefa de classe `aula`
    -- a `sem_lista` cuja aula a CUMPRE (#530, #768) nao o tinha. Saiu de toda a Teoria; o `data-slug`
    fica: e por ele que a assinatura no leitor risca o item e o tique conclui a tarefa."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    bayes = _item(_index(raiz), 'data-tarefa="877"')
    assert 'data-slug="bayes" data-tipo="aula" data-titulo="A Escada de Bayes"' in bayes
    assert ('<a class="qd-bloco qd-alvo hub-aula" href="aulas/bayes.html" data-titulo="A Escada de Bayes">'
            '<p class="qd-tema">') in bayes and "qd-feito" not in bayes
    assert "<button" not in bayes and "aria-pressed" not in bayes
    assert bayes.count("<a ") == 1 and "abrir aula" not in bayes, "P21: o cartao inteiro e o alvo"
    assert '<p class="qd-meta"><span class="qd-bl">MFC</span><span class="qd-atraso">' in bayes, \
        "com a aula como acao, a meta nao repete a classe ('aula')"


def test_feito_sai_riscado_na_biblioteca_no_build(tmp_path):
    # s216 (part-1): a autopsia vira aula avulsa aqui (analise nao mora na Teoria) e a aula das
    # hernias prepara a 26, para Atrasadas seguir com uma tarefa depois do Bayes feito. s216 (part-3):
    # "Concluidas" virou a Biblioteca -- o feito vai riscado para la, e a aula avulsa (sem tarefa
    # pendente) mora la desde o build, sem riscar; ordem = data de criacao, mais nova primeiro.
    raiz, data_fn = _repo(tmp_path)
    quadro = dict(QUADRO, autopsia=dict(QUADRO["autopsia"], tipo="aula", bloco="VARIAS"),
                  hernias=dict(QUADRO["hernias"], tarefas=[26, 49]))
    _construir(raiz, data_fn, quadro=quadro, estado={"bayes": {"feito": True, "ts": "x"},
                                                     "rd-renal": {"feito": True, "ts": "y"},
                                                     "autopsia": {"feito": False, "ts": "z"}})
    pagina = _index(raiz)
    secoes, feitas = pagina.split('id="hub-quadro-feitas"', 1)
    assert 'data-tarefa="877"' not in secoes and 'data-slug="rd-renal"' not in secoes
    bayes = _item(feitas, 'data-tarefa="877"')
    assert 'data-feito="1"' in bayes and 'data-secao="atrasadas"' in bayes and "qd-feito" not in bayes
    assert 'data-slug="rd-renal"' in feitas and 'id="hub-quadro-nfeitas">3<' in feitas
    autopsia = _item(feitas, 'data-slug="autopsia"')
    assert "data-feito" not in autopsia and 'data-secao="biblioteca"' in autopsia, "desmarcado nao risca"
    assert _biblioteca(pagina) == ["rd-renal", "877", "autopsia"], "por area: CM, MFC, Varias areas (s218)"
    assert '<section class="qd-bib" id="hub-quadro-feitas"' in pagina, "s218: o corpo da aba, nao um <details>"
    assert not re.search(r'<details class="qd-area"[^>]*\bopen\b', pagina), "as areas nascem recolhidas"
    assert ".qd-item[data-feito] .qd-tema{text-decoration:line-through" in pagina
    assert dict((k, v) for k, _t, v in _secoes(pagina))["atrasadas"] == ["26"],         "Atrasadas perde o Bayes feito"


def test_sem_plano_tudo_vai_para_a_biblioteca_e_sem_aula_nem_plano_diz(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn, plano=[], cal={})
    secoes = _secoes(_index(raiz))
    assert [s[0] for s in secoes] == [], "s218: sem plano nao ha semana; a RD mora na Biblioteca"
    assert _biblioteca(_index(raiz)) == ["rd-renal", "hernias", "bayes"], \
        "CM (a RD) e 'Sem área' (sem plano, a tarefa nao resolve), a mais nova primeiro; a analise nao entra"
    assert hub.html_aulas([]) == '<p class="hub-vazio">Nada no quadro ainda: nem tarefa pendente, nem aula.</p>'


def test_aula_ligada_so_a_tarefa_concluida_fica_na_biblioteca(tmp_path):
    """s216 (part-3, decisao do operador em 05/10: "so daqui em diante"): a aula cuja tarefa ja foi
    concluida nao e mais "candidata a arquivo" (o `git mv` para artifacts/arquivo/ acabou): fica na
    Biblioteca da Teoria, a um toque, sem aviso no build."""
    raiz, data_fn = _repo(tmp_path, slugs=("hernias",))
    plano = [_t(49, 2, "Hernias", 21, URL, status="feita")]
    _m, _p, avisos = _construir(raiz, data_fn, plano=plano)
    assert not [a for a in avisos if "arquivo" in a], avisos
    assert _biblioteca(_index(raiz)) == ["hernias"]
    assert "artifacts/arquivo" not in Path(hub.__file__).read_text(encoding="utf-8").split('"""', 2)[2], \
        "o hub nao manda mais mover aula para artifacts/arquivo/"


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
    assert [s[0] for s in _secoes(_index(raiz))] == [] and _biblioteca(_index(raiz)) == ["hernias"]


def test_teoria_sem_o_quadrado_feito_e_o_estado_segue_no_db(tmp_path):
    """P20 (s219): o quadrado 'feito' saiu da pagina inteira (HTML, CSS e JS) e, com ele, o que so
    existia para ele (o aviso "Marcar como feita nao funciona nesta visualizacao", o `disabled`, o
    clique). Fica o que a assinatura usa: `quadro/<slug>` no db, o item com `data-slug`, o movimento
    para a Biblioteca e o aviso de quando o db nao salvou."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert "qd-feito" not in pagina and "Marcar como feita" not in pagina and "como feita\"" not in pagina
    assert '<p class="qd-aviso" id="hub-quadro-aviso" role="status" hidden></p>' in pagina
    assert len(re.findall(r'<li class="qd-item[^"]*"[^>]*data-slug=', pagina)) == 2, \
        "bayes + a RD avulsa (s216: a analise saiu) seguem com a chave do quadro"
    js = pagina.split("function iniciarQuadro()", 1)[1].split("// ---", 1)[0]
    assert 'db.collection("quadro")' in js and "semArmazenamento" in js
    assert ".set({feito: novo, ts: new Date().toISOString()})" in js
    assert 'querySelectorAll(".qd-item[data-slug]")' in js, "so item com slug entra no estado"
    assert '.qd-sem[data-secao="' in js, "o item que volta a pendente vai para a SUA secao"
    assert 'addEventListener("click"' not in js and ".disabled" not in js, "nada a clicar no quadro"


def test_quadro_celular_alvo_de_toque_e_grid_item_encolhe(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert "sticky" not in pagina.lower() and "nowrap" not in pagina.lower()
    assert ".qd-feito" not in pagina and "padding-right:66px" not in pagina, "P20: o quadrado e a folga dele sairam"
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
    """O "Ir para os cards" e o "abrir aula" do painel sao interceptados pelo hub. s216 (part-1, A1):
    o documento abre DIRETO pelo href do link clicado -- procurar o `a.hub-aula` na Teoria deixava o
    Dossie e a Autopsia (que sairam de la) sem abrir."""
    corpo = extrair_funcao(TEMPLATE_HUB_REAL, "function preparar(quadro){")
    assert 'querySelectorAll("a[data-hub-aba], a[data-hub-aula]")' in corpo
    assert "painelAtalho(a" in corpo
    atalho = extrair_funcao(TEMPLATE_HUB_REAL, "function painelAtalho(a")
    assert "abrirNaTeoria(" in atalho and "a.hub-aula" not in atalho and "abrirAula(alvo)" not in TEMPLATE_HUB_REAL
    assert "abrirAula(href, titulo, origem)" in extrair_funcao(TEMPLATE_HUB_REAL, "function abrirNaTeoria(")


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
    d = _decidir(raiz, estado={"rd-renal": {"feito": True}})   # s216: a analise nao mora na Teoria
    assert d["acao"] == "mesmo_lote" and d["motivos"] == ["quadro de aulas mudou"]


def test_plano_mudou_republica_o_mesmo_lote(tmp_path):
    """s195: tarefa concluida (ou nova) muda o quadro, logo a projecao -- sem lote novo. s216
    (part-1): a tarefa da TEORIA (de aula ou com aula ligada); lista sem aula concluida muda so o
    Painel (o E01: o `mesmo_lote` sobe so o `painel.html`)."""
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    plano = [dict(l) for l in PLANO]
    plano[1]["status"] = "feita"                        # a 877, tarefa de aula
    d = _decidir(raiz, plano=plano)
    assert d["acao"] == "mesmo_lote" and d["motivos"] == ["quadro de aulas mudou"]
    plano = [dict(l) for l in PLANO]
    plano[0]["status"] = "feita"                        # a 26, lista sem aula: fora da Teoria, MAS
    # s218: o total real de questoes da semana (a linha "Questoes atrasadas") muda -- republica
    assert _decidir(raiz, plano=plano)["motivos"] == ["quadro de aulas mudou"]
    plano = [dict(l) for l in PLANO]
    plano[0]["q_previstas"] = 19.0                      # o mesmo numero: nada muda
    assert _decidir(raiz, plano=plano)["acao"] == "nada"


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
    monkeypatch.setattr(hub, "questoes_no_hub", lambda: {})   # s201/P20: hermetico (nao ler o banco real)
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


# --------------------------------------------------------------------------
# Aba Questoes por semana (s200): o calendario vai para a pagina com a MESMA regua do quadro
# --------------------------------------------------------------------------

def test_semanas_da_aba_questoes_usam_a_regua_do_quadro():
    cal = {1: (date(2026, 9, 14), date(2026, 9, 20)), 2: (date(2026, 9, 21), date(2026, 9, 27)),
           3: (date(2026, 9, 28), date(2026, 10, 4))}
    linhas = [{"status": "pendente", "semana_plano": 1}, {"status": "pendente", "semana_plano": 3}]
    html_ = hub.html_semanas(linhas, cal, date(2026, 9, 26))
    dados = json.loads(re.search(r'id="hub-semanas">(.*)</script>', html_).group(1))
    assert dados["atual"] == hub.semana_atual(cal, date(2026, 9, 26), linhas) == 2
    assert dados["datas"]["2"] == ["21/09", "27/09"]
    # sem calendario: a menor semana com pendencia, como no quadro; nada inventado
    assert json.loads(re.search(r'>(.*)</script>', hub.html_semanas(linhas, {}, date(2026, 9, 26)))
                      .group(1)) == {"atual": 1, "datas": {}}


def test_pagina_real_leva_o_calendario_das_semanas_uma_vez():
    pagina = hub.montar_index(TEMPLATE_HUB_REAL, TEMPLATE_PLAYER_REAL, {"sessao": "x", "cards": []},
                              [], True, datetime(2026, 9, 26, 12, 0),
                              calendario={2: (date(2026, 9, 21), date(2026, 9, 27))})
    assert pagina.count('id="hub-semanas"') == 1
    assert "@hub:semanas" not in pagina


def test_simulado_no_hub_na_teoria_abre_a_aula_e_nao_a_lista(tmp_path):
    """⚰️ s201 na Teoria: o simulado com questoes no banco ganhava 'resolver no hub' (aba Listas em
    Simulados). P21 (s220, pedido do operador em 07/10: "se estou na teoria, abro automaticamente a
    aula"): o cartao da Teoria abre a aula; o atalho para as questoes segue no Painel."""
    raiz, data_fn = _repo(tmp_path)
    plano = [dict(l, no_hub=True) if l["id"] == 1793 else l for l in PLANO]
    # s216 (part-1): so com aula ligada o simulado aparece na Teoria
    _construir(raiz, data_fn, plano=plano, quadro=dict(QUADRO, hernias=dict(QUADRO["hernias"], tarefas=[49, 1793])))
    simulado = _item(_index(raiz), 'data-tarefa="1793"')
    assert "resolver no hub" not in simulado and "data-hub-aba" not in simulado
    assert "prova em PDF no computador" not in simulado and "simulados/uerj" not in simulado
    assert '<a class="qd-bloco qd-alvo hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias">' in simulado


def test_lista_na_teoria_nao_leva_link_de_lista_nem_do_emed(tmp_path):
    """⚰️ s213 (D4-1) na Teoria: a lista com questoes no banco abria a aba Listas, e fora do banco o
    "abrir lista" do EMED. P21 (s220): a Teoria e a aula -- nenhum link de lista, com ou sem banco; a
    precedencia D4-1 ("nao sair do medhub") segue no Painel (`test_painel`)."""
    raiz, data_fn = _repo(tmp_path)
    plano = [dict(l, no_hub=True) if l["id"] == 49 else l for l in PLANO]
    # s216 (part-1): a 68 so aparece na Teoria com aula ligada
    _construir(raiz, data_fn, plano=plano, quadro=dict(QUADRO, hernias=dict(QUADRO["hernias"], tarefas=[49, 68])))
    pagina = _index(raiz)
    for tid in (49, 68):
        item = _item(pagina, 'data-tarefa="%d"' % tid)
        assert "resolver no hub" not in item and "abrir lista" not in item and URL not in item, tid
        assert item.count("<a ") == 1 and '<a class="qd-bloco qd-alvo hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias">' in item, "a aula que prepara e o alvo"


def test_painel_remede_ao_abrir_semana():
    """s213 (D4-3): abrir um `<details>` dentro do iframe do Painel (semana da rota, "Ver as
    outras") re-mede a altura; sem isso a semana aberta vira rolagem aninhada no celular. O
    `toggle` nao borbulha: o ouvinte e de CAPTURA no documento do iframe."""
    assert 'doc.addEventListener("toggle", function(){ medir(quadro); }, true);' in TEMPLATE_HUB_REAL


def test_leitor_do_plano_marca_as_tarefas_com_questoes_no_banco(monkeypatch):
    """P20 (s219): a marca `no_hub` (resolve na aba Listas) e a contagem `q_hub` saem da MESMA leitura
    (`plano.questoes_no_hub`, o criterio do `--exportar`); sem a leitura, ninguem marcado."""
    monkeypatch.setattr(hub.db, "plano_listar", lambda: [dict(l) for l in PLANO])
    monkeypatch.setattr(hub, "questoes_no_hub", lambda: {1793: 59, 875: 15})
    linhas, aviso = hub._ler_plano()
    assert aviso is None
    por_id = {l["id"]: l for l in linhas}
    assert por_id[1793]["no_hub"] is True and por_id[1793]["q_hub"] == 59
    assert por_id[875]["no_hub"] is True and por_id[875]["q_hub"] == 15
    assert not any(l.get("no_hub") for l in linhas if l["id"] not in (1793, 875))

    def quebra():
        raise RuntimeError("sem tabela")
    monkeypatch.setattr(hub, "questoes_no_hub", quebra)
    linhas, aviso = hub._ler_plano()
    assert aviso is None and not any(l.get("no_hub") or l.get("q_hub") for l in linhas)


# ------------------------------------------------ 5. o quadro conclui sozinho (s214)
# Hotfix `.vibeflow/hotfixes/2026-10-04-assinar-nao-conclui.md`. Pedido do operador em 04/10/2026:
# "mesmo assinando as listas, elas nao sao 'resolvidas', tendo que clicar no concluir do lado de fora".
# No banco: assinou `doc_rd-hepato` as 20:45:07 e tocou "feito" em `quadro/rd-hepato` as 20:45:13 (o
# mesmo em rd-hemostasia e rd-vias-biliares). As funcoes REAIS (`iniciarQuadro`, `assinaEnviar`,
# `assinaPintar`...) rodam em node sobre o quadro REAL de `hub.html_quadro_de`, num DOM falso minimo
# com seletor proprio, e um banco falso em memoria.

HOJE = date(2026, 10, 4)
# o estado de 04/10 minimizado: 3 RD avulsas (revisoes) e 4 tarefas de lista (t26 e t1793 resolvidas
# no banco, t49 e t68 capturadas); hoje = semana 3, logo 1 e 2 sao Atrasadas
PLANO_QD = [_t(26, 1, "Diabetes na Gestação", 19, URL),
            _t(49, 2, "Hérnias da Parede Abdominal", 21, URL, bloco="CIR"),
            _t(1793, 2, "UERJ 2021 -- prova inteira", 60, "simulados/uerj/2021.pdf", bloco="Simulado",
               area="Simulado"),
            _t(68, 3, "Doenças Glomerulares", 21, URL, bloco="CM")]
AULAS = [hub.Aula(s, s, "2026-10-0%d" % (i + 1), "artifacts/aula-%s.html" % s)
         for i, s in enumerate(("rd-hemostasia", "rd-hepato", "rd-vias-biliares", "prep"))]
REGISTRO = {s: {"tipo": "revisao", "titulo": "Revisão direcionada " + s[3:], "disciplinas": [d]} for s, d in
            (("rd-hemostasia", "Hematologia"), ("rd-hepato", "Hepatologia"), ("rd-vias-biliares", "Cirurgia"))}
# s216 (part-1): lista so mora na Teoria com aula ligada -- uma aula que prepara as 4 mantem o cenario
REGISTRO["prep"] = {"tipo": "aula", "titulo": "Aula que prepara", "tarefas": [26, 49, 68, 1793]}
QUADRO_HTML = hub.html_quadro_de(AULAS, REGISTRO, {}, PLANO_QD, CAL, HOJE)[0]
LEITOR_HTML = TEMPLATE_HUB_REAL.split('<div id="hub-leitor" hidden>', 1)[1].split("</section>", 1)[0]
LISTAS = {"t26": {"status": "resolvida", "tarefa": 26}, "t49": {"status": "capturada", "tarefa": 49},
          "t1793": {"status": "resolvida", "tarefa": 1793}, "t68": {"status": "capturada", "tarefa": 68}}
FEITA = {"feito": True, "ts": "2026-10-04T18:02:33.000Z"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _Arvore(HTMLParser):
    """HTML -> {t, a, c, x} (tag, atributos, filhos, texto) para o DOM falso montar."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = {"t": "body", "a": {}, "c": [], "x": ""}
        self.pilha = [self.raiz]

    def handle_starttag(self, tag, attrs):
        no = {"t": tag, "a": {k: "" if v is None else v for k, v in attrs}, "c": [], "x": ""}
        self.pilha[-1]["c"].append(no)
        if tag not in VOID:
            self.pilha.append(no)

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, 0, -1):
            if self.pilha[i]["t"] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        self.pilha[-1]["x"] += data


def _arvore(html):
    p = _Arvore()
    p.feed(html)
    return p.raiz


def _opcional(padrao):
    m = re.search(padrao, TEMPLATE_HUB_REAL)
    return m.group(1) if m else ""


#: s216 (part-2): a marca de listas/* mora em funcoes de TOPO (a Teoria e o Painel as chamam)
FUNCS_LISTAS = "\n".join(
    [re.search(r"\n  (var LISTAS_VIVAS = [^\n]+;)", TEMPLATE_HUB_REAL).group(1)] +
    [extrair_funcao(TEMPLATE_HUB_REAL, a) for a in (
        "function listasResolvidas(docs){", "function listasPintar(alvo){",
        "function marcarListasEm(raiz, db, aplicar, depois){")])

FUNCS_QD = "\n".join(
    [re.search(r"\n  (var %s = [^\n]+;)" % n, TEMPLATE_HUB_REAL).group(1)
     for n in ("ASSINA", "PEND_ERRO", "PEND_LEITURA", "PEND_ABSORVIDO")] +
    [_opcional(r"\n  (var quadroMarcarFeito = [^\n]+;)")] +
    [extrair_funcao(TEMPLATE_HUB_REAL, a) for a in (
        "function pendDataCurta(iso){", "function pendEstadoDoc(item){",
        "function pendTextoInicial(estado, rascunho){", "function pendAssinatura(slug, comentario, agora){",
        "function assinaPintar(){", "function assinaEnviar(){", "function assinaVoltar(slug, ok){",
        "function iniciarQuadro(){")] +
    [FUNCS_LISTAS])

# DOM falso: arvore de El com seletor de compostos (tag, #id, .classe, [attr], [attr="v"],
# :not([attr])) e combinador descendente -- o que o quadro e o rodape usam, nada alem
DOM_QD = r"""
function El(tag, attrs){ this.tagName = String(tag).toUpperCase(); this.attrs = {}; for(var k in attrs){ this.attrs[k] = attrs[k]; }
  this.children = []; this.parentNode = null; this._ouv = {}; this._texto = ""; this.offsetWidth = 1; this.style = {}; var el = this;
  this.classList = {add: function(c){ var cs = el._cls(); if(cs.indexOf(c) < 0){ cs.push(c); el.attrs["class"] = cs.join(" "); } },
    remove: function(c){ el.attrs["class"] = el._cls().filter(function(x){ return x !== c; }).join(" "); },
    contains: function(c){ return el._cls().indexOf(c) >= 0; }}; }
El.prototype._cls = function(){ return String(this.attrs["class"] || "").split(/\s+/).filter(Boolean); };
El.prototype.getAttribute = function(k){ return Object.prototype.hasOwnProperty.call(this.attrs, k) ? String(this.attrs[k]) : null; };
El.prototype.setAttribute = function(k, v){ this.attrs[k] = String(v); };
El.prototype.removeAttribute = function(k){ delete this.attrs[k]; };
El.prototype.hasAttribute = function(k){ return Object.prototype.hasOwnProperty.call(this.attrs, k); };
["hidden", "disabled", "open"].forEach(function(p){ Object.defineProperty(El.prototype, p, {
  get: function(){ return this.hasAttribute(p); }, set: function(v){ if(v){ this.attrs[p] = ""; } else { delete this.attrs[p]; } }}); });
Object.defineProperty(El.prototype, "className", {get: function(){ return this.getAttribute("class") || ""; }, set: function(v){ this.attrs["class"] = String(v); }});
Object.defineProperty(El.prototype, "textContent", {
  get: function(){ return this._texto + this.children.map(function(c){ return c.textContent; }).join(""); },
  set: function(v){ this.children.forEach(function(c){ c.parentNode = null; }); this.children = []; this._texto = String(v); }});
El.prototype.appendChild = function(n){ if(n.parentNode){ n.parentNode.removeChild(n); } n.parentNode = this; this.children.push(n); return n; };
El.prototype.insertBefore = function(n, ref){ if(ref == null){ return this.appendChild(n); } if(n.parentNode){ n.parentNode.removeChild(n); }
  this.children.splice(this.children.indexOf(ref), 0, n); n.parentNode = this; return n; };
El.prototype.removeChild = function(n){ var i = this.children.indexOf(n); if(i >= 0){ this.children.splice(i, 1); } n.parentNode = null; return n; };
El.prototype.addEventListener = function(t, f){ (this._ouv[t] = this._ouv[t] || []).push(f); };
El.prototype.click = function(){ (this._ouv.click || []).forEach(function(f){ f({}); }); };
function parseSel(s){ var c = {tag: null, cls: [], tem: [], igual: [], nao: []}, t = /^[a-zA-Z][a-zA-Z0-9]*/.exec(s);
  if(t){ c.tag = t[0].toUpperCase(); s = s.slice(t[0].length); }
  var resto = s.replace(/#([\w-]+)|\.([\w-]+)|:not\(\[([\w-]+)\]\)|\[([\w-]+)(?:="([^"]*)")?\]/g, function(_, id, cl, nao, at, val){
    if(id){ c.igual.push(["id", id]); } else if(cl){ c.cls.push(cl); } else if(nao){ c.nao.push(nao); }
    else if(val !== undefined){ c.igual.push([at, val]); } else { c.tem.push(at); } return ""; });
  if(resto){ throw new Error("seletor fora do DOM falso: " + resto); } return c; }
function casaUm(e, c){ return (!c.tag || e.tagName === c.tag) && c.cls.every(function(x){ return e._cls().indexOf(x) >= 0; }) &&
  c.tem.every(function(a){ return e.hasAttribute(a); }) && c.nao.every(function(a){ return !e.hasAttribute(a); }) &&
  c.igual.every(function(p){ return e.getAttribute(p[0]) === p[1]; }); }
function casa(e, partes){ if(!casaUm(e, partes[partes.length - 1])){ return false; }
  var i = partes.length - 2, p = e.parentNode; while(i >= 0 && p){ if(casaUm(p, partes[i])){ i--; } p = p.parentNode; } return i < 0; }
function desc(n, f){ n.children.forEach(function(c){ f(c); desc(c, f); }); }
El.prototype.querySelectorAll = function(sel){ var partes = sel.trim().split(/\s+/).map(parseSel), out = [];
  desc(this, function(e){ if(casa(e, partes)){ out.push(e); } }); return out; };
El.prototype.querySelector = function(sel){ return this.querySelectorAll(sel)[0] || null; };
function montar(no){ var e = new El(no.t, no.a); e._texto = no.x; no.c.forEach(function(f){ e.appendChild(montar(f)); }); return e; }
var DOC = montar(__ARVORE__);
var document = {activeElement: null, createElement: function(t){ return new El(t, {}); }};
function $(id){ var r = null; desc(DOC, function(e){ if(!r && e.getAttribute("id") === id){ r = e; } }); return r; }
"""

# banco falso: quadro e listas em memoria; onSnapshot avisa de novo a cada escrita; `negar` simula a
# regra de leitura (callback de erro); escritas registradas
BANCO_QD = r"""
var CFG = __CFG__, BANCO = {quadro: CFG.quadro || {}, listas: CFG.listas || {}, "analises/pendencias/itens": CFG.pend || {}},
    ESCRITAS = [], OUV = {}, GRAVADAS = [], VOLTOU = [];
function foto(nome){ return {docs: Object.keys(BANCO[nome] || {}).map(function(id){ return {id: id, data: function(){ return BANCO[nome][id]; }}; })}; }
var DB = {collection: function(nome){ return {
  where: function(){ return this; },   // s216: o filtro nao importa no banco falso (os docs ja sao os do teste)
  onSnapshot: function(ok, erro){
    if((CFG.negar || []).indexOf(nome) >= 0){ Promise.resolve().then(function(){ erro(new Error("sem permissao")); }); return function(){}; }
    (OUV[nome] = OUV[nome] || []).push(ok); Promise.resolve().then(function(){ ok(foto(nome)); }); return function(){}; },
  doc: function(id){ return {set: function(d){
    if(CFG.falhaQuadro){ return Promise.reject(new Error("fora")); }
    ESCRITAS.push([nome, id, d]); (BANCO[nome] = BANCO[nome] || {})[id] = d;
    Promise.resolve().then(function(){ (OUV[nome] || []).forEach(function(f){ f(foto(nome)); }); });
    return Promise.resolve(); }}; }}; }};
var window = {claude: {use: function(){ return Promise.resolve(CFG.semDb ? null : DB); }}};
function pendGravar(id, dados){ if(CFG.falhaAssina){ return Promise.reject(new Error("fora")); } GRAVADAS.push(id); return Promise.resolve(); }
function pendRascunho(){ return null; }
function assinaLer(){}
// s216 (part-4, A11): o voltar a origem e do leitor; aqui so registra QUANDO foi chamado e o que estava na tela
function voltarOrigem(slug){ VOLTOU.push([slug, $("hub-assina-st").textContent]); }
"""

ACAO_QD = r"""
function espera(){ return new Promise(function(ok){ setTimeout(ok, 0); }); }
function estado(){
  var itens = {};
  DOC.querySelectorAll(".qd-item").forEach(function(li){
    var onde = null, p = li.parentNode;
    while(p){ if(p.getAttribute("id") === "hub-quadro-feitas"){ onde = "feitas"; break; }
      if(p.tagName === "SECTION" && p.hasAttribute("data-secao")){ onde = p.getAttribute("data-secao"); break; } p = p.parentNode; }
    var marca = li.querySelector(".qd-registro");
    itens[li.getAttribute("data-slug") || "t" + li.getAttribute("data-tarefa")] =
      {onde: onde, feito: li.hasAttribute("data-feito"), marca: marca ? marca.textContent : null};
  });
  var secoes = {}; DOC.querySelectorAll(".qd-sem").forEach(function(s){ secoes[s.getAttribute("data-secao")] = s.querySelector("[data-n]").textContent; });
  // s217 (P17): os grupos de grande area da Biblioteca, na ordem da pagina, com os itens de cada um
  var grupos = DOC.querySelectorAll(".qd-area").map(function(g){ return [g.getAttribute("data-area"),
    g.querySelectorAll(".qd-item").map(function(li){ return li.getAttribute("data-slug") || "t" + li.getAttribute("data-tarefa"); })]; });
  var nv = $("hub-quadro-novas");
  return {itens: itens, secoes: secoes, grupos: grupos, escritas: ESCRITAS, gravadas: GRAVADAS, st: $("hub-assina-st").textContent, voltou: VOLTOU,
          nfeitas: $("hub-quadro-nfeitas").textContent, novas: nv && !nv.hidden ? nv.textContent : "", aviso_oculto: $("hub-quadro-aviso").hidden};
}
var qd = $("hub-quadro");
iniciarQuadro();
espera().then(function(){
  if(CFG.assinar){ ASSINA.slug = CFG.assinar; ASSINA.item = CFG.assinado || null; $("hub-assina-coment").value = ""; assinaEnviar(); }
  return espera();
}).then(espera).then(function(){ return new Promise(function(ok){ setTimeout(ok, CFG.esperaMs || 0); }); })
  .then(function(){ console.log(JSON.stringify(estado())); });
"""


def _rodar_qd(**cfg):
    if not NODE:
        pytest.skip("node ausente no PATH: conclusao automatica do quadro nao verificada (skip declarado)")
    arvore = _arvore(LEITOR_HTML + QUADRO_HTML)
    prog = (DOM_QD.replace("__ARVORE__", json.dumps(arvore, ensure_ascii=False)) +
            BANCO_QD.replace("__CFG__", json.dumps(cfg, ensure_ascii=False)) + FUNCS_QD + "\n" + ACAO_QD)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8",
                             timeout=60, env=dict(os.environ, TZ="America/Sao_Paulo"))
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_o_quadro_de_partida_e_o_do_dia():
    """Sanidade do cenario: as 3 RD na Biblioteca (s218), as listas em Atrasadas/Semana 3, nada feito."""
    out = _rodar_qd()
    assert {k: v["onde"] for k, v in out["itens"].items()} == {
        "rd-hemostasia": "feitas", "rd-hepato": "feitas", "rd-vias-biliares": "feitas",
        "t26": "atrasadas", "t49": "atrasadas", "t1793": "atrasadas", "t68": "3"}
    assert out["escritas"] == [] and out["nfeitas"] == "3" and out["novas"] == "3 novas"


# ------------------------------------------------ 5a. assinar = concluir

def test_assinar_a_leitura_conclui_o_item_do_quadro():
    """O 04/10 dele: rd-hemostasia ja feita; assina rd-hepato -> quadro/rd-hepato feito, sem 2o toque."""
    out = _rodar_qd(quadro={"rd-hemostasia": FEITA}, assinar="rd-hepato")
    assert out["gravadas"] == ["doc_rd-hepato"]
    assert [e[:2] for e in out["escritas"]] == [["quadro", "rd-hepato"]], "uma escrita, no doc do quadro"
    assert out["escritas"][0][2]["feito"] is True and out["escritas"][0][2]["ts"].startswith("20")
    assert out["itens"]["rd-hepato"] == {"onde": "feitas", "feito": True, "marca": None}
    assert out["itens"]["rd-vias-biliares"] == {"onde": "feitas", "feito": False, "marca": None}
    assert out["nfeitas"] == "3" and out["novas"] == "1 nova", "s218: lida, a RD deixa de ser nova"
    assert out["st"] == "Assinado e concluído", out["st"]


@pytest.mark.parametrize("cfg", [
    {"quadro": {"rd-hemostasia": FEITA}, "assinar": "rd-hemostasia"},   # ja feito: nao regrava
    {"assinar": "dossie-uerj"},                                           # documento fora do quadro
    {"assinar": "rd-hepato", "semDb": True},                              # quadro sem banco
    {"assinar": "rd-hepato", "falhaAssina": True},                        # a assinatura nao gravou
], ids=["ja-feito", "fora-do-quadro", "sem-banco", "assinatura-falhou"])
def test_assinar_nao_regrava_nem_inventa(cfg):
    out = _rodar_qd(**cfg)
    assert out["escritas"] == []
    assert "concluído" not in out["st"]
    if cfg["assinar"] == "rd-hemostasia":
        assert out["itens"]["rd-hemostasia"]["onde"] == "feitas", "assinar nunca desmarca"
    else:
        assert out["itens"]["rd-hepato"] == {"onde": "feitas", "feito": False, "marca": None}


def test_quadro_que_nao_salva_desfaz_a_tela_e_avisa():
    """A assinatura gravou, o quadro nao: o item volta para a secao, o aviso aparece, o rodape nao mente."""
    out = _rodar_qd(assinar="rd-hepato", falhaQuadro=True)
    assert out["gravadas"] == ["doc_rd-hepato"] and out["escritas"] == []
    assert out["itens"]["rd-hepato"] == {"onde": "feitas", "feito": False, "marca": None}
    assert out["novas"] == "3 novas", "desfeito, volta a ser nova"
    assert out["aviso_oculto"] is False
    assert out["st"].startswith("Assinado em "), out["st"]


# ------------------------------------------------ 5b. lista resolvida sai da semana

def test_lista_resolvida_vai_para_concluidas_com_selo_sem_gravar():
    out = _rodar_qd(listas=LISTAS)
    for t in ("t26", "t1793"):
        assert out["itens"][t] == {"onde": "feitas", "feito": True, "marca": "resolvida · registro pendente"}
    assert out["itens"]["t49"] == {"onde": "atrasadas", "feito": False, "marca": None}
    assert out["itens"]["t68"]["onde"] == "3"
    assert out["escritas"] == [], "a lista resolvida so muda a tela; o plano e do backend"
    assert out["secoes"]["atrasadas"] == "1" and out["nfeitas"] == "5", "2 listas + as 3 RDs da Biblioteca"


def test_sem_leitura_de_listas_o_quadro_fica_como_o_build():
    """Hub aberto por link (regra `listas` = leitura do dono): nada se move, o resto do quadro segue."""
    out = _rodar_qd(listas=LISTAS, negar=["listas"], quadro={"rd-hemostasia": FEITA})
    assert out["itens"]["t26"] == {"onde": "atrasadas", "feito": False, "marca": None}
    assert out["itens"]["rd-hemostasia"]["onde"] == "feitas"
    assert out["escritas"] == []


# ------------------------------------------------ 6. s216 (hub-integracao part-2): o Painel le listas/*
# Pedido do operador em 05/10/2026 ("integracao, remocao de redundancias"): uma lista resolvida na aba
# Listas aparecia resolvida na Teoria e ABERTA no Painel, ate o proximo tique. As MESMAS funcoes de topo
# (`marcarListasEm` & cia.) pintam os dois, de uma assinatura so de listas/*; casam pelo campo `tarefa`
# do doc, nao pelo id (A4: `t49_1` conta para a 49). O Painel so LE.

def _painel_html():
    from tools import painel

    def t(id_, tema, classe="lista", url=URL, q=21):
        return {"id": id_, "semana": 3, "atrasada": False, "tema": tema, "q": q, "classe": classe,
                "url_lista": url, "area": None, "rotulo": "CM", "aula": None, "aulas": [], "no_hub": False}
    return ('<ol class="tarefas">%s</ol>' % "".join(painel._html_tarefa(x) for x in (
        t(26, "Diabetes na Gestação"), t(49, "Hérnias"), t(68, "Glomerulares"),
        t(877, "Raciocínio", classe="aula", url=None, q=0))) +
        painel._html_docs([{"slug": "dossie-uerj", "titulo": "Dossiê UERJ"}]))


ACAO_PAINEL = r"""
function espera(){ return new Promise(function(ok){ setTimeout(ok, 0); }); }
var MEDIU = 0;
function estado(raiz){ var o = {};
  raiz.querySelectorAll("li.tarefa").forEach(function(li){ var s = li.querySelector(".qd-registro");
    o[li.getAttribute("data-tarefa") || "doc"] = {resolvida: li.classList.contains("t-resolvida"), marca: s ? s.textContent : null}; });
  return o; }
var SAIDA = {};
marcarListasEm($("pa"), CFG.semDb ? null : DB, null, function(){ MEDIU++; });
espera().then(espera).then(function(){
  SAIDA.a = estado($("pa")); SAIDA.mediu = MEDIU;
  // o Painel que carrega DEPOIS do snapshot (a aba abriu agora): pinta na hora, sem esperar evento
  marcarListasEm($("pb"), null, null, null); SAIDA.b_na_hora = estado($("pb"));
  if(!CFG.negar){ DB.collection("listas").doc("t26").set({status: "capturada", tarefa: 26});
                  DB.collection("listas").doc("t68").set({status: "resolvida", tarefa: 68}); }
  return espera();
}).then(espera).then(function(){ SAIDA.depois = estado($("pa")); SAIDA.escritas_painel = ESCRITAS.length;
  console.log(JSON.stringify(SAIDA)); });
"""


def _rodar_painel(**cfg):
    if not NODE:
        pytest.skip("node ausente no PATH: marca do Painel nao verificada (skip declarado)")
    arvore = _arvore('<div id="pa">%s</div><div id="pb">%s</div>' % (_painel_html(), _painel_html()))
    prog = (DOM_QD.replace("__ARVORE__", json.dumps(arvore, ensure_ascii=False)) +
            BANCO_QD.replace("__CFG__", json.dumps(cfg, ensure_ascii=False)) + FUNCS_LISTAS + "\n" + ACAO_PAINEL)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8",
                             timeout=60, env=dict(os.environ, TZ="America/Sao_Paulo"))
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


LISTAS_PAINEL = {"t26": {"status": "resolvida", "tarefa": 26}, "t49_1": {"status": "resolvida", "tarefa": 49},
                 "t68": {"status": "capturada", "tarefa": 68}}
SELO = "resolvida · registro pendente"


def test_lista_resolvida_pinta_o_painel_sem_publish():
    out = _rodar_painel(listas=LISTAS_PAINEL)
    assert out["a"]["26"] == {"resolvida": True, "marca": SELO}
    assert out["a"]["49"] == {"resolvida": True, "marca": SELO}, "A4: t49_1 conta para a tarefa 49"
    assert out["a"]["68"] == {"resolvida": False, "marca": None}
    assert out["a"]["877"] == {"resolvida": False, "marca": None}
    assert out["a"]["doc"] == {"resolvida": False, "marca": None}, "a Documentacao nao e tarefa do plano"
    assert out["mediu"] >= 1, "o Painel cresce ao pintar: o hub mede o iframe de novo"
    assert out["b_na_hora"]["26"]["resolvida"] is True, "quem chega depois do snapshot pinta na hora"
    assert out["depois"]["26"] == {"resolvida": False, "marca": None}, "voltou a capturada: a marca sai"
    assert out["depois"]["68"] == {"resolvida": True, "marca": SELO}
    assert out["escritas_painel"] == 2, "so as 2 escritas do proprio teste: o Painel nunca grava"


def test_sem_leitura_de_listas_o_painel_fica_como_o_build():
    out = _rodar_painel(listas=LISTAS_PAINEL, negar=["listas"])
    assert all(v == {"resolvida": False, "marca": None} for v in out["a"].values())
    assert all(v == {"resolvida": False, "marca": None} for v in out["b_na_hora"].values())


def test_painel_liga_o_selo_ao_carregar():
    corpo = extrair_funcao(TEMPLATE_HUB_REAL, "function preparar(quadro){")
    assert 'quadro.id === "hub-painel-quadro"' in corpo and "painelListas(doc, quadro)" in corpo
    liga = extrair_funcao(TEMPLATE_HUB_REAL, "function painelListas(doc, quadro){")
    assert "marcarListasEm(doc," in liga and "medir(quadro)" in liga and ".qd-registro" in liga
    ini = extrair_funcao(TEMPLATE_HUB_REAL, "function iniciarQuadro(){")
    assert "marcarListasEm(qd, db," in ini and "function marcarListas(db)" not in ini, "uma regra so, de topo"


def test_p21_sem_ligacoes_da_aba_listas_na_pagina_nem_na_projecao(tmp_path):
    """⚰️ s216 part-2 (F4) / s218 (P2): o `<script id="hub-ligacoes">` (tarefa -> aulas e resumos) so
    existia para os links "abrir aula"/"resumo: ..." debaixo das listas da aba Listas, e o hash dele
    entrava na projecao. P21 (s220): a lista e so a lista -- o JSON, o lugar no template e o motivo
    "ligacoes tarefa -> aula mudaram" sairam; aula ligada a tarefa FORA da Teoria nao muda nada que o
    operador veja, entao nao republica."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert 'id="hub-ligacoes"' not in pagina and "@hub:ligacoes" not in pagina
    assert "ligacoes" not in dict(hub.LUGARES_HUB) and not hasattr(hub, "dados_ligacoes")
    assert "ligacoes" not in json.loads((raiz / "tmp" / "hub" / hub.ESTADO_POS).read_text(encoding="utf-8"))["projecao"]
    hub.confirmar(raiz / "tmp" / "hub", agora=AGORA)
    assert _decidir(raiz)["acao"] == "nada"
    quadro = dict(QUADRO, hernias=dict(QUADRO["hernias"], tarefas=[49, 903]))   # 903 ja feita: fora da Teoria
    d = hub.decidir(_lote(), raiz / "tmp" / "hub", raiz=raiz, notas=[], estado_quadro={}, quadro=quadro,
                    data_fn=_repo_datas(raiz), plano_linhas=list(PLANO), calendario=CAL, agora=AGORA)
    assert d["acao"] == "nada", d["motivos"]
    # o registro de um publish ANTERIOR a P21 (com a chave) nao pede publish por ela
    reg = dict(hub.ler_projecao_registrada(raiz / "tmp" / "hub"), ligacoes="sha-antigo")
    assert hub.precisa_publicar(reg, reg, _lote(), set())["acao"] == "nada"



# ------------------------------------------------ 7. s216 (hub-integracao part-4, P14): assinar fecha e volta
# Pedido do operador em 05/10/2026: "ao marcar/assinar ... automaticamente aquela pagina fosse fechada e
# voltassemos para a pagina anterior". O `voltarOrigem` e stub aqui (A11): o que se prende e QUANDO o
# leitor fecha -- so depois do quadro responder (A10) -- e que falha mantem a pagina aberta.

@pytest.mark.parametrize("cfg,voltou", [
    ({"assinar": "rd-hepato"}, [["rd-hepato", "Assinado e concluído"]]),
    ({"assinar": "dossie-uerj", "esperaMs": 700}, [["dossie-uerj", "Assinado em "]]),
    ({"assinar": "dossie-uerj"}, []),
    ({"assinar": "rd-hemostasia", "quadro": {"rd-hemostasia": FEITA}, "esperaMs": 700}, [["rd-hemostasia", "Assinado em "]]),
    ({"assinar": "rd-hepato", "falhaQuadro": True, "esperaMs": 700}, []),
    ({"assinar": "rd-hepato", "falhaAssina": True, "esperaMs": 700}, []),
    ({"assinar": "rd-hepato", "semDb": True, "esperaMs": 700}, []),
], ids=["concluiu-volta-na-hora", "fora-do-quadro-volta-em-600ms", "fora-do-quadro-antes-dos-600ms",
        "ja-feito-volta-em-600ms", "quadro-falhou-fica-aberta", "assinatura-falhou-fica-aberta",
        "quadro-sem-banco-fica-aberta"])
def test_assinar_fecha_e_volta_para_a_aba_de_origem(cfg, voltou):
    out = _rodar_qd(**cfg)
    assert [v[0] for v in out["voltou"]] == [v[0] for v in voltou]
    for v, esperado in zip(out["voltou"], voltou):
        assert v[1].startswith(esperado[1]), v


# ------------------------------------------------ 8. s217 (P17): a Biblioteca por grande area
# Pedido do operador em 06/10/2026: "a biblioteca nao tem como ser desorganizada. preciso que voce
# organize por grande area (CM, Cir, MFC, Ped ou GO)". Grupos na ordem dele, vazio nao aparece, o mais
# recente primeiro dentro do grupo. A aula herda o bloco da tarefa do plano (a de `tarefa_id` vence;
# senao a primeira de `tarefas`); o item sem tarefa (a RD) declara `bloco` no registro; VARIAS (as
# pilulas) = grupo final "Varias areas", so com item. Sem area resolvivel = defeito ACUSADO pelo build
# e pelo --check, nomeando o slug (WARN, padrao warn-first: o hub do dia nao trava), e o item aparece em
# "Sem area", no fim -- nunca some.

PLANO_BIB = [_t(530, 1, "REMIT", 0, None, fonte="custom", status="feita", bloco="CIR"),
             _t(26, 1, "DMG", 19, URL, status="feita", bloco="GO"),
             _t(40, 2, "DMG II", 19, URL, status="feita", bloco="GO"),
             _t(96, 1, "Topicos em Pediatria", 20, URL, status="feita", bloco="PED"),
             _t(367, 2, "Tireoide", 0, None, fonte="custom", status="feita", bloco="CM"),
             _t(590, 2, "Vulva", 0, None, fonte="custom", status="feita", bloco="GO"),
             _t(875, 3, "Prevencao Quaternaria", 0, None, fonte="custom", bloco="MFC")]
REG_BIB = {"remit": {"tipo": "aula", "titulo": "REMIT", "tarefa_id": 530, "bloco": "CM"},   # o plano vence
           "dmg": {"tipo": "aula", "titulo": "DMG", "tarefas": [26, 40]},
           "mista": {"tipo": "aula", "titulo": "Mista", "tarefa_id": 96, "tarefas": [26]},   # tarefa_id vence
           "tireoide": {"tipo": "aula", "titulo": "Tireoide", "tarefas": [367, 590]},        # a primeira
           "prevq": {"tipo": "aula", "titulo": "Prevencao Quaternaria", "tarefa_id": 875},
           "rd-hepato": {"tipo": "revisao", "titulo": "Hepato", "bloco": "CM"},
           "rd-hernias": {"tipo": "revisao", "titulo": "Hernias", "bloco": "CIR"},
           "rd-pilulas": {"tipo": "revisao", "titulo": "Pilulas", "bloco": "VARIAS"},
           "dossie": {"tipo": "analise", "titulo": "Dossie"}}
DATAS_BIB = {"remit": "2026-10-01", "dmg": "2026-09-20", "mista": "2026-09-25", "tireoide": "2026-10-02",
             "prevq": "2026-10-03", "rd-hepato": "2026-10-04", "rd-hernias": "2026-10-05",
             "rd-pilulas": "2026-10-06", "dossie": "2026-10-06"}
AULAS_BIB = [hub.Aula(s, s, d, "artifacts/aula-%s.html" % s) for s, d in DATAS_BIB.items()]
FEITOS_BIB = {s: FEITA for s in ("prevq", "rd-hernias", "rd-pilulas", "rd-hepato")}


def _grupos(pagina):
    """[(area, rotulo, n, [ids de tarefa | slugs])] das grandes areas da Biblioteca (s218: `<details>` ->
    disciplinas), na ordem da pagina; confere que cada item carrega o `data-area` do grupo em que esta e
    que a contagem e a dos documentos (a RD de varias disciplinas conta 1)."""
    bib = pagina.split('id="hub-quadro-feitas"', 1)[1].split("</section>", 1)[0]
    saida = []
    for m in re.finditer(r'<details class="qd-area" data-area="([A-Z]+)"><summary class="qd-area-tit">'
                         r'<span class="qd-seta" aria-hidden="true"></span>([^<]+) <span class="qd-n" data-n>'
                         r'(\d+)</span>.*?</summary>(.*?)</details>', bib, re.S):
        lis = re.findall(r'<li class="qd-item[^"]*"[^>]*>', m.group(4))
        assert all('data-area="%s"' % m.group(1) in li for li in lis), (m.group(1), lis)
        itens = [a or b for a, b in re.findall(
            r'<li class="qd-item[^"]*"[^>]*?(?:data-tarefa="(\d+)"|data-slug="([\w-]+)")', m.group(4))]
        assert int(m.group(3)) == len(set(itens)), "a contagem do grupo e a dos documentos dele"
        saida.append((m.group(1), m.group(2), int(m.group(3)), itens))
    return saida


def test_biblioteca_agrupa_por_grande_area_na_ordem_do_operador():
    """CM, CIR, MFC, PED, GO e, no fim, "Varias areas"; dentro do grupo, o mais recente primeiro (a
    data de criacao que a Biblioteca ja usava); o feito vem riscado no grupo da tarefa que cumpre."""
    pagina, avisos = hub.html_quadro_de(AULAS_BIB, REG_BIB, FEITOS_BIB, PLANO_BIB, CAL, HOJE)
    # s218: dentro da disciplina (aqui 'Outros': o plano sintetico nao tem `area`), as aulas antes das
    # revisoes ja lidas (a RD nova sobe ao topo; nenhuma aqui)
    assert _grupos(pagina) == [
        ("CM", "Clínica Médica", 2, ["tireoide", "rd-hepato"]),
        ("CIR", "Cirurgia", 2, ["remit", "rd-hernias"]),
        ("MFC", "Medicina de Família e Comunidade", 1, ["875"]),
        ("PED", "Pediatria", 1, ["mista"]),
        ("GO", "Ginecologia e Obstetrícia", 1, ["dmg"]),
        ("VARIAS", "Várias áreas", 1, ["rd-pilulas"])]
    assert 'Biblioteca <span class="qd-n" id="hub-quadro-nfeitas">8</span>' in pagina
    assert 'data-slug="dossie"' not in pagina, "a analise segue fora da Teoria"
    assert not [a for a in avisos if "grande area" in a], avisos
    prevq = _item(pagina, 'data-tarefa="875"')
    assert 'data-feito="1"' in prevq and 'data-secao="3"' in prevq, "riscado, com a origem para desmarcar"
    # a ordem e os rotulos dos grupos vem do build, para a pagina criar o grupo que ainda nao existe
    areas = re.search(r'<div class="qd-areas" data-areas="([^"]+)" data-disc-fim="Outros">', pagina).group(1)
    assert json.loads(html.unescape(areas)) == [list(p) for p in hub.AREAS_BIBLIOTECA]
    assert [p[0] for p in hub.AREAS_BIBLIOTECA] == ["CM", "CIR", "MFC", "PED", "GO", "VARIAS", "SEM"]


def test_grupo_vazio_nao_aparece_e_todo_item_da_teoria_carrega_a_area():
    """Nada feito: as RDs ficam em Revisoes e a Prevencao Quaternaria na semana -- MFC e "Varias areas"
    nao aparecem. Todo item (secao ou Biblioteca) leva `data-area`: e o que o cliente le para mover o
    feito para o grupo certo sem publish."""
    pagina, _ = hub.html_quadro_de(AULAS_BIB, REG_BIB, {}, PLANO_BIB, CAL, HOJE)
    # s218: a RD mora na Biblioteca desde o build (nova); so a MFC (a Prevencao Quaternaria na semana) falta
    assert [g[0] for g in _grupos(pagina)] == ["CM", "CIR", "PED", "GO", "VARIAS"]
    assert 'class="qd-area" data-area="MFC"' not in pagina
    assert [g[3] for g in _grupos(pagina)][:2] == [["rd-hepato", "tireoide"], ["rd-hernias", "remit"]], \
        "a RD nova sobe ao topo da disciplina"
    assert 'data-area="VARIAS"' in _item(pagina, 'data-slug="rd-pilulas"')
    assert 'data-area="MFC"' in _item(pagina, 'data-tarefa="875"')
    assert all("data-area=" in li for li in re.findall(r'<li class="qd-item[^"]*"[^>]*>', pagina))
    vazia, _ = hub.html_quadro_de(AULAS_BIB[:1], REG_BIB, {}, [_t(530, 3, "REMIT", fonte="custom", bloco="CIR")],
                                  CAL, HOJE)
    assert _grupos(vazia) == [] and '<div class="qd-areas" data-areas=' in vazia, \
        "Biblioteca vazia: sem grupo, mas com a ordem para o primeiro feito"


def test_area_da_aula_vem_da_tarefa_do_plano_e_a_da_rd_do_registro():
    blocos = {530: "CIR", 26: "GO", 96: "PED", 367: "CM", 590: "GO"}
    assert hub.grande_area(REG_BIB["remit"], blocos) == "CIR", "o plano vence o `bloco` do registro"
    assert hub.grande_area(REG_BIB["mista"], blocos) == "PED", "tarefas discordam: a de tarefa_id"
    assert hub.grande_area(REG_BIB["tireoide"], blocos) == "CM", "sem tarefa_id: a primeira de `tarefas`"
    assert hub.grande_area(REG_BIB["rd-pilulas"], blocos) == "VARIAS"
    assert hub.grande_area({"tipo": "aula", "tarefa_id": 999, "bloco": "GO"}, blocos) == "GO", \
        "tarefa fora do plano: vale o `bloco` declarado"
    assert hub.grande_area({"tipo": "revisao"}, blocos) is None
    assert hub.grande_area({"tipo": "aula", "tarefas": [999]}, {}) is None


def test_item_sem_area_cai_em_sem_area_e_o_build_e_o_check_acusam_o_slug(tmp_path, capsys):
    reg = dict(REG_BIB, **{"rd-sem": {"tipo": "revisao", "titulo": "RD sem bloco"},
                           "orfa": {"tipo": "aula", "titulo": "Orfa", "tarefa_id": 999},
                           "orfa-com-bloco": {"tipo": "aula", "titulo": "Orfa GO", "tarefa_id": 998, "bloco": "GO"}})
    aulas = AULAS_BIB + [hub.Aula(s, s, d, "artifacts/aula-%s.html" % s) for s, d in
                         (("rd-sem", "2026-10-06"), ("orfa", "2026-09-01"), ("orfa-com-bloco", "2026-09-02"))]
    pagina, avisos = hub.html_quadro_de(aulas, reg, dict(FEITOS_BIB, **{"rd-sem": FEITA}), PLANO_BIB, CAL, HOJE)
    grupos = _grupos(pagina)
    assert grupos[-1] == ("SEM", "Sem área", 2, ["orfa", "rd-sem"]), "no fim; a aula antes da RD lida"
    assert ("GO", "Ginecologia e Obstetrícia", 2, ["dmg", "orfa-com-bloco"]) in grupos
    sem = [a for a in avisos if "grande area" in a]
    assert len(sem) == 2 and "rd-sem" in sem[0] and "orfa" in sem[1] and "#999" in sem[1], sem
    assert all("bloco" in a and hub.QUADRO_REG in a for a in sem)
    # plano fora (o build ja avisa "plano indisponivel"): a aula com tarefa nao vira defeito de registro
    _p, degradado = hub.html_quadro_de([a for a in AULAS_BIB if a.slug == "dmg"], REG_BIB, {}, [], {}, HOJE)
    assert not [a for a in degradado if "grande area" in a], degradado
    # o --check le a pagina montada e acusa pelo slug, sem mudar o exit (warn-first)
    assert hub.sem_area_na_pagina(pagina) == ["orfa", "rd-sem"]
    (tmp_path / "index.html").write_text(pagina, encoding="utf-8")
    manifesto = {"file_path": "index.html", "files": {}, "mantidos": sorted(hub.hrefs_relativos(pagina))}
    (tmp_path / "manifesto.json").write_text(json.dumps(manifesto), encoding="utf-8")
    capsys.readouterr()
    assert hub.main(["--check", "--out", str(tmp_path)]) == 0
    saida = capsys.readouterr().out
    assert "AVISO" in saida and "rd-sem" in saida and "orfa" in saida, saida


def test_bloco_fora_do_vocabulario_falha_alto(tmp_path):
    arq = tmp_path / "q.json"
    for ruim in ("Clinica", "SEM"):
        arq.write_text(json.dumps({"itens": {"rd-x": {"tipo": "revisao", "bloco": ruim}}}), encoding="utf-8")
        with pytest.raises(ValueError, match="bloco"):
            hub.ler_quadro(arq)


def _defeitos_das_rds(reg, raiz):
    """[defeitos] das RDs (`tipo: revisao`) e das rotas da Teoria no registro `reg`, contra os resumos de
    `raiz/resumos/` -- a FORMA da tabela do brief da s218 (part-2b), sem contagem: toda RD declara
    `disciplinas` (>= 1, sem repetir) e `resumos` (>= 1, todos no disco), não usa mais `bloco` nem cai em
    "Várias áreas"; todo item da Teoria tem rota (tarefa, `disciplinas` ou `bloco`). [] = ok."""
    defeitos = []
    for slug, v in sorted(reg.items()):
        if v["tipo"] != "revisao":
            continue
        discs = v.get("disciplinas") or []
        if not discs or len(set(discs)) != len(discs):
            defeitos.append("RD sem `disciplinas` (ou com disciplina repetida): %s" % slug)
        if not v.get("resumos"):
            defeitos.append("RD sem `resumos` de origem: %s" % slug)
        if "bloco" in v:
            defeitos.append("RD com `bloco` (leitura antiga, ⚰️ s218): %s" % slug)
        if any(area == "VARIAS" for area, _d in hub.lugares_do_registro(v, {})):
            defeitos.append("RD em 'Várias áreas': %s" % slug)
    defeitos += hub.avisos_fontes_rd(reg, raiz)
    defeitos += ["item da Teoria sem tarefa e sem `disciplinas`: %s" % s for s, v in sorted(reg.items())
                 if v["tipo"] != "analise" and v.get("tarefa_id") is None and not v.get("tarefas")
                 and not v.get("disciplinas") and not v.get("bloco")]
    return defeitos


@pytest.mark.vivo
def test_registro_real_rds_com_disciplinas_e_fontes_no_disco(monkeypatch):
    """s218 (a tabela do brief, conferida no <title>/h1 e no "Fonte:" de cada artifacts/aula-rd-*.html): toda
    RD declara `disciplinas` (>= 1, do vocabulario) e `resumos` (de onde saiu), e todo resumo-fonte existe no
    disco. A guarda que alcanca a PROXIMA RD: item da Teoria sem tarefa e sem `disciplinas` -- a suite do
    commit acusa antes do hub; nenhuma RD cai mais em "Varias areas" (⚰️ s218).

    Part-2b (10/10/2026): a forma da tabela é a regra de `_defeitos_das_rds`, medida em TODA RD, sem
    contagem; com o plano real, nenhum item do registro cai em "Sem área". Pula com motivo (`VIVO:`) sem
    o registro ou sem `resumos/`; sem o banco, mede o registro e pula antes do plano -- a guarda vem antes
    de qualquer conexão e o `db.DB_PATH` aponta para o banco que ela conferiu."""
    if not (ROOT / hub.QUADRO_REG).is_file():
        pytest.skip("VIVO: %s ausente -- RDs do registro real não medidas" % hub.QUADRO_REG)
    if not (ROOT / hub.DIR_RESUMOS).is_dir():
        pytest.skip("VIVO: %s/ ausente -- resumos-fonte das RDs não medidos" % hub.DIR_RESUMOS)
    reg = hub.ler_quadro(ROOT / hub.QUADRO_REG)
    # ⚰️ 10/10/2026 (part-2b): `len(rds) == 20`, as `disciplinas` de 4 RDs nomeadas e os tamanhos 7 e 8 da
    # rd-pilulas e da rd-pilulas-0510 -- a tabela do brief da s218 re-contada a cada RD registrada (o caso
    # s216: 2 FAILED). Contagem é relatório (o print); a forma é `_defeitos_das_rds`.
    print("  registro: %d RDs" % sum(v["tipo"] == "revisao" for v in reg.values()))
    defeitos = _defeitos_das_rds(reg, ROOT)
    assert defeitos == [], defeitos
    doc = json.loads((ROOT / hub.QUADRO_REG).read_text(encoding="utf-8"))["_doc"]
    assert "s218" in doc and "disciplinas" in doc and "⚰️" in doc
    if not REAL_DB.is_file():
        pytest.skip("VIVO: ipub.db ausente -- área das aulas com tarefa no plano real não medida "
                    "(o registro foi medido)")
    monkeypatch.setattr(hub.db, "DB_PATH", str(REAL_DB))
    linhas, aviso = hub._ler_plano()
    if aviso or not linhas:
        pytest.skip("VIVO: plano real indisponível (%s) -- área das aulas com tarefa não medida"
                    % (aviso or "vazio"))
    aulas = [hub.Aula(s, s, "2026-10-01", "artifacts/aula-%s.html" % s) for s in reg]
    pagina, avisos = hub.html_quadro_de(aulas, reg, {}, linhas, {}, date(2026, 10, 6))
    assert not [a for a in avisos if "grande area" in a], avisos
    assert 'data-area="SEM"' not in pagina and 'data-area="VARIAS"' not in pagina


def test_gemeo_hermetico_das_rds_acusa_cada_forma_plantada(tmp_path):
    """Gêmeo hermético do vivo acima (part-2b): o MESMO `_defeitos_das_rds` sobre um registro sintético e
    uma pasta `resumos/` com um arquivo só. A RD bem-formada e a análise passam; cada defeito plantado é
    acusado pelo slug. A parte do plano (item sem grande área no quadro) tem gêmeo próprio:
    `test_item_sem_area_cai_em_sem_area_e_o_build_e_o_check_acusam_o_slug`."""
    (tmp_path / "resumos" / "Cirurgia").mkdir(parents=True)
    (tmp_path / "resumos" / "Cirurgia" / "Hérnias.md").write_text("# Hérnias\n", encoding="utf-8")
    ok = {"tipo": "revisao", "disciplinas": ["Cirurgia"], "resumos": ["Cirurgia/Hérnias.md"]}
    reg = {"rd-ok": ok,
           "rd-repetida": dict(ok, disciplinas=["Cirurgia", "Cirurgia"]),
           "rd-sem-fonte": {"tipo": "revisao", "disciplinas": ["Cirurgia"]},
           "rd-fonte-sumida": dict(ok, resumos=["Cirurgia/Sumiu.md"]),
           "rd-com-bloco": dict(ok, bloco="CIR"),
           "rd-varias": {"tipo": "revisao", "bloco": "VARIAS", "resumos": ["Cirurgia/Hérnias.md"]},
           "aula-solta": {"tipo": "aula"},
           "doc": {"tipo": "analise"}}
    assert _defeitos_das_rds(reg, tmp_path) == [
        "RD com `bloco` (leitura antiga, ⚰️ s218): rd-com-bloco",
        "RD sem `disciplinas` (ou com disciplina repetida): rd-repetida",
        "RD sem `resumos` de origem: rd-sem-fonte",
        "RD sem `disciplinas` (ou com disciplina repetida): rd-varias",
        "RD com `bloco` (leitura antiga, ⚰️ s218): rd-varias",
        "RD em 'Várias áreas': rd-varias",
        "resumo-fonte inexistente na RD rd-fonte-sumida: resumos/Cirurgia/Sumiu.md -- corrija `resumos` em "
        "core/hub_quadro.json",
        "item da Teoria sem tarefa e sem `disciplinas`: aula-solta"]


def _sem_dado(tmp_path, monkeypatch, quadro):
    """Aponta o banco do vivo para um arquivo inexistente e, com `quadro=True`, o registro do quadro
    também (part-2b). `quadro=False` deixa um registro SINTÉTICO mínimo (sem RD) em tmp_path, para o
    vivo chegar até o plano sem depender do registro real. Devolve o caminho do banco ausente."""
    if quadro:
        monkeypatch.setattr(hub, "QUADRO_REG", "core/nao-existe-hub-quadro.json")
    else:
        sintetico = tmp_path / "hub_quadro.json"
        sintetico.write_text(json.dumps({"_doc": "s218: `disciplinas` por RD; ⚰️ `bloco`", "itens": {}}),
                             encoding="utf-8")
        monkeypatch.setattr(hub, "QUADRO_REG", str(sintetico))   # absoluto: ROOT / absoluto = absoluto
    ausente = tmp_path / "sem-banco" / "ipub.db"
    monkeypatch.setitem(globals(), "REAL_DB", ausente)
    return ausente


@pytest.mark.parametrize("vivo,quadro", [
    ("test_registro_real_so_com_as_aulas_em_aberto_e_ligadas_ao_plano", True),
    ("test_registro_real_rds_com_disciplinas_e_fontes_no_disco", True),
    ("test_registro_real_rds_com_disciplinas_e_fontes_no_disco", False),
], ids=["registro-sem-registro", "rds-sem-registro", "rds-sem-banco"])
def test_vivos_pulam_com_motivo_sem_o_dado(tmp_path, monkeypatch, vivo, quadro):
    """DoD 1 da part-2b: sem o registro (ou, com ele, sem o banco do plano), cada vivo PULA com motivo
    `VIVO:` -- não volta verde nem cai em asserção sobre registro vazio -- e não cria o banco."""
    import inspect
    ausente = _sem_dado(tmp_path, monkeypatch, quadro)
    fn = globals()[vivo]
    kwargs = {"monkeypatch": monkeypatch} if "monkeypatch" in inspect.signature(fn).parameters else {}
    with pytest.raises(pytest.skip.Exception, match=r"VIVO:"):
        fn(**kwargs)
    assert not ausente.exists() and not ausente.parent.exists(), "a guarda tem de vir antes do connect"


def test_lista_resolvida_vai_para_o_grupo_do_bloco_da_tarefa():
    """A lista resolvida na aba Listas sai da semana na hora para o grupo do BLOCO dela (a 26 e GO; o
    simulado 1793 tem area "Simulado", que o plano le como CM) -- o grupo nasce na ordem."""
    out = _rodar_qd(listas=LISTAS)
    # s218: no grupo CM, as disciplinas A-Z (Hematologia, Hepatologia, Simulado); a RD nova no topo da sua
    assert out["grupos"] == [["CM", ["rd-hemostasia", "rd-hepato", "t1793"]], ["CIR", ["rd-vias-biliares"]],
                             ["GO", ["t26"]]], out["grupos"]
    assert out["nfeitas"] == "5"


# ------------------------------------------------ 9. P20 (s219): a tarefa na Teoria, uma regra com o Painel

def test_tarefa_sem_link_com_questoes_no_banco_conta_o_banco_e_abre_a_aula(tmp_path):
    """s219: 26 tarefas ganharam caderno no hub sem `url_lista` (t530 REMIT, t768 aorta, t875...). O
    "resolver no hub" exigia o link -- a REMIT mostrava so "abrir aula", e a meta dizia "sem lista"
    com 20 questoes esperando na aba Listas. Agora: questoes no banco = "resolver no hub" e "N
    questoes" (a contagem do banco), sem rotulo de classe; o titulo do EMED sai sem o ' | '. P21 (s220):
    o "resolver no hub" saiu da Teoria -- o cartao abre a aula; as questoes moram na aba Listas."""
    raiz, data_fn = _repo(tmp_path, slugs=("remit", "rd-renal"))
    remit = dict(_t(530, 2, "Resposta Endócrino- | Metabólica-Inflamatória ao Trauma | Cicatrização de Feridas",
                    0, None, fonte="extensivo", bloco="CIR", area="Cirurgia"), no_hub=True, q_hub=20)
    sem_nada = _t(531, 2, "Tema sem nada", 0, None, fonte="extensivo", bloco="CIR", area="Cirurgia")
    quadro = {"remit": {"tipo": "aula", "titulo": "REMIT", "tarefa_id": 530},
              "rd-renal": QUADRO["rd-renal"], "x": {"tipo": "aula", "titulo": "X", "tarefas": [531]}}
    _construir(raiz, data_fn, quadro=quadro, plano=[remit, sem_nada])
    pagina = _index(raiz)
    item = _item(pagina, 'data-tarefa="530"')
    assert ('<p class="qd-tema">Resposta Endócrino-Metabólica-Inflamatória ao Trauma · Cicatrização de '
            'Feridas</p>') in item, "o titulo na tela; o `tema` do banco nao muda"
    assert '<span class="qd-bl">CIR</span><span>20 questões</span>' in item
    assert "resolver no hub" not in item and "data-hub-aba" not in item
    assert '<a class="qd-bloco qd-alvo hub-aula" href="aulas/remit.html" data-titulo="REMIT">' in item
    assert "sem lista" not in item and "qd-feito" not in item
    sem = re.search(r'data-secao="2".*?</section>', pagina, re.S).group(0)
    assert '<p class="qd-qsem">Questões da semana: <b>20</b>' in sem, "o cabecalho conta o banco"


def test_p21_tarefa_sem_aula_e_cartao_sem_acao_e_diz_aula_a_preparar():
    """P20 item 4: 'aula a preparar' e texto apagado da META, so quando a tarefa nao tem acao. P21 (s220):
    na Teoria a unica acao e a aula ("resolver no hub" saiu) -- a tarefa sem aula e um cartao SEM acao
    (`qd-sem-aula`: texto apagado, nenhum link, nada que pareca botao) e a meta diz por que, tambem
    com questoes no hub (a t1797, custom de aula com caderno: as questoes estao na aba Listas). O
    Painel segue a regra dele (`test_meta_e_acao_da_tarefa_no_painel_seguem_a_regra_da_teoria`)."""
    linhas = [dict(_t(1797, 2, "Tuberculose 360", 0, None, fonte="custom", bloco="CM"), no_hub=True, q_hub=20),
              _t(1796, 2, "Condições crônicas na APS", 0, None, fonte="custom", bloco="MFC")]
    secoes, _b, _a = hub.secoes_do_quadro([], plano_linhas=linhas, calendario=CAL, hoje=date(2026, 9, 23))
    itens = {i["id"]: hub._html_item(i) for s in secoes for i in s["itens"]}
    assert "<span>20 questões</span><span>aula a preparar</span>" in itens[1797]
    assert '<span>aula a preparar</span>' in itens[1796]
    for tid, item in itens.items():
        assert 'class="qd-item qd-sem-aula"' in item and '<div class="qd-bloco"><p class="qd-tema">' in item, tid
        for fora in ("<a ", "<button", "qd-acao", "qd-alvo", "resolver no hub", "tabindex", "role="):
            assert fora not in item, (tid, fora)


def test_aba_listas_mostra_o_titulo_pela_mesma_regra_da_teoria():
    """P20 item 5: a aba Listas desenha o `tema` do doc `listas/*` no navegador -- a mesma correcao de
    exibicao em JS (`temaExibido`), presa a `plano.tema_exibido` caso a caso (paridade, nunca copia
    divergente). O doc no banco nao muda."""
    from tools import plano
    if not NODE:
        pytest.skip("node ausente no PATH: paridade do titulo na aba Listas nao verificada (skip declarado)")
    casos = ["Resposta Endócrino- | Metabólica-Inflamatória ao Trauma | Cicatrização de Feridas",
             "Arboviroses | HIV | Tuberculose | Meningites e Meningoencefalites", "A |B", "| A |", "",
             "Endocardite Bacteriana - Endocardite Infecciosa", "Pré-Natal; Assistência ao Parto"]
    fn = extrair_funcao(TEMPLATE_HUB_REAL, "function temaExibido(t){")
    prog = fn + "\nconsole.log(JSON.stringify(%s.map(temaExibido)));" % json.dumps(casos, ensure_ascii=False)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8", timeout=60)
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout) == [plano.tema_exibido(c) for c in casos]
    lista = extrair_funcao(TEMPLATE_HUB_REAL, "function qzItemLista(l, atrasada){")
    assert "qzEsc(temaExibido(l.tema))" in lista
    assert '$("qz-tema").textContent = (temaExibido(l.tema) || id)' in TEMPLATE_HUB_REAL


def test_sem_db_o_quadro_nao_acusa_controle_que_nao_existe():
    """P20: sem o quadrado, a pagina sem `db` nao tem o que desabilitar nem o que avisar (era "Marcar
    como feita nao funciona nesta visualizacao"); a assinatura sem banco segue sem gravar nada."""
    out = _rodar_qd(semDb=True)
    assert out["aviso_oculto"] is True and out["escritas"] == []
    assert out["itens"]["rd-hepato"] == {"onde": "feitas", "feito": False, "marca": None}


# ------------------------------------------------ 10. P21 (s220): Teoria = aula; Listas = questoes
# Pedido do operador em 07/10/2026, noite, resolvendo listas: "se estou em listas e clico na tarefa,
# naturalmente devo ir especificamente para as questoes e, por outro lado, se estou na teoria, abro
# automaticamente a aula." O lado da aba Listas mora em `test_hub_render` (`test_p21_lista_e_so_a_lista...`).

def test_p21_tarefa_com_duas_aulas_mostra_as_duas_como_alvos_e_nenhuma_lista(tmp_path):
    """2+ aulas (a #811 tem duas): o cartao NAO e alvo -- cada aula e um alvo proprio de 1 toque, com o
    titulo dela, e nenhum link de lista. A aula dividida por 2 tarefas (#876/#879) e o alvo inteiro de
    cada cartao."""
    raiz, data_fn = _repo(tmp_path, slugs=("hernias", "hernias-b", "bayes"))
    quadro = {"hernias": {"tipo": "aula", "titulo": "A Escada das Hernias", "tarefas": [49, 68]},
              "hernias-b": {"tipo": "aula", "titulo": "Hernias <II> & cia", "tarefas": [49]},
              "bayes": QUADRO["bayes"]}
    plano = [dict(l, no_hub=True) if l["id"] == 49 else l for l in PLANO]
    _construir(raiz, data_fn, plano=plano, quadro=quadro)
    pagina = _index(raiz)
    duas = _item(pagina, 'data-tarefa="49"')
    assert '<div class="qd-bloco"><p class="qd-tema">Hernias da Parede Abdominal</p>' in duas, "o cartao nao e alvo"
    # a ordem e a das ligacoes (a aula mais nova primeiro, como sempre foi no bloco)
    assert re.findall(r'<div class="qd-aulas">(.*?)</div>', duas, re.S) == [
        '<a class="hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias">A Escada das Hernias</a>'
        '<a class="hub-aula" href="aulas/hernias-b.html" data-titulo="Hernias &lt;II&gt; &amp; cia">'
        'Hernias &lt;II&gt; &amp; cia</a>']
    assert duas.count("<a ") == 2 and "qd-alvo" not in duas
    for fora in ("resolver no hub", "abrir lista", "abrir aula", URL, "qd-acao"):
        assert fora not in duas, fora
    dividida = _item(pagina, 'data-tarefa="68"')   # a mesma aula prepara a 49 e a 68
    assert dividida.count("<a ") == 1 and '<a class="qd-bloco qd-alvo hub-aula" href="aulas/hernias.html" data-titulo="A Escada das Hernias"><p class="qd-tema">' in dividida


def test_p21_cartao_alvo_e_acessivel_e_o_sem_aula_nao_parece_botao(tmp_path):
    """O cartao-link: bloco inteiro clicavel (alvo >= 44 px pelo proprio bloco), foco visivel, sem
    sublinhado; o toque cai no ouvinte `a.hub-aula` -> `abrirAula` (o leitor dentro do hub). Cada aula
    do cartao de 2+ aulas tem 44 px. O cartao sem aula: fundo transparente, texto apagado e nenhum
    cursor/hover de botao."""
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    css = pagina[pagina.index("<style>"):pagina.index("</style>")]

    def regra(sel):
        m = re.search(r"(?:^|[}\n])%s\{([^}]*)\}" % re.escape(sel), css)
        assert m, sel
        return m.group(1)
    alvo = regra(".qd-alvo")
    for decl in ("display:block", "color:inherit", "text-decoration:none"):
        assert decl in alvo, decl
    assert "outline:3px solid var(--acento)" in regra(".qd-alvo:focus-visible")
    assert "min-height:44px" in regra(".qd-aulas a")
    assert "outline:3px solid var(--acento)" in regra(".qd-aulas a:focus-visible")
    assert "color:var(--tinta3)" in regra(".qd-sem-aula .qd-tema")
    assert "background:transparent" in regra(".qd-sem-aula .qd-bloco")
    assert not re.search(r"\.qd-sem-aula[^{]*\{[^}]*cursor:pointer", css)
    liga = re.search(r'querySelectorAll\("a\.hub-aula"\), function\(a\)\{(.*?)\}\);\n  \}\);', TEMPLATE_HUB_REAL, re.S)
    assert liga and "abrirAula(a)" in liga.group(1), "o cartao e um a.hub-aula: o toque abre o leitor"
