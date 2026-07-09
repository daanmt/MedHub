# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-09 -- **s114: S12 avanca 2/6 (Vigilancia+SI+MFC 96,2% + DM Tipo2+Agudas+Cronicas completo 87,2%, 100q/dia) + achado de dois SSOTs no cronograma (ordem=xlsx Drive editado a mao / detalhamento=Cronograma.pdf) + correcao do marco ENAMED (10k meta-prova, 12k era o valor exposto por engano) + usuario delegou autoridade permanente pra recalibrar dificuldade divergente.***

## > Proximo passo imediato
1. **Mesmo dia (09/07), sessao seguinte (pedido explicito do operador):** HAS Pt. 2 (Teoria, resumo -- so PDF cru em `resumos/Clínica Médica/Cardiologia/`, extrair+autorar antes do bloco de questoes).
2. Depois: DITC II (Teoria, extensivo -- estende `DITC.md` existente, nao e tema-zero).
3. Restam da S12 depois disso: Disturbios do Potassio (tema-zero, so PDF cru), Cefaleias+Epilepsias (tema-zero, nem PDF-fonte localizado ainda -- maior risco da semana).
4. FSRS: 9 atrasados + 5 hoje (backlog 400 novos) -- `/revisar` ou `fsrs_queue.py`.

## Padroes de erro vivos -- atencao do scrum master
- RED **REINCIDENCIA CONFIRMADA (2x): crianca DM1 doente = hipoglicemia, nao CAD** -- cruzou automatico com o erro #229 (overlap 0,63) MESMO apos a aula-base da propria sessao (s114) ter citado o cenario quase literalmente horas antes. Ensinar nao bastou -- candidato a mini-drill dedicado do card 775 (fsrs_queue --pre-bloco), nao so mais uma entrada na fila normal.
- RED **Ancoragem no farmaco (familia bug no1b) reapareceu:** glibenclamida marcada por reflexo "remedio de diabetes conhecido" num quadro de acidose latica por METFORMINA -- nao checou se o mecanismo do farmaco batia com o quadro clinico (AG aumentado, sem cetose).
- RED **Fato certo, pergunta errada (familia bug no1c):** "albuminuria e mais precoce que creatinina" (verdadeiro, serve pra ESTADIAR nefropatia) aplicado numa pergunta de CLEARANCE (por que esta paciente hipoglicemiou -- creatinina/TFGe e quem responde).
- RED **Enunciado longo com ruido decisivo escondido:** questao de DM2 grave (55a, obesa) tinha os 2 numeros que decidiam (GJ 323, HbA1c 10,7%) afogados num painel laboratorial de 15+ itens com varios red herrings (ferritina, transaminases, TSH normais) -- extrair o que decide antes de resolver.
- Padroes antigos (enunciado negativo, pe de Charcot, mapa de reforco instavel, ferro x folato) seguem arquivados, sem novo evento nesta sessao.

## Estado por frente
- **Volume & Metas:** 4865 / 10000 (perf. ~79.4%). Hoje: 100. Ritmo-alvo ~77.8q/dia (66d p/ ENAMED). [derivado: day_plan --handoff-block]
- **Conteudo:** 63 resumos, 4 enriquecidos nesta sessao (Vigilancia em Saude; DM Complicacoes Cronicas x2; DM Tipo 2; DM Complicacoes Agudas x2). Gap novo sinalizado: `Sistemas de Informacao em Saude.md` com prosa fora do padrao-ouro (autoria original s069, nao e dano do episodio Antigravity) -- candidato a reforja, nao feito ainda.
- **Erros & Cards:** +8 erros analisados nesta sessao, 7 cards novos (769-771, 773-775) + 1 banca-divergente sem card (772, gate F26 -- banca admitiu ambiguidade no proprio gabarito).
- **FSRS:** 9 atrasados + 5 hoje. Backlog: 400 novos. [derivado: day_plan --handoff-block]
- **Infraestrutura:** corrigido o marco ENAMED em `performance.py`/`day_plan.py` (ainda referenciavam 12k pos-recalibracao s093/099, que fixou 10k como meta-prova; 12k virou teto/stretch exposto a parte) -- inflava o "faltam" em ~2.000q. Fixture `SEED` do harness ajustado (MFC saiu, mesmo padrao ja usado pra Vulvovaginites em s110p2). Achado novo de arquitetura: cronograma tem DOIS SSOTs -- ordem/semana das tarefas vem do xlsx do Drive (editado a mao pelo usuario), detalhamento vem do `Cronograma.pdf` intocado; `grade.json` so deriva do PDF e nao captura a reordenacao manual (`project_cronograma_dual_ssot`). Usuario delegou autoridade permanente pra sobrescrever nota de dificuldade divergente sem pausar (`feedback_autoridade_recalibragem_dificuldade`).

## Pendencias ativas
Aula-base de Pre-Natal I (debito antigo, arrastado -- resumo pronto, falta so a escada de degraus). Apendicite Aguda -- verificar status do resumo (F16, nao tocado nesta sessao). Reescrever TCE.md + **Sistemas de Informacao em Saude.md (achado novo desta sessao)**. Reforjar cards 95/120 (120 via gate de evidencia). Corrigir rotulo `sessao_num=115->114` do bloco Endocrino de hoje (erro meu, tratei 2 blocos do mesmo dia como sessoes separadas) -- bloqueado pelo classificador de auto mode, nao insisti; nao afeta volume/performance (agregam por area+data), so a rastreabilidade sessao-a-sessao. Ledger `AUDITORIA_MEDHUB.md`: F21/F30 seguem abertos. Proximos achados comecam em F34.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_114.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
