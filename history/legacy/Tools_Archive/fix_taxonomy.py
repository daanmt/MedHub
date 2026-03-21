import sqlite3

def fix_taxonomy():
    conn = sqlite3.connect('ipub.db')
    cursor = conn.cursor()

    print("Corrigindo Taxonomia...")

    # 1. Pediatria (Estava sob 'Geral')
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Pediatria' WHERE tema = 'Pediatria' OR tema LIKE '%Pediatria%'")
    
    # 2. Clínica Médica (Consolidando temas dispersos)
    temas_clinica = ['Cardiologia', 'Endocrinologia', 'Hematologia', 'Infectologia', 'Nefrologia', 'Neurologia', 'Pneumologia', 'Gastroenterologia']
    for tema in temas_clinica:
        cursor.execute("UPDATE taxonomia_cronograma SET area = 'Clínica Médica' WHERE tema = ?", (tema,))
        cursor.execute("UPDATE taxonomia_cronograma SET area = 'Clínica Médica' WHERE area = 'Cirurgia' AND tema = ?", (tema,))

    # 3. Ginecologia e Obstetrícia
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Ginecologia e Obstetrícia' WHERE tema LIKE '%[GIN]%' OR tema LIKE '%[OBS]%'")
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Ginecologia e Obstetrícia' WHERE area = 'GO'")

    # 4. Medicina Preventiva
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Medicina Preventiva' WHERE area = 'Preventiva'")
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Medicina Preventiva' WHERE tema IN ('Medidas de Saúde Coletiva', 'Processo Saúde-Doença')")

    # 5. Limpeza de 'Geral' e 'Taxonomia'
    cursor.execute("DELETE FROM taxonomia_cronograma WHERE area = 'Taxonomia de Áreas e Temas'")
    
    # Se sobrar algo em Geral que sabemos ser de outra área
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Cirurgia' WHERE area = 'Geral' AND tema IN ('Trauma', 'TCE')")

    conn.commit()
    
    # Verificação
    cursor.execute("SELECT DISTINCT area FROM taxonomia_cronograma")
    areas = cursor.fetchall()
    print(f"Áreas consolidadas: {[a[0] for a in areas]}")
    
    conn.close()

if __name__ == "__main__":
    fix_taxonomy()
