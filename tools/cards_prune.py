"""cards_prune.py -- poda de flashcards APOSENTADOS do ipub.db [DESTRUTIVO], dry-run por default.

Spec: .vibeflow/specs/plano-ssot-e-cards-v2-part-5.md (PRD plano-ssot-e-cards-v2, P5).
Permit do usuario (16/09/2026, s183): lote 1 = aposentados (needs_qualitative=2) SEM revlog
e SEM marca de reforja. Os aposentados com historico ficam ate triagem individual.

Uso:
  python tools/cards_prune.py --criterio aposentados-sem-historico            # dry-run: N + ids
  python tools/cards_prune.py --criterio aposentados-sem-historico --apply --expect 125
  python tools/cards_prune.py --ids 12,34,56 --apply --expect 3

Rito (nunca pulado no --apply):
  1. mede N de novo e RECUSA (exit 2) se N != --expect  (COUNT-ASSERT pre)
  2. FIXA o backup do proprio inicio (backup_db.fixar_antes_do_ato, F137 parte 2: fora da rotacao, sha256)
  3. exporta as linhas dos 4 tabelas para artifacts/backups/pruned_<ts>.json
  4. apaga em UMA transacao: fsrs_revlog -> reforja_marks -> fsrs_cards -> flashcards
  5. COUNT-ASSERT pos: flashcards caiu exatamente N e nenhum id sobreviveu

Fronteira: nao toca questoes_erros, taxonomia_cronograma, review_log, sessoes_bulk;
nao altera stability/difficulty de card algum (so remove linhas inteiras).
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO_ROOT / "ipub.db"
EXPORT_DIR_DEFAULT = REPO_ROOT / "artifacts" / "backups"

CRITERIOS = {
    "aposentados-sem-historico": (
        "SELECT f.id FROM flashcards f "
        "WHERE f.needs_qualitative = 2 "
        "AND NOT EXISTS (SELECT 1 FROM fsrs_revlog r WHERE r.card_id = f.id) "
        "AND NOT EXISTS (SELECT 1 FROM reforja_marks m WHERE m.card_id = f.id) "
        "ORDER BY f.id"
    ),
}

# ordem de delecao: filhos antes do pai (PRAGMA foreign_keys e OFF no projeto; a ordem e
# o COUNT-ASSERT substituem a cascata)
TABELAS = (("fsrs_revlog", "card_id"), ("reforja_marks", "card_id"),
           ("fsrs_cards", "card_id"), ("flashcards", "id"))


def selecionar(conn, criterio=None, ids=None):
    """Ids-alvo, em ordem crescente. `ids` explicitos vencem o criterio; ids inexistentes
    sao ignorados (o COUNT-ASSERT do --expect denuncia a diferenca)."""
    if ids:
        marks = ",".join("?" * len(ids))
        rows = conn.execute(f"SELECT id FROM flashcards WHERE id IN ({marks}) ORDER BY id",
                            tuple(ids)).fetchall()
        return [r[0] for r in rows]
    if criterio not in CRITERIOS:
        raise ValueError(f"criterio desconhecido: {criterio!r} (validos: {sorted(CRITERIOS)})")
    return [r[0] for r in conn.execute(CRITERIOS[criterio]).fetchall()]


def exportar(conn, ids):
    """Snapshot das linhas que vao sumir (as 4 tabelas), serializavel em JSON."""
    conn.row_factory = sqlite3.Row
    out = {}
    marks = ",".join("?" * len(ids))
    for tabela, col in TABELAS:
        rows = conn.execute(f"SELECT * FROM {tabela} WHERE {col} IN ({marks})",
                            tuple(ids)).fetchall()
        out[tabela] = [dict(r) for r in rows]
    conn.row_factory = None
    return out


def apagar(conn, ids):
    """Apaga em UMA transacao. Retorna {tabela: linhas apagadas}. COUNT-ASSERT pos embutido."""
    antes = conn.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    n = len(ids)
    apagadas = {}
    params = [(i,) for i in ids]
    # SQL literal por tabela (nao f-string): o scanner de writers do harness
    # (tools/test_writer_allowlist.py) le o texto-fonte e precisa VER cada tabela-alvo.
    with conn:
        apagadas["fsrs_revlog"] = conn.executemany(
            "DELETE FROM fsrs_revlog WHERE card_id = ?", params).rowcount
        apagadas["reforja_marks"] = conn.executemany(
            "DELETE FROM reforja_marks WHERE card_id = ?", params).rowcount
        apagadas["fsrs_cards"] = conn.executemany(
            "DELETE FROM fsrs_cards WHERE card_id = ?", params).rowcount
        apagadas["flashcards"] = conn.executemany(
            "DELETE FROM flashcards WHERE id = ?", params).rowcount
    depois = conn.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    marks = ",".join("?" * n)
    sobreviventes = conn.execute(
        f"SELECT COUNT(*) FROM flashcards WHERE id IN ({marks})", tuple(ids)).fetchone()[0]
    assert antes - depois == n, (
        f"COUNT-ASSERT pos: flashcards caiu {antes - depois}, esperado {n}")
    assert sobreviventes == 0, f"COUNT-ASSERT pos: {sobreviventes} id(s) sobreviveram"
    return apagadas


def _backup_real(db_path=DB_DEFAULT, ato="cards_prune --apply"):
    """F137 parte 2: o backup FIXADO do proprio inicio da poda (fora da rotacao keep-5, sha256 no
    manifesto). Era o backup da rotacao -- que um dia de muitos backups expulsava. Falha levanta."""
    _tools = os.path.dirname(os.path.abspath(__file__))
    if _tools not in sys.path:
        sys.path.insert(0, _tools)
    import backup_db
    rec = backup_db.fixar_antes_do_ato(ato, db=db_path, out=lambda *_: None)
    return f"FIXADO {rec['arquivo']} sha256 {rec['sha256']}"


def executar(conn, criterio=None, ids=None, apply=False, expect=None,
             backup_fn=_backup_real, export_dir=EXPORT_DIR_DEFAULT, out=print):
    """Orquestra o rito. Retorna (exit_code, ids_alvo, caminho_export|None)."""
    alvo = selecionar(conn, criterio, ids)
    n = len(alvo)
    out(f"[cards_prune] criterio={criterio or 'ids'} alvo={n} card(s)")
    out("  ids: " + (", ".join(map(str, alvo)) if alvo else "(nenhum)"))
    if not apply:
        out("  DRY-RUN: nada gravado. Para aplicar: --apply --expect " + str(n))
        return 0, alvo, None
    if expect is None or expect != n:
        out(f"  RECUSADO: --expect {expect} != N medido {n}. Nada gravado.")
        return 2, alvo, None
    if n == 0:
        out("  nada a apagar.")
        return 0, alvo, None
    try:
        out("  backup: " + str(backup_fn()))
    except Exception as e:  # noqa: BLE001 -- sem ponto de retorno = recusa (F137 parte 2)
        out(f"  RECUSADO: sem ponto de retorno FIXADO ({e}). Nada gravado.")
        return 1, alvo, None
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    caminho = export_dir / f"pruned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    snapshot = {"gerado_em": datetime.now().isoformat(timespec="seconds"),
                "criterio": criterio or "ids", "n": n, "ids": alvo,
                "linhas": exportar(conn, alvo)}
    caminho.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    out(f"  export: {caminho} ({sum(len(v) for v in snapshot['linhas'].values())} linhas)")
    apagadas = apagar(conn, alvo)
    out("  apagadas: " + ", ".join(f"{t}={c}" for t, c in apagadas.items()))
    out(f"  OK: {n} flashcard(s) removido(s); COUNT-ASSERT pos batido.")
    return 0, alvo, caminho


def main(argv=None):
    ap = argparse.ArgumentParser(description="Poda de flashcards aposentados [DESTRUTIVO], dry-run por default.")
    ap.add_argument("--criterio", choices=sorted(CRITERIOS), help="criterio nomeado de selecao")
    ap.add_argument("--ids", help="ids explicitos separados por virgula (vence --criterio)")
    ap.add_argument("--apply", action="store_true", help="grava (default: dry-run)")
    ap.add_argument("--expect", type=int, help="COUNT-ASSERT: N esperado; obrigatorio com --apply")
    ap.add_argument("--db", default=str(DB_DEFAULT), help="caminho do banco (default: ipub.db da raiz)")
    args = ap.parse_args(argv)
    ids = [int(x) for x in args.ids.split(",") if x.strip()] if args.ids else None
    if not ids and not args.criterio:
        ap.error("informe --criterio ou --ids")
    if args.apply and args.expect is None:
        ap.error("--apply exige --expect N")
    conn = sqlite3.connect(args.db)
    try:
        code, _, _ = executar(conn, args.criterio, ids, args.apply, args.expect,
                              backup_fn=lambda: _backup_real(
                                  args.db, f"cards_prune --apply --expect {args.expect}"),
                              export_dir=EXPORT_DIR_DEFAULT)
    finally:
        conn.close()
    return code


if __name__ == "__main__":
    sys.exit(main())
