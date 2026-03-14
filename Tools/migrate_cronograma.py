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
    temas_df = df_raw.iloc[1:].fillna("")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cronograma_progresso")
    
    # Marcador exato para o ponto de parada (Semana 5, item Sífilis)
    stop_theme = "Sífilis na Gestação e Sífilis Congênita (Teoria I)"
    stop_reached = False
    
    count = 0
    for col_idx, semana in enumerate(semanas):
        semana_str = str(semana).strip()
        for row_idx in range(len(temas_df)):
            tema_raw = str(temas_df.iloc[row_idx, col_idx])
            tema_clean = " ".join(tema_raw.replace("\n", " ").split()).strip()
            
            if not tema_clean or tema_clean.upper() in ["QUESTÕES", "PROVAS", "NAN"]:
                continue
            
            # Status padrão baseado no marcador global
            current_status = "Pendente" if stop_reached else "Concluído"
            
            # Ponto de Parada Específico: Fim da Semana 5 (Doenças Inflamatórias do Tecido Conjuntivo I)
            # Conferimos tanto o tema quanto a semana para evitar parar na semana 1 acidentalmente
            target_semana = "09/03 a 13/03/26"
            if target_semana in semana_str and "Inflamatória" in tema_clean and "Conjuntivo I" in tema_clean:
                stop_reached = True
                current_status = "Concluído"
                print(f"Marcador final de conclusão (Semana 5) encontrado: {tema_clean}")

            cursor.execute('''
                INSERT INTO cronograma_progresso (semana, tema, status, pos_semana, pos_tema)
                VALUES (?, ?, ?, ?, ?)
            ''', (semana_str, tema_clean, current_status, col_idx, row_idx))
            count += 1

    conn.commit()
    conn.close()
    print(f"Sucesso! {count} temas importados. Foco na Semana 5 (Sífilis concluído).")

if __name__ == "__main__":
    migrate()
