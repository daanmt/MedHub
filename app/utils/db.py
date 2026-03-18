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

def init_fsrs_cache_tables():
    """Cria tabelas FSRS para os cards do flashcards_cache.json (se não existirem)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fsrs_cache_cards (
            erro_origem INTEGER PRIMARY KEY,
            state INTEGER DEFAULT 0,
            stability REAL DEFAULT 0.0,
            difficulty REAL DEFAULT 0.0,
            scheduled_days INTEGER DEFAULT 0,
            reps INTEGER DEFAULT 0,
            lapses INTEGER DEFAULT 0,
            last_review DATETIME,
            due DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fsrs_cache_revlog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            erro_origem INTEGER,
            rating INTEGER,
            state INTEGER,
            stability REAL,
            difficulty REAL,
            scheduled_days INTEGER,
            review_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def get_cache_fsrs_state(erro_origem: int) -> dict:
    """Retorna o estado FSRS de um card do cache. Inicializa se não existir."""
    init_fsrs_cache_tables()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fsrs_cache_cards WHERE erro_origem = ?", (erro_origem,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        fsrs = FSRS()
        return {**fsrs.init_card(), 'erro_origem': erro_origem}

    cols = ['erro_origem', 'state', 'stability', 'difficulty', 'scheduled_days',
            'reps', 'lapses', 'last_review', 'due']
    return dict(zip(cols, row))


def record_cache_review(erro_origem: int, rating: int) -> dict:
    """Aplica FSRS e persiste o estado atualizado para um card do cache."""
    init_fsrs_cache_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fsrs_cache_cards WHERE erro_origem = ?", (erro_origem,))
    row = cursor.fetchone()

    fsrs = FSRS()
    if row is None:
        card_data = fsrs.init_card()
    else:
        cols = ['erro_origem', 'state', 'stability', 'difficulty', 'scheduled_days',
                'reps', 'lapses', 'last_review', 'due']
        card_data = dict(zip(cols, row))

    new_state = fsrs.evaluate(card_data, rating)

    cursor.execute('''
        INSERT INTO fsrs_cache_cards
            (erro_origem, state, stability, difficulty, scheduled_days, reps, lapses, last_review, due)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(erro_origem) DO UPDATE SET
            state=excluded.state, stability=excluded.stability, difficulty=excluded.difficulty,
            scheduled_days=excluded.scheduled_days, reps=excluded.reps, lapses=excluded.lapses,
            last_review=excluded.last_review, due=excluded.due
    ''', (
        erro_origem, new_state['state'], new_state['stability'], new_state['difficulty'],
        new_state['scheduled_days'], new_state['reps'], new_state['lapses'],
        new_state['last_review'], new_state['due']
    ))

    cursor.execute('''
        INSERT INTO fsrs_cache_revlog (erro_origem, rating, state, stability, difficulty, scheduled_days)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        erro_origem, rating, new_state['state'], new_state['stability'],
        new_state['difficulty'], new_state['scheduled_days']
    ))

    conn.commit()
    conn.close()
    return new_state


def get_cache_due_count() -> int:
    """Quantos cards do cache estão vencidos para revisão hoje."""
    try:
        init_fsrs_cache_tables()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM fsrs_cache_cards WHERE due <= ? AND state > 0",
            (datetime.now(),)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def sync_git():
    """Executa o commit e push do banco de dados para o GitHub"""
    import subprocess
    try:
        # 1. Add
        subprocess.run(["git", "add", "ipub.db"], check=True)
        # 2. Commit
        msg = f"update: progress sync {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        # 3. Push
        subprocess.run(["git", "push"], check=True)
        return True, "Sincronização concluída com sucesso!"
    except subprocess.CalledProcessError as e:
        return False, f"Erro no processo Git: {e}"
    except Exception as e:
        return False, f"Erro inesperado: {e}"
