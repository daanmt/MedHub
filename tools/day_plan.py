"""day_plan.py — Plano do Dia para o boot proativo.

Compõe: tema dormente do dia, volume vs ritmo-alvo (ENAMED), fila FSRS
(vencidos + backlog), a próxima tarefa do PLANO e uma sugestão de passo imediato.
O boot (AGENTE §2 passo 4) roda isto e lidera com o plano.

⚰️ **O ramo CALENDÁRIO do bloco de cronograma morreu em 17/09/2026** (PRD
`plano-ssot-e-cards-v2`, Parte 4; `cronograma-contract` v1.3). Até aqui
`_cronograma_hoje` respondia "o que vem agora" com TRÊS fontes que nunca
conversaram, e as três estão mortas:
  ⚰️ `grade.json` como fonte de ordem (calendário do PDF da Reta Final);
  ⚰️ o snapshot em `preparacao_estado.cronograma_conclusao_drive`, morto,
     ⚰️ que `_conclusao_drive` lia e `cronograma.py --sync-drive` escrevia --
     os dois removidos (Partes 4 e 8);
  ⚰️ a ordem manual do xlsx (`_ordenar_por_drive`), morta.
Nenhuma delas era verdade-de-estado: o snapshot envelhecia em silêncio (banner de
42 dias no boot real de 06/09) e a ordem que o usuário reordenava à mão nunca
chegava ao agente. Agora a fonte é UMA -- `plano_tarefas` (`tools/plano.py`), a
mesma tabela que `--concluir`/`--cortar`/`--mover` editam. As três funções foram
REMOVIDAS, não comentadas. ⚰️ *A frase que este parágrafo trazia até 17/09 --
"o código do sync segue vivo em `tools/cronograma.py`, remoção = Parte 8" --
expirou em 18/09/2026: a Parte 8 chegou e o sync do Drive foi removido de lá
também, sob snapshot reversível.*

Escritas (únicas, ambas de metadado de processo): a condição declarada do dia
(condicao_dia via db.registrar_condicao_dia) e o PLANO recomendado do dia
(plano_dia via persistir_plano — spec telemetria-estudo-part-1; o realizado já
vive em fsrs_revlog/review_log/sessoes_bulk, o planejado agora sobrevive para a
aderência planejado×real). Todo o resto permanece read-only; --no-persist simula.

Reusa: dormant_refresh.pick (dormência), performance.get_totais/_questoes_do_mes/MARCOS
(volume/ritmo), app.utils.db (fila FSRS). Não duplica constantes de meta.

Uso: python tools/day_plan.py [--json]
"""
import argparse
import glob
import importlib
import json
import math
import os
import re
import sys
from datetime import date, datetime

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import app.utils.db as db                                     # noqa: E402
import dormant_refresh as dr                                  # noqa: E402
from performance import (  # noqa: E402
    FIM_CONTEUDO_ALVO,
    MARCOS,
    get_questoes_do_mes,
    get_totais,
    volume_vs_marco,
)


def _warn_degradacao(componente, erro):
    """F60 (descolar part-6): a degradacao graciosa CONTINUA -- so deixa de ser muda.

    Imprime `[WARN] <componente>: <erro curto>` em stderr (ASCII, 1 linha,
    truncado). O plano do dia segue saindo com o bloco ausente -- o que muda e
    que o operador passa a SABER que ele saiu sem zona/frieza/prescricao, em
    vez de ler um plano incompleto como se fosse completo. stderr de proposito:
    o stdout do day_plan e consumido pelo hook de SessionStart.
    """
    msg = str(erro).replace("\n", " ").strip() or type(erro).__name__
    if len(msg) > 120:
        msg = msg[:117] + "..."
    print(f"[WARN] {componente}: {msg}", file=sys.stderr)


#: F132 (s195): replica LITERAL de `app.utils.db.RETIDO_REFORJA_SUBQUERY` (este CLI nao
#: importa o modulo): card com marca de reforja aberta de origem humana fica fora da fila,
#: logo fora de `vencidos` -- senao o painel contaria o que a fila nao serve (F64: UM contador).
_RETIDO_REFORJA = """
    SELECT card_id FROM reforja_marks
    GROUP BY card_id, motivo
    HAVING SUM(evento = 'marcada') > SUM(evento IN ('fechada', 'descartada'))
       AND SUM(evento = 'marcada' AND COALESCE(origem, '') NOT LIKE 'detector:%') > 0
"""


def _fsrs_counts(con):
    now = datetime.now()
    ts = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(" ")
    te = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat(" ")
    base = ("FROM fsrs_cards fc JOIN flashcards f ON f.id=fc.card_id "
            "WHERE COALESCE(f.needs_qualitative,0) < 2")
    tem_marcas = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                             "AND name='reforja_marks'").fetchone() is not None
    if tem_marcas:
        base += " AND f.id NOT IN (%s)" % _RETIDO_REFORJA
    cur = con.cursor()

    def c(extra, *p):
        return cur.execute(f"SELECT COUNT(*) {base} {extra}", p).fetchone()[0]

    return {
        "atrasados": c("AND fc.state>0 AND fc.due < ?", ts),
        "hoje": c("AND fc.state>0 AND fc.due >= ? AND fc.due <= ?", ts, te),
        "backlog_novos": c("AND fc.state = 0"),
    }


# s126 -- virada multi-banca: a meta de volume deixa de ser "10k até o ENAMED" e passa a ser
# o 2o ciclo (UERJ/USP). Nomes e números vêm de performance.MARCOS, fonte única.
META_CICLO, DATA_CICLO = MARCOS[1][1], MARCOS[1][2]   # 12.500 @ 31/12/2026


def DIAS_ATE_CICLO(hoje):
    return (DATA_CICLO - hoje).days


# ---------------------------------------------------------------------------
# Entidade multi-prova (spec consolidacao-part-4). O calendário do estudante tem
# mais de uma data e elas NAO sao a mesma coisa: ENAMED (13/09) e PROVA; o fim da
# grade EMED (25/10) e fecho de CRONOGRAMA, ~6 semanas DEPOIS da prova. Confundir
# as duas foi o que produziu o ritmo-alvo ficticio corrigido na s126.
# 🔴 Fronteira dura: este bloco e DISPLAY (countdown no cabecalho do plano). O
# RITMO continua calculado contra a GRADE em _cronograma_hoje (correcao deliberada
# da s126) -- nada daqui alimenta formula de ritmo.
# UERJ/USP entram em core/provas.json quando houver edital -- sem codigo novo.
# ---------------------------------------------------------------------------
# F88 (s174): o parser vive em app/utils/provas.py (leitor UNICO -- o balanceador FSRS
# tambem le de la). Re-export para os consumidores e a suite test_provas.
from app.utils.provas import PROVAS_PATH, carregar_provas  # noqa: E402,F401


def _texto_countdown(nome, tipo, dias):
    """Rotulo por TIPO: prova conta para a data; grade conta para o fecho."""
    if tipo == "grade":
        if dias > 0:
            return f"grade fecha em {dias}d"
        return "grade fecha hoje" if dias == 0 else f"grade fechou ha {-dias}d"
    if dias > 0:
        return f"{nome} em {dias}d"
    return f"{nome} e hoje" if dias == 0 else f"{nome} foi ha {-dias}d"


def countdown_provas(hoje, provas=None, path=None):
    """[{nome, tipo, data, dias, texto}] -- dias = data - hoje (hoje inclusive,
    dia do evento exclusivo; mesma convencao de _cronograma_hoje)."""
    itens = provas if provas is not None else carregar_provas(path)
    saida = []
    for p in itens:
        dias = (p["data"] - hoje).days
        saida.append({"nome": p["nome"], "tipo": p["tipo"],
                      "data": p["data"].isoformat(), "dias": dias,
                      "texto": _texto_countdown(p["nome"], p["tipo"], dias)})
    return saida


def render_countdown(provas):
    """Linha unica do cabecalho: 'ENAMED em 30d · grade fecha em 72d'.
    Sem provas legiveis -> string vazia (o cabecalho simplesmente nao ganha a linha)."""
    return " · ".join(p["texto"] for p in provas) if provas else ""


# Política de teto dinâmico (F4 -- decisão do operador 2026-07-05).
# Norma: core/contracts/fsrs-management-contract.md §Teto dinâmico.
# s126: teto sobe 30 -> 40 (usuário pediu "flashcards mais frequentes" ao trocar o regime de
# sprint pelo de constância; as questões caem de ~96 para ~55/dia e a folga vai pros cards).
# s159 (virada UERJ/MFC): teto sobe 40 -> 60, ritmo declarado sustentável pelo usuário
# ("60q/dia + 60 flashcards/dia"). O CAP cai de 2x para 1.5x no mesmo movimento: dobrar o teto
# em regime de dívida (120/dia) reinstalaria exatamente o pico-e-queda que o usuário rejeitou
# ("de nada adianta fazer 500 questões em 5 dias e depois passar 2~3 dias sem estudar").
# s196 (25/09/2026): teto 60 -> 90 por decisão do operador ("pode subir o limite para 90 cards");
# CAP 1.0 = 90 também em dívida (135/dia reinstalaria o pico-e-queda).
TETO_BASE = 90            # cards/dia fora do regime de dívida
CAP_MULTIPLICADOR = 1.0   # teto_efetivo nunca excede CAP_MULTIPLICADOR * TETO_BASE

# Recomendador do dia (PRD orquestracao part-2).
# Norma e significado de cada parâmetro: core/contracts/orquestracao-contract.md
# (a tabela de parâmetros do contrato espelha ESTES nomes/valores — paridade testada).
JANELA_RITMO_DIAS = 14            # janela móvel do ritmo real (q/dia)
TEMPO_DEFAULT_H = 4.0             # horas assumidas sem --tempo
ENERGIA_DEFAULT = "media"         # energia assumida sem --energia
QUESTOES_POR_HORA = 15            # conversão tempo -> capacidade de questões
LIMIAR_FOLGA_DESCANSO_DIAS = 3    # folga projetada mínima p/ descanso com energia baixa
PERIODO_SIMULADO_SEMANAS = 4      # slot de simulado a cada N semanas de conteúdo
FRESCOS_JANELA_HORAS = 48         # janela do mini-drill anti-reincidência
FSRS_LEVE_CAP = 15                # cap de cards no dia leve/descanso
FATOR_ENERGIA = {"alta": 1.0, "media": 0.85, "baixa": 0.6}  # modula a capacidade


def vencidos_de(fsrs):
    """F64 (s176): o contador do regime de dívida tem UM nome -- `vencidos`.

    `vencidos = atrasados + hoje`. A divergência que o achado registra: o código
    disparava o regime por `atrasados` e o operador lia `vencidos`. Na s162 havia
    **45 atrasados + 22 p/ hoje = 67**: o dono leu "67 > 60, logo regime de
    dívida", o código leu "45 < 60, teto base", e o agente recomendou PARAR o
    estudo com base no número do código. A leitura do dono prevaleceu e está
    escrita: **card vencido hoje é dívida igual a card vencido ontem** -- o que
    define dívida é a fila não drenada, não a data em que ela venceu.

    Consequência do critério antigo: numa dívida composta majoritariamente por
    cards de HOJE, o regime nunca disparava e o teto travava em 60 com a fila
    inteira vencida. Norma: `core/contracts/fsrs-management-contract.md`.
    """
    return int(fsrs.get("atrasados", 0) or 0) + int(fsrs.get("hoje", 0) or 0)


def _teto_efetivo(vencidos):
    """Teto do dia: regime de dívida quando `vencidos` > TETO_BASE; o teto sobe
    até o cap para drenar. O argumento é `vencidos` (F64), NUNCA `atrasados`."""
    if vencidos > TETO_BASE:
        return int(min(TETO_BASE + vencidos, CAP_MULTIPLICADOR * TETO_BASE))
    return TETO_BASE


def _diagnostico():
    """Variância/zona + habilidades reincidentes + débito de simulado.

    s126: a média já está boa (77,6%) e não diz o que fazer; a **variância**
    entre blocos é o sinal que prescreve. Degradação graciosa em bloco: sinal
    ausente nunca derruba o plano do dia (mesmo contrato de `_cronograma_hoje`).
    """
    out = {}
    try:
        import variancia as V
        z = V.zona()
        if z.get('zona'):
            out['zona'] = z['zona']
            out['prescricao'] = z['prescricao']
            out['desvio'] = z['metricas']['desvio']
            out['media_blocos'] = z['metricas']['media']
            out['cobertura_pct'] = z['cobertura']['pct']
            out['acao_variancia'] = z.get('acao_variancia')
        out['simulado'] = V.simulado_check()
    except Exception as e:
        _warn_degradacao("zona/prescricao", e)
    try:
        import app.utils.db as _db
        df = _db.get_habilidades_reincidentes(limit=3, min_temas=2)
        if df is not None and not df.empty:
            out['habilidades'] = df.to_dict('records')
    except Exception as e:
        _warn_degradacao("habilidades", e)
    return out or None


def _cronograma_hint():
    """Fallback legado: 1ª linha numerada de '## Próximos passos' do ESTADO (frágil)."""
    try:
        with open(os.path.join(ROOT, "ESTADO.md"), encoding="utf-8") as fh:
            txt = fh.read()
    except Exception:
        return None
    m = re.search(r'##\s*Pr[óo]ximos passos(.*?)(?:\n##\s|\Z)', txt, re.S)
    if not m:
        return None
    lm = re.search(r'^\s*\d+\.\s*(.+)$', m.group(1), re.M)
    return lm.group(1).strip() if lm else None


def _dias_desde(iso, hoje):
    try:
        return (hoje - date.fromisoformat(str(iso)[:10])).days
    except Exception:
        return None


def reconcile_planilha(hoje=None, con=None):
    """W1 do reconcile-contract deixa de ser manual: REPORTA planilha x db (B3/F35).

    Read-only e nunca bloqueante. Compara o snapshot gravado por
    `importar_sessoes.py --snapshot` com `sessoes_bulk` e devolve um dos OITO
    estados nomeados. Regras que vieram das duas unicas reconciliacoes que o
    projeto teve (s075 e s110, ambas script one-shot):

    - **total batendo nao e alinhado.** Na s110, 3 dos 4 achados eram mislabel
      de area (`GO`, `Clinica Medica`) e o relabeling NAO mudou o total. Por
      isso `alinhado` exige detalhe por area; sem ele o estado e
      `sem_detalhe_area`, que diz o que nao foi verificado.
    - **as duas idades sao perguntas diferentes.** `ultimo_lancamento` responde
      "a planilha ainda e alimentada?" (a idade do F35); `lido_em` responde
      "minha copia dela e velha?". Colapsar as duas perde a primeira.
    - **db > planilha com a planilha parada nao e drift**, e planilha atrasada;
      **planilha > db e `import_pendente`** -- o caso dos 76q da s110, achado
      pelo operador, nao pelo sistema.
    """
    hoje = hoje or date.today()
    base = {"estado": "nao_medido", "planilha_total": None, "db_total": None, "delta": None,
            "ultimo_lancamento": None, "idade_planilha_dias": None, "lido_em": None,
            "idade_leitura_dias": None, "db_ultimo_registro": None, "areas_divergentes": [],
            "detalhe_por_area": False, "declarado_em": None, "motivo_abandono": None,
            "degradou": False,
            "acao": "python tools/importar_sessoes.py --snapshot --total N "
                    "--por-area @abas.json --ultimo-lancamento AAAA-MM-DD"}
    proprio = con is None
    try:
        import importar_sessoes as imp
        snap = imp.ler_snapshot()
        con = con or db.get_connection()
        linha = con.execute("SELECT COALESCE(SUM(questoes_feitas),0), MAX(data_sessao) "
                            "FROM sessoes_bulk").fetchone()
        base["db_total"], base["db_ultimo_registro"] = linha[0], linha[1]
        db_por_area = {r[0]: r[1] for r in con.execute(
            "SELECT area, SUM(questoes_feitas) FROM sessoes_bulk GROUP BY area")}
    except Exception as e:                      # leitor quebrado NUNCA derruba o boot (DoD 4)
        _warn_degradacao("reconcile_planilha", e)
        base["degradou"] = True
        return base
    finally:
        if proprio and con is not None:
            try:
                con.close()
            except Exception:
                pass

    if not snap:
        return base

    base["lido_em"] = (snap.get("lido_em") or "")[:10] or None
    base["idade_leitura_dias"] = _dias_desde(base["lido_em"], hoje)
    base["ultimo_lancamento"] = snap.get("ultimo_lancamento")
    base["idade_planilha_dias"] = _dias_desde(base["ultimo_lancamento"], hoje)
    base["planilha_total"] = snap.get("total")
    base["declarado_em"] = snap.get("declarado_em")
    base["motivo_abandono"] = snap.get("motivo_abandono")
    if base["planilha_total"] is not None:
        base["delta"] = base["db_total"] - base["planilha_total"]

    if not snap.get("fonte_viva", True):
        base["estado"] = "abandonada"
        base["acao"] = None
        return base
    if base["planilha_total"] is None:
        return base                              # declaracao sem numero -> segue nao_medido

    por_area = snap.get("por_area") or None
    base["detalhe_por_area"] = bool(por_area)
    if por_area:
        for area in sorted(set(por_area) | set(db_por_area)):
            p, d = por_area.get(area), db_por_area.get(area)
            if (p or 0) != (d or 0):
                base["areas_divergentes"].append(
                    {"area": area, "planilha": p, "db": d, "delta": (d or 0) - (p or 0)})
        base["areas_divergentes"].sort(key=lambda a: abs(a["delta"]), reverse=True)

    delta = base["delta"]
    if delta == 0:
        if base["areas_divergentes"]:
            base["estado"] = "divergente_por_area"
        elif por_area:
            base["estado"] = "alinhado"
            base["acao"] = None
        else:
            base["estado"] = "sem_detalhe_area"
    elif delta < 0:
        base["estado"] = "import_pendente"
    elif (base["ultimo_lancamento"] and base["db_ultimo_registro"]
          and base["ultimo_lancamento"] < base["db_ultimo_registro"][:10]):
        base["estado"] = "planilha_atrasada"
    else:
        base["estado"] = "divergente"
    return base


def render_planilha(r):
    """Uma linha, SEMPRE (DoD 1) -- inclusive `NAO MEDIDO`. Ausencia de medicao e
    um estado reportado, nao silencio."""
    e = r["estado"]
    if e == "nao_medido":
        extra = " (leitor degradou -- ver stderr)" if r.get("degradou") else ""
        return (f"- 📋 **Planilha x db (W1/F35):** ⚠️ **NAO MEDIDO**{extra} — nenhum snapshot da "
                f"planilha registrado; db tem {r.get('db_total') if r.get('db_total') is not None else '?'}q. "
                f"Registrar ao ler o Drive: `{r['acao']}`")
    idade = (f"planilha parada ha **{r['idade_planilha_dias']}d** ({r['ultimo_lancamento']})"
             if r["idade_planilha_dias"] is not None else "idade da planilha desconhecida")
    leitura = (f" · copia lida ha {r['idade_leitura_dias']}d"
               if r["idade_leitura_dias"] else "")
    if e == "abandonada":
        quando = r["declarado_em"] or "?"
        return (f"- 📋 **Planilha x db (W1/F35):** comparacao **suspensa** — planilha declarada "
                f"fora de uso em {quando} ({r['motivo_abandono'] or 'sem motivo'}); ultimo delta "
                f"medido {r['delta'] if r['delta'] is not None else '—'}")
    cab = (f"- 📋 **Planilha x db (W1/F35):** {r['planilha_total']} x {r['db_total']} "
           f"· delta **{r['delta']:+d}** · {idade}{leitura}")
    rotulos = {
        "alinhado": "✅ alinhado (total e todas as abas)",
        "sem_detalhe_area": "⚠️ total bate, mas o snapshot veio **sem detalhe por area** — "
                            "mislabel de area NAO foi verificado (s110: 3 de 4 achados eram isso)",
        "divergente_por_area": "🔴 total bate e as **abas nao** — assinatura de mislabel de area (F89)",
        "import_pendente": "🔴 planilha **a frente** do db: volume lancado e nunca importado "
                           "(`--rows-file`)",
        "planilha_atrasada": "planilha **atrasada** em relacao ao db — delta explicado pela idade, "
                             "nao por import perdido",
        "divergente": "🔴 **divergente** sem explicacao pela idade",
    }
    linhas = [cab, f"    • {rotulos.get(e, e)}"]
    for a in r["areas_divergentes"][:5]:
        linhas.append(f"    • {a['area']}: planilha {a['planilha'] if a['planilha'] is not None else '—'}"
                      f" x db {a['db'] if a['db'] is not None else '—'} ({a['delta']:+d})")
    resto = len(r["areas_divergentes"]) - 5
    if resto > 0:
        linhas.append(f"    • ... +{resto} area(s) divergente(s)")
    return "\n".join(linhas)


#: Quantas tarefas pendentes o boot lista por vez (DoD 1 da Parte 4: 3-5).
PROXIMAS_TAREFAS = 5

#: Primeira semana da FASE 2 do plano (`plano_tarefas.semana_plano`). A fronteira
#: nao e digitada duas vezes: por construcao ela e `plano.semana_fase2(21)` -- a
#: Fase 2 comeca no extensivo S21 -- e `tools/test_plano_dia.py` trava as duas
#: contra divergencia silenciosa. Fase 1 = semanas 1-7 (16/09 -> 01/11, UERJ).
PRIMEIRA_SEMANA_FASE2 = 8


def _fase_do_plano(semana):
    """Semana do plano -> fase (1 | 2). `None` quando a semana e desconhecida."""
    if semana is None:
        return None
    try:
        return 1 if int(semana) < PRIMEIRA_SEMANA_FASE2 else 2
    except (TypeError, ValueError):
        return None


def _q_prevista(linha):
    """`q_previstas` como inteiro tolerante (a coluna e REAL e aceita NULL)."""
    try:
        return int(round(float(linha.get("q_previstas") or 0)))
    except (TypeError, ValueError):
        return 0


def _plano_pendencia():
    """Pendência da revisão de status por área (`db.plano_pendencia_revisao`, Parte 3).

    Devolve SEMPRE uma lista -- vazia quando a passada zerou, quando a tabela está
    vazia e quando o leitor falha. O boot silencia nos três casos: linha de
    pendência com tabela vazia seria falso-positivo, o defeito que os irmãos
    F1/POSICAO/B1 já pagaram.
    """
    try:
        return db.plano_pendencia_revisao() or []
    except Exception as e:
        _warn_degradacao("plano_pendencia_revisao", e)
        return []


def _calendario_trilha():
    """Calendario da Fase 1 (`plano.calendario_trilha`, s189). Falha -> `{}` + WARN: sem
    calendario a cota do dia SOME da tela, nunca sai inventada (regra F1/POSICAO/B1)."""
    try:
        import plano
        return plano.calendario_trilha()
    except Exception as e:
        _warn_degradacao("calendario_trilha", e)
        return {}


def cota_do_dia(pendentes, calendario, hoje):
    """F123b (s189): cota de questoes do dia = q pendentes das semanas do plano ATE a semana
    de CALENDARIO corrente / dias que faltam nela, hoje incluso. Divisao, nao scheduler. PURA.

    - semana de calendario = a primeira cujo `fim` >= hoje; na vespera dela os dias contam a
      partir do `inicio` (`comecou=False`);
    - atraso entra: pendente de semana ANTERIOR soma e sai declarado em `q_atrasadas`. Pela
      semana do PLANO (menor com pendencia), um atraso de uma semana daria divisor zero --
      por isso a POSICAO continua sendo a do plano e a COTA e a do calendario;
    - semana do plano depois da de calendario (Fase 2) e linha sem semana (reserva) nunca
      entram;
    - sem calendario, ou depois do fim dele -> `None`: a linha some, nunca numero inventado.
    """
    if not calendario:
        return None
    futuras = [s for s in sorted(calendario) if calendario[s][1] >= hoje]
    if not futuras:
        return None
    semana = futuras[0]
    inicio, fim = calendario[semana]
    dias = (fim - max(hoje, inicio)).days + 1
    q_semana = q_atrasadas = 0
    for linha in pendentes:
        if linha.get("status", "pendente") != "pendente":
            continue
        try:
            s = int(linha.get("semana_plano"))
        except (TypeError, ValueError):
            continue                              # reserva: fora da fila, fora da cota
        if s == semana:
            q_semana += _q_prevista(linha)
        elif s < semana:
            q_atrasadas += _q_prevista(linha)
    q = q_semana + q_atrasadas
    return {"semana": semana, "inicio": inicio.isoformat(), "fim": fim.isoformat(),
            "dias": dias, "q_restantes": q, "q_atrasadas": q_atrasadas,
            "cota": math.ceil(q / dias) if q else 0, "comecou": hoje >= inicio}


def _cronograma_hoje(total_q, hoje, calendario=None):
    """Bloco de cronograma do Plano do Dia, derivado de `plano_tarefas` (o SSOT).

    Read-only. Semana corrente = **menor `semana_plano` com pendencia**, nunca a
    data: estar atrasado vira "a semana 3 ainda tem 4 tarefas", que e informacao
    de gestao (mesmo espirito do `cronograma-contract`: plano nao e
    verdade-de-estado, e por isso a POSICAO nao sai do calendario).

    s189 (F123): o ritmo e da FASE 1 -- numerador = pendentes das semanas 1-7, divisor =
    dias ate o alvo declarado; a Fase 2 e a reserva ficam fora da conta (e declaradas em
    `fora_da_fase1_q`). A cota do dia e a unica leitura de calendario (`cota_do_dia`).
    `calendario=None` le o da trilha; os testes injetam o seu.

    Tabela ausente ou vazia -> `None` (degradacao graciosa: o plano do dia sai sem
    o bloco, jamais com um bloco inventado -- regra dos irmaos F1/POSICAO/B1).
    """
    try:
        linhas = db.plano_listar()
    except Exception as e:
        _warn_degradacao("plano_tarefas", e)
        return None
    if not linhas:
        return None      # plano nao semeado: silencio, nunca bloco fabricado
    pendentes = [l for l in linhas if l.get("status") == "pendente"]
    semanas = sorted({l["semana_plano"] for l in pendentes
                      if l.get("semana_plano") is not None})
    semana = semanas[0] if semanas else None
    da_semana = [l for l in linhas if l.get("semana_plano") == semana] if semana else []
    vivas = [l for l in da_semana if l.get("status") != "cortada"]

    proximas = [{
        "id": l.get("id"), "fonte": l.get("fonte"), "area": l.get("area"),
        "tema": l.get("tema"), "tipo": l.get("tipo"), "tipo_norm": l.get("tipo_norm"),
        "q_previstas": _q_prevista(l), "url_lista": l.get("url_lista"),
        "semana_plano": l.get("semana_plano"),
    } for l in pendentes[:PROXIMAS_TAREFAS]]

    # s189 (F123a): numerador e denominador da MESMA fase. Ate aqui `restante` somava TODAS
    # as pendentes (a Fase 2 vai ate set/2027) e dividia pelos dias da Fase 1: 273 q/dia.
    restante = sum(_q_prevista(l) for l in pendentes
                   if _fase_do_plano(l.get("semana_plano")) == 1)
    # s159/s174: o divisor do ritmo continua sendo FIM_CONTEUDO_ALVO -- data-alvo
    # DECLARADA de planejamento (performance.py), auditavel, nunca um countdown de
    # display. A fronteira da s126 segue valendo aqui dentro.
    try:
        dias_grade = (FIM_CONTEUDO_ALVO - hoje).days
    except (TypeError, AttributeError):
        dias_grade = None
    if dias_grade is not None and dias_grade < 1:
        dias_grade = None     # alvo vencido: sem divisor (era max(dias, 1) -- numero inventado)
    if calendario is None:
        calendario = _calendario_trilha()

    return {
        "semana": semana,
        "fase": _fase_do_plano(semana),
        "tarefas_semana": len(vivas),
        "feitas_semana": sum(1 for l in vivas if l.get("status") == "feita"),
        "pendentes_semana": sum(1 for l in vivas if l.get("status") == "pendente"),
        "previstas": sum(_q_prevista(l) for l in vivas),
        "sem_semana": sum(1 for l in pendentes if l.get("semana_plano") is None),
        "proximas": proximas,
        "temas": [t["tema"] for t in proximas if t.get("tema")][:3],
        "pendentes_total": len(pendentes),
        "dias_grade": dias_grade,
        "fim_conteudo_alvo": FIM_CONTEUDO_ALVO.isoformat(),
        "restante_q": restante,
        "fora_da_fase1_q": sum(_q_prevista(l) for l in pendentes) - restante,
        "ritmo_cronograma": round(restante / dias_grade, 1) if dias_grade else None,
        "cota": cota_do_dia(pendentes, calendario, hoje),
        "ritmo_meta": round(max(0, META_CICLO - total_q) / DIAS_ATE_CICLO(hoje), 1)
                      if DIAS_ATE_CICLO(hoje) > 0 else None,
    }


# ---------------------------------------------------------------------------
# Revisão Calibrada — inferência da nota de dificuldade (read-only).
# infer_nota() é determinística e só lê sinais FRIOS independentes da própria
# saída (anti-circularidade, PRD §7.6). day_plan NÃO escreve estado: a
# persistência da nota é feita na abertura de task (skill /revisar), não aqui.
# Norma: core/contracts/revisao-calibrada-contract.md.
# ---------------------------------------------------------------------------

DEGRAU_PARAGRAFOS = {"D10": (7, 9), "D8": (5, 6), "D5": (3, 4), "D2": (1, 2)}


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _degrau_de(nota):
    """Mapa nota→degrau de registro (PRD §4.6)."""
    if nota >= 9:
        return "D10"
    if nota >= 7:
        return "D8"
    if nota >= 4:
        return "D5"
    return "D2"


def _nota_fresca(at, dias=7):
    """True se o carimbo `dificuldade_at` (isoformat, espaço como separador) tem <= `dias`.
    Ilegível/ausente = False (nota velha re-infere — F47). Puro e testável."""
    if not at:
        return False
    try:
        from datetime import datetime as _dt
        carimbo = _dt.fromisoformat(str(at))
        return (_dt.now() - carimbo).days <= dias
    except Exception:
        return False


def _divergencia(nota_usuario, nota_inferida):
    """Divergência auto-nota × inferência (PRD §4.4). None se |Δ|<3 ou sem nota do usuário."""
    if nota_usuario is None or abs(nota_usuario - nota_inferida) < 3:
        return None
    return {"usuario": nota_usuario, "inferida": nota_inferida,
            "delta": nota_usuario - nota_inferida}


def infer_nota(sinais):
    """Nota de dificuldade inferida (1-10). Determinística — PRD §7.3.

    `sinais`: dict com acerto_hist (None se 0q), acerto_bloco (None se inexistente),
    score_dorm (float), leu_tema (bool), prevalencia ('alta'|'media'|'baixa').
    Só sinais FRIOS independentes da saída (§7.6): nunca a profundidade do
    ensino nem o acerto "morno" medido logo depois dele (⚰️ dizia "pós-PREPARAR",
    sub-modo revogado na s170 -- o mecanismo descrito segue igual).
    """
    acerto_hist = sinais.get("acerto_hist")
    acerto_bloco = sinais.get("acerto_bloco")
    score_dorm = sinais.get("score_dorm")
    leu_tema = bool(sinais.get("leu_tema"))
    prevalencia = sinais.get("prevalencia") or "media"

    # eixo 1 — performance histórica define a BASE
    if acerto_hist is None and not leu_tema:
        base = 9                      # estreia pura → onboarding
    elif acerto_hist is None:
        base = 6                      # leu, sem volume registrado
    elif acerto_hist < 50:
        base = 8
    elif acerto_hist < 65:
        base = 7
    elif acerto_hist < 80:
        base = 5
    else:
        base = 3                      # >= 80%

    # eixo 2 — frieza (dormência) empurra p/ cima; quente puxa p/ baixo.
    # score_dorm None = sinal AUSENTE (≠ quente) → eixo neutro.
    if score_dorm is not None:
        if score_dorm >= 40:
            base += 2
        elif score_dorm >= 25:
            base += 1
        elif score_dorm < 7:
            base -= 1

    # eixo 3 — último bloco fraco confirma dificuldade VIVA
    if acerto_bloco is not None and acerto_bloco < 60:
        base += 1

    # eixo 4 — prevalência ENAMED = piso de banca, não teto (neutro hoje §7.7)
    if prevalencia == "baixa":
        base -= 1
    nota = _clamp(base, 1, 10)
    if prevalencia == "alta":
        nota = max(nota, 4)
    return nota


def montar_sinais(area, tema):
    """Coleta os sinais frios de um tema do db/radar (read-only). PRD §7.3/§7.6."""
    stats = db.get_tema_stats(area, tema)
    acerto_hist = stats["percentual"] if (stats and stats.get("questoes")) else None
    acerto_bloco = db.get_ultimo_bloco_tema(area, tema)

    score_dorm = None       # None = sem sinal de dormência (≠ quente)
    try:
        import review_radar
        for r in review_radar.coletar(area=area):
            if r.get("tema") == tema:
                score_dorm = r.get("score")
                break
    except Exception:
        pass

    last = db.get_theme_last_review(area=area, tema=tema)
    leu = bool(last and last.get("last_review"))
    if not leu:
        try:
            gtc = importlib.import_module("app.engine.get_topic_context")
            leu = gtc._find_resumo(tema) is not None
        except Exception:
            pass

    return {
        "acerto_hist": acerto_hist,
        "acerto_bloco": acerto_bloco,
        "score_dorm": score_dorm,
        "leu_tema": leu,
        "prevalencia": "media",       # §7.7: grade.json ainda não tem prevalencia_enamed
    }


def _proposito(area, tema):
    """exercicios (amplo) vs flashcards (direcionado). Cluster vencido → flashcards. PRD §5.2/§7.4."""
    try:
        q = db.get_cards_by_bucket(area=area, tema=tema)
        vencidos = len(q.get("atrasados", [])) + len(q.get("hoje", []))
    except Exception:
        vencidos = 0
    return ("flashcards" if vencidos >= 3 else "exercicios"), vencidos


def _norm_tema(s):
    """Normaliza um tema p/ igualdade: casefold + trim + colapso de espaços."""
    return " ".join((s or "").casefold().split())


def _material_do_tema(tema):
    """material_indicado da grade por igualdade normalizada (C1). 'resumo' se ausente.

    Igualdade normalizada (não substring): substring com string vazia era a raiz do C1
    (tema vazio casava qualquer tema; o `break` interno deixava semanas seguintes
    sobrescreverem). Ignora temas vazios e faz early-return no 1º match — determinístico.
    """
    try:
        import cronograma as cr
        grade = cr.load_grade()
    except Exception:
        return "resumo"
    alvo = _norm_tema(tema)
    if not alvo:
        return "resumo"
    for s in grade["semanas"]:
        for t in s["tasks"]:
            tt = t.get("tema", "")
            if tt and _norm_tema(tt) == alvo:
                return t.get("material_indicado", "resumo")
    return "resumo"


def _material_efetivo(tema, material):
    """F30: se o cronograma diz 'resumo' mas o .md nao existe, rebaixa para
    'extensivo' -- nao prometer "so ler o resumo" quando ele nao existe (tema-zero
    mascarado). Read-only; reusa o resolver `_find_resumo` (indexa stem desde s096).
    Qualquer falha na resolucao -> mantem o rotulo original (nunca quebra o boot)."""
    if material != "resumo":
        return material
    try:
        gtc = importlib.import_module("app.engine.get_topic_context")
        if gtc._find_resumo(tema) is None:
            return "extensivo"
    except Exception:
        pass
    return material


def difficulty_report(area, tema):
    """Proposta read-only de nota/degrau/proposito p/ a abertura de task (PRD R3/R4).

    Regra D10 (extensivo): material extensivo ou inferência sem nota explícita → degrau D10 + dever de Deep-Researchness; a nota explícita do usuário (fonte=usuario) sempre vence (precedência input > pergunta > inferência).
    """
    sinais = montar_sinais(area, tema)
    nota_inferida = infer_nota(sinais)
    d = db.get_dificuldade(area, tema)
    nota_reg = d["nota"] if (d and d.get("nota") is not None) else None
    fonte = d["fonte"] if d else None
    # F47 (descolar part-3): a FONTE decide — Cláusulas 2/7 do revisao-calibrada-contract,
    # que estavam sem implementação (QUALQUER nota persistida virava "do usuário" e a msg
    # de divergência atribuía ao usuário nota que ele não deu; 12/21 temas afetados).
    # Precedência: 'usuario' soberana > nota persistida FRESCA (aula/agente_inferida, 7d)
    # > inferência corrente (nota velha não-soberana re-infere; a fonte fica honesta).
    nota_usuario = nota_reg if fonte == "usuario" else None
    if nota_usuario is not None:
        nota_efetiva, fonte_efetiva = nota_usuario, "usuario"
    elif nota_reg is not None and _nota_fresca(d.get("at")):
        nota_efetiva, fonte_efetiva = nota_reg, (fonte or "persistida")
    else:
        nota_efetiva, fonte_efetiva = nota_inferida, "inferencia_corrente"

    mat = _material_efetivo(tema, _material_do_tema(tema))   # F30: rebaixa se o .md nao existe

    # G5: nota explícita do usuário NUNCA é sobrescrita. O floor extensivo só levanta nota
    # que veio da INFERÊNCIA (calibração deliberada persistida e fresca também fica de pé —
    # Cláusula 10: 'aula' não é sobrescrita por heurística).
    deep_research = False
    if mat == "extensivo" and fonte_efetiva == "inferencia_corrente":
        nota_efetiva = max(nota_inferida, 9)
        deep_research = True

    degrau = _degrau_de(nota_efetiva)
    proposito, vencidos = _proposito(area, tema)
    largura = ("amplo (escopo do cronograma)" if proposito == "exercicios"
               else "direcionado (cluster vencido)")
    # ⚰️ F97 (s177): esta string dizia "..., PREPARAR {descomprimido}+mecanismo,
    # {largura}; depois DRENAR" -- prescrevendo, no plano que o agente le no 1o
    # turno, um sub-modo REVOGADO na s170. O gate CONTRATO_REVOGADO nao a via
    # porque so varria markdown. A ordem do contrato v1.3 e a inversa: DRENAR
    # primeiro, e o ensino acontece so na Revisao Direcionada de FECHAMENTO.
    passo = (f"Revisar {tema} como dif-{nota_efetiva} ({degrau}) [Material: {mat}]: "
             f"DRENAR a fila e fechar com Revisao Direcionada "
             f"{'descomprimida' if nota_efetiva >= 7 else 'comprimida'}+mecanismo, "
             f"{largura}.")
    return {
        "area": area, "tema": tema,
        "nota_usuario": nota_usuario, "nota_fonte": fonte,
        "fonte_efetiva": fonte_efetiva,
        "nota_inferida": nota_inferida, "nota_efetiva": nota_efetiva,
        "degrau": degrau, "paragrafos": list(DEGRAU_PARAGRAFOS[degrau]),
        "divergencia": _divergencia(nota_usuario, nota_inferida),
        "proposito": proposito, "cards_vencidos": vencidos,
        "material_indicado": mat,
        "deep_research": deep_research,
        "sinais": sinais,
        "sugestao_passo": passo,
    }


def recomendar_dia(sinais, tempo_h=None, energia=None):
    """Recomendador do dia (PRD orquestracao part-2) — função de decisão
    DETERMINÍSTICA e PURA: dict de sinais derivados -> estrutura de blocos.
    Nenhum acesso a db/arquivo aqui (testável por fixtures). Regras R1-R5 e
    parâmetros nomeados: core/contracts/orquestracao-contract.md.
    """
    defaults_assumidos = tempo_h is None and energia is None
    tempo_h = TEMPO_DEFAULT_H if tempo_h is None else float(tempo_h)
    energia = (energia or ENERGIA_DEFAULT).lower()
    fator = FATOR_ENERGIA.get(energia, FATOR_ENERGIA[ENERGIA_DEFAULT])
    capacidade_q = int(tempo_h * QUESTOES_POR_HORA * fator)

    # s126: o ritmo necessário da GRADE mede-se contra o fim da grade (~25/10), não contra a
    # data do ENAMED -- a grade fecha ~6 semanas depois da prova. Usar dias_enamed aqui era o
    # que inflava o "necessário" para ~116q/dia. Fallback p/ dias_enamed se o sinal faltar.
    dias = sinais.get("dias_grade") or sinais.get("dias_enamed") or 0
    restante = sinais.get("restante_grade_q") or 0
    ritmo_real = sinais.get("ritmo_real") or 0.0
    ritmo_nec = round(restante / dias, 1) if dias > 0 else None
    if restante <= 0:
        dias_p_fechar, folga_dias = 0, dias
    elif ritmo_real > 0:
        dias_p_fechar = math.ceil(restante / ritmo_real)
        folga_dias = dias - dias_p_fechar
    else:
        dias_p_fechar, folga_dias = None, None  # sem ritmo medido na janela
    projecao = {"ritmo_real": ritmo_real, "ritmo_necessario": ritmo_nec,
                "dias_para_fechar": dias_p_fechar, "folga_dias": folga_dias,
                "janela_dias": JANELA_RITMO_DIAS}

    blocos, just = [], []
    contexto = {"tempo_h": tempo_h, "energia": energia, "capacidade_q": capacidade_q}
    frescos = sinais.get("frescos_tema_alvo") or []
    tema_alvo = sinais.get("tema_alvo")
    vencidos = sinais.get("vencidos") or 0
    teto = sinais.get("teto_efetivo") or TETO_BASE

    # R1 — anti-reincidência primeiro: cards de erro frescos do tema-alvo
    if frescos:
        blocos.append({"tipo": "mini-drill", "qtd": len(frescos), "alvo": tema_alvo,
                       "motivo": "card(s) de erro frescos (<%dh) no tema-alvo"
                                 % FRESCOS_JANELA_HORAS})
        just.append("reincidência: %d card(s) frescos de %s" % (len(frescos), tema_alvo))

    # R2 — descanso: energia baixa + folga projetada acima do limiar
    if energia == "baixa" and folga_dias is not None and folga_dias >= LIMIAR_FOLGA_DESCANSO_DIAS:
        blocos.append({"tipo": "descanso", "qtd": 0, "alvo": None,
                       "motivo": "energia baixa + folga projetada de %dd (limiar %dd)"
                                 % (folga_dias, LIMIAR_FOLGA_DESCANSO_DIAS)})
        if vencidos > 0:
            blocos.append({"tipo": "fsrs", "qtd": min(teto, FSRS_LEVE_CAP, vencidos),
                           "alvo": "vencidos", "motivo": "revisão leve (dia de descanso)"})
        just.append("descanso permitido: folga %dd >= %dd e energia baixa — sem tema novo hoje"
                    % (folga_dias, LIMIAR_FOLGA_DESCANSO_DIAS))
        just.append("ritmo real %.1fq/dia vs necessário %sq/dia (janela %dd)"
                    % (ritmo_real, ritmo_nec, JANELA_RITMO_DIAS))
        return {"blocos": blocos, "justificativa": just, "projecao": projecao,
                "defaults_assumidos": defaults_assumidos, "contexto": contexto}

    # R3 — simulado periódico (usa a área 'Simulado' já existente no registro)
    semana = sinais.get("semana_conteudo")
    if semana and semana % PERIODO_SIMULADO_SEMANAS == 0:
        blocos.append({"tipo": "simulado", "qtd": 1, "alvo": "Simulado",
                       "motivo": "slot periódico (semana S%d, a cada %d semanas)"
                                 % (semana, PERIODO_SIMULADO_SEMANAS)})
        just.append("semana S%d é múltipla de %d: slot de simulado"
                    % (semana, PERIODO_SIMULADO_SEMANAS))

    # R4 — questões da grade: alvo = min(capacidade do dia, ritmo necessário);
    # atrasado (folga negativa) => capacidade máxima do dia
    alvo_q = capacidade_q if ritmo_nec is None else min(capacidade_q,
                                                        max(int(math.ceil(ritmo_nec)), 1))
    if folga_dias is not None and folga_dias < 0:
        alvo_q = capacidade_q
        just.append("grade atrasada (%dd de déficit projetado): capacidade máxima em questões"
                    % -folga_dias)
    if alvo_q > 0 and restante > 0:
        blocos.append({"tipo": "questoes", "qtd": alvo_q,
                       "alvo": tema_alvo or "próximo tema da semana",
                       "motivo": "necessário %sq/dia; capacidade ~%dq (%.1fh x %d q/h x %.2f)"
                                 % (ritmo_nec, capacidade_q, tempo_h, QUESTOES_POR_HORA, fator)})
    just.append("ritmo real %.1fq/dia vs necessário %sq/dia (janela %dd)"
                % (ritmo_real, ritmo_nec, JANELA_RITMO_DIAS))

    # R5 — FSRS até o teto efetivo (F4 governa a dívida)
    fsrs_qtd = min(teto, vencidos + 15)
    if fsrs_qtd > 0:
        blocos.append({"tipo": "fsrs", "qtd": fsrs_qtd, "alvo": "fila do dia",
                       "motivo": "teto efetivo %d (dívida: %d vencidos)" % (teto, vencidos)})
    just.append("dívida FSRS: %d vencidos; teto %d; pool %d nunca introduzidos"
                % (vencidos, teto, sinais.get("backlog_novos") or 0))
    if sinais.get("lag"):
        just.append("posição: conteúdo S%s (%s sem atrás do calendário)"
                    % (semana, sinais["lag"]))

    return {"blocos": blocos, "justificativa": just, "projecao": projecao,
            "defaults_assumidos": defaults_assumidos, "contexto": contexto}


def build(tempo_h=None, energia=None):
    con = db.get_connection()
    hoje = date.today()
    # F88 (s174): a conta acumulado/meta/faltam/ritmo e UMA, em performance.volume_vs_marco
    # (o cronograma --gap chama a mesma). Nada de marco literal nem get_totais soltos aqui.
    vm = volume_vs_marco(con, hoje)
    q_mes = get_questoes_do_mes(con, hoje.strftime("%Y-%m"))
    q_hoje = con.cursor().execute(
        "SELECT COALESCE(SUM(questoes_feitas),0) FROM sessoes_bulk "
        "WHERE data_sessao = ?",  # s126: simulado CONTA no volume (reverte s099)
        (hoje.isoformat(),)).fetchone()[0]
    fsrs = _fsrs_counts(con)
    # F71 rider (s174): overflow do blackout de prova e ESTADO do banco, nao so stderr --
    # o boot o mostra com card_id e due (leitor read-only db.overflow_blackout).
    fsrs["overflow_blackout"] = db.overflow_blackout(con.cursor())
    # F64 (c): o teto sem o SALDO obriga o agente a derivar a conta a mao -- e errar.
    # `consumo_hoje` = revisoes JA gravadas hoje (fsrs_revlog), a mesma fonte do
    # `realizado_do_dia` da aderencia.
    try:
        consumo_hoje = realizado_do_dia(con, hoje.isoformat())["cards"]
    except Exception as e:
        _warn_degradacao("consumo_hoje", e)
        consumo_hoje = None
    con.close()

    dormant = dr.pick()
    vencidos = vencidos_de(fsrs)      # F64: UMA definicao, usada pelo gatilho E pelo texto
    if (q_hoje or 0) == 0:
        passo = "Quebrar o zero do dia: bloco de questões da área prioritária (refresh pré-bloco antes)."
    elif vencidos > 0:
        passo = f"Revisar {vencidos} cards vencidos (/revisar) + seguir com questões."
    else:
        passo = "Seguir o cronograma: próximo tema previsto + questões."

    cron = _cronograma_hoje(vm["total"], hoje)

    # Sinais do recomendador (part-2) — todos derivados; falha de um sinal não
    # derruba o plano (degradação graciosa, mesmo espírito do cronograma).
    temas_semana = (cron or {}).get("temas") or []
    tema_alvo = temas_semana[0] if temas_semana else None
    try:
        ritmo_real = db.get_ritmo_real(JANELA_RITMO_DIAS)
    except Exception:
        ritmo_real = 0.0
    try:
        frescos = (db.get_fresh_error_cards(tema=tema_alvo, janela_horas=FRESCOS_JANELA_HORAS)
                   if tema_alvo else [])
    except Exception:
        frescos = []
    sinais = {
        # Parte 4: `dias_enamed` saiu (era lido do cronograma.py e o fallback `dias`
        # sequer existia neste escopo -- NameError latente quando `cron` era None).
        # O divisor do recomendador continua sendo `dias_grade`, que agora nasce do
        # alvo declarado FIM_CONTEUDO_ALVO, nunca de uma data de prova.
        # s189 (F123a): os DOIS sinais sao da Fase 1 -- o 273 q/dia do boot tambem
        # governava o R4 ("grade atrasada, 235d de deficit"). Alvo vencido chega como
        # None e o R4 cai na capacidade, em vez de dividir por um 1 inventado.
        "dias_grade": cron.get("dias_grade") if cron else 1,
        "restante_grade_q": (cron or {}).get("restante_q") or 0,
        "ritmo_real": ritmo_real,
        "vencidos": vencidos,
        "teto_efetivo": _teto_efetivo(vencidos),
        "backlog_novos": fsrs["backlog_novos"],
        # R3 (simulado periodico) le esta chave. O NOME e do `orquestracao-contract`
        # (§R3); a FONTE mudou na Parte 4 -- era a semana de calendario/
        # `preparacao_estado`, agora e a semana do PLANO (`plano_tarefas`).
        "semana_conteudo": (cron or {}).get("semana"),
        "tema_alvo": tema_alvo,
        "frescos_tema_alvo": frescos,
    }

    return {
        "data": hoje.isoformat(),
        "provas": countdown_provas(hoje),   # multi-prova: display, nao alimenta ritmo
        "dormant": dormant,
        "volume": {
            "total": vm["total"], "acertos": vm["acertos"],
            "hoje": q_hoje or 0, "mes": q_mes or 0,
            "alvo_enamed": vm["meta"], "faltam": vm["faltam"],
            "dias_ate_marco": vm["dias"], "ritmo_alvo": vm["ritmo_alvo"],
            "marco": vm["marco"],   # s126: rótulo do marco-alvo via volume_vs_marco (F88)
        },
        "fsrs": fsrs,
        "divida": {
            "atrasados": fsrs["atrasados"],
            "vencidos": vencidos,                      # F64: o contador do gatilho
            "regime_divida": vencidos > TETO_BASE,
            "teto_base": TETO_BASE,
            "teto_efetivo": _teto_efetivo(vencidos),
            "consumo_hoje": consumo_hoje,              # F64 (c): teto sem saldo obriga conta a mao
        },
        "cronograma": cron,
        # Parte 3 -> Parte 4: quanto ainda falta da passada de revisão de status por
        # área. Lista VAZIA quando zerou E quando a tabela nem existe -- o boot
        # silencia nos dois casos (nunca falso-positivo com tabela vazia).
        "plano_pendencia": _plano_pendencia(),
        "planilha": reconcile_planilha(hoje),    # W1 reporta, nunca bloqueia (B3/F35)
        "cronograma_hint": _cronograma_hint(),   # fallback se a grade não existir
        "diagnostico": _diagnostico(),           # variância/zona + habilidades (s126)
        "sugestao_passo": passo,
        "recomendacao": recomendar_dia(sinais, tempo_h=tempo_h, energia=energia),
    }


def review_plan(new_limit=10):
    """Clusters do dia derivados da fila real (F3) -- read-only.

    Mesma fonte da fila (get_cards_by_bucket, mesmo new_limit default do
    fsrs_queue): a contagem não pode divergir do que --list entrega. Mata a
    classe de erro de contagem manual observada na s108 (3x).
    """
    buckets = db.get_cards_by_bucket(new_limit=new_limit)
    clusters = {}
    # P3 part-2: bucket `erros_frescos` entra na contagem (paridade F3 com o
    # --list); para o cluster ele conta como "novos" (é card novo — só é
    # servido antes), sem criar chave nova de display.
    for nome in ("atrasados", "erros_frescos", "hoje", "novos"):
        for card in buckets.get(nome, []):
            chave = (card.get("area") or "(sem area)", card.get("tema") or "(sem tema)")
            c = clusters.setdefault(chave, {"area": chave[0], "tema": chave[1],
                                            "atrasados": 0, "hoje": 0, "novos": 0,
                                            "total": 0})
            c["novos" if nome == "erros_frescos" else nome] += 1
            c["total"] += 1

    # Sinal de frieza por cluster (F5) -- score de dormência do review_radar.
    # Fallback AUDÍVEL: radar indisponível -> frieza=None + [WARN] em stderr
    # (F60; day_plan segue read-only e resiliente, o julgamento frio/quente é
    # do contrato, não daqui -- mas a ausência do sinal deixa de ser muda).
    frieza = {}
    try:
        import review_radar
        for r in review_radar.coletar():
            frieza[(r.get("area"), r.get("tema"))] = r.get("score")
    except Exception as e:
        _warn_degradacao("frieza", e)
    for c in clusters.values():
        c["frieza"] = frieza.get((c["area"], c["tema"]))

    # F64: mesmo conceito, outra granularidade -- o cluster tambem ordena por
    # VENCIDOS, e pela mesma definicao. Soma manual aqui recriaria a divergencia
    # num lugar onde ninguem iria procura-la.
    return sorted(clusters.values(),
                  key=lambda c: (-vencidos_de(c), -c["total"], c["area"], c["tema"]))


def render_review_plan(clusters):
    if not clusters:
        return "# 📋 Plano de Revisão — fila vazia"
    total = sum(c["total"] for c in clusters)
    out = [f"# 📋 Plano de Revisão — {total} cards em {len(clusters)} cluster(s)", ""]
    for c in clusters:
        partes = [f"{c[b]} {b}" for b in ("atrasados", "hoje", "novos") if c[b]]
        frio = ""
        if c.get("frieza") is not None:
            frio = f" · frieza {c['frieza']}" + (" ❄️" if c["frieza"] >= 25 else "")
        out.append(f"- **{c['area']} · {c['tema']}** — {c['total']} card(s): "
                   f"{', '.join(partes)}{frio}")
    return "\n".join(out)


def _contar_resumos():
    """Higiene (F6): contagem derivada de resumos/**/*.md -- MESMO glob do
    audit_resumos (o numero bate com o linter). Digitar o contador a mao foi a
    raiz do drift 63x61 no ESTADO. None em falha (nunca quebra o bloco)."""
    try:
        return len(glob.glob(os.path.join(ROOT, "resumos", "**", "*.md"), recursive=True))
    except Exception:
        return None


def telemetria_fila(fsrs, divida):
    """Rotulacao canonica da fila FSRS: separa DIVIDA (revisao ja vencida) de
    POOL (cards nunca introduzidos). Ambos aparecem com due no passado no db
    (card novo nasce com due=now -- insert_questao.py), mas so a divida e atraso
    real; o pool e metrado pelo teto de introducao/dia. NAO altera nenhuma
    contagem -- so reusa os buckets de _fsrs_counts/_teto_efetivo sob nomes que
    nao mentem (encerra a leitura de 'backlog: N novos' como se fosse divida).

    divida (atrasada) = state>0 AND due<hoje   (fsrs['atrasados'])
    hoje              = state>0 AND due=hoje    (fsrs['hoje'])
    pool              = state=0                 (fsrs['backlog_novos'])
    """
    return {
        "divida": fsrs["atrasados"],
        "hoje": fsrs["hoje"],
        "pool": fsrs["backlog_novos"],
        "teto": divida["teto_efetivo"],
        "regime_divida": divida["regime_divida"],
    }


def render_handoff_block(p):
    """Bloco numerico 'Estado por frente' derivado do db (F6 -- AUDITORIA_MEDHUB).

    ASCII puro, pronto para colar no HANDOFF.md. So numeros derivados: o texto
    qualitativo (proximo tema, gaps, pendencias) continua manual no fechamento.
    """
    v, f = p["volume"], p["fsrs"]
    t = telemetria_fila(f, p["divida"])
    perf = round(v["acertos"] / v["total"] * 100, 1) if v["total"] else 0.0
    linhas = [
        f"- **Volume & Metas:** {v['total']} / {v['alvo_enamed']} (perf. ~{perf}%). "
        f"Hoje: {v['hoje']}. Ritmo do marco de volume ~{v['ritmo_alvo']}q/dia "
        f"({v['dias_ate_marco']}d p/ {v.get('marco', 'marco')}).",
        f"- **FSRS:** divida {t['divida']} atrasados + {t['hoje']} p/ hoje "
        f"-- pool {t['pool']} nunca introduzidos (entram <={t['teto']}/dia).",
    ]
    n_resumos = _contar_resumos()
    if n_resumos is not None:
        linhas.append(f"- **Conteudo:** {n_resumos} resumos em resumos/. [derivado: glob]")
    # F53 (descolar part-4): a frente 'Erros & Cards' passa a ser DERIVADA — o vocabulario
    # completo do handoff-contract sai do gerador, nao da mao.
    try:
        ec = db.contar_erros_cards()
        linhas.append(
            f"- **Erros & Cards:** {ec['erros']} erros registrados · {ec['cards_ativos']} "
            f"cards ativos · {ec['needs_qualitative']} needs_qualitative na fila · "
            f"taxonomia {ec['temas']} temas. [derivado: db]")
    except Exception:
        pass  # bloco derivado degrada em silencio aqui; o [WARN] do plano cobre a classe
    c = p.get("cronograma")
    if c and c.get("semana"):
        # s189 (F123): a cota e o ritmo da Fase 1 viajam DERIVADOS -- o "~77 q/dia" que a
        # s188 digitou a mao no HANDOFF era a terceira regua para a mesma pergunta.
        extra = ""
        cota = c.get("cota")
        if cota:
            extra += f" · cota ~{cota['cota']}q/dia ate {_dm(cota['fim'])}"
        if c.get("ritmo_cronograma") is not None:
            extra += f" · Fase 1 ~{c['ritmo_cronograma']}q/dia"
        linhas.append(
            f"- **Posicao:** plano semana {c['semana']} (fase {c.get('fase') or '?'}) "
            f"· {c.get('feitas_semana', 0)}/{c.get('tarefas_semana', 0)} tarefas da semana "
            f"feitas{extra} [derivado: plano_tarefas]")
    return "\n".join(linhas)


def _dm(iso):
    """`'2026-09-19'` -> `'19/09'` (so display)."""
    try:
        return date.fromisoformat(iso).strftime("%d/%m")
    except (TypeError, ValueError):
        return str(iso or "?")


def _linhas_ritmo_do_plano(c):
    """As reguas do PLANO no bloco de cronograma (s189, F123), cada uma dizendo o que mede:
    a cota do dia (semana de calendario da trilha) e o ritmo da Fase 1 (alvo declarado). O
    marco de volume do ciclo vai junto, com o nome e o numero reais (o rotulo antigo,
    `2o ciclo {META_CICLO // 1000}k`, arredondava 12.500 para 12k)."""
    linhas = []
    cota = c.get("cota")
    if cota:
        extra = []
        if cota["q_atrasadas"]:
            extra.append(f"inclui {cota['q_atrasadas']}q atrasadas de semana anterior")
        if not cota["comecou"]:
            extra.append(f"a semana {cota['semana']} comeca em {_dm(cota['inicio'])}")
        sufixo = ("; " + "; ".join(extra)) if extra else ""
        linhas.append(f"    • 🎯 **Cota do dia:** ~{cota['cota']}q ({cota['q_restantes']}q "
                      f"pendentes ate o fim da semana {cota['semana']}, em {cota['dias']} "
                      f"dia(s): {_dm(cota['inicio'])} -> {_dm(cota['fim'])}{sufixo})")
    faixa = f"semanas 1-{PRIMEIRA_SEMANA_FASE2 - 1}"
    alvo = c.get("fim_conteudo_alvo") or "?"
    if c.get("ritmo_cronograma") is not None:
        fase = (f"ritmo da Fase 1 ~{c['ritmo_cronograma']}q/dia ({c.get('restante_q', 0)}q "
                f"pendentes nas {faixa} ate {alvo}; Fase 2 e reserva fora da conta)")
    else:
        fase = (f"ritmo da Fase 1: sem divisor -- alvo {alvo} vencido "
                f"({c.get('restante_q', 0)}q pendentes nas {faixa})")
    if c.get("ritmo_meta") is not None:
        fase += (f" · marco de volume {MARCOS[1][0]} ({META_CICLO} ate "
                 f"{DATA_CICLO.strftime('%d/%m')}) ~{c['ritmo_meta']}q/dia")
    linhas.append(f"    • {fase}")
    return linhas


def render(p):
    d, v, f = p["dormant"], p["volume"], p["fsrs"]
    out = [f"# 🗓️ Plano do Dia — {p['data']}", ""]
    # Countdown multi-prova: cada data com o proprio rotulo (prova x fecho de grade).
    linha_provas = render_countdown(p.get("provas") or [])
    if linha_provas:
        out += [f"- ⏳ **Datas:** {linha_provas}"]
    if d.get("empty"):
        out.append("- 🌡️ **Refrescar (dormente):** nenhum tema elegível.")
    else:
        out.append(f"- 🌡️ **Refrescar (dormente):** {d['tema']} ({d['area']} · "
                   f"{d['dias_sem_revisar']}d sem rever · {d['n_cards']} cards · {d.get('perf') or '—'}%)")
    # s189: esta regua mede o MARCO DE VOLUME (performance.volume_vs_marco), nao o plano --
    # a do plano e o "ritmo da Fase 1" do bloco de cronograma. Cada uma diz o que mede.
    meta = f"de {v['alvo_enamed']} " if v.get("alvo_enamed") else ""
    out.append(f"- 📊 **Volume:** {v['total']} acum. · hoje {v['hoje']} · faltam {v['faltam']} "
               f"p/ o marco de volume {meta}({v.get('marco', 'marco')}) "
               f"em {v['dias_ate_marco']}d "
               f"→ ~{v['ritmo_alvo']}q/dia (~{round(v['ritmo_alvo'] * 7 / 6)}q em 6 dias/sem)")
    t = telemetria_fila(f, p["divida"])
    out.append(f"- 🔁 **FSRS:** dívida {t['divida']} atrasados + {t['hoje']} p/ hoje "
               f"· pool {t['pool']} nunca introduzidos (entram <={t['teto']}/dia)")
    ov = f.get("overflow_blackout") or []
    if ov:
        ids = " ".join(f"#{o['card_id']}" for o in ov[:12]) + (" ..." if len(ov) > 12 else "")
        dias_ov = sorted({o["due"] for o in ov})
        out.append(f"    • ⚠️ **Overflow de blackout (F71):** {len(ov)} card(s) presos em "
                   f"{', '.join(dias_ov)} sem vaga antes da prova -- {ids} "
                   f"(`python tools/fsrs_load.py --blackout`)")
    dv = p["divida"]
    regime = " · **REGIME DE DÍVIDA** (teto sobe até drenar)" if dv["regime_divida"] else ""
    # F64: o gatilho é `vencidos` (atrasados + hoje), e o saldo do dia sai junto do teto --
    # teto sem saldo obriga o leitor a derivar a conta a mão, que foi como a s162 errou.
    consumo = dv.get("consumo_hoje")
    saldo = (f" · **{consumo}/{dv['teto_efetivo']} usados hoje** "
             f"({max(0, dv['teto_efetivo'] - consumo)} restantes)") if consumo is not None else ""
    out.append(f"- 🎯 **Teto do dia:** {dv['teto_efetivo']} cards (base {dv['teto_base']}"
               f"{regime}) · gatilho = **{dv.get('vencidos', 0)} vencidos** "
               f"(atrasados + hoje){saldo}")
    c = p.get("cronograma")
    if c:
        # Parte 4: a fonte do "o que vem agora" é `plano_tarefas`, não o calendário
        # do PDF nem o snapshot do xlsx. Semana corrente = menor `semana_plano` com
        # pendência -- sem projeção por data (plano não é verdade-de-estado).
        if c.get("semana"):
            # s189: a cota vai TAMBEM no cabecalho -- o hook de SessionStart corta o plano em
            # `memory_boot._DAY_PLAN_MAX_LINES` linhas (eram 8; 40 desde a s190), e a linha
            # detalhada, la embaixo do bloco, pode nao chegar ao boot.
            cota = c.get("cota")
            cab_cota = (f" · 🎯 cota ~{cota['cota']}q/dia ate {_dm(cota['fim'])}"
                        if cota else "")
            out.append(f"- 🧭 **Cronograma:** plano **semana {c['semana']}** "
                       f"(fase {c.get('fase') or '?'}) · "
                       f"{c.get('feitas_semana', 0)}/{c.get('tarefas_semana', 0)} tarefas feitas "
                       f"· {c.get('previstas', 0)}q previstas na semana{cab_cota}")
        else:
            out.append(f"- 🧭 **Cronograma:** plano sem semana atribuída — "
                       f"{c.get('pendentes_total', 0)} tarefa(s) pendente(s) fora de semana "
                       f"(`python tools/plano.py --mover ID --semana N`)")
        for i, t in enumerate(c.get("proximas") or [], 1):
            qtd = f" · {t['q_previstas']}q" if t.get("q_previstas") else ""
            url = f" · {t['url_lista']}" if t.get("url_lista") else ""
            sem = (f" [S{t['semana_plano']}]"
                   if t.get("semana_plano") and t["semana_plano"] != c.get("semana") else "")
            out.append(f"    {i}. [{t.get('fonte') or '?'}]{sem} {t.get('tema') or '(sem tema)'}"
                       f" ({t.get('tipo') or '?'}{qtd}){url}")
        if c.get("sem_semana"):
            out.append(f"    • {c['sem_semana']} tarefa(s) pendente(s) SEM semana do plano "
                       f"(`python tools/plano.py --listar --status pendente`)")
        out.extend(_linhas_ritmo_do_plano(c))
    elif p.get("cronograma_hint"):
        out.append(f"- 🧭 **Cronograma:** {p['cronograma_hint'][:120]}")
    # Pendência da revisão de status por área (Parte 3). UMA linha enquanto houver
    # tarefa com origem aproximada; SILÊNCIO quando zerar -- e também quando a
    # tabela está vazia, que é o falso-positivo que os irmãos F1/POSICAO/B1 pagaram.
    pend = p.get("plano_pendencia") or []
    if pend:
        n = sum(a.get("aproximadas", 0) for a in pend)
        amostra = "; ".join(f"{a['area']} {a['aproximadas']}/{a['total']}" for a in pend[:4])
        resto = len(pend) - 4
        out.append(f"- 📋 **Status do plano por conferir:** {n} tarefa(s) ainda com origem "
                   f"`{db.ORIGEM_APROXIMADA}` em {len(pend)} área(s) — {amostra}"
                   f"{f'; +{resto} área(s)' if resto > 0 else ''} "
                   f"(`python tools/plano.py --revisar-area AREA`)")
    # W1 do reconcile (B3/F35): a linha sai SEMPRE, inclusive como NAO MEDIDO.
    out.append(render_planilha(p.get("planilha") or reconcile_planilha()))
    d = p.get("diagnostico")
    if d:
        if d.get("zona"):
            out.append(f"- 🔬 **Diagnóstico:** zona **{d['zona']}** · média dos blocos "
                       f"{d['media_blocos']}% · **desvio {d['desvio']} pp** · "
                       f"grade {d['cobertura_pct']}% percorrida")
            out.append(f"    • {d['prescricao']}")
            if d.get("acao_variancia"):
                out.append(f"    • 🔴 {d['acao_variancia']}")
        sim = d.get("simulado") or {}
        if sim.get("em_debito"):
            out.append(f"    • ⚠️ **Simulado em débito** (nenhum em {sim['janela_dias']}d · "
                       f"último {sim.get('ultimo') or 'nunca'}) — política: 1/semana")
        for h in (d.get("habilidades") or [])[:3]:
            flag = " 🔴" if h.get("padrao_de_raciocinio") else ""
            out.append(f"    • habilidade reincidente{flag}: {h['texto']} "
                       f"({h['ocorrencias']}x em {h['temas_distintos']} temas)")
    r = p.get("recomendacao")
    if r:
        ctx = r["contexto"]
        rotulo = "defaults" if r["defaults_assumidos"] else "dia"
        out.append(f"- 🧠 **Recomendação do dia** [{rotulo}: {ctx['tempo_h']:g}h/{ctx['energia']}]:")
        for i, b in enumerate(r["blocos"], 1):
            alvo = f" — {b['alvo']}" if b.get("alvo") else ""
            qtd = f" {b['qtd']}" if b.get("qtd") else ""
            out.append(f"    {i}. {b['tipo']}{qtd}{alvo} · {b['motivo']}")
        pj = r["projecao"]
        if pj["dias_para_fechar"] is not None:
            out.append(f"    • projeção: ritmo real {pj['ritmo_real']}q/dia → grade fecha em "
                       f"~{pj['dias_para_fechar']}d (folga {pj['folga_dias']}d) · "
                       f"necessário {pj['ritmo_necessario']}q/dia (janela {pj['janela_dias']}d)")
        else:
            out.append(f"    • projeção: sem ritmo medido na janela de {pj['janela_dias']}d — "
                       f"necessário {pj['ritmo_necessario']}q/dia")
        out.append(f"    • sinais: {'; '.join(r['justificativa'][:3])}")
    out.append(f"- ▶️ **Passo sugerido:** {p['sugestao_passo']}")
    return "\n".join(out)


PLANO_DIA_DDL = '''
CREATE TABLE IF NOT EXISTS plano_dia (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    data               TEXT NOT NULL,
    ordem              INTEGER NOT NULL,
    task_tipo          TEXT NOT NULL,
    alvo_tema          TEXT,
    volume_planejado   INTEGER NOT NULL DEFAULT 0,
    tempo_h            REAL,
    energia            TEXT,
    defaults_assumidos INTEGER NOT NULL DEFAULT 0,
    criado_em          TEXT NOT NULL
)
'''


def persistir_plano(p):
    """Persiste os blocos recomendados do dia (spec telemetria-estudo-part-1).

    delete+insert TRANSACIONAL por data: o plano é atômico por dia — re-rodar
    substitui (precedente F22: nunca acumula); UPSERT por (data, ordem) deixaria
    blocos órfãos quando o re-run recomenda menos blocos. Lazy DDL no padrão
    preparacao_estado (registrar_sessao_bulk). Só metadado de processo:
    tipo/qtd/label/flags — nenhum conteúdo clínico. Falha vira WARN; o plano
    do stdout nunca se perde por causa da persistência.
    """
    r = p.get("recomendacao") or {}
    blocos = r.get("blocos") or []
    ctx = r.get("contexto") or {}
    con = None
    try:
        con = db.get_connection()
        con.execute(PLANO_DIA_DDL)
        con.execute("CREATE INDEX IF NOT EXISTS idx_plano_dia_data ON plano_dia(data)")
        con.execute("DELETE FROM plano_dia WHERE data = ?", (p["data"],))
        agora = datetime.now().isoformat(timespec="seconds")
        for i, b in enumerate(blocos, 1):
            con.execute(
                "INSERT INTO plano_dia (data, ordem, task_tipo, alvo_tema, "
                "volume_planejado, tempo_h, energia, defaults_assumidos, criado_em) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (p["data"], i, b.get("tipo") or "?", b.get("alvo"),
                 int(b.get("qtd") or 0), ctx.get("tempo_h"), ctx.get("energia"),
                 1 if r.get("defaults_assumidos") else 0, agora))
        con.commit()
    except Exception as e:
        if con is not None:
            try:
                con.rollback()
            except Exception:
                pass
        print(f"[WARN] PLANO_DIA: persistência falhou ({e}) — o plano segue no stdout.")
    finally:
        if con is not None:
            con.close()


def ler_plano(data_iso):
    """Blocos planejados de uma data (consumo da part-2 e do --plano-de)."""
    con = None
    try:
        con = db.get_connection()
        rows = con.execute(
            "SELECT ordem, task_tipo, alvo_tema, volume_planejado, tempo_h, "
            "energia, defaults_assumidos, criado_em FROM plano_dia "
            "WHERE data = ? ORDER BY ordem", (data_iso,)).fetchall()
    except Exception:
        rows = []
    finally:
        if con is not None:
            con.close()
    cols = ("ordem", "task_tipo", "alvo_tema", "volume_planejado", "tempo_h",
            "energia", "defaults_assumidos", "criado_em")
    return [dict(zip(cols, r)) for r in rows]


# --- Aderência planejado × real (spec telemetria-estudo-part-2) ---------------
# Família de medição por tipo de bloco: qual fonte MEDIDA responde pelo tipo.
# Trava anti-sycophancy: a classificação deriva SÓ de fsrs_revlog/sessoes_bulk
# (realizado medido); tempo_h/energia são dimensão do plano, nunca evidência.
FAMILIA_MEDICAO = {"mini-drill": "cards", "fsrs": "cards",
                   "questoes": "questoes", "simulado": "simulado",
                   "descanso": None}


def realizado_do_dia(con, data_iso):
    """Realizado MEDIDO do dia, direto das fontes SSOT (read-only)."""
    q = con.execute(
        "SELECT COALESCE(SUM(questoes_feitas),0) FROM sessoes_bulk "
        "WHERE area <> 'Simulado' AND data_sessao = ?", (data_iso,)).fetchone()[0]
    sim = con.execute(
        "SELECT COUNT(*) FROM sessoes_bulk "
        "WHERE area = 'Simulado' AND data_sessao = ?", (data_iso,)).fetchone()[0]
    cards = con.execute(
        "SELECT COUNT(*) FROM fsrs_revlog WHERE date(review_time) = ?",
        (data_iso,)).fetchone()[0]
    return {"questoes": q or 0, "simulado": sim or 0, "cards": cards or 0}


def classificar_dia(plano_rows, realizado):
    """Classificação PURA planejado×real de um dia (testável por fixtures).

    Regras determinísticas: cumprido (real >= planejado), parcial (0 < real <
    planejado), pulado (real == 0 e planejado > 0); volume 0 (ex.: descanso) =
    cumprido trivial. Famílias que dividem a mesma medida (mini-drill e fsrs
    dividem 'cards') alocam o realizado NA ORDEM do plano — mini-drill primeiro
    por construção (R1 vem antes). Realizado sem bloco correspondente (ou acima
    do planejado da família) vira 'extra' — estudo não planejado é sinal de 1ª
    classe, nunca descartado.
    """
    saldo = dict(realizado)
    consumo_planejado = {}
    blocos = []
    for b in sorted(plano_rows, key=lambda r: r.get("ordem", 0)):
        medida = FAMILIA_MEDICAO.get(b.get("task_tipo"))
        planejado = int(b.get("volume_planejado") or 0)
        if medida is None:
            blocos.append(dict(b, realizado=None,
                               status="cumprido" if planejado == 0 else "pulado"))
            continue
        consumo_planejado[medida] = consumo_planejado.get(medida, 0) + planejado
        real = min(saldo.get(medida, 0), planejado)
        saldo[medida] = saldo.get(medida, 0) - real
        if planejado == 0 or real >= planejado:
            status = "cumprido"
        elif real > 0:
            status = "parcial"
        else:
            status = "pulado"
        blocos.append(dict(b, realizado=real, status=status))
    extra = [{"tipo": medida, "qtd": resto}
             for medida, resto in sorted(saldo.items()) if resto > 0]
    return {"blocos": blocos, "extra": extra}


def aderencia(fim=None, semanas=1):
    """Série de aderência por dia na janela (deriva TUDO do db; zero input manual)."""
    fim = fim or date.today()
    dias = []
    con = None
    try:
        con = db.get_connection()
        for delta in range(semanas * 7 - 1, -1, -1):
            d = fim.fromordinal(fim.toordinal() - delta)
            data_iso = d.isoformat()
            plano = ler_plano(data_iso)
            try:
                real = realizado_do_dia(con, data_iso)
            except Exception:
                real = {"questoes": 0, "simulado": 0, "cards": 0}
            if plano:
                dia = classificar_dia(plano, real)
                dia["sem_plano"] = False
            else:
                # honestidade > completude: sem plano gravado, nada é "pulado";
                # o realizado aparece inteiro como extra (sinal, não erro).
                dia = {"blocos": [],
                       "extra": [{"tipo": k, "qtd": v}
                                 for k, v in sorted(real.items()) if v > 0],
                       "sem_plano": True}
            dia["data"] = data_iso
            dias.append(dia)
    finally:
        if con is not None:
            con.close()
    return dias


def render_aderencia(dias):
    out = ["# 📈 Aderência planejado × real", ""]
    for dia in dias:
        if dia["sem_plano"]:
            extras = ", ".join(f"{e['qtd']} {e['tipo']}" for e in dia["extra"])
            out.append(f"- **{dia['data']}** — sem plano gravado"
                       + (f" · extra: {extras}" if extras else ""))
            continue
        marcas = {"cumprido": "OK", "parcial": "parcial", "pulado": "PULADO"}
        partes = []
        for b in dia["blocos"]:
            real_txt = "-" if b["realizado"] is None else b["realizado"]
            partes.append(f"{b['task_tipo']} {real_txt}/{b['volume_planejado']} "
                          f"[{marcas[b['status']]}]")
        extras = ", ".join(f"{e['qtd']} {e['tipo']}" for e in dia["extra"])
        out.append(f"- **{dia['data']}** — " + " · ".join(partes)
                   + (f" · extra: {extras}" if extras else ""))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Plano do Dia (read-only).")
    ap.add_argument("--json", action="store_true", help="Saída JSON crua")
    ap.add_argument("--handoff-block", action="store_true", dest="handoff_block",
                    help="Emite o bloco numérico 'Estado por frente' derivado do db, "
                         "pronto para colar no HANDOFF.md (F6: número digitado vira derivado)")
    ap.add_argument("--review-plan", action="store_true", dest="review_plan",
                    help="Emite os clusters do dia (area/tema + contagem por bucket) "
                         "derivados da fila real (F3); com --json, sai o agregado cru")
    ap.add_argument("--difficulty", nargs=2, metavar=("AREA", "TEMA"),
                    help="Reporta nota inferida + degrau + proposito de um tema (read-only)")
    ap.add_argument("--tempo", type=float, default=None, metavar="H",
                    help="Horas disponíveis hoje (recomendador; default declarado no output)")
    ap.add_argument("--energia", choices=["alta", "media", "baixa"], default=None,
                    help="Energia do dia (recomendador; modula a capacidade)")
    ap.add_argument("--no-persist", action="store_true", dest="no_persist",
                    help="Simulação: monta o plano sem gravar em plano_dia")
    ap.add_argument("--plano-de", metavar="YYYY-MM-DD", dest="plano_de",
                    help="Imprime o plano PERSISTIDO de uma data (JSON)")
    ap.add_argument("--planilha", action="store_true",
                    help="Reconcile W1 planilha x db com a idade da planilha (read-only, "
                         "nunca bloqueia); com --json sai o dict cru")
    ap.add_argument("--aderencia", action="store_true",
                    help="Relatório aderência planejado×real por dia (derivado do db)")
    ap.add_argument("--semanas", type=int, default=1, metavar="N",
                    help="Janela do --aderencia em semanas (default 1)")
    args = ap.parse_args()
    if args.plano_de:
        print(json.dumps(ler_plano(args.plano_de), ensure_ascii=False, indent=2))
        return
    if args.aderencia:
        dias = aderencia(semanas=max(1, args.semanas))
        print(json.dumps(dias, ensure_ascii=False, indent=2) if args.json
              else render_aderencia(dias))
        return
    if args.planilha:
        r = reconcile_planilha()
        print(json.dumps(r, ensure_ascii=False, indent=2) if args.json else render_planilha(r))
        return
    if args.handoff_block:
        print(render_handoff_block(build()))
        return
    if args.review_plan:
        clusters = review_plan()
        print(json.dumps(clusters, ensure_ascii=False, indent=2) if args.json
              else render_review_plan(clusters))
        return
    if args.difficulty:
        area, tema = args.difficulty
        print(json.dumps(difficulty_report(area, tema), ensure_ascii=False,
                         default=str, indent=2))
        return
    if args.tempo is not None or args.energia is not None:
        try:   # condição declarada do dia vira série (pergunta em aberto 2 do PRD)
            db.registrar_condicao_dia(args.tempo, args.energia)
        except Exception:
            pass
    p = build(tempo_h=args.tempo, energia=args.energia)
    # Persistência SÓ no caminho que renderiza o plano do dia (default/--json):
    # os modos de relatório (--handoff-block/--review-plan/--difficulty) retornam
    # antes e NÃO regravam — o handoff-block no fechamento rodaria com defaults e
    # sobrescreveria a intenção declarada de manhã (--tempo/--energia), corrompendo
    # a série de aderência da part-2.
    if not args.no_persist:
        persistir_plano(p)
    print(json.dumps(p, ensure_ascii=False, default=str, indent=2) if args.json else render(p))


if __name__ == "__main__":
    main()
