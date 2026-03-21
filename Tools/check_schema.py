import sqlite3

def check_db():
    try:
        conn = sqlite3.connect('ipub.db')
        c = conn.cursor()
        c.execute("PRAGMA table_info(questoes_erros)")
        cols = [row[1] for row in c.fetchall()]
        print("Colunas de questoes_erros:", cols)
        
        c.execute("PRAGMA table_info(flashcards)")
        cols2 = [row[1] for row in c.fetchall()]
        print("Colunas de flashcards:", cols2)
        conn.close()
    except Exception as e:
        print("Erro:", e)

if __name__ == '__main__':
    check_db()
