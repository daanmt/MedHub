# Spec: medhub Fase 0 · Lote 0 — Part 3: catraca de cláusulas derivada do HEAD + CLI check coerente

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/E-testes-harness.md` §Espelhos e catracas (`clausulas_check`, "A 128ª", `cli_signature_check`)
> Parte 3 (de 7). Depois da part-1 (mesmo arquivo `tools/auto_check.py`).
> Repo-alvo: medhub (implement + audit no loop vibeflow dele). Código conferido em leitura @ `6d0239a`; contagem rodada em leitura (`python -B -X utf8 tools/clausulas_check.py --orfas --portador banco-emed`) em 2026-10-10.

## Objective

A contagem de cláusulas órfãs deixa de ter base digitada à mão: o commit que cria órfã nova é bloqueado contra a contagem do `HEAD`, a 128ª órfã recebe terminal, e o `cli_signature_check` passa a dizer que é BLOCK.

## Context

- **Catraca com folga.** `tools/clausulas_check.py:80-87`: `BASE_ORFAS = 127`, "subir exige editar ESTA linha no mesmo commit… descer é livre". `catraca(orfas, base)` (`:90-97`) só devolve mensagem de WARN; o `auto_check` imprime `[WARN] CLAUSULA_ORFA_SUBIU` sem tocar `all_passed` (`auto_check.py:1260-1265`). [E] reconstruiu por commit: a contagem caiu para 126 (s216–s218) e a base não desceu; a 127ª entrou em `4122645` (s219) escondida pela folga; a 128ª em `953124c` (s221). Medido hoje: **ORFAS 128**; a 128ª é `.claude/commands/banco-emed.md:154` (o parágrafo `> **Figura (s221, P22):** a URL da <img> do enunciado sai em figuras ...`).
- **Severidade.** No check 29 só `gate_inexistente` e `nv_sem_data` são BLOCK ("base ZERO por construção", `auto_check.py:1228-1234`); órfã é WARN porque "o passivo nasce em 271". Uma órfã **nova** em relação ao `HEAD` também tem base zero por construção — o mesmo argumento.
- **Cabeçalho que mente.** `tools/cli_signature_check.py:21-23` ("WARN-first … nasce WARN, vira BLOCK quando a base zerar"), `:150` (`description="... WARN-first, exit 0 sempre"`) e `:165` (`"-- WARN, nao bloqueia"`). Mas o check 26 do `auto_check` (`:1146-1180`) imprime `[BLOCK] CLI_ASSINATURA (D5)` e faz `all_passed = False` desde a s177 (base zerou).
- Candidato a terminal da 128ª: existe `tools/test_emed_api.py::test_figura_do_enunciado_vem_do_statement_html_e_viaja_como_url` (`:467`). O registro de gates do `clausulas_check` é derivado de `auto_check` + `test_*` de `tools/`.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: lembrar de editar uma constante à mão e um cabeçalho que diz o contrário do gate. Nenhuma fricção virtuosa é tocada.

## Definition of Done

1. [ ] **Contagem por revisão.** `tools/clausulas_check.py` ganha `extrair_texto(texto, portador)` (o `extrair(path)` atual passa a delegar a ele) e `orfas_na_revisao(rev, root=None)` que conta órfãs sobre o conteúdo dos portadores numa revisão do git (`"HEAD"` ou `":"` = índice), lido por `git show`/`git cat-file`. `tools/test_clausulas_check.py::test_catraca_derivada_do_head` monta um repo git sintético em `tmp_path` (padrão `tools/test_emed_api.py:363-367`), commita um portador com N órfãs e prova: índice com N+1 → mensagem de BLOCK; com N ou N−1 → `None`; sem `HEAD` (repo vazio) → `None` com aviso, nunca exceção.
2. [ ] **Sem base digitada.** A linha `BASE_ORFAS = 127` some (ou fica só como fallback documentado para repo sem `HEAD`); `catraca` recebe a base calculada. `git grep -n "BASE_ORFAS = 127" -- tools/` → vazio.
3. [ ] **Severidade por modo.** No `--staged` (pre-commit), órfãs(índice) > órfãs(`HEAD`) imprime `[BLOCK] CLAUSULA_ORFA_SUBIU` e faz `all_passed = False`; no `--changed`/`--all`, a comparação árvore × `HEAD` continua WARN. A decisão de severidade mora numa função pura do `clausulas_check` (ex.: `severidade_catraca(modo)`), testada em `test_clausulas_check.py`.
4. [ ] **A 128ª com terminal.** O parágrafo "Figura (s221, P22)" de `.claude/commands/banco-emed.md` recebe terminal: `<!-- CHECK: test_figura_do_enunciado_vem_do_statement_html_e_viaja_como_url -->` se o implementador confirmar, lendo o teste, que ele prova a frase; senão `<!-- NAO-VERIFICAVEL: motivo (revisar: AAAA-MM-DD) -->`. `python tools/sync_skills.py` e `python tools/sync_skills.py --check` (exit 0) no mesmo commit. `python -X utf8 tools/clausulas_check.py` mostra `ORFAS (sem terminal) : 127` (colar a saída no audit).
5. [ ] **Cabeçalho coerente.** `tools/cli_signature_check.py:21-23`, `:150` e `:165` dizem o que o gate faz: o CLI avulso sai 0 e informa; o check 26 do `auto_check` bloqueia o commit. `git grep -n "nao bloqueia\|exit 0 sempre" -- tools/cli_signature_check.py` → vazio.
6. [ ] **Suíte verde e craftsmanship:** `python -m pytest tools/ -q` passa; nenhuma violação dos Don'ts de `.vibeflow/conventions.md` (espelho em `.agents/skills/` só por `sync_skills.py`); o comentário da catraca e o do check 29 explicam por que o delta nasce BLOCK (base zero por construção, mesma razão de `gate_inexistente` — `AGENTE.md §6`, "regra nova nasce WARN e só vira BLOCK quando a base zerar").

## Scope

`tools/clausulas_check.py`, `tools/auto_check.py` (só o bloco do check 29 e o comentário), `tools/test_clausulas_check.py`, `tools/cli_signature_check.py` (só textos), `.claude/commands/banco-emed.md` (só o terminal), `.agents/skills/source-command-banco-emed/SKILL.md` (gerado por `sync_skills.py`). **Budget: 6 arquivos.**

## Anti-scope

- **Fronteiras:** design no ai-eng, implementação no medhub.
- **Nada que mude conteúdo clínico, FSRS ou o hub publicado.** Em `banco-emed.md` só entra o comentário-terminal; o texto da cláusula não muda (o conserto de figuras é o P5, Lote 1).
- Não anotar as outras 127 órfãs; não mudar o detector léxico (`DEONTICO`), nem a regra de `gate_inexistente`/`nv_sem_data`, nem o check 26.
- Não mudar o exit code do `cli_signature_check.py` avulso.

## Technical Decisions

1. **Base = `HEAD`, comparada ao índice**, em vez de base = último selo. O `HEAD` é determinístico e está sempre disponível no pre-commit; o selo é ritual de fechamento e pode estar sessões atrás. Descer continua livre (o próximo `HEAD` já é menor). Ler o **índice** (`git show :<path>`), não a árvore, evita que órfã não-staged de outro agente bloqueie um commit alheio (dois agentes compartilham a árvore — `AGENTE.md §10`).
2. **BLOCK só para o delta**, WARN para o passivo — mesmo critério que já faz `gate_inexistente` nascer BLOCK.
3. **Custo**: ~30 portadores × `git show` por commit. Se passar de ~2 s, usar um único `git cat-file --batch`. Tempo impresso pelo `run_command`.

## Applicable Patterns

- `tools/test_emed_api.py:363-367,370-378`: repo git sintético em `tmp_path` (`git init -q`, `git -C <repo> add`).
- `tools/clausulas_check.py` `catraca` (PURA) e o padrão "função pura no módulo, `auto_check` só orquestra" (`.vibeflow/patterns/warn-first-check.md`).
- `AGENTE.md §10.3`: quem edita skill roda `sync_skills.py` e `--check` no mesmo commit.

## Risks

- **"O commit desta parte é bloqueado pela própria catraca."** → Não: `HEAD` tem 128 e o índice terá 127.
- **"Repo raso ou primeiro commit."** → Sem `HEAD`: aviso e sem BLOCK (DoD 1).
- **"Carriers renomeados entre HEAD e índice."** → A contagem é total (soma de todos os portadores da revisão), não por arquivo.
- **"O CHECK escolhido não prova a frase."** → DoD 4 manda ler o teste antes; na dúvida, `NAO-VERIFICAVEL` com data.

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-1.md` (mesmo `tools/auto_check.py`; o pre-commit já roda os checks "sempre" em todo commit).
