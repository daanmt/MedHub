# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-08 -- **s113: F33 RESOLVIDO -- sync mecanico de conclusao real do cronograma (xlsx Drive) via ciclo /discover->/gen-spec->/implement->/audit (PASS). cronograma-contract v1.1 + W8 novo.***

## > Proximo passo imediato
1. **FSRS:** 3 atrasados + 6 hoje (backlog 393 novos) -- `/revisar` ou `fsrs_queue.py`.
2. **Debito aberto (arrastado):** aula-base de Pre-Natal I NUNCA foi feita (operador adiantou pra cold recall) -- resumo pronto, so falta a "escada de degraus" antes de fechar o tema de verdade.
3. **Proximo bloco de conteudo real (S12, agora via sync automatico -- nao mais manual):** DITC II (Teoria) -- proxima acao pedida pelo operador (revisao Parte I + expansao Parte II) -- + Disturbios do Potassio, Cefaleias+Epilepsias, HAS Pt.2 (Teoria) + 2 blocos de Revisao por Questoes (MFC+Vigilancia+SIS; DM Tipo2 completo). Fonte: `preparacao_estado.cronograma_conclusao_drive` (boot sincroniza 1x/dia-calendario via MCP Drive quando `day_plan` sinalizar `conclusao_desatualizada` -- ver AGENTE.md §2 passo 4).
4. Slot de simulado previsto ainda nesta semana (S12, ciclo de 4 semanas).

## Padroes de erro vivos -- atencao do scrum master
- RED **Enunciado negativo reincidiu 2x no MESMO bloco de novo (DM Q1+Q4)** -- 3a sessao seguida com esse padrao (s110 Pre-Natal Q1+Q3, agora DM). Padrao cronico ja mapeado (`feedback_enunciado_negativo`); sob fadiga de leitura marca alternativa VERDADEIRA como se fosse a falsa. Ritual: rotular V/F cada alternativa antes de decidir, sempre que ver "mostra-se inadequado"/"conceito inadequado"/EXCETO.
- RED **Inversao intuitiva do mecanismo (pe de Charcot):** denervacao autonomica "deveria" sugerir isquemia/vasoconstricao, mas causa VASODILATACAO em microvasos (perda do tonus simpatico) -- 57% da turma errou na mesma direcao, sinal de armadilha sistemica, nao so individual.
- RED **Vies otimista em fato de diretriz (DM pos-ICP):** assumiu que "tratar bem os fatores de risco" reduz obito/eventos no diabetico revascularizado; a diretriz SBC/SBHCI 2017 diz o oposto (nao ha reducao efetiva demonstrada) -- 72% da turma errou pro lado otimista.
- RED **Mapa de reforco instavel (Imunizacoes, arrastado):** inventa reforco onde nao existe (Hepatite B) E perde reforco onde passou a existir (Febre Amarela aos 4 anos, 2020).
- RED **Ferro x folato, direcoes opostas no 1o trimestre confundidas (arrastado):** ferro deve ser LIMITADO; folato deve ser INICIADO cedo. Mesma janela, sentidos opostos.

## Estado por frente
- **Volume & Metas:** 4765 / 12000 (perf. ~79.2%). Hoje: 0. Ritmo-alvo ~108.0q/dia (67d p/ ENAMED). [derivado: day_plan --handoff-block]
- **Conteudo:** 63 resumos, sem mudanca nesta sessao (engenharia pura). Gap de alta alavanca seguinte: Apendicite Aguda (F16, resumo ainda pendente).
- **Erros & Cards:** sem novos cards nesta sessao.
- **FSRS:** 3 atrasados + 6 hoje. Backlog: 393 novos. [derivado: day_plan --handoff-block]
- **Infraestrutura:** F33 resolvido -- `tools/cronograma.py --sync-drive` (parse xlsx + matching semana/tema/tipo + snapshot em `preparacao_estado`), `day_plan.py` filtra por conclusao real, W8 novo (`reconcile-contract.md`), `cronograma-contract.md` v1.1 (Clausula 5 corrigida -- ponteiro de texto estava deprecado desde 06/07 sem o contrato refletir). 8 testes novos (19/19 PASS) + `auto_check.py --changed` PASSED.

## Pendencias ativas
Aula-base de Pre-Natal I (debito, ver acima). Apendicite Aguda ainda sem resumo (F16, cobertura ja prioriza). Reescrever TCE.md + Sistemas de Informacao em Saude.md. Reforjar cards 95/120 (120 via gate de evidencia). Ledger `AUDITORIA_MEDHUB.md`: F21 aberto (contrato de aula), F30 aberto (material_indicado x resumo real) -- candidatos a Opus. Proximos achados comecam em F34.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_113.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
