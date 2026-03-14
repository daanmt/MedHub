import pandas as pd
import sqlite3
import os

# Caminhos
DB_PATH = 'ipub.db'
EXCEL_PATH = 'Tools/Dashboard EMED 2026.xlsx'

def import_performance():
    if not os.path.exists(EXCEL_PATH):
        print(f"Erro: Arquivo {EXCEL_PATH} não encontrado.")
        return

    # Limpa contadores antes de importar para evitar acúmulo
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("Resetando contadores no Banco de Dados...")
    cursor.execute("UPDATE taxonomia_cronograma SET questoes_realizadas = 0, questoes_acertadas = 0, percentual_acertos = 0")
    conn.commit()

    # Mapeamento de abas para as áreas do banco
    mapping = {
        'Pediatria': 'Pediatria',
        'Preventiva': 'Medicina Preventiva e Saúde Pública',
        'Cirurgia': 'Cirurgia',
        'Obstetrícia': 'Ginecologia e Obstetrícia',
        'Ginecologia': 'Ginecologia e Obstetrícia',
        'Infectologia': 'Clínica Médica',
        'Gastro': 'Clínica Médica',
        'Endocrino': 'Clínica Médica',
        'Cardiologia': 'Clínica Médica',
        'Psiquiatria': 'Clínica Médica',
        'Neurologia': 'Clínica Médica',
        'Nefrologia': 'Clínica Médica',
        'Hematologia': 'Clínica Médica',
        'Pneumo': 'Clínica Médica',
        'Dermato': 'Clínica Médica',
        'Reumato': 'Clínica Médica',
        'Hepato': 'Clínica Médica',
        'Otorrino': 'Clínica Médica',
        'Ortopedia': 'Clínica Médica',
        'Oftalmo': 'Clínica Médica'
        # 'Quadro Geral' removido para evitar double-count
    }

    results = {} # area: {'acertos': 0, 'total': 0}

    print("Lendo abas do Excel...")
    xl = pd.ExcelFile(EXCEL_PATH)
    
    for sheet in xl.sheet_names:
        if sheet not in mapping:
            continue
            
        area = mapping[sheet]
        if area not in results:
            results[area] = {'acertos': 0, 'total': 0}
            
        print(f"  Processando {sheet} -> {area}...")
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=None)
            
            # Encontra a linha onde a coluna B (Index 1) é "Total"
            total_row = df[df[1] == 'Total']
            
            if not total_row.empty:
                row_data = total_row.iloc[0]
                
                # Para a linha "Total": 
                # Index 5 (Col F) = Total Realizadas
                # Index 6 (Col G) = Acertos
                val_total = row_data[5]
                val_acertos = row_data[6]
                
                t = float(val_total) if isinstance(val_total, (int, float)) and not pd.isna(val_total) else 0
                a = float(val_acertos) if isinstance(val_acertos, (int, float)) and not pd.isna(val_acertos) else 0
                
                if t > 0:
                    results[area]['total'] += t
                    results[area]['acertos'] += a
                    print(f"    Extraído: {a} acertos de {t} totais.")
                else:
                    print(f"    Aviso: Aba {sheet} tem 'Total' zerado ou inválido.")
            else:
                print(f"    Aviso: Linha 'Total' não encontrada na aba {sheet}.")
                
        except Exception as e:
            print(f"Erro ao processar aba {sheet}: {e}")

    print("\nAtualizando Banco de Dados...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Reset inicial
    cursor.execute("UPDATE taxonomia_cronograma SET questoes_realizadas = 0, questoes_acertadas = 0, percentual_acertos = 0")
    
    total_db_realizadas = 0
    total_db_acertos = 0

    for area, data in results.items():
        v_total = int(data['total'])
        v_acertos = int(data['acertos'])
        if v_total == 0: continue
        
        total_db_realizadas += v_total
        total_db_acertos += v_acertos
        
        print(f"  Final {area}: {v_acertos} / {v_total}")
        
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE area = ? LIMIT 1", (area,))
        row = cursor.fetchone()
        
        percent = (v_acertos / v_total * 100)
        if row:
            cursor.execute('''
                UPDATE taxonomia_cronograma 
                SET questoes_realizadas = ?, 
                    questoes_acertadas = ?, 
                    percentual_acertos = ?,
                    ultima_revisao = ?
                WHERE id = ?
            ''', (v_total, v_acertos, percent, '2026-03-14', row[0]))
        else:
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, 'Geral', ?, ?, ?, ?)
            ''', (area, v_total, v_acertos, percent, '2026-03-14'))

    conn.commit()
    conn.close()
    print(f"\nSucesso Global! Total: {total_db_acertos} / {total_db_realizadas}")

if __name__ == "__main__":
    import_performance()

if __name__ == "__main__":
    import_performance()
