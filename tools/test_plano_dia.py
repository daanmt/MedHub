"""Suite do plano do dia: persistencia (telemetria-estudo-part-1) + o bloco de
cronograma derivado de `plano_tarefas` (plano-ssot-e-cards-v2 Parte 4).

Cobre: persistencia dos blocos com flags do run, idempotencia por dia
(delete+insert substitui, nunca acumula), leitura ordenada (ler_plano),
schema sem coluna de texto clinico e resiliencia (db indisponivel -> WARN,
plano segue). Parte 4: semana corrente = menor `semana_plano` com pendencia, as
proximas tarefas em ordem com fonte/tipo/q/url, a linha `Posicao:` do
`--handoff-block` e o SILENCIO com tabela vazia (regra dos irmaos F1/POSICAO/B1).
Fixtures 100%% sinteticas: labels/ids fake, zero conteudo real.

Executavel standalone (python tools/test_plano_dia.py) e coletavel pelo pytest.
"""
import sqlite3
import sys
from datetime import date

import pytest

import app.utils.db as db
from tools import day_plan
from tools.day_plan import ler_plano, persistir_plano

COLS_PERMITIDAS = {"id", "data", "ordem", "task_tipo", "alvo_tema",
                   "volume_planejado", "tempo_h", "energia",
                   "defaults_assumidos", "criado_em"}


def _plano_fake(data="2026-07-12", blocos=None, tempo_h=2.0, energia="baixa",
                defaults=False):
    if blocos is None:
        blocos = [
            {"tipo": "mini-drill", "qtd": 3, "alvo": "Tema A", "motivo": "m"},
            {"tipo": "questoes", "qtd": 40, "alvo": "Tema B", "motivo": "m"},
            {"tipo": "fsrs", "qtd": 30, "alvo": "fila do dia", "motivo": "m"},
        ]
    return {"data": data,
            "recomendacao": {"blocos": blocos,
                             "contexto": {"tempo_h": tempo_h, "energia": energia,
                                          "capacidade_q": 60},
                             "defaults_assumidos": defaults}}


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    caminho = str(tmp_path / "ipub.db")
    monkeypatch.setattr(db, "DB_PATH", caminho)
    return caminho


def test_persiste_blocos_com_flags_do_run(tmp_db):
    persistir_plano(_plano_fake())
    rows = ler_plano("2026-07-12")
    assert len(rows) == 3
    assert [r["task_tipo"] for r in rows] == ["mini-drill", "questoes", "fsrs"]
    assert rows[0]["volume_planejado"] == 3 and rows[1]["alvo_tema"] == "Tema B"
    assert rows[0]["tempo_h"] == 2.0 and rows[0]["energia"] == "baixa"
    assert rows[0]["defaults_assumidos"] == 0 and rows[0]["criado_em"]


def test_re_run_mesmo_dia_substitui_nunca_acumula(tmp_db):
    persistir_plano(_plano_fake())
    persistir_plano(_plano_fake(blocos=[
        {"tipo": "descanso", "qtd": 0, "alvo": None, "motivo": "m"}]))
    rows = ler_plano("2026-07-12")
    assert len(rows) == 1  # substituiu os 3 blocos; zero orfaos
    assert rows[0]["task_tipo"] == "descanso" and rows[0]["alvo_tema"] is None


def test_dias_diferentes_coexistem(tmp_db):
    persistir_plano(_plano_fake(data="2026-07-12"))
    persistir_plano(_plano_fake(data="2026-07-13"))
    assert len(ler_plano("2026-07-12")) == 3
    assert len(ler_plano("2026-07-13")) == 3


def test_leitura_ordenada_por_ordem(tmp_db):
    persistir_plano(_plano_fake())
    assert [r["ordem"] for r in ler_plano("2026-07-12")] == [1, 2, 3]


def test_schema_sem_coluna_de_texto_clinico(tmp_db):
    persistir_plano(_plano_fake())
    con = sqlite3.connect(tmp_db)
    cols = {r[1] for r in con.execute("PRAGMA table_info(plano_dia)")}
    con.close()
    assert cols == COLS_PERMITIDAS  # ids/enums/contadores/flags apenas


def test_defaults_assumidos_registrado(tmp_db):
    persistir_plano(_plano_fake(defaults=True, tempo_h=3.0, energia="media"))
    rows = ler_plano("2026-07-12")
    assert all(r["defaults_assumidos"] == 1 for r in rows)


def test_data_sem_plano_retorna_vazio(tmp_db):
    assert ler_plano("2099-01-01") == []


def test_falha_de_db_warn_e_nao_lanca(monkeypatch, capsys):
    def _explode():
        raise RuntimeError("db indisponivel")
    monkeypatch.setattr(db, "get_connection", _explode)
    try:
        persistir_plano(_plano_fake())  # nao pode lancar
    finally:
        pass
    assert "PLANO_DIA" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Parte 4 -- o bloco de cronograma sai de `plano_tarefas`, nao do calendario.
# --------------------------------------------------------------------------

def _tarefa(n, **kw):
    """Linha sintetica de `plano_tarefas`. Area sempre do vocabulario canonico
    (o writer valida por `validar_area` -- area fantasma derruba o lote)."""
    base = {"fonte": "extensivo", "ref_semana_fonte": 40, "tarefa_fonte": n,
            "semana_plano": 1, "ordem": n, "area": "Preventiva",
            "tema": "Tema %d" % n, "tipo": "Teoria I", "tipo_norm": "teoria",
            "url_lista": None, "q_previstas": 10, "status": "pendente"}
    base.update(kw)
    return base


def _semear(linhas):
    db.plano_upsert_tarefas(linhas, aplicar=True)


def _p_render(cron, pendencia=None):
    """`p` minimo para `day_plan.render` -- so o que o bloco de cronograma usa."""
    return {"data": "2026-09-17", "dormant": {"empty": True},
            "volume": {"total": 1, "acertos": 1, "hoje": 0, "mes": 0, "alvo_enamed": 2,
                       "faltam": 1, "dias_ate_marco": 1, "ritmo_alvo": 1.0, "marco": "m"},
            "fsrs": {"atrasados": 0, "hoje": 0, "backlog_novos": 0},
            "divida": {"atrasados": 0, "vencidos": 0, "regime_divida": False,
                       "teto_base": 60, "teto_efetivo": 60},
            "cronograma": cron,
            "planilha": {"estado": "nao_medido", "acao": "-", "db_total": 0},
            "plano_pendencia": pendencia or [], "sugestao_passo": "x"}


def test_semana_corrente_e_a_menor_com_pendencia(tmp_db):
    """Nao e a semana do calendario nem a menor da tabela: e a menor com PENDENCIA.
    Semana 1 fechada -> a corrente passa a ser a 2 (Technical Decision da spec)."""
    _semear([
        _tarefa(1, semana_plano=1, status="feita"),
        _tarefa(2, semana_plano=1, status="cortada"),
        _tarefa(3, semana_plano=2, status="pendente", q_previstas=30),
        _tarefa(4, semana_plano=2, status="feita", q_previstas=12),
        _tarefa(5, semana_plano=3, status="pendente", q_previstas=99),
    ])
    c = day_plan._cronograma_hoje(0, date.today())
    assert c["semana"] == 2, "menor semana_plano com pendente (got %s)" % c["semana"]
    assert c["fase"] == 1, "semanas 1-7 sao Fase 1"
    assert (c["feitas_semana"], c["tarefas_semana"]) == (1, 2), \
        "X/Y conta a semana SEM as cortadas (got %s/%s)" % (c["feitas_semana"],
                                                            c["tarefas_semana"])
    assert c["previstas"] == 42, "q previstas da semana (got %s)" % c["previstas"]
    assert c["restante_q"] == 129, "restante = q de TODAS as pendentes da Fase 1 (s189: " \
                                   "nunca as da Fase 2), nao so as da semana"


def test_proximas_tarefas_em_ordem_com_os_campos_do_dod(tmp_db):
    _semear([
        _tarefa(1, ordem=2, tema="Segundo"),
        _tarefa(2, ordem=1, tema="Primeiro", fonte="rf", ref_semana_fonte=17,
                tipo="Revisao por Questoes", q_previstas=51,
                url_lista="https://exemplo/lista"),
        _tarefa(3, ordem=3, tema="Feito", status="feita"),
        _tarefa(4, ordem=4, tema="Terceiro"),
    ])
    c = day_plan._cronograma_hoje(0, date.today())
    temas = [t["tema"] for t in c["proximas"]]
    assert temas == ["Primeiro", "Segundo", "Terceiro"], \
        "ordem do plano, sem as feitas (got %s)" % temas
    p0 = c["proximas"][0]
    assert (p0["fonte"], p0["tipo"], p0["q_previstas"], p0["url_lista"]) == (
        "rf", "Revisao por Questoes", 51, "https://exemplo/lista"), \
        "campos do DoD 1 (got %s)" % p0
    assert len(c["proximas"]) <= day_plan.PROXIMAS_TAREFAS, "teto de 3-5 tarefas"
    render = day_plan.render(_p_render(c))
    assert "Cronograma:** plano **semana 1**" in render, "DoD 1: a linha sai do plano"
    assert "https://exemplo/lista" in render and "51q" in render, "url + q no render"
    assert "Drive desatualizado" not in render, "DoD 1: o banner do Drive morreu"


def test_fronteira_de_fase_nao_diverge_de_plano_py():
    """A fronteira Fase 1 / Fase 2 mora em UM lugar so: `plano.semana_fase2(21)` e a
    primeira semana da Fase 2 por construcao, e `day_plan` nao pode digitar outra."""
    import plano as pl
    assert day_plan.PRIMEIRA_SEMANA_FASE2 == pl.semana_fase2(21)
    assert day_plan._fase_do_plano(pl.semana_fase2(21) - 1) == 1
    assert day_plan._fase_do_plano(pl.semana_fase2(21)) == 2
    assert day_plan._fase_do_plano(None) is None


def test_handoff_block_reporta_posicao_do_plano(tmp_db):
    _semear([_tarefa(1, status="feita"), _tarefa(2), _tarefa(3)])
    c = day_plan._cronograma_hoje(0, date.today())
    p = {"volume": {"total": 10, "acertos": 8, "hoje": 0, "alvo_enamed": 100,
                    "faltam": 90, "dias_ate_marco": 30, "ritmo_alvo": 3.0, "marco": "m"},
         "fsrs": {"atrasados": 0, "hoje": 0, "backlog_novos": 0},
         "divida": {"atrasados": 0, "vencidos": 0, "teto_efetivo": 60, "teto_base": 60,
                    "regime_divida": False},
         "cronograma": c}
    linhas = [l for l in day_plan.render_handoff_block(p).splitlines()
              if l.startswith("- **Posicao:**")]
    assert linhas, "o bloco do HANDOFF continua declarando a posicao"
    esperado = ("- **Posicao:** plano semana 1 (fase 1) · 1/3 tarefas da "
                "semana feitas")
    assert linhas[0].startswith(esperado), "formato do DoD 1 (got %r)" % linhas[0]
    assert "nominal S" not in linhas[0], "a posicao nominal por calendario morreu"


def test_tabela_vazia_silencia_em_vez_de_inventar(tmp_db):
    """Regra dos irmaos F1/POSICAO/B1: plano nao semeado NAO produz bloco, NAO
    produz linha de pendencia e NAO derruba o plano do dia."""
    assert day_plan._cronograma_hoje(0, date.today()) is None, "tabela ausente -> None"
    assert day_plan._plano_pendencia() == [], "tabela ausente -> zero pendencia"
    _semear([_tarefa(1, status="feita")])      # semeada, mas sem NENHUMA pendencia
    c = day_plan._cronograma_hoje(0, date.today())
    assert c is not None and c["semana"] is None, "sem pendencia -> semana desconhecida"
    assert c["proximas"] == [] and c["pendentes_total"] == 0
    assert day_plan._plano_pendencia() == [], "origem NULL nao e pendencia de revisao"
    assert "Status do plano por conferir" not in day_plan.render(_p_render(c))


def test_pendencia_de_revisao_sai_enquanto_houver_origem_aproximada(tmp_db):
    """DoD 3: UMA linha enquanto restar `dashboard_2026-09-10`; silencio ao zerar."""
    _semear([
        _tarefa(1, status="feita", origem_conclusao=db.ORIGEM_APROXIMADA),
        _tarefa(2, status="pendente", origem_conclusao=db.ORIGEM_USUARIO),
    ])
    pend = day_plan._plano_pendencia()
    assert [(x["area"], x["aproximadas"]) for x in pend] == [("Preventiva", 1)], \
        "conta por area (got %s)" % pend
    com = day_plan.render(_p_render(None, pend)).splitlines()
    linhas = [l for l in com if "Status do plano por conferir" in l]
    assert len(linhas) == 1, "UMA linha, nunca um bloco (got %d)" % len(linhas)
    assert db.ORIGEM_APROXIMADA in linhas[0] and "--revisar-area" in linhas[0], \
        "a linha nomeia a origem e o comando corretivo"
    assert "Status do plano por conferir" not in day_plan.render(_p_render(None, []))


def test_calendario_e_snapshot_do_drive_sairam_do_codigo():
    """DoD 2: as funcoes do ramo calendario/Drive foram REMOVIDAS, nao comentadas,
    e nenhuma suite volta a tratar o snapshot do Drive como fonte VIVA.

    O oraculo do codigo e a CHAMADA (`get_preparacao(...)`), nao a mencao: a lapide
    do modulo cita a chave morta de proposito -- narrar a revogacao e o registro
    correto (mesma regra de isencao do gate CONTRATO_REVOGADO)."""
    import inspect
    from pathlib import Path
    for morto in ("_conclusao_drive", "_ordenar_por_drive",
                  "_resolver_semana_conteudo", "_semana_conteudo"):
        assert not hasattr(day_plan, morto), "%s deveria ter sido removido" % morto
    fonte = inspect.getsource(day_plan)
    for chamada in ('get_preparacao("cronograma_conclusao_drive")',
                    "get_preparacao('cronograma_conclusao_drive')"):
        assert chamada not in fonte, "day_plan voltou a ler o snapshot: %s" % chamada
    culpadas = []
    for suite in sorted(Path(day_plan.__file__).parent.glob("test_*.py")):
        if suite.name == Path(__file__).name:
            continue                      # esta suite DECLARA o invariante
        for linha in suite.read_text(encoding="utf-8").splitlines():
            if "cronograma_conclusao_drive" in linha and not linha.strip().startswith("#"):
                culpadas.append("%s: %s" % (suite.name, linha.strip()[:70]))
    assert culpadas == [], \
        "DoD 2: suite tratando o snapshot do Drive como fonte viva: %s" % culpadas


# --------------------------------------------------------------------------
# s189 (F123, spec trilha-autoridade-unica) -- ritmo da Fase 1 e cota do dia:
# numerador e denominador da MESMA fase.
# --------------------------------------------------------------------------

HOJE_F123 = date(2026, 9, 18)          # 44 dias ate FIM_CONTEUDO_ALVO (01/11)
CALENDARIO_FAKE = {1: (date(2026, 9, 19), date(2026, 9, 20)),
                   2: (date(2026, 9, 21), date(2026, 9, 27)),
                   3: (date(2026, 9, 28), date(2026, 10, 4))}


def test_ritmo_da_fase1_nao_conta_fase2_nem_reserva(tmp_db):
    """F123a: o boot somava TODAS as pendentes (a Fase 2 vai ate set/2027, mais a reserva)
    e dividia pelos dias da Fase 1 -- 273 q/dia no banco real de 18/09. Com Fase 2 e reserva
    NO BANCO, so as semanas 1-7 entram no numerador. Alvo vencido -> sem divisor."""
    _semear([
        _tarefa(1, semana_plano=1, status="feita", q_previstas=40),
        _tarefa(2, semana_plano=2, q_previstas=30),
        _tarefa(3, semana_plano=7, q_previstas=70),
        _tarefa(4, semana_plano=8, q_previstas=500),                 # Fase 2
        _tarefa(5, semana_plano=20, q_previstas=300),                # Fase 2
        _tarefa(6, semana_plano=None, ordem=None, q_previstas=77),   # reserva
    ])
    c = day_plan._cronograma_hoje(0, HOJE_F123, calendario={})
    assert c["restante_q"] == 100, "so a Fase 1 no numerador (got %s)" % c["restante_q"]
    assert c["fora_da_fase1_q"] == 877, "Fase 2 + reserva ficam FORA, mas declaradas"
    assert c["dias_grade"] == 44, "o divisor segue sendo FIM_CONTEUDO_ALVO (s159)"
    assert c["ritmo_cronograma"] == round(100 / 44, 1)
    render = day_plan.render(_p_render(c))
    assert "ritmo da Fase 1" in render and "100q pendentes" in render
    assert "977" not in render and "900q" not in render, "a soma de todas as fases vazou"
    vencido = day_plan._cronograma_hoje(0, date(2026, 11, 2), calendario={})
    assert vencido["ritmo_cronograma"] is None and vencido["dias_grade"] is None, \
        "alvo vencido nao ganha divisor inventado (era max(dias, 1))"
    assert "sem divisor" in day_plan.render(_p_render(vencido))


def test_cota_do_dia_divide_o_restante_da_semana_pelos_dias():
    """F123b: cota = q pendentes ate a semana de CALENDARIO corrente / dias que faltam nela.
    Atraso soma (e e declarado); Fase 2 e reserva nunca entram; sem calendario, ou depois
    dele, a cota e None -- nunca um numero inventado."""
    pend = [{"semana_plano": 1, "q_previstas": 162, "status": "pendente"},
            {"semana_plano": 2, "q_previstas": 500, "status": "pendente"},
            {"semana_plano": 9, "q_previstas": 999, "status": "pendente"},     # Fase 2
            {"semana_plano": None, "q_previstas": 77, "status": "pendente"}]   # reserva
    c = day_plan.cota_do_dia(pend, CALENDARIO_FAKE, date(2026, 9, 18))        # vespera
    assert (c["semana"], c["dias"], c["q_restantes"], c["cota"], c["comecou"]) == \
        (1, 2, 162, 81, False), c
    c = day_plan.cota_do_dia(pend, CALENDARIO_FAKE, date(2026, 9, 20))        # ultimo dia
    assert (c["dias"], c["cota"], c["comecou"]) == (1, 162, True), c
    c = day_plan.cota_do_dia(pend, CALENDARIO_FAKE, date(2026, 9, 22))        # semana 2
    assert (c["semana"], c["dias"], c["q_restantes"], c["q_atrasadas"]) == \
        (2, 6, 662, 162), "a semana 1 atrasada soma e e declarada (got %s)" % c
    assert c["cota"] == 111, "ceil(662 / 6)"
    assert day_plan.cota_do_dia(pend, CALENDARIO_FAKE, date(2026, 10, 5)) is None
    assert day_plan.cota_do_dia(pend, {}, date(2026, 9, 22)) is None


def test_render_declara_o_que_cada_regua_mede(tmp_db):
    """F123 + pedido do /ai-eng: duas reguas para 'quantas questoes por dia' so convivem se
    cada uma disser o que mede -- marco de volume, ritmo da Fase 1, cota do dia."""
    _semear([_tarefa(1, semana_plano=1, q_previstas=162),
             _tarefa(2, semana_plano=9, q_previstas=999)])
    c = day_plan._cronograma_hoje(0, HOJE_F123, calendario=CALENDARIO_FAKE)
    render = day_plan.render(_p_render(c))
    assert "Cota do dia:** ~81q" in render, "cota da semana 1 = 162q / 2 dias"
    assert "marco de volume" in render, "a linha de Volume declara que mede o marco"
    assert "2o ciclo 12k" not in render, "o rotulo arredondava 12.500 para 12k"
    cabecalho = [l for l in render.splitlines() if "**Cronograma:**" in l]
    assert cabecalho and "cota ~81q/dia" in cabecalho[0], \
        "a cota vai no cabecalho: o hook de boot so injeta as 8 primeiras linhas"
    bloco = day_plan.render_handoff_block(_p_render(c))
    assert "Ritmo do marco de volume" in bloco and "cota ~81q/dia" in bloco


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
