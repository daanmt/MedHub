import re
import pandas as pd
from pathlib import Path
from .file_io import read_md, get_abs_path

def get_error_stats(rel_path="caderno_erros.md") -> dict:
    """Faz o parse de métricas básicas do Caderno de Erros legível."""
    content = read_md(rel_path)
    
    # Contabiliza instâncias de Erro (qualquer subhead H4 com tipo de erro ou elo)
    total_erros = len(re.findall(r'\*\*Tipo de erro:\*\*', content, re.IGNORECASE))
    
    # Faz uma heurística simples de áreas:
    # Acha seções entre H2 (##)
    areas_blocks = re.split(r'\n##\s+', content)
    areas_count = {}
    
    if len(areas_blocks) > 1:
        for block in areas_blocks[1:]:
            lines = block.split('\n')
            area_name = lines[0].strip()
            # Ignora o sumário / indice se houver
            if "Índice" in area_name or area_name.startswith("Erros"):
                continue
            
            # Conta qtas vezes aparece a Tag de Erro no bloco da área
            erros_na_area = len(re.findall(r'\*\*Tipo de erro:\*\*', block, re.IGNORECASE))
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
        
        # Extrai data via RegEx ou fallback no nome do arquivo
        date_match = re.search(r'\*\*Data:\*\*\s*([\d-]+)', content)
        if date_match:
            date_str = date_match.group(1)
        else:
            # Tenta pegar os primeiros 10 caracteres do nome (YYYY-MM-DD)
            date_str = file.name[:10]
            
        sessions.append({
            "arquivo": file.name,
            "data": date_str,
            "preview": content[:100] + "..."
        })
        
    df = pd.DataFrame(sessions)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        # Fallback para mtime se pd.to_datetime falhou (NaT)
        import os
        from datetime import datetime
        mask = df['data'].isnull()
        if mask.any():
            for idx in df[mask].index:
                f_name = df.at[idx, 'arquivo']
                mtime = os.path.getmtime(h_path / f_name)
                df.at[idx, 'data'] = datetime.fromtimestamp(mtime)
        
        df = df.sort_values(by="data", ascending=False)
    return df
