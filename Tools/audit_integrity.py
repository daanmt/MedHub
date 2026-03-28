#!/usr/bin/env python3
"""MedHub — Auditoria de Integridade do Banco. Uso: python tools/audit_integrity.py"""
import sys, os
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.db import get_connection

def main():
    conn = get_connection()
    ok = True

    print("\n=== MedHub — Auditoria de Integridade ===\n")

    # 1. Schema: colunas obrigatórias em flashcards
    cols = {r[1] for r in conn.execute("PRAGMA table_info(flashcards)").fetchall()}
    required = {'frente_pergunta','verso_resposta','verso_regra_mestre',
                'verso_armadilha','frente_contexto','quality_source',
                'card_version','needs_qualitative'}
    missing = required - cols
    if missing:
        print(f"[FAIL] flashcards schema: colunas faltando: {missing}")
        ok = False
    else:
        print("[OK]   flashcards: schema v5 completo")

    # 2. fsrs_cards órfãos
    orphan_fsrs = conn.execute("""
        SELECT COUNT(*) FROM fsrs_cards fc
        LEFT JOIN flashcards f ON fc.card_id = f.id
        WHERE f.id IS NULL
    """).fetchone()[0]
    if orphan_fsrs:
        print(f"[WARN] fsrs_cards órfãos (sem flashcard): {orphan_fsrs}")
        ok = False
    else:
        print("[OK]   fsrs_cards: sem órfãos")

    # 3. fsrs_revlog órfãos
    orphan_revlog = conn.execute("""
        SELECT COUNT(*) FROM fsrs_revlog r
        LEFT JOIN fsrs_cards fc ON r.card_id = fc.card_id
        WHERE fc.card_id IS NULL
    """).fetchone()[0]
    if orphan_revlog:
        print(f"[WARN] fsrs_revlog órfãos (sem fsrs_cards): {orphan_revlog}")
    else:
        print("[OK]   fsrs_revlog: consistente")

    # 4. questoes_erros sem flashcard
    no_flash = conn.execute("""
        SELECT COUNT(*) FROM questoes_erros qe
        LEFT JOIN flashcards f ON f.questao_id = qe.id
        WHERE f.id IS NULL
    """).fetchone()[0]
    print(f"[INFO] questoes_erros sem flashcard: {no_flash}")

    # 5. Taxonomia mismatch
    orphan_temas = conn.execute("""
        SELECT COUNT(DISTINCT f.tema_id) FROM flashcards f
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE t.id IS NULL
    """).fetchone()[0]
    total_temas = conn.execute("SELECT COUNT(DISTINCT tema_id) FROM flashcards").fetchone()[0]
    if orphan_temas:
        print(f"[WARN] tema_ids sem match em taxonomia_cronograma: {orphan_temas}/{total_temas}")
        print("       -> Ver tools/fix_taxonomy_bridge.py para corrigir")
    else:
        print("[OK]   taxonomia: todos os tema_ids mapeados")

    # 6. Cards sem verso_resposta (vazio após regeneração)
    empty_resp = conn.execute("""
        SELECT COUNT(*) FROM flashcards
        WHERE verso_resposta IS NULL OR TRIM(verso_resposta) = ''
    """).fetchone()[0]
    if empty_resp:
        print(f"[WARN] cards sem verso_resposta (dados insuficientes): {empty_resp}")
    else:
        print("[OK]   verso_resposta: todos populados")

    # 7. Backup policy check
    import glob
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_pattern = os.path.join(project_root, 'artifacts', 'backups', 'ipub_backup_*.db')
    backups = sorted(glob.glob(backup_pattern))
    if backups:
        print(f"[INFO] Backups disponíveis: {len(backups)} em artifacts/backups/")
        print(f"       Mais recente: {os.path.basename(backups[-1])}")
        print("       NOTA: Restaurar backup requer re-rodar migrate_flashcards.py + regenerate_cards.py")
    else:
        print("[WARN] Nenhum backup encontrado — rode tools/backup_db.py")

    print()
    print("[SUMÁRIO]", "OK — sem problemas críticos" if ok else "ATENÇÃO — verificar items [FAIL]")
    print()
    conn.close()

if __name__ == '__main__':
    main()
