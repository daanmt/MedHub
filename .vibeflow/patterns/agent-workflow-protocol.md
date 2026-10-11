---
tags: [agent, workflow, boot, closure, protocol, session, ssot]
modules: [.agents/workflows/, AGENTE.md]
applies_to: [workflows, commands, sessions]
confidence: inferred
status: active
canonical_source: AGENTE.md §2-3 (boot/closure), §6 (siamese twins) — this pattern is a
  gen-spec-time mirror, not the SSOT; on conflict AGENTE.md wins
last_verified: 2026-08-25
---
# Pattern: Agent Workflow Protocol

<!-- vibeflow:auto:start -->
## What
A sequência de boot e de fechamento que toda sessão de agente segue, mais a regra das "irmãs siamesas" (o erro vai para o `ipub.db`, a lição vai para `resumos/`). A fonte é `AGENTE.md` §2 (boot), §3 (fechamento) e §5.5 (SSOTs); os workflows de `.agents/workflows/` abrem pelo boot e fecham pelo protocolo de fechamento. Este pattern é espelho para o `gen-spec`: em conflito, o `AGENTE.md` vence.

## Where
- `CLAUDE.md` -> `AGENTE.md` — lido antes de qualquer ação; §2 boot, §3 fechamento.
- `HANDOFF.md` — camada operacional curta, lida PRIMEIRO no boot e atualizada em toda sessão significativa (`core/contracts/handoff-contract.md`).
- `ESTADO.md` — snapshot macro, atualizado só quando o macro muda (`core/contracts/estado-contract.md`).
- `tools/day_plan.py` — o Plano do Dia, injetado pelo hook `SessionStart` (não re-rodar à mão).
- `.agents/workflows/analisar-questoes.md`, `criar-resumo.md`, `registrar-sessao.md`, `gerar-reforco.md`, `curar-cards.md` — workflows por tarefa (tabela em `AGENTE.md` §7.1).
- `history/session_NNN.md` + `history/INDEX.md` — registro de cada sessão.
- `tools/selo.py` — rotação do ledger no selo (`--rotacionar`).

## The Pattern

**Boot (`AGENTE.md` §2):**
```
1. HANDOFF.md            # próximo passo imediato + estado por frente (ler PRIMEIRO)
2. ESTADO.md             # snapshot macro: metas, indicador, marcos
3. check de reconcile    # core/contracts/reconcile-contract.md; BLOCKING -> resolver antes
4. Plano do Dia          # já injetado pelo hook SessionStart: não re-rodar; abrir com o PANORAMA
5. workflow da tarefa    # .agents/workflows/<tarefa>.md
6. último log            # history/session_NNN.md mais recente (índice em history/INDEX.md)
7. memória longa         # hook SessionStart; senão: python -m app.memory.inspect --context
8. RAG na sessão         # app/engine/rag.py via get_topic_context
```

**Irmãs siamesas:**
```
Questão errada -> tools/insert_questao.py -> ipub.db (questoes_erros + flashcards + fsrs_cards)
Lição          -> resumo do tema         -> resumos/<Área>/[<Subárea>/]<Tema>.md
```

**Análise de questões (`.agents/workflows/analisar-questoes.md`):**
```
0. Preflight = boot do AGENTE.md
1. Interpretar o input (questões erradas OU anotações de estudo)
2. Protocolo de .claude/commands/analisar-questao.md (cunhagem consulta o deck EMED do tema)
3. insert_questao.py pela invocação canônica do §9 (lote: --errors-file numa transação)
4. Resumo: inserir no lugar temático; "Armadilhas de Prova" só acumula
5. Responder ao usuário
6. Fechamento do AGENTE.md + registrar-sessao.md
```

**Fechamento (`AGENTE.md` §3):**
```
1. HANDOFF.md  -- sempre; números do "Estado por frente" saem de
                  python tools/day_plan.py --handoff-block (nunca digitados)
2. ESTADO.md   -- só se o macro mudou
3. history/session_NNN.md + linha em history/INDEX.md (.agents/workflows/registrar-sessao.md)
4. auto-higiene -- python tools/selo.py --rotacionar (dry-run), depois --apply --expect N;
                   arquivo absorvido sai no mesmo commit
5. git add dos arquivos (nunca git add .), commit semântico, push
```

## Rules
- `AGENTE.md` antes de qualquer ação; no boot, `HANDOFF.md` antes de `ESTADO.md`.
- O Plano do Dia não se re-roda à mão: o hook `SessionStart` já o injetou.
- `ESTADO.md` não é diário: muda só com indicador cruzando marco, frente abrindo/fechando ou contrato/skill versionado. Narrativa de sessão vai em `history/`.
- Irmãs siamesas: erro relevante gera as duas escritas (banco e resumo).
- "Armadilhas de Prova" é cumulativa: só adicionar ou refinar.
- Registro de erro: um item por questão, em chamada single ou em lote `--errors-file` (transação única, rollback total).
- Log de sessão: `history/session_NNN.md`, número com 3 dígitos, mais a linha no `history/INDEX.md`.
- PDFs-fonte do EMED são RETIDOS (s086); só os `.txt` temporários da extração se apagam.
- `ipub.db` e `medhub_memory.db` nunca vão para o git.

## Examples from this codebase
- `AGENTE.md` §2 e §3 — boot e fechamento canônicos.
- `.agents/workflows/analisar-questoes.md` — workflow de 7 passos (0-6) com o `insert_questao`.
- `.agents/workflows/registrar-sessao.md` — fecha no plano as tarefas do dia (`tools/plano.py --concluir`) antes do log e republica o hub.
- `history/session_223.md` — log de sessão recente.
- Conflito em aberto: o passo 8 de `.agents/workflows/criar-resumo.md` ainda manda `tools/extract_pdfs.py --delete-pdfs`, contra a retenção de PDFs da s086 (`AGENTE.md` e a skill `extrair-pdf` dizem que os PDFs ficam).
<!-- vibeflow:auto:end -->

## Anti-patterns
- Starting work without reading AGENTE.md + ESTADO.md — leads to duplicate work, stale context
- Updating resumo without inserting error to DB (or vice versa) — violates siamese twins rule
- Deleting or overwriting existing armadilhas — they accumulate across sessions intentionally
- Creating `history/session_NNN.md` without updating `ESTADO.md` first — ESTADO.md is the primary state record
- Batch-committing multiple sessions worth of errors — each error is a discrete event with its own insert call
