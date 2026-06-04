---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [estado-contract, reconcile-contract, AGENTE]
---

# Contrato do HANDOFF.md
**Versão 1.0 | 2026-06-03 (sessão 075) — primeira instância; adaptado do `agente-daktus-content/core/contracts/handoff-contract.md` v2.0**

> Documento normativo. Define papel, estrutura, limites e rotação do `HANDOFF.md`.
> Referenciado por: `AGENTE.md` (§2 boot — lido PRIMEIRO; §3 closure), `estado-contract.md`, `reconcile-contract.md`.

---

## Papel

O `HANDOFF.md` é a **camada operacional curta**. Permite a qualquer agente saber, em < 2 minutos, onde está o trabalho e o **próximo passo imediato**.

Ele **não é** histórico de sessões. **Não é** sumário acumulativo. É um snapshot do *agora*.

---

## Limite hard

**Máximo: 60 linhas.** Um HANDOFF normal cabe em ~25-35 linhas. Violação é condição **BLOCKING** que ativa o Reconcile Mode (ver `reconcile-contract.md`).

---

## Estrutura obrigatória

```markdown
# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: YYYY-MM-DD — [descrição breve em ~5 palavras] (sessão NNN)*

## ▶ Próximo passo imediato (ao retomar)
[1-3 itens — a primeira coisa a fazer na próxima sessão]

## Estado por frente
- **Volume & Metas:** [status] | [próximo passo — 1 linha]
- **Conteúdo:** [status] | [resumo ativo / gap — 1 linha]
- **Erros & Cards:** [status] | [1 linha]
- **FSRS:** [fila ativa / backlog / vencidos] | [1 linha]
- **Infraestrutura:** [apenas se mudou; omitir se nada mudou]

## Última sessão — sessão NNN
- [máximo 5 bullets]

## Pendências/observações ativas (opcional)
[máximo 3 linhas; omitir se nada]

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
```

---

## Regras de conteúdo

**Permitido:** próximo passo imediato; 1 linha por frente; última sessão (≤5 bullets); pendências cross-frente (≤3 linhas).

**Proibido:**
- Conteúdo de sessões anteriores à última (vive em `history/`).
- Narrativa de mais de uma sessão.
- Duplicação do que está em `history/session_NNN.md`.
- Mais de 5 bullets em "Última sessão" / mais de 1 linha por frente.

---

## Rotação (regra de ouro)

Ao fechar uma sessão significativa:
1. O conteúdo de "Última sessão" **já existe** em `history/session_NNN.md`.
2. A seção "Última sessão" é **substituída** (não acumulada) pela sessão corrente.
3. "Estado por frente" é atualizado para refletir o estado real pós-sessão.

**Se você está adicionando ao HANDOFF sem remover algo equivalente, está acumulando em vez de rotacionar. Interromper.**

---

## Sessão significativa

Requer `history/session_NNN.md` + atualização do HANDOFF quando produz: resumo criado/editado, erros inseridos, cards cunhados/regenerados, volume registrado, mudança de infraestrutura (skills/tools/contratos), ou resolução de pendência bloqueante.

**Não-significativa** (só pointer no INDEX, sem session_NNN): leitura/diagnóstico sem artefato; `/performance` ou `/revisar` puro sem mudança de conteúdo; exploração < 15 min sem persistência.
