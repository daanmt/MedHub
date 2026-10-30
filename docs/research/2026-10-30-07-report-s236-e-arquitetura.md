---
type: research
status: active
relates_to: [HANDOFF, history/session_236.md, docs/BACKLOG-PRODUTO.md, docs/research/2026-10-30-06-ui-auditoria-impeccable.md, DESIGN.md, AGENTE.md, docs/REFORMA-CHECKPOINT.md]
---

# Report do dia (s236, 30/10/2026) e arquitetura do MedHub

Report da sessão 236, escrito pelo agente de estudo (rascunho de um subagente Sonnet, revisado e fechado pelo principal). Feito para ler no celular. Marcas: **(medido aqui)** = contagem feita em 30/10.

Fontes entre parênteses: `s236` = `history/session_236.md`; `HANDOFF`; `P37` etc. = `docs/BACKLOG-PRODUTO.md`; `auditoria` = relatório do impeccable de hoje; `liquidos`, `aulao2`, `rdfig`, `aulao1fig` = `tmp/<nome>/`; `ai-eng` = resumo de arquitetura do ai-eng; `ADR` = ADR do banco de evidências; `CHECKPOINT` = `docs/REFORMA-CHECKPOINT.md`.

## 1. Sumário executivo

1. O hub saiu do dia na **Version 144** (entrou na 139); cinco publicações (140 a 144); suíte completa **1825 passed**, +5 sobre a s235 (s236, HANDOFF).
2. Cards: lote `2026-10-29a` gravado (197 válidas de 200; 4 defeitos para a reforja) e fila de véspera `2026-10-31a` (100 cards) no ar (s236).
3. Aulas: 2 novas (líquidos cavitários; aulão de véspera parte 2, 20 temas no total com a parte 1) e 6 refiguradas: as 5 RDs foram de 1 figura para 3 a 5, e o aulão parte 1 de 4 para 10 (rdfig, aulao1fig).
4. UI: 8 pedidos dele (P37-P42, P44, P46) entregues. Auditoria do impeccable: 0 P0, 4 P1, 14 P2, 7 P3. Aplicados 3 P1 e 4 P2; sobram 1 P1, 10 P2 e 7 P3 (auditoria, s236).
5. Regra nova dele: referência só de artigo, diretriz e consenso (nunca resumo); todo card novo com referência. O banco de evidências saiu em ADR aceito e pacote próprio, e foi APLICADO no MedHub no fim do dia (watermark 2274, 0 cards em quarentena, 32 fontes públicas, suíte 1835 passed; commit de fechamento desta sessão) (ADR, ai-eng, s236).
6. Achamos 14 divergências clínicas em resumos, PDFs e no mapa da UERJ; **nenhuma foi aplicada**. Somam-se às 6 correções da s235 (liquidos, aulao2, HANDOFF).
7. Falta ele: o UERJ 2026 (t890, 93 questões) esta noite e amanhã; 5 pendências do UERJ 2025; 4 perguntas da auditoria; PD-20261030-06 e -07 do ai-eng; D-01 e D-07 (HANDOFF).
8. A seção 3 documenta a arquitetura em 7 camadas, 2 fluxos, a tabela de SSOT e as dívidas abertas, cada uma com fonte; o que o ai-eng não observou continua marcado assim.

## 2. O que fizemos hoje

Commit do dia: `01d46b6` (29 arquivos, 3.830 inserções, 400 remoções; `git show --stat`). Pedido dele, ~18h: sincronizar o hub, mais a aula dos temas mais cobrados e a aula de líquidos (s236).

Versões do hub no dia: 140 (18:41, pedidos P37-P42, fila e painel), 141 (18:50, título curto), 142 (19:00, líquidos), 143 (19:45, aulão 2) e 144 (20:20, refiguração, realce rosa e quick wins). Tique às 18:05 (s236).

### (a) Estudo

- **Tique (18:05):** `--record-lote --apply --expect 197` gravou 197 válidas de 200 (revlog 4871 para 5068). Defeitos para a reforja: #1021 e #524 "contexto cortado"; #281 e #564 "pergunta circular" (s236).
- **Fila de véspera `2026-10-31a`:** 100 cards, pool de 197, 13 retidos pela reforja. Saldo do dia zerado: consumo 197 contra teto 100 (s236).
- **Ele esvaziou a fila e dispensou a revisão direcionada de hoje.** O UERJ 2026 (t890, 93 questões, ensaio geral) segue `capturada`; ele começa esta noite e termina amanhã, junto de mais cards (s236, HANDOFF). Pendências do UERJ 2025: 5 abertas (Q43, Q56, Q58, Q65, Q80), a declaração não bate com a marcação (HANDOFF).
- **Aviso do CLI:** aula feita no quadro com tarefa pendente (#1797, TB 360); `plano.py --concluir` exige `--sessao` porque a tarefa tem caderno de 20 questões. Relatado, não forçado (s236).
- **Hoje no Painel depois do U1:** tarefas 1797, 380, 740 e 890; 80 questões = soma dos cartões (s236). **Véspera (31/10), leve:** aulão (partes 1 e 2), líquidos, UERJ de Bolso e as 5 RDs da 2025; cards só se a fila for curta (HANDOFF, item 0).

### (b) Aulas

Pedido dele: aula com os 10 temas mais prevalentes na UERJ ("talvez até os 20") e uma aula só de derrames e análise de líquidos, com os diferenciais (s236). A parte 1 do aulão já estava na Teoria desde a s235; ele não tinha visto (s236).

| Aula | Figuras | Referências | Questões | Obs. |
|---|---|---|---|---|
| `liquidos-cavitarios` (nova) | 4 | 35 | 24 da UERJ 2021-2025; 6 são erros dele ("você caiu nisso") | 5 capítulos, 87 KB; 12 refs "não conferido no original" |
| `aulao-vespera-uerj-2` (nova) | 10 | 43 | 64 (temas 11-20 pelo peso 2021-2025) | 92 KB; todo capítulo com "você caiu nisso" |
| `aulao-vespera-uerj` (parte 1, refigurada) | 4 para 10 | 22 | 30 "teste agora" (s235); questões por capítulo em `tmp/aulao/temas.md` | 85.950 para 103.616 bytes |
| RD CM `rd-cm-2910` | 1 para 5 | 22 | 6 erros no bloco | 20 realces rosa no texto |
| RD CIR | 1 para 3 | 16 | 3 erros no bloco | 9 realces |
| RD GO | 1 para 4 | 15 | 5 erros no bloco | 10 realces |
| RD PED | 1 para 4 | 19 (9 citam `resumos/`) | 1 erro no bloco | 11 realces |
| RD MFC | 1 para 3 | 21 (8 citam `resumos/`) | 3 erros no bloco | 6 realces |

Fontes: figuras e realces (s236, rdfig, aulao1fig); questões das aulas novas (s236); erros por bloco = total do bloco menos acertos da UERJ 2025 (HANDOFF: CM 14/20, CIR 16/19, GO 15/20, PED 18/19, MFC 16/19; soma 18, igual aos 18 erros da s235). A RD cobre os temas de nota 1-2, não só esses erros. Referências contadas nos `<li id="ref-N">` de `artifacts/aula-*.html` (medido aqui).

- **Como foram feitas:** líquidos e aulão 2 por subagente Opus, cada um lido inteiro pelo principal e registrado em `core/hub_quadro.json`; os dois receberam, no meio, a regra "Referências sem resumos nem PDF do EMED" (s236). Refiguração (P45): figura do /anima por seção com mecanismo, legenda de uma linha, rosa só no elemento que decide, âmbar só em aviso; aulas anteriores a 30/10 seguem com 1 figura até serem reabertas (rdfig, aulao1fig, P45).
- **Texto clínico intacto:** fora das figuras é idêntico ao HEAD (`check_figs.py`). Única frase nova: o mecanismo da vacina conjugada na RD PED, pedida pelo principal para a figura não dizer o que o texto não diz (s236, rdfig).
- **Conferência visual:** Edge headless a 390 px nos dois temas, sem rolagem horizontal nas 5 RDs; menor texto de SVG com 11 a 12 px (rdfig); no aulão 1 o texto da figura sai a ~9 px no leitor (aulao1fig).
- **P48 (aberto):** as aulas e RDs antigas listam resumo e apostila em Referências, e o hub só esconde o que vem como "Fonte:" no texto (P48). Medido aqui: nas 5 RDs, PED e MFC têm 9 e 8 referências começando por "Resumo..." (`resumos/`); CM, CIR e GO têm 0; o aulão 1 tem 1 "Material de curso (EMED)". O P48 foi corrigido no backlog: são as RDs de PED e MFC e as aulas anteriores a 30/10, não as 5 RDs.
- **Custo dos subagentes (s236):** líquidos 435 mil tokens e 28 min; aulão 2 572 mil e 43 min; RDs 347 mil e 27 min; aulão 1 296 mil e 23 min; realce e docs 211 mil e 13 min; auditoria 308 mil e 14 min; quick wins 238 mil e 13 min. A soma das sete linhas é 2,41 milhões de tokens (usage do harness, somado aqui); com os 3 subagentes seguintes (quick wins 238 mil, rascunho deste report 324 mil, evidence-bank em curso) o dia passa de 3 milhões.

### (c) UI (pedidos dele em 30/10)

| Pedido | O que mudou | Hub |
|---|---|---|
| P37 | Aba Cards sem aviso âmbar de fila velha e sem legendas de teclado; 3 botões numa linha | 140 |
| P38 | Questão: "< Listas", paginador no topo, Responder à direita da certeza (apagado até letra + certeza), sem legendas "eu sei / entre duas / não sei" | 140 |
| P39 | Painel: dois lugares fixos por tarefa (Resolver e Abrir aula); o que não existe fica apagado | 140 |
| P40 | Grifo: amarelo, ciano, rosa (a ativa segue rosa) | 140 |
| P41 | "Base deste documento" fora; o hub descarta a base interna | 140 |
| P42 | Barra do leitor da Teoria: voltar e Grifo numa linha, título abaixo | 140 |
| P44 | Título da lista acima da barra e curto (corta acima de 70 caracteres; dado do plano intacto) | 141 |
| P46 | Cards com realce rosa: `**x**` em qualquer campo; número com unidade ou sinal no verso | 144 |

Fonte: s236 e backlog P37-P46. A P43 (referência nos cards) está em (f).

- **Quick wins da auditoria** (U1, U2, U3, U5, U6, U11, U12) entraram na Version 144; ver (e). Conferência em Edge headless a 390, 768 e 1280 (`tmp/ui_capturas/s236*`) (s236).
- **Testes:** 5 novos (realce, paridade `tituloCurto`, aula lida com lista pendente, acentos do player, `aria-pressed`) (HANDOFF); arquivos tocados: `test_hub_quadro`, `test_hub_render`, `test_painel`, `test_player_js` (`git show --stat`).

### (d) Design system e documentação

- **DESIGN.md** (63 linhas alteradas no commit do dia), regras novas: **Rosa Realça Rule** (rosa realça o dado que decide, 1 a 3 por seção ou card; âmbar é aviso; ciano é interação); **posição fixa > elemento condicional** (o controle que não existe fica apagado, nunca some); figura em toda seção com mecanismo, sem legenda de cores em frase; pé da questão (Sólida, Dúvida, Chute, Responder), barra do leitor e Referências sem base interna.
- **Named Rules hoje:** Cor Literal, Um Papel por Cor, Rosa Realça (nova), Nunca Só Cor, Sem Caixa-Alta, Número Único, Um Wrap, 390 Primeiro, Fosco, Cromado É Luz (DESIGN.md, medido aqui).
- **`aula-base.md`:** §Figura (uma por seção, imagem domina) e §base interna (resumo, verso e apostila não entram em Referências) (s236, commit).
- **`estilo-flashcard.md`:** §Realce e referência. Regra **provisória**: a fonte vai no fim do `verso_regra_mestre` entre colchetes, `[Fonte: ...]`; "card sem fonte não entra"; revisar em 2026-11-15; sai quando o banco de evidências entrar (estilo-flashcard).
- **Sidecar do impeccable:** `.impeccable/design.json` regenerado (componentes novos: Paginador da questão; Certeza e Responder; Rosa Realça) e `.impeccable/config.json` novo, com a **exceção `side-tab`**: o detector ignora a regra só em `core/templates/player.html` (filete das seções do card e do aviso, decisão do tema v4 da s227, pré-existente) (s236, commit).
- **Espelhos de skill:** `.agents/skills/source-command-aula-base` e `estilo-flashcard` têm alteração **sem commit** no working tree (`git status`, medido aqui); `sync_skills.py --check` dá paridade OK (medido aqui). `exchange-log.jsonl` e `generation_log.jsonl` também ficam sem commit (repo público).

### (e) Auditoria UI/UX (impeccable)

Relatório: `docs/research/2026-10-30-06-ui-auditoria-impeccable.md`. Somente leitura; rodou em contexto único (sem subagente aninhado).

- **Critique (Nielsen): média 27/40**, banda Aceitável, no topo; igual a 19/10. Painel 26, Teoria 29, Listas 26, Questão 29, Fim 24, Cards 27, Leitor 28. O fim de lista é o pior; Questão e Teoria são o melhor.
- **Audit técnico: 15/20 (Bom)**, desceu 1 ponto desde 19/10 (16/20). Causa: incrementos de 29-30/10 aplicaram regras dele pela metade.
- **Achados:** 0 P0, 4 P1, 14 P2, 7 P3 (25 no total). Detector: 342 ocorrências, cerca de 95% falsos positivos sancionados pelo DESIGN.md; só 2 verdadeiros (meta a 4,4:1 e o "+N" do gráfico a 11,2 px). Evidência: 33 capturas, zero rolagem horizontal e zero erro de JS em 11 cenas por 3 larguras; tema claro conferido a 390 px.

**Aplicados hoje (Version 144):**

| ID | Prio | O que corrigiu |
|---|---|---|
| U1 | P1 | Aula lida não tira do Hoje a tarefa com lista pendente (Painel e Listas concordam) |
| U2 | P1 | Voltar sempre "< Listas"; título e relógio na 1ª linha, determinístico |
| U3 | P1 | Meta em `tinta2` sobre o cartão tingido (era 4,4:1) |
| U5 | P2 | Simulados com título curto (mantém "parte N") |
| U6 | P2 | "Resolver" apagado também na RD |
| U11 | P2 | Acentos do player (valor gravado "Erro de portugues" intacto) |
| U12 | P2 | `aria-pressed` na certeza |

**Abertos (P2 e P3 ficam para o ai-eng priorizar, P47):**
- **P1:** U4 -- "Lista concluída" fica fixo com o Concluir travado por declarações pendentes (esforço S). Conferido: `hub.html:639` segue estático. O P47 foi corrigido no backlog: 3 dos 4 P1 aplicados; U4 fica para a próxima sessão de engenharia.
- **P2 (10):** U7 Virar some no verso do card (S) · U8 relógio com moldura de botão (S) · U9 paginador a 36 px no celular, regra é 44 (S) · U10 Responder apagado parece 4ª opção (S) · U13 dois resumos do Hoje com vocabulários diferentes (S) · U14 área e cor diferentes entre Painel e Listas (M) · U15 "Erradas: 1, 4, 5" não é tocável (M) · U16 três matizes de realce no leitor (M) · U17 rótulo "coágulo" colidiu com o título na Fig 1 da RD CM, conferir antes de publicar (S) · U18 "197 de 100 hoje" com barra vazia (M).
- **P3 (7):** U19 a U25: "+12" a 11,2 px; `.t-btn-off` com borda invisível; sem `h1`; × de riscar na revelada; 6 pesos de fonte pedidos; título duplicado no leitor (só registrar); "Aa Grifo" x "Aa" no celular.

**As 4 perguntas fechadas para ele (auditoria, "Decisões dele"):**
- **D1 (U1):** tarefa com aula lida e lista pendente. (a) fica no Hoje até resolver; (b) sai e as questões saem do total; (c) como estava. Recomendação (a).
- **D2 (U2):** voltar do fim da lista. (a) sempre "< Listas"; (b) rótulo distinto, ex. "< Resultado"; (c) "< Lista". Recomendação (a).
- **D3 (U14):** rótulo de área no cartão. (a) grande área UERJ nas 3 abas; (b) disciplina nas 3; (c) como hoje. Recomendação (a).
- **D4 (U16):** realce na leitura depois do rosa. (a) termo-chave em branco 650 e rosa único colorido; (b) termo-chave segue ciano e rosa só no dado decisivo; (c) termo-chave em roxo-tinta. Sem recomendação forte (a desfaz pedido dele de 12/10).
- **Estado:** U1 e U2 foram aplicados na opção (a), a recomendada, sem esperar a resposta dele (autonomia de recalcular rota; reversível). D3 e D4 esperam.

### (f) Banco de evidências

Origem: regra dele em 30/10, *"Não podemos referenciar resumos, apenas artigos, guidelines, consensos, etc. Inclusive, a partir de hoje, todos os cards devem conter referências"*, mais a proposta de um banco separado no molde do `daktus-content` (s236, P43).

**Decisões dele (ADR, "já tomadas no ato", não reabertas):** (1) `ipub.db` é banco de performance e o banco de evidências é outro database; (2) ele pode beber do `ipub.db` para se povoar; (3) nenhuma evidência entra sem referência que a sustente, e resumo, apostila e verso de card não são referência; (4) a partir de 30/10 todo card novo carrega referência; (5) **GO ao ADR** com revisão (PD-20261030-05, resolvida em 30/10 ~19h BRT): fila de evidências estilo inbox e gate "nada estrutural antes de 02/11" **desarmado**; F1 começa em 30/10 (ADR, Adendo 2).

**Estado de cada peça:**

| Peça | Estado | Prova |
|---|---|---|
| ADR v1.1 (ai-eng) | ACEITO | commit `2c8bd10` do ai-eng |
| Pacote `evidence-bank` (repo próprio `C:/Users/daanm/evidence-bank/`) | entregue; selftest 6/6 segundo o commit; não reexecutado aqui; o ai-eng marca o código como "não observado" | commit `9d86181` (medido aqui) |
| Backlog P43 no MedHub | ABERTO | commit `01d46b6` |
| Aplicação no MedHub (9 passos) | APLICADA em 30/10 ~21h: `init` + `beber-fontes` na cópia e no ipub real (resultados idênticos); quarentena dentro de `ativo_where()`; 3 writers de card com quarentena + fila; `evidence-researcher` com o JSON; contrato v1.5; 10 testes novos; fila de véspera intacta (mesmos 100 cards) | commit de fechamento da s236 (o que inclui este report); fecha a PD-20261030-08 |
| Regra provisória `[Fonte: ...]` | em vigor desde 30/10; 0 cards com fonte até hoje (ADR) | commit `01d46b6` (estilo-flashcard) |

**O que o ADR decidiu (6 bifurcações):** (1) `evidencias.db` separado, na raiz, gitignored, sem FK entre bancos (id textual `ev-<hash>`), `referencia` do ipub só copiada; (2) grão = uma linha por afirmação clínica, com N fontes; (3) pontes N:N `card_evidencia` e `questao_evidencia` no ipub (o ai-eng divergiu da coluna única proposta; o MedHub concordou); (4) sem retroação em massa, o card entra pela reforja e pelos lotes novos; (5) `evidence-researcher` produz JSON importável, e item sem fonte nunca entra como evidência; (6) gate dos inserts a partir de F2, reforja e aulas em F3, importador do `daktus-content` em F4.

**Fases (ADR, Adendo 2, re-datadas):** F1 de 30/10 a 01/11 (`init`, schema, pontes, fontes, `fila-add`, `triar`, `status`, `selftest`); F2 depois (`pesquisar`, `folha`, `decidir`, inserts com quarentena); F3 reforja e aulas com Referências geradas; F4 importador do content, em janela com tokens sobrando (D110).

**O pacote (evidence-bank README):** Python 3.11+ só com stdlib, SQLite, sem LLM e sem rede. Sete invariantes checadas pelo código, entre elas: evidência órfã = 0, toda evidência nasceu de uma decisão, `auditoria` append-only, só fonte `publica`. Fila: `aberta`, `triada`, `pesquisada`, `decidida`. Comandos: `init`, `add-fonte`, `fila-add`, `triar`, `pesquisar`, `folha`, `decidir`, `buscar`, `status`, `export`, `beber-fontes`, `beber-solucoes`, `quarentena-sql`, `selftest`. Exit 3 = recusa de gate.

**O que o MedHub aplicou (ai-eng, pacote de 9 passos; feito em 30/10, s236):**

| # | Onde | O que fazer |
|---|---|---|
| 1-3 | `.gitignore`, raiz | `*.db` já cobre `evidencias.db`; `init --ipub` (antes, cópia do `ipub.db`) cria o banco, o watermark e as 2 pontes; `beber-fontes` copia `referencia` pública para `fonte` |
| 4 | `app/utils/db.py:72` | conjunção de quarentena dentro de `ATIVO_WHERE` e `ativo_where()`; recriar a view `flashcards_ativos` |
| 5 | `insert_card_base.py`, `insert_questao.py` | card novo sem ponte ativa entra em quarentena (não é servido ao FSRS), nunca recusado |
| 6 | `.claude/agents/evidence-researcher.md` | emitir também o JSON de intercâmbio |
| 7 | inbox do MedHub | `folha` gera a PD de decisão; ele assina; `decidir --folha` aplica |
| 8 | `core/contracts/evidence-governance.md` | v1.5 |
| 9 | `docs/REFORMA-CHECKPOINT.md` | registrar o banco como item da Fase 1 |

- **Quarentena:** vale só para `flashcards.id` acima do watermark; os 2.146 legados seguem servidos e entram pela reforja (ADR).
- **Base que já existe:** `referencia` com 247 linhas (33 `publica`, 93 `propria`, 121 `terceiro`) e `solucao_referencia` com 821 vínculos, desde 12/10 (M-031); o banco nasce daí, não do zero (ADR, s236).
- **Divergência de contagem:** o ADR diz 2.146 flashcards; o HANDOFF diz 2106 cards ativos (derivado). É total x ativos: o ADR contou `flashcards` inteira; o HANDOFF conta pelo `ATIVO_WHERE`.
- **Não fazer agora (ai-eng):** `beber-solucoes` em massa, reforja para a fila, aulas com Referências geradas e a delegação ao agente.
- **Inbox do ai-eng:** PD-06 (delegação), PD-07 (onde o pacote mora), PD-08 (esta aplicação), PD-10 (F4); a PD-09 (relatório em PDF) já fechou. Report ao ai-eng: `~/ai-eng/HANDOFF-MEDHUB-banco-evidencias-2026-10-30.md` (ai-eng, s236).

### (g) Divergências clínicas achadas hoje, NÃO aplicadas

Nenhum resumo foi editado (os briefs proibiram). As aulas já ensinam a versão "depois". Decisão dele, depois da prova. São 14 itens numerados nos dois arquivos (6 + 8), todos abaixo: o item 4 da parte 2 tem duas pendências (linhas 5 e 6) e o item 5 de líquidos vem junto do 4 (linha 11) (liquidos, aulao2).

**Resumos do MedHub (`.md`):**
1. `Meningites.md` §3, l.31, tríade de Cushing. Antes: "bradipneia + hipertensão arterial + arritmias respiratórias". Depois: hipertensão (pressão de pulso alargada) + bradicardia + respiração irregular. Fonte: já correto em `TCE.md` l.106 e 169; Harrison, não conferido no original (liquidos 1).
2. `DRGE, Esofagites e Corpo Estranho.md`, esofagite eosinofílica. Antes: "mediada por IgE". Depois: doença imune/antígeno-mediada (tipo 2), em geral não mediada por IgE; IgE específica não guia a dieta de exclusão. Fonte: Dellon et al., consenso AGREE, Gastroenterology 2018;155(4):1022-1033 (aulao2 1).
3. `Hérnia Femoral Encarcerada.md` §3 (Lichtenstein). Antes: tela fixada "ao tubérculo púbico e ao tendão conjunto". Depois: borda inferior em sutura contínua no ligamento inguinal, do tubérculo púbico até além do anel interno; superior no tendão conjunto. A UERJ 2024 Q40 cobrou. Fonte: HerniaSurge, Hernia 2018;22(1):1-165; Sabiston 21ª ed. (aulao2 2).
4. `[GIN] Climatério e TH.md` §4, propedêutica (banca-dependente). Antes: "mamografia (40a)", FEBRASGO. Depois (acrescentar): na UERJ vale o MS, mamografia 50-74 anos a cada 2 anos; 40-49 só por decisão compartilhada; colo pelo DNA-HPV. Fonte: INCA, Diretrizes de detecção precoce do câncer de mama, 2015 (aulao2 3).
5. `Endometriose.md` §8.1 não nomeia a 1ª linha hormonal. Depois: progestágeno contínuo ou pílula; GnRH é 2ª linha. Fonte: ESHRE 2022; pendência antiga em `tmp/uerj2024/GO/divergencias.md` item 3 (aulao2 4).
6. Hipotireoidismo subclínico e glicemia de jejum 102 (UERJ 2025 Q84, MFC). Pendência antiga, `tmp/uerj2025/MFC/divergencias.md` itens 1 e 2; fontes BMJ 2019 e OMS/MS. Coincide com a correção (d) da s235 (aulao2 4).
7. `Infecção de Trato Urinário em Pediatria (ITU).md` é esboço. Faltam: imagem depois da 1ª ITU febril (USG; UCM se alterado ou recidiva), disfunção vesicointestinal, Enterococcus com uropatia, nefropatia do refluxo (DRC/HAS). A UERJ cobrou os quatro (2022 Q37, 2023 Q65, 2025 Q68 e Q69). Fonte: AAP, Roberts, Pediatrics 2011;128(3):595-610; ICCS, Austin, Neurourol Urodyn 2016;35(4):471-481 (aulao2 5).
8. Sem resumo `.md`: glomerulares, nódulo e câncer de tireoide, hipotireoidismo, hérnia de hiato, acalasia e Zenker, câncer gástrico e de esôfago, incontinência urinária, prolapso, infecções congênitas (exceto sífilis). É lacuna, não erro (aulao2 6).

**PDFs do curso (só registro; a aula cita a fonte primária):**
9. `6. Complicações da Cirrose Hepática.pdf`, profilaxia primária da PBE. Antes: "ureia ≥ 25 mg/dl". Depois: BUN ≥ 25 mg/dL (ureia ≥ ~53 mg/dL; ureia = BUN x 2,14). Com "ureia ≥ 25" quase todo cirrótico entraria. Fonte: Fernández et al., Gastroenterology 2007;133(3):818-824; AASLD 2012 (liquidos 2).
10. `15. Pericardiopatias.pdf`, tamponamento. Antes: "via cirúrgica (janela pericárdica) é preferível". Depois: pericardiocentese guiada por eco é a via padrão; cirurgia na purulenta, no hemopericárdio (trauma, dissecção de aorta) e no derrame loculado ou recidivante. Fonte: ESC 2015, Adler et al., Eur Heart J 2015;36:2921-2964, lido de memória: conferir no original antes de mexer em card. UERJ 2025 Q4 deu pericardiocentese (liquidos 3).
11. Mesmo PDF, pericardite urêmica. Antes: corticoide "útil em etiologia ... urêmica"; a tabela da mesma apostila diz "diálise de urgência". Depois: diálise (intensificar); anti-inflamatório só se não responder. Fonte: ESC 2015, não conferido no original (liquidos 4). Já registradas em `tmp/uerj2025/CM/divergencias.md` itens 5 e 6 (liquidos 5): o PDF de Pericardiopatias põe Kussmaul no tamponamento (é da constrição) e a Tabela 8 do PDF de Choque diz que só o cardiogênico tem capilar pulmonar alto.
12. `8. Neoplasias de Estômago e Esôfago.pdf`, margem proximal da gastrectomia subtotal. Antes: 6 cm (bem diferenciado) e 10 cm (indiferenciado). Depois: 3 cm (expansivo) e 5 cm (infiltrativo), número do card da RD de neoplasias do TGI de 05/10. Fonte: JGCA 2018, Gastric Cancer 2021;24(1):1-21 (aulao2 7).
13. `29. Hérnia da Parede Abdominal.pdf`, hérnia umbilical. Antes: tela para defeito acima de 3 cm. Depois: tela a partir de 1 cm. Fonte: EHS/AHS, Henriksen et al., Br J Surg 2020;107(3):171-190 (aulao2 8).

**Mapa da UERJ:**
14. `uerj_mapa_questoes` (em `simulados/uerj/`), 2023 Q8. Antes: foco "ascite de GASA baixo, suspeita de TB peritoneal", tema Tuberculose. Depois: ascite de GASA baixo com proteína baixa = síndrome nefrótica (proteinúria e biópsia renal); tema Doenças Glomerulares. Fonte: gabarito pós-recurso 2023 (Q8 = C) e `tmp/lote_uerj2023.json`; contar a Q8 em TB infla o peso de TB no mapa (liquidos 6).

## 3. Arquitetura do MedHub

Fonte principal: **ai-eng, sabatina de 28/10 + resumo de 30/10** (`C:/Users/daanm/ai-eng/artifacts/2026-10-30-medhub-arquitetura-resumo-para-report.md`), incorporado com as ressalvas dele. Cruzado com `AGENTE.md`, `DESIGN.md` e `docs/REFORMA-CHECKPOINT.md`. Onde o ai-eng escreveu "não observado", este texto repete a marca. Contagens "(medido aqui)" são de 30/10.

### 3.1 Mapa em camadas

```
+-----------------------------------------------+
| 7 IRMAOS: /ai-eng (orquestra), evidence-bank  |
| 6 GOVERNANCA: HANDOFF, ESTADO, history/,      |
|   backlogs, ledger (selo.py)                  |
| 5 HARNESS: pre-commit, auto_check, suite      |
| 4 AGENTE: skills, workflows, evidence-        |
|   researcher, memoria                         |
| 3 HUB: Artifact, ArtifactData, player,        |
|   painel, leitor                              |
| 2 NUCLEO: app/utils/db.py + CLIs em tools/    |
| 1 DADOS: ipub.db, core/*.json, contratos,     |
|   resumos/                                    |
+-----------------------------------------------+
```

### 3.2 As camadas, uma a uma

**1. Dados** (ai-eng §1)
- **`ipub.db`:** SQLite local-only, `user_version` 0; é o SSOT operacional (AGENTE §5.5). Tabelas por papel: cards e FSRS (`flashcards` e a view `flashcards_ativos`, `fsrs_cards`, `fsrs_revlog`, `reforja_marks`, `emed_card_ancora`); erros e habilidades (`questoes_erros`, `habilidades`, `questao_habilidades`); questões e fontes (`emed_questoes`, `emed_respostas`, `emed_solucoes`, `referencia`, `solucao_referencia`); plano e revisão (`taxonomia_cronograma`, `plano_tarefas`, `plano_dia`, `preparacao_estado`, `review_log`, `sessoes_bulk`).
- **Classificação de 10/10:** 11 SSOT; `fsrs_cards` é replay do revlog (derivada); `plano_dia` é telemetria. Cinco riscos de migração: 3 regimes de fuso, ids virados chave natural, revlog não append-only (`cards_prune`), JSON em TEXT, estado que pode existir só no db do artifact.
- **`core/*.json`:** `areas`, `provas`, `sprint`, `fsrs_params`, `hub_quadro`, `hub_resumos`, `objetivos`, `lastro_alias` (medido aqui: 8 arquivos) e `core/cronograma/*.json`.
- **9 contratos normativos** em `core/contracts/` (medido aqui: 9): cronograma, estado, evidence-governance (v1.4), forgetting-curve, fsrs-management, handoff, orquestracao, reconcile, revisao-calibrada.
- **Conhecimento clínico:** `resumos/**/*.md` em git, 136 resumos (HANDOFF, derivado). Os PDFs-fonte do EMED são retidos em `resumos/` (AGENTE §7.3).
- **Não observado pelo ai-eng:** conteúdo das linhas do `ipub.db` (só schema e COUNT em modo `ro`, 28/10).

**2. Núcleo e CLIs** (ai-eng §2)
- **`app/utils/db.py`:** único writer do `ipub.db` e ponto de troca previsto da plataforma. `ATIVO_WHERE`/`ativo_where()` é a definição única de card ativo. Em volta: `fsrs.py`, `fsrs_balance.py`, `regua.py`, `card_checks.py`, `card_atomicity.py`, `relogio.py`, `areas.py`, `provas.py`, `notas_player.py`.
- **58 CLIs** de nível superior em `tools/` (ai-eng 28/10; medido aqui: 58). Por papel: estudo (`fsrs_queue`, `fsrs_load`, `reforja`, `review_radar`, `dormant_refresh`, `insert_questao`, `insert_card_base`, `insert_card_extra`); plano (`day_plan`, `plano`, `trilha`, `cronograma`, `performance`); banco de questões (`emed_api`, `emed_banco`, `prova_pdf`); entrega (`hub`, `painel`); engenharia (`auto_check`, `selo`, `reachability_check`, `backup_db`, `init_db`, `sync_skills`, `setup_hooks`).
- **Regra de assinatura:** cada CLI tem a assinatura canônica em UMA skill (AGENTE §7.2); a tabela de CLIs (§7.4) é gerada por `reachability_check.py --tabela`.

**3. Hub** (ai-eng §3; DESIGN.md)
- **Build:** `tools/hub.py --build` lê o `ipub.db`, `hub_quadro.json`, `hub_resumos.json`, `artifacts/painel.html` e o lote de `fsrs_queue.py --export-player`, e gera o `index.html` de `core/templates/hub.html`, `player.html` e `tema.css`.
- **Publicação:** é a ferramenta Artifact acionada pelo agente, nunca pelo código. Um artifact, URL fixa (HANDOFF), hoje na Version 144.
- **ArtifactData** (db do artifact): `sessoes/<lote>/notas`, `respostas/*`, `listas/*`, `quadro/<slug>`, `analises/*`.
- **Abas:** Painel, Teoria, Listas (Questões e Simulados), Cards. O **player** grava a nota 1-4 no FSRS-6; o **painel** é `tools/painel.py`, derivado do banco; o **leitor** abre aulas e resumos em iframe com `tema-aula.css`.
- **Backend = tique** `/hub-backend`: lê o ArtifactData e grava `emed_respostas`, `sessoes_bulk`, `plano --concluir` e o FSRS (`--record-lote`) no `ipub.db`.
- **Fronteiras declaradas (HANDOFF):** o backend só vale com o PC acordado e a sessão aberta; o cron só dispara com o REPL ocioso; 1 tique por subagente custou 243 mil tokens e 33 min em 28/10, por isso hoje é à mão, sem cron.
- **Dívidas:** `hub.html` monolítico com JS inline (MH-17); tetos do artifact (255 entradas, 25 mil docs, 256 KiB por doc); sem autenticação (ai-eng). Página de 617 KB (auditoria).
- **Não observado pelo ai-eng:** conteúdo do db do artifact e o hub publicado (que ele viu na Version 136).

**4. Agente: skills, `.claude` e memória** (ai-eng §4)
- **15 skills** em `.claude/commands/` (medido aqui: 15; ai-eng: 15): `/revisar`, `/analisar-questao`, `/aula-base`, `/banco-emed`, `/engenharia-cli`, `/pesquisar-evidencia`, `/estilo-flashcard`, `/estilo-resumo`, `/cronograma`, `/performance`, `/hub-backend`, entre outras. Skill é referência atômica; o workflow (`.agents/workflows/`, 6 arquivos, medido aqui) orquestra (AGENTE §7.2).
- **1 agente:** `.claude/agents/evidence-researcher.md`, sem Bash; devolve afirmação, veredito e fonte; governado por `evidence-governance.md` v1.4.
- **Hooks:** 2 em `.claude/settings.json` (`SessionStart` roda `memory_boot.py`; `PostToolUse(SendMessage)` roda `exchange_log.py`). Espelho `.agents/skills` gerado por `sync_skills.py` (uso não medido, MH-21).
- **Memória:** 1 camada, canônica em git (`AGENTE.md`, `ESTADO.md`, `HANDOFF.md`, `resumos/`, `ipub.db`). LangMem, RAG e Chroma saíram em 11/10. A memória automática do harness é decorativa: regra load-bearing vive no repo (AGENTE §8, §10.5).

**5. Harness** (ai-eng §5)
- **Pre-commit:** `.git/hooks/pre-commit` (fora do git), instalado por `setup_hooks.py`; roda `auto_check.py`, que dispara a suíte quando mudam `tools/`, `app/`, `core/`, `artifacts/`, `.claude/` ou `.agents/`.
- **Sensores no `auto_check`:** `BANCO_NO_RECORTE`, `CONTRATO_REVOGADO`, `DOC_DRIFT`/`DOC_REF`, `MEMORY_POINTERS`, `SUITES_ORFAS`, `HANDOFF_LONGO`, `POSICAO_DRIFT`, `ERROS_ORFAOS`, `PAINEL_DIVIDA`; mais `reachability_check` e `selo.py`.
- **Suíte:** 1.819 testes coletados em 28/10 (ai-eng); 1825 passed hoje (s236); 110 arquivos `test_*.py` (medido aqui); 12 marcados `vivo`; fixture `db_sintetico` (ai-eng).
- **Reconcile:** contrato v1.4, implementação parcial (matriz de 10/10, não rechecada). **CI:** ausente (0 workflows; `main` sem proteção). **Não observado pelo ai-eng:** execução da suíte e tempo de boot.

**6. Governança: sessões, handoff, backlog, ledger**
- **`HANDOFF.md`** (estado operacional curto, lido primeiro no boot) e **`ESTADO.md`** (macro) (AGENTE §2).
- **`history/session_NNN.md`** por sessão, mais `history/INDEX.md` e o `exchange-log` (AGENTE §3).
- **Backlogs:** `docs/BACKLOG-PRODUTO.md` (pedidos dele, até o P48) e `docs/BACKLOG-UNICO-MEDHUB.md` (engenharia, M-001 a M-120 segundo o HANDOFF).
- **Ledger:** `AUDITORIA_MEDHUB.md` (só o aberto) e `history/auditoria/resolvidos.md`; `python tools/selo.py` mostra aberto x resolvido x limite (HANDOFF).
- **Rito de fechamento:** HANDOFF, ESTADO se o macro mudou, `session_NNN`, auto-higiene, commit semântico (AGENTE §3).

**7. Agentes irmãos**
- **`/ai-eng`:** orquestra a reforma, as specs e as decisões; o MedHub é o executor e audita pelo loop do vibeflow (AGENTE §10.6). Os dois editam o mesmo repo (AGENTE §10: reler antes de escrever; preservar bloco alheio).
- **`evidence-bank`:** pacote próprio e standalone (ver 2(f)); consumo por CLI ou `import`; sem import de `medhub/` nem de `daktus-content/` (ai-eng §7).

### 3.3 Fluxo de um dia de estudo

```
[1] LISTA no hub (aba Listas, player de questoes)
      | letra + certeza + elos declarados
      v
[2] ArtifactData: respostas/*, listas/*,
      | sessoes/<lote>/notas
      | tique (/hub-backend), hoje a mao
      v
[3] ipub.db: emed_respostas, sessoes_bulk,
      | plano_tarefas
      v
[4] ANALISE dos erros (/analisar-questao)
      | insert_questao.py: questoes_erros, habilidades
      | analises/* voltam ao hub
      v
[5] CARDS (insert_card_base, estilo-flashcard)
      v
[6] FSRS (fsrs_cards, fsrs_revlog)
      | fsrs_queue.py --export-player
      v
[7] FILA do dia (lote AAAA-MM-DDx) -> aba Cards
      | nota 1-4 no player -> ArtifactData
      v
    volta ao [3] no proximo tique (--record-lote)
```

Os passos 2 para 3 e 7 para 3 só acontecem no tique. Sem tique, o hub guarda e o banco não sabe (HANDOFF, ai-eng §3).

### 3.4 Fluxo de uma aula

```
[1] PEDIDO dele (tema, peso na UERJ)
      v
[2] BRIEF do principal (acentos; /aula-base,
      | /anima; sem resumo em Referencias)
      v
[3] SUBAGENTE Opus -> artifacts/aula-<slug>.html
      v
[4] PRINCIPAL le inteira e confere
      v
[5] core/hub_quadro.json (registro da aula)
      v
[6] hub.py --build -> Artifact publish (mesma
      | URL) -> --confirmar
      v
[7] LEITOR do hub (iframe + tema-aula.css)
      | grifos e perguntas -> ArtifactData
      v
[8] ASSINATURA (assinar = concluir a tarefa;
      RD alimenta o review_log)
```

Fontes: s236 (passos 2 a 6), DESIGN.md §Leitor de aulas, memória do projeto (assinar = concluir). Passo 8: `hub-assina*` em `hub.html` (DESIGN.md); a ligação da RD com o `review_log` vem do AGENTE §7.3 (`/revisar`).

### 3.5 O que é SSOT de quê

| Domínio | SSOT | Commit? | Fonte |
|---|---|---|---|
| Erros, FSRS, cronograma, `review_log` | `ipub.db` | não | AGENTE §5.5 |
| Ordem e conclusão das tarefas | colunas de `plano_tarefas` | não | HANDOFF |
| Agenda do sprint | `core/sprint.json` | sim | HANDOFF |
| Áreas, provas, parâmetros FSRS | `core/areas.json`, `provas.json`, `fsrs_params.json` | sim | ai-eng §1 |
| O que é card ativo | `ATIVO_WHERE`/`ativo_where()` em `db.py` | sim | ai-eng §2 |
| Quadro do hub (aulas, RDs) | `core/hub_quadro.json` | sim | ai-eng §3, s236 |
| Conhecimento clínico | `resumos/**/*.md` | sim | AGENTE §5.5 |
| Regras normativas | `core/contracts/*.md` (9) | sim | ai-eng §1 |
| Tokens visuais | `core/templates/tema.css` | sim | DESIGN.md |
| Contrato visual | `DESIGN.md` (sidecar `.impeccable/design.json` é derivado) | sim | DESIGN.md, s236 |
| Estado macro e operacional | `ESTADO.md` e `HANDOFF.md` | sim | AGENTE §2, §5.5 |
| Pedidos dele | `docs/BACKLOG-PRODUTO.md` | sim | backlog |
| Fontes das Soluções | `referencia`, `solucao_referencia` (ipub) | não | ADR |
| Evidências (desde 30/10) | `evidencias.db` (evidence-bank), raiz do repo, gitignored | não | ADR, s236 |
| Estado vivo da página | db do artifact; o backend grava no `ipub.db` | não | ai-eng §3 |
| Chaves de API; memória do harness (decorativa) | `.env`; `MEMORY.md` | não | AGENTE §5.5, §10.5 |

### 3.6 Dívidas abertas

Os números envelhecem: cada linha traz data e fonte.

| Dívida | Fonte e data |
|---|---|
| Cópia off-machine do `ipub.db` parada desde 11/10 (MH-06, M-147); D-07 | ai-eng 30/10; HANDOFF |
| Repo PÚBLICO com cópia do banco de 14/03, `exchange-log` integral e 8 enunciados no histórico (D-01); sem CI, `main` sem proteção, descrição do GitHub falsa | HANDOFF 28/10; ai-eng (MH-05, MH-28) |
| `db.py` é god module e importa `event_log` (app para tools); schema sem versão (DDL espalhado, `user_version` 0) | ai-eng (MH-07, MH-14, MH-16) |
| Leitores que escrevem: `selo.py`, `performance.py` e outros abrem o `ipub.db` em escrita (`get_connection` roda DDL) | HANDOFF; ai-eng (MH-10: 6 de 7) |
| `auto_check.main()` com 889 linhas; pins em `requirements.txt` e `.venv` documentado que não é o usado; contexto de boot sem teto em bytes | ai-eng (MH-08, MH-01, MH-02, MH-19, MH-20) |
| Espelho `.agents/skills` sem uso medido; `settings.local.json` versionado com regras mortas | ai-eng (MH-21, MH-22) |
| Reforma pausada desde `7bd5642` (11/10 22:09), retomada prevista para 02/11; Lote 3 (docs), Lote 4 (dados: fuso, ids congelados, `cards_prune` sem DELETE) e Lote 5 (medições) não executados | ai-eng; `git log` (medido aqui); CHECKPOINT 11/10 |
| Lote 3 docs: M-105, M-120, M-121, M-128, M-131 (`tmp/` solto), M-132, M-133, M-135, M-137 a M-139, M-146, M-149, M-150, M-152; M-154 (`init_db --help` abre o banco real em escrita) e M-155 (gate isenta por "antigo" ou "morto") | CHECKPOINT 11/10; commit `7bd5642` |
| `referencia`: apply do estoque adiado para depois de 01/11 (M-031); M-141: 491 PDFs (6,2 GB) e `decks/cards.json` (379 MB) fora de qualquer cópia; M-136 retenção do repo de backup; M-130 `tmp/alca_s213` é decisão dele | CHECKPOINT 11/10 |
| Selo: 3 abertos (F39, F69, F111 com prazo 02/11), 118 resolvidos, 5 limites (medido em 28/10); **não fecha desde 20/10** (F128 com revisão vencida); F78 limite (revisar 02/11); F110 sem gate | HANDOFF |
| ~40 achados da sabatina fora do ledger, em `tmp/aieng/`, entram só com o veredito dele | HANDOFF |
| Sem trava na entrada: 11 cards da s216 nasceram sem acento (hotfix proposto) | HANDOFF (s217) |
| Reforja: 5 marcas abertas (#774, #987, #988, #432, #1439) e 4 novas de hoje (#1021, #524, #281, #564) | HANDOFF; s236 |
| P48 (referências internas em aulas e RDs antigas); 2 worktrees vazias para limpar (o classificador barrou o agente); 7 arquivos de imagem soltos e não rastreados na raiz do repo público | P48; HANDOFF; `git status` (medido aqui) |
| Memória automática do harness com fato vencido ("34 aulas"; são 67; medido aqui: 67) | ai-eng, consolidado v2 |

### 3.7 O que ninguém observou

Repetido do ai-eng e do HANDOFF para não virar certeza: conteúdo das linhas do `ipub.db` e do db do artifact; execução da suíte e tempo de boot (a suíte 1825 é do log da s236, não reexecutada aqui); código do `evidence-bank` como entregue (este rascunho viu o README e o commit, não rodou o selftest); o reconcile (B3, B4, W2 e W4 "sem implementação" na matriz de 10/10, não rechecado); e "o ai-eng não re-auditou o MedHub hoje" (ai-eng).

## 4. Próximos passos

**30/10 (noite):** ele faz o UERJ 2026 (t890, 93 questões) no hub; backend à mão, 1 tique quando ele voltar. Com a t890 resolvida: registrar (`--area Simulado`, `--sessao 236`, acerto por bloco na observação), analisar pelos elos declarados (mais de 8 erros = 1 subagente Opus por bloco), RD por bloco e republicar (HANDOFF, item 0).

**31/10 (véspera leve):** aulão (partes 1 e 2), líquidos, UERJ de Bolso e as 5 RDs da 2025; cards só se a fila `2026-10-31a` (100) for curta (HANDOFF, s236). A rota da s233 previa o UERJ 2026 inteiro em 30/10; ele decidiu começar hoje à noite e terminar amanhã, junto de mais cards (mensagem dele de 30/10). A véspera fica, portanto, metade simulado e metade leitura; a trilha não muda por isso. **01/11:** prova UERJ/MFC, inscrito (HANDOFF).

**02/11 em diante:**
- Recalibrar a trilha pelo acerto acumulado das 6 UERJ (antes da 2025 e 2026: CIR 60% < CM 61% < PED 64% < GO 64% < MFC 85%) (HANDOFF).
- Banco de evidências: F2 (`pesquisar`, `folha`, `decidir`; a 1ª folha espera a correção do `beber-solucoes`, que hoje grava a Solução inteira como afirmação -- defeito reportado ao ai-eng), F3 (reforja e aulas) e F4 (importador do content, PD-10) (ADR, ai-eng, s236).
- Auditoria de UI: U4 (P1), os 10 P2 e os 7 P3, com o ai-eng priorizando (P47). P48: limpar referências de resumo nas aulas e RDs antigas (P48).
- Reforma retomada (prevista para 02/11); selo com F111 (prazo 02/11) e F78 (revisar 02/11) (ai-eng, HANDOFF). Norte de longo prazo: Psiquiatria/IPUB via ENAMED 2027 (HANDOFF).

## 5. Decisões que esperam ele

**A. Correções clínicas da s235 (linha PARA VOCE do HANDOFF; antes, depois e fonte em `tmp/uerj2025/*/divergencias.md` e `tmp/aulao/divergencias.md`):**
1. `HIV.md`: DTG "contraindicado no 1º trimestre" para TDF+3TC+DTG em qualquer idade gestacional (PCDT TV 2022; só fonte secundária, abrir o PDF antes).
2. `Síndrome de Down.md`: ortopédica mais comum = pé plano (91%, Foley 2019), não a atlantoaxial; endocrinopatia mais frequente = hipotireoidismo.
3. `Meningites.md`: na UERJ (Nelson e Harrison), lactente acima de 3 meses = cefalosporina de 3ª + vancomicina (UERJ 2024 Q73; proposto na s231).
4. `Diabetes Mellitus Tipo 2.md`: a UERJ MFC usa glicemia de jejum alterada a partir de 110 (OMS/MS), não 100.
5. `Planejamento Familiar.md` l.125: "CA de mama < 5 anos" para "sem doença há 5 anos" (OMS MEC 2015).
6. `Arboviroses.md` sem Oropouche (Q2 da 2025).
- Mais as **14 divergências de hoje** (seção 2(g)) e as antigas: Rastreamento do Colo §4 AGC endométrio ">= 45" para ">= 35 ou qualquer idade com sangramento" (PDF EMED 21 p17, MS 2016); `Meningites.md` herpética "> 50 anos" para qualquer idade; `Trauma.md` l.244 "cobrir vísceras" não é a etapa E (HANDOFF, s226).
- Pendentes antigas: Q30, Q44 e Q47 da UERJ 2021; 2 da RD de Hérnias; SHG §2; profilaxia de HBV com rituximabe (HANDOFF).

**B. Pendências no hub (declaração não bate com a marcação):** UERJ 2025 Q43, Q56, Q58, Q65 e Q80 (HANDOFF). Não abrir o dossiê de terceiros antes de 2024, 2025 e 2026 (HANDOFF).

**C. As 4 perguntas da auditoria:** D1 a D4 (seção 2(e)). D1 e D2 já aplicadas na opção (a); reversíveis se ele preferir (b) ou (c).

**D. Do ai-eng (inbox):**
1. **PD-20261030-06:** ligar ou não a delegação ao agente na decisão da fila de evidências (confirmado + Tier 1 BR, ou canônico com PMID). Até ele decidir, tudo vai à folha assinada por ele (ai-eng).
2. **PD-20261030-07:** onde o `evidence-bank` mora (só local; repo privado no GitHub; ou dentro da org Daktus). Proposta: privado no `daanmt` até o 1º consumidor real da Daktus. Prazo 03/11. A PD-05 (GO ao ADR) já está resolvida com a assinatura dele (ai-eng).
3. **Sabatina:** "11 perguntas ao Daniel" no consolidado v2 do ai-eng (`brain/observed-systems/varredura-clean-code-2026-10-28/01-CONSOLIDADO-V2-2026-10-30.md`); não foram relidas nesta sessão.

**E. Do HANDOFF (sabatina de 28/10):**
1. **D-01:** tornar o repo `daanmt/MedHub` privado já (o histórico público tem cópia do banco de 14/03, o exchange-log integral e 8 enunciados em `core/simulados/`) ou só depois do veredito (HANDOFF).
2. **D-07:** retomar a cópia off-machine do `ipub.db`, parada desde 11/10 (HANDOFF).
3. O consolidado v2 do ai-eng "guarda" PD-01 (repo privado) e PD-06 (backup do `ipub.db`) para a sessão do MedHub: são as mesmas decisões D-01 e D-07 do HANDOFF, com ids diferentes nos dois inboxes.

**F. Outras:**
- **P48:** varredura única que remove resumos e apostila de Referências e renumera, ou migração quando a aula for reaberta (P48). **Selo:** F39 (pergunta fechada), F69 e F111 (prazo 02/11), todos dele (HANDOFF). **Regra provisória do card com fonte:** revisar em 2026-11-15 (estilo-flashcard).
- **2 worktrees vazias:** `! git worktree remove --force .claude/worktrees/agent-a2cbded1c948fd460` e `agent-aa656c46bdaec8e45` (HANDOFF).
