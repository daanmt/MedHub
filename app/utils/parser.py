import re
import pandas as pd
from pathlib import Path
from .file_io import read_md, get_abs_path

def parse_caderno_erros(rel_path="caderno_erros.md") -> list[dict]:
    """Parse estruturado do caderno de erros lendo campos da Doutrina IPUB v4.0/v5.0"""
    content = read_md(rel_path)
    entries = []
    
    current_area = "Geral"
    current_tema = "Miscelânea"
    current_error = None
    
    # Mapeamento de campos amigáveis para o builder
    field_map = {
        "**Tipo de erro:**": "tipo_erro",
        "**Elo quebrado:**": "elo_quebrado",
        "**Armadilha de prova:**": "armadilha_prova",
        "**Conceito de Ouro:**": "conceito_de_ouro",
        "**Gabarito:**": "alternativa_correta",
        "**Caso:**": "enunciado"
    }
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## '):
            current_area = line.replace('## ', '').strip()
        elif line.startswith('### '):
            tema_candidate = line.replace('### ', '').strip()
            # Heurística para áreas
            if tema_candidate in ["Pediatria", "Cirurgia", "Clínica Médica", "Ginecologia e Obstetrícia", "Preventiva"]:
                current_area = tema_candidate
            else:
                current_tema = tema_candidate
        elif line.startswith('#### '):
            if current_error:
                entries.append(current_error)
                
            current_error = {
                "id": len(entries) + 1,
                "titulo": line.replace('#### ', '').strip(),
                "area": current_area,
                "tema": current_tema,
                "tipo_erro": "N/A",
                "elo_quebrado": "N/A",
                "armadilha_prova": "N/A",
                "conceito_de_ouro": "N/A",
                "alternativa_correta": "N/A",
                "enunciado": "",
                "numero": len(entries) + 1
            }
        elif current_error is not None:
            # Extração de campos via prefixo
            matched = False
            for prefix, key in field_map.items():
                if line.strip().startswith(prefix):
                    val = line.split(prefix, 1)[-1].strip()
                    current_error[key] = val
                    matched = True
                    break
            
            # Se não for campo marcado e tivermos um erro ativo, pode ser continuação do caso
            if not matched and line.strip() and not line.startswith('#'):
                # Heurística: se o enunciado já começou e não é outro campo, acumula
                if current_error['enunciado'] and len(current_error['enunciado']) < 1000:
                    current_error['enunciado'] += " " + line.strip()
                elif not any(line.startswith(p) for p in field_map.keys()):
                    # Se for a primeira linha após o título e não for campo, pode ser o início do caso
                    pass
                
    if current_error:
        entries.append(current_error)
        
    return entries
                
    if current_error:
        entries.append(current_error)
        
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
    from datetime import datetime
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
