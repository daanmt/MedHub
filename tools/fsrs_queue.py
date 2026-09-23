"""fsrs_queue.py — fila de revisão FSRS em JSON para revisão conversacional.

Camada fina sobre ``app.utils.db``: lê a fila de cards vencidos via
``get_cards_by_bucket()`` e grava avaliações via ``record_review()``. Não abre
``sqlite3`` nem reimplementa o FSRS — delega tudo à camada de acesso canônica,
preservando o caminho de escrita único e o audit trail em ``fsrs_revlog``.

Existe para que o agente (Claude Code) conduza a revisão dentro da conversa
— inclusive via remote-control no celular. É a ÚNICA superfície de revisão
desde o pivot agent-first (s074): a UI local foi removida.

Uso:
    python tools/fsrs_queue.py --next [--area X] [--tema Y]
    python tools/fsrs_queue.py --list [--area X] [--tema Y] [--limit N] [--new-limit M] [--cluster]
    python tools/fsrs_queue.py --record <card_id> --rating <1-4>
    python tools/fsrs_queue.py --export-player [--limit N] [--sessao ID] [--out ARQ.json]
    python tools/fsrs_queue.py --build-player --lote ARQ.json [--out PAGINA.html]
    python tools/fsrs_queue.py --record-lote NOTAS.json --lote ARQ.json [--apply --expect N]

Ordem da fila: atrasados -> hoje -> novos. Com --cluster (F3), a prioridade de
bucket é preservada e, dentro de cada bucket, os cards são agrupados por
(area, tema) — revisão em cluster sem re-agrupamento manual. Cards aposentados
(needs_qualitative >= 2) são excluídos pela própria query do db.

Player (spec plano-ssot-e-cards-v2-part-9): o trio --export-player /
--build-player / --record-lote leva o DRENAR para uma pagina (Artifact) e
traz as notas de volta. A pagina NUNCA grava FSRS: quem grava e o
--record-lote, por `record_review` -- o caminho de escrita unico continua
sendo `app/utils/db.py` (Invariante C do revisao-calibrada-contract).

Assinatura canônica documentada em .claude/commands/revisar.md (contrato §7.2).
"""
import argparse
from datetime import date, datetime
import io
import json
import os
from pathlib import Path
import sys

# Saída sempre em UTF-8 — evita UnicodeEncodeError no console cp1252 do Windows
# quando o card contém marcadores clínicos (🔴, ⚠️, ⭐) ou acentuação.
if __name__ == "__main__" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Permite importar app.utils.db ao rodar como script standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ...e os CLIs irmaos de tools/ (day_plan detem o teto do dia -- F64, um contador so)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import db  # noqa: E402
from app.utils import notas_player  # noqa: E402


def _cluster_key(card):
    """Chave de agrupamento (area, tema); cards sem taxonomia vão ao fim do bucket."""
    return (card.get("area") is None, card.get("area") or "",
            card.get("tema") is None, card.get("tema") or "")


PREVALENCIA_PATH = Path(__file__).resolve().parents[1] / "core" / "cronograma" / "prevalencia_enamed.json"
_RANK = {"alta": 0, "media": 1, "baixa": 2}


def load_prevalencia(path=None):
    """Mapa (area, tema) -> rank (0 alta, 1 media, 2 baixa) lido de
    core/cronograma/prevalencia_enamed.json (insumo manual, F63). Arquivo
    ausente ou invalido -> {} (a fila volta ao FIFO, nunca quebra)."""
    path = Path(path) if path else PREVALENCIA_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {(t.get("area"), t.get("tema")): _RANK.get(t.get("prevalencia"), 3)
            for t in data.get("temas", []) if t.get("tema")}


def rank_novos_por_prevalencia(cards, prev_map, new_limit):
    """Reordena o bucket `novos` por prevalencia ENAMED (alta -> media -> baixa
    -> sem sinal), desempate por card_id (FIFO original), e corta em new_limit.
    Puro: nao toca banco nem FSRS -- so a ORDEM de introducao muda (s165:
    'prevalencia = prioridade na fila dos nunca introduzidos')."""
    def key(c):
        return (prev_map.get((c.get("area"), c.get("tema")), 3), int(c.get("card_id", 0)))
    ordered = sorted(cards, key=key)
    return ordered[:new_limit] if new_limit is not None else ordered


def _ordered_queue(area=None, tema=None, limit=None, new_limit=10, cluster=False,
                   prevalencia=False):
    """Achata os buckets na ordem de prioridade, anotando o bucket de origem.

    P3 part-2: ordem `atrasados → erros_frescos → hoje → novos` — card de erro
    recente fura a fila ANTES de novos FIFO (banda prioritária explícita); cada
    card já vem com `selection_reason` do db. Com cluster=True (F3), ordena
    secundariamente por (area, tema) DENTRO de cada bucket — sort estável
    preserva a sub-ordem por due no mesmo tema.
    """
    if prevalencia:
        # puxa o pool inteiro de state=0 e reordena em Python (o LIMIT do SQL
        # cortaria em FIFO antes da prevalencia agir)
        buckets = db.get_cards_by_bucket(area=area, tema=tema, new_limit=10**6)
        buckets["novos"] = rank_novos_por_prevalencia(
            buckets.get("novos", []), load_prevalencia(), new_limit)
    else:
        buckets = db.get_cards_by_bucket(area=area, tema=tema, new_limit=new_limit)
    ordered = []
    for nome in ("atrasados", "erros_frescos", "hoje", "novos"):
        cards = buckets.get(nome, [])
        if cluster:
            cards = sorted(cards, key=_cluster_key)
        for card in cards:
            card = dict(card)
            card["bucket"] = nome
            ordered.append(card)
    if limit is not None:
        ordered = ordered[:limit]
    return ordered


def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False, default=str))


# ---------------------------------------------------------------------------
# Player de cards (spec plano-ssot-e-cards-v2-part-9)
# ---------------------------------------------------------------------------

#: Campos que viajam do banco para a TELA do player. Tudo que a pagina nao
#: mostra fica fora do export de proposito (`needs_qualitative` e `due` sao
#: estado do FSRS, nao conteudo de card). `selection_reason` vai porque a
#: pagina o exibe ("por que o card veio", revisar.md) E porque o --record-lote
#: o propaga para o revlog.
CAMPOS_PLAYER = ("card_id", "frente_contexto", "frente_pergunta", "verso_resposta",
                 "verso_regra_mestre", "verso_armadilha", "area", "tema",
                 "selection_reason", "bucket")

TEMPLATE_PLAYER = Path(__file__).resolve().parents[1] / "core" / "templates" / "player.html"
MARCA_ABRE = '<script id="lote" type="application/json">'
MARCA_FECHA = "</script>"
TETO_FALLBACK = 60


def teto_do_dia(ordered):
    """Teto de cards do dia. O SSOT do numero e `day_plan` (F64: UM contador --
    `vencidos = atrasados + hoje`, nunca `atrasados` sozinho). Import indisponivel
    -> TETO_FALLBACK com WARN em stderr: degrada, mas nunca em silencio (F60)."""
    vencidos = sum(1 for c in ordered if c.get("bucket") in ("atrasados", "hoje"))
    try:
        import day_plan
        return int(day_plan._teto_efetivo(vencidos))
    except Exception as e:
        print("[WARN] teto do dia veio do fallback (%s): day_plan indisponivel (%s)"
              % (TETO_FALLBACK, e), file=sys.stderr)
        return TETO_FALLBACK


def montar_lote(ordered, limit=None, sessao=None, gerado_em=None):
    """Lote do player a partir da fila JA ordenada. Puro: nao toca banco.

    Preserva a ordem e os buckets do --list e corta em `limit`. So os
    CAMPOS_PLAYER viajam."""
    if limit is not None:
        ordered = ordered[:limit]
    cards = []
    for c in ordered:
        item = {k: c.get(k) for k in CAMPOS_PLAYER}
        if item.get("card_id") is not None:
            item["card_id"] = int(item["card_id"])
        cards.append(item)
    return {
        "sessao": sessao or date.today().isoformat(),
        "gerado_em": gerado_em or datetime.now().isoformat(timespec="seconds"),
        "total": len(cards),
        "cards": cards,
    }


def injetar_lote(template, lote):
    """Injeta o lote no `<script id="lote" type="application/json">` do template.

    `<`, `>` e `&` viram escape \\uXXXX: dentro de uma string JSON isso e
    equivalente e torna `</script>` impossivel de fechar por dentro do texto do
    card. A pagina le com `JSON.parse(textContent)`."""
    bruto = json.dumps(lote, ensure_ascii=False, default=str)
    seguro = (bruto.replace("&", "\\u0026")
                   .replace("<", "\\u003c")
                   .replace(">", "\\u003e"))
    ocorrencias = template.count(MARCA_ABRE)
    if ocorrencias != 1:
        # Guarda nascida de um bug real: um comentario do template citava a
        # propria tag, o `find` casava com a MENCAO e a injecao comia a pagina
        # inteira ate o proximo </script>. Marcador ambiguo falha ALTO.
        raise ValueError("template com %d ocorrencia(s) do marcador %r -- "
                         "tem de ser exatamente 1" % (ocorrencias, MARCA_ABRE))
    i = template.find(MARCA_ABRE)
    ini = i + len(MARCA_ABRE)
    fim = template.find(MARCA_FECHA, ini)
    if fim < 0:
        raise ValueError("template sem </script> depois do marcador do lote")
    return template[:ini] + seguro + template[fim:]


def lista_de_notas(obj):
    """A lista `notas` do JSON (`{"notas": [...]}` ou a lista crua), ou None."""
    notas = obj.get("notas") if isinstance(obj, dict) else obj
    return notas if isinstance(notas, list) else None


RAIZ = Path(__file__).resolve().parents[1]
#: Quarentena no SSOT (s193, decisao 4 do `/ai-eng`): doc rejeitado ou nota FORA DE ORDEM
#: e copiado INTEIRO, com o motivo, para `history/quarentena/<sessao>.json` no `--apply` --
#: nada sai do `db` da pagina (poda) sem copia commitada no repo.
PASTA_QUARENTENA = RAIZ / "history" / "quarentena"
#: Marca da ultima gravacao do hub (s193, decisao 5): a fila do chat avisa se ela e velha.
MARCADOR_HUB = RAIZ / "tmp" / "hub" / "ultima_gravacao_hub.json"
JANELA_HUB_H = 6


def arquivo_quarentena(sessao, pasta=None):
    """`history/quarentena/<sessao>.json` (sessao saneada para nome de arquivo)."""
    nome = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in str(sessao or "sessao"))
    return Path(pasta or PASTA_QUARENTENA) / (nome + ".json")


def triar_notas(obj, cards, agora=None, fuso=None):
    """A quarentena com o doc CRU: `(registros, rejeitadas, avisos)`.

    `rejeitadas` = [{"indice", "doc", "motivo"}] -- o que o `--apply` arquiva antes de
    qualquer poda; cada `registro` leva o doc cru em "doc" (a nota FORA DE ORDEM tambem
    e arquivada inteira). Regras em `ler_notas`."""
    notas = lista_de_notas(obj)
    if notas is None:
        return [], [{"indice": None, "doc": None,
                     "motivo": "JSON de notas sem a lista `notas`"}], []
    validos = {}
    for c in cards or []:
        if c.get("card_id") is not None:
            validos[int(c["card_id"])] = c
    agora = agora or db.agora()
    por_card, rejeitadas, avisos = {}, [], []
    for i, n in enumerate(notas):
        registro, motivo = notas_player.validar_nota(n, validos, agora, fuso)
        if registro is None:
            rejeitadas.append({"indice": i, "doc": n, "motivo": motivo})
            continue
        registro["doc"] = n
        cid = registro["card_id"]
        primeira = por_card.get(cid)
        if primeira is not None:
            if registro["quando"] < primeira["quando"]:
                por_card[cid], registro = registro, primeira
            avisos.append("card_id %d repetido -- conta a nota de menor ts (%s); a de %s "
                          "fica fora (relearning nao regrava)"
                          % (cid, por_card[cid]["quando"], registro["quando"]))
            continue
        por_card[cid] = registro
    return list(por_card.values()), rejeitadas, avisos


def ler_notas(obj, cards, agora=None, fuso=None):
    """Normaliza o JSON de notas vindo da pagina (input NAO confiavel).

    Devolve `(registros, rejeitadas, avisos)`; `registros` = [{card_id, rating,
    defeito, motivo, selection_reason, quando, doc}], `quando` = o relogio da revisao
    (`notas_player.relogio`). QUARENTENA (s193): cada doc estranho -- card fora do
    lote, rating fora de 1..4, defeito sem motivo, sem rating e sem defeito, ts
    ausente/ilegivel/sem fuso/no futuro -- sai em `rejeitadas` com o motivo (texto;
    o detalhe com o doc cru e o `triar_notas`), e os validos seguem. card_id repetido
    conta UMA vez -- a nota de MENOR ts, a 1a de fato -- com AVISO (o relearning da
    pagina nunca gera segunda nota gravavel)."""
    registros, rejeitadas, avisos = triar_notas(obj, cards, agora, fuso)
    textos = [r["motivo"] if r["indice"] is None else "nota #%d: %s" % (r["indice"], r["motivo"])
              for r in rejeitadas]
    return registros, textos, avisos


def arquivar_quarentena(caminho, sessao, itens, agora=None):
    """Acrescenta `itens` ({"tipo", "motivo", "doc"}) ao arquivo de quarentena da sessao.

    Idempotente: o mesmo (tipo, doc) nao entra duas vezes -- reler e regravar a sessao nao
    duplica. Devolve (novos, total). Grava so no repo (JSON); nunca no banco."""
    caminho = Path(caminho)
    atual = {"sessao": sessao, "itens": []}
    if caminho.is_file():
        atual = json.loads(caminho.read_text(encoding="utf-8"))
    chave = lambda it: (it["tipo"], json.dumps(it["doc"], sort_keys=True, ensure_ascii=False))
    vistos = {chave(it) for it in atual.get("itens", [])}
    carimbo = (agora or db.agora()).strftime("%Y-%m-%d %H:%M:%S")
    novos = 0
    for it in itens:
        if chave(it) in vistos:
            continue
        vistos.add(chave(it))
        atual.setdefault("itens", []).append(dict(it, arquivado_em=carimbo))
        novos += 1
    if novos:
        atual["_doc"] = ("Quarentena do fsrs_queue --record-lote (s193): doc rejeitado ou nota "
                         "FORA DE ORDEM, copiado inteiro com o motivo ANTES de qualquer poda do "
                         "db da pagina. Recuperacao e manual.")
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(atual, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
    return novos, len(atual.get("itens", []))


def aviso_hub(marcador, agora, janela_h=JANELA_HUB_H):
    """O WARN da fila do chat (s193, decisao 5 do `/ai-eng`), PURO: None se o hub foi
    gravado ha menos de `janela_h` horas; senao o texto. `marcador` = o dict de
    `ultima_gravacao_hub.json` ou None."""
    from datetime import timedelta
    try:
        quando = datetime.fromisoformat(str((marcador or {}).get("gravado_em")))
    except ValueError:
        quando = None
    if quando is not None and agora - quando <= timedelta(hours=janela_h):
        return None
    ultima = "nunca" if quando is None else quando.strftime("%d/%m %H:%M")
    return ("[WARN] HUB: ultima gravacao do hub = %s (janela %dh). O /revisar no chat ABRE "
            "gravando as notas pendentes do hub -- ArtifactData list da colecao viva (linha 3 "
            "do HANDOFF) -> --record-lote dry-run -> --apply --expect N (N pode ser 0); senao "
            "a nota do celular sai FORA DE ORDEM (revisar.md)." % (ultima, janela_h))


def _avisar_hub(caminho=None):
    """Le o marcador (ausente/ilegivel = nunca) e imprime o aviso em STDERR -- o stdout da
    fila e JSON por contrato."""
    try:
        marcador = json.loads(Path(caminho or MARCADOR_HUB).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        marcador = None
    texto = aviso_hub(marcador, db.agora())
    if texto:
        print(texto, file=sys.stderr)


def _contar_revlog():
    """COUNT do fsrs_revlog pela conexao canonica (leitura; nao abre sqlite3 proprio)."""
    conn = db.get_connection()
    try:
        return int(conn.execute("SELECT COUNT(*) FROM fsrs_revlog").fetchone()[0])
    finally:
        conn.close()


def aplicar_notas(registros, apply=False, expect=None, out=print,
                  record_fn=None, reforja_fn=None, count_fn=None, gravado_fn=None,
                  rejeitadas=(), quarentena=None, marcador=None, sessao=None):
    """Grava o lote de notas. Dry-run por default (mesmo rito do cards_prune).

    Cada nota com rating e classificada contra o revlog do card
    (`notas_player.situacao`, s193): JA GRAVADA sai da conta; FORA DE ORDEM e
    reportada e NAO grava; NOVA grava no relogio da revisao (`quando`), em ordem
    crescente de ts -- o N do `--expect` conta so as NOVAS. `--apply` exige
    `--expect` igual a esse N (COUNT-ASSERT pre) e confere que `fsrs_revlog`
    cresceu EXATAMENTE N (COUNT-ASSERT pos). Os `defeito` viram marca de reforja
    (`origem='player'`), que nao conta como revisao -- uma vez so por nota.
    `quarentena` (path): no `--apply`, as `rejeitadas` ({"indice", "doc", "motivo"}, de
    `triar_notas`) e as FORA DE ORDEM sao arquivadas inteiras ali ANTES de gravar.
    `marcador` (path): com o COUNT-ASSERT batido, registra a gravacao do hub (a fila do
    chat avisa quando ela esta velha). Retorna (exit_code, N)."""
    record_fn = record_fn or db.record_review
    reforja_fn = reforja_fn or db.marcar_reforja
    count_fn = count_fn or _contar_revlog
    gravado_fn = gravado_fn or db.estado_gravacao_player
    sem_relogio = [r for r in registros if r.get("quando") is None]
    registros = [r for r in registros if r.get("quando") is not None]
    gravado = gravado_fn([r["card_id"] for r in registros])
    vazio = {"revisoes": [], "marca_player": None}
    novas, ja_gravadas, fora_de_ordem = [], [], []
    for r in (r for r in registros if r["rating"] is not None):
        g = gravado.get(r["card_id"], vazio)
        s = notas_player.situacao(r["quando"], g["revisoes"])
        if s == notas_player.JA_GRAVADA:
            ja_gravadas.append(r)
        elif s == notas_player.FORA_DE_ORDEM:
            fora_de_ordem.append((r, notas_player.ultima_revisao(g["revisoes"])))
        else:
            novas.append(r)
    novas.sort(key=lambda r: (r["quando"], r["card_id"]))
    defeitos, ja_marcados = [], []
    for r in (r for r in registros if r["defeito"]):
        marca = gravado.get(r["card_id"], vazio)["marca_player"]
        (ja_marcados if notas_player.defeito_ja_marcado(r["quando"], marca)
         else defeitos).append(r)
    n = len(novas)
    out("[record-lote] novas=%d ja_gravadas=%d fora_de_ordem=%d defeito(s)=%d "
        "(ja marcados %d)" % (n, len(ja_gravadas), len(fora_de_ordem), len(defeitos),
                              len(ja_marcados)))
    for r in novas:
        out("  %d -> %d (%s) @ %s" % (r["card_id"], r["rating"],
                                      r["selection_reason"] or "auto", r["quando"]))
    if ja_gravadas:
        out("  JA GRAVADAS (fora do N): %s"
            % ", ".join(str(r["card_id"]) for r in ja_gravadas))
    for r, ultima in fora_de_ordem:
        out("  FORA DE ORDEM: %d -> %d, nota de %s e o revlog ja tem revisao de %s -- "
            "NAO gravada (o estado FSRS so anda para a frente)"
            % (r["card_id"], r["rating"], r["quando"], ultima))
    for r in sem_relogio:
        out("  SEM RELOGIO: %d -- registro sem `quando` (nao veio do ler_notas); NAO gravado"
            % r["card_id"])
    for r in defeitos:
        out("  %d -> DEFEITO: %s" % (r["card_id"], r["motivo"]))
    if ja_marcados:
        out("  DEFEITO JA MARCADO (sem 2a marca): %s"
            % ", ".join(str(r["card_id"]) for r in ja_marcados))
    arquivar = ([{"tipo": "rejeitada", "motivo": r["motivo"], "doc": r["doc"]}
                 for r in rejeitadas if r.get("indice") is not None]
                + [{"tipo": "fora_de_ordem", "doc": r.get("doc"),
                    "motivo": "nota de %s; o revlog ja tem revisao de %s" % (r["quando"], ultima)}
                   for r, ultima in fora_de_ordem])
    if arquivar and quarentena is not None:
        out("  QUARENTENA: %d doc(s) %s em %s (antes de qualquer poda)"
            % (len(arquivar), "arquivados" if apply else "a arquivar no --apply", quarentena))
    if not apply:
        out("  DRY-RUN: nada gravado. Para aplicar: --apply --expect %d" % n)
        return 0, n
    if expect is None or expect != n:
        out("  RECUSADO: --expect %s != N medido %d. Nada gravado." % (expect, n))
        return 2, n
    if arquivar and quarentena is not None:
        novos, total = arquivar_quarentena(quarentena, sessao, arquivar)
        out("  quarentena: +%d novo(s), %d no arquivo -- commitar ANTES de podar o db"
            % (novos, total))
    antes = count_fn()
    gravados = 0
    for r in novas:
        try:
            record_fn(r["card_id"], r["rating"], selection_reason=r["selection_reason"],
                      quando=r["quando"])
            gravados += 1
        except (db.ConcurrentReviewError, ValueError) as e:
            # corrida ou recusa do writer (futuro / nao posterior a ultima revisao):
            # o COUNT-ASSERT pos acusa a diferenca e o CLI sai 2
            out("  [WARN] card %d NAO gravado: %s" % (r["card_id"], e))
    marcas = 0
    for r in defeitos:
        reforja_fn(r["card_id"], r["motivo"], origem="player")
        marcas += 1
    depois = count_fn()
    out("  gravados=%d marcas_reforja=%d fsrs_revlog %d -> %d" % (gravados, marcas, antes, depois))
    if depois - antes != n:
        out("  COUNT-ASSERT pos FALHOU: fsrs_revlog cresceu %d, esperado %d"
            % (depois - antes, n))
        return 2, n
    out("  OK: %d revisao(oes) gravada(s); COUNT-ASSERT pos batido." % n)
    if marcador is not None:
        marca = {"sessao": sessao, "gravado_em": db.agora().isoformat(timespec="seconds"),
                 "novas": n, "arquivadas": len(arquivar)}
        Path(marcador).parent.mkdir(parents=True, exist_ok=True)
        Path(marcador).write_text(json.dumps(marca, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0, n


def main():
    parser = argparse.ArgumentParser(
        description="Fila de revisão FSRS em JSON para revisão conversacional."
    )
    acao = parser.add_mutually_exclusive_group(required=True)
    acao.add_argument("--next", action="store_true",
                      help="Imprime o próximo card vencido (objeto JSON)")
    acao.add_argument("--list", action="store_true",
                      help="Imprime o lote da fila (array JSON)")
    acao.add_argument("--record", type=int, metavar="CARD_ID",
                      help="Grava a avaliação de um card (exige --rating)")
    acao.add_argument("--card", type=int, metavar="CARD_ID",
                      help="Serve UM card por id, com as frentes e o verso. READ-ONLY: "
                           "nao toca a fila nem o FSRS, e serve card fora da fila "
                           "(inclusive APOSENTADO, com ativo=false). E o leitor que o "
                           "re-drill inter-sessao exige -- F99.")
    acao.add_argument("--preview", type=int, metavar="CARD_ID",
                      help="P3: consequencia dos 4 ratings p/ um card (JSON), sem gravar nada")
    acao.add_argument("--export-player", dest="export_player", action="store_true",
                      help="Exporta o lote do dia p/ o player (JSON com sessao, "
                           "gerado_em, cards[]). Mesma ordem/buckets do --list; "
                           "sem --limit, corta no teto do dia")
    acao.add_argument("--build-player", dest="build_player", action="store_true",
                      help="Injeta o lote (--lote) em core/templates/player.html "
                           "e grava a pagina em --out")
    acao.add_argument("--record-lote", dest="record_lote", metavar="NOTAS.json",
                      help="Grava o lote de notas do player por record_review. "
                           "Dry-run por default; exige --lote (o export) p/ validar")
    acao.add_argument("--pre-bloco", dest="pre_bloco", metavar="TEMA",
                      help="Mini-drill anti-reincidência (F23): lista SÓ os cards de erro "
                           "FRESCOS (state 0, janela --janela-horas) do tema-alvo, antes de "
                           "um bloco de questões. Rating segue o --record normal")
    parser.add_argument("--rating", type=int, choices=[1, 2, 3, 4],
                        help="Avaliação 1=Novamente 2=Difícil 3=Bom 4=Fácil (com --record)")
    parser.add_argument("--reason", default=None,
                        choices=["vencido", "fresh_error", "agendado", "novo", "pre_bloco", "auto"],
                        help="P3: por que o card foi servido — propague o selection_reason "
                             "que veio no --next/--list; persiste no revlog. F76: o --record "
                             "recomputa o bucket real e grava fsrs_revlog.reason_servido; "
                             "divergencia vira [WARN] em stderr (nao bloqueia). "
                             "`auto` = gravar o recomputado")
    parser.add_argument("--area", help="Filtro de área (match exato)")
    parser.add_argument("--tema", help="Filtro de tema (LIKE)")
    parser.add_argument("--limit", type=int, help="Máximo de cards na fila (--list)")
    parser.add_argument("--prevalencia", action="store_true",
                        help="Reordena os cards NOVOS por prevalencia ENAMED "
                             "(core/cronograma/prevalencia_enamed.json: alta -> media -> "
                             "baixa -> sem sinal; desempate FIFO). Opt-in; so muda a "
                             "ordem de introducao, nunca o FSRS (s165)")
    parser.add_argument("--new-limit", type=int, default=10, dest="new_limit",
                        help="Máximo de cards novos (state 0). Default: 10")
    parser.add_argument("--cluster", action="store_true",
                        help="Agrupa por (area, tema) dentro de cada bucket, preservando "
                             "a prioridade atrasados -> hoje -> novos (F3). Opt-in: sem a "
                             "flag, a ordem é a atual")
    parser.add_argument("--janela-horas", type=int, default=48, dest="janela_horas",
                        help="Janela de frescor do --pre-bloco em horas (default 48; "
                             "norma: core/contracts/orquestracao-contract.md)")
    parser.add_argument("--out", help="Arquivo de saida do --export-player "
                                      "(default tmp/player_<sessao>.json) ou do "
                                      "--build-player (default artifacts/player-<sessao>.html)")
    parser.add_argument("--lote", help="Caminho do JSON exportado pelo --export-player "
                                       "(exigido por --build-player e --record-lote)")
    parser.add_argument("--sessao", help="Id da sessao do player (default: data de hoje). "
                                         "Vira a colecao sessoes/<sessao>/notas na pagina")
    parser.add_argument("--apply", action="store_true",
                        help="--record-lote: grava de verdade (default: dry-run)")
    parser.add_argument("--expect", type=int,
                        help="--record-lote: COUNT-ASSERT, N esperado de revisoes; "
                             "obrigatorio com --apply e recusado se != N medido")
    args = parser.parse_args()

    if args.pre_bloco:
        frescos = db.get_fresh_error_cards(tema=args.pre_bloco,
                                           janela_horas=args.janela_horas)
        if not frescos:
            _emit({"empty": True, "pre_bloco": args.pre_bloco,
                   "msg": "0 cards frescos p/ '%s' na janela de %dh"
                          % (args.pre_bloco, args.janela_horas)})
            return
        out = []
        for card in frescos:
            card = dict(card)
            card["bucket"] = "pre-bloco"
            out.append(card)
        _emit(out)
        return

    if args.export_player:
        _avisar_hub()           # trocar o lote sem gravar a aba Cards perde a sessao das notas
        ordered = _ordered_queue(area=args.area, tema=args.tema, limit=None,
                                 new_limit=args.new_limit,
                                 prevalencia=args.prevalencia, cluster=args.cluster)
        limite = args.limit if args.limit is not None else teto_do_dia(ordered)
        lote = montar_lote(ordered, limit=limite, sessao=args.sessao)
        destino = Path(args.out) if args.out else Path("tmp") / ("player_%s.json" % lote["sessao"])
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(lote, ensure_ascii=False, indent=1, default=str),
                           encoding="utf-8")
        _emit({"export": str(destino), "sessao": lote["sessao"],
               "total": lote["total"], "teto": limite, "pool": len(ordered)})
        return

    if args.build_player:
        if not args.lote:
            parser.error("--build-player exige --lote ARQ.json")
        lote = json.loads(Path(args.lote).read_text(encoding="utf-8"))
        html = injetar_lote(TEMPLATE_PLAYER.read_text(encoding="utf-8"), lote)
        destino = (Path(args.out) if args.out
                   else Path("artifacts") / ("player-%s.html" % lote.get("sessao", "sessao")))
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(html, encoding="utf-8")
        _emit({"build": str(destino), "sessao": lote.get("sessao"),
               "cards": len(lote.get("cards", []))})
        return

    if args.record_lote:
        notas_obj = json.loads(Path(args.record_lote).read_text(encoding="utf-8"))
        caminho = args.lote or (notas_obj.get("lote") if isinstance(notas_obj, dict) else None)
        if not caminho:
            print("[record-lote] RECUSADO: informe --lote ARQ.json (o export que gerou "
                  "a pagina) -- e contra ele que o card_id e validado", file=sys.stderr)
            sys.exit(2)
        lote = json.loads(Path(caminho).read_text(encoding="utf-8"))
        if lista_de_notas(notas_obj) is None:
            print("[record-lote] RECUSADO: JSON de notas sem a lista `notas`. Nada gravado.",
                  file=sys.stderr)
            sys.exit(2)
        registros, rejeitadas, avisos = triar_notas(notas_obj, lote.get("cards", []))
        for a in avisos:
            print("[WARN] " + a, file=sys.stderr)
        # Quarentena (s193): doc estranho e reportado e fica de fora; os validos
        # seguem. Nao sai 2 -- um doc torto nao trava as notas boas do operador. No
        # --apply ele e ARQUIVADO inteiro em history/quarentena/<sessao>.json.
        for r in rejeitadas:
            print("[REJEITADA] nota #%s: %s" % (r["indice"], r["motivo"]), file=sys.stderr)
        if rejeitadas:
            print("[record-lote] rejeitadas=%d (nada delas e gravado; motivo por doc em "
                  "stderr)" % len(rejeitadas))
        sessao = lote.get("sessao") or "sessao"
        code, _ = aplicar_notas(registros, apply=args.apply, expect=args.expect,
                                rejeitadas=rejeitadas, quarentena=arquivo_quarentena(sessao),
                                marcador=MARCADOR_HUB, sessao=sessao)
        if code:
            sys.exit(code)
        return

    if args.record is not None:
        if args.rating is None:
            parser.error("--record exige --rating <1-4>")
        try:
            metrics = db.record_review(args.record, args.rating,
                                       selection_reason=args.reason)
        except db.ConcurrentReviewError as e:
            # part-2: fail-safe — reporta e NAO regrava (Invariante C).
            _emit({"recorded": False, "card_id": args.record,
                   "error": f"rating nao gravado (estado mudou desde a leitura): {e}"})
            sys.exit(1)
        # F76 (s174): proveniencia recomputada no ato -- divergencia AVISA (stderr,
        # nao bloqueia) e fica GRAVADA em fsrs_revlog.reason_servido.
        if metrics.get("reason_divergente"):
            print(f"[WARN] reason divergente: servido={metrics.get('reason_servido')}, "
                  f"recebido={metrics.get('selection_reason')} "
                  f"(gravado em fsrs_revlog.reason_servido; revisar.md §4)", file=sys.stderr)
        _emit({
            "recorded": True,
            "card_id": args.record,
            "rating": args.rating,
            "next_due": metrics.get("due"),
            "state": metrics.get("state"),
            "selection_reason": metrics.get("selection_reason"),
            "reason_servido": metrics.get("reason_servido"),
            "reason_divergente": bool(metrics.get("reason_divergente")),
        })
        return

    if args.card is not None:
        card = db.card_por_id(args.card)
        if card is None:
            _emit({"card_id": args.card, "found": False,
                   "erro": f"card #{args.card} nao existe em flashcards"})
            return
        _emit({**card, "found": True})
        return

    if args.preview is not None:
        _emit({"card_id": args.preview, "preview": db.preview_ratings(args.preview)})
        return

    # s193 (decisao 5 do /ai-eng): a fila do chat nunca passa na frente do celular.
    _avisar_hub()
    ordered = _ordered_queue(area=args.area, tema=args.tema,
                             limit=args.limit, new_limit=args.new_limit, prevalencia=args.prevalencia,
                             cluster=args.cluster)

    if args.next:
        if not ordered:
            _emit({"empty": True})
            return
        card = ordered[0]
        # P3 part-3: preview embutido no momento do rating (so no --next; no
        # --list seria 4xN evaluates sem uso). Falha de preview nunca derruba
        # a fila — o card sai sem o campo, com o erro anotado.
        try:
            card["preview"] = db.preview_ratings(card["card_id"])
        except Exception as e:
            card["preview_error"] = str(e)
        _emit(card)
    else:  # --list
        _emit(ordered)


if __name__ == "__main__":
    main()
