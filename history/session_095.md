---
type: session
sessao: 095
data: 2026-06-27 ~23:55 (sábado -- continuação da s094, mesmo dia)
area_foco: Forja os 21 flashcards da s094 + sistema de sync do cronograma (F1-F4) + fechamento formal
---

# Sessão 095 -- Flashcards do dia + Sync do Cronograma (F1-F4)

## Contexto
Sessão de **engenharia + cards** (sem questões novas), continuação direta da s094. Duas entregas: (1) **cunhou os 21 flashcards do dia** que ficaram pendentes da s094 (os elos já estavam mapeados no handoff -- só cunhar); (2) construiu o **sistema de sync do cronograma completo (Fases 1-4 do ultraplan s094)**, que desbloqueia o PRD de Revisão Calibrada. Acumulado mantém **4.112 (41% da meta-prova 10k)**.

## O que foi feito
- **21 flashcards forjados (#589-609)**, 5 erros-âncora via `insert_questao.py --cards-file` (driver UTF-8 p/ blindar acentos no shell): **Meningites 6** (glicorraquia relativa, Hib×TB, viral×herpes, quimioprofilaxia, pneumococo+vanco, neurocisticercose) · **Distúrbios Ácido-Base 5** (AG×BE, hiperclorêmica, Winter, gap osmolar, K na CAD) · **Pneumo Intensiva 4** (VC por peso predito, ART, prega vocal×estenose, máscara laríngea) · **Pé diabético 4** (foco cirúrgico>exame, revascularizar>amputar, ITB calcificado, mal perfurante) · **Hepatites 2** (HBV pós-exposição por anti-HBs, mutante pré-core). Todos `qualitative`, FSRS state 0. Eixo metacognitivo costurado = **bug nº1**.
- **Correção de convenção:** 2 temas criados em ASCII -> normalizados p/ acentuados, casando o nome do resumo (`Distúrbios Ácido-Base`, `Diabetes Mellitus - Complicações Crônicas`); cards seguem por `tema_id`.
- **Sistema de sync do cronograma -- F1-F4 (ultraplan `docs/plans/s094-ultraplan.md`):**
  - **F1** -- `tools/cronograma.py` (derivador único, read-only) + `core/cronograma/grade.json` (30 sem · 352 tasks · 10218q; versionado). `AREA_PDF_TO_CANON` (linchpin do JOIN). Subcomandos `--rebuild`/`--check`/`--json`/`--gap`/`--validate`. Validado: **S10=273, S11-28=6689/222**, 20/20 áreas, `--check` por sha256.
  - **F2** -- `--radar`: cruza performance × cobertura futura, fronteira pré/pós-ENAMED, flags 🔴/⚪/🟡/🟢. Normaliza rótulos sujos (W4: GO sinalizado, mojibake Obstetrícia) na leitura.
  - **F3** -- `day_plan.py`: troca o regex frágil por leitura da grade; resolve conteúdo×calendário (ponteiro `Próxima = SNN` + fallback nominal); boot mostra S11, temas e dois ritmos.
  - **F4** -- contrato `core/contracts/cronograma-contract.md` + skill `/cronograma` + patches `reconcile-contract.md` (W5-W7), `forgetting-curve-contract.md` (Boot 4ª fonte), `AGENTE.md` (§6/§7.3/§7.4).

## Achados
- **De S11, o cronograma cobre TODAS as 20 áreas antes do ENAMED** (Oftalmo S11/S20, Otorrino S14/S20, Ortopedia S14/S21) -- **corrige a premissa do ultraplan §b.4** ("Oftalmo/Ortopedia 0q no cronograma"). Gaps só surgem em posições tardias (de S26: Oftalmo ⚪, Otorrino 🔴).
- **Gap honesto (`--gap` de S11):** 4.112 + 6.689 = 10.801 a 100% -> os **10k cabem dentro do cronograma a 88% de execução**; 12k exige banco extra (+1.199). O gargalo é **execução**, não conteúdo (confirma o ESTADO).
- **`_find_resumo` (em `get_topic_context`) indexa só `especialidade`/`area`/`aliases` do frontmatter -- não o nome do arquivo nem o tema** -> resolução tema->resumo é fuzzy frágil (relaciona com "revisados=0/taxonomia poluída"). **Pré-requisito do `infer_nota` do PRD** -> fix aditivo = indexar `path.stem.lower()`.

## Decisões / fronteiras
- **Cronograma é read-only no db** (Cláusula 5 do contrato): zero write em `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log`; elo cronograma↔desempenho em memória (join por `AREA_PDF_TO_CANON`); único write = ponteiro textual `Próxima = SNN`. W5-W7 do reconcile nunca BLOCKING.
- Commits separados por fase: **F1 `4c73060`**, **F2+F3 `2cec796`**, **F4+fechamento** (este).

## Artefatos criados/modificados
- **Novos:** `tools/cronograma.py`, `core/cronograma/grade.json`, `core/contracts/cronograma-contract.md`, `.claude/commands/cronograma.md`, `history/session_095.md`.
- **Modificados:** `tools/day_plan.py` (integração), `core/contracts/reconcile-contract.md` (W5-W7), `core/contracts/forgetting-curve-contract.md` (Boot), `AGENTE.md` (§6/§7.3/§7.4), `HANDOFF.md`, `ESTADO.md`, `history/INDEX.md`.
- **`ipub.db`** (local-only): +21 cards (#589-609) + 5 erros (#362-366); 2 temas normalizados.
- Contadores: **364 erros · ~410 cards** (#609 último) · **51 resumos**.

## Próximo (s096)
**A) Implementar o PRD de Revisão Calibrada** (DESBLOQUEADO): `dificuldade` em `taxonomia_cronograma` + `infer_nota()` + fusão `/revisar`+`/refrescar`; **pré-req = fix `_find_resumo`**. **B) Semana 11** (estudo): FSRS vencidos + ≥100q. **C) FSRS:** drenar #554-609. **D) Carry-over:** sessão Cirurgia + `/schedule`.
