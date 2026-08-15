"""Suite da condicao B1 do reconcile -- teto do HANDOFF (spec consolidacao-part-4).

B1 (`HANDOFF.md > 60 linhas`) era declarada BLOCKING no contrato desde a s075 e
nunca existiu em codigo: o HANDOFF passou de 60 e nada bloqueou (achado D3/s144,
"warning-first virou warning-only"). Estes testes travam a promocao a BLOCKING
de fato -- inclusive a fronteira (60 passa, 61 bloqueia) e o modo defensivo.

Fixtures 100%% sinteticas: HANDOFFs de mentira em tmp_path, zero conteudo real.
Executavel standalone (python tools/test_handoff_teto.py) e coletavel pelo pytest.
"""
import pytest

from tools.auto_check import LIMITE_HANDOFF, check_handoff_len


def _handoff(tmp_path, n_linhas, nome="HANDOFF.md"):
    alvo = tmp_path / nome
    alvo.write_text("\n".join(f"linha {i}" for i in range(n_linhas)), encoding="utf-8")
    return str(alvo)


def test_dentro_do_teto_passa(tmp_path):
    assert check_handoff_len(_handoff(tmp_path, 10)) is None


def test_fronteira_exata_nao_bloqueia(tmp_path):
    """60 linhas e o teto contratual, nao o estouro."""
    assert check_handoff_len(_handoff(tmp_path, LIMITE_HANDOFF)) is None


def test_uma_linha_acima_bloqueia(tmp_path):
    estouro = check_handoff_len(_handoff(tmp_path, LIMITE_HANDOFF + 1))
    assert estouro == (LIMITE_HANDOFF + 1, LIMITE_HANDOFF)


def test_conta_linhas_fisicas(tmp_path):
    assert check_handoff_len(_handoff(tmp_path, 120))[0] == 120


def test_limite_customizavel(tmp_path):
    assert check_handoff_len(_handoff(tmp_path, 12), limite=10) == (12, 10)
    assert check_handoff_len(_handoff(tmp_path, 12), limite=20) is None


def test_arquivo_ausente_e_silencioso(tmp_path):
    """Sem HANDOFF -> None. Nunca falso-positivo barulhento (regra dos irmaos F1/POSICAO)."""
    assert check_handoff_len(str(tmp_path / "nao-existe.md")) is None


def test_teto_do_contrato_e_60():
    assert LIMITE_HANDOFF == 60


def test_handoff_real_esta_dentro_do_teto():
    """Regressao viva: se o HANDOFF do repo estourar, esta suite cai junto com o harness."""
    assert check_handoff_len() is None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
