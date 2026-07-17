# Spec: Padrao de Autoria Atomico EMED (Part 2)

> Generated via /vibeflow:gen-spec on 2026-07-17 from .vibeflow/prds/emed-flashcard-corpus.md

## Objective

Refinar `/estilo-flashcard` para o padrao atomico do EMED — frente gerativa curta, resposta de uma frase, o "porque" fora do recall — mantendo o targeting metacognitivo (o card nasce do erro).

## Context

`/estilo-flashcard` ja prega "conteudo clinico atomico, um conceito por card" (Principio 1), mas o **formato de 5 campos** (todo card carrega `verso_regra_mestre` + `verso_armadilha`) induz o "paragraph card": o recall fica poluido com regra + armadilha + contexto. A auditoria do usuario (17.07) reprovou a safra recente por isso (833 double-barreled; 350/398 sim/nao com muro no verso; 835 set). O deck EMED de Endometriose (25 cards, decodificado) e a referencia oposta: frente gerativa curta, resposta de uma frase, zero armadilha embutida — a pegadinha emerge da cobertura do deck + discriminacao por adjacencia. Este spec so muda o **contrato de autoria** (as regras); o fluxo que o aplica e a Part 3.

## Definition of Done

1. `/estilo-flashcard` tem uma secao "Formato atomico (referencia EMED)" com as regras derivadas (1 fato por card; frente gerativa, nunca sim/nao com payload no verso; resposta de uma frase; sets/enumeracoes -> cloze ou cards ordenados; fonte+data em fato banca-dependente) e um **antes/depois** com card real (ex.: 833 ou 350).
2. Os 5 campos estruturados reenquadrados: `verso_regra_mestre`/`verso_armadilha` explicitamente = **contexto lido-depois** (parentese, fora da carga de recall) **OU** um **card discriminador proprio** (estilo interference-busting, como EMED ureteral x vesical) — com a regra de quando usar cada forma. O recall e sempre 1 fato.
3. Reconciliacao declarada no texto: **mantem** o targeting metacognitivo (card ancorado no elo quebrado do erro — personalizacao que o EMED nao tem); **troca** a formulacao (adota o formato EMED). Um elo quebrado -> N cards atomicos.
4. Cumulativo (Regra de Acumulo): NAO deleta as secoes validas existentes (altura graduada / cards de andaime; fronteira com `estilo-resumo`; heranca de evidencia). O padrao atomico refina, nao apaga.
5. **[quality]** Espelho `sync_skills` regenerado (`tools/sync_skills.py`), `sync_skills --check` limpo; ASCII/no-LaTeX (a propria skill exige isso); `python -X utf8 tools/auto_check.py --changed` sem achado BLOCK.

## Scope

- `.claude/commands/estilo-flashcard.md` (refino: nova secao + reenquadramento dos campos + reconciliacao).
- Regeneracao do espelho `.agents/skills/source-command-estilo-flashcard/SKILL.md` via `sync_skills.py`.

## Anti-scope

- `analisar-questao.md` / workflows / `insert_questao.py` — o **fluxo** que consome o padrao e a Part 3.
- Consulta ao deck EMED (Part 3).
- Mudanca de schema em `flashcards` (os 5 campos continuam; muda como sao preenchidos).
- Reescrita do exemplo-ancora de Ulceras Genitais (fica; e adicionado o exemplo EMED, cumulativo).

## Technical Decisions

- **Refino, nao reescrita**: o Principio 1 ja diz atomico; o gap e o formato induzir bundling. A correcao cirurgica = reenquadrar regra_mestre/armadilha (fora do recall) + adicionar a secao EMED + o antes/depois. Menor blast radius, preserva a memoria institucional.
- **regra_mestre/armadilha viram opcionais por card**: default = fora do recall (parentese) ou card discriminador; deixam de ser "todo card carrega os 5 campos". Trade-off: o schema mantem os campos (compat), mas o contrato desaconselha enche-los como carga de recall.
- **sync_skills obrigatorio**: a skill e fonte canonica; o espelho e build artifact (decisao s107). Editar sem regenerar = WARN de paridade.

## Applicable Patterns

- `error-insertion-pipeline.md` — a skill referencia o pipeline; nao reespecificar.
- Contrato §7.2 (AGENTE.md) — assinatura canonica de CLI vive em UMA skill; nao duplicar.
- Decisao s107 — `.claude/commands` = fonte, `.agents/skills` = espelho gerado.
- Convencao §4.5 — ASCII/no-LaTeX.

## Risks

- **Contradicao com o texto existente** (o atual glorifica os 5 campos) -> reenquadrar explicitamente, nao deixar duas verdades; marcar a evolucao ("antes: 5 campos como carga; agora: 1 fato + porque fora do recall").
- **Perda das secoes de andaime/altura graduada** -> Regra de Acumulo no DoD 4; sao ortogonais e ficam.
- **Espelho dessincronizado** -> DoD 5 (sync_skills --check).

## Dependencies

Nenhuma. Pode rodar em paralelo com a Part 1. (A Part 3 depende desta.)
