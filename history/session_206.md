# Session 206 -- Varredura do banco de cards (fila de reforja 284 -> 24) + aula #875 + backend no ar

**Data:** 2026-09-29 (terça, 17h30-19h40) - **Ferramenta:** Claude Code (Opus 5.5) - **Continuidade:** `session_205.md`

---

## Pedido do operador

Abriu a sessão para manter o backend do hub enquanto fazia cards no celular, com o simulado UERJ pendente para depois e a semana focada nas listas da S2. Em seguida pediu: *"Temos diversos cards marcados para reforja, bem como todo o restante para varrer. Você pode resolver isso enquanto eu sigo com os cards?"*

## O que foi feito

1. **Régua calibrada pelas marcas dele.** O card mais curto que ele marcou "Card longo" tinha 486 chars; 1.112 de 1.594 violavam o teto de 480. O /ai-eng contestou o estimador (mínimo de uma marca, sem os negativos) e a query nas notas do player (725 instâncias com snapshot, `tmp/varredura_s206/query_corte_longo.txt`) mostrou um **joelho em 800** para longo+composta (0,7% abaixo de 400; 7,4% em 500-600; 14,6% em 700-800; 43% em 800-900). Decisão: marcados + >= 800 agora; 600-800 e < 600 ficam para ele (pergunta A/B no chat).
2. **Limpeza mecânica da fila:** 25 marcas de predicado que já não disparavam foram fechadas por re-verificação e 2 marcas de cards aposentados foram descartadas. 🔴 **Tropeço:** a 1ª tentativa leu os ids de um arquivo com `\r` e gravou **25 linhas "fechada" órfãs** (reforja_marks ids 772-796, motivo `X\r`, origem `s206-varredura`), que não fecham nada. Causa em `db.fechar_reforja`: faz strip do motivo só para buscar o predicado e grava o motivo cru. Refeito limpo. Hotfix com GO do /ai-eng no micro-lote.
3. **Piloto do principal (5 cards) e o rito:** `tmp/varredura_s206/` ganhou `exportar.py` (read-only), `validar.py` (os gates do `recurate_cards.validar` + régua de tamanho + dêixis + `--exigir-removido` + polaridade), `fatos.py` (lente bidirecional de número/sigla), `pt_sensor.py` (léxico pt do pyspellchecker em scratchpad + vocabulário dos `resumos/`, **fora** do brief dos filhos, lição do F113), `montar_apply.py` (recusa card do lote vivo) e `fechar_marcas.py` (fecha só par aberto de verdade). Brief v1 -> v2 (frente preservada salvo defeito de frente; `removido` declarado) -> v3 (sigla por extenso, pedido dele: *"não lembro o que é HIT"*).
4. **5 reforjadores Opus** (lote_01 de 87 para calibrar, depois onda2_1..4 de 76-78 cada, só marcados + >= 800). O principal leu todo item acusado pelas lentes e uma amostra aleatória dos limpos, restaurou 1 frente reescrita só para escapar do detector (#1098) e expandiu 2 siglas introduzidas (#753 IG, #263 CI). Aplicado por `recurate_cards.py --apply` (backup fixado por ato) + `insert_card_extra.py`; 1 aposentado (#367, duplicata do #366, conferido).
5. **As 8 marcas novas dele no lote 29c** (composta, português, circular, "não lembro o que é HIT/essas siglas") foram reforjadas pelo principal (<= 8 itens, F93 cl. 1).
6. **Evidência:** 22 dúvidas clínicas que os reforjadores sinalizaram sem mexer no conteúdo, auditadas por 2 `evidence-researcher` (sem Write: o JSON foi gravado pelo principal em `tmp/varredura_s206/evid_out.json`): 12 CORRIGIR, 3 BANCA_DEPENDENTE, 5 CONFIRMA, 2 INCERTO. **Os 12 CORRIGIR são pré-existentes (12/12, 0 introduzidos pela reescrita)**, medido contra o `antes.json` de cada apply. Um corretor Opus reescreveu 15; o principal aplicou 6 sem conflito (#822 #7 #1392 #1033 #76 #1365) e segurou 9 para o operador, porque 4 contradizem o gabarito da questão-fonte (banca x evidência).
7. **Aula-base #875 Prevenção Quaternária** no hub (fonte: EMED `10. Processo Saúde-Doença.pdf` 2.1.1-2.1.5; peças fixas de MFC marcadas como complemento), no quadro com `tarefa_id` 875.
8. **Backend:** tique manual às 18:28 (o cron das 18:07 não disparou, a sessão estava ocupada): `2026-09-29c` 100/100 gravado (92 válidas, 8 marcas) -> fila de véspera `2026-09-30a` (150) no ar; tique das 18:36 republicou o mesmo lote; tique das 19:25 no-op.

## Números (mesmas réguas, antes -> depois)

- Fila de reforja: **284 -> 24** (as 24 no lote vivo 30a, retidas até ele drenar). Cards ativos: 1.594 -> 1.692 (+99 extras, -1 aposentado). Reescritos: 325 + 6 correções de conteúdo.
- Comprimento: mediana 533 -> 431; p90 837 -> 674; máx 1.365 -> 1.010; >= 800 chars ~199 -> 6; fora da régua 1.112 -> 793 (quase todos na faixa 480-800 não marcada).
- Português (léxico, classe "certo"): 46 -> 38 cards. Siglas incomuns sem expansão: lente mecânica ruidosa (880/1.637), não usada como medida.
- Goldens do banco real re-medidos no commit `02c8105`: P1 contexto redundante 13 -> 11 (spec `alinhamento-frente-do-card` atualizada); registro do quadro com a aula nova; linha gerada de `tools/reforja.py` no AGENTE.md §7.4 (+43).

## Custo dos subagentes (usage do harness)

- Reforjadores: lote_01 353.232 tokens / 28,9 min; onda2_1 430.965 / 42,1; onda2_2 384.820 / 32,3; onda2_3 403.062 / 37,1; onda2_4 379.815 / 34,9.
- Evidência: lote A 178.724 / 18,4 min; lote B 187.810 / 17,0 min. Corretor: 185.663 / 15,7 min.
- Total: ~2,50 M tokens de filho.

## Decisões e sinais do /ai-eng (canal direto, ai-eng-40)

- Triagem: F141 ALTERA (spec própria; QUANDO = decisão do operador; medida entregue: 21/37 = 57% no ramo curto em 29/09); F142 GO com ALTERA; O-2 py-fsrs 6.3.2 GO; F128/F122 GO condicionais; F127 GO; hotfix `db.fechar_reforja` GO.
- **Decisão do operador colhida por ele: regime do ledger APROVADO** ("Aprovo para os dois"): 3º destino `limites-conhecidos` com data de revisão acusada pelo selo + campo `vizinhos:` recusado pelo check `frente`.
- Pendência para a s207: destino dos 9 itens do STATE dele (casar por conteúdo) -- lista no HANDOFF.

## Artefatos

- Commits: `f144bc3`, `f009e17` (tiques), `02c8105` (aula + goldens), e o do selo.
- `ipub.db` (local): 13 backups fixados `artifacts/backups/ipub_fixado_20260929_1756*..1927*` (sha no `tmp/varredura_s206/NOTAS_SELO.md`).
- `tmp/varredura_s206/` (local, fora do git): rito, briefs, propostas, applies com `antes.json` (rollback), `NOTAS_SELO.md`.

## Linhas do backend (tiques)

- hub-backend (tique manual, 18:28): 2026-09-29c gravado (92 validas · 0 quarentena · 8 marcas de reforja) -> 2026-09-30a no ar (150 cards, fila de vespera, saldo de hoje zerado em 159/100); hub Version 49
- hub-backend (tique 18:36): republicado com o mesmo lote 2026-09-30a (painel mudou: novos esperando 554 -> 563, extras da varredura); hub Version 50
- aula-base #875 publicada no hub; Version 51
- hub-backend (tique 19:25): lote 2026-09-30a em 0/150, projecao igual -- nada a fazer

## Próximos passos

Ver o "ABRIR A s207 POR AQUI" do `HANDOFF.md`: as 3 decisões dele (faixa 600-800, 9 cards de evidência, QUANDO do F141), as 24 marcas retidas no lote 30a, o micro-lote de engenharia e o regime do ledger, o UERJ 2021 e a poda.
