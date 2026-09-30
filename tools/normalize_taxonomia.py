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
#: RODADA 3 APLICADA em 29/09/2026 (s207, backup ipub_fixado_20260929_220057) -- fica como registro.
MERGE_RODADA3_APLICADA = [
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
MERGE = []

DELETE_TEMA = []

# F65 erros (s207; operador no chat: "reaponta os 201 erros do bulk pro tema real"):
# tema = o dos cards nascidos do erro (178); empate e sem card, pelo titulo/enunciado (23).
# (questao_id, tema_id destino). questao_habilidades acompanha.
MOVE_ERRO = [
    (1, 117),
    (2, 220),
    (3, 117),
    (4, 117),
    (5, 219),
    (6, 219),
    (7, 173),
    (8, 150),
    (9, 153),
    (10, 199),
    (11, 184),
    (12, 184),
    (13, 184),
    (14, 184),
    (15, 184),
    (16, 184),
    (17, 146),
    (18, 146),
    (19, 140),
    (20, 146),
    (21, 146),
    (22, 143),
    (23, 146),
    (24, 146),
    (25, 146),
    (26, 146),
    (27, 146),
    (28, 168),
    (29, 170),
    (30, 170),
    (31, 170),
    (32, 170),
    (33, 170),
    (34, 170),
    (35, 170),
    (36, 221),
    (37, 170),
    (38, 170),
    (39, 170),
    (40, 170),
    (41, 222),
    (42, 222),
    (43, 222),
    (44, 176),
    (45, 222),
    (46, 143),
    (47, 140),
    (48, 143),
    (49, 143),
    (50, 121),
    (51, 121),
    (52, 121),
    (53, 121),
    (54, 121),
    (55, 121),
    (56, 121),
    (57, 121),
    (58, 121),
    (59, 121),
    (60, 121),
    (61, 223),
    (62, 223),
    (63, 223),
    (64, 223),
    (65, 223),
    (66, 224),
    (67, 224),
    (68, 223),
    (69, 192),
    (70, 192),
    (71, 192),
    (72, 192),
    (73, 159),
    (74, 159),
    (75, 159),
    (76, 159),
    (77, 161),
    (78, 226),
    (79, 226),
    (80, 226),
    (81, 226),
    (82, 226),
    (83, 226),
    (84, 226),
    (85, 227),
    (86, 226),
    (87, 217),
    (88, 226),
    (89, 226),
    (90, 226),
    (91, 127),
    (92, 228),
    (93, 163),
    (94, 163),
    (95, 163),
    (96, 163),
    (97, 163),
    (98, 163),
    (99, 169),
    (100, 170),
    (101, 192),
    (102, 192),
    (103, 173),
    (104, 173),
    (105, 173),
    (106, 171),
    (107, 173),
    (108, 255),
    (109, 171),
    (110, 171),
    (111, 173),
    (112, 173),
    (113, 149),
    (114, 149),
    (115, 187),
    (116, 229),
    (117, 187),
    (118, 187),
    (119, 229),
    (120, 231),
    (121, 187),
    (122, 232),
    (123, 117),
    (124, 117),
    (125, 117),
    (126, 270),
    (127, 234),
    (128, 156),
    (129, 156),
    (130, 192),
    (131, 146),
    (132, 146),
    (133, 146),
    (134, 146),
    (135, 146),
    (136, 146),
    (137, 146),
    (138, 336),
    (139, 115),
    (140, 115),
    (141, 115),
    (142, 115),
    (143, 115),
    (144, 163),
    (145, 163),
    (146, 163),
    (147, 163),
    (148, 184),
    (149, 282),
    (150, 282),
    (151, 184),
    (152, 184),
    (153, 184),
    (154, 282),
    (155, 184),
    (156, 184),
    (157, 253),
    (158, 253),
    (159, 253),
    (160, 253),
    (161, 253),
    (162, 253),
    (163, 179),
    (164, 179),
    (165, 179),
    (166, 179),
    (167, 165),
    (168, 165),
    (169, 165),
    (170, 163),
    (171, 165),
    (172, 163),
    (173, 163),
    (174, 163),
    (175, 339),
    (176, 163),
    (177, 146),
    (178, 146),
    (179, 146),
    (180, 146),
    (181, 140),
    (182, 481),
    (183, 146),
    (184, 143),
    (185, 140),
    (186, 336),
    (187, 140),
    (188, 140),
    (189, 115),
    (190, 115),
    (191, 115),
    (192, 251),
    (193, 251),
    (194, 251),
    (195, 251),
    (196, 251),
    (197, 251),
    (198, 253),
    (199, 253),
    (200, 253),
    (201, 253)
]

# F65 (s207; M4 do operador: "agente propoe, eu aprovo" -> aprovou os 35 no chat da s207):
# card preso em balde `[bulk] <Area>` (balde de VOLUME, F37) vai para o tema real.
# (card_id, tema_id destino). So o tema muda: conteudo e FSRS intactos.
MOVE_CARD = [
    (279, 253),
    (281, 253),
    (283, 253),
    (285, 253),
    (287, 253),
    (291, 179),
    (293, 179),
    (295, 179),
    (297, 179),
    (299, 165),
    (301, 165),
    (303, 165),
    (305, 163),
    (307, 165),
    (309, 163),
    (311, 163),
    (313, 163),
    (315, 339),
    (317, 163),
    (321, 146),
    (325, 146),
    (327, 140),
    (329, 481),
    (333, 143),
    (335, 140),
    (337, 336),
    (339, 140),
    (341, 140),
    (343, 115),
    (345, 115),
    (347, 115),
    (349, 251),
    (351, 251),
    (357, 251),
    (359, 251)
]

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
    print("\n[6] MOVE CARD (F65: card preso em [bulk] -> tema real)")
    ruins = []
    for cid, tid in MOVE_CARD:
        r = cur.execute("SELECT t.tema FROM flashcards f JOIN taxonomia_cronograma t ON t.id = f.tema_id "
                        "WHERE f.id=?", (cid,)).fetchone()
        destino = cur.execute("SELECT tema FROM taxonomia_cronograma WHERE id=?", (tid,)).fetchone()
        ja = r is not None and destino is not None and r[0] == destino[0]
        if not ja and (r is None or not r[0].startswith("[bulk]") or destino is None
                       or destino[0].startswith("[bulk]")):
            ruins.append((cid, tid, r and r[0], destino and destino[0]))
        print(f"    card {cid}: {r[0] if r else '(INEXISTENTE)'} -> {name(cur, tid)}"
              + ("  (ja la)" if ja else ""))
    if ruins:
        print(f"\n[ABORT] MOVE_CARD fora da regra (origem tem de ser [bulk], destino real): {ruins}")
        con.close()
        sys.exit(1)
    print(f"\n[7] MOVE ERRO (F65: erro preso em [bulk] -> tema real): {len(MOVE_ERRO)} declarados")
    ruins_e = []
    for qid, tid in MOVE_ERRO:
        r = cur.execute("SELECT t.tema FROM questoes_erros q JOIN taxonomia_cronograma t ON t.id = q.tema_id "
                        "WHERE q.id=?", (qid,)).fetchone()
        destino = cur.execute("SELECT tema FROM taxonomia_cronograma WHERE id=?", (tid,)).fetchone()
        ja = r is not None and destino is not None and r[0] == destino[0]
        if not ja and (r is None or not r[0].startswith("[bulk]") or destino is None
                       or destino[0].startswith("[bulk]")):
            ruins_e.append((qid, tid))
    if ruins_e:
        print(f"[ABORT] MOVE_ERRO fora da regra: {ruins_e[:10]}")
        con.close()
        sys.exit(1)
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
            movidos = sum(con.execute("UPDATE flashcards SET tema_id=? WHERE id=? AND tema_id<>?",
                                      (tid, cid, tid)).rowcount for cid, tid in MOVE_CARD)
            print(f"    MOVE_CARD: {movidos} card(s) re-apontado(s) de {len(MOVE_CARD)} declarados")
            me = mh = 0
            for qid, tid in MOVE_ERRO:
                velho = con.execute("SELECT tema_id FROM questoes_erros WHERE id=?", (qid,)).fetchone()[0]
                me += con.execute("UPDATE questoes_erros SET tema_id=? WHERE id=? AND tema_id<>?",
                                  (tid, qid, tid)).rowcount
                mh += con.execute("UPDATE questao_habilidades SET tema_id=? WHERE questao_id=? AND tema_id=?",
                                  (tid, qid, velho)).rowcount
            print(f"    MOVE_ERRO: {me} erro(s) re-apontado(s) de {len(MOVE_ERRO)}; {mh} linha(s) de habilidade")
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
