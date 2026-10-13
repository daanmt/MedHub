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
# s203 (27/09/2026, decisao do operador): UMA meta (10.000 questoes em 01/11) e UM ritmo -- o
# dela. O plano "anda junto": a Fase 1 aparece como COBERTURA da meta (fechando as listas, onde
# o acumulado chega), nunca como um 2o "por dia". ⚰️ *Eram 4 reguas no boot (s189, F123):
# marco de volume, ritmo da Fase 1, cota do dia da semana de calendario e o Ciclo 2026 -- a
# cota despejava a semana inteira no domingo ("~474q/dia ate 27/09").*
# --------------------------------------------------------------------------

HOJE_F123 = date(2026, 9, 18)          # 44 dias ate FIM_CONTEUDO_ALVO (01/11)


def test_cobertura_da_fase1_nao_conta_fase2_nem_reserva(tmp_db):
    """F123a segue: so as semanas 1-7 contam (a Fase 2 vai ate set/2027, mais a reserva). O que
    mudou e a FORMA: a Fase 1 vira a cobertura da meta -- acumulado + pendentes da Fase 1 --, com
    os simulados declarados, e nao um ritmo proprio."""
    _semear([
        _tarefa(1, semana_plano=1, status="feita", q_previstas=40),
        _tarefa(2, semana_plano=2, q_previstas=30),
        _tarefa(3, semana_plano=7, q_previstas=70),
        _tarefa(7, semana_plano=3, area="Simulado", q_previstas=60),
        _tarefa(4, semana_plano=8, q_previstas=500),                 # Fase 2
        _tarefa(5, semana_plano=20, q_previstas=300),                # Fase 2
        _tarefa(6, semana_plano=None, ordem=None, q_previstas=77),   # reserva
    ])
    c = day_plan._cronograma_hoje(9000, HOJE_F123)
    assert c["restante_q"] == 160, "so a Fase 1 (got %s)" % c["restante_q"]
    assert c["simulados_q"] == 60, "os simulados da Fase 1 sao declarados a parte"
    assert c["fora_da_fase1_q"] == 877, "Fase 2 + reserva ficam FORA, mas declaradas"
    assert c["fechando_q"] == 9160, "acumulado + pendentes da Fase 1"
    assert "ritmo_cronograma" not in c and "cota" not in c and "ritmo_meta" not in c
    render = day_plan.render(_p_render(c))
    linha = [l for l in render.splitlines() if "Plano da Fase 1" in l]
    assert linha and "160q pendentes" in linha[0] and "60q de simulados" in linha[0], render
    assert "9160" in linha[0], "a cobertura diz onde o acumulado chega fechando o plano"
    assert "977" not in render and "1037" not in render, "a soma de todas as fases vazou"
    assert "q/dia" not in linha[0], "a Fase 1 nao carrega um 2o ritmo"


def test_uma_meta_um_ritmo_no_boot_e_no_handoff(tmp_db):
    """O boot e o bloco do HANDOFF dizem UM 'por dia': o da meta. Sem cota de semana, sem ritmo
    da Fase 1, sem Ciclo 2026."""
    _semear([_tarefa(1, semana_plano=1, q_previstas=162),
             _tarefa(2, semana_plano=9, q_previstas=999)])
    c = day_plan._cronograma_hoje(0, HOJE_F123)
    p = _p_render(c)
    render = day_plan.render(p)
    assert render.count("q/dia") == 1, "UM ritmo no boot (got %d): %s" % (render.count("q/dia"), render)
    for morto in ("Cota do dia", "cota ~", "ritmo da Fase 1", "Ciclo 2026", "12500", "marco de volume"):
        assert morto not in render, morto
    meta = [l for l in render.splitlines() if "**Meta:**" in l]
    assert meta and "~1.0q/dia" in meta[0], "o ritmo e o da meta (volume_vs_marco)"
    bloco = day_plan.render_handoff_block(p)
    assert bloco.count("q/dia") == 1 and "cota" not in bloco and "Fase 1 ~" not in bloco, bloco


def _hook_de_boot():
    """O hook nao e pacote importavel: carrega por path (mesmo padrao do F102)."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "memory_boot_s189", Path(day_plan.__file__).parent / "hooks" / "memory_boot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_meta_cabe_no_corte_do_boot(tmp_db):
    """s189 (nota do /ai-eng), na regua de s203: o ritmo do dia tem de CHEGAR ao boot. A posicao
    e presa contra o cap REAL do hook, nunca contra um literal. Pior caso de linhas acima: com
    Datas E overflow de blackout (F71)."""
    mb = _hook_de_boot()
    _semear([_tarefa(1, semana_plano=1, q_previstas=162)])
    c = day_plan._cronograma_hoje(0, HOJE_F123)
    p = _p_render(c)
    p["provas"] = day_plan.countdown_provas(HOJE_F123)
    p["fsrs"] = dict(p["fsrs"], overflow_blackout=[{"card_id": 1, "due": "2026-11-01"}])
    texto = day_plan.render(p)
    linhas = [l for l in texto.splitlines() if l.strip()]
    posicao = next(i for i, l in enumerate(linhas, 1) if "**Meta:**" in l)
    assert posicao <= mb._DAY_PLAN_MAX_LINES,         "a meta e a linha %d e o boot injeta %d" % (posicao, mb._DAY_PLAN_MAX_LINES)
    assert "**Meta:**" in mb._resumir_plano(texto, mb._DAY_PLAN_MAX_LINES)


def test_corte_do_boot_se_declara():
    """Cap que avisa > cap que trunca em silencio: o boot diz quantas linhas cortou."""
    mb = _hook_de_boot()
    texto = "\n".join("linha %d" % i for i in range(1, 13))
    resumo = mb._resumir_plano(texto, 8).splitlines()
    assert resumo[:8] == ["linha %d" % i for i in range(1, 9)]
    assert "+4 linha(s) do plano cortadas" in resumo[8]
    assert "cortadas" not in mb._resumir_plano("a\n\nb", 8), "sem corte, sem aviso"
    corte = mb._resumir_plano(texto, 8, completo=mb._CMD_PANORAMA).splitlines()[8]
    assert "plano.py --panorama" in corte, "o corte do panorama aponta para o comando DELE"


def test_boot_entrega_o_panorama(monkeypatch):
    """s190 (pedido do operador, 20/09/2026): o boot abre com o PANORAMA -- tarefas em aberto
    com o que fazer em cada, meta, passos, metricas. Tres pecas, as tres presas aqui: (1) o
    panorama do plano entra como secao propria; (2) as metricas do Plano do Dia moram depois
    da 8a linha, entao o cap antigo as cortava -- o cap cobre o plano inteiro de hoje; (3) o
    texto-contrato manda o agente ENTREGAR o panorama, e continua mandando oferecer o
    proximo ato sem executar a sessao. Falha do panorama -> secao ausente, boot de pe."""
    mb = _hook_de_boot()
    monkeypatch.setattr(mb, "_day_plan_summary", lambda: "- plano")
    monkeypatch.setattr(mb, "_drift_flag", lambda *_a, **_k: "")
    monkeypatch.setattr(mb, "_panorama_summary", lambda: "## 🧭 Panorama do plano -- semana 2")
    ctx = mb.build_context()
    assert ctx.index("## Plano do Dia") < ctx.index("Panorama do plano -- semana 2") \
        < ctx.index("[Boot v2"), "plano, panorama e so entao o contrato"
    # s226 (sprint-final-uerj part-5): o item (2) e o HOJE DO SPRINT, o mesmo do Painel e das Listas.
    # ⚰️ *Era "ONDE ESTAMOS -- semana do plano, feitas x pendentes, atraso" e "TAREFAS EM ABERTO".*
    for secao in ("PANORAMA", "META", "HOJE DO SPRINT", "TAREFAS DE HOJE", "PASSOS DE HOJE",
                  "MÉTRICAS", "Próximo ato", "NÃO execute a sessão inteira",
                  "fora do sprint", "simulado do dia", "sem sprint no banco: a semana do plano"):
        assert secao in mb._CONTRATO, f"o contrato do boot perdeu: {secao}"
    assert "ONDE ESTAMOS" not in mb._CONTRATO, "a semana do plano saiu do item (2) do boot"
    assert mb._DAY_PLAN_MAX_LINES >= 30, \
        "ritmo real x necessario e diagnostico sao as linhas ~20-27 do Plano do Dia"

    monkeypatch.setattr(mb, "_panorama_summary", lambda: "")
    assert "Panorama do plano" not in mb.build_context().split("[Boot v2")[0]


# --------------------------------------------------------------------------
# s226 (sprint-final-uerj part-5): o boot e o recomendador falam o "hoje" do sprint -- a MESMA
# `plano.agenda_sprint` do "Plano de hoje" do Painel (part-3) e da aba Listas (part-4).
# --------------------------------------------------------------------------

HOJE_SPRINT = date(2026, 10, 13)


def _semear_sprint():
    """Plano sintetico com agenda: a rolada (dia 12, pendente) entra no hoje; a feita do dia 13 nao;
    amanha uma tarefa; um simulado em 17/10; uma fora do sprint com o motivo na nota."""
    _semear([
        _tarefa(1, semana_plano=3, area="Cirurgia", tema="Rolada de ontem", q_previstas=20,
                url_lista="https://exemplo/rolada"),
        _tarefa(2, semana_plano=4, area="Pediatria", tema="Asma | Bronquiolite", q_previstas=30),
        _tarefa(3, semana_plano=4, area="Cirurgia", tema="Feita hoje", status="feita", q_previstas=25),
        _tarefa(4, semana_plano=5, area="Obstetrícia", tema="Pré-Natal", q_previstas=40),
        _tarefa(5, semana_plano=5, area="Simulado", tema="UERJ 2026 -- prova INTEIRA", q_previstas=100),
        _tarefa(6, semana_plano=6, area="Cardiologia", tema="Fora", q_previstas=50),
    ])
    ids = {l["tarefa_fonte"]: int(l["id"]) for l in db.plano_listar()}
    dias = {1: "2026-10-12", 2: "2026-10-13", 3: "2026-10-13", 4: "2026-10-14", 5: "2026-10-17"}
    mud = [{"id": ids[n], "dia_plano": d, "nota": None} for n, d in dias.items()]
    mud.append({"id": ids[6], "dia_plano": None, "nota": "sprint: fora (sem vaga ate 31/10)"})
    db.plano_set_dias(mud, aplicar=True)
    return ids


def test_boot_painel_listas_mesmo_hoje(tmp_db, monkeypatch):
    """DoD 3 (PRD Success Criteria 2): do MESMO banco sintetico, os ids de hoje e o total de questoes
    sao iguais no boot (bloco Cronograma e panorama), no Painel (part-3) e nas Listas (part-4) -- e a
    ordem tambem."""
    import hub
    import painel
    import plano
    ids = _semear_sprint()
    monkeypatch.setattr(painel, "_aulas_por_tarefa", lambda: {})
    monkeypatch.setattr(painel, "_rd_nao_assinada", lambda: None)
    c = day_plan._cronograma_hoje(0, HOJE_SPRINT)
    do_boot = [t["id"] for t in c["sprint"]["hoje"]]
    linhas = plano.linhas_com_q_hub(db.plano_listar())
    no_painel = painel._bloco_sprint(linhas, HOJE_SPRINT)
    nas_listas = hub.dados_sprint(linhas, HOJE_SPRINT)
    assert do_boot == [ids[1], ids[2]], "a rolada de ontem entra no hoje; a feita nao"
    assert do_boot == [t["id"] for t in no_painel["hoje"]] == nas_listas["hoje"]
    assert c["sprint"]["q_hoje"] == no_painel["q_hoje"] == nas_listas["q_hoje"] == 50
    # o TEXTO do boot e do panorama mostra as mesmas tarefas, na mesma ordem
    render = day_plan.render(_p_render(c))
    pos = [render.index("#%d " % i) for i in do_boot]
    assert pos == sorted(pos) and "#%d " % ids[3] not in render
    panorama = plano.render_panorama_sprint(plano.resumo_sprint(linhas, HOJE_SPRINT))
    pos = [panorama.index("#%d " % i) for i in do_boot]
    assert pos == sorted(pos) and "Hoje (13/10):** 2 tarefa(s) · 50 questoes" in panorama


def test_bloco_cronograma_do_boot_com_sprint(tmp_db):
    """DoD 1: com sprint, "Hoje (DD/MM): N tarefas · Q questoes" com cada tarefa e o que fazer,
    "Amanha" em 1 linha e "Fora do sprint: N"; sem semana e sem atrasadas. A cobertura conta o
    sprint (acumulado + q com dia) e declara o fora."""
    ids = _semear_sprint()
    c = day_plan._cronograma_hoje(9000, HOJE_SPRINT)
    s = c["sprint"]
    assert (s["q_sprint"], s["simulados_q"], s["fora"], s["q_fora"]) == (190, 100, 1, 50)
    assert s["fechando_q"] == 9190 and s["amanha"]["data"] == "2026-10-14"
    linhas = day_plan.render(_p_render(c)).splitlines()
    i = next(n for n, l in enumerate(linhas) if "Cronograma" in l)
    assert "**Hoje (13/10): 2 tarefa(s) · 50 questoes**" in linhas[i]
    assert linhas[i + 1].strip().startswith("1. #%d" % ids[1]) and "lista: https://exemplo/rolada" in linhas[i + 1]
    assert linhas[i + 2].strip().startswith("2. #%d" % ids[2]) and "Asma · Bronquiolite" in linhas[i + 2]
    assert "caderno" in linhas[i + 2], "sem link e com questoes previstas: o que fazer e o caderno"
    assert "Amanha (14/10): 1 tarefa(s) · 40q -- Pré-Natal" in linhas[i + 3]
    assert "Fora do sprint: 1 tarefa(s) · 50q" in linhas[i + 4]
    assert "acumulado chega a 9190 em 01/11" in linhas[i + 5] and "fora do sprint 50q" in linhas[i + 5]
    render = "\n".join(linhas)
    for morto in ("plano **semana", "atrasada", "Plano da Fase 1", "tarefas feitas"):
        assert morto not in render, morto
    assert render.count("q/dia") == 1, "o sprint nao traz um 2o ritmo"


def test_sem_sprint_o_bloco_antigo_segue(tmp_db):
    """Degradacao declarada: banco sem `dia_plano` -> `sprint` None e o bloco da semana."""
    _semear([_tarefa(1, semana_plano=2, q_previstas=30)])
    c = day_plan._cronograma_hoje(0, HOJE_SPRINT)
    assert c["sprint"] is None
    render = day_plan.render(_p_render(c))
    assert "Cronograma:** plano **semana 2**" in render and "Hoje (" not in render


def _sinais(sprint=None, semana=4):
    return {"dias_grade": 19, "restante_grade_q": 2000, "ritmo_real": 20.0, "vencidos": 10,
            "teto_efetivo": 100, "backlog_novos": 5, "semana_conteudo": semana,
            "tema_alvo": "Asma", "frescos_tema_alvo": [], "sprint": sprint}


def test_recomendador_com_sprint_le_o_dia_da_agenda():
    """DoD 2: com sprint, nada de "simulado periodico" pela semana nem "capacidade ~Nq" por formula:
    as questoes sao as tarefas de hoje e o simulado e o do dia na agenda; os cards seguem."""
    hoje = [{"id": 1, "area": "Cirurgia", "tema": "Asma", "q": 20},
            {"id": 2, "area": "Pediatria", "tema": "B", "q": 30}]
    r = day_plan.recomendar_dia(_sinais({"hoje": hoje, "simulado_hoje": None}))
    assert [b["tipo"] for b in r["blocos"]] == ["questoes", "fsrs"], r["blocos"]
    assert r["blocos"][0]["qtd"] == 50 and "plano de hoje do sprint" in r["blocos"][0]["motivo"]
    for morto in ("slot periódico", "capacidade ~", "capacidade máxima", "múltipla de"):
        assert morto not in repr(r), morto
    sim = {"id": 9, "area": "Simulado", "tema": "UERJ 2026", "q": 100}
    r = day_plan.recomendar_dia(_sinais({"hoje": [sim], "simulado_hoje": sim}))
    assert [(b["tipo"], b["alvo"]) for b in r["blocos"]] == [("simulado", "UERJ 2026"), ("fsrs", "fila do dia")]
    sem = day_plan.recomendar_dia(_sinais(None))
    assert "slot periódico" in repr(sem) and "capacidade ~" in repr(sem), "sem sprint, R3/R4 de antes"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
