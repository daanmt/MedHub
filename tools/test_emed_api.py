"""Testes de tools/emed_api.py -- lista do EMED -> docs `questoes/*` pela API, SEM LLM (s202).

Regua do /ai-eng para o item 0 da s202 (decisao do operador, 26/09/2026): WHITELIST NA FRONTEIRA --
todo JSON produzido tem SO as chaves do escopo publico, e nada do resto da resposta (solucao,
forum, estatistica, video, percentuais, resposta do usuario) chega a disco, stdout ou stderr (o
mesmo predicado da purga (e)); TOKEN nunca impresso, arquivo rastreado ou fora do .gitignore =
recusa; DISCURSIVA sai e e declarada por numero e a contagem fecha em 3 (achadas = gravadas +
declaradas = --expect); TUDO OU NADA -- recusa nomeada e a pasta nem criada.

A rede nunca e tocada: `_get_json` e trocado por paginas sinteticas no formato do mapa de campos
MEDIDO na 1a corrida real (27/09/2026; era o do cic-0003 da s198, que pedia `exams[].institution`
e recusou a t3 inteira). O GOLDEN (a lista real Saude do Idoso, t3) le a saida local gitignored e PULA
sem ela -- nenhum texto EMED no git.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import emed_api  # noqa: E402
import emed_banco  # noqa: E402
from app.utils import db  # noqa: E402

PROF = "SENTINELA_PROFESSOR"          # tudo que vier marcado com isto NAO pode sair do processo
TOKEN = "TOKEN_SENTINELA_abc123"
CADERNO = "5e89c2cb-3ac4-4607-aef9-0c7a3d533ec8"


CAT_OUTRO = "4383bd62-e829-491e-8bb5-b40bd649817f"


def _exame(nome="SP - Sistema Único de  Saúde - SUS SP", ano=2020):
    """`exams[]` no formato MEDIDO na 1a corrida real (27/09, `--esquema` da t3): a instituicao e o
    catalogo `CATALOGO_INSTITUICAO` (o mesmo texto do `badges[0]`); nao existe `institution`."""
    return {"catalogs": {emed_api.CATALOGO_INSTITUICAO: {"id": "c1", "name": nome},
                         CAT_OUTRO: {"id": "c2", "name": f"{PROF} catalogo vizinho"}},
            "badges": [{"type": emed_api.CATALOGO_INSTITUICAO, "text": nome},
                       {"type": "YEAR", "text": str(ano)}, {"type": CAT_OUTRO, "text": f"{PROF} badge"}],
            "year": ano, "complement": "", "candidates_number": 999, "remuneration": 1}


def _item(emed_id, n_alts=4, correta=1, img=False, corretas=None):
    """Um item no formato da API real (mapa medido em 27/09), com TODO o conteudo que a whitelist
    tem de matar."""
    corretas = {correta} if corretas is None else set(corretas)
    item = {
        "id": emed_id,
        "answer_type": "MULTIPLE_CHOICE",
        "statement_text": (f"<p>Paciente {emed_id} com achado &amp; queixa.</p><p>Qual a conduta?</p>"
                           + ('<img src="figura.png">' if img else "")),
        "alternatives": [{"sanitized_body": f"<p>opção {i}</p>", "correct": i in corretas,
                          "answer_percentage": 12.5, "solution": f"{PROF} alternativa {i}"}
                         for i in range(n_alts)],
        "solution": {"sanitized_complete": f"{PROF} comentário geral", "author": f"{PROF} autor"},
        "topics": [{"name": "Medicina Preventiva"}, {"name": "Saúde do Idoso"}],
        "exams": [_exame()],
        "has_video_solution": True, "forum_id": 77,
        "user_solution": {"answer": "A", "nota": f"{PROF} resposta do usuario"},
        "accuracy_percentage": 41.0,
    }
    if n_alts == 0:                           # a discursiva REAL (t3 Q24, 27/09): sem a chave, tipo DISCURSIVE
        del item["alternatives"]
        item["answer_type"] = "DISCURSIVE"
    return item


def _lista(n, discursivas=(), **kw):
    """n itens em ordem; os numeros em `discursivas` (1-based) vem sem alternativas."""
    return [_item(str(4000000000 + i), n_alts=0 if i in discursivas else 4, **kw) for i in range(1, n + 1)]


def _fake_get(itens, chamadas=None):
    def get(url, headers, timeout=30):
        if chamadas is not None:
            chamadas.append(url)
        assert headers["Authorization"] == f"Bearer {TOKEN}"
        pag = int(url.split("page=")[1].split("&")[0])
        per = int(url.split("per_page=")[1].split("&")[0])
        return {"data": itens[(pag - 1) * per: pag * per], "meta": {"page": pag}}
    return get


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    """Token pela env, banco vazio (sem plano -> o `--caderno` manda), sem espera real."""
    monkeypatch.setenv("EMED_TOKEN", TOKEN)
    monkeypatch.delenv("EMED_REQUESTER_ID", raising=False)
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "vazio.db"))
    monkeypatch.setattr(emed_api, "_dormir", lambda s: None)
    return tmp_path


def _cli(tmp_path, *extra):
    return emed_api.main(["--lista", "t9", "--caderno", CADERNO, "--out", str(tmp_path / "out"), *extra])


# ---------------------------------------------------------------- whitelist na fronteira

def test_extrair_devolve_so_o_escopo_publico():
    q = emed_api.extrair(_item("4000000001", correta=2))
    assert set(q) <= set(emed_api.CHAVES_EXTRAIDAS)
    assert PROF not in json.dumps(q, ensure_ascii=False)
    assert q["emed_id"] == "4000000001" and q["gabaritos"] == ["C"]
    assert q["enunciado"] == "Paciente 4000000001 com achado & queixa.\nQual a conduta?"
    assert q["alternativas"][0] == ("A", "opção 0") and len(q["alternativas"]) == 4
    assert (q["banca"], q["ano"]) == ("SP - Sistema Único de Saúde - SUS SP, 2020", "2020")
    assert q["tags"] == "Medicina Preventiva > Saúde do Idoso" and q["figura"] is False


def test_banca_e_o_catalogo_da_instituicao_com_espacos_colapsados_e_o_1o_exame():
    """Regressao da 1a corrida real (27/09): o mapa do executor pedia `exams[].institution`, que a
    API nao tem -- a t3 inteira foi recusada. A instituicao e o catalogo fixo; o espaco duplo que a
    API traz em alguns nomes colapsa (a pagina o colapsa); questao com N exames usa o 1o."""
    item = _item("4000000001")
    item["exams"] = [_exame("SP - Universidade de São Paulo - USP - RP  (HC-FMRP)", 2021),
                     _exame("outra instituicao", 2019)]
    q = emed_api.extrair(item)
    assert (q["banca"], q["ano"]) == ("SP - Universidade de São Paulo - USP - RP (HC-FMRP), 2021", "2021")
    assert PROF not in json.dumps(q, ensure_ascii=False)


def test_exame_sem_o_catalogo_da_instituicao_e_recusa_nomeada_sem_valor():
    item = _item("4000000001")
    del item["exams"][0]["catalogs"][emed_api.CATALOGO_INSTITUICAO]
    with pytest.raises(emed_api.Recusa) as e:
        emed_api.extrair(item)
    assert emed_api.CATALOGO_INSTITUICAO in str(e.value) and "--esquema" in str(e.value)
    assert PROF not in str(e.value)


def test_discursiva_real_vem_sem_a_chave_e_objetiva_sem_a_chave_e_recusa():
    """Regressao da 1a corrida real (27/09): a discursiva da t3 (Q24) vem SEM `alternatives` e com
    `answer_type` DISCURSIVE -- a lista inteira foi recusada. Sem a chave e sem esse tipo segue recusa."""
    assert emed_api.extrair(_item("4000000001", n_alts=0))["alternativas"] == []
    objetiva = _item("4000000002")
    del objetiva["alternatives"]
    with pytest.raises(emed_api.Recusa, match="'alternatives' ausente"):
        emed_api.extrair(objetiva)


def test_alternativa_sai_em_uma_linha_e_pontuacao_solta_cola_na_anterior():
    """Regressao do golden t3 (27/09): na Q9 a API poe o ponto final da alternativa num bloco HTML
    a parte -> 'A) texto\\n.' quebrava o contrato 1 linha = 1 alternativa (o hub le por linha). A
    captura da s199 tinha 'A) texto.' -- e a forma que a pagina mostra."""
    item = _item("4000000001")
    item["alternatives"][0]["sanitized_body"] = "<p>Hipotireoidismo subclínico</p>."
    item["alternatives"][1]["sanitized_body"] = "<p>Primeira parte</p><p>segunda parte</p>"
    q = emed_api.extrair(item)
    assert q["alternativas"][0] == ("A", "Hipotireoidismo subclínico.")
    assert q["alternativas"][1] == ("B", "Primeira parte segunda parte")
    doc = emed_api.montar_docs([q], "t9", 9)[0]
    assert [ln[:3] for ln in doc["alternativas"].splitlines()] == ["A) ", "B) ", "C) ", "D) "]


def test_html_para_texto_quebras_entidades_tabela_e_figura():
    txt, fig = emed_api.html_para_texto("<p>a&nbsp;&lt;190</p><br>b<table><tr><td>x</td><td>y</td></tr></table>"
                                        '<img src="i.png">')
    assert txt == "a <190\nb\nx y" and fig is True          # '<190' e texto, nao tag (licao F108)


def test_propriedade_nada_alem_da_whitelist_chega_a_disco_ou_saida(ambiente, monkeypatch, capsys):
    """PROPRIEDADE (o predicado da purga (e)): todo arquivo gravado tem so chaves permitidas, e a
    sentinela do professor e o token nao aparecem em NENHUM byte de disco, stdout ou stderr."""
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(23, discursivas={7}, img=True)))
    assert _cli(ambiente, "--apply", "--expect", "23", "--conferir") == 0
    saida = capsys.readouterr()
    arquivos = list((ambiente / "out").rglob("*"))
    assert len([a for a in arquivos if a.is_file()]) == 22
    for a in arquivos:
        if a.is_file():
            bruto = a.read_text(encoding="utf-8")
            assert PROF not in bruto and TOKEN not in bruto
            assert set(json.loads(bruto)) <= set(emed_api.CHAVES_PUBLICAS) | set(emed_api.CHAVES_META)
    for canal in (saida.out, saida.err):
        assert PROF not in canal and TOKEN not in canal


def test_esquema_imprime_so_chaves_e_tipos(ambiente, monkeypatch, capsys):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(3)))
    assert _cli(ambiente, "--esquema") == 0
    out = capsys.readouterr().out
    assert "alternatives[].sanitized_body: str" in out and "solution.sanitized_complete: str" in out
    assert PROF not in out and "Paciente" not in out and TOKEN not in out
    assert not (ambiente / "out").exists()


# ---------------------------------------------------------------- contagem, discursiva, tudo ou nada

def test_discursiva_sai_declarada_e_a_contagem_fecha_em_3(ambiente, monkeypatch, capsys):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(5, discursivas={3})))
    assert _cli(ambiente, "--apply", "--expect", "5", "--json") == 0
    r = json.loads(capsys.readouterr().out)
    assert (r["achadas"], r["gravadas"], r["discursivas"]) == (5, 4, [3])
    nums = sorted(int(p.stem.split("_")[1]) for p in (ambiente / "out" / "questoes").iterdir())
    assert nums == [1, 2, 4, 5]                            # a numeracao e a da LISTA: o buraco fica


def test_expect_errado_recusa_e_nao_cria_a_pasta(ambiente, monkeypatch, capsys):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(5, discursivas={3})))
    assert _cli(ambiente, "--apply", "--expect", "4") == 2
    out = capsys.readouterr().out
    assert "RECUSA" in out and "achadas 5 (4 gravaveis + 1 discursiva" in out
    assert not (ambiente / "out").exists()


def test_certo_errado_e_alternativa_so_imagem_saem_declaradas_e_a_contagem_fecha(ambiente, monkeypatch, capsys):
    """Regressao da s218 (07/10/2026): 5 listas da Fase 1 (t833 t376 t110 t805 t826, ~200 questoes)
    eram recusadas INTEIRAS por 1-2 questoes que o hub nao desenha -- certo/errado (2 alternativas) e
    alternativa feita so de imagem (texto vazio, `<img>`). Saem DECLARADAS por numero e motivo, como a
    discursiva; a contagem fecha em achadas = gravadas + discursivas + fora."""
    so_imagem = _item("4000000004")
    so_imagem["alternatives"][2]["sanitized_body"] = '<p><img src="alt.png"></p>'
    # a forma REAL (t833 Q34, t376 Q19, t110 Q34, medida em 07/10): `sanitized_body` VAZIO e a imagem
    # so no `body` -- o `body` e lido so para saber SE ha imagem, nunca para texto
    real = _item("4000000006")
    for alt in real["alternatives"]:
        alt["sanitized_body"], alt["body"] = "", f'<p style="x"><img src="a.png" alt="{PROF}"></p>'
    itens = [_item("4000000001"), _item("4000000002", n_alts=2), _item("4000000003", n_alts=0),
             so_imagem, _item("4000000005"), real]
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(itens))
    assert _cli(ambiente, "--apply", "--expect", "6", "--json") == 0
    saida = capsys.readouterr().out
    r = json.loads(saida)
    assert (r["achadas"], r["gravadas"], r["discursivas"]) == (6, 2, [3])
    assert r["fora"] == {"2": "certo/errado (2 alternativas)", "4": "alternativa so com imagem",
                         "6": "alternativa so com imagem"}
    assert PROF not in saida
    nums = sorted(int(p.stem.split("_")[1]) for p in (ambiente / "out" / "questoes").iterdir())
    assert nums == [1, 5]                                  # a numeracao e a da LISTA: os buracos ficam


def test_alternativa_vazia_sem_imagem_segue_recusa(ambiente, monkeypatch, capsys):
    """O que vira declaracao e so a FORMA que o hub nao desenha; texto vazio sem imagem e defeito de
    dado (ou mudanca da API) e segue tudo ou nada."""
    vazia = _item("4000000002")
    vazia["alternatives"][1]["sanitized_body"] = "<p> </p>"
    monkeypatch.setattr(emed_api, "_get_json", _fake_get([_item("4000000001"), vazia]))
    assert _cli(ambiente, "--apply", "--expect", "2") == 2
    assert "Q2: enunciado ou alternativa vazia" in capsys.readouterr().out
    assert not (ambiente / "out").exists()


def test_expect_errado_conta_as_declaradas_fora(ambiente, monkeypatch, capsys):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get([_item("4000000001"), _item("4000000002", n_alts=2)]))
    assert _cli(ambiente, "--apply", "--expect", "1") == 2
    assert "achadas 2 (1 gravaveis + 0 discursiva(s) + 1 fora do formato" in capsys.readouterr().out


def test_apply_sem_expect_recusa_antes_da_rede(ambiente, monkeypatch, capsys):
    chamadas = []
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(3), chamadas))
    assert _cli(ambiente, "--apply") == 2
    assert "--expect" in capsys.readouterr().out and chamadas == []


@pytest.mark.parametrize("item, trecho", [
    (_item("4000000002", corretas=()), "Q2: 0 alternativas corretas"),
    (_item("4000000002", corretas=(0, 1)), "Q2: 2 alternativas corretas"),
    (_item("4000000002", n_alts=3), "Q2: 3 alternativas"),
    (_item("4000000002", n_alts=6), "Q2: 6 alternativas"),
    (_item("4000000001"), "emed_id repetido"),
])
def test_perturbado_e_recusa_nomeada_sem_gravar_nada(ambiente, monkeypatch, capsys, item, trecho):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get([_item("4000000001"), item, _item("4000000003")]))
    assert _cli(ambiente, "--apply", "--expect", "3") == 2
    out = capsys.readouterr().out
    assert trecho in out and PROF not in out
    assert not (ambiente / "out").exists()


def test_dry_run_e_o_default_e_nao_grava(ambiente, monkeypatch, capsys):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(4)))
    assert _cli(ambiente, "--expect", "4") == 0
    assert "dry-run" in capsys.readouterr().out
    assert not (ambiente / "out").exists()


# ---------------------------------------------------------------- ritmo e rede

def test_paginacao_em_ordem_com_pausa_entre_paginas(ambiente, monkeypatch, capsys):
    chamadas, pausas = [], []
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(45), chamadas))
    monkeypatch.setattr(emed_api, "_dormir", pausas.append)
    assert _cli(ambiente, "--expect", "45", "--pausa", "1.5") == 0
    assert [int(c.split("page=")[1].split("&")[0]) for c in chamadas] == [1, 2, 3]
    assert all("per_page=20" in c and CADERNO in c for c in chamadas)
    assert pausas == [1.5, 1.5]                                 # entre paginas, nunca antes da 1a


def test_pagina_repetida_pela_api_e_recusa_nao_laco(ambiente, monkeypatch, capsys):
    """API que ignora `page` devolve sempre a mesma pagina cheia: o emed_id repetido para tudo."""
    cheia = _lista(20)
    monkeypatch.setattr(emed_api, "_get_json", lambda url, headers, timeout=30: {"data": cheia})
    assert _cli(ambiente, "--expect", "20") == 2
    assert "emed_id repetido" in capsys.readouterr().out


def test_http_401_recusa_sem_vazar_o_token(ambiente, monkeypatch, capsys):
    def nega(url, headers, timeout=30):
        raise emed_api.Recusa(emed_api.mensagem_http(401))
    monkeypatch.setattr(emed_api, "_get_json", nega)
    assert _cli(ambiente, "--expect", "3") == 2
    out = capsys.readouterr().out
    assert "HTTP 401" in out and "token" in out and TOKEN not in out


# ---------------------------------------------------------------- token

def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    return repo


def test_token_rastreado_pelo_git_e_recusa(tmp_path):
    repo = _repo(tmp_path)
    (repo / ".gitignore").write_text(".emed_token\n", encoding="utf-8")
    arq = repo / ".emed_token"
    arq.write_text(TOKEN + "\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-f", ".emed_token"], check=True)
    with pytest.raises(emed_api.Recusa) as e:
        emed_api.ler_credencial(str(arq), env={}, raiz=str(repo))
    assert "RASTREADO" in str(e.value) and TOKEN not in str(e.value)


def test_token_fora_do_gitignore_e_recusa(tmp_path):
    repo = _repo(tmp_path)
    arq = repo / ".emed_token"
    arq.write_text(TOKEN + "\n", encoding="utf-8")
    with pytest.raises(emed_api.Recusa) as e:
        emed_api.ler_credencial(str(arq), env={}, raiz=str(repo))
    assert ".gitignore" in str(e.value) and TOKEN not in str(e.value)


def test_token_ignorado_monta_os_cabecalhos(tmp_path):
    repo = _repo(tmp_path)
    (repo / ".gitignore").write_text(".emed_token\n", encoding="utf-8")
    arq = repo / ".emed_token"
    arq.write_text(f"Bearer {TOKEN}\nx-requester-id: req-1\n", encoding="utf-8")
    h = emed_api.ler_credencial(str(arq), env={}, raiz=str(repo))
    assert h["Authorization"] == f"Bearer {TOKEN}" and h["x-requester-id"] == "req-1"
    assert h["x-vertical"] == "medicina"


def test_token_do_repo_esta_no_gitignore():
    r = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", ".emed_token"])
    assert r.returncode == 0


def test_sem_token_recusa_com_o_caminho(tmp_path):
    with pytest.raises(emed_api.Recusa) as e:
        emed_api.ler_credencial(str(tmp_path / "nao_existe"), env={}, raiz=str(tmp_path))
    assert "EMED_TOKEN" in str(e.value)


# ---------------------------------------------------------------- caderno x plano, ingestao, conferencia

def test_caderno_divergente_do_plano_e_recusa():
    plano = {"url_lista": f"https://med.estrategia.com/cadernos-e-simulados/cadernos/{CADERNO}/?per_page=20"}
    assert emed_api.caderno_da_lista(plano, None) == CADERNO
    assert emed_api.caderno_da_lista(None, f"https://x/cadernos/{CADERNO}/") == CADERNO
    with pytest.raises(emed_api.Recusa):
        emed_api.caderno_da_lista(plano, "11111111-2222-3333-4444-555555555555")
    with pytest.raises(emed_api.Recusa):
        emed_api.caderno_da_lista(None, None)


def test_conferir_acha_divergencia_por_emed_id_e_gabarito():
    docs = [{"num": 1, "emed_id": "a", "gabarito": "B"}, {"num": 2, "emed_id": "b", "gabarito": "C"},
            {"num": 3, "emed_id": "c", "gabarito": "D"}]
    banco = [{"num": "1", "emed_id": "a", "gabarito": "B"}, {"num": "2", "emed_id": "b", "gabarito": "A"},
             {"num": "3", "emed_id": "z", "gabarito": "D"}, {"num": "4", "emed_id": "d", "gabarito": "A"}]
    c = emed_api.conferir(docs, banco)
    assert c["iguais"] == [1] and c["divergentes"] == {2: ["gabarito"], 3: ["emed_id"]}
    assert c["so_no_banco"] == [4] and c["so_na_api"] == []


def test_docs_passam_pelo_ingerir(ambiente, monkeypatch, capsys):
    monkeypatch.setattr(emed_api, "_get_json", _fake_get(_lista(4, discursivas={2}, img=True)))
    assert _cli(ambiente, "--apply", "--expect", "4") == 0
    capsys.readouterr()
    assert emed_banco.main(["--ingerir", str(ambiente / "out"), "--apply", "--expect", "3", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["novas"] == 3
    q = {int(r["num"]): r for r in db.emed_listar_questoes("t9")}
    assert sorted(q) == [1, 3, 4] and q[1]["solucao"] in ("", None) and q[1]["executor"] == "emed_api"
    assert json.loads(q[1]["extras"]) == {"ano": "2020", "figura": True}


# ---------------------------------------------------------------- GOLDEN: a lista real (t3, Saude do Idoso)

GOLDEN_T3 = ROOT / "tmp" / "emed_api" / "t3" / "questoes"


def test_golden_t3_saude_do_idoso():
    """31 achadas = 30 gravadas + Q24 discursiva declarada (contagem confirmada pelo operador em
    26/09); lente 2 = emed_id e gabarito de cada numero iguais aos da captura t3 da s199 no ipub.db."""
    if not GOLDEN_T3.is_dir():
        pytest.skip("saida local da t3 ausente (gitignored): golden nao verificado")
    docs = [json.loads(p.read_text(encoding="utf-8")) for p in GOLDEN_T3.glob("t3_*.json")]
    assert sorted(d["num"] for d in docs) == [n for n in range(1, 32) if n != 24]
    for d in docs:
        assert set(d) <= set(emed_api.CHAVES_PUBLICAS) | set(emed_api.CHAVES_META)
        letras = [linha.split(")")[0] for linha in d["alternativas"].splitlines()]
        assert 4 <= len(letras) <= 5 and d["gabarito"] in letras
    banco = db.emed_listar_questoes("t3")
    if not banco:
        pytest.skip("t3 ausente do ipub.db: lente 2 nao verificada")
    c = emed_api.conferir(docs, banco)
    assert (len(c["iguais"]), c["divergentes"], c["so_no_banco"], c["so_na_api"]) == (30, {}, [], [])
