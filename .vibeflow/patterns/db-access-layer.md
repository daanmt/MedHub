---
tags: [sqlite, db, data-access, ipub, queries, pandas]
modules: [app/utils/db.py, tools/]
applies_to: [services, handlers, scripts]
confidence: inferred
status: active
canonical_source: app/utils/db.py module docstring
last_verified: 2026-08-25
---
# Pattern: DB Access Layer

<!-- vibeflow:auto:start -->
## What
Todo acesso ao `ipub.db` na camada `app/` passa por `app/utils/db.py`: funções nomeadas que abrem a conexão por `get_connection()`, fazem o trabalho com SQL parametrizado e devolvem tipos simples (`pd.DataFrame`, `dict`, `int`, `bool`). O contrato está no docstring do módulo, inclusive o relógio único do banco (F80). Os CLIs de `tools/` ou chamam essas funções (camada fina) ou, quando são writers standalone, abrem `sqlite3` próprio, com o perímetro de escrita preso por teste.

## Where
- `app/utils/db.py` — a camada. Agrupa conexão e relógio, cards ativos, preparação, FSRS (`record_review`), reforja, plano (`plano_*`), sessões e o banco EMED (`emed_*`).
- Chamador em `app/`: `app/engine/get_topic_context.py` (`import app.utils.db as db`).
- CLIs finos, sem `sqlite3` próprio (toda escrita passa por um writer do `db.py`): `tools/plano.py`, `tools/reforja.py`, `tools/emed_banco.py`, `tools/listas.py`, `tools/dormant_refresh.py`, `tools/fsrs_queue.py`; `tools/painel.py` e `tools/hub.py` só leem.
- Writers standalone com conexão própria (exceção autorizada): `tools/insert_questao.py`, `tools/insert_card_base.py`, `tools/insert_card_extra.py`, `tools/recurate_cards.py`, `tools/registrar_sessao_bulk.py`, `tools/normalize_taxonomia.py`, `tools/cards_prune.py`, `tools/habilidades.py`, `tools/dedup_taxonomia.py`, `tools/backfill_review_log.py`. O mapa arquivo -> tabelas está em `tools/test_writer_allowlist.py::ALLOWLIST`.
- Fora desta regra: `app/memory/store.py` abre `sqlite3` para o `medhub_memory.db` (backend da memória longa, não o `ipub.db`) e `app/memory/manager.py` abre o `ipub.db` só em `mode=ro`.

## The Pattern

**Conexão (FKs ligadas por conexão + VIEW canônica):**
```python
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ipub.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    # part-1 (flashcards-integridade): as FKs sempre existiram no schema, mas o
    # SQLite so as impoe com o PRAGMA ligado — e ele e por-conexao.
    conn.execute("PRAGMA foreign_keys = ON")
    _ensure_views(conn)
    return conn
```

**Leitura em DataFrame (`try/finally`):**
```python
def ativos():
    """Cards ativos (definição canônica) como DataFrame — helper único p/ os
    consumidores que hoje reimplementam o filtro."""
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM flashcards_ativos", conn)
    finally:
        conn.close()
```

**Escrita (cursor + commit, carimbo do relógio único):**
```python
def log_review(tema_id=None, resumo_path=None, kind='dormant_refresh',
               source='agent', note=None) -> int:
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
```

**DDL preguiçosa + UPSERT idempotente:**
```python
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
```

**Writer de lote com dry-run no mesmo caminho de código** (`plano_upsert_tarefas`, trecho):
```python
    conn = get_connection()
    try:
        if aplicar:
            _ensure_plano_table(conn)
        existentes = _chaves_plano(conn)
        ...
        if not aplicar:
            # dry-run NAO cria nem a tabela: "nao grava" inclui DDL.
            return {"novas": len(novas), "existentes": len(chaves) - len(novas),
                    "ids_novos": []}
```
O CLI (`tools/plano.py`) mede com `aplicar=False`, imprime o COUNT-ASSERT e só grava com `--apply --expect N` quando `N` bate com o medido.

**Leitura e escrita do FSRS:** `record_review(flashcard_id, rating, selection_reason=None, quando=None)` lê o estado e delega a `_aplicar_review`, que usa lock otimista e levanta `ConcurrentReviewError` numa corrida, sem gravar nada. `quando` (LOCAL naive) é o instante da revisão; no futuro ou não posterior à última revisão -> `ValueError`. Ver a função no `db.py`; não copiar o corpo para cá.

## Rules
- `import sqlite3` em `app/` só no `db.py` (exceção: `app/memory/`, ver Where). Em `tools/`, só writers standalone; CLI novo prefere a camada fina.
- Conexão sempre por `get_connection()`. CLI com conexão própria liga `PRAGMA foreign_keys = ON` (o `insert_questao.py` faz isso).
- Fechar sempre. O idioma atual é `try: ... finally: conn.close()`; funções antigas fecham em linha (`log_review`, `set_dificuldade`).
- `conn.commit()` antes do `close()` em toda escrita.
- SQL parametrizado (`?`, `params=(...)`) para todo valor. f-string só para fragmento canônico do próprio módulo (`ativo_where('f.')`, `RETIDO_REFORJA_SUBQUERY`), nunca para valor de entrada.
- Carimbo de tempo só por `agora()` / `carimbo()` / `hoje()` (hora LOCAL naive). Quem está fora do módulo chama pelo atributo (`db.agora()`) para o teste poder congelar o relógio. Nunca depender do `DEFAULT CURRENT_TIMESTAMP` (UTC): `tools/test_fuso_unico.py` falha nomeando o arquivo.
- Toda tabela escrita existe no schema do `tools/init_db.py` ou tem DDL preguiçosa (`_ensure_<tabela>_table`, `_ensure_<x>_column(s)` com `CREATE ... IF NOT EXISTS` / `ALTER ... ADD COLUMN` idempotente). Trava: `tools/test_schema_escrita.py`.
- Writer novo, ou tabela nova num writer, = editar `ALLOWLIST` em `tools/test_writer_allowlist.py` de propósito (o diff denuncia).
- "Card ativo" tem uma definição: `ATIVO_WHERE` / `ativo_where(alias)` / VIEW `flashcards_ativos` / `ativos()`. Não reescrever o filtro.
- Writer de lote expõe `aplicar=False` no mesmo caminho do apply; o CLI faz dry-run por padrão e COUNT-ASSERT (`--apply --expect N`).
- Devolver tipos simples (`DataFrame`, `dict`, `int`, `bool`), nunca linha crua de cursor.
- Teste nunca toca o `ipub.db` real: `monkeypatch.setattr(db, "DB_PATH", <tmp_path>)`.

## Examples from this codebase
Citar por nome de função, não por linha (o `db.py` passa de 3.000 linhas):
- `get_connection()` e `_ensure_views()` — conexão.
- `ativos()`, `contar_erros_cards()`, `get_preparacao()` — leitura.
- `log_review()`, `set_dificuldade()` — escrita com cursor + commit.
- `set_preparacao()` — UPSERT com DDL preguiçosa.
- `plano_upsert_tarefas(rows, aplicar=True)`, `emed_upsert_questoes(rows, aplicar=True)` — lote com dry-run.
- `record_review()` / `_aplicar_review()` — FSRS com lock otimista.
- `agora()`, `carimbo()`, `hoje()` — relógio único (F80).
<!-- vibeflow:auto:end -->

## Anti-patterns
- `import sqlite3` outside `app/utils/db.py` or an authorized standalone CLI — there is no UI layer anymore (Streamlit was removed, see `AGENTE.md`); every `app/` caller goes through `db.py`
- String interpolation in SQL: `f"SELECT * WHERE id = {user_id}"` — SQL injection risk
- Forgetting `conn.close()` — SQLite WAL mode won't release the file lock
- Returning raw cursor rows from db.py functions — callers would depend on positional column order

## Manual Corrections

**2026-10-10 (M-127, fecho do Lote 0 da Fase 0) -- os dois exemplos canônicos da região gerada acima estão MORTOS.**
`get_db_metrics()` e `update_cronograma_status()` saíram do `app/utils/db.py` na part-4a (`a240f94`),
junto com outras 8 funções sem chamador. E `cronograma_progresso` nunca existiu no schema: o
`UPDATE` do exemplo de escrita falhava calado. Não copie esses dois blocos. Os exemplos vivos de
hoje, copiados do `db.py`:

**Read function (returns DataFrame)** -- `ativos()`, o helper canônico de cards ativos que as
skills citam:
```python
def ativos():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM flashcards_ativos", conn)
    finally:
        conn.close()
```

**Write function (cursor + commit)** -- `log_review()`, chamado por `tools/dormant_refresh.py`:
```python
def log_review(tema_id=None, resumo_path=None, kind='dormant_refresh',
               source='agent', note=None) -> int:
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
```

Na lista "Examples from this codebase", troque `get_db_metrics()` e `update_cronograma_status()`
por `ativos()` e `log_review()`. Trava contra a volta da classe: `tools/test_schema_escrita.py`
(toda tabela escrita existe no schema do `init_db` ou tem DDL lazy). O próximo `analyze` deve
regenerar a região gerada a partir do código e absorver esta correção.
