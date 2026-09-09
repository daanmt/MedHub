---
type: contract
layer: core
status: canonical
version: 1.3
relates_to: [forgetting-curve-contract, fsrs-management-contract, cronograma-contract, AGENTE]
---

# Contrato de Execução de Revisão Calibrada
**Versão 1.3 | 2026-09-08 (s170: o sub-modo PREPARAR e a Camada 1 sao REVOGADOS; todo o ensino migra para a Revisao Direcionada de fechamento -- Clausula 11, Invariante F, lapide do Invariante D) — anterior: 1.2, 2026-07-06 (s109+, F18c/F21: Invariante E + Clausula 10); 1.1, 2026-07-05 (s108+, F8/F9: Invariantes C e D); 1.0, 2026-06-28 (sessao 096).**

> Documento normativo. Governa a **competência única `/revisar`** cuja descompressão é calibrada por uma **nota de dificuldade-para-o-usuário (1-10) por tema**, sem cegar a curva de esquecimento. Consome o score de dormência e a retrievability de `forgetting-curve-contract.md` (não os redefine) e o `(tema, tipo)` de `cronograma-contract.md`. Referenciado por: `AGENTE.md` (§1.2, §6, §7.3), `.claude/commands/revisar.md`.

---

## Papel

O estudante via `/revisar` (cards FSRS) e `/refrescar` (re-ensino de tema dormente) como **duas portas de um mesmo gesto** ("preparar o terreno e treinar"). A calibração de descompressão era ad-hoc e binária (frio→descomprime / quente→comprime). Faltava o eixo que o usuário pediu: **o quão difícil o tema é PARA ELE** — um eixo contínuo 1-10 que modula a profundidade narrativa. Este contrato funde as duas competências em sub-modos internos e formaliza a escala, a inferência determinística e as barreiras que protegem o motor de memória.

---

## Cláusula 1 — A escala 1-10 (régua de descompressão)

Mede **dificuldade-para-este-usuário**, não dificuldade intrínseca do tema. Governa **quanto descomprimir**. Quanto MENOR a nota, MAIS COMPRIMIDA a revisão.

- **10 = onboarding fundacional** — descomprimido ao máximo, do zero; ancora cada conceito, mecanismo > fato. Referência viva: resumo "Diabetes — Complicações Crônicas" (s094).
- **1 = ultra-comprimido** — só 🔴 gatilhos/armadilhas em flash; tema dominado, quente, baixa prevalência de banca.
- **Reduzem a nota** (mais compressão): tema fácil (acerto alto, stability alta), quente (dormência baixa), baixa prevalência ENAMED.
- **Elevam a nota** (mais descompressão): tema novo/estreia, frio/dormente, alta incidência de erro, alta prevalência de banca.

## Cláusula 2 — Fontes da nota e precedência

Precedência **dura**: **input explícito do usuário > pergunta respondida > inferência do agente**. A inferência é a *proposta default*; nunca silencia um input do usuário.

- **Input explícito** — soberano ("esse é um 8"), persistido `fonte='usuario'`.
- **Pergunta** — se a task abre sem nota: "De 1 a 10, quão difícil é X pra você hoje?".
- **Inferência** — `infer_nota()` (Cláusula 6), persistida `fonte='agente_inferida'`.

**Divergência auto-nota × performance (§4.4).** O agente computa `nota_inferida` **mesmo quando há nota do usuário**. Se `|nota_usuario − nota_inferida| ≥ 3`, **sinaliza sem sobrescrever** ("Você marcou 3, mas seu histórico aqui é 48% e faz 26 dias — confirma o 3 ou subo pra 6?"). Dois limites duros: (a) a nota **NUNCA** governa o agendamento FSRS (regido por recall real em DRENAR); (b) se a nota foi baixa e o bloco seguinte sai fraco (`acerto_bloco < 60%`), a próxima abertura **propõe** nota maior citando a evidência.

## Cláusula 3 — Mapa nota → degrau de registro (switches mecânicos)

Quatro degraus de formato, com switches **auditáveis por contagem/regex** (não adjetivos):

> **Regra D10 (extensivo) — única, idêntica em `tools/day_plan.py`, este contrato e `AGENTE.md §1.2`:** material extensivo ou inferência sem nota explícita → degrau D10 + dever de Deep-Researchness; a nota explícita do usuário (fonte=usuario) sempre vence (precedência input > pergunta > inferência).

- **Degrau D10 (notas 9-10) — Onboarding do zero / Deep-Researchness.** Parágrafos: **7-9.** **Degrau 0 explícito** (a régua do "normal" antes da nuance). **Toda sigla definida por extenso na 1ª ocorrência.** Espinha: *mecanismo → por que existe → valores → ajustes → o que acontece se errar → contexto de uso*. Nenhum salto: cada seção referencia a anterior. **Obrigação de Deep-Researchness:** quando acionado por cronograma de extensivo ou nota 9-10, o agente tem o dever proativo de varrer a literatura de base em profundidade, antecipando conexões entre especialidades, controvérsias de bancas e exceções clínicas antes de o usuário realizar questões ou auditar resumos.
- **Degrau D8 (notas 7-8) — Descomprimido com mecanismo.** Parágrafos: **5-6.** Degrau 0 explícito; siglas-chave expandidas. Fundação + cadeia causal + nuance.
- **Degrau D5 (notas 4-6) — Gatilhos + armadilhas.** Parágrafos: **3-4.** Degrau 0 assumido conhecido. Mecanismo curto + conduta; fecha com gatilhos-de-prova + 🔴 armadilhas.
- **Degrau D2 (notas 1-3) — Só armadilhas / flash.** Parágrafos: **1-2** ou bullets. Sem reconstruir fundação. 🔴 armadilha + diferencial "X vs Y".

A nota explícita do usuário **escolhe o degrau diretamente**; sem nota, a faixa sai do `infer_nota()`. Implementação do mapa: `day_plan._degrau_de()` + `DEGRAU_PARAGRAFOS`.

## Cláusula 4 — Fases da sessão de cards (DRENAR → Revisão Direcionada)

⚰️ **Reescrita na v1.3 (s170).** A clausula descrevia a fusao do `/refrescar` num sub-modo de aquecimento pre-drill. Esse sub-modo foi **revogado pela Clausula 11** — o texto original fica no historico do git. `/revisar` continua sendo **uma porta so**; o que mudou foi o numero de fases dentro dela: **duas, nao tres**.

- **DRENAR** (card-a-card; **ESCREVE FSRS**) — o player FSRS. **Primeira fase e unica superficie que move o FSRS.** Durante o drill: nota e tally, nada mais (Invariante F).
- **REVISAO DIRECIONADA** (narrativo; **FSRS read-only**) — **segunda fase, no fechamento**, ancorada nos temas de nota **1-2**. **Unica superficie de ensino da sessao de cards** (Clausula 11).
- Nao ha aquecimento antes do drill: **toda nota do DRENAR e recall a frio**, que e o sinal que o FSRS quer.

**Arquitetura por propósito (v1.2, s110 — correção de calibração; alvo remapeado na v1.3).** ⚰️ O texto original calibrava o sub-modo revogado. **A regra sobrevive nas duas superficies que a Clausula 11 preserva**, cada uma herdando uma metade: rumo a **EXERCÍCIOS** -> **`/aula-base`** (pre-questoes, intocada pela v1.3); rumo a **FLASHCARDS** -> **Revisao Direcionada** de fechamento. O propósito não muda só a LARGURA; muda a **arquitetura** do ensino. **`/aula-base`, antes de questões:** os **degraus são fundamentais** — cobre o **escopo-árvore inteiro** que a prova cobra (doses, diferenciais, a árvore de decisão completa) e **DESTRINCHA o mecanismo** dos conceitos/exames discriminadores (não só os nomeia), mesmo em nota média. **Revisão Direcionada, depois dos cards:** o alvo é **fino e provado pelo drill** — os temas de nota 1-2, não uma varredura do cluster (compressão ok; o card já disse onde dói). ⭐ **Descompressão (nota) ≠ cobertura de mecanismo:** nomear um discriminador ("whiff+", "clue cells") sem abrir **o que é e por que** é profundidade D2 disfarçada de D5 — e reforça o **Invariante E / Cláusula 10** (a cobertura do ponto de decisão inclui abrir o mecanismo, não só citá-lo). Precedente vivo: aula de Vulvovaginites (s110) — os exames whiff/KOH/clue cells foram nomeados e não destrinchados; refeita com os degraus.

## Cláusula 5 — Invariantes de integridade (barreiras invioláveis)

**Invariante A — o ensino é read-only no FSRS** *(sujeito remapeado na v1.3: era o sub-modo revogado, hoje é a **Revisão Direcionada** — Cláusula 11, Fronteiras duras)*. Writes permitidos na Revisão Direcionada: `review_log` (Invariante B) e edição de `resumos/` (acúmulo, nunca apaga). **Proibidos:** `record_review`, `insert_questao`, qualquer UPDATE em `fsrs_cards`/`fsrs_revlog`. **DRENAR é a única superfície que move o FSRS.** Auditada por `tools/test_revisao_calibrada.py` (a contagem de `fsrs_revlog`/`fsrs_cards` não muda numa Revisão Direcionada) + gate estático (`dormant_refresh.py` não menciona `record_review`/`fsrs_*`).

**Invariante B — a Revisão Direcionada SEMPRE carimba `review_log`** *(realocado na v1.3 — Cláusula 11: o carimbo migra do sub-modo revogado para o fechamento)*. A curva de dormência é alimentada exclusivamente por `review_log`. Sem o carimbo, o radar acharia que o tema "nunca foi revisto" (loop, score distorcido). **Regra:** toda Revisão Direcionada, ao concluir, grava **1 linha por tema reabordado** via `db.log_review`/`dormant_refresh.py --stamp --kind`, com `kind` discriminado pelo gatilho:
- tema do **radar de dormência** → `kind='dormant_refresh'`;
- tema do **cronograma / fila FSRS / pedido direto** → `kind='directed_review'`.

**Invariante C — Janela de override ANTES do record (F9, v1.1).** No DRENAR, o rating só é gravado **depois** da janela de override: o agente **propõe** a nota (com justificativa de 1 linha), aguarda a resposta do usuário (confirmação, correção ou avanço), e **só então** chama `record_review` — **uma vez por card por sessão, sempre**. Não existe amend pós-record: `record_review` é append-only por design (INSERT em `fsrs_revlog` + UPDATE em `fsrs_cards`); re-gravar recalcula o FSRS sobre estado já mutado e corrompe o agendamento (caso real: card 403, s108 — nota 2 corrigida p/ 4 após o record moveu o due indevidamente e deixou 2 linhas de revlog). Se um erro de gravação real acontecer, registra-se o ocorrido em `history/session_NNN.md` como achado — **nunca** re-record. Esta invariante RESOLVE a contradição da v1.0 entre "o usuário pode sobrepor a nota" e a regra anti-duplo-registro: o override intencional acontece **dentro da janela**, antes da gravação. No modo lote, a janela é **única por lote** (notas propostas do lote inteiro → confirmação/correção → gravação do lote).

⚰️ **Invariante D — Isolamento de conteudo do PREPARAR (F8, v1.1) — REVOGADO na v1.3.** Existia para impedir que o aquecimento pre-drill vazasse a resposta dos cards do bloco. Com o PREPARAR revogado (Clausula 11) nao ha aquecimento antes do drill, logo nao ha o que isolar: toda nota do DRENAR volta a ser recall a frio, que e o sinal que o FSRS quer. O texto original fica no historico do git. **Nao re-derivar:** se alguem reintroduzir aquecimento pre-bloco, o Invariante D volta a ser necessario junto.

**Invariante F — Silencio no meio do DRENAR (s170, v1.3).** Durante o DRENAR o agente entrega **verso + nota + tally, e nada mais**. Zero prosa explicativa entre blocos, **inclusive para nota 1 e 2**. Feedback no meio do drill quebra o ritmo e foi reprovado explicitamente pelo usuario em duas rodadas (s154: corta a prosa de nota 3; s170: corta tambem a de 1-2). **Unica excecao:** achado de **defeito de CARD** (pergunta composta, premissa embutida, contexto desalinhado, binaria) — e sobre a autoria do card, nao sobre o desempenho do usuario, e continua sendo reportado na hora, em uma linha. Auditavel por leitura do transcript, nao por teste automatico.

**Invariante E — Cobertura de ponto de prova é piso fixo (F21, v1.2).** A descompressão (nota 1-10) calibra **profundidade/prosa**; a **cobertura do conjunto de pontos de decisão de alto rendimento** do tema é **inviolável**. Nenhum degrau — nem o D2 (flash) — autoriza **ELIMINAR** um ponto de prova testável: comprimir **encurta** um ponto, **nunca o corta** (detalhamento na Cláusula 10). Raiz: a Q2 da s109 caiu num ponto de decisão (ileotiflectomia) que a descompressão D10→D7 eliminou em vez de encurtar. Auditada pela presença da Cláusula 10 + do checklist de cobertura no render.

## Cláusula 6 — Inferência determinística (`infer_nota`)

`infer_nota(sinais)` (em `tools/day_plan.py`) é a SSOT da nota inferida — função de pontos clampada em 1-10. Pseudocódigo normativo:

```
def infer_nota(sinais):
    acerto_hist  = sinais.acerto_hist     # None se 0 questões
    acerto_bloco = sinais.acerto_bloco    # None se inexistente
    score_dorm   = sinais.score_dorm      # None = sinal ausente (≠ quente)
    leu_tema     = sinais.leu_tema
    prevalencia  = sinais.prevalencia or 'media'

    # eixo 1 — performance histórica define a BASE
    if   acerto_hist is None and not leu_tema:  base = 9   # estreia pura → onboarding
    elif acerto_hist is None:                   base = 6   # leu, sem volume
    elif acerto_hist < 50:                       base = 8
    elif acerto_hist < 65:                       base = 7
    elif acerto_hist < 80:                       base = 5
    else:                                        base = 3  # >= 80%
    # eixo 2 — frieza (None = neutro; quente puxa p/ baixo)
    if score_dorm is not None:
        if   score_dorm >= 40:  base += 2
        elif score_dorm >= 25:  base += 1
        elif score_dorm < 7:    base -= 1
    # eixo 3 — último bloco fraco confirma dificuldade VIVA
    if acerto_bloco is not None and acerto_bloco < 60:  base += 1
    # eixo 4 — prevalência ENAMED = piso de banca, não teto
    if prevalencia == 'baixa':  base -= 1
    nota = clamp(base, 1, 10)
    if prevalencia == 'alta':   nota = max(nota, 4)
    return nota
```

**Anti-circularidade (§7.6, invariante de sinal).** `infer_nota` lê **apenas sinais frios independentes da própria saída**: nunca (a) a profundidade do ensino que ela gerou, nem ⚰️ (b) *o acerto "morno" medido logo após o aquecimento pré-drill* — **exclusão órfã desde a v1.3**: sem aquecimento antes do drill, essa medição não pode mais ser produzida, e toda nota do DRENAR já é fria. A exclusão fica **como estava, não recalibrada** — mexer no `infer_nota` é spec própria, não hotfix de texto. 🔴 **Não re-derivar:** se o aquecimento pré-bloco voltar, (b) volta a ter alvo. **Histerese assimétrica:** a nota inferida **SOBE** com 1 sinal forte; só **DESCE** após ≥ 2 sinais frios consistentes (ex.: 2 blocos ≥ 80% **e** stability subindo). Errar para mais (descomprimir além) é mais barato que para menos.

## Cláusula 7 — Persistência da nota

Estado **de tema** em `taxonomia_cronograma` (local-only): `dificuldade INTEGER` (1-10, NULL = não calibrado), `dificuldade_fonte TEXT` (`'usuario'|'agente_inferida'|'aula'`), `dificuldade_at TIMESTAMP`. Escrita **exclusivamente** via `db.set_dificuldade(area, tema, nota, fonte)` — 🔴 única exceção autorizada à regra "só `insert_questao` escreve `taxonomia_cronograma`": toca **apenas** as 3 colunas novas. **Frescor:** `NULL` ou (`agente_inferida` **e** `dificuldade_at` > 7 dias) → reinferir antes de abrir; `'aula'` é nota registrada (fato da forja, Cláusula 10) — **não** dispara reinferência automática. Nota `fonte='usuario'` é soberana (não recalcula a aplicada, mas computa a inferida p/ checar divergência).

## Cláusula 8 — Degradação graciosa (prevalência ENAMED)

`core/cronograma/grade.json` ainda **não** carrega `prevalencia_enamed`. Enquanto não carregar: `prevalencia = 'media'` (peso neutro; eixo 4 não atua, sem piso de banca). Quando a grade ganhar o campo, basta `cronograma.py` fornecê-lo — **nenhuma** mudança em `infer_nota()`.

## Cláusula 9 — Decisões das questões abertas (PRD §10, propostas-semente ratificadas em uso)

1. **Nota por TEMA** (não por tema×tipo); o tipo de bloco modula a **largura** (amplo/direcionado), não a nota.
2. **Frescor = 7 dias** para reinferir nota `agente_inferida`.
3. **Histerese:** baixar a nota exige 2 sinais frios consistentes (blocos ≥ 80% + stability↑).
4. **Prevalência:** peso neutro até a grade carregar o campo (Cláusula 8).
5. ⚰️ **Revogado na v1.3** — o item mandava o aquecimento pré-drill oferecer o DRENAR em seguida. Sem aquecimento, **o DRENAR é a entrada da sessão de cards**, não a segunda etapa de nada.
5b. **Cluster frio entra na fila da Revisão Direcionada (F5; reescrito na v1.3).** ⚰️ O item mandava o DRENAR **oferecer aquecimento** ao abrir um cluster frio — revogado pela Cláusula 11, que realoca o sinal em vez de descartá-lo. **Regra atual:** cluster com score de dormência `>= 25` (via `day_plan --review-plan`/`review_radar`) **entra na fila de prioridade da Revisão Direcionada de fechamento**, junto dos temas de nota 1-2. Não dispara nada antes do drill. O limiar vive AQUI (contrato), não no CLI — o CLI só expõe o score cru. 🔴 **O sensor não morreu, morreu o consumidor** (lápide do F5 em `AUDITORIA_MEDHUB.md:68`).
6. **Soberania do usuário prevalece** mesmo com dormência alta — o agente sinaliza a divergência, não sobrescreve.

## Cláusula 10 — Descompressão (calibrável) × Cobertura (piso fixo) + registro no ato (F18c/F21, v1.2)

Duas dimensões **ortogonais** no render de qualquer ensino calibrado — **`/aula-base`** (pré-questões) ou **Revisão Direcionada** (fechamento dos cards) —, que **não se confundem**:

- **Descompressão = elástico (calibrável).** A nota 1-10 governa a **profundidade** narrativa, o nº de parágrafos e a prosa (Cláusula 3). Tema fácil/quente comprime; difícil/frio descomprime.
- **Cobertura de pontos de decisão de alto rendimento = PISO FIXO (não calibrável).** O **conjunto** de pontos de prova testáveis do tema é um piso por tema, derivado do **sumário da fonte** (índice do resumo / aula-base; precedente s089 — o LCR lido por dado parcial, não pelo conjunto). Mesmo em **D2** (nota 1-3, flash) o render passa pelo **checklist de cobertura** antes de fechar: comprimir a **prosa** de um ponto é legítimo; **eliminar** o ponto não é. **Compressão encurta um ponto de decisão; nunca o exclui** (Invariante E). Raiz do F21: a Q2 da s109 caiu exatamente num ponto (ileotiflectomia) que a descompressão D10→D7 **eliminou** em vez de encurtar.

**Dependência de operacionalização (não bloqueia a cláusula).** O checklist **mecânico** de cobertura deriva o piso do sumário da fonte — que depende da cobertura de `.md`/sumário (relatório de cobertura do pipeline de conhecimento; o RAG é **gold-only** — a collection `pdf_raw`/two-tier foi removida na consolidação part-2). Enquanto a cobertura mecânica não amadurece, o piso deriva **do que houver** (índice do resumo presente ou o escopo exato do cronograma). A cláusula é a **barreira de conduta agora**; o motor mecânico vem com a cobertura.

**Registro no ato (F18c).** A nota 1-10 que **calibrou** a descompressão é **registrada no fechamento** da aula via `db.set_dificuldade(area, tema, nota, fonte='aula')` — o sinal caro da forja da aula deixa de ser efêmero e passa a alimentar a Revisão Calibrada. **Respeita a precedência da Cláusula 2:** `fonte='aula'` **não sobrescreve** uma nota soberana `fonte='usuario'` (registra apenas quando a nota da aula não colide com input explícito do usuário). **Zero schema novo** — reusa as 3 colunas de dificuldade e o `set_dificuldade` existente.

---

## Cláusula 11 — Morte do PREPARAR: todo o ensino migra para o fechamento (s170, v1.3)

**Decisão do usuário, tomada durante a s170.** A preparação pré-drill (`PREPARAR`, que já havia absorvido o `/refrescar` e a Camada 0) e a expansão por-card na virada (Camada 1) **deixam de existir**. A sessão de cards passa a ter **duas fases e não três**: `DRENAR` (executa e mede) -> `REVISÃO DIRECIONADA` (ensina, no fechamento).

**Evidência que motivou:** na própria s170 o agente entregou um PREPARAR de 5 parágrafos antes do bloco de Cirurgia Infantil. O usuário respondeu os 8 cards **sem ter lido o bloco**, e o classificou como *"muito ruim, denso e confuso"*. Registro literal da decisão: *"proponho integrar tudo na revisão direcionada ao final"* e *"insisto em receber feedback via revisão direcionada no final da sessão de cards apenas, considerando as notas 1 e 2"*.

**Três razões, registradas para impedir re-derivação:**
1. **Ritual pulado não é degrau, é atrito.** Aquecimento que não é lido não aquece nada — e ainda consome o orçamento de atenção do drill.
2. **Vocabulário colapsado.** `refrescar`, `PREPARAR`, `Revisão Direcionada` e `aula-base` eram quatro nomes para duas coisas. Sobram duas superfícies de ensino, cada uma com gatilho próprio: a **Revisão Direcionada** (pós-cards, dirigida por nota 1-2) e a **`/aula-base`** (pré-questões, gatilho híbrido por dificuldade em `AGENTE.md §1.2`).
3. **Ensinar depois mira dado, ensinar antes mira palpite.** O gap tratado no fechamento foi **provado pelo drill**; o gap tratado no aquecimento é previsto pelo agente.

🔴 **O que NÃO mudou:** a `/aula-base` segue viva e intocada — ela é pré-**QUESTÕES**, não pré-cards, e tem eficácia medida (Meningites 53% -> 75%). O que morreu foi o aquecimento pré-**CARDS**.

**Realocações obrigatórias:**
- **Invariante B (carimbo de `review_log`)** migra do PREPARAR para a **Revisão Direcionada** — um carimbo por tema reabordado, `--kind directed_review` (ou `dormant_refresh` quando o tema entrou pela dormência). A curva continua sem cegar.
- **Tema dormente do dia** e **cluster frio (F5)** deixam de disparar aquecimento e passam a **entrar na fila de prioridade** da Revisão Direcionada de fechamento.
- **Cláusula 3 (degraus D10/D8/D5/D2)** e **Cláusula 10 (cobertura = piso fixo)** continuam válidas, agora calibrando a **Revisão Direcionada** em vez do PREPARAR.
- **Gatilho de andaime** (cunhar cards `base`/`mecanismo` quando um cluster inteiro cai) sobrevive, agora disparado **pelo resultado do drill**.

**Cláusula de forma (s170).** O bloco de fechamento tem de ser **legível de primeira**: prosa com hierarquia tipográfica, cada fato dito **uma vez só**, sem pilha de bullets nem parágrafo-monólito. Densidade que não é lida não ensina — foi exatamente esse o modo de falha do PREPARAR revogado.

---

## Fronteiras duras (resumo)

- O ensino (**Revisão Direcionada**) **nunca** escreve FSRS (Invariante A). DRENAR é a única superfície que move o FSRS.
- TODA Revisão Direcionada carimba `review_log` (Invariante B, realocado na v1.3) — a curva nunca cega.
- Rating só grava **após a janela de override**, uma vez por card (Invariante C) — não existe amend pós-record.
- ⚰️ Invariante D (isolamento do PREPARAR) **revogado na v1.3** — sem aquecimento pré-drill não há o que isolar.
- **Silêncio no meio do DRENAR** (Invariante F, v1.3): nota e tally durante o drill; prosa só no fechamento, sobre notas 1-2. Exceção: defeito de card.
- A nota **nunca** governa o agendamento FSRS — só a profundidade da preparação.
- Descompressão é calibrável; **cobertura de ponto de prova é piso fixo** (Invariante E / Cláusula 10) — compressão encurta, nunca corta.
- A nota que calibrou a aula é **registrada no fechamento** (`fonte='aula'`, Cláusula 10), sem sobrescrever `fonte='usuario'`.
- `set_dificuldade` toca só as 3 colunas de dificuldade. `infer_nota` é read-only e só lê sinais frios.

*Ratificação:* este contrato nasce `pending-ratification`; vira `canonical` após validação em uso (1ª abertura de task calibrada de ponta a ponta).
