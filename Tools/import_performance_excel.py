import pandas as pd
import sqlite3
import os
from datetime import date

# Caminhos relativos à raiz do projeto
DB_PATH = 'ipub.db'
EXCEL_PATH = 'Tools/Dashboard EMED 2026.xlsx'

# Mapeamento de abas para as áreas canônicas do banco
SHEET_AREA_MAP = {
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
    'Oftalmo': 'Clínica Médica',
}


def import_performance():
    """
    Importa dados de desempenho do Excel EMED para o ipub.db.
    Estratégia: DELETE + INSERT por área (garante dados limpos sem double-count).
    Retorna (sucesso: bool, mensagem: str).
    """
    if not os.path.exists(EXCEL_PATH):
        msg = f"Arquivo não encontrado: {EXCEL_PATH}"
        print(msg)
        return False, msg

    results = {}  # area -> {'acertos': int, 'total': int}

    print("Lendo abas do Excel...")
    xl = pd.ExcelFile(EXCEL_PATH)

    for sheet in xl.sheet_names:
        if sheet not in SHEET_AREA_MAP:
            continue

        area = SHEET_AREA_MAP[sheet]
        if area not in results:
            results[area] = {'acertos': 0.0, 'total': 0.0}

        print(f"  Processando {sheet} -> {area}...")
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet, header=None)

            # Linha onde coluna B (index 1) == 'Total'
            total_row = df[df[1] == 'Total']
            if total_row.empty:
                print(f"    Aviso: linha 'Total' não encontrada em '{sheet}'.")
                continue

            row_data = total_row.iloc[0]
            # Col F (index 5) = Total Realizadas; Col G (index 6) = Acertos
            t = float(row_data[5]) if isinstance(row_data[5], (int, float)) and not pd.isna(row_data[5]) else 0.0
            a = float(row_data[6]) if isinstance(row_data[6], (int, float)) and not pd.isna(row_data[6]) else 0.0

            if t > 0:
                results[area]['total'] += t
                results[area]['acertos'] += a
                print(f"    {a:.0f} acertos / {t:.0f} realizadas")
            else:
                print(f"    Aviso: Total zerado ou inválido em '{sheet}'.")

        except Exception as e:
            print(f"    Erro ao processar '{sheet}': {e}")

    if not results:
        msg = "Nenhum dado extraído do Excel."
        print(msg)
        return False, msg

    print("\nAtualizando banco de dados (DELETE + INSERT por área)...")
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    total_realizadas = 0
    total_acertos = 0

    for area, data in results.items():
        v_total = int(data['total'])
        v_acertos = int(data['acertos'])
        if v_total == 0:
            continue

        total_realizadas += v_total
        total_acertos += v_acertos
        percent = v_acertos / v_total * 100

        print(f"  {area}: {v_acertos} / {v_total} ({percent:.1f}%)")

        # DELETE todas as linhas dessa área (evita stale sub-area rows)
        cursor.execute("DELETE FROM taxonomia_cronograma WHERE area = ?", (area,))
        # INSERT uma única linha agregada por área
        cursor.execute(
            "INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao) "
            "VALUES (?, 'Geral', ?, ?, ?, ?)",
            (area, v_total, v_acertos, percent, today)
        )

    conn.commit()
    conn.close()

    msg = f"Importação concluída: {total_acertos} acertos / {total_realizadas} questões ({total_acertos/total_realizadas*100:.1f}%)"
    print(f"\n{msg}")
    return True, msg


if __name__ == "__main__":
    import_performance()
