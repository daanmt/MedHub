"""test_linter_escopo_staged.py -- F116 (s187): o linter de resumos no modo --staged
auditava o CORPUS INTEIRO enquanto se rotulava "(N arquivos)".

O defeito, medido em 18/09/2026 no proprio commit do F104:

    ✅ PASSED - Linter de Qualidade de Resumos (1 arquivos)  ⚠️ 35 WARN

Eu havia acabado de reescrever UM resumo, e o linter rodado direto sobre ele dava
`WARN_TOTAL=0`. Os 35 eram o passivo GLOBAL dos 136 resumos -- `audit_resumos.py`
sem argumento nenhum devolve exatamente 35. A causa estava em uma linha:

    cmd = [sys.executable, "tools/audit_resumos.py"]
    if mode == "--changed" and resumos_to_check:     # <- `--staged` de fora
        cmd.extend(resumos_to_check)

`resumos_to_check` e preenchido nos DOIS modos, mas a lista de arquivos so era
anexada no `--changed`. No `--staged` -- que e **o modo do git pre-commit hook**,
o gate que de fato guarda os commits -- o CLI rodava sem argumento e auditava tudo.

🔴 **Duas consequencias, e a segunda e a grave:**
  1. **O rotulo mente.** "(1 arquivos) 35 WARN" leva quem le a atribuir 35 defeitos
     ao arquivo recem-escrito. Eu quase registrei isso no ledger como propriedade
     do `TCE.md`.
  2. **O escopo do GATE e outro.** Um BLOCK preexistente em resumo alheio derrubaria
     um commit que nao o toca, apontando para o arquivo errado. Nao mordeu ate hoje
     porque o `BLOCK_TOTAL` global esta em 0 -- sorte, nao desenho.

🔴 **E contradiz o contrato escrito.** `AGENTE.md §6` diz, verbatim: *"o git
pre-commit hook roda `--staged` (**audita so o que sera selado**)"*. O codigo dizia
outra coisa havia tempo, e nenhum gate comparava os dois.

Classe: **escopo MAIOR que o declarado** -- a imagem espelhada do F115 (escopo menor
que o necessario). A familia toda da janela s187 e a mesma pergunta: *o sensor
alcanca exatamente o que ele diz que alcanca?*
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import auto_check as ac                                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_staged_passa_a_lista_de_arquivos():
    """O caso do defeito: modo do pre-commit hook tem que auditar SO o staged."""
    cmd = ac.cmd_linter_resumos("--staged", ["resumos/A.md", "resumos/B.md"])
    assert "resumos/A.md" in cmd and "resumos/B.md" in cmd, \
        "--staged sem a lista faz o CLI auditar o corpus inteiro (F116)"


def test_changed_continua_passando_a_lista():
    cmd = ac.cmd_linter_resumos("--changed", ["resumos/A.md"])
    assert "resumos/A.md" in cmd


def test_all_audita_tudo_e_NAO_passa_lista():
    """`--all` e o modo global por desenho -- auditar tudo ali esta certo."""
    cmd = ac.cmd_linter_resumos("--all", ["resumos/A.md"])
    assert "resumos/A.md" not in cmd
    assert cmd[-1].endswith("audit_resumos.py")


def test_lista_vazia_nunca_vira_varredura_global_silenciosa():
    """Guarda contra a regressao equivalente: se a lista chega vazia num modo
    incremental, o CLI rodaria sem argumento e auditaria tudo -- exatamente o
    F116 por outro caminho. O chamador so invoca o linter quando ha arquivo,
    e este teste fixa o contrato da funcao pura."""
    for mode in ("--changed", "--staged"):
        assert ac.cmd_linter_resumos(mode, []) is None, \
            f"{mode} com lista vazia tem que devolver None (nao rodar), nunca varrer tudo"


def test_o_rotulo_diz_o_ESCOPO_REAL():
    """O rotulo e a metade que enganou: '(1 arquivos)' sobre uma varredura de 136.
    Modo incremental nomeia a contagem; modo global se declara Global."""
    assert ac.label_linter_resumos("--staged", ["a.md"]) == \
        "Linter de Qualidade de Resumos (1 arquivos)"
    assert ac.label_linter_resumos("--changed", ["a.md", "b.md"]) == \
        "Linter de Qualidade de Resumos (2 arquivos)"
    assert "Global" in ac.label_linter_resumos("--all", [])


def test_o_contrato_escrito_continua_valendo():
    """`AGENTE.md §6` promete 'audita so o que sera selado'. Se a promessa for
    reescrita, este teste cai e obriga a decidir de novo -- em vez de a prosa e o
    codigo divergirem em silencio por meses, que foi o que aconteceu."""
    txt = open(os.path.join(ROOT, "AGENTE.md"), encoding="utf-8").read()
    assert "audita só o que será selado" in txt, \
        "o contrato do harness staged-only sumiu do AGENTE.md §6"
