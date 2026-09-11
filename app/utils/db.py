"""
MedHub DB access layer — única fonte de `import sqlite3` na camada `app/`.

Convenções: reads retornam `pandas.DataFrame`; writes usam cursor+commit
explícitos; sempre fechar via `conn.close()`; queries parametrizadas
(`params=(...)`) para evitar SQL injection. `DB_PATH` é resolvido relativo
à raiz do repo.

Callers acima: `app/engine/*.py`, CLIs em `tools/` (`fsrs_queue`, `day_plan`,
`cronograma`, ...). CLIs de escrita em `tools/` usam `sqlite3` diretamente por design
(scripts standalone) -- mas o RELOGIO e um so (abaixo).

## Zona canonica de tempo = LOCAL naive (F80, hotfix 2026-09-09, s174)

Todo carimbo gravado no `ipub.db` sai de `agora()`/`carimbo()` deste modulo: hora LOCAL
do sistema, sem tzinfo, formato `YYYY-MM-DD HH:MM:SS` (o mesmo shape do
`CURRENT_TIMESTAMP`, entao `date(col)`/`MAX(col)` continuam funcionando). E a zona que
o nucleo FSRS ja usa (`fsrs.py`: `due_local`/`last_review_local`), que a SSOT volumetrica
(`sessoes_bulk.data_sessao`) ja usa e que todo leitor de "dia" assume (`date.today()`).
Nenhum writer pode depender do `DEFAULT CURRENT_TIMESTAMP` do SQLite (que e UTC):
`tools/test_fuso_unico.py` varre os INSERTs e falha nomeando o arquivo.

🔴 HISTORICO: ate o commit-fronteira deste hotfix, `fsrs_revlog.review_time`,
`questoes_erros.data_registro` e `review_log.reviewed_at` foram gravados em UTC pelo
DEFAULT. Essas linhas NAO foram reescritas (SSOT; o revlog calibra o FSRS). Brasil nao
tem horario de verao desde 2019, logo o deslocamento historico e um shift constante de
-3h (`America/Sao_Paulo`); backfill = item separado, dry-run + COUNT-ASSERT (§10.7),
gatilho do operador. Ledger: `AUDITORIA_MEDHUB.md` F80.
"""

import sqlite3
import sys
import pandas as pd
import os
from datetime import datetime
from app.utils.fsrs import FSRS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

FORMATO_CARIMBO = "%Y-%m-%d %H:%M:%S"


def agora():
    """O relogio unico do `ipub.db` (F80): hora LOCAL naive. Monkeypatchavel nos
    testes (`db.agora = lambda: <instante>`) -- por isso os writers chamam pelo
    atributo do modulo, nunca `from db import agora`."""
    return datetime.now()


def carimbo():
    """`agora()` no formato de carimbo do banco (`YYYY-MM-DD HH:MM:SS`)."""
    return agora().strftime(FORMATO_CARIMBO)


def hoje():
    """Dia local corrente, derivado do MESMO relogio (`sessoes_bulk.data_sessao`)."""
    return agora().date()


# Definição canônica de "card ativo" (part-5, flashcards-integridade) — FONTE
# ÚNICA. Antes havia 3 definições divergentes em 5 arquivos (`!= 2`, `< 2` sem
# COALESCE, sem filtro). CLIs read-only que não importam este módulo replicam a
# expressão LITERALMENTE, com comentário apontando para cá.
ATIVO_WHERE = "COALESCE(needs_qualitative, 0) < 2"


def ativo_where(alias=""):
    """Expressão canônica de ativo, com alias opcional (ex.: ativo_where('f.'))."""
    return f"COALESCE({alias}needs_qualitative, 0) < 2"


def _ensure_views(conn):
    """VIEW canônica dos ativos. Idempotente; em fixture sem a tabela, a view
    fica pendente sem quebrar a conexão (SQLite só resolve nomes no SELECT)."""
    try:
        conn.execute("CREATE VIEW IF NOT EXISTS flashcards_ativos AS "
                     f"SELECT * FROM flashcards WHERE {ATIVO_WHERE}")
    except sqlite3.OperationalError:
        pass  # db mínimo de teste sem flashcards — view é opcional aí


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # part-1 (flashcards-integridade): as FKs sempre existiram no schema, mas o
    # SQLite so as impoe com o PRAGMA ligado — e ele e por-conexao.
    conn.execute("PRAGMA foreign_keys = ON")
    _ensure_views(conn)
    return conn


def contar_erros_cards():
    """Contadores da frente 'Erros & Cards' p/ o handoff-block (F53, descolar part-4):
    os números do HANDOFF/ESTADO viram DERIVADOS de verdade (eram digitados à mão sob o
    rótulo 'derivados'). Read-only."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        erros = cur.execute("SELECT COUNT(*) FROM questoes_erros").fetchone()[0]
        try:
            ativos_n = cur.execute("SELECT COUNT(*) FROM flashcards_ativos").fetchone()[0]
        except Exception:
            ativos_n = cur.execute(
                f"SELECT COUNT(*) FROM flashcards f WHERE {ativo_where('f.')}").fetchone()[0]
        nq = cur.execute("SELECT COUNT(*) FROM flashcards f JOIN fsrs_cards c "
                         "ON c.card_id = f.id WHERE f.needs_qualitative = 1 "
                         "AND c.state < 2").fetchone()[0]
        temas = cur.execute("SELECT COUNT(*) FROM taxonomia_cronograma").fetchone()[0]
        return {"erros": int(erros), "cards_ativos": int(ativos_n),
                "needs_qualitative": int(nq), "temas": int(temas)}
    finally:
        conn.close()


def ativos():
    """Cards ativos (definição canônica) como DataFrame — helper único p/ os
    consumidores que hoje reimplementam o filtro."""
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM flashcards_ativos", conn)
    finally:
        conn.close()


# --- Preparação (posição SSOT + estado de orquestração; PRD orquestracao-preparacao part-1) ---

def _ensure_preparacao_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS preparacao_estado (
            chave         TEXT PRIMARY KEY,
            valor         TEXT NOT NULL,
            atualizado_em TEXT NOT NULL,
            fonte         TEXT
        )
    ''')


def set_preparacao(chave, valor, fonte=None):
    """Grava estado de preparação (key-value). Upsert idempotente."""
    conn = get_connection()
    try:
        _ensure_preparacao_table(conn)
        conn.execute('''
            INSERT INTO preparacao_estado (chave, valor, atualizado_em, fonte)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chave) DO UPDATE SET
                valor = excluded.valor,
                atualizado_em = excluded.atualizado_em,
                fonte = excluded.fonte
        ''', (chave, str(valor), agora().isoformat(timespec="seconds"), fonte))
        conn.commit()
    finally:
        conn.close()


def get_preparacao(chave):
    """Lê estado de preparação. Retorna {valor, atualizado_em, fonte} ou None."""
    conn = get_connection()
    try:
        _ensure_preparacao_table(conn)
        row = conn.execute(
            "SELECT valor, atualizado_em, fonte FROM preparacao_estado WHERE chave = ?",
            (chave,)).fetchone()
    finally:
        conn.close()
    if not row:
        return None
    return {"valor": row[0], "atualizado_em": row[1], "fonte": row[2]}


def get_semana_conteudo():
    """Semana de conteúdo do cronograma (posição SSOT). int ou None."""
    item = get_preparacao("semana_conteudo")
    if not item:
        return None
    try:
        return int(item["valor"])
    except (TypeError, ValueError):
        return None


def get_ritmo_real(janela_dias=14, incluir_simulado=True):
    """Ritmo real de questões (q/dia) na janela móvel, de sessoes_bulk.
    s126: simulado passa a CONTAR (reverte s099) -- é volume real e, do 2o ciclo em diante,
    a maior parte do estudo é prova antiga/simulado. Passe incluir_simulado=False para medir
    só o avanço da grade EMED."""
    filtro = "" if incluir_simulado else "area <> 'Simulado' AND "
    conn = get_connection()
    try:
        # F80b: o corte vem do relogio unico (LOCAL), nunca do date('now') do
        # SQLite (UTC) -- entre 21h e a meia-noite locais o dia UTC ja virou e a
        # janela inteira desliza. `data_sessao` e gravado local pelo writer.
        from datetime import timedelta as _td
        corte = (agora().date() - _td(days=int(janela_dias))).isoformat()
        row = conn.execute(
            "SELECT COALESCE(SUM(questoes_feitas), 0) FROM sessoes_bulk "
            "WHERE " + filtro + "data_sessao >= ?",
            (corte,)).fetchone()
    finally:
        conn.close()
    total = row[0] if row else 0
    return round(total / janela_dias, 1) if janela_dias > 0 else 0.0


def get_fresh_error_cards(tema=None, janela_horas=48):
    """Cards de erro FRESCOS: state=0 criados na janela (o INSERT de fsrs_cards
    grava due=now na criação — para state 0, due == momento de criação; contrato
    fixado por teste). Exclui aposentados/quarentena (needs_qualitative >= 2 —
    vazamento fechado na part-1). Filtro opcional por tema/area (LIKE)."""
    conn = get_connection()
    try:
        extra = ""
        # F80b: corte derivado de `agora()` (LOCAL), o mesmo relogio que gravou
        # o `due`. Com datetime('now') o SQLite responde em UTC e a janela de
        # `janela_horas` encolhe pelo offset da zona (3h em BRT).
        from datetime import timedelta as _td
        params = [(agora() - _td(hours=int(janela_horas))).strftime(FORMATO_CARIMBO)]
        if tema:
            extra = " AND (t.tema LIKE ? OR t.area LIKE ?)"
            params += ["%" + tema + "%", "%" + tema + "%"]
        df = pd.read_sql('''
            SELECT f.id, f.frente_pergunta, t.area, t.tema, fc.due
            FROM flashcards f
            JOIN fsrs_cards fc ON fc.card_id = f.id
            JOIN taxonomia_cronograma t ON t.id = f.tema_id
            WHERE fc.state = 0 AND fc.due >= ?
              AND COALESCE(f.needs_qualitative, 0) < 2''' + extra + '''
            ORDER BY f.id DESC
        ''', conn, params=params)
    finally:
        conn.close()
    return df.to_dict('records')


def registrar_condicao_dia(tempo_h, energia):
    """Registra as condições declaradas do dia (tempo/energia) em preparacao_estado
    — série bruta para o preditivo futuro (PRD orquestracao, pergunta em aberto 2)."""
    import json as _json
    set_preparacao(
        "condicao_dia",
        _json.dumps({"data": datetime.now().date().isoformat(),
                     "tempo_h": tempo_h, "energia": energia}, ensure_ascii=False),
        fonte="day_plan")

def get_db_metrics():
    """Consulta métricas de desempenho por área (1 linha por área após import fixado)."""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT
            area AS "Área",
            SUM(questoes_realizadas) AS "Total",
            SUM(questoes_acertadas)  AS "Acertos"
        FROM taxonomia_cronograma
        GROUP BY area
        HAVING SUM(questoes_realizadas) > 0
    ''', conn)
    conn.close()
    if df.empty:
        return {'total_questoes': 0, 'total_acertos': 0, 'media_desempenho': 0.0, 'df_areas': df}
    df['Desempenho'] = (df['Acertos'] / df['Total'] * 100).round(1)
    df = df.sort_values('Desempenho', ascending=True)
    total_questoes = int(df['Total'].sum())
    total_acertos  = int(df['Acertos'].sum())
    media          = total_acertos / total_questoes * 100 if total_questoes > 0 else 0.0
    return {'total_questoes': total_questoes, 'total_acertos': total_acertos,
            'media_desempenho': round(media, 1), 'df_areas': df}

def get_taxonomia_rendimento():
    """Lista (area, tema, volume, erros) por tema da taxonomia — read-only.

    Sinal de rendimento para priorização de cobertura de SSOT (F16a): `volume` =
    `questoes_realizadas`; `erros` = `questoes_realizadas - questoes_acertadas`.
    Temas sem questões entram com volume/erros 0. Retorna list[dict].
    """
    conn = get_connection()
    df = pd.read_sql(
        'SELECT area, tema, '
        'questoes_realizadas AS volume, '
        '(questoes_realizadas - questoes_acertadas) AS erros '
        'FROM taxonomia_cronograma',
        conn)
    conn.close()
    return df.to_dict('records')

def get_caderno_erros():
    """Traz todos os flashcards do caderno unindo relacionalmente com a taxonomia"""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT 
            t.area as Área,
            t.tema as Tema,
            q.tipo_erro as Tipo,
            q.habilidades_sequenciais as Elo,
            q.enunciado as Questão,
            q.alternativa_correta as Correta,
            q.alternativa_marcada as Marcada,
            q.armadilha_prova as Armadilha
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
        ORDER BY q.id DESC
    ''', conn)
    conn.close()
    return df

def get_cronograma():
    """Retorna o DataFrame do progresso do cronograma"""
    conn = get_connection()
    df = pd.read_sql('SELECT id, semana as Semana, tema as Tema, status as Status FROM cronograma_progresso ORDER BY pos_semana, pos_tema', conn)
    conn.close()
    return df

def update_cronograma_status(row_id, new_status):
    """Atualiza o status de um tema no cronograma"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE cronograma_progresso SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_status, row_id))
    conn.commit()
    conn.close()

def get_due_cards_count():
    """Retorna quantos cards estão vencidos para hoje"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fsrs_cards WHERE due <= ?", (datetime.now(),))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_caderno_detalhado(area=None):
    """Caderno de erros detalhado para a página de consulta (read-only).

    Retorna colunas: id, area, tema, titulo, elo, caso, explicacao, armadilha.
    Filtro opcional por área (match exato). Diferente de `get_caderno_erros()`
    (que serve outra visão); ambos coexistem.
    """
    conn = get_connection()
    sql = '''
        SELECT q.id, t.area, t.tema, q.titulo,
               q.habilidades_sequenciais AS elo,
               q.o_que_faltou AS caso,
               q.explicacao_correta AS explicacao,
               q.armadilha_prova AS armadilha
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
    '''
    params = ()
    if area:
        sql += ' WHERE t.area = ?'
        params = (area,)
    sql += ' ORDER BY q.id DESC'
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

def carga_agendada(cursor, inicio, fim):
    """{date: n_cards} de cards de revisão já agendados na faixa. Read-only.

    Ignora cards aposentados (`needs_qualitative >= 2`): eles nunca entram na
    fila, então não são carga real e não devem influenciar o balanceamento.
    """
    from datetime import date as _date
    linhas = cursor.execute(
        "SELECT date(f.due) AS d, COUNT(1) FROM fsrs_cards f "
        "JOIN flashcards l ON l.id = f.card_id "
        "WHERE f.state > 0 AND COALESCE(l.needs_qualitative, 0) < 2 "
        "  AND date(f.due) BETWEEN ? AND ? GROUP BY d",
        (inicio.isoformat(), fim.isoformat())).fetchall()
    out = {}
    for d, n in linhas:
        try:
            out[_date.fromisoformat(d)] = n
        except (TypeError, ValueError):
            continue
    return out


def blackout_provas(path=None):
    """Dias a evitar no agendamento FSRS (F71): dia de cada prova + o seguinte.

    Delega ao leitor UNICO `app.utils.provas` (F88): nenhuma data no codigo,
    nenhum segundo parser de `core/provas.json`. Tolerante por contrato (WARN em
    stderr, nunca excecao -- o stdout do `fsrs_queue --record` e JSON puro).
    """
    from app.utils import provas
    return provas.blackout_provas(path)


def overflow_blackout(cursor, dias_evitar=None):
    """Cards de revisao ATIVOS cujo `due` esta num dia de blackout (F71, rider do
    `/ai-eng`): o overflow nao e so impresso -- e estado do banco, e este leitor
    read-only o entrega a qualquer painel (boot `day_plan`, `fsrs_load --blackout`).
    Returns: [{card_id, due}] ordenado por due, card_id."""
    evitar = set(blackout_provas() if dias_evitar is None else dias_evitar)
    if not evitar:
        return []
    marcadores = ",".join("?" * len(evitar))
    rows = cursor.execute(
        "SELECT f.card_id, date(f.due) FROM fsrs_cards f "
        "JOIN flashcards l ON l.id = f.card_id "
        f"WHERE f.state > 0 AND {ativo_where('l.')} AND date(f.due) IN ({marcadores}) "
        "ORDER BY f.due, f.card_id",
        tuple(sorted(d.isoformat() for d in evitar))).fetchall()
    return [{"card_id": int(c), "due": d} for c, d in rows]


def _balancear_due(cursor, metrics, hoje=None, dias_evitar=None):
    """Aplica o load balancer ao `due` calculado pelo FSRS. Devolve metrics.

    Mantém `stability`/`difficulty` intocados; ajusta `due` e, por honestidade
    do revlog, `scheduled_days` para o intervalo efetivamente agendado.
    `hoje`/`dias_evitar` sao injetaveis (testes e re-rodada sobre a fila);
    por default = hoje real e o blackout de `core/provas.json` (F71).
    """
    from datetime import date as _date, datetime as _dt, timedelta as _td
    from app.utils.fsrs_balance import escolher_dia, folga_de

    due = metrics.get("due")
    if isinstance(due, str):
        due = _dt.fromisoformat(due)
    if not isinstance(due, _dt):
        return metrics

    intervalo = int(metrics.get("scheduled_days") or 0)
    if int(metrics.get("state") or 0) != 2 or not folga_de(intervalo):
        return metrics

    hoje = hoje or _date.today()
    alvo = due.date()
    f = folga_de(intervalo)
    evitar = set(blackout_provas() if dias_evitar is None else dias_evitar)
    carga = carga_agendada(cursor, alvo - _td(days=f), alvo + _td(days=f))
    novo_dia, desloc = escolher_dia(alvo, intervalo, carga, hoje,
                                    state=int(metrics.get("state") or 0),
                                    dias_evitar=evitar)
    if novo_dia in evitar:
        # F71 (d): alvo em blackout sem vaga antes da prova na folga. NAO empurra
        # em silencio: mantem o due do FSRS e declara o overflow ao operador.
        print(f"[FSRS_BALANCE] OVERFLOW: due {alvo} cai no blackout de prova e nao ha "
              f"vaga antes da prova dentro da folga (+-{f}d); due mantido.",
              file=sys.stderr)
        return metrics
    if not desloc:
        return metrics

    metrics = dict(metrics)
    metrics["due"] = _dt.combine(novo_dia, due.time())
    metrics["scheduled_days"] = max(0, intervalo + desloc)
    # Informe de operador em STDERR: o stdout dos CLIs que gravam revisao
    # (fsrs_queue --record) e JSON puro por contrato (hotfix 2026-09-06).
    print(f"[FSRS_BALANCE] due {alvo} -> {novo_dia} ({desloc:+d}d; "
          f"carga {carga.get(alvo, 0)} -> {carga.get(novo_dia, 0)})",
          file=sys.stderr)
    return metrics


def rebalancear_blackout(conn, hoje=None, dias_evitar=None, aplicar=False):
    """Re-roda o balanceador (F71) sobre a fila EXISTENTE: cards de revisao cujo
    `due` cai no blackout de prova vao para antes da prova, dentro da folga.

    Operacao em massa sobre `fsrs_cards` -> disciplina §10.7: `aplicar=False`
    (default) e o dry-run que declara o diff; `aplicar=True` grava e faz o
    COUNT-ASSERT (n de linhas escritas == n declarado; divergencia = rollback).
    So toca `due`/`scheduled_days` -- `stability`/`difficulty` intocados, nenhuma
    linha de revlog (nao e revisao). Cards sem vaga antes da prova ficam onde
    estao e saem em `overflow` (nunca empurrados em silencio).

    Returns: {movidos: [{card_id, de, para, deslocamento}], overflow: [{card_id,
    due, motivo}], resumo: {"de -> para": n}, aplicado: bool, escritos: int}.
    """
    from datetime import date as _date, datetime as _dt, timedelta as _td
    from app.utils.fsrs_balance import escolher_dia, folga_de, DESLOCAMENTO_MAXIMO

    hoje = hoje or _date.today()
    evitar = set(blackout_provas() if dias_evitar is None else dias_evitar)
    vazio = {"movidos": [], "overflow": [], "resumo": {}, "aplicado": bool(aplicar),
             "escritos": 0, "blackout": sorted(d.isoformat() for d in evitar)}
    if not evitar:
        return vazio
    cursor = conn.cursor()
    marcadores = ",".join("?" * len(evitar))
    rows = cursor.execute(
        "SELECT f.card_id, f.due, f.scheduled_days FROM fsrs_cards f "
        "JOIN flashcards l ON l.id = f.card_id "
        f"WHERE f.state = 2 AND {ativo_where('l.')} AND date(f.due) IN ({marcadores}) "
        "ORDER BY f.due, f.card_id",
        tuple(sorted(d.isoformat() for d in evitar))).fetchall()
    if not rows:
        return vazio
    carga = carga_agendada(cursor, min(evitar) - _td(days=DESLOCAMENTO_MAXIMO),
                           max(evitar) + _td(days=DESLOCAMENTO_MAXIMO))
    movidos, overflow, resumo = [], [], {}
    for card_id, due, intervalo in rows:
        due_dt = _dt.fromisoformat(str(due))
        alvo = due_dt.date()
        intervalo = int(intervalo or 0)
        if not folga_de(intervalo):
            overflow.append({"card_id": int(card_id), "due": alvo.isoformat(),
                             "motivo": f"intervalo {intervalo}d sem folga"})
            continue
        novo, desloc = escolher_dia(alvo, intervalo, carga, hoje, state=2, dias_evitar=evitar)
        if novo in evitar or not desloc:
            overflow.append({"card_id": int(card_id), "due": alvo.isoformat(),
                             "motivo": f"sem vaga antes da prova na folga (+-{folga_de(intervalo)}d)"})
            continue
        movidos.append({"card_id": int(card_id), "de": alvo, "para": novo,
                        "deslocamento": int(desloc), "due_novo": _dt.combine(novo, due_dt.time()),
                        "scheduled_days": max(0, intervalo + desloc), "due_lido": str(due)})
        carga[novo] = carga.get(novo, 0) + 1
        carga[alvo] = max(0, carga.get(alvo, 0) - 1)
        chave = f"{alvo.isoformat()} -> {novo.isoformat()}"
        resumo[chave] = resumo.get(chave, 0) + 1
    escritos = 0
    if aplicar and movidos:
        for m in movidos:
            cursor.execute("UPDATE fsrs_cards SET due = ?, scheduled_days = ? "
                           "WHERE card_id = ? AND due = ?",
                           (m["due_novo"], m["scheduled_days"], m["card_id"], m["due_lido"]))
            escritos += cursor.rowcount
        if escritos != len(movidos):            # COUNT-ASSERT (§10.7)
            conn.rollback()
            raise RuntimeError(f"COUNT-ASSERT falhou: declarados {len(movidos)}, "
                               f"escritos {escritos} -- rollback, nada gravado")
        conn.commit()
    for m in movidos:
        m.pop("due_novo", None); m.pop("due_lido", None); m.pop("scheduled_days", None)
    return {"movidos": movidos, "overflow": overflow, "resumo": resumo,
            "aplicado": bool(aplicar), "escritos": escritos,
            "blackout": sorted(d.isoformat() for d in evitar)}


class ConcurrentReviewError(Exception):
    """Re-record bloqueado: o estado FSRS mudou entre a leitura e a gravação.

    Trava técnica da Invariante C do contrato revisao-calibrada (part-2) —
    antes era garantia só de protocolo (incidente card 403, s108)."""


ROTULOS_RATING = {1: "again", 2: "hard", 3: "good", 4: "easy"}


def preview_ratings(flashcard_id):
    """P3 part-3: a consequência dos 4 ratings ANTES da escolha — rating é
    input do modelo, não intervalo fixo. Read-only: roda o scheduler sobre
    CÓPIAS do estado lido; zero escrita. O intervalo é PRÉ-balanceador — o
    record pode deslocar o due em ±5% quando o intervalo é >= 4d (flag
    `balanceado_apos_record` avisa)."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn,
                         params=(flashcard_id,))
    finally:
        conn.close()
    if df.empty:
        card_data = FSRS().init_card()
        card_data['card_id'] = flashcard_id
    else:
        card_data = df.iloc[0].to_dict()
    fsrs = FSRS()
    out = {}
    for rating in (1, 2, 3, 4):
        m = fsrs.evaluate(dict(card_data), rating)
        dias = int(m["scheduled_days"])
        out[ROTULOS_RATING[rating]] = {
            "scheduled_days": dias,
            "due": str(m["due"]),
            "rotulo": "hoje" if dias < 1 else f"{dias}d",
            "balanceado_apos_record": dias >= 4,
        }
    return out


def _ensure_revlog_columns(conn):
    """P3 part-1: colunas de proveniência no revlog — `card_version` (a versão
    que o usuário VIU) e `selection_reason` (por que o card foi servido).
    ALTER idempotente (padrão `_ensure_status_column` do repo). Histórico
    antigo fica NULL — proveniência começa agora, sem backfill."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(fsrs_revlog)")}
    if "card_version" not in cols:
        conn.execute("ALTER TABLE fsrs_revlog ADD COLUMN card_version INTEGER")
    if "selection_reason" not in cols:
        conn.execute("ALTER TABLE fsrs_revlog ADD COLUMN selection_reason TEXT")
    if "reason_servido" not in cols:
        # F76 (s174): proveniencia RECOMPUTADA no ato do record (bucket real do
        # card antes da revisao). Divergencia = selection_reason != reason_servido,
        # consultavel por SQL -- o contador de gate-miss (B1) le daqui.
        conn.execute("ALTER TABLE fsrs_revlog ADD COLUMN reason_servido TEXT")


REASONS_EQUIVALENTES = {
    # `pre_bloco` e MODO de servico (mini-drill de erros frescos de um tema), nao
    # bucket: o card por baixo e fresh_error ou novo. Nao e divergencia.
    "pre_bloco": {"fresh_error", "novo"},
}


def bucket_de(state, due, questao_id, instante=None):
    """Bucket REAL de um card (puro): a mesma regra de `get_cards_by_bucket`, sem banco.

    vencido    = state>0 e due antes de hoje 00:00
    agendado   = state>0 e due dentro de hoje
    fresh_error= state 0, nascido de erro (questao_id) e due (= criacao) na janela JANELA_FRESH_H
    novo       = state 0 fora disso
    futuro     = state>0 com due depois de hoje (servido fora de qualquer bucket)
    """
    from datetime import datetime as _dt, timedelta as _td
    instante = instante or agora()          # relogio unico (F80)
    if isinstance(due, str):
        due = _dt.fromisoformat(due)
    if not isinstance(due, _dt):
        return "novo" if not int(state or 0) else "futuro"
    if int(state or 0) == 0:
        if questao_id is not None and due >= instante - _td(hours=JANELA_FRESH_H):
            return "fresh_error"
        return "novo"
    inicio = instante.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + _td(days=1)
    if due < inicio:
        return "vencido"
    if due < fim:
        return "agendado"
    return "futuro"


def reason_diverge(recebido, servido) -> bool:
    """Divergencia de proveniencia (F76). Sem `recebido` nao ha o que comparar."""
    if not recebido or not servido:
        return False
    if recebido == servido:
        return False
    return servido not in REASONS_EQUIVALENTES.get(recebido, set())


def record_review(flashcard_id, rating, selection_reason=None):
    """Aplica o algoritmo FSRS e atualiza o banco de dados.

    part-2 (flashcards-integridade): lê o estado e delega a `_aplicar_review`
    (lock otimista). Corrida → `ConcurrentReviewError`, nada gravado.
    P3 part-1: `selection_reason` opcional (vencido|fresh_error|agendado|novo|
    pre_bloco) persiste no revlog; assinatura retro-compatível."""
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn, params=(flashcard_id,))
        if df.empty:
            # Card sem linha FSRS: antes o UPDATE atingia 0 linhas e a revisão se
            # perdia do estado (só o revlog registrava). Agora vira INSERT.
            fsrs = FSRS()
            card_data = fsrs.init_card()
            card_data['card_id'] = flashcard_id
            card_novo = True
        else:
            card_data = df.iloc[0].to_dict()
            card_novo = False
        # F76 (s174): proveniencia REAL recomputada ANTES de aplicar (a revisao
        # muda state/due). `--reason auto` = usar a recomputada.
        row_q = conn.execute("SELECT questao_id FROM flashcards WHERE id = ?",
                             (flashcard_id,)).fetchone()
        questao_id = row_q[0] if row_q else None
        reason_servido = bucket_de(card_data.get('state'), card_data.get('due'), questao_id)
        if selection_reason == "auto":
            selection_reason = reason_servido
        metrics = _aplicar_review(conn, card_data, rating, card_novo=card_novo,
                                  selection_reason=selection_reason,
                                  reason_servido=reason_servido)
        metrics["reason_servido"] = reason_servido
        metrics["selection_reason"] = selection_reason
        metrics["reason_divergente"] = reason_diverge(selection_reason, reason_servido)
        return metrics
    finally:
        conn.close()


def _aplicar_review(conn, card_data, rating, card_novo=False, selection_reason=None,
                    reason_servido=None):
    """Núcleo da gravação sobre um estado LIDO (testável em separado).

    Lock otimista: o UPDATE é condicionado ao `last_review` lido — duas
    aplicações do MESMO estado → a segunda dá rowcount 0 → rollback +
    `ConcurrentReviewError`, e o revlog NÃO ganha linha. Para card novo o
    INSERT usa a PK como trava (corrida falha alto com IntegrityError)."""
    cursor = conn.cursor()
    flashcard_id = card_data['card_id']

    # `last_review`/`elapsed_days` do estado lido — normalizados p/ o WHERE
    # (pandas devolve None/NaN para NULL; o banco guarda TEXT).
    lr_lido = card_data.get('last_review')
    if lr_lido is None or isinstance(lr_lido, float):
        lr_lido = ''
    else:
        lr_lido = str(lr_lido)
    elapsed_anterior = None if card_novo else card_data.get('elapsed_days')
    if isinstance(elapsed_anterior, float):
        elapsed_anterior = None

    # Calcula próximo estado via FSRS
    fsrs = FSRS()
    new_metrics = fsrs.evaluate(card_data, rating)

    # Load balancing do calendário (s128). Dentro da janela de folga do
    # intervalo (+-5%), escolhe o dia de MENOR carga já agendada -- achata
    # o pico sem tocar em stability/difficulty. Só card de revisão com
    # intervalo >= 4d é elegível; a regra vive em fsrs_balance (puro).
    # Falha aqui nunca derruba a gravação da revisão.
    try:
        new_metrics = _balancear_due(cursor, new_metrics)
    except Exception as e:                                    # pragma: no cover
        print(f"[WARN] FSRS_BALANCE: balanceamento pulado ({e}); due original mantido.",
              file=sys.stderr)

    if card_novo:
        cursor.execute('''
            INSERT INTO fsrs_cards (card_id, state, due, stability, difficulty,
                                    elapsed_days, scheduled_days, reps, lapses, last_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flashcard_id, new_metrics['state'], new_metrics['due'], new_metrics['stability'],
            new_metrics['difficulty'], new_metrics['elapsed_days'], new_metrics['scheduled_days'],
            new_metrics['reps'], new_metrics['lapses'], new_metrics['last_review']
        ))
    else:
        cursor.execute('''
            UPDATE fsrs_cards
            SET state = ?, due = ?, stability = ?, difficulty = ?,
                elapsed_days = ?, scheduled_days = ?, reps = ?, lapses = ?, last_review = ?
            WHERE card_id = ?
              AND COALESCE(CAST(last_review AS TEXT), '') = ?
        ''', (
            new_metrics['state'], new_metrics['due'], new_metrics['stability'], new_metrics['difficulty'],
            new_metrics['elapsed_days'], new_metrics['scheduled_days'], new_metrics['reps'],
            new_metrics['lapses'], new_metrics['last_review'], flashcard_id, lr_lido
        ))
        if cursor.rowcount == 0:
            conn.rollback()
            raise ConcurrentReviewError(
                f"card {flashcard_id}: estado FSRS mudou desde a leitura -- "
                f"re-record bloqueado (Invariante C, revisao-calibrada)")

    # Log da revisão — só grava quando o estado gravou (mesma transação).
    # `last_elapsed_days` = elapsed do estado ANTERIOR (era sempre-NULL antes).
    # P3 part-1: proveniência — versão VISTA capturada do banco no ato (fonte =
    # banco, não chamador; single-user, versão corrente == versão vista).
    _ensure_revlog_columns(conn)
    row_v = cursor.execute("SELECT card_version FROM flashcards WHERE id = ?",
                           (flashcard_id,)).fetchone()
    versao_vista = row_v[0] if row_v and row_v[0] is not None else None
    # F80: carimbo explicito pelo relogio unico (LOCAL) -- nunca o DEFAULT do SQLite (UTC).
    cursor.execute('''
        INSERT INTO fsrs_revlog (card_id, rating, state, due, stability, difficulty,
                                 elapsed_days, last_elapsed_days, scheduled_days,
                                 card_version, selection_reason, review_time, reason_servido)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        flashcard_id, rating, new_metrics['state'], new_metrics['due'],
        new_metrics['stability'], new_metrics['difficulty'],
        new_metrics['elapsed_days'], elapsed_anterior, new_metrics['scheduled_days'],
        versao_vista, selection_reason, carimbo(), reason_servido
    ))

    conn.commit()
    return new_metrics

def get_erros_resumidos():
    """Traz erros agrupados por tema para o Bloco 3"""
    conn = get_connection()
    df = pd.read_sql('''
        SELECT
            t.area || ' - ' || t.tema as TemaFull,
            q.tipo_erro,
            q.habilidades_sequenciais as elo_quebrado,
            q.armadilha_prova,
            q.id
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
        ORDER BY t.area, t.tema
    ''', conn)
    conn.close()
    return df


def get_erros_por_tema(tema: str) -> list:
    """Retorna erros recentes filtrados por tema ou área (busca substring, case-insensitive).

    Args:
        tema: Termo de busca (ex: "Cardiologia", "IC", "Insuficiência Cardíaca").

    Returns:
        list[dict]: Lista de erros com chaves id, titulo, tipo_erro,
                    habilidades_sequenciais, armadilha_prova, explicacao_correta,
                    area, tema. Retorna [] se nenhum resultado.
    """
    conn = get_connection()
    df = pd.read_sql('''
        SELECT q.id, q.titulo, q.tipo_erro,
               q.habilidades_sequenciais, q.armadilha_prova, q.explicacao_correta,
               t.area, t.tema
        FROM questoes_erros q
        JOIN taxonomia_cronograma t ON q.tema_id = t.id
        WHERE LOWER(t.tema) LIKE LOWER(?) OR LOWER(t.area) LIKE LOWER(?)
        ORDER BY q.id DESC
        LIMIT 20
    ''', conn, params=(f'%{tema}%', f'%{tema}%'))
    conn.close()
    return df.to_dict('records')


def get_bulk_totals_por_area():
    """Totais de sessoes_bulk por área para o dashboard (read-only, F10).

    Colunas: area, feitas, acertos, sessoes, ultima_sessao, pct.
    DataFrame vazio se o banco/tabela não existir — a página degrada graciosamente.
    """
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = get_connection()
    try:
        df = pd.read_sql('''
            SELECT
                area,
                SUM(questoes_feitas)     AS feitas,
                SUM(questoes_acertadas)  AS acertos,
                COUNT(DISTINCT sessao_num) AS sessoes,
                MAX(data_sessao)           AS ultima_sessao
            FROM sessoes_bulk
            WHERE questoes_feitas > 0
            GROUP BY area
            ORDER BY feitas DESC
        ''', conn)
        df['pct'] = (df['acertos'] / df['feitas'] * 100).round(1)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


def get_trend_sessoes():
    """Série (area, sessao_num, pct) de sessoes_bulk para tendência do dashboard (read-only, F10)."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = get_connection()
    try:
        df = pd.read_sql('''
            SELECT sessao_num, area, questoes_feitas, questoes_acertadas,
                   data_sessao,
                   CASE WHEN questoes_feitas > 0
                        THEN CAST(questoes_acertadas AS REAL) / questoes_feitas * 100
                        ELSE 0 END AS pct
            FROM sessoes_bulk
            WHERE sessao_num > 0
              AND questoes_feitas > 0
            ORDER BY area, sessao_num
        ''', conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


def get_erros_por_area():
    """Contagem de questoes_erros por área para o dashboard (read-only, F10)."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = get_connection()
    try:
        df = pd.read_sql('''
            SELECT t.area, COUNT(q.id) AS erros
            FROM questoes_erros q
            JOIN taxonomia_cronograma t ON t.id = q.tema_id
            GROUP BY t.area
        ''', conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


# P3 part-2: banda prioritária de erros frescos no dreno padrão. Constantes
# simples — tabela de política só se a política começar a variar de verdade.
JANELA_FRESH_H = 48   # janela de frescor (h) — mesma norma do --pre-bloco
CAP_FRESH = 8         # máx. de cards de erro fresco furando a fila por corrida


def get_cards_by_bucket(area=None, tema=None, new_limit=10) -> dict:
    """Retorna flashcards FSRS divididos em QUATRO buckets de prioridade.

    Ordem de serviço (fsrs_queue): atrasados → erros_frescos → hoje → novos.
    P3 part-2: `erros_frescos` = state=0 nascidos de ERRO (questao_id NOT NULL)
    criados na janela JANELA_FRESH_H, cap CAP_FRESH, mais fresco primeiro —
    ataca a reincidência na fila padrão (antes só no --pre-bloco opt-in).
    Sem duplicata: esses ids são excluídos de `novos`.

    Args:
        area: filtro opcional de área (match exato em taxonomia_cronograma.area)
        tema: filtro opcional de tema (LIKE em taxonomia_cronograma.tema)
        new_limit: máximo de cards novos (state == 0) retornados

    Returns:
        dict {atrasados, erros_frescos, hoje, novos}; cada card carrega
        `selection_reason` ∈ {vencido, fresh_error, agendado, novo} além de
        card_id, campos v5, needs_qualitative, due, area, tema. Aposentados
        excluídos pela definição canônica (ativo_where).
    """
    conn = get_connection()
    # F80b: UM relogio para a funcao inteira. Antes, `atrasados`/`hoje` usavam
    # este `now` local e a banda `erros_frescos` perguntava as horas ao SQLite
    # (UTC) -- duas bandas da mesma fila em dois relogios.
    from datetime import timedelta as _td
    now = agora()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    cols = '''f.id AS card_id, f.frente_contexto, f.frente_pergunta,
              f.verso_resposta, f.verso_regra_mestre, f.verso_armadilha,
              f.needs_qualitative, fc.due, t.area, t.tema'''
    base = f'''
        SELECT {cols}
        FROM flashcards f
        JOIN fsrs_cards fc ON f.id = fc.card_id
        LEFT JOIN taxonomia_cronograma t ON f.tema_id = t.id
        WHERE {ativo_where('f.')}
    '''
    extra = ''
    extra_params = []
    if area:
        extra += ' AND t.area = ?'
        extra_params.append(area)
    if tema:
        extra += ' AND t.tema LIKE ?'
        extra_params.append(f'%{tema}%')

    df_atrasados = pd.read_sql(
        base + extra + ' AND fc.due < ? AND fc.state > 0 ORDER BY fc.due ASC',
        conn, params=(*extra_params, today_start))

    df_hoje = pd.read_sql(
        base + extra + ' AND fc.due >= ? AND fc.due <= ? AND fc.state > 0 ORDER BY fc.due ASC',
        conn, params=(*extra_params, today_start, today_end))

    # Banda prioritária: erro fresco (due == criação p/ state=0 — contrato
    # fixado por teste em get_fresh_error_cards). Card-base/andaime (sem
    # questao_id) NÃO fura a fila — não é anti-reincidência.
    df_frescos = pd.read_sql(
        base + extra + ''' AND fc.state = 0 AND f.questao_id IS NOT NULL
            AND fc.due >= ? ORDER BY fc.due DESC LIMIT ?''',
        conn, params=(*extra_params,
                      (now - _td(hours=JANELA_FRESH_H)).strftime(FORMATO_CARIMBO),
                      CAP_FRESH))
    ids_frescos = [int(x) for x in df_frescos["card_id"].tolist()]

    not_in = ""
    params_novos = list(extra_params)
    if ids_frescos:
        not_in = " AND f.id NOT IN (%s)" % ",".join("?" * len(ids_frescos))
        params_novos += ids_frescos
    df_novos = pd.read_sql(
        base + extra + ' AND fc.state = 0' + not_in + ' ORDER BY f.id ASC LIMIT ?',
        conn, params=(*params_novos, new_limit))

    conn.close()

    def _tag(registros, reason):
        return [dict(r, selection_reason=reason) for r in registros]

    return {
        "atrasados": _tag(df_atrasados.to_dict('records'), "vencido"),
        "erros_frescos": _tag(df_frescos.to_dict('records'), "fresh_error"),
        "hoje": _tag(df_hoje.to_dict('records'), "agendado"),
        "novos": _tag(df_novos.to_dict('records'), "novo"),
    }


def update_flashcard_fields(card_id, fields) -> bool:
    """Atualiza os campos v5 de um flashcard existente, preservando o estado FSRS.

    Usado na regeneração de cards (Onda B): reescreve o conteúdo mantendo o
    `card_id` — logo `fsrs_cards`/`fsrs_revlog` permanecem intactos. Marca o
    card como qualitativo e incrementa `card_version`.

    Args:
        card_id: id do flashcard a atualizar.
        fields: dict com qualquer subconjunto de {frente_contexto,
            frente_pergunta, verso_resposta, verso_regra_mestre,
            verso_armadilha, tipo}.

    Returns:
        True se um card foi atualizado; False se `card_id` não existe ou
        nenhum campo válido foi fornecido.
    """
    permitidos = {'frente_contexto', 'frente_pergunta', 'verso_resposta',
                  'verso_regra_mestre', 'verso_armadilha', 'tipo'}
    sets = {k: v for k, v in fields.items() if k in permitidos}
    if not sets:
        return False

    # P3 part-4: gate de qualidade TAMBÉM aqui — este é o caminho de escrita
    # documentado fora dos CLIs (a regen queue instrui o agente a chamar
    # direto). Mesmos predicados parciais do recurate (campos presentes).
    # card_checks vive em tools/ (import lazy por __file__, imune a
    # monkeypatch de DB_PATH).
    # 🔴 FAIL-LOUD (F85, s174): se o gate nao importa, a escrita nao acontece.
    # O `except` antigo degradava para WARN "porque o app nao pode quebrar sem
    # tools/" -- esse app era a UI Streamlit, removida; a justificativa
    # sobreviveu ao motivo (Reachability-Debt variante 3). Mesma forma do
    # gemeo F84 (ratchet do verso), 20 linhas abaixo.
    try:
        _tools = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), 'tools')
        import sys as _sys
        if _tools not in _sys.path:
            _sys.path.insert(0, _tools)
        import card_checks as _cc
    except Exception as e:
        raise RuntimeError(
            f"gate de qualidade (card_checks) indisponivel ({e}) — reescrita RECUSADA. "
            "O gate nao roda, logo a escrita nao acontece.") from e
    erros = list(_cc.checar_encoding(sets))
    for k in ('frente_pergunta', 'verso_resposta'):
        if k in sets and not str(sets[k]).strip():
            erros.append(f"{k} vazia")
    if sets.get('frente_pergunta'):
        t = _cc.checar_pergunta_template(sets)
        if t:
            erros.append(t)
        emb = _cc.checar_resposta_embutida(sets)
        if emb:
            erros.append(emb)
    if erros:
        raise ValueError("gate de qualidade reprovou a reescrita (regua "
                         ".claude/commands/estilo-flashcard.md): " + " | ".join(erros))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT card_version, verso_resposta, frente_contexto, "
                   "frente_pergunta FROM flashcards WHERE id = ?", (card_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return False
    versao_antes = (row[0] if row[0] is not None else 1)
    verso_antes = row[1]

    # F81/B1 (s176) -- alinhamento interno da FRENTE, sobre a visao MERGEADA.
    # Este writer e um dos dois caminhos de REFORJA, e a reforja mira a frente
    # (memoria feedback_reforja_mira_frente). Rodar os predicados so sobre
    # `sets` deixaria passar a edicao parcial: quem reescreve so a pergunta nao
    # carrega o contexto no payload, o predicado veria contexto vazio e ficaria
    # mudo -- que e a forma exata do F79/F79b/F81 (gate que nao cobre o caminho
    # real). WARN, nunca bloqueio: warning-first ate o passivo zerar.
    _frente = {"frente_contexto": sets.get("frente_contexto", row[2]),
               "frente_pergunta": sets.get("frente_pergunta", row[3])}
    for _pred in (_cc.checar_contexto_redundante,
                  _cc.checar_pergunta_generica_com_contexto,
                  _cc.checar_contrafactual_mal_formado):
        _aviso = _pred(_frente)
        if _aviso:
            print(f"[WARN] card #{card_id}: {_aviso}", file=sys.stderr)

    # s170 — ratchet de nao-crescimento do verso. Este writer nao roda gate de
    # atomicidade nenhum (so encoding/template/resposta-embutida), entao sem
    # isto a guarda instalada no recurate seria contornavel por aqui: gate que
    # nao cobre o caminho real e o defeito F79/F79b/F81 se repetindo.
    verso_depois = sets.get('verso_resposta', verso_antes)
    try:
        from audit_card_atomicity import checar_ratchet_verso, medir_verso
    except Exception as e:
        # 🔴 FAIL-LOUD, nao fail-open (audit /ai-eng sobre d2026a1). Degradar
        # para WARN aqui seria escrever sem guarda dentro do proprio fix que
        # existe para impedir isso -- "aviso nao existe, vira gate". A recusa
        # so vale quando a escrita TOCA o verso: bloquear uma edicao de frente
        # por causa do ratchet seria gratuito.
        checar_ratchet_verso = medir_verso = None
        if 'verso_resposta' in sets:
            conn.close()
            raise RuntimeError(
                f"ratchet do verso indisponivel ({e}) — reescrita RECUSADA. "
                "O gate nao roda, logo a escrita nao acontece.")
        print(f"[WARN] CARD_GATE: telemetria de verso indisponivel ({e}).")
    if checar_ratchet_verso is not None and 'verso_resposta' in sets:
        r = checar_ratchet_verso(verso_antes, sets['verso_resposta'])
        if r:
            conn.close()
            raise ValueError(f"ratchet do verso reprovou a reescrita: {r}")

    # Nomes de coluna vêm de um allowlist fixo (não de input) — sem injeção.
    assignments = ", ".join(f"{col} = ?" for col in sets)
    cursor.execute(
        f"UPDATE flashcards SET {assignments}, "
        "quality_source = 'qualitative', needs_qualitative = 0, "
        "card_version = COALESCE(card_version, 1) + 1 WHERE id = ?",
        (*sets.values(), card_id),
    )
    conn.commit()
    conn.close()
    len_a, fr_a = medir_verso(verso_antes) if medir_verso else (0, 0)
    len_d, fr_d = medir_verso(verso_depois) if medir_verso else (0, 0)
    _log_reforja(card_id, 'db.update_flashcard_fields', versao_antes,
                 versao_antes + 1, 'reforja', sorted(sets),
                 (len_a, len_d, fr_a, fr_d))
    return True


def _log_reforja(card_id, writer, versao_antes, versao_depois, reason, campos,
                 verso_metrica=(0, 0, 0, 0)):
    """Evento append-only de REESCRITA de card — chamado SÓ pós-commit.

    Fecha o buraco do hotfix 2026-09-08: `card_version` subia sem que nada
    registrasse quem reescreveu, quando e por quê (o card #321 chegou a v2 com
    o texto do defeito intacto, e não havia como provar). Carrega SÓ ids,
    contagens e tags — nunca texto clínico (contrato de `tools/event_log.py`).
    Falha de log jamais derruba a escrita do card: o `except` é largo de
    propósito, e o card já está commitado quando chegamos aqui.
    """
    try:
        import event_log
        len_a, len_d, fr_a, fr_d = verso_metrica
        event_log.registrar('reforja', {
            'card_id': card_id, 'writer': writer, 'version_antes': versao_antes,
            'version_depois': versao_depois, 'reason': reason,
            'campos': list(campos), 'n_campos': len(campos),
            'len_verso_antes': len_a, 'len_verso_depois': len_d,
            'n_frases_antes': fr_a, 'n_frases_depois': fr_d,
        })
    except Exception as e:  # pragma: no cover — nunca propaga
        print(f"[WARN] REFORJA_LOG: evento nao registrado para card {card_id} ({e}).")


# ---------------------------------------------------------------------------
# Curva de esquecimento — revisão TEMÁTICA (review_log)
# SSOT do "tempo desde a última revisão" por tema. Complementa o FSRS (nível
# card); o refresh dormente NUNCA toca fsrs_cards/fsrs_revlog. Ver
# core/contracts/forgetting-curve-contract.md.
# ---------------------------------------------------------------------------

def resolve_tema_id(area, tema):
    """Resolve (area, tema) -> id em taxonomia_cronograma por match EXATO.

    Centraliza a regra de identidade do tema por (area, tema). Não cria linha.
    Se houver duplicatas (taxonomia poluída pré-dedup), retorna o menor id
    (determinístico). Returns int ou None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM taxonomia_cronograma WHERE area = ? AND tema = ? ORDER BY id ASC LIMIT 1",
        (area, tema))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# --- reforja_marks (B2 / F40+F41+G7, s176) --------------------------------
# A fila de reforja como ESTADO. Tres writers e um leitor; ninguem mais toca a
# tabela (allowlist F49). Append-only por contrato: nao ha UPDATE aqui, e nao ha
# coluna de status para dar UPDATE.

class ReforjaAindaDefeituosa(ValueError):
    """Fechamento RECUSADO: o predicado que motivou a marca ainda dispara.

    Existe porque "alguem editou" nunca foi evidencia de "o defeito saiu". F82
    mediu #321 em card_version=2 com o defeito intacto; a s176 mediu #1568 com
    evento `reforja` registrado em 09-09 e ainda disparando o predicado. Quem
    fecha uma marca afirma que o defeito acabou -- e a afirmacao e checavel.
    """


def _card_para_predicado(conn, card_id):
    row = conn.execute(
        "SELECT frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, "
        "verso_armadilha FROM flashcards WHERE id = ?", (card_id,)).fetchone()
    if row is None:
        return None
    return {"frente_contexto": row[0], "frente_pergunta": row[1],
            "verso_resposta": row[2], "verso_regra_mestre": row[3],
            "verso_armadilha": row[4]}


def cards_ativos_para_predicado():
    """Todos os cards ATIVOS no shape que os predicados de `card_checks` consomem.

    Existe para a ingestao da fila de reforja (F39, s177): varrer o baralho com um
    predicado do registro e propor marcas. Read-only, e o shape e IDENTICO ao de
    `_card_para_predicado` -- se divergissem, a marca proposta pela varredura e a
    re-verificacao do fechamento estariam lendo campos diferentes do mesmo card,
    que e como um gate passa a mentir. Ativo = `ATIVO_WHERE`, a definicao canonica.
    """
    conn = get_connection()
    try:
        linhas = conn.execute(
            "SELECT id, frente_contexto, frente_pergunta, verso_resposta, "
            f"verso_regra_mestre, verso_armadilha FROM flashcards WHERE {ATIVO_WHERE} "
            "ORDER BY id").fetchall()
    finally:
        conn.close()
    return [{"id": r[0], "frente_contexto": r[1], "frente_pergunta": r[2],
             "verso_resposta": r[3], "verso_regra_mestre": r[4],
             "verso_armadilha": r[5]} for r in linhas]


def _registrar_marca(card_id, evento, motivo, evidencia=None, origem=None):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO reforja_marks (card_id, evento, motivo, evidencia, origem, "
            "criado_em) VALUES (?, ?, ?, ?, ?, ?)",
            (int(card_id), evento, motivo, evidencia, origem, carimbo()))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def marcar_reforja(card_id, motivo, origem=None) -> int:
    """Abre uma marca de reforja. Marcar o MESMO card de novo cria outra linha --
    e proposital: '#792 marcado 3x' deixa de ser anedota de HANDOFF e vira COUNT."""
    if not (motivo or "").strip():
        raise ValueError("motivo e obrigatorio -- marca sem motivo nao fecha nem audita")
    return _registrar_marca(card_id, "marcada", motivo.strip(), origem=origem)


def fechar_reforja(card_id, motivo, forcar=False, justificativa=None, origem=None) -> int:
    """Fecha uma marca RE-VERIFICANDO o defeito que a motivou.

    Se `motivo` nomeia um predicado de `card_checks.PREDICADOS_VERIFICAVEIS`, ele e
    re-executado sobre o card COMO ESTA no banco agora. Ainda dispara -> recusa
    (`ReforjaAindaDefeituosa`), a menos que `forcar=True` COM justificativa escrita,
    que fica gravada na linha para auditoria.

    Motivo fora do registro (pacote-de-fatos, pergunta circular, o eixo C semantico)
    nao tem predicado que o meca: fecha com `evidencia='humana'`. Fronteira
    DECLARADA, nunca metrica inventada (AGENTE.md secao 10.8).
    """
    import card_checks as _cc
    predicado = _cc.PREDICADOS_VERIFICAVEIS.get((motivo or "").strip())
    conn = get_connection()
    try:
        card = _card_para_predicado(conn, card_id)
    finally:
        conn.close()
    if card is None:
        raise ValueError(f"card #{card_id} nao existe")

    if predicado is None:
        if forcar and not (justificativa or "").strip():
            raise ValueError("forcar exige justificativa escrita")
        return _registrar_marca(card_id, "fechada", motivo, evidencia="humana", origem=origem)

    ainda = predicado(card)
    if ainda and not forcar:
        raise ReforjaAindaDefeituosa(
            f"card #{card_id} AINDA dispara '{motivo}' apos a reforja: {ainda}. "
            f"Reescrever nao e o mesmo que resolver -- a marca continua aberta. "
            f"Para fechar assim mesmo, use forcar=True com justificativa escrita.")
    if ainda and forcar:
        if not (justificativa or "").strip():
            raise ValueError("forcar exige justificativa escrita")
        return _registrar_marca(card_id, "fechada", motivo,
                                evidencia=f"forcado: {justificativa.strip()}", origem=origem)
    return _registrar_marca(card_id, "fechada", motivo,
                            evidencia=f"predicado {motivo} re-rodou limpo", origem=origem)


def descartar_reforja(card_id, motivo, justificativa, origem=None) -> int:
    """'Olhei e nao era defeito' -- desfecho legitimo e DIFERENTE de 'resolvi'.

    Sem este estado, marca falsa fecharia como conserto e a metrica de passivo
    mentiria para cima."""
    if not (justificativa or "").strip():
        raise ValueError("descartar exige justificativa escrita")
    return _registrar_marca(card_id, "descartada", motivo,
                            evidencia=f"descartada: {justificativa.strip()}", origem=origem)


def fila_reforja(incluir_fechadas=False):
    """Estado DERIVADO dos eventos -- a unica cifra citavel do passivo (G7).

    Uma marca (card_id, motivo) esta ABERTA quando o numero de 'marcada' excede o de
    'fechada' + 'descartada' para aquele par. Devolve lista de dicts ordenada por
    n_marcacoes desc (o reincidente primeiro), depois card_id.
    """
    conn = get_connection()
    try:
        linhas = conn.execute(
            "SELECT card_id, motivo, evento, COUNT(*) FROM reforja_marks "
            "GROUP BY card_id, motivo, evento").fetchall()
    finally:
        conn.close()
    agrupado = {}
    for card_id, motivo, evento, n in linhas:
        d = agrupado.setdefault((card_id, motivo),
                                {"card_id": card_id, "motivo": motivo,
                                 "marcada": 0, "fechada": 0, "descartada": 0})
        d[evento] = n
    saida = []
    for d in agrupado.values():
        d["n_marcacoes"] = d["marcada"]
        d["aberta"] = d["marcada"] > (d["fechada"] + d["descartada"])
        if d["aberta"] or incluir_fechadas:
            saida.append(d)
    saida.sort(key=lambda d: (-d["n_marcacoes"], d["card_id"]))
    return saida


def log_review(tema_id=None, resumo_path=None, kind='dormant_refresh',
               source='agent', note=None) -> int:
    """Registra uma revisão TEMÁTICA em review_log e retorna o id da linha.

    NÃO toca o FSRS (fsrs_cards/fsrs_revlog) — é o registro de re-ensino
    narrativo do tema, complementar à revisão de cards. `kind` ∈
    {dormant_refresh, directed_review, resumo_read, backfill}.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO review_log (tema_id, resumo_path, kind, source, note, reviewed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tema_id, resumo_path, kind, source, note, carimbo()))   # F80: relogio unico
    conn.commit()
    rid = cursor.lastrowid
    conn.close()
    return rid


def get_theme_last_review(tema_id=None, area=None, tema=None):
    """Última revisão de um tema, unindo as 3 fontes de tempo (read-only).

    Fontes: review_log.reviewed_at, fsrs_cards.last_review (via
    flashcards.tema_id) e taxonomia_cronograma.ultima_revisao. Aceita `tema_id`
    direto OU (area, tema). Datas ISO comparam lexicograficamente, então
    `max()` por string dá a mais recente.

    Returns dict {tema_id, last_review (str|None), source (str|None)} ou None
    se o tema não existe.
    """
    if tema_id is None:
        if area is not None and tema is not None:
            tema_id = resolve_tema_id(area, tema)
        if tema_id is None:
            return None
    conn = get_connection()
    cursor = conn.cursor()
    candidates = []  # (timestamp_str, source)
    r = cursor.execute(
        "SELECT MAX(reviewed_at) FROM review_log WHERE tema_id = ?", (tema_id,)).fetchone()
    if r and r[0]:
        candidates.append((r[0], 'review_log'))
    r = cursor.execute('''
        SELECT MAX(fc.last_review) FROM fsrs_cards fc
        JOIN flashcards f ON f.id = fc.card_id
        WHERE f.tema_id = ?''', (tema_id,)).fetchone()
    if r and r[0]:
        candidates.append((r[0], 'fsrs'))
    r = cursor.execute(
        "SELECT ultima_revisao FROM taxonomia_cronograma WHERE id = ?", (tema_id,)).fetchone()
    if r and r[0]:
        candidates.append((r[0], 'taxonomia'))
    conn.close()
    if not candidates:
        return {"tema_id": tema_id, "last_review": None, "source": None}
    best = max(candidates, key=lambda x: x[0])
    return {"tema_id": tema_id, "last_review": best[0], "source": best[1]}


# ---------------------------------------------------------------------------
# Revisão Calibrada — nota de dificuldade-para-o-usuário por TEMA (1-10)
# Estado-de-tema em taxonomia_cronograma. 🔴 Única exceção autorizada à regra
# "só insert_questao.py escreve taxonomia": set_dificuldade toca APENAS as 3
# colunas dificuldade/dificuldade_fonte/dificuldade_at — nunca volume, acertos,
# perf% ou ultima_revisao. Ver core/contracts/revisao-calibrada-contract.md.
# ---------------------------------------------------------------------------

def set_dificuldade(area, tema, nota, fonte) -> bool:
    """Grava a nota de dificuldade (1-10) de um tema. Returns True/False.

    `fonte` ∈ {'usuario', 'agente_inferida', 'aula'} — 'aula' e a nota que
    calibrou a forja de uma aula/PREPARAR, registrada no ato (F18c, Clausula 10
    do revisao-calibrada-contract); nao dispara reinferencia automatica e nao
    deve sobrescrever uma nota soberana 'usuario' (precedencia e responsabilidade
    do chamador). `nota` e clampada em [1,10] (ou None para limpar). False se o
    tema (area, tema) nao existe na taxonomia (nao cria linha — isso e papel do
    insert_questao).
    """
    tema_id = resolve_tema_id(area, tema)
    if tema_id is None:
        return False
    if nota is not None:
        nota = max(1, min(10, int(nota)))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE taxonomia_cronograma "
        "SET dificuldade = ?, dificuldade_fonte = ?, dificuldade_at = ? "
        "WHERE id = ?",
        (nota, fonte, agora().isoformat(" "), tema_id))
    conn.commit()
    conn.close()
    return True


def get_dificuldade(area, tema):
    """Lê a nota de dificuldade de um tema.

    Returns dict {'nota', 'fonte', 'at'} ou None se o tema não existe.
    Tema existente mas sem calibração → {'nota': None, 'fonte': None, 'at': None}
    (distingue "não calibrado" de "tema ausente").
    """
    tema_id = resolve_tema_id(area, tema)
    if tema_id is None:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT dificuldade, dificuldade_fonte, dificuldade_at "
        "FROM taxonomia_cronograma WHERE id = ?", (tema_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {"nota": row[0], "fonte": row[1], "at": row[2]}


def get_tema_stats(area, tema):
    """Volume/performance de um tema (read-only). None se o tema não existe.

    Sinal FRIO para infer_nota (eixo 1). Returns
    {'questoes', 'acertos', 'percentual', 'ultima_revisao'}.
    """
    tema_id = resolve_tema_id(area, tema)
    if tema_id is None:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao "
        "FROM taxonomia_cronograma WHERE id = ?", (tema_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {"questoes": row[0], "acertos": row[1],
            "percentual": row[2], "ultima_revisao": row[3]}


def get_ultimo_bloco_tema(area, tema):
    """% de acerto do bloco MAIS RECENTE de (area, tema) em sessoes_bulk (read-only).

    sessoes_bulk não tem coluna `tema` — o tema vive em `observacoes`; casa por
    LIKE. Sinal FRIO para infer_nota (eixo 3). None se não houver bloco do tema
    (eixo não atua — degradação graciosa).
    """
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT questoes_feitas, questoes_acertadas FROM sessoes_bulk "
        "WHERE area = ? AND observacoes LIKE ? AND questoes_feitas > 0 "
        "ORDER BY data_sessao DESC, id DESC LIMIT 1",
        (area, f"%{tema}%")).fetchone()
    conn.close()
    if not row or not row[0]:
        return None
    return round(row[1] / row[0] * 100, 1)



# --- Ledger de Habilidades (spec ledger-de-habilidades) ---
# Camada de LEITURA para app/ e agentes. A escrita em massa (backfill) e a
# curadoria vivem no CLI standalone `tools/habilidades.py`; aqui expomos o que
# o dashboard e o agente precisam consultar durante a sessão.

VEREDITOS_HABILIDADE = ('acertou', 'incerteza', 'desatencao', 'errou', 'indefinido')


def get_habilidades_reincidentes(limit=10, min_temas=1):
    """Habilidades ordenadas por reincidência (DataFrame, read-only).

    `temas_distintos >= 3` separa **padrão de raciocínio** de **lacuna de
    conteúdo**: a mesma habilidade falhando em temas diferentes não é
    desconhecer o tema, é desconhecer a habilidade. É a granularidade que a
    faixa dos 75-80% exige — `weak_areas` continua sendo por tema, esta camada
    é por habilidade. Devolve DataFrame vazio se o ledger ainda não existir.
    """
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT h.id AS habilidade_id, h.texto, "
            "       COUNT(qh.id)               AS ocorrencias, "
            "       COUNT(DISTINCT qh.tema_id) AS temas_distintos, "
            "       SUM(CASE WHEN qh.veredito = 'errou'     THEN 1 ELSE 0 END) AS n_errou, "
            "       SUM(CASE WHEN qh.veredito = 'incerteza' THEN 1 ELSE 0 END) AS n_incerteza "
            "  FROM habilidades h "
            "  JOIN questao_habilidades qh ON qh.habilidade_id = h.id "
            " GROUP BY h.id, h.texto "
            "HAVING temas_distintos >= ? "
            " ORDER BY ocorrencias DESC, temas_distintos DESC "
            " LIMIT ?", conn, params=(int(min_temas), int(limit)))
    except Exception:
        return pd.DataFrame(columns=['habilidade_id', 'texto', 'ocorrencias',
                                     'temas_distintos', 'n_errou', 'n_incerteza'])
    finally:
        conn.close()
    if not df.empty:
        df['padrao_de_raciocinio'] = df['temas_distintos'] >= 3
    return df


def registrar_habilidade(texto, tema_id=None, veredito='errou', questao_id=None,
                         origem='agente'):
    """Registra uma ocorrência de habilidade. NÃO toca `questoes_erros`.

    Existe para o caso que o pipeline de erro não cobre: aprendizado colhido de
    questão **acertada** (ou acertada com dúvida). Por isso `questao_id` é
    opcional e nada aqui incrementa erro nem volume.
    """
    if veredito not in VEREDITOS_HABILIDADE:
        raise ValueError("veredito inválido: %r -- válidos: %s"
                         % (veredito, ', '.join(VEREDITOS_HABILIDADE)))
    if not texto or not str(texto).strip():
        raise ValueError("texto da habilidade vazio")
    import unicodedata
    _s = unicodedata.normalize('NFKD', str(texto))
    norm = ' '.join(''.join(c for c in _s if not unicodedata.combining(c)).lower().split())
    agora_iso = agora().isoformat(timespec='seconds')
    conn = get_connection()
    try:
        cur = conn.cursor()
        row = cur.execute('SELECT id FROM habilidades WHERE texto_norm = ?',
                          (norm,)).fetchone()
        if row:
            hid = row[0]
        else:
            cur.execute('INSERT INTO habilidades (texto, texto_norm, precisa_curadoria, '
                        'criado_em) VALUES (?, ?, 0, ?)', (str(texto).strip(), norm, agora_iso))
            hid = cur.lastrowid
        cur.execute('INSERT INTO questao_habilidades (habilidade_id, questao_id, tema_id, '
                    'ordem, veredito, origem, criado_em) VALUES (?, ?, ?, 0, ?, ?, ?)',
                    (hid, questao_id, tema_id, veredito, origem, agora_iso))
        conn.commit()
        return hid
    finally:
        conn.close()


# --- Série de blocos para diagnóstico de variância (spec variancia-e-zona) ---

def get_serie_blocos(piso_questoes=15, ultimos=None, incluir_simulado=False):
    """Série de % de acerto por bloco (DataFrame, read-only).

    Substrato do diagnóstico de variância: no platô dos 75-80%, a **variância**
    entre blocos diz mais que a média — nota alta numa prova e baixa em outra
    indica desempenho dependente do perfil da prova, não do conhecimento.
    Blocos abaixo do piso são excluídos: 5 questões geram % com granularidade
    de 20 pp e poluem a métrica com ruído amostral.
    """
    filtro = "" if incluir_simulado else "area <> 'Simulado' AND "
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT data_sessao, area, questoes_feitas, questoes_acertadas "
            "FROM sessoes_bulk WHERE " + filtro + "questoes_feitas >= ? "
            "ORDER BY data_sessao, id", conn, params=(int(piso_questoes),))
    finally:
        conn.close()
    if df.empty:
        return df
    df['pct'] = (df['questoes_acertadas'] / df['questoes_feitas'] * 100).round(1)
    if ultimos:
        df = df.tail(int(ultimos))
    return df
