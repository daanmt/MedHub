import sqlite3
import os

DB_PATH = 'ipub.db'

def init_db():
    print("Iniciando a criação do banco de dados IPUB... (Fase 2/3 Roadmap)")
    
    # Se já existir, podemos optar por backup (neste script iniciaremos zerado caso delete-se)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela 1: Taxonomia do Estratégia Med & Dash de Progresso
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxonomia_cronograma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT NOT NULL,           -- Ex: Cirurgia, Pediatria, G.O
        tema TEXT NOT NULL,           -- Ex: ATLS, Imunizações, Sífilis na Gestação
        questoes_realizadas INTEGER DEFAULT 0,
        questoes_acertadas INTEGER DEFAULT 0,
        percentual_acertos REAL DEFAULT 0.0,
        ultima_revisao DATE
    )
    ''')

    # Tabela 2: Caderno de Erros Estruturado
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questoes_erros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema_id INTEGER,
        enunciado TEXT,
        alternativa_correta TEXT,
        alternativa_marcada TEXT,
        tipo_erro TEXT,              -- Ex: Lacuna de conhecimento, Erro de aplicação
        elo_quebrado TEXT,
        armadilha_prova TEXT,
        data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tema_id) REFERENCES taxonomia_cronograma(id)
    )
    ''')

    # Tabela 3: Flashcards Front/Back ou Cloze
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questao_id INTEGER,          -- Link com a origem do erro
        tema_id INTEGER,             -- Link com a taxonomia
        tipo TEXT,                   -- 'FrontBack' ou 'Cloze'
        frente TEXT NOT NULL,
        verso TEXT NOT NULL,
        FOREIGN KEY (questao_id) REFERENCES questoes_erros(id),
        FOREIGN KEY (tema_id) REFERENCES taxonomia_cronograma(id)
    )
    ''')

    # Tabela 4: FSRS (Memory State) - O cérebro do espaçamento
    # state: 0=New, 1=Learning, 2=Review, 3=Relearning
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fsrs_cards (
        card_id INTEGER PRIMARY KEY, -- 1:1 com flashcards(id)
        state INTEGER DEFAULT 0,
        due DATETIME,                -- Próxima revisão agendada
        stability REAL DEFAULT 0.0,  -- (S) Em dias pra cair a 90%
        difficulty REAL DEFAULT 0.0, -- (D) Otimizado via heurística retroativa
        elapsed_days INTEGER DEFAULT 0,
        scheduled_days INTEGER DEFAULT 0,
        reps INTEGER DEFAULT 0,
        lapses INTEGER DEFAULT 0,
        last_review DATETIME,
        FOREIGN KEY (card_id) REFERENCES flashcards(id)
    )
    ''')

    # Tabela 5: FSRS Log de Revisão (Fundamental para otimização futura)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fsrs_revlog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER,
        rating INTEGER,               -- 1=Again, 2=Hard, 3=Good, 4=Easy
        state INTEGER,
        due DATETIME,
        stability REAL,
        difficulty REAL,
        elapsed_days INTEGER,
        last_elapsed_days INTEGER,
        scheduled_days INTEGER,
        review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (card_id) REFERENCES fsrs_cards(card_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Sucesso! Modelo DSR + Excel EMED instanciados no SQLite virtual (ipub.db).")

if __name__ == "__main__":
    init_db()
