# Spec: Dêixis sobre contexto vazio vira BLOCK (F79b / item 1.1)

> Escrita em 2026-09-10 (s176, janela 2), **abertura do Tier 1**. Ordem: `/ai-eng` N=78, regime D71.
> Ledger: `AUDITORIA_MEDHUB.md` F79b (§6n) · inventário `docs/MEMORIA-AUDITORIA.md §11` linha 1.1.
> Classe *quick*: o remédio já estava escrito no ledger. O que esta spec acrescenta é a **medição**
> que decide WARN × BLOCK -- e ela mudou a resposta.

## Objetivo

Impedir que nasça card cuja pergunta aponta para um antecedente que o card não tem. É o terceiro
defeito consecutivo da família (F79 · F79b · F81) achado por **leitura do usuário** e não por gate.

## Contexto -- três medições, e a terceira reverte a primeira

**1. O gate existia e não cobria o caso para o qual foi criado.** Card **#367** (s169):
`frente_contexto = ''`, pergunta *"Que elementos **do caso** (histórico do paciente e circunstância
do achado) classificam **essa** morte como suspeita?"*. `card_self_sufficiency.py --json` devolveu
**10 achados no banco inteiro e o #367 não estava entre eles** -- o check procurava
auto-suficiência por outros critérios e nunca cruzava **dêixis** com **contexto vazio**.

**2. 🔴 O fixture da ordem NÃO reproduz mais.** Medido hoje: o `#367` foi **reforjado** -- tem
vinheta completa (*"Médico de família com vínculo longitudinal é chamado para atestar o óbito..."*)
e outra pergunta. O achado de 09/09 descrevia um card que já não existe nessa forma. Fixture que
cicatriza é **dado**, não motivo de parada: a classe do defeito continua real e o gate é
prospectivo. O texto original vira **fixture sintético**, com a proveniência escrita.

**3. A regex ingênua encontra a população errada -- de novo.** Três candidatos, medidos sobre os
**1419 cards ativos**:

| candidato | achados | veredito |
|---|---|---|
| amplo (`d[oa]\|n[oa]` + substantivo clínico) | **26** | **todos falsos** -- *"do paciente asmático"*, *"na criança"*, *"no lactente"* são **classe**, não referência a vinheta |
| estreito (DEMONSTRATIVO + substantivo de caso, ou anáfora explícita) | **1** | ainda falso: `#620`, *"confirmação **do caso**"* = caso-índice epidemiológico |
| final (estreito + guarda de caso epidemiológico) | **0** | **passivo 0, falso-positivo 0**; **95 controles** com a mesma dêixis **e** vinheta ficam fora |

## Definition of Done

1. **Predicado único, na biblioteca única.** `checar_deixis_sem_contexto` em `tools/card_checks.py`.
   O `card_self_sufficiency.py` **importa o mesmo predicado** em vez de copiar a regex -- copiar
   criaria a segunda fonte, que é o defeito que o F89 acabou de matar no vocabulário de área.
2. 🔴 **Dispara só na CONJUNÇÃO**, nunca por dêixis sozinha: pergunta com referência a antecedente
   **E** `frente_contexto` abaixo de `CORTE_CONTEXTO_MINIMO`. Teste: o mesmo par de perguntas
   dispara sem vinheta e **não** dispara com ela.
3. **Nasce BLOCK, e a justificativa é a medição, não a vontade.** Entra em `erros` de
   `validar_card`. A política warning-first autoriza BLOCK **quando a base zerar**; a base está
   zerada e medida (**0 / 1419**, FP 0, 95 controles). O corte e a medição ficam **no código**, ao
   lado do predicado -- número sem proveniência é claim que envelhece.
4. **Os falsos-positivos medidos viram fixture negativa.** Classe genérica (5 perguntas vivas do
   banco) e caso-índice epidemiológico (`#620`) **têm teste próprio**: se o predicado alargar, a
   suíte acusa antes do usuário.
5. **Sentinela de população.** Um teste re-mede o passivo no banco real e exige **0**. Se cair, ou
   o predicado alargou ou entrou card defeituoso -- as duas leituras exigem ação, e **nenhuma
   delas é afrouxar o corte** (lição do item 0.2).
6. **Portador de autoria atualizado:** `/estilo-flashcard` ganha o 4º defeito nomeado, marcado
   como o **único BLOCK** da série, com o conserto em uma frase e a distinção dêixis × classe.
7. **Craftsmanship gate:** `auto_check --changed` verde; suíte completa verde (baseline **540**).

## Escopo

`tools/card_checks.py` (predicado + 3 regex + corte) · `tools/card_self_sufficiency.py` (consome o
predicado) · `tools/test_deixis_sem_contexto.py` (novo) + `pytest.ini` ·
`.claude/commands/estilo-flashcard.md` (+ espelho).

## Anti-escopo

- 🔴 **Não normalizar nem reescrever card nenhum.** O passivo é zero; não há o que consertar.
- Não estender o predicado para dêixis **com** vinheta (isso é o eixo C do F81, declarado
  não-verificável por regex).
- Não tocar os 3 anti-padrões antigos do `card_self_sufficiency` -- eles seguem WARN, com o
  passivo de 11 que já têm.

## Ponto cego DECLARADO

O predicado mede **ausência de vinheta**, não **suficiência** dela. Uma vinheta de 20 caracteres
que não carrega o dado que a pergunta pede passa no corte e continua sendo card ruim -- isso é o
eixo A do F81 (contexto redundante/decorativo), medido por outro predicado e ainda assim
incompleto. E o corte de 15 caracteres é **convenção declarada**, não fronteira natural:
a distribuição é **bimodal e medida** -- `frente_contexto` vazio: **468** · entre 1 e 14 chars:
**0** · entre 15 e 29: **5** · >= 30: **946**. Como ninguém vive na faixa 1-14, o valor exato do
corte **nunca foi testado contra dado real**; ele separa "vazio" de "tem alguma coisa", e qualquer
número entre 1 e 15 daria o mesmo resultado hoje.
