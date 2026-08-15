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

Modo REFS (2026-08-14, consolidacao part-5 -- defeitos D1/D2/D3):
o modo de anotacao acima so ve o que alguem anotou a mao, em 4 docs. As normas
que mentem vivem em outro lugar (.claude/commands/, .claude/agents/,
.agents/workflows/, core/contracts/) e mentem sem anotacao nenhuma. O modo refs
varre esses diretorios e WARNa duas especies de referencia morta:
    (a) path de arquivo citado na norma que nao existe no repo;
    (b) nome de tool `mcp__<server>__<tool>` cujo <server> nao esta no .mcp.json.
Barato por construcao: so le texto, so olha crase e link markdown, e descarta
o que nao consegue julgar (URL, path absoluto, glob, placeholder).

Uso standalone: python tools/doc_drift.py [--json] [--mode all|annot|refs]
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

# --- Modo REFS -------------------------------------------------------------

# Onde as normas VIVAS moram. A ALLOWLIST acima (modo anotacao) fica intacta:
# sao escopos distintos, com especies de achado distintas.
REFS_DIRS = (".claude/commands", ".claude/agents", ".agents/workflows",
             "core/contracts")

# Extensoes que caracterizam "ref a arquivo do repo". Sem extensao conhecida o
# token nao vira path -- evita falso-positivo em prosa ("two-tier gold/pdf_raw").
REFS_EXTS = (".py", ".md", ".json", ".txt", ".db", ".ini", ".cfg", ".toml",
             ".yml", ".yaml", ".sql", ".sh", ".ps1", ".csv", ".xlsx")

# Servers MCP que legitimamente NAO estao no .mcp.json: os connectors da
# claude.ai sao configurados no harness (OAuth), fora do repo. Prefixo.
MCP_EXTERNOS = ("claude_ai_",)

RE_BACKTICK = re.compile(r"`([^`\n]+)`")
RE_MDLINK = re.compile(r"\]\(([^)\s]+)\)")
# Crase que carrega um COMANDO vira lista de tokens; crase que carrega um path
# fica inteira (paths de resumo tem espaco: "resumos/Clinica Medica/...").
RE_COMANDO = re.compile(
    r"^\s*(?:python|py|pwsh|powershell|bash|sh|git|uvx|pip|pytest|node|npm)\b"
    r"|\s--\S")
# Linha que AFIRMA a ausencia nao esta mentindo ao citar o morto -- e lapide.
# Mesma semantica da especie `path <x> absent` do modo anotacao: drift e
# realidade != doc, e aqui doc e realidade concordam.
RE_LAPIDE = re.compile(
    r"removid|deletad|descontinuad|aposentad|descomissionad|expurgad"
    r"|c[oó]digo morto|n[ãa]o existe|deixou de existir", re.I)
RE_MCP_TOOL = re.compile(r"mcp__([A-Za-z0-9_.-]+?)__[A-Za-z0-9]")
RE_LINHA_SUFIXO = re.compile(r":\d+(?:-\d+)?$")
RE_PLACEHOLDER = re.compile(r"NNN|XXX|nnn|\.\.\.")
RE_ABSOLUTO = re.compile(r"^[A-Za-z]:[\\/]")


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


def normalizar_ref(token, exigir_barra=True):
    """Token cru -> path relativo verificavel, ou None se o sensor nao pode julgar.

    Pura (nao toca filesystem). Descarta URL, path absoluto, glob, placeholder e
    qualquer token sem extensao conhecida. `exigir_barra` distingue as duas
    origens: em crase so aceitamos algo que PARECA path do repo (tem '/'); em
    link markdown o alvo pode ser irmao do proprio doc (sem '/').
    """
    if not token:
        return None
    t = token.strip().strip("*_`\"'")
    t = t.strip("(),;:")
    t = t.split("::", 1)[0]                  # app/utils/db.py::sync_git -> .py
    t = t.split("#", 1)[0]                   # doc.md#ancora -> doc.md
    t = RE_LINHA_SUFIXO.sub("", t)           # norma.md:64 / :14-15 -> norma.md
    t = t.strip().rstrip(".,;:")
    if not t:
        return None
    if t.startswith(("http://", "https://", "mailto:", "/", "\\", "~", "#")):
        return None
    if RE_ABSOLUTO.match(t) or RE_PLACEHOLDER.search(t):
        return None
    if any(c in t for c in '*?<>{}|"\''):
        return None
    if t.startswith((".venv/", "node_modules/", "__pycache__/")):
        return None
    if exigir_barra and "/" not in t:
        return None
    if not t.lower().endswith(REFS_EXTS):
        return None
    return t


def _refs_da_linha(linha):
    """[(token, exige_barra)] candidatos da linha: crases + alvos de link markdown."""
    cands = []
    for m in RE_BACKTICK.finditer(linha):
        conteudo = m.group(1)
        # So um COMANDO vira lista de palavras. Fatiar sempre quebraria path
        # com espaco no meio ("resumos/Clinica Medica/Neurologia/TCE.md").
        if RE_COMANDO.search(conteudo):
            cands.extend((tok, True) for tok in conteudo.split())
        else:
            cands.append((conteudo, True))
    for m in RE_MDLINK.finditer(linha):
        cands.append((m.group(1), False))
    return cands


def _mcp_servers(root):
    """Set de servers declarados no .mcp.json. Ausente/ilegivel -> set vazio."""
    alvo = root / ".mcp.json"
    try:
        dados = json.loads(alvo.read_text(encoding="utf-8"))
    except Exception:
        return set()
    servers = dados.get("mcpServers")
    return set(servers) if isinstance(servers, dict) else set()


def scan_refs(root=None):
    """Varre REFS_DIRS e devolve achados de referencia morta (path e mcp).

    Pura no sentido util ao teste: so LE (nunca escreve), toda a entrada vem do
    `root` recebido, e nunca lanca excecao. Achado: {doc, linha, regra,
    tipo ('ref'), msg}.
    """
    root = Path(root).resolve() if root else ROOT_DIR
    servers = _mcp_servers(root)
    # So julgamos ref cujo 1o segmento e uma entrada real da raiz. Ref a OUTRO
    # repo ("agente-daktus-content/...", "skills/...") o sensor nao pode julgar
    # -- e silencio honesto, nao cobertura fingida.
    try:
        raizes = {p.name for p in root.iterdir()}
    except Exception:
        raizes = set()
    achados = []
    for rel in REFS_DIRS:
        base = root / rel
        if not base.is_dir():
            continue
        for arq in sorted(base.rglob("*.md")):
            try:
                linhas = arq.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            doc = arq.relative_to(root).as_posix()
            for i, linha in enumerate(linhas, 1):
                if RE_LAPIDE.search(linha):
                    continue
                vistos = set()
                for token, exige_barra in _refs_da_linha(linha):
                    ref = normalizar_ref(token, exigir_barra=exige_barra)
                    if not ref or ref in vistos:
                        continue
                    vistos.add(ref)
                    if (root / ref).exists():
                        continue
                    # Link irmao: tambem vale relativo ao diretorio do doc.
                    if not exige_barra and (arq.parent / ref).exists():
                        continue
                    # Guarda so vale para path repo-relativo; link irmao (sem
                    # barra) ja foi resolvido contra o dir do proprio doc.
                    if "/" in ref and ref.split("/", 1)[0] not in raizes:
                        continue
                    achados.append(_achado(
                        doc, i, ref, "ref",
                        f"path citado nao existe no repo: {ref}"))
                for m in RE_MCP_TOOL.finditer(linha):
                    server = m.group(1)
                    if server in vistos or server in servers:
                        continue
                    vistos.add(server)
                    if server.startswith(MCP_EXTERNOS):
                        continue
                    achados.append(_achado(
                        doc, i, f"mcp__{server}__*", "ref",
                        f"server MCP '{server}' nao esta em .mcp.json "
                        f"(declarados: {', '.join(sorted(servers)) or 'nenhum'})"))
    return achados


def run_checks(root=None, db_path=None, modo="all"):
    """Varre a ALLOWLIST, verifica cada anotacao, devolve lista de achados.

    `modo`: 'annot' (so anotacoes drift-check), 'refs' (so referencias mortas)
    ou 'all' (ambos, default -- e o que o auto_check consome).
    Achado: {doc, linha, regra, tipo ('drift'|'sintaxe'|'ref'), msg}.
    Lista vazia = docs e realidade coerentes. Nunca lanca excecao.
    """
    root = Path(root).resolve() if root else ROOT_DIR
    db = Path(db_path) if db_path else root / "ipub.db"
    achados = []
    if modo in ("all", "annot"):
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
    if modo in ("all", "refs"):
        achados.extend(scan_refs(root))
    return achados


def main():
    parser = argparse.ArgumentParser(
        description="Sensor de drift doc-vs-codigo (WARN-first; exit 0 sempre).")
    parser.add_argument("--json", action="store_true",
                        help="saida machine-readable (lista JSON de achados)")
    parser.add_argument("--mode", choices=("all", "annot", "refs"), default="all",
                        help="all (default) | annot (so drift-check) | refs (so refs mortas)")
    args = parser.parse_args()
    achados = run_checks(modo=args.mode)
    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
        return 0
    if not achados:
        print("doc_drift: 0 achados -- docs e realidade coerentes.")
        return 0
    TAGS = {"drift": "DOC_DRIFT", "sintaxe": "DOC_DRIFT_SYNTAX", "ref": "DOC_REF"}
    for a in achados:
        tag = TAGS.get(a["tipo"], "DOC_DRIFT")
        print(f"[WARN] {tag}: {a['doc']}:{a['linha']} -- {a['msg']}")
        print(f"       regra: {a['regra']}")
    print(f"doc_drift: {len(achados)} achado(s) -- WARN nao bloqueia; reconciliar doc ou corrigir anotacao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
