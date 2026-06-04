---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [reconcile-contract, estado-contract, AGENTE]
---

# Contrato de Gerenciamento do FSRS
**Versão 1.0 | 2026-06-03 (sessão 075) — primeira instância**

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
- **Ratings honestos:** o agente avalia 1-4 pela resposta do usuário (contrato em `revisar.md` §Modo conversacional); honestidade > generosidade — a precisão do FSRS depende disso.

---

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
