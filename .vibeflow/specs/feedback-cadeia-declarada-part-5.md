# Spec: Feedback por elo declarado -- part 5: ingestão das declarações no ipub.db

> Escrita em 2026-10-02 (s211). PRD: `.vibeflow/prds/feedback-cadeia-declarada.md` (Scope v0, item 4, parte de dados).

## Objetivo

O que o aluno declara na página (estado de cada elo, grifos, modo, cadeia com defeito) chega ao `ipub.db` pelo registro que já existe e fica consultável por CLI, para a análise e para o mapa de fragilidade.

## Contexto

`emed_banco.py --registrar` -> `db.emed_upsert_respostas` grava hoje `letra, confianca, correta, gabarito, racional, elo, tempo_s, flag, respondido_em, riscadas`. Os campos novos das parts 2-4 (`elos`, `cadeia_defeito`, `modo`, `grifos`) seriam descartados em silêncio -- o mesmo defeito que as `riscadas` tiveram até a s200. E o `--erros` ainda imprime a leitura "o elo em que a letra marcada cai", que o PRD revogou.

**Fricção que esta spec remove:** dado declarado sem porta de consulta -- viciosa.

## Definition of Done

1. **Colunas e upsert.** `emed_respostas` ganha `elos`, `grifos`, `modo` e `cadeia_defeito` (migração idempotente em `_ensure_emed_tables`, como a de `riscadas`). `emed_upsert_respostas` grava: `elos` como JSON canônico de lista (valores só de `sim | incerteza | desatencao | nao | ""`; valor fora do vocabulário = doc em `invalidas`), `grifos` como JSON canônico, `modo` (`estudo | prova | ""`), `cadeia_defeito` = o motivo (texto). Mudança só nesses campos, com o mesmo `respondido_em`, conta como `atualizadas`. Testes: `test_registro_grava_elos_grifos_modo_e_defeito`, `test_elo_fora_do_vocabulario_invalida_o_doc`, `test_registro_e_idempotente_com_os_campos_novos`.
2. **`--erros` com a declaração.** Para cada errada ou não-sólida: cada elo da cadeia numerado com o estado DECLARADO ("[Não]", "[sem declaração]"; certa e sólida sem `elos` = "[presumido Sim]"), os conflitos determinísticos (elo `descartar` com `letra` = letra marcada e declarado `sim`), o motivo de `cadeia_defeito` e os trechos grifados (o texto, não os offsets). A linha "o elo em que a letra cai" só sai para solução v2 SEM declaração, rotulada "legado". Teste: `test_erros_imprime_declarado_e_conflito`.
3. **`--elos [LISTA]`.** Nova flag: uma linha por elo declarado diferente de `sim` (lista, questão, índice, estado, `habilidade` da v3 ou o texto do elo na v2, objetivo), ordenada `nao` -> `incerteza` -> `desatencao`; com `--json`, o mesmo em JSON; sem LISTA, todas. Teste: `test_elos_lista_os_nao_sim_na_ordem`.
4. **`--defeitos`.** Nova flag: as questões com `cadeia_defeito` (lista, número, motivo) -- a fila de correção de cadeia. Teste: `test_defeitos_lista_cadeias_sinalizadas`.
5. **Skill e gates.** As flags novas e os campos novos documentados em `.claude/commands/banco-emed.md` (tabela de flags + linha `respostas/<lista>_<num>` da tabela de coleções), com lápide na leitura pela letra; `sync_skills --check` 0; gate D5 (`cli_signature_check`) verde; `test_writer_allowlist` verde.
6. **Craftsmanship.** `import sqlite3` só em `app/utils/db.py`; `emed_banco.py` segue camada fina (nenhuma SQL nele); suíte inteira verde; nenhuma escrita em `questoes_erros`, `flashcards` ou FSRS por estas flags (read-only fora do upsert).

## Scope

**Arquivos (4):** `app/utils/db.py` · `tools/emed_banco.py` · `tools/test_emed_banco.py` · `.claude/commands/banco-emed.md` (+ espelho).

## Anti-scope

- Gerar card ou linha no ledger de habilidades automaticamente (part-6 dá o rito; a escrita segue pelos writers existentes, acionados pelo agente).
- Painel/hub mostrando esses dados entre listas (faixa de padrões: pós-v0).
- Recalcular `--por-objetivo` com base nos elos.
- Tocar `tools/hub.py`, a página ou o tique do `/hub-backend`.

## Technical Decisions

- **JSON em coluna TEXT** (como `extras`): os campos são lidos inteiros, nunca filtrados por SQL; tabela-filha por elo seria modelagem antes da hora (o ambiente próprio, pós-v0, é o lugar dela).
- **Ausente = presumido só na leitura:** o banco guarda o que foi declarado; a presunção é regra de exibição, declarada no `--erros`.
- **Valor estranho invalida o doc:** o db da página é entrada não confiável (conta compartilhada, todo visitante é owner); mesma régua da `confianca`.

## Applicable Patterns

- `patterns/db-access-layer.md`; rito de lote do `AGENTE.md §10.7` (dry-run, `--apply`, `--expect`) -- já embutido no `--registrar`.
- `patterns/warn-first-check.md` (D5).

## Risks

- **Resposta antiga re-registrada perder campo:** o upsert só compara/atualiza; ausente no doc = "" no banco, e os docs antigos não têm os campos. Coberto pelo teste de idempotência.
- **Offsets de grifo sem o texto da questão** (questão podada): o `--erros` imprime o trecho só quando o texto existe; senão, cala.

## Dependencies

- `.vibeflow/specs/feedback-cadeia-declarada-part-4.md`
