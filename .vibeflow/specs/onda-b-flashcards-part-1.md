# Spec: Onda B · Part 1 — Contrato de Autoria de Flashcard

> Gerado via /vibeflow:gen-spec em 2026-06-03
> PRD: `.vibeflow/prds/onda-b-flashcards-metacognitivos.md`
> Split: part 1 de 3 (por limite de DoD). Ver part-2, part-3.

## Objective

Estabelecer um contrato canônico de autoria de flashcards (skill `estilo-flashcard.md`) que codifica os 5 princípios validados na sessão 074, para que todo card — do agente — reforce o conteúdo onde o raciocínio rompeu, em vez de enunciar fatos genéricos.

## Context

A skill `/analisar-questao` (§8) já manda fornecer os 5 campos estruturados, mas não diz *como* cunhar um bom card — não há régua de qualidade. A geração heurística (`regenerate_cards.py`) preencheu o vácuo com perguntas genéricas (validado no erro #211). Falta o equivalente de `estilo-resumo.md`, mas para cards. Esta part é **doc-only** (skills), define a régua que as parts 2 e 3 executam.

## Definition of Done

1. Existe `.claude/commands/estilo-flashcard.md` (skill canônica) com os 5 princípios: (a) card = conteúdo clínico atômico, 1 conceito/card; (b) o erro define o alvo (`tipo_erro`+`o_que_faltou`); (c) pergunta direta sem vazar resposta nem colar `habilidades_sequenciais` cru; (d) regra-mestre = a distinção/sobreposição; (e) armadilha = o distrator específico ancorado no resumo.
2. O contrato inclui o caso-âncora #211 com exemplo **ruim** (os 2 cards heurísticos atuais) vs **bom** (os 2 cards atômicos úlcera/corrimento), tornando a régua falsificável.
3. `.claude/commands/analisar-questao.md` §8 referencia `estilo-flashcard.md` como fonte da régua, **sem reespecificar** os princípios (contrato §7.2 — uma fonte só).
4. O contrato define a granularidade (atômico; teto de cards por erro) e quando criar card de armadilha separado vs linha de armadilha no card de conteúdo.
5. **(Quality gate)** A skill segue o formato dos comandos existentes (frontmatter `description/type/layer/status`, pt-BR) e não duplica conteúdo já canônico em `analisar-questao.md`/`estilo-resumo.md`.

## Scope

- `.claude/commands/estilo-flashcard.md` (novo) — o contrato de 5 princípios + exemplos bom/ruim (caso 211) + regras de granularidade.
- `.claude/commands/analisar-questao.md` (editar) — §8 passa a referenciar a skill nova.

## Anti-scope

- Qualquer código (`insert_questao.py`, `db.py`) — é a part-2.
- Backfill / aposentar `regenerate_cards*.py` — é a part-3.
- Mudança de schema.
- Reescrever `estilo-resumo.md`.

## Technical Decisions

- **Skill própria, não seção embutida.** O contrato é referência atômica reutilizável (vale para go-forward e backfill); vive em uma skill, e `analisar-questao` referencia (contrato §7.2). Trade-off: mais um arquivo, mas evita duplicação semântica.
- **Caso-âncora real (#211) embutido.** Régua abstrata sem exemplo vira interpretável; o par ruim/bom torna o critério verificável (espelha como `estilo-resumo` usa exemplos).

## Applicable Patterns

- `agent-workflow-protocol.md` — skill = referência canônica; §7.2 (sem reespecificação cruzada).
- `clinical-summary-format.md` — espelhar o rigor de `estilo-resumo.md` (contrato de autoria com exemplos).

## Risks

- **Régua virar texto morto** se `analisar-questao` não a referenciar de fato → DoD #3 amarra a referência.
- **Sobreposição com `estilo-resumo`** → o contrato cobre cards (recall atômico), não resumos (didática 80/20); deixar a fronteira explícita.

## Dependencies

Nenhuma. É a fundação das parts 2 e 3.
