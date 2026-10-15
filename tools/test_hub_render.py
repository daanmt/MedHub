"""test_hub_render.py -- a tela de revelacao da aba Listas do hub (qzSolucao & cia.) em node.

Spec: veredito do /ai-eng sobre a s200, #6 ALTERA (26/09/2026) -- o render da cadeia sai de um harness
AD HOC para este arquivo; desde 02/10/2026 (s211, `feedback-cadeia-declarada-part-2`) ele prende a
tela em que o ALUNO declara cada elo (Sim / Incerteza / Desatencao / Nao) e a pagina NAO infere quebra.
As funcoes REAIS sao extraidas de `core/templates/hub.html` (casamento de chaves, nunca copiadas) e
rodam em node com um DOM falso minimo (`$` devolve objetos com hidden/className/innerHTML/value).

Cenarios com GOLDEN do HTML inteiro em `tools/goldens/hub_render/<cenario>.html` (declarada,
presumida, conflito, legado) -- qualquer mudanca de render acusa. Mudou de proposito:
`MEDHUB_ATUALIZAR_GOLDEN=1 pytest tools/test_hub_render.py`, e o diff do golden vai no commit (e a
declaracao). Golden ausente = falha, nunca verde vazio. ⚰️ *Os goldens por estado da analise
(ok/quebrou/nao_usou/nao_avaliado/provisoria) morreram em 02/10/2026 com a leitura pelas letras.*

Sem `node` no PATH os cenarios sao PULADOS (skip declarado); os testes estaticos rodam sempre.
LIMITE DECLARADO: mede o HTML que as funcoes produzem, nao o CSS nem o que o celular desenha.

s214 (pedidos do operador em 04/10/2026), no fim do arquivo: as SECOES RECOLHIVEIS das abas Aulas e
Listas e o GRIFO DENTRO DAS AULAS -- ver o cabecalho da secao "s214".
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import hub  # noqa: E402  (s214: o quadro REAL de hub.html_quadro_de para as secoes)

TEMPLATE = (ROOT / "core" / "templates" / "hub.html").read_text(encoding="utf-8")
GOLDEN_DIR = ROOT / "tools" / "goldens" / "hub_render"
NODE = shutil.which("node")
ATUALIZAR = os.environ.get("MEDHUB_ATUALIZAR_GOLDEN") == "1"


def _fim_do_regex(src, i):
    """Indice logo apos o `/` que fecha o regex literal aberto em `src[i]` (classe [...] inclusa)."""
    i += 1
    classe = False
    while i < len(src):
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            classe = True
        elif c == "]":
            classe = False
        elif c == "/" and not classe:
            return i + 1
        i += 1
    raise ValueError("regex literal sem fim")


def extrair_funcao(src, assinatura):
    """O texto de `function nome(...){ ... }` casando chaves e pulando strings e regex literais."""
    ini = src.index(assinatura)
    i = src.index("{", ini)
    prof, aspas = 0, None
    while i < len(src):
        c = src[i]
        if aspas:
            if c == "\\":
                i += 2
                continue
            if c == aspas:
                aspas = None
        elif c == "/" and src[:i].rstrip()[-1:] in tuple("(,=:[!&|?{};"):
            i = _fim_do_regex(src, i)
            continue
        elif c in "'\"`":
            aspas = c
        elif c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                return src[ini:i + 1]
        i += 1
    raise ValueError(f"chaves desbalanceadas em {assinatura}")


def _declaracao(src, inicio):
    """O texto de `var NOME = {...};` (objeto literal no topo da declaracao)."""
    i = src.index(inicio)
    corpo = extrair_funcao(src[i:].replace(inicio, "function _x(){", 1), "function _x(){")
    return inicio + corpo[len("function _x(){"):] + ";"


FUNCS = "\n".join([_declaracao(TEMPLATE, "var QZ_DECL = {"), _declaracao(TEMPLATE, "var QZ_LEGADO = {")] +
                  [extrair_funcao(TEMPLATE, a) for a in (
                      "function qzEsc(s){", "function qzAlts(txt){", "function qzAltsHtml(q, r, revelada, g){",
                      "function qzCadeia(q){", "function qzPrecisaDeclarar(q, r){", "function qzDeclPendente(q, r){",
                      "function qzConflitos(q, r){", "function qzElosDe(q, r, a){", "function qzSolucao(q, r){",
                      "function qzAgenteHtml(a){", "function qzDeclarar(i, st){", "function qzDefeito(motivo){",
                      "function qzDefeitoUi(r){", "function qzEhSimulado(l){", "function qzModoDaLista(l){",
                      "function qzComFlag(l){", "function qzListaAtual(){", "function qzModoUi(l){",
                      "function qzResponder(){", "function qzRevelaAoAbrir(r){", "function qzTrava(q, r){",
                      "function qzResumoElos(qs, resp){", "function qzElosFimHtml(qs, resp){",
                      "function qzConcluirUi(pendentes){", "function qzGrifoMesclar(intervalos, novo){",
                      "function qzGrifoValido(v, n){", "function qzGrifoHtml(texto, intervalos){",
                      "function qzGrifoRemover(intervalos, pos){", "function qzGrifosDe(q){",
                      "function qzGrifosSalvar(q, g){")] +
                  [re.search(r"\n  (var QZ_DICA_TRAVA = [^\n]+;)", TEMPLATE).group(1),
                   re.search(r"\n  (var QZ_ORDEM_REVER = [^\n]+;)", TEMPLATE).group(1)])

HARNESS = r"""
var els = {};
function $(id){ return els[id] || (els[id] = {id: id, hidden: false, textContent: "", className: "", innerHTML: "", value: "",
  disabled: false, checked: false, attrs: {}, setAttribute: function(k, v){ this.attrs[k] = v; },
  querySelectorAll: function(){ return []; }}); }
var QZ = {ana: __ANA__, qs: [__Q__], pos: 0, resp: {}, grifos: {}, lista: "t26"};
var LS = {};
function qzLs(k, v){ if(v === undefined){ return LS[k] === undefined ? null : JSON.parse(JSON.stringify(LS[k])); } LS[k] = JSON.parse(JSON.stringify(v)); }
var GRAVADOS = [];
function qzGravar(r){ QZ.resp[r.num] = r; GRAVADOS.push(JSON.parse(JSON.stringify(r))); return Promise.resolve(true); }
function qzAgora(){ return "2026-10-02T12:00:00.000Z"; }
__FUNCS__
var q = QZ.qs[0], r = __R__;
if(r){ QZ.resp[q.num] = r; }
var SAIDA = {};
__ACAO__
console.log(JSON.stringify(SAIDA));
"""

RENDER = """qzSolucao(q, r); var b = $("qz-medhub");
SAIDA = {className: b.className, html: b.innerHTML, texto: b.textContent, obj_hidden: $("qz-obj").hidden,
         obj: $("qz-obj").textContent, pe: $("qz-sol-pe").innerHTML, gravados: GRAVADOS};"""

# v3: identificar -> recordar -> descartar B; A certa
SOL3 = {"versao": 3, "pede": "A conduta na gestante com HbA1c 6,8%.",
        "cadeia": [{"tipo": "identificar", "elo": "Identificou que as GJ estão na faixa de DMG.",
                    "chave": "GJ 92-125 = DMG.", "habilidade": "Classificar a GJ do 1º trimestre"},
                   {"tipo": "recordar", "elo": "Recordou que HbA1c >= 6,5% fecha DM prévio.",
                    "chave": "HbA1c >= 6,5% = DM prévio.", "habilidade": "Aplicar o critério pela HbA1c"},
                   {"tipo": "descartar", "letra": "B", "elo": "Descartou o DMG (B) pela HbA1c.",
                    "chave": "A HbA1c decide.", "habilidade": "Usar o achado que exclui"}],
        "alternativas": {"A": {"certa": True, "porque": "HbA1c fecha DM prévio."},
                         "B": {"porque": "Ignora a HbA1c."},
                         "C": {"porque": "TOTG com GJ alterada."},
                         "D": {"porque": "Adia o tratamento."}},
        "conferir": "Banca usa o critério antigo."}
# v2 (t26/t96): cada errada ainda carrega `elo` -- a pagina NAO pode mais usa-lo
SOL2 = {"versao": 2, "pede": "A conduta na gestante com HbA1c 6,8%.",
        "cadeia": [{"elo": "Classificar a glicemia de jejum", "chave": "GJ 92-125 = DMG."},
                   {"elo": "Aplicar o critério de DM prévio", "chave": "HbA1c >= 6,5% = DM prévio."},
                   {"elo": "Definir a conduta", "chave": "Tratar já."}],
        "alternativas": {"A": {"certa": True, "porque": "HbA1c fecha DM prévio."},
                         "B": {"elo": 1, "porque": "Lê a GJ como normal."},
                         "C": {"elo": 2, "porque": "Ignora a HbA1c."},
                         "D": {"elo": 3, "porque": "Adia o tratamento."}},
        "conferir": ""}
ALTS = "A) DM prévio; tratar já\nB) DMG\nC) TOTG com 24 semanas\nD) Repetir a GJ"


def _q(sol=SOL3, **extra):
    q = {"num": 8, "solucao_medhub": sol, "objetivo": "DM prévio x DMG", "fontes_medhub": "SBD 2026",
         "alternativas": ALTS, "gabarito": "A"}
    q.update(extra)
    return q


def _resp(letra, confianca="duvida", riscadas=(), **extra):
    r = {"num": 8, "letra": letra, "gabarito": "A", "correta": letra == "A", "confianca": confianca,
         "riscadas": list(riscadas)}
    r.update(extra)
    return r


def _rodar(q, r, ana=None, acao=RENDER):
    if not NODE:
        pytest.skip("node ausente no PATH: tela de revelacao nao verificada (skip declarado)")
    prog = (HARNESS.replace("__FUNCS__", FUNCS).replace("__ACAO__", acao)
                   .replace("__ANA__", json.dumps({str(q["num"]): ana} if ana else {}))
                   .replace("__Q__", json.dumps(q)).replace("__R__", json.dumps(r)))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8",
                             timeout=60)
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


class _Cadeia(HTMLParser):
    """Cada <li> de `ol.qz-cadeia` -> {classe, on: [estados marcados], presumido, chave, em}."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elos, self._na_ol, self._li, self._em, self._chave, self.texto = [], False, None, False, False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if tag == "ol" and "qz-cadeia" in cls:
            self._na_ol = True
        elif tag == "li" and self._na_ol:
            self._li = {"classe": cls, "on": [], "presumido": False, "chave": None, "em": None}
        elif self._li is not None and tag == "button" and "on" in cls.split():
            self._li["on"].append(a.get("data-st"))
            self._li["presumido"] = self._li["presumido"] or "presumido" in cls.split()
        elif self._li is not None and tag == "span" and "qz-chave" in cls:
            self._chave, self._li["chave"] = True, ""
        elif self._li is not None and tag == "em":
            self._em, self._li["em"] = True, ""

    def handle_endtag(self, tag):
        if tag == "span":
            self._chave = False
        elif tag == "em":
            self._em = False
        elif tag == "li" and self._li is not None:
            self.elos.append(self._li)
            self._li = None
        elif tag == "ol":
            self._na_ol = False

    def handle_data(self, data):
        self.texto.append(data)
        if self._chave:
            self._li["chave"] += data
        if self._em:
            self._li["em"] += data


def _cadeia(html):
    p = _Cadeia()
    p.feed(html)
    p.close()
    return p.elos, "".join(p.texto)


def _golden(nome, html):
    arq = GOLDEN_DIR / f"{nome}.html"
    if ATUALIZAR:
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        arq.write_text(html + "\n", encoding="utf-8", newline="\n")
    assert arq.is_file(), f"golden ausente: {arq} (gerar com MEDHUB_ATUALIZAR_GOLDEN=1)"
    assert html + "\n" == arq.read_text(encoding="utf-8"), (
        f"render de '{nome}' mudou -- se foi de proposito, regenere o golden e comite o diff")


#: frases da leitura pelas letras, revogada em 02/10/2026 -- nenhuma pode voltar ao HTML
INFERENCIA = ("provável quebra", "a sua letra cai", "evidência: você riscou", "leitura provisória",
              "falha no elo", "Você: riscou")


def test_funcoes_extraidas_do_template():
    """A extracao acha as funcoes inteiras (ancora sumiu = falha alta, nunca skip)."""
    assert FUNCS.count("function ") >= 13 and FUNCS.rstrip().endswith(("}", ";"))
    assert "qz-cadeia" in FUNCS and "data-st" in FUNCS


# ------------------------------------------------ DoD 1: declaracao por elo (+ goldens)

#: cenario -> (q, resposta, analise ou None, [(classe do li, estados on, presumido, tem chave, em)])
CENARIOS = {
    "declarada": (_q(), _resp("C", elos=["sim", "incerteza", "nao"]), None,
                  [("sim", ["sim"], False, True, None), ("incerteza", ["incerteza"], False, True, None),
                   ("nao", ["nao"], False, True, None)]),
    "presumida": (_q(), _resp("A", "solida", ["B", "C"]), None,
                  [("", ["sim"], True, False, None)] * 3),
    "conflito": (_q(), _resp("B", elos=["sim", "nao", "sim"]), None,
                 [("sim", ["sim"], False, True, None), ("nao", ["nao"], False, True, None),
                  ("sim conflito", ["sim"], False, True,
                   "conflito: você marcou a alternativa que este elo descarta")]),
    "legado": (_q(SOL2), _resp("C", riscadas=["B"]),
               {"estados": ["ok", "quebrou", "nao_usou"], "quebrou": 1, "veredito_em": "2026-09-26T21:10:00Z"},
               [("sim", ["sim"], False, True, None), ("nao", ["nao"], False, True, None),
                ("desatencao", ["desatencao"], False, True, None)]),
}


@pytest.mark.parametrize("nome", sorted(CENARIOS))
def test_render_da_declaracao(nome):
    q, resp, ana, esperado = CENARIOS[nome]
    out = _rodar(q, resp, ana)
    assert out["className"] == "qz-sol"
    elos, texto = _cadeia(out["html"])
    assert [(e["classe"], e["on"], e["presumido"], e["chave"] is not None, e["em"]) for e in elos] == esperado
    assert out["html"].count('data-st="') == 4 * len(esperado)               # 4 botoes por elo
    assert not any(f in texto for f in INFERENCIA)
    assert out["gravados"] == []                                              # render nunca grava
    assert out["obj_hidden"] is False and out["obj"] == "DM prévio x DMG"
    _golden(nome, out["html"])


def test_presumida_rotula_e_nao_grava_e_legado_rotula_a_data():
    _, texto = _cadeia(_rodar(*CENARIOS["presumida"][:3])["html"])
    assert "Sim presumido" in texto
    _, texto = _cadeia(_rodar(*CENARIOS["legado"][:3])["html"])
    assert "da análise de 26/09" in texto


def test_declaracao_grava_o_array_alinhado_a_cadeia():
    """O toque grava `elos` (um por elo, vocabulario declarado) pelo qzGravar: errada comeca vazia;
    tocar de novo desmarca; presumido materializa o Sim que ele via; legado NAO vira declaracao."""
    acao = """qzDeclarar(1, "nao"); qzDeclarar(0, "sim"); qzDeclarar(0, "sim"); qzDeclarar(2, "xx"); qzDeclarar(9, "sim");
SAIDA = {gravados: GRAVADOS.map(function(g){ return g.elos; })};"""
    out = _rodar(_q(), _resp("C"), None, acao)
    assert out["gravados"] == [["", "nao", ""], ["sim", "nao", ""], ["", "nao", ""]]
    pres = _rodar(_q(), _resp("A", "solida"), None, 'qzDeclarar(1, "incerteza"); SAIDA = {g: GRAVADOS};')
    assert [g["elos"] for g in pres["g"]] == [["sim", "incerteza", "sim"]]
    leg = _rodar(*CENARIOS["legado"][:3], 'qzDeclarar(0, "sim"); SAIDA = {g: GRAVADOS};')
    assert [g["elos"] for g in leg["g"]] == [["sim", "", ""]]
    assert set(leg["g"][0]) >= {"letra", "confianca", "riscadas", "elos"}    # o doc inteiro, nao so o campo


def test_precisa_e_pendente():
    acao = """var c = function(rr){ return [qzPrecisaDeclarar(q, rr), qzDeclPendente(q, rr)]; };
SAIDA = {errada: c(r), solida: c({correta: true, confianca: "solida"}), duvida: c({correta: true, confianca: "duvida"}),
  parcial: c({correta: false, elos: ["sim", "", "nao"]}), cheia: c({correta: false, elos: ["sim", "nao", "nao"]}),
  torta: c({correta: false, elos: ["sim", "nao"]}), sem_cadeia: [qzPrecisaDeclarar({num: 8, solucao_medhub: "texto"}, r), qzDeclPendente({num: 8}, r)]};"""
    out = _rodar(_q(), _resp("C"), None, acao)
    assert out == {"errada": [True, True], "solida": [False, False], "duvida": [True, True],
                   "parcial": [True, True], "cheia": [True, False], "torta": [True, True],
                   "sem_cadeia": [False, False]}


# ------------------------------------------------ DoD 2: zero inferencia

@pytest.mark.parametrize("sol", [SOL2, SOL3], ids=["v2", "v3"])
def test_pagina_nao_infere_quebra_pela_letra(sol):
    """Errada, riscou uma letra, sem declaracao e sem analise: todos os elos neutros (sem classe,
    nenhum botao marcado), nenhuma frase da leitura pelas letras -- nem na v2, que ainda tem `elo`
    nas alternativas."""
    out = _rodar(_q(sol), _resp("C", riscadas=["B"]))
    elos, texto = _cadeia(out["html"])
    assert [(e["classe"], e["on"], e["chave"], e["em"]) for e in elos] == [("", [], None, None)] * 3
    assert not any(f in texto for f in INFERENCIA)
    assert "Como foi cada elo?" in texto


def test_template_nao_carrega_a_inferencia():
    """Nem no HTML montado nem no JS: as frases da leitura pelas letras sairam do template."""
    for frase in INFERENCIA:
        assert frase not in TEMPLATE, frase


# ------------------------------------------------ DoD 3: porque sob a alternativa

class _Alts(HTMLParser):
    """`.qz-alt` -> {classe, porque (texto) e se esta escondido}."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.alts, self._pq = {}, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div" and "qz-alt" in (a.get("class") or "").split():
            self._l = a.get("data-l")
            self.alts[self._l] = {"classe": a.get("class"), "porque": None, "escondido": None}
        elif tag == "p" and "qz-porque" in (a.get("class") or ""):
            self._pq = self.alts[self._l]
            self._pq.update(porque="", escondido="hidden" in a)

    def handle_endtag(self, tag):
        if tag == "p":
            self._pq = None

    def handle_data(self, data):
        if self._pq is not None:
            self._pq["porque"] += data


def _alts(html):
    p = _Alts()
    p.feed(html)
    p.close()
    return p.alts


def test_porque_aparece_sob_o_gabarito_e_a_marcada():
    acao = """SAIDA = {antes: qzAltsHtml(q, null, false), depois: qzAltsHtml(q, r, true)};"""
    out = _rodar(_q(), _resp("C", riscadas=["D"]), None, acao)
    antes = _alts(out["antes"])
    assert all(a["porque"] is None for a in antes.values())                   # antes de revelar: nada
    d = _alts(out["depois"])
    assert (d["A"]["porque"], d["A"]["escondido"]) == ("HbA1c fecha DM prévio.", False)   # gabarito
    assert (d["C"]["porque"], d["C"]["escondido"]) == ("TOTG com GJ alterada.", False)    # marcada
    assert d["B"]["escondido"] is True and d["D"]["escondido"] is True                    # no toque
    assert "gab" in d["A"]["classe"] and "errada" in d["C"]["classe"] and "riscada" in d["D"]["classe"]
    assert "Alternativas" not in out["depois"] and "elo" not in out["depois"]


def test_secao_alternativas_e_linha_voce_sairam_da_solucao():
    out = _rodar(_q(), _resp("C", riscadas=["B"], elos=["sim", "nao", "nao"]))
    assert "qz-altsol" not in out["html"] and "Alternativas" not in out["html"]
    assert "Você:" not in out["html"] and "porque" not in out["html"]
    assert "Conferir: Banca usa o critério antigo." in out["pe"] and "SBD 2026" in out["pe"]


# ------------------------------------------------ DoD 4: linha do agente

ANALISE = {"veredito_hub": "Você declarou o elo 2 como Não: é o critério da HbA1c.", "armadilha": "GJ normal engana.",
           "cards": [812, 813], "pedia": "Pedia X", "comporta": "Comporta Y", "conflitos": []}


def test_linha_do_agente_sem_conflito_nao_pede_veredito():
    out = _rodar(_q(), _resp("C"), None, "SAIDA = {h: qzAgenteHtml(%s)};" % json.dumps(ANALISE))
    h = out["h"]
    assert "Você declarou o elo 2" in h and "Armadilha: GJ normal engana." in h and "#812 #813" in h
    assert "data-v=" not in h and "qz-vered-nota" not in h
    assert "Pedia" not in h and "Comporta" not in h


def test_linha_do_agente_com_conflito_pede_veredito():
    a = dict(ANALISE, conflitos=[1], veredito_operador="em_parte")
    out = _rodar(_q(), _resp("C"), None, "SAIDA = {h: qzAgenteHtml(%s), vazio: qzAgenteHtml(null)};" % json.dumps(a))
    assert re.findall(r'data-v="(\w+)"', out["h"]) == ["concordo", "em_parte", "discordo"]
    assert 'data-v="em_parte" class="on"' in out["h"] and "qz-vered-nota" in out["h"]
    assert out["vazio"] == ""


# ------------------------------------------------ DoD 5: conflito deterministico

def test_conflitos_so_no_descartar_da_letra_marcada_declarado_sim():
    acao = """SAIDA = {
  sim: qzConflitos(q, {letra: "b", elos: ["sim", "sim", "sim"]}),
  nao: qzConflitos(q, {letra: "B", elos: ["sim", "sim", "nao"]}),
  outra: qzConflitos(q, {letra: "C", elos: ["sim", "sim", "sim"]}),
  sem: qzConflitos(q, {letra: "B"}), torta: qzConflitos(q, {letra: "B", elos: ["sim"]}),
  v2: qzConflitos({solucao_medhub: %s}, {letra: "B", elos: ["sim", "sim", "sim"]})};""" % json.dumps(SOL2)
    out = _rodar(_q(), _resp("B"), None, acao)
    assert out == {"sim": [2], "nao": [], "outra": [], "sem": [], "torta": [], "v2": []}


# ------------------------------------------------ DoD 6: defeito de cadeia + limpeza

def test_defeito_de_cadeia_grava_motivo():
    acao = """var vazio = qzDefeito("   "); var ok = qzDefeito("  o elo 2 repete o gabarito ");
SAIDA = {vazio: vazio, ok: ok, gravados: GRAVADOS, st: $("qz-defeito-st").textContent, form: $("qz-defeito-form").hidden};"""
    out = _rodar(_q(), _resp("C"), None, acao)
    assert out["vazio"] is False and out["ok"] is True and len(out["gravados"]) == 1
    assert out["gravados"][0]["cadeia_defeito"] == {"motivo": "o elo 2 repete o gabarito",
                                                    "ts": "2026-10-02T12:00:00.000Z"}
    assert out["st"] == "Enviado: o elo 2 repete o gabarito" and out["form"] is True


def test_chips_de_causa_sairam():
    """Os 8 chips de "Onde quebrou?" e a caixa de 5 campos sairam; sobra UMA linha opcional de
    racional; o campo `elo` (chip) deixou de ser escrito."""
    for morto in ('data-e="nao_sabia"', "Onde quebrou?", 'id="qz-elo"', 'id="qz-meta-erro"', '"Pedia"',
                  '"Comporta"', "O que te levou à letra marcada?"):
        assert morto not in TEMPLATE, morto
    assert TEMPLATE.count('placeholder="Algo a acrescentar? (opcional)"') == 1
    i = TEMPLATE.index("var r = {lista:")
    assert " elo:" not in TEMPLATE[i:TEMPLATE.index("};", i)]
    assert not re.search(r"\br\.elo\s*=", TEMPLATE)


def test_resposta_antiga_sem_campos_novos_abre_sem_erro():
    """Lista em curso (respostas sem `elos`, `cadeia_defeito`, `racional`): a tela abre e a linha do
    defeito fica limpa."""
    r = {"num": 8, "letra": "C", "gabarito": "A", "correta": False, "confianca": "chute"}
    out = _rodar(_q(), r, None, RENDER + ' qzDefeitoUi(r); SAIDA.st = $("qz-defeito-st").textContent;')
    assert out["className"] == "qz-sol" and out["st"] == "" and out["gravados"] == []


def test_v1_em_texto_segue_como_texto():
    q = _q("Pede a conduta. Decide: HbA1c >= 6,5%. Gabarito A.", objetivo="")
    out = _rodar(q, _resp("C"))
    assert out["className"] == "qz-texto" and out["html"] == ""
    assert out["texto"].startswith("Pede a conduta.") and out["obj_hidden"] is True


# ------------------------------------------------ DoD 7: vocabulario, forma

BRIEF = (ROOT / "docs" / "SOLUCAO-MEDHUB-BRIEF.md").read_text(encoding="utf-8")


def _vocabulario_do_brief():
    (linha,) = [l for l in BRIEF.splitlines() if "Vocabulário declarado:" in l]
    return set(re.findall(r"`([a-z_]+)`", linha.split("Vocabulário declarado:", 1)[1]))


def _estados_que_a_pagina_declara():
    decl = _declaracao(TEMPLATE, "var QZ_DECL = {")
    return set(re.findall(r"[{,]\s*([a-z_]+)\s*:", decl))


def test_vocabulario_de_estados_do_brief_e_o_da_pagina():
    """#8 do /ai-eng: o estado por elo tem UM portador (o brief). O vocabulário DECLARADO que ele
    define é exatamente o que a página oferece -- estado novo num lado só quebra aqui."""
    assert _vocabulario_do_brief() == _estados_que_a_pagina_declara() == {
        "sim", "incerteza", "desatencao", "nao"}


def test_skill_e_autopsia_apontam_o_brief_e_nao_redefinem():
    """`/banco-emed` e `/analisar-questao` §3.3 apontam §Estado por elo; nenhum dos dois volta a
    carregar a definição (o rótulo de `nao_usou` é a assinatura de uma cópia)."""
    for nome in ("banco-emed.md", "analisar-questao.md"):
        txt = (ROOT / ".claude" / "commands" / nome).read_text(encoding="utf-8")
        assert "SOLUCAO-MEDHUB-BRIEF.md" in txt and "Estado por elo" in txt, nome
        assert "sabia, não aplicou" not in txt, nome


def _css_da_tela_revelada():
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    return [l for l in css.splitlines() if re.match(r"\s*\.(qz-porque|qz-alt\.tem-pq|qz-cad|qz-sol|qz-pede|qz-decl|qz-cadeia|"
                                                     r"qz-chave|qz-rodape|qz-linha|qz-link|qz-defeito|qz-analise|qz-ag-|"
                                                     r"qz-modo-lista|qz-modo-escolha|qz-seg\.qz-seg2|qz-elos|qz-rev\.(nao|incerteza|desatencao))", l)
            or "qz-decl" in l]


def test_forma_da_tela_revelada():
    """Craftsmanship do DoD 7: cor so por token, toque >= 44 px nos botoes novos, rotulo de botao
    <= 15 caracteres, nada fixo na rolagem, grid item com min-width:0."""
    css = _css_da_tela_revelada()
    assert css, "CSS da tela revelada nao encontrado"
    assert not [l for l in css if re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", l)]
    assert not re.search(r"position\s*:\s*(sticky|fixed)", TEMPLATE)
    for sel in (".qz-decl button{", ".qz-link{", ".qz-defeito-form button{", ".qz-linha{"):
        (regra,) = [l for l in css if sel in l]
        assert "min-height:44px" in regra, sel
    assert "min-width:0" in [l for l in css if l.startswith(".qz-cadeia li{")][0]
    rotulos = list(re.findall(r':\s*"([^"]+)"', _declaracao(TEMPLATE, "var QZ_DECL = {")))
    # s229: o seletor de modo saiu (lista = Estudo, simulado = Prova); "Modo estudo/prova" nao sao mais rotulos
    rotulos += ["Erro na cadeia", "Enviar", "Concordo", "Em parte", "Discordo",
                "Concluir lista", "Rever uma a uma", "Mudar resposta"]
    assert "qz-modo-lista" not in TEMPLATE and "qz-modo-escolha" not in TEMPLATE.split("<script", 1)[0]
    assert all(r in TEMPLATE for r in rotulos) and max(len(r) for r in rotulos) <= 15
    for morto in ("Marcar lista como resolvida", "Rever em sequência", "Alterar resposta"):   # > 15 (celular)
        assert morto not in TEMPLATE, morto


# ------------------------------------------------ s201: aba Listas dividida em Questoes | Simulados

LISTAS_JS = "\n".join([_declaracao(TEMPLATE, "var ROT_QZ = {"), _declaracao(TEMPLATE, "var QZ_SUB = {"),
                       # s214: as semanas das Listas recolhem; o estado (secAberta) e lido na renderizacao
                       re.search(r"\n  (var SECOES_CHAVE = [^\n]+;)", TEMPLATE).group(1)] +
                      [extrair_funcao(TEMPLATE, a) for a in (
                          "function qzEsc(s){", "function temaExibido(t){",   # P20: o titulo da lista
                          "function qzLs(k, v){", "function qzChip(l){",       # s226: chip so fora do normal
                          "function qzItemLista(l, atrasada, motivo){",   # P21 (s220): sem qzAulasHtml
                          "function qzEhSimulado(l){",
                          # s226 (sprint part-4): os grupos do sprint e a data do simulado
                          "function qzDia(iso){", "function qzGruposSprint(sp, ls){", "function qzRenderSprint(ls){",
                          "function qzQuandoSim(l){",
                          "function qzNomeSim(l){", "function qzItemSim(l, daVez){", "function qzRenderSimulados(ls){",
                          "function secoesLer(){", "function secAberta(id, padrao){", "function secSemanaAtual(atual, comItens){",
                          "function secPadraoAberta(chave, corrente){", "function secTituloHtml(id, alvo, aberta, miolo){",
                          "function qzRenderListas(){")])

HARNESS_LISTAS = r"""
var els = {};
function botao(m){ var b = {m: m, innerHTML: "", on: false, attrs: {}};
  b.getAttribute = function(k){ return k === "data-m" ? b.m : b.attrs[k]; };
  b.setAttribute = function(k, v){ b.attrs[k] = v; };
  b.classList = {toggle: function(c, v){ b.on = !!v; }};
  return b; }
var BOT = [botao("questoes"), botao("simulados")];
function $(id){ if(!els[id]){ els[id] = {id: id, innerHTML: "", textContent: "", hidden: false,
  querySelectorAll: function(){ return id === "qz-modo" ? BOT : []; }}; } return els[id]; }
var QZ = {listas: __LISTAS__, modo: __MODO__};
var QZ_SEM = {atual: 2, datas: {"2": ["21/09", "27/09"]}};
var QZ_SPRINT = __SPRINT__;
var QZ_DIAS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
__FUNCS__
qzRenderListas();
console.log(JSON.stringify({html: $("qz-listas").innerHTML, sub: $("qz-sub").textContent,
  botoes: BOT.map(function(b){ return [b.m, b.on, b.innerHTML]; })}));
"""

LISTAS = [
    {"_id": "t49", "tema": "Hérnias da Parede Abdominal", "area": "Cirurgia", "semana": 2, "seq": 1, "q": 21, "status": "capturada"},
    {"_id": "t26", "tema": "Diabetes na Gestação", "area": "Obstetrícia", "semana": 2, "seq": 2, "q": 19, "status": "resolvida"},
    {"_id": "t1794", "tema": "UERJ 2022 -- prova INTEIRA (60q), cronometrada, 5 blocos", "area": "Simulado", "semana": 3, "seq": 90, "q": 60, "status": "capturada"},
    {"_id": "t1793", "tema": "UERJ 2021 -- prova INTEIRA (60q), cronometrada, 5 blocos", "area": "Simulado", "semana": 2, "seq": 90, "q": 60, "status": "capturada"},
    {"_id": "t890", "tema": "UERJ 2026 -- prova INTEIRA (100q), cronometrada, 5 blocos", "area": "Simulado", "semana": 6, "seq": 90, "q": 100, "status": "pendente"},
]


def _listas(modo, sprint=None, listas=None):
    if not NODE:
        pytest.skip("node ausente no PATH: divisao da aba nao verificada (skip declarado)")
    prog = (HARNESS_LISTAS.replace("__FUNCS__", LISTAS_JS)
            .replace("__LISTAS__", json.dumps(LISTAS if listas is None else listas))
            .replace("__MODO__", json.dumps(modo)).replace("__SPRINT__", json.dumps(sprint)))
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        caminho = f.name
    try:
        out = subprocess.run([NODE, caminho], capture_output=True, text=True, encoding="utf-8", timeout=60)
    finally:
        Path(caminho).unlink(missing_ok=True)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_modo_questoes_mostra_so_as_listas_e_conta_as_abertas():
    out = _listas("questoes")
    assert "Hérnias" in out["html"] and "UERJ" not in out["html"]
    assert "Diabetes na Gestação" in out["html"]                          # resolvida, recolhida no fim
    assert out["botoes"] == [["questoes", True, "Questões<small>1</small>"],
                             ["simulados", False, "Simulados<small>2</small>"]]
    assert out["sub"].startswith("As listas na ordem do plano de hoje")


def test_modo_simulados_mostra_as_provas_na_ordem_do_plano_com_a_da_vez():
    out = _listas("simulados")
    html = out["html"]
    assert "Hérnias" not in html and "UERJ 2026" not in html                # pendente (nao carregada) fica fora
    assert html.index("UERJ 2021") < html.index("UERJ 2022")                 # ordem do plano (semana)
    assert "UERJ 2021 <span class=\"qd-n\">· a da vez</span>" in html and html.count("a da vez") == 1
    assert "60 questões" in html and "~3 h" in html and " -- prova INTEIRA" not in html
    assert out["botoes"][1][1] is True and out["sub"].startswith("As provas da UERJ")


# ------------------------------------------------ s226 (sprint-final-uerj part-4): Listas pelo sprint

#: o mesmo plano sintetico para o Painel e as Listas: hoje = 13/10; a #49 rolou de ontem, a #26 e de hoje,
#: a #30 de amanha, o simulado #1793 no domingo 25/10, a #77 fora com o motivo; a #12 feita nao entra
HOJE_SPRINT = date(2026, 10, 13)
PLANO_SPRINT = [
    {"id": 12, "status": "concluida", "dia_plano": "2026-10-13", "tema": "Feita", "area": "Cirurgia",
     "bloco": "CIR", "q_previstas": 20, "semana_plano": 1},
    {"id": 26, "status": "pendente", "dia_plano": "2026-10-13", "tema": "Diabetes na Gestação",
     "area": "Obstetrícia", "bloco": "GO", "q_previstas": 19, "semana_plano": 2},
    {"id": 49, "status": "pendente", "dia_plano": "2026-10-12", "tema": "Hérnias", "area": "Cirurgia",
     "bloco": "CIR", "q_previstas": 21, "semana_plano": 2},
    {"id": 30, "status": "pendente", "dia_plano": "2026-10-14", "tema": "Asma", "area": "Pediatria",
     "bloco": "PED", "q_previstas": 30, "semana_plano": 3},
    {"id": 1793, "status": "pendente", "dia_plano": "2026-10-25", "tema": "UERJ 2026 -- prova INTEIRA",
     "area": "Simulado", "bloco": "SIM", "q_previstas": 100, "semana_plano": 4},
    {"id": 77, "status": "pendente", "dia_plano": None, "tema": "Fora", "area": "Clínica Médica",
     "bloco": "CM", "q_previstas": 40, "semana_plano": 5, "nota": "sprint: fora (sem vaga ate 31/10)"},
]
LISTAS_SPRINT = [
    {"_id": "t26", "tarefa": 26, "tema": "Diabetes na Gestação", "area": "Obstetrícia", "semana": 2, "seq": 2, "q": 19, "status": "capturada"},
    {"_id": "t49_2", "tarefa": 49, "tema": "Hérnias parte 2", "area": "Cirurgia", "semana": 2, "seq": 9, "q": 10, "status": "capturada"},
    {"_id": "t49_1", "tarefa": 49, "tema": "Hérnias parte 1", "area": "Cirurgia", "semana": 2, "seq": 8, "q": 11, "status": "capturada"},
    {"_id": "t30", "tarefa": 30, "tema": "Asma", "area": "Pediatria", "semana": 3, "seq": 1, "q": 30, "status": "capturada"},
    {"_id": "t77", "tarefa": 77, "tema": "Fora", "area": "Clínica Médica", "semana": 5, "seq": 1, "q": 40, "status": "capturada"},
    {"_id": "t12", "tarefa": 12, "tema": "Feita", "area": "Cirurgia", "semana": 1, "seq": 1, "q": 20, "status": "capturada"},
    {"_id": "t5", "tarefa": 5, "tema": "Resolvida", "area": "Cirurgia", "semana": 1, "seq": 1, "q": 20, "status": "resolvida"},
    {"_id": "t1793", "tarefa": 1793, "tema": "UERJ 2026 -- prova INTEIRA (100q)", "area": "Simulado", "semana": 4, "seq": 90, "q": 100, "status": "capturada"},
]


def _ids_do_grupo(html, grupo):
    """Os ids das listas de uma secao `data-grupo` da aba Listas, na ordem da tela."""
    m = re.search(r'<section[^>]* data-grupo="%s">(.*?)</section>' % re.escape(grupo), html)
    return re.findall(r'data-qzl="([^"]+)"', m.group(1)) if m else []


def test_listas_e_painel_mesmo_hoje(monkeypatch):
    """O "Hoje" da aba Listas e o "Plano de hoje" do Painel saem do MESMO `plano.agenda_sprint`: do mesmo
    plano sintetico, as tarefas das listas de Hoje = as tarefas do Painel, na mesma ordem."""
    from tools import painel
    monkeypatch.setattr(painel, "_aulas_por_tarefa", lambda: {})
    monkeypatch.setattr(painel, "_rd_nao_assinada", lambda: None)
    do_painel = [t["id"] for t in painel._bloco_sprint(PLANO_SPRINT, HOJE_SPRINT)["hoje"]]
    sprint = hub.dados_sprint(PLANO_SPRINT, HOJE_SPRINT)
    assert sprint["hoje"] == do_painel == [49, 26], "a rolada de ontem entra no hoje, na ordem do dia"
    assert sprint["q_hoje"] == painel._bloco_sprint(PLANO_SPRINT, HOJE_SPRINT)["q_hoje"]
    out = _listas("questoes", sprint, LISTAS_SPRINT)
    hoje = _ids_do_grupo(out["html"], "hoje")
    tarefas = []
    for i in hoje:
        t = next(l["tarefa"] for l in LISTAS_SPRINT if l["_id"] == i)
        if t not in tarefas:
            tarefas.append(t)
    assert tarefas == do_painel and hoje == ["t49_1", "t49_2", "t26"], "a mesma tarefa pelo seq"


def test_listas_agrupam_por_hoje_proximos_dias_e_fora_do_sprint():
    sprint = hub.dados_sprint(PLANO_SPRINT, HOJE_SPRINT)
    html = _listas("questoes", sprint, LISTAS_SPRINT)["html"]
    assert "Semana" not in html and "Atrasadas" not in html and "qd-atraso" not in html
    assert html.index('data-grupo="hoje"') < html.index("Próximos dias") < html.index('data-grupo="d2026-10-14"') \
        < html.index('data-grupo="fora"') < html.index("Resolvidas")
    assert "Hoje <span class=\"qd-n\">3 listas · 40 questões</span>" in html
    assert "qua 14/10 <span class=\"qd-n\">1 lista · 30 questões</span>" in html
    assert _ids_do_grupo(html, "d2026-10-14") == ["t30"]
    # s226 (audit part-4): o Fora e SO o do Painel; lista sem dia nem marca vai para "Outras listas"
    assert _ids_do_grupo(html, "fora") == ["t77"]
    assert _ids_do_grupo(html, "outras") == ["t12"], "a de tarefa sem dia (feita no plano) cai em Outras listas"
    assert "sem vaga até 31/10" in html and "fora do plano até 01/11" in html and "Outras listas · 1" in html
    assert re.search(r'<section data-grupo="hoje">', html) and re.search(r'<section data-recolhida data-grupo="fora">', html)
    assert "UERJ" not in html, "o simulado segue na sua sub-aba"


def test_sem_hub_sprint_as_listas_caem_nas_semanas():
    html = _listas("questoes", None, LISTAS_SPRINT)["html"]
    assert "Semana 2" in html and 'data-grupo=' not in html


def test_simulado_leva_a_data_do_sprint():
    sprint = hub.dados_sprint(PLANO_SPRINT, HOJE_SPRINT)
    html = _listas("simulados", sprint, LISTAS_SPRINT)["html"]
    assert '<span class="qz-quando">dom 25/10</span>' in html and "semana 4" not in html


# ------------------------------------------------ s227 (hub-tema-v4 part-3): Listas e Cards em placas

def test_listas_em_placas_e_a_grade_de_duas_colunas_no_desktop():
    """DoD 3: Hoje e uma placa; Proximos dias + Fora do sprint + Outras listas, outra; Resolvidas, uma terceira --
    grupos, ordem e rotulos os de antes (os testes acima seguem). A grade so ganha as duas colunas (`qz-duas`) com
    a placa da direita; no desktop Proximos ocupa a coluna 2 nas duas linhas e Resolvidas sobe para baixo de Hoje.
    Simulados no mesmo idioma; sem sprint, as semanas numa placa (secoes irmas diretas). O seletor e a legenda
    ficam fora das placas."""
    sprint = hub.dados_sprint(PLANO_SPRINT, HOJE_SPRINT)
    html = _listas("questoes", sprint, LISTAS_SPRINT)["html"]
    assert html.startswith('<div class="qz-grade qz-duas"><div class="placa qz-p-hoje"><section data-grupo="hoje">')
    hoje, resto = html.split('<div class="placa qz-p-prox">', 1)
    prox, feitas = resto.split('<div class="placa qz-p-feitas">', 1)
    assert 'data-grupo="d' not in hoje and 'data-grupo="fora"' not in hoje
    assert prox.startswith('<h3 class="qz-grupo">Próximos dias</h3>')
    assert all('data-grupo="%s"' % g in prox for g in ("d2026-10-14", "fora", "outras"))
    assert feitas.startswith('<details class="qd-feitas"><summary>Resolvidas') and "data-grupo=" not in feitas
    so_hoje = _listas("questoes", dict(sprint, proximos=[], fora=[]),
                      [l for l in LISTAS_SPRINT if l["tarefa"] in (26, 49)])["html"]
    assert so_hoje.startswith('<div class="qz-grade"><div class="placa qz-p-hoje">') and "qz-p-prox" not in so_hoje, \
        "sem a placa da direita, uma coluna"
    sims = _listas("simulados", sprint, LISTAS_SPRINT + [
        {"_id": "t1790", "tarefa": 1790, "tema": "UERJ 2020 -- prova", "area": "Simulado", "semana": 1, "seq": 90,
         "q": 60, "status": "resolvida"}])["html"]
    assert sims.startswith('<div class="qz-grade qz-sim"><div class="placa qz-p-provas"><section>')
    assert '<div class="placa qz-p-feitas"><details class="qd-feitas"><summary>Resolvidos' in sims
    semanas = _listas("questoes", None, LISTAS_SPRINT)["html"]
    assert semanas.startswith('<div class="qz-grade"><div class="placa qz-p-semanas"><section')
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    assert re.search(r"\n\.qz-grade\{display:grid;[^}]*align-items:start", css)
    assert ".qz-grade .qz-lista > li:last-child > button{border-bottom-color:transparent}" in css
    desk = re.search(r"@media \(min-width:900px\)\{(.*?)\n\}", css, re.S).group(1)
    assert re.search(r"\.qz-duas,\.qz-sim\{grid-template-columns:repeat\(2,minmax\(0,1fr\)\)\}", desk)
    assert ".qz-duas{grid-template-rows:auto 1fr}" in desk
    assert ".qz-duas > .qz-p-prox{grid-column:2;grid-row:1 / span 2}" in desk
    assert ".qz-duas > .qz-p-feitas{grid-column:1;grid-row:2}" in desk
    i = TEMPLATE.index('<div class="qz-cabeca">')
    cabeca = TEMPLATE[i:TEMPLATE.index("\n      </div>", i)]
    assert 'id="qz-modo"' in cabeca and 'id="qz-sub"' in cabeca
    assert TEMPLATE.index('class="qz-cabeca"') < TEMPLATE.index('id="qz-listas"'), "seletor e legenda fora das placas"


def test_cards_topo_e_card_em_placas_e_o_standalone_leva_a_placa():
    """DoD 4: o topo do player (titulo, contadores, relogio, pausa, barra, tally) e UMA placa; o card, a placa
    ELEVADA (--afundado) logo abaixo, com os botoes fora dela; a tela de fim, uma placa. O standalone do
    --build-player embute o tema (a primitiva .placa vem junto). Ids e ordem do corpo: os de antes."""
    from tools.fsrs_queue import TEMPLATE_PLAYER, embutir_tema
    txt = TEMPLATE_PLAYER.read_text(encoding="utf-8")
    corpo = txt[txt.index("@player:corpo:inicio"):txt.index("@player:corpo:fim")]
    topo = re.search(r'<div class="placa cards-topo">(.*?)\n  </div>', corpo, re.S).group(1)
    for id_ in ("dia-contador", "pendentes", "relogio", "btn-pausa", "progresso", "tally"):
        assert 'id="%s"' % id_ in topo, id_
    card = re.search(r'<article class="card placa" id="card"[^>]*>(.*?)</article>', corpo, re.S).group(1)
    assert "btn-virar" not in card and "notas-botoes" not in card, "os botoes ficam fora da placa do card"
    # s229 (pedido dele, 15/10): o Virar subiu para o bloco de cima, com Pausar e Defeito
    assert corpo.index("cards-topo") < corpo.index('id="btn-virar"') < corpo.index('id="card"') < corpo.index('id="fim"')
    assert '<section class="painel-fim placa" id="fim" hidden>' in corpo
    css = txt[txt.index("@player:css:inicio"):txt.index("@player:css:fim")]
    assert ".card.placa{background:var(--afundado);border-color:var(--linha-forte)}" in css
    assert not re.search(r"(?:^|[}\n])\.placa(?:::before)?\{", css), "a placa e composta, nunca redefinida"
    assert re.search(r"\n\.placa\{", embutir_tema(txt)), "o standalone leva a primitiva do tema"


def test_virar_pausar_e_defeito_no_bloco_de_cima():
    """s229 (pedido dele, 15/10: "'Virar o card' sobe para o bloco de cima junto com os outros dois, mantendo a
    paleta dele (ciano); 'Pausar' em ambar/amarelo; 'Defeito do card' em rosa"): os TRES numa linha
    (`.topo-acoes`) dentro da placa do topo, depois da barra; as opcoes do defeito logo abaixo. O registro gravado
    nao muda (`defeito:true, motivo` -- o que o --record-lote le como marca de reforja)."""
    from tools.fsrs_queue import TEMPLATE_PLAYER
    txt = TEMPLATE_PLAYER.read_text(encoding="utf-8")
    corpo = txt[txt.index("@player:corpo:inicio"):txt.index("@player:corpo:fim")]
    topo = corpo[corpo.index('<div class="placa cards-topo">'):corpo.index('<main id="drill">')]
    linha = re.search(r'<div class="acoes topo-acoes">(.*?)</div>', topo, re.S).group(1)
    assert [m for m in re.findall(r'id="(btn-[a-z]+)"', linha)] == ["btn-virar", "btn-pausa", "btn-defeito"]
    assert '<button id="btn-virar" class="primario">' in linha
    assert '<button type="button" id="btn-pausa" class="pausa" aria-pressed="false">' in linha
    assert '<button type="button" id="btn-defeito" class="defeito" aria-expanded="false" aria-controls="defeito-opcoes">' in linha
    assert topo.index('id="progresso"') < topo.index('topo-acoes') < topo.index('id="defeito-opcoes"') < topo.index('id="form-defeito"')
    main = corpo[corpo.index('<main id="drill">'):corpo.index("</main>")]
    assert "btn-virar" not in main and "btn-pausa" not in main and "btn-defeito" not in main
    assert corpo.count('id="btn-defeito"') == corpo.count('id="btn-virar"') == corpo.count('id="btn-pausa"') == 1
    css = txt[txt.index("@player:css:inicio"):txt.index("@player:css:fim")]
    assert ".pausa{border-color:var(--aviso);color:var(--aviso)}" in css, "Pausar em ambar"
    assert "#btn-defeito{border-color:var(--rosa);color:var(--rosa)}" in css, "Defeito em rosa"
    assert ".primario{background:var(--acento)" in css, "Virar segue ciano"
    js = txt[txt.index("@player:js:inicio"):]
    assert "var registro = {card_id:id, ts:anterior.ts, defeito:true, motivo:motivo};" in js, "o dado gravado nao muda"


def test_tocar_no_card_vira_e_o_card_tem_camadas():
    """s228 (pedido dele): tocar no card vira (o mesmo virar(), selecao de texto nao vira); a frente leva a dica e o
    cursor; o verso e o degrau de baixo da mesma placa (--card de borda a borda), nao caixa dentro do card."""
    from tools.fsrs_queue import TEMPLATE_PLAYER
    txt = TEMPLATE_PLAYER.read_text(encoding="utf-8")
    js = txt[txt.index("@player:js:inicio"):]
    assert '$("card").addEventListener("click", function(){' in js and "virar();" in js.split('$("card").addEventListener("click"', 1)[1][:300]
    assert '$("card").classList.add("frente");' in js and '$("card").classList.remove("frente");' in js
    css = txt[txt.index("@player:css:inicio"):txt.index("@player:css:fim")]
    assert ".card.frente{cursor:pointer}" in css
    # s229 (adendo dele, 15/10: "pode remover o 'toque no card para virar'"): a mecanica fica, a micro-dica sai
    assert "toque no card para virar" not in txt and 'id="toque"' not in txt and ".toque{" not in css
    assert "border-top:1px solid var(--borda-placa);border-radius:0 0 calc(var(--raio-placa) - 1px)" in css
    assert "box-shadow" not in css, "sem sombra"


# ------------------------------------------------ s227 (hub-tema-v4 part-4): questao, fim e leitor em placas

class _Cadeias(HTMLParser):
    """Le o markup do template (o conteudo de <script>/<style> e dado para o parser): `ids` = id -> as listas de
    classes da raiz ate o elemento (inclusive); `itens` = [tag, id, data-*/type/role, rotulo] de todo elemento com
    id e de todo controle, em ordem de documento, com os ids dos ancestrais. Rotulo = o 1o texto direto do botao ou
    do summary. Uma tag que fecha fecha tambem o que ficou aberto dentro dela."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha, self.ids, self.itens = [], {}, []
        self._rotulo = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if a.get("id"):
            self.ids[a["id"]] = [c for _t, c, _i in self.pilha] + [cls]
        if a.get("id") or tag in ("button", "input", "textarea", "label", "form", "details", "summary"):
            extra = " ".join("%s=%s" % (k, v) for k, v in sorted(a.items()) if k.startswith("data-") or k in ("type", "role"))
            self.itens.append(([tag, a.get("id", ""), extra, ""], {i for _t, _c, i in self.pilha if i}))
            if tag in ("button", "summary"):
                self._rotulo = self.itens[-1][0]
        if tag not in self.VOID:
            self.pilha.append((tag, cls, a.get("id")))

    def handle_endtag(self, tag):
        if tag in ("button", "summary"):
            self._rotulo = None
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        if self._rotulo is not None and not self._rotulo[3] and data.strip():
            self._rotulo[3] = data.strip()


def _cadeias(html):
    p = _Cadeias()
    p.feed(html)
    return p


def _itens_de(html, raiz):
    """Os itens [tag, id, data-*/type/role, rotulo] do elemento de id `raiz` e de dentro dele, em ordem de documento."""
    return [it for it, acima in _cadeias(html).itens if it[1] == raiz or raiz in acima]


def test_questao_fim_e_leitor_em_placas():
    """DoD 2 e 4: o enunciado (meta, texto, figuras) e uma placa; as alternativas, a certeza e os botoes ficam no
    fundo (nunca caixa dentro de caixa); veredito + cadeia (+ analise e o rodape) formam a placa do resultado, com a
    Proxima fora; no fim, metricas | por bloco | Elos | revisao, uma placa cada, os botoes fora; o leitor e uma placa
    sem padding em volta do iframe e a assinatura e a placa de baixo, com a mesma largura. A barra e o trilho seguem
    no fundo, com a largura do corpo (um max-width so no conteiner da tela, regra s212). Nenhuma placa dentro de
    outra; a placa e composta, nunca redefinida. Camada de leitura: a pagina da aula e a placa, as caixas sobem um
    degrau, a figura no idioma da placa, a medida de 46rem e a tabela que rola (L1) seguem."""
    p = _cadeias(TEMPLATE)

    def placa_de(id_):
        cadeia = [c for c in p.ids[id_] if "placa" in c]
        assert len(cadeia) <= 1, (id_, cadeia)   # nunca placa dentro de placa
        return " ".join(cadeia[0]) if cadeia else None

    for id_ in ("qz-pos", "qz-banca", "qz-tags", "qz-enun", "qz-figs", "qz-figura"):
        assert placa_de(id_) == "placa qz-enun-placa", id_
    for id_ in ("qz-veredito", "qz-medhub-box", "qz-medhub", "qz-analise", "qz-racional", "qz-defeito", "qz-sol-box",
                "qz-forum-box"):
        assert placa_de(id_) == "placa qz-resultado", id_
    for id_ in ("qz-voltar", "qz-tema", "qz-grifo", "qz-relogio", "qz-trilho", "qz-aviso-lista",
                "qz-alts", "qz-antes", "qz-seg", "qz-flag", "qz-ant", "qz-pular", "qz-responder", "qz-status",
                "qz-proxima", "qz-concluir", "qz-rever", "qz-fim-status", "hub-leitor-voltar", "hub-leitor-aviso"):
        assert placa_de(id_) is None, id_
    assert placa_de("qz-tiles") == placa_de("qz-erradas") == "placa qz-p-metricas"
    assert placa_de("qz-porobj") == "placa qz-porobj"
    assert placa_de("qz-elos-fim") == "placa qz-p-elos"
    assert placa_de("qz-revisao") == "placa qz-p-revisao"
    assert placa_de("hub-leitor-quadro") == "placa hub-leitor-placa"
    assert placa_de("hub-assina") == placa_de("hub-assina-btn") == "hub-assina placa"
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    assert "#aba-cards,#hub-leitor,#qz-player{max-width:var(--wrap);margin-inline:auto}" in css
    assert not re.search(r"\.(qz-trilho|hub-leitor-barra|qz-corpo|qz-enun-placa|qz-resultado)\{[^}]*max-width", css)
    assert not re.search(r"(?:^|[}\n])\.placa(?:::before)?\{", css), "a placa e composta, nunca redefinida"
    assert ".placa.hub-leitor-placa{padding:0}" in css
    assert ".hub-assina.placa{margin-inline:0!important}" in css, "assinatura com a largura da placa do leitor"
    assinatura = re.search(r"\n\.hub-assina\{([^}]*)\}", css).group(1)
    assert "border" not in assinatura and "background" not in assinatura, "superficie e borda vem da .placa"
    assert re.search(r"\.qz-p-elos:has\(> \.qz-elos-fim\[hidden\]\),\s*\.hub-leitor-placa:has\(> \.hub-quadro\[hidden\]\)"
                     r"\{display:none\}", css), "placa vazia nao aparece"
    assert not re.search(r"\.qz-tiles\{[^}]*border", css), "a placa de metricas faz o papel dos dois filetes"
    aula = (ROOT / "core" / "templates" / "tema-aula.css").read_text(encoding="utf-8")
    assert ":root{--leitor-placa:var(--card)}" in aula
    assert "body{--paper:var(--leitor-placa);--card:var(--afundado)}" in aula
    assert re.search(r"figure\.fig-an\{--card:var\(--leitor-placa\);background:var\(--leitor-placa\);"
                     r"border-color:var\(--borda-placa\)", aula)
    assert re.search(r"\.trilho-box\{background:var\(--sunk\);border:0", aula), ".trilho-box sem moldura dentro da placa"
    assert ".wrap{max-width:46rem;" in aula, "a medida de leitura segue"
    assert re.search(r"\n\.tw\{[^}]*overflow-x:auto", aula), "L1: a tabela larga rola na propria caixa"
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", aula), "cor so por token"


# o inventario da tela da questao e do leitor ANTES da part 4 (HEAD 232bab5): id, data-*/type/role e rotulo, na
# ordem do documento. A part 4 so pos classe e wrapper: nenhum id, botao, ordem ou rotulo pode mudar
INVENTARIO_QUESTAO = [
    ["div", "qz-player", "", ""], ["button", "qz-voltar", "type=button", "‹ Todas as listas"], ["p", "qz-tema", "", ""],
    # s229 (pedido dele, 15/10): o botao unico do grifo (3 cores em cascata) tambem nas Listas; o seletor de modo
    # (`qz-modo-lista`, `qz-modo-escolha`) saiu: lista = Estudo, simulado = Prova
    ["div", "qz-grifo", "data-aberto=false", ""], ["button", "qz-grifo-btn", "type=button", "Aa"],
    ["div", "qz-grifo-cor", "role=group", ""], ["button", "", "data-cor=rosa type=button", "Aa"],
    ["button", "", "data-cor=ciano type=button", "Aa"], ["button", "", "data-cor=amarelo type=button", "Aa"],
    ["span", "qz-relogio", "", ""], ["div", "qz-trilho", "", ""],
    ["p", "qz-aviso-lista", "", ""],
    ["div", "qz-questao", "", ""], ["span", "qz-pos", "", ""], ["span", "qz-banca", "", ""], ["span", "qz-tags", "", ""],
    ["p", "qz-enun", "", ""], ["div", "qz-figs", "", ""], ["p", "qz-figura", "", ""], ["div", "qz-alts", "role=radiogroup", ""],
    ["div", "qz-antes", "", ""], ["div", "qz-seg", "", ""], ["button", "", "data-c=solida type=button", "Sólida"],
    ["button", "", "data-c=duvida type=button", "Dúvida"], ["button", "", "data-c=chute type=button", "Chute"],
    ["label", "qz-marca", "", ""], ["input", "qz-flag", "type=checkbox", ""], ["button", "qz-ant", "type=button", "‹ Anterior"],
    ["button", "qz-pular", "type=button", "Pular ›"], ["button", "qz-responder", "type=button", "Responder"],
    ["div", "qz-depois", "", ""], ["p", "qz-veredito", "", ""], ["section", "qz-medhub-box", "", ""],
    ["p", "qz-cad-tit", "", ""], ["span", "qz-obj", "", ""], ["span", "qz-conferir", "", ""], ["div", "qz-medhub", "", ""],
    ["div", "qz-analise", "", ""], ["input", "qz-racional", "type=text", ""], ["div", "qz-defeito", "", ""],
    ["button", "qz-defeito-abrir", "type=button", "Erro na cadeia"], ["form", "qz-defeito-form", "", ""],
    ["input", "qz-defeito-motivo", "type=text", ""], ["button", "", "type=submit", "Enviar"], ["p", "qz-defeito-st", "", ""],
    ["div", "qz-sol-pe", "", ""], ["details", "qz-sol-box", "", ""], ["summary", "", "", "Comentário do professor"],
    ["div", "qz-sol", "", ""], ["details", "qz-forum-box", "", ""], ["summary", "", "", "Fórum"], ["div", "qz-forum", "", ""],
    ["p", "qz-status", "", ""], ["button", "qz-proxima", "type=button", "Próxima"], ["div", "qz-fim", "", ""],
    ["div", "qz-tiles", "", ""], ["p", "qz-erradas", "", ""], ["div", "qz-porobj", "", ""], ["div", "qz-elos-fim", "", ""],
    ["ol", "qz-revisao", "", ""], ["button", "qz-concluir", "type=button", "Concluir lista"],
    ["button", "qz-rever", "type=button", "Rever uma a uma"], ["p", "qz-fim-status", "", ""],
]
INVENTARIO_LEITOR = [
    ["div", "hub-leitor", "", ""], ["button", "hub-leitor-voltar", "type=button", "‹ Teoria"], ["p", "hub-leitor-titulo", "", ""],
    # s228: o botao unico da cor do grifo, so no leitor da Teoria, com as tres cores em cascata
    ["div", "hub-grifo", "data-aberto=false", ""], ["button", "hub-grifo-btn", "type=button", "Aa"],
    ["div", "hub-grifo-cor", "role=group", ""], ["button", "", "data-cor=rosa type=button", "Aa"],
    ["button", "", "data-cor=ciano type=button", "Aa"], ["button", "", "data-cor=amarelo type=button", "Aa"],
    ["p", "hub-leitor-aviso", "", ""], ["a", "hub-leitor-link", "", ""], ["iframe", "hub-leitor-quadro", "", ""],
    ["div", "hub-assina", "data-st=sem role=group", ""], ["p", "hub-assina-tit", "", ""],
    ["textarea", "hub-assina-coment", "", ""], ["p", "hub-assina-retorno", "", ""], ["p", "hub-assina-st", "role=status", ""],
    ["button", "hub-assina-btn", "type=button", "Assinar leitura"],
]


def test_ids_botoes_e_ordem_da_questao_e_do_leitor_nao_mudaram():
    """DoD 3 (interacao identica; ele resolve o simulado de 17/10 nesta tela): os ids que o JS consome, os botoes
    (data-*, tipo, rotulo), os campos e a ordem da questao, do fim e do leitor sao os de antes da part 4. Os atalhos
    do teclado seguem os mesmos (A-E, 1-5, S/D/C, Enter)."""
    assert _itens_de(TEMPLATE, "qz-player") == INVENTARIO_QUESTAO
    assert _itens_de(TEMPLATE, "hub-leitor") == INVENTARIO_LEITOR
    teclas = TEMPLATE[TEMPLATE.index('document.addEventListener("keydown"'):]
    teclas = teclas[:teclas.index("\n  });")]
    for trecho in ('"ABCDE".indexOf(k)', '"12345".indexOf(k)', '{S: "solida", D: "duvida", C: "chute"}[k]',
                   '$("qz-responder").click()', '$("qz-proxima").click()'):
        assert trecho in teclas, trecho


def test_hub_sprint_no_build_e_null_sem_sprint():
    assert hub.html_sprint([dict(l, dia_plano=None) for l in PLANO_SPRINT], HOJE_SPRINT) == \
        '<script type="application/json" id="hub-sprint">null</script>'
    d = hub.dados_sprint(PLANO_SPRINT, HOJE_SPRINT)
    assert d["proximos"] == [{"data": "2026-10-14", "tarefas": [30], "q": 30},
                             {"data": "2026-10-25", "tarefas": [1793], "q": 100}]
    assert d["fora"] == [{"id": 77, "motivo": "sem vaga até 31/10"}] and d["dias"]["1793"] == "2026-10-25"


# ------------------------------------------------ s211 part-3: modo Estudo/Prova + tela de fim com os elos

def test_simulado_e_sempre_prova_e_so_ele_tem_revisar_depois():
    """s229 (pedido dele, 15/10): simulado SEMPRE Prova e lista SEMPRE Estudo -- o doc da lista e o aparelho nao
    mudam isso; o "Revisar depois" (voltar antes de entregar) so aparece no simulado."""
    acao = """var sim = {area: "Simulado", modo: "estudo"}; qzModoUi(sim); var flag_sim = $("qz-marca").hidden;
qzModoUi({area: "Obstetrícia", modo: "prova"}); var flag_lista = $("qz-marca").hidden;
SAIDA = {sim: qzModoDaLista(sim), lista: qzModoDaLista({area: "Obstetrícia", modo: "prova"}), vazio: qzModoDaLista(null),
         flag_sim: flag_sim, flag_lista: flag_lista, com_flag: [qzComFlag(sim), qzComFlag({area: "Cirurgia"})]};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"sim": "prova", "lista": "estudo", "vazio": "estudo", "flag_sim": False, "flag_lista": True,
                   "com_flag": [True, False]}


def test_lista_nao_pergunta_o_modo_nem_grava_revisar_depois():
    """s229: sem o seletor (`#qz-modo-escolha` e `#qz-modo-lista` sairam do HTML e do JS); na lista, a resposta
    grava `flag: false` mesmo com o checkbox marcado (ninguem le no backend; so o simulado usa)."""
    corpo = TEMPLATE.split("<script", 1)[0]
    assert "qz-modo-escolha" not in corpo and "qz-modo-lista" not in TEMPLATE
    assert "Antes de ver o gabarito" not in TEMPLATE, "s229: a legenda da certeza saiu"
    assert "function qzEscolher(" not in TEMPLATE and "function qzEscolheModo(" not in TEMPLATE
    assert '<label class="qz-marca" id="qz-marca" hidden>' in corpo
    acao = """QZ.listas = [{_id: "t26", tarefa: 26, area: "Cirurgia"}, {_id: "s1", tarefa: 90, area: "Simulado"}];
QZ.letra = "C"; QZ.conf = "duvida"; QZ.t0 = Date.now(); $("qz-flag").checked = true;
QZ.lista = "t26"; QZ.modoLista = "estudo"; function qzRevelar(){} function qzDepoisDe(){} function qzParar(){}
qzResponder(); QZ.lista = "s1"; QZ.modoLista = "prova"; qzResponder();
SAIDA = {lista: GRAVADOS[0].flag, simulado: GRAVADOS[1].flag};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"lista": False, "simulado": True}


def test_estudo_revela_apos_responder_e_prova_nao():
    acao = """function qzParar(){} function qzRevelar(qq, rr){ SAIDA.revelou = rr.modo; } function qzDepoisDe(p){ SAIDA.depois = p; }
QZ.listas = [{_id: "t26", tarefa: 26}]; QZ.lista = "t26"; QZ.letra = "C"; QZ.conf = "duvida"; QZ.t0 = Date.now();
SAIDA.revelou = null; SAIDA.depois = null; QZ.modoLista = "estudo"; qzResponder(); SAIDA.estudo = {revelou: SAIDA.revelou, depois: SAIDA.depois, gravou: GRAVADOS[0].modo};
SAIDA.revelou = null; SAIDA.depois = null; QZ.modoLista = "prova"; qzResponder();
SAIDA.prova = {revelou: SAIDA.revelou, depois: SAIDA.depois, gravou: GRAVADOS[1].modo};
SAIDA.reabre = [qzRevelaAoAbrir({modo: "estudo"}), qzRevelaAoAbrir({modo: "prova"}), qzRevelaAoAbrir(null)];"""
    out = _rodar(_q(), None, None, acao)
    assert out["estudo"] == {"revelou": "estudo", "depois": None, "gravou": "estudo"}
    assert out["prova"] == {"revelou": None, "depois": 0, "gravou": "prova"}
    assert out["reabre"] == [True, False, False]        # respondida em Estudo reabre revelada mesmo em Prova


def test_pendencia_trava_proxima_e_concluir():
    acao = """QZ.modoLista = "estudo"; var r1 = {correta: false, confianca: "duvida"};
var a = [qzTrava(q, r1), $("qz-proxima").disabled, $("qz-status").textContent];
r1.elos = ["sim", "nao", "sim"]; var b = [qzTrava(q, r1), $("qz-proxima").disabled, $("qz-status").textContent];
QZ.modoLista = "prova"; var c = [qzTrava(q, {correta: false}), $("qz-proxima").disabled];
var fim = [2, 1, 0].map(function(n){ qzConcluirUi(n); return [$("qz-concluir").disabled, $("qz-fim-status").textContent]; });
SAIDA = {a: a, b: b, c: c, fim: fim};"""
    out = _rodar(_q(), None, None, acao)
    assert out["a"][:2] == [True, True] and out["a"][2].lower() == "declare os elos para seguir."
    assert out["b"] == [False, False, ""]
    assert out["c"] == [False, False]
    assert out["fim"] == [[True, "Faltam 2 declarações."], [True, "Falta 1 declaração."], [False, ""]]
    # Enter nao fura a trava: o atalho e o proprio botao conferem `disabled`
    assert 'if(!$("qz-proxima").disabled){ $("qz-proxima").click(); }' in TEMPLATE
    assert 'if($("qz-proxima").disabled){ return; }' in TEMPLATE
    assert '$("qz-concluir").disabled){ return; }' in TEMPLATE


def test_questao_sem_cadeia_nao_trava():
    """Sem cadeia (v1 em texto ou sem solução) nunca há pendência; "Erro na cadeia" conta como
    declaração (a trava não prende lista de cadeia defeituosa)."""
    acao = """QZ.modoLista = "estudo"; var errada = {correta: false, confianca: "chute"};
var defeito = {correta: false, confianca: "chute", cadeia_defeito: {motivo: "elo 2 repete o gabarito"}};
SAIDA = {v1: qzTrava({num: 1, solucao_medhub: "texto"}, errada), sem: qzTrava({num: 2}, errada), defeito: qzTrava(q, defeito),
  resumo: qzResumoElos([{num: 1, solucao_medhub: "texto"}, {num: 2}, q], {"1": errada, "2": errada, "8": defeito}).pendentes};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"v1": False, "sem": False, "defeito": False, "resumo": 0}


QS_FIM = [_q(num=8), _q(num=9), _q(num=10), _q(num=11), _q("texto v1", num=12)]
RESP_FIM = {"8": _resp("C", elos=["sim", "nao", "incerteza"], num=8), "9": _resp("A", "solida", num=9),
            "10": _resp("A", "duvida", elos=["desatencao", "sim", "sim"], num=10), "11": _resp("D", num=11),
            "12": _resp("B", num=12)}


def test_resumo_dos_elos_na_ordem_de_revisao():
    acao = "SAIDA = qzResumoElos(%s, %s);" % (json.dumps(QS_FIM), json.dumps(RESP_FIM))
    out = _rodar(_q(), None, None, acao)
    assert out["cont"] == {"sim": 6, "incerteza": 1, "desatencao": 1, "nao": 1}   # presumido conta como Sim
    assert [(x["num"], x["i"], x["estado"]) for x in out["itens"]] == [(8, 1, "nao"), (8, 2, "incerteza"),
                                                                      (10, 0, "desatencao")]
    assert out["pendentes"] == 1                                                      # Q11 sem declaração


def test_fim_elos_golden():
    acao = "SAIDA = {html: qzElosFimHtml(%s, %s), vazio: qzElosFimHtml([], {})};" % (
        json.dumps(QS_FIM), json.dumps(RESP_FIM))
    out = _rodar(_q(), None, None, acao)
    html = out["html"]
    assert out["vazio"] == ""
    assert re.findall(r'data-rev="(\d+)"', html) == ["0", "0", "2"]                  # tocável: abre a questão
    assert html.index("Q8</b><i>Não</i><span>Recordou") < html.index("Q8</b><i>Incerteza</i><span>Descartou") < html.index("Q10</b>")
    _golden("fim_elos", html)


def test_textos_da_aba_curtos_e_sem_o_elo_que_quebrou():
    """QZ_SUB e o parágrafo do fim: no máximo 2 frases cada, sem a promessa da análise que confirma
    o elo que quebrou (quem declara é o aluno)."""
    sub = _declaracao(TEMPLATE, "var QZ_SUB = {")
    textos = re.findall(r':\s*"([^"]+)"', sub)
    i = TEMPLATE.index('<div class="qz-elos-fim"')
    # s229 (adendo dele, 15/10: "sem micro-dica de interacao obvia"): o "Toque numa questao para ver..." do fim saiu
    assert '<p class="hub-sub" style="margin:0">' not in TEMPLATE[i:TEMPLATE.index('id="qz-revisao"', i)]
    assert len(textos) == 2
    for t in textos:
        assert len(re.findall(r"[.!?](?:\s|$)", t)) <= 2, t
    assert "confirma o elo que quebrou" not in TEMPLATE


# ------------------------------------------------ s211 part-4: marca-texto no enunciado e nas alternativas

def test_grifo_mescla_sobrepostos_e_adjacentes():
    acao = """SAIDA = {sobrepostos: qzGrifoMesclar([[5, 10], [0, 3]], [2, 6]), adjacentes: qzGrifoMesclar([[0, 3]], [3, 5]),
  separados: qzGrifoMesclar([[8, 9]], [0, 2]), sem_novo: qzGrifoMesclar([[4, 6], [1, 2]], null), vazio: qzGrifoMesclar(null, [1, 3])};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"sobrepostos": [[0, 10]], "adjacentes": [[0, 5]], "separados": [[0, 2], [8, 9]],
                   "sem_novo": [[1, 2], [4, 6]], "vazio": [[1, 3]]}


def test_grifo_html_escapa_e_ignora_intervalo_invalido():
    acao = """SAIDA = {h: qzGrifoHtml("a<b & c\\nfim", [[0, 3], [5, 99], [-1, 2], [4, 4], ["x", 2], [2, 2.5], [1, 3]]),
  nada: qzGrifoHtml("x > y", null), lixo: qzGrifoHtml("abc", "nao e lista")};"""
    out = _rodar(_q(), None, None, acao)
    assert out["h"] == '<mark class="qz-grifo" data-i="0">a&lt;b</mark> &amp; c\nfim'
    assert out["nada"] == "x &gt; y" and out["lixo"] == "abc"


def test_grifo_remover_intervalo():
    acao = """var g = [[0, 3], [5, 9]];
SAIDA = {meio: qzGrifoRemover(g, 6), inicio: qzGrifoRemover(g, 0), fim_exclusivo: qzGrifoRemover(g, 3), fora: qzGrifoRemover(g, 20)};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"meio": [[0, 3]], "inicio": [[5, 9]], "fim_exclusivo": [[0, 3], [5, 9]],
                   "fora": [[0, 3], [5, 9]]}


def test_alternativa_tem_role_radio_e_nao_e_button():
    """O corpo da alternativa deixou de ser <button> (texto selecionavel); `role="radio"` + `tabindex`
    antes de revelar, o X de riscar segue botao; teclado: Enter/Espaco na alternativa e A-E/1-5."""
    out = _rodar(_q(), None, None, 'SAIDA = {h: qzAltsHtml(q, null, false, {A: [[0, 2]], C: [[100, 200]]})};')
    h = out["h"]
    assert '<button type="button" class="qz-alt-btn"' not in h
    assert h.count('role="radio" tabindex="0" aria-checked="false"') == 4
    assert h.count('<button type="button" class="qz-risca"') == 4
    assert '<span class="qz-alt-txt"><mark class="qz-grifo" data-i="0">DM</mark> prévio; tratar já</span>' in h
    _golden("alternativa", h)
    assert 'e.target.classList.contains("qz-alt-btn") && (e.key === "Enter" || e.key === " ")' in TEMPLATE
    assert "querySelector('.qz-alt[data-l=\"' + k + '\"] .qz-alt-btn')" in TEMPLATE
    assert 'querySelectorAll(".qz-alt-btn")[parseInt(k, 10) - 1]' in TEMPLATE


def test_grifos_viajam_no_doc_da_resposta_e_voltam_na_revisao():
    acao = """function qzParar(){} function qzRevelar(){} function qzDepoisDe(){}
QZ.listas = [{_id: "t26", tarefa: 26}]; QZ.letra = "C"; QZ.conf = "duvida"; QZ.t0 = Date.now(); QZ.modoLista = "prova";
qzGrifosSalvar(q, {enun: [[0, 8]]});                       // antes de responder: so rascunho local
var antes = {gravados: GRAVADOS.length, rascunho: LS["medhub.grifos.t26"]};
qzResponder();                                             // ao responder: entram no doc
var g = qzGrifosDe(q); g.A = [[0, 2]]; qzGrifosSalvar(q, g);   // depois: cada mudanca regrava
var docs = GRAVADOS.map(function(d){ return d.grifos; });
QZ.grifos = {}; LS = {}; QZ.resp = {}; QZ.resp[q.num] = JSON.parse(JSON.stringify(GRAVADOS[GRAVADOS.length - 1]));   // outra sessao, so o db
var volta = qzGrifosDe(q);
SAIDA = {antes: antes, docs: docs, volta: volta, alts: qzAltsHtml(q, QZ.resp[q.num], true, volta), enun: qzGrifoHtml("Gestante de 7 semanas", volta.enun)};"""
    out = _rodar(_q(), None, None, acao)
    assert out["antes"] == {"gravados": 0, "rascunho": {"8": {"enun": [[0, 8]]}}}
    assert out["docs"] == [{"enun": [[0, 8]]}, {"enun": [[0, 8]], "A": [[0, 2]]}]
    assert out["volta"] == {"enun": [[0, 8]], "A": [[0, 2]]}
    assert '<mark class="qz-grifo" data-i="0">DM</mark>' in out["alts"]
    assert out["enun"] == '<mark class="qz-grifo" data-i="0">Gestante</mark> de 7 semanas'


def test_grifo_uma_cor_de_token_e_limite_declarado():
    """Uma cor ATIVA por vez, por token (`--qz-grifo`; s227, part 6: rosa, ciano ou amarelo, escolhida no topo do hub,
    nunca por grifo); pinta so o fundo, o texto fica com a cor dele (`color:inherit`); sem barra flutuante nem menu
    na questao; o limite (selecao por toque no celular nao testada) declarado no template e no brief."""
    (regra,) = [l for l in TEMPLATE.splitlines() if l.startswith(".qz-grifo{")]
    assert "background:var(--grifo-rosa)" in regra and "color:inherit" in regra and "#" not in regra
    assert "--qz-grifo-tinta" not in regra, "o grifo nao troca a cor do texto (pedido dele, s227)"
    assert TEMPLATE.count('class="qz-grifo"') == 1                        # um so tipo de grifo
    # s229: o seletor das Listas e o MESMO botao unico da Teoria (`.hub-grifo`, id `qz-grifo`); nada de menu proprio
    for proibido in ("qz-grifo-menu", "qz-grifo-barra"):
        assert proibido not in TEMPLATE
    assert '.qz-grifo[data-cor="ciano"]{background:var(--grifo-ciano)}' in TEMPLATE
    assert "NAO e verificado por teste" in TEMPLATE and "TOQUE no navegador do celular" in TEMPLATE
    assert "`grifos`" in BRIEF and "Não verificado por teste: a seleção por toque no navegador do celular" in BRIEF


# ======================================================================== s214: secoes recolhiveis e grifo
# Pedidos do operador em 04/10/2026:
# 1. "Seria bacana poder recolher as semanas, deixando apenas a que eu quisesse (ate os proprios blocos,
#    como revisoes direcionadas, etc.)". O titulo de cada secao vira o controle (role=button, Enter/Espaco,
#    aria-expanded); a escolha fica POR APARELHO em `localStorage["medhub.secoes"]`; sem escolha salva,
#    abertas = revisoes, atrasadas e a semana da vez (a 1a >= atual com itens), recolhidas = as semanas
#    seguintes e "Outras aulas". Nas Listas o HTML e refeito a cada snapshot: o estado sobrevive ao
#    re-render (delegacao + estado lido na renderizacao).
# 2. "os blocos das aulas tambem poderiam ter o mecanismo de selecionar e destacar". Ancora = BLOCO +
#    offset + trecho; re-ancora pelo trecho; mescla por bloco; o aparelho guarda ANTES do banco
#    (`analises/grifos/itens/<slug>`) e reenvia quando o banco volta.
# As funcoes REAIS do template rodam em node: as secoes da aba Aulas sobre o quadro REAL de
# `hub.html_quadro_de`, no DOM falso e com o banco falso de `test_hub_quadro` (junto do `iniciarQuadro`
# real, para o recontar e o movimento para Concluidas); as Listas pelo `qzRenderListas` real; o grifo
# pelas funcoes PURAS e pela gravacao com banco e aparelho falsos. O que o DOM falso nao tem (Range,
# selecao, CSS, nos de texto: `grifoBlocos`, `grifoPintar`, `grifoCapturar`) foi conferido em navegador
# real (Edge headless a 390 px). LIMITE DECLARADO: a selecao por TOQUE so o aparelho prova.

URL_SEC = "https://med.estrategia.com/cadernos/x/?per_page=20"


def _tarefa(id_, semana, tema, q=0, url=None, fonte="rf", status="pendente", bloco="GO", area=None):
    """A linha de `plano_tarefas` que o quadro le (a forma do `_t` de test_hub_quadro)."""
    return {"id": id_, "semana_plano": semana, "tema": tema, "q_previstas": float(q),
            "url_lista": url, "fonte": fonte, "status": status, "bloco": bloco, "ordem": id_,
            "area": area}


HOJE_SEC = date(2026, 10, 4)
CAL_SEC = {1: (date(2026, 9, 14), date(2026, 9, 20)), 2: (date(2026, 9, 21), date(2026, 9, 27)),
           3: (date(2026, 9, 28), date(2026, 10, 4)), 4: (date(2026, 10, 5), date(2026, 10, 11)),
           5: (date(2026, 10, 12), date(2026, 10, 18))}


def _var(nome):
    return re.search(r"\n  (var %s = [^\n]+;)" % nome, TEMPLATE).group(1)


def _funcs(*assinaturas):
    return "\n".join(extrair_funcao(TEMPLATE, a) for a in assinaturas)


def _node(prog):
    if not NODE:
        pytest.skip("node ausente no PATH: secoes/grifo do hub nao verificados (skip declarado)")
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


#: aparelho falso: `quebrado` simula storage bloqueado (aba privada, previa) -- todo acesso lanca
APARELHO = r"""
var LS = __LS__, LS_QUEBRADO = __QUEBRADO__;
function lsChecar(){ if(LS_QUEBRADO){ throw new Error("storage bloqueado"); } }
var localStorage = {getItem: function(k){ lsChecar(); return Object.prototype.hasOwnProperty.call(LS, k) ? LS[k] : null; },
  setItem: function(k, v){ lsChecar(); LS[k] = String(v); }, removeItem: function(k){ lsChecar(); delete LS[k]; },
  key: function(i){ lsChecar(); return Object.keys(LS)[i] || null; }};
Object.defineProperty(localStorage, "length", {get: function(){ lsChecar(); return Object.keys(LS).length; }});
"""


def _aparelho(ls=None, quebrado=False):
    return (APARELHO.replace("__LS__", json.dumps(ls or {}, ensure_ascii=False))
            .replace("__QUEBRADO__", "true" if quebrado else "false"))


# ======================================================================== 1. secoes da aba Aulas

# hoje = semana 3; a semana 1 e Atrasadas; 4 e 5 vem depois. Uma RD avulsa (bloco proprio), uma
# aula avulsa sem tarefa ("Outras aulas") e uma aula que CUMPRE a tarefa 70 da semana 4 (tem o
# "feito"). s216 (part-1): lista so mora na Teoria com aula ligada -- `prep-x` prepara as 4 listas,
# para as secoes seguirem as mesmas; a analise saiu da Teoria (vive na Documentacao do Painel).
PLANO_SEC = [_tarefa(26, 1, "Diabetes na Gestação", 19, URL_SEC),
             _tarefa(49, 3, "Hérnias da Parede Abdominal", 21, URL_SEC, bloco="CIR"),
             _tarefa(70, 4, "Aorta e pericárdio", 0, None, fonte="custom", bloco="CM"),
             _tarefa(68, 4, "Doenças Glomerulares", 21, URL_SEC, bloco="CM"),
             _tarefa(71, 5, "Tireoide", 18, URL_SEC, bloco="CM")]
AULAS_SEC = [hub.Aula(s, s, "2026-10-0%d" % (i + 1), "artifacts/aula-%s.html" % s)
             for i, s in enumerate(("rd-hepato", "avulsa-x", "aorta", "prep-x"))]
REGISTRO_SEC = {"rd-hepato": {"tipo": "revisao", "titulo": "Revisão direcionada hepato", "bloco": "CM"},
                "avulsa-x": {"tipo": "aula", "titulo": "Aula avulsa", "bloco": "GO"},
                "aorta": {"tipo": "aula", "titulo": "A aorta", "tarefa_id": 70},
                "prep-x": {"tipo": "aula", "titulo": "Aula que prepara", "tarefas": [26, 49, 68, 71]}}


def _pagina_quadro(plano=PLANO_SEC):
    return (hub.html_semanas(plano, CAL_SEC, HOJE_SEC) +
            hub.html_quadro_de(AULAS_SEC, REGISTRO_SEC, {}, plano, CAL_SEC, HOJE_SEC)[0])


SECOES_JS = "\n".join([_var("SECOES_CHAVE"), _funcs(
    "function secoesLer(){", "function secAberta(id, padrao){", "function secGuardar(id, aberta){",
    "function secSemanaAtual(atual, comItens){", "function secPadraoAberta(chave, corrente){",
    "function secPintar(sec, aberta){", "function secAlternar(sec, id){", "function secTecla(ev, acao){",
    "function hubSemanas(){", "function secLigar(sec, id, alvo, padrao){", "function areaLigar(g){",
    "function secoesQuadro(raizQd){")])

ACAO_SECOES = r"""
function espera(){ return new Promise(function(ok){ setTimeout(ok, 0); }); }
var qd = $("hub-quadro"), TECLAS = 0, AVISOS = [];
console.warn = function(m){ AVISOS.push(String(m)); };
function feitoEm(slug){ return qd.querySelector('.qd-item[data-slug="' + slug + '"]').hasAttribute("data-feito"); }
function titulo(chave){ return qd.querySelector('.qd-sem[data-secao="' + chave + '"] .qd-titulo'); }
function tocar(chave){ titulo(chave).click(); }
function tecla(chave, k){ (titulo(chave)._ouv.keydown || []).forEach(function(f){ f({key: k, preventDefault: function(){ TECLAS++; }}); }); }
// P20 (s219): sem o quadrado, o "feito" chega pelos caminhos REAIS -- marcar = a assinatura da leitura
// (`quadroMarcarFeito`, grava `quadro/<slug>`); desmarcar = o doc do db muda (so o agente o faz) e o
// onSnapshot real do quadro aplica, na hora
function feito(slug){
  var li = qd.querySelector('.qd-item[data-slug="' + slug + '"]');
  if(!li.hasAttribute("data-feito")){ quadroMarcarFeito(slug); return; }
  BANCO.quadro[slug] = {feito: false, ts: "t"}; (OUV.quadro || []).forEach(function(f){ f(foto("quadro")); });
}
function secoes(){ var o = {};
  qd.querySelectorAll(".qd-sem").forEach(function(s){ var t = s.querySelector(".qd-titulo"), l = s.querySelector(".qd-lista");
    o[s.getAttribute("data-secao")] = {aberta: !s.hasAttribute("data-recolhida"), expanded: t.getAttribute("aria-expanded"),
      role: t.getAttribute("role"), tab: t.getAttribute("tabindex"), controls: t.getAttribute("aria-controls"),
      lista: l ? l.getAttribute("id") : null, seta: !!t.querySelector(".qd-seta"), oculta: s.hidden,
      n: s.querySelector("[data-n]").textContent, vazio_oculto: s.querySelector(".qd-vazio").hidden}; });
  return o; }
function onde(slug){ var li = qd.querySelector('.qd-item[data-slug="' + slug + '"]'), p = li.parentNode;
  while(p){ if(p.getAttribute("id") === "hub-quadro-feitas"){ return "feitas"; } if(p.tagName === "SECTION"){ return p.getAttribute("data-secao"); } p = p.parentNode; }
  return null; }
iniciarQuadro();
secoesQuadro(qd);
var SAIDA = {inicio: secoes()};
espera().then(function(){ __ACAO__ return espera(); }).then(espera).then(function(){
  SAIDA.fim = secoes(); SAIDA.ls = LS; SAIDA.teclas = TECLAS; SAIDA.avisos = AVISOS;
  SAIDA.areas_abertas = qd.querySelectorAll(".qd-area").map(function(g){ return !!g.open; });
  console.log(JSON.stringify(SAIDA)); });
"""


def _rodar_secoes(acao="", ls=None, quebrado=False, plano=PLANO_SEC, cfg=None, extra=""):
    # tardio: test_hub_quadro importa deste arquivo (NODE, extrair_funcao) -- no topo seria import circular
    from tools.test_hub_quadro import BANCO_QD, DOM_QD, FUNCS_QD, _arvore
    prog = (DOM_QD.replace("__ARVORE__", json.dumps(_arvore(_pagina_quadro(plano)), ensure_ascii=False)) +
            BANCO_QD.replace("__CFG__", json.dumps(cfg or {}, ensure_ascii=False)) + _aparelho(ls, quebrado) +
            FUNCS_QD + "\n" + SECOES_JS + "\n" + extra + "\n" + ACAO_SECOES.replace("__ACAO__", acao))
    return _node(prog)


def _abertas(estado):
    return {k: v["aberta"] for k, v in estado.items() if not v["oculta"]}


def test_padrao_abre_o_backlog_de_rds():
    """s226 (sprint-final-uerj part-4): a Teoria nao tem semana; a unica secao e o backlog "Revisoes
    direcionadas", aberto de partida e recolhivel como as outras (titulo = controle)."""
    out = _rodar_secoes()
    assert _abertas(out["inicio"]) == {"rd": True}
    for chave, s in out["inicio"].items():
        assert (s["role"], s["tab"], s["seta"]) == ("button", "0", True), chave
        assert s["expanded"] == ("true" if s["aberta"] else "false"), chave
        assert s["controls"] == s["lista"] == "qd-lista-" + chave, "aria-controls aponta a lista da secao"
    assert out["ls"] == {}, "sem toque, nada gravado no aparelho"


def test_semana_da_vez_e_padrao_puros_seguem_para_as_listas_sem_sprint():
    """As puras da semana da vez seguem (a aba Listas sem sprint ainda agrupa por semana)."""
    puras = _node(SECOES_JS + "\nconsole.log(JSON.stringify({a: secSemanaAtual(3, [5, 4]), b: secSemanaAtual(3, []),"
                  " c: secSemanaAtual(0, [6, 2]), d: [\"revisoes\", \"atrasadas\", \"biblioteca\", \"sem\", \"4\", \"s4\", \"5\", \"s5\", \"rd\"]"
                  ".map(function(k){ return secPadraoAberta(k, 4); })}));")
    assert puras == {"a": 4, "b": 3, "c": 2, "d": [True, True, False, True, True, True, False, False, True]}


def test_toque_e_teclado_alternam_e_o_aparelho_lembra():
    out = _rodar_secoes('tocar("rd"); tecla("rd", "Enter"); tecla("rd", " "); tecla("rd", "a");')
    assert _abertas(out["fim"]) == {"rd": False} and out["fim"]["rd"]["expanded"] == "false"
    assert out["teclas"] == 2, "Enter e Espaco viram toque (preventDefault: a pagina nao rola); 'a' nao"
    assert json.loads(out["ls"]["medhub.secoes"]) == {"aulas:rd": False}
    # recarregar: o mesmo aparelho, uma pagina nova -- vale o que ele escolheu
    assert _abertas(_rodar_secoes(ls=out["ls"])["inicio"]) == {"rd": False}


def test_sem_storage_tudo_funciona_e_so_nao_lembra():
    out = _rodar_secoes('tocar("rd");', quebrado=True)
    assert _abertas(out["fim"]) == {"rd": False}
    assert _abertas(_rodar_secoes(quebrado=True)["inicio"]) == {"rd": True}


# ⚰️ s226 (sprint-final-uerj part-4): `test_recontar_e_biblioteca_nao_desfazem_a_secao_recolhida` -- a
# aula que cumpre a tarefa mora na Biblioteca desde o build (sem semana de origem); o recontar do backlog
# esta em `test_rd_assinada_some_do_backlog_e_perde_a_etiqueta_na_biblioteca`.



def test_aula_avulsa_mora_na_biblioteca_recolhida():
    """s216 (part-3): "Outras aulas" e "Concluidas" viraram UMA secao, a Biblioteca (o mesmo
    `<details id="hub-quadro-feitas">`, recolhida): a aula sem tarefa pendente mora la desde o build e,
    marcada como feita, fica la riscada -- nao existe mais secao "outras"."""
    out = _rodar_secoes('SAIDA.antes = {onde: onde("avulsa-x"), feito: feitoEm("avulsa-x"), n: $("hub-quadro-nfeitas").textContent};'
                        ' feito("avulsa-x"); SAIDA.meio = {onde: onde("avulsa-x"), feito: feitoEm("avulsa-x"),'
                        ' n: $("hub-quadro-nfeitas").textContent};')
    # s218: a Biblioteca guarda tambem a RD (rd-hepato): 2 documentos
    # s226 (part-4): sem semanas, a aorta e a prep-x tambem moram na Biblioteca: 4 documentos
    assert out["antes"] == {"onde": "feitas", "feito": False, "n": "4"}
    assert out["meio"] == {"onde": "feitas", "feito": True, "n": "4"}, "feita, fica na Biblioteca, riscada"
    assert "outras" not in out["inicio"] and "outras" not in out["fim"]
    assert _rodar_secoes()["areas_abertas"] == [False, False], "s218: as grandes areas nascem recolhidas"


def test_desmarcar_sem_secao_de_origem_fica_na_biblioteca():
    """s216 (part-3, A7): desmarcar devolve o item a secao de origem gravada no `data-secao` DELE. s218: o
    que MORA na Biblioteca (`data-secao="biblioteca"`: a aula avulsa, a RD) fica na sua disciplina, sem
    riscar e sem aviso -- e o lugar dele, nao uma secao que sumiu."""
    out = _rodar_secoes('feito("avulsa-x"); return espera().then(function(){ feito("avulsa-x");'
                        ' SAIDA.depois = {onde: onde("avulsa-x"), feito: feitoEm("avulsa-x")}; });')
    assert out["depois"] == {"onde": "feitas", "feito": False}
    assert out["avisos"] == []
    volta = _rodar_secoes('feito("aorta"); return espera().then(function(){ feito("aorta"); });')
    assert volta["avisos"] == [], "com origem (a semana 4), volta sem aviso"


# s217 (P17, pedido do operador em 06/10/2026: "organize por grande area (CM, Cir, MFC, Ped ou GO)"): a
# Biblioteca em grupos por area. O cliente move o feito para o grupo do `data-area` do item, CRIA o grupo
# que ainda nao existe na posicao da ordem (a ordem e os rotulos vem do build, em `data-areas`), reconta
# o grupo e o total e tira o grupo que esvazia. Cada grupo recolhe como as secoes (titulo = controle,
# teclado, estado por aparelho em medhub.secoes); padrao: recolhido.
GRUPOS_JS = r"""
function grupos(){ return qd.querySelectorAll("#hub-quadro-feitas .qd-area").map(function(g){ var nv = g.querySelector("[data-novas]");
  return {area: g.getAttribute("data-area"), n: g.querySelector("[data-n]").textContent, novas: nv && !nv.hidden ? nv.textContent : "",
    discs: g.querySelectorAll(".qd-disc").map(function(d){ return [d.getAttribute("data-disc"), d.querySelector("[data-n]").textContent,
      d.querySelectorAll(".qd-item").map(function(li){ return (li.querySelector(".qd-nova") ? "*" : "") + (li.getAttribute("data-slug") || "t" + li.getAttribute("data-tarefa")); })]; }),
    aberta: !!g.open, tag: g.tagName, sumario: !!g.querySelector("summary")}; }); }
function tituloGrupo(a){ return qd.querySelector('#hub-quadro-feitas .qd-area[data-area="' + a + '"] summary'); }
function nfeitas(){ return $("hub-quadro-nfeitas").textContent; }
function novas(){ var e = $("hub-quadro-novas"); return e.hidden ? "" : e.textContent; }
"""


def test_rd_assinada_some_do_backlog_e_perde_a_etiqueta_na_biblioteca():
    """s226 (sprint-final-uerj part-4): a Teoria nao tem semana -- nada viaja de uma secao para a
    Biblioteca. A RD assinada (a assinatura grava `quadro/<slug>`) SOME do backlog do topo, que reconta e
    diz "Nenhuma..."; a copia da Biblioteca fica no lugar e perde "nova". Desfeita no db, volta aos dois."""
    acao = GRUPOS_JS + r"""
SAIDA.g0 = grupos(); SAIDA.v0 = novas();
feito("rd-hepato"); SAIDA.s1 = secoes()["rd"]; SAIDA.g1 = grupos(); SAIDA.v1 = novas();
SAIDA.oculta1 = qd.querySelector('.qd-sem[data-secao="rd"] .qd-item').hidden;
return espera().then(function(){ feito("rd-hepato"); SAIDA.s2 = secoes()["rd"]; SAIDA.v2 = novas();
  SAIDA.oculta2 = qd.querySelector('.qd-sem[data-secao="rd"] .qd-item').hidden; });"""
    out = _rodar_secoes(acao)
    assert out["inicio"]["rd"]["n"] == "1" and out["inicio"]["rd"]["vazio_oculto"] is True
    assert out["v0"] == "1 nova" and "*rd-hepato" in out["g0"][0]["discs"][-1][2]
    assert out["s1"]["n"] == "0" and out["s1"]["vazio_oculto"] is False and out["oculta1"] is True
    assert out["v1"] == "" and "rd-hepato" in out["g1"][0]["discs"][-1][2], "lida, fica na Biblioteca"
    assert out["s2"]["n"] == "1" and out["oculta2"] is False and out["v2"] == "1 nova", "desfeita, volta"
    assert out["avisos"] == []


# ⚰️ s226 (sprint-final-uerj part-4): `test_feito_cai_na_disciplina_e_a_rd_nova_perde_a_etiqueta_no_lugar` e
# `test_grande_area_que_nao_existia_nasce_na_ordem` -- sem semanas na Teoria, nenhum item viaja de uma
# secao para a Biblioteca (o grupo que nasce ao vivo so servia a esse movimento); a etiqueta "nova" da RD
# lida segue presa acima.


def test_grupo_da_biblioteca_recolhe_e_o_aparelho_lembra():
    """s218: a grande area e um <details> (o pedido); o TOQUE no summary grava a escolha no aparelho (o
    clique chega antes da troca, entao grava o contrario do estado atual); recarregar abre como ele deixou."""
    acao = GRUPOS_JS + r"""
tituloGrupo("GO").click(); SAIDA.ls1 = JSON.parse(LS["medhub.secoes"] || "{}");"""
    out = _rodar_secoes(acao)
    assert out["ls1"] == {"aulas:biblioteca:GO": True}
    de_novo = _rodar_secoes(GRUPOS_JS + "SAIDA.g = grupos();", ls=out["ls"])
    assert [(g["area"], g["aberta"]) for g in de_novo["g"]] == [("CM", False), ("GO", True)], \
        "recarregar: vale a escolha dele; a que ele nao tocou nasce recolhida"
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    assert "min-width:0" in re.search(r"\.qd-area\{([^}]*)\}", css).group(1)
    assert re.search(r"\.qd-areas\{[^}]*display:grid", css)


def test_voltar_ao_item_concluido_abre_a_biblioteca_e_o_grupo_dele():
    """Part-4 (P14): ao voltar do leitor, o item concluido e marcado na Teoria e a Biblioteca abre; com
    os grupos (s217), o grupo dele abre tambem -- sem gravar no aparelho (nao foi escolha dele)."""
    acao = GRUPOS_JS + r"""
El.prototype.contains = function(n){ for(var p = n; p; p = p.parentNode){ if(p === this){ return true; } } return false; };
feito("rd-hepato"); var li = marcarRecente("aulas", "rd-hepato");
SAIDA.recente = {slug: li.getAttribute("data-slug"), marca: li.classList.contains("qd-recente"), grupo: grupos()[0]};"""
    extra = _funcs("function qdGrupoDe(li){", "function marcarRecente(aba, slug){")
    out = _rodar_secoes(acao, extra=extra)
    assert out["recente"]["slug"] == "rd-hepato" and out["recente"]["marca"] is True
    assert out["recente"]["grupo"]["area"] == "CM" and out["recente"]["grupo"]["aberta"] is True
    assert "aulas:biblioteca:CM" not in json.loads(out["ls"].get("medhub.secoes", "{}")), "abrir por codigo nao grava"


# ======================================================================== 2. secoes da aba Listas

LISTAS_SEC = [
    {"_id": "t26", "tema": "Diabetes na Gestação", "area": "Obstetrícia", "semana": 1, "seq": 1, "q": 19, "status": "capturada"},
    {"_id": "t49", "tema": "Hérnias", "area": "Cirurgia", "semana": 3, "seq": 2, "q": 21, "status": "capturada"},
    {"_id": "t90", "tema": "Já resolvida", "area": "Cirurgia", "semana": 3, "seq": 3, "q": 10, "status": "resolvida"},
    {"_id": "t68", "tema": "Glomerulares", "area": "Nefrologia", "semana": 4, "seq": 4, "q": 21, "status": "capturada"},
    {"_id": "t71", "tema": "Tireoide", "area": "Endocrinologia", "semana": 5, "seq": 5, "q": 18, "status": "capturada"},
    {"_id": "t80", "tema": "Reserva", "area": "Clínica", "seq": 6, "q": 12, "status": "capturada"},
]

LISTAS_FUNCS = LISTAS_JS + "\n" + _funcs(
    "function secGuardar(id, aberta){", "function secPintar(sec, aberta){", "function secAlternar(sec, id){",
    "function secTecla(ev, acao){", "function qzListasClique(e){", "function qzListasTecla(e){")

HARNESS_LISTAS_SEC = r"""
var els = {}, ABRIU = [];
function botao(m){ var b = {m: m, innerHTML: "", attrs: {}};
  b.getAttribute = function(k){ return k === "data-m" ? b.m : b.attrs[k]; }; b.setAttribute = function(k, v){ b.attrs[k] = v; };
  b.classList = {toggle: function(){}}; return b; }
var BOT = [botao("questoes"), botao("simulados")];
function $(id){ if(!els[id]){ els[id] = {id: id, innerHTML: "", textContent: "", hidden: false,
  querySelectorAll: function(){ return id === "qz-modo" ? BOT : []; }}; } return els[id]; }
function qzAbrir(id){ ABRIU.push(id); }
var ABRIU_AULA = []; function abrirNaTeoria(href, titulo){ ABRIU_AULA.push([href, titulo]); }
var QZ = {listas: __LISTAS__, modo: "questoes"};
var QZ_SEM = {atual: __ATUAL__, datas: {}};
var QZ_SPRINT = null;   // s226 (part-4): sem sprint, as semanas de sempre
__FUNCS__
// a secao renderizada, como o navegador a teria: atributos + o titulo dentro dela
function secaoDe(chave){
  var sec = {attrs: {}, hasAttribute: function(k){ return k in this.attrs; }, setAttribute: function(k, v){ this.attrs[k] = v; },
    removeAttribute: function(k){ delete this.attrs[k]; }, querySelector: function(){ return tit; }};
  var tit = {attrs: {"data-sec": "listas:" + chave}, parentNode: sec, getAttribute: function(k){ return this.attrs[k]; },
    setAttribute: function(k, v){ this.attrs[k] = v; }, closest: function(s){ return s === "[data-sec]" ? tit : null; }};
  var m = new RegExp('<section( data-recolhida)?><h3[^>]*data-sec="listas:' + chave + '"').exec($("qz-listas").innerHTML);
  if(m && m[1]){ sec.attrs["data-recolhida"] = ""; }
  return {sec: sec, tit: tit};
}
function evento(alvo, extra){ var e = {target: {closest: function(s){ return alvo(s); }}, key: extra, prevenido: false,
  preventDefault: function(){ e.prevenido = true; }}; return e; }
function estado(){ var o = {}, re = /<section( data-recolhida)?><h3 class="qd-titulo" role="button" tabindex="0" data-sec="listas:([^"]+)" aria-controls="([^"]+)" aria-expanded="(true|false)">/g, m;
  while((m = re.exec($("qz-listas").innerHTML))){ o[m[2]] = {aberta: !m[1], expanded: m[4], controls: m[3]}; } return o; }
var SAIDA = {};
qzRenderListas(); SAIDA.inicio = estado();
__ACAO__
console.log(JSON.stringify(SAIDA));
"""


def _rodar_listas(acao="", atual=3, ls=None, quebrado=False, listas=LISTAS_SEC):
    prog = (_aparelho(ls, quebrado) + HARNESS_LISTAS_SEC.replace("__FUNCS__", LISTAS_FUNCS)
            .replace("__LISTAS__", json.dumps(listas, ensure_ascii=False)).replace("__ATUAL__", str(atual))
            .replace("__ACAO__", acao))
    return _node(prog)


def test_listas_nascem_no_padrao_com_titulo_controle():
    out = _rodar_listas()
    assert {k: v["aberta"] for k, v in out["inicio"].items()} == {
        "atrasadas": True, "s3": True, "s4": False, "s5": False, "sem": True}
    assert all(v["expanded"] == ("true" if v["aberta"] else "false") for v in out["inicio"].values())
    assert all(v["controls"] == "qz-sec-" + k for k, v in out["inicio"].items())
    so_futuras = _rodar_listas(listas=[l for l in LISTAS_SEC if l.get("semana") in (4, 5)])
    assert {k: v["aberta"] for k, v in so_futuras["inicio"].items()} == {"s4": True, "s5": False}, \
        "semana atual sem lista: a 4 e a da vez"


@pytest.mark.parametrize("quebrado", [False, True], ids=["com-storage", "sem-storage"])
def test_listas_recolhem_e_sobrevivem_ao_rerender(quebrado):
    """O toque chega pela delegacao no conteiner; o snapshot seguinte refaz o HTML e o estado fica.
    Sem storage, a escolha vive na memoria da pagina: sobrevive ao re-render (so nao ao recarregar)."""
    acao = r"""
var s4 = secaoDe("s4"), s3 = secaoDe("s3");
qzListasClique(evento(function(s){ return s === "[data-sec]" ? s4.tit : null; }));
var tec = evento(function(s){ return s === "[data-sec]" ? s3.tit : null; }, " "); qzListasTecla(tec);
SAIDA.na_hora = {s4: !("data-recolhida" in s4.sec.attrs), s3: !("data-recolhida" in s3.sec.attrs), prevenido: tec.prevenido};
QZ.listas[0].status = "resolvida"; QZ.listas.push({_id: "t72", tema: "Nova", area: "CM", semana: 4, seq: 7, q: 5, status: "capturada"});
qzRenderListas(); SAIDA.depois = estado();
qzListasClique(evento(function(s){ return s === "button[data-qzl]" ? {getAttribute: function(){ return "t68"; }} : null; }));
SAIDA.abriu = ABRIU; SAIDA.ls = LS;"""
    out = _rodar_listas(acao, quebrado=quebrado)
    assert out["na_hora"] == {"s4": True, "s3": False, "prevenido": True}
    depois = {k: v["aberta"] for k, v in out["depois"].items()}
    assert depois == {"s3": False, "s4": True, "s5": False, "sem": True}, "a atrasada resolveu: o grupo saiu"
    assert out["abriu"] == ["t68"], "tocar na lista continua abrindo a lista"
    if quebrado:
        assert out["ls"] == {}
    else:
        assert json.loads(out["ls"]["medhub.secoes"]) == {"listas:s4": True, "listas:s3": False}


def test_listas_e_aulas_tem_chaves_proprias_no_aparelho():
    """'aulas:4' e 'listas:s4' sao escolhas diferentes: recolher a semana 4 numa aba nao mexe na outra."""
    out = _rodar_listas(ls={"medhub.secoes": json.dumps({"aulas:4": True, "aulas:3": False})})
    assert out["inicio"]["s4"]["aberta"] is False and out["inicio"]["s3"]["aberta"] is True


def test_secao_recolhivel_no_celular():
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    regra = re.search(r"\.qd-titulo\[data-sec\]\{([^}]*)\}", css).group(1)
    assert "min-height:44px" in regra and "cursor:pointer" in regra
    assert re.search(r"\[data-recolhida\] > \.qd-lista,\[data-recolhida\] > \.qz-lista,\[data-recolhida\] > \.qd-vazio\{display:none\}", css)
    assert "prefers-reduced-motion: reduce){.qd-seta{transition:none}}" in css
    assert not re.search(r"position\s*:\s*(sticky|fixed)", TEMPLATE) and "nowrap" not in TEMPLATE.lower()
    assert "try{ secoesQuadro(qd); }catch(e){}" in TEMPLATE, "falha nas secoes nunca derruba o quadro"
    # s218: a Biblioteca e o corpo da aba (uma <section>); cada grande area, um <details>
    quadro = hub.html_quadro_de(AULAS_SEC, REGISTRO_SEC, {}, PLANO_SEC, CAL_SEC, HOJE_SEC)[0]
    assert '<section class="qd-bib" id="hub-quadro-feitas"' in quadro and '<details class="qd-area" data-area="CM">' in quadro
    assert re.search(r"\[data-recolhida\] > \.qd-qsem,\[data-recolhida\] > \.qd-resumos\{display:none\}", css)
    assert ".qd-area-corpo > .qd-disc:only-child > .qd-disc-tit{display:none}" in css


# ======================================================================== 3. grifo nas aulas: funcoes puras

GRIFO_PURAS = _funcs("function qzGrifoMesclar(intervalos, novo){", "function grifoValido(g){",
                     "function grifoResolver(textos, g){", "function grifoResolverPos(textos, g, t){", "function grifoNormalizar(textos, lista){",
                     "function grifoAparar(texto, ini, fim){", "function grifoFatias(tamanhos, ini, fim){",
                     "function grifoReconciliar(local, banco){")


def _puras(expr):
    return _node(GRIFO_PURAS + "\nconsole.log(JSON.stringify(" + expr + "));")


def test_grifo_reancora_pelo_offset_pelo_trecho_e_pelo_documento():
    textos = ["A PEEP mantém o alvéolo aberto.", "Pplatô < 30 e PEEP alta.", "Driving pressure < 15."]
    casos = {
        "bate": {"b": 0, "ini": 2, "fim": 6, "txt": "PEEP"},
        "deslocou": {"b": 0, "ini": 0, "fim": 4, "txt": "PEEP"},                 # texto mudou: mesmo bloco
        "outro_bloco": {"b": 0, "ini": 0, "fim": 16, "txt": "Driving pressure"},  # o bloco perdeu o trecho
        "sumiu": {"b": 1, "ini": 0, "fim": 6, "txt": "Auto-P"},
        "bloco_inexistente": {"b": 9, "ini": 0, "fim": 6, "txt": "Pplatô"},
        "txt_errado": {"b": 0, "ini": 2, "fim": 6, "txt": "PEE"},
        "branco": {"b": 0, "ini": 1, "fim": 2, "txt": " "},
        "fracionado": {"b": 0, "ini": 1.5, "fim": 6, "txt": "PEEP"},
    }
    out = _puras("(function(){ var t = %s, c = %s, o = {}; Object.keys(c).forEach(function(k){ o[k] = grifoResolver(t, c[k]); }); return o; })()"
                 % (json.dumps(textos, ensure_ascii=False), json.dumps(casos, ensure_ascii=False)))
    assert out["bate"] == {"b": 0, "ini": 2, "fim": 6, "txt": "PEEP"}
    assert out["deslocou"] == {"b": 0, "ini": 2, "fim": 6, "txt": "PEEP"}
    assert out["outro_bloco"] == {"b": 2, "ini": 0, "fim": 16, "txt": "Driving pressure"}
    assert out["bloco_inexistente"] == {"b": 1, "ini": 0, "fim": 6, "txt": "Pplatô"}
    for k in ("sumiu", "txt_errado", "branco", "fracionado"):
        assert out[k] is None, k


def test_grifo_mescla_no_mesmo_bloco_e_descarta_o_que_nao_ancora():
    textos = ["alfa beta gama delta", "epsilon zeta"]
    lista = [{"b": 1, "ini": 0, "fim": 7, "txt": "epsilon"},
             {"b": 0, "ini": 5, "fim": 9, "txt": "beta"},
             {"b": 0, "ini": 7, "fim": 15, "txt": "ta gama "},     # sobrepoe beta -> um so
             {"b": 0, "ini": 15, "fim": 20, "txt": "delta"},       # encosta -> junta
             {"b": 0, "ini": 0, "fim": 3, "txt": "xyz"},           # nao ancora: sai sem erro
             None, "lixo", {"b": "0", "ini": 0, "fim": 4, "txt": "alfa"}]
    out = _puras("grifoNormalizar(%s, %s)" % (json.dumps(textos), json.dumps(lista)))
    assert out == [{"b": 0, "ini": 5, "fim": 20, "txt": "beta gama delta"},
                   {"b": 1, "ini": 0, "fim": 7, "txt": "epsilon"}]


def test_grifo_apara_o_branco_e_fatia_por_no_de_texto():
    out = _puras('{a: grifoAparar("  PEEP alta \\n", 0, 13), b: grifoAparar("x  y", 0, 2), c: grifoAparar("ab", 0, 2),'
                 ' f: grifoFatias([5, 3, 10], 3, 12), g: grifoFatias([4, 0, 4], 4, 8), h: grifoFatias([4], 4, 4)}')
    assert out == {"a": [2, 11], "b": None, "c": [0, 2], "f": [[0, 3, 5], [1, 0, 3], [2, 0, 4]],
                   "g": [[2, 0, 4]], "h": []}


def test_grifo_aparelho_pendente_vence_e_o_banco_manda_no_resto():
    g1, g2 = [{"b": 0, "ini": 0, "fim": 4, "txt": "alfa"}], [{"b": 1, "ini": 0, "fim": 4, "txt": "beta"}]
    casos = {
        "pendente_mais_novo": [{"grifos": g1, "pendente": True, "atualizado_em": "2026-10-04T21:00:00Z"},
                               {"grifos": g2, "atualizado_em": "2026-10-04T20:00:00Z"}],
        "pendente_sem_banco": [{"grifos": g1, "pendente": True, "atualizado_em": "2026-10-04T21:00:00Z"}, None],
        "pendente_mais_velho": [{"grifos": g1, "pendente": True, "atualizado_em": "2026-10-04T19:00:00Z"},
                                {"grifos": g2, "atualizado_em": "2026-10-04T20:00:00Z"}],
        "confirmado_e_banco_vazio": [{"grifos": g1, "pendente": False, "atualizado_em": "2026-10-04T21:00:00Z"}, None],
        "nada": [None, None],
    }
    out = _puras("(function(){ var c = %s, o = {}; Object.keys(c).forEach(function(k){ o[k] = grifoReconciliar(c[k][0], c[k][1]); }); return o; })()"
                 % json.dumps(casos))
    assert out["pendente_mais_novo"]["grifos"] == g1 and out["pendente_mais_novo"]["reenviar"] is True
    assert out["pendente_sem_banco"]["fonte"] == "aparelho"
    assert out["pendente_mais_velho"] == {"grifos": g2, "fonte": "banco", "reenviar": False,
                                          "atualizado_em": "2026-10-04T20:00:00Z"}
    assert out["confirmado_e_banco_vazio"]["grifos"] == [] and out["confirmado_e_banco_vazio"]["fonte"] == "banco", \
        "o banco manda: o agente limpou"
    assert out["nada"]["grifos"] == []


# ======================================================================== 4. grifo nas aulas: gravacao

GRIFO_GRAVA = "\n".join([_var("GRIFO_COLECAO"), _var("GRIFO_PREFIXO"), _var("GRIFO"), _funcs(
    "function pendIdValido(id){", "function grifoLocal(slug, v){", "function grifoDb(){",
    "function grifoEnviar(slug){", "function grifoSalvar(slug, grifos){", "function grifoReenviarTodos(exceto){")])

BANCO_GRIFO = r"""
var BANCO = __BANCO__, PEDIDOS = 0, VISTO = [], ESCRITAS = [], FORA = true;
function colecao(path){ return {doc: function(id){ return {
  get: function(){ VISTO.push(JSON.parse(localStorage.getItem("medhub.grifos.aula." + id) || "null"));
    var v = BANCO[id]; return Promise.resolve({exists: v !== undefined, data: function(){ return v; }}); },
  set: function(d){ ESCRITAS.push(["set", path, id]); BANCO[id] = JSON.parse(JSON.stringify(d)); return Promise.resolve(); },
  update: function(d){ ESCRITAS.push(["update", path, id]); Object.assign(BANCO[id], JSON.parse(JSON.stringify(d))); return Promise.resolve(); }}; }}; }
var window = {claude: {use: function(){ PEDIDOS++; return Promise.resolve(FORA ? null : {collection: colecao}); }}};
"""


def _gravar(acao, banco=None, ls=None):
    prog = (_aparelho(ls) + BANCO_GRIFO.replace("__BANCO__", json.dumps(banco or {})) + GRIFO_GRAVA +
            "\nvar SAIDA = {};\nPromise.resolve().then(function(){ " + acao + " }).then(function(){ "
            "SAIDA.banco = BANCO; SAIDA.ls = LS; SAIDA.visto = VISTO; SAIDA.escritas = ESCRITAS; SAIDA.pedidos = PEDIDOS;"
            " console.log(JSON.stringify(SAIDA)); });")
    return _node(prog)


G_AULA = [{"b": 3, "ini": 2, "fim": 6, "txt": "PEEP", "extra": "fora do registro"}]


def test_grifo_vai_ao_aparelho_antes_do_banco_e_reenvia_quando_ele_volta():
    acao = """return grifoSalvar("rd-vent", %s).then(function(ok){ SAIDA.sem_banco = {ok: ok, ls: JSON.parse(LS["medhub.grifos.aula.rd-vent"])};
      FORA = false; return grifoEnviar("rd-vent"); }).then(function(ok){ SAIDA.voltou = ok; });""" % json.dumps(G_AULA)
    out = _gravar(acao)
    assert out["sem_banco"]["ok"] is False
    assert out["sem_banco"]["ls"]["pendente"] is True and out["sem_banco"]["ls"]["grifos"] == [
        {"b": 3, "ini": 2, "fim": 6, "txt": "PEEP"}], "so b/ini/fim/txt; guardado mesmo sem banco"
    assert out["pedidos"] == 2, "R10: o banco que nao veio nao fica memorizado"
    assert out["voltou"] is True and out["escritas"] == [["set", "analises/grifos/itens", "rd-vent"]]
    doc = out["banco"]["rd-vent"]
    assert doc["origem"] == "rd-vent" and doc["grifos"] == out["sem_banco"]["ls"]["grifos"]
    assert doc["atualizado_em"] == out["sem_banco"]["ls"]["atualizado_em"]
    assert out["visto"][0]["pendente"] is True, "o aparelho ja tinha o grifo quando o banco foi lido"
    assert json.loads(out["ls"]["medhub.grifos.aula.rd-vent"])["pendente"] is False, "confirmado: sai do pendente"


def test_grifo_regrava_por_update_preservando_o_que_o_agente_acrescentou():
    out = _gravar('FORA = false; return grifoSalvar("rd-vent", %s);' % json.dumps(G_AULA),
                  banco={"rd-vent": {"origem": "rd-vent", "grifos": [], "lido_pelo_agente": "2026-10-05"}})
    assert out["escritas"] == [["update", "analises/grifos/itens", "rd-vent"]]
    assert out["banco"]["rd-vent"]["lido_pelo_agente"] == "2026-10-05"
    assert out["banco"]["rd-vent"]["grifos"][0]["txt"] == "PEEP"


def test_pendentes_de_outras_aulas_sobem_e_o_confirmado_nao_regrava():
    pend = lambda t: json.dumps({"grifos": [{"b": 0, "ini": 0, "fim": 4, "txt": t}], "pendente": True,
                                 "atualizado_em": "2026-10-04T20:00:00Z"})
    ls = {"medhub.grifos.aula.rd-a": pend("alfa"), "medhub.grifos.aula.rd-b": pend("beta"),
          "medhub.grifos.aula.rd-c": json.dumps({"grifos": [], "pendente": False, "atualizado_em": "x"}),
          "medhub.grifos.aula.a/b": pend("ruim"), "medhub.secoes": "{}"}
    out = _gravar('FORA = false; grifoReenviarTodos("rd-a"); return GRIFO.fila;', ls=ls)
    assert out["escritas"] == [["set", "analises/grifos/itens", "rd-b"]], \
        "so a outra pendente: a aberta (rd-a) reconcilia na leitura; a confirmada e o id invalido ficam"
    assert json.loads(out["ls"]["medhub.grifos.aula.rd-a"])["pendente"] is True


# ======================================================================== 5. grifo nas aulas: amarracao

def test_leitor_liga_o_grifo_sem_poder_derrubar_e_mede_depois():
    corpo = extrair_funcao(TEMPLATE, "function preparar(quadro){")
    liga = 'if(quadro.id === "hub-leitor-quadro"){ try{ grifoLigar(doc, quadro, GRIFO.slug); }catch(e){} }'
    assert liga in corpo and corpo.index(liga) < corpo.index("    medir(quadro);")
    assert "GRIFO.slug = pendSlug(href); GRIFO.ctx = null;" in extrair_funcao(TEMPLATE, "function abrirAula(")
    assert 'GRIFO.slug = ""; GRIFO.ctx = null;' in extrair_funcao(TEMPLATE, "function fecharAula(){")
    mudar = extrair_funcao(TEMPLATE, "function grifoMudar(ctx, lista){")
    assert mudar.index("grifoPintar(ctx)") < mudar.index("medir(ctx.quadro)"), "a altura e medida de novo"


def test_grifo_mora_em_analises_e_nao_toca_a_alca_nem_os_controles():
    assert _var("GRIFO_COLECAO") == 'var GRIFO_COLECAO = "analises/grifos/itens";'
    assert set(re.findall(r'claude\.use\("(\w+)"\)', TEMPLATE)) == {"db"}, "nada novo na declaracao do publish"
    fora = re.search(r'var GRIFO_FORA = "([^"]+)";', TEMPLATE).group(1)
    for sel in ("form.pend", "button", "textarea", "a[href]", "input", "select"):
        assert sel in fora, sel
    blocos = extrair_funcao(TEMPLATE, "function grifoBlocos(doc){")
    assert '!el.closest("form.pend") && !el.querySelector("form.pend")' in blocos
    assert "!el.querySelector(GRIFO_BLOCO)" in blocos, "bloco = folha"
    salvar = extrair_funcao(TEMPLATE, "function grifoSalvar(slug, grifos){")
    assert salvar.index("grifoLocal(slug,") < salvar.index("grifoEnviar(slug)"), "aparelho ANTES do banco"
    estilo = extrair_funcao(TEMPLATE, "function grifoEstilo(doc){")
    assert '"--grifo-" + c' in estilo and 'mark.hub-grifo[data-cor="ciano"]' in estilo, "s228: uma regra por cor do grifo"
    assert "color:inherit" in estilo and "--qz-grifo-tinta" not in estilo and "MarkText" not in estilo, \
        "s227 (part 6): no leitor o grifo tambem pinta so o fundo"


# ======================================================================== 6. s216: hub-integracao
# PRD `.vibeflow/prds/hub-integracao-cortar-passos.md` (pedido do operador em 05/10/2026: "os ganhos
# agora sao de integracao, remocao de redundancias, cortar passos desnecessarios"). As funcoes REAIS
# do template rodam em node com stubs minimos do que elas chamam.

#: o que `abrirAula` toca, falso: o DOM do leitor, a alca, o grifo e o carregamento do quadro
LEITOR_FALSO = r"""
var els = {}, CHAMADAS = [];
function $(id){ return els[id] || (els[id] = {id: id, hidden: false, textContent: "", attrs: {},
  setAttribute: function(k, v){ this.attrs[k] = v; }, getAttribute: function(k){ return this.attrs[k]; }}); }
var lista = $("hub-aulas-lista"), leitor = $("hub-leitor"); leitor.hidden = true;
var window = {scrollTo: function(x, y){ CHAMADAS.push(["scrollTo", y]); }, pageYOffset: 0};
var GRIFO = {slug: "", ctx: null};
function pendSoltar(){ CHAMADAS.push(["pendSoltar"]); }
function assinaAbrir(slug){ CHAMADAS.push(["assinaAbrir", slug]); }
function carregar(q, href, aviso){ CHAMADAS.push(["carregar", q.id, href]); }
"""

#: o que `painelAtalho` toca, falso: a troca de aba, o modo das Listas e o leitor
ATALHO_FALSO = r"""
var CHAMADAS = [];
var window = {scrollTo: function(x, y){ CHAMADAS.push(["scrollTo", y]); }, pageYOffset: 0};
function ir(aba, gravar){ CHAMADAS.push(["ir", aba, gravar]); }
function qzModoPedido(m){ CHAMADAS.push(["modo", m]); }
function abrirAula(href, titulo){ CHAMADAS.push(["abrirAula", href, titulo]); }
function leitorOrigem(){ return {aba: "painel", y: 0}; }
var document = {querySelector: function(){ throw new Error("o Painel nao procura o link na Teoria (A1)"); }};
function link(attrs, tema){
  var li = tema == null ? null : {querySelector: function(s){ return s === ".t-tema" ? {textContent: tema} : null; }};
  return {getAttribute: function(k){ return Object.prototype.hasOwnProperty.call(attrs, k) ? attrs[k] : null; },
          closest: function(s){ return s === "li" ? li : null; }};
}
"""


#: s216 (part-4): a origem do leitor (a aba e a rolagem de ANTES de abrir) e o que abrirAula le dela
ORIGEM_FALSA = r"""
var raiz = {attrs: {"data-aba": "aulas"}, getAttribute: function(k){ return this.attrs[k] || null; }};
window.requestAnimationFrame = function(f){ f(); }; window.innerHeight = 800;
function ir(aba, gravar){ raiz.attrs["data-aba"] = aba; CHAMADAS.push(["ir", aba, gravar]); }
function fecharAula(){ CHAMADAS.push(["fecharAula"]); }
function marcarRecente(aba, slug){ CHAMADAS.push(["recente", aba, slug]); return null; }
"""

LEITOR_FUNCS = "\n".join([_var("ABAS"), _var("LEITOR"), _var("ROTULO_ABA"), _funcs(
    "function valida(aba){", "function pendIdValido(id){", "function pendSlug(href){", "function leitorOrigem(){",
    "function abrirAula(")])


def test_painel_abre_o_documento_pelo_href_sem_procurar_na_teoria():
    """Part-1 (A1): o Dossie e a Autopsia sairam da Teoria; o "abrir documento" do Painel abria a
    aba e nao abria nada (procurava `a.hub-aula[href]` no DOM dela). O atalho passa o href e o
    titulo do PROPRIO link (`data-titulo`; sem ele, o tema do item) ao `abrirAula`."""
    prog = (ATALHO_FALSO + _var("ABAS") + "\n" + _funcs("function valida(aba){", "function painelAtalho(a", "function abrirNaTeoria(") +
            r"""
var SAIDA = {};
CHAMADAS = []; painelAtalho(link({"href": "aulas/dossie-uerj.html", "data-hub-aula": "dossie-uerj"}, "Dossiê UERJ"));
SAIDA.doc = CHAMADAS;
CHAMADAS = []; painelAtalho(link({"href": "aulas/dmg.html", "data-hub-aula": "dmg", "data-titulo": "A Escada do DMG"}, "Diabetes"));
SAIDA.aula = CHAMADAS;
CHAMADAS = []; painelAtalho(link({"href": "#cards", "data-hub-aba": "cards"}));
SAIDA.cards = CHAMADAS;
CHAMADAS = []; painelAtalho(link({"href": "#questoes", "data-hub-aba": "questoes", "data-hub-modo": "simulados"}));
SAIDA.listas = CHAMADAS;
console.log(JSON.stringify(SAIDA));""")
    out = _node(prog)
    assert out["doc"][-1] == ["abrirAula", "aulas/dossie-uerj.html", "Dossiê UERJ"]
    assert ["ir", "aulas", True] in out["doc"]
    assert out["aula"][-1] == ["abrirAula", "aulas/dmg.html", "A Escada do DMG"], "data-titulo vence o tema"
    assert ["ir", "cards", True] in out["cards"] and not [c for c in out["cards"] if c[0] == "abrirAula"]
    assert ["modo", "simulados"] in out["listas"] and ["ir", "questoes", True] in out["listas"]


def test_abrir_aula_aceita_o_link_ou_o_par_href_titulo():
    """Part-1: `abrirAula(link)` (a Teoria) e `abrirAula(href, titulo)` (o Painel) abrem o MESMO
    leitor: titulo, link de pagina inteira, alca e grifo pelo slug do href, quadro carregado."""
    prog = (LEITOR_FALSO + ORIGEM_FALSA + LEITOR_FUNCS +
            r"""
var SAIDA = {};
abrirAula("aulas/dossie-uerj.html", "Dossiê UERJ");
SAIDA.par = {titulo: $("hub-leitor-titulo").textContent, link: $("hub-leitor-link").attrs.href, grifo: GRIFO.slug,
  lista: lista.hidden, leitor: leitor.hidden, chamadas: CHAMADAS};
CHAMADAS = [];
abrirAula({getAttribute: function(k){ return {href: "aulas/dmg.html", "data-titulo": "A Escada do DMG"}[k] || null; }});
SAIDA.el = {titulo: $("hub-leitor-titulo").textContent, link: $("hub-leitor-link").attrs.href, grifo: GRIFO.slug, chamadas: CHAMADAS};
console.log(JSON.stringify(SAIDA));""")
    out = _node(prog)
    assert out["par"]["titulo"] == "Dossiê UERJ" and out["par"]["link"] == "aulas/dossie-uerj.html"
    assert out["par"]["grifo"] == "dossie-uerj" and out["par"]["lista"] is True and out["par"]["leitor"] is False
    assert ["assinaAbrir", "dossie-uerj"] in out["par"]["chamadas"]
    assert ["carregar", "hub-leitor-quadro", "aulas/dossie-uerj.html"] in out["par"]["chamadas"]
    assert out["el"]["titulo"] == "A Escada do DMG" and out["el"]["link"] == "aulas/dmg.html"
    assert ["carregar", "hub-leitor-quadro", "aulas/dmg.html"] in out["el"]["chamadas"]


def test_p21_lista_e_so_a_lista_e_o_toque_abre_as_questoes():
    """P21 (pedido do operador em 07/10, noite, resolvendo listas: "o bloco 'listas' esta bugado,
    alternando entre tarefas com e sem hiperlinks abaixo ... se estou em listas e clico na tarefa,
    naturalmente devo ir especificamente para as questoes"). ⚰️ s216 part-2 / s218 P2: o "abrir aula" e o
    "resumo: ..." debaixo das listas que tinham aula ligada (daí o alterna). Cada item e SO o botao da
    lista -- nenhum link irmao --, o toque abre a lista (o player; a escolha Estudo/Prova da s211 e o 1o
    passo dele) e nada do que existia so para os links sobra na pagina: o `#hub-ligacoes`, o
    `HUB_LIGACOES`, o `qzAulasHtml`, o CSS `.qz-aula` e o ramo do clique."""
    acao = r"""
SAIDA.html = $("qz-listas").innerHTML;
var b = {getAttribute: function(k){ return k === "data-qzl" ? "t68" : null; }};
var ev = evento(function(s){ return s === "button[data-qzl]" ? b : null; });
qzListasClique(ev); SAIDA.lista = ABRIU.slice(); SAIDA.aula = ABRIU_AULA.slice();
QZ.listas[1].status = "resolvendo"; qzRenderListas(); SAIDA.depois = $("qz-listas").innerHTML;"""
    out = _rodar_listas(acao)
    for html in (out["html"], out["depois"]):
        itens = re.findall(r"<li[^>]*>(.*?)</li>", html, re.S)
        assert len(itens) == len(LISTAS_SEC), itens
        assert all(re.fullmatch(r'<button type="button" data-qzl="[^"]+">.*?</button>', i, re.S) for i in itens),             "cada item e SO o botao da lista: nada debaixo dele"
        assert "<a " not in html and "abrir aula" not in html and "resumo:" not in html
    assert out["lista"] == ["t68"] and out["aula"] == [], "o toque abre a lista, nunca a aula"
    for morto in ("qzAulasHtml", "HUB_LIGACOES", 'id="hub-ligacoes"', "@hub:ligacoes", ".qz-aula", "a.qz-aula"):
        assert morto not in TEMPLATE, morto
    clique = extrair_funcao(TEMPLATE, "function qzListasClique(e){")
    assert "abrirNaTeoria" not in clique and 'closest("button[data-qzl]")' in clique


def test_voltar_origem_fecha_volta_para_a_aba_e_restaura_o_scroll():
    """Part-4 (P14, DoD 1): a origem (aba + rolagem) e gravada ANTES de qualquer `ir` -- o Painel grava
    `medhub.aba = aulas` ao abrir, e sem isso a origem seria sempre a Teoria. `voltarOrigem` fecha o
    leitor, volta a aba de origem, marca o item e restaura a rolagem; sem origem, volta a Teoria. O
    botao de voltar do leitor diz para onde vai."""
    prog = (LEITOR_FALSO + ORIGEM_FALSA + LEITOR_FUNCS + "\n" +
            _funcs("function abrirNaTeoria(", "function voltarOrigem(") + r"""
var SAIDA = {};
raiz.attrs["data-aba"] = "painel"; window.pageYOffset = 640;
abrirNaTeoria("aulas/dossie-uerj.html", "Dossiê UERJ");
SAIDA.aberto = {aba: raiz.attrs["data-aba"], origem: LEITOR.origem, voltar: $("hub-leitor-voltar").textContent};
CHAMADAS = []; window.pageYOffset = 0;
voltarOrigem("dossie-uerj");
setTimeout(function(){
  SAIDA.volta = CHAMADAS; SAIDA.aba = raiz.attrs["data-aba"]; SAIDA.origem = LEITOR.origem;
  raiz.attrs["data-aba"] = "aulas"; window.pageYOffset = 300;
  abrirAula({getAttribute: function(k){ return {href: "aulas/dmg.html", "data-titulo": "DMG"}[k] || null; }});
  SAIDA.teoria = {origem: LEITOR.origem, voltar: $("hub-leitor-voltar").textContent};
  LEITOR.origem = null; CHAMADAS = [];
  voltarOrigem();
  setTimeout(function(){ SAIDA.sem = CHAMADAS; console.log(JSON.stringify(SAIDA)); }, 200);
}, 200);""")
    out = _node(prog)
    assert out["aberto"]["aba"] == "aulas"
    assert out["aberto"]["origem"] == {"aba": "painel", "y": 640}, "capturada ANTES do ir"
    assert out["aberto"]["voltar"] == "‹ Painel"
    assert out["volta"][:3] == [["fecharAula"], ["ir", "painel", True], ["recente", "painel", "dossie-uerj"]]
    assert ["scrollTo", 640] in out["volta"] and out["origem"] is None
    assert out["teoria"] == {"origem": {"aba": "aulas", "y": 300}, "voltar": "‹ Teoria"}
    assert out["sem"][:2] == [["fecharAula"], ["ir", "aulas", True]] and ["scrollTo", 0] in out["sem"]
    corpo = extrair_funcao(TEMPLATE, "function abrirNaTeoria(")
    assert corpo.index("leitorOrigem()") < corpo.index('ir("aulas"'), "a origem antes da troca de aba"
    assert '$("hub-leitor-voltar").addEventListener("click", function(){ voltarOrigem(); });' in TEMPLATE


CONCLUIR_FALSO = r"""
var UPD = [], FECHOU = 0, FALHA = __FALHA__;
QZ.lista = "t49";
QZ.db = {doc: function(p){ return {update: function(d){ UPD.push([p, d.status]);
  return FALHA ? Promise.reject({code: "permission-denied"}) : Promise.resolve(); }}; }};
function qzFecharLista(){ FECHOU++; }
function qzAgora(){ return "2026-10-05T12:00:00.000Z"; }
"""


def test_concluir_lista_fecha_e_marca_a_recente():
    """Part-4 (P14, DoD 3): "Concluir lista" grava `status: resolvida` e, no `.then`, fecha a lista: a aba
    Listas volta com a lista recem-resolvida marcada (`qz-recente`, por ESTADO -- o snapshot refaz o HTML,
    marcar no DOM se perderia, A12): primeiro na semana, depois em Resolvidas (aberta) e, no rerender
    seguinte, sem marca. Falha: fica na tela de fim, com o erro."""
    extra = _funcs("function qzConcluir(){", "function qzConcluiu(lista){", "function qzRolarRecente(){")
    acao = r"""
qzConcluir();
setTimeout(function(){
  SAIDA.antes = $("qz-listas").innerHTML; SAIDA.fechou = FECHOU; SAIDA.upd = UPD; SAIDA.st = $("qz-fim-status").textContent;
  QZ.listas[1].status = "resolvida"; qzRenderListas(); SAIDA.snap = $("qz-listas").innerHTML; SAIDA.recente = QZ.recente || null;
  qzRenderListas(); SAIDA.depois = $("qz-listas").innerHTML;
  console.log(JSON.stringify(SAIDA)); }, 50);"""
    out = _rodar_listas(CONCLUIR_FALSO.replace("__FALHA__", "false") + extra + acao)
    assert out["upd"] == [["listas/t49", "resolvida"]] and out["fechou"] == 1
    assert '<li class="qz-recente"><button type="button" data-qzl="t49">' in out["antes"]
    assert '<details class="qd-feitas" open><summary>Resolvidas' in out["snap"]
    assert '<li class="qz-recente"><button type="button" data-qzl="t49">' in out["snap"].split("Resolvidas", 1)[1]
    assert out["recente"] is None, "a marca vale por 1 rerender na lista ja resolvida"
    assert "qz-recente" not in out["depois"] and "<details class=\"qd-feitas\" open>" not in out["depois"]
    falhou = _rodar_listas(CONCLUIR_FALSO.replace("__FALHA__", "true") + extra + acao)
    assert falhou["fechou"] == 0 and "qz-recente" not in falhou["antes"]
    assert falhou["st"] == "Não gravou (permission-denied)."
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    assert re.search(r"\.qz-lista li\.qz-recente > button\{[^}]*\}", css)
    assert '$("qz-concluir").addEventListener("click", qzConcluir);' in TEMPLATE



# ------------------------------------------------ s216 (hub-integracao part-6, P08 v0): "Hoje ao vivo"
# O Painel publicado e foto; a pagina ja grava as notas do lote e as respostas. Ao abrir, ela SOMA ao
# lado do numero publicado o que gravou depois ("+K", `title="desde o publish"`), nunca o substitui, nunca
# mexe no teto nem no saldo. Dupla contagem (A16): o lote no ar ja gravado (sessao == a gravada) soma 0;
# questao de lista ja registrada no plano (a tarefa saiu do Painel) nao soma. Dia por `Date.parse` (A17).

VIVO_PURAS = _funcs("function vivoDia(t){", "function vivoCards(notas, lote, sessaoGravada){",
                    "function vivoQuestoes(respostas, listasPendentesDeRegistro, hojeLogico){")


def test_lote_ja_gravado_nao_conta_duas_vezes():
    notas = [{"card_id": 1, "rating_primeira": 3}, {"card_id": 2, "rating_primeira": 1},
             {"card_id": 2, "rating_primeira": 4}, {"card_id": 3, "defeito": True, "motivo": "x"}]
    out = _node(VIVO_PURAS + "\nconsole.log(JSON.stringify({no_ar: vivoCards(%s, {sessao: '05b'}, '05a'),"
                " gravado: vivoCards(%s, {sessao: '05a'}, '05a'), sem_lote: vivoCards(%s, null, '05a'),"
                " sem_marcador: vivoCards(%s, {sessao: '05b'}, '')}));" % ((json.dumps(notas),) * 4))
    assert out == {"no_ar": 2, "gravado": 0, "sem_lote": 0, "sem_marcador": 2}, \
        "card distinto com nota; defeito nao e revisao; lote ja gravado ja esta no numero publicado"


def test_lista_registrada_no_plano_nao_conta_as_respostas():
    resp = [{"lista": "t49", "num": 1, "respondido_em": "2026-10-05T13:00:00.000Z"},       # 10h de 05/10
            {"lista": "t49", "num": 1, "respondido_em": "2026-10-05T13:05:00.000Z"},       # a mesma questao
            {"lista": "t49", "num": 2, "respondido_em": "2026-10-06T02:00:00.000Z"},       # 23h de 05/10 (A17)
            {"lista": "t49", "num": 3, "respondido_em": "2026-10-04T15:00:00.000Z"},       # ontem
            {"lista": "t49_1", "num": 1, "respondido_em": "2026-10-05T14:00:00.000Z"},
            {"lista": "t26", "num": 1, "respondido_em": "2026-10-05T14:00:00.000Z"},       # registrada: fora
            {"lista": "t49", "num": 4, "respondido_em": "lixo"}]
    out = _node(VIVO_PURAS + "\nconsole.log(JSON.stringify({k: vivoQuestoes(%s, ['t49', 't49_1'], '2026-10-05'),"
                " nada: vivoQuestoes(%s, [], '2026-10-05')}));" % (json.dumps(resp), json.dumps(resp)))
    assert out == {"k": 3, "nada": 0}


VIVO_PREPARO = r"""
Object.keys(CFG.colecoes || {}).forEach(function(k){ BANCO[k] = CFG.colecoes[k]; });
(BANCO.respostas ? Object.keys(BANCO.respostas) : []).forEach(function(k){ var r = BANCO.respostas[k];
  if(r.respondido_em === "HOJE"){ r.respondido_em = new Date().toISOString(); }
  if(r.respondido_em === "ONTEM"){ r.respondido_em = new Date(Date.now() - 36 * 3600 * 1000).toISOString(); } });
function espera(){ return new Promise(function(ok){ setTimeout(ok, 0); }); }
// s229: um numero so (publicado + K) -- `mais` = o K que a pagina somou (data-vivo-k), `title` o do proprio numero;
// o span "+K" ciano morreu (`span.vivo` nunca existe)
function fracao(chave){ var b = $("pa").querySelector('b[data-vivo="' + chave + '"]');
  if($("pa").querySelector('span.vivo')){ throw new Error("o +K voltou"); }
  return {b: b.textContent, base: b.getAttribute("data-base"), mais: b.getAttribute("data-vivo-k"), title: b.getAttribute("title")}; }
"""

ACAO_VIVO = VIVO_PREPARO + r"""
painelVivo($("pa"), CFG.semDb ? null : DB);
espera().then(espera).then(espera).then(espera).then(function(){
  console.log(JSON.stringify({cards: fracao("cards"), questoes: fracao("questoes"), escritas: ESCRITAS})); });
"""

#: s227: o db como o `painelListas` o entrega (o `use("db")` no. 1) e a foto depois de `CFG.esperaMs` (o relogio
#: do RELOGIO_JS encurta 10x as esperas >= 1 s da retentativa)
ACAO_VIVO_CONEXAO = VIVO_PREPARO + r"""
window.claude.use("db").then(function(db){ painelVivo($("pa"), db); });
_st(function(){
  console.log(JSON.stringify({cards: fracao("cards"), questoes: fracao("questoes"), escritas: ESCRITAS, usos: USOS_DB,
                              esperas: ESPERAS_VISTAS, avisos: AVISOS_LEITURA, texto: $("pa").textContent})); }, CFG.esperaMs);
"""


def _painel_vivo_html(sessao_gravada):
    from tools import painel
    d = {"questoes": {"feitas_hoje": 30, "alvo_dia": 120.0, "meta": 10000, "faltam": 1000, "dias": 27,
                      "data_meta": "2026-11-01"},
         "cards": {"vencidos": 10, "novos": 50, "teto": 100, "consumo_hoje": 62, "restantes": 38,
                   "retencao_7d": {"retencao": None}},
         "agenda": {"dias": [{"data": "2026-10-06", "n": 3}]}, "sessao_gravada": sessao_gravada}

    def t(id_):
        return {"id": id_, "semana": 4, "atrasada": False, "tema": "T%d" % id_, "q": 21, "classe": "lista",
                "url_lista": "https://x", "area": None, "rotulo": "CM", "aula": None, "aulas": [], "no_hub": True}
    return ('<div id="pa">%s<ol class="tarefas">%s</ol></div>'
            % (painel._html_dia(d, "2026-10-05"), "".join(painel._html_tarefa(t(i)) for i in (49, 68))))


def _rodar_vivo(sessao_no_ar="2026-10-05b", sessao_gravada="2026-10-05a", acao=None, conexao="", **cfg):
    """O `painelVivo` REAL sobre o banco falso do test_hub_quadro. `conexao` (JS) troca o `use("db")` depois do
    banco (o CONEXAO_JS: a 1a conexao falha em toda leitura) e entra com o RELOGIO_JS antes dele."""
    from tools.test_hub_quadro import BANCO_QD, DOM_QD, _arvore
    lote = '<script id="lote" type="application/json">%s</script>' % json.dumps({"sessao": sessao_no_ar, "cards": []})
    arvore = _arvore(_painel_vivo_html(sessao_gravada) + lote)
    # s227: o painelVivo le pela assinatura resiliente (retentativa com conexao nova)
    funcs = "\n".join([VIVO_PURAS, _var("ESPERAS_LEITURA"),
                       _funcs("function assinarResiliente(consulta, onDados, opts){",
                              "function vivoPintar(doc, chave, k){", "function loteNoAr(){",
                              "function painelVivo(doc, db){")])
    relogio = RELOGIO_JS.replace("__FALHAS__", "{}") if conexao else ""
    prog = (DOM_QD.replace("__ARVORE__", json.dumps(arvore, ensure_ascii=False)) + relogio +
            BANCO_QD.replace("__CFG__", json.dumps(cfg, ensure_ascii=False)) + conexao + "\n" + funcs + "\n" +
            (acao or ACAO_VIVO))
    return _node(prog)


COLECOES_VIVO = {
    "sessoes/2026-10-05b/notas": {"1": {"card_id": 1, "rating_primeira": 3}, "2": {"card_id": 2, "rating_primeira": 4},
                                  "3": {"card_id": 3, "defeito": True, "motivo": "x"}},
    "listas": {"t49": {"tarefa": 49, "status": "resolvendo"}, "t49_1": {"tarefa": 49, "status": "capturada"},
               "t68": {"tarefa": 68, "status": "resolvida"}, "t26": {"tarefa": 26, "status": "resolvida"},
               "t90": {"tarefa": 90, "status": "pendente"}},
    "respostas": {"t49_1": {"lista": "t49", "num": 1, "respondido_em": "HOJE"},
                  "t49_2": {"lista": "t49", "num": 2, "respondido_em": "ONTEM"},
                  "t49_1_1": {"lista": "t49_1", "num": 1, "respondido_em": "HOJE"},
                  "t68_1": {"lista": "t68", "num": 1, "respondido_em": "HOJE"},
                  "t26_1": {"lista": "t26", "num": 1, "respondido_em": "HOJE"}},
}


def test_ao_vivo_so_soma_e_nunca_altera_o_publicado():
    out = _rodar_vivo(colecoes=COLECOES_VIVO)
    # s229 (pedido dele, 15/10: "um unico numero branco que sobe em tempo real"): o numero vira publicado + K
    assert out["cards"] == {"b": "64", "base": "62", "mais": "2", "title": "2 desde o publish"}
    assert out["questoes"] == {"b": "33", "base": "30", "mais": "3", "title": "3 desde o publish"}, \
        "t49 (1 de hoje), t49_1 e t68 (resolvida, registro pendente); t26 ja registrada (fora do Painel) nao"
    assert out["escritas"] == [], "o Painel nunca grava"
    gravado = _rodar_vivo(sessao_no_ar="2026-10-05a", colecoes=COLECOES_VIVO)
    assert gravado["cards"]["mais"] is None and gravado["cards"]["b"] == "62", "lote no ar ja gravado: +0, sem span"
    sem_db = _rodar_vivo(semDb=True, colecoes=COLECOES_VIVO)
    assert sem_db["cards"] == {"b": "62", "base": "62", "mais": None, "title": None}
    assert sem_db["questoes"]["mais"] is None, "sem db (nao-dono, offline): o Painel fica como o publicado"
    assert "painelVivo(doc, db)" in _funcs("function painelListas(doc, quadro){")
    assert ".vivo{" not in _funcs("function painelListas(doc, quadro){"), "s229: o estilo do +K ciano saiu"


# ---------------------------------------------------------------------------------------------------
# Fase 0 · lote 1 · part 1.1b (DoD 1, 11/10/2026): o AVISO de figura perdida e a figura NA ALTERNATIVA.
# `sem_figura: true` (a captura declarou a perda) mostra 1 linha discreta acima das alternativas, no
# `#qz-figura` que ja existe. `figuras_alt` ({letra: [urls]}) so vira imagem quando `figuras_img_alt`
# traz o data URI da mesma letra -- URL externa nunca e carregada (CSP do artifact / offline).
# ---------------------------------------------------------------------------------------------------

AVISO_SEM_FIGURA = "A figura desta questão não veio na captura."
PNG = "data:image/png;base64,iVBORw0KGgo="


def _com_aviso(acao):
    return extrair_funcao(TEMPLATE, "function qzFiguraAviso(q, nImgs){") + "\n" + acao


def test_sem_figura_mostra_a_linha_do_aviso():
    acao = _com_aviso("""SAIDA = {sem: qzFiguraAviso({sem_figura: true}, 0), sem_com_img: qzFiguraAviso({sem_figura: true}, 1),
      nada: qzFiguraAviso({}, 0), pdf: qzFiguraAviso({figura: true, pagina: 7}, 0),
      sem_e_pdf: qzFiguraAviso({sem_figura: true, figura: true, pagina: 7}, 0)};""")
    out = _rodar(_q(), None, None, acao)
    assert out["sem"] == AVISO_SEM_FIGURA
    assert out["sem_com_img"] == "", "a figura embutida chegou: sem aviso"
    assert out["nada"] == ""
    assert out["pdf"] == "Esta questão tem uma figura que o texto não traz: caderno da prova, página 7."
    assert out["sem_e_pdf"] == AVISO_SEM_FIGURA, "a perda declarada pela captura vence"
    corpo = extrair_funcao(TEMPLATE, "function qzMostrar(i){")
    assert '$("qz-figura").textContent = qzFiguraAviso(q, qzImgs.length)' in corpo
    i_aviso, i_alts = TEMPLATE.index('id="qz-figura"'), TEMPLATE.index('id="qz-alts"')
    assert i_aviso < i_alts, "o aviso mora acima das alternativas"
    assert re.search(r'<p class="qd-aviso qz-figura" id="qz-figura" hidden></p>', TEMPLATE), "sem layout novo"


def test_figura_da_alternativa_so_com_data_uri():
    q = _q(figuras_alt={"B": ["https://emed.example/b.png"], "C": ["https://emed.example/c.png"]},
           figuras_img_alt={"B": [PNG, "https://emed.example/x.png"]})
    out = _rodar(q, None, None, 'SAIDA = {h: qzAltsHtml(q, null, false, {})};')
    h = out["h"]
    blocos = dict(re.findall(r'<div class="qz-alt[^"]*" data-l="([A-E])">(.*?)(?=<div class="qz-alt[ "]|$)', h, re.S))
    assert blocos["B"].count("<img") == 1 and f'src="{PNG}"' in blocos["B"]
    assert 'alt="Figura da alternativa B"' in blocos["B"]
    assert "<img" not in blocos["A"] and "<img" not in blocos["C"], "URL sem data URI: nada extra"
    assert "https://" not in h, "URL externa nunca vai ao src (CSP / offline)"
    i_txt = blocos["B"].index('class="qz-alt-txt"')
    assert blocos["B"].index("<img") > blocos["B"].index("</span>", i_txt), "fora do texto: grifo nao desloca"
    assert ".qz-alt .qz-fig{" in TEMPLATE


def test_alternativa_sem_figura_nao_muda_o_render():
    base = _rodar(_q(), None, None, 'SAIDA = {h: qzAltsHtml(q, null, false, {})};')["h"]
    so_url = _rodar(_q(figuras_alt={"B": ["https://emed.example/b.png"]}), None, None,
                    'SAIDA = {h: qzAltsHtml(q, null, false, {})};')["h"]
    assert so_url == base


# ======================================================================== s226 part-1: abas que se recuperam
# Relato dele (13/10): tocar em Listas ou Teoria deixava a tela presa em "Não consegui ler" ate recarregar --
# a assinatura era feita uma vez so. Agora as leituras das abas passam por `assinarResiliente`: erro =
# console.warn com o codigo + nova assinatura em 1/2/4 s; esgotadas, "Tentar de novo". O banco falso daqui
# imita o `leitura=1x|0` do `core/templates/ui_harness.html` e CONTA os ouvintes vivos (risco: 2 listeners).
# O relogio: as esperas >= 1 s sao anotadas e encurtadas 10x (o teste nao dorme 7 s).

RELOGIO_JS = r"""
var ESPERAS_VISTAS = [], AVISOS_LEITURA = [], _st = setTimeout;
setTimeout = function(f, ms){ if(ms >= 1000){ ESPERAS_VISTAS.push(ms); ms = ms / 10; } return _st(f, ms); };
console.warn = function(){ AVISOS_LEITURA.push(Array.prototype.slice.call(arguments)); };
function dormir(ms){ return new Promise(function(ok){ _st(ok, ms); }); }
// banco falso de leitura: `falhas[col]` = quantas assinaturas seguidas falham (99 = ate `bancoBom()`)
var FALHAS = __FALHAS__, ATIVOS = {}, ASSINATURAS = {};
function bancoBom(){ Object.keys(FALHAS).forEach(function(k){ FALHAS[k] = 0; }); }
function consultaFalsa(col, docs){
  var q = {where: function(){ return q; }, orderBy: function(){ return q; },
    onSnapshot: function(ok, erro){
      ASSINATURAS[col] = (ASSINATURAS[col] || 0) + 1;
      if((FALHAS[col] || 0) > 0){ FALHAS[col]--; var vivo = true;
        _st(function(){ if(vivo){ erro({code: "unavailable", message: "falha de leitura (db falso)"}); } }, 5);
        return function(){ vivo = false; }; }
      ATIVOS[col] = (ATIVOS[col] || 0) + 1; var vivo2 = true;
      _st(function(){ if(vivo2){ ok({docs: docs().map(function(d){ return {id: d.id, data: function(){ return Object.freeze(d.dado); }}; }),
                                    metadata: {fromCache: false}}); } }, 5);
      return function(){ if(vivo2){ vivo2 = false; ATIVOS[col]--; } }; }};
  return q;
}
"""

QZ_LEITURA_JS = "\n".join([_var("ESPERAS_LEITURA"), _funcs(
    "function assinarResiliente(consulta, onDados, opts){", "function htmlRetentar(texto, chave){",
    "function iniciarQuestoes(){", "function qzSemDb(){", "function qzListasClique(e){")])

HARNESS_QZ_LEITURA = RELOGIO_JS + r"""
var els = {};
function $(id){ if(!els[id]){ els[id] = {id: id, innerHTML: "", textContent: "", hidden: false}; } return els[id]; }
$("qz-listas").innerHTML = '<p class="qd-vazio">Carregando as listas…</p>';
var QZ = {db: null, listas: [], iniciado: false, subListas: null};
var RENDERS = 0;
function qzRenderListas(){ RENDERS++; $("qz-listas").innerHTML = "LISTAS " + QZ.listas.map(function(l){ return l._id; }).join(","); }
var DB = {collection: function(c){ return consultaFalsa(c, function(){ return [{id: "t49", dado: {seq: 1}}, {id: "t26", dado: {seq: 2}}]; }); }};
var window = {claude: {use: function(){ return Promise.resolve(DB); }}};
__FUNCS__
function clicar(sel){ qzListasClique({target: {closest: function(s){ return s === sel ? {} : null; }}}); }
var SAIDA = {};
(async function(){
__ACAO__
  SAIDA.esperas = ESPERAS_VISTAS; SAIDA.avisos = AVISOS_LEITURA; SAIDA.ativos = ATIVOS; SAIDA.assinaturas = ASSINATURAS;
  console.log(JSON.stringify(SAIDA));
})();
"""


def _rodar_qz_leitura(acao, falhas):
    return _node(HARNESS_QZ_LEITURA.replace("__FUNCS__", QZ_LEITURA_JS)
                 .replace("__FALHAS__", json.dumps(falhas)).replace("__ACAO__", acao))


def _rodar_quadro_leitura(acao, falhas, quadro=None, conexao=""):
    """A Teoria REAL (`iniciarQuadro` + o quadro do build) sobre o banco falso do test_hub_quadro, com a
    colecao `quadro` trocada pela consulta que falha."""
    from tools.test_hub_quadro import BANCO_QD, DOM_QD, FUNCS_QD, _arvore
    troca = r"""
var _colQd = DB.collection;
DB.collection = function(nome){ if(nome !== "quadro"){ return _colQd(nome); }
  var c = consultaFalsa("quadro", function(){ return Object.keys(BANCO.quadro).map(function(id){ return {id: id, dado: BANCO.quadro[id]}; }); });
  c.doc = _colQd(nome).doc; return c; };
"""
    prog = (DOM_QD.replace("__ARVORE__", json.dumps(_arvore(_pagina_quadro()), ensure_ascii=False)) + RELOGIO_JS.replace("__FALHAS__", json.dumps(falhas)) +
            BANCO_QD.replace("__CFG__", json.dumps({"quadro": quadro or {}}, ensure_ascii=False)) + troca + conexao + _aparelho() +
            FUNCS_QD + r"""
var qd = $("hub-quadro"), SAIDA = {};
function feitoEm(slug){ return qd.querySelector('.qd-item[data-slug="' + slug + '"]').hasAttribute("data-feito"); }
function aviso(){ var a = $("hub-quadro-aviso"); return {oculto: a.hidden, html: a.hidden ? "" : String(a.innerHTML || a.textContent || "")}; }
iniciarQuadro();
(async function(){
""" + acao + r"""
  SAIDA.esperas = ESPERAS_VISTAS; SAIDA.avisos = AVISOS_LEITURA; SAIDA.ativos = ATIVOS; SAIDA.assinaturas = ASSINATURAS;
  console.log(JSON.stringify(SAIDA));
})();
""")
    return _node(prog)


def test_listas_se_recuperam_da_falha_de_leitura():
    """`leitura=1x`: a 1a assinatura de `listas` falha; a aba mostra "Carregando…", reassina em 1 s e as
    listas aparecem sem recarregar (bem antes dos 5 s), com UM ouvinte vivo e o log com codigo e tentativa.
    Reabrir a aba durante a espera nao cria um 2o ouvinte."""
    acao = r"""
  iniciarQuestoes(); await dormir(50);
  SAIDA.na_espera = $("qz-listas").innerHTML;
  iniciarQuestoes(); iniciarQuestoes();                      // tocar na aba de novo durante a espera
  await dormir(200);
  SAIDA.depois = $("qz-listas").innerHTML; SAIDA.estado = QZ.subListas.estado(); SAIDA.iniciado = QZ.iniciado;
"""
    out = _rodar_qz_leitura(acao, {"listas": 1})
    assert "Carregando as listas" in out["na_espera"] and "Tentar de novo" not in out["na_espera"]
    assert out["depois"] == "LISTAS t49,t26" and out["estado"] == "viva" and out["iniciado"] is True
    assert out["esperas"] == [1000] and sum(out["esperas"]) <= 5000
    assert out["avisos"] == [["[hub] leitura listas falhou", "unavailable", 1]]
    assert out["ativos"] == {"listas": 1} and out["assinaturas"] == {"listas": 2}, "um ouvinte so, nunca dois"

    # a Teoria: o "feito" do db chega depois da falha, sem recarregar; o aviso diz "Carregando…" e some
    acao_qd = r"""
  await dormir(50);
  SAIDA.na_espera = aviso(); SAIDA.feito_na_espera = feitoEm("rd-hepato");
  await dormir(200);
  SAIDA.depois = aviso(); SAIDA.feito = feitoEm("rd-hepato"); SAIDA.estado = quadroLeitura.estado();
"""
    qd = _rodar_quadro_leitura(acao_qd, {"quadro": 1}, quadro={"rd-hepato": {"feito": True, "ts": "t"}})
    assert qd["na_espera"] == {"oculto": False, "html": "Carregando…"} and qd["feito_na_espera"] is False
    assert qd["depois"]["oculto"] is True and qd["feito"] is True and qd["estado"] == "viva"
    assert qd["esperas"] == [1000] and qd["avisos"] == [["[hub] leitura quadro falhou", "unavailable", 1]]
    assert qd["ativos"] == {"quadro": 1}


def test_botao_tentar_de_novo_reassina():
    """`leitura=0`: 1 + 3 tentativas (1 s, 2 s, 4 s) e a aba mostra a falha com "Tentar de novo"; com o
    banco de volta, o toque carrega. Reabrir a aba com a assinatura morta tambem reassina."""
    acao = r"""
  iniciarQuestoes(); await dormir(1000);
  SAIDA.morta = $("qz-listas").innerHTML; SAIDA.estado_morta = QZ.subListas.estado(); SAIDA.iniciado_morta = QZ.iniciado;
  bancoBom(); clicar("[data-retentar]"); await dormir(50);
  SAIDA.depois_botao = $("qz-listas").innerHTML; SAIDA.estado = QZ.subListas.estado();
"""
    out = _rodar_qz_leitura(acao, {"listas": 99})
    assert "Não consegui ler as listas." in out["morta"] and 'data-retentar="listas"' in out["morta"]
    assert 'class="primario hub-retentar"' in out["morta"] and ">Tentar de novo</button>" in out["morta"]
    assert out["estado_morta"] == "morta" and out["iniciado_morta"] is False
    assert out["esperas"] == [1000, 2000, 4000]
    assert [a[2] for a in out["avisos"]] == [1, 2, 3, 4] and all(a[:2] == ["[hub] leitura listas falhou", "unavailable"] for a in out["avisos"])
    assert out["depois_botao"] == "LISTAS t49,t26" and out["estado"] == "viva"
    assert out["ativos"] == {"listas": 1} and out["assinaturas"] == {"listas": 5}

    # reabrir a aba (ir("questoes") -> iniciarQuestoes) com a assinatura morta: reassina, mostra "Carregando…"
    reabrir = r"""
  iniciarQuestoes(); await dormir(1000); bancoBom();
  iniciarQuestoes(); SAIDA.na_hora = $("qz-listas").innerHTML; await dormir(50);
  SAIDA.depois = $("qz-listas").innerHTML;
"""
    out2 = _rodar_qz_leitura(reabrir, {"listas": 99})
    assert "Carregando as listas" in out2["na_hora"] and out2["depois"] == "LISTAS t49,t26"
    assert out2["ativos"] == {"listas": 1}

    # a Teoria: morta = aviso com o botao; o botao (quadroRetentar) reassina; reabrir a aba usa o mesmo caminho
    acao_qd = r"""
  await dormir(1000);
  SAIDA.morta = aviso(); SAIDA.estado_morta = quadroLeitura.estado();
  bancoBom(); quadroRetentar(); SAIDA.na_hora = aviso(); await dormir(50);
  SAIDA.depois = aviso(); SAIDA.feito = feitoEm("rd-hepato"); SAIDA.estado = quadroLeitura.estado();
"""
    qd = _rodar_quadro_leitura(acao_qd, {"quadro": 99}, quadro={"rd-hepato": {"feito": True, "ts": "t"}})
    assert qd["estado_morta"] == "morta" and 'data-retentar="quadro"' in qd["morta"]["html"]
    assert qd["na_hora"]["html"] == "Carregando…" and qd["depois"]["oculto"] is True
    assert qd["feito"] is True and qd["estado"] == "viva" and qd["ativos"] == {"quadro": 1}
    assert 'if(aba === "aulas" && quadroLeitura && quadroLeitura.estado() === "morta"){ quadroRetentar(); }' in TEMPLATE


def test_leituras_das_abas_passam_pela_assinatura_resiliente():
    """DoD 1: as cinco leituras (listas, quadro, questoes/respostas/analises da lista aberta) passam por UMA
    funcao -- nenhum `.onSnapshot(` direto nelas; o `qzLimpar` para as da lista aberta (timer incluso)."""
    assert TEMPLATE.count("function assinarResiliente(") == 1
    ini = extrair_funcao(TEMPLATE, "function iniciarQuestoes(){")
    qd = extrair_funcao(TEMPLATE, "function iniciarQuadro(){")
    abrir = extrair_funcao(TEMPLATE, "function qzAbrir(id){")
    assert "onSnapshot" not in ini and "assinarResiliente(" in ini and 'collection("listas")' in ini
    assert ".onSnapshot(" not in qd and 'assinarResiliente(function(db){ return db.collection("quadro"); }' in qd
    assert "onSnapshot" not in abrir
    assert [c for c in ("questoes", "respostas", "analises") if 'qzAssinarLista("%s", id,' % c in abrir] == \
        ["questoes", "respostas", "analises"]
    assert "Recarregue a página" not in TEMPLATE
    assert "QZ.unsubs.push(h.parar)" in extrair_funcao(TEMPLATE, "function qzAssinarLista(col, id, onDados){")


# s226 (sprint-final-uerj part-1): a v108 publicada com a pagina aberta deixou as Listas em "Nao consegui ler"
# ate ele sair do artifact e voltar -- as 3 tentativas reusavam a conexao morta. O banco falso daqui imita o
# `leitura=conexao` do ui_harness: a 1a conexao (`use("db")` no. 1) falha em toda leitura; a 2a funciona.
CONEXAO_JS = r"""
var USOS_DB = 0, _dbBom = DB;
var DB_MORTO = {collection: function(c){ var q = consultaFalsa(c, function(){ return []; }); var on = q.onSnapshot;
  q.onSnapshot = function(ok, erro){ FALHAS[c] = 1; return on(ok, erro); }; q.doc = function(){ return {set: function(){ return Promise.reject({code: "unavailable"}); }}; };
  return q; }};
window.claude.use = function(){ USOS_DB++; return Promise.resolve(USOS_DB === 1 ? DB_MORTO : _dbBom); };
"""


def test_retentativa_pede_conexao_nova():
    """DoD 1-3: a 1a tentativa usa o `db` de quem assinou; da 2a em diante a assinatura pede `use("db")` de
    novo, a consulta recebe o `db` novo e o `QZ.db` passa a ser ele -- as Listas e a Teoria carregam sem
    recarregar, com 2 chamadas a `use("db")` (a da aba + a da reconexao) e um ouvinte so."""
    acao = r"""
  iniciarQuestoes(); await dormir(50);
  SAIDA.morto_antes = QZ.db === DB_MORTO;
  await dormir(200);
  SAIDA.depois = $("qz-listas").innerHTML; SAIDA.estado = QZ.subListas.estado();
  SAIDA.qz_db_novo = QZ.db === _dbBom; SAIDA.usos = USOS_DB;
"""
    prog = (HARNESS_QZ_LEITURA.replace("__FUNCS__", QZ_LEITURA_JS + chr(10) + CONEXAO_JS)
            .replace("__FALHAS__", json.dumps({})).replace("__ACAO__", acao))
    out = _node(prog)
    assert out["morto_antes"] is True, "a 1a tentativa usa o db obtido pela aba"
    assert out["depois"] == "LISTAS t49,t26" and out["estado"] == "viva"
    assert out["qz_db_novo"] is True, "a gravacao de respostas usa o db da reconexao"
    assert out["usos"] == 2 and out["esperas"] == [1000]
    assert out["avisos"] == [["[hub] leitura listas falhou", "unavailable", 1]]
    assert out["ativos"] == {"listas": 1}

    # a Teoria: o mesmo caminho; o db de `iniciarQuadro` e o morto, o da 2a tentativa o bom
    acao_qd = r"""
  await dormir(250);
  SAIDA.depois = aviso(); SAIDA.feito = feitoEm("rd-hepato"); SAIDA.estado = quadroLeitura.estado(); SAIDA.usos = USOS_DB;
"""
    qd = _rodar_quadro_leitura(acao_qd, {}, quadro={"rd-hepato": {"feito": True, "ts": "t"}}, conexao=CONEXAO_JS)
    assert qd["depois"]["oculto"] is True and qd["feito"] is True and qd["estado"] == "viva"
    assert qd["usos"] == 2 and qd["ativos"] == {"quadro": 1}

    # a forma: os chamadores montam a consulta sobre o db RECEBIDO, nunca o capturado -- os 4 das abas e,
    # desde a s227, os 3 do "+K" do Painel (notas do lote, listas, respostas de cada lista)
    assert TEMPLATE.count("assinarResiliente(function(db){ return db.collection(") == 7
    assert "assinarResiliente(function(){" not in TEMPLATE and "QZ.db.collection(col)" not in TEMPLATE
    assert TEMPLATE.count("aoReconectar: function(novo){ QZ.db = novo; }") == 2


def test_ao_vivo_do_painel_sobrevive_a_conexao_morta():
    """s227 (relato dele, 13/10: "eu ja fiz questões. por que elas não estão aparecendo no painel?"): o hub
    republicado com a pagina aberta mata a conexao do `db` -- as leituras do `painelVivo` engoliam o erro e o
    "+11" das questoes de hoje ficava em 0, calado (o mesmo A18 da v108). Com `leitura=conexao` (a 1a conexao,
    a que o `painelListas` entrega, falha em TODA leitura) o "+K" das questoes e dos cards aparece pela
    retentativa com conexao nova; com o banco morto de vez, fica o publicado, sem botao e sem quebrar."""
    out = _rodar_vivo(colecoes=COLECOES_VIVO, conexao=CONEXAO_JS, acao=ACAO_VIVO_CONEXAO, esperaMs=400)
    assert out["cards"] == {"b": "64", "base": "62", "mais": "2", "title": "2 desde o publish"}
    assert out["questoes"] == {"b": "33", "base": "30", "mais": "3", "title": "3 desde o publish"}
    assert out["escritas"] == [], "o Painel nunca grava"
    assert out["usos"] == 3, "o do painelListas + uma reconexao por leitura que caiu (notas, listas)"
    assert out["esperas"] == [1000, 1000]
    assert sorted(a[0] for a in out["avisos"]) == ["[hub] leitura listas do painel falhou",
                                                   "[hub] leitura notas do painel falhou"]
    assert all(a[1:] == ["unavailable", 1] for a in out["avisos"]), "o console.warn com o codigo e a tentativa"
    # o banco morto de vez: 1 + 3 tentativas por leitura, o publicado fica, nenhum "Tentar de novo" no Painel
    morta = CONEXAO_JS + 'window.claude.use = function(){ USOS_DB++; return Promise.resolve(DB_MORTO); };\n'
    fim = _rodar_vivo(colecoes=COLECOES_VIVO, conexao=morta, acao=ACAO_VIVO_CONEXAO, esperaMs=1200)
    assert fim["cards"]["mais"] is None and fim["questoes"]["mais"] is None and fim["cards"]["b"] == "62"
    assert sorted(fim["esperas"]) == [1000, 1000, 2000, 2000, 4000, 4000]
    assert sorted(a[2] for a in fim["avisos"]) == [1, 1, 2, 2, 3, 3, 4, 4]
    assert "Tentar de novo" not in fim["texto"]
    # a forma: nenhuma leitura direta sobrou no painelVivo
    corpo = _funcs("function painelVivo(doc, db){")
    assert ".onSnapshot(" not in corpo and corpo.count("assinarResiliente(") == 3
    assert "aoMorrer" not in corpo, "sem botao no Painel: esgotadas, fica o publicado"


def test_chip_da_lista_so_fora_do_normal():
    """DoD 4 (A21): "pronta" (capturada) sem chip; em curso = respondidas/total do espelho do aparelho;
    resolvida segue com o check (CSS)."""
    acao = r"""
SAIDA.chips = {pronta: qzChip({_id: "t1", status: "capturada", q: 21}),
  em_curso: qzChip({_id: "t68", status: "capturada", q: 21}),
  resolvendo: qzChip({_id: "t2", status: "resolvendo", q: 10}),
  resolvida: qzChip({_id: "t3", status: "resolvida", q: 19}),
  sem_status: qzChip({_id: "t4", q: 5})};
SAIDA.html = $("qz-listas").innerHTML;"""
    out = _rodar_listas(acao, ls={"medhub.respostas.t68": json.dumps({"1": {"letra": "A"}, "2": {"letra": "B"}})})
    c = out["chips"]
    assert c["pronta"] == "" and c["sem_status"] == ""
    assert c["em_curso"] == '<span class="qz-chip resolvendo">em curso 2/21</span>'
    assert c["resolvendo"] == '<span class="qz-chip resolvendo">em curso</span>'
    assert c["resolvida"] == '<span class="qz-chip resolvida">resolvida</span>'
    assert "pronta" not in out["html"] and "em curso 2/21" in out["html"]
    assert ".qz-chip.resolvida::before{content:\"\\2713\\00A0\"}" in TEMPLATE
    assert re.search(r"\.hub-marca\{[^}]*font-size:1\.375rem", TEMPLATE)
    assert ".hub-marca span{color:var(--acento)}" in TEMPLATE   # s226: "Hub" no azul da paleta (pedido dele)


# ---------------------------------------------------------------------------------------------------
# s226 (hub-correcoes-pos-tema-v3 part-2): a aba Cards mostra o contador do Painel ("N de T hoje"), com
# N = consumo_hoje + a MESMA conta do `vivoCards`; a fila do lote vem como 2o numero, menor; lote de dia
# anterior ao do aparelho ganha 1 aviso acima do 1o card e segue drenavel.
# ---------------------------------------------------------------------------------------------------

CARDS_DIA = _funcs("function vivoDia(t){", "function vivoCards(notas, lote, sessaoGravada){",
                   "function loteNoAr(){", "function cardsDia(){", "function cardsContador(dia, notas, lote){",
                   "function cardsDiaDoLote(iso){", "function cardsAvisoFila(lote, hojeLocal){",
                   "function cardsPintar(notas){")

DOM_CARDS = r"""
var els = {};
function $(id){ return els[id] || null; }
function el(id, txt){ var cl = {}; els[id] = {id: id, hidden: false, textContent: txt || "",
  classList: {add: function(c){ cl[c] = 1; }, has: function(c){ return !!cl[c]; }}}; return els[id]; }
var metros = el("metros");
["dia-n", "dia-t", "metro-lote", "aviso-fila"].forEach(function(i){ el(i); });
el("dia-contador").hidden = true; els["dia-contador"].parentNode = metros; els["aviso-fila"].hidden = true;
el("lote", __LOTE__); el("hub-dia", __DIA__);
"""


def _rodar_cards(lote, dia, notas):
    prog = (DOM_CARDS.replace("__LOTE__", json.dumps(json.dumps(lote)))
            .replace("__DIA__", json.dumps(json.dumps(dia))) + CARDS_DIA + """
cardsPintar(%s);
console.log(JSON.stringify({n: $("dia-n").textContent, t: $("dia-t").textContent, visivel: !$("dia-contador").hidden,
  lote_oculto: $("metro-lote").hidden, menor: $("metros").classList.has("com-dia"),
  aviso: $("aviso-fila").hidden ? null : $("aviso-fila").textContent}));""" % json.dumps(notas))
    return _node(prog)


def _hoje_iso(delta=0):
    from datetime import timedelta
    return (date.today() + timedelta(days=delta)).isoformat()


def test_cards_e_painel_mostram_o_mesmo_contador():
    """DoD 1: o numero da aba = o do Painel com o "+K" ao vivo (base + vivoCards), lido do MESMO dado
    (`hub.dia_do_painel` do HTML do painel); lote ja gravado (o `consumo_hoje` ja o inclui) soma 0."""
    notas = list(COLECOES_VIVO["sessoes/2026-10-05b/notas"].values())
    dia = hub.dia_do_painel(_painel_vivo_html("2026-10-05a"), date(2026, 10, 5))
    assert (dia["consumo_hoje"], dia["teto"], dia["sessao_gravada"]) == (62, 100, "2026-10-05a")
    lote = {"sessao": "2026-10-05b", "gerado_em": _hoje_iso() + "T06:00:00", "cards": [{"card_id": 1}]}
    out = _rodar_cards(lote, dia, notas)
    painel = _rodar_vivo(colecoes=COLECOES_VIVO)["cards"]                 # o Painel: 62 com "+2"
    assert int(out["n"]) == int(painel["b"]) == int(painel["base"]) + int(painel["mais"]) == 64
    assert out["t"] == "100" and out["visivel"] and out["lote_oculto"] and out["menor"]
    gravado = _rodar_cards(dict(lote, sessao="2026-10-05a"), dia, notas)
    assert gravado["n"] == "62", "lote ja gravado: o consumo_hoje do build ja traz as notas dele"
    sem = _rodar_cards(lote, None, notas)
    assert not sem["visivel"] and not sem["lote_oculto"], "sem o contador do Painel: a aba e a do lote"
    # o cabecalho: o contador e o numero; a fila segue visivel, com rotulo menor (DoD 2)
    player = (ROOT / "core" / "templates" / "player.html").read_text(encoding="utf-8")
    assert '<span class="metro dia" id="dia-contador" hidden><b id="dia-n">0</b> de <span id="dia-t">0</span> hoje</span>' in player
    assert '<span class="metro fila">fila <b id="pendentes">0</b></span>' in player
    assert re.search(r"\.com-dia \.metro\.fila\{font-size:var\(--fs-meta\)\}", player)
    assert "iniciarCardsDia();" in TEMPLATE and 'assinarResiliente(function(db){ return db.collection("sessoes/" + lote.sessao + "/notas"); }' in TEMPLATE


def test_fila_de_outro_dia_avisa_e_segue_drenavel():
    """DoD 3: lote com `gerado_em` de ontem = aviso unico "Fila de DD/MM -- a de hoje ainda nao saiu.";
    de hoje (ou a de vespera, amanha) = sem aviso. O aviso so pinta: a fila do player nao muda."""
    ontem = _hoje_iso(-1)
    rot = "Fila de %s/%s -- a de hoje ainda não saiu." % (ontem[8:10], ontem[5:7])
    lote = {"sessao": "x", "gerado_em": ontem + "T21:40:00", "cards": [{"card_id": 1}, {"card_id": 2}]}
    dia = {"data": ontem, "consumo_hoje": 3, "teto": 150, "sessao_gravada": ""}
    assert _rodar_cards(lote, dia, [])["aviso"] == rot
    assert _rodar_cards(dict(lote, gerado_em=_hoje_iso() + "T01:17:20"), dia, [])["aviso"] is None
    assert _rodar_cards(dict(lote, gerado_em=_hoje_iso(1) + "T06:00:00"), dia, [])["aviso"] is None
    assert _rodar_cards(dict(lote, cards=[]), dia, [])["aviso"] is None, "lote vazio: nada a drenar, sem aviso"
    assert _rodar_cards(lote, None, [])["aviso"] == rot, "o aviso nao depende do contador"
    player = (ROOT / "core" / "templates" / "player.html").read_text(encoding="utf-8")
    corpo = player[player.index("<!-- @player:corpo:inicio -->"):player.index('<main id="drill">')]
    assert corpo.count('id="aviso-fila"') == 1, "um aviso so, acima do 1o card"
    assert "aviso-fila" not in player[player.index("<!-- @player:js:inicio -->"):], \
        "o player nao le o aviso: a fila e a gravacao sao as de sempre (nota com o ts de hoje)"


# ======================================================================== s227: hub-tema-v4 parts 6 e 7
# Pedido dele sobre a Version 113 (13/10/2026): "o destaque nao fica mais em rosa ou ciano, mas no amarelo antigo.
# Seria ate interessante se desse para ter as 3 cores [...] o destaque esta mudando a cor do texto e ele poderia
# apenas manter a cor do texto e mudar o fundo dele [...] nos resumos, favor remover todos os 'Fonte:...' espalhados
# pelo texto, e concentra-los ao final, tal como um artigo." Specs `.vibeflow/specs/hub-tema-v4-part-6.md` (UMA cor
# ativa trocavel, rosa por padrao, decidido por ele) e `hub-tema-v4-part-7.md` (Referencias no leitor). A parte de
# DOM real da part 7 (Range, querySelector, estilo computado) roda no Edge headless; sem Edge, PULADA (declarado).

def _topo():
    return TEMPLATE[TEMPLATE.index('<header class="hub-topo">'):TEMPLATE.index("</header>")]


def test_seletor_da_cor_do_grifo_e_um_botao_unico_so_no_leitor_da_teoria():
    """s228 (pedido dele: "sobretudo em um botao que apareca so dentro do bloco de teoria, e que seja um botao unico,
    que quando clicamos ele expande em cascata com as 3 opcoes"): fora do topo; DENTRO da barra do leitor da Teoria um
    botao (aria-expanded/aria-controls, 44 px) que abre o grupo das tres cores (rosa, ciano, amarelo, nome acessivel,
    a ativa por aria-pressed + contorno); a cascata e um atraso por botao; cor so por token; nada sticky/fixed.
    ⚰️ *s227 (part 6): tres amostras no topo do hub, a direita da marca.*"""
    assert 'id="hub-grifo' not in _topo(), "saiu do topo"
    i = TEMPLATE.index('<div id="hub-leitor" hidden>')
    barra = TEMPLATE[i:TEMPLATE.index('id="hub-leitor-aviso"', i)]
    assert barra.index('id="hub-leitor-titulo"') < barra.index('id="hub-grifo-btn"') < barra.index('id="hub-grifo-cor"')
    # s229 (pedido dele, 15/10): o MESMO botao tambem na barra da questao (Listas) -- dois widgets, uma cor ativa
    assert TEMPLATE.count('id="hub-grifo-btn"') == 1 and TEMPLATE.count('data-cor="rosa" aria-pressed') == 2
    j = TEMPLATE.index('<div id="qz-player" hidden>')
    barra_q = TEMPLATE[j:TEMPLATE.index('id="qz-relogio"', j)]
    assert barra_q.index('id="qz-tema"') < barra_q.index('<div class="hub-grifo" id="qz-grifo" data-aberto="false">') \
        < barra_q.index('aria-controls="qz-grifo-cor"')
    assert 'aria-expanded="false" aria-controls="hub-grifo-cor"' in barra
    grupo = re.search(r'<div class="hub-grifo-cor" id="hub-grifo-cor" role="group" aria-label="Cor do próximo grifo">(.*?)</div>', barra, re.S)
    assert grupo, "o grupo com o nome acessivel"
    botoes = re.findall(r'<button type="button" data-cor="(\w+)" aria-pressed="(true|false)" aria-label="(\w+)"', grupo.group(1))
    assert botoes == [("rosa", "true", "Rosa"), ("ciano", "false", "Ciano"), ("amarelo", "false", "Amarelo")]
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    assert ".hub-grifo-cor button{min-width:44px;min-height:44px;" in css and "min-height:44px" in css.split(".hub-grifo-btn{", 1)[1].split("}", 1)[0]
    assert '.hub-grifo-cor button[aria-pressed="true"]{border-color:var(--acento)}' in css
    assert '.hub-grifo[data-aberto="true"] .hub-grifo-cor button:nth-child(3){transition-delay:120ms}' in css, "a cascata"
    for cor in ("rosa", "ciano", "amarelo"):
        assert '.hub-grifo-cor button[data-cor="%s"] .hub-grifo-am{background:var(--grifo-%s)}' % (cor, cor) in css
    for l in [l for l in css.splitlines() if "hub-grifo" in l and "{" in l]:
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|sticky|fixed|nowrap", l), l
    js = TEMPLATE[TEMPLATE.index("// ------------------------------------------------ cor do grifo"):]
    js = js[:js.index("// ------------------------------------------------ secoes recolhiveis")]
    assert 'GRIFO_COR_CHAVE = "medhub.grifo"' in js and "grifoCorAplicar(grifoCorLer(), false);" in js
    assert "try{ localStorage.setItem(GRIFO_COR_CHAVE, cor); }catch(e){}" in js
    assert 'e.key === "Escape"' in js and "grifoMenu(false, id)" in js
    assert 'var GRIFO_WIDGETS = ["hub-grifo", "qz-grifo"];' in js


COR_GRIFO_JS = r"""
var LS = __LS__, LANCA = __LANCA__;
var localStorage = {getItem: function(k){ if(LANCA){ throw new Error("bloqueado"); } return Object.prototype.hasOwnProperty.call(LS, k) ? LS[k] : null; },
  setItem: function(k, v){ if(LANCA){ throw new Error("bloqueado"); } LS[k] = String(v); }};
var attrs = {}, docAttrs = {};
var raiz = {setAttribute: function(k, v){ attrs[k] = v; }, getAttribute: function(k){ return Object.prototype.hasOwnProperty.call(attrs, k) ? attrs[k] : null; }};
function botao(c){ var a = {"data-cor": c, "aria-pressed": "?"}; return {a: a, getAttribute: function(k){ return a[k]; }, setAttribute: function(k, v){ a[k] = v; }}; }
var BOTOES = ["rosa", "ciano", "amarelo"].map(botao), caixa = {querySelectorAll: function(){ return BOTOES; }};
var VALOR = {rosa: "color-mix(in srgb,#FF4FA3 32%,transparent)", ciano: "color-mix(in srgb,#00D9E8 32%,transparent)",
             amarelo: "color-mix(in srgb,#FFD447 32%,transparent)"};
var window = {getComputedStyle: function(){ return {getPropertyValue: function(p){ var c = p.replace("--grifo-", ""); return VALOR[c] ? " " + VALOR[c] : ""; }}; }};
var estilo = __COM_ESTILO__ ? {id: "hub-grifo-estilo", textContent: "mark.hub-grifo{background:velho}"} : null;
var docLeitor = {head: {appendChild: function(s){ estilo = s; }}, documentElement: {setAttribute: function(k, v){ docAttrs[k] = v; }},
  getElementById: function(id){ return id === "hub-grifo-estilo" ? estilo : null; }, createElement: function(){ return {}; }};
function $(id){ return id === "hub-grifo-cor" ? caixa : (id === "hub-leitor-quadro" ? {contentDocument: docLeitor} : null); }
function foto(){ return {attr: attrs["data-grifo"], pressed: BOTOES.map(function(b){ return b.a["aria-pressed"]; }).join(","),
  ls: LANCA ? null : (LS["medhub.grifo"] || null), estilo: estilo ? estilo.textContent : null, doc: docAttrs["data-grifo"] || null}; }
var lida = grifoCorLer(); grifoCorAplicar(lida, false); var antes = foto();
if(__COM_ESTILO__){ grifoEstilo(docLeitor); } var pintado = estilo ? estilo.textContent : null;
grifoCorAplicar("ciano", true); var depois = foto();
console.log(JSON.stringify({lida: lida, antes: antes, depois: depois, pintado: pintado}));
"""


def _cor_grifo(ls=None, lanca=False, com_estilo=True):
    prog = "\n".join([_var("GRIFO_CORES"), _var("GRIFO_WIDGETS")] + [extrair_funcao(TEMPLATE, a) for a in (
        "function grifoCorValida(c){", "function grifoCorLer(){", "function grifoCorAplicar(cor, gravar){", "function grifoEstilo(doc){")])
    return _node(prog + COR_GRIFO_JS.replace("__LS__", json.dumps(ls or {})).replace("__LANCA__", json.dumps(lanca))
                 .replace("__COM_ESTILO__", json.dumps(com_estilo)))


def test_cor_do_grifo_padrao_rosa_o_aparelho_lembra_e_a_troca_nao_repinta():
    """s227 part 6 + s228: sem nada no aparelho (ou valor invalido, ou storage bloqueado) = rosa; o aparelho lembra a
    escolha; a troca grava `data-grifo` no <html> do shell e marca o botao (aria-pressed), mas NAO reescreve o estilo
    do documento aberto (s228: so os proximos grifos mudam). O estilo do leitor tem uma regra por cor."""
    vazio = _cor_grifo()
    assert vazio["lida"] == "rosa" and vazio["antes"]["attr"] == "rosa" and vazio["antes"]["pressed"] == "true,false,false"
    assert vazio["antes"]["ls"] is None, "abrir nao grava: so o toque grava"
    assert vazio["depois"]["attr"] == "ciano" and vazio["depois"]["pressed"] == "false,true,false" and vazio["depois"]["ls"] == "ciano"
    assert vazio["depois"]["estilo"] == vazio["pintado"], "trocar a cor nao repinta o que ja existe"
    est = vazio["pintado"]
    assert "mark.hub-grifo{background:color-mix(in srgb,#FF4FA3 32%,transparent);color:inherit;" in est
    assert 'mark.hub-grifo[data-cor="ciano"]{background:color-mix(in srgb,#00D9E8 32%,transparent)}' in est
    assert 'mark.hub-grifo[data-cor="amarelo"]{background:color-mix(in srgb,#FFD447 32%,transparent)}' in est
    assert _cor_grifo({"medhub.grifo": "amarelo"})["antes"]["attr"] == "amarelo", "o aparelho lembra"
    assert _cor_grifo({"medhub.grifo": "verde"})["lida"] == "rosa", "valor fora das tres = rosa"
    bloqueado = _cor_grifo(lanca=True)
    assert bloqueado["lida"] == "rosa" and bloqueado["depois"]["attr"] == "ciano", "sem armazenamento: troca na tela, nao lembra"


def test_cada_grifo_guarda_a_cor_com_que_nasceu():
    """s228 (pedido dele: "alterando apenas a cor dos proximos grifos, e nao todos"): o grifo nasce com a cor ativa e a
    guarda no registro (`cor`, so quando nao e rosa: o formato salvo de antes segue valido e fica rosa); a pintura usa a
    cor do grifo (data-cor), nunca a ativa; as questoes, sem o seletor, ficam no rosa padrao."""
    cap = extrair_funcao(TEMPLATE, "function grifoCapturar(ctx){")
    assert 'grifoCorValida(raiz.getAttribute("data-grifo"))' in cap and "novo.cor = cor" in cap
    assert "if(g.cor){ x.cor = g.cor; }" in extrair_funcao(TEMPLATE, "function grifoSalvar(slug, grifos){")
    assert 'if(g.cor){ mk.setAttribute("data-cor", g.cor); }' in extrair_funcao(TEMPLATE, "function grifoPintar(ctx){")
    for assinatura in ("function grifoEnviar(slug){", "function qzGrifosSalvar(q, g){", "function qzGrifoHtml(texto, intervalos){"):
        assert not re.search(r"data-grifo|GRIFO_COR|medhub\.grifo\b", extrair_funcao(TEMPLATE, assinatura)), assinatura
    textos = ["PEEP alta e FiO2 baixa", "outro bloco"]
    lista = [{"b": 0, "ini": 0, "fim": 4, "txt": "PEEP"},                       # antigo, sem cor = rosa
             {"b": 0, "ini": 2, "fim": 9, "txt": "EP alta", "cor": "ciano"},    # sobrepoe, outra cor: nao funde
             {"b": 0, "ini": 12, "fim": 16, "txt": "FiO2", "cor": "ciano"},
             {"b": 0, "ini": 14, "fim": 22, "txt": "O2 baixa", "cor": "ciano"},  # mesma cor: funde
             {"b": 1, "ini": 0, "fim": 5, "txt": "outro", "cor": "verde"}]       # cor invalida = rosa
    out = _puras("grifoNormalizar(%s, %s)" % (json.dumps(textos), json.dumps(lista)))
    assert out == [{"b": 0, "ini": 0, "fim": 4, "txt": "PEEP"},
                   {"b": 0, "ini": 2, "fim": 9, "txt": "EP alta", "cor": "ciano"},
                   {"b": 0, "ini": 12, "fim": 22, "txt": "FiO2 baixa", "cor": "ciano"},
                   {"b": 1, "ini": 0, "fim": 5, "txt": "outro"}], out


# ------------------------------------------------------------------ part 7: Referencias no fim (leitor)
REF_VARS = ("REF_PREFIXO", "REF_FIM", "REF_SINAL", "REF_SIGLA", "REF_BASE", "REF_EXT_SIGLA", "REF_EXT_PALAVRA",
            "REF_CANDIDATO", "REF_FORA", "REF_BLOCO", "REF_NAO_DESCE", "GRIFO_BLOCO")
REF_FUNCS = ("function grifoTextos(bloco){", "function grifoBlocos(doc){", "function grifoValido(g){",
             "function grifoResolver(textos, g){", "function grifoResolverPos(textos, g, t){", "function ehReferencia(texto){", "function ehBaseInterna(texto){",
             "function refChave(texto){", "function refTirarPrefixo(no){", "function refPodarFim(no){",
             "function refFimDe(el){", "function refAnterior(el){", "function refsAchar(doc){",
             "function refSup(doc, n, id){", "function refsMontar(doc){")


def _refs_js():
    return "\n".join(_var(v) for v in REF_VARS) + "\n" + "\n".join(extrair_funcao(TEMPLATE, a) for a in REF_FUNCS)


def test_eh_referencia_separa_fonte_bibliografica_de_conteudo_clinico():
    """Part 7 (correcao do principal): "Fonte:" tambem e CONTEUDO -- a fonte do sangramento no TCE fica. So move o que
    tem cara de referencia; a base interna (resumo, verso de card, apostila, PDF do curso) vai para a linha da base."""
    casos = {
        "arterial em cerca de 85% dos casos -- classicamente a artéria meníngea média, lesada por fratura do osso "
        "temporal (a escama temporal é a região mais fina da calota).": [False, False],
        "venosa -- ruptura das veias-ponte que atravessam o espaço subdural.": [False, False],
        "Apostila Estratégia MED -- Prof. Alexandre Melitto (2024)": [True, True],
        "resumos/Cirurgia/30. Complicações Pós-Operatórias.pdf (febre pós-operatória; íleo)": [True, True],
        "verso dos cards 1778 e 1779 + PDF EMED resumos/Cirurgia/19. Vesícula.pdf": [True, True],
        "verso do card (sem resumo local)": [True, True],
        "R1 Cirurgia/3. Doenças da Coluna Vertebral.pdf (Cir/3) e Cirurgia/Coluna.md": [True, True],
        "MS/Fiocruz-IFF, Portal de Boas Práticas (2023, selo MS) + FEBRASGO Protocolo nº 8 (2018).": [True, False],
        "PMID 42366997, DOI 10.1161/CIR.0000000000001455.": [True, False],
        "SBC. Diretriz Brasileira de Insuficiência Cardíaca, 2023": [True, False],
        "carne vermelha, feijão e folhas verdes": [False, False],
    }
    prog = _refs_js() + "\nvar C = %s, o = {}; Object.keys(C).forEach(function(k){ o[k] = [ehReferencia(k), ehBaseInterna(k)]; });" \
        "console.log(JSON.stringify(o));" % json.dumps(casos, ensure_ascii=False)
    assert _node(prog) == casos
    # a regra e uma funcao pura com nome (o linter dos resumos replica): nada de DOM dentro dela
    for a in ("function ehReferencia(texto){", "function ehBaseInterna(texto){"):
        assert "doc" not in extrair_funcao(TEMPLATE, a)


def test_preparar_monta_as_referencias_antes_da_fonte_dos_atalhos_e_do_grifo_sem_poder_derrubar():
    """Part 7 DoD 1 e 3: so no quadro do leitor, ANTES do fonteLigar (que liga o resumos/X.md dentro da lista), do
    laco das ancoras (o sobrescrito rola ate a referencia) e do grifoLigar; num try/catch, como o fonteLigar."""
    corpo = extrair_funcao(TEMPLATE, "function preparar(quadro){")
    liga = 'if(quadro.id === "hub-leitor-quadro"){ try{ refsMontar(doc); }catch(e){} }'
    assert corpo.count("refsMontar(") == 1 and liga in corpo
    assert corpo.index(liga) < corpo.index("fonteLigar(doc)") < corpo.index('querySelectorAll("a[href]")') < corpo.index("grifoLigar(doc")


def test_tema_aula_estiliza_as_duas_familias_de_referencias_com_a_mesma_regra():
    """Part 7 DoD 5 + complemento do principal: sobrescrito pequeno em ciano de link; secao com filete em cima, titulo
    no peso das secoes, lista em legenda lavanda; a base em meta; a familia do leitor (.hub-ref, section.hub-refs,
    .hub-base) e a da aula nova (sup.ref, section.refs, p.base) no MESMO seletor; cor so por token."""
    aula = (ROOT / "core" / "templates" / "tema-aula.css").read_text(encoding="utf-8")
    assert re.search(r"\nsup\.hub-ref,sup\.ref\{font-size:\.7em;[^}]*vertical-align:super", aula)
    assert "sup.hub-ref a,sup.ref a{color:var(--teal-ink);" in aula
    assert re.search(r"\nsection\.hub-refs,section\.refs\{[^}]*border-top:1px solid var\(--line\)", aula)
    assert re.search(r"\nsection\.hub-refs ol,section\.refs ol\{[^}]*font-size:var\(--fs-legenda\)[^}]*color:var\(--ink2\)", aula)
    assert re.search(r"\n\.hub-base,p\.base\{[^}]*font-size:var\(--fs-meta\)[^}]*color:var\(--ink3\)", aula)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|sticky|fixed|nowrap", aula)


def _edge_rodar(js_do_teste, nome):
    """Roda `js_do_teste` (que preenche SAIDA e chama fim()) numa pagina local no Edge headless e devolve SAIDA."""
    from tools import ui_capturas as uc
    edge = uc.achar_edge()
    if not edge:
        pytest.skip("Edge ausente: a transformacao das Referencias no DOM real nao foi verificada (skip declarado)")
    pasta = Path(tempfile.mkdtemp(prefix="medhub_refs_"))
    pagina = pasta / ("%s.html" % nome)
    pagina.write_text("""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><pre id="saida"></pre><script>
var SAIDA = {};
function fim(){ document.getElementById("saida").textContent = JSON.stringify(SAIDA).replace(/[\\u007f-\\uffff]/g,
  function(c){ return "\\\\u" + ("000" + c.charCodeAt(0).toString(16)).slice(-4); }); }
function carregar(html){ return new Promise(function(ok){ var f = document.createElement("iframe"); f.style.width = "390px";
  f.srcdoc = html; f.onload = function(){ ok(f.contentDocument); }; document.body.appendChild(f); }); }   // srcdoc ANTES de entrar: o 1o load e o dele
function txt(el){ return el ? el.textContent.replace(/\\s+/g, " ").trim() : null; }
function fontesFora(d){ var out = [], w = d.createTreeWalker(d.body, 4), t;
  while((t = w.nextNode())){ if(/Fontes?\\s*:/.test(t.data) && !t.parentElement.closest("section.hub-refs, section.refs, p.base")){
    out.push(txt(t.parentElement.closest("p, li, div, figcaption, blockquote, td") || t.parentElement)); } }
  return out; }
%s
%s
</script></body></html>""" % (_refs_js(), js_do_teste), encoding="utf-8")
    perfil = tempfile.mkdtemp(prefix="medhub_edge_")
    try:
        r = subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                            "--disable-extensions", "--user-data-dir=%s" % perfil, "--virtual-time-budget=8000",
                            "--dump-dom", pagina.as_uri()], capture_output=True, timeout=120)
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
        shutil.rmtree(pasta, ignore_errors=True)
    m = re.search(r'<pre id="saida">(.*?)</pre>', r.stdout.decode("utf-8", "replace"), re.S)
    assert m and m.group(1).strip(), "a pagina de teste nao terminou: %s" % r.stderr.decode("utf-8", "replace")[-400:]
    import html as _html
    return json.loads(_html.unescape(m.group(1)))


DOC_REFS = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><style>.esc li{display:grid;grid-template-columns:auto 1fr}</style></head><body><div class="wrap">
<section class="sec"><h2>Um</h2>
  <p id="a">A principal fonte de ferro na dieta é a carne. Fonte de calor alta.</p>
  <ol class="esc"><li id="passo"><span class="n">1</span><span>Passo um da escada.</span></li></ol>
  <div class="trap" id="trap">Armadilha um.</div>
  <p class="src">Fonte: resumos/Cirurgia/30. Complicações Pós-Operatórias.pdf (febre)</p>
</section>
<section class="sec"><h2>Dois</h2>
  <figure class="fig-an"><svg viewBox="0 0 10 10" role="img" aria-label="x"></svg>
    <figcaption id="cap">Legenda da figura, ainda na faixa.<span class="fa-src">Fonte: SBC. Diretriz de IC 2023</span></figcaption></figure>
  <p id="b">Depois da figura vem o texto grifado aqui.</p>
  <p class="src">Fonte: SBC. Diretriz de IC 2023</p>
  <ul><li id="tce"><strong>Fonte:</strong> arterial em cerca de 85% dos casos -- a artéria meníngea média.</li></ul>
  <ul><li id="trail">Armadilha de IC no gabarito clássico. Fonte: PMID 42366997, DOI 10.1161/CIR.1.</li></ul>
  <ol class="esc"><li id="passo2"><span class="n">2</span><span>Passo dois da escada.</span></li></ol>
  <p class="src">Fonte: Ministério da Saúde. PCDT de Hepatites Virais, 2022</p>
  <blockquote><p id="olho">Fonte: Apostila Estratégia MED -- Prof. X (2024)
Câncer mais frequente nas mulheres</p></blockquote>
</section>
<footer><p><strong>Fonte:</strong> <code>resumos/Pediatria/34. Kawasaki.pdf</code> (EMED)</p></footer>
</div></body></html>"""

DOC_SEM_FONTE = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><div class="wrap">
<p>A principal fonte de ferro: carne vermelha.</p><p>Fonte de calor alta.</p><ul><li>Fonte: arterial, 85%.</li></ul></div></body></html>"""

DOC_REFS_NOVA = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><div class="wrap">
<p id="x">Texto novo.<sup class="ref"><a href="#ref-1">1</a></sup></p>
<p id="y">Outro texto.</p><p class="src">Fonte: KDIGO 2021</p><p class="src">Fonte: verso do card 12</p>
<section class="refs" id="refs"><h2>Referências</h2><ol><li id="ref-1">AHA 2020</li></ol><p class="base">Base deste documento: resumos/X.md</p></section>
</div></body></html>"""

JS_REFS = """
var GRIFOS = [["b", "texto grifado"], ["cap", "ainda na faixa"], ["trail", "gabarito clássico"], ["olho", "mais frequente"],
              ["passo2", "Passo dois"], ["tce", "arterial"]];
(async function(){
  try{
    var d = await carregar(%s), b1 = grifoBlocos(d), t1 = b1.map(function(b){ return b.textContent; });
    var gs = GRIFOS.map(function(p){ var i = b1.indexOf(d.getElementById(p[0])), ini = t1[i].indexOf(p[1]);
      return {b: i, ini: ini, fim: ini + p[1].length, txt: p[1], id: p[0]}; });   // o grifo salvo ANTES (s214)
    SAIDA.stats = refsMontar(d);
    var b2 = grifoBlocos(d), t2 = b2.map(function(b){ return b.textContent; });
    SAIDA.grifos = gs.map(function(g){ var r = grifoResolver(t2, g); return {id: g.id, mesmo_bloco: !!r && r.b === g.b,
      mesmo_offset: !!r && r.ini === g.ini, el: r && b2[r.b].id}; });
    SAIDA.blocos = {antes: b1.length, prefixo_igual: b1.every(function(b, i){ return b2[i] === b || b2[i].classList.contains("hub-ref-lugar"); })};
    SAIDA.fora = fontesFora(d);
    SAIDA.txt = {a: txt(d.getElementById("a")), cap: txt(d.getElementById("cap")), b: txt(d.getElementById("b")), trap: txt(d.getElementById("trap")),
      trail: txt(d.getElementById("trail")), tce: txt(d.getElementById("tce")), passo2: txt(d.getElementById("passo2")), olho: txt(d.getElementById("olho"))};
    SAIDA.sups = Array.prototype.map.call(d.querySelectorAll("sup.hub-ref a"), function(a){ return [a.getAttribute("href"), a.textContent, (a.closest("[id]") || {}).id]; });
    SAIDA.sup_no_texto_do_passo = !!d.querySelector("#passo2 > span:last-child > sup.hub-ref");
    SAIDA.refs = Array.prototype.map.call(d.querySelectorAll("section.hub-refs ol > li"), function(li){ return [li.id, txt(li)]; });
    SAIDA.base = Array.prototype.map.call(d.querySelectorAll("section.hub-refs .hub-base li"), function(li){ return txt(li); });
    var sec = d.querySelectorAll("section.hub-refs");
    SAIDA.sec = {n: sec.length, h2: txt(sec[0] && sec[0].querySelector("h2")), base_tit: txt(sec[0] && sec[0].querySelector(".hub-base > p")),
      pai: sec[0] && sec[0].parentNode.className, ultima: !!sec[0] && sec[0].parentNode.lastElementChild === sec[0],
      depois_do_rodape: !!sec[0] && sec[0].previousElementSibling.tagName === "FOOTER"};
    SAIDA.ocultos = {rodape: d.querySelector("footer").hidden, olho_visivel: !d.getElementById("olho").closest("[hidden]"),
      lugares: d.querySelectorAll(".hub-ref-lugar").length, lugares_escondidos: Array.prototype.every.call(d.querySelectorAll(".hub-ref-lugar"),
      function(e){ return e.hidden && d.defaultView.getComputedStyle(e).display === "none" && !e.textContent; })};
    var html1 = d.body.innerHTML; SAIDA.de_novo = refsMontar(d); SAIDA.idempotente = d.body.innerHTML === html1;
    var d2 = await carregar(%s); refsMontar(d2); SAIDA.reabrir_igual = d2.body.innerHTML === html1;
    var d3 = await carregar(%s), h3 = d3.body.innerHTML; SAIDA.sem = {stats: refsMontar(d3), igual: d3.body.innerHTML === h3, sec: !!d3.querySelector("section.hub-refs, .hub-base")};
    var d4 = await carregar(%s); SAIDA.nova = {stats: refsMontar(d4), hub: d4.querySelectorAll("section.hub-refs").length,
      refs: Array.prototype.map.call(d4.querySelectorAll("section.refs ol > li"), function(li){ return [li.id, txt(li)]; }),
      sup: Array.prototype.map.call(d4.querySelectorAll("#y sup a"), function(a){ return [a.getAttribute("href"), a.textContent]; }),
      base: txt(d4.querySelector("p.base")), fora: fontesFora(d4)};
  }catch(e){ SAIDA.erro = String(e && e.stack || e); }
  fim();
})();
""" % (json.dumps(DOC_REFS), json.dumps(DOC_REFS), json.dumps(DOC_SEM_FONTE), json.dumps(DOC_REFS_NOVA))


@pytest.fixture(scope="module")
def refs_saida():
    return _edge_rodar(JS_REFS, "refs")


def test_referencias_tiram_a_fonte_do_meio_e_montam_a_lista_no_fim(refs_saida):
    """Part 7 DoD 1, 2 e 6: p.src, span.fa-src na legenda, a "Fonte:" que fecha o item e o rodape saem do texto; o que
    so CITA a palavra (ou e conteudo: o TCE) fica; a base interna vai para "Base deste documento" sem numero; as
    referencias de verdade viram a lista numerada na ordem de aparicao, a repetida com o MESMO numero; o sobrescrito na
    legenda, no fim do bloco anterior (dentro do item da grade, nunca um item novo) e no proprio item; a secao no fim
    do conteiner do ultimo texto (depois do rodape, como num artigo)."""
    s = refs_saida
    assert "erro" not in s, s.get("erro")
    assert s["fora"] == ["Fonte: arterial em cerca de 85% dos casos -- a artéria meníngea média."], "so o TCE fica"
    assert s["stats"] == {"referencias": 3, "base": 3, "movidas": 7}
    assert s["refs"] == [["hub-ref-1", "SBC. Diretriz de IC 2023"], ["hub-ref-2", "PMID 42366997, DOI 10.1161/CIR.1."],
                         ["hub-ref-3", "Ministério da Saúde. PCDT de Hepatites Virais, 2022"]]
    assert s["base"] == ["resumos/Cirurgia/30. Complicações Pós-Operatórias.pdf (febre)", "Apostila Estratégia MED -- Prof. X (2024)",
                         "resumos/Pediatria/34. Kawasaki.pdf (EMED)"]
    assert s["sups"] == [["#hub-ref-1", "1", "cap"], ["#hub-ref-1", "1", "b"], ["#hub-ref-2", "2", "trail"], ["#hub-ref-3", "3", "passo2"]]
    assert s["sup_no_texto_do_passo"] is True, "na linha em grade o sobrescrito entra no texto, nunca vira um item novo"
    assert s["txt"]["a"] == "A principal fonte de ferro na dieta é a carne. Fonte de calor alta.", "citar a palavra nao move"
    assert s["txt"]["cap"] == "Legenda da figura, ainda na faixa.1" and s["txt"]["b"] == "Depois da figura vem o texto grifado aqui.1"
    assert s["txt"]["trail"] == "Armadilha de IC no gabarito clássico.2"
    assert s["txt"]["trap"] == "Armadilha um.", "fonte interna nao deixa numero"
    assert s["txt"]["passo2"] == "2Passo dois da escada.3"
    assert s["txt"]["olho"] == "Câncer mais frequente nas mulheres", "no '> Fonte:' do resumo so a 1a linha e a fonte"
    assert s["sec"] == {"n": 1, "h2": "Referências", "base_tit": "Base deste documento:", "pai": "wrap", "ultima": True,
                        "depois_do_rodape": True}
    assert s["ocultos"] == {"rodape": True, "olho_visivel": True, "lugares": 4, "lugares_escondidos": True}


def test_referencias_preservam_os_grifos_salvos_antes(refs_saida):
    """Part 7 DoD 4: o bloco que sai deixa um marcador vazio do MESMO tipo e a secao entra depois de todo bloco de
    antes -- os blocos de antes ficam no mesmo indice e o grifo salvo antes (inclusive DEPOIS de uma fonte movida)
    re-ancora pelo proprio offset, no mesmo elemento."""
    s = refs_saida
    assert s["blocos"]["prefixo_igual"] is True
    for g in s["grifos"]:
        assert g["mesmo_bloco"] and g["el"] == g["id"], g
        # o olho do resumo perde a 1a linha (a fonte) no COMECO: o trecho re-ancora pelo texto no mesmo bloco
        assert g["mesmo_offset"] is (g["id"] != "olho"), g


def test_referencias_idempotentes_sem_fonte_nada_e_aula_nova_usa_a_lista_dela(refs_saida):
    """Part 7 DoD 3 + complemento do principal: rodar de novo nao duplica e reabrir da o mesmo documento; sem "Fonte:"
    (ou so conteudo) nada muda e nenhuma secao nasce; documento com section.refs nao ganha uma segunda -- a fonte que
    sobrou entra na lista dela (numero seguinte, a mesma ancora) e a base interna no p.base."""
    s = refs_saida
    assert s["de_novo"] is None and s["idempotente"] is True and s["reabrir_igual"] is True
    assert s["sem"] == {"stats": {"referencias": 0, "base": 0, "movidas": 0}, "igual": True, "sec": False}
    n = s["nova"]
    assert n["hub"] == 0 and n["stats"] == {"referencias": 1, "base": 1, "movidas": 2}
    assert n["refs"] == [["ref-1", "AHA 2020"], ["hub-ref-2", "KDIGO 2021"]] and n["sup"] == [["#hub-ref-2", "2"]]
    assert n["base"] == "Base deste documento: resumos/X.md · verso do card 12" and n["fora"] == []


# ======================================================================== s229 (front, pedido dele em 15/10)

def test_grifo_das_listas_guarda_a_cor_e_a_nova_cor_corta_a_antiga():
    """Item 6d: o grifo das Listas nasce com a cor ativa do botao ([ini, fim, cor]; rosa = sem o 3o campo, o de
    antes); da mesma cor funde, de outra cor CORTA o trecho que cobre (vale o ultimo) -- intervalos disjuntos."""
    acao = """SAIDA = {mesma: qzGrifoMesclar([[0, 5, "ciano"]], [3, 8, "ciano"]),
  corta: qzGrifoMesclar([[0, 10]], [3, 6, "amarelo"]),
  cobre: qzGrifoMesclar([[2, 4, "ciano"]], [0, 8]),
  antigo: qzGrifoMesclar([[0, 5], [3, 8, "ciano"]], null),
  html: qzGrifoHtml("abcdefghij", [[0, 2], [4, 6, "ciano"], [7, 9, "lixo"]])};"""
    out = _rodar(_q(), None, None, acao)
    assert out["mesma"] == [[0, 8, "ciano"]]
    assert out["corta"] == [[0, 3], [3, 6, "amarelo"], [6, 10]]
    assert out["cobre"] == [[0, 8]]
    assert out["antigo"] == [[0, 5], [5, 8, "ciano"]], "dado antigo sobreposto vira disjunto"
    assert out["html"] == ('<mark class="qz-grifo" data-i="0">ab</mark>cd<mark class="qz-grifo" data-i="4" '
                           'data-cor="ciano">ef</mark>ghij'), "cor desconhecida = intervalo invalido"
    cap = extrair_funcao(TEMPLATE, "function qzGrifoCapturar(){")
    assert 'grifoCorValida(raiz.getAttribute("data-grifo"))' in cap and '[ini, fim, cor]' in cap


def test_resolver_do_painel_abre_a_lista_da_tarefa():
    """Item 2: o botao "Resolver" leva `data-hub-tarefa`; a aba Listas abre JA na lista dela -- a 1a ainda por
    resolver, senao a resolvida (revisao); pendente/bloqueada nao abre."""
    prog = extrair_funcao(TEMPLATE, "function qzListaDaTarefa(listas, tarefa){") + """
var L = [{_id: "t9", tarefa: 9, status: "resolvida"}, {_id: "t9_1", tarefa: 9, status: "capturada"},
         {_id: "t5", tarefa: 5, status: "resolvida"}, {_id: "t7", tarefa: 7, status: "pendente"}];
console.log(JSON.stringify([qzListaDaTarefa(L, "9")._id, qzListaDaTarefa(L, 5)._id, qzListaDaTarefa(L, "7"),
                            qzListaDaTarefa(null, "9")]));"""
    assert _node(prog) == ["t9_1", "t5", None, None]
    atalho = extrair_funcao(TEMPLATE, "function painelAtalho(a){")
    assert 'a.getAttribute("data-hub-tarefa")' in atalho and "qzAbrirPendente()" in atalho
    assert "qzAbrirPendente(); }" in extrair_funcao(TEMPLATE, "function iniciarQuestoes(){")


def test_nova_some_quando_ele_abre_e_o_aparelho_lembra():
    """Item 5: a RD e a analise nao feitas levam "nova" ate ele ABRIR o item no leitor -- `vistoMarcar` grava em
    localStorage["medhub.vistos"] (try/catch; sem storage, na memoria da pagina) e o quadro tira a etiqueta."""
    prog = "\n".join([_var("VISTOS_CHAVE"), "var quadroVisto = function(s){ CHAMOU.push(s); }, CHAMOU = [];",
                       "var localStorage = {d: {}, getItem: function(k){ if(QUEBRADO){ throw 1; } return this.d[k] || null; },"
                       " setItem: function(k, v){ if(QUEBRADO){ throw 1; } this.d[k] = v; }}, QUEBRADO = false;",
                       _funcs("function vistosLer(){", "function visto(slug){", "function vistoMarcar(slug){")]) + """
var antes = visto("dossie-uerj"); vistoMarcar("dossie-uerj"); var depois = visto("dossie-uerj");
var gravado = JSON.parse(localStorage.d["medhub.vistos"]);
QUEBRADO = true; vistoMarcar("rd-x");
console.log(JSON.stringify({antes: antes, depois: depois, gravado: gravado, sem_storage: visto("rd-x"), chamou: CHAMOU}));"""
    out = _node(prog)
    assert out == {"antes": False, "depois": True, "gravado": {"dossie-uerj": 1}, "sem_storage": True,
                   "chamou": ["dossie-uerj", "rd-x"]}
    assert 'vistoMarcar(pendSlug(href))' in extrair_funcao(TEMPLATE, "function abrirAula(link, titulo, origem){")
    qd = extrair_funcao(TEMPLATE, "function iniciarQuadro(){")
    assert '(t === "revisao" || t === "analise")' in qd and "quadroVisto = function(slug){" in qd


def test_botoes_tematicos_da_teoria_e_das_listas():
    """Itens 5 e 6f: o "abrir aula" da Teoria e o mesmo botao tematico do Painel (`.hub-btn`); "Todas as listas", o
    voltar do leitor, "Anterior" e "Pular" no desenho do "Responder" (contorno ciano, 44 px); a banca em rosa, o
    tema em ciano (item 6e)."""
    corpo = TEMPLATE.split("<script", 1)[0]
    for id_ in ("qz-voltar", "hub-leitor-voltar", "qz-ant", "qz-pular"):
        assert re.search(r'<button type="button" class="hub-btn" id="%s">' % id_, corpo), id_
    css = TEMPLATE[TEMPLATE.index("<style>"):TEMPLATE.index("</style>")]
    regra = re.search(r"\n\.hub-btn\{([^}]*)\}", css).group(1)
    assert "min-height:44px" in regra and "border:1px solid var(--acento)" in regra and "var(--raio)" in regra
    assert "#qz-banca{color:var(--rosa)" in css and "#qz-tags{color:var(--acento-tinta)" in css
