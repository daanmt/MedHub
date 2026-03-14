import re
import pandas as pd
from pathlib import Path
from .file_io import read_md, get_abs_path

def parse_caderno_erros(rel_path="caderno_erros.md") -> list[dict]:
    """Parse estruturado do caderno de erros lendo hierarquia H2/H3 e H4"""
    content = read_md(rel_path)
    entries = []
    
    current_area = "Desconhecida"
    current_tema = "Geral"
    current_error = None
    
    for line in content.split('\n'):
        if line.startswith('## '):
            current_area = line.replace('## ', '').strip()
            current_tema = "Geral"
        elif line.startswith('### '):
            tema_candidate = line.replace('### ', '').strip()
            # Heurística: se for area principal disfarçada de H3
            if tema_candidate in ["Pediatria", "Cirurgia", "Clínica Médica", "Ginecologia e Obstetrícia", "Medicina Preventiva e Saúde Pública", "Preventiva", "GO"]:
                current_area = tema_candidate
                current_tema = "Geral"
            else:
                current_tema = tema_candidate
        elif line.startswith('#### '):
            if current_error:
                entries.append(current_error)
                
            current_error = {
                "titulo": line.replace('#### ', '').strip(),
                "area": current_area,
                "tema": current_tema,
                "tipo": "Não classificado",
                "elo": "",
                "complexidade": "",
                "conteudo_bruto": line + "\n"
            }
        elif current_error is not None:
            current_error["conteudo_bruto"] += line + "\n"
            
            # Extrai os metadados principais mapeados
            if "**Tipo de erro:**" in line:
                current_error['tipo'] = line.split("**Tipo de erro:**")[-1].strip()
            elif "**Elo quebrado:**" in line:
                current_error['elo'] = line.split("**Elo quebrado:**")[-1].strip()
            elif "**Complexidade:**" in line:
                current_error['complexidade'] = line.split("**Complexidade:**")[-1].strip()
                
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

def parse_session_date(content: str, filename: str):
    """Extrai a data de uma sessão via múltiplas heurísticas de regex"""
    from datetime import datetime
    patterns = [
        r'\*\*Data:\*\*\s*(\d{4}-\d{2}-\d{2})',
        r'\*Data:\s*(\d{4}-\d{2}-\d{2})',
        r'Data:\s*(\d{4}-\d{2}-\d{2})',
    ]
    for pat in patterns:
        m = re.search(pat, content[:1000]) # Scan primeiras linhas
        if m:
            try:
                return datetime.strptime(m.group(1), '%Y-%m-%d')
            except:
                pass
                
    # Fallback: nome do arquivo
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y-%m-%d')
        except:
            pass
    return None

def parse_sessions(history_dir="history") -> pd.DataFrame:
    """Varre os logs de estudo md em history/ e constrói um DataFrame em memória"""
    h_path = get_abs_path(history_dir)
    sessions = []
    
    if not h_path.exists():
        return pd.DataFrame()
        
    for file in h_path.glob("session_*.md"):
        content = file.read_text(encoding="utf-8")
        
        # Extrai data via regex profundo
        date_obj = parse_session_date(content, file.name)
        date_str = date_obj.strftime('%Y-%m-%d') if date_obj else None
        
        # Fallback de string para a ordenacao
        if not date_str:
            date_str = file.name[:10]
            
        # Extrai numero da sessão (ex: session_023 -> 23)
        num_match = re.search(r'session_(\d+)', file.name)
        session_id = int(num_match.group(1)) if num_match else 0
            
        sessions.append({
            "arquivo": file.name,
            "session_id": session_id,
            "data": date_str,
            "preview": content[:100] + "..."
        })
        
    df = pd.DataFrame(sessions)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        # Tenta resolver NaT com data mtime local
        import os
        from datetime import datetime
        mask = df['data'].isnull()
        if mask.any():
            for idx in df[mask].index:
                try:
                    mtime = os.path.getmtime(h_path / df.at[idx, 'arquivo'])
                    df.at[idx, 'data'] = datetime.fromtimestamp(mtime)
                except:
                    pass
                    
        # Para ordenação secundária, caso datas sejam iguais, usamos id
        df = df.sort_values(by=["data", "session_id"], ascending=[False, False])
    return df
