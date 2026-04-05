import sqlite3
import pandas as pd
import os
from datetime import datetime
from app.utils.fsrs import FSRS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_db_metrics():
    """Consulta métricas de desempenho por área (1 linha por área após import fixado)."""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT
            area AS "Área",
            SUM(questoes_realizadas) AS "Total",
            SUM(questoes_acertadas)  AS "Acertos"
        FROM taxonomia_cronograma
        GROUP BY area
        HAVING SUM(questoes_realizadas) > 0
    ''', conn)
    conn.close()
    if df.empty:
        return {'total_questoes': 0, 'total_acertos': 0, 'media_desempenho': 0.0, 'df_areas': df}
    df['Desempenho'] = (df['Acertos'] / df['Total'] * 100).round(1)
    df = df.sort_values('Desempenho', ascending=True)
    total_questoes = int(df['Total'].sum())
    total_acertos  = int(df['Acertos'].sum())
    media          = total_acertos / total_questoes * 100 if total_questoes > 0 else 0.0
    return {'total_questoes': total_questoes, 'total_acertos': total_acertos,
            'media_desempenho': round(media, 1), 'df_areas': df}

def get_caderno_erros():
    """Traz todos os flashcards do caderno unindo relacionalmente com a taxonomia"""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT 
            t.area as Área,
            t.tema as Tema,
            q.tipo_erro as Tipo,
            q.habilidades_sequenciais as Elo,
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

def get_cronograma():
    """Retorna o DataFrame do progresso do cronograma"""
    conn = get_connection()
    df = pd.read_sql('SELECT id, semana as Semana, tema as Tema, status as Status FROM cronograma_progresso ORDER BY pos_semana, pos_tema', conn)
    conn.close()
    return df

def update_cronograma_status(row_id, new_status):
    """Atualiza o status de um tema no cronograma"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE cronograma_progresso SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_status, row_id))
    conn.commit()
    conn.close()

def get_due_cards_count():
    """Retorna quantos cards estão vencidos para hoje"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fsrs_cards WHERE due <= ?", (datetime.now(),))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_next_due_card():
    """Busca o próximo card a ser revisado (Frente, Verso, CardID)"""
    conn = get_connection()
    # Pela lógica FSRS, buscamos o que venceu há mais tempo
    df = pd.read_sql('''
        SELECT 
            f.id as flashcard_id,
            f.frente,
            f.verso,
            fc.state,
            fc.stability,
            fc.difficulty,
            fc.reps,
            fc.lapses,
            t.area,
            t.tema
        FROM fsrs_cards fc
        JOIN flashcards f ON f.id = fc.card_id
        JOIN taxonomia_cronograma t ON t.id = f.tema_id
        WHERE fc.due <= ?
        ORDER BY fc.due ASC
        LIMIT 1
    ''', conn, params=(datetime.now(),))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

def record_review(flashcard_id, rating):
    """Aplica o algoritmo FSRS e atualiza o banco de dados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Busca estado atual do card
    df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn, params=(flashcard_id,))
    if df.empty:
        fsrs = FSRS()
        card_data = fsrs.init_card()
        card_data['card_id'] = flashcard_id
    else:
        card_data = df.iloc[0].to_dict()

    # 2. Calcula próximo estado via FSRS
    fsrs = FSRS()
    new_metrics = fsrs.evaluate(card_data, rating)
    
    # 3. Atualiza banco
    cursor.execute('''
        UPDATE fsrs_cards 
        SET state = ?, due = ?, stability = ?, difficulty = ?, 
            elapsed_days = ?, scheduled_days = ?, reps = ?, lapses = ?, last_review = ?
        WHERE card_id = ?
    ''', (
        new_metrics['state'], new_metrics['due'], new_metrics['stability'], new_metrics['difficulty'],
        new_metrics['elapsed_days'], new_metrics['scheduled_days'], new_metrics['reps'], 
        new_metrics['lapses'], new_metrics['last_review'], flashcard_id
    ))
    
    # 4. Log da revisão (Tabela nova no schema v3.6)
    cursor.execute('''
        INSERT INTO fsrs_revlog (card_id, rating, state, due, stability, difficulty, elapsed_days, scheduled_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        flashcard_id, rating, new_metrics['state'], new_metrics['due'], 
        new_metrics['stability'], new_metrics['difficulty'], 
        new_metrics['elapsed_days'], new_metrics['scheduled_days']
    ))
    
    conn.commit()
    conn.close()
    return new_metrics

def get_erros_resumidos():
    """Traz erros agrupados por tema para o Bloco 3"""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT
            t.area || ' - ' || t.tema as TemaFull,
            q.tipo_erro,
            q.habilidades_sequenciais as elo_quebrado,
            q.armadilha_prova,
            q.id
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
        ORDER BY t.area, t.tema
    ''', conn)
    conn.close()
    return df


def get_erros_por_tema(tema: str) -> list:
    """Retorna erros recentes filtrados por tema ou área (busca substring, case-insensitive).

    Args:
        tema: Termo de busca (ex: "Cardiologia", "IC", "Insuficiência Cardíaca").

    Returns:
        list[dict]: Lista de erros com chaves id, titulo, tipo_erro,
                    habilidades_sequenciais, armadilha_prova, explicacao_correta,
                    area, tema. Retorna [] se nenhum resultado.
    """
    conn = get_connection()
    df = pd.read_sql('''
        SELECT q.id, q.titulo, q.tipo_erro,
               q.habilidades_sequenciais, q.armadilha_prova, q.explicacao_correta,
               t.area, t.tema
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
        WHERE LOWER(t.tema) LIKE LOWER(?) OR LOWER(t.area) LIKE LOWER(?)
        ORDER BY q.id DESC
        LIMIT 20
    ''', conn, params=(f'%{tema}%', f'%{tema}%'))
    conn.close()
    return df.to_dict('records')


def get_cards_by_bucket() -> dict:
    """Retorna flashcards FSRS divididos em três buckets temporais.

    Returns:
        dict com chaves:
            atrasados (list[dict]): cards vencidos antes de hoje (state > 0)
            hoje (list[dict]): cards que vencem hoje (state > 0)
            novos (list[dict]): cards nunca revisados (state == 0), max 10
        Cada dict contém: card_id, frente_pergunta, verso_resposta, due, area, tema.
    """
    conn = get_connection()
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    df_atrasados = pd.read_sql('''
        SELECT f.id AS card_id, f.frente_pergunta, f.verso_resposta,
               fc.due, t.area, t.tema
        FROM flashcards f
        JOIN fsrs_cards fc ON f.id = fc.card_id
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE fc.due < ? AND fc.state > 0
        ORDER BY fc.due ASC
    ''', conn, params=(today_start,))

    df_hoje = pd.read_sql('''
        SELECT f.id AS card_id, f.frente_pergunta, f.verso_resposta,
               fc.due, t.area, t.tema
        FROM flashcards f
        JOIN fsrs_cards fc ON f.id = fc.card_id
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE fc.due >= ? AND fc.due <= ? AND fc.state > 0
        ORDER BY fc.due ASC
    ''', conn, params=(today_start, today_end))

    df_novos = pd.read_sql('''
        SELECT f.id AS card_id, f.frente_pergunta, f.verso_resposta,
               fc.due, t.area, t.tema
        FROM flashcards f
        JOIN fsrs_cards fc ON f.id = fc.card_id
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE fc.state = 0
        ORDER BY f.id ASC
        LIMIT 10
    ''', conn)

    conn.close()
    return {
        "atrasados": df_atrasados.to_dict('records'),
        "hoje": df_hoje.to_dict('records'),
        "novos": df_novos.to_dict('records'),
    }

