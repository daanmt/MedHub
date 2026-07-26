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
DB_PATH = ROOT_DIR / 'ipub.db'

# --- duplo-ask -------------------------------------------------------------
# Cada alternativa e uma assinatura independente de "segunda demanda". O ponto
# comum: apos o interrogativo, um 'e' introduz um NOVO nucleo a ser respondido.
# Usa-se ' e ' com artigo/interrogativo/imperativo a seguir para nao casar
# enumeracao dentro de um mesmo fato ("dor e febre", "sifilis e cancro mole").
RE_DUPLO_ASK = re.compile(
    r"("
    r"\be\s+(qual|quais|quando|como|onde|quanto|quantos|quantas)\b"     # "qual X e qual Y"
    r"|\be\s+(por\s+qu[eê]|porqu[eê]|o\s+porqu[eê]|o\s+que|em\s+que|de\s+que)\b"
    r"|\be\s+(diga|explique|justifique|cite|indique|informe|classifique)\b"
    r"|\brespectivamente\b"
    r"|\b(as|os)\s+(duas|dois)\s+\w+"                                   # "quais as duas manifestacoes"
    r")",
    re.IGNORECASE)

# Segunda assinatura: pergunta com interrogativo + ' e ' + ARTIGO + substantivo.
# Exige o interrogativo para nao casar prosa de contexto.
RE_INTERROGATIVO = re.compile(
    r"\b(qual|quais|quando|como|onde|por\s+qu[eê]|o\s+que|quanto[as]?)\b",
    re.IGNORECASE)
RE_E_ARTIGO_NUCLEO = re.compile(
    r"\be\s+(a|o|as|os)\s+[a-zà-ÿ]{4,}", re.IGNORECASE)

# --- resposta-multifato ----------------------------------------------------
LIMITE_CHARS = 220          # acima disso ja nao e "uma frase"
LIMITE_FRASES = 3           # 3+ terminadores = paragrafo
RE_TERMINADOR = re.compile(r"[.!?](?:\s|$)")


def _conn(db_path=None):
    p = Path(db_path) if db_path else DB_PATH
    return sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)


def _conta_interrogacoes(txt):
    return txt.count("?")


def checar_front(txt):
    """Retorna o rotulo do padrao duplo-ask, ou None."""
    if not txt:
        return None
    if _conta_interrogacoes(txt) > 1:
        return "duplo-ask/duas-interrogacoes"
    if RE_DUPLO_ASK.search(txt):
        return "duplo-ask/conectivo"
    if RE_INTERROGATIVO.search(txt) and RE_E_ARTIGO_NUCLEO.search(txt):
        return "duplo-ask/segundo-nucleo"
    return None


def checar_verso(txt):
    """Retorna o rotulo do padrao resposta-multifato, ou None."""
    if not txt:
        return None
    n_frases = len(RE_TERMINADOR.findall(txt))
    if len(txt) > LIMITE_CHARS:
        return "resposta-multifato/paragrafo"
    if n_frases >= LIMITE_FRASES:
        return "resposta-multifato/multi-frase"
    return None


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
