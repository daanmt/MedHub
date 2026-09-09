# Session 172 -- O operador tria os 85 cards e escreve o limite do 6o principio; dois auloes expoem 11 pontos em que o repo ensinava a resposta errada

**Data:** 2026-09-08 (noite) -> 2026-09-09 (madrugada) · **Ferramenta:** Claude Code (Opus 5) · **Continuidade:** `session_171.md`
**Sem questoes, sem drill.** Sessao de triagem, contrato e conteudo. O drill dos 44 cards fica para 09/09 por decisao do operador.

---

## 1. A bancada de triagem -- e as 25 inversoes

Os 85 candidatos da s171 foram publicados num Artifact dedicado (`db` capability), cada card com frente,
verso e a evidencia da questao (gabarito x marcada + elo quebrado), **ja abertos com a proposta do agente
marcada** -- ele mexia so no que discordasse e o veredito gravava no banco do artifact para eu ler de volta.

**Resultado: 44 mantidos de 85, com 25 vereditos invertidos (29%).** E a inversao tem padrao limpo, oposto ao
que a triagem do agente supos:

- **Resgatou 12** (eu havia cortado), **8 deles `conteudo`** -- fato duro: janela de 48-72 h da excisao;
  resolucao em 7-10 dias; SIRI em 4-8 semanas; bilirrubina > 0,2 mg/dL/h; diabetes = 25% dos polidramnios;
  "grao de cafe"; doxiciclina 100 mg 12/12 h por 7 d; reforco faltante da febre amarela. **Nada disso se deduz.**
- **Cortou 13** (eu havia mantido): **5 `discriminador`, 2 `mecanismo`, 2 `nuance`** -- todos **regeneraveis**
  a partir do card-nucleo mais o mecanismo, ou o proprio raciocinio da questao reescrito como pergunta.
- **Os 12 `elo_quebrado` sobreviveram sem UMA inversao.** "Nucleo do erro intocavel" esta validado.

⚰️ **O caso que derruba a intuicao:** *"por que insuficiencia uteroplacentaria, RCF e pos-datismo cursam com
oligoamnio?"* foi celebrado na s171 como o melhor achado do 6o principio -- um card que resolve tres
alternativas pelo mesmo mecanismo. **O operador cortou.** Resolver tres de uma vez e o sintoma, nao a virtude:
se um mecanismo unico explica as tres, ele reconstroi as tres e o card nao acrescenta recall. **Economia de
cards nao e rendimento de cards.**

**Veredito literal dele sobre o 6o principio:** *"em resumo, ampliou os pontos de conteudo passiveis de
expansao, mas cunhou bastante ruido -- o que eu justamente temia. nesse sentido, os cards realmente precisam
de juizes de qualidade ate mesmo pedagogica."*

## 2. O contrato ganha o limite que a s171 previu que precisaria

`estilo-flashcard.md` -> novo **§Triagem, o teste de regenerabilidade**: *o aluno consegue REGENERAR esta
resposta a partir do card-nucleo mais o mecanismo que ele ja tem?* **Sim -> nao e card** (vai para o
`verso_regra_mestre` ou para lugar nenhum). **Nao -> e card.** Mais o **corolario que inverte a heuristica**:
`conteudo` (cutoff, prazo, dose, prevalencia, nome de achado, contagem de calendario) rende mais que
`discriminador` derivado da mesma questao -- generaliza `feedback_epidemiologia_dados_cristalizar` de
epidemiologia para **todo fato arbitrario**. O principio 6 **fica**; ganha o filtro.

**Lote inserido:** 17 erros + 44 cards, transacao unica (erros 970 -> 987, cards 1543 -> 1587). A proposta do
agente ficou em `_s8_erros_batch.PROPOSTA_AGENTE.json` para o diff sobreviver.

## 3. 🔬 F87 -- o harness verifica FORMA e e cego a RENDIMENTO

Os **13 cards que o operador reprovou passam** em `audit_card_atomicity.py`, `card_self_sufficiency.py` e nos
predicados de `card_checks.py`. Sao atomicos, um criterio de acerto, frente gerativa, verso curto. O harness
responde *"esta bem formado?"* e nunca *"isto acrescenta recall?"*.

🔎 **O unico predicado que reagiu, e reagiu no lugar certo:** apos aplicar o corte dele, o `insert_questao.py`
emitiu `[AVISO-CARD] distrator-perdido` em **exatamente 2 dos 17 erros** (Liquido Amniotico e HIV) -- os dois em
que os cards cortados eram os que carregavam a alternativa marcada. Existe UM predicado adjacente a rendimento
no repo, ele funciona, e **ele nao bloqueia**. Marca a tensao real entre o 6o principio (ler as alternativas) e
o filtro de regenerabilidade (cortar o deduzivel). Candidato natural a fixture de qualquer gate futuro.

## 4. Absorcao dos dois auloes do Estrategia (ENAMED 2026)

Transcricoes de **Obstetricia** e **Pediatria II** lidas por 2 subagentes Opus contra o corpus (read-only, com
evidencia `arquivo:linha`). **O achado nao foi o conteudo novo -- foi o conteudo VELHO que continuava sendo
ensinado.** Toda linha foi conferida por mim contra a transcricao antes de editar.

🔴 **O pior: o clampeamento do cordao estava errado em DOIS arquivos, em direcoes OPOSTAS.**
`Reanimacao Neonatal.md` dizia "30 s se >= 34 sem / 60 s se < 34"; `Cuidados Neonatais.md` dizia exatamente o
espelho (">60 s no termo / 30 s no prematuro"). Nenhum dos dois esta certo -- a diretriz SBP de 12/06/2026 manda
**60 s para qualquer IG**. E o efeito e o que assusta: **um erro validava o outro** -- quem abrisse os dois veria
dois numeros e concluiria que a distincao existe.

**`Reanimacao Neonatal.md` reescrito por inteiro** (stub -> active). A diretriz mudou em 12/06/2026 e o arquivo
era pre-2026: ordenha de cordao (nova; `grep ordenha` no repo dava **zero**); estimulo tatil virou **15 s** (nao
"duas vezes"); **revisao de tecnica entre degraus** ausente -- e e o ponto que as bancas mais exploram hoje;
**faixa de FC 60-100 pos-IOT** ausente (o arquivo so tinha <100 e <60, o que apaga o degrau que separa quem
entendeu a escada); ventilador em T preferencial; mascara laringea de resgate -> interface de 1a linha em >= 34 s
e **proibida** em < 34 s; FiO2 60% na IOT com titulacao de 20 em 20; escalonamento progressivo de FiO2 removido.

**Imunizacoes** (2a maior fraqueza, 24 erros): "o reforco de polio aos 4 anos foi abolido" era verdade **ate
02/08/2026** -- reintroduzido com VIP em 03/08 (NT 64/2026). O **melhor cenario do tetano tinha so metade**
(exigia "ultima dose < 5 anos" e omitia "**E >= 3 doses**"). A **contagem do componente tetanico** -- o `faltou`
literal do erro 14 do Simulado 8 -- nao existia em lugar nenhum. Mais pneumo 23 -> 20 no idoso, BCG de mae
bacilifera -> rifampicina 4 meses **sem PPD**, Abrysvo a partir de 28 sem (32-36 e ACIP/EUA).

**Ictericia e Sepse Neonatal** -- fecha o loop do erro 2 do Simulado 8: o arquivo dava "> 0,5 mg/dL/h **ou**
> 5 mg/dL/dia", e os dois numeros nao fecham (5/dia = 0,21/h). Conferi no comentario da **propria banca**:
ENARE/ENAMED 2025 cobra **> 0,2 mg/dL/h**, e persistencia **7 d no termo / 14 no pre-termo** (o arquivo dava
14/21). **Ele errou a questao aplicando o 0,5 que estava aqui.** Sao duas reguas (patologica x prolongada) que o
arquivo colapsava numa. Junto: sepse tardia e **oxacilina + amicacina**; o arquivo prescrevia vancomicina de
rotina **e** tinha armadilha dizendo "vanco, nao oxacilina".

**GO:** `Pré-Natal.md` colapsava **tres faixas de carga viral em duas** no HIV -- a faixa do meio (detectavel
porem < 1.000) **recebe AZT**, e ha erro registrado no banco exatamente nesse tema. Criterios de NTG trocaram o
eixo (pediam contagem de dosagens, o arquivo escreveu duracao).

**Diarreia:** "comprometimento do estado geral, disenteria, colera grave" listados com virgula -- a virgula
transformou uma **conjuncao** em tres gatilhos e liberava ATB para toda crianca com sangue nas fezes.

**Nao absorvido de proposito (o repo esta mais certo que a aula):** cicatriz uterina segmentar x corporal, e
swab de EGB em 35-37 semanas.

## 5. Auditoria de evidencia -- 5 pontos contestados, e o saldo constrange os dois lados

Os pontos em que repo e aula divergiam foram para o `evidence-researcher` em vez de para o meu palpite.
**Em 2 a aula estava errada, em 2 o repo estava errado, em 1 os dois estavam.**

- **Gluconato de calcio -- as DUAS versoes do arquivo erradas.** Os 3 parametros disparam **suspensao**; o
  gluconato dispara em **arreflexia patelar OU dificuldade respiratoria** (e PCR). **Oliguria isolada NAO
  antidota** -- suspende e dosa magnesio. O corpo errava incluindo a diurese; a armadilha errava excluindo a
  arreflexia: **cada uma corrigia metade do erro da outra e nenhuma acertava.** (MS/Fiocruz-IFF 2023 + FEBRASGO 8/2018)
- **Beta-hCG -- o repo NAO estava desatualizado.** 1.500-2.000 e FEBRASGO 22/2018; 3.500 e **ACOG PB 193/2018**,
  nao do MS como a aula afirmou. Nao competem: 2.000 otimiza **sensibilidade**, 3.500 otimiza **especificidade**
  (nao interromper topica viavel ainda invisivel). Ambos com a mesma excecao: gestacao multipla.
- **Hamilton -- a aula acertou o veredito e errou o motivo.** FIGO 2022 (PMID 35297039, integral via PMC): a
  massagem uterina **continua** no 1o degrau do tratamento; o que desceu foi a **compressao bimanual**, hoje
  medida temporizadora. O que a FIGO tirou foi a massagem sustentada da **PREVENCAO** -- a aula colapsou
  prevencao e tratamento. De quebra: tranexamico repete se persistir apos 30 min ou recorrer em 24 h, nao "a cada 6 h".
- **Cortes da PE -- ninguem errado; a aula misturou dois eixos.** Creatinina > 1,1 e transaminases 2x LSN sao
  **gravidade da PE** (ACOG 222/2020) -- os numeros do repo, CONFIRMADOS. TGO/TGP >= 70, BT >= 1,2, LDH >= 600
  sao **HELLP** (Tennessee). E o 70 U/L **e** o mesmo "2x LSN" em unidade absoluta.
- **FiO2 60% no prematuro -- CONFIRMADO VERBATIM, e o PDF nao e restrito** (o subagente de Pediatria supos que
  fosse). Guinsburg R, Almeida MFB, PRN-SBP, Diretrizes 2026, 12/06/2026, DOI 10.25060/PRN-SBP-2026-2. Titular
  **+/-20% a cada 30 s**, blender obrigatorio. 🔴 A SBP foi **alem do ILCOR** (que recomenda apenas >= 0,30), e a
  evidencia e **fisiologica, nao de desfecho**: TORPIDO 30/60 (JAMA 2026) deu morte/lesao cerebral **47% x 48%**
  -- o que mudou foi menos massagem e menos adrenalina no grupo 0,60.

## 6. Artefatos

- `.claude/commands/estilo-flashcard.md` (+ espelho `.agents/`) -- §Triagem novo, limite do 6o principio, `description` atualizada
- `AUDITORIA_MEDHUB.md` §6p -- **F87** (ABERTO, nao agendado -- fila congelada)
- `core/simulados/_s8_erros_batch.json` (reconstruido pelos vereditos) + `_s8_erros_batch.PROPOSTA_AGENTE.json` (novo)
- **9 resumos:** `Reanimação Neonatal.md` (reescrito, stub -> active) · `Cuidados Neonatais.md` · `Imunizações.md` ·
  `Icterícia e Sepse Neonatal.md` · `Diarreia.md` · `GO/Pré-Natal.md` · `GO/[OBS] Sangramentos da Primeira Metade.md` ·
  `GO/Síndromes Hipertensivas da Gestação.md` · `GO/Hemorragia Pós-Parto.md` · `GO/Gravidez ectópica.md`
- Memoria: `feedback_triagem_cards_pos_simulado` reescrita (o criterio "no que resolve varias alternativas" **revogado**)
- Commits: `f453262` (contrato + F87 + lote) · `cfea19f` (absorcao dos auloes) · `2f159ee` (auditoria de evidencia)

## 7. Decisoes

- **O 6o principio fica, com filtro.** Nao foi revogado -- a ampliacao e real e o operador a confirma. O que
  faltava era o juiz, e o juiz e **pedagogico**, nao estrutural.
- **A triagem e humana e acontece ANTES do `insert_questao.py`**, com a lista integral guardada em disco para o
  corte poder ser derrubado. Superficie validada: Artifact com os candidatos ja marcados, gravando veredito no db.
- **Ponto contestado nao vira edicao de resumo por palpite** -- vai para o `evidence-researcher`. Rendeu 2
  correcoes que eu teria feito ao contrario se tivesse seguido a aula.
- **Fila de engenharia segue CONGELADA.** F87 foi numerado, nao agendado.

## 8. Pendencias

- 🃏 **Drill dos 44 cards novos** + fila de hoje. **Pool 701 nunca introduzidos**, teto 60/dia.
- 📉 🔴 **VOLUME:** as **100 questoes do Simulado 8 continuam sem registro** em `sessoes_bulk` -- fluxo da planilha,
  nunca digitando (F37). E **0 questoes** hoje, com ritmo-alvo em 65,4q/dia.
- 📚 **Backlog de conteudo dos auloes (nao executado):** criar `Distúrbios Respiratórios do Período Neonatal.md`
  (cobertura **zero** no repo -- SDR/TTRN/SAM, com o corte de 35 semanas como discriminador) e
  `Infecções Congênitas.md` (**nenhum tratamento** de toxo/CMV/herpes/varicela existe no repo). Em GO:
  prevencao da prematuridade -- **"cerclagem" nao aparece uma unica vez no repo inteiro** -- alem de secoes de
  distocias, Bishop/inducao e rotura uterina.
- ⚠️ **RAG cego:** `index_resumos.py` falhou (**Ollama fora do ar**) e o auditor de evidencia teve **zero
  resultados** nas 3 consultas locais. Nada do que foi corrigido hoje e alcancavel por busca semantica ate reindexar.
- 📄 **Manual de Gestacao de Alto Risco (MS 2022)** excede o teto de 10 MB do fetch e barrou a confirmacao
  primaria em 2 itens da auditoria. E a bibliografia declarada do ENAMED -- baixa-lo uma vez resolve os dois.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.

---
*Anterior: `session_171.md` · Macro: `ESTADO.md` · Ledger: `AUDITORIA_MEDHUB.md` · Auditoria: `docs/MEMORIA-AUDITORIA.md`*
