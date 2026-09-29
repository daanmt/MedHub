"""rotacao_ledger_s204.py -- migracao ONE-SHOT: parte o `AUDITORIA_MEDHUB.md` em
frente (so o que esta em aberto) e historico (`history/auditoria/resolvidos.md`).

JA APLICADA em 28/09/2026 (s204). NAO re-rodar: depois dela quem move achado
resolvido e `python tools/selo.py --rotacionar`. Fica aqui como registro do que
foi feito e de como foi provado. Spec: `.vibeflow/specs/ledger-rotacao-part-1.md`.

O que a migracao faz, e so isso:
  - o documento antigo vai INTEIRO para o historico, na ordem original (as secoes
    narrativas inclusive), menos os blocos dos achados em aberto;
  - os blocos dos achados em aberto vao para a frente, do mais novo para o mais
    antigo, sob um preambulo novo;
  - o frontmatter antigo (5 linhas de metadado) e substituido nos dois arquivos.

PROVA DE CONSERVACAO (recusa escrever se qualquer uma falhar):
  1. o multiconjunto dos sha256 dos blocos F e o mesmo antes e depois;
  2. todo segmento que nao e bloco F esta no historico, byte a byte, na ordem;
  3. conta de bytes: corpo antigo = corpo do historico + blocos da frente;
  4. `selo.rotacionar` sobre o resultado move ZERO e `fora_do_lugar` fica vazio.

Uso:  python tools/_archive/migrations/rotacao_ledger_s204.py            # dry-run
      python tools/_archive/migrations/rotacao_ledger_s204.py --apply
"""
import argparse
import hashlib
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import selo  # noqa: E402

FRONTMATTER_FRENTE = """---
type: report
layer: root
status: working-draft
relates_to: [AGENTE, ESTADO, HANDOFF]
---
"""

PREAMBULO_FRENTE = FRONTMATTER_FRENTE + """
# AUDITORIA_MEDHUB -- o que esta EM ABERTO

> **Este arquivo so tem achado em aberto.** O que foi resolvido mora em
> `history/auditoria/resolvidos.md`, com o texto inteiro e as secoes narrativas de cada sessao.
> Decisao do operador em 28/09/2026 (s204): *"o que resolvermos, sai da frente"*.
>
> **Encoding:** ASCII limpo, Zero LaTeX, sem setas Unicode (AGENTE.md secao 4.5). Usar `->`, `<=`, `--`.

## Como usar

1. **Ver o estado:** `python tools/selo.py` -- aberto x resolvido, e quem decide cada item. **Achar um achado:** `python tools/selo.py --onde F38`.
2. **Antes de escrever achado novo:** buscar o mecanismo AQUI e no historico (`grep` pelos termos). Se ja existe, a entrada nova cita a antiga. Gate-miss da s204: o F140 re-derivou errado o que o F32 ja tinha certo.  <!-- NAO-VERIFICAVEL: nada le a intencao de escrever um achado; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
3. **Cabecalho do achado:** id, titulo, severidade e status, nesta ordem, separados por ` -- `. Severidade: ALTA (fere integridade de estado/SSOT), MEDIA (custo recorrente), BAIXA (polimento). Status que FICA na frente: ABERTO, GATE (pergunta ao operador), DECLARADO (remedio proposto ou nao-verificavel datado), PARCIAL, MITIGADO. Status que SAI: RESOLVIDO, SUPERADO, RETRATADO.
4. **No selo da sessao:** `python tools/selo.py --rotacionar` (dry-run) e depois `--apply --expect N`. O bloco viaja inteiro; nada e reescrito, resumido nem apagado.  <!-- CHECK: test_repo_real_consistente -->

## Indice

<!-- selo:indice:inicio -->
<!-- selo:indice:fim -->

## Achados em aberto

"""

CABECA_HISTORICO = """---
type: report
layer: history
status: archive
relates_to: [AGENTE, HANDOFF]
---

> **HISTORICO DO LEDGER.** Aqui mora todo achado RESOLVIDO, SUPERADO ou RETRATADO, com o texto
> inteiro, e as secoes narrativas das sessoes de auditoria. O que esta em aberto mora em
> `AUDITORIA_MEDHUB.md`. Rotacao de partida em 28/09/2026 (s204, decisao do operador); dai em
> diante, `python tools/selo.py --rotacionar` acrescenta ao FIM deste arquivo.
> Citacao por NUMERO DE LINHA escrita antes da rotacao nao vale mais: procure pelo id do achado.

"""


def _sha(texto):
    return hashlib.sha256(texto.strip().encode("utf-8")).hexdigest()


def _sem_frontmatter(texto):
    """(frontmatter, corpo). Frontmatter = bloco `---` ... `---` no topo."""
    if not texto.startswith("---"):
        return "", texto
    fim = texto.find("\n---", 3)
    fim = texto.find("\n", fim + 1) + 1
    return texto[:fim], texto[fim:]


def migrar(antigo):
    fm, corpo = _sem_frontmatter(antigo)
    partes = selo.blocos(corpo)
    assert "".join(p["texto"] for p in partes) == corpo, "particao perdeu texto"
    terminal = {a["id"]: a["terminal"] for a in selo.achados_de(corpo, "frente")}
    abertos = [p for p in partes if p["tipo"] == "F"
               and terminal.get(p["id"]) not in selo.TERMINAIS_RESOLVIDOS]
    resto = [p for p in partes if p not in abertos]

    # frente: do mais novo para o mais antigo; a continuacao segue o pai
    ordem = []
    for p in abertos:
        if p["id"] not in ordem:
            ordem.append(p["id"])
    ordem.sort(key=lambda fid: -int(fid[1:]))
    blocos_frente = []
    for fid in ordem:
        for p in abertos:
            if p["id"] == fid:
                txt = p["texto"].rstrip("\n") + "\n\n"
                blocos_frente.append(txt)
    frente = PREAMBULO_FRENTE + "".join(blocos_frente).rstrip("\n") + "\n"
    historico = CABECA_HISTORICO + "".join(p["texto"] for p in resto)

    frente, historico, movidos = selo.rotacionar(frente, historico)

    # ---- provas ----
    provas = []
    antes = sorted(_sha(p["texto"]) for p in partes if p["tipo"] == "F")
    depois = sorted(_sha(b["texto"]) for t in (frente, historico)
                    for b in selo.blocos(t) if b["tipo"] == "F")
    provas.append(("1. sha256 dos blocos F conservado (%d blocos)" % len(antes),
                   antes == depois))
    cursor, em_ordem = 0, True
    for p in resto:
        i = historico.find(p["texto"], cursor)
        if i < 0:
            em_ordem = False
            break
        cursor = i + len(p["texto"])
    provas.append(("2. %d segmentos nao-abertos no historico, byte a byte, na ordem"
                   % len(resto), em_ordem))
    bytes_resto = sum(len(p["texto"]) for p in resto)
    bytes_abertos = sum(len(p["texto"]) for p in abertos)
    provas.append(("3. conta de bytes: corpo %d = resto %d + abertos %d"
                   % (len(corpo), bytes_resto, bytes_abertos),
                   len(corpo) == bytes_resto + bytes_abertos))
    provas.append(("3b. historico = cabeca nova + resto (%d bytes)" % len(historico),
                   len(historico) == len(CABECA_HISTORICO) + bytes_resto))
    provas.append(("4. rotacionar sobre o resultado move zero", movidos == []))
    achados = selo.achados_de(frente, "frente") + selo.achados_de(historico, "historico")
    total_antes = len(selo.achados_de(corpo, "frente"))
    provas.append(("5. total de achados %d = %d" % (total_antes, len(achados)),
                   total_antes == len(achados)))
    errados = ([a["id"] for a in selo.achados_de(frente, "frente")
                if a["terminal"] in selo.TERMINAIS_RESOLVIDOS]
               + [a["id"] for a in selo.achados_de(historico, "historico")
                  if a["terminal"] not in selo.TERMINAIS_RESOLVIDOS])
    provas.append(("6. nada fora do lugar", errados == []))
    return frente, historico, provas, {"abertos": ordem, "frontmatter_antigo": fm,
                                        "bytes_antigo": len(antigo)}


def main():
    ap = argparse.ArgumentParser(description="Migracao one-shot da rotacao do ledger (s204)")
    ap.add_argument("--apply", action="store_true", help="Escreve os dois arquivos")
    args = ap.parse_args()
    if os.path.exists(selo.LEDGER_RESOLVIDOS):
        print("[migracao] RECUSADO: %s ja existe -- a migracao ja foi aplicada. "
              "Use `python tools/selo.py --rotacionar`." % selo.REL_RESOLVIDOS)
        return 2
    with open(selo.LEDGER, encoding="utf-8") as fh:
        antigo = fh.read()
    frente, historico, provas, info = migrar(antigo)
    ok = True
    for nome, passou in provas:
        print("  [%s] %s" % ("OK" if passou else "FALHOU", nome))
        ok = ok and passou
    print("  abertos na frente (%d): %s" % (len(info["abertos"]), ", ".join(info["abertos"])))
    print("  bytes: antigo %d -> frente %d + historico %d"
          % (info["bytes_antigo"], len(frente), len(historico)))
    if not ok:
        print("[migracao] RECUSADO: prova de conservacao falhou. Nada escrito.")
        return 2
    if not args.apply:
        print("[migracao] dry-run -- nada escrito (use --apply)")
        return 0
    os.makedirs(os.path.dirname(selo.LEDGER_RESOLVIDOS), exist_ok=True)
    with open(selo.LEDGER_RESOLVIDOS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(historico)
    with open(selo.LEDGER, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(frente)
    print("[migracao] escrito: AUDITORIA_MEDHUB.md e %s" % selo.REL_RESOLVIDOS)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
