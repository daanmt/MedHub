import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'dashboard_umed.csv')

AREA_MAP = {
    "Pediatria": ["Imunizações", "Exantemáticas", "Icterícia", "Neonatal", "Pediátricas", "Cardiopatias Congênitas", "Asma", "Aleitamento", "Diarreia", "Pneumonias na Infância", "Choque em Pediatria", "Alergia Alimentar", "Reanimação", "Crescimento", "Constipação", "Pediatria", "Desnutrição", "Obesidade", "Bronquiolite", "Puberdade", "Kawasaki", "Distúrbios Metabólicos", "Genéticas", "Desenvolvimento", "Fibrose Cística"],
    "Cirurgia": ["Trauma", "Cirurgia", "Apendicite", "Colecistite", "Colangite", "Diverticulite", "Hérnias", "Abdome Agudo", "Tumores", "Pós-Operatórias", "Vascular", "Anestesiologia"],
    "Ginecologia e Obstetrícia": ["Benignas da Mama", "Climatério", "Colo Uterino", "Úlceras", "Planejamento Familiar", "Vulvovaginites", "Endometriose", "Câncer", "Sangramento", "Prolapsos", "Incontinência", "Violência Sexual", "Ovário", "Primeira Metade", "Sífilis na Gestação", "Hipertensivas", "Pré-Natal", "Parto", "Vitalidade", "Diabetes na Gestação", "Segunda Metade", "Partograma", "Gestação Múltipla", "Hemorragia"],
    "Medicina Preventiva e Saúde Pública": ["Processo", "Medidas de Saúde", "Vigilância", "Sistemas de Informação", "Medicina de Família", "SUS", "Atenção Primária", "Ética", "Financiamento", "Estatística", "Normas", "Saúde Coletiva", "Epidemiologia"],
    "Clínica Médica": ["Tuberculose", "HIV", "Arboviroses", "Tireotoxicose", "Pneumonias Bacterianas", "Osteoporose", "Diabetes Mellitus", "Sepse", "Meningites", "Hipotireoidismo", "Intestino", "Animais Peçonhentos", "Endocardites", "Pancreatite", "Insuficiência Cardíaca", "Glomerulares", "AVC", "Cefaleias", "Epilepsias", "Psiquiatria", "Valvopatias", "Anemias", "Leucemias", "Doença Renal", "Distúrbios", "Hepatologia", "Demências", "Reumatologia", "Dermatologia", "Lesão Renal", "Asma", "DPOC"]
}

def guess_area(tema):
    for area, keywords in AREA_MAP.items():
        for kw in keywords:
            if kw.lower() in tema.lower():
                return area
    return "Clínica Médica"

def importar_smart():
    print(f"Lendo dados de {CSV_PATH} com mapeamento Inteligente...")
    
    temas_stats = {}
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader); next(reader); next(reader)
        
        for row in reader:
            if len(row) < 8: continue
            assunto = row[2].strip()
            if not assunto or assunto == 'Assunto' or "Total" in row[1]: continue
                
            feitas_str = row[5].strip()
            acertos_str = row[6].strip()
            feitas = int(feitas_str) if feitas_str and feitas_str.isdigit() else 0
            acertos = int(acertos_str) if acertos_str and acertos_str.isdigit() else 0
            
            if assunto not in temas_stats:
                temas_stats[assunto] = {'feitas': 0, 'acertos': 0}
            temas_stats[assunto]['feitas'] += feitas
            temas_stats[assunto]['acertos'] += acertos

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for tema_cru, stats in temas_stats.items():
        if stats['feitas'] == 0: continue
            
        feitas = stats['feitas']
        acertos = stats['acertos']
        percentual = (acertos / feitas * 100) if feitas > 0 else 0.0
        
        tema_limpo = " / ".join(tema_cru.split('\n'))
        area_correta = guess_area(tema_limpo)
        
        # Procura por correspondência exata
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE tema = ?", (tema_limpo,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE taxonomia_cronograma 
                SET questoes_realizadas = ?, questoes_acertadas = ?, percentual_acertos = ?, area = ?
                WHERE id = ?
            ''', (feitas, acertos, percentual, area_correta, row[0]))
        else:
            # Insere novo já com a área calculada
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, ?, ?, ?, ?, date('now'))
            ''', (area_correta, tema_limpo, feitas, acertos, percentual))
            
    conn.commit()
    conn.close()
    print("Mapeamento inteligente concluído e banco atualizado com as áreas corretas!")

if __name__ == '__main__':
    importar_smart()
