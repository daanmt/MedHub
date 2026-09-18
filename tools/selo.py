"""selo.py -- a tabela item -> terminal da reforma de engenharia, DERIVADA (s187).

O selo de "reforma completa" tem de **provar, item a item, por conteudo** que todo
item de engenharia chegou a um terminal nomeado:

  FEITO      -- commit + suite
  DECLARADO  -- marca literal "nao-verificavel" + data de revisao
  GATE       -- pergunta de 1 linha ao operador, nomeada
  SUPERADO   -- o sujeito do achado deixou de existir

🔴 **A tabela e DERIVADA, nunca digitada.** Uma tabela de selo mantida a mao e a
mesma classe do G5 (tabela gerada que envelhece) e do F95 (registro manual com
buraco) -- e seria especialmente ridicula aqui, porque o que ela audita e
justamente registros que mentiam sobre o proprio status.

Fontes, todas ja existentes:
  - `AUDITORIA_MEDHUB.md`  -> cabecalho de cada achado (status por conteudo)
  - `git log --grep`       -> o commit que fechou cada achado
  - `clausulas_check`      -> cobertura do item 1.10
  - `consistencia_check`   -> discordancias cabecalho x §11 (G14) e x portador (G14b)
  - docstring das suites   -> o ESCOPO que cada sensor novo declara NAO alcancar

⚠️ **Limite declarado:** a coluna `terminal` sai do CABECALHO do achado. Se um
cabecalho mentir, o selo herda a mentira -- foi exatamente o que aconteceu com
F109/F110 (riders pousados, cabecalho ABERTO) e com F36/F72 (sujeito removido,
cabecalho ABERTO). Por isso o selo so fecha com as discordancias em ZERO: os dois
checks de status sao o contra-peso, e o proprio selo os imprime.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

LEDGER = os.path.join(ROOT, "AUDITORIA_MEDHUB.md")

# Terminal derivado do cabecalho, por CONTEUDO. Ordem importa: o 1o que casar vence.
REGRAS_TERMINAL = [
    (re.compile(r"\*\*SUPERAD", re.I), "SUPERADO"),
    # `RESOLVIDO` e `RESOLVIDOS` (agregado, ex. F75 "12/12 RESOLVIDOS"), `ENTREGUE`,
    # `FECHADO`, `CONCLUIDO` -- vocabulario real do ledger, medido, nao suposto.
    (re.compile(r"\*\*(?:[^*]*)?(?:RESOLVID[OA]S?|ENTREGUE|FECHAD[OA]|CONCLUID[OA]|REVOGAD[OA])", re.I), "FEITO"),
    (re.compile(r"\*\*MITIGAD", re.I), "FEITO (parcial)"),
    (re.compile(r"\*\*RETRATAD", re.I), "RETRATADO"),
    (re.compile(r"\*\*GATE", re.I), "GATE"),
    (re.compile(r"\*\*DECLARAD[OA]", re.I), "DECLARADO"),
    (re.compile(r"\*\*ABERTO", re.I), "ABERTO"),
    (re.compile(r"\*\*PARCIAL", re.I), "PARCIAL"),
]

# Itens ABERTO que sao de DADO/POLITICA do operador -> terminal GATE, com a
# pergunta de 1 linha. Nao sao engenharia e nao entram no codigo sem ordem dele.
# 🔴 Esta e a UNICA parte digitada do selo, e e digitada porque a pergunta ao
# operador nao existe em lugar nenhum de onde deriva-la. Cada linha e um contrato
# com ele, nao um dado do repo.
GATES_DO_OPERADOR = {
    "F87":  "Quais cards do baralho pagam aluguel? (o harness ve FORMA, nao RENDIMENTO)",
    "F100": "Re-ensinar nao fechou 3 pontos da s175 -- mudo o metodo de re-ensino?",
    "F105": "Triar as 11 marcas de pergunta composta abertas na fila de reforja?",
    "F111": "R8: o extensivo leitura-first garante recall no dia 1? (decision brief, prazo 02/11)",
}

# Sensores nascidos nesta janela -> a suite que os prova. O ESCOPO que cada um
# declara NAO alcancar sai da docstring da suite, nao daqui (F116: rotulo tem de
# dizer o escopo real).
SENSORES_DA_JANELA = {
    "F115 -- comprimento total do card":       "tools/test_comprimento_total.py",
    "1.10 -- clausula com terminal":           "tools/test_clausulas_check.py",
    "Invariante A -- ensino nao escreve FSRS": "tools/test_invariante_a.py",
    "F99 -- leitor de card por id":            "tools/test_card_por_id.py",
    "G14b -- cabecalho x portador":            "tools/test_status_portador.py",
    "F116 -- escopo do linter no --staged":    "tools/test_linter_escopo_staged.py",
}


def achados_do_ledger():
    with open(LEDGER, encoding="utf-8") as fh:
        txt = fh.read()
    saida = []
    vistos = set()
    for m in re.finditer(r"^###\s+(F\d+)\s*--\s*(.+)$", txt, re.M):
        fid, resto = m.group(1), m.group(2)
        # `### F63 -- atualizacao (s165)` e continuacao do MESMO achado, nao outro.
        # Sem isto o selo conta o item duas vezes e o total mente (medido: F63).
        if re.match(r"\s*atualiza[cç][aã]o", resto, re.I) or fid in vistos:
            continue
        vistos.add(fid)
        terminal = "SEM TERMINAL"
        for rx, nome in REGRAS_TERMINAL:
            if rx.search(resto):
                terminal = nome
                break
        titulo = re.split(r"\s+--\s+\*\*", resto)[0]
        saida.append({"id": fid, "titulo": titulo.strip(), "terminal": terminal})
    return saida


def commit_de(fid):
    """O commit que nomeia o achado. Derivado do git, nunca digitado."""
    try:
        r = subprocess.run(["git", "log", "--oneline", "-1", f"--grep={fid}\\b", "-E"],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        linha = (r.stdout or "").strip().splitlines()
        return linha[0].split()[0] if linha else ""
    except Exception:                                        # pragma: no cover
        return ""


def escopo_declarado(caminho_suite):
    """O que o sensor declara NAO alcancar, lido da docstring da propria suite."""
    p = os.path.join(ROOT, caminho_suite)
    if not os.path.exists(p):
        return "(suite ausente)"
    with open(p, encoding="utf-8") as fh:
        txt = fh.read()
    m = re.search(r'"""(.*?)"""', txt, re.S)
    doc = m.group(1) if m else ""
    for marca in ("LIMITE DECLARADO", "ESCOPO DECLARADO", "Limite declarado",
                  "LIMITES DECLARADOS", "Fronteira declarada"):
        i = doc.find(marca)
        if i >= 0:
            trecho = doc[i:i + 420].replace("\n", " ")
            trecho = re.sub(r"\s+", " ", trecho).replace("*", "")
            return trecho.strip()
    return "(sem limite declarado na docstring -- defeito: todo sensor declara o que nao ve)"


def discordancias():
    try:
        import consistencia_check as cc
        return [a for a in cc.run_checks() if a["check"] in ("status", "portador")]
    except Exception as e:                                   # pragma: no cover
        return [{"check": "erro", "alvo": str(e), "payload": {}}]


def cobertura_110():
    try:
        import clausulas_check as cn
        return cn.run_checks()[1]
    except Exception as e:                                   # pragma: no cover
        return {"erro": str(e)}


def main():
    ap = argparse.ArgumentParser(description="Tabela item -> terminal do selo (derivada)")
    ap.add_argument("--markdown", action="store_true", help="Saida em markdown p/ colar no selo")
    ap.add_argument("--sensores", action="store_true", help="So o escopo declarado dos sensores novos")
    args = ap.parse_args()

    achados = achados_do_ledger()
    disc = discordancias()
    cob = cobertura_110()

    if args.sensores:
        print("\n| Sensor novo (s187) | O que ele DECLARA nao alcancar |")
        print("|---|---|")
        for nome, suite in SENSORES_DA_JANELA.items():
            print(f"| {nome} | {escopo_declarado(suite)[:300]} |")
        return 0

    abertos = [a for a in achados if a["terminal"] == "ABERTO"]
    sem_term = [a for a in achados if a["terminal"] == "SEM TERMINAL"]

    if args.markdown:
        print("| Item | Terminal | Evidencia |")
        print("|---|---|---|")
        for a in achados:
            if a["terminal"] in ("FEITO", "FEITO (parcial)", "SUPERADO"):
                ev = commit_de(a["id"]) or "(ledger)"
            elif a["terminal"] == "ABERTO":
                ev = GATES_DO_OPERADOR.get(a["id"], "DECLARADO -- ver ledger")
            else:
                ev = "(ledger)"
            term = "GATE" if (a["terminal"] == "ABERTO" and a["id"] in GATES_DO_OPERADOR) else a["terminal"]
            print(f"| {a['id']} | {term} | {ev} |")
        return 0

    print()
    print(f"  Achados no ledger              : {len(achados)}")
    for t in ("FEITO", "FEITO (parcial)", "SUPERADO", "PARCIAL", "RETRATADO", "ABERTO", "SEM TERMINAL"):
        n = sum(1 for a in achados if a["terminal"] == t)
        if n:
            print(f"    {t:<22}       : {n}")
    print()
    print("  ABERTOS, com terminal nomeado:")
    for a in abertos:
        alvo = GATES_DO_OPERADOR.get(a["id"])
        print(f"    {a['id']:<6} {'GATE      ' if alvo else 'DECLARADO '} {alvo or a['titulo'][:76]}")
    print()
    print(f"  Item 1.10 -- clausulas normativas : {cob.get('normativas')}")
    print(f"    com CHECK / declaradas / orfas  : {cob.get('com_check')} / "
          f"{cob.get('nao_verificaveis')} / {cob.get('orfas')}  "
          f"({cob.get('cobertura_pct')}% cobertas)")
    print()
    print(f"  Discordancias de status (G14+G14b): {len(disc)}")
    for d in disc:
        print(f"    🔴 {d['check']}: {d['alvo']}")
    print()
    completa = (not sem_term) and (not disc) and all(
        a["id"] in GATES_DO_OPERADOR for a in abertos)
    print("  " + ("✅ Todo item tem terminal nomeado e nenhum status diverge."
                  if completa else
                  "🔴 NAO fecha: ha item sem terminal, status divergente, ou ABERTO sem GATE nomeado."))
    if sem_term:
        print("     sem terminal: " + ", ".join(a["id"] for a in sem_term))
    for a in abertos:
        if a["id"] not in GATES_DO_OPERADOR:
            print(f"     ABERTO sem GATE nomeado: {a['id']} -- {a['titulo'][:70]}")
    return 0 if completa else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
