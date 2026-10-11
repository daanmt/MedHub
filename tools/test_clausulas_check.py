"""test_clausulas_check.py -- item 1.10 (s187): clausula normativa tem terminal nomeado.

O defeito de fundo: **nao havia como saber quais regras o harness impoe e quais sao
prosa de honra.** F90 e F97 sao a forma aguda (clausula revogada seguiu prescrevendo, o
painel imprimiu PASSED); a cronica e 283 prescricoes em 23 portadores sem resposta para
"esta e verificada?".

O teste central e `test_anotacao_que_nomeia_gate_inexistente_e_BLOCK`: anotacao mentirosa
e PIOR que anotacao nenhuma, porque fabrica aparencia de cobertura. E o F90 um nivel
acima -- la o registro de portadores era manual e tinha buraco; aqui o registro de gates
e DERIVADO do auto_check e das suites, e toda anotacao e conferida contra ele.

Nasce BLOCK (nao WARN) pela mesma condicao que promoveu F79b e D5: o passivo e zero por
construcao -- nao existe anotacao nenhuma hoje, entao a primeira que mentir sera nova.

LIMITE DECLARADO: o gate confere que o nome do CHECK existe, nunca que aquele gate testa
MESMO aquela clausula. A metade semantica (a anotacao e honesta?) nao tem sensor e fica
com a leitura humana. O detector tambem e lexical (~86% de precisao amostrada): clausula
escrita sem marcador deontico e invisivel para o inventario inteiro.
"""
import datetime as dt
import hashlib
import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import clausulas_check as cn                                   # noqa: E402


def _portador(tmp_path, corpo, nome="contrato-sintetico.md"):
    p = tmp_path / nome
    p.write_text(corpo, encoding="utf-8")
    return str(p)


def _com(monkeypatch, path):
    monkeypatch.setattr(cn, "portadores", lambda: [path])


# --- o guarda central: anotacao que mente --------------------------------------------

def test_anotacao_que_nomeia_gate_inexistente_e_BLOCK(tmp_path, monkeypatch):
    """Anotacao mentirosa e pior que anotacao nenhuma -- fabrica aparencia de cobertura."""
    p = _portador(tmp_path, "- O agente **nunca** escreve FSRS no ensino. "
                            "<!-- CHECK: GATE_QUE_NAO_EXISTE -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks()
    assert resumo["com_check"] == 0, "gate inexistente NAO pode contar como cobertura"
    assert [a["tipo"] for a in achados] == ["gate_inexistente"]
    assert achados[0]["severidade"] == "BLOCK"


def test_anotacao_com_gate_REAL_conta_como_coberta(tmp_path, monkeypatch):
    """O nome tem que existir no registro DERIVADO -- aqui, uma suite real do repo."""
    assert "test_comprimento_total" in cn.registro_de_gates()
    p = _portador(tmp_path, "- O card **nunca** nasce acima do corte. "
                            "<!-- CHECK: test_comprimento_total -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks()
    assert resumo["com_check"] == 1 and achados == []


def test_registro_de_gates_e_DERIVADO_nao_enumerado(tmp_path):
    """Licao do F90/F95: registro mantido a mao tem buraco. Este sai do auto_check
    (slugs das descricoes) e das suites (modulo + funcao), por AST."""
    g = cn.registro_de_gates()
    assert "CONTRATO_REVOGADO" in g, "slug de gate do auto_check tem que entrar"
    assert "test_clausulas_check" in g, "o proprio modulo de teste tem que entrar"
    assert any(n.startswith("test_anotacao_que_nomeia") for n in g), \
        "funcao de teste tem que entrar -- inclusive as escritas nesta sessao"
    assert len(g) > 300


# --- o terminal DECLARADO -------------------------------------------------------------

def test_nao_verificavel_com_data_futura_e_terminal_valido(tmp_path, monkeypatch):
    p = _portador(tmp_path, "- O tom **deve** ser caloroso e motivacional. "
                            "<!-- NAO-VERIFICAVEL: julgamento de estilo (revisar: 2027-06-01) -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks(hoje=dt.date(2026, 9, 18))
    assert resumo["nao_verificaveis"] == 1 and achados == []


def test_nao_verificavel_SEM_data_e_BLOCK(tmp_path, monkeypatch):
    """Marca sem data nunca e revisitada -- vira isencao permanente por esquecimento.
    A data e o que torna a declaracao uma divida, e nao uma anistia."""
    p = _portador(tmp_path, "- O tom **deve** ser caloroso. "
                            "<!-- NAO-VERIFICAVEL: julgamento de estilo -->\n")
    _com(monkeypatch, p)
    achados, resumo = cn.run_checks()
    assert [a["tipo"] for a in achados] == ["nv_sem_data"]
    assert achados[0]["severidade"] == "BLOCK"
    assert resumo["nao_verificaveis"] == 0


def test_nao_verificavel_vencida_vira_WARN(tmp_path, monkeypatch):
    p = _portador(tmp_path, "- O tom **deve** ser caloroso. "
                            "<!-- NAO-VERIFICAVEL: estilo (revisar: 2026-01-01) -->\n")
    _com(monkeypatch, p)
    achados, _ = cn.run_checks(hoje=dt.date(2026, 9, 18))
    assert [a["tipo"] for a in achados] == ["nv_vencida"]
    assert achados[0]["severidade"] == "WARN"


# --- colocacao e escopo do detector ---------------------------------------------------

def test_anotacao_na_linha_ANTERIOR_vale():
    """Clausula longa fica ilegivel com a anotacao no fim -- a linha de cima e valida."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("<!-- CHECK: CONTRATO_REVOGADO -->\n"
                     "- A clausula revogada **nunca** segue prescrevendo.\n")
        cl = cn.extrair(p)
        assert len(cl) == 1 and cl[0]["check"] == "CONTRATO_REVOGADO"


def test_bloco_de_codigo_nao_e_clausula():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("```python\n# sempre valida antes de gravar\nx = 1\n```\n")
        assert cn.extrair(p) == []


def test_linha_de_tabela_e_heading_ficam_de_fora():
    """Exclusao MEDIDA, nao por gosto: 64 dos 347 hits crus eram doc de flag de CLI
    (que o argparse ja impoe) ou titulo de secao."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("## Clausula 4 -- o derivador\n"
                     "| `--sessao ID` | **Exige** o id. |\n"
                     "- O derivador **nunca** escreve no ipub.db.\n")
        cl = cn.extrair(p)
        assert len(cl) == 1 and "derivador **nunca** escreve" in cl[0]["texto"]


# --- estado do repo REAL ---------------------------------------------------------------

def test_repo_real_sem_anotacao_mentirosa():
    """O que justifica nascer BLOCK: a base e ZERO por construcao. Se esta cair, alguem
    anotou uma clausula com um gate que nao existe -- e e exatamente o caso a pegar."""
    achados, resumo = cn.run_checks()
    graves = [a for a in achados if a["severidade"] == "BLOCK"]
    assert graves == [], "; ".join(f"{a['tipo']}@{a['portador']}:{a['linha']}" for a in graves)
    print(f"  repo: {resumo['clausulas']} clausulas, {resumo['com_check']} com check, "
          f"{resumo['nao_verificaveis']} declaradas, {resumo['orfas']} orfas "
          f"({resumo['cobertura_pct']}% cobertas)")


def test_inventario_do_repo_tem_a_forma_esperada():
    """Ratchet frouxo: o inventario nao pode SUMIR (detector quebrado passando por
    limpo) nem explodir. Nao asserta numero exato -- os portadores sao editados."""
    _, resumo = cn.run_checks()
    assert 150 <= resumo["clausulas"] <= 600, resumo
    assert resumo["gates_conhecidos"] > 300, resumo


def test_catraca_pura_compara_com_a_base_dada():
    """s189 (pedido do /ai-eng): a contagem de orfas do 1.10 nao sobe sem DECLARACAO. Fase 0
    Lote 0 part-3: a base deixou de ser digitada (`BASE_ORFAS`, fixa em 127, tinha folga -- a
    contagem caiu a 126, a base nao desceu, e a 127a e a 128a entraram escondidas). A base agora
    e a contagem do HEAD, calculada; `catraca` so compara. Descer segue livre."""
    assert not hasattr(cn, "BASE_ORFAS"), "a base digitada morreu: quem da a base e o HEAD"
    assert cn.catraca(127, 127) is None and cn.catraca(124, 127) is None
    msg = cn.catraca(129, 127)
    assert msg and "2 clausula(s) nova(s)" in msg and "HEAD" in msg and "BASE_ORFAS" not in msg
    assert cn.catraca(5, None) is None, "sem base (repo sem HEAD) nao ha o que comparar"


# --- catraca derivada do HEAD (Fase 0 Lote 0 part-3) ----------------------------------
# Repos git SINTETICOS em tmp_path (padrao `test_emed_api._repo`): nada aqui le ou escreve o
# indice do repo real.

@pytest.fixture
def git_isolado(monkeypatch):
    """Esta suite roda DENTRO do pre-commit (check 2d), e o git exporta `GIT_INDEX_FILE` para o
    hook -- em `git commit -a` ou `git commit <caminhos>` o caminho e ABSOLUTO e aponta o indice
    do commit em curso do repo REAL. Herdado, `git -C <repo sintetico> add` escreveria nele.
    Limpar o ambiente `GIT_*` mantem o repo sintetico sintetico."""
    for chave in [k for k in os.environ if k.upper().startswith("GIT_")]:
        monkeypatch.delenv(chave, raising=False)


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=sintetico",
                           "-c", "user.email=sintetico@exemplo.invalid",
                           "-c", "commit.gpgsign=false", *args],
                          check=True, capture_output=True)


def _repo_git(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / ".claude" / "commands").mkdir(parents=True)
    (repo / "core" / "contracts").mkdir(parents=True)
    return repo


def _orfas(n, tag="x"):
    """n clausulas deonticas sem terminal, cada uma com texto proprio."""
    return "".join(f"- O agente **nunca** pula o passo {tag}{i}.\n" for i in range(n))


def test_catraca_derivada_do_head(tmp_path, git_isolado):
    """DoD 1 da part-3: orfas(indice) contra orfas(HEAD), lidas do git -- sem numero digitado."""
    repo = _repo_git(tmp_path)
    r = str(repo)
    skill = repo / ".claude" / "commands" / "sintetico.md"

    # repo vazio (sem HEAD, o 1o commit): None com aviso -- nunca excecao, nunca BLOCK
    skill.write_text(_orfas(5), encoding="utf-8")
    _git(repo, "add", "-A")
    assert cn.orfas_na_revisao("HEAD", root=r, gates=set()) is None
    sem_head = cn.catraca_contra_head("--staged", root=r, gates=set())
    assert sem_head["mensagem"] is None and "HEAD" in (sem_head["aviso"] or "")

    # HEAD com N = 3: 2 na skill + 1 no AGENTE.md. NAO contam: a anotada (tem terminal), o
    # README (nao e portador) e a subpasta (o glob dos portadores nao e recursivo).
    skill.write_text(_orfas(2) + "- O agente **nunca** narra. <!-- NAO-NORMATIVA: narrativa -->\n",
                     encoding="utf-8")
    (repo / "AGENTE.md").write_text(_orfas(1, "ag"), encoding="utf-8")
    (repo / "README.md").write_text(_orfas(7, "rd"), encoding="utf-8")
    sub = repo / ".claude" / "commands" / "sub"
    sub.mkdir()
    (sub / "fundo.md").write_text(_orfas(4, "sb"), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    assert cn.orfas_na_revisao("HEAD", root=r, gates=set()) == 3

    def staged():
        _git(repo, "add", "-A")
        return cn.catraca_contra_head("--staged", root=r, gates=set())

    # N+1 no indice -> mensagem de BLOCK, que aponta a clausula nova
    skill.write_text(_orfas(3), encoding="utf-8")
    res = staged()
    assert (res["head"], res["atual"], res["severidade"]) == (3, 4, "BLOCK")
    assert res["mensagem"] and "1 clausula(s) nova(s)" in res["mensagem"]
    assert ".claude/commands/sintetico.md:3" in res["mensagem"]
    assert cn.orfas_na_revisao(":", root=r, gates=set()) == 4

    # N e N-1 -> None (descer e livre; o proximo HEAD ja e a base menor)
    skill.write_text(_orfas(2), encoding="utf-8")
    assert staged()["mensagem"] is None
    skill.write_text(_orfas(1), encoding="utf-8")
    assert staged()["mensagem"] is None

    # o INDICE manda, nao a arvore: orfa nao-staged (de outro agente) nao bloqueia commit alheio
    skill.write_text(_orfas(9), encoding="utf-8")
    assert cn.catraca_contra_head("--staged", root=r, gates=set())["mensagem"] is None

    # contagem TOTAL, nao por arquivo: portador renomeado com as mesmas orfas nao cria orfa nova
    skill.write_text(_orfas(2), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "mv", ".claude/commands/sintetico.md", "core/contracts/sintetico-contract.md")
    res = cn.catraca_contra_head("--staged", root=r, gates=set())
    assert (res["head"], res["atual"], res["mensagem"]) == (3, 3, None)


def test_severidade_catraca_por_modo(tmp_path, git_isolado):
    """DoD 3 da part-3: o delta nasce BLOCK no --staged (pre-commit) e segue WARN no
    --changed/--all. Base zero por construcao -- toda orfa a mais que o HEAD e nova --, a mesma
    razao que faz `gate_inexistente` nascer BLOCK (AGENTE.md secao 6: vira BLOCK quando a base
    zera)."""
    assert cn.severidade_catraca("--staged") == "BLOCK"
    assert cn.severidade_catraca("--changed") == "WARN"
    assert cn.severidade_catraca("--all") == "WARN"

    # --changed/--all comparam a ARVORE com o HEAD e so avisam
    repo = _repo_git(tmp_path)
    r = str(repo)
    skill = repo / ".claude" / "commands" / "sintetico.md"
    skill.write_text(_orfas(2), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    skill.write_text(_orfas(3), encoding="utf-8")                 # so na arvore, nada staged
    for modo in ("--changed", "--all"):
        res = cn.catraca_contra_head(modo, root=r, gates=set())
        assert (res["head"], res["atual"]) == (2, 3)
        assert (res["severidade"], res["recorte"]) == ("WARN", "arvore")
        assert res["mensagem"] and "1 clausula(s) nova(s)" in res["mensagem"]
    assert cn.catraca_contra_head("--staged", root=r, gates=set())["mensagem"] is None


def test_catraca_com_git_ilegivel_avisa_e_nao_derruba(tmp_path, git_isolado):
    """Falha do git (aqui: raiz inexistente) = aviso explicito e sem BLOCK, nunca excecao."""
    res = cn.catraca_contra_head("--staged", root=str(tmp_path / "nao-existe"), gates=set())
    assert res["mensagem"] is None and res["aviso"] and "git" in res["aviso"]


# --- o BLOCK do check 29 barra o commit (Fase 0 Lote 0 part-3h, M-122) ----------------
# Desde 9ea675a (s187) o ramo `if graves_clau:` imprimia [BLOCK] e FAILED, mas nao zerava
# `all_passed`: o `main()` saia 0 e o commit passava com "Todos os checks passaram!". O teste
# roda o `main()` real IN-PROCESS (nada de commit em subprocesso: o hook roda a suite, que
# rodaria o hook -- licao da part-1). Tudo que nao e o check 29 fica neutro, para que o exit
# code dependa so dele: sem arquivo staged, a suite nao roda; os sensores caros ou que leem o
# banco (consistencia, D5, F38, F89) devolvem vazio; a catraca devolve "sem delta".

def _achado(tipo, severidade):
    return {"tipo": tipo, "severidade": severidade, "portador": "AGENTE.md", "linha": 1,
            "texto": "- O agente **nunca** pula o passo sintetico."}


def _main_do_check29(monkeypatch, capsys, achados):
    import auto_check
    import cli_signature_check
    import consistencia_check
    resumo = {"orfas": 1, "normativas": 1, "cobertura_pct": 0.0, "nao_normativas": 0}
    monkeypatch.setattr(cn, "registro_de_gates", lambda: set())
    monkeypatch.setattr(cn, "run_checks", lambda hoje=None, gates=None: (list(achados), resumo))
    monkeypatch.setattr(cn, "catraca_contra_head", lambda modo, root=None, gates=None: {
        "severidade": "BLOCK", "mensagem": None, "aviso": None, "head": 1, "atual": 1,
        "recorte": "indice"})
    monkeypatch.setattr(consistencia_check, "run_checks", lambda *a, **k: [])
    monkeypatch.setattr(cli_signature_check, "run_checks", lambda *a, **k: [])
    monkeypatch.setattr(sys, "argv", ["auto_check.py", "--staged"])
    monkeypatch.setattr(auto_check, "get_staged_files", lambda: [])
    monkeypatch.setattr(auto_check, "_staged_deletados", lambda: [])
    monkeypatch.setattr(auto_check, "run_command", lambda *a, **k: (True, ""))
    monkeypatch.setattr(auto_check, "_ledger_record", lambda *a, **k: None)
    monkeypatch.setattr(auto_check, "card_watermark_mudou", lambda *a, **k: (False, None))
    monkeypatch.setattr(auto_check, "card_watermark_selar", lambda *a, **k: None)
    monkeypatch.setattr(auto_check, "check_erros_orfaos", lambda *a, **k: [])
    monkeypatch.setattr(auto_check, "check_areas_fora_vocabulario", lambda *a, **k: [])
    capsys.readouterr()
    codigo = auto_check.main()
    return codigo, capsys.readouterr().out


@pytest.mark.parametrize("tipo", ["gate_inexistente", "nv_sem_data"])
def test_block_do_check29_barra_o_commit(monkeypatch, capsys, tipo):
    """DoD 2 da part-3h: anotacao com gate inexistente (ou marca sem data) e BLOCK desde o
    nascimento -- e BLOCK que nao muda o exit code e so um aviso com outro nome."""
    codigo, out = _main_do_check29(monkeypatch, capsys, [_achado(tipo, "BLOCK")])
    assert f"[BLOCK] CLAUSULA_{tipo.upper()}" in out
    assert codigo == 1, f"[BLOCK] {tipo} impresso e exit {codigo}: o commit passaria"
    assert "Todos os checks passaram" not in out


def test_check29_sem_achado_grave_sai_0(monkeypatch, capsys):
    """O outro lado do DoD 2: orfa e WARN (o passivo nasce em 271) e nao barra o commit."""
    for achados in ([], [_achado("orfa", "WARN")]):
        codigo, out = _main_do_check29(monkeypatch, capsys, achados)
        assert codigo == 0, out[-600:]
        assert "[BLOCK]" not in out


# --- git hermetico na suite (Fase 0 Lote 0 part-3h, M-123) -----------------------------
# A suite roda dentro do pre-commit, e o git exporta para o hook o `GIT_INDEX_FILE` do commit
# em curso (absoluto em `commit -a`/`commit <caminhos>`). Sem hook aqui (recursao, e o
# classificador negou a sonda na part-3): o ambiente do "pai" vai EXPLICITO no subprocesso.

_GIT_DO_HOOK = ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_PREFIX",
                "GIT_OBJECT_DIRECTORY")


def _md5(caminho):
    with open(caminho, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _env_sem_git():
    return {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}


def _sentinela_e_repo_a(tmp_path):
    """Indice VALIDO como sentinela -- o `.git/index` de um 2o repo sintetico depois de um
    `add`, copiado para fora dele (um arquivo qualquer daria "index corrupt" e um falso "nao
    reproduz") -- e o repo A, com o arquivo `x` ainda por adicionar."""
    env = _env_sem_git()
    a, b = tmp_path / "repo_a", tmp_path / "repo_b"
    for repo in (a, b):
        subprocess.run(["git", "init", "-q", str(repo)], check=True, env=env)
    (b / "b.txt").write_text("b\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(b), "add", "b.txt"], check=True, env=env)
    sentinela = tmp_path / "sentinela.index"
    shutil.copyfile(b / ".git" / "index", sentinela)
    (a / "x").write_text("x\n", encoding="utf-8")
    return a, sentinela


def test_git_index_file_herdado_desvia_o_add_para_o_indice_alheio(tmp_path):
    """DoD 4(i), a REPRODUCAO, que e tambem o controle positivo do (ii): sem ela, um
    sentinela que nada muda daria um (ii) verde por vacuidade. `git -C A add x` com
    `GIT_INDEX_FILE` herdado escreve no indice apontado, e o de A nem nasce."""
    a, sentinela = _sentinela_e_repo_a(tmp_path)
    antes = _md5(sentinela)
    pai = {**_env_sem_git(), "GIT_INDEX_FILE": str(sentinela)}
    subprocess.run(["git", "-C", str(a), "add", "x"], check=True, env=pai, capture_output=True)
    assert _md5(sentinela) != antes, "o add herdado nao tocou o sentinela: nao reproduz"
    listado = subprocess.run(["git", "-C", str(a), "ls-files"], check=True, env=pai,
                             capture_output=True, text=True).stdout.split()
    assert sorted(listado) == ["b.txt", "x"], "o add de A foi parar no indice de B"
    assert not (a / ".git" / "index").exists()


def test_fixture_de_sessao_tira_o_git_do_pai(tmp_path, monkeypatch, request):
    """DoD 4(ii): a fixture `autouse` de sessao do conftest raiz limpa o ambiente `GIT_*` do
    hook, e o `git -C A add x` fica no indice de A, sem tocar o sentinela. O "pai" e simulado
    pondo a variavel no `os.environ` e chamando a MESMA funcao de limpeza que a fixture chama;
    no teardown, a restauracao devolve o que tirou."""
    import conftest
    assert "_git_hermetico" in request.fixturenames, "a fixture de sessao tem de ser autouse"
    assert not [k for k in _GIT_DO_HOOK if k in os.environ], "fixture ativa: nada do hook aqui"

    a, sentinela = _sentinela_e_repo_a(tmp_path)
    antes = _md5(sentinela)
    monkeypatch.setenv("GIT_INDEX_FILE", str(sentinela))        # o pai: o commit em curso
    removidas = conftest.limpar_git_env()
    assert removidas == {"GIT_INDEX_FILE": str(sentinela)} and "GIT_INDEX_FILE" not in os.environ
    subprocess.run(["git", "-C", str(a), "add", "x"], check=True, capture_output=True)
    assert _md5(sentinela) == antes, "o sentinela mudou: o add herdou o indice do pai"
    assert (a / ".git" / "index").exists(), "o add tem de cair no indice do proprio repo A"
    conftest.restaurar_git_env(removidas)
    assert os.environ["GIT_INDEX_FILE"] == str(sentinela)

    # as 5 chaves, num ambiente que nao e o do processo
    env = {**_env_sem_git(), **{k: str(tmp_path / k) for k in _GIT_DO_HOOK}, "PATH_X": "fica"}
    removidas = conftest.limpar_git_env(env)
    assert sorted(removidas) == sorted(_GIT_DO_HOOK) and not set(_GIT_DO_HOOK) & set(env)
    assert env["PATH_X"] == "fica", "so as chaves do hook saem"
    conftest.restaurar_git_env(removidas, env)
    assert all(env[k] == str(tmp_path / k) for k in _GIT_DO_HOOK)
