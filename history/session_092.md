---
type: session
sessao: 092
data: 2026-06-26
area_foco: Semana 10 modo volume -- Preventiva (Sistemas de Informação) + Ginecologia (Planejamento Familiar)
---

# Sessão 092 -- Semana 10 em modo VOLUME (recuperação de cronograma)

## Contexto
Aberta após o encerramento formal da s091, a pedido do usuário: **modo volume / recuperação de atraso no cronograma** -- foco em fechar tasks e acumular questões, não em aulas longas. Revisado o `Cronograma.pdf`: as **6 tasks iniciais da Semana 10** mapeadas (tema + sub-temas + nº de questões = **147q**), com duas descobertas de planejamento: **T1 e T6 são o mesmo tema** (Sistemas de Informação -- Teoria + Revisão) e **T5 não tem caderno de questões** (só teoria; "questões na próxima tarefa"). Calibração de aula mudada para **refresh COMPRIMIDO** (gatilhos + armadilhas), aceito pelo usuário no modo volume.

## O que foi feito
- **Revisão do cronograma (S10):** T1 Sistemas de Informação Teoria (23q) · T2 Exantemáticas Teoria (18q) · T3 Cirurgia Infantil Pt3 (22q) · T4 Planejamento Familiar Revisão (42q) · T5 Síndromes Hipertensivas Teoria (**0q**, só leitura) · T6 Sistemas de Informação Revisão (42q). Total **147q**.
- **T1 + T6 -- Sistemas de Informação em Saúde:** refresh comprimido (SIM/SINAN/SINASC/e-SUS/complementares). Dois cadernos: **65q / 60 (92%)**. 4 erros únicos -> 4 cards (#570-573).
- **T4 -- Planejamento Familiar (Revisão):** refresh comprimido (Pearl/LARC, elegibilidade OMS, DIU, CE, esterilização). Bloco **42q / 32 (76%)** -- o mais difícil do dia. 10 erros -> 10 cards (#574-583).
- **Volume `sessoes_bulk` s092:** Preventiva 65/60 + Ginecologia 42/32 = **107q / 92 (86%)**.
- **2 resumos turbinados** (Regra de Acúmulo): `Sistemas de Informação` (SISVAN, DO causa externa, causa básica) e `Planejamento Familiar` (DIU pós-parto cat 3, bariátrica disabsortiva, exclusão por DUM).

## Padrões de erro identificados
- **Mudança de eixo vs s091:** aqui o gargalo foi **CONTEÚDO FINO**, não execução de prova -- temas de revisão expõem lacunas factuais.
- **🔴 Cluster Declaração de Óbito (T6, 3 erros):** causa externa **É emitida pelo IML** (não "não se emite") · competência = **legista sempre** (não SVO; SVO é morte natural) · causa básica = a que **inicia** a cadeia (HAS), não a intermediária (ICC).
- **⚠️ SISVAN errado 2× (T1 e T6, mesma questão):** marcador de consumo = **dia anterior** ("ontem"), não último mês. Alerta "não errar 2× pelo mesmo motivo".
- **🔴 Sub-cluster DIU (T4, 4 erros):** cobre é eficaz **imediato** (sem barreira) · gravidez+DIU <12sem retira **se fio visível** · pré-inserção = **exame pélvico** (não USG) · exclusão de gravidez = **DUM** (não teste). + elegibilidade: bariátrica disabsortiva -> não oral; puerpério 48h-4sem -> DIU cat 3; dismenorreia secundária -> SIU-LNG.

## Artefatos criados/modificados
- **14 cards novos** (#570-573 Sistemas de Informação · #574-583 Planejamento Familiar).
- **2 resumos turbinados:** `Preventiva/Sistemas de Informação em Saúde.md`, `GO/Planejamento Familiar.md`.
- **2 memórias:** novo `project_contrato_execucao_cronograma`; refino de `feedback_aula_descomprimida_preferencia` (calibração por tipo de bloco).
- Contadores: **354 erros · ~384 cards ativos**.

## Decisões / pendências
- **FRENTE NOVA (pedido do usuário) -- formalizar o contrato de execução `cronograma↔resumos↔aulas-base`:** conferir o cronograma antes de cada bloco (sub-temas EXATOS + nº de questões) -> ancorar no resumo -> calibrar a aula pelo tipo (teoria nova = **descomprimida**; revisão/volume = **comprimida**). Esboçar `core/contracts/execucao-cronograma-contract.md` na s093. Spec em `project_contrato_execucao_cronograma`.
- **Calibração de aula refinada:** bloco NOVO de teoria densa -> DESCOMPRIMIR (T2/T3 na s093); revisão/decoreba -> comprimir.
- 🐛 **`Sistemas de Informação em Saúde.md` tem redação ruim/imprecisa -> candidato a REESCRITA.**
- Mantidas: resumo de ectópica (PDF Sangramentos 1ª Metade); reescrever `TCE.md`; corrigir ramp do `performance.py`.

## Meta de junho
- Meta acumulada: **4.500**. Acumulado atual: **3.946**. Déficit: **554**.

## Próximo (s093)
**Matar T2 + T3** das 6 tasks da Semana 10, com **AULA-BASE DESCOMPRIMIDA** (são blocos novos de teoria). **Conferir o cronograma antes** (sub-temas já no HANDOFF: T2 = Rubéola/Varicela/Mão-Pé-Boca/Escarlatina, 18q; T3 = Hidronefrose/Criptorquidia/Escroto Agudo/Neuroblastoma/Wilms, 22q). Em paralelo, **esboçar o contrato de execução**. Drenar FSRS (30 novos #554-583 + vencidos).
