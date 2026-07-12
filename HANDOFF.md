# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-12 -- **s119: Drenagem FSRS conversacional -- 50 cards em 13 blocos temáticos (PREPARAR calibrado por nota -> DRENAR). Notas 26x4/12x3/8x2/4x1 (sólido 76%); fila de atrasados/hoje ZERADA. Buraco: Icterícia neonatal (2x1+2x2 -> dif 8). Achado próprio: vazamento do PREPARAR em D10 (F8 reincidiu -- aquecer != responder). Nenhum resumo/código tocado. ai-eng commitou mudanças estruturais (telemetria + reflection + RAG) a ACIONAR na próxima sessão. s119 a selar (commit pendente).***

## > Proximo passo imediato
1. **PRÓXIMA SESSÃO = QUESTÕES (13/07) + ACIONAR as mudanças estruturais do ai-eng:**
   - `python tools/day_plan.py --aderencia [--semanas N]` -- **telemetria de aderência planejado × real** (nova, telemetria-estudo part-1/2). Rodar no boot/fechamento da sessão de questões.
   - `python tools/reflect.py` -- **rito REFLECTION da execução** de engenharia (gated: propõe, nunca executa). Fechamento.
   - **RAG/busca reformado pelo ai-eng** -- usar o mecanismo novo ao localizar conteúdo em `resumos/`.
   - `python tools/cronograma.py --sync-drive <xlsx>` **OBRIGATÓRIO** antes dos próximos temas (Drive stale; fileId em `.claude/commands/importar-planilha.md`).
2. **Icterícia neonatal -- leitura dedicada do resumo** (cluster frio, dificuldade 8). Único buraco de conteúdo puro da s119.
3. **Card 209 (paracoco / "por que RX imperativo") -- REFORJAR** na curadoria (card fraco/circular; não aposentar).
4. **Batch pendente (plano s116):** **Imunizações III (29q)** + **Colecistite e Colangite (18q)**.
5. **Mini-drill de enunciado negativo** -- reincidente s112-118 (não apareceu na s119 por ser FSRS); prioridade.

## Padroes de erro vivos -- atencao do scrum master
- 🟢 **bug nº1 quase ausente como EXECUÇÃO na s119.** Os erros do FSRS foram **lacuna de conteúdo**, não leitura parcial. Onde poderia morder (ectópica 114/116, PTI 7), o usuário fez o **oposto** (não tratou com dado isolado / não se assustou com o número). Mas o eixo segue vivo em **questões** (s117 acuidade/contexto, s118 3x) -- não relaxar em prova.
- 🔴 **enunciado negativo -- REINCIDENTE (s112/116/117/118):** rotular cada opção V/F. Mini-drill = prioridade pendente.
- 🔴 **Buraco de conteúdo: Icterícia neonatal (dif 8):** direta nunca fisiológica; colestase banca-dependente (AVB × hepatite); baixa ingesta × leite materno (timing); ABO×Rh pelo tipo MATERNO; IGIV só hemólise isoimune grave.
- 🔴 **Achado próprio -- vazamento do PREPARAR (F8 reincidiu):** em D10, descomprimir demais entregou as respostas de 3 cards (asma infância). Aquecer o mecanismo != dissolver o par pergunta-resposta.
- Carregado: DDx breadth (s118), acuidade/contexto (s117), IECA-first-no-diabético, criança DM1 = hipoglicemia.

## Estado por frente
- **Volume & Metas:** 4961 / 10000 (perf. ~79.1%). Hoje: 0 (revisão pura). Ritmo-alvo ~80q/dia (63d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** pós-drenagem s119 -- **1 hoje + 12 amanhã (13/07)** + 158 agendados futuros (171 total). **Backlog: 409 novos** drenáveis (+226 aposentados fora da fila). Drain s119: **50 cards** (26x4/12x3/8x2/4x1); atrasados/hoje zerados. Os 12 cards nota 1-2 reaparecem a frio em 12-13/07.
- **Conteudo:** resumos em resumos/ (nenhum alterado na s119). [contador canonico: `python tools/cobertura_conhecimento.py` -> ".md cunhados", exclui INDEX.md -- nao hardcodar]
<!-- drift-check: sqlite "SELECT COUNT(*) FROM flashcards WHERE id BETWEEN 797 AND 809" == 13 -->
- **Erros & Cards:** sem novos (revisão pura). `review_log` +21 carimbos `directed_review` (ids 66-86). `dificuldade`: Arboviroses=5 (`usuario`), Icterícia e Sepse Neonatal=8 (`aula`). Card 209 -> reforja.
- **Posicao cronograma:** conteúdo S12 (nominal S15, atraso ~3 sem). [derivado: preparacao_estado] Drive stale.
- **Infraestrutura:** **ai-eng ativo -- commitou telemetria-estudo (part-1/2), rito reflection-execucao, warn-first-check, RAG/busca reformado** (ver commits 1fd3af2..c17a6dc). Achado F8 (vazamento do PREPARAR em D10) reincidiu -- candidato a checklist de isolamento.

## Handoff de engenharia recebido (ai-eng, 2026-07-12)
🔧 **`.vibeflow/prds/HANDOFF-integridade-harness-taxonomia.md`** — handoff do arquiteto (execução assumida pelo próprio ai-eng em 2026-07-12): (1) `auto_check --all` roda só 2 de N suítes (`test_fsrs` etc. sem gate — F35 parcial); (2) ~~`taxonomia_cronograma` sem `UNIQUE(area,tema)`~~ **item cai — o índice `ux_taxonomia_area_tema` existe desde a s083** (erro de verificação da auditoria de 2026-07-12; reconciliado na implantação do sensor de drift). FSRS fiel confirmado JÁ FEITO (commit `46df800`) — não refazer.
🔧 **Novas capacidades a ACIONAR (specs `telemetria-estudo-part-{1,2}`, `reflection-execucao`):** `day_plan --aderencia` (planejado × real) e `reflect.py` (rito de fechamento gated). Estrear na próxima sessão de questões.

## Pendencias ativas
🔴 Icterícia neonatal leitura dedicada (dif 8). Card 209 reforja. Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Aula-base de Pré-Natal I. Reforjar cards 95/120 (120 via gate de evidência). Rótulo `sessao_num=115` pendente. Ledger `AUDITORIA_MEDHUB.md`: **F21 reconciliado 2026-07-12** (conduta no contrato v1.2; enforcement na spec `mecanismo-conhecimento-consolidacao-part-3`); F35 (reconcile de volume W1/F29 + seletor de suite do auto_check); **F8 reincidente** (isolamento do PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025). Banca-dependente no DITC II (belimumabe/nefrite, SAF 2023).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_119.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
