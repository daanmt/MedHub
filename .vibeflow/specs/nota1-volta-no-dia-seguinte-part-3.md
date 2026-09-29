# Spec: nota 1 volta no dia seguinte -- part 3 (portadores, rito dos 3 passos)

> Origem: F140 e F32. A norma hoje prescreve o comportamento que as parts 1 e 2 mudam.

## Objetivo

Contratos, skills e ledger passam a descrever o sistema que existe: nota 1 volta no dia seguinte e o lote enche o saldo do teto.

## Contexto

`revisao-calibrada-contract.md:232` diz "o card volta hoje"; `revisar.md` trata "relearning que volta hoje" como esperado; `fsrs-management-contract.md` fixa `--new-limit 10` e lista 3 buckets (a fila usa 4). Revogar cláusula tem 3 passos no mesmo commit (AGENTE 10.10): declarar, lapidar no portador que o agente lê no ato, cadastrar o termo.

## Que fricção esta spec remove -- e ela é virtuosa ou viciosa?

Remove norma que contradiz o código: **viciosa** (o agente obedeceria cláusula morta). Nenhuma fricção de estudo é tocada.

## Definition of Done

1. `revisao-calibrada-contract.md`: linha da nota 1 na Cláusula 14 reescrita, lápide com data e motivo, versão do frontmatter igual à do corpo.
2. `fsrs-management-contract.md`: estado 3 descrito como legado; novos do lote = saldo (chat = 10); ordem com os 4 buckets; versão consistente.
3. `revisar.md` e `hub-backend.md` atualizados; `python tools/sync_skills.py --check` sai 0.
4. Termos cadastrados em `docs/MEMORIA-AUDITORIA.md` e o gate `CONTRATO_REVOGADO` PASSED.
5. Ledger: F140 e F32 com status RESOLVIDO; `python tools/selo.py` com 0 discordâncias.
6. Suíte completa verde e `auto_check --changed` PASSED.

## Escopo

- `core/contracts/revisao-calibrada-contract.md`, `core/contracts/fsrs-management-contract.md`
- `.claude/commands/revisar.md`, `.claude/commands/hub-backend.md` (espelhos gerados por `sync_skills`)
- `docs/MEMORIA-AUDITORIA.md`, `AUDITORIA_MEDHUB.md`

## Anti-escopo

- Rotação do ledger (spec própria).
- `docs/FUNDAMENTOS-APRENDIZAGEM.md` e `docs/research/`: documentos explicativos, não normativos.
- F141, F142.

## Decisões técnicas

- **Um commit para as 3 parts.** O rito exige declaração, lápide e cadastro juntos; separar o código da norma deixaria o repo contraditório entre commits.
- **F32 fecha junto.** A colisão era "duas camadas de reaprendizagem"; o motor deixa de ser uma delas.

## Padrões aplicáveis

- `patterns/agent-workflow-protocol.md`: skill é fonte única; espelho é artefato de build.
- `patterns/warn-first-check.md`: o gate de termo revogado casa substring literal; a lápide segue o formato já usado nos portadores.

## Riscos

- **Termo cadastrado que ainda aparece em linha ativa** bloqueia o commit. Mitigação: rodar o gate antes de cadastrar e depois.
- **Lápide fora do formato** vira falso positivo. Mitigação: copiar o formato das lápides vizinhas.

## Dependencies

- `.vibeflow/specs/nota1-volta-no-dia-seguinte-part-1.md`
- `.vibeflow/specs/nota1-volta-no-dia-seguinte-part-2.md`
