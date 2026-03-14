import pandas as pd
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')
EXCEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Cronograma de Reta Final.xlsx')

def migrate():
    if not os.path.exists(EXCEL_PATH):
        print(f"Erro: Arquivo {EXCEL_PATH} não encontrado.")
        return

    print("Lendo planilha do cronograma...")
    # Header na linha 1 (0-indexed) é onde estão as semanas
    # Header na linha 2 (0-indexed) é onde estão as áreas
    df_raw = pd.read_excel(EXCEL_PATH, header=1)
    
    # Pegamos as semanas da primeira linha (são as colunas do df carregado com header=1)
    semanas = df_raw.columns.tolist()
    
    # As áreas estão na primeira linha de dados agora
    areas = df_raw.iloc[0].tolist()
    
    # Os temas começam da linha 1 em diante
    temas_df = df_raw.iloc[1:].fillna("")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Limpar tabela antes de re-popular (ou poderíamos fazer um merge inteligente, 
    # mas para o setup inicial a limpeza é mais segura)
    cursor.execute("DELETE FROM cronograma_progresso")
    
    count = 0
    for col_idx, semana in enumerate(semanas):
        area = areas[col_idx]
        if str(area).lower() == "nan" or not area:
            continue
            
        for row_idx in range(len(temas_df)):
            tema = temas_df.iloc[row_idx, col_idx]
            if tema and str(tema).strip() and str(tema).upper() != "QUESTÕES" and str(tema).upper() != "PROVAS":
                cursor.execute('''
                    INSERT INTO cronograma_progresso (semana, area, tema, status)
                    VALUES (?, ?, ?, ?)
                ''', (str(semana).strip(), str(area).strip(), str(tema).strip(), 'Pendente'))
                count += 1

    conn.commit()
    conn.close()
    print(f"Sucesso! {count} temas de estudo importados para o ipub.db.")

if __name__ == "__main__":
    migrate()
