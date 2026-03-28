import os
import glob
import re
from pathlib import Path

# Configurações do Linter
TEMAS_DIR = Path(__file__).parent.parent / "resumos"
REQUIRED_SECTIONS = [r"(#+)\s*(\d+\.\s*)?Armadilhas de Prova"]
ANTI_PATTERNS = [
    (r"\|.*\|.*\|", "Tabela ASCII detectada (Proibido pelo estilo-resumo.md)")
]
REQUIRED_MARKERS = ["⚠️", "🔴", "⭐"] # Recomenda-se ter pelo menos um

def audit_summaries():
    print(f"Iniciando auditoria em: {TEMAS_DIR}")
    md_files = glob.glob(str(TEMAS_DIR / "**" / "*.md"), recursive=True)
    
    if not md_files:
        print("Nenhum arquivo .md encontrado.")
        return

    erros_encontrados = 0
    arquivos_com_erro = 0

    print(f"\nAuditando {len(md_files)} resumos clínicos...\n")

    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        file_name = Path(file_path).relative_to(TEMAS_DIR)
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

if __name__ == "__main__":
    audit_summaries()
