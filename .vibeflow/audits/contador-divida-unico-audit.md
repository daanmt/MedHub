# Audit Report: contador-divida-unico (F64 + rider F95, item 1.2)

**Verdict: PASS**

> Spec: **o proprio ledger** (`AUDITORIA_MEDHUB.md` F64, direcoes a/b/c) -- classe *quick*, o mesmo
> tratamento do item 0.4. Sessao **s176 janela 2** (2026-09-10).
> Suite: `python -m pytest tools/ -q` -> **560 passed** (baseline 550; +10 do suite novo).
> Harness: `auto_check --changed` -> **PASSED**, 0 BLOCK.

## DoD (as tres direcoes do achado, cada uma binaria)

- [x] **(a) Decidir e ESCREVER o contador no `fsrs-management-contract`.** v1.2 -> v1.3:
  *"o contador e `vencidos = atrasados + hoje`"*, com a razao que o decide -- **o que define divida
  e a fila nao drenada, nao a data em que ela venceu**. A redacao antiga (`atrasados > TETO_BASE`)
  fica sob **lapide**, nao apagada: os numeros da s162 so se explicam com ela a vista. Changelog
  junto (nao reintroduz o G11).
- [x] **(b) `_teto_efetivo` recebe o contador decidido, com teste.** A assinatura passou a se
  chamar `vencidos` -- nome, nao so valor. `day_plan.vencidos_de(fsrs)` e a **unica**
  implementacao, usada por: gatilho · `divida.vencidos` no `--json` · texto do render · **ordenacao
  dos clusters** (mesmo conceito, outra granularidade -- deixa-la somando a mao recriaria a
  divergencia num lugar onde ninguem iria procura-la). `test_uma_implementacao_so` **varre o
  arquivo** e recusa soma manual nova.
- [x] **(c) O render imprime o consumo do dia.** `usados/teto` + restantes, de `fsrs_revlog` via
  `realizado_do_dia` (a mesma fonte da aderencia -- nao inventa contador). Degrada com
  `_warn_degradacao` se a leitura falhar; o plano do dia nunca cai por causa do saldo.
- [x] **Ritual de revogacao em 3 passos** (`AGENTE.md §10 item 10`): declarar (contrato) ->
  lapidar (a linha morta, no lugar) -> **cadastrar** `atrasados > TETO_BASE` em
  `_TERMOS_REVOGADOS`. `test_termo_revogado_cadastrado_no_gate` trava os tres.
- [x] **Craftsmanship.** 560 passed; `auto_check --changed` PASSED; ASCII limpo; nenhuma escrita
  nova no `ipub.db`; allowlist F49 intacta.

## A fixture e o proprio incidente

`S162 = {atrasados: 45, hoje: 22}`. O teste nao afirma so o valor novo -- ele **reencena a
divergencia**: `vencidos (67) > TETO_BASE` **e** `atrasados (45) <= TETO_BASE`, no mesmo assert.
Depois mede a consequencia: `_teto_efetivo(67) == 90` contra `_teto_efetivo(45) == 60`. E
`test_divida_composta_so_de_HOJE_dispara_o_regime` fixa o caso patologico (`atrasados=0`,
`hoje=80`), em que o criterio antigo **nunca** disparava o regime -- que e justamente quando ele
mais precisaria.

## Rider F95 -- achado ao cumprir o passo (3)

Ao cadastrar o termo, conferi se o contrato FSRS estava na varredura do gate. **Nao estava** -- e
carregava um **`PREPARAR` vivo e prescritivo** (`:72`, *"um PREPARAR aquece o tema e drena o cluster
inteiro"*), revogado na s170 e em vigor num contrato canonico. Classe: **o F90 um nivel acima** --
o F90 deu ritual ao registro de **TERMOS**; o registro de **PORTADORES** continuou manual e sem
ritual, e termo cadastrado nao alcanca arquivo que ninguem mandou varrer (*Reachability-Debt*,
forma *sem perimetro*). Corrigido: lapide na linha + o contrato na lista, com o porque no codigo.

🔬 **Medicao do buraco:** os 7 termos revogados varridos sobre `core/contracts/`,
`.claude/commands/` e `.agents/` fora da lista -> **1 portador real**. Os demais hits sao os
espelhos `.agents/skills/source-command-*/SKILL.md`, **artefato de build gerado dos canonicos ja
vigiados**: inclui-los duplicaria todo achado sem acrescentar alcance, e por isso ficaram fora --
decisao registrada, nao omissao.

## Pattern Compliance

- [x] **Fonte unica** -- a mesma disciplina do 0.6 (`AREAS_VALIDAS`) aplicada a um *conceito* em vez
  de a uma *lista*: o defeito era duas leituras do mesmo nome, nao duas copias de um dado.
- [x] **Degradacao graciosa com WARN** (`_warn_degradacao`) no unico caminho novo que le o banco.
- [x] **Contrato com changelog e frontmatter coerente** (G11 nao reintroduzido).
- [x] **Testes inscritos no `pytest.ini`** com nota de 5 linhas.

## Convention Violations

Nenhuma.

## Critical Gate

Clean — no destructive operations detected. O diff nao contem SQL de escrita, migration,
`DROP`/`DELETE`, exec dinamico nem segredo. As unicas mudancas de comportamento sao: um gatilho que
dispara **mais cedo** (teto sobe, nunca desce) e uma linha a mais no relatorio do boot.

## Fronteiras DECLARADAS (nao ler PASS como cobertura)

1. 🔴 **A mudanca e INERTE no estado de hoje.** Com `atrasados=0` e `hoje=4`, os dois criterios dao
   o mesmo veredito. Isso e **dado, nao atenuante**: o valor do conserto aparece so quando a divida
   acumula -- e o criterio antigo falhava exatamente no caso em que ela e feita de cards de HOJE.
   Quem quiser evidencia de efeito em uso real tera de esperar a proxima divida.
2. **O agravante do achado NAO foi resolvido.** A sessao que cruza a meia-noite continua sem aviso;
   o teto segue por dia de calendario. O saldo impresso torna a virada **visivel** (o numero zera),
   mas isso e sintoma legivel, **nao sensor** -- e a diferenca esta escrita no ledger.
3. **A lista de portadores do gate segue ENUMERADA A MAO.** O F95 tapou o buraco medido; nao deu
   ritual ao registro. Deriva-la e da mesma familia do **(ii') do F90** e pertence a **varredura
   unica (1.8)**. Ate la, o alcance depende de alguem lembrar -- que e o defeito que o proprio F95
   descreve, agora declarado em vez de silencioso.
4. **A politica de estudo mudou de fato.** `vencidos` dispara o regime mais cedo que `atrasados`, o
   que significa teto de ate 90 em dias em que antes seria 60. A base da decisao e a posicao do
   **operador** registrada na s162 (*"card vencido hoje e divida igual a card vencido ontem"*) e a
   recomendacao do ledger -- nao uma escolha de engenharia. Fica **declarado** para que ele possa
   reverter com uma frase, editando o contrato.

---

**Ready to ship.**
