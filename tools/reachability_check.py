"""reachability_check.py — check de ALCANCABILIDADE v0 (consolidacao part-6).

A pergunta que nenhum outro check do harness faz: **alguem chega aqui?**

Nasceu do achado D4 do ciclo de consolidacao ("construido-e-nunca-conectado"):
`check_fk_orphans.py` existia, funcionava e passava nos testes -- e nao era
chamado por harness nenhum. `test_variancia.py` idem, fora de todo `pytest.ini`.
Codigo assim nao da erro: ele so nao acontece. Nenhum linter, nenhum teste e
nenhuma suite verde detecta a ausencia de um chamador.

O check varre os ALVOS (`tools/*.py`, `app/**/*.py`) e pergunta, para cada um,
se existe ao menos UM referenciador vivo: `pytest.ini`, `.claude/`, `.agents/`,
hooks declarados em `.claude/settings.json`, outro `.py`, ou um contrato em
`core/contracts/`. Sem referenciador -> ORFAO -> WARN.

Warn-first, exit 0 SEMPRE: orfao pode ser legitimo (utilitario one-shot que
ainda vai ser usado). Promover a BLOCK e decisao do operador, nao deste script,
que nao escreve nada no repo.

v0 e deliberadamente RASO (anti-scope da spec): casamento por NOME, nao analise
estatica de imports. Um arquivo citado num `.md` conta como alcancavel -- porque
no MedHub o agente le o `.md` e roda o CLI: a mencao E a chamada.

PORTABILIDADE: toda a configuracao vive no bloco CONFIG abaixo. Plugar noutro
repo = trocar esse bloco. Nada mais no arquivo assume MedHub.

Uso:
    python tools/reachability_check.py            # relatorio humano
    python tools/reachability_check.py --json     # achados em JSON
    python tools/reachability_check.py --tabela   # tabela markdown dos CLIs vivos
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ===========================================================================
# CONFIG — a unica parte acoplada ao repo. Trocar este bloco = portar o check.
# ===========================================================================

ROOT_DIR = Path(__file__).parent.parent.resolve()

# Alvos: o que precisa ser alcancado. (glob relativo a raiz)
ALVOS = ["tools/*.py", "app/**/*.py"]

# Referenciadores: onde um alvo pode ser mencionado para contar como vivo.
REFERENCIADORES = [
    "pytest.ini",
    ".claude/**/*.md", ".claude/**/*.json",
    ".agents/**/*.md",
    "core/contracts/*.md",
    "tools/**/*.py", "app/**/*.py",
]

# Nao sao alvos (nem referenciadores): arquivo morto/arquivado nao ressuscita
# nada, e cache nao e codigo.
EXCLUSOES = ["**/__pycache__/**", "tools/_archive/**", "**/.git/**"]

# Alvos vivos POR CONSTRUCAO, com o motivo. Sao os casos em que "ninguem cita o
# nome" nao significa "ninguem chega": o mecanismo de alcance nao passa por
# mencao textual do arquivo.
ISENTOS = {
    "__init__.py": "marcador de pacote — alcancado pelo import do pacote, nunca pelo nome",
    # Audit da consolidacao part-6 (ai-eng): sob demanda POR NORMA, nao orfaos.
    "calibrate_card_checks.py": "calibrador dos limiares de card_checks — norma: limiar "
                                "so muda re-rodando a calibracao (decisions.md 2026-08-14)",
    "audit_fsrs.py": "inspetor manual read-only do motor FSRS — ferramenta de mao "
                     "declarada na tabela do AGENTE.md §7.4",
}

# Diretorio cujos .py sao alcancados por declaracao em settings.json (hooks) --
# o hook cita o caminho, entao o casamento normal ja pega; fica aqui so para
# documentar a intencao de varrer settings.json como referenciador.
ARQUIVOS_DE_HOOK = [".claude/settings.json"]

# Titulo do ledger. None desliga o registro.
LEDGER_TAG = "reachability"

# ===========================================================================
# Fim da CONFIG.
# ===========================================================================


def _casa_glob(rel, pattern):
    """Glob -> regex. Feito a mao porque `Path.match` nao resolve `**` no MEIO
    do padrao (`**/__pycache__/**`), que e exatamente a forma das exclusoes."""
    rx = re.escape(pattern.replace("\\", "/"))
    rx = rx.replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(rx, rel) is not None


def _excluido(rel):
    return any(_casa_glob(rel, pat) for pat in EXCLUSOES)


def _globs(padroes):
    """Paths relativos (posix) que casam com os padroes, sem exclusoes."""
    achados = set()
    for pat in padroes:
        for p in ROOT_DIR.glob(pat):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT_DIR).as_posix()
            if _excluido(rel):
                continue
            achados.add(rel)
    return sorted(achados)


def _padroes_de_alvo(rel):
    """Formas pelas quais um alvo pode ser citado.

    Devolve (padroes_fortes, padrao_modulo):
      - fortes: caminho do arquivo ou nome-com-extensao. Valem em QUALQUER
        referenciador, inclusive .md/.json (o doc tem de nomear o arquivo).
      - modulo: o stem cru (`card_checks`, `store`). So vale dentro de .py --
        `import card_checks`. Em prosa, um stem solto e ruido: `performance`
        aparece em dezenas de .md sem se referir a `tools/performance.py`.
    """
    stem = Path(rel).stem
    fortes = {rel, rel.replace("/", "\\"), Path(rel).name}
    if rel.startswith("app/"):
        fortes.add(rel[:-3].replace("/", "."))          # app.utils.db
    return fortes, stem


def _referenciadores_de(rel, corpus):
    """Lista de referenciadores vivos do alvo `rel`. Nunca conta o proprio
    arquivo (auto-referencia em docstring nao e alcance)."""
    fortes, stem = _padroes_de_alvo(rel)
    rx_stem = re.compile(rf"(?<![\w.]){re.escape(stem)}(?![\w])")
    quem = []
    for ref_rel, texto in corpus.items():
        if ref_rel == rel:
            continue
        if any(f in texto for f in fortes):
            quem.append(ref_rel)
        elif ref_rel.endswith(".py") and rx_stem.search(texto):
            quem.append(ref_rel)
    return quem


def _carregar_corpus():
    """{caminho_relativo: texto} de todos os referenciadores legiveis."""
    corpus = {}
    for rel in _globs(REFERENCIADORES + ARQUIVOS_DE_HOOK):
        try:
            corpus[rel] = (ROOT_DIR / rel).read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
    return corpus


def run_checks(root=None):
    """Retorna lista de achados [{'alvo', 'payload'}] — vazia = tudo alcancavel.
    Assinatura igual aos demais sensores do harness (doc_drift, check_fk_orphans).
    """
    global ROOT_DIR
    orig = ROOT_DIR
    if root:
        ROOT_DIR = Path(root).resolve()
    try:
        corpus = _carregar_corpus()
        achados = []
        for rel in _globs(ALVOS):
            nome = Path(rel).name
            if nome in ISENTOS:
                continue
            quem = _referenciadores_de(rel, corpus)
            if not quem:
                achados.append({"alvo": rel, "payload": {"referenciadores": 0}})
        return achados
    finally:
        ROOT_DIR = orig


def inventario(root=None):
    """[(alvo, [referenciadores])] de TODOS os alvos — insumo da tabela de CLIs."""
    global ROOT_DIR
    orig = ROOT_DIR
    if root:
        ROOT_DIR = Path(root).resolve()
    try:
        corpus = _carregar_corpus()
        return [(rel, _referenciadores_de(rel, corpus)) for rel in _globs(ALVOS)]
    finally:
        ROOT_DIR = orig


def _resumo_docstring(rel):
    """1a linha util da docstring do modulo, para a coluna de descricao."""
    try:
        txt = (ROOT_DIR / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    m = re.search(r'^\s*(?:"""|\'\'\')(.*?)(?:\n|"""|\'\'\')', txt, re.S)
    if not m:
        return ""
    linha = m.group(1).strip()
    linha = re.sub(r"^[\w./]+\.py\s*[-—:]\s*", "", linha)   # tira o "nome.py — "
    linha = re.sub(r"^MedHub\s*[-—:]\s*", "", linha)
    return linha.split(". ")[0].strip().rstrip(".")[:88]


def tabela_markdown(root=None):
    """Tabela markdown dos CLIs vivos de tools/ (exclui testes e nao-CLIs).

    Gerada do inventario para que AGENTE.md §7 nao seja digitado a mao — uma
    tabela mantida a mao envelhece em silencio, que e o defeito que este
    proprio check existe para pegar.
    """
    global ROOT_DIR
    orig = ROOT_DIR
    if root:
        ROOT_DIR = Path(root).resolve()
    try:
        linhas = ["| CLI | O que faz | Alcancado por |",
                  "|---|---|---|"]
        # inventario() sem `root`: ROOT_DIR ja esta apontado aqui — e
        # _resumo_docstring le arquivo, entao precisa da MESMA raiz (o bug que
        # o teste da tabela pegou: descricao vinha vazia do repo errado).
        for rel, quem in inventario():
            nome = Path(rel).name
            if not rel.startswith("tools/") or nome.startswith("test_") or nome in ISENTOS:
                continue
            if not quem:
                continue
            docs = [q for q in quem if not q.endswith(".py")]
            cod = [q for q in quem if q.endswith(".py")]
            mostrados = docs[:2] or cod[:2]
            origem = ", ".join(f"`{q}`" for q in mostrados)
            extra = len(quem) - len(mostrados)
            if extra > 0:
                origem += f" (+{extra})"
            # descricao vazia = modulo sem docstring. Fica visivel de proposito:
            # a lacuna na tabela e o proprio pedido de docstring.
            linhas.append(f"| `{rel}` | {_resumo_docstring(rel) or '—'} | {origem} |")
        return "\n".join(linhas)
    finally:
        ROOT_DIR = orig


def main():
    ap = argparse.ArgumentParser(description="Check de alcancabilidade (warn-first).")
    ap.add_argument("--json", action="store_true", help="achados em JSON")
    ap.add_argument("--tabela", action="store_true",
                    help="tabela markdown dos CLIs vivos (para AGENTE.md §7)")
    args = ap.parse_args()

    if args.tabela:
        print(tabela_markdown())
        return 0

    achados = run_checks()
    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
        return 0

    total = len(_globs(ALVOS))
    if not achados:
        print(f"[OK] REACHABILITY: {total} alvo(s) varrido(s), 0 orfaos "
              f"(todos com >=1 referenciador vivo).")
    else:
        for a in achados:
            print(f"[WARN] REACHABILITY: {a['alvo']} -- nenhum referenciador vivo "
                  f"(pytest.ini / .claude / .agents / hooks / .py / contrato). "
                  f"Conectar ou aposentar.")
        print(f"\n[WARN] REACHABILITY: {len(achados)}/{total} alvo(s) orfao(s). "
              f"Warn-first: nao bloqueia.")
    if LEDGER_TAG:
        try:
            import ledger_self
            ledger_self.record(LEDGER_TAG, achados)
        except Exception as e:
            print(f"[WARN] REACHABILITY: ledger indisponivel ({e}); achados so no stdout.")
    return 0  # warn-first: nunca bloqueia


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    sys.exit(main())
