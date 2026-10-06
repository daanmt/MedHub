#!/usr/bin/env python3
"""
cobertura_conhecimento -- relatorio read-only de cobertura de SSOT clinico (F16a).

Cruza resumos/**/*.pdf (fontes) contra resumos/**/*.md (SSOT cunhado), pareando
por stem normalizado (+ fuzzy leve como desempate), e emite a fila de PDFs-orfaos
(sem .md) ordenada por sinal de rendimento: temas da SEMANA CORRENTE primeiro,
depois presenca na grade do cronograma, depois volume/erros na taxonomia.

E06 (s216): a SEMANA CORRENTE e a do PLANO (`plano_tarefas`), pela regua do
`plano.panorama` (a mesma do boot e do Painel), e os temas dela saem das tarefas
dessa semana. ⚰️ *Ate a s216 vinha de `preparacao_estado.semana_conteudo` (fallback:
calendario do `grade.json` da Reta Final) e cruzava com os temas da grade antiga: em
05/10/2026 o relatorio chamava de corrente a S17 da grade, com o plano na S4.* A grade
antiga segue so como sinal de prioridade (`[grade]`) da fila restante.

Read-only estrito: NAO cria, move ou deleta nenhum arquivo; apenas relata.

Uso:
    python tools/cobertura_conhecimento.py
    python tools/cobertura_conhecimento.py --dir resumos
"""

import argparse
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

# Raiz do projeto no path para imports absolutos (padrao dos CLIs em tools/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Limiares de pareamento fuzzy (SequenceMatcher.ratio sobre stems normalizados).
FUZZY_COBERTO = 0.90   # >= => considerado coberto (par fuzzy de alta confianca)
FUZZY_REVISAR = 0.75   # [REVISAR, COBERTO) => orfao COM candidato a revisar


def normaliza_stem(nome: str) -> str:
    """Normaliza um nome de arquivo/tema para pareamento tolerante.

    Remove prefixo numerico do EMED ("12 - Tema", "12. Tema", "12) Tema"),
    acentos, case e pontuacao; colapsa espacos. O pareamento exato e pessimista
    (332/333 orfaos no censo cru); esta normalizacao e o que torna o match util.
    """
    s = re.sub(r"^\s*\d+\s*[-.)_]*\s*", "", nome)          # prefixo numerico EMED
    s = unicodedata.normalize("NFKD", s)                    # decompoe acentos
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)                       # pontuacao -> espaco
    return s.strip()


def coletar(base_dir: str):
    """Varre base_dir e retorna (list[Path] pdfs, list[Path] mds).

    Le apenas nomes de arquivo (nao abre PDFs). INDEX.md e ignorado.
    """
    base = Path(base_dir)
    pdfs = sorted(p for p in base.rglob("*") if p.suffix.lower() == ".pdf")
    mds = sorted(p for p in base.rglob("*.md") if p.name != "INDEX.md")
    return pdfs, mds


def parear(pdf_paths, md_paths):
    """Pareia cada PDF contra os .md por stem normalizado + fuzzy leve.

    Retorna list[dict] com chaves: path, stem, norm, coberto (bool),
    via ('exato'|'fuzzy'|None), candidato (str|None), score (float).
    """
    md_norms = [(normaliza_stem(m.stem), m.stem) for m in md_paths]
    md_norm_set = {n for n, _ in md_norms}

    out = []
    for p in pdf_paths:
        pnorm = normaliza_stem(p.stem)
        if pnorm in md_norm_set:
            out.append({"path": str(p), "stem": p.stem, "norm": pnorm,
                        "coberto": True, "via": "exato", "candidato": None, "score": 1.0})
            continue
        # melhor candidato fuzzy entre os .md
        melhor_score, melhor_nome = 0.0, None
        for mnorm, mstem in md_norms:
            r = SequenceMatcher(None, pnorm, mnorm).ratio()
            if r > melhor_score:
                melhor_score, melhor_nome = r, mstem
        if melhor_score >= FUZZY_COBERTO:
            out.append({"path": str(p), "stem": p.stem, "norm": pnorm,
                        "coberto": True, "via": "fuzzy", "candidato": melhor_nome,
                        "score": round(melhor_score, 2)})
        elif melhor_score >= FUZZY_REVISAR:
            out.append({"path": str(p), "stem": p.stem, "norm": pnorm,
                        "coberto": False, "via": None, "candidato": melhor_nome,
                        "score": round(melhor_score, 2)})
        else:
            out.append({"path": str(p), "stem": p.stem, "norm": pnorm,
                        "coberto": False, "via": None, "candidato": None, "score": 0.0})
    return out


def _area_do_path(path: str, base_dir: str) -> str:
    """Primeira componente sob base_dir (ex.: resumos/Cirurgia/... -> 'Cirurgia')."""
    try:
        rel = Path(path).resolve().relative_to(Path(base_dir).resolve())
        return rel.parts[0] if len(rel.parts) > 1 else ""
    except Exception:
        return ""


def priorizar(orfaos, semana_norms, grade_norms, taxonomia):
    """Ordena os orfaos por sinal de rendimento.

    orfaos: list[dict] com 'stem','norm','area','candidato','score'.
    taxonomia: dict norm -> (volume, erros, area).
    Retorna (semana, restantes): listas enriquecidas com in_grade/volume/erros.
    A secao 'semana' e separada; as restantes ordenam por presenca na grade,
    depois volume, erros e nome.
    """
    enriq = []
    for o in orfaos:
        vol, err, area_tax = taxonomia.get(o["norm"], (0, 0, ""))
        enriq.append({
            **o,
            "in_semana": o["norm"] in semana_norms,
            "in_grade": o["norm"] in grade_norms,
            "volume": vol,
            "erros": err,
            "area": o.get("area") or area_tax,
        })

    def chave(x):
        return (0 if x["in_grade"] else 1, -x["volume"], -x["erros"], x["stem"].lower())

    def chave_semana(x):
        return (-x["volume"], -x["erros"], x["stem"].lower())

    semana = sorted([x for x in enriq if x["in_semana"]], key=chave_semana)
    restantes = sorted([x for x in enriq if not x["in_semana"]], key=chave)
    return semana, restantes


def carregar_grade():
    """Grade antiga da Reta Final (`grade.json`), so para o sinal `[grade]`. Degrada -> None."""
    try:
        import cronograma
        return cronograma.load_grade()
    except Exception:
        return None


def temas_norm_tarefas(linhas, semana):
    """Stems normalizados dos temas das tarefas VIVAS (nao cortadas) de UMA semana do plano.

    O tema do plano junta temas com `|`/`;`/`,` -- e o `|` tambem e quebra de linha do PDF
    no meio de um nome ("Endocrino- | Metabolica"). Entram o tema inteiro E cada parte."""
    out = set()
    for l in linhas:
        if l.get("semana_plano") != semana or l.get("status") == "cortada":
            continue
        tema = str(l.get("tema") or "")
        for parte in [tema] + [p for p in re.split(r"[|;,]", tema) if p.strip()]:
            norm = normaliza_stem(parte)
            if norm:
                out.add(norm)
    return out


def semana_do_plano(linhas, calendario, hoje):
    """(semana, temas_norm) da semana corrente do PLANO. PURA sobre os argumentos.

    A semana e a do `plano.panorama` -- reuso, nao copia: calendario da trilha (primeira
    semana cujo fim >= hoje), com fallback na menor semana com pendencia. Sem semana ->
    (None, set())."""
    import plano
    pan = plano.panorama(linhas, calendario, hoje)
    if not pan or not pan.get("semana"):
        return None, set()
    return pan["semana"], temas_norm_tarefas(linhas, pan["semana"])


def carregar_semana():
    """`semana_do_plano` sobre o `plano_tarefas` real. Degrada gracioso -> (None, set())."""
    try:
        import plano
        from app.utils import db
        return semana_do_plano(db.plano_listar(), plano.calendario_trilha(), db.hoje())
    except Exception:
        return None, set()


def temas_norm_grade(grade):
    if not grade:
        return set()
    out = set()
    for s in grade.get("semanas", []):
        for t in s.get("tasks", []):
            if t.get("tema"):
                out.add(normaliza_stem(t["tema"]))
    return out


def taxonomia_por_norm():
    """dict norm -> (volume, erros, area), agregando temas com o mesmo stem."""
    from app.utils import db
    out = {}
    for row in db.get_taxonomia_rendimento():
        k = normaliza_stem(row.get("tema", "") or "")
        if not k:
            continue
        vol = int(row.get("volume") or 0)
        err = int(row.get("erros") or 0)
        cur = out.get(k, (0, 0, ""))
        out[k] = (cur[0] + vol, cur[1] + err, row.get("area") or cur[2])
    return out


def _fmt_linha(x, marca_grade=False):
    grade_tag = "[grade] " if (marca_grade and x["in_grade"]) else ""
    rev = f"  {{rev: {x['candidato']} ~{x['score']}}}" if x.get("candidato") else ""
    area = f" area={x['area']}" if x["area"] else ""
    return f"  {grade_tag}{x['stem']}{area} vol={x['volume']} err={x['erros']}{rev}"


def render(pareado, semana_orfaos, restantes, n_pdfs, n_mds, semana_n):
    linhas = []
    cobertos = [p for p in pareado if p["coberto"]]
    exato = sum(1 for p in cobertos if p["via"] == "exato")
    fuzzy = sum(1 for p in cobertos if p["via"] == "fuzzy")
    n_orfaos = len(semana_orfaos) + len(restantes)

    linhas.append("== Cobertura de Conhecimento (resumos/) ==")
    linhas.append(f"PDFs-fonte  : {n_pdfs}")
    linhas.append(f".md cunhados: {n_mds}")
    linhas.append(f"Cobertos    : {len(cobertos)} ({exato} exato, {fuzzy} fuzzy)")
    linhas.append(f"Orfaos      : {n_orfaos}")
    linhas.append("")

    if semana_n:
        linhas.append(f"-- Temas da SEMANA CORRENTE do plano (S{semana_n}) sem .md --")
        if semana_orfaos:
            for x in semana_orfaos:
                linhas.append(_fmt_linha(x))
        else:
            linhas.append("  (nenhum orfao na semana corrente)")
    else:
        linhas.append("-- Semana corrente: plano indisponivel (`python tools/plano.py --panorama`) --")
    linhas.append("")

    linhas.append("-- Fila de autoria priorizada (orfaos restantes) --")
    if restantes:
        for x in restantes:
            linhas.append(_fmt_linha(x, marca_grade=True))
    else:
        linhas.append("  (nenhum)")

    return "\n".join(linhas)


def semana_orfaos_correntes(dir_resumos: str = "resumos"):
    """Temas da semana corrente do PLANO SEM .md canonico, + numero da semana.

    Reusa o pipeline de cobertura (coletar -> parear -> semana -> priorizar) sem
    imprimir -- consumido pelo WARN de tools/auto_check.py (spec mecanismo-conhecimento
    part-3). Retorna (list[dict] orfaos_da_semana, int semana_n).

    Degrada para ([], 0) quando o plano esta indisponivel ou qualquer etapa falha:
    silencio, nunca falso-positivo (mesma disciplina do relatorio).
    """
    try:
        pdfs, mds = coletar(dir_resumos)
        pareado = parear(pdfs, mds)
        semana_n, semana_norms = carregar_semana()
        if not semana_n:
            return [], 0
        grade_norms = temas_norm_grade(carregar_grade())
        taxonomia = taxonomia_por_norm()
        orfaos = [{"stem": p["stem"], "norm": p["norm"],
                   "area": _area_do_path(p["path"], dir_resumos),
                   "candidato": p["candidato"], "score": p["score"]}
                  for p in pareado if not p["coberto"]]
        semana_orfaos, _ = priorizar(orfaos, semana_norms, grade_norms, taxonomia)
        return semana_orfaos, semana_n
    except Exception:
        return [], 0


def main():
    parser = argparse.ArgumentParser(
        description="Relatorio read-only de cobertura de SSOT clinico (PDFs vs .md)."
    )
    parser.add_argument("--dir", default="resumos",
                        help="Diretorio raiz dos resumos (default: resumos)")
    args = parser.parse_args()

    if not Path(args.dir).exists():
        print(f"Erro: diretorio '{args.dir}' nao encontrado.")
        sys.exit(1)

    pdfs, mds = coletar(args.dir)
    pareado = parear(pdfs, mds)

    semana_n, semana_norms = carregar_semana()
    grade_norms = temas_norm_grade(carregar_grade())
    taxonomia = taxonomia_por_norm()

    orfaos = [{"stem": p["stem"], "norm": p["norm"],
               "area": _area_do_path(p["path"], args.dir),
               "candidato": p["candidato"], "score": p["score"]}
              for p in pareado if not p["coberto"]]

    semana_orfaos, restantes = priorizar(orfaos, semana_norms, grade_norms, taxonomia)
    print(render(pareado, semana_orfaos, restantes, len(pdfs), len(mds), semana_n))
    sys.exit(0)


if __name__ == "__main__":
    main()
