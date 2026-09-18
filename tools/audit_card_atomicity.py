"""Check de ATOMICIDADE de flashcard (spec: estilo-flashcard.md §Formato atomico).

Detecta cards ATIVOS (needs_qualitative < 2) que violam o minimum information
principle -- o defeito que a sessao 124 chamou de "paragraph card" e que o
usuario reidentificou ao vivo na s128 ("os cards nao devem ter diversos
requisitos de acerto").

Dois anti-padroes (regex deterministica, v0):

  - duplo-ask         : a FRENTE cobra duas respostas distintas ("qual a via E a
                        composicao", "diagnostico E tratamento", "... e por que",
                        "quais as duas", duas interrogacoes). Torna a nota FSRS
                        ininterpretavel: acertar 1 de 2 nao e "meio card".
  - resposta-multifato: o VERSO responde em paragrafo em vez de uma frase
                        (regra 3 do formato atomico) -- carga de recuperacao
                        inflada, ilusao de competencia.

WARN-first: DETECTA e reporta; nunca corrige, nunca bloqueia, nunca escreve
(abre o db em modo read-only). A saida do main() e a worklist de reforja -- o
desmembramento em si e curadoria (update_flashcard_fields + insert_card_extra),
fora deste modulo.

duplo-ask aplica so no FRONT; resposta-multifato so no verso -- evita casar o
campo errado.

🔴 CLASSE CONHECIDA DE FALSO-POSITIVO -- card discriminador. A regra 5 do
formato atomico ENDOSSA contrastar duas entidades num card so ("A x B: qual
delas ...?"). O detector nao distingue "duas demandas" de "um contraste", entao
esses cards disparam duplo-ask. Criterio de desempate ao triar a worklist: conte
os CRITERIOS DE ACERTO, nao as entidades citadas. "Cancro mole x donovanose:
qual doi E qual tem adenite?" = 2 criterios -> defeito real. "Cancro mole x
donovanose: qual das duas doi e cursa com adenite?" = 1 criterio (a resposta e
uma so) -> legitimo, ainda que o regex acuse.

Classes de falso-positivo ja mapeadas (todas com o mesmo desempate acima):
  1. card discriminador   -- "A x B: qual das duas ...?"
  2. copula sem acento    -- "Qual e a unica vacina ...?"  [guarda automatica]
  3. par 'entre X e Y'    -- "intervalo entre a transfusao e a vacina"  [guarda automatica]
  4. objetos da MESMA resposta -- "Qual exame define o diagnostico e o prognostico?"
     (a resposta e um exame so). SEM guarda automatica: a assinatura sintatica e
     identica a de uma segunda demanda real, entao exige olho humano. Libere item
     a item via `--permitir-atomicidade` do recurate_cards.py (que absorveu
     o apply_reforja na consolidacao part-6).

As guardas 2 e 3 nasceram de auditar a propria worklist (s128) -- o corpus grava
sem acento por convencao, o que colapsa a copula "e" e a conjuncao "e" na mesma
letra. Sem elas o detector superestimava em ~8% (220 -> 203 cards de duplo-ask).

Uso standalone: python tools/audit_card_atomicity.py [--json] [--limit N]
Uso pelo harness: from audit_card_atomicity import run_checks
"""
import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
DB_PATH = ROOT_DIR / 'ipub.db'

# ⚰️ Os predicados PUROS (regexes, `checar_front`, `checar_verso`, `medir_verso`,
# `checar_ratchet_verso`, `LIMITE_CHARS`, `LIMITE_FRASES`) mudaram para
# `app/utils/card_atomicity.py` em 18/09/2026 (item 1.9a). Motivo: `app/utils/db.py`
# precisa deles e os alcancava montando `sys.path` com `__file__` -- seta invertida.
# Aqui fica a VARREDURA (abre banco, fala com terminal); o nucleo e importado.
from app.utils.card_atomicity import (               # noqa: E402,F401
    LIMITE_CHARS, LIMITE_FRASES, RE_TERMINADOR,
    checar_front, checar_verso, medir_verso, checar_ratchet_verso,
)


def _conn(db_path=None):
    p = Path(db_path) if db_path else DB_PATH
    return sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)



def run_checks(db_path=None):
    """Varre os cards ativos. Retorna lista de achados (dicts). Read-only."""
    achados = []
    conn = _conn(db_path)
    try:
        conn.row_factory = sqlite3.Row
        linhas = conn.execute(
            "SELECT f.id, f.frente_pergunta, f.verso_resposta, f.tipo, "
            "       t.area, t.tema "
            "FROM flashcards f "
            "LEFT JOIN taxonomia_cronograma t ON t.id = f.tema_id "
            "WHERE COALESCE(f.needs_qualitative, 0) < 2 "
            "ORDER BY f.id").fetchall()
    finally:
        conn.close()

    for r in linhas:
        for padrao in (checar_front(r["frente_pergunta"]),
                       checar_verso(r["verso_resposta"])):
            if padrao:
                achados.append({
                    "id": r["id"],
                    "padrao": padrao,
                    "area": r["area"] or "?",
                    "tema": r["tema"] or "?",
                    "tipo": r["tipo"] or "?",
                    "front": (r["frente_pergunta"] or "")[:110],
                })
    return achados


def main():
    parser = argparse.ArgumentParser(
        description="Check de atomicidade de flashcard (WARN-first; exit 0 sempre).")
    parser.add_argument("--json", action="store_true", help="saida JSON (worklist)")
    parser.add_argument("--limit", type=int, default=25,
                        help="quantos achados listar no modo texto (default 25)")
    parser.add_argument("--padrao", default=None,
                        help="filtra por prefixo de padrao (ex.: duplo-ask)")
    args = parser.parse_args()

    achados = run_checks()
    if args.padrao:
        achados = [a for a in achados if a["padrao"].startswith(args.padrao)]

    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=1))
        return 0

    total = len(achados)
    por_padrao = Counter(a["padrao"] for a in achados)
    por_tema = Counter(f'{a["area"]} / {a["tema"]}' for a in achados)
    ids = {a["id"] for a in achados}

    print(f"# Atomicidade de flashcards -- {total} achado(s) em {len(ids)} card(s)")
    print()
    for p, n in por_padrao.most_common():
        print(f"  {n:>4}  {p}")
    print()
    print("  temas mais afetados:")
    for t, n in por_tema.most_common(10):
        print(f"  {n:>4}  {t}")
    print()
    for a in achados[:args.limit]:
        print(f"[WARN] CARD_ATOMICIDADE/{a['padrao']}: card #{a['id']} "
              f"({a['area']}/{a['tema']}) -- {a['front']}")
    if total > args.limit:
        print(f"  ... e mais {total - args.limit} (use --json p/ a worklist completa)")
    print()
    print("-- WARN nao bloqueia; worklist de reforja (desmembrar/atomizar).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
