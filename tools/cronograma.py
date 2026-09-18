"""tools/cronograma.py — Derivador único do cronograma de Reta Final (read-only).

SSOT = `Cronograma.pdf` (raiz, IP do EMED, gitignored). Deriva
`core/cronograma/grade.json` (camada versionável, estrutural — sem texto clínico).

🔴 FRONTEIRA DURA (contrato de cronograma, ultraplan s094 §c/§d.3): este módulo
NÃO escreve no `ipub.db` — nem `taxonomia_cronograma`, nem `sessoes_bulk`, nem
FSRS, nem `review_log`. É derivador puro + leitor. O único acoplamento com o DB
é leitura (`--gap` lê o total acumulado via performance, read-only).

Fonte → derivado:
  Cronograma.pdf  --(PyPDF2)-->  páginas  --(parse)-->  grade.json (+ _meta sha256)

Subcomandos:
  --rebuild         extrai do PDF, parseia, (re)grava grade.json
  --check           compara sha256 do PDF vs grade._meta (W5 do reconcile)
  --json [--semana N]   imprime a grade inteira (ou só a semana N)
  --gap [--meta M]  gap honesto de volume: acum(ipub) + cronograma restante vs meta
  --validate        roda asserções de validação (S10=273, S11-28=6689/222, áreas)

Uso: python tools/cronograma.py --rebuild
"""
import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))



def resolve_pdf_path(root=None):
    """Localiza o `Cronograma.pdf`: raiz do repo (canonico, contrato) e, como
    fallback, `data/` (onde o arquivo vive ao lado dos outros PDFs de dados).
    Devolve o caminho canonico mesmo quando nenhum existe, para a mensagem de
    erro nomear o lugar certo (hotfix 2026-09-06: `--check` abortava com
    FileNotFoundError e o instrumento W5 do reconcile ficava morto)."""
    root = root or ROOT
    canon = os.path.join(root, "Cronograma.pdf")
    if os.path.exists(canon):
        return canon
    alt = os.path.join(root, "data", "Cronograma.pdf")
    return alt if os.path.exists(alt) else canon


PDF_EXTENSIVO_NOME = "[52 wk] Cronograma Extensivo.pdf"


def resolve_pdf_extensivo(root=None):
    """Localiza o `[52 wk] Cronograma Extensivo.pdf`: raiz do repo (canonico) e,
    como fallback, `data/` -- mesmo padrao de `resolve_pdf_path` (hotfix s166).
    Devolve o caminho canonico mesmo quando nenhum existe, para a mensagem de
    erro do `--check-extensivo` nomear o lugar certo."""
    root = root or ROOT
    canon = os.path.join(root, PDF_EXTENSIVO_NOME)
    if os.path.exists(canon):
        return canon
    alt = os.path.join(root, "data", PDF_EXTENSIVO_NOME)
    return alt if os.path.exists(alt) else canon


PDF_PATH = resolve_pdf_path()
GRADE_PATH = os.path.join(ROOT, "core", "cronograma", "grade.json")
PDF_EXTENSIVO_PATH = resolve_pdf_extensivo()
GRADE_EXTENSIVO_PATH = os.path.join(ROOT, "core", "cronograma", "grade_extensivo.json")

# Âncora de datas: derivada do fato documentado "26/06 calendário na S13" (ESTADO.md).
# S1 inicia 2026-03-30 (segunda) → S13 = 22/06–28/06 ⊇ 26/06. Ajustável: regravar a grade.
# Semanas são blocos de 7 dias; o usuário segue por CONTEÚDO (atrás do calendário nominal).
SEMANA_1_INICIO = "2026-03-30"

# Linchpin do sync (ultraplan §c.4): nomes longos do PDF → 20 áreas canônicas do DB
# (AREAS_VALIDAS de registrar_sessao_bulk.py). Identidade para os que já batem.
AREA_PDF_TO_CANON = {
    "Pediatria": "Pediatria",
    "Cirurgia": "Cirurgia",
    "Preventiva": "Preventiva",
    "Medicina Preventiva": "Preventiva",
    "Obstetrícia": "Obstetrícia",
    "Ginecologia": "Ginecologia",
    "Infectologia": "Infecto",
    "Gastroenterologia": "Gastro",
    "Endocrinologia": "Endocrino",
    "Nefrologia": "Nefrologia",
    "Neurologia": "Neurologia",
    "Cardiologia": "Cardiologia",
    "Pneumologia": "Pneumo",
    "Reumatologia": "Reumato",
    "Hematologia": "Hemato",
    "Psiquiatria": "Psiquiatria",
    "Hepatologia": "Hepato",
    "Dermatologia": "Dermato",
    "Ortopedia": "Ortopedia",
    "Otorrinolaringologia": "Otorrino",
    "Oftalmologia": "Oftalmo",
}

# Tipos genéricos do bloco Resumo (semanas iniciais usam isto no lugar do tema).
TIPOS_GENERICOS = {
    "Teoria + Exercícios", "Revisão", "Revisão por Questões",
    "Revisão Final", "Diversos Assuntos", "Questões Erradas",
}

# Rodapés/cabeçalhos do PDF a descartar no parse.
_JUNK = re.compile(
    r"^(?:\d+|Resumo|Atividades|Estratégia|MEDRESIDÊNCIA MÉDICA|"
    r"Estratégia MED \| Cronograma.*|Medicina\s+livre.*|med\.estrategia\.com|"
    r"Links Materiais Teóricos|Observações)\s*$"
)


def normaliza_area(area_pdf):
    """(area_norm, multi_area). Multi = task abrangente (Rev. por Questões / simulado)."""
    a = re.sub(r"\s+", " ", area_pdf or "").strip().rstrip(",")
    if a in AREA_PDF_TO_CANON:
        return AREA_PDF_TO_CANON[a], False
    return "Multi", True


def normaliza_area_extensivo(disciplina):
    """area_norm do Extensivo -- reusa `AREA_PDF_TO_CANON` (Technical Decision da spec
    plano-ssot-e-cards-v2-part-1: um so lugar para a taxonomia EMED -> canonica, em vez
    de uma segunda tabela). `disciplina` chega ja na forma canonica-acentuada (ver
    `_casa_disciplina`), entao a maioria bate direto -- as mesmas 20 especialidades da
    Reta Final aparecem aqui.

    Duas disciplinas do Extensivo NAO estao em `AREA_PDF_TO_CANON`/`core/areas.json` e
    caem em `Multi` por decisao documentada (spec DoD 3, Risk):
      - "Todas as Disciplinas": ja e o coringa multi-area na Reta Final (`normaliza_area`).
      - "Radiologia": NAO existe em `core/areas.json` (vocabulario do operador, F89) e a
        spec autoriza `Multi` OU uma proposta -- 6/735 tarefas (0,8%), sem card/questao
        vinculado a "Radiologia" como especialidade isolada no ipub.db hoje; `Multi` evita
        inventar uma 21a area sem decisao do operador (mudar a lista e ato dele, F89)."""
    return AREA_PDF_TO_CANON.get(disciplina, "Multi")


def normaliza_tipo(tipo_verbatim):
    """tipo_norm ∈ {teoria, revisao, revisao_questoes, outro} -- calibra a aula por bloco."""
    t = (tipo_verbatim or "").lower()
    if ("quest" in t and "revis" in t) or "errad" in t or "diversos" in t:
        return "revisao_questoes"
    if "revis" in t:
        return "revisao"
    if "teoria" in t or "exerc" in t:
        return "teoria"
    return "outro"


def _dewrap(text):
    return re.sub(r"\s+", " ", text).strip()


def _clean(lines):
    return [l for l in lines if l.strip() and not _JUNK.match(l.strip())]


def _split_tarefas(block_lines):
    """{N: [linhas]} a partir dos marcadores 'Tarefa N' (linha isolada)."""
    tasks, cur = {}, None
    for l in block_lines:
        m = re.match(r"^Tarefa (\d+)\s*$", l.strip())
        if m:
            cur = int(m.group(1))
            tasks[cur] = []
        elif cur is not None:
            tasks[cur].append(l)
    return tasks


def _parse_payload(payload_lines):
    """Linhas após a área num task do Resumo → (tema, tipo_verbatim)."""
    s = _dewrap(" ".join(_clean(payload_lines)))
    if not s:
        return "", ""
    if s in TIPOS_GENERICOS:                 # semana inicial: só categoria, tema vem do detalhe
        return "", s
    m = re.search(r"\(([^)]*)\)\s*$", s)      # "...tema (Tipo)" -- tipo no fim entre parênteses
    if m:
        return s[:m.start()].strip(), m.group(1).strip()
    return s, ""                              # tema sem tipo explícito


def _parse_detail(detail_lines):
    """{N: {tema_detail, questoes, raw}} -- tema via '(Livro Digital|Assunto): tema (Tipo)' + Links.

    F77b (s176): o literal era só `Livro Digital:`. As tarefas de **Revisão por Questões** usam
    `Assunto:` -- ex.: *"Obstetricia Assunto: Pre-Natal; Assistencia ao Parto; Vitalidade Fetal
    (Revisao por Questoes)"* -- e nasciam com `tema` VAZIO no `grade.json`, 5 por ciclo. O tema
    estava escrito no PDF e o parser o jogava fora; é a mesma família do drift "Revisão por
    Questões" (tarefa multi-tema que cai em campo emprestado e fica subnotificada).
    """
    out = {}
    for n, lines in _split_tarefas(detail_lines).items():
        s = _dewrap(" ".join(lines))
        m = re.search(r"(?:Livro Digital|Assunto):\s*(.+?)\s*\((?:Teoria|Revis[ãa]o)[^)]*\)", s)
        counts = [int(c) for c in re.findall(r"Link\s*-\s*(\d+)\s*quest", s)]
        out[n] = {"tema_detail": m.group(1).strip() if m else "", "questoes": sum(counts), "raw": s}
    return out


def parse_grade(paginas, semana_1_inicio=SEMANA_1_INICIO):
    """Lista de semanas + total de questões, a partir das páginas extraídas do PDF."""
    lines = "\n".join(paginas).split("\n")
    starts = []
    for i, l in enumerate(lines):
        m = re.match(r"^Semana (\d{2})$", l.strip())
        if m and "Resumo" in [x.strip() for x in lines[i + 1:i + 3]]:
            starts.append((i, int(m.group(1))))

    s1 = datetime.strptime(semana_1_inicio, "%Y-%m-%d").date()
    semanas, total_q = [], 0
    for k, (i, n) in enumerate(starts):
        j = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        wl = lines[i:j]
        ati = next((x for x, l in enumerate(wl) if l.strip() == "Atividades"), len(wl))
        rtasks = _split_tarefas(wl[:ati])
        dtasks = _parse_detail(wl[ati:])

        tasks = []
        for tn in sorted(rtasks):
            clean = _clean(rtasks[tn])
            area_pdf = clean[0].strip() if clean else ""
            tema_r, tipo_v = _parse_payload(clean[1:])
            d = dtasks.get(tn, {})
            area_norm, multi = normaliza_area(area_pdf)
            tipo_norm = normaliza_tipo(tipo_v)
            # material_indicado (C4 recalibrado, s107): 'extensivo' SÓ quando o texto do PDF
            # menciona explicitamente 'Extensivo'/'Livro Digital Completo' E a task NÃO é de
            # revisão (revisar o LDI já estudado ≠ leitura extensiva fresca). O gatilho antigo
            # `tipo_norm=='teoria'` era largo demais -- marcava 279/352 (79%) como extensivo,
            # esvaziando a calibração. Novo critério ancora na menção textual: ~44% das tasks.
            raw = d.get("raw", "")
            menciona_ext = re.search(r"extensivo|livro digital completo", raw, re.I)
            eh_revisao = re.search(r"revis[ãa]o", raw, re.I)
            mat = "extensivo" if (menciona_ext and not eh_revisao) else "resumo"
            tasks.append({
                "tarefa": tn,
                "area_pdf": area_pdf,
                "area_norm": area_norm,
                "multi_area": multi,
                "tema": tema_r or d.get("tema_detail", "") or "",
                "tipo": tipo_v,
                "tipo_norm": tipo_norm,
                "material_indicado": mat,
                "questoes": int(d.get("questoes", 0) or 0),
            })

        # total da SEMANA = soma de TODOS os "Link - NN questões" da semana (validado: S10=273,
        # S11-28=6689).
        wq = sum(int(c) for c in re.findall(r"Link\s*-\s*(\d+)\s*quest", "\n".join(wl)))
        total_q += wq

        # F77 (s176) -- a contagem POR TAREFA passa a viajar, com marca de confiança.
        #
        # ⚰️ A regra antiga dizia: "NÃO atribuímos count por task: o PDF não amarra
        # link[i]<->task[i] de forma garantida (ultraplan §c.5) -> o consumidor rateia igual".
        # O dado já era calculado por `_parse_detail` e **descartado**. O rateio igual erra por
        # até 3x na dimensão que o usuário usa para planejar o dia: na S17 ele daria 26,6q para
        # toda tarefa, quando as reais valem de 16q (Pneumonias Bacterianas) a 50q (APS Revisão).
        #
        # A desconfiança era razoável em 2026-07 e nunca foi medida. Medida na s168: em S17-S20 a
        # soma das tarefas bate EXATAMENTE com o total da semana nas quatro (293/380/449/301).
        # Então o dado bom viaja e o caso duvidoso degrada -- em vez de jogar fora o dado bom em
        # 100% das semanas por causa de uma dúvida que nunca se materializou.
        soma_tasks = sum(t["questoes"] for t in tasks)
        if tasks and soma_tasks == wq and wq > 0:
            fonte = "link_no_bloco"          # reconciliou: a atribuição por tarefa é confiável
        else:
            fonte = "rateio_igual"           # degradação declarada, com o motivo no WARN
            rate = (wq / len(tasks)) if tasks else 0.0
            for t in tasks:
                t["questoes"] = round(rate, 1)
            if tasks and wq > 0:
                print(f"[WARN] S{n:02d}: soma das tarefas ({soma_tasks}q) != total da semana "
                      f"({wq}q) -- questoes por tarefa degradadas para rateio igual "
                      f"({rate:.1f}q/tarefa). O `questoes_fonte` declara isso.", file=sys.stderr)
        for t in tasks:
            t["questoes_fonte"] = fonte

        inicio = s1 + timedelta(days=(n - 1) * 7)
        semanas.append({
            "semana": n,
            "inicio": inicio.isoformat(),
            "fim": (inicio + timedelta(days=6)).isoformat(),
            "total_questoes": wq,
            "questoes_fonte": fonte,
            "n_tasks": len(tasks),
            "tasks": tasks,
        })
    return semanas, total_q


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extrai_paginas(pdf_path=PDF_PATH):
    import PyPDF2
    reader = PyPDF2.PdfReader(pdf_path)
    return [(p.extract_text() or "") for p in reader.pages]


def rebuild(pdf_path=PDF_PATH, grade_path=GRADE_PATH, semana_1_inicio=SEMANA_1_INICIO):
    semanas, total_q = parse_grade(extrai_paginas(pdf_path), semana_1_inicio)
    grade = {
        "_meta": {
            "fonte": os.path.basename(pdf_path),
            "fonte_sha256": sha256_file(pdf_path),
            "fonte_mtime": datetime.fromtimestamp(os.path.getmtime(pdf_path)).isoformat(timespec="seconds"),
            "extraido_em": datetime.now().isoformat(timespec="seconds"),
            "semana_1_inicio": semana_1_inicio,
            "n_semanas": len(semanas),
            "n_tasks": sum(s["n_tasks"] for s in semanas),
            "total_questoes": total_q,
            "areas_canon": sorted(set(AREA_PDF_TO_CANON.values())),
        },
        "semanas": semanas,
    }
    os.makedirs(os.path.dirname(grade_path), exist_ok=True)
    with open(grade_path, "w", encoding="utf-8") as f:
        json.dump(grade, f, ensure_ascii=False, indent=2)
    return grade


def load_grade(grade_path=GRADE_PATH):
    with open(grade_path, encoding="utf-8") as f:
        return json.load(f)


def check(pdf_path=PDF_PATH, grade_path=GRADE_PATH):
    if not os.path.exists(grade_path):
        return {"status": "missing", "msg": "grade.json não existe -- rode --rebuild"}
    g = load_grade(grade_path)
    if not os.path.exists(pdf_path):
        return {"status": "missing_pdf",
                "msg": f"Cronograma.pdf nao encontrado ({pdf_path}; tambem procurado em data/) "
                       "-- W5 nao verificavel; a grade.json continua valida como derivado"}
    cur, old = sha256_file(pdf_path), g["_meta"].get("fonte_sha256")
    fresh = cur == old
    return {
        "status": "fresh" if fresh else "stale",
        "pdf_sha256": cur, "grade_sha256": old,
        "msg": "grade em dia" if fresh else "PDF mudou desde a última grade -- rode --rebuild (W5)",
    }


def get_semana(grade, n):
    return next((s for s in grade["semanas"] if s["semana"] == n), None)


def semana_corrente(grade, hoje=None):
    """Semana NOMINAL (por data) que contém hoje. NB: o usuário segue por conteúdo,
    tipicamente atrás do calendário nominal (ESTADO: 'calendário na S13 × conteúdo na S10')."""
    h = (hoje or date.today()).isoformat()
    for s in grade["semanas"]:
        if s["inicio"] <= h <= s["fim"]:
            return s["semana"]
    return None


def gap_payload(conn, grade, hoje=None, meta=None, desde=None):
    """Payload do `--gap` (F88, s174): acumulado e meta vem da UNICA conta do repo,
    `performance.volume_vs_marco` -- a mesma que o boot (`day_plan`) imprime. `meta`
    explicita e what-if (override), nunca default literal. Read-only."""
    from performance import volume_vs_marco
    vm = volume_vs_marco(conn, hoje)
    out = gap_volume(grade, vm["total"], meta if meta is not None else vm["meta"], desde,
                     hoje=hoje)
    out["marco"] = vm["marco"]
    return out


def gap_volume(grade, total_acum, meta, desde_semana=None, hoje=None):
    """Gap honesto de volume (ultraplan §a.3): mesmo a 100% do cronograma, falta banco extra?
    `meta`/`total_acum` chegam de `gap_payload` (fonte unica) -- sem default literal (F88)."""
    if desde_semana is None:
        desde_semana = semana_corrente(grade, hoje) or 1
    restante = sum(s["total_questoes"] for s in grade["semanas"] if s["semana"] >= desde_semana)
    projecao = total_acum + restante
    return {
        "meta": meta,
        "acumulado": total_acum,
        "desde_semana": desde_semana,
        "cronograma_restante": restante,
        "projecao_se_100pct": projecao,
        "gap_volume": max(0, meta - projecao),
    }


# ───────────────────────── Fase 2 -- Radar cobertura × performance ─────────────────────────
ENAMED = "2026-09-13"   # fronteira pré/pós para o radar de cobertura


def _norm_perf_area(area):
    """Rótulo de sessoes_bulk → área canônica (ou None p/ pular). Trata os sujos do W4."""
    canon = set(AREA_PDF_TO_CANON.values())
    if area in canon:
        return area, None
    a = (area or "").strip()
    if a.startswith("Obstetr"):                      # mojibake "Obstetr�cia"
        return "Obstetrícia", f"rótulo sujo {a!r} normalizado → Obstetrícia"
    if a == "GO":
        return None, "rótulo 'GO' ambíguo Gineco/Obstetrícia -- não atribuído (split não-trivial)"
    return None, f"rótulo desconhecido {a!r} fora de AREAS_VALIDAS -- ignorado"


def radar(grade, por_area, desde_semana=None, enamed=ENAMED):
    """Cruza performance (sessoes_bulk) × cobertura futura do cronograma (rateio igual),
    com fronteira pré/pós-ENAMED. Read-only. Não escreve nada."""
    if desde_semana is None:
        desde_semana = semana_corrente(grade) or 1

    perf, warnings = {}, []
    for area, q, a, _pct in por_area:
        canon, w = _norm_perf_area(area)
        if w:
            warnings.append(w)
        if canon:
            pq, pa = perf.get(canon, (0, 0))
            perf[canon] = (pq + q, pa + a)
    perf = {k: (q, (100.0 * a / q if q else 0.0)) for k, (q, a) in perf.items()}

    cov_pre, cov_post, weeks_by_area = {}, {}, {}
    for s in grade["semanas"]:
        if s["semana"] < desde_semana or s["n_tasks"] == 0:
            continue
        # F77 (s176): usa a contagem POR TAREFA quando ela reconciliou com o total da semana
        # (`questoes_fonte == "link_no_bloco"`); cai para o rateio igual só quando não
        # reconciliou -- e aí o próprio campo já vem rateado pelo derivador. Grade antiga, sem o
        # campo, continua no rateio: o leitor não quebra com `grade.json` de antes desta sessão.
        rate = s["total_questoes"] / s["n_tasks"]          # fallback (ultraplan §c.5)
        bucket = cov_pre if s["inicio"] <= enamed else cov_post
        for t in s["tasks"]:
            if t["multi_area"]:
                continue
            A = t["area_norm"]
            q_task = t.get("questoes") if t.get("questoes_fonte") else None
            bucket[A] = bucket.get(A, 0.0) + (q_task if q_task is not None else rate)
            weeks_by_area.setdefault(A, set()).add(s["semana"])

    rows = []
    for A in sorted(set(AREA_PDF_TO_CANON.values())):
        q, pct = perf.get(A, (0, 0.0))
        pre, post = round(cov_pre.get(A, 0.0)), round(cov_post.get(A, 0.0))
        weak = (q < 50) or (pct < 70.0)
        if pre > 0:
            flag, tag = "🟢", "coberta pré-ENAMED"
        elif post > 0:
            flag, tag = "🟡", "só pós-ENAMED (tarde)"
        elif q == 0:
            flag, tag = "⚪", "gap total (0q feito · 0 no cronograma restante)"
        elif weak:
            flag, tag = "🔴", "fraca SEM cobertura restante"
        else:
            flag, tag = "🟢", "dominada (sem mais no cronograma)"
        rows.append({
            "area": A, "feito_q": q, "pct": round(pct, 1),
            "cobertura_pre": pre, "cobertura_pos": post,
            "flag": flag, "tag": tag,
            "semanas": sorted(weeks_by_area.get(A, set())),
        })
    return {"desde_semana": desde_semana, "enamed": enamed, "rows": rows, "warnings": warnings}


def render_radar(r):
    ordem = {"🔴": 0, "⚪": 1, "🟡": 2, "🟢": 3}
    out = [f"# 🧭 Radar cronograma × performance (desde S{r['desde_semana']} · ENAMED {r['enamed']})", ""]
    for w in r["warnings"]:
        out.append(f"- ⚠️ {w}")
    if r["warnings"]:
        out.append("")
    for row in sorted(r["rows"], key=lambda x: (ordem[x["flag"]], x["area"])):
        sem = f" · S{row['semanas']}" if row["semanas"] else ""
        out.append(
            f"- {row['flag']} **{row['area']}** -- {row['feito_q']}q feito ({row['pct']}%) · "
            f"cobertura restante pré {row['cobertura_pre']}q / pós {row['cobertura_pos']}q · {row['tag']}{sem}"
        )
    return "\n".join(out)


def validate(grade):
    """Asserções da Fase 1 (ultraplan §e). Retorna (ok, linhas)."""
    out, ok = [], True
    s10 = get_semana(grade, 10)
    q10 = s10["total_questoes"] if s10 else None
    out.append(f"{'✓' if q10 == 273 else '✗'} S10 = {q10}q (esperado 273)")
    ok &= q10 == 273

    s11_28 = [s for s in grade["semanas"] if 11 <= s["semana"] <= 28]
    q = sum(s["total_questoes"] for s in s11_28)
    t = sum(s["n_tasks"] for s in s11_28)
    out.append(f"{'✓' if q == 6689 else '✗'} S11-28 = {q}q (esperado 6689)")
    out.append(f"{'✓' if t == 222 else '✗'} S11-28 = {t} tasks (esperado 222)")
    ok &= q == 6689 and t == 222

    validas = set(AREA_PDF_TO_CANON.values()) | {"Multi"}
    bad = sorted({tk["area_norm"] for s in grade["semanas"] for tk in s["tasks"]} - validas)
    out.append(f"{'✓' if not bad else '✗'} todas area_norm ∈ AREAS_VALIDAS∪Multi"
               + (f" -- fora: {bad}" if bad else ""))
    ok &= not bad

    # quantas áreas das 20 canônicas o cronograma cobre (single, não-Multi)
    cobertas = {tk["area_norm"] for s in grade["semanas"] for tk in s["tasks"] if not tk["multi_area"]}
    out.append(f"  cobertura: {len(cobertas)}/20 áreas canônicas aparecem como task single")
    return ok, out


# ⚰️ ───── Sync Drive -- conclusão real (xlsx) -- REMOVIDO em 18/09/2026 ─────
# part-8 do PRD `plano-ssot-e-cards-v2`. Aqui viviam `DRIVE_SHEET_NAME`,
# `_norm_tema_xlsx`, `_parse_conclusao_xlsx`, `diff_drive` e `sync_drive` (a flag
# `--sync-drive`), que liam o `Cronograma de Reta Final.xlsx` baixado do Drive e
# gravavam o snapshot de conclusão em `preparacao_estado`.
#
# **Motivo:** o Drive deixou de ser fonte de plano e progresso (decisão do
# operador em 16/09/2026: *"Sim, banco é a fonte"*). A conclusão virou coluna
# (`plano_tarefas.status`/`origem_conclusao`, part-4) e a W8 do reconcile foi
# revogada junto. Manter o sync traria de volta DOIS sinais de conclusão e com
# eles a pergunta "qual dos dois vale?", que era o defeito original.
#
# **Reversibilidade (nunca deleção seca):** o último snapshot produzido por este
# código (2026-07-26, 52.802 chars) está exportado em
# `artifacts/snapshot-cronograma-drive-2026-07-26.json`, com sha256 e instruções
# de reversão; a chave `preparacao_estado.cronograma_conclusao_drive` **segue no
# banco, intocada**. O código sai do arquivo, não da história do git.
#
# Quem responde hoje pelo que este bloco respondia: `tools/plano.py` (plano),
# `tools/listas.py` (volume por lista) e `tools/painel.py` (a visão consolidada
# que substituiu as 20 tabelas do Dashboard).

# ───────────────── Extensivo (52 semanas) -- segundo derivador ─────────────────
# PRD plano-ssot-e-cards-v2, Parte 1. SSOT = `[52 wk] Cronograma Extensivo.pdf`
# (raiz, IP do EMED, gitignored). Deriva `core/cronograma/grade_extensivo.json`.
# Mesmo modulo/PDF-lib da Reta Final (Technical Decision: §7.2 pede assinatura
# canonica em UMA skill -- o `/cronograma` ja e a dona). Portado do prototipo
# validado na s183 (scratchpad/parse_extensivo.py, 52 semanas / 735 tarefas).
#
# 🔴 Falha dura (Technical Decision da spec): a contagem parseada tem que bater
# 735 tarefas / 52 semanas. Divergencia aborta o `--rebuild-extensivo` (nunca
# versiona um catalogo com buraco silencioso) -- a excecao declarada e
# `--expect-tasks N`, quando o PDF do EMED mudou de verdade.

EXTENSIVO_TASKS_ESPERADAS = 735
EXTENSIVO_SEMANAS_ESPERADAS = 52

# Disciplinas do Extensivo, forma canonica-acentuada (a mesma que aparece no PDF
# quando o PyPDF2 extrai bem -- medido, s183). Ordenado do nome mais longo para o
# mais curto: "Medicina Preventiva" tem que vencer antes de qualquer prefixo menor
# coincidir por acidente.
EXTENSIVO_DISCIPLINAS = [
    "Medicina Preventiva", "Pediatria", "Cirurgia", "Ginecologia", "Obstetrícia",
    "Infectologia", "Gastroenterologia", "Endocrinologia", "Cardiologia", "Nefrologia",
    "Hepatologia", "Reumatologia", "Ortopedia", "Otorrinolaringologia", "Oftalmologia",
    "Neurologia", "Pneumologia", "Hematologia", "Psiquiatria", "Dermatologia",
    "Radiologia", "Todas as Disciplinas",
]

# Variantes ABREVIADAS que o PDF usa a partir de certas semanas (medido, s183: "Preventiva"
# sozinho desde a S20; "Hepato"/"Gastro"/"Hemato"/"Reumato" etc. a partir da S29) -- casam
# para a MESMA forma canônica de `EXTENSIVO_DISCIPLINAS` (mesma taxonomia da Reta Final,
# `AREA_PDF_TO_CANON`, que já tem essas formas longas como chave).
_EXTENSIVO_DISC_ALIASES = {
    "Preventiva": "Medicina Preventiva", "Hepato": "Hepatologia", "Gastro": "Gastroenterologia",
    "Hemato": "Hematologia", "Reumato": "Reumatologia", "Endocrino": "Endocrinologia",
    "Cardio": "Cardiologia", "Neuro": "Neurologia", "Pneumo": "Pneumologia",
    "Infecto": "Infectologia", "Dermato": "Dermatologia", "Otorrino": "Otorrinolaringologia",
    "Oftalmo": "Oftalmologia",
}


def _strip_acentos(s):
    """casefold-like p/ acento: usado só p/ CASAR (o valor guardado continua com
    acento -- ver `_casa_disciplina`). Decompor NFD e remover marca combinante
    preserva o comprimento caractere-a-caractere (1 char acentuado -> 1 char
    base), então um índice calculado no texto sem acento vale no texto original."""
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn")


_EXTENSIVO_DISC_CANON = {d: d for d in EXTENSIVO_DISCIPLINAS}
_EXTENSIVO_DISC_CANON.update(_EXTENSIVO_DISC_ALIASES)

_EXTENSIVO_DISC_STRIP = sorted(
    ((_strip_acentos(variante), canon) for variante, canon in _EXTENSIVO_DISC_CANON.items()),
    key=lambda par: -len(par[0]),
)

# Semana 52 ("Revisão Final") lista VÁRIAS disciplinas por tarefa, encadeadas por vírgula/"e"
# (ex. "Cardio, Psiquiatria e Nefro") -- não é uma disciplina só com nome comprido, é uma
# task genuinamente multi-área. `_eh_tarefa_multi_disciplina` detecta o conector logo após a
# 1ª disciplina casada; quando acha, a task inteira vira `Todas as Disciplinas`/`Multi` em
# vez de ficar presa à primeira disciplina da lista.
_CONECTOR_MULTI_RE = re.compile(r"^\s*(?:,|e)\s+", re.I)


def _eh_tarefa_multi_disciplina(resto_apos_primeira_disciplina):
    stripped = _strip_acentos(resto_apos_primeira_disciplina)
    m = _CONECTOR_MULTI_RE.match(stripped)
    if not m:
        return False
    cauda = stripped[m.end():]
    return any(cauda.startswith(chave) for chave, _ in _EXTENSIVO_DISC_STRIP)


_SEMANA_EXT_RE = re.compile(r"ExtensivoSemana (\d{2})$")
_TIPO_EXT_RE = re.compile(
    r"(Revis[aã]o por Quest[oõ]es|Quest[oõ]es Erradas|Revis[aã]o te[oó]rica direcionada|"
    r"Simulado|Revis[aã]o(?:\s+(?:I{1,3}|IV|V))?|Teoria(?:\s+(?:I{1,3}|IV|V))?)\s*$"
)
_PAGINAS_EXT_RE = re.compile(r"p[aá]ginas?\s*(\d{1,3})\s*(?:a|at[eé]|-)\s*(\d{1,3})", re.I)
_QUESTOES_EXT_RE = re.compile(r"(\d{1,3})\s*quest[oõ]es")
_URL_LISTA_EXT_RE = re.compile(
    r"Link\s*-\s*\d{1,3}\s*quest[oõ]es\s*:\s*(https?://.*?)"
    r"(?:Acesse o material|Aula de|Obs\s*1|\Z)",
    re.I | re.S,
)
# guarda contra a URL "vazar" p/ dentro da frase seguinte quando nenhum dos
# terminadores acima aparece (PDF glued sem espaço, ex. "...per_page=20Acesse"):
# qualquer acento (português corrido) invalida o candidato.
_URL_CHARSET_EXT_RE = re.compile(r"^https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")


class ExtensivoContagemDivergente(RuntimeError):
    """A contagem parseada do Extensivo não bate 735/52 (nem `--expect-tasks`)."""


def _casa_disciplina(resto):
    """(disciplina_canonica|None, resto_sem_o_prefixo_da_disciplina)."""
    stripped = _strip_acentos(resto)
    for chave, canon in _EXTENSIVO_DISC_STRIP:
        if stripped.startswith(chave):
            return canon, resto[len(chave):].strip()
    return None, resto


def _parse_resumo_semana(linhas_bloco):
    """Bloco 'Resumo' (lista curta) de UMA semana -> tasks[] sem os campos do
    'Passo a Passo' (paginas/questoes/url, preenchidos depois por
    `_parse_detalhe_tarefa`). Linha SEM espaço final = fim de um componente
    (glued Tarefa N / assunto / tipo); linha COM espaço final = wrap de PDF
    (glue direto, sem separador) -- é assim que o PyPDF2 devolve texto
    justificado. Portado do protótipo (s183)."""
    blob = ""
    for ln in linhas_bloco:
        if not ln.strip():
            continue
        if ln.endswith(" "):
            blob += ln
        else:
            blob += ln + " // "
    blob = blob.replace(" ", " ")

    partes = re.split(r"Tarefa\s*(\d{1,2})\s*", blob)
    tasks = []
    for k in range(1, len(partes), 2):
        num = int(partes[k])
        corpo = partes[k + 1].strip().strip("/").strip()
        corpo = re.sub(r"\s*//\s*$", "", corpo).strip()
        b2 = re.sub(r"\s+", " ", corpo.replace(" // ", " ~ ")).strip()

        m_tipo = _TIPO_EXT_RE.search(b2)
        if m_tipo:
            tipo_verbatim, resto = m_tipo.group(1), b2[:m_tipo.start()].strip()
        else:
            tipo_verbatim, resto = None, b2

        disc_canon, resto2 = _casa_disciplina(resto)
        if disc_canon and disc_canon != "Todas as Disciplinas" \
                and _eh_tarefa_multi_disciplina(resto2):
            disc_canon, resto2 = "Todas as Disciplinas", resto   # lista encadeada (S52)
        assunto = re.sub(r"\s+", " ", resto2).strip().strip("~").strip()
        subtemas = [x.strip() for x in assunto.split("~") if x.strip()]
        assunto = " | ".join(subtemas)

        if tipo_verbatim is None and "Diversos Assuntos" in assunto:
            tipo_verbatim = "Diversos Assuntos"
            assunto = "Diversos Assuntos"
            subtemas = ["Diversos Assuntos"]

        tasks.append({
            "tarefa": num,
            "disciplina": disc_canon,
            "area_norm": normaliza_area_extensivo(disc_canon),
            "assunto": assunto,
            "subtemas": subtemas,
            "tipo": tipo_verbatim or "",
            "tipo_norm": normaliza_tipo(tipo_verbatim),
        })
    return tasks


def _parse_detalhe_tarefa(corpo):
    """Bloco 'Passo a Passo' de UMA tarefa -> páginas do Livro Digital, n_questoes
    declarado, n_links_questoes e url_lista (best-effort, nunca scraping -- só o
    que o texto do PDF já expõe; ver `_URL_LISTA_EXT_RE`)."""
    flat = re.sub(r"\s+", " ", corpo)
    paginas = []
    for lo, hi in _PAGINAS_EXT_RE.findall(flat):
        par = [int(lo), int(hi)]
        if par not in paginas:
            paginas.append(par)
    n_paginas = sum(hi - lo + 1 for lo, hi in paginas)
    qs = _QUESTOES_EXT_RE.findall(flat)
    n_questoes = int(qs[0]) if qs else None
    n_links = len(re.findall(r"cadernos/", flat))

    url = None
    m_url = _URL_LISTA_EXT_RE.search(corpo)
    if m_url:
        candidato = re.sub(r"\s+", "", m_url.group(1))
        if _URL_CHARSET_EXT_RE.match(candidato):
            url = candidato

    return {
        "paginas_livro": paginas, "n_paginas": n_paginas,
        "n_questoes": n_questoes, "n_links_questoes": n_links, "url_lista": url,
    }


def _juntar_paginas_extensivo(paginas):
    """Junta as páginas extraídas (`extrai_paginas`) com o marcador
    '===== PAGE N =====' que `parse_extensivo_text` usa p/ delimitar onde a
    tabela Resumo de uma semana acaba -- ela não atravessa a próxima página no
    PDF real (medido, s183); sem o marcador o parser não sabe separar o Resumo
    da semana N do Passo a Passo que continua logo depois."""
    return "\n".join(f"===== PAGE {i + 1} =====\n{p}" for i, p in enumerate(paginas))


#: marca d'água repetida em TODA página do PDF (2100x medido no doc real) -- sem filtro,
#: ela cola na última tarefa de cada semana (a que não tem "Tarefa N+1" pra bounda-la) e
#: quebra o `_TIPO_EXT_RE` (ancorado em `$`, deixa de achar o fim da linha real).
_WATERMARK_EXT = "Medicina livre, venda proibida, twitter @Livremedicina"


def parse_extensivo_text(texto):
    """Função pura: texto já com marcadores de página (`_juntar_paginas_extensivo`)
    -> `semanas[].tasks[]` no schema da spec (sem `_meta` -- quem monta o `_meta`
    é `rebuild_extensivo`). Portado do protótipo validado na s183
    (scratchpad/parse_extensivo.py, 52 semanas / 735 tarefas)."""
    linhas = [l for l in texto.split("\n") if l.strip() != _WATERMARK_EXT]

    wk_start = {}
    for i, l in enumerate(linhas):
        m = _SEMANA_EXT_RE.search(l)
        if m and i + 1 < len(linhas) and linhas[i + 1].strip() == "Resumo":
            w = int(m.group(1))
            if w not in wk_start:
                wk_start[w] = i
    wk_keys = sorted(wk_start)

    semanas = []
    for w in wk_keys:
        i = wk_start[w]
        j = i + 2
        buf = []
        while j < len(linhas) and not linhas[j].startswith("===== PAGE"):
            buf.append(linhas[j])
            j += 1
        semanas.append({"semana": w, "tasks": _parse_resumo_semana(buf)})

    bounds = []
    for idx, w in enumerate(wk_keys):
        a = wk_start[w]
        b = wk_start[wk_keys[idx + 1]] if idx + 1 < len(wk_keys) else len(linhas)
        bounds.append((w, a, b))

    detalhes = {}
    for w, a, b in bounds:
        seg = "\n".join(linhas[a:b])
        pedacos = re.split(r"Tarefa (\d{1,2})\s*\n", seg)
        for k in range(1, len(pedacos), 2):
            detalhes[(w, int(pedacos[k]))] = _parse_detalhe_tarefa(pedacos[k + 1])

    for wk in semanas:
        for t in wk["tasks"]:
            d = detalhes.get((wk["semana"], t["tarefa"]), {})
            t["paginas_livro"] = d.get("paginas_livro", [])
            t["n_paginas"] = d.get("n_paginas", 0)
            t["n_questoes"] = d.get("n_questoes")
            t["n_links_questoes"] = d.get("n_links_questoes", 0)
            t["url_lista"] = d.get("url_lista")

    return semanas


def rebuild_extensivo(pdf_path=None, grade_path=GRADE_EXTENSIVO_PATH, expect_tasks=None):
    """(Re)gera `grade_extensivo.json` a partir do PDF. Falha dura (levanta
    `ExtensivoContagemDivergente`) quando a contagem não bate 735 tarefas / 52
    semanas -- `expect_tasks` é a ÚNICA válvula de escape declarada (flag
    `--expect-tasks`): quando passada, destrava a checagem INTEIRA (tarefas E
    semanas, contra o valor que o parser efetivamente encontrou), porque a spec
    só previu um flag para "o PDF do EMED mudou de verdade" -- duas válvulas
    separadas para um único escape declarado seria inventar assinatura que a
    skill não documenta (§7.2). Sem o flag, os dois números continuam
    invariantes: 735/52."""
    pdf_path = pdf_path or PDF_EXTENSIVO_PATH
    escape_declarado = expect_tasks is not None
    alvo_tasks = expect_tasks if escape_declarado else EXTENSIVO_TASKS_ESPERADAS
    texto = _juntar_paginas_extensivo(extrai_paginas(pdf_path))
    semanas = parse_extensivo_text(texto)

    n_semanas = len(semanas)
    n_tasks = sum(len(s["tasks"]) for s in semanas)
    alvo_semanas = n_semanas if escape_declarado else EXTENSIVO_SEMANAS_ESPERADAS
    sem_disciplina = [(s["semana"], t["tarefa"]) for s in semanas for t in s["tasks"]
                       if t["disciplina"] is None]
    if n_semanas != alvo_semanas or n_tasks != alvo_tasks or sem_disciplina:
        detalhe = f" · sem disciplina reconhecida: {sem_disciplina[:10]}" if sem_disciplina else ""
        raise ExtensivoContagemDivergente(
            f"parse do Extensivo divergiu do esperado: {n_semanas} semanas / {n_tasks} "
            f"tarefas (esperado {alvo_semanas}/{alvo_tasks}){detalhe}. "
            "Falha dura por decisão da spec (melhor recusar gerar que versionar um "
            "catálogo com buraco silencioso) -- use --expect-tasks N se o PDF do EMED "
            "mudou de verdade.")

    n_teoria = sum(1 for s in semanas for t in s["tasks"] if t["tipo_norm"] == "teoria")
    n_revisao = sum(1 for s in semanas for t in s["tasks"] if t["tipo_norm"] == "revisao")
    n_rpq = sum(1 for s in semanas for t in s["tasks"] if t["tipo_norm"] == "revisao_questoes")

    grade = {
        "_meta": {
            "fonte": os.path.basename(pdf_path),
            "sha256": sha256_file(pdf_path),
            "gerado_em": datetime.now().isoformat(timespec="seconds"),
            "n_semanas": n_semanas,
            "n_tasks": n_tasks,
            "n_teoria": n_teoria,
            "n_revisao": n_revisao,
            "n_rpq": n_rpq,
        },
        "semanas": semanas,
    }
    os.makedirs(os.path.dirname(grade_path), exist_ok=True)
    with open(grade_path, "w", encoding="utf-8") as f:
        json.dump(grade, f, ensure_ascii=False, indent=2)
    return grade


def check_extensivo(pdf_path=None, grade_path=GRADE_EXTENSIVO_PATH):
    """Espelho de `check()` p/ o Extensivo -- mesmo contrato: `fresh`/`stale`/
    `missing`/`missing_pdf`, nunca traceback com PDF ausente."""
    pdf_path = pdf_path or PDF_EXTENSIVO_PATH
    if not os.path.exists(grade_path):
        return {"status": "missing",
                "msg": "grade_extensivo.json não existe -- rode --rebuild-extensivo"}
    g = load_grade(grade_path)
    if not os.path.exists(pdf_path):
        return {"status": "missing_pdf",
                "msg": f"'{PDF_EXTENSIVO_NOME}' não encontrado ({pdf_path}; também "
                       "procurado em data/) -- check não verificável; o "
                       "grade_extensivo.json continua válido como derivado"}
    cur, old = sha256_file(pdf_path), g["_meta"].get("sha256")
    fresh = cur == old
    return {
        "status": "fresh" if fresh else "stale",
        "pdf_sha256": cur, "grade_sha256": old,
        "msg": "grade_extensivo em dia" if fresh else
               "PDF do Extensivo mudou desde a última grade -- rode --rebuild-extensivo",
    }


def main():
    ap = argparse.ArgumentParser(description="Derivador do cronograma (read-only).")
    ap.add_argument("--rebuild", action="store_true", help="(re)gera grade.json do PDF")
    ap.add_argument("--check", action="store_true", help="grade.json em dia vs PDF?")
    ap.add_argument("--json", action="store_true", help="imprime a grade")
    ap.add_argument("--gap", action="store_true", help="gap de volume vs meta")
    ap.add_argument("--radar", action="store_true", help="cobertura futura × performance (Fase 2)")
    ap.add_argument("--validate", action="store_true", help="asserções da Fase 1")
    ap.add_argument("--semana", type=int, help="filtra --json para a semana N")
    ap.add_argument("--desde", type=int, help="semana inicial p/ --gap/--radar (default: nominal por data)")
    ap.add_argument("--meta", type=int, default=None,
                    help="what-if p/ --gap (default: marco-alvo via performance.volume_vs_marco -- F88)")
    ap.add_argument("--rebuild-extensivo", action="store_true", dest="rebuild_extensivo",
                    help="(re)gera core/cronograma/grade_extensivo.json a partir do "
                         "'[52 wk] Cronograma Extensivo.pdf' (52 semanas -- plano-ssot-e-cards-v2 P1)")
    ap.add_argument("--check-extensivo", action="store_true", dest="check_extensivo",
                    help="grade_extensivo.json em dia vs o PDF do Extensivo? (sha256)")
    ap.add_argument("--expect-tasks", type=int, default=None, dest="expect_tasks",
                    help="override da contagem esperada de tarefas do --rebuild-extensivo "
                         "(default 735; só quando o PDF do EMED mudou de verdade)")
    args = ap.parse_args()

    if args.rebuild:
        g = rebuild()
        m = g["_meta"]
        print(f"grade.json gerado: {m['n_semanas']} semanas · {m['n_tasks']} tasks · {m['total_questoes']}q")
        print(f"  fonte: {m['fonte']} · sha256 {m['fonte_sha256'][:16]}… · S1={m['semana_1_inicio']}")
        ok, linhas = validate(g)
        print("\n".join(linhas))
        sys.exit(0 if ok else 1)
    if args.check:
        print(json.dumps(check(), ensure_ascii=False, indent=2))
        return
    if args.validate:
        ok, linhas = validate(load_grade())
        print("\n".join(linhas))
        sys.exit(0 if ok else 1)
    if args.gap:
        import app.utils.db as db
        con = db.get_connection()
        # F88: acumulado/meta da fonte unica (volume OFICIAL, inclui Simulado -- s126).
        # `cronograma_restante` continua sendo a parte que so o cronograma sabe.
        payload = gap_payload(con, load_grade(), meta=args.meta, desde=args.desde)
        con.close()
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return
    if args.radar:
        import app.utils.db as db
        from performance import get_por_area
        con = db.get_connection()
        pa = get_por_area(con)
        con.close()
        print(render_radar(radar(load_grade(), pa, desde_semana=args.desde)))
        return
    if args.json:
        g = load_grade()
        out = get_semana(g, args.semana) if args.semana else g
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    if args.rebuild_extensivo:
        try:
            g = rebuild_extensivo(expect_tasks=args.expect_tasks)
        except (ExtensivoContagemDivergente, FileNotFoundError, ValueError) as e:
            print(f"[ERRO] {e}")
            sys.exit(1)
        m = g["_meta"]
        print(f"grade_extensivo.json gerado: {m['n_semanas']} semanas · {m['n_tasks']} tarefas "
              f"(teoria={m['n_teoria']} revisao={m['n_revisao']} rpq={m['n_rpq']})")
        print(f"  fonte: {m['fonte']} · sha256 {m['sha256'][:16]}…")
        sys.exit(0)
    if args.check_extensivo:
        r = check_extensivo()
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(0 if r["status"] == "fresh" else 1)
    ap.print_help()


if __name__ == "__main__":
    main()
