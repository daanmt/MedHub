# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-19 -- **s125: DRENAGEM FSRS MARATONA (80 cards em 14 blocos) + passada de CURADORIA (20 cards reforjados atomicos in-place) + gate de evidencia (3 cards banca-dependentes, PMID-ancorados) + Sepse Revisao (aula legada + 37q/83,8% + 6 cards + resumo expandido). Padrao-mestre da familia bug no1 consolidado.***

## > Proximo passo imediato

**Proxima S13 (ordem real do Drive, dada pelo usuario):**
1. 🎯 **Doenca Inflamatoria Intestinal (Teoria)** -- proximo bloco. Aula-base ancorada no PDF EMED -> questoes -> cards dos erros.
2. Depois: Pneumologia Intensiva II (Teoria) · Transtornos de Humor + Psiq Social + Reforma (Teoria) · Intro Hepatologia + Ictericia nao-obstrutiva + Hepatites Virais (Revisao) · **Arboviroses + Meningites + Sepse (Revisao por Questoes)** -- Sepse volta aqui pra ser drilada.
3. 📊 **Volume:** ~86q/dia (56d p/ ENAMED).

**Sepse (Revisao) FECHADA na s125:** aula D5 ancorada no resumo gold (mecanismo aberto) + 37q/31a (**83,8%**) + 6 cards (840-845) + `Sepse.md` expandido com a **camada legada** (SIRS, EGDT/SvcO2, "sepse grave" abolido, mediadores, escalonamento de ATB) -- 4/6 erros bateram nesse andar que o resumo Sepsis-3-forward omitia. `review_log` carimbado (directed_review, tema 266).

## Padroes de erro vivos -- atencao do scrum master
- 🔴 **PADRAO-MESTRE consolidado (`feedback_bug_discriminador_exclui`):** ancora no achado saliente/frequente e **ignora o discriminador que EXCLUI** o dx obvio -- o dado que derruba a resposta errada quase sempre esta escrito. Provas s125: #338 (mediastino>pulmao), #342 (Listeria>GBS), #280 (dupla bolha=duodenal), #498 (irredutivel->encarcerada, ignorou indolor/sem obstrucao), #322/#507 (default sem ler contexto), #348/#340 (pular o ABC pro definitivo), #422 (IECA->BRA, mesmo mecanismo). **Ritual:** "qual dado aqui EXCLUI o que eu ia marcar?"
- 🔴 **Inversao de direcao** (#416 K hipo/hiper na rabdomiolise). 🟡 **Pergunta composta** (usuario ja a reconhece sozinho).
- 🟢 **Vitorias:** reforjados validaram a frio (398/757/759/833 -> 4); Pre-Natal cru 4/4/4; #419 resistiu a ancoragem no farmaco (leu a urina, nao o captopril).

## Estado por frente
- **Volume & Metas:** 5165 / 10000 (perf. ~79.3%). Hoje: 37. Ritmo-alvo ~86.3q/dia (56d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** divida 1 atrasados + 7 p/ hoje -- pool 365 nunca introduzidos (entram <=30/dia). [derivado] s125 drenou 80 cards (65 avaliados: 34x4/9x3/9x2/13x1, 66% solido) + 20 reforjados + 8 novos M4 intake.
- **Conteudo:** 71 resumos + **Corpus EMED 275 decks**. `Sepse.md` expandido (camada legada). [derivado: glob]
- **Erros & Cards:** 6 novos de Sepse (840-845). **20 reforjados** (346/354/364/368/416/417/418/421/489/490/491/492/493/499/501/509/511 atomicos + 420/423/760 evidencia). **3 banca-dependentes** flagueados (420 Ringer/K, 423 bicarbonato, 760 ferro).
- **Posicao cronograma:** db=S13 (nominal S16, atraso 3 sem). Drive stale -- `--sync-drive` nao rodou (base64 grande nao materializa em disco a mao); ordem real da S13 veio do usuario.

## Pendencias ativas
Bloco S13 DII (Teoria, question-first). Reforja de `TCE.md` + `Sistemas de Informacao em Saude.md` (prosa fora do padrao). Card #828 (GO/Pre-Natal, opcao-anaforico) = ultimo WARN de auto-suficiencia. Ledger `AUDITORIA_MEDHUB.md`: **F36 novo** (boot Drive: agente nao materializa binario grande baixado via MCP -> `--sync-drive` pulado 2 sessoes seguidas); F35 (reconcile volume + seletor de suite auto_check); F8 (isolamento PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_125.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
