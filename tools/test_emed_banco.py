"""Testes de tools/emed_banco.py + app/utils/db.py::emed_* (banco de questões EMED).

Banco sintético em `tmp_path` (padrão do `test_plano.py`): `db.DB_PATH` é
monkeypatchado, o `ipub.db` real NUNCA é tocado. Os docs imitam o layout do
`ArtifactData list ... out_dir`: `<DIR>/<colecao>/<doc_id>.json`.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from app.utils import db  # noqa: E402
import emed_banco  # noqa: E402


# ------------------------------------------------------------------- fixtures

def _usar_db(tmp_path, monkeypatch):
    """Aponta `db.DB_PATH` para um banco novo em tmp (restaurado pelo monkeypatch)."""
    caminho = str(tmp_path / "emed.db")
    monkeypatch.setattr(db, "DB_PATH", caminho)
    return caminho


def _questao(num, **extra):
    """Doc `questoes` sintético com a forma do real."""
    doc = {"lista": "t26", "tarefa": 26, "num": num, "banca": "UERJ 2024",
           "gabarito": "B", "emed_id": f"e{num}",
           "enunciado": f"Gestante de 28 semanas com glicemia de jejum alterada ({num}).",
           "alternativas": "A) Dieta\nB) Insulina\nC) Metformina\nD) Glibenclamida",
           "solucao": "Insulina é a primeira escolha.", "forum": "", "tags": "Obstetrícia",
           "estatistica": "62% de acerto", "capturado_em": "2026-09-25T10:00:00",
           "executor": "claude-chrome"}
    doc.update(extra)
    return doc


def _escrever(base, colecao, doc_id, doc):
    """Grava um doc em `<base>/<colecao>/<doc_id>.json`."""
    pasta = base / colecao
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{doc_id}.json").write_text(json.dumps(doc, ensure_ascii=False),
                                          encoding="utf-8")


def _tabelas(caminho):
    """Nomes das tabelas `emed_*` presentes no banco."""
    con = sqlite3.connect(caminho)
    try:
        return {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'emed_%'")}
    finally:
        con.close()


def _json_saida(capsys):
    """Última saída do stdout parseada como JSON."""
    return json.loads(capsys.readouterr().out)


# ------------------------------------------------------------------- testes

def test_ingerir_idempotente(tmp_path, monkeypatch, capsys):
    """3 novas; 2a rodada 3 iguais; alterar `solucao` de uma -> 1 atualizada."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    for n in (1, 2, 3):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (3, 0, 0)
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 3)
    _escrever(base, "questoes", "t26_2", _questao(2, solucao="Nova solução com acento."))
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 1, 2)
    q2 = [q for q in db.emed_listar_questoes("t26") if q["num"] == 2][0]
    assert q2["solucao"] == "Nova solução com acento."


def test_dry_run_nao_cria_tabela(tmp_path, monkeypatch, capsys):
    """Dry-run conta mas não roda DDL: `sqlite_master` segue sem `emed_*`."""
    caminho = _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "questoes", "t26_1", _questao(1))
    assert emed_banco.main(["--ingerir", str(base), "--json"]) == 0
    assert _json_saida(capsys)["novas"] == 1
    assert _tabelas(caminho) == set()


def test_expect_divergente_nao_grava(tmp_path, monkeypatch, capsys):
    """`--expect` errado -> exit 2 e nada gravado (nem a tabela)."""
    caminho = _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    for n in (1, 2):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--expect", "5"]) == 2
    assert "COUNT-ASSERT" in capsys.readouterr().out
    assert _tabelas(caminho) == set()
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--expect", "2"]) == 0
    assert len(db.emed_listar_questoes()) == 2


def test_doc_sem_gabarito_invalido_resto_grava(tmp_path, monkeypatch, capsys):
    """Doc sem `gabarito` vai para `invalidas`; os outros gravam."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "questoes", "t26_1", _questao(1))
    ruim = _questao(2)
    del ruim["gabarito"]
    _escrever(base, "questoes", "t26_2", ruim)
    _escrever(base, "questoes", "t26_3", _questao(3, estatistica=None))
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert c["novas"] == 2 and c["invalidas"] == ["t26_2"]
    assert sorted(q["num"] for q in db.emed_listar_questoes()) == [1, 3]


def test_registrar_contagens_resumo_e_ordem_temporal(tmp_path, monkeypatch, capsys):
    """1 certa sólida + 1 errada chute; `correta` calculada; antiga não sobrescreve."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    for n in (1, 7):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    capsys.readouterr()
    _escrever(base, "respostas", "t26_1", {
        "lista": "t26", "tarefa": 26, "num": 1, "letra": "B", "confianca": "solida",
        "correta": True, "gabarito": "B", "racional": "insulina", "elo": "",
        "tempo_s": 60, "flag": False, "respondido_em": "2026-09-25T11:00:00"})
    _escrever(base, "respostas", "t26_7", {   # sem `correta` nem `gabarito`: calcula
        "lista": "t26", "tarefa": 26, "num": 7, "letra": "C", "confianca": "chute",
        "racional": "achei que metformina", "elo": "1a linha", "tempo_s": 120,
        "respondido_em": "2026-09-25T11:05:00"})
    assert emed_banco.main(["--registrar", str(base), "--apply"]) == 0
    saida = capsys.readouterr().out
    assert "novas=2" in saida
    assert "feitas 2 · acertos 1 (solidas 1, duvidas 0, chutes 1)" in saida
    assert "erradas: 7" in saida and "tempo medio 90s" in saida
    assert '--feitas 2 --acertos 1 --tarefa 26 --obs "EMED t26 via Bancada"' in saida
    r7 = [r for r in db.emed_listar_respostas("t26") if r["num"] == 7][0]
    assert r7["correta"] == 0
    # resposta mais ANTIGA no arquivo nao sobrescreve a mais nova do banco
    _escrever(base, "respostas", "t26_7", {
        "lista": "t26", "num": 7, "letra": "B", "confianca": "solida",
        "respondido_em": "2026-09-24T09:00:00"})
    assert emed_banco.main(["--registrar", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 2)
    r7 = [r for r in db.emed_listar_respostas("t26") if r["num"] == 7][0]
    assert (r7["letra"], r7["correta"]) == ("C", 0)


def test_podar_questoes_so_hash_igual(tmp_path, monkeypatch, capsys):
    """Só docs com hash igual ao banco entram em `ids`; alterado vai a `nao_seguros`."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    for n in (1, 2):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    _escrever(base, "questoes", "t26_2", _questao(2, forum="comentário novo"))
    _escrever(base, "questoes", "t26_3", _questao(3))     # nunca ingerida
    capsys.readouterr()
    assert emed_banco.main(["--podar", str(base)]) == 0
    arq = json.loads((base / "podar_questoes.json").read_text(encoding="utf-8"))
    assert arq["colecao"] == "questoes" and arq["ids"] == ["t26_1"] and arq["n"] == 1
    assert sorted(arq["nao_seguros"]) == ["t26_2", "t26_3"]


def test_exportar_round_trip(tmp_path, monkeypatch, capsys):
    """exportar -> ingerir de novo = tudo `iguais`, mesmos campos do doc."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    for n in (1, 2):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    _escrever(base, "questoes", "t26_3", _questao(3, tarefa=None, estatistica=None))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 0
    arquivos = sorted(p.name for p in (out / "questoes").glob("*.json"))
    assert arquivos == ["t26_1.json", "t26_2.json", "t26_3.json"]
    doc = json.loads((out / "questoes" / "t26_1.json").read_text(encoding="utf-8"))
    assert set(doc) == set(_questao(1))
    assert doc["tags"] == "Obstetrícia"
    capsys.readouterr()
    assert emed_banco.main(["--ingerir", str(out), "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 3)


def test_erros_status_e_leitura_sem_tabela(tmp_path, monkeypatch, capsys):
    """`--status`/`--erros` em banco vazio não quebram; com dados, erro+chute aparecem."""
    caminho = _usar_db(tmp_path, monkeypatch)
    assert emed_banco.main(["--status", "--json"]) == 0
    assert _json_saida(capsys) == []
    assert _tabelas(caminho) == set()
    base = tmp_path / "buf"
    for n in (1, 2, 3):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    resp = {1: ("B", "solida"), 2: ("B", "chute"), 3: ("A", "duvida")}
    for n, (letra, conf) in resp.items():
        _escrever(base, "respostas", f"t26_{n}", {
            "lista": "t26", "tarefa": 26, "num": n, "letra": letra, "confianca": conf,
            "tempo_s": 30, "respondido_em": "2026-09-25T12:00:00"})
    emed_banco.main(["--ingerir", str(base), "--apply"])
    emed_banco.main(["--registrar", str(base), "--apply"])
    capsys.readouterr()
    assert emed_banco.main(["--erros", "t26", "--json"]) == 0
    assert [e["num"] for e in _json_saida(capsys)] == [2, 3]
    assert emed_banco.main(["--status", "--lista", "t26", "--json"]) == 0
    s = _json_saida(capsys)[0]
    assert (s["capturadas"], s["respondidas"], s["acertos"], s["erradas"]) == (3, 3, 2, 1)
    assert s["area"] is None   # plano_tarefas ausente: tolerado


def test_uso_invalido_e_pasta_ausente(tmp_path, monkeypatch):
    """Nenhum modo ou pasta inexistente -> exit 1."""
    _usar_db(tmp_path, monkeypatch)
    assert emed_banco.main([]) == 1
    assert emed_banco.main(["--ingerir", str(tmp_path / "nao_existe")]) == 1


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
