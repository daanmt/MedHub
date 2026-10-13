"""test_ui_capturas.py -- as partes PURAS de `tools/ui_capturas.py` (s225), sem abrir o Edge.

Cobre o parse de --larguras/--cenas, a trava de tmp/ (o seed tem conteudo do EMED: --seed e --out
fora de tmp/ sao recusados antes de escrever), a montagem do seed a partir de pastas sinteticas
(tmp_path), o default de seeds, o HTML do harness com o SEED escapado (nada do seed fecha o
<script>), a paridade cena do tool x roteiro do harness, o roteiro decidido sobre o seed e a
leitura da medida que o harness deixa no DOM da moldura.

Fora por desenho: o caminho com navegador (Edge headless + http.server + o JS do harness rodando).
Ele e o proprio tool -- `python tools/ui_capturas.py` -- e a conferencia e o PNG.
"""
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import ui_capturas as uc  # noqa: E402


def _grava(raiz, rel, conteudo):
    p = Path(raiz) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo), encoding="utf-8")
    return p


# ------------------------------------------------------------------ argumentos
def test_larguras_sem_repetir_na_ordem_dada():
    assert uc.parse_larguras("390, 768,390,1280") == [390, 768, 1280]
    assert uc.parse_larguras("1280") == [1280]


@pytest.mark.parametrize("texto", ["", " , ", "abc", "390,x", "-390", "0", "199", "4001", "39.5"])
def test_largura_invalida_recusa(texto):
    with pytest.raises(ValueError):
        uc.parse_larguras(texto)


def test_cenas_default_todas_e_lista_sem_repetir():
    assert uc.parse_cenas(None) == list(uc.CENAS)
    assert uc.parse_cenas("todas") == list(uc.CENAS)
    assert uc.parse_cenas("revelada, FIM,revelada") == ["revelada", "fim"]


def test_cena_desconhecida_recusa_citando_as_validas():
    with pytest.raises(ValueError, match="painel"):
        uc.parse_cenas("revelada,xpto")


def test_trava_de_tmp_e_estrita(tmp_path):
    base = tmp_path / "tmp"
    assert uc.dentro_de(base / "ui_capturas" / "x", base)
    assert not uc.dentro_de(base, base)                       # a propria tmp/ nao e "dentro"
    assert not uc.dentro_de(tmp_path / "tmp2" / "x", base)    # prefixo de nome nao engana
    assert not uc.dentro_de(base / ".." / "fora", base)


def _hub_falso(tmp_path):
    hub = tmp_path / "hub"
    _grava(hub, "index.html", "<title>MedHub</title>")
    return hub


def test_out_fora_de_tmp_recusa_sem_escrever(tmp_path, capsys):
    fora = tmp_path / "fora"
    rc = uc.main(["--hub", str(_hub_falso(tmp_path)), "--out", str(fora), "--cenas", "teoria"])
    assert rc == 1
    assert not fora.exists()
    assert "fora de tmp/" in capsys.readouterr().err


def test_seed_fora_de_tmp_recusa(tmp_path, capsys):
    seed = tmp_path / "seed"
    seed.mkdir()
    rc = uc.main(["--hub", str(_hub_falso(tmp_path)), "--seed", str(seed), "--cenas", "teoria"])
    assert rc == 1
    assert "--seed fora de tmp/" in capsys.readouterr().err


@pytest.mark.parametrize("argv, trecho", [
    (["--porta", "8766"], "reservada"),
    (["--porta", "8767"], "reservada"),
    (["--larguras", "abc"], "largura invalida"),
    (["--cenas", "xpto"], "cena desconhecida"),
])
def test_erro_de_uso_sai_1(tmp_path, capsys, argv, trecho):
    assert uc.main(["--hub", str(_hub_falso(tmp_path))] + argv) == 1
    assert trecho in capsys.readouterr().err


def test_hub_sem_index_sai_1(tmp_path, capsys):
    assert uc.main(["--hub", str(tmp_path / "vazio")]) == 1
    assert "sem index.html" in capsys.readouterr().err


def test_flag_desconhecida_sai_1_e_nao_2(capsys):
    with pytest.raises(SystemExit) as e:
        uc.main(["--nao-existe"])
    assert e.value.code == 1


# ----------------------------------------------------------------------- seed
def test_seed_de_pastas_sinteticas(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _grava(a, "listas/t1.json", {"tema": "A", "status": "capturada"})
    _grava(a, "questoes/t1_1.json", {"lista": "t1", "num": 1})
    _grava(a, "lixo.txt", "nao e doc")
    _grava(a, "vetor.json", [1, 2])                           # nao e objeto -> ignorado
    _grava(a, "quebrado.json", "{")                           # JSON invalido -> ignorado
    _grava(b, "listas/t1.json", {"tema": "B", "status": "capturada"})
    _grava(b, "sessoes/s1/notas/7.json", {"card_id": 7})
    seed, est = uc.montar_seed([a, b])
    assert sorted(seed) == ["listas/t1", "questoes/t1_1", "sessoes/s1/notas/7"]
    assert seed["listas/t1"]["tema"] == "B"                   # a pasta posterior vence no mesmo id
    assert est == {"docs": 3, "ignorados": 2, "por_colecao": {"listas": 1, "questoes": 1, "sessoes": 1}}


def test_seeds_padrao_pula_o_que_nao_existe_e_pega_o_player_de_nome_maior(tmp_path):
    for nome in ("hub_db", "player_2026-09-30a_db", "player_2026-10-10a_db", "player_2026-10-10a_db_fim",
                 "player_db_2026-12-31"):
        (tmp_path / nome).mkdir()
    assert uc.seeds_padrao(tmp_path) == [tmp_path / "hub_db", tmp_path / "player_2026-10-10a_db"]
    assert uc.seeds_padrao(tmp_path / "nada") == []


# -------------------------------------------------------------------- harness
def test_harness_escapa_o_seed_e_cola_o_hub():
    cabeca = uc.HARNESS.read_text(encoding="utf-8")
    perigo = "</script><script>alert(1)</script> <!-- &     fim"
    seed = {"questoes/t1_1": {"enunciado": perigo, "lista": "t1", "num": 1}}
    pagina = uc.html_harness(seed, "<p>o hub</p>", cabeca)
    assert uc.MARCA_SEED not in pagina
    literal = re.search(r"var SEED = (.*?);\n", pagina).group(1)
    for proibido in ("</script", "<!--", "<", ">", "&", " ", " "):
        assert proibido not in literal, proibido
    assert json.loads(literal) == seed                        # o escape e JSON valido e ida-e-volta
    assert pagina.count("</script>") == cabeca.count("</script>")
    assert pagina.endswith("\n<body>\n<p>o hub</p>\n</body></html>\n")


def test_harness_sem_a_marca_recusa():
    with pytest.raises(uc.ErroDeUso):
        uc.html_harness({}, "<p></p>", "<head><script>var SEED = {};</script></head>")


def test_toda_cena_do_tool_tem_roteiro_no_harness():
    txt = uc.HARNESS.read_text(encoding="utf-8")
    assert txt.count(uc.MARCA_SEED) == 1
    faltam = [c for c in uc.CENAS if not re.search(r"\b%s: \{aba: \"" % c, txt)]
    assert not faltam, "cena sem roteiro no ui_harness.html: %s" % faltam


# --------------------------------------------------------------------- roteiro
LOTE_VAZIO = '<script id="lote" type="application/json">{"sessao":"s","cards":[]}</script>'
LOTE_2 = '<script id="lote" type="application/json">{"sessao":"s9","cards":[{"card_id":1},{"card_id":2,"x":"<\\/script>"}]}</script>'
TEORIA = ('<section id="aba-painel"><a class="hub-aula" href="aulas/do-painel.html">p</a></section>'
          '<section id="aba-aulas"><a class="qd-bloco qd-alvo hub-aula" href="aulas/x.html" data-titulo="X">x</a>'
          '<a href="aulas/sem-classe.html">s</a><a class="hub-aula" href="resumos/r.html">r</a></section>'
          '<section id="aba-cards"><a class="hub-aula" href="aulas/dos-cards.html">c</a></section>')


def _seed_listas():
    cad3 = {"cadeia": [{"elo": "a"}, {"elo": "b"}, {"elo": "c"}]}
    return {
        "listas/t1": {"status": "capturada", "semana": 2, "seq": 1, "area": "Cirurgia"},
        "listas/t2": {"status": "resolvida", "semana": 1, "seq": 5, "area": "Pediatria"},
        "listas/t3": {"status": "pendente", "semana": 1, "seq": 1, "area": "GO"},      # a aba nao desenha
        "listas/s1": {"status": "capturada", "semana": 1, "seq": 1, "area": "Simulado"},
        "questoes/t1_1": {"lista": "t1", "num": 1, "solucao_medhub": cad3},
        "questoes/t1_2": {"lista": "t1", "num": 2, "solucao_medhub": cad3},
        "questoes/t2_1": {"lista": "t2", "num": 1, "solucao_medhub": cad3},
        "questoes/t3_1": {"lista": "t3", "num": 1, "solucao_medhub": cad3},
        "respostas/t1_1": {"lista": "t1", "num": 1, "correta": True, "confianca": "solida"},
        "respostas/t2_1": {"lista": "t2", "num": 1, "correta": False, "confianca": "duvida",
                           "elos": ["sim", "nao", "sim"]},
        "respostas/t3_1": {"lista": "t3", "num": 1, "correta": False, "confianca": "chute",
                           "elos": ["nao", "nao", "nao"]},
    }


def _por_cena(plano):
    return {p["cena"]: p for p in plano}


def test_listas_visiveis_no_filtro_e_na_ordem_da_aba():
    ids = [lid for lid, _ in uc.listas_visiveis(_seed_listas())]
    assert ids == ["t1", "t2", "s1"]                          # aberta, resolvida, simulado; pendente fora


def test_roteiro_escolhe_lista_questao_e_revelada(tmp_path):
    site = tmp_path / "site"
    _grava(site, "painel.html", "<p>painel</p>")
    _grava(site, "aulas/x.html", "<p>aula</p>")
    _grava(site, "resumos/r.html", "<p>resumo</p>")
    plano = _por_cena(uc.planejar(list(uc.CENAS), _seed_listas(), LOTE_2 + TEORIA, site))
    assert plano["questao"]["params"] == {"lista": "t1", "num": 2, "modo": "questoes"}   # 1a sem resposta
    assert "podada" not in plano["questao"]["info"]
    # errada/duvida com elos declarados vence a certa e solida (cadeia recolhida), mesmo em lista posterior;
    # a t3 (pendente) nunca entra, apesar de ter a candidata mais "rica"
    assert plano["revelada"]["params"] == {"lista": "t2", "num": 1, "modo": "questoes"}
    assert plano["fim"]["params"] == {"lista": "t2", "modo": "questoes"}
    assert plano["cards"]["params"] == {} and "2 cards" in plano["cards"]["info"]
    assert plano["aula"]["info"] == "aulas/x.html"            # o 1o a.hub-aula DA TEORIA
    assert plano["resumo"]["info"] == "resumos/r.html"
    assert all("params" in p for p in plano.values())


def test_roteiro_sem_dados_diz_o_motivo(tmp_path):
    plano = _por_cena(uc.planejar(list(uc.CENAS), {}, LOTE_VAZIO, tmp_path / "site"))
    for cena in ("questao", "revelada", "fim", "cards", "verso", "aula", "resumo", "painel"):
        assert plano[cena].get("motivo"), cena
    for cena in ("teoria", "listas", "simulados"):           # tela vazia ainda e tela
        assert plano[cena]["params"] == {}


def test_lista_toda_respondida_poda_a_1a_questao(tmp_path):
    seed = {"listas/t9": {"status": "resolvida", "area": "Simulado"},
            "questoes/t9_3": {"lista": "t9", "num": 3}, "questoes/t9_1": {"lista": "t9", "num": 1},
            "respostas/t9_1": {"lista": "t9", "num": 1}, "respostas/t9_3": {"lista": "t9", "num": 3}}
    plano = _por_cena(uc.planejar(["questao", "revelada", "fim"], seed, LOTE_VAZIO, tmp_path))
    assert plano["questao"]["params"] == {"lista": "t9", "num": 1, "modo": "simulados"}
    assert "podada" in plano["questao"]["info"]
    assert plano["revelada"].get("motivo")                    # sem cadeia, nada a revelar
    assert plano["fim"]["params"] == {"lista": "t9", "modo": "simulados"}


def test_aula_cujo_arquivo_falta_diz_qual(tmp_path):
    plano = _por_cena(uc.planejar(["aula"], {}, TEORIA, tmp_path / "site"))
    assert "aulas/x.html" in plano["aula"]["motivo"]


def test_primeiro_link_e_lote():
    assert uc.primeiro_link(TEORIA, "aulas/") == "aulas/x.html"
    assert uc.primeiro_link(TEORIA, "resumos/") == "resumos/r.html"
    assert uc.primeiro_link("<p>sem teoria</p>", "aulas/") is None
    assert uc.ler_lote(LOTE_2)["sessao"] == "s9"
    assert uc.ler_lote("<p>sem lote</p>") == {}


def test_slug_da_aula_em_paridade_com_o_hub():
    hub = pytest.importorskip("tools.hub")
    for nome in ("aula-hernias.html", "aula-TB 360.html", "aula-Hérnias_v2.HTML", "rd-x.html", "aula-.html"):
        assert uc.slug_aula(nome) == hub.slug_de(nome), nome


# ---------------------------------------------------------------------- medida
def test_le_a_medida_do_dump_da_moldura():
    dom = ('<html><body><iframe id="ui-quadro"></iframe><pre id="ui-resultado" hidden="">'
           '{"cena":"fim","ok":true,"info":"lista t1 \\u00b7 a &lt;b&gt; &amp; c","rola":false}</pre></body></html>')
    assert uc.ler_resultado(dom) == {"cena": "fim", "ok": True, "info": "lista t1 · a <b> & c", "rola": False}
    assert uc.ler_resultado('<pre id="ui-resultado" hidden=""></pre>') is None   # roteiro nao terminou
    assert uc.ler_resultado('<pre id="ui-resultado">{quebrado</pre>') is None
    assert uc.ler_resultado("") is None


def test_coluna_da_medida():
    assert uc.medida_txt({"ok": True, "rola": False, "quadros": []}) == "ok"
    rola = {"ok": True, "rola": True, "sw": 512, "cw": 390,
            "elementos": [{"sel": "#qz-alts div.qz-alt", "largura": 430}], "quadros": []}
    assert uc.medida_txt(rola) == "ROLA +122px: #qz-alts div.qz-alt 430px"
    quadro = {"ok": True, "rola": False, "quadros": [{"id": "hub-leitor-quadro", "rola": True, "sw": 400, "cw": 358, "elementos": []}]}
    assert uc.medida_txt(quadro) == "ROLA no hub-leitor-quadro +42px: ?"
    assert "NAO montou: sem lista" in uc.medida_txt({"ok": False, "erro": "sem lista", "quadros": []})
    assert uc.medida_txt(None, "o Edge saiu com 1") == "FALHOU: o Edge saiu com 1"
