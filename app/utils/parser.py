import re
import pandas as pd
from pathlib import Path
from .file_io import read_md, get_abs_path

def get_error_stats(rel_path="caderno_erros.md") -> dict:
    """Faz o parse de métricas básicas do Caderno de Erros legível."""
    content = read_md(rel_path)
    
    # Contabiliza instâncias de Erro (qualquer subhead H4 com tipo de erro ou elo)
    total_erros = len(re.findall(r'\\*\\*Tipo de erro:\\*\\*', content, re.IGNORECASE))
    
    # Faz uma heurística simples de áreas:
    # Acha seções entre H2 (##)
    areas_blocks = re.split(r'\\n##\\s+', content)
    areas_count = {}
    
    if len(areas_blocks) > 1:
        for block in areas_blocks[1:]:
            lines = block.split('\\n')
            area_name = lines[0].strip()
            # Ignora o sumário / indice se houver
            if "Índice" in area_name or area_name.startswith("Erros"):
                continue
            
            # Conta qtas vezes aparece a Tag de Erro no bloco da área
            erros_na_area = len(re.findall(r'\\*\\*Tipo de erro:\\*\\*', block, re.IGNORECASE))
            if erros_na_area > 0:
                areas_count[area_name] = erros_na_area
                
    return {
        "total": total_erros,
        "por_area": areas_count
    }

def parse_sessions(history_dir="history") -> pd.DataFrame:
    """Varre os logs de estudo md em history/ e constrói um DataFrame em memória"""
    h_path = get_abs_path(history_dir)
    sessions = []
    
    if not h_path.exists():
        return pd.DataFrame()
        
    for file in h_path.glob("session_*.md"):
        content = file.read_text(encoding="utf-8")
        
        if not date_match:
            # Tenta pegar a data de modificação do arquivo como fallback se o nome do arquivo falhar
            import os
            from datetime import datetime
            mtime = os.path.getmtime(file)
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
        sessions.append({
            "arquivo": file.name,
            "data": date_str,
            "preview": content[:100] + "..."
        })
        
    df = pd.DataFrame(sessions)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df = df.sort_values(by="data", ascending=False)
    return df
