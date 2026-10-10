# Spec: medhub Fase 0 · Lote 0 — Part 2c: os acoplados fora do núcleo do pytest

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/E-testes-harness.md` §P7 Classe 1 (itens 4, 12, 13) e §Allowlist × arquivos
> Parte 2c (de 7). Pode correr em paralelo com a 2b, depois da 2a.
> Repo-alvo: medhub (implement + audit no loop vibeflow dele). Código conferido em leitura @ `6d0239a`.

## Objective

Os três acoplados ao dado vivo que rodam por caminhos laterais (golden t3 do EMED, o script `test_revisao_calibrada` via bridge e a telemetria do day_plan via `auto_check`) passam a separar o que é hermético do que é vivo, sem ler o `ipub.db` real em silêncio.

## Context

- `tools/test_emed_api.py:449-464` (`test_golden_t3_saude_do_idoso`): lente 1 compara a captura gitignored `tmp/emed_api/t3/questoes` (skip sem ela); lente 2 lê `db.emed_listar_questoes("t3")` no banco real e exige `(30, {}, [], [])`. As duas lentes vivem na mesma função: edição de questão no banco quebra a lente 1 junto.
- `tools/test_revisao_calibrada.py:78-83` (`test_seed`): script-style (fora do `python_files`; roda só como 1 teste do `test_pytest_bridge`, por exit code). Lê `db.get_dificuldade(...)` com o `DB_PATH` real e exige a nota do `SEED`; o comentário `:46-55` registra que o SEED já foi encolhido 3 vezes porque temas avançam no fluxo normal. As funções de `:69`, `:86`, `:209` usam cópia do banco.
- `tools/test_day_plan_telemetria.py:55-63` (`test_header_distingue_pool_divida`): unittest, fora do `python_files`, roda só pelo check 3 do `auto_check` quando `day_plan` é tocado. Faz `day_plan.render(day_plan.build())` sobre o banco vivo (`skipTest` sem banco).

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: teste que muda de veredito porque o operador estudou. Nenhuma fricção virtuosa é tocada.

## Definition of Done

1. [ ] `test_emed_api.py`: a lente 2 (banco) vira função própria marcada `@pytest.mark.vivo`, com `pytest.skip("VIVO: ...")` sem banco ou sem a t3; a lente 1 (captura) continua com o skip declarado de hoje e não toca o banco.
2. [ ] `test_revisao_calibrada.py`: nenhuma função lê o `ipub.db` real. O `test_seed` roda sobre banco sintético criado pelo próprio script (`init_db` em diretório temporário + o `SEED` inserido), com `db.DB_PATH` apontado para lá antes da primeira chamada e uma asserção no script que confere isso. `python tools/test_revisao_calibrada.py` sai 0 e `python -m pytest tools/test_pytest_bridge.py -q` passa.
3. [ ] `test_day_plan_telemetria.py::test_header_distingue_pool_divida` roda sobre banco sintético semeado com cards novos e devidos (pool e dívida), com `db.DB_PATH` apontado para ele, e o cabeçalho contém `pool` e `nunca introduzidos`. Se o `build()` não montar sobre o schema sintético, o teste fica com `skipTest("VIVO: ...")` explícito e o audit registra por quê. `python tools/test_day_plan_telemetria.py` sai 0.
4. [ ] Suíte completa `python -m pytest tools/ -q` verde (o bridge inclui o script do DoD 2).
5. [ ] Nenhuma violação dos Don'ts de `.vibeflow/conventions.md`; os docstrings dos três dizem o que é hermético e o que é vivo.

## Scope

`tools/test_emed_api.py`, `tools/test_revisao_calibrada.py`, `tools/test_day_plan_telemetria.py`. **Budget: 3 arquivos.**

## Anti-scope

- **Fronteiras:** design no ai-eng, implementação no medhub.
- **Nada que mude conteúdo clínico, FSRS ou o hub publicado:** `tools/emed_api.py`, `tools/day_plan.py`, `app/utils/db.py` e o `SEED` (valores) não mudam.
- Não colocar os scripts no `python_files` (eles imprimem checks; coleta crua viraria verde decorativo — `pytest.ini:3-6`). Não mexer no `test_pytest_bridge.py` nem no check 3 do `auto_check`.
- Não reescrever os scripts para pytest-nativo.

## Technical Decisions

1. **Separar lentes em funções** em vez de um skip no meio: o resultado de cada lente fica legível no relatório.
2. **Script-style ganha banco próprio**, não marcador: marcadores de pytest não valem quando o arquivo roda como script.
3. **Fallback declarado** no DoD 3: se o `build()` exigir tabelas/linhas que o schema sintético não tem, a saída honesta é skip explícito com motivo — nunca `return`.

## Applicable Patterns

- `tools/test_fuso_unico_leitores.py:48-62` (banco canônico via `init_db` em `tmp_path`).
- Funções de `test_revisao_calibrada.py` que já usam cópia do banco (`:69`, `:86`, `:209`): mesma técnica, agora sem partir do banco real.
- Convenção `VIVO:` da part-2a.

## Risks

- **"O SEED sintético deixa de provar o que o real provava."** → O que se testa é a regra de leitura (`get_dificuldade` devolve nota e fonte gravadas); o estado do operador não é invariante de código.
- **"`build()` precisa de muitas tabelas."** → `init_db` cria o schema canônico; o seed mínimo é cards em `flashcards`/`fsrs_cards`. Se não bastar, vale o fallback do DoD 3.

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-2a.md` (convenção `VIVO:` e marcador `vivo`).
