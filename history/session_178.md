# Session 178 -- Janela 3 da reforma: o Tier 1 fecha, e quatro registros deixam de ser digitados a mao

**Data:** 2026-09-11 (manha) - **Ferramenta:** Claude Code (Opus 5, 1M) - **Continuidade:** `session_177.md`

Sessao de **ENGENHARIA**, terceira janela da reforma, orquestrada pelo `/ai-eng` (regime D71).
**Permit do operador, verbatim: _"Vamos continuar a sessão de engenharia até o final, pois não irei
estudar mais hoje"_** (2026-09-10 ~22:10), reafirmado na virada (~23:55: _"pronto. já dei clear
nele. continue."_). Fila **selada** pelo `/ai-eng`, sem re-derivacao: 1.5 -> 1.9.

---

## O que foi entregue (5 itens, 5 commits, **0 spawns de subagente**)

| # | item | commit | o que mudou |
|---|---|---|---|
| 1.5 | **F7** morto por medicao | `b6cf807` | heuristica de competidor deletada; achados migrados para a fila de reforja |
| 1.6 | **F39** fila mecanica | `ca5e333` | `reforja.py --ingerir`; 270 cards viram estado com lifecycle |
| 1.7 | **D5** assinatura de CLI | `5b1a5c5` | sensor novo **BLOCK**; `/engenharia-cli` nasce; 65 flags orfas -> 0 |
| 1.8 | varredura unica | `84d604e` | G5/G10/G14 viram CHECK; portadores e termos viram DERIVACAO |
| 1.9c | convencao de trace | `270ac57` | `reproduction` mede o fixture, `status` mede o fix |

**Suite 578 -> 621.** `auto_check --all` PASSED em todos. 5 audits vibeflow PASS.

---

## O fio da janela: **quatro registros que ninguem conseguia manter a mao**

Os cinco itens pareciam independentes na fila. Na execucao, quatro deles eram a mesma doenca em
camadas diferentes -- **um registro mantido por memoria humana**:

1. **O lexico do F7** dependia de curadoria continua de alguem. Ficou **68 dias** com os 2 termos
   da calibracao inicial, cobrindo 0,5% do baralho. Nao foi desleixo: ninguem consegue alimentar a
   mao um vocabulario clinico inteiro.
2. **A worklist de atomicidade** reimprimia 270 cards ha **47 dias** (202 repeticoes do mesmo card
   no ledger-of-self) porque **olhar nao tinha onde ser gravado** -- WARN nao distingue "nao triado"
   de "triado, e e falso-positivo".
3. **A regra §7.2** ("assinatura canonica em UMA skill") existia em prosa. Medida: **65 de 168
   flags** (39%) em skill nenhuma, **17 CLIs** sem dona -- inclusive o reescritor in-place do
   baralho e um CLI declaradamente destrutivo.
4. **As listas do gate de revogacao** (termos e portadores) eram digitadas. O comentario do proprio
   codigo prometia *"ninguem enumera a mao"* e enumerava logo abaixo.

O remedio foi o mesmo nos quatro: **parar de manter** -- matar, mecanizar ou derivar.

---

## Tres achados de graca (a serie continua)

- **F96** -- o isolamento do 1.3, de ontem, cobriu o caminho de SUCESSO do sink de vocabulario e
  deixou o de FALHA escrevendo no `history/memory_errors.log` de **producao**: 14 linhas em 12h, uma
  por rodada da suite. O painel conta as linhas desse arquivo -- **a suite inflava o numero que o
  operador le**. Achado no stderr do proprio `auto_check`, fechando o 1.5.
- **F97** -- `day_plan.py` montava o passo do dia com *"..., **PREPARAR** descomprimido+mecanismo;
  depois DRENAR"*: mecanismo **revogado na s170**, na ordem que a s170 **inverteu**, na string que o
  agente le no **1o turno de toda sessao**. Sobreviveu 6 dias a uma revogacao com lapide, contrato
  v1.3 e termo cadastrado -- porque `_PORTADORES_NORMA` **so tinha markdown**. Achado lendo `--help`
  para escrever as assinaturas do 1.7.
- **O sensor que se acusou** -- a 1a versao do `cli_signature_check` usava regex sobre o fonte,
  casou o `add_argument("--x")` escrito na **propria docstring** e reportou uma flag inexistente.
  Trocado para AST; o caso virou teste.

**Padrao dos tres:** nenhum veio de ler codigo procurando defeito. Vieram de **usar** o sistema --
ler o stderr depois da suite, ler o `--help` para documentar, rodar o sensor sobre si mesmo.

---

## Precisao medida, nao suposta (as tres vezes que a 1a versao errou)

Esta janela produziu tres sensores, e **os tres nasceram errados**. O que os consertou foi rodar
sobre o corpus real antes de aceitar o numero:

| sensor | 1a versao | o que a medicao mostrou | regra que sobrou |
|---|---|---|---|
| F7 (herdado) | WARN experimental | 2 disparos, **1 falso** -- o #913 discrimina por IDADE, nao por fluxo | matar: a classe e semantica, o proxy erra metade |
| G14 status | toda mencao a `**F<id>**` | **2 achados, os 2 falsos** -- lapide cita F-id vizinho | linha de inventario riscada + sujeito = 1o F-id apos `FEITO`; `PARCIAL` nao conta |
| G10 paths | todo path inexistente | **3 de 5 falsos**, todos no `ROADMAP` | linha que AFIRMA a ausencia e lapide, nao ponteiro morto |

O `PARCIAL` do G14 merece nota: e o **meio-termo declarado** (F16, F39 -- mecanismo fechado,
divida de conteudo aberta). Trata-lo como contradicao seria **punir quem escreveu honestamente**
que a coisa esta pela metade.

---

## Decisoes que NAO sao de engenharia (ficam com o operador)

- **G1/G8 -- rotacao do ledger.** `docs/MEMORIA-AUDITORIA.md` **e** o indice que o boot le, e a
  rotacao do `AUDITORIA_MEDHUB.md` (251 KB) e o **F62**. Engenharia nao apaga registro de auditoria
  por conta propria.
- **F57 -- 72 memorias com ponteiro.** O proprio §11 manda ser *"lote por sessao de ESTUDO, nao de
  engenharia"*.
- **A fila de reforja saltou de 2 para 272 abertas.** E o numero honesto (o WARN ja dizia 270), mas
  e uma mudanca grande num numero que o operador le -- declarada, nao escondida no commit.
- **Politica F64** (teto pode ir a 90 em dia que seria 60) segue mantida, como a janela 2 deixou.

---

## Fronteiras DECLARADAS (nao ler os PASS como cobertura)

- **G10 isenta por LINHA:** uma linha com path morto **e** frase de ausencia escapa inteira -- foi
  exatamente o caso do `ESTADO.md`, corrigido na fonte, mas a classe permanece possivel.
- **G5 e sensivel a qualquer arquivo novo:** a tabela §7.4 se re-gera **por ultimo**, antes do
  commit. Disparou 3x nesta sessao, uma por arquivo criado.
- **G14 ve rotulo, nao verdade:** achado fechado erroneamente nos dois registros passa nos dois.
- **`cli_signature_check` mede presenca, nao semantica**, e flag generica pode colar em skill
  vizinha -- o vies **infla** a cobertura, nunca acusa injustamente. *"Flag em duas skills"* **nao**
  e reportada: o unico sinal e co-ocorrencia, e converter isso em achado seria metrica inventada.
- **O gate de revogacao casa substring literal** e a isencao por SECAO nao existe em `.py` (cai para
  heuristica de linha) -- ampliar para bloco de comentario e trabalho futuro.
- **A precisao do detector de atomicidade nao foi re-medida:** os 270 herdam a calibracao da s128 e
  a classe de falso-positivo declarada (card discriminador).

---

## Custo

**0 spawns de subagente** nas tres janelas da reforma. Nenhum item exigiu delegacao: a regua do
§1.1 (F93) manda o principal decidir sozinho ate ~8 itens, e a varredura maior desta janela (24
CLIs) foi resolvida por um sensor de 200 linhas, nao por leitura em paralelo.
