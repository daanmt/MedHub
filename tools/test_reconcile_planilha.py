"""test_reconcile_planilha.py -- W1 do reconcile REPORTA planilha x db (B3/F35, s176).

Fixtures deterministicas sobre `day_plan.reconcile_planilha` / `render_planilha` e sobre
o ingestor puro `importar_sessoes.montar_snapshot`. Db temporario; nada toca o ipub.db real.

Os numeros das fixtures dos dois estados acionaveis vem da UNICA reconciliacao real
documentada (s110, `tools/_archive/migrations/fix_data_delta_110.py`): total 4660 na planilha
x 4584 no db (delta 76), e o mislabel de area que NAO mudou o total. Fixture que reproduz o
defeito historico, nao numero inventado.
"""
import json
import os
import sqlite3
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.utils.db as db          # noqa: E402
import day_plan as dp              # noqa: E402
import importar_sessoes as imp     # noqa: E402

HOJE = date(2026, 9, 10)


def _db_temp(linhas=()):
    """Db minimo com sessoes_bulk; `linhas` = (area, feitas, data_sessao)."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "sessao_num INTEGER, area TEXT, questoes_feitas INTEGER, "
                "questoes_acertadas INTEGER, data_sessao DATE, observacoes TEXT)")
    for i, (area, feitas, data_sessao) in enumerate(linhas, 1):
        con.execute("INSERT INTO sessoes_bulk (sessao_num, area, questoes_feitas, "
                    "questoes_acertadas, data_sessao) VALUES (?,?,?,?,?)",
                    (i, area, feitas, feitas, data_sessao))
    con.commit()
    con.close()
    return path


def _com_db(linhas, snap=None, fn=None):
    tmp = _db_temp(linhas)
    orig = db.DB_PATH
    db.DB_PATH = tmp
    try:
        if snap is not None:
            db.set_preparacao(imp.CHAVE_SNAPSHOT, json.dumps(snap), fonte="teste")
        return fn()
    finally:
        db.DB_PATH = orig
        os.remove(tmp)


def _snap(total, por_area=None, ultimo="2026-09-09", lido="2026-09-10T08:00:00",
          viva=True, motivo=None, declarado=None):
    return {"total": total, "por_area": por_area, "ultimo_lancamento": ultimo,
            "lido_em": lido, "fonte_viva": viva, "motivo_abandono": motivo,
            "declarado_em": declarado}


# --- DoD 1: a linha SEMPRE sai, inclusive sem dado -------------------------------------

def test_sem_snapshot_e_nao_medido_e_a_linha_sai():
    r = _com_db([("Cirurgia", 7126, "2026-09-09")], None,
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "nao_medido", "sem snapshot -> NAO MEDIDO (nunca delta zero assumido)"
    assert r["delta"] is None, "delta nao pode ser fabricado sem planilha"
    assert r["db_total"] == 7126, "o lado que existe continua sendo medido"
    linha = dp.render_planilha(r)
    assert "NAO MEDIDO" in linha and "--snapshot" in linha, \
        "a ausencia de medicao e reportada COM o comando que a resolve"


def test_render_nunca_devolve_vazio_em_nenhum_estado():
    """DoD 1 no nivel do render: nao existe estado que produza silencio."""
    estados = [
        _snap(7126, {"Cirurgia": 7126}),                    # alinhado
        _snap(7126),                                        # sem_detalhe_area
        _snap(4660, ultimo="2026-09-09"),                   # import_pendente
        _snap(6288, ultimo="2026-07-20"),                   # planilha_atrasada
        _snap(6288, {"Cirurgia": 6288}, viva=False, motivo="parou", declarado="2026-09-10"),
    ]
    for snap in estados:
        r = _com_db([("Cirurgia", 7126, "2026-09-09")], snap,
                    lambda: dp.reconcile_planilha(hoje=HOJE))
        linha = dp.render_planilha(r)
        assert linha.strip().startswith("- 📋"), f"estado {r['estado']} sem linha"
        assert "W1/F35" in linha, f"estado {r['estado']} sem a ancora do achado"


# --- DoD 3: oito estados nomeados, com as fixtures reais da s110 ------------------------

def test_alinhado_exige_detalhe_por_area():
    r = _com_db([("Cirurgia", 4584, "2026-09-09")], _snap(4584, {"Cirurgia": 4584}),
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "alinhado" and r["delta"] == 0
    assert r["acao"] is None, "alinhado nao pede acao"


def test_total_batendo_sem_abas_nao_e_alinhado():
    """s110: 3 de 4 achados eram mislabel de area e o relabeling NAO mudou o total.
    Sem detalhe por area, 'total bate' e uma nao-verificacao -- e o estado diz isso."""
    r = _com_db([("Cirurgia", 4584, "2026-09-09")], _snap(4584),
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "sem_detalhe_area", "total igual sem abas nao pode passar por alinhado"
    assert r["detalhe_por_area"] is False
    assert "NAO foi verificado" in dp.render_planilha(r)


def test_divergente_por_area_com_total_igual_e_a_assinatura_do_mislabel():
    """Fixture s110: 'Clinica Medica' no db x Infecto/Hemato/Oftalmo na planilha.
    Somas identicas (70 x 70); so a distribuicao denuncia."""
    linhas = [("Clinica Medica", 70, "2026-09-09")]
    snap = _snap(70, {"Infecto": 25, "Hemato": 25, "Oftalmo": 20})
    r = _com_db(linhas, snap, lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["delta"] == 0, "o total bate -- e esse o ponto"
    assert r["estado"] == "divergente_por_area"
    areas = {a["area"] for a in r["areas_divergentes"]}
    assert areas == {"Clinica Medica", "Infecto", "Hemato", "Oftalmo"}
    assert "Clinica Medica" in dp.render_planilha(r), "a area crua aparece no relatorio (F89)"


def test_import_pendente_reproduz_os_76q_da_s110():
    r = _com_db([("Cirurgia", 4584, "2026-09-09")], _snap(4660, ultimo="2026-09-09"),
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "import_pendente", "planilha a frente do db = volume nunca importado"
    assert r["delta"] == -76, "o delta da s110, com o sinal dizendo de que lado esta a sobra"


def test_planilha_atrasada_distingue_idade_de_drift():
    """db a frente E planilha parada ha 52d: delta explicado pela idade, nao por import perdido."""
    r = _com_db([("Cirurgia", 7126, "2026-09-09")], _snap(6288, ultimo="2026-07-20"),
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "planilha_atrasada"
    assert r["idade_planilha_dias"] == 52, "a idade da planilha e o dado do F35"
    assert r["delta"] == 838


def test_divergente_quando_a_idade_nao_explica():
    """db a frente com a planilha lancada HOJE: a idade nao cobre o delta."""
    r = _com_db([("Cirurgia", 7126, "2026-09-09")], _snap(6288, ultimo="2026-09-10"),
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "divergente", "planilha fresca e menor que o db = divergencia real"


def test_duas_idades_nao_colapsam():
    """'a planilha ainda e alimentada?' e 'minha copia dela e velha?' sao perguntas distintas."""
    r = _com_db([("Cirurgia", 7126, "2026-09-09")],
                _snap(6288, ultimo="2026-07-20", lido="2026-09-05T10:00:00"),
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["idade_planilha_dias"] == 52 and r["idade_leitura_dias"] == 5, \
        "as duas idades sao medidas separadamente"


# --- DoD 6: a resposta do operador muda o peso, nao o mecanismo -------------------------

def test_abandonada_suspende_a_cobranca_e_preserva_o_ultimo_delta():
    snap = _snap(6288, {"Cirurgia": 6288}, ultimo="2026-07-20", viva=False,
                 motivo="parei de lancar", declarado="2026-09-10")
    r = _com_db([("Cirurgia", 7126, "2026-09-09")], snap,
                lambda: dp.reconcile_planilha(hoje=HOJE))
    assert r["estado"] == "abandonada" and r["acao"] is None, "para de cobrar"
    assert r["delta"] == 838, "o ultimo delta medido continua gravado e exibido"
    linha = dp.render_planilha(r)
    assert "suspensa" in linha and "838" in linha, "reporta suspenso -- nao some da tela"


def test_declarar_abandono_nao_apaga_o_snapshot():
    def _corpo():
        db.set_preparacao(imp.CHAVE_SNAPSHOT, json.dumps(_snap(6288, {"Cirurgia": 6288})),
                          fonte="teste")
        novo = imp.declarar_abandono("planilha morreu", hoje=HOJE)
        assert novo["total"] == 6288 and novo["por_area"] == {"Cirurgia": 6288}, \
            "declarar abandono nao pode zerar a medicao anterior"
        assert novo["fonte_viva"] is False and novo["declarado_em"] == "2026-09-10"
        return True
    assert _com_db([("Cirurgia", 7126, "2026-09-09")], None, _corpo)


# --- DoD 4: reporta, nunca bloqueia ----------------------------------------------------

def test_leitor_quebrado_degrada_sem_derrubar_o_boot():
    orig_get = db.get_connection

    def explode():
        raise sqlite3.OperationalError("banco inacessivel (simulado)")

    db.get_connection = explode
    try:
        r = dp.reconcile_planilha(hoje=HOJE)
    finally:
        db.get_connection = orig_get
    assert r["estado"] == "nao_medido" and r["degradou"] is True, \
        "falha do leitor vira estado reportado, nunca excecao para fora"
    assert "degradou" in dp.render_planilha(r), "a linha declara que degradou"


def test_build_continua_saindo_com_a_secao_planilha():
    p = {"planilha": {"estado": "nao_medido", "db_total": 10, "degradou": False,
                      "acao": "cmd"}}
    assert dp.render_planilha(p["planilha"]), "render nao depende de db aberto"


# --- DoD 5: o ingestor recusa planilha internamente inconsistente ----------------------

def test_total_divergente_da_soma_das_abas_e_recusado_com_os_dois_numeros():
    """O bug de formula do Quadro Geral (s075, Obstetricia somava acertos) para na porta."""
    try:
        imp.montar_snapshot(total=100, por_area={"Pediatria": 60, "Cirurgia": 30},
                            ultimo_lancamento="2026-07-20", hoje=HOJE)
        assert False, "total x soma das abas divergente deveria recusar"
    except ValueError as e:
        assert "100" in str(e) and "90" in str(e), "a mensagem carrega os DOIS numeros"


def test_por_area_sem_total_deriva_o_total_da_soma():
    snap = imp.montar_snapshot(por_area={"Pediatria": 60, "Cirurgia": 30},
                               ultimo_lancamento="2026-07-20", hoje=HOJE)
    assert snap["total"] == 90 and snap["fonte_viva"] is True


def test_data_no_futuro_e_total_negativo_sao_recusados():
    for kwargs, esperado in (
        ({"total": 100, "ultimo_lancamento": "2026-12-31"}, "futuro"),
        ({"total": -1, "ultimo_lancamento": "2026-07-20"}, "negativo"),
        ({"total": 100, "ultimo_lancamento": None}, "obrigatorio"),
        ({"total": 100, "ultimo_lancamento": "20/07/2026"}, "AAAA-MM-DD"),
    ):
        try:
            imp.montar_snapshot(hoje=HOJE, **kwargs)
            assert False, f"deveria recusar: {kwargs}"
        except ValueError as e:
            assert esperado in str(e), f"mensagem sem '{esperado}': {e}"


def test_snapshot_roundtrip_grava_e_le():
    def _corpo():
        snap = imp.montar_snapshot(por_area={"Pediatria": 60}, ultimo_lancamento="2026-07-20",
                                   hoje=HOJE)
        imp.gravar_snapshot(snap)
        lido = imp.ler_snapshot()
        assert lido["total"] == 60 and lido["ultimo_lancamento"] == "2026-07-20"
        r = dp.reconcile_planilha(hoje=HOJE)
        assert r["planilha_total"] == 60, "o reconcile le o que o ingestor gravou"
        return True
    assert _com_db([("Pediatria", 100, "2026-09-09")], None, _corpo)


def test_ler_snapshot_nunca_levanta():
    def _corpo():
        db.set_preparacao(imp.CHAVE_SNAPSHOT, "{nao e json}", fonte="teste")
        assert imp.ler_snapshot() is None, "snapshot corrompido le como ausente, nao como erro"
        return True
    assert _com_db([], None, _corpo)


# --- DoD 7: paridade contrato <-> codigo -----------------------------------------------

def test_contrato_w1_nao_declara_mais_manual():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(raiz, "core/contracts/reconcile-contract.md"),
              encoding="utf-8") as fh:
        w1 = [ln for ln in fh if ln.strip().startswith("| **W1**")]
    assert w1, "linha W1 sumiu da matriz do reconcile-contract"
    assert "day_plan" in w1[0] and "--planilha" in w1[0], \
        "W1 precisa nomear o instrumento real (a coluna diz a VERDADE por linha, F56)"


def test_skill_carrega_a_assinatura_do_flag_novo():
    """AGENTE §7.2: assinatura canonica de CLI vive em UMA skill."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(raiz, ".claude/commands/importar-planilha.md"),
              encoding="utf-8") as fh:
        texto = fh.read()
    for flag in ("--snapshot", "--ultimo-lancamento", "--por-area", "--abandonada"):
        assert flag in texto, f"{flag} sem assinatura canonica na skill"


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
