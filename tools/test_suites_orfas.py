"""Suite do invariante F43 -- suite que existe tem que estar em algum registro.

"Quais testes rodam" no MedHub nao tem UM registro: tem TRES, todos mantidos a
mao e nenhum ciente do outro -- `pytest.ini` (`python_files`), as suites citadas
por nome em `tools/auto_check.py`, e os script-style rodados por subprocess em
`tools/test_pytest_bridge.py`. Uma suite fora dos tres existe, passa no code
review e **nunca executa** -- o mesmo modo de falha do D4/alcancabilidade.

Nao ha orfa hoje (37/37). Este check existe para que o autor da PROXIMA suite
descubra que esqueceu de inscrever antes do commit, e nao tres sessoes depois.

Auto-referencia deliberada: esta suite tambem precisou ser inscrita a mao no
`pytest.ini`. Se um dia ela sumir da allowlist, ela para de rodar -- e o unico
detector disso e ela mesma, rodando pelo `auto_check`. Redundancia de proposito.

Fixtures sinteticas (repo de mentira em tmp_path) + 1 teste de regressao viva.
Executavel standalone (python tools/test_suites_orfas.py) e coletavel pelo pytest.
"""
import pytest

from tools.utils.state_utils import check_suites_orfas


def _repo(tmp_path, suites=(), pytest_ini="", auto_check="", bridge=None):
    """Repo sintetico. `bridge=None` NAO cria o arquivo do bridge.

    Detalhe que custou uma rodada vermelha: `test_pytest_bridge.py` e registro
    E suite ao mesmo tempo (casa `test_*.py`). Criado vazio, ele vira orfao de
    si proprio e envenena todo teste. No repo real ele esta inscrito no
    `pytest.ini`; aqui o fixture faz o equivalente, mencionando o proprio nome.
    """
    (tmp_path / "tools").mkdir(exist_ok=True)
    for nome in suites:
        (tmp_path / "tools" / nome).write_text("# fake", encoding="utf-8")
    (tmp_path / "pytest.ini").write_text(pytest_ini, encoding="utf-8")
    (tmp_path / "tools" / "auto_check.py").write_text(auto_check, encoding="utf-8")
    if bridge is not None:
        (tmp_path / "tools" / "test_pytest_bridge.py").write_text(
            bridge, encoding="utf-8")
        # O bridge e registro E suite ao mesmo tempo. No repo real ele esta
        # inscrito no `pytest.ini`; o fixture faz o equivalente. Ate a s171 ele
        # se cobria com um COMENTARIO com o proprio nome -- o que so funcionava
        # porque o predicado era substring. Esse era o defeito.
        linha = "python_files = test_pytest_bridge.py"
        atual = (tmp_path / "pytest.ini").read_text(encoding="utf-8")
        if "python_files" in atual:
            atual = atual.replace("python_files =", "python_files = test_pytest_bridge.py")
        else:
            atual = (atual + chr(10) + linha).strip()
        (tmp_path / "pytest.ini").write_text(atual, encoding="utf-8")
    return str(tmp_path)


# --------------------------------------------------------------------------
# Deteccao
# --------------------------------------------------------------------------

def test_suite_fora_dos_tres_registros_e_orfa(tmp_path):
    r = _repo(tmp_path, suites=["test_solta.py"])
    assert check_suites_orfas(r) == ["test_solta.py"]


def test_inscrita_no_pytest_ini_passa(tmp_path):
    r = _repo(tmp_path, suites=["test_ok.py"],
              pytest_ini="python_files = test_ok.py")
    assert check_suites_orfas(r) is None


def test_citada_no_auto_check_passa(tmp_path):
    """Registro 2: suites que o harness invoca por nome, sem passar pelo pytest."""
    r = _repo(tmp_path, suites=["test_ok.py"],
              auto_check="run_command(['python', 'tools/test_ok.py'], 'suite')")
    assert check_suites_orfas(r) is None


def test_citada_no_bridge_passa(tmp_path):
    """Registro 3: script-style rodados por subprocess (asserts em print)."""
    r = _repo(tmp_path, suites=["test_ok.py"],
              bridge="_roda('tools/test_ok.py')")
    assert check_suites_orfas(r) is None


def test_varias_orfas_saem_ordenadas(tmp_path):
    r = _repo(tmp_path, suites=["test_b.py", "test_a.py"])
    assert check_suites_orfas(r) == ["test_a.py", "test_b.py"]


def test_mistura_orfa_e_coberta(tmp_path):
    r = _repo(tmp_path, suites=["test_ok.py", "test_solta.py"],
              pytest_ini="python_files = test_ok.py")
    assert check_suites_orfas(r) == ["test_solta.py"]


# --------------------------------------------------------------------------
# Mencionada != inscrita (F86, s171) -- o predicado le ESTRUTURA, nao substring
# --------------------------------------------------------------------------

def test_mencao_em_string_de_warn_nao_conta_como_inscricao(tmp_path):
    """🔴 O CASO REAL que motivou o F86.

    Na s171 a suite `test_contrato_revogado.py` nasceu fora do `python_files` --
    12 testes escritos, ZERO executados -- e o `SUITES_ORFAS` passou VERDE
    porque o nome aparecia numa mensagem de WARN dentro do proprio
    `auto_check.py`, escrita no mesmo commit pelo autor do gate novo.
    """
    r = _repo(tmp_path, suites=["test_ok.py"],
              auto_check='print(f"detalhe: pytest tools/test_ok.py -q")')
    assert check_suites_orfas(r) == ["test_ok.py"]


def test_mencao_em_comentario_nao_conta_como_inscricao(tmp_path):
    r = _repo(tmp_path, suites=["test_ok.py"],
              auto_check="# a suite real e tools/test_ok.py, ver adiante")
    assert check_suites_orfas(r) == ["test_ok.py"]


def test_mencao_em_lista_de_gatilho_nao_conta(tmp_path):
    """Lista de arquivos que DISPARAM um check != comando que EXECUTA a suite.

    O `auto_check` real tem as duas coisas, e so a segunda e inscricao.
    """
    r = _repo(tmp_path, suites=["test_ok.py"],
              auto_check='tocados = ["tools/db.py", "tools/test_ok.py"]')
    assert check_suites_orfas(r) == ["test_ok.py"]


def test_python_files_casado_por_fnmatch(tmp_path):
    """`python_files` sao PADROES, nao nomes literais -- e como o pytest le.

    O predicado por substring dava falso-positivo aqui: `test_ok.py` nao e
    substring de `test_*.py`, entao uma suite legitimamente coletada era
    acusada de orfa.
    """
    r = _repo(tmp_path, suites=["test_ok.py"], pytest_ini="python_files = test_*.py")
    assert check_suites_orfas(r) is None


def test_comando_montado_em_variavel_conta_como_inscricao(tmp_path):
    """O `auto_check` real monta `cmd_tel = [sys.executable, "tools/test_X.py"]`
    e so depois chama `run_command(cmd_tel, ...)`. Ler so os argumentos da
    chamada perderia esses casos."""
    r = _repo(tmp_path, suites=["test_ok.py"],
              auto_check=('cmd = [sys.executable, "tools/test_ok.py"]' + chr(10)
                          + 'run_command(cmd, "d")'))
    assert check_suites_orfas(r) is None


def test_registro_ilegivel_nao_levanta_e_nao_cobre(tmp_path):
    """Sensor tolerante: `auto_check.py` com sintaxe quebrada nao derruba o
    check -- so deixa de cobrir."""
    r = _repo(tmp_path, suites=["test_ok.py"],
              pytest_ini="python_files = test_ok.py",
              auto_check="def (((( isto nao parseia")
    assert check_suites_orfas(r) is None


# --------------------------------------------------------------------------
# Modo defensivo (regra dos irmaos F1/POSICAO/B1: nunca falso-positivo barulhento)
# --------------------------------------------------------------------------

def test_sem_tools_e_silencioso(tmp_path):
    assert check_suites_orfas(str(tmp_path)) is None


def test_sem_suite_nenhuma_e_silencioso(tmp_path):
    assert check_suites_orfas(_repo(tmp_path)) is None


def test_registros_ausentes_nao_levantam(tmp_path):
    """Sem nenhum registro legivel o check se cala em vez de acusar tudo."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "test_x.py").write_text("# fake", encoding="utf-8")
    assert check_suites_orfas(str(tmp_path)) is None


# --------------------------------------------------------------------------
# Regressao viva
# --------------------------------------------------------------------------

def test_repo_real_nao_tem_suite_orfa():
    """Se esta cair, alguem criou uma suite e esqueceu de inscrever."""
    orfas = check_suites_orfas()
    assert orfas is None, f"suites que existem e nao rodam: {orfas}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
