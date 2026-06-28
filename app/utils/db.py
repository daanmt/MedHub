"""
MedHub DB access layer — única fonte de `import sqlite3` na camada `app/`.

Convenções: reads retornam `pandas.DataFrame`; writes usam cursor+commit
explícitos; sempre fechar via `conn.close()`; queries parametrizadas
(`params=(...)`) para evitar SQL injection. `DB_PATH` é resolvido relativo
à raiz do repo.

Callers acima: `app/pages/*.py`, `app/engine/*.py`. CLIs em `tools/` usam
`sqlite3` diretamente por design (scripts standalone).
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from app.utils.fsrs import FSRS

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

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

def record_review(flashcard_id, rating):
    """Aplica o algoritmo FSRS e atualiza o banco de dados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Busca estado atual do card
    df = pd.read_sql("SELECT * FROM fsrs_cards WHERE card_id = ?", conn, params=(flashcard_id,))
    if df.empty:
        fsrs = FSRS()
        card_data = fsrs.init_card()
        card_data['card_id'] = flashcard_id
    else:
        card_data = df.iloc[0].to_dict()

    # 2. Calcula próximo estado via FSRS
    fsrs = FSRS()
    new_metrics = fsrs.evaluate(card_data, rating)
    
    # 3. Atualiza banco
    cursor.execute('''
        UPDATE fsrs_cards 
        SET state = ?, due = ?, stability = ?, difficulty = ?, 
            elapsed_days = ?, scheduled_days = ?, reps = ?, lapses = ?, last_review = ?
        WHERE card_id = ?
    ''', (
        new_metrics['state'], new_metrics['due'], new_metrics['stability'], new_metrics['difficulty'],
        new_metrics['elapsed_days'], new_metrics['scheduled_days'], new_metrics['reps'], 
        new_metrics['lapses'], new_metrics['last_review'], flashcard_id
    ))
    
    # 4. Log da revisão (Tabela nova no schema v3.6)
    cursor.execute('''
        INSERT INTO fsrs_revlog (card_id, rating, state, due, stability, difficulty, elapsed_days, scheduled_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        flashcard_id, rating, new_metrics['state'], new_metrics['due'], 
        new_metrics['stability'], new_metrics['difficulty'], 
        new_metrics['elapsed_days'], new_metrics['scheduled_days']
    ))
    
    conn.commit()
    conn.close()
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


def get_cards_by_bucket(area=None, tema=None, new_limit=10) -> dict:
    """Retorna flashcards FSRS divididos em três buckets temporais.

    Args:
        area: filtro opcional de área (match exato em taxonomia_cronograma.area)
        tema: filtro opcional de tema (LIKE em taxonomia_cronograma.tema)
        new_limit: máximo de cards novos (state == 0) retornados

    Returns:
        dict com chaves:
            atrasados (list[dict]): cards vencidos antes de hoje (state > 0)
            hoje (list[dict]): cards que vencem hoje (state > 0)
            novos (list[dict]): cards nunca revisados (state == 0), max new_limit
        Cada dict contém: card_id, frente_contexto, frente_pergunta,
        verso_resposta, verso_regra_mestre, verso_armadilha, needs_qualitative,
        due, area, tema. Cards aposentados (needs_qualitative >= 2) são excluídos.
    """
    conn = get_connection()
    now = datetime.now()
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
        WHERE f.needs_qualitative < 2
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

    df_novos = pd.read_sql(
        base + extra + ' AND fc.state = 0 ORDER BY f.id ASC LIMIT ?',
        conn, params=(*extra_params, new_limit))

    conn.close()
    return {
        "atrasados": df_atrasados.to_dict('records'),
        "hoje": df_hoje.to_dict('records'),
        "novos": df_novos.to_dict('records'),
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

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM flashcards WHERE id = ?", (card_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False

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
    return True


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
        INSERT INTO review_log (tema_id, resumo_path, kind, source, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (tema_id, resumo_path, kind, source, note))
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

    `fonte` ∈ {'usuario', 'agente_inferida'}. `nota` é clampada em [1,10]
    (ou None para limpar). False se o tema (area, tema) não existe na taxonomia
    (não cria linha — isso é papel do insert_questao).
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
        (nota, fonte, datetime.now().isoformat(" "), tema_id))
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

