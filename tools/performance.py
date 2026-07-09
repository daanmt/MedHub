"""
performance.py
==============
Checagem rápida de performance MedHub.

Imprime em stdout um relatório markdown com 5 blocos:
1. Total acumulado de questões, acertos e performance geral.
2. Meta do mês corrente + ritmo diário necessário.
3. Custo/questão (acumulado + mês corrente) classificado em faixas.
4. Marcos adiante: ENAMED meta-prova (10.000, 13/09), teto/stretch (12.000) e plano dez/2026 (17.000).
5. Áreas fracas (< 75%) e gaps absolutos (0 questões).

Uso:
    python tools/performance.py

Zero flags obrigatórias. Read-only. Stdlib apenas.
"""
import sqlite3
import argparse
import os
import sys
import calendar
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

# Slot agregado de simulado (s098): sinal da predição ENAMED, NÃO volume.
# Decisão s099: simulado não conta como questão "feita" (não polui cronograma/meta).
# Os erros do simulado viram flashcards nos temas reais; a linha fica em sessoes_bulk
# apenas como ponto da série de predição. Toda agregação de volume exclui esta área.
AREA_SIMULADO = "Simulado"
_EXCLUI_SIMULADO = f"area <> '{AREA_SIMULADO}'"

# Meta final coerente com ESTADO.md (reconcile s084): R$ 4.410 / 17.000q = R$ 0,26/q em dez/2026.
META_CUSTO_Q = 0.26

# Ramp oficial pos-reconcile s084 (= Dashboard EMED 2026): mai 3.000 -> dez 17.000.
# investimento e ACUMULADO (+R$ 210/mes). Confirmado contra a aba mensal da planilha.
METAS_MENSAIS = {
    "2026-05": {"meta_acumulada": 3000,  "investimento": 2940.00},
    "2026-06": {"meta_acumulada": 4500,  "investimento": 3150.00},
    "2026-07": {"meta_acumulada": 6250,  "investimento": 3360.00},
    "2026-08": {"meta_acumulada": 8000,  "investimento": 3570.00},
    "2026-09": {"meta_acumulada": 10000, "investimento": 3780.00},
    "2026-10": {"meta_acumulada": 12500, "investimento": 3990.00},
    "2026-11": {"meta_acumulada": 15000, "investimento": 4200.00},
    "2026-12": {"meta_acumulada": 17000, "investimento": 4410.00},
}

# Faixas: (limite_superior_exclusivo, emoji, rotulo)
# A última faixa usa float('inf') como teto.
FAIXAS_CUSTO = [
    (0.26,         "🟢", "Meta (dez/2026)"),
    (0.40,         "🟡", "Ótimo"),
    (0.60,         "🟠", "Bom"),
    (1.00,         "🔴", "Alto"),
    (float('inf'), "🟣", "Crítico"),
]

AREAS_VALIDAS = [
    "Pediatria", "Preventiva", "Cirurgia", "Infecto", "Obstetrícia",
    "Ginecologia", "Gastro", "Endocrino", "Cardiologia", "Psiquiatria",
    "Neurologia", "Nefrologia", "Hemato", "Pneumo", "Dermato",
    "Reumato", "Hepato", "Otorrino", "Ortopedia", "Oftalmo",
]

# (nome, alvo_acumulado, data_da_prova | None)
# Marcos com data ganham projeções de ritmo (RITMOS_PROJECAO) no bloco 2.
# Recalibração s093/099 (docs/plans/s094-ultraplan.md + ESTADO.md): meta-prova = 10.000,
# 12.000 vira teto/stretch. Gatilho de reavaliação em S13 (~12/07): acumulo >=5.600 -> volta
# a 12.000 como meta; <5.200 -> confirma 10.000. Ambos os marcos seguem expostos até lá.
MARCOS = [
    ("ENAMED (meta-prova)", 10000, date(2026, 9, 13)),
    ("ENAMED (teto/stretch)", 12000, date(2026, 9, 13)),
    ("Plano dez/2026 (2o ciclo: UERJ/USP)", 17000, None),
]

# Ritmos diários usados nas projeções dos marcos datados (q/dia).
RITMOS_PROJECAO = (80, 90, 100)


def get_totais(conn):
    cur = conn.cursor()
    cur.execute(f"SELECT SUM(questoes_feitas), SUM(questoes_acertadas) FROM sessoes_bulk WHERE {_EXCLUI_SIMULADO}")
    row = cur.fetchone()
    total_q = row[0] or 0
    total_a = row[1] or 0
    return total_q, total_a


def get_por_area(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT area, SUM(questoes_feitas), SUM(questoes_acertadas)
          FROM sessoes_bulk
         WHERE """ + _EXCLUI_SIMULADO + """
         GROUP BY area
    """)
    resultado = []
    for area, q, a in cur.fetchall():
        q = q or 0
        a = a or 0
        pct = (100.0 * a / q) if q else 0.0
        resultado.append((area, q, a, pct))
    return resultado


def get_questoes_do_mes(conn, mes_yyyy_mm):
    cur = conn.cursor()
    cur.execute(
        f"SELECT SUM(questoes_feitas) FROM sessoes_bulk WHERE {_EXCLUI_SIMULADO} AND strftime('%Y-%m', data_sessao) = ?",
        (mes_yyyy_mm,),
    )
    row = cur.fetchone()
    return row[0] or 0


def classificar_custo(valor):
    for limite, emoji, rotulo in FAIXAS_CUSTO:
        if valor <= limite:
            return emoji, rotulo
    return FAIXAS_CUSTO[-1][1], FAIXAS_CUSTO[-1][2]


def mes_anterior(mes_yyyy_mm):
    ano, mes = mes_yyyy_mm.split("-")
    ano, mes = int(ano), int(mes)
    if mes == 1:
        return f"{ano - 1}-12"
    return f"{ano}-{mes - 1:02d}"


def dias_restantes_no_mes(hoje):
    _, ultimo_dia = calendar.monthrange(hoje.year, hoje.month)
    return max(1, ultimo_dia - hoje.day + 1)


def fmt_moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def bloco_total(total_q, total_a):
    if total_q == 0:
        return [
            "## 1. Total acumulado",
            "",
            "Nenhuma questão registrada em `sessoes_bulk`.",
        ]
    pct = 100.0 * total_a / total_q
    return [
        "## 1. Total acumulado",
        "",
        f"- **Questões feitas:** {total_q}",
        f"- **Acertos:** {total_a}",
        f"- **Performance geral:** {pct:.1f}%",
    ]


def bloco_meta_mes(mes_atual, total_q, hoje):
    if mes_atual not in METAS_MENSAIS:
        return [
            "## 3. Meta do mês",
            "",
            f"⚠️ Mês corrente ({mes_atual}) fora da série `METAS_MENSAIS`.",
            "Atualize o dicionário no topo de `tools/performance.py` para voltar a operar.",
        ]
    meta = METAS_MENSAIS[mes_atual]["meta_acumulada"]
    deficit = meta - total_q
    linhas = [
        "## 3. Meta do mês",
        "",
        f"- **Mês corrente:** {mes_atual}",
        f"- **Meta acumulada:** {meta}",
        f"- **Acumulado atual:** {total_q}",
    ]
    if deficit <= 0:
        linhas.append(f"- ✅ **Meta atingida** — excedente de {abs(deficit)}q.")
    else:
        dias = dias_restantes_no_mes(hoje)
        ritmo = deficit / dias
        linhas.extend([
            f"- **Déficit:** {deficit}q",
            f"- **Dias restantes (incluindo hoje):** {dias}",
            f"- **Ritmo necessário:** ~{ritmo:.0f}q/dia",
        ])
    return linhas


def bloco_custo(mes_atual, total_q, questoes_mes):
    linhas = ["## 4. Custo por questão", ""]
    if mes_atual not in METAS_MENSAIS:
        linhas.append(f"⚠️ Mês corrente ({mes_atual}) fora da série — sem dados de investimento.")
        return linhas

    investimento_acumulado = METAS_MENSAIS[mes_atual]["investimento"]

    # Parcela do mês = diff vs mês anterior; fallback se for o primeiro da série
    mes_ant = mes_anterior(mes_atual)
    if mes_ant in METAS_MENSAIS:
        parcela_mes = investimento_acumulado - METAS_MENSAIS[mes_ant]["investimento"]
    else:
        parcela_mes = investimento_acumulado  # Superestima; aceito no v0

    # Acumulado
    if total_q > 0:
        custo_acum = investimento_acumulado / total_q
        emoji_a, rotulo_a = classificar_custo(custo_acum)
        distancia_a = custo_acum - META_CUSTO_Q
        linhas.append(
            f"- **Acumulado:** {fmt_moeda(custo_acum)}/q {emoji_a} {rotulo_a}"
            f" — distância da meta ({fmt_moeda(META_CUSTO_Q)}): {fmt_moeda(distancia_a)}"
        )
    else:
        linhas.append("- **Acumulado:** N/A (0 questões)")

    # Mês corrente
    if questoes_mes > 0:
        custo_mes = parcela_mes / questoes_mes
        emoji_m, rotulo_m = classificar_custo(custo_mes)
        distancia_m = custo_mes - META_CUSTO_Q
        linhas.append(
            f"- **Mês corrente ({mes_atual}):** {fmt_moeda(custo_mes)}/q"
            f" {emoji_m} {rotulo_m} — distância da meta: {fmt_moeda(distancia_m)}"
            f" _(parcela do mês: {fmt_moeda(parcela_mes)} / {questoes_mes}q)_"
        )
    else:
        linhas.append(f"- **Mês corrente ({mes_atual}):** N/A (0 questões no mês)")

    return linhas


def bloco_marcos(total_q, hoje):
    linhas = ["## 2. Marcos adiante", ""]
    for nome, alvo, data_marco in MARCOS:
        faltam = alvo - total_q
        if faltam <= 0:
            linhas.append(f"- ✅ **{nome}** ({alvo}) — meta já atingida (excedente {abs(faltam)}q).")
            continue
        linhas.append(f"- **{nome}** ({alvo}) — faltam **{faltam}q**.")
        if data_marco is None:
            continue
        dias = (data_marco - hoje).days  # hoje inclusive, dia da prova exclusivo
        if dias <= 0:
            linhas.append(f"  - ⚠️ Data do marco ({data_marco.isoformat()}) já passou — atualizar `MARCOS`.")
            continue
        ritmo_alvo = faltam / dias
        linhas.append(
            f"  - **{dias} dias** até {data_marco.strftime('%d/%m/%Y')}"
            f" — ritmo para o alvo: ~{ritmo_alvo:.0f}q/dia."
        )
        # Custo/q projetado usa o investimento acumulado do mês do marco.
        invest_marco = METAS_MENSAIS.get(data_marco.strftime("%Y-%m"), {}).get("investimento")
        for ritmo in RITMOS_PROJECAO:
            proj = total_q + ritmo * dias
            pct = 100.0 * proj / alvo
            extra = ""
            if invest_marco:
                custo_proj = invest_marco / proj
                emoji, _rotulo = classificar_custo(custo_proj)
                extra = f" · custo/q proj.: {fmt_moeda(custo_proj)} {emoji}"
            linhas.append(
                f"  - Projeção **{ritmo}q/dia** → {proj} acumuladas ({pct:.0f}% do alvo){extra}"
            )
    return linhas


def bloco_areas(por_area):
    linhas = ["## 5. Áreas fracas e gaps", ""]

    fracas = sorted(
        [(a, q, ac, p) for (a, q, ac, p) in por_area if q > 0 and p < 75.0],
        key=lambda x: x[3],
    )
    if fracas:
        linhas.append("**Áreas com performance < 75% (revisar):**")
        for area, q, _ac, p in fracas:
            linhas.append(f"- 🔴 {area} — {p:.1f}% ({q}q)")
    else:
        linhas.append("**Áreas com performance < 75%:** nenhuma.")

    linhas.append("")

    areas_com_q = {a for (a, q, _ac, _p) in por_area if q > 0}
    gaps = [a for a in AREAS_VALIDAS if a not in areas_com_q]
    if gaps:
        linhas.append("**Áreas com 0 questões (gaps absolutos):**")
        linhas.append("- " + ", ".join(gaps))
    else:
        linhas.append("**Gaps absolutos:** nenhum — todas as áreas têm questões.")

    return linhas


def formatar_relatorio(total_q, total_a, por_area, mes_atual, questoes_mes, hoje):
    partes = []
    partes.append(f"# Performance MedHub — {hoje.isoformat()}")
    partes.append("")
    partes.extend(bloco_total(total_q, total_a))
    partes.append("")
    partes.extend(bloco_marcos(total_q, hoje))
    partes.append("")
    partes.extend(bloco_meta_mes(mes_atual, total_q, hoje))
    partes.append("")
    partes.extend(bloco_custo(mes_atual, total_q, questoes_mes))
    partes.append("")
    partes.extend(bloco_areas(por_area))
    return "\n".join(partes)


def main():
    # Garante UTF-8 no stdout — emojis das faixas (🟢🟡🟠🔴🟣) quebram
    # no cp1252 default do Windows quando chamado via subprocess.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # Python < 3.7 ou stdout não-reconfigurável

    parser = argparse.ArgumentParser(
        description="Checagem rápida de performance MedHub (relatório markdown em stdout)."
    )
    parser.parse_args()

    hoje = date.today()
    mes_atual = hoje.strftime("%Y-%m")

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        total_q, total_a = get_totais(conn)
        por_area = get_por_area(conn)
        questoes_mes = get_questoes_do_mes(conn, mes_atual)
    finally:
        if conn:
            conn.close()

    relatorio = formatar_relatorio(total_q, total_a, por_area, mes_atual, questoes_mes, hoje)
    print(relatorio)


if __name__ == "__main__":
    main()
