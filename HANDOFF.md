# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-16 (noite) -- **s183 (PLANEJAMENTO + ENGENHARIA)**: hibrido APROVADO; norte reordenado (Psiquiatria/IPUB via ENAMED 2027, alvo 95%; UERJ/MFC = plano B); **reforma `plano-ssot-e-cards-v2` em curso via subagentes** -- entregues P5 poda, P6 Autopsia, part-1 grade do extensivo, part-9 player (capability `db` provada: 34 notas na 1a sessao), part-2 `plano_tarefas` (896), part-3 mutacoes; faltam 4/6/7/8. Volume 7.326 (sem questoes hoje); **60 cards no player em 16,5 min, 75% de retencao**.*

> ✅ Recursos do ENAMED **enviados** (16/09). **Inscricao UERJ fecha 01/10 (acao do usuario).** **Permit de engenharia NOVO (16/09, verbatim no PRD)**: PRD `plano-ssot-e-cards-v2`, executar por spec com GO do `/ai-eng` (silencio = GO).

## > Proximo passo imediato

1. 🃏 **Lote do player de 16/09 FECHADO** (60 revisoes gravadas; 75% >= 3; **16,5 min por 60 cards -- criterio do PRD batido**). Amanha: novo lote `--export-player --limit 60` -> `--build-player` -> republicar a MESMA URL (https://claude.ai/artifact/T53xLp1Wdba6W72Mvdid6Y, passar `url`) com `capabilities: {db: {}}`; colecao nova `sessoes/2026-09-17/notas`. 🔴 **#787 (hiperaldosteronismo) caiu pela 3a vez e #597 (Winter) ficou em 2**: o eixo nefro (7 das 15 notas baixas) pede a `/aula-base` D9-D10 de Acido-Base + Potassio ANTES de novo drill, nao mais re-drill.
2. 📚 **Questoes (Fase 1, semana 1 do plano):** `python tools/plano.py --listar --semana 1` -- Vitalidade Fetal T (25) + Cirurgia Vascular R (43) + SUA R (42) + Pneumonias na Infancia T (24); ao registrar o bulk, `plano.py --concluir ID --sessao <id da linha de sessoes_bulk>`. Erros -> **Autopsia** (`analisar-questao.md §3.3`, pagina `artifacts/autopsia-AAAA-MM-DD.html`).
3. 📚 **Frente MFC-UERJ (2 resumos/sem):** Prevencao Quaternaria -> AMI -> raciocinio diagnostico quantitativo -> MCCP -> polifarmacia -> paliativos -> rastreamento (`simulados/uerj/UERJ_MFC_por_edicao_2021-2026.md §3.1`); treino nos blocos Q81-100 (`simulados/uerj/`) e REVALIDA (`simulados/inep/`).
4. 🗓️ **Revisao de status por area (173 linhas aproximadas):** `plano.py --pendencia-revisao` -> `--revisar-area Preventiva` (24/115) -> `--confirmar-area ... --apply --expect N`; ordem MFC, PED, CIR, GO. Fase 1 esta em ~3.050q para 2.760: rebalancear a semana 3 (794q) com `--mover`/`--cortar`.
5. 🔴 8 temas SEM RESUMO do ENAMED seguem (RAPS, Anafilaxia, FA, Osteoporose, HPB/PSA, Onco ped, Coqueluche, TEA) -- ja sao tarefas `custom` do plano. Reforja: 283 abertas.

## Fila de engenharia -- permit NOVO de 16/09 (PRD `plano-ssot-e-cards-v2`); por spec, GO do `/ai-eng` (silencio = GO)

- **Entregues na s183:** P5 `cards_prune.py` (125 fora) · P6 clausula Autopsia · part-1 `grade_extensivo.json` · part-9 player (`--export-player/--build-player/--record-lote`; contrato v1.4) · part-2 `plano_tarefas` (896) · part-3 mutacoes/revisao. **Pendentes, nesta ordem: part-4 e part-6 em PARALELO** (arquivos disjuntos: 4 = `day_plan.py` + contratos + `auto_check`; 6 = `db.py` + `registrar_sessao_bulk.py` + `listas.py`) -> **part-7 painel -> part-8 congelar Drive**. Specs em `.vibeflow/specs/plano-ssot-e-cards-v2-part-N.md`.
- **Regra de orquestracao que funcionou (5 partes/dia):** 1 subagente por parte, `model` explicito, arquivos confinados pela spec; `pytest.ini`, espelhos (`sync_skills`), tabela AGENTE §7.4 (`reachability_check --tabela`) e commit sao do orquestrador; **commit antes de subir a onda seguinte** (o hook roda a suite inteira). Cada filho re-medido pelo principal antes do selo.
- Abertos herdados: F98-F108 (s182/s183); F38 falso positivo de 13/09 declarado no teste vivo. Decisoes do OPERADOR empilhadas (a)-(k) da s182/s183 -- (k) conciliar 7 areas da planilha deixa de importar quando a part-8 congelar o Drive.

## Estado por frente

- **Norte:** 🎯 **Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%)**. Plano B: **UERJ/MFC 01/11/2026 (46d)**. USP fora. Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo **S21-S48** (425 tarefas, 1.002 h, ~6.600q) de 02/11 ate o ENAMED 2027 (~set/2027, data ASSUMIDA); horas 12-15/sem em R1 ou 20+ trabalhando.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~66.8q/dia (46d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. **Corpus novo:** `simulados/inep/` (ENAMED 2025 x2 cadernos + gabaritos; REVALIDA 2022/1-2026/1; 23 PDFs oficiais) e `simulados/uerj/` (cadernos AD 2021-2026).
- **FSRS:** 60 revisoes gravadas em 16/09 via player (revlog 2.981); divida remanescente ~73 vencidos; pool 685 nunca introduzidos. [derivado em 16/09 antes do lote; re-medir no boot]
- **Conteudo:** 136 resumos em resumos/. [derivado: glob] Preventiva: **so 3/22 decks pagam aluguel na UERJ** (MFC, Idoso, Testes Dx); P4, polifarmacia, paliativos e MCCP **sem resumo**.
- **Erros & Cards:** 1041 erros registrados · 1476 cards ativos · 2 needs_qualitative na fila · taxonomia 302 temas. [derivado: db] Reforja 283.
- **Cronograma:** `plano_tarefas` semeada (896: extensivo 735 / rf 139 / custom 22; pendente 632, feita 173 aprox., cortada 91). Fase 1 = semanas 1-7 (104 tarefas / ~3.050q); `python tools/plano.py --listar --semana 1`. Dashboard do Drive = 707 tarefas do extensivo (fonte congelada em `dashboard_snapshot.json`). W1 gravado 16/09.
- **Engenharia:** **suite 714**; `plano_tarefas` = SSOT do plano; `cards_prune.py` = unico caminho de exclusao; `cards_prune.py` = unico caminho de exclusao de card; ledger 109 ids (+E1, E2, F108 propostos; F38 falso positivo de 13/09 declarado no teste vivo).
- **Posicao:** conteudo S17 (nominal S25, atraso 8 sem) [derivado: preparacao_estado] -- na RF; no extensivo, ver linha Cronograma.
- **Datas:** fim da grade 09/10 · **UERJ 01/11** · inscricao UERJ ate **01/10** · recurso ENAMED ate **17/09**.

## Ultima sessao -- s183 (2026-09-16, 13h -> 18h) -- PLANEJAMENTO + ENGENHARIA

Detalhe em `history/session_183.md`. Manha: 5 subagentes de analise (~1,01M tokens) -> hibrido, guias, Medcards, INEP, bloco MFC da UERJ desde 2021. Tarde: PRD + 8 specs e **5 partes implementadas por subagentes (Opus x4, Sonnet x1; ~1,16M tokens; ~2h de relogio)**, cada uma re-medida pelo principal; 2 defeitos pegos no caminho (injecao do player pelo proprio filho; `nota` apagada no re-seed, fechado pelo orquestrador). **Total do dia: 10 spawns, ~2,17M tokens.** Suite 621 -> 714. Commits: 545e127, 4333d2a, 5a788ec, c5dc40e, d9f3bcf, e45c81b, ce05027 + selo.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- Data do ENAMED 2027 e horas na residencia sao **ASSUNCOES**. UERJ 2019-2020 nao verificadas (PDFs removidos da Cepuerj). Gabarito REVALIDA 2026/1 so com login. 2 graficos do guia UERJ corrompidos (Endocrino, Pneumo). Top-5 das outras 4 areas na UERJ = leitura qualitativa, nao contagem.
- Herdadas e vivas: **F100** 4a medicao pendente · **F98** · F7/F104 (semanticas) · D5 · G10 · G5 · F35 · F89 · F79b · F66 · F64 · eixo C do F81 · F80b.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_183.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
