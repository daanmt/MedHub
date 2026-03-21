import sqlite3

DB_PATH = 'ipub.db'

def padronizar_areas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Unificar "GO" e similares para "Ginecologia e Obstetrícia"
    cursor.execute("""
        UPDATE taxonomia_cronograma 
        SET area = 'Ginecologia e Obstetrícia' 
        WHERE area = 'GO' OR area = 'Ginecologia' OR area = 'Ginecologia e obstetricia'
    """)
    
    # Consolidar Sífilis cases if they belong to different themes but same area
    # Not deleting them just in case they have different questions, but standardizing area
    
    conn.commit()
    conn.close()
    print("Áreas padronizadas!")

if __name__ == "__main__":
    padronizar_areas()
