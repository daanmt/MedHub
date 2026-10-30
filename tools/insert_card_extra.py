"""insert_card_extra.py — insere card adicional ancorado no erro de ORIGEM e/ou na resposta EMED.

Card de questao CERTA (consolidacao, elo `incerteza`) ancora na RESPOSTA (`emed`), nunca em
erro vizinho (P6, Fase 0 Lote 1 part-3). Modelo: `questao_id` = a ORIGEM do card (o erro de
onde nasceu, 0..1; o card de atomizacao da curadoria herda o do original); `emed` = as ancoras
de consolidacao (0..n) em `emed_respostas(lista, num)`, gravadas em `emed_card_ancora` pelo
writer unico `db.emed_ancorar_card`. Todo card traz AO MENOS UMA ancora (`questao_id`, `emed`
ou as duas) e `tema_id`. Todas as ancoras sao validadas, so em leitura, ANTES de qualquer
escrita (tambem no dry-run): ancora invalida ou card sem ancora = exit 1, NADA gravado.
Idempotente: mesma `frente_pergunta` no mesmo `questao_id` ou ja ancorada no mesmo
`(lista, num)` vira [SKIP]. --dry-run e o default; o DDL so roda sob --apply.

Evidencia (s236, evidence-bank; contrato evidence-governance v1.5 §7): com `evidencias.db`
pareado, card sem `evidencias: ["ev-..."]` ativas entra EM QUARENTENA (fora do FSRS) e as
afirmacoes dele (`afirmacoes`; sem elas, a regra-mestre) vao a fila do banco antes do commit --
nunca recusado por falta de evidencia; recusa so por forma (`app/utils/evidencias_ponte.py`).

JSON de entrada (--from): lista de
  {tema_id, questao_id?, emed? ("t40_5" ou ["t40_5", "t40_17"]), tipo?, frente_contexto?,
   frente_pergunta, verso_resposta, verso_regra_mestre?, verso_armadilha?, origem_card?}

Re-ancoragem (--reancorar FILE), para card ancorado errado: JSON
  [{card_id, tema_id, emed: [...], questao_id? (default null)}]
Dry-run default imprime `questao_id <velho> -> <novo>`, `tema_id <velho> -> <novo>` e as
ancoras a criar. `--apply` exige `--expect N` (N = cards que mudam; diverge = exit 2) e o
backup FIXADO do inicio do ato (`backup_db.fixar_antes_do_ato`; sem ele, recusa). Tudo numa
transacao; card ja no estado pedido conta como `iguais` (re-execucao = 0 mudancas).

Uso:
    python tools/insert_card_extra.py --from cards.json            # dry-run
    python tools/insert_card_extra.py --from cards.json --apply
    python tools/insert_card_extra.py --reancorar plano.json       # dry-run
    python tools/insert_card_extra.py --reancorar plano.json --apply --expect 6
"""
import sqlite3, json, argparse, os, sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 🔴 RAIZ do repo, nao `tools/` (F118, s187). O 1.9(a) moveu `card_checks` para
# `app/utils/`, e ancorar no proprio diretorio deixou este CLI inalcancavel como
# CLI -- a suite nao via porque o pytest insere a raiz antes de importar.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils import card_checks  # gate de qualidade — biblioteca PURA em app/ (1.9a)
from app.utils import db  # P6: emed_chave / emed_validar_ancora / emed_ancorar_card (writer unico)
from app.utils import evidencias_ponte  # s236: quarentena + fila do evidence-bank

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')


def _chaves_emed(valor):
    """`"t40_5"` ou lista -> [(lista, num), ...] sem repeticao (ValueError se a chave e torta)."""
    if valor is None or valor == "" or valor == []:
        return []
    itens = [valor] if isinstance(valor, str) else list(valor)
    out = []
    for item in itens:
        chave = db.emed_chave(item)
        if chave not in out:
            out.append(chave)
    return out


def _ancoras_atuais(conn, card_id):
    """Ancoras emed ja gravadas do card; sem a tabela (banco antes do DDL) = nenhuma."""
    try:
        return {(r[0], r[1]) for r in conn.execute(
            "SELECT lista, num FROM emed_card_ancora WHERE card_id = ?", (card_id,))}
    except sqlite3.OperationalError:
        return set()


def _existe(conn, tabela, ident):
    return conn.execute(f"SELECT 1 FROM {tabela} WHERE id = ?", (ident,)).fetchone() is not None


def _validar_ancoras(conn, qid, chaves, rotulo):
    """Erros (lista de str) das ancoras de um card -- so leitura. Zero ancoras e erro."""
    erros = []
    if qid is None and not chaves:
        erros.append(f"{rotulo}: sem ancora (questao_id do erro de origem ou emed da resposta)")
    if qid is not None and not _existe(conn, "questoes_erros", qid):
        erros.append(f"{rotulo}: questao_id {qid} nao existe em questoes_erros")
    for lista, num in chaves:
        try:
            db.emed_validar_ancora(conn, lista, num)
        except ValueError as e:
            erros.append(f"{rotulo}: {e}")
    return erros


def _fixar_antes(ato):
    """F137 parte 2: o ponto de retorno FIXADO do proprio inicio do ato (`backup_db`). Levanta
    quando nao ha -- quem chama RECUSA e nada e gravado (padrao de `emed_banco._fixar_antes`)."""
    _tools = os.path.dirname(os.path.abspath(__file__))
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    import backup_db
    return backup_db.fixar_antes_do_ato(ato, db=DB_PATH)


def _conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # part-4: FKs impostas
    return conn


def inserir(args):
    dry = not args.apply
    cards = json.load(open(args.src, encoding='utf-8'))

    # Gate de qualidade (part-4): valida o lote ANTES de qualquer escrita.
    erros_gate, avisos_gate = [], []
    for i, card in enumerate(cards):
        res = card_checks.validar_card(card)
        erros_gate += [f"card {i}: {e}" for e in res["erros"]]
        avisos_gate += [f"card {i}: {a}" for a in res["avisos"]]
    for a in avisos_gate:
        print(f"  [AVISO-CARD] {a}")
    if erros_gate:
        for e in erros_gate:
            print(f"  [ERRO] {e}")
        print("\n[ERRO] gate de qualidade reprovou o lote (regua "
              ".claude/commands/estilo-flashcard.md). NADA gravado.")
        sys.exit(1)

    conn = _conectar()
    cur = conn.cursor()

    # P6: TODAS as ancoras validadas, so em leitura, antes de qualquer escrita (tambem no dry-run).
    erros, plano = [], []
    for i, c in enumerate(cards):
        rotulo = f"card {i}"
        qid, tid = c.get('questao_id'), c.get('tema_id')
        try:
            chaves = _chaves_emed(c.get('emed'))
        except ValueError as e:
            erros.append(f"{rotulo}: {e}")
            continue
        if tid is None:
            erros.append(f"{rotulo}: sem tema_id")
        erros += _validar_ancoras(conn, qid, chaves, rotulo)
        plano.append((c, qid, tid, chaves))
    if erros:
        for e in erros:
            print(f"  [ERRO] {e}")
        print("\n[ERRO] ancora invalida no lote (card de questao certa ancora na resposta, "
              "`emed`, nunca em erro vizinho). NADA gravado.")
        conn.close()
        sys.exit(1)

    ins = skip = 0
    pendentes = []  # s236: (card_id, card, area, tema, tema_id) -> evidencias_ponte.aplicar
    if not dry and any(chaves for _, _, _, chaves in plano):
        db._ensure_emed_tables(conn)  # DDL idempotente, so sob --apply
    try:
        for c, qid, tid, chaves in plano:
            fp = c['frente_pergunta']
            ex = None
            if qid is not None:
                ex = cur.execute("SELECT id FROM flashcards WHERE questao_id=? AND frente_pergunta=?",
                                 (qid, fp)).fetchone()
            for lista, num in chaves:
                if ex:
                    break
                try:
                    ex = cur.execute(
                        "SELECT f.id FROM flashcards f JOIN emed_card_ancora a ON a.card_id = f.id "
                        "WHERE f.frente_pergunta = ? AND a.lista = ? AND a.num = ?",
                        (fp, lista, num)).fetchone()
                except sqlite3.OperationalError:
                    ex = None
            ancoras = ", ".join(f"{l}_{n}" for l, n in chaves) or "-"
            if ex:
                print(f"  [SKIP] já existe card {ex[0]} (questao {qid}, emed {ancoras})")
                skip += 1
                continue
            print(f"  [INSERT] questao {qid} emed {ancoras} tema {tid} "
                  f"(origem #{c.get('origem_card')}): {fp[:60]}")
            cid = 0  # dry-run: sem id; a fila do evidence-bank valida a forma com `card:0`
            if not dry:
                cur.execute(
                    "INSERT INTO flashcards (questao_id, tema_id, tipo, frente_contexto, frente_pergunta, "
                    "verso_resposta, verso_regra_mestre, verso_armadilha, quality_source, needs_qualitative, card_version) "
                    "VALUES (?,?,?,?,?,?,?,?, 'qualitative', 0, 1)",
                    (qid, tid, c.get('tipo', 'conteudo'), c.get('frente_contexto', ''), fp,
                     c['verso_resposta'], c.get('verso_regra_mestre', ''), c.get('verso_armadilha', '')))
                cid = cur.lastrowid
                cur.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, ?)", (cid, datetime.now()))
                for lista, num in chaves:
                    db.emed_ancorar_card(conn, lista, num, cid)
            area_tema = cur.execute("SELECT area, tema FROM taxonomia_cronograma WHERE id = ?",
                                    (tid,)).fetchone() or (None, None)
            pendentes.append((cid, c, area_tema[0], area_tema[1], tid))
            ins += 1
        # s236: evidência ANTES do commit -- ponte `ativa`, ou quarentena + fila do evidence-bank.
        ev = evidencias_ponte.aplicar(None if dry else conn, pendentes,
                                      agente="medhub:insert_card_extra", db_path=DB_PATH,
                                      dry_run=dry)
        for a in ev["avisos"]:
            print(f"  [AVISO-EVIDENCIA] {a}")
        if evidencias_ponte.linha_resumo(ev):
            print(f"  {evidencias_ponte.linha_resumo(ev)}")
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[ERRO] {e} -- transacao desfeita. NADA gravado.")
        sys.exit(1)

    if not dry:
        conn.commit()
        print(f"\nCommitado: {ins} inseridos, {skip} pulados.")
    else:
        print(f"\n(dry-run) {ins} seriam inseridos, {skip} pulados. Nada gravado.")
    conn.close()


def _fmt(v):
    return "NULL" if v is None else str(v)


def reancorar(args):
    """--reancorar: dry-run -> COUNT-ASSERT (--expect) -> fixado -> grava numa transacao."""
    plano = json.load(open(args.reancorar, encoding='utf-8'))
    conn = _conectar()
    erros, mudancas, iguais, n_ancoras = [], [], 0, 0
    for i, item in enumerate(plano):
        cid = item.get('card_id')
        rotulo = f"card {cid if cid is not None else '#' + str(i)}"
        row = conn.execute("SELECT questao_id, tema_id FROM flashcards WHERE id = ?",
                           (cid,)).fetchone() if cid is not None else None
        if row is None:
            erros.append(f"{rotulo}: nao existe em flashcards")
            continue
        qid, tid = item.get('questao_id'), item.get('tema_id')
        try:
            chaves = _chaves_emed(item.get('emed'))
        except ValueError as e:
            erros.append(f"{rotulo}: {e}")
            continue
        if tid is None or not _existe(conn, "taxonomia_cronograma", tid):
            erros.append(f"{rotulo}: tema_id {tid} nao existe em taxonomia_cronograma")
        erros += _validar_ancoras(conn, qid, chaves, rotulo)
        atuais = _ancoras_atuais(conn, cid)
        novas = [k for k in chaves if k not in atuais]
        extras = sorted(atuais - set(chaves))
        if extras:
            print(f"  [AVISO] {rotulo}: ancora(s) ja gravada(s) fora do plano, mantida(s): "
                  + ", ".join(f"{l}_{n}" for l, n in extras))
        if (row[0], row[1]) == (qid, tid) and not novas:
            iguais += 1
            continue
        print(f"  [MUDA] {rotulo}: questao_id {_fmt(row[0])} -> {_fmt(qid)}; "
              f"tema_id {_fmt(row[1])} -> {_fmt(tid)}; ancoras a criar: "
              + (", ".join(f"{l}_{n}" for l, n in novas) or "-"))
        mudancas.append((cid, qid, tid, novas))
        n_ancoras += len(novas)
    if erros:
        for e in erros:
            print(f"  [ERRO] {e}")
        print("\n[ERRO] re-ancoragem recusada. NADA gravado.")
        conn.close()
        return 1

    print(f"\n{len(mudancas)} card(s) mudam, {iguais} iguais; {n_ancoras} ancora(s) a criar.")
    if not args.apply:
        print("(dry-run) Nada gravado. Para gravar: --apply --expect "
              f"{len(mudancas)}")
        conn.close()
        return 0
    if args.expect is None or args.expect != len(mudancas):
        print(f"[ERRO] COUNT-ASSERT: --expect {_fmt(args.expect)} != {len(mudancas)} card(s) "
              "que mudam. NADA gravado.")
        conn.close()
        return 2
    if not mudancas:
        print("Nada a gravar (0 mudancas).")
        conn.close()
        return 0
    try:
        _fixar_antes("insert_card_extra --reancorar")
    except Exception as e:
        print(f"[ERRO] sem ponto de retorno FIXADO ({e}). NADA gravado.")
        conn.close()
        return 1
    try:
        db._ensure_emed_tables(conn)
        for cid, qid, tid, novas in mudancas:
            conn.execute("UPDATE flashcards SET questao_id = ?, tema_id = ? WHERE id = ?",
                         (qid, tid, cid))
            for lista, num in novas:
                db.emed_ancorar_card(conn, lista, num, cid)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] {e} -- transacao desfeita. NADA gravado.")
        return 1
    finally:
        conn.close()
    print(f"Commitado: {len(mudancas)} card(s) re-ancorado(s), {n_ancoras} ancora(s) criada(s).")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument('--from', dest='src', help='JSON de cards novos')
    modo.add_argument('--reancorar', metavar='FILE', help='JSON [{card_id, tema_id, emed, questao_id?}]')
    ap.add_argument('--apply', action='store_true', help='Grava (default: dry-run)')
    ap.add_argument('--expect', type=int, help='--reancorar --apply: N de cards que mudam (COUNT-ASSERT)')
    args = ap.parse_args()
    if args.reancorar:
        return reancorar(args)
    inserir(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
