"""test_hub.py -- o MedHub HUB (spec .vibeflow/specs/medhub-hub-v0-part-1.md).

O que esta suite trava, em ordem de risco:

1. **Link morto na vitrine.** Todo `<a href>` relativo do index aponta para um arquivo que o manifesto
   PUBLICA (valor nao-nulo). Um link para arquivo que nao subiu e exatamente a morte de link que o hub
   existe para matar (alcancabilidade, Reachability-Debt).
2. **Omitir nao remove.** No update o runtime MANTEM o arquivo omitido; so `null` remove. Aula que
   sumiu da fonte (ou caiu do cap) e consta na listagem publicada TEM de sair como `null` -- senao o
   artifact so cresce ate o teto de 255 entradas e o publish falha.
3. **Teto de entradas como dado:** arquivos + a pagina <= 255 - 8.
4. **O player tem UMA fonte.** O hub compoe as regioes marcadas de `core/templates/player.html`;
   marcador ausente ou repetido falha alto; o lote faz ida e volta sem perda (`extrair_lote`).
5. **Celular** (feedback registrado do operador): nada `sticky`, nada `nowrap`, um `.wrap` so,
   rotulos de aba curtos, alvo de toque >= 44px, `min-width:0` no item de grid de texto variavel.

Repo sintetico em `tmp_path` para o golden -- o `ipub.db` real NUNCA e escrito (o hub le o plano
read-only para o quadro por semanas, aqui injetado vazio; o relogio unico vem congelado por
parametro). Os templates sao os REAIS. O quadro em si: `test_hub_quadro.py`.
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from tools import hub  # noqa: E402
from tools.fsrs_queue import MARCA_ABRE, TEMPLATE_PLAYER  # noqa: E402

AGORA = datetime(2026, 9, 22, 20, 30, 0)
TEMPLATE_HUB_REAL = hub.TEMPLATE_HUB.read_text(encoding="utf-8")
TEMPLATE_PLAYER_REAL = TEMPLATE_PLAYER.read_text(encoding="utf-8")


def _lote(sessao="2026-09-22h", n=2):
    cards = [{"card_id": 100 + i, "frente_contexto": "Caso %d" % i,
              "frente_pergunta": "Pergunta %d?" % i, "verso_resposta": "R%d" % i,
              "verso_regra_mestre": None, "verso_armadilha": None, "area": "Clinica",
              "tema": "IC", "selection_reason": "vencido", "bucket": "atrasados"}
             for i in range(n)]
    return {"sessao": sessao, "gerado_em": "2026-09-22T20:00:00", "total": n, "cards": cards}


def _repo(tmp_path, aulas, painel=True):
    """aulas = [(slug, titulo, data)]. Devolve (raiz, data_fn)."""
    art = tmp_path / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    datas = {}
    for slug, titulo, data in aulas:
        (art / ("aula-%s.html" % slug)).write_text(
            "<title>%s</title>\n<style>body{color:#111}</style>\n<p>aula</p>\n" % titulo,
            encoding="utf-8")
        datas["aula-%s.html" % slug] = data
    if painel:
        (art / "painel.html").write_text("<!DOCTYPE html><title>Painel</title><p>p</p>",
                                         encoding="utf-8")

    def data_fn(path, _raiz):
        return datas[Path(path).name], None
    return tmp_path, data_fn


#: O registro REAL do quadro (s194/s195): as aulas do golden (dmg, raciocinio-diagnostico,
#: topicos-pediatria) estao nele; as demais slugs dos testes entram como `aula` com WARN.
QUADRO_REAL = hub.ler_quadro(ROOT / hub.QUADRO_REG)


def _construir(raiz, data_fn, publicado=(), lote=None):
    return hub.construir(lote or _lote(), raiz=raiz, out=raiz / "tmp" / "hub",
                         publicado=publicado, agora=AGORA, data_fn=data_fn,
                         template_hub=TEMPLATE_HUB_REAL, template_player=TEMPLATE_PLAYER_REAL,
                         quadro=QUADRO_REAL, plano_linhas=[], calendario={})


# --------------------------------------------------------------------------
# 1. Golden do manifesto (repo sintetico fixo)
# --------------------------------------------------------------------------

def test_golden_do_manifesto_num_repo_sintetico(tmp_path):
    raiz, data_fn = _repo(tmp_path, [("dmg", "A Escada do DMG", "2026-09-22"),
                                     ("raciocinio-diagnostico", "A Escada de Bayes", "2026-09-21"),
                                     ("topicos-pediatria", "Topicos em Pediatria", "2026-09-07")])
    manifesto, problemas, avisos = _construir(
        raiz, data_fn, publicado=["index.html", "painel.html", "aulas/velha.html"])
    assert problemas == [] and avisos == []
    assert manifesto == {
        "file_path": "tmp/hub/index.html",
        "files": {
            "aulas/dmg.html": "artifacts/aula-dmg.html",
            "aulas/raciocinio-diagnostico.html": "artifacts/aula-raciocinio-diagnostico.html",
            "aulas/topicos-pediatria.html": "artifacts/aula-topicos-pediatria.html",
            "aulas/velha.html": None,
            "painel.html": "artifacts/painel.html",
        },
        "sessao": "2026-09-22h",
        "total_cards": 2,
        "aulas": 3,
        "montado_em": "2026-09-22 20:30:00",
        "mantidos": [],          # DIFF (s193): sem registro, nada fica de fora -- o v0
    }
    gravado = json.loads((raiz / "tmp" / "hub" / "manifesto.json").read_text(encoding="utf-8"))
    assert gravado == manifesto, "o arquivo e exatamente o que o agente passa ao publish"


def test_lista_de_aulas_sai_da_mais_nova_para_a_mais_antiga(tmp_path):
    raiz, data_fn = _repo(tmp_path, [("a", "Antiga", "2026-08-01"), ("n", "Nova", "2026-09-22"),
                                     ("m", "Meio", "2026-09-01")])
    _construir(raiz, data_fn)
    pagina = (raiz / "tmp" / "hub" / "index.html").read_text(encoding="utf-8")
    ordem = re.findall(r'href="aulas/(\w+)\.html"', pagina)
    assert ordem == ["n", "m", "a"]


# --------------------------------------------------------------------------
# 2. Propriedades
# --------------------------------------------------------------------------

def test_todo_href_relativo_do_index_esta_no_manifesto(tmp_path):
    raiz, data_fn = _repo(tmp_path, [("x%d" % i, "Aula %d" % i, "2026-09-%02d" % (i + 1))
                                     for i in range(9)])
    manifesto, problemas, _ = _construir(raiz, data_fn)
    pagina = (raiz / "tmp" / "hub" / "index.html").read_text(encoding="utf-8")
    vivos = {p for p, f in manifesto["files"].items() if f is not None}
    hrefs = hub.hrefs_relativos(pagina)
    assert hrefs, "o index tem de linkar aulas e painel"
    assert hrefs <= vivos, "link morto na vitrine: %s" % sorted(hrefs - vivos)
    assert problemas == []


def test_teto_de_entradas_com_cap(tmp_path):
    aulas = [("a%03d" % i, "Aula %d" % i, "2026-%02d-%02d" % (1 + i // 28, 1 + i % 28))
             for i in range(130)]
    raiz, data_fn = _repo(tmp_path, aulas)
    manifesto, problemas, avisos = _construir(raiz, data_fn)
    vivos = [p for p, f in manifesto["files"].items() if f is not None]
    assert len(vivos) + 1 <= hub.LIMITE_ENTRADAS - hub.RESERVADAS
    assert manifesto["aulas"] == hub.CAP_AULAS == 120
    assert any("fora do cap" in a for a in avisos)
    assert problemas == []


def test_lote_faz_ida_e_volta_sem_perda():
    lote = _lote(n=3)
    lote["cards"][0]["verso_resposta"] = 'fecha </script> & "aspas" <b>x</b>'
    pagina = hub.montar_index(TEMPLATE_HUB_REAL, TEMPLATE_PLAYER_REAL, lote, [], False, AGORA)
    assert pagina.count(MARCA_ABRE) == 1
    assert "</script> &" not in pagina.split(MARCA_ABRE, 1)[1].split("</script>", 1)[0]
    assert hub.extrair_lote(pagina) == lote


def test_manifesto_estourando_o_teto_falha_alto():
    aulas = [hub.Aula("a%d" % i, "A", "2026-09-01", "artifacts/aula-a%d.html" % i)
             for i in range(hub.TETO_ENTRADAS)]
    with pytest.raises(ValueError, match="teto"):
        hub.montar_manifesto(aulas, painel_fonte="artifacts/painel.html")


# --------------------------------------------------------------------------
# 3. Perturbacao e cap: o que sai vira null
# --------------------------------------------------------------------------

def test_perturbacao_aula_removida_vira_null(tmp_path):
    raiz, data_fn = _repo(tmp_path, [("hernias", "Hernias", "2026-09-22"),
                                     ("dmg", "DMG", "2026-09-22")])
    antes, _, _ = _construir(raiz, data_fn)
    publicado = list(antes["files"])
    (raiz / "artifacts" / "aula-dmg.html").unlink()
    depois, problemas, _ = _construir(raiz, data_fn, publicado=publicado)
    assert depois["files"]["aulas/dmg.html"] is None
    assert depois["files"]["aulas/hernias.html"] == "artifacts/aula-hernias.html"
    assert problemas == []


def test_cap_130_aulas_as_que_caem_e_estavam_publicadas_viram_null(tmp_path):
    aulas = [("a%03d" % i, "Aula %d" % i, "2026-%02d-%02d" % (1 + i // 28, 1 + i % 28))
             for i in range(130)]
    raiz, data_fn = _repo(tmp_path, aulas)
    publicado = ["aulas/a%03d.html" % i for i in range(130)]
    manifesto, _, _ = _construir(raiz, data_fn, publicado=publicado)
    nulos = sorted(p for p, f in manifesto["files"].items() if f is None)
    assert nulos == ["aulas/a%03d.html" % i for i in range(10)], "as 10 mais antigas saem"
    assert manifesto["files"]["aulas/a129.html"] == "artifacts/aula-a129.html"


def test_index_nunca_entra_em_files_nem_vira_null():
    files = hub.montar_manifesto([], painel_fonte=None,
                                 publicado=["index.html", "./index.html", "painel.html"])
    assert "index.html" not in files
    assert files == {"painel.html": None}


def test_publicado_aceita_texto_e_json():
    texto = "# listagem do Artifact\nindex.html\naulas/dmg.html  63 KB\n\n./painel.html\n"
    assert hub.ler_publicado(texto) == ["index.html", "aulas/dmg.html", "painel.html"]
    assert hub.ler_publicado('["aulas/a.html", {"path": "painel.html"}]') == [
        "aulas/a.html", "painel.html"]
    assert hub.ler_publicado('{"files": {"aulas/a.html": "artifacts/aula-a.html"}}') == [
        "aulas/a.html"]
    assert hub.ler_publicado("") == []


# --------------------------------------------------------------------------
# 3b. DIFF (v1, s193): so o novo ou alterado sobe; o resto o runtime mantem
# --------------------------------------------------------------------------

_TRES = [("hernias", "Hernias", "2026-09-22"), ("dmg", "DMG", "2026-09-21"),
         ("s17", "S17", "2026-09-07")]


def _publicar(raiz, data_fn, vivos=None):
    """build -> (publish aceito) -> --confirmar. Devolve o manifesto e a listagem viva que o
    publish deixaria: {path: bytes} de tudo no ar."""
    manifesto, problemas, _ = _construir(raiz, data_fn, publicado=vivos or {})
    assert problemas == []
    assert hub.main(["--confirmar", "--out", str(raiz / "tmp" / "hub")]) == 0
    estado = json.loads((raiz / "tmp" / "hub" / hub.ESTADO_POS).read_text(encoding="utf-8"))
    return manifesto, {p: e["bytes"] for p, e in estado["arquivos"].items()}


def test_diff_sem_mudanca_o_segundo_publish_nao_manda_nada(tmp_path):
    raiz, data_fn = _repo(tmp_path, _TRES)
    primeiro, vivos = _publicar(raiz, data_fn)
    assert primeiro["mantidos"] == [] and len(primeiro["files"]) == 4, "1o publish: tudo vai"
    segundo, problemas, _ = _construir(raiz, data_fn, publicado=vivos)
    assert segundo["files"] == {}, "nada mudou: files vazio, so a pagina sobe"
    assert segundo["mantidos"] == ["aulas/dmg.html", "aulas/hernias.html", "aulas/s17.html",
                                   "painel.html"]
    assert problemas == [], "aula mantida segue linkada no index sem virar link morto"


def test_diff_um_byte_alterado_vai_e_o_resto_fica(tmp_path):
    raiz, data_fn = _repo(tmp_path, _TRES)
    _, vivos = _publicar(raiz, data_fn)
    aula = raiz / "artifacts" / "aula-dmg.html"
    aula.write_text(aula.read_text(encoding="utf-8").replace("aula", "aulA"), encoding="utf-8")
    manifesto, problemas, _ = _construir(raiz, data_fn, publicado=vivos)
    assert manifesto["files"] == {"aulas/dmg.html": "artifacts/aula-dmg.html"}
    assert "aulas/dmg.html" not in manifesto["mantidos"] and problemas == []


def test_diff_nunca_omite_o_que_nao_esta_na_listagem_viva(tmp_path):
    """Artifact recriado (ou arquivo removido por fora): o registro diz 'publicado', a listagem
    viva nao. Sem a listagem, nada fica de fora -- omitir e o erro silencioso."""
    raiz, data_fn = _repo(tmp_path, _TRES)
    _, vivos = _publicar(raiz, data_fn)
    sem_dmg = {p: b for p, b in vivos.items() if p != "aulas/dmg.html"}
    manifesto, _, _ = _construir(raiz, data_fn, publicado=sem_dmg)
    assert manifesto["files"] == {"aulas/dmg.html": "artifacts/aula-dmg.html"}
    tudo, _, _ = _construir(raiz, data_fn, publicado=[])
    assert tudo["mantidos"] == [] and len(tudo["files"]) == 4, "sem --publicado: o v0"


def test_diff_tamanho_vivo_divergente_manda_de_novo(tmp_path):
    """Registro e fonte batem, mas o servidor tem OUTRO tamanho: o registro esta velho
    (confirmado sem publish, publish por outra via). A listagem viva desempata."""
    raiz, data_fn = _repo(tmp_path, _TRES)
    _, vivos = _publicar(raiz, data_fn)
    vivos["aulas/s17.html"] += 1
    manifesto, _, _ = _construir(raiz, data_fn, publicado=vivos)
    assert manifesto["files"] == {"aulas/s17.html": "artifacts/aula-s17.html"}


def test_diff_registro_so_muda_pelo_confirmar(tmp_path):
    raiz, data_fn = _repo(tmp_path, _TRES)
    registro = raiz / "tmp" / "hub" / hub.REGISTRO
    _construir(raiz, data_fn)
    assert not registro.exists(), "build nunca escreve o registro"
    _, vivos = _publicar(raiz, data_fn)
    antes = registro.read_text(encoding="utf-8")
    (raiz / "artifacts" / "aula-hernias.html").write_text("<title>Nova</title>", encoding="utf-8")
    manifesto, _, _ = _construir(raiz, data_fn, publicado=vivos)
    assert registro.read_text(encoding="utf-8") == antes, "publish nao confirmado nao contamina"
    assert manifesto["files"] == {"aulas/hernias.html": "artifacts/aula-hernias.html"}


def test_diff_nulo_sai_do_estado_e_a_aula_removida_vira_null(tmp_path):
    raiz, data_fn = _repo(tmp_path, _TRES)
    _, vivos = _publicar(raiz, data_fn)
    (raiz / "artifacts" / "aula-s17.html").unlink()
    manifesto, problemas, _ = _construir(raiz, data_fn, publicado=vivos)
    assert manifesto["files"] == {"aulas/s17.html": None}
    estado = json.loads((raiz / "tmp" / "hub" / hub.ESTADO_POS).read_text(encoding="utf-8"))
    assert "aulas/s17.html" not in estado["arquivos"] and problemas == []


def test_publicado_aceita_a_listagem_do_artifact_como_ela_sai():
    listagem = (
        'Published files of https://claude.ai/artifact/X (version 1-a), 3 files by path\n'
        '- "aulas/dmg.html"  text/html  63060 bytes\n'
        '- "index.html"  text/html  226443 bytes\n'
        '- "painel.html"  text/html  10919 bytes\n'
        '[Stored for the live version, as the artifact service holds it: contract 0.2.54]\n'
        '<artifact-stored-declaration>\n{"db":{"rules":[]}}\n</artifact-stored-declaration>\n')
    assert hub.ler_publicado_detalhado(listagem) == [
        ("aulas/dmg.html", 63060), ("index.html", 226443), ("painel.html", 10919)]
    assert hub.ler_publicado_detalhado('[{"path": "aulas/a.html", "bytes": 12}]') == [
        ("aulas/a.html", 12)]


def test_confirmar_sem_build_sai_1(tmp_path):
    assert hub.main(["--confirmar", "--out", str(tmp_path)]) == 1


# --------------------------------------------------------------------------
# 4. --check
# --------------------------------------------------------------------------

def test_check_acusa_fonte_inexistente(tmp_path):
    pagina = '<a href="aulas/x.html">x</a>'
    problemas = hub.checar(pagina, {"aulas/x.html": "artifacts/aula-x.html"}, tmp_path)
    assert problemas == ["fonte inexistente: aulas/x.html <- artifacts/aula-x.html"]


def test_check_acusa_href_fora_do_manifesto(tmp_path):
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "painel.html").write_text("p", encoding="utf-8")
    pagina = ('<a href="painel.html">p</a> <a href="aulas/sumiu.html#topo">s</a> '
              '<a href="https://med.estrategia.com/x">ext</a> <a href="#ancora">a</a>')
    problemas = hub.checar(pagina, {"painel.html": "artifacts/painel.html",
                                    "aulas/sumiu.html": None}, tmp_path)
    assert problemas == ["link morto no index: aulas/sumiu.html (fora do manifesto)"]


def test_check_pela_cli_sai_1_com_problema_e_0_sem(tmp_path):
    fonte = tmp_path / "aula.html"
    fonte.write_text("a", encoding="utf-8")
    (tmp_path / "index.html").write_text('<a href="aulas/a.html">a</a>', encoding="utf-8")
    manifesto = {"file_path": "index.html", "files": {"aulas/a.html": fonte.as_posix()}}
    (tmp_path / "manifesto.json").write_text(json.dumps(manifesto), encoding="utf-8")
    assert hub.main(["--check", "--out", str(tmp_path)]) == 0
    fonte.unlink()
    assert hub.main(["--check", "--out", str(tmp_path)]) == 1


def test_build_pela_cli_sai_1_quando_o_check_acusa(tmp_path, monkeypatch):
    def check_falso(*_a, **_k):
        return ["link morto no index: aulas/x.html (fora do manifesto)"]
    lote = tmp_path / "lote.json"
    lote.write_text(json.dumps(_lote()), encoding="utf-8")
    monkeypatch.setattr(hub, "checar", check_falso)
    assert hub.main(["--build", "--lote", str(lote), "--out", str(tmp_path / "out")]) == 1


# --------------------------------------------------------------------------
# 5. Escape, regioes do player, templates reais
# --------------------------------------------------------------------------

def test_titulo_de_aula_com_script_sai_escapado():
    aula = hub.Aula("x", '<script>alert(1)</script> & "t"', "2026-09-22", "artifacts/aula-x.html")
    trecho = hub.html_aulas([aula])
    assert "<script>" not in trecho
    assert "&lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;t&quot;" in trecho


def test_titulo_lido_por_parser_com_entidade():
    assert hub.titulo_de("<title>A Escada das H&eacute;rnias</title><p>x</p>") == \
        "A Escada das Hérnias"
    assert hub.titulo_de("<p>sem titulo</p>") == ""


def test_regioes_do_player_real_cada_marcador_1x():
    regioes = hub.extrair_regioes_player(TEMPLATE_PLAYER_REAL)
    assert set(regioes) == {"css", "corpo", "js"}
    assert "--acento" in regioes["css"]
    assert 'id="drill"' in regioes["corpo"] and 'class="wrap"' not in regioes["corpo"]
    assert regioes["js"].lstrip().startswith("<script>")
    assert MARCA_ABRE not in "".join(regioes.values()), "o lote nao pode vir junto com o player"


def test_marcador_do_player_ausente_ou_repetido_falha_alto():
    sem = TEMPLATE_PLAYER_REAL.replace("<!-- @player:corpo:inicio -->", "")
    with pytest.raises(ValueError, match="exatamente 1"):
        hub.extrair_regioes_player(sem)
    dobrado = TEMPLATE_PLAYER_REAL.replace("/* @player:css:fim */",
                                           "/* @player:css:fim */ /* @player:css:fim */")
    with pytest.raises(ValueError, match="exatamente 1"):
        hub.extrair_regioes_player(dobrado)


def test_lugar_do_hub_repetido_falha_alto():
    dobrado = TEMPLATE_HUB_REAL.replace("<!-- @hub:aulas -->", "<!-- @hub:aulas --><!-- @hub:aulas -->")
    with pytest.raises(ValueError, match="exatamente 1"):
        hub.montar_index(dobrado, TEMPLATE_PLAYER_REAL, _lote(), [], True, AGORA)


def test_hub_real_monta_com_titulo_no_inicio_e_sem_esqueleto_proprio():
    pagina = hub.montar_index(TEMPLATE_HUB_REAL, TEMPLATE_PLAYER_REAL, _lote(), [], True, AGORA)
    assert pagina.index("<title>MedHub</title>") < 8192, "o titulo so e lido nos primeiros 8 KB"
    # fora dos <script>: o JS do leitor MONTA um esqueleto para a aula no srcdoc, de proposito
    marcacao = re.sub(r"<script\b.*?</script>", "", pagina, flags=re.S | re.I)
    assert not re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", marcacao, re.I), \
        "o publish embrulha a pagina num esqueleto; o template nao traz o seu"
    assert "@hub:" not in pagina and "@player:" not in pagina


# --------------------------------------------------------------------------
# 6. Celular (feedback do operador) e teclado do player por aba
# --------------------------------------------------------------------------

def _pagina_real():
    aulas = [hub.Aula("hernias", "A Escada das Hernias", "2026-09-22", "artifacts/aula-hernias.html")]
    return hub.montar_index(TEMPLATE_HUB_REAL, TEMPLATE_PLAYER_REAL, _lote(), aulas, True, AGORA)


def test_celular_sem_sticky_sem_nowrap_e_um_wrap_so():
    pagina = _pagina_real()
    assert "sticky" not in pagina.lower()
    assert "nowrap" not in pagina.lower()
    assert pagina.count('class="wrap"') == 1


def test_abas_curtas_e_com_alvo_de_toque():
    pagina = _pagina_real()
    rotulos = re.findall(r'class="hub-aba"[^>]*>([^<]+)</button>', pagina)
    assert rotulos == ["Painel", "Aulas", "Cards", "Listas"]  # s200: "Questões" quebrava a barra no celular
    assert all(len(r) <= 15 for r in rotulos)
    regra_aba = re.search(r"\.hub-aba\{([^}]*)\}", pagina).group(1)
    assert "min-height:44px" in regra_aba
    regra_titulo = re.search(r"\.qd-tema\{([^}]*)\}", pagina).group(1)
    assert "min-width:0" in regra_titulo


def test_abas_na_ordem_painel_aulas_cards_e_painel_e_o_padrao():
    """Feedback do operador (s194): Painel primeiro, Aulas, Cards; sem hash nem aba lembrada, abre
    no Painel. Hash e aba lembrada continuam vencendo o padrao."""
    pagina = _pagina_real()
    abas = re.findall(r'<button type="button" class="hub-aba"[^>]*data-aba="(\w+)"', pagina)
    # s197: 4a aba "Questoes" (decisao do operador em 26/09/2026: o bloco de questoes mora no hub)
    assert abas == ["painel", "aulas", "cards", "questoes"]
    primeiro = re.search(r'<button type="button" class="hub-aba"[^>]*>', pagina).group(0)
    assert 'aria-selected="true"' in primeiro and 'data-aba="painel"' in primeiro
    botoes = re.findall(r'<button type="button" class="hub-aba"[^>]*>', pagina)
    assert sum('aria-selected="true"' in bt for bt in botoes) == 1
    assert 'var ABAS = ["painel", "aulas", "cards", "questoes"];' in pagina
    assert 'ir(doHash() || lembrada() || "painel", false);' in pagina
    assert ':root:not([data-aba]) #aba-painel' in pagina, "sem JS, a aba visivel e o Painel"


#: Texto de bastidor que o operador nao quer ver na tela (s194): nomes de CLI, de capability, de
#: funcao do banco, carimbo de montagem. Casado no index MONTADO, fora de comentarios.
BASTIDOR = ("ArtifactData", "--record-lote", "record_review", "fsrs_queue", "tools/painel.py",
            "Progresso, FSRS e proximas tarefas", "capability", "runtime do Artifact",
            "montado ", "DRENAR", "hub-estado", "Fallback declarado")


def _sem_comentarios(pagina):
    sem_html = re.sub(r"<!--.*?-->", "", pagina, flags=re.S)
    sem_bloco = re.sub(r"/\*.*?\*/", "", sem_html, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$|(?<=[;{}])\s*//[^\n]*", "", sem_bloco)


def test_index_montado_sem_texto_de_bastidor():
    pagina = _sem_comentarios(_pagina_real())
    achados = [t for t in BASTIDOR if t in pagina]
    assert not achados, "texto de bastidor no index montado: %s" % achados
    assert "2026-09-22h" not in pagina.split(MARCA_ABRE, 1)[0], \
        "o id da sessao nao aparece como texto antes do lote"
    sessao = re.search(r'<[^>]*id="sessao"[^>]*>', pagina).group(0)
    assert "hidden" in sessao, "o id da sessao fica no DOM, escondido"


def test_painel_sem_montagem_nao_cita_o_cli():
    pagina = _sem_comentarios(hub.montar_index(TEMPLATE_HUB_REAL, TEMPLATE_PLAYER_REAL, _lote(),
                                               [], False, AGORA))
    assert "tools/painel.py" not in pagina and "hub.py" not in pagina


def test_quadro_do_hub_esconde_o_bastidor_do_painel():
    """O painel avulso guarda o rodape de fonte (governanca); no hub ele some."""
    pagina = _pagina_real()
    assert "[data-backoffice]{display:none!important}" in pagina


def test_teclado_do_player_so_age_na_aba_cards():
    pagina = _pagina_real()
    assert "function abaDoPlayerAtiva()" in pagina
    corpo_do_handler = pagina.split('document.addEventListener("keydown", function(ev){', 1)[1]
    assert corpo_do_handler.lstrip().startswith("if(!abaDoPlayerAtiva()){ return; }")


def test_aula_e_painel_abrem_dentro_da_pagina_sem_navegar():
    pagina = _pagina_real()
    assert "fetch(href" in pagina and ".srcdoc" in pagina
    assert 'target="_blank"' not in pagina.split("<script", 1)[0], \
        "link de aula nao abre aba nova: o leitor e dentro do hub"


# --------------------------------------------------------------------------
# 7. --extrair-lote pela CLI e integracao com o repo real (read-only)
# --------------------------------------------------------------------------

def test_extrair_lote_pela_cli(tmp_path):
    lote = _lote(n=4)
    pagina = hub.montar_index(TEMPLATE_HUB_REAL, TEMPLATE_PLAYER_REAL, lote, [], False, AGORA)
    salvo = tmp_path / "viva.html"
    salvo.write_text(pagina, encoding="utf-8")
    destino = tmp_path / "lote.json"
    assert hub.main(["--extrair-lote", str(salvo), "--out-lote", str(destino)]) == 0
    assert json.loads(destino.read_text(encoding="utf-8")) == lote


def test_repo_real_monta_sem_problema(tmp_path):
    """Regressao viva, read-only: as aulas e o painel REAIS de `artifacts/` e o plano REAL do
    `ipub.db` montam sem link morto (a prova em PDF e caminho local: texto, nunca link).
    Escreve so em tmp_path."""
    manifesto, problemas, avisos = hub.construir(_lote(), raiz=ROOT, out=tmp_path / "hub",
                                                 agora=AGORA,
                                                 data_fn=lambda p, r: ("2026-09-22", None))
    assert problemas == []
    assert not [a for a in avisos if "sem tipo" in a or "candidata a arquivo" in a], avisos
    pagina = (tmp_path / "hub" / "index.html").read_text(encoding="utf-8")
    assert re.search(r'<section class="qd-sem" data-secao="\d+"', pagina), "semanas do plano real"
    assert "questões" in pagina
    reais = sorted(p.name for p in (ROOT / "artifacts").glob("aula-*.html"))
    esperado = min(len(reais), hub.CAP_AULAS)
    assert manifesto["aulas"] == esperado
    for nome in reais[:esperado]:
        assert "aulas/%s.html" % hub.slug_de(nome) in manifesto["files"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
