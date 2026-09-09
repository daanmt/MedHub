## Audit Report: suite-mencionada-nao-inscrita (hotfix F86, s171)

**Verdict: PASS**

Alvo: `.vibeflow/hotfixes/2026-09-08-suite-mencionada-nao-inscrita.md`.
Auditor: a janela do MedHub, pelo loop do vibeflow (`AGENTE.md §10.6`, divisão revista na s171).

### DoD Checklist

- [x] **O caso real virou fixture e nasceu vermelho.** 3 testes cobrem as três formas de menção
      que o predicado antigo aceitava — string de WARN, comentário, lista de gatilho
      (`tools/test_suites_orfas.py`, seção "Mencionada != inscrita"). Os três falhavam antes do
      fix e passam depois.
- [x] **fnmatch fiel ao pytest.** `test_python_files_casado_por_fnmatch` era o 4º vermelho — e
      expõe um erro no sentido oposto: com `python_files = test_*.py`, o predicado por substring
      acusava de órfã uma suíte que o pytest coleta de verdade.
- [x] **Estrutura, inclusive via variável.** `_suites_executadas` resolve `Assign` de lista
      literal antes da chamada, que é o formato real de `cmd_tel`/`cmd_css_test` no `auto_check`.
      Ler só os argumentos literais da chamada perderia esses casos.
- [x] **Zero falso-positivo no repo.** `check_suites_orfas()` == `None` no HEAD;
      `pytest tools/ -q` = **413 passed**; `auto_check --all` = **BLOCK_TOTAL=0**.

### Contrafactual (a prova que importa)

Um hotfix de gate tem de responder *"ele teria pego o caso?"*, e isso não sai de fixture
sintética. Medido no código real:

```
_suites_executadas('tools/auto_check.py')
  -> ['test_card_self_sufficiency.py', 'test_day_plan_telemetria.py', 'test_fsrs_balance.py']
```

`test_contrato_revogado.py` **não está na lista**, embora apareça no arquivo como texto (comentário
+ string de WARN). Sem a inscrição no `pytest.ini`, o predicado novo o acusa. **O gate teria
pego o caso que o motivou.**

### Pattern Compliance

- [x] **Sensor tolerante** (`conventions.md §Sensors`): registro ausente **ou com sintaxe
      quebrada** deixa de cobrir e nunca levanta. Provado por
      `test_registro_ilegivel_nao_levanta_e_nao_cobre` — um `auto_check.py` que não parseia
      devolve conjunto vazio, não exceção.
- [x] **Convenção de retorno preservada:** `None` quando não há órfãs, nunca `[]` — igual aos
      checks irmãos. `test_sem_suite_nenhuma_e_silencioso` e os defensivos continuam verdes.
- [x] **"Falso positivo é como um sensor vira ignorado."** O fix corrige um falso-positivo real
      (o do glob) além do falso-negativo. O check ficou mais estrito **e** menos barulhento.
- [x] **Função pura, injetável por `root`** — as 15 fixtures rodam em `tmp_path` sem tocar o repo.

### Convention Violations

Nenhuma.

### Critical Gate

- ✅ **ALLOWED [SEC108]** `tools/utils/state_utils.py` — `"check_output"`, `"Popen"` — override:
  são **nomes a reconhecer via AST**, comparados contra `ast.Call.func`; nada aqui executa nada.
  Declarado in-loco com `vibeflow:allow SEC108` e a razão.

Fora isso, **clean**. Diff: 4 arquivos versionados +192/−10, mais o trace doc. Zero SQL, IaC,
k8s, segredo, exclusão em massa; nenhuma proteção removida (varredura sobre linhas `-`:
SEC101-103, SEC107, DAT103, DAT105 → sem correspondência).

### Achados (nenhum bloqueante)

- 🔴 **[ALTA, confiança máxima] O fixture do próprio gate se defendia com a brecha do gate.**
  O helper `_repo` cobria `test_pytest_bridge.py` — que é registro **e** suíte ao mesmo tempo —
  escrevendo um **comentário com o próprio nome** no arquivo. Só funcionava porque o predicado
  era substring. Trocado por inscrição no `pytest.ini` do repo sintético, que é o que o repo
  real faz. Vale registrar como padrão: *quando um gate é fraco, os testes dele tendem a herdar
  a fraqueza como conveniência* — e passam a documentá-la em vez de acusá-la.
- 🟡 **[MÉDIA, confiança alta] `_strings` devolvia todo literal da chamada** (`'-q'`, `'utf-8'`,
  descrições humanas) na 1ª versão. Inofensivo na interseção, mas fazia a função mentir sobre o
  que devolve e abria colisão acidental com um nome de arquivo. Estreitado a `test_*.py`.
- 🔵 **[INFO] Alcance declarado, não pretendido.** O check cobre os **3 registros conhecidos**, e
  `REGISTROS_DE_SUITE` continua mantido à mão. Executor novo que não seja nenhum dos três segue
  invisível. O predicado ficou fiel; **o número de registros é outro eixo**, e não foi tocado —
  declarado, não fingido.
- 🔵 **[INFO] Não verifica que o teste PASSA**, só que é coletado. Suíte verde-decorativa
  (funções que imprimem sem assert) é o eixo que o próprio comentário do `pytest.ini` já trata,
  e segue fora do escopo.
- 🔵 **[INFO] Custo.** `ast.parse` de 2 arquivos por execução do check. `auto_check --all`
  continua no mesmo patamar; nenhum impacto mensurável.

### Nota de série

F86 entra na série gate-miss (`AGENTE.md §10.8`) na classe **tooling** — distinta da classe
**conteúdo** (F79/F79b/F81). Decisão do `/ai-eng` nesta sessão: o registro de gate-miss carrega
o campo `classe` e o contador conta **por classe**; misturar as duas mata o número. F86 é a 1ª
fixture da classe tooling.

### Próximo passo

**Ready to ship.** Commitar fix + testes + trace doc + F86 como uma unidade.

---
*5 hotfix docs ainda não consolidados em `.vibeflow/hotfixes/` — rodar `audit --consolidate-hotfixes`.*
