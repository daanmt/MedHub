import sqlite3
import shutil
import sys
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts', 'backups')


def main():
    # 0. Verificar versão SQLite
    if sqlite3.sqlite_version_info < (3, 35, 0):
        print(f"ERRO: SQLite {sqlite3.sqlite_version} < 3.35.0 — ALTER TABLE ... DROP COLUMN não suportado.")
        sys.exit(1)
    print(f"SQLite {sqlite3.sqlite_version}: OK")

    if not os.path.exists(DB_PATH):
        print(f"ERRO: banco não encontrado em {DB_PATH}")
        sys.exit(1)

    # 1. Backup datado antes de qualquer DROP
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"ipub_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup criado: {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Validação pré-DROP: migração v5 deve estar completa
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM flashcards WHERE frente_pergunta IS NULL AND frente IS NOT NULL"
        )
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"ERRO: migração v5 incompleta — {count} card(s) com frente não migrada. Abortando.")
            conn.close()
            sys.exit(1)
        print(f"Validação v5: 0 cards com frente_pergunta NULL — OK")
    except sqlite3.OperationalError as e:
        if "no such column: frente" in str(e):
            print("Coluna frente já removida — validação pulada.")
        else:
            print(f"ERRO na validação pré-DROP: {e}")
            conn.close()
            sys.exit(1)

    # 3. DROP tabelas legacy
    for table in ['fsrs_cache_cards', 'fsrs_cache_revlog', 'cronograma_progresso']:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"DROP TABLE {table}: OK")

    # 4. DROP colunas legacy da tabela flashcards
    for col in ['frente', 'verso']:
        try:
            cursor.execute(f"ALTER TABLE flashcards DROP COLUMN {col}")
            print(f"ALTER TABLE flashcards DROP COLUMN {col}: OK")
        except sqlite3.OperationalError as e:
            if "no such column" in str(e):
                print(f"Coluna {col} já não existe — pulando.")
            else:
                print(f"ERRO ao remover coluna {col}: {e}")
                conn.close()
                sys.exit(1)

    conn.commit()
    conn.close()
    print("\nLimpeza concluída com sucesso.")


if __name__ == '__main__':
    main()
