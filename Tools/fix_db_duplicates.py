import sqlite3
import pandas as pd

DB_PATH = 'ipub.db'

def fix_duplicates():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Unificar Sifilis
    c.execute("SELECT id, tema FROM taxonomia_cronograma WHERE tema LIKE '%ifilis%'")
    rows = c.fetchall()
    
    if rows:
        main_id = rows[0][0]
        # Aplica explicitamente as 47 feitas e 43 corretas que o usuario pontuou, 
        # e joga a última_revisão para 'now'
        c.execute('''
            UPDATE taxonomia_cronograma 
            SET tema = 'Sífilis na Gestação e Congênita', 
                area = 'Ginecologia e Obstetrícia', 
                questoes_realizadas = 47, 
                questoes_acertadas = 43, 
                percentual_acertos = 91.49, 
                ultima_revisao = date('now') 
            WHERE id = ?
        ''', (main_id,))
        
        # Redirecionar dependencias dos outros ids e deletar 
        for r in rows[1:]:
            old_id = r[0]
            c.execute("UPDATE questoes_erros SET tema_id = ? WHERE tema_id = ?", (main_id, old_id))
            c.execute("UPDATE flashcards SET tema_id = ? WHERE tema_id = ?", (main_id, old_id))
            c.execute("DELETE FROM taxonomia_cronograma WHERE id = ?", (old_id,))

    # 2. Deletar 'Geral' se não tiver questoes_realizadas
    c.execute("DELETE FROM taxonomia_cronograma WHERE tema = 'Geral' AND questoes_realizadas = 0")

    conn.commit()
    conn.close()
    print("Sinergia concluída: Sífilis unificada com 43 acertos e dependências migradas.")

if __name__ == '__main__':
    fix_duplicates()
