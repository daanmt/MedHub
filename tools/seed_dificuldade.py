"""seed_dificuldade.py — calibração inicial das notas de dificuldade (PRD s094 §4.7).

Persiste as 8 notas-exemplo (fonte='usuario', soberanas) via db.set_dificuldade.
Temas canônicos do cronograma que ainda não têm linha em taxonomia_cronograma
(temas futuros da S11) são criados com volume 0 — consistente com as linhas
volume-0 já existentes para temas canônicos (ex.: Hepatites Virais). Nomes
casados com core/cronograma/grade.json. Idempotente: re-rodar sobrescreve as
mesmas notas e não duplica linhas (UNIQUE(area,tema) + checagem prévia).

Uso: python tools/seed_dificuldade.py [--dry-run]
"""
import argparse
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:                                   # UTF-8 no console cp1252 do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.utils.db as db  # noqa: E402

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ipub.db")

# (area, tema, nota) — nomes canônicos casados com grade.json / taxonomia. PRD §4.7.
SEED = [
    ("Hepato", "Hepatites Virais", 8),
    ("Preventiva", "Medicina de Família e Comunidade", 3),
    ("Pediatria", "Doenças Exantemáticas", 6),
    ("Cirurgia", "Cirurgia Infantil", 8),
    ("Ginecologia", "Vulvovaginites", 7),
    ("Obstetrícia", "Síndromes Hipertensivas da Gestação", 6),
    ("Pediatria", "Imunizações", 9),
    ("Infecto", "Sepse", 6),
]


def _ensure_linha(area, tema):
    """Cria a linha (area, tema) com volume 0 se não existir. Returns (tema_id, criou)."""
    tid = db.resolve_tema_id(area, tema)
    if tid is not None:
        return tid, False
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO taxonomia_cronograma "
            "(area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos) "
            "VALUES (?, ?, 0, 0, 0.0)", (area, tema))
        conn.commit()
    finally:
        conn.close()
    return db.resolve_tema_id(area, tema), True


def main():
    ap = argparse.ArgumentParser(description="Seed das notas de dificuldade (PRD §4.7).")
    ap.add_argument("--dry-run", action="store_true", help="Só mostra o plano, não grava")
    args = ap.parse_args()

    aplicadas = criadas = 0
    for area, tema, nota in SEED:
        existe = db.resolve_tema_id(area, tema) is not None
        if args.dry_run:
            print(f"  [{'existe' if existe else 'CRIAR '}] {area} | {tema} -> {nota}")
            continue
        _tid, criou = _ensure_linha(area, tema)
        criadas += int(criou)
        ok = db.set_dificuldade(area, tema, nota, "usuario")
        aplicadas += int(ok)
        print(f"  [{'novo' if criou else 'ok  '}] {area} | {tema} -> {nota} "
              f"({'gravou' if ok else 'FALHOU'})")
    if not args.dry_run:
        print(f"Seed OK - {aplicadas}/{len(SEED)} notas aplicadas; {criadas} linha(s) criada(s).")
    return args.dry_run or aplicadas == len(SEED)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
