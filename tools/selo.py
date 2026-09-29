"""selo.py -- a tabela item -> terminal da reforma de engenharia, DERIVADA (s187),
e a ROTACAO do ledger (s204).

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
  - `AUDITORIA_MEDHUB.md`  -> a FRENTE: so o que esta em aberto
  - `history/auditoria/resolvidos.md` -> o HISTORICO: o que ja fechou
  - `git log --grep`       -> o commit que fechou cada achado
  - `clausulas_check`      -> cobertura do item 1.10
  - `consistencia_check`   -> discordancias de status (G14, G14b) e de lugar (frente)
  - docstring das suites   -> o ESCOPO que cada sensor novo declara NAO alcancar

ROTACAO (s204, decisao do operador em 28/09/2026: "o que resolvermos, sai da
frente"). `--rotacionar` move para o fim do historico todo bloco de achado cujo
cabecalho diz FEITO, SUPERADO ou RETRATADO e regrava o INDICE do topo da frente.
MITIGADO e PARCIAL ficam: tem residuo declarado. O bloco viaja INTEIRO -- nada e
reescrito, resumido nem apagado. Dry-run por default; `--apply` exige `--expect N`.

⚠️ **Limite declarado:** a coluna `terminal` sai do CABECALHO do achado. Se um
cabecalho mentir, o selo herda a mentira -- foi exatamente o que aconteceu com
F109/F110 (riders pousados, cabecalho ABERTO) e com F36/F72 (sujeito removido,
cabecalho ABERTO). Por isso o selo so fecha com as discordancias em ZERO: os
checks de status sao o contra-peso, e o proprio selo os imprime. Vale tambem para
a rotacao: cabecalho que mente leva o bloco para o arquivo errado.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

LEDGER = os.path.join(ROOT, "AUDITORIA_MEDHUB.md")
#: Onde mora o que ja fechou. `history/` e o SSOT do que aconteceu; o bloco e
#: MOVIDO para ca, nunca copiado (a regra "sem archive/" e contra copia orfa).
LEDGER_RESOLVIDOS = os.path.join(ROOT, "history", "auditoria", "resolvidos.md")
REL_RESOLVIDOS = "history/auditoria/resolvidos.md"

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

#: O que SAI da frente na rotacao. `FEITO (parcial)` (= MITIGADO) e `PARCIAL` ficam:
#: os dois declaram residuo, e residuo e trabalho em aberto.
TERMINAIS_RESOLVIDOS = ("FEITO", "SUPERADO", "RETRATADO")

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

MARCA_INDICE_INI = "<!-- selo:indice:inicio -->"
MARCA_INDICE_FIM = "<!-- selo:indice:fim -->"

_RE_CABECALHO = re.compile(r"^(#{1,3})\s+\S")
_RE_ACHADO = re.compile(r"^###\s+(F\d+)\s*--\s*(.+?)\s*$")
_RE_CONTINUACAO = re.compile(r"\s*atualiza[cç][aã]o", re.I)
_RE_CERCA = re.compile(r"^\s*(```|~~~)")
_RE_SEVERIDADE = re.compile(r"\*\*(ALTA|MEDIA|MÉDIA|BAIXA)\*\*")
_RE_STATUS = re.compile(r"\*\*([^*]+)\*\*\s*$")


# ------------------------------------------------------------- leitura -----

def terminal_de(resto):
    """O terminal que o cabecalho declara, pelo 1o padrao que casar."""
    for rx, nome in REGRAS_TERMINAL:
        if rx.search(resto):
            return nome
    return "SEM TERMINAL"


def blocos(texto):
    """Particiona o ledger em segmentos, SEM perder 1 byte: a concatenacao dos
    `texto` devolvidos e o arquivo de entrada.

    Segmento `F` = do cabecalho `### F<n> -- ...` ate o proximo cabecalho de nivel
    1 a 3. Segmento `outro` = todo o resto (preambulo, secoes narrativas). Linha
    dentro de cerca de codigo nunca e cabecalho -- um `# comentario` num bloco de
    codigo partiria o achado ao meio."""
    partes, atual, em_cerca = [], None, False
    for linha in texto.splitlines(keepends=True):
        if _RE_CERCA.match(linha):
            em_cerca = not em_cerca
        cabecalho = (not em_cerca) and _RE_CABECALHO.match(linha)
        if cabecalho:
            m = _RE_ACHADO.match(linha.rstrip("\r\n"))
            if atual is not None:
                partes.append(atual)
            atual = {"tipo": "F" if m else "outro", "id": m.group(1) if m else None,
                     "cabecalho": m.group(2) if m else linha.strip(), "texto": linha}
            continue
        if atual is None:
            atual = {"tipo": "outro", "id": None, "cabecalho": "", "texto": ""}
        atual["texto"] += linha
    if atual is not None:
        partes.append(atual)
    return partes


def achados_de(texto, onde):
    """Os achados de UM arquivo do ledger. `### F63 -- atualizacao (s165)` e
    continuacao do MESMO achado, nao outro: sem isto o selo conta o item duas
    vezes e o total mente (medido: F63)."""
    saida, vistos = [], set()
    for b in blocos(texto):
        if b["tipo"] != "F":
            continue
        fid, resto = b["id"], b["cabecalho"]
        if _RE_CONTINUACAO.match(resto) or fid in vistos:
            continue
        vistos.add(fid)
        sev = _RE_SEVERIDADE.search(resto)
        status = _RE_STATUS.search(resto)
        saida.append({"id": fid,
                      "titulo": re.split(r"\s+--\s+\*\*", resto)[0].strip(),
                      "terminal": terminal_de(resto),
                      "severidade": (sev.group(1).replace("É", "E") if sev else "-"),
                      "status": (status.group(1).strip() if status else ""),
                      "onde": onde})
    return saida


def _ler(caminho):
    if not os.path.exists(str(caminho)):
        return ""
    with open(str(caminho), encoding="utf-8") as fh:
        return fh.read()


def achados_do_ledger(frente=None, historico=None):
    """Frente + historico. Achado que aparece nos DOIS conta uma vez, pela frente
    -- e a duplicidade e acusada por `fora_do_lugar`."""
    da_frente = achados_de(_ler(frente or LEDGER), "frente")
    ids = {a["id"] for a in da_frente}
    do_hist = [a for a in achados_de(_ler(historico or LEDGER_RESOLVIDOS), "historico")
               if a["id"] not in ids]
    return da_frente + do_hist


def fora_do_lugar(frente=None, historico=None):
    """[(id, motivo)]: resolvido que ainda esta na frente, aberto que foi parar no
    historico, achado nos dois arquivos."""
    da_frente = achados_de(_ler(frente or LEDGER), "frente")
    do_hist = achados_de(_ler(historico or LEDGER_RESOLVIDOS), "historico")
    saida = []
    for a in da_frente:
        if a["terminal"] in TERMINAIS_RESOLVIDOS:
            saida.append((a["id"], "resolvido (%s) ainda na frente -- rotacionar" % a["terminal"]))
    for a in do_hist:
        if a["terminal"] not in TERMINAIS_RESOLVIDOS:
            saida.append((a["id"], "%s no historico -- so resolvido mora la" % a["terminal"]))
    repetidos = {a["id"] for a in da_frente} & {a["id"] for a in do_hist}
    for fid in sorted(repetidos, key=lambda s: int(s[1:])):
        saida.append((fid, "aparece na frente E no historico"))
    return saida


def quem_decide(achado):
    """Derivado do status literal do cabecalho; nunca digitado por item."""
    status = achado["status"].lower()
    if (achado["terminal"] == "GATE" or achado["id"] in GATES_DO_OPERADOR
            or "operador" in status):
        return "operador"
    if "ai-eng" in status:
        return "/ai-eng"
    if "revisar" in status or "verific" in status:
        return "revisao datada"
    return "engenharia"


def rotulo(achado):
    """O status como o operador o le na lista de abertos: o nome do CABECALHO, nao o
    terminal interno do selo (`FEITO (parcial)` numa lista de abertos confundiria)."""
    if achado["id"] in GATES_DO_OPERADOR:
        return "GATE"
    return "MITIGADO" if achado["terminal"] == "FEITO (parcial)" else achado["terminal"]


def _ordem(achado):
    return -int(achado["id"][1:])


def em_aberto(achados):
    return sorted((a for a in achados if a["terminal"] not in TERMINAIS_RESOLVIDOS),
                  key=_ordem)


def linhas_em_aberto(achados):
    """A lista que responde "o que esta em aberto?". TODAS as classes nao
    resolvidas -- ate a s204 GATE e DECLARADO ficavam fora da saida padrao."""
    saida = []
    for a in em_aberto(achados):
        texto = GATES_DO_OPERADOR.get(a["id"]) or a["titulo"]
        saida.append("    %-5s %-5s %-10s %-14s %s"
                     % (a["id"], a["severidade"], rotulo(a), quem_decide(a), texto[:84]))
    return saida


# ------------------------------------------------------------- rotacao -----

def indice(achados):
    """O indice do topo da frente. Sem data de proposito: data faria o arquivo
    envelhecer sozinho, e o que importa e ele bater com o derivado."""
    abertos = em_aberto(achados)
    resolvidos = len(achados) - len(abertos)
    linhas = ["**Em aberto: %d** · Resolvidos: %d (em `%s`) · indice gerado por "
              "`python tools/selo.py --rotacionar`, nunca editado a mao"
              % (len(abertos), resolvidos, REL_RESOLVIDOS),
              "",
              "| Id | Sev. | Status | Quem decide | Achado |",
              "|---|---|---|---|---|"]
    for a in abertos:
        titulo = a["titulo"].replace("|", "/")
        if len(titulo) > 110:
            titulo = titulo[:107].rstrip() + "..."
        linhas.append("| %s | %s | %s | %s | %s |"
                      % (a["id"], a["severidade"], rotulo(a), quem_decide(a), titulo))
    return "\n".join(linhas)


def aplicar_indice(frente, achados):
    """Regrava o que esta ENTRE os marcadores. Frente sem marcadores fica como esta."""
    i = frente.find(MARCA_INDICE_INI)
    f = frente.find(MARCA_INDICE_FIM)
    if i < 0 or f < i:
        return frente
    return (frente[:i + len(MARCA_INDICE_INI)] + "\n" + indice(achados) + "\n"
            + frente[f:])


def rotacionar(frente, historico, hoje=None):
    """(nova_frente, novo_historico, ids_movidos). Puro: recebe e devolve TEXTO.

    Sai da frente todo bloco F cujo achado tem terminal resolvido -- inclusive os
    blocos de continuacao, que seguem o status do pai. O bloco vai INTEIRO para o
    fim do historico, sob `## Rotacionados em <dia>`. Sem nada a mover, os dois
    textos voltam iguais (so o indice e regravado, e ele e deterministico)."""
    hoje = hoje or datetime.date.today().isoformat()
    partes = blocos(frente)
    terminal = {a["id"]: a["terminal"] for a in achados_de(frente, "frente")}
    fica, sai, movidos = [], [], []
    for b in partes:
        if b["tipo"] == "F" and terminal.get(b["id"]) in TERMINAIS_RESOLVIDOS:
            sai.append(b)
            if b["id"] not in movidos:
                movidos.append(b["id"])
        else:
            fica.append(b)
    nova_frente = "".join(b["texto"] for b in fica)
    novo_hist = historico
    if sai:
        corpo = "".join(b["texto"] if b["texto"].endswith("\n") else b["texto"] + "\n"
                        for b in sai)
        novo_hist = (historico.rstrip("\n") + "\n\n## Rotacionados em %s\n\n" % hoje
                     + corpo.rstrip("\n") + "\n")
    achados = achados_de(nova_frente, "frente") + achados_de(novo_hist, "historico")
    return aplicar_indice(nova_frente, achados), novo_hist, movidos


def rotacionar_arquivos(frente, historico, apply=False, expect=None, hoje=None):
    """O `--rotacionar` sobre arquivos. Dry-run por default. `--apply` exige
    `--expect N` igual ao numero MEDIDO de achados a mover (COUNT-ASSERT): o N e
    declarado antes, o dry-run confirma, e so entao se escreve. Exit 0 ok, 2 recusa."""
    texto_f, texto_h = _ler(frente), _ler(historico)
    nova_f, novo_h, movidos = rotacionar(texto_f, texto_h, hoje=hoje)
    print("[rotacao] %d achado(s) resolvido(s) na frente: %s"
          % (len(movidos), ", ".join(movidos) or "nenhum"))
    indice_mudou = nova_f != texto_f and not movidos
    if indice_mudou:
        print("[rotacao] o indice do topo esta diferente do derivado e sera regravado")
    if not apply:
        print("[rotacao] dry-run -- nada escrito (use --apply --expect %d)" % len(movidos))
        return 0
    if expect is None or int(expect) != len(movidos):
        print("[rotacao] RECUSADO: --expect %s, medido %d. Nada escrito."
              % (expect, len(movidos)))
        return 2
    if novo_h != texto_h:
        os.makedirs(os.path.dirname(str(historico)), exist_ok=True)
        with open(str(historico), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(novo_h)
    if nova_f != texto_f:
        with open(str(frente), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(nova_f)
    print("[rotacao] escrito: %d movido(s) para %s" % (len(movidos), REL_RESOLVIDOS))
    return 0


def indice_velho(frente=None, historico=None):
    """True quando o indice do topo da frente nao bate com o derivado."""
    texto = _ler(frente or LEDGER)
    if MARCA_INDICE_INI not in texto:
        return False
    return aplicar_indice(texto, achados_do_ledger(frente, historico)) != texto


# ------------------------------------------------------- o selo em si -----

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
    ap = argparse.ArgumentParser(description="Tabela item -> terminal do selo (derivada) "
                                             "e rotacao do ledger")
    ap.add_argument("--markdown", action="store_true", help="Saida em markdown p/ colar no selo")
    ap.add_argument("--sensores", action="store_true", help="So o escopo declarado dos sensores novos")
    ap.add_argument("--rotacionar", action="store_true",
                    help="Move os achados resolvidos da frente para o historico e regrava "
                         "o indice. Dry-run por default")
    ap.add_argument("--apply", action="store_true",
                    help="--rotacionar: escreve de verdade (exige --expect)")
    ap.add_argument("--expect", type=int,
                    help="--rotacionar --apply: COUNT-ASSERT, N de achados a mover; "
                         "recusado se != N medido")
    ap.add_argument("--onde", metavar="FID",
                    help="Diz em que arquivo o achado mora (ex.: --onde F38)")
    args = ap.parse_args()

    if args.rotacionar:
        return rotacionar_arquivos(LEDGER, LEDGER_RESOLVIDOS, apply=args.apply,
                                   expect=args.expect)

    achados = achados_do_ledger()

    if args.onde:
        fid = args.onde.upper()
        a = next((x for x in achados if x["id"] == fid), None)
        if a is None:
            print("%s: nao existe no ledger" % fid)
            return 1
        arquivo = "AUDITORIA_MEDHUB.md" if a["onde"] == "frente" else REL_RESOLVIDOS
        print("%s: %s -- %s -- %s" % (fid, arquivo, a["terminal"], a["titulo"][:90]))
        return 0

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
    lugar = fora_do_lugar()
    velho = indice_velho()

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

    nao_resolvidos = em_aberto(achados)
    print()
    print(f"  Achados no ledger              : {len(achados)}")
    print(f"    em aberto  (frente)          : {len(nao_resolvidos)}")
    print(f"    resolvidos (historico)       : {len(achados) - len(nao_resolvidos)}")
    print()
    for t in ("FEITO", "SUPERADO", "RETRATADO", "FEITO (parcial)", "PARCIAL", "GATE",
              "DECLARADO", "ABERTO", "SEM TERMINAL"):
        n = sum(1 for a in achados if a["terminal"] == t)
        if n:
            print(f"    {t:<22}       : {n}")
    print()
    print("  EM ABERTO (id, severidade, status, quem decide):")
    for linha in linhas_em_aberto(achados):
        print(linha)
    print()
    print(f"  Item 1.10 -- clausulas normativas : {cob.get('normativas')}")
    print(f"    com CHECK / declaradas / orfas  : {cob.get('com_check')} / "
          f"{cob.get('nao_verificaveis')} / {cob.get('orfas')}  "
          f"({cob.get('cobertura_pct')}% cobertas)")
    print()
    print(f"  Discordancias de status (G14+G14b): {len(disc)}")
    for d in disc:
        print(f"    🔴 {d['check']}: {d['alvo']}")
    print(f"  Fora do lugar (frente x historico): {len(lugar)}")
    for fid, motivo in lugar:
        print(f"    🔴 {fid}: {motivo}")
    if velho:
        print("    🔴 indice do topo da frente diferente do derivado -- `--rotacionar --apply --expect 0`")
    print()
    completa = (not sem_term) and (not disc) and (not lugar) and (not velho) and all(
        a["id"] in GATES_DO_OPERADOR for a in abertos)
    print("  " + ("✅ Todo item tem terminal nomeado, nenhum status diverge e nada esta fora do lugar."
                  if completa else
                  "🔴 NAO fecha: ha item sem terminal, status divergente, item fora do lugar, "
                  "indice velho ou ABERTO sem GATE nomeado."))
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
