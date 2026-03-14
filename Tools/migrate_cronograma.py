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
    df_raw = pd.read_excel(EXCEL_PATH, header=1)
    
    semanas = df_raw.columns.tolist()
    # Descartamos a linha de áreas (PED, GO, etc) pois agora é irrelevante
    temas_df = df_raw.iloc[1:].fillna("")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cronograma_progresso")
    
    # Marcador para Sífilis na Gestação e Sífilis Congênita (Teoria I)
    # Segundo o usuário, tudo antes disso já foi resolvido.
    target_theme = "Sífilis na Gestação e Sífilis Congênita (Teoria I)"
    target_found = False
    
    count = 0
    # Processamos coluna por coluna (Semana por Semana)
    for col_idx, semana in enumerate(semanas):
        for row_idx in range(len(temas_df)):
            tema = str(temas_df.iloc[row_idx, col_idx]).strip()
            
            # Pula células vazias ou separadores de rotina
            if not tema or tema.upper() in ["QUESTÕES", "PROVAS", "NAN"]:
                continue
            
            # Lógica de status histórico
            # Se ainda não encontramos Sífilis, marcamos como Concluído
            # Se encontrarmos o tema alvo Exato (ou parcial aproximado), marcamos como Concluído e viramos a chave
            current_status = "Concluído" if not target_found else "Pendente"
            
            # Checagem de match (Flexibilidade para quebras de linha ou espaços)
            if "Sífilis na Gestação" in tema and "Sífilis Congênita" in tema:
                target_found = True
                current_status = "Concluído"

            cursor.execute('''
                INSERT INTO cronograma_progresso (semana, tema, status, pos_semana, pos_tema)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(semana).strip(), tema, current_status, col_idx, row_idx))
            count += 1

    conn.commit()
    conn.close()
    print(f"Sucesso! {count} temas de estudo importados. Status histórico aplicado até Sífilis.")

if __name__ == "__main__":
    migrate()
