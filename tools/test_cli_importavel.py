"""test_cli_importavel.py -- F118 (s187): todo CLI de `tools/` roda COMO CLI.

🔴 **O defeito, e ele e meu.** A refatoracao **1.9(a)** (s186) moveu `card_checks` de
`tools/` para `app/utils/`. Dois CLIs ancoravam o `sys.path` no **proprio diretorio**:

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -> tools/
    from app.utils import card_checks                                 # precisa da RAIZ

Antes do 1.9a isso funcionava, porque `card_checks` morava em `tools/`. Depois, nao.
Medido em 18/09/2026: **`tools/insert_card_extra.py` e `tools/calibrate_card_checks.py`
morrem com `ModuleNotFoundError: No module named 'app'` ao serem invocados**. O
`insert_card_extra` e o writer canonico de card adicional sobre um `questao_id`
existente -- ou seja, um caminho de escrita do baralho ficou inalcancavel por 1 dia.

🔴 **Por que a suite inteira era CEGA a isso, e este e o ponto:** o pytest insere a raiz
do repo no `sys.path` antes de importar os modulos de teste. Entao
`test_writer_gates.py` importa `insert_card_extra` **com o path que o proprio CLI
deveria ter fornecido** e passa. O gate alcanca o MODULO; nao alcanca o PONTO DE
ENTRADA. Nenhum dos checks existentes olha para isso: o `IMPORT_DANGLING` resolve
imports estaticamente, o `D5` le assinatura de flag, o `reachability_check` conta
referenciadores.

Classe: a familia da janela s187 numa superficie nova -- *o sensor alcanca o modulo e
nao o executavel*. Irma do F116 (escopo maior que o declarado) pelo avesso: aqui o
escopo do teste e **menor que o uso real**, e a diferenca e exatamente o que o harness
fornece de graca e o usuario nao.

Nasce BLOCK: a base zerou no mesmo commit (2 -> 0), a mesma condicao do F79b e do D5.

⚠️ **LIMITE DECLARADO:** este gate prova que o CLI **carrega** (import + parser de
argumentos). Ele nao prova que o CLI FUNCIONA -- nao executa nenhum caminho real, nao
toca banco e nao valida saida. E o piso, nao o teto: um CLI pode passar aqui e falhar
na primeira invocacao de verdade.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")

# CLIs que nao expoem `--help` por desenho (script-style, sem argparse). Ficam de fora
# do teste de PARSER, mas continuam no teste de IMPORT -- a lista e explicita para que
# a isencao seja visivel, nunca inferida por heuristica.
SEM_ARGPARSE = set()


def _clis():
    for nome in sorted(os.listdir(TOOLS)):
        if not nome.endswith(".py"):
            continue
        if nome.startswith("test_") or nome == "__init__.py":
            continue
        yield nome


def _rodar(nome, args):
    return subprocess.run([sys.executable, "-X", "utf8", os.path.join(TOOLS, nome), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=ROOT, timeout=90)


def test_nenhum_cli_morre_por_import_ao_ser_invocado():
    """O caso do defeito: `python tools/insert_card_extra.py --help` ->
    ModuleNotFoundError. O CLI tem de ancorar o proprio `sys.path`, porque em uso real
    NAO ha pytest para faze-lo por ele."""
    quebrados = []
    for nome in _clis():
        r = _rodar(nome, ["--help"])
        erro = (r.stderr or "")
        if "ModuleNotFoundError" in erro or "ImportError" in erro:
            linha = next((x for x in erro.splitlines()
                          if "ModuleNotFoundError" in x or "ImportError" in x), erro[:120])
            quebrados.append(f"{nome}: {linha.strip()}")
    assert quebrados == [], (
        "CLI que nao carrega quando invocado como CLI -- o pytest fornece o sys.path "
        "que o proprio arquivo deveria fornecer, entao a suite passa e o uso real morre: "
        + "; ".join(quebrados))


def test_o_gate_pega_uma_ancora_errada_plantada(tmp_path):
    """Um gate que nunca viu um positivo nao foi testado. Reproduz o caso real: ancora
    no PROPRIO diretorio em vez da raiz, com um import que exige a raiz."""
    sub = tmp_path / "tools"
    sub.mkdir()
    (sub / "quebrado.py").write_text(
        "import os, sys\n"
        "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        "from app.utils import card_checks\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-X", "utf8", str(sub / "quebrado.py")],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(tmp_path), timeout=60)
    assert "ModuleNotFoundError" in (r.stderr or ""), \
        "o fixture tinha que reproduzir o defeito; se nao reproduz, o teste acima nao prova nada"


def test_a_lista_de_clis_nao_esta_vazia():
    """Guarda anti-vacuidade: lista vazia deixaria o teste acima verde sem olhar nada."""
    nomes = list(_clis())
    assert len(nomes) > 40, f"so {len(nomes)} CLIs encontrados -- o glob quebrou?"
    assert "insert_card_extra.py" in nomes, "o CLI do defeito original tem que estar no escopo"


def test_escopo_do_gate_esta_declarado():
    doc = sys.modules[__name__].__doc__.replace("*", "").lower()
    assert "limite declarado" in doc
    assert "nao prova que o cli funciona" in doc
