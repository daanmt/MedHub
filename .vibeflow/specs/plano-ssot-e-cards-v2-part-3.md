---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 3
slug: plano-ssot-e-cards-v2-part-3
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/plano.py
  - app/utils/db.py
---

# Spec -- Parte 3: mutações do plano (`concluir`, `cortar`, `mover`) e revisão de status por área

> PRD `plano-ssot-e-cards-v2`, P1 (terceira parte). Depende da Parte 2.

## Objective
O agente passa a operar o plano por comando -- concluir, cortar, mover -- e conduz com o usuário a revisão completa do status inicial por área, de modo que nenhuma linha fique com origem `dashboard_2026-09-10` ao fim da passada.

## Context
A Parte 2 semeia `plano_tarefas` com status aproximado. O usuário confessou marcar tarefas no lugar de outras no Dashboard e recusou o corte de escopo "revisar só S17-S28 + S21-S30": a revisão é completa, por área, em passadas curtas, começando por MFC, Pediatria, Cirurgia e GO. Reordenar semana deixa de ser ritual no xlsx (`project_cronograma_dual_ssot`).

## Definition of Done
1. `tools/plano.py --concluir ID --sessao N [--data AAAA-MM-DD]` grava `status='feita'`, `data_conclusao`, `sessao_bulk_id=N` (a sessão precisa existir em `sessoes_bulk`, senão recusa), `origem_conclusao='usuario'`; `--cortar ID --motivo "..."` grava `cortada` + `nota`; `--mover ID --semana N [--ordem K]` regrava `semana_plano/ordem`; `--reabrir ID` volta a `pendente`. Todas via writers em `db.py` (`plano_set_status`, `plano_mover`), com `atualizado_em = db.agora()`.
2. `tools/plano.py --revisar-area AREA` imprime a lista da área em formato de conferência (id, semana fonte, tema, tipo, status atual, origem) em blocos de <= 25 linhas; `--confirmar-area AREA --feitas "1,4,9" --pendentes "2,3"` aplica em lote com dry-run + `--expect N` e marca `origem_conclusao='usuario'` em **todas** as linhas da área (inclusive as que não mudaram de status -- a conferência é a evidência).
3. `python tools/plano.py --pendencia-revisao` imprime, por área, quantas linhas ainda têm `origem_conclusao='dashboard_2026-09-10'`; o `day_plan.py` (Parte 4) consome este número. Critério de sucesso 2 do PRD: zero ao fim da passada.
4. `tools/test_plano.py` estendido: recusa de sessão inexistente, idempotência de `--concluir`, `--confirmar-area` com `--expect` errado (nada grava), lote correto marca origem em toda a área; `auto_check --changed` PASSED.
5. Craftsmanship: nenhuma escrita direta (`sqlite3`) fora de `db.py`; toda flag nova em `/engenharia-cli`; mensagens de recusa nomeiam o motivo e o comando corretivo.

## Scope
`tools/plano.py` (flags acima), `app/utils/db.py` (2 writers + leitor `plano_pendencia_revisao`), `tools/test_plano.py`, `.claude/commands/engenharia-cli.md` (+ espelho), `.agents/workflows/registrar-sessao.md` (passo novo: "ao registrar bulk de um bloco, `--concluir` a tarefa correspondente").

## Anti-scope
Sem interface conversacional nova: a revisão por área é o agente lendo `--revisar-area` e escrevendo `--confirmar-area` a partir das respostas do usuário no chat. Sem inferência de conclusão a partir de `sessoes_bulk` (isso é a Parte 6, e mesmo lá é vínculo, não conclusão automática). Sem `day_plan`.

## Technical Decisions
- **`origem_conclusao` é a trilha de auditoria, não `status`**: uma linha pode continuar `feita` e mudar de `dashboard_2026-09-10` para `usuario`; é o que permite o critério "zero aproximadas" sem reescrever histórico.
- **`--confirmar-area` em lote com `--expect`** em vez de N comandos `--concluir`: a passada tem ~700 linhas e o rito por linha viraria 700 turnos.
- **`--concluir` exige `sessoes_bulk` existente**: fecha a porta do "feito sem volume" e prepara o `tarefa_id` da Parte 6.

## Applicable Patterns
- `db-access-layer.md`, `error-insertion-pipeline.md` (COUNT-ASSERT), `agent-workflow-protocol.md` (o passo novo entra no workflow, não na skill).

## Risks
- Fadiga na revisão de 707 linhas -> ordem por peso UERJ e blocos de 25; o `--pendencia-revisao` mostra o que falta para o boot cobrar sem repetir o que já foi.
- Conflito com `cronograma_progresso` (tabela antiga escrita por `insert_questao`): declarar no `_meta` da Parte 4 que `plano_tarefas` é a fonte de conclusão e `cronograma_progresso` fica como legado lido por ninguém (lápide, não deleção).

## Dependencies
- .vibeflow/specs/plano-ssot-e-cards-v2-part-2.md
