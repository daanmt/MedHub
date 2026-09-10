# Session 175 -- Drenagem integral da fila FSRS (76 cards) e a correcao dura do usuario sobre o formato do DRENAR

**Data:** 2026-09-10 (manha, ~06h50 -> ~08h) - **Ferramenta:** Claude Code (Opus 5, 1M) - **Continuidade:** `session_174.md`
Sessao de **ESTUDO** (zero engenharia, conforme o gate do HANDOFF). O usuario abriu pedindo cards e a fila do dia foi drenada por inteiro.

---

## 0. O que o usuario trouxe

- Fez sozinho, na quarta 09/09: a **lista de revisao de Diarreia** (nao registrada -- ver Pendencias) e **105 cards** de FSRS (confirmado no revlog).
- Pediu explicitamente: *"Queria fazer mais uns cards contigo agora cedo."*

## 1. A correcao do usuario -- tres regras furadas no primeiro bloco

Terceiro turno da sessao, veredito literal: *"Voce saiu completamente do padrao. Esta dando feedback de card nota 3 e 4, dividindo os blocos em 'menores' e ainda colocando esse trem no cli: `<sub>...</sub>`. Voce deu o boot direito, mestre?"*

As tres, e o que causou cada uma:

| furo | regra violada | causa raiz |
|---|---|---|
| justificativa em prosa em TODO card (inclusive 3 e 4) | **Invariante F** (`revisar.md`): verso + nota + tally e nada mais | o **passo 4 da propria skill** ainda manda "informar a nota proposta + justificativa em 1 linha" -- texto anterior a s154/s170 que o Invariante F supersede e ninguem lapidou |
| lote de **6** cards | regua real = **10-15** (s130 pediu 10; s152 rodou blocos de 15) | o **"Modo conversacional padrao"** da mesma skill ainda diz *"o usuario pediu 3, depois 5, depois 6"* -- idem, texto morto nao lapidado |
| `<sub>preview</sub>` em HTML por card | ruido ilegivel no terminal | contrato P3 part-3 manda mostrar o preview "junto das opcoes"; como a nota e do agente (override passivo), nao ha opcoes -- o preview virou decoracao |

**O boot estava certo** (AGENTE.md + HANDOFF + skill inteira + estado medido antes do 1o card). O erro foi de **precedencia entre camadas do mesmo documento**: apliquei as linhas velhas em vez das que as revogam. Virou **F90** no ledger (`§6r`).

**Correcao aplicada no mesmo turno:** blocos de **16**, pipeline de **profundidade 2** (gabarito do bloco N sai junto com as perguntas do N+2), preview cortado, zero prosa no meio.

## 2. A drenagem -- 76 cards, fila zerada

Fila servida com `--cluster --prevalencia` (ENAMED em 3d): 9 atrasados + 2 erros frescos + 55 de hoje + 10 novos.

| bloco | tamanho | notas |
|---|---|---|
| 1 (formato errado) | 6 | `4 4 3 3 4 4` |
| A | 6 | `4 4 4 1 1 4` |
| B | 16 | `4 1 4 4 4 3 4 4 4 3 4 1 4 4 2 4` |
| C | 16 | `4 4 3 3 4 1 4 4 4 4 4 2 4 4 4 4` |
| D | 16 | `4 4 4 4 4 4 3 4 4 4 4 4 4 4 1 3` |
| E | 16 | `4 4 4 4 4 4 1 3 1 1 1 1 4 2 4 1` |

**Total: 52x nota 4 - 9x nota 3 - 3x nota 2 - 12x nota 1.**

**A separacao que muda o diagnostico** (e que quase virou leitura errada):

| | cards | notas 1-2 | leitura |
|---|---|---|---|
| vencidos + agendados (ja vistos) | 66 | **6** | ~91% funcional |
| **novos** (1a exposicao) | 10 | **7** | intake, nao esquecimento |

Seis das doze notas 1 eram **cards novos de Cirurgia Infantil, nunca introduzidos**. Contar essas 6 como "buraco" teria inflado o diagnostico em 100%. Vale como regra: **nota 1 em card `state=0` e linha de base, nao sinal.**

## 3. Achado clinico da sessao -- o bug 1c apareceu vivo, duas vezes em 20 cards

- **#313** (pancreatite, nota 3): "por que a TC nas primeiras 72h engana?" -> respondeu **subestima porque a necrose ainda nao se definiu**. Certo.
- **#311** (pancreatite, nota 2), 20 cards depois: "por que o USG, e nao a TC, e o **primeiro** exame?" -> repetiu **a mesma frase**. A resposta era outra: o USG responde **"e biliar?"** (etiologia acionavel no dia 1 -- CPRE se colangite, colecistectomia na mesma internacao); a TC responde "ha necrose/colecao?" **apos 72h**.

E o padrao [[feedback_bug_fato_contexto_errado]] (fato verdadeiro aplicado fora da condicao que ele governa), desta vez capturado **dentro da mesma sessao**, com o fato correto sendo aprendido no card 3 e mal-aplicado no card 27. Ritual proposto ao usuario: *"a pergunta e sobre etiologia, gravidade ou complicacao?"*.

**Outros gaps reais (card ja visto, nota 1-2):**

- **#1270 x #453 -- AGC fundido num braco so.** Respondeu "colposcopia" para os dois. AGC dispara **dois bracos**: cervical (colposcopia sempre, qualquer idade) e endometrial (**so se >= 45a ou SUA** -> USG TV -> histeroscopia se alterado). Erro estrutural, nao de memoria.
- **#735 -- indicacao de dreno na apendicectomia INVERTIDA.** Respondeu peritonite/extravasamento, que e exatamente a armadilha. Dreno = risco **localizado** (abscesso localizado, autolise de base p/ vigiar o coto); peritonite difusa, liquido livre e sepse **nao** drenam.
- **#1584 -- Imunizacoes, "ainda exige" lido como "o esquema e de".** 1 dose de triplice viral aos 12 meses, faltava **1**; respondeu 2. E a armadilha literal do card ("reiniciar em vez de completar") na sua **2a maior area de erro acumulado** (25 erros).
- **#1568** (DRESS x SSJ), **#1574** (Osgood x SDPF), **#1571** (hemangioma x HNF), **#1539** (AMP 150 mg IM = dose contraceptiva, nao hemostatica).

**O que ele ganhou** (vale registrar -- e sinal de curva subindo): resistiu ao hematoma "contido" no AAST IV (#238), ao "cruza a linha media" no Wilms (#587), e fechou **clozapina x carbamazepina** (#560/#561) no **5o encontro** com esse par -- estava listado como padrao ativo no HANDOFF da s174.

## 4. Defeitos de card capturados (flywheel de reforja)

| card | defeito | estado |
|---|---|---|
| **#1568** | frente pede achado "AUSENTE nesse quadro" e no mesmo folego o que ele "afastaria/fecharia" -- falta o *se estivesse presente*. Premissa embutida + tempo verbal contraditorio | **novo** -- fixture do F81 (eixo contexto x pergunta) |
| **#583** | composta ("se baseia em que **e** como difere do sintotermico") | ja na fila de reforja (HANDOFF s174); **confirmado em uso** -- ele respondeu so a 1a metade |
| **#582** | composta ("qual via evitar **e** como regularizar") | idem, **confirmado em uso** |

Os tres reforcam [[feedback_reforja_flywheel_auditoria]]: defeito de card e achado, nao ruido.

## 5. Revisao Direcionada de fechamento

Seis eixos densos + dois curtos, ancorados em `resumos/` (diagnostico do resumo contra o gap):

1. **AGC tem dois bracos** (cervical x endometrial, e por que o risco de 15-56% nao autoriza pular a triagem)
2. **Pancreatite: cada exame responde uma pergunta** -- e o bug transversal do item 3 acima
3. **DRESS x SSJ** -- a mucosa e o divisor (edemacia sem descolar x necrose com Nikolsky+ e mucosite em ~90%)
4. **Joelho que doi na crianca** -- Osgood (caroco no tuberculo) x SDPF (retropatelar difusa, nada a palpar) x Perthes (joelho normal, quadril limitado)
5. **Apendicite** -- quando drenar + os dois novos pediatricos (GECA em ~40%, USG > 6 mm)
6. **Imunizacoes do adolescente** -- HPV 9-14 c/ resgate ate 19 - ACWY 11-14 **sem resgate** - triplice viral 2 doses ate 29a, **completar nao reiniciar**
- curtos: HNF (cicatriz central com realce tardio) e AMP 150 mg IM

**Diagnostico do resumo:** `resumos/Cirurgia/Cirurgia Infantil.md` **cobre todos os 6 pontos que cairam** (linhas 120-122 volvo, 146/151 HAEC, 244-245 apendicite pediatrica + corte de 6 mm, 331/337/370 Wilms x neuro, 378 biopsia hepatica na AVB). **Nenhuma edicao de resumo foi necessaria** -- o gap era recall / 1a exposicao, nao materia deficiente. Registro explicito porque a tentacao contraria e forte (ver [[feedback_diagnostico_resumo_nao_e_conhecimento]], que vale nos DOIS sentidos).

**Carimbos `review_log`** (Invariante B): ids 143-150, `kind=directed_review`, temas 410 - 209 - 451 - 454 - 290 - 265 - 452 - 447.
**Notas de aula (F18c):** 410=7 - 209=6 - 451=8 - 454=7 - 290=6 - 265=8 - 452=8 - 447=4 (`fonte='aula'`; nenhuma nota soberana `usuario` foi sobrescrita).

## 6. Numeros

- **Cards:** 76 revisados (0 re-record; regra anti-duplo-registro respeitada). Fila do dia **zerada**; 4 cards de relearning voltam amanha (735, 1571, 1270, 1584) + 10 novos entraram no lugar.
- **Blackout F71 em acao:** o #238 pediu 14/09 e o balanceador declarou **OVERFLOW** (sem vaga antes do ENAMED dentro da folga) em vez de silenciar. O mecanismo da s174 funcionou na primeira sessao real.
- **Volume de questoes:** inalterado em **7036** -- a lista de Diarreia continua sem registro.
- **Re-drill:** nao executado (usuario encerrou); os 12 cards nota 1-2 ficam para a proxima sessao de cards.

## 7. Pendencias abertas por esta sessao

1. **`registrar_sessao_bulk` da lista de Diarreia (revisao) de 09/09** -- falta feitas/acertos. Ele avisou que **retorna com as questoes do dia**; a ordem dura vale: registrar ANTES de analisar.
2. **Re-drill dos 12 cards nota 1-2** na abertura da proxima sessao de cards.
3. **Alvo ~100 cards/dia (qui-sex-sab)** -- a fila natural entregou 76. Para chegar a 100 e preciso abrir o `--new-limit` (default 10) contra o pool de **647** nunca introduzidos. **Decisao do operador**, ligada a F87 (regua de "card bom").
4. **F90** -- lapidar as duas linhas mortas do `revisar.md` (passo 4 "justificativa em 1 linha"; "Modo conversacional" com lote de 3/5/6). **Fila de engenharia**, nao esta janela.


---

## 8. Segundo ato -- 90 questoes registradas e 15 erros analisados (tarde)

O usuario voltou com **quatro listas** feitas em 09/09 e nunca registradas. Ordem dura respeitada: `registrar_sessao_bulk` **antes** de qualquer analise, em todas.

| lista | area | feitas | acertos | % |
|---|---|---|---|---|
| Diarreia (revisao) | Pediatria | 41 | 34 | 82,9 |
| Urologia T I | Cirurgia | 20 | 17 | 85,0 |
| Pneumonias Bact. T I | Pneumo | 16 | 13 | 81,2 |
| Urologia T II | Cirurgia (`--acumular`) | 13 | 11 | 84,6 |
| **total** | | **90** | **75** | **83,3** |

Volume **7036 -> 7126**. Estava congelado desde 08/09. Todas carimbadas com data de estudo 09/09 e observacao de que o registro e de 10/09.

**15 erros analisados, 4 elos que reincidem, 24 cards cunhados, 7 cortes por regenerabilidade.**

### 8.1 O achado clinico do dia -- confirmado no banco, nao inferido

🔴 **A prescricao da HPB e o output default quando aparece uma prostata.** O erro **#997** (Uro I Q1) tem `alternativa_marcada` = *"Prescrever alfa-agonista isolado ou associado a inibidor da 5-alfarredutase"*. O erro de Uro II Q2 tem *"Alfa-bloqueador associado a inibidor da 5-alfa-redutase"*. **Mesma prescricao, duas listas, duas perguntas diferentes, mesmo dia.**

Os dois **nao** se colapsam, e a diferenca manda o remedio: em #997 a droga era certa para a doenca e errada para o **momento** (investigar antes de tratar); em Uro II Q2 e errada para o **paciente** (I-PSS 7 < 8) e para a **pergunta** (o enunciado declara que ele veio para rastreamento de cancer). Formulacao correta = "output default diante de uma prostata", **nao** "trata antes de investigar", que so cobre um dos casos.

Em Uro II Q2 **os dois cortes ja estavam escritos no resumo dele** (linhas 96 e 108). E "sabia mas nao aplicou".

### 8.2 Os outros elos

- **Fato no contexto errado (1c) foi a assinatura do dia -- 5 ocorrencias, em tres escalas diferentes:** molecula (norfloxacina generalizada de "fluoroquinolona respiratoria"), framework decisorio (criterios de HPB aplicados ao CaP), e motivo da consulta (tratou HPB em consulta de rastreamento). Mais as duas de pancreatite da manha (a resposta de "TC precoce" reaplicada na pergunta da etiologia biliar).
- **Reincidencia exata em 2 dias:** Q3 de Diarreia e o erro **#963** (07/09) verbatim. Ele corrigiu a 1a metade e **repetiu a 2a identica** -- escolha estavel, nao desatencao.
- **Enunciado negativo (PAC Q3): fork aberto, nao fechado.** Marcar a alternativa A exige afirmar que ela e falsa; nao saber a vacina, sozinho, nao produz esse clique. Rota (i) erro de comando x rota (iii) promocao da Klebsiella. A distribuicao da turma pende para (i) -- A ficou com 7%, o balde de erro de leitura. **Pergunta ao usuario ficou pendente** (§9).
- **Buracos de cobertura de resumo, nao falha de estudo:** 3 dos 7 erros de Diarreia (§7 sem uma linha sobre acido-base ou potassio) e a §5.10 inteira de PAC (zero cobertura de eosinofilias pulmonares no repo).

### 8.3 Achados de mecanismo (F90-F92) -- ver `AUDITORIA_MEDHUB.md §6r/§6s`

- **F92 (RESOLVIDO):** o `Urologia.md` ensinava, na secao Armadilhas, **verbatim a alternativa que ele marcou e errou**. Corolario de metodo adotado: **ao diagnosticar erro em tema com resumo, ler o que o resumo diz sobre a alternativa MARCADA**, nao so sobre a correta.
- **F91 (ABERTO, ALTA):** `rag.search()` devolve `[]` com o motor offline; um subagente leu isso e escreveu fato falso num relatorio de evidencia.
- **F90 (ABERTO):** gate `CONTRATO_REVOGADO` cego por inventario.

## 9. Pendencias abertas por este segundo ato

1. **Pergunta ao usuario para fechar o fork da PAC Q3:** *"quando voce marcou A, estava afirmando que o pneumococo NAO e o agente mais provavel naquele etilista diabetico -- ou estava marcando a que achou verdadeira?"* Se rota (iii), resgatar o card cortado sobre "fator de risco nao destrona o agente mais comum".
2. **Valores laboratoriais da Uro II Q2** (eram imagem, nao transcritos). Se havia relacao PSA livre/total, o gabarito fica alcancavel pelo criterio do proprio resumo, sem depender do corte NAO-VERIFICAVEL.
3. **`resumos/Pediatria/Imunizacoes.md` §4.6** diz "as indicacoes nao mudaram, so o produto" -- desatualizado pela NT 52/2026 (19 -> 21 itens, esquema novo, CRIE -> RIE). Subproduto da auditoria, nao achado desta lista.
4. **Corte de sodio para salina hipertonica (120 x 125)** -- marcado como banca-dependente no resumo e no card, **nao auditado**.
5. **Corte superior do rastreamento SBU (70 x 75)** -- marcado no `Urologia.md §2.6` como "a conferir", numero **nao sobrescrito**.

## 10. Feedback do usuario sobre uso de subagents (correcao de processo)

Ao final, veredito literal: *"achei, no entanto, que voce deu uma volta muito grande para entregar algo simples. sumonou subagents que sumonaram outros subagents, para checar uma informacao. como os blocos eram curtos, voce mesmo poderia ter checado, que seja via websearch."*

**Custo medido que da o argumento:** 3 spawns, **~673k tokens e ~66 min** para 15 erros. O spawn de Urologia gastou ~25 min e ~238k tokens em **3 erros**, com cadeia de 2 niveis. E a delegacao **nao poupou a verificacao**: re-medi as afirmacoes load-bearing e **rejeitei duas** (os "772 cards" que eram 647; o "nao ha resumo indexado" que era falso).

Memoria `feedback_subagent_unico_analise_questoes` reescrita: **ate ~8 erros o agente principal analisa sozinho**; verificacao de cutoff via WebSearch direto; subagente so acima disso e **um so**; nunca subagente que sumona subagente. 🔴 A regra vive so na memoria do harness -- **candidata a portador versionado** (bifurcacao 6.1 do handoff de engenharia).

## 11. Handoff de engenharia

O `/ai-eng` (N=78, `ai-eng-ff`) reabriu o canal antes do fecho pedindo todos os achados. Entregue em **`docs/HANDOFF-ENG-2026-09-10.md`** (blob `db82fc3`), com destilado no canal (D22): achados de subagent, delta desde 09-09 16:00, Tier 3/0/1 em **ZERO** (gate de janela de estudo, desvio conforme), F90/F91/F92, contagens re-medidas e **3 bifurcacoes** para ele ordenar. Zero autorizacao concedida a peer.
