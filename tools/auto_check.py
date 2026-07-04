import os
import sys
import subprocess
from pathlib import Path

# Garante compatibilidade nativa de encoding em terminais Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()

def _git_files(args):
    """Roda `git -c core.quotepath=false <args>` (com -z) e devolve lista de paths.

    quotepath=false + split por NUL garante que caminhos acentuados (ex.:
    'resumos/Clínica Médica/...') e com espaços cheguem inteiros, sem aspas
    literais nem escapes octais que fariam o Path().exists() falhar em silêncio.
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

    Usado pelo modo --changed (Reflexo Autônomo do agente: valida a árvore).
    """
    diff = _git_files(["diff", "--name-only", "-z", "HEAD"])
    if diff is None:
        return None
    untracked = _git_files(["ls-files", "--others", "--exclude-standard", "-z"])
    if untracked is None:
        return None
    return sorted(set(diff) | set(untracked))


def get_staged_files():
    """Apenas o que está staged para o commit (ACMR). Quotepath-safe.

    Usado pelo modo --staged (git pre-commit hook: valida só o que será selado).
    --diff-filter=ACMR exclui deleções (D) para não auditar arquivo removido.
    """
    staged = _git_files(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"])
    if staged is None:
        return None
    return sorted(set(staged))

def run_command(cmd_list, desc):
    print(f"\n[AUTO-CHECK] Executando: {desc}")
    print(f"            $ {' '.join(cmd_list)}")
    res = subprocess.run(cmd_list, cwd=ROOT_DIR)
    return res.returncode == 0

def main():
    mode = "--changed"
    if len(sys.argv) > 1 and sys.argv[1] in ("--all", "-a"):
        mode = "--all"
    elif len(sys.argv) > 1 and sys.argv[1] in ("--staged", "-s"):
        mode = "--staged"
    elif len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("Uso: python tools/auto_check.py [--changed | --staged | --all]")
        print("  --changed (padrão): Audita os arquivos modificados/novos na árvore (Reflexo Autônomo do agente).")
        print("  --staged          : Audita apenas os arquivos staged para commit (git pre-commit hook).")
        print("  --all             : Roda auditoria completa (todos os resumos e testes centrais).")
        return 0

    print("=" * 60)
    print("🤖 MEDHUB AUTONOMOUS HARNESS & PROACTIVE LINTER")
    print("=" * 60)

    resumos_to_check = []
    tools_to_check = []

    if mode in ("--changed", "--staged"):
        changed_files = get_staged_files() if mode == "--staged" else get_changed_files()
        if changed_files is None:
            mode = "--all"
        else:
            origem = "staged para commit" if mode == "--staged" else "modificado(s)/untracked na sessão"
            print(f"🔍 Detectados {len(changed_files)} arquivo(s) {origem}.")
            for f in changed_files:
                path_obj = ROOT_DIR / f
                if not path_obj.exists():
                    continue
                # Classificar
                if f.replace("\\", "/").startswith("resumos/") and f.endswith(".md"):
                    resumos_to_check.append(f)
                elif (f.replace("\\", "/").startswith("tools/") or f.replace("\\", "/").startswith("core/")) and f.endswith(".py"):
                    tools_to_check.append(f)

            if not resumos_to_check and not tools_to_check:
                print("\n✅ Nenhum arquivo crítico (resumos/*.md ou scripts python estruturais) foi alterado.")
                print("   O harness não exige execução de suítes de teste para esta mudança. Aprovado!")
                print("=" * 60)
                return 0
            
            print(f"   ↳ Resumos para auditar: {len(resumos_to_check)}")
            print(f"   ↳ Scripts estruturais para testar: {len(tools_to_check)}")

    all_passed = True
    results_summary = []

    # 1. Auditar Resumos
    if mode == "--all" or resumos_to_check:
        cmd = [sys.executable, "tools/audit_resumos.py"]
        if mode == "--changed" and resumos_to_check:
            cmd.extend(resumos_to_check)
        
        desc = "Linter de Qualidade de Resumos" + (" (Global)" if mode == "--all" else f" ({len(resumos_to_check)} arquivos)")
        success = run_command(cmd, desc)
        all_passed = all_passed and success
        results_summary.append((desc, success))

    # 2. Auditar Motor Python / Testes de Calibração
    if mode == "--all" or tools_to_check:
        cmd_test = [sys.executable, "tools/test_revisao_calibrada.py"]
        desc = "Suíte Central de Testes (Revisão Calibrada e D10)"
        success = run_command(cmd_test, desc)
        all_passed = all_passed and success
        results_summary.append((desc, success))

        # Se houver teste específico de autonomia
        test_autonomia_path = ROOT_DIR / "tools" / "test_autonomia_hooks.py"
        if test_autonomia_path.exists() and (mode == "--all" or any("autonomia" in f or "hooks" in f for f in tools_to_check)):
            cmd_auto = [sys.executable, "tools/test_autonomia_hooks.py"]
            desc_auto = "Suíte de Testes do Harness de Autonomia e Hooks"
            success_auto = run_command(cmd_auto, desc_auto)
            all_passed = all_passed and success_auto
            results_summary.append((desc_auto, success_auto))

    # Resumo Final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DO HARNESS AUTÔNOMO")
    print("=" * 60)
    for desc, success in results_summary:
        icon = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {icon} - {desc}")
    print("=" * 60)

    if all_passed:
        print("\n🎉 Todos os checks passaram! Trabalho validado autônoma e independentemente.")
        return 0
    else:
        print("\n🛑 FALHA DETECTADA! Corrija as inconsistências acima antes de considerar a entrega concluída.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
