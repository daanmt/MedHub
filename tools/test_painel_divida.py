"""Descolar part-1 (F54/P5): painel de DIVIDA — o leitor obrigatorio do ledger-of-self.

Asserts nativos, fixtures sinteticas em tmp_path (zero db real, zero rede). Cobre:
ordenacao idade x ocorrencias, tail do memory_errors.log, resiliencia (estado ausente).
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ledger_self import painel_divida  # noqa: E402


def _estado(tmp_path, entradas):
    hist = tmp_path / "history"
    hist.mkdir(parents=True, exist_ok=True)
    (hist / "ledger_self_state.json").write_text(
        json.dumps(entradas, ensure_ascii=False), encoding="utf-8")


def _iso_ha(dias):
    return (datetime.now(timezone.utc) - timedelta(days=dias)).isoformat(timespec="seconds")


def test_painel_ordena_por_idade_x_ocorrencias(tmp_path):
    _estado(tmp_path, {
        "aaa": {"check": "card_atomicidade", "alvo": "card#1", "status": "open",
                "opened_at": _iso_ha(2), "occurrences": 3},       # score ~6
        "bbb": {"check": "doc_drift", "alvo": "HANDOFF.md:x", "status": "open",
                "opened_at": _iso_ha(40), "occurrences": 100},    # score ~4000 (o F54 real)
        "ccc": {"check": "parity", "alvo": "cmd<->skill", "status": "resolved",
                "opened_at": _iso_ha(90), "occurrences": 999},    # resolvido: fora
    })
    linhas = painel_divida(root=tmp_path)
    assert linhas[0].startswith("== DIVIDA ==") and "2 aberto(s)" in linhas[0]
    assert "doc_drift" in linhas[1]          # o antigo-e-frequente vem PRIMEIRO
    assert "card_atomicidade" in linhas[2]
    assert not any("parity" in l for l in linhas)   # resolvido nao aparece


def test_painel_mostra_memory_errors_e_auditoria(tmp_path):
    _estado(tmp_path, {})
    (tmp_path / "history" / "memory_errors.log").write_text(
        "erro antigo\nno such table: questoes_erros\n", encoding="utf-8")
    (tmp_path / "AUDITORIA_MEDHUB.md").write_text("x" * 2048, encoding="utf-8")
    linhas = painel_divida(root=tmp_path)
    assert any("memory_errors.log: 2 linha(s)" in l and "questoes_erros" in l for l in linhas)
    assert any("AUDITORIA_MEDHUB.md: 2 KB" in l for l in linhas)


def test_painel_resiliente_sem_estado(tmp_path):
    linhas = painel_divida(root=tmp_path)   # nada existe
    assert linhas and linhas[0].startswith("== DIVIDA ==")


def test_painel_agrupa_o_resto_por_check(tmp_path):
    entradas = {f"fp{i}": {"check": "card_atomicidade", "alvo": f"card#{i}", "status": "open",
                           "opened_at": _iso_ha(10), "occurrences": 5} for i in range(8)}
    _estado(tmp_path, entradas)
    linhas = painel_divida(root=tmp_path, top=5)
    assert any(l.startswith("  (+3 abertos:") and "card_atomicidade: 3" in l for l in linhas)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
