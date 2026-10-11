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
