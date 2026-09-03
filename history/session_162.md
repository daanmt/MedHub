# Session 162 — Veredito da des-colagem + FSRS 45 cards (blocos 4-6)
**Data:** 2026-09-02 -> 2026-09-03 (sessão cruzou a meia-noite)
**Ferramenta:** Claude Code (Opus 5, 1M) — effort max
**Continuidade:** Sessão 161 (Antigravity)

---

## O que foi feito

### 1. Auditoria da reforma: a des-colagem foi APROVADA

O usuário pediu o veredito sobre o ciclo DESCOLAR (F45-F61, entregue pelo /ai-eng em 01/09),
testado por ele na s161 num harness estrangeiro. Auditado contra o **banco**, não contra a prosa
da s161.

**O teste decisivo era o P7** (`3cd4b18` -- "regra load-bearing viaja com o repo, não com a
memória do harness") e ele passou da forma mais dura possível: a s161 rodou inteira no
**Antigravity (Sonnet 4.6)**, sem nenhuma memória do harness do Claude Code, bootando só do
repositório -- leu `AGENTE.md`, rodou o `auto_check`, executou 45 revisões e selou o rito de
fechamento correto (HANDOFF + session log + INDEX num commit semântico). Era exatamente a tese.

Parte por parte:

| parte | achados | veredito na s162 |
|---|---|---|
| **P7** | F57/F59 | ✅ harness estrangeiro bootou só do repo e selou certo |
| **P6** | F60/F58 | ✅ `auto_check` exit 0 **com 2 WARNs impressos**, não engolidos; F58 validou um session log escrito por agente estrangeiro |
| **P3** | F45/F46/F47 | ⚠️ **PARCIAL** -- F46 confirmado (bancos-fantasma sumiram), mas **F45 ficou a meio caminho: ver F66** abaixo, descoberto no fechamento desta sessão |
| **P1** | painel de DÍVIDA | ✅ abriu o `posicao_ssot` às 13h33 -- o minuto exato do selo da s161 |
| **P2** | IMPORT_DANGLING | ✅ PASSED |

**Tentativa de quebrar os números:** o banco cru mostra **108** cards vencidos contra os **45**
que o `day_plan` reporta. Os 63 de diferença são exatamente a coorte `needs_qualitative=2`
(falência FSRS da s075), corretamente excluída pelo filtro. **O `day_plan` está certo.**

### 2. Falhas encontradas na reforma (3)

1. 🔴 **Os sensores funcionam, o fechamento não.** O `POSICAO_DRIFT` disparou no minuto do selo
   da s161: ela escreveu "S17" na prosa e nunca rodou `preparacao.py --set-semana`. O SSOT ficou
   em S16 e **o plano do dia da s162 bootou prescrevendo conteúdo de S16.** Detecção nova e boa;
   loop de remediação nunca exercido. **Fechado nesta sessão** (`--set-semana 17`, fonte
   `sessao_161_s17_confirmado_usuario`; ledger `opened -> resolved`, dívida 283 -> 282).
2. **O painel de DÍVIDA conta linha, não item aberto.** No boot reportava `memory_errors.log:
   7 linhas` como dívida viva, mas as 7 eram de 30/08, de um bug morto em `8b5273d` (F46) --
   painel que grita lobo ensina a não ler painel. 🔴 **E durante o próprio fechamento desta
   sessão o número saltou para 146**, disparado pelo hook que consolida o session log novo: o
   defeito não é só "conta ferida cicatrizada", é **crescimento sem teto**. Foi assim que o F66
   apareceu.
3. **`scratch/` não foi limpo** pela s161 (auto-higiene §3.4). O conteúdo é o sinal:
   `parse_queue.py`, `find_card.py`, `queue_raw.txt` (178 KB) -- o harness estrangeiro
   **reimplementou o parser da fila FSRS** em vez de consumir o JSON do CLI. Atrito de
   superfície, não erro dele.

### 3. Correção do placar da s161

O HANDOFF da s161 registrou "~55% (25/45)" mas itemizou 13+3+7 = 23 na mesma linha, o que deixa
22 nota-4, não 25. O `fsrs_revlog` confirma **22**. Números reais da s161: **recall perfeito
49% (22/45)**, **retenção 64% (29/45)**. Número digitado à mão contradizendo a própria
itemização -- a doença que a regra F6 trata, num campo que ela não cobre.

### 4. FSRS -- 45 cards em 3 blocos (blocos 4-6 da dívida)

| bloco | dia | nota 4 | nota 3 | nota 2 | nota 1 | recall perfeito | retenção |
|---|---|---|---|---|---|---|---|
| 4 | 02/09 | 9 | 3 | 2 | 1 | 60% | 80% |
| 5 | 02/09 | 6 | 4 | 2 | 3 | 40% | 67% |
| 6 | 03/09 | 10 | 3 | 2 | 0 | 67% | 87% |
| **total** | | **25** | **10** | **6** | **4** | **56%** | **78%** |

**Contra os 49%/64% da s161** -- a mesma pessoa, o mesmo dia. A curva subiu: 64% -> 80% -> 67%
-> 87%.

🔴 **Erro de leitura do agente, registrado:** após o bloco 5 eu diagnostiquei degradação por
fadiga e **recomendei parar o estudo**. O bloco 6 (o melhor dos três, zero nota-1) refutou. A
queda do bloco 5 era a **colisão de clones 311/313** (ver F65), não cansaço. Diagnosticar fadiga
a partir de um único bloco, com o instrumento contaminado, é o padrão
`feedback_card_defeituoso_contamina_diagnostico` na sua forma agregada -- não foi um card que
contaminou uma leitura, foi um par de cards que contaminou a leitura de um **bloco inteiro** e
quase custou 30 cards de drenagem.

Contagem por dia de calendário: **02/09 fechou em 75** revisões (45 da s161 + 30 daqui, sob o CAP
de 90); **03/09 abriu limpo** e recebeu 15.

### 5. Bloco 7 servido, não respondido

15 cards apresentados (422, 699, 709, 4, 244, 1354, 122, 485, 459, 1089, 1101, 1117, 706, 558,
297) -- o usuário encerrou antes de responder. **Nenhum `--record` emitido**: os 15 permanecem na
fila, sem dano.

---

## Padrões de erro identificados

1. 🔴 **TCE: reflexo neuro-específico antes do ABC (3ª ocorrência).** Card 540, nota 1 --
   respondeu "cabeceira elevada e manitol"; a armadilha impressa no verso é literalmente essa
   resposta. As duas medidas de maior impacto são **evitar hipóxia e evitar hipotensão** (A-B-C).
   A s151 já registrou "hiperventilação em TCE grave, 2 instâncias na mesma sessão". Mesma
   matéria, mesma classe: a manobra de PIC atropela o ABC. **Terceira vez que TCE cobra isso.**
2. **Inversão de direção de marcador.** Card 1290 -- escreveu beta-hCG "> 1,5k" para liberar MTX;
   o critério é **< 5.000 (ideal < 1.500)**. Âncora de mecanismo entregue na sessão: MTX é
   antimetabólito e mata trofoblasto em proliferação -- **menos doença = funciona; mais doença =
   cirurgia**, e os 3 critérios apontam para o mesmo lado. Tamanho também errado (disse 2,5;
   é 3,5-4 cm).
3. **Fato verdadeiro no contexto errado.** Card 313 -- respondeu com o conteúdo do card 311
   ("TC vê mal microcálculos") e depois apagou no 311. Regra entregue: **na pancreatite, USG
   entra cedo para dizer POR QUÊ; TC entra depois de 72h para dizer QUÃO GRAVE.**
4. **Ancoragem no dado saliente, segundo dado sem uso.** Card 1416 -- leu trastuzumabe, respondeu
   "HER+" e ignorou o inibidor de aromatase do enunciado, que é justamente o dado que faz o
   subtipo ser **Luminal HER2-positivo**. Espelho do padrão-mestre discriminador-exclui.
5. **Pergunta binária: acerta o conteúdo, erra o sim/não.** Card 155 -- "pode, mas segue
   conjunto". O rider está certo (cuidado compartilhado), a palavra de abertura está errada (a
   resposta é **não**). Em item V/F perderia o ponto. Graduado 2 por isso.
6. **Colestase neonatal / AVB (reincidência da s161).** Card 245, nota 1 -- por que a SBP elege
   AVB como causa mais relevante sem ser a mais frequente: **tratamento cirúrgico com janela
   curta** (Kasai), relevância = urgência + desfecho, não frequência.

### Acertos que valem registro

- **Card 1358** (integralidade: princípio do SUS x atributo de Starfield) -- a armadilha do card
  diz *"Erro já cometido 2x pelo usuário"*, e a s161, **na mesma manhã**, flagrou "confusão SUS x
  Starfield" como gap. Acertou. O sistema fechou um gap em horas.
- **Card 325** (peritonite franca dispensa imagem antes da laparotomia) -- é o padrão
  **"instável = via aberta"** que o pegou 3× na s161. Aguentou.
- **Card 1096** (endometriose) -- resposta **mais completa que o próprio verso**: resistência à
  progesterona + aromatase sobre-expressa + receptor de estrogênio, quando o card pedia só a
  primeira.
- **Card 539** (rastreio de AAA) -- textbook, com o "uma vez" incluso.

---

## Achados de engenharia registrados em `AUDITORIA_MEDHUB.md §4o`

- **F63 — a prioridade que governa o estudo não viaja com o repo.** O usuário reordenou o xlsx do
  Drive por cores (**Roxo > Rosa > Salmão**, prevalência ENAMED do guia do EMED) e é essa ordem
  que decide o estudo até 13/09: das 11 tasks da S17, só **6 são roxas**. `grade.json` é parse
  **fiel** do PDF (verificado 11/11 contra a planilha) mas **não carrega a cor**; `infer_nota()`
  tem o **eixo 4 cabeado para `prevalencia_enamed`** e roda neutro por falta do campo. Resultado:
  o usuário **reenuncia a prioridade a cada sessão e a cada harness** -- para o Antigravity em
  02/09 e para o Claude Code no mesmo dia. É a tese do P7 violada na camada que o projeto existe
  para servir. Aberto desde a s147 como "achado registrado, não resolvido".
- **F64 — o gatilho do regime de dívida lê `atrasados`, o dono lê `vencidos`.** Havia 45
  atrasados + 22 hoje = 67 vencidos; `_teto_efetivo` leu 45 < 60 e travou o teto em 60. O usuário
  contestou e a leitura dele é a mais defensável. A política declarada não diz **qual contador**
  dispara. Agravante medido: a sessão cruzou a meia-noite e **nada avisou** -- o agente seguiu
  argumentando com o orçamento do dia anterior por 2 turnos.
- **F65 — o balde `[bulk] <Área>` esconde 72 cards do radar de dormência.** `[bulk] Cirurgia`
  (55 cards) abriga pancreatite, trauma abdominal, **demência/MEEM** e **esclerose múltipla**.
  Tema é a chave de `review_radar`, do cluster de frieza e do gatilho de PREPARAR -- 72 cards
  (5,7% do banco) são invisíveis a toda essa camada. Sintoma medido: `--review-plan` devolveu
  **40 clusters para 77 cards**, nenhum sinal frio acionável. Adendo honesto: a limpeza já
  constava como pendência Tier-3 no `ESTADO.md` -- o achado não a descobre, **quantifica**.

---

## Fila de reforja — 15 itens

| origem | cards | defeito |
|---|---|---|
| s161 | 821, 702, 283, 505, 411 | pergunta dupla |
| bloco 4 | 570 | composta (período do marcador **e** medidas de rotina) |
| bloco 4 | 128 | contradição interna: resposta diz "falha **ou** reinfecção", regra-mestre e armadilha afirmam "reinfecção **confirmada**" |
| bloco 4 | 705 | alvo não-cravável ("5 anos (ou 5 a 10 anos)") |
| bloco 4 | 1360 | binária = 50% de chute |
| bloco 5 | **311 + 313** | **colisão de clones** -- mesmo tema, mesma pergunta, eixos diferentes, servidos no mesmo bloco; custou 2 notas 1 |
| bloco 5 | 470 | sem campo de armadilha |
| bloco 6 | 1415 | enunciado disjuntivo que parseia como sim/não (metade da nota 2 é autoria) |
| bloco 6 | 1086 | cobra STEP **e** esquema, autodeclarando-se 🔴 BANCA-DEPENDENTE com 2 alternativas defensáveis |
| bloco 6 | 1126 | sem campo de armadilha |

---

## Artefatos criados/modificados

- `AUDITORIA_MEDHUB.md` — seção **§4o** nova: F63, F64, F65 + adendo de alcançabilidade
- `ESTADO.md` — frentes Infraestrutura / Posição / FSRS (macro mudou: des-colagem entregue **e**
  validada)
- `HANDOFF.md` — rotação da última sessão + próximo passo
- `history/session_162.md`, `history/INDEX.md`
- `ipub.db` — 45 revisões FSRS; `preparacao_estado.semana_conteudo` 16 -> 17
- `history/ledger_self.jsonl` — `posicao_ssot` opened (s161) -> resolved (s162)

---

## Decisões tomadas

- **A des-colagem está aprovada** e a frente de engenharia sai do estado "aguardando retorno do
  /ai-eng". O que sobra dela é dívida de fechamento (as 3 falhas acima), não dívida de projeto.
- **Ponteiro de conteúdo gravado em S17** no SSOT, com prioridade nos temas roxos até 13/09.
- **Teto do dia não foi furado**: 02/09 fechou em 75 (CAP 90). A recomendação de parar em 90 foi
  retirada -- estava fundada em leitura errada do bloco 5 **e** em orçamento de dia já vencido.

## Próximos passos

1. 🔴 **Redrill NÃO executado** -- 10 cards nota 1-2 desta sessão (540, 570, 1290, 313, 311, 245,
   650, 155, 1416, 1415) + 8 nota 3 + **16 da s161**. É passo obrigatório do protocolo
   (`/revisar` §Relearning intra-sessão), não opcional. **Segunda sessão consecutiva em que fica
   pendente.**
2. **Blocos 7-9** -- 43 vencidos restantes (26 atrasados + 17 hoje). 45 cards zeram a dívida
   FSRS e encostam no teto de 03/09.
3. 🎯 **Simulado ENAMED na íntegra** -- em débito há 10 dias, com a prova em 10. Sob
   `PLAYBOOK_EXECUCAO_PROVA.md`.
4. **Inscrição UERJ 2027** -- aberta desde 02/09, fecha 01/10 (23h59). Ação do usuário.
5. **Grade EMED S17, temas roxos** até 13/09: Diarreia (Teoria) -> SUA (Teoria) -> APS (Revisão)
   -> Diarreia (Revisão) -> Urologia I -> Pneumonias I.
6. **Frente MFC (Gusso + Duncan)** -- abre 14/09, lastro zero, vale 20% da UERJ.
7. **F63/F64/F65 são minha fila de trabalho** (papel auditor-observador): F65 tem o caminho mais
   curto (reclassificar 72 cards + WARN no `auto_check`) e o maior retorno -- destrava o radar de
   dormência e o `detect_clones` para o par 311/313.
8. 🔴 **F66 -- descoberto no fechamento desta sessão, do painel que a reforma criou.** 45% da
   memória de fraquezas (111 de 244 WeakAreas) é órfã por **abreviação**: o vocabulário canônico
   usa `Infecto`/`Gastro`/`Hepato`/`Dermato` e o Haiku escreve `Infectologia`/`Gastroenterologia`.
   `_norm` não faz substring, então o dado está certo e é descartado. Dois danos: o **top 8 de
   fraquezas do boot** é disputado por só 55% do store (área órfã nunca casa `error_count`, fica
   em 0 e nunca sobe no ranking), e o log cresce **111-139 linhas por consolidação, para sempre**.
   O fix é um dicionário de alias -- F45 consertou o mecanismo, faltou o vocabulário.
