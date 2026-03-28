#!/usr/bin/env python3
"""
MedHub — Auditoria Permanente de Qualidade de Flashcards

Uso:
    python Tools/audit_flashcard_quality.py               # resumo de métricas
    python Tools/audit_flashcard_quality.py --examples 5  # exemplos dos piores cards
    python Tools/audit_flashcard_quality.py --export FILE # exporta IDs p/ passe LLM
    python Tools/audit_flashcard_quality.py --tipo armadilha
    python Tools/audit_flashcard_quality.py --signal alt_letter  # detalha 1 sinal

Critérios objetivos de baixa qualidade:
  CRÍTICO  alt_letter     — verso contém "(A)", "(B)" etc. (referência de gabarito)
  CRÍTICO  sobre_prefix   — frente começa com "Sobre X:" (pergunta artificial)
  CRÍTICO  habilidade_n   — frente contém "Habilidade N —" (artefato de pipeline)
  ALTO     arm_afirmacao  — armadilha como afirmação (sem ?)
  ALTO     badge_rd       — verso contém "RESPOSTA DIRETA" (badge vazando)
  ALTO     regra_vazia    — verso_regra_mestre nulo ou vazio
  ARQT.    structured_null — frente_pergunta NULL (usa fallback legacy)
  ARQT.    needs_qual     — needs_qualitative=1 (marcado para LLM)
"""

import sys, os, json, argparse, re
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.db import get_connection

SIGNALS = {
    'alt_letter': {
        'label':    'Alternativa de gabarito no verso (A)/(B)...',
        'severity': 'CRÍTICO',
        'sql_eff':  "({back} LIKE '%(A)%' OR {back} LIKE '%(B)%' OR {back} LIKE '%(C)%'"
                    " OR {back} LIKE '%(D)%' OR {back} LIKE '%(E)%')",
    },
    'sobre_prefix': {
        'label':    'Prefixo "Sobre X:" na pergunta (artificial)',
        'severity': 'CRÍTICO',
        'sql_eff':  "{front} LIKE '%Sobre %:%'",
    },
    'habilidade_n': {
        'label':    '"Habilidade N" na pergunta (artefato de pipeline)',
        'severity': 'CRÍTICO',
        'sql_eff':  "({front} LIKE '%Habilidade _ —%' OR {front} LIKE '%Habilidade _:%' OR {front} LIKE '%Habilidade %')",
    },
    'arm_afirmacao': {
        'label':    'Armadilha como afirmação (sem ?)',
        'severity': 'ALTO',
        'sql_raw':  "tipo = 'armadilha' AND {front} NOT LIKE '%?%'",
    },
    'badge_rd': {
        'label':    'Badge "RESPOSTA DIRETA" no verso',
        'severity': 'ALTO',
        'sql_eff':  "{back} LIKE '%RESPOSTA DIRETA%'",
    },
    'regra_vazia': {
        'label':    'Regra mestre vazia',
        'severity': 'ALTO',
        'sql_raw':  "verso_regra_mestre IS NULL OR TRIM(verso_regra_mestre) = ''",
    },
    'structured_null': {
        'label':    'Campos estruturados NULL (usa fallback legacy)',
        'severity': 'ARQT.',
        'sql_raw':  "frente_pergunta IS NULL OR TRIM(frente_pergunta) = ''",
    },
    'needs_qual': {
        'label':    'Marcado para revisão qualitativa (needs_qualitative=1)',
        'severity': 'INFO',
        'sql_raw':  "needs_qualitative = 1",
    },
}

# "effective" front/back: usa structured se populado, senão legacy
EFF_FRONT = "CASE WHEN frente_pergunta IS NOT NULL AND TRIM(frente_pergunta) != '' THEN frente_pergunta ELSE frente END"
EFF_BACK  = "CASE WHEN verso_resposta  IS NOT NULL AND TRIM(verso_resposta)  != '' THEN verso_resposta  ELSE verso  END"


def build_sql(signal_key, tipo_filter=None):
    sig = SIGNALS[signal_key]
    if 'sql_eff' in sig:
        condition = sig['sql_eff'].format(front=EFF_FRONT, back=EFF_BACK)
    else:
        condition = sig['sql_raw'].format(front=EFF_FRONT, back=EFF_BACK)

    where_parts = [condition]
    if tipo_filter:
        where_parts.append(f"tipo = '{tipo_filter}'")
    return "SELECT id FROM flashcards WHERE " + " AND ".join(f"({p})" for p in where_parts)


def count_signal(conn, signal_key, tipo_filter=None):
    sql = build_sql(signal_key, tipo_filter)
    return conn.execute(f"SELECT COUNT(*) FROM ({sql})").fetchone()[0]


def ids_signal(conn, signal_key, tipo_filter=None):
    return [r[0] for r in conn.execute(build_sql(signal_key, tipo_filter)).fetchall()]


def all_problematic_ids(conn, tipo_filter=None):
    """IDs com ao menos 1 sinal crítico ou alto (exclui INFO)."""
    exclude = {'needs_qual', 'regra_vazia', 'structured_null'}  # tracked separately
    parts = []
    for key, sig in SIGNALS.items():
        if key in exclude:
            continue
        if 'sql_eff' in sig:
            c = sig['sql_eff'].format(front=EFF_FRONT, back=EFF_BACK)
        else:
            c = sig['sql_raw'].format(front=EFF_FRONT, back=EFF_BACK)
        parts.append(f"({c})")

    where = " OR ".join(parts)
    tipo_clause = f" AND tipo = '{tipo_filter}'" if tipo_filter else ""
    rows = conn.execute(f"SELECT DISTINCT id FROM flashcards WHERE ({where}){tipo_clause}").fetchall()
    return [r[0] for r in rows]


def print_examples(conn, signal_key, n, tipo_filter=None):
    sql = build_sql(signal_key, tipo_filter)
    rows = conn.execute(f"""
        SELECT f.id, f.tipo, f.quality_source, f.needs_qualitative,
               {EFF_FRONT} as ef, {EFF_BACK} as eb
        FROM flashcards f
        WHERE f.id IN ({sql})
        LIMIT {n}
    """).fetchall()
    for r in rows:
        print(f"\n  id={r[0]}  tipo={r[1]}  source={r[2]}  nq={r[3]}")
        print(f"  FRENTE: {(r[4] or '')[:120]}")
        print(f"  VERSO:  {(r[5] or '')[:120]}")


def run(args):
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    tipo_filter = args.tipo if hasattr(args, 'tipo') and args.tipo != 'all' else None

    print()
    print("=" * 60)
    print("  MedHub — Auditoria de Qualidade de Flashcards")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(f"\nTotal de cards: {total}")
    if tipo_filter:
        filtered = conn.execute(f"SELECT COUNT(*) FROM flashcards WHERE tipo='{tipo_filter}'").fetchone()[0]
        print(f"Filtro tipo={tipo_filter}: {filtered} cards")
    print()

    # Distribuição por quality_source
    print("DISTRIBUIÇÃO POR QUALITY_SOURCE:")
    for r in conn.execute("SELECT quality_source, COUNT(*) FROM flashcards GROUP BY quality_source ORDER BY 2 DESC").fetchall():
        print(f"  {r[0] or 'NULL':<20}: {r[1]}")

    print()
    print("SINAIS DE BAIXA QUALIDADE (campos efetivos — o que a UI/CLI exibe):")
    counts = {}
    for key, sig in SIGNALS.items():
        n = count_signal(conn, key, tipo_filter)
        counts[key] = n
        pct = f"{n/total*100:.1f}%" if total > 0 else "0%"
        print(f"  [{sig['severity']:<6}] {sig['label']:<52}: {n:>4}  ({pct})")

    # Total problemáticos (union)
    bad_ids = all_problematic_ids(conn, tipo_filter)
    pct_bad = len(bad_ids) / total * 100 if total > 0 else 0
    print()
    print(f"TOTAL COM ≥1 SINAL CRÍTICO/ALTO:  {len(bad_ids)} / {total}  ({pct_bad:.1f}%)")
    print(f"Cards OK (sem sinais críticos):    {total - len(bad_ids)} / {total}")

    if args.examples > 0:
        signal_key = args.signal if hasattr(args, 'signal') and args.signal else 'alt_letter'
        n = count_signal(conn, signal_key, tipo_filter)
        if n > 0:
            print(f"\nEXEMPLOS — sinal '{signal_key}' (max {args.examples}):")
            print_examples(conn, signal_key, args.examples, tipo_filter)
        else:
            print(f"\nNenhum card com sinal '{signal_key}'.")

    if args.export:
        # --only-needs-qual: exportar todos os needs_qualitative=1 (não só os objetivamente ruins)
        if hasattr(args, 'only_needs_qual') and args.only_needs_qual:
            export_ids = [r[0] for r in conn.execute(
                "SELECT id FROM flashcards WHERE needs_qualitative = 1 ORDER BY id"
            ).fetchall()]
            print(f"Modo --only-needs-qual: {len(export_ids)} cards com needs_qualitative=1")
        else:
            export_ids = bad_ids

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_cards': total,
            'problematic_count': len(export_ids),
            'problematic_ids': export_ids,
            'signal_counts': counts,
            'cards': [],
        }
        # Exportar dados completos dos cards para passe LLM
        for card_id in export_ids:
            row = conn.execute("""
                SELECT f.id, f.tipo, f.quality_source, f.needs_qualitative,
                       f.frente, f.verso, f.frente_contexto, f.frente_pergunta,
                       f.verso_resposta, f.verso_regra_mestre, f.verso_armadilha,
                       q.titulo, q.enunciado, q.alternativa_correta,
                       q.habilidades_sequenciais, q.o_que_faltou,
                       q.explicacao_correta, q.armadilha_prova,
                       COALESCE(t.area,'') as area, COALESCE(t.tema,'') as tema
                FROM flashcards f
                LEFT JOIN questoes_erros q ON f.questao_id = q.id
                LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
                WHERE f.id = ?
            """, (card_id,)).fetchone()
            if row:
                cols = ['id','tipo','quality_source','needs_qualitative',
                        'frente','verso','frente_contexto','frente_pergunta',
                        'verso_resposta','verso_regra_mestre','verso_armadilha',
                        'titulo','enunciado','alternativa_correta',
                        'habilidades_sequenciais','o_que_faltou',
                        'explicacao_correta','armadilha_prova','area','tema']
                export_data['cards'].append(dict(zip(cols, row)))

        with open(args.export, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"\nExportado: {len(export_ids)} cards -> {args.export}")

    print()
    conn.close()


def main():
    p = argparse.ArgumentParser(description="MedHub — Auditoria de Qualidade de Flashcards")
    p.add_argument('--examples', type=int, default=0,
                   help='Número de exemplos a mostrar por sinal')
    p.add_argument('--signal', default='alt_letter',
                   choices=list(SIGNALS.keys()),
                   help='Sinal a detalhar nos exemplos (default: alt_letter)')
    p.add_argument('--export', metavar='FILE',
                   help='Exportar cards problemáticos para JSON (input para LLM)')
    p.add_argument('--tipo', default='all', choices=['all', 'elo_quebrado', 'armadilha'],
                   help='Filtrar por tipo de card')
    p.add_argument('--only-needs-qual', action='store_true', dest='only_needs_qual',
                   help='Exportar apenas cards com needs_qualitative=1 (ignorar filtro de sinais)')
    args = p.parse_args()
    run(args)


if __name__ == '__main__':
    main()
