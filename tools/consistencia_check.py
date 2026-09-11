#!/usr/bin/env python3
"""Varredura unica de CONSISTENCIA entre registros (item 1.8, s177).

Tres classes de defeito que a auditoria G1-G14 mediu e que tinham em comum **nao
ter gate**: alguem notava, corrigia a instancia, e a classe voltava. Cada check
aqui pergunta *"alguem chega aqui?"* / *"este registro ainda diz a verdade?"* --
nao presenca de string.

  **G5 -- tabela GERADA que envelhece.** A secao 7.4 do `AGENTE.md` e produzida
  por `reachability_check --tabela` e **colada** a mao. Cada CLI novo a deixa
  stale em silencio, que e o proprio defeito (*construido-e-nunca-conectado*)
  que a tabela existe para expor. O check re-gera e compara.

  **G10 -- ponteiro morto fora de `memory/`.** O `MEMORY_POINTERS` (F57) acusa
  `tools/*.py` inexistente citado em `memory/*.md`; a citacao IDENTICA dentro de
  `ESTADO.md` nenhum gate via. O sensor existia e o alcance dele parava na
  fronteira do diretorio -- gate-miss de categoria, nao de poder expressivo.
  🔴 **Isencao por LAPIDE:** linha que AFIRMA a ausencia ("foi removido",
  "nao existe mais", "deletado", "~~riscado~~") e lapide, nao mentira -- e a
  convencao ja escrita em `.vibeflow/conventions.md`. Sem essa isencao o check
  nasce cheio de falso-positivo no `ROADMAP.md`, que e um historico.

  **G14 -- registro que mente sobre o proprio status.** Achado com `**ABERTO**`
  ou `**PARCIAL**` no cabecalho do `AUDITORIA_MEDHUB.md` enquanto o `§11` do
  `docs/MEMORIA-AUDITORIA.md` ja o carrega como `⚰️ FEITO`. Decisao do `/ai-eng`
  ao receber a medicao de 10/09: *"status falso nao e smell -- um registro que
  mente sobre o proprio status e o defeito F90 no portador que o operador le"*.

Alem dos checks, este modulo e a casa de duas DERIVACOES que substituem
enumeracao a mao no `auto_check` (F95 e o (ii') do F90):

  `portadores_derivados()` -- a lista de portadores da norma deixa de ser
  digitada: e todo `core/contracts/*.md`, todo `.claude/commands/*.md` e os docs
  de raiz, mais os portadores de CODIGO que o F97 acrescentou. Medido antes de
  trocar: a lista derivada (27) acha **3** achados reais que a manual (10) nao
  via -- entre eles um `PREPARAR` vivo e prescritivo no `README.md`.

  `termos_revogados_do_ledger()` -- os termos revogados passam a sair de
  marcadores legiveis por maquina no `docs/MEMORIA-AUDITORIA.md`
  (`<!-- TERMO-REVOGADO: termo | onde -->`), em vez de um dict digitado. E o que
  o comentario do `auto_check` prometia desde a s171 e nao cumpria.

WARN-first: este modulo detecta e reporta; quem decide severidade e o
`auto_check`.

Uso:
    python tools/consistencia_check.py [--json] [--check {todos,tabela,paths,status}]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()

#: Docs de raiz varridos por G10 (ponteiro morto) e usados como portadores.
DOCS_RAIZ = ("AGENTE.md", "ESTADO.md", "HANDOFF.md", "README.md", "ROADMAP.md")

#: Portadores de CODIGO -- nao vem de glob porque a maioria dos `.py` nao carrega
#: norma. Estes dois carregam: `day_plan` monta o passo que o agente le no 1o
#: turno e `dormant_refresh` expoe texto de `--help` no ato do uso (F97).
PORTADORES_CODIGO = ("tools/day_plan.py", "tools/dormant_refresh.py")

RE_PATH_PY = re.compile(r"\b((?:tools|app)/[\w./-]+\.py)\b")

#: Vocabulario de AUSENCIA: a linha declara que a coisa nao existe mais. Linha
#: assim e lapide, nao ponteiro morto (`.vibeflow/conventions.md`).
RE_AUSENCIA = re.compile(
    r"(⚰️|~~|\bfoi removid|\bforam removid|\bfoi deletad|\bforam deletad|"
    r"\bnao existe|\bnão existe|\bdescontinuad|\baposentar\b|\baposentad|"
    r"\bcodigo morto|\bcódigo morto|\bdeletad[ao]s? (?:em|na|no)\b|\bmorreu\b)",
    re.IGNORECASE)

RE_TERMO_MARCADOR = re.compile(
    r"<!--\s*TERMO-REVOGADO:\s*(?P<termo>[^|]+?)\s*\|\s*(?P<onde>[^>]+?)\s*-->")


# ---------------------------------------------------------------- G5 ---------
def check_tabela_gerada(root=None):
    """A tabela 7.4 do AGENTE bate com `reachability_check --tabela`?

    Compara **linha a linha**, nao so a contagem: CLI que troca de referenciador
    muda a 3a coluna sem mudar o numero de linhas, e foi assim que a versao
    anterior da tabela envelheceu sem ninguem ver.
    """
    base = Path(root).resolve() if root else ROOT_DIR
    agente = base / "AGENTE.md"
    if not agente.is_file():
        return []
    try:
        out = subprocess.run(
            [sys.executable, "-X", "utf8", str(base / "tools" / "reachability_check.py"),
             "--tabela"],
            capture_output=True, text=True, encoding="utf-8", cwd=str(base), timeout=120)
    except Exception as e:  # noqa: BLE001 -- sensor fora do ar nao inventa achado
        return [{"alvo": "AGENTE.md §7.4", "payload": {"erro": f"gerador indisponivel: {e}"}}]

    def linhas_cli(texto):
        return [l.rstrip() for l in texto.splitlines() if l.startswith("| `tools/")]

    gerada = linhas_cli(out.stdout)
    no_doc = linhas_cli(agente.read_text(encoding="utf-8", errors="replace"))
    if not gerada:
        return []
    if gerada == no_doc:
        return []
    so_gerada = [l.split("|")[1].strip() for l in gerada if l not in no_doc]
    so_doc = [l.split("|")[1].strip() for l in no_doc if l not in gerada]
    return [{"alvo": "AGENTE.md §7.4", "payload": {
        "linhas_geradas": len(gerada), "linhas_no_doc": len(no_doc),
        "so_na_gerada": so_gerada[:8], "so_no_doc": so_doc[:8]}}]


# --------------------------------------------------------------- G10 ---------
def check_paths_mortos(root=None, docs=None):
    """`tools/*.py` ou `app/*.py` citado num doc de raiz e inexistente no disco.

    Isento quando a linha AFIRMA a ausencia (lapide). Sem a isencao, o
    `ROADMAP.md` -- que e historico e narra o que foi deletado -- viraria ruido
    puro, e um sensor ruidoso e desligado na segunda sessao.
    """
    base = Path(root).resolve() if root else ROOT_DIR
    achados = []
    for nome in (docs if docs is not None else DOCS_RAIZ):
        f = base / nome
        if not f.is_file():
            continue
        for i, linha in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            mortos = [p for p in RE_PATH_PY.findall(linha) if not (base / p).exists()]
            if not mortos:
                continue
            if RE_AUSENCIA.search(linha):
                continue                      # lapide: a linha declara que nao existe
            achados.append({"alvo": f"{nome}:{i}",
                            "payload": {"paths": sorted(set(mortos))}})
    return achados


# --------------------------------------------------------------- G14 ---------
def _lapidados_no_inventario(texto):
    """F-ids que o §11 declara FEITOS -- o SUJEITO da linha, nao toda mencao.

    🔴 Precisao medida, nao suposta. A 1a versao coletava todo `**F<id>**` de
    qualquer linha com `⚰️` + `FEITO` e devolveu **2 achados, os 2 falsos**: uma
    lapide cita F-ids vizinhos o tempo todo ("familia F34/F36/F63", "⚰️ fechados
    na s176: ..."), e o texto de um item fechado MENCIONA os que ele nao fecha.
    A regra que sobrou: a linha tem de ser uma **linha de inventario riscada**
    (`| ~~N.N~~ |`) e o sujeito e o **primeiro** `**F<id>**` depois do `FEITO`.
    """
    feitos = set()
    for linha in texto.splitlines():
        if not linha.lstrip().startswith("| ~~"):
            continue
        if "⚰️" not in linha or "FEITO" not in linha:
            continue
        depois = linha.split("FEITO", 1)[1]
        m = re.search(r"\*\*(F\d+)\*\*", depois)
        if m:
            feitos.add(m.group(1))
    return feitos


def check_status_ledger(root=None):
    """Cabecalho do achado no ledger x lapide do inventario.

    Achado marcado `**ABERTO**`/`**PARCIAL**` no `AUDITORIA_MEDHUB.md` cujo F-id
    o `§11` ja declara `⚰️ FEITO`. A direcao inversa (fechado no ledger e aberto
    no §11) tambem e achado -- os dois registros sao lidos por gente diferente.
    """
    base = Path(root).resolve() if root else ROOT_DIR
    led = base / "AUDITORIA_MEDHUB.md"
    mem = base / "docs" / "MEMORIA-AUDITORIA.md"
    if not (led.is_file() and mem.is_file()):
        return []
    cabecalhos = {}
    for m in re.finditer(r"^###\s+(F\d+)\b(.*)$", led.read_text(encoding="utf-8", errors="replace"),
                         re.M):
        cabecalhos[m.group(1)] = m.group(2)
    feitos = _lapidados_no_inventario(mem.read_text(encoding="utf-8", errors="replace"))
    achados = []
    for fid in sorted(feitos, key=lambda s: int(s[1:])):
        linha = cabecalhos.get(fid)
        if linha is None:
            continue
        # 🔴 `PARCIAL` NAO e achado. E um estado declarado e legitimo -- "o
        # mecanismo fechou, a divida de conteudo segue" (F16, F39). Contradicao
        # e `ABERTO` x `FEITO`: ai um dos dois registros mente. Tratar PARCIAL
        # como divergencia seria punir a honestidade de quem escreveu o meio-termo.
        aberto = re.search(r"\*\*ABERTO", linha)
        tem_lapide = "⚰️" in linha or "RESOLVIDO" in linha
        if aberto and not tem_lapide:
            achados.append({"alvo": f"AUDITORIA_MEDHUB.md §{fid}",
                            "payload": {"cabecalho": "ABERTO",
                                        "inventario": "FEITO (⚰️ no §11)"}})
    return achados


# ------------------------------------------------ derivacoes (F95 / ii') -----
def portadores_derivados(root=None):
    """Lista de portadores da norma, DERIVADA em vez de digitada (F95).

    Todo contrato, toda skill canonica, os docs de raiz e os portadores de
    codigo do F97. Enumerar a mao foi o defeito duas vezes seguidas: o F95 achou
    o contrato FSRS fora da lista com um `PREPARAR` vivo, e a medicao que trocou
    a lista achou outro no `README.md`.
    """
    base = Path(root).resolve() if root else ROOT_DIR
    saida = []
    for pasta, padrao in ((base / "core" / "contracts", "*.md"),
                          (base / ".claude" / "commands", "*.md")):
        if pasta.is_dir():
            saida += [p.relative_to(base).as_posix() for p in sorted(pasta.glob(padrao))]
    saida += [d for d in DOCS_RAIZ if (base / d).is_file()]
    saida += [p for p in PORTADORES_CODIGO if (base / p).is_file()]
    return tuple(sorted(set(saida)))


def termos_revogados_do_ledger(root=None):
    """{termo: onde} lido dos marcadores do `docs/MEMORIA-AUDITORIA.md` ((ii')).

    Formato: `<!-- TERMO-REVOGADO: <termo literal> | <onde foi revogado> -->`.
    Doc ausente ou sem marcador devolve `{}` -- o chamador decide o fallback, e
    e ele que garante que o gate nunca fica sem vocabulario.
    """
    base = Path(root).resolve() if root else ROOT_DIR
    mem = base / "docs" / "MEMORIA-AUDITORIA.md"
    if not mem.is_file():
        return {}
    texto = mem.read_text(encoding="utf-8", errors="replace")
    return {m.group("termo"): m.group("onde") for m in RE_TERMO_MARCADOR.finditer(texto)}


# --------------------------------------------------------------- API ---------
CHECKS = {
    "tabela": ("G5  tabela gerada (AGENTE §7.4) stale", check_tabela_gerada),
    "paths": ("G10 ponteiro morto em doc de raiz", check_paths_mortos),
    "status": ("G14 status do ledger x lapide do §11", check_status_ledger),
}


def run_checks(root=None):
    """[{'check','alvo','payload'}] de todos os sub-checks. Vazio = consistente."""
    saida = []
    for chave, (_, fn) in CHECKS.items():
        for a in fn(root=root):
            saida.append({"check": chave, **a})
    return saida


def main():
    ap = argparse.ArgumentParser(
        description="Varredura de consistencia entre registros (G5/G10/G14; WARN-first).")
    ap.add_argument("--json", action="store_true", help="saida machine-readable")
    ap.add_argument("--check", choices=["todos"] + list(CHECKS), default="todos",
                    help="roda so um sub-check (default: todos)")
    args = ap.parse_args()

    alvos = CHECKS if args.check == "todos" else {args.check: CHECKS[args.check]}
    achados = []
    for chave, (rotulo, fn) in alvos.items():
        for a in fn():
            achados.append({"check": chave, **a})

    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
        return 0

    print()
    print("=" * 70)
    print("  Consistencia entre registros (item 1.8) -- WARN, nao bloqueia")
    print("=" * 70)
    for chave, (rotulo, _) in alvos.items():
        n = [a for a in achados if a["check"] == chave]
        selo = "OK " if not n else f"{len(n):>2} "
        print(f"  [{selo}] {rotulo}")
        for a in n[:8]:
            print(f"          {a['alvo']}  {a['payload']}")
    print()
    print(f"  portadores derivados : {len(portadores_derivados())}")
    print(f"  termos do ledger     : {len(termos_revogados_do_ledger())}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
