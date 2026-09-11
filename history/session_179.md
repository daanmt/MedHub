# Session 179 -- Drenagem de 90 cards (teto), e a primeira contra-evidencia medida da Revisao Direcionada

**Data:** 2026-09-11 (tarde, ~11h40 -> ~13h40) - **Ferramenta:** Claude Code (Opus 5, 1M) - **Continuidade:** `session_178.md` (engenharia, manha)
Sessao de **ESTUDO**. Zero engenharia: o permit de 10/09 estava consumido e o operador abriu pedindo cards.

---

## 0. O que o usuario trouxe

- Abriu com *"bora, manda os cards"* e uma **regra nova, permanente**: *"a partir de hoje, passarei a compartilhar o racional por ter marcado a questao incorreta e, com isso, voce tera mais recursos para dissecar o erro com mais profundidade."* Gravado na memoria como `feedback_usuario_declara_racional_erro` -- **racional declarado vence racional inferido**.
- Pediu, no mesmo turno: *"Favor agendar os cards que cairem no dia 13/14 para 15/09 em diante."* Virou **F98**.
- Encerrou com *"retorno depois com mais questoes que eu tenha feito e mais uma rodada de 90 flashcards."*

## 1. A drenagem -- 90 cards, o teto exato

Fila servida com `--cluster --prevalencia`: **4 atrasados + 8 erros frescos + 78 de hoje + 10 novos = 100**. Os 10 novos ficaram **de fora por decisao**: teto do dia = 90 (regime de divida), ENAMED em 2 dias e blackout em 13-14/09 -- intake novo hoje nasceria sem lugar para cair. 4 + 8 + 78 = 90 fecha o teto sem sobra.

| bloco | tamanho | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|
| 1 | 15 | 7 | 3 | 1 | 4 |
| 2+3 | 30 | 16 | 5 | 2 | 7 |
| 4+5 | 30 | 22 | 2 | 3 | 3 |
| 6 | 15 | 8 | 4 | 1 | 2 |
| **total** | **90** | **53** | **14** | **7** | **16** |

**59% nota 4, 74% em 3-4.** Zero `[WARN] reason divergente` nas 90 gravacoes (proveniencia propagada corretamente em todas). Zero re-record.

**Pipeline de profundidade 2 aplicado a partir do 2o turno** -- o bloco 1 saiu sozinho, e foi erro meu de abertura: `feedback_revisar_pipeline_blocos` manda liberar **os dois primeiros** de saida. Corrigido no turno seguinte (gabarito do 1 + perguntas do 2 **e** do 3 juntos), e o operador passou a responder **30 frentes por turno** sem atrito -- confirmando de novo que o apetite e maior que o texto da skill sugere.

## 2. O achado da sessao -- ensinar nao fechou o gap (F100)

Tres pontos de **Cirurgia Infantil** falharam **duas vezes cada** (card + re-drill) e os tres tinham sido ensinados na Revisao Direcionada da **s175, 24 horas antes**:

- **#719** (AVB / biopsia hepatica): "tc com contraste" -> "ecoendoscopia?"
- **#721** (apendice > 6 mm): "5mm?" -> **"3 mm?"** -- andou **para longe**, o que diz que nao ha ancora nenhuma
- **#720** (GECA em 40%): "adenite mesenterica" -> "pela adenite mesenterica, nao?" -- mesma resposta

A s175 registrou que o resumo *"cobre todos os 6 pontos"* e que **nenhuma edicao era necessaria**. **Re-verifiquei: cobre mesmo** -- `resumos/Cirurgia/Cirurgia Infantil.md` linhas 378/379/380, cada uma com marcador vermelho, mais o corpo em 244-245. Entao resumo correto + aula dada + `review_log` carimbado = zero retencao em 24h.

Leitura que sai disso, e ela e estreita de proposito: os quatro pontos sao **fato arbitrario** (6 mm, 40%, biopsia x colangioRM, o nome HAEC), nao regeneram de mecanismo, e o gargalo e **numero de exposicoes**, nao materia deficiente nem autoria de card. O mesmo fechamento da s175 produziu **14 fechamentos** hoje (Faget, PTH baixo, via oral na gestante, os dois bracos do AGC, 47x69 -- neste ele ainda somou a mola completa 46 diploide, que o card nem pedia). **A Revisao Direcionada funciona onde ha mecanismo e falha onde o fato e arbitrario.**

## 3. Onde o RESUMO era deficiente -- 3 edicoes

Contra o ramo do `revisar.md` secao Fechamento, dois gaps de hoje **nao** eram recall:

- **Mama x endometrio (#1409, invertido 2x).** `[GIN] CA de Mama.md` atribui obesidade pos-menopausa a aromatizacao periferica; `[GIN] CA de Endometrio.md` atribui obesidade a aromatizacao periferica. **Os dois dizem a mesma coisa sobre orgaos diferentes e nenhum dizia como separar.** O erro nao era dele: a materia nao carregava o discriminador. Armadilha escrita **nos dois**, espelhada: *origem PERIFERICA (adiposo, pos-menopausa) -> mama; falha de OPOSICAO no ciclo (anovulacao, SOP, tamoxifeno, TRH sem progestagenio) -> endometrio.*
- **IRIS (#1566, "uma semana" -> "8-12 semanas").** `HIV.md` so carregava a janela de **espera** (2-10 semanas antes de iniciar TARV na neurocriptococose) e **nunca** a de instalacao. Adicionado: **4-8 semanas APOS iniciar**, quase sempre < 3 meses, com a armadilha de conduta (piora precoce lida como falha do esquema).

`auto_check --changed`: **PASSED** (3 arquivos, 1 WARN nao-bloqueante).

## 4. Re-drill de fechamento -- 26 frentes, sem gravar FSRS

23 de nota 1-2 + as **3 pendentes da s175** (#311, #453, #1539). Os outros 6 dos "12 da s175" cairam na fila de hoje por conta propria (relearning) e foram drillados **a frio**, com sinal FSRS real -- pre-drillar teria esquentado a medicao.

**14 fecharam - 11 seguiram abertos - 1 parcial.** Os 11 abertos viraram os eixos da Revisao Direcionada, conforme o corte da s173 (travou 2x -> sai do loop, vira reonboarding curto).

**Padroes que atravessaram a sessao:**

- **Inversao de direcao** (`feedback_inversao_direcao_marcador`), 2x: #954 (via topica x oral na gestante) e #461 (PTH alto x baixo na adinamica). Ambos fechados no re-drill.
- **Numero vizinho no recall**, 3x: I-PSS (7 -> 20, nunca o 8), DRESS (7 dias x 2-6 semanas), IRIS. Os tres com conceito certo pendurado no degrau errado.
- **Pergunta composta** (`feedback_bug_pergunta_composta`): #583 respondido pela metade **mesmo depois de eu avisar, no mesmo turno, que era composto e pedir as duas metades**. #582 idem, e #566 e #1068 na mesma familia. O aviso explicito nao imunizou.
- **Andar para tras no re-drill**: #721 (5 -> 3 mm) e #1588 (azitromicina -> ceftriaxona, com o enunciado dizendo gonococo NEGATIVO). Sinal de ausencia de ancora, nao de esquecimento.

## 5. Revisao Direcionada -- 8 eixos

1. **Cirurgia Infantil** (5 gaps): AVB/biopsia - apendice > 6 mm com o 5 como distrator plantado - apendicite CAUSA diarreia em 40% dos menores de 5a - HAEC e alarme, nao melhora - volvo de intestino medio (pobreza de gas x multiplos niveis da atresia)
2. **Mama x endometrio** -- com a edicao dos dois resumos
3. **CAD pediatrica** -- edema cerebral (60-90% das mortes), nao potassio; o contraste que fixa: *adulto morre de hipocalemia, crianca morre de edema cerebral*
4. **Os numeros que nao colam** -- I-PSS 8/20 - DRESS 2-6 sem - IRIS 4-8 sem
5. **Uretrite nao gonococica** -- doxi 7d e escolha, azitro 1g e alternativa; e a duracao faz parte da resposta (distratores plantam doxi 30d e azitro 500mg 10d)
6. **Sopro anforico** -- curto, o resumo ja cobria (linha 222)

**Carimbos `review_log`** (Invariante B): ids **151-158**, `kind=directed_review`, temas 253 - 441 - 169 - 459 - 451 - 150 - 457 - 460.
**Notas de aula (F18c):** 441=7 - 169=6 - 459=6 - 451=7 - 150=6 - 457=7 - 460=5 (fonte aula). **Cirurgia Infantil (253) NAO foi sobrescrita** -- nota soberana do usuario = 8.

## 6. Numeros

- **Cards:** 90 revisados, 0 re-record. Fila **nao zerou**: ao drenar os 8 erros frescos, **outros 8 entraram no lugar** (#1598-#1602 Diarreia, #1603/#1604/#1606 Urologia) -- o bucket serve por lote, entao o passivo era maior que os 100 da abertura. Mais os 10 novos deixados de fora.
- **Volume de questoes: 0.** Inalterado em **7126**.
- **Projecao entregue no fechamento** (o operador perguntou pela fila): pico de **64 cards em 12/09** -- sabado do Simulado 10, obra das 16 notas 1 de hoje; 15/09 real e ~55 (26 agendados + ~29 vindos do blackout); depois a curva desaba para 7-16/dia, que **nao e folga, e vacuo**. Pool de **663 nunca introduzidos**: no teto de 60/dia cabem ~460 ate a UERJ, os outros ~200 nao entram -- *a pergunta nao e quantos por dia, e QUAIS 460*, e a ordenacao por prevalencia ENAMED nao serve mais porque o norte e UERJ (MFC de 6,7% -> 20%).
- **Gap estrutural reconfirmado:** cronograma restante = 1.927q; **100% dele leva a 9.053**, ainda **1.347 abaixo** do marco de 10.400. A grade nao fecha a meta nem em execucao perfeita.

## 7. Achados registrados no ledger

**F98** (guarda de blackout do F71 nao ve intervalo curto -- 9 cards de hoje cairam em 13-14/09) - **F99** (nao existe CLI que sirva card por id: o proprio passo 1 do HANDOFF nao era executavel) - **F100** (re-ensino nao fechou o gap -- contra-evidencia direta de um remedio aplicado na s175). Detalhe integral em `AUDITORIA_MEDHUB.md` secao 6v. **Nenhum implementado** -- permit de engenharia consumido, e os tres tocam spec (`record_review`, superficie do `fsrs_queue`, contrato de skill).

## 8. Pendencias abertas por esta sessao

1. **`registrar_sessao_bulk` da lista de Diarreia de 09/09** -- segue sem feitas/acertos (herdada da s175). Os 5 cards de erro fresco de Diarreia na fila confirmam que o bloco foi analisado; o **volume** nunca entrou.
2. **Volume de hoje em 0**, com ritmo-alvo de 64,2 q/dia e ~45 q/dia reais em setembro.
3. **Fila de hoje a noite:** 8 erros frescos + 10 novos com gravacao; os **14 de relearning NAO levam segunda gravacao** (anti-duplo-registro -- ja re-drillados hoje).
4. **Rescope da grade para o formato UERJ** e a decisao de **quais 460 dos 663** -- segunda 14/09, junto com a abertura da frente MFC.
5. **Auto-higiene executada:** `tmp/` esvaziado (7 arquivos de scratch de agosto, todos com 0 referencias fora de `tmp/`); a linha do HANDOFF que os apontava sai junto.
