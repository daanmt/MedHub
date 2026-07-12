"""Sensor de drift doc-vs-codigo (check 7 do auto_check -- degrau 1 da auto-evolucao).

Verifica anotacoes machine-readable nos docs de estado/engenharia contra a
realidade do repo (codigo, filesystem, schema do ipub.db). WARN-first: o
sensor DETECTA e reporta; nunca corrige, nunca bloqueia, nunca escreve.

Fronteira clinica: a allowlist de docs e fixa (ROADMAP/HANDOFF/ESTADO/
AUDITORIA_MEDHUB) -- o sensor jamais abre resumos/** ou conteudo de cards.

Sintaxe da anotacao (comentario HTML, linha propria, acima do claim):
    <!-- drift-check: sqlite "SELECT ..." == 13 -->
    <!-- drift-check: symbol app/utils/db.py::nome_do_simbolo exists|absent -->
    <!-- drift-check: path tools/arquivo.py exists|absent -->
    <!-- drift-check: unique tabela (col_a, col_b) exists|absent -->

Semantica: a anotacao codifica o que o DOC afirma; drift = realidade != doc.
Anotacao malformada ou inverificavel gera achado de sintaxe (WARN), nunca crash.

Uso standalone: python tools/doc_drift.py [--json]
Uso pelo harness: from doc_drift import run_checks (check 7 do auto_check.py)
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()

# Allowlist FIXA (fronteira clinica): so docs de estado/engenharia da raiz.
ALLOWLIST = ("ROADMAP.md", "HANDOFF.md", "ESTADO.md", "AUDITORIA_MEDHUB.md")

RE_ANNOT = re.compile(r"<!--\s*drift-check:\s*(.+?)\s*-->")
RE_SQLITE = re.compile(r'^sqlite\s+"(?P<query>.+)"\s*==\s*(?P<valor>-?\d+)$')
RE_SYMBOL = re.compile(r'^symbol\s+(?P<path>\S+)::(?P<nome>\w+)\s+(?P<esperado>exists|absent)$')
RE_PATH = re.compile(r'^path\s+(?P<path>\S+)\s+(?P<esperado>exists|absent)$')
RE_UNIQUE = re.compile(r'^unique\s+(?P<tabela>\w+)\s*\((?P<cols>[^)]+)\)\s+(?P<esperado>exists|absent)$')


def _achado(doc, linha, regra, tipo, msg):
    return {"doc": doc, "linha": linha, "regra": regra, "tipo": tipo, "msg": msg}


def _check_sqlite(m, doc, linha, regra, db_path):
    query, esperado = m.group("query"), int(m.group("valor"))
    if not query.lstrip().lower().startswith("select"):
        return [_achado(doc, linha, regra, "sintaxe",
                        "so consultas SELECT sao permitidas na especie sqlite")]
    con = None
    try:
        # mode=ro: o sensor nao pode escrever no db nem por bug.
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        row = con.execute(query).fetchone()
        real = row[0] if row else None
    except Exception as e:
        return [_achado(doc, linha, regra, "sintaxe",
                        f"consulta inverificavel ({e})")]
    finally:
        if con is not None:
            con.close()
    if real != esperado:
        return [_achado(doc, linha, regra, "drift",
                        f"doc afirma {esperado}, db responde {real}")]
    return []


def _check_symbol(m, doc, linha, regra, root):
    alvo = root / m.group("path")
    if not alvo.is_file():
        return [_achado(doc, linha, regra, "sintaxe",
                        f"arquivo {m.group('path')} nao encontrado para inspecao")]
    try:
        texto = alvo.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [_achado(doc, linha, regra, "sintaxe", f"arquivo ilegivel ({e})")]
    existe = re.search(rf"\b{re.escape(m.group('nome'))}\b", texto) is not None
    esperado = m.group("esperado") == "exists"
    if existe != esperado:
        real = "presente" if existe else "ausente"
        return [_achado(doc, linha, regra, "drift",
                        f"doc afirma simbolo {m.group('esperado')}, mas esta {real} "
                        f"em {m.group('path')}")]
    return []


def _check_path(m, doc, linha, regra, root):
    existe = (root / m.group("path")).exists()
    esperado = m.group("esperado") == "exists"
    if existe != esperado:
        real = "existe" if existe else "nao existe"
        return [_achado(doc, linha, regra, "drift",
                        f"doc afirma path {m.group('esperado')}, mas {m.group('path')} {real}")]
    return []


def _check_unique(m, doc, linha, regra, db_path):
    tabela = m.group("tabela")
    cols_alvo = {c.strip().lower() for c in m.group("cols").split(",") if c.strip()}
    con = None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        # Cobre CREATE UNIQUE INDEX e constraint de tabela (sqlite_autoindex).
        indices = con.execute(f"PRAGMA index_list({tabela})").fetchall()
        existe = False
        for idx in indices:
            nome, unico = idx[1], idx[2]
            if not unico:
                continue
            cols_idx = {r[2].lower() for r in
                        con.execute(f"PRAGMA index_info({nome})").fetchall()}
            if cols_idx == cols_alvo:
                existe = True
                break
    except Exception as e:
        return [_achado(doc, linha, regra, "sintaxe",
                        f"schema inverificavel ({e})")]
    finally:
        if con is not None:
            con.close()
    esperado = m.group("esperado") == "exists"
    if existe != esperado:
        real = "existe" if existe else "nao existe"
        return [_achado(doc, linha, regra, "drift",
                        f"doc afirma unique {m.group('esperado')} em {tabela}"
                        f"({', '.join(sorted(cols_alvo))}), mas o indice {real}")]
    return []


def _verificar(regra, doc, linha, root, db_path):
    m = RE_SQLITE.match(regra)
    if m:
        return _check_sqlite(m, doc, linha, regra, db_path)
    m = RE_SYMBOL.match(regra)
    if m:
        return _check_symbol(m, doc, linha, regra, root)
    m = RE_PATH.match(regra)
    if m:
        return _check_path(m, doc, linha, regra, root)
    m = RE_UNIQUE.match(regra)
    if m:
        return _check_unique(m, doc, linha, regra, db_path)
    return [_achado(doc, linha, regra, "sintaxe",
                    "anotacao malformada -- especies validas: sqlite | symbol | path | unique")]


def run_checks(root=None, db_path=None):
    """Varre a ALLOWLIST, verifica cada anotacao, devolve lista de achados.

    Achado: {doc, linha, regra, tipo ('drift'|'sintaxe'), msg}.
    Lista vazia = docs e realidade coerentes. Nunca lanca excecao.
    """
    root = Path(root).resolve() if root else ROOT_DIR
    db = Path(db_path) if db_path else root / "ipub.db"
    achados = []
    for nome in ALLOWLIST:
        doc = root / nome
        if not doc.is_file():
            continue
        try:
            linhas = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for i, linha in enumerate(linhas, 1):
            for m in RE_ANNOT.finditer(linha):
                achados.extend(_verificar(m.group(1).strip(), nome, i, root, db))
    return achados


def main():
    parser = argparse.ArgumentParser(
        description="Sensor de drift doc-vs-codigo (WARN-first; exit 0 sempre).")
    parser.add_argument("--json", action="store_true",
                        help="saida machine-readable (lista JSON de achados)")
    args = parser.parse_args()
    achados = run_checks()
    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
        return 0
    if not achados:
        print("doc_drift: 0 achados -- docs e realidade coerentes.")
        return 0
    for a in achados:
        tag = "DOC_DRIFT" if a["tipo"] == "drift" else "DOC_DRIFT_SYNTAX"
        print(f"[WARN] {tag}: {a['doc']}:{a['linha']} -- {a['msg']}")
        print(f"       regra: {a['regra']}")
    print(f"doc_drift: {len(achados)} achado(s) -- WARN nao bloqueia; reconciliar doc ou corrigir anotacao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
