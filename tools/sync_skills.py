"""sync_skills.py — gerador determinístico das skills agent-agnostic.

Fonte canônica ÚNICA: `.claude/commands/<x>.md` (onde as skills do agente
primário, Claude Code, vivem e evoluem). Os espelhos
`.agents/skills/source-command-<x>/SKILL.md` são BUILD ARTIFACTS — commitados
para o Codex consumir, mas NUNCA editados à mão. Este script é a única
autoridade sobre o frontmatter e o wrapper do espelho.

Espelha a disciplina do AGENTE.md §7.2 ("cada CLI tem assinatura canônica em
UMA skill; workflows referenciam, não copiam") para o par command↔skill.

Uso:
    python tools/sync_skills.py            # regenera todos os espelhos
    python tools/sync_skills.py --check    # não escreve; exit 1 se algum fora de sync
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = ROOT / ".claude" / "commands"
SKILLS_DIR = ROOT / ".agents" / "skills"


def _split_frontmatter(text):
    """(frontmatter, body) a partir de '---\\n...\\n---\\n<body>'. body pós-frontmatter."""
    m = re.match(r"^﻿?---[ \t]*\n(.*?)\n---[ \t]*\n?(.*)$", text, re.S)
    if not m:
        return "", text
    return m.group(1), m.group(2)


def _description_line(frontmatter):
    """Valor cru (com aspas) da chave description do command — reusado verbatim."""
    m = re.search(r"^description:[ \t]*(.+?)[ \t]*$", frontmatter, re.M)
    return m.group(1) if m else '""'


def _norm_body(body):
    """Normaliza o corpo: sem linhas em branco nas pontas + um \\n final."""
    return body.strip("\n") + "\n"


def _render_skill(slug, description_line, body):
    """Monta o SKILL.md: frontmatter agent-skill + wrapper + corpo verbatim."""
    return (
        "---\n"
        f'name: "source-command-{slug}"\n'
        f"description: {description_line}\n"
        "---\n\n"
        f"# source-command-{slug}\n\n"
        f"Use this skill when the user asks to run the migrated source command `{slug}`.\n\n"
        "## Command Template\n\n"
        f"{body}"
    )


def _mirror_body(text):
    """Corpo do espelho: tudo após '## Command Template' + linha em branco. None se ausente."""
    m = re.search(r"^## Command Template[ \t]*\n\n(.*)$", text, re.S | re.M)
    return m.group(1) if m else None


def _commands():
    """slugs canônicos = basename dos .claude/commands/*.md."""
    return sorted(p.stem for p in COMMANDS_DIR.glob("*.md"))


def _expected(slug):
    """(caminho_do_espelho, conteudo_esperado, corpo_normalizado) para um slug."""
    cmd_path = COMMANDS_DIR / f"{slug}.md"
    fm, body = _split_frontmatter(cmd_path.read_text(encoding="utf-8"))
    body = _norm_body(body)
    content = _render_skill(slug, _description_line(fm), body)
    skill_path = SKILLS_DIR / f"source-command-{slug}" / "SKILL.md"
    return skill_path, content, body


def check():
    """Retorna lista de slugs fora de sync (corpo divergente ou espelho ausente)."""
    drift = []
    for slug in _commands():
        skill_path, _content, body = _expected(slug)
        if not skill_path.exists():
            drift.append(slug)
            continue
        atual = _mirror_body(skill_path.read_text(encoding="utf-8"))
        # Compara só o CORPO (frontmatter/wrapper diferem por construção).
        if atual is None or atual.strip() != body.strip():
            drift.append(slug)
    return drift


def generate():
    """(Re)escreve todos os espelhos. Retorna nº de arquivos alterados."""
    changed = 0
    for slug in _commands():
        skill_path, content, _body = _expected(slug)
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        antigo = skill_path.read_text(encoding="utf-8") if skill_path.exists() else None
        if antigo != content:
            skill_path.write_text(content, encoding="utf-8", newline="\n")
            changed += 1
            print(f"  ~ source-command-{slug}/SKILL.md")
    return changed


def main():
    if "--check" in sys.argv[1:]:
        drift = check()
        if drift:
            for slug in drift:
                print(f"PARITY_DRIFT: {slug} "
                      f"(edite .claude/commands/{slug}.md e rode `python tools/sync_skills.py`)")
            return 1
        print("Paridade command<->skill: OK (todos os espelhos em sync).")
        return 0

    n = generate()
    print(f"sync_skills: {n} espelho(s) atualizado(s) de {len(_commands())} command(s)."
          if n else f"sync_skills: já em sync ({len(_commands())} command(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
