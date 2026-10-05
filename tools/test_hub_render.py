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
                      "function qzDefeitoUi(r){", "function qzEhSimulado(l){", "function qzModoDaLista(l, espelho){",
                      "function qzEscolheModo(l, espelho, temResposta){", "function qzModoUi(l){",
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
    for sel in (".qz-decl button{", ".qz-link{", ".qz-defeito-form button{", ".qz-linha{", ".qz-modo-lista{"):
        (regra,) = [l for l in css if sel in l]
        assert "min-height:44px" in regra, sel
    assert "min-width:0" in [l for l in css if l.startswith(".qz-cadeia li{")][0]
    rotulos = list(re.findall(r':\s*"([^"]+)"', _declaracao(TEMPLATE, "var QZ_DECL = {")))
    rotulos += ["Erro na cadeia", "Enviar", "Concordo", "Em parte", "Discordo", "Modo estudo", "Modo prova",
                "Estudo", "Prova", "Concluir lista", "Rever uma a uma", "Mudar resposta"]
    assert all(r in TEMPLATE for r in rotulos) and max(len(r) for r in rotulos) <= 15
    for morto in ("Marcar lista como resolvida", "Rever em sequência", "Alterar resposta"):   # > 15 (celular)
        assert morto not in TEMPLATE, morto


# ------------------------------------------------ s201: aba Listas dividida em Questoes | Simulados

LISTAS_JS = "\n".join([_declaracao(TEMPLATE, "var ROT_QZ = {"), _declaracao(TEMPLATE, "var QZ_SUB = {"),
                       # s214: as semanas das Listas recolhem; o estado (secAberta) e lido na renderizacao
                       re.search(r"\n  (var SECOES_CHAVE = [^\n]+;)", TEMPLATE).group(1)] +
                      [extrair_funcao(TEMPLATE, a) for a in (
                          "function qzEsc(s){", "function qzItemLista(l, atrasada){", "function qzEhSimulado(l){",
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


def _listas(modo):
    if not NODE:
        pytest.skip("node ausente no PATH: divisao da aba nao verificada (skip declarado)")
    prog = (HARNESS_LISTAS.replace("__FUNCS__", LISTAS_JS).replace("__LISTAS__", json.dumps(LISTAS))
            .replace("__MODO__", json.dumps(modo)))
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
    assert out["sub"].startswith("As listas da semana")


def test_modo_simulados_mostra_as_provas_na_ordem_do_plano_com_a_da_vez():
    out = _listas("simulados")
    html = out["html"]
    assert "Hérnias" not in html and "UERJ 2026" not in html                # pendente (nao carregada) fica fora
    assert html.index("UERJ 2021") < html.index("UERJ 2022")                 # ordem do plano (semana)
    assert "UERJ 2021 <span class=\"qd-n\">· a da vez</span>" in html and html.count("a da vez") == 1
    assert "60 questões" in html and "~3 h" in html and " -- prova INTEIRA" not in html
    assert out["botoes"][1][1] is True and out["sub"].startswith("As provas da UERJ")


# ------------------------------------------------ s211 part-3: modo Estudo/Prova + tela de fim com os elos

def test_simulado_e_sempre_prova():
    acao = """var sim = {area: "Simulado", modo: "estudo"}; QZ.modoLista = "prova"; qzModoUi(sim);
var esc = $("qz-modo-lista").hidden; QZ.modoLista = "estudo"; qzModoUi({area: "Obstetrícia"});
SAIDA = {modo: qzModoDaLista(sim, "estudo"), escolhe: qzEscolheModo(sim, null, false), controle_sim: esc,
         controle_lista: $("qz-modo-lista").hidden, rotulo: $("qz-modo-lista").textContent};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"modo": "prova", "escolhe": False, "controle_sim": True, "controle_lista": False,
                   "rotulo": "Modo estudo"}


def test_modo_da_lista_vem_do_doc_e_do_espelho():
    """O doc da lista manda (vale entre aparelhos); o espelho local cobre o db fora do ar; lista
    antiga sem modo e com respostas nao pergunta (segue Prova)."""
    acao = """SAIDA = {doc: qzModoDaLista({modo: "estudo"}, "prova"), espelho: qzModoDaLista({}, "estudo"),
  nada: qzModoDaLista({}, null), lixo: qzModoDaLista({modo: "x"}, "y"),
  pergunta: qzEscolheModo({}, null, false), com_resp: qzEscolheModo({}, null, true),
  com_modo: qzEscolheModo({modo: "prova"}, null, false), com_espelho: qzEscolheModo({}, "estudo", false)};"""
    out = _rodar(_q(), None, None, acao)
    assert out == {"doc": "estudo", "espelho": "estudo", "nada": "", "lixo": "", "pergunta": True,
                   "com_resp": False, "com_modo": False, "com_espelho": False}


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
    textos.append(re.search(r'<p class="hub-sub" style="margin:0">([^<]+)</p>', TEMPLATE[i:]).group(1))
    assert len(textos) == 3
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
    """Uma cor so, por token proprio (`--qz-grifo`, ambar nos dois temas -- o tom fraco sumia no escuro, s211); sem barra flutuante, menu ou
    seletor de cor; o limite (selecao por toque no celular nao testada) declarado no template e no brief."""
    (regra,) = [l for l in TEMPLATE.splitlines() if l.startswith(".qz-grifo{")]
    assert "background:var(--qz-grifo)" in regra and "color:var(--qz-grifo-tinta)" in regra and "#" not in regra
    assert TEMPLATE.count('class="qz-grifo"') == 1                        # um so tipo de grifo
    for proibido in ("qz-grifo-cor", "qz-grifo-menu", "qz-grifo-barra"):
        assert proibido not in TEMPLATE
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
# analise sem tarefa ("Outras aulas") e uma aula que CUMPRE a tarefa 70 da semana 4 (tem o "feito").
PLANO_SEC = [_tarefa(26, 1, "Diabetes na Gestação", 19, URL_SEC),
             _tarefa(49, 3, "Hérnias da Parede Abdominal", 21, URL_SEC, bloco="CIR"),
             _tarefa(70, 4, "Aorta e pericárdio", 0, None, fonte="custom", bloco="CM"),
             _tarefa(68, 4, "Doenças Glomerulares", 21, URL_SEC, bloco="CM"),
             _tarefa(71, 5, "Tireoide", 18, URL_SEC, bloco="CM")]
AULAS_SEC = [hub.Aula(s, s, "2026-10-0%d" % (i + 1), "artifacts/aula-%s.html" % s)
             for i, s in enumerate(("rd-hepato", "dossie-x", "aorta"))]
REGISTRO_SEC = {"rd-hepato": {"tipo": "revisao", "titulo": "Revisão direcionada hepato"},
                "dossie-x": {"tipo": "analise", "titulo": "Dossiê"},
                "aorta": {"tipo": "aula", "titulo": "A aorta", "tarefa_id": 70}}


def _pagina_quadro(plano=PLANO_SEC):
    return (hub.html_semanas(plano, CAL_SEC, HOJE_SEC) +
            hub.html_quadro_de(AULAS_SEC, REGISTRO_SEC, {}, plano, CAL_SEC, HOJE_SEC)[0])


SECOES_JS = "\n".join([_var("SECOES_CHAVE"), _funcs(
    "function secoesLer(){", "function secAberta(id, padrao){", "function secGuardar(id, aberta){",
    "function secSemanaAtual(atual, comItens){", "function secPadraoAberta(chave, corrente){",
    "function secPintar(sec, aberta){", "function secAlternar(sec, id){", "function secTecla(ev, acao){",
    "function hubSemanas(){", "function secoesQuadro(raizQd){")])

ACAO_SECOES = r"""
function espera(){ return new Promise(function(ok){ setTimeout(ok, 0); }); }
var qd = $("hub-quadro"), TECLAS = 0;
function titulo(chave){ return qd.querySelector('.qd-sem[data-secao="' + chave + '"] .qd-titulo'); }
function tocar(chave){ titulo(chave).click(); }
function tecla(chave, k){ (titulo(chave)._ouv.keydown || []).forEach(function(f){ f({key: k, preventDefault: function(){ TECLAS++; }}); }); }
function feito(slug){ qd.querySelector('.qd-item[data-slug="' + slug + '"] .qd-feito').click(); }
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
  SAIDA.fim = secoes(); SAIDA.ls = LS; SAIDA.teclas = TECLAS;
  console.log(JSON.stringify(SAIDA)); });
"""


def _rodar_secoes(acao="", ls=None, quebrado=False, plano=PLANO_SEC, cfg=None):
    # tardio: test_hub_quadro importa deste arquivo (NODE, extrair_funcao) -- no topo seria import circular
    from tools.test_hub_quadro import BANCO_QD, DOM_QD, FUNCS_QD, _arvore
    prog = (DOM_QD.replace("__ARVORE__", json.dumps(_arvore(_pagina_quadro(plano)), ensure_ascii=False)) +
            BANCO_QD.replace("__CFG__", json.dumps(cfg or {}, ensure_ascii=False)) + _aparelho(ls, quebrado) +
            FUNCS_QD + "\n" + SECOES_JS + "\n" + ACAO_SECOES.replace("__ACAO__", acao))
    return _node(prog)


def _abertas(estado):
    return {k: v["aberta"] for k, v in estado.items() if not v["oculta"]}


def test_padrao_abre_revisoes_atrasadas_e_a_semana_da_vez():
    out = _rodar_secoes()
    assert _abertas(out["inicio"]) == {"revisoes": True, "atrasadas": True, "3": True, "4": False,
                                       "5": False, "outras": False}
    for chave, s in out["inicio"].items():
        assert (s["role"], s["tab"], s["seta"]) == ("button", "0", True), chave
        assert s["expanded"] == ("true" if s["aberta"] else "false"), chave
        assert s["controls"] == s["lista"] == "qd-lista-" + chave, "aria-controls aponta a lista da secao"
    assert out["ls"] == {}, "sem toque, nada gravado no aparelho"


def test_semana_atual_vazia_abre_a_proxima_com_itens():
    """Hoje = semana 3 sem nada pendente: a fixa fica ("Nada em aberto") e a semana 4 vira a da vez."""
    plano = [l for l in PLANO_SEC if l["semana_plano"] != 3]
    out = _rodar_secoes(plano=plano)
    assert _abertas(out["inicio"]) == {"revisoes": True, "atrasadas": True, "3": True, "4": True,
                                       "5": False, "outras": False}
    puras = _node(SECOES_JS + "\nconsole.log(JSON.stringify({a: secSemanaAtual(3, [5, 4]), b: secSemanaAtual(3, []),"
                  " c: secSemanaAtual(0, [6, 2]), d: [\"revisoes\", \"atrasadas\", \"outras\", \"sem\", \"4\", \"s4\", \"5\", \"s5\"]"
                  ".map(function(k){ return secPadraoAberta(k, 4); })}));")
    assert puras == {"a": 4, "b": 3, "c": 2, "d": [True, True, False, True, True, True, False, False]}


def test_toque_e_teclado_alternam_e_o_aparelho_lembra():
    out = _rodar_secoes('tocar("revisoes"); tocar("5"); tecla("atrasadas", "Enter"); tecla("atrasadas", " ");'
                        ' tecla("outras", " "); tecla("3", "a");')
    fim = _abertas(out["fim"])
    assert fim == {"revisoes": False, "atrasadas": True, "3": True, "4": False, "5": True, "outras": True}
    assert out["fim"]["5"]["expanded"] == "true" and out["fim"]["revisoes"]["expanded"] == "false"
    assert out["teclas"] == 3, "Enter e Espaco viram toque (preventDefault: a pagina nao rola); 'a' nao"
    assert json.loads(out["ls"]["medhub.secoes"]) == {"aulas:revisoes": False, "aulas:5": True,
                                                      "aulas:atrasadas": True, "aulas:outras": True}
    # recarregar: o mesmo aparelho, uma pagina nova -- vale o que ele escolheu; o resto segue o padrao
    de_novo = _rodar_secoes(ls=out["ls"])
    assert _abertas(de_novo["inicio"]) == fim


def test_sem_storage_tudo_funciona_e_so_nao_lembra():
    out = _rodar_secoes('tocar("revisoes"); tocar("4");', quebrado=True)
    assert _abertas(out["fim"])["revisoes"] is False and _abertas(out["fim"])["4"] is True
    de_novo = _rodar_secoes(quebrado=True)
    assert _abertas(de_novo["inicio"])["revisoes"] is True and _abertas(de_novo["inicio"])["4"] is False


def test_recontar_e_concluidas_nao_desfazem_a_secao_recolhida():
    """A aula que cumpre a tarefa 70 mora na semana 4 (recolhida): feito -> Concluidas, a semana conta 1
    (a lista 68 fica), segue recolhida; desfeito -> volta para a semana 4, ainda recolhida."""
    out = _rodar_secoes('feito("aorta"); SAIDA.meio = {onde: onde("aorta"), sec: secoes()["4"]};'
                        ' return espera().then(function(){ feito("aorta"); });')
    meio = out["meio"]
    assert meio["onde"] == "feitas"
    assert meio["sec"]["n"] == "1" and meio["sec"]["aberta"] is False and meio["sec"]["oculta"] is False
    assert out["fim"]["4"]["n"] == "2" and out["fim"]["4"]["aberta"] is False
    assert out["fim"]["4"]["vazio_oculto"] is True


def test_outras_aulas_some_vazia_e_volta_recolhida():
    out = _rodar_secoes('feito("dossie-x"); SAIDA.meio = secoes()["outras"];'
                        ' return espera().then(function(){ feito("dossie-x"); });')
    assert out["meio"]["oculta"] is True and out["meio"]["n"] == "0", "recontar esconde a nao fixa vazia"
    assert out["fim"]["outras"]["oculta"] is False and out["fim"]["outras"]["aberta"] is False


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
var QZ = {listas: __LISTAS__, modo: "questoes"};
var QZ_SEM = {atual: __ATUAL__, datas: {}};
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
    # "Concluidas" segue <details>; nenhuma secao nova depende do hub.py
    assert '<details class="qd-feitas" id="hub-quadro-feitas">' in hub.html_quadro_de(AULAS_SEC, REGISTRO_SEC, {}, PLANO_SEC, CAL_SEC, HOJE_SEC)[0]


# ======================================================================== 3. grifo nas aulas: funcoes puras

GRIFO_PURAS = _funcs("function qzGrifoMesclar(intervalos, novo){", "function grifoValido(g){",
                     "function grifoResolver(textos, g){", "function grifoNormalizar(textos, lista){",
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
    assert "GRIFO.slug = pendSlug(href); GRIFO.ctx = null;" in extrair_funcao(TEMPLATE, "function abrirAula(link){")
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
    assert '"--qz-grifo"' in estilo and '"--qz-grifo-tinta"' in estilo, "a cor e o token das questoes"
