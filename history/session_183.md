# Session 183 -- Hibrido aprovado: Reta Final rescopada ate 01/11 + extensivo como espinha do ENAMED 2027; o bloco MFC da UERJ lido nos cadernos
**Data:** 2026-09-16 (13h -> 17h30)
**Ferramenta:** Claude Code / Fable 5.1 (principal) + 5 subagentes (Opus x3, Sonnet x2)
**Continuidade:** Sessao 182 (ENAMED 2026 = 75/100)
**Tipo:** PLANEJAMENTO (zero questoes, zero cards; engenharia so `.gitignore`)

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

## 2. Decisoes tomadas (usuario, 16/09/2026)
- **Hibrido APROVADO** (Cenario C). Fase 1: RF rescopada por peso UERJ ate 01/11 (2.760q). Fase 2: extensivo S21-S48 de 02/11 ate o ENAMED 2027.
- **Norte reordenado:** foco nº1 = Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%); UERJ/MFC = plano B. USP fora.
- Medcards = banco de referencia; nunca bulk import. INEP (ENAMED + REVALIDA) = material de calibracao.
- Engenharia: `.gitignore` dos `.apkg` feito; `grade_extensivo.json` (E1) e CLI Medcards (E2) por spec com GO do `/ai-eng`.

## 3. Fase 1 rescopada (numeros: `grade.json` x `Realizada?` do Dashboard)
RF S17-S28: 149 tarefas, **139 pendentes / 4.036q**. Prioridade 1 (MFC/PED/CIR/GO) 76 tarefas / 2.272q; CM 50 / 1.423q; cauda 13 / 341q. Orcamento 2.760: MFC-EMED ~210 (MFC Revisao 50, Saude do Idoso T+R 32, RpQ 41, Etica R 39, Financiamento ~50) · PED 564 · CIR 469 · GO ~790 · CM dirigida ~320 · 8 temas sem resumo 160 · treino MFC nos blocos Q81-100 da UERJ 2023-2026 + REVALIDA ~200. **Cortado ate 01/11:** Estatistica Medica (126), NRs (63), IVAS pt.2, Polo Posterior, Cirrose, DPOC, Derrame/Neoplasia pulmonar, Onco cutanea, Ortopedia.

## 4. Artefatos criados/modificados
- `.gitignore` (+`*.apkg`, `Medcards 2022/`) · `simulados/inep/` (23 PDFs gitignored + `INVENTARIO.md`) · `simulados/uerj/` (13 PDFs gitignored + `UERJ_MFC_por_edicao_2021-2026.md`) · `HANDOFF.md` · `ESTADO.md` · `history/INDEX.md` · este log.
- `preparacao_estado.planilha_snapshot` (W1) gravado. Nada escrito em `taxonomia_cronograma`, `sessoes_bulk`, FSRS ou `resumos/`.
- Memoria: `project_norte_2027_psiquiatria_ipub`, `project_plano_hibrido_extensivo_2027`, `project_dashboard_drive_catalogo_extensivo`, `project_medcards_2022_corpus`, `project_anki_html_extraction_lesson` (+ ponteiros em `project_norte_uerj_mfc` e `reference_edital_uerj_2027`).

## 5. Achados para o ledger
- **F108** -- extrator de HTML por regex engole comparadores numericos (`<190`): 123/12.974 cards perderam cutoff em silencio; medido e corrigido no scratch; regra: parser + pre-escape + diff v1/v2.
- **E1** -- Dashboard cataloga o extensivo (707) e o `grade.json` a RF (352): a conclusao real nunca casou 1:1; derivar `grade_extensivo.json` fecha a familia F72.
- **E2** -- Medcards sem CLI de consulta (espelho do EMED).
- **Premissa corrigida** -- "bloco MFC e novidade do edital 2027" (s159) era falsa: existe desde 2021.

## 6. Custo dos subagentes (F93, clausula 10)
5 spawns: Opus cronograma 158.523 tokens / 34 min · Sonnet cards 203.825 / 28 min · Opus guias 272.626 / 40 min · Sonnet INEP 118.672 / 16 min · Opus UERJ-MFC 254.032 / 29 min. **Total ~1,01M tokens, ~147 min de filho, ~75 min de relogio em 2 ondas.** 6 numeros load-bearing re-medidos pelo principal (735 tarefas; fronteira S21; 123 cards; CM 42,0%/MFC 6,71%; bloco MFC desde 2021; 23 PDFs) -- todos confirmados.

## 7. Pendencias
- Recursos do ENAMED ate 17/09 (usuario). Inscricao UERJ ate 01/10.
- Divida FSRS: 106 vencidos (nao drenados hoje). Re-sondar #787/#597.
- Frente MFC-UERJ: cunhar Prevencao Quaternaria, AMI, Raciocinio diagnostico quantitativo, MCCP, Polifarmacia, Paliativos, Rastreamento BR (2/semana).
- Conciliar as 7 areas divergentes na planilha (usuario). E1/E2 por spec.
