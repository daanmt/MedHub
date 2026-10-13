# PRD: Sprint final até a UERJ (13/10 -> 31/10) -- um backlog, um plano por dia

> Gerado em 13/10/2026 (s226) a partir do pedido dele, com 1 rodada de discovery (AskUserQuestion, as 3
> recomendações aceitas). Loop vibeflow: este PRD -> specs -> implement + audit por subagente Opus.

## Problem

Nas palavras dele (13/10): *"muitas rotas para o mesmo 'lugar' [...] o backlog se dispersou entre painel, teoria e
listas. existem, de certa forma, 3 cronogramas simultâneos: o principal, no painel, o das teorias -- que é irrelevante --
e o das listas, que tenta se aproximar da do painel"*. E: *"já estamos no dia 13/10 e a prova é 01/11, temos simulados
em aberto, temas quentes não tocados, excesso de atrasos e divisão por semana ineficiente"*.

Medido em 13/10 (`plano.py --listar --status pendente --json`): **83 tarefas pendentes até a S7, ~2.568 questões**
(CM 1.117 · PED 514 · GO 433 · CIR 307 · MFC 197), 21 delas atrasadas da S4; 5 simulados (420 q). O ritmo real é 35 q/dia
(7 d); fechar tudo pediria ~135 q/dia em 19 dias. A semana do plano empilha "atrasadas" que nunca zeram e não diz o que
fazer HOJE. Os três quadros (Painel `_html_semana`, Teoria `html_semanas`/`qd-sem`, Listas `qzRenderListas` por
`QZ_SEM`) repetem a mesma fila com contagens diferentes ("620 questões atrasadas" na Teoria x 23 listas/698 nas Listas).

Achado da mesma manhã (bug, não design): depois de uma troca de versão do hub com a página aberta, a aba Listas esgota
as 3 tentativas de leitura e fica em "Não consegui ler as listas"; sair do artifact e voltar resolve. A tentativa nova
reaproveita a mesma conexão do banco (`QZ.db`), que ficou velha.

## Target Audience

Ele, a 19 dias da UERJ/MFC (01/11/2026, domingo), estudando no hub (celular e desktop) entre plantões. Precisa abrir o
hub e saber, sem pensar, o que fazer hoje: quais listas, qual simulado, quantos cards, qual RD.

## Proposed Solution

1. **Um plano por dia até 31/10, gerado** (`plano.py --sprint`): cada tarefa pendente do sprint ganha uma DATA
   (`dia_plano`), com capacidade de **80 q/dia** (decisão dele, 13/10). Ordem: simulados em dia fixo; o resto pelo
   **peso UERJ do tema** (`faixa_uerj`: alta > média > baixa) e, no empate, o **bloco mais fraco no acumulado das 3 provas
   UERJ** (CIR, depois PED...). Atrasada não ganha prioridade só por estar atrasada. O que não cabe fica **fora do
   sprint**, visível e com o motivo -- nunca apagado. Dia que passou com tarefa não feita: ela **rola** para o próximo
   dia com vaga no próximo `--sprint` (o plano se recalcula; não acumula "atrasadas").
2. **Simulados do sprint** (decisão dele): UERJ 2024, 2025 e 2026; os 2 cadernos UERJ 2017-2020 saem do sprint
   (`--cortar` com motivo). Datas padrão (editáveis num arquivo de configuração versionado): 2024 em sáb 17/10, 2025 em
   qua 21/10, 2026 em **dom 25/10** como ensaio geral (mesmo dia da semana da prova). Dia de simulado não recebe lista.
3. **Painel = o backlog único**: o bloco "Semana N do plano" vira **"Hoje"** (as tarefas do dia, a dose de cards do dia,
   a RD do dia se houver) + **"Próximos dias"** (um dia por linha, recolhido) até 31/10 + **"Fora do sprint · N"**
   (recolhido). Some "Atrasadas", "Desta semana", "Até a prova" por semana.
4. **Teoria = consulta**: Biblioteca (como hoje) + **um backlog próprio só de Revisões Direcionadas** (as não assinadas
   primeiro). Somem as semanas, as atrasadas e as contagens de questões da aba.
5. **Listas = consulta que reflete o Painel**: as listas na ordem do plano diário, agrupadas em "Hoje", "Próximos dias" e
   "Fora do sprint"; sem agrupamento por semana próprio, sem contagem paralela.
6. **Hotfix da leitura**: a tentativa nova pede conexão nova ao banco (`window.claude.use("db")` de novo) antes de
   reassinar.

## Success Criteria

- `plano.py --sprint` (dry-run) imprime, por dia de 13/10 a 31/10, as tarefas e a soma de questões; nenhum dia passa de
  80 q (dia de simulado = só o simulado); os 3 simulados nas datas configuradas; `--apply --expect N` grava `dia_plano`
  e a lista "fora do sprint" com o motivo. Rodar de novo no dia seguinte, sem mudança, dá 0 alterações (idempotente)
  salvo o rolamento das não feitas.
- O Painel, a aba Listas e o boot mostram o MESMO "hoje" (mesmas tarefas, mesmo total de questões) -- teste que monta os
  três a partir do mesmo banco sintético e compara.
- A aba Teoria não mostra semana, atrasadas nem contagem de questões; mostra o backlog de RDs e a Biblioteca.
- Com o banco falso trocando a conexão (a 1ª conexão sempre falha, a 2ª funciona), a aba Listas se recupera sozinha.
- Conferido em navegador real (`python tools/ui_capturas.py`, 390/768/1280) e nas suítes.

## Scope v0

1. Hotfix da reconexão (`core/templates/hub.html`).
2. `plano.py --sprint` + coluna `dia_plano` (writer do `plano.py`, allowlist) + config `core/sprint.json` (capacidade,
   datas dos simulados, data final) + corte dos 2 cadernos.
3. Painel: Hoje / Próximos dias / Fora do sprint (`tools/painel.py`).
4. Teoria e Listas consultivas (`tools/hub.py` + `core/templates/hub.html`).
5. Boot e recomendador lendo o dia do sprint (`tools/day_plan.py`, `plano.panorama`).

## Anti-scope

- FSRS, teto de cards e P09 (a dose de cards do dia é a que já existe; só aparece no "Hoje").
- Mudar a meta (10.000 segue a meta declarada; o plano é a capacidade -- o Painel já mostra onde o acumulado fecha).
- Reescrever a trilha UERJ (`trilha.py`) ou o mapa; recalibrar pesos por bloco além de usar o acerto acumulado como
  desempate.
- Fase 2 / extensivo, tarefas sem semana (166): ficam fora do sprint, intocadas.
- Editor de plano na página (arrastar tarefa de dia): o plano se edita pelo CLI; a página só lê.
- Cunhagem de cadeias/listas novas para temas quentes não tocados (é trabalho de conteúdo, outra frente).

## Technical Context

- `plano_tarefas` (`app/utils/db.py` ~l.1721): `semana_plano`, `ordem`, `bloco`, `q_previstas`, `status`, `nota`; writers
  só em `tools/plano.py` (allowlist `tools/test_writer_allowlist.py`, COUNT-ASSERT + dry-run, `AGENTE.md §10.7`).
- Peso: `plano.faixa_uerj(area, tema, prevalencia)` (~l.724) e `PESO_BLOCO` (~l.91); acerto por bloco nas provas UERJ:
  `sessoes_bulk` área Simulado (obs com o placar por bloco) -- 2021 CIR 7/12, 2023 CIR 8/20, 2022 CIR 5/12.
- Painel: `tools/painel.py` `_html_semana` (~l.508), `_html_rota` (~l.488), `semana_atual`; part-3 da s226 deixou a
  linha = alvo único (`<li class="tarefa" data-tarefa>` preservado).
- Teoria: `tools/hub.py` `html_semanas` (~l.1055), `qd-sem`/`qd-semanas` (~l.1013); Biblioteca `qd-bib`.
- Listas: `core/templates/hub.html` `qzRenderListas` (~l.2094) agrupa por `QZ_SEM` (`<script id="hub-semanas">`).
- Leitura resiliente: `assinarResiliente` (~l.1697); `iniciarQuestoes` guarda `QZ.db`.
- Boot: `tools/day_plan.py` (bloco Cronograma e Panorama vêm de `plano.panorama`).
- Regras de UI: `docs/UI.md`; conferência: `tools/ui_capturas.py`.

## Open Questions

- Datas dos simulados: as padrão acima valem salvo redireção dele (ficam em `core/sprint.json`).
- Hoje (13/10) já começou: o 1º dia do sprint recebe a capacidade cheia ou proporcional? Proposta: cheia, e o que
  sobrar rola para amanhã no próximo `--sprint`.
