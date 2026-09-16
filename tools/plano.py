#!/usr/bin/env python3
"""plano.py -- o plano de estudo como DADO (`plano_tarefas`): semeadura e listagem.

Spec: `.vibeflow/specs/plano-ssot-e-cards-v2-part-2.md` (PRD plano-ssot-e-cards-v2, P1).
Depende da part-1 (`core/cronograma/grade_extensivo.json`).

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
`--apply` exige `--expect N` e RECUSA (exit 2) se N != o numero medido na hora.

Uso:
    python tools/plano.py --semear --dry-run
    python tools/plano.py --semear --apply --expect 896
    python tools/plano.py --listar --semana 1
    python tools/plano.py --listar --bloco MFC --status pendente --json

Camada fina sobre `app.utils.db` -- nao abre `sqlite3` proprio (toda escrita e
`plano_upsert_tarefas`). Assinatura canonica em `.claude/commands/engenharia-cli.md`.
"""
import argparse
import json
import math
import os
import sys
import unicodedata

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

#: Carimbo da origem do status inicial. Fixo: o snapshot e dado CONGELADO, e a data
#: que importa e a da planilha (modificada em 10/09), nao a da leitura.
ORIGEM_DASHBOARD = "dashboard_2026-09-10"

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


def montar_linhas(extensivo=None, dashboard=None, grade_rf=None, custom=None):
    """As tres fontes -> linhas prontas para `db.plano_upsert_tarefas`, mais o
    relatorio de COUNT-ASSERT. Nada de I/O de banco aqui: puro sobre os JSONs."""
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
                "url_lista": t.get("url_lista"), "q_previstas": q,
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
                "tipo": t["tipo"], "tipo_norm": t["tipo_norm"], "url_lista": None,
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
    }
    return linhas, relatorio


# -------------------------------------------------------------------- comandos

def _contar(linhas, chave):
    saida = {}
    for l in linhas:
        saida[l[chave]] = saida.get(l[chave], 0) + 1
    return saida


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
    out(f"  no banco: {medida['novas']} nova(s), {medida['existentes']} ja existente(s)")

    if not apply:
        out(f"  DRY-RUN: nada gravado. Para aplicar: --semear --apply --expect "
            f"{medida['novas']}")
        return 0, linhas, rel
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


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Plano de estudo como dado (plano_tarefas): semeadura e listagem.")
    ap.add_argument("--semear", action="store_true",
                    help="semeia plano_tarefas das 3 fontes (dry-run por default)")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicita o default do --semear: conta e imprime, nao grava")
    ap.add_argument("--apply", action="store_true", help="grava (exige --expect N)")
    ap.add_argument("--expect", type=int,
                    help="COUNT-ASSERT: N de linhas NOVAS esperadas; difere -> exit 2")
    ap.add_argument("--listar", action="store_true", help="lista a tabela (read-only)")
    ap.add_argument("--semana", type=int, help="filtro: semana do plano")
    ap.add_argument("--bloco", choices=["MFC", "PED", "CIR", "GO", "CM"],
                    help="filtro: bloco de peso UERJ (derivado da area)")
    ap.add_argument("--status", choices=list(db.STATUS_PLANO), help="filtro: status")
    ap.add_argument("--fonte", choices=list(db.FONTES_PLANO), help="filtro: fonte")
    ap.add_argument("--json", action="store_true", help="saida do --listar em JSON")
    args = ap.parse_args(argv)

    if args.semear == args.listar:
        ap.error("informe --semear OU --listar")
    if args.apply and args.dry_run:
        ap.error("--apply e --dry-run sao mutuamente exclusivos")
    if args.semear:
        if args.apply and args.expect is None:
            ap.error("--apply exige --expect N")
        code, _, _ = semear(apply=args.apply, expect=args.expect)
        return code
    code, _ = listar(semana=args.semana, bloco=args.bloco, status=args.status,
                     fonte=args.fonte, como_json=args.json)
    return code


if __name__ == "__main__":
    sys.exit(main())
