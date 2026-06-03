"""test_fsrs.py - vetores de teste do adapter FSRS (app/utils/fsrs.py).

Valida que o adapter sobre py-fsrs (referencia: open-spaced-repetition/py-fsrs,
pinado em requirements.txt como fsrs>=6.3.1) preserva a interface esperada por
record_review e produz agendamento fiel. Standalone: `python tools/test_fsrs.py`.
"""
import os
import sys
from datetime import datetime, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.fsrs import FSRS, _SCHEDULER, REQUEST_RETENTION
from fsrs import Card, Rating

EXPECTED_KEYS = {"state", "stability", "difficulty", "elapsed_days",
                 "scheduled_days", "reps", "lapses", "last_review", "due"}

GOOD, AGAIN, EASY = 3, 1, 4
_fails = []


def check(name, cond):
    print(f"  [{'OK' if cond else 'FAIL'}] {name}")
    if not cond:
        _fails.append(name)


def _aged(card):
    """Recua last_review para simular revisao no vencimento (elapsed > 0)."""
    card = dict(card)
    card["last_review"] = datetime.now() - timedelta(days=max(1, card["scheduled_days"]))
    return card


def main():
    print("== test_fsrs (adapter py-fsrs, retention=%.2f) ==" % REQUEST_RETENTION)
    fsrs = FSRS()

    # 1. New + Good: shape, chaves, invariantes basicos
    r = fsrs.evaluate(fsrs.init_card(), GOOD)
    check("1. retorna exatamente as 9 chaves", set(r.keys()) == EXPECTED_KEYS)
    check("1. state graduou para Review (2)", r["state"] == 2)
    check("1. stability > 0", r["stability"] > 0)
    check("1. scheduled_days >= 1 (intervalo em dias)", r["scheduled_days"] >= 1)
    check("1. elapsed_days == 0 (card novo)", r["elapsed_days"] == 0)
    check("1. reps == 1, lapses == 0", r["reps"] == 1 and r["lapses"] == 0)

    # 2. Easy gera mais estabilidade que Good (card novo)
    r_good = fsrs.evaluate(fsrs.init_card(), GOOD)
    r_easy = fsrs.evaluate(fsrs.init_card(), EASY)
    check("2. stability(Easy) > stability(Good)", r_easy["stability"] > r_good["stability"])

    # 3. Good no vencimento x3: estabilidade cresce (elapsed > 0)
    c = fsrs.evaluate(fsrs.init_card(), GOOD)
    stabs = [c["stability"]]
    for _ in range(2):
        c = fsrs.evaluate(_aged(c), GOOD)
        stabs.append(c["stability"])
    check("3. stability cresce em Good no vencimento", stabs[-1] > stabs[0])
    check("3. scheduled_days cresce", c["scheduled_days"] > r_good["scheduled_days"])

    # 4. Again em card graduado (Review) -> Relearning + lapse
    c = fsrs.evaluate(fsrs.init_card(), GOOD)   # -> Review (2)
    state_antes, lapses_antes = c["state"], c["lapses"]
    c = fsrs.evaluate(_aged(c), AGAIN)
    check("4. graduou para Review antes do Again", state_antes == 2)
    check("4. Again em Review -> Relearning (3)", c["state"] == 3)
    check("4. lapse incrementado", c["lapses"] == lapses_antes + 1)

    # 5. Again em card NOVO nao conta como lapse
    r = fsrs.evaluate(fsrs.init_card(), AGAIN)
    check("5. Again em card novo -> lapses == 0", r["lapses"] == 0)

    # 6. Fidelidade: stability(new, Good) == py-fsrs de referencia
    ref_card, _ = _SCHEDULER.review_card(Card(), Rating.Good)
    ours = fsrs.evaluate(fsrs.init_card(), GOOD)
    check("6. stability bate com py-fsrs de referencia",
          abs(ours["stability"] - ref_card.stability) < 1e-9)

    print("\nRESULTADO:", "OK - todos passaram" if not _fails else f"FALHAS: {_fails}")
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(main())
