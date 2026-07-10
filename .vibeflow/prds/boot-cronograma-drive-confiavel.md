---
title: "Boot Confiavel -- Disparo Forcado do Sync Drive, Ordenacao Real, Integridade de Rotulo e Higiene de Estado"
type: prd
status: approved
author: "Claude Code (sessao 115, Fable 5)"
date: "2026-07-09"
relates_to:
  - core/contracts/cronograma-contract.md
  - core/contracts/reconcile-contract.md
  - AGENTE.md
  - tools/cronograma.py
  - tools/day_plan.py
  - tools/insert_questao.py
  - AUDITORIA_MEDHUB.md
---

# PRD: Boot Confiavel -- Disparo Forcado do Sync Drive, Ordenacao Real, Integridade de Rotulo e Higiene de Estado

> Gerado via /vibeflow:discover em 2026-07-09 (sessao 115). Ledger de origem: AUDITORIA_MEDHUB.md (achado novo **F34** + resolve **F30**/**F31** + onda de higiene do risco 5 da auditoria de boot). Registro de engenharia de sistemas: o conteudo clinico e apenas o *dado* que as estruturas (snapshot, fila, contrato, CLI, hook) transportam.

## Problem

O boot do MedHub deriva toda a sua inteligencia de cronograma de fontes locais (o hook `SessionStart` roda **headless** e so enxerga o `ipub.db` + `grade.json`). Mas a **verdade de execucao** do cronograma vive no Drive: o usuario risca tarefas concluidas E **reordena tarefas manualmente** no `Cronograma de Reta Final.xlsx`, enquanto o `Cronograma.pdf` (SSOT estrutural do `grade.json`) fica congelado. So o agente interativo alcanca o Drive (via MCP); o hook nao. O resultado e uma costura estrutural onde tudo que depende do Drive -- conclusao real (W8/F33), reconcile de volume (W1/F29) e a ordenacao das tarefas -- fica refem da disciplina do agente lembrar de rodar `cronograma.py --sync-drive`, e **regride silenciosamente** quando ele nao roda.

Essa regressao nao e teorica: **o boot desta sessao (09/07) a exibiu ao vivo em dois pontos.** (1) O `day_plan` injetado listou `proximos temas: Medicina de Familia (extensivo), Imunizacoes (extensivo), Apendicite (extensivo)` -- os tres **ja feitos** (riscados no Drive, HANDOFF s114/F33) -- porque nenhum snapshot fresco de conclusao existia no boot headless, entao o `day_plan` caiu para a ordem-do-PDF (o comportamento degradado previsto na Clausula 5, mas silencioso demais). (2) O plano recomendou `Refrescar: Leishmaniose`, tema que o **F31** documenta como sem nenhum lastro escrito (nem `.md` nem PDF-fonte). Some-se o **F30**: tarefas vem com `material_indicado: resumo` (implicando "so ler o resumo existente") sem que ninguem verifique se o `.md` existe -- Pre-Natal era tema-zero mascarado. O agente confia em rotulos que a arvore de arquivos contradiz.

Por baixo, a propria camada de estado que o boot le como verdade-macro drifta a mao: o `ESTADO.md` virou diario de sessoes contra o proprio `estado-contract` (a linha "Indicador Atual" acumula s096..s114 num paragrafo-corrido), o contador de resumos aparece como **63** e **61** no mesmo arquivo, e o ponteiro de abertos do `HANDOFF` omite o F31 (que tem instancia viva hoje). Ponteiros mantidos a mao driftam; os derivados nao -- e o boot le os mantidos a mao.

## Target Audience

Usuario unico -- medico em preparacao (sprint ENAMED 13/09; objetivo central Psiquiatria UFRJ/IPUB; paralelas reais = UERJ tradicional + Pro-Residencia MFC da UERJ, talvez USP) -- **e os agentes gerenciadores** (Claude Code primario, mais os irmaos), que precisam abrir a sessao com um plano de cronograma fiel a execucao real sem o usuario ter de contestar o boot toda vez.

## Proposed Solution

Fechar a costura headless/Drive respeitando a arquitetura ja decidida (Clausula 1: sem dependencia de MCP no boot automatico; Clausula 3: sem cron, sem daemon). Nao automatizamos o fetch do Drive -- **tornamos o disparo interativo confiavel e a regressao impossivel de passar despercebida**, e enriquecemos o que o sync ja captura. Quatro ondas:

1. **Onda C (keystone) -- Disparo forcado + degradacao graciosa.** Promover o sync do Drive de passo *condicional* ("se aparecer o WARNING, buscar" -- AGENTE 2.4 hoje) para **acao obrigatoria** quando o snapshot esta velho: o agente busca o xlsx via MCP e roda `--sync-drive` **antes** de apresentar "proximos temas". Se o MCP estiver indisponivel (sessao headless/offline), apresenta calendario-only **com caveat explicito nomeando o risco de temas-ja-feitos** -- nunca em silencio. O `day_plan` ganha um banner de frescor no topo ("Drive: Nd atras / STALE"). Sem BLOCK (a Clausula 6 mantem reconcile "sempre WARNING, nunca hostil"; a escolha e enforced-action, nao gate).

2. **Onda A -- Ordenacao real (aditivo ao --sync-drive).** Enquanto ja parseia o xlsx para o tachado, o `--sync-drive` passa a capturar tambem **(ordem, semana)** por tarefa e grava no snapshot `preparacao_estado`. O `day_plan` posiciona "proximos temas" pela **ordem real do xlsx** quando o snapshot e do dia-calendario corrente; degrada para a sequencia do PDF (comportamento atual) quando ausente/velho, com WARN. Puramente aditivo a Clausula 5 -- nada reescreve o `grade.json`.

3. **Onda B -- Integridade de rotulo (independente do Drive, 100% local).** Fecha F30 e F31: (a) o `day_plan`/`cronograma` chama `get_topic_context._find_resumo(area, tema)` em tempo real ao render e **rebaixa `material_indicado` de `resumo` para `extensivo`** quando o `.md` nao existe -- deixa de prometer "so ler o resumo" quando ele nao existe; (b) `insert_questao.py` emite **WARN read-only** no ato da insercao quando o tema nao tem nenhum lastro escrito (`_find_resumo` None e sem PDF-fonte par), sinalizando o par Siamese Twins quebrado na hora, nao meses depois num refresh.

4. **Onda D (leve) -- Higiene da camada de estado (risco 5, "derive, nao mantenha a mao").** Derivar o contador de resumos (um numero, do filesystem, no `--handoff-block`) em vez de digita-lo; aplicar a regra do `estado-contract` de que a linha "Indicador Atual" nao e diario de sessoes (enxugar o acumulo, mover narrativa de sessao para `history/`); corrigir o ponteiro de abertos do `HANDOFF` para incluir F31.

## Success Criteria

1. **Disparo/degradacao:** num dia-calendario sem sync fresco, o `day_plan` mostra "Drive: STALE (Nd)" no topo E o agente roda `--sync-drive` antes de apresentar "proximos temas"; com MCP indisponivel, apresenta calendario-only com caveat explicito citando o risco de temas-ja-feitos. Em nenhum caminho o boot apresenta "proximos temas" silenciosamente sobre snapshot velho.
2. **Ordenacao:** com snapshot fresco apos reordenacao manual no xlsx, "proximos temas" reflete a **ordem do xlsx**, nao a sequencia do PDF. Sem snapshot fresco, cai para PDF-order + WARN (nunca falha silenciosa).
3. **F30:** tarefa com `material_indicado: resumo` cujo `.md` nao existe e rebaixada automaticamente para `extensivo` no render do plano.
4. **F31:** `insert_questao` para tema sem `.md` e sem PDF-fonte emite WARN read-only no ato, sem bloquear a insercao.
5. **Higiene:** o contador de resumos e derivado (um valor, bate com `resumos/**/*.md`); a linha "Indicador Atual" do `ESTADO` deixa de crescer por sessao; o bloco de abertos do `HANDOFF` inclui F31.
6. **Nao-regressao de fronteira:** nenhuma escrita nova em `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log` (Clausula 5); `grade.json` permanece derivado so do PDF (Clausula 1/3); `auto_check.py --changed` PASSED apos as ondas.

## Scope v0

- **C:** `AGENTE.md` 2.4 reescrito (sync condicional -> acao obrigatoria quando stale + fallback calendario-only-com-caveat); `day_plan.py` emite banner de frescor do Drive ("Drive: Nd / STALE") no topo do bloco de cronograma e marca "proximos temas" como derivados-de-snapshot-velho quando aplicavel; `reconcile-contract.md` W8 refinado (frescor obrigatorio-de-tentativa, nao so opcional).
- **A:** `cronograma.py --sync-drive` estendido para capturar `(ordem, semana)` por task no snapshot `preparacao_estado` (chave estendida ou irma de `cronograma_conclusao_drive`); `day_plan.py::_resolver_semana_conteudo`/o resolvedor de "proximos temas" le a ordem do snapshot quando fresco, PDF-order como fallback; `cronograma-contract.md` Clausula 5 documenta a chave nova.
- **B:** `day_plan.py`/`cronograma.py` chamam `_find_resumo` ao render e rebaixam `material_indicado` (F30); `insert_questao.py` faz check read-only pos/pre-insert e emite WARN quando sem lastro (F31); reaproveita o `_find_resumo` que ja indexa `path.stem.lower()` (corrigido s096).
- **D:** `day_plan.py --handoff-block` passa a derivar/emitir o contador de resumos; `ESTADO.md` linha Indicador enxugada + regra reforcada no `estado-contract.md`; `HANDOFF.md` ponteiro de abertos corrigido (F31).
- **Fatiamento provavel (budget <=6 arquivos/spec):** o gen-spec deve dividir em ~3 specs -- **spec-1 = C+A** (costura Drive: disparo + ordenacao, mesmos arquivos `cronograma.py`/`day_plan.py`/contratos); **spec-2 = B** (integridade de rotulo, `day_plan`/`cronograma`/`insert_questao`); **spec-3 = D** (higiene, `day_plan --handoff-block`/`ESTADO`/`HANDOFF`/`estado-contract`).

## Anti-scope

- **Sem automacao real do fetch do Drive** (cron, daemon, credencial de servico, cache local do xlsx) -- viola Clausula 1 ("evita dependencia de MCP no boot") e Clausula 3 ("sem cron, sem daemon"). O sync continua disparado pelo agente interativo; so forcamos a disciplina e matamos a regressao silenciosa.
- **Sem reconstrucao estrutural do `grade.json` a partir do xlsx** (promover o xlsx a SSOT de ordenacao) -- quebra Clausula 1 (SSOT = `Cronograma.pdf`) e Clausula 3 (`grade.json` = cache regeneravel do PDF). A ordem do xlsx vive no snapshot `preparacao_estado`, sobreposta em memoria, nunca no `grade.json`.
- **Sem BLOCK de boot** por estar atrasado ou por snapshot velho (Clausula 6: reconcile sempre WARNING). A opcao escolhida e enforced-action + degradacao graciosa, nao hard gate.
- **Sem alinhamento fino `questoes_por_lista[i] <-> tasks[i]`** -- permanece rateio igual (fora de escopo declarado na `cronograma-contract`).
- **Sem escrita nova em `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log`** (Clausula 5). O unico write permitido segue sendo `preparacao_estado` via CLI.
- **Sem tocar** motor/agendamento FSRS, Streamlit (`app/pages`), schema do `ipub.db` alem da chave/valor existente em `preparacao_estado`.
- **Sem fabricar `history/session_NNN` retroativos** nem mexer no reconcile de volume W1/F29 alem de o banner de frescor cobrir tambem "quando foi o ultimo reconcile de volume" (a mecanizacao completa do W1 e item separado).
- Risco 4 da auditoria de boot (single-target ENAMED) **descartado** pelo usuario: as paralelas reais (UERJ MFC) ja sao servidas pelo eixo-tema porque MFC esta no proprio cronograma ENAMED; nao ha conceito de "prova-alvo" nesta PRD.

## Technical Context

- **Costura headless/interativo:** o hook `SessionStart` (`tools/hooks/memory_boot.py`) roda `day_plan.py` via subprocess e injeta texto -- **sem acesso a MCP**. O fetch do Drive (`mcp__claude_ai_Google_Drive__download_file_content`, fileId em `.claude/commands/importar-planilha.md`) so acontece na conversa. AGENTE 2.4 ja reconhece isso ("se o MCP falhar/estiver indisponivel (sessao headless), seguir com o plano calendario-only") -- esta PRD torna o caminho stale **ruidoso e obrigatorio-de-tentativa**, nao silencioso-e-opcional.
- **Mecanismo de snapshot (a reusar/estender):** `preparacao_estado` (`ipub.db`, chave/valor/`atualizado_em`/`fonte`) ja carrega `cronograma_conclusao_drive` (v1.1, F33). Frescor = dia-calendario de `atualizado_em`; `day_plan` degrada para calendario puro quando ausente/velho. A Onda A adiciona `(ordem, semana)` no mesmo padrao. Escrita via CLI, `import sqlite3` so em `app/utils/db.py` (+ CLIs standalone) -- padrao `db-access-layer.md`.
- **Matching semantico ja existente:** `--sync-drive` casa xlsx-task <-> `grade.json`-task por `(semana, tema normalizado via unicodedata, tipo_norm)` porque o indice nao bate 1:1 entre PDF e xlsx. A ordem do xlsx (indice de linha por task) sai do mesmo parse.
- **`_find_resumo`:** ja indexa `path.stem.lower()` desde s096 (era pre-requisito do `infer_nota`); a Onda B **consome** o resultado dele para verificar o rotulo, nao reescreve o resolvedor.
- **Contratos governантes:** `cronograma-contract.md` (Clausulas 1/2/3/5/6 + changelog v1.1/F33), `reconcile-contract.md` (W8 e a filosofia "nunca BLOCKING"), `estado-contract.md` (ESTADO nao e diario), `AGENTE.md` 2.4 (boot passo 4) e 6 (decisoes de cronograma). Padroes vibeflow aplicaveis: `agent-workflow-protocol.md`, `db-access-layer.md`.
- **Harness:** `auto_check.py --changed` (BLOCK/WARN), invariante `POSICAO_DRIFT` e `SESSION_POINTER_DRIFT` ja no lugar; a Onda D pode ganhar um WARN de "contador de resumos digitado a mao diverge do derivado" se barato.
- **Ledger:** achado novo da costura de disparo/ordenacao = **F34** (proximos comecam em F34 por HANDOFF); esta PRD resolve **F30**/**F31** e a onda de higiene (risco 5). Trilha de engenharia -> este doc + `.vibeflow/`; nada de conteudo clinico aqui (secao 7.6 do ledger).

## Open Questions

Nenhuma. Forks resolvidos na discovery de 2026-07-09: (1) enforcement do disparo = acao obrigatoria + degradacao graciosa (nao hard gate, respeita Clausula 6); (2) ordenacao = incremental via snapshot (estrutural descartado por violar Clausula 1/3); (3) risco 5 incluido como onda leve (gen-spec fatia); (4) risco 4 (single-target) descartado. Detalhe de schema do snapshot (estender `cronograma_conclusao_drive` vs chave irma `cronograma_ordem_drive`) e decisao de implementacao para o gen-spec, nao fork de produto.
