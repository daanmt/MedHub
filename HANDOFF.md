# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-26 -- **s128: Hepatologia S13 (41q, 68,3%) + 13 erros persistidos + dreno de 40 cards + F39 (40% do baralho nao-atomico -- detector entregue).***

## > Proximo passo imediato

1. 🎯 **SIMULADO ENAMED de 100 questoes -- HOJE (26/07).** Fecha o debito aberto desde 28/06 e e a **primeira medicao de variancia em condicao de prova** (desvio 11,9 pp = gargalo isolado nº1). Registrar com `--area Simulado`.
2. **3 rituais para levar:** *o que EXCLUI o que eu ia marcar* · *o que esta NORMAL, e o que esse normal proibe* · *quantas perguntas o enunciado embutiu*.
3. Depois: as 2 tasks restantes da S13 -- **Transtornos de Humor + Psiq Social** (D10/extensivo -> aula-base completa antes) e **Arboviroses + Meningites + Sepse** (revisao -> direto a questao).

## 🔬 Diagnostico vigente (`python tools/variancia.py --zona`)

**Zona COBERTURA** -- desempenho alto sobre 43,0% da grade. Prescricao: **AVANCAR a grade**.
🔴 **Variancia 11,9 pp (alta)** -- corre POR FORA da zona, prescreve **simulado** em qualquer quadrante.
📈 **Conta refeita (s128):** o "20,9 q/dia real" mistura dias vazios. Por **dia trabalhado** julho deu **56,9 q/dia** -- ja acima dos ~53/dia da meta a 6 dias/semana. **O gargalo e FREQUENCIA (15 de 26 dias = 58%), nao capacidade.** A 6 dias/sem o marco de 9.454 cai (~9.745). Nao fecha: grade EMED inteira exigiria ~75 q/dia trabalhado -> ~76% de cobertura ate 25/10. **Fork registrado, nao decidido.**

## Capacidades novas (s128) -- usar

- **`tools/audit_card_atomicity.py`** -- detector de card nao-atomico (`duplo-ask` + `resposta-multifato`), read-only, **check 9 do `auto_check`** (WARN). Triar a worklist por **CRITERIOS DE ACERTO**, nao por regex: card discriminador e falso-positivo conhecido e esta documentado no modulo.
- **`estilo-flashcard.md` §UM CRITERIO DE ACERTO (s128)** -- regua nova, formulada pelo usuario. Card que admite "acertei metade" torna a nota FSRS ininterpretavel. Demanda composta se treina em QUESTAO, nunca em card.
- **`insert_questao.py --errors-file`** -- lote transacional de erros (usado p/ os 13 de Hepato). 🔴 **`--habilidades` alimenta o ledger; `--elo` NAO** (errei isso e tive de reparar).

## 🔄 Politica de cards MUDOU (s128) -- de teto para PISO

**>= 30 cards/dia**, definido pelo usuario. Deixou de ser limite de protecao e virou **compromisso de vazao**. Razao dele, e ela corrige um erro meu: a atomizacao **baixa a carga cognitiva por card**, entao o custo de uma sessao e **tempo, nao contagem** -- eu havia alarmado sobre o pool subir de 383 p/ ~500 medindo em unidades. 🔴 **Nao tratar crescimento de pool como custo automatico**: perguntar o tempo real por card antes de alarmar. Estado: base ativa 787 = 283 introduzidos + **504 no pool**. A 30 novos/dia o pool zera em ~17 dias (11/08).

## ⚖️ Load balancing do FSRS (s128) -- NOVO, pedido do usuario

O agendamento agora **olha o calendario**. Dentro da folga do intervalo (+-5%, piso 1d / teto 10d), escolhe o dia de MENOR carga -- achata o pico sem tocar em `stability`/`difficulty`. So card de revisao com intervalo >= 4d; nunca no passado; empate fica no dia do FSRS. Norma em `AGENTE.md §6`; regra pura em `app/utils/fsrs_balance.py`; aplicado em `db.record_review`. **Ver o efeito: `python tools/fsrs_load.py`** (mostra a distribuicao + o **CV**, que e a metrica a derrubar). Estado inicial medido: **pico 48 no dia 27/07 contra media 9,2 -- CV 1,13**. O balanceamento so age em revisoes FUTURAS: o grumo ja agendado nao se desfaz sozinho.

## Padroes de erro vivos -- atencao do scrum master

- 🔴 **Padrao-mestre, FACETA NOVA: o discriminador e um exame NORMAL.** 3 instancias limpas na s128 (transaminase normal excluia hepatite; DHL/hemograma normais excluiam hemolise; transaminase normal excluia indicacao de tratar). Ele le "normal" como ausencia de informacao.
- 🔴 **Bug nº1 (numero contra a regua)** -- card 421: "dialise depende do valor?" -> depende de **AEIOU**, nao de numero.
- 🟡 **Pergunta composta -- NAO INFLAR.** Contei 6 ocorrencias na s128; **5 eram defeito de card duplo**, 1 real. O padrao existe, mas so se mede em **questao de prova**.
- 🟢 **Sensor em desenvolvimento:** no card 462 ele verbalizou o discriminador ("essa funcao minima ai e foda") e ainda assim errou. Detecta, mas nao converte em mudanca de resposta -- alvo do proximo ciclo.

## Estado por frente
- **Volume & Metas:** 5295 / 9454 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~45.7q/dia (91d p/ Cronograma EMED (grade completa)). [derivado: day_plan --handoff-block]
- **FSRS:** divida 0 atrasados + 9 p/ hoje -- pool 395 nunca introduzidos (entram <=40/dia). [derivado]
- **Conteudo:** 71 resumos. `Pneumologia Intensiva.md` **ja tinha** a secao 7 de VMNI completa -- a lacuna da s127 era da AULA, nao do resumo.
- **Erros & Cards:** 606 erros (+13) · 908 cards (+47 cunhados, +12 desmembrados, 9 reescritos in-place com FSRS preservado).
- **Posicao cronograma:** conteudo S13 (nominal S17, atraso 4 sem). Drive stale 17d (F36).

## Pendencias ativas
**Worklist de atomicidade: ~350 cards** (227 duplo-ask primeiro -- corrompem a nota; depois os 137 so-paragrafo). Lotes por tema, priorizando quem cai na fila FSRS dos proximos dias; nunca big-bang. Reforja de `TCE.md` + `Sistemas de Informacao em Saude.md`. Ledger `AUDITORIA_MEDHUB.md`: **F39 novo** (atomicidade, PARCIAL), **F38** (erros analisados nao chegam a `questoes_erros` -- delta retroativo de ate 131), **F36 elevado a ALTA** (o MCP entrega o xlsx; o que quebra e a transcricao de 30 KB -- so codigo conserta, `--fetch-drive`), F37, F35, F8.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_128.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
