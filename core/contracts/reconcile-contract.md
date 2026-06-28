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
| **W1** | Planilha Dashboard (somas das **abas por disciplina**) diverge de `sessoes_bulk` | WARNING | `/importar-planilha` (verificar) — comparar contra as abas, **nunca** o Quadro Geral |
| **W2** | `history/session_NNN.md` existe mas não está no `history/INDEX.md` | WARNING | INDEX desatualizado |
| **W3** | Backlog FSRS (`state=0`) cresceu sem drenagem há N sessões | WARNING | `fsrs-management-contract.md` |
| **W4** | Áreas em `sessoes_bulk` fora de `AREAS_VALIDAS` | WARNING | vocabulário (ver sessão 075: `GO`, `Obstetricia`) |
| **W5** | `grade.json` defasado vs `Cronograma.pdf` (sha256 difere) | WARNING | `python tools/cronograma.py --check` |
| **W6** | "Próxima = SNN" (semana de conteúdo) no HANDOFF/ESTADO desatualizada vs o trabalho real | WARNING | ponteiro textual vs últimas sessões |
| **W7** | Gap de meta materializado (`acum + cronograma restante < meta`) — **fork estratégico, reporta UMA vez** | WARNING | `python tools/cronograma.py --gap` |

**BLOCKING** → resolver antes de iniciar trabalho novo. **WARNING** → reportar; trabalho pode seguir.
> **Cronograma (W5-W7) nunca é BLOCKING:** plano não é verdade-de-estado; estar atrasado é *informação de gestão*, não corrupção (`cronograma-contract.md`).

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
  → W5: python tools/cronograma.py --rebuild (regenera o cache; grade.json é derivado do PDF).
  → W6: atualizar o ponteiro textual "Próxima = SNN" no HANDOFF/ESTADO (único write da feature de cronograma).
  → W7: reportar UMA vez; registrar a decisão do usuário em ESTADO §Metas; silenciar até a premissa mudar.
       🔴 Resolução de W5-W7 NÃO grava no db (cronograma-contract.md, Cláusula 5).

PASSO 4 — Saída
  → Condição: HANDOFF ≤ 60 linhas + header com session em history/ + HANDOFF ⟷ ESTADO ⟷ db consistentes.
  → Commitar a reconciliação como commit separado, antes do trabalho da sessão.
```

**Arquivos alteráveis no Reconcile:** `HANDOFF.md`, `ESTADO.md`, `history/`, `history/INDEX.md`, `ipub.db` (via CLIs/migração), `core/cronograma/grade.json` (cache regenerável via `--rebuild`). **Não alterar** em reconcile: `resumos/`, `skills/`, `.claude/commands/`, `Cronograma.pdf` (SSOT).

---

## Absorção de dados de performance (planilha → db)

A planilha do Drive (`Dashboard EMED 2026`) é o **SSOT de volume** e a fonte **mais fresca**: o usuário a preenche **logo após cada estudo** (lê o tema + faz exercícios), registrando as questões/performance nas linhas de tarefa do dashboard e **riscando / mudando a cor do tema no cronograma** ao concluí-lo. Consequências para o reconcile:

- **A planilha geralmente já reflete o trabalho.** Quando o usuário diz "registrei / concluí X", o esperado é **delta = 0** vs o db se já tiver sido importado nesta sessão — confirmar, não duplicar. Se o db ainda não tem, importar o delta.
- **Abas por disciplina são autoritativas.** **W1 reconcilia contra a soma das abas por disciplina** (que não dependem de fórmula de agregação), não contra o Quadro Geral. O Quadro Geral teve **um** bug de fórmula confirmado (Obstetrícia somava acertos em vez de questões — corrigido pelo usuário em s075).
- ⚠️ **Falso-positivo por delay de leitura:** a leitura via MCP (content snippet / read) pode **atrasar vs a edição ao vivo** do Google. Em s075 o QG do Infecto pareceu não somar (177 vs 217 da aba), mas era **delay de propagação** — minutos depois mostrava 217. **Re-checar após alguns minutos antes de concluir que é bug de fórmula.** Não alertar o usuário sobre "bug" sem reconfirmar.
- **Sinal de conclusão de tema:** tema **riscado / recolorido** no cronograma = concluído. É o gatilho que alimenta a priorização do *próximo tema* (a fila de `ESTADO.md §Próximos passos` segue o cronograma). Ler os marcadores via `download_file_content` + openpyxl (ver `.claude/commands/importar-planilha.md`).
- **Delta, não total:** a planilha guarda acumulados por tarefa; importar só `(soma da aba) − (total no db)` por área — via `/importar-planilha` → `tools/importar_sessoes.py`.
- **Usuário relata "fiz X, acertei Y" (sem ter lançado na planilha ainda):** `tools/registrar_sessao_bulk.py` ANTES de processar erros (decisão "SSOT volumétrica" em `AGENTE.md §6`). O usuário tipicamente lança na planilha em paralelo — conciliar, não somar em dobro.
- **Cronograma:** a planilha `Cronograma de Reta Final.xlsx` NÃO persiste no db — leitura sob demanda para guiar prioridades e ler os marcadores de conclusão (decisão sessão 075).
