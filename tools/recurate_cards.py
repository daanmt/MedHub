"""recurate_cards.py — o reescritor in-place CANONICO de flashcards.

Nascida na sessão 081: a revisão card-a-card expôs uma safra antiga (mar/2026)
com formulação fraca (perguntas circulares, decoreba de ordem, armadilha pedante)
que a auditoria automática (audit_flashcard_quality.py) não detecta — só o olho humano.
Este CLI reescreve esses cards in-place, preservando o card_id (e portanto
o estado FSRS: `fsrs_cards`/`fsrs_revlog` ficam intactos), incrementando card_version.

CONSOLIDACAO PART-6 (fusao a): absorveu tools/apply_reforja.py, que fazia a
mesma coisa (reescrita in-place preservando FSRS) por outra porta e com outro
nivel de rigor. Dois reescritores com rigores diferentes = o lote passa pelo
mais frouxo. Agora ha UM, com TODOS os rigores:

  1. schema       -- card_id existe; ha ao menos um campo permitido;
                     frente_pergunta/verso_resposta nao vem vazios.
  2. encoding     -- AGENTE.md secao 4.5 via card_checks.RE_PROIBIDO: proibido
                     LaTeX ($...$, \\rightarrow, \\le), setas Unicode,
                     aspas/travessoes inteligentes.
  3. formulacao   -- template-conduta-criterio e resposta-embutida
                     (card_checks.checar_pergunta_template / _resposta_embutida).
  4. atomicidade  -- roda o proprio detector (audit_card_atomicity) sobre o
                     conteudo PROPOSTO. Uma reforja que continua duplo-ask nao
                     entra: o remedio e auditado pelo mesmo criterio que
                     diagnosticou a doenca. Rebaixavel com
                     --permitir-atomicidade para card discriminador legitimo.

ALL-OR-NOTHING: falha de qualquer gate em qualquer item -> NADA e aplicado, em
transacao unica. Deliberado: lote parcialmente aplicado deixa o baralho num
estado que ninguem sabe descrever. (Antes da part-6 este CLI aplicava item a
item, pulando os rejeitados -- exatamente o estado indescritivel.)

DRY-RUN E O DEFAULT (herdado do apply_reforja). Use --apply para gravar.
`--dry-run` segue aceito (explicito e redundante) para nao quebrar o workflow
documentado em .agents/workflows/curar-cards.md.

Cada item aceita as chaves curtas do workflow OU os nomes de coluna v5:
  {card_id, contexto|frente_contexto, pergunta|frente_pergunta,
   resposta|verso_resposta, regra|verso_regra_mestre,
   armadilha|verso_armadilha, tipo, aposentar?}
  - aposentar=true  -> needs_qualitative=2 (remove da fila); não altera conteúdo.
  - caso contrário  -> atualiza os campos fornecidos, card_version+1,
                       quality_source='qualitative', needs_qualitative=0.

Uso:
  python tools/recurate_cards.py --from tmp/curadoria.json            # dry-run
  python tools/recurate_cards.py --from tmp/curadoria.json --dry-run  # idem
  python tools/recurate_cards.py --from tmp/curadoria.json --apply
  python tools/recurate_cards.py --from tmp/curadoria.json --apply --permitir-atomicidade
"""
import sqlite3
import os
import json
import argparse
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_TOOLS_DIR)
sys.path.insert(0, _TOOLS_DIR)
sys.path.insert(0, _ROOT_DIR)
import card_checks  # gate de qualidade (part-4) — mesma biblioteca dos demais writers

DB_PATH = os.path.join(_ROOT_DIR, 'ipub.db')

# Chave do JSON -> coluna. As chaves curtas sao a interface do workflow
# curar-cards.md; os nomes v5 vieram do apply_reforja (fusao a) e seguem
# aceitos para que lotes ja gerados naquele formato continuem valendo.
FIELD_MAP = {
    'contexto': 'frente_contexto',
    'pergunta': 'frente_pergunta',
    'resposta': 'verso_resposta',
    'regra': 'verso_regra_mestre',
    'armadilha': 'verso_armadilha',
    'tipo': 'tipo',
    'frente_contexto': 'frente_contexto',
    'frente_pergunta': 'frente_pergunta',
    'verso_resposta': 'verso_resposta',
    'verso_regra_mestre': 'verso_regra_mestre',
    'verso_armadilha': 'verso_armadilha',
}


def _campos_do_item(e):
    """{coluna: valor} dos campos presentes. Chave curta vence a longa se ambas
    vierem (nao deveria acontecer; determinismo > surpresa)."""
    campos = {}
    for k, col in FIELD_MAP.items():
        if e.get(k) is not None and col not in campos:
            campos[col] = e[k]
    return campos


def validar(edits, conn, permitir_atomicidade=False):
    """Roda os 4 gates sobre o lote INTEIRO. Retorna (erros, avisos, plano).

    `plano` = lista de acoes ja resolvidas [(tipo, card_id, campos, versao)],
    montada so para os itens sem erro -- mas a aplicacao so acontece se
    `erros` estiver vazio (all-or-nothing).

    Relata TODOS os problemas de uma vez: num lote de dezenas de cards,
    devolver um erro por vez vira ping-pong com o curador.
    """
    erros, avisos, plano = [], [], []
    try:
        from audit_card_atomicity import checar_front, checar_verso
    except Exception as e:                                    # pragma: no cover
        erros.append(f"detector de atomicidade indisponivel ({e}) -- gate 4 impossivel")
        return erros, avisos, plano

    for i, e in enumerate(edits):
        cid = e.get('card_id')
        rot = f"item {i} (card {cid if cid is not None else '?'})"
        if not isinstance(cid, int):
            erros.append(f"{rot}: card_id ausente ou nao-inteiro")
            continue
        row = conn.execute(
            "SELECT frente_pergunta, card_version FROM flashcards WHERE id=?",
            (cid,)).fetchone()
        if not row:
            erros.append(f"{rot}: card_id inexistente no db")
            continue
        antiga, ver = row[0], (row[1] or 1)

        if e.get('aposentar'):
            plano.append(("aposentar", cid, {}, ver, antiga))
            continue

        campos = _campos_do_item(e)
        # part-4: fim do no-op disfarcado — item sem campo valido NAO executa
        # UPDATE, NAO incrementa card_version, NAO flipa quality_source.
        if not campos:
            erros.append(f"{rot}: nenhum campo valido "
                         f"({', '.join(sorted(FIELD_MAP))}) — nenhum campo valido, item rejeitado")
            continue

        # gate 1 -- schema: obrigatorios presentes nao podem vir vazios/nao-string
        for col, val in campos.items():
            if not isinstance(val, str):
                erros.append(f"{rot}: campo {col} nao e string")
        for col in ("frente_pergunta", "verso_resposta"):
            if col in campos and not str(campos[col]).strip():
                erros.append(f"{rot}: {col} vazia")

        # gates 2+3 -- encoding e formulacao, sobre os campos PRESENTES (edicao
        # parcial e legitima — nao exigir campos que o item nao esta alterando).
        for msg in card_checks.checar_encoding(campos):
            erros.append(f"{rot}: {msg}")
        if campos.get("frente_pergunta"):
            t = card_checks.checar_pergunta_template(campos)
            if t:
                erros.append(f"{rot}: {t}")
            emb = card_checks.checar_resposta_embutida(campos)
            if emb:
                erros.append(f"{rot}: {emb}")

        # gate 4 -- a reforja resolveu mesmo? (absorvido do apply_reforja)
        fp, vr = campos.get("frente_pergunta"), campos.get("verso_resposta")
        if isinstance(fp, str) and (p := checar_front(fp)):
            avisos.append(f"{rot}: frente ainda acusa {p} -- {fp[:70]}")
        if isinstance(vr, str) and (p := checar_verso(vr)):
            avisos.append(f"{rot}: verso ainda acusa {p}")

        plano.append(("refazer", cid, campos, ver, antiga))

    return erros, avisos, plano


def aplicar(plano, conn):
    """Aplica o plano em TRANSACAO UNICA (all-or-nothing na escrita, nao so na
    validacao): qualquer excecao no meio faz rollback do lote inteiro."""
    n_refeitos = n_aposentados = 0
    try:
        for tipo, cid, campos, ver, _antiga in plano:
            if tipo == "aposentar":
                conn.execute("UPDATE flashcards SET needs_qualitative=2 WHERE id=?", (cid,))
                n_aposentados += 1
                continue
            sets = [f"{col}=?" for col in campos]
            vals = list(campos.values())
            sets += ["card_version=?", "quality_source=?", "needs_qualitative=?"]
            vals += [ver + 1, 'qualitative', 0, cid]
            conn.execute(f"UPDATE flashcards SET {', '.join(sets)} WHERE id=?", vals)
            n_refeitos += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return n_refeitos, n_aposentados


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from', dest='src', required=True, help='JSON com a lista de edições')
    ap.add_argument('--apply', action='store_true', help='grava (default: dry-run)')
    ap.add_argument('--dry-run', action='store_true',
                    help='mostra o que faria, sem gravar (ja e o default; explicito)')
    ap.add_argument('--permitir-atomicidade', action='store_true',
                    help='rebaixa o gate 4 (atomicidade) de bloqueio para aviso -- '
                         'use so para card discriminador legitimo, conferido a olho')
    args = ap.parse_args()
    gravar = args.apply and not args.dry_run

    try:
        with open(args.src, encoding='utf-8-sig') as f:
            edits = json.load(f)
    except Exception as e:
        print(f"[ERRO] JSON ilegivel: {e}. NADA aplicado.")
        return 1
    if not isinstance(edits, list) or not edits:
        print("[ERRO] esperado array JSON nao-vazio. NADA aplicado.")
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # part-4: FKs impostas
    try:
        erros, avisos, plano = validar(edits, conn, args.permitir_atomicidade)
        for e in erros:
            print(f"  [ERRO] {e}")
        for a in avisos:
            print(f"  [AVISO-ATOMICIDADE] {a}")

        bloqueia_atom = bool(avisos) and not args.permitir_atomicidade
        if erros or bloqueia_atom:
            print()
            if erros:
                print(f"[ERRO] {len(erros)} problema(s) de schema/encoding/formulacao.")
            if bloqueia_atom:
                print(f"[ERRO] {len(avisos)} reforja(s) NAO resolveram o defeito. "
                      "Corrija o JSON, ou passe --permitir-atomicidade se forem "
                      "cards discriminadores legitimos (1 criterio de acerto).")
            print("NADA aplicado (all-or-nothing).")
            return 1

        n_ref = sum(1 for p in plano if p[0] == "refazer")
        n_apo = sum(1 for p in plano if p[0] == "aposentar")
        print(f"[GATE] {len(plano)} item(ns) aprovados "
              f"(schema + encoding + formulacao + atomicidade).")
        for tipo, cid, campos, ver, antiga in plano[:8]:
            if tipo == "aposentar":
                print(f"  [APOSENTAR] card {cid}: \"{(antiga or '')[:55]}...\"")
            else:
                curtos = sorted(campos)
                print(f"  [REFAZER] card {cid} v{ver}->v{ver+1} | campos: {', '.join(curtos)}")
        if len(plano) > 8:
            print(f"  ... e mais {len(plano) - 8}")

        if not gravar:
            print(f"\n(dry-run) {n_ref} seriam refeitos, {n_apo} aposentados. "
                  f"Nada gravado. Use --apply.")
            return 0

        n_refeitos, n_aposentados = aplicar(plano, conn)
        print(f"\n[OK] Commitado: {n_refeitos} refeitos, {n_aposentados} aposentados "
              f"-- FSRS preservado (card_id intacto).")
        return 0
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
