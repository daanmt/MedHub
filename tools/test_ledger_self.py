"""Suite do ledger-of-self (tools/ledger_self.py).

Cobre: emissao (opened), dedup por fingerprint (occurrences, zero linhas novas),
transicao opened->resolved->reopened (nada deletado), isolamento por check
(check que nao rodou nao resolve), corrupcao de linha JSONL (WARN, nunca crash)
e o invariante de que o modulo so escreve em history/ledger_self* (o ledger
humano AUDITORIA_MEDHUB.md e intocado).

Executavel standalone (python tools/test_ledger_self.py) e coletavel pelo pytest.
"""
import json
import sys

import pytest

from tools.ledger_self import JSONL_NAME, STATE_NAME, abertos, record, validar_jsonl


def _eventos(tmp_path):
    p = tmp_path / "history" / JSONL_NAME
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _estado(tmp_path):
    return json.loads((tmp_path / "history" / STATE_NAME).read_text(encoding="utf-8"))


ACHADO = {"alvo": "ROADMAP.md:unique taxonomia (area, tema) exists",
          "payload": {"tipo": "drift", "msg": "doc afirma exists, indice nao existe"}}


def test_warn_vira_evento_opened_com_fingerprint(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    evs = _eventos(tmp_path)
    assert len(evs) == 1 and evs[0]["event"] == "opened"
    assert evs[0]["check"] == "doc_drift" and evs[0]["fingerprint"]
    assert evs[0]["payload"]["tipo"] == "drift"
    estado = _estado(tmp_path)
    assert len(estado) == 1
    entrada = next(iter(estado.values()))
    assert entrada["status"] == "open" and entrada["occurrences"] == 1


def test_mesmo_warn_re_run_nao_duplica_e_incrementa(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    record("doc_drift", [ACHADO], root=tmp_path)
    record("doc_drift", [ACHADO], root=tmp_path)
    assert len(_eventos(tmp_path)) == 1  # zero linhas novas no jsonl
    entrada = next(iter(_estado(tmp_path).values()))
    assert entrada["occurrences"] == 3 and entrada["status"] == "open"


def test_run_limpo_resolve_sem_deletar(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    record("doc_drift", [], root=tmp_path)  # check rodou limpo
    evs = _eventos(tmp_path)
    assert [e["event"] for e in evs] == ["opened", "resolved"]
    entrada = next(iter(_estado(tmp_path).values()))
    assert entrada["status"] == "resolved" and entrada["resolved_at"]
    assert len(_estado(tmp_path)) == 1  # nada deletado


def test_reaparicao_gera_novo_opened(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    record("doc_drift", [], root=tmp_path)
    record("doc_drift", [ACHADO], root=tmp_path)  # flapping
    evs = _eventos(tmp_path)
    assert [e["event"] for e in evs] == ["opened", "resolved", "opened"]
    entrada = next(iter(_estado(tmp_path).values()))
    assert entrada["status"] == "open"


def test_check_que_nao_rodou_nao_resolve_de_outro(tmp_path):
    record("doc_drift", [ACHADO], root=tmp_path)
    record("parity", [], root=tmp_path)  # outro check, limpo
    entrada = [v for v in _estado(tmp_path).values() if v["check"] == "doc_drift"][0]
    assert entrada["status"] == "open"  # doc_drift nao rodou de novo -> intacto


def test_abertos_ordena_por_recorrencia(tmp_path):
    raro = {"alvo": "raro", "payload": {}}
    freq = {"alvo": "frequente", "payload": {}}
    record("parity", [raro, freq], root=tmp_path)
    record("parity", [raro, freq], root=tmp_path)
    record("parity", [freq], root=tmp_path)  # raro resolve, freq segue
    vivos = abertos(root=tmp_path)
    assert [v["alvo"] for v in vivos] == ["frequente"]
    assert vivos[0]["occurrences"] == 3


def test_jsonl_corrompido_warn_e_segue(tmp_path, capsys):
    record("doc_drift", [ACHADO], root=tmp_path)
    p = tmp_path / "history" / JSONL_NAME
    with p.open("a", encoding="utf-8") as f:
        f.write("{linha quebrada\n")
    eventos, corrompidas = validar_jsonl(root=tmp_path)
    assert len(eventos) == 1 and corrompidas == 1
    assert "LEDGER_SELF" in capsys.readouterr().out


def test_estado_corrompido_reinicia_sem_crash(tmp_path, capsys):
    record("doc_drift", [ACHADO], root=tmp_path)
    (tmp_path / "history" / STATE_NAME).write_text("nao-e-json", encoding="utf-8")
    record("doc_drift", [ACHADO], root=tmp_path)  # nao pode lancar
    entrada = next(iter(_estado(tmp_path).values()))
    assert entrada["status"] == "open"
    assert "LEDGER_SELF" in capsys.readouterr().out


def test_so_escreve_em_history_ledger_self(tmp_path):
    (tmp_path / "AUDITORIA_MEDHUB.md").write_text("# ledger humano\n", encoding="utf-8")
    antes = (tmp_path / "AUDITORIA_MEDHUB.md").read_text(encoding="utf-8")
    record("doc_drift", [ACHADO], root=tmp_path)
    record("doc_drift", [], root=tmp_path)
    assert (tmp_path / "AUDITORIA_MEDHUB.md").read_text(encoding="utf-8") == antes
    escritos = sorted(p.name for p in tmp_path.rglob("*") if p.is_file())
    assert escritos == sorted(["AUDITORIA_MEDHUB.md", JSONL_NAME, STATE_NAME])


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
