# Spec: Orquestracao da Preparacao -- Part 2: Recomendador do dia (day_plan)

> Gerado via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/orquestracao-preparacao.md` (Onda 2).
> Encoding ASCII limpo. Budget: <= 6 arquivos.

## Objetivo

O `day_plan` deixa de ser relatorio e passa a RECOMENDAR o dia: mix de blocos (questoes por tema da grade, cards FSRS, mini-drill, simulado, descanso) com quantidades, justificativa citando os sinais, e projecao de fechamento da grade -- deterministico, transparente, parametrizado em contrato.

## Contexto

A s109 planejou ~120q; o dia real (tempo curto + cansaco) rendeu 60q de tema unico + drenagem de cards -- decisao 100% na intuicao do operador. O day_plan ja deriva quase todos os sinais (ritmo_cronograma, divida, teto efetivo F4, backlog, clusters F3); falta a FUNCAO DE DECISAO que os combina e a coleta do contexto do dia (tempo/energia). Precedente de forma: teto dinamico F4 = norma no contrato (fsrs-management v1.1) + mecanica no CLI (parametros nomeados no topo). Decisao do operador (2026-07-05): reduzir carga, descansar ou simulado sao saidas legitimas; v0 deterministico (nada de ML).

## Definition of Done

1. [ ] `python tools/day_plan.py` emite secao "Recomendacao do dia": lista ordenada de blocos com quantidades (ex.: `1. mini-drill 2 cards frescos do tema-alvo · 2. 30q tema X da S12 · 3. 15 cards FSRS (teto 30)`) + justificativa citando >= 3 sinais derivados (ritmo real vs necessario, divida/teto, backlog, posicao/atraso da part-1, slack) + os numeros batem com fixtures deterministicas (db temp).
2. [ ] Projecao no output: `ritmo real (janela 14d) = X q/dia -> grade fecha ~DATA (folga/deficit de N dias); necessario = Y q/dia` -- computada de `sessoes_bulk` (janela parametrizada) x grade restante (cronograma.py) x dias para a prova; fixtures cobrem atraso e adiantamento.
3. [ ] `--tempo <horas>` e `--energia alta|media|baixa` alteram a recomendacao conforme regras do contrato (ex.: energia baixa -> sem tema novo pesado, prioriza revisao/cluster quente; tempo curto -> 1 bloco unico do tema mais critico); omitidos, o output declara os defaults assumidos (`[defaults: tempo 4h, energia media]`). Condicoes informadas sao registradas em `preparacao_estado` (serie historica futura; leitura opcional).
4. [ ] Descanso e simulado sao saidas reais: fixtures disparam ambos (regra descanso: energia baixa + folga projetada >= limiar; regra simulado: slot periodico parametrizado usando a area "Simulado" existente). Quando disparam, a recomendacao diz o motivo e o que NAO fazer ("hoje nao puxar tema novo").
5. [ ] Se ha cards de erro FRESCOS (state=0, criados ha <48h via `fsrs_cards.due` de state-0) no tema-alvo do dia, a recomendacao abre com mini-drill deles (funcao `get_fresh_error_cards(tema, janela_horas)` em db.py -- a part-3 expoe no CLI da fila; aqui e sinal).
6. [ ] Norma escrita: `core/contracts/orquestracao-contract.md` (NOVO) nomeia TODOS os parametros (janelas, limiares, pesos de prioridade, regra de descanso/simulado) com os MESMOS nomes das constantes no topo do day_plan.py (padrao TETO_BASE/CAP_MULTIPLICADOR do F4); AGENTE.md aponta o contrato na secao de fluxos. Teste verifica paridade: toda constante citada no contrato existe no CLI.
7. [ ] Craftsmanship: recomendador e funcao pura testavel (sinais -> dict de blocos; render separado); sem flags novas o output atual permanece (a secao nova ADICIONA, nao muda o existente); ASCII; `pytest` + standalone + `auto_check --staged` verdes.

## Escopo

- `tools/day_plan.py`: constantes nomeadas (JANELA_RITMO_DIAS, LIMIAR_FOLGA_DESCANSO, PERIODO_SIMULADO_SEMANAS, defaults de tempo/energia), `recomendar_dia(sinais, tempo, energia) -> dict` (pura), secao de render, flags `--tempo`/`--energia`.
- `app/utils/db.py`: `get_ritmo_real(janela_dias)` (sessoes_bulk), `get_fresh_error_cards(tema, janela_horas)` (state=0 + due recente + tema), `registrar_condicao_dia(tempo, energia)` (preparacao_estado).
- `core/contracts/orquestracao-contract.md` (NOVO): norma + parametros nomeados + exemplos de decisao.
- `AGENTE.md`: 1 linha apontando o contrato (secao de fluxos/boot).
- `tools/test_orquestrador.py` (NOVO): fixtures deterministicas (db temp) cobrindo mix normal, descanso, simulado, tempo curto, energia baixa, atraso de grade, paridade contrato-CLI.
- Bridge pytest (conftest/test_pytest_bridge) se necessario para o teste novo.

## Anti-escopo

- NADA de ML/estatistica alem de media movel simples (janela) e aritmetica de projecao.
- Nao mexer em `_teto_efetivo`/parametros do F4 (validados com dados reais na rodada 1).
- Nao gerar conteudo de simulado; apenas recomendar o slot.
- Nao alterar fila FSRS nem record_review (part-3 cuida da fila).
- Nao construir persistencia de serie alem do registro do dia em preparacao_estado (usar a serie = ciclo futuro).
- Streamlit intocado.

## Decisoes tecnicas

- **Funcao de decisao pura + render separado**: testabilidade deterministica (a mesma dos testes de infer_nota); os sinais entram como dict, a saida e estrutura -- o render so formata. Trade-off: um pouco mais de plumbing; vale pela auditabilidade.
- **Norma no contrato, mecanica no CLI** (precedente F4): o operador ajusta comportamento lendo/alterando parametros nomeados sem novo ciclo de engenharia.
- **Prioridade v0 (ordem fixa documentada)**: (1) mini-drill anti-reincidencia se ha fresco no tema-alvo; (2) fechar grade (bloco de questoes do proximo tema da semana de conteudo) ate o alvo diario derivado do ritmo NECESSARIO (cap por tempo/energia); (3) FSRS ate o teto efetivo; (4) slots especiais (simulado periodico; descanso quando regra dispara, substituindo 2-3). Racional: decisao do operador -- "o foco e fechar o cronograma inteiro antes da prova" com flashcards relevantes mas acumulando; a ordem poe grade na frente e usa o teto F4 (ja validado) como governador dos cards.
- **Energia/tempo como INPUT declarado, nao inferencia**: v0 coleta honestamente (flags + registro); inferir fadiga sem dado e fabricacao.

## Padroes aplicaveis

- `db-access-layer.md` (novas leituras em db.py, retorno dict/DataFrame).
- `agent-workflow-protocol.md` (contrato novo + AGENTE apontando; paridade command<->skill NAO se aplica -- não e skill de fluxo /revisar, e contrato de norma; sem espelho em .claude/commands).
- Precedentes de codigo: `_teto_efetivo` (F4), `infer_nota` + fixtures (Revisao Calibrada), `--review-plan` (F3).

## Riscos (premortem)

- **Recomendacao verbosa/ignorada** (decoracao): mitigar com formato de 3-5 linhas max no render e gate anti-decorativo declarado no contrato (3 sessoes sem a recomendacao alterar o dia real -> revisar/remover).
- **Parametros errados de fabrica** (descanso facil demais / dificil demais): defaults conservadores + todos nomeados no contrato para ajuste por uso; a projecao imprime os numeros-fonte para o operador auditar a conta.
- **Sinal de frescor depender de `due` de state-0**: se algum caminho futuro criar card state-0 com due != criacao, o frescor quebra silenciosamente -- teste fixa o contrato atual (insert cria due=now) e o assert quebra visivel se mudar.

## Dependencies

- .vibeflow/specs/orquestracao-preparacao-part-1.md (posicao SSOT e o sinal de atraso; preparacao_estado para condicoes do dia)
