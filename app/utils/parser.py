import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from .file_io import read_md, get_abs_path

_SKIP_SECTIONS = {
    'Distribuição por Tipo de Erro',
    'Distribuição por Área',
    'Taxonomia de Áreas e Temas',
}

def parse_caderno_erros(rel_path="caderno_erros.md") -> list[dict]:
    """Parse estruturado e robusto do caderno de erros (Reforma v3.0 Stateful)"""
    content = read_md(rel_path)
    entries = []

    current_area = "Geral"
    current_tema = "Miscelânea"
    _in_skip = False

    lines = content.split('\n')
    current_entry = None

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Rastreamento de Estado (Ressalva 1)
        if line.startswith('## '):
            section = line.replace('## ', '').strip()
            if section in _SKIP_SECTIONS:
                _in_skip = True
            else:
                _in_skip = False
                current_area = section
            continue

        if _in_skip:
            continue

        if line.startswith('### '):
            current_tema = line.replace('### ', '').strip()
            continue
            
        # Início de Entrada
        if line.startswith('#### '):
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "id": len(entries) + 1,
                "titulo": line.replace('#### ', '').strip(),
                "area": current_area,
                "tema": current_tema,
                "numero": len(entries) + 1,
                "raw_text": ""
            }
            continue
            
        if current_entry:
            current_entry["raw_text"] += line + "\n"
            
    if current_entry:
        entries.append(current_entry)
        
    # Extração de campos via Regex Flexível (Ressalva 2)
    for entry in entries:
        raw = entry["raw_text"]
        
        # Elo quebrado
        m_elo = re.search(r'\*\*Elo quebrado:\*\*\s*(.+)', raw)
        entry["elo_quebrado"] = m_elo.group(1).strip() if m_elo else "N/A"
        
        # Caso / Enunciado
        m_caso = re.search(r'\*\*Caso:\*\*\s*(.+?)(?=\n\*\*|\n---|\Z)', raw, re.DOTALL)
        entry["caso"] = m_caso.group(1).strip() if m_caso else "N/A"
        entry["enunciado"] = entry["caso"]
        
        # Explicação / Conceito de Ouro
        m_expl = re.search(r'\*\*Explicação correta(?:\s*\(.*?\))?:\*\*\s*(.+?)(?=\n\*\*|\n---|\Z)', raw, re.DOTALL)
        entry["explicacao_correta"] = m_expl.group(1).strip() if m_expl else "N/A"
        entry["conceito_de_ouro"] = entry["explicacao_correta"]
        
        # Armadilha / Nuance
        m_arm = re.search(r'\*\*Armadilha(?:\s*/\s*nuance)?:\*\*\s*(.+?)(?=\n\*\*|\n---|\Z)', raw, re.DOTALL)
        entry["armadilha"] = m_arm.group(1).strip() if m_arm else "N/A"
        entry["armadilha_prova"] = entry["armadilha"]
        
        # O que faltou
        m_faltou = re.search(r'\*\*O que faltou:\*\*\s*(.+?)(?=\n\*\*|\n---|\Z)', raw, re.DOTALL)
        entry["o_que_faltou"] = m_faltou.group(1).strip() if m_faltou else "N/A"
        
    return entries

def get_error_stats(rel_path="caderno_erros.md") -> dict:
    """Faz o parse de métricas básicas agregadas para o Dashboard e Analytics."""
    entries = parse_caderno_erros(rel_path)
    
    areas_count = {}
    for e in entries:
        a = e["area"]
        areas_count[a] = areas_count.get(a, 0) + 1
                
    return {
        "total": len(entries),
        "por_area": areas_count,
        "raw_entries": entries
    }

def parse_session_date(content: str, filename: str = "") -> datetime | None:
    """Extrai a data de uma sessão via múltiplas heurísticas de regex (v2.0 Fix)"""
    patterns = [
        r'\*\*Data:\*\*\s*(\d{4}-\d{2}-\d{2})',
        r'\*Data:\s*(\d{4}-\d{2}-\d{2})',
        r'Data:\s*(\d{4}-\d{2}-\d{2})',
    ]
    for pat in patterns:
        m = re.search(pat, content[:500])
        if m:
            try:
                return datetime.strptime(m.group(1), '%Y-%m-%d')
            except:
                pass
    return None

def parse_sessions(history_dir="history") -> pd.DataFrame:
    """Varre os logs de estudo md em history/ e constrói um DataFrame em memória (v2.0 Sorted)"""
    h_path = get_abs_path(history_dir)
    sessions = []
    
    if not h_path.exists():
        return pd.DataFrame()
        
    # Busca arquivos session_NNN.md
    files = list(h_path.glob("session_*.md"))
    
    # Ordenação por número extraído do nome (Plan v2.0 Fix)
    files.sort(key=lambda f: int(re.search(r'(\d+)', f.name).group(1)), reverse=True)
    
    for file in files:
        content = file.read_text(encoding="utf-8")
        
        # Extrai data via regex profundo
        date_obj = parse_session_date(content, file.name)
        date_str = date_obj.strftime('%Y-%m-%d') if date_obj else "Desconhecida"
        
        # Extrai numero da sessão
        num_match = re.search(r'session_(\d+)', file.name)
        session_id = int(num_match.group(1)) if num_match else 0
            
        sessions.append({
            "arquivo": file.name,
            "session_id": session_id,
            "data": date_str,
            "preview": content[:120].replace('\n', ' ') + "..."
        })
        
    return pd.DataFrame(sessions)

def save_new_error(area, tema, titulo, elo, caso, explicacao, armadilha):
    """Salva um novo erro diretamente no caderno_erros.md (Zero-DB Persistence)"""
    file_path = get_abs_path("caderno_erros.md")
    content = f"""
#### {titulo}

**Complexidade:** Média
**Elo quebrado:** {elo}
**Tipo de erro:** Erro de aplicação

**Caso:** {caso}

**Explicação correta:**
{explicacao}

**Armadilha / nuance:**
{armadilha}

---
"""
    # Append no final do arquivo
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)
    return True
