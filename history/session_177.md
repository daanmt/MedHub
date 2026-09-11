# Session 177 -- Janela 2 da reforma: o Tier 0 fecha, o Tier 1 abre, e quatro fixtures cicatrizam

**Data:** 2026-09-10 (noite/madrugada) - **Ferramenta:** Claude Code (Opus 5, 1M) - **Continuidade:** `session_176.md`

Sessao de **ENGENHARIA**, segunda janela do mesmo dia, orquestrada pelo `/ai-eng` N=78 (regime D71).
**Permit do operador, verbatim: _"Vamos continuar a sessão de engenharia até o final, pois não irei
estudar mais hoje"_** (~22:10, dito ao `/ai-eng`) -- revoga, so para hoje, o *"nada de engenharia;
voltar ao estudo"* com que o `HANDOFF.md` abria.

---

## O que foi entregue (7 itens, 9 commits, **0 spawns de subagente**)

| item | id | commit | o que mudou |
|---|---|---|---|
| 0.5 | **F35** | `fbb6ddb` | reconcile W1 planilha x db **reporta** no boot, com a IDADE da planilha |
| 0.6 | **F89** + **F94** | `a27c375` | vocabulario de area vira **dado unico**; 3 writers fail-loud |
| 0.7 | promotes x3 | `0bb9335` | F71 · F80 no contrato FSRS; F76 no spec do F81; **6 cabecalhos param de mentir** |
| 1.1 | **F79b** | `ca329ff` | deixis sobre contexto vazio = **BLOCK** |
| 1.2 | **F64** + **F95** | `6a00a3c` | regime de divida com **um** contador, e ele esta escrito |
| 1.3 | **F66** | `241d26d` `b39b839` | memoria de fraquezas para de ser orfa por abreviacao |
| 1.4 | **F42** | `de9596f` | editar o espelho da skill deixa de sumir em silencio |

**Suite 503 -> 578.** `auto_check --changed` PASSED em todos. **7 audits vibeflow, todos PASS**
(o 0.7 e docs: razao declarada em vez de audit, conforme o formato de checkpoint).

---

## O fio do dia: **quatro fixtures da ordem nao reproduziam mais**

A janela 1 ja tinha topado com isso uma vez (os fixtures #1568/#1574 no 0.2, que pontuavam no chao
da distribuicao). Na janela 2 aconteceu **quatro vezes**, e o padrao merece nome:

1. **F79b/#367** -- o card do achado foi **reforjado** desde a s169: hoje tem vinheta completa e
   outra pergunta. O defeito que originou o item **ja estava consertado**.
2. **F35** -- o numero `6.288` do Dashboard que o `HANDOFF.md` carregava **nao tem data nem
   comando**. Nao foi adotado: entrou no mecanismo como o primeiro `NAO MEDIDO`.
3. **F66** -- a direcao (d) do achado (*"sanear as 3 entradas duplicadas do vocabulario"*)
   **deixou de existir**: ela pressupunha vocabulario derivado da taxonomia, e o **0.6, tres horas
   antes**, trocou a fonte por `core/areas.json`. **Um item do Tier 0 apagou uma direcao do Tier 1.**
4. **F89** -- o passivo medido (18 linhas / 5 pares) e **maior** que as 7 linhas de 09-09, e inclui
   uma variante acentuada nova (`Clínica Médica`).

🔴 **A regra que sai disso:** *fixture que cicatriza e **dado**, nao motivo de parada* -- desde que a
CLASSE do defeito continue real e o remedio seja **prospectivo**. Nos quatro casos o item seguiu, com
a medicao de hoje no lugar da de ontem e a divergencia escrita. O oposto -- afrouxar a metrica ate o
fixture caber -- foi o que a janela 1 recusou no 0.2.

---

## Tres achados novos, todos **de graca**

- **F94** (no 0.6): `insert_card_base` e `cards_regen_queue` ainda **sequestravam o stdout global**
  no mero `import`. Apareceu porque o teste do F89 derrubou 9 testes que nem tocavam o modulo. O
  `importar_sessoes` **ja tinha consertado o proprio sitio** e o `fsrs_queue` **ja tinha a guarda
  certa** -- os dois irmaos ficaram. Invisiveis porque **nenhum teste os importava**.
- **F95** (no 1.2): o registro de **PORTADORES** do gate `CONTRATO_REVOGADO` era enumerado a mao e
  tinha buraco -- o contrato FSRS estava fora da varredura e carregava um **`PREPARAR` vivo e
  prescritivo**, revogado desde a s170. **E o F90 um nivel acima:** o F90 deu ritual ao registro de
  TERMOS; o de PORTADORES continuou sem.
- **o byte invisivel** (no 1.1): 13 sequencias `\b` saíram de um heredoc como **backspace literal**
  dentro das regex. `sed` e `grep` **nao mostram** o byte, o modulo importava, a suite ficava verde --
  e o predicado **nunca casava nada**. Pegou porque o smoke test manual rodou **o caso positivo**
  antes do commit. *Predicado que nao casa o proprio caso-teste positivo e indistinguivel de
  predicado que nao existe.*

---

## Dois defeitos meus, e o que os pegou

No 1.3 o sink de divida gravava no **caminho de producao**, e a suite (que chama o reconciliador com
store sintetico) sobrescreveu **100 itens reais por 1 `wa_dummy`**. Isolei no `conftest` -- **e nao
bastou**: `tools/test_memory.py` e **script-style, roda por subprocess** e nao ve fixture de pytest.
A correcao que vale nos dois harnesses foi prender o caminho em **`_HISTORY_DIR`**, a costura que o
modulo **ja expunha** e que aquele teste **ja patchava**.

🔴 **O que denunciou as duas vezes nao foi a suite** -- ela ficou verde nas duas -- **foi conferir o
numero do painel depois de rodar a suite.**

---

## Decisao que NAO e de engenharia (esta com o operador)

O **F64** mudou o gatilho do regime de divida de `atrasados` para **`vencidos = atrasados + hoje`**.
Isso muda **politica de estudo**: dias que teriam teto 60 podem ir a 90. A fonte da decisao e a
posicao dele registrada na **s162**, verbatim -- *"card vencido hoje e divida igual a card vencido
ontem"* -- que o ledger ja chamara de *"a mais defensavel"*. O `/ai-eng` mandou **manter** e leva o
efeito a ele. **Hoje e inerte** (0 atrasados + 4 hoje: mesmo veredito nos dois criterios). Reverter =
uma frase no contrato + lapide.

---

## Perguntas novas para o operador (Tier 2)

- 🔴 **`Oncologia`, `Urologia`, `Radiologia`, `Medicina de Emergencia` sao areas?** O F66 mediu:
  entre os 100 WeakAreas que seguem sem area canonica, uma classe inteira e de **especialidade
  legitima que a lista canonica nao tem**. Agora ele tem o numero, e a lista e dele (`core/areas.json`).
- **18 linhas fantasma** (`GO`, `Clinica Medica`, ...) com 39 cards + 33 erros pendurados: os writers
  ja **recusam** criar novas, mas reclassificar as existentes e RODADA 3.

---

## Fronteiras DECLARADAS (nao ler os 7 PASS como cobertura)

- **F35:** a fidelidade do snapshot ao Drive e **nao verificavel** enquanto o F36 nao tiver
  transporte proprio. Valida-se coerencia interna, nunca fidelidade.
- **F89:** o gate e de **vocabulario**, nao de **verdade** -- Apendicite sob `Pediatria` passa em tudo.
- **F79b:** mede **ausencia** de vinheta, nao **suficiencia**; e FP 0 vale para os 1419 cards que
  **existem** -- BLOCK sobre corpus futuro e extrapolacao assumida.
- **F64:** o agravante da sessao que cruza a meia-noite **nao** foi resolvido -- o saldo impresso
  torna a virada *visivel*, mas isso e sintoma legivel, **nao sensor**.
- **F66:** 34% de orfandade **permanece**, e o efeito no **ranking** do boot **nao foi medido** --
  normalizar a area nao recalcula `error_count` sozinho; isso aparece na proxima consolidacao.
- **F42:** o aviso depende de **mtime**, que nao e historico; o banner e a camada que nao depende de
  relogio. E nada **impede** a edicao: o WARN informa, o sync sobrescreve.
- **F95:** a lista de portadores segue **enumerada a mao** -- deriva-la e da familia do (ii') e
  pertence a **1.8**.
