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


#: F42 (s176): banner de ARTEFATO GERADO. O espelho e o arquivo que o agente
#: encontra PRIMEIRO -- e o que o `grep` de skill retorna e o que a listagem
#: expoe -- e nada nele dizia que editar ali e trabalho perdido. Na s159 uma
#: edicao real foi sobrescrita, o sync reportou sucesso, o `git status` ficou
#: limpo, e o ledger chegou a registrar como entregue algo que nao existia mais
#: em disco. O banner e a metade barata do conserto; a outra e o aviso de mtime.
_BANNER = (
    "<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI.\n"
    "     Edite `.claude/commands/{slug}.md` e rode `python tools/sync_skills.py`.\n"
    "     Qualquer edicao feita neste arquivo e SOBRESCRITA no proximo sync. -->\n"
)


def _render_skill(slug, description_line, body):
    """Monta o SKILL.md: frontmatter agent-skill + banner + wrapper + corpo verbatim."""
    return (
        "---\n"
        f'name: "source-command-{slug}"\n'
        f"description: {description_line}\n"
        "---\n\n"
        + _BANNER.format(slug=slug) +
        f"\n# source-command-{slug}\n\n"
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


def _edicao_perdida(slug, skill_path, antigo, body):
    """F42: o espelho tem edição à mão que este sync vai destruir?

    Critério CONJUNTO — não basta mtime (muda por `git checkout`) nem basta
    divergência (é o caso normal de "a fonte mudou"). Acusa quando o corpo do
    espelho diverge da fonte **E** o espelho é mais NOVO que o command: essa é a
    assinatura de "alguém editou aqui depois". Devolve a 1ª linha divergente —
    é o que faz o autor reconhecer o próprio texto antes de perdê-lo.
    """
    cmd_path = COMMANDS_DIR / f"{slug}.md"
    try:
        if skill_path.stat().st_mtime <= cmd_path.stat().st_mtime:
            return None
    except OSError:
        return None
    atual = _mirror_body(antigo or "")
    if atual is None or atual.strip() == body.strip():
        return None
    linhas_esp = atual.strip().splitlines()
    linhas_src = body.strip().splitlines()
    for i, linha in enumerate(linhas_esp):
        if i >= len(linhas_src) or linhas_src[i] != linha:
            return linha.strip()[:110] or "(linha em branco)"
    return "(o espelho tem linhas a mais no fim)"


def generate():
    """(Re)escreve todos os espelhos. Retorna nº de arquivos alterados."""
    changed = 0
    for slug in _commands():
        skill_path, content, body = _expected(slug)
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        antigo = skill_path.read_text(encoding="utf-8") if skill_path.exists() else None
        if antigo != content:
            # F42: avisa ANTES de sobrescrever — depois o rastro some (o disco volta ao
            # gerado e o `git status` fica limpo, indistinguível de um sync inocente).
            perdida = _edicao_perdida(slug, skill_path, antigo, body)
            if perdida:
                print(f"[WARN] ESPELHO_EDITADO_A_MAO: source-command-{slug}/SKILL.md é mais "
                      f"NOVO que .claude/commands/{slug}.md e diverge dele — a edição feita no "
                      f"espelho vai ser PERDIDA agora. 1a linha divergente: {perdida!r}. "
                      f"O canônico é `.claude/commands/{slug}.md`: leve a edição para lá e rode "
                      f"o sync de novo (F42).", file=sys.stderr)
            skill_path.write_text(content, encoding="utf-8", newline="\n")
            changed += 1
            print(f"  ~ source-command-{slug}/SKILL.md")
    return changed


def main():
    if "--check" in sys.argv[1:]:
        drift = check()
        if drift:
            for slug in drift:
                print(f"PARITY_DRIFT: {slug} -- o espelho .agents/skills/source-command-"
                      f"{slug}/SKILL.md diverge do CANONICO. O canonico e "
                      f".claude/commands/{slug}.md: edite LA -- editar o espelho e trabalho "
                      f"PERDIDO (F42) -- e rode `python tools/sync_skills.py`.")
            return 1
        print("Paridade command<->skill: OK (todos os espelhos em sync).")
        return 0

    n = generate()
    print(f"sync_skills: {n} espelho(s) atualizado(s) de {len(_commands())} command(s)."
          if n else f"sync_skills: já em sync ({len(_commands())} command(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
