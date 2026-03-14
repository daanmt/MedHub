import sqlite3
import pandas as pd
import os
from datetime import datetime
from app.utils.fsrs import FSRS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_db_metrics():
    """Consulta métricas detalhadas: Erros, Acertos e Desempenho por Área"""
    conn = get_connection()
    # Puxamos dados de acertos/realizações da taxonomia
    df_tax = pd.read_sql('''
        SELECT 
            area as Área,
            SUM(questoes_realizadas) as Total,
            SUM(questoes_acertadas) as Acertos
        FROM taxonomia_cronograma
        GROUP BY area
    ''', conn)
    
    # Puxamos dados de erros do caderno
    df_erros = pd.read_sql('''
        SELECT 
            t.area as Área,
            COUNT(q.id) as Erros
        FROM taxonomia_cronograma t
        LEFT JOIN questoes_erros q ON q.tema_id = t.id
        GROUP BY t.area
    ''', conn)
    
    # Merge dos dados
    df_final = pd.merge(df_tax, df_erros, on="Área", how="left").fillna(0)
    df_final['Erros'] = df_final['Erros'].astype(int)
    
    # Cálculo de Desempenho (%) por Área
    df_final['Desempenho'] = df_final.apply(
        lambda x: (x['Acertos'] / x['Total'] * 100) if x['Total'] > 0 else 0, axis=1
    )
    
    total_erros = int(df_final['Erros'].sum())
    total_acertos = int(df_final['Acertos'].sum())
    total_questoes = int(df_final['Total'].sum())
    media_desempenho = (total_acertos / total_questoes * 100) if total_questoes > 0 else 0
    
    conn.close()
    return {
        "total_erros": total_erros,
        "total_acertos": total_acertos,
        "total_questoes": total_questoes,
        "media_desempenho": media_desempenho,
        "df_areas": df_final.sort_values(by="Erros", ascending=False)
    }

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
