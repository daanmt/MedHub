---
description: "Conduz uma sessão conversacional de revisão de flashcards FSRS — puxa a fila vencida via tools/fsrs_queue.py, apresenta card a card e grava a avaliação 1-4. Funciona via remote-control (celular)."
type: skill
layer: commands
status: canonical
---

# Skill: Revisar

O agente vira o **player de flashcards**. Conduz a revisão por repetição espaçada dentro da conversa, sem depender do Streamlit local — o que permite revisar via remote-control (celular). A leitura da fila e a gravação dos ratings passam pelo CLI `tools/fsrs_queue.py`, que é uma camada fina sobre `app/utils/db.py` (`get_cards_by_bucket` + `record_review`).

Use quando o usuário pedir qualquer variação de: "revisar", "vamos revisar flashcards", "tenho cards pra hoje?", "quero estudar os cards de Cardiologia".

---

## Estrutura da sessão — DRENAR -> REVISÃO DIRECIONADA (s170)

> `/revisar` é a **competência única** de revisão. Norma: [`core/contracts/revisao-calibrada-contract.md`](../../core/contracts/revisao-calibrada-contract.md). **Duas fases, nesta ordem, sem terceira:**

- **DRENAR** (card-a-card; **ESCREVE FSRS**) — o player FSRS descrito abaixo. Única superfície que move o FSRS.
  - 🔴 **Invariante C (override-antes-do-record, F9):** o rating só é gravado **após a janela de override** (nota proposta -> confirmação/correção do usuário -> gravação única). Nunca `--record` antes da janela; nunca re-record depois dela.
  - 🔴 **Invariante F (silêncio no meio — s170, regra do usuário).** Durante o DRENAR o agente entrega **verso + nota + tally, e nada mais**. **Zero prosa explicativa entre blocos**, inclusive para nota 1 e 2. Feedback no meio do drill quebra o ritmo e foi reprovado explicitamente. **Única exceção:** **defeito de CARD** (pergunta composta, premissa embutida, contexto desalinhado, binária) — é sobre a autoria do card, não sobre o desempenho, e continua sendo reportado na hora, em uma linha.
- **REVISÃO DIRECIONADA** (narrativo; **FSRS read-only**) — **a única superfície de ensino da sessão**, entregue **no fechamento**, ancorada nos temas que caíram em **nota 1 e 2**. Absorve o antigo `/refrescar`, o antigo sub-modo **PREPARAR** e a antiga **Camada 1** (micro-resumo na virada). Especificada na seção *Fechamento* abaixo.
  - 🔴 **Invariante A:** a Revisão Direcionada **NUNCA** emite `record_review` nem `UPDATE` em `fsrs_cards`/`fsrs_revlog` — nenhum write de FSRS. O FSRS da sessão já foi escrito no DRENAR.
  - 🔴 **Invariante B:** a Revisão Direcionada **SEMPRE** carimba `review_log` ao concluir — `python tools/dormant_refresh.py --stamp --tema-id <id> --kind <dormant_refresh|directed_review>` (tema puxado por dormência -> `dormant_refresh`; tema puxado pelos gaps do drill / cronograma / pedido -> `directed_review`). A curva nunca cega. Um carimbo por tema reabordado.

### ⚰️ Lápide — o sub-modo PREPARAR (s096-s170)

O PREPARAR era o re-ensino calibrado entregue **antes** de drillar (absorvia o `/refrescar` e a Camada 0). **Morreu na s170, por decisão do usuário.** Motivos registrados, para que ninguém o re-derive:

1. **Não era lido.** Na s170 o agente entregou um PREPARAR de 5 parágrafos antes do bloco de Cirurgia Infantil; o usuário respondeu os 8 cards **sem ter lido o bloco** e o classificou como *"muito ruim, denso e confuso"*. Um ritual que o aluno pula não é um degrau, é atrito.
2. **Quatro nomes para uma coisa só.** `refrescar`, `PREPARAR`, `Revisão Direcionada` e `aula-base` viraram um vocabulário confuso que o próprio usuário sinalizou. A consolidação em **uma** superfície de ensino é o remédio.
3. **O momento estava errado.** Aquecer antes mede "pegou o aquecimento"; ensinar depois mira o **gap que o drill acabou de provar que existe**. O segundo é dado; o primeiro é palpite.

🔴 **Não confundir com a `/aula-base`**, que **segue viva**: ela é pré-**QUESTÕES** (gatilho híbrido por dificuldade, `AGENTE.md §1.2`), não pré-cards, e tem eficácia medida (Meningites 53% -> 75%). O que morreu foi o aquecimento pré-**CARDS**.

O **Invariante D (isolamento, F8)** morreu junto: ele existia para impedir que o aquecimento vazasse a resposta dos cards do bloco. Sem aquecimento antes do drill, não há o que isolar.

### Resolver a nota na abertura de task

`python tools/day_plan.py --difficulty "<area>" "<tema>"` -> JSON com `nota_usuario`, `nota_inferida`, `nota_efetiva`, `degrau`, `paragrafos`, `divergencia`, `proposito`. Precedência **dura**: input do usuário > pergunta > inferência (`infer_nota`). Se `divergencia` != null (|Δ| >= 3), **sinalizar sem sobrescrever**. Persistir a nota usada via `db.set_dificuldade` (`fonte='usuario'` é soberana). 🔴 **A nota calibra SÓ a profundidade da REVISÃO DIRECIONADA — nunca o agendamento FSRS** (regido por recall real em DRENAR).

🔴 **Cobertura é piso fixo, não elástico (Cláusula 10 / Invariante E do contrato).** A nota calibra a **profundidade/prosa**; o **conjunto de pontos de decisão de alto rendimento** do tema é **piso fixo por tema**, derivado do **sumário da fonte** (índice do resumo / escopo do cronograma). Mesmo em **D2** (flash), passar pelo **checklist de cobertura** antes de fechar: comprimir a prosa de um ponto é legítimo; **eliminar** o ponto não é — **compressão encurta, nunca corta** (raiz do F21: ponto de decisão apagado pela descompressão).

---

## Invocação do CLI

```bash
# Próximo card vencido (objeto JSON) — opcionalmente filtrado
python tools/fsrs_queue.py --next [--area "Cardiologia"] [--tema "Insufic"]

# Lote da fila (array JSON) — para ver o tamanho/escopo da sessão
python tools/fsrs_queue.py --list [--area X] [--tema Y] [--limit N] [--new-limit M] [--prevalencia]

# Gravar a avaliação de um card (1=Novamente 2=Difícil 3=Bom 4=Fácil)
# P3: propagar o selection_reason que veio no card servido (--next/--list)
python tools/fsrs_queue.py --record <card_id> --rating <1-4> --reason <vencido|fresh_error|agendado|novo|pre_bloco|auto>
# F76 (s174): o --record RECOMPUTA o bucket real do card e grava fsrs_revlog.reason_servido;
# --reason divergente do servido => [WARN] em stderr (nao bloqueia) e a divergencia fica
# consultavel por SQL (selection_reason != reason_servido). `auto` grava o recomputado.

# P3: consequência dos 4 ratings para um card (sem gravar nada)
python tools/fsrs_queue.py --preview <card_id>
```

---

## Contrato de apresentação (P3 part-3)

Regras de EXIBIÇÃO do card na conversa — codificadas aqui porque a correção do
vazamento de rótulo (modo de falha #8 do handoff de flashcards) era tribal:

1. **Não vazar a categoria antes da revelação**: NUNCA exibir `tema`/`area`
   acima da pergunta enquanto o verso está fechado (entrega a categoria da
   resposta). Tema/área só aparecem APÓS a revelação, junto do verso.
2. **Preview do próximo intervalo -- só quando notável**: o `--next` traz
   `preview`, a consequência das 4 notas para aquele card.
   ⚰️ *Revogada em 10/09/2026 (F90) a prescrição original de "mostrar a consequência das 4 escolhas junto das opções":*
   sob **override passivo** (s123) o usuário **não escolhe** a nota -- não existem
   "opções" ao lado das quais exibir o preview. A cláusula ficou órfã da própria
   premissa e o painel de 4 linhas virou ruído no terminal. Vale a régua do passo 5
   do loop: reportar o próximo `due` **só quando notável** (relearning que volta
   hoje, salto longo), dentro do tally. O rating é input do modelo, não um
   intervalo fixo; `balanceado_apos_record: true` = o dia final pode deslocar
   +-5% (balanceador de carga).
3. **Dizer por que o card veio**: o card servido carrega `selection_reason` —
   exibir de forma curta (`fresh_error` → "⚠ erro recente"; `vencido` →
   "↻ revisão vencida"; `agendado` → "agendado p/ hoje"; `novo` → "✦ novo").
4. **Propagar a proveniência no record**: gravar SEMPRE com `--reason` igual ao
   `selection_reason` servido — é o que torna a fila auditável no revlog. Desde o
   F76 (s174) o CLI recomputa o bucket e grava `reason_servido` na mesma linha: um
   `[WARN] reason divergente` em stderr é gate-miss do agente (bloco misto gravado
   com um reason só, como o #559 na s167) — corrigir o hábito, não silenciar.

**Flags:**

| Flag | Semântica |
|---|---|
| `--next` | Imprime o próximo card da fila como objeto JSON. Fila vazia → `{"empty": true}`. |
| `--list` | Imprime a fila inteira (respeitando filtros/limites) como array JSON. |
| `--record CARD_ID` | Grava a avaliação do card. **Exige `--rating`.** Delega a `record_review()` (UPDATE `fsrs_cards` + INSERT `fsrs_revlog`). Imprime `{recorded, card_id, rating, next_due, state}`. |
| `--rating 1..4` | Avaliação. Só com `--record`. |
| `--area` | Filtro de área (match exato). |
| `--tema` | Filtro de tema (LIKE parcial). |
| `--limit` | Máximo de cards na fila (aplicado a `--list`). |
| `--new-limit` | Máximo de cards novos (`state = 0`). Default 10. |
| `--pre-bloco TEMA` | Mini-drill anti-reincidência (F23): lista só os cards de erro FRESCOS (`state 0`, dentro de `--janela-horas`) do tema-alvo, antes de um bloco de questões. O rating segue o `--record` normal com `--reason pre_bloco`. |
| `--janela-horas N` | Janela de frescor (horas) usada por `--pre-bloco`. |
| `--prevalencia` | **Opt-in (s165).** Reordena o bucket `novos` por prevalência ENAMED lida de `core/cronograma/prevalencia_enamed.json` (alta -> media -> baixa -> sem sinal; desempate FIFO por `card_id`) e só depois corta em `--new-limit`. Regra do usuário: **prevalência = prioridade na fila dos nunca introduzidos**. Não toca FSRS nem banco -- só a ordem de introdução. Sem o arquivo, degrada para FIFO. |

**Ordem da fila:** atrasados → hoje → novos. Cards aposentados (`needs_qualitative >= 2`) são excluídos pela query. Campos de cada card: `card_id, frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha, needs_qualitative, due, area, tema, bucket`.

---

## Protocolo do loop conversacional

1. **Abrir a sessão.** Rodar `--list` (com os filtros que o usuário pediu, se houver) para saber quantos cards há e anunciar o tamanho da sessão ("você tem 12 cards: 8 atrasados, 2 de hoje, 2 novos"). Para conduzir por tema, usar `--cluster` (mantém buckets, agrupa temas) e/ou `day_plan.py --review-plan` (clusters com contagem + sinal de frieza derivados).
   - **Cluster frio -> nota da Revisão Direcionada (F5, reescrito na s170).** Cluster com sinal **frio** (`frieza >= 25` no `--review-plan`) **não** recebe aquecimento antes do drill (o PREPARAR morreu — ver lápide acima). O sinal de frieza é **anotado** na abertura e usado no fechamento para **priorizar** esse tema na Revisão Direcionada, junto com os gaps de nota 1-2 que o próprio drill produzir.

2. **Apresentar a FRENTE.** Para o card atual, mostrar `frente_contexto` (se houver) como contexto e `frente_pergunta` como a pergunta. **Não revelar o verso ainda.** Convidar o usuário a tentar responder.
3. **Revelar o VERSO sob pedido.** Quando o usuário responder ou pedir ("mostra", "não sei", "revela"), mostrar `verso_resposta`, depois `verso_regra_mestre` (a regra de ouro) e, se preenchida, `verso_armadilha` (o distrator/pegadinha).
4. **Propor a nota (janela de override PASSIVA — contrato, Invariante C).** O agente **propõe a nota 1-4 com base na resposta do usuário** (não pede o número). Critério: cravou conceito + regra-mestre → 4; acertou o núcleo, faltou detalhe → 3; recall parcial/na zona mas sem o alvo → 2; errou ou "não sei" → 1. **Informar a nota proposta** ("-> 3") -- e só ela. ⚰️ *A "justificativa em 1 linha" que esta linha prescreveu até 10/09/2026 foi **revogada pelo Invariante F** (s170): durante o DRENAR o agente entrega verso + nota + tally, e nada mais. A explicação é entrada da Revisão Direcionada de fechamento, não do meio do drill (F90).* 🔴 **NÃO solicitar confirmação** ("confirma as notas?") — a proposta da nota é um **mecanismo automático** (feedback do usuário, s123: reprovou o pedágio 3× numa sessão). A janela de override é **passiva**, não um gate bloqueante: o usuário **sobrepõe proativamente** quando discorda ("não, o 35 foi 4"); o **silêncio = aceite**. Ratings honestos > generosos — a precisão do FSRS depende disso.
5. **Gravar no mesmo turno + avançar.** Logo após propor as notas do lote, rodar `--record <card_id> --rating <n>` de cada card — **uma única vez por card** — e **apresentar o próximo bloco no mesmo turno**, sem pausa entre propor e gravar. Reportar o próximo `due` só quando notável (relearning que volta hoje, salto longo). Correção que o usuário levante **antes** do record daquele card entra como nota final; correção **depois** do record não gera re-record (Invariante C — 2 linhas de revlog corrompem o FSRS): vira nota de fechamento em `history/session_NNN.md`.
6. **Avançar.** Buscar o próximo card (novo `--next`, ou o próximo item do lote já obtido no passo 1). Repetir 2-5.
7. **Fechar com Revisão Direcionada.** Quando a fila esvaziar (`{"empty": true}`) ou o usuário parar: (a) resumo de sessão — cards revisados + distribuição de ratings; (b) rodar a **Revisão Direcionada de fechamento** (seção abaixo) — a **única** entrega de ensino da sessão; (c) **carimbar `review_log`** para cada tema reabordado (Invariante B); (d) **Registrar a nota da aula (F18c).** Gravar a nota 1-10 que calibrou a descompressão da Revisão Direcionada via `db.set_dificuldade(area, tema, nota, fonte='aula')` — o sinal caro da forja deixa de ser efêmero. **Não sobrescrever** uma nota soberana `fonte='usuario'` (Cláusula 2/10 do contrato).

### ⚰️ Camada 0 — refresh pré-bloco (s082-s170, MORTA)

Era o "esquentar antes de sondar": leitura curta ancorada no resumo **antes** de drillar um tema frio. Morreu junto com o PREPARAR na s170 (lápide acima) — o ensino inteiro migrou para o fechamento. **O que sobreviveu dela**, realocado:

- **Calibrar a dose ao estado do tema** — tema frio pede descompressão, tema consolidado pede só a discriminação fina. Continua valendo, agora aplicado à **Revisão Direcionada de fechamento**.
- **Gatilho de andaime** — se o drill expõe um **cluster** caindo no mesmo eixo (não um card isolado), a fundação está ausente -> cunhar **cards de andaime** (`base`/`mecanismo`/...) via `tools/insert_card_base.py`, costurando o degrau imediatamente adjacente ao buraco (**propagação local**). O degrau `mecanismo` rende mais — o gap costuma ser causalidade, não fato. Régua: [`estilo-flashcard.md`](estilo-flashcard.md) §Altura graduada. Continua valendo, agora disparado **pelo resultado do drill**, não por previsão.
- ⚰️ **Morreu:** "a nota pós-refresh mede pegou no aquecimento". Sem aquecimento, toda nota do DRENAR é recall a frio — que é exatamente o sinal que o FSRS quer.

### Modo conversacional padrão (contrato core — sessão 075)

Comportamentos default desta skill, ajustáveis pelo usuário a qualquer momento:

- **Renderização em lote + override passivo.** Apresentar **N frentes de uma vez**, com **default de 10-15** -- proveniência: a s130 pediu blocos de 10 ([[feedback_revisar_apresentacao_cards]], que corrige explicitamente que *"isso NÃO é pedido para reduzir o tamanho do bloco"*) e a s152 rodou 90 cards em blocos de 15 ([[feedback_revisar_pipeline_blocos]]). ⚰️ *A redação antiga desta linha -- "default ajustável, o usuário pediu 3, depois 5, depois 6" -- foi **revogada em 10/09/2026** (F90): ficou congelada num pedido pontual da s123, sobreviveu à régua de 10-15 sem lápide e o agente a obedeceu em uso real na s175, partindo a fila em blocos de 6.* O usuário responde todas; o agente revela + **propõe as notas do lote** + **grava o lote** + **apresenta o próximo bloco**, tudo no **mesmo turno**. A janela de override é **passiva** (Invariante C, s123): **nunca perguntar "confirma as notas?"** a cada lote — é fricção que o usuário reprovou 3× ("isso é um mecanismo automático"). O usuário sobrepõe proativamente; silêncio = aceite. Sem pedido explícito do usuário, usar o default 10-15 -- **nunca 6**.
- **Avaliação automática pelo agente** (passo 4 acima): o agente propõe a nota, não o usuário — e grava no mesmo turno (janela passiva), sem solicitar confirmação.
- **Auto-confirmação do override quando o veredito é óbvio (s112 — regra do usuário, versionada aqui).** Quando a resposta do usuário decide sozinha o veredito (bateu ponto a ponto com o gabarito, ou errou/não sabia claramente), **o próprio agente fecha a janela de override e grava** — "quem deve confirmar é você, automaticamente. Pode seguir." A confirmação mecânica depois de um recall já demonstrado é atrito puro. Continua valendo a transparência do Invariante C: a **nota** fica visível. ⚰️ *O "+ justificativa de 1 linha" desta cláusula foi **revogado em 10/09/2026** junto com o do passo 4 -- mesma causa (Invariante F, s170), mesmo achado (F90).* **Só pause de verdade em ambiguidade real** — resposta parcial, zona cinzenta entre duas notas adjacentes, ou divergência entre o que o usuário disse e o que o card pede.
- **Papel de scrum master ativo:** ao detectar **erro repetido** (mesmo conceito errado em cards diferentes), parar e sinalizar explicitamente — não deixar passar (regra "não errar duas vezes pelo mesmo motivo"). Conectar o card ao erro de origem em `questoes_erros` quando útil.
- ⚰️ **Camada 1 — expansão de contexto na virada (s076-s170, MORTA).** Era o micro-resumo *just-in-time* de 2-4 linhas logo após virar um card nota 1-2. **Revogada pelo Invariante F**: o usuário reprovou explicitamente o feedback no meio do drill (s170: *"feedbacks nos meios dos blocos de cards também são ruins"*, depois de já ter cortado a prosa de nota 3 na s154). A lacuna do card 1-2 **não** se fecha na virada — ela vira entrada da **Revisão Direcionada de fechamento**, que é onde o tema ganha ancoragem teórica de verdade.
- **Flip obrigatório do card (feedback do usuário, sessão 077).** Após a tentativa, **sempre virar o card** — revelar `verso_resposta` + `verso_regra_mestre` (+ `verso_armadilha`) de **todo** card, mesmo nos acertos (3-4). Ver a formulação exata da resposta consolida a memória; nunca pular o verso "porque acertou".
- **Relearning intra-sessão (estilo Anki — s077; PASSO obrigatório, corrigido em s161).** Todo card avaliado **< 4** (1, 2 ou 3) entra numa **fila de re-drill da própria sessão** e é **re-apresentado** (só a frente) **até sair 4** — sem cap arbitrário. 🔴 O antigo "em 1-2 repetições" ERA o bug: com o cap, cards nota 1/2 apareciam 1× por sessão e o loop nunca rodava de fato (confirmado pelo usuário em 15/08 como bug real de execução, não falso-positivo de auditoria). Manter a fila explícita na conversa e **fechá-la antes de encerrar** — ela é passo do protocolo, não comportamento opcional. **Esse re-drill é consolidação, NÃO grava no FSRS** — a nota do FSRS é **uma só por card por sessão** (a 1ª tentativa honesta), respeitando a regra anti-duplo-registro. Priorizar 1 e 2 sobre 3 quando a fila estiver grande; fechar quando a fila esvaziar ou o usuário parar. 🔴 **Corte do loop (s173, regra do usuário):** card que trava **2x em "não lembro"** no re-drill **sai do loop** e vira entrada da Revisão Direcionada com **reonboarding curto do tema** (mecanismo + réguas, 1 parágrafo); só depois volta a ser sondado. Repetir a sonda sem reabordar a fonte trava o aluno -- *"em temas que não me lembro, preciso de um reonboarding curto, senão trava"* (09/09). É o mesmo princípio de "o card é a sonda, o resumo é a fonte", aplicado dentro do loop. *(Mecanizar a fila em código — `fsrs_queue.py` devolvendo o redrill — está registrado como **candidato** no painel de DÍVIDA do `auto_check`; não foi implementado.)*
- **Honestidade sobre generosidade:** preferir a nota que reflete o recall real, mesmo que baixa.

### Fechamento: Revisão Direcionada — a única superfície de ensino (s078, reescrita na s170)

> **Princípio: o card é a sonda, o resumo é a fonte.** Reforçar a sonda (re-drillar o card) sem reabordar a fonte (a matéria do resumo) é dispendioso e infrutífero — o card vira *leech* e ressurge eternamente. Quando um gap não está consolidado, a correção é **reabordar a matéria**, não repetir a pergunta. Feedback do usuário (s078): *"ficarei voltando eternamente nos cards se a matéria que trata do desafio do card não for reabordada"*.

🔴 **Escopo (s170, regra do usuário):** a Revisão Direcionada é **onde TODO o ensino da sessão acontece** — absorveu o `/refrescar`, o antigo PREPARAR e a antiga Camada 1. A entrada é o conjunto de temas que caíram em **nota 1 e 2**. Racional do usuário: *"claramente são temas fracos, precisando de ancoragem teórica, o que faz com que a revisão direcionada cumpra sua função de direcionar para os gaps dos cards na teoria."* Nota 3 **não** entra por padrão (só se o mesmo tema já estiver entrando por um 1-2).

Ao fechar a sessão, **antes** de encerrar:

1. **Clusterizar os gaps por TEMA/conceito, não por card.** Agrupar todo card avaliado **1 ou 2** e todo erro repetido pelo **elo metacognitivo / tema de origem** (ver [[feedback-flashcard-metacognitivo]]). Ex.: "Febre Amarela — números (incubação 3-6 x viremia <7)"; "PTI — gatilho de tratamento (púrpura úmida x valor de plaqueta)". Somar aqui os clusters que abriram a sessão com sinal **frio** (F5) e o tema **dormente** do dia, se houver — é o slot que o `/refrescar` ocupava.
2. **Para cada gap-tema, voltar ao resumo de origem** em `resumos/` — localizar via RAG local `app.engine.rag.search` (não ler arquivo inteiro à toa). Diagnosticar o resumo **contra o gap**:
   - **Resumo cobre o ponto com clareza** -> gap é puro recall/decoreba -> entregar **re-ensino direcionado condensado**: denso, ancorado no resumo, focado na **discriminação exata** que falhou. Sem editar o resumo.
   - **Resumo é raso/omisso no ponto** -> a **matéria é deficiente** -> **expandir o resumo**: adicionar a discriminação/armadilha que faltou, seguindo `/estilo-resumo` + **Regra de Acúmulo** (armadilhas cumulativas, nunca sobrescrever) + Siamese Twins (`AGENTE.md §6`). É o passo que faz o card **parar de ser leech**.
   - **Resumo está inchado em torno do ponto** -> **comprimir**: tighten o sinal para o ponto ficar localizável. Nunca deletar armadilhas — comprimir é reorganizar, não apagar conteúdo de prova.
3. **Entregar** no chat + aplicar as edições de resumo que o diagnóstico exigir. Editar `resumos/` é mudança de SSOT clínico: seguir `/estilo-resumo`, preservar armadilhas. Adicionar armadilha/discriminação (cumulativo) é in-bounds; reestruturação grande -> confirmar escopo antes.
4. **Blast radius (s143).** Ao fechar o gap, não citar de passagem os temas vizinhos: abrir **5-6 eixos** — temas centrais, armadilhas, erros sistêmicos e fraquezas notáveis (sinalizadas ou percebidas) — **na mesma densidade** do eixo principal.
5. **Calibrar a intensidade (papel de scrum master).** Gap pontual (1 card decoreba, resumo já cobre) -> re-ensino curto. Cluster reincidente (mesmo tema falhando em vários cards / em sessões anteriores) -> re-ensino denso + provável edição do resumo. Registrar os temas reabordados no `history/session_NNN.md` de fechamento.
6. 🔴 **Forma (s170).** O bloco entregue tem de ser **legível de primeira**: prosa com hierarquia tipográfica, um fato dito **uma vez só**, sem pilha de bullets e sem parágrafo-monólito. O antigo PREPARAR da s170 foi rejeitado sem ser lido (*"muito ruim, denso e confuso"*) — densidade que não é lida não ensina nada. Régua: [[feedback_aula_base_prosa_enxuta]].
7. 🔴 **Carimbar `review_log`** para cada tema reabordado (Invariante B) — `dormant_refresh.py --stamp --tema-id <id> --kind directed_review` (ou `dormant_refresh` quando o tema entrou por dormência).

---

## Assinatura canônica — `tools/dormant_refresh.py`

> **Portador canônico deste CLI** (`AGENTE.md §7.2`). O `refrescar.md` é stub de redirecionamento
> e **não** carrega assinatura. A do `tools/day_plan.py` (usado aqui via `--difficulty`) vive em
> `engenharia-cli.md`, para não existir em dois lugares.

| Flag | Função |
|---|---|
| `--pick` | Escolhe o tema dormente do dia (JSON). Ordem: tema com cards ativos, não-`[bulk]`/`Geral`, não reabordado na janela, maior score de dormência. |
| `--context` | Substrato narrativo do tema (JSON) — resumo + erros + cards + chunks do RAG. Exige `--tema`. |
| `--stamp` | Carimba em `review_log` (**Invariante B**). Exige `--tema-id`. |
| `--area AREA` | Filtro de área (match exato), com `--pick`/`--context`. |
| `--tema TEMA` | Tema a contextualizar (com `--context`). |
| `--tema-id N` | id do tema (com `--stamp`). |
| `--resumo PATH` | Caminho do resumo reabordado, gravado na linha do carimbo (com `--stamp`). |
| `--note "..."` | Nota curta do que foi reabordado, gravada na linha (com `--stamp`). |
| `--kind {dormant_refresh,directed_review}` | Gatilho: dormência **vs** gap do drill/cronograma/pedido. |
| `--window-days N` | Janela anti-repetição do `--pick`, em dias (default 7) — impede o radar de devolver o mesmo tema dia após dia. |

🔴 **Fronteira dura:** nenhuma dessas flags toca o FSRS. `--stamp` escreve **só** em `review_log`,
que é o SSOT do tempo-de-revisão **temática** (a curva do TEMA ≠ a do card).

---

## Regra anti-duplo-registro (reconciliada com o override — F9)

O CLI é **stateless** — cada `--record` grava uma linha em `fsrs_revlog`. A deduplicação é responsabilidade do agente: **mantenha o conjunto de `card_id` já avaliados nesta conversa** e nunca chame `--record` duas vezes para o mesmo card na mesma sessão. (A dedup vive **só** no agente: não há mais camada de UI guardando estado de sessão.)

**Sem contradição com o "usuário pode sobrepor":** o override intencional acontece **dentro da janela do passo 4, ANTES do record** (Invariante C do contrato). Depois do record não há amend — re-gravar recalcula o FSRS sobre estado já mutado e deixa 2 linhas de revlog (caso card 403, s108). Correção tardia vira nota de fechamento em `history/`, nunca segundo `--record`.

---

## Notas

- **Não há sessão Streamlit.** Esta skill é a interface primária (e única) de revisão na pivotagem agent-first (ROADMAP Linha 8). O player `app/pages/2_estudo.py` foi removido (código morto — consolidacao-part-1).
- **`ipub.db` é local-only.** O CLI roda na máquina onde o banco vive; via remote-control, o comando é executado nessa máquina e o resultado volta para a conversa.
- **Avaliação honesta.** Incentivar o usuário a tentar responder antes de revelar o verso — a precisão do FSRS depende de ratings honestos.
- O FSRS subjacente é o de `app/utils/fsrs.py` (substituição pela referência é a part-2 da Onda A; esta skill não muda quando o FSRS for trocado, pois grava via `record_review()`).
