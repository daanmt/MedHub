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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Portadores de norma. Resumos e history NAO entram: conteudo clinico e registro
# historico nao prescrevem comportamento do agente.
def portadores():
    alvos = sorted(glob.glob(os.path.join(ROOT, ".claude", "commands", "*.md")))
    alvos += sorted(glob.glob(os.path.join(ROOT, "core", "contracts", "*.md")))
    alvos += [os.path.join(ROOT, "AGENTE.md")]
    return [a for a in alvos if os.path.exists(a)]


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
#: Subir exige editar ESTA linha no mesmo commit que cria a clausula sem terminal -- o diff do
#: git e a declaracao. Descer e livre (e desejado): baixe a base quando a contagem cair.
#: Historico medido na s189 (o sensor rodado em worktree de cada commit): 127 no selo da janela
#: 6 da s187 (b96348b), 132 no ultimo commit da s187 (d4f0bb8: +5 da secao do cards_rendimento
#: e do recall imediato do /revisar), 132 na s188 (+0 -- o "+7 da s188" do HANDOFF era
#: atribuicao errada sobre um 125 medido antes), 134 com a s189, 127 depois de anotar as 7.
BASE_ORFAS = 127


def catraca(orfas, base=BASE_ORFAS):
    """`None` se a contagem de orfas nao passou da base; senao a mensagem do WARN. PURA."""
    if orfas <= base:
        return None
    return (f"{orfas} orfas > base {base}: {orfas - base} clausula(s) nova(s) sem terminal. "
            f"Anote no mesmo ato (`<!-- CHECK: nome -->`, `NAO-VERIFICAVEL` com data ou "
            f"`NAO-NORMATIVA`) ou suba BASE_ORFAS em tools/clausulas_check.py no MESMO commit "
            f"-- o diff e a declaracao.")


def extrair(path):
    """Clausulas candidatas de UM portador. Lista de dicts, sem I/O alem da leitura."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        linhas = fh.read().splitlines()
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
            "portador": os.path.relpath(path, ROOT).replace("\\", "/"),
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


def run_checks(hoje=None):
    """Achados sobre TODOS os portadores. Read-only, puro salvo leitura de arquivo.

    Devolve (achados, resumo). Severidade:
      gate_inexistente -> BLOCK (anotacao que mente e pior que anotacao nenhuma)
      nv_sem_data      -> BLOCK (marca sem data nunca e revisitada -- vira permanente)
      nv_vencida       -> WARN  (a data chegou; re-decidir)
      orfa             -> WARN  (warn-first: o passivo nasce grande, por construcao)
    """
    hoje = hoje or _dt.date.today()
    gates = registro_de_gates()
    achados, total, cobertas, declaradas, ruido = [], 0, 0, 0, 0
    for p in portadores():
        for c in extrair(p):
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
