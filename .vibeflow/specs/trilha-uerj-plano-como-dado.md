---
type: spec
projeto: MedHub
feature: trilha-uerj-plano-como-dado
slug: trilha-uerj-plano-como-dado
status: implemented
relates_to:
  - .vibeflow/specs/plano-ssot-e-cards-v2-part-2.md
  - tools/plano.py
  - core/cronograma/plano_trilha.json
  - core/cronograma/links_listas.json
---

# Spec -- a trilha da Fase 1 vira DADO, e o link da lista viaja ate o plano

> Nascida em sessao de ESTUDO (s188, 2026-09-18), por uso real: o operador pediu o
> cronograma reconciliado ate a UERJ "com tarefas e listas de exercicios". Dois defeitos
> impediam a entrega pelo motor que ele usa todo dia (`day_plan`, painel). Auditoria
> posterior: `/ai-eng`.

## Objective
A ordem da Fase 1 de `plano_tarefas` passa a sair de um arquivo versionado
(`plano_trilha.json`) aplicado por cima das regras puras, e toda tarefa com lista de
exercicios no PDF passa a carregar o link em `url_lista`.

## Context
Medido em 18/09/2026, antes da mudanca:

- **F119 -- link construido e nunca conectado.** `core/cronograma/links_exercicios.json`
  (170 URLs, s147) nao tem NENHUM consumidor (`grep -rn links_exercicios --include=*.py` =
  vazio) e a Reta Final era semeada com `"url_lista": None` cravado (`tools/plano.py`, bloco
  `rf_linhas`). No banco: **0 de 139** linhas `rf` e **66 de 735** linhas `extensivo` com link
  (`plano.py --listar --json`). O painel imprimia "sem lista" em 11 das 14 tarefas da semana.
  Os PDFs carregam o link como ANOTACAO de hiperlink (1.430 no Extensivo, 2.349 na Reta
  Final, medidos com PyPDF2), e o parser so olhava TEXTO.
- **F120 -- estrategia de estudo cravada em codigo.** `ordenar_fase1` decide a Fase 1 por
  regra fixa: bloco MFC abre o plano (semanas 1-2, ordem 1), Clinica Medica fora da lista
  `CM_DIRIGIDA` e CORTADA. Quando o operador derrubou a premissa (UERJ = 20 questoes por
  bloco, Edital 2027), mudar o plano exigia mudar codigo e testes. O unico outro caminho,
  `--mover`, **e desfeito pelo proximo `--semear --apply`**: `semana_plano` e `ordem` estao
  em `CAMPOS_SEMEADOS` (`app/utils/db.py:1735`) e o upsert os reescreve. A spec part-2 ja
  previa a saida ("regra em JSON viria depois se a ordem precisar mudar sem codigo").

## Definition of Done
1. `montar_linhas` preenche `url_lista` de linhas `rf` e `extensivo` a partir de
   `core/cronograma/links_listas.json`; tarefa sem entrada fica `None` (nunca inventa) e o
   `url_lista` que a fonte ja traz sobrevive. Teste: `test_links_preenchem_url_lista_de_rf_e_extensivo`,
   `test_link_do_arquivo_nao_apaga_o_da_fonte`.
2. `aplicar_trilha` (funcao PURA) regrava `semana_plano`/`ordem` e, quando pedidos,
   `status`/`nota`; agendar linha cortada pela regra pura a reabre. Teste:
   `test_trilha_sobrepoe_semana_ordem_status_e_nota`.
3. Com `fase1_exclusiva`, linha PENDENTE que a regra pura poria nas semanas 1-7 e que a
   trilha nao lista sai da fila (semana NULL + nota) sem mudar de status; a Fase 2 nao e
   tocada. Teste: `test_trilha_exclusiva_tira_da_fase1_quem_nao_esta_nela`.
4. Override sem linha correspondente aparece no relatorio e DERRUBA o `--apply` (exit 2);
   `status` fora de `pendente|cortada` e `semana_plano < 1` sao recusados na montagem.
   Testes: `test_trilha_com_chave_inexistente_aparece_e_recusa_o_apply`,
   `test_trilha_recusa_semana_e_status_invalidos`.
5. Fontes injetadas (testes) nunca leem trilha/links do disco:
   `test_fontes_injetadas_nao_leem_trilha_nem_links_do_disco`. Regressao viva:
   `test_trilha_real_nao_tem_override_orfao`.
6. Banco real: `--semear --apply --expect N` com COUNT-ASSERT, backup antes
   (`tools/backup_db.py`), e os status que mudam reconciliados pelos writers de UMA linha
   (`--reabrir`/`--cortar`), com contagem esperada declarada antes e conferida depois.
7. `auto_check --changed` PASSED e suite completa verde.

## Scope
`tools/plano.py` (camadas `links`/`trilha` em `montar_linhas`, `aplicar_trilha`,
`indexar_links`, mensagens do `semear`), `tools/test_plano.py`, dois dados novos em
`core/cronograma/`, `core/cronograma/plano_custom.json` (provas UERJ inteiras como
simulado), `.claude/commands/engenharia-cli.md` (os dois arquivos de dado).

## Anti-scope
Nenhum writer novo em `app/utils/db.py`; nenhuma flag nova de CLI; `ordenar_fase1`/
`ordenar_fase2` e seus testes ficam intactos (a trilha e camada POR CIMA, e ausente = a
politica pura continua valendo). Nao tocar `day_plan.py` nem `painel.py`. Nao reler o Drive.

## Technical Decisions
- **Camada de dado por cima de regra pura, nao troca da regra.** Trocar `ordenar_fase1` por
  outra regra cravada repetiria o F120 na proxima mudanca de estrategia. Com a trilha, mudar
  o plano e editar JSON + `--semear`, e o diff do git mostra o que mudou no ESTUDO.
- **Status de linha existente nao muda pelo re-seed** (contrato da part-3, mantido): a
  trilha fixa o status INICIAL (banco novo) e, no banco vivo, a transicao passa pelos
  writers de uma linha. Os dois caminhos convergem; o limite esta na docstring.
- **Link por anotacao, nao por texto.** A URL no texto do PDF vem quebrada em linhas; na
  anotacao vem inteira. Extracao e one-shot (script em scratch); o DADO e que e versionado.
- **Hermetismo por construcao**: `links`/`trilha` so sao lidos do disco quando nenhuma
  fonte foi injetada.

## Risks
- Trilha envelhece se o operador sair dela: `semana_plano` segue sendo "menor semana com
  pendente" (nunca calendario), entao atraso nao quebra nada -- so empurra.
- `fase1_exclusiva` esconde tarefa pendente da fila: por isso a nota `fora da trilha da
  Fase 1 (reserva)` e o contador `trilha_fora` impresso no dry-run.

## Limites declarados
- O casamento tarefa<->link do Extensivo e por geometria de pagina; tarefa ambigua fica
  SEM link (nunca com link errado). Contagem no `_doc` de `links_listas.json`.
- A trilha nao tem gate que a compare com a incidencia UERJ: a qualidade da ESTRATEGIA e
  julgamento do agente + operador, revisado a cada simulado semanal.
