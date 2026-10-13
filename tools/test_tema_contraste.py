"""Contraste do tema (hub-tema-v4 part-1, s227): le os hex do core/templates/tema.css e mede pela WCAG 2.x.

A tabela de contraste do docs/UI.md §3 era digitada a mao e envelhecia em silencio a cada troca de paleta (ele muda de
ideia rapido: trocar a paleta = trocar os dois blocos de cor do tema.css). Aqui o numero sai do arquivo, nos DOIS temas,
para os pares que a UI usa: texto sobre as tres superficies, borda de controle, borda da placa contra o fundo e o texto
sobre preenchimento. Sem banco, sem rede.
"""
import re
from pathlib import Path

import pytest

TEMA = Path(__file__).resolve().parent.parent / "core" / "templates" / "tema.css"

SUPERFICIES = ("papel", "card", "afundado")
TEXTOS = ("tinta", "tinta2", "tinta3", "acento", "acento-tinta", "rosa", "roxo-tinta", "ok", "erro", "aviso")
PREENCHIMENTOS = ("acento", "rosa", "roxo", "erro", "aviso", "ok")


def _blocos():
    css = TEMA.read_text(encoding="utf-8")
    escuro = re.search(r':root:not\(\[data-theme="light"\]\),:root\[data-theme="dark"\]\{(.*?)\n\}', css, re.S)
    claro = re.search(r':root\[data-theme="light"\]\{(.*?)\n\}', css, re.S)
    assert escuro and claro, "os dois blocos de cor do tema.css (escuro e claro) mudaram de forma"
    return {"escuro": escuro.group(1), "claro": claro.group(1)}


def _hex(bloco, nome):
    m = re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})\b" % re.escape(nome), bloco)
    assert m, "--%s sem hex de 6 digitos no bloco" % nome
    return m.group(1)


def _lum(h):
    canais = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_contraste_do_calculo_bate_com_a_referencia():
    assert round(contraste("#FFFFFF", "#000000"), 1) == 21.0
    assert round(contraste("#767676", "#FFFFFF"), 2) == 4.54   # o cinza-limite classico da WCAG AA


@pytest.mark.parametrize("tema", ["escuro", "claro"])
def test_texto_legivel_nas_tres_superficies(tema):
    bloco = _blocos()[tema]
    falhas = []
    for t in TEXTOS:
        for s in SUPERFICIES:
            c = contraste(_hex(bloco, t), _hex(bloco, s))
            minimo = 7.0 if t == "tinta" else 4.5
            if c < minimo:
                falhas.append("%s sobre %s = %.2f (< %.1f)" % (t, s, c, minimo))
    assert not falhas, "%s: %s" % (tema, "; ".join(falhas))


@pytest.mark.parametrize("tema", ["escuro", "claro"])
def test_borda_de_controle_e_borda_da_placa(tema):
    bloco = _blocos()[tema]
    for s in ("card", "afundado"):
        c = contraste(_hex(bloco, "linha-forte"), _hex(bloco, s))
        assert c >= 3.0, "%s: borda de controle sobre %s = %.2f (< 3:1)" % (tema, s, c)
    # a placa precisa se separar do fundo a olho (o 'chapado' da v3 era a falta disso)
    c = contraste(_hex(bloco, "borda-placa"), _hex(bloco, "papel"))
    assert c >= 1.6, "%s: borda da placa contra o fundo = %.2f (< 1,6:1)" % (tema, c)
    # o trilho vazio (barra, anel) aparece sobre a placa: o 0 de 76 da manha nao pode sumir (s227)
    c = contraste(_hex(bloco, "trilho"), _hex(bloco, "card"))
    assert c >= 1.35, "%s: trilho sobre a placa = %.2f (< 1,35:1)" % (tema, c)


@pytest.mark.parametrize("tema", ["escuro", "claro"])
def test_texto_sobre_preenchimento(tema):
    bloco = _blocos()[tema]
    falhas = ["%s = %.2f" % (p, contraste(_hex(bloco, "sobre"), _hex(bloco, p)))
              for p in PREENCHIMENTOS if contraste(_hex(bloco, "sobre"), _hex(bloco, p)) < 4.5]
    assert not falhas, "%s: --sobre abaixo de 4,5:1 sobre %s" % (tema, ", ".join(falhas))


def test_placa_e_primitiva_unica_sem_sombra_nem_brilho():
    css = TEMA.read_text(encoding="utf-8")
    assert len(re.findall(r"^\.placa\{", css, re.M)) == 1, "a .placa tem UMA regra (as telas compoem, nunca redefinem)"
    regras = re.findall(r"\{([^}]*)\}", css)
    assert not any("box-shadow" in r or "text-shadow" in r for r in regras), "profundidade sem sombra nem brilho"
    assert "max-width" not in css, "o painel e o player contam max-width <= 2 na pagina pronta"
    for nome in ("--cromado", "--luz", "--borda-placa", "--largura", "--raio-placa"):
        assert nome + ":" in css, "%s ausente do tema" % nome
