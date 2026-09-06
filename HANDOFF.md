# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-06 (noite) -- S167 (Claude Code / Fable 5.1): 90 cards drenados (divida zerada, 90% retencao) + Simulado 7 registrado e autopsiado (82%, 18 erros, 43 cards)*

## > Proximo passo imediato

1. 🎯 **Semana da ENAMED (07 a 13/09) -- decisao pendente do usuario sobre o mix.** Proposta da s167 (nao decidida): cards = revisoes do dia (~21/dia) + 30-40 novos por prevalencia (`fsrs_queue --list --prevalencia --cluster`, ~60/dia em 1 bloco) e devolver as tardes as questoes dos roxos S17 a ~64-66q/dia. Setembro fechou 06/09 com 190q (90 + Simulado); o alvo do mes pede ~63/dia. O sprint 120/dia (s165, expira 14/09) segue valido ate o usuario redirecionar.
2. 🔁 **Cards de amanha (07/09):** 14 agendados + 15 relearning de hoje que rolam (5 nota-1 da s167: #120, #419, #1424, #148, #1073 + 10 da s166 ja drillados 2x pela frente). 🔴 Os 10 da s166 (#245, #740, #741, #577, #1381, #736, #313, #706, #709, #1270) ainda aparecem como `vencido`: **regravar so na proxima sessao-calendario** (1 record por card por sessao ja foi consumido na s166). Os 43 cards novos do S7 (1484-1526) entram como `fresh_error`: drillar cedo. **Cirurgia Infantil** (22 dos 40 primeiros do pool por prevalencia) so depois do tronco D10 (fraqueza nº 1, 43 cards nunca vistos).
3. **Reforja pendente (13 da s167 + 18 anteriores):** compostas #175, #1041, #1424, #572, #581; binarias #151, #837; #526 (ctx = pergunta), #1112 (ctx contradiz), #258 (tema errado: ileo pos-op sob Pancreatite), #910 (frente aberta; podofilotoxina valida no PCDT), #527 (truncado), #513 (fork: lista sem vinheta). Anteriores: #792, #4, #1117, 821, 702, 283, 505, 411, 570, 128, 705, 1360, 470, 1415, 1086, 1126. Dedup F67: (GO, Endometriose) -> (Ginecologia, Endometriose) (#1095/#1446 clones).
4. **Sobras do redrill s167 (so pela frente na abertura):** #1112 (swab EGB 35-37, oscilou), #567 (cefalohematoma: conduta = expectante + vigiar ictericia, nunca dita), #245 (Kasai < 60d, fechou na 5a com ancora de mecanismo -- conferir se segurou).
5. **Ritual de execucao p/ a prova (S7: 8 de 18 erros por execucao; corrigir so isso = ~90%):** antes de marcar, "qual dado aqui EXCLUI o que eu ia marcar?" (Q25 45d + amilase; Q61 jovem + B + LDH; Q73 5 anos + crosta; Q81 testiculo 2 mL; Q32 SpO2 83% + FR 10). Segundo: "a pergunta pede X **e** Y?" (#567 3x, Q24). Treinar em BLOCO DE QUESTOES, nao em card.
6. **Cunhagem fraco-primeiro (ate 12/09), 8-10 atomicos/tema dos decks EMED:** SCA (zero tudo), Derrame pleural, Crise hipertensiva, Dislipidemia nova, Obesidade/SM, Dermatoses infecciosas, SUA (roxo S17), Down, Kawasaki, Diarreia, Puberdade/Baixa estatura, Convulsao febril, Choque/Phoenix, TB/ILTB, ITU, Saude do trabalhador.
7. **Grade S17 roxos ate 13/09:** Diarreia (Teoria, sem resumo -> aula-base) -> SUA (Teoria) -> APS (Revisao) -> Diarreia (Revisao) -> Urologia I -> Pneumonias I. (Ordem = esta lista, NAO a do `day_plan` -- Drive 43d sem sync, F72.)
8. **Inscricao UERJ** fecha 01/10 (Cepuerj, R$ 380). Acao do usuario.
9. 🔬 **Engenharia aberta (ledger §4q):** F76 (`--record --reason` sem checagem de proveniencia, S), F71 (balanceador x provas.json, S/M), F72 (day_plan x snapshot stale, S), D5 (skills `day-plan`/`curar-cards`, M), D11 (escopo do doc_drift, S); F63/F65-F69 seguem. F69 ganhou peso: reincidente nº 1 do ledger de habilidades = "incorporar diretriz nova" (7 temas; S7 Q79 GINA 2026, Q89 PNI 2026).

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (56d). ENAMED 13/09 (7d) termometro: S6 80% -> S7 82%.
- **Volume & Metas:** 6821 / 10400 (perf. ~78.8%). Hoje: 100. Ritmo-alvo ~63.9q/dia (56d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 0 atrasados + 15 p/ hoje -- pool 675 nunca introduzidos (entram <=60/dia; sprint 120 ate 13/09). Carga 07-13/09: 14/16/34/14/22/23/22.
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 958 erros registrados · 1332 cards ativos · 2 needs_qualitative na fila · taxonomia 274 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S23, atraso 6 sem) [derivado: preparacao_estado]
- **Prevalencia:** `core/cronograma/prevalencia_enamed.json` (5 aulas). Pendentes: Ped II, Preventiva II (12/09), Cirurgia II, CM II.
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**.

## Ultima sessao -- s167 (2026-09-06 noite): 90 CARDS + SIMULADO 7
**Estudo:** 10 blocos de 9 (decisao do usuario), pipeline de 2, feedback so 1-2. 80 gravados: **54x4 / 18x3 / 3x2 / 5x1 = 90% retencao, 68% perfeito** (s164 54%, s166 77%); divida de atrasados zerada; Indicadores 5/6 saltou p/ 2027. Redrill s166: 6 fecharam de primeira, 4 reincidiram e fecharam no redrill (#709, #1270, #741, #245). R2 sob fadiga (4/18) -> Revisao Direcionada em 5 eixos (trajeto define o metodo no penetrante #322/#1073; reacao hansenica tipo 1 x 2 #201; AGC em 2 bracos #1270 + endometriose + EGB; pediatria #567/#513/#1363; cristalizacao) -> R3 14/17; `review_log` 116-125. Cirurgia Infantil #526/#527 sairam 4. 12 defeitos de card (13%).
**Simulado 7:** 82/100 registrado antes da analise; 18 erradas extraidas do PDF pela cor dos spans; autopsia por 1 fork -> `core/simulados/_s7_erros_batch.json` -> 18 `questoes_erros` + 43 cards (1484-1526); 4 temas novos (Semiologia Cardiaca, Nodulos Hepaticos Benignos, ITU na Gestacao, Piodermites); reincidencia Q89 x erro 568 (Imunizacoes). Execucao 8/18, conhecimento 10/18 (piso: Q63 HBsAg lido como resolvida, Q67, Q59, Q50; diretriz 2026: Q79, Q89). `habilidades --backfill` +62.
**Engenharia:** ledger 4q (F40 evidencias, F67 clones, leech candidatos, F76 novo).

## Pendencias/observacoes ativas
- 🔴 **Mix cards x questoes de 07 a 13/09** -- decisao do usuario (item 1).
- 🔴 **Inscricao UERJ** -- fecha 01/10.
- 📚 **Frente MFC (Gusso + Duncan)** -- abre 14/09. Rescope da grade pro formato UERJ em 14/09.
- 💉 Diretrizes novas a conferir nos resumos: Calendario Vacinal 2026 (Q89: pneumo 20V idoso acamado, covid semestral), GINA 2026 (Q79: ICS-formoterol como resgate 6-11 anos, dose unica na crise leve), Reanimacao SBP 2026, Dislipidemia 2025, ATLS 11 (parcial), SINAN 2026 (F69).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_167.md*
