# Session 113 -- F33 resolvido: sync mecânico de conclusão real do cronograma (xlsx Drive)

**Data:** 2026-07-08
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 112 (DM Complicações Crônicas)

---

## O que foi feito

**Trigger:** operador pediu o plano do dia; o boot recomendou "próximos temas: MFC, Imunizações, Apendicite Aguda" (S12) -- o operador contestou, essas tarefas já tinham sido feitas. Verificação ao vivo via `download_file_content` (MCP Google Drive) + `openpyxl` na planilha `Cronograma de Reta Final.xlsx` (marcador de conclusão = `cell.font.strike`) confirmou: MFC/Imunizações (Teoria I-II) e Apendicite (Teoria+Revisão) estavam riscados (FEITOS); o pendente real de S12 era outro conjunto (DITC II, Distúrbios do Potássio, Cefaleias+Epilepsias, HAS Pt.2 + 2 blocos de Revisão por Questões). Registrado como achado **F33** no ledger.

**Ciclo vibeflow completo (papel: eu implemento, ver "virada de papel" s110):**
1. **`/discover`** -- PRD em `.vibeflow/prds/cronograma-sync-conclusao-drive.md`. Discovery com 2 perguntas (gatilho de sync = 1x/dia-calendário; snapshot gitignored).
2. **`/gen-spec`** -- durante a leitura do código, descoberta importante: o PRD assumia que o "único write permitido" era o ponteiro de texto `Próxima = SNN` (`cronograma-contract.md` Cláusula 5 v1.0), mas isso já estava **deprecado** desde 06/07 -- existe `preparacao_estado` (tabela chave/valor no `ipub.db`, PRD `orquestracao-preparacao` part-1) que já substituiu o texto, e `day_plan.py` já emitia `[WARN] POSICAO_VIA_TEXTO (deprecado)` quando caía no fallback. O contrato nunca foi corrigido quando o SSOT migrou -- mesma classe de drift doc↔código do F33 original. Spec desviou do PRD: reusar `preparacao_estado` (nova chave `cronograma_conclusao_drive`) em vez de criar arquivo `.json` novo.
3. **`/implement`** -- 6 arquivos (orçamento exato): `tools/cronograma.py` (`--sync-drive`: parse `cell.font.strike` + matching por `(semana, tema normalizado via unicodedata, tipo_norm)` -- índice de task não bate 1:1 entre PDF e xlsx), `tools/day_plan.py` (`_conclusao_drive()` + filtro em `_cronograma_hoje()` + aviso em `render()`), `tools/test_orquestrador.py` (8 testes novos), `core/contracts/reconcile-contract.md` (W8), `core/contracts/cronograma-contract.md` (Cláusula 5 corrigida, v1.1), `AGENTE.md` (§2 passo 4, instrução mecânica de sync).
4. **`/audit`** -- **PASS**. 19/19 testes + `auto_check.py --changed` PASSED. Validado contra o xlsx real: 352 tasks, 119 concluídas -- resultado bate 1:1 com a apuração manual que originou o achado.

**Fechamento:** F33 marcado RESOLVIDO no ledger (mesmo molde do F29).

## Artefatos criados/modificados

- `.vibeflow/{prds,specs,audits}/cronograma-sync-conclusao-drive.md` -- ciclo vibeflow completo.
- `tools/cronograma.py` -- `--sync-drive` (`_norm_tema_xlsx`, `_parse_conclusao_xlsx`, `diff_drive`, `sync_drive`).
- `tools/day_plan.py` -- `_conclusao_drive()`, filtro em `_cronograma_hoje()`, aviso em `render()`.
- `tools/test_orquestrador.py` -- 8 testes novos (normalização, matching, staleness, integração).
- `core/contracts/reconcile-contract.md` -- condição W8.
- `core/contracts/cronograma-contract.md` -- Cláusula 5 v1.1 (write permitido corrigido) + Changelog.
- `AGENTE.md` -- §2 passo 4 (instrução de sync).
- `AUDITORIA_MEDHUB.md` -- F33 RESOLVIDO; próximos achados começam em F34.
- `.vibeflow/decisions.md` -- decisão + 2 pitfalls (contrato desatualizado; mojibake era artefato de console, não corrupção real do Drive).
- `ipub.db` (`preparacao_estado.cronograma_conclusao_drive`) -- snapshot real gravado (352 tasks). Local-only.

## Próximos passos

1. FSRS: 3 atrasados + 6 hoje, backlog 393 novos.
2. Próximo bloco de conteúdo real (S12, via sync automático): **DITC II** (Teoria -- revisão da Parte I + expansão Parte II, pedido do operador) + Distúrbios do Potássio, Cefaleias+Epilepsias, HAS Pt.2 + 2 blocos de Revisão por Questões.
3. Slot de simulado previsto ainda em S12 (ciclo de 4 semanas).
4. Débito arrastado: aula-base de Pré-Natal I ainda pendente.
