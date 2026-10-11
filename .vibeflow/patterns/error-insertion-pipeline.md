---
tags: [error-tracking, sqlite, flashcards, cli, data-ingestion, ipub]
modules: [tools/, app/utils/]
applies_to: [scripts, commands, data-ingestion]
confidence: inferred
status: active
canonical_source: tools/insert_questao.py module docstring; .claude/commands/analisar-questao.md §9
last_verified: 2026-08-25
---
# Pattern: Error Insertion Pipeline

<!-- vibeflow:auto:start -->
## What
O caminho canônico para registrar uma questão errada: `tools/insert_questao.py` grava, numa transação de commit único, o tema em `taxonomia_cronograma` (se novo), o erro em `questoes_erros`, os cards em `flashcards` e o estado FSRS inicial em `fsrs_cards`. Os cards são cunhados pelo agente e passam pelo gate de qualidade antes de qualquer INSERT; não existe mais geração heurística.

## Where
- `tools/insert_questao.py` — o writer (modo single, `--cards-file`, lote `--errors-file`, pré-check `--errors-file ... --dry-run`).
- `app/utils/card_checks.py` — `validar_card()` e `checar_distrator()`, o gate de cunhagem.
- `app/utils/areas.py` — `validar_area()`, a precondição de `--area` (vocabulário em `core/areas.json`).
- `app/utils/db.py` — relógio único (`db.agora()`, `db.carimbo()`), `db.emed_chave()` e `db.emed_ligar_erro()` (vínculo com a aba Questões do hub).
- `tools/utils/lastro.py` — `tem_lastro()`, por trás do aviso `[SEM-LASTRO]`.
- `.claude/commands/analisar-questao.md` §9 — assinatura canônica (8 obrigatórios + opcionais) e mapa argumento -> coluna; `.agents/workflows/analisar-questoes.md` aponta para lá.
- Volume de questões (feitas/acertos) NÃO passa por aqui: é `tools/registrar_sessao_bulk.py` (`sessoes_bulk`).

## The Pattern

**Invocação single (forma de `.claude/commands/analisar-questao.md` §9):**
```bash
python tools/insert_questao.py \
  --area "<subespecialidade real, valor já existente na taxonomia>" \
  --tema "<tema>" --titulo "<título curto>" \
  --enunciado "<enunciado limpo>" \
  --correta "<texto da correta>" --marcada "<texto marcado>" \
  --erro "<tipo>" --elo "<habilidade que faltou>" --armadilha "<distrator>" \
  --habilidades "<Hab 1 -> Hab 2>" --faltou "<conceito>" --explicacao "<regra mestre>" \
  --frente_contexto "..." --frente_pergunta "...?" --verso_resposta "..." \
  --verso_regra_mestre "..." --verso_armadilha "..." \
  [--cards-file cards.json] [--status anulada|banca-divergente] [--sessao ID] [--emed LISTA_NUM]
```

**Contrato de cunhagem, PURO e antes de qualquer escrita (`avaliar_cunhagem`, trecho):**
```python
    if status in ("anulada", "banca-divergente"):
        # F26: anulada/banca-divergente registra o ERRO mas NAO cunha card.
        return {"cards": [], "tuplas": [], "erros": [], "avisos": [],
                "sem_cards": False}
    if cards is None and frente_pergunta and verso_resposta:
        # Modo flags individuais (CLI single): converge para o caminho unico.
        cards = [{
            "tipo": "elo_quebrado",
            ...
        }]
    if not cards:
        return {"cards": [], "tuplas": [], "erros": [], "avisos": [],
                "sem_cards": True}
    ctx = {"titulo": titulo, "tema": tema, "area": area}
    erros, avisos, tuplas = [], [], []
    for i, c in enumerate(cards):
        res = card_checks.validar_card(c, contexto=ctx)
        erros += [f"card {i}: {e_}" for e_ in res["erros"]]
        avisos += [f"card {i}: {a_}" for a_ in res["avisos"]]
```
`insert_questao()` levanta `ValueError(MSG_SEM_CARDS)` sem cards e `ValueError(MSG_GATE_REPROVOU + ...)` com `erros`; `avisos` saem como `[AVISO-CARD]` e não bloqueiam.

**Transação (dentro de `insert_questao()`, trecho):**
```python
        if own_conn:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON")  # part-1: FKs do schema impostas
        cursor = conn.cursor()
        _ensure_status_column(cursor)
        _ensure_sessao_column(cursor)
        ...
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE area = ? AND tema = ?", (area, tema))
        ...
        cursor.execute('''
            INSERT INTO questoes_erros
            (tema_id, titulo, complexidade, enunciado, alternativa_correta, alternativa_marcada,
             tipo_erro, habilidades_sequenciais, o_que_faltou, explicacao_correta, armadilha_prova, status,
             data_registro, sessao_bulk_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tema_id, titulo, complexidade, enunciado, correta, chamada,
              erro, habilidades, faltou, explicacao, armadilha, status,
              db.carimbo(),    # F80: relogio unico (LOCAL), nunca o DEFAULT UTC
              int(sessao) if sessao is not None else None))
        questao_id = cursor.lastrowid
        if emed_lista is not None:
            db.emed_ligar_erro(conn, emed_lista, emed_num, questao_id)
        for tipo_card, fc_, fp_, vr_, vrm_, va_ in cards_to_insert:
            cursor.execute('''
                INSERT INTO flashcards (questao_id, tema_id, tipo,
                                        frente_contexto, frente_pergunta, verso_resposta,
                                        verso_regra_mestre, verso_armadilha,
                                        quality_source, needs_qualitative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'qualitative', 0)
            ''', (questao_id, tema_id, tipo_card,
                  fc_, fp_, vr_, vrm_, va_))
            card_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO fsrs_cards (card_id, state, due)
                VALUES (?, 0, ?)
            ''', (card_id, db.agora()))
        ...
        if own_conn:
            conn.commit()
            _flush_eventos()
```

**Lote (`insert_batch`):** valida campos obrigatórios, `status` e vínculos de todos os itens ANTES da transação; pula por dedupe de conteúdo `(area, tema, TRIM(enunciado))`; chama `insert_questao(..., conn=conn)` em cada item; qualquer exceção -> `conn.rollback()`, zero gravado.

## Rules
- `--area` passa por `areas.validar_area()` antes de tudo: área fora de `core/areas.json` é recusada, nunca normalizada.
- Todo erro válido exige cards: `--cards-file` (N cards atômicos, régua em `.claude/commands/estilo-flashcard.md`) ou o par `--frente_pergunta` + `--verso_resposta`. Sem isso o insert falha. O fallback heurístico foi removido (incidente dos 68, 2026-08-13).
- `--status anulada|banca-divergente` registra o erro SEM card (não é lacuna real) e imprime `[GATE-EVIDENCIA]`.
- Todo card nasce `quality_source='qualitative'`, `needs_qualitative=0`, e ganha linha em `fsrs_cards` com `state=0`.
- `taxonomia_cronograma`: cria `(area, tema)` se não existir e atualiza só `ultima_revisao`. `questoes_realizadas` e `questoes_acertadas` NÃO mudam aqui (volume = `registrar_sessao_bulk.py`).
- `--elo` não tem coluna: alimenta só o matcher de reincidência (F25). O elo persistido é `o_que_faltou` (via `--faltou`).
- Carimbos por `db.carimbo()` / `db.agora()` (F80), nunca pelo DEFAULT UTC do SQLite.
- Vínculos opcionais na mesma transação: `--sessao` (id da LINHA de `sessoes_bulk`, nunca o `sessao_num`) e `--emed` (resposta da aba Questões). Vínculo recusado = nada gravado.
- Pós-commit, só informativos (nunca mudam o resultado): `[REINCIDENCIA]` (F25) e `[SEM-LASTRO]` (F31). Eventos `generation`/`reincidencia` só vão para o `event_log` depois do commit.
- Lote: uma transação para o arquivo inteiro, rollback total em qualquer falha; `--dry-run` só existe com `--errors-file` e não abre conexão.
- Exit code: 0 em sucesso, 1 em falha, nos dois modos (F27).
- `DB_PATH` do CLI: `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`; o perímetro de tabelas dele está em `tools/test_writer_allowlist.py`.

## Examples from this codebase
- `tools/insert_questao.py::avaliar_cunhagem` — contrato de cunhagem puro, usado pelo writer e pelo pré-check (F107).
- `tools/insert_questao.py::insert_questao` — a transação; com `conn=` externa não abre, não commita, não fecha e propaga a exceção.
- `tools/insert_questao.py::insert_batch` / `checar_lote` — lote transacional e pré-check read-only.
- `tools/insert_questao.py::checar_reincidencia` — matcher lexical F25 (`LIMIAR_OVERLAP = 0.5`).
- Testes: `tools/test_insert_questao.py`, `tools/test_batch_insert.py`, `tools/test_insert_dry_run.py`, `tools/test_reincidencia.py`, `tools/test_insert_questao_vinculo.py`, `tools/test_writer_gates.py`.
<!-- vibeflow:auto:end -->



## Anti-patterns
- Inserting errors directly in the DB without going through `insert_questao.py` — bypasses FSRS init and metrics update
- Passing `--frente_pergunta` without `--verso_resposta` (or vice versa) — only one won't trigger qualitative path
- Updating `taxonomia_cronograma.questoes_acertadas` manually — this is managed by the ETL import script, not by error insertion


## Manual Corrections

**2026-10-10 (M-127, fecho do Lote 0 da Fase 0):** a linha "`cronograma_progresso` status set to
'Concluído' via fuzzy LIKE match on tema name" da região gerada acima está **morta**. A tabela
nunca existiu no schema, e o bloco `try/except: pass` que a escrevia saiu do `insert_questao.py`
na part-4a (`a240f94`). O `insert_questao` não marca conclusão de cronograma: a conclusão de
tarefa é coluna de `plano_tarefas`, escrita por `tools/plano.py`. Trava: `tools/test_schema_escrita.py`.
