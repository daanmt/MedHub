# Hotfix: suite-mencionada-nao-inscrita

origin: third-party
status: verified

## Symptom

O check `SUITES_ORFAS` (invariante **F43**) existe para garantir que "toda `tools/test_*.py`
citada em >= 1 registro de execucao" -- ou seja, que uma suite que existe **de fato roda**.
Ele valida por **substring sobre um blob**:

```python
blob = "".join(corpus)   # busca por substring: separador e irrelevante
orfas = [nome for nome in suites if nome not in blob]
```
(`tools/utils/state_utils.py:356-357`)

**Caso real, medido na s171 durante o hotfix `clausula-revogada-em-vigor`:**
`tools/test_contrato_revogado.py` foi escrito com 12 testes e **NAO foi inscrito no
`python_files` do `pytest.ini`** (que e allowlist explicita, nao glob). Resultado: **12 testes
escritos, ZERO executados** -- a suite ficou em `395 passed` antes e depois de adicionar 12
testes. So foi percebido porque o numero nao subiu.

E o `SUITES_ORFAS` **passou verde durante todo esse tempo.** Motivo: o nome do arquivo aparecia
dentro do blob -- numa **string de mensagem de WARN** que eu tinha acabado de escrever no
proprio `auto_check.py` (`f"pytest tools/test_contrato_revogado.py -q"`) e num comentario. O
gate se satisfez com uma mencao que o proprio autor do gate novo criou, no mesmo commit.

**Mencionada != inscrita.** Um gate inteiro (`CONTRATO_REVOGADO`, 12 testes) esteve a um
`git commit` de entrar no repo sem nunca ter rodado, com o verificador dizendo que estava tudo
certo.

A fraqueza ja estava REGISTRADA -- anexo dos menores da auditoria s160: *"`suites_orfas` valida
por substring (mencionada != inscrita)"*. Ficou como observacao, sem caso e sem fixture, e o
caso chegou.

## Checkpoint

hypothesis: o predicado do F43 pergunta *"o nome aparece no texto de algum registro?"* quando a
pergunta que importa e *"o nome esta no conjunto que algum executor de fato executa?"*. Os tres
registros TEM estrutura legivel e ela esta sendo jogada fora pelo `"".join(corpus)`:
`pytest.ini` tem o campo `python_files` (lista de padroes que o pytest casa por fnmatch);
`tools/auto_check.py` executa suite via lista de comando `[sys.executable, "tools/test_X.py"]`
(as vezes atribuida a variavel antes do `run_command`); `tools/test_pytest_bridge.py` chama
`_run_suite("test_X.py")`. Ler a estrutura em vez do blob responde a pergunta certa.

falsification_test: se o predicado ja fosse estrutural, uma suite cujo nome aparece SO numa
string de WARN e fora do `python_files` seria acusada. Medido no HEAD `09ce3de`:
`check_suites_orfas()` retornou `None` (nenhuma orfa) com `test_contrato_revogado.py` nessa
exata condicao. Hipotese sobrevive.

blind_spots: (a) o `python_files` do pytest e casado por **fnmatch**, entao a emulacao tem de
usar fnmatch e nao igualdade -- um `test_*.py` no campo cobriria tudo legitimamente; (b) o
predicado nao verifica que o teste PASSA, so que e coletado -- suite verde-decorativa (funcoes
sem assert) e outro eixo, ja tratado pelo comentario do proprio `pytest.ini`; (c) executor novo
que nao seja nenhum dos 3 registros continua invisivel -- alcance declarado.

## Preservation

- O check continua **tolerante**: registro ausente ou ilegivel nao cobre nada e **nunca
  levanta** (convencao de sensor). Um `pytest.ini` corrompido nao pode derrubar o `auto_check`.
- Continua devolvendo `None` quando nao ha orfas (convencao dos demais checks), nao `[]`.
- Nenhuma suite hoje coberta pode virar falso-positivo: `check_suites_orfas()` tem de continuar
  `None` no HEAD apos o fix.
- `auto_check --all` termina com 0 BLOCK e a suite fica em >= 407 passed.

## Eliminated / Evidence

## Root cause

`check_suites_orfas` respondia a pergunta errada. Perguntava *"o nome aparece no TEXTO de algum
registro?"*; a pergunta que o F43 existe para fazer e *"o nome esta no conjunto que algum
executor de fato EXECUTA?"*. O `"".join(corpus)` destruia a estrutura dos tres registros e
transformava qualquer mencao -- comentario, docstring, mensagem de WARN, lista de gatilho -- em
prova de execucao.

🔴 **A falha e auto-infligivel por construcao:** quem escreve um gate novo naturalmente cita o
nome da suite na mensagem de erro do proprio gate. Foi exatamente o que aconteceu -- a mencao
que satisfez o verificador foi escrita pelo autor, no mesmo commit, na string do WARN.

**O erro tinha dois sentidos, nao um.** Alem do falso-NEGATIVO (mencao contando como
inscricao), havia falso-POSITIVO simetrico: `python_files` sao **padroes** casados por fnmatch,
e com `python_files = test_*.py` uma suite realmente coletada seria acusada de orfa, porque o
nome nao e substring do padrao. Os dois erros vem da mesma causa -- ignorar a estrutura.

## Fix

files_changed: `tools/utils/state_utils.py` (unico arquivo de CODIGO) ·
`tools/test_suites_orfas.py` (regressao, suite ampliada)

Cada registro passa a ser lido pela sua estrutura:
- **`pytest.ini`** -> `_padroes_python_files()` extrai o campo e o casamento e por **fnmatch**,
  que e como o pytest decide. Corrige o falso-positivo do glob.
- **`tools/auto_check.py`** e **`tools/test_pytest_bridge.py`** -> `_suites_executadas()` faz
  `ast.parse` e recolhe nomes `test_*.py` passados como argumento a um **verbo de execucao**
  (`run_command`, `_run_suite`, `_roda`, `run`, `Popen`, ...). Resolve tambem a lista montada em
  **variavel** antes da chamada (`cmd_tel = [sys.executable, "tools/test_x.py"]; run_command(cmd_tel, ...)`),
  que e o formato real em varios pontos do `auto_check` -- ler so os argumentos literais da
  chamada perderia esses casos.
- Sintaxe quebrada num registro = conjunto vazio, nunca excecao (convencao de sensor preservada).

**Contrafactual verificado, nao afirmado:** `_suites_executadas(auto_check.py)` devolve
`['test_card_self_sufficiency.py', 'test_day_plan_telemetria.py', 'test_fsrs_balance.py']` --
**`test_contrato_revogado.py` NAO esta na lista**, embora apareca no arquivo como texto. Sem a
inscricao no `pytest.ini`, o predicado novo a acusa. O gate teria pego o caso que o motivou.

## DoD

- [x] **Caso real vira fixture e nasceu vermelho:** mencao em string de WARN, em comentario e
      em lista de gatilho -- 3 testes, todos falhando antes do fix, todos verdes depois.
- [x] **fnmatch fiel ao pytest:** `test_python_files_casado_por_fnmatch` era o 4o vermelho
      (falso-positivo do predicado antigo) e passa.
- [x] **Estrutura, inclusive via variavel:** `test_comando_montado_em_variavel_conta_como_inscricao`
      verde; `_suites_executadas` resolve `Assign` de lista literal antes da chamada.
- [x] **Zero falso-positivo:** `check_suites_orfas()` == `None` no HEAD; `pytest tools/ -q` =
      **413 passed**; `auto_check --all` = 0 BLOCK.

## Regression

WHEN uma suite `tools/test_*.py` existe e seu nome aparece nos registros apenas como texto
(comentario, mensagem de WARN, docstring) sem estar no `python_files` nem dentro de uma chamada
de execucao, THEN `check_suites_orfas` a retorna como orfa.

test: `tools/test_suites_orfas.py` (suite ja existente, ampliada)
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **A suite de regressao ja existia e foi AMPLIADA**, nao criada: `tools/test_suites_orfas.py`
  ganhou 6 testes (4 vermelhos + 2 de preservacao). 16 testes no arquivo, 413 na suite.
- **O helper `_repo` da propria suite usava o defeito.** Ele cobria o `test_pytest_bridge.py`
  (que e registro E suite ao mesmo tempo) escrevendo um **comentario com o proprio nome** --
  o que so funcionava porque o predicado era substring. Trocado por inscricao no `pytest.ini`
  do repo sintetico, que e o que o repo real faz. 🔴 O fixture do gate estava se defendendo
  com a mesma brecha que o gate deixava passar.
- **`_strings` filtra para `test_*.py`.** A 1a versao devolvia todo literal da chamada (`'-q'`,
  `'utf-8'`, descricoes) -- inofensivo na intersecao, mas fazia a funcao mentir sobre o que
  devolve e abria colisao acidental. Estreitado ao que ela promete.
- **Alcance declarado, nao pretendido:** o check cobre os TRES registros conhecidos. Um executor
  novo que nao seja nenhum deles continua invisivel -- e o `REGISTROS_DE_SUITE` continua sendo
  mantido a mao. O predicado ficou fiel; o **numero de registros** e outro eixo, nao tocado aqui.
- **Nao verifica que o teste PASSA**, so que e coletado. Suite verde-decorativa (funcoes sem
  assert) e o eixo que o proprio comentario do `pytest.ini` ja trata, e segue fora do escopo.
