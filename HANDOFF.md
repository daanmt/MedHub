# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-05 (noite) -- S165 (Claude Code / Fable 5.1): 5 aulas EMED digeridas -> `prevalencia_enamed.json` + `fsrs_queue --prevalencia`; NENHUM card gravado; redrill em debito pela 5a sessao*

## > Proximo passo imediato

1. 🎯 **DRENAGEM FSRS em 2 blocos de 60 (regra do usuario s165: 120/dia como sprint ate 13/09, NAO e o novo teto; s159 = 60 volta depois do ENAMED).** Redrill acumulado: **64 cards nota 1-2** (24 da s161/162 + 2 + 38 da s164) + 26 nota-3; **54 dos 64 ja estao vencidos** -- a drenagem E o redrill. Puxar com `python tools/fsrs_queue.py --list --limit 200 --new-limit 0 --cluster`.
   - **Bloco 1 (62) = consolidar:** 54 redrill em cluster + 8 `fresh_error` do Simulado 6 (1472-1476, 1478-1480). Sub-blocos ja montados na s165: 1.1 Epilepsias 11 (1455,1456,788,789,790,792,1457,1185,1187,1191,1192) + 540 (TCE, 3a ocorrencia) + 4 + 244 + 245; 1.2 Vulvovaginites 9 (1444,665,667,740,741,744,745,747,937) + Ulceras 381, 908, 1478 + Planejamento 577, 1283, 1284; 1.3 Colecistite 6 (1089,1481,1482,823,1296,1381) + Apendicite 5 (727,728,734,736,1380) + bulk 297, 311, 313 + Polipos 706, 709; 1.4 GO/Ped/Prev singletons (1101,1117,485,122,1270,1404,1475,1476,558,1354,459,1472,1473,1474,1479,1480). Tronco (PREPARAR, sem versos) antes de cluster frio -- Epilepsias e Vulvovaginites ja carimbados no `review_log` (ids 111, 112). Nota honesta; a nota mede "pegou o framework". Redrill dos 1-2 so pela frente ao fim do bloco, + 10 nota-2 que o FSRS empurrou p/ outubro (155,383,570,650,828,1115,1290,1415,1416,1442), sem `--record`.
   - **Bloco 2 (60) = expandir:** ~20 vencidos de menor estabilidade + **~32-40 NOVOS via `--prevalencia`** (`python tools/fsrs_queue.py --list --new-limit 40 --prevalencia`). Smoke da s165: o bucket abre com **Cirurgia Infantil 22** (fraqueza nº 1, 43 no pool, "cai todo ano" no INEP), depois Dependencia Quimica/tabagismo 4, Planejamento 4, SIS 3, MFC 3. Deslizar hoje: Vulvovaginites (ja tem 9 no redrill).
2. 🔴 **Regra nova (usuario, s165): prevalencia = prioridade na fila dos nunca introduzidos.** Portador: `tools/fsrs_queue.py --prevalencia` (opt-in, so ordem de introducao, FSRS intocado) lendo `core/cronograma/prevalencia_enamed.json` (89 temas, 59 alta, 5 fontes, 35 padroes de banca). Ligar o mesmo arquivo ao `infer_nota()` eixo 4 (F63) e ao day_plan e engenharia pendente.
3. **Cunhagem fraco-primeiro (dias 06-12/09), 8-10 atomicos/tema dos decks EMED, so onde o pool nao tem:** SCA (zero tudo), Derrame pleural, Crise hipertensiva, Dislipidemia nova, Obesidade/SM, Dermatoses infecciosas, SUA (roxo S17, zero cards, resumo existe), Down, Kawasaki, Diarreia, Puberdade/Baixa estatura, Convulsao febril, Choque/Phoenix, TB/ILTB, ITU, Saude do trabalhador.
4. **Grade S17 roxos ate 13/09:** Diarreia (Teoria, sem resumo -> aula-base) -> SUA (Teoria) -> APS (Revisao) -> Diarreia (Revisao) -> Urologia I -> Pneumonias I. ~65q/dia.
5. **Inscricao UERJ** fecha 01/10 (Cepuerj, R$ 380). Acao do usuario.
6. 🔬 **Engenharia (ledger §4o): F63 (dado agora existe), F65 agravado (`[bulk] Cirurgia` 148 erros, `[bulk] Pneumo` 17), F66, F67-F69 novos** (ver AUDITORIA).

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (57d). ENAMED 13/09 (8d) termometro.
- **Volume & Metas:** 6721 / 10400 (perf. ~78.8%). Hoje: 0. Ritmo-alvo ~64.5q/dia (57d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 57 atrasados + 52 p/ hoje -- pool 642 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 940 erros registrados · 1289 cards ativos · 2 needs_qualitative na fila · taxonomia 270 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S23, atraso 6 sem) [derivado: preparacao_estado]
- **Prevalencia (novo SSOT de insumo):** `core/cronograma/prevalencia_enamed.json` -- Ped I, Gineco, CM I, Cirurgia I (Revalida, proxy), Preventiva I. Pendentes: Ped II, Preventiva II (12/09), Cirurgia II, CM II, revisao de vespera.
- **Reforja:** 15 itens (821,702,283,505,411 + 570,128,705,1360 + 311/313 clones, 470 + 1415,1086,1126).
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**.

## Ultima sessao -- s165 (2026-09-05): AULAS EMED -> PREVALENCIA, sem drenagem
Boot achou a **s164 nao selada** (3 commits, sem log/HANDOFF/INDEX) -- reconstruida em `history/session_164.md`. Blocos 1.1 e 1.2 montados e entregues (troncos sem versos) mas o usuario preferiu enviar 5 transcricoes das Horas da Verdade do Estrategia MED (INEP). Cada aula virou: tabela tema x sinal do professor x pool/ativos/erros/resumo + padroes de banca, persistidos em `prevalencia_enamed.json` (5 commits). Achados: **SCA e o maior buraco do banco** (zero linha, zero card, zero resumo; "esta na moda"); **Cirurgia Infantil = fraqueza nº 1 com 43 cards nunca vistos** (a municao ja existe); **SUA** (3o tema de Gineco) sem card e sem linha; a **Q66 do Simulado 6 e a questao que o professor de endocrino resolve ao vivo** (volume -> potassio -> insulina); a aula de neuro + a de trauma dao pela 3a vez o mecanismo do card 540 (PPC = PAM - PIC, sem hipotensao permissiva em TCE). Resumos ja absorvem HAS 2025 (130/80, MAPA), levetiracetam EV e a maior parte do ATLS 11 (faltam "sangue total > 1:1:1", Sellick contraindicada, classificacao leve/moderado/grave a conferir). Fechou com o usuario fixando **prevalencia = prioridade** -> implementado `--prevalencia` no `fsrs_queue` (5 testes, auto_check PASSED 363).

## Pendencias/observacoes ativas
- 🔴 **REDRILL 64 cards nota 1-2 -- 5 sessoes em debito.** Bloco 1 da proxima sessao paga.
- 🔴 **Nenhuma questao/card hoje.** Dia zero de volume; o sprint 120 cards/dia comeca na proxima.
- 🔴 **Inscricao UERJ** -- fecha 01/10.
- 📚 **Frente MFC (Gusso + Duncan)** -- abre 14/09. Rescope da grade pro formato UERJ em 14/09.
- 🔬 **F66** (memoria de fraquezas orfa por abreviacao) segue a maior prioridade de engenharia; **F67** taxonomia duplicada (colo x2, TH x2, Asma x5, PF/Contracepcao, Ulceras x2) divide FSRS/dormencia; **F68** 15 temas prevalentes sem linha na taxonomia; **F69** resumos Trauma/Dislipidemia com lacunas de diretriz nova (banca-dependente).
- 💉 Diretrizes novas a conferir nos resumos: Calendario Vacinal 2026, GINA 2026, Reanimacao SBP 2026, HAS 2025 (ok), Dislipidemia 2025, ATLS 11 (parcial), SINAN 2026.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_165.md*
