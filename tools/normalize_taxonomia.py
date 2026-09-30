"""normalize_taxonomia.py — saneia taxonomia_cronograma (Fase 1 da curadoria de cards, s097).

[DESTRUTIVO] O `--apply` so roda depois do backup FIXADO do proprio inicio (F137 parte 2; recusa sem ele).
`--dry-run` é o default; `--apply` grava.

Resolve o que `dedup_taxonomia.py` NÃO pega (ele agrupa por (area,tema) EXATO):
  - encoding/acento (Sistemas de Informacao vs Informação);
  - áreas inválidas fora de AREAS_VALIDAS (GO, Clinica Medica) -> dissolver na especialidade;
  - duplicatas CONCEITUAIS (mesmo tema clínico, nomes diferentes: DRC x3, Hipertensivas x2);
  - [bulk]/Geral totalmente vazios (0 cards e 0 questões).

Operações declarativas abaixo. Transação atômica (with con); re-aponta FKs
(questoes_erros.tema_id, flashcards.tema_id) nos merges; recria UNIQUE(area,tema)
no fim (falha => duplicata restante => rollback). O dry-run simula o estado final
e acusa colisões ANTES de aplicar.

Uso:
    python tools/normalize_taxonomia.py            # dry-run (default)
    python tools/normalize_taxonomia.py --apply     # grava
"""
import argparse
import os
import sqlite3
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

# --- Operações declarativas -------------------------------------------------
# RODADA 1 (aplicada 2026-06-28, s097): Obstetricia->Obstetrícia; dissolução das
# áreas fantasma Clinica Medica e GO; merges Sist.Informação / Planej.Familiar /
# DRC x3 / Hipertensivas da Gestação; 10 [bulk]/Geral vazios. (115 -> 100 temas)
#
# RODADA 2 (aplicada; esporotricose 229<-230 + trofoblástica 224<-225).
#
# RODADA 3 (s207, F67 -- M3 do operador em 29/09/2026: "Aprovar em bloco", lista do
# docs/DRYRUN-F65-F67-2026-09-09.md §4 + as 3 novas do mesmo tipo mostradas a ele no chat
# da s207, que escolheu "As 11"): sobrevive a linha da area CANONICA; a area fantasma
# (GO, Clinica Medica -- F89) sai. Ficam SEPARADOS por decisao: Asma Pediatria x Pneumo,
# TCE Neuro x Pediatria, Medidas de Saude Coletiva Pt. I/II. Operações ativas abaixo:
RENAME_AREA = []
MOVE_TEMA = []
RENAME_TEMA = []

# Fusões: (sobrevivente_id, [perdedores], nome_final, area_final)
MERGE = [
    (253, [139], 'Cirurgia Infantil', 'Cirurgia'),  # <- 139 [Cirurgia] Cirurgia Infantil I
    (282, [233], 'Asma na Infância', 'Pediatria'),  # <- 233 [Pediatria] Asma na infância
    (344, [301], 'Endometriose', 'Ginecologia'),  # <- 301 [GO] Endometriose
    (337, [417], 'Câncer de Mama - Fatores de Risco', 'Ginecologia'),  # <- 417 [GO] Câncer de Mama - Fatores de Risco
    (199, [348], 'Assistência ao Parto', 'Obstetrícia'),  # <- 348 [GO] Assistência ao Parto
    (272, [286], 'Anemias Hemolíticas', 'Hemato'),  # <- 286 [Clínica Médica] Anemias Hemolíticas
    (223, [347], 'Gravidez ectópica', 'Ginecologia'),  # <- 347 [GO] Gravidez ectópica
    (266, [285], 'Sepse', 'Infecto'),  # <- 285 [Clínica Médica] Sepse
    (465, [431], 'Doenças de Vulva e Vagina', 'Ginecologia'),  # <- 431 [GO] Doenças de Vulva e Vagina
    (484, [300], 'Pré-Natal', 'Obstetrícia'),  # <- 300 [GO] Pré-Natal
    (464, [419], 'Tumores Anexiais e Câncer de Ovário', 'Ginecologia'),  # <- 419 [GO] Tumores Anexiais e Câncer de Ovário
]

DELETE_TEMA = []

#: Toda tabela com `tema_id -> taxonomia_cronograma(id)` (s207). Fusao que esquece uma deixa
#: linha orfa; o VERIF do fim confere as quatro.
TABELAS_COM_TEMA = ("questoes_erros", "flashcards", "review_log", "questao_habilidades")


def nchild(cur, tid):
    return (cur.execute("SELECT COUNT(*) FROM questoes_erros WHERE tema_id=?", (tid,)).fetchone()[0]
            + cur.execute("SELECT COUNT(*) FROM flashcards WHERE tema_id=?", (tid,)).fetchone()[0])


def name(cur, tid):
    r = cur.execute("SELECT area, tema FROM taxonomia_cronograma WHERE id=?", (tid,)).fetchone()
    return f"[{r[0]}] {r[1]}" if r else "(INEXISTENTE)"


def simulate(cur):
    """Estado final (area,tema) por id após as operações; retorna lista de colisões."""
    final = {tid: (area, tema) for tid, area, tema in
             cur.execute("SELECT id, area, tema FROM taxonomia_cronograma").fetchall()}
    for de, para in RENAME_AREA:
        for tid in list(final):
            if final[tid][0] == de:
                final[tid] = (para, final[tid][1])
    for tid, area in MOVE_TEMA:
        if tid in final:
            final[tid] = (area, final[tid][1])
    for tid, nome in RENAME_TEMA:
        if tid in final:
            final[tid] = (final[tid][0], nome)
    for surv, losers, nome, area in MERGE:
        final[surv] = (area, nome)
        for L in losers:
            final.pop(L, None)
    for tid in DELETE_TEMA:
        final.pop(tid, None)
    cnt = Counter(final.values())
    return final, [k for k, v in cnt.items() if v > 1]


def _fixar_antes(ato, db_path):
    """F137 parte 2: o ponto de retorno FIXADO do proprio inicio do ato (`backup_db`). Levanta
    `SemPontoDeRetorno` quando nao ha -- quem chama RECUSA e nada e gravado."""
    _tools = os.path.dirname(os.path.abspath(__file__))
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    import backup_db
    return backup_db.fixar_antes_do_ato(ato, db=db_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="Grava (default: dry-run)")
    args = ap.parse_args()
    dry = not args.apply

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    antes = cur.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0]

    print(f"{'(DRY-RUN) ' if dry else ''}Saneamento da taxonomia\n" + "=" * 64)

    print("\n[1] RENAME AREA (grafia canônica)")
    for de, para in RENAME_AREA:
        n = cur.execute("SELECT COUNT(*) FROM taxonomia_cronograma WHERE area=?", (de,)).fetchone()[0]
        print(f"    {de!r} -> {para!r}  ({n} temas)")
    print("\n[2] MOVE TEMA -> área canônica")
    for tid, area in MOVE_TEMA:
        print(f"    {name(cur, tid)} -> [{area}]  (filhos={nchild(cur, tid)})")
    print("\n[3] RENAME TEMA")
    for tid, nome in RENAME_TEMA:
        print(f"    {name(cur, tid)} -> {nome!r}")
    print("\n[4] MERGE (fusão conceitual; re-aponta FKs)")
    for surv, losers, nome, area in MERGE:
        print(f"    surv {surv} {name(cur, surv)} (filhos={nchild(cur, surv)})  =>  [{area}] {nome!r}")
        for L in losers:
            print(f"         <= loser {L} {name(cur, L)} (filhos={nchild(cur, L)})")
    print("\n[5] DELETE vazios (0 cards E 0 questões)")
    for tid in DELETE_TEMA:
        print(f"    {tid} {name(cur, tid)} (filhos={nchild(cur, tid)})")

    # Guard 1: deletes precisam ter 0 filhos
    bad = [tid for tid in DELETE_TEMA if nchild(cur, tid) > 0]
    if bad:
        print(f"\n[ABORT] temas em DELETE_TEMA têm filhos: {bad}")
        con.close()
        sys.exit(1)

    # Guard 2: simular colisões no estado final
    final, colis = simulate(cur)
    print(f"\n[SIMULAÇÃO] temas {antes} -> {len(final)} | colisões (area,tema) = {colis if colis else 'nenhuma'}")
    if colis:
        print("[ABORT] a migração geraria duplicatas — ajuste as operações.")
        con.close()
        sys.exit(1)

    if dry:
        print("\n(dry-run) nada gravado. O --apply fixa o backup do proprio inicio (F137).")
        con.close()
        return

    try:
        rec = _fixar_antes("normalize_taxonomia --apply", DB_PATH)
    except Exception as e:  # noqa: BLE001 -- sem ponto de retorno = recusa (F137 parte 2)
        print(f"\n[ERRO] sem ponto de retorno FIXADO (F137): {e}. Nada gravado.")
        con.close()
        sys.exit(1)
    print(f"FIXADO {rec['arquivo']} sha256 {rec['sha256']} (vai para o ledger no item do ato)")
    try:
        with con:
            con.execute("DROP INDEX IF EXISTS ux_taxonomia_area_tema")
            for de, para in RENAME_AREA:
                con.execute("UPDATE taxonomia_cronograma SET area=? WHERE area=?", (para, de))
            for tid, area in MOVE_TEMA:
                con.execute("UPDATE taxonomia_cronograma SET area=? WHERE id=?", (area, tid))
            for tid, nome in RENAME_TEMA:
                con.execute("UPDATE taxonomia_cronograma SET tema=? WHERE id=?", (nome, tid))
            for surv, losers, nome, area in MERGE:
                ph = ",".join("?" * len(losers))
                for L in losers:
                    # s207: TODA tabela com FK para o tema -- review_log e questao_habilidades
                    # ficavam orfas (medido: 9 e 151 linhas nos perdedores da RODADA 3).
                    for tabela in TABELAS_COM_TEMA:
                        con.execute(f"UPDATE {tabela} SET tema_id=? WHERE tema_id=?", (surv, L))
                ids = [surv] + losers
                qr, qa, ult = con.execute(
                    f"SELECT MAX(questoes_realizadas), MAX(questoes_acertadas), MAX(ultima_revisao) "
                    f"FROM taxonomia_cronograma WHERE id IN ({','.join('?' * len(ids))})", ids).fetchone()
                pct = round((qa or 0) / qr * 100, 2) if qr else 0.0
                con.execute("UPDATE taxonomia_cronograma SET tema=?, area=?, questoes_realizadas=?, "
                            "questoes_acertadas=?, percentual_acertos=?, ultima_revisao=? WHERE id=?",
                            (nome, area, qr, qa, pct, ult, surv))
                con.execute(f"DELETE FROM taxonomia_cronograma WHERE id IN ({ph})", losers)
            for tid in DELETE_TEMA:
                con.execute("DELETE FROM taxonomia_cronograma WHERE id=?", (tid,))
            con.execute("CREATE UNIQUE INDEX ux_taxonomia_area_tema "
                        "ON taxonomia_cronograma(area, tema)")
        print("\nAPLICADO com sucesso.")
    except sqlite3.Error as e:
        print(f"\n[ERRO] transação revertida: {e}")
        con.close()
        sys.exit(1)

    dup = cur.execute("SELECT COUNT(*) FROM (SELECT 1 FROM taxonomia_cronograma "
                      "GROUP BY area, tema HAVING COUNT(*)>1)").fetchone()[0]
    orfaos = {t: cur.execute(f"SELECT COUNT(*) FROM {t} x LEFT JOIN taxonomia_cronograma t "
                             f"ON x.tema_id=t.id WHERE x.tema_id IS NOT NULL AND t.id IS NULL").fetchone()[0]
              for t in TABELAS_COM_TEMA}
    depois = cur.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0]
    print(f"VERIF -> linhas {antes} -> {depois} | dup={dup} | órfãos {orfaos}")
    con.close()


if __name__ == "__main__":
    main()
