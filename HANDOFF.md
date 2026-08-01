# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-01 -- **s130: Meningites (resumo novo) + Reforma Psiquiatrica completa + Arboviroses/Meningites/Sepse (57q, 91,2%) + dreno de 50 cards + S13 COMPLETA (12/12).***

## > Proximo passo imediato

1. 🎯 **SIMULADO ENARE/ENAMED de 100 questoes -- amanha (2026-08-02), trazido pelo usuario.** Fecha o debito de simulado (politica 1/semana, ultimo em 28/06 -- 5 semanas de atraso) e ataca direto a **variancia alta entre blocos (10,4 pp)**, que o diagnostico (`variancia.py --zona`) prescreve resolver com simulado, nao com mais bloco por tema. Registrar com `--area Simulado`.
2. Depois do simulado: **seguir drenando a fila FSRS** (~50 cards restantes: 41 atrasados + 9 hoje) e **avancar o cronograma pra S14** -- a S13 fechou nesta sessao (12/12 tasks; as 2 ultimas eram Psiquiatria e a Revisao por Questoes de Infecto, ambas concluidas s129/s130).

## 🎯 S13 COMPLETA (s130) -- nao confiar mais no aviso antigo do day_plan

As 2 tasks que a s128 tinha isolado como pendentes (10: Transtornos de Humor+Reforma Psiquiatrica; 12: Arboviroses+Meningites+Sepse, Revisao por Questoes) foram concluidas nas sessoes 129 e 130. **S13 = 12/12.** O `day_plan` ainda pode sugerir temas antigos da S13 (SUS/Imunizacoes/Colecistite) por causa do Drive stale (F36) -- ignorar, ja foram feitos em 13-15/07 (ver s128).

## 🔬 Diagnostico vigente (`python tools/variancia.py --zona`)

**Zona COBERTURA** -- desempenho alto sobre 43,0% da grade. Prescricao: **AVANCAR a grade**.
🔴 **Variancia 10,4 pp (alta)** -- corre POR FORA da zona, prescreve **simulado** em qualquer quadrante. Em debito ha 5 semanas -- o usuario ja programou o simulado de amanha para isso.

## Padroes de erro vivos -- atencao do scrum master

- 🔴 **Dengue Grupo C x D -- 3ª reincidencia (s130).** Mesmo discriminador (sinal de alarme isolado reclassifica pra C, nao pula pra D) errado 3x: 2 em junho, 1 em s130. O resumo (`Arboviroses.md`) ja tem a regra certa desde a 2ª ocorrencia -- **isso nao e lacuna de conteudo, e recall que nao resiste a pressao de prova.** Merece ficar no radar ate parar de reincidir.
- 🟡 **"Direcao certa, parou antes do detalhe" (s130).** Padrao notado no dreno de cards: varias respostas acertaram o principio geral mas nao o numero/regime especifico que fecha a questao (criterios ADA, regime basal+bolus, local de puncao do pneumotorax pos-ATLS 10/11). Nao e falta de conhecimento, e parar cedo demais na resposta.
- 🟡 **Cair na armadilha que o proprio card ja avisava (s130).** 4 casos no dreno (LSIL 20a, DMO-DRC/calcio-vs-dieta, TTA penetrante/TC-vs-laparoscopia, cardiopatia cianotica/CIA-vs-TGA) -- ver o verso uma vez nao bastou pra internalizar nesses pontos.
- 🔴 **Padrao-mestre (discriminador que EXCLUI), faceta "exame NORMAL"** -- vivo desde s128, sem nova instancia limpa em s129/s130.

## Capacidades novas (s129/s130) -- usar

- **Recuperar aula-base de transcript anterior em vez de regenerar** -- quando o usuario ja recebeu uma aula-base na mesma sessao/dia mas nao fez as questoes ainda, ler o `.jsonl` da sessao anterior em `C:\Users\daanm\.claude\projects\C--Users-daanm-medhub\` e extrair o texto ja pronto, poupando tokens. Usado com sucesso em s129.
- **F39 continua:** mais 2 cards reforjados por atomicidade (138, 487) -- reescrita in-place com `update_flashcard_fields` + `insert_card_base.py` para os companheiros. Worklist de atomicidade segue (~350 cards, ver Pendencias).

## Estado por frente
- **Volume & Metas:** 5385 / 9454 (perf. ~79.3%). Hoje: 57. Ritmo-alvo ~47.9q/dia (85d p/ Cronograma EMED (grade completa)). [derivado: day_plan --handoff-block]
- **FSRS:** divida 41 atrasados + 9 p/ hoje -- pool 520 nunca introduzidos (entram <=80/dia). [derivado]
- **Conteudo:** 75 resumos. 2 novos completos esta sessao (`Meningites.md`, `Psiquiatria Social e Reforma Psiquiatrica.md`) + 1 da sessao anterior (`Transtornos do Humor.md`).
- **Erros & Cards:** 619 erros (+8 s129, +5 s130, incluindo 2 banca-divergentes) · 1033 cards (+13 nesta sessao entre erros e reforja).
- **Meta do mes (agosto):** 7000 acumulado ate 31/08 -- deficit 1615q, ritmo necessario ~52q/dia.
- **Posicao cronograma:** S13 **completa** (12/12). Proximo: S14.

## Pendencias ativas
**Worklist de atomicidade: ~348 cards** (227 duplo-ask primeiro -- corrompem a nota; depois os 137 so-paragrafo; -2 esta sessao). Lotes por tema, priorizando quem cai na fila FSRS dos proximos dias; nunca big-bang. Ledger `AUDITORIA_MEDHUB.md`: **F39** (atomicidade, PARCIAL, avancando), **F38** (erros analisados nao chegam a `questoes_erros` -- delta retroativo de ate 131), **F36 ALTA** (Drive stale, MCP entrega o xlsx mas a transcricao de 30 KB quebra -- so codigo conserta, `--fetch-drive`), F37, F35, F8.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_130.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
