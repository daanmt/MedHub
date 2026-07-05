---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [reconcile-contract, estado-contract, AGENTE]
---

# Contrato de Gerenciamento do FSRS
**Versão 1.1 | 2026-07-05 (s108+, F3/F4 do ledger AUDITORIA_MEDHUB) — anterior: 1.0, 2026-06-03 (sessão 075)**

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
- **State FSRS** (`fsrs_cards.state`): 0 = novo (nunca revisado), 1 = aprendendo, 2 = revisão.

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

- `TETO_BASE = 30` cards/dia (agendados + novos), vigente fora do regime de dívida.
- **Regime de dívida:** `atrasados > TETO_BASE`. Nele, `teto_efetivo = min(TETO_BASE + atrasados, 2 * TETO_BASE)` -- na prática o teto **dobra (60) até a dívida drenar**, e volta a 30 quando `atrasados <= 30`.
- A fonte dos números é `day_plan.py` (campo `divida` no `--json`; linha "Teto do dia" no render). Constantes nomeadas em `tools/day_plan.py` (`TETO_BASE`, `CAP_MULTIPLICADOR`) -- ajuste é edição de 1 linha + este contrato.
- O teto **informa** a sessão de revisão; quem drena é o `/revisar`. Nenhuma drenagem automática.
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

`ipub.db` é **local-only**. O Streamlit Cloud tem filesystem efêmero — **não** persiste FSRS. O `/revisar` roda na máquina onde o banco vive (inclusive via remote-control/celular). Não há sincronização de FSRS para o Cloud; qualquer feature de revisão no Cloud seria stateless e está fora de escopo.

---

## Reconciliação FSRS (boot)

No check de boot (`reconcile-contract.md`), reportar: total de cards qualitativos, backlog (`state=0`), fila vencida hoje, e tendência do backlog. Drift sem drenagem → W3.
