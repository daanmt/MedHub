---
type: contract
layer: core
status: canonical
version: 1.7
relates_to: [forgetting-curve-contract, fsrs-management-contract, cronograma-contract, AGENTE]
---

# Contrato de Execução de Revisão Calibrada
**Versão 1.7 | 2026-09-22 (s192, MedHub HUB: Cláusula 15 -- o player mora na aba Cards de UM artifact permanente, republicado no lugar; a publicação de um artifact NOVO por lote é REVOGADA; a gravação no relógio da revisão, idempotente e com quarentena fica ESPECIFICADA -- part-2, pendente -- e, até ela, notas do hub não são gravadas) -- anterior: 1.6, 2026-09-18 (s186, R2/F112: Cláusula 14 -- a régua de notas passa a ser a NATIVA do FSRS e vira propriedade VERSIONADA de cada linha do revlog; a régua v1 é REVOGADA) -- anterior: 1.5, 2026-09-17 (s185, F110: Cláusula 13 -- fricção virtuosa não se automatiza; declarada SEM gate) -- anterior: 1.4, 2026-09-16 (s183: o DRENAR ganha uma SEGUNDA superficie -- o player de cards como pagina, Clausula 12. Nenhuma clausula revogada; A, C e F preservados por construcao) -- anterior: 1.3, 2026-09-08 (s170: o sub-modo PREPARAR e a Camada 1 sao REVOGADOS; todo o ensino migra para a Revisao Direcionada de fechamento -- Clausula 11, Invariante F, lapide do Invariante D); 1.2, 2026-07-06 (s109+, F18c/F21: Invariante E + Clausula 10); 1.1, 2026-07-05 (s108+, F8/F9: Invariantes C e D); 1.0, 2026-06-28 (sessao 096).**  <!-- NAO-NORMATIVA: linha de changelog/versao -->

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

Precedência **dura**: **input explícito do usuário > pergunta respondida > inferência do agente**. A inferência é a *proposta default*; nunca silencia um input do usuário.  <!-- CHECK: test_fonte_usuario_e_soberana -->

- **Input explícito** — soberano ("esse é um 8"), persistido `fonte='usuario'`.
- **Pergunta** — se a task abre sem nota: "De 1 a 10, quão difícil é X pra você hoje?".
- **Inferência** — `infer_nota()` (Cláusula 6), persistida `fonte='agente_inferida'`.  <!-- CHECK: test_boot_verdadeiro -->

**Divergência auto-nota × performance (§4.4).** O agente computa `nota_inferida` **mesmo quando há nota do usuário**. Se `|nota_usuario − nota_inferida| ≥ 3`, **sinaliza sem sobrescrever** ("Você marcou 3, mas seu histórico aqui é 48% e faz 26 dias — confirma o 3 ou subo pra 6?"). Dois limites duros: (a) a nota **NUNCA** governa o agendamento FSRS (regido por recall real em DRENAR); (b) se a nota foi baixa e o bloco seguinte sai fraco (`acerto_bloco < 60%`), a próxima abertura **propõe** nota maior citando a evidência.  <!-- NAO-VERIFICAVEL: o calculo tem codigo, mas 'o agente pergunta ao usuario na divergencia' e conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->

## Cláusula 3 — Mapa nota → degrau de registro (switches mecânicos)

Quatro degraus de formato, com switches **auditáveis por contagem/regex** (não adjetivos):

> **Regra D10 (extensivo) — única, idêntica em `tools/day_plan.py`, este contrato e `AGENTE.md §1.2`:** material extensivo ou inferência sem nota explícita → degrau D10 + dever de Deep-Researchness; a nota explícita do usuário (fonte=usuario) sempre vence (precedência input > pergunta > inferência).  <!-- NAO-VERIFICAVEL: identidade SEMANTICA entre 3 portadores (mesma norma, redacoes diferentes) -- o mesmo vao do F117 (revisar: 2026-12-31) -->

- **Degrau D10 (notas 9-10) — Onboarding do zero / Deep-Researchness.** Parágrafos: **7-9.** **Degrau 0 explícito** (a régua do "normal" antes da nuance). **Toda sigla definida por extenso na 1ª ocorrência.** Espinha: *mecanismo → por que existe → valores → ajustes → o que acontece se errar → contexto de uso*. Nenhum salto: cada seção referencia a anterior. **Obrigação de Deep-Researchness:** quando acionado por cronograma de extensivo ou nota 9-10, o agente tem o dever proativo de varrer a literatura de base em profundidade, antecipando conexões entre especialidades, controvérsias de bancas e exceções clínicas antes de o usuário realizar questões ou auditar resumos.
- **Degrau D8 (notas 7-8) — Descomprimido com mecanismo.** Parágrafos: **5-6.** Degrau 0 explícito; siglas-chave expandidas. Fundação + cadeia causal + nuance.
- **Degrau D5 (notas 4-6) — Gatilhos + armadilhas.** Parágrafos: **3-4.** Degrau 0 assumido conhecido. Mecanismo curto + conduta; fecha com gatilhos-de-prova + 🔴 armadilhas.
- **Degrau D2 (notas 1-3) — Só armadilhas / flash.** Parágrafos: **1-2** ou bullets. Sem reconstruir fundação. 🔴 armadilha + diferencial "X vs Y".

A nota explícita do usuário **escolhe o degrau diretamente**; sem nota, a faixa sai do `infer_nota()`. Implementação do mapa: `day_plan._degrau_de()` + `DEGRAU_PARAGRAFOS`.

## Cláusula 4 — Fases da sessão de cards (DRENAR → Revisão Direcionada)

⚰️ **Reescrita na v1.3 (s170).** A clausula descrevia a fusao do `/refrescar` num sub-modo de aquecimento pre-drill. Esse sub-modo foi **revogado pela Clausula 11** — o texto original fica no historico do git. `/revisar` continua sendo **uma porta so**; o que mudou foi o numero de fases dentro dela: **duas, nao tres**.  <!-- NAO-NORMATIVA: lapide da redacao revogada na v1.3 -->

- **DRENAR** (card-a-card; **ESCREVE FSRS**) — o player FSRS. **Primeira fase e unica superficie que move o FSRS.** Durante o drill: nota e tally, nada mais (Invariante F).  <!-- CHECK: test_invariante_a -->
- **REVISAO DIRECIONADA** (narrativo; **FSRS read-only**) — **segunda fase, no fechamento**, ancorada nos temas de nota **1-2**. **Unica superficie de ensino da sessao de cards** (Clausula 11).  <!-- CHECK: test_invariante_a -->
- Nao ha aquecimento antes do drill: **toda nota do DRENAR e recall a frio**, que e o sinal que o FSRS quer.
- **Duas superficies para a MESMA fase (v1.4):** o DRENAR acontece no chat **ou** no player de cards (Clausula 12). Continuam sendo **duas fases, nao tres** -- o player troca o veiculo do drill, nunca o lugar do ensino.  <!-- NAO-NORMATIVA: reafirma a contagem de fases, nao prescreve -->

**Arquitetura por propósito (v1.2, s110 — correção de calibração; alvo remapeado na v1.3).** ⚰️ O texto original calibrava o sub-modo revogado. **A regra sobrevive nas duas superficies que a Clausula 11 preserva**, cada uma herdando uma metade: rumo a **EXERCÍCIOS** -> **`/aula-base`** (pre-questoes, intocada pela v1.3); rumo a **FLASHCARDS** -> **Revisao Direcionada** de fechamento. O propósito não muda só a LARGURA; muda a **arquitetura** do ensino. **`/aula-base`, antes de questões:** os **degraus são fundamentais** — cobre o **escopo-árvore inteiro** que a prova cobra (doses, diferenciais, a árvore de decisão completa) e **DESTRINCHA o mecanismo** dos conceitos/exames discriminadores (não só os nomeia), mesmo em nota média. **Revisão Direcionada, depois dos cards:** o alvo é **fino e provado pelo drill** — os temas de nota 1-2, não uma varredura do cluster (compressão ok; o card já disse onde dói). ⭐ **Descompressão (nota) ≠ cobertura de mecanismo:** nomear um discriminador ("whiff+", "clue cells") sem abrir **o que é e por que** é profundidade D2 disfarçada de D5 — e reforça o **Invariante E / Cláusula 10** (a cobertura do ponto de decisão inclui abrir o mecanismo, não só citá-lo). Precedente vivo: aula de Vulvovaginites (s110) — os exames whiff/KOH/clue cells foram nomeados e não destrinchados; refeita com os degraus.  <!-- NAO-NORMATIVA: lapide do texto de calibracao original -->

## Cláusula 5 — Invariantes de integridade (barreiras invioláveis)

**Invariante A — o ensino é read-only no FSRS** *(sujeito remapeado na v1.3: era o sub-modo revogado, hoje é a **Revisão Direcionada** — Cláusula 11, Fronteiras duras)*. Writes permitidos na Revisão Direcionada: `review_log` (Invariante B) e edição de `resumos/` (acúmulo, nunca apaga). **Proibidos:** `record_review`, `insert_questao`, qualquer UPDATE em `fsrs_cards`/`fsrs_revlog`. **DRENAR é a única superfície que move o FSRS.** Auditada por `tools/test_revisao_calibrada.py` (a contagem de `fsrs_revlog`/`fsrs_cards` não muda numa Revisão Direcionada) + gate estático (`dormant_refresh.py` não menciona `record_review`/`fsrs_*`).  <!-- CHECK: test_invariante_a -->

**Invariante B — a Revisão Direcionada SEMPRE carimba `review_log`** *(realocado na v1.3 — Cláusula 11: o carimbo migra do sub-modo revogado para o fechamento)*. A curva de dormência é alimentada exclusivamente por `review_log`. Sem o carimbo, o radar acharia que o tema "nunca foi revisto" (loop, score distorcido). **Regra:** toda Revisão Direcionada, ao concluir, grava **1 linha por tema reabordado** via `db.log_review`/`dormant_refresh.py --stamp --kind`, com `kind` discriminado pelo gatilho:  <!-- NAO-VERIFICAVEL: 🔴 RAIO ALTO, custo declarado -- o carimbo tem CLI testado, mas nada obriga a chamada no fechamento; exigiria um evento de fim-de-sessao que nao existe (revisar: 2027-03-31) -->
- tema do **radar de dormência** → `kind='dormant_refresh'`;
- tema do **cronograma / fila FSRS / pedido direto** → `kind='directed_review'`.

**Invariante C — Janela de override ANTES do record (F9, v1.1).** No DRENAR, o rating só é gravado **depois** da janela de override: o agente **propõe** a nota (com justificativa de 1 linha), aguarda a resposta do usuário (confirmação, correção ou avanço), e **só então** chama `record_review` — **uma vez por card por sessão, sempre**. Não existe amend pós-record: `record_review` é append-only por design (INSERT em `fsrs_revlog` + UPDATE em `fsrs_cards`); re-gravar recalcula o FSRS sobre estado já mutado e corrompe o agendamento (caso real: card 403, s108 — nota 2 corrigida p/ 4 após o record moveu o due indevidamente e deixou 2 linhas de revlog). Se um erro de gravação real acontecer, registra-se o ocorrido em `history/session_NNN.md` como achado — **nunca** re-record. Esta invariante RESOLVE a contradição da v1.0 entre "o usuário pode sobrepor a nota" e a regra anti-duplo-registro: o override intencional acontece **dentro da janela**, antes da gravação. No modo lote, a janela é **única por lote** (notas propostas do lote inteiro → confirmação/correção → gravação do lote).  <!-- NAO-VERIFICAVEL: 🔴 RAIO ALTO, custo declarado -- provar a ORDEM (override antes do record) exigiria carimbar dois instantes no revlog, i.e. schema novo no caminho critico de escrita (revisar: 2027-03-31) -->

⚰️ **Invariante D — Isolamento de conteudo do PREPARAR (F8, v1.1) — REVOGADO na v1.3.** Existia para impedir que o aquecimento pre-drill vazasse a resposta dos cards do bloco. Com o PREPARAR revogado (Clausula 11) nao ha aquecimento antes do drill, logo nao ha o que isolar: toda nota do DRENAR volta a ser recall a frio, que e o sinal que o FSRS quer. O texto original fica no historico do git. **Nao re-derivar:** se alguem reintroduzir aquecimento pre-bloco, o Invariante D volta a ser necessario junto.  <!-- NAO-NORMATIVA: lapide do Invariante D revogado -->

**Invariante F — Silencio no meio do DRENAR (s170, v1.3).** Durante o DRENAR o agente entrega **verso + nota + tally, e nada mais**. Zero prosa explicativa entre blocos, **inclusive para nota 1 e 2**. Feedback no meio do drill quebra o ritmo e foi reprovado explicitamente pelo usuario em duas rodadas (s154: corta a prosa de nota 3; s170: corta tambem a de 1-2). **Unica excecao:** achado de **defeito de CARD** (pergunta composta, premissa embutida, contexto desalinhado, binaria) — e sobre a autoria do card, nao sobre o desempenho do usuario, e continua sendo reportado na hora, em uma linha. Auditavel por leitura do transcript, nao por teste automatico.  <!-- NAO-VERIFICAVEL: 🔴 RAIO ALTO -- no player e estrutural (nao ha canal de prosa) e por isso la e gate; no chat e ausencia de comportamento, que nao deixa artefato (revisar: 2027-03-31) -->

**Invariante E — Cobertura de ponto de prova é piso fixo (F21, v1.2).** A descompressão (nota 1-10) calibra **profundidade/prosa**; a **cobertura do conjunto de pontos de decisão de alto rendimento** do tema é **inviolável**. Nenhum degrau — nem o D2 (flash) — autoriza **ELIMINAR** um ponto de prova testável: comprimir **encurta** um ponto, **nunca o corta** (detalhamento na Cláusula 10). Raiz: a Q2 da s109 caiu num ponto de decisão (ileotiflectomia) que a descompressão D10→D7 eliminou em vez de encurtar. Auditada pela presença da Cláusula 10 + do checklist de cobertura no render.  <!-- NAO-VERIFICAVEL: cobertura de ponto de prova e semantica; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->

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

**Anti-circularidade (§7.6, invariante de sinal).** `infer_nota` lê **apenas sinais frios independentes da própria saída**: nunca (a) a profundidade do ensino que ela gerou, nem ⚰️ (b) *o acerto "morno" medido logo após o aquecimento pré-drill* — **exclusão órfã desde a v1.3**: sem aquecimento antes do drill, essa medição não pode mais ser produzida, e toda nota do DRENAR já é fria. A exclusão fica **como estava, não recalibrada** — mexer no `infer_nota` é spec própria, não hotfix de texto. 🔴 **Não re-derivar:** se o aquecimento pré-bloco voltar, (b) volta a ter alvo. **Histerese assimétrica:** a nota inferida **SOBE** com 1 sinal forte; só **DESCE** após ≥ 2 sinais frios consistentes (ex.: 2 blocos ≥ 80% **e** stability subindo). Errar para mais (descomprimir além) é mais barato que para menos.  <!-- CHECK: test_boot_verdadeiro -->

## Cláusula 7 — Persistência da nota

Estado **de tema** em `taxonomia_cronograma` (local-only): `dificuldade INTEGER` (1-10, NULL = não calibrado), `dificuldade_fonte TEXT` (`'usuario'|'agente_inferida'|'aula'`), `dificuldade_at TIMESTAMP`. Escrita **exclusivamente** via `db.set_dificuldade(area, tema, nota, fonte)` — 🔴 única exceção autorizada à regra "só `insert_questao` escreve `taxonomia_cronograma`": toca **apenas** as 3 colunas novas. **Frescor:** `NULL` ou (`agente_inferida` **e** `dificuldade_at` > 7 dias) → reinferir antes de abrir; `'aula'` é nota registrada (fato da forja, Cláusula 10) — **não** dispara reinferência automática. Nota `fonte='usuario'` é soberana (não recalcula a aplicada, mas computa a inferida p/ checar divergência).  <!-- NAO-NORMATIVA: descreve o schema da coluna, nao prescreve conduta -->

## Cláusula 8 — Degradação graciosa (prevalência ENAMED)

`core/cronograma/grade.json` ainda **não** carrega `prevalencia_enamed`. Enquanto não carregar: `prevalencia = 'media'` (peso neutro; eixo 4 não atua, sem piso de banca). Quando a grade ganhar o campo, basta `cronograma.py` fornecê-lo — **nenhuma** mudança em `infer_nota()`.

## Cláusula 9 — Decisões das questões abertas (PRD §10, propostas-semente ratificadas em uso)

1. **Nota por TEMA** (não por tema×tipo); o tipo de bloco modula a **largura** (amplo/direcionado), não a nota.
2. **Frescor = 7 dias** para reinferir nota `agente_inferida`.
3. **Histerese:** baixar a nota exige 2 sinais frios consistentes (blocos ≥ 80% + stability↑).  <!-- NAO-VERIFICAVEL: histerese e regra de decisao do agente sobre sinais; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
4. **Prevalência:** peso neutro até a grade carregar o campo (Cláusula 8).  <!-- NAO-NORMATIVA: declara peso neutro ate a grade carregar o campo -->
5. ⚰️ **Revogado na v1.3** — o item mandava o aquecimento pré-drill oferecer o DRENAR em seguida. Sem aquecimento, **o DRENAR é a entrada da sessão de cards**, não a segunda etapa de nada.
5b. **Cluster frio entra na fila da Revisão Direcionada (F5; reescrito na v1.3).** ⚰️ O item mandava o DRENAR **oferecer aquecimento** ao abrir um cluster frio — revogado pela Cláusula 11, que realoca o sinal em vez de descartá-lo. **Regra atual:** cluster com score de dormência `>= 25` (via `day_plan --review-plan`/`review_radar`) **entra na fila de prioridade da Revisão Direcionada de fechamento**, junto dos temas de nota 1-2. Não dispara nada antes do drill. O limiar vive AQUI (contrato), não no CLI — o CLI só expõe o score cru. 🔴 **O sensor não morreu, morreu o consumidor** (lápide do F5 em `AUDITORIA_MEDHUB.md:68`).  <!-- NAO-VERIFICAVEL: conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
6. **Soberania do usuário prevalece** mesmo com dormência alta — o agente sinaliza a divergência, não sobrescreve.

## Cláusula 10 — Descompressão (calibrável) × Cobertura (piso fixo) + registro no ato (F18c/F21, v1.2)

Duas dimensões **ortogonais** no render de qualquer ensino calibrado — **`/aula-base`** (pré-questões) ou **Revisão Direcionada** (fechamento dos cards) —, que **não se confundem**:

- **Descompressão = elástico (calibrável).** A nota 1-10 governa a **profundidade** narrativa, o nº de parágrafos e a prosa (Cláusula 3). Tema fácil/quente comprime; difícil/frio descomprime.  <!-- NAO-VERIFICAVEL: profundidade narrativa e semantica; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
- **Cobertura de pontos de decisão de alto rendimento = PISO FIXO (não calibrável).** O **conjunto** de pontos de prova testáveis do tema é um piso por tema, derivado do **sumário da fonte** (índice do resumo / aula-base; precedente s089 — o LCR lido por dado parcial, não pelo conjunto). Mesmo em **D2** (nota 1-3, flash) o render passa pelo **checklist de cobertura** antes de fechar: comprimir a **prosa** de um ponto é legítimo; **eliminar** o ponto não é. **Compressão encurta um ponto de decisão; nunca o exclui** (Invariante E). Raiz do F21: a Q2 da s109 caiu exatamente num ponto (ileotiflectomia) que a descompressão D10→D7 **eliminou** em vez de encurtar.  <!-- NAO-VERIFICAVEL: idem 138 -- o PISO e um conjunto semantico de pontos (revisar: 2027-03-31) -->

**Dependência de operacionalização (não bloqueia a cláusula).** O checklist **mecânico** de cobertura deriva o piso do sumário da fonte — que depende da cobertura de `.md`/sumário (relatório de cobertura do pipeline de conhecimento; o RAG é **gold-only** — a collection `pdf_raw`/two-tier foi removida na consolidação part-2). Enquanto a cobertura mecânica não amadurece, o piso deriva **do que houver** (índice do resumo presente ou o escopo exato do cronograma). A cláusula é a **barreira de conduta agora**; o motor mecânico vem com a cobertura.  <!-- NAO-NORMATIVA: declara dependencia de operacionalizacao, nao prescreve -->

**Registro no ato (F18c).** A nota 1-10 que **calibrou** a descompressão é **registrada no fechamento** da aula via `db.set_dificuldade(area, tema, nota, fonte='aula')` — o sinal caro da forja da aula deixa de ser efêmero e passa a alimentar a Revisão Calibrada. **Respeita a precedência da Cláusula 2:** `fonte='aula'` **não sobrescreve** uma nota soberana `fonte='usuario'` (registra apenas quando a nota da aula não colide com input explícito do usuário). **Zero schema novo** — reusa as 3 colunas de dificuldade e o `set_dificuldade` existente.  <!-- NAO-VERIFICAVEL: o writer `set_dificuldade` e testado (allowlist F49); 'registrar no fechamento' e conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->

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
- **Invariante B (carimbo de `review_log`)** migra do PREPARAR para a **Revisão Direcionada** — um carimbo por tema reabordado, `--kind directed_review` (ou `dormant_refresh` quando o tema entrou pela dormência). A curva continua sem cegar.  <!-- NAO-NORMATIVA: changelog da migracao do Invariante B -->
- **Tema dormente do dia** e **cluster frio (F5)** deixam de disparar aquecimento e passam a **entrar na fila de prioridade** da Revisão Direcionada de fechamento.
- **Cláusula 3 (degraus D10/D8/D5/D2)** e **Cláusula 10 (cobertura = piso fixo)** continuam válidas, agora calibrando a **Revisão Direcionada** em vez do PREPARAR.  <!-- NAO-NORMATIVA: changelog de quais clausulas seguem validas -->
- **Gatilho de andaime** (cunhar cards `base`/`mecanismo` quando um cluster inteiro cai) sobrevive, agora disparado **pelo resultado do drill**.

**Cláusula de forma (s170).** O bloco de fechamento tem de ser **legível de primeira**: prosa com hierarquia tipográfica, cada fato dito **uma vez só**, sem pilha de bullets nem parágrafo-monólito. Densidade que não é lida não ensina — foi exatamente esse o modo de falha do PREPARAR revogado.  <!-- NAO-VERIFICAVEL: legibilidade do bloco de fechamento e julgamento; conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->

---

## Cláusula 12 -- O player de cards é superfície de DRENAR, não uma terceira fase (s183, v1.4)

**Decisão do usuário (PRD `plano-ssot-e-cards-v2`, P4).** Drenar 60 cards no chat custa turnos demais. O DRENAR passa a ter **duas superfícies**, e só o veículo muda:

- **Conversacional** -- o loop card-a-card desta skill, que continua sendo o default.
- **Player** -- uma página com teclado e toque: `Espaço` vira, `1-4` dá a nota, `D` marca defeito com motivo curto. O player é `core/templates/player.html` (fonte única); desde a v1.7 ele mora na **aba Cards do MedHub HUB** (Cláusula 15). ⚰️ *Até a v1.6 cada lote era montado por `--build-player` e publicado como um artifact NOVO com `capabilities: {db: {}}` -- revogado na s192: a conta claude.ai é compartilhada, o operador apagava os artifacts por higiene e as notas do `db` iam junto.*  <!-- CHECK: test_hub -->

**As duas são a MESMA fase.** A sessão continua tendo **duas fases e não três** (Cláusula 4): o player substitui o veículo do DRENAR, nunca a Revisão Direcionada, que segue no chat, no fechamento, sobre as notas 1-2.  <!-- NAO-NORMATIVA: reafirma a contagem de fases -->

🔴 **Os invariantes são preservados por CONSTRUÇÃO, não por disciplina:**

- **Invariante A (o ensino não escreve FSRS)** -- a página não ensina: ela mostra frente, verso e tally. Nenhuma prosa, nenhum re-ensino. O ensino inteiro continua na Revisão Direcionada.  <!-- CHECK: test_invariante_a -->
- **Invariante C (trava técnica em `record_review`)** -- a página **não tem caminho de escrita para o FSRS**. Ela grava a primeira nota de cada card na capability `db` (coleção `sessoes/<sessao>/notas`, 1 doc por card: `{card_id, rating_primeira, ts, defeito?, motivo?}`); quem move o FSRS é `fsrs_queue.py --record-lote`, que chama `record_review`. A janela de override do lote acontece **no dry-run**, antes do `--apply`; depois do `--apply` não há amend, como sempre. Auditado por `tools/test_fsrs_queue_player.py` (o `fsrs_queue.py` não ganha tabela nova na allowlist F49).  <!-- CHECK: test_dry_run_nao_grava_nada -->
- **Invariante F (silêncio no meio)** -- estrutural: não há canal para prosa durante o drill. A exceção de sempre (defeito de card) é a tecla `D`, que vira marca de reforja (`origem='player'`) em vez de uma linha no chat.  <!-- NAO-VERIFICAVEL: no player e estrutural; a clausula tambem governa o chat, onde e conduta do agente, sem artefato que a registre (revisar: 2027-03-31) -->
- **Regra anti-duplo-registro** -- o relearning da página recoloca o card no **fim do lote** e **não gera segunda nota gravável**: a página guarda `rating_primeira` e nunca a sobrescreve. O CLI reforça: `card_id` repetido no arquivo de notas conta **uma** revisão, com WARN.  <!-- CHECK: test_duplicata_gera_uma_unica_revisao -->

**Rito de gravação (mesma disciplina de operação em massa, `AGENTE.md §10.7`):** dry-run -> `--apply --expect N` com o N medido -> COUNT-ASSERT pós (`fsrs_revlog` cresceu exatamente N). A página é **input não confiável**: `card_id` é validado contra o export e `rating` tem de estar em 1..4 antes de qualquer escrita.

**Degradação declarada.** Se `claude.use("db")` devolver `null` (capability não concedida, visualização sem runtime), a página **declara na tela** que o armazenamento está fora e expõe as notas em JSON para colar no chat -- mesmo formato que o `--record-lote` consome. Nunca perde o lote em silêncio.  <!-- NAO-VERIFICAVEL: degradacao sem capability acontece no navegador do operador, fora do alcance do harness (revisar: 2027-03-31) -->

**Fora de escopo por decisão:** sem botão "aposentar" na página (aposentar é `reforja.py` / `cards_prune.py`) e sem Revisão Direcionada dentro dela.

---

## Cláusula 15 -- o player mora no MedHub HUB, um artifact só (s192, v1.7)

**Decisão do operador (22/09/2026) e do `/ai-eng` (PRD `medhub-hub-2026-09-22`, spec `medhub-hub-v0`).** A causa das notas e links perdidos não era hospedagem: a conta claude.ai é **compartilhada com o time de conteúdo**, cada lote virava um artifact novo na galeria do time, e o operador apagava por higiene. O DRENAR no player passa a acontecer na **aba Cards do MedHub HUB**: UM artifact fixado, com `description` "NÃO apagar", republicado **no lugar** a cada lote (URL nas 8 primeiras linhas do `HANDOFF.md`). O rito é o de `.claude/commands/revisar.md`, "DRENAR no player".  <!-- NAO-NORMATIVA: registra a decisao e aponta o portador do rito -->

- **Mesma fase, mesmo player.** A Cláusula 12 segue inteira: duas fases, não três; a página não ensina (Invariante A); a página não tem caminho de escrita para o FSRS (Invariante C); silêncio no meio (Invariante F). O hub só compõe o MESMO `core/templates/player.html` (`tools/hub.py --build`) ao lado das abas Aulas e Painel.  <!-- CHECK: test_dry_run_nao_grava_nada -->
- **Relógio da revisão (a entrar com a part-2, `medhub-hub-v0-part-2`, pendente em 22/09).** O `--record-lote` passa a gravar cada nota no momento em que ela foi dada (o `ts` da página, em hora local, truncado ao segundo), não na hora da gravação: é o que o FSRS modela, e é o que torna a gravação idempotente por igualdade. Revisão mais nova sem a igual = FORA DE ORDEM, reportada, nunca gravada por cima. **Até lá, notas do hub não são gravadas** (gate no rito de `revisar.md`, com TERMINAL: part-2 verde na s193, senão fallback no fechamento dela -- o congelamento nunca atravessa 2 sessões de estudo).  <!-- NAO-VERIFICAVEL: part-2 pendente em 22/09; vira CHECK quando entrar (revisar: 2026-09-30) -->
- **Quarentena no writer.** A conta é compartilhada, quem abre é OWNER, e o owner atende todo nível das regras do `db` -- a regra (`sessoes` = `interact`, o resto = `admin`) limita membro da organização, não o owner. Por isso a fronteira real é o CLI: doc estranho é rejeitado e reportado, e os válidos seguem (a entrar com a part-2; hoje o doc estranho ainda recusa o lote inteiro, que é o lado seguro).  <!-- NAO-VERIFICAVEL: part-2 pendente em 22/09; vira CHECK quando entrar (revisar: 2026-09-30) -->
- **Poda.** O `db` de um artifact guarda no máximo 5.000 documentos (medido no servidor em 22/09: "1 of 5000 documents used") e a página grava 1 por card: a sessão que SAIU da aba é podada depois de uma releitura dar 0 novas e 0 rejeitadas; a do lote corrente, nunca. Depende da idempotência da part-2.  <!-- NAO-VERIFICAVEL: a poda e ato do agente via ArtifactData, fora do alcance do harness (revisar: 2027-03-31) -->
- **Hub apagado** (`artifact-deleted`): recriado com o 1o publish completo e REPORTADO no HANDOFF e no session log; as notas do `db` foram com ele e isso é dado, nunca silêncio.  <!-- NAO-VERIFICAVEL: recriar e reportar sao atos do agente fora do harness (revisar: 2027-03-31) -->

---

## Fronteiras duras (resumo)

- O ensino (**Revisão Direcionada**) **nunca** escreve FSRS (Invariante A). DRENAR é a única superfície que move o FSRS.  <!-- CHECK: test_invariante_a -->
- TODA Revisão Direcionada carimba `review_log` (Invariante B, realocado na v1.3) — a curva nunca cega.  <!-- NAO-VERIFICAVEL: mesmo vao do Invariante B (linha 69) (revisar: 2027-03-31) -->
- Rating só grava **após a janela de override**, uma vez por card (Invariante C) -- não existe amend pós-record. No player (Cláusula 12) a janela é o **dry-run** do `--record-lote`, e a página não tem caminho de escrita para o FSRS.  <!-- CHECK: test_duplicata_gera_uma_unica_revisao -->
- O **player é veículo do DRENAR**, não fase nova (Cláusula 12, v1.4): duas superfícies, dois invariantes preservados por construção, uma só Revisão Direcionada no chat.  <!-- NAO-NORMATIVA: reafirma o desenho do player como veiculo -->
- ⚰️ Invariante D (isolamento do PREPARAR) **revogado na v1.3** — sem aquecimento pré-drill não há o que isolar.  <!-- NAO-NORMATIVA: lapide do Invariante D -->
- **Silêncio no meio do DRENAR** (Invariante F, v1.3): nota e tally durante o drill; prosa só no fechamento, sobre notas 1-2. Exceção: defeito de card.  <!-- NAO-VERIFICAVEL: mesmo vao do Invariante F (linha 77) (revisar: 2027-03-31) -->
- A nota **nunca** governa o agendamento FSRS — só a profundidade da preparação. *(Esta fronteira fala da nota de DIFICULDADE-POR-TEMA 1-10. A nota de card 1-4 é outra coisa: ela é o input do modelo, e desde a v1.6 tem régua declarada -- Cláusula 14.)*  <!-- CHECK: test_writer_allowlist -->
- A **régua da nota de card é a nativa do FSRS** e cada revisão carrega a versão sob a qual foi dada (Cláusula 14) — trocar o vocabulário nunca reinterpreta o histórico.  <!-- CHECK: test_regua_fsrs -->
- Descompressão é calibrável; **cobertura de ponto de prova é piso fixo** (Invariante E / Cláusula 10) — compressão encurta, nunca corta.  <!-- NAO-VERIFICAVEL: mesmo vao das linhas 138-139 (revisar: 2027-03-31) -->
- A nota que calibrou a aula é **registrada no fechamento** (`fonte='aula'`, Cláusula 10), sem sobrescrever `fonte='usuario'`.  <!-- CHECK: test_fonte_usuario_e_soberana -->
- `set_dificuldade` toca só as 3 colunas de dificuldade. `infer_nota` é read-only e só lê sinais frios.

*Ratificação:* este contrato nasce `pending-ratification`; vira `canonical` após validação em uso (1ª abertura de task calibrada de ponta a ponta).

---

## Cláusula 14 -- a régua da nota de card é a NATIVA do FSRS, e é versionada (v1.6, R2/F112, s186)

**A régua.** No DRENAR a nota 1-4 mede **esforço de recuperação**, não completude da resposta:

| nota | significado | como o motor a trata |
|---|---|---|
| **1** | falhou -- não recuperou, ou "não sei" | único lapso; o card volta hoje |
| **2** | lembrou **com esforço** -- chegou lá, mas custou | acerto difícil; intervalo curto |
| **3** | lembrou -- recuperação normal | **o caso padrão** |
| **4** | lembrou **sem esforço** -- imediato | raro por construção |

**Portador único:** [`app/utils/regua.py`](../../app/utils/regua.py). O `revisar.md`, o player e o
otimizador **leem** de lá; nenhum deles redefine a tabela.

⚰️ **A régua v1 (completude: *"cravou conceito + regra-mestre -> 4 ... recall parcial sem o alvo -> 2"*)
está REVOGADA desde 18/09/2026.** Medido no F112: como o motor lê a escala por esforço, a nota 2 --
o card que o usuário **não** lembrou -- era agendada como acerto e voltava em ~14 dias. Decisão do
operador em 17/09 (opção (b)), com os números do R1 na mão.

🔴 **Revogar o vocabulário não pode reescrever o passado.** As 3.067 revisões gravadas sob a v1  <!-- CHECK: test_regua_fsrs -->
continuam existindo, e sob a régua nova elas significariam outra coisa. Por isso a régua é
propriedade **da linha**: `fsrs_revlog.regua_versao` carimba toda revisão nova, o histórico fica
`NULL` (= v1 **por declaração**, nunca por inferência), e a tradução v1 -> nativa acontece **só na  <!-- CHECK: test_regua_fsrs -->
entrada do Optimizer**. O revlog é imutável; não há backfill.

**Consequência no player (Cláusula 12):** o relearning intra-sessão passa de `nota < 4` para  <!-- CHECK: test_regua_fsrs -->
**`nota < 3`** -- repete enquanto falhou ou custou. Sob a v1, exigir 4 era exigir domínio; sob a v2
seria exigir ausência de esforço, e o 3 nunca sairia da fila.  <!-- NAO-NORMATIVA: justificativa do limiar, continuacao da linha 237 -->

**Parâmetros do modelo seguem os de referência do py-fsrs.** `app/utils/fsrs.py` consulta
`core/fsrs_params.json` e **recusa** adotar conjunto cuja régua de ajuste não seja a régua de
escrita (F114: na visão `remap` do R1, `w3` e `w16` -- stability inicial e bônus de Easy -- são o
default intocado, porque aquela visão mapeia `4 -> 3` e não tem um único exemplo de Easy). A meta
de retenção fica em **0,90** até haver `review_duration_ms` medido.

---

## Cláusula 13 -- fricção virtuosa não se automatiza (v1.5, F110, s185)

Nem todo atrito no estudo é desperdício. Recall antes de virar o verso, recall a frio, nota honesta,
relearning até o critério, racional declarado, ritual de prova e triagem humana de card são
**dificuldades desejáveis**: é delas que vem a retenção. O atrito vicioso é outro -- copiar id à mão,
descobrir um defeito de lote por vez, procurar o card certo sem porta de consulta.

🔴 **Antes de propor qualquer reforma cujo argumento seja "reduzir atrito", ler o ledger de fricções
em [`docs/FUNDAMENTOS-APRENDIZAGEM.md`](../../docs/FUNDAMENTOS-APRENDIZAGEM.md) e dizer de qual dos
dois se trata.** Toda spec nova responde, em uma linha: **"que fricção esta spec remove, e ela é
virtuosa ou viciosa?"** Remover fricção virtuosa é regressão pedagógica com cara de melhoria de
produto -- e o gate não pega, porque o código fica mais limpo.

⚠️ **Limite declarado (§10.8):** esta cláusula **não tem gate**. Nenhum check distingue as duas  <!-- NAO-NORMATIVA: DECLARA que a clausula nao tem gate -- e a declaracao, nao a clausula -->
fricções, e inventar uma métrica para o painel ficar verde seria pior que declarar o buraco. O
portador é a leitura obrigatória, e a falha de leitura é invisível por construção.  <!-- NAO-NORMATIVA: continuacao do limite declarado da linha 262 -->
