import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def _git_files(args):
    """Roda `git -c core.quotepath=false <args>` (com -z) e devolve lista de paths.

    quotepath=false + split por NUL garante que caminhos acentuados (ex.:
    'resumos/Clinica Medica/...') e com espacos cheguem inteiros, sem aspas
    literais nem escapes octais que fariam o Path().exists() falhar em silencio.
    """
    cmd = ["git", "-c", "core.quotepath=false"] + args
    try:
        res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True,
                             encoding="utf-8", check=False)
    except Exception as e:
        print(f"[WARN] Falha ao consultar o git ({e}).")
        return None
    if res.returncode != 0:
        return None
    return [p for p in res.stdout.split("\0") if p.strip()]


def get_changed_files():
    """Modificados (working tree vs HEAD) + untracked. Quotepath-safe.

    Usado pelo modo --changed (Reflexo Autonomo do agente: valida a arvore).
    """
    diff = _git_files(["diff", "--name-only", "-z", "HEAD"])
    if diff is None:
        return None
    untracked = _git_files(["ls-files", "--others", "--exclude-standard", "-z"])
    if untracked is None:
        return None
    return sorted(set(diff) | set(untracked))


def get_staged_files():
    """Apenas o que esta staged para o commit (ACMR). Quotepath-safe.

    Usado pelo modo --staged (git pre-commit hook: valida so o que sera selado).
    --diff-filter=ACMR exclui delecoes (D) para nao auditar arquivo removido.
    """
    staged = _git_files(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"])
    if staged is None:
        return None
    return sorted(set(staged))
