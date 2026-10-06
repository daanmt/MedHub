"""test_hub_pendencias.py -- a alca fechada v0 do hub (spec .vibeflow/specs/alca-fechada-v0.md).

Pedido do operador em 04/10/2026: pergunta do agente ganha lugar de resposta dentro do hub, e todo
documento aberto no leitor pode ser assinado ("comunicacao em alca fechada"). O que esta suite trava:

1. **A colecao certa.** Respostas e assinaturas vao para `analises/pendencias/itens` -- caminho que
   herda a regra `analises` (leitura e escrita so do dono) sem mudar a declaracao do publish.
2. **O documento e ligado pelo hub.** O `preparar` do quadro procura `form.pend` no documento aberto;
   o leitor tem a assinatura no rodape (uma vez, no template).
3. **Nunca perder texto** (24/09: 64 de 90 notas perdidas com o banco fora): o rascunho vai para o
   `localStorage` antes de qualquer gravacao e so sai depois dela confirmada.
4. **Estados.** `aberta` = Pendente; `respondida` = "Respondida em dd/mm" com o texto; `absorvida` =
   campo travado com o retorno do agente. Funcoes REAIS extraidas do template, rodadas em node.

LIMITE DECLARADO: mede o HTML e as funcoes puras, nao o CSS nem os handlers no celular -- isso e a
conferencia em navegador real (Edge headless, 390 px), feita fora da suite.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import hub  # noqa: E402
from tools.fsrs_queue import TEMPLATE_PLAYER  # noqa: E402
from tools.test_hub_render import NODE, extrair_funcao  # noqa: E402

TEMPLATE = hub.TEMPLATE_HUB.read_text(encoding="utf-8")
TEMPLATE_PLAYER_REAL = TEMPLATE_PLAYER.read_text(encoding="utf-8")
AUTOPSIA = ROOT / "artifacts" / "aula-autopsia-uerj-2021.html"

PURAS = ("function pendDataCurta(iso){", "function pendEstado(item){",
         "function pendContagem(chaves){", "function pendRegistro(meta, texto, agora){",
         "function pendAssinatura(slug, comentario, agora){", "function pendSlug(href){",
         "function pendTextoInicial(estado, rascunho){", "function pendEstadoDoc(item){",
         "function pendIdValido(id){")
FUNCS = "\n".join(extrair_funcao(TEMPLATE, a) for a in PURAS)


def _rodar(acao, funcs=None, assincrono=False):
    if not NODE:
        pytest.skip("node ausente no PATH: estados da alca fechada nao verificados (skip declarado)")
    corpo = FUNCS if funcs is None else funcs
    if assincrono:  # `acao` devolve uma promessa; imprime o valor resolvido
        prog = corpo + "\nPromise.resolve((function(){ " + acao + " })()).then(function(SAIDA){ console.log(JSON.stringify(SAIDA)); });\n"
    else:
        prog = corpo + "\nvar SAIDA = (function(){ " + acao + " })();\nconsole.log(JSON.stringify(SAIDA));\n"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        env = dict(os.environ, TZ="America/Sao_Paulo")
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8",
                             timeout=60, env=env)
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


# ------------------------------------------------ 1. colecao e ligacao (estatico, sempre roda)

def test_template_grava_pendencias_na_colecao_do_dono():
    """A colecao mora sob `analises` (regra read/write admin ja declarada); 3 segmentos = colecao."""
    assert 'var PEND_COLECAO = "analises/pendencias/itens";' in TEMPLATE
    assert PEND_COLECAO_SEGMENTOS() == 3
    assert 'db.collection(PEND_COLECAO)' in TEMPLATE
    assert '.where("origem", "==", ' in TEMPLATE, "o hub le so os itens do documento aberto"
    # nada de capability nova: a pagina continua so pedindo o db
    assert re.findall(r'claude\.use\("(\w+)"\)', TEMPLATE) and \
        set(re.findall(r'claude\.use\("(\w+)"\)', TEMPLATE)) == {"db"}


def PEND_COLECAO_SEGMENTOS():
    return len(re.search(r'var PEND_COLECAO = "([^"]+)";', TEMPLATE).group(1).split("/"))


def test_documento_com_form_pend_e_ligado_pelo_quadro():
    corpo = extrair_funcao(TEMPLATE, "function preparar(quadro){")
    assert "pendLigar(doc, quadro)" in corpo, "o preparar liga os formularios do documento aberto"
    ligar = extrair_funcao(TEMPLATE, "function pendLigar(doc, quadro){")
    assert 'querySelectorAll("form.pend[data-pend]")' in ligar
    assert "data-pend-contador" in TEMPLATE and "data-pend-estado" in TEMPLATE


def test_rascunho_vai_ao_aparelho_antes_e_sai_so_depois_da_gravacao():
    enviar = extrair_funcao(TEMPLATE, "function pendEnviar(f){")
    i_rasc = enviar.index("pendRascunho(f.id, texto)")
    i_grava = enviar.index("pendGravar(")
    assert i_rasc < i_grava, "o rascunho e salvo ANTES de tentar o banco"
    assert "pendRascunho(f.id, null)" in enviar.split(".then(", 1)[1], \
        "o rascunho so e apagado no .then (gravacao confirmada)"
    assert "Não salvou. O rascunho ficou guardado neste aparelho. Toque para reenviar." in TEMPLATE
    ls = extrair_funcao(TEMPLATE, "function pendRascunho(id, texto){")
    assert "try{" in ls and "catch(e)" in ls and '"medhub.pend." + id' in ls


def test_gravacao_faz_merge_lendo_antes():
    """`set` substitui o documento inteiro; o seed traz titulo/obrigatoria/criada_em que nao podem sumir."""
    grava = extrair_funcao(TEMPLATE, "function pendGravar(id, dados){")
    assert ".get()" in grava and ".update(dados)" in grava and ".set(dados)" in grava


def test_leitor_tem_a_assinatura_uma_vez():
    leitor = TEMPLATE.split('<div id="hub-leitor" hidden>', 1)[1].split("</section>", 1)[0]
    assert leitor.count('id="hub-assina"') == 1
    assert ">Assinar leitura<" in leitor
    assert 'id="hub-assina-coment"' in leitor
    assert TEMPLATE.count('id="hub-assina"') == 1
    assert "assinaLer(slug)" in extrair_funcao(TEMPLATE, "function assinaAbrir(slug){")
    assert '"doc_" + ' in extrair_funcao(TEMPLATE, "function assinaLer(slug){")


def test_hub_montado_leva_a_alca_sem_quebrar_o_celular():
    aulas = [hub.Aula("hernias", "A Escada das Hernias", "2026-09-22", "artifacts/aula-hernias.html")]
    lote = {"sessao": "2026-10-04a", "gerado_em": "", "total": 0, "cards": []}
    pagina = hub.montar_index(TEMPLATE, TEMPLATE_PLAYER_REAL, lote, aulas, True,
                              __import__("datetime").datetime(2026, 10, 4, 12, 0))
    assert 'var PEND_COLECAO = "analises/pendencias/itens";' in pagina
    assert pagina.count('id="hub-assina"') == 1
    assert "sticky" not in pagina.lower() and "nowrap" not in pagina.lower()
    assert pagina.count('class="wrap"') == 1
    regra = re.search(r"\.hub-assina button\{([^}]*)\}", pagina).group(1)
    assert "min-height:44px" in regra
    assert "—" not in pagina.split("<script", 1)[0] and "→" not in pagina


# ------------------------------------------------ 2. estados (node)

def test_estados_aberta_respondida_absorvida():
    out = _rodar("""return {
      nada: pendEstado(null),
      aberta: pendEstado({status: "aberta", pergunta: "x"}),
      resp: pendEstado({status: "respondida", resposta: "Achei que era D", respondida_em: "2026-10-04T15:00:00.000Z"}),
      resp_vazia: pendEstado({status: "respondida", resposta: ""}),
      abs: pendEstado({status: "absorvida", resposta: "R", retorno_agente: "Erro registrado com card 812.", absorvida_em: "2026-10-05T15:00:00.000Z"})
    };""")
    assert out["nada"]["chave"] == "pendente" and out["nada"]["rotulo"] == "Pendente"
    assert out["aberta"]["chave"] == "pendente" and not out["aberta"]["travado"]
    assert out["resp"] == {"chave": "respondida", "rotulo": "Respondida em 04/10", "travado": False,
                           "texto": "Achei que era D", "retorno": ""}
    assert out["resp_vazia"]["chave"] == "pendente"
    assert out["abs"]["chave"] == "absorvida" and out["abs"]["travado"]
    assert out["abs"]["retorno"] == "Erro registrado com card 812." and out["abs"]["texto"] == "R"
    assert out["abs"]["rotulo"] == "Absorvida em 05/10"


def test_contador_conta_respondida_e_absorvida():
    out = _rodar('return [pendContagem(["pendente","respondida","absorvida"]), pendContagem([]), pendContagem(["respondida"])];')
    assert out == ["2 de 3 respondidas", "", "1 de 1 respondida"]


def test_registro_e_assinatura_na_forma_do_banco():
    out = _rodar("""var ag = "2026-10-04T15:00:00.000Z"; return {
      r: pendRegistro({origem: "autopsia-uerj-2021", ref: "t1793_30", tipo: "pergunta", pergunta: "Por que?"}, "  Porque sim ", ag),
      a: pendAssinatura("autopsia-uerj-2021", " ok ", ag),
      s: [pendSlug("aulas/autopsia-uerj-2021.html"), pendSlug("dossie-uerj.html"), pendSlug("")]};""")
    assert out["r"] == {"origem": "autopsia-uerj-2021", "ref": "t1793_30", "tipo": "pergunta",
                        "pergunta": "Por que?", "resposta": "Porque sim", "status": "respondida",
                        "respondida_em": "2026-10-04T15:00:00.000Z"}
    assert out["a"] == {"origem": "autopsia-uerj-2021", "tipo": "documento", "status": "assinado",
                        "assinado_em": "2026-10-04T15:00:00.000Z", "comentario": "ok"}
    assert out["s"] == ["autopsia-uerj-2021", "dossie-uerj", ""]


def test_rascunho_volta_ao_abrir_e_nunca_destrava_absorvida():
    out = _rodar("""var p = pendEstado(null), r = pendEstado({status:"respondida", resposta:"A"}),
      a = pendEstado({status:"absorvida", resposta:"A", retorno_agente:"feito"}); return [
      pendTextoInicial(p, "meu rascunho"), pendTextoInicial(p, null), pendTextoInicial(r, null),
      pendTextoInicial(r, "A editada"), pendTextoInicial(r, "A"), pendTextoInicial(a, "outra")];""")
    assert out == [{"texto": "meu rascunho", "rascunho": True}, {"texto": "", "rascunho": False},
                   {"texto": "A", "rascunho": False}, {"texto": "A editada", "rascunho": True},
                   {"texto": "A", "rascunho": False}, {"texto": "A", "rascunho": False}]


def test_estado_do_documento_assinado():
    out = _rodar("""return [pendEstadoDoc(null), pendEstadoDoc({status:"assinado", assinado_em:"2026-10-04T15:00:00.000Z", comentario:"li"}),
      pendEstadoDoc({status:"absorvida", assinado_em:"2026-10-04T15:00:00.000Z", comentario:"li", retorno_agente:"respondido"})];""")
    assert out[0]["chave"] == "sem" and out[0]["rotulo"] == ""
    assert out[1] == {"chave": "assinado", "rotulo": "Assinado em 04/10", "travado": False,
                      "texto": "li", "retorno": ""}
    assert out[2]["travado"] and out[2]["retorno"] == "respondido"


# ------------------------------------------------ 2b. correcoes do audit (s213, alca-fechada-v0-audit.md)

# banco falso: get/update/set sobre um objeto; conta as escritas
BANCO_FALSO = """
var BANCO = {}, ESCRITAS = 0, FALHA = false;
var COL = {doc: function(id){ return {
  get: function(){ return FALHA ? Promise.reject(new Error("fora")) :
    Promise.resolve({exists: id in BANCO, data: function(){ return BANCO[id]; }}); },
  update: function(d){ ESCRITAS++; Object.assign(BANCO[id], d); return Promise.resolve(); },
  set: function(d){ ESCRITAS++; BANCO[id] = d; return Promise.resolve(); }}; }};
function pendDb(){ return Promise.resolve(COL); }
"""
GRAVAR = "\n".join(extrair_funcao(TEMPLATE, a) for a in (
    "function pendIdValido(id){", "function pendRegistro(meta, texto, agora){",
    "function pendGravar(id, dados){"))
META = '{origem: "autopsia-uerj-2021", ref: "t1793_44", tipo: "pergunta", pergunta: "?"}'


def test_gravar_nao_sobrescreve_absorvida():
    """C1: a pagina sem o estado (banco fora ao abrir) tenta enviar; o banco ja absorveu -> recusa."""
    out = _rodar(f"""
      BANCO["autopsia-uerj-2021_q44"] = {{status: "absorvida", resposta: "R", retorno_agente: "card 812", titulo: "Q44"}};
      BANCO["autopsia-uerj-2021_q30"] = {{status: "aberta", titulo: "Q30", obrigatoria: true}};
      var r = {{}};
      return pendGravar("autopsia-uerj-2021_q44", pendRegistro({META}, "nova", "2026-10-04T15:00:00.000Z"))
        .then(function(){{ r.abs = "gravou"; }}, function(e){{ r.abs = {{travado: !!e.travado, status: e.item.status}}; }})
        .then(function(){{ return pendGravar("autopsia-uerj-2021_q30", pendRegistro({META}, "minha", "2026-10-04T15:00:00.000Z")); }})
        .then(function(){{ return pendGravar("novo_1", pendRegistro({META}, "x", "2026-10-04T15:00:00.000Z")); }})
        .then(function(){{ return pendGravar("a/b", {{}}).then(function(){{ r.barra = "gravou"; }}, function(e){{ r.barra = e.message; }}); }})
        .then(function(){{ r.banco = BANCO; r.escritas = ESCRITAS; return r; }});""",
                 funcs=BANCO_FALSO + GRAVAR, assincrono=True)
    assert out["abs"] == {"travado": True, "status": "absorvida"}
    assert out["banco"]["autopsia-uerj-2021_q44"] == {"status": "absorvida", "resposta": "R",
                                                     "retorno_agente": "card 812", "titulo": "Q44"}
    # o caminho comum continua: merge preserva o seed, documento novo e criado
    q30 = out["banco"]["autopsia-uerj-2021_q30"]
    assert q30["obrigatoria"] is True and q30["titulo"] == "Q30" and q30["status"] == "respondida"
    assert out["banco"]["novo_1"]["resposta"] == "x"
    assert out["barra"] == "id invalido" and "a/b" not in out["banco"]
    assert out["escritas"] == 2


ENVIAR_STUBS = """
var LS = {};
var localStorage = {getItem: function(k){ return k in LS ? LS[k] : null; }, setItem: function(k, v){ LS[k] = String(v); },
                    removeItem: function(k){ delete LS[k]; }};
var PEND_ABSORVIDO = "Este item já foi absorvido.", PINTADO = null;
function pendPintar(f, item){ PINTADO = item; }
function pendContar(){} function medir(){} function pendLer(){}
"""
ENVIAR = "\n".join(extrair_funcao(TEMPLATE, a) for a in (
    "function pendRascunho(id, texto){", "function pendEnviar(f){"))


def _form(valor):
    return ('{id: "autopsia-uerj-2021_q44", ta: {value: "' + valor + '"}, bt: {}, st: {}, estado: null, erro: false, '
            'aviso: "", meta: ' + META + ', ctx: {itens: {}, falha: {}, quadro: null}}')


def test_envio_sobre_absorvida_repinta_travado_e_avisa():
    """C1 no formulario: nada gravado, item do banco na tela, aviso, sem estado de erro."""
    out = _rodar(f"""
      BANCO["autopsia-uerj-2021_q44"] = {{status: "absorvida", resposta: "R", retorno_agente: "card 812"}};
      var f = {_form("nova")};
      return pendEnviar(f).then(function(){{ return {{erro: f.erro, aviso: f.aviso, pintado: PINTADO,
        escritas: ESCRITAS, rascunho: localStorage.getItem("medhub.pend." + f.id)}}; }});""",
                 funcs=BANCO_FALSO + GRAVAR + ENVIAR_STUBS + ENVIAR, assincrono=True)
    assert out["erro"] is False and out["aviso"] == "Este item já foi absorvido."
    assert out["pintado"]["status"] == "absorvida" and out["pintado"]["retorno_agente"] == "card 812"
    assert out["escritas"] == 0


def test_rascunho_editado_durante_a_gravacao_nao_e_apagado():
    """R7: o texto mudou enquanto a gravacao antiga corria; a confirmacao dela nao apaga o rascunho novo."""
    out = _rodar(f"""
      var f = {_form("primeira")};
      var p = pendEnviar(f);
      f.ta.value = "segunda, mais longa"; localStorage.setItem("medhub.pend." + f.id, f.ta.value);
      return p.then(function(){{
        var g = {_form("igual")}; g.id = "outro_1";
        return pendEnviar(g).then(function(){{ return {{editado: localStorage.getItem("medhub.pend." + f.id),
          igual: localStorage.getItem("medhub.pend.outro_1")}}; }}); }});""",
                 funcs=BANCO_FALSO + GRAVAR + ENVIAR_STUBS + ENVIAR, assincrono=True)
    assert out == {"editado": "segunda, mais longa", "igual": None}


def test_banco_ausente_nao_fica_memorizado():
    """R10: o 1o pedido ao banco volta vazio; o 2o pede de novo e acha o banco, sem recarregar a pagina."""
    pdb = extrair_funcao(TEMPLATE, "function pendDb(){")
    out = _rodar("""
      return pendDb().then(function(c1){ return pendDb().then(function(c2){ return {c1: c1, c2: c2, pedidos: n}; }); });""",
                 funcs=('var n = 0, PEND_COLECAO = "analises/pendencias/itens", PEND = {pronto: null};\n'
                        'var window = {claude: {use: function(){ n++; return Promise.resolve(n === 1 ? null : '
                        '{collection: function(p){ return "col:" + p; }}); }}};\n' + pdb),
                 assincrono=True)
    assert out == {"c1": None, "c2": "col:analises/pendencias/itens", "pedidos": 2}


def test_id_do_formulario_e_validado():
    """R3: so [A-Za-z0-9_-]{1,120}; id fora disso nao vira caminho nem chave do aparelho."""
    out = _rodar('return ["autopsia-uerj-2021_q44", "", "a/b", "x".repeat(121), "x".repeat(120), "doc_dossie-uerj", "q 1", null]'
                 '.map(pendIdValido);')
    assert out == [True, False, False, False, True, True, False, False]
    ligar = extrair_funcao(TEMPLATE, "function pendLigar(doc, quadro){")
    assert "if(!pendIdValido(id)){" in ligar and "ta.disabled = true; bt.disabled = true;" in ligar
    assert 'pendIdValido("doc_" + m[1])' in extrair_funcao(TEMPLATE, "function pendSlug(href){")


def test_leitura_que_falha_avisa_e_tenta_de_novo_ao_toque():
    """R1: erro de leitura escreve o aviso nos estados e no rodape; o toque rele."""
    assert 'var PEND_LEITURA = "Não consegui ler as respostas salvas. Toque para tentar de novo.";' in TEMPLATE
    ler = extrair_funcao(TEMPLATE, "function pendLer(ctx){")
    assert "function(){ pendFalhaLeitura(ctx, [o]); }" in ler, "callback de erro do onSnapshot"
    assert "if(!col){ pendFalhaLeitura(ctx, ctx.origens); return; }" in ler
    assert "rot = PEND_LEITURA;" in extrair_funcao(TEMPLATE, "function pendPintar(f, item){")
    assert "else if(ctx.falha[f.meta.origem]){ pendLer(ctx); }" in extrair_funcao(TEMPLATE, "function pendLigar(doc, quadro){")
    assina = extrair_funcao(TEMPLATE, "function assinaLer(slug){")
    assert "function(){ assinaFalha(slug); }" in assina and "if(!col){ assinaFalha(slug); return; }" in assina
    assert "leitura ? PEND_LEITURA" in extrair_funcao(TEMPLATE, "function assinaPintar(){")
    assert "else if(ASSINA.leitura){ assinaLer(ASSINA.slug); }" in TEMPLATE


def test_falha_nas_pendencias_nao_derruba_o_leitor():
    """R2: pendLigar embrulhado; medir roda depois, sempre."""
    corpo = extrair_funcao(TEMPLATE, "function preparar(quadro){")
    assert "try{ pendLigar(doc, quadro); }catch(e){}" in corpo
    assert corpo.index("try{ pendLigar(doc, quadro); }") < corpo.index("    medir(quadro);")


# ------------------------------------------------ 3. a Autopsia real (artefato versionado)

class _Forms(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms, self.contadores = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form" and "pend" in (a.get("class") or "").split():
            self.forms.append(a)
        if "data-pend-contador" in a:
            self.contadores.append(a["data-pend-contador"])


@pytest.mark.skipif(not AUTOPSIA.is_file(), reason="Autopsia UERJ 2021 ausente")
def test_autopsia_tem_as_22_perguntas_com_as_que_travam_erro_primeiro():
    html = AUTOPSIA.read_text(encoding="utf-8")
    p = _Forms()
    p.feed(html)
    perg = [f for f in p.forms if f.get("data-tipo") == "pergunta"]
    coment = [f for f in p.forms if f.get("data-tipo") == "comentario"]
    assert len(perg) == 22
    assert [f["data-ref"] for f in perg[:3]] == ["t1793_30", "t1793_44", "t1793_47"]
    assert all(f["data-origem"] == "autopsia-uerj-2021" for f in p.forms)
    assert len({f["data-pend"] for f in p.forms}) == len(p.forms), "id unico por formulario"
    assert coment and all(f["data-pend"].startswith("autopsia-uerj-2021_c") for f in coment)
    assert p.contadores == ["autopsia-uerj-2021", "autopsia-uerj-2021"]
    assert "Abra pelo hub para responder" in html
    assert html.count("fecha um erro sem card") == 3
    # R8: as 3 obrigatorias abertas; as 19 opcionais num <details> recolhido com o contador do grupo
    secao = html.split('<section id="perguntas">', 1)[1].split("</section>", 1)[0]
    abertas, grupo = secao.split('<details class="pend-opc" data-pend-grupo>', 1)
    assert abertas.count('data-tipo="pergunta"') == 3
    assert grupo.count('data-tipo="pergunta"') == 19 and "<span>19 perguntas opcionais</span>" in grupo.split("</summary>", 1)[0]
    assert 'data-pend-contador="autopsia-uerj-2021"' in grupo.split("</summary>", 1)[0]



# ------------------------------------------------ s216 (hub-integracao part-4): o Painel ve a assinatura
# Documento assinado no leitor aparece assinado no Painel: pelo `quadro/<slug>` quando ele existe (a aula do
# quadro) e por `analises/pendencias/itens/doc_<slug>` quando nao (o documento fora do quadro, como o
# Dossie). So o dono le `analises/`: para quem nao le, falha calada e o Painel fica como o build (A13).

def _painel_docs_html():
    from tools import painel

    def t(id_, tema, aulas):
        return {"id": id_, "semana": 4, "atrasada": False, "tema": tema, "q": 0, "classe": "aula",
                "url_lista": None, "area": None, "rotulo": "CM", "aula": None, "aulas": aulas, "no_hub": False}
    return ('<ol class="tarefas">%s</ol>' % "".join(painel._html_tarefa(x) for x in (
        t(768, "Aorta", [{"slug": "aorta", "titulo": "A aorta"}]),
        t(367, "Tireoide", [{"slug": "tireoide", "titulo": "A tireoide"}]))) +
        painel._html_docs([{"slug": "dossie-uerj", "titulo": "Dossiê UERJ"},
                           {"slug": "autopsia-uerj-2021", "titulo": "Autópsia UERJ 2021"},
                           {"slug": "outro-doc", "titulo": "Outro"}]))


ACAO_ASSINADOS = r"""
function espera(){ return new Promise(function(ok){ setTimeout(ok, 0); }); }
var MEDIU = 0;
painelAssinados($("pa"), DB, function(){ MEDIU++; });
espera().then(espera).then(function(){ var o = {};
  $("pa").querySelectorAll("li.tarefa").forEach(function(li){ var a = li.querySelector("a[data-hub-aula]"), m = li.querySelector(".t-assinado");
    o[a.getAttribute("data-hub-aula")] = [li.classList.contains("qd-assinado"), m ? m.textContent : null]; });
  console.log(JSON.stringify({li: o, mediu: MEDIU, escritas: ESCRITAS})); });
"""


def _rodar_assinados(**cfg):
    from tools.test_hub_quadro import BANCO_QD, DOM_QD, _arvore
    if not NODE:
        pytest.skip("node ausente no PATH: assinatura no Painel nao verificada (skip declarado)")
    funcs = "\n".join([re.search(r"\n  (var PEND_COLECAO = [^\n]+;)", TEMPLATE).group(1),
                       extrair_funcao(TEMPLATE, "function painelMarcarAssinado(li, sim){"),
                       extrair_funcao(TEMPLATE, "function painelAssinados(doc, db, depois){")])
    corpo = (DOM_QD.replace("__ARVORE__", json.dumps(_arvore('<div id="pa">%s</div>' % _painel_docs_html()),
                                                    ensure_ascii=False)) +
             BANCO_QD.replace("__CFG__", json.dumps(cfg, ensure_ascii=False)) + funcs + "\n" + ACAO_ASSINADOS)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(corpo)
        caminho = f.name
    try:
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8", timeout=60,
                             env=dict(os.environ, TZ="America/Sao_Paulo"))
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


PEND_ASSINADOS = {"doc_dossie-uerj": {"tipo": "documento", "status": "assinado"},
                  "doc_autopsia-uerj-2021": {"tipo": "documento", "status": "absorvida"},
                  "doc_tireoide": {"tipo": "documento", "status": "assinado"},
                  "doc_aorta": {"tipo": "documento", "status": "assinado"}}


def test_documento_assinado_pinta_o_painel():
    out = _rodar_assinados(quadro={"aorta": {"feito": False}}, pend=PEND_ASSINADOS)
    li = out["li"]
    assert li["dossie-uerj"] == [True, " · assinado"], "fora do quadro: vale a assinatura"
    assert li["autopsia-uerj-2021"][0] is True, "absorvida pelo agente tambem foi assinada"
    assert li["tireoide"][0] is True, "sem doc no quadro: vale a assinatura"
    assert li["aorta"] == [False, None], "com doc no quadro, vale o quadro (desmarcado = nao)"
    assert li["outro-doc"] == [False, None]
    assert out["mediu"] >= 1 and out["escritas"] == [], "o Painel so le"
    feito = _rodar_assinados(quadro={"aorta": {"feito": True}}, pend={})
    assert feito["li"]["aorta"][0] is True and feito["li"]["dossie-uerj"][0] is False


def test_sem_leitura_de_analises_o_painel_fica_como_o_build():
    out = _rodar_assinados(quadro={"aorta": {"feito": True}}, pend=PEND_ASSINADOS,
                           negar=["analises/pendencias/itens"])
    assert out["li"]["dossie-uerj"] == [False, None] and out["li"]["aorta"][0] is True
    corpo = extrair_funcao(TEMPLATE, "function painelListas(doc, quadro){")
    assert "painelAssinados(doc, db" in corpo
