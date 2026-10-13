# Spec: sprint-final-uerj -- part 5: boot e recomendador falam o "hoje" do sprint

> PRD: `.vibeflow/prds/sprint-final-uerj.md` (Success Criteria 2). Gerada em 13/10/2026 (s226).

## Objetivo

A abertura da sessão (hook `SessionStart`) entrega o mesmo "hoje" que o Painel e as Listas: as tarefas do dia, o
simulado do dia e a dose de cards, em vez da semana e das atrasadas.

## Definition of Done

1. `tools/day_plan.py`: o bloco "🧭 Cronograma" e o Panorama usam `plano.agenda_sprint` quando há sprint: "Hoje (DD/MM):
   N tarefas · Q questões" com cada tarefa e o que fazer (lista/caderno/aula), "Amanhã" em 1 linha e "Fora do sprint: N";
   sem sprint, o bloco antigo.
2. O recomendador deixa de propor "simulado periódico" e "capacidade ~51q" por fórmula quando há sprint: o simulado do
   dia vem do sprint; o resto da recomendação (cards) segue.
3. Teste de paridade `test_boot_painel_listas_mesmo_hoje` (banco sintético): o conjunto de ids de hoje é igual no boot,
   no Painel (part-3) e nas Listas (part-4).
4. O contrato de boot (`tools/hooks/memory_boot.py` `_CONTRATO`, preso por `test_boot_entrega_o_panorama`) passa a
   pedir "hoje do sprint" no lugar de "onde estamos na semana"; o teste atualizado verde.
5. Artesania: suíte verde; `auto_check --changed` PASSED; `cronograma-contract` ganha a cláusula do sprint (v1.6) com
   lápide da regra semanal que deixa de valer até 31/10 (§10.10: declarar, lapidar, cadastrar o termo se houver).

## Escopo

`tools/day_plan.py`, `tools/hooks/memory_boot.py`, `core/contracts/cronograma-contract.md`, testes de `day_plan` e do
boot, `docs/MEMORIA-AUDITORIA.md` §12 (se houver termo revogado).

## Anti-escopo

Painel, hub; FSRS; a meta (`performance.MARCOS`).

## Dependencies

- .vibeflow/specs/sprint-final-uerj-part-4.md
