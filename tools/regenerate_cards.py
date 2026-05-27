import sqlite3, re, json, argparse
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'ipub.db'

# --- Validacao heuristica ---
BAD_PATTERNS = [
    r'^em \w+: qual o valor limiar',
    r'^em \w+: qual a sequencia',
    r'^sobre \w+:',
    r'^qual a conduta correta em:',
    r'^qual a abordagem correta em:',  # fallback genérico demais
    r'n/a',
]

NA_VALUES = {'n/a', 'n/a.', 'ver explicacao', 'ver explicacão', 'ver explicação', '-', ''}

def clean(s):
    """Retorna string vazia se s for None, vazio, ou N/A."""
    if not s: return ''
    s = s.strip()
    return '' if s.lower() in NA_VALUES else s


def strip_letter_ref(text: str) -> str:
    """Remove referência de gabarito tipo '(B)', '(C)' do final do texto.

    Ex: 'Adenosina (B)' -> 'Adenosina'
        'Manobra Vagal (C).' -> 'Manobra Vagal'
        'conduta expectante (A)' -> 'conduta expectante'
    """
    if not text:
        return text
    cleaned = re.sub(r'\s*\([A-Ea-e]\)\s*\.?\s*$', '', text.strip())
    return cleaned.strip()

def is_low_quality(pergunta: str) -> bool:
    p = pergunta.lower().strip()
    if len(p) < 15: return True
    for pat in BAD_PATTERNS:
        if re.search(pat, p): return True
    return False

def first_n(text, limit):
    if not text or text.strip().lower() in NA_VALUES: return ''
    sentences = re.split(r'(?<=[.!?])\s', text.strip())
    result = ''
    for s in sentences:
        if len(result) + len(s) + 1 <= limit:
            result += (' ' if result else '') + s
        else:
            break
    return result or text[:limit]

def heuristic_fields(q):
    habs   = clean(q['habilidades_sequenciais'] or '')
    faltou = clean(q['o_que_faltou'] or '').rstrip('.')
    # Pega o ultimo elo da cadeia de habilidades
    last_h = habs.split('\u2192')[-1].strip().rstrip('.') if '\u2192' in habs else ''
    if last_h.lower() in NA_VALUES: last_h = ''
    perg   = last_h or faltou or f"Qual a conduta correta em: {q['titulo']}?"
    if not perg.endswith('?'): perg += '?'

    # Resposta: preferir alternativa_correta stripada de letra de gabarito
    resp_raw = strip_letter_ref(first_n(q['alternativa_correta'], 200))
    if len(resp_raw) < 8:
        # Texto muito curto (ex: só a letra 'D') — usar explicacao como resposta
        resp_raw = first_n(q['explicacao_correta'], 200)
        if len(resp_raw) < 8:
            resp_raw = ''  # Sem dados suficientes — UI usará fallback legado

    flagged = is_low_quality(perg) or len(resp_raw) == 0
    return {
        'frente_contexto':    first_n(q['enunciado'], 150),
        'frente_pergunta':    perg,
        'verso_resposta':     resp_raw,
        'verso_regra_mestre': first_n(q['explicacao_correta'], 250),
        'verso_armadilha':    first_n(q['armadilha_prova'], 200),
        'quality_source':     'heuristic_flagged' if flagged else 'heuristic',
        'needs_qualitative':  1 if flagged else 0,
    }

def fields_changed(old, new):
    keys = ['frente_pergunta', 'verso_resposta', 'verso_regra_mestre', 'verso_armadilha']
    return any((old.get(k) or '') != new.get(k, '') for k in keys)

def apply_update(conn, card_id, old_fields, new_fields, dry_run):
    changed = fields_changed(old_fields, new_fields)
    new_version = (old_fields.get('card_version') or 1) + (1 if changed else 0)
    if dry_run:
        def safe(s): return (s or '')[:80].encode('ascii', 'replace').decode('ascii')
        print(f"\n[DRY] card {card_id} changed={changed}")
        print(f"  perg:  {safe(new_fields['frente_pergunta'])}")
        print(f"  resp:  {safe(new_fields['verso_resposta'])}")
        print(f"  flag:  {new_fields['needs_qualitative']}")
        return
    conn.execute("""
        UPDATE flashcards SET
            frente_contexto=?, frente_pergunta=?, verso_resposta=?,
            verso_regra_mestre=?, verso_armadilha=?,
            quality_source=?, card_version=?, needs_qualitative=?
        WHERE id=?
    """, (new_fields['frente_contexto'], new_fields['frente_pergunta'],
          new_fields['verso_resposta'],  new_fields['verso_regra_mestre'],
          new_fields['verso_armadilha'], new_fields['quality_source'],
          new_version, new_fields['needs_qualitative'], card_id))

def load_cards(conn, only_ids=None, tipo_filter=None):
    conds = ["f.questao_id IS NOT NULL"]
    if only_ids:    conds.append(f"f.id IN ({','.join(map(str, only_ids))})")
    if tipo_filter: conds.append(f"f.tipo = '{tipo_filter}'")
    where = "WHERE " + " AND ".join(conds)
    return conn.execute(f"""
        SELECT f.id, f.tipo, f.frente, f.verso,
               COALESCE(f.card_version, 1) as card_version,
               f.quality_source,
               q.titulo, q.enunciado, q.alternativa_correta,
               q.habilidades_sequenciais, q.o_que_faltou,
               q.explicacao_correta, q.armadilha_prova,
               t.tema, t.area
        FROM flashcards f
        JOIN questoes_erros q ON f.questao_id = q.id
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        {where}
    """).fetchall()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['heuristic', 'qualitative'], default='heuristic')
    p.add_argument('--tipo', choices=['elo_quebrado', 'armadilha', 'all'], default='elo_quebrado',
                   help='elo_quebrado (padrao), armadilha (template especifico), all')
    p.add_argument('--only-ids', nargs='+', type=int)
    p.add_argument('--dry-run',  action='store_true')
    p.add_argument('--export',   metavar='FILE', help='Exportar contextos JSON para Claude Code')
    p.add_argument('--apply',    metavar='FILE', help='Aplicar JSON gerado pelo Claude Code')
    args = p.parse_args()

    col_names = ['id', 'tipo', 'frente', 'verso', 'card_version', 'quality_source',
                 'titulo', 'enunciado', 'alternativa_correta', 'habilidades_sequenciais',
                 'o_que_faltou', 'explicacao_correta', 'armadilha_prova', 'tema', 'area']

    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row

        if args.apply:
            data = json.loads(Path(args.apply).read_text(encoding='utf-8'))
            retired = applied = 0
            for item in data:
                cid = item.pop('id')
                # needs_qualitative=2 no JSON: aposentar card (excluir da fila FSRS)
                if item.get('needs_qualitative') == 2:
                    if not args.dry_run:
                        conn.execute(
                            "UPDATE flashcards SET needs_qualitative=2 WHERE id=?", (cid,)
                        )
                        retired += 1
                    else:
                        print(f"[DRY] card {cid}: APOSENTADO (needs_qualitative=2)")
                    continue
                row = conn.execute("SELECT * FROM flashcards WHERE id=?", (cid,)).fetchone()
                old = dict(row) if row else {}
                item['quality_source'] = 'qualitative'
                item['needs_qualitative'] = 0
                apply_update(conn, cid, old, item, args.dry_run)
                applied += 1
            if not args.dry_run: conn.commit()
            print(f"Aplicados: {applied} cards  |  Aposentados: {retired}")
            return

        tipo_filter = None if args.tipo == 'all' else args.tipo
        rows = load_cards(conn, args.only_ids, tipo_filter)
        cards = [dict(zip(col_names, r)) for r in rows]

        if args.export:
            Path(args.export).write_text(
                json.dumps(cards, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            print(f"Exportados: {len(cards)} cards -> {args.export}")
            return

        # Heuristico
        updated = flagged = 0
        for c in cards:
            old = dict(c)
            # Cards tipo='armadilha': template especifico
            if c['tipo'] == 'armadilha':
                new_fields = {
                    'frente_contexto':    first_n(c['enunciado'], 100),
                    'frente_pergunta':    f"Qual o distrator do examinador em '{c['titulo']}'?",
                    'verso_resposta':     first_n(c['armadilha_prova'], 200),
                    'verso_regra_mestre': first_n(c['explicacao_correta'], 200),
                    'verso_armadilha':    '',  # não redundante: regra mestre já cobre
                    'quality_source':     'heuristic',
                    'needs_qualitative':  1,  # armadilha sempre flags para LLM
                }
            else:
                new_fields = heuristic_fields(c)

            apply_update(conn, c['id'], old, new_fields, args.dry_run)
            if not args.dry_run:
                updated += 1
                if new_fields['needs_qualitative']: flagged += 1

        if not args.dry_run:
            conn.commit()
            print(f"Regenerados: {updated} | Marcados para revisao qualitativa: {flagged}")
            print("Cards flagged disponiveis via: SELECT id FROM flashcards WHERE needs_qualitative=1")

if __name__ == '__main__':
    main()
