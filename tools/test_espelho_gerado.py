"""test_espelho_gerado.py -- F42: editar o espelho deixa de ser silencioso (s176, item 1.4).

O incidente (s159, ao vivo): uma edicao real foi feita em
`.agents/skills/source-command-analisar-questao/SKILL.md`, o `sync_skills` a **sobrescreveu**
e reportou sucesso (`~ source-command-... · 1 espelho atualizado`) -- saida **indistinguivel**
de um sync que preservou trabalho. O `git status` ficou limpo, entao a perda nao deixou rastro,
e o ledger chegou a registrar como ENTREGUE uma direcao que nao existia mais em disco.

Duas metades baratas: **banner** no artefato gerado (o espelho e o arquivo que o agente encontra
primeiro) e **aviso antes de sobrescrever** quando o espelho e mais novo que a fonte.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import sync_skills as ss   # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


# --- (a) banner: o artefato se declara gerado ---------------------------------------

def test_todo_espelho_carrega_o_banner_apontando_o_canonico():
    espelhos = sorted((ROOT / ".agents" / "skills").glob("source-command-*/SKILL.md"))
    assert espelhos, "nenhum espelho encontrado -- o teste nao esta medindo nada"
    for e in espelhos:
        slug = e.parent.name.replace("source-command-", "")
        texto = e.read_text(encoding="utf-8")
        assert "ARQUIVO GERADO" in texto and "NAO EDITE AQUI" in texto, f"{e} sem banner"
        assert f".claude/commands/{slug}.md" in texto, \
            f"{e}: o banner tem que nomear o CANONICO deste slug, nao um generico"


def test_o_banner_nao_entra_no_corpo_comparado_pela_paridade():
    """O banner e wrapper, nao conteudo: `--check` continua verde apos a mudanca."""
    assert ss.check() == [], "banner nao pode virar drift de paridade"


# --- (b) o aviso: edicao no espelho para de sumir em silencio ------------------------

def _repo_sintetico(tmp_path, corpo_cmd="# X\n\nCorpo canonico.\n"):
    cmds = tmp_path / ".claude" / "commands"
    cmds.mkdir(parents=True)
    (cmds / "alvo.md").write_text(
        '---\ndescription: "d"\n---\n\n' + corpo_cmd, encoding="utf-8")
    (tmp_path / ".agents" / "skills").mkdir(parents=True)
    return cmds


def _apontar(tmp_path):
    ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR = (
        tmp_path, tmp_path / ".claude" / "commands", tmp_path / ".agents" / "skills")


def test_espelho_editado_depois_da_fonte_e_ACUSADO_com_a_linha_perdida(tmp_path, capsys):
    orig = (ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR)
    try:
        _repo_sintetico(tmp_path)
        _apontar(tmp_path)
        ss.generate()                                   # espelho nasce em sync
        caminho, _c, body = ss._expected("alvo")
        time.sleep(0.01)
        caminho.write_text(caminho.read_text(encoding="utf-8").replace(
            "Corpo canonico.", "Corpo canonico.\nLINHA QUE O AUTOR ESCREVEU NO ESPELHO."),
            encoding="utf-8")
        os.utime(caminho, None)                          # espelho mais NOVO que a fonte
        ss.generate()
        err = capsys.readouterr().err
        assert "ESPELHO_EDITADO_A_MAO" in err, "sobrescrever edicao a mao nao pode ser silencioso"
        assert "LINHA QUE O AUTOR ESCREVEU NO ESPELHO" in err, \
            "o aviso tem que devolver a linha perdida -- e o que faz o autor reconhece-la"
        assert ".claude/commands/alvo.md" in err, "e apontar o canonico"
    finally:
        ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR = orig


def test_fonte_editada_normalmente_NAO_acusa(tmp_path, capsys):
    """O caso comum -- editar o canonico e rodar o sync -- nao pode virar ruido."""
    orig = (ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR)
    try:
        cmds = _repo_sintetico(tmp_path)
        _apontar(tmp_path)
        ss.generate()
        time.sleep(0.01)
        (cmds / "alvo.md").write_text(
            '---\ndescription: "d"\n---\n\n# X\n\nCorpo canonico EDITADO NA FONTE.\n',
            encoding="utf-8")
        capsys.readouterr()
        ss.generate()
        assert "ESPELHO_EDITADO_A_MAO" not in capsys.readouterr().err, \
            "fonte mais nova que o espelho e o fluxo NORMAL -- avisar aqui e falso-positivo"
    finally:
        ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR = orig


def test_criterio_e_CONJUNTO_mtime_sozinho_nao_acusa(tmp_path):
    """`git checkout` mexe em mtime sem mexer em conteudo -- so mtime daria ruido."""
    orig = (ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR)
    try:
        _repo_sintetico(tmp_path)
        _apontar(tmp_path)
        ss.generate()
        caminho, _c, body = ss._expected("alvo")
        os.utime(caminho, None)                          # novo, porem IDENTICO
        assert ss._edicao_perdida("alvo", caminho,
                                  caminho.read_text(encoding="utf-8"), body) is None
    finally:
        ss.ROOT, ss.COMMANDS_DIR, ss.SKILLS_DIR = orig


def test_mensagem_de_paridade_aponta_o_canonico():
    """O WARN que o `auto_check` mostra tem que dizer ONDE editar (direcao do achado)."""
    fonte = (ROOT / "tools" / "sync_skills.py").read_text(encoding="utf-8")
    assert "editar o espelho e trabalho" in fonte and "PARITY_DRIFT" in fonte


if __name__ == "__main__":
    print("Suite pytest-nativa (usa tmp_path/capsys): rode `python -m pytest "
          "tools/test_espelho_gerado.py -q`.")
