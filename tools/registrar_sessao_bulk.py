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
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

AREAS_VALIDAS = [
    "Pediatria", "Preventiva", "Cirurgia", "Infecto", "Obstetrícia",
    "Ginecologia", "Gastro", "Endocrino", "Cardiologia", "Psiquiatria",
    "Neurologia", "Nefrologia", "Hemato", "Pneumo", "Dermato",
    "Reumato", "Hepato", "Otorrino", "Ortopedia", "Oftalmo",
    "Simulado",  # slot dedicado a simulados: volume/desempenho AGREGADO (tendencia/predicao ENAMED);
                 # os erros individuais continuam vinculados aos temas clinicos reais (resumos/flashcards)
]

def registrar(sessao_num: int, area: str, feitas: int, acertos: int,
              data: str | None = None, obs: str = "",
              acumular: bool = False, semana: int | None = None):
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

        # 2. Guarda contra insercao dupla (idempotencia). Com --acumular (F22),
        # 2o bloco da mesma (sessao, area) SOMA na linha existente -- a taxonomia
        # abaixo recebe apenas o delta deste bloco (sem dupla contagem).
        existing = conn.execute(
            "SELECT id, questoes_feitas FROM sessoes_bulk WHERE sessao_num=? AND area=?",
            (sessao_num, area)
        ).fetchone()
        acumulado = False
        if existing:
            if not acumular:
                print("[AVISO] Sessao %03d/%s ja existe (id=%d, feitas=%d). Nada alterado." % (
                    sessao_num, area, existing[0], existing[1]))
                conn.close()
                return False
            conn.execute("""
                UPDATE sessoes_bulk
                SET questoes_feitas    = questoes_feitas    + ?,
                    questoes_acertadas = questoes_acertadas + ?,
                    observacoes = CASE
                        WHEN observacoes IS NULL OR observacoes = '' THEN ?
                        ELSE observacoes || ' | ' || ?
                    END
                WHERE id = ?
            """, (feitas, acertos, obs, obs, existing[0]))
            acumulado = True
        else:
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

        # 4. Posicao SSOT no ato do registro (part-1): mesmo caminho/tabela do
        # tools/preparacao.py (standalone: SQL direto, upsert idempotente).
        if semana:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preparacao_estado (
                    chave         TEXT PRIMARY KEY,
                    valor         TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL,
                    fonte         TEXT
                )
            """)
            conn.execute("""
                INSERT INTO preparacao_estado (chave, valor, atualizado_em, fonte)
                VALUES ('semana_conteudo', ?, ?, 'registro-volume')
                ON CONFLICT(chave) DO UPDATE SET
                    valor = excluded.valor,
                    atualizado_em = excluded.atualizado_em,
                    fonte = excluded.fonte
            """, (str(semana), datetime.now().isoformat(timespec="seconds")))

        conn.commit()

        erros = feitas - acertos
        pct   = acertos / feitas * 100 if feitas else 0
        sufixo = " (acumulado: bloco somado a linha existente)" if acumulado else ""
        print("[OK] Sessao %03d | %s%s" % (sessao_num, area, sufixo))
        print("     Questoes: %d | Acertos: %d | Erros: %d | %.1f%%" % (feitas, acertos, erros, pct))
        if semana:
            print("     Posicao atualizada: semana de conteudo S%d [preparacao_estado]" % semana)
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
    parser.add_argument("--acumular", action="store_true",
                        help="Soma este bloco a um registro existente da mesma "
                             "(sessao, area) em vez de recusar (F22: 2o bloco do dia)")
    parser.add_argument("--semana",   default=None, type=int,
                        help="Atualiza a posicao SSOT (semana de conteudo) no ato do registro")

    args = parser.parse_args()
    registrar(
        sessao_num=args.sessao,
        area=args.area,
        feitas=args.feitas,
        acertos=args.acertos,
        data=args.data,
        obs=args.obs,
        acumular=args.acumular,
        semana=args.semana,
    )
