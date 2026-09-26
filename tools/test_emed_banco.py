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
