# Session 076 — CAD/EHH (7 erros) + regeneração completa dos 87 cards heurísticos órfãos + /revisar (fantasma Dengue C/D resolvido)
**Data:** 2026-06-04
**Ferramenta:** Claude Code (Opus 4.8 — 1M context)
**Continuidade:** Sessão 075

---

## O que foi feito

### Demanda 1 — CAD/EHH (Complicações Agudas do DM)
- Volume registrado: **34q / 27a (79,4%)** em Endocrino via `registrar_sessao_bulk.py` → acumulado **3.210 → 3.244**.
- 7 erros analisados com diagnóstico do elo metacognitivo quebrado → 7 cards qualitativos (IDs 406-412) via caminho `cards=` da `insert_questao()` (UTF-8, sem escaping de CLI no Windows).
- Resumo `Diabetes Mellitus - Complicações Agudas.md` turbinado: **+4 armadilhas** novas (Q1 hipo vs CAD em criança doente; Q3 convulsão DM1 = hipoglicemia/glucagon; Q4 tríade — cetose é o critério faltante; Q2 stem negativo do EHH) + 3 bullets integrados nos blocos. Linter limpo.

### Demanda 2 — Regeneração dos 87 cards heurísticos "restantes"
- **Causa-raiz:** a bankruptcy da s075 aposentou só os `needs_qualitative=1` (70 cards); **87 heurísticos com `nq=0` escaparam** e a `cards_regen_queue.py` herdou o filtro órfão (`nq=1`) → retornava vazio.
- **Fix infra:** critério da fila trocado para `quality_source='heuristic' AND needs_qualitative!=2`; docstring + `estilo-flashcard.md §Backfill` (reativada) atualizadas.
- **87 regenerados** qualitativamente em 4 ondas via `update_flashcard_fields` (preserva `card_id` → estado FSRS). Backup-first (`ipub_backup_20260604_135335.db`).
  - Onda 1 (25): áreas não-Cirurgia (Pneumo, Gastro, Infecto, GO, Hemato, Endo, Hepato, Nefro, Pediatria) — 24 regen + 1 duplicata (#276) aposentada.
  - Ondas 2-4 (62): bloco "[bulk] Cirurgia".
- **Resultado: 0 heurísticos ativos.** Fila FSRS 100% qualitativa. 93 cards meus auditados: 0 defeitos.

### /revisar — 15 cards (modo conversacional, lotes de 5)
- Ratings: 7×4, 3×2, 5×1.
- 🎯 **Card #394 (Dengue: grupo C 10 mL/kg/1h vs D 20/20min) resolvido** — falhava 2-3× (pendência vigiada da s075); cravado.

## Padrões de erro identificados
- **CAD/EHH:** 4 dos 7 erros (Q2,Q5,Q6,Q7) foram sobre armadilhas **já documentadas** no resumo → gargalo é aplicação sob pressão + leitura de comando negativo, não conhecimento. Cluster da insulina (Q1/Q3/Q5/Q6): fraqueza nos "portões" de quando NÃO insulinizar (hipoglicemia, K<3,3, sem-bolus pediátrico).
- **/revisar (novo, PALS):** diferenciação de taquicardias na criança é ponto fraco — TSV sinusal (tratar a causa) vs TSV (vagal→adenosina) vs bradicardia (adrenalina, não atropina). Vagal-first aplicado no adulto mas não no lactente.
- **Dengue:** eixo de gravidade é o **extravasamento plasmático**, não o sangramento (card #396 errado). ADE nomeado parcialmente (#397).

## Artefatos criados/modificados
- `resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md` (4 armadilhas + 3 bullets)
- `tools/cards_regen_queue.py` (critério órfão corrigido + docstring)
- `.claude/commands/estilo-flashcard.md` (§Backfill atualizada/reativada)
- `ipub.db` (local-only): +7 erros (233 total), +7 cards CAD/EHH, 87 cards regenerados, 1 aposentado, 15 revlogs FSRS, +1 sessoes_bulk

## Decisões tomadas
- Regenerar os 87 heurísticos órfãos (decisão do usuário) em vez de aposentá-los — o caminho §Backfill da `estilo-flashcard.md` foi reativado para esta finalidade.
- Aposentar a duplicata #276 (idêntica a #274) em vez de manter dois cards FSRS iguais.

## Continuação (pós-fechamento inicial)

### /revisar — +5 cards (Febre Amarela) → 20 no total
- Bloco FA: 4/5 caíram (vetores, vírus, sinal de Faget, viremia/isolamento) — **Febre Amarela é o calcanhar confirmado**. Esquema vacinal (9m+4a) acertado.
- **Feedback do usuário (encodado):** ao errar um card (nota 1-2), apresentar **micro-resumo do bloco** (revisão *just-in-time*). Gravado em `.claude/commands/revisar.md §Modo conversacional` + memória `feedback-revisar-conversational-mode`.

### Adendo — Camada de governança de evidência (port adaptado do irmão)
Por diretriz do usuário, portado o mecanismo de busca/auditoria de evidência científica do `agente-daktus-content`, adaptado ao MedHub:
- `core/contracts/evidence-governance.md` (contrato): hierarquia **sociedades BR + MS > RCT/meta + guidelines INT > consenso** + **lente da banca**; taxonomia de 6 vereditos com **`DESATUALIZADO`** (banca × evidência atual) como assinatura MedHub; conflito banca×evidência → ensina a banca + 🔴 armadilha banca-dependente (drift não silenciado); honest-negative; boundary abstract-only; audit-before-advance.
- `.claude/commands/pesquisar-evidencia.md` (skill operacional) + `.claude/agents/evidence-researcher.md` (subagente fan-out, read-only).
- `pubmedmcp` adicionado ao `.mcp.json` (local/gitignored; conecta no próximo boot).
- Integração: AGENTE.md §6/§7.3, analisar-questao, estilo-resumo, estilo-flashcard.
- Escopo v1.0: **go-forward + skill sob demanda** (sem varredura retroativa). Fonte: `pubmed-audit-layer.md` + `evidence-bank-governance.md` + `daktus-evidence` do irmão.

## Próximos passos
- **Reiniciar o Claude Code** para o `pubmedmcp` conectar (a auditoria por PMID/DOI só funciona após o restart; antes disso degrada para WebSearch).
- **NOVA DEMANDA — re-fil dos temas `[bulk]`:** dezenas de cards estão mal-rotulados (cardiopatias congênitas, iSGLT-2, metas HbA1c, epidemiologia, GO — todos sob "[bulk] Cirurgia"); infla o "Cirurgia due" e distorce o filtro por área do `/revisar`. Migração one-shot, backup-first.
- **Drenar backlog FSRS** (15 cards restantes da fila de hoje + 4 que voltam hoje por rating 1 + novos) por área fraca.
- **Bloco PALS** (arritmias pediátricas) como revisão dirigida.
- **Resumo `Diabetes - Complicações Crônicas`** segue como gap do cronograma (DM2 + Agudas + Crônicas fecham o bloco DM).
