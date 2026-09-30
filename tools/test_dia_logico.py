"""F141 (s207): um relogio so para "um dia" -- o DIA LOGICO (data local).

O defeito: o py-fsrs mede o decorrido por 24 h truncadas e a fila serve por dia-calendario.
O card 638 visto em 27/09 16:56 e servido em 28/09 14:24 (21,5 h) caiu no ramo de "mesmo
dia" e a estabilidade caiu 0,212 -> 0,083. Estes testes travam: (1) a funcao unica,
(2) o adapter contando dias logicos, (3) a entrada do Optimizer no mesmo relogio.
"""
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils.fsrs import FSRS  # noqa: E402
from app.utils.relogio import dia_logico, dias_entre  # noqa: E402
import fsrs_optimize  # noqa: E402


# --- 1. a funcao unica -------------------------------------------------------

def test_dia_logico_aceita_carimbo_datetime_e_date():
    assert dia_logico("2026-09-28 14:24:00") == date(2026, 9, 28)
    assert dia_logico("2026-09-28T23:59:59.5") == date(2026, 9, 28)
    assert dia_logico(datetime(2026, 9, 28, 0, 0, 1)) == date(2026, 9, 28)
    assert dia_logico(date(2026, 9, 28)) == date(2026, 9, 28)


def test_dia_logico_de_instante_com_fuso_usa_a_zona_local():
    utc = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
    assert dia_logico(utc) == utc.astimezone().date()


@pytest.mark.parametrize("ruim", [None, "", "lixo", 42])
def test_dia_logico_falha_alto(ruim):
    with pytest.raises(ValueError):
        dia_logico(ruim)


def test_dias_entre_conta_a_virada_nao_as_24h():
    assert dias_entre("2026-09-27 16:56:00", "2026-09-28 14:24:00") == 1   # 21,5 h
    assert dias_entre("2026-09-27 23:59:00", "2026-09-28 00:01:00") == 1   # 2 min
    assert dias_entre("2026-09-28 00:01:00", "2026-09-28 23:59:00") == 0   # ~24 h
    assert dias_entre("2026-09-20 22:00:00", "2026-09-26 08:00:00") == 6   # 5 d 10 h


# --- 2. o adapter ------------------------------------------------------------

def _card_revisado(ultima):
    return {"card_id": 638, "state": 2, "stability": 0.212, "difficulty": 6.0,
            "due": ultima + timedelta(days=1), "last_review": ultima, "reps": 1, "lapses": 1}


def test_card_de_1_dia_servido_na_manha_seguinte_nao_cai_no_ramo_curto():
    """O caso 638: 21,5 h depois e UM dia logico -- mesmo resultado que 25 h depois."""
    ultima = datetime(2026, 9, 27, 16, 56, 0)
    f = FSRS()
    manha = f.evaluate(_card_revisado(ultima), 3, quando=datetime(2026, 9, 28, 14, 24, 0))
    noite = f.evaluate(_card_revisado(ultima), 3, quando=datetime(2026, 9, 28, 17, 56, 0))
    assert manha["elapsed_days"] == noite["elapsed_days"] == 1
    assert manha["stability"] == pytest.approx(noite["stability"])
    assert manha["difficulty"] == pytest.approx(noite["difficulty"])


def test_mesmo_dia_logico_segue_no_ramo_curto():
    ultima = datetime(2026, 9, 28, 8, 0, 0)
    f = FSRS()
    mesmo = f.evaluate(_card_revisado(ultima), 3, quando=datetime(2026, 9, 28, 20, 0, 0))
    outro = f.evaluate(_card_revisado(ultima), 3, quando=datetime(2026, 9, 29, 8, 0, 0))
    assert mesmo["elapsed_days"] == 0 and outro["elapsed_days"] == 1
    assert mesmo["stability"] != pytest.approx(outro["stability"])


def test_last_review_gravado_e_o_real_nao_o_da_biblioteca():
    """Revlog e fsrs_cards intactos: o adapter devolve o instante REAL da revisao."""
    q = datetime(2026, 9, 28, 14, 24, 0)
    out = FSRS().evaluate(_card_revisado(datetime(2026, 9, 27, 16, 56, 0)), 3, quando=q)
    assert out["last_review"] == q


def test_revisao_anterior_a_ultima_segue_recusada():
    ultima = datetime(2026, 9, 28, 14, 0, 0)
    with pytest.raises(ValueError):
        FSRS().evaluate(_card_revisado(ultima), 3, quando=datetime(2026, 9, 28, 13, 0, 0))


# --- 3. a entrada do Optimizer ----------------------------------------------

def test_optimizer_recebe_a_revisao_no_00h_do_dia_logico():
    a = fsrs_optimize.no_dia_logico(datetime(2026, 9, 27, 23, 50, tzinfo=timezone.utc))
    b = fsrs_optimize.no_dia_logico(datetime(2026, 9, 28, 0, 10, tzinfo=timezone.utc))
    c = fsrs_optimize.no_dia_logico(datetime(2026, 9, 28, 23, 50, tzinfo=timezone.utc))
    assert (b - a).days == 1, "virada de dia com 20 min tem de contar 1 dia"
    assert (c - b).days == 0, "mesmo dia logico com ~24 h tem de contar 0"
    assert a.tzinfo is not None
