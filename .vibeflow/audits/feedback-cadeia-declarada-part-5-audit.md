## Audit Report: feedback-cadeia-declarada part-5 (ingestão das declarações no ipub.db)

> Auditado em 2026-10-02 (s211), subagente de implementação. Spec: `.vibeflow/specs/feedback-cadeia-declarada-part-5.md`.
> Dependência: part-4 PASS (commit `c0a1649`).

**Verdict: PASS**

### DoD Checklist

- [x] **1. Colunas e upsert.** `_ensure_emed_tables` acrescenta `elos`, `grifos`, `modo`, `cadeia_defeito` (ALTER idempotente, como
  `riscadas`); `_COLUNAS_EMED_R` lê as quatro (banco não migrado -> `NULL AS`, sem DDL). `declaracao_norm(doc)` (pura): `elos` =
  JSON canônico de lista só com `sim|incerteza|desatencao|nao|""`; `grifos` = JSON canônico (`sort_keys`); `modo` em
  `estudo|prova|""`; `cadeia_defeito` = o motivo; fora do vocabulário (incl. `elos` não-lista, `grifos` não-objeto) = `invalidas`.
  Mudança só nesses campos com o mesmo `respondido_em` = `atualizadas`; NULL de linha pré-migração conta igual a "" (doc antigo
  re-registrado segue `iguais`). Testes: `test_registro_grava_elos_grifos_modo_e_defeito`,
  `test_elo_fora_do_vocabulario_invalida_o_doc[4 casos]`, `test_registro_e_idempotente_com_os_campos_novos`. O teste de propriedade
  F133 voltou a exigir `[]` (conjunto `_SEM_DESTINO_ATE_A_PART_5` esvaziado, com lápide).
- [x] **2. `--erros` com a declaração.** Erradas e não-sólidas; cada elo numerado com o estado DECLARADO (`[Sim]`, `[Não]`,
  `[sem declaração]`; certa e sólida sem `elos` = `[presumido Sim]` em `declaracao()`), `CONFLITO no elo k`, `Cadeia com defeito:`,
  `Grifou:` com o TRECHO (intervalo inválido ou texto ausente cala). "o elo em que a letra cai" e "executou o(s) elo(s)" só para v2
  SEM declaração, rotulados `legado:`. Pedido do coordenador: v3 nunca imprime "cai no elo None" (`texto_solucao` v3 sem `elo` nas
  alternativas). Teste: `test_erros_imprime_declarado_e_conflito`.
- [x] **3. `--elos [LISTA]`.** `elos_nao_sim()` + `cmd_elos`: lista, questão, índice, estado, `habilidade` (v3) ou texto do elo (v2),
  objetivo; ordem `nao` -> `incerteza` -> `desatencao`; `--json`; sem LISTA, todas. Teste: `test_elos_lista_os_nao_sim_na_ordem`.
- [x] **4. `--defeitos`.** `defeitos_de_cadeia()` + `cmd_defeitos` (lista, número, motivo; filtro `--lista`). Teste:
  `test_defeitos_lista_cadeias_sinalizadas`.
- [x] **5. Skill e gates.** `banco-emed.md`: linhas `--elos`, `--defeitos`, `--erros` (com lápide da leitura pela letra), `--lista`,
  `--json` e a linha `respostas/<lista>_<num>` (campos + forma no banco). `sync_skills --check` 0; `auto_check --changed`
  -> `Assinatura canonica de CLI (D5)` PASSED; `pytest tools/test_writer_allowlist.py tools/test_cli_assinatura.py` -> 14 passed;
  `emed_banco.py --help` mostra as duas flags.
- [x] **6. Craftsmanship.** `grep "import sqlite3\|execute(" tools/emed_banco.py` -> vazio (camada fina); as flags novas só chamam
  `db.emed_listar_*` (read-only: nada em `questoes_erros`, `flashcards` ou FSRS). Suíte inteira:
  `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> **1345 passed**.

### Pattern Compliance

- [x] `patterns/db-access-layer.md`: SQL e DDL só em `db.py`; parâmetros `?`; writer único `emed_upsert_respostas`.
- [x] Rito de lote (§10.7) intacto: `--registrar` segue dry-run por padrão, `--apply`, `--expect`.
- [x] `patterns/warn-first-check.md` (D5) verde.

### Desvios / decisões

- Seleção do `--erros` alargada de "erradas e chutes" para "erradas e não-sólidas", como o DoD 2 diz: a dúvida certa entra
  (declaração obrigatória nela). Ela aparece como `CERTA (duvida)`; `insert_questao --emed` continua recusando certa não-chute.
- `modo` fora do vocabulário também invalida o doc (a spec só nomeava `elos`; mesma régua da `confianca`).
- `grifos` que não é objeto invalida o doc; objeto vazio grava "".
- `elos_ok`/`elo_letra` da leitura metacognitiva também viraram legado (são a mesma leitura pelas letras revogada na part-2).
- `--elos` não lista presumido (é Sim por definição) nem resposta com `elos` de tamanho diferente da cadeia.

### Critical Gate

Clean -- só `ALTER TABLE ... ADD COLUMN` idempotente (aditivo; nenhum DROP/DELETE/UPDATE em massa).

### Não verificado

- O `--registrar` contra o `ipub.db` real (regra: nenhum `--apply` no banco real); a migração foi exercitada em banco sintético,
  inclusive linha pré-migração com NULL.

14 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
