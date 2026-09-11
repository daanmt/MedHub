#!/usr/bin/env python3
"""
MedHub — Auditoria Permanente de Qualidade de Flashcards

Uso:
    python tools/audit_flashcard_quality.py               # resumo de métricas
    python tools/audit_flashcard_quality.py --examples 5  # exemplos dos piores cards
    python tools/audit_flashcard_quality.py --export FILE # exporta IDs p/ passe LLM
    python tools/audit_flashcard_quality.py --tipo armadilha
    python tools/audit_flashcard_quality.py --signal alt_letter  # detalha 1 sinal

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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.utils.db import get_connection, ativo_where
import card_checks  # detectores cross-field (part-5) — mesma biblioteca do write-gate

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
    'orfao_sem_andaime': {
        'label':    'Órfão sem âncora (questao_id NULL e não-andaime)',
        'severity': 'ALTO',
        'sql_raw':  "questao_id IS NULL AND tipo NOT IN ('base','mecanismo','nuance','andaime')",
    },
}

# "effective" front/back: schema v5 (frente/verso removidos em medhub-cleanup)
EFF_FRONT = "COALESCE(NULLIF(TRIM(frente_pergunta), ''), '[sem pergunta]')"
EFF_BACK  = "COALESCE(NULLIF(TRIM(verso_resposta),  ''), '[sem resposta]')"

# ⚰️ HEURÍSTICA F7 -- REVOGADA em 11/09/2026 (s177, item 1.5 da fila de engenharia).
# Viveu aqui de 05/07 a 11/09/2026 como `check_discriminacao_lexicon` + léxico
# `tools/data/competidores_categorias.json` (ambos deletados no mesmo commit).
# Nasceu WARN experimental com gate anti-decorativo declarado ("3 execuções sem
# sinal acionável -> remover") e a medição única que o fechou foi esta:
#   alcance  -- o léxico tocava a RESPOSTA de 15 cards e a ARMADILHA de 12, dos
#               1611 do banco; só 8 cards eram ELEGÍVEIS (léxico casa nos dois
#               lados). Campo de visão = 0,5% da base, num único eixo clínico
#               (cardiopatia congênita cianótica hiper x hipofluxo).
#   precisão -- 2 disparos, 1 verdadeiro: #95 (o caso-semente: resposta HCE,
#               armadilha só nomeia Fallot e não exclui a TGA) e #913 (FALSO --
#               a armadilha nomeia a categoria oposta porque o eixo daquele card
#               é IDADE, não fluxo; o competidor citado é o correto). 50% sobre
#               n=2, com o único verdadeiro já nomeado no ledger desde 07/2026.
#   curadoria -- o léxico dependia de curadoria contínua do agente-player e
#               ficou 68 dias com os 2 termos-semente. Nenhum teste o importava.
# Por que morre em vez de virar BLOCK: a classe do F7 ("a armadilha se defende do
# competidor ERRADO") é SEMÂNTICA -- depende de qual eixo o card discrimina. Um
# léxico só sabe proxiá-la por oposição de categoria, e essa proxy errou metade
# das vezes. Promover a BLOCK travaria card correto. Pela verification-stack
# (AGENTE.md §10.8) o eixo fica DECLARADO como não-verificável por gate, nunca
# convertido em métrica para o painel ficar verde.
# Onde a classe continua viva: os dois achados reais do F7 viraram estado na fila
# de reforja (`python tools/reforja.py --fila`: #95 discriminacao_incompleta,
# #120 diagnostico_raro_forcado, ambos `[sem predicado]` por declaração), e a
# régua de autoria segue em `.claude/commands/estilo-flashcard.md`.
# Guarda contra ressurreição silenciosa: `tools/test_heuristica_f7_morta.py`.


def build_sql(signal_key, tipo_filter=None):
    sig = SIGNALS[signal_key]
    if 'sql_eff' in sig:
        condition = sig['sql_eff'].format(front=EFF_FRONT, back=EFF_BACK)
    else:
        condition = sig['sql_raw'].format(front=EFF_FRONT, back=EFF_BACK)

    # part-5: os sinais auditam os ATIVOS (definição canônica db.ATIVO_WHERE) —
    # antes este auditor era o único sem filtro (3ª definição divergente).
    where_parts = [condition, ativo_where()]
    if tipo_filter:
        where_parts.append(f"tipo = '{tipo_filter}'")
    return "SELECT id FROM flashcards WHERE " + " AND ".join(f"({p})" for p in where_parts)


def count_signal(conn, signal_key, tipo_filter=None):
    sql = build_sql(signal_key, tipo_filter)
    return conn.execute(f"SELECT COUNT(*) FROM ({sql})").fetchone()[0]


def ids_signal(conn, signal_key, tipo_filter=None):
    return [r[0] for r in conn.execute(build_sql(signal_key, tipo_filter)).fetchall()]


def all_problematic_ids(conn, tipo_filter=None):
    """IDs de cards ATIVOS com ao menos 1 sinal — TODOS os sinais contam.

    part-5: o exclude-set {needs_qual, regra_vazia, structured_null} foi
    REMOVIDO — a exclusão escondia do agregado exatamente os sinais que teriam
    pego o incidente dos 68 (§6.5.2 da pré-auditoria)."""
    parts = []
    for key, sig in SIGNALS.items():
        if 'sql_eff' in sig:
            c = sig['sql_eff'].format(front=EFF_FRONT, back=EFF_BACK)
        else:
            c = sig['sql_raw'].format(front=EFF_FRONT, back=EFF_BACK)
        parts.append(f"({c})")

    where = " OR ".join(parts)
    tipo_clause = f" AND tipo = '{tipo_filter}'" if tipo_filter else ""
    rows = conn.execute(f"SELECT DISTINCT id FROM flashcards WHERE ({where}) "
                        f"AND ({ativo_where()}){tipo_clause}").fetchall()
    return [r[0] for r in rows]


def check_cross_field(conn):
    """part-5: predicados RELACIONAIS da biblioteca card_checks sobre os ativos.

    Retorna (por_tag, distrator): por_tag = {tag: [card_ids]}; distrator =
    [questao_ids] com alternativa_marcada perdida nos cards derivados.
    WARN, nunca afeta exit code (warn-first)."""
    rows = conn.execute(f"""
        SELECT f.id, f.questao_id, f.frente_contexto, f.frente_pergunta,
               f.verso_resposta, f.verso_regra_mestre, f.verso_armadilha,
               q.titulo, q.alternativa_marcada, t.tema
        FROM flashcards f
        LEFT JOIN questoes_erros q ON q.id = f.questao_id
        LEFT JOIN taxonomia_cronograma t ON t.id = f.tema_id
        WHERE {ativo_where('f.')}
    """).fetchall()
    por_tag = {}
    por_questao = {}
    for (cid, qid, fc, fp, vr, vrm, va, titulo, marcada, tema) in rows:
        card = {"frente_contexto": fc, "frente_pergunta": fp, "verso_resposta": vr,
                "verso_regra_mestre": vrm, "verso_armadilha": va}
        ctx = {"titulo": titulo, "tema": tema}
        for achado in (card_checks.checar_pergunta_template(card, ctx),
                       card_checks.checar_resposta_embutida(card, ctx),
                       card_checks.checar_multi_parte(card),
                       card_checks.checar_negativo_orfao(card),
                       card_checks.checar_contexto_artefato(card)):
            if achado:
                tag = achado.split(" ")[0].rstrip(",")
                por_tag.setdefault(tag, []).append(cid)
        if qid is not None:
            por_questao.setdefault(qid, {"marcada": marcada, "cards": []})
            por_questao[qid]["cards"].append(card)
    distrator = []
    for qid, dados in por_questao.items():
        if card_checks.checar_distrator({"alternativa_marcada": dados["marcada"]},
                                        dados["cards"]):
            distrator.append(qid)
    return por_tag, sorted(distrator)


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
    ativos_n = conn.execute(
        f"SELECT COUNT(*) FROM flashcards WHERE {ativo_where()}").fetchone()[0]
    print(f"\nTotal de cards: {total}  (ativos: {ativos_n} — definição canônica; "
          f"os sinais auditam os ativos)")
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
        pct = f"{n/ativos_n*100:.1f}%" if ativos_n > 0 else "0%"
        print(f"  [{sig['severity']:<6}] {sig['label']:<52}: {n:>4}  ({pct})")

    # Total problemáticos (union) — part-5: TODOS os sinais contam no agregado
    bad_ids = all_problematic_ids(conn, tipo_filter)
    pct_bad = len(bad_ids) / ativos_n * 100 if ativos_n > 0 else 0
    print()
    print(f"TOTAL COM ≥1 SINAL (todos os sinais; ativos):  {len(bad_ids)} / {ativos_n}  ({pct_bad:.1f}%)")
    print(f"Cards ativos OK (sem nenhum sinal):            {ativos_n - len(bad_ids)} / {ativos_n}")

    # part-5: detectores cross-field (relacionais) — WARN, não bloqueia
    cross_tags, cross_distrator = check_cross_field(conn)
    print()
    print("DETECTORES CROSS-FIELD (card_checks — mesmos predicados do write-gate; WARN):")
    if not cross_tags and not cross_distrator:
        print("  nenhum card ativo sinalizado")
    for tag in sorted(cross_tags):
        ids = cross_tags[tag]
        print(f"  [WARN] {tag:<22}: {len(ids):>4} card(s)  (ex.: {ids[:8]})")
    if cross_distrator:
        print(f"  [WARN] distrator-perdido      : {len(cross_distrator):>4} questão(ões) — "
              f"alternativa_marcada não aparece nos cards derivados (ex.: {cross_distrator[:8]})")

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
            # part-5: sinais relacionais no export, com tag própria
            'cross_field': {tag: ids for tag, ids in cross_tags.items()},
            'cross_field_distrator_questoes': cross_distrator,
            'cards': [],
        }
        # Exportar dados completos dos cards para passe LLM
        for card_id in export_ids:
            row = conn.execute("""
                SELECT f.id, f.tipo, f.quality_source, f.needs_qualitative,
                       f.frente_contexto, f.frente_pergunta,
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
                        'frente_contexto','frente_pergunta',
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


MIN_REVISOES_PARA_LER = 300   # abaixo disto o contador DECLARA que nao informa


def contar_gate_miss(conn):
    """F81/B1 (s176): quantas vezes um card que os predicados de FRENTE pegariam foi
    efetivamente SERVIDO ao aluno -- e por que bucket ele foi servido.

    🔴 DENOMINADORES SEPARADOS. `fsrs_revlog.reason_servido` nasceu no F76 (s174): revisao
    anterior a isso tem o campo NULL. Somar NULL como se fosse uma classe faria o painel
    inventar uma categoria maior que todas as outras juntas. A janela e explicitamente
    `reason_servido IS NOT NULL`, e o que ficou de fora e reportado COMO fora, com contagem
    visivel.

    🔴 NASCE DIZENDO QUE NAO SABE. Com poucas revisoes dentro da janela, a distribuicao por
    classe e ruido. Abaixo de MIN_REVISOES_PARA_LER o contador imprime os numeros crus e
    declara que ainda nao ha leitura -- em vez de nascer verde e ser citado como se informasse.

    Retorna dict (puro no formato, nao imprime): a impressao e do chamador.
    """
    import card_checks as _cc
    predicados = (("contexto_redundante", _cc.checar_contexto_redundante),
                  ("pergunta_generica", _cc.checar_pergunta_generica_com_contexto),
                  ("contrafactual_mal_formado", _cc.checar_contrafactual_mal_formado))

    # Marca sobre o baralho INTEIRO, aposentados inclusive: a pergunta e historica
    # ("um card defeituoso chegou ao aluno?"), e um card aposentado hoje pode ter
    # sido servido ontem. O recorte ATIVO e reportado a parte para nao divergir em
    # silencio da populacao que a spec declara (12/4/1 = 17 ativos).
    marcados, marcados_ativos = {}, 0
    for cid, ctx, perg, nq in conn.execute(
            "SELECT id, frente_contexto, frente_pergunta, COALESCE(needs_qualitative,0) "
            "FROM flashcards "
            "WHERE COALESCE(frente_contexto,'') <> '' AND COALESCE(frente_pergunta,'') <> ''"):
        card = {"frente_contexto": ctx, "frente_pergunta": perg}
        classes = [nome for nome, fn in predicados if fn(card)]
        if classes:
            marcados[cid] = classes
            if nq < 2:
                marcados_ativos += 1

    dentro = conn.execute(
        "SELECT COUNT(*) FROM fsrs_revlog WHERE reason_servido IS NOT NULL").fetchone()[0]
    fora = conn.execute(
        "SELECT COUNT(*) FROM fsrs_revlog WHERE reason_servido IS NULL").fetchone()[0]

    por_classe = {}
    if marcados:
        marcas = ",".join(str(i) for i in marcados)
        for razao, cid, n in conn.execute(
                f"SELECT reason_servido, card_id, COUNT(*) FROM fsrs_revlog "
                f"WHERE reason_servido IS NOT NULL AND card_id IN ({marcas}) "
                f"GROUP BY reason_servido, card_id"):
            for classe in marcados[cid]:
                por_classe.setdefault(classe, {}).setdefault(razao, 0)
                por_classe[classe][razao] += n

    return {"cards_marcados": len(marcados), "cards_marcados_ativos": marcados_ativos,
            "revisoes_na_janela": dentro,
            "revisoes_fora_da_janela": fora,
            "por_classe": por_classe,
            "informa": dentro >= MIN_REVISOES_PARA_LER,
            "minimo_para_informar": MIN_REVISOES_PARA_LER}


def print_gate_miss(conn):
    r = contar_gate_miss(conn)
    print()
    print("=" * 60)
    print("  Gate-miss da FRENTE (F81/B1) — defeito que chegou ao aluno")
    print("=" * 60)
    print(f"  cards marcados por algum predicado : {r['cards_marcados']}  (no baralho ativo: {r['cards_marcados_ativos']})")
    print(f"  JANELA (reason_servido preenchido) : {r['revisoes_na_janela']} revisoes")
    print(f"  FORA da janela (anterior ao F76)   : {r['revisoes_fora_da_janela']} revisoes "
          f"— nao entram em nenhuma classe, por contrato")
    if not r["informa"]:
        print()
        print(f"  [DECLARADO] A janela tem {r['revisoes_na_janela']} revisoes; o contador so "
              f"passa a informar com >= {r['minimo_para_informar']}.")
        print("  Os numeros abaixo sao crus e NAO devem ser lidos como distribuicao.")
    print()
    if not r["por_classe"]:
        print("  (nenhuma revisao dentro da janela tocou um card marcado)")
    for classe, razoes in sorted(r["por_classe"].items()):
        total = sum(razoes.values())
        detalhe = " · ".join(f"{k}={v}" for k, v in sorted(razoes.items()))
        print(f"  {classe:28s} {total:4d}  ({detalhe})")
    print()


def main():
    p = argparse.ArgumentParser(description="MedHub — Auditoria de Qualidade de Flashcards")
    p.add_argument('--gate-miss', action='store_true', dest='gate_miss',
                   help='Contador de gate-miss da FRENTE (F81/B1), com janela declarada')
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
    if args.gate_miss:
        conn = get_connection()
        try:
            print_gate_miss(conn)
        finally:
            conn.close()
        return
    run(args)


if __name__ == '__main__':
    main()
