"""test_notas_player.py -- as regras PURAS do `--record-lote` (spec medhub-hub-v0-part-2, s193).

O que esta suite trava, em ordem de risco:

1. **Um conversor so, truncado ao segundo.** O `ts` da pagina tem milissegundos e o carimbo
   do banco nao: comparar sem truncar faz 07:17:50 < 07:17:50.144 e a mesma nota regrava.
   A nota relida bate IGUAL com a linha que ela mesma gravou.
2. **Fuso explicito.** UTC -> local com fuso INJETADO (-03:00); ts sem fuso e recusado,
   nunca adivinhado (adivinhar desloca a revisao em 3h em silencio).
3. **Idempotencia por igualdade, nunca `>=`.** JA GRAVADA so com a linha igual; revisao
   mais nova sem a igual = FORA DE ORDEM; linha ilegivel no revlog falha alto.
4. **Quarentena.** Cada tipo de doc estranho sai com o seu motivo.

Sem banco, sem relogio de parede: tudo injetado. Pytest-nativo + standalone.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.utils.notas_player import (  # noqa: E402
    FORA_DE_ORDEM,
    JA_GRAVADA,
    NOVA,
    defeito_ja_marcado,
    relogio,
    situacao,
    ultima_revisao,
    validar_nota,
)

BRT = timezone(timedelta(hours=-3))
AGORA = datetime(2026, 9, 22, 20, 0, 0)          # relogio do banco (LOCAL naive)
CARDS = {92: {"card_id": 92, "selection_reason": "vencido"},
         7: {"card_id": 7, "selection_reason": "novo"}}


def _falha(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        return str(e)
    raise AssertionError("deveria ter falhado com ValueError: %r" % (args,))


# --------------------------------------------------------------------------
# 1-2. relogio: UTC -> local, fuso injetado, truncado ao segundo
# --------------------------------------------------------------------------

def test_relogio_converte_utc_para_local_com_fuso_injetado_e_trunca():
    """A nota real do #92 (22/09): 10:17:50.144 UTC = 07:17:50 em Brasilia."""
    assert relogio("2026-09-22T10:17:50.144Z", BRT) == datetime(2026, 9, 22, 7, 17, 50)
    assert relogio("2026-09-22T10:17:50.999+00:00", BRT) == datetime(2026, 9, 22, 7, 17, 50), (
        "trunca, nao arredonda: .999 fica no mesmo segundo")
    assert relogio("2026-09-23T01:30:00Z", BRT) == datetime(2026, 9, 22, 22, 30, 0), (
        "a virada do dia UTC nao e a do dia local")


def test_relogio_recusa_ts_ausente_ilegivel_ou_sem_fuso():
    assert "ausente" in _falha(relogio, None)
    assert "ausente" in _falha(relogio, "   ")
    assert "ilegivel" in _falha(relogio, "ontem de manha")
    assert "ilegivel" in _falha(relogio, 1758536270144)
    assert "sem fuso" in _falha(relogio, "2026-09-22T07:17:50")


def test_nota_relida_bate_igual_com_a_linha_que_ela_gravou():
    """Propriedade do conversor unico: o que se grava (`quando` -> carimbo) e o que se
    compara saem do mesmo `relogio` -- a releitura cai em JA GRAVADA, nunca em NOVA."""
    quando = relogio("2026-09-22T10:17:50.144Z", BRT)
    carimbo_gravado = quando.strftime("%Y-%m-%d %H:%M:%S")      # o que o writer grava
    assert carimbo_gravado == "2026-09-22 07:17:50"
    assert situacao(relogio("2026-09-22T10:17:50.144Z", BRT), [carimbo_gravado]) == JA_GRAVADA


# --------------------------------------------------------------------------
# 3. situacao: JA GRAVADA / FORA DE ORDEM / NOVA
# --------------------------------------------------------------------------

def test_situacao_classifica_pela_igualdade_e_pela_ordem():
    t = datetime(2026, 9, 22, 7, 17, 50)
    assert situacao(t, []) == NOVA, "card sem revisao"
    assert situacao(t, ["2026-06-13 23:41:26"]) == NOVA, "so revisao mais velha"
    assert situacao(t, ["2026-06-13 23:41:26", "2026-09-22 07:17:50"]) == JA_GRAVADA
    assert situacao(t, ["2026-09-22 19:37:33"]) == FORA_DE_ORDEM, (
        "o caso real do #92: gravado as 19:37 no relogio velho, nota das 07:17")
    assert situacao(t, ["2026-09-22 07:17:50", "2026-09-23 08:00:00"]) == JA_GRAVADA, (
        "a igual vence: nota ja gravada que ganhou revisao depois nao vira FORA DE ORDEM")
    assert situacao(t, [datetime(2026, 9, 22, 7, 17, 50, 373312)]) == JA_GRAVADA, (
        "datetime do banco com microssegundos tambem trunca")


def test_situacao_nunca_usa_maior_ou_igual():
    """Objecao do `/ai-eng` (22/09): com `review_time >= ts`, a 2a nota do mesmo card
    gravada na mesma janela sumiria em silencio. Um segundo de diferenca e NOVA."""
    assert situacao(datetime(2026, 9, 22, 7, 17, 51), ["2026-09-22 07:17:50"]) == NOVA


def test_linha_ilegivel_no_revlog_falha_alto():
    assert "review_time" in _falha(situacao, datetime(2026, 9, 22), [None])
    _falha(situacao, datetime(2026, 9, 22), ["lixo"])


def test_ultima_revisao_e_defeito_ja_marcado():
    assert ultima_revisao([]) is None
    assert ultima_revisao(["2026-09-01 10:00:00", "2026-09-22 19:37:33"]) == datetime(
        2026, 9, 22, 19, 37, 33)
    t = datetime(2026, 9, 22, 7, 17, 50)
    assert defeito_ja_marcado(t, None) is False
    assert defeito_ja_marcado(t, "2026-09-22 19:37:51") is True, "marca gravada depois da nota"
    assert defeito_ja_marcado(t, "2026-09-22 07:17:50") is True, ">= basta"
    assert defeito_ja_marcado(t, "2026-09-18 12:28:10") is False, "marca de outra sessao, antes"


# --------------------------------------------------------------------------
# 4. validar_nota: a quarentena, um motivo por tipo de doc estranho
# --------------------------------------------------------------------------

def test_nota_valida_leva_quando_e_a_proveniencia_do_export():
    reg, motivo = validar_nota({"card_id": "92", "rating_primeira": 1, "ts": "2026-09-22T10:17:50.144Z",
                                "selection_reason": "mentira"}, CARDS, AGORA, BRT)
    assert motivo is None
    assert reg == {"card_id": 92, "rating": 1, "defeito": False, "motivo": "",
                   "selection_reason": "vencido", "quando": datetime(2026, 9, 22, 7, 17, 50)}


def test_cada_doc_estranho_sai_com_o_seu_motivo():
    ts = "2026-09-22T10:17:50.144Z"
    casos = [
        (["a", "b"], "nao e objeto"),
        ({"rating_primeira": 3, "ts": ts}, "sem card_id inteiro"),
        ({"card_id": 99, "rating_primeira": 3, "ts": ts}, "fora do lote"),
        ({"card_id": 92, "rating_primeira": 7, "ts": ts}, "rating invalido"),
        ({"card_id": 92, "rating_primeira": "tres", "ts": ts}, "rating invalido"),
        ({"card_id": 92, "defeito": True, "ts": ts}, "SEM motivo"),
        ({"card_id": 92, "ts": ts}, "sem rating e sem defeito"),
        ({"card_id": 92, "rating_primeira": 3}, "ts ausente"),
        ({"card_id": 92, "rating_primeira": 3, "ts": "22/09 07h"}, "ts ilegivel"),
        ({"card_id": 92, "rating_primeira": 3, "ts": "2026-09-22T07:17:50"}, "ts sem fuso"),
        ({"card_id": 92, "rating_primeira": 3, "ts": "2026-09-22T23:00:01Z"}, "ts no futuro"),
    ]
    for nota, esperado in casos:
        reg, motivo = validar_nota(nota, CARDS, AGORA, BRT)
        assert reg is None and motivo and esperado in motivo, (
            "%r deveria sair com %r, saiu %r" % (nota, esperado, motivo))


def test_defeito_sem_rating_e_valido():
    reg, motivo = validar_nota({"card_id": 7, "defeito": True, "motivo": " pergunta composta ",
                                "ts": "2026-09-22T12:00:00Z"}, CARDS, AGORA, BRT)
    assert motivo is None and reg["rating"] is None and reg["defeito"] is True
    assert reg["motivo"] == "pergunta composta"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
