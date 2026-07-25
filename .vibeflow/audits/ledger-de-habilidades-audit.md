# Audit Report: Ledger de Habilidades

> Auditado em 2026-07-25 · Spec: `.vibeflow/specs/ledger-de-habilidades.md`

**Verdict: PASS**

## DoD Checklist

- [x] **1. Schema idempotente** — `tools/init_db.py` cria `habilidades` + `questao_habilidades` via `CREATE TABLE IF NOT EXISTS` + `CREATE UNIQUE INDEX IF NOT EXISTS idx_qhab_dedup`. Executado 2x sobre o `ipub.db` real sem erro nem duplicação. Teste: `test_dod1_schema_idempotente`.
- [x] **2. Backfill não-destrutivo** — `questoes_erros` medida antes/depois do backfill real: `(593, 86666)` em ambos (contagem + soma de `length(habilidades_sequenciais)`). O CLI não emite `UPDATE`/`DELETE` sobre nenhuma tabela (scan de código confirma: só 2 `INSERT INTO`, ambos nas tabelas novas). Reexecução é no-op (`ocorrencias_novas=0`). Testes: `test_dod2_backfill_nao_destrutivo`, `test_dod2b_backfill_idempotente`.
- [x] **3. Reincidência consultável** — `--reincidentes` ordena por `(ocorrencias DESC, temas_distintos DESC)` e marca `padrao_de_raciocinio` em `temas_distintos >= 3`. `--min-temas` filtra. Teste: `test_dod3_reincidentes_e_flag` (fixture com a mesma habilidade em 3 temas dedupa em 1 linha com 3 ocorrências). **Validação externa:** no backfill real o ledger elevou "marcar a falsa" e "rotular cada alternativa V/F" a 4 temas distintos cada — reconstruindo, a partir dos dados, o padrão *enunciado negativo* que estava catalogado à mão em `feedback_enunciado_negativo`.
- [x] **4. Enum de veredito fechado** — `_validar_veredito` levanta `ValueError` nomeando os 4 válidos. Espelhado em `db.registrar_habilidade`. Teste: `test_dod4_enum_fechado`.
- [x] **5. Ingestão de questão ACERTADA** — `--add` executado no db real: `questoes_erros` 593 -> 593, `sessoes_bulk` 84 -> 84. `questao_id` nulo, `veredito` persistido, `tema_id` resolvido por `(area, tema)`. Testes: `test_dod5_add_nao_toca_erros_nem_volume`, `test_dod5b_incerteza_e_estado_proprio`.
- [x] **6. Craftsmanship gate** — `auto_check --changed`: 0 BLOCK, 0 WARN. Paridade command↔skill OK (`sync_skills --check`). `import sqlite3` apenas em `db.py` + CLI standalone (padrão já estabelecido em 8+ CLIs de `tools/`). Sem setas Unicode nem LaTeX nos arquivos novos.

## Testes

| Suíte | Resultado |
|---|---|
| `test_habilidades.py` (nova) | 38/38 PASS |
| `test_orquestrador.py` | PASS |
| `test_revisao_calibrada.py` | PASS |
| `test_day_plan_telemetria.py` | PASS |
| `test_aderencia.py` | 11 passed |

## Pattern Compliance

- [x] **db-access-layer** — `sqlite3` só em `db.py` (camada app) e no CLI standalone `tools/habilidades.py`. Leituras em `db.py` retornam DataFrame, conforme a convenção do módulo.
- [x] **error-insertion-pipeline** — o ledger **pendura-se** no pipeline sem alterá-lo: `insert_questao.py` intocado; o backfill lê `questoes_erros` e o forward-flow entra por `--add`/`registrar_habilidade`.
- [x] **agent-workflow-protocol** — harness rodado antes de reportar conclusão (§1.3 do AGENTE).
- [x] **Assinatura canônica em UMA skill** (AGENTE §7.2) — `tools/habilidades.py` documentado só em `.claude/commands/analisar-questao.md` §10; espelho regenerado por `sync_skills.py`.

## Critical Gate

**Clean — nenhuma operação destrutiva detectada.**
- Nenhuma regra de _Database_ disparou: a migração é puramente aditiva (2 `CREATE TABLE IF NOT EXISTS`, 3 índices). Zero `DROP`/`TRUNCATE`/`ALTER ... DROP`.
- Nenhuma regra de _Security_, _Data_, _Config_, _IaC_ ou _K8s_ aplicável ao diff.
- `git diff HEAD` sobre os 4 arquivos rastreados: 186 inserções, 1 remoção (linha de `print` do `init_db.py`, substituída pela versão com as tabelas novas).

## Limitação conhecida (documentada, não bloqueante)

🟡 **A reincidência é fraca sobre o histórico, por natureza do dado.** O backfill produziu **1.324 habilidades distintas para 1.336 ocorrências** — quase nenhuma dedup. Causa: as habilidades históricas foram redigidas como prosa sob medida para cada questão ("Reconhecer obstrução por estenose fibrótica na Crohn e pesar as ressecções prévias"), não como rótulos reutilizáveis. Texto único nunca reincide.

Isso **não é defeito da implementação** — o spec previu o risco ("Métrica virar teatro") e a mitigação está ativa: `--report` declara explicitamente quantas ocorrências aguardam curadoria e adverte que a métrica ainda não tem poder. O valor real virá do **forward-flow**, com a regra de autoria adicionada à ETAPA 2 de `/analisar-questao` (habilidade reutilizável, sem sentinelas, marcando qual elo quebrou).

Duas correções feitas durante a implementação, ambas descobertas ao rodar o backfill contra dados reais:
1. **Sentinela `N/A`** ocupava 125 registros em 31 temas e virava a "habilidade mais reincidente" do ledger. Filtrada, junto de rótulos de categoria (`Diagnóstico`, `Terapêutica`).
2. **Segundo formato não previsto** — lista numerada multi-linha (`1. ... 2. ...`), ~22% dos registros. O parser original jogaria todos na fila de curadoria; agora reconhece os dois formatos.

## Próximos passos

- Curadoria incremental dos vereditos (`indefinido` -> `errou`/`acertou`/`incerteza`) conforme as questões forem revisitadas. Sem isso `n_errou` e `n_incerteza` seguem zerados.
- Spec 2 (não implementado): **variância entre provas + diagnóstico de zona** — a métrica do vídeo 1 (variância importa mais que média) sobre `sessoes_bulk`, mais integração do bloco de reincidentes no `day_plan`.
