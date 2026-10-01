"""test_player_js.py -- comportamento do JS do player (core/templates/player.html) rodado em node.

Spec: feedback do operador s194 (itens 3, 4 e 5 do hub). Sem jsdom: um DOM falso minimo, montado a
partir dos ids REAIS da regiao `corpo` do template (quem nasce `hidden` no HTML nasce escondido
aqui), relogio controlado (`Date.now`) e `setInterval` disparado a mao. Sem `node` no PATH, os
testes comportamentais sao PULADOS (skip declarado) e sobra o teste estatico do fim do arquivo.

O que se mede:
- item 3: o aviso MOMENTANEO ("Vire o card antes...") some ao virar e ao avancar; o aviso
  PERSISTENTE (armazenamento indisponivel) continua na tela;
- item 4: tempo ATIVO -- conta so com card na tela, teto de TETO_OCIOSO por intervalo entre
  gestos, pausa com a aba oculta e com a tecla P, sobrevive a reload por localStorage e degrada
  para zero sem erro quando o storage lanca;
- item 5: a tela de fim traz desempenho e a agenda de 7 dias (agenda_base + previsao de cada
  card pela nota recebida); lote antigo, sem os campos novos, mostra so o desempenho.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import hub  # noqa: E402
from tools.fsrs_queue import TEMPLATE_PLAYER  # noqa: E402

NODE = shutil.which("node")
TEMPLATE = TEMPLATE_PLAYER.read_text(encoding="utf-8")
REGIOES = hub.extrair_regioes_player(TEMPLATE)
MINUTO = 60 * 1000


class _Ids(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = {}
        self.notas = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids[a["id"]] = {"hidden": "hidden" in a, "tag": tag}
        if tag == "button" and "data-nota" in a:
            self.notas.append(a["data-nota"])


def _estrutura():
    p = _Ids()
    p.feed(REGIOES["corpo"])
    p.close()
    return p.ids, p.notas


def _js_do_player():
    js = REGIOES["js"]
    ini = js.index("<script>") + len("<script>")
    return js[ini:js.rindex("</script>")]


HARNESS = r"""
var IDS = __IDS__, NOTAS = __NOTAS__, LOTE_JSON = __LOTE__, OPC = __OPC__;
var relogio = 1000000, intervalos = [], docOuv = {}, janOuv = {};
Date.now = function(){ return relogio; };
function mk(id, tag){
  var el = {id:id, tagName:(tag||"div").toUpperCase(), hidden:false, textContent:"", value:"",
    style:{}, open:false, attrs:{}, filhos:[], ouv:{}, _html:"",
    classList:{add:function(){}, remove:function(){}, contains:function(){return false;}, toggle:function(){}},
    setAttribute:function(k,v){ this.attrs[k]=String(v); }, getAttribute:function(k){ return k in this.attrs ? this.attrs[k] : null; },
    removeAttribute:function(k){ delete this.attrs[k]; },
    addEventListener:function(t,f){ (this.ouv[t]=this.ouv[t]||[]).push(f); },
    focus:function(){}, appendChild:function(c){ this.filhos.push(c); return c; },
    querySelectorAll:function(){ return []; },
    disparar:function(t, ev){ (this.ouv[t]||[]).forEach(function(f){ f(ev || {preventDefault:function(){}}); }); }
  };
  Object.defineProperty(el, "innerHTML", {get:function(){ return this._html; }, set:function(v){ this._html=String(v); this.filhos=[]; }});
  return el;
}
var ELS = {};
Object.keys(IDS).forEach(function(id){ ELS[id] = mk(id, IDS[id].tag); ELS[id].hidden = IDS[id].hidden; });
ELS.lote = mk("lote", "script"); ELS.lote.textContent = LOTE_JSON;
var BOTOES = NOTAS.map(function(n){ var b = mk("nota"+n, "button"); b.attrs["data-nota"] = n; return b; });
var documento = {
  hidden:false,
  getElementById:function(id){ return ELS[id] || null; },
  documentElement:{getAttribute:function(){ return null; }},
  querySelectorAll:function(sel){ return sel.indexOf("notas-botoes") >= 0 ? BOTOES : []; },
  createElement:function(t){ return mk(null, t); },
  addEventListener:function(t,f){ (docOuv[t]=docOuv[t]||[]).push(f); }
};
var armazem = {};
var ls = OPC.lsQuebrado ? {getItem:function(){ throw new Error("negado"); }, setItem:function(){ throw new Error("negado"); }}
  : {getItem:function(k){ return k in armazem ? armazem[k] : null; }, setItem:function(k,v){ armazem[k]=String(v); }};
if(OPC.armazem){ armazem = OPC.armazem; }
global.document = documento;
global.window = {addEventListener:function(t,f){ (janOuv[t]=janOuv[t]||[]).push(f); }};
// db falso SINCRONO (OPC.db = {docs:{id:doc}}): `then` chama na hora, para o cenario
// ler o resultado sem esperar microtask. `OPC.dbFalha` = todo set() falha; `OPC.dbFalhas` = N = os
// N primeiros set() falham e o resto passa (a falha PASSAGEIRA, "unavailable" de 27/09).
var DB = {}, escritas = [];
function falhaAgora(){ if(OPC.dbFalha){ return true; } if(OPC.dbFalhas > 0){ OPC.dbFalhas -= 1; return true; } return false; }
function ST(v){ return {then:function(f){ var r = f(v); return (r && typeof r.then === "function") ? r : ST(r); }, catch:function(){ return this; }}; }
function STErr(e){ return {then:function(){ return this; }, catch:function(g){ g(e); return ST(undefined); }}; }
if(OPC.db){
  DB = OPC.db.docs || {};
  var colecaoFalsa = {
    doc:function(id){ return {set:function(reg){ if(falhaAgora()){ return STErr({code:"falhou"}); } DB[id] = reg; escritas.push(String(id)); return ST(undefined); }}; },
    get:function(){ return ST({docs: Object.keys(DB).map(function(k){ var d = DB[k]; return {data:function(){ return d; }}; })}); }
  };
  var dbFalso = {collection:function(){ return colecaoFalsa; }};
  global.window.claude = {use:function(){ return ST(dbFalso); }};
  // s210: `OPC.dbAdiado` = o db so responde quando o cenario chama abrirDb() -- a corrida do
  // reload em que o operador ja deu nota antes de `colecao.get()` voltar (01/10, "volta no tempo").
  if(OPC.dbAdiado){
    var aoAbrir = null, depois = [];
    var cadeia = {then:function(g){ depois.push(g); return cadeia; }, catch:function(){ return cadeia; }};
    global.window.claude = {use:function(){ return {then:function(f){ aoAbrir = f; return cadeia; }, catch:function(){ return this; }}; }};
    global.abrirDb = function(){
      var r = aoAbrir(dbFalso);
      if(!r || typeof r.then !== "function"){ r = ST(r); }
      depois.forEach(function(g){ r = r.then(g); });
    };
  }
}
global.localStorage = ls;
global.navigator = {};
global.setInterval = function(f){ intervalos.push(f); return intervalos.length; };
global.setTimeout = function(){ return 0; };
function passar(ms){ var passos = Math.floor(ms / 1000); for(var i = 0; i < passos; i++){ relogio += 1000; intervalos.forEach(function(f){ f(); }); } relogio += ms % 1000; }
function tecla(k){ (docOuv.keydown||[]).forEach(function(f){ f({key:k, code:k===" "?"Space":"", target:{tagName:"BODY"}, preventDefault:function(){}}); }); }
function ocultar(sim){ documento.hidden = sim; (docOuv.visibilitychange||[]).forEach(function(f){ f({}); }); }
function el(id){ return ELS[id]; }
function segundos(){ var p = el("relogio").textContent.split(":"); return p.length === 2 ? (+p[0])*60 + (+p[1]) : NaN; }
var SAIDA = {};
__PLAYER__
__CENARIO__
console.log(JSON.stringify({saida: SAIDA, armazem: armazem, db: DB, escritas: escritas}));
"""


def _card(i, tema="IC", previsao=None):
    c = {"card_id": 100 + i, "frente_contexto": None, "frente_pergunta": "P%d?" % i,
         "verso_resposta": "R%d" % i, "verso_regra_mestre": None, "verso_armadilha": None,
         "area": "Clinica", "tema": tema, "selection_reason": "vencido", "bucket": "atrasados"}
    if previsao is not None:
        c["previsao"] = previsao
    return c


def _lote(cards, **extra):
    lote = {"sessao": "t-js", "gerado_em": "2026-09-23T08:00:00", "total": len(cards),
            "cards": cards}
    lote.update(extra)
    return lote


def _rodar(lote, cenario, opc=None):
    if not NODE:
        pytest.skip("node ausente no PATH: comportamento do JS nao verificado (skip declarado)")
    ids, notas = _estrutura()
    prog = (HARNESS.replace("__IDS__", json.dumps(ids))
                   .replace("__NOTAS__", json.dumps(notas))
                   .replace("__LOTE__", json.dumps(json.dumps(lote)))
                   .replace("__OPC__", json.dumps(opc or {}))
                   .replace("__PLAYER__", _js_do_player())
                   .replace("__CENARIO__", cenario))
    # s195: o programa passou de 32 KB e `node -e` estourava a linha de comando do Windows
    # (CreateProcess falha como FileNotFoundError). Vai por arquivo.
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        r = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8",
                           timeout=60)
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


LOTE3 = _lote([_card(0), _card(1, "Asma"), _card(2, "DPOC")])


# --------------------------------------------------------------------------
# Item 3: aviso momentaneo x persistente
# --------------------------------------------------------------------------

def test_aviso_de_virar_some_ao_virar():
    out = _rodar(LOTE3, """
      tecla("3");
      SAIDA.antes = !el("aviso-momento").hidden;
      tecla(" ");
      SAIDA.depois = !el("aviso-momento").hidden;
    """)["saida"]
    assert out == {"antes": True, "depois": False}


def test_aviso_de_virar_some_ao_avancar_de_card():
    out = _rodar(LOTE3, """
      tecla("3"); tecla(" "); tecla("1");        // avisou, virou (sumiu), avaliou
      tecla("4");                                 // card novo, sem virar: avisa de novo
      SAIDA.avisou = !el("aviso-momento").hidden;
      el("motivo").value = "pergunta composta";
      el("form-defeito").disparar("submit");      // avanca pelo defeito, sem virar
      SAIDA.depois_do_defeito = !el("aviso-momento").hidden;
    """)["saida"]
    assert out == {"avisou": True, "depois_do_defeito": False}


def test_aviso_persistente_de_armazenamento_continua_na_tela():
    """Sem `window.claude` (fora do runtime), o aviso de armazenamento e persistente."""
    out = _rodar(LOTE3, """
      SAIDA.inicio = !el("aviso").hidden;
      tecla(" "); tecla("3"); tecla(" "); tecla("3");
      SAIDA.depois = !el("aviso").hidden;
      SAIDA.dados_abertos = el("fim-bruto").open;
    """)["saida"]
    assert out == {"inicio": True, "depois": True, "dados_abertos": True}


# --------------------------------------------------------------------------
# Item 4: tempo ativo
# --------------------------------------------------------------------------

def test_tempo_conta_com_card_na_tela_e_para_no_teto_ocioso():
    out = _rodar(LOTE3, """
      passar(20000);                   // 20 s olhando o card
      SAIDA.a = segundos();
      passar(60 * 60 * 1000);          // uma hora sem gesto: so o teto de 3 min conta
      SAIDA.b = segundos();
    """)["saida"]
    assert out["a"] == 20
    assert out["b"] == 180, "o teto ocioso e 3 min desde o ultimo gesto"


def test_tempo_nao_conta_com_a_aba_oculta():
    out = _rodar(LOTE3, """
      passar(10000);
      ocultar(true);
      passar(10 * 60 * 1000);
      ocultar(false);
      passar(5000);
      SAIDA.s = segundos();
    """)["saida"]
    assert out["s"] == 15


def test_tecla_p_pausa_e_retoma():
    out = _rodar(LOTE3, """
      passar(10000);
      tecla("p");
      SAIDA.pausado = el("btn-pausa").attrs["aria-pressed"];
      passar(60000);
      tecla("P");
      passar(4000);
      SAIDA.s = segundos();
      SAIDA.retomado = el("btn-pausa").attrs["aria-pressed"];
    """)["saida"]
    assert out == {"pausado": "true", "s": 14, "retomado": "false"}


def test_tempo_ativo_sobrevive_ao_reload():
    primeiro = _rodar(LOTE3, "passar(42000);")
    out = _rodar(LOTE3, "passar(3000); SAIDA.s = segundos();",
                 {"armazem": primeiro["armazem"]})["saida"]
    assert out["s"] == 45


def test_storage_quebrado_degrada_para_zero_sem_erro():
    out = _rodar(LOTE3, "passar(7000); SAIDA.s = segundos();", {"lsQuebrado": True})["saida"]
    assert out["s"] == 7


# --------------------------------------------------------------------------
# Item 5: tela de fim
# --------------------------------------------------------------------------

DIAS = ["2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29",
        "2026-09-30"]


def _prev(n1, n2, n3, n4):
    return {"1": n1, "2": n2, "3": n3, "4": n4}


def test_fim_mostra_desempenho_e_agenda_com_as_notas_recebidas():
    cards = [
        _card(0, "IC", _prev("2026-09-23", "2026-09-25", "2026-09-27", "2026-10-09")),
        _card(1, "Asma", _prev("2026-09-23", "2026-09-24", "2026-09-26", "2026-10-02")),
        _card(2, "DPOC", _prev("2026-09-23", "2026-09-24", "2026-09-28", "2026-10-05")),
    ]
    lote = _lote(cards, agenda_base={"dias": [{"data": d, "n": 10} for d in DIAS],
                                     "vencidos_fora_do_lote": 5})
    out = _rodar(lote, """
      tecla(" "); passar(10000); tecla("3");      // IC -> 3 -> 27/09
      tecla(" "); passar(10000); tecla("1");      // Asma -> 1 -> hoje: volta amanha (24/09)
      tecla(" "); passar(10000); tecla("2");      // DPOC -> 2 -> 24/09
      tecla(" "); passar(5000); tecla("3");       // relearning da Asma: nao gera 2a nota
      tecla(" "); passar(5000); tecla("3");       // relearning do DPOC
      SAIDA.fim = !el("fim").hidden;
      SAIDA.pct = el("fim-pct").textContent;
      SAIDA.tempo = el("fim-tempo").textContent;
      SAIDA.dist = el("fim-dist").innerHTML;
      SAIDA.temas = el("fim-temas").filhos.map(function(li){ return li.textContent; });
      SAIDA.agenda_visivel = !el("fim-agenda").hidden;
      SAIDA.svg = el("fim-agenda-grafico").innerHTML;
      SAIDA.origem = el("fim-origem").textContent;
    """)["saida"]
    assert out["fim"] and out["agenda_visivel"]
    assert out["pct"] == "33%"                    # 1 de 3 com nota >= 3
    assert out["tempo"] == "0:40"
    assert 'data-nota="1" data-n="1"' in out["dist"] and 'data-nota="3" data-n="1"' in out["dist"]
    assert sorted(out["temas"]) == ["Asma", "DPOC"]
    svg = out["svg"]
    assert "<svg" in svg and 'role="img"' in svg
    # dia 1 (24/09): base 10 + 5 vencidos fora + Asma(1, clampada) + DPOC(2) = 10+5 | 2
    assert 'data-dia="2026-09-24" data-base="15" data-lote="2"' in svg
    assert 'data-dia="2026-09-27" data-base="10" data-lote="1"' in svg
    assert 'data-dia="2026-09-30" data-base="10" data-lote="0"' in svg
    for proibido in ("ArtifactData", "--record-lote", "FSRS"):
        assert proibido not in out["origem"]


def test_lote_antigo_sem_campos_novos_mostra_so_desempenho():
    out = _rodar(LOTE3, """
      tecla(" "); tecla("3"); tecla(" "); tecla("4"); tecla(" "); tecla("3");
      SAIDA.fim = !el("fim").hidden;
      SAIDA.pct = el("fim-pct").textContent;
      SAIDA.resumo = !el("fim-resumo").hidden;
      SAIDA.agenda = !el("fim-agenda").hidden;
    """)["saida"]
    assert out == {"fim": True, "pct": "100%", "resumo": True, "agenda": False}


# --------------------------------------------------------------------------
# s195: espelho local das notas, reenvio ao db e previsao no dia da nota
# --------------------------------------------------------------------------

def test_notas_sobrevivem_ao_reload_sem_db():
    """Sem `window.claude` (db fora), as notas ficam no localStorage e o reload retoma de onde
    parou -- o incidente de 24/09 (90 notas perdidas num reload) nao se repete no mesmo aparelho."""
    primeiro = _rodar(LOTE3, """
      tecla(" "); tecla("3"); tecla(" "); tecla("1");
      SAIDA.feitos = el("feitos").textContent;
      SAIDA.aviso = el("aviso").textContent;
    """)
    assert primeiro["saida"]["feitos"] == "2"
    assert "SEM CONEXAO" in primeiro["saida"]["aviso"]
    guardadas = json.loads(primeiro["armazem"]["medhub.notas.t-js"])
    assert sorted(n["card_id"] for n in guardadas) == [100, 101]
    segundo = _rodar(LOTE3, """
      SAIDA.feitos = el("feitos").textContent;
      SAIDA.pergunta = el("pergunta").textContent;
      SAIDA.fila = el("pendentes").textContent;
    """, {"armazem": primeiro["armazem"]})["saida"]
    # 100 (nota 3) resolvido; 101 (nota 1) volta em relearning; 102 nunca visto vem primeiro
    assert segundo == {"feitos": "2", "pergunta": "P2?", "fila": "2"}


def test_notas_locais_sao_reenviadas_quando_o_db_abre():
    primeiro = _rodar(LOTE3, 'tecla(" "); tecla("4"); tecla(" "); tecla("3");')
    segundo = _rodar(LOTE3, """
      SAIDA.feitos = el("feitos").textContent;
      SAIDA.aviso_oculto = el("aviso").hidden;
      SAIDA.momento = el("aviso-momento").textContent;
    """, {"armazem": primeiro["armazem"], "db": {"docs": {"100": {"card_id": 100, "rating_primeira": 4, "ts": "x"}}}})
    assert segundo["saida"]["feitos"] == "2"
    assert segundo["escritas"] == ["101"], "so o que o db nao tinha e reenviado"
    assert set(segundo["db"]) == {"100", "101"}
    assert segundo["saida"]["aviso_oculto"] is True
    assert "1 nota(s)" in segundo["saida"]["momento"]


def test_falha_de_gravacao_no_meio_do_lote_avisa_forte_e_guarda_local():
    out = _rodar(LOTE3, """
      tecla(" "); tecla("3");
      SAIDA.aviso = el("aviso").textContent;
      SAIDA.visivel = !el("aviso").hidden;
    """, {"db": {"docs": {}}, "dbFalha": True})
    assert out["saida"]["visivel"] and "SEM CONEXAO" in out["saida"]["aviso"]
    assert "falha ao salvar: falhou" in out["saida"]["aviso"]
    assert [n["card_id"] for n in json.loads(out["armazem"]["medhub.notas.t-js"])] == [100]


def test_falha_passageira_volta_a_tentar_na_nota_seguinte_e_reenvia_o_que_ficou_no_aparelho():
    """Regressao de 27/09 (s203): 1 set() com "unavailable" desligava o banco pelo RESTO do lote --
    as notas seguintes iam so para o aparelho ate um reload. A nota seguinte tem de tentar de
    novo; aceita, o que so o aparelho tinha vai junto e o aviso forte sai."""
    out = _rodar(LOTE3, """
      tecla(" "); tecla("3");                  // 100: o banco falha (passageiro)
      SAIDA.aviso_depois_da_falha = !el("aviso").hidden;
      tecla(" "); tecla("4");                  // 101: o banco voltou
      SAIDA.aviso_oculto = el("aviso").hidden;
      SAIDA.momento = el("aviso-momento").textContent;
    """, {"db": {"docs": {}}, "dbFalhas": 1})
    assert out["saida"]["aviso_depois_da_falha"] is True
    assert set(out["db"]) == {"100", "101"}, "a nota que falhou foi reenviada quando o banco voltou"
    assert out["saida"]["aviso_oculto"] is True
    assert "1 nota(s)" in out["saida"]["momento"]


def test_db_que_chega_depois_da_1a_nota_poda_a_fila_e_nao_volta_no_tempo():
    """Regressao de 01/10 (s210, lote 2026-09-30a): o operador saiu do artifact e voltou; o
    aparelho voltou sem espelho e a fila recomecou do 1o card. Ele deu nota ANTES de o db
    responder (`interagiu`) e o remontar pos-db era pulado: os cards ja feitos voltavam."""
    out = _rodar(LOTE3, """
      tecla(" "); tecla("4");                  // 100 de novo (o db ainda nao respondeu)
      abrirDb();                               // db: 100 e 101 ja feitos noutra abertura
      SAIDA.pergunta = el("pergunta").textContent;
      SAIDA.fila = el("pendentes").textContent;
    """, {"dbAdiado": True, "db": {"docs": {
        "100": {"card_id": 100, "rating_primeira": 4, "ts": "2026-10-01T12:00:00Z"},
        "101": {"card_id": 101, "rating_primeira": 3, "ts": "2026-10-01T12:01:00Z"}}}})
    assert out["saida"] == {"pergunta": "P2?", "fila": "1"}
    assert out["db"]["100"]["ts"] == "2026-10-01T12:00:00Z", "a 1a nota gravada nao e sobrescrita"


def test_defeito_que_so_o_aparelho_tem_sobrevive_ao_db_e_e_reenviado():
    """Regressao de 01/10 (card 714): o aparelho tinha nota 1 + defeito; o db so a nota 1. O
    restaurar do db sobrescrevia o registro local e o defeito sumia do aparelho e do banco."""
    local = [{"card_id": 101, "rating_primeira": 1, "ts": "2026-10-01T13:02:33Z",
              "defeito": True, "motivo": "Siglas"}]
    out = _rodar(LOTE3, "SAIDA.fila = el(\"pendentes\").textContent;", {
        "armazem": {"medhub.notas.t-js": json.dumps(local)},
        "db": {"docs": {"101": {"card_id": 101, "rating_primeira": 1,
                                "ts": "2026-10-01T13:02:33Z"}}}})
    espelho = {n["card_id"]: n for n in json.loads(out["armazem"]["medhub.notas.t-js"])}
    assert espelho[101].get("defeito") is True and espelho[101].get("motivo") == "Siglas"
    assert out["db"]["101"].get("defeito") is True, "o que o db tem a menos e reenviado"
    assert out["saida"]["fila"] == "2", "card com defeito sai da fila"


def test_voltar_a_aba_ressincroniza_com_o_db():
    """Notas que chegaram ao db por outra abertura (outro aparelho, outra aba) enquanto esta
    estava oculta saem da fila quando ela volta a ficar visivel."""
    out = _rodar(LOTE3, """
      tecla(" "); tecla("3");                  // 100 feito aqui; na tela: P1
      ocultar(true);
      DB["101"] = {card_id:101, rating_primeira:4, ts:"2026-10-01T12:05:00Z"};
      ocultar(false);
      SAIDA.pergunta = el("pergunta").textContent;
    """, {"db": {"docs": {}}})
    assert out["saida"]["pergunta"] == "P2?"


def test_redrill_feito_nao_volta_a_fila_ao_remontar():
    """Regressao de 01/10 (s210): os 61 cards de nota < 3 ja redrilados voltavam a fila a cada
    remontagem (reload, volta da aba): o resultado do redrill nao era persistido. O redrill
    resolvido grava `redrill_ok` no registro (aparelho e db), sem tocar a 1a nota."""
    out = _rodar(LOTE3, """
      tecla(" "); tecla("1");                  // 100: nota 1 -> relearning
      tecla(" "); tecla("3");                  // 101
      tecla(" "); tecla("4");                  // 102
      tecla(" "); tecla("3");                  // redrill do 100 resolvido
      ocultar(true); ocultar(false);           // volta da aba remonta a fila
      SAIDA.fila = el("pendentes").textContent;
      SAIDA.fim = !el("fim").hidden;
    """, {"db": {"docs": {}}})
    assert out["saida"] == {"fila": "0", "fim": True}
    assert out["db"]["100"]["rating_primeira"] == 1, "a 1a nota segue a unica gravavel"
    assert out["db"]["100"].get("redrill_ok") is True
    recarga = _rodar(LOTE3, 'SAIDA.fila = el("pendentes").textContent;',
                     {"armazem": out["armazem"]})["saida"]
    assert recarga["fila"] == "0", "o reload tambem nao reapresenta o redrill feito"


def test_fim_com_banco_fora_diz_que_as_notas_estao_no_aparelho():
    """Com o espelho local ok, a tela de fim nao pode dizer 'Nada foi salvo fora desta tela': as
    notas estao no aparelho e vao ao banco no proximo abrir com conexao."""
    out = _rodar(LOTE3, """
      tecla(" "); tecla("3"); tecla(" "); tecla("3"); tecla(" "); tecla("3");
      SAIDA.origem = el("fim-origem").textContent;
      SAIDA.titulo = el("fim-titulo").textContent;
    """, {"db": {"docs": {}}, "dbFalha": True})
    assert out["saida"]["titulo"] == "Lote concluido"
    assert "guardadas neste aparelho" in out["saida"]["origem"]
    assert "Nada foi salvo" not in out["saida"]["origem"]


def test_agenda_desloca_a_previsao_para_o_dia_da_nota():
    """Export de vespera (gerado_em 23/09) drenado em 24/09: a previsao "24/09" da nota 4 e, na
    verdade, 25/09 -- o grafico andava 1 dia para tras e mostrava o card 'agendado hoje'."""
    cards = [_card(0, "IC", _prev("2026-09-23", "2026-09-23", "2026-09-24", "2026-09-24")),
             _card(1, "Asma", _prev("2026-09-23", "2026-09-25", "2026-09-27", "2026-10-09"))]
    lote = _lote(cards, agenda_base={"dias": [{"data": d, "n": 0} for d in DIAS],
                                     "vencidos_fora_do_lote": 0})
    out = _rodar(lote, """
      relogio = new Date(2026, 8, 24, 21, 0, 0).getTime();   // nota dada em 24/09, 21h local
      tecla(" "); tecla("4");                                 // IC: previsao 24/09 -> 25/09
      tecla(" "); tecla("3");                                 // Asma: 27/09 -> 28/09
      SAIDA.svg = el("fim-agenda-grafico").innerHTML;
    """)["saida"]["svg"]
    assert 'data-dia="2026-09-24" data-base="0" data-lote="0"' in out
    assert 'data-dia="2026-09-25" data-base="0" data-lote="1"' in out
    assert 'data-dia="2026-09-28" data-base="0" data-lote="1"' in out


# --------------------------------------------------------------------------
# Estatico (roda sempre, com ou sem node)
# --------------------------------------------------------------------------

def test_estatico_aviso_momentaneo_separado_do_persistente():
    js = _js_do_player()
    assert 'avisarMomento("Vire o card' in js
    assert 'avisar("Vire o card' not in js
    for funcao in ("function virar(){", "function mostrar(){"):
        corpo = js.split(funcao, 1)[1].split("\n  function ", 1)[0]
        assert "esconderMomento()" in corpo, "%s tem de esconder o aviso momentaneo" % funcao
    assert 'id="aviso-momento"' in REGIOES["corpo"] and 'id="aviso"' in REGIOES["corpo"]


def test_estatico_timer_sem_relogio_de_parede():
    js = _js_do_player()
    assert "Math.min.apply(null, ts)" not in js, "o inicio pelo menor ts era relogio de parede"
    assert "visibilitychange" in js and "TETO_OCIOSO_MS" in js


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
