"""learning_efficacy.py — eficácia de aprendizado por dimensão (P3 part-4).

Read-only (`mode=ro`). Responde com dados o que antes era palpite:
  - distribuição de ratings (Again..Easy) por `tipo`, `card_version`,
    `quality_source` e `selection_reason` — revlog pós-P3; linhas sem
    proveniência agrupam como 'pre-P3' (sem backfill, honesto);
  - reincidência pós-card: eventos `reincidencia` / eventos `generation`
    (proxy: erro novo batendo em tema que JÁ tinha cards — o card não
    preveniu a repetição).

🔴 GATE ANTI-DECORATIVO: se em 3 ciclos de curadoria nenhum número daqui
alterar uma decisão observável (reforja, política de fila, limiar de
detector), REMOVER este script — falsa telemetria é pior que ausência.

Uso: python tools/learning_efficacy.py [--json]
"""
import argparse
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ipub.db")

DIMENSOES = ("tipo", "card_version", "quality_source", "selection_reason")


def compute(db_path=None, log_path=None):
    """Agrega ratings por dimensão + reincidência. Retorna dict (testável)."""
    path = db_path or DB_PATH
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cols_revlog = {r[1] for r in con.execute("PRAGMA table_info(fsrs_revlog)")}
        tem_prov = {"card_version", "selection_reason"} <= cols_revlog
        sel_ver = "COALESCE(CAST(r.card_version AS TEXT), 'pre-P3')" if tem_prov else "'pre-P3'"
        sel_mot = "COALESCE(r.selection_reason, 'pre-P3')" if tem_prov else "'pre-P3'"
        rows = con.execute(f"""
            SELECT COALESCE(f.tipo, '?'), {sel_ver},
                   COALESCE(f.quality_source, '?'), {sel_mot},
                   r.rating, COUNT(*)
            FROM fsrs_revlog r
            LEFT JOIN flashcards f ON f.id = r.card_id
            GROUP BY 1, 2, 3, 4, 5
        """).fetchall()
    finally:
        con.close()

    def _marginal(indice):
        agg = {}
        for linha in rows:
            chave, rating, n = linha[indice], linha[4], linha[5]
            d = agg.setdefault(str(chave), {1: 0, 2: 0, 3: 0, 4: 0})
            if rating in d:
                d[rating] += n
        out = {}
        for chave, d in sorted(agg.items()):
            total = sum(d.values())
            out[chave] = {"total": total,
                          "again_rate": round(d[1] / total, 3) if total else 0.0,
                          "ratings": d}
        return out

    resultado = {dim: _marginal(i) for i, dim in enumerate(DIMENSOES)}

    try:
        import event_log
        n_gen = len(event_log.eventos("generation", log_path=log_path))
        n_rei = len(event_log.eventos("reincidencia", log_path=log_path))
    except Exception:
        n_gen = n_rei = 0
    resultado["reincidencia"] = {
        "geracoes": n_gen, "reincidencias": n_rei,
        "taxa": round(n_rei / n_gen, 3) if n_gen else None,
        "nota": "proxy: erro novo batendo em tema que ja tinha cards (eventos pos-P3)",
    }
    return resultado


def main():
    ap = argparse.ArgumentParser(description="Eficacia de aprendizado (read-only).")
    ap.add_argument("--json", action="store_true", help="saida JSON crua")
    args = ap.parse_args()
    r = compute()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    print("EFICACIA DE APRENDIZADO (revlog; proveniencia pos-P3)")
    for dim in DIMENSOES:
        print(f"\n  por {dim}:")
        for chave, d in r[dim].items():
            print(f"    {chave:<14} n={d['total']:>5}  again={d['again_rate']:.1%}")
    rei = r["reincidencia"]
    print(f"\n  reincidencia pos-card: {rei['reincidencias']}/{rei['geracoes']}"
          + (f" ({rei['taxa']:.1%})" if rei["taxa"] is not None else "")
          + f"  [{rei['nota']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
