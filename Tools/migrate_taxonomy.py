"""
Migration script to align ipub.db taxonomy and counts with user spreadsheet.
Canonical Disciplines: 20 areas. Total volume: 2631 questions.
"""
import sqlite3
from datetime import datetime

DB_PATH = "ipub.db"

# 1. Target Data from Spreadsheet
TARGETS = {
    "Pediatria": {"f": 289, "p": 84.78},
    "Cirurgia": {"f": 259, "p": 76.06},
    "Ginecologia": {"f": 260, "p": 78.46},
    "Preventiva": {"f": 454, "p": 81.94},
    "Obstetrícia": {"f": 172, "p": 88.66},
    "Infecto": {"f": 177, "p": 79.66},
    "Gastro": {"f": 103, "p": 76.70},
    "Cardiologia": {"f": 66, "p": 68.18},
    "Nefrologia": {"f": 61, "p": 75.41},
    "Endocrino": {"f": 95, "p": 75.79},
    "Hepato": {"f": 14, "p": 57.14},
    "Neuro": {"f": 528, "p": 78.41},
    "Pneumo": {"f": 44, "p": 75.00},
    "Otorrino": {"f": 19, "p": 68.42},
    "Psiquiatria": {"f": 23, "p": 86.96},
    "Reumato": {"f": 21, "p": 100.00},
    "Hemato": {"f": 20, "p": 90.00},
    "Dermato": {"f": 24, "p": 66.67},
    "Ortopedia": {"f": 1, "p": 100.00},
    "Oftalmo": {"f": 1, "p": 100.00}
}

# Calculated acertos for the Geral entries
for k, v in TARGETS.items():
    TARGETS[k]["a"] = int(round(v["f"] * (v["p"] / 100.0)))

# 2. Theme to Discipline Map
THEME_MAP = {
    "Diabetes Mellitus - Complicações Agudas": "Endocrino",
    "Pancreatite Aguda e Crônica": "Gastro",
    "Hanseníase e Síndromes Verrucosas": "Dermato",
    "Hepatite B e C": "Hepato",
    "Sífilis na Gestação e Congênita": "Obstetrícia",
    "Úlceras Genitais": "Ginecologia",
    "Vigilância em Saúde": "Preventiva",
    "Sistemas de Informação em Saúde": "Preventiva",
    "Medidas de Saúde Coletiva Pt. I": "Preventiva",
    "Medidas de Saúde Coletiva Pt. II": "Preventiva",
    "Processo Saúde-Doença": "Preventiva",
    "Trauma - Avaliação Inicial, Vias Aéreas e Trauma Torácico": "Cirurgia",
    "Trauma - Choque": "Cirurgia",
    "Trauma Abdominal e Pélvico": "Cirurgia",
    "Cuidados Neonatais": "Pediatria",
    "Cardiopatias Congênitas": "Pediatria",
    "Emergências Pediátricas": "Pediatria",
    "Icterícia e Sepse Neonatal": "Pediatria",
    "Doenças Exantemáticas": "Pediatria",
    "Imunizações": "Pediatria",
    "Asma": "Pediatria"
}

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[migracao] Iniciando remodelagem de taxonomia...")

    # A. Atualizar áreas dos temas existentes
    for tema, disc in THEME_MAP.items():
        cursor.execute("UPDATE taxonomia_cronograma SET area = ? WHERE tema = ?", (disc, tema))
        if cursor.rowcount > 0:
            print(f"  - Tema '{tema}' movido para '{disc}'")

    # B. Consolidar Disciplinas (Geral)
    for disc, metrics in TARGETS.items():
        # Get sum of specific themes currently in this area
        cursor.execute("SELECT SUM(questoes_realizadas), SUM(questoes_acertadas) FROM taxonomia_cronograma WHERE area = ? AND tema != 'Geral'", (disc,))
        res = cursor.fetchone()
        current_f = res[0] or 0
        current_a = res[1] or 0
        
        needed_f = max(0, metrics["f"] - current_f)
        needed_a = max(0, metrics["a"] - current_a)
        
        # Upsert 'Geral' theme for this discipline
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE area = ? AND tema = 'Geral'", (disc,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE taxonomia_cronograma 
                SET questoes_realizadas = ?, questoes_acertadas = ?, percentual_acertos = ?, ultima_revisao = ?
                WHERE id = ?
            ''', (needed_f, needed_a, metrics["p"], datetime.now().strftime('%Y-%m-%d'), row[0]))
        else:
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, 'Geral', ?, ?, ?, ?)
            ''', (disc, needed_f, needed_a, metrics["p"], datetime.now().strftime('%Y-%m-%d')))
            
        print(f"  - Disciplina '{disc}' sincronizada: {metrics['f']} questões totais ({needed_f} em Geral)")

    # C. Limpeza de Legado (Remover áreas não canônicas que ficaram vazias)
    cursor.execute("DELETE FROM taxonomia_cronograma WHERE area NOT IN ({})".format(','.join(['?']*len(TARGETS))), list(TARGETS.keys()))
    
    conn.commit()
    
    # D. Verificação Final
    cursor.execute("SELECT SUM(questoes_realizadas) FROM taxonomia_cronograma")
    total = cursor.fetchone()[0]
    print(f"\n[migracao] Concluída. Total de questões no banco: {total}")
    
    conn.close()

if __name__ == "__main__":
    migrate()
