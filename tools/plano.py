#!/usr/bin/env python3
"""plano.py -- o plano de estudo como DADO (`plano_tarefas`): semeadura, listagem e
progresso (concluir / cortar / mover / revisar por area).

Specs: `.vibeflow/specs/plano-ssot-e-cards-v2-part-2.md` (semeadura) e `-part-3.md`
(mutacoes e revisao por area). Depende da part-1 (`core/cronograma/grade_extensivo.json`).

Ate a s183 o "plano" era a soma de tres coisas que nunca conversaram: `grade.json`
(calendario do PDF da Reta Final), um snapshot do Dashboard do Drive e a cabeca do
usuario. Este CLI faz o plano existir como linha de banco, semeado de TRES fontes:

    extensivo  as 735 tarefas do Cronograma Extensivo (52 semanas, part-1)
    rf         as 139 tarefas PENDENTES da Reta Final S17-S28
    custom     as tarefas escritas a mao em `core/cronograma/plano_custom.json`

🔴 Semear NUNCA infere conclusao. O status inicial sai do snapshot do Dashboard
(`dashboard_snapshot.json`, congelado em 2026-09-16, `origem_conclusao=dashboard_2026-09-10`),
que e sinal APROXIMADO por confissao do usuario. Sem match de nome -> `pendente`, e o
numero de nao-casados e IMPRESSO no dry-run. A verdade e fixada na revisao por area (part-3).

Rito (mesmo do `tools/cards_prune.py`, AGENTE.md secao 10.7): dry-run e o default,
`--apply` exige `--expect N` e RECUSA (exit 2) se N != o numero medido na hora. Vale
para o `--semear` e para o lote da `--confirmar-area`; mutacao de UMA linha
(`--concluir`/`--cortar`/`--mover`/`--reabrir`) grava direto -- nao e operacao em lote.

Uso:
    python tools/plano.py --semear --dry-run
    python tools/plano.py --semear --apply --expect 896
    python tools/plano.py --listar --semana 1
    python tools/plano.py --listar --bloco MFC --status pendente --json
    python tools/plano.py --concluir 123 --sessao 126
    python tools/plano.py --cortar 124 --motivo "coberto pela Reta Final"
    python tools/plano.py --mover 125 --semana 4 --ordem 2
    python tools/plano.py --reabrir 126
    python tools/plano.py --revisar-area Preventiva
    python tools/plano.py --confirmar-area Preventiva --feitas "1,4" --pendentes "2" --dry-run
    python tools/plano.py --pendencia-revisao
    python tools/plano.py --reserva > docs/RESERVA-FASE1.md

Camada fina sobre `app.utils.db` -- nao abre `sqlite3` proprio (toda escrita e
`plano_upsert_tarefas`, `plano_set_status`, `plano_mover` ou `plano_confirmar_area`).
Assinatura canonica em `.claude/commands/engenharia-cli.md`.
"""
import argparse
import json
import math
import os
import sys
import unicodedata
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import db  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_CRONO = os.path.join(ROOT, "core", "cronograma")
P_EXTENSIVO = os.path.join(DIR_CRONO, "grade_extensivo.json")
P_DASHBOARD = os.path.join(DIR_CRONO, "dashboard_snapshot.json")
P_GRADE_RF = os.path.join(DIR_CRONO, "grade.json")
P_CUSTOM = os.path.join(DIR_CRONO, "plano_custom.json")
#: Links das listas de exercicios por (fonte, semana, tarefa), extraidos das ANOTACOES de
#: hiperlink dos dois PDFs (s188, F119). Dado versionado; ausente = nenhum link aplicado.
P_LINKS = os.path.join(DIR_CRONO, "links_listas.json")
#: A TRILHA da Fase 1 como dado (s188, F120): overrides de semana/ordem/status/nota por
#: (fonte, ref_semana_fonte, tarefa_fonte), aplicados DEPOIS das regras puras. Ausente =
#: vale a politica pura de `ordenar_fase1`.
P_TRILHA = os.path.join(DIR_CRONO, "plano_trilha.json")
#: Incidencia por (area, tema) nas provas UERJ 2021-2026 (s188, F121). Lida pela RESERVA (s189).
P_PREVALENCIA = os.path.join(DIR_CRONO, "prevalencia_uerj.json")

#: Carimbo da origem do status inicial. Fixo: o snapshot e dado CONGELADO, e a data
#: que importa e a da planilha (modificada em 10/09), nao a da leitura. A string mora
#: em `db` (part-3): quem conta a pendencia de revisao e quem semeia tem que casar.
ORIGEM_DASHBOARD = db.ORIGEM_APROXIMADA

#: Tamanho do bloco de conferencia do `--revisar-area` (spec part-3): a passada tem
#: ~900 linhas e conferir tudo de uma vez e como nao conferir.
BLOCO_REVISAO = 25

#: Ordem de ataque da revisao por area = peso do bloco na prova da UERJ (20q por
#: conteudo, `reference_edital_uerj_2027`). MFC primeiro, cauda de CM por ultimo.
PESO_BLOCO = {"MFC": 0, "PED": 1, "CIR": 2, "GO": 3, "CM": 4}

#: Media por lista medida no PDF da Reta Final. Usada so quando a fonte NAO declara
#: o numero -- e nesse caso a linha leva `q_estimada` na nota (numero derivado nunca
#: se passa por medido).
Q_PADRAO_REVISAO = 43.0
Q_PADRAO_TEORIA = 0.0


# ---------------------------------------------------------------- normalizacao

def normalizar(texto):
    """casefold + sem acento + `-`/`|` viram espaco + espacos colapsados.

    O `-` entra no colapso porque o PDF quebra nomes no meio ("Disturbios Acido-
    Base") e o Dashboard nao ("Disturbios Acido-Base"): sem isso o par nunca casa.
    NAO faz substring nem stemming -- casamento e exato depois de normalizado.
    """
    t = unicodedata.normalize("NFKD", str(texto or ""))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("-", " ").replace("|", " ")
    return " ".join(t.casefold().split())


def partes_do_tema(tema):
    """Tema bundlado ("A; B; C") -> lista de partes. `;` e `,` separam."""
    return [p.strip() for p in str(tema or "").replace(";", ",").split(",") if p.strip()]


# ------------------------------------------------------------------- snapshot

def indexar_dashboard(tarefas):
    """Dois indices do snapshot: por (area, assunto, tipo) e por (area, assunto).

    O primeiro responde "esta tarefa exata esta marcada?"; o segundo responde "existe
    QUALQUER `Teoria*` deste assunto marcada?", que e a regra da Reta Final (la o tema
    e generico e a tarefa do PDF nao tem numero romano).
    """
    por_tarefa, por_tema = {}, {}
    for t in tarefas:
        chave = (t["area"], normalizar(t["assunto"]), normalizar(t["tipo"]))
        por_tarefa.setdefault(chave, []).append(t)
        por_tema.setdefault((t["area"], normalizar(t["assunto"])), []).append(t)
    return {"por_tarefa": por_tarefa, "por_tema": por_tema}


def status_extensivo(idx, area, assunto, tipo):
    """`True` (casou e esta marcada), `False` (casou e nao esta) ou `None` (sem match).

    `None` e o caso que a spec obriga a nascer `pendente`: nome divergente entre o PDF
    e o Dashboard nao e evidencia de nada.
    """
    linhas = idx["por_tarefa"].get((area, normalizar(assunto), normalizar(tipo)))
    if not linhas:
        return None
    return any(bool(l["realizada"]) for l in linhas)


def _tipos_compativeis(tipo_norm, linhas):
    """Linhas do snapshot cujo tipo BRUTO responde por `tipo_norm` da Reta Final."""
    if tipo_norm == "teoria":
        return [l for l in linhas if normalizar(l["tipo"]).startswith("teoria")]
    if tipo_norm == "revisao_questoes":
        return [l for l in linhas if normalizar(l["tipo"]).startswith("revisao por questoes")]
    return [l for l in linhas if normalizar(l["tipo"]).startswith("revisao")
            and not normalizar(l["tipo"]).startswith("revisao por questoes")]


def status_rf(idx, area, tema, tipo_norm):
    """Reta Final: o tema pode ser BUNDLADO, e so conta feito se TODAS as partes
    tiverem match feito. Parte sem match derruba a tarefa inteira para pendente --
    "nao achei" nunca vira "ja fiz"."""
    partes = partes_do_tema(tema)
    if not partes:
        return False
    for parte in partes:
        linhas = idx["por_tema"].get((area, normalizar(parte)))
        if not linhas:
            return False
        candidatas = _tipos_compativeis(tipo_norm, linhas)
        if not candidatas or not any(bool(l["realizada"]) for l in candidatas):
            return False
    return True


# ------------------------------------------------- regras de fase (puras, part-2)

#: Fase 1 = 16/09 -> 01/11/2026 (7 semanas ate a prova da UERJ). Ela nao roda o
#: extensivo inteiro: leva a Reta Final PENDENTE ordenada por peso de bloco UERJ,
#: mais o punhado de tarefas de Preventiva que sao literalmente o bloco de MFC.
ASSUNTOS_MFC_FASE1 = {normalizar(a) for a in (
    "Medicina de Família e Comunidade",
    "Saúde do Idoso",
    "Atenção Primária à Saúde no Brasil",
    "Processo Saúde-Doença",
)}

#: Prioridade 1 da Fase 1: os quatro blocos que a UERJ pesa (MFC, PED, CIR, GO).
AREAS_PRI1 = ("Preventiva", "Pediatria", "Cirurgia", "Ginecologia", "Obstetrícia")

#: Cauda de baixo peso na UERJ -- cortada na Fase 1 (volta pelo extensivo na Fase 2).
CAUDA_AREAS = ("Otorrino", "Oftalmo", "Dermato", "Ortopedia", "Hepato", "Pneumo")
CAUDA_TEMAS = tuple(normalizar(t) for t in ("Estatística Médica", "Normas Regulamentadoras"))

#: Clinica Medica DIRIGIDA: o recorte de CM que a Fase 1 mantem, por fraqueza medida
#: (Nefro/gasometria e dificuldade DECLARADA pelo usuario em 12/09) e por peso de prova.
CM_DIRIGIDA = tuple(normalizar(t) for t in (
    "Ácido-Base", "Potássio", "Nefrolitíase", "Hipertensão Arterial Sistêmica",
    "Fibrilação", "Parada Cardiorrespiratória", "Pólipos e Neoplasias Intestinais",
    "Doenças Inflamatórias do Tecido Conjuntivo", "Anemias Microcíticas", "Leucemias",
))
#: Dos temas acima, estes so entram quando a tarefa e de REVISAO (a teoria deles ja
#: rodou; o que falta e o drill).
CM_DIRIGIDA_SO_REVISAO = tuple(normalizar(t) for t in ("Nefrolitíase",
                                                       "Hipertensão Arterial Sistêmica"))

NOTA_CAUDA = "Fase 1: cauda de baixo peso UERJ"
NOTA_CM_EXTENSIVO = "Fase 1: coberto pelo extensivo na Fase 2"
NOTA_RESERVA = "reserva: aprofundamento por fraqueza"
NOTA_FINAL_FSRS = "revisão final substituída pelo FSRS"
NOTA_MFC_PUXADA = "Fase 1: bloco MFC/APS da UERJ, puxado do extensivo"
NOTA_FORA_DA_TRILHA = "fora da trilha da Fase 1 (reserva)"

#: Semanas do plano que pertencem a Fase 1 (16/09 -> 01/11/2026). A trilha exclusiva so
#: tem autoridade sobre esta faixa; a Fase 2 (8+) nunca e tocada por ela.
SEMANAS_FASE1 = range(1, 8)
#: Status que um override PODE pedir. `feita` fica de fora de proposito: conclusao so
#: nasce de `--concluir` com sessao vinculada (part-3), nunca de arquivo de plano.
STATUS_TRILHA = ("pendente", "cortada")


def semana_fase1_pri1(semana_rf):
    """S17-S18 -> 1, S19-S20 -> 2, ... S27-S28 -> 6. Duas semanas da Reta Final
    comprimidas em uma do plano: a Fase 1 tem 7 semanas para 12 da RF."""
    return 1 + (int(semana_rf) - 17) // 2


def semana_fase1_cm(semana_rf):
    """CM dirigida ocupa a segunda metade da Fase 1 (semanas 3-7), preservando a
    ORDEM da Reta Final: as 12 semanas S17-S28 sao espalhadas na faixa de 5."""
    return 3 + (int(semana_rf) - 17) * 5 // 12


def semana_fase2(semana_ext):
    """Fase 2 comeca na semana 8 do plano e segue o extensivo a partir da S21."""
    return 8 + (int(semana_ext) - 21)


def _contem(tema, padroes):
    alvo = normalizar(tema)
    return any(p in alvo for p in padroes)


def e_cauda(linha):
    """Cauda da Fase 1: area de baixo peso OU tema explicitamente excluido."""
    return linha["area"] in CAUDA_AREAS or _contem(linha["tema"], CAUDA_TEMAS)


def e_cm_dirigida(linha):
    """CM dirigida: tema da lista; dois deles so na forma REVISAO."""
    alvo = normalizar(linha["tema"])
    for padrao in CM_DIRIGIDA:
        if padrao not in alvo:
            continue
        if padrao in CM_DIRIGIDA_SO_REVISAO and linha["tipo_norm"] == "teoria":
            continue
        return True
    return False


def ordenar_fase1(linhas):
    """Fase 1 (semanas 1-7, 16/09 -> 01/11/2026). Funcao PURA.

    Recebe as candidatas -- Reta Final PENDENTE de S17-S28 (`fonte='rf'`) e o punhado
    de tarefas de Preventiva puxadas do extensivo (`fonte='extensivo'`) -- e devolve
    cada uma com `semana_plano`, `ordem`, `status` e `nota` decididos.

    Ordem das regras (a primeira que casa vence):
      1. extensivo puxado -> semanas 1-2, ordem 1 (o bloco MFC abre o plano);
      2. RF na cauda de baixo peso UERJ -> `cortada`;
      3. RF nos blocos MFC/PED/CIR/GO -> semanas 1-6 por `semana_fase1_pri1`;
      4. RF de CM DIRIGIDA -> semanas 3-7 por `semana_fase1_cm`;
      5. resto da Clinica Medica -> `cortada` (o extensivo cobre na Fase 2).
    """
    saida = []
    puxadas = sorted([l for l in linhas if l["fonte"] == "extensivo"],
                     key=lambda l: (l["ref_semana_fonte"], l["tarefa_fonte"]))
    corte = math.ceil(len(puxadas) / 2)
    for i, linha in enumerate(puxadas):
        saida.append({**linha, "semana_plano": 1 if i < corte else 2, "ordem": 1,
                      "status": "pendente", "nota": NOTA_MFC_PUXADA})
    for linha in sorted([l for l in linhas if l["fonte"] == "rf"],
                        key=lambda l: (l["ref_semana_fonte"], l["tarefa_fonte"])):
        semana_rf = linha["ref_semana_fonte"]
        if e_cauda(linha):
            decisao = {"semana_plano": None, "ordem": None, "status": "cortada",
                       "nota": NOTA_CAUDA}
        elif linha["area"] in AREAS_PRI1:
            decisao = {"semana_plano": semana_fase1_pri1(semana_rf),
                       "ordem": linha["tarefa_fonte"], "status": "pendente", "nota": None}
        elif e_cm_dirigida(linha):
            decisao = {"semana_plano": semana_fase1_cm(semana_rf),
                       "ordem": linha["tarefa_fonte"], "status": "pendente",
                       "nota": "Fase 1: CM dirigida"}
        else:
            decisao = {"semana_plano": None, "ordem": None, "status": "cortada",
                       "nota": NOTA_CM_EXTENSIVO}
        saida.append({**linha, **decisao})
    return saida


def ordenar_fase2(linhas):
    """Fase 2 (semanas 8+) e o resto do extensivo. Funcao PURA.

    Recebe as tarefas do extensivo que NAO foram puxadas para a Fase 1, cada uma com
    `feita` (`True`/`False`/`None` = sem match no Dashboard), e decide:

      - S49-S52 -> `cortada` ("revisão final substituída pelo FSRS");
      - marcada no Dashboard -> `feita`, com `origem_conclusao`, e `semana_plano=NULL`
        (foi feita no calendario do extensivo, nunca ocupou slot DESTE plano -- datar
        para tras seria ficcao);
      - S1-S20 pendente -> `pendente` com `semana_plano=NULL` e nota de reserva:
        so entra na fila quando alguem mover, por fraqueza;
      - S21-S48 pendente -> `semana_plano = 8 + (S - 21)`, com duas excecoes puxadas
        para a frente: Preventiva das S21-S26 -> semanas 8-9, e `IAMCSSST`/`Osteoporose`
        da S44 -> semana 12.
    """
    saida = []
    for linha in linhas:
        semana_ext = linha["ref_semana_fonte"]
        if semana_ext >= 49:
            decisao = {"semana_plano": None, "ordem": None, "status": "cortada",
                       "nota": NOTA_FINAL_FSRS, "origem_conclusao": None}
        elif linha.get("feita") is True:
            decisao = {"semana_plano": None, "ordem": None, "status": "feita",
                       "nota": None, "origem_conclusao": ORIGEM_DASHBOARD}
        elif semana_ext <= 20:
            decisao = {"semana_plano": None, "ordem": None, "status": "pendente",
                       "nota": NOTA_RESERVA, "origem_conclusao": None}
        else:
            semana = semana_fase2(semana_ext)
            nota = None
            if linha["area"] == "Preventiva" and 21 <= semana_ext <= 26:
                semana = 8 + (semana_ext - 21) // 3
                nota = "Fase 2: Preventiva/APS/SUS puxada para as semanas 8-9"
            elif semana_ext == 44 and _contem(linha["tema"], ("iamcssst", "infarto",
                                                              "osteoporose")):
                semana = 12
                nota = "Fase 2: IAM/Osteoporose puxados para a semana 12"
            decisao = {"semana_plano": semana, "ordem": linha["tarefa_fonte"],
                       "status": "pendente", "nota": nota, "origem_conclusao": None}
        saida.append({**linha, **decisao})
    return saida


# ------------------------------------------------------- trilha como dado (s188)

def indexar_links(links):
    """`links_listas.json` -> {(fonte, semana, tarefa): url}. So entra quem tem URL."""
    idx = {}
    for fonte in ("rf", "extensivo"):
        for item in (links or {}).get(fonte) or []:
            if item.get("url"):
                idx[(fonte, int(item["semana"]), int(item["tarefa"]))] = item["url"]
    return idx


def _validar_override(o):
    chave = (o.get("fonte"), o.get("ref_semana_fonte"), o.get("tarefa_fonte"))
    if None in chave:
        raise ValueError(
            f"override sem chave completa (fonte, ref_semana_fonte, tarefa_fonte): {o}")
    semana = o.get("semana_plano")
    if semana is not None and (not isinstance(semana, int) or semana < 1):
        raise ValueError(f"override {chave}: semana_plano invalida ({semana!r})")
    status = o.get("status")
    if status is not None and status not in STATUS_TRILHA:
        raise ValueError(f"override {chave}: status {status!r} fora de {STATUS_TRILHA} "
                         f"(conclusao nasce de --concluir, nunca da trilha)")
    return chave


def aplicar_trilha(decididas, trilha):
    """Aplica a trilha (dado) sobre as linhas ja decididas pelas regras puras. PURA.

    Cada override casa por `(fonte, ref_semana_fonte, tarefa_fonte)` e regrava
    `semana_plano`/`ordem` (sempre) e `status`/`nota` (quando presentes). Com
    `fase1_exclusiva`, toda linha PENDENTE que estaria nas semanas da Fase 1 e NAO esta na
    trilha sai da fila (semana/ordem NULL + nota) sem mudar de status -- a Fase 1 passa a
    ter UMA autoridade. Devolve `(linhas, {"aplicados", "sem_linha", "fora"})`.

    Limite declarado: o re-seed so reescreve `CAMPOS_SEMEADOS`; o `status` de linha que JA
    existe no banco nao muda por aqui -- muda por `--reabrir`/`--cortar`.
    """
    stats = {"aplicados": 0, "sem_linha": [], "fora": 0}
    overrides = (trilha or {}).get("overrides") or []
    if not overrides:
        return decididas, stats
    por_chave = {}
    for o in overrides:
        chave = _validar_override(o)
        if chave in por_chave:
            raise ValueError(f"override duplicado na trilha: {chave}")
        por_chave[chave] = o
    vistos = set()
    saida = []
    for d in decididas:
        chave = (d["fonte"], d["ref_semana_fonte"], d["tarefa_fonte"])
        o = por_chave.get(chave)
        if o is not None:
            vistos.add(chave)
            novo = {**d, "semana_plano": o.get("semana_plano"), "ordem": o.get("ordem")}
            if o.get("status") is not None:
                novo["status"] = o["status"]
            elif novo.get("status") == "cortada" and o.get("semana_plano") is not None:
                novo["status"] = "pendente"   # agendar e reabrir: cortada nao tem semana
            if "nota" in o:
                novo["nota"] = o["nota"]
            elif d.get("status") == "cortada" and novo["status"] == "pendente":
                novo["nota"] = None           # a nota de corte da politica pura caducou
            stats["aplicados"] += 1
            saida.append(novo)
            continue
        if (trilha.get("fase1_exclusiva") and d.get("semana_plano") in SEMANAS_FASE1
                and d.get("status", "pendente") == "pendente"):
            stats["fora"] += 1
            saida.append({**d, "semana_plano": None, "ordem": None,
                          "nota": _nota(d.get("nota"), NOTA_FORA_DA_TRILHA)})
            continue
        saida.append(d)
    stats["sem_linha"] = sorted(k for k in por_chave if k not in vistos)
    return saida, stats


def calendario_trilha(trilha=None):
    """`calendario` da trilha -> `{semana_plano: (inicio, fim)}` em `date`. PURA sobre o
    dict; sem argumento le `plano_trilha.json` (ausente ou sem calendario -> `{}`).

    s189 (F123b): e o UNICO calendario da Fase 1 -- a cota do dia do `day_plan` le daqui, a
    mesma fonte que o `aplicar_trilha` consome. Data malformada LEVANTA: calendario errado
    nao vira cota silenciosa."""
    if trilha is None:
        trilha = _ler(P_TRILHA) if os.path.exists(P_TRILHA) else {}
    return {int(s): (date.fromisoformat(f["inicio"]), date.fromisoformat(f["fim"]))
            for s, f in ((trilha or {}).get("calendario") or {}).items()}


# ------------------------------------------------------------------ q_previstas

def q_prevista(n_questoes, tipo_norm):
    """`n_questoes` quando a fonte declara; senao a media por tipo. Devolve
    `(valor, estimada)` -- `estimada=True` obriga a nota a dizer `q_estimada`."""
    if n_questoes is not None and float(n_questoes) > 0:
        return float(n_questoes), False
    padrao = Q_PADRAO_REVISAO if tipo_norm in ("revisao", "revisao_questoes") else Q_PADRAO_TEORIA
    return padrao, True


def _nota(*pedacos):
    itens = [p for p in pedacos if p]
    return "; ".join(itens) if itens else None


# --------------------------------------------------------------- montagem geral

def _ler(caminho):
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def montar_linhas(extensivo=None, dashboard=None, grade_rf=None, custom=None,
                  links=None, trilha=None):
    """As tres fontes -> linhas prontas para `db.plano_upsert_tarefas`, mais o
    relatorio de COUNT-ASSERT. Nada de I/O de banco aqui: puro sobre os JSONs.

    `links` e `trilha` (s188) sao camadas de DADO por cima das regras puras. So sao lidas
    do disco no caminho de PRODUCAO (nenhuma fonte injetada); com fonte injetada, omitidas
    valem vazio -- o dado real nunca vaza para dentro de um teste sintetico."""
    producao = all(f is None for f in (extensivo, dashboard, grade_rf, custom))
    if links is None:
        links = _ler(P_LINKS) if producao and os.path.exists(P_LINKS) else {}
    if trilha is None:
        trilha = _ler(P_TRILHA) if producao and os.path.exists(P_TRILHA) else {}
    idx_links = indexar_links(links)
    extensivo = extensivo if extensivo is not None else _ler(P_EXTENSIVO)
    dashboard = dashboard if dashboard is not None else _ler(P_DASHBOARD)
    grade_rf = grade_rf if grade_rf is not None else _ler(P_GRADE_RF)
    custom = custom if custom is not None else _ler(P_CUSTOM)
    idx = indexar_dashboard(dashboard["tarefas"])

    # --- extensivo: as 735 tarefas, com o status do Dashboard anexado
    brutas, sem_match = [], 0
    for semana in extensivo["semanas"]:
        for t in semana["tasks"]:
            feita = status_extensivo(idx, t["area_norm"], t["assunto"], t["tipo"])
            if feita is None:
                sem_match += 1
            area = t["area_norm"] if t["area_norm"] != "Multi" else None
            q, estimada = q_prevista(t.get("n_questoes"), t["tipo_norm"])
            brutas.append({
                "fonte": "extensivo", "ref_semana_fonte": semana["semana"],
                "tarefa_fonte": t["tarefa"], "area": area, "tema": t["assunto"],
                "tipo": t["tipo"], "tipo_norm": t["tipo_norm"],
                "url_lista": (idx_links.get(("extensivo", semana["semana"], t["tarefa"]))
                              or t.get("url_lista")),
                "q_previstas": q,
                "feita": feita, "sem_match": feita is None,
                "_marcas": _nota("q_estimada" if estimada else None,
                                 None if area else
                                 f"area_fonte={t['disciplina']} fora de core/areas.json (F89)"),
                "_subtemas": t.get("subtemas") or [],
            })

    # --- quem o bloco MFC da UERJ puxa do extensivo para a Fase 1
    def alvo_mfc(linha):
        if linha["area"] != "Preventiva" or linha["feita"] is True:
            return False
        if normalizar(linha["tema"]) in ASSUNTOS_MFC_FASE1:
            return True
        return (linha["tipo_norm"] == "revisao_questoes"
                and any(normalizar(s) in ASSUNTOS_MFC_FASE1 for s in linha["_subtemas"]))

    puxadas = [l for l in brutas if alvo_mfc(l)]
    chaves_puxadas = {(l["ref_semana_fonte"], l["tarefa_fonte"]) for l in puxadas}
    resto = [l for l in brutas
             if (l["ref_semana_fonte"], l["tarefa_fonte"]) not in chaves_puxadas]

    # --- Reta Final: so o que esta PENDENTE nas S17-S28
    rf_linhas, rf_total = [], 0
    for semana in grade_rf["semanas"]:
        if not (17 <= semana["semana"] <= 28):
            continue
        for t in semana["tasks"]:
            rf_total += 1
            if status_rf(idx, t["area_norm"], t["tema"], t["tipo_norm"]):
                continue
            fonte_q = t.get("questoes_fonte")
            if fonte_q == "rateio_igual":
                q, marca = float(t.get("questoes") or 0.0), "q_rateio"
            else:
                q, estimada = q_prevista(t.get("questoes"), t["tipo_norm"])
                marca = "q_estimada" if estimada else None
            rf_linhas.append({
                "fonte": "rf", "ref_semana_fonte": semana["semana"],
                "tarefa_fonte": t["tarefa"], "area": t["area_norm"], "tema": t["tema"],
                "tipo": t["tipo"], "tipo_norm": t["tipo_norm"],
                "url_lista": idx_links.get(("rf", semana["semana"], t["tarefa"])),
                "q_previstas": q, "_marcas": marca,
            })

    decididas = ordenar_fase1(puxadas + rf_linhas) + ordenar_fase2(resto)

    # --- custom: semana/ordem vem do arquivo (o operador edita a mao)
    for t in custom["tarefas"]:
        decididas.append({
            "fonte": "custom", "ref_semana_fonte": 0, "tarefa_fonte": t["tarefa_fonte"],
            "semana_plano": t.get("semana_plano"), "ordem": t.get("ordem"),
            "area": t["area"], "tema": t["tema"], "tipo": t.get("tipo"),
            "tipo_norm": t.get("tipo_norm"), "url_lista": t.get("url_lista"),
            "q_previstas": float(t.get("q_previstas") or 0.0), "status": "pendente",
            "nota": t.get("nota"), "_marcas": None, "origem_conclusao": None,
        })

    decididas, st_trilha = aplicar_trilha(decididas, trilha)
    links_aplicados = sum(
        1 for d in decididas
        if d["fonte"] in ("rf", "extensivo") and d.get("url_lista")
        and idx_links.get((d["fonte"], d["ref_semana_fonte"], d["tarefa_fonte"]))
        == d.get("url_lista"))

    linhas = []
    for d in decididas:
        linhas.append({
            "fonte": d["fonte"], "ref_semana_fonte": d["ref_semana_fonte"],
            "tarefa_fonte": d["tarefa_fonte"], "semana_plano": d.get("semana_plano"),
            "ordem": d.get("ordem"), "area": d.get("area"), "tema": d.get("tema"),
            "tipo": d.get("tipo"), "tipo_norm": d.get("tipo_norm"),
            "url_lista": d.get("url_lista"), "q_previstas": d.get("q_previstas"),
            "status": d.get("status", "pendente"),
            "origem_conclusao": d.get("origem_conclusao"),
            "nota": _nota(d.get("nota"), d.get("_marcas")),
        })

    relatorio = {
        "extensivo_total": len(brutas),
        "extensivo_s21_s48": sum(1 for l in brutas if 21 <= l["ref_semana_fonte"] <= 48),
        "extensivo_s1_s20": sum(1 for l in brutas if l["ref_semana_fonte"] <= 20),
        "extensivo_s49_s52": sum(1 for l in brutas if l["ref_semana_fonte"] >= 49),
        "extensivo_sem_match": sem_match,
        "extensivo_sem_area": sum(1 for l in brutas if not l["area"]),
        "extensivo_puxadas_fase1": len(puxadas),
        "rf_total_s17_s28": rf_total,
        "rf_pendentes": len(rf_linhas),
        "custom": len(custom["tarefas"]),
        "links_aplicados": links_aplicados,
        "trilha_aplicados": st_trilha["aplicados"],
        "trilha_sem_linha": st_trilha["sem_linha"],
        "trilha_fora": st_trilha["fora"],
    }
    return linhas, relatorio


# -------------------------------------------------------------------- comandos

def _contar(linhas, chave):
    saida = {}
    for l in linhas:
        saida[l[chave]] = saida.get(l[chave], 0) + 1
    return saida


def _comparavel(campo, valor):
    """`q_previstas` e REAL no banco e float/int no JSON: compara como float."""
    if campo == "q_previstas" and valor is not None:
        return float(valor)
    return valor


def diferenca_semeada(linhas, atuais):
    """Linhas JA EXISTENTES que o re-seed reescreveria, e em quais campos. PURA.

    s189: o `--expect N` so prova quantas linhas NOVAS entram; "o re-seed nao muda nada"
    ficava sem prova. Espelha o UPSERT de `db.plano_upsert_tarefas`: so `CAMPOS_SEMEADOS`,
    e a `nota` de linha com `origem_conclusao = usuario` sobrevive (nao conta como mudanca).
    Devolve `(chaves_que_mudam, {campo: n})`."""
    por_chave = {(a["fonte"], a["ref_semana_fonte"], a["tarefa_fonte"]): a for a in atuais}
    mudam, campos = [], {}
    for l in linhas:
        chave = (l["fonte"], l["ref_semana_fonte"], l["tarefa_fonte"])
        a = por_chave.get(chave)
        if a is None:
            continue
        dif = [c for c in db.CAMPOS_SEMEADOS
               if not (c == "nota" and a.get("origem_conclusao") == db.ORIGEM_USUARIO)
               and _comparavel(c, l.get(c)) != _comparavel(c, a.get(c))]
        if dif:
            mudam.append(chave)
            for c in dif:
                campos[c] = campos.get(c, 0) + 1
    return mudam, campos


def semear(apply=False, expect=None, out=print, **fontes):
    """Rito de semeadura. Devolve `(exit_code, linhas, relatorio)`."""
    linhas, rel = montar_linhas(**fontes)
    por_fonte = _contar(linhas, "fonte")
    por_status = _contar(linhas, "status")
    medida = db.plano_upsert_tarefas(linhas, aplicar=False)

    out(f"[plano] semeadura: {len(linhas)} linha(s) montadas das 3 fontes")
    out("  COUNT-ASSERT por fonte:")
    out(f"    extensivo = {por_fonte.get('extensivo', 0)}"
        f"  (S1-S20 {rel['extensivo_s1_s20']} | S21-S48 {rel['extensivo_s21_s48']}"
        f" | S49-S52 {rel['extensivo_s49_s52']})")
    out(f"    rf        = {por_fonte.get('rf', 0)}"
        f"  (pendentes das {rel['rf_total_s17_s28']} tarefas S17-S28)")
    out(f"    custom    = {por_fonte.get('custom', 0)}")
    out("  COUNT-ASSERT por status inicial:")
    for st in db.STATUS_PLANO:
        out(f"    {st:<9} = {por_status.get(st, 0)}")
    out(f"  nao casaram nome no Dashboard: {rel['extensivo_sem_match']}"
        f" tarefa(s) do extensivo -> nascem pendente (nunca feita por inferencia)")
    out(f"  sem area canonica (F89, area=NULL + nota): {rel['extensivo_sem_area']}")
    out(f"  puxadas do extensivo para a Fase 1 (bloco MFC/APS): "
        f"{rel['extensivo_puxadas_fase1']}")
    out(f"  links de lista aplicados (links_listas.json): {rel['links_aplicados']}")
    out(f"  trilha (plano_trilha.json): {rel['trilha_aplicados']} override(s) aplicado(s), "
        f"{rel['trilha_fora']} linha(s) tiradas da Fase 1 por nao estarem nela")
    if rel["trilha_sem_linha"]:
        out(f"  ATENCAO: trilha com {len(rel['trilha_sem_linha'])} override(s) sem linha "
            f"correspondente: {rel['trilha_sem_linha'][:8]}")
    out(f"  no banco: {medida['novas']} nova(s), {medida['existentes']} ja existente(s)")
    mudam, campos = diferenca_semeada(linhas, db.plano_listar())
    rel["mudariam"], rel["mudariam_campos"] = len(mudam), campos
    out(f"  mudariam nos campos semeados: {len(mudam)} linha(s) existente(s)"
        + (f" -- {', '.join(f'{c} {n}' for c, n in sorted(campos.items()))}; ex.: "
           f"{mudam[:3]}" if mudam else " (re-seed idempotente sobre o banco atual)"))

    if not apply:
        out(f"  DRY-RUN: nada gravado. Para aplicar: --semear --apply --expect "
            f"{medida['novas']}")
        return 0, linhas, rel
    if rel["trilha_sem_linha"]:
        out("  RECUSADO: a trilha tem override sem linha correspondente -- o plano pedido "
            "nao e o que seria gravado. Nada gravado.")
        return 2, linhas, rel
    if expect is None or int(expect) != medida["novas"]:
        out(f"  RECUSADO: --expect {expect} != {medida['novas']} nova(s) medida(s). "
            f"Nada gravado.")
        return 2, linhas, rel
    resultado = db.plano_upsert_tarefas(linhas, aplicar=True)
    out(f"  OK: {resultado['novas']} linha(s) inserida(s), "
        f"{resultado['existentes']} atualizada(s) nos campos semeados "
        f"({', '.join(db.CAMPOS_SEMEADOS)}).")
    return 0, linhas, rel


def listar(semana=None, bloco=None, status=None, fonte=None, como_json=False, out=print):
    """Leitura da tabela (read-only)."""
    linhas = db.plano_listar(semana=semana, bloco=bloco, status=status, fonte=fonte)
    if como_json:
        out(json.dumps(linhas, ensure_ascii=False, indent=1))
        return 0, linhas
    if not linhas:
        out("[plano] nenhuma tarefa para o filtro.")
        return 0, linhas
    out(f"[plano] {len(linhas)} tarefa(s)")
    out(f"  {'sem':>3} {'ord':>3}  {'bloco':<5} {'fonte':<9} {'status':<8} "
        f"{'q':>5}  tema")
    for l in linhas:
        sem = "--" if l["semana_plano"] is None else l["semana_plano"]
        ordem = "--" if l["ordem"] is None else l["ordem"]
        q = "--" if l["q_previstas"] is None else f"{l['q_previstas']:.0f}"
        out(f"  {sem:>3} {ordem:>3}  {l['bloco']:<5} {l['fonte']:<9} {l['status']:<8} "
            f"{q:>5}  {l['area'] or '(sem area)'} | {l['tema']}")
    return 0, linhas


# ------------------------------------------------------------ reserva (s189)

#: Faixa de incidencia UERJ do `prevalencia_uerj.json` (alta >= 4 questoes, media 2-3, baixa 1).
ORDEM_FAIXA = {"alta": 0, "media": 1, "baixa": 2}


def _grupo_reserva(nota):
    nota = nota or ""
    if NOTA_FORA_DA_TRILHA in nota:
        return "fora da trilha"
    if NOTA_RESERVA in nota:
        return "reserva do extensivo"
    return "sem semana"


def reserva(linhas, prevalencia, estados=None):
    """Linhas PENDENTES fora da fila (`semana_plano` NULL) x peso UERJ. PURA.

    s189 (fatia 2 do /ai-eng): a `fase1_exclusiva` tira linhas da fila e nenhum fluxo as le --
    forma "sem consulta" por construcao; o tema de alta incidencia pode sumir sem ninguem ver.
    Cruza dois dados que ja existiam: as linhas e o `prevalencia_uerj.json`. Casamento pelo
    MESMO `casa` do gerador (`tools/trilha.py`, limite (d)): linha que nao casa sai com
    `temas_uerj=[]` e `faixa=None` -- nao-medida, nunca peso zero silencioso. Ordena por peso
    desc, nao casadas por ultimo. `na_fila_por` = as linhas AGENDADAS na Fase 1 que ja cobrem o
    mesmo tema UERJ (o risco real e a faixa alta sem nenhuma). `estados` (opcional) =
    `{(area, tema): ZERO|TOCADO|PARCIAL|FEITO}` da reconciliacao do gerador -- diz POR QUE a
    trilha deixou a linha de fora (tema ja feito x nunca estudado)."""
    import trilha
    temas = [(t["area"], trilha.toks(t["tema"]), t)
             for t in (prevalencia or {}).get("temas") or []]

    def casados_de(l):
        partes = ([trilha.toks(x) for x in trilha.partes_da_tarefa(l.get("tema"))]
                  or [trilha.toks(l.get("tema"))])
        return [t for a, tk, t in temas
                if a == l.get("area") and any(trilha.casa(tk, p) for p in partes)]

    # quem JA cobre cada tema UERJ na fila da Fase 1: tema em reserva que outra linha agendada
    # cobre nao sumiu -- o risco real e o tema de faixa alta sem NENHUMA linha na fila
    na_fila = {}
    for l in linhas:
        if l.get("semana_plano") in SEMANAS_FASE1 and l.get("status") != "cortada":
            for t in casados_de(l):
                na_fila.setdefault((t["area"], t["tema"]), []).append(
                    (l.get("id"), l.get("semana_plano")))
    saida = []
    for l in linhas:
        if l.get("status") != "pendente" or l.get("semana_plano") is not None:
            continue
        casados = casados_de(l)
        faixas = sorted({t["prevalencia"] for t in casados}, key=lambda f: ORDEM_FAIXA.get(f, 9))
        cobertura = sorted({x for t in casados for x in na_fila.get((t["area"], t["tema"]), [])},
                           key=lambda x: (x[1], x[0] or 0))
        saida.append({
            "id": l.get("id"), "fonte": l.get("fonte"),
            "ref_semana_fonte": l.get("ref_semana_fonte"), "tarefa_fonte": l.get("tarefa_fonte"),
            "area": l.get("area"), "tema": l.get("tema"), "tipo": l.get("tipo"),
            "q_previstas": l.get("q_previstas"), "grupo": _grupo_reserva(l.get("nota")),
            "temas_uerj": [t["tema"] for t in casados],
            "n_uerj": sum(t["n"] for t in casados),
            "peso_uerj": round(sum(t["peso"] for t in casados), 1),
            "faixa": faixas[0] if faixas else None,
            "na_fila_por": [{"id": i, "semana": s} for i, s in cobertura],
            "estado": sorted({(estados or {}).get((t["area"], t["tema"])) or "?"
                              for t in casados}) if estados is not None else [],
        })
    saida.sort(key=lambda x: (not x["temas_uerj"], -x["peso_uerj"], x["grupo"], x["id"] or 0))
    return saida


def _estados_da_trilha():
    """`{(area, tema): estado}` da reconciliacao do gerador (`tools/trilha.py`), sobre a entrada
    fixada. Falha -> `None` + WARN: a coluna sai `--`, a reserva nao cai."""
    try:
        import trilha
        params = trilha.carregar_parametros()
        e = trilha.carregar_entrada(params)
        temas = trilha.pontuar(trilha.reconciliar(e["mapa"], e["catalogo"], e["dashboard"],
                                                  e["cobertura"]), e["mapa"], params)
        return {(t["area"], t["tema"]): t["estado"] for t in temas}
    except Exception as erro:                    # noqa: BLE001 -- degrada visivel
        print(f"[WARN] reserva: estado da trilha indisponivel ({erro})", file=sys.stderr)
        return None


def _celula(valor):
    return str(valor if valor not in (None, "") else "--").replace("|", "\\|")


def _tabela_reserva(itens):
    saida = ["| id | grupo | area | tarefa | tipo | q | UERJ n (peso) | faixa | tema(s) UERJ "
             "| tema ja na fila por | estado (18/09) |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in itens:
        q = "--" if x["q_previstas"] is None else f"{float(x['q_previstas']):.0f}"
        fila = ", ".join(f"#{c['id']} (S{c['semana']})" for c in x["na_fila_por"][:4])
        if len(x["na_fila_por"]) > 4:
            fila += f" +{len(x['na_fila_por']) - 4}"
        saida.append("| #%s | %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s |" % (
            x["id"], x["grupo"], _celula(x["area"]), _celula(x["tema"]), _celula(x["tipo"]), q,
            x["n_uerj"], x["peso_uerj"], _celula(x["faixa"]), _celula("; ".join(x["temas_uerj"])),
            _celula(fila or "NENHUMA"), _celula("/".join(x["estado"]))))
    return saida


def render_reserva(itens, hoje):
    """A reserva em Markdown, para o operador ler UMA vez (o gate e o olho, nao o aviso)."""
    altas = [x for x in itens if x["faixa"] == "alta"]
    orfas = [x for x in altas if not x["na_fila_por"]]
    casadas = [x for x in itens if x["temas_uerj"]]
    sem_par = [x for x in itens if not x["temas_uerj"]]
    grupos = {}
    for x in itens:
        grupos[x["grupo"]] = grupos.get(x["grupo"], 0) + 1
    out = [
        "# Reserva da Fase 1 -- linhas pendentes FORA da fila",
        "",
        f"> Gerado por `python tools/plano.py --reserva` em {hoje}. Nao editar: regenerar. Para "
        f"o operador ler UMA vez (fatia 2 do `/ai-eng`, s189): o gate e o olho, nao o aviso. "
        f"Terminal datado: 02/11/2026, junto do F111.",
        "",
        f"**{len(itens)} linha(s) pendente(s) sem semana** -- "
        + ", ".join(f"{n} {g}" for g, n in sorted(grupos.items()))
        + f". **{len(altas)} em faixa ALTA** da UERJ (tema com >= 4 questoes em 2021-2026), "
        f"das quais **{len(orfas)} sem NENHUMA linha na fila da Fase 1 cobrindo o tema** (o risco "
        f"real: as outras tem o tema agendado por outra tarefa, coluna `tema ja na fila por`); "
        f"{len(sem_par)} sem tema casado na prevalencia.",
        "",
        "Como ler: `UERJ n (peso)` = questoes das provas UERJ 2021-2026 nos temas que a tarefa "
        "cobre (2021-2022 valem 0,7 no peso). `fora da trilha` = a trilha da Fase 1 nao a "
        "escolheu (`fase1_exclusiva`); `reserva do extensivo` = S1-S20 do extensivo, fora do "
        "plano por regra da part-2. `estado (18/09)` = como o gerador da trilha via o tema "
        "(ZERO nunca estudado, TOCADO, PARCIAL, FEITO) -- e o porque da exclusao: a prioridade e "
        "peso UERJ x lacuna. Para trazer uma linha para a Fase 1: entrada em "
        "`core/cronograma/trilha/custom.json` (com `racional`) + `python tools/trilha.py "
        "--gravar` + `python tools/plano.py --semear --dry-run`.",
        "",
    ]
    if orfas:
        out += ["## 🔴 Faixa ALTA sem nenhuma linha na fila -- conferir primeiro", ""] +             _tabela_reserva(orfas) + [""]
    cobertas = [x for x in altas if x["na_fila_por"]]
    if cobertas:
        out += ["## ⚠️ Faixa ALTA com o tema ja na fila por outra tarefa", ""] +             _tabela_reserva(cobertas) + [""]
    out += ["## Todas as casadas, por peso UERJ", ""] + _tabela_reserva(casadas) + [""]
    if sem_par:
        out += ["## Sem tema casado na prevalencia UERJ -- conferir a olho", "",
                "O casamento e por tokens (o mesmo do gerador da trilha): linha aqui NAO tem peso "
                "zero, tem peso NAO MEDIDO.", ""] + _tabela_reserva(sem_par) + [""]
    return "\n".join(out)


# ---------------------------------------------------------- panorama (s190)

#: O QUE FAZER com uma tarefa pendente, derivado de CAMPOS (`url_lista`, `q_previstas`,
#: `fonte`) -- nunca de substring da `nota`, que e prosa e muda de redacao. A ordem e a de
#: leitura: a classe mais pronta primeiro.
CLASSES_PANORAMA = {
    "lista": "lista pronta -- abrir o link",
    "caderno": "sem link, com questoes previstas -- montar o caderno no banco do EMED pelo filtro",
    "aula": "aula-base do agente (tarefa custom, sem lista no EMED)",
    "sem_lista": "sem link de lista -- aula-base + 10-15 questoes do banco pelo filtro do tema",
}

#: Quantas tarefas em aberto o panorama lista por extenso; o resto sai CONTADO, com o comando.
PANORAMA_TAREFAS = 12

AREA_SIMULADO = "Simulado"


def classe_da_tarefa(linha):
    """Classe de `CLASSES_PANORAMA` de uma linha de `plano_tarefas`. PURA."""
    if linha.get("url_lista"):
        return "lista"
    try:
        q = float(linha.get("q_previstas") or 0)
    except (TypeError, ValueError):
        q = 0
    if q > 0:
        return "caderno"
    return "aula" if linha.get("fonte") == "custom" else "sem_lista"


def _q(linha):
    try:
        return int(round(float(linha.get("q_previstas") or 0)))
    except (TypeError, ValueError):
        return 0


def _por_classe(linhas):
    contagem = {c: 0 for c in CLASSES_PANORAMA}
    for l in linhas:
        contagem[classe_da_tarefa(l)] += 1
    return contagem


def panorama(linhas, calendario, hoje):
    """O plano EM ABERTO como o operador precisa ler no boot. PURA.

    s190 (pedido do operador, 20/09/2026): ele abriu os artifacts, viu tarefa sem lista e nao
    soube o que fazer nem qual era a ordem dos simulados -- a informacao existia no banco e
    nenhuma tela a entregava junta. Aqui ela sai de `plano_tarefas` + calendario da trilha:

    - `semana`: a de CALENDARIO (primeira cujo `fim` >= hoje), a mesma regua da cota do
      `day_plan`; sem calendario, ou depois do fim dele, cai para a POSICAO do plano (menor
      semana com pendencia) e `inicio`/`fim` saem `None` -- nunca data inventada;
    - `abertas`: pendentes da semana e de semana ANTERIOR (`atrasada`), na ordem do plano,
      cada uma com a `classe` (o que fazer com ela);
    - `simulados`: a sequencia de provas da Fase 1 com o status de cada uma;
    - `proxima`: a semana seguinte, contada por classe;
    - `fase1`: a fila inteira da Fase 1, contada por classe.

    Reserva (semana NULL) e Fase 2 alem da proxima semana ficam de fora: e panorama de
    execucao, nao inventario (`--reserva` e `--listar` sao os inventarios)."""
    vivas = [l for l in linhas if l.get("semana_plano") is not None
             and l.get("status") != "cortada"]
    pendentes = [l for l in vivas if l.get("status") == "pendente"]
    futuras = [s for s in sorted(calendario or {}) if calendario[s][1] >= hoje]
    if futuras:
        semana = futuras[0]
        inicio, fim = calendario[semana]
        dias = (fim - max(hoje, inicio)).days + 1
    else:
        semanas = sorted({l["semana_plano"] for l in pendentes})
        semana, inicio, fim, dias = (semanas[0] if semanas else None), None, None, None
    if semana is None:
        return None

    # a ordem DENTRO da semana e a do leitor (`db.plano_listar`), a mesma que o `day_plan`
    # mostra: sort estavel so por semana -- uma segunda regra de ordem seria outra autoridade
    chave = lambda l: l["semana_plano"]
    abertas = sorted((l for l in pendentes if l["semana_plano"] <= semana), key=chave)
    da_semana = [l for l in vivas if l["semana_plano"] == semana]
    seguinte = [l for l in pendentes if l["semana_plano"] == semana + 1]
    fase1 = [l for l in pendentes if l["semana_plano"] in SEMANAS_FASE1]
    sims = sorted((l for l in vivas if l.get("area") == AREA_SIMULADO
                   and l["semana_plano"] in SEMANAS_FASE1), key=chave)

    def item(l):
        return {"id": l.get("id"), "semana": l["semana_plano"],
                "atrasada": l["semana_plano"] < semana, "bloco": l.get("bloco"),
                "area": l.get("area"), "tema": l.get("tema"), "q": _q(l),
                "classe": classe_da_tarefa(l), "url_lista": l.get("url_lista"),
                "nota": l.get("nota")}

    cal_seg = (calendario or {}).get(semana + 1)
    return {
        "hoje": hoje.isoformat(), "semana": semana,
        "inicio": inicio.isoformat() if inicio else None,
        "fim": fim.isoformat() if fim else None, "dias": dias,
        "feitas_semana": sum(1 for l in da_semana if l.get("status") == "feita"),
        "tarefas_semana": len(da_semana),
        "abertas": [item(l) for l in abertas],
        "q_abertas": sum(_q(l) for l in abertas),
        "atrasadas": sum(1 for l in abertas if l["semana_plano"] < semana),
        "classes_abertas": _por_classe(abertas),
        "simulados": [{"id": l.get("id"), "semana": l["semana_plano"], "tema": l.get("tema"),
                       "q": _q(l), "status": l.get("status"),
                       "url_lista": l.get("url_lista")} for l in sims],
        "proxima": {"semana": semana + 1,
                    "inicio": cal_seg[0].isoformat() if cal_seg else None,
                    "fim": cal_seg[1].isoformat() if cal_seg else None,
                    "tarefas": len(seguinte), "q": sum(_q(l) for l in seguinte),
                    "classes": _por_classe(seguinte)} if seguinte else None,
        "fase1": {"tarefas": len(fase1), "q": sum(_q(l) for l in fase1),
                  "classes": _por_classe(fase1)},
    }


def _dm(iso):
    return f"{iso[8:10]}/{iso[5:7]}" if iso else "?"


def _classes_em_texto(classes):
    rotulo = {"lista": "com lista", "caderno": "caderno a criar", "aula": "aula-base",
              "sem_lista": "sem lista"}
    return ", ".join(f"{n} {rotulo[c]}" for c, n in classes.items() if n) or "nenhuma"


def _nome_curto(tema):
    return (tema or "(sem tema)").split(" -- ")[0].split(" (")[0][:48]


def render_panorama(p):
    """O panorama em Markdown compacto -- e o que o hook de boot injeta."""
    if not p:
        return "## 🧭 Panorama do plano\n- plano sem tarefa pendente em semana atribuida."
    janela = (f" ({_dm(p['inicio'])} -> {_dm(p['fim'])}, {p['dias']} dia(s) com hoje)"
              if p["inicio"] else " (fora do calendario da trilha: posicao pelo plano)")
    atraso = f" · **{p['atrasadas']} atrasada(s)** de semana anterior" if p["atrasadas"] else ""
    out = [f"## 🧭 Panorama do plano -- semana {p['semana']}{janela}",
           f"- **Em aberto:** {len(p['abertas'])} tarefa(s) · {p['q_abertas']}q{atraso} · "
           f"{p['feitas_semana']}/{p['tarefas_semana']} feitas na semana · "
           f"{_classes_em_texto(p['classes_abertas'])}"]
    sims = p["simulados"]
    if sims:
        feitos = sum(1 for s in sims if s["status"] == "feita")
        prox = next((s for s in sims if s["status"] == "pendente"), None)
        seq = " -> ".join(("~~%s~~" if s["status"] == "feita" else "%s")
                          % f"S{s['semana']} {_nome_curto(s['tema'])}" for s in sims)
        da_vez = (f" · **da vez: {_nome_curto(prox['tema'])}** ({prox['q']}q"
                  + (f", {prox['url_lista']}" if prox["url_lista"] else ", SEM link")
                  + ")") if prox else ""
        out.append(f"- **Simulados da Fase 1:** {feitos}/{len(sims)} feitos{da_vez} · {seq}")
    out.append("- **Tarefas em aberto (ordem do plano):**")
    for i, t in enumerate(p["abertas"][:PANORAMA_TAREFAS], 1):
        marca = f" [S{t['semana']} atrasada]" if t["atrasada"] else ""
        q = f" · {t['q']}q" if t["q"] else ""
        if t["classe"] == "lista":
            acao = f"lista: {t['url_lista']}"
        else:
            nota = f" -- {t['nota'][:110]}" if t.get("nota") else ""
            acao = f"**{t['classe']}**{nota}"
        out.append(f"    {i}. #{t['id']}{marca} [{t['bloco'] or '?'}] {t['area'] or '?'} | "
                   f"{(t['tema'] or '(sem tema)')[:70]}{q} · {acao}")
    resto = len(p["abertas"]) - PANORAMA_TAREFAS
    if resto > 0:
        out.append(f"    • +{resto} tarefa(s) em aberto "
                   f"(`python tools/plano.py --listar --semana {p['semana']} --status pendente`)")
    nx = p["proxima"]
    if nx:
        quando = f", {_dm(nx['inicio'])} -> {_dm(nx['fim'])}" if nx["inicio"] else ""
        out.append(f"- **Proxima semana (S{nx['semana']}{quando}):** {nx['tarefas']} tarefa(s) · "
                   f"{nx['q']}q · {_classes_em_texto(nx['classes'])}")
    f1 = p["fase1"]
    out.append(f"- **Fase 1 inteira:** {f1['tarefas']} pendente(s) · {f1['q']}q · "
               f"{_classes_em_texto(f1['classes'])}")
    usadas = [c for c in CLASSES_PANORAMA if c != "lista" and f1["classes"].get(c)]
    if usadas:
        out.append("- **Legenda:** " + "; ".join(f"`{c}` = {CLASSES_PANORAMA[c]}"
                                                 for c in usadas))
    return "\n".join(out)


# ------------------------------------------------- progresso (part-3): helpers

def ids_da_lista(texto):
    """`"1, 4,9"` -> `[1, 4, 9]`. Vazio -> `[]`. Item nao inteiro LEVANTA (silenciar
    um id malformado seria confirmar a area sem a linha que o usuario apontou)."""
    itens = [p.strip() for p in str(texto or "").replace(";", ",").split(",") if p.strip()]
    saida = []
    for item in itens:
        if not item.isdigit():
            raise ValueError(f"id invalido na lista: {item!r} (esperado inteiro positivo)")
        saida.append(int(item))
    return saida


def data_valida(texto):
    """`AAAA-MM-DD` -> a propria string. Formato errado LEVANTA nomeando o esperado."""
    try:
        datetime.strptime(str(texto), "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValueError(f"data invalida: {texto!r} (esperado AAAA-MM-DD)")
    return str(texto)


def compor_nota_corte(nota_atual, motivo):
    """Motivo do corte ANEXADO a nota, nunca no lugar dela: a nota da semeadura carrega
    marcas que ninguem pode perder (`q_estimada`, `area_fonte=...`). Corte repetido
    SUBSTITUI o motivo anterior em vez de empilhar. Funcao pura.

    🔴 `nota` esta em `db.CAMPOS_SEMEADOS`: um `--semear --apply` futuro reescreve a
    nota e o motivo do corte se perde (o `status='cortada'` sobrevive, esse fica fora
    do UPDATE). Divida declarada -- o motivo e explicacao, nao o dado de controle.
    """
    pedacos = [p.strip() for p in str(nota_atual or "").split(";")
               if p.strip() and not p.strip().casefold().startswith("corte:")]
    return "; ".join(pedacos + [f"corte: {str(motivo).strip()}"])


def _origem_curta(valor):
    """Rotulo de coluna: `dash` (aproximado), `usuario`, `--` (nunca afirmado)."""
    if not valor:
        return "--"
    return "dash" if valor == db.ORIGEM_APROXIMADA else str(valor)


def _sem_fonte(linha):
    ref = linha.get("ref_semana_fonte")
    return "--" if not ref else f"S{ref}"


def _linha_conferencia(l):
    return (f"  {l['id']:>5} {l['fonte'][:3]:<4} {_sem_fonte(l):>4}  "
            f"{l['status']:<8} {_origem_curta(l['origem_conclusao']):<8} "
            f"{(l['tipo'] or '--')[:20]:<20}  {l['tema'] or '(sem tema)'}")


# ------------------------------------------------- progresso (part-3): comandos

def concluir(tarefa_id, sessao, data=None, out=print):
    """`--concluir`: a tarefa foi feita, e o volume dela esta em `sessoes_bulk`."""
    resumo = db.sessao_bulk_resumo(sessao)
    if resumo is None:
        out(f"[plano] RECUSADO: sessao {sessao} nao existe em sessoes_bulk. "
            f"`--sessao` e o ID da linha, nao o `sessao_num`.")
        out(f"  Registre o volume primeiro (tools/registrar_sessao_bulk.py, assinatura "
            f"em /importar-planilha) e repita: --concluir {tarefa_id} --sessao <id>.")
        return 2, None
    try:
        quando = data_valida(data) if data else db.hoje().isoformat()
        resultado = db.plano_set_status(tarefa_id, "feita", sessao_bulk_id=int(sessao),
                                        data_conclusao=quando,
                                        origem_conclusao=db.ORIGEM_USUARIO)
    except ValueError as e:
        out(f"[plano] RECUSADO: {e}")
        return 2, None
    if resultado is None:
        out(f"[plano] RECUSADO: tarefa {tarefa_id} nao existe em plano_tarefas. "
            f"Confira o id com: python tools/plano.py --listar --semana N")
        return 2, None
    d = resultado["depois"]
    out(f"[plano] OK: tarefa {d['id']} FEITA em {quando} "
        f"({d['area'] or '(sem area)'} | {d['tema']})")
    out(f"  sessao {resumo['id']}: bloco #{resumo['sessao_num']} de {resumo['area']} em "
        f"{resumo['data_sessao']}, {resumo['questoes_feitas']}q "
        f"({resumo['questoes_acertadas']} acertos)")
    out(f"  origem_conclusao: {resultado['antes']['origem_conclusao'] or '--'} -> "
        f"{d['origem_conclusao']}")
    return 0, resultado


def concluir_leitura(tarefa_id, data=None, out=print):
    """`--concluir ID --leitura` (s194, decisao do operador): tarefa de AULA -- sem
    lista e sem questoes previstas -- fica feita pela leitura confirmada (o "feito" do
    quadro de aulas do hub), sem bloco em `sessoes_bulk`, porque nao ha volume a
    vincular. Tarefa com lista ou com questoes previstas e recusada: leitura nao
    substitui o bloco de questoes."""
    tarefa = db.plano_obter(tarefa_id)
    if tarefa is None:
        out(f"[plano] RECUSADO: tarefa {tarefa_id} nao existe em plano_tarefas.")
        return 2, None
    if tarefa.get("url_lista") or (tarefa.get("q_previstas") or 0) > 0:
        out(f"[plano] RECUSADO: tarefa {tarefa_id} tem lista ou questoes previstas -- "
            f"--leitura so vale para aula. Registre o bloco e use --concluir "
            f"{tarefa_id} --sessao <id>.")
        return 2, None
    try:
        quando = data_valida(data) if data else db.hoje().isoformat()
        resultado = db.plano_set_status(tarefa_id, "feita", data_conclusao=quando,
                                        origem_conclusao=db.ORIGEM_USUARIO)
    except ValueError as e:
        out(f"[plano] RECUSADO: {e}")
        return 2, None
    d = resultado["depois"]
    out(f"[plano] OK: tarefa {d['id']} FEITA em {quando} por leitura "
        f"({d['area'] or '(sem area)'} | {d['tema']}) -- sem bloco de questoes")
    return 0, resultado


def cortar(tarefa_id, motivo, out=print):
    """`--cortar`: a tarefa sai do plano, e o motivo fica escrito na linha."""
    motivo = (motivo or "").strip()
    if not motivo:
        out("[plano] RECUSADO: --cortar exige --motivo \"...\". Corte sem motivo "
            "e tema que some do plano sem ninguem saber por que.")
        return 2, None
    atual = db.plano_obter(tarefa_id)
    if atual is None:
        out(f"[plano] RECUSADO: tarefa {tarefa_id} nao existe em plano_tarefas. "
            f"Confira o id com: python tools/plano.py --listar --semana N")
        return 2, None
    resultado = db.plano_set_status(tarefa_id, "cortada",
                                    origem_conclusao=db.ORIGEM_USUARIO,
                                    nota=compor_nota_corte(atual.get("nota"), motivo))
    d = resultado["depois"]
    out(f"[plano] OK: tarefa {d['id']} CORTADA ({d['area'] or '(sem area)'} | {d['tema']})")
    out(f"  nota: {d['nota']}")
    return 0, resultado


def _trava_da_trilha(atual, semana, trilha):
    """Motivo de recusa do `--mover` com a trilha ativa, ou `None`. PURA.

    s189 (F120, fatia 4 do /ai-eng): com `fase1_exclusiva`, `semana_plano`/`ordem` da Fase 1
    sao reescritos pelo proximo re-seed -- o `--mover` reportava sucesso e o efeito sumia (CLI
    que mente). A Fase 1 tem UMA autoridade: linha que ESTA nela, ou que iria PARA ela, e
    recusada no ponto da mutacao, com a entrada exata da camada manual no lugar."""
    if not (trilha or {}).get("fase1_exclusiva"):
        return None
    de, para = atual.get("semana_plano"), int(semana)
    if de not in SEMANAS_FASE1 and para not in SEMANAS_FASE1:
        return None
    entrada = (f'{{"fonte": "{atual.get("fonte")}", "ref_semana_fonte": '
               f'{atual.get("ref_semana_fonte")}, "tarefa_fonte": {atual.get("tarefa_fonte")}, '
               f'"semana_plano": {para}, "ordem": N, "racional": "..."}}')
    return (f"a trilha da Fase 1 esta ativa (fase1_exclusiva) e a tarefa {atual.get('id')} "
            f"{'esta' if de in SEMANAS_FASE1 else 'iria'} na Fase 1 (semana {de or '--'} -> "
            f"{para}): o proximo re-seed desfaria o --mover. Caminho que dura: acrescentar em "
            f"core/cronograma/trilha/custom.json a entrada {entrada} e rodar "
            f"`python tools/trilha.py --gravar` + `python tools/plano.py --semear --dry-run`.")


def mover(tarefa_id, semana, ordem=None, out=print, trilha=None):
    """`--mover`: replanejar semana/ordem sem tocar em status (substitui o ritual de
    reordenar o xlsx do Drive a mao). `trilha=None` le o `plano_trilha.json` do disco; os
    testes do banco sintetico injetam `{}`. Com a trilha ativa, linha da Fase 1 e RECUSADA
    (`_trava_da_trilha`)."""
    if trilha is None:
        trilha = _ler(P_TRILHA) if os.path.exists(P_TRILHA) else {}
    atual = db.plano_obter(tarefa_id)
    if atual is not None and semana is not None:
        try:
            motivo = _trava_da_trilha(atual, semana, trilha)
        except (TypeError, ValueError):
            motivo = None                # semana malformada: o writer recusa com a mensagem dele
        if motivo:
            out(f"[plano] RECUSADO: {motivo}")
            return 2, None
    try:
        resultado = db.plano_mover(tarefa_id, semana, ordem=ordem)
    except ValueError as e:
        out(f"[plano] RECUSADO: {e}")
        return 2, None
    if resultado is None:
        out(f"[plano] RECUSADO: tarefa {tarefa_id} nao existe em plano_tarefas. "
            f"Confira o id com: python tools/plano.py --listar --semana N")
        return 2, None
    a, d = resultado["antes"], resultado["depois"]
    out(f"[plano] OK: tarefa {d['id']} movida da semana {a['semana_plano'] or '--'} "
        f"para a {d['semana_plano']} (ordem {a['ordem'] or '--'} -> {d['ordem'] or '--'})")
    out(f"  status inalterado: {d['status']} ({d['area'] or '(sem area)'} | {d['tema']})")
    return 0, resultado


def reabrir(tarefa_id, out=print):
    """`--reabrir`: volta a `pendente` e APAGA o vinculo de conclusao (data/sessao)."""
    resultado = db.plano_set_status(tarefa_id, "pendente",
                                    origem_conclusao=db.ORIGEM_USUARIO)
    if resultado is None:
        out(f"[plano] RECUSADO: tarefa {tarefa_id} nao existe em plano_tarefas. "
            f"Confira o id com: python tools/plano.py --listar --semana N")
        return 2, None
    a, d = resultado["antes"], resultado["depois"]
    out(f"[plano] OK: tarefa {d['id']} REABERTA ({a['status']} -> {d['status']}; "
        f"{d['area'] or '(sem area)'} | {d['tema']})")
    if a["sessao_bulk_id"] or a["data_conclusao"]:
        out(f"  vinculo de conclusao apagado (era sessao {a['sessao_bulk_id'] or '--'} "
            f"em {a['data_conclusao'] or '--'})")
    if d["semana_plano"]:
        out(f"  a tarefa continua na semana {d['semana_plano']}")
    else:
        out("  a tarefa esta SEM semana no plano -- enfileire com "
            f"--mover {d['id']} --semana N")
    return 0, resultado


def revisar_area(area, out=print):
    """`--revisar-area`: lista de CONFERENCIA em blocos de <= 25 linhas (read-only)."""
    from app.utils.areas import AreaInvalida, validar_area
    try:
        area = validar_area(area, origem="plano.py --revisar-area")
    except AreaInvalida as e:
        out(f"[plano] RECUSADO: {e}")
        return 2, []
    # Ordem da FONTE (extensivo S1..S52, depois RF, depois custom), nao a do plano: a
    # conferencia e feita contra o Dashboard/PDF, que estao nessa ordem. Ordenar pela
    # semana do plano obrigaria o usuario a procurar cada linha na planilha.
    linhas = sorted(db.plano_listar(area=area),
                    key=lambda l: (l["fonte"], l["ref_semana_fonte"] or 0,
                                   l["tarefa_fonte"] or 0))
    if not linhas:
        out(f"[plano] nenhuma tarefa da area {area} (o plano foi semeado? "
            f"python tools/plano.py --semear --dry-run)")
        return 0, []
    aprox = [l for l in linhas if l["origem_conclusao"] == db.ORIGEM_APROXIMADA]
    total = len(linhas)
    blocos = (total + BLOCO_REVISAO - 1) // BLOCO_REVISAO
    out(f"[plano] {area}: {total} tarefa(s) | {len(aprox)} ainda com origem aproximada "
        f"({db.ORIGEM_APROXIMADA})")
    for i in range(blocos):
        fatia = linhas[i * BLOCO_REVISAO:(i + 1) * BLOCO_REVISAO]
        out(f"  -- bloco {i + 1}/{blocos}: linhas {i * BLOCO_REVISAO + 1}-"
            f"{i * BLOCO_REVISAO + len(fatia)} de {total} --")
        out(f"  {'id':>5} {'font':<4} {'sem':>4}  {'status':<8} {'origem':<8} "
            f"{'tipo':<20}  tema")
        for l in fatia:
            out(_linha_conferencia(l))
    out(f"  Conferido? Liste o que esta FEITO e o que esta PENDENTE; o resto da area so "
        f"recarimba a origem (a conferencia e a evidencia).")
    out(f'    python tools/plano.py --confirmar-area "{area}" --feitas "" '
        f'--pendentes "" --dry-run')
    return 0, linhas


def confirmar_area(area, feitas="", pendentes="", apply=False, expect=None, out=print):
    """`--confirmar-area`: revisao por area em LOTE, com dry-run + COUNT-ASSERT.

    `N` do `--expect` = linhas da area que serao TOCADAS = a area inteira, porque a
    conferencia carimba `origem_conclusao` ate em quem nao muda de status.
    """
    try:
        ids_f = ids_da_lista(feitas)
        ids_p = ids_da_lista(pendentes)
        medida = db.plano_confirmar_area(area, ids_f, ids_p, aplicar=False)
    except ValueError as e:                     # AreaInvalida herda de ValueError
        out(f"[plano] RECUSADO: {e}")
        return 2, None

    out(f"[plano] confirmar-area {medida['area']}: {medida['alvo']} linha(s) na area")
    out("  COUNT-ASSERT:")
    out(f"    marcar feita      = {medida['feitas']}")
    out(f"    marcar pendente   = {medida['pendentes']}")
    out(f"    so recarimbar     = {medida['so_origem']}  (status inalterado; a "
        f"conferencia e a evidencia)")
    out("    ---------------------------")
    out(f"    linhas tocadas    = {medida['alvo']}  <- este e o N do --expect")
    out(f"  origem hoje: {medida['aproximadas']} aproximada(s), "
        f"{medida['ja_confirmadas']} ja confirmada(s) por {db.ORIGEM_USUARIO}")

    if not apply:
        out(f"  DRY-RUN: nada gravado. Para aplicar, repita com "
            f"--apply --expect {medida['alvo']}")
        return 0, medida
    if expect is None or int(expect) != medida["alvo"]:
        out(f"  RECUSADO: --expect {expect} != {medida['alvo']} linha(s) medida(s) na "
            f"hora. Nada gravado -- rode o --dry-run e use o N impresso.")
        return 2, medida
    final = db.plano_confirmar_area(area, ids_f, ids_p, aplicar=True)
    out(f"  OK: {final['alvo']} linha(s) de {final['area']} com "
        f"origem_conclusao={db.ORIGEM_USUARIO} ({final['feitas']} feita(s), "
        f"{final['pendentes']} pendente(s), {final['so_origem']} sem mudanca de status).")
    restante = db.plano_pendencia_revisao()
    out(f"  falta revisar: {sum(d['aproximadas'] for d in restante)} linha(s) em "
        f"{len(restante)} area(s) -- python tools/plano.py --pendencia-revisao")
    return 0, final


def pendencia_revisao(como_json=False, out=print):
    """`--pendencia-revisao`: quanto falta da passada, por area (read-only). Zero e o
    criterio de sucesso 2 do PRD; o `day_plan.py` (part-4) consome este numero."""
    linhas = sorted(db.plano_pendencia_revisao(),
                    key=lambda d: (PESO_BLOCO.get(d["bloco"], 9), -d["aproximadas"],
                                   d["area"]))
    if como_json:
        out(json.dumps(linhas, ensure_ascii=False, indent=1))
        return 0, linhas
    total = sum(d["aproximadas"] for d in linhas)
    if not linhas:
        out(f"[plano] pendencia de revisao: 0 -- nenhuma linha com origem "
            f"{db.ORIGEM_APROXIMADA}. Passada COMPLETA (criterio 2 do PRD).")
        return 0, linhas
    out(f"[plano] pendencia de revisao: {total} linha(s) com origem aproximada "
        f"({db.ORIGEM_APROXIMADA}) em {len(linhas)} area(s)")
    out(f"  {'bloco':<6} {'area':<14} {'aprox':>6} {'total':>6}")
    for d in linhas:
        out(f"  {d['bloco']:<6} {d['area']:<14} {d['aproximadas']:>6} {d['total']:>6}")
    out(f"  {'TOTAL':<6} {'':<14} {total:>6}")
    out(f"  Ordem de ataque = peso do bloco na UERJ. Proxima: "
        f'python tools/plano.py --revisar-area "{linhas[0]["area"]}"')
    return 0, linhas


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Plano de estudo como dado (plano_tarefas): semeadura, listagem "
                    "e progresso (concluir/cortar/mover/revisar por area).")
    ap.add_argument("--semear", action="store_true",
                    help="semeia plano_tarefas das 3 fontes (dry-run por default)")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicita o default do --semear: conta e imprime, nao grava")
    ap.add_argument("--apply", action="store_true", help="grava (exige --expect N)")
    ap.add_argument("--expect", type=int,
                    help="COUNT-ASSERT: N de linhas NOVAS esperadas; difere -> exit 2")
    ap.add_argument("--listar", action="store_true", help="lista a tabela (read-only)")
    ap.add_argument("--semana", type=int,
                    help="filtro do --listar: semana do plano; alvo do --mover")
    ap.add_argument("--bloco", choices=["MFC", "PED", "CIR", "GO", "CM"],
                    help="filtro: bloco de peso UERJ (derivado da area)")
    ap.add_argument("--status", choices=list(db.STATUS_PLANO), help="filtro: status")
    ap.add_argument("--fonte", choices=list(db.FONTES_PLANO), help="filtro: fonte")
    ap.add_argument("--json", action="store_true",
                    help="saida do --listar / --pendencia-revisao / --reserva / --panorama em JSON")
    ap.add_argument("--concluir", type=int, metavar="ID",
                    help="marca a tarefa como feita (exige --sessao, ou --leitura em tarefa de aula)")
    ap.add_argument("--leitura", action="store_true",
                    help="--concluir de tarefa de AULA (sem lista e sem questoes previstas) "
                         "pela leitura confirmada, sem bloco em sessoes_bulk")
    ap.add_argument("--sessao", type=int, metavar="N",
                    help="id da linha em sessoes_bulk (NAO o sessao_num); precisa existir")
    ap.add_argument("--data", metavar="AAAA-MM-DD",
                    help="data de conclusao do --concluir (default: hoje)")
    ap.add_argument("--cortar", type=int, metavar="ID",
                    help="tira a tarefa do plano (exige --motivo)")
    ap.add_argument("--motivo", help="por que a tarefa foi cortada; vai para a nota")
    ap.add_argument("--mover", type=int, metavar="ID",
                    help="regrava semana/ordem da tarefa (exige --semana)")
    ap.add_argument("--ordem", type=int, metavar="K",
                    help="ordem dentro da semana no --mover (default: preserva)")
    ap.add_argument("--reabrir", type=int, metavar="ID",
                    help="volta a tarefa para pendente e apaga o vinculo de conclusao")
    ap.add_argument("--revisar-area", metavar="AREA",
                    help="lista de conferencia da area em blocos de 25 (read-only)")
    ap.add_argument("--confirmar-area", metavar="AREA",
                    help="revisao da area em lote (dry-run por default; --apply exige "
                         "--expect N)")
    ap.add_argument("--feitas", default="",
                    help='ids do --confirmar-area que estao FEITOS (ex.: "1,4,9")')
    ap.add_argument("--pendentes", default="",
                    help='ids do --confirmar-area que estao PENDENTES (ex.: "2,3")')
    ap.add_argument("--pendencia-revisao", action="store_true",
                    help="quantas linhas ainda tem origem aproximada, por area (read-only)")
    ap.add_argument("--reserva", action="store_true",
                    help="linhas pendentes FORA da fila (semana NULL) por peso UERJ, com aviso de "
                         "faixa alta -- Markdown no stdout (read-only)")
    ap.add_argument("--panorama", action="store_true",
                    help="o plano EM ABERTO para o boot: semana de calendario, tarefas pendentes "
                         "com o que fazer em cada (lista / caderno / aula / sem_lista), sequencia "
                         "de simulados, proxima semana -- Markdown no stdout (read-only)")
    args = ap.parse_args(argv)

    modos = {
        "--semear": args.semear,
        "--listar": args.listar,
        "--concluir": args.concluir is not None,
        "--cortar": args.cortar is not None,
        "--mover": args.mover is not None,
        "--reabrir": args.reabrir is not None,
        "--revisar-area": bool(args.revisar_area),
        "--confirmar-area": bool(args.confirmar_area),
        "--pendencia-revisao": args.pendencia_revisao,
        "--reserva": args.reserva,
        "--panorama": args.panorama,
    }
    ligados = [nome for nome, ativo in modos.items() if ativo]
    if len(ligados) != 1:
        ap.error("informe exatamente UM modo (" + " | ".join(modos) + "); recebido: "
                 + (", ".join(ligados) if ligados else "nenhum"))
    if args.apply and args.dry_run:
        ap.error("--apply e --dry-run sao mutuamente exclusivos")
    modo = ligados[0]

    if modo == "--semear":
        if args.apply and args.expect is None:
            ap.error("--apply exige --expect N")
        code, _, _ = semear(apply=args.apply, expect=args.expect)
        return code
    if modo == "--concluir":
        if args.leitura:
            if args.sessao is not None:
                ap.error("--leitura e --sessao sao mutuamente exclusivos")
            code, _ = concluir_leitura(args.concluir, data=args.data)
            return code
        if args.sessao is None:
            ap.error("--concluir exige --sessao N (o id da linha em sessoes_bulk), ou "
                     "--leitura para tarefa de aula")
        code, _ = concluir(args.concluir, args.sessao, data=args.data)
        return code
    if modo == "--cortar":
        code, _ = cortar(args.cortar, args.motivo)
        return code
    if modo == "--mover":
        if args.semana is None:
            ap.error("--mover exige --semana N")
        code, _ = mover(args.mover, args.semana, ordem=args.ordem)
        return code
    if modo == "--reabrir":
        code, _ = reabrir(args.reabrir)
        return code
    if modo == "--revisar-area":
        code, _ = revisar_area(args.revisar_area)
        return code
    if modo == "--confirmar-area":
        if args.apply and args.expect is None:
            ap.error("--apply exige --expect N")
        code, _ = confirmar_area(args.confirmar_area, feitas=args.feitas,
                                 pendentes=args.pendentes, apply=args.apply,
                                 expect=args.expect)
        return code
    if modo == "--pendencia-revisao":
        code, _ = pendencia_revisao(como_json=args.json)
        return code
    if modo == "--reserva":
        prev = _ler(P_PREVALENCIA) if os.path.exists(P_PREVALENCIA) else {"temas": []}
        itens = reserva(db.plano_listar(), prev, estados=_estados_da_trilha())
        if args.json:
            print(json.dumps(itens, ensure_ascii=False, indent=1))
        else:
            print(render_reserva(itens, db.hoje().isoformat()))
        orfas = sum(1 for x in itens if x["faixa"] == "alta" and not x["na_fila_por"])
        if orfas:
            print(f"[WARN] RESERVA: {orfas} linha(s) de faixa ALTA da UERJ sem NENHUMA linha na "
                  f"fila da Fase 1 cobrindo o tema -- o operador confere a lista uma vez",
                  file=sys.stderr)
        return 0
    if modo == "--panorama":
        pan = panorama(db.plano_listar(), calendario_trilha(), db.hoje())
        print(json.dumps(pan, ensure_ascii=False, indent=1) if args.json
              else render_panorama(pan))
        return 0
    code, _ = listar(semana=args.semana, bloco=args.bloco, status=args.status,
                     fonte=args.fonte, como_json=args.json)
    return code


if __name__ == "__main__":
    sys.exit(main())
