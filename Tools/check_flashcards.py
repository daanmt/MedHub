import sqlite3
import pandas as pd

def check_flashcards():
    conn = sqlite3.connect('ipub.db')
    df = pd.read_sql_query("SELECT id, frente, verso FROM flashcards", conn)
    generic = df[df['verso'].str.contains('este cenário', case=False, na=False) | df['verso'].str.contains('seu erro', case=False, na=False)]
    print(f"Total flashcards: {len(df)}")
    print(f"Total genéricos/placeholders detectados: {len(generic)}")
    for _, r in generic.head(5).iterrows():
        print(f"ID {r['id']} -> {r['verso'][:100]}...")
    conn.close()

if __name__ == '__main__':
    check_flashcards()
