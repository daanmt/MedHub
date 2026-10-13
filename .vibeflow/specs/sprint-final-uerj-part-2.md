# Spec: sprint-final-uerj -- part 2: `plano.py --sprint`, um dia por tarefa até 31/10

> PRD: `.vibeflow/prds/sprint-final-uerj.md` (Solution 1 e 2). Gerada em 13/10/2026 (s226).
> Decisões dele (13/10): capacidade 80 q/dia; simulados UERJ 2024, 2025, 2026 (cadernos 2017-2020 saem); ordem pelo
> peso UERJ do tema.

## Objetivo

Cada tarefa pendente do sprint ganha uma data de 13/10 a 31/10 que cabe em 80 q/dia; o que não cabe fica "fora do
sprint" com o motivo -- e o plano se recalcula ao rodar de novo.

## Contexto

`plano_tarefas` tem `semana_plano`/`ordem` e writers só em `tools/plano.py` (allowlist F49, COUNT-ASSERT). Medido em
13/10: 83 pendentes até a S7, ~2.568 q. Peso: `plano.faixa_uerj` e `PESO_BLOCO`.

## Definition of Done

1. `core/sprint.json` (versionado): `{"inicio":"2026-10-13","fim":"2026-10-31","capacidade_q":80,
   "simulados":{"892":"2026-10-17","891":"2026-10-21","890":"2026-10-25"},"cortar":[1798,1799]}`; o código lê só dele
   (nenhuma data ou número do sprint no código).
2. Coluna `dia_plano TEXT NULL` em `plano_tarefas` (DDL idempotente no `db.py`, como as colunas anteriores) e coluna
   lógica "fora do sprint" = `dia_plano NULL` + nota `sprint: fora (<motivo>)`. Writer novo só no `plano.py`, cadastrado
   na allowlist (`tools/test_writer_allowlist.py` verde).
3. Função PURA `plano.montar_sprint(linhas, config, hoje, peso)` -> `{dias: {data: [ids]}, fora: [{id, motivo}],
   cortadas: [ids]}`: simulados no dia fixo e sozinhos; demais pendentes das semanas <= 7 ordenados por
   (faixa UERJ alta > média > baixa > sem faixa, peso do bloco mais fraco, ordem atual do plano), encaixados no 1º dia
   >= hoje com vaga (soma de `q_da_tarefa` <= capacidade; tarefa maior que a capacidade ocupa um dia sozinha); dias
   passados nunca recebem tarefa. Testes em `tools/test_plano.py`: capacidade nunca excedida, simulado sozinho no dia,
   ordem por peso, determinismo, tarefa feita não entra, 2ª corrida igual = 0 mudanças.
4. CLI `plano.py --sprint` (dry-run default: tabela por dia com tarefas e soma, depois "fora do sprint" com motivo e as
   cortadas) e `--sprint --apply --expect N` (N = linhas cujo `dia_plano`/nota mudam; diverge = exit 2; backup fixado
   antes, como os outros writers em lote); `--cortar` dos ids de `cortar` com motivo "sprint final: fora dos simulados".
5. Assinatura do CLI na skill que já carrega o `plano.py` (`.claude/commands/cronograma.md`, + `sync_skills.py` e
   `--check`); `cli_signature_check` (D5) verde.
6. Artesania: sem SQL fora do `db.py`/`plano.py`; suíte inteira verde; `auto_check --changed` PASSED; nada gravado no
   `ipub.db` real pelo subagente (o `--apply` real é do principal).

## Escopo

`tools/plano.py`, `app/utils/db.py`, `core/sprint.json`, `tools/test_plano.py`, `tools/test_writer_allowlist.py`,
`.claude/commands/cronograma.md` (+ espelho gerado).

## Anti-escopo

Painel, hub, boot (parts 3-5); a trilha (`trilha.py`); tarefas sem semana e Fase 2; mudar `semana_plano`.

## Decisões técnicas

- `dia_plano` ao lado de `semana_plano` (não substitui): a semana segue sendo a origem e o histórico; o dia é a agenda.
- Rolamento sem estado: o `--sprint` de amanhã recomputa a partir de hoje com as pendentes de hoje; nada "atrasa".
- Peso do bloco mais fraco: do acerto acumulado das provas UERJ registradas (área Simulado) quando der para ler; senão
  `PESO_BLOCO`. Declarar no docstring qual foi usado.

## Riscos

- `faixa_uerj` sem prevalência para tarefa custom -> cai em "sem faixa" (último); testar.
- `q_previstas` fracionário (836,3) -> somar com `q_da_tarefa` (a régua do Painel), não o campo cru.
