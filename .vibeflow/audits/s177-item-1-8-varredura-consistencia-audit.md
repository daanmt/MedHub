# Audit Report: s177 item 1.8 -- varredura única de consistência (G5 · G10 · G14 · G11 · G3 · G6 · D11 · (ii') · portadores)

**Data:** 2026-09-11 · **HEAD base:** `5b1a5c5` · **Escopo:** item 1.8 da fila selada (janela 3)

**Veredito: PASS**

> **Razao declarada para o formato:** item de fila de divida tecnica, sem spec em `.vibeflow/specs/`.
> O DoD e a lista que o `/ai-eng` selou -- *"G5 · G6 · G10 · G11 · G3 · G1/G8 · D11 · (ii') termos
> derivados · G14 cabeçalho×lápide · derivar `_PORTADORES_NORMA` -- cada um vira CHECK de ALCANCE
> no `auto_check`, 'alguém chega aqui?', não presença de string"*.

## DoD Checklist -- um por item da lista selada

- [x] **G5 -- tabela gerada stale.** `consistencia_check --check tabela` re-gera por
  `reachability_check --tabela` e compara **linha a linha**, não só a contagem: CLI que troca de
  referenciador muda a 3ª coluna sem mudar o número de linhas, que foi como a tabela envelheceu sem
  ninguém ver. 🔬 **O check se provou sozinho:** disparou **três vezes** nesta sessão, uma a cada
  arquivo novo criado no próprio item.
- [x] **G6 -- ponteiro de sessão meio-cego.** ⚰️ **Já estava coberto.** `check_session_pointer`
  trata `alem_do_max` **e** `arquivo_ausente`, o segundo com BLOCK e mensagem própria. O achado
  descrevia um gate que deixou de existir entre a medição do G6 e hoje. **Fixture-aging, não
  trabalho** -- e a linha só continuava aberta porque ninguém re-mediu.
- [x] **G10 -- ponteiro morto fora de `memory/`.** `--check paths` varre os 5 docs de raiz.
  O `ESTADO.md` de fato citava `tools/autopsia_template.py`, deletado na s156 (F57) -- recebeu
  lápide. 🔴 **Regra de precisão MEDIDA:** linha que afirma a ausência é lápide, não ponteiro morto
  (convenção do `.vibeflow/conventions.md`); sem a isenção, 3 dos 5 achados iniciais eram falsos, todos
  no `ROADMAP.md`, que é histórico.
- [x] **G11 -- frontmatter × corpo.** Fechado **sem check novo**: o predicado P2 do
  `check_contrato_revogado` já comparava, e só não via os contratos porque a lista de portadores era
  digitada. Derivada a lista, as 3 divergências apareceram (`cronograma` fm 1.2 × corpo 1.0;
  `evidence-governance` fm 1.0 × corpo 1.1; `orquestracao` sem campo) e foram corrigidas.
- [x] **G3 -- cabeçalho do F75 × tabela.** Fechado, e **não com outro número fixo**: o cabeçalho
  passou a declarar a **data da contagem** (12/12 em 11/09/2026) e a redação congelada da s166 virou
  lápide. A tabela andou (D4/D3 depois da s166, **D5 no 1.7**, **D11 neste item**) enquanto o
  cabeçalho ficou parado -- a definição de claim-aging.
- [x] **G1/G8 -- NÃO fechados, e declarado por quê.** G1 não é defeito de gate: `MEMORIA-AUDITORIA`
  **é** o índice que o boot lê, e a rotação do ledger é **F62, decisão do operador** -- engenharia
  não apaga registro de auditoria por conta própria. G8 é disciplina de escrita, exercida em três
  lugares neste item (cabeçalho do F75, painel, o próprio KB do ledger). O que **virou mecanismo**
  é a parte verificável: G3/G5/G14.
- [x] **D11 -- falso conforto do sensor verde.** O `--help` do `doc_drift.py` passou a declarar o
  escopo, **nomear quem cobre o resto hoje** (D5 -> `cli_signature_check` BLOCK; G5/G10/G14 ->
  `consistencia_check`; cláusula revogada -> `check_contrato_revogado`) e **o que segue sem sensor**:
  prosa que descreve mecanismo extinto sem citar path nem termo cadastrado.
- [x] **(ii') -- termos derivados do ledger.** Nova **§12** do inventário com marcadores
  `<!-- TERMO-REVOGADO: termo | onde -->`, lidos por `termos_revogados_do_ledger()`. O dict do
  `auto_check` virou **semente**. Um check acusa termo que exista só no código (o modo de falha que
  o (ii') existe para impedir) e um teste trava os dois lados.
- [x] **G14 -- status do ledger × lápide do §11.** `--check status`. 🔴 **A 1ª versão devolveu 2
  achados e os 2 eram falsos** -- lápide cita F-id vizinho o tempo todo. Regras que sobraram, cada
  uma com fixture: linha de inventário **riscada**, sujeito = 1º F-id **depois** do `FEITO`, e
  `PARCIAL` **não** conta (é o meio-termo declarado de F16/F39 -- puni-lo seria punir a honestidade).
- [x] **Derivar `_PORTADORES_NORMA` (F95).** `portadores_derivados()`: todo contrato, toda skill,
  os 5 docs de raiz, os 2 portadores de **código** do F97. 🔬 **Medido antes de trocar:** manual =
  10 portadores / 0 achados; derivada = **29 / 3 achados reais** -- entre eles um `PREPARAR` vivo e
  prescritivo no `README.md`, portador que ninguém havia cadastrado: o F95 acontecendo de novo, e a
  derivação pegando-o no ato.
- [x] **Tudo verde.** `pytest -q` -> **621 passed** (605 -> 621). `auto_check --all` -> **PASSED**,
  com os dois checks novos (`Consistencia entre registros`, `Registro de termo revogado derivado`).

## Pattern Compliance

- [x] **CHECK de alcance, não de string** (a instrução do `/ai-eng`): os três sub-checks perguntam
  *"este registro ainda diz a verdade?"*, e os dois derivadores perguntam *"alguém chega aqui?"*.
- [x] **WARN-first:** os checks novos nascem WARN (nenhum quebra código); o único BLOCK da sessão
  (D5, item 1.7) nasceu assim por medição de base zerada.
- [x] **Fallback declarado:** derivação que falha degrada para a semente, **nunca** esvazia o gate --
  com teste próprio. *Gate vazio passa por estar vazio*, que é pior que enumerar à mão.
- [x] **Assinatura uniforme de sensor** (`run_checks(root=None) -> [{'alvo','payload'}]`) e registro
  no `_ledger_record`, como `doc_drift` e `reachability_check`.
- [x] **Tabela gerada não se edita à mão:** regenerada pelo comando que a gera, como manda a §7.4.
- [x] **§7.2:** o CLI novo entrou em `engenharia-cli.md` **porque o gate do 1.7 bloqueou o commit**
  até que entrasse -- o gate da sessão anterior cobrando a desta.

## Convention Violations

Nenhuma.

## Critical Gate

Clean. Nenhuma escrita em banco, schema ou credencial; o item é sensores + documentação + 3
correções de metadado de contrato + 2 lápides em docs.

## Limites DECLARADOS (não maquiados)

1. **G10 isenta por LINHA.** Uma linha que cite um path morto **e** uma frase de ausência escapa
   inteira -- foi exatamente o caso do `ESTADO.md` (o `autopsia_template.py` vivia na mesma linha do
   *"equivalente ainda não existe"*). Corrigido na fonte, mas a classe permanece possível.
2. **G5 é sensível a qualquer arquivo novo.** Criar um CLI ou uma suíte muda os referenciadores e
   deixa a tabela stale -- por isso ela se regenera **por último**, antes do commit. É ruído
   legítimo: exatamente o envelhecimento que o check existe para expor.
3. **G14 vê rótulo, não verdade.** Ele compara `ABERTO` × `⚰️ FEITO`; não julga se o item está de
   fato feito. Um achado fechado erroneamente nos dois registros passa nos dois.
4. **O gate de revogação casa substring literal** -- limite herdado do F90, agora escrito também na
   §12 do inventário, ao lado dos marcadores.
5. **G1/G8 seguem abertos por decisão, não por esquecimento** (ver DoD acima).

---

12 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
