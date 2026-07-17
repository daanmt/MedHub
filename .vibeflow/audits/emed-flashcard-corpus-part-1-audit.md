# Audit Report: Corpus EMED — Colheita + Extração (Part 1)

> Auditado em 2026-07-17 · spec `.vibeflow/specs/emed-flashcard-corpus-part-1.md`

**Verdict: PASS**

## DoD Checklist

- [x] **1. CLI `--harvest` + `--query`** — `tools/emed_flashcards.py` com os dois modos. Testados: harvest processou 275; `--query "Colecistite"` -> fuzzy (43 cards), `"Imunizacoes"` -> exact (69), `"Endometriose"` -> exact (25).
- [x] **2. 275 decks em `resumos/<area>/Flashcards - <Tema>.pdf`, área correta, 0 misfiled/perdido** — verificado 275 PDFs no disco; report: `unmapped=0, collisions=0, empty=0, errors=0`. Spot-check: Endocrinologia (10 temas numéricos resolvidos), Colecistite->Cirurgia, Imunizações->Pediatria. Mapeamento de área derivado do layout real (`Clínica Médica/Infectologia|Psiquiatria` confirmados).
- [x] **3. Sidecar `.cards.json` {n,frente,verso}, watermark limpo, image-only flagado** — 275 sidecars, 7565 cards. **Resíduo de tag/watermark = 0 verificado sobre TODOS os 7565 cards** (0 frente com especialidade grudada, 0 `@livremedicina`, 0 URL/stock/atribuição). 89 cards resposta-imagem (verso vazio) sinalizados em `image_answer_cards`. `empty_decks=0`.
- [x] **4. `--query` exato/fuzzy/candidatos** — matcher normalizado (sem pontuação) + token-containment + difflib; ambiguidade -> candidatos. Casos: exato (Endometriose/Imunizações), fuzzy (Colecistite via substring, "Diabetes Complicacoes Cronicas", "Infarto...Supra"->IAMCSSST via nome completo), ambíguo ("Diabetes" -> candidatos).
- [x] **5. PDFs + `.cards.json` gitignored** — `.gitignore` +`*.cards.json` +`artifacts/emed_harvest_report.json`. `git check-ignore` confirma; `git status -- resumos/` vazio; 275 no disco, **0 rastreados** (`git ls-files`).
- [x] **6. ASCII/no-LaTeX + /workflows QA + auto_check --changed sem BLOCK** — 0 caracteres proibidos (§4.5); **QA workflow (35 decks, fan-out paralelo)** achou resíduo sistemático de tag que o scan determinístico não via -> corrigido -> re-verificado; `auto_check --changed` = **Todos os checks passaram** (0 BLOCK; 1 WARN de paridade `revisar.md` é pré-existente, não desta feature).

## Pattern Compliance

- [x] **error-insertion-pipeline / convenção `tools/`** — CLI standalone, `REPO_ROOT` via `Path(__file__).parent.parent`, saída JSON no stdout. **Read-only no `ipub.db`** (não importa `sqlite3`) — respeita a fronteira dura do spec.
- [x] **Política de PDF s086** — decks mantidos gitignored dentro de `resumos/` (IP EMED). Consistente.
- [x] **Convenção §4.5 (ASCII/no-LaTeX)** — `chr(0x2013)/chr(0x2014)` em vez de travessões literais; scan de chars proibidos = NONE.

## Convention Violations

Nenhuma.

## Critical Gate

- ✅ **Clean — no destructive operations detected.** Scan de triggers no tool = nenhum (0 `eval/exec/subprocess/os.system/secret/delete_all/destroy_all/purge`). Diff tracked = só `.gitignore` (+4). Ops de arquivo (`shutil.copy2`, `Path.unlink`) não disparam regra do catálogo; o `unlink` do auto-prune é **escopado** a órfãos `Flashcards - *` fora do source atual (gitignored, nunca código/tracked) — reviewed-safe.

## Notas

- **Bugs achados e corrigidos no implement** (rigor, não gaps residuais): (a) derivação de tema — estrutura tem 3 variantes (`<Tema>\<Tema>`, `<Tema>\1`, `<Tema>\<TemaCompleto>`); fixado para o nome mais completo com prune self-healing; (b) limpeza de tag — reescrita (noise-regex + strip de especialidade + common-affix guardado) após o QA workflow expor resíduo sistemático.
- **89 cards resposta-imagem** (verso vazio) são intrínsecos (diagramas/tabelas sem texto), sinalizados — não são defeito de extração. A Part 3 deve tratá-los (pular ou marcar).

**Ready to ship (Part 1).**
