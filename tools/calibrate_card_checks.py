"""calibrate_card_checks.py — calibração dos detectores contra o incidente real.

Roda os predicados de `card_checks` sobre os 68 cards do incidente de
2026-08-13 (`questao_id BETWEEN 781 AND 814`, todos aposentados nq=2) e mede
o recall: quantos dos 68 os detectores pegam HOJE. Meta do ciclo: >= 66/68
(spec part-5, DoD 6). Também mede falso-positivo aparente nos qualitativos
ATIVOS (erro-level apenas), para vigiar precisão.

Read-only (`mode=ro`); execução MANUAL (o banco fica fora do git — isto não é
teste de CI). Imprime IDs e contagens, NUNCA conteúdo de card. Resultado
persistido no ledger-of-self (`calibracao|card_checks`).

Uso: python tools/calibrate_card_checks.py
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import card_checks  # noqa: E402

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ipub.db")
META = 66  # de 68


def _cards(conn, where, params=()):
    return conn.execute(f"""
        SELECT f.id, f.frente_contexto, f.frente_pergunta, f.verso_resposta,
               f.verso_regra_mestre, f.verso_armadilha, q.titulo, t.tema
        FROM flashcards f
        LEFT JOIN questoes_erros q ON q.id = f.questao_id
        LEFT JOIN taxonomia_cronograma t ON t.id = f.tema_id
        WHERE {where}
    """, params).fetchall()


def _detecta(row):
    """Retorna lista de tags ERRO-level disparadas para a linha."""
    (cid, fc, fp, vr, vrm, va, titulo, tema) = row
    card = {"frente_contexto": fc, "frente_pergunta": fp, "verso_resposta": vr,
            "verso_regra_mestre": vrm, "verso_armadilha": va}
    ctx = {"titulo": titulo, "tema": tema}
    tags = []
    t = card_checks.checar_pergunta_template(card, ctx)
    if t:
        tags.append(t)
    e = card_checks.checar_resposta_embutida(card, ctx)
    if e:
        tags.append(e.split(" ")[0])
    return tags


def main():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        incidente = _cards(conn, "f.questao_id BETWEEN 781 AND 814")
        detectados, por_tag, perdidos = 0, {}, []
        for row in incidente:
            tags = _detecta(row)
            if tags:
                detectados += 1
                for t in tags:
                    por_tag[t] = por_tag.get(t, 0) + 1
            else:
                perdidos.append(row[0])

        # Falso-positivo aparente: erro-level nos qualitativos ATIVOS
        # (definicao canonica db.ATIVO_WHERE, inline por ser conexao ro).
        ativos_qual = _cards(conn, "COALESCE(f.needs_qualitative,0) < 2 "
                                   "AND f.quality_source = 'qualitative'")
        fp_ids = [r[0] for r in ativos_qual if _detecta(r)]
    finally:
        conn.close()

    total = len(incidente)
    print("CALIBRACAO card_checks x incidente 2026-08-13")
    print(f"  recall: {detectados}/{total} (meta >= {META}/68)")
    for t in sorted(por_tag):
        print(f"    {t}: {por_tag[t]}")
    if perdidos:
        print(f"  NAO detectados ({len(perdidos)}): ids {perdidos}")
    linha_fp = (f"  falso-positivo aparente (erro-level): {len(fp_ids)} / "
                f"{len(ativos_qual)} qualitativos ativos")
    if fp_ids:
        linha_fp += f" — ids {fp_ids[:12]}"
    print(linha_fp)
    veredito = "PASS" if detectados >= META else "FAIL"
    print(f"  veredito: {veredito}")

    try:
        import ledger_self
        ledger_self.record("calibracao_card_checks", [{
            "alvo": "incidente-781-814",
            "payload": {"recall": f"{detectados}/{total}", "meta": f">={META}",
                        "por_tag": por_tag, "nao_detectados": perdidos,
                        "falso_pos_aparente": len(fp_ids), "veredito": veredito},
        }])
    except Exception as e:
        print(f"  [WARN] ledger indisponivel ({e}); resultado so no stdout.")
    return 0 if veredito == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
