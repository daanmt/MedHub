---
name: "source-command-estilo-flashcard"
description: "Contrato de autoria de flashcards do MedHub — os 5 princípios para cunhar cards ancorados no erro metacognitivo. Consultar antes de gerar ou regenerar qualquer card."
---

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

## Os 5 princípios

1. **Conteúdo clínico atômico.** Um conceito por card. Decompor em vez de combinar: se o erro toca duas listas (ex.: agentes de úlcera *e* de corrimento), são **dois cards**, não um. O card é **recall de conteúdo**, nunca um card sobre "o hábito de raciocínio".
2. **O erro define o alvo.** `tipo_erro` + `o_que_faltou` apontam *qual* conteúdo drilar e *qual distinção/sobreposição* tornar central. O card é específico ao erro do aluno — não uma varredura genérica do tema.
3. **Pergunta direta, sem vazar a resposta.** A `frente_pergunta` é uma pergunta clínica real terminando em "?". **Nunca** colar o `habilidades_sequenciais` cru, **nunca** embutir a resposta no contexto, **nunca** usar template tipo "Qual o distrator típico em...?".
4. **Regra-mestre = a distinção/sobreposição** que previne a confusão. É o princípio transferível que costura este erro a outros (ex.: *Chlamydia* L1-L3 = úlcera vs D-K = corrimento).
5. **Armadilha = o distrator específico** que pegou o usuário, ancorado no resumo (que carrega o alerta de incidência em prova). Não um distrator hipotético — o que de fato induziu o erro.

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
