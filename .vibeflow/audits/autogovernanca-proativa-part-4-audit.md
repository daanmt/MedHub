## Audit Report: autogovernanca-proativa-part-4

**Verdict: PASS**

Auditado em 2026-07-04 contra `.vibeflow/specs/autogovernanca-proativa-part-4.md`.
Dependências satisfeitas: Partes 2 e 3 auditadas PASS nesta sessão.
Testes: suíte central (Partes 1-4) + harness de autonomia verdes; `auto_check --all` exit 0; `ipub.db` byte-idêntico.
Critical Gate: limpo.

### DoD Checklist
- [x] **1 — C1 matching de tema estável** — `tools/day_plan.py::_material_do_tema` (`day_plan.py:242`) usa igualdade normalizada (`_norm_tema` = casefold + trim + colapso de espaços), ignora temas vazios (`if tt and _norm_tema(tt)==alvo`) e faz early-return no 1º match. Testado: `day_plan.py --difficulty Hepato "Hepatites Virais"` em runs repetidos → `material_indicado` idêntico ("resumo"/"resumo", ESTÁVEL).
- [x] **2 — G5 precedência preservada** — material extensivo **nunca** sobrescreve nota explícita: o floor só aplica quando `nota_usuario is None` (`day_plan.py:288`), aplicando `max(nota_inferida, 9)` (degrau **D10**, não D8) + `deep_research: True` no retorno. Testado em db temp: tema extensivo (Pediatria/Cuidados Neonatais) sem nota → D10, nota_efetiva 9, deep_research True; com nota explícita 4 (usuario) → **mantém 4, degrau D5, deep_research False**.
- [x] **3 — C4 heurística recalibrada** — `tools/cronograma.py:179` troca o gatilho largo `tipo_norm=='teoria'` por menção textual a "Extensivo"/"Livro Digital Completo" **E não-revisão** (docstring inline documenta o critério e o porquê). `--rebuild` regenerou `core/cronograma/grade.json` mantendo **n_tasks=352 e total_questoes=10218**, com distribuição equilibrada: **155 extensivo / 197 resumo = 44.0%** (< 60%, era 79.3%).
- [x] **4 — Regra única D10 nos 3 artefatos** — a frase "material extensivo ou inferência sem nota explícita → degrau D10 + dever de Deep-Researchness; a nota explícita do usuário (fonte=usuario) sempre vence (precedência input > pergunta > inferência)" aparece **verbatim** (verificado por `grep -F`) em `tools/day_plan.py` (docstring de `difficulty_report`), `core/contracts/revisao-calibrada-contract.md` (Cláusula 3) e `AGENTE.md §1.2`.
- [x] **5 — R6 governança formalizada** — `AGENTE.md` ganhou **§1.3 real** "Reflexo Autônomo de Validação (Auto-Linter Reflex)", movido para fora do §1.2 (era um bullet interno com auto-referência quebrada). A tabela §7.4 registra `auto_check.py`, `setup_hooks.py` e `sync_skills.py`. A §6 ganhou 2 decisões: "Harness autônomo staged-only + warning-first" e "Fonte canônica de skills = `.claude/commands` + espelhos gerados".
- [x] **6 — Craftsmanship (suíte e harness verdes)** — os checks documentais de `test_revisao_calibrada.py` (`test_contrato`/`test_agente`/`test_degrau_mecanico`, que fazem grep de strings do contrato/AGENTE) continuam passando após as edições ("TODOS OS CHECKS PASSARAM (Partes 1-4)"). `python -X utf8 tools/auto_check.py --all` → exit 0. `day_plan.py` roda sem exceção (smoke exit 0).

### Pattern Compliance
- [x] **agent-workflow-protocol + AGENTE §7.4/§6** — segue. Os 3 CLIs novos entram na tabela §7.4 (fonte fiel); as 2 decisões entram na §6. §1.3 vira seção real, corrigindo a auto-referência.
- [x] **revisao-calibrada-contract.md** — a regra única D10 casa com a Cláusula 3 (degraus D10/D8/D5/D2 preservados) e a precedência input>pergunta>inferência da Cláusula 2; o floor 9 mapeia corretamente para D10 (`_degrau_de(9)=="D10"`).

### Convention Violations
Nenhuma. `snake_case` (`_norm_tema`, `_material_do_tema`); pt-BR; degradação graciosa (`_material_do_tema` cai para "resumo" em qualquer exceção de `load_grade`). O `import sqlite3` de `day_plan` não foi tocado (não existe — usa `app.utils.db`).

### Critical Gate
✅ **Clean — no destructive operations detected.** Nenhum gatilho do catálogo no diff de código/doc (sem `sqlite3`/DROP/DELETE/subprocess/secret). `core/cronograma/grade.json` é regenerado pelo `--rebuild`: mudaram só `material_indicado` (flips da recalibração) e `_meta` (timestamps/sha da extração) — não é migration nem `.sql`.

### Nota de decisão (C4)
A Technical Decision citava "menção a Extensivo/Livro Digital Completo E ausência de 'Resumo'". "Resumo" ocorre 694× no PDF (estrutural, não discriminante) — usá-lo zeraria a marcação. Adotei a **contraparte semântica real**: menção a "Extensivo"/"Livro Digital Completo" E **não-revisão** (`revis[ãa]o`), mantendo a exigência de menção textual explícita da TD e ancorando no DoD mensurável (< 60% → obtido 44%). Registrado no docstring de `cronograma.py` e em `.vibeflow/decisions.md`.

### Próximos passos
**Ready to ship.** Partes 1-4 do PRD de Autogovernança estão todas PASS. Pronto para o commit final de tudo, como o usuário pediu.
