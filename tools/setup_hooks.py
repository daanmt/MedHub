import os
import sys
import stat
from pathlib import Path

# Garante compatibilidade nativa de encoding em terminais Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
GIT_DIR = ROOT_DIR / ".git"
HOOKS_DIR = GIT_DIR / "hooks"
PRE_COMMIT_PATH = HOOKS_DIR / "pre-commit"

HOOK_CONTENT = """#!/bin/sh
echo ""
echo "============================================================"
echo "🛡️  MEDHUB GIT HOOK: VERIFICAÇÃO AUTÔNOMA PRÉ-COMMIT"
echo "============================================================"
python -X utf8 tools/auto_check.py --staged
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ COMMIT BLOQUEADO pelo Harness Autônomo!"
    echo "   Corrija as pendências de estilo/código apontadas acima antes de commitar."
    exit 1
fi
echo "✅ Validação autônoma pré-commit aprovada!"
exit 0
"""

def install():
    if not GIT_DIR.exists():
        print(f"❌ Erro: Diretório .git não encontrado em {ROOT_DIR}.")
        print("   O repositório Git ainda não foi inicializado nesta pasta.")
        return False

    HOOKS_DIR.mkdir(parents=True, exist_ok=True)

    if PRE_COMMIT_PATH.exists():
        backup_path = HOOKS_DIR / "pre-commit.bak"
        print(f"⚠️  Hook pré-existente encontrado. Gerando backup em: {backup_path.name}")
        PRE_COMMIT_PATH.replace(backup_path)

    with open(PRE_COMMIT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK_CONTENT)

    # Tornar executável em sistemas Linux/macOS ou terminais Git Bash
    try:
        st = os.stat(PRE_COMMIT_PATH)
        os.chmod(PRE_COMMIT_PATH, st.st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception as e:
        print(f"[WARN] Não foi possível alterar permissões UNIX ({e}). No Windows isso é normal.")

    print(f"✅ Git Hook de pre-commit instalado com sucesso em:\n   {PRE_COMMIT_PATH}")
    print("   A partir de agora, qualquer commit será blindado automaticamente pelo tools/auto_check.py!")
    return True

def uninstall():
    if not PRE_COMMIT_PATH.exists():
        print("⚠️  Hook pre-commit não está instalado.")
        return True

    PRE_COMMIT_PATH.unlink()
    backup_path = HOOKS_DIR / "pre-commit.bak"
    if backup_path.exists():
        backup_path.replace(PRE_COMMIT_PATH)
        print("✅ Hook restaurado a partir do backup pre-commit.bak.")
    else:
        print("✅ Hook pre-commit removido com sucesso.")
    return True

def main():
    action = "--install"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--uninstall", "-u"):
            action = "--uninstall"
        elif sys.argv[1] in ("--help", "-h"):
            print("Uso: python tools/setup_hooks.py [--install | --uninstall]")
            return 0

    print("=" * 60)
    print("🔧 MEDHUB GIT HOOKS SETUP ENGINE")
    print("=" * 60)

    if action == "--install":
        success = install()
    else:
        success = uninstall()

    print("=" * 60)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
