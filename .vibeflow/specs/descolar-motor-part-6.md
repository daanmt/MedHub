# Spec: Descolar part-6 — exit codes que não mentem + integridade de history/ (F60 · F58)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.
> "Funciona headless... ou PARA ruidosamente": exit 0 com 'BACKUP CORROMPIDO' no stdout é a
> antítese; o padrão certo já existe no repo (F27, `insert_questao.py:474`) e não generalizou.

## Objective

Os writers críticos param de sair 0 em falha, as degradações do day_plan deixam de ser
silenciosas, e um session log novo corrompido é acusado no commit em que nasce.

## Context

F60: `backup_db.py:104` imprime "BACKUP CORROMPIDO -- abortando" e sai **0**;
`importar_sessoes.py:60` sai 0 com 100% das linhas rejeitadas; 18/45 CLIs nunca retornam ≠0;
11 excepts silenciosos só no day_plan (plano pode sair sem zona/frieza/prescrição sem 1 aviso).
F58: `session_156.md` corrompido NO SSOT pela escrita da s156 (BOM + escapes comidos:
`\t`ools→tab, `pp/`, `uto_check`) — nenhum gate olha `history/`; o campo `Ferramenta:` do INDEX
é o que torna o swap test possível (preservar).

## Definition of Done

1. [ ] `backup_db.py`: qualquer aborto (integrity_check falho, cópia falha) → exit ≠ 0; teste
       com db corrompido sintético.
2. [ ] `importar_sessoes.py`: 100% das linhas rejeitadas → exit ≠ 0 (parcial: exit 0 + resumo
       com contagem de rejeitadas); teste.
3. [ ] `day_plan.py`: os excepts de degradação imprimem `[WARN] <componente>: <erro curto>` em
       stderr ao degradar zona/frieza/prescrição (mínimo: esses 3 componentes) — o plano continua
       saindo (degradação graciosa CONTINUA; só deixa de ser muda).
4. [ ] Check `history_integrity` no auto_check (WARN): `session_NNN.md` novo (mtime > último run
       ou N > máx do INDEX) sem BOM, sem bytes de controle fora de `\n\t`, com header mínimo
       (`# Sessão` ou equivalente do template) — pega a classe F58 no commit seguinte.
5. [ ] Suite verde; testes registrados; craftsmanship: mensagens ASCII; nenhum comportamento de
       degradação removido (fail-open preservado, só AUDÍVEL).

## Scope

`tools/backup_db.py` · `tools/importar_sessoes.py` · `tools/day_plan.py` · `tools/auto_check.py`
· teste novo (≤6).

## Anti-scope

- Os outros ~15 CLIs sem exit≠0 (viram candidatos no painel; generalizar = ciclo 2 com a lista).
- Reparar `session_156.md` histórico (corrompido "no git para sempre" — lápide; reescrever
  história é decisão do dono).
- Encoding-check retroativo da história inteira (só session NOVO).

## Applicable Patterns

- `warn-first-check.md` · convenção CLI do repo (argparse, exit simétrico — F27 como referência).

## Risks

- exit≠0 novo em `backup_db` pode quebrar chamador que ignorava falha → grep de chamadores no
  implement; se houver, ajustar o chamador no MESMO commit (falha de backup ignorada é o bug).

## References

- `insert_questao.py:474` (F27) — o padrão a generalizar.
- `ai-eng/HANDOFF-MEDHUB-COLA.md` §4 F58/F60.
