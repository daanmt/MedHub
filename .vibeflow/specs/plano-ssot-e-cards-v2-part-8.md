---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 8
slug: plano-ssot-e-cards-v2-part-8
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - .claude/commands/importar-planilha.md
  - .claude/commands/cronograma.md
  - tools/cronograma.py
---

# Spec -- Parte 8: congelar o Drive (o banco é a fonte)

> PRD `plano-ssot-e-cards-v2`, P3 (segunda metade). Depende da Parte 7 (o painel tem que existir antes de o Drive parar de ser fonte). Fecha o critério de sucesso 4 do PRD.

## Objective
O `Dashboard EMED 2026` e o `Cronograma de Reta Final.xlsx` deixam de ser fonte de plano e progresso: o boot para de cobrar sync, os mecanismos de leitura ganham lápide e o único dado manual que sobrevive é a tabela de investimento/mês.

## Context
Decisão do usuário em 16/09/2026 (pergunta direta): *"Sim, banco é a fonte"*. Hoje: W1 compara planilha x db (`importar_sessoes.py --snapshot`, F35), W8 lê `cronograma_conclusao_drive` (morto na Parte 4), `--sync-drive` parseia o xlsx, `/importar-planilha` descreve o fluxo "agente lê, código persiste". O mecanismo `--abandonada MOTIVO` já existe para W1.

## Definition of Done
1. `python tools/importar_sessoes.py --abandonada "s18x: banco e a fonte (PRD plano-ssot-e-cards-v2 P3)"` executado; `python tools/day_plan.py --planilha` imprime `comparação suspensa` com o último delta medido preservado (o de 16/09: 6.349 x 7.326).
2. `tools/cronograma.py`: `--sync-drive`, `diff_drive`, `_parse_conclusao_xlsx` removidos (não comentados), com o teste correspondente removido e a docstring do módulo atualizada; `openpyxl` deixa de ser import do módulo.
3. `.claude/commands/importar-planilha.md` reescrita como **stub de lápide** (⚰️ + data + motivo + ponteiro para `plano.py`/`listas.py`/`painel.py`), mantendo só a seção da tabela de investimento/mês (input do `/performance`) e o `--abandonada`; `.claude/commands/cronograma.md` sem a assinatura do `--sync-drive`; espelhos regenerados.
4. Termos revogados cadastrados (`--sync-drive`, `Realizada?` como sinal de conclusão, `cronograma_conclusao_drive`) via marcador `<!-- TERMO-REVOGADO: ... -->` no inventário que o gate deriva; `test_contrato_revogado.py` vê os três; memória do harness atualizada por ponteiro (`project_cronograma_dual_ssot`, `project_planilhas_google_drive` ganham cabeçalho de supersessão).
5. `auto_check --changed` PASSED; `reachability_check` não acusa órfão novo; `doc_drift` sem ref morta.
6. Craftsmanship: nada deletado sem `grep` do nome no repo e nos portadores de regra (AGENTE §10.4); commit único contendo declaração + lápide + cadastro (§10.10).

## Scope
`tools/cronograma.py`, `tools/test_cronograma_*.py` (remoção do teste de sync), `.claude/commands/importar-planilha.md`, `.claude/commands/cronograma.md`, inventário de termos revogados (`docs/MEMORIA-AUDITORIA.md §12` ou onde o gate lê), memórias (ponteiros).

## Anti-scope
Não deletar nem editar nada no Drive (os arquivos ficam lá, congelados, como histórico do usuário). Não remover `importar_sessoes.py` (o `--snapshot/--abandonada` e a leitura de investimento continuam). Não tocar `sessoes_bulk`.

## Technical Decisions
- **Abandonar via mecanismo existente, não via código novo**: `--abandonada` foi desenhado exatamente para "a planilha deixou de ser fonte" (F35, s176); usar é mais barato e mais honesto que apagar o W1.
- **Remover `--sync-drive` de fato** (não só lápide): é código que lê binário do Drive por ritual manual -- a classe que a Cláusula 5b já chamava de "se precisa de bytes, não é do agente". Fica a lápide na skill para o histórico.

## Applicable Patterns
- `agent-workflow-protocol.md` (revogação em 3 passos), `warn-first-check.md` (W1 continua existindo em modo suspenso; nenhum check some, muda de estado).

## Risks
- Usuário voltar a preencher o Drive por hábito -> o painel (Parte 7) e o `--concluir` no fechamento cobrem a necessidade; a lápide na skill explica ao próximo agente por que não importar.

## Dependencies
- .vibeflow/specs/plano-ssot-e-cards-v2-part-7.md
