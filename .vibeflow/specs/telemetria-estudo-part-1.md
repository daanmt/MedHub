# Spec: Telemetria de estudo — part 1: persistir o planejado — degrau 3/4

> Gerado de `.vibeflow/prds/HANDOFF-telemetria-comportamento-estudo.md` em 2026-07-12 (Fable/ai-eng).
> Executor: Fable/ai-eng (reforma delegada pelo operador). Split declarado no PRD: part-1
> persiste o plano; part-2 computa aderência.
> ⛔ Fronteira clínica CRÍTICA: estruturas novas guardam SÓ metadado de processo
> (timestamps, contadores, enums, ids opacos). Se para computar algo for preciso LER um
> card/resumo, está fora.

## Objective

O plano do dia (o que o `day_plan` recomendou, com os flags de contexto) passa a ser
persistido no `ipub.db` — sem o PLANEJADO gravado, aderência planejado×real é incomputável.

## Context

O realizado já existe (`fsrs_revlog`, `review_log`, `sessoes_bulk`); o planejado evapora
no stdout do `day_plan`. `preparacao_estado` é KV (chave/valor) — não comporta um plano
multi-bloco por dia; precisa de tabela própria. `--tempo`/`--energia` são parseados em
`build(tempo_h, energia)` e descartados. Tese D54 do operador: orquestração da preparação
exige comparar intenção com execução.

## Definition of Done

1. [ ] Migração idempotente no padrão `cleanup_db.py` (backup do `ipub.db` → validação →
   DDL) cria `plano_dia`: `id, data, ordem, task_tipo (enum texto), alvo_tema (texto
   opaco/label da task — sem conteúdo clínico), volume_planejado (int), tempo_h (real,
   nullable), energia (texto, nullable), criado_em`. Re-rodar a migração não duplica nem
   falha. Nenhuma coluna de texto clínico (pergunta/resposta/trecho) — schema é a prova.
2. [ ] Rodar `day_plan` (build) persiste os blocos recomendados do dia com os flags do
   run; **idempotente por dia**: re-rodar no mesmo dia substitui o plano daquele dia numa
   transação (delete+insert por `data`), nunca acumula (precedente F22).
3. [ ] Flag novo `--no-persist` existe para simulação (rodar plano hipotético sem gravar);
   default é persistir.
4. [ ] Leitura: função que retorna os blocos planejados de uma data (consumida pela part-2);
   `day_plan --plano-de YYYY-MM-DD` imprime o plano gravado daquele dia.
5. [ ] Craftsmanship: `pytest` inteiro verde + suíte nova com fixture sintética (ids/labels
   fake, zero conteúdo real de card); contrato de paridade do recomendador **intocado**
   (suíte existente de paridade segue verde — persistir não muda o que se recomenda);
   convenções db (conexão fechada, commit antes de close) e Don'ts respeitados.

## Scope

- `tools/migrate_plano_dia.py` (novo, padrão cleanup_db) OU extensão do mecanismo de
  migração existente — o que `cleanup_db.py` sugerir na leitura; decisão na implementação.
- `tools/day_plan.py`: persistência ao final do `build()` + `--no-persist` + `--plano-de`.
- `tools/test_plano_dia.py` (novo).

## Anti-scope

- NÃO computar aderência (part-2). NÃO mudar R1-R5/recomendações. NÃO armazenar texto
  clínico. NÃO notificar usuário. NÃO inferir energia (flag declarado, ponto).
- NÃO migrar dados históricos (não existem — o planejado nunca foi gravado; a série começa
  agora).
- NÃO tocar `preparacao_estado` (posição SSOT continua onde está).

## Technical Decisions

- **Tabela própria, não KV**: plano é multi-linha por dia com tipos; forçar em
  `preparacao_estado` (KV) seria JSON-em-célula — inqueryável.
- **delete+insert transacional por `data`** em vez de UPSERT por (data, ordem): o plano é
  atômico por dia (se o re-run recomenda 3 blocos onde havia 5, UPSERT deixaria 2 órfãos).
- **`alvo_tema` é label opaco** (mesmo string que o day_plan já imprime) — referência para
  humanos e para o matcher da part-2; o sensor nunca abre o resumo por trás do label.
- **Persistência no day_plan (conexão própria)**: tools/ é exceção autorizada do pattern
  db-access-layer; `day_plan` já gerencia conexão (`_fsrs_counts(con)`).

## Applicable Patterns

- `db-access-layer.md` — exceção autorizada tools/; disciplina de conexão.
- `error-insertion-pipeline.md` — CLI/argparse/stdout.
- Padrão de migração `cleanup_db.py` (backup→validação→DDL) — mesmo do handoff de integridade.

## Risks

- **Timezone/borda de meia-noite** (plano de ontem vs hoje) → mitigação: `data` = date
  local do run, documentado; teste de borda com data explícita injetável.
- **`--handoff-block` diverge do plano persistido** (dois retratos do mesmo dia) →
  mitigação: persistir DEPOIS de montar o mesmo objeto `p` que alimenta
  `render_handoff_block(p)` — uma fonte, dois consumidores.
- **ipub.db em .gitignore** (a série é local-only e não sobrevive a clone) → aceito: é o
  contrato de todo o db do MedHub (F11); backup é responsabilidade existente do fluxo.

## Dependencies

- Nenhuma dentro da série (paralelizável com degraus 1-2). O handoff de integridade
  (UNIQUE em taxonomia) toca o db por migração — coordenar ordem para backups não colidirem.
