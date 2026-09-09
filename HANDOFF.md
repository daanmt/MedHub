# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-08 -- S170 (Claude Code / Opus 5): 50 cards (58%) + 20q de Etica (100%), contrato `/revisar` v1.3 (PREPARAR REVOGADO), auditoria do banco em 3 frentes com o `/ai-eng`, 9 commits, 395 testes*

> 🔴 **ESTA SESSAO REINICIOU COM CONTEXTO LIMPO.** O `/ai-eng` tambem. Nada da conversa de 08/09 sobrevive na cabeca de nenhum dos dois -- so o que esta escrito aqui, no `history/session_170.md` e nos ledgers. **Ler `history/session_170.md` inteiro antes de agir**: ele tem os padroes de erro, os achados e a fila de trabalho acordada.

## > Proximo passo imediato

1. 🧠 **MEMORIA DA AUDITORIA -> [`docs/MEMORIA-AUDITORIA.md`](docs/MEMORIA-AUDITORIA.md)** -- indice F1->F81 por status, ciclos, mecanismos, D53-D68 e as inconsistencias **G1-G13**; ler ANTES de qualquer frente de engenharia (2o fio: `AGENTE.md` §10 item 9). O ledger `AUDITORIA_MEDHUB.md` e o drill-down e **o boot nao le** (G1).
2. ❄️ **Fila de engenharia CONGELADA** ate sessao dedicada com contexto limpo (decisao do operador, 08/09; `/ai-eng` encerrou em `758b7fd`). Itens 3->7: spec **F81** (com campo `classe` no contador de gate-miss) · fila de reforja como ESTADO (`reforja_marks`) · gate de selecao 0->1 · checks de alcancabilidade + 3 riders · hotfix **F85** (`db.py:765`). **D71:** implement E audit sao daqui (loop vibeflow); o `/ai-eng` orquestra; silencio dele = GO. O que ficou decidido sai do **ledger**, nunca da memoria.
3. 🔁 **Cards:** fila de hoje pelo `day_plan`. 🔴 **Teto 60/dia** (90 SO em regime de divida). O sprint de 120/dia foi **revogado em 07/09** -- ler `fsrs-management-contract`, nao a memoria.
4. 📚 **Simulado 8 (ENARE/ENAMED 2025) ANALISADO: 78/95 = 82,1%** -- maior do ciclo, contra media historica de 60,8%. 17 erros com gabarito, marcacao e comentario oficial coletados; semente em `%TEMP%/claude/.../s8/seed.json`. Cunhagem dos cards em curso. **Sprint S17-S20 segue:** faltam ~610 das 725 questoes.

## Fila de engenharia acordada com o `/ai-eng` (GO dado, nao executada)
Protocolo em `AGENTE.md §10.6-8`: destilado <=3k + remedio por achado -> ele responde GO/NO-GO/ALTERA. **Implement e daqui, audit e dele.**
- **Spec F81** -- predicado contexto x pergunta em `card_checks.py`. DoD tem de provar que dispara pelo caminho de **CADA um dos 7 writers** (nao 5), nao isolado. 2º predicado no mesmo spec: **pergunta generica so como CONJUNCAO** (generica **E** contexto pobre) -- isolado flagaria 49 cards legitimos. Eixo C fica **declarado como nao verificavel**. Contador de gate-miss com F79/F79b/F81 como fixtures.
- **Spec da fila de reforja** -- tabela `reforja_marks` com lifecycle (**nunca coluna booleana**: uma coluna que so flipa apaga a evidencia da reincidencia). A prosa vira CONSUMIDORA. Fechamento **explicito**, nunca inferido de `card_version` subir (#321 e a prova: v2 com o defeito intacto). Entrega inteira ou espera. Check de idade N=6 dentro do mesmo spec.
- **Dry-run do lote 600-799** (132 cards) sob `§10.7`: COUNT-ASSERT + dry-run declarados ANTES. Gatilho e do operador, nunca do agente -- e conteudo clinico. Ja pode rodar: a guarda de nao-crescimento do verso existe desde `d2026a1`.
- **4 achados de 08/09 sem F-id** (G2): hotfix do event_log, ratchet, fail-loud, justificativa orfa.
- **Pendente do operador:** apagao do `/graphify` (**nao aprovado** -- fica de pe; sequencia fixture->GO->apagao parada no passo 1) · contexto obrigatorio em card novo (49% do pool nasce sem; bloquear congela metade da introducao).

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (54d). ENAMED 13/09 (5d) termometro.
- **Volume & Metas:** 6936 / 10400 (perf. ~79.0%). Ritmo-alvo ~64.1q/dia (54d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 0 atrasados + 13 p/ hoje -- pool 657 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 970 erros registrados · 1353 cards ativos · 2 needs_qualitative na fila · taxonomia 275 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s170 (2026-09-08)
**Cards (50, 58%):** 21x4 · 8x3 · 6x2 · 15x1. 🏆 **A inversao Wilms x neuroblastoma quebrou** (2 cards, os 2 certos). **SUA: 25% -> 73%** -- o re-ensino completo do dia anterior, com uma noite de sono, e o que produziu recall. **Etica Medica 20/20.**
**Contrato:** `/revisar` v1.3 -- ⚰️ **PREPARAR, Camada 0, Camada 1 e Invariante D REVOGADOS**; a sessao passa a ter 2 fases (DRENAR -> **REVISAO DIRECIONADA de fechamento**, unica superficie de ensino, sobre notas **1-2**). **Invariante F:** silencio no meio do drill -- nota e tally, excecao unica para **defeito de card**. A **`/aula-base` NAO foi afetada** (e pre-questoes).
**Engenharia:** reforja passou a **deixar rastro** (evento `reforja` nos 2 writers, pos-commit) + **ratchet de nao-crescimento do verso** (BLOCK nos 2 writers, fail-loud) + `ESTADO.md` que se contradizia corrigido + ledger de trocas agente<->agente com hook.

## Padroes confirmados na s170
- 🔴 **O no do fluxograma nao e lido -- 5o dia, e sobreviveu a 2 explicacoes no mesmo dia.** Acerta a CONDUTA (curetagem) e erra o CRITERIO que autoriza chegar nela (estabilidade **APOS** o volume). Tem o destino decorado, nao a regra de decisao. **5 areas.**
- 🔴 **Erro repetido em 24h:** "reagiu ao leite" -> APLV. Substancia redutora e teste de ACUCAR e **afasta** a via alergica.
- 🔴 **Clozapina x carbamazepina: 5o encontro.** O resumo cobre o ponto com clareza -- nao e falta de material, e alca de recuperacao que nao engata.

## Pendencias/observacoes ativas
- 🃏 **Reforja: 6 cards da s170** (#243, #561, #582, #321, #365, #792) + passivo de ~37. 🔴 **#321 e #792 ja tinham sido marcados antes** (s158/s166) e nunca foram reforjados -- so descobrimos porque o `card_version` denunciou.
- 🔬 **Ledger (s171): F82-F85 numerados** (`AUDITORIA_MEDHUB.md §6o`) -- F82/F83/F84 nasceram RESOLVIDOS, **F85** (justificativa orfa `db.py:765`) fecha no item (7). Lapides de F5/F8 escritas. **Abertos (20 F + 2 D):** F85, F81, F80, F79b, F78, F77b, F77, F76, F72, F71, F42, F36, F35 · F63-F69 · D5, D11. 🔴 A lista viaja INTEIRA agora -- F35/F36/F42/F64 faltavam (metade do G4).
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, Reanimacao SBP 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 44d sem sync (F72): a ordem confiavel e a lista verde homologada na s168.
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_170.md * Trocas: history/exchange-log.jsonl*
