"""Testes de tools/emed_banco.py + app/utils/db.py::emed_* (banco de questões EMED).

Banco sintético em `tmp_path` (padrão do `test_plano.py`): `db.DB_PATH` é
monkeypatchado, o `ipub.db` real NUNCA é tocado. Os docs imitam o layout do
`ArtifactData list ... out_dir`: `<DIR>/<colecao>/<doc_id>.json`.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

import pytest

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
    # s219: a banca era "UERJ 2024" -- spoiler de simulado, que o `--exportar` agora segura
    doc = {"lista": "t26", "tarefa": 26, "num": num, "banca": "SES-DF 2024",
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

def test_extras_vao_para_coluna_e_voltam_no_export(tmp_path, monkeypatch, capsys):
    """Chave sem coluna (acerto_pct, video...) vira JSON em `extras`; o `--exportar`
    devolve as chaves soltas e a re-ingestão dá `iguais` (hash estável nos 2 caminhos)."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "questoes", "t26_1", _questao(1, acerto_pct=93, video=True,
                                                   alternativas_pct="A 2% B 93% C 5%"))
    _escrever(base, "questoes", "t26_2", _questao(2))
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["novas"] == 2
    q1, q2 = db.emed_listar_questoes("t26")
    assert json.loads(q1["extras"]) == {"acerto_pct": 93, "video": True,
                                        "alternativas_pct": "A 2% B 93% C 5%"}
    assert q2["extras"] == ""
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out),
                            "--sem-cadeia", "teste: extras e hash, sem Solucao"]) == 0
    capsys.readouterr()
    doc1 = json.loads((out / "questoes" / "t26_1.json").read_text(encoding="utf-8"))
    assert doc1["acerto_pct"] == 93 and doc1["video"] is True and "extras" not in doc1
    assert emed_banco.main(["--ingerir", str(out), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 2)
    # mudar um extra conta como atualizada (o hash cobre `extras`)
    _escrever(base, "questoes", "t26_1", _questao(1, acerto_pct=40))
    assert emed_banco.main(["--ingerir", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["atualizadas"] == 1


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
    assert emed_banco.main(["--exportar", "t26", "--out", str(out),
                            "--sem-cadeia", "teste: round trip do doc, sem Solucao"]) == 0
    arquivos = sorted(p.name for p in (out / "questoes").glob("*.json"))
    assert arquivos == ["t26_1.json", "t26_2.json", "t26_3.json"]
    doc = json.loads((out / "questoes" / "t26_1.json").read_text(encoding="utf-8"))
    assert set(doc) == set(_questao(1))
    assert doc["tags"] == "Obstetrícia"
    capsys.readouterr()
    assert emed_banco.main(["--ingerir", str(out), "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 3)


def test_exportar_nao_reenvia_spoiler_uerj_de_lista_do_emed(tmp_path, monkeypatch, capsys):
    """Regressao da s219 (07/10/2026): 37 questoes UERJ 2022-2026 sairam das listas do hub e ficaram
    no ipub.db; o `--exportar` nao pode semea-las de volta. A prova da UERJ em si (`prova_pdf`) e o
    simulado e sai inteira."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    hupe = "RJ - Universidade do Estado do Rio de Janeiro - UERJ (Hospital Universitário Pedro Ernesto - HUPE)"
    _escrever(base, "questoes", "t26_1", _questao(1))
    _escrever(base, "questoes", "t26_2", _questao(2, banca=f"{hupe}, 2022", executor="emed_api"))
    _escrever(base, "questoes", "t26_3", _questao(3, banca=f"{hupe}, 2019", executor="emed_api"))
    _escrever(base, "questoes", "t1794_1", _questao(1, lista="t1794", tarefa=1794, banca="UERJ 2022",
                                                     executor="prova_pdf"))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    capsys.readouterr()
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out),
                            "--sem-cadeia", "teste: regra do spoiler, sem Solucao"]) == 0
    assert "spoiler UERJ fora: [2]" in capsys.readouterr().out
    assert sorted(p.name for p in (out / "questoes").glob("t26_*.json")) == ["t26_1.json", "t26_3.json"]
    assert json.loads((out / "listas" / "t26.json").read_text(encoding="utf-8"))["q"] == 2
    assert emed_banco.main(["--exportar", "t1794", "--out", str(out),
                            "--sem-cadeia", "teste: prova sem plano semeado"]) == 0
    assert (out / "questoes" / "t1794_1.json").is_file()


def test_contagem_no_hub_por_tarefa_e_a_do_exportar(tmp_path, monkeypatch, capsys):
    """P20 (s219): a Teoria e o Painel contam as questoes da tarefa pelo MESMO criterio do `--exportar`
    (o que a aba Listas recebe): o spoiler UERJ 2022-2026 de lista do EMED fica fora; a prova em PDF
    conta inteira. Uma regra so (`fora_do_hub`), usada pelos dois."""
    _usar_db(tmp_path, monkeypatch)
    assert emed_banco.questoes_no_hub_por_tarefa() == {}, "banco sem a tabela = nada no hub"
    base = tmp_path / "buf"
    hupe = "RJ - Universidade do Estado do Rio de Janeiro - UERJ (Hospital Universitário Pedro Ernesto - HUPE)"
    _escrever(base, "questoes", "t26_1", _questao(1))
    _escrever(base, "questoes", "t26_2", _questao(2, banca=f"{hupe}, 2022", executor="emed_api"))
    _escrever(base, "questoes", "t26_3", _questao(3, banca=f"{hupe}, 2019", executor="emed_api"))
    _escrever(base, "questoes", "t1794_1", _questao(1, lista="t1794", tarefa=1794, banca="UERJ 2022",
                                                     executor="prova_pdf"))
    _escrever(base, "questoes", "t1794_2", _questao(2, lista="t1794", tarefa=1794, banca="UERJ 2022",
                                                     executor="prova_pdf"))
    _escrever(base, "questoes", "t30_1", _questao(1, lista="t30", tarefa=30, banca=f"{hupe}, 2023",
                                                   executor="emed_api"))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    capsys.readouterr()
    assert emed_banco.questoes_no_hub_por_tarefa() == {26: 2, 1794: 2}, "so spoiler = fora do hub"
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out),
                            "--sem-cadeia", "teste: contagem do hub, sem Solucao"]) == 0
    assert json.loads((out / "listas" / "t26.json").read_text(encoding="utf-8"))["q"] == 2
    assert emed_banco.fora_do_hub({"banca": f"{hupe}, 2022", "executor": "emed_api"})
    assert not emed_banco.fora_do_hub({"banca": "UERJ 2022", "executor": "prova_pdf"})
    assert "fora_do_hub(" in Path(emed_banco.__file__).read_text(encoding="utf-8").split("def cmd_exportar", 1)[1]


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


# ------------------------------------------------------- solução MedHub (s199)

def _solucao(num, **extra):
    """Doc `solucoes/<lista>_<num>` cunhado pelo hub (sem comentário do professor)."""
    doc = {"lista": "t26", "num": num,
           "solucao": f"Pede a conduta ({num}). Decide: glicemia de jejum >= 92. Gabarito B.",
           "divergente": False, "fontes": "SBD 2024"}
    doc.update(extra)
    return doc


def test_solucoes_idempotente_e_invalida(tmp_path, monkeypatch, capsys):
    """2 novas + 1 inválida (sem texto); 2a rodada iguais; texto novo = atualizada."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    _escrever(base, "solucoes", "t26_1", _solucao(1))
    _escrever(base, "solucoes", "t26_2", _solucao(2, divergente=True))
    _escrever(base, "solucoes", "t26_3", _solucao(3, solucao="  "))
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (2, 0, 0)
    assert c["invalidas"] == ["t26_3"]
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 2)
    _escrever(base, "solucoes", "t26_1", _solucao(1, solucao="Outra solução, com acento."))
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--expect", "1", "--json"]) == 0
    assert _json_saida(capsys)["atualizadas"] == 1
    s1, s2 = db.emed_listar_solucoes("t26")
    assert s1["solucao"] == "Outra solução, com acento." and s1["divergente"] == 0
    assert s2["divergente"] == 1 and s2["fontes"] == "SBD 2024"


def test_solucoes_dry_run_sem_tabela(tmp_path, monkeypatch, capsys):
    """Dry-run conta e não roda DDL."""
    caminho = _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    _escrever(base, "solucoes", "t26_1", _solucao(1))
    assert emed_banco.main(["--solucoes", str(base), "--json"]) == 0
    assert _json_saida(capsys)["novas"] == 1
    assert _tabelas(caminho) == set()


def test_exportar_leva_solucao_medhub_e_round_trip(tmp_path, monkeypatch, capsys):
    """Questão com solução exporta `solucao_medhub`/`divergente`; sem solução, as chaves
    não aparecem; o doc exportado re-ingerido segue `iguais` (não vira `extras`)."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    for n in (1, 2):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
    _escrever(base, "solucoes", "t26_1", _solucao(1, divergente=True))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    assert emed_banco.main(["--solucoes", str(base), "--apply"]) == 0
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out),
                            "--sem-cadeia", "teste: so a Q1 tem Solucao (v1)"]) == 0
    d1 = json.loads((out / "questoes" / "t26_1.json").read_text(encoding="utf-8"))
    d2 = json.loads((out / "questoes" / "t26_2.json").read_text(encoding="utf-8"))
    assert d1["solucao_medhub"] == _solucao(1)["solucao"] and d1["divergente"] is True
    assert "solucao_medhub" not in d2 and "divergente" not in d2
    capsys.readouterr()
    assert emed_banco.main(["--ingerir", str(out), "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["novas"], c["atualizadas"], c["iguais"]) == (0, 0, 2)


# ------------------------------------------------------------ s200: cadeia, objetivo, riscadas

def _v2(num, **extra):
    """Solução v2 sintética: 2 elos; B certa; A cai no elo 1, C e D no elo 2."""
    doc = {"lista": "t26", "num": num, "versao": 2, "objetivo": "Indicação de insulina",
           "pede": "A conduta na gestante com glicemia fora da meta.",
           "cadeia": [{"elo": "Classificar o controle glicêmico", "chave": "2+ valores acima da meta."},
                      {"elo": "Escolher o fármaco na gestação", "chave": "Insulina é a 1ª escolha."}],
           "alternativas": {"A": {"elo": 1, "porque": "Dieta já falhou."},
                            "B": {"certa": True, "porque": "Insulina."},
                            "C": {"elo": 2, "porque": "Metformina é 2ª linha."},
                            "D": {"elo": 2, "porque": "Glibenclamida é contraindicada."}},
           "divergente": False, "conferir": "", "fontes": "SBD 2026"}
    doc.update(extra)
    return doc


def test_solucao_v2_valida_grava_cadeia_e_objetivo(tmp_path, monkeypatch, capsys):
    """v2 válida grava a cadeia como JSON e o objetivo em coluna; forma torta é inválida
    (elo fora da cadeia, 2 certas) sem derrubar o lote; o export leva a cadeia como OBJETO."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "questoes", "t26_1", _questao(1))
    _escrever(base, "solucoes", "t26_1", _v2(1))
    torta = _v2(2)
    torta["alternativas"]["A"]["elo"] = 9
    _escrever(base, "solucoes", "t26_2", torta)
    duas = _v2(3)
    duas["alternativas"]["C"] = {"certa": True, "porque": "x"}
    _escrever(base, "solucoes", "t26_3", duas)
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    capsys.readouterr()
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert c["novas"] == 1 and sorted(c["invalidas"]) == ["t26_2", "t26_3"]
    (s1,) = db.emed_listar_solucoes("t26")
    assert s1["objetivo"] == "Indicação de insulina"
    assert db.solucao_estruturada(s1["solucao"])["cadeia"][1]["elo"] == "Escolher o fármaco na gestação"
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 0
    d = json.loads((out / "questoes" / "t26_1.json").read_text(encoding="utf-8"))
    assert d["solucao_medhub"]["alternativas"]["C"]["elo"] == 2
    assert d["objetivo"] == "Indicação de insulina"


def test_objetivo_ausente_preserva_o_do_banco(tmp_path, monkeypatch, capsys):
    """Re-ingerir uma solução SEM a chave `objetivo` (arquivo v1 antigo) não apaga o objetivo."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    _escrever(base, "solucoes", "t26_1", _v2(1))
    assert emed_banco.main(["--solucoes", str(base), "--apply"]) == 0
    sem = _v2(1)
    del sem["objetivo"]
    _escrever(base, "solucoes", "t26_1", sem)
    capsys.readouterr()
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["iguais"] == 1
    assert db.emed_listar_solucoes("t26")[0]["objetivo"] == "Indicação de insulina"


def test_riscadas_gravam_e_viram_leitura_metacognitiva(tmp_path, monkeypatch, capsys):
    """As riscadas da página entram no banco e a leitura cruza com a cadeia: letra errada
    riscada = elo executado; a marcada aponta o elo que quebrou; riscar a certa é alarme."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "questoes", "t26_1", _questao(1))
    _escrever(base, "solucoes", "t26_1", _v2(1))
    _escrever(base, "respostas", "t26_1",
              {"lista": "t26", "num": 1, "letra": "C", "confianca": "duvida", "gabarito": "B",
               "riscadas": ["d", "A"], "respondido_em": "2026-09-26T10:00:00Z"})
    for modo in ("--ingerir", "--solucoes", "--registrar"):
        assert emed_banco.main([modo, str(base), "--apply"]) == 0
    capsys.readouterr()
    assert db.emed_listar_respostas("t26")[0]["riscadas"] == "A,D"
    (e,) = emed_banco.erros_da_lista("t26")
    m = e["leitura"]
    assert m["riscadas"] == ["A", "D"] and m["restantes"] == ["B", "C"]
    assert m["elos_ok"] == [1, 2] and m["elo_letra"] == 2 and not m["riscou_certa"]
    assert "ficou entre B e C" in emed_banco.texto_leitura(m, "duvida")
    # s202 (nota de UX da s201): 3 letras = lista em portugues, nao "A e C e D"
    assert "ficou entre A, C e D" in emed_banco.texto_leitura(dict(m, restantes=["A", "C", "D"]), "duvida")
    m2 = emed_banco.leitura_metacognitiva({"letra": "C", "gabarito": "B", "riscadas": "B"},
                                          db.emed_listar_solucoes("t26")[0]["solucao"])
    assert m2["riscou_certa"] is True


def test_por_objetivo_soma_listas_do_mesmo_tema_e_chute_nao_e_firme():
    """O mapa de fragilidade soma t26 + t40 (mesmo tema) por objetivo; chute certo não conta
    como firme; questão sem objetivo aparece como '(sem objetivo)'."""
    status = [{"lista": "t26", "tema": "DMG"}, {"lista": "t40", "tema": "DMG"}]
    resp = [{"lista": "t26", "num": 1, "correta": 1, "confianca": "solida"},
            {"lista": "t40", "num": 7, "correta": 1, "confianca": "chute"},
            {"lista": "t40", "num": 8, "correta": 0, "confianca": "solida"},
            {"lista": "t40", "num": 9, "correta": 1, "confianca": "duvida"}]
    sols = [{"lista": "t26", "num": 1, "objetivo": "Indicação de insulina"},
            {"lista": "t40", "num": 7, "objetivo": "Indicação de insulina"},
            {"lista": "t40", "num": 8, "objetivo": "Indicação de insulina"}]
    g = {x["objetivo"]: x for x in emed_banco.por_objetivo(status, resp, sols)}
    ins = g["Indicação de insulina"]
    assert (ins["feitas"], ins["firmes"], ins["chutes_certos"]) == (3, 1, 1)
    assert ins["erradas"] == ["t40 Q8"]
    assert g["(sem objetivo)"]["firmes"] == 1


# ------------------------------------------------ s201: F134 (perturbação) e F133 (propriedade)

def test_exportar_em_banco_nao_migrado_mantem_as_solucoes(tmp_path, monkeypatch, capsys):
    """F134 -- PERTURBAÇÃO: o banco perde as colunas que a s200 criou (`emed_solucoes.objetivo`,
    `emed_respostas.riscadas`), como um banco que ainda não rodou o ALTER. O `--exportar` tem de
    manter as N soluções. O `_emed_ler` de antes do `da62e95` fazia o SELECT com a coluna nova,
    levava `OperationalError` e o próprio `except` devolvia `[]`: o hub seria semeado sem
    nenhuma Solução MedHub, em silêncio. Ler também não pode migrar o banco (leitura sem DDL)."""
    caminho = _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    n = 3
    for i in range(1, n + 1):
        _escrever(base, "questoes", f"t26_{i}", _questao(i))
        _escrever(base, "solucoes", f"t26_{i}", _v2(i))
    _escrever(base, "respostas", "t26_1", {
        "lista": "t26", "tarefa": 26, "num": 1, "letra": "C", "confianca": "duvida",
        "riscadas": ["A"], "respondido_em": "2026-09-26T10:00:00Z"})
    for modo in ("--ingerir", "--solucoes", "--registrar"):
        assert emed_banco.main([modo, str(base), "--apply"]) == 0
    capsys.readouterr()

    con = sqlite3.connect(caminho)       # a perturbação: o banco "volta" para antes da s200
    # o banco sintético carrega views do schema geral sem as tabelas delas (flashcards...), e o
    # DROP COLUMN re-valida o schema inteiro; as views não entram no que este teste mede
    for (view,) in con.execute("SELECT name FROM sqlite_master WHERE type='view'").fetchall():
        con.execute(f"DROP VIEW {view}")
    con.execute("ALTER TABLE emed_solucoes DROP COLUMN objetivo")
    con.execute("ALTER TABLE emed_respostas DROP COLUMN riscadas")
    con.commit()
    con.close()

    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out),
                            "--sem-cadeia", "teste: v2 sem a coluna objetivo"]) == 0
    docs = [json.loads((out / "questoes" / f"t26_{i}.json").read_text(encoding="utf-8"))
            for i in range(1, n + 1)]
    assert sum(1 for d in docs if d.get("solucao_medhub")) == n
    assert all(d["solucao_medhub"]["cadeia"] for d in docs)   # a v2 viaja como objeto
    assert all("objetivo" not in d for d in docs)             # coluna ausente = sem objetivo
    (r,) = db.emed_listar_respostas("t26")
    assert r["letra"] == "C" and r["riscadas"] is None
    con = sqlite3.connect(caminho)
    try:
        assert "objetivo" not in {c[1] for c in con.execute("PRAGMA table_info(emed_solucoes)")}
    finally:
        con.close()


_HUB_TEMPLATE = ROOT / "core" / "templates" / "hub.html"
#: ⚰️ s211: as chaves que a página passou a gravar nas parts 2-4 (`elos`, `cadeia_defeito`, `modo`,
#: `grifos`) ficaram neste conjunto até a part-5 dar coluna a elas; vazio de novo, o predicado volta a
#: exigir `[]` -- toda chave da página tem destino.
_SEM_DESTINO_ATE_A_PART_5 = set()
#: doc da página -> coluna do banco quando o nome muda (o mesmo mapeamento do writer)
_ALIAS_DOC_COLUNA = {"tarefa": "tarefa_id"}


def _chaves_da_resposta_na_pagina():
    """As chaves que a página grava em `respostas/<lista>_<num>`, LIDAS do template, nunca
    digitadas: o literal `var r = {...}` do botão Responder + toda atribuição `r.<chave> =`.
    Chave com `_` inicial é estado local (a página a filtra antes do `set`)."""
    src = _HUB_TEMPLATE.read_text(encoding="utf-8")
    i = src.index("var r = {lista:")          # âncora sumiu = o teste quebra alto, não passa
    j = src.index("};", i)
    chaves = set(re.findall(r"[{,]\s*([A-Za-z_]\w*)\s*:", src[i + len("var r = "):j + 1]))
    chaves |= set(re.findall(r"\br\.([A-Za-z_]\w*)\s*=(?!=)", src))
    return {c for c in chaves if not c.startswith("_")}


def _chaves_sem_destino(tmp_path, chaves):
    """Grava pelo `--registrar` um doc com TODAS as `chaves` e devolve as que não chegaram a
    uma coluna de `emed_respostas` (nem a `extras`, se um dia a tabela tiver)."""
    plaus = {"lista": "t26", "tarefa": 26, "num": 1, "letra": "C", "confianca": "duvida",
             "correta": False, "gabarito": "B", "riscadas": ["A"], "racional": "sentinela",
             "elo": "li_errado", "tempo_s": 42, "flag": True,
             "respondido_em": "2026-09-26T10:00:00Z",
             # s211: valores do vocabulário (sentinela solta seria doc inválido, nada gravado)
             "elos": ["sim", "nao"], "grifos": {"enun": [[0, 3]]}, "modo": "estudo",
             "cadeia_defeito": {"motivo": "sentinela", "ts": "2026-10-02T12:00:00Z"}}
    doc = {c: plaus.get(c, f"sentinela-{c}") for c in chaves}
    base = tmp_path / "prop"
    _escrever(base, "questoes", "t26_1", _questao(1))
    _escrever(base, "respostas", "t26_1", doc)
    for modo in ("--ingerir", "--registrar"):
        assert emed_banco.main([modo, str(base), "--apply"]) == 0
    con = sqlite3.connect(db.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        (linha,) = [dict(r) for r in con.execute("SELECT * FROM emed_respostas")]
    finally:
        con.close()
    extras = json.loads(linha.get("extras") or "{}")
    return sorted(c for c in chaves
                  if linha.get(_ALIAS_DOC_COLUNA.get(c, c)) in (None, "") and c not in extras)


def test_toda_chave_que_a_pagina_grava_na_resposta_tem_destino(tmp_path, monkeypatch, capsys):
    """F133 -- PROPRIEDADE: toda chave que a página grava num doc `respostas/*` chega ao banco
    (coluna ou `extras`). A s197 gravava `riscadas` e o writer as descartava por não ter
    coluna nem `extras`; o teste da s200 cobria `riscadas`, não a PRÓXIMA chave. O controle
    negativo prova que o predicado acusa uma chave nova sem destino."""
    _usar_db(tmp_path, monkeypatch)
    chaves = _chaves_da_resposta_na_pagina()
    assert {"letra", "confianca", "riscadas", "racional", "elos"} <= chaves   # a leitura pegou
    assert _chaves_sem_destino(tmp_path, chaves) == sorted(_SEM_DESTINO_ATE_A_PART_5)
    capsys.readouterr()
    _usar_db(tmp_path / "ctl", monkeypatch)
    (tmp_path / "ctl").mkdir()
    assert _chaves_sem_destino(tmp_path / "ctl", chaves | {"chave_nova"}) == sorted(
        _SEM_DESTINO_ATE_A_PART_5 | {"chave_nova"})


# ------------------------------------------------ s201: lista fechada de objetivo (#5 do /ai-eng)

_OBJETIVOS = ROOT / "core" / "objetivos.json"
_BRIEF = ROOT / "docs" / "SOLUCAO-MEDHUB-BRIEF.md"


def test_catalogo_de_objetivos_bem_formado():
    """`core/objetivos.json`: todo tema com listas e 6-9 objetivos, sem objetivo repetido no
    tema e sem lista em dois temas (a lista decide o tema na validação)."""
    cat = json.loads(_OBJETIVOS.read_text(encoding="utf-8"))
    vistas = {}
    for t in cat["temas"]:
        assert t["tema"] and t["listas"], t
        assert 6 <= len(t["objetivos"]) <= 9, t["tema"]
        assert len(set(t["objetivos"])) == len(t["objetivos"]), t["tema"]
        assert not any(o.startswith("outro:") for o in t["objetivos"])
        for lista in t["listas"]:
            assert lista not in vistas, f"{lista} em {vistas.get(lista)} e {t['tema']}"
            vistas[lista] = t["tema"]


def test_objetivo_valida_contra_a_lista_fechada_do_tema():
    """Objetivo do tema passa; fora da lista, 'outro:' sem rótulo e lista sem entrada no
    catálogo são problema; 'outro: <rótulo>' passa; objetivo AUSENTE não é problema (a chave
    ausente preserva o do banco)."""
    cat = {"temas": [{"tema": "DMG", "listas": ["t26"],
                      "objetivos": ["Indicação de insulina", "DM prévio x DMG"]}]}
    ok = _v2(1)
    assert db.solucao_v2_problemas(ok, catalogo=cat) == []
    assert db.solucao_v2_problemas(_v2(1, objetivo="outro: Prevenção de acidentes"),
                                   catalogo=cat) == []
    sem = _v2(1)
    del sem["objetivo"]
    assert db.solucao_v2_problemas(sem, catalogo=cat) == []
    fora = db.solucao_v2_problemas(_v2(1, objetivo="Rastreio universal"), catalogo=cat)
    assert fora and "fora da lista fechada" in fora[0]
    assert db.solucao_v2_problemas(_v2(1, objetivo="outro:  "), catalogo=cat)
    orfa = db.solucao_v2_problemas(_v2(1, lista="t999"), catalogo=cat)
    assert orfa and "core/objetivos.json" in orfa[0]


def test_writer_recusa_objetivo_fora_da_lista_do_catalogo_real(tmp_path, monkeypatch, capsys):
    """O caminho real (`--solucoes`) lê `core/objetivos.json`: t26 com objetivo inventado vai
    para `invalidas` e nada é gravado."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    _escrever(base, "solucoes", "t26_1", _v2(1, objetivo="Objetivo inventado"))
    _escrever(base, "solucoes", "t26_2", _v2(2))
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert c["invalidas"] == ["t26_1"] and c["novas"] == 1


def test_brief_le_o_catalogo_e_nao_carrega_copia():
    """O brief aponta `core/objetivos.json` e não carrega a lista de nenhum tema (no máximo 1
    objetivo por tema, o do exemplo): duas cópias divergem, e foi o que o #5 fechou."""
    brief = _BRIEF.read_text(encoding="utf-8")
    assert "core/objetivos.json" in brief
    for t in json.loads(_OBJETIVOS.read_text(encoding="utf-8"))["temas"]:
        assert sum(o in brief for o in t["objetivos"]) <= 1, t["tema"]


#: O banco que o vivo mede (part-2b). Constante de módulo para o teste de skip apontá-la para um
#: arquivo inexistente.
REAL_DB = ROOT / "ipub.db"


def _objetivos_fora_do_catalogo(db_path, catalogo=None):
    """(linhas com objetivo, [(lista, num, objetivo, problema)]) de `emed_solucoes` em `db_path`, lidas
    em read-only e julgadas pela MESMA regra do writer (`db.problema_de_objetivo`); sem `catalogo`, o
    `core/objetivos.json`. O vivo e o gêmeo hermético passam por aqui."""
    con = sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)
    try:
        linhas = con.execute("SELECT lista, num, objetivo FROM emed_solucoes "
                             "WHERE COALESCE(objetivo, '') <> '' ORDER BY lista, num").fetchall()
    finally:
        con.close()
    cat = db.carregar_objetivos() if catalogo is None else catalogo
    ruins = []
    for lista, num, objetivo in linhas:
        problema = db.problema_de_objetivo(lista, objetivo, cat)
        if problema:
            ruins.append((lista, num, objetivo, problema))
    return linhas, ruins


@pytest.mark.vivo
def test_objetivos_gravados_no_banco_real_cabem_no_catalogo():
    """Leitura read-only do `ipub.db` real: todo objetivo gravado está na lista fechada do tema da sua
    lista ou é 'outro: <rótulo>'. FORMA, não conjunto (part-2b): pertencer ao catálogo versionado, que é
    o conjunto PERMITIDO -- nunca bater com uma lista de objetivos tirada do banco. O gêmeo hermético
    (`test_gemeo_objetivo_gravado_fora_do_catalogo_e_acusado`) planta o caso e exige a acusação.

    Pula com motivo (`VIVO:`) sem o banco, sem a coluna ou sem objetivo gravado; a guarda vem antes de
    qualquer conexão."""
    if not REAL_DB.is_file():
        pytest.skip("VIVO: ipub.db ausente -- objetivos gravados x core/objetivos.json não medidos")
    try:
        linhas, ruins = _objetivos_fora_do_catalogo(REAL_DB)
    except sqlite3.OperationalError as e:
        pytest.skip(f"VIVO: ipub.db sem emed_solucoes.objetivo ({e}) -- objetivos não medidos")
    if not linhas:
        pytest.skip("VIVO: ipub.db sem objetivo gravado em emed_solucoes -- catálogo não medido")
    print(f"  objetivos: {len(linhas)} gravados, {len(ruins)} fora do catálogo")
    assert ruins == [], f"objetivo gravado fora da lista fechada do tema: {ruins}"


def test_gemeo_objetivo_gravado_fora_do_catalogo_e_acusado(db_sintetico, tmp_path, capsys):
    """Gêmeo hermético do vivo acima (part-2b): o writer real grava 3 soluções com objetivo válido
    HOJE (2 do catálogo, 1 'outro: <rótulo>'); depois o catálogo muda -- o caso que o gate do writer
    não pega. Mesmo leitor, mesma regra: o objetivo que saiu da lista do tema e a lista que saiu do
    catálogo são acusados; o 'outro: <rótulo>' nunca."""
    base = tmp_path / "sol"
    _escrever(base, "solucoes", "t26_1", _v2(1))
    _escrever(base, "solucoes", "t26_2", _v2(2, objetivo="DM prévio x DMG"))
    _escrever(base, "solucoes", "t26_3", _v2(3, objetivo="outro: Prevenção de acidentes"))
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["novas"] == 3
    linhas, ruins = _objetivos_fora_do_catalogo(db_sintetico)
    assert len(linhas) == 3 and ruins == [], "com o catálogo real, nada a acusar"
    encolhido = {"temas": [{"tema": "DMG", "listas": ["t26"], "objetivos": ["Indicação de insulina"]}]}
    _l, ruins = _objetivos_fora_do_catalogo(db_sintetico, encolhido)
    assert [(lista, num) for lista, num, _o, _p in ruins] == [("t26", 2)], ruins
    assert "fora da lista fechada" in ruins[0][3]
    _l, ruins = _objetivos_fora_do_catalogo(db_sintetico, {"temas": []})
    assert [(lista, num) for lista, num, _o, _p in ruins] == [("t26", 1), ("t26", 2)], ruins
    assert all("core/objetivos.json" in p for _l, _n, _o, p in ruins)


def test_vivo_pula_com_motivo_sem_banco(tmp_path, monkeypatch):
    """DoD 1 da part-2b: sem o banco, o vivo PULA com motivo `VIVO:` e não cria o arquivo."""
    ausente = tmp_path / "ipub.db"
    monkeypatch.setitem(globals(), "REAL_DB", ausente)
    with pytest.raises(pytest.skip.Exception, match=r"VIVO:"):
        test_objetivos_gravados_no_banco_real_cabem_no_catalogo()
    assert not ausente.exists(), "a guarda tem de vir antes do connect"


def test_writer_valida_objetivo_tambem_na_v1(tmp_path, monkeypatch, capsys):
    """Doc v1 (texto) com objetivo inventado também é recusado: o gate vale para o objetivo
    GRAVADO, não para a forma da solução."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    _escrever(base, "solucoes", "t26_1", _solucao(1, objetivo="Objetivo inventado"))
    _escrever(base, "solucoes", "t26_2", _solucao(2, objetivo="DM prévio x DMG"))
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert c["invalidas"] == ["t26_1"] and c["novas"] == 1


# ------------------------------------------------ s201: amostra de leitura das soluções (#7 do /ai-eng)

def test_amostra_de_leitura_divergentes_mais_duas_aleatorias_estaveis():
    """Por lista: TODAS as divergentes + 2 aleatórias entre as não divergentes; a mesma entrada
    dá a mesma amostra (semente = o conjunto de chaves), lista pequena devolve o que existe."""
    docs = ([_v2(n, lista="t40") for n in range(1, 11)]
            + [_v2(11, lista="t40", divergente=True), _v2(1, lista="t26")])
    a = emed_banco.amostra_leitura(docs)
    assert a["t40"]["divergentes"] == [11]
    assert len(a["t40"]["aleatorias"]) == 2 and 11 not in a["t40"]["aleatorias"]
    assert set(a["t40"]["aleatorias"]) <= set(range(1, 11))
    assert emed_banco.amostra_leitura(list(reversed(docs))) == a        # estável
    assert a["t26"] == {"divergentes": [], "aleatorias": [1]}


def test_solucoes_json_traz_a_amostra_de_leitura(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    for n in (1, 2, 3, 4):
        _escrever(base, "solucoes", f"t26_{n}", _v2(n, divergente=(n == 4)))
    assert emed_banco.main(["--solucoes", str(base), "--json"]) == 0
    saida = _json_saida(capsys)
    assert saida["leitura"]["t26"]["divergentes"] == [4]
    assert len(saida["leitura"]["t26"]["aleatorias"]) == 2


def test_tarefas_com_questoes_le_o_banco_e_tolera_tabela_ausente(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    assert db.tarefas_com_questoes() == set()                          # sem tabela: vazio, sem DDL
    base = tmp_path / "buf"
    _escrever(base, "questoes", "t26_1", _questao(1))
    assert emed_banco.main(["--ingerir", str(base), "--apply"]) == 0
    assert db.tarefas_com_questoes() == {26}


# ------------------------------------------------ s211: Solução v3 (feedback-cadeia-declarada part-1)

_CAT = {"temas": [{"tema": "DMG", "listas": ["t26"],
                   "objetivos": ["Indicação de insulina", "DM prévio x DMG"]}]}


def _v3(num, **extra):
    """Solução v3 sintética: identificar -> recordar -> descartar C; B certa."""
    doc = {"lista": "t26", "num": num, "versao": 3, "objetivo": "Indicação de insulina",
           "pede": "A conduta na gestante com glicemia fora da meta.",
           "cadeia": [
               {"tipo": "identificar", "elo": "Identificou que 2+ valores estão acima da meta.",
                "chave": "2+ valores acima da meta = controle inadequado.",
                "habilidade": "Classificar o controle glicêmico na gestação"},
               {"tipo": "recordar", "elo": "Recordou que a insulina é a 1ª escolha na gestação.",
                "chave": "Insulina é a 1ª escolha.", "habilidade": "Escolher o fármaco na gestação"},
               {"tipo": "descartar", "letra": "C", "elo": "Descartou a metformina (C) como 2ª linha.",
                "chave": "Metformina só se a insulina não for viável.",
                "habilidade": "Usar o achado que exclui o tratamento concorrente"}],
           "alternativas": {"A": {"porque": "Dieta já falhou."},
                            "B": {"certa": True, "porque": "Insulina."},
                            "C": {"porque": "Metformina é 2ª linha."},
                            "D": {"porque": "Glibenclamida é contraindicada."}},
           "divergente": False, "conferir": "", "fontes": "SBD 2026"}
    doc.update(extra)
    return doc


def _v3_probs(doc):
    return db.solucao_v3_problemas(doc, catalogo=_CAT)


def test_solucao_v3_valida_nao_tem_problema():
    assert _v3_probs(_v3(1)) == []
    sem_descartar = _v3(1)
    sem_descartar["cadeia"] = sem_descartar["cadeia"][:2]          # 2 elos, 0 descartar: ok
    assert _v3_probs(sem_descartar) == []
    com_elo_herdado = _v3(1)
    com_elo_herdado["alternativas"]["A"]["elo"] = 9                 # elo da v2 numa errada: ignorado
    assert _v3_probs(com_elo_herdado) == []


def test_solucao_v3_cadeia_com_menos_de_2_ou_mais_de_4_elos():
    curta = _v3(1)
    curta["cadeia"] = curta["cadeia"][:1]
    assert any("cadeia com 1 elo(s)" in p for p in _v3_probs(curta))
    longa = _v3(1)
    longa["cadeia"] = longa["cadeia"][:2] + [dict(longa["cadeia"][2], letra=x) for x in "ACD"]
    assert any("cadeia com 5 elo(s)" in p for p in _v3_probs(longa))
    assert _v3_probs(_v3(1, cadeia=[])) == ["cadeia vazia"]


@pytest.mark.parametrize("campo", ["elo", "chave", "habilidade", "tipo"])
def test_solucao_v3_elo_sem_campo_obrigatorio(campo):
    doc = _v3(1)
    del doc["cadeia"][1][campo]
    assert f"elo 2 sem {campo}" in _v3_probs(doc)


def test_solucao_v3_tipo_fora_do_vocabulario():
    doc = _v3(1)
    doc["cadeia"][1]["tipo"] = "aplicar"
    assert any(p.startswith("elo 2 com tipo fora de identificar | recordar | descartar")
               for p in _v3_probs(doc))


def test_solucao_v3_primeiro_elo_nao_e_identificar():
    doc = _v3(1)
    doc["cadeia"][0]["tipo"] = "recordar"
    assert "1º elo não é identificar" in _v3_probs(doc)


def test_solucao_v3_sem_nenhum_recordar():
    doc = _v3(1)
    doc["cadeia"][1]["tipo"] = "identificar"
    assert "nenhum elo recordar" in _v3_probs(doc)


def test_solucao_v3_ordem_violada():
    doc = _v3(1)
    doc["cadeia"] = [doc["cadeia"][0], doc["cadeia"][2], doc["cadeia"][1]]  # descartar antes de recordar
    assert any(p.startswith("ordem violada no elo 3: recordar depois de descartar")
               for p in _v3_probs(doc))


def test_solucao_v3_descartar_sem_letra():
    doc = _v3(1)
    del doc["cadeia"][2]["letra"]
    assert "elo 3 descartar sem letra" in _v3_probs(doc)


def test_solucao_v3_descartar_letra_inexistente():
    doc = _v3(1)
    doc["cadeia"][2]["letra"] = "E"
    assert any("descarta a letra E, inexistente" in p for p in _v3_probs(doc))


def test_solucao_v3_descartar_a_letra_certa():
    doc = _v3(1)
    doc["cadeia"][2]["letra"] = "b"
    assert "elo 3 descarta a letra certa (B)" in _v3_probs(doc)


def test_solucao_v3_alternativa_sem_porque():
    doc = _v3(1)
    doc["alternativas"]["D"] = {"porque": "  "}
    assert "alternativa D sem porque" in _v3_probs(doc)


def test_solucao_v3_numero_de_certas_diferente_de_1():
    duas = _v3(1)
    duas["alternativas"]["A"]["certa"] = True
    assert "2 alternativas certas (esperado 1)" in _v3_probs(duas)
    nenhuma = _v3(1)
    nenhuma["alternativas"]["B"].pop("certa")
    assert "0 alternativas certas (esperado 1)" in _v3_probs(nenhuma)


def test_solucao_v3_pede_vazio():
    assert "pede vazio" in _v3_probs(_v3(1, pede=""))


def test_solucao_v3_objetivo_fora_da_lista_fechada():
    probs = _v3_probs(_v3(1, objetivo="Rastreio universal"))
    assert any("fora da lista fechada" in p for p in probs)
    assert _v3_probs(_v3(1, objetivo="outro: Prevenção de acidentes")) == []


def test_solucao_problemas_despacha_pela_versao():
    """`versao` 3 -> v3; 2 (ou ausente) -> v2: o mesmo doc v2 continua válido pela v2 e é
    recusado pela v3 (sem `tipo`/`habilidade`)."""
    assert db.solucao_problemas(_v3(1), catalogo=_CAT) == []
    assert db.solucao_problemas(_v2(1), catalogo=_CAT) == []
    assert db.solucao_problemas(dict(_v2(1), versao=3), catalogo=_CAT)
    assert db.solucao_problemas(_v3(1, versao="3"), catalogo=_CAT) == []


def test_solucao_v3_grava_e_v2_continua_gravando(tmp_path, monkeypatch, capsys):
    """Convivência: v3 válida grava (`versao` 3, sem o `elo` herdado nas alternativas), v3 torta
    vai para `invalidas`, a v2 do mesmo lote grava, e `solucao_estruturada` devolve as duas."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "sol"
    herdado = _v3(1)
    herdado["alternativas"]["A"]["elo"] = 2
    _escrever(base, "solucoes", "t26_1", herdado)
    _escrever(base, "solucoes", "t26_2", _v2(2))
    torta = _v3(3)
    torta["cadeia"][0]["tipo"] = "descartar"
    _escrever(base, "solucoes", "t26_3", torta)
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert c["novas"] == 2 and c["invalidas"] == ["t26_3"]
    s = {r["num"]: db.solucao_estruturada(r["solucao"]) for r in db.emed_listar_solucoes("t26")}
    assert s[1]["versao"] == 3 and s[1]["cadeia"][2]["letra"] == "C"
    assert "elo" not in s[1]["alternativas"]["A"]
    assert s[2]["versao"] == 2 and s[2]["alternativas"]["C"]["elo"] == 2
    assert db.solucao_estruturada('{"versao": 4, "cadeia": []}') is None


def test_exemplo_do_brief_passa_no_validador():
    """O exemplo JSON do brief É o contrato: extraído do bloco ```json e validado pelo mesmo
    validador do writer, contra o catálogo real de objetivos."""
    brief = _BRIEF.read_text(encoding="utf-8")
    blocos = re.findall(r"```json\n(.*?)\n```", brief, re.S)
    assert blocos, "o brief perdeu o bloco ```json do exemplo"
    exemplo = json.loads(blocos[0])
    assert exemplo["versao"] == 3
    assert db.solucao_problemas(exemplo) == []



# ------------------------------------------------ s211 part-5: a declaração chega ao ipub.db

def _resp_doc(num, letra, confianca="duvida", **extra):
    doc = {"lista": "t26", "tarefa": 26, "num": num, "letra": letra, "confianca": confianca,
           "gabarito": "B", "respondido_em": f"2026-10-02T10:0{num}:00Z"}
    doc.update(extra)
    return doc


def _linha(caminho, num):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    try:
        return dict(con.execute("SELECT * FROM emed_respostas WHERE num = ?", (num,)).fetchone())
    finally:
        con.close()


def test_registro_grava_elos_grifos_modo_e_defeito(tmp_path, monkeypatch, capsys):
    caminho = _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "respostas", "t26_1", _resp_doc(
        1, "C", elos=["sim", "nao", ""], grifos={"enun": [[0, 8]], "A": [[0, 3]]}, modo="estudo",
        cadeia_defeito={"motivo": " elo 2 repete o gabarito ", "ts": "2026-10-02T12:00:00Z"}))
    _escrever(base, "respostas", "t26_2", _resp_doc(2, "B", "solida"))           # antiga: sem os campos
    assert emed_banco.main(["--registrar", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["novas"] == 2
    r1, r2 = _linha(caminho, 1), _linha(caminho, 2)
    assert json.loads(r1["elos"]) == ["sim", "nao", ""]
    assert json.loads(r1["grifos"]) == {"A": [[0, 3]], "enun": [[0, 8]]}
    assert (r1["modo"], r1["cadeia_defeito"]) == ("estudo", "elo 2 repete o gabarito")
    assert (r2["elos"], r2["grifos"], r2["modo"], r2["cadeia_defeito"]) == ("", "", "", "")


@pytest.mark.parametrize("campo, valor", [
    ("elos", ["sim", "ok"]), ("elos", "sim"), ("modo", "simulado"), ("grifos", [[0, 3]])])
def test_elo_fora_do_vocabulario_invalida_o_doc(tmp_path, monkeypatch, capsys, campo, valor):
    """O db da página é entrada não confiável: valor fora do vocabulário vai para `invalidas` e o
    resto do lote grava (mesma régua da `confianca`)."""
    _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "respostas", "t26_1", _resp_doc(1, "C", **{campo: valor}))
    _escrever(base, "respostas", "t26_2", _resp_doc(2, "C", elos=["incerteza", "desatencao"]))
    assert emed_banco.main(["--registrar", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert c["invalidas"] == ["t26_1"] and c["novas"] == 1


def test_registro_e_idempotente_com_os_campos_novos(tmp_path, monkeypatch, capsys):
    """Re-registrar = `iguais`; mudar SÓ a declaração com o mesmo `respondido_em` = `atualizadas`;
    linha anterior à migração (colunas NULL) re-registrada com o doc antigo segue `iguais`."""
    caminho = _usar_db(tmp_path, monkeypatch)
    base = tmp_path / "buf"
    _escrever(base, "respostas", "t26_1", _resp_doc(1, "C", elos=["sim", ""], modo="prova"))
    _escrever(base, "respostas", "t26_2", _resp_doc(2, "B", "solida"))
    assert emed_banco.main(["--registrar", str(base), "--apply"]) == 0
    capsys.readouterr()
    assert emed_banco.main(["--registrar", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["iguais"] == 2
    _escrever(base, "respostas", "t26_1", _resp_doc(1, "C", elos=["sim", "nao"], modo="prova"))
    assert emed_banco.main(["--registrar", str(base), "--apply", "--json"]) == 0
    c = _json_saida(capsys)
    assert (c["atualizadas"], c["iguais"]) == (1, 1)
    assert json.loads(_linha(caminho, 1)["elos"]) == ["sim", "nao"]
    con = sqlite3.connect(caminho)
    con.execute("UPDATE emed_respostas SET elos = NULL, grifos = NULL, modo = NULL, "
                "cadeia_defeito = NULL WHERE num = 2")
    con.commit()
    con.close()
    assert emed_banco.main(["--registrar", str(base), "--apply", "--json"]) == 0
    assert _json_saida(capsys)["iguais"] == 2


def _lista_com_declaracoes(tmp_path):
    """t26: Q1 v3 errada (C) com conflito, defeito e grifo; Q2 v3 errada sem declaração; Q3 v3 certa na
    dúvida; Q4 v2 errada sem declaração (legado); Q5 v3 certa sólida (fica de fora)."""
    base = tmp_path / "buf"
    for n in (1, 2, 3, 4, 5):
        _escrever(base, "questoes", f"t26_{n}", _questao(n))
        _escrever(base, "solucoes", f"t26_{n}", _v2(n) if n == 4 else _v3(n))
    _escrever(base, "respostas", "t26_1", _resp_doc(
        1, "C", elos=["sim", "nao", "sim"], grifos={"enun": [[0, 8]], "C": [[0, 10]], "D": [[0, 999]]},
        cadeia_defeito={"motivo": "o elo 1 não decide nada"}, modo="estudo"))
    _escrever(base, "respostas", "t26_2", _resp_doc(2, "A", "chute"))
    _escrever(base, "respostas", "t26_3", _resp_doc(3, "B", "duvida", elos=["sim", "incerteza", "desatencao"]))
    _escrever(base, "respostas", "t26_4", _resp_doc(4, "C"))
    _escrever(base, "respostas", "t26_5", _resp_doc(5, "B", "solida"))
    for modo in ("--ingerir", "--solucoes", "--registrar"):
        assert emed_banco.main([modo, str(base), "--apply"]) == 0
    return base


def test_erros_imprime_declarado_e_conflito(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _lista_com_declaracoes(tmp_path)
    capsys.readouterr()
    assert emed_banco.main(["--erros", "t26"]) == 0
    out = capsys.readouterr().out
    blocos = {int(b.split(" ·")[0]): b for b in out.split("=" * 72 + "\nQ")[1:]}
    assert sorted(blocos) == [1, 2, 3, 4]                       # erradas + não-sólidas; a sólida certa sai
    b1 = blocos[1]
    assert "1. [Sim] Identificou que 2+ valores" in b1 and "2. [Não] Recordou" in b1 and "3. [Sim] Descartou" in b1
    assert "CONFLITO no elo 3" in b1 and "Cadeia com defeito: o elo 1 não decide nada" in b1
    assert 'Grifou: enunciado "Gestante" · C "Metformina"' in b1   # trecho, não offset; o inválido cala
    assert "modo estudo" in b1
    assert "[sem declaração]" in blocos[2] and "CERTA (duvida)" in blocos[3] and "[Incerteza]" in blocos[3]
    assert "cai no elo None" not in out                        # v3 nunca aponta elo pela alternativa
    assert "cai no elo" not in b1 and "cai no elo" not in blocos[2]
    assert "legado: a letra marcada cai no elo 2" in blocos[4]   # v2 sem declaração: rotulada legado
    # presumido: certa e sólida sem `elos` é leitura, não dado
    d = emed_banco.declaracao({"correta": 1, "confianca": "solida", "letra": "B"},
                              json.dumps(dict(_v3(5), versao=3)))
    assert [x["rotulo"] for x in d["elos"]] == ["presumido Sim"] * 3 and not d["declarado"]


def test_elos_lista_os_nao_sim_na_ordem(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    base = _lista_com_declaracoes(tmp_path)
    _escrever(base, "respostas", "t40_1", dict(_resp_doc(1, "C", elos=["nao", "sim", "sim"]), lista="t40", tarefa=40))
    _escrever(base, "solucoes", "t40_1", _v3(1, lista="t40"))
    for modo in ("--solucoes", "--registrar"):
        assert emed_banco.main([modo, str(base), "--apply"]) == 0
    capsys.readouterr()
    assert emed_banco.main(["--elos", "t26", "--json"]) == 0
    itens = _json_saida(capsys)
    assert [(x["num"], x["i"], x["estado"]) for x in itens] == [(1, 2, "nao"), (3, 2, "incerteza"),
                                                               (3, 3, "desatencao")]
    assert itens[0]["habilidade"] == "Escolher o fármaco na gestação"
    assert itens[0]["objetivo"] == "Indicação de insulina"
    assert emed_banco.main(["--elos", "--json"]) == 0             # sem LISTA: todas
    todos = _json_saida(capsys)
    assert [(x["lista"], x["num"], x["estado"]) for x in todos][:2] == [("t26", 1, "nao"), ("t40", 1, "nao")]
    assert emed_banco.main(["--elos", "t26"]) == 0
    assert "t26 | Q1 | 2 | Não | Escolher o fármaco na gestação" in capsys.readouterr().out


def test_defeitos_lista_cadeias_sinalizadas(tmp_path, monkeypatch, capsys):
    _usar_db(tmp_path, monkeypatch)
    _lista_com_declaracoes(tmp_path)
    capsys.readouterr()
    assert emed_banco.main(["--defeitos", "--json"]) == 0
    assert _json_saida(capsys) == [{"lista": "t26", "num": 1, "motivo": "o elo 1 não decide nada"}]
    assert emed_banco.main(["--defeitos", "--lista", "t40"]) == 0
    assert "nenhuma cadeia sinalizada" in capsys.readouterr().out


# ------------------------------------------------------------------- Fase 0 Lote 1 part-1.1a: mescla de figura

URL_F = "https://estrategia-prod-questoes.s3.amazonaws.com/images/X/X-400.png"


def _linha_q(caminho, num, lista="t26"):
    """A linha de `emed_questoes` como dict (leitura direta do banco SINTETICO)."""
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    try:
        r = con.execute("SELECT * FROM emed_questoes WHERE lista = ? AND num = ?", (lista, num)).fetchone()
        return dict(r) if r else None
    finally:
        con.close()


def _contar_q(caminho):
    con = sqlite3.connect(caminho)
    try:
        return con.execute("SELECT COUNT(*) FROM emed_questoes").fetchone()[0]
    finally:
        con.close()


def _chrome(db_sintetico, *nums, **extra):
    """Linhas do Chrome (sem figura) gravadas pelo writer real no banco sintetico do Lote 0."""
    assert db.DB_PATH == db_sintetico and Path(db_sintetico).name == "ipub.db"
    assert Path(db_sintetico).resolve() != (ROOT / "ipub.db").resolve()     # sentinela: nunca o real
    cont = db.emed_upsert_questoes([_questao(n, **extra) for n in nums])
    assert cont["novas"] == len(nums)


def test_mescla_da_figura_a_linha_do_chrome_sem_tocar_o_texto(db_sintetico):
    """DoD 3 (a) (1.1a): a linha do Chrome ganha `figuras`/`figuras_alt`; enunciado, alternativas,
    gabarito e solucao ficam byte a byte; o `hash` acompanha o `extras` novo."""
    _chrome(db_sintetico, 1, 2)
    antes = _linha_q(db_sintetico, 1)
    r = db.emed_mesclar_figuras({"e1": {"figura": True, "figuras": [URL_F], "figuras_alt": {"B": [URL_F]}}})
    assert r == {"atualizadas": 1, "iguais": 0, "ausentes": []}
    depois = _linha_q(db_sintetico, 1)
    for c in ("enunciado", "alternativas", "gabarito", "solucao", "emed_id", "banca", "tags",
              "forum", "estatistica", "executor", "capturado_em", "lista", "num"):
        assert depois[c] == antes[c], c
    assert json.loads(depois["extras"]) == {"figura": True, "figuras": [URL_F], "figuras_alt": {"B": [URL_F]}}
    assert depois["hash"] == db.emed_hash_questao(depois) != antes["hash"]
    assert _linha_q(db_sintetico, 2)["extras"] == ""                      # a outra linha nao muda


def test_mescla_de_emed_id_desconhecido_vai_para_ausentes_sem_insert(db_sintetico):
    """DoD 3 (b) (1.1a): a mescla nunca cria linha."""
    _chrome(db_sintetico, 1)
    r = db.emed_mesclar_figuras({"nao-existe": {"figuras": [URL_F]}})
    assert r == {"atualizadas": 0, "iguais": 0, "ausentes": ["nao-existe"]}
    assert _contar_q(db_sintetico) == 1


def test_mescla_e_idempotente(db_sintetico):
    """DoD 3 (c) (1.1a): a 2a rodada com o mesmo mapa da `atualizadas` 0."""
    _chrome(db_sintetico, 1)
    mapa = {"e1": {"figura": True, "figuras": [URL_F]}}
    assert db.emed_mesclar_figuras(mapa)["atualizadas"] == 1
    h = _linha_q(db_sintetico, 1)["hash"]
    assert db.emed_mesclar_figuras(mapa) == {"atualizadas": 0, "iguais": 1, "ausentes": []}
    assert _linha_q(db_sintetico, 1)["hash"] == h


def test_mescla_com_figuras_derruba_o_sem_figura(db_sintetico):
    """DoD 3 (d) (1.1a): a figura chegou, a declaracao cai; as chaves que nao sao de figura ficam."""
    _chrome(db_sintetico, 1, sem_figura=True, acerto_pct=40)
    assert json.loads(_linha_q(db_sintetico, 1)["extras"]) == {"acerto_pct": 40, "sem_figura": True}
    r = db.emed_mesclar_figuras({"e1": {"figura": True, "figuras": [URL_F], "sem_figura": True}})
    assert r["atualizadas"] == 1
    assert json.loads(_linha_q(db_sintetico, 1)["extras"]) == {"acerto_pct": 40, "figura": True,
                                                              "figuras": [URL_F]}


def _recaptura(tmp_path):
    """A pasta do `emed_api --apply` da recaptura: 1 com figura, 1 sem chave de figura, 1 ausente."""
    base = tmp_path / "recaptura"
    _escrever(base, "questoes", "t26_1", {"lista": "t26", "num": 1, "emed_id": "e1", "figura": True,
                                          "figuras": [URL_F], "enunciado": "TEXTO NOVO DA API"})
    _escrever(base, "questoes", "t26_2", {"lista": "t26", "num": 2, "emed_id": "e2", "enunciado": "x"})
    _escrever(base, "questoes", "t26_9", {"lista": "t26", "num": 9, "emed_id": "e9", "sem_figura": True})
    return base


def test_cli_figuras_dry_run_nao_escreve(db_sintetico, tmp_path, capsys):
    """DoD 4 (1.1a): sem `--apply` e dry-run com a contagem -- nada gravado."""
    _chrome(db_sintetico, 1, 2)
    antes = _linha_q(db_sintetico, 1)
    assert emed_banco.main(["--figuras", str(_recaptura(tmp_path)), "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["atualizadas"], r["ausentes"], r["aplicado"]) == (1, ["e9"], False)
    assert _linha_q(db_sintetico, 1) == antes


def test_cli_figuras_apply_sem_expect_recusa(db_sintetico, tmp_path, capsys):
    """DoD 4 (1.1a): `--apply` exige `--expect N` -- recusa, nada gravado."""
    _chrome(db_sintetico, 1)
    antes = _linha_q(db_sintetico, 1)
    assert emed_banco.main(["--figuras", str(_recaptura(tmp_path)), "--apply"]) == 1
    assert "--expect" in capsys.readouterr().out
    assert _linha_q(db_sintetico, 1) == antes


def test_cli_figuras_apply_fixa_antes_e_mescla_so_a_figura(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 4 (1.1a): `--apply --expect N` segue o rito (COUNT-ASSERT + backup fixado quando ha
    `atualizadas`), imprime `ausentes` e nao troca o enunciado pelo da recaptura."""
    _chrome(db_sintetico, 1, 2)
    atos = []
    monkeypatch.setattr(emed_banco, "_fixar_antes",
                        lambda ato: atos.append(ato) or {"arquivo": "f.db", "sha256": "abc"})
    base = _recaptura(tmp_path)
    assert emed_banco.main(["--figuras", str(base), "--apply", "--expect", "2"]) == 2   # COUNT-ASSERT
    assert atos == [] and "figuras" not in (_linha_q(db_sintetico, 1)["extras"] or "")
    capsys.readouterr()
    assert emed_banco.main(["--figuras", str(base), "--apply", "--expect", "1"]) == 0
    out = capsys.readouterr().out
    assert len(atos) == 1 and "e9" in out and "FIXADO" in out
    linha = _linha_q(db_sintetico, 1)
    assert json.loads(linha["extras"])["figuras"] == [URL_F]
    assert linha["enunciado"] == _questao(1)["enunciado"]


def test_exportar_so_figuras_leva_so_as_chaves_de_figura(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 4 (1.1a): `--exportar --so-figuras` escreve `OUT/upd/<lista>_<num>.json` so com as chaves de
    figura + `emed_id`, e so dos docs que tem alguma -- nunca `solucao_medhub`, `enunciado`, `alternativas`."""
    _chrome(db_sintetico, 1, 2, 3)
    db.emed_mesclar_figuras({"e1": {"figura": True, "figuras": [URL_F], "figuras_alt": {"A": [URL_F]}},
                             "e3": {"sem_figura": True}})
    assert db.emed_upsert_solucoes([_solucao(1)])["novas"] == 1
    monkeypatch.setattr(emed_banco, "figura_data_uri", lambda u: "data:image/webp;base64,AAAA")
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out), "--so-figuras"]) == 0
    arquivos = sorted(p.name for p in (out / "upd").glob("*.json"))
    assert arquivos == ["t26_1.json", "t26_3.json"]
    d1 = json.loads((out / "upd" / "t26_1.json").read_text(encoding="utf-8"))
    assert d1 == {"emed_id": "e1", "figura": True, "figuras": [URL_F], "figuras_alt": {"A": [URL_F]},
                  "figuras_img": ["data:image/webp;base64,AAAA"]}
    d3 = json.loads((out / "upd" / "t26_3.json").read_text(encoding="utf-8"))
    assert d3 == {"emed_id": "e3", "sem_figura": True}
    for d in (d1, d3):
        assert not {"solucao_medhub", "enunciado", "alternativas"} & set(d)
    assert not (out / "questoes").exists()


# ---------------------------------------------------- hotfix 1.1b DoD 5: retratacao do sem_figura

#: Falso positivo REAL da regra antiga (quadro clinico) e o positivo verdadeiro da t40 Q6.
ENUNC_FP = "Febre e dor lombar. Diante do quadro clínico e laboratorial apresentado, a conduta é:"
ENUNC_VP = ("A análise do perfil glicêmico da última semana está demonstrada na tabela a seguir: "
            "Qual a conduta mais adequada para este caso clínico?")


def _semear_sem_figura(db_sintetico):
    """1 = falso positivo (com `figura` e `acerto_pct`, que ficam); 2 = positivo verdadeiro;
    3 = falso positivo que JA tem `figuras` (fora do escopo); 4 = sem marca."""
    assert db.emed_upsert_questoes([
        _questao(1, enunciado=ENUNC_FP, sem_figura=True, figura=True, acerto_pct=40),
        _questao(2, enunciado=ENUNC_VP, sem_figura=True),
        _questao(3, enunciado=ENUNC_FP, sem_figura=True, figuras=[URL_F]),
        _questao(4, enunciado=ENUNC_FP)])["novas"] == 4
    assert Path(db_sintetico).resolve() != (ROOT / "ipub.db").resolve()     # sentinela: nunca o real


def _cita(enunciado):
    import emed_api
    return bool(emed_api.CITA_FIGURA.search(enunciado))


def test_reavaliar_sem_figura_derruba_so_o_falso_positivo(db_sintetico):
    """Hotfix 1.1b DoD 5: so a linha com `sem_figura`, sem `figuras` e que a regra nova NAO marca perde
    o `sem_figura` (hash re-derivado); `figura`/`figuras`/outras chaves e as outras linhas ficam."""
    _semear_sem_figura(db_sintetico)
    antes = {n: _linha_q(db_sintetico, n) for n in (1, 2, 3, 4)}
    medida = db.emed_reavaliar_sem_figura(_cita, aplicar=False)
    assert (medida["atualizadas"], medida["iguais"], medida["listas"]) == (1, 1, ["t26_1"])
    assert {n: _linha_q(db_sintetico, n) for n in (1, 2, 3, 4)} == antes          # dry-run
    r = db.emed_reavaliar_sem_figura(_cita)
    assert (r["atualizadas"], r["listas"]) == (1, ["t26_1"])
    l1 = _linha_q(db_sintetico, 1)
    assert json.loads(l1["extras"]) == {"acerto_pct": 40, "figura": True}
    assert l1["hash"] == db.emed_hash_questao(l1) != antes[1]["hash"]
    for c in ("enunciado", "alternativas", "gabarito", "solucao", "emed_id"):
        assert l1[c] == antes[1][c], c
    for n in (2, 3, 4):
        assert _linha_q(db_sintetico, n) == antes[n], n


def test_reavaliar_sem_figura_e_idempotente(db_sintetico):
    """Hotfix 1.1b DoD 5: a 2a rodada nao muda nada."""
    _semear_sem_figura(db_sintetico)
    assert db.emed_reavaliar_sem_figura(_cita)["atualizadas"] == 1
    h = _linha_q(db_sintetico, 1)["hash"]
    r = db.emed_reavaliar_sem_figura(_cita)
    assert (r["atualizadas"], r["iguais"], r["listas"]) == (0, 1, [])
    assert _linha_q(db_sintetico, 1)["hash"] == h


def test_cli_reavaliar_sem_figura_dry_run_e_rito(db_sintetico, capsys, monkeypatch):
    """Hotfix 1.1b DoD 5: `--reavaliar-sem-figura` e dry-run por padrao (imprime as `lista_num`);
    `--apply` sem `--expect` recusa; `--expect` errado = COUNT-ASSERT; certo = backup FIXADO + grava."""
    _semear_sem_figura(db_sintetico)
    antes = _linha_q(db_sintetico, 1)
    assert emed_banco.main(["--reavaliar-sem-figura", "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["atualizadas"], r["listas"], r["aplicado"]) == (1, ["t26_1"], False)
    assert emed_banco.main(["--reavaliar-sem-figura", "--apply"]) == 1
    assert "--expect" in capsys.readouterr().out
    atos = []
    monkeypatch.setattr(emed_banco, "_fixar_antes",
                        lambda ato: atos.append(ato) or {"arquivo": "f.db", "sha256": "abc"})
    assert emed_banco.main(["--reavaliar-sem-figura", "--apply", "--expect", "2"]) == 2
    assert _linha_q(db_sintetico, 1) == antes and atos == []
    capsys.readouterr()
    assert emed_banco.main(["--reavaliar-sem-figura", "--apply", "--expect", "1"]) == 0
    out = capsys.readouterr().out
    assert len(atos) == 1 and "FIXADO" in out and "t26_1" in out
    assert "sem_figura" not in json.loads(_linha_q(db_sintetico, 1)["extras"])


# ------------------------------------- part 1.2 (P2): versao da Solucao, gate de cadeia, sensor

def test_versao_solucao_pura_seis_casos():
    """DoD 2 (1.2): `versao_solucao` -- 3 (v3), 2 (v2), 1 (texto que nao e cadeia: prosa, JSON torto,
    versao desconhecida) e 0 (vazio/None). A mesma funcao que o loader da Fase 1 vai usar."""
    assert db.versao_solucao(json.dumps(_v3(1))) == 3
    assert db.versao_solucao(json.dumps(_v2(1))) == 2
    assert db.versao_solucao("Pede a conduta. Gabarito B.") == 1
    assert db.versao_solucao('{"versao": 3, "cadeia": [') == 1
    assert db.versao_solucao('{"versao": 4}') == 1
    assert db.versao_solucao("") == 0 and db.versao_solucao("   ") == 0
    assert db.versao_solucao(None) == 0


def _sem_objetivo(doc):
    """O doc da Solucao sem a chave `objetivo` (o writer aceita; o gate nao)."""
    doc = dict(doc)
    doc.pop("objetivo", None)
    return doc


def _semear_gate(db_sintetico, sols, nums=(1, 2), lista="t26", **extra_q):
    """Questoes `nums` da `lista` + Solucoes `sols` (docs) pelos writers reais, no banco sintetico."""
    assert Path(db_sintetico).resolve() != (ROOT / "ipub.db").resolve()     # sentinela: nunca o real
    tarefa = int(lista.lstrip("t"))
    assert db.emed_upsert_questoes([_questao(n, lista=lista, tarefa=tarefa, **extra_q)
                                    for n in nums])["novas"] == len(nums)
    if sols:
        c = db.emed_upsert_solucoes(sols)
        assert c["invalidas"] == [] and c["novas"] == len(sols)


def _simulado(tarefa_id):
    """Tarefa do plano com `area = Simulado` (a regra do hub) no banco sintetico."""
    conn = db.get_connection()
    try:
        db._ensure_plano_table(conn)
        conn.execute("INSERT INTO plano_tarefas (id, fonte, area, tema) VALUES (?, 'custom', "
                     "'Simulado', 'Simulado UERJ')", (tarefa_id,))
        conn.commit()
    finally:
        conn.close()


def test_gate_exportar_v3_completa_passa(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): todas com v3 e objetivo -> exit 0 e os arquivos saem."""
    _semear_gate(db_sintetico, [_v3(1), _v3(2)])
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out), "--sem-figuras"]) == 0
    assert "RECUSA" not in capsys.readouterr().out
    assert sorted(p.name for p in (out / "questoes").glob("*.json")) == ["t26_1.json", "t26_2.json"]


def test_gate_exportar_v1_recusa_sem_criar_out(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): Solucao v1 (prosa) -> RECUSA, exit 1, e `OUT` nem existe (gate antes do makedirs)."""
    _semear_gate(db_sintetico, [_v3(1), _solucao(2, objetivo="Indicação de insulina")])
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 1
    assert "RECUSA: t26 sem cadeia em Q2" in capsys.readouterr().out
    assert not out.exists()


def test_gate_exportar_sem_solucao_recusa(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): questao sem Solucao -> exit 1 (sem cadeia e sem objetivo)."""
    _semear_gate(db_sintetico, [_v3(1)])
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 1
    saida = capsys.readouterr().out
    assert "sem cadeia em Q2" in saida and "sem objetivo em Q2" in saida
    assert not out.exists()


def test_gate_exportar_v3_sem_objetivo_recusa(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): v3 valida mas sem `objetivo` (o writer aceita) -> exit 1."""
    _semear_gate(db_sintetico, [_v3(1), _sem_objetivo(_v3(2))])
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 1
    saida = capsys.readouterr().out
    assert "RECUSA: t26 sem objetivo em Q2" in saida and "sem cadeia" not in saida
    assert not out.exists()


def test_gate_exportar_sem_cadeia_motivo_passa_e_vazio_e_erro(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): `--sem-cadeia MOTIVO` deixa passar e imprime o motivo e os numeros;
    `--sem-cadeia ""` e erro de uso (exit 1, nada escrito)."""
    _semear_gate(db_sintetico, [])
    vazio = tmp_path / "vazio"
    assert emed_banco.main(["--exportar", "t26", "--out", str(vazio), "--sem-cadeia", ""]) == 1
    assert "--sem-cadeia" in capsys.readouterr().err
    assert not vazio.exists()
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out), "--sem-cadeia", "motivo-x"]) == 0
    saida = capsys.readouterr().out
    assert "motivo-x" in saida and "sem 2" in saida and "RECUSA" not in saida
    assert (out / "questoes" / "t26_1.json").is_file()


def test_gate_exportar_v2_passa_como_legado(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): a v2 e cadeia validada -> passa com o rotulo `legado v2: N`."""
    _semear_gate(db_sintetico, [_v3(1), _v2(2)])
    assert emed_banco.main(["--exportar", "t26", "--out", str(tmp_path / "exp")]) == 0
    assert "legado v2: 1" in capsys.readouterr().out


def test_gate_exportar_simulado_nao_se_aplica(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): lista cuja tarefa e `area = Simulado` no plano passa sem Solucao nenhuma."""
    _simulado(1794)
    _semear_gate(db_sintetico, [], lista="t1794", banca="UERJ 2022", executor="prova_pdf")
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t1794", "--out", str(out)]) == 0
    assert "simulado: gate de cadeia nao se aplica" in capsys.readouterr().out
    assert (out / "questoes" / "t1794_1.json").is_file()


def test_gate_exportar_so_figuras_nao_passa_pelo_gate(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): `--so-figuras` de lista v1 -> exit 0 (o patch de figura nao e entrada de lista)."""
    _semear_gate(db_sintetico, [_solucao(1), _solucao(2)])
    assert emed_banco.main(["--exportar", "t26", "--out", str(tmp_path / "exp"), "--so-figuras"]) == 0
    assert "RECUSA" not in capsys.readouterr().out


def test_gate_exportar_spoiler_nao_entra_na_conta(db_sintetico, tmp_path, capsys):
    """DoD 3 (1.2): a questao spoiler (fora do hub) sem Solucao nao derruba a lista."""
    hupe = "RJ - Universidade do Estado do Rio de Janeiro - UERJ (Hospital Universitário Pedro Ernesto - HUPE)"
    _semear_gate(db_sintetico, [_v3(1)], nums=(1,))
    assert db.emed_upsert_questoes([_questao(2, banca=f"{hupe}, 2022", executor="emed_api")])["novas"] == 1
    out = tmp_path / "exp"
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 0
    assert "spoiler UERJ fora: [2]" in capsys.readouterr().out
    c = emed_banco.cobertura_cadeia([q for q in db.emed_listar_questoes("t26")
                                     if not emed_banco.fora_do_hub(q)], db.emed_listar_solucoes("t26"))
    assert (c["n"], c["v3"], c["sem"], c["sem_cadeia"], c["sem_objetivo"]) == (1, 1, 0, [], [])


def test_status_sensor_de_cadeia_por_lista(db_sintetico, capsys):
    """DoD 4 (1.2): o `--status` ganha `v3 | v2 | v1 | sem | sem_obj` por lista (todas as questoes
    do banco) e `[WARN] SEM_CADEIA` para lista fora de simulado com v1 + sem > 0. Exit 0 sempre."""
    _semear_gate(db_sintetico, [_v3(1), _sem_objetivo(_v3(2))])                              # v3
    _semear_gate(db_sintetico, [_sem_objetivo(_v2(1, lista="t40"))], nums=(1,), lista="t40")  # v2
    _semear_gate(db_sintetico, [_solucao(1, lista="t61")], lista="t61")                       # v1 + sem
    _simulado(1794)
    _semear_gate(db_sintetico, [], nums=(1,), lista="t1794")                                  # simulado
    assert emed_banco.main(["--status", "--json"]) == 0
    por = {s["lista"]: s for s in _json_saida(capsys)}
    chaves = ("v3", "v2", "v1", "sem", "sem_obj")
    assert tuple(por["t26"][k] for k in chaves) == (2, 0, 0, 0, 1)
    assert tuple(por["t40"][k] for k in chaves) == (0, 1, 0, 0, 1)
    assert tuple(por["t61"][k] for k in chaves) == (0, 0, 1, 1, 2)
    assert tuple(por["t1794"][k] for k in chaves) == (0, 0, 0, 1, 1)
    assert emed_banco.main(["--status"]) == 0
    saida = capsys.readouterr().out
    assert "v3 | v2 | v1 | sem | sem_obj" in saida
    assert [ln for ln in saida.splitlines() if ln.startswith("[WARN]")] == ["[WARN] SEM_CADEIA: t61 (2/2)"]


# ------------------- Lote 2 part 2.1 (M-031): fontes -> rotulo -> referencia (rotulos SINTETICOS)
# O repo e publico por ora (REFORMA-CHECKPOINT.md:53): nenhum rotulo daqui vem do banco real.

def test_fonte_rotulos_corte_r0_formatos_f1_f2_f3_e_vazios():
    """DoD 2 (2.1), R0: corta em `;` so com profundidade 0 de parenteses e sem digito logo depois;
    apara e descarta os vazios. F1 (rotulo unico), F2 (`;` dentro de parenteses), F3 (`AAAA;vol:pag`)."""
    assert db.fonte_rotulos("SBX Consenso Ficticio 2020") == ["SBX Consenso Ficticio 2020"]          # F1
    f2 = "Autor A, Autor B. Titulo ficticio. Rev Fict (2019; 12: 34-40); SBX Consenso 2021"
    assert db.fonte_rotulos(f2) == ["Autor A, Autor B. Titulo ficticio. Rev Fict (2019; 12: 34-40)",
                                    "SBX Consenso 2021"]                                            # F2
    f3 = "Autor C. Titulo ficticio. Rev Fict 2019;240:578; ZZA Manual 2018"
    assert db.fonte_rotulos(f3) == ["Autor C. Titulo ficticio. Rev Fict 2019;240:578", "ZZA Manual 2018"]
    assert db.fonte_rotulos("SBX 2020;  ; ZZA Manual ;") == ["SBX 2020", "ZZA Manual"]
    assert db.fonte_rotulos("") == [] and db.fonte_rotulos(None) == [] and db.fonte_rotulos(" ; ") == []


_CASOS_FONTE = [
    # (rotulo sintetico, subconjunto esperado da saida)
    ("Resumo Tireoide Ficticia §2.3",                                                         # R4 propria
     dict(status="ok", motivo=None, classe="citacao", tipo="propria", sigla="MEDHUB", ano=None,
          documento="Tireoide Ficticia", detalhe="§2.3")),
    ("resumo tireoide ficticia",
     dict(status="ok", tipo="propria", sigla="MEDHUB", documento="tireoide ficticia", detalhe=None)),
    ("Apostila EMED Endocrinologia Ficticia (vol. 2)",                                        # R4 terceiro
     dict(status="ok", classe="citacao", tipo="terceiro", sigla="EMED", ano=None,
          documento="Endocrinologia Ficticia", detalhe="vol. 2")),
    ("SBX Diretriz Ficticia de Exemplo 2021 (cap. 3)",                                        # R4 publica, R7b
     dict(status="ok", classe="citacao", tipo="publica", sigla="SBX", ano=2021,
          documento="Diretriz Ficticia de Exemplo", detalhe="cap. 3")),
    ("Fulano Beltrano -- Tratado Ficticio de Clinica",                                        # R7a autor
     dict(status="ok", tipo="publica", sigla="Fulano Beltrano", ano=None,
          documento="Tratado Ficticio de Clinica", detalhe=None)),
    ("SBX/ZZA -- Consenso Ficticio",                                                          # R7a so siglas
     dict(status="ok", sigla="SBX/ZZA", documento="Consenso Ficticio")),
    ("SBX Consenso 2019 -- Capitulo Ficticio",                                                # R7a: Y ao detalhe
     dict(status="ok", sigla="SBX", ano=2019, documento="Consenso", detalhe="Capitulo Ficticio")),
    ("Consenso ficticio de exemplo (ZZA)",                                                    # R7c
     dict(status="ok", sigla="ZZA", ano=None, documento="Consenso ficticio de exemplo", detalhe="ZZA")),
    ("Fulano II Revisao 2019",                                                                # R7d; romano
     dict(status="ok", sigla="Fulano", ano=2019, documento="II Revisao")),
    ("SBX: Diretriz Ficticia 2020",                                                           # `: ` com sigla
     dict(status="ok", sigla="SBX", ano=2020, documento="Diretriz Ficticia")),
    ("ZZA 2020",                                                                              # R8: vazio com ano
     dict(status="ok", sigla="ZZA", ano=2020, documento="")),
    ("Figura do enunciado não capturada",                                                     # R3
     dict(status="nao_referencia", motivo="nota", classe="nota", tipo=None, sigla=None)),
    ("Tabela ausente na captura",
     dict(status="nao_referencia", motivo="nota", classe="nota")),
    ("ver a discussão do fórum da questão",                                                   # R5 minuscula
     dict(status="nao_referencia", motivo="prosa", classe="nota", tipo="publica")),
    ("Observação: tema recorrente em prova",                                                  # R5 `: ` sem sigla
     dict(status="nao_referencia", motivo="prosa", classe="nota", tipo="publica")),
    ("Aula 3 do modulo ficticio",                                                             # remissao a aula
     dict(status="sem_parse", motivo="sem_emissor", classe="nota", tipo="publica")),
    ("SBX Consenso 2019 e Atualizacao 2021",                                                  # R6 dois anos
     dict(status="sem_parse", motivo="multi_fonte", classe="citacao", tipo="publica")),
    ("SBX Consenso + ZZA Manual",                                                             # R6 ` + `
     dict(status="sem_parse", motivo="multi_fonte", classe="citacao")),
    ("Manual Ficticio de Condutas",                                                           # R7e
     dict(status="sem_parse", motivo="sem_emissor", classe="citacao", tipo="publica")),
    ("ZZA",                                                                                   # R8
     dict(status="sem_parse", motivo="sem_documento", classe="citacao", sigla="ZZA")),
]


@pytest.mark.parametrize("rotulo, esperado", _CASOS_FONTE, ids=[c[0][:28] for c in _CASOS_FONTE])
def test_fonte_estruturada_regras_r1_r8_e_classe(rotulo, esperado):
    """DoD 2 (2.1) + ALTERA (classe): um caso de cada `tipo`, `Autor -- Titulo`, nota e prosa,
    `multi_fonte`, `sem_emissor`, `sem_documento`; `classe` = citacao | nota por ocorrencia."""
    saida = db.fonte_estruturada(rotulo)
    assert {k: saida[k] for k in esperado} == esperado


def test_fonte_estruturada_url_pmid_doi_saem_com_o_traco():
    """DoD 2 (2.1), R1: URL, PMID tirado de URL do PubMed e DOI saem do texto com o ` -- ` que os precede."""
    r = db.fonte_estruturada("ZZA Consenso Ficticio -- https://pubmed.ncbi.nlm.nih.gov/12345678/")
    assert (r["status"], r["url"], r["pmid"], r["doi"]) == (
        "ok", "https://pubmed.ncbi.nlm.nih.gov/12345678/", "12345678", None)
    assert (r["sigla"], r["documento"], r["detalhe"]) == ("ZZA", "Consenso Ficticio", None)
    r = db.fonte_estruturada("QWE Guideline Ficticio 2022 -- 10.1234/fict.2022.001")
    assert (r["doi"], r["url"], r["ano"], r["documento"]) == ("10.1234/fict.2022.001", None, 2022,
                                                            "Guideline Ficticio")
    r = db.fonte_estruturada("SBX Portal Ficticio https://exemplo.invalid/pagina")
    assert (r["url"], r["pmid"], r["documento"]) == ("https://exemplo.invalid/pagina", None, "Portal Ficticio")


def test_fonte_estruturada_ano_detalhe_e_data():
    """DoD 2 (2.1), R2 + R6: ano dentro de data ou de numero nao conta; sem ano na cabeca, vale o
    UNICO ano do detalhe; o detalhe junta os parenteses de 1o nivel e o trecho a partir do 1o `§`."""
    for rotulo in ("ZZA Nota Tecnica Ficticia de 12/03/2019", "ZZA Manual Ficticio 2019-05-01",
                   "ZZA Boletim Ficticio 120190"):
        r = db.fonte_estruturada(rotulo)
        assert (r["status"], r["ano"]) == ("ok", None), rotulo
    r = db.fonte_estruturada("ZZA Consenso Ficticio (atualizado em 2018)")
    assert (r["ano"], r["detalhe"], r["documento"]) == (2018, "atualizado em 2018", "Consenso Ficticio")
    r = db.fonte_estruturada("ZZA Consenso Ficticio (2018; revisao 2020)")
    assert (r["status"], r["ano"]) == ("ok", None)          # dois anos no detalhe: nenhum vale
    assert db.fonte_estruturada("Resumo Tema Ficticio (tabela 2) §3")["detalhe"] == "tabela 2 | §3"
    assert db.fonte_estruturada("Resumo Tema Ficticio §3 (tabela 2)")["detalhe"] == "§3 (tabela 2)"


def test_chave_referencia_normalizada_e_saida_deterministica():
    """DoD 2 (2.1), R9: chave = SIGLA|ano-ou-vazio|documento, casefold e espacos colapsados; a mesma
    entrada da a mesma saida (corte e parser puros)."""
    assert db.chave_referencia("ZZA", 2020, "  Consenso   Ficticio ") == "zza|2020|consenso ficticio"
    assert db.chave_referencia("zza", None, "CONSENSO ficticio") == "zza||consenso ficticio"
    chaves = {"status", "motivo", "classe", "tipo", "sigla", "ano", "documento", "detalhe",
              "url", "doi", "pmid"}
    for rotulo, _ in _CASOS_FONTE:
        a, b = db.fonte_estruturada(rotulo), db.fonte_estruturada(rotulo)
        assert a == b and set(a) == chaves
    texto = "; ".join(r for r, _ in _CASOS_FONTE)
    assert db.fonte_rotulos(texto) == db.fonte_rotulos(texto)


# --- writer de sincronizacao (DoD 3), CLI (DoD 4) e sensor (DoD 5), no banco sintetico do Lote 0

_FONTES_SINT = {("t26", 1): "Resumo Tireoide Ficticia §2; Figura do enunciado não capturada",
                ("t26", 2): "Resumo Tireoide Ficticia §4",
                ("t40", 1): "Apostila EMED Endocrinologia Ficticia (vol. 2)",
                ("t40", 2): "",
                ("t61", 1): "SBX Diretriz Ficticia 2021; Manual Ficticio de Condutas"}


def _hash_solucao(solucao, divergente, fontes, objetivo):
    """A formula do `hash` de `emed_solucoes` (s199: texto + divergente + fontes + objetivo), escrita
    de novo aqui de proposito: o teste da part 2.2 prova que o gate da fonte nao a muda."""
    import hashlib
    canon = json.dumps({"solucao": solucao, "divergente": divergente, "fontes": fontes,
                        "objetivo": objetivo}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(canon.encode("utf-8")).hexdigest()


def _semear_legado(sols):
    """Linhas de `emed_solucoes` como o ESTOQUE de antes do gate da part 2.2, por SQL direto e so em
    banco sintetico: `fontes` com prosa, nota ou `sem_parse`, que o writer de hoje recusa no delta
    (Solucao nova ou `fontes` alterado). O `hash` segue a formula do writer."""
    assert Path(db.DB_PATH).resolve() != (ROOT / "ipub.db").resolve()       # sentinela: nunca o real
    conn = db.get_connection()
    try:
        db._ensure_emed_tables(conn)
        for s in sols:
            sol, fon, obj = s["solucao"].strip(), s["fontes"].strip(), s.get("objetivo", "")
            div = int(bool(s.get("divergente")))
            conn.execute("INSERT INTO emed_solucoes (lista, num, solucao, divergente, fontes, objetivo, "
                         "hash, cunhado_em, atualizado_em) VALUES (?, ?, ?, ?, ?, ?, ?, "
                         "'2026-10-01 10:00:00', '2026-10-01 10:00:00')",
                         (s["lista"], s["num"], sol, div, fon, obj, _hash_solucao(sol, div, fon, obj)))
        conn.commit()
    finally:
        conn.close()


def _trocar_fontes_legado(lista, num, fontes):
    """O `fontes` do estoque trocado por fora do writer (SQL direto, banco sintetico): exercita a
    `atualizada` do `referencias_sincronizar` sem passar pelo gate da part 2.2."""
    assert Path(db.DB_PATH).resolve() != (ROOT / "ipub.db").resolve()       # sentinela: nunca o real
    con = sqlite3.connect(db.DB_PATH)
    try:
        con.execute("UPDATE emed_solucoes SET fontes = ? WHERE lista = ? AND num = ?", (fontes, lista, num))
        con.commit()
    finally:
        con.close()


def _semear_fontes(db_sintetico, questoes=False):
    """5 Solucoes v1 com `fontes` sinteticas (uma lista de cada `tipo`) como ESTOQUE (part 2.2: pelo
    writer, o delta com prosa/nota/`sem_parse` e recusado; o estoque e anterior ao gate); com
    `questoes`, tambem as questoes (o `--status` simples so lista quem tem questao)."""
    assert Path(db_sintetico).resolve() != (ROOT / "ipub.db").resolve()     # sentinela: nunca o real
    if questoes:
        assert db.emed_upsert_questoes([_questao(n, lista=l, tarefa=int(l[1:]))
                                        for (l, n) in _FONTES_SINT])["novas"] == 5
    _semear_legado([_solucao(n, lista=l, fontes=f) for (l, n), f in _FONTES_SINT.items()])
    assert len(db.emed_listar_solucoes()) == 5


def _tabelas_ref(caminho):
    con = sqlite3.connect(caminho)
    try:
        return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' "
                                          "AND name IN ('referencia', 'solucao_referencia')")}
    finally:
        con.close()


def _sha(caminho):
    import hashlib
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def _contagem(r):
    return {k: r[k] for k in ("solucoes", "com_fontes", "rotulos", "ok", "nao_referencia", "sem_parse",
                              "n_nota", "referencias_novas", "novas", "atualizadas", "iguais",
                              "sem_vinculo")}


_ESPERADO_1o = dict(solucoes=5, com_fontes=4, rotulos=6, ok=4, nao_referencia=1, sem_parse=1, n_nota=1,
                    referencias_novas=3, novas=4, atualizadas=0, iguais=0, sem_vinculo=1)


def test_referencia_ddl_idempotente_duas_fks_e_check(db_sintetico):
    """DoD 3 (2.1): `_ensure_referencia_tables` 2x; as 2 FKs de `solucao_referencia` (referencia e a
    composta `(lista, num)` -> `emed_solucoes`, CASCADE); `tipo` fora do CHECK e recusado."""
    conn = db.get_connection()
    try:
        db._ensure_emed_tables(conn)
        db._ensure_referencia_tables(conn)
        db._ensure_referencia_tables(conn)
        fks = conn.execute("PRAGMA foreign_key_list(solucao_referencia)").fetchall()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO referencia (chave, sigla, documento, tipo) VALUES ('x', 'X', 'd', 'outro')")
    finally:
        conn.close()
    por_fk = {}
    for _id, _seq, tabela, de, para, _upd, on_delete, _m in fks:
        por_fk.setdefault((tabela, on_delete), set()).add((de, para))
    assert por_fk == {("referencia", "NO ACTION"): {("referencia_id", "id")},
                      ("emed_solucoes", "CASCADE"): {("lista", "lista"), ("num", "num")}}
    assert _tabelas_ref(db_sintetico) == {"referencia", "solucao_referencia"}


def test_referencias_sincronizar_dry_run_apply_e_reexecucao(db_sintetico):
    """DoD 3 (2.1): `aplicar=False` nao roda DDL e mede; o apply grava as mesmas contagens com as
    invariantes; o leitor devolve os vinculos na ordem; rodar de novo da 0 mudancas; `fontes` intacto."""
    _semear_fontes(db_sintetico)
    hashes = {(s["lista"], s["num"]): (s["fontes"], s["hash"]) for s in db.emed_listar_solucoes()}
    seco = db.referencias_sincronizar(aplicar=False)
    assert _contagem(seco) == _ESPERADO_1o and seco["motivos"] == {"nota": 1, "sem_emissor": 1}
    assert _tabelas_ref(db_sintetico) == set() and db.referencias_por_solucao() == {}
    feito = db.referencias_sincronizar()
    assert _contagem(feito) == _ESPERADO_1o and feito["referencias_sem_vinculo"] == 0
    assert feito["novas"] + feito["atualizadas"] + feito["iguais"] + feito["sem_vinculo"] == 5
    assert feito["ok"] + feito["nao_referencia"] + feito["sem_parse"] == feito["rotulos"]
    vinc = db.referencias_por_solucao()
    assert sorted(vinc) == [("t26", 1), ("t26", 2), ("t40", 1), ("t61", 1)]
    assert [(v["ordem"], v["chave"], v["detalhe"]) for v in vinc[("t26", 1)]] == [
        (1, "medhub||tireoide ficticia", "§2")]
    assert vinc[("t26", 2)][0]["chave"] == vinc[("t26", 1)][0]["chave"]          # uma referencia, 2 vinculos
    assert [(v["ordem"], v["tipo"], v["ano"]) for v in vinc[("t61", 1)]] == [(1, "publica", 2021)]
    de_novo = db.referencias_sincronizar()
    assert (de_novo["novas"], de_novo["atualizadas"], de_novo["referencias_novas"],
            de_novo["iguais"], de_novo["sem_vinculo"]) == (0, 0, 0, 4, 1)
    assert {(s["lista"], s["num"]): (s["fontes"], s["hash"]) for s in db.emed_listar_solucoes()} == hashes


def test_referencias_atualizada_preserva_verificacao_da_mesma_ordem_e_chave(db_sintetico):
    """DoD 3 (2.1): Solucao atualizada (fontes mudou) preserva `verificada_em` e `substrato` do vinculo
    de mesma `(ordem, chave)`; o vinculo novo nasce nao verificado (nulo); nenhuma referencia e apagada."""
    _semear_fontes(db_sintetico)
    db.referencias_sincronizar()
    con = sqlite3.connect(db_sintetico)
    con.execute("UPDATE solucao_referencia SET verificada_em = '2026-10-11', substrato = 'canonico' "
                "WHERE lista = 't61' AND num = 1 AND ordem = 1")
    con.commit()
    con.close()
    novo = "SBX Diretriz Ficticia 2021; Manual Ficticio de Condutas; ZZA Manual Ficticio 2020"
    _trocar_fontes_legado("t61", 1, novo)     # part 2.2: pelo writer, o `sem_parse` no delta e recusado
    r = db.referencias_sincronizar()
    assert (r["novas"], r["atualizadas"], r["iguais"], r["referencias_novas"]) == (0, 1, 3, 1)
    v = db.referencias_por_solucao()[("t61", 1)]
    assert [(x["ordem"], x["verificada_em"], x["substrato"]) for x in v] == [
        (1, "2026-10-11", "canonico"), (3, None, None)]
    _trocar_fontes_legado("t61", 1, "Manual Ficticio de Condutas")
    r = db.referencias_sincronizar()
    assert (r["atualizadas"], r["sem_vinculo"], r["referencias_sem_vinculo"]) == (1, 1, 2)
    con = sqlite3.connect(db_sintetico)
    try:
        assert con.execute("SELECT COUNT(*) FROM referencia").fetchone()[0] == 4
    finally:
        con.close()


def _status_estranho(original):
    def falso(rotulo):
        r = original(rotulo)
        return dict(r, status="outro") if r["tipo"] == "terceiro" else r
    return falso


@pytest.mark.parametrize("quebra", ["rotulos", "solucoes", "orfa"])
def test_referencias_invariante_quebrada_e_rollback_sem_gravar(db_sintetico, monkeypatch, quebra):
    """DoD 3 (2.1): cada invariante e conferida dentro da transacao -- `ok + nao_referencia +
    sem_parse = rotulos`, `novas + atualizadas + iguais + sem_vinculo = COUNT(*)` e, no 1o apply,
    nenhuma referencia sem vinculo. Quebrada = `ValueError` e rollback (nem as tabelas ficam)."""
    _semear_fontes(db_sintetico)
    if quebra == "rotulos":
        monkeypatch.setattr(db, "fonte_estruturada", _status_estranho(db.fonte_estruturada))
    elif quebra == "solucoes":
        ler = db._emed_ler
        monkeypatch.setattr(db, "_emed_ler", lambda conn, tabela, colunas, lista=None:
                            ler(conn, tabela, colunas, lista)[1:])
    else:
        monkeypatch.setattr(db, "_vinculos_gravar", lambda *a, **k: None)
    with pytest.raises(ValueError):
        db.referencias_sincronizar()
    assert _tabelas_ref(db_sintetico) == set()


def test_referencias_falha_no_meio_nao_deixa_nada_gravado(db_sintetico, monkeypatch):
    """DoD 3 (2.1): uma falha no meio da escrita (2a Solucao) desfaz tudo, DDL inclusive."""
    _semear_fontes(db_sintetico)
    antes = _sha(db_sintetico)
    gravar, chamadas = db._vinculos_gravar, []

    def quebra_na_segunda(*a, **k):
        chamadas.append(1)
        if len(chamadas) == 2:
            raise RuntimeError("falha sintetica no meio")
        return gravar(*a, **k)

    monkeypatch.setattr(db, "_vinculos_gravar", quebra_na_segunda)
    with pytest.raises(RuntimeError):
        db.referencias_sincronizar()
    assert _tabelas_ref(db_sintetico) == set() and _sha(db_sintetico) == antes


def test_cli_referencias_dry_run_nao_muda_o_banco(db_sintetico, capsys):
    """DoD 4 (2.1): `--referencias` sem `--apply` imprime as contagens, `nao_ok: X/Y (Z%)` e o
    histograma de `motivo`; o sha256 do banco sintetico fica igual."""
    _semear_fontes(db_sintetico)
    antes = _sha(db_sintetico)
    assert emed_banco.main(["--referencias"]) == 0
    out = capsys.readouterr().out
    assert "solucoes=5" in out and "rotulos=6" in out and "referencias_novas=3" in out
    assert "nao_ok: 2/6 (33.3%)" in out and "n_nota=1" in out
    assert "motivo nota: 1" in out and "motivo sem_emissor: 1" in out
    assert _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()


def test_cli_referencias_rito_expect_apply_e_reexecucao(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 4 (2.1): `--apply` sem `--expect` = exit 1; `--expect` divergente = exit 2 (N = novas +
    atualizadas, em Solucoes); o apply FIXA sempre antes da 1a escrita e grava; de novo = 0 mudancas."""
    _semear_fontes(db_sintetico)
    antes = _sha(db_sintetico)
    atos = []
    monkeypatch.setattr(emed_banco, "_fixar_antes",
                        lambda ato: atos.append(ato) or {"arquivo": "f.db", "sha256": "abc"})
    assert emed_banco.main(["--referencias", "--apply"]) == 1
    assert "--expect" in capsys.readouterr().out
    regua = _regua_segue(tmp_path, monkeypatch)        # part 2.3: o apply exige --regua (SEGUE)
    assert emed_banco.main(["--referencias", "--apply", "--expect", "3", "--regua", regua]) == 2
    assert "COUNT-ASSERT" in capsys.readouterr().out
    assert _sha(db_sintetico) == antes and atos == []
    assert emed_banco.main(["--referencias", "--apply", "--expect", "4", "--regua", regua, "--json"]) == 0
    r = _json_saida(capsys)
    assert r["aplicado"] is True and _contagem(r) == _ESPERADO_1o and len(atos) == 1
    assert r["fixado"] == {"arquivo": "f.db", "sha256": "abc"}
    assert _tabelas_ref(db_sintetico) == {"referencia", "solucao_referencia"}
    assert emed_banco.main(["--referencias", "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["novas"], r["atualizadas"], r["referencias_novas"], r["aplicado"]) == (0, 0, 0, False)


def test_cli_referencias_sem_fixado_recusa_sem_gravar(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 4 (2.1): o fixado que levanta = exit 1 e nada gravado (nem DDL)."""
    _semear_fontes(db_sintetico)
    antes = _sha(db_sintetico)

    def sem_ponto(ato):
        raise RuntimeError("sem ponto de retorno sintetico")

    monkeypatch.setattr(emed_banco, "_fixar_antes", sem_ponto)
    regua = _regua_segue(tmp_path, monkeypatch)        # part 2.3: o apply exige --regua (SEGUE)
    assert emed_banco.main(["--referencias", "--apply", "--expect", "4", "--regua", regua]) == 1
    assert "FIXADO" in capsys.readouterr().out
    assert _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()


def test_status_fontes_sensor_por_lista_e_warn(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 5 (2.1): `cobertura_fontes` (PURA) por lista -- rot/ok/nref/sem/terc/vinc + n_nota/pct_nota;
    sem as tabelas `vinc` = 0; `--status` simples fecha com `[WARN] FONTES_SEM_ESTRUTURA`; exit 0 e
    nada escrito. Uma lista de cada tipo: t26 propria (+ nota), t40 terceiro, t61 publica (+ sem_emissor)."""
    _semear_fontes(db_sintetico, questoes=True)
    antes = _sha(db_sintetico)
    assert emed_banco.main(["--status", "--fontes", "--json"]) == 0
    por = {d["lista"]: d for d in _json_saida(capsys)}
    chaves = ("rot", "ok", "nref", "sem", "terc", "vinc", "n_nota", "pct_nota")
    assert {k: tuple(d[k] for k in chaves) for k, d in por.items()} == {
        "t26": (3, 2, 1, 0, 0, 0, 1, 33.3), "t40": (1, 1, 0, 0, 1, 0, 0, 0.0),
        "t61": (2, 1, 0, 1, 0, 0, 0, 0.0)}
    assert emed_banco.main(["--status", "--fontes", "--lista", "t40"]) == 0
    out = capsys.readouterr().out
    assert "lista | rot | ok | nref | sem | terc | vinc | n_nota | pct_nota" in out
    assert "t40 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 0.0" in out and "t26 |" not in out
    assert emed_banco.main(["--status"]) == 0
    warns = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("[WARN]")]
    assert warns[-1] == "[WARN] FONTES_SEM_ESTRUTURA: 2 rótulos em 2 listas (ver --status --fontes)"
    assert all(w.startswith("[WARN] SEM_CADEIA") for w in warns[:-1])
    assert _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()
    monkeypatch.setattr(emed_banco, "_fixar_antes", lambda ato: {"arquivo": "f.db", "sha256": "abc"})
    regua = _regua_segue(tmp_path, monkeypatch)        # part 2.3: o apply exige --regua (SEGUE)
    assert emed_banco.main(["--referencias", "--apply", "--expect", "4", "--regua", regua]) == 0
    capsys.readouterr()
    assert emed_banco.main(["--status", "--fontes", "--json"]) == 0
    assert {d["lista"]: d["vinc"] for d in _json_saida(capsys)} == {"t26": 2, "t40": 1, "t61": 1}
    sols = [{"lista": "t9", "num": 1, "fontes": "SBX Diretriz 2020; ver nota"}]
    assert emed_banco.cobertura_fontes(sols, {("t9", 1): [{}]}) == [
        {"lista": "t9", "rot": 2, "ok": 1, "nref": 1, "sem": 0, "terc": 0, "vinc": 1, "n_nota": 1,
         "pct_nota": 50.0}]


# --- Fase 0 Lote 2 part 2.2: o gate da fonte no writer (evidence-governance v1.3 §7.1) -------------
# Rotulos SINTETICOS (siglas inventadas SBX/ZZA/QWE); nenhum rotulo real de Solucao.

_OK_PUB = "SBX 2020 Diretriz Ficticia A"
_OK_PUB2 = "ZZA 2021 Manual Ficticio B"
_OK_PUB3 = "QWE 2022 Guia Ficticio C"
_OK_PROPRIA = "Resumo Tema Ficticio §2"
_OK_TERCEIRO = "Apostila EMED Capitulo Ficticio (vol. 1)"
_BRIEF = ROOT / "docs" / "SOLUCAO-MEDHUB-BRIEF.md"


def _doc22(num, fontes, lista="t26", **extra):
    """Doc v1 da Solucao com `_doc_id` (a chave do `motivos`) e o `fontes` dado."""
    return _solucao(num, lista=lista, fontes=fontes, _doc_id=f"{lista}_{num}", **extra)


def _troca(**mudar):
    """`troca_fonte` valido (substrato do §3, data <= hoje, motivo), com os campos de `mudar`."""
    t = {"substrato": "fallback", "verificada_em": "2026-10-10", "motivo": "a 2a lente achou a certa"}
    t.update(mudar)
    return t


def _relogio(monkeypatch):
    """Relogio fixo do banco: hoje = 11/10/2026 (o `verificada_em` futuro e 12/10)."""
    import datetime as _dt
    monkeypatch.setattr(db, "agora", lambda: _dt.datetime(2026, 10, 11, 12, 0, 0))


def _carimbar(lista, num, ordem, verificada_em, substrato):
    """Verificacao posta a mao num vinculo (banco sintetico), para ver o que o writer preserva."""
    assert Path(db.DB_PATH).resolve() != (ROOT / "ipub.db").resolve()       # sentinela: nunca o real
    con = sqlite3.connect(db.DB_PATH)
    try:
        con.execute("UPDATE solucao_referencia SET verificada_em = ?, substrato = ? "
                    "WHERE lista = ? AND num = ? AND ordem = ?", (verificada_em, substrato, lista, num, ordem))
        con.commit()
    finally:
        con.close()


def test_gate_fonte_nova_ok_grava_com_vinculos_inclusive_terceiro(tmp_path, monkeypatch):
    """DoD 2 (2.2): Solucao nova com todos os rotulos `ok` grava, e os vinculos dela entram na mesma
    transacao (helper da 2.1), nao verificados; `terceiro` (apostila do EMED) marca e nunca recusa. Os
    vinculos sao os que o `referencias_sincronizar` derivaria: a sincronizacao seguinte da `iguais`."""
    _usar_db(tmp_path, monkeypatch)
    docs = [_doc22(1, f"{_OK_PUB}; {_OK_PROPRIA}"), _doc22(2, _OK_TERCEIRO),
            _doc22(3, f"{_OK_PUB2} (tabela 2) §4")]
    c = db.emed_upsert_solucoes(docs)
    assert (c["novas"], c["invalidas"], c["motivos"]) == (3, [], {})
    vinc = db.referencias_por_solucao()
    assert {k: [(v["ordem"], v["tipo"], v["verificada_em"], v["substrato"]) for v in vs]
            for k, vs in vinc.items()} == {
        ("t26", 1): [(1, "publica", None, None), (2, "propria", None, None)],
        ("t26", 2): [(1, "terceiro", None, None)],
        ("t26", 3): [(1, "publica", None, None)]}
    r = db.referencias_sincronizar(aplicar=False)
    assert (r["novas"], r["atualizadas"], r["iguais"], r["referencias_novas"]) == (0, 0, 3, 0)


@pytest.mark.parametrize("fontes, motivo", [
    ("ver a discussao no porque da certa", "rotulo_nao_referencia:prosa"),
    (f"{_OK_PUB}; Figura do enunciado não capturada", "rotulo_nao_referencia:nota"),
    ("Manual Ficticio de Condutas", "rotulo_sem_parse:sem_emissor"),
    ("", "fonte_vazia"),
    ("  ;  ", "fonte_vazia"),
])
def test_gate_fonte_nova_com_prosa_nota_ou_vazia_vai_para_invalidas(tmp_path, monkeypatch, fontes,
                                                                     motivo):
    """DoD 2 (2.2): Solucao nova exige >= 1 rotulo e todos `ok` no parser unico; senao vai para
    `invalidas` e `motivos` diz por que (`fonte_vazia` ou `rotulo_<status>:<motivo>`, sem o texto
    do rotulo). A outra do lote grava; a recusada nao deixa linha nem vinculo."""
    _usar_db(tmp_path, monkeypatch)
    c = db.emed_upsert_solucoes([_doc22(1, fontes), _doc22(2, _OK_PUB)])
    assert (c["novas"], c["invalidas"], c["motivos"]) == (1, ["t26_1"], {"t26_1": motivo})
    assert [s["num"] for s in db.emed_listar_solucoes()] == [2]
    assert list(db.referencias_por_solucao()) == [("t26", 2)]


def test_gate_legada_com_fontes_identico_e_sem_parse_e_iguais(tmp_path, monkeypatch):
    """DoD 2 (2.2): a linha do estoque com `fontes` identico ao do banco (depois do `strip`) nao passa
    pelo gate: reingerida igual = `iguais`; com outro texto e o mesmo `fontes` = `atualizada`, e os
    vinculos dela (com a verificacao carimbada) ficam intactos. Mudar o `fontes` sem limpar o
    `sem_parse` e recusado."""
    _usar_db(tmp_path, monkeypatch)
    legado = f"{_OK_PUB}; Manual Ficticio de Condutas"
    _semear_legado([_solucao(1, fontes=legado)])
    db.referencias_sincronizar()
    _carimbar("t26", 1, 1, "2026-10-01", "canonico")
    antes = db.referencias_por_solucao()
    c = db.emed_upsert_solucoes([_doc22(1, legado)])
    assert (c["iguais"], c["invalidas"], c["motivos"]) == (1, [], {})
    c = db.emed_upsert_solucoes([_doc22(1, "  " + legado + " ", solucao="Outro texto da solucao.")])
    assert (c["atualizadas"], c["invalidas"], c["motivos"]) == (1, [], {})
    assert db.referencias_por_solucao() == antes
    assert antes[("t26", 1)][0]["verificada_em"] == "2026-10-01"
    c = db.emed_upsert_solucoes([_doc22(1, f"{legado}; {_OK_PUB2}")])
    assert (c["atualizadas"], c["invalidas"], c["motivos"]) == (
        0, ["t26_1"], {"t26_1": "rotulo_sem_parse:sem_emissor"})
    assert db.emed_listar_solucoes()[0]["fontes"] == legado


def test_gate_remocao_sem_troca_fonte_e_recusada(tmp_path, monkeypatch):
    """DoD 2 (2.2): fonte que ja se estruturava (chave `ok` do `fontes` do banco) so sai ou troca com
    2a lente declarada, nunca por ausencia (s222). Sem `troca_fonte`: `invalidas`, motivo
    `troca_sem_2a_lente`, e o banco fica byte a byte. Mudar so o detalhe nao e remocao; prosa que sai
    nao pede troca (TD 4: a saida dela e a propria limpeza)."""
    _usar_db(tmp_path, monkeypatch)
    assert db.emed_upsert_solucoes([_doc22(1, f"{_OK_PUB}; {_OK_PUB2}")])["novas"] == 1
    antes = _sha(db.DB_PATH)
    for novo in (_OK_PUB, f"{_OK_PUB}; {_OK_PUB3}", f"{_OK_PUB3}; {_OK_PUB2}"):
        c = db.emed_upsert_solucoes([_doc22(1, novo)])
        assert (c["atualizadas"], c["invalidas"], c["motivos"]) == (
            0, ["t26_1"], {"t26_1": "troca_sem_2a_lente"}), novo
    assert _sha(db.DB_PATH) == antes
    c = db.emed_upsert_solucoes([_doc22(1, f"{_OK_PUB} (tabela 1); {_OK_PUB2}")])
    assert (c["atualizadas"], c["invalidas"]) == (1, [])
    _semear_legado([_solucao(2, fontes=f"{_OK_PUB}; ver nota da aula")])
    c = db.emed_upsert_solucoes([_doc22(2, _OK_PUB)])
    assert (c["atualizadas"], c["invalidas"], c["motivos"]) == (1, [], {})


def test_gate_remocao_com_troca_fonte_valida_grava_e_carimba(tmp_path, monkeypatch):
    """DoD 2 (2.2): com `troca_fonte` valido (substrato do §3, `verificada_em` <= hoje, motivo) a troca
    grava; o vinculo novo (chave fora do `fontes` antigo) ganha `verificada_em` e `substrato` da
    declaracao, e o da mesma `(ordem, chave)` preserva o seu. O `fontes` antigo fica no fixado do
    rito (F137), nao no banco."""
    _usar_db(tmp_path, monkeypatch)
    _relogio(monkeypatch)
    assert db.emed_upsert_solucoes([_doc22(1, f"{_OK_PUB}; {_OK_PUB2}")])["novas"] == 1
    _carimbar("t26", 1, 1, "2026-10-01", "canonico")
    novo = f"{_OK_PUB}; {_OK_PUB3}"
    c = db.emed_upsert_solucoes([_doc22(1, novo, troca_fonte=_troca(verificada_em="2026-10-11"))])
    assert (c["atualizadas"], c["invalidas"], c["motivos"]) == (1, [], {})
    v = db.referencias_por_solucao()[("t26", 1)]
    assert [(x["ordem"], x["chave"], x["verificada_em"], x["substrato"]) for x in v] == [
        (1, "sbx|2020|diretriz ficticia a", "2026-10-01", "canonico"),
        (2, "qwe|2022|guia ficticio c", "2026-10-11", "fallback")]
    s = db.emed_listar_solucoes()[0]
    assert s["fontes"] == novo and s["hash"] == _hash_solucao(s["solucao"], 0, novo, "")


@pytest.mark.parametrize("troca, motivo", [
    (_troca(substrato="memoria"), "troca_sem_2a_lente:substrato"),
    (_troca(verificada_em="2026-10-12"), "troca_sem_2a_lente:verificada_em"),
    (_troca(verificada_em="10/10/2026"), "troca_sem_2a_lente:verificada_em"),
    (_troca(motivo="   "), "troca_sem_2a_lente:motivo"),
    ("pesquisei e achei", "troca_sem_2a_lente:forma"),
])
def test_gate_troca_fonte_torta_e_recusada(tmp_path, monkeypatch, troca, motivo):
    """DoD 2 (2.2): `troca_fonte` torto -- substrato fora do §3, data futura ou fora de AAAA-MM-DD,
    motivo vazio, ou nao e objeto -- nao e 2a lente: recusado, com o campo no motivo; banco intacto."""
    _usar_db(tmp_path, monkeypatch)
    _relogio(monkeypatch)
    assert db.emed_upsert_solucoes([_doc22(1, f"{_OK_PUB}; {_OK_PUB2}")])["novas"] == 1
    antes = _sha(db.DB_PATH)
    c = db.emed_upsert_solucoes([_doc22(1, f"{_OK_PUB}; {_OK_PUB3}", troca_fonte=troca)])
    assert (c["atualizadas"], c["invalidas"], c["motivos"]) == (0, ["t26_1"], {"t26_1": motivo})
    assert _sha(db.DB_PATH) == antes


def test_gate_dry_run_sha256_igual_e_json_mostra_motivos(tmp_path, monkeypatch, capsys):
    """DoD 2 (2.2): o dry-run mede pelo mesmo caminho (mesmos `invalidas` e `motivos` do apply) e o
    banco fica byte a byte; o `--json` do `--solucoes` mostra `motivos`. O apply grava so a valida."""
    _usar_db(tmp_path, monkeypatch)
    assert db.emed_upsert_solucoes([_doc22(1, f"{_OK_PUB}; {_OK_PUB2}")])["novas"] == 1
    base = tmp_path / "lote"
    _escrever(base, "solucoes", "t26_1", _solucao(1, fontes=_OK_PUB))
    _escrever(base, "solucoes", "t26_2", _solucao(2, fontes="ver o porque da certa"))
    _escrever(base, "solucoes", "t26_3", _solucao(3, fontes=_OK_TERCEIRO))
    esperado = {"t26_1": "troca_sem_2a_lente", "t26_2": "rotulo_nao_referencia:prosa"}
    antes = _sha(db.DB_PATH)
    seco = db.emed_upsert_solucoes(emed_banco.ler_docs(str(base), "solucoes"), aplicar=False)
    assert (seco["novas"], seco["invalidas"], seco["motivos"]) == (1, ["t26_1", "t26_2"], esperado)
    assert _sha(db.DB_PATH) == antes
    assert emed_banco.main(["--solucoes", str(base), "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["motivos"], r["aplicado"]) == (esperado, False) and _sha(db.DB_PATH) == antes
    assert emed_banco.main(["--solucoes", str(base), "--apply", "--expect", "1", "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["novas"], r["invalidas"], r["motivos"], r["aplicado"]) == (
        1, ["t26_1", "t26_2"], esperado, True)
    assert sorted(db.referencias_por_solucao()) == [("t26", 1), ("t26", 3)]


def test_gate_falha_no_vinculo_desfaz_a_linha(tmp_path, monkeypatch):
    """DoD 2 (2.2): a linha e os vinculos dela vao numa transacao so -- uma falha ao gravar o vinculo
    desfaz tambem o `emed_solucoes` (e a DDL das tabelas da 2.1): banco byte a byte."""
    _usar_db(tmp_path, monkeypatch)
    _semear_legado([_solucao(1, fontes=_OK_PUB)])
    antes = _sha(db.DB_PATH)

    def quebra(*a, **k):
        raise RuntimeError("falha sintetica no vinculo")

    monkeypatch.setattr(db, "_vinculos_gravar", quebra)
    with pytest.raises(RuntimeError):
        db.emed_upsert_solucoes([_doc22(2, _OK_PUB2)])
    assert _sha(db.DB_PATH) == antes and [s["num"] for s in db.emed_listar_solucoes()] == [1]
    assert _tabelas_ref(db.DB_PATH) == set()

def test_gate_hash_de_linha_com_fontes_inalterado_fica_igual(tmp_path, monkeypatch):
    """DoD 2 (2.2): o gate nao entra no `hash` (s199: texto + divergente + fontes + objetivo); a linha
    com `fontes` inalterado reingerida tem o mesmo hash, e `troca_fonte` sobrando no doc nao muda nada."""
    _usar_db(tmp_path, monkeypatch)
    doc = _doc22(1, _OK_PUB)
    assert db.emed_upsert_solucoes([doc])["novas"] == 1
    h = db.emed_listar_solucoes()[0]["hash"]
    assert h == _hash_solucao(doc["solucao"], 0, _OK_PUB, "")
    c = db.emed_upsert_solucoes([dict(doc, troca_fonte=_troca())])
    assert (c["iguais"], c["invalidas"], c["motivos"]) == (1, [], {})
    assert db.emed_listar_solucoes()[0]["hash"] == h


def test_brief_exemplos_de_fontes_passam_no_parser():
    """DoD 4 (2.2): o `fontes` do exemplo JSON do brief (o literal de sempre) e o exemplo sintetico de
    cada familia da gramatica (evidence-governance §7.1) passam inteiros no parser unico, um de cada
    `tipo`."""
    texto = _BRIEF.read_text(encoding="utf-8")
    do_json = re.findall(r'"fontes": "([^"]*)"', texto)
    assert do_json == ["Consenso OPAS/MS/FEBRASGO/SBD 2017"]
    exemplos = re.findall(r"^\s*- `[^`]+` -> `([^`]+)`\s*$", texto, re.M)
    assert len(exemplos) == 3
    tipos = []
    for fontes in do_json + exemplos:
        estruturados = [db.fonte_estruturada(r) for r in db.fonte_rotulos(fontes)]
        assert estruturados and all(e["status"] == "ok" for e in estruturados), fontes
        tipos.append(estruturados[0]["tipo"])
    assert tipos[1:] == ["publica", "propria", "terceiro"]


def test_brief_da_solucao_e_portador_do_gate_contrato_revogado():
    """DoD 5 (2.2): o brief e o portador lido no ato pelo subagente que cunha a Solucao; fora da
    varredura, a lapide dele seria decorativa (F95). Entra por constante explicita (TD 6)."""
    import consistencia_check
    assert "docs/SOLUCAO-MEDHUB-BRIEF.md" in consistencia_check.PORTADORES_DOCS
    assert "docs/SOLUCAO-MEDHUB-BRIEF.md" in consistencia_check.portadores_derivados()


# --- Fase 0 Lote 2 part 2.3: amostra de 62 com semente gravada + regua de parada no apply (M-031) ----
# Rotulos SINTETICOS (siglas inventadas SBX/ZZA/QWE); nenhum rotulo real de Solucao. O arquivo da
# amostra vai para `PASTA_AMOSTRA`, apontada para `tmp_path` em todo teste.

_NOTA = "Figura do enunciado não capturada"          # nota (R3)
_REMISSAO = "Aula 3 do modulo ficticio"              # nota por remissao, com status sem_parse
_SEM_EMISSOR = "Manual Ficticio de Condutas"         # citacao sem_parse (R7e)
_AMOSTRA10 = [{"lista": "t80", "num": n, "fontes": _OK_PUB2} for n in range(1, 11)]


def _sols_amostra(listas=3, por=6, fontes=_OK_PUB):
    """Linhas de `emed_solucoes` sinteticas (`lista`, `num`, `fontes`): `listas` x `por`, todas com fonte."""
    return [{"lista": f"t{100 + i}", "num": n, "fontes": fontes}
            for i in range(listas) for n in range(1, por + 1)]


def _pop(n_ok=0, n_sem=0, n_nota=0, n_remissao=0, lista="t70"):
    """Populacao sintetica: uma Solucao por rotulo, na ordem ok -> sem_parse -> nota -> remissao."""
    fontes = ([_OK_PUB] * n_ok + [_SEM_EMISSOR] * n_sem + [_NOTA] * n_nota + [_REMISSAO] * n_remissao)
    return [{"lista": lista, "num": i, "fontes": f} for i, f in enumerate(fontes, 1)]


def _triada(sols, vereditos=None, padrao="ok"):
    """A amostra de TODAS as `sols` (por_lista = len) com cada rotulo `ok` triado: `padrao`, salvo o que
    `vereditos` diz por `(num, ordem)`."""
    am = emed_banco.amostra_arquivo(sols, "abc1234", por_lista=len(sols))
    for s in am["solucoes"]:
        for r in s["rotulos"]:
            if r["veredito"] is None and r["parse"]["status"] == "ok":
                r["veredito"] = (vereditos or {}).get((s["num"], r["ordem"]), padrao)
    return am


def _regua_segue(tmp_path, monkeypatch):
    """`--regua` com veredito SEGUE forcado (a regua em si tem os testes dela): o rito do apply da 2.1
    continua testavel com o gate da 2.3 no lugar."""
    arq = tmp_path / "amostra-segue.json"
    arq.write_text("{}", encoding="utf-8")
    real = emed_banco.regua_referencias
    monkeypatch.setattr(emed_banco, "regua_referencias",
                        lambda populacao, amostra: dict(real(populacao, amostra), veredito="SEGUE", motivos=[]))
    return str(arq)


def _spy_fixar(monkeypatch):
    atos = []
    monkeypatch.setattr(emed_banco, "_fixar_antes",
                        lambda ato: atos.append(ato) or {"arquivo": "f.db", "sha256": "abc"})
    return atos


# DoD 2: o sorteio puro

def test_amostra_referencias_mesma_semente_mesma_amostra_e_formula_declarada():
    """DoD 2 (2.3): mesma semente = mesma amostra (a ordem de entrada nao importa); outra semente = outra
    amostra; por lista vale `random.Random(f"{semente}:{lista}").sample(sorted(nums), min(2, n))`."""
    import random
    sols = _sols_amostra()
    a = emed_banco.amostra_referencias(sols, 0x9a5963f)
    assert a == emed_banco.amostra_referencias(list(reversed(sols)), 0x9a5963f)
    assert sorted(a["listas"]) == ["t100", "t101", "t102"] and a["curtas"] == {}
    for lista, nums in a["listas"].items():
        assert nums == sorted(random.Random(f"{0x9a5963f}:{lista}").sample(list(range(1, 7)), 2))
    assert emed_banco.amostra_referencias(sols, 0x1234567)["listas"] != a["listas"]


def test_amostra_referencias_lista_nova_nao_muda_as_outras():
    """DoD 2 (2.3): a semente por lista isola as listas -- acrescentar uma nao muda o sorteio das outras."""
    sols = _sols_amostra()
    antes = emed_banco.amostra_referencias(sols, 42)["listas"]
    mais = sols + [{"lista": "t999", "num": n, "fontes": _OK_PUB2} for n in range(1, 9)]
    depois = emed_banco.amostra_referencias(mais, 42)["listas"]
    assert {k: v for k, v in depois.items() if k != "t999"} == antes and len(depois["t999"]) == 2


def test_amostra_referencias_fontes_vazio_nunca_entra_e_lista_curta_e_reportada():
    """DoD 2 (2.3): `fontes` vazio (None, "", so espacos, so `;`) nunca entra; lista com 1 Solucao com
    fonte entra com 1 e sai em `curtas`; lista sem nenhuma nao aparece."""
    vazias = [{"lista": "t100", "num": n, "fontes": f} for n, f in ((10, ""), (11, None), (12, " ; "), (13, "  "))]
    sols = (_sols_amostra(listas=1, por=2) + vazias
            + [{"lista": "t200", "num": 1, "fontes": _OK_PUB}, {"lista": "t200", "num": 2, "fontes": ""},
               {"lista": "t300", "num": 1, "fontes": None}])
    for semente in range(20):
        a = emed_banco.amostra_referencias(sols, semente)
        assert a["listas"] == {"t100": [1, 2], "t200": [1]} and a["curtas"] == {"t200": 1}


def test_amostra_referencias_31_listas_com_2_ou_mais_dao_62():
    """DoD 2 (2.3): 31 listas com >= 2 Solucoes com fonte cada = 2 x 31 = 62, nenhuma curta."""
    sols = [{"lista": f"t{i}", "num": n, "fontes": _OK_PUB} for i in range(1, 32) for n in range(1, 3 + i % 5)]
    a = emed_banco.amostra_referencias(sols, 0x9a5963f)
    assert len(a["listas"]) == 31 and sum(len(v) for v in a["listas"].values()) == 62 and a["curtas"] == {}


# DoD 3: D1 (ida e volta) e o `--amostra-referencias`

def test_d1_ida_e_volta_passa_em_todo_ok_do_parser_e_pega_campo_montado_errado():
    """DoD 3 (2.3): a D1 passa em todo rotulo `ok` da tabela de casos do parser (2.1) e pega o campo
    montado errado (documento fora de ordem ou com palavra de fora, sigla e ano de outro rotulo);
    MEDHUB/EMED nao se conferem (derivadas); letra e digito colados nao enganam o token."""
    oks = [r for r, _ in _CASOS_FONTE if db.fonte_estruturada(r)["status"] == "ok"]
    assert len(oks) >= 10
    for rotulo in oks:
        assert emed_banco.d1_ida_e_volta(rotulo, db.fonte_estruturada(rotulo)) is None, rotulo
    rotulo = "SBX Diretriz Ficticia de Exemplo 2021 (cap. 3)"
    certo = db.fonte_estruturada(rotulo)
    assert emed_banco.d1_ida_e_volta(rotulo, dict(certo, documento="Ficticia Diretriz de Exemplo")) == "documento"
    assert emed_banco.d1_ida_e_volta(rotulo, dict(certo, documento="Diretriz Ficticia Outra")) == "documento"
    assert emed_banco.d1_ida_e_volta(rotulo, dict(certo, sigla="ZZA")) == "sigla"
    assert emed_banco.d1_ida_e_volta(rotulo, dict(certo, ano=2012)) == "ano"
    assert emed_banco.d1_ida_e_volta("SBX2019 Consenso Ficticio",
                                     {"sigla": "SBX", "ano": 2019, "documento": "Consenso Ficticio"}) is None


def test_cli_amostra_referencias_grava_so_na_pasta_amostra_com_a_forma(db_sintetico, tmp_path, monkeypatch,
                                                                       capsys):
    """DoD 3 (2.3): `--amostra-referencias HEX` escreve SO `PASTA_AMOSTRA/amostra-<hex>.json`: a semente
    (hex gravado + int), por Solucao `lista`/`num`/sha1 do `fontes`, por rotulo `ordem`/`rotulo`/o parse
    inteiro/`d1`/`veredito` null/`origem` null; imprime so contagens; o banco nao muda."""
    import hashlib
    _semear_fontes(db_sintetico)        # t26 (2 com fonte), t40 (1 com fonte + 1 vazia), t61 (1)
    pasta = tmp_path / "lote2"
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(pasta))
    antes = _sha(db_sintetico)
    assert emed_banco.main(["--amostra-referencias", "ABC1234"]) == 0
    out = capsys.readouterr().out
    assert [p.name for p in pasta.iterdir()] == ["amostra-abc1234.json"]
    am = json.loads((pasta / "amostra-abc1234.json").read_text(encoding="utf-8"))
    assert (am["semente"], am["semente_int"], am["por_lista"]) == ("abc1234", 0xabc1234, 2)
    assert am["curtas"] == {"t40": 1, "t61": 1}
    fontes = {(s["lista"], s["num"]): s["fontes"] for s in db.emed_listar_solucoes()}
    assert [(s["lista"], s["num"]) for s in am["solucoes"]] == [("t26", 1), ("t26", 2), ("t40", 1), ("t61", 1)]
    for s in am["solucoes"]:
        f = fontes[(s["lista"], s["num"])]
        assert s["sha1_fontes"] == hashlib.sha1(f.encode("utf-8")).hexdigest()
        assert [(r["ordem"], r["rotulo"]) for r in s["rotulos"]] == list(enumerate(db.fonte_rotulos(f), 1))
        for r in s["rotulos"]:
            assert set(r) == {"ordem", "rotulo", "parse", "d1", "veredito", "origem"}
            assert r["parse"] == db.fonte_estruturada(r["rotulo"])
            assert (r["veredito"], r["origem"]) == (None, None)
            assert r["d1"] == ("ok" if r["parse"]["status"] == "ok" else None)
    assert "solucoes=4" in out and "rotulos=6" in out and "ok=4" in out and "d1_falhas=0" in out
    assert "curtas=2" in out and "amostra-abc1234.json" in out
    assert "Ficticia" not in out and "Tireoide" not in out          # so contagens, nenhum rotulo
    assert _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()


def test_cli_amostra_referencias_d1_nasce_mal_atribuido_com_origem_d1(db_sintetico, tmp_path, monkeypatch,
                                                                      capsys):
    """DoD 3 (2.3): o rotulo `ok` cujo `documento` saiu montado errado nasce `mal_atribuido:documento`,
    `origem: D1`, `d1: falha:documento`; a contagem `d1_falhas` sai no `--json`."""
    _semear_fontes(db_sintetico)
    pasta = tmp_path / "lote2"
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(pasta))
    original = db.fonte_estruturada

    def torto(rotulo):
        r = original(rotulo)
        return dict(r, documento="Ficticia Diretriz") if r["sigla"] == "SBX" else r

    monkeypatch.setattr(db, "fonte_estruturada", torto)
    assert emed_banco.main(["--amostra-referencias", "abc1234", "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["solucoes"], r["rotulos"], r["ok"], r["d1_falhas"]) == (4, 6, 4, 1)
    am = json.loads((pasta / "amostra-abc1234.json").read_text(encoding="utf-8"))
    sbx = [x for s in am["solucoes"] for x in s["rotulos"] if x["parse"]["sigla"] == "SBX"]
    assert [(x["d1"], x["veredito"], x["origem"]) for x in sbx] == [
        ("falha:documento", "mal_atribuido:documento", "D1")]


@pytest.mark.parametrize("semente", ["9a5963", "9a5963fa", "xyz1234", " "])
def test_cli_amostra_referencias_semente_torta_recusa_sem_escrever(db_sintetico, tmp_path, monkeypatch, semente):
    """DoD 3 (2.3): a semente e um hex de 7 caracteres; outra coisa = erro de uso (exit 1), nada escrito."""
    pasta = tmp_path / "lote2"
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(pasta))
    assert emed_banco.main(["--amostra-referencias", semente]) == 1
    assert not pasta.exists()


def test_cli_amostra_referencias_nao_sobrescreve_a_triagem(db_sintetico, tmp_path, monkeypatch, capsys):
    """DoD 3 (2.3): o arquivo da amostra ja existe (com a triagem dentro) -> recusa, exit 1, intacto."""
    _semear_fontes(db_sintetico)
    pasta = tmp_path / "lote2"
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(pasta))
    assert emed_banco.main(["--amostra-referencias", "abc1234"]) == 0
    arq = pasta / "amostra-abc1234.json"
    arq.write_text(arq.read_text(encoding="utf-8").replace('"veredito": null', '"veredito": "ok"', 1),
                   encoding="utf-8")
    triado = arq.read_bytes()
    capsys.readouterr()
    assert emed_banco.main(["--amostra-referencias", "abc1234"]) == 1
    assert "RECUSA" in capsys.readouterr().out and arq.read_bytes() == triado


# DoD 4: a regua pura (so `classe = citacao`; nota fora de p e de a)

def test_regua_p_acima_de_10_para_e_a_igual_a_10_segue():
    """DoD 4 (2.3): `REGUA_LIMITE = 0.10` estrito -- p = 0,11 da PARA; p = 0,10 e a = 0,10 dao SEGUE;
    a = 0,20 da PARA. `p` e `a` saem como (num, den)."""
    assert emed_banco.REGUA_LIMITE == 0.10
    am = _triada(_AMOSTRA10, {(3, 1): "mal_atribuido:sigla"})
    r = emed_banco.regua_referencias(_pop(n_ok=80, n_sem=10) + _AMOSTRA10, am)
    assert (r["veredito"], r["p"], r["a"], r["motivos"]) == ("SEGUE", (10, 100), (1, 10), [])
    r = emed_banco.regua_referencias(_pop(n_ok=79, n_sem=11) + _AMOSTRA10, am)
    assert (r["veredito"], r["p"], r["motivos"]) == ("PARA", (11, 100), ["p 11/100 (11.0%) > 10%"])
    am = _triada(_AMOSTRA10, {(3, 1): "mal_atribuido:sigla", (4, 1): "mal_atribuido:ano"})
    r = emed_banco.regua_referencias(_pop(n_ok=90) + _AMOSTRA10, am)
    assert (r["veredito"], r["a"], r["motivos"]) == ("PARA", (2, 10), ["a 2/10 (20.0%) > 10%"])


def test_regua_tudo_limpo_segue_e_impreciso_nao_conta():
    """DoD 4 (2.3): tudo triado e limpo da SEGUE; `impreciso` nao conta; o histograma so tem nomes."""
    am = _triada(_AMOSTRA10, {(5, 1): "impreciso"})
    r = emed_banco.regua_referencias(_pop(n_ok=90) + _AMOSTRA10, am)
    assert (r["veredito"], r["motivos"], r["p"], r["a"]) == ("SEGUE", [], (0, 100), (0, 10))
    assert r["histograma"] == {"impreciso": 1, "ok": 9}


def test_regua_triagem_incompleta_para():
    """DoD 4 (2.3): um rotulo `ok` da amostra sem veredito = PARA ("triagem incompleta")."""
    am = _triada(_AMOSTRA10)
    am["solucoes"][0]["rotulos"][0]["veredito"] = None
    r = emed_banco.regua_referencias(_pop(n_ok=90) + _AMOSTRA10, am)
    assert (r["veredito"], r["motivos"]) == ("PARA", ["triagem incompleta: 1 rotulo(s) ok sem veredito"])


def test_regua_amostra_velha_para(monkeypatch):
    """DoD 4 (2.3): o sha1 do `fontes` de uma Solucao da amostra mudou (ou ela sumiu) = PARA ("amostra
    velha"); o parse mudou com o mesmo `fontes` (parser alterado depois do sorteio, TD 3) = PARA tambem."""
    am = _triada(_AMOSTRA10)
    trocada = [dict(s, fontes=_OK_PUB3) if s["num"] == 2 else s for s in _AMOSTRA10]
    r = emed_banco.regua_referencias(_pop(n_ok=90) + trocada, am)
    assert (r["veredito"], r["motivos"]) == ("PARA", ["amostra velha: 1 Solucao(oes) com fontes mudado ou "
                                                      "ausente desde o sorteio"])
    r = emed_banco.regua_referencias(_pop(n_ok=90) + _AMOSTRA10[1:], am)
    assert r["veredito"] == "PARA" and r["motivos"][0].startswith("amostra velha: 1 ")
    original = db.fonte_estruturada
    monkeypatch.setattr(db, "fonte_estruturada",
                        lambda rotulo: dict(original(rotulo), detalhe="outro"))
    r = emed_banco.regua_referencias(_pop(n_ok=90) + _AMOSTRA10, am)
    assert (r["veredito"], r["motivos"]) == ("PARA", ["amostra velha: o parse de 10 Solucao(oes) mudou desde o "
                                                      "sorteio (parser alterado = semente queimada)"])


def test_regua_mede_so_citacao_nota_fica_fora_de_p_e_a():
    """DoD 4 (2.3, TD 2): acrescentar 100 `nota` -- com status `nao_referencia` ou `sem_parse` (remissao)
    -- nao muda `p`; `n_nota`/`pct_nota` saem a parte; nota > 30% vira achado de conteudo, nao PARA;
    1 `nota` da amostra marcada `mal_atribuido:nao_referencia` sobe `a`."""
    base = _pop(n_ok=85, n_sem=5) + _AMOSTRA10
    am = _triada(_AMOSTRA10)
    r0 = emed_banco.regua_referencias(base, am)
    r1 = emed_banco.regua_referencias(base + _pop(n_nota=100, lista="t71"), am)
    r2 = emed_banco.regua_referencias(base + _pop(n_remissao=100, lista="t71"), am)
    assert r0["p"] == r1["p"] == r2["p"] == (5, 100)
    assert [r["n_nota"]["populacao"] for r in (r0, r1, r2)] == [0, 100, 100]
    assert (r1["pct_nota"]["populacao"], r1["veredito"]) == (50.0, "SEGUE")
    assert r0["achados"] == [] and r1["achados"] == ["nota 100/200 (50.0%) > 30% na populacao: achado de "
                                                     "conteudo (M-024/M-025), nao PARA"]
    sols = _AMOSTRA10 + [{"lista": "t80", "num": 11, "fontes": _NOTA}]
    am = _triada(sols)
    r = emed_banco.regua_referencias(base + sols[-1:], am)
    assert (r["a"], r["n_nota"]["amostra"], r["veredito"]) == ((0, 10), 1, "SEGUE")
    am["solucoes"][-1]["rotulos"][0]["veredito"] = "mal_atribuido:nao_referencia"
    r = emed_banco.regua_referencias(base + sols[-1:], am)
    assert r["a"] == (1, 10) and r["histograma"]["nota:mal_atribuido:nao_referencia"] == 1


def test_regua_citacao_fora_de_ok_conta_sem_triagem_e_vocabulario_fechado():
    """DoD 4 (2.3): a citacao `sem_parse` da amostra conta em `a` sem veredito; `mal_atribuido:<campo>`
    conta; um veredito fora do vocabulario = PARA."""
    sols = _AMOSTRA10[:9] + [{"lista": "t80", "num": 10, "fontes": _SEM_EMISSOR}]
    am = _triada(sols, {(1, 1): "mal_atribuido:tipo"})
    r = emed_banco.regua_referencias(_pop(n_ok=90) + sols, am)
    assert (r["a"], r["veredito"]) == ((2, 10), "PARA")
    assert r["histograma"] == {"mal_atribuido:tipo": 1, "ok": 8, "sem_parse:sem_emissor": 1}
    am = _triada(_AMOSTRA10, {(1, 1): "errado"})
    r = emed_banco.regua_referencias(_pop(n_ok=90) + _AMOSTRA10, am)
    assert (r["veredito"], r["motivos"]) == ("PARA", ["veredito fora do vocabulario: 1"])


def test_aplicar_vereditos_tokens_lista_num_ordem_puro_e_d1_manda():
    """DoD 6 (2.3), a entrada dos vereditos: tokens `lista_num#ordem=veredito[:campo]`; PURA (a amostra de
    entrada fica intacta); recusa forma, vocabulario, fora da amostra, o veredito da D1 (ela manda no
    campo dela), campo != nao_referencia em nota e o duplicado divergente."""
    sols = [{"lista": "t80", "num": 1, "fontes": f"{_OK_PUB}; {_NOTA}"}, {"lista": "t80", "num": 2, "fontes": _OK_PUB2}]
    am = emed_banco.amostra_arquivo(sols, "abc1234")
    am["solucoes"][1]["rotulos"][0].update(d1="falha:documento", veredito="mal_atribuido:documento", origem="D1")
    copia = json.loads(json.dumps(am))
    tokens = ["t80_1#1=ok", "t80_1#2=mal_atribuido:nao_referencia", "t80_2#1=ok", "t80_9#1=ok", "t80_1#1=bom",
              "lixo", "t80_1#2=mal_atribuido:sigla", "t80_1#1=impreciso", "t80_2#1=mal_atribuido:documento"]
    nova, rel = emed_banco.aplicar_vereditos(am, tokens)
    assert am == copia
    assert rel == {"aplicados": 3, "recusados": [
        ("t80_2#1=ok", "d1_manda"), ("t80_9#1=ok", "fora_da_amostra"), ("t80_1#1=bom", "vocabulario"),
        ("lixo", "forma"), ("t80_1#2=mal_atribuido:sigla", "nota_so_nao_referencia"),
        ("t80_1#1=impreciso", "duplicado_divergente")]}
    assert [(r["veredito"], r["origem"]) for s in nova["solucoes"] for r in s["rotulos"]] == [
        ("ok", "triagem"), ("mal_atribuido:nao_referencia", "triagem"), ("mal_atribuido:documento", "D1")]


# DoD 5: o gate no apply

def test_cli_referencias_apply_sem_regua_recusa_exit_1_sem_fixar(db_sintetico, capsys, monkeypatch):
    """DoD 5 (2.3): `--referencias --apply` sem `--regua` = exit 1; o fixado nao e chamado; nada gravado."""
    _semear_fontes(db_sintetico)
    antes, atos = _sha(db_sintetico), _spy_fixar(monkeypatch)
    assert emed_banco.main(["--referencias", "--apply", "--expect", "4"]) == 1
    assert "--regua" in capsys.readouterr().out
    assert atos == [] and _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()


def test_cli_referencias_apply_com_regua_para_exit_3_sem_fixar(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 5 (2.3): com veredito PARA (triagem incompleta; p 1/5) = exit 3 com `PARA: ...`, antes do
    COUNT-ASSERT; o fixado nao e chamado; nada gravado (nem DDL). `--regua` ilegivel = exit 1."""
    _semear_fontes(db_sintetico)
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(tmp_path / "lote2"))
    assert emed_banco.main(["--amostra-referencias", "abc1234"]) == 0
    arq = str(tmp_path / "lote2" / "amostra-abc1234.json")
    capsys.readouterr()
    antes, atos = _sha(db_sintetico), _spy_fixar(monkeypatch)
    for expect in ("4", "99"):
        assert emed_banco.main(["--referencias", "--apply", "--expect", expect, "--regua", arq]) == 3
        out = capsys.readouterr().out
        assert "PARA: " in out and "triagem incompleta: 4 rotulo(s) ok sem veredito" in out
        assert "COUNT-ASSERT" not in out
    assert emed_banco.main(["--referencias", "--regua", str(tmp_path / "nao_existe.json")]) == 1
    assert atos == [] and _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()


def test_cli_referencias_regua_dry_run_imprime_veredito_p_a_e_histograma_sem_conteudo(db_sintetico, tmp_path,
                                                                                      capsys, monkeypatch):
    """DoD 5 (2.3): `--referencias --regua ARQ` (dry-run) imprime o veredito, `p` e `a` com numerador e
    denominador, `n_nota` e o histograma -- so nomes de regra, nenhum rotulo; exit 0; o banco nao muda.
    Os vereditos entram pelos tokens (`aplicar_vereditos`). `--regua` fora do `--referencias` = exit 1."""
    _semear_fontes(db_sintetico)
    pasta = tmp_path / "lote2"
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(pasta))
    assert emed_banco.main(["--amostra-referencias", "abc1234"]) == 0
    arq = pasta / "amostra-abc1234.json"
    am = json.loads(arq.read_text(encoding="utf-8"))
    tokens = [f"{s['lista']}_{s['num']}#{r['ordem']}=ok" for s in am["solucoes"] for r in s["rotulos"]
              if r["parse"]["status"] == "ok"]
    am, rel = emed_banco.aplicar_vereditos(am, tokens)
    assert rel == {"aplicados": 4, "recusados": []}
    arq.write_text(json.dumps(am, ensure_ascii=False), encoding="utf-8")
    capsys.readouterr()
    antes = _sha(db_sintetico)
    assert emed_banco.main(["--referencias", "--regua", str(arq)]) == 0
    out = capsys.readouterr().out
    assert "regua (semente abc1234): PARA" in out
    assert "p (populacao, so citacao): 1/5 (20.0%)" in out and "a (amostra, so citacao): 1/5 (20.0%)" in out
    assert "PARA: p 1/5 (20.0%) > 10%" in out and "PARA: a 1/5 (20.0%) > 10%" in out
    assert "nota: populacao 1/6 (16.7%)" in out
    assert "regua sem_parse:sem_emissor: 1" in out and "regua ok: 4" in out and "regua nota: 1" in out
    assert "Ficticia" not in out and "Tireoide" not in out and "Condutas" not in out
    assert emed_banco.main(["--referencias", "--regua", str(arq), "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["regua"]["veredito"], r["regua"]["p"], r["regua"]["a"], r["aplicado"]) == ("PARA", [1, 5], [1, 5], False)
    assert emed_banco.main(["--status", "--regua", str(arq)]) == 1
    assert _sha(db_sintetico) == antes and _tabelas_ref(db_sintetico) == set()


def test_cli_referencias_apply_com_regua_segue_e_expect_certo_grava(db_sintetico, tmp_path, capsys, monkeypatch):
    """DoD 5 (2.3): populacao so com citacao `ok` (p = 0) + amostra inteira triada `ok` = SEGUE; o
    COUNT-ASSERT continua (exit 2); com `--expect` certo o fixado sai antes e grava; o JSON leva a regua."""
    fontes = {("t26", 1): _OK_PUB, ("t26", 2): _OK_PUB2, ("t40", 1): _OK_PROPRIA, ("t40", 2): _OK_TERCEIRO,
              ("t61", 1): f"{_OK_PUB3}; {_NOTA}"}
    _semear_legado([_solucao(n, lista=l, fontes=f) for (l, n), f in fontes.items()])
    pasta = tmp_path / "lote2"
    monkeypatch.setattr(emed_banco, "PASTA_AMOSTRA", str(pasta))
    assert emed_banco.main(["--amostra-referencias", "abc1234"]) == 0
    arq = pasta / "amostra-abc1234.json"
    am = json.loads(arq.read_text(encoding="utf-8"))
    am, _rel = emed_banco.aplicar_vereditos(am, [f"{s['lista']}_{s['num']}#{r['ordem']}=ok"
                                                 for s in am["solucoes"] for r in s["rotulos"]
                                                 if r["parse"]["status"] == "ok"])
    arq.write_text(json.dumps(am, ensure_ascii=False), encoding="utf-8")
    capsys.readouterr()
    antes, atos = _sha(db_sintetico), _spy_fixar(monkeypatch)
    assert emed_banco.main(["--referencias", "--apply", "--expect", "4", "--regua", str(arq)]) == 2
    assert "COUNT-ASSERT" in capsys.readouterr().out and atos == [] and _sha(db_sintetico) == antes
    assert emed_banco.main(["--referencias", "--apply", "--expect", "5", "--regua", str(arq), "--json"]) == 0
    r = _json_saida(capsys)
    assert (r["aplicado"], r["regua"]["veredito"], r["regua"]["p"], r["regua"]["a"]) == (True, "SEGUE", [0, 5], [0, 5])
    assert len(atos) == 1 and _tabelas_ref(db_sintetico) == {"referencia", "solucao_referencia"}
    assert len(db.referencias_por_solucao()) == 5
