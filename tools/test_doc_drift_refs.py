"""Suite do modo REFS do sensor de drift (tools/doc_drift.py::scan_refs).

O modo anotacao so ve o que alguem anotou a mao, em 4 docs. O modo refs varre
as normas VIVAS (.claude/commands, .claude/agents, .agents/workflows,
core/contracts) e acusa referencia morta sem depender de anotacao nenhuma.

Cobre: ref morta plantada (o caso que motivou o modo), ref viva, server MCP
fora do .mcp.json, e as quatro regras de precisao que impedem o sensor de
virar ruido -- lapide, ref a outro repo, path com espaco, e o que ele
declaradamente nao julga (URL/glob/placeholder/absoluto).

Executavel standalone (python tools/test_doc_drift_refs.py) e coletavel pelo pytest.
"""
import json
import sys

import pytest

from tools.doc_drift import REFS_DIRS, normalizar_ref, run_checks, scan_refs


def _mk_repo(tmp_path, mcp_servers=("pubmedmcp",)):
    """Repo sintetico minimo: .mcp.json + as raizes que o sensor usa de fronteira."""
    (tmp_path / ".mcp.json").write_text(
        json.dumps({"mcpServers": {s: {"command": "uvx"} for s in mcp_servers}}),
        encoding="utf-8")
    for rel in REFS_DIRS:
        (tmp_path / rel).mkdir(parents=True, exist_ok=True)
    (tmp_path / "tools").mkdir(exist_ok=True)
    (tmp_path / "tools" / "vivo.py").write_text("# vivo\n", encoding="utf-8")
    (tmp_path / "resumos" / "Clinica Medica").mkdir(parents=True, exist_ok=True)
    (tmp_path / "resumos" / "Clinica Medica" / "TCE.md").write_text(
        "resumo\n", encoding="utf-8")
    return tmp_path


def _mk_norma(tmp_path, rel, linhas, nome="norma.md"):
    alvo = tmp_path / rel / nome
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return alvo


# --- o caso que motivou o modo: ref morta plantada ---

def test_ref_morta_plantada_e_acusada(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands",
              ["Rode `tools/fantasma.py` antes de fechar a sessao."])
    achados = scan_refs(tmp_path)
    assert len(achados) == 1
    a = achados[0]
    assert a["tipo"] == "ref"
    assert a["doc"] == ".claude/commands/norma.md"
    assert a["linha"] == 1
    assert "tools/fantasma.py" in a["msg"]


def test_ref_viva_silencia(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands", ["Rode `tools/vivo.py`."])
    assert scan_refs(tmp_path) == []


@pytest.mark.parametrize("rel", REFS_DIRS)
def test_todos_os_dirs_em_escopo_sao_varridos(tmp_path, rel):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, rel, ["ref: `tools/fantasma.py`"])
    achados = scan_refs(tmp_path)
    assert len(achados) == 1 and achados[0]["doc"].startswith(rel)


def test_doc_fora_do_escopo_e_ignorado(tmp_path):
    _mk_repo(tmp_path)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "solto.md").write_text(
        "ref: `tools/fantasma.py`\n", encoding="utf-8")
    assert scan_refs(tmp_path) == []


# --- especie mcp ---

def test_mcp_fora_do_mcp_json_e_acusado(tmp_path):
    _mk_repo(tmp_path, mcp_servers=("pubmedmcp",))
    _mk_norma(tmp_path, ".claude/agents",
              ["Use `mcp__obsidian-notes-rag__search_notes` para os resumos."])
    achados = scan_refs(tmp_path)
    assert len(achados) == 1
    assert achados[0]["tipo"] == "ref"
    assert "obsidian-notes-rag" in achados[0]["msg"]
    assert "pubmedmcp" in achados[0]["msg"]


def test_mcp_declarado_silencia(tmp_path):
    _mk_repo(tmp_path, mcp_servers=("pubmedmcp",))
    _mk_norma(tmp_path, ".claude/agents",
              ["Use `mcp__pubmedmcp__search_abstracts` com query precisa."])
    assert scan_refs(tmp_path) == []


def test_connector_da_claude_ai_e_externo_por_design(tmp_path):
    # Connectors da claude.ai vivem no harness (OAuth), nunca no .mcp.json.
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands",
              ["Ler via `mcp__claude_ai_Google_Drive__read_file_content`."])
    assert scan_refs(tmp_path) == []


def test_mcp_json_ausente_nao_quebra(tmp_path):
    _mk_repo(tmp_path)
    (tmp_path / ".mcp.json").unlink()
    _mk_norma(tmp_path, ".claude/commands",
              ["Use `mcp__pubmedmcp__search_abstracts`."])
    achados = scan_refs(tmp_path)
    assert len(achados) == 1 and "nenhum" in achados[0]["msg"]


# --- as regras de precisao (sem elas o sensor vira ruido e ninguem le) ---

def test_lapide_nao_e_mentira(tmp_path):
    # A norma AFIRMA a ausencia; doc e realidade concordam -> nao ha drift.
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands",
              ["O player `app/pages/2_estudo.py` foi removido (codigo morto)."])
    assert scan_refs(tmp_path) == []


def test_ref_a_outro_repo_nao_e_julgada(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, "core/contracts",
              ["Irmao: `agente-daktus-content/core/contracts/handoff.md`"])
    assert scan_refs(tmp_path) == []


def test_path_com_espaco_nao_e_fatiado(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".agents/workflows",
              ["Referencia: `resumos/Clinica Medica/TCE.md`"])
    assert scan_refs(tmp_path) == []


def test_comando_em_crase_tem_os_tokens_avaliados(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".agents/workflows",
              ["Rode `python tools/fantasma.py --rows-file <linhas.json>`"])
    achados = scan_refs(tmp_path)
    assert len(achados) == 1 and "tools/fantasma.py" in achados[0]["msg"]


@pytest.mark.parametrize("token", [
    "https://exemplo.com/doc.md",       # URL
    "resumos/**/*.md",                  # glob
    "history/session_NNN.md",           # placeholder
    "C:/Users/daanm/medhub/tools/x.py",  # absoluto
    "/etc/passwd.txt",                  # absoluto posix
    ".venv/lib/pacote.py",              # dependencia
    "gold/pdf_raw",                     # sem extensao: prosa, nao path
    "mcp__pubmedmcp__search_abstracts",  # sem barra
])
def test_o_que_o_sensor_declaradamente_nao_julga(token):
    assert normalizar_ref(token) is None


@pytest.mark.parametrize("token,esperado", [
    ("tools/doc_drift.py", "tools/doc_drift.py"),
    ("`tools/doc_drift.py`", "tools/doc_drift.py"),
    ("core/contracts/norma.md:64", "core/contracts/norma.md"),
    ("core/contracts/norma.md:14-15", "core/contracts/norma.md"),
    ("app/utils/db.py::sync_git", "app/utils/db.py"),
    ("docs/guia.md#secao", "docs/guia.md"),
    ("(tools/x.py),", "tools/x.py"),
])
def test_normalizacao_e_pura_e_previsivel(token, esperado):
    assert normalizar_ref(token) == esperado


def test_link_markdown_irmao_resolve_pelo_dir_do_doc(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands", ["x"], nome="irmao.md")
    _mk_norma(tmp_path, ".claude/commands",
              ["Ver [irmao](irmao.md) e [sumido](sumido.md)."])
    achados = scan_refs(tmp_path)
    assert len(achados) == 1 and "sumido.md" in achados[0]["msg"]


def test_ref_repetida_na_linha_conta_uma_vez(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands",
              ["`tools/fantasma.py` e de novo `tools/fantasma.py`"])
    assert len(scan_refs(tmp_path)) == 1


# --- integracao com run_checks (o que o auto_check consome) ---

def test_modo_refs_nao_traz_anotacao_e_vice_versa(tmp_path):
    _mk_repo(tmp_path)
    (tmp_path / "HANDOFF.md").write_text(
        "<!-- drift-check: path tools/fantasma.py exists -->\nprosa\n",
        encoding="utf-8")
    _mk_norma(tmp_path, ".claude/commands", ["ref: `tools/fantasma.py`"])
    db = tmp_path / "ipub.db"
    so_annot = run_checks(root=tmp_path, db_path=db, modo="annot")
    so_refs = run_checks(root=tmp_path, db_path=db, modo="refs")
    tudo = run_checks(root=tmp_path, db_path=db, modo="all")
    assert [a["tipo"] for a in so_annot] == ["drift"]
    assert [a["tipo"] for a in so_refs] == ["ref"]
    assert len(tudo) == len(so_annot) + len(so_refs) == 2


def test_default_de_run_checks_inclui_refs(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands", ["ref: `tools/fantasma.py`"])
    achados = run_checks(root=tmp_path, db_path=tmp_path / "ipub.db")
    assert [a["tipo"] for a in achados] == ["ref"]


def test_sensor_nunca_escreve_nem_lanca(tmp_path):
    _mk_repo(tmp_path)
    _mk_norma(tmp_path, ".claude/commands",
              ["`tools/fantasma.py`", "`resumos/nao/existe.md`", "lixo ``` solto"])
    antes = sorted(p.relative_to(tmp_path).as_posix()
                   for p in tmp_path.rglob("*") if p.is_file())
    achados = scan_refs(tmp_path)
    depois = sorted(p.relative_to(tmp_path).as_posix()
                    for p in tmp_path.rglob("*") if p.is_file())
    assert antes == depois
    assert all(a["tipo"] == "ref" for a in achados)


def test_repo_sem_os_dirs_em_escopo_silencia(tmp_path):
    (tmp_path / ".mcp.json").write_text('{"mcpServers":{}}', encoding="utf-8")
    assert scan_refs(tmp_path) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
