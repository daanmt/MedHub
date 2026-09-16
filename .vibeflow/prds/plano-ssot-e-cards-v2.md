# PRD: Plano como SSOT, ledger de listas, painel gerado e player de cards (v2)

> Generated via discover on 2026-09-16 (s183). Refina a 1ª versão escrita à mão na mesma sessão; incorpora as decisões do usuário de 16/09 e os cortes do discover.
> Permit textual: *"Preciso de um planejamento mais estável, orquestrado por você, que tem mais contexto sobre mim do que as planilhas."*
> ⚰️ **P5 (`tools/cards_prune.py`, lote 1 = 125 aposentados) e P6 (cláusula Autópsia, `analisar-questao.md §3.3`) foram ENTREGUES na s183** e ficam fora deste PRD. Spec de P5: `.vibeflow/specs/plano-ssot-e-cards-v2-part-5.md`.

## Problem

O plano de estudo não tem dono único. O detalhamento vive no `Cronograma.pdf` (Reta Final, 30 semanas), a ordem no xlsx do Drive, e a conclusão no `Dashboard EMED 2026`, que cataloga as **707 tarefas do Cronograma Extensivo** (52 semanas), não as 352 da Reta Final. O usuário fazia tarefas que não existiam no Dashboard e marcava outras no lugar; a coluna `Realizada?` é aproximada por confissão dele. O `grade.json` nunca casou 1:1 com a conclusão real (família F72), e o boot lidera com uma posição projetada pelo calendário, não lida.

As listas de exercícios não têm ledger: `links_exercicios.json` guarda URL e nº de questões só para S15-S30 da Reta Final; `sessoes_bulk` (126 sessões) não referencia tarefa nem link. "Qual lista fiz, quantas, quantos acertos" só se responde lendo prosa em `observacoes`.

Drenar cards é lento: o `/revisar` conversacional apresenta card a card no chat e a nota é digitada; 60 cards custam 5-6 blocos de conversa e contexto. O usuário pede UI mais amigável e mais rápida.

## Target Audience

Usuário único: médico, foco nº1 Psiquiatria/IPUB via ENAMED 2027 (alvo 95%), plano B UERJ/MFC em 01/11/2026; regime 60 questões + 60 cards/dia; opera por chat no desktop (teclado) com celular como fallback; consome páginas como Artifact.

## Proposed Solution

Quatro partes, nesta ordem de dependência:

**P1 -- Plano como SSOT no `ipub.db`.** Uma tabela `plano_tarefas` passa a ser a única verdade de "o que estudar, em que ordem, e o que já foi feito". Ela é semeada de três fontes: o Cronograma Extensivo (derivado do PDF de 52 semanas para `core/cronograma/grade_extensivo.json`, mesmo modelo do `grade.json`), a Reta Final (S17-S28 pendentes) e tarefas custom (7 resumos MFC-UERJ, 8 temas sem resumo, termômetros INEP). O status inicial vem do `Realizada?` do Dashboard de 10/09 marcado como **aproximado**; a verdade é fixada numa **revisão completa por área com o usuário**, começando pelos blocos de maior peso (MFC, Pediatria, Cirurgia, GO), em passadas curtas: o agente lista, o usuário corrige, o agente grava. A semana do plano e a ordem são do agente (Fase 1 por peso UERJ até 01/11; Fase 2 = extensivo S21-S48 reordenado), editáveis por comando (`concluir`, `cortar`, `mover`). O Plano do Dia passa a ler essa tabela; o W8 do reconcile morre.

**P2 -- Ledger de listas de exercícios.** Cada sessão registrada aponta para a tarefa (e portanto para o link da lista e o nº previsto). Backfill único das 104 sessões com `observacoes` por casamento de nome, sem match = vazio, nunca chute. Um comando read-only responde progresso por tarefa, por bloco UERJ e por semana.

**P3 -- Painel gerado.** Uma página fixada, regenerada a cada fechamento de sessão, com progresso por bloco, listas feitas x previstas, FSRS, custo/questão e as próximas 7 tarefas. O Drive deixa de ser fonte: o snapshot W1 é marcado `--abandonada` (mecanismo já existente), e a tabela de investimento/mês continua manual porque é entrada, não derivado. Sem exportação para Sheet no v0.

**P4 -- Player de cards como Artifact (desktop-first).** Uma página com a fila do dia embutida no publish, teclado `1-4` e toque, relearning intra-sessão (nota < 4 volta ao fim do lote), botão `defeito` com motivo, contador e tally. O estado sobrevive a refresh e é lido pelo agente no fechamento, que grava em lote pelo caminho único do FSRS (`record_review` via `fsrs_queue.py --record`), gravando **só a primeira nota** de cada card. Sem botão "aposentar" (é decisão de triagem, não de drill). A Revisão Direcionada de fechamento continua no chat; o `/revisar` conversacional fica como fallback.

## Success Criteria

1. `python tools/day_plan.py` lidera com a próxima tarefa vinda de `plano_tarefas` (fonte, link, nº previsto) e o boot não emite mais `Drive desatualizado`.
2. Revisão de status concluída: 100% das tarefas com `origem_conclusao` = `usuario` ou `cortada`; zero linhas ainda `dashboard_2026-09-10` ao fim da passada.
3. `python tools/listas.py --progresso` responde listas feitas x previstas com acertos por bloco UERJ sem ler o Drive; backfill com N declarado e conferido.
4. Painel publicado e fixado; `day_plan --planilha` diz `comparação suspensa`.
5. Uma sessão de 60 cards fecha no player em menos tempo que no chat (métrica: minutos por 60 cards, medidos 3 sessões antes e 3 depois) e grava 60 revisões via `--record`, com exatamente 1 revisão por card.
6. Toda operação em lote (semeadura, backfill, gravação das notas) tem dry-run + COUNT-ASSERT escritos antes de rodar; `test_writer_allowlist.py` lista cada writer novo.

## Scope v0

- P1: `tools/cronograma.py --rebuild-extensivo` -> `core/cronograma/grade_extensivo.json`; tabela `plano_tarefas`; `tools/plano.py` (`--semear`, `--listar`, `--concluir ID --sessao N`, `--cortar ID`, `--mover ID --semana N`, `--revisar-area AREA`); `day_plan.py` lendo a tabela; contrato `cronograma-contract.md` v1.3.
- P2: `sessoes_bulk.tarefa_id`; `registrar_sessao_bulk.py --tarefa ID`; `tools/plano.py --backfill-sessoes` (dry-run/COUNT-ASSERT); `tools/listas.py`.
- P3: `tools/painel.py --html` -> `artifacts/painel.html` (publicado pelo agente no fechamento); `importar_sessoes.py --abandonada` executado; lápides em `/importar-planilha` e `/cronograma` (`--sync-drive`).
- P4: `tools/fsrs_queue.py --export-player` (JSON do lote) + template `artifacts/player.html` + `tools/fsrs_queue.py --record-lote ARQUIVO` (dry-run + COUNT-ASSERT, 1 nota por card, chama `record_review`); contrato `revisao-calibrada-contract.md` v1.4 (o player é a Fase DRENAR; Invariantes A/C/F preservados).

## Anti-scope

- Editar à mão o Dashboard/xlsx do Drive; exportar Sheet; scraping de listas do Estratégia.
- Botão "aposentar" no player; Revisão Direcionada dentro do player; migrar o FSRS para Anki; qualquer UI fora de Artifact (zero Streamlit).
- Import em massa dos Medcards; alterar `stability`/`difficulty`; tocar `taxonomia_cronograma` e `review_log` por estas partes.
- Revisar o status de tarefas fora de uma passada explícita com o usuário (nada é marcado "feito" por inferência).

## Technical Context

- `app/utils/db.py` é o único arquivo com `import sqlite3` (conventions §Database access); writers novos passam por ele e entram na allowlist de `tools/test_writer_allowlist.py`. Padrão `db-access-layer.md`.
- `tools/cronograma.py` já deriva `grade.json` do PDF da Reta Final (PyPDF2); o parser do extensivo foi prototipado na s183 (52 semanas, 735 tarefas, `paginas_livro`, `n_links_questoes`) e vira `--rebuild-extensivo`. Fronteira do contrato: read-only no db (o único write da feature de cronograma é o ponteiro textual) -- **P1 muda isso e precisa versionar `cronograma-contract.md`** (v1.3) para declarar `plano_tarefas` como tabela da feature.
- `day_plan.py` hoje lê grade + `preparacao_estado.cronograma_conclusao_drive` (`_conclusao_drive`, `_cronograma_hoje`, `_ordenar_por_drive`); P1 substitui essas três por uma leitura de `plano_tarefas`.
- `fsrs_queue.py --list` já emite o lote em JSON e `--record CARD_ID --rating --reason` grava por `record_review` (único caminho; balanceador e blackout dentro). P4 só embrulha: exporta o lote e reimporta as notas.
- `importar_sessoes.py --abandonada MOTIVO` já existe (F35, s176) e é o mecanismo para congelar o Drive.
- Padrões: `warn-first-check.md` (regra nova nasce WARN), `error-insertion-pipeline.md`, `agent-workflow-protocol.md` (skill = referência atômica; workflow = orquestração; toda flag nova documentada na skill dona -- gate D5 BLOQUEIA).
- Orçamento: <= 6 arquivos por task (index) -> P1 e P4 vão se dividir em partes no gen-spec.

## Open Questions

- Capacidade de estado do Artifact para o player (P4): confirmar no skill `artifact-capabilities` qual capability guarda estado por viewer que o agente consegue ler de volta; se nenhuma servir, o fallback v0 é a página gerar um bloco de texto com as notas que o usuário cola no chat.
- Data do ENAMED 2027 (assumida ~set/2027) e horas na residência (12-15 h/sem) seguem assunções para a Fase 2 do plano.
