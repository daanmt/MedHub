---
tags: [error-tracking, sqlite, flashcards, cli, data-ingestion, ipub]
modules: [tools/, app/utils/]
applies_to: [scripts, commands, data-ingestion]
confidence: inferred
---
# Pattern: Error Insertion Pipeline

<!-- vibeflow:auto:start -->
## What
The canonical pipeline for registering a wrong answer: one CLI call to `tools/insert_questao.py` atomically creates an entry in `questoes_erros`, 1-2 flashcards in `flashcards`, initializes FSRS state in `fsrs_cards`, and updates `taxonomia_cronograma` metrics.

## Where
- `tools/insert_questao.py` — the CLI entry point
- `app/utils/db.py` — `record_review()` for FSRS updates post-registration
- `.agents/workflows/analisar-questoes.md` — agent workflow that invokes this pipeline
- `.claude/commands/analisar-questao.md` — skill spec for Claude

## The Pattern

**CLI invocation (from agent workflow):**
```bash
python tools/insert_questao.py \
  --area "Clínica Médica" \
  --tema "Insuficiência Cardíaca" \
  --titulo "IC Descompensada - Betabloqueador" \
  --enunciado "Paciente com IC FEVE 30%..." \
  --correta "Manter betabloqueador" \
  --marcada "Suspender betabloqueador" \
  --erro "Conceitual" \
  --elo "Não sabia que betabloqueador deve ser mantido em descompensação" \
  --armadilha "Confundir instabilidade hemodinâmica com descompensação leve" \
  --habilidades "Conhecer indicações de suspensão de betabloqueador em IC" \
  --explicacao "Betabloqueador melhora mortalidade mesmo em IC descompensada..." \
  --frente_pergunta "Na IC descompensada sem instabilidade, betabloqueador deve ser..." \
  --verso_resposta "Mantido — suspender apenas em choque cardiogênico ou bradicardia sintomática" \
  --verso_regra_mestre "Betabloqueador reduz mortalidade em ICFEr; suspender APENAS se instabilidade grave" \
  --verso_armadilha "Examinador descreve 'piora' para induzir suspensão indevida"
```

**Atomic transaction inside `insert_questao()`:**
```python
# 1. Upsert tema in taxonomia_cronograma
cursor.execute("SELECT id FROM taxonomia_cronograma WHERE tema = ?", (tema,))
row = cursor.fetchone()
if row:
    tema_id = row[0]
else:
    cursor.execute('''
        INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, ...)
        VALUES (?, ?, 0, 0, 0, ?)
    ''', (area, tema, datetime.now().strftime('%Y-%m-%d')))
    tema_id = cursor.lastrowid

# 2. Insert questao_erro (always 1 per call)
cursor.execute('''
    INSERT INTO questoes_erros
    (tema_id, titulo, complexidade, enunciado, alternativa_correta, alternativa_marcada,
     tipo_erro, habilidades_sequenciais, o_que_faltou, explicacao_correta, armadilha_prova)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (...))
questao_id = cursor.lastrowid

# 3. Generate 1-2 flashcards (elo_quebrado always, armadilha if len > 20)
for tipo_card, frente, verso, fc_, fp_, vr_, vrm_, va_, qs_ in cards_to_insert:
    needs_q = 0 if qs_ == 'qualitative' else 1
    cursor.execute('INSERT INTO flashcards (...) VALUES (...)', (...))
    card_id = cursor.lastrowid
    # 4. Init FSRS state for each card
    cursor.execute('INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, ?)',
                   (card_id, datetime.now()))

# 5. Update taxonomy metrics
cursor.execute('''
    UPDATE taxonomia_cronograma
    SET questoes_realizadas = questoes_realizadas + 1, ultima_revisao = ?
    WHERE id = ?
''', (...))

conn.commit()  # Single commit — all or nothing
```

**Quality source determination:**
```python
use_qualitative = all([frente_pergunta, verso_resposta])
qual_source_elo = 'qualitative' if use_qualitative else 'heuristic'
needs_q = 0 if qual_source_elo == 'qualitative' else 1
```

## Rules
- One `insert_questao.py` call per wrong question — never batch insert
- `--frente_pergunta` + `--verso_resposta` together → `quality_source='qualitative'`, `needs_qualitative=0`
- Without them → `quality_source='heuristic'`, `needs_qualitative=1` (pending LLM rewrite)
- Card type 2 (armadilha) only created if `len(armadilha) > 20 and armadilha != "N/A"`
- `questoes_realizadas` is incremented even for errors (it tracks questions attempted, not just correct)
- `questoes_acertadas` is NOT updated by `insert_questao` — only by performance import ETL
- `cronograma_progresso` status set to 'Concluído' via fuzzy LIKE match on tema name
- `DB_PATH` in tools: `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`

## Examples from this codebase

File: `tools/insert_questao.py` (lines 44-159)
```python
def insert_questao(area, tema, enunciado, correta, chamada, erro, elo, armadilha,
                   complexidade="Media", habilidades="N/A", faltou="N/A", explicacao="N/A",
                   titulo="Erro sem titulo",
                   frente_contexto=None, frente_pergunta=None,
                   verso_resposta=None, verso_regra_mestre=None, verso_armadilha=None):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # ... [full pipeline above] ...
        conn.commit()
        print(f"Sucesso! Questão '{titulo}' inserida. Flashcard IPUB High-Level [ID: {card_id}] gerado.")
        return True
    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")
        return False
    finally:
        if conn:
            conn.close()
```

File: `tools/insert_questao.py` — heuristic question inversion (lines 18-42)
```python
def _invert_elo_to_question(elo: str, tema: str) -> str:
    """Transforma texto do elo quebrado em pergunta cirúrgica."""
    elo_lower = elo.lower()
    if any(x in elo_lower for x in ['limiar', 'ponto de corte', 'mg/dl', 'bpm']):
        return f"Em {tema}: qual o valor limiar/dose correto para {_extract_key_term(elo)}?"
    if any(x in elo_lower for x in ['antes', 'primeiro', 'prioritário', 'sequência']):
        return f"Em {tema}: qual a sequência correta de conduta? (Dica: a ordem importa)"
    # ... other patterns ...
    elo_clean = elo.rstrip('.').strip()
    return f"{elo_clean}?" if len(elo_clean) > 20 and not elo_clean.endswith('?') else f"Qual a abordagem diagnóstica/terapêutica em {tema}?"
```
<!-- vibeflow:auto:end -->

## Anti-patterns
- Inserting errors directly in the DB without going through `insert_questao.py` — bypasses FSRS init and metrics update
- Passing `--frente_pergunta` without `--verso_resposta` (or vice versa) — only one won't trigger qualitative path
- Updating `taxonomia_cronograma.questoes_acertadas` manually — this is managed by the ETL import script, not by error insertion
