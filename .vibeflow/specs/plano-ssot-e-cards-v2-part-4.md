---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 4
slug: plano-ssot-e-cards-v2-part-4
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/day_plan.py
  - core/contracts/cronograma-contract.md
  - core/contracts/reconcile-contract.md
---

# Spec -- Parte 4: o Plano do Dia lê `plano_tarefas`; contratos versionados; W8 morre

> PRD `plano-ssot-e-cards-v2`, P1 (última parte). Depende da Parte 3. Fecha o critério de sucesso 1 do PRD.

## Objective
O boot lidera com a próxima tarefa vinda de `plano_tarefas` (fonte, link, nº previsto, semana do plano), e o banner `Drive desatualizado` deixa de existir porque a conclusão não vem mais do Drive.

## Context
`tools/day_plan.py` hoje deriva "próximos temas" de `grade.json` por calendário (`_cronograma_hoje`), filtra pela `preparacao_estado.cronograma_conclusao_drive` (`_conclusao_drive`, snapshot de 26/07) e reordena pelo xlsx (`_ordenar_por_drive`). O `cronograma-contract` v1.2 declara a feature read-only no db com um único write (ponteiro textual); o `reconcile-contract` tem o W8 (fronteira real desconhecida). As Partes 1-3 tornam essas três funções e o W8 obsoletos.

## Definition of Done
1. `python tools/day_plan.py` imprime a linha `🧭 Cronograma:` a partir de `plano_tarefas`: semana do plano corrente (menor `semana_plano` com pendente), as próximas 3-5 tarefas pendentes em ordem (`fonte`, `tema`, `tipo`, `q_previstas`, `url_lista` quando houver) e o total de questões previstas da semana; `--handoff-block` passa a emitir `Posicao: plano semana N (fase 1|2) · X/Y tarefas da semana feitas` no lugar de "conteudo S17 (nominal S25)".
2. `_conclusao_drive`, `_ordenar_por_drive` e o ramo calendário de `_cronograma_hoje` são removidos (não comentados); `tools/test_plano_dia.py`/`test_boot_verdadeiro.py` atualizados; nenhum teste da suíte referencia `cronograma_conclusao_drive` como fonte viva.
3. Boot emite **uma** linha de pendência de revisão (`plano_pendencia_revisao`, Parte 3) enquanto houver linha `dashboard_2026-09-10`, e silencia quando zerar -- nunca falso positivo com tabela vazia (regra dos irmãos F1/POSICAO/B1).
4. `core/contracts/cronograma-contract.md` -> **v1.3**: declara `plano_tarefas` como tabela da feature (única exceção ao read-only, com os writers nomeados), lápida a Cláusula 5b (dois sinais do Drive) e o `--sync-drive` com ⚰️ + data + motivo; `core/contracts/reconcile-contract.md` -> W8 lapidado (**declarar + lapidar + cadastrar termo revogado em `_TERMOS_REVOGADOS`/marcador `<!-- TERMO-REVOGADO -->`, os três no mesmo commit -- AGENTE §10.10**); W5b novo = `cronograma.py --check-extensivo` (WARN).
5. `auto_check --changed` PASSED com o gate `CONTRATO_REVOGADO` enxergando o termo novo (teste `test_contrato_revogado.py` estendido com o termo).
6. Craftsmanship: `POSICAO_DRIFT` deixa de comparar com `preparacao_estado.semana_conteudo` (fonte morta) e passa a comparar com `plano_tarefas`; `preparacao.py --set-semana` ganha lápide na skill; zero ponteiro morto em doc de raiz (G10).

## Scope
`tools/day_plan.py`, `tools/test_plano_dia.py` (ou suíte equivalente já existente), `core/contracts/cronograma-contract.md`, `core/contracts/reconcile-contract.md`, `tools/auto_check.py` (termo revogado + POSICAO_DRIFT), `.claude/commands/cronograma.md` (lápide do `--sync-drive`).

## Anti-scope
Sem tocar `fsrs`/`review_log`/dormência (`review_radar`, `dormant_refresh` seguem iguais). Sem deletar `tools/cronograma.py --sync-drive` nesta parte (lápide na skill; remoção do código é a Parte 8, junto do congelamento do Drive). Sem painel.

## Technical Decisions
- **Semana corrente = menor `semana_plano` com pendência**, não calendário: estar atrasado vira "a semana 3 ainda tem 4 tarefas", que é informação de gestão, sem projeção por data (mantém o espírito do `cronograma-contract`: plano não é verdade-de-estado).
- **Ritmo-alvo continua medindo a grade/marco (`performance.volume_vs_marco`), não a prova** -- F88 intacto; o que muda é só a fonte de "o que vem a seguir".
- **Revogação em três passos no mesmo commit** (F90): é a parte que mais mata cláusula viva (5b, W8, `--sync-drive`), logo é a parte em que o gate mais precisa enxergar.

## Applicable Patterns
- `warn-first-check.md` (W5b nasce WARN; pendência de revisão é linha, não bloqueio).
- `agent-workflow-protocol.md` (boot: AGENTE §2 passo 4 cita o `day_plan`; o texto do passo é atualizado em uma linha).

## Risks
- Regressão silenciosa em `test_boot_verdadeiro` (o boot "verdadeiro" testa a saída completa) -> rodar a suíte inteira antes do commit, não só a nova.
- Esquecer o passo 3 da revogação (cadastrar termo) -> DoD 5 exige o teste ver o termo.

## Dependencies
- .vibeflow/specs/plano-ssot-e-cards-v2-part-3.md
