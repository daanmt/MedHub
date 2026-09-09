# Hotfix: clausula-revogada-em-vigor

origin: third-party
status: verified

## Symptom

O contrato `core/contracts/revisao-calibrada-contract.md` foi promovido a **v1.3** na s170.
A **Clausula 11** (`:146`) declara literalmente: *"A preparacao pre-drill (`PREPARAR`, que ja
havia absorvido o `/refrescar` e a Camada 0) e a expansao por-card na virada (Camada 1)
**deixam de existir**"*.

O texto revogado **nao foi removido nem lapidado**. `grep -nE 'PREPARAR|Camada 0|Camada 1'`
no contrato retorna 22 linhas; descontando as que carregam lapide (`:74`, `:174`), o cabecalho
de versao (`:10`) e o corpo da propria Clausula 11 (`:146-165`), restam **12 linhas ATIVAS**
que continuam prescrevendo o mecanismo morto:

| linha | o que prescreve (revogado) |
|---|---|
| `:54` `:56` `:58` `:60` `:62` | Clausula 4 inteira -- "Fusao em sub-modos (PREPARAR / DRENAR)", a transicao PREPARAR -> DRENAR, a arquitetura por proposito |
| `:66` | **Invariante A** -- "PREPARAR e read-only no FSRS" |
| `:68` | **Invariante B** -- "PREPARAR SEMPRE carimba `review_log`" -- contradiz `:160`, que diz que B migrou para a Revisao Direcionada |
| `:113` | anti-circularidade que governa `infer_nota`: exclui "o acerto morno medido logo apos PREPARAR" -- calibrada contra uma medicao que nao pode mais existir |
| `:129` | item 5 -- "PREPARAR oferece DRENAR" |
| `:130` | item 5b -- "DRENAR **oferece** PREPARAR quando o cluster esta frio", limiar `>=25` |
| `:135` | "render de qualquer aula/PREPARAR calibrado" |
| `:142` | "a nota que calibrou a descompressao e registrada no fechamento da **aula/PREPARAR**" -- governa onde o carimbo de `set_dificuldade` cai |

**A 5b e lida ANTES da Clausula 11.** Um agente que le o contrato de cima para baixo executa a
oferta de PREPARAR e so 16 linhas depois descobre que o PREPARAR nao existe.

**Como o defeito foi contado -- tres medicoes, tres numeros.** Leitura humana (Claude Code):
**1** linha (achou a 5b, passou pela 5 uma linha acima). Enumeracao a partir de grep truncado
em 110 colunas (`/ai-eng`): **10** linhas (o token `PREPARAR` de `:113` e `:142` caiu fora do
corte). Grep sem truncar: **12**. Nenhum dos dois metodos e confiavel -- e por isso que a
regressao deste hotfix e um lint, e a contagem do "antes" sai dele.

**Superficie maior que o contrato.** O agente que executa `/revisar` le o **command**, nao o
contrato. Medido: `.claude/commands/revisar.md` 11 linhas brutas (8 fora de lapide),
`.claude/commands/refrescar.md` 2 (1), `AGENTE.md` 3. Se sobrar UMA prescricao ativa nos
portadores executaveis, a lapide no contrato e decorativa.

**Segundo defeito, mesmo arquivo, mesma classe (G11):** frontmatter `version: 1.0` (`:5`) x
cabecalho do corpo `**Versao 1.3**` (`:10`). O contrato mente sobre a propria versao.

## Checkpoint

hypothesis: nao ha gate nenhum que confronte texto normativo ATIVO contra revogacao declarada
no mesmo documento. `doc_drift` mede doc-vs-CODIGO (referencia morta a arquivo/simbolo); o eixo
doc-vs-DECISAO -- "esta clausula ainda vale?" -- nao tem sensor. Por isso a revogacao da s170
fechou o texto que a declara (Clausula 11) e deixou intacto o texto que ela revoga.

falsification_test: se existisse cobertura, algum check do `auto_check --all` teria acusado
apos o commit da v1.3. Rodei `auto_check --all` no HEAD `09ce3de`: **0 BLOCK**, e nenhum dos 22
checks menciona clausula revogada. Hipotese sobrevive.

blind_spots: (a) o lint julga por TERMO em registro explicito, entao clausula revogada cujo
nome nao esteja no registro passa -- alcance declarado, nao pretendido; (b) nao verifica se a
reescrita esta clinicamente/pedagogicamente correta, so que o termo morto nao prescreve; (c) o
eixo semantico (clausula que contradiz outra sem usar o termo) fica **declarado nao-verificado**,
mesma disciplina do eixo C do F81.

## Preservation

- A `/aula-base` NAO e afetada: e pre-QUESTOES, nao pre-cards, e a Clausula 11 a preserva
  explicitamente. Nenhuma linha sobre `/aula-base` pode mudar de sentido.
- Lapides ja existentes (`:74` Invariante D, `:174`, e os blocos de lapide dos commands) sao
  **evidencia historica**: o texto nao se altera, e o lint tem de continuar isentando-os.
- `auto_check --all` termina com **0 BLOCK** e a suite fica em **>= 395 passed**.
- `infer_nota` NAO e recalibrado aqui (spec separada, decisao ja tomada com o `/ai-eng`).

## Eliminated / Evidence

## Root cause

**Nao existe gate que confronte texto normativo ATIVO contra revogacao declarada no mesmo
documento.** O `doc_drift` mede doc-vs-CODIGO (referencia morta a arquivo/simbolo). O eixo
doc-vs-DECISAO -- *"esta clausula ainda vale?"* -- nao tinha sensor nenhum. Por isso a s170
conseguiu escrever a Clausula 11 (que declara a revogacao) e deixar intacto todo o texto que
ela revoga: os dois vivem no mesmo arquivo, e nada os confronta.

Corolario que o proprio hotfix demonstrou: **a superficie do defeito e maior que o documento
que declara a revogacao.** O agente que executa `/revisar` le o command, nao o contrato --
e `AGENTE.md:164` mandava, em linha viva, *"ver `/revisar` Camada 0"*, um ponteiro para secao
revogada.

## Fix

files_changed: `tools/auto_check.py` (unico arquivo de CODIGO) · `tools/test_contrato_revogado.py`
(regressao) · `pytest.ini` (inscricao) · e os DOCUMENTOS que sao o objeto do defeito:
`core/contracts/revisao-calibrada-contract.md`, `.claude/commands/revisar.md`,
`.claude/commands/refrescar.md`, `AGENTE.md`, `ESTADO.md`

**Gate (`tools/auto_check.py`)** -- `check_contrato_revogado`, dois predicados. P1: termo de um
registro de REVOGADOS (`PREPARAR`, `Camada 0`, `Camada 1`) em linha ativa de um portador da
norma. Isencao **por SECAO**, nao por linha: bloco sob heading de lapide e isento inteiro,
heading irmao/superior fecha a secao. P2: `frontmatter.version` x `**Versao X.Y` do corpo.
Portadores: contrato + 2 commands + `AGENTE.md` + `ESTADO.md` + `HANDOFF.md` (os dois ultimos
sao lidos no boot e custavam 0 achados -- cobertura de graca).

**Severidade -- deliberada.** O **BLOCK real e o teste**, que vive na suite, e a suite e
BLOCKING no pre-commit (check 2d, F44). A linha no `auto_check` e **painel**. Nao e o
"warning-first virou warning-only" do D3/F54: o gate ja morde pelo teste; duplicar o BLOCK
aqui criaria dois donos da mesma regra, que e a doenca que o F43 registra.

**Documentos** -- lapide no padrao de `:74` e reescrita **so onde a Clausula 11 ja mapeia**:
Invariante A -> sujeito vira a Revisao Direcionada (`:171`); Invariante B -> migra para o
fechamento (`:160`); cluster frio/F5 -> entra na fila de prioridade, nao dispara aquecimento;
`aula/PREPARAR` -> `aula`. Onde a Clausula 11 nao mapeia (`:113`, anti-circularidade do
`infer_nota` calibrada contra o "acerto morno" pos-aquecimento), **lapide e ponto** -- o
`infer_nota` NAO foi recalibrado, e spec propria.

## DoD

- [x] Lint **vermelho -> verde**: **18 achados** no HEAD `09ce3de` (12 prescricoes no contrato
      + 5 nos portadores executaveis + 1 de versao) -> **0**. Contagem produzida pelo lint.
- [x] Isencao **por SECAO** provada por 4 fixtures dedicadas (bloco de lapide isento inteiro;
      heading irmao fecha a secao; heading que nomeia o termo morto E achado; termo qualificado
      como "antigo" e isento). 10 fixtures verdes desde a 1a execucao.
- [x] P2 `frontmatter.version` == versao do corpo: vermelho (1.0 x 1.3) -> verde (1.3).
- [x] `pytest tools/ -q` = **407 passed** (395 + os 12 novos); `auto_check --all` = **0 BLOCK**.

## Regression

WHEN um portador da norma do `/revisar` contem linha ativa que prescreve termo revogado
(`PREPARAR`, `Camada 0`, `Camada 1`) fora de lapide, fora de secao de lapide e fora do
cabecalho de versao, THEN `check_contrato_revogado` retorna essa linha como achado; e WHEN o
`version` do frontmatter diverge da versao declarada no corpo THEN retorna o achado de versao.

test: `tools/test_contrato_revogado.py`
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **Dois defeitos no proprio gate, achados pela execucao e nao pela leitura.** (1) A 1a versao
  fazia `continue` em todo heading, entao `## Clausula 4 -- Fusao em sub-modos (PREPARAR /
  DRENAR)` -- o titulo que anuncia o mecanismo morto -- **escapava**. Corrigido, e virou
  fixture. (2) Faltava reconhecer o termo qualificado como "antigo/a" como marcacao legitima
  de morte; sem isso o gate acusava narrativa correta nos commands. Ambos entraram no registro
  porque o lint foi rodado antes de ser acreditado.
- **A contagem do "antes" mudou tres vezes, por tres metodos.** Leitura humana: 1 linha.
  Enumeracao sobre saida de grep truncada em 110 colunas (`/ai-eng`): 10. Grep integral: 12.
  Lint: **18** (as 12 mais 5 nos portadores executaveis mais a de versao). Nenhum humano
  chegou ao numero; e o argumento de existir o gate.
- 🔴 **Gate-miss encontrado durante o proprio hotfix (§10.8).** `tools/test_contrato_revogado.py`
  nasceu **fora do `python_files` do `pytest.ini`** -- 12 testes escritos e ZERO executados no
  run da suite (395 antes, 395 depois). O check `SUITES_ORFAS` (F43), que existe exatamente
  para isso, **passou verde**: ele valida por **substring**, e o nome do arquivo aparecia numa
  string dentro do `auto_check.py` (a mensagem do WARN que eu tinha acabado de escrever).
  *Mencionada != inscrita* -- a fraqueza ja estava registrada no anexo dos menores da s160 e
  agora tem um caso real. Inscrito no `pytest.ini`; a suite foi para **407**. **O F43 vira
  achado proprio da serie gate-miss** (deferido para numeracao, F86 candidato).
- **Orcamento de arquivos:** 1 arquivo de CODIGO (`auto_check.py`), dentro do teto. Os 5
  documentos alterados sao o **objeto** do defeito, nao codigo colateral -- uma revogacao nao
  propagada e distribuida por construcao, e o escopo foi medido pelo lint antes de tocar
  qualquer um.
- **G13 (`ESTADO.md`) entrou no mesmo hotfix**, como acordado -- mesma classe, blast radius zero.
- **Colateral NAO corrigido aqui:** `infer_nota` segue calibrado contra um sinal que nao pode
  mais existir (`:113`). Lapidado, nao consertado -- spec propria, decisao ja tomada.
