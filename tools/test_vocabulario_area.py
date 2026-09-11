"""test_vocabulario_area.py -- vocabulario de area unico + fail-loud nos writers (F89, s176).

O achado: `GO` e `Clinica Medica` foram dissolvidas pela RODADA 1 do `normalize_taxonomia`
(s097) e VOLTARAM com ids novos, porque nenhum dos 3 writers de `taxonomia_cronograma`
consultava lista nenhuma -- e as duas copias da lista (`registrar_sessao_bulk` x
`performance`) ja divergiam entre si.

Fixtures deterministicas; db temporario; nada toca o ipub.db real. As areas fantasma
usadas sao as MEDIDAS no banco (`GO`, `Clinica Medica`), nao inventadas.
"""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.utils.areas as areas                                    # noqa: E402
from tools.utils.state_utils import check_areas_fora_vocabulario   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- DoD 1 e 6: uma fonte, e nenhuma copia sobreviveu --------------------------------

def test_nenhuma_copia_da_lista_sobrevive_no_repo():
    """A lista literal so pode existir no leitor unico. Copia nova FALHA nomeando o arquivo."""
    copias = []
    for sub in ("tools", "app"):
        base = os.path.join(ROOT, sub)
        for dirpath, _, arquivos in os.walk(base):
            if "__pycache__" in dirpath:
                continue
            for nome in arquivos:
                if not nome.endswith(".py") or nome.startswith("test_"):
                    continue
                caminho = os.path.join(dirpath, nome)
                with open(caminho, encoding="utf-8-sig", errors="replace") as fh:
                    texto = fh.read()
                if "AREAS_VALIDAS = [" in texto or "AREAS_CLINICAS = [" in texto:
                    copias.append(os.path.relpath(caminho, ROOT))
    assert copias == [], f"copia literal da lista fora da fonte unica: {copias}"


def test_reexport_do_registrar_bulk_continua_importavel_e_identico():
    """`importar_sessoes` importa `AREAS_VALIDAS` dali -- e re-export, nunca copia."""
    import registrar_sessao_bulk as rsb
    assert list(rsb.AREAS_VALIDAS) == list(areas.AREAS_VALIDAS)
    assert len(rsb.AREAS_VALIDAS) == 21, "a LISTA e do operador; o teste so trava o tamanho atual"


def test_performance_usa_a_mesma_fonte():
    import performance as perf
    assert list(perf.AREAS_VALIDAS) == list(areas.AREAS_VALIDAS)
    assert list(perf.AREAS_CLINICAS) == list(areas.AREAS_CLINICAS)


# --- DoD 2: o leitor NAO e tolerante ------------------------------------------------

def _json_temp(conteudo):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(conteudo)
    return path


def test_vocabulario_ausente_levanta_em_vez_de_devolver_vazio():
    try:
        areas._carregar(os.path.join(tempfile.gettempdir(), "nao_existe_areas_f89.json"))
        assert False, "arquivo ausente deveria levantar, nunca devolver lista vazia"
    except areas.VocabularioIndisponivel as e:
        assert "ausente" in str(e)


def test_vocabulario_ilegivel_e_vazio_levantam():
    """Licao do F91: retorno degradado que o chamador confunde com resposta valida.
    Sem vocabulario, reprovar tudo e aprovar tudo sao ambos falsos."""
    for conteudo, esperado in (("{nao e json", "ilegivel"),
                               ('{"clinicas": []}', "VAZIO")):
        path = _json_temp(conteudo)
        try:
            areas._carregar(path)
            assert False, f"deveria levantar para {conteudo!r}"
        except areas.VocabularioIndisponivel as e:
            assert esperado in str(e)
        finally:
            os.remove(path)


# --- DoD 3: duas listas nomeadas, diferenca por decisao ------------------------------

def test_simulado_e_valido_para_escrita_e_fora_das_clinicas():
    assert "Simulado" in areas.AREAS_VALIDAS, "simulado e area gravavel (volume agregado)"
    assert "Simulado" not in areas.AREAS_CLINICAS, \
        "simulado nao e especialidade -- nao pode virar 'gap' do /performance"
    assert len(areas.AREAS_VALIDAS) == len(areas.AREAS_CLINICAS) + len(areas.AREAS_AGREGADAS)


def test_gaps_do_performance_nunca_listam_simulado():
    """Preserva o comportamento da copia antiga -- agora por decisao declarada."""
    import performance as perf
    with open(os.path.join(ROOT, "tools", "performance.py"), encoding="utf-8") as fh:
        fonte = fh.read()
    assert "gaps = [a for a in AREAS_CLINICAS" in fonte, \
        "a lista de gaps tem que percorrer AREAS_CLINICAS, nao AREAS_VALIDAS"
    assert "Simulado" not in perf.AREAS_CLINICAS


# --- DoD 4: fail-loud nos 3 writers de taxonomia -------------------------------------

def _db_taxonomia(linhas=()):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE taxonomia_cronograma (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "area TEXT, tema TEXT, questoes_realizadas INTEGER DEFAULT 0, "
                "questoes_acertadas INTEGER DEFAULT 0, percentual_acertos REAL DEFAULT 0, "
                "ultima_revisao TEXT)")
    con.execute("CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "sessao_num INTEGER, area TEXT, questoes_feitas INTEGER, "
                "questoes_acertadas INTEGER, data_sessao DATE, observacoes TEXT)")
    for area, tema in linhas:
        con.execute("INSERT INTO taxonomia_cronograma (area, tema) VALUES (?,?)", (area, tema))
    con.commit()
    con.close()
    return path


def test_writer_1_registrar_sessao_bulk_recusa_area_fantasma():
    import registrar_sessao_bulk as rsb
    try:
        rsb.registrar(sessao_num=999, area="GO", feitas=10, acertos=5)
        assert False, "registrar() deveria recusar area fora do vocabulario"
    except areas.AreaInvalida as e:
        assert "registrar_sessao_bulk" in str(e) and "GO" in str(e)


def test_writer_2_insert_card_base_recusa_area_fantasma():
    import insert_card_base as icb
    tmp = _db_taxonomia()
    con = sqlite3.connect(tmp)
    try:
        icb.get_or_create_tema(con.cursor(), "Clinica Medica", "Sepse")
        assert False, "get_or_create_tema deveria recusar area fora do vocabulario"
    except areas.AreaInvalida as e:
        assert "insert_card_base" in str(e)
    finally:
        con.close()
        os.remove(tmp)


def test_writer_3_insert_questao_recusa_area_fantasma():
    """Levanta ANTES de qualquer escrita E antes do contrato de cunhagem: `area` e a
    precondicao mais barata, entao o chamador ve o primeiro problema real, nao o segundo."""
    import insert_questao as iq
    tmp = _db_taxonomia()
    con = sqlite3.connect(tmp)
    try:
        iq.insert_questao(area="GO", tema="Contracepcao", enunciado="Caso.",
                          correta="A", chamada="B", erro="Conceitual",
                          elo="elo", armadilha="distrator", conn=con)
        assert False, "insert_questao deveria recusar area fora do vocabulario"
    except areas.AreaInvalida as e:
        assert "insert_questao" in str(e)
        assert con.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0] == 0,             "recusou e ainda assim criou a linha"
    finally:
        con.close()
        os.remove(tmp)


def test_os_tres_writers_chamam_o_gate():
    """Varredura: writer novo que esqueca a chamada aparece aqui (irmao do F49)."""
    for arquivo in ("tools/registrar_sessao_bulk.py", "tools/insert_questao.py",
                    "tools/insert_card_base.py"):
        with open(os.path.join(ROOT, arquivo), encoding="utf-8") as fh:
            texto = fh.read()
        assert "validar_area(" in texto, f"{arquivo} escreve taxonomia sem chamar o gate"


def test_gate_recusa_tambem_acumulo_em_linha_fantasma_existente():
    """O fantasma para de CRESCER -- nao basta barrar linha nova."""
    import registrar_sessao_bulk as rsb
    tmp = _db_taxonomia(linhas=[("GO", "[bulk] GO")])
    orig = rsb.DB_PATH
    rsb.DB_PATH = tmp
    try:
        rsb.registrar(sessao_num=1, area="GO", feitas=10, acertos=8, acumular=True)
        assert False, "acumulo em linha fantasma existente tambem tem que recusar"
    except areas.AreaInvalida:
        con = sqlite3.connect(tmp)
        n = con.execute("SELECT questoes_realizadas FROM taxonomia_cronograma "
                        "WHERE area='GO'").fetchone()[0]
        con.close()
        assert n == 0, "recusou e ainda assim escreveu"
    finally:
        rsb.DB_PATH = orig
        os.remove(tmp)


def test_mensagem_nomeia_a_ambiguidade_em_vez_de_chutar_uma_area():
    """s110: 3 linhas de `Clinica Medica` eram Infecto, Hemato e Oftalmo. Chutar UMA
    area seria repetir o erro -- entao a dica e a AMBIGUIDADE."""
    for fantasma, marca in (("GO", "Ginecologia OU Obstetricia"),
                            ("Clinica Medica", "especialidade real")):
        try:
            areas.validar_area(fantasma)
            assert False, f"{fantasma} deveria recusar"
        except areas.AreaInvalida as e:
            assert marca in str(e), f"mensagem de {fantasma} sem a dica de ambiguidade: {e}"


def test_typo_ganha_sugestao_e_area_valida_passa():
    assert areas.validar_area("  Cirurgia  ") == "Cirurgia", "espaco nas bordas nao invalida"
    try:
        areas.validar_area("Cardiolgia")
        assert False, "typo deveria recusar"
    except areas.AreaInvalida as e:
        assert "Cardiologia" in str(e)
    assert areas.area_valida("Hemato") and not areas.area_valida("GO")


# --- DoD 5: o passivo vira WARN, nomeado -------------------------------------------

def test_check_encontra_o_passivo_nas_duas_tabelas():
    tmp = _db_taxonomia(linhas=[("GO", "[bulk] GO"), ("GO", "Contracepcao"),
                                ("Cirurgia", "Apendicite")])
    con = sqlite3.connect(tmp)
    con.execute("INSERT INTO sessoes_bulk (sessao_num, area, questoes_feitas, "
                "questoes_acertadas, data_sessao) VALUES (1,'Clinica Medica',10,8,'2026-09-01')")
    con.commit()
    con.close()
    try:
        achados = check_areas_fora_vocabulario(db_path=tmp)
        assert achados is not None
        pares = {(t, a): n for t, a, n in achados}
        assert pares.get(("taxonomia_cronograma", "GO")) == 2
        assert pares.get(("sessoes_bulk", "Clinica Medica")) == 1
        assert not any(a == "Cirurgia" for _, a, _ in achados), "area valida nao e achado"
    finally:
        os.remove(tmp)


def test_check_devolve_none_quando_a_base_esta_limpa():
    tmp = _db_taxonomia(linhas=[("Cirurgia", "Apendicite"), ("Simulado", "[bulk] Simulado")])
    try:
        assert check_areas_fora_vocabulario(db_path=tmp) is None, \
            "base limpa nao pode gerar WARN (nem 'Simulado', que e area valida)"
    finally:
        os.remove(tmp)


def test_check_nasce_WARN_e_nao_rebaixa_o_veredito():
    """Politica warning-first (s106/107): limpar as linhas e do OPERADOR (RODADA 3)."""
    with open(os.path.join(ROOT, "tools", "auto_check.py"), encoding="utf-8") as fh:
        fonte = fh.read()
    assert "results_summary.append((desc_f89, True," in fonte, \
        "o check F89 tem que entrar com success=True (WARN nao bloqueia)"
    assert "AREAS_FANTASMA" in fonte


if __name__ == "__main__":
    falhas = 0
    for nome, fn in sorted(list(globals().items())):
        if nome.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  OK   {nome}")
            except AssertionError as e:
                falhas += 1
                print(f"  FALHA {nome}: {e}")
    print(f"\n{'FALHOU' if falhas else 'PASSOU'} -- {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
