"""Corpus de flashcards do EMED 2024 -- colheita, extracao e consulta.

Nascido na sessao 124 (spec .vibeflow/specs/emed-flashcard-corpus-part-1.md):
o curso extensivo do EMED traz 1 deck de flashcards por tema (Flashc.pdf), no
formato atomico de referencia (frente = pagina impar, verso = par; watermark
"Estrategia MED" a limpar). Este CLI:

  --harvest --source <path>   Copia cada Flashc.pdf para
                              resumos/<area>/Flashcards - <Tema>.pdf (mapeando
                              a especialidade EMED -> taxonomia resumos),
                              extrai os pares frente/verso para um sidecar
                              co-locado .cards.json e escreve um relatorio.
                              Idempotente.
  --query --tema "X" [--area Y]
                              Resolve o tema -> deck (match normalizado exato ->
                              fuzzy difflib) e imprime os pares como JSON.

Fronteira dura: read-only no ipub.db (nao importa sqlite3). O corpus e so
referencia de autoria; a cunhagem/FSRS vive em insert_questao.py/insert_card_base.py.
Os PDFs e os .cards.json sao IP do EMED -> gitignored.
"""
import argparse
import difflib
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
RESUMOS_ROOT = REPO_ROOT / "resumos"

# Especialidade EMED (top folder, sem "_-_Extensivo") -> caminho relativo em resumos/
AREA_MAP = {
    "Ginecologia": "GO",
    "Obstetricia": "GO",
    "Cardiologia": "Clinica Medica/Cardiologia",
    "Dermatologia": "Clinica Medica/Dermatologia",
    "Endocrinologia": "Clinica Medica/Endocrinologia",
    "Gastroenterologia": "Clinica Medica/Gastroenterologia",
    "Hematologia": "Clinica Medica/Hematologia",
    "Hepatologia": "Clinica Medica/Hepatologia",
    "Infectologia": "Clinica Medica/Infectologia",
    "Nefrologia": "Clinica Medica/Nefrologia",
    "Neurologia": "Clinica Medica/Neurologia",
    "Pneumologia": "Clinica Medica/Pneumologia",
    "Psiquiatria": "Clinica Medica/Psiquiatria",
    "Reumatologia": "Clinica Medica/Reumatologia",
    "Pediatria": "Pediatria",
    "Medicina Preventiva": "Preventiva",
    "Cirurgia": "Cirurgia",
    "Ortopedia": "Cirurgia",
}

WATERMARK_LINES = {"Estrategia", "MED", "Estrategia MED", "Estratégia", "Estratégia MED"}

# Ruidos que vazam no texto extraido (watermarks variam por deck/fonte; legendas de figura).
NOISE_RE = [
    re.compile(r"Estrat[ée]gia\s*MED", re.I),
    re.compile(r"Medicina livre,?\s*venda proibida\.?", re.I),
    re.compile(r"(?:Twitter\s*)?@\s*livremedicina", re.I),
    re.compile(r"Legenda[:\s].*$", re.I),
    re.compile(r"Fonte[:\s].*$", re.I),
    re.compile(r"(?:Figura|Imagem)\s+retirad[ao].*$", re.I),
    re.compile(r"Retirad[ao]\s+do\s+manual.*$", re.I),
]

# Nomes de especialidade que aparecem como tag de categoria (usados so como referencia
# para o guard do common-affix; a frente e limpa pela especialidade REAL do deck).
SPECIALTY_CANON = [
    "Ginecologia", "Obstetricia", "Cardiologia", "Dermatologia", "Endocrinologia",
    "Gastroenterologia", "Hematologia", "Hepatologia", "Infectologia", "Nefrologia",
    "Neurologia", "Pneumologia", "Psiquiatria", "Reumatologia", "Pediatria",
    "Cirurgia", "Ortopedia", "Medicina Preventiva", "Preventiva",
]


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalize_key(s: str) -> str:
    """Chave de match: sem acento, minusculo, sem prefixo numerico, sem pontuacao."""
    s = strip_accents(s).lower()
    s = s.replace("_", " ")
    s = re.sub(r"^\s*\d+[\.\)\-]?\s*", "", s)  # tira "5. " / "12) "
    s = re.sub(r"[^a-z0-9\s]", " ", s)          # tira pontuacao (-, (), , ) p/ tokenizar
    s = re.sub(r"\s+", " ", s).strip()
    return s


def match_score(want: str, key: str) -> float:
    """Score 0-1 combinando containment de tokens da query, substring e difflib."""
    wt = [t for t in want.split() if t]
    kt = set(key.split())
    contain = sum(1 for t in wt if t in kt) / len(wt) if wt else 0.0
    substr = 1.0 if want and (want in key or key in want) else 0.0
    ratio = difflib.SequenceMatcher(None, want, key).ratio()
    return round(max(contain, substr, ratio), 3)


def map_area(top_folder: str):
    """Especialidade (nome do top folder) -> caminho relativo em resumos/, ou None."""
    spec = top_folder.replace("_-_Extensivo", "").replace("_", " ").strip()
    spec_na = strip_accents(spec)
    for key, dest in AREA_MAP.items():
        if strip_accents(key).lower() == spec_na.lower():
            return dest
    # fallback tolerante: "Medicina Preventiva intensivo" etc.
    if spec_na.lower().startswith("medicina preventiva"):
        return "Preventiva"
    return None


def resumos_dest_dir(rel: str) -> Path:
    """Resolve o caminho de destino real, tolerando acento (Clinica Medica)."""
    parts = rel.split("/")
    cur = RESUMOS_ROOT
    for part in parts:
        match = None
        if cur.exists():
            for child in cur.iterdir():
                if child.is_dir() and strip_accents(child.name).lower() == strip_accents(part).lower():
                    match = child
                    break
        cur = match if match else (cur / part)
    return cur


def clean_page(text: str) -> str:
    lines = [l.strip() for l in (text or "").splitlines()]
    lines = [l for l in lines if l and l not in WATERMARK_LINES]
    joined = " ".join(lines).strip()
    joined = re.sub(r"^MED\s*", "", joined)          # "MED" grudado do ultimo watermark
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined


def _strip_noise(text: str) -> str:
    """Remove watermarks e legendas de figura que vazam no texto."""
    for rx in NOISE_RE:
        text = rx.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_known(text: str, labels) -> str:
    """Remove um rotulo conhecido (especialidade/tema) colado no inicio ou fim,
    com ou sem espaco, case-insensitive. Ex.: 'EndocrinologiaQuais' -> 'Quais'."""
    for lab in labels:
        lab = (lab or "").strip()
        if len(lab) < 2:
            continue
        text = re.sub(r"^\s*" + re.escape(lab), "", text, flags=re.IGNORECASE).strip()
        text = re.sub(re.escape(lab) + r"\s*$", "", text, flags=re.IGNORECASE).strip()
    return text


def _affix_is_label(affix: str, tema: str, specialty: str) -> bool:
    """O affix comum e um rotulo (derivado do tema/especialidade) e nao conteudo real?"""
    a = normalize_key(affix)
    if len(a) < 3:
        return False
    for ref in (normalize_key(tema), normalize_key(specialty)):
        if ref and (a in ref or ref in a):
            return True
    return a in {normalize_key(s) for s in SPECIALTY_CANON}


def _strip_common_affix(cards, field, tema, specialty):
    """Tira o prefixo/sufixo comum a TODOS os cards do campo -- a tag curta de tema
    (ex.: 'DRC ', '.Hepatites virais') que so aparece repetida. Guardado: so remove
    se o affix for um rotulo (nao conteudo), protegendo respostas tipo 'Sim'/'Nao'."""
    vals = [c[field] for c in cards if c[field].strip()]
    if len(vals) < 2:
        return
    pfx = os.path.commonprefix(vals)
    sfx = os.path.commonprefix([v[::-1] for v in vals])[::-1]
    strip_pfx = _affix_is_label(pfx, tema, specialty)
    strip_sfx = _affix_is_label(sfx, tema, specialty)
    for c in cards:
        t = c[field]
        if not t.strip():
            continue
        if strip_pfx and t.startswith(pfx):
            t = t[len(pfx):]
        if strip_sfx and len(t) > len(sfx) and t.endswith(sfx):
            t = t[:len(t) - len(sfx)]
        c[field] = t.strip(" .:;,-" + chr(0x2013) + chr(0x2014))


def clean_deck(cards, specialty, tema):
    """Limpeza a nivel de deck: noise (watermark/legenda) + tag de especialidade nas
    frentes + tag de tema nos versos (conhecida e curta via common-affix)."""
    for c in cards:
        c["frente"] = _strip_known(_strip_noise(c["frente"]), [specialty])
        c["verso"] = _strip_known(_strip_noise(c["verso"]), [tema, specialty])
    _strip_common_affix(cards, "verso", tema, specialty)
    _strip_common_affix(cards, "frente", tema, specialty)
    return [c for c in cards if c["frente"].strip() or c["verso"].strip()]


def extract_cards(pdf_path: Path, specialty: str, tema: str):
    """Extrai [{n, frente, verso}] do deck. frente=pagina impar, verso=par."""
    from PyPDF2 import PdfReader
    reader = PdfReader(str(pdf_path))
    pages = [clean_page(p.extract_text() or "") for p in reader.pages]
    cards = [{"n": i // 2 + 1, "frente": pages[i], "verso": pages[i + 1]}
             for i in range(0, len(pages) - 1, 2)]
    return clean_deck(cards, specialty, tema)


def harvest(source: Path, force: bool = False):
    if not source.exists():
        print(json.dumps({"error": f"source nao existe: {source}"}, ensure_ascii=False))
        return 1
    report = {"total_pdfs": 0, "copied": 0, "skipped_existing": 0, "extracted": 0,
              "unmapped": [], "empty_decks": [], "errors": [], "collisions": [],
              "pruned": [], "decks": []}
    expected = set()

    for pdf in source.rglob("Flashc.pdf"):
        report["total_pdfs"] += 1
        rel = pdf.relative_to(source)
        top_folder = rel.parts[0]
        # Tema = pasta mais profunda (nome completo e mais limpo). 3 variantes:
        #   <Esp>\<Tema>\<Tema>\Flashc.pdf   (dup)        -> deepest = Tema
        #   <Esp>\<Tema>\<TemaCompleto>\...  (curto/full) -> deepest = TemaCompleto (melhor)
        #   <Esp>\<Tema>\1\Flashc.pdf        (numerada)   -> deepest = "1" -> cai pra rel.parts[1]
        deepest = pdf.parent.name
        tema_folder = deepest if not deepest.isdigit() else rel.parts[1]
        tema = tema_folder.replace("_", " ").strip()
        area_rel = map_area(top_folder)
        if area_rel is None:
            report["unmapped"].append({"pdf": str(rel), "top": top_folder})
            continue
        dest_dir = resumos_dest_dir(area_rel)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_pdf = dest_dir / f"Flashcards - {tema}.pdf"
        sidecar = dest_dir / f"Flashcards - {tema}.cards.json"
        expected.add(dest_pdf)

        # Idempotencia: deck ja copiado (mesmo tamanho) E ja extraido -> pula por completo
        # (evita reler o HD externo em re-runs).
        if (not force and dest_pdf.exists() and dest_pdf.stat().st_size == pdf.stat().st_size
                and sidecar.exists()):
            report["skipped_existing"] += 1
            try:
                n = json.loads(sidecar.read_text(encoding="utf-8")).get("n_cards")
            except Exception:
                n = None
            report["decks"].append({"tema": tema, "area": area_rel, "n_cards": n,
                                    "pdf": str(dest_pdf.relative_to(REPO_ROOT))})
            continue

        if dest_pdf.exists() and dest_pdf.stat().st_size == pdf.stat().st_size:
            report["skipped_existing"] += 1
        elif dest_pdf.exists():
            report["collisions"].append({"tema": tema, "dest": str(dest_pdf.relative_to(REPO_ROOT))})
            shutil.copy2(pdf, dest_pdf)
            report["copied"] += 1
        else:
            shutil.copy2(pdf, dest_pdf)
            report["copied"] += 1

        try:
            cards = extract_cards(pdf, top_folder.replace("_-_Extensivo", "").replace("_", " ").strip(), tema)
            sidecar = dest_dir / f"Flashcards - {tema}.cards.json"
            sidecar.write_text(json.dumps(
                {"tema": tema, "area": area_rel, "n_cards": len(cards), "cards": cards},
                ensure_ascii=False, indent=1), encoding="utf-8")
            report["extracted"] += 1
            deck_rec = {"tema": tema, "area": area_rel, "n_cards": len(cards),
                        "pdf": str(dest_pdf.relative_to(REPO_ROOT))}
            report["decks"].append(deck_rec)
            if not cards:
                report["empty_decks"].append({"tema": tema, "area": area_rel, "pdf": str(rel)})
        except Exception as e:
            report["errors"].append({"pdf": str(rel), "error": repr(e)})

    # Auto-prune: remove decks Flashcards-* orfaos (renomeacoes/execucoes antigas) que
    # nao correspondem a nenhum deck do source atual -- torna o harvest self-healing.
    for existing in RESUMOS_ROOT.rglob("Flashcards - *.pdf"):
        if existing not in expected:
            side = existing.with_name(existing.stem + ".cards.json")
            try:
                existing.unlink()
                if side.exists():
                    side.unlink()
                report["pruned"].append(str(existing.relative_to(REPO_ROOT)))
            except Exception as e:
                report["errors"].append({"prune": str(existing), "error": repr(e)})

    # QA leve pos-colheita: varre os sidecars locais (sem reler o HD) e sinaliza
    # cards de resposta-imagem (verso vazio = diagrama/foto sem texto extraivel).
    img_cards, img_heavy = 0, []
    for sc in RESUMOS_ROOT.rglob("Flashcards - *.cards.json"):
        try:
            cards = json.loads(sc.read_text(encoding="utf-8")).get("cards", [])
        except Exception:
            continue
        empty_v = sum(1 for c in cards if not (c.get("verso") or "").strip())
        img_cards += empty_v
        if cards and empty_v / len(cards) >= 0.30:
            img_heavy.append({"deck": str(sc.relative_to(REPO_ROOT)),
                              "empty_verso": empty_v, "n_cards": len(cards)})
    report["image_answer_cards"] = img_cards
    report["image_heavy_decks"] = img_heavy

    report_path = REPO_ROOT / "artifacts" / "emed_harvest_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    summary = {k: v for k, v in report.items() if k not in ("decks",)}
    summary["report_path"] = str(report_path.relative_to(REPO_ROOT))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


def _iter_sidecars(area=None):
    root = RESUMOS_ROOT
    if area:
        d = resumos_dest_dir(area)
        roots = [d] if d.exists() else []
    else:
        roots = [root]
    for r in roots:
        yield from r.rglob("Flashcards - *.cards.json")


def query(tema: str, area=None):
    want = normalize_key(tema)
    scored = []
    for sc in _iter_sidecars(area):
        try:
            data = json.loads(sc.read_text(encoding="utf-8"))
        except Exception:
            continue
        cand_tema = data.get("tema") or sc.name.replace("Flashcards - ", "").replace(".cards.json", "")
        key = normalize_key(cand_tema)
        scored.append({"exact": key == want, "score": match_score(want, key),
                       "tema": cand_tema, "area": data.get("area"),
                       "deck": str(sc.relative_to(REPO_ROOT)), "n_cards": data.get("n_cards"),
                       "cards": data.get("cards", [])})
    scored.sort(key=lambda x: (x["exact"], x["score"]), reverse=True)
    candidates = [{"tema": s["tema"], "area": s["area"], "score": s["score"]} for s in scored[:5]]

    def emit(match, top=None):
        out = {"match": match, "query": tema, "candidates": candidates}
        if top is not None:
            out.update({"tema": top["tema"], "area": top["area"], "deck": top["deck"],
                        "n_cards": top["n_cards"], "cards": top["cards"]})
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0

    if not scored:
        return emit("none")
    exact_hits = [s for s in scored if s["exact"]]
    if len(exact_hits) == 1:
        return emit("exact", exact_hits[0])
    top = scored[0]
    second = scored[1]["score"] if len(scored) > 1 else 0.0
    # match confiante = alto score E claramente a frente do 2o (evita chute em empate)
    if top["score"] >= 0.85 and (top["score"] - second) >= 0.12:
        return emit("fuzzy", top)
    return emit("none")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harvest", action="store_true", help="Colher + extrair os decks do EMED")
    ap.add_argument("--source", help="Raiz do corpus EMED (ex.: D:\\Med\\Estrategia 2024 Extensivo\\Extensivo)")
    ap.add_argument("--query", action="store_true", help="Consultar o deck de um tema")
    ap.add_argument("--tema", help="Tema a consultar")
    ap.add_argument("--area", help="Filtro de area (opcional)")
    ap.add_argument("--force", action="store_true", help="Re-extrai todos (ignora idempotencia)")
    args = ap.parse_args()

    if args.harvest:
        if not args.source:
            print(json.dumps({"error": "--harvest exige --source"}, ensure_ascii=False))
            return 1
        return harvest(Path(args.source), force=args.force)
    if args.query:
        if not args.tema:
            print(json.dumps({"error": "--query exige --tema"}, ensure_ascii=False))
            return 1
        return query(args.tema, args.area)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
