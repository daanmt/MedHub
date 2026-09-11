"""test_contador_divida.py -- F64: o regime de divida tem UM contador (s176, item 1.2).

O defeito, medido na s162: havia **45 atrasados + 22 para hoje = 67 vencidos**. O
operador leu "67 > 60, logo regime de divida"; o codigo leu "45 < 60, teto base"; e o
agente **recomendou parar o estudo** com o numero do codigo. A politica declarada
("teto 60/dia, CAP 1,5x") nunca dissera QUAL contador dispara o regime -- `_teto_efetivo`
escolheu `atrasados` sem que a escolha estivesse escrita em portador nenhum.

Fixtures deterministicas sobre funcoes puras; db temporario onde precisa. A fixture
central e a propria s162 -- numero real, com a divergencia que ele produziu.
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

import day_plan as dp   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# s162: o caso que originou o achado.
S162 = {"atrasados": 45, "hoje": 22, "backlog_novos": 300}


def test_vencidos_e_atrasados_mais_hoje():
    assert dp.vencidos_de(S162) == 67
    assert dp.vencidos_de({}) == 0, "dict incompleto nao pode explodir o boot"
    assert dp.vencidos_de({"atrasados": None, "hoje": None}) == 0


def test_a_divergencia_da_s162_virou_UMA_leitura():
    """O ponto do achado: os dois numeros existiam e davam veredito oposto."""
    vencidos = dp.vencidos_de(S162)
    assert vencidos > dp.TETO_BASE, "67 > 60 -- a leitura do dono"
    assert S162["atrasados"] <= dp.TETO_BASE, "45 <= 60 -- a leitura antiga do codigo"
    assert dp._teto_efetivo(vencidos) == 90, "regime de divida dispara e o teto vai ao CAP"
    assert dp._teto_efetivo(S162["atrasados"]) == dp.TETO_BASE, \
        "o criterio antigo travaria o teto em 60 com a fila inteira vencida"


def test_divida_composta_so_de_HOJE_dispara_o_regime():
    """Efeito perverso do criterio antigo: `atrasados` = 0 e o regime nunca disparava."""
    fsrs = {"atrasados": 0, "hoje": 80}
    assert dp.vencidos_de(fsrs) == 80
    assert dp._teto_efetivo(dp.vencidos_de(fsrs)) == 90
    assert dp._teto_efetivo(fsrs["atrasados"]) == dp.TETO_BASE, "era isto que travava"


def test_teto_respeita_base_e_cap():
    assert dp._teto_efetivo(0) == dp.TETO_BASE
    assert dp._teto_efetivo(dp.TETO_BASE) == dp.TETO_BASE, "60 nao e regime; 61 e"
    assert dp._teto_efetivo(dp.TETO_BASE + 1) == dp.TETO_BASE + dp.TETO_BASE + 1 \
        if dp.TETO_BASE + dp.TETO_BASE + 1 <= dp.CAP_MULTIPLICADOR * dp.TETO_BASE \
        else dp._teto_efetivo(dp.TETO_BASE + 1) == int(dp.CAP_MULTIPLICADOR * dp.TETO_BASE)
    assert dp._teto_efetivo(10_000) == int(dp.CAP_MULTIPLICADOR * dp.TETO_BASE), \
        "o CAP e teto duro, nao sugestao"


# --- F64 (c): o teto sai com o SALDO do dia ------------------------------------------

def test_render_nomeia_o_gatilho_e_mostra_o_saldo():
    p = {"data": "2026-09-10", "provas": [], "dormant": {"empty": True},
         "volume": {"total": 1, "hoje": 0, "faltam": 1, "dias_ate_marco": 1,
                    "ritmo_alvo": 1.0, "marco": "X"},
         "fsrs": {"atrasados": 45, "hoje": 22, "backlog_novos": 10},
         "divida": {"atrasados": 45, "vencidos": 67, "regime_divida": True,
                    "teto_base": 60, "teto_efetivo": 90, "consumo_hoje": 12},
         "sugestao_passo": "x", "planilha": {"estado": "nao_medido", "db_total": 1,
                                             "degradou": False, "acao": "cmd"}}
    texto = dp.render(p)
    assert "67 vencidos" in texto, "o gatilho tem que aparecer NOMEADO"
    assert "atrasados + hoje" in texto, "e a definicao junto -- o achado foi ambiguidade"
    assert "12/90 usados hoje" in texto and "78 restantes" in texto, \
        "teto sem saldo obriga o leitor a derivar a conta a mao (foi como a s162 errou)"
    assert "REGIME DE DÍVIDA" in texto


def test_render_nao_quebra_sem_consumo_medido():
    """Degradacao graciosa: falha ao ler o revlog nao derruba o plano do dia."""
    p = {"data": "2026-09-10", "provas": [], "dormant": {"empty": True},
         "volume": {"total": 1, "hoje": 0, "faltam": 1, "dias_ate_marco": 1,
                    "ritmo_alvo": 1.0, "marco": "X"},
         "fsrs": {"atrasados": 0, "hoje": 0, "backlog_novos": 0},
         "divida": {"atrasados": 0, "vencidos": 0, "regime_divida": False,
                    "teto_base": 60, "teto_efetivo": 60, "consumo_hoje": None},
         "sugestao_passo": "x", "planilha": {"estado": "nao_medido", "db_total": 1,
                                             "degradou": False, "acao": "cmd"}}
    texto = dp.render(p)
    assert "Teto do dia" in texto and "usados hoje" not in texto


def test_consumo_hoje_conta_o_revlog_do_dia():
    fd, tmp = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    con = sqlite3.connect(tmp)
    con.execute("CREATE TABLE fsrs_revlog (id INTEGER PRIMARY KEY, review_time TIMESTAMP)")
    con.execute("CREATE TABLE sessoes_bulk (id INTEGER PRIMARY KEY, area TEXT, "
                "questoes_feitas INTEGER, data_sessao DATE)")
    con.executemany("INSERT INTO fsrs_revlog (review_time) VALUES (?)",
                    [("2026-09-10 08:00:00",), ("2026-09-10 22:30:00",),
                     ("2026-09-09 23:59:59",)])
    con.commit()
    try:
        assert dp.realizado_do_dia(con, "2026-09-10")["cards"] == 2, \
            "o saldo e por dia de calendario -- a revisao de ontem nao conta"
    finally:
        con.close()
        os.remove(tmp)


# --- portadores: uma definicao, escrita onde alguem le --------------------------------

def test_contrato_declara_vencidos_e_lapida_a_redacao_antiga():
    with open(os.path.join(ROOT, "core/contracts/fsrs-management-contract.md"),
              encoding="utf-8") as fh:
        texto = fh.read()
    assert "vencidos = atrasados + hoje" in texto, "o contador tem que estar ESCRITO"
    assert "⚰️" in texto and "atrasados > TETO_BASE" in texto, \
        "a redacao morta fica com lapide, nao apagada -- a s162 so se explica com ela a vista"


def test_termo_revogado_cadastrado_no_gate():
    """Passo (3) do ritual de revogacao (AGENTE.md secao 10, item 10)."""
    from tools.auto_check import _TERMOS_REVOGADOS, _PORTADORES_NORMA
    assert "atrasados > TETO_BASE" in _TERMOS_REVOGADOS, \
        "declarar e lapidar sem cadastrar deixa o gate cego para a proxima (F90)"
    assert "core/contracts/fsrs-management-contract.md" in _PORTADORES_NORMA, \
        "F95: o contrato FSRS estava fora da varredura e carregava um PREPARAR vivo"


def test_uma_implementacao_so():
    """`atrasados + hoje` calculado a mao noutro lugar recria a divergencia."""
    with open(os.path.join(ROOT, "tools", "day_plan.py"), encoding="utf-8") as fh:
        linhas = [ln for ln in fh
                  if 'atrasados"] + ' in ln and "hoje" in ln and "def " not in ln]
    assert linhas == [], f"soma manual de vencidos fora de vencidos_de(): {linhas}"


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
