"""Previsao de carga do calendario FSRS (s128) -- read-only.

Mostra quantos cards vencem por dia, para tornar VISIVEL o efeito do load
balancer (`app/utils/fsrs_balance.py`). Sem isto o achatamento e invisivel:
o usuario so sentiria a carga, nunca veria a distribuicao.

Metricas de dispersao (calculadas so sobre os dias futuros da janela):
  pico       -- maior carga num unico dia
  media/dp   -- media e desvio-padrao da carga diaria
  CV         -- desvio/media. E o numero que o balanceamento deve derrubar
                ao longo do tempo; carga perfeitamente plana tem CV = 0.

Uso:
  python tools/fsrs_load.py                 # 21 dias
  python tools/fsrs_load.py --dias 45
  python tools/fsrs_load.py --json
"""
import argparse
import json
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, pstdev

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = ROOT_DIR / 'ipub.db'


def coletar(dias):
    hoje = date.today()
    fim = hoje + timedelta(days=dias - 1)
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    try:
        # Atrasados entram todos no dia de hoje -- e assim que a fila os serve.
        atrasados = conn.execute(
            "SELECT COUNT(1) FROM fsrs_cards f JOIN flashcards l ON l.id=f.card_id "
            "WHERE f.state > 0 AND COALESCE(l.needs_qualitative,0) < 2 "
            "  AND date(f.due) < ?", (hoje.isoformat(),)).fetchone()[0]
        linhas = conn.execute(
            "SELECT date(f.due) AS d, COUNT(1) FROM fsrs_cards f "
            "JOIN flashcards l ON l.id=f.card_id "
            "WHERE f.state > 0 AND COALESCE(l.needs_qualitative,0) < 2 "
            "  AND date(f.due) BETWEEN ? AND ? GROUP BY d",
            (hoje.isoformat(), fim.isoformat())).fetchall()
        pool = conn.execute(
            "SELECT COUNT(1) FROM fsrs_cards f JOIN flashcards l ON l.id=f.card_id "
            "WHERE f.state = 0 AND COALESCE(l.needs_qualitative,0) < 2").fetchone()[0]
    finally:
        conn.close()

    carga = {}
    for d, n in linhas:
        try:
            carga[date.fromisoformat(d)] = n
        except (TypeError, ValueError):
            continue
    carga[hoje] = carga.get(hoje, 0) + atrasados
    serie = [(hoje + timedelta(days=i), carga.get(hoje + timedelta(days=i), 0))
             for i in range(dias)]
    return serie, atrasados, pool


def main():
    ap = argparse.ArgumentParser(description="Previsao de carga do calendario FSRS (read-only).")
    ap.add_argument("--dias", type=int, default=21)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    serie, atrasados, pool = coletar(args.dias)
    if args.json:
        print(json.dumps({
            "atrasados": atrasados, "pool": pool,
            "serie": [{"dia": d.isoformat(), "cards": n} for d, n in serie],
        }, ensure_ascii=False, indent=1))
        return 0

    valores = [n for _, n in serie]
    m = mean(valores) if valores else 0
    dp = pstdev(valores) if len(valores) > 1 else 0
    cv = (dp / m) if m else 0
    largura = max(valores + [1])

    print(f"# Carga do calendario FSRS -- proximos {args.dias} dias")
    print(f"  atrasados hoje: {atrasados} | pool nunca introduzido: {pool}")
    print()
    for d, n in serie:
        barra = "#" * int(round(n / largura * 46)) if n else ""
        print(f"  {d.isoformat()}  {n:>4}  {barra}")
    print()
    print(f"  pico {max(valores) if valores else 0} | media {m:.1f} | desvio {dp:.1f} "
          f"| CV {cv:.2f}")
    print("  (CV = desvio/media: quanto MENOR, mais homogenea a carga. "
          "O balanceamento derruba isso ao longo das revisoes.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
