import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_db_metrics():
    """Consulta limpa trazendo métricas 100% fieis de taxonomia_cronograma e questoes_erros"""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT 
            t.area as Área,
            COUNT(q.id) as Erros
        FROM taxonomia_cronograma t
        LEFT JOIN questoes_erros q ON q.tema_id = t.id
        GROUP BY t.area
        HAVING Erros > 0
        ORDER BY Erros DESC
    ''', conn)
    total = int(df['Erros'].sum()) if not df.empty else 0
    conn.close()
    return {"total": total, "df_areas": df}

def get_caderno_erros():
    """Traz todos os flashcards do caderno unindo relacionalmente com a taxonomia"""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT 
            t.area as Área,
            t.tema as Tema,
            q.tipo_erro as Tipo,
            q.elo_quebrado as Elo,
            q.enunciado as Questão,
            q.alternativa_correta as Correta,
            q.alternativa_marcada as Marcada,
            q.armadilha_prova as Armadilha
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
        ORDER BY q.id DESC
    ''', conn)
    conn.close()
    return df
