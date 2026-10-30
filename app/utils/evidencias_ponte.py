"""evidencias_ponte.py -- os writers de card do MedHub falando com o `evidence-bank` (s236, 30/10/2026).

Lei: ADR `ai-eng:artifacts/adr-banco-evidencias-clinicas-medhub-2026-10-30.md` v1.1 (Adendo 2 R2) +
`core/contracts/evidence-governance.md` v1.5 §7/§8. Ordem de aplicação:
`ai-eng:artifacts/2026-10-30-evidence-bank-aplicacao-medhub.md` passo 5.

Card novo nunca chega ao estudo sem fonte; muda só o lugar onde ele espera:
  - card com `evidencias: ["ev-..."]` ATIVAS no `evidencias.db` pareado -> ponte
    `card_evidencia(estado='ativa')` (caminho feliz);
  - senão -> 1 item na `fila` do banco por afirmação (`afirmacoes: [...]` do JSON; sem elas, a
    regra-mestre sem o colchete `[Fonte: ...]`; sem regra-mestre, "pergunta -> resposta") + ponte
    `estado='fila'` com o `fila_id`. O card entra EM QUARENTENA (`db.ativo_where` o tira do FSRS
    enquanto não houver ponte `ativa`) e NUNCA é recusado por falta de evidência. Recusa só por
    FORMA: o lote da fila que não valida no §1 da spec derruba o insert inteiro (nada gravado).

Sem `evidencias.db` pareado (`db.evidencias_path`) não há watermark nem quarentena: nada a fazer.
O pacote é importado do diretório irmão `../evidence-bank` (`EVIDENCE_BANK_DIR` sobrepõe); a
escrita no ipub passa pelo writer único `db.ponte_evidencia_gravar`, na conexão do chamador
(mesma transação do card). A fila (outro arquivo) comita antes do ipub: se o commit do ipub
falhar depois dela, sobra item de fila sem card -- limite declarado (README do pacote: não há
atomicidade entre os dois arquivos).
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

from app.utils import db

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVIDENCE_BANK_DIR = (os.environ.get("EVIDENCE_BANK_DIR")
                     or os.path.join(os.path.dirname(RAIZ), "evidence-bank"))

#: `tipo` do item quando o JSON não declara (a regra-mestre é, por construção, a conduta do card).
TIPO_PADRAO = "conduta"
_RE_COLCHETE_FONTE = re.compile(r"\s*\[Fonte:[^\]]*\]\s*$", re.I)


def carregar_pacote():
    """O módulo `evidence_bank`, ou RuntimeError dizendo onde ele foi procurado."""
    try:
        import evidence_bank
        return evidence_bank
    except ImportError:
        pass
    if not os.path.isdir(os.path.join(EVIDENCE_BANK_DIR, "evidence_bank")):
        raise RuntimeError(f"evidence-bank indisponivel em {EVIDENCE_BANK_DIR} "
                           f"(EVIDENCE_BANK_DIR sobrepoe)")
    if EVIDENCE_BANK_DIR not in sys.path:
        sys.path.append(EVIDENCE_BANK_DIR)   # no FIM: nunca sombreia modulo do medhub
    import evidence_bank
    return evidence_bank


def afirmacoes_do_card(card):
    """[(afirmacao, tipo)] de um card: `afirmacoes` (str ou {afirmacao, tipo}) ou a regra-mestre."""
    brutas = card.get("afirmacoes")
    if brutas:
        out = []
        for a in brutas:
            if isinstance(a, dict):
                out.append((str(a.get("afirmacao") or "").strip(), a.get("tipo") or TIPO_PADRAO))
            else:
                out.append((str(a or "").strip(), TIPO_PADRAO))
        return out
    regra = _RE_COLCHETE_FONTE.sub("", str(card.get("verso_regra_mestre") or "")).strip()
    if not regra:
        regra = (f"{str(card.get('frente_pergunta') or '').strip()} -> "
                 f"{str(card.get('verso_resposta') or '').strip()}")
    return [(regra, TIPO_PADRAO)]


def _ativas(banco, pedidas):
    if not pedidas:
        return set()
    marc = ",".join("?" * len(pedidas))
    return {r[0] for r in banco.conn.execute(
        f"SELECT id FROM evidencia WHERE status = 'ativa' AND id IN ({marc})", tuple(sorted(pedidas)))}


def aplicar(conn, pendentes, agente, db_path=None, dry_run=False):
    """Pontes + fila dos cards recém-inseridos (ainda sem commit no ipub).

    `pendentes` = [(card_id, card_dict, area, tema, tema_id)]; no `dry_run`, `card_id` pode ser 0
    e `conn` None (só valida a forma e conta). Devolve {banco, ativos, quarentena, fila, avisos}.
    Levanta ValueError (forma do lote da fila) ou RuntimeError (pacote ausente): o chamador desfaz
    o ipub e nada fica gravado."""
    res = {"banco": False, "ativos": 0, "quarentena": 0, "fila": 0, "avisos": []}
    caminho = db.evidencias_path(db_path)
    if not pendentes or not os.path.exists(caminho):
        return res
    res["banco"] = True
    eb = carregar_pacote()
    pedidas = {e for _, card, *_ in pendentes for e in (card.get("evidencias") or []) if isinstance(e, str)}
    with eb.open_db(caminho, readonly=True) as b:
        ativas = _ativas(b, pedidas)
    pontes_ativas, por_card, itens = [], [], []
    for card_id, card, area, tema, tema_id in pendentes:
        evs = list(dict.fromkeys(e for e in (card.get("evidencias") or []) if e in ativas))
        fora = sorted({e for e in (card.get("evidencias") or [])} - ativas)
        if fora:
            res["avisos"].append(f"card {card_id}: evidencia(s) sem status ativa ignorada(s): {fora}")
        if evs:
            res["ativos"] += 1
            pontes_ativas += [(card_id, e) for e in evs]
            continue
        res["quarentena"] += 1
        vistos = set()
        for afirmacao, tipo in afirmacoes_do_card(card):
            ev = eb.evidencia_id(area, afirmacao)
            if ev in vistos:
                continue
            vistos.add(ev)
            itens.append({"afirmacao": afirmacao, "tipo": tipo, "area": area, "tema": tema,
                          "tema_id": tema_id, "origem": f"card:{int(card_id)}"})
            por_card.append((card_id, ev))
    res["fila"] = len(itens)
    ids = {}
    if itens:
        payload = {"agente": agente,
                   "gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"),
                   "itens": itens}
        with eb.open_db(caminho) as b:
            _, _, erros = b.validar_lote(payload)
            if erros:
                raise ValueError("lote da fila do evidence-bank com forma invalida: "
                                 + json.dumps(erros, ensure_ascii=False)[:600])
            if not dry_run:
                antes = b.conn.execute("SELECT COALESCE(max(id), 0) FROM fila").fetchone()[0]
                b.fila_add(payload)
                for fid, origem, afirm, area_ in b.conn.execute(
                        "SELECT id, origem, afirmacao, area FROM fila WHERE id > ?", (antes,)):
                    ids[(origem, eb.evidencia_id(area_, afirm))] = fid
    if dry_run:
        return res
    for card_id, ev in pontes_ativas:
        db.ponte_evidencia_gravar(conn, "card", card_id, ev, "ativa")
    for card_id, ev in por_card:
        db.ponte_evidencia_gravar(conn, "card", card_id, ev, "fila",
                                  ids.get((f"card:{int(card_id)}", ev)))
    return res


def linha_resumo(res):
    """A linha do stdout dos writers ('' sem banco pareado)."""
    if not res.get("banco"):
        return ""
    return (f"[EVIDENCIA] {res['ativos']} card(s) com evidencia ativa; {res['quarentena']} em "
            f"QUARENTENA (fora do FSRS ate a decisao na fila); {res['fila']} item(ns) na fila do "
            f"evidence-bank.")
