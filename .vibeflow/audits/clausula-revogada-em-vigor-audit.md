## Audit Report: clausula-revogada-em-vigor (hotfix G12/G13/G11, s171)

**Verdict: PASS**

Alvo: `.vibeflow/hotfixes/2026-09-08-clausula-revogada-em-vigor.md`.
Auditor: a própria janela do MedHub, pelo loop do vibeflow — divisão revista pelo operador em
08/09 (`AGENTE.md §10.6`): implement **e** audit são daqui; o `/ai-eng` orquestra.

### DoD Checklist

- [x] **Lint vermelho → verde, contagem produzida pela ferramenta.** `check_contrato_revogado()`
      no HEAD `09ce3de` = **18 achados** (12 prescrições no contrato + 5 nos portadores
      executáveis + 1 de versão); depois do fix = **0**. Evidência: as duas execuções estão no
      transcript e o teste `test_repo_sem_clausula_revogada_em_vigor[prescricao|versao]` nasceu
      falhando com a lista literal e hoje passa.
- [x] **Isenção por SEÇÃO, não por linha.** 4 fixtures dedicadas em
      `tools/test_contrato_revogado.py:45,55,63,71`: bloco sob heading de lápide isento inteiro;
      heading irmão fecha a seção (achado volta na linha 9); heading que **nomeia** o termo morto
      É achado; termo qualificado como "antigo" é isento. As 10 fixtures passaram desde a
      primeira execução — só os 2 testes de estado do repo nasceram vermelhos, que é a
      separação correta entre provar o DESENHO e provar o ESTADO.
- [x] **P2 frontmatter × corpo.** `revisao-calibrada-contract.md:5` era `version: 1.0` com o
      corpo declarando `**Versão 1.3**` (`:10`). Hoje `1.3`. Fecha o **G11** testado, não por
      edição solta.
- [x] **Suíte e harness.** `pytest tools/ -q` = **407 passed** em 14,4s (395 + os 12 novos);
      `auto_check --all` = **BLOCK_TOTAL=0**, com a linha `CONTRATO_REVOGADO` no painel.

### Pattern Compliance

- [x] **Sensores são WARN-first e nunca escrevem** (`conventions.md §Sensors`).
      `check_contrato_revogado` é função pura, devolve lista, não edita nada. A linha no
      `auto_check` é painel. Evidência: `tools/auto_check.py:866-880`.
- [x] **"Linha que afirma uma ausência é lápide, não mentira — o scan pula"** — a convenção que
      o `doc_drift` já carrega foi honrada e **estendida por seção**, que é o mesmo princípio
      aplicado ao bloco. Evidência: `_linha_e_lapide` + a lógica de `nivel_lapide`.
- [x] **Régua irmã importada, não copiada.** `RE_LAPIDE` do `doc_drift` entra por import
      (`tools/auto_check.py`, topo do bloco) e a extensão local (`revogad|morte|antigo|⚰`) está
      documentada com o motivo: as duas medem eixos distintos — "isto sumiu?" × "este bloco
      narra uma revogação?". Duas réguas divergindo seria a classe que o F57/F43 registram.
- [x] **Assinatura injetável, no padrão do check irmão.** `check_contrato_revogado(root=,
      portadores=, termos=)` espelha `check_memory_pointers(mem_dir=, root=)` — é o que permite
      as fixtures em `tmp_path` sem tocar o repo real.
- [x] **"Falso-positivo é como um sensor vira ignorado."** Tratado como requisito de desenho, não
      como acaso: a isenção por seção e o marcador "antigo" existem exatamente para isso, e o
      gate nasce com **0** achados.

### Convention Violations

Nenhuma.

### Critical Gate

**Clean — nenhuma operação destrutiva detectada.**

Diff real (`git diff HEAD` + 2 untracked): 9 arquivos versionados, +179/−22, mais
`tools/test_contrato_revogado.py` e o trace doc. Varredura do catálogo sobre linhas
**adicionadas** (DS/SEC/IAC/K8S/CFG/DAT) e sobre linhas **removidas** (SEC101-103, SEC107,
DAT103, DAT105): zero correspondências. Não há SQL, IaC, k8s, segredo, `eval`/`exec`, exclusão
em massa nem remoção de proteção. O único arquivo de código é `tools/auto_check.py`, e a
mudança é aditiva (um check novo + o wiring).

### Achados (nenhum bloqueante)

- 🟡 **[MÉDIA, confiança alta] Gate-miss encontrado durante o próprio hotfix.**
  `tools/test_contrato_revogado.py` nasceu **fora do `python_files` do `pytest.ini`** — 12
  testes escritos e **zero executados** (a suíte ficou em 395 depois de eu adicionar 12 testes;
  foi essa discrepância que denunciou). O check `SUITES_ORFAS` (F43), que existe exatamente
  para isso, **passou verde**: ele valida por **substring**, e o nome do arquivo já aparecia
  numa string dentro do `auto_check.py` — a mensagem do WARN que eu tinha acabado de escrever.
  *Mencionada ≠ inscrita.* A fraqueza estava documentada no anexo dos menores da s160 e agora
  tem caso real e caro (um gate inteiro poderia ter sido mergeado sem nunca rodar).
  **Corrigido nesta rodada** (inscrito; suíte 395 → 407). **A causa permanece aberta** →
  candidato a F86 na série gate-miss (§10.8).
- 🟡 **[BAIXA, confiança alta] Dois defeitos no próprio lint, achados por execução e não por
  leitura.** (1) A 1ª versão fazia `continue` em todo heading, então `## Cláusula 4 — Fusão em
  sub-modos (PREPARAR / DRENAR)` — o título que anuncia o mecanismo morto — escapava.
  (2) Faltava reconhecer "antigo/a" como marcação legítima. Ambos corrigidos e convertidos em
  fixture. Registrado porque é a mesma lição do dia: rodar antes de acreditar.
- 🔵 **[INFO] Dívida deliberada, declarada e não fechada:** `infer_nota` segue calibrado contra
  o "acerto morno medido logo após o aquecimento" — sinal que não pode mais ser produzido
  (`revisao-calibrada-contract.md:113`). **Lapidado, não consertado**, por decisão explícita
  com o `/ai-eng`: recalibrar é spec própria, não hotfix de texto.
- 🔵 **[INFO] Alcance declarado, não pretendido:** o gate julga por **termo em registro
  explícito**. Cláusula revogada cujo termo não esteja em `_TERMOS_REVOGADOS` passa, e o eixo
  semântico (cláusula que contradiz outra sem usar o termo) fica **declarado não-verificado** —
  mesma disciplina do eixo C do F81, e não convertido numa métrica inventada para o painel
  ficar verde.
- 🔵 **[INFO] Severidade escolhida, não herdada.** O BLOCK real é o teste (a suíte é BLOCKING no
  pre-commit, check 2d/F44); a linha no `auto_check` é painel. Não é o "warning-first virou
  warning-only" do D3/F54 — o gate morde pelo teste, e duplicar o BLOCK criaria dois donos da
  mesma regra.
- 🔵 **[INFO] Orçamento de arquivos.** 1 arquivo de CÓDIGO (`auto_check.py`), dentro do teto do
  hotfix. Os 5 documentos alterados são o **objeto** do defeito: uma revogação não propagada é
  distribuída por construção, e o escopo saiu do lint antes de qualquer edição.

### Próximo passo

**Ready to ship.** Commitar fix + teste + trace doc como uma unidade.

---
*4 hotfix docs ainda não consolidados em `.vibeflow/hotfixes/` — rodar `audit --consolidate-hotfixes`.*
