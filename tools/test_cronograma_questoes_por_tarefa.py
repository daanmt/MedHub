"""F77 + F77b (s176): o derivador do cronograma para de jogar fora dado que ja calcula.

Dois achados irmaos, ambos da familia "construido-e-descartado":

**F77** -- `grade.json` guardava `total_questoes` so no nivel da SEMANA, e o comentario do proprio
`parse_grade` instruia o consumidor a ratear igual. Mas `_parse_detail` JA calculava as questoes
por tarefa e o valor era descartado. Na S17 o rateio dava **26,6q para toda tarefa**; as reais vao
de **16q (Pneumonias Bacterianas) a 50q (APS Revisao)** -- erro de ate 3x, justamente na dimensao
que o usuario usa para planejar o dia.

A desconfianca que motivou o descarte ("o PDF nao amarra link[i] <-> task[i]") era razoavel em
2026-07 e **nunca foi medida**. Medida: em S17-S20 a soma das tarefas bate EXATAMENTE com o total
da semana nas quatro (293/380/449/301). Dai o desenho: o dado bom viaja com marca de confianca
(`questoes_fonte`), e a semana que NAO reconcilia degrada para o rateio -- em vez de jogar fora o
dado bom em 100% das semanas por causa de uma duvida que nunca se materializou.

**F77b** -- `_parse_detail` exigia o literal `Livro Digital:`. As tarefas de "Revisao por Questoes"
usam `Assunto:`, e nasciam com `tema` VAZIO. Medido no rebuild real: tarefas sem tema caem de
**35 para 15**, e entre as `revisao_questoes` de **32 para 12** -- 20 temas que estavam escritos
no PDF e eram jogados fora.

Fixtures sinteticas com a forma do PDF; zero dependencia do `Cronograma.pdf` (que e IP e
gitignored).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import cronograma as cr  # noqa: E402


def _pagina(tarefas_resumo, tarefas_detalhe):
    """Monta uma pagina com a forma real: cabecalho, blocos de Tarefa, 'Atividades', detalhe."""
    linhas = ["Semana 17", "Resumo", ""]
    for n, corpo in tarefas_resumo:
        linhas += [f"Tarefa {n}"] + corpo
    linhas += ["Atividades"]
    for n, corpo in tarefas_detalhe:
        linhas += [f"Tarefa {n}"] + corpo
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# F77b -- `Assunto:` passa a ser reconhecido
# ---------------------------------------------------------------------------
def test_assunto_e_reconhecido_como_fonte_de_tema():
    """Verbatim da forma que nascia sem tema: as 5 'Revisao por Questoes' por ciclo."""
    d = cr._parse_detail([
        "Tarefa 12",
        "Obstetricia Assunto: Pre-Natal; Assistencia ao Parto; Vitalidade Fetal "
        "(Revisao por Questoes)",
        "Link - 30 questoes",
    ])
    assert d[12]["tema_detail"] == "Pre-Natal; Assistencia ao Parto; Vitalidade Fetal"
    assert d[12]["questoes"] == 30


def test_livro_digital_continua_reconhecido():
    """O literal antigo nao pode ter sido trocado -- foi AMPLIADO."""
    d = cr._parse_detail([
        "Tarefa 1",
        "Clinica Medica Livro Digital: Pneumonias Bacterianas (Teoria)",
        "Link - 16 questoes",
    ])
    assert d[1]["tema_detail"] == "Pneumonias Bacterianas"
    assert d[1]["questoes"] == 16


# ---------------------------------------------------------------------------
# F77 -- a contagem por tarefa viaja, com marca de confianca
# ---------------------------------------------------------------------------
def test_questoes_por_tarefa_quando_a_soma_reconcilia():
    """16q e 50q -- e nao 33q para cada, que e o que o rateio igual diria."""
    pag = _pagina(
        [(1, ["Clinica Medica", "Pneumonias Bacterianas", "(Teoria)"]),
         (2, ["Preventiva", "Atencao Primaria a Saude no Brasil", "(Revisao)"])],
        [(1, ["Clinica Medica Livro Digital: Pneumonias Bacterianas (Teoria)",
              "Link - 16 questoes"]),
         (2, ["Preventiva Livro Digital: Atencao Primaria a Saude no Brasil (Revisao)",
              "Link - 50 questoes"])])
    semanas, total = cr.parse_grade([pag])
    s = semanas[0]

    assert s["total_questoes"] == 66 and total == 66
    assert s["questoes_fonte"] == "link_no_bloco"
    por_tarefa = {t["tarefa"]: t["questoes"] for t in s["tasks"]}
    assert por_tarefa == {1: 16, 2: 50}, (
        "rateio igual daria 33q para as duas -- erro de 2x na tarefa de 16q e de 1,5x na de 50q")
    assert all(t["questoes_fonte"] == "link_no_bloco" for t in s["tasks"])


def test_soma_que_nao_reconcilia_degrada_para_rateio_e_AVISA(capsys):
    """🔴 A degradacao e DECLARADA em dois lugares: o WARN e o campo `questoes_fonte`.

    Este e o caso que a desconfianca original temia. Ele existe (1 semana em 30 no PDF real) e o
    remedio nao e jogar fora o dado bom das outras 29 -- e degradar esta, em voz alta.
    """
    pag = _pagina(
        [(1, ["Clinica Medica", "Tema A", "(Teoria)"]),
         (2, ["Cirurgia", "Tema B", "(Teoria)"])],
        [(1, ["Clinica Medica Livro Digital: Tema A (Teoria)", "Link - 10 questoes"]),
         (2, ["Cirurgia Livro Digital: Tema B (Teoria)", "Link - 10 questoes"])])
    # Link ORFAO: entra no total da semana (que varre a semana inteira) e em NENHUM bloco de
    # tarefa (o `_split_tarefas` descarta o que vem antes do 1o marcador `Tarefa N`). E a forma
    # exata da divergencia que a desconfianca original temia -- e que existe, em 1 semana de 30.
    pag = pag.replace("Atividades\n", "Atividades\nLink - 80 questoes\n")

    semanas, _ = cr.parse_grade([pag])
    s = semanas[0]

    assert s["total_questoes"] == 100
    assert s["questoes_fonte"] == "rateio_igual"
    assert {t["questoes"] for t in s["tasks"]} == {50.0}, "degradou para o rateio igual"
    err = capsys.readouterr().err
    assert "!=" in err and "rateio igual" in err, \
        "a degradacao tem de ir para stderr nomeando a divergencia: %r" % err


def test_o_campo_declara_a_fonte_em_toda_tarefa():
    """Sem `questoes_fonte` o consumidor nao sabe se o numero e medido ou rateado --
    e esse e exatamente o tipo de numero que envelhece mentindo (D67)."""
    pag = _pagina([(1, ["Clinica Medica", "Tema A", "(Teoria)"])],
                  [(1, ["Clinica Medica Livro Digital: Tema A (Teoria)", "Link - 12 questoes"])])
    semanas, _ = cr.parse_grade([pag])
    for t in semanas[0]["tasks"]:
        assert t["questoes_fonte"] in ("link_no_bloco", "rateio_igual")


# ---------------------------------------------------------------------------
# O consumidor: usa o dado por tarefa, mas nao quebra com grade.json ANTIGA
# ---------------------------------------------------------------------------
def _grade(tasks, total, com_fonte=True):
    for t in tasks:
        if not com_fonte:
            t.pop("questoes_fonte", None)
            t.pop("questoes", None)
    return {"semanas": [{"semana": 17, "inicio": "2026-07-20", "fim": "2026-07-26",
                         "total_questoes": total, "n_tasks": len(tasks), "tasks": tasks}]}


def test_radar_usa_a_contagem_por_tarefa_quando_ela_existe():
    """🔴 O consumidor que MOTIVOU o achado: a cobertura por area deixa de ser rateada.

    Com 66q em duas tarefas, o rateio igual daria 33q para cada area. As reais sao 16 e 50 --
    e e essa a coluna que o usuario le para decidir onde o cronograma ainda o cobre.
    """
    tasks = [{"tarefa": 1, "area_norm": "Cardiologia", "multi_area": False,
              "questoes": 16, "questoes_fonte": "link_no_bloco"},
             {"tarefa": 2, "area_norm": "Cirurgia", "multi_area": False,
              "questoes": 50, "questoes_fonte": "link_no_bloco"}]
    out = cr.radar(_grade(tasks, 66), [], desde_semana=1, enamed="2026-12-31")
    cob = {r["area"]: r["cobertura_pre"] for r in out["rows"]}
    assert cob["Cardiologia"] == 16 and cob["Cirurgia"] == 50, (
        "o radar rateou em vez de usar a contagem por tarefa: %r" % cob)


def test_radar_nao_quebra_com_grade_antiga_sem_o_campo():
    """Grade gerada antes desta sessao nao tem `questoes`/`questoes_fonte`. O leitor
    tem de cair no rateio em vez de levantar KeyError."""
    tasks = [{"tarefa": 1, "area_norm": "Cardiologia", "multi_area": False},
             {"tarefa": 2, "area_norm": "Cirurgia", "multi_area": False}]
    cr.radar(_grade(tasks, 66, com_fonte=False), [], desde_semana=1, enamed="2026-12-31")
