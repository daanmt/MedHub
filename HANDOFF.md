# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-11 -- **S179 (ESTUDO, tarde)**: 90 cards drenados (teto exato), 3 resumos editados, F98/F99/F100 no ledger. Volume de questoes do dia: **0**.*

> 🔴 **Semana do ENAMED (dom 13/09). Questoes, simulados e cards -- nada de engenharia.** O permit de 10/09 segue **CONSUMIDO**; a janela 4 so reabre com **permit NOVO, citado verbatim**, via kickoff do `/ai-eng`. 🆕 **Regra permanente do operador (s179):** ele passa a **declarar o racional** da alternativa errada -- racional declarado vence racional inferido no diagnostico.

## > Proximo passo imediato

1. 📝 **`registrar_sessao_bulk` da lista de Diarreia de 09/09** -- ainda sem feitas/acertos (2 sessoes seguidas). **Registrar ANTES de analisar** qualquer questao nova.
2. 🎯 **QUESTOES.** Hoje fechou em **0**, com ritmo-alvo de **64,2/dia** e ~45/dia reais em setembro. O operador volta com questoes feitas -- registrar, depois analisar (ele traz o racional do erro junto).
3. 🃏 **Fila da noite: 8 erros frescos + 10 novos**, com gravacao. 🔴 Os **14 de relearning NAO levam segunda gravacao** -- ja re-drillados na s179 (anti-duplo-registro).
4. 🔴 **Sabado 12/09 = 64 cards + Simulado 10.** Se colidir, **o simulado vence**: confirmar o 82,1% do Simulado 8 antes do ENAMED vale mais que 64 revisoes.
5. 🗓️ **Segunda 14/09 e dia de DECISAO:** abre a frente **MFC** (20% da UERJ, Gusso + Duncan, zero volume ate hoje), chegam ~55 cards, e vence o **rescope da grade** para o formato UERJ -- incluindo **quais ~460 dos 663** nunca-introduzidos entram ate 01/11.
6. 🔴 **Passivo de cards: `reforja --fila` diz 272 abertas.** Triar e do operador -- `--fechar` re-verifica o predicado, `--descartar` e *"olhei e nao era defeito"*, e **card discriminador legitimo sai por `--descartar`**, nunca por `--fechar`.
7. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo (Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo, **Farmacodermias**, Esquistossomose, Liquido Amniotico) + s172 (Disturbios Resp. Neonatais, Infeccoes Congenitas, cerclagem). **395 PDFs / 136 `.md` / 327 orfaos**.

## Fila de engenharia -- **TIER 0 e TIER 1 ZERADOS**. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- ⚰️ **Janelas 1-3 (s176/s177/s178) -- Tier 0 e Tier 1 ZERADOS:** 0.0 a 0.7 e 1.1 a 1.9c, mais os riders F96/F97. Itens e lapides em `docs/MEMORIA-AUDITORIA.md §11`.
- 🆕 **s179 (ESTUDO) abriu tres, nenhum implementado** -- `AUDITORIA_MEDHUB.md §6v`: **F98** (guarda de blackout do F71 so ve intervalo >= 4d; 9 cards de hoje cairam em 13-14/09 sem virar candidatos) · **F99** (nao ha CLI que sirva card por id -- o passo 1 do HANDOFF nao era executavel) · **F100** (re-ensino nao fechou o gap; contra-evidencia de um remedio da s175).
- 🔜 **ABERTURA DA JANELA 4 (decidida pelo `/ai-eng`):** o smell **`db.py -> tools/card_checks` por `__file__`** (camada invertida, **toca 7 writers**). Vai **por spec** -- `gen-spec -> implement -> audit` -- com o §11 linha 1.15 como **insumo**, nunca como spec.
- 🧑‍⚖️ **1.10 segue CANDIDATO, sem GO do operador** (toda clausula de skill/`AGENTE.md` = CHECK nomeado ou marca literal "nao-verificavel").
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) `reforja.py --backfill --apply`; (b) **RODADA 3** do `normalize_taxonomia` (18 linhas fantasma); (c) ⚰️ *overflow 13-14/09* -- **DECIDIDO na s179: empurrar para 15/09+, nunca para antes da prova**; a mitigacao aceita e a inacao (reaparecem como atrasados), o conserto e o F98; (d) backfill UTC->local; (e) `--new-limit` x pool 663 -- agora com numero: **cabem ~460 ate 01/11 no teto de 60/dia**; (f) `Oncologia`/`Urologia`/`Radiologia`/`Medicina de Emergencia` sao areas?; (g) F64 (teto 60 -> 90 em dia de divida); (h) **G1/G8 -- rotacao do ledger (255 KB)**: e F62, decisao dele; (i) **F57** (72 memorias com ponteiro) e lote de sessao de ESTUDO; (j) os de sempre: apagao do `/graphify`, F35, F87, F62/F55/F37.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (51d). ENAMED 13/09 (**2d**) termometro.
- **Volume & Metas:** 7126 / 10400 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~64.2q/dia. 🔴 **A grade NAO fecha a meta:** 1.927q restantes levam a 9.053, **1.347 abaixo** do marco.
- **FSRS:** divida 0 atrasados + 14 p/ hoje -- pool **663** nunca introduzidos. Calendario: **pico 64 em 12/09**, ~55 em 15/09 (26 + ~29 do blackout), depois **7-16/dia -- vacuo, nao folga**. CV 0,71.
- **Conteudo:** 136 resumos. **Cobertura medida: 327 temas com PDF e sem `.md`.**
- **Erros & Cards:** 1002 erros · 1419 cards ativos · taxonomia 288 temas. Fila de reforja: **272 abertas**.
- **Engenharia:** suite **621** · `auto_check --all` PASSED · ledger **102 ids**.
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem).
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s179 (2026-09-11, tarde) -- ESTUDO

Detalhe integral em `history/session_179.md`.
🃏 **90 cards, o teto exato do dia** (4 atrasados + 8 erros frescos + 78 de hoje; os 10 novos ficaram fora por decisao). Notas `4 x53 · 3 x14 · 2 x7 · 1 x16` -- **74% em 3-4**, zero re-record, zero divergencia de `reason`.
🔴 **O fio da sessao: ensinar nao fechou o gap.** Tres pontos de Cirurgia Infantil ensinados na Revisao Direcionada da s175 falharam **duas vezes cada** 24h depois -- e o resumo **cobre os tres** (linhas 378/379/380, com marcador). Resumo correto + aula dada + carimbo gravado = **zero retencao**. Virou **F100**. A leitura e estreita de proposito: o mesmo fechamento da s175 produziu **14 fechamentos** hoje -- **funciona onde ha mecanismo, falha onde o fato e arbitrario** (6 mm, 40%, HAEC nao regeneram de nada).
📝 **Onde a materia ERA deficiente, editei 3 resumos:** `[GIN] CA de Mama.md` e `[GIN] CA de Endometrio.md` atribuiam **a mesma aromatizacao periferica a orgaos diferentes**, sem discriminador -- o par invertido 2x **nao era falha dele**; `HIV.md` so carregava a janela de **espera** da IRIS (2-10 sem antes) e nunca a de **instalacao** (4-8 sem depois).
🧹 **Auto-higiene:** `tmp/` esvaziado (7 arquivos de scratch de agosto, 0 referencias fora de `tmp/`).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🆕 **F98/F99/F100:** a guarda de blackout **nao cobre** intervalo < 4d, e nota 1-2 produz exatamente esse -- o painel `--blackout` diz "0 movidos / 19 overflow" e **nao conta** os 9 de hoje, que nunca foram candidatos · o re-drill inter-sessao **so funciona por acaso** (frente reconstruida de `history/` **nao e a fonte**) · o F100 e **n=3, 24h, um tema**: nao generaliza para "Revisao Direcionada nao funciona".
- **F7:** a CLASSE segue real, **declarada nao-verificavel por gate**. **F39:** entrega onde registrar, nao o conserto; precisao do detector **nao** re-medida.
- **D5** mede presenca, nao semantica · **G10** isenta por LINHA · **G5** e sensivel a arquivo novo · **G14** ve rotulo, nao verdade · o gate de revogacao casa substring literal.
- Herdadas e vivas: **F35** · **F89** (vocabulario, nao verdade) · **F79b** (ausencia de vinheta, nao suficiencia) · **F66** (34% de orfandade) · **F64** · eixo C do **F81** · sitios gemeos do **F80b**.

## Pendencias/observacoes ativas

- 🃏 **Reforja:** `python tools/reforja.py --fila` e a **unica cifra citavel** do passivo -- **272**.
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 46d sem sync (F72); Dashboard EMED x db medido pelo boot (F35).
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`. Portador dele: `C:/Users/daanm/ai-eng/brain/interactions/2026-09-10-handoff-medhub-reforma-subagents.md`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_179.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
