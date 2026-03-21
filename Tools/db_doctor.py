import sqlite3
import os
import re

DB_PATH = 'ipub.db'

def clean_html_tags(text):
    if not text:
        return text
    # Remove div wraps
    cleaned = re.sub(r'<div[^>]*>', '', text)
    cleaned = cleaned.replace('</div>', '')
    # Remove some breaks that markdown doesn't like alongside html
    cleaned = cleaned.replace('<br>', '\n')
    return cleaned.strip()

def run_doctor():
    print("Iniciando Cirurgia no Banco de Dados (DB Doctor)...")
    if not os.path.exists(DB_PATH):
        print("ipub.db não encontrado!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Pulverizar linhas "Importado via CSV" fantasmas que sobraram
    cursor.execute("DELETE FROM taxonomia_cronograma WHERE area = 'Importado via CSV'")
    rowcount = cursor.rowcount
    print(f"[{rowcount}] Linhas lixo 'Importado via CSV' apagadas do cronograma.")

    # 2. Limpar a formatação HTML dos Flashcards
    cursor.execute("SELECT id, frente, verso FROM flashcards")
    cards = cursor.fetchall()
    cleaned_count = 0

    for card_id, frente, verso in cards:
        new_frente = clean_html_tags(frente)
        new_verso = clean_html_tags(verso)

        if new_frente != frente or new_verso != verso:
            cursor.execute("UPDATE flashcards SET frente = ?, verso = ? WHERE id = ?", (new_frente, new_verso, card_id))
            cleaned_count += 1
    
    print(f"[{cleaned_count}] Flashcards tiveram a casca HTML removida, mantendo apenas Markdown.")

    # 3. Consertar a área de itens em duplicidade sem acento
    cursor.execute("UPDATE taxonomia_cronograma SET area = 'Ginecologia e Obstetrícia' WHERE tema LIKE '%Sifilis%' AND area != 'Ginecologia e Obstetrícia'")
    print(f"[{cursor.rowcount}] Correções ortográficas forçadas na Taxonomia.")

    conn.commit()
    conn.close()
    print("Cirurgia concluída com sucesso! Banco limpo e higienizado para o MedHub.")

if __name__ == "__main__":
    run_doctor()
