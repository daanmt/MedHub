# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-16 -- **s122: dia gigante de S13 (102q). Imunizações loop M2 FECHADO (aula D10 -> 18 cards do pool drenados -> resumo backfillado). Pré-Natal II Exame Físico (aula D5, 21q/85,7%). Endometriose tema-zero DESTRAVADO (aula D8, 26q/73%, resumo criado do zero). 10 cards de erro novos (826-835).***

## > Proximo passo imediato

**Fechar os loops M4 (cards frescos entram em <=2 dias) + continuar S13:**
1. 🎴 **Drenar os cards frescos do dia** (colados nos temas): 5 de **Endometriose** (831-835), 3 de **Pré-Natal II** (828-830), 5 do pool Teoria I de Pré-Natal (757-761). `/revisar DRENAR --area GO --new-limit 20`.
2. 🧭 **Continuar S13:** o Drive estava stale -- rodar `python tools/cronograma.py --sync-drive <xlsx>` no boot antes de confiar nos `próximos temas`. Tarefas restantes da Semana 13.
3. 📊 **Volume:** ritmo-alvo ~82.6q/dia (s122 fez 102, acima). Retomar questões dos próximos temas.

**Princípio (M4):** card fresco entra colado no tema estudado, em <=2 dias -- não recriar o pool de junho.

## Padroes de erro vivos -- atencao do scrum master
- 🔃 **Inversão de marcador / número-vs-faixa (reincidiu 2x s122):** Doppler 10-11 sem lido como valor único (é janela 9-12); aromatase marcada como "falta" quando é **super-expressa**. Fixar a DIREÇÃO no mecanismo.
- 🔴 **Bug nº1 / leitura por dado parcial (reincidiu s122):** fechou RCF só na altura uterina baixa, ignorou a USG normal que a corrige. "Pior/parâmetro isolado" ainda vivo.
- 🆕 **Sobre-investigar / não confiar no dx clínico (NOVO, 2x em Endometriose):** pediu laparoscopia/exame especializado antes de tratar. Endometriose é dx CLÍNICO -> quadro típico = empírico. Observar se transfere.
- 🟢 **Imunizações (D10, era a maior alavanca do pool): 18 cards drenados, resumo completo.** Fraqueza nº1 muito atacada nesta sessão.

## Estado por frente
- **Volume & Metas:** 5128 / 10000 (perf. ~79.3%). Hoje: 102. Ritmo-alvo ~82.6q/dia (59d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** divida 2 atrasados + 7 p/ hoje -- pool 417 nunca introduzidos (entram <=30/dia). [derivado] 16 cards de Imunizações introduzidos s122.
- **Conteudo:** 71 resumos em resumos/ (🆕 Endometriose; Imunizações backfillado +3 seções). [derivado: glob]
- **Erros & Cards:** 10 cards de erro novos (826-835); 672 reforjado; 817/752 aposentados. Cards frescos (13) a drenar (M4).
- **Posicao cronograma:** db=S13 (nominal S16, atraso 3 sem). Drive stale -- `--sync-drive` quando houver xlsx local.

## Pendencias ativas
🔴 Drenar os 13 cards frescos (M4). Dedup taxonomia `Pré-Natal` GO(300)×Obstetrícia(291) (nota `agente_inferida=9` stale na de Obstetrícia -- colapsar MAX). Aula-base de Pré-Natal I. Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Reforjar cards 95/120 (120 via gate de evidência). M2 continua nos pools de Cirurgia (Infantil/Apendicite/Trauma) e GO (Hipertensivas/Vulvovaginites). Ledger `AUDITORIA_MEDHUB.md`: F35 (reconcile volume + seletor de suite auto_check); F8 (isolamento PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025). Banca-dependente no DITC II (belimumabe/nefrite, SAF 2023).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_122.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
