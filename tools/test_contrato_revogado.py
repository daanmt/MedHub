"""Regressao do gate CONTRATO_REVOGADO (G12/G11, s171).

O defeito: o contrato `revisao-calibrada` foi para v1.3 declarando na Clausula 11
que o PREPARAR, a Camada 0 e a Camada 1 "deixam de existir" -- e 12 linhas ATIVAS
do proprio contrato continuaram prescrevendo o mecanismo morto, alem dos
portadores executaveis que o agente de fato le.

Por que o oraculo e um lint e nao uma leitura: no dia em que o defeito foi achado,
tres metodos deram tres numeros para a MESMA pergunta -- leitura humana 1,
enumeracao sobre grep truncado em 110 colunas 10, grep integral 12. A contagem que
vira DoD sai de ferramenta.

Os testes de fixture provam o DESENHO (isencao por secao, nao por linha); o teste
de repo prova o ESTADO. O de repo e o que nasceu vermelho.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.auto_check import (  # noqa: E402
    check_contrato_revogado,
    _PORTADORES_NORMA,
    _TERMOS_REVOGADOS,
)

TERMOS = {"PREPARAR": "contrato-fixture v9.9, Clausula X"}


def _doc(tmp_path, nome, texto):
    (tmp_path / nome).write_text(texto, encoding="utf-8")
    return check_contrato_revogado(root=tmp_path, portadores=(nome,), termos=TERMOS)


# --- P1: prescricao ativa x narrativa de lapide -----------------------------

def test_linha_ativa_com_termo_revogado_e_achado(tmp_path):
    a = _doc(tmp_path, "c.md", "# C\n\n## Clausula 2\n\nO agente oferece o PREPARAR.\n")
    assert [(x[1], x[2]) for x in a] == [(5, "prescricao")]


def test_secao_de_lapide_isenta_o_bloco_inteiro(tmp_path):
    """A isencao e por SECAO. Sem ela o gate acusa a narrativa da propria
    revogacao -- nasce com falso-positivo e e desligado na 2a sessao."""
    a = _doc(tmp_path, "c.md",
             "# C\n\n### Lapide -- o sub-modo PREPARAR\n\n"
             "O PREPARAR era o re-ensino antes do drill.\n"
             "Morreu na s170: nao era lido.\n")
    assert a == []


def test_heading_irmao_fecha_a_secao_de_lapide(tmp_path):
    """Perigo real da isencao por secao: vazar para o resto do documento."""
    a = _doc(tmp_path, "c.md",
             "# C\n\n### Lapide -- PREPARAR\n\nO PREPARAR morreu.\n\n"
             "### Clausula viva\n\nO agente oferece o PREPARAR.\n")
    assert [x[1] for x in a] == [9]


def test_heading_que_nomeia_o_termo_morto_e_achado(tmp_path):
    """`## Clausula 4 -- Fusao em sub-modos (PREPARAR / DRENAR)` escapou da 1a
    versao deste gate: o titulo e o que o leitor usa para decidir se a secao
    ainda vale."""
    a = _doc(tmp_path, "c.md", "# C\n\n## Clausula 4 -- sub-modos (PREPARAR / DRENAR)\n")
    assert [(x[1], x[2]) for x in a] == [(3, "prescricao")]


def test_linha_que_marca_o_termo_como_antigo_e_isenta(tmp_path):
    """Narrativa que qualifica o termo como morto e registro correto."""
    a = _doc(tmp_path, "c.md",
             "# C\n\nA Revisao Direcionada absorveu o antigo PREPARAR.\n")
    assert a == []


# --- P2: frontmatter x cabecalho do corpo ----------------------------------

def test_versao_divergente_entre_frontmatter_e_corpo(tmp_path):
    a = _doc(tmp_path, "c.md",
             "---\ntype: contract\nversion: 1.0\n---\n\n# C\n**Versao 1.3 | 2026-09-08**\n")
    assert [(x[1], x[2]) for x in a] == [(0, "versao")]


def test_versao_coerente_nao_e_achado(tmp_path):
    a = _doc(tmp_path, "c.md",
             "---\ntype: contract\nversion: 1.3\n---\n\n# C\n**Versao 1.3 | 2026-09-08**\n")
    assert a == []


def test_cabecalho_de_versao_nao_conta_como_prescricao(tmp_path):
    """A linha que ANUNCIA a revogacao cita o termo por obrigacao."""
    a = _doc(tmp_path, "c.md",
             "---\ntype: contract\nversion: 1.3\n---\n\n# C\n"
             "**Versao 1.3 | 2026-09-08 (o PREPARAR e REVOGADO)**\n")
    assert a == []


# --- registro e estado do repo ---------------------------------------------

def test_portadores_declarados_existem_no_disco():
    """Gate que aponta para arquivo inexistente vigia o nada (F82, variante 1)."""
    faltando = [p for p in _PORTADORES_NORMA if not (ROOT / p).is_file()]
    assert faltando == [], f"portadores declarados e ausentes: {faltando}"


def test_registro_de_termos_nao_esta_vazio():
    assert _TERMOS_REVOGADOS, "registro vazio = gate que nunca dispara"


@pytest.mark.parametrize("tipo", ["prescricao", "versao"])
def test_repo_sem_clausula_revogada_em_vigor(tipo):
    """🔴 O TESTE QUE NASCEU VERMELHO.

    No HEAD `09ce3de`: 17 achados `prescricao` (12 no contrato + 5 nos
    portadores executaveis) + 1 `versao` (frontmatter 1.0 x corpo 1.3).
    """
    achados = [x for x in check_contrato_revogado() if x[2] == tipo]
    detalhe = "\n".join(f"  {f}:{ln} -- {d}" for f, ln, _, d in achados)
    assert not achados, (
        f"{len(achados)} achado(s) de '{tipo}': clausula revogada ainda em vigor.\n"
        f"{detalhe}")
