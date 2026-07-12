# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-10 -- **s117: Cefaleias;Epilepsias + DITC II = 3 resumos gold do zero (Estratégia MED, subagentes + auto_check PASS). Bloco Neuro 30q/20a (66,7%); 9 erros -> 9 cards (788-796). Bloqueio da s116 (PDF de Cefaleias adulto) resolvido pelo usuário. Corrigi erro factual da fonte (TVC seio cavernoso -> sagital superior) no SSOT + banca-dependente. Aulas D7->D5 (Neuro) + D9 (DITC II). Q1 banca-divergente sem card.***

## > Proximo passo imediato
1. **MODO RECUPERAÇÃO 11-12/07** (usuário cansado): sanar pendências + **drenar flashcards**; rush do cronograma volta **segunda 13/07**.
2. **Hoje (s118, em curso):** questões de **DITC II** -> analisar -> cards (área `Reumato`, tema DITC II/LES). Drenar **FSRS: 26 vencidos + backlog até o teto de 30**. Refresh **Leishmaniose** (dormente).
3. **Segunda 13/07:** `python tools/cronograma.py --sync-drive <xlsx>` OBRIGATÓRIO antes do rush (Drive 2d desatualizado).
4. **Batch pendente (plano s116):** faltam **Imunizações III (29q)** + **Colecistite e Colangite (18q)** -- só Cefaleias;Epilepsias saiu das 101q planejadas.
5. **Mini-drill de enunciado negativo** -- reincidente 3ª sessão seguida.

## Padroes de erro vivos -- atencao do scrum master
- 🔴 **Casar conduta x acuidade/contexto (família bug nº1 + ATLS, 3x na s117):** Q2 (pulou a ventilação pós-benzo, foi em manitol), Q3 (açúcar VO no inconsciente), Q9 (fenitoína IV em crise única). Aplica a conduta certa no momento errado -- "parar antes de completar a verificação".
- 🔴 **Enunciado negativo -- REINCIDENTE (Q5/Q6; 3ª sessão seguida):** rotular cada opção V/F antes de marcar. Hora do mini-drill dedicado.
- 🔴 **Sintomático x profilático (Q10):** di-hidroergotamina (abortiva) numa pergunta de profilaxia, mesmo após a aula do dia.
- Lacunas pontuais s117: B6 x B12 (status refratário), recorrência de crise febril (pico BAIXO, contraintuitivo), duração > 24h não é red flag.
- Carregado: enunciado negativo (s116 2x, s112, s100...), IECA-first-no-diabético, criança DM1 doente = hipoglicemia não CAD.

## Estado por frente
- **Volume & Metas:** 4937 / 10000 (perf. ~79.3%). Hoje: 0. Ritmo-alvo ~79.1q/dia (64d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** 18 atrasados + 8 hoje. Backlog: 421 novos. [derivado: day_plan --handoff-block]
- **Conteudo:** 69 resumos em resumos/ (+3 na s117: Cefaleias, Epilepsias, DITC II). [derivado: glob] DITC II = sibling do `DITC.md` (não extensão).
- **Erros & Cards:** +9 na s117 (cards 788-796). Q1 banca-divergente sem card.
- **Posicao cronograma:** conteúdo S12 (nominal S15, atraso ~3 sem). [derivado: preparacao_estado] Drive 2d stale.
- **Infraestrutura:** nenhuma mudança de contrato/script (só conteúdo + operação normal). Pipeline "usuário larga PDF Estratégia -> subagente redige -> eu audito" validado 3x nesta sessão.

## Pendencias ativas
🔴 Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Aula-base de Pré-Natal I (débito antigo). Reforjar cards 95/120 (120 via gate de evidência). Rótulo `sessao_num=115` (bloco Endocrino da s114) segue pendente -- reconciliar quando conveniente. Ledger `AUDITORIA_MEDHUB.md`: **F21 aberto**; próximos achados em F35 (mecanizar reconcile de volume W1/F29 + fechar blind spot do seletor de suite do auto_check). Ano da diretriz de HAS (2020 x SBC 2025). **Banca-dependente flagados no DITC II** (belimumabe/nefrite, SAF 2023) -- auditar via `/pesquisar-evidencia` se quiser.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_117.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
