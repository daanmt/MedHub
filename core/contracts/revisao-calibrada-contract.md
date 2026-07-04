---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [forgetting-curve-contract, fsrs-management-contract, cronograma-contract, AGENTE]
---

# Contrato de Execução de Revisão Calibrada
**Versão 1.0 | 2026-06-28 (sessão 096) — primeira instância. Materializa o PRD `docs/plans/s094-revisao-calibrada-PRD.md` (revisão adversarial).**

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

Estado **de tema** em `taxonomia_cronograma` (local-only): `dificuldade INTEGER` (1-10, NULL = não calibrado), `dificuldade_fonte TEXT` (`'usuario'|'agente_inferida'`), `dificuldade_at TIMESTAMP`. Escrita **exclusivamente** via `db.set_dificuldade(area, tema, nota, fonte)` — 🔴 única exceção autorizada à regra "só `insert_questao` escreve `taxonomia_cronograma`": toca **apenas** as 3 colunas novas. **Frescor:** `NULL` ou (`agente_inferida` **e** `dificuldade_at` > 7 dias) → reinferir antes de abrir. Nota `fonte='usuario'` é soberana (não recalcula a aplicada, mas computa a inferida p/ checar divergência).

## Cláusula 8 — Degradação graciosa (prevalência ENAMED)

`core/cronograma/grade.json` ainda **não** carrega `prevalencia_enamed`. Enquanto não carregar: `prevalencia = 'media'` (peso neutro; eixo 4 não atua, sem piso de banca). Quando a grade ganhar o campo, basta `cronograma.py` fornecê-lo — **nenhuma** mudança em `infer_nota()`.

## Cláusula 9 — Decisões das questões abertas (PRD §10, propostas-semente ratificadas em uso)

1. **Nota por TEMA** (não por tema×tipo); o tipo de bloco modula a **largura** (amplo/direcionado), não a nota.
2. **Frescor = 7 dias** para reinferir nota `agente_inferida`.
3. **Histerese:** baixar a nota exige 2 sinais frios consistentes (blocos ≥ 80% + stability↑).
4. **Prevalência:** peso neutro até a grade carregar o campo (Cláusula 8).
5. **PREPARAR oferece DRENAR** em seguida (competência única); pode encerrar como pura preparação se o usuário parar.
6. **Soberania do usuário prevalece** mesmo com dormência alta — o agente sinaliza a divergência, não sobrescreve.

---

## Fronteiras duras (resumo)

- PREPARAR **nunca** escreve FSRS (Invariante A). DRENAR é a única superfície que move o FSRS.
- TODO PREPARAR carimba `review_log` (Invariante B) — a curva nunca cega.
- A nota **nunca** governa o agendamento FSRS — só a profundidade da preparação.
- `set_dificuldade` toca só as 3 colunas de dificuldade. `infer_nota` é read-only e só lê sinais frios.

*Ratificação:* este contrato nasce `pending-ratification`; vira `canonical` após validação em uso (1ª abertura de task calibrada de ponta a ponta).
