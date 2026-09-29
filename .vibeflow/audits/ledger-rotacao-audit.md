# Audit Report: rotação do ledger (parts 1, 2 e 3)

**Data:** 2026-09-28 (s204) · **HEAD base:** `6c32845` · **Specs:** `.vibeflow/specs/ledger-rotacao-part-{1,2,3}.md`

**Verdict: PASS**

## DoD Checklist

### Part 1 -- mover e enxergar

- [x] **1. Só o resolvido sai, e cada bloco se conserva.** `test_rotacao_move_so_os_resolvidos_e_conserva_cada_bloco` (11 testes vermelhos antes: o módulo não tinha as funções).
- [x] **2. Idempotência, dry-run, COUNT-ASSERT.** `test_rotacao_e_idempotente`, `test_dry_run_nao_escreve`, `test_expect_errado_recusa_sem_escrever`.
- [x] **3. Continuação e resíduo.** `test_continuacao_viaja_com_o_pai`, `test_mitigado_e_parcial_ficam_na_frente`.
- [x] **4. O selo lista tudo que está aberto.** `test_selo_lista_todo_item_em_aberto`; saída real: 19 itens, com GATE e DECLARADO.
- [x] **5. Migração do ledger real com prova de conservação.** 125 blocos F com sha256 conservado; 153 segmentos não abertos no histórico, byte a byte, na ordem; conta de bytes fecha (403.134 = 348.996 + 54.138); total de achados 124 = 124; rotacionar sobre o resultado move zero.
- [x] **6. Suíte e harness.** 1245 passed; `auto_check --changed` PASSED.

### Part 2 -- leitores e o gate

- [x] **1. `test_resolvido_na_frente_e_achado`, `test_aberto_no_historico_e_achado`.**
- [x] **2. `test_indice_velho_e_achado`.**
- [x] **3. `test_status_le_os_dois_arquivos`** (G14 e G14b).
- [x] **4. `test_repo_real_consistente`** verde depois da migração; o check `frente` entra por ele e bloqueia.
- [x] **5. Avisos** de `auto_check.py` (F38, F89) e `habilidades.py` (F38) apontam `history/auditoria/resolvidos.md`.
- [x] **6. Suíte e harness.**

### Part 3 -- portadores

- [x] **1. `AGENTE.md`:** fechamento (3, item 4), co-edição (10.1) e memória da auditoria (10.9) descrevem o par e a busca antes de escrever achado novo.
- [x] **2. `/engenharia-cli`:** `--rotacionar`, `--apply`, `--expect`, `--onde`; `sync_skills --check` 0; D5 PASSED.
- [x] **3. `registrar-sessao.md`:** passo 5b.
- [x] **4. `README.md` e `docs/MEMORIA-AUDITORIA.md`.**
- [x] **5. `revisao-calibrada-contract.md`:** a citação por número de linha virou citação por id.
- [x] **6. Suíte, harness e `selo.py`:** fecha, 0 discordâncias, 0 fora do lugar.

## Pattern Compliance

- [x] `warn-first-check` -- o índice é gerado entre marcadores e conferido contra o derivado; nada digitado.
- [x] `agent-workflow-protocol` -- skill no canônico, espelho regenerado.

## Critical Gate

Clean -- no destructive operations detected. O rotacionador escreve dois arquivos Markdown versionados; nenhuma regra do catálogo disparou.

## Desvios declarados

- **`tools/doc_drift.py` NÃO mudou** (estava no escopo da part 2). `test_allowlist_e_exatamente_os_4_docs_de_estado` prende a lista do sensor nos 4 documentos de estado, de propósito. O ledger não tem anotação `drift-check` ativa; o item saiu.
- **`FEITO (parcial)` aparece como `MITIGADO`** na lista de abertos e no índice: vale o nome do cabeçalho.
- **Tabela gerada de `AGENTE.md` 7.4:** 2 linhas regeneradas (check G5).

## Resíduos

- Docstrings e comentários que citam achado resolvido pelo nome do arquivo da frente (`day_plan.py`, `db.py`, `state_utils.py`): seguem resolvíveis pelo preâmbulo da frente e por `selo.py --onde`.
- `docs/MEMORIA-AUDITORIA.md` §3 e §3b: retrato de 17/09, até o F113.
- "Quem decide" é heurística sobre o texto do status; F129 sai como `engenharia` e o texto diz que o veredito é do operador.
- As seções "Evidencias novas para achados abertos" (2) foram para o histórico junto da narrativa da sessão em que nasceram.
