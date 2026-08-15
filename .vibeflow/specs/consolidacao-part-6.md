# Spec: consolidacao-part-6 — wiring, fusões com absorção e o check de alcançabilidade v0

> PRD: `consolidacao-alcancabilidade.md` · D4 do handoff (construído-e-nunca-conectado) + consertos 9/10/11 + fusões §4. Aqui nasce o artefato reusável do ciclo.

## Objective
O que ficou vivo fica ALCANÇÁVEL — e o harness ganha o check que pergunta "alguém chega aqui?".

## Definition of Done
1. [ ] `check_fk_orphans` vira **check 10** do `auto_check.py` (warn-first, gatilho junto dos checks de card).
2. [ ] `pytest.ini` ganha `test_variancia.py` (CLI vivo `/performance` com teste que não rodava em harness nenhum).
3. [ ] **Fusões com absorção** (fundir sem absorver rebaixa rigor):
   a. `apply_reforja.py` + `recurate_cards.py` → UM reescritor in-place canônico: fica o `recurate_cards` (interface do workflow oficial) ABSORVENDO o gate 3 de atomicidade + all-or-nothing do apply_reforja; `apply_reforja` morre; `curar-cards.md`/refs atualizadas; testes dos dois consolidados.
   b. `audit_integrity.py` → morre; seu check de schema (PRAGMA table_info × colunas obrigatórias) absorvido pelo `check_fk_orphans.py` (que já é o check 10).
   c. `migrate_dificuldade.py` → morre; as 3 colunas `dificuldade*` entram na `CREATE TABLE` do `init_db.py` (um `ipub.db` recriado do zero nasce ÍNTEGRO — teste: init_db em tmp + PRAGMA confere colunas).
4. [ ] **Check de alcançabilidade v0** (o artefato reusável): `tools/reachability_check.py` — para cada `tools/*.py` e `app/**/*.py`: existe ≥1 referenciador vivo (pytest.ini · .claude/ · .agents/ · hooks · outro .py · contrato)? Órfãos → WARN com lista (warn-first; ledger tag `reachability`). Roda no `auto_check --all`. Design PORTÁVEL (paths/configuração no topo) — segundo plugue será o daktus-hub.
5. [ ] `AGENTE.md §7` declara o real: `curar-cards.md` no índice de workflows + tabela de CLIs cobrindo os ~21 vivos fora dela (gerar a tabela do próprio reachability_check p/ não digitar à mão).
6. [ ] `pytest` verde; rodar `reachability_check` no repo pós-parts-1-5 → a lista de órfãos esperada é VAZIA ou justificada linha a linha no relatório do audit.

## Scope
`tools/auto_check.py` · `tools/reachability_check.py`✚ · `tools/recurate_cards.py` · `tools/apply_reforja.py`✝ · `tools/audit_integrity.py`✝ · `tools/check_fk_orphans.py` · `tools/migrate_dificuldade.py`✝ · `tools/init_db.py` · `pytest.ini` · `AGENTE.md §7` · `curar-cards.md` · testes.

## Anti-scope
NÃO análise estática de imports profunda (grep de nome basta p/ v0); NÃO endurecer nada a BLOCK; NÃO generalizar para outros repos NESTE ciclo (portátil ≠ instalado).
