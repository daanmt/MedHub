# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-05 -- **s109: apendicite (aula-base D10/D7) + 60q em 2 blocos (44a, ~73%) + 10 cards (727-736). Papel coordenador-observador ATIVO -> ledger F16-F26 alimentado. Git deixado p/ o Fable.***

## > Proximo passo imediato -- s110
**A) ANTI-REINCIDENCIA (antes de qualquer bloco novo).** Mini-drill dos cards **729 (piuria nao afasta) + 730 (caso classico = operar, nao pedir imagem)** ANTES do proximo bloco -- o reflexo de confirmacao reincidiu 3x num unico bloco. **AGORA COM COMANDO (ciclo 2):** `python tools/fsrs_queue.py --pre-bloco "Apendicite" --janela-horas 96` serve os cards frescos direto. Depois seguir o volume: S12 do cronograma OU continuar R+ gastro, conforme o operador decidir.
**B) CONSOLIDACAO -- resumo de apendicite (F16).** Cunhar `resumos/Cirurgia/Apendicite Aguda.md` no padrao gold (`/estilo-resumo`) a partir da aula-base D10 (registrada no log da s109) + armadilhas dos cards 727-736. Fecha o gap de cobertura E realimenta o RAG (hoje cego a apendicite).
**C) ENGENHARIA -- ciclo 2 ENTREGUE (Fable, 2026-07-06; ledger secao 3g; vibeflow 4/4 PASS).** PRD ORQUESTRACAO DA PREPARACAO completo: F22/F23/F24/F25/F26 RESOLVIDOS + posicao SSOT (op-3) + recomendador do dia. **NOVO NO FLUXO (usar a partir da s110):** (1) posicao NUNCA mais por texto -- `python tools/preparacao.py --set-semana N` (ou `--semana N` no registrar_sessao_bulk); day_plan e `--handoff-block` EMITEM a posicao; (2) plano do dia com contexto: `python tools/day_plan.py --tempo H --energia alta|media|baixa` -> secao "Recomendacao do dia" (mix + projecao; norma em `core/contracts/orquestracao-contract.md`); (3) mini-drill: `fsrs_queue --pre-bloco TEMA`; (4) 2o bloco mesma area/dia: `--acumular` (NUNCA mais falsear sessao); (5) lote de erros: `insert_questao --errors-file lote.json` (transacao unica, dedupe); (6) anulada/banca-divergente: `--status` (registra sem card + gate de evidencia). POSICAO ATUAL REGISTRADA: S12 (conteudo) -- day_plan mostra atraso de 3 sem vs calendario. Restam p/ ciclo 3: F16-F19 (pipeline PDF->md->RAG) + F21 (piso de cobertura no contrato de aula) + F27/F28 (novos, secao 3g).

## Padroes de erro vivos -- atencao do scrum master
- RED RED **Reflexo de confirmacao (apendicite / familia bug nº1):** no caso classico jovem <48h, PEDE exame (US/TC) em vez de operar. Reincidiu **3x num unico bloco** (Q4/Q8/Q11 da s109), horas apos ser carded (730). Isca frequente = ruido urinario (piuria nao afasta, 729). **Prioridade nº1 -- mini-drill 729+730 antes do proximo bloco.**
- RED **Discriminacao de DDx (apendicite):** ancora em "FID = apendicite" e ignora os dados CONTRA (1 semana + leucopenia/linfocitose -> adenite; cronicidade + emagrecimento -> Crohn; stem negativo -> Crohn menos provavel no agudo). Rodar o checklist do "contra": duracao, febre, hemograma, cronicidade.
- RED **Massa/liquido = intervir (mesmo eixo do trauma):** plastrao bloqueado estavel -> "operar ja" (e conservador); dreno -> "liquido livre" (e autolise de base/abscesso localizado). Discriminador = localizado-x-difuso, estavel-x-instavel.
- RED **Pneumotorax hipertensivo (asma AESP pos-IOT):** assimetria de murmurio + dessaturacao subita = puncao de alivio ANTES de mexer no ventilador. Leak persistente (card 213, s108).
- RED **Bug nº1 / parar antes de completar a verificacao:** sifilis congenita (card 189) -- falta de info materna = inadequada = TRATAR o RN (50k UI/kg/dose, 10d).
- RED **Reacao Reversa (Tipo 1):** neurite aguda = Prednisona 1 mg/kg/dia e MANTER a PQT.
- RED **PTT:** hemolise mecanica (Coombs negativo, esquizocitos) -> plasmaferese de urgencia (heparina contraindicada).

## Estado por frente
- **Volume & Metas:** 4514 / 12000 (perf. ~79.0%). Hoje: 60. Ritmo-alvo ~106.9q/dia (70d p/ ENAMED). [derivado: day_plan --handoff-block] | Proximo: S12 ou continuar R+ gastro.
- **Conteudo:** 61 resumos. Gaps: TCE.md, Sistemas de Informacao em Saude.md. **NOVO gap de alta alavanca: `resumos/Cirurgia/Apendicite Aguda.md` (F16)** -- so PDF-fonte + aula efemera + 10 cards; RAG cego ao tema.
- **Erros & Cards:** **+10 cards de erro de apendicite (727-736)** ancorados no elo. Reincidencia intra-sessao no link do card 730 (3x). Pendentes de reforge: 95, 120.
- **FSRS:** 1 atrasados + 2 hoje. Backlog: 361 novos. [derivado: day_plan --handoff-block] (+10 cards novos hoje.)
- **Infraestrutura:** ledger de engenharia cresceu **F16-F26** (papel coordenador-observador, contrato s109; memoria `project_papel_auditor_ledger`). Trilha dupla respeitada (conteudo -> aqui/log; engenharia -> ledger). Rodada de engenharia paralela (Fable/ai-eng) tocou 3d/F20 (venv) + preparou a janela do expurgo (F11, GATED).

## Pendencias ativas
Consolidar `resumos/Cirurgia/Apendicite Aguda.md` (F16, ciclo 3). Mini-drill anti-reincidencia (`--pre-bloco "Apendicite"`) antes do proximo bloco. Reescrever TCE.md + Sistemas de Informacao em Saude.md. Reforjar cards 95/120 (/curar-cards; 120 via gate de evidencia -- pode usar `--status banca-divergente` no re-registro). **Fable ciclo 2 FEITO** (s109 commitada + PRD/specs/4 parts/audits; 12 commits locais). **PENDENTE DO OPERADOR: (a) push p/ origin (gate do harness pede go nominal ao Fable ou `git push` manual); (b) expurgo F11 (mirror+ferramenta prontos, go nominal na janela limpa).**

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_109.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
