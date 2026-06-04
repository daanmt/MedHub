---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [handoff-contract, reconcile-contract, AGENTE]
---

# Contrato do ESTADO.md
**Versão 1.0 | 2026-06-03 (sessão 075) — primeira instância; adaptado do `agente-daktus-content/core/contracts/estado-contract.md` v2.1**

> Documento normativo. Define papel, estrutura e limites do `ESTADO.md`.
> Referenciado por: `AGENTE.md` (§2 boot, §3 closure), `handoff-contract.md`, `reconcile-contract.md`.

---

## Papel

O `ESTADO.md` é o **snapshot canônico macro** do MedHub. Responde: *"onde estou na jornada — metas, indicador, marcos?"* — não em nível de sessão.

Ele **não é** diário de sessões (isso é `history/`). Ele **não é** a camada operacional imediata (isso é `HANDOFF.md`). É o estado consolidado de metas e frentes.

---

## Frentes de estudo (vocabulário canônico)

O MedHub tem 4 frentes + infraestrutura. Toda seção "por frente" (aqui e no HANDOFF) usa este vocabulário:

| Frente | O que cobre | SSOT |
|---|---|---|
| **Volume & Metas** | questões feitas/acertos, marcos (ENAMED/ENARE/Final), custo/Q | `sessoes_bulk` + planilha Drive |
| **Conteúdo** | resumos clínicos | `resumos/**/*.md` |
| **Erros & Cards** | erros estruturados + flashcards | `questoes_erros` + `flashcards` |
| **FSRS** | fila de revisão espaçada | `fsrs_cards` + `fsrs_revlog` |
| **Infraestrutura** | skills, tools, RAG, contratos | repositório |

---

## Estrutura fixa

```
# ESTADO — MedHub
*Atualizado: YYYY-MM-DD (sessão NNN) | Ferramenta: ...*

## Metas
- Marcos com alvo + data + ritmo (ENAMED/ENARE/Final)
- Indicador atual (questões / alvo) + performance geral
- Contadores macro (resumos, erros, cards ativos)

## Estado por frente (macro)
- Volume & Metas: [1 linha]
- Conteúdo: [1 linha]
- Erros & Cards: [1 linha]
- FSRS: [1 linha — fila ativa, backlog]

## Próximos passos
[fila de prioridades guiada pelo cronograma — pointer para ROADMAP/cronograma]

## Repositório
```

---

## Regras de conteúdo

**Permitido:** metas e marcos, indicador macro, estado de fase por frente (1 linha), contadores, fila de prioridades macro.

**Proibido:**
- Narrativa de sessão ("o que foi feito na sessão 074…") → vai em `history/`.
- Pendências operacionais imediatas → vão no `HANDOFF.md`.
- Lista session-by-session acumulada (o ESTADO antigo tinha "Últimas 10 sessões" — isso é pointer para `history/INDEX.md`, não conteúdo).

---

## Frequência de atualização

Atualizar **quando o estado macro muda:** indicador cruza marco, nova frente, skill/contrato muda de versão, meta revisada. **Não** atualizar para progresso iterativo dentro da mesma frente (isso é HANDOFF + history).

---

## Relacionamento com HANDOFF.md

| Documento | Pergunta | Granularidade | Update |
|---|---|---|---|
| `HANDOFF.md` | "o que está rolando agora?" | operacional (sessão) | toda sessão significativa |
| `ESTADO.md` | "onde estou na jornada?" | macro (marco/indicador) | quando o macro muda |

Divergência entre os dois → `reconcile-contract.md`.

---

## Verificação antes de commitar

- O indicador do ESTADO bate com `sessoes_bulk` (via `/performance`)?
- O estado por frente é consistente com o HANDOFF na mesma edição?
- Contadores (resumos, erros, cards) refletem o repositório/`ipub.db`?
