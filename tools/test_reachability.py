"""test_reachability.py — suite do check de alcancabilidade v0 (part-6).

Testa contra um REPO SINTETICO em tmp (mesma tecnica do test_doc_drift_refs):
plantar um orfao conhecido e um alcancado conhecido e exigir que o sensor
separe os dois. Testar contra o repo real seria um teste que muda de veredito
toda vez que alguem adiciona um arquivo.

Pytest-nativo + standalone.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reachability_check as RC  # noqa: E402


def _repo(base):
    """Monta um repo sintetico. Devolve o Path da raiz."""
    r = Path(base)
    (r / "tools").mkdir(parents=True)
    (r / "tools" / "__pycache__").mkdir()
    (r / "tools" / "_archive").mkdir()
    (r / "app" / "utils").mkdir(parents=True)
    (r / ".agents" / "workflows").mkdir(parents=True)
    (r / "core" / "contracts").mkdir(parents=True)

    # alcancado por outro .py (import)
    (r / "tools" / "lib_viva.py").write_text('"""lib_viva.py — biblioteca."""\n',
                                             encoding="utf-8")
    (r / "tools" / "consumidor.py").write_text(
        '"""consumidor.py — usa a lib."""\nimport lib_viva\n', encoding="utf-8")
    # alcancado por doc (.agents) — no MedHub a mencao E a chamada
    (r / "tools" / "cli_doc.py").write_text('"""cli_doc.py — CLI do workflow."""\n',
                                            encoding="utf-8")
    # o mesmo doc alcanca os dois consumidores, para que o unico orfao do
    # fixture seja o plantado de proposito
    (r / ".agents" / "workflows" / "w.md").write_text(
        "Rodar `python tools/cli_doc.py --dry-run`, depois `tools/consumidor.py` "
        "e `tools/usa_app.py`.\n", encoding="utf-8")
    # alcancado por pytest.ini
    (r / "tools" / "test_algo.py").write_text('"""test_algo.py — suite."""\n',
                                              encoding="utf-8")
    (r / "pytest.ini").write_text("[pytest]\npython_files = test_algo.py\n",
                                  encoding="utf-8")
    # alcancado por contrato
    (r / "tools" / "cli_contrato.py").write_text('"""cli_contrato.py — CLI."""\n',
                                                 encoding="utf-8")
    (r / "core" / "contracts" / "c.md").write_text(
        "A escrita passa por `tools/cli_contrato.py`.\n", encoding="utf-8")
    # alcancado por caminho dotted (app)
    (r / "app" / "utils" / "db.py").write_text('"""db.py — acesso."""\n', encoding="utf-8")
    (r / "app" / "utils" / "__init__.py").write_text("", encoding="utf-8")
    (r / "app" / "__init__.py").write_text("", encoding="utf-8")
    (r / "tools" / "usa_app.py").write_text(
        '"""usa_app.py."""\nfrom app.utils.db import x\n', encoding="utf-8")
    # ORFAOS: ninguem cita
    (r / "tools" / "orfao.py").write_text('"""orfao.py — construido e nunca conectado."""\n',
                                          encoding="utf-8")
    (r / "app" / "utils" / "orfao_app.py").write_text('"""orfao_app.py."""\n',
                                                      encoding="utf-8")
    # ruido que NAO deve virar alvo nem referenciador
    (r / "tools" / "__pycache__" / "orfao.cpython-312.pyc").write_text("x", encoding="utf-8")
    (r / "tools" / "_archive" / "morto.py").write_text(
        '"""morto.py."""\nimport orfao\n', encoding="utf-8")
    return r


def _rodar(base):
    return {a["alvo"] for a in RC.run_checks(root=str(base))}


def test_separa_orfao_de_alcancado():
    with tempfile.TemporaryDirectory() as td:
        r = _repo(td)
        orfaos = _rodar(r)
        assert orfaos == {"tools/orfao.py", "app/utils/orfao_app.py"}, orfaos


def test_cada_tipo_de_referenciador_conta():
    """py-import, doc .agents, pytest.ini, contrato e caminho dotted de app."""
    with tempfile.TemporaryDirectory() as td:
        orfaos = _rodar(_repo(td))
        for vivo in ("tools/lib_viva.py", "tools/cli_doc.py", "tools/test_algo.py",
                     "tools/cli_contrato.py", "app/utils/db.py"):
            assert vivo not in orfaos, f"{vivo} tem referenciador e foi acusado de orfao"


def test_arquivo_arquivado_nao_ressuscita():
    """`tools/_archive/morto.py` importa `orfao` — mas codigo arquivado nao e
    referenciador vivo. Se contasse, o check daria alta a um defunto."""
    with tempfile.TemporaryDirectory() as td:
        assert "tools/orfao.py" in _rodar(_repo(td))


def test_init_py_isento():
    """__init__.py nunca e citado pelo nome; e alcancado pelo import do pacote."""
    with tempfile.TemporaryDirectory() as td:
        orfaos = _rodar(_repo(td))
        assert not any(o.endswith("__init__.py") for o in orfaos), orfaos


def test_autoreferencia_nao_salva():
    """Um arquivo que so cita a si mesmo (docstring com o proprio nome) segue
    orfao — auto-referencia nao e alcance."""
    with tempfile.TemporaryDirectory() as td:
        r = _repo(td)
        (r / "tools" / "narcisista.py").write_text(
            '"""narcisista.py — uso: python tools/narcisista.py"""\n', encoding="utf-8")
        assert "tools/narcisista.py" in _rodar(r)


def test_stem_solto_em_md_nao_conta():
    """Em prosa, um stem sem `.py` e ruido (a palavra `orfao` num .md nao
    significa que alguem roda `tools/orfao.py`). Em .py, `import orfao` conta."""
    with tempfile.TemporaryDirectory() as td:
        r = _repo(td)
        (r / ".agents" / "workflows" / "ruido.md").write_text(
            "Um orfao nao e problema por si so.\n", encoding="utf-8")
        assert "tools/orfao.py" in _rodar(r), "mencao solta em prosa nao e alcance"
        (r / "tools" / "importador.py").write_text(
            '"""importador.py."""\nimport orfao\n', encoding="utf-8")
        assert "tools/orfao.py" not in _rodar(r), "import em .py e alcance"


def test_tabela_markdown_sai_bem_formada():
    """DoD5: a tabela do AGENTE.md sai do proprio check (nao e digitada a mao)."""
    with tempfile.TemporaryDirectory() as td:
        md = RC.tabela_markdown(root=str(_repo(td)))
        linhas = md.splitlines()
        assert linhas[0].startswith("| CLI |") and set(linhas[1]) <= set("|-")
        assert "`tools/cli_doc.py`" in md
        assert "CLI do workflow" in md, "descricao vem da docstring do modulo"
        assert "tools/orfao.py" not in md, "orfao nao entra na tabela de vivos"
        assert "test_algo" not in md, "teste nao e CLI"


def test_warn_first_exit_zero():
    """Orfao nao bloqueia: o CLI sai 0 mesmo acusando."""
    orig = RC.ROOT_DIR
    with tempfile.TemporaryDirectory() as td:
        RC.ROOT_DIR = Path(_repo(td))
        argv = sys.argv
        sys.argv = ["reachability_check.py", "--json"]
        try:
            assert RC.main() == 0
        finally:
            sys.argv = argv
            RC.ROOT_DIR = orig


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    falhas = 0
    for fn in fns:
        try:
            fn()
            print("  OK  " + fn.__name__)
        except AssertionError as e:
            falhas += 1
            print("  XX  %s: %s" % (fn.__name__, e))
    print()
    if falhas:
        print("FALHOU: %d teste(s)" % falhas)
        sys.exit(1)
    print("TODOS OS TESTES PASSARAM (consolidacao part-6, reachability v0)")
