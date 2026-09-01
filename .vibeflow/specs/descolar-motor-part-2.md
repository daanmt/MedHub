# Spec: Descolar part-2 — escopo de escrita vira TESTE; mortos morrem de verdade (F49 · F51 · F50)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.
> Melhor custo/benefício pontual do dossiê (handoff §5): um teste de ~40 linhas converte F49 de
> prosa em código e de quebra blinda F51 e F52(b).

## Objective

Nenhum arquivo escreve em tabela do `ipub.db` fora de uma allowlist declarada e TESTADA; os dois
mortos-que-parecem-vivos morrem com lápide; e a classe "import dangling mascarado por .pyc" ganha
sensor.

## Context

F49: `AGENTE.md:170` declara writer-gate que 5 arquivos violam (`insert_card_base.py:65`,
`registrar_sessao_bulk.py:115,132`, `normalize_taxonomia.py`, `dedup_taxonomia.py`) e
`test_writer_gates.py` testa OUTRA coisa (o docstring admite). F51: `auto_recurate_duplo_ask.py`
é writer de cards que BYPASSA `card_checks`, com dep fantasma (`google.generativeai`) e BOM que
quebra `ast.parse` — inerte por acidente, 0 refs. F50: `autopsia_simulados.py`, 852 linhas
quebradas desde a s156 (importa módulo deletado), mascarado por `.pyc` órfão — 5 dias
"vivo". O padrão do teste allowlist já está provado em `test_revisao_calibrada.py:127-149`.

## Definition of Done

1. [ ] `tools/test_writer_allowlist.py` (novo, registrado no pytest.ini): varre `tools/**.py` +
       `app/**.py` (leitura com `utf-8-sig` — lição do BOM/F51) por `INSERT INTO|UPDATE|DELETE FROM`
       sobre tabelas do `ipub.db` e FALHA se o par (tabela, arquivo) não estiver na allowlist
       declarada (os writers reais do §3 do handoff). Passa HOJE com a allowlist inicial.
2. [ ] Sabotagem verificada no implement (docstring com data): arquivo novo com `INSERT INTO
       flashcards` fora da lista → teste FALHA nomeando arquivo e tabela.
3. [ ] `tools/auto_recurate_duplo_ask.py` e `tools/autopsia_simulados.py` DELETADOS; lápide =
       entrada de RESOLUÇÃO nos achados F50/F51 da `AUDITORIA_MEDHUB.md` (padrão F22-F26
       "RESOLVIDO") + linha tombstone onde o index citar; `.pyc` órfãos correspondentes removidos.
4. [ ] Check de import-dangling no `auto_check`: `ast`-parse de cada `tools/*.py` (utf-8-sig),
       resolve `import tools.X`/`from tools.X` contra o disco; módulo inexistente = WARN nomeado
       (nasce WARN — política s106/107). NÃO executa os CLIs (ast-only, sem side effects).
5. [ ] Suite verde; `sync_skills --check` exit 0 (nenhuma skill citava os mortos — verificar);
       craftsmanship: zero `import sqlite3` novo fora de `db.py`.

## Scope

`tools/test_writer_allowlist.py` (novo) · `tools/auto_check.py` (import-check) · deleção dos 2
mortos · `AUDITORIA_MEDHUB.md` (status F50/F51) · `pytest.ini` (≤6 files; deleções contam leve).

## Anti-scope

- Reescrever `auto_recurate_duplo_ask` sob card_checks (morre sem substituto; renasce por demanda
  real, sob gate — decisão do PRD).
- Consertar os writers listados no F49 para passarem por caminho único (a allowlist DECLARA o
  estado real; estreitar a lista = decisão futura com o painel).
- `compileall` executável (ast-only — não rodar código de CLI no check).

## Technical Decisions

- Allowlist = ESTADO REAL de hoje (writers verificados pela s160), não o ideal do AGENTE.md — o
  teste trava o PERÍMETRO primeiro; encolher o perímetro é passo 2 consciente. `AGENTE.md:170`
  ganha a redação verdadeira (aponta a allowlist como fonte).
- Deleção com lápide, não `_archive/` (o repo já tem convenção de tombstone; arquivo morto em
  archive vira ruído de grep).

## Applicable Patterns

- `db-access-layer.md` · `warn-first-check.md` (import-check nasce WARN).

## Risks

- Regex de SQL pega string em comentário/docstring → mitigação: mesmo trade-off do padrão provado
  em test_revisao_calibrada (falso-positivo raro é allowlist-ável com 1 linha; falso-negativo é
  que custa).

## References

- `test_revisao_calibrada.py:127-149` — o padrão a replicar.
- `ai-eng/HANDOFF-MEDHUB-COLA.md` §4 F49/F50/F51, §5 (relações).
