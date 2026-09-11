#!/usr/bin/env python3
"""Check de ASSINATURA CANONICA de CLI (D5, s177 -- AGENTE.md secao 7.2).

A regra que este sensor mede e a terceira do contrato Skills x Workflows x CLIs:

    "Cada CLI em `tools/` tem assinatura canonica em UMA skill. A assinatura
     COMPLETA (todos os flags, semantica de cada argumento) vive em exatamente
     um `.claude/commands/*.md`."

Ela nunca teve instrumento. O resultado, medido em 11/09/2026 antes deste
arquivo existir: **63 das 168 flags (37,5%) nao apareciam em skill nenhuma**, e
**16 CLIs nao eram citados por skill alguma**. Nao por desleixo -- por falta de
alcance: a regra existia em prosa, e prosa nao acusa. E a mesma forma do D4
(construido-e-nunca-conectado) e do G5 (tabela mantida a mao que envelhece).

O que o check mede, exatamente:

    flag `--x` de `tools/y.py` e ORFA quando NENHUMA skill que cita `y.py`
    contem a string `--x`.

WARN-first (politica secao 6, s106/107): nasce WARN, vira BLOCK quando a base
zerar -- foi assim que o F79b virou BLOCK na s176, por medicao e nao por
vontade. Enquanto houver orfa, bloquear so pararia o commit de quem nao criou o
passivo.

🔴 LIMITES DECLARADOS (verification-stack, AGENTE.md 10.8) -- este sensor
SUBESTIMA de proposito, e o vies e para o lado seguro (nunca acusa quem
documentou):

  (a) **Extracao estatica.** As flags saem dos nos `add_argument` da AST,
      nao de executar `--help`. Parser construido dinamicamente (loop sobre
      lista, subparser gerado) escapa. Rodar 32 subprocessos em todo commit
      custaria mais do que o sinal vale; a convencao da casa e `add_argument`
      explicito, e o desvio fica declarado aqui em vez de virar numero falso.
  (b) **Presenca, nao SEMANTICA.** O check ve a string `--x` na skill certa. Ele
      nao le se a linha explica o argumento ou se e um exemplo de uma linha. Um
      flag citado de passagem conta como documentado -- o check mede piso, nao
      qualidade.
  (c) **Flag generica pode colar em skill errada.** `--json`, `--apply`,
      `--area` aparecem em varios CLIs. Se a skill que cita `y.py` menciona
      `--json` por causa de OUTRO CLI, a flag de `y.py` passa. Isso INFLA a
      cobertura (falso negativo), nunca acusa injustamente.
  (d) ⚰️ **"Flag documentada em DUAS skills" NAO e reportada.** A medicao de
      11/09 encontrou candidatos (`--area` em `analisar-questao` + `estilo-
      flashcard`), mas o unico sinal disponivel e co-ocorrencia -- as duas
      skills citam o CLI e as duas contem a string, o que acontece o tempo todo
      quando skills vizinhas usam CLIs vizinhos. Co-ocorrencia NAO e prova de
      assinatura duplicada, e converter isso em achado seria inventar metrica
      para o painel ficar verde. Fica DECLARADO como nao-verificavel por este
      check.

Uso:
    python tools/cli_signature_check.py [--json] [--limit N]
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()

RE_FLAG = re.compile(r"""add_argument\(\s*['"](--[a-z0-9][a-z0-9\-]*)['"]""", re.IGNORECASE)

#: CLIs isentos, com o motivo escrito. Isencao sem motivo vira buraco silencioso
#: -- foi o que o F95 mediu no registro de portadores.
ISENTOS = {
    "sync_skills.py": "gerador dos proprios espelhos; roda pelo auto_check, nao por agente",
    "setup_hooks.py": "instalador one-shot do hook de git; nao entra em fluxo de estudo",
    "init_db.py": "bootstrap de schema; chamado por teste e migracao, nunca por skill",
}


def flags_de(path: Path):
    """Flags declaradas por `add_argument` no fonte. Estatico -- ver limite (a).

    Le a AST, nao o texto. A 1a versao usava regex sobre o fonte e se acusou a si
    mesma: a string `add_argument("--x")` escrita DENTRO desta docstring virou
    uma flag `--x` inexistente. Achado de graca e didatico -- um sensor que le
    comentario como codigo mede o arquivo, nao o programa. Fallback para regex
    so quando a AST nao parseia (arquivo em edicao); ai o vies volta, declarado.
    """
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        arvore = ast.parse(src)
    except SyntaxError:
        return sorted(set(RE_FLAG.findall(src)))
    achadas = set()
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        alvo = getattr(no.func, "attr", None) or getattr(no.func, "id", None)
        if alvo != "add_argument":
            continue
        for arg in no.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                    and arg.value.startswith("--"):
                achadas.add(arg.value)
    return sorted(achadas)


def _skills(root: Path):
    d = root / ".claude" / "commands"
    if not d.is_dir():
        return {}
    return {p.name: p.read_text(encoding="utf-8", errors="replace") for p in sorted(d.glob("*.md"))}


def donos_de(nome_cli: str, skills: dict):
    """Skills que DECLARAM este CLI (citam o nome do arquivo)."""
    return [s for s, txt in skills.items() if nome_cli in txt]


def run_checks(root=None):
    """[{'alvo': 'tools/x.py', 'payload': {...}}] -- vazio = secao 7.2 satisfeita.

    Assinatura igual aos demais sensores do harness (doc_drift, reachability_check).
    """
    base = Path(root).resolve() if root else ROOT_DIR
    skills = _skills(base)
    achados = []
    for p in sorted((base / "tools").glob("*.py")):
        if p.name.startswith("test_") or p.name == "__init__.py" or p.name in ISENTOS:
            continue
        flags = flags_de(p)
        if not flags:
            continue                      # sem flags nao ha assinatura a documentar
        donos = donos_de(p.name, skills)
        orfas = [f for f in flags
                 if not any(f in skills[s] for s in donos)]
        if orfas:
            achados.append({"alvo": f"tools/{p.name}",
                            "payload": {"flags": len(flags), "orfas": orfas,
                                        "donos": donos}})
    return achados


def main():
    ap = argparse.ArgumentParser(
        description="Assinatura canonica de CLI x skill (D5; WARN-first, exit 0 sempre).")
    ap.add_argument("--json", action="store_true", help="saida JSON (worklist)")
    ap.add_argument("--limit", type=int, default=25,
                    help="quantos CLIs listar no modo texto (default 25)")
    args = ap.parse_args()

    achados = run_checks()
    if args.json:
        print(json.dumps(achados, ensure_ascii=False, indent=2))
        return 0

    total_orfas = sum(len(a["payload"]["orfas"]) for a in achados)
    sem_dono = [a for a in achados if not a["payload"]["donos"]]
    print()
    print("=" * 70)
    print("  Assinatura canonica de CLI (AGENTE.md 7.2) -- WARN, nao bloqueia")
    print("=" * 70)
    print(f"  CLIs com flag orfa : {len(achados)}")
    print(f"  flags orfas        : {total_orfas}")
    print(f"  CLIs sem skill dona: {len(sem_dono)}")
    print()
    for a in sorted(achados, key=lambda x: (-len(x["payload"]["orfas"]), x["alvo"]))[:args.limit]:
        pl = a["payload"]
        dono = ", ".join(pl["donos"]) if pl["donos"] else "NENHUMA SKILL O CITA"
        print(f"  {a['alvo']:<38} {len(pl['orfas'])}/{pl['flags']}  <- {dono}")
        print(f"      {' '.join(pl['orfas'])}")
    if len(achados) > args.limit:
        print(f"  ... +{len(achados) - args.limit} CLI(s) (--limit N, ou --json)")
    print()
    print("  Onde documentar: a skill que ja e dona do CLI; sem dona, a secao de")
    print("  `.claude/commands/engenharia-cli.md`. Depois: `python tools/sync_skills.py`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
