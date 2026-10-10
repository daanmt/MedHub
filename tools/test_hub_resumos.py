"""test_hub_resumos.py -- s218: os RESUMOS na Teoria do MedHub HUB e a Biblioteca por area -> disciplina.

Pedido do operador (07/10/2026): "a biblioteca deveria cobrir os resumos, que sao as fontes de fato mais
densas dos conteudos ... As revisoes podem entrar na biblioteca ... com a taxonomia correta, integrando os
respectivos blocos de disciplinas" e "nas proximas semanas ... temos apenas 69 questoes". O que esta suite
trava:

1. **Conversor md -> HTML** (`tools/hub.py`, Python puro, deterministico): todo texto escapado (F108:
   "<190" e texto, `<script>` nunca vira tag), frontmatter fora, bullets aninhados por indentacao,
   wikilink publicado vira link do leitor e o nao publicado vira texto, tabela pipe, bloco cercado em
   `<pre>` com a arvore intacta, emoji intacto no titulo e na citacao.
2. **Registro `core/hub_resumos.json`**: schema falha ALTO (GO sem disciplina, tarefa nao inteira); o
   arquivo que nao existe e AVISO e sai do lote; o registro real existe inteiro no disco (⚰️ 10/10/2026,
   part-2b: "lote 1 = 31" -- a contagem saiu, fica a forma; os testes do dado real são `vivo`).
3. **Biblioteca**: area -> disciplina; a RD de varias disciplinas aparece em CADA uma e conta 1; a RD
   nova no topo; o resumo mostra quem o cita e a RD mostra de onde saiu.
4. **Semana**: o cabecalho conta tarefas e resumos; dentro, o total REAL de questoes pendentes da semana
   (no plano real, a S4 = a soma das pendentes da semana 4), sem a soma parcial de antes.
5. **Manifesto**: as paginas `resumos/<slug>.html` no `files`, com diff por hash; o teto de entradas conta
   os resumos e estoura com erro nomeado; o `.md` corrigido muda a projecao.
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import hub  # noqa: E402
from tools.fsrs_queue import TEMPLATE_PLAYER  # noqa: E402

AGORA = datetime(2026, 10, 7, 9, 0, 0)
CAL = {3: (date(2026, 9, 28), date(2026, 10, 4)), 4: (date(2026, 10, 5), date(2026, 10, 11)),
       5: (date(2026, 10, 12), date(2026, 10, 18))}


def _t(id_, semana, tema, q=0, bloco="CM", area=None, status="pendente", fonte="rf"):
    return {"id": id_, "semana_plano": semana, "tema": tema, "q_previstas": float(q), "url_lista": None,
            "fonte": fonte, "status": status, "bloco": bloco, "ordem": id_, "area": area}


# ======================================================================== 1. conversor

def test_conversor_escapa_todo_texto_e_nunca_cria_tag():
    corpo = hub.md_para_html("# Hipercalemia <190\n\n- K <190 e **Na >130** <script>alert(1)</script>\n"
                             "- `<b>codigo</b>` & [x](javascript:alert(1))\n")
    assert "<script" not in corpo and "&lt;script&gt;alert(1)&lt;/script&gt;" in corpo
    assert "<h1>Hipercalemia &lt;190</h1>" in corpo, "F108: '<190' e texto, nunca tag"
    assert "<strong>Na &gt;130</strong>" in corpo
    assert "<code>&lt;b&gt;codigo&lt;/b&gt;</code> &amp; [x](javascript:alert(1))" in corpo
    assert "href=" not in corpo and "<b>" not in corpo, "so http(s)/mailto vira link"
    assert hub.md_para_html("[x](javascript:void)") == "<p>x</p>", "link sem http(s) vira texto"


def test_conversor_tira_o_frontmatter_e_aninha_bullets_por_indentacao():
    md = ("---\ntype: knowledge\naliases: [TB]\n---\n\n# Tuberculose\n\n"
          "- nivel 1\n    - nivel 2 (4 espacos)\n        - nivel 3\n- outro 1\n  - nivel 2 (2 espacos)\n"
          "  continua o item\n\n- depois da linha em branco\n\n1. um\n2. dois\n    1. sub\n")
    corpo = hub.md_para_html(md)
    assert "type: knowledge" not in corpo and "aliases" not in corpo
    assert corpo.startswith("<h1>Tuberculose</h1>")
    # o texto do item com sublista vai num <div>: o grifo do leitor so ancora em bloco-folha
    assert ("<ul><li><div>nivel 1</div><ul><li><div>nivel 2 (4 espacos)</div><ul><li>nivel 3</li></ul></li></ul></li>"
            "<li><div>outro 1</div><ul><li>nivel 2 (2 espacos) continua o item</li></ul></li>"
            "<li>depois da linha em branco</li></ul>") in corpo
    assert "<ol><li>um</li><li><div>dois</div><ol><li>sub</li></ol></li></ol>" in corpo
    assert hub.titulo_md(md) == "Tuberculose"


def test_wikilink_publicado_vira_link_do_leitor_e_o_nao_publicado_texto():
    pub = hub.Resumo("GO/Pré-Natal.md", "resumo-pre-natal", "Pré-Natal", "GO", "Obstetrícia", (22,), "x")
    links = hub.links_dos_resumos([pub])
    corpo = hub.md_para_html("Ver [[Pré-Natal]], [[pré-natal|o pré-natal]] e [[Toxoplasmose na Gestação]].", links)
    assert ('<a href="resumos/resumo-pre-natal.html" data-hub-aula="resumo-pre-natal" '
            'data-titulo="Pré-Natal">Pré-Natal</a>') in corpo
    assert '>o pré-natal</a>' in corpo, "alias e nome sem caixa (como no Obsidian)"
    assert "Toxoplasmose na Gestação." in corpo and corpo.count("<a ") == 2, "nao publicado = texto"


def test_tabela_pipe_vira_table_com_rolagem_propria():
    corpo = hub.md_para_html("| Droga | Dose <x |\n|---|:---:|\n| **RIP** | 10 mg/kg |\n| [[A|B]] | 2 |\n")
    assert corpo == ('<div class="tab"><table><thead><tr><th>Droga</th><th>Dose &lt;x</th></tr></thead>'
                     '<tbody><tr><td><strong>RIP</strong></td><td>10 mg/kg</td></tr>'
                     '<tr><td>B</td><td>2</td></tr></tbody></table></div>')
    assert ".tab{overflow-x:auto}" in hub.CSS_RESUMO


def test_bloco_cercado_vira_pre_escapado_com_a_arvore_intacta():
    """Adendo do principal (07/10): o fluxograma em arvore do Rastreamento Colo mora num bloco ```."""
    md = "Antes\n```\nDNA-HPV <x>\n├── Negativo -> repetir\n│     └── **nao e negrito**\n```\nDepois\n"
    corpo = hub.md_para_html(md)
    assert ('<div class="cod"><pre><code>DNA-HPV &lt;x&gt;\n├── Negativo -&gt; repetir\n'
            '│     └── **nao e negrito**</code></pre></div>') in corpo
    assert corpo.startswith("<p>Antes</p>") and corpo.endswith("<p>Depois</p>")
    assert re.search(r"\.cod pre\{[^}]*overflow-x:auto", hub.CSS_RESUMO), "a rolagem e do <pre>, nunca da pagina"
    assert "nowrap" not in hub.CSS_RESUMO


def test_emoji_intacto_no_titulo_e_na_citacao():
    md = "### ⭐ Mais cobrado\n\n> ⚠️ **Padrão de prova -- leia o enunciado**\n> - item 🔴\n"
    corpo = hub.md_para_html(md)
    assert "<h3>⭐ Mais cobrado</h3>" in corpo
    assert ("<blockquote><p>⚠️ <strong>Padrão de prova -- leia o enunciado</strong></p>\n"
            "<ul><li>item 🔴</li></ul></blockquote>") in corpo


def test_pagina_do_resumo_e_deterministica_com_tema_claro_e_escuro():
    r = hub.Resumo("Clínica Médica/Infectologia/Tuberculose.md", "resumo-tuberculose", "Tuberculose", "CM",
                   "Infectologia", (1797,), "# Tuberculose\n\n- BAAR\n")
    p1, p2 = hub.paginas_resumos([r]), hub.paginas_resumos([r])
    assert p1 == p2 and list(p1) == ["resumos/resumo-tuberculose.html"]
    pagina = p1["resumos/resumo-tuberculose.html"]
    assert pagina.startswith("<!DOCTYPE html>") and pagina.count('class="wrap"') == 1
    assert '<p class="rs-olho">Resumo · Infectologia</p>' in pagina
    assert ':root[data-theme="dark"]' in pagina and "prefers-color-scheme:dark" in pagina
    assert hub.slug_resumo("GO/[OBS] Sífilis na Gestação e Congênita.md") == "resumo-obs-sifilis-na-gestacao-e-congenita"
    longo = hub.slug_resumo("Clínica Médica/Cardiologia/" + "Palavra " * 30 + ".md")
    assert len(longo) <= hub.SLUG_RESUMO_MAX and re.fullmatch(r"resumo-[a-z0-9-]+", longo)


# ======================================================================== 2. registro

def _reg(tmp_path, itens):
    arq = tmp_path / "r.json"
    arq.write_text(json.dumps({"itens": itens}, ensure_ascii=False), encoding="utf-8")
    return arq


@pytest.mark.parametrize("itens,trecho", [
    ({"GO/Pré-Natal.md": {"tarefas": [22]}}, "GO sem `disciplina`"),
    ({"GO/Pré-Natal.md": {"tarefas": [22], "disciplina": "Pediatria"}}, "GO sem `disciplina`"),
    ({"Cirurgia/Hérnias.md": {"tarefas": ["49"]}}, "tarefas"),
    ({"Cirurgia/Hérnias.md": {"tarefas": [True]}}, "tarefas"),
    ({"Cirurgia/Hérnias.md": {"tarefas": [49], "disciplina": "Cirugia"}}, "disciplina"),
    ({"Outra/X.md": {"tarefas": [1]}}, "fora das pastas"),
    ({"Cirurgia/Hérnias.txt": {"tarefas": [1]}}, ".md"),
], ids=["go-sem-disciplina", "go-disciplina-errada", "tarefa-texto", "tarefa-bool", "disciplina-fora",
        "pasta-desconhecida", "nao-md"])
def test_registro_de_resumos_com_schema_errado_falha_alto(tmp_path, itens, trecho):
    with pytest.raises(ValueError, match=re.escape(trecho)):
        hub.ler_resumos(_reg(tmp_path, itens))


def test_resumo_inexistente_e_aviso_nomeado_e_sai_do_lote(tmp_path):
    (tmp_path / "resumos" / "Cirurgia").mkdir(parents=True)
    (tmp_path / "resumos" / "Cirurgia" / "Hérnias.md").write_text("# Hérnias\n", encoding="utf-8")
    reg = hub.ler_resumos(_reg(tmp_path, {"Cirurgia/Hérnias.md": {"tarefas": [49]},
                                          "Cirurgia/Sumiu.md": {"tarefas": [50]}}))
    resumos, avisos = hub.coletar_resumos(tmp_path, reg)
    assert [r.slug for r in resumos] == ["resumo-hernias"]
    assert resumos[0].area == "CIR" and resumos[0].disciplina == "Cirurgia" and resumos[0].tarefas == (49,)
    assert len(avisos) == 1 and "resumos/Cirurgia/Sumiu.md" in avisos[0] and hub.RESUMOS_REG in avisos[0]
    with pytest.raises(ValueError, match="slug de resumo repetido"):
        hub.coletar_resumos(tmp_path, reg, aulas=[hub.Aula("resumo-hernias", "x", "2026-10-01", "a")])


#: O banco que os vivos do plano medem (part-2b). Constante de módulo para o teste de skip apontá-la
#: para um arquivo inexistente.
REAL_DB = ROOT / "ipub.db"


def _defeitos_do_lote(raiz):
    """(registro, resumos, defeitos) do `core/hub_resumos.json` de `raiz` -- a FORMA (part-2b), sem a
    contagem do lote: registro e disco concordam (nenhum aviso de resumo inexistente e
    `len(resumos) == len(reg)`), slug único e dentro do `pendIdValido` (até 120 com o `doc_`), área e
    disciplina do vocabulário. Lido por `hub.ler_resumos`/`hub.coletar_resumos` (o schema já falha ALTO
    lá). [] = ok. O vivo e o gêmeo passam por aqui."""
    raiz = Path(raiz)
    reg = hub.ler_resumos(raiz / hub.RESUMOS_REG)
    resumos, avisos = hub.coletar_resumos(raiz, reg)
    defeitos = list(avisos)
    if len(resumos) != len(reg):
        defeitos.append("registro com %d resumos, disco com %d" % (len(reg), len(resumos)))
    if len({r.slug for r in resumos}) != len(resumos):
        defeitos.append("slug de resumo repetido no lote")
    defeitos += ["slug longo demais para o pendIdValido: %s" % r.slug for r in resumos
                 if len("doc_" + r.slug) > 120]
    areas = set(hub.AREA_DA_PASTA.values())
    defeitos += ["resumo fora das áreas %s: %s (%s)" % (sorted(areas), r.caminho, r.area)
                 for r in resumos if r.area not in areas]
    defeitos += ["resumo com disciplina fora do vocabulário: %s (%s)" % (r.caminho, r.disciplina)
                 for r in resumos if r.disciplina not in hub.DISCIPLINAS]
    return reg, resumos, defeitos


@pytest.mark.vivo
def test_registro_real_do_lote_existe_inteiro_e_sem_slug_repetido():
    """O registro REAL tem a forma de `_defeitos_do_lote`: registro e disco concordam, slug único e
    dentro do pendIdValido, área e disciplina do vocabulário. Pula com motivo (`VIVO:`) sem o registro,
    sem `resumos/` ou com o registro vazio."""
    if not (ROOT / hub.RESUMOS_REG).is_file():
        pytest.skip("VIVO: %s ausente -- lote de resumos real não medido" % hub.RESUMOS_REG)
    if not (ROOT / hub.DIR_RESUMOS).is_dir():
        pytest.skip("VIVO: %s/ ausente -- registro x disco não medido" % hub.DIR_RESUMOS)
    reg, resumos, defeitos = _defeitos_do_lote(ROOT)
    if not reg:
        pytest.skip("VIVO: %s sem item -- lote de resumos real não medido" % hub.RESUMOS_REG)
    print(f"  lote: {len(resumos)} resumos de {len(reg)} no registro, áreas {sorted({r.area for r in resumos})}")
    # ⚰️ 10/10/2026 (part-2b): `len(resumos) == len(reg) == 31`, `len(slugs) == 31`, as áreas
    # == {CM, CIR, MFC, PED, GO} e a (área, disciplina, tarefas) da Tuberculose -- o lote 1 da s218
    # contado à mão; resumo novo no registro derrubava a suíte. Contagem é relatório (o print).
    assert defeitos == [], defeitos


def test_gemeo_hermetico_do_lote_acusa_registro_sem_arquivo(tmp_path):
    """Gêmeo hermético do vivo acima (part-2b): o MESMO `_defeitos_do_lote` sobre um repo sintético.
    Registro e disco concordando, nada a acusar; o resumo registrado que não existe no disco é acusado
    pelo caminho e pela discordância registro x disco. O schema torto (falha ALTO) tem gêmeo próprio,
    `test_registro_de_resumos_com_schema_errado_falha_alto`; o slug repetido,
    `test_resumo_inexistente_e_aviso_nomeado_e_sai_do_lote`."""
    raiz = _repo(tmp_path)
    _reg, resumos, defeitos = _defeitos_do_lote(raiz)
    assert [r.slug for r in resumos] == ["resumo-tuberculose"] and defeitos == [], defeitos
    reg = json.loads((raiz / hub.RESUMOS_REG).read_text(encoding="utf-8"))
    reg["itens"]["Cirurgia/Sumiu.md"] = {"tarefas": [50]}
    (raiz / hub.RESUMOS_REG).write_text(json.dumps(reg, ensure_ascii=False), encoding="utf-8")
    _reg, _r, defeitos = _defeitos_do_lote(raiz)
    assert len(defeitos) == 2, defeitos
    assert "resumos/Cirurgia/Sumiu.md" in defeitos[0] and "registro com 2 resumos, disco com 1" in defeitos[1]


# ======================================================================== 3. Biblioteca area -> disciplina

R_TB = hub.Resumo("Clínica Médica/Infectologia/Tuberculose.md", "resumo-tuberculose", "Tuberculose", "CM",
                  "Infectologia", (1797,), "# Tuberculose\n")
R_HAS = hub.Resumo("Clínica Médica/Cardiologia/HAS.md", "resumo-has", "HAS", "CM", "Cardiologia", (19,), "# HAS\n")
R_PN = hub.Resumo("GO/Pré-Natal.md", "resumo-pre-natal", "Pré-Natal", "GO", "Obstetrícia", (22,), "# PN\n")
REG = {"tb-360": {"tipo": "aula", "titulo": "Tuberculose 360", "tarefa_id": 1797},
       "rd-pilulas": {"tipo": "revisao", "titulo": "Pílulas", "disciplinas": ["Infectologia", "Cardiologia", "Obstetrícia"],
                      "resumos": ["Clínica Médica/Infectologia/Tuberculose.md", "Pediatria/Diarreia.md"]},
       "rd-velha": {"tipo": "revisao", "titulo": "Velha lida", "disciplinas": ["Infectologia"]}}
AULAS = [hub.Aula("tb-360", "x", "2026-10-06", "artifacts/aula-tb-360.html"),
         hub.Aula("rd-pilulas", "x", "2026-10-05", "artifacts/aula-rd-pilulas.html"),
         hub.Aula("rd-velha", "x", "2026-10-01", "artifacts/aula-rd-velha.html")]
PLANO = [_t(1797, 3, "TB 360", 0, area="Infecto", status="feita", fonte="custom"),
         _t(19, 4, "HAS", 42, area="Cardiologia"), _t(22, 4, "Pré-Natal", 36, bloco="GO", area="Obstetrícia"),
         _t(23, 4, "Lista sem aula", 100, area="Pneumo"), _t(30, 5, "Outra", 50)]


def _quadro(estado=None):
    return hub.html_quadro_de(AULAS, REG, estado or {"rd-velha": {"feito": True}}, PLANO, CAL, date(2026, 10, 7),
                              [R_TB, R_HAS, R_PN])


def _area(pagina, area):
    return re.search(r'<details class="qd-area" data-area="%s">.*?</details>' % area, pagina, re.S).group(0)


def _discs(bloco):
    return [(d, re.findall(r'data-(?:slug|resumo)="([\w-]+)"', corpo))
            for d, corpo in re.findall(r'<div class="qd-disc" data-disc="([^"]+)">(.*?)</ul></div>', bloco, re.S)]


def test_rd_de_varias_disciplinas_aparece_em_cada_uma_e_a_nova_no_topo():
    pagina, avisos = _quadro()
    assert not [a for a in avisos if "grande area" in a], avisos
    cm = _area(pagina, "CM")
    assert _discs(cm) == [("Cardiologia", ["rd-pilulas", "resumo-has"]),
                          ("Infectologia", ["rd-pilulas", "resumo-tuberculose", "tb-360", "rd-velha"])], \
        "A-Z; dentro: a RD nova, os resumos, as aulas, a RD lida"
    assert _discs(_area(pagina, "GO")) == [("Obstetrícia", ["rd-pilulas", "resumo-pre-natal"])]
    assert '<span class="qd-n" data-n>5</span><span class="qd-novas" data-novas>1 nova</span></summary>' in cm, \
        "a area conta cada documento uma vez (a RD de 2 disciplinas da CM conta 1)"
    assert 'id="hub-quadro-nfeitas">6</span><span class="qd-novas" id="hub-quadro-novas" data-novas>1 nova</span>' in pagina
    assert 'data-area="VARIAS"' not in pagina, "a RD declara as disciplinas: nada em Varias areas"


def test_ligacoes_obsidian_resumo_citado_e_fontes_da_rd():
    pagina, _ = _quadro()
    tb = re.search(r'<li class="qd-item qd-resumo" data-resumo="resumo-tuberculose".*?</li>', pagina, re.S).group(0)
    assert ('<p class="qd-lig"><span class="tenue">Citado em:</span> '
            '<a class="hub-aula" href="aulas/tb-360.html" data-titulo="Tuberculose 360">Tuberculose 360</a> · '
            '<a class="hub-aula" href="aulas/rd-pilulas.html" data-titulo="Pílulas">Pílulas</a></p>') in tb
    assert '<a class="hub-aula" href="resumos/resumo-tuberculose.html" data-titulo="Tuberculose">abrir resumo</a>' in tb
    rd = re.search(r'<li class="qd-item"[^>]*data-slug="rd-pilulas".*?</li>', pagina, re.S).group(0)
    assert ('<p class="qd-lig"><span class="tenue">Fontes:</span> <a class="hub-aula" href="resumos/resumo-tuberculose.html" '
            'data-titulo="Tuberculose">Tuberculose</a> · <span>Diarreia</span></p>') in rd, "nao publicado = texto"
    mapa = json.loads(re.search(r'<script type="application/json" id="hub-resumos">(.*?)</script>', pagina).group(1))
    assert mapa["Clínica Médica/Infectologia/Tuberculose.md"] == {
        "href": "resumos/resumo-tuberculose.html", "slug": "resumo-tuberculose", "titulo": "Tuberculose"}


# ======================================================================== 4. semana

def test_semana_conta_tarefas_e_resumos_e_diz_o_total_real_do_plano():
    pagina, _ = _quadro()
    sem4 = re.search(r'<section class="qd-sem" data-secao="4".*?</section>', pagina, re.S).group(0)
    assert re.search(r'<h3 class="qd-titulo">Semana 4 · 05/10 a 11/10 <span class="qd-n"><span data-n>0</span> '
                     r'<span data-nrot>tarefas</span> · 2 resumos</span></h3>', sem4)
    assert ('<p class="qd-qsem">Questões da semana: <b>178</b>, na <a href="#questoes" data-hub-aba="questoes" '
            'data-hub-modo="questoes">aba Listas</a></p>') in sem4, "19 + 22 + 23: TODAS as pendentes da semana"
    assert ('<details class="qd-resumos"><summary>Resumos desta semana <span class="qd-n">2</span></summary>'
            '<ul class="qd-rlista"><li><a class="hub-aula" href="resumos/resumo-has.html" data-titulo="HAS">HAS</a></li>'
            '<li><a class="hub-aula" href="resumos/resumo-pre-natal.html"') in sem4
    assert "questões</span>" not in sem4, "a soma parcial saiu do cabecalho"


#: O cabeçalho de uma seção de SEMANA da Teoria: "<N> tarefa(s)" e, quando há, " · <N> resumo(s)".
_RE_CABECALHO_SEM = re.compile(r'<section class="qd-sem" data-secao="(\d+)"[^>]*><h3 class="qd-titulo">[^<]*'
                               r'<span class="qd-n"><span data-n>\d+</span> <span data-nrot>tarefas?</span>'
                               r'(?: · (\d+) resumos?)?</span></h3>')


def _semanas_divergentes(pagina, linhas, resumos):
    """[(semana, campo, na página, esperado)] das seções de SEMANA da Teoria -- a forma do s218 em TODA
    semana que a página mostra (part-2b; antes, só a S4): a linha "Questões da semana" = a soma de `_q_de`
    das pendentes da semana no plano (0 = linha ausente) e o "N resumos" do cabeçalho = os resumos cujas
    tarefas estão pendentes nela. Cabeçalho fora da forma também é acusado. [] = ok."""
    q_pagina = _q_teoria(pagina)
    cabecalhos = {m.group(1): int(m.group(2) or 0) for m in _RE_CABECALHO_SEM.finditer(pagina)}
    saida = []
    for semana in sorted((k for k in q_pagina if k.isdigit()), key=int):
        da_semana = [l for l in linhas if l.get("status") == "pendente"
                     and l.get("semana_plano") is not None and int(l["semana_plano"]) == int(semana)]
        esperado = int(sum(hub._q_de(l) for l in da_semana))
        if q_pagina[semana][0] != esperado:
            saida.append((semana, "questões", q_pagina[semana][0], esperado))
        n_resumos = len(hub._resumos_de(resumos, da_semana))
        if semana not in cabecalhos:
            saida.append((semana, "cabeçalho", None, n_resumos))
        elif cabecalhos[semana] != n_resumos:
            saida.append((semana, "resumos", cabecalhos[semana], n_resumos))
    return saida


@pytest.mark.vivo
def test_semana_4_do_plano_real_diz_a_soma_das_pendentes(monkeypatch):
    """O plano REAL: toda semana que a Teoria mostra diz o total REAL de questões pendentes dela e conta
    os seus resumos (`_semanas_divergentes`). Nasceu na S4 (s218: "69 questões" nas semanas 4 a 7, que
    tinham 2.750 pendentes); a part-2b mede TODAS as semanas da página -- a S4 sem pendentes, ou fora
    da página, não derruba mais a suíte.

    Pula com motivo (`VIVO:`) sem banco, sem plano ou sem semana no quadro; a guarda vem antes de
    qualquer conexão e o `db.DB_PATH` aponta para o banco que ela conferiu."""
    if not REAL_DB.is_file():
        pytest.skip("VIVO: ipub.db ausente -- total por semana da Teoria no plano real não medido")
    monkeypatch.setattr(hub.db, "DB_PATH", str(REAL_DB))
    linhas, aviso = hub._ler_plano()
    if aviso or not linhas:
        pytest.skip("VIVO: plano real indisponível (%s) -- total por semana não medido" % (aviso or "vazio"))
    cal = hub.calendario_trilha()
    reg = hub.ler_quadro(ROOT / hub.QUADRO_REG)
    resumos, _ = hub.coletar_resumos(ROOT)
    aulas = [hub.Aula(s, s, "2026-10-01", "artifacts/aula-%s.html" % s) for s in reg]
    pagina, _ = hub.html_quadro_de(aulas, reg, {}, linhas, cal, date(2026, 10, 7), resumos)
    semanas = [k for k in _q_teoria(pagina) if k.isdigit()]
    if not semanas:
        pytest.skip("VIVO: plano real sem semana na Teoria de 07/10 -- total por semana não medido")
    print(f"  semanas na Teoria: {semanas}")
    # ⚰️ 10/10/2026 (part-2b): `re.search(... data-secao="4" ...).group(0)` -- só a S4, que levantava
    # quando ela saía da página -- e o cabeçalho da S4 obrigado a ter resumo (s222: "31 -> 30 ao concluir
    # a t40"). A forma vale agora para toda semana, com ou sem resumo.
    assert _semanas_divergentes(pagina, linhas, resumos) == []
    assert not re.search(r"\d+ questões</span></h3>", pagina), "nenhum cabecalho soma questoes"


def test_gemeo_semana_com_total_ou_resumos_errados_e_acusada():
    """Gêmeo hermético do vivo acima (part-2b): o MESMO `_semanas_divergentes` sobre o quadro sintético
    (`test_semana_conta_tarefas_e_resumos_e_diz_o_total_real_do_plano` é o golden dele). Correto, nada a
    acusar; a soma PARCIAL do s218 plantada na S4 e a contagem de resumos errada são acusadas."""
    pagina, _ = _quadro()
    resumos = [R_TB, R_HAS, R_PN]
    assert _semanas_divergentes(pagina, PLANO, resumos) == []
    parcial = pagina.replace("Questões da semana: <b>178</b>", "Questões da semana: <b>69</b>")
    assert parcial != pagina
    assert _semanas_divergentes(parcial, PLANO, resumos) == [("4", "questões", 69, 178)]
    um = pagina.replace("tarefas</span> · 2 resumos</span>", "tarefas</span> · 1 resumo</span>")
    assert um != pagina
    assert _semanas_divergentes(um, PLANO, resumos) == [("4", "resumos", 1, 2)]


# ======================================================================== 5. manifesto e build

def _repo(tmp_path):
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "aula-tb-360.html").write_text("<title>TB</title><p>x</p>", encoding="utf-8")
    pasta = tmp_path / "resumos" / "Clínica Médica" / "Infectologia"
    pasta.mkdir(parents=True)
    (pasta / "Tuberculose.md").write_text("---\na: b\n---\n# Tuberculose\n\n- <190\n", encoding="utf-8")
    (tmp_path / "core").mkdir()
    (tmp_path / hub.RESUMOS_REG).write_text(json.dumps(
        {"itens": {"Clínica Médica/Infectologia/Tuberculose.md": {"tarefas": [1797]}}}, ensure_ascii=False),
        encoding="utf-8")
    return tmp_path


def _build(raiz, publicado=(), **kw):
    return hub.construir({"sessao": "x", "cards": []}, raiz=raiz, out=raiz / "tmp" / "hub", agora=AGORA,
                         publicado=publicado, data_fn=lambda p, r: ("2026-10-06", None),
                         template_hub=hub.TEMPLATE_HUB.read_text(encoding="utf-8"),
                         template_player=TEMPLATE_PLAYER.read_text(encoding="utf-8"),
                         quadro={"tb-360": {"tipo": "aula", "titulo": "TB 360", "tarefa_id": 1797}},
                         plano_linhas=PLANO, calendario=CAL, **kw)


def test_build_gera_as_paginas_e_o_manifesto_com_diff_por_hash(tmp_path):
    raiz = _repo(tmp_path)
    manifesto, problemas, avisos = _build(raiz)
    assert problemas == [] and manifesto["resumos"] == 1
    pub = "resumos/resumo-tuberculose.html"
    assert manifesto["files"][pub] == "tmp/hub/resumos/resumo-tuberculose.html"
    pagina = (raiz / "tmp" / "hub" / pub).read_text(encoding="utf-8")
    assert "<li>&lt;190</li>" in pagina and "a: b" not in pagina
    assert 'href="%s"' % pub in (raiz / "tmp" / "hub" / "index.html").read_text(encoding="utf-8")
    hub.confirmar(raiz / "tmp" / "hub", agora=AGORA)
    vivos = [(p, e["bytes"]) for p, e in json.loads((raiz / "tmp" / "hub" / hub.REGISTRO)
                                                     .read_text(encoding="utf-8"))["arquivos"].items()]
    manifesto, _p, _a = _build(raiz, publicado=vivos)
    assert pub in manifesto["mantidos"] and pub not in manifesto["files"], "intocado nao sobe de novo"
    lote = {"sessao": "x", "cards": []}
    decide = lambda: hub.decidir(lote, raiz / "tmp" / "hub", raiz=raiz, notas=[], estado_quadro={},  # noqa: E731
                                 quadro={"tb-360": {"tipo": "aula", "titulo": "TB 360", "tarefa_id": 1797}},
                                 data_fn=lambda p, r: ("2026-10-06", None), plano_linhas=PLANO, calendario=CAL,
                                 agora=AGORA)
    assert decide()["motivos"] == ["lote drenado (0/0)"] or decide()["acao"] == "nova_fila"
    md = raiz / "resumos" / "Clínica Médica" / "Infectologia" / "Tuberculose.md"
    md.write_text(md.read_text(encoding="utf-8") + "- corrigido\n", encoding="utf-8")
    assert "resumos mudaram" in decide()["motivos"], "o .md corrigido republica sem lote novo"
    manifesto, _p, _a = _build(raiz, publicado=vivos)
    assert manifesto["files"].get(pub), "mudou: sobe de novo"


def test_teto_de_entradas_conta_os_resumos_e_estoura_com_erro_nomeado():
    aulas = [hub.Aula("a%d" % i, "A", "2026-09-01", "artifacts/aula-a%d.html" % i) for i in range(200)]
    resumos = [("resumos/resumo-%d.html" % i, "tmp/hub/resumos/resumo-%d.html" % i) for i in range(45)]
    files = hub.montar_manifesto(aulas, "artifacts/painel.html", (), resumos)
    assert len(files) + 1 == hub.TETO_ENTRADAS, "200 aulas + 45 resumos + painel + pagina = o teto"
    with pytest.raises(ValueError, match=r"200 aulas, 46 resumos, 1 painel.*hub_resumos"):
        hub.montar_manifesto(aulas, "artifacts/painel.html", (), resumos + [("resumos/resumo-x.html", "x")])


def test_p21_aba_listas_sem_resumo_da_tarefa_e_a_teoria_segue_com_ele():
    """⚰️ s218 (P2): o "resumo: <titulo>" debaixo das listas da aba Listas (via `dados_ligacoes`). P21
    (s220, pedido do operador: "se estou em listas e clico na tarefa ... devo ir especificamente para
    as questoes"): a aba Listas e so a lista. O resumo da tarefa segue na Teoria ("Resumos desta
    semana") e na Biblioteca; a "Fonte: resumos/X.md" da RD segue virando link no leitor."""
    assert not hasattr(hub, "dados_ligacoes") and not hasattr(hub, "html_ligacoes")
    js = hub.TEMPLATE_HUB.read_text(encoding="utf-8")
    assert "resumo: " not in js and "qz-aula" not in js, "a aba Listas nao rotula resumo nem aula"
    assert "fonteLigar(doc)" in js and 'id="hub-resumos"' not in js, "o mapa vem do build, a ligacao do leitor"


# ======================================================================== 6. Teoria x Painel (adendo do principal)

def _q_teoria(pagina):
    """{secao: (q da semana, q com as atrasadas | None)} das linhas "Questoes ..." da Teoria."""
    saida = {}
    for chave, corpo in re.findall(r'<section class="qd-sem" data-secao="([^"]+)".*?>(.*?)</section>', pagina, re.S):
        m = re.search(r'<p class="qd-qsem">[^:]+: <b>(\d+)</b>(?: · com as atrasadas: <b>(\d+)</b>)?', corpo)
        saida[chave] = (int(m.group(1)), int(m.group(2)) if m.group(2) else None) if m else (0, None)
    return saida


def _divergencias_painel(linhas, cal, hoje, pagina):
    """(panorama | None, q da Teoria, [(semana, campo, na Teoria, no Painel)]): a semana corrente do Painel
    (`q_abertas`, que SOMA as atrasadas) e cada semana da rota contra a linha "Questões" da Teoria. A
    corrente do Painel sem seção na Teoria também diverge (part-2b: antes, `KeyError`). [] = as duas
    telas dizem o mesmo. O vivo e o gêmeo passam por aqui."""
    from tools import plano
    pan = plano.panorama(linhas, cal, hoje)
    q = _q_teoria(pagina)
    if pan is None:
        return None, q, []
    divergencias = []
    atual = str(pan["semana"])
    if atual not in q:
        divergencias.append((atual, "seção", None, pan["q_abertas"]))
    else:
        corrente = q[atual][1] if q[atual][1] is not None else q[atual][0]
        if corrente != pan["q_abertas"]:
            divergencias.append((atual, "corrente", corrente, pan["q_abertas"]))
    for r in pan["rota"]:
        semana = str(r["semana"])
        if semana in q and q[semana][0] != r["q"]:
            divergencias.append((semana, "rota", q[semana][0], r["q"]))
    return pan, q, divergencias


def _confere_com_o_painel(linhas, cal, hoje, pagina):
    pan, q, divergencias = _divergencias_painel(linhas, cal, hoje, pagina)
    assert pan is not None, "o plano sintético tem semana corrente"
    assert divergencias == [], "a semana corrente: o Painel soma as atrasadas -- %s" % divergencias
    return pan, q


def test_total_da_semana_na_teoria_e_o_do_painel_com_e_sem_atrasadas():
    """A mesma regua (`_q_de` = `plano._q`, so pendentes): a rota do Painel (`r["q"]`) e a semana da Teoria
    batem; a corrente do Painel (`q_abertas`) INCLUI as atrasadas -- a Teoria diz o mesmo numero ao lado."""
    linhas = [_t(10, 3, "Atrasada com aula", 30, fonte="custom"), _t(11, 3, "Atrasada lista", 20),
              _t(19, 4, "HAS", 42, area="Cardiologia"), _t(22, 4, "PN", 36, bloco="GO"),
              _t(30, 5, "Outra", 50), _t(31, 5, "Feita", 70, status="feita")]
    r_atr = hub.Resumo("Clínica Médica/Pneumologia/X.md", "resumo-x", "X", "CM", "Pneumologia", (11,), "# X\n")
    pagina, _ = hub.html_quadro_de(AULAS, REG, {}, linhas, CAL, date(2026, 10, 7), [R_HAS, R_PN, r_atr])
    pan, q = _confere_com_o_painel(linhas, CAL, date(2026, 10, 7), pagina)
    assert q["atrasadas"] == (50, None) and q["4"] == (78, 128) and pan["q_abertas"] == 128
    sem_atraso = [l for l in linhas if l["semana_plano"] != 3]
    pagina, _ = hub.html_quadro_de(AULAS, REG, {}, sem_atraso, CAL, date(2026, 10, 7), [R_HAS, R_PN])
    assert _q_teoria(pagina)["4"] == (78, None), "sem atrasada, um numero so"


@pytest.mark.vivo
def test_plano_real_teoria_e_painel_dizem_o_mesmo_total_por_semana(monkeypatch):
    """O plano REAL: a Teoria e o Painel dizem o mesmo total por semana (`_divergencias_painel`) -- a
    corrente com as atrasadas, as da rota sem elas. Part-2b: a corrente do Painel sem seção na Teoria
    vira divergência nomeada (antes, `KeyError`), e o plano sem semana corrente pula.

    Pula com motivo (`VIVO:`) sem banco, sem plano ou sem semana corrente; a guarda vem antes de
    qualquer conexão e o `db.DB_PATH` aponta para o banco que ela conferiu."""
    if not REAL_DB.is_file():
        pytest.skip("VIVO: ipub.db ausente -- Teoria x Painel no plano real não medido")
    monkeypatch.setattr(hub.db, "DB_PATH", str(REAL_DB))
    linhas, aviso = hub._ler_plano()
    if aviso or not linhas:
        pytest.skip("VIVO: plano real indisponível (%s) -- Teoria x Painel não medido" % (aviso or "vazio"))
    cal = hub.calendario_trilha()
    reg = hub.ler_quadro(ROOT / hub.QUADRO_REG)
    resumos, _ = hub.coletar_resumos(ROOT)
    aulas = [hub.Aula(s, s, "2026-10-01", "artifacts/aula-%s.html" % s) for s in reg]
    hoje = date(2026, 10, 7)
    pagina, _ = hub.html_quadro_de(aulas, reg, {}, linhas, cal, hoje, resumos)
    pan, _q, divergencias = _divergencias_painel(linhas, cal, hoje, pagina)
    if pan is None:
        pytest.skip("VIVO: plano real sem semana corrente em 07/10 -- Teoria x Painel não medido")
    assert divergencias == [], "Teoria x Painel: %s" % divergencias


def test_gemeo_teoria_que_diverge_do_painel_e_acusada():
    """Gêmeo hermético do vivo acima (part-2b): o MESMO `_divergencias_painel` sobre o quadro sintético
    (`test_total_da_semana_na_teoria_e_o_do_painel_com_e_sem_atrasadas` cobre as atrasadas). As duas
    telas batendo, nada a acusar; a Teoria com outro número na semana corrente, ou sem a seção dela,
    é acusada."""
    hoje = date(2026, 10, 7)
    pagina, _ = _quadro()
    pan, _q, div = _divergencias_painel(PLANO, CAL, hoje, pagina)
    assert pan["semana"] == 4 and div == [], div
    torta = pagina.replace("Questões da semana: <b>178</b>", "Questões da semana: <b>69</b>")
    assert _divergencias_painel(PLANO, CAL, hoje, torta)[2] == [("4", "corrente", 69, 178)]
    sem_s4 = re.sub(r'<section class="qd-sem" data-secao="4".*?</section>', "", pagina, flags=re.S)
    assert _divergencias_painel(PLANO, CAL, hoje, sem_s4)[2] == [("4", "seção", None, 178)]


@pytest.mark.parametrize("vivo", ["test_registro_real_do_lote_existe_inteiro_e_sem_slug_repetido",
                                  "test_semana_4_do_plano_real_diz_a_soma_das_pendentes",
                                  "test_plano_real_teoria_e_painel_dizem_o_mesmo_total_por_semana"])
def test_vivos_pulam_com_motivo_sem_o_dado(tmp_path, monkeypatch, vivo):
    """DoD 1 da part-2b: sem o registro de resumos e sem o banco do plano, cada vivo PULA com motivo
    `VIVO:` -- não volta verde nem cai em asserção sobre dado vazio -- e não cria o banco."""
    import inspect
    monkeypatch.setattr(hub, "RESUMOS_REG", "core/nao-existe-hub-resumos.json")
    ausente = tmp_path / "sem-banco" / "ipub.db"
    monkeypatch.setitem(globals(), "REAL_DB", ausente)
    fn = globals()[vivo]
    kwargs = {"monkeypatch": monkeypatch} if "monkeypatch" in inspect.signature(fn).parameters else {}
    with pytest.raises(pytest.skip.Exception, match=r"VIVO:"):
        fn(**kwargs)
    assert not ausente.exists() and not ausente.parent.exists(), "a guarda tem de vir antes do connect"
