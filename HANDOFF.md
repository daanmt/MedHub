# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-09 -- S172 (Claude Code / Opus 5): o operador triou os **85 cards** e inverteu **25 vereditos**; contrato de flashcard ganhou o **teste de regenerabilidade**; lote de **44 cards** inserido; dois auloes do Estrategia absorvidos -> **11 pontos em que o repo ensinava a resposta errada**; auditoria de evidencia fechou 5 pontos contestados; **F87** no ledger*

> 🔴 **A FILA DE ENGENHARIA SEGUE CONGELADA** por decisao do operador -- retoma em sessao dedicada, contexto limpo dos dois lados. Esta sessao e de **ESTUDO**: drillar os 44 cards novos e recuperar volume. **Ler `history/session_172.md` antes de agir.**

## > Proximo passo imediato

1. 🃏 **DRILL DOS 44 CARDS NOVOS + fila de hoje.** Divida **13 atrasados + 52 p/ hoje**; pool **701 nunca introduzidos**. 🔴 **Teto 60/dia** (90 SO em regime de divida). Os 44 sao o lote do Simulado 8 ja triado por ele -- e a **primeira medida real do teste de regenerabilidade**: se o corte foi bom, a taxa destes deve bater acima da media de estreia (~22%).
2. 📉 🔴 **VOLUME -- e a frente mais atrasada.** **0 questoes** ontem, ritmo-alvo em **65,4q/dia** e **ENAMED em 4 dias**. E as **100 questoes do Simulado 8 continuam sem registro** em `sessoes_bulk`: registrar pelo fluxo da planilha -> `/importar-planilha`, **nunca digitando** (F37). A lancar: **78 certas / 17 erradas / 4 anuladas / 1 nao computada**.
3. ⚠️ **REINDEXAR O RAG:** `python tools/index_resumos.py` **falhou -- Ollama fora do ar**. As 15 correcoes de conteudo da s172 (incluindo a Reanimacao Neonatal reescrita) **nao sao alcancaveis por busca semantica** ate isso rodar. O auditor de evidencia teve **zero resultados** nas 3 consultas locais pela mesma causa.
4. 🧠 **MEMORIA DA AUDITORIA -> [`docs/MEMORIA-AUDITORIA.md`](docs/MEMORIA-AUDITORIA.md)** -- indice F1->F87 por status, ciclos, mecanismos, D53-D68, inconsistencias G1-G13; ler ANTES de qualquer frente de engenharia (2o fio: `AGENTE.md` §10 item 9).
5. ❄️ **Engenharia CONGELADA** ate sessao dedicada (`/ai-eng` encerrou em `758b7fd`). Itens: spec **F81** (campo `classe` no contador) · `reforja_marks` · gate de selecao 0->1 · alcancabilidade + 3 riders · hotfix **F85**. **F87 foi numerado, NAO agendado.** **D71:** implement E audit daqui (loop vibeflow); ele orquestra; silencio = GO; o decidido sai do **ledger**.

## Fila de engenharia acordada com o `/ai-eng` (GO dado, nao executada)
Protocolo em `AGENTE.md §10.6-8`: destilado <=3k + remedio por achado -> ele responde GO/NO-GO/ALTERA. **Implement e daqui, audit e dele.**
- **Spec F81** -- predicado contexto x pergunta em `card_checks.py`. DoD tem de provar que dispara pelo caminho de **CADA um dos 7 writers** (nao 5), nao isolado. 2º predicado no mesmo spec: **pergunta generica so como CONJUNCAO** (generica **E** contexto pobre) -- isolado flagaria 49 cards legitimos. Eixo C fica **declarado como nao verificavel**. Contador de gate-miss com F79/F79b/F81 como fixtures.
- **Spec da fila de reforja** -- tabela `reforja_marks` com lifecycle (**nunca coluna booleana**: uma coluna que so flipa apaga a evidencia da reincidencia). A prosa vira CONSUMIDORA. Fechamento **explicito**, nunca inferido de `card_version` subir (#321 e a prova: v2 com o defeito intacto). Entrega inteira ou espera. Check de idade N=6 dentro do mesmo spec.
- **Dry-run do lote 600-799** (132 cards) sob `§10.7`: COUNT-ASSERT + dry-run declarados ANTES. Gatilho e do operador, nunca do agente -- e conteudo clinico. Ja pode rodar: a guarda de nao-crescimento do verso existe desde `d2026a1`.
- **4 achados de 08/09 sem F-id** (G2): hotfix do event_log, ratchet, fail-loud, justificativa orfa.
- **Pendente do operador:** apagao do `/graphify` (**nao aprovado** -- fica de pe; sequencia fixture->GO->apagao parada no passo 1) · contexto obrigatorio em card novo (49% do pool nasce sem; bloquear congela metade da introducao).

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (53d). ENAMED 13/09 (**4d**) termometro.
- **Volume & Metas:** 6936 / 10400 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~65.4q/dia (53d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 13 atrasados + 52 p/ hoje -- pool 701 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 987 erros registrados · 1397 cards ativos · 2 needs_qualitative na fila · taxonomia 286 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s172 (2026-09-08 noite -> 09/09 madrugada)
**Triagem:** o operador julgou os **85 candidatos** numa bancada dedicada (Artifact com `db`, cards ja abertos com a proposta do agente) e **inverteu 25 vereditos (29%)**, fechando em **44**. Resgatou 12 -- **8 deles `conteudo`**, fato duro que nao se deduz. Cortou 13 -- **5 `discriminador` + 2 `mecanismo` + 2 `nuance`**, todos regeneraveis do card-nucleo. Os **12 `elo_quebrado` sobreviveram sem uma inversao**. ⚰️ O card do oligoamnio, celebrado na s171 como o melhor achado do 6o principio, foi **cortado**: resolver 3 alternativas com um mecanismo unico e o sintoma, nao a virtude.
**Contrato:** `estilo-flashcard` ganhou o **§Triagem -- teste de regenerabilidade** (*"o aluno consegue REGENERAR esta resposta a partir do card-nucleo mais o mecanismo que ja tem?"*) + o corolario que inverte a heuristica (`conteudo` rende mais que `discriminador` derivado da mesma questao). O principio 6 **fica**; ganha o filtro que a s171 previu que precisaria.
**Conteudo:** dois auloes ENAMED absorvidos por 2 subagentes -> **11 pontos em que o repo ensinava errado**, todos conferidos por mim antes de editar. `Reanimação Neonatal.md` **reescrito** (stub -> active, diretriz SBP mudou em 12/06/2026).
**Evidencia:** 5 pontos contestados ao `evidence-researcher`. **Em 2 a aula estava errada, em 2 o repo, em 1 os dois.**

## 🔴 A classe de achado da s172 -- o repo ensinando a resposta errada
- 🔴 **O clampeamento do cordao estava errado em DOIS arquivos, em direcoes OPOSTAS** (`Reanimação Neonatal.md` dizia 30s/60s; `Cuidados Neonatais.md` dizia o espelho). **Um erro validava o outro:** quem abrisse os dois veria dois numeros e concluiria que a distincao existe. Correto: **60s para qualquer IG**. É o padrao da colangite da s171 repetido -- **procurar contradicao entre arquivos, nao so dentro de um**.
- 🔴 **Ictericia fechou o loop de um erro real:** o resumo dava "> 0,5 mg/dL/h" e a banca cobra **0,2**. Ele errou a questao aplicando o numero que estava aqui.
- 🔴 **Gluconato de calcio: as DUAS versoes do arquivo erradas** -- cada uma corrigia metade do erro da outra e nenhuma acertava.
- 🔴 **Ponto contestado nao vira edicao por palpite.** A auditoria rendeu **2 correcoes que eu teria feito ao contrario** se tivesse seguido a aula (beta-hCG e cortes da PE).

## Padroes de erro ativos (ultima medicao: s170)
- 🔴 **O no do fluxograma nao e lido.** Acerta a CONDUTA e erra o CRITERIO que autoriza chegar nela. **5 areas.**
- 🔴 **Clozapina x carbamazepina: 5o encontro.** Nao e falta de material -- e alca de recuperacao que nao engata.
- 🔴 **Ancoragem no achado saliente** ignorando o dado que EXCLUI o dx obvio (padrao-mestre, `feedback_bug_discriminador_exclui`).

## Pendencias/observacoes ativas
- 📚 **Backlog de conteudo dos auloes (NAO executado):** criar `Distúrbios Respiratórios do Período Neonatal.md` (cobertura **zero** no repo -- SDR/TTRN/SAM, corte de 35 semanas como discriminador) e `Infecções Congênitas.md` (**nenhum tratamento** de toxo/CMV/herpes/varicela existe no repo). Em GO: prevencao da prematuridade -- 🔴 **"cerclagem" nao aparece uma unica vez no repo inteiro** -- alem de distocias, Bishop/inducao e rotura uterina.
- 📄 **Manual de Gestacao de Alto Risco (MS 2022)** excede o teto de 10 MB do fetch e barrou a confirmacao primaria em 2 itens da auditoria (beta-hCG e cortes da PE). E a **bibliografia declarada do ENAMED** -- baixa-lo uma vez resolve os dois.
- 🃏 **Reforja: 6 cards da s170** (#243, #561, #582, #321, #365, #792) + passivo de ~37. 🔴 **#321 e #792 ja tinham sido marcados antes** (s158/s166) e nunca foram reforjados.
- 🔬 **Ledger: F87 numerado** (`AUDITORIA_MEDHUB.md §6p`) -- o harness verifica FORMA e e cego a RENDIMENTO; os 13 cards reprovados pelo operador **passam** em todos os predicados. **Abertos (21 F + 2 D):** F87, F85, F81, F80, F79b, F78, F77b, F77, F76, F72, F71, F42, F36, F35 · F63-F69 · D5, D11.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026. ✅ **Reanimacao SBP 2026 -- FEITA na s172** (diretriz de 12/06/2026 absorvida, DOI 10.25060/PRN-SBP-2026-2).
- ⚠️ Drive 45d sem sync (F72): a ordem confiavel e a lista verde homologada na s168.
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_172.md * Trocas: history/exchange-log.jsonl*
