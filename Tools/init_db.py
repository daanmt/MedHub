import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

def init_db():
    """Cria o schema canônico do ipub.db (idempotente via CREATE TABLE IF NOT EXISTS).

    Schema alinhado com o estado vivo do app (sessão 071+):
      - flashcards: v5 (frente_contexto / frente_pergunta / verso_resposta /
        verso_regra_mestre / verso_armadilha + quality_source / card_version /
        needs_qualitative). Sem colunas legadas frente/verso.
      - sessoes_bulk: agregados por sessão (escrito por registrar_sessao_bulk.py,
        lido pelo dashboard e por performance.py).
    """
    print(f"Inicializando schema do ipub.db em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela 1: Taxonomia (mapa área → tema com agregados)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxonomia_cronograma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        area TEXT NOT NULL,
        tema TEXT NOT NULL,
        questoes_realizadas INTEGER DEFAULT 0,
        questoes_acertadas INTEGER DEFAULT 0,
        percentual_acertos REAL DEFAULT 0.0,
        ultima_revisao DATE
    )
    ''')

    # Tabela 2: Caderno de erros estruturado
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questoes_erros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema_id INTEGER,
        titulo TEXT,
        complexidade TEXT,
        enunciado TEXT,
        alternativa_correta TEXT,
        alternativa_marcada TEXT,
        tipo_erro TEXT,
        habilidades_sequenciais TEXT,
        o_que_faltou TEXT,
        explicacao_correta TEXT,
        armadilha_prova TEXT,
        data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tema_id) REFERENCES taxonomia_cronograma(id)
    )
    ''')

    # Tabela 3: Flashcards v5 (schema atual; sem colunas legadas frente/verso)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questao_id INTEGER,
        tema_id INTEGER,
        tipo TEXT,
        frente_contexto TEXT,
        frente_pergunta TEXT,
        verso_resposta TEXT,
        verso_regra_mestre TEXT,
        verso_armadilha TEXT,
        quality_source TEXT DEFAULT 'legacy',
        card_version INTEGER DEFAULT 1,
        needs_qualitative INTEGER DEFAULT 0,
        FOREIGN KEY (questao_id) REFERENCES questoes_erros(id),
        FOREIGN KEY (tema_id) REFERENCES taxonomia_cronograma(id)
    )
    ''')

    # Tabela 4: FSRS state (1:1 com flashcards)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fsrs_cards (
        card_id INTEGER PRIMARY KEY,
        state INTEGER DEFAULT 0,
        due DATETIME,
        stability REAL DEFAULT 0.0,
        difficulty REAL DEFAULT 0.0,
        elapsed_days INTEGER DEFAULT 0,
        scheduled_days INTEGER DEFAULT 0,
        reps INTEGER DEFAULT 0,
        lapses INTEGER DEFAULT 0,
        last_review DATETIME,
        FOREIGN KEY (card_id) REFERENCES flashcards(id)
    )
    ''')

    # Tabela 5: FSRS log de revisão
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fsrs_revlog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER,
        rating INTEGER,
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

    # Tabela 6: Sessoes bulk (agregados por sessão; SSOT de totais no dashboard)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessoes_bulk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sessao_num INTEGER,
        area TEXT NOT NULL,
        questoes_feitas INTEGER DEFAULT 0,
        questoes_acertadas INTEGER DEFAULT 0,
        data_sessao DATE DEFAULT CURRENT_DATE,
        observacoes TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print("Schema criado/atualizado. Tabelas: taxonomia_cronograma, questoes_erros, "
          "flashcards (v5), fsrs_cards, fsrs_revlog, sessoes_bulk.")

if __name__ == "__main__":
    init_db()
