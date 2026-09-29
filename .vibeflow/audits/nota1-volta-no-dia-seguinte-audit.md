# Audit Report: nota 1 volta no dia seguinte (parts 1, 2 e 3)

**Data:** 2026-09-28 (s204) · **HEAD base:** `eaaae16` · **Specs:** `.vibeflow/specs/nota1-volta-no-dia-seguinte-part-{1,2,3}.md`

**Verdict: PASS**

> Um relatório e um commit para as 3 parts, como a part 3 decide: o rito dos 3 passos exige
> declaração, lápide e cadastro no mesmo commit do código que muda a norma.

## DoD Checklist

### Part 1 -- motor

- [x] **1. Check "Again em Review fica em Review", escrito antes e visto vermelho.** `tools/test_fsrs.py` check 4. Vermelho: `[FAIL] 4. Again em Review -> fica em Review (2)` e `due >= 1 dia`. Verde depois do fix.
- [x] **2. Propriedade estado x nota.** Check 7. O vermelho listou os casos: nota 1 -> 10 min; nota 2 sobre estado 3 -> 15 min (o loop). Verde: nenhuma combinação devolve o card no mesmo dia.
- [x] **3. Fonte única dos argumentos.** `test_scheduler_do_otimizador_usa_os_kwargs_de_producao` (vermelho: `relearning_steps` com 600 s). `tools/fsrs_optimize.py` importa `KWARGS_BASE` de `app/utils/fsrs.py`.
- [x] **4. Golden.** Scheduler antigo x novo sobre as mesmas entradas, cópia do banco, 3.589 linhas: S e D idênticos em todas; `state`/`due` diferem em 362, todas de nota 1 ou 2 sobre estado 2 ou 3 (279 + 57 + 26). Zero diferenças fora do esperado. Script: `tmp/f140_auditoria/golden_part1.py`.
- [x] **5. `.vibeflow/index.md` e `conventions.md`** descrevem o Scheduler com `relearning_steps=()` e a fonte única.
- [x] **6. Suíte e harness.** `auto_check --changed` PASSED, suíte completa verde.

### Part 2 -- novos do lote = saldo

- [x] **1. `test_export_sem_new_limit_enche_o_saldo_com_novos`.** Vermelho reproduziu o episódio: `assert 13 == 53`. Verde: 3 + 50.
- [x] **2. `test_new_limit_explicito_vence_o_saldo`.** 3 + 5.
- [x] **3. `test_fila_do_chat_segue_com_10_novos`.** `--list` e `--next` pedem 10.
- [x] **4. Conferência contra o banco real, read-only.** Export com `--out` no scratch: `total` 53, `teto` 53, `consumo_hoje` 47.
- [x] **5. Docstring com os 4 buckets.** `test_docstring_do_modulo_lista_os_quatro_buckets_na_ordem_da_funcao`.
- [x] **6. Suíte e harness.** Idem part 1.

### Part 3 -- portadores

- [x] **1. `revisao-calibrada-contract.md` v1.9.** Linha da nota 1 reescrita, lápide de linha única, frontmatter igual ao corpo.
- [x] **2. `fsrs-management-contract.md` v1.6.** Estado 3 como legado, novos do lote = saldo, 4 buckets, changelog.
- [x] **3. Skills.** `revisar.md` e `hub-backend.md`; `sync_skills --check` sai 0.
- [x] **4. Termos cadastrados.** 4 marcadores em `docs/MEMORIA-AUDITORIA.md`; `check_contrato_revogado()` devolve lista vazia.
- [x] **5. Ledger.** F140 e F32 RESOLVIDOS; `selo.py` com 0 discordâncias.
- [x] **6. Suíte e harness.** Idem.

## Pattern Compliance

- [x] `db-access-layer` -- nenhum acesso novo a banco; `fsrs_queue.py` segue sem `sqlite3` (`test_fsrs_queue_nao_ganhou_tabela_nova` verde).
- [x] `agent-workflow-protocol` -- skills editadas no canônico, espelhos regenerados.
- [x] `warn-first-check` -- nenhum sensor novo; 3 cláusulas novas anotadas com `CHECK`; órfãs em 124, abaixo da base 127 da catraca (tinham subido a 129 antes da anotação).

## Convention Violations

- Nenhuma.

## Critical Gate

Clean -- no destructive operations detected. Diff de 18 arquivos varrido (linhas adicionadas e removidas); nenhuma regra do catálogo disparou; nenhum `import sqlite3` novo.

## Desvios declarados

- **Orçamento da part 1: 7 arquivos, 1 acima.** O sétimo é uma linha da tabela GERADA de `AGENTE.md` 7.4: o check G5 acusou a tabela como velha porque `fsrs_optimize.py` ganhou um referenciador. Regeneração mecânica, não decisão.
- **De carona na part 3:** os números do regime de dívida em `fsrs-management` (60/90 -> 100/150), redação velha desde a s196.

## Resíduos

- Os 4 cards ativos que já estavam em estado 3 com `due` em 28/09 não foram migrados; amanhecem `atrasados`.
- `AGENTE.md` 6 (balanceador) ainda chama os passos de relearning de "intra-sessão".
- `docs/FUNDAMENTOS-APRENDIZAGEM.md:89` lista 3 buckets; é documento explicativo, fora do gate.
- F141 e F142 seguem abertos.
