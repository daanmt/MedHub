# Spec: Religar a Cunhagem — Selecao por Contexto (Part 3)

> Generated via /vibeflow:gen-spec on 2026-07-17 from .vibeflow/prds/emed-flashcard-corpus.md

## Objective

Fazer o fluxo de cunhagem consultar o deck EMED do tema e adaptar **so os cards que casam com o elo quebrado** do erro (ou lacuna), no padrao atomico — nunca o deck inteiro.

## Context

Hoje `analisar-questao.md §8` entrega 1-3 cards + o comando `insert_questao.py`, cunhados do zero pelo agente. Com o corpus colhido (Part 1) e o padrao atomico (Part 2), a cunhagem ganha uma fonte de referencia: o deck EMED do tema. O modelo decidido no PRD e **selecao por contexto** — o card EMED entra so quando casa com o gap especifico, reformulado atomico e ancorado no elo do erro. Nunca import em massa (rejeitado: ~6.000 cards detonariam a fila e a estrategia "matar os cards").

## Definition of Done

1. `analisar-questao.md §8` ganha o passo "Consultar deck EMED": rodar `python tools/emed_flashcards.py --query --tema "<tema>" [--area <area>]` -> receber os pares frente/verso -> selecionar os que tocam o elo quebrado/lacuna -> adaptar ao padrao atomico (Part 2), ancorando no erro do aluno.
2. A selecao e **dirigida por contexto**, documentada como tal: entram so os cards cujo conteudo casa com o elo quebrado / tema fraco / lacuna; **nunca** o deck inteiro. O criterio de match (elo do erro x frente/verso EMED) esta escrito.
3. **Fallback gracioso**: sem deck para o tema (query retorna vazio/candidatos), o fluxo cai na autoria do zero pelo padrao Part 2, sem erro e sem travar.
4. O workflow `.agents/workflows/analisar-questoes.md` referencia o passo de consulta (orquestracao), **sem** reespecificar o protocolo da skill (contrato §7.2).
5. **Demo end-to-end**: reforjar o cluster Endometriose (831-835) usando o deck EMED colhido, no padrao atomico, persistido (`recurate_cards.py` para reescrever preservando `card_id`/FSRS; splits novos via `insert_card_base.py`); FSRS preservado onde o card_id e mantido.
6. **[quality]** Espelhos `sync_skills` regenerados + `--check` limpo; sem duplicacao semantica skill<->workflow (workflow referencia, nao copia); ASCII/no-LaTeX; `python -X utf8 tools/auto_check.py --changed` sem achado BLOCK.

## Scope

- `.claude/commands/analisar-questao.md` (§8/§9: passo de consulta EMED + selecao por contexto + fallback).
- `.agents/workflows/analisar-questoes.md` (referencia a orquestracao).
- `.agents/workflows/gerar-reforco.md` (se toca cunhagem — alinhar ao mesmo passo).
- Regeneracao dos espelhos `sync_skills`.
- Demo: reforja do cluster Endometriose (831-835) — persistida.

## Anti-scope

- Import em massa de deck (rejeitado no PRD).
- Mudanca no `insert_questao.py`/schema (os cards ja saem atomicos; o CLI persiste como hoje).
- Selecao semantica automatica por embedding (v0 = o agente le os pares e escolhe pelo elo; sem classificador).
- Reforja dos outros flagados (350/398/757/759) — segue como trabalho de conteudo pos-implement, fora do DoD (o demo de Endometriose prova o fluxo).
- Gate de evidencia do 760.

## Technical Decisions

- **Selecao pelo agente, nao por codigo**: o agente le os pares EMED e escolhe os que casam com o elo (semantica humana), reformulando atomico. Trade-off: nao-deterministico, mas e exatamente o julgamento metacognitivo que e o diferencial; um classificador seria over-engineering no v0.
- **Persistencia via CLIs existentes**: `recurate_cards.py` (reescreve preservando FSRS) + `insert_card_base.py` (splits novos) + `insert_questao.py` (go-forward). Sem CLI novo.
- **Workflow referencia, nao reespecifica** (contrato §7.2): a orquestracao numera o passo e chama a skill por path; o protocolo vive so na skill.

## Applicable Patterns

- `error-insertion-pipeline.md` — o passo de consulta entra ANTES do `insert_questao`; a persistencia segue o pipeline canonico.
- `agent-workflow-protocol.md` — workflow orquestra, skill especifica.
- Contrato §7.2 — sem duplicacao skill<->workflow.
- `estilo-flashcard.md` (Part 2) — o padrao atomico que os cards adaptados seguem.
- Decisao s107 — regenerar espelhos.

## Risks

- **Deck EMED conflita com o resumo/gabarito da banca** -> heranca de evidencia (estilo-flashcard §Evidencia): o card herda o veredito da origem; conflito banca x evidencia -> 🔴 armadilha banca-dependente. Nao copiar cegamente o EMED se divergir do resumo auditado.
- **Agente puxa demais (vira import disfarcado)** -> DoD 2 (selecao por contexto, criterio escrito) + o teto de 30/dia + revisao humana; log de quantos cards vieram do deck vs autorais.
- **Tema sem deck** -> DoD 3 (fallback).
- **Duplicar card que ja existe no baralho** -> checar reincidencia (F25) antes de persistir; idempotencia do `insert_card_base` por (tema, pergunta, tipo).

## Dependencies

- .vibeflow/specs/emed-flashcard-corpus-part-1.md (query interface)
- .vibeflow/specs/emed-flashcard-corpus-part-2.md (padrao atomico)
