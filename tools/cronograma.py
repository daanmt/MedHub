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
from datetime import date, datetime, timedelta

try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

PDF_PATH = os.path.join(ROOT, "Cronograma.pdf")
GRADE_PATH = os.path.join(ROOT, "core", "cronograma", "grade.json")

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


def normaliza_tipo(tipo_verbatim):
    """tipo_norm ∈ {teoria, revisao, revisao_questoes, outro} — calibra a aula por bloco."""
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
    m = re.search(r"\(([^)]*)\)\s*$", s)      # "...tema (Tipo)" — tipo no fim entre parênteses
    if m:
        return s[:m.start()].strip(), m.group(1).strip()
    return s, ""                              # tema sem tipo explícito


def _parse_detail(detail_lines):
    """{N: {tema_detail, questoes, raw}} — tema via 'Livro Digital: tema (Tipo)' + contagem de Links."""
    out = {}
    for n, lines in _split_tarefas(detail_lines).items():
        s = _dewrap(" ".join(lines))
        m = re.search(r"Livro Digital:\s*(.+?)\s*\((?:Teoria|Revis[ãa]o)[^)]*\)", s)
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
            # `tipo_norm=='teoria'` era largo demais — marcava 279/352 (79%) como extensivo,
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
            })

        # total da SEMANA = soma de TODOS os "Link - NN questões" da semana (validado: S10=273,
        # S11-28=6689). NÃO atribuímos count por task: o PDF não amarra link[i]↔task[i] de forma
        # garantida (ultraplan §c.5) → o consumidor rateia igual (total_questoes / n_tasks).
        wq = sum(int(c) for c in re.findall(r"Link\s*-\s*(\d+)\s*quest", "\n".join(wl)))
        total_q += wq
        inicio = s1 + timedelta(days=(n - 1) * 7)
        semanas.append({
            "semana": n,
            "inicio": inicio.isoformat(),
            "fim": (inicio + timedelta(days=6)).isoformat(),
            "total_questoes": wq,
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
        return {"status": "missing", "msg": "grade.json não existe — rode --rebuild"}
    g = load_grade(grade_path)
    cur, old = sha256_file(pdf_path), g["_meta"].get("fonte_sha256")
    fresh = cur == old
    return {
        "status": "fresh" if fresh else "stale",
        "pdf_sha256": cur, "grade_sha256": old,
        "msg": "grade em dia" if fresh else "PDF mudou desde a última grade — rode --rebuild (W5)",
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


def gap_volume(grade, total_acum, meta=10000, desde_semana=None):
    """Gap honesto de volume (ultraplan §a.3): mesmo a 100% do cronograma, falta banco extra?"""
    if desde_semana is None:
        desde_semana = semana_corrente(grade) or 1
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


# ───────────────────────── Fase 2 — Radar cobertura × performance ─────────────────────────
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
        return None, "rótulo 'GO' ambíguo Gineco/Obstetrícia — não atribuído (split não-trivial)"
    return None, f"rótulo desconhecido {a!r} fora de AREAS_VALIDAS — ignorado"


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
        rate = s["total_questoes"] / s["n_tasks"]          # rateio igual (ultraplan §c.5)
        bucket = cov_pre if s["inicio"] <= enamed else cov_post
        for t in s["tasks"]:
            if t["multi_area"]:
                continue
            A = t["area_norm"]
            bucket[A] = bucket.get(A, 0.0) + rate
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
            f"- {row['flag']} **{row['area']}** — {row['feito_q']}q feito ({row['pct']}%) · "
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
               + (f" — fora: {bad}" if bad else ""))
    ok &= not bad

    # quantas áreas das 20 canônicas o cronograma cobre (single, não-Multi)
    cobertas = {tk["area_norm"] for s in grade["semanas"] for tk in s["tasks"] if not tk["multi_area"]}
    out.append(f"  cobertura: {len(cobertas)}/20 áreas canônicas aparecem como task single")
    return ok, out


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
    ap.add_argument("--meta", type=int, default=10000, help="meta de volume p/ --gap")
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
        from performance import get_totais
        con = db.get_connection()
        tot, _ = get_totais(con)
        con.close()
        print(json.dumps(gap_volume(load_grade(), tot or 0, args.meta, args.desde),
                         ensure_ascii=False, indent=2))
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
    ap.print_help()


if __name__ == "__main__":
    main()
