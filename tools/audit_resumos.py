import os
import sys
import glob
import re
from pathlib import Path

# Garante compatibilidade nativa de encoding em terminais Windows sem quebrar icones
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Configurações do Linter
TEMAS_DIR = Path(__file__).parent.parent / "resumos"
REQUIRED_SECTIONS = [r"(#+)\s*(\d+\.\s*)?Armadilhas de Prova"]
ANTI_PATTERNS = [
    (r"\|.*\|.*\|", "Tabela ASCII detectada (Proibido pelo estilo-resumo.md)")
]
REQUIRED_MARKERS = ["⚠️", "🔴", "⭐"] # Recomenda-se ter pelo menos um

def audit_summaries(file_list=None):
    if file_list is None and len(sys.argv) > 1:
        # Se passados pela CLI
        file_list = [f for f in sys.argv[1:] if f.endswith('.md') and os.path.exists(f)]
        if not file_list and len(sys.argv) > 1:
            print("Nenhum arquivo .md válido foi encontrado nos argumentos.")
            return 0

    if file_list:
        md_files = file_list
        print(f"Iniciando auditoria pontual em {len(md_files)} arquivo(s) .md...")
    else:
        print(f"Iniciando auditoria global em: {TEMAS_DIR}")
        md_files = glob.glob(str(TEMAS_DIR / "**" / "*.md"), recursive=True)
    
    if not md_files:
        print("Nenhum arquivo .md encontrado para auditoria.")
        return 0

    erros_encontrados = 0
    arquivos_com_erro = 0

    print(f"\nAuditando {len(md_files)} resumos clínicos...\n")

    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        try:
            file_name = Path(file_path).resolve().relative_to(TEMAS_DIR.resolve())
        except ValueError:
            file_name = Path(file_path)
            
        issues = []

        # 1. Checar se tem Armadilhas de Prova
        has_armadilhas = False
        for section in REQUIRED_SECTIONS:
            if re.search(section, content, re.IGNORECASE):
                has_armadilhas = True
                break
                
        if not has_armadilhas:
            issues.append("[FALTA ESTRUTURA] Seção 'Armadilhas de Prova' ausente.")

        # 2. Checar Anti-patterns (Ex: Tabelas)
        for pattern, msg in ANTI_PATTERNS:
            if re.search(pattern, content):
                issues.append(f"[ANTI-PATTERN] {msg}")

        # 3. Checar marcadores (Warning apenas)
        has_markers = any(marker in content for marker in REQUIRED_MARKERS)
        if not has_markers:
            issues.append("[AVISO STYLE] Nenhum marcador visual (⚠️, 🔴, ⭐) encontrado. O resumo pode estar muito passivo.")

        # Reportar se houver issues
        if issues:
            arquivos_com_erro += 1
            print(f"❌ {file_name}")
            for issue in issues:
                print(f"   ↳ {issue}")
                if not issue.startswith("[AVISO"):
                    erros_encontrados += 1

    print("\n" + "="*40)
    if erros_encontrados == 0 and arquivos_com_erro == 0:
        print("✅ AUDITORIA PERFEITA! Todos os resumos seguem o padrão MedHub.")
    else:
        print(f"⚠️  RESULTADO: {erros_encontrados} erro(s) crítico(s) em {arquivos_com_erro} arquivo(s).")
    print("="*40)
    
    return 1 if erros_encontrados > 0 else 0

if __name__ == "__main__":
    exit_code = audit_summaries()
    sys.exit(exit_code)
