# Audit Report: vocabulario-de-area-unico (F89, item 0.6 do Tier 0)

**Verdict: PASS**

> Spec: `.vibeflow/specs/vocabulario-de-area-unico.md` · sessao **s176 janela 2** (2026-09-10).
> Suite: `python -m pytest tools/ -q` -> **540 passed** (baseline da spec: 523; +17 do suite novo).
> Harness: `python -X utf8 tools/auto_check.py --changed` -> **PASSED**, 0 BLOCK.

## DoD Checklist

- [x] **1. Uma fonte, e ela e DADO.** `core/areas.json` (novo) + `app/utils/areas.py` (novo, leitor
  unico), no molde exato de `core/provas.json` + `app/utils/provas.py`. A lista carrega `_doc`
  dizendo que muda-la e decisao do operador. Consequencia que a spec buscava: a **RODADA 3 virou
  edicao de dado**, nao de codigo.
- [x] **2. O leitor NAO e tolerante.** `_carregar()` levanta `VocabularioIndisponivel` em arquivo
  ausente (`areas.py:44-47`), ilegivel (`:48-49`) e **vazio** (`:53-55`); nao existe caminho que
  devolva lista vazia. A divergencia deliberada em relacao ao `provas.py` esta **escrita na
  docstring do modulo**, com o porque. Testes: `test_vocabulario_ausente_levanta_em_vez_de_devolver_vazio`,
  `test_vocabulario_ilegivel_e_vazio_levantam`.
- [x] **3. Duas listas nomeadas.** `AREAS_CLINICAS` (20) · `AREAS_AGREGADAS` (`Simulado`) ·
  `AREAS_VALIDAS` = uniao (21). `performance.py` passou a montar gaps sobre `AREAS_CLINICAS` --
  comportamento identico ao de antes, agora **por decisao declarada** (`_nota_agregadas` no JSON) em
  vez de por copia desatualizada. Testes: `test_simulado_e_valido_para_escrita_e_fora_das_clinicas`,
  `test_gaps_do_performance_nunca_listam_simulado`.
- [x] **4. Fail-loud nos 3 writers.** `registrar_sessao_bulk.registrar` (logo apos o guard de
  `acertos>feitas`), `insert_questao.insert_questao` (**no topo da funcao** -- `area` e a precondicao
  mais barata, entao o chamador ve o primeiro problema real e nao o segundo) e
  `insert_card_base.get_or_create_tema`. Um teste por writer + `test_os_tres_writers_chamam_o_gate`
  (varredura: writer que esqueca a chamada aparece). **Acumulo em linha fantasma existente tambem
  recusa** e o teste confirma que nada foi escrito
  (`test_gate_recusa_tambem_acumulo_em_linha_fantasma_existente`).
- [x] **5. O passivo vira WARN, nao BLOCK.** `check_areas_fora_vocabulario` (read-only, as 2 tabelas)
  + `[WARN] AREAS_FANTASMA` no `auto_check`, com `success=True` (nao rebaixa veredito). Saida real:
  **5 pares, 18 linhas**. Testes: deteccao nas 2 tabelas, `None` em base limpa (incluindo `Simulado`,
  que e valido) e a paridade que exige `success=True` na fonte.
  ⚠️ **DEVIACAO DECLARADA (1):** a spec dizia "a consulta vive em `app/utils/db.py`"; foi para
  `tools/utils/state_utils.py`. Razao: e onde **todos** os checks de estado do `auto_check` ja vivem
  (`check_erros_orfaos`, `check_session_pointer`, `check_needs_qualitative`) -- a intencao da clausula
  (consulta fora do corpo do check) esta cumprida, e seguir o padrao real do repo vale mais que
  seguir meu palpite escrito antes de ler `state_utils`. Registrada em vez de silenciada, e a spec
  **nao** foi reescrita para caber no resultado.
- [x] **6. Nenhuma copia sobrevive.** `test_nenhuma_copia_da_lista_sobrevive_no_repo` varre
  `tools/` + `app/` e falha nomeando o arquivo. `registrar_sessao_bulk.AREAS_VALIDAS` continua
  importavel (o `importar_sessoes` depende dele) como **re-export**
  (`test_reexport_do_registrar_bulk_continua_importavel_e_identico`).
- [x] **7. Craftsmanship gate.** `auto_check --changed` PASSED; 540 passed; `sqlite3` so na camada de
  acesso e nos CLIs standalone (excecao ja prevista em `conventions.md`); allowlist F49 **inalterada**
  (`validar_area` nao emite SQL); ASCII limpo no codigo novo.

## Pattern Compliance

- [x] **Fonte unica de dado em `core/` + leitor em `app/`** — precedente `provas.json`/`provas.py`
  (F88) seguido, inclusive na direcao da dependencia (`app/` nao importa `tools/`).
- [x] **Sensors (WARN-first)** — o check novo detecta, nomeia e nao corrige; nasce WARN por politica
  s106/107 e a razao (o passivo e conteudo do operador) esta no codigo, nao so no ledger.
- [x] **Agent norms** — canonicos editados em `.claude/commands/`, espelhos por `sync_skills --check`
  exit 0; os **ponteiros mortos** para o antigo endereco da lista foram corrigidos nos 3 portadores
  (`importar-planilha`, `performance`, `curar-cards`), que e a metade dentro do repo da regra §10.4.
- [x] **File naming / testes** — `tools/test_vocabulario_area.py` inscrito no `pytest.ini` com nota.

## Convention Violations

Nenhuma.

## Critical Gate

Clean — no destructive operations detected.

Diff (19 arquivos modificados + 4 novos) varrido por `DROP` · `TRUNCATE` · `DELETE FROM` ·
`eval/exec/subprocess` · segredo literal · TLS · `rmtree`: **zero ocorrencias**. Nenhuma migration e
nenhum `UPDATE`/`DELETE` novo: a mudanca **so adiciona recusas** ao caminho de escrita. O efeito
colateral mais forte do diff e, por construcao, **impedir** escritas que antes aconteciam.

## Achado dentro do item (rider, F94 -- corrigido no ato)

Escrever o teste antes do codigo derrubou 9 testes que nem tocavam o modulo:
`tools/insert_card_base.py:51` e `tools/cards_regen_queue.py:29` faziam
`sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)` **incondicional no topo do modulo**,
sequestrando o stdout do processo no mero `import`. O `importar_sessoes.py` **ja tinha consertado o
proprio sitio** (com o motivo na docstring) e o `fsrs_queue.py:33` **ja tinha a guarda certa** -- os
dois irmaos ficaram para tras. Classe: **sitio gemeo de defeito ja consertado** (forma do F80b e do
2o silenciador do F91), invisivel porque **nenhum teste os importava**. Ambos receberam a guarda do
`fsrs_queue`; varredura fechada: os 3 usos restantes sao fixtures de teste sobre `io.BytesIO()`.
Ledger `AUDITORIA_MEDHUB.md §6u`.

## Fronteiras DECLARADAS (nao ler PASS como cobertura completa)

1. 🔴 **O gate e de VOCABULARIO, nao de VERDADE.** Ele garante que a area existe na lista, nunca que
   e a area **certa** para o tema: `insert_questao --area Pediatria --tema "Apendicite Aguda"` passa
   em todos os checks. Essa camada e a RODADA 3 (conteudo, do operador) e continua **sem
   instrumento** -- declarado, nao convertido em metrica (§10.8).
2. **O passivo de 18 linhas NAO foi migrado.** Ha 39 cards + 33 erros pendurados nas linhas
   fantasma; reclassificar e do operador (Tier 2.1). A spec impede o crescimento e **conta** o que
   existe. Migrar por conta propria repetiria o erro da RODADA 1: operacao unica sem gate de retorno.
3. **Nao ha normalizacao automatica**, e isso e escolha: `GO` e Ginecologia **ou** Obstetricia, e na
   s110 tres linhas de `Clinica Medica` eram Infecto, Hemato e Oftalmo. O writer entrega a
   **ambiguidade** e recusa; quem decide e quem chamou.
4. **A LISTA entregue e a ATUAL** (21 itens, identica a que estava em `registrar_sessao_bulk`).
   Fundir/renomear/acrescentar e RODADA 3.

## Achado de bookkeeping (medido, NAO corrigido aqui -- por ordem)

`grep -nE "^### F<id> " AUDITORIA_MEDHUB.md` mostra **6 achados fechados na janela 1 ainda com
`ABERTO`/`PARCIAL` no cabecalho do ledger**: F40 · F41 · F77 · F77b · F81 · F91 — enquanto o §11
carrega a lapide com commit. Fica para a **varredura unica (1.8)** pelo proprio principio do
`/ai-eng` (*higiene em varredura unica*), nao por nao ter sido visto; registrado como **G14** na
linha 1.8 do `§11`. As linhas de status do `§3` **ja foram** re-derivadas das lapides nesta janela.

## Estado dos hotfixes

12 hotfix docs em `.vibeflow/hotfixes/` ainda nao consolidados — `audit --consolidate-hotfixes`.
Pendencia herdada; nao e deste item.

---

**Ready to ship.**
