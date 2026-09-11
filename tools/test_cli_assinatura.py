"""D5 (s177, item 1.7): toda flag de CLI tem assinatura canonica em UMA skill.

A regra e a terceira do contrato Skills x Workflows x CLIs (`AGENTE.md secao 7.2`) e
existia so em prosa desde que foi escrita. Prosa nao acusa: medido em 11/09/2026, antes
do sensor, **65 das 168 flags (39%) nao apareciam em skill nenhuma** e **17 CLIs nao eram
citados por skill alguma** -- entre eles `recurate_cards` (que reescreve o baralho
in-place) e `normalize_taxonomia` (declaradamente destrutivo). Um agente que precisasse
deles teria de ler o fonte, que e exatamente o que a secao 7.2 existe para evitar.

O check nasce **BLOCK**, e a politica warning-first concorda: *"regra nova nasce WARN e
vira BLOCK quando a base zerar"* -- e a base zerou no mesmo commit que criou o sensor
(`engenharia-cli.md` + as assinaturas nas skills donas). Mesma mecanica do F79b na s176:
promocao por MEDICAO, nunca por vontade.

O teste de repo no fim e o RATCHET: ele nao prova que o passado estava certo, prova que
a partir daqui flag nova sem doc para o commit.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import cli_signature_check as sig  # noqa: E402


def _repo(tmp_path, arquivos):
    """Repo sintetico: {'tools/x.py': '...', '.claude/commands/y.md': '...'}."""
    for rel, conteudo in arquivos.items():
        alvo = tmp_path / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")
    return tmp_path


CLI_COM_DUAS = (
    "import argparse\n"
    "def main():\n"
    "    p = argparse.ArgumentParser()\n"
    "    p.add_argument('--alfa')\n"
    "    p.add_argument('--beta')\n"
)


# --- P1: extracao pela AST, nao pelo texto -----------------------------------

def test_flag_citada_em_docstring_nao_conta(tmp_path):
    """O sensor le o PROGRAMA, nao o arquivo. Achado de graca na 1a versao: a
    regex casou `add_argument("--x")` escrito dentro da propria docstring e o
    check se acusou de ter uma flag que nao existe."""
    arq = tmp_path / "z.py"
    arq.write_text('"""Doc: use add_argument("--fantasma") assim."""\n'
                   "import argparse\n"
                   "p = argparse.ArgumentParser()\n"
                   "p.add_argument('--real')\n", encoding="utf-8")
    assert sig.flags_de(arq) == ["--real"]


def test_arquivo_quebrado_cai_no_fallback_sem_explodir(tmp_path):
    arq = tmp_path / "quebrado.py"
    arq.write_text("def main(:\n    p.add_argument('--meio')\n", encoding="utf-8")
    assert sig.flags_de(arq) == ["--meio"]     # regex de fallback, declarada


# --- P2: a regra 7.2 propriamente dita ---------------------------------------

def test_flag_sem_skill_nenhuma_e_orfa(tmp_path):
    r = _repo(tmp_path, {"tools/x.py": CLI_COM_DUAS})
    a = sig.run_checks(root=r)
    assert len(a) == 1 and a[0]["alvo"] == "tools/x.py"
    assert a[0]["payload"]["orfas"] == ["--alfa", "--beta"]
    assert a[0]["payload"]["donos"] == []


def test_flag_documentada_na_skill_dona_nao_e_orfa(tmp_path):
    r = _repo(tmp_path, {
        "tools/x.py": CLI_COM_DUAS,
        ".claude/commands/s.md": "Rode `python tools/x.py --alfa V --beta W`.",
    })
    assert sig.run_checks(root=r) == []


def test_skill_que_NAO_cita_o_cli_nao_o_documenta(tmp_path):
    """A assinatura tem dono. Flag citada numa skill que nem nomeia o arquivo e
    coincidencia de vocabulario (`--json`, `--apply` estao em toda parte), nao
    assinatura canonica -- senao o check daria por documentado o que ninguem
    consegue achar partindo do CLI."""
    r = _repo(tmp_path, {
        "tools/x.py": CLI_COM_DUAS,
        ".claude/commands/outra.md": "Aqui falamos de --alfa e --beta, mas de outro CLI.",
    })
    a = sig.run_checks(root=r)
    assert len(a) == 1 and a[0]["payload"]["orfas"] == ["--alfa", "--beta"]


def test_documentacao_parcial_acusa_so_o_que_falta(tmp_path):
    r = _repo(tmp_path, {
        "tools/x.py": CLI_COM_DUAS,
        ".claude/commands/s.md": "`tools/x.py --alfa` faz alfa.",
    })
    a = sig.run_checks(root=r)
    assert a[0]["payload"]["orfas"] == ["--beta"]
    assert a[0]["payload"]["donos"] == ["s.md"]


def test_cli_sem_flag_nao_e_achado(tmp_path):
    r = _repo(tmp_path, {"tools/sem_flag.py": "print('oi')\n"})
    assert sig.run_checks(root=r) == []


def test_suite_de_teste_nao_e_cli(tmp_path):
    r = _repo(tmp_path, {"tools/test_x.py": CLI_COM_DUAS})
    assert sig.run_checks(root=r) == []


def test_isento_declarado_e_pulado(tmp_path):
    nome = next(iter(sig.ISENTOS))
    r = _repo(tmp_path, {f"tools/{nome}": CLI_COM_DUAS})
    assert sig.run_checks(root=r) == []


def test_toda_isencao_tem_motivo_escrito():
    """Isencao sem motivo vira buraco silencioso -- foi o que o F95 mediu no
    registro de portadores do gate de revogacao."""
    assert all(isinstance(v, str) and len(v) > 20 for v in sig.ISENTOS.values())


# --- P3: ratchet sobre o repo real -------------------------------------------

def test_repo_real_tem_ZERO_flag_orfa():
    """A base zerou em 11/09/2026 (era 65 orfas / 17 CLIs sem dona). Este teste e
    o que impede de voltar: flag nova exige uma linha de doc no mesmo commit."""
    achados = sig.run_checks()
    assert achados == [], (
        "flag de CLI sem assinatura em skill: "
        + "; ".join(f"{a['alvo']} -> {' '.join(a['payload']['orfas'])}" for a in achados)
        + ". Documentar na skill dona ou em .claude/commands/engenharia-cli.md "
          "e rodar `python tools/sync_skills.py`."
    )
