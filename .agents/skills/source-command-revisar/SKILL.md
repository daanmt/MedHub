---
name: "source-command-revisar"
description: "Conduz uma sessão conversacional de revisão de flashcards FSRS — puxa a fila vencida via tools/fsrs_queue.py, apresenta card a card e grava a avaliação 1-4. Funciona via remote-control (celular)."
---

# source-command-revisar

Use this skill when the user asks to run the migrated source command `revisar`.

## Command Template

# Skill: Revisar

O agente vira o **player de flashcards**. Conduz a revisão por repetição espaçada dentro da conversa, sem depender do Streamlit local — o que permite revisar via remote-control (celular). A leitura da fila e a gravação dos ratings passam pelo CLI `tools/fsrs_queue.py`, que é uma camada fina sobre `app/utils/db.py` (`get_cards_by_bucket` + `record_review`).

Use quando o usuário pedir qualquer variação de: "revisar", "vamos revisar flashcards", "tenho cards pra hoje?", "quero estudar os cards de Cardiologia".

---

## Revisão Calibrada — sub-modos PREPARAR / DRENAR (s096)

> `/revisar` é a **competência única** de revisão — absorveu `/refrescar`. Norma: [`core/contracts/revisao-calibrada-contract.md`](../../core/contracts/revisao-calibrada-contract.md). Dois sub-modos com permissões **disjuntas**:

- **PREPARAR** (narrativo; **FSRS read-only**) — re-ensino calibrado do tema **antes** de drillar. Absorve o antigo `/refrescar` e a Camada 0. Profundidade calibrada pela **nota de dificuldade 1-10** (degrau D10/D8/D5/D2, Cláusula 3 do contrato); largura pelo **propósito** (amplo → exercícios / direcionado → flashcards). Largura e profundidade são ortogonais.
  - 🔴 **Arquitetura por propósito (Cláusula 4 do contrato).** O propósito muda a **arquitetura**, não só a largura. **Antes de QUESTÕES** (amplo → exercícios): **os degraus são fundamentais** — cobrir o **escopo-árvore inteiro** (doses, diferenciais, árvore de decisão) e **DESTRINCHAR o mecanismo** dos exames/conceitos discriminadores (não só nomear), mesmo em nota média (D5). **Antes de FLASHCARDS** (direcionado): **refresh curto** + contexto dos problemas dos cards. Nomear "whiff+/clue cells/KOH" sem abrir o que são = profundidade D2 disfarçada; a cobertura do ponto de decisão inclui **abrir o mecanismo** (Invariante E / Cláusula 10).
  - 🔴 **Invariante A:** PREPARAR **NUNCA** emite `record_review` nem `UPDATE` em `fsrs_cards`/`fsrs_revlog` — nenhum write de FSRS.
  - 🔴 **Invariante B:** PREPARAR **SEMPRE** carimba `review_log` ao concluir — `python tools/dormant_refresh.py --stamp --tema-id <id> --kind <dormant_refresh|directed_review>` (dormência → `dormant_refresh`; cronograma/fila/pedido → `directed_review`). A curva nunca cega.
  - 🔴 **Invariante D (isolamento, F8):** o refresh aquece **conceitos e mecanismos**, nunca o par pergunta-resposta dos cards do bloco — montado a partir do resumo **sem abrir os versos**; regras como **tendência** ("geralmente X; considerar Y se Z"), nunca absoluto. **Classe de card:** raciocínio/conduta → aquecer o framework é legítimo (a nota pós-refresh mede "pegou o framework" — sinalizar); **fato puro** (definição/eponímia/dado seco) → refresh **contraindicado**: só orientação de entorno, o fato cobrado é retido para o recall.
- **DRENAR** (card-a-card; **ESCREVE FSRS**) — o player FSRS descrito abaixo. Única superfície que move o FSRS. A transição **PREPARAR → DRENAR** é o único ponto em que o FSRS passa a ser escrito.
  - 🔴 **Invariante C (override-antes-do-record, F9):** o rating só é gravado **após a janela de override** (nota proposta → confirmação/correção do usuário → gravação única). Nunca `--record` antes da janela; nunca re-record depois dela.

### Resolver a nota na abertura de task

`python tools/day_plan.py --difficulty "<area>" "<tema>"` → JSON com `nota_usuario`, `nota_inferida`, `nota_efetiva`, `degrau`, `paragrafos`, `divergencia`, `proposito`. Precedência **dura**: input do usuário > pergunta > inferência (`infer_nota`). Se `divergencia` ≠ null (|Δ| ≥ 3), **sinalizar sem sobrescrever** ("marcou 3, mas histórico 48%/26d — confirma o 3 ou subo pra 6?"). Persistir a nota usada via `db.set_dificuldade` (`fonte='usuario'` é soberana). 🔴 **A nota calibra SÓ a profundidade da PREPARAÇÃO — nunca o agendamento FSRS** (regido por recall real em DRENAR).

🔴 **Cobertura é piso fixo, não elástico (Cláusula 10 / Invariante E do contrato).** A nota calibra a **profundidade/prosa**; o **conjunto de pontos de decisão de alto rendimento** do tema é **piso fixo por tema**, derivado do **sumário da fonte** (índice do resumo / escopo do cronograma). Mesmo em **D2** (flash), passar pelo **checklist de cobertura** antes de fechar: comprimir a prosa de um ponto é legítimo; **eliminar** o ponto não é — **compressão encurta, nunca corta** (raiz do F21: ponto de decisão apagado pela descompressão).

> As **Camadas 0/1/2** abaixo permanecem válidas, reenquadradas: **Camada 0** = PREPARAR (agora graduada por nota, não fixa em "sempre descomprime"); **Camadas 1/2** = dentro de DRENAR (micro-resumo na virada + Revisão Direcionada de fechamento).

---

## Invocação do CLI

```bash
# Próximo card vencido (objeto JSON) — opcionalmente filtrado
python tools/fsrs_queue.py --next [--area "Cardiologia"] [--tema "Insufic"]

# Lote da fila (array JSON) — para ver o tamanho/escopo da sessão
python tools/fsrs_queue.py --list [--area X] [--tema Y] [--limit N] [--new-limit M]

# Gravar a avaliação de um card (1=Novamente 2=Difícil 3=Bom 4=Fácil)
python tools/fsrs_queue.py --record <card_id> --rating <1-4>
```

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

**Ordem da fila:** atrasados → hoje → novos. Cards aposentados (`needs_qualitative >= 2`) são excluídos pela query. Campos de cada card: `card_id, frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha, needs_qualitative, due, area, tema, bucket`.

---

## Protocolo do loop conversacional

1. **Abrir a sessão.** Rodar `--list` (com os filtros que o usuário pediu, se houver) para saber quantos cards há e anunciar o tamanho da sessão ("você tem 12 cards: 8 atrasados, 2 de hoje, 2 novos"). Para conduzir por tema, usar `--cluster` (mantém buckets, agrupa temas) e/ou `day_plan.py --review-plan` (clusters com contagem + sinal de frieza derivados).
   - **PREPARAR proativo (F5):** ao abrir um cluster com sinal **frio** (`frieza >= 25` no `--review-plan`, ou stability/histórico equivalente), **oferecer** o PREPARAR antes de sondar ("cluster X está frio — aqueço antes?") sem esperar pedido. Oferta ≠ execução: o usuário decide, e pode recusar de uma vez para a sessão ("hoje sem PREPARAR"). A fronteira dura permanece: PREPARAR não toca FSRS (Invariantes A/D).
2. **Apresentar a FRENTE.** Para o card atual, mostrar `frente_contexto` (se houver) como contexto e `frente_pergunta` como a pergunta. **Não revelar o verso ainda.** Convidar o usuário a tentar responder.
3. **Revelar o VERSO sob pedido.** Quando o usuário responder ou pedir ("mostra", "não sei", "revela"), mostrar `verso_resposta`, depois `verso_regra_mestre` (a regra de ouro) e, se preenchida, `verso_armadilha` (o distrator/pegadinha).
4. **Propor a nota e abrir a janela de override (contrato, Invariante C).** O agente **propõe a nota 1-4 com base na resposta do usuário** (não pede o número). Critério: cravou conceito + regra-mestre → 4; acertou o núcleo, faltou detalhe → 3; recall parcial/na zona mas sem o alvo → 2; errou ou "não sei" → 1. **Informar a nota proposta** ("→ 3") e a justificativa em 1 linha, e **aguardar a resposta do usuário**: confirmação, correção ("não, foi 2") ou simples avanço valem como fechamento da janela. **Nada é gravado neste passo.** Ratings honestos > generosos — a precisão do FSRS depende disso.
5. **Gravar — só após a janela.** Fechada a janela do passo 4, rodar `--record <card_id> --rating <n>` com a nota final — **uma única vez por card**. Confirmar com o próximo `due` retornado ("próxima revisão em N dias"). Correção que chegar **depois** do record não gera re-record (Invariante C): registrar o ocorrido no fechamento (`history/session_NNN.md`) e seguir.
6. **Avançar.** Buscar o próximo card (novo `--next`, ou o próximo item do lote já obtido no passo 1). Repetir 2-5.
7. **Fechar com Revisão Direcionada.** Quando a fila esvaziar (`{"empty": true}`) ou o usuário parar: (a) resumo de sessão — cards revisados + distribuição de ratings; (b) rodar a **Revisão Direcionada de fechamento** (ver seção abaixo) — voltar aos resumos dos temas onde houve gap e **reabordar a matéria**, não só re-drillar o card; (c) **Registrar a nota da aula (F18c).** Se a sessão fez PREPARAR/aula calibrada, gravar no fechamento a nota 1-10 que calibrou a descompressão via `db.set_dificuldade(area, tema, nota, fonte='aula')` — o sinal caro da forja deixa de ser efêmero. **Não sobrescrever** uma nota soberana `fonte='usuario'` (Cláusula 2/10 do contrato): registrar só quando a nota da aula não colide com input explícito do usuário.

### Camada 0 — Refresh pré-bloco e compressão calibrada (sessão 082)

> **Princípio: esquentar antes de sondar.** Medir recall a frio num tema gelado (pós-pausa, ou cards de estreia) só produz notas 1 e nenhuma reativação. Antes de drillar um bloco de tema frio, **refrescar a fundação** — uma leitura curta e dirigida pelos conceitos que os cards vão sondar, ancorada no resumo. Casa leitura + cards (e/ou questões); não a sonda crua primeiro. Feedback do usuário (s082): *"refrescar a memória com um resuminho gravitando em torno da sessão, antes de realizar os cards"*.

1. **Calibrar a compressão ao estado do tema.** A dose do refresh escala com o quão frio está o tema — sinal objetivo: **stability média + taxa de acerto do cluster**. Tema frio → **descomprimir** (conceitos primitivos, do chão). Tema consolidado → **comprimir** (só a discriminação fina). Não entregar fundação a quem já domina (vira ruído); não drillar o topo de quem não tem chão (o card vira leech).
2. **A nota pós-refresh mede "pegou no aquecimento", não recall a frio.** Sinalizar isso ao usuário; para estreia/tema frio é o correto — o FSRS calibra o recall real conforme os cards reaparecem nos dias seguintes.
3. **Gatilho de andaime.** Se o bloco expõe um **cluster** caindo no mesmo eixo (não um card isolado), a fundação está ausente → cunhar **cards de andaime** (`base`/`mecanismo`/…) via `tools/insert_card_base.py`, costurando o degrau imediatamente adjacente ao buraco (**propagação local**). O degrau `mecanismo` (porquê causal encadeado) rende mais — o gap costuma ser causalidade, não fato. Régua: [`estilo-flashcard.md`](estilo-flashcard.md) §Altura graduada.

### Modo conversacional padrão (contrato core — sessão 075)

Comportamentos default desta skill, ajustáveis pelo usuário a qualquer momento:

- **Renderização em lote.** Apresentar **N frentes de uma vez** (default ajustável durante a sessão — o usuário pediu 3, depois 5). O usuário responde todas; o agente revela + **propõe as notas do lote inteiro** e abre **uma janela de override única do lote** (Invariante C); confirmadas/corrigidas, grava o lote de uma vez. Sem lote explícito, usar 1 por vez.
- **Avaliação automática pelo agente** (passo 4 acima): o agente propõe a nota, não o usuário — e grava só após a janela.
- **Papel de scrum master ativo:** ao detectar **erro repetido** (mesmo conceito errado em cards diferentes), parar e sinalizar explicitamente — não deixar passar (regra "não errar duas vezes pelo mesmo motivo"). Conectar o card ao erro de origem em `questoes_erros` quando útil.
- **Camada 1 — Expansão de contexto na virada (micro-resumo *just-in-time*; feedback s076).** Quando a nota for **1 ou 2**, logo após virar o card apresentar uma **expansão curta (~2-4 linhas) do conceito errado** — não só o gabarito, mas o contexto que o cerca (a regra-mestre + por que o distrator engana + a fronteira com conceitos vizinhos), ancorada no resumo de origem em `resumos/` (via RAG `mcp__obsidian-notes-rag__search_notes` quando útil). Objetivo: fechar a lacuna **enquanto está quente**. Em acerto sólido (4) não interromper; num 3 frágil, uma linha de fronteira basta. Esta é a versão **por-card**; a consolidação **por-tema** vem na Camada 2 (Revisão Direcionada de fechamento).
- **Flip obrigatório do card (feedback do usuário, sessão 077).** Após a tentativa, **sempre virar o card** — revelar `verso_resposta` + `verso_regra_mestre` (+ `verso_armadilha`) de **todo** card, mesmo nos acertos (3-4). Ver a formulação exata da resposta consolida a memória; nunca pular o verso "porque acertou".
- **Relearning intra-sessão (estilo Anki — feedback do usuário, sessão 077).** Todo card avaliado **< 4** (1, 2 ou 3) entra numa **fila de re-drill da própria sessão** e é **re-apresentado** (frente) antes de fechar, em 1-2 repetições, até o usuário acertar com fluência. **Esse re-drill é consolidação, NÃO grava no FSRS** — a nota do FSRS é **uma só por card por sessão** (a 1ª tentativa honesta), respeitando a regra anti-duplo-registro. O re-drill é puramente mnemônico (repetição espaçada curta dentro da sessão). Priorizar 1 e 2 sobre 3 quando a fila estiver grande. Fechar quando a fila de re-drill esvaziar ou o usuário parar.
- **Honestidade sobre generosidade:** preferir a nota que reflete o recall real, mesmo que baixa.

### Fechamento: Revisão Direcionada (Camada 2 — contrato, sessão 078)

> **Princípio: o card é a sonda, o resumo é a fonte.** Reforçar a sonda (re-drillar o card) sem reabordar a fonte (a matéria do resumo) é dispendioso e infrutífero — o card vira *leech* e ressurge eternamente. Quando um gap não está consolidado (ou só parcialmente), a correção é **reabordar a matéria**, não repetir a pergunta. Feedback do usuário (s078): *"ficarei voltando eternamente nos cards se a matéria que trata do desafio do card não for reabordada"*.

Ao fechar a sessão, **antes** de encerrar, rodar a Revisão Direcionada sobre os gaps acumulados:

1. **Clusterizar os gaps por TEMA/conceito, não por card.** Agrupar todo card avaliado `< 4` e todo erro repetido pelo **elo metacognitivo / tema de origem** (ver [[feedback-flashcard-metacognitivo]]). Ex.: "Febre Amarela — números (incubação 3-6 × viremia <7)"; "PTI — gatilho de tratamento (púrpura úmida × valor de plaqueta)".
2. **Para cada gap-tema, voltar ao resumo de origem** em `resumos/` — localizar via RAG `mcp__obsidian-notes-rag__search_notes` (não ler arquivo inteiro à toa). Diagnosticar o resumo **contra o gap**:
   - **Resumo cobre o ponto com clareza** → gap é puro recall/decoreba → entregar **re-ensino direcionado condensado** (o "resumo direcionado ao final"): denso, ancorado no resumo, focado na **discriminação exata** que falhou. Sem editar o resumo.
   - **Resumo é raso/omisso no ponto** → a **matéria é deficiente** → **expandir o resumo**: adicionar a discriminação/armadilha que faltou, seguindo `/estilo-resumo` + **Regra de Acúmulo** (armadilhas cumulativas, nunca sobrescrever) + Siamese Twins (`AGENTE.md §6`). É o passo que faz o card **parar de ser leech**.
   - **Resumo está inchado em torno do ponto** → **comprimir**: tighten o sinal para o ponto ficar localizável. Nunca deletar armadilhas (Regra de Acúmulo) — comprimir é reorganizar/condensar, não apagar conteúdo de prova.
3. **Entregar** a Revisão Direcionada no chat (o re-ensino condensado) + aplicar as edições de resumo que o diagnóstico exigir. Editar `resumos/` é mudança de SSOT clínico: seguir `/estilo-resumo`, preservar armadilhas. Adicionar armadilha/discriminação (cumulativo) é in-bounds; reestruturação grande ou compressão substantiva → confirmar escopo com o usuário antes.
4. **Calibrar a intensidade (papel de scrum master).** Gap pontual (1 card decoreba, resumo já cobre) → 2-3 linhas de re-ensino. Cluster reincidente (mesmo tema falhando em vários cards / em sessões anteriores) → re-ensino mais denso + provável edição do resumo. As duas camadas — expansão na virada (1) e Revisão Direcionada de fechamento (2) — são complementares; o scrum master escolhe a dose. Registrar os temas reabordados no `history/session_NNN.md` de fechamento.

---

## Regra anti-duplo-registro (reconciliada com o override — F9)

O CLI é **stateless** — cada `--record` grava uma linha em `fsrs_revlog`. A deduplicação é responsabilidade do agente: **mantenha o conjunto de `card_id` já avaliados nesta conversa** e nunca chame `--record` duas vezes para o mesmo card na mesma sessão. (Espelha a regra `reviewed_ids` do player Streamlit, mas no nível do agente.)

**Sem contradição com o "usuário pode sobrepor":** o override intencional acontece **dentro da janela do passo 4, ANTES do record** (Invariante C do contrato). Depois do record não há amend — re-gravar recalcula o FSRS sobre estado já mutado e deixa 2 linhas de revlog (caso card 403, s108). Correção tardia vira nota de fechamento em `history/`, nunca segundo `--record`.

---

## Notas

- **Não há sessão Streamlit.** Esta skill é a interface primária de revisão na pivotagem agent-first (ROADMAP Linha 8). O player em `app/pages/2_estudo.py` permanece como opção desktop, intocado.
- **`ipub.db` é local-only.** O CLI roda na máquina onde o banco vive; via remote-control, o comando é executado nessa máquina e o resultado volta para a conversa.
- **Avaliação honesta.** Incentivar o usuário a tentar responder antes de revelar o verso — a precisão do FSRS depende de ratings honestos.
- O FSRS subjacente é o de `app/utils/fsrs.py` (substituição pela referência é a part-2 da Onda A; esta skill não muda quando o FSRS for trocado, pois grava via `record_review()`).
