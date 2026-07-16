"""Check de auto-suficiencia de flashcard (check 8 do auto_check -- spec
auto-suficiencia-card-e-telemetria-fila Part 1).

Detecta cards ATIVOS (needs_qualitative < 2) que nao sao respondiveis a frio --
referenciam algo que nao esta no proprio card. Tres anti-padroes (regex
deterministica, v0), derivados do audit da sessao 121:

  - opcao-anaforico : o front cita alternativa/opcao/afirmacao falsa/(A)(B)/
                      enunciado negativo -- pressupoe um conjunto de opcoes que
                      NAO esta no card (cunhado de questao de enunciado negativo).
  - deitico         : o front aponta "neste caso/deste paciente/acima/mencionado"
                      -- um dado ausente do card.
  - pct-fake        : o verso traz percentual fabricado ("61% caem/erram").

WARN-first: DETECTA e reporta; nunca corrige, nunca bloqueia, nunca escreve
(abre o db em modo read-only). A saida do main() e a worklist de reforja de
conteudo (id/padrao/area/tema) -- a reforja em si e curadoria, fora deste modulo.

opcao-anaforico e deitico aplicam so no FRONT; pct-fake so no verso -- evita
casar o campo errado.

Uso standalone: python tools/card_self_sufficiency.py [--json]
Uso pelo harness: from card_self_sufficiency import run_checks (check 8 do auto_check.py)
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

# Assinaturas dos anti-padroes (audit da sessao 121, apertadas com guarda de
# contexto anaforico). A prosa clinica reusa "opcao/alternativa" (terapeutica)
# e "acima" (comparador de valor) em sentido nao-MCQ -> so disparam quando ha
# moldura de prova / referencia deitica real. Classes [aá]/[cç] casam com ou
# sem acento (encoding defensivo em Windows).
RE_OPCAO = re.compile(
    r"("
    r"\([A-E]\)"                                               # (A)-(E) enumerado
    r"|enunciado\s+negativo"
    r"|assertiva"                                              # termo quase sempre MCQ
    r"|assinal\w*\s+a\s+(alternativa|afirmativa|assertiva|op[cç][aã]o|frase)"
    r"|(alternativa|afirmativa|assertiva|op[cç][aã]o|frase|afirma[cç][aã]o)"
    r"\s+(correta|incorreta|errada|falsa|verdadeira)"          # "alternativa correta"
    r"|por\s+que\b.{0,60}?(errad|fals[ao]|incorret)"           # critica de opcao
    r"|(op[cç][aã]o|alternativa)\s+['\"]"                      # opcao 'citada'
    r")",
    re.IGNORECASE)
RE_DEITICO = re.compile(
    r"("
    r"neste\s+caso|deste\s+paciente|nessa\s+situa|a\s+seguir"
    r"|\bmencionad|\bcitad"                                    # \b mata 'ressuscitada'
    r"|(quadro|caso|paciente|figura|imagem|tabela|texto|enunciado)\s+acima"
    r"|acima\s+(descrit|cit|mencion|expost|apresentad|referid|relatad)"
    r")",
    re.IGNORECASE)
RE_PCT_FAKE = re.compile(
    r"\d{1,3}\s*%\s*(caem|marcam|erram|escolhem|assinalam|confundem|optam)",
    re.IGNORECASE)

# (padrao, regex, campo) -- campo define ONDE aplicar (front vs verso).
PADROES = (
    ("opcao-anaforico", RE_OPCAO, "front"),
    ("deitico", RE_DEITICO, "front"),
    ("pct-fake", RE_PCT_FAKE, "verso"),
)


def _texto(card, campo):
    """Concatena os campos do front ou do verso do card. Defensivo a None."""
    if campo == "front":
        partes = (card.get("frente_contexto"), card.get("frente_pergunta"))
    else:
        partes = (card.get("verso_regra_mestre"), card.get("verso_armadilha"))
    return " ".join(p for p in partes if p)


def _achado(card, padrao):
    return {"id": card.get("id"), "padrao": padrao,
            "area": card.get("area"), "tema": card.get("tema")}


def _cards_ativos(db_path):
    """Le os cards ativos (needs_qualitative < 2) do ipub.db. Read-only.

    Devolve lista de dicts; nunca lanca (sem db / erro de leitura -> lista vazia).
    """
    if not Path(db_path).exists():
        return []
    con = None
    try:
        # mode=ro: o check nao pode escrever no db nem por bug.
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT fl.id AS id, fl.frente_contexto AS frente_contexto, "
            "fl.frente_pergunta AS frente_pergunta, "
            "fl.verso_regra_mestre AS verso_regra_mestre, "
            "fl.verso_armadilha AS verso_armadilha, "
            "t.tema AS tema, t.area AS area "
            "FROM flashcards fl LEFT JOIN taxonomia_cronograma t ON t.id = fl.tema_id "
            "WHERE fl.needs_qualitative < 2").fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
    finally:
        if con is not None:
            con.close()


def run_checks(cards=None, db_path=None):
    """Devolve a lista de achados de nao-auto-suficiencia sobre os cards ativos.

    Achado: {id, padrao, area, tema}. Um card pode disparar mais de um padrao
    (um achado por padrao). Lista vazia = corpus auto-suficiente. Nunca lanca.

    cards: lista de dicts injetavel (para teste); default = le do ipub.db.
    """
    if cards is None:
        db = Path(db_path) if db_path else ROOT_DIR / "ipub.db"
        cards = _cards_ativos(db)
    achados = []
    for card in cards:
        for padrao, regex, campo in PADROES:
            try:
                if regex.search(_texto(card, campo)):
                    achados.append(_achado(card, padrao))
            except Exception:
                continue
    return achados


def main():
    parser = argparse.ArgumentParser(
        description="Check de auto-suficiencia de flashcard (WARN-first; exit 0 sempre).")
    parser.add_argument("--json", action="store_true",
                        help="saida machine-readable (lista JSON de achados = worklist de reforja)")
    args = parser.parse_args()
    achados = run_checks()
    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
        return 0
    if not achados:
        print("card_self_sufficiency: 0 achados -- corpus auto-suficiente.")
        return 0
    por_padrao = Counter(a["padrao"] for a in achados)
    for a in sorted(achados, key=lambda x: (x["padrao"], x["id"] or 0)):
        print(f"[WARN] CARD_AUTOSUFICIENCIA/{a['padrao']}: card #{a['id']} "
              f"({a['area']} / {a['tema']})")
    resumo = " · ".join(f"{p}: {n}" for p, n in por_padrao.most_common())
    print(f"card_self_sufficiency: {len(achados)} achado(s) [{resumo}] "
          f"-- WARN nao bloqueia; worklist de reforja de conteudo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
