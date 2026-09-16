---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 5
slug: plano-ssot-e-cards-v2-part-5
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/cards_prune.py
  - tools/test_cards_prune.py
  - tools/test_writer_allowlist.py
  - .claude/commands/engenharia-cli.md
---

# Spec -- Parte 5: poda de flashcards aposentados (`tools/cards_prune.py`)

> Deriva do PRD `plano-ssot-e-cards-v2` (P5). Permit do usuario em 16/09/2026: *"existem cards ruins, 'aposentados' -- que sinceramente se nao derem pra ser aproveitados podem ser excluidos"*; lote 1 aprovado por pergunta direta: **apagar os 125 aposentados sem revlog e sem marca de reforja** (de 192; os 67 com historico ficam).

## Objective
Dar ao banco um caminho unico, auditavel e reversivel de EXCLUSAO de flashcards (hoje so existe reescrita in-place), e executar o lote 1.

## Definition of Done
1. `python tools/cards_prune.py --criterio aposentados-sem-historico` (dry-run, default) imprime N e os ids, sem escrever no banco.
2. `--apply` exige `--expect N` igual ao N medido no momento da execucao; divergencia = recusa (exit 2) sem escrever.
3. `--apply` roda `tools/backup_db.py` ANTES de apagar e exporta as linhas de `flashcards`, `fsrs_cards`, `fsrs_revlog` e `reforja_marks` dos ids para `artifacts/backups/pruned_<timestamp>.json`; so entao apaga, em UMA transacao, na ordem revlog -> marks -> fsrs_cards -> flashcards. COUNT-ASSERT pos: `flashcards` diminui exatamente N e nenhum dos ids sobrevive.
4. `tools/test_cards_prune.py` (db sintetico em tmp) cobre: selecao do criterio, dry-run sem efeito, recusa por `--expect` errado, apply correto (N removidos nas 4 tabelas, export com N entradas, demais linhas intactas, zero orfaos FK); registrado em `pytest.ini`.
5. `tools/test_writer_allowlist.py` lista o novo writer; `.claude/commands/engenharia-cli.md` documenta TODAS as flags; `sync_skills --check` OK; `auto_check --changed` PASSED.
6. Lote 1 executado no `ipub.db` real: dry-run = 125, apply com `--expect 125`, `check_fk_orphans.py` limpo; numero e caminho do export no `history/session_183.md`.

## Scope
`tools/cards_prune.py` (novo), `tools/test_cards_prune.py` (novo), `tools/test_writer_allowlist.py` (allowlist), `pytest.ini` (registro), `.claude/commands/engenharia-cli.md` (+ espelho gerado).

## Anti-scope
Nao toca `stability`/`difficulty`; nao apaga erros (`questoes_erros`); nao apaga aposentados COM historico; nao reescreve card (isso e `recurate_cards.py`); nao cria flag para pular o backup.

## Technical decisions
- Funcoes puras sobre `sqlite3.Connection` (`selecionar`, `exportar`, `apagar`) + `executar()` que recebe `backup_fn`; o CLI injeta o backup real (subprocess de `backup_db.py`), o teste injeta um stub. Sem flag "sem backup".
- Criterio v0 unico: `aposentados-sem-historico` (needs_qualitative=2 AND sem revlog AND sem reforja_marks) + `--ids` explicito para lotes triados a mao. Novos criterios entram por nome, nunca por SQL livre.
- `PRAGMA foreign_keys` e OFF por default no projeto: a ordem de delecao e o COUNT-ASSERT substituem a cascata.
