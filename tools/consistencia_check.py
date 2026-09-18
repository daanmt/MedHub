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
def _registros_de_volume():
    """[(data_sessao, area, feitas)] de `sessoes_bulk`. None = nao deu para ler.

    Vai pelo leitor de `app/utils/db.py` (AGENTE 6: agente/CLI nao faz SQL direto).
    `get_trend_sessoes` ja filtra `questoes_feitas > 0`, que e exatamente o que uma
    pendencia do tipo "sem feitas/acertos" afirma NAO existir.
    """
    try:
        sys.path.insert(0, str(ROOT_DIR))
        from app.utils import db
        df = db.get_trend_sessoes()
        if df is None or getattr(df, "empty", True):
            return None
        return [(str(r.data_sessao)[:10], str(r.area), int(r.questoes_feitas))
                for r in df.itertuples()]
    except Exception:
        return None


#: a linha precisa COBRAR registro -- data solta nao e pendencia
_RX_COBRANCA = re.compile(
    r"registrar_sessao_bulk|sem\s+feitas|sem\s+volume|nunca\s+entrou|"
    r"n[ãa]o\s+(?:foi\s+)?registrad|falta\s+(?:registrar|lan[çc]ar)|"
    r"pendente\s+de\s+registro", re.IGNORECASE)
_RX_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_RX_BR = re.compile(r"\b(\d{2})/(\d{2})(?:/(\d{4}))?\b")


def _datas_da_linha(linha, anos_conhecidos):
    """Datas ISO extraidas da linha. `dd/mm` sem ano vira candidato em cada ano visto."""
    datas = {f"{a}-{m}-{d}" for a, m, d in _RX_ISO.findall(linha)}
    for d, m, a in _RX_BR.findall(linha):
        if a:
            datas.add(f"{a}-{m}-{d}")
        else:
            datas.update(f"{ano}-{m}-{d}" for ano in anos_conhecidos)
    return datas


def check_pendencia_fantasma(root=None, _registros=None):
    """F101: pendencia do HANDOFF que o proprio banco ja desmente.

    O HANDOFF da s179 e da s180 cobrou o registro da lista de Diarreia de 09/09
    "sem feitas/acertos"; o registro existia desde a s175 (`175 | Pediatria | 41 |
    34 | 2026-09-09`). Texto herdado do 1o ato, escrito ANTES do registro, copiado
    por duas sessoes sem ninguem re-medir. Custo evitado: +41 questoes duplicadas
    no SSOT volumetrico. Classe: claim que envelhece (AGENTE 10.9).

    ⚠️ LIMITE DECLARADO, e e grande: so alcanca pendencia com FORMA reconhecivel --
    palavra que cobra registro MAIS uma data. "Falta lancar o bloco de ontem" e
    invisivel para este check, e isso fica dito em vez de maquiado (10.8). WARN por
    nascimento (AGENTE 6: regra nova nasce warn-first).
    """
    base = Path(root).resolve() if root else ROOT_DIR
    handoff = base / "HANDOFF.md"
    if not handoff.is_file():
        return []
    registros = _registros if _registros is not None else _registros_de_volume()
    if not registros:
        return []          # nao da para checar -> silencio, nunca acusacao
    por_data = {}
    for data, area, feitas in registros:
        por_data.setdefault(data, []).append((area, feitas))
    anos = {d[:4] for d in por_data}
    achados = []
    for n, linha in enumerate(handoff.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not _RX_COBRANCA.search(linha):
            continue
        for data in sorted(_datas_da_linha(linha, anos)):
            if data in por_data:
                quem = "; ".join(f"{a} {f}q" for a, f in por_data[data])
                achados.append({
                    "alvo": f"HANDOFF.md:{n}",
                    "payload": {"data": data, "registrado": quem,
                                "linha": linha.strip()[:160]}})
                break
    return achados


def _cabecalhos_do_ledger(led):
    saida = {}
    for m in re.finditer(r"^###\s+(F\d+)\b(.*)$",
                         led.read_text(encoding="utf-8", errors="replace"), re.M):
        saida[m.group(1)] = m.group(2)
    return saida


def check_status_portador(root=None):
    """G14b (s187): cabecalho do achado x o PORTADOR real, nao o §11.

    🔴 **O buraco que isto fecha, medido em 18/09/2026.** O `check_status_ledger`
    so enxerga achado que alguem lembrou de por no `§11` do `MEMORIA-AUDITORIA`.
    **F109 e F110 nunca entraram la** -- e os dois tiveram os riders de doc
    pousados na s185 com o cabecalho do ledger dizendo `ABERTO` por um dia, ate
    a s187 ler os portadores. Gate-miss por **escopo de alvo**: o sensor existe,
    olha o registro vizinho, e o painel fica verde. Mesma forma do F115 e do
    proprio Invariante A (s187) -- a terceira ocorrencia da serie na mesma janela.

    O sinal usado e **derivado, nao digitado**: contrato e skill carimbam o F-id
    na propria linha de versao (`**Versao 1.4 | ... (s185, F109: ...)**`). Se um
    portador declara ter absorvido o achado, o cabecalho nao pode dizer ABERTO.

    ⚠️ **LIMITE DECLARADO:** so alcanca achado cujo remedio virou **versao de
    portador**. Remedio que e so codigo (sem bump de contrato) continua invisivel
    aqui -- fica com o `check_status_ledger` e com o §11. Nao maquiar: isto e
    uma segunda lente, nao a lente completa (10.8, verification-stack).
    """
    base = Path(root).resolve() if root else ROOT_DIR
    led = base / "AUDITORIA_MEDHUB.md"
    if not led.is_file():
        return []
    cabecalhos = _cabecalhos_do_ledger(led)
    fontes = sorted((base / "core" / "contracts").glob("*.md"))
    fontes += sorted((base / ".claude" / "commands").glob("*.md"))
    reivindicado = {}
    for f in fontes:
        for linha in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if not linha.startswith("**Vers"):
                continue
            for fid in re.findall(r"\bF\d{1,3}\b", linha):
                reivindicado.setdefault(fid, set()).add(f.name)
    achados = []
    for fid in sorted(reivindicado, key=lambda s: int(s[1:])):
        linha = cabecalhos.get(fid)
        if linha is None:
            continue
        if re.search(r"\*\*ABERTO", linha) and "⚰️" not in linha and "RESOLVIDO" not in linha:
            achados.append({"alvo": f"AUDITORIA_MEDHUB.md §{fid}",
                            "payload": {"cabecalho": "ABERTO",
                                        "portadores": sorted(reivindicado[fid])}})
    return achados


CHECKS = {
    "tabela": ("G5  tabela gerada (AGENTE §7.4) stale", check_tabela_gerada),
    "paths": ("G10 ponteiro morto em doc de raiz", check_paths_mortos),
    "status": ("G14 status do ledger x lapide do §11", check_status_ledger),
    "portador": ("G14b status do ledger x versao do portador", check_status_portador),
    "fantasma": ("F101 pendencia do HANDOFF que o banco desmente", check_pendencia_fantasma),
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
