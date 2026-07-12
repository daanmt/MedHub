# Session 118 -- DITC II (LES+SAF) questões: 24q/11a (46%), 13 erros -> 13 cards (797-809) + feedback de calibragem D9 + DDx no resumo + FSRS lote 1

**Data:** 2026-07-11
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 117 (selada no início desta -- commit 655b2fc)

---

## O que foi feito

**Fechamento da s117 (housekeeping):** ao virar o dia, selei a s117 (3 resumos gold Cefaleias/Epilepsias/DITC II + bloco Neuro + 9 cards) -- commit 655b2fc (HANDOFF + session_117.md + INDEX). Push adiado para o fecho de hoje.

**Modo recuperação (usuário cansado, 11-12/07):** dia de sanar pendências + drenar flashcards; rush do cronograma volta 13/07. Aula-base **D9** de DITC II (LES+SAF) entregue no início.

**DITC II (LES+SAF) -- questões:** `registrar_sessao_bulk --sessao 118 --area Reumato` = **24q/11a (45,8%)**. Acumulado 4937 -> 4961.

**Feedback de calibragem (importante):** o usuário apontou que a aula **D9 saiu enxuta-incompleta** -- sem os diagnósticos diferenciais que um D8+ exige. O bloco era quase todo DDx do espectro reumato inteiro (esclerose sistêmica, vasculites, Henoch-Schönlein, fibromialgia, síndrome pulmão-rim, AHAI x microangiopática). **Erro de calibragem do agente**, assumido. Memória `feedback_aula_base_cobertura_escopo` atualizada (refino s118: DDx é parte da cobertura; num D8+ os diferenciais são núcleo, não apêndice).

**13 erros -> 13 cards (797-809), batch (`--errors-file`, 0 pulados):**
- **DDx breadth (buraco de aula):** Q3 (ES x LES -- úlcera digital/Raynaud longo), Q9 (Henoch-Schönlein x Goodpasture -- púrpura + complemento normal), Q7 (LES x fibromialgia -- sinovite/febre), Q5 (nefropatia da SAF x nefrite lúpica), Q11 (AHAI Coombs+ x microangiopática), Q2 (pulmão-rim: granular=LES x linear=Goodpasture x pauci=ANCA).
- **bug nº1 / leitura parcial (eixo nº1 do usuário, 3x):** Q2 (ignorou o padrão granular), Q8 (ancorou na proteinúria 7g -> membranosa, quando cilindros hemáticos + complemento baixo = classe IV), Q13 (não usou o complemento como filtro -- 'aumento de C3' na atividade lúpica é sempre falso).
- **enunciado negativo (Q4):** marcou afirmação verdadeira em vez da falsa (retinopatia por antimalárico = suspensão DEFINITIVA). **REINCIDENTE -- 3ª+ sessão seguida.**
- **lacunas:** Q1 (Evans = AHAI + plaquetopenia imune), Q6 (pior prognóstico = negro/baixo NSE, não articular/ANA), Q10 (parar corticoide crônico -> insuf. adrenal secundária), Q12 (grávida lúpica mantém HCQ + prednisona).
- Erros tagados por doença (LES / Esclerose Sistêmica / SAF / Vasculites) para rastreio da fraqueza no tema certo.

**DITC II.md estendido (paga a dívida da aula):** nova **§11 Diagnósticos Diferenciais do LES e das DITC** (ES x LES, síndrome pulmão-rim, HSP, LES x fibromialgia, AHAI x microangiopática) + 6 armadilhas novas (Evans, prognóstico, retirada de corticoide, filtro do complemento, retinopatia). auto_check PASS.

**FSRS -- drain lote 1 (5 cards):** 203 Esporotricose (4), 201 Hanseníase reação tipo 1 (4 -- sabia manter PQT), 194 Hanseníase dx inicial (1), 206 Hanseníase contatos (1), 64 DM2 meta 7,6% aos 61a (4 -- não caiu no corte universal <7%). **Hanseníase veio fria** (2 brancos + 1 parcial num só lote). Usuário encerrou após o lote 1.

## Padrões de erro identificados

- 🔴 **bug nº1 / leitura parcial (eixo nº1, 3x na s118):** tinha o discriminador (granular=LES, complemento baixo=atividade, classe IV x V) mas ancorou num achado só (proteinúria, hemoptise). Mesmo padrão da s117 (acuidade/contexto) e do simulado.
- 🔴 **DDx breadth -- falha de AULA (do agente):** aula D9 sem os diferenciais. Corrigido no resumo + memória.
- 🔴 **enunciado negativo -- REINCIDENTE (3ª+ sessão seguida):** Q4. Mini-drill agora é prioridade real.
- Lacunas: Evans, prognóstico do LES, retirada de corticoide, gravidez lúpica.

## Artefatos criados/modificados

- `resumos/Clínica Médica/Reumatologia/DITC II.md` -- MODIFICADO (§11 DDx + 6 armadilhas).
- `ipub.db` -- +24q/11a (bulk s118 Reumato); +13 cards (797-809); +5 reviews FSRS (203/201/194/206/64). Local-only.
- Memória `feedback_aula_base_cobertura_escopo` -- refino s118 (DDx como cobertura).

## Decisões tomadas

- **Seção de DDx mora no resumo do LES** ("como distinguir o LES dos mimetizadores") -- é o que o bloco cobra.
- **Erros de DDx tagados por doença** (Esclerose Sistêmica, SAF, Vasculites), não só em "LES", para rastrear a fraqueza no tema certo.
- **Push liberado no fecho de hoje** (s117 + s118 juntas).

## Próximos passos

1. **PRÓXIMA SESSÃO -- plano do usuário (engatilhado no boot):** (a) **revisão/PREPARAR de CADA tema** dos próximos ~50 cards da fila; (b) depois **drenar 50 cards** (atrasados + hoje + backlog). Boot deve puxar a fila viva (`python tools/fsrs_queue.py --list --limit 50 --cluster`). Snapshot dos temas (11/07, Trauma-pesado): Trauma Abdominal (10), Cir. Infantil I (6), Trauma Avaliação Inicial (5), Pancreatite (4), Hemostasia/Arboviroses (3), Ectópica/Emergências Ped/Hanseníase/TCE ped/Choque (2 cada), + ~10 temas com 1.
2. **Hanseníase -- Revisão Direcionada pendente** (cluster frio no lote 1: dx/estesiometria + vigilância de contato 5 anos).
3. **Batch pendente do usuário:** **Imunizações III (29q)** + **Colecistite (18q)**.
4. **Rush do cronograma volta 13/07** (`cronograma.py --sync-drive` obrigatório antes -- Drive stale).
5. **Mini-drill de enunciado negativo** -- reincidente 3ª+ sessão seguida.
