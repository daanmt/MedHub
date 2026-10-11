"""Inventario de CLAUSULAS NORMATIVAS e sua cobertura por gate (item 1.10, s187).

O defeito que isto encerra: **nao da para saber quais regras o harness realmente
impoe e quais sao prosa de honra.** O F90 e o F97 sao a forma aguda disso -- uma
clausula revogada continuou prescrevendo porque nada a verificava, e o painel
imprimia PASSED. A forma cronica e pior porque e silenciosa: 283 prescricoes
espalhadas por 23 portadores, e nenhuma maneira de responder "esta e verificada?".

Cada clausula normativa chega a UM de dois terminais, anotado NO PROPRIO PORTADOR
(secao 10.5: regra load-bearing nao mora fora do portador; anotacao sobre a regra,
tampouco -- registro separado drifta em silencio, que e o F95 e o G5):

    <!-- CHECK: NOME_DO_GATE -->
    <!-- NAO-VERIFICAVEL: motivo curto (revisar: YYYY-MM-DD) -->
    <!-- NAO-NORMATIVA: motivo curto -->

A anotacao vale para a clausula na MESMA linha ou na linha imediatamente anterior.

O terceiro terminal existe porque o detector e LEXICAL e erra ~14%: linha narrativa que
cita uma regra ("a 3a regra passou a ter instrumento em 11/09") nao e prescricao. Marca-la
como NAO-VERIFICAVEL seria mentira -- nao e regra sem gate, **nao e regra**. Ele fica em
coluna PROPRIA no resumo, nunca somado a cobertura, justamente para nao virar porta dos
fundos: quem inflar `NAO-NORMATIVA` esta declarando imprecisao do detector, nao cobrindo
clausula. Efeito colateral util: conforme as marcas entram, a precisao do detector passa
de AMOSTRADA a MEDIDA.

🔴 **O gate nomeado tem que EXISTIR.** Anotacao que aponta para check inexistente e
pior que anotacao nenhuma: cria a aparencia de cobertura. E o F90 um nivel acima --
la o registro do gate era manual e tinha buraco; aqui o registro e DERIVADO do
`auto_check` e das suites, e a anotacao e conferida contra ele. Por isso esse achado
nasce BLOCK e nao WARN: o passivo e zero por construcao (nenhuma anotacao mentirosa
existe hoje), que e a mesma condicao que promoveu o F79b e o D5.

⚠️ **LIMITES DECLARADOS do detector (nunca maquiados):**
  - E LEXICAL: acha marcador deontico ("deve", "nunca", "sempre", "exige", ...), nao
    normatividade. Amostra de 14 lida a olho em 18/09/2026: **12 normativas, 2 prosa
    narrativa** (~86%). O numero e CANDIDATO, nao censo.
  - Exclui linha de TABELA e HEADING por medicao, nao por gosto: 64 dos 347 hits
    crus eram doc de flag de CLI (`| --sessao | Exige ... |`, que o argparse ja
    impoe) ou titulo de secao. Ficaram 283.
  - NAO mede se o gate anotado testa mesmo AQUELA clausula -- so que ele existe.
    Essa e a metade semantica, e fica declarada como nao-verificavel por construcao
    (secao 10.8, verification-stack).
"""
import argparse
import ast
import datetime as _dt
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Portadores de norma. Resumos e history NAO entram: conteudo clinico e registro
# historico nao prescrevem comportamento do agente.
def portadores(root=None):
    root = root or ROOT
    alvos = sorted(glob.glob(os.path.join(root, ".claude", "commands", "*.md")))
    alvos += sorted(glob.glob(os.path.join(root, "core", "contracts", "*.md")))
    alvos += [os.path.join(root, "AGENTE.md")]
    return [a for a in alvos if os.path.exists(a)]


#: Os MESMOS portadores de `portadores()`, como caminho do git (relativo a raiz, com `/`).
#: Espelha o glob: `*.md` direto na pasta (nao recursivo) e sem arquivo oculto.
RE_PORTADOR_GIT = re.compile(r"(?:\.claude/commands|core/contracts)/[^/.][^/]*\.md|AGENTE\.md")
PATHSPECS_PORTADORES = (".claude/commands", "core/contracts", "AGENTE.md")


DEONTICO = re.compile(
    r"\b(deve[m]?|dever[aá][o]?|nunca|jamais|sempre|obrigat[oó]ri[oa]|proibid[oa]|"
    r"veda[do]{0,2}|exige|exigid[oa]|tem que|t[eê]m que|precisa[m]? ser|"
    r"n[aã]o pode[m]?|impresc[ií]nd[ií]vel|inegoci[aá]vel|regra:|invariante|"
    r"cl[aá]usula)\b", re.I)

LINHA_DE_TABELA = re.compile(r"^\s*\|")
HEADING = re.compile(r"^\s*#{1,6}\s")

RE_CHECK = re.compile(r"<!--\s*CHECK:\s*([^>]+?)\s*-->")
RE_NAOVERIF = re.compile(
    r"<!--\s*NAO-VERIFICAVEL:\s*(.+?)\s*\(revisar:\s*(\d{4}-\d{2}-\d{2})\s*\)\s*-->")
RE_NAOVERIF_SEM_DATA = re.compile(r"<!--\s*NAO-VERIFICAVEL:(?!.*revisar:)")
RE_NAONORM = re.compile(r"<!--\s*NAO-NORMATIVA:\s*(.+?)\s*-->")

#: CATRACA do item 1.10 (s189, pedido do /ai-eng): a contagem de orfas NAO SOBE sem declaracao.
#: Ate a Fase 0 Lote 0 part-3 a base era DIGITADA (a constante `BASE_ORFAS`, fixa em 127:
#: "subir exige editar esta linha"), e teve folga: a contagem caiu a 126 (s216-s218), a base
#: nao desceu, e a 127a (s219, 4122645) e a 128a (s221, 953124c) entraram escondidas. Agora a
#: base e CALCULADA: a contagem do HEAD, lida pelo git (`orfas_na_revisao`). Descer segue
#: livre -- o proximo HEAD ja e a base menor -- e subir nao tem mais numero a editar: a unica
#: declaracao e o terminal na clausula.
#: Historico medido na s189 (o sensor rodado em worktree de cada commit): 127 no selo da janela
#: 6 da s187 (b96348b), 132 no ultimo commit da s187 (d4f0bb8: +5 da secao do cards_rendimento
#: e do recall imediato do /revisar), 132 na s188 (+0 -- o "+7 da s188" do HANDOFF era
#: atribuicao errada sobre um 125 medido antes), 134 com a s189, 127 depois de anotar as 7.
#:
#: SEVERIDADE (`severidade_catraca`): no `--staged` (pre-commit) o DELTA indice x HEAD e
#: BLOCK; no `--changed`/`--all` (arvore x HEAD) segue WARN. O delta tem base ZERO por construcao
#: -- toda orfa a mais que o HEAD foi criada neste commit --, a mesma razao que faz
#: `gate_inexistente` nascer BLOCK (AGENTE.md secao 6: regra nova nasce WARN e so vira BLOCK
#: "quando a base zerar"). O PASSIVO (as orfas que o HEAD ja tem) segue WARN: ele nasceu em 271.
#: O pre-commit le o INDICE, nunca a arvore: dois agentes dividem a arvore (AGENTE.md secao 10),
#: e orfa nao-staged de um nao pode bloquear o commit do outro.


class GitIlegivel(RuntimeError):
    """O git nao respondeu (fora de repo, binario ausente, objeto ilegivel)."""


def severidade_catraca(modo):
    """Severidade do delta de orfas por modo do `auto_check`. PURA.

    `--staged` = o pre-commit: BLOCK (base zero por construcao, ver o comentario acima).
    Qualquer outro modo (`--changed`, `--all`) compara a ARVORE com o HEAD: WARN.
    """
    return "BLOCK" if modo == "--staged" else "WARN"


def catraca(orfas, base):
    """`None` se a contagem de orfas nao passou da base; senao a mensagem. PURA.

    `base` e a contagem do HEAD, calculada (`orfas_na_revisao("HEAD")`); `None` = repo sem
    HEAD, nada a comparar. A severidade nao mora aqui: e de `severidade_catraca(modo)`.
    """
    if base is None or orfas is None or orfas <= base:
        return None
    return (f"{orfas} orfas > {base} no HEAD: {orfas - base} clausula(s) nova(s) sem terminal. "
            f"Anote no mesmo ato (`<!-- CHECK: nome -->`, "
            f"`<!-- NAO-VERIFICAVEL: motivo (revisar: AAAA-MM-DD) -->` ou "
            f"`<!-- NAO-NORMATIVA: motivo -->`) -- a base e o HEAD, nao ha numero a subir.")


def extrair(path):
    """Clausulas candidatas de UM portador. Lista de dicts, sem I/O alem da leitura."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        texto = fh.read()
    return extrair_texto(texto, os.path.relpath(path, ROOT).replace("\\", "/"))


def extrair_texto(texto, portador):
    """Clausulas candidatas de um TEXTO de portador (do disco ou de uma revisao do git). PURA.

    `portador` e o rotulo gravado em cada achado (caminho relativo a raiz, com `/`).
    """
    linhas = texto.splitlines()
    achados, dentro_code = [], False
    for i, ln in enumerate(linhas):
        if ln.strip().startswith("```"):
            dentro_code = not dentro_code
            continue
        if dentro_code or not DEONTICO.search(ln):
            continue
        if LINHA_DE_TABELA.match(ln) or HEADING.match(ln):
            continue
        # a anotacao vale na mesma linha OU na imediatamente anterior
        vizinhanca = ln + "\n" + (linhas[i - 1] if i > 0 else "")
        m_check = RE_CHECK.search(vizinhanca)
        m_nv = RE_NAOVERIF.search(vizinhanca)
        achados.append({
            "portador": portador,
            "linha": i + 1,
            "texto": ln.strip()[:220],
            "check": m_check.group(1).strip() if m_check else None,
            "nao_verificavel": m_nv.group(1).strip() if m_nv else None,
            "revisar_em": m_nv.group(2) if m_nv else None,
            "nv_sem_data": bool(RE_NAOVERIF_SEM_DATA.search(vizinhanca)) and not m_nv,
            "nao_normativa": (RE_NAONORM.search(vizinhanca).group(1).strip()
                              if RE_NAONORM.search(vizinhanca) else None),
        })
    return achados


def registro_de_gates():
    """Nomes de gate que EXISTEM, derivados -- nunca enumerados a mao (licao do F90/F95).

    Tres fontes: (a) slugs em CAIXA-ALTA e ids F/D/G citados nas descricoes de check do
    `auto_check`; (b) nome de cada modulo `tools/test_*.py`; (c) nome de cada funcao
    `test_*` dentro deles.
    """
    nomes = set()
    ac = os.path.join(ROOT, "tools", "auto_check.py")
    if os.path.exists(ac):
        with open(ac, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        for desc in re.findall(r'desc_\w+\s*=\s*["\'](.+?)["\']', src):
            nomes.update(re.findall(r"\b[A-Z][A-Z0-9_]{3,}\b", desc))
            nomes.update(re.findall(r"\b[FDG]\d{1,3}[a-z]?\b", desc))
    for t in sorted(glob.glob(os.path.join(ROOT, "tools", "test_*.py"))):
        nomes.add(os.path.splitext(os.path.basename(t))[0])
        try:
            with open(t, encoding="utf-8", errors="replace") as fh:
                arvore = ast.parse(fh.read())
        except SyntaxError:                                    # pragma: no cover
            continue
        for n in ast.walk(arvore):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_"):
                nomes.add(n.name)
    return nomes


def run_checks(hoje=None, gates=None):
    """Achados sobre TODOS os portadores. Read-only, puro salvo leitura de arquivo.

    Devolve (achados, resumo). Severidade:
      gate_inexistente -> BLOCK (anotacao que mente e pior que anotacao nenhuma)
      nv_sem_data      -> BLOCK (marca sem data nunca e revisitada -- vira permanente)
      nv_vencida       -> WARN  (a data chegou; re-decidir)
      orfa             -> WARN  (warn-first: o passivo nasce grande, por construcao)
    `gates`: o registro ja derivado (o `auto_check` deriva uma vez e reusa na catraca).
    """
    gates = registro_de_gates() if gates is None else gates
    clausulas = [c for p in portadores() for c in extrair(p)]
    return classificar(clausulas, gates, hoje)


#: Tipos que contam como ORFA no resumo (`normativas - com_check - nao_verificaveis`): tudo o
#: que nao chegou a terminal VALIDO. Fora o BLOCK proprio de `gate_inexistente`/`nv_sem_data`,
#: os dois tambem somam aqui -- e isso que mantem a catraca e o `ORFAS` impresso no mesmo numero.
SEM_TERMINAL = ("orfa", "gate_inexistente", "nv_sem_data")


def classificar(clausulas, gates, hoje=None):
    """(achados, resumo) sobre clausulas ja extraidas. PURA."""
    hoje = hoje or _dt.date.today()
    achados, total, cobertas, declaradas, ruido = [], 0, 0, 0, 0
    for c in clausulas:
        total += 1
        if c["nv_sem_data"]:
            achados.append({**c, "tipo": "nv_sem_data", "severidade": "BLOCK"})
            continue
        if c["check"]:
            if c["check"] not in gates:
                achados.append({**c, "tipo": "gate_inexistente", "severidade": "BLOCK"})
            else:
                cobertas += 1
            continue
        if c["nao_normativa"]:
            ruido += 1          # imprecisao DECLARADA do detector -- nunca cobertura
            continue
        if c["nao_verificavel"]:
            declaradas += 1
            if _dt.date.fromisoformat(c["revisar_em"]) < hoje:
                achados.append({**c, "tipo": "nv_vencida", "severidade": "WARN"})
            continue
        achados.append({**c, "tipo": "orfa", "severidade": "WARN"})
    normativas = total - ruido            # denominador honesto: ruido nao e clausula
    resumo = {
        "clausulas": total, "normativas": normativas, "com_check": cobertas,
        "nao_verificaveis": declaradas, "nao_normativas": ruido,
        "orfas": normativas - cobertas - declaradas,
        "cobertura_pct": (round(100.0 * (cobertas + declaradas) / normativas, 1)
                          if normativas else 0.0),
        "gates_conhecidos": len(gates),
        "block": sum(1 for a in achados if a["severidade"] == "BLOCK"),
    }
    return achados, resumo


# --- contagem numa REVISAO do git (catraca, Fase 0 Lote 0 part-3) ----------------------

def _git(root, args, entrada=None):
    """stdout (bytes) de `git -C root <args>`; `GitIlegivel` se o git falhar."""
    try:
        res = subprocess.run(["git", "-C", root, "-c", "core.quotepath=false", *args],
                             input=entrada, capture_output=True, check=False)
    except OSError as e:                                   # git fora do PATH
        raise GitIlegivel(f"git indisponivel ({e})") from e
    if res.returncode != 0:
        erro = res.stderr.decode("utf-8", "replace").strip().splitlines()
        raise GitIlegivel(f"git {' '.join(args[:2])}: {erro[-1] if erro else res.returncode}")
    return res.stdout


def _revisao_existe(rev, root):
    """False para `HEAD` de repo sem commit (o 1o commit); `GitIlegivel` fora de repo."""
    try:
        res = subprocess.run(["git", "-C", root, "rev-parse", "-q", "--verify", f"{rev}^{{commit}}"],
                             capture_output=True, check=False)
    except OSError as e:
        raise GitIlegivel(f"git indisponivel ({e})") from e
    if res.returncode == 0:
        return True
    if res.returncode == 1 and not res.stderr.strip():   # repo valido, revisao ausente
        return False
    erro = res.stderr.decode("utf-8", "replace").strip().splitlines()
    raise GitIlegivel(f"git rev-parse: {erro[-1] if erro else res.returncode}")


def _ler_blobs(objetos, root):
    """Conteudo de cada objeto (`HEAD:caminho` ou `:caminho`) num UNICO `git cat-file --batch`.

    Medido em 10/10/2026 (25 portadores): um `git show` por portador custava 1,6-1,8 s para
    HEAD + indice, a cada commit; o lote unico custa uma fracao disso (Decisao Tecnica 3 da spec).
    """
    if not objetos:
        return []
    pedido = "".join(o + "\n" for o in objetos).encode("utf-8")
    saida = _git(root, ["cat-file", "--batch"], entrada=pedido)
    textos, pos = [], 0
    for obj in objetos:
        fim = saida.find(b"\n", pos)
        cabecalho = saida[pos:fim].decode("utf-8", "replace").split() if fim >= 0 else []
        if len(cabecalho) != 3 or cabecalho[1] != "blob":
            raise GitIlegivel(f"cat-file {obj}: {' '.join(cabecalho) or 'sem resposta'}")
        tamanho = int(cabecalho[2])
        textos.append(saida[fim + 1:fim + 1 + tamanho].decode("utf-8", "replace"))
        pos = fim + 1 + tamanho + 1                      # o blob termina com um LF extra
    return textos


def conteudos_na_revisao(rev, root=None):
    """[(portador, texto)] dos portadores numa revisao. `None` se a revisao nao existe.

    `rev`: `":"` = o INDICE (o que o commit vai selar); `None` = a ARVORE (disco); qualquer
    outro = commit-ish do git (`"HEAD"`). Mesmo conjunto de `portadores()` (`RE_PORTADOR_GIT`).
    """
    root = root or ROOT
    if rev is None:
        pares = []
        for p in portadores(root):
            with open(p, encoding="utf-8", errors="replace") as fh:
                pares.append((os.path.relpath(p, root).replace("\\", "/"), fh.read()))
        return pares
    if rev == ":":
        lista = _git(root, ["ls-files", "-z", "--", *PATHSPECS_PORTADORES])
        prefixo = ":"
    else:
        if not _revisao_existe(rev, root):
            return None
        lista = _git(root, ["ls-tree", "-r", "-z", "--name-only", rev, "--", *PATHSPECS_PORTADORES])
        prefixo = f"{rev}:"
    caminhos = [c for c in dict.fromkeys(lista.decode("utf-8", "replace").split("\0"))
                if c and RE_PORTADOR_GIT.fullmatch(c)]
    return list(zip(caminhos, _ler_blobs([prefixo + c for c in caminhos], root)))


def _sem_terminal(rev, root, gates):
    """Achados SEM terminal valido na revisao (`SEM_TERMINAL`); `None` se ela nao existe."""
    pares = conteudos_na_revisao(rev, root)
    if pares is None:
        return None
    clausulas = [c for portador, texto in pares for c in extrair_texto(texto, portador)]
    achados, _ = classificar(clausulas, gates)
    return [a for a in achados if a["tipo"] in SEM_TERMINAL]


def orfas_na_revisao(rev, root=None, gates=None):
    """Contagem de orfas numa revisao do git (`"HEAD"`, ou `":"` = indice); `None` sem HEAD.

    O mesmo numero que `run_checks()[1]["orfas"]` daria sobre aquele conteudo. O registro de
    gates e o da ARVORE (o mesmo do `run_checks`) dos dois lados da comparacao: a catraca mede
    o delta de CONTEUDO dos portadores; conferir o nome do CHECK e do `gate_inexistente`.
    """
    gates = registro_de_gates() if gates is None else gates
    sem = _sem_terminal(rev, root or ROOT, gates)
    return None if sem is None else len(sem)


def catraca_contra_head(modo, root=None, gates=None):
    """A catraca do 1.10 contra o HEAD, no recorte do modo. Nunca levanta por falha do git.

    `--staged`: indice x HEAD; outro modo: arvore x HEAD. Devolve dict com `severidade`
    (`severidade_catraca(modo)`), `mensagem` (`None` = nao subiu), `aviso` (`None` = mediu),
    `head`, `atual` e `recorte`. Sem HEAD (1o commit) ou git ilegivel: `mensagem` None e
    `aviso` dizendo por que -- nunca BLOCK sem medida, nunca silencio.
    """
    root = root or ROOT
    recorte = ":" if modo == "--staged" else None
    out = {"severidade": severidade_catraca(modo), "mensagem": None, "aviso": None,
           "head": None, "atual": None, "recorte": "indice" if recorte == ":" else "arvore"}
    gates = registro_de_gates() if gates is None else gates
    try:
        base = _sem_terminal("HEAD", root, gates)
        if base is None:
            out["aviso"] = ("repo sem HEAD (1o commit): a catraca nao tem base -- nada a "
                            "comparar, sem BLOCK.")
            return out
        atual = _sem_terminal(recorte, root, gates)
    except (GitIlegivel, OSError) as e:
        out["aviso"] = (f"git ilegivel ({e}): orfas x HEAD nao medidas neste run -- sem BLOCK, "
                        f"mas o delta ficou sem sensor.")
        return out
    out["head"], out["atual"] = len(base), len(atual)
    msg = catraca(len(atual), len(base))
    if msg:
        # quais sao as novas: diferenca de multiconjunto por TEXTO (nao por arquivo, para que
        # portador renomeado nao vire "novo"). Clausula nova com texto igual a uma orfa antiga
        # escapa da amostra -- o numero do delta, nao.
        resto = {}
        for a in base:
            resto[a["texto"]] = resto.get(a["texto"], 0) + 1
        novas = []
        for a in atual:
            if resto.get(a["texto"], 0):
                resto[a["texto"]] -= 1
            else:
                novas.append(f"{a['portador']}:{a['linha']}")
        onde = "; ".join(novas[:5]) + ("; ..." if len(novas) > 5 else "")
        out["mensagem"] = msg + (f" Nova(s) no {out['recorte']}: {onde}." if novas else "")
    return out


def main():
    p = argparse.ArgumentParser(description="Inventario de clausulas normativas (1.10)")
    p.add_argument("--json", action="store_true", help="Saida JSON (contrato de maquina)")
    p.add_argument("--portador", help="Filtra por caminho (substring)")
    p.add_argument("--orfas", action="store_true", help="So as clausulas sem terminal")
    p.add_argument("--por-portador", action="store_true", help="Contagem agregada por arquivo")
    args = p.parse_args()

    achados, resumo = run_checks()
    if args.portador:
        achados = [a for a in achados if args.portador in a["portador"]]
    if args.orfas:
        achados = [a for a in achados if a["tipo"] == "orfa"]

    if args.json:
        print(json.dumps({"resumo": resumo, "achados": achados},
                         ensure_ascii=False, indent=2))
        return 1 if resumo["block"] else 0

    print()
    print(f"  Hits do detector                : {resumo['clausulas']}")
    print(f"    marcadas NAO-NORMATIVA (ruido): {resumo['nao_normativas']}"
          f"   <- imprecisao declarada, fora do denominador")
    print(f"  Clausulas normativas            : {resumo['normativas']}")
    print(f"    com CHECK nomeado             : {resumo['com_check']}")
    print(f"    declaradas nao-verificaveis   : {resumo['nao_verificaveis']}")
    print(f"    ORFAS (sem terminal)          : {resumo['orfas']}")
    print(f"  Cobertura                       : {resumo['cobertura_pct']}%"
          f"   (gates conhecidos: {resumo['gates_conhecidos']})")
    print()
    print("  🔴 O numero e CANDIDATO, nao censo: o detector e LEXICAL. Amostra lida a")
    print("     olho em 18/09/2026: 12 de 14 normativas (~86%). Ver limites na docstring.")
    print()
    if args.por_portador:
        por = {}
        for a in achados:
            por.setdefault(a["portador"], []).append(a)
        for k in sorted(por, key=lambda x: -len(por[x])):
            print(f"    {len(por[k]):>4}  {k}")
        print()
    graves = [a for a in achados if a["severidade"] == "BLOCK"]
    for a in graves:
        print(f"  [BLOCK] {a['tipo']}  {a['portador']}:{a['linha']}")
        print(f"          {a['texto'][:140]}")
    if args.orfas or args.portador:
        for a in achados[:60]:
            if a["severidade"] != "BLOCK":
                print(f"  [{a['tipo']}] {a['portador']}:{a['linha']}  {a['texto'][:120]}")
    return 1 if graves else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
