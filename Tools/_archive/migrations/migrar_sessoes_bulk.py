"""
migrar_sessoes_bulk.py
Migracao unica: cria sessoes_bulk e corrige taxonomia_cronograma
com os dados reais (ground truth) fornecidos pelo usuario.

Execute uma vez:
    python tools/migrar_sessoes_bulk.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

HISTORICO = [
    ("Pediatria",    330, 278),
    ("Preventiva",   499, 415),
    ("Cirurgia",     341, 259),
    ("Infecto",      177, 141),
    ("Obstreticia",  253, 213),
    ("Ginecologia",  260, 204),
    ("Gastro",       188, 152),
    ("Endocrino",     95,  72),
    ("Cardiologia",   66,  45),
    ("Psiquiatria",   23,  20),
    ("Neurologia",   549, 431),
    ("Nefrologia",    61,  46),
    ("Hemato",        20,  18),
    ("Pneumo",        80,  61),
    ("Dermato",       24,  16),
    ("Reumato",       21,  21),
    ("Hepato",        14,   8),
    ("Otorrino",      19,  13),
    ("Ortopedia",      0,   0),
    ("Oftalmo",        0,   0),
]

AREAS_FANTASMA = (
    "Clinica Medica", "Cl\u00ednica M\u00e9dica",
    "Saude Coletiva", "Sa\u00fade Coletiva",
    "GO",
)

def criar_tabela(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessoes_bulk (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao_num          INTEGER,
            area                TEXT NOT NULL,
            questoes_feitas     INTEGER DEFAULT 0,
            questoes_acertadas  INTEGER DEFAULT 0,
            data_sessao         DATE DEFAULT CURRENT_DATE,
            observacoes         TEXT
        )
    """)
    print("[OK] Tabela sessoes_bulk criada (ou ja existia).")

def ja_migrado(conn):
    cur = conn.execute("SELECT COUNT(*) FROM sessoes_bulk WHERE sessao_num = 0")
    return cur.fetchone()[0] > 0

def corrigir_taxonomia(conn):
    for area, feitas, acertos in HISTORICO:
        if feitas == 0:
            continue
        pct = round(acertos / feitas * 100, 2)
        row = conn.execute(
            "SELECT id FROM taxonomia_cronograma WHERE area = ? LIMIT 1", (area,)
        ).fetchone()
        if row:
            conn.execute("""
                UPDATE taxonomia_cronograma
                SET questoes_realizadas = ?,
                    questoes_acertadas  = ?,
                    percentual_acertos  = ?
                WHERE area = ?
            """, (feitas, acertos, pct, area))
            print("  [FIX] %-15s -> %d feitas / %d acertos (%.1f%%)" % (area, feitas, acertos, pct))
        else:
            conn.execute("""
                INSERT INTO taxonomia_cronograma
                    (area, tema, questoes_realizadas, questoes_acertadas,
                     percentual_acertos, ultima_revisao)
                VALUES (?, ?, ?, ?, ?, '2026-04-16')
            """, (area, "[bulk] " + area, feitas, acertos, pct))
            print("  [NEW] %-15s -> criada (%d / %d)" % (area, feitas, acertos))

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        criar_tabela(conn)

        if ja_migrado(conn):
            print("[AVISO] Migracao historica (sessao_num=0) ja executada. Abortando.")
            return

        print("\n[INFO] Inserindo dados historicos em sessoes_bulk ...")
        total_q = 0
        total_a = 0
        for area, feitas, acertos in HISTORICO:
            conn.execute("""
                INSERT INTO sessoes_bulk
                    (sessao_num, area, questoes_feitas, questoes_acertadas,
                     data_sessao, observacoes)
                VALUES (0, ?, ?, ?, '2026-04-16', 'Migracao historica -- sessoes 001-066')
            """, (area, feitas, acertos))
            total_q += feitas
            total_a += acertos
            pct = (acertos / feitas * 100) if feitas else 0.0
            print("  [OK] %-15s: %4d questoes, %4d acertos (%.1f%%)" % (area, feitas, acertos, pct))

        print("\n[TOTAL] %d questoes / %d acertos (%.1f%%)" % (total_q, total_a, total_a / total_q * 100))

        print("\n[INFO] Corrigindo taxonomia_cronograma ...")
        corrigir_taxonomia(conn)

        for f in AREAS_FANTASMA:
            conn.execute("DELETE FROM taxonomia_cronograma WHERE area = ?", (f,))
        # Ortopedia/Oftalmo zeradas tambem sao lixo
        conn.execute("""
            DELETE FROM taxonomia_cronograma
            WHERE area IN ('Ortopedia', 'Oftalmo') AND questoes_realizadas = 0
        """)
        print("[OK] Areas fantasma removidas.")

        conn.commit()
        print("\n[SUCESSO] Migracao concluida!")
    except Exception as e:
        print("[ERRO]", e)
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
