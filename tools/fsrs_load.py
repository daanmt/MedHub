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
  python tools/fsrs_load.py --blackout      # F71: painel do blackout de prova + DRY-RUN da
                                            #      re-rodada do balanceador (diff declarado)
  python tools/fsrs_load.py --blackout --apply   # grava o diff declarado (COUNT-ASSERT §10.7)

`--blackout` e a UNICA acao que escreve, e so com `--apply`; a escrita passa por
`app.utils.db.rebalancear_blackout` (writer allowlistado), nunca por SQL daqui.
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


def blackout(aplicar, como_json):
    """Painel F71: dias de blackout (core/provas.json), carga neles, e a re-rodada do
    balanceador sobre a fila -- dry-run por default, `--apply` grava. O diff sai
    DECLARADO (COUNT por 'de -> para') no mesmo ato; overflow e listado, nunca movido."""
    sys.path.insert(0, str(ROOT_DIR))
    from app.utils import db
    conn = db.get_connection()
    try:
        r = db.rebalancear_blackout(conn, aplicar=aplicar)
    finally:
        conn.close()
    if como_json:
        print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
        return 0
    modo = "APLICADO" if r["aplicado"] else "DRY-RUN (nada gravado)"
    print(f"# Blackout de prova (F71) -- {modo}")
    print(f"  dias de blackout (core/provas.json): {', '.join(r['blackout']) or 'nenhum'}")
    print(f"  cards movidos: {len(r['movidos'])} | overflow (ficam onde estao): {len(r['overflow'])}"
          + (f" | escritos: {r['escritos']}" if r["aplicado"] else ""))
    for chave, n in sorted(r["resumo"].items()):
        print(f"    COUNT {n:>3}  {chave}")
    if r["overflow"]:
        print("  overflow:")
        for o in r["overflow"]:
            print(f"    #{o['card_id']} due {o['due']} -- {o['motivo']}")
    if not r["aplicado"] and r["movidos"]:
        print("  -> para gravar exatamente este diff: python tools/fsrs_load.py --blackout --apply")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Previsao de carga do calendario FSRS (read-only).")
    ap.add_argument("--dias", type=int, default=21)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--blackout", action="store_true",
                    help="F71: painel do blackout de prova + re-rodada do balanceador (dry-run)")
    ap.add_argument("--apply", action="store_true",
                    help="com --blackout: grava o diff declarado (COUNT-ASSERT)")
    args = ap.parse_args()

    if args.apply and not args.blackout:
        ap.error("--apply so faz sentido com --blackout")
    if args.blackout:
        return blackout(args.apply, args.json)

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
