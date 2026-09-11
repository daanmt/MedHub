"""Guarda de revogacao da heuristica F7 (s177, item 1.5 da fila de engenharia).

A heuristica de competidor (`check_discriminacao_lexicon` + o lexico
`tools/data/competidores_categorias.json`) foi morta em 11/09/2026 depois da
medicao unica que o `/ai-eng` pediu: campo de visao de 8 cards elegiveis em
1611 (um unico eixo clinico) e precisao 1/2 -- o disparo #913 era FALSO porque
aquele card discrimina por IDADE, nao por fluxo pulmonar. A classe do F7
("a armadilha se defende do competidor ERRADO") e semantica e fica DECLARADA
como nao-verificavel por gate (AGENTE.md secao 10.8), nunca convertida em
metrica para o painel ficar verde.

Por que uma DELECAO ganha suite: o F90 ensinou que revogar tem tres passos --
declarar, lapidar no portador que alguem le, e **registrar** onde uma maquina
veja. Para clausula de texto o registro e o `_TERMOS_REVOGADOS`; para codigo
morto o registro e este teste. Sem ele, a unica coisa que impede a heuristica
de voltar num commit futuro e alguem lembrar da medicao.

Rider: ate hoje NENHUM teste importava `audit_flashcard_quality.py` (486
linhas, 8 sinais servindo o `/curar-cards`). Este e o primeiro -- o mesmo
Reachability-Debt no instrumento que manteve o F94 invisivel.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.audit_flashcard_quality as afq  # noqa: E402

SIMBOLOS_MORTOS = ("check_discriminacao_lexicon", "LEXICON_PATH", "_norm_txt")


def test_simbolos_da_heuristica_nao_ressuscitam():
    vivos = [nome for nome in SIMBOLOS_MORTOS if hasattr(afq, nome)]
    assert not vivos, (
        f"simbolo da heuristica F7 de volta no modulo: {vivos}. "
        "A revogacao foi medida em 11/09/2026 (precisao 1/2, alcance 8/1611); "
        "reintroduzir exige NOVA medicao e lapide nova, nao um revert."
    )


def test_lexico_nao_volta_ao_disco():
    lexico = ROOT / "tools" / "data" / "competidores_categorias.json"
    assert not lexico.exists(), (
        f"{lexico} voltou. O lexico dependia de curadoria continua que nunca "
        "aconteceu (68 dias com os 2 termos-semente) -- era o insumo, nao o gate."
    )


def test_lapide_segue_no_sitio():
    """A lapide e o passo (2) do ritual: ela morre so com nova decisao escrita."""
    src = (ROOT / "tools" / "audit_flashcard_quality.py").read_text(encoding="utf-8")
    assert "HEURÍSTICA F7 -- REVOGADA" in src
    assert "tools/reforja.py --fila" in src, (
        "a lapide tem que continuar apontando para onde os dois achados reais "
        "do F7 (#95, #120) viraram estado -- senao a revogacao vira perda."
    )


def test_cli_ainda_monta_sem_a_heuristica():
    """Smoke de import + superficie: a delecao nao podia levar o CLI junto."""
    for nome in ("main", "build_sql", "count_signal", "SIGNALS"):
        assert hasattr(afq, nome), f"{nome} sumiu do audit_flashcard_quality"
    assert "alt_letter" in afq.SIGNALS
