---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 9
slug: plano-ssot-e-cards-v2-part-9
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/fsrs_queue.py
  - core/templates/player.html
  - .claude/commands/revisar.md
  - core/contracts/revisao-calibrada-contract.md
---

# Spec -- Parte 9: player de cards como Artifact (desktop-first) com gravação em lote pelo caminho único do FSRS

> PRD `plano-ssot-e-cards-v2`, P4. **Independente das Partes 1-8** (só depende do que já existe em `fsrs_queue.py`); pode ser executada antes delas. Fecha o critério de sucesso 5 do PRD.

## Objective
Drenar 60 cards vira uma página com teclado `1-4`, relearning no lote e flag de defeito, cujas notas o agente lê no fechamento e grava em lote por `record_review` -- em menos tempo que o `/revisar` no chat, sem mudar o caminho de escrita do FSRS.

## Context
`fsrs_queue.py --list` já emite o lote em JSON (`card_id, frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha, area, tema, selection_reason, bucket`) e `--record CARD_ID --rating --reason` grava por `record_review` (balanceador, blackout, `reason_servido`, evento de reforja). O contrato `revisao-calibrada` v1.3 define DRENAR (nota e tally, silêncio -- Invariante F) e a Revisão Direcionada de fechamento no chat. O Artifact runtime oferece a capability `db` (doc store JSON que o agente lê de volta com `ArtifactData`), o que responde à Open Question do PRD. Decisões do usuário: desktop-first; sem botão "aposentar".

## Definition of Done
1. `python tools/fsrs_queue.py --export-player [--limit N] [--out tmp/player_<data>.json]` grava o lote do dia (mesmos buckets/ordem do `--list`, teto do dia respeitado) em JSON com `sessao`, `gerado_em`, `cards[]` e **sem** campo que não vá para a tela; e `--build-player --lote ARQ [--out artifacts/player-<data>.html]` injeta o lote em `core/templates/player.html` num `<script id="lote" type="application/json">`.
2. `core/templates/player.html` (página autocontida, contrato de renderização do projeto): frente -> `Espaço` vira -> `1-4` nota (toque: 4 botões grandes); nota `< 4` recoloca o card no fim do lote (relearning) **sem** gerar segunda nota gravável; `D` marca defeito com motivo (texto curto) e pula; contador `feitos/total`, tally por nota e tempo decorrido; estado persiste em `claude.use("db")` na coleção `sessoes/<sessao>/notas` (1 doc por card: `{card_id, rating_primeira, ts, defeito?, motivo?}`) e sobrevive a refresh (recarrega o progresso do `db`); com `db` indisponível (`null`), a página mostra um bloco de texto com as notas para colar no chat (fallback declarado, não silencioso).
3. `python tools/fsrs_queue.py --record-lote ARQ.json [--apply --expect N]`: dry-run lista `card_id -> rating` e o N; `--apply` grava exatamente N revisões via `record_review` com `selection_reason` do export (1 por card, ignora duplicatas com WARN), e envia os `defeito` para `db.marcar_reforja(card_id, motivo, origem='player')`; COUNT-ASSERT pós: `fsrs_revlog` cresce N.
4. `tools/test_fsrs_queue_player.py`: export sem campos extras, build injeta o JSON, `--record-lote` com `--expect` errado não grava, duplicata de `card_id` gera 1 revisão, defeito vira marca; `record_review` continua sendo o único write (asserção via allowlist: `fsrs_queue.py` não ganha tabela nova).
5. `.claude/commands/revisar.md` ganha a seção **"DRENAR no player"** (assinatura das 3 flags, rito: export -> build -> publicar com `capabilities: {db: {}}` -> usuário drena -> agente lê `ArtifactData` -> grava `tmp/player_<data>_notas.json` -> `--record-lote` -> Revisão Direcionada no chat sobre as notas 1-2); `core/contracts/revisao-calibrada-contract.md` -> **v1.4**: o player é superfície de DRENAR; Invariantes A (ensino não escreve FSRS), C (trava técnica em `record_review`) e F (silêncio no meio) preservados por construção; espelho regenerado.
6. Medição do critério 5 do PRD registrada em `history/`: minutos por 60 cards em 3 sessões no chat (histórico) x 3 no player; se o player não for mais rápido, a spec falha (não se "ajusta" a régua).
7. Craftsmanship: `auto_check --changed` PASSED (D5, allowlist, F43); zero LaTeX/setas Unicode; página com `.wrap` único, tokens de tema, teclado com foco visível, `prefers-reduced-motion` respeitado.

## Scope
`tools/fsrs_queue.py` (3 flags), `core/templates/player.html`, `tools/test_fsrs_queue_player.py`, `pytest.ini`, `.claude/commands/revisar.md` (+ espelho), `core/contracts/revisao-calibrada-contract.md`.

## Anti-scope
Sem botão "aposentar" (cortado no discover; aposentar é `reforja.py`/`cards_prune.py`). Sem Revisão Direcionada dentro da página. Sem gravar FSRS a partir da página (a página nunca chama `record_review`; só o CLI, no fechamento). Sem Anki. Sem `sample`/`mcp` capabilities no v0. Sem mudar o teto diário nem a ordem dos buckets.

## Technical Decisions
- **`db` capability, não `artifact` (republish)**: as notas são "dado que Claude lê depois" -- exatamente o caso de `db`; republicar a página a cada nota seria 60 publishes e conflito garantido. Coleção por sessão evita colisão entre dias; `ArtifactData` lê tudo de uma vez no fechamento.
- **Só a primeira nota é gravável**: a página guarda `rating_primeira` e nunca sobrescreve; o relearning é estado local do lote (memória `feedback_relearning_intrasessao`: a 1ª nota grava, as demais só recirculam).
- **`--record-lote` com dry-run + `--expect`**: mesmo rito de `cards_prune.py`; a página é untrusted input (shared data), então o CLI valida `card_id` contra o export e `rating in 1..4` antes de gravar.
- **Fallback sem capability = texto para colar**, declarado na tela: cobre celular sem grant e preview; nunca perde o lote em silêncio.

## Applicable Patterns
- `db-access-layer.md` (marcar reforja via `db.marcar_reforja`), `error-insertion-pipeline.md` (COUNT-ASSERT), `warn-first-check.md` (duplicata = WARN, não bloqueio).
- Novo padrão a registrar depois do 1º uso: **"Artifact como superfície de entrada + CLI como único writer"** (candidato a `.vibeflow/patterns/artifact-input-surface.md`).

## Risks
- Capability `db` negada ou indisponível na sessão do usuário -> fallback de texto (DoD 2); medir na 1ª sessão real.
- Card com HTML/aspas quebrando o JSON injetado -> escapar `</script>` e usar `JSON.parse(textContent)`; teste com card sintético contendo `<`, `>`, aspas.
- Tempo por 60 cards não cair -> a régua é a do PRD; sem número, a parte não fecha.

## Dependencies
Nenhuma dura. Recomendado executar logo após a Parte 1 para colher o ganho de tempo enquanto as Partes 2-4 andam.
