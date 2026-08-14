"""check_fk_orphans.py — varredura read-only de órfãos referenciais no ipub.db.

As FKs do schema sempre existiram, mas só passaram a ser impostas na part-1
(PRAGMA foreign_keys por conexão). Linhas órfãs PRÉ-existentes não são pegas
pelo PRAGMA (ele só valida escritas novas) — este script as detecta.

Padrão warn-first: reporta [WARN] e sai exit 0 SEMPRE — limpeza de dado é
decisão do operador/agente MedHub, nunca deste script (que não escreve nada).
Achados registrados no ledger-of-self (tag `fk_orphans`) quando disponível.

Uso: python tools/check_fk_orphans.py
Baseline 2026-08-14: 0 órfãos nas 5 varreduras.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ipub.db")

# (nome da varredura, SQL de contagem de órfãos)
VARREDURAS = [
    ("fsrs_cards->flashcards",
     "SELECT COUNT(*) FROM fsrs_cards fc LEFT JOIN flashcards f ON f.id = fc.card_id "
     "WHERE f.id IS NULL"),
    ("fsrs_revlog->fsrs_cards",
     "SELECT COUNT(*) FROM fsrs_revlog r LEFT JOIN fsrs_cards fc ON fc.card_id = r.card_id "
     "WHERE fc.card_id IS NULL"),
    ("flashcards->questoes_erros",
     "SELECT COUNT(*) FROM flashcards f WHERE f.questao_id IS NOT NULL "
     "AND NOT EXISTS (SELECT 1 FROM questoes_erros q WHERE q.id = f.questao_id)"),
    ("flashcards->taxonomia_cronograma",
     "SELECT COUNT(*) FROM flashcards f WHERE f.tema_id IS NOT NULL "
     "AND NOT EXISTS (SELECT 1 FROM taxonomia_cronograma t WHERE t.id = f.tema_id)"),
    ("flashcards sem estado FSRS",
     "SELECT COUNT(*) FROM flashcards f LEFT JOIN fsrs_cards fc ON fc.card_id = f.id "
     "WHERE fc.card_id IS NULL"),
]


def run_checks(db_path=None):
    """Roda as 5 varreduras. Retorna lista de achados [{'alvo', 'payload'}] —
    vazia = base limpa. Sensor defensivo: banco inacessível vira achado próprio
    (nunca silêncio que mascare sensor quebrado)."""
    path = db_path or DB_PATH
    achados = []
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except Exception as e:
        return [{"alvo": "sensor", "payload": {"erro": f"banco inacessivel: {e}"}}]
    try:
        for nome, sql in VARREDURAS:
            try:
                n = conn.execute(sql).fetchone()[0]
            except Exception as e:
                achados.append({"alvo": nome, "payload": {"erro": f"varredura falhou: {e}"}})
                continue
            if n > 0:
                achados.append({"alvo": nome, "payload": {"orfaos": n}})
    finally:
        conn.close()
    return achados


def main():
    achados = run_checks()
    if not achados:
        print("[OK] FK_ORPHANS: 0 orfaos nas 5 varreduras.")
    for a in achados:
        det = a["payload"].get("erro") or f"{a['payload'].get('orfaos')} linha(s) orfa(s)"
        print(f"[WARN] FK_ORPHANS: {a['alvo']} -- {det}. "
              f"Limpeza e decisao do operador; este script nao escreve.")
    try:
        import ledger_self
        ledger_self.record("fk_orphans", achados)
    except Exception as e:
        print(f"[WARN] FK_ORPHANS: ledger indisponivel ({e}); achados so no stdout.")
    return 0  # warn-first: nunca bloqueia


if __name__ == "__main__":
    sys.exit(main())
