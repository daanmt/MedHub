---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [estado-contract, handoff-contract, fsrs-management-contract, AGENTE]
---

# Contrato de Reconciliação (Reconcile Mode)
**Versão 1.0 | 2026-06-03 (sessão 075) — primeira instância; adaptado do Reconcile Mode de `agente-daktus-content/core/contracts/handoff-contract.md`**

> Documento normativo. Define o protocolo de detecção e resolução de *drift* de estado no boot.
> Referenciado por: `AGENTE.md` (§2 boot), `estado-contract.md`, `handoff-contract.md`, `fsrs-management-contract.md`.

---

## Papel

O MedHub tem **quatro superfícies de estado que podem divergir**: a planilha do Drive (SSOT de volume), o `ipub.db` (`sessoes_bulk`/FSRS), o `ESTADO.md` (snapshot macro) e o `HANDOFF.md` (operacional). Este contrato define um **check de boot** que detecta divergências **antes** de qualquer trabalho — formalizando o que foi feito manualmente na sessão 075 (conciliação planilha↔db que achou 40q de delta + 2 áreas mal-rotuladas).

---

## Check de boot (rodar no início de toda sessão de estudo)

Leitura rápida, read-only. Reporta divergências; não grava sem confirmação.

| # | Condição | Tipo | Como checar |
|---|---|---|---|
| **B1** | `HANDOFF.md` > 60 linhas | BLOCKING | contagem de linhas |
| **B2** | Header do HANDOFF aponta `sessão NNN` mas `history/session_NNN.md` não existe | BLOCKING | existência do arquivo |
| **B3** | "Estado por frente" do HANDOFF contradiz o `ESTADO.md` | BLOCKING | cross-check macro |
| **B4** | Indicador do `ESTADO.md` diverge do total de `sessoes_bulk` | BLOCKING | `/performance` vs ESTADO |
| **W1** | Planilha Dashboard (Drive) diverge de `sessoes_bulk` | WARNING | `/importar-planilha` (verificar) |
| **W2** | `history/session_NNN.md` existe mas não está no `history/INDEX.md` | WARNING | INDEX desatualizado |
| **W3** | Backlog FSRS (`state=0`) cresceu sem drenagem há N sessões | WARNING | `fsrs-management-contract.md` |
| **W4** | Áreas em `sessoes_bulk` fora de `AREAS_VALIDAS` | WARNING | vocabulário (ver sessão 075: `GO`, `Obstetricia`) |

**BLOCKING** → resolver antes de iniciar trabalho novo. **WARNING** → reportar; trabalho pode seguir.

---

## Resolução

```
PASSO 1 — Diagnóstico (não alterar nada)
  → Listar condições presentes. Registrar: "Boot em reconcile; BLOCKINGs: [...]".

PASSO 2 — Resolver BLOCKING
  → B1: trimmar HANDOFF para ≤ 60 linhas (mover excedente para history/).
  → B2: criar history/session_NNN.md reconstituída (marcar "reconstituída").
  → B3/B4: alinhar HANDOFF/ESTADO ao estado real (preferir o db/repositório).

PASSO 3 — Resolver WARNING (se houver)
  → W1: rodar a conciliação planilha↔db; importar delta via tools/importar_sessoes.py (com confirmação).
  → W2: adicionar entry no history/INDEX.md.
  → W3: agendar onda de drenagem (ver fsrs-management-contract.md).
  → W4: normalizar rótulos (migração one-shot em tools/, nunca SQL direto inline).

PASSO 4 — Saída
  → Condição: HANDOFF ≤ 60 linhas + header com session em history/ + HANDOFF ⟷ ESTADO ⟷ db consistentes.
  → Commitar a reconciliação como commit separado, antes do trabalho da sessão.
```

**Arquivos alteráveis no Reconcile:** `HANDOFF.md`, `ESTADO.md`, `history/`, `history/INDEX.md`, `ipub.db` (via CLIs/migração). **Não alterar** em reconcile: `resumos/`, `skills/`, `.claude/commands/`.

---

## Absorção de dados de performance (planilha → db)

A planilha do Drive (`Dashboard EMED 2026`) é o **SSOT de volume**; o usuário a edita manualmente. Regras de absorção:

- **No boot:** W1 detecta drift planilha↔`sessoes_bulk`. Se houver, oferecer conciliação (não importar silenciosamente).
- **Delta, não total:** a planilha guarda acumulados por tarefa; importar só `(total na aba) − (total no db)` por área — via `/importar-planilha` → `tools/importar_sessoes.py`. Ver `.claude/commands/importar-planilha.md`.
- **Usuário relata "fiz X, acertei Y":** `tools/registrar_sessao_bulk.py` ANTES de processar erros (decisão "SSOT volumétrica" em `AGENTE.md §6`).
- **Cronograma:** a planilha `Cronograma de Reta Final.xlsx` NÃO persiste no db — leitura sob demanda para guiar prioridades (decisão sessão 075).
