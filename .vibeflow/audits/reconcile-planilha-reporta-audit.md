# Audit Report: reconcile-planilha-reporta (B3 / F35, item 0.5 do Tier 0)

**Verdict: PASS**

> Spec: `.vibeflow/specs/reconcile-planilha-reporta.md` · sessao **s176 janela 2** (2026-09-10).
> Suite: `python -m pytest tools/ -q` -> **523 passed** (baseline da spec: 503; +20 do suite novo).
> Harness: `python -X utf8 tools/auto_check.py --changed` -> **PASSED**, 0 BLOCK
> (11 checks verdes; o unico WARN e o ERROS_ORFAOS/F38 preexistente, alheio a este item).

## DoD Checklist

- [x] **1. A linha SEMPRE sai no Plano do Dia, inclusive sem dado.** `render()` chama
  `render_planilha()` incondicionalmente (`tools/day_plan.py:1124`) e o estado `nao_medido` tem
  texto proprio com o comando que o resolve (`:379-385`). Verificado no boot real: a linha
  `📋 Planilha x db (W1/F35): ⚠️ NAO MEDIDO ... db tem 7126q` sai hoje.
  Testes: `test_sem_snapshot_e_nao_medido_e_a_linha_sai`, `test_render_nunca_devolve_vazio_em_nenhum_estado`
  (varre 5 estados e exige a ancora `W1/F35` em cada um).
- [x] **2. Snapshot e ESTADO gravado, com as duas idades separadas.** Chave `planilha_snapshot`
  (`tools/importar_sessoes.py:46`), payload com `por_area` · `total` · `ultimo_lancamento` · `lido_em`
  (`:94-98`). Writer unico = `db.set_preparacao` -- o modulo **nao abre `sqlite3`**, entao a
  allowlist do F49 (`tools/test_writer_allowlist.py`) segue intacta e verde. As duas idades sao
  calculadas separadamente (`day_plan.py:340-343`). Teste: `test_duas_idades_nao_colapsam` (52d x 5d).
- [x] **3. Comparacao POR AREA, com oito estados nomeados.** `reconcile_planilha()`
  (`tools/day_plan.py:281-376`) devolve `nao_medido` · `alinhado` · `divergente_por_area` ·
  `import_pendente` · `planilha_atrasada` · `divergente` · `abandonada` · `sem_detalhe_area`.
  Fixtures com os numeros reais da s110: `test_import_pendente_reproduz_os_76q_da_s110`
  (4660 x 4584, delta -76) e `test_divergente_por_area_com_total_igual_e_a_assinatura_do_mislabel`
  (`Clinica Medica` 70 x `Infecto+Hemato+Oftalmo` 70 -- **delta 0 e ainda assim divergente**).
- [x] **4. Reporta, nunca bloqueia.** Nenhum `raise` escapa: o leitor inteiro esta em
  `try/except Exception` -> `_warn_degradacao` + `degradou=True` (`:326-330`); a linha do render
  declara a degradacao. Nenhum check novo entrou no `auto_check`; nenhum exit code mudou.
  Teste: `test_leitor_quebrado_degrada_sem_derrubar_o_boot` (monkeypatch em `db.get_connection`).
- [x] **5. O ingestor recusa planilha internamente inconsistente.** `montar_snapshot()`
  (`tools/importar_sessoes.py:49-98`) levanta `ValueError` com **os dois numeros na mensagem** quando
  `--total` diverge da soma das abas (`:78-81`), mais data no futuro, total negativo, data ausente e
  formato invalido. Verificado por CLI (exit 2 nos quatro casos) e por
  `test_total_divergente_da_soma_das_abas_e_recusado_com_os_dois_numeros` +
  `test_data_no_futuro_e_total_negativo_sao_recusados`.
- [x] **6. A resposta do operador muda o PESO, nao o mecanismo.** `--abandonada "<motivo>"` ->
  `declarar_abandono()` (`:113-125`) faz `update` sobre o snapshot existente, preservando `total` e
  `por_area`; o estado vira `abandonada`, `acao` vira `None` (para de cobrar) e a linha continua
  exibindo o ultimo delta medido. Testes: `test_abandonada_suspende_a_cobranca_e_preserva_o_ultimo_delta`,
  `test_declarar_abandono_nao_apaga_o_snapshot`.
- [x] **7. Portadores atualizados no mesmo commit.** `reconcile-contract.md` W1 troca `manual` pelo
  instrumento real, PASSO 3 ganha a acao por estado, secao de absorcao normatiza o snapshot,
  `version: 1.2 -> 1.3` **com entrada de changelog** (nao reintroduz o G11). `/importar-planilha`
  ganha o passo 6 do fluxo + a assinatura canonica dos 4 flags; `sync_skills --check` exit 0.
  Os dois portadores tem **teste de paridade** (`test_contrato_w1_nao_declara_mais_manual`,
  `test_skill_carrega_a_assinatura_do_flag_novo`) -- ambos nasceram **vermelhos** e so ficaram verdes
  depois da edicao, que e a prova de que medem.

## Pattern Compliance

- [x] **Database access** (`conventions.md`) — `day_plan` nao importa `sqlite3`; le por
  `db.get_connection()` e fecha em `finally` (`:331-336`). `importar_sessoes` nao abre conexao:
  delega a `db.set_preparacao`/`get_preparacao`.
- [x] **Sensors (WARN-first)** — o reconcile **detecta e reporta**; nao corrige, nao bloqueia, nao
  escreve. A unica escrita da feature e explicita, por comando do agente (`--snapshot`).
  Honest silence respeitado ao contrario do usual: onde nao ha medicao, ele **diz** que nao ha.
- [x] **File naming / testes** — `tools/test_reconcile_planilha.py` inscrito em `python_files`
  do `pytest.ini` com a nota de 5 linhas no padrao do arquivo. O gate `test_suites_orfas` (F43)
  **pegou a omissao** antes do commit: suite existia e nao rodava. Gate funcionando como projetado.
- [x] **Agent norms** — canonico em `.claude/commands/`, espelho regenerado por `sync_skills`,
  nunca editado a mao. Assinatura de CLI em **uma** skill (§7.2).
- [x] **Encoding (AGENTE §4.5)** — ASCII limpo no codigo novo: `->`, `--`, aspas retas; sem LaTeX,
  sem setas Unicode. Os emoji de rotulo seguem o padrao ja vigente no `render()`.

## Convention Violations

Nenhuma.

## Critical Gate

Clean — no destructive operations detected.

Varredura sobre `git diff HEAD -U0` (9 arquivos, +396/-15) mais os 2 untracked: zero ocorrencias de
`DROP` · `TRUNCATE` · `DELETE FROM` · `eval/exec/subprocess` · segredo literal · flag de TLS ·
`debug = true` · delete em massa. Nenhuma migration, nenhum `.tf/.yaml` de infra, nenhum endpoint.
`os.remove()` aparece apenas em `tools/test_reconcile_planilha.py` sobre paths de `tempfile.mkstemp`,
no mesmo padrao de `test_orquestrador.py` — limpeza de fixture, nao operacao sobre dado real.
A unica escrita nova no `ipub.db` e um upsert de 1 linha em `preparacao_estado` via o writer ja
allowlistado; `sessoes_bulk` **nao e tocado** por nenhum caminho novo.

## Fronteiras DECLARADAS (nao ler PASS como cobertura completa)

1. 🔴 **Fidelidade do snapshot ao Drive e NAO VERIFICAVEL.** Quem alimenta o snapshot e o agente,
   lendo a planilha por MCP. A spec valida **coerencia interna** (soma das abas x total declarado,
   datas no passado) e nada mais: um snapshot errado produz um relatorio errado com a mesma
   confianca de um certo. Enquanto o **F36** (transporte de binario) nao fechar, nao existe gate
   para isso — e esta declarado em vez de virar metrica inventada (§10.8 do `AGENTE.md`). Mitigacao
   parcial e honesta: a linha do boot exibe `lido_em`, para que a idade da copia nunca passe por
   medicao fresca.
2. **Vocabulario de area continua sem validacao** — area fantasma (`GO`, `Clinica Medica`) aparece
   **crua** no relatorio como divergencia. E o sintoma, nao o conserto: consertar na origem e o
   **F89**, item **0.6**, o proximo da fila. Anti-escopo respeitado.
3. **O numero 6.288 do `HANDOFF.md` nao foi adotado.** Nao tem data nem comando (claim envelhecido,
   D67/G8) — entra no mecanismo como o primeiro `NAO MEDIDO`, nao como fixture.

## Estado dos hotfixes

**12 hotfix docs** em `.vibeflow/hotfixes/` ainda nao consolidados (`ls .vibeflow/hotfixes/*.md | wc -l`,
medido agora) — rodar `audit --consolidate-hotfixes`. Pendencia herdada, ja declarada no `HANDOFF.md`
(que cita os 2 mais recentes, da janela 1); nao e deste item. ⚠️ O `HANDOFF.md` diz "2 hotfix docs" e
o diretorio tem 12: o numero de la conta os **novos**, o do consolidador conta **todos os presentes**.

---

**Ready to ship.**
