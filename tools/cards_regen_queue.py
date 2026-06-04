"""cards_regen_queue.py — fila de regeneração de flashcards em JSON.

CLI **read-only** que emite, em JSON, os erros cujos cards precisam ser
regenerados (critério: `quality_source = 'heuristic'` e ainda não aposentado,
`needs_qualitative != 2`), junto com:
  - o substrato metacognitivo de `questoes_erros` (tipo_erro, habilidades_sequenciais,
    o_que_faltou, alternativa_correta/marcada, armadilha_prova, enunciado);
  - os cards atuais (card_id + campos v5) para o agente reescrever.

O agente lê esta fila, cunha cards atômicos pela régua
(`.claude/commands/estilo-flashcard.md`) e persiste via:
  - `app.utils.db.update_flashcard_fields(card_id, fields)` para reescrever um
    card existente preservando o estado FSRS; e/ou
  - `tools/insert_questao.py --cards-file` para adicionar cards novos ao erro.

Camada fina sobre `app.utils.db` — não abre `sqlite3` próprio.

Uso:
    python tools/cards_regen_queue.py [--area "GO"] [--limit N] [--questao-id ID]

Assinatura canônica documentada em `.claude/commands/estilo-flashcard.md`.
"""
import argparse
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import db  # noqa: E402


def fetch_regen_queue(area=None, limit=None, questao_id=None):
    """Retorna lista de erros (+ cards atuais) a regenerar.

    Critério: erros com ao menos um card heurístico ainda ativo
    (`quality_source = 'heuristic'` e `needs_qualitative != 2`). Pós-bankruptcy
    da sessão 075, o antigo sinal `needs_qualitative = 1` ficou órfão (os 70
    cards flagueados viraram `= 2`), deixando 87 heurísticos `nq = 0` invisíveis;
    este critério os recupera. Filtros opcionais: area, questao_id, limit.
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    where = ["f.quality_source = 'heuristic'", "f.needs_qualitative != 2"]
    params = []
    if questao_id is not None:
        where.append("q.id = ?")
        params.append(questao_id)
    if area:
        where.append("t.area = ?")
        params.append(area)
    clause = " AND ".join(where)

    cursor.execute(f"""
        SELECT DISTINCT q.id
        FROM questoes_erros q
        JOIN flashcards f ON f.questao_id = q.id
        LEFT JOIN taxonomia_cronograma t ON q.tema_id = t.id
        WHERE {clause}
        ORDER BY q.id ASC
    """, params)
    qids = [r[0] for r in cursor.fetchall()]
    if limit is not None:
        qids = qids[:limit]

    fila = []
    for qid in qids:
        cursor.execute("""
            SELECT q.id, t.area, t.tema, q.titulo, q.tipo_erro,
                   q.habilidades_sequenciais, q.o_que_faltou,
                   q.alternativa_correta, q.alternativa_marcada,
                   q.armadilha_prova, q.explicacao_correta, q.enunciado
            FROM questoes_erros q
            LEFT JOIN taxonomia_cronograma t ON q.tema_id = t.id
            WHERE q.id = ?
        """, (qid,))
        cols = [d[0] for d in cursor.description]
        erro = dict(zip(cols, cursor.fetchone()))

        cursor.execute("""
            SELECT id AS card_id, tipo, frente_contexto, frente_pergunta,
                   verso_resposta, verso_regra_mestre, verso_armadilha,
                   quality_source, needs_qualitative
            FROM flashcards WHERE questao_id = ?
            ORDER BY id ASC
        """, (qid,))
        ccols = [d[0] for d in cursor.description]
        erro["cards_atuais"] = [dict(zip(ccols, row)) for row in cursor.fetchall()]
        fila.append(erro)

    conn.close()
    return fila


def main():
    parser = argparse.ArgumentParser(
        description="Fila de regeneração de flashcards (read-only) em JSON."
    )
    parser.add_argument("--area", help="Filtro de área (match exato)")
    parser.add_argument("--limit", type=int, help="Máximo de erros retornados")
    parser.add_argument("--questao-id", type=int, dest="questao_id",
                        help="Regenerar apenas um erro específico")
    args = parser.parse_args()

    fila = fetch_regen_queue(area=args.area, limit=args.limit,
                             questao_id=args.questao_id)
    print(json.dumps(fila, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
