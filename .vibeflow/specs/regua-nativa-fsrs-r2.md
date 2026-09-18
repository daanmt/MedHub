# Spec: Régua nativa do FSRS (R2 / F112, opção b)

> Escrita em 2026-09-18 (s186), onda 3 da reforma de engenharia. Ordem: `/ai-eng` N=80, regime D71.
> Ledger: `AUDITORIA_MEDHUB.md` F112 (decidido pelo operador em 17/09) · inventário `docs/MEMORIA-AUDITORIA.md §11`.
> Insumo: `core/fsrs_params.json` (R1, `b394f2f`) · baseline `tools/test_fsrs_blackout_curto.py::test_baseline_do_R2_intervalo_por_nota`.
> **Toda medição abaixo foi feita nesta sessão, com o comando registrado.** Número sem comando não entra em spec (D72).

## Objetivo

Trocar a régua de notas do MedHub pela **semântica nativa do FSRS** -- `1 falhou · 2 lembrou com
esforço · 3 lembrou · 4 sem esforço` -- e fazer a troca ser **datável**: cada revisão passa a
carregar sob qual régua foi dada, para que o histórico velho nunca seja relido com o vocabulário
novo. O F112 mediu o defeito; a opção (b) foi decidida; esta spec é a aterrissagem.

## Contexto

A régua antiga (`.claude/commands/revisar.md` passo 4) define a nota por **completude da
resposta**: *"cravou conceito + regra-mestre -> 4; acertou o núcleo, faltou detalhe -> 3; recall
parcial/na zona mas sem o alvo -> 2; errou ou 'não sei' -> 1"*. O motor lê a mesma escala por
**esforço de recuperação**: Again é o único lapso, Hard é *recuperou com esforço*, Easy é *sem
esforço*. As duas réguas coincidem no 1 e divergem em todo o resto -- a nota 2 do MedHub ("sem o
alvo") entra no motor como acerto.

🔴 **O que de fato muda no código é menos do que o nome sugere, e isso precisa estar escrito.** O
adaptador já passa `Rating(rating)` em identidade (`app/utils/fsrs.py:119`) e os rótulos internos
já são nativos (`ROTULOS_RATING = {1: again, 2: hard, 3: good, 4: easy}`, `app/utils/db.py:579`).
A camada deslocada sempre foi a **prosa em português** que instrui quem dá a nota. Portanto a
opção (b) **não** altera o agendamento por si: ela altera (i) o vocabulário nos portadores, (ii)
como o histórico é lido na entrada do Optimizer, (iii) o limiar de relearning do player e (iv),
*se e quando adotados*, os parâmetros. Vender (b) como "o agendamento vai mudar" seria claim falso.

### Medição 1 -- o que a adoção dos parâmetros faria (830 cards reais em Review)

```
python -X utf8 -c "<replay de fsrs_cards state=2 sob Scheduler(default) x Scheduler(remap)>"
# mediana de dias até a próxima revisão, 830 cards com stability > 0

nota   default (hoje)        remap (R1)          delta da mediana
 1     mediana   0 / média   0    mediana  0 / média  0      +0d
 2     mediana  24 / média  29.4  mediana  8 / média  8.2   -16d
 3     mediana  50 / média  65.2  mediana 50 / média 65.2    +0d
 4     mediana  70 / média  87.0  mediana 50 / média 65.2   -20d
```

O F112 em uma linha de comportamento: **o card que você lembrou com esforço volta em 8 dias, não
em 24.** É o ganho real da onda.

### Medição 2 -- 🔴 ACHADO NOVO: dois parâmetros da visão `remap` são default herdado, não ajuste

```
python -X utf8 -c "<diff índice a índice: Scheduler().parameters x visoes.remap.parametros>"
w3   8.295600 == 8.295600   <-- INTOCADO
w16  1.872900 == 1.872900   <-- INTOCADO
# os outros 19 se moveram. Na visão `cru` os dois se movem (w3=8.433273, w16=1.958405).
# core/fsrs_params.json: visoes.remap.distribuicao_notas_efetivas = {"1": 918, "2": 536, "3": 1613}
#                        -- não existe chave "4".
```

`w3` (stability inicial de Easy) e `w16` (bônus de Easy) são **exatamente** os defaults do py-fsrs
na visão `remap`, e o motivo é estrutural: o mapa do R1 manda `4 -> 3`, então a visão `remap` tem
**zero linhas com nota 4** e o otimizador nunca teve gradiente nesses dois eixos. Eles não
convergiram -- eles nunca foram tocados.

Consequência direta para esta spec: **a régua v2 vai começar a emitir nota 4 de verdade** ("sem
esforço"), e adotar um conjunto cujo eixo de Easy nunca foi identificado é pedir ao modelo que
agende um rótulo que ele nunca viu. Classe do achado: *parâmetro sem dado que o identifique é
default com carimbo de medido* -- irmã da métrica auto-confirmante do F113 (s185) e da presença
!= cobertura do `cli_signature_check`. Vai para o ledger como **F114**.

Por isso a adoção de parâmetros sai do escopo desta onda (ver Anti-escopo) e vira condição: só
depois de haver histórico sob a régua v2, que é precisamente o que o versionamento abaixo cria.

## Definition of Done

1. **Portador único da régua.** `core/reguas.py` declara, em um lugar só: `REGUA_ATUAL = 2`, o
   rótulo de cada nota sob v2, e `MAPA_V1_PARA_NATIVO = {1: 1, 2: 1, 3: 2, 4: 3}` com a
   justificativa por nota herdada do R1. `tools/fsrs_optimize.py` **para de hardcodar** o mapa e
   passa a lê-lo de lá (hoje ele vive duplicado no docstring `:36-46` e no dict `:167-177`).
   Binário: `grep -c "2 -> 1" tools/fsrs_optimize.py` não encontra mapa literal fora de citação.
2. **`fsrs_revlog.regua_versao` (INTEGER), ALTER idempotente** no padrão já existente
   (`_ensure_revlog_columns`, `app/utils/db.py:613`). `record_review` grava `REGUA_ATUAL` em toda
   linha nova. **Sem backfill**: histórico fica `NULL`, e `NULL` significa v1 *por declaração no
   schema e no contrato*, nunca por inferência. Mesma doutrina de `card_version`/`selection_reason`
   ("proveniência começa agora").
3. **Remap por LINHA na entrada do Optimizer.** `fsrs_optimize.py` deixa de aplicar o mapa ao
   revlog inteiro: linha com `regua_versao` NULL ou 1 recebe `MAPA_V1_PARA_NATIVO`, linha com 2
   recebe identidade. O `fsrs_revlog` continua **imutável** (`mode=ro`, zero instrução de escrita).
4. **🔒 GATE DE PARIDADE.** Sobre o revlog de hoje (3.067 linhas, 100% v1 por construção), o
   caminho novo por linha reproduz a saída do R1 **parâmetro a parâmetro** (21 floats) e no
   `log_loss` do hold-out. Teste escrito ANTES da mudança; se a paridade quebrar, o refactor
   mudou número que ninguém pediu para mudar.
5. **Adaptador lê `core/fsrs_params.json` com recusa versionada.** `app/utils/fsrs.py` carrega os
   parâmetros quando o arquivo traz `adotado: true` **e** a régua do fit é a régua de escrita;
   qualquer outra combinação cai no default do py-fsrs e **diz por quê** (stderr, uma linha).
   Sem o arquivo, sem `adotado`, ou com régua divergente -> default. `REQUEST_RETENTION` fica
   **0,90** (rider declarado: 0,70/0,80 é a saída mais fraca por construção enquanto não houver
   `review_duration_ms` real). Binário: 4 testes, um por ramo.
6. **Revogação da régua v1 pelos TRÊS passos do F90, no mesmo commit.** (a) declarar no F112 do
   ledger; (b) lápide em `.claude/commands/revisar.md:161` -- o portador que o agente lê no ato --
   com `⚰️` + data + motivo; (c) marcador `<!-- TERMO-REVOGADO: cravou conceito + regra-mestre |
   revisar.md passo 4, R2/F112 -->` em `docs/MEMORIA-AUDITORIA.md`, de onde
   `termos_revogados_do_ledger` deriva o vocabulário do gate `CONTRATO_REVOGADO`.
   Binário: `auto_check` acusa se a frase velha reaparecer em linha ativa.
7. **Tela do player sob o olho do operador.** `core/templates/player.html` recebe os rótulos v2 e
   o limiar de relearning correspondente (ver Fork A). 🔴 **Não pousa sem o operador ver a tela** --
   condição dele, registrada no HANDOFF; é a superfície que ele lê todos os dias.
8. **Suite verde + `auto_check` PASSED + amostra lida a olho.** Lição da s185 como linha de DoD,
   não como boa intenção: invariante sintático serve de *guard*, nunca de prova; antes de reportar,
   ler uma amostra aleatória da saída com o olho. E todo número reportado aqui sai de sensor
   **independente** do remédio.

## Forks para o operador (os dois vão junto com a tela do player)

**Fork A -- limiar de relearning intra-sessão.** `player.html:393` e `:455` recolocam o card na
fila quando `nota < 4`, e a memória `feedback_relearning_intrasessao` fixa "nota <4 volta até sair
4". Isso foi escrito sob a régua v1, onde 4 = *"cravou conceito + regra-mestre"* -- pedir 4 era
pedir domínio. Sob v2, 4 = *"sem esforço"*, um degrau que o FSRS espera que seja **raro**: manter
`< 4` passa a exigir ausência de esforço para o card sair da fila, e o 3 ("lembrou") vira
repetição eterna. Tradução fiel = **`< 3`** (repete enquanto falhou ou custou). Efeito prático:
sessões mais curtas. *Recomendação: `< 3`.*

**Fork B -- adotar ou não os parâmetros agora.** Adotar entrega a Medição 1 (nota 2: 24d -> 8d,
que é o F112 virando comportamento) e arrasta a Medição 2 (o eixo de Easy nunca identificado, com
o efeito colateral de 4 e 3 colapsarem em 50d -- o "sem esforço" deixaria de valer mais que o
"lembrou"). *Recomendação: **não adotar nesta onda.*** Landa-se a régua e o versionamento; assim
que houver histórico v2 com nota 4 real, o R1 roda de novo sobre a visão mista e aí `w3`/`w16`
nascem medidos. O custo de esperar é adiar os -16d do nota 2; o custo de não esperar é agendar
Easy com parâmetro que nunca viu um Easy.

## Escopo

- `core/reguas.py` (novo) · `app/utils/fsrs.py` · `app/utils/db.py` (`_ensure_revlog_columns`,
  `_aplicar_review`) · `tools/fsrs_optimize.py` · `core/templates/player.html` ·
  `.claude/commands/revisar.md` + `python tools/sync_skills.py` no mesmo commit (§10.3) ·
  `core/contracts/revisao-calibrada-contract.md` · `AUDITORIA_MEDHUB.md` (F112, F114) ·
  `docs/MEMORIA-AUDITORIA.md` · testes.
- Migração do banco sob o rito §10.7: `backup_db.py` -> dry-run -> COUNT-ASSERT. `ALTER TABLE ADD
  COLUMN` é aditivo, mas o rito não tem exceção por ser fácil.

## Anti-escopo

- ❌ **Adotar parâmetros** (Fork B; condicionado a histórico v2 -- ver Medição 2).
- ❌ `review_duration_ms` -- rider aberto, espera o player medir de verdade.
- ❌ Mexer na meta de retenção (fica 0,90).
- ❌ Leech próprio (limiar de lapsos -> fila de reforja) -- item 3 do remédio do F112, onda futura.
- ❌ Backfill de `regua_versao` no histórico. `NULL` = v1 é declaração; reescrever 3.067 linhas
  para dizer o que a ausência já diz é escrita sem ganho sobre SSOT.
- ❌ Amend de rating pós-record. O **Invariante C** (janela de override ANTES do record, 1 record
  por card) segue valendo tal como está; o que esta spec garante sobre o F9 é que **nenhum
  segundo escritor nasce** -- a versão da régua viaja na linha para que um rating v1 nunca seja
  relido como v2. ⚠️ *Se a ordem "F9 no mesmo caminho único" quisesse dizer criar um caminho de
  correção pós-gravação, isso é escopo novo e precisa de GO -- uma pergunta, levada ao `/ai-eng`.*

## Riscos

| Risco | Mitigação |
|---|---|
| Régua nova + histórico velho lidos como um só corpus | DoD 2 + 3 (versão por linha) e DoD 4 (paridade) |
| `test_baseline_do_R2_intervalo_por_nota` não muda e alguém lê isso como "R2 não pousou" | O teste **muda de justificativa, não de número**, se o Fork B for "não adotar": sob v2 a relação `4 >= 2*2` deixa de ser o defeito F112 e passa a ser a relação **correta**. A atualização do docstring é parte do DoD 6 |
| Operador segue dando nota pela régua velha por hábito | Os rótulos na tela do player são o portador que ele lê no ato (DoD 7); a prosa do `revisar.md` é a que instrui o agente |
