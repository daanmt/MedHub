"""apply_reforja.py — aplica reescritas de flashcard preservando o estado FSRS.

Contraparte de escrita do detector `audit_card_atomicity.py` (s128). Recebe um
JSON de reescritas (card_id + campos v5) e chama `db.update_flashcard_fields`,
que mantem o `card_id` -- logo `fsrs_cards`/`fsrs_revlog` ficam intactos e o
historico de repeticao do card sobrevive a reforja.

Nasceu para consumir output de CURADORIA EM LOTE (inclusive de subagentes), e
por isso e GATEADO: nada e aplicado sem passar por tres validacoes.

  1. schema      -- card_id existe no db; ha ao menos um campo permitido;
                    frente_pergunta e verso_resposta nao vem vazios.
  2. encoding    -- AGENTE.md secao 4.5: proibido LaTeX ($...$, \\rightarrow,
                    \\le), setas Unicode, aspas/travessoes inteligentes.
  3. atomicidade -- roda o proprio detector sobre o conteudo PROPOSTO. Uma
                    reforja que continua duplo-ask nao entra: o remedio e
                    auditado pelo mesmo criterio que diagnosticou a doenca.

Falha de qualquer gate em qualquer item -> NADA e aplicado (all-or-nothing).
Isso e deliberado: lote parcialmente aplicado deixa o baralho num estado que
ninguem sabe descrever.

--dry-run e o DEFAULT. Use --apply para gravar.

Uso:
    python tools/apply_reforja.py --from reforja_A.json
    python tools/apply_reforja.py --from reforja_A.json --apply
    python tools/apply_reforja.py --from reforja_A.json --apply --permitir-atomicidade
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / 'tools'))

DB_PATH = ROOT_DIR / 'ipub.db'
CAMPOS_OK = {'frente_contexto', 'frente_pergunta', 'verso_resposta',
             'verso_regra_mestre', 'verso_armadilha', 'tipo'}

# AGENTE.md secao 4.5 -- encoding limpo, zero LaTeX.
RE_PROIBIDO = [
    (re.compile(r"\$[^$]*\$"), "LaTeX inline ($...$)"),
    (re.compile(r"\\(rightarrow|leftarrow|le\b|ge\b|mu\b|times\b|approx)"), "comando LaTeX"),
    (re.compile(r"[\u2192\u2190\u2194\u21d2]"), "seta Unicode"),
    (re.compile(r"[\u2018\u2019\u201c\u201d]"), "aspa inteligente"),
    (re.compile(r"[\u2013\u2014]"), "travessao inteligente"),
]


def _validar(itens):
    """Retorna (ok, erros, avisos). Nao toca o db exceto para checar existencia."""
    erros, avisos = [], []
    try:
        from audit_card_atomicity import checar_front, checar_verso
    except Exception as e:                                    # pragma: no cover
        erros.append(f"detector de atomicidade indisponivel ({e}) -- gate 3 impossivel")
        return False, erros, avisos

    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    try:
        existentes = {r[0] for r in conn.execute("SELECT id FROM flashcards")}
    finally:
        conn.close()

    for i, it in enumerate(itens):
        rot = f"item {i} (card {it.get('card_id', '?')})"
        cid = it.get("card_id")
        if not isinstance(cid, int):
            erros.append(f"{rot}: card_id ausente ou nao-inteiro")
            continue
        if cid not in existentes:
            erros.append(f"{rot}: card_id inexistente no db")
        campos = {k: v for k, v in it.items() if k in CAMPOS_OK}
        if not campos:
            erros.append(f"{rot}: nenhum campo permitido ({sorted(CAMPOS_OK)})")
            continue
        for obrig in ("frente_pergunta", "verso_resposta"):
            if obrig in campos and not str(campos[obrig]).strip():
                erros.append(f"{rot}: {obrig} vazio")
        # gate 2 -- encoding
        for k, v in campos.items():
            if not isinstance(v, str):
                erros.append(f"{rot}: campo {k} nao e string")
                continue
            for rx, nome in RE_PROIBIDO:
                if rx.search(v):
                    erros.append(f"{rot}: {nome} proibido em {k}")
        # gate 3 -- a reforja resolveu mesmo?
        fp, vr = campos.get("frente_pergunta"), campos.get("verso_resposta")
        if fp and (p := checar_front(fp)):
            avisos.append(f"{rot}: frente ainda acusa {p} -- {fp[:70]}")
        if vr and (p := checar_verso(vr)):
            avisos.append(f"{rot}: verso ainda acusa {p}")
    return not erros, erros, avisos


def main():
    ap = argparse.ArgumentParser(
        description="Aplica reescritas de flashcard preservando FSRS (gateado; dry-run default).")
    ap.add_argument("--from", dest="src", required=True, help="JSON de reescritas")
    ap.add_argument("--apply", action="store_true", help="grava (default: dry-run)")
    ap.add_argument("--permitir-atomicidade", action="store_true",
                    help="rebaixa o gate 3 (atomicidade) de bloqueio para aviso -- "
                         "use so para card discriminador legitimo, conferido a olho")
    args = ap.parse_args()

    try:
        itens = json.loads(Path(args.src).read_text(encoding="utf-8-sig"))
    except Exception as e:
        print(f"[ERRO] JSON ilegivel: {e}. NADA aplicado.")
        return 1
    if not isinstance(itens, list) or not itens:
        print("[ERRO] esperado array JSON nao-vazio. NADA aplicado.")
        return 1

    # Relata TODOS os problemas de uma vez -- num lote de dezenas de cards,
    # devolver um tipo de erro por vez vira ping-pong com o curador.
    ok, erros, avisos = _validar(itens)
    for e in erros:
        print(f"  [ERRO] {e}")
    for a in avisos:
        print(f"  [AVISO-ATOMICIDADE] {a}")

    bloqueia_atom = bool(avisos) and not args.permitir_atomicidade
    if erros or bloqueia_atom:
        print()
        if erros:
            print(f"[ERRO] {len(erros)} problema(s) de schema/encoding.")
        if bloqueia_atom:
            print(f"[ERRO] {len(avisos)} reforja(s) NAO resolveram o defeito. "
                  "Corrija o JSON, ou passe --permitir-atomicidade se forem "
                  "cards discriminadores legitimos (1 criterio de acerto).")
        print("NADA aplicado (all-or-nothing).")
        return 1

    print(f"[GATE] {len(itens)} item(ns) aprovados (schema + encoding + atomicidade).")
    if not args.apply:
        for it in itens[:8]:
            print(f"  [DRY] card {it['card_id']}: "
                  f"{str(it.get('frente_pergunta', '(so verso)'))[:72]}")
        if len(itens) > 8:
            print(f"  ... e mais {len(itens) - 8}")
        print("\n(dry-run) nada gravado. Use --apply.")
        return 0

    from app.utils.db import update_flashcard_fields
    aplicados, falhos = 0, []
    for it in itens:
        campos = {k: v for k, v in it.items() if k in CAMPOS_OK}
        if update_flashcard_fields(it["card_id"], campos):
            aplicados += 1
        else:
            falhos.append(it["card_id"])
    print(f"[OK] {aplicados}/{len(itens)} card(s) reescrito(s) -- FSRS preservado.")
    if falhos:
        print(f"[WARN] falharam: {falhos}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
