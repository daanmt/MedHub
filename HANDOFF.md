# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-11 -- **s118: DITC II (LES+SAF) 24q/11a (46%); 13 erros -> 13 cards (797-809). Feedback: aula D9 saiu enxuta-incompleta (sem DDx) -> memória atualizada + §11 Diagnósticos Diferenciais costurada no DITC II.md (auto_check PASS). FSRS drain lote 1 (5 cards). s117 selada (commit 655b2fc). Modo recuperação (cansaço); rush volta 13/07.***

## > Proximo passo imediato
1. **PRÓXIMA SESSÃO (plano do usuário):** (a) **revisão/PREPARAR de CADA tema** dos próximos ~50 cards da fila FSRS; (b) depois **drenar 50 cards** (atrasados + hoje + backlog). Boot: puxar a fila viva `python tools/fsrs_queue.py --list --limit 50 --cluster` e oferecer o PREPARAR por tema. Snapshot 11/07 (Trauma-pesado): Trauma Abdominal (10), Cir. Infantil I (6), Trauma Aval. Inicial (5), Pancreatite (4), Hemostasia/Arboviroses (3), Ectópica/Emerg.Ped/Hanseníase/TCE ped/Choque (2), + ~10 temas com 1.
2. **Hanseníase -- Revisão Direcionada pendente** (veio fria no drain: dx inicial/estesiometria + vigilância de contato 5 anos).
3. **Segunda 13/07:** rush do cronograma volta -> `python tools/cronograma.py --sync-drive <xlsx>` OBRIGATÓRIO antes (Drive stale).
4. **Batch pendente (plano s116):** faltam **Imunizações III (29q)** + **Colecistite e Colangite (18q)**.
5. **Mini-drill de enunciado negativo** -- reincidente 3ª+ sessão seguida (prioridade).

## Padroes de erro vivos -- atencao do scrum master
- 🔴 **bug nº1 / leitura parcial (eixo nº1, 3x na s118):** tinha o discriminador (granular=LES, complemento baixo=atividade, classe IV x V) mas ancorou num achado só (proteinúria, hemoptise). Mesmo padrão da s117 (acuidade/contexto) e do simulado. **É o eixo que mais sangra ponto.**
- 🔴 **enunciado negativo -- REINCIDENTE (Q4; 3ª+ sessão seguida):** rotular cada opção V/F antes de marcar. Mini-drill = prioridade.
- 🔴 **DDx breadth -- falha de AULA (do agente):** aula D9 sem diferenciais; corrigido no resumo + memória `feedback_aula_base_cobertura_escopo`. Ao dar aula de tema integrador (LES, pulmão-rim, poliartrite), listar os DDx no checklist de cobertura.
- Lacunas s118: Evans (AHAI+plaquetopenia), prognóstico do LES (negro/NSE, não articular/ANA), retirada de corticoide -> insuf. adrenal, gravidez lúpica (mantém HCQ+prednisona).
- Carregado: acuidade/contexto (s117), IECA-first-no-diabético, criança DM1 = hipoglicemia.

## Estado por frente
- **Volume & Metas:** 4961 / 10000 (perf. ~79.1%). Hoje: 24. Ritmo-alvo ~78.7q/dia (64d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** 13 atrasados + 10 hoje. Backlog: 434 novos. [derivado: day_plan --handoff-block] Drain s118: 5 cards (3x nota 4, 2x nota 1).
- **Conteudo:** resumos em resumos/ (DITC II estendido com §11 DDx). [contador canonico: `python tools/cobertura_conhecimento.py` -> ".md cunhados", exclui INDEX.md -- nao hardcodar]
<!-- drift-check: sqlite "SELECT COUNT(*) FROM flashcards WHERE id BETWEEN 797 AND 809" == 13 -->
- **Erros & Cards:** +13 na s118 (cards 797-809). Temas por doença (LES/Esclerose Sistêmica/SAF/Vasculites).
- **Posicao cronograma:** conteúdo S12 (nominal S15, atraso ~3 sem). [derivado: preparacao_estado] Drive stale.
- **Infraestrutura:** nenhuma mudança de contrato/script. Pipeline "usuário larga PDF Estratégia -> subagente redige -> eu audito" segue validado.

## Handoff de engenharia recebido (ai-eng, 2026-07-12)
🔧 **`.vibeflow/prds/HANDOFF-integridade-harness-taxonomia.md`** — handoff do arquiteto (execução assumida pelo próprio ai-eng em 2026-07-12): (1) `auto_check --all` roda só 2 de N suítes (`test_fsrs` etc. sem gate — F35 parcial); (2) ~~`taxonomia_cronograma` sem `UNIQUE(area,tema)`~~ **item cai — o índice `ux_taxonomia_area_tema` existe desde a s083** (erro de verificação da auditoria de 2026-07-12; reconciliado na implantação do sensor de drift). FSRS fiel confirmado JÁ FEITO (commit `46df800`) — não refazer.

## Pendencias ativas
🔴 Hanseníase Revisão Direcionada (cluster frio). Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Aula-base de Pré-Natal I. Reforjar cards 95/120 (120 via gate de evidência). Rótulo `sessao_num=115` pendente. Ledger `AUDITORIA_MEDHUB.md`: **F21 reconciliado 2026-07-12** (conduta resolvida no contrato v1.2; enforcement mecanico na spec `mecanismo-conhecimento-consolidacao-part-3`); F35 (reconcile de volume W1/F29 + seletor de suite do auto_check). Ano da diretriz de HAS (2020 x SBC 2025). Banca-dependente no DITC II (belimumabe/nefrite, SAF 2023) -- auditar via `/pesquisar-evidencia` se quiser.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_118.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
