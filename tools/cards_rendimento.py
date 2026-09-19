"""cards_rendimento.py -- o card que CONSOME revisao e nao retem (s187). Read-only.

O harness inteiro mede **forma** de card (atomicidade, auto-suficiencia, alinhamento da
frente, comprimento). Nada mede **rendimento**: o card pode ser impecavel e ainda assim
custar revisao sem comprar retencao. Medido em 18/09/2026: **#70 tem 11 revisoes e
stability de 0,67 dia** -- onze passagens compraram menos de um dia.

🔴 **O corte e DERIVADO do proprio baralho, nao importado.** O limiar classico do Anki
(8 lapsos) acharia **ZERO** aqui: o maximo do baralho e 4. Importar a constante seria o
sensor que existe, roda e nao alcanca -- a familia da janela s187. Ancora usada:

    lapses >= 2  E  stability < mediana do baralho

`lapses >= 2` = falhou mais de uma vez (nao e tropeco isolado; 60 de 822 revisados).
`stability < mediana` = depois dessas falhas o modelo ainda nao espera que o card
sobreviva ao intervalo tipico do baralho. Os dois juntos: **48 cards (5,8%)** em
18/09/2026. A mediana e RE-MEDIDA a cada execucao -- o corte acompanha o baralho em vez
de envelhecer como numero fixo.

⚠️ **LIMITE DECLARADO -- e o mais importante deste arquivo.** Isto **NAO fecha o F87**.
O F87 e sobre triagem na AUTORIA ("este card deveria existir?"), e os 13 cards que o
operador cortou **nunca entraram no baralho** -- nao tem `reps`, nao tem `lapses`, nao
tem stability. **Nenhum sinal derivado do FSRS pode alcanca-los.** Este sensor mede o
eixo IRMAO: entre os cards que existem, quais nao estao pagando aluguel. O F87 segue
aberto como GATE do operador, e dizer o contrario seria cobertura aparente (a classe que
o item 1.10 existe para impedir).

⚠️ Segundo limite: baixo rendimento **nao** e defeito do card. Pode ser tema genuinamente
dificil, card na fase de aprendizado, ou lacuna de fundacao que pede andaime em vez de
reforja. Por isso a saida e **CANDIDATO a triagem**, nunca veredito -- como no F115.
"""
import argparse
import json
import os
import sqlite3
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "ipub.db")

MIN_LAPSES = 2          # falhou mais de uma vez -- nao e tropeco isolado


def medir(db_path=None):
    """(candidatos, resumo). Read-only: abre em modo ro e nunca escreve."""
    caminho = db_path or DB_PATH
    con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    try:
        linhas = con.execute(
            "SELECT fc.card_id, fc.reps, fc.lapses, fc.stability, t.area, t.tema "
            "FROM fsrs_cards fc JOIN flashcards f ON f.id = fc.card_id "
            "LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id "
            "WHERE COALESCE(f.needs_qualitative, 0) < 2 AND fc.reps > 0 "
            "AND fc.stability IS NOT NULL").fetchall()
    finally:
        con.close()
    if not linhas:
        return [], {"revisados": 0, "candidatos": 0, "mediana_stability": None}
    mediana = statistics.median(r[3] for r in linhas)
    cand = [{"card_id": r[0], "reps": r[1], "lapses": r[2],
             "stability": round(r[3], 2), "area": r[4], "tema": r[5],
             "custo_por_dia": round(r[1] / r[3], 2) if r[3] else None}
            for r in linhas if r[2] >= MIN_LAPSES and r[3] < mediana]
    cand.sort(key=lambda c: (-c["lapses"], c["stability"]))
    return cand, {
        "revisados": len(linhas),
        "candidatos": len(cand),
        "pct": round(100.0 * len(cand) / len(linhas), 1),
        "mediana_stability": round(mediana, 1),
        "min_lapses": MIN_LAPSES,
    }


def main():
    p = argparse.ArgumentParser(description="Cards que consomem revisao sem reter (read-only)")
    p.add_argument("--json", action="store_true", help="Saida JSON (contrato de maquina)")
    p.add_argument("--limit", type=int, default=20, help="Quantos listar no modo texto")
    args = p.parse_args()
    cand, res = medir()
    if args.json:
        print(json.dumps({"resumo": res, "candidatos": cand}, ensure_ascii=False, indent=2))
        return 0
    print()
    print(f"  Cards ativos com >=1 revisao : {res['revisados']}")
    print(f"  Mediana de stability          : {res['mediana_stability']}d  (re-medida agora)")
    print(f"  CANDIDATOS (lapses >= {res['min_lapses']} e stability < mediana): "
          f"{res['candidatos']} ({res.get('pct')}%)")
    print()
    for c in cand[:args.limit]:
        print(f"    #{c['card_id']:<5} reps={c['reps']:<3} lapses={c['lapses']} "
              f"stability={c['stability']:>6}d  [{c['area']}/{c['tema']}]")
    print()
    print("  🔴 CANDIDATO a triagem, nunca veredito: baixo rendimento pode ser tema dificil")
    print("     ou lacuna de fundacao (pede andaime, nao reforja). Decide leitura humana.")
    print("  ⚠️ NAO fecha o F87: aquele eixo e triagem na AUTORIA, e os 13 cards que o")
    print("     operador cortou nunca entraram no baralho -- nao ha FSRS que os alcance.")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
