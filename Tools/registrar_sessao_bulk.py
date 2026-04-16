"""
registrar_sessao_bulk.py
========================
Registra o volume total de questões feitas numa sessão de estudo —
separado do pipeline de erros.

Uso (pelo agente ou manualmente):
    python tools/registrar_sessao_bulk.py \\
        --sessao 067 \\
        --area Cirurgia \\
        --feitas 30 \\
        --acertos 24 \\
        [--obs "Bloco ATLS"]

O agente deve chamar este script assim que o usuário informar:
    "Fiz X questões, acertei Y, abaixo vão Z erros."
"""
import sqlite3
import argparse
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

AREAS_VALIDAS = [
    "Pediatria", "Preventiva", "Cirurgia", "Infecto", "Obstetrícia",
    "Ginecologia", "Gastro", "Endocrino", "Cardiologia", "Psiquiatria",
    "Neurologia", "Nefrologia", "Hemato", "Pneumo", "Dermato",
    "Reumato", "Hepato", "Otorrino", "Ortopedia", "Oftalmo",
]

def registrar(sessao_num: int, area: str, feitas: int, acertos: int,
              data: str | None = None, obs: str = ""):
    if acertos > feitas:
        raise ValueError(f"Acertos ({acertos}) não pode ser maior que feitas ({feitas}).")

    data_sessao = data or date.today().isoformat()

    conn = sqlite3.connect(DB_PATH)
    try:
        # 1. Garante que a tabela existe
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessoes_bulk (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                sessao_num          INTEGER,
                area                TEXT NOT NULL,
                questoes_feitas     INTEGER DEFAULT 0,
                questoes_acertadas  INTEGER DEFAULT 0,
                data_sessao         DATE DEFAULT CURRENT_DATE,
                observacoes         TEXT
            )
        """)

        # 2. Guarda contra insercao dupla (idempotencia)
        existing = conn.execute(
            "SELECT id, questoes_feitas FROM sessoes_bulk WHERE sessao_num=? AND area=?",
            (sessao_num, area)
        ).fetchone()
        if existing:
            print("[AVISO] Sessao %03d/%s ja existe (id=%d, feitas=%d). Nada alterado." % (
                sessao_num, area, existing[0], existing[1]))
            conn.close()
            return False

        # 3. Insere o registro da sessao
        conn.execute("""
            INSERT INTO sessoes_bulk
                (sessao_num, area, questoes_feitas, questoes_acertadas, data_sessao, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sessao_num, area, feitas, acertos, data_sessao, obs))

        # 3. Atualiza acumulado em taxonomia_cronograma (para o "Foco Crítico")
        row = conn.execute(
            "SELECT id FROM taxonomia_cronograma WHERE area = ? LIMIT 1", (area,)
        ).fetchone()

        pct_feitas  = feitas
        pct_acertos = acertos

        if row:
            conn.execute("""
                UPDATE taxonomia_cronograma
                SET questoes_realizadas = questoes_realizadas + ?,
                    questoes_acertadas  = questoes_acertadas  + ?,
                    percentual_acertos  = CASE
                        WHEN (questoes_realizadas + ?) > 0
                        THEN CAST(questoes_acertadas + ? AS REAL) /
                             (questoes_realizadas + ?)  * 100
                        ELSE 0
                    END,
                    ultima_revisao = ?
                WHERE area = ?
            """, (pct_feitas, pct_acertos,
                  pct_feitas, pct_acertos, pct_feitas,
                  data_sessao, area))
        else:
            pct = round(acertos / feitas * 100, 2) if feitas else 0
            conn.execute("""
                INSERT INTO taxonomia_cronograma
                    (area, tema, questoes_realizadas, questoes_acertadas,
                     percentual_acertos, ultima_revisao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (area, f"[bulk] {area}", feitas, acertos, pct, data_sessao))

        conn.commit()

        erros = feitas - acertos
        pct   = acertos / feitas * 100 if feitas else 0
        print("[OK] Sessao %03d | %s" % (sessao_num, area))
        print("     Questoes: %d | Acertos: %d | Erros: %d | %.1f%%" % (feitas, acertos, erros, pct))
        return True

    except Exception as e:
        print("[ERRO] %s" % str(e))
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Registra bulk de questões de uma sessão de estudo."
    )
    parser.add_argument("--sessao",   required=True, type=int,
                        help="Número da sessão (ex: 67)")
    parser.add_argument("--area",     required=True,
                        help=f"Área clínica. Válidas: {', '.join(AREAS_VALIDAS)}")
    parser.add_argument("--feitas",   required=True, type=int,
                        help="Total de questões feitas")
    parser.add_argument("--acertos",  required=True, type=int,
                        help="Total de questões acertadas")
    parser.add_argument("--data",     default=None,
                        help="Data da sessão (YYYY-MM-DD). Padrão: hoje")
    parser.add_argument("--obs",      default="",
                        help="Observação opcional (ex: 'Bloco ATLS')")

    args = parser.parse_args()
    registrar(
        sessao_num=args.sessao,
        area=args.area,
        feitas=args.feitas,
        acertos=args.acertos,
        data=args.data,
        obs=args.obs,
    )
