---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [forgetting-curve-contract, fsrs-management-contract, cronograma-contract, AGENTE]
---

# Contrato de Execução de Revisão Calibrada
**Versão 1.2 | 2026-07-06 (s109+, F18c/F21 do pipeline de conhecimento: Invariante E + Cláusula 10) — anterior: 1.1, 2026-07-05 (s108+, F8/F9: Invariantes C e D); 1.0, 2026-06-28 (sessão 096). Materializa o PRD `docs/plans/s094-revisao-calibrada-PRD.md` (revisão adversarial) + PRD `pipeline-conhecimento` (Onda 3).**

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

## Cláusula 4 — Fusão em sub-modos (PREPARAR / DRENAR)

`/refrescar` deixa de ser skill autônoma e vira o **sub-modo PREPARAR** dentro de `/revisar`. Uma porta só; a fronteira vira **interna** (dois sub-modos com permissões disjuntas).

- **PREPARAR** (narrativo; FSRS read-only) — releitura calibrada ao degrau (Cláusula 3) e ao **propósito**: **amplo** rumo a EXERCÍCIOS (cobre o escopo do cronograma com postura proativa de revelar nuances e interconexões sob D10) ou **direcionado** rumo a FLASHCARDS (foca o cluster vencido). Largura (propósito) e profundidade (nota) são **ortogonais**.
- **DRENAR** (card-a-card; ESCREVE FSRS) — o player FSRS atual (Camadas 1/2 do `/revisar`). Única superfície que move o FSRS.
- A transição **PREPARAR → DRENAR** é o único ponto em que o FSRS passa a ser escrito.

## Cláusula 5 — Invariantes de integridade (barreiras invioláveis)

**Invariante A — PREPARAR é read-only no FSRS.** Writes permitidos em PREPARAR: `review_log` (Invariante B) e, na Camada 2, edição de `resumos/` (acúmulo, nunca apaga). **Proibidos:** `record_review`, `insert_questao`, qualquer UPDATE em `fsrs_cards`/`fsrs_revlog`. Auditada por `tools/test_revisao_calibrada.py` (a contagem de `fsrs_revlog`/`fsrs_cards` não muda num PREPARAR) + gate estático (`dormant_refresh.py` não menciona `record_review`/`fsrs_*`).

**Invariante B — PREPARAR SEMPRE carimba `review_log`.** A curva de dormência é alimentada exclusivamente por `review_log`. Ao virar sub-modo acionável também por tema do cronograma (não-dormente), o carimbo deixaria de ser garantido — e o radar acharia que o tema "nunca foi revisto" (loop, score distorcido). **Regra:** todo PREPARAR, ao concluir, grava 1 linha via `db.log_review`/`dormant_refresh.py --stamp --kind`, com `kind` discriminado pelo gatilho:
- tema do **radar de dormência** → `kind='dormant_refresh'`;
- tema do **cronograma / fila FSRS / pedido direto** → `kind='directed_review'`.

**Invariante C — Janela de override ANTES do record (F9, v1.1).** No DRENAR, o rating só é gravado **depois** da janela de override: o agente **propõe** a nota (com justificativa de 1 linha), aguarda a resposta do usuário (confirmação, correção ou avanço), e **só então** chama `record_review` — **uma vez por card por sessão, sempre**. Não existe amend pós-record: `record_review` é append-only por design (INSERT em `fsrs_revlog` + UPDATE em `fsrs_cards`); re-gravar recalcula o FSRS sobre estado já mutado e corrompe o agendamento (caso real: card 403, s108 — nota 2 corrigida p/ 4 após o record moveu o due indevidamente e deixou 2 linhas de revlog). Se um erro de gravação real acontecer, registra-se o ocorrido em `history/session_NNN.md` como achado — **nunca** re-record. Esta invariante RESOLVE a contradição da v1.0 entre "o usuário pode sobrepor a nota" e a regra anti-duplo-registro: o override intencional acontece **dentro da janela**, antes da gravação. No modo lote, a janela é **única por lote** (notas propostas do lote inteiro → confirmação/correção → gravação do lote).

**Invariante D — Isolamento de conteúdo do PREPARAR (F8, v1.1).** O PREPARAR aquece **conceitos e mecanismos**, **nunca** o par pergunta-resposta específico dos cards do bloco que vem a seguir. Regras operacionais: (a) o refresh é montado a partir do resumo/substrato do tema **sem abrir os versos** dos cards do bloco; (b) formulações sempre como **tendência** ("geralmente X; considerar Y se Z"), nunca como absoluto — uma imprecisão no aquecimento vira erro induzido no card seguinte (erro de ensino amplificado, 3º canal de viés observado na s108); (c) **distinção de classe de card**: em cards de **raciocínio/conduta**, aquecer o framework é legítimo — mas a nota pós-refresh mede "pegou o framework", não recall a frio, e isso é sinalizado; em cards de **fato puro** (definição/eponímia/dado seco), o refresh é **contraindicado** — aquecê-los É entregar a resposta; o refresh limita-se à orientação de entorno e o fato cobrado é retido para o recall.

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

**Anti-circularidade (§7.6, invariante de sinal).** `infer_nota` lê **apenas sinais frios independentes da própria saída**: nunca (a) a profundidade da preparação que ela gerou, nem (b) o acerto "morno" medido logo após PREPARAR (o aquecimento infla o recall). **Histerese assimétrica:** a nota inferida **SOBE** com 1 sinal forte; só **DESCE** após ≥ 2 sinais frios consistentes (ex.: 2 blocos ≥ 80% **e** stability subindo). Errar para mais (descomprimir além) é mais barato que para menos.

## Cláusula 7 — Persistência da nota

Estado **de tema** em `taxonomia_cronograma` (local-only): `dificuldade INTEGER` (1-10, NULL = não calibrado), `dificuldade_fonte TEXT` (`'usuario'|'agente_inferida'|'aula'`), `dificuldade_at TIMESTAMP`. Escrita **exclusivamente** via `db.set_dificuldade(area, tema, nota, fonte)` — 🔴 única exceção autorizada à regra "só `insert_questao` escreve `taxonomia_cronograma`": toca **apenas** as 3 colunas novas. **Frescor:** `NULL` ou (`agente_inferida` **e** `dificuldade_at` > 7 dias) → reinferir antes de abrir; `'aula'` é nota registrada (fato da forja, Cláusula 10) — **não** dispara reinferência automática. Nota `fonte='usuario'` é soberana (não recalcula a aplicada, mas computa a inferida p/ checar divergência).

## Cláusula 8 — Degradação graciosa (prevalência ENAMED)

`core/cronograma/grade.json` ainda **não** carrega `prevalencia_enamed`. Enquanto não carregar: `prevalencia = 'media'` (peso neutro; eixo 4 não atua, sem piso de banca). Quando a grade ganhar o campo, basta `cronograma.py` fornecê-lo — **nenhuma** mudança em `infer_nota()`.

## Cláusula 9 — Decisões das questões abertas (PRD §10, propostas-semente ratificadas em uso)

1. **Nota por TEMA** (não por tema×tipo); o tipo de bloco modula a **largura** (amplo/direcionado), não a nota.
2. **Frescor = 7 dias** para reinferir nota `agente_inferida`.
3. **Histerese:** baixar a nota exige 2 sinais frios consistentes (blocos ≥ 80% + stability↑).
4. **Prevalência:** peso neutro até a grade carregar o campo (Cláusula 8).
5. **PREPARAR oferece DRENAR** em seguida (competência única); pode encerrar como pura preparação se o usuário parar.
5b. **DRENAR oferece PREPARAR quando o cluster está frio (F5, v1.1):** o gatilho do aquecimento deixa de morar só no pedido do usuário — ao abrir um cluster no DRENAR com sinal frio (score de dormência `>= 25` via `day_plan --review-plan`/`review_radar`), o agente **oferece** o PREPARAR proativamente. Oferta, nunca execução automática; recusa do usuário vale para a sessão. O limiar vive AQUI (contrato), não no CLI — o CLI só expõe o score cru.
6. **Soberania do usuário prevalece** mesmo com dormência alta — o agente sinaliza a divergência, não sobrescreve.

## Cláusula 10 — Descompressão (calibrável) × Cobertura (piso fixo) + registro no ato (F18c/F21, v1.2)

Duas dimensões **ortogonais** no render de qualquer aula/PREPARAR calibrado, que **não se confundem**:

- **Descompressão = elástico (calibrável).** A nota 1-10 governa a **profundidade** narrativa, o nº de parágrafos e a prosa (Cláusula 3). Tema fácil/quente comprime; difícil/frio descomprime.
- **Cobertura de pontos de decisão de alto rendimento = PISO FIXO (não calibrável).** O **conjunto** de pontos de prova testáveis do tema é um piso por tema, derivado do **sumário da fonte** (índice do resumo / aula-base; precedente s089 — o LCR lido por dado parcial, não pelo conjunto). Mesmo em **D2** (nota 1-3, flash) o render passa pelo **checklist de cobertura** antes de fechar: comprimir a **prosa** de um ponto é legítimo; **eliminar** o ponto não é. **Compressão encurta um ponto de decisão; nunca o exclui** (Invariante E). Raiz do F21: a Q2 da s109 caiu exatamente num ponto (ileotiflectomia) que a descompressão D10→D7 **eliminou** em vez de encurtar.

**Dependência de operacionalização (não bloqueia a cláusula).** O checklist **mecânico** de cobertura deriva o piso do sumário da fonte — que depende da cobertura de `.md`/sumário (Partes 1-2 do pipeline de conhecimento: relatório de cobertura + RAG two-tier). Enquanto a cobertura mecânica não amadurece, o piso deriva **do que houver** (índice do resumo presente ou o escopo exato do cronograma). A cláusula é a **barreira de conduta agora**; o motor mecânico vem com a cobertura.

**Registro no ato (F18c).** A nota 1-10 que **calibrou** a descompressão é **registrada no fechamento** da aula/PREPARAR via `db.set_dificuldade(area, tema, nota, fonte='aula')` — o sinal caro da forja da aula deixa de ser efêmero e passa a alimentar a Revisão Calibrada. **Respeita a precedência da Cláusula 2:** `fonte='aula'` **não sobrescreve** uma nota soberana `fonte='usuario'` (registra apenas quando a nota da aula não colide com input explícito do usuário). **Zero schema novo** — reusa as 3 colunas de dificuldade e o `set_dificuldade` existente.

---

## Fronteiras duras (resumo)

- PREPARAR **nunca** escreve FSRS (Invariante A). DRENAR é a única superfície que move o FSRS.
- TODO PREPARAR carimba `review_log` (Invariante B) — a curva nunca cega.
- Rating só grava **após a janela de override**, uma vez por card (Invariante C) — não existe amend pós-record.
- PREPARAR isolado das respostas do bloco; fato puro não se aquece (Invariante D) — a validade do trial de recall é sagrada.
- A nota **nunca** governa o agendamento FSRS — só a profundidade da preparação.
- Descompressão é calibrável; **cobertura de ponto de prova é piso fixo** (Invariante E / Cláusula 10) — compressão encurta, nunca corta.
- A nota que calibrou a aula é **registrada no fechamento** (`fonte='aula'`, Cláusula 10), sem sobrescrever `fonte='usuario'`.
- `set_dificuldade` toca só as 3 colunas de dificuldade. `infer_nota` é read-only e só lê sinais frios.

*Ratificação:* este contrato nasce `pending-ratification`; vira `canonical` após validação em uso (1ª abertura de task calibrada de ponta a ponta).
