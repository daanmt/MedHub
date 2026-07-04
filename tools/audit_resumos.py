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
REQUIRED_MARKERS = ["⚠️", "🔴", "⭐"]  # Recomenda-se ter pelo menos um

# Severidades (Parte 2 do PRD de Autogovernança):
#   BLOCK -> exit 1 (bloqueia o commit)   |   WARN -> exit 0 (só adverte)
BLOCK, WARN = "BLOCK", "WARN"

# Regras NOVAS nascem WARN (decisão warning-first do usuário; promoção a BLOCK
# só "quando a base zerar", fora desta parte).
FRONTMATTER_KEYS = ("type", "area", "especialidade", "status")  # §5.2
# Encoding não-ASCII proibido. `←`/`…` legítimos NÃO entram (preservados de propósito).
ENCODING_PROIBIDO = {
    "→": "seta unicode (use '->')",
    "—": "travessão em-dash (use '--')",
    "–": "en-dash (use '-')",
    r"$\rightarrow$": "LaTeX \\rightarrow (use '->')",
}


def _frontmatter_faltando(content):
    """Chaves §5.2 ausentes/vazias no frontmatter. WARN. [] = ok."""
    m = re.match(r"---\s*\n(.*?)\n---\s*(?:\n|$)", content.lstrip("﻿"), re.S)
    if not m:
        return ["(sem frontmatter)"]
    fm = m.group(1)
    return [k for k in FRONTMATTER_KEYS if not re.search(rf"^{k}\s*:\s*\S", fm, re.M)]


def _encoding_proibido(content):
    """Caracteres de encoding não-ASCII proibidos presentes. WARN. [] = ok."""
    return [ch for ch in ENCODING_PROIBIDO if ch in content]


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

    block_total = 0            # conta só BLOCK -> governa o exit code
    arquivos_com_block = 0
    warn_agg = {}              # tipo de WARN -> nº de arquivos afetados (agregado, não linha-a-linha)

    print(f"\nAuditando {len(md_files)} resumos clínicos...\n")

    for file_path in md_files:
        try:
            file_name = Path(file_path).resolve().relative_to(TEMAS_DIR.resolve())
        except ValueError:
            file_name = Path(file_path)

        # Encoding deixou de ser mascarado: sem errors='ignore'. Byte inválido -> BLOCK.
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            block_total += 1
            arquivos_com_block += 1
            print(f"❌ {file_name}")
            print(f"   ↳ [{BLOCK}] [ENCODING] UnicodeDecodeError: {e}")
            continue

        issues = []  # (sev, msg)

        # 1. Armadilhas de Prova presente? (BLOCK)
        has_armadilhas = any(re.search(s, content, re.IGNORECASE) for s in REQUIRED_SECTIONS)
        if not has_armadilhas:
            issues.append((BLOCK, "[FALTA ESTRUTURA] Seção 'Armadilhas de Prova' ausente."))

        # 2. Anti-patterns estruturais (ex: tabelas ASCII) (BLOCK)
        for pattern, msg in ANTI_PATTERNS:
            if re.search(pattern, content):
                issues.append((BLOCK, f"[ANTI-PATTERN] {msg}"))

        # 3. Marcadores visuais (WARN — já era não-bloqueante)
        if not any(marker in content for marker in REQUIRED_MARKERS):
            issues.append((WARN, "[STYLE] Nenhum marcador visual (⚠️, 🔴, ⭐). O resumo pode estar passivo."))

        # 4. Frontmatter §5.2 (WARN — regra nova)
        faltando = _frontmatter_faltando(content)
        if faltando:
            issues.append((WARN, f"[FRONTMATTER §5.2] campos ausentes: {', '.join(faltando)}"))

        # 5. Encoding não-ASCII proibido (WARN — regra nova)
        proibidos = _encoding_proibido(content)
        if proibidos:
            issues.append((WARN, f"[ENCODING] caractere proibido: {' '.join(proibidos)}"))

        # Reportar BLOCK por arquivo (linha-a-linha); agregar WARN por tipo.
        blocks = [m for sev, m in issues if sev == BLOCK]
        if blocks:
            arquivos_com_block += 1
            block_total += len(blocks)
            print(f"❌ {file_name}")
            for msg in blocks:
                print(f"   ↳ [{BLOCK}] {msg}")
        for sev, msg in issues:
            if sev == WARN:
                tipo = msg[msg.find("[") + 1: msg.find("]")]
                warn_agg[tipo] = warn_agg.get(tipo, 0) + 1

    warn_total = sum(warn_agg.values())

    print("\n" + "=" * 40)
    if block_total == 0 and warn_total == 0:
        print("✅ AUDITORIA PERFEITA! Todos os resumos seguem o padrão MedHub.")
    else:
        if block_total:
            print(f"🛑 BLOCK: {block_total} erro(s) crítico(s) em {arquivos_com_block} arquivo(s). (bloqueia)")
        else:
            print("✅ BLOCK: 0 erro(s) crítico(s). (não bloqueia)")
        if warn_total:
            print(f"⚠️  WARN: {warn_total} aviso(s) — não bloqueia (agregado por tipo):")
            for tipo, n in sorted(warn_agg.items()):
                print(f"      • {tipo}: {n} arquivo(s)")
    print("=" * 40)
    # Linha machine-readable para o auto_check distinguir WARN de BLOCK sem reimplementar a regra.
    print(f"[AUTO-CHECK-META] BLOCK_TOTAL={block_total} WARN_TOTAL={warn_total}")

    return 1 if block_total > 0 else 0


if __name__ == "__main__":
    exit_code = audit_summaries()
    sys.exit(exit_code)
