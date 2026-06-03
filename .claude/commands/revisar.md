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

1. **Abrir a sessão.** Rodar `--list` (com os filtros que o usuário pediu, se houver) para saber quantos cards há e anunciar o tamanho da sessão ("você tem 12 cards: 8 atrasados, 2 de hoje, 2 novos").
2. **Apresentar a FRENTE.** Para o card atual, mostrar `frente_contexto` (se houver) como contexto e `frente_pergunta` como a pergunta. **Não revelar o verso ainda.** Convidar o usuário a tentar responder.
3. **Revelar o VERSO sob pedido.** Quando o usuário responder ou pedir ("mostra", "não sei", "revela"), mostrar `verso_resposta`, depois `verso_regra_mestre` (a regra de ouro) e, se preenchida, `verso_armadilha` (o distrator/pegadinha).
4. **Coletar a avaliação.** Pedir 1-4 (1=Novamente, 2=Difícil, 3=Bom, 4=Fácil). Aceitar linguagem natural ("acertei fácil" → 4, "errei" → 1).
5. **Gravar.** Rodar `--record <card_id> --rating <n>`. Confirmar com o próximo `due` retornado ("próxima revisão em N dias").
6. **Avançar.** Buscar o próximo card (novo `--next`, ou o próximo item do lote já obtido no passo 1). Repetir 2-5.
7. **Fechar.** Quando a fila esvaziar (`{"empty": true}`) ou o usuário parar, resumir: quantos cards revisados e a distribuição de ratings.

---

## Regra anti-duplo-registro

O CLI é **stateless** — cada `--record` grava uma linha em `fsrs_revlog`. A deduplicação é responsabilidade do agente: **mantenha o conjunto de `card_id` já avaliados nesta conversa** e nunca chame `--record` duas vezes para o mesmo card na mesma sessão. (Espelha a regra `reviewed_ids` do player Streamlit, mas no nível do agente.)

---

## Notas

- **Não há sessão Streamlit.** Esta skill é a interface primária de revisão na pivotagem agent-first (ROADMAP Linha 8). O player em `app/pages/2_estudo.py` permanece como opção desktop, intocado.
- **`ipub.db` é local-only.** O CLI roda na máquina onde o banco vive; via remote-control, o comando é executado nessa máquina e o resultado volta para a conversa.
- **Avaliação honesta.** Incentivar o usuário a tentar responder antes de revelar o verso — a precisão do FSRS depende de ratings honestos.
- O FSRS subjacente é o de `app/utils/fsrs.py` (substituição pela referência é a part-2 da Onda A; esta skill não muda quando o FSRS for trocado, pois grava via `record_review()`).
