"""Testes de tools/prova_pdf.py -- caderno de prova em PDF -> docs `questoes/*` (s201, caminho PDF).

Regua do /ai-eng para o caminho PDF (presenca da s201): GOLDEN (provas reais com contagem esperada),
PROPRIEDADE (toda questao com gabarito e 4-5 alternativas, numero unico, escopo publico), PERTURBADO
(gabarito faltando, discursiva -> recusa nomeada, nada gravado) e TIMEOUT no parser.

Os PDFs da UERJ sao gitignored (IP da banca fica local): o golden PULA sem eles (skip declarado).
O resto roda sobre paginas sinteticas no formato de `ler_pdf` -- o PDF nunca e tocado ali.
"""
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import prova_pdf  # noqa: E402
from app.utils import db  # noqa: E402
import emed_banco  # noqa: E402

LOGO = (40.0, 20.0, 120.0, 60.0)          # caixa que se repete em toda pagina = cabecalho
FIG = (100.0, 500.0, 400.0, 700.0)


def _paginas(com_figura=True):
    """Caderno sintetico de 3 questoes: capa com instrucoes "1)"/"2)", cabecalhos, hifen de quebra,
    item "3)" dentro de enunciado, bloco com "/" espacado, aviso final e uma figura na Q3."""
    capa = [(10, "ORGANIZADOR"), (100, "Além deste caderno de 3 questões, você recebeu:"),
            (120, "Duração máxima da prova: 1 hora"), (140, "1) Na mesa, apenas este caderno."),
            (160, "2) Terminada a prova, entregue o caderno.")]
    cab = [(5, "RESIDÊNCIA MÉDICA UERJ - 2099            ACESSO DIRETO - PROVA OBJETIVA"),
           (12, "Página 2 de 3"), (20, "ORGANIZADOR")]
    p2 = cab + [(80, "CLÍNICA MÉDICA"),
                (100, "1) Mulher com anticorpo anti-"), (112, "receptor de fosfolipase e achado"),
                (124, "3) descrito no laudo. A etiologia é:"),
                (140, "a) primária"), (152, "b) secundária"), (164, "c) neoplásica"), (176, "d) lúpica"),
                (300, "GINECOLOGIA / OBSTETRÍCIA"),
                (320, "2) Gestante de 30 semanas. A conduta é:"),
                (340, "a) parto"), (352, "b) corticoide"), (364, "c) observar"), (376, "d) sulfato")]
    p3 = cab + [(80, "PEDIATRIA"), (100, "3) Lactente com a imagem a seguir. O diagnóstico é:"),
                (720, "a) A"), (732, "b) B"), (744, "c) C"), (756, "d) D"),
                (780, "PROIBIDO DESTACAR ESTA E QUALQUER"), (792, "OUTRA FOLHA DOS CADERNOS DE PROVA")]
    return [(1, capa, [LOGO]), (2, p2, [LOGO]), (3, p3, [LOGO] + ([FIG] if com_figura else []))]


GAB = {"1": "C", "2": "B", "3": "A"}


# ---------------------------------------------------------------- leitura (sintetica)

def test_parse_pula_a_capa_e_le_blocos_hifen_item_interno_e_figura():
    p = prova_pdf.parse_uerj(_paginas())
    qs = p["questoes"]
    assert (p["capa_n"], p["duracao_h"]) == (3, 1)
    assert [q["num"] for q in qs] == [1, 2, 3]                           # capa "1)"/"2)" nao contam
    assert [q["bloco"] for q in qs] == ["Clínica Médica", "Ginecologia e Obstetrícia", "Pediatria"]
    assert "anti-receptor" in qs[0]["enunciado"] and "3) descrito" in qs[0]["enunciado"]
    assert [a for a, _ in qs[0]["alternativas"]] == list("ABCD")
    assert qs[2]["alternativas"][-1] == ("D", "D")                        # aviso final nao gruda
    assert [q["figura"] for q in qs] == [False, False, True]              # logo repetido nao e figura


def test_figura_em_folha_sem_questao_nao_marca_ninguem():
    pags = _paginas(com_figura=False) + [(4, [(10, "PROIBIDO DESTACAR ESTA E QUALQUER")], [LOGO, FIG])]
    assert not any(q["figura"] for q in prova_pdf.parse_uerj(pags)["questoes"])


# ---------------------------------------------------------------- propriedade e perturbacao

def test_problemas_vazio_no_caderno_sao():
    assert prova_pdf.problemas(prova_pdf.parse_uerj(_paginas()), GAB, esperado=3) == []


def test_discursiva_gabarito_faltando_e_contagens_sao_recusas_nomeadas():
    pags = _paginas()
    pags[1] = (2, [l for l in pags[1][1] if not l[1].startswith(("a) p", "b) co", "c) ob", "d) su"))],
               pags[1][2])                                               # Q2 sem alternativas
    probs = prova_pdf.problemas(prova_pdf.parse_uerj(pags), {"1": "C", "2": "B"}, esperado=4)
    txt = " | ".join(probs)
    assert "Q2: alternativas nenhuma" in txt
    assert "Q3: gabarito 'ausente'" in txt
    assert "o gabarito tem 2 respostas" in txt and "--expect 4" in txt


def test_capa_diferente_do_parse_e_recusa():
    p = prova_pdf.parse_uerj(_paginas())
    p["capa_n"] = 60
    assert any("a capa diz 60" in x for x in prova_pdf.problemas(p, GAB))


def test_docs_escopo_publico_e_anulada_fora():
    docs, anuladas = prova_pdf.montar_docs(prova_pdf.parse_uerj(_paginas()),
                                           {"1": "C", "2": "ANULADA", "3": "A"}, "t9", 9, "UERJ 2099",
                                           agora="2026-09-26T16:00:00")
    assert anuladas == [2] and [d["num"] for d in docs] == [1, 3]
    d = docs[0]
    assert d["alternativas"].splitlines()[0] == "A) primária" and d["tags"] == "Clínica Médica"
    assert (d["solucao"], d["forum"], d["estatistica"], d["emed_id"]) == ("", "", "", "")
    assert docs[1]["figura"] is True and "figura" not in d


# ---------------------------------------------------------------- CLI: tudo ou nada + timeout

def _gab_json(tmp_path, respostas):
    arq = tmp_path / "gab.json"
    arq.write_text(json.dumps({"edicoes": {"2099": {"respostas": respostas}}}), encoding="utf-8")
    return arq


def _cli(tmp_path, respostas, *extra):
    return prova_pdf.main(["--pdf", "x.pdf", "--edicao", "2099", "--lista", "t9",
                           "--out", str(tmp_path / "out"), "--gabaritos", str(_gab_json(tmp_path, respostas)),
                           *extra])


def test_cli_grava_tudo_quando_nao_ha_problema(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(prova_pdf, "ler_pdf", lambda caminho: _paginas())
    assert _cli(tmp_path, GAB, "--expect", "3") == 0
    assert sorted(p.name for p in (tmp_path / "out" / "questoes").iterdir()) == \
        ["t9_1.json", "t9_2.json", "t9_3.json"]


def test_cli_gabarito_faltando_nao_grava_nada(tmp_path, monkeypatch, capsys):
    """PERTURBADO: a 'pagina do gabarito' sem a Q3 -> recusa nomeada, nenhum arquivo (nem metade)."""
    monkeypatch.setattr(prova_pdf, "ler_pdf", lambda caminho: _paginas())
    assert _cli(tmp_path, {"1": "C", "2": "B"}) == 2
    assert "RECUSA" in capsys.readouterr().out
    assert not (tmp_path / "out").exists()


def test_cli_timeout_do_parser_e_recusa(tmp_path, monkeypatch, capsys):
    def lento(caminho):
        time.sleep(3)
        return _paginas()
    monkeypatch.setattr(prova_pdf, "ler_pdf", lento)
    assert _cli(tmp_path, GAB, "--timeout", "1") == 2
    assert "passou de 1s" in capsys.readouterr().out
    assert not (tmp_path / "out").exists()


def test_cli_lista_fora_do_formato_e_recusa(tmp_path, capsys):
    assert prova_pdf.main(["--pdf", "x.pdf", "--edicao", "2099", "--lista", "uerj2099",
                           "--out", str(tmp_path / "o")]) == 2


def test_docs_passam_pelo_ingerir_e_o_export_devolve_pagina_e_figura(tmp_path, monkeypatch, capsys):
    """Os docs sao o formato da Bancada: `--ingerir` aceita todos; `pagina`/`figura` viajam em
    `extras` e voltam soltos no `--exportar`."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "emed.db"))
    monkeypatch.setattr(prova_pdf, "ler_pdf", lambda caminho: _paginas())
    assert _cli(tmp_path, GAB) == 0
    capsys.readouterr()
    assert emed_banco.main(["--ingerir", str(tmp_path / "out"), "--apply", "--expect", "3", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["novas"] == 3
    assert emed_banco.main(["--exportar", "t9", "--out", str(tmp_path / "exp")]) == 0
    d3 = json.loads((tmp_path / "exp" / "questoes" / "t9_3.json").read_text(encoding="utf-8"))
    assert d3["figura"] is True and d3["pagina"] == 3 and d3["tags"] == "Pediatria"


# ---------------------------------------------------------------- GOLDEN: as 6 provas reais

UERJ = ROOT / "simulados" / "uerj"
GOLDEN = {  # edicao: (pdf, questoes gravadas, anuladas, tamanhos dos 5 blocos)
    "2021": ("uerj_ad_2021_a.pdf", 60, [], [12, 12, 12, 12, 12]),
    "2022": ("uerj_ad_2022_a.pdf", 60, [], [12, 12, 12, 12, 12]),
    "2023": ("uerj_ad_2023_a.pdf", 100, [], [20, 20, 20, 20, 20]),
    "2024": ("uerj_ad_2024_a.pdf", 100, [], [20, 20, 20, 20, 20]),
    "2025": ("uerj_ad_2025_prova.pdf", 97, [36, 66, 96], [20, 19, 20, 19, 19]),
    "2026": ("uerj_ad_2026_a.pdf", 100, [], [20, 20, 20, 20, 20]),
}


@pytest.mark.parametrize("edicao", sorted(GOLDEN))
def test_golden_provas_uerj_reais(edicao):
    pdf, n, anuladas, blocos = GOLDEN[edicao]
    if not (UERJ / pdf).is_file():
        pytest.skip(f"{pdf} ausente (gitignored): golden nao verificado")
    gab = json.loads((UERJ / "gabaritos_2021-2026.json").read_text(encoding="utf-8"))["edicoes"][edicao]["respostas"]
    parse = prova_pdf.parse_uerj(prova_pdf.ler_pdf(str(UERJ / pdf)))
    assert prova_pdf.problemas(parse, gab, esperado=len(gab)) == []
    docs, anul = prova_pdf.montar_docs(parse, gab, "t1", 1, f"UERJ {edicao}")
    assert (len(docs), anul) == (n, anuladas)
    por_bloco = {}
    for d in docs:
        por_bloco[d["tags"]] = por_bloco.get(d["tags"], 0) + 1
        assert d["gabarito"] in [l.split(")")[0] for l in d["alternativas"].splitlines()]
    assert list(por_bloco.values()) == blocos and set(por_bloco) == set(prova_pdf.BLOCOS_UERJ.values())


def test_figuras_batem_com_o_mapa_independente():
    """Segunda lente: o mapa tematico (s188, outros agentes lendo o texto) marca 3 questoes com
    imagem; o parser acha as mesmas 3 pela caixa da imagem na pagina."""
    mapa = UERJ / "uerj_mapa_questoes_2021-2026.json"
    if not mapa.is_file() or not all((UERJ / g[0]).is_file() for g in GOLDEN.values()):
        pytest.skip("mapa ou PDFs ausentes")
    esperado = {(q["edicao"], q["n"]) for q in json.loads(mapa.read_text(encoding="utf-8"))["questoes"]
                if q.get("imagem")}
    achado = set()
    for edicao, (pdf, *_rest) in GOLDEN.items():
        for q in prova_pdf.parse_uerj(prova_pdf.ler_pdf(str(UERJ / pdf)))["questoes"]:
            if q["figura"]:
                achado.add((int(edicao), q["num"]))
    assert achado == esperado
