# Session 183 -- Hibrido aprovado: Reta Final rescopada ate 01/11 + extensivo como espinha do ENAMED 2027; o bloco MFC da UERJ lido nos cadernos
**Data:** 2026-09-16 (13h -> 17h30)
**Ferramenta:** Claude Code / Fable 5.1 (principal) + 5 subagentes (Opus x3, Sonnet x2)
**Continuidade:** Sessao 182 (ENAMED 2026 = 75/100)
**Tipo:** PLANEJAMENTO + ENGENHARIA (zero questoes, zero cards; PRD + P6 + P5 executada)

---

## 0. O que o usuario trouxe

1. `[52 wk] Cronograma Extensivo.pdf` (Estrategia MED, 420 paginas) na raiz -- quer avaliar migrar da Reta Final (30 sem) para o extensivo, porque a RF "e pouco e nao aproveita a maior divisao entre tarefas e temas".
2. Pasta `Medcards 2022/` (130 `.apkg`, 12.974 notas, 361 MB) -- avaliar pertinencia, qualidade e aproveitabilidade.
3. Revisao dos guias estatisticos UERJ e USP; Drive "ainda com problema de sync".
4. Pedido explicito de orquestracao com subagentes Opus/Sonnet e um plano.
5. **Na 2a fala (decisao):** hibrido APROVADO; horas na residencia = as assumidas (12-15 h/sem) ou **20 h+ se for trabalhar**; **USP fora**; **foco nº1 = Psiquiatria no IPUB, nota de corte 940, alvo 95%**; UERJ/MFC = **plano B** (bolsa complementar + bonus 10%); liberdade total para buscar ENAMED e REVALIDA anteriores (INEP); temas de MFC da UERJ pelas edicoes previas + WebSearch.

## 1. O que foi feito

### 1.1 Leitura do Drive e reconcile W1 (principal)
- Dashboard EMED 2026 lido via MCP (modificado 10/09). **Descoberta:** as 20 tabelas por disciplina somam **707 tarefas no formato Teoria I/II/III + Revisao + Revisao por Questoes = o catalogo das S1-S48 do extensivo**, nao as 352 da Reta Final. 674/735 tarefas do extensivo casam por nome (92%). O `--sync-drive` casa o xlsx de 30 semanas com o `grade.json` da RF -- outro espaco de tarefas. E a raiz da familia F72.
- Fronteira real pelo `Realizada?`: 178/707 feitas (25%); temas tocados 39%. S1-S20: 53% tarefas / 75% temas; S21-S30: 13% / 33%; S31-S48: 3% / 6%. **Entrada util no extensivo = S21.**
- Snapshot W1 gravado (`importar_sessoes.py --snapshot --por-area @abas.json --ultimo-lancamento 2026-09-10`): planilha 6.349 x db 7.326; Simulado (931) e GO nao-splitado (85) explicam o grosso; divergencias reais por area: Obstetricia -59, Dermato +41 (Hanseniase 12/08 fora da planilha), Cirurgia +40 (Urologia 09/09), Ortopedia -27, Endocrino -24, Pneumo +16, Ginecologia -26.

### 1.2 Cronograma extensivo x Reta Final (subagente Opus, 158k tokens, 34 min; re-medido)
- Extensivo: **52 semanas, 735 tarefas** (465 teoria / 218 revisao / 45 RpQ + 28 de revisao final), 13.778 paginas de leitura, 333 listas (~14.300q). Ritmo nativo **33,5 h/sem e 39 q/dia** (leitura-first); RF = 29 h/sem e 49 q/dia; contrato = 60 q/dia.
- Cobertura: ~130 temas que a RF nao tem (Pediatria +23, Obstetricia +12, Cardio +13, Preventiva +11); no sentido inverso so `Endocardites`. Nos temas comuns, +25% de tarefas/tema.
- Peso: **45% CM / 12% MFC** contra 20/20 na UERJ; SUS abre na S19, APS S21, Potassio S26, FA S27, Anafilaxia S33, IAM com supra S44, Osteoporose S44. `grep` de Wilms/Neuroblastoma/Coqueluche/PSA = **0** nas 420 paginas.
- 90% dos temas tem PDF-fonte local em `resumos/` (296/329; 395 PDFs); os 33 sem PDF incluem Psiquiatria inteira, Reumato (AR, DITC), Demencias, ECG, Marcos Legais, Polipos.
- Cenarios: **A** (manter RF S17->S24) = 2.756q cabem exatos nos 46 dias; **B** (migrar ja, S21-S27) = +25% de horas e ~1.380q A MENOS ate a UERJ; **C** (hibrido) = RF rescopada ate 01/11 + extensivo **S21-S48** (425 tarefas, 1.002 h, ~6.600q) de 02/11/2026 ate o ENAMED 2027. Modelo de horas do principal com residencia a partir de 01/03/2027: 17 sem x 30 h + 28 sem x 12-15 h = 844-928 h = 84-93%; a cauda Radio/Oftalmo/Otorrino/Orto/Dermato (33 tarefas, 74 h) fecha a conta.

### 1.3 Corpus Medcards 2022 (subagente Sonnet, 204k tokens, 28 min; re-medido)
- 12.974 notas / 129 decks ativos. Amostra lida a mao (287): **54% ATOMICO-OK, 31% pacote-de-fatos, 9% V-ou-F, 3% datado, 3% dedutivel, 0,5% verso vazio**; duplicacao real 0,2%; genero term->fato, sem vinheta.
- Pertinencia: 29 decks batem em fraqueza persistente (3.410 notas; ~1.840 atomicos estimados); cobre 6/8 temas-sem-resumo do ENAMED (FA/Arritmias 63, Coqueluche 48, Osteoporose 20, Onco ped 15, HPB/PSA 12, Anafilaxia 9); **RAPS e TEA = 0**.
- 🔴 **Defeito do MEU extrator (F108):** o regex de limpar HTML engolia `< 190 mg/dl ... >` como tag. Auditor mediu 4.638 cards (35,75%) com comparador e **123 com perda confirmada**; re-medi com `html.parser` + pre-escape: 883 cards mudaram, 123 recuperaram texto (numero identico). Corpus v2 corrigido no scratch; licao na memoria (`project_anki_html_extraction_lesson`).
- Veredito: **banco de referencia de autoria** (modelo `emed_flashcards.py`), 1 card por vez no fluxo `analisar-questao`, numero reconferido contra o `.apkg`; **nunca bulk import**.

### 1.4 Guias estatisticos UERJ / USP / ENAMED (subagente Opus, 273k tokens, 40 min; re-medido)
- UERJ N=835 (2017-2023): **CM 42,04% -> 20% (x0,48); MFC 6,71% -> 20% (x2,98)**; Preventiva 58,33 MFC / 26,04 Epi / 11,46 SUS / 3,13 Etica (p.8 + p.11 -- os 3 numeros da s159 BATEM). Bloco CM de 20q: nenhum subtema chega a 1 questao esperada; cauda de Cirurgia sem nome = 7,66/20q. 2 graficos corrompidos no PDF (Endocrino p.15, Pneumo p.23); Top-10 sem contagem.
- USP N=882: CM 35,9%; Preventiva invertida (Epi 53,5 / SUS 26,3 / MFC 11,4). Fora do plano por decisao do usuario.
- ENAMED: o guia previa 11% Preventiva; a prova real deu 29% (x2,61) -- **a prova real vence o guia**. 13/15 do top-15 ENAMED estao no top-25 UERJ.

### 1.5 Corpus INEP (subagente Sonnet, 119k tokens, 16 min; conferido no disco)
- `simulados/inep/`: **23 PDFs oficiais (39 MB, 100% download.inep.gov.br)**: ENAMED 2025 (2 cadernos + 2 gabaritos definitivos), ENAMED 2026 (copia do caderno 2 + gabarito preliminar), REVALIDA objetiva 2022/1 a 2025/2 (prova + gabarito) e 2026/1 (so prova ampliada; gabarito atras de login). Todos com texto extraivel. Inventario com URLs em `simulados/inep/INVENTARIO.md`.

### 1.6 Bloco MFC da UERJ nos cadernos 2021-2026 (subagente Opus, 254k tokens, 29 min; conferido nos PDFs)
- 🔴 **Corrige a premissa da s159:** o bloco de MFC com 20% do caderno **existe desde 2021** (rotulo "Medicina Preventiva" em 2021, "MFC" a partir de 2022; 12/60 ate 2022, 20/100 desde 2023). Conferi os cabecalhos nos PDFs: 2025 e 2026 = "MEDICINA DE FAMILIA E COMUNIDADE" na Q81. O guia classifica por TEMA (dengue -> Infecto), o caderno por BLOCO -- por isso "11,5%" e "20%" nao se contradizem.
- **104 questoes em 6 edicoes, 100% fonte primaria.** 92,3% MFC clinica/ferramentas; SUS 3,8%; Epi 3,8%; **Etica 0/104**. Top: Prevencao quaternaria (19 mencoes; quase sempre 2a camada da vinheta), Saude do idoso (13), Testes diagnosticos/probabilidade pre-teste (12; a vinheta dor precordial + TE caiu nas 6 edicoes), Condicoes cronicas na APS (11; 0 desde 2024), Rastreamento (11), MCCP (11), Polifarmacia/desprescricao (8), Ciclos de vida (7), Paliativos/dor (6), Saude mental/AUDIT/Prochaska (5), Violencia (5), IVAS/ATB racional (5), Vigilancia/DO (5), Dengue (4), MBE (4).
- Gap: `resumos/Preventiva/` tem 22 decks; **3 pagam aluguel** (MFC, Idoso, Testes Dx); nao existe resumo para P4, polifarmacia, paliativos nem MCCP. Mapeamento Gusso/Duncan por subtema em `simulados/uerj/UERJ_MFC_por_edicao_2021-2026.md §3.1`. Cadernos persistidos em `simulados/uerj/` (gitignored). 2019-2020 nao verificados (PDFs removidos da Cepuerj).

### 1.7 Engenharia executada apos a 2a decisao do usuario (permit textual: *"planejamento mais estavel, orquestrado por voce"*)
- **PRD `plano-ssot-e-cards-v2`** (`.vibeflow/prds/`): 6 partes -- P6 Autopsia diaria, P5 poda, P1 `plano_tarefas` SSOT + `grade_extensivo.json`, P2 ledger de listas, P3 painel gerado (Drive vira historico), P4 player de cards em Artifact. Tres decisoes por pergunta direta: **banco e a fonte** (Drive congelado; so investimento/mes manual), **poda lote 1 aprovada**, **player desktop-first**.
- **P6 entregue como cláusula:** `analisar-questao.md §3.3 Autopsia do bloco` (CONTRATO s183) -- toda sessao de questoes gera `artifacts/autopsia-AAAA-MM-DD.html` com enunciado, cadeia + elo, comporta, armadilha, fonte com URL, veredito, racional declarado e cards com teste de regenerabilidade; orcamento por tipo (§11) e regua F93 inalterados. Espelho regenerado (`sync_skills`).
- **P5 entregue e EXECUTADO:** `tools/cards_prune.py` (unico writer de exclusao; criterio nomeado, `--ids`, `--apply` exige `--expect`, backup + export + DELETE em 1 transacao + COUNT-ASSERT) + `tools/test_cards_prune.py` (6 testes, db sintetico, backup injetado) + allowlist + `pytest.ini` + `/engenharia-cli`. Spec `.vibeflow/specs/plano-ssot-e-cards-v2-part-5.md`. **Lote 1 no banco real:** dry-run 125 -> `--apply --expect 125` -> backup `artifacts/backups/ipub_backup_20260916_152847.db`, export `artifacts/backups/pruned_20260916_152847.json` (250 linhas), apagadas `fsrs_cards=125, flashcards=125, revlog=0, marks=0`; `check_fk_orphans` limpo. Cards: 1.668 -> **1.543** (ativos 1.476 intocados; aposentados 192 -> **67**, todos com historico).
- **Harness:** 3 gates acusaram e foram atendidos sem silenciar -- (a) allowlist nao via `DELETE FROM {tabela}` em f-string (SQL virou literal); (b) G5 tabela §7.4 regenerada + G10 ponteiro futuro `tools/medcards.py` removido do HANDOFF; (c) **F38 falso positivo declarado**: o bloco ENAMED de 13/09 tem os 25 erros persistidos em 15/09 (ids 1019-1043, d+2, fora da janela d..d+1) -- instancia declarada no teste vivo com a causa, janela NAO alargada. Suite **621 -> 627**, `auto_check --changed` PASSED.

### 1.8 Reforma via subagentes -- onda 1 (permit: *"Toque a reforma via subagents opus e sonnet 5 lhe ajudando. Esta sessao principal se mantem como orquestradora"*)
- **PRD refinado via `/vibeflow:discover`** (fast-track: 2 cortes aceitos -- player sem "aposentar", painel sem Sheet; corte "revisar so S17-S28 + S21-S30" RECUSADO -> revisao completa por area) e **8 specs via `/vibeflow:gen-spec`** (`plano-ssot-e-cards-v2-part-{1,2,3,4,6,7,8,9}`; 5 = poda). Ordem: 1 -> 9 -> 2 -> 3 -> 4 -> 6 -> 7 -> 8. Commit `c5dc40e`.
- **Onda 1 (partes 1 e 9 em paralelo, conjuntos de arquivos disjuntos; orquestrador faz `pytest.ini`, espelhos, tabela §7.4, commit):**
  - **Part-1 (Sonnet, 261k tokens, 27 min):** `cronograma.py --rebuild-extensivo/--check-extensivo/--expect-tasks` -> `core/cronograma/grade_extensivo.json` (52 sem / 735 tarefas: 465 teoria, 218 revisao, 52 RpQ; `url_lista` em 66/735 -- o PDF expoe poucas). 18 testes. Achados do filho: marca d'agua do PDF colava na ultima tarefa da semana (51 tarefas em `outro` -> 0); disciplina abreviada e listas multi-disciplina tratadas; `Radiologia` -> `Multi` (nao esta em `areas.json`); typo `10218.5` na spec (o real e 10218). Re-medido pelo orquestrador: 18 passed, `--check-extensivo` fresh.
  - **Part-9 (Opus, 243k tokens, 25 min):** `fsrs_queue.py --export-player/--build-player/--record-lote` (+ `--out --lote --sessao --apply --expect`), `core/templates/player.html` (Espaco/1-4/D, relearning no lote sem 2a nota, capability `db` em `sessoes/<sessao>/notas`, fallback de texto declarado), `revisao-calibrada-contract` **v1.4** (Clausula 12: player = superficie de DRENAR, Invariantes A/C/F por construcao), 19 testes. **Defeito pego e corrigido pelo proprio filho:** a injecao casava o 1o marcador e o comentario do template citava a tag -> comeu o `<style>` (`max-width` = 0); agora recusa template com marcador != 1. Re-medido: 27 passed com allowlist + record_review.
  - **Player do dia publicado** com `capabilities: {db: {}}`: https://claude.ai/artifact/T53xLp1Wdba6W72Mvdid6Y (60 cards -- `--limit 60`, teto decidido pelo usuario em 15/09; o `_teto_efetivo` dava 90 pelo regime de divida). Copia `artifacts/player-2026-09-16.html`. Criterio 5 do PRD (minutos por 60 cards) fica para medir na 1a drenagem real.
  - Dados de semeadura da part-2 criados pelo orquestrador: `core/cronograma/dashboard_snapshot.json` (707 tarefas / 186 realizadas, sinal aproximado) e `core/cronograma/plano_custom.json` (22 tarefas: 7 resumos MFC-UERJ, 8 temas sem resumo, 4 blocos Q81-100 da UERJ, 3 termometros INEP; 540q).
  - Selo: suite **627 -> 664**, `auto_check --changed` PASSED, commit `d9f3bcf`.

### 1.9 Onda 2 -- part-2 `plano_tarefas` (Opus, 213k tokens, 24 min)
- `app/utils/db.py`: `_ensure_plano_table`, `plano_upsert_tarefas`, `plano_listar`, `bloco_de`/`BLOCOS_UERJ`; `tools/plano.py --semear/--dry-run/--apply/--expect/--listar/--semana/--bloco/--status/--fonte/--json` (zero escrita propria; so `db.py` ganhou `plano_tarefas` na allowlist); 24 testes. Dry-run reproduziu **139 pendentes da RF com zero divergencia** contra a conta do orquestrador.
- **Decisoes do orquestrador sobre os 5 pontos do filho:** formula enumerada `1 + (S-17)//2` (o `*7//12` do brief era typo); CM dirigida `3 + (S-17)*5//12`; `semana_plano=NULL` para feita/cortada; `Multi`/Radiologia = `area=NULL` + nota F89 (26 linhas, sem chute); marca `q_rateio` nas 15 tarefas da RF com rateio.
- **Semeadura no banco real (orquestrador):** backup `ipub_backup_20260916_165237.db` -> `--semear --apply --expect 896` -> **896 linhas** (extensivo 735 / rf 139 / custom 22; pendente 632 / feita 173 / cortada 91; 101 sem match de nome nascem pendente; 173 com `origem_conclusao=dashboard_2026-09-10` a revisar na part-3). Fase 1 (semanas 1-7): 104 tarefas pendentes / ~3.050q -- acima do orcamento de 2.760; rebalancear com `--mover` (part-3) quando a semana 3 (794q) chegar.

### 1.10 Onda 3 -- part-3 mutacoes do plano + revisao por area (Opus, 196k tokens, 22 min)
- `db.py`: `plano_set_status`, `plano_mover`, `plano_confirmar_area` (1 transacao), `plano_pendencia_revisao`; `plano.py --concluir/--cortar/--mover/--reabrir/--revisar-area/--confirmar-area/--pendencia-revisao` (13 flags, todas na skill); workflow `registrar-sessao` ganha o passo 0 (concluir a tarefa ao registrar o bulk); 25 testes novos (49 no arquivo).
- **Pendencia de revisao medida no banco real: 173 linhas aproximadas em 20 areas** (Preventiva 24/115, Pediatria 29/118, Cirurgia 22/102, Ginecologia 19/75, Obstetricia 13/76, Infecto 14/54, ...). `--confirmar-area Preventiva` toca 115 linhas (N do `--expect`).
- Divergencias declaradas pelo filho e aceitas: `--sessao` e o `id` da linha de `sessoes_bulk` (nao o `sessao_num`; o output ecoa area/data/questoes); `origem_conclusao` vale para qualquer status ("quem afirmou isto"); 3 writers em vez de 2.
- **Defeito apontado pelo filho e fechado pelo orquestrador:** `nota` estava em `CAMPOS_SEMEADOS` e um re-seed apagaria o motivo do `--cortar` -> `ON CONFLICT ... nota = CASE WHEN origem_conclusao='usuario' THEN nota antiga ELSE excluded.nota END` + `test_reseed_preserva_nota_do_usuario`. Suite **688 -> 714**.

## 2. Decisoes tomadas (usuario, 16/09/2026)
- **Hibrido APROVADO** (Cenario C). Fase 1: RF rescopada por peso UERJ ate 01/11 (2.760q). Fase 2: extensivo S21-S48 de 02/11 ate o ENAMED 2027.
- **Norte reordenado:** foco nº1 = Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%); UERJ/MFC = plano B. USP fora.
- Medcards = banco de referencia; nunca bulk import. INEP (ENAMED + REVALIDA) = material de calibracao.
- Engenharia: `.gitignore` dos `.apkg` feito; `grade_extensivo.json` (E1) e CLI Medcards (E2) por spec com GO do `/ai-eng`.

## 3. Fase 1 rescopada (numeros: `grade.json` x `Realizada?` do Dashboard)
RF S17-S28: 149 tarefas, **139 pendentes / 4.036q**. Prioridade 1 (MFC/PED/CIR/GO) 76 tarefas / 2.272q; CM 50 / 1.423q; cauda 13 / 341q. Orcamento 2.760: MFC-EMED ~210 (MFC Revisao 50, Saude do Idoso T+R 32, RpQ 41, Etica R 39, Financiamento ~50) · PED 564 · CIR 469 · GO ~790 · CM dirigida ~320 · 8 temas sem resumo 160 · treino MFC nos blocos Q81-100 da UERJ 2023-2026 + REVALIDA ~200. **Cortado ate 01/11:** Estatistica Medica (126), NRs (63), IVAS pt.2, Polo Posterior, Cirrose, DPOC, Derrame/Neoplasia pulmonar, Onco cutanea, Ortopedia.

## 4. Artefatos criados/modificados
- `tools/cards_prune.py`, `tools/test_cards_prune.py`, `tools/test_writer_allowlist.py`, `tools/test_erros_orfaos.py`, `pytest.ini`, `.claude/commands/{engenharia-cli,analisar-questao}.md` (+espelhos), `AGENTE.md §7.4` (tabela regenerada), `.vibeflow/prds/plano-ssot-e-cards-v2.md`, `.vibeflow/specs/plano-ssot-e-cards-v2-part-5.md` · `.gitignore` (+`*.apkg`, `Medcards 2022/`) · `simulados/inep/` (23 PDFs gitignored + `INVENTARIO.md`) · `simulados/uerj/` (13 PDFs gitignored + `UERJ_MFC_por_edicao_2021-2026.md`) · `HANDOFF.md` · `ESTADO.md` · `history/INDEX.md` · este log.
- `preparacao_estado.planilha_snapshot` (W1) gravado. Nada escrito em `taxonomia_cronograma`, `sessoes_bulk`, FSRS ou `resumos/`.
- Memoria: `project_norte_2027_psiquiatria_ipub`, `project_plano_hibrido_extensivo_2027`, `project_dashboard_drive_catalogo_extensivo`, `project_medcards_2022_corpus`, `project_anki_html_extraction_lesson` (+ ponteiros em `project_norte_uerj_mfc` e `reference_edital_uerj_2027`).

## 5. Achados para o ledger
- **F108** -- extrator de HTML por regex engole comparadores numericos (`<190`): 123/12.974 cards perderam cutoff em silencio; medido e corrigido no scratch; regra: parser + pre-escape + diff v1/v2.
- **E1** -- Dashboard cataloga o extensivo (707) e o `grade.json` a RF (352): a conclusao real nunca casou 1:1; derivar `grade_extensivo.json` fecha a familia F72.
- **E2** -- Medcards sem CLI de consulta (espelho do EMED).
- **Premissa corrigida** -- "bloco MFC e novidade do edital 2027" (s159) era falsa: existe desde 2021.

## 6. Custo dos subagentes (F93, clausula 10)
5 spawns: Opus cronograma 158.523 tokens / 34 min · Sonnet cards 203.825 / 28 min · Opus guias 272.626 / 40 min · Sonnet INEP 118.672 / 16 min · Opus UERJ-MFC 254.032 / 29 min. Part-1 Sonnet 261.175 / 27 min · Part-9 Opus 243.067 / 25 min · Part-2 Opus 212.815 / 24 min · Part-3 Opus 195.747 / 22 min. **Total ~1,92M tokens, ~245 min de filho, ~150 min de relogio em 5 ondas.** 6 numeros load-bearing re-medidos pelo principal (735 tarefas; fronteira S21; 123 cards; CM 42,0%/MFC 6,71%; bloco MFC desde 2021; 23 PDFs) -- todos confirmados.

## 7. Pendencias
- Recursos do ENAMED ate 17/09 (usuario). Inscricao UERJ ate 01/10.
- Divida FSRS: 106 vencidos (nao drenados hoje). Re-sondar #787/#597.
- Frente MFC-UERJ: cunhar Prevencao Quaternaria, AMI, Raciocinio diagnostico quantitativo, MCCP, Polifarmacia, Paliativos, Rastreamento BR (2/semana).
- P1 (`plano_tarefas` + `grade_extensivo.json`) e a proxima spec; depois P2, P3, P4. Conciliar as 7 areas divergentes na planilha deixa de ser necessario quando P3 congelar o Drive -- registrar o delta uma vez e seguir pelo banco.
