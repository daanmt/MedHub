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
