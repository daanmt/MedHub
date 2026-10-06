---
type: session
layer: history
status: canonical
---

# Sessão 216 -- 2026-10-05/06 -- engenharia do hub (integração e corte de passos) + RD de Hérnias

Modelo: Fable 5.1 (principal) + 3 subagentes Opus. Operador presente até ~23h de 05/10; depois, ordens repassadas pelo /ai-eng (observador na sessão).

## Produto (decisões dele, todas no `docs/BACKLOG-PRODUTO.md`)

- P14 (assinar/marcar fecha e volta), P15 (régua: integração, menos redundância, menos passos; 95% estudando), P16 (artifact = memória da interação entre aparelhos; tique 1x/dia em sessão Haiku; o resto é registro e automação).
- Abas Painel | Teoria | Listas | Cards; Documentação só no Painel; Biblioteca só daqui em diante; "Hoje ao vivo" só soma; **P09: lote conta no dia da 1ª nota**.
- Descartados: Aba Análise (E08, absorvida por Painel > Documentação), E03 até 01/11. **part-1b (comentário do EMED pela API) AUTORIZADO** como insumo da análise dos elos; ele destrava no prompt de permissão quando aparecer.
- Triagem do /ai-eng: E10 (F141 remédio A = `relearning_steps=()`; F142 = guarda na 2ª nota do dia) e E12 (E01 sem backend: trecho gerado em arquivos de dados). Para depois da s216.

## Engenharia (PRD `.vibeflow/prds/hub-integracao-cortar-passos.md`; specs `hub-integracao-part-1..6`)

Executor único (Opus, 627 mil tokens, 225 chamadas, 68 min pelo `usage`): as 6 parts com teste antes do código.

- part-1 Teoria só com teoria (92 -> 18 tarefas na aba; filtro só de exibição) + abas reordenadas + `abrirAula(href, titulo)`.
- part-2 Painel lê `listas/*` (`marcarListasEm` de topo aplicado ao iframe; `data-tarefa` no li do painel) + Listas -> aula que prepara (`#hub-ligacoes`, hash na projeção).
- part-3 Biblioteca (mesmo id `hub-quadro-feitas`; origem no `data-secao`; aviso "candidata a arquivo" saiu; `CAP_AULAS` 200; ritos reescritos).
- part-4 Concluir = fechar e voltar (`LEITOR.origem` antes do `ir`; `voltarOrigem` só após o quadro; `QZ.recente`; `qd-assinado` no Painel).
- part-5 Regra P09: `day_plan.consumo_logico` (desvio declarado: lotes de até 2 dias antes, não só o último gravado; casa por `(card_id, review_time)`); `realizado_do_dia` intacto; contrato `fsrs-management` v1.8.
- part-6 Hoje ao vivo: `data-vivo`/`data-sessao-gravada`/`data-gerado-iso` no painel; `vivoCards` (sessão, não horário) e `vivoQuestoes` (por lista, dia lógico por `Date.parse`).
- Dívida (2º subagente Opus, 256 mil tokens, 34 min): E02 (sonda `sitecustomize` no subprocesso, 9 testes), E05 (25.000 docs em 3 portadores + `revisar.md`), E06 (`cobertura_conhecimento` pela régua do `plano.panorama`; `semana_conteudo` sem leitor), E11 (órfã nasceu em 4990357/s211, não na s215; anotada `NAO-VERIFICAVEL`; catraca volta a 127).
- Mapa de código (Explore Opus, 224 mil tokens, 8,5 min): 18 armadilhas A1-A18, todas resolvidas nas specs.
- Conferência em navegador (regra s211): harness em scratch (db falso semeado com `tmp/hub_db` + `tmp/bancada`, runner de cenários, Edge headless a 390 px, temas claro e escuro). 23 capturas: abas, Teoria, Biblioteca, Listas com "abrir aula", leitor com "‹ Painel/‹ Teoria/‹ Listas", assinar documento volta ao Painel com "· assinado", assinar aula volta à Teoria, lista resolvida riscada no Painel sem publish, "+12" cards e "+2" questões ao vivo. Achado: o build copiado para o harness estava velho (a RD caía dentro da tarefa); refeito.
- Suíte **1447** (era 1409). `auto_check --changed` PASSED.
- Hub **Version 74** (publish com `aulas/rd-hernias.html` + `painel.html`; 24 aulas intocadas).

## Estudo: lista t49 (Hérnias da Parede Abdominal), 10/21, resolvida 05/10 22h29

- Registrada: `emed_banco --registrar` (21 novas), bulk #216 Cirurgia 21q/10 (`sessoes_bulk.id=135`, data 05/10), `plano.py --concluir 49 --sessao 135`.
- 11 erros com os elos DECLARADOS por ele como insumo (`insert_questao --errors-file`, erros #1118-1128, cards #1905-1915, `--emed t49_N`). Clusters: encarcerada x estrangulada (Q5, Q13, Q20; 2 sólidas erradas), operar x observar (Q1, Q4), técnicas (Q12, Q15, Q18), complicações (Q11, Q14, Q17). Q20 divergente (banca opera; diretriz aceita taxe), registrado com a divergência.
- Habilidades: incerteza (Q21 chute certo), desatenção (Q1 elo 3; Q17 elo 1, grifou "nem urinou" e não converteu). Carimbo `directed_review` no tema 421.
- RD no hub: `artifacts/aula-rd-hernias.html` (tipo `revisao`, bloco Revisões direcionadas), com 2 perguntas na alça fechada (`rd-hernias_q4`: qual item julgou falso; `rd-hernias_q20`: considerou a hérnia resolvida pela redução ou o AAS como motivo de adiar) semeadas em `analises/pendencias/itens`.
- Feedback dele "cadeia com defeito: elo 1 óbvio" (Q4): absorvido como regra para Soluções futuras (questão de contagem não ganha o elo "julgar cada item"); a cadeia da t49_4 não foi reescrita (os `elos` declarados estão alinhados a ela).
- Limite: sem resumo local de Hérnias (`SEM-LASTRO` em 11 inserts); a RD ancora na Solução MedHub (HerniaSurge 2018, WSES 2017, Sabiston, Miller). Candidato a resumo.

## Fricções

- O publish do hub foi recusado 2x pelo gate "view the live version" mesmo com o build derivado da mesma versão; exigiu ler o fonte salvo por trechos (a linha do quadro tem 45 mil caracteres). Custo real do E01 nesta sessão: ~150 mil tokens só de leitura da página.
- O harness de navegador copiou um build velho (mtime) e a RD apareceu no lugar errado até o `cp -f` explícito.
- A questão ao vivo mostrou "+2" com 3 semeadas porque a meia-noite passou no meio da captura: comportamento correto, não defeito.

## Para o operador

- Responder as 2 perguntas da RD de Hérnias no hub (Teoria > Revisões direcionadas > Hérnias).
- F141 (remédio A): aceita que um card falhado hoje só reapareça amanhã, nunca na mesma fila?
- E12 (E01 sem backend): fazer numa sessão própria antes de outra melhoria de UI?
