#!/usr/bin/env python3
"""
MedHub — Correção de Taxonomia: Bridge para 21 tema_ids Órfãos

Os tema_ids 1–21 e outros (27, 37–41) foram criados pelo insert_questao.py
em sessões anteriores ao ETL do Excel (que iniciou IDs em 22). Esses IDs
ficaram órfãos porque o ETL não herdou os registros antigos.

Modos:
    python Tools/fix_taxonomy_bridge.py --diagnose
        → Mostra os orphans com proposta de mapeamento e amostra de títulos

    python Tools/fix_taxonomy_bridge.py --apply --dry-run
        → Simula INSERT sem alterar o banco

    python Tools/fix_taxonomy_bridge.py --apply
        → Executa INSERT OR IGNORE para cada orphan mapeável

    python Tools/fix_taxonomy_bridge.py --export-manual bridge_manual.csv
        → Exporta CSV dos ambíguos para revisão manual
"""

import sys, os, csv, argparse, sqlite3

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ipub.db')

# Mapeamento inferido a partir dos títulos/conteúdo das questoes_erros vinculadas.
# Derivado de análise manual dos 21 orphan tema_ids (sessão 058).
MAPPING = {
    1:  ('Cirurgia',        'Trauma'),
    2:  ('Pediatria',       'Emergências Pediátricas'),
    3:  ('Pediatria',       'Geral'),
    4:  ('Pediatria',       'Geral'),
    5:  ('Clínica Médica',  'Geral'),
    6:  ('Clínica Médica',  'Endocrinologia'),
    7:  ('Clínica Médica',  'Geral'),
    8:  ('Pediatria',       'Cardiopatias Congênitas'),
    9:  ('Obstetrícia',     'Geral'),
    10: ('Obstetrícia',     'Geral'),
    11: ('Ginecologia',     'Geral'),
    12: ('Saúde Coletiva',  'Epidemiologia'),
    13: ('Saúde Coletiva',  'Epidemiologia'),
    19: ('Saúde Coletiva',  'Epidemiologia'),
    21: ('Clínica Médica',  'Gastroenterologia'),
    27: ('Clínica Médica',  'Endocrinologia'),
    37: ('Clínica Médica',  'Infectologia'),
    38: ('Clínica Médica',  'Infectologia'),
    39: ('Clínica Médica',  'Infectologia'),
    40: ('Clínica Médica',  'Infectologia'),
    41: ('Clínica Médica',  'Infectologia'),
}


def get_orphans(conn):
    """Retorna lista de tema_ids sem entry em taxonomia_cronograma."""
    rows = conn.execute("""
        SELECT DISTINCT f.tema_id
        FROM flashcards f
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE t.id IS NULL
        ORDER BY f.tema_id
    """).fetchall()
    return [r[0] for r in rows]


def get_sample_titles(conn, tema_id, n=3):
    rows = conn.execute("""
        SELECT q.titulo FROM questoes_erros q
        WHERE q.tema_id = ?
        ORDER BY q.id
        LIMIT ?
    """, (tema_id, n)).fetchall()
    return [r[0] or '(sem título)' for r in rows]


def get_card_count(conn, tema_id):
    return conn.execute(
        "SELECT COUNT(*) FROM flashcards WHERE tema_id = ?", (tema_id,)
    ).fetchone()[0]


def diagnose(conn):
    orphans = get_orphans(conn)
    if not orphans:
        print("[OK] Nenhum orphan encontrado — taxonomia íntegra.")
        return

    print(f"\nOrphan tema_ids: {len(orphans)}\n")
    print(f"{'ID':>4}  {'N':>4}  {'Area proposta':<20}  {'Tema proposto':<25}  Amostra títulos")
    print("-" * 100)

    unmapped = []
    for tid in orphans:
        n = get_card_count(conn, tid)
        titles = get_sample_titles(conn, tid)
        sample = titles[0][:55] if titles else '-'

        if tid in MAPPING:
            area, tema = MAPPING[tid]
            print(f"  {tid:>2}  {n:>4}  {area:<20}  {tema:<25}  {sample}")
        else:
            print(f"  {tid:>2}  {n:>4}  {'???':<20}  {'???':<25}  {sample}")
            unmapped.append(tid)

    print()
    if unmapped:
        print(f"[ATENÇÃO] {len(unmapped)} tema_ids sem mapeamento: {unmapped}")
        print("          Use --export-manual para gerar CSV de revisão.")
    else:
        print(f"[OK] Todos os {len(orphans)} orphans têm mapeamento proposto.")
        print("     Use --apply --dry-run para simular, ou --apply para executar.")


def apply_mapping(conn, dry_run=False):
    orphans = get_orphans(conn)
    if not orphans:
        print("[OK] Nenhum orphan para corrigir.")
        return

    applied = skipped = 0
    for tid in orphans:
        if tid not in MAPPING:
            print(f"  [SKIP] tema_id={tid}: sem mapeamento — use --export-manual")
            skipped += 1
            continue

        area, tema = MAPPING[tid]
        n = get_card_count(conn, tid)

        if dry_run:
            print(f"  [DRY]  tema_id={tid:>2}  n={n:>3}  INSERT ({area} / {tema})")
        else:
            conn.execute("""
                INSERT OR IGNORE INTO taxonomia_cronograma
                    (id, area, tema, questoes_realizadas, questoes_acertadas,
                     percentual_acertos, ultima_revisao)
                VALUES (?, ?, ?, 0, 0, 0, date('now'))
            """, (tid, area, tema))
            print(f"  [OK]   tema_id={tid:>2}  n={n:>3}  ({area} / {tema})")
            applied += 1

    if not dry_run:
        conn.commit()
        print(f"\nInseridos: {applied}  |  Pulados: {skipped}")
        # Verificar resultado
        remaining = get_orphans(conn)
        if remaining:
            print(f"[WARN] Ainda há {len(remaining)} orphans: {remaining}")
        else:
            print("[OK] taxonomia_cronograma: todos os tema_ids mapeados.")
    else:
        print(f"\n[DRY-RUN] {len(orphans) - skipped} INSERTs simulados — sem alteração no banco.")


def export_manual(conn, csv_path):
    orphans = get_orphans(conn)
    unmapped = [t for t in orphans if t not in MAPPING]

    if not unmapped:
        print("[OK] Sem orphans sem mapeamento — nada para exportar.")
        return

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['tema_id', 'n_flashcards', 'area_proposta', 'tema_proposto',
                         'titulo_1', 'titulo_2', 'titulo_3'])
        for tid in unmapped:
            n = get_card_count(conn, tid)
            titles = get_sample_titles(conn, tid, 3)
            titles += [''] * (3 - len(titles))
            writer.writerow([tid, n, '', ''] + titles)

    print(f"Exportado: {len(unmapped)} orphans → {csv_path}")


def main():
    p = argparse.ArgumentParser(description='MedHub — Fix Taxonomy Bridge')
    p.add_argument('--diagnose',      action='store_true',
                   help='Mostrar orphans com proposta de mapeamento')
    p.add_argument('--apply',         action='store_true',
                   help='Executar INSERTs para corrigir os orphans')
    p.add_argument('--dry-run',       action='store_true',
                   help='Simular sem alterar o banco (usar com --apply)')
    p.add_argument('--export-manual', metavar='CSV',
                   help='Exportar CSV dos orphans sem mapeamento automático')
    args = p.parse_args()

    if not any([args.diagnose, args.apply, args.export_manual]):
        p.print_help()
        return

    with sqlite3.connect(DB) as conn:
        if args.diagnose:
            diagnose(conn)
        if args.apply:
            apply_mapping(conn, dry_run=args.dry_run)
        if args.export_manual:
            export_manual(conn, args.export_manual)


if __name__ == '__main__':
    main()
