---
type: reference
layer: root
status: active
---

# Fundamentos de Ensino-Aprendizagem do MedHub -- principio nomeado x mecanismo que o implementa

*Criado na sessao 184 (2026-09-17). Origem: duas transcricoes trazidas pelo usuario (J.R. Smith, "The Study System That Made Me A Doctor At The World's Top Hospital" e "I NEVER Take Notes Anymore -- My Full AI System As A Doctor") + quatro varreduras de literatura por subagentes isolados (relatorios crus em `docs/research/2026-09-17-*.md`; fontes com forca de evidencia na secao 6). Encoding: ASCII limpo nas pontuacoes (`->`, `--`, aspas retas), conforme `AGENTE.md` secao 4.5. Plano de reformas derivado: `PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md` (raiz).*

---

## 0. Por que este documento existe

A arquitetura de ensino do MedHub foi construida **empiricamente**, sessao a sessao, a partir de correcoes do usuario (s075 -> s183) e de padroes de engenharia herdados do `/ai-eng` e do agente irmao `agente-daktus-content`. Nenhum portador nomeava o **principio da ciencia da aprendizagem** por tras de cada decisao. Sem o nome, cada decisao nova era re-derivada do zero -- e uma reforma bem-intencionada podia contradizer um principio que o sistema ja obedecia sem saber.

Este documento faz tres coisas, e so tres:

1. **Nomeia o principio** (com fonte verificada) atras de cada mecanismo vivo, e diz se o mecanismo o **CONFIRMA**, esta em **TENSAO** com ele ou revela uma **LACUNA**.
2. **Declara o ledger de friccoes** (secao 3): quais atritos do estudo sao **virtuosos** (produzem aprendizagem; nunca automatizar) e quais sao **viciosos** (custam tempo e nada devolvem; automatizar sem do). E a lente que faltava para julgar toda reforma de "reduzir atrito".
3. **Registra lacunas e tensoes** com destino no ledger (`AUDITORIA_MEDHUB.md` F109-F112).

🔴 **Fronteira:** este arquivo e **explicativo**, nao normativo. A NORMA continua morando nos contratos e skills (`core/contracts/`, `.claude/commands/`); aqui vive o **porque**, com ponteiro para o portador do **o que**. Decisao nova de ensino: conferir o principio aqui **antes** de re-derivar; se a decisao contradiz um principio, o onus e **medir** (desenho n-of-1, secao 6 item E) antes de mudar contrato. Regra de manutencao herdada de `docs/MEMORIA-AUDITORIA.md`: numero sem data e claim que envelhece.

---

## 1. Os tres motores (Learn -> Retain -> Apply) e onde cada um vive

O video 1 organiza o sistema em tres fases. O MedHub ja tinha as tres, com outros nomes -- o mapa serve para ver que **nenhuma fase esta faltando** e onde cada uma e medida.

| Fase (video 1) | O que a fase promete | Superficie no MedHub (portador) | Como se mede aqui |
|---|---|---|---|
| **LEARN** -- primeira exposicao eficiente e de alta qualidade | video curto > aula longa; canal duplo (Mayer); "a primeira exposicao nunca basta" | Aula EMED/PDF (usuario) -> **`/aula-base`** so quando tema-zero ou nota D8+ (gatilho hibrido, `AGENTE.md` secao 1.2); tema D5 ou menor = **questoes primeiro**, aula depois mirando o buraco. `resumos/` = documento vivo por tema. | taxa de acerto pos-aula (Meningites 53% -> 75%); nota 1-10 registrada `fonte='aula'` (Clausula 10) |
| **RETAIN** -- repeticao espacada, todo dia, simples | Anki de manha antes de tudo; cards do bloco encerrado continuam; "estudar para o eu futuro"; simplicidade > intensidade | **FSRS-6** (`py-fsrs` 6.3.2, retencao-alvo 0,9, parametros default) no card + **curva no nivel do TEMA** (`forgetting-curve-contract.md`: radar de dormencia, `review_log`, `DORMENTE_DIAS = 21`) + teto **60/dia, 90 em divida** (`fsrs-management-contract.md`) + **player de cards** (Clausula 12) | retencao por lote (s164 54% -> s167 90% -> player 75% em 16,5 min); divida `vencidos = atrasados + hoje`; CV do calendario (`fsrs_load.py`) |
| **APPLY** -- prova como habilidade treinavel; achar o gap antes que a prova ache | efeito de teste; questoes > releitura; ultimas 1-2 semanas so questoes | **60 questoes/dia question-first** (s159) + **Autopsia** de todo bloco (`analisar-questao.md` secao 3.3) + **Ledger de Habilidades** (secao 10) + **`docs/PLAYBOOK_EXECUCAO_PROVA.md`** + slot de simulado a cada 4 semanas (R3, `orquestracao-contract.md`) + S29-S30 da grade **sem conteudo novo** por construcao | banco 79,1% x simulados (S6-S9 80-86%; ENAMED real 75); 60% execucao x 40% lacuna na serie de 9 provas; override do modal medido 13/13 (s180) |

O que o mapa mostra de novo: a fase RETAIN do video e **card-first** (deck pre-pronto, "unsuspend na mesma noite"); a do MedHub e **erro-first** (o card nasce do elo que quebrou). E uma escolha deliberada, e a evidencia esta do lado dela (Deng 2015: cards proprios predisseram a nota; o deck comercial pronto nao -- secao 2, P4) -- mas ela deixa um buraco especifico na Fase 2 do plano (F111, secao 4).

---

## 2. Principio a principio

Formato de cada entrada: **o que a literatura diz** -> **como o MedHub ja faz** (portador) -> **estado** (CONFIRMA / TENSAO / LACUNA) com a **medida interna** quando existe. Referencias completas na secao 6.

### P1 -- Ilusao de fluencia / "massing illusion" (Kornell 2009; Kornell & Bjork 2008)

Familiaridade nao e retencao: no experimento de flashcards, o espacamento venceu o cramming para **90% dos participantes** e, ainda assim, **72% acreditavam que o cramming tinha sido melhor** (Kornell 2009). O julgamento e ancorado na fluencia do momento, nao na memoria do desempenho.

**No MedHub:** o principio foi **descoberto na pratica, com o usuario corrigindo o agente duas vezes** -- s150 (*"nao e so porque a afirmacao esta no resumo que eu sei"*) e s171 (*"o aprendizado e um movimento circular"*), registrado em `feedback_diagnostico_resumo_nao_e_conhecimento` e na regra de `analisar-questao.md` secao 3.1: o sinal de conhecimento e o **historico de recall** (`fsrs_revlog`), nunca a presenca do texto. **Medido:** s169 -- o consolidado segura ~85% e os **erros analisados horas antes voltam a 25%**; F100 (s179) -- prosa densa entregue 1x = zero retencao em 24h para fato arbitrario.

**Estado: CONFIRMA, e com numero proprio.** Corolario que ja vale: "analise feita", "resumo escrito" e "card cunhado" sao eventos do agente, nao do aluno.

### P2 -- Curva de esquecimento (Ebbinghaus 1885; Murre & Dros 2015; Custers 2010)

O esquecimento e rapido no inicio e desacelera. A cifra popular "70% esquecido em 24h" **nao vale**: o numero de Ebbinghaus em 1 dia e *savings* = 0,33 (economia no reaprendizado, nao proporcao lembrada), em silabas sem sentido, com n = 1. A replicacao (Murre & Dros 2015) bate ate 6 dias. Em medicina, a revisao de Custers 2010 mede **2/3 a 3/4 do conhecimento retido apos 1 ano** e pouco abaixo de 50% apos 2 anos.

**No MedHub:** a curva e gerida em **dois niveis**: o **card** (FSRS: stability/difficulty/retrievability) e o **tema** (`review_radar.py`: `dias + (1 - retrievability) * 30 + vencidos * 2`, limiar 21 dias). Nenhum dos dois usa a cifra de Ebbinghaus: o sistema **mede a propria curva** (retencao por lote, reincidencia de card, F100).

**Estado: CONFIRMA.** Duas notas: o limiar de 21 dias e heuristico (s083), nao derivado -- calibra-lo com a retrievability medida e candidato, nao divida; e o "salto" apos uma noite de sono (Murre & Dros) e um argumento mecanicista para o primeiro intervalo nunca ser no mesmo dia -- o que o FSRS sem `learning_steps` ja faz (P17).

### P3 -- Espacamento e "estudar para o eu futuro" (Cepeda et al. 2006; Brown, Roediger & McDaniel 2014)

Sessoes espacadas vencem sessoes massificadas mesmo quando parecem mais lentas; o intervalo otimo e uma faixa larga, nao um ponto. O video 1: cards de bioquimica continuam durante imunologia porque o Step 1 e daqui a um ano.

**No MedHub:** o FSRS **nunca suspende** o card do bloco encerrado -- a fila e transversal ao cronograma por construcao. O **balanceador de carga** (`app/utils/fsrs_balance.py`, +-5% do intervalo) existe *porque* a curva e ~plana perto do otimo -- e a folga que a literatura descreve, usada para achatar o calendario. O plano hibrido (Fase 2 = extensivo S21-S48 ate o ENAMED 2027) e o "eu futuro" com horizonte de 12 meses.

**Estado: CONFIRMA.**

### P4 -- Efeito de teste / pratica de recuperacao (Roediger & Karpicke 2006; Larsen, Butler & Roediger 2008/2009; Dunlosky et al. 2013; Deng 2015)

Recuperar da memoria fortalece mais que reler: uma semana depois, 56% x 42%; na comparacao STTT x SSSS, **61% x 40% (d = 1,26)** -- e o grupo que so reestudou era o **mais confiante**. Na tabela de Dunlosky 2013, **practice testing e distributed practice sao as duas unicas tecnicas de utilidade ALTA**; releitura, sublinhar e resumir sao BAIXA. Em medicina, Deng, Gluckstein & Larsen 2015: questoes e flashcards Anki foram **preditores independentes** do Step 1 (+1 ponto a cada ~445 questoes ou ~1.700 cards); o deck comercial pronto (Firecracker) **nao predisse**. Ressalva dura: o unico estudo de Step 2 CK (raciocinio clinico) **nao achou beneficio do Anki** -- e o ENAMED se parece com o Step 2.

**No MedHub:** e a espinha inteira -- questoes primeiro (s126), card = sonda (`revisar.md`), **flip obrigatorio** (ver o verso mesmo no acerto: feedback pos-recuperacao amplifica o efeito), Autopsia por bloco, **questoes e cards em paralelo** (60 + 60/dia, s159 -- exatamente o que "preditores independentes" recomenda). E a razao pela qual a **revogacao do PREPARAR/Camada 0 (s170)** esta certa pela literatura, nao so pelo gosto do usuario: reler antes de sondar e baixa utilidade **e** contamina o sinal de recall a frio que o FSRS precisa (Invariante D, lapide).

**Estado: CONFIRMA, com um aviso de dose:** o card sustenta o **substrato factual**; a decisao clinica e sustentada por questoes intercaladas e pela Autopsia (P6, P13). Dobrar o teto de cards para uma prova de raciocinio clinico nao tem lastro -- o 60/60 esta bem calibrado.

### P5 -- Pre-teste e "errar antes de aprender" (Richland, Kornell & Kao 2009; Sinha & Kapur 2021)

Tentar responder antes da instrucao -- e errar -- melhora a aprendizagem posterior. Meta-analise de *productive failure* (166 comparacoes, >12.000 participantes): **d = 0,36** (IC 0,20-0,51), subindo a **0,58** quando o desenho e fiel. **Condicao inegociavel:** a instrucao vem DEPOIS e **usa os erros cometidos** (compara a solucao falha com a canonica); errar e depois receber a aula generica nao e productive failure.

**No MedHub:** e exatamente o **gatilho hibrido da s126** -- tema D5 ou menor = questoes primeiro, aula depois mirando o buraco que o erro expos (`AGENTE.md` secao 1.2). A ressalva da literatura ("base minima") e o outro ramo do mesmo gatilho: tema-zero ou D8+ recebe `/aula-base` antes. A condicao "instrucao usa os erros" e a **Revisao Direcionada ancorada nas notas 1-2** e a **Autopsia** (cadeia, elo quebrado, comporta, racional declarado). **Medido:** F100, 3a medicao (s181) -- os 4 fatos arbitrarios de Cirurgia Infantil fecharam 4/4 quando o mecanismo veio **junto da sonda no mesmo turno**, e falharam quando veio como prosa isolada.

**Estado: CONFIRMA.** A literatura valida "questao primeiro + fechamento ancorado nos erros" **melhor** do que valida "aula completa e depois questoes".

### P6 -- Intercalacao x bloqueio (Kornell & Bjork 2008; Rohrer & Taylor 2007; Hatala, Brooks & Norman 2003; Rozenshtein 2016)

Misturar categorias parecidas na pratica (intercalar) treina **discriminacao** melhor que praticar em blocos por categoria -- e os aprendizes sentem o contrario. Numeros: pintores 0,61 x 0,35 (d ~ 1,0) com **78% acertando mais no intercalado e 78% dizendo que o bloqueado foi igual ou melhor**; **ECG 46% x 30%** (pratica mista, educacao medica); radiografia de torax 57% x 43%. Birnbaum et al. 2013 atribuem o ganho a **discriminacao**, nao ao intervalo. **Quando bloquear:** ao extrair UMA regra de varios exemplos, quando as categorias ja se distinguem facilmente, ou no nivel zero de conhecimento (Dunlosky da utilidade MODERADA ao interleaving por isso). Leitura pratica: *primeira exposicao a tema virgem = bloco; a partir de duas entidades confundiveis, intercalar.*

**No MedHub:** a fila FSRS **ja intercala por default** -- `fsrs_queue._ordered_queue` achata os buckets `atrasados -> hoje -> novos` misturando temas; `--cluster` e **opt-in**. E a familia nº 1 de erro deste usuario e **discriminacao**: "o discriminador que EXCLUI" (padrao-mestre, s125), clusters de diagnostico diferencial (PLECT, s142; Wilms x neuroblastoma, s182: *"fiz tantos cards e perdi uma questao de graca"*).

🔴 **Estado: TENSAO documental (F109).** O ledger (F3, s108) e o PRD `engenharia-ledger-f1-f13` chamam a revisao em cluster de *"pedagogicamente superior"*. A premissa nao se sustenta: o cluster **parece** melhor pelo mesmo mecanismo que faz o cramming parecer melhor (P1). O comportamento vivo (default intercalado) esta certo; o que estava errado era a justificativa escrita -- e uma justificativa errada num portador e convite para alguem "corrigir" o default. **Decisao registrada (s184):** a ordem intercalada e **default deliberado**; `--cluster` fica para (a) onboarding de cluster frio/tema-zero (bloquear primeiro, intercalar depois) e (b) andaime. Lapide no F3; rider no `fsrs-management-contract.md` e em `revisar.md` sao itens da fila (planejamento, nao executados).

### P7 -- Dificuldades desejaveis e friccao virtuosa (Bjork 1994; Bastani et al. 2025; Eagleman, entrevista citada no video 2)

Certos atritos **sao** a aprendizagem: o esforco de recuperar, o desconforto de nao conseguir explicar. A evidencia quantificada mais forte do dossie e um experimento de campo com ~1.000 alunos (Bastani et al. 2025, PNAS): IA que **entrega a resposta pronta** sobe a pratica em **+48%** e derruba a prova sem IA em **-17%**; a versao com **guardrail socratico** (so dicas) sobe a pratica em +127% e **zera a queda**. O video 2 e a versao anedotica: com captura + resumo + organizacao 100% automaticos, o autor *"estava rapido demais para saber o que nao sabia"*, e reintroduziu **uma** friccao -- ler as notas do dia a procura do que nao consegue explicar.

**No MedHub:** o sistema protege varias friccoes virtuosas **por contrato** sem nunca te-las nomeado como tal: Invariante F (silencio no DRENAR), recall a frio (Clausula 11), relearning ate nota 4, *"perguntar o raciocinio antes de diagnosticar"* (secao 3.2, CONTRATO s182), racional declarado (s179), o ritual de execucao, a triagem humana dos cards (s172). E automatiza as viciosas: `--errors-file`, `--review-plan`, player, RAG, numeros derivados.

🔴 **Estado: LACUNA de portador (F110).** Nenhum documento dizia **quais** friccoes sao protegidas. Toda reforma de "reduzir atrito" (player, `--errors-file`, subagentes) foi julgada por custo, nunca por "o que de processamento do aluno sai junto". A secao 3 deste arquivo passa a ser o portador; o eixo e semantico e fica **declarado como nao-verificavel por gate** (`AGENTE.md` secao 10.8). Corolario de engenharia (varredura 3): quando o agente e **autor e avaliador** do mesmo artefato (escreve a aula e depois julga se ela ensinou), a literatura de *automation bias* (Parasuraman & Manzey 2010) preve complacencia -- o juiz do rendimento tem de ser o dado do aluno (drill, questao), nunca o proprio agente.

### P8 -- Autoexplicacao e interrogacao elaborativa (Chi et al. 1994; Bisra et al. 2018; Metcalfe 2017)

Explicar *por que* -- para si mesmo, antes de receber a explicacao -- produz mais aprendizagem: **g = 0,55** na meta-analise de Bisra et al. 2018 (64 estudos, ~6.000 participantes). E o erro cometido com **alta confianca** e o que mais se corrige quando confrontado (*hypercorrection*, Metcalfe 2017).

**No MedHub:** e o **modo de ensino** inteiro: escada de degraus amarrados, *"deduza, nao decore"*, altitude mecanismo > fato (`AGENTE.md` secao 1.2), o "porque" fora do recall no formato atomico, e do lado do aluno o **racional declarado** e a pergunta obrigatoria (secao 3.2). O teste de regenerabilidade (s172) e o corolario honesto: **mecanismo e discriminador sao para ENSINAR, nao para SONDAR** -- card cuja resposta se deduz do mecanismo mede a deducao, nao a memoria; o card e para o **fato arbitrario** (cutoff, prazo, dose, nome de achado). O hypercorrection e o argumento para o veredito `errou` com racional declarado ser o insumo **mais valioso** da Autopsia, acima do `incerteza`.

**Estado: CONFIRMA.** Dois modos, duas superficies: elaboracao na `/aula-base` e na Revisao Direcionada; recuperacao no card.

### P9 -- Principio da informacao minima e atomicidade (Wozniak, 20 rules; referencia EMED)

Um fato por card; frente gerativa; verso de uma frase. Cards inflados dao ilusao de competencia (acerta 3 de 5, marca "bom", perde 2).

**No MedHub:** `estilo-flashcard.md` secao Formato atomico (s124), `audit_card_atomicity.py`, ratchet de nao-crescimento do verso (BLOCK), `card_checks.py` nos writers. **Medido:** ~280 nao-atomicos herdados na worklist; 25 de 85 inversoes na triagem da s172. A varredura 2 confirma o porque da triagem humana: itens gerados por LLM chegam perto do item humano em dificuldade, mas com **distratores fracos** ("redator novato") -- o juiz pedagogico continua sendo o operador.

**Estado: CONFIRMA -- com o limite que a s182 expos.** Card atomico **nao transfere sozinho dentro de um cluster de diferencial** (Q52, 2a evidencia). As duas respostas ja existem e se somam: tabela comparativa lado a lado na aula de cluster (`feedback_aula_cluster_diferencial_tabela`) e **intercalacao** na fila (P6).

### P10 -- Reaprendizagem sucessiva ate criterio (Rawson & Dunlosky 2011; Rawson, Dunlosky & Sciartelli 2013)

Recall ate acertar **dentro** da sessao, repetido em sessoes espacadas: **+10 pontos** na prova do curso; **24 dias depois, >60% retido x <20%** de quem estudou sozinho; o custo por conceito cai de ~3 min para ~1 min na 3a sessao. Os autores sao explicitos: flashcards podem instanciar isso *ou nao* -- a diferenca e **criterio de parada + o item voltar na MESMA sessao**.

**No MedHub:** relearning intra-sessao ate nota 4 (`revisar.md`, passo obrigatorio desde a s161), **redrill automatico no player** (o que o usuario elogiou em 16/09: *"justamente por ja fazer o redrill automaticamente"*), corte do loop em 2 travadas -> reonboarding curto (s173). A 1a nota e a unica que grava no FSRS -- o redrill consolida, nao agenda.

**Estado: CONFIRMA.** E o mecanismo com a evidencia mais direta de todo o sistema.

### P11 -- Consistencia > intensidade; comportamento = motivacao x habilidade x gatilho (Fogg; Lally et al. 2010; Clear; Tracy)

"Consistencia vence intensidade" e **forte pela via da memoria** (pratica distribuida = utilidade ALTA, Dunlosky) e **fraca pela via do habito** (Fogg e modelo, nao achado; Lally 2010 = mediana de 66 dias numa **faixa de 18 a 254**, com o modelo ajustando em 39 de 96 pessoas). O unico dado tranquilizador e empirico: **perder um dia nao quebra a curva**.

**No MedHub:** e a decisao da s159 nas palavras do usuario -- *"de nada adianta fazer 500 questoes em 5 dias e depois passar 2-3 dias sem estudar"* -> 60q + 60 cards/dia; sprint de 120 **revogado** (s168); `CAP_MULTIPLICADOR` 1,5 e nao 2 para nao reinstalar pico-e-queda. **Gatilho:** o hook `SessionStart` injeta o Plano do Dia e o boot abre com "Proximo ato" (Boot v2). **Habilidade:** o player cortou 60 cards de uma tarde para 16,5 min. **Frog:** a ordem de abertura e **cards primeiro, questoes depois** (`ESTADO.md` Proximos passos, item 1).

**Estado: CONFIRMA.** Principio derivado que vale escrever: **a complexidade fica do lado do agente; o ritual do usuario tem tres gestos** (abrir o link, teclar 1-4, contar os erros). Toda reforma que adicione um gesto ao usuario paga esse custo em consistencia.

### P12 -- Aprendizagem multimidia (Mayer, CTML)

Numa aula em HTML com texto + tabelas + diagramas **sem audio** valem: multimidia (palavras + grafico), **coerencia** (cortar o extraneo -- o mais importante), **sinalizacao** (mostrar o esqueleto, nao colorir tudo), **contiguidade espacial** (legenda colada ao elemento; tabela logo abaixo do paragrafo que a interpreta), segmentacao (secoes ritmadas) e **pre-treino** (siglas e parametros antes do mecanismo). **Nao se aplicam** modalidade e contiguidade temporal. **Redundancia** se aplica reformulada: o mesmo fato dito duas vezes (prosa + tabela + box) e carga extranea. Ressalva: **reversao por expertise** -- sinalizacao, pre-treino e redundancia invertem de sinal em aprendiz avancado; aula de tema virgem e aula de revisao **nao devem seguir o mesmo design**.

**No MedHub:** `/aula-base` como Artifact HTML com design real (s149) e o canal visual; **"cada fato dito uma vez so"** (Clausula de forma, s170; `feedback_aula_base_prosa_enxuta`) e a coerencia/redundancia; os marcadores 🔴/⭐/⚠️ sao a sinalizacao; a **tabela lado a lado** para cluster de diferencial e a contiguidade espacial; o **onboarding de siglas** (D10) e o pre-treino; a **calibracao por nota 1-10** (D10/D8/D5/D2) e exatamente a resposta ao efeito de reversao por expertise.

**Estado: CONFIRMA.** O PREPARAR revogado (*"denso e confuso"*) violava coerencia -- a literatura preve o resultado.

### P13 -- Prova como habilidade e a troca de alternativa (Larsen; Kruger, Wirtz & Miller 2005; Benjamin, Cavell & Shallenberger 1984; Sherbino et al. 2014)

Saber e performar sob condicao de prova sao habilidades distintas. Sobre trocar de alternativa, a literatura e mais forte sobre a **media** do que sobre a condicao: **51% das trocas vao de errada para certa e 25% de certa para errada** (n = 3.291 trocas); 54% dos que trocam sao ajudados e 19% prejudicados; nenhum dos 33 estudos da revisao de 1984 achou prejuizo. A crenca "fique com o primeiro instinto" e majoritaria e **se fortalece com a experiencia** (78% entre veteranos x 65% entre calouros). "So troque com motivo nomeado" e uma **sintese defensavel** (troca guiada por informacao nova ajuda; palpite nao), nao a conclusao literal dos papers. Sobre vies cognitivo em diagnostico: fechamento prematuro e o erro cognitivo isolado mais comum (Graber 2005), mas o unico RCT que ensinou "cognitive forcing strategies" a estudantes deu **resultado nulo** (Sherbino 2014) -- nomear o vies nao basta; o que muda comportamento e **pratica com feedback sobre o raciocinio**.

**No MedHub:** `docs/PLAYBOOK_EXECUCAO_PROVA.md` (familia do bug nº 1, comportas por tema, tripe da s131), slot de simulado a cada 4 semanas, e o **override do modal** medido na s180 (13/13 erradas do S9 na alternativa nao-modal; custo 4-5 questoes) com a **regra dos dois finalistas**: so trocar se conseguir **nomear o erro** da favorita.

**Estado: CONFIRMA, com duas calibracoes.** (1) A regra dos dois finalistas **nao pode ser lida como "fique com o primeiro instinto"** -- isso custa pontos na media; ela proibe a troca **sem motivo nomeado**, que e o padrao medido deste usuario ("facil demais", 13/13). A literatura descreve populacoes; o padrao dele foi medido individualmente e vence. (2) O playbook e uma lista de vieses nomeados, e Sherbino mostra que a lista sozinha nao muda desempenho: o que treina e o **ritual rodado em toda questao com feedback na Autopsia** -- e por isso a medida do proximo simulado (override do modal cai?) e o teste, nao a leitura do playbook.

### P14 -- Um documento vivo por tema (video 2: "one running document per topic")

Conhecimento acumula num unico lugar por assunto, que fica mais rico com o tempo e e pesquisavel -- nunca uma nota nova por ocasiao. A varredura 3 confirma o padrao pelo lado da engenharia (ADR de Nygard 2011; *living documentation*) e nota que **nenhuma arquitetura de memoria de agente pesquisada** (MemGPT, Generative Agents, A-MEM, Mem0) trata memoria **procedimental** como eixo proprio -- os contratos e skills do MedHub estao a frente disso.

**No MedHub:** `resumos/{Area}/{Tema}.md` + **Regra de Acumulo** (armadilhas cumulativas, nunca sobrescrever) + **Siamese Twins** (erro -> `ipub.db`; licao -> resumo) + a regra critica de `analisar-questao.md` secao 4 (inserir como bullet integrado, nunca "a Q2 abordou...") + RAG gold-only sobre os `.md`.

**Estado: CONFIRMA** -- existe desde a fundacao do repo. O F103/F106 (`[SEM-LASTRO]` falso por nome) e o lembrete de que "um documento por tema" exige um **mapa tema -> documento**, nao igualdade de nome.

### P15 -- Captura sem friccao viciosa (video 2: Granola -> Claude -> Docs; Whisper)

Tudo que e digitacao, formatacao e arquivamento sai do humano; o momento de aprendizagem e capturado sem parar para escrever. A afirmacao do video 2 de que "escrever divide a atencao" (Mueller & Oppenheimer 2014) **nao sobreviveu a replicacao** (Morehead 2019; Urry 2021, nulas): o que importa nao e como se registra, e se depois se recupera.

**No MedHub:** e o **pivot agent-first** (s074: agente = cerebro, codigo = FSRS) levado ao registro -- `insert_questao --errors-file`, Autopsia gerada, `--handoff-block`, player construido e publicado pelo agente, subagentes para varredura. O usuario **declara** (racional, notas, contagens); o agente **persiste**.

**Estado: CONFIRMA, com a ressalva do P7:** o video 2 e o alerta de que este e o eixo onde o sistema pode passar do ponto. O ledger da secao 3 e a guarda.

### P16 -- Revisao diaria de baixo risco para achar o que nao se explica (video 2, a friccao reintroduzida)

Ler o que o dia capturou **com o objetivo de encontrar lacunas** -- nao para reorganizar -- e, achando algo que nao se consegue explicar, ir atras e anotar a mao.

**No MedHub:** a **Autopsia diaria** e lida pelo usuario e ja exige dele o **racional declarado** por erro (o veredito do elo fica `pendente` sem ele); a **Revisao Direcionada** de fechamento e ancorada nas notas 1-2 que o proprio drill produziu (*"ensinar depois mira dado, ensinar antes mira palpite"*).

**Estado: CONFIRMA (parcial).** A busca de lacuna e dirigida pelo dado (nota 1-2, erro), nao por uma releitura livre do usuario. Nao se propoe ritual novo: adicionar um gesto ao dia cobra o custo do P11.

### P17 -- O que a nota significa para o agendador (py-fsrs 6.3.2; tutorial oficial do FSRS)

No FSRS, **Again (1) e a unica nota de lapso**; Hard (2), Good (3) e Easy (4) sao **acertos** com crescimento de estabilidade decrescente. O tutorial oficial e explicito: "Hard" e *recuperou com esforco*, **nunca** "errei parcialmente" -- usar Hard para erro parcial infla o intervalo. "Easy" e *sem esforco algum*; o acerto normal e Good.

**No MedHub:** `revisar.md` passo 4 define **2 = "recall parcial/na zona mas sem o alvo"** (um nao-acerto por conteudo) e **4 = "cravou conceito + regra-mestre"** (o acerto normal), e `app/utils/fsrs.py` passa a nota direto (`Rating(rating)`; lapse so em 1). **Medido em 17/09/2026 (read-only, `fsrs_revlog` com `state=2`, 2.981 revisoes):** nota 1 -> intervalo medio **1,0 dia**; nota 2 -> **14,2 dias** (312 revisoes); nota 3 -> 16,7 dias (525); nota 4 -> **34,3 dias** (1.551 revisoes = **52% de todas**). Ou seja: o card que o aluno **nao lembrou de verdade** volta em duas semanas, quase como um acerto; e o acerto normal recebe o bonus de "facil".

🔴 **Estado: TENSAO (F112).** A regua do agente esta deslocada um degrau para cima em relacao a semantica do algoritmo. E uma causa plausivel do padrao "consolidado a 85%, erros frescos a 25%" (s169) e das reincidencias de fato arbitrario (F100): a nota 2 agenda longe demais. Remedios possiveis (fila, decisao do operador): remapear 2 -> Again no adaptador; ou redefinir a regua (3 = certo padrao; 4 so sem esforco; 2 so "lembrei com esforco"); e, em qualquer caso, **rodar o `Optimizer` do py-fsrs sobre o revlog proprio** (2.981 revisoes >= minimo oficial de 400-1.000), que absorve parte do deslocamento ao ajustar os parametros ao comportamento real de nota. Nao executado nesta sessao.

---

## 3. Ledger de friccoes -- o que e protegido e o que se automatiza

> **Regra de decisao para qualquer reforma futura:** antes de remover uma friccao, perguntar *"o que de PROCESSAMENTO do aluno sai junto?"* Se a resposta e **uma tentativa de recuperacao, uma autoexplicacao ou uma autoavaliacao**, a friccao e **virtuosa** e fica. Se e **digitacao, contagem, busca, formatacao ou espera**, e **viciosa** e sai. Eixo semantico: **nao ha gate** que o verifique; a guarda e esta lista, lida antes de escrever spec (F110). Evidencia-mae: Bastani et al. 2025 (P7).

### 3.1 Friccoes VIRTUOSAS -- protegidas; nunca automatizar, nunca "otimizar" para fora

| # | Friccao | Portador que a protege |
|---|---|---|
| V1 | **Tentar lembrar ANTES de ver o verso** (chat: "nao revelar o verso ainda"; player: `Espaco` vira so depois da tentativa) | `revisar.md` passos 2-3; Clausula 12 |
| V2 | **Recall a frio** -- nenhum aquecimento antes do drill | `revisao-calibrada-contract.md` Clausula 11; lapide do Invariante D ("nao re-derivar") |
| V3 | **Nota honesta 1-4**, proposta pelo agente a partir da resposta e sobreponivel pelo usuario; honestidade > generosidade (semantica a corrigir: P17/F112) | Invariante C; `revisar.md` passo 4 |
| V4 | **Relearning ate 4 na propria sessao**; travou 2x -> reonboarding curto, nao repeticao | `revisar.md` secao Relearning (s161, s173); player |
| V5 | **Racional declarado pelo usuario antes do diagnostico do agente**; sem ele, o veredito do elo fica `pendente` | `analisar-questao.md` secoes 3.2 e 3.3 (CONTRATO s182/s183) |
| V6 | **Ritual de execucao em prova** rodado pelo proprio aluno (comporta, "qual dado EXCLUI", checksum de F, dois finalistas) | `docs/PLAYBOOK_EXECUCAO_PROVA.md` |
| V7 | **Triagem humana dos cards** pelo teste de regenerabilidade -- o harness verifica forma e e cego a rendimento | `estilo-flashcard.md` secao Triagem (s172) |
| V8 | **Ler o verso mesmo no acerto** (flip obrigatorio) | `revisar.md`, feedback s077 |
| V9 | **Questoes antes da aula** em tema D5 ou menor (errar antes de aprender) | `AGENTE.md` secao 1.2, gatilho hibrido (s126) |
| V10 | **Ensino so no fechamento, sobre gap provado pelo drill** -- nunca sobre previsao | Clausula 11, razao 3; Invariante F |
| V11 | **Ler a Autopsia** e responder a pergunta de raciocinio que ela deixou registrada | `analisar-questao.md` secao 3.3 |

### 3.2 Friccoes VICIOSAS -- automatizadas ou a automatizar

| # | Friccao | Mecanismo que a remove |
|---|---|---|
| X1 | Digitar erros e cards no banco, um a um | `insert_questao.py --errors-file`; `--dry-run` de lote (F107, candidato) |
| X2 | Montar a fila, agrupar, contar blocos a mao (errou 3x na s108) | `fsrs_queue.py`, `day_plan.py --review-plan` |
| X3 | Virar card e gravar nota turno a turno no chat | player de cards (60 em 16,5 min) + `--record-lote` |
| X4 | Achar o trecho certo do resumo | RAG `app.engine.get_topic_context` |
| X5 | Escrever e atualizar resumo e Autopsia | agente (Siamese Twins); o usuario le e declara |
| X6 | Digitar numeros de estado (volume, FSRS, backlog) | `day_plan.py --handoff-block` -- nunca a mao (F6) |
| X7 | Verificar diretriz/fonte; varrer web aberta | `/pesquisar-evidencia` + `evidence-researcher`; web aberta em **subagente isolado** (s184) |
| X8 | Servir um card por id, fora da fila | `fsrs_queue.py --card` (F99, candidato) |

---

## 4. Lacunas e tensoes achadas (destino no ledger; nada executado na s184 -- sessao de planejamento)

- **F109 -- premissa "cluster e pedagogicamente superior" x intercalacao.** Comportamento vivo certo (default intercalado), justificativa escrita errada (F3, PRD). Lapide registrada no F3; riders no contrato FSRS e em `revisar.md` sao itens da fila.
- **F110 -- friccoes virtuosas sem portador.** Secao 3 deste arquivo passa a ser o portador; eixo declarado nao-verificavel por gate. Item da fila: clausula-ponteiro no `revisao-calibrada-contract` e checklist de "qual friccao esta spec remove?" no template de spec.
- **F111 -- Fase 2 (extensivo, leitura-first) nao garante recall no dia da primeira exposicao. Decisao do operador.** O extensivo tem **465 tarefas de teoria em 735** e ritmo nativo de 39q/dia; uma tarefa T fechada sem bloco de questoes gera **zero sonda** (cards nascem de erro ou de andaime; o R1 mini-drill so ve erros frescos de 48h). Proposta compativel com "nunca bulk import": **intake por tarefa concluida** -- ao fechar uma tarefa T (`plano.py --concluir`), triar o deck EMED do tema (`emed_flashcards.py --query`) pelo teste de regenerabilidade e introduzir **so os sobreviventes** (fato arbitrario) no mesmo dia, dentro do teto. Deng 2015 (cards proprios predizem, deck pronto nao) e o teto de utilidade do Anki no Step 2 CK sao os dois limites do intake: filtrado e pequeno. Prazo natural: antes de 02/11/2026.
- **F112 -- semantica das notas 1-4 deslocada em relacao ao FSRS (P17).** Medido: nota 2 agenda em 14 dias; nota 4 e 52% das revisoes. Fila: `Optimizer` sobre o revlog (read-only, parametros em dado versionado) -> decisao do operador sobre a regua -> eventual remapeamento no adaptador (toca `record_review`, o caminho unico de escrita: **spec**, nunca hotfix).
- **Calibracoes registradas sem reforma:** (a) regra dos dois finalistas nao e "primeiro instinto" (P13); (b) nomear vies nao muda desempenho -- o ritual com feedback muda (P13, Sherbino); (c) aula de tema virgem e de revisao pedem designs diferentes (P12, reversao por expertise); (d) leech nao e recurso do FSRS, e do app -- o MedHub precisa do proprio limiar de lapsos cruzado com Difficulty (varredura 4).

---

## 5. O que NAO adotar dos videos, e por que (afirmacoes superestimadas, com a fonte que as derruba)

- **Deck pre-pronto com "unsuspend" em massa por topico (AnKing).** Rejeitado pela politica "nunca bulk import", pelo teste de regenerabilidade, pela divida observada (pool de 685 cards nunca introduzidos em 16/09/2026) **e por Deng 2015** (deck comercial pronto nao predisse a nota; cards proprios predisseram). O que se aproveita e a **cadencia** (card do tema no dia da exposicao), como intake filtrado -- F111.
- **"70% esquecido em 24h" como numero de projeto.** Erro de categoria (savings != % lembrado), silabas sem sentido, n = 1; em medicina sao 65-75% **retidos** em 1 ano (Custers 2010).
- **"Escrever a mao vence digitar / anotar divide a atencao".** Duas replicacoes diretas deram nulo (Morehead 2019; Urry 2021).
- **"66 dias para formar um habito".** Mediana de uma faixa de 18 a 254 dias, modelo ajustado em 39 de 96 (Lally 2010). O que vale e a pratica distribuida, nao o mito do habito.
- **"FSRS e comprovadamente superior ao SM-2 para aprender".** O benchmark (9.999 colecoes, ~350M revisoes; FSRS-6 melhor em 99,6% delas) mede **calibracao de previsao** (log loss), nao aprendizado; nao ha RCT com desfecho de prova; os proprios autores dizem que a comparacao com o SM-2 nao e justa. "20-30% menos revisoes" vem de simulacao.
- **"Anki aumenta sua nota".** Tudo observacional; beneficio no Step 1 (fundacional) e **ausente** no unico estudo de Step 2 CK (raciocinio clinico).
- **"Interleaving sempre vence".** Utilidade MODERADA em Dunlosky; o proprio Kornell & Bjork construiu o caso em que o bloqueio vence (extrair uma regra unica).
- **"Aula multimidia bem desenhada produz retencao".** Validada em transferencia imediata com novatos; varios principios invertem em avancados.
- **Ferramentas do video 2 (Granola, Whisper, Notion, Genie).** A captura aqui e o agente + CLIs; o "resumo diario por e-mail" e a Autopsia + HANDOFF. Trocar de ferramenta nao e o ganho; a lente de friccao e.
- **Renomear as fases para Learn/Retain/Apply.** O vocabulario vivo e DRENAR / Revisao Direcionada / `/aula-base`; a s170 ja pagou o preco de quatro nomes para duas coisas. Este documento mapeia, nao renomeia.
- **Reintroduzir aquecimento pre-drill por causa do "3 exposicoes".** A terceira exposicao do video e uma **revisao** (recall), nao uma releitura -- e o FSRS ja a agenda. Invariante D e Clausula 11 seguem em vigor.

---

## 6. Fontes verificadas (varredura s184; forca de evidencia entre colchetes)

Relatorios crus, com URL/DOI por item e as ressalvas integrais: `docs/research/2026-09-17-01-ciencia-aprendizagem.md` (Opus, 31 buscas, 22 min), `-02-agentes-ia-offloading.md` (Sonnet, 25 buscas, 23 min), `-03-engenharia-agentes-estudo.md` (Sonnet, 34 buscas, 25 min), `-04-open-spaced-repetition.md` (Sonnet, 30 buscas, 18 min). Itens marcados NAO VERIFICADO nos relatorios nao entram aqui.

**A. Memoria e pratica**
- Kornell 2009, *Applied Cognitive Psychology* 23:1297, DOI 10.1002/acp.1537 -- espacamento x cramming em flashcards (90% / 72%). [estudo controlado]
- Kornell & Bjork 2008, *Psychological Science* 19:585, DOI 10.1111/j.1467-9280.2008.02127.x -- intercalacao induz discriminacao; 0,61 x 0,35; ilusao 78%/78%. [estudo controlado]
- Rohrer & Taylor 2007, *Instructional Science* 35:481, DOI 10.1007/s11251-007-9015-8 -- intercalacao em matematica. [estudo controlado]
- Hatala, Brooks & Norman 2003, *Adv Health Sci Educ* 8:17, PMID 12652166 -- ECG por pratica mista, 46% x 30%. [estudo controlado, educacao medica]
- Rozenshtein et al. 2016, PMID 27236286 -- radiografia de torax, 57,1% x 43,1%. [estudo controlado]
- Birnbaum, Kornell, Bjork & Bjork 2013, *Memory & Cognition* 41:392, DOI 10.3758/s13421-012-0272-7 -- o ganho da intercalacao e discriminacao. [estudo controlado]
- Murre & Dros 2015, *PLoS ONE* 10:e0120644, DOI 10.1371/journal.pone.0120644 -- replicacao de Ebbinghaus. [replicacao]
- Custers 2010, *Adv Health Sci Educ* 15:109, PMID 18274876 -- 2/3 a 3/4 retidos apos 1 ano em medicina. [revisao]
- Roediger & Karpicke 2006, *Psychological Science* 17:249, PMID 16507066 -- efeito de teste (61% x 40%, d = 1,26). [estudo controlado]
- Larsen, Butler & Roediger 2008 (*Med Educ* 42:959, PMID 18823514) e 2009 (PMID 19930508) -- teste em residentes/estudantes. [revisao + RCT]
- Karpicke & Blunt 2011, *Science*, DOI 10.1126/science.1199327 -- recuperacao > mapa conceitual. [estudo controlado; numeros nao extraidos]
- Dunlosky et al. 2013, *Psychological Science in the Public Interest* 14:4, PMID 26173288 -- tabela de utilidade das 10 tecnicas. [revisao sistematica]
- Bjork 1994 (dificuldades desejaveis) e Bjork & Bjork 1992 (nova teoria do desuso). [teoria]
- Richland, Kornell & Kao 2009, *JEP: Applied* 15:243, PMID 19751074; Kornell, Hays & Bjork 2009, DOI 10.1037/a0015729 -- pre-teste. [estudo controlado]
- Sinha & Kapur 2021, *Review of Educational Research* 91:761, DOI 10.3102/00346543211019105 -- productive failure, d = 0,36 (0,58 com fidelidade). [meta-analise]
- Rawson & Dunlosky 2011 (DOI 10.1037/a0023956); Rawson, Dunlosky & Sciartelli 2013 (DOI 10.1007/s10648-013-9240-4); Janes et al. 2020 (DOI 10.1002/acp.3699) -- successive relearning. [estudo controlado em sala real]
- Chi et al. 1994 (autoexplicacao); Bisra et al. 2018, *Educational Psychology Review*, g = 0,55. [meta-analise]
- Metcalfe 2017, *Annual Review of Psychology* -- aprender com erros; hypercorrection. [revisao]
- Mayer, *Multimedia Learning* (3a ed. 2020, DOI 10.1017/9781316941355) -- principios da CTML. [teoria + meta-analises por principio]
- Lally et al. 2010, *Eur J Soc Psychol* 40:998, DOI 10.1002/ejsp.674 -- 66 dias (18-254). [observacional]
- Fogg 2009, DOI 10.1145/1541948.1541999 (B = MAP). [modelo]
- Kruger, Wirtz & Miller 2005, *JPSP* 88:725, PMID 15898871; Benjamin, Cavell & Shallenberger 1984, DOI 10.1177/009862838401100303 -- troca de resposta. [estudo de campo + revisao de 33 estudos]
- Mueller & Oppenheimer 2014 (DOI 10.1177/0956797614524581) x Morehead et al. 2019 (DOI 10.1007/s10648-019-09468-2) e Urry et al. 2021 (DOI 10.1177/0956797620965541) -- anotar a mao: replicacoes nulas. [replicacao direta]
- Deng, Gluckstein & Larsen 2015, *Perspect Med Educ* 4:308, PMID 26498443 -- questoes e cards como preditores independentes do Step 1; Firecracker nao. [observacional]

**B. Agentes de IA, offloading e vies**
- Bastani et al. 2025, *PNAS* 122:e2422633122, DOI 10.1073/pnas.2422633122 -- IA sem guardrail: +48% / -17%; com guardrail socratico: +127% / 0. [experimento de campo, N ~ 1.000]
- Gerlich 2025, *Societies* 15:6, DOI 10.3390/soc15010006 (survey N = 666); Lee et al. 2025, CHI (survey N = 319); Kosmyna et al. 2025, arXiv:2506.08872 (EEG, N = 54/18, **preprint contestado**) -- offloading cognitivo. [correlacional / preprint]
- Tutor CoPilot (Stanford, RCT ~1.000 alunos): +4 pp de dominio, +9 pp com tutores fracos. [RCT]
- Graber, Franklin & Gordon 2005, *Arch Intern Med* -- fechamento prematuro e o erro cognitivo mais comum. [serie de casos] Croskerry 2003, *Acad Med* -- cognitive forcing strategies. [opiniao] Sherbino et al. 2014, *CJEM* (N = 191) -- ensinar forcing strategies **nao** reduziu erro. [RCT, negativo]
- Settles & Meeder 2016 (HLR, Duolingo); Piech et al. 2015 (DKT); BKT -- nenhum modela esquecimento no nivel do tema. [papers primarios]

**C. Ecossistema FSRS (open-spaced-repetition)**
- Ye, Su & Cao 2022, KDD, DOI 10.1145/3534678.3539081 (SSP-MMC); Su et al. 2023, *TKDE*, DOI 10.1109/TKDE.2023.3251721 (modelo DSR). [papers]
- srs-benchmark (github.com/open-spaced-repetition/srs-benchmark): FSRS-6 log loss 0,384, AUC 0,683, superior ao SM-2 em 99,6% das ~10k colecoes. [benchmark observacional, nao revisado]
- `fsrs` 6.3.2 no PyPI = FSRS-6 (21 parametros, decay individual w20); `Optimizer(review_logs).compute_optimal_parameters()`; minimo oficial 400-1.000 revisoes; `learning_steps=()` gradua direto para Review; Again = unico lapso; "Hard" nunca para erro parcial. [README/tutorial oficiais]
- Leech: recurso do Anki (8 lapsos -> suspender), nao do FSRS. [forum oficial]

**D. Engenharia de agentes**
- Park et al. 2023 (Generative Agents, arXiv:2304.03442, UIST); Packer et al. 2023 (MemGPT, arXiv:2310.08560); A-MEM 2025 (arXiv:2502.12110, NeurIPS); Mem0 2025 (arXiv:2504.19413) -- memoria em camadas; **falta gatilho algoritmico de consolidacao** no MedHub (reflection por importancia). [papers]
- Anthropic, "Effective context engineering for AI agents" (set/2025), "Building effective agents" (dez/2024), "How we built our multi-agent research system" (jun/2025); Cognition, "Don't build multi-agents" (jun/2025) -- fan-out so para leitura; escrita single-threaded. [blogs oficiais] Confirma "eu orquestro, subagentes varrem".
- Nygard 2011 (ADR); Martraire 2019 (*Living Documentation*) -- contratos versionados + gates; **nao existe ferramenta de industria** para prosa-x-banco: o COUNT-ASSERT e nomenclatura local. [padrao de facto]
- Kravitz & Duan 2014 (AHRQ, ensaios N-of-1); Bloom 1984 "2 sigma" **contestado** (reanalises 2023-24: g ~ 0,70). [relatorio tecnico / reanalises]
- Parasuraman & Manzey 2010, *Human Factors* 52(3) (automation bias); Bainbridge 1983 (ironies of automation) -- o conflito **agente autor = agente avaliador** nao e coberto pela literatura classica. [papers]
- Simon Willison 2025 ("lethal trifecta"); OWASP Top 10 for LLM Applications 2025 (prompt injection = #1) -- base da regra de web aberta em subagente isolado. [fonte primaria / documento oficial]

**E. Como medir antes de mudar contrato (metodo, nao fonte).** O MedHub e um n = 1: intervencao pedagogica nova (ex.: regua de notas, intake da Fase 2) pede desenho **N-of-1 com crossover** -- dois blocos de temas de dificuldade equivalente, uma intervencao em cada, *washout* de uma semana, desfecho = retencao no drill + acerto em questoes novas do tema (a medida de "exemplares novos" que a literatura de intercalacao usa). Sem isso, "a aula X melhorou a retencao Y" e correlacao.
