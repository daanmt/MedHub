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
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 0
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
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 0
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
    assert emed_banco.main(["--exportar", "t26", "--out", str(out)]) == 0
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
             "respondido_em": "2026-09-26T10:00:00Z"}
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
    assert {"letra", "confianca", "riscadas", "racional", "elo"} <= chaves   # a leitura pegou
    assert _chaves_sem_destino(tmp_path, chaves) == []
    capsys.readouterr()
    _usar_db(tmp_path / "ctl", monkeypatch)
    (tmp_path / "ctl").mkdir()
    assert _chaves_sem_destino(tmp_path / "ctl", chaves | {"chave_nova"}) == ["chave_nova"]


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


def test_objetivos_gravados_no_banco_real_cabem_no_catalogo():
    """Leitura read-only do `ipub.db` real: todo objetivo gravado está na lista do tema da sua
    lista ou é 'outro: ...'. Sem banco (CI), pula."""
    import pytest
    real = ROOT / "ipub.db"
    if not real.is_file():
        pytest.skip("sem ipub.db")
    con = sqlite3.connect(f"file:{real}?mode=ro", uri=True)
    try:
        linhas = con.execute("SELECT lista, num, objetivo FROM emed_solucoes "
                             "WHERE COALESCE(objetivo, '') <> ''").fetchall()
    except sqlite3.OperationalError:
        pytest.skip("banco sem emed_solucoes.objetivo")
    finally:
        con.close()
    ruins = [(l, n, o) for l, n, o in linhas
             if db.solucao_v2_problemas(_v2(n, lista=l, objetivo=o))]
    assert ruins == []


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
