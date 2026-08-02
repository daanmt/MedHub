# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-02 -- **s131+s132: Simulado ENARE/ENAMED (100q, 54%) processado por completo (46/46 erros) + 2 padroes novos no ledger + PLAYBOOK_EXECUCAO_PROVA.md atualizado (tripe) + estrategia multi-banca refinada + dreno FSRS 30/100 cards + Revisao Direcionada de fechamento.***

## > Proximo passo imediato

1. **Continuar o dreno FSRS: restam 70 cards** (32 atrasados/hoje + 38 novos do pool) do lote de 100 que o usuario pediu -- ver `tools/fsrs_queue.py --list --limit 70 --new-limit 38`.
2. **Escrever as armadilhas nos `resumos/*.md` correspondentes aos 46 erros do simulado -- pendencia aberta.** ~34 temas SEM resumo ainda (1 de 35 ja resolvido: Doencas Benignas da Mama, s132). Ver lista completa em "Pendencias ativas". Frente propria, lote por especialidade.
3. **Retomar cronograma S14** (ignorar sugestao de S13 do `day_plan` -- Drive stale, ver aviso abaixo). Sem sprint: ritmo ~47-55q/dia em 6 dias/semana, decisao s126 reafirmada.
4. **Simulado semanal virou compromisso.** Proximo em ate 7 dias. Restam ~5-6 ate o ENAMED (13/09) -- ultimo cai no Interludio ja planejado (07-13/09).

## 🔁 Dreno FSRS s132 -- 30/100 cards, padrao "direcao certa sem o detalhe" reincidiu 4x

Notas: ~19x4, 8x2, 2x3, 1x1. Revisao Direcionada de fechamento (descomprimida, a pedido do usuario) conferiu os 8 resumos de origem dos 11 cards <4: **10 ja bem cobertos** (recall gap, nao lacuna -- trauma/Pringle/amilase, ulceras genitais, hanseniase, iSGLT-2, endometriose, rastreamento colo, LRA). **1 expandido:** Doencas Benignas da Mama (fibroadenoma complexo x cisto complexo -- usuario respondeu "mastectomia" pra lesao benigna).

## 🎯 Simulado ENARE/ENAMED processado (s131) -- achado mais denso da preparacao ate aqui

100q, 54% (vs 78,2% de media nos blocos por tema -- gap grande e real, nao ruido). Registrado `sessao 131 / area Simulado` no `sessoes_bulk`. Os 46 erros foram analisados em 2 lotes e persistidos via `insert_questao.py --errors-file` (0 duplicatas, cards atomicos + FSRS inicializado em todos). Detalhe tecnico e todas as questoes ficam no db (`questoes_erros` ids 622-667); o que importa reter aqui sao os PADROES, nao as questoes individuais.

**3 padroes cruzaram de "achado isolado" pra 🔴 PADRAO DE RACIOCINIO confirmado** (`tools/habilidades.py --reincidentes`):
- **"Ler exame NORMAL como dado que EXCLUI"** (vivo desde s128) -- agora **5 especialidades, 100% erro**. Reforcado por Cirurgia (bridas), Neurologia (demencia vascular x HPN), Obstetricia (pre-eclampsia).
- **NOVO -- "Incorpora diretriz/protocolo desatualizado"** -- **4 especialidades**: SBC-HAS 2025, Reanimacao Neonatal 2026, Dislipidemia 2025 (LDL<40 em risco extremo), ATLS 11a ed. (xABCDE). Mecanismo diferente dos outros -- nao e processo interrompido, e regua desatualizada na memoria.
- **NOVO -- "Pula a hierarquia do exame inicial pro avancado"** -- **3 especialidades**: lombalgia (RM em vez de radiografia), anemia perniciosa (biopsia de medula em vez de anti-FI), TCE leve (neurocirurgia em vez de TC).

Ambos os novos + o reforco do padrao-mestre estao documentados em `PLAYBOOK_EXECUCAO_PROVA.md` (secoes "s131") e em `feedback_bug_discriminador_exclui` / `project_decompose_bug_execucao_prova` (memoria). O reflexo de execucao virou **tripe** (3 perguntas antes de marcar qualquer resposta -- ver playbook).

**Confirmacoes diretas de areas fracas preexistentes:** drenagem biliar (colangite + coledocolitiase/CPRE-vs-colecistectomia) atingida **2x** na mesma sessao -- mesmo tema do radar de 884 erros. Tamponamento cardiaco antes de laparotomia bateu na area "sequencia ATLS desorganizada" ja catalogada.

**Bloco 4 da prova (Q61-80) despencou pra 35%** -- mas a dificuldade populacional media das questoes erradas ali (~51%) e parecida com a dos outros blocos (49-60%). Nao foi conteudo mais dificil; o usuario relatou atencao dividida durante a prova (multitasking). Variancia intra-prova tambem e sinal de execucao, nao so de conteudo.

**Estrategia acordada com o usuario (nao muda o plano s126, refina a aplicacao):**
- Ate o ENAMED (13/09): cronograma no ritmo atual (sem sprint por causa do susto), tripe de execucao rodando em toda questao, simulado semanal sem excecao.
- Pos-ENAMED (~26/10, UERJ/USP nov-dez): pivo ja planejado pra provas antigas da propria banca continua valendo; o tripe ja vai pronto (nao se reaprende); primeira rodada de provas antigas de cada banca deve ser tratada como simulado diagnostico (rodar variancia equivalente assim que houver ~15-20q).

## Padroes de erro vivos -- atencao do scrum master

- 🔴 **Dengue Grupo C x D -- 3a reincidencia (s130).** Mesmo discriminador (sinal de alarme isolado reclassifica pra C, nao pula pra D) errado 3x. O resumo ja tem a regra certa -- e recall que nao resiste a pressao de prova, nao lacuna de conteudo. Sem instancia nova no simulado s131 (tema nao caiu nesta prova).
- 🟡 **"Direcao certa, parou antes do detalhe" (s130).** Acertar o principio geral mas nao o numero/regime especifico que fecha a questao. Ainda vivo -- proxima ocorrencia limpa marca para o playbook.
- 🟡 **Cair na armadilha que o proprio card ja avisava (s130).** Ver o verso uma vez nao bastou pra internalizar em 4 casos.

## Estado por frente
- **Volume & Metas:** 5485 / 9454 (perf. ~78.8%). Hoje: 100. Ritmo-alvo ~47.2q/dia (84d p/ Cronograma EMED (grade completa)). [derivado: day_plan --handoff-block]
- **FSRS:** divida 26 atrasados + 15 p/ hoje (drenada de 62 nesta sessao) -- pool 566 nunca introduzidos (entram <=40/dia). [derivado]
- **Conteudo:** 75 resumos em resumos/ (1 expandido nesta sessao: Doencas Benignas da Mama). [derivado: glob]
- **Posicao:** conteudo S13 (nominal S18, atraso 5 sem) [derivado: preparacao_estado] -- ⚠️ **S13 ja fechou 12/12 na s130** (SUS/Imunizacoes/Colecistite feitos em 13-15/07); o derivado so nao reflete isso por causa do Drive stale (F36). Proximo tema real: **S14**.
- **Erros & Cards:** 667 erros acumulados (+46 nesta sessao) · cards + FSRS inicializados para todos os 46.
- **Diagnostico (`variancia.py --zona`):** zona COBERTURA (media blocos 78,2%, desvio 10,4pp alto, 43% da grade percorrida). Simulado em dia (registrado hoje).

## Pendencias ativas

**Escrever resumos/armadilhas dos 46 erros do simulado s131** -- ~35 temas SEM resumo ainda (criados so na taxonomia pelo insert): Obstrucao Intestinal por Bridas, Sepse e Choque Septico (Phoenix), Sindromes Demenciais, Abscesso Perianal, Profilaxia Antirrabica, Lombalgia e Sinais de Alarme, Dermatoses Neonatais Transitorias, Sindromes Pleuropulmonares, Etica Medica-Recusa Terapeutica, Vigilancia do Obito Materno, Vulvovaginites, Hernia Femoral Encarcerada, Ulceras Genitais (IST), Apneia Obstrutiva do Sono, Reanimacao Neonatal, Anemia Megaloblastica e Perniciosa, Prevencao Secundaria Pos-IAM (Dislipidemia), Diabetes Mellitus na Gestacao, Asma-Crise Aguda, Hanseniase, TCE Leve, Contracepcao, Declaracao de Obito, DPP, Trauma Esplenico, Restricao de Crescimento Fetal, Poluicao Atmosferica e Queimadas, Suplementacao de Ferro, Trauma Penetrante Toraco-Abdominal, Cancer de Mama-Fatores de Risco, Indicadores Epidemiologicos, Controle de Hemorragia Exsanguinante (ATLS), Febre Reumatica, Trauma Toracico (Tamponamento), Amenorreia Primaria, Convulsao Febril, Endometriose, DNPM. Lotes por especialidade, priorizando quem cai na fila FSRS primeiro.

**Worklist de atomicidade: ~348 cards** (herdada, sem mudanca nesta sessao). Ledger `AUDITORIA_MEDHUB.md`: F39 (atomicidade, PARCIAL), F38, F36 ALTA (Drive stale), F37, F35, F8.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_131.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
