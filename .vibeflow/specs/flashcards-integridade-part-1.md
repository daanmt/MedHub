# Spec: flashcards-integridade-part-1 — P0: contrato de geração, vazamentos e FK enforcement

> De: `.vibeflow/prds/flashcards-integridade-geracao.md` · Gerado 2026-08-14 (ai-eng)
> Ordem: 1ª de 6. Sem dependências.

## Objective

Nenhum card volta a ser cunhado por heurística silenciosa: `insert_questao.py` sem `cards` **falha alto**, os dois vazamentos de fila conhecidos fecham, e as FKs declaradas passam a ser impostas.

## Context

Incidente 2026-08-13: lote de 34 registros sem `cards` → 68 cards de template, 0 detectados. O caminho heurístico (`insert_questao.py:172-206`) gera template banido pela spec (`estilo-flashcard.md:26`), embute `titulo` na pergunta e reintroduz `needs_qualitative=1` (`:210`). `cards: []` cai no branch "SEM card" com mensagem `[GATE-EVIDENCIA]` falsa (`:153`, `:250-252`). `get_fresh_error_cards` (`db.py:100-121`) não filtra `needs_qualitative` — aposentado reaparece. `cards_regen_queue.py:47` usa `nq != 2` (nq=3 voltaria como ativo). `get_connection()` (`db.py:22`) nunca liga `PRAGMA foreign_keys` — as 6 cláusulas `REFERENCES` do DDL são decorativas (verificado no `sqlite_master` 2026-08-14; 0 órfãos hoje — ligar é seguro).

## Definition of Done

1. [ ] `insert_questao` (single e `--errors-file`): item sem `cards` E sem par `frente_pergunta`+`verso_resposta` explícito → `ValueError`/exit≠0 citando `.claude/commands/estilo-flashcard.md`; **zero linhas gravadas** (transação intacta — teste conta linhas antes/depois). `cards: []` → mesmo erro. Item `status in ('anulada','banca-divergente')` → registra erro sem card com a mensagem `[GATE-EVIDENCIA]` (único branch onde ela aparece).
2. [ ] Caminho heurístico removido: `grep -r "qual a conduta/criterio correto" tools/` e `grep -r "Qual o distrator tipico" tools/` retornam vazio; `frente_elo`/`verso_elo` e o regex de `trigger` não existem mais; todo card inserido tem `quality_source='qualitative'` e `needs_qualitative=0`.
3. [ ] `get_fresh_error_cards` filtra `COALESCE(f.needs_qualitative,0) < 2` — teste com fixture: card aposentado dentro da janela de 48h NÃO retorna; card ativo retorna.
4. [ ] `cards_regen_queue.py` usa `COALESCE(needs_qualitative,0) < 2` como definição de ativo (nq=3 hipotético fica fora — teste).
5. [ ] `db.get_connection()` e as conexões próprias de `insert_questao.py` (`:121`, `:330`) retornam `PRAGMA foreign_keys` == 1 (teste); INSERT de `fsrs_cards` com `card_id` inexistente falha com `IntegrityError` (teste).
6. [ ] `tools/check_fk_orphans.py` (novo, read-only, `mode=ro`) reporta as 5 varreduras de órfãos (fsrs_cards→flashcards, revlog→fsrs_cards, flashcards→questoes_erros, flashcards→taxonomia, flashcards sem fsrs_cards) como WARN e sai exit 0; registra no ledger via `ledger_self` se disponível (padrão warn-first).
7. [ ] Craftsmanship: `pytest` na raiz verde (baseline 115 passed + novos); nenhum Don't de `conventions.md` violado (sqlite3 só em db.py/CLIs standalone; `finally: conn.close()`; pt-BR; parametrização `?` em todo SQL novo).

## Scope

- `tools/insert_questao.py` — remoção do branch heurístico; contrato de erro; modo de flags individuais (`frente_pergunta`+`verso_resposta` presentes) vira card qualitativo único pelo MESMO caminho A (validação de presença já existente `:159-162`); PRAGMA nas 2 conexões próprias.
- `app/utils/db.py` — PRAGMA na fábrica; filtro nq em `get_fresh_error_cards`.
- `tools/cards_regen_queue.py` — definição de ativo.
- `tools/check_fk_orphans.py` — novo.
- `tools/test_insert_questao.py` — novo (fixture SQLite em tmp_path com schema mínimo real das 4 tabelas + taxonomia; monkeypatch de `DB_PATH` em `insert_questao` e `db`).

## Anti-scope

- NÃO deletar os 139 cards `heuristic` nem tocar dados existentes.
- NÃO mudar defaults de dry-run de nenhum CLI.
- NÃO adicionar CHECK constraints (rebuild de tabela — decisão nq=1 pendente do lado MedHub).
- NÃO tocar o docstring/`--help` além do necessário para o novo contrato.
- NÃO tocar `--pre-bloco` em `fsrs_queue.py` (herda o filtro corrigido de graça).
- NÃO tocar conteúdo clínico; fixtures com texto dummy.

## Technical Decisions

- **Falhar alto > opt-in**: contrato s076 já "aposentou" a heurística e ela voltou; só remoção de código segura. Callers reais (grep em `.claude/commands/` + `.agents/`) são todos agent-first — nada quebra.
- **Modo flags individuais preservado**: `frente_pergunta`+`verso_resposta` explícitos são autoria qualitativa legítima (CLI single). Convergir para o caminho A (montar `cards=[{...}]` internamente) em vez de manter dois caminhos.
- **PRAGMA por conexão** (SQLite exige): na fábrica `db.get_connection()` + nas conexões standalone de `insert_questao`. Demais writers ganham na part-4. Conexões `mode=ro` não precisam (não escrevem).
- **Órfãos: report, não delete** — limpeza de dado é decisão do lado MedHub (PRD open question 3). Hoje 0 órfãos; o script existe para detectar regressão.
- **Trade-off aceito**: FK ON pode fazer um DELETE futuro de `flashcards` falhar alto se houver `fsrs_cards`/`revlog` filhos — é o comportamento desejado (integridade explícita); `cleanup_db.py` não está no escopo e será ajustado se/quando falhar.

## Applicable Patterns

- `patterns/db-access-layer.md` — fábrica única, `?` params, close explícito.
- `patterns/error-insertion-pipeline.md` — pipeline erro→card preservado no caminho A.
- `patterns/warn-first-check.md` — `check_fk_orphans` nasce WARN, lógica em módulo próprio, ledger.
- Convenções: pt-BR, argparse, mensagens humanas no stdout, return bool.

## Risks

- **R1**: algum workflow `.agents/` dependa do fallback sem `cards` → mitigação: grep prévio mostrou todos passam `cards`; se um lote legado falhar, a mensagem de erro instrui exatamente o que falta (fail-loud é o comportamento pedido pelo handoff §7.1).
- **R2**: PRAGMA quebrar INSERT existente com FK inválida → mitigação: 0 órfãos hoje; `get_or_create_tema` garante parent; teste de IntegrityError cobre o caminho.
- **R3**: fixture de teste divergir do schema real → mitigação: DDL da fixture copiado do `sqlite_master` real (verificado 2026-08-14).
