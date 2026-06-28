---
type: prd
projeto: MedHub
sessao: s094
status: draft
autor: arquiteto-de-produto (agente) · revisado-adversarialmente (agente)
data: 2026-06-27
relates_to:
  - .claude/commands/revisar.md
  - .claude/commands/refrescar.md
  - core/contracts/forgetting-curve-contract.md
  - core/contracts/fsrs-management-contract.md
  - docs/plans/s094-ultraplan.md
  - tools/day_plan.py
  - tools/performance.py
  - tools/review_radar.py
  - tools/dormant_refresh.py
  - app/engine/get_topic_context.py
  - memory/feedback_aula_descomprimida_preferencia.md
titulo: "Contrato de Execução de Revisão Calibrada"
---

# PRD — Contrato de Execução de Revisão Calibrada (MedHub, s094)

> **Uma frase:** unificar `/revisar` e `/refrescar` numa competência única `/revisar` cuja **descompressão é calibrada por uma nota de dificuldade-para-o-usuário de 1 a 10 por tema**, definida na abertura de cada task do cronograma — **sem cegar a curva de esquecimento por tema** (radar de dormência + `review_log`), que continua sendo alimentada pela própria preparação.

---

## 0. Notas do revisor adversarial (o que esta versão conserta)

A versão anterior estava conceitualmente sólida mas tinha cinco buracos operacionais. Esta versão os fecha:

1. **A fusão podia CEGAR a curva.** O `/refrescar` carimbava `review_log` (kind `dormant_refresh`) — é isso que alimenta o radar de dormência. Ao virar "sub-modo PREPARAR" acionável também por tema do cronograma (não-dormente), o carimbo deixava de ser garantido. **Correção (§5.3):** carimbar `review_log` vira **invariante obrigatória de TODO PREPARAR** (não opcional), com `kind` discriminado por gatilho. A curva nunca para de ser alimentada.
2. **A escala 1-10 era descritiva, não operável.** **Correção (§7.3):** algoritmo determinístico `infer_nota()` — função de pontos, sinais explícitos, clamp 1-10, falsificável por CLI.
3. **Divergência auto-nota × performance não estava tratada** ("acha fácil mas erra"). **Correção (§4.4):** a nota do usuário governa o **formato da preparação**, mas **nunca** governa o agendamento FSRS (regido por recall real); divergência ≥ 3 é sinalizada e o bloco seguinte recalibra.
4. **Circularidade subdiagnosticada.** **Correção (§7.6):** a inferência só lê sinais **independentes da própria saída** (recall frio do FSRS, blocos de exercício), nunca a profundidade da preparação nem o acerto "morno" pós-preparação.
5. **DoD com critérios subjetivos** ("absurdamente didática", "tom excelente"). **Correção (§9):** DoD reescrito só com proxies mecânicos (contagem de parágrafos em faixa, sigla expandida na 1ª ocorrência, ausência de linha nova em `fsrs_revlog`, retorno numérico de CLI).

**Dependência dura sinalizada:** `tools/cronograma.py` e `core/cronograma/grade.json` **ainda não existem** — hoje `day_plan._cronograma_hint()` raspa o próximo passo de `ESTADO.md` por regex. R4 depende da frente cronograma-sync (s094) entregar essa fonte. **Degradação graciosa (§7.7):** se a grade não existir, a inferência roda sem `prevalencia_enamed` (peso neutro) e o `cronograma_hint` continua vindo do `ESTADO.md`.

---

## 1. Problema & Contexto

### 1.1 A sobreposição que incomoda (`/revisar` ↔ `/refrescar`)

Hoje existem duas skills com fronteiras que, na prática vivida do usuário, **se atropelam**:

- **`/revisar`** (`.claude/commands/revisar.md`): player conversacional de flashcards FSRS. Puxa a fila vencida via `tools/fsrs_queue.py`, apresenta card a card, grava rating 1-4 (`--record`). Tem **Camada 0** (refresh pré-bloco — releitura comprimida/descomprimida conforme estado do tema), **Camada 1** (micro-resumo na virada de card errado) e **Camada 2** (revisão direcionada ao fechar, que volta ao resumo de origem e o edita).
- **`/refrescar`** (`.claude/commands/refrescar.md`): re-ensino narrativo de **tema dormente** (3-6 parágrafos descomprimidos, mecanismo→conduta→armadilha). Seleciona o tema por radar de dormência (`tools/review_radar.py` + `tools/dormant_refresh.py`), carimba `review_log.kind='dormant_refresh'` e **nunca toca o FSRS**.

O incômodo é nomeado pelo usuário: **"revisão = releitura rápida + flashcards; drenar flashcards, no fim, É revisar"**. A Camada 0 do `/revisar` já faz uma releitura calibrada antes de drillar — o mesmo gesto do `/refrescar`, só com gatilho e regra de compressão diferentes. O usuário enxerga **uma competência só** ("preparar o terreno e depois treinar"); o sistema a expõe como duas portas.

### 1.2 A calibração de descompressão hoje é ad-hoc e dicotômica

- **`/refrescar`** opera num ponto fixo: **sempre descomprime** (tema dormente → narrativa densa).
- **`/revisar` Camada 0** calibra por sinal objetivo (`stability` + acerto do cluster), mas **sem escala formal** — binário na prática: *frio → descomprimir / consolidado → comprimir*.
- AGENTE.md §1.2 reconhece o gap: *"Calibração pendente: ajustar o grau de descompressão para os pontos estratégicos que as bancas cobram"*.

A s092 refinou para **calibração por tipo de bloco** (teoria nova → descomprimir; revisão/modo-volume → comprimir); a s090 fixou a **preferência por aula descomprimida** quando o usuário pede a aula. Falta o eixo ortogonal que o usuário pede agora: **o quão difícil o tema é PARA ELE** — um mesmo tipo (revisão) merece compressões diferentes em Hepatites (8) e em MFC Teoria I (3). Sem essa régua, a calibração colapsa num liga-desliga.

### 1.3 Por que agora (s094)

A frente cronograma-sync (`docs/plans/s094-ultraplan.md`) está construindo a **abertura de task** a partir do `day_plan.py`. Esse é o ponto natural para **injetar a nota e calibrar a preparação**. A referência viva de um "10" acabou de nascer: o resumo **"Diabetes — Complicações Crônicas"** (s094), produzido em modo onboarding fundacional.

---

## 2. Visão & Objetivo

**Visão.** A revisão do MedHub é **um gesto só** — preparar o terreno e treinar — cuja profundidade narrativa se ajusta automaticamente ao que *este* estudante precisa *neste* tema *neste* momento. Sem escolher entre duas portas; sem "comprimir ou descomprimir" no escuro.

**Objetivo (s094).** Formalizar o **Contrato de Execução de Revisão Calibrada**:

1. **R1** — Escala de dificuldade-do-tema **1-10** que governa a descompressão, com fontes/precedência, persistência e mapa nota→degrau.
2. **R2** — Aglutinação de `/revisar` + `/refrescar` numa competência única, com dois propósitos de saída (exercícios=amplo / flashcards=direcionado) **sem violar a fronteira dura "refresh narrativo não escreve FSRS" nem cegar a curva de dormência**.
3. **R3** — Fluxo de **abertura de task** que resolve a nota e calibra a preparação, integrado ao boot/`day_plan.py`.
4. **R4** — Integração com o **cronograma (fonte das tasks)** e o **`/performance` (sinal bom × ruim)** que alimenta a inferência automática da nota, **com algoritmo determinístico e tratamento de circularidade**.

**Não-objetivo.** Reescrever o FSRS; gerar aulas-base automaticamente (Tier-3); alterar `insert_questao`. Contrato de *calibração e fusão de competências de revisão*, não de motor de memória.

---

## 3. Conceito Central — `/revisar` calibrado por dificuldade

A competência única **`/revisar`** ganha **um parâmetro de calibração de primeira classe: a nota 1-10**, que modula a descompressão em todos os momentos da preparação:

```
abertura de task ──► nota de dificuldade (1-10)  ──► nível de descompressão
        │              (input > pergunta > inferência)        │
        │                                                     ├─► sub-modo PREPARAR (narrativo; FSRS read-only;
        ▼                                                     │      SEMPRE carimba review_log)
  próximo tema do                                             │      • amplo  (rumo a EXERCÍCIOS)
  cronograma (day_plan)                                       │      • direcionado (rumo a FLASHCARDS)
                                                              │
                                                              └─► sub-modo DRENAR (card-a-card; ESCREVE FSRS)
```

Princípios herdados (não reinventar): **escada de degraus amarrados** (contrato s086, template de descompressão); **mecanismo > fato** (a espinha é a cadeia causal); **fronteira dura** (PREPARAR nunca move stability/due; só `review_log`. DRENAR sempre grava FSRS).

---

## 4. R1 — Escala de Dificuldade do Tema (1-10)

### 4.1 A régua

Mede **dificuldade-para-este-usuário**, não dificuldade intrínseca do tema. Governa **quanto descomprimir**.

- **10 = onboarding fundacional.** Descomprimido, didático ao máximo, do zero. Ancora cada conceito, define sigla por extenso na 1ª aparição, sem salto lógico, mecanismo > fato. **Referência viva: resumo "Diabetes — Complicações Crônicas" (s094).**
- **1 = ultra-comprimido.** Quase nenhuma prosa: só 🔴 gatilhos/armadilhas em flash, discriminação fina. Tema dominado, quente, baixa relevância de banca.
- **Quanto MENOR a nota, MAIS COMPRIMIDA a revisão.** A nota é o eixo contínuo entre os dois polos; o degrau (§4.6) é a saída acionável.

### 4.2 Direção dos modificadores

Reduzem a nota (mais compressão): tema **fácil** (acerto histórico alto, stability alta no cluster); tema **quente** (recém-visto/revisado, dormência baixa); **baixa prevalência ENAMED**.
Elevam a nota (mais descompressão): tema **novo/estreia**; **frio/dormente**; **alta incidência de erro**; **alta prevalência de banca**.

### 4.3 Fontes da nota e precedência

Precedência dura: **input explícito do usuário > pergunta respondida > inferência do agente**. A inferência é a *proposta default*; **nunca silencia** um input do usuário.

- **Input explícito** — soberano. ("esse é um 8")
- **Pergunta do agente** — se a task abre sem nota: "De 1 a 10, quão difícil é Hepatites pra você hoje?"
- **Inferência** — algoritmo determinístico §7.3 (performance histórica + frieza FSRS + último bloco + se já leu + prevalência).

### 4.4 Divergência auto-nota × performance (NOVO — ataque tratado)

O usuário pode "achar fácil mas errar". A nota do usuário é soberana sobre **o formato da preparação** — mas tem **dois limites duros**:

1. **A nota NUNCA governa o agendamento FSRS.** O FSRS é regido por recall real (rating 1-4 em DRENAR). Marcar "3, fácil" não acelera nem adia nenhum card. A nota só decide *quanto texto* o usuário lê antes de drillar. Isso impede que o otimismo do usuário corrompa a curva.
2. **Sinalização de divergência.** Na abertura, o agente computa `nota_inferida` mesmo quando há nota do usuário. Se `|nota_usuario − nota_inferida| ≥ 3`, **sinaliza** sem sobrescrever: *"Você marcou 3, mas seu histórico aqui é 48% e faz 26 dias — confirma o 3 ou subo pra 6?"*. O usuário decide.
3. **Recalibração pós-bloco.** Se a nota foi baixa (preparação comprimida) e o **bloco seguinte** (DRENAR ou exercícios) sai fraco (`acerto_bloco < 60%`), o agente registra o desencontro e, na **próxima** abertura do mesmo tema, propõe nota maior citando a evidência: *"Marcou 3 mas errou 6/10 — vou tratar como 6 desta vez."* A nota do usuário continua persistida como `fonte='usuario'`, mas a proposta de subida é trazida explicitamente (não aplicada à revelia).

### 4.5 Persistência da nota

Estado **de tema**, não de sessão. Em `taxonomia_cronograma` (SSOT de estado-por-tema; colunas atuais confirmadas: `id, area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao`):

- **Coluna `dificuldade INTEGER` (1-10, nullable).**
- **`dificuldade_fonte TEXT`** (`'usuario' | 'agente_inferida'`) — distingue nota soberana de proposta.
- **`dificuldade_at TIMESTAMP`** — recência, para reinferir quando a proposta envelhece.
- **`NULL` = "ainda não calibrado"** → dispara pergunta na abertura (ou inferência em modo autônomo).
- **Local-only** (`ipub.db` não vai pro Cloud; regra dura).
- Escrita via helper `app/utils/db.set_dificuldade(area, tema, nota, fonte)` — `import sqlite3` confinado ao `db.py`. 🔴 **Única exceção autorizada** à regra "só `insert_questao.py` escreve em `taxonomia_cronograma`": `set_dificuldade` toca **apenas** as 3 colunas novas, nunca volume/acertos/perf%.

### 4.6 Mapeamento nota → degrau de registro (degraus acionáveis)

Quatro degraus de formato. Cada um especifica **switches mecânicos** (não adjetivos), auditáveis no DoD. (Bullets, não tabela — contrato de resumo.)

- **Degrau D10 (notas 9-10) — Onboarding do zero.**
  - Parágrafos: **7-9.**
  - **Degrau 0 explícito** (a régua do "normal" enunciada antes da nuance).
  - **Toda sigla definida por extenso na 1ª ocorrência** (auditável).
  - Espinha obrigatória: *mecanismo → por que existe → valores → ajustes → o que acontece se errar → contexto de uso.*
  - Nenhum salto: cada seção abre referenciando a anterior.
  - Molde: resumo "DM Complicações Crônicas" (s094). Equivale ao polo "sempre descomprime" do `/refrescar` atual, agora ancorado em nota.
- **Degrau D8 (notas 7-8) — Descomprimido com mecanismo.**
  - Parágrafos: **5-6.** Degrau 0 explícito. Siglas-chave expandidas.
  - Fundação + cadeia causal + nuance; escada articulada. Tema frio/estreia com alguma base. (≈ Camada 0 "descomprimir" de hoje.)
- **Degrau D5 (notas 4-6) — Gatilhos + armadilhas.**
  - Parágrafos: **3-4.** Degrau 0 **assumido conhecido**.
  - Mecanismo curto + conduta; fecha com gatilhos-de-prova condensados + 🔴 armadilhas. Tema equilibrado. (≈ refresh comprimido s092 — rendeu 86% na S10.)
- **Degrau D2 (notas 1-3) — Só armadilhas / flash.**
  - Parágrafos: **1-2** ou bullets. Sem reconstruir fundação.
  - 🔴 armadilha + diferencial "X vs Y". Tema dominado/quente/baixa-prevalência.

A nota explícita do usuário **escolhe o degrau diretamente**, ignorando os limiares de inferência. Quando não há nota, a faixa sai do `infer_nota()` (§7.3).

### 4.7 Calibração inicial (notas-exemplo — s094, `fonte='usuario'`, soberanas)

Hepatites=**8**; MFC Teoria I=**3**; Doenças Exantemáticas (Revisão)=**6**; Cirurgia Infantil=**8-9** (persistir 8; ver §10 sobre variação intra-tema); Vulvovaginites=**7**; Síndromes Hipertensivas=**6**; Imunizações=**9**; Sepse=**6**.

---

## 5. R2 — Aglutinação `/revisar` + `/refrescar`

### 5.1 A competência única

`/refrescar` deixa de ser skill independente e vira o **sub-modo PREPARAR** dentro de `/revisar`. O usuário invoca **uma coisa**, que abre com a preparação calibrada e flui para a drenagem de cards. A fronteira não desaparece — vira **interna** (dois sub-modos com permissões disjuntas), nunca duas portas.

### 5.2 Os dois propósitos de saída

A preparação prepara a execução de **exercícios** OU de **flashcards**. O propósito modula a **largura** (não a profundidade):

- **Preparar para EXERCÍCIOS → AMPLA.** Cobre o escopo inteiro dos sub-temas do cronograma (o cronograma define o escopo, não o resumo). Mais superfície — a questão pode cair em qualquer canto.
- **Preparar para FLASHCARDS → DIRECIONADA.** Foca nos eixos dos cards vencidos na fila (o cluster que vai cair). Menos superfície, mais profundidade no que será sondado.

**Largura (propósito) e profundidade (nota 1-10) são ortogonais:** nota-8 para exercícios = descomprimido E amplo; nota-3 para flashcards = comprimido E direcionado.

### 5.3 Invariantes de integridade (a barreira que protege a curva)

Após a fusão, **duas** invariantes protegem o motor de memória — não uma. A versão anterior só nomeava a primeira.

**Invariante A — PREPARAR é read-only no FSRS.**
- Writes permitidos em PREPARAR: **`review_log`** (ver Invariante B) e, na Camada 2, edição de `resumos/` (acúmulo, nunca apaga).
- Writes **proibidos**: `record_review`, `insert_questao`, qualquer UPDATE em `fsrs_cards`/`fsrs_revlog`. Mudar stability/retrievability sem avaliação do estudante invalida o FSRS (refrescar.md:47).
- **DRENAR** escreve `fsrs_revlog` (INSERT) + `fsrs_cards` (UPDATE) via `fsrs_queue.py --record`. **Única superfície que move o FSRS.** Regra anti-duplo preservada: uma nota por card por sessão.
- **Barreira:** a transição PREPARAR → DRENAR é o único ponto em que o FSRS passa a ser escrito.

**Invariante B — PREPARAR SEMPRE carimba `review_log` (NOVO — fechando o buraco da curva).**
A curva de dormência por tema é alimentada exclusivamente por `review_log`. No `/refrescar` atual, o carimbo era garantido porque toda invocação vinha do radar de dormência. Ao virar sub-modo acionável **também** por tema do cronograma (não-dormente), o carimbo deixaria de ser garantido — e o radar passaria a achar que o tema "nunca foi revisto", recomendando-o de novo (loop) e distorcendo o score de dormência.
- **Regra:** **todo** PREPARAR, ao concluir, grava uma linha em `review_log` via `db.log_review`, com `kind` discriminado pelo gatilho:
  - tema veio do **radar de dormência** → `kind='dormant_refresh'`;
  - tema veio do **cronograma / fila FSRS / pedido direto** → `kind='directed_review'`.
  - (Ambos os `kind` já existem no schema atual de `review_log`: `{dormant_refresh, directed_review, resumo_read, backfill}`.)
- **Consequência:** o radar (`review_radar.py`) e a leitura unificada (`db.get_theme_last_review`) continuam fiéis qualquer que seja o gatilho da preparação. A curva nunca cega — é a própria preparação que a mantém viva.

### 5.4 Checklist de invariantes (o que NÃO pode se perder na fusão)

- Separação re-ensino ≠ avaliação (agora **sub-modos**, não skills).
- Seleção de tema dormente **por radar** (tempo-sem-rever + retrievability), não card-a-card.
- **Janela anti-repetição de 7 dias** do `dormant_refresh` (rotação de temas) — preservada.
- Descompressão narrativa como re-hidratação (agora **graduada por nota**, não fixa em "sempre descomprime").
- Nucleus em **erros vivos** (`erros_recentes[:10]` + `weak_areas` de `get_topic_context`) — não virar "resumo genérico".
- **Invariante A** (read-only FSRS) **e Invariante B** (carimbo `review_log` obrigatório) — invioláveis.

---

## 6. R3 — Fluxo de Abertura de Task

Ao abrir uma task nova do cronograma:

1. **Boot/`day_plan.py` identifica o próximo tema** da semana corrente e seu **tipo** (teoria nova / revisão / revisão por questões). *(Hoje via `_cronograma_hint()` raspando `ESTADO.md`; quando a grade existir, via `cronograma.py` — §7.7.)*
2. **Resolução da nota:**
   - Usuário **enviou** → usa (`fonte='usuario'`).
   - Senão lê `taxonomia_cronograma.dificuldade`: preenchida e `fonte='usuario'` → usa; `NULL` ou `agente_inferida` antiga → **infere** (§7.3) e, conforme autonomia (AGENTE §1.1), **propõe decisivamente** ("Vou tratar Hepatites como 8 — corrija-me") em vez de menu. Pausa só em fork real.
   - **Computa `nota_inferida` mesmo quando há nota do usuário** → checa divergência (§4.4).
3. **Calibra a preparação** ao degrau (§4.6) **e** ao propósito (§5.2: exercícios=amplo / flashcards=direcionado), conferindo o escopo no `Cronograma.pdf` antes do bloco (contrato de execução, s092/s094).
4. **Persiste** a nota usada (`fonte`/`at`) para a próxima abertura já vir calibrada.
5. **Conclui PREPARAR carimbando `review_log`** (Invariante B) e **flui para DRENAR** — ponto onde o FSRS volta a ser escrito.

Integração: este é o passo 4 do `day_plan.py` na frente cronograma-sync. O `day_plan.py` já importa `dormant_refresh` e `performance`; estender com leitura de `dificuldade` e `infer_nota()` é encaixe natural.

---

## 7. R4 — Integração Cronograma + `/performance` (CRÍTICA)

Fecha o loop entre o estado real do estudante e o grau de descompressão. Sem ela, a nota inferida fica cega ao desempenho e ao foco da semana.

### 7.1 O cronograma é a FONTE das tasks/temas

- `Cronograma.pdf`/`core/cronograma/grade.json` (SSOT, **a criar** na frente s094) → `tools/cronograma.py` emite `(semana, tema, tipo_bloco, prevalencia_enamed, nº questões)`.
- `tools/day_plan.py` lê o próximo tema da semana e resolve em `taxonomia_cronograma` por `(area, tema)`.
- O cronograma define o **escopo** do bloco (sub-temas EXATOS, conferidos no PDF antes); o resumo é a fonte de conhecimento; **a nota calibra a profundidade**.
- Acoplamento por **DATA**, não por task-id — flexível ao ritmo real (S10 executada a 54%).

### 7.2 O `/performance` ALIMENTA a inferência

`tools/performance.py` (read-only sobre `sessoes_bulk`) já reporta áreas bom × ruim (`get_por_area` → perf por área; bloco de áreas fracas). Hoje **não cruza com o cronograma** — gap que R4 fecha. Regra central:

- **Área/tema fraco no `/performance` ⇒ nota MAIOR ⇒ revisão mais DESCOMPRIMIDA.**
- Área/tema forte e quente ⇒ nota menor ⇒ revisão mais comprimida.

A performance deixa de ser só relatório e vira **sinal de calibração**.

### 7.3 Algoritmo determinístico da nota inferida (NOVO — operacionalização)

`infer_nota()` é uma função de pontos sobre sinais já disponíveis, projetada e **clampada** em 1-10. Vive ao lado de `day_plan.build()` (read-only). Pseudocódigo normativo:

```
def infer_nota(sinais):
    # ── sinais (todos independentes da própria saída; ver §7.6) ──────────────
    acerto_hist  = taxonomia.percentual_acertos            # None se 0 questões
    acerto_bloco = ultimo_bloco(sessoes_bulk, area, tema)  # None se inexistente
    score_dorm   = review_radar.score(tema)        # dias + (1-R)*30 + vencidos*2
    leu_tema     = bool(review_log OR ultima_revisao OR resumo_existe)
    prevalencia  = grade.prevalencia_enamed or 'media'     # alta|media|baixa

    # ── eixo 1: dificuldade-de-conteúdo (performance) define a BASE ───────────
    if   acerto_hist is None and not leu_tema:  base = 9   # estreia pura → onboarding
    elif acerto_hist is None:                   base = 6   # leu, sem volume registrado
    elif acerto_hist < 50:                      base = 8
    elif acerto_hist < 65:                      base = 7
    elif acerto_hist < 80:                      base = 5
    else:                                       base = 3   # >= 80%

    # ── eixo 2: frieza (dormência) empurra p/ cima; quente puxa p/ baixo ──────
    if   score_dorm >= 40:  base += 2
    elif score_dorm >= 25:  base += 1
    elif score_dorm < 7:    base -= 1          # tema quente/fresco

    # ── eixo 3: último bloco fraco confirma dificuldade VIVA (override) ───────
    if acerto_bloco is not None and acerto_bloco < 60:  base += 1

    # ── eixo 4: prevalência ENAMED = piso de banca, não teto ─────────────────
    if prevalencia == 'baixa':  base -= 1
    nota = clamp(base, 1, 10)
    if prevalencia == 'alta':   nota = max(nota, 4)   # banca cobra → nunca < 4
    return nota
```

Propriedades verificáveis (entram no DoD):
- `acerto_hist < 50%` ⇒ base 8 ⇒ `nota ≥ 7`. ✔ (DoD-5)
- `acerto_hist ≥ 80%` **e** quente (`score_dorm < 7`) **e** `prevalencia='baixa'` ⇒ 3−1−1 = 1 ⇒ `nota ≤ 3` (piso de banca não dispara). ✔ (DoD-5)
- estreia pura ⇒ base 9 ⇒ degrau D10 (onboarding).

### 7.4 Como o day_plan/boot consome

```
python tools/day_plan.py --difficulty "Clínica Médica" "Hepatites Virais"
→ {
   "cronograma_hint": "Hepatites Virais (Revisão, semana 10)",
   "nota_usuario":  null,
   "nota_inferida": 8,            # infer_nota(): acerto 48% + dormida 26d
   "divergencia":   null,
   "proposito": "flashcards",     # fila vencida grande → DIRECIONADA
   "degrau": "D8",
   "sugestao_passo": "Revisar Hepatites como dif-8 (D8), PREPARAR descomprimido+mecanismo, direcionado aos cards vencidos"
}
```

### 7.5 Frescor da nota

Se `dificuldade IS NULL` **ou** (`dificuldade_fonte='agente_inferida'` **e** `dificuldade_at` antigo > N dias) → recalcular `infer_nota()` antes de abrir. Nota `fonte='usuario'` é soberana: não recalcula a aplicada, mas **computa** a inferida para checar divergência (§4.4).

### 7.6 Anti-circularidade (NOVO — ataque tratado)

O loop *nota alta → mais descompressão → melhora performance → nota cai → menos descompressão* é o **desejado** (curva de aprendizado fechando). Os riscos reais são **circularidade de sinal** e **chattering**. Mitigações duras:

- **A inferência NUNCA lê a própria saída.** `infer_nota()` é proibida de usar como sinal: (a) a profundidade da preparação que ela própria gerou; (b) o **acerto "morno"** medido logo após PREPARAR (o aquecimento infla o recall e baixaria a nota falsamente). Só lê **sinais frios e independentes**: `percentual_acertos` histórico, `acerto_bloco` de blocos de **exercício/DRENAR** (não da leitura imediata), `score_dorm` do FSRS, `prevalencia`.
- **Histerese assimétrica.** A nota inferida só **DESCE** após ≥ 2 sinais frios consistentes (ex.: 2 blocos ≥ 80% **e** stability subindo). **SOBE** com 1 sinal forte. Errar para mais (descomprimir além do necessário) é mais barato que errar para menos.
- **Piso por prevalência ENAMED.** Tema de alta prevalência não desce de 4, mesmo dominado (já embutido em `infer_nota()`).
- **Soberania trava o loop.** Nota `fonte='usuario'` congela a inferência aplicada até o usuário liberar.

### 7.7 Degradação graciosa (dependência cronograma-sync ainda não pronta)

`cronograma.py`/`grade.json` **não existem hoje** (`day_plan._cronograma_hint()` raspa `ESTADO.md`). Enquanto não existem:
- `prevalencia_enamed` = `'media'` (peso neutro; eixo 4 não atua, sem piso de banca).
- `cronograma_hint` continua de `ESTADO.md`.
- `infer_nota()` roda com 3 eixos (performance + frieza + último bloco) — degradação suave, não falha.
Quando a grade chegar, basta `cronograma.py` passar a fornecer `prevalencia_enamed`; nenhuma mudança em `infer_nota()`.

---

## 8. Integração com o Sistema

### 8.1 Skills a fundir/versionar

- **`.claude/commands/revisar.md`** — vira o contrato da competência única. Adiciona: parâmetro `dificuldade`, sub-modos PREPARAR/DRENAR, dois propósitos, mapa nota→degrau, **Invariante B (carimbo `review_log` obrigatório)**. Camadas 0/1/2 reenquadradas dentro de PREPARAR/DRENAR.
- **`.claude/commands/refrescar.md`** — **deprecado como skill autônoma**; conteúdo (re-ensino dormente + barreiras) migra para o sub-modo PREPARAR. Stub de redirecionamento por compatibilidade **ou** arquivo em `history/legacy/`.

### 8.2 CLIs afetados (sem reescrever lógica)

- **`tools/fsrs_queue.py`** — núcleo inalterado (`--next/--list/--record`); motor do DRENAR. Possível flag `--difficulty <area> <tema>` para puxar a nota junto da fila.
- **`tools/dormant_refresh.py`** — `--stamp`/`--context` servem o PREPARAR; o `--stamp` passa a ser chamado por **todo** PREPARAR (Invariante B), com `kind` parametrizável (`dormant_refresh` | `directed_review`).
- **`tools/review_radar.py`** — continua selecionando tema dormente; passa a **alimentar `infer_nota()`** (score → eixo 2).
- **`tools/performance.py`** — `get_por_area` vira sinal de inferência (eixo 1/3); read-only inalterado.
- **`app/utils/db.py`** — novos `set_dificuldade()/get_dificuldade()` + migração de schema (3 colunas em `taxonomia_cronograma`). Já é o lar de `log_review`/`get_theme_last_review`. Único lugar com `import sqlite3` na app.
- **`tools/day_plan.py`** — passa a emitir `nota_usuario`/`nota_inferida`/`divergencia`/`proposito`/`degrau`; hospeda `infer_nota()`. Flag `--difficulty <area> <tema>`.
- **`tools/cronograma.py`** (a criar, frente s094) — emite próximo tema + tipo + `prevalencia_enamed`.

### 8.3 Contratos a criar/editar

- **CRIAR `core/contracts/revisao-calibrada-contract.md`** (este PRD vira o contrato lateral). Normativo: escala 1-10, mapa nota→degrau, fontes/precedência, **regra de divergência (§4.4)**, fusão em sub-modos, **Invariantes A e B**, `infer_nota()` (§7.3), anti-circularidade (§7.6), degradação graciosa (§7.7). Frontmatter `type: contract / layer: core / status: pending-ratification`.
- **RELAÇÃO com `forgetting-curve-contract.md`** — este contrato **consome** o score de dormência e a retrievability de lá (não redefine). A inferência é uma *projeção* desse score + stability na faixa 1-10. **Invariante A** ("refresh não escreve FSRS") **e a alimentação de `review_log`** são herdadas e **reforçadas** pela Invariante B.
- **RELAÇÃO com `cronograma-contract.md`** (a criar, frente s094) — o cronograma é a FONTE; este contrato consome `(tema, tipo, prevalencia_enamed)`.
- **EDITAR `AGENTE.md §1.2`** — substituir *"Calibração pendente"* por ponteiro ao novo contrato e ao mapa de degraus.
- **Reusar** o template de `core/contracts/` (padrão `reconcile`/`fsrs-management`).

---

## 9. Definition of Done (binário / falsificável)

Todos os critérios abaixo são verificáveis por comando ou grep — **sem juízo subjetivo**.

1. **DoD-1 (schema).** `PRAGMA table_info(taxonomia_cronograma)` lista `dificuldade`, `dificuldade_fonte`, `dificuldade_at`; e `app/utils/db.py` expõe `set_dificuldade()/get_dificuldade()`. Verificação: uma chamada CLI grava `(área, tema, 7, 'usuario')` e a releitura retorna `7/'usuario'`.
2. **DoD-2 (seed).** As 8 notas-exemplo (§4.7) estão persistidas com `fonte='usuario'`; leitura confirma os valores exatos (Hepatites=8, MFC TeoriaI=3, Imunizações=9, …).
3. **DoD-3 (contrato).** Existe `core/contracts/revisao-calibrada-contract.md` com frontmatter de contrato, contendo (grep): os **4 degraus** (D10/D8/D5/D2) com suas faixas de parágrafos, **Invariante A e Invariante B nomeadas**, e o pseudocódigo de `infer_nota()`.
4. **DoD-4 (skill).** `.claude/commands/revisar.md` documenta sub-modos PREPARAR/DRENAR e declara textualmente que **PREPARAR não emite `record_review` nem UPDATE em `fsrs_cards`** e que **PREPARAR sempre carimba `review_log`**; `/refrescar` está deprecado/redirecionado (stub ou `history/legacy/`).
5. **DoD-5 (inferência numérica).** `python tools/day_plan.py --difficulty <area> <tema>` retorna JSON com `nota_inferida` inteiro 1-10. Assertion: tema com `percentual_acertos < 50%` ⇒ `nota_inferida ≥ 7`; tema com `percentual_acertos ≥ 80%`, `score_dorm < 7` e prevalência não-alta ⇒ `nota_inferida ≤ 3`. (Falsificável: roda `infer_nota()` com fixtures.)
6. **DoD-6 (divergência).** Com nota do usuário = 3 e `nota_inferida = 6`, o JSON do `day_plan --difficulty` traz `divergencia` não-nulo (campo com os dois valores); com `|Δ| < 3`, `divergencia = null`.
7. **DoD-7 (degrau mecânico).** Num PREPARAR de teste com nota 9, o registro tem **7-9 parágrafos** e **toda sigla aparece expandida na 1ª ocorrência** (auditável por contagem + regex de sigla); com nota 2, tem **≤ 2 parágrafos** e nenhuma reconstrução de fundação. *(Proxies mecânicos — sem "didático"/"excelente".)*
8. **DoD-8 (barreira A auditável).** Existe asserção/teste que **falha** se o caminho PREPARAR chamar `record_review`; e, numa sessão de teste, **`SELECT COUNT(*) FROM fsrs_revlog` não muda** entre o início e o fim de PREPARAR (só muda após iniciar DRENAR).
9. **DoD-9 (curva alimentada — barreira B auditável).** Após um PREPARAR de teste, existe **exatamente 1 linha nova** em `review_log` para o tema, com `kind ∈ {dormant_refresh, directed_review}` conforme o gatilho. *(Sem esta, a fusão teria cegado o radar.)*
10. **DoD-10 (AGENTE).** `AGENTE.md §1.2` não contém mais a string "Calibração pendente" e aponta para `core/contracts/revisao-calibrada-contract.md`.

---

## 10. Riscos, Trade-offs e Questões Abertas

**Riscos**
- **Erosão da barreira FSRS na fusão.** Maior risco. Mitigação: Invariante A + asserção (DoD-8) + barreira textual no contrato.
- **Curva de dormência cega pós-fusão** (PREPARAR não-dormente sem carimbo). Mitigação: **Invariante B** + DoD-9.
- **Nota inferida estagnada.** Mitigação: `dificuldade_at` + reinferir quando velha (§7.5).
- **Sobrescrever input do usuário.** Mitigação: precedência dura (§4.3) + `fonte`.
- **Circularidade de sinal / chattering.** Mitigação: a inferência só lê sinais frios independentes (§7.6) + histerese assimétrica.
- **`taxonomia_cronograma` como write-target.** Mitigação: `set_dificuldade` toca só 3 colunas; write isolado e auditável.
- **Subjetividade da nota.** Aceito: a nota é um *prior* calibrável, não verdade; o feedback frio pós-bloco a corrige (§4.4).

**Trade-offs**
- **Escala contínua vs simplicidade.** Quatro degraus de saída (não dez prosas distintas) — escolhido por operabilidade; a nota 1-10 é a entrada, o degrau é a saída acionável.
- **Persistir no `ipub.db` (local-only) vs Cloud.** Local: coerente com a arquitetura de estado.
- **Deprecar `/refrescar` vs duas portas.** Deprecar resolve o incômodo, ao custo de migração e muscle-memory.

**Questões abertas (decisão do usuário)**
1. **Nota por tema, ou por (tema × tipo de bloco)?** Cirurgia Infantil = 8-9 sugere variação intra-tema (apendicite vs Meckel). Proposta inicial: **por tema**, com o tipo modulando **largura**, não a nota. Confirmar?
2. **`dificuldade_at` "antigo" = quantos dias** para reinferir uma nota `agente_inferida`? Proposta-semente: 7 dias.
3. **Histerese — "2 sinais consistentes" exatos** para baixar a nota: calibrar com o histórico real (quais 2? blocos ≥80% + stability↑?).
4. **Prevalência ENAMED:** fonte estruturada (`grade.json` com peso por área) ou julgamento do agente até a grade existir? (Hoje: peso neutro — §7.7.)
5. **PREPARAR pode encerrar como pura preparação** (equivalente ao `/refrescar` standalone), ou sempre oferece DRENAR em seguida?
6. **Conflito dormência alta (descomprimir) × nota baixa do usuário (comprimir):** input do usuário vence, mas o agente sinaliza (já em §4.4)? Confirmar que a soberania prevalece mesmo com tema 30d dormido.

---

*Fim do PRD — s094 Revisão Calibrada (revisão adversarial). Próximo passo: ratificar e materializar `core/contracts/revisao-calibrada-contract.md`.*
