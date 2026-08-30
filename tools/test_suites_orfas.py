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
            bridge + "  # test_pytest_bridge.py", encoding="utf-8")
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
