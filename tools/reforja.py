#!/usr/bin/env python3
"""reforja.py -- a fila de reforja de flashcards como ESTADO consultavel (B2, s176).

O problema que este CLI encerra: ate hoje uma marcacao de reforja era uma FRASE num
`HANDOFF.md`. Consequencias medidas -- o passivo foi contado como 12, 13, 15 e 38 em
sessoes diferentes (G7, quatro numeros para a mesma pergunta), e o card #792 viajou
marcado por tres sessoes e esta em `card_version = 1`: nunca foi tocado.

🔴 E o fechamento e VERIFICADO, nao declarado. F82 estabeleceu que `card_version` nao
e evidencia de reforja feita (#321 em v2 com o defeito intacto); a s176 mediu o caso
mais duro: #1568 tem evento `reforja` de 2026-09-09 (v1 -> v2) e CONTINUA disparando
`checar_contrafactual_mal_formado`. Reescrever nao e o mesmo que resolver. Por isso
`--fechar` re-roda o predicado que motivou a marca e recusa se ele ainda acusar.

Camada fina sobre `app.utils.db` -- nao abre `sqlite3` proprio.

Uso:
    python tools/reforja.py --fila [--todas] [--json]
    python tools/reforja.py --marcar 792 --motivo contrafactual_mal_formado [--origem s176]
    python tools/reforja.py --fechar 1568 --motivo contrafactual_mal_formado
    python tools/reforja.py --fechar 1568 --motivo X --forcar --justificativa "..."
    python tools/reforja.py --descartar 243 --motivo X --justificativa "olhei, nao era defeito"
    python tools/reforja.py --ingerir nao_atomico       # worklist de detector -> fila (dry-run)
    python tools/reforja.py --ingerir nao_atomico --apply
    python tools/reforja.py --backfill --dry-run        # declara o COUNT antes de escrever
    python tools/reforja.py --backfill --apply          # decisao do OPERADOR

Assinatura canonica documentada em `.claude/commands/estilo-flashcard.md` (AGENTE.md secao 7.2).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import db  # noqa: E402
import card_checks  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Marcas que existiam SO EM PROSA, com a proveniencia de cada uma. Esta lista e o
# escopo INTEIRO do backfill -- deliberadamente so o que tem origem citavel.
#
# 🔴 O "passivo ~37" que o HANDOFF menciona NAO entra: nao existe lista dele em lugar
# nenhum, so o numero. Fabricar 37 linhas a partir de um numero sem nomes seria
# inventar estado -- exatamente a doenca que este CLI existe para curar. Ele fica
# declarado como nao-migrado; quando alguem produzir a lista, ela entra por --marcar.
BACKFILL = [
    (792, "contrafactual_mal_formado", "HANDOFF s175: '#792 (3a marcacao)' -- 1 de 3"),
    (792, "contrafactual_mal_formado", "HANDOFF s175: '#792 (3a marcacao)' -- 2 de 3"),
    (792, "contrafactual_mal_formado", "HANDOFF s175: '#792 (3a marcacao)' -- 3 de 3"),
    (582, "multi_parte", "HANDOFF s175: '#582/#583 compostas, confirmadas em uso'"),
    (583, "multi_parte", "HANDOFF s175: '#582/#583 compostas, confirmadas em uso'"),
    (1568, "contrafactual_mal_formado", "HANDOFF s175: '#1568 NOVO' -- frente pede achado ausente"),
    (243, "pacote_de_fatos", "HANDOFF s175: passivo nomeado"),
    (561, "pacote_de_fatos", "HANDOFF s175: passivo nomeado"),
    (321, "pergunta_generica", "HANDOFF s175: '#321 (rated 4, defeito intacto)' -- F82"),
]


def cmd_fila(args):
    fila = db.fila_reforja(incluir_fechadas=args.todas)
    if args.json:
        print(json.dumps(fila, ensure_ascii=False, indent=2))
        return 0
    if not fila:
        print("Fila de reforja vazia.")
        return 0
    abertas = [d for d in fila if d["aberta"]]
    print()
    print("=" * 66)
    print("  Fila de reforja -- a UNICA cifra citavel do passivo (G7)")
    print("=" * 66)
    print(f"  abertas: {len(abertas)}" + (f"   (listando {len(fila)}, com fechadas)" if args.todas else ""))

    # Resumo por motivo (s177, 1.6): com a ingestao de detector a fila passa de
    # dezenas para centenas de linhas. Sem o agregado, a cifra citavel voltaria a
    # ser "role a tela e conte" -- que e a doenca que este CLI curou no 0.3.
    por_motivo = {}
    for d in abertas:
        por_motivo[d["motivo"]] = por_motivo.get(d["motivo"], 0) + 1
    if len(por_motivo) > 1 or len(abertas) > args.limit:
        print()
        print("  por motivo (abertas):")
        for motivo, n in sorted(por_motivo.items(), key=lambda kv: (-kv[1], kv[0])):
            selo = "" if motivo in card_checks.PREDICADOS_VERIFICAVEIS else "  [sem predicado]"
            print(f"    {n:>4}  {motivo}{selo}")
    print()

    mostradas = fila[:args.limit]
    for d in mostradas:
        estado = "ABERTA " if d["aberta"] else "fechada"
        marca = f"{d['n_marcacoes']}x" if d["n_marcacoes"] > 1 else "  "
        verificavel = "" if d["motivo"] in card_checks.PREDICADOS_VERIFICAVEIS else "  [sem predicado]"
        print(f"  {estado} #{d['card_id']:<5} {marca:>3}  {d['motivo']}{verificavel}")
    if len(fila) > len(mostradas):
        print(f"  ... +{len(fila) - len(mostradas)} linha(s) (--limit N, ou --json para a lista inteira)")
    print()
    nao_verificaveis = {d["motivo"] for d in fila
                        if d["motivo"] not in card_checks.PREDICADOS_VERIFICAVEIS}
    if nao_verificaveis:
        print("  [DECLARADO] motivos sem predicado que os meca -- fecham por palavra humana,")
        print("              e a linha grava `evidencia='humana'`: " + ", ".join(sorted(nao_verificaveis)))
        print()
    return 0


def cmd_marcar(args):
    rid = db.marcar_reforja(args.marcar, args.motivo, origem=args.origem)
    fila = [d for d in db.fila_reforja() if d["card_id"] == args.marcar and d["motivo"] == args.motivo]
    n = fila[0]["n_marcacoes"] if fila else 1
    print(f"[MARCADA] #{args.marcar} '{args.motivo}' (linha {rid}) -- {n}a marcacao deste par.")
    if n >= 3:
        print(f"  🔴 {n} marcacoes e ZERO fechamentos. Foi assim que o #792 atravessou tres "
              f"sessoes sem nunca ser tocado -- marcar de novo nao move o card.")
    return 0


def cmd_fechar(args):
    try:
        rid = db.fechar_reforja(args.fechar, args.motivo, forcar=args.forcar,
                                justificativa=args.justificativa, origem=args.origem)
    except db.ReforjaAindaDefeituosa as e:
        print(f"[RECUSADO] {e}", file=sys.stderr)
        return 1
    print(f"[FECHADA] #{args.fechar} '{args.motivo}' (linha {rid}).")
    return 0


def cmd_descartar(args):
    rid = db.descartar_reforja(args.descartar, args.motivo, args.justificativa, origem=args.origem)
    print(f"[DESCARTADA] #{args.descartar} '{args.motivo}' (linha {rid}) -- "
          f"desfecho legitimo e DIFERENTE de 'resolvi'.")
    return 0


def cmd_backfill(args):
    existentes = {(d["card_id"], d["motivo"]): d["n_marcacoes"]
                  for d in db.fila_reforja(incluir_fechadas=True)}
    faltantes = []
    for card_id, motivo, origem in BACKFILL:
        ja = existentes.get((card_id, motivo), 0)
        pedidos = sum(1 for c, m, _ in BACKFILL if (c, m) == (card_id, motivo))
        if sum(1 for f in faltantes if (f[0], f[1]) == (card_id, motivo)) < pedidos - ja:
            faltantes.append((card_id, motivo, origem))

    print()
    print(f"  COUNT-ASSERT declarado ANTES de escrever: {len(faltantes)} linha(s) a criar "
          f"(de {len(BACKFILL)} marcas com proveniencia).")
    for card_id, motivo, origem in faltantes:
        print(f"    #{card_id:<5} {motivo:<28} <- {origem}")
    print()
    print("  🔴 NAO migrado, declarado: o 'passivo ~37' do HANDOFF nao tem lista em lugar")
    print("     nenhum, so o numero. Fabricar 37 linhas a partir de um numero sem nomes seria")
    print("     inventar estado -- a propria doenca que esta fila cura. Entra por --marcar")
    print("     quando alguem produzir a lista.")
    print()

    if not args.apply:
        print("  [DRY-RUN] nada foi escrito. Rodar com --apply e decisao do OPERADOR.")
        return 0

    escritas = 0
    for card_id, motivo, origem in faltantes:
        db.marcar_reforja(card_id, motivo, origem=f"backfill: {origem}")
        escritas += 1
    if escritas != len(faltantes):
        print(f"  [ERRO] COUNT-ASSERT falhou: declarei {len(faltantes)}, escrevi {escritas}.",
              file=sys.stderr)
        return 1
    print(f"  [APLICADO] {escritas} linha(s) criadas -- bate com o COUNT declarado.")
    return 0


def cmd_ingerir(args):
    """F39 (s177, 1.6): a worklist de um detector vira ESTADO com lifecycle.

    O defeito que isto encerra: o check de atomicidade acusa ~270 cards a cada
    rodada do harness ha 47 dias, e o numero nao se move -- nao porque ninguem
    olhou, mas porque olhar nao tinha onde ser gravado. WARN solto nao distingue
    "ainda nao triado" de "triado e e falso-positivo". A fila distingue: ABERTA,
    `fechada` (predicado re-verificado) e `descartada` (palavra humana: olhei e
    nao era defeito).

    Idempotente por construcao -- par (card, motivo) que ja tem QUALQUER marca
    nao recebe outra:
      * ABERTA      -> re-marcar inflaria `n_marcacoes`, cujo significado e
                       "marcado de novo e ninguem tocou". Detector re-rodando
                       nao e sinal humano novo.
      * descartada  -> o veredito humano seria apagado a cada varredura.
      * fechada E AINDA acusando -> NAO re-marca em silencio: reporta. E a classe
                       F82 ("edicao != resolucao"); re-abrir sozinho esconderia
                       que um fechamento nao valeu.
    """
    motivo = args.ingerir.strip()
    predicado = card_checks.PREDICADOS_VERIFICAVEIS.get(motivo)
    if predicado is None:
        print(f"[RECUSADO] '{motivo}' nao esta em card_checks.PREDICADOS_VERIFICAVEIS.",
              file=sys.stderr)
        print("  Ingerir por motivo sem predicado criaria marca que NENHUMA maquina "
              "sabe fechar -- fila que so cresce.", file=sys.stderr)
        print("  Disponiveis: " + ", ".join(sorted(card_checks.PREDICADOS_VERIFICAVEIS)),
              file=sys.stderr)
        return 1

    cards = db.cards_ativos_para_predicado()
    acusados = [c["id"] for c in cards if predicado(c)]

    marcas = {(d["card_id"], d["motivo"]): d for d in db.fila_reforja(incluir_fechadas=True)}
    novos, ja_abertas, encerradas_reacusando = [], [], []
    for card_id in acusados:
        d = marcas.get((card_id, motivo))
        if d is None:
            novos.append(card_id)
        elif d["aberta"]:
            ja_abertas.append(card_id)
        else:
            encerradas_reacusando.append(card_id)

    print()
    print(f"  Ingestao de '{motivo}' sobre {len(cards)} cards ATIVOS.")
    print(f"  predicado acusa : {len(acusados)}")
    print(f"  ja ABERTAS      : {len(ja_abertas)} (nao re-marca: inflaria n_marcacoes)")
    print(f"  ja encerradas   : {len(encerradas_reacusando)}", end="")
    if encerradas_reacusando:
        print(f"  🔴 fechada/descartada e o predicado AINDA acusa: "
              f"{encerradas_reacusando[:10]}{' ...' if len(encerradas_reacusando) > 10 else ''}")
        print("                    -> classe F82 (edicao != resolucao) ou descarte consciente "
              "de falso-positivo; nao re-marco em silencio.")
    else:
        print()
    print(f"  COUNT-ASSERT declarado ANTES de escrever: {len(novos)} linha(s) a criar.")
    print()
    print("  🔴 FALSO-POSITIVO CONHECIDO no lote: card DISCRIMINADOR (\"A x B: qual das")
    print("     duas ...?\") dispara duplo-ask e e legitimo. O desempate e contar CRITERIOS")
    print("     DE ACERTO, e nenhum regex faz isso -- por desenho o desfecho desses e")
    print("     `--descartar` com justificativa, nunca `--fechar`.")
    print()

    if not args.apply:
        print("  [DRY-RUN] nada foi escrito. Rodar de novo com --apply.")
        return 0

    origem = args.origem or f"detector:{motivo}"
    escritas = 0
    for card_id in novos:
        db.marcar_reforja(card_id, motivo, origem=origem)
        escritas += 1
    if escritas != len(novos):
        print(f"  [ERRO] COUNT-ASSERT falhou: declarei {len(novos)}, escrevi {escritas}.",
              file=sys.stderr)
        return 1
    print(f"  [APLICADO] {escritas} linha(s) criadas -- bate com o COUNT declarado.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Fila de reforja de flashcards como estado (B2)")
    p.add_argument("--fila", action="store_true", help="Lista o passivo (default)")
    p.add_argument("--todas", action="store_true", help="Inclui marcas ja fechadas/descartadas")
    p.add_argument("--json", action="store_true", help="Saida em JSON")
    p.add_argument("--marcar", type=int, metavar="CARD_ID", help="Abre uma marca de reforja")
    p.add_argument("--fechar", type=int, metavar="CARD_ID",
                   help="Fecha uma marca RE-VERIFICANDO o predicado que a motivou")
    p.add_argument("--descartar", type=int, metavar="CARD_ID",
                   help="Encerra a marca como 'nao era defeito' (exige --justificativa)")
    p.add_argument("--motivo", help="Nome do defeito; se for um predicado conhecido, o "
                                    "fechamento e verificado por maquina")
    p.add_argument("--justificativa", help="Texto obrigatorio em --descartar e em --forcar")
    p.add_argument("--forcar", action="store_true",
                   help="Fecha mesmo com o predicado ainda acusando (exige --justificativa)")
    p.add_argument("--origem", help="Sessao/contexto que originou a marca")
    p.add_argument("--ingerir", metavar="MOTIVO",
                   help="Varre os cards ATIVOS com um predicado de card_checks e "
                        "propoe marcas (dry-run; --apply escreve)")
    p.add_argument("--limit", type=int, default=25,
                   help="Quantas linhas detalhar em --fila (default 25; --json nao corta)")
    p.add_argument("--backfill", action="store_true", help="Migra as marcas que viviam em prosa")
    p.add_argument("--dry-run", action="store_true", dest="dry_run",
                   help="Com --backfill/--ingerir: so declara o COUNT, nao escreve")
    p.add_argument("--apply", action="store_true",
                   help="Com --backfill/--ingerir: executa apos o COUNT-ASSERT")
    args = p.parse_args()

    if args.backfill:
        return cmd_backfill(args)
    if args.ingerir:
        return cmd_ingerir(args)
    for flag, fn in (("marcar", cmd_marcar), ("fechar", cmd_fechar), ("descartar", cmd_descartar)):
        if getattr(args, flag) is not None:
            if not args.motivo:
                p.error(f"--{flag} exige --motivo")
            return fn(args)
    return cmd_fila(args)


if __name__ == "__main__":
    sys.exit(main())
