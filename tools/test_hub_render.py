"""test_hub_render.py -- o render da Solucao MedHub em cadeia (qzSolucao, aba Listas do hub) em node.

Spec: veredito do /ai-eng sobre a s200, #6 ALTERA (26/09/2026). Na s200 o desenho da cadeia foi
conferido por um harness node AD HOC, no scratchpad -- fora do repo, nada impedia a regressao.
Aqui a funcao REAL e extraida de `core/templates/hub.html` (casamento de chaves, nunca copiada) e
roda em node com um DOM falso minimo (`$` devolve objetos com hidden/className/innerHTML).

Um cenario por ESTADO de elo que a analise declara (`ok` · `quebrou` · `nao_usou` ·
`nao_avaliado` · conflito = `nao_avaliado` + `conflitos`), mais a leitura PROVISORIA (sem analise:
a pagina le as letras e rotula) e a v1 em texto. Cada cenario tem:
- assercoes SEMANTICAS por elo (classe do <li> e rotulo do <em>) -- o significado que nao pode mudar;
- um GOLDEN do HTML inteiro em `tools/goldens/hub_render/<cenario>.html` -- qualquer mudanca de
  render acusa. Mudou de proposito: `MEDHUB_ATUALIZAR_GOLDEN=1 pytest tools/test_hub_render.py`,
  e o diff do golden vai no commit (e a declaracao). Golden ausente = falha, nunca verde vazio.

Sem `node` no PATH os cenarios sao PULADOS (skip declarado); o teste de extracao roda sempre.
LIMITE DECLARADO: mede o HTML que a funcao produz, nao o CSS nem o que o celular desenha.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
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


FUNCS = "\n".join(extrair_funcao(TEMPLATE, a) for a in
                  ("function qzEsc(s){", "function qzSolucao(q, r){"))

HARNESS = r"""
var els = {};
function $(id){ return els[id] || (els[id] = {id: id, hidden: false, textContent: "", className: "", innerHTML: ""}); }
var QZ = {ana: __ANA__};
__FUNCS__
qzSolucao(__Q__, __R__);
var b = $("qz-medhub");
console.log(JSON.stringify({className: b.className, html: b.innerHTML, texto: b.textContent,
                            obj_hidden: $("qz-obj").hidden, obj: $("qz-obj").textContent}));
"""

SOL = {"versao": 2, "pede": "A conduta na gestante com HbA1c 6,8%.",
       "cadeia": [{"elo": "Classificar a glicemia de jejum", "chave": "GJ 92-125 = DMG."},
                  {"elo": "Aplicar o critério de DM prévio", "chave": "HbA1c >= 6,5% = DM prévio."},
                  {"elo": "Definir a conduta", "chave": "Tratar já."}],
       "alternativas": {"A": {"certa": True, "porque": "HbA1c fecha DM prévio."},
                        "B": {"elo": 1, "porque": "Lê a GJ como normal."},
                        "C": {"elo": 2, "porque": "Ignora a HbA1c."},
                        "D": {"elo": 3, "porque": "Adia o tratamento."}},
       "conferir": ""}
Q = {"num": 8, "solucao_medhub": SOL, "objetivo": "DM prévio x DMG", "fontes_medhub": "SBD 2026"}


def _resp(letra, confianca="duvida", riscadas=()):
    return {"letra": letra, "gabarito": "A", "correta": letra == "A", "confianca": confianca,
            "riscadas": list(riscadas)}


#: cenario -> (resposta, analise da questao 8 ou None, [(classe, rotulo) esperados por elo], provisoria?)
CENARIOS = {
    "provisoria": (_resp("C", riscadas=["B"]), None,
                   [("ok", None), ("quebrou", "provável quebra: a sua letra cai neste elo"), ("", None)],
                   True),
    "ok": (_resp("A", "solida", ["B", "C", "D"]), {"estados": ["ok", "ok", "ok"]},
           [("ok", "firme"), ("ok", "firme"), ("ok", "firme")], False),
    "quebrou": (_resp("D"), {"estados": ["ok", "quebrou", "ok"], "quebrou": 1},
                [("ok", "firme"), ("quebrou", "quebrou aqui (análise do hub)"), ("ok", "firme")],
                False),
    "nao_usou": (_resp("C"), {"estados": ["nao_usou", "quebrou", "ok"], "quebrou": 1},
                 [("naousou", "você sabia, mas não aplicou na hora de decidir"),
                  ("quebrou", "quebrou aqui (análise do hub)"), ("ok", "firme")], False),
    "nao_avaliado": (_resp("C"), {"estados": ["ok", "quebrou", "nao_avaliado"], "quebrou": 1},
                     [("ok", "firme"), ("quebrou", "quebrou aqui (análise do hub)"),
                      ("", "a questão não chegou a testar este elo")], False),
    "conflito": (_resp("B"), {"estados": ["nao_avaliado", "quebrou", "ok"], "quebrou": 1,
                              "conflitos": [0]},
                 [("", "conflito: você declarou este elo firme, mas a letra marcada é a que ele exclui"),
                  ("quebrou", "quebrou aqui (análise do hub)"), ("ok", "firme")], False),
}


class _Cadeia(HTMLParser):
    """Os <li> de `ol.qz-cadeia`: (classe, texto do <em> de rotulo ou None), e o texto todo."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elos, self._na_ol, self._li, self._em, self.texto = [], False, None, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "ol" and "qz-cadeia" in (a.get("class") or ""):
            self._na_ol = True
        elif tag == "li" and self._na_ol:
            self._li = [a.get("class") or "", None]
        elif tag == "em" and self._li is not None:
            self._em = {"classe": a.get("class") or "", "txt": ""}

    def handle_endtag(self, tag):
        if tag == "em" and self._em is not None:
            if not self._em["txt"].startswith("evidência"):
                self._li[1] = self._em["txt"]
            self._em = None
        elif tag == "li" and self._li is not None:
            self.elos.append(tuple(self._li))
            self._li = None
        elif tag == "ol":
            self._na_ol = False

    def handle_data(self, data):
        self.texto.append(data)
        if self._em is not None:
            self._em["txt"] += data


def _cadeia(html):
    p = _Cadeia()
    p.feed(html)
    p.close()
    return p.elos, "".join(p.texto)


def _rodar(q, r, ana):
    if not NODE:
        pytest.skip("node ausente no PATH: render da cadeia nao verificado (skip declarado)")
    prog = (HARNESS.replace("__FUNCS__", FUNCS)
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


def _golden(nome, html):
    arq = GOLDEN_DIR / f"{nome}.html"
    if ATUALIZAR:
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        arq.write_text(html + "\n", encoding="utf-8", newline="\n")
    assert arq.is_file(), f"golden ausente: {arq} (gerar com MEDHUB_ATUALIZAR_GOLDEN=1)"
    assert html + "\n" == arq.read_text(encoding="utf-8"), (
        f"render de '{nome}' mudou -- se foi de proposito, regenere o golden e comite o diff")


def test_funcoes_extraidas_do_template():
    """A extracao acha as duas funcoes inteiras (ancora sumiu = falha alta, nunca skip)."""
    assert FUNCS.count("function ") >= 2 and FUNCS.rstrip().endswith("}")
    assert "qz-cadeia" in FUNCS and "conflitos" in FUNCS


@pytest.mark.parametrize("nome", sorted(CENARIOS))
def test_render_por_estado_do_elo(nome):
    resp, ana, esperado, provisoria = CENARIOS[nome]
    out = _rodar(Q, resp, ana)
    assert out["className"] == "qz-sol"
    elos, texto = _cadeia(out["html"])
    assert elos == esperado
    assert ("leitura provisória" in texto) is provisoria
    assert out["obj_hidden"] is False and out["obj"] == "DM prévio x DMG"
    _golden(nome, out["html"])


def test_letra_marcada_mostra_a_quebra_da_analise_quando_diverge():
    """Cenario `quebrou`: a letra D cai no elo 3, a analise quebrou no elo 2 -> a linha da D diz
    onde a cadeia DELE quebrou (a solucao diz onde a letra falha em geral)."""
    resp, ana, _, _ = CENARIOS["quebrou"]
    _, texto = _cadeia(_rodar(Q, resp, ana)["html"])
    assert "a sua cadeia quebrou no elo 2" in texto


def test_estados_de_tamanho_errado_nao_pintam_e_nao_viram_provisoria():
    """`estados` com tamanho diferente da cadeia e ignorado (nao pinta elo errado), mas a analise
    com `quebrou` segue valendo: rotulo da analise, sem o rotulo de PROVISORIA."""
    out = _rodar(Q, _resp("C"), {"estados": ["ok", "quebrou"], "quebrou": 1})
    elos, texto = _cadeia(out["html"])
    assert elos == [("", None), ("quebrou", "quebrou aqui (análise do hub)"), ("", None)]
    assert "leitura provisória" not in texto


def test_v1_em_texto_segue_como_texto():
    q = dict(Q, solucao_medhub="Pede a conduta. Decide: HbA1c >= 6,5%. Gabarito A.", objetivo="")
    out = _rodar(q, _resp("C"), None)
    assert out["className"] == "qz-texto" and out["html"] == ""
    assert out["texto"].startswith("Pede a conduta.") and out["obj_hidden"] is True


BRIEF = (ROOT / "docs" / "SOLUCAO-MEDHUB-BRIEF.md").read_text(encoding="utf-8")


def _vocabulario_do_brief():
    import re
    (linha,) = [l for l in BRIEF.splitlines() if "Vocabulário:" in l and "`quebrou`" in l]
    return set(re.findall(r"`([a-z_]+)`", linha.split("Vocabulário:", 1)[1]))


def _estados_que_a_pagina_rotula():
    import re
    ini = FUNCS.index("var rot = {")
    fim = FUNCS.index("}[st]", ini)
    return set(re.findall(r"[{,]\s*([a-z_]+)\s*:", FUNCS[ini + len("var rot = "):fim + 1]))


def test_vocabulario_de_estados_do_brief_e_o_da_pagina():
    """#8 do /ai-eng: o estado por elo tem UM portador (o brief). O vocabulário que ele define é
    exatamente o que a página rotula -- estado novo num lado só quebra aqui."""
    assert _vocabulario_do_brief() == _estados_que_a_pagina_rotula() == {
        "ok", "quebrou", "nao_usou", "nao_avaliado"}


def test_skill_e_autopsia_apontam_o_brief_e_nao_redefinem():
    """`/banco-emed` e `/analisar-questao` §3.3 apontam §Estado por elo; nenhum dos dois volta a
    carregar a definição (o rótulo de `nao_usou` é a assinatura de uma cópia)."""
    for nome in ("banco-emed.md", "analisar-questao.md"):
        txt = (ROOT / ".claude" / "commands" / nome).read_text(encoding="utf-8")
        assert "SOLUCAO-MEDHUB-BRIEF.md" in txt and "Estado por elo" in txt, nome
        assert "sabia, não aplicou" not in txt, nome
