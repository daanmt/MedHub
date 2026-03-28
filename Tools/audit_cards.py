import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'ipub.db'

with sqlite3.connect(DB) as conn:
    def q(sql): return conn.execute(sql).fetchone()[0]

    total       = q("SELECT COUNT(*) FROM flashcards")
    legacy      = q("SELECT COUNT(*) FROM flashcards WHERE quality_source='legacy' OR quality_source IS NULL")
    heuristic   = q("SELECT COUNT(*) FROM flashcards WHERE quality_source='heuristic'")
    h_flagged   = q("SELECT COUNT(*) FROM flashcards WHERE quality_source='heuristic_flagged'")
    needs_qual  = q("SELECT COUNT(*) FROM flashcards WHERE needs_qualitative=1")
    qualitative = q("SELECT COUNT(*) FROM flashcards WHERE quality_source='qualitative'")
    incomplete  = q("SELECT COUNT(*) FROM flashcards WHERE frente_pergunta IS NULL OR verso_resposta IS NULL")
    ui_fallback = q("""SELECT COUNT(*) FROM flashcards
                       WHERE frente_pergunta IS NULL OR verso_resposta IS NULL
                          OR frente_pergunta='' OR verso_resposta=''""")

    print(f"Total cards:               {total}")
    print(f"  Legacy (sem regen):      {legacy}")
    print(f"  Heuristic OK:            {heuristic}")
    print(f"  Heuristic flagged:       {h_flagged}")
    print(f"  Needs qualitative (1):   {needs_qual}")
    print(f"  Qualitative:             {qualitative}")
    print(f"  Campos incompletos:      {incomplete}")
    print(f"  UI caira em fallback:    {ui_fallback}")

    # Breakdown por tipo
    print()
    for tipo in ['elo_quebrado', 'armadilha']:
        n = q(f"SELECT COUNT(*) FROM flashcards WHERE tipo='{tipo}'")
        print(f"  tipo={tipo}: {n}")
