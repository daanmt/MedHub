# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-15 -- **s121: dia de FSRS + engenharia + curadoria (0 questão nova). Drenei 26 vencidos (dívida→0). Auditei o baralho e tracei a estratégia M1-M4 de "matar os cards". Entreguei 2 features vibeflow (linter de auto-suficiência + telemetria pool×dívida, audit PASS ×2). M1 feito: 27 cards reforjados, worklist do linter 24→0.***

## > Proximo passo imediato

**M2 -- Intake priorizado, fraco-primeiro (o baralho está limpo, agora se ENCHE por prioridade):**
1. 🔴 **Imunizações 18 cards no pool** -- casar com a task **Imunizações-Revisão D10 da S13**: aula-base D10 (ancorada no PDF EMED) -> questões -> **drenar as 18 no mesmo dia** (loop fechado, `/revisar DRENAR --area Pediatria --tema Imuniza --new-limit 18`).
2. Depois: clusters de **Cirurgia** (Infantil 32, Apendicite, Trauma) e **GO** (Hipertensivas 23, Vulvovaginites) -- ~20 novos/dia.
3. **Volume:** dia de estudo real -> retomar questões (ritmo-alvo ~83q/dia; s121 não teve questão nova).

**Princípio (M4):** card fresco entra em ≤2 dias -- não recriar o pool de junho. **Card entra colado no tema sendo estudado** (validado pelo usuário).
**Worklist de reforja futura:** `python tools/card_self_sufficiency.py --json` (hoje: 0).

## Padroes de erro vivos -- atencao do scrum master
- 🔴 **Imunizações = dificuldade ABSOLUTA (D10):** área mais fraca, 18 cards ainda no pool. A revisão S13 é a maior alavanca.
- 🟠 **Bug nº1 (execução):** #19 asma na drenagem -- ancorar num parâmetro isolado em vez do conjunto ("pior parâmetro manda"). Faceta viva.
- 🟢 **Enunciado negativo SUSPENSO como foco (s120):** erros eram de conteúdo. Não reintroduzir sem sinal real ([[feedback_analise_hard_soft_skill]]).

## Estado por frente
- **Volume & Metas:** 5026 / 10000 (perf. ~79.1%). Hoje: 18. Ritmo-alvo ~82.9q/dia (60d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** divida 0 atrasados + 2 p/ hoje -- pool 425 nunca introduzidos (entram <=30/dia). [derivado] Baralho auditado: 596 ativos, 66/105 temas nunca drilados.
- **Conteudo:** 70 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 27 cards reforjados s121 (`card_version`++, FSRS preservado); worklist auto-suficiência = 0. Nenhum erro/card novo (dia sem questão).
- **Posicao cronograma:** db=S13 (nominal S16, atraso 3 sem). Drive stale -- `--sync-drive` quando houver xlsx local.
- **Infraestrutura:** 🆕 `card_self_sufficiency.py` (check WARN no auto_check) + `day_plan.telemetria_fila` (pool×dívida). PRD+2 specs+2 audits em `.vibeflow/`. `reflect.py` = rodar (sessão teve engenharia).

## Pendencias ativas
🔴 M2 Imunizações-Revisão D10 (aula PDF EMED -> questões -> drenar 18 cards). Backfill resumo Imunizações (Raiva/COVID/Dengue/Zóster). Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Aula-base de Pré-Natal I/II. Reforjar cards 95/120 (120 via gate de evidência -- já reforjado s121 na auto-suficiência, checar conteúdo). Ledger `AUDITORIA_MEDHUB.md`: F35 (reconcile volume + seletor de suite auto_check); F8 (isolamento PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025). Banca-dependente no DITC II (belimumabe/nefrite, SAF 2023). Opcional: F próprio p/ re-arquitetar `due=now()` (só telemetria foi feita).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_121.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
