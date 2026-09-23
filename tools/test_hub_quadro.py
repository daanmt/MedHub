"""test_hub_quadro.py -- s194: a aba Aulas como QUADRO e o tique que republica quando a PROJECAO muda.

Pedido do operador (23/09): Aulas como backlog em que ele RISCA o que ja fez, separado por tipo
(analise/plano x aula-base x revisao direcionada); o painel conversando com a aba Cards; o hub em
sync sem esperar o lote drenar. O que esta suite trava:

1. **Registro versionado** `core/hub_quadro.json`: tipo por slug; slug desconhecido = `aula` + WARN
   no build (nunca silencioso); tipo invalido falha alto.
2. **Quadro**: uma coluna por tipo; o que esta feito no `db` sai RISCADO em "Concluidas" ja no
   build; sem `db`, o controle nasce desabilitado e a frase curta existe.
3. **Projecao**: `--precisa-publicar` diz sim/nao e a acao -- `nova_fila` (lote drenado),
   `mesmo_lote` (so painel/quadro mudou: MESMO `sessao`, MESMOS cards), `nada`. O carimbo de hora
   do painel nao conta.
4. **Tarefa de aula**: aula feita com `tarefa_id` pendente vira pendencia RELATADA (o
   `plano.py --concluir` exige `--sessao`; o tique nao inventa caminho).

Repo sintetico em tmp_path; o `ipub.db` nunca e tocado (o plano entra injetado).
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import hub  # noqa: E402
from tools.fsrs_queue import TEMPLATE_PLAYER  # noqa: E402

AGORA = datetime(2026, 9, 23, 20, 0, 0)
TEMPLATE_HUB_REAL = hub.TEMPLATE_HUB.read_text(encoding="utf-8")
TEMPLATE_PLAYER_REAL = TEMPLATE_PLAYER.read_text(encoding="utf-8")
QUADRO = {"hernias": {"tipo": "aula", "titulo": "A Escada das Hernias"},
          "autopsia": {"tipo": "analise", "titulo": "Autopsia UERJ 2023"},
          "bayes": {"tipo": "aula", "titulo": "A Escada de Bayes", "tarefa_id": 877},
          "rd-renal": {"tipo": "revisao", "titulo": "Revisao direcionada renal"}}
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


def _construir(raiz, data_fn, lote=None, quadro=None, estado=None):
    return hub.construir(lote or _lote(), raiz=raiz, out=raiz / "tmp" / "hub", agora=AGORA,
                         data_fn=data_fn, template_hub=TEMPLATE_HUB_REAL,
                         template_player=TEMPLATE_PLAYER_REAL,
                         quadro=QUADRO if quadro is None else quadro, estado_quadro=estado)


def _index(raiz):
    return (raiz / "tmp" / "hub" / "index.html").read_text(encoding="utf-8")


def _decidir(raiz, lote=None, notas=(), estado=None, plano=()):
    return hub.decidir(lote or _lote(), raiz / "tmp" / "hub", raiz=raiz, notas=list(notas),
                       estado_quadro=estado or {}, quadro=QUADRO,
                       data_fn=_repo_datas(raiz), plano_linhas=list(plano))


def _repo_datas(raiz):
    def data_fn(p, _r):
        nomes = sorted(x.name for x in (Path(raiz) / "artifacts").glob("aula-*.html"))
        return "2026-09-%02d" % (10 + nomes.index(Path(p).name)), None
    return data_fn


# --------------------------------------------------------------------------
# 1. Registro versionado
# --------------------------------------------------------------------------

def test_registro_real_semeado_com_as_sete_aulas():
    reg = hub.ler_quadro(ROOT / hub.QUADRO_REG)
    tipos = {s: v["tipo"] for s, v in reg.items()}
    assert tipos["autopsia-uerj-2023"] == "analise" and tipos["s17"] == "analise"
    for s in ("hernias", "dmg", "raciocinio-diagnostico", "topicos-pediatria", "cancer-de-mama"):
        assert tipos[s] == "aula", s
    assert reg["raciocinio-diagnostico"]["tarefa_id"] == 877
    reais = {hub.slug_de(p.name) for p in (ROOT / "artifacts").glob("aula-*.html")}
    assert reais <= set(reg), "aula real sem tipo no registro: %s" % sorted(reais - set(reg))


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
                                   template_player=TEMPLATE_PLAYER_REAL)
    assert any("registro do quadro ausente" in a for a in avisos)


def test_tipo_invalido_no_registro_falha_alto(tmp_path):
    arq = tmp_path / "q.json"
    arq.write_text(json.dumps({"itens": {"x": {"tipo": "palestra"}}}), encoding="utf-8")
    with pytest.raises(ValueError, match="palestra"):
        hub.ler_quadro(arq)


# --------------------------------------------------------------------------
# 2. O quadro no index
# --------------------------------------------------------------------------

def test_uma_coluna_por_tipo_na_ordem_e_cada_aula_na_sua(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert re.findall(r'<section class="qd-col" data-tipo="(\w+)"', pagina) == \
        ["aula", "revisao", "analise"]
    rotulos = re.findall(r'<h3 class="qd-titulo">([^<]+?) <span', pagina)
    assert rotulos == ["Aulas-base", "Revisões", "Análises"]
    assert all(len(r) <= 15 for r in rotulos)
    col = {t: pagina.split('data-tipo="%s" aria-label' % t, 1)[1].split("</section>", 1)[0]
           for t in ("aula", "revisao", "analise")}
    assert 'data-slug="autopsia"' in col["analise"] and 'data-slug="rd-renal"' in col["revisao"]
    assert 'data-slug="hernias"' in col["aula"] and 'data-slug="bayes"' in col["aula"]


def test_feito_sai_riscado_em_concluidas_no_build(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn, estado={"hernias": {"feito": True, "ts": "x"},
                                      "autopsia": {"feito": False, "ts": "y"}})
    pagina = _index(raiz)
    colunas, feitas = pagina.split('id="hub-quadro-feitas"', 1)
    assert 'data-slug="hernias"' not in colunas, "feito continua na coluna"
    item = re.search(r'<li class="qd-item" data-slug="hernias"[^>]*>.*?</li>', feitas).group(0)
    assert 'data-feito="1"' in item and 'aria-pressed="true"' in item
    assert 'id="hub-quadro-nfeitas">1<' in feitas
    assert 'data-slug="autopsia"' in colunas, "desmarcado volta para a coluna"
    assert ".qd-item[data-feito] .hub-aula-t{text-decoration:line-through" in pagina


def test_sem_db_controle_nasce_desabilitado_com_frase_curta(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    botoes = re.findall(r'<button type="button" class="qd-feito"[^>]*>', pagina)
    assert len(botoes) == 4 and all(" disabled" in b for b in botoes)
    aviso = re.search(r'<p class="qd-aviso" id="hub-quadro-aviso" hidden>([^<]+)</p>', pagina)
    assert aviso and len(aviso.group(1)) <= 80
    js = pagina.split("function iniciarQuadro()", 1)[1]
    assert 'db.collection("quadro")' in js and "semArmazenamento" in js
    assert ".set({feito: novo, ts: new Date().toISOString()})" in js


def test_quadro_celular_alvo_de_toque_e_grid_item_encolhe(tmp_path):
    raiz, data_fn = _repo(tmp_path)
    _construir(raiz, data_fn)
    pagina = _index(raiz)
    assert "sticky" not in pagina.lower() and "nowrap" not in pagina.lower()
    assert "width:44px;height:44px" in re.search(r"\.qd-feito\{([^}]*)\}", pagina).group(1)
    for regra in (r"\.qd-col\{([^}]*)\}", r"\.qd-item\{([^}]*)\}"):
        assert "min-width:0" in re.search(regra, pagina).group(1)
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
    """O "Ir para os cards" e o "abrir aula" do painel sao interceptados pelo hub."""
    assert 'querySelectorAll("a[data-hub-aba], a[data-hub-aula]")' in TEMPLATE_HUB_REAL
    assert "abrirAula(alvo)" in TEMPLATE_HUB_REAL


def test_declaracao_de_capabilities_documentada_nos_portadores():
    """A regra nova `quadro` e a declaracao COMPLETA (non-empty = full set: esquecer `sessoes`
    revogaria a escrita das notas)."""
    decl = ('{db: {rules: [{path: "", read: "view", write: "admin"}, {path: "sessoes", '
            'write: "interact"}, {path: "quadro", write: "interact"}]}}')
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
    d = _decidir(raiz, estado={"autopsia": {"feito": True}})
    assert d["acao"] == "mesmo_lote" and d["motivos"] == ["quadro de aulas mudou"]


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
    assert "restaurar(snap.docs || [])" in player


def test_ids_com_nota_le_o_dump_por_arquivo(tmp_path):
    d = tmp_path / "notas"
    d.mkdir()
    (d / "500.json").write_text('{"card_id": 500, "rating_primeira": 3}', encoding="utf-8")
    (d / "501.json").write_text('{"card_id": 501, "defeito": true}', encoding="utf-8")
    assert hub.ids_com_nota(d) == {500, 501}
    assert hub.ids_com_nota(None) == set()


def test_cli_precisa_publicar_sim_e_nao(tmp_path, capsys, monkeypatch):
    raiz, data_fn = _repo(tmp_path)
    _publicado(raiz, data_fn)
    arq_lote = tmp_path / "lote.json"
    arq_lote.write_text(json.dumps(_lote()), encoding="utf-8")
    monkeypatch.setattr(hub, "RAIZ", raiz)
    monkeypatch.setattr(hub, "QUADRO_REG", "q.json")
    (raiz / "q.json").write_text(json.dumps({"itens": QUADRO}), encoding="utf-8")
    monkeypatch.setattr(hub, "data_de_criacao", _repo_datas(raiz))
    monkeypatch.setattr(hub.db, "plano_listar", lambda: [])
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
    """O `plano.py --concluir` exige `--sessao`; o hub so relata, nunca grava o plano."""
    fonte = Path(hub.__file__).read_text(encoding="utf-8")
    assert "plano_set_status" not in fonte and "import plano" not in fonte


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
