"""Suite do rito de REFLECTION (tools/reflect.py).

Cobre: sem-sinal honesto (ledger vazio/estavel), datum com evidencia
(fingerprint + contagem), recusa de proposta sem evidencia integra,
idempotencia de leitura (2 runs sem mudanca -> 2o e sem-sinal), escrita
restrita ao proprio datum (snapshot de filesystem) e input corrompido ->
WARN + sem-sinal, nunca crash.

Executavel standalone (python tools/test_reflect.py) e coletavel pelo pytest.
"""
import json
import sys

import pytest

from tools.ledger_self import STATE_NAME, record
from tools.reflect import DATA_NAME, SEM_SINAL, run_reflect

ACHADO = {"alvo": "ROADMAP.md:claim-x", "payload": {"tipo": "drift"}}


def _data(tmp_path):
    p = tmp_path / "history" / DATA_NAME
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def test_ledger_vazio_datum_sem_sinal_sem_proposta(tmp_path):
    datum = run_reflect(root=tmp_path)
    assert datum["resumo"] == SEM_SINAL and datum["sinal"] is False
    assert datum["proposta"] is None
    assert len(_data(tmp_path)) == 1  # datum gravado mesmo sem sinal


def test_achado_recorrente_datum_cita_evidencia(tmp_path):
    for _ in range(3):
        record("doc_drift", [ACHADO], root=tmp_path)
    datum = run_reflect(root=tmp_path)
    assert datum["sinal"] is True
    assert datum["achados"][0]["occurrences"] == 3
    fp = datum["achados"][0]["fingerprint"]
    assert datum["proposta"]["evidencia"] == [fp]
    assert datum["proposta"]["score_recorrencia"] == 3
    assert fp in datum["resumo"]


def test_idempotencia_segundo_run_sem_mudanca_e_sem_sinal(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    d1 = run_reflect(root=tmp_path)
    d2 = run_reflect(root=tmp_path)  # ledger inalterado entre os runs
    assert d1["sinal"] is True
    assert d2["sinal"] is False and d2["resumo"] == SEM_SINAL
    assert d2["proposta"] is None


def test_recorrencia_sem_evento_novo_e_sinal(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    run_reflect(root=tmp_path)
    record("doc_drift", [ACHADO], root=tmp_path)  # occurrences 1->2; zero eventos novos
    datum = run_reflect(root=tmp_path)
    assert datum["sinal"] is True and datum["proposta"]["score_recorrencia"] == 2


def test_evidencia_ausente_recusa_proposta(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    # corrompe a integridade do candidato: occurrences invalida
    state_p = tmp_path / "history" / STATE_NAME
    state = json.loads(state_p.read_text(encoding="utf-8"))
    for v in state.values():
        v["occurrences"] = "nao-e-numero"
    state_p.write_text(json.dumps(state), encoding="utf-8")
    datum = run_reflect(root=tmp_path)
    assert datum["sinal"] is True          # evento opened existe na janela
    assert datum["proposta"] is None       # mas nao ha candidato integro
    assert "anti-fabricacao" in datum["resumo"]


def test_escreve_apenas_o_proprio_datum(tmp_path):
    (tmp_path / "AUDITORIA_MEDHUB.md").write_text("# humano\n", encoding="utf-8")
    record("doc_drift", [ACHADO], root=tmp_path)
    antes = {p: p.stat().st_mtime_ns for p in tmp_path.rglob("*") if p.is_file()}
    run_reflect(root=tmp_path)
    depois = {p for p in tmp_path.rglob("*") if p.is_file()}
    novos = depois - set(antes)
    assert novos == {tmp_path / "history" / DATA_NAME}
    mudados = [p for p, m in antes.items() if p.stat().st_mtime_ns != m]
    assert mudados == []  # nada pre-existente tocado


def test_input_corrompido_warn_e_sem_crash(tmp_path, capsys):
    hist = tmp_path / "history"
    hist.mkdir()
    (hist / "ledger_self.jsonl").write_text("{quebrado\n", encoding="utf-8")
    datum = run_reflect(root=tmp_path)  # nao pode lancar
    assert datum["resumo"] == SEM_SINAL
    assert "LEDGER_SELF" in capsys.readouterr().out  # WARN visivel


def test_datum_corrompido_no_historico_ignorado(tmp_path, capsys):
    record("doc_drift", [ACHADO], root=tmp_path)
    run_reflect(root=tmp_path)
    p = tmp_path / "history" / DATA_NAME
    with p.open("a", encoding="utf-8") as f:
        f.write("nao-e-json\n")
    datum = run_reflect(root=tmp_path)  # janela cai no ultimo datum VALIDO
    assert datum["sinal"] is False
    assert "REFLECT" in capsys.readouterr().out


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
