---
type: session
sessao: 094
data: 2026-06-27 22:17 (estudo e registro: 2026-06-27, sábado)
area_foco: Fecha a Semana 10 (5 tasks restantes; 11/11) + 4 resumos novos + frente Revisão Calibrada (PRD) + registro onboarding fundacional
---

# Sessão 094 -- Fecha a Semana 10 + frente Revisão Calibrada (PRD)

## Contexto
Sessão de fechamento de bloco do cronograma e de duas frentes de método. **Matou as 5 tasks restantes da Semana 10** (que ficaram da s092+s093) -- **126q/87 (69%)** em 5 blocos -- e com isso **FECHOU a Semana 10 (11/11 tasks, 273q: s092 107 + s093 40 + s094 126)**. Próxima = **Semana 11**. Em paralelo, **criou 4 resumos novos** (os 4 temas teóricos do dia não tinham resumo de base) e abriu **duas frentes estratégicas**: um **PRD de Revisão Calibrada** (escala de dificuldade 1-10 calibra a descompressão; aglutina `/revisar` + `/refrescar`) e o **registro "onboarding fundacional"** (formato de resumo para temas onde o usuário é iniciante). Norte estratégico mantido: **Psiquiatria UFRJ/IPUB**; sprint total ENAMED (13/09); também UERJ (MFC) e USP. Acumulado **4.112 (41% da meta-prova 10k)**.

## O que foi feito
- **Meningites (Revisão) -- Infecto -- 50q / 35 (70%).** Aula comprimida (revisão). Eixo dos 4 erros: **leitura do LCR por dado parcial** (glicorraquia relativa), fronteiras viral × herpes × Hib, e quimioprofilaxia meningocócica. **2 não-erros** (gabaritos ruins: rifampicina como 1ª linha; "meningococo é o mais comum no BR").
- **Distúrbios Ácido-Base / Gasometria -- Nefrologia -- 19q / 5 (26%).** **Lacuna conceitual** (ânion-gap × base excess, papel do cloro/potássio, compensação × distúrbio misto) **DESTRAVADA via aula**. O bug nº1 (ler o valor absoluto, não o esperado) **migrou do LCR para a PaCO₂**. Tema de iniciante -> resumo reescrito no registro onboarding.
- **Pneumologia Intensiva -- Pneumo -- 15q / 12 (80%).** Erros: ventilação protetora (recrutamento agressivo ↑ mortalidade/ART), paralisia de prega vocal × estenose subglótica, máscara laríngea não protege contra aspiração. Tema de iniciante -> resumo onboarding.
- **Diabetes - Complicações Crônicas -- Endócrino -- 17q / 13 (76%).** **As 4 erradas TODAS no eixo cirúrgico-vascular do pé diabético:** controle de foco infeccioso > exame; revascularizar ANTES de amputar; ITB falso-normal por calcificação; mal perfurante plantar = úlcera neuropática.
- **Hepatites Virais -- Hepato -- 25q / 22 (88%).** Ataca **Hepato** (área mais fraca). Erros no **eixo HBV ocupacional/pós-exposição** (anti-HBs ≥10 = protegido, só notifica SINAN; não-resposta = repetir esquema completo 3 doses) + 1 capciosa (HBeAg com a exceção do mutante pré-core).
- **4 resumos NOVOS criados** (Diabetes Comp. Crônicas, Distúrbios Ácido-Base, Pneumologia Intensiva, Hepatites Virais). Os de **Ácido-Base e Pneumo foram REESCRITOS no novo registro "onboarding fundacional"** (a pedido do usuário, iniciante nesses 2 temas). Total de resumos: **51**.
- **Volume s094:** 5 blocos = **126q / 87 (69%)**. Acumulado **4.112**.

## Padrões de erro identificados
- **Eixo dominante (recorrente) = bug nº1 / "não completar a verificação/conduta".** Mesma assinatura migrando de tema em tema:
  - **Leitura de exame por dado parcial** (Meningites: LCR lido pela glicorraquia relativa isolada, não o conjunto) -> **migra para a PaCO₂** na gasometria (lê o valor absoluto, não o esperado pela compensação).
  - **Não fechar a conduta** (pé diabético: acerta o quadro, erra a sequência cirúrgico-vascular -- foco infeccioso antes do exame; revascularizar antes de amputar). 4/4 erros do bloco no mesmo eixo.
  - **HBV ocupacional/pós-exposição:** a regra de conduta pós-acidente (anti-HBs ≥10 / não-resposta) não estava fechada.
- **Lacuna de conteúdo real (não execução) em Ácido-Base (26%)** -- tema de iniciante; destravado pela aula. Aqui o gargalo foi matéria, não processo.

## Decisões estratégicas (forks do usuário)
1. **Contrato de Revisão Calibrada (PRD aprovado).** Escala de **dificuldade do tema 1-10** calibra a descompressão da revisão (10 = onboarding total, referência = resumo de DM; comprime se fácil / quente / baixa-prevalência no ENAMED; **nota dada pelo usuário OU inferida pela performance**). **Aglutina `/revisar` + `/refrescar`** numa competência única (prepara o tema para exercícios = revisão ampla, ou para flashcards = revisão direcionada; o refresh **não toca o FSRS**). **Integra cronograma + `/performance`** (área fraca -> nota maior -> revisão mais descomprimida). PRD gerado via workflow em `docs/plans/s094-revisao-calibrada-PRD.md`; **6 questões abertas APROVADAS** pelo usuário. Memória: `project_revisao_calibrada`.
2. **Registro "onboarding fundacional".** Formato de resumo para temas onde o usuário é iniciante: siglas definidas na 1ª aparição, cada nuance esgotada antes de seguir, cada parâmetro explicado, foco na vida médica prática. Aplicado a Ácido-Base + Pneumo Intensiva. Memória: `feedback_registro_onboarding_iniciante`.

## Artefatos criados/modificados
- **4 resumos novos:** `resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Crônicas.md`, `resumos/Clínica Médica/Nefrologia/Distúrbios Ácido-Base.md`, `resumos/Clínica Médica/Pneumologia/Pneumologia Intensiva.md`, `resumos/Clínica Médica/Hepatologia/Hepatites Virais.md` (os 2 últimos de Nefro/Pneumo no registro onboarding).
- **PRD:** `docs/plans/s094-revisao-calibrada-PRD.md` (novo).
- **`sessoes_bulk`:** 5 linhas da sessão 94 (todas data 2026-06-27).
- **2 memórias novas:** `project_revisao_calibrada`, `feedback_registro_onboarding_iniciante` (+ `MEMORY.md` atualizado).
- Contadores: **51 resumos · 359 erros · ~389 cards** (#588 último -- **flashcards do dia ainda a cunhar**).

## Frentes abertas (s095+)
1. **Cunhar os flashcards do dia** (Meningites + Ácido-Base + Pneumo + Diabetes + Hepatites) -- combinado para o fim do dia / s095; ainda pendente.
2. **Implementar o PRD de Revisão Calibrada** -- fase de execução. **Bloqueio:** `tools/cronograma.py` + `core/cronograma/grade.json` ainda não existem (dependência da frente cronograma-sync, F1 do ultraplan s093).
3. **Semana 11 do cronograma** (S10 fechada -> avança).
4. **Gaps de cobertura de aula** detectados (candidatos a card/andaime): **pé diabético cirúrgico-vascular**; **HBV ocupacional/pós-exposição**.
5. Carry-over s093: sessão dedicada de Cirurgia; integrar `/schedule` na gestão de calendário.

## Próximo (s095)
**A) Cunhar os flashcards do dia** (5 blocos de erro -> cards). **B) Semana 11** do cronograma. **C) Engenharia -- F1 do sync** (`tools/cronograma.py` + `grade.json`): inexistentes, e agora também **desbloqueiam o PRD de Revisão Calibrada** -> F2 radar -> F3 day_plan -> F4 contrato. **D) FSRS** (#554-588 + vencidos via `/revisar`). Convenção mantida: registros com **data + hora**.
