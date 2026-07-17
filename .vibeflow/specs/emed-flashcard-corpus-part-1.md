# Spec: Corpus EMED — Colheita + Extração (Part 1)

> Generated via /vibeflow:gen-spec on 2026-07-17 from .vibeflow/prds/emed-flashcard-corpus.md

## Objective

Colher os 275 `Flashc.pdf` do EMED 2024 para `resumos/<area>/Flashcards - <Tema>.pdf` e extrair cada deck em pares frente/verso estruturados, consultaveis por tema — a fundacao que alimenta a cunhagem (Parts 2-3).

## Context

O corpus vive em `D:\Med\Estrategia 2024 Extensivo\Extensivo\<Esp>_-_Extensivo\<Tema>\<Tema>\Flashc.pdf` (275 decks, 18 especialidades, estrutura regular; tema = nome da pasta). PyPDF2 extrai o texto (frente=pagina impar, verso=par; watermark "Estrategia MED" repetido a limpar) — validado no deck de Endometriose (25 cards). Hoje o corpus e inacessivel a cunhagem. O layout `resumos/` de destino esta confirmado: `Clinica Medica/<esp>` (inclui Infectologia, Psiquiatria), `GO`, `Cirurgia`, `Pediatria`, `Preventiva`.

## Definition of Done

1. Existe `tools/emed_flashcards.py` com dois modos: `--harvest --source <path>` (copia + renomeia + mapeia area, idempotente) e `--query --tema "X" [--area Y]` (retorna os pares frente/verso do deck como JSON no stdout).
2. Apos `--harvest`, os **275** decks estao em `resumos/<area>/Flashcards - <Tema>.pdf` com area correta (contagem == 275; spot-check de 1 deck por especialidade confere area e tema); 0 misfiled, 0 perdidos.
3. Cada deck tem sidecar `Flashcards - <Tema>.cards.json` = lista `{n, frente, verso}` com watermark limpo; decks image-only/corruptos (texto vazio) entram num relatorio de flags (`emed_harvest_report.json`) sem quebrar o batch.
4. `--query --tema "Endometriose"` retorna os 25 pares; a resolucao tema->deck faz match exato-normalizado (lowercase, sem acento, underscore->espaco, sem prefixo numerico) -> fuzzy difflib (ratio >= 0.85) -> lista de candidatos se ambiguo/ausente.
5. PDFs (`*.pdf` ja coberto) **e** os `*.cards.json` derivados ficam gitignored (IP do EMED; RAG local) — `.gitignore` atualizado e verificado (`git status` nao lista os artefatos).
6. **[quality]** ASCII/no-LaTeX limpo (convencao §4.5); a colheita/extracao dos 275 roda via `/workflows` (fan-out por deck: extrai -> estrutura -> valida) para paralelizar + QA por deck; `python -X utf8 tools/auto_check.py --changed` sem achado BLOCK.

## Scope

- CLI `tools/emed_flashcards.py` (harvest + extract + query + report).
- Tabela de mapeamento area EMED -> resumos (Ginecologia/Obstetricia->GO; Cardio/Dermato/Endocrino/Gastro/Hemato/Hepato/Nefro/Neuro/Pneumo/Psiquiatria/Reumato/Infectologia->Clinica Medica/<esp>; Pediatria->Pediatria; Medicina Preventiva->Preventiva; Cirurgia->Cirurgia; Ortopedia->Cirurgia).
- Extracao estruturada (par a par) para `.cards.json` co-locado.
- `.gitignore` para os `.cards.json`.
- Workflow de fan-out (extract+validate) sobre os 275 decks.

## Anti-scope

- Indexacao semantica / ChromaDB / mudanca no RAG (`app/engine/rag.py`) — match por tema basta no v0; busca semantica sobre card text fica pra depois.
- Qualquer escrita no `ipub.db` / FSRS (isto e so corpus de referencia).
- OCR de decks image-only (so flag no relatorio).
- Cards de especialidades sem `Flashc.pdf` (Oftalmo/Otorrino/Radiografia/Preventiva-intensivo = 0 decks).

## Technical Decisions

- **Store = sidecar JSON estruturado por deck** (nao ChromaDB): a selecao (Part 3) e card-a-card por tema; um store tema-keyed e o minimo robusto e respeita o anti-scope de RAG. Trade-off: sem busca semantica cross-deck — aceitavel, pode-se alimentar o RAG existente depois.
- **Resolucao tema->deck**: normalizacao + difflib (stdlib, sem dep nova). Trade-off: fuzzy pode errar em temas proximos; mitigado por retornar candidatos quando ratio < 1.0 e o agente decide.
- **Harvest idempotente**: re-rodar nao duplica (skip se destino existe + hash igual). Protege contra HD desmontar no meio.
- **Workflow no /implement**: fan-out por deck (extrai+valida) — honra o mandato de /workflows e da QA por deck (flag image-only) que um loop serial esconderia; log explicito de decks dropados (no silent cap).

## Applicable Patterns

- `error-insertion-pipeline.md` — o CLI segue a convencao de `tools/` (DB_PATH pattern se tocar db; aqui e read-only de filesystem, stdout JSON).
- Convencao §4.5 (AGENTE.md) — ASCII/no-LaTeX em qualquer output.
- Politica de PDF s086 — manter PDF gitignored dentro de `resumos/`.
- **Novo micro-pattern**: "corpus de referencia externo -> sidecar estruturado gitignored" (documentar em `.vibeflow/patterns/` se reusado).

## Risks

- **HD desmonta no meio da colheita** -> harvest idempotente + rodar tudo numa passada enquanto D: esta montado; report parcial se faltar.
- **Nome de pasta EMED != tema do resumo/taxonomia** -> resolvido na Part 3 (query fuzzy); aqui so garantir que o nome do arquivo preserva o tema EMED limpo.
- **Deck image-only** (sem texto) -> flag no report, nao quebra; vira referencia visual, sem sidecar util.
- **Colisao de nome de tema entre areas** (ex.: "Sistemas de Informacao em Saude" em GO e Preventiva) -> o par (area, tema) desambigua; `--query` aceita `--area`.

## Dependencies

Nenhuma. Pode rodar em paralelo com a Part 2.
