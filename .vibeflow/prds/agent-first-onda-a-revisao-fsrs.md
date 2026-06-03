# PRD: Onda A — Revisão Conversacional de Flashcards + FSRS Fiel

> Gerado via /vibeflow:discover em 2026-06-03
> Linha Evolutiva 8 do ROADMAP.md (MedHub Agent-First)

## Problem

O usuário estuda para residência médica (meta ENARE de 17.000 questões) e revisa flashcards por repetição espaçada. Hoje a revisão FSRS só funciona pelo app Streamlit local (`app/pages/2_estudo.py`), o que cria dois problemas:

1. **Inacessível remotamente.** O `ipub.db` é SQLite local e o Streamlit Cloud não persiste o estado FSRS (filesystem efêmero). Via remote-control (celular), o usuário não alcança nem o app nem o banco — não consegue revisar fora do PC.
2. **Agendamento não-fiel.** O `app/utils/fsrs.py` (82 linhas) é uma simplificação caseira que o próprio header admite "não é fiel ao algoritmo oficial" — fórmula linear de dificuldade + exponencial improvisada de estabilidade, `elapsed_days` igual a `scheduled_days`. Intervalos errados corroem a retenção, que é justamente o propósito do FSRS.

Há ainda bugs latentes no player Streamlit (closure captura o card errado; `fc_idx` estoura índice ao filtrar no meio da sessão), mas corrigi-los está fora desta onda.

## Target Audience

Usuário único — o dono do MedHub (candidato a residência, estudo solo), interagindo primariamente via Claude Code (desktop + remote-control no celular).

## Proposed Solution

Duas capacidades acopladas (mesma onda, sequência de implementação A1 → A2):

- **A1 — Revisão conversacional.** O agente vira o player de flashcards. Um CLI fino e determinístico (`tools/fsrs_queue.py`) emite a fila / próximo card vencido em **JSON** (buckets atrasado/hoje/novo, filtros área/tema, `needs_qualitative < 2`). Uma skill (`/revisar`) documenta como o agente conduz o loop conversacional: apresenta a frente → revela o verso sob pedido → captura a avaliação 1-4 → grava via `record_review()` já existente. Funciona em qualquer lugar que o Claude Code rode, sem hospedagem, sem migrar o banco.
- **A2 — FSRS fiel.** Substituir a fórmula caseira de `app/utils/fsrs.py` pela lógica de referência (`fsrs4anki` como spec / `py-fsrs` como port Python da mesma org), **preservando** o schema `fsrs_cards`/`fsrs_revlog` e a interface `init_card()`/`evaluate()` para não quebrar `record_review()` nem `review_cli.py`.

## Success Criteria

- O usuário completa uma sessão de revisão inteira **dentro da conversa do Claude Code** (desktop ou celular via remote-control), com os ratings persistidos no `ipub.db` e visíveis em `fsrs_revlog`.
- A fila respeita a política atual: ordem atrasado → hoje → novo; `needs_qualitative < 2`; filtros área/tema; `state = 0` sempre entra.
- Os intervalos do FSRS fiel batem com a implementação de referência dentro de tolerância, para um conjunto de vetores de teste conhecidos (sequência de ratings → intervalo esperado). O audit trail de `fsrs_revlog` permanece válido.
- Sem duplo-registro de um mesmo card dentro de uma sessão conversacional.

## Scope v0

- `tools/fsrs_queue.py` — CLI **read-only** que emite o próximo card / lote em JSON, honrando buckets + filtros + `needs_qualitative < 2`. `import sqlite3` permitido (CLI standalone, conforme convenção), reusando a lógica de query existente onde possível.
- Skill `/revisar` — documento canônico da assinatura do `fsrs_queue.py` + protocolo do loop conversacional do agente + mapeamento rating → `record_review()`.
- FSRS fiel em `app/utils/fsrs.py` (ou módulo novo) usando a lógica de referência; manter a interface `init_card()`/`evaluate()` estável.
- Vetores de teste validando a saída do FSRS contra a referência.

## Anti-scope

- Aposentar `regenerate_cards.py` / `regenerate_cards_llm.py` (Onda B).
- Ingestão via Google Sheets MCP (Onda C).
- Reescrever/corrigir o player FSRS do Streamlit (Onda D) — fica desktop-only como está; esta onda só **não pode quebrá-lo**.
- Mudanças no dashboard.
- Geração de novos flashcards.
- Migrar o `ipub.db` para fora do SQLite / hospedagem em nuvem.
- Alterar o schema `fsrs_cards`/`fsrs_revlog` — preservar colunas.

## Technical Context

- `app/utils/db.py::record_review(card_id, rating)` já aplica FSRS + faz `UPDATE fsrs_cards` + `INSERT fsrs_revlog`. **Reusar como único caminho de escrita** (preserva o audit trail). Ver pattern `fsrs-review-flow.md`.
- Lógica de buckets + filtros já existe em `tools/review_cli.py` (atrasado: `state>0 AND due<hoje`; hoje; novo: `state=0`). O `fsrs_queue.py` extrai o lado de leitura em JSON.
- Schema: `fsrs_cards(card_id PK, state, due, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review)`; `fsrs_revlog` (audit). Flashcards v5: `frente_contexto/frente_pergunta/verso_resposta/verso_regra_mestre/verso_armadilha`.
- Convenção (AGENTE §5.5/§6/§7.2): `import sqlite3` só em `app/utils/db.py` e CLIs standalone em `tools/`; assinatura do CLI documentada em **exatamente uma** skill; `ipub.db` é local-only, nunca commitar.
- Referência FSRS: `fsrs4anki` (algoritmo) / `py-fsrs` (port Python, mesma org). O `fsrs.py` atual tem `DEFAULT_W` (17 pesos FSRS v4) mas usa só ~3. **Bug a NÃO propagar:** `elapsed_days` hoje é igual a `scheduled_days` — o FSRS fiel deve computar `elapsed_days` a partir de `last_review` (tempo real decorrido), que é input da retrievability.
- Bug latente adjacente: `db.py::get_next_due_card()` faz `SELECT` das colunas removidas `frente`/`verso`. Se `fsrs_queue.py` o substituir, considerar remover `get_next_due_card()` (cleanup mínimo, não obrigatório nesta onda).
- **Risco (do desafio no discovery):** A2 muda a matemática de agendamento de todos os reviews futuros. Recomenda-se implementar **A1 antes de A2** mesmo dentro deste PRD único, e validar A2 contra vetores de teste antes de confiar nela.

## Open Questions

- **`py-fsrs` como dependência vs. vendorizar a lógica inline?** `py-fsrs` é instalável via pip e mantido pela open-spaced-repetition (garante fidelidade), mas adiciona dependência. Decidir no gen-spec — inclinação: usar `py-fsrs` e envolvê-lo atrás da interface `init_card()`/`evaluate()` existente.
- **Retention target do FSRS fiel.** Caseiro atual = 90%. `py-fsrs` default `request_retention = 0.9`. Manter 0.9 salvo decisão contrária.
- **`/revisar` apresenta cards em lote ou um-a-um?** Default: um-a-um com revelar-sob-pedido, espelhando a UX do `review_cli`. Confirmar no spec.
