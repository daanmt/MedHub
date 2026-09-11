---
type: contract
layer: core
status: canonical
version: 1.2
relates_to: [reconcile-contract, estado-contract, AGENTE]
---

# Contrato de Gerenciamento do FSRS
**Versão 1.2 | 2026-09-10 (s176, item 0.7 -- promotes F71 e F80) · v1.1 2026-07-05 (s108+, F3/F4 do ledger AUDITORIA_MEDHUB) · v1.0 2026-06-03 (sessão 075)**

> Documento normativo. Define como a fila de repetição espaçada é gerenciada, drenada e mantida.
> Referenciado por: `AGENTE.md`, `reconcile-contract.md` (W3), `.claude/commands/revisar.md`, `.claude/commands/estilo-flashcard.md`.

---

## Papel

O FSRS é o motor de retenção do MedHub. Este contrato evita os dois modos de falha observados na sessão 075: **backlog represado** (307 cards bons nunca revisados, fila real de só 25) e **poluição por cards legados** (70 heurísticos de baixa qualidade na fila).

---

## Estado do banco (vocabulário)

- **Cards qualitativos** (`needs_qualitative = 0`): cunhados pelo agente pela régua `estilo-flashcard.md`. **São a fila ativa.**
- **Cards aposentados** (`needs_qualitative = 2`): excluídos da fila pelo `fsrs_queue`. Inclui os 70 heurísticos legados após a **bankruptcy da sessão 075**.
- **`needs_qualitative = 1`** (heurístico ativo): **não deve mais existir** após a bankruptcy. Se reaparecer (geração legada), é defeito.
- **State FSRS** (`fsrs_cards.state`): 0 = novo (nunca revisado), 1 = aprendendo, 2 = revisão, **3 = relearning** (card de revisão que caiu — passo intra-sessão do py-fsrs; existia no dado sem constar aqui, F52c/v1.1).
- **Invariante `needs_qualitative`**: card com `needs_qualitative = 1` **não deve existir na fila ativa** (`state < 2`) — sensor `NEEDS_QUALITATIVE_ATIVO` (WARN) no `auto_check` (v1.1; antes o invariante era prosa sem sensor, violado em 6 cards).

## Balanceador de carga do agendamento (v1.1 — absorve `app/utils/fsrs_balance.py`, F52a)

O balanceador é PARTE DESTE CONTRATO (operava fora dele desde a s128; a norma efetiva vivia
num doc de comando). Parâmetros estáveis, agora lei: em **toda gravação de card `state == 2`**
com intervalo ≥ 4 dias, `record_review` pode mover o **`due`** (nunca `stability`/`difficulty`)
para o dia de **menor carga** dentro da janela de **±5% do intervalo** (piso 1 dia, teto 10),
nunca para hoje/passado; empate preserva o dia do FSRS. Falha no balanceamento degrada para o
`due` original com WARN. Suíte `tools/test_fsrs_balance.py` é BLOCKING no `auto_check` (2c).

### Calendário de provas: blackout e overflow (v1.2 -- promote do F71, s174)

O balanceador **conhece o calendário**, e isso é lei, não detalhe de implementação. A janela de
**blackout** -- o **dia da prova e o dia seguinte** -- **não recebe card e não é atravessada**:
um alvo que caia nela é movido para **antes** da prova; sem vaga dentro da folga de ±5%, o card
**fica onde está** e passa a ser **overflow DECLARADO**, nunca um card silenciosamente empurrado
para depois. 🔴 **As datas saem de `core/provas.json`** (leitor único `app/utils/provas.py`) --
**data literal no código é proibida**: um blackout hardcoded envelhece exatamente quando importa,
que é na véspera da prova seguinte. O overflow é **estado do banco**, não log: `db.overflow_blackout`
o expõe com `card_id` e `due`, o Plano do Dia o imprime no boot, e `tools/fsrs_load.py --blackout`
re-roda o balanceador sobre a fila com **dry-run + COUNT-ASSERT**. Resolver um overflow (mover à
mão para antes da prova) é **decisão do operador**, não do harness.

### Zona canônica: o relógio é LOCAL e é um só (v1.2 -- promote do F80/F80b, s174/s176)

Todo instante que o `ipub.db` grava ou compara é **hora LOCAL naive**, e vem de **`db.agora()`** --
o relógio único. A regra vale para **writers E leitores**: `SELECT ... datetime('now')` devolve
**UTC** e comparar isso com uma coluna gravada em local é erro silencioso de fuso. Medido no F80b:
a janela de "erro fresco" de 48h operava como **45h**, e a janela de volume deslizava um dia inteiro
entre 21h e a meia-noite. `db.agora()` é monkeypatchável nos testes, e por isso os chamadores a
invocam **pelo atributo do módulo** (`db.agora()`), nunca por `from db import agora`.
🔴 **Escopo DECLARADO:** a varredura estrutural que impõe isto cobre `app/`; os sítios gêmeos em
`tools/` (`audit_fsrs.py`, `variancia.py`) seguem **deferidos, não esquecidos** -- e o histórico
anterior a `37e0859` continua gravado em UTC (backfill é decisão do operador, Tier 2.3).

---

## Política de fila (`/revisar`)

- **Cap de novos por sessão:** default `--new-limit 10`. Não despejar o backlog inteiro — drenar em ondas.
- **Priorização por área fraca:** ao drenar, filtrar por `--area`/`--tema` das áreas com pior performance (cruzar com `/performance`). Cards de Cardiologia/Hepato/Dermato/FA antes de áreas fortes.
- **Ordem natural da fila:** atrasados → hoje → novos (definida no `fsrs_queue`).
- **Revisão em cluster (F3, v1.1):** `fsrs_queue.py --cluster` preserva a prioridade de bucket e agrupa por (area, tema) dentro de cada bucket -- um PREPARAR aquece o tema e drena o cluster inteiro. `day_plan.py --review-plan` emite os clusters do dia com contagem derivada da fila real (contagem manual foi fonte de erro 3x na s108). A flag é opt-in: sem ela, a ordem é a natural.
- **Ratings honestos:** o agente avalia 1-4 pela resposta do usuário (contrato em `revisar.md` §Modo conversacional); honestidade > generosidade — a precisão do FSRS depende disso.

---

## Teto dinâmico (F4, v1.1 -- decisão do operador 2026-07-05)

A tensão estrutural observada na s108 (44 agendados > teto de 30 antes de qualquer card novo) é resolvida por **teto dinâmico**, não por teto fixo + mutirão:

- `TETO_BASE = 60` cards/dia (agendados + novos), vigente fora do regime de dívida.
  *(histórico: 30 na v1.1 → 40 na s126 → **60 na s159**, ritmo declarado sustentável pelo usuário na virada UERJ/MFC: "60q/dia + 60 flashcards/dia".)*
- `CAP_MULTIPLICADOR = 1.5` — fator máximo de escala do teto em regime de dívida.
  *(era 2 até a s159; caiu junto com a subida do TETO_BASE — dobrar 60 daria 120/dia e reinstalaria o pico-e-queda que o usuário rejeitou explicitamente.)*
- **Regime de dívida:** `atrasados > TETO_BASE`. Nele, `teto_efetivo = int(min(TETO_BASE + atrasados, CAP_MULTIPLICADOR * TETO_BASE))` — na prática o teto sobe **até 90 até a dívida drenar**, e volta a 60 quando `atrasados <= 60`.
- A fonte dos números é `day_plan.py` (campo `divida` no `--json`; linha "Teto do dia" no render). Constantes nomeadas em `tools/day_plan.py` (`TETO_BASE`, `CAP_MULTIPLICADOR`) — ajuste é edição de 1 linha + este contrato.
- O teto **informa** a sessão de revisão; quem drena é o `/revisar`. Nenhuma drenagem automática.
- ⚰️ **Exceção datada (s165, 2026-09-05 -> 13/09/2026) -- ENCERRADA ANTES DO PRAZO em 2026-09-07 (s168).** O usuário autorizou um *sprint* de **120 cards/dia** (2 blocos de 60) até o ENAMED, como decisão pontual e não como novo teto. **Revogada pelo próprio usuário na s168**, ao decidir o sprint de questões S17-S20: *"Manteremos o teto de 60 cards e, se necessário subimos se o teto estourar."* Efeito: o regime canônico (**60/dia, máx. 90 em dívida**) volta a valer de 07/09 em diante, sem esperar 14/09 -- o "subimos se estourar" é exatamente o `CAP_MULTIPLICADOR` já vigente, não uma segunda exceção. `TETO_BASE`/`CAP_MULTIPLICADOR` nunca mudaram. Lápide mantida (e não deletada) porque a s165/s166/s167 rodaram sob ela e os números daquelas sessões só se explicam com ela à vista.
- Alternativa descartada: "modo mutirão" (teto fixo + sessão dedicada quando estourar) -- decisão registrada no PRD engenharia-ledger-f1-f13.

## Drenagem do backlog (ondas)

Backlog = cards `state = 0` (nunca revisados). Após a bankruptcy, ~307 cards qualitativos.

- **Meta:** reduzir o backlog a cada sessão de revisão, não deixá-lo crescer monotonicamente.
- **Onda típica:** 15-25 cards/sessão, priorizados por área fraca. Em ~15 sessões o backlog inicial drena.
- **W3 (reconcile):** se o backlog crescer sem drenagem por várias sessões, o boot sinaliza — é gatilho para uma sessão de `/revisar` dirigida.
- **Sinal de saúde:** `cards em state≥1 / total qualitativo` subindo ao longo do tempo.

---

## Aposentadoria de cards

- **Bankruptcy de legados (sessão 075):** os 70 heurísticos (`needs_qualitative=1`) foram aposentados (`=2`) em vez de regenerados. Supera o caminho de backfill-regeneração de `estilo-flashcard.md` para estes cards.
- **Go-forward:** cards novos nascem qualitativos (`=0`) via `insert_questao.py --cards-file`. A geração heurística está aposentada — nunca reintroduzir `needs_qualitative=1`.
- **Aposentar um card vivo:** `needs_qualitative = 2` (migração one-shot em `tools/`, backup-first). Usar quando um card é redundante ou o erro de origem foi corrigido.

---

## Zero-DB no Cloud (invariante)

`ipub.db` é **local-only**. O `/revisar` roda na máquina onde o banco vive (inclusive via remote-control/celular) — é a interface única de revisão desde a pivotagem agent-first. Não há réplica hospedada do FSRS nem sincronização remota: qualquer estado de revisão fora desta máquina está fora de escopo.

---

## Reconciliação FSRS (boot)

No check de boot (`reconcile-contract.md`), reportar: total de cards qualitativos, backlog (`state=0`), fila vencida hoje, e tendência do backlog. Drift sem drenagem → W3.

---

## Changelog

- **v1.2 (2026-09-10, s176 -- item 0.7 do Tier 0):** dois **promotes** de comportamento que já era
  permanente e não tinha portador em `core/contracts/` -- **calendário de provas** (blackout +
  overflow declarado, datas sempre de `core/provas.json`; F71) e **zona canônica LOCAL** (relógio
  único `db.agora()`, writers **e** leitores; F80/F80b). Nenhuma mudança de código: o que muda é
  que a regra passa a existir onde alguém a lê antes de reimplementá-la. O terceiro promote do
  item (o campo `fsrs_revlog.reason_servido`, F76) ficou no spec do F81, que é o portador certo
  dele.
- **v1.1 (2026-07-05, s108+):** balanceador de carga absorvido como lei (F52a); teto dinâmico (F4).
- **v1.0 (2026-06-03, s075):** contrato inicial -- backlog represado e poluição por cards legados.
