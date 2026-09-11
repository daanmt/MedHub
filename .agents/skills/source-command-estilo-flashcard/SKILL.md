---
name: "source-command-estilo-flashcard"
description: "Contrato de autoria de flashcards do MedHub — os 6 princípios para cunhar cards ancorados no erro metacognitivo, mais o teste de regenerabilidade que tria os candidatos antes de persistir. Consultar antes de gerar, triar ou regenerar qualquer card."
---

<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI.
     Edite `.claude/commands/estilo-flashcard.md` e rode `python tools/sync_skills.py`.
     Qualquer edicao feita neste arquivo e SOBRESCRITA no proximo sync. -->

# source-command-estilo-flashcard

Use this skill when the user asks to run the migrated source command `estilo-flashcard`.

## Command Template

# Skill: Estilo Flashcard

> Consultar este arquivo SEMPRE antes de cunhar ou regenerar um flashcard.
> É a régua de qualidade dos cards, assim como `estilo-resumo.md` é a dos resumos.
> A análise do erro (habilidades sequenciais, elo quebrado) vive em `analisar-questao.md`; aqui está **como o card é escrito**.

---

## Princípio central

O flashcard do MedHub não enuncia um fato genérico sobre um tema — ele **reforça o conteúdo exato onde o raciocínio rompeu** quando o usuário errou a questão. O substrato vem de `questoes_erros` (`tipo_erro`, `o_que_faltou`, `habilidades_sequenciais`, `alternativa_marcada` vs `alternativa_correta`, `armadilha_prova`) cruzado com o resumo correspondente (via RAG local). O card é a costura entre o ponto de ruptura e a rede de conhecimento.

---

## Os 6 princípios

1. **Conteúdo clínico atômico.** Um conceito por card. Decompor em vez de combinar: se o erro toca duas listas (ex.: agentes de úlcera *e* de corrimento), são **dois cards**, não um. O card é **recall de conteúdo**, nunca um card sobre "o hábito de raciocínio".
2. **O erro define o alvo.** `tipo_erro` + `o_que_faltou` apontam *qual* conteúdo drilar e *qual distinção/sobreposição* tornar central. O card é específico ao erro do aluno — não uma varredura genérica do tema.
3. **Pergunta direta, sem vazar a resposta.** A `frente_pergunta` é uma pergunta clínica real terminando em "?". **Nunca** colar o `habilidades_sequenciais` cru, **nunca** embutir a resposta no contexto, **nunca** usar template tipo "Qual o distrator típico em...?".
4. **Regra-mestre = a distinção/sobreposição** que previne a confusão. É o princípio transferível que costura este erro a outros (ex.: *Chlamydia* L1-L3 = úlcera vs D-K = corrimento).
5. **Armadilha = o distrator específico** que pegou o usuário, ancorado no resumo (que carrega o alerta de incidência em prova). Não um distrator hipotético — o que de fato induziu o erro.


6. **A questão errada é uma porta, não um alvo pontual (s171).** Formulação do usuário: *"mais do que treinar a distinção entre o marcado e o gabarito, a questão incorreta é uma oportunidade de revisar os nós que conectam o tema às alternativas e ao raciocínio mais complexo, conectando com outros temas próximos / nucleares."* **As alternativas erradas não são descarte — são nós.** Um distrator plausível carrega conteúdo que merece card próprio mesmo quando o usuário não o marcou: na Q77 da s171, as quatro alternativas erradas eram todas causas de **oligo**âmnio, cada uma por um mecanismo distinto — um mapa inteiro que se perderia se o conjunto parasse em "12 cm é poli". Ler o item inteiro rende 3-5 cards; ler só o par marcado↔gabarito rende 1.
   - **Não anula o princípio 2, amplia-o.** O erro continua definindo o **núcleo** e o primeiro card; o que muda é que o conjunto não para nele. A varredura proibida no princípio 2 é a genérica *sobre o tema*; esta é ancorada **nas alternativas que a banca de fato escreveu** — que são, por construção, o recorte que a prova considera discriminante.
   - **Mais cards, nunca cards maiores.** Ampliar o escopo não afrouxa a atomicidade: cada nó novo é um card novo com **um** critério de acerto, nunca um verso mais gordo. Ampliação que engorda o verso é a via direta para o passivo de não-atômicos (e para o ratchet do `d2026a1` recusar a escrita).
   - **Conectar a tema vizinho/nuclear é legítimo quando a ligação é estruturante** — é o que transforma conhecimento em rede em vez de lista, e é o mesmo princípio dos cards de altura graduada (`project_cards_altura_graduada`): o andaime a montante vale card quando o cluster inteiro depende dele.
   - 🔴 **LIMITE (s172, primeiro teste em produção).** O 6o princípio foi aplicado ao Simulado 8 e o operador reverteu **25 dos 85** vereditos de triagem. Formulação dele: *"ampliou os pontos de conteúdo passíveis de expansão, mas cunhou bastante ruído -- o que eu justamente temia. nesse sentido, os cards realmente precisam de juízes de qualidade até mesmo pedagógica."* O princípio **fica** -- a ampliação é real e ele a confirma. O que ele ganha é o filtro do §Triagem abaixo. Sem esse filtro, ler o item inteiro produz volume, não rendimento.

---

## Triagem -- o teste de regenerabilidade (s172)

Cunhar sob o 6o princípio e **triar** são atos separados. A cunhagem varre as alternativas; a triagem decide quais nós viram card. Sem a triagem o 6o princípio entrega ruído -- medido: 85 candidatos para 17 erros, dos quais o operador manteve 44.

**O teste, aplicado card a card antes de persistir:**

> O aluno consegue **regenerar** esta resposta a partir do card-núcleo do erro mais o mecanismo geral que ele já tem?
>
> - **Sim -> não é card.** O conteúdo pertence ao `verso_regra_mestre` do card-núcleo, ou a lugar nenhum. Card cuja resposta se deduz mede a dedução, não a memória -- e a nota FSRS que ele produz não informa nada.
> - **Não -> é card.** Fato arbitrário: um número, uma janela de tempo, um nome próprio de achado, uma contagem de doses, um esquema posológico. Nada disso se deduz; ou está na memória ou não está.

**O que as 25 inversões mostraram:**

| ele RESGATOU (eu havia cortado) | ele CORTOU (eu havia mantido) |
|---|---|
| 12 cards, **8 deles `conteudo`** -- fato duro | 13 cards, **5 `discriminador` + 2 `mecanismo` + 2 `nuance`** |
| "janela de 48-72 h para a excisão"; "resolve em 7 a 10 dias"; "SIRI em 4 a 8 semanas"; "bilirrubina > 0,2 mg/dl por hora"; "diabetes materno = 25% dos polidrâmnios"; "grão de café"; "doxiciclina 100 mg 12/12 h por 7 dias"; "falta o reforço da febre amarela" | "por que insuficiência uteroplacentária, RCF e pós-datismo cursam com oligoâmnio"; "fistulização aponta TB e não linfoma"; "PPD 0 é anergia"; "clearance não levanta o veto ao DOAC"; "hidropisia imune ou não imune" |
| **Nenhum se deduz.** | **Todos se deduzem** do card-núcleo mais o mecanismo -- ou são o próprio raciocínio da questão reescrito como pergunta. |

⚰️ **O caso que derruba a intuição.** *"Por que insuficiência uteroplacentária, restrição de crescimento fetal e pós-datismo cursam com oligoâmnio?"* foi celebrado na s171 como o melhor achado do 6o princípio -- um card que resolve três alternativas pelo mesmo mecanismo. O operador cortou. **Resolver três alternativas de uma vez é exatamente o sintoma:** se um mecanismo único explica as três, o aluno reconstrói as três a partir dele e o card não acrescenta recall. Economia de cards não é rendimento de cards.

**Corolário que inverte a heurística de triagem.** O instinto metacognitivo puxa para o `discriminador` e o `mecanismo` -- parecem mais nobres que o fato solto. Contra este usuário o rendimento é o oposto: `conteudo` (cutoff, prazo, dose, prevalência, nome de achado, contagem de calendário) rende mais que `discriminador` derivado da mesma questão. Metade disso já estava em `feedback_epidemiologia_dados_cristalizar` ("dado numérico solto não tem âncora de raciocínio para este usuário; vira card dedicado sempre") -- a s172 generaliza de epidemiologia para **todo fato arbitrário**. O que **não** muda: o card-núcleo (`elo_quebrado`) é intocável -- os 12 núcleos das 85 triagens sobreviveram sem uma única inversão.

🔴 **O juiz que falta é pedagógico, não estrutural.** Os 13 cards que o operador cortou **passam** no `audit_card_atomicity.py` e nos predicados de `card_checks.py`: são atômicos, têm um critério de acerto, frente gerativa, verso curto. O harness verifica FORMA e é cego a RENDIMENTO. Enquanto não existir predicado para isso, a triagem é humana e acontece **antes** do `insert_questao.py` -- e a lista integral de candidatos fica em disco para o operador derrubar o corte (`core/simulados/_s8_candidatos_full.json`; a proposta do agente, para o diff, em `_s8_erros_batch.PROPOSTA_AGENTE.json`).

---

## Formato atômico (referência EMED — sessão 124)

> **A régua de formulação foi calibrada.** Os 5 princípios acima definem *o que* testar (o elo quebrado); esta seção define *como escrever* — no **minimum information principle** (Wozniak), aferido contra os decks oficiais do EMED (275 decks colhidos em `resumos/**/Flashcards - <Tema>.pdf`, consultáveis por `python tools/emed_flashcards.py --query --tema "<tema>"`).

**O modo de falha que isto corrige — o "paragraph card":** empacotar `frente_contexto` + `frente_pergunta` + `verso_resposta` + `verso_regra_mestre` + `verso_armadilha` num item só. O aluno acerta 3 de 5 pedaços, marca "Bom", e os 2 esquecidos somem (illusion of competence). A auditoria da s124 reprovou a safra por isto (833 double-barreled; 350/398 sim/não com muro no verso; 835 set).

**As 7 regras (das 20 de Wozniak + os decks EMED):**

1. **Atômico -- 1 fato por card.** Se a resposta tem um "e" (progesterona *e* aromatase), são **dois cards**. O EMED nunca junta.
2. **Frente gerativa, nunca sim/não com o payload no verso.** A frente força *produzir* o discriminador, não julgar uma afirmação. ("Proteinúria: critério diagnóstico ou de gravidade?" > "proteinúria é gravidade? s/n".)
3. **Resposta = uma frase.** O EMED responde "Ovários." / "Estrogênio." / "Videolaparoscopia com biópsia." Curto e específico -- densidade clínica sim, parágrafo não.
4. **O "porquê" sai do recall.** Mecanismo/regra vai entre parênteses (lido *depois*, para consolidar) OU vira um **card discriminador próprio** -- não entra na carga de recuperação.
5. **Interferência -> card discriminador.** Quando duas coisas confundem (aromatase altaxbaixa, ureteralxvesical), um card que **contrasta as duas diretamente** (estilo EMED, cards adjacentes 23x24). A armadilha vira esse card, não um parágrafo colado.
6. **Evitar sets/enumerações.** Ranking de sítios, listas longas -> cloze ou cards ordenados, ou cortar a cauda de baixo rendimento. (O EMED testa "sítio mais frequente? -> Ovários", não o ranking inteiro.)
7. **Fonte + data em fato banca-dependente.** ACOG 2013, SBC 2025, MS -> selo de fonte/ano no card (herda a auditoria de evidência, ver §Evidência).

🔴 **Régua operacional (s128) -- UM CRITÉRIO DE ACERTO por card.** O teste decisivo não é contar entidades citadas, é contar **em quantas coisas independentes o aluno pode errar**. Se um card admite "acertei metade", ele está quebrado: a nota FSRS vira ininterpretável (acertar 1 de 2 não é "meio card", e o agendamento passa a mentir). Formulação do usuário: *"que a informação solicitada no card seja clara, que os cards não tenham diversos requisitos de acerto, e focassem no núcleo epistemológico do erro, na concatenação lógica dos conhecimentos necessários"*.

- ❌ "Qual a via **e** a composição da TH?" -> 2 critérios -> **dois cards**.
- ❌ "Qual o exame **e** a medicação?" -> 2 critérios (e aqui o exame nem discrimina) -> **um card, o da medicação**.
- ✅ "Cancro mole x donovanose: qual das duas dói e cursa com adenite?" -> 2 entidades, **1 critério** (a resposta é uma só) -> card discriminador legítimo (regra 5).

**Teste eixo x pacote (s142 -- distingue "múltiplos fatos" de "um fato com várias vitrines").** Antes de dar nota parcial ou marcar um card como double-barreled, pergunte: a resposta é **um eixo/discriminador único** com consequências que decorrem automaticamente dele (eixo), ou são **fatos independentes** que só coincidem de estar na mesma pergunta (pacote)? Só o pacote é defeito.
- ✅ **Eixo:** "O que determina qual das três (hérnia/hidrocele/cisto de cordão) se manifesta?" -> "O calibre do conduto." Isso é a resposta COMPLETA -- não exigir que o aluno também recite qual calibre dá qual entidade; isso é elaboração do mesmo eixo, não um segundo critério. Nota cheia por nomear o eixo.
- ✅ **Eixo:** "O que muda entre combinado e progestágeno isolado em TEV/trombogênica/amamentação/pós-parto?" -> "Ter ou não estrogênio" é o eixo único; os 4 contextos são vitrines do mesmo fato, não 4 critérios.
- ❌ **Pacote:** "Qual o protocolo de vigilância de contatos de hanseníase, e por quanto tempo?" -> embute um fluxograma inteiro (avaliação inicial -> sintomático/assintomático -> reagente/não-reagente -> duração) numa resposta só. Isso não é discriminador único com vitrines -- são nós de decisão diferentes. Vira 1 card por nó (ver `analisar-questao.md` §11, taxonomia "Fluxograma").
- ❌ **Pacote (cadeia causal longa):** um card cuja resposta é uma cadeia de 3+ elos causais encadeados (ex.: "por que a DRC causa hiperparatireoidismo" -> queda de TFG -> hiperfosfatemia + queda de 1-alfa-hidroxilase -> hipocalcemia -> estímulo à paratireoide) não é card, é aula compactada. **Decompor em 1 card por elo/mecanismo** (altura `mecanismo`, ver §Altura graduada) ou arquivar (`needs_qualitative=2`) se nenhum elo isolado vale a pena.

🔴 **A reforja também precisa passar no teste de eixo x pacote.** Corrigir o CONTEÚDO de um card errado (fato trocado, dado desatualizado) não corrige automaticamente o FORMATO -- é comum reescrever a resposta certa ainda empacotando vários nós/fatos juntos (aconteceu em produção: um card de conteúdo errado foi corrigido e o reescrito ainda saiu mais double-barreled que o original). Ao reforjar, rodar os dois testes (conteúdo E atomicidade) sempre, não só o que motivou a reforja.

🔴 **Reforja por "confuso"/"mandado" mira a FRENTE, não o verso (sessão 151).** Quando o usuário sinaliza que um card está confuso sem apontar erro de conteúdo, o defeito normalmente mora no ESTÍMULO -- `frente_contexto` truncando achados demais numa frase só, ou `frente_pergunta` abstrata demais para gerar recall. Reescrever o verso, mesmo que o conteúdo fique melhor, não resolve essa queixa: confirmado numa drenagem de 80 cards em que dois cards foram reforjados mexendo principalmente no verso, com a frente quase intocada -- o usuário leu os dois como "idênticos" nas duas vezes que foram re-apresentados. Só depois de reescrever a frente de verdade (cortar achado redundante, separar clínica de exame em frases distintas, converter pergunta abstrata em mini-caso concreto que já embute o padrão discriminador) é que o usuário confirmou. Ao reforjar por queixa de confusão, editar primeiro/principalmente `frente_contexto`+`frente_pergunta`; só tocar no verso se o conteúdo também estiver errado. Se a queixa persistir após uma rodada, perguntar explicitamente qual campo incomoda em vez de adivinhar de novo.

**Fronteira com a execução de prova:** questão de prova *legitimamente* cobra duas metades ao mesmo tempo. Isso se treina **resolvendo questões**, não no flashcard -- espelhar a demanda composta no card contamina a medida de recall. Detector: `python tools/audit_card_atomicity.py` (WARN no `auto_check`); triar a worklist pelo critério acima, não pelo regex.

### Reconciliação com o targeting metacognitivo

Isto **não** repudia o card ancorado no erro -- **refina**. O diagnóstico metacognitivo (os 5 princípios) continua escolhendo **QUAL fato atômico** testar (o elo que quebrou -- personalização que o EMED não tem). Muda a **formulação**: um elo quebrado -> **N cards atômicos** no formato EMED, um deles podendo ser o discriminador. Certo no *o quê*; corrigido no *empacotamento*.

### Antes/depois

**833 (double-barreled) ->** 2 atômicos + 1 discriminador:
> ❌ "Quanto à progesterona e à aromatase, o que caracteriza o endométrio na endometriose?" -> verso com 2 fatos + regra + armadilha.
> ✅ **A:** "Na endometriose, a aromatase nos implantes está aumentada ou reduzida?" -> "Aumentada (super-expressa)." *(gera estrogênio local -> por isso inibidor de aromatase funciona)*
> ✅ **B:** "Na endometriose, o endométrio ectópico responde à progesterona?" -> "Não -- é resistente." *(perde o freio antiestrogênico -> proliferação)*

**350 (sim/não com muro) ->** gerativo + datado:
> ✅ "Proteinúria é critério diagnóstico ou de gravidade da pré-eclâmpsia?" -> "Diagnóstico." *(gravidade > 5g/24h removida pela ACOG 2013)*

---

## Convenção de Encoding e Zero LaTeX (sessão 103/108)

É rigorosamente **proibido** utilizar sintaxe de LaTeX inline (`$ ... $` ou `$$ ... $$`), comandos matemáticos (`\rightarrow`, `\le`, `\ge`, `\mu`), ou cifrões encapsulando números e desigualdades (`$< 60$`, `$> 1000$`, `$\rightarrow$`) na redação dos campos `frente_pergunta`, `frente_contexto`, `verso_resposta`, `verso_regra_mestre` e `verso_armadilha`.
- Também é proibido o uso de setas Unicode (→) e aspas ou travessões inteligentes (–, —).
- **Usar exclusivamente ASCII/Markdown limpo:** seta simples (`->`), sinais diretos (`< 60`, `> 1000`, `<=`, `>=`), aspas retas (' ou ") e hifens simples/duplos (- ou --).
- Essa regra garante legibilidade limpa, evita quebras de encoding na exportação para Anki/FSRS e previne ruídos de leitura no terminal Windows.

---

## Granularidade

- **1 a 3 cards por erro.** A maioria dos erros rende 1-2. Acima de 3, o erro provavelmente mistura conceitos — reanalisar.
- **Armadilha: linha vs card próprio.** O distrator vai como `verso_armadilha` dentro do card de conteúdo. Só vira **card separado** se for ele mesmo um conceito recall-ável e distinto (raro). Não criar card de armadilha por padrão.
- **Atômico ≠ raso.** Atômico é *um conceito*, mas a resposta deve ser completa (agentes com seus nomes, doses, critérios) — densidade clínica como nos resumos.

---

## Altura graduada e cards de andaime (sessão 082)

O card ancorado no erro (acima) é o **topo** de uma cadeia — o elo metacognitivo fino da questão. Para temas em que o estudante está **frio**, o topo é inacessível: faltam os elos a montante. A altura de um card é, portanto, um **gradiente**, não um par base/topo:

- **`base`** — conceito primitivo do tema (ex.: "cianose = shunt D→E"). Não nasce de um erro; nasce de uma **lacuna de fundação detectada num cluster** e é ancorado no resumo.
- **`mecanismo`** — o porquê causal **encadeado** que liga a base ao topo (ex.: "por que a T4F cursa com hipofluxo"). É o degrau onde o raciocínio mecanístico se firma — o de **maior rendimento**, porque o gap diagnosticado costuma ser causalidade, não fato.
- **`nuance`/`detalhe`** — discriminações finas intermediárias, quando preciso.
- **topo** (`conteudo`/`elo_quebrado`) — o card de erro clássico.

O campo `tipo` carrega a altura. Quantos degraus existem é **inferido da iteração**: onde um elo trava (cluster de cards-alvo caindo no mesmo eixo), costura-se o degrau **imediatamente adjacente** (propagação local) — não se repete o topo nem se reconstrói tudo. Cards de andaime são baratos e cirúrgicos; acumulá-los é o **mapa fino das lacunas**, não ruído.

**Gatilho:** card isolado caindo = recall (re-drill). **Cluster** caindo no mesmo conceito = fundação ausente → gerar andaime.

### CLI — `tools/insert_card_base.py`

Persiste cards de andaime (qualquer altura via `tipo`) **sem erro de origem** (`questao_id=NULL`), criando `flashcards` + `fsrs_cards` (state 0). Idempotente por (tema, pergunta, tipo). Assinatura canônica:

```bash
python tools/insert_card_base.py --area AREA --tema "TEMA" --from cards.json [--dry-run]
```

JSON: lista de `{tipo?, frente_contexto?, frente_pergunta, verso_resposta, verso_regra_mestre?, verso_armadilha?}` (`tipo` default `'base'`). Cada card de andaime segue os 5 princípios acima + a regra de grounding: razão de existir explicável em 1 linha, ancorada no resumo + no cluster que o motivou (`ai-eng`: "especificidade sem contexto é criptografia").

---

## Exemplo-âncora: erro #211 (Úlceras Genitais)

**Erro real:** validou a alternativa por reconhecer 3 de 4 agentes corretos numa questão de lista, sem conferir o 4º (*Trichomonas* — corrimento, não úlcera).

### ❌ Ruim (geração heurística atual)

> **P:** "1) Classificar IST por síndrome: úlcera (...) vs corrimento (...); 2) Em questões de lista, conferir cada item; 3) Saber que Chlamydia tem dois comportamentos conforme sorotipo?"
> **R:** "Trichomonas vaginalis é protozoário..."

Por que falha: colou o `habilidades_sequenciais` cru (não é pergunta, vaza tudo); viola os princípios 1 e 3.

> **P:** "Qual o distrator típico do examinador em: IST por síndrome — armadilha do agente intruso em lista?"

Por que falha: template genérico; não força recall de conteúdo. Viola 1, 2, 3.

### ✅ Bom (atômico, ancorado)

**Card 1 — Úlcera**
> **P:** Quais agentes causam **úlcera** genital?
> **R:** *Treponema pallidum* (sífilis) · HSV · *Haemophilus ducreyi* (cancro mole) · *Klebsiella granulomatis* (donovanose) · *Chlamydia trachomatis* **L1-L3** (LGV).
> **Regra-mestre:** *Chlamydia* entra aqui só nos sorotipos **L1-L3**; os **D-K** dão corrimento — mesma bactéria, dois quadros por sorotipo.
> **Armadilha:** *Trichomonas* **não** causa úlcera — é o intruso clássico enfiado em listas de úlcera.

**Card 2 — Corrimento**
> **P:** Quais agentes causam **corrimento/cervicite**?
> **R:** *Trichomonas vaginalis* · *Neisseria gonorrhoeae* · *Chlamydia trachomatis* **D-K** · *Gardnerella vaginalis* · *Candida*.
> **Regra-mestre:** *Chlamydia* **D-K = corrimento**; **L1-L3 = úlcera (LGV)** — a pegadinha da sobreposição.
> **Armadilha:** *Trichomonas* aparece como distrator em listas de "úlcera" — confira: é corrimento.

A distinção (dois grupos) e a sobreposição (*Chlamydia* por sorotipo) ficam reforçadas nos dois cards; o erro específico (*Trichomonas* mal-agrupado) vira a linha de armadilha — sem meta-card.

---

## Os 5 campos estruturados (output)

```
frente_contexto:    [cenário clínico em 1-2 frases, OU vazio se a pergunta é conceitual direta — nunca vaza a resposta]
frente_pergunta:    [pergunta clínica direta, termina em "?"]
verso_resposta:     [resposta completa e densa — nunca uma letra isolada]
verso_regra_mestre: [a distinção/sobreposição que previne a confusão]
verso_armadilha:    [o distrator específico que pegou o usuário, ancorado no resumo]
```

🔴 **Reenquadramento (s124 -- ver §Formato atômico):** `verso_regra_mestre` e `verso_armadilha` **deixam de ser carga de recall obrigatória em todo card**. O recall é sempre **1 fato** (`verso_resposta` = uma frase, não um parágrafo). Default: a **regra** entra como parêntese lido-depois OU vira **card discriminador próprio**; a **armadilha** idem (card discriminador, não parágrafo colado). Encher os 5 campos como um mini-resumo é o "paragraph card" (defeito). Os campos permanecem no schema (compat), mas o contrato desaconselha usá-los como carga de recuperação.

Persistir via `insert_questao.py` (go-forward) ou via o caminho de UPDATE/`--cards-file` (regeneração) — ver `analisar-questao.md` §9 e a spec da Onda B.

### 🔴 Alinhamento interno da FRENTE — os 3 defeitos nomeados (F81/B1, s176)

> Todo predicado anterior comparava **frente × verso**. A relação entre `frente_contexto` e
> `frente_pergunta` estava fora de cobertura — e foi de lá que saíram os três últimos defeitos
> achados por **leitura do usuário**, não por gate. Os três abaixo nascem **WARN** no
> `card_checks.py`; viram BLOCK quando o passivo zerar. Spec:
> [`.vibeflow/specs/alinhamento-frente-do-card.md`](../../.vibeflow/specs/alinhamento-frente-do-card.md).

1. **Contexto redundante** — a pergunta reengole o contexto (>= 80% dos tokens). O contexto existe
   para trazer **dado que a pergunta precisa**; se a pergunta já diz tudo, ele só ocupa a tela
   antes do texto se repetir. Caso extremo: contexto == pergunta, palavra por palavra.
   *Ao cunhar:* ou o contexto carrega um dado concreto (idade, tempo, valor, achado de exame), ou
   ele fica **vazio de verdade** — meio-termo é ruído.
2. **Pergunta genérica com vinheta decorativa** — a pergunta nomeia um par `A x B` **e** pede um
   discriminador geral (*"que achado separa"*, *"qual das duas"*), respondível direto do livro.
   A vinheta não é lida, porque a resposta sai igual sem ela.
   *A correção não é apagar a vinheta: é fazer a pergunta APLICAR ao caso* — "qual a hipótese mais
   provável?" obriga a ler os dados; "que achado separa?" não. Mesmo par de diagnósticos, cards de
   qualidade oposta.
3. **Contrafactual mal-formado** — a pergunta afirma que um achado está **ausente neste quadro** e,
   ao mesmo tempo, pede que esse achado **exclua** um diagnóstico. Falta o condicional.
   *O conserto é uma expressão:* **"se estivesse presente"**. Compare — ❌ *"Qual achado, AUSENTE
   nesse quadro, afastaria DRESS?"* × ✅ *"Qual achado, **se presente** durante o episódio, aponta
   para crise não epiléptica?"*. Mesmo desenho, e só o segundo é respondível.

⚠️ **O que os predicados NÃO pegam, e a spec declara:** o caso em que a vinheta trabalha
**contra** a pergunta por razão puramente semântica. Isso é leitura, não regex — e continua sendo
trabalho humano. Gate verde aqui não significa frente alinhada; significa que os três padrões
nomeados não aparecem.

### 🔴 Dêixis sem contexto — o 4º defeito, e o único que é **BLOCK** (F79b, s176)

A pergunta aponta para um antecedente — *"neste paciente"*, *"esse médico"*, *"do caso acima"*,
*"na vinheta"* — e **não existe vinheta**: `frente_contexto` está vazio. O card é literalmente
**inrespondível a frio**, e nenhuma dose de conhecimento o salva. Foi assim que o usuário achou o
`#367` no drill da s169 (*"que elementos DO CASO... classificam ESSA morte como suspeita?"*, com
contexto vazio) — e o check de auto-suficiência tinha rodado e não o pegou.

*Ao cunhar:* **ou a vinheta entra, ou a pergunta perde a referência anafórica.** "Qual a conduta
neste paciente?" sem vinheta vira "Qual a conduta na *[condição]*?".

🔴 **Este nasce BLOCK, não WARN** — a escrita é **recusada**. A regra warning-first diz "vira BLOCK
quando a base zerar", e a base **está** zerada e medida: **passivo 0, falso-positivo 0 em 1419
cards ativos**, com **95 cards de controle** que usam a mesma dêixis **e têm vinheta** (legítimos,
corretamente fora). O gate aqui é **prospectivo**: impede o defeito de reentrar pela porta do
writer — que foi exatamente como as áreas fantasma voltaram (F89).

⚠️ **Dêixis é demonstrativo, não classe.** *"do paciente asmático"*, *"na criança"*, *"no
lactente"* são **categoria clínica**, não referência a um caso — o candidato amplo do predicado
pegava 26 cards assim, todos falsos. E *"confirmação **do caso**"* é caso-índice epidemiológico,
não vinheta.

---

## Fila de reforja — `tools/reforja.py` (B2, s176)

> **Assinatura canônica deste CLI** (`AGENTE.md §7.2`: a assinatura completa vive em UMA skill).
> Spec: [`.vibeflow/specs/fila-de-reforja-como-estado.md`](../../.vibeflow/specs/fila-de-reforja-como-estado.md).

**Por que existe:** marcar um card para reforja era escrever uma frase num `HANDOFF.md`. O passivo
foi contado como **12, 13, 15 e 38** em sessões diferentes, e o **#792** atravessou três sessões
marcado e está em `card_version = 1` — nunca foi tocado.

| Comando | Função |
|---|---|
| `--fila [--todas] [--json]` | O passivo. **É a única cifra citável** — número escrito à mão em HANDOFF é claim que envelhece. |
| `--marcar ID --motivo M [--origem S]` | Abre uma marca. Marcar o mesmo par de novo **cria outra linha** (append-only): 3 marcações são 3 linhas, e a fila conta. |
| `--fechar ID --motivo M` | Fecha **re-verificando**. Se `M` nomeia um predicado de `card_checks`, ele re-roda sobre o card como está agora e **recusa** o fechamento se ainda acusar. |
| `--fechar ... --forcar --justificativa "..."` | Fecha mesmo assim. A justificativa fica **gravada na linha**. |
| `--descartar ID --motivo M --justificativa "..."` | *"Olhei e não era defeito"* — desfecho legítimo e **diferente** de "resolvi". |
| `--backfill --dry-run` / `--apply` | Migra as marcas que viviam em prosa. Declara o COUNT **antes** de escrever; o `--apply` é decisão do operador. |

🔴 **Fechar é uma afirmação checável.** `card_version` **não** é evidência de reforja feita — o
F82 mediu **#321** em `v2` com o defeito intacto, e a s176 mediu o caso mais duro: **#1568** tem
evento de reforja de 09/09 (`v1 -> v2`, mexeu na `frente_pergunta`) e **continua disparando** o
predicado de contrafactual. *Reescrever não é o mesmo que resolver.* Nenhum sinal de "alguém
editou" fecha uma marca.

⚠️ **Fronteira declarada:** defeito sem predicado que o meça — *pacote de fatos*, *pergunta
circular*, o eixo C semântico — fecha por palavra humana, e a linha grava `evidencia: 'humana'`.
Não é falha: é o limite do que hoje é verificável, escrito em vez de maquiado.

🔴 **Um WARN dos predicados NÃO vira marca sozinho.** O CLI oferece candidatos; quem marca é
gente. Lição do **F87**: o harness mede *forma*, não *rendimento* — 13 cards que o operador
reprovou passam em todos os predicados.

---

## Backfill — regenerar cards legados

> **Histórico:** sessão 075 aposentou (`needs_qualitative = 2`) os 70 cards heurísticos flagueados (`needs_qualitative = 1`). A sessão 076 descobriu **87 heurísticos remanescentes** (`quality_source = 'heuristic'`, `nq = 0`) que escaparam do filtro da bankruptcy e os **regenerou** por este protocolo (decisão do usuário: regenerar, não aposentar). O critério da fila foi corrigido de `nq = 1` para `quality_source = 'heuristic' AND nq != 2`. Após s076 **não há heurísticos ativos** — esta seção volta a ficar dormente; só reaparece se a geração heurística for reintroduzida (não deve).

Os cards cunhados pela heurística antiga devem ser refeitos pelo agente, um erro por vez:

1. **Puxar a fila:** `python tools/cards_regen_queue.py [--area X] [--limit N] [--questao-id ID]` — emite, em JSON, cada erro com seu substrato metacognitivo (`tipo_erro`, `habilidades_sequenciais`, `o_que_faltou`, `alternativa_correta`/`marcada`, `armadilha_prova`) + os `cards_atuais` (com `card_id`). Critério atual: `quality_source = 'heuristic'` e `needs_qualitative != 2`.
2. **Ancorar no resumo:** buscar o resumo correspondente via RAG local (`app.engine.rag.search`) para os critérios/alertas de incidência.
3. **Cunhar** 1-3 cards atômicos pelos 5 princípios acima.
4. **Persistir, preservando o FSRS:**
   - Reescrever um card existente (mantém `card_id` → estado FSRS):
     ```python
     from app.utils.db import update_flashcard_fields
     update_flashcard_fields(card_id, {"frente_pergunta": "...", "verso_resposta": "...",
                                        "verso_regra_mestre": "...", "verso_armadilha": "...",
                                        "tipo": "conteudo"})
     ```
   - Adicionar cards novos ao mesmo erro: `python tools/insert_questao.py --cards-file <json>` (ver `analisar-questao.md §9`).
5. **Priorizar áreas fracas** (`--area`) e processar em lotes — não big-bang. Revisar a qualidade pela régua antes de seguir.

> A geração heurística (`regenerate_cards.py`) foi **aposentada** — a geração é do agente, o código só persiste.

---

## Fronteira com `estilo-resumo.md`

- **Resumo** = documento técnico de referência, didática 80/20, cumulativo, por tema.
- **Flashcard** = recall atômico de um ponto de ruptura específico, ancorado no resumo.

O card consome o resumo; não o substitui nem o duplica.

## Evidência: o card herda a auditoria da origem

O card **não é auditado isoladamente** — ele herda o veredito de evidência da questão/resumo de origem (`core/contracts/evidence-governance.md` §1). Quando a `verso_regra_mestre` afirma uma conduta/dose/cutoff decisória já auditada, **carregar a citação** (sociedade/ano ou PMID) e, se for conflito banca x evidência, refletir o 🔴 alerta banca-dependente na `verso_armadilha`.
