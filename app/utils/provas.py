"""Leitor UNICO de `core/provas.json` (F88, hotfix 2026-09-09; rider b do F71).

Antes havia dois parsers do mesmo arquivo -- `tools/day_plan.carregar_provas` (countdown do
boot) e `app/utils/db.blackout_provas` (balanceador FSRS, F71) -- a mesma classe de defeito
do F88 (duas fontes para o mesmo numero). Este modulo e a fonte: vive em `app/` porque a
camada `app/` nao pode importar `tools/` sem inverter a dependencia; `tools/day_plan.py`
re-exporta `carregar_provas`/`PROVAS_PATH` daqui (assinatura e WARNs preservados -- a suite
`tools/test_provas.py` continua valendo).

Parser TOLERANTE por contrato: arquivo ausente, ilegivel, JSON invalido ou entrada malformada
emitem WARN em **stderr** e sao ignorados -- nem o plano do dia nem o `fsrs_queue --record`
(stdout JSON puro) quebram por causa do calendario. Pior caso = lista vazia / blackout vazio.
"""
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROVAS_PATH = os.path.join(ROOT, "core", "provas.json")


def carregar_provas(path=None):
    """Le core/provas.json -> [{nome, data(date), tipo}] ordenado por data.

    Parser TOLERANTE por contrato: arquivo ausente, ilegivel, JSON invalido ou
    entrada malformada emitem WARN em stderr e sao ignorados -- o plano do dia
    nunca quebra por causa do countdown (mesmo espirito da degradacao graciosa
    do cronograma). Pior caso = lista vazia.
    """
    alvo = path or PROVAS_PATH
    try:
        with open(alvo, encoding="utf-8") as fh:
            dados = json.load(fh)
    except FileNotFoundError:
        print(f"[WARN] PROVAS_AUSENTE: {alvo} nao encontrado -- plano segue sem countdown.",
              file=sys.stderr)
        return []
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, ValueError) as e:
        print(f"[WARN] PROVAS_ILEGIVEL: {alvo} ({e}) -- plano segue sem countdown.",
              file=sys.stderr)
        return []
    if not isinstance(dados, list):
        print(f"[WARN] PROVAS_FORMATO: {alvo} nao contem uma lista -- plano segue sem countdown.",
              file=sys.stderr)
        return []
    provas = []
    for i, item in enumerate(dados):
        if not isinstance(item, dict):
            print(f"[WARN] PROVAS_ENTRADA: item {i} nao e objeto -- ignorado.", file=sys.stderr)
            continue
        nome, bruto = item.get("nome"), item.get("data")
        tipo = item.get("tipo") or "prova"
        try:
            quando = date.fromisoformat(str(bruto))
        except (ValueError, TypeError):
            print(f"[WARN] PROVAS_DATA: '{nome or i}' com data invalida ({bruto!r}) -- ignorado.",
                  file=sys.stderr)
            continue
        if not nome:
            print(f"[WARN] PROVAS_NOME: item {i} sem nome -- ignorado.", file=sys.stderr)
            continue
        provas.append({"nome": str(nome), "data": quando, "tipo": str(tipo)})
    return sorted(provas, key=lambda p: p["data"])


def datas_de_prova(provas=None, path=None):
    """Datas das entradas `tipo == "prova"` (o fecho de grade nao e prova)."""
    itens = provas if provas is not None else carregar_provas(path)
    return [p["data"] for p in itens if p.get("tipo") == "prova"]


def blackout_provas(path=None, provas=None):
    """Dias a evitar no agendamento FSRS (F71): dia de cada prova + o seguinte.
    A regra de quantos dias entram e de `app.utils.fsrs_balance.blackout_de` (pura)."""
    from app.utils.fsrs_balance import blackout_de
    return blackout_de(datas_de_prova(provas, path))
