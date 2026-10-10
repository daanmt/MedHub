# PRD: medhub Fase 0 — preparar o ambiente para virar plataforma (Scope v0 = Lote 0: chão limpo / harness hermético)

> Generated via discover on 2026-10-10 (discover conduzido pelo arquiteto `/ai-eng` sob ordem do operador de 10/10; redação pelo redator de specs do ai-eng; o operador entra só por pergunta fechada)
> Evidência (ai-eng, leitura apenas sobre o medhub): `brain/observed-systems/medhub-reforma-2026-10-10/` — A (identidade do código), B (dados), C (entrega/UI), D1 (git/housekeeping), D2 (contratos/pendências), E (testes/harness). Achados do próprio agente do medhub em 10/10 (ledger no pre-commit, `reachability_check` gravando, `/loop` morto pelo `/clear`).
> Código do medhub conferido em leitura em 2026-10-10 @ `6d0239a` (os `path:linha` das specs vêm dessa leitura).
> Repo-alvo: `C:/Users/daanm/medhub`. **Implement e audit são do medhub** (loop vibeflow dele, `AGENTE.md §10.6`); este PRD, as specs e o prompt-pack nascem no ai-eng e chegam ao medhub por cópia do orquestrador (portador no repo deles).

## Problem

O medhub vai virar plataforma madura depois de 01/11/2026 (backend real, banco servidor, front React, deploy). Hoje quase nada do que ele afirma sobre si mesmo é verificável de forma hermética, e cada decisão de migração herdaria esse ruído:

1. **O harness escreve no que deveria só medir.** O hook de boot roda `tools/day_plan.py` sem `--no-persist` (`tools/hooks/memory_boot.py:72-76`) e faz DELETE+INSERT em `plano_dia` do banco vivo a cada abertura de sessão (`tools/day_plan.py:1309,1313`). O pre-commit grava `history/ledger_self.jsonl` e `history/card_watermark.json`, ambos rastreados, depois do stage — a árvore nunca fica limpa (commit de resíduo `d48de82`; `ledger_self.jsonl` tocado em 87 commits).
2. **O gate pula.** A matriz de disparo do `auto_check` é por extensão (`tools/auto_check.py:567-571`): commit só com `core/*.json`, `core/templates/*`, `artifacts/*` ou `app/**` sai com "Nenhum arquivo crítico... Aprovado!" (`:580-589`) sem a suíte e sem os checks que o próprio código chama de "roda SEMPRE". Caso real: s216, 2 FAILED só apareceram no commit seguinte.
3. **A suíte mede o dado do operador.** 13 funções em 12 arquivos abrem o `ipub.db` real com valor fixo; 4 passam sem medir (`return`) quando não há banco. A suíte quebra quando o operador estuda.
4. **A catraca tem folga.** `BASE_ORFAS = 127` fixa (`tools/clausulas_check.py:87`), 128 órfãs medidas, só WARN; a 128ª está em `.claude/commands/banco-emed.md:154`. O cabeçalho do `cli_signature_check` diz WARN, mas o check é BLOCK no `auto_check`.
5. **Peso morto e local.** Módulos sem chamador, `tools/_archive/` (14 arquivos), `.streamlit/`, escrita em tabela inexistente `cronograma_progresso` engolida por `try/except: pass` (`tools/insert_questao.py:413-420`), 6.708 objetos soltos no `.git` (57,8 MiB), `artifacts/backups/` 436 MB (53 fixados), `tmp/` 382 MB / 32.959 arquivos.

Sem chão limpo, nenhum número que os lotes seguintes produzirem pode ser conferido por comando.

## Target Audience

- **Implementador:** agente Claude Code na sessão do medhub, com o loop vibeflow (`implement` → `audit`). Recebe cada parte como spec auto-suficiente; a part-1 vem com prompt-pack.
- **Orquestrador:** `/ai-eng` — triagem, sequência e GO/NO-GO/ALTERA só em bifurcação; silêncio = GO (`AGENTE.md §10.6`).
- **Operador** (médico; prova em 01/11/2026): beneficiário. Entra só por pergunta fechada (ver Open Questions).

## Proposed Solution

A Fase 0 resolve agora as pendências de engenharia, gestão, housekeeping e arquitetura, em seis lotes executados em ordem. **Só o Lote 0 é especificado aqui**; os demais estão apenas nomeados.

| Lote | Conteúdo (1 linha) | Tipo |
|---|---|---|
| **0** | Chão limpo / harness hermético: hooks e pre-commit não escrevem nem pulam; testes herméticos; catraca de cláusulas derivada; código morto e peso local | **spec-agora** (7 partes, abaixo) |
| 1 | Bugs de estudo: P5 figuras · P2 `versao` da solução como gate · P6 âncora de card em `emed_respostas` | spec-pendente |
| 2 | P1 fontes estruturadas: JSON por fonte + migrador COUNT-ASSERT 872 + regra "fonte só sai com 2ª lente" + amostra de 62 | ADR + spec-pendente |
| 3 | Hub e contratos: P4 pendência na lista; contradições de contrato; README/index; `.vibeflow` com ciclo de vida; backlog em 1 lugar | spec-pendente |
| 4 | Dados pré-migração: marcador de fuso; `cards_prune` soft-delete; ids congelados; figuras fora de `tmp/`; backup off-machine | ADR + decisão-operador (destino do backup) |
| 5 | Medições do portão da Fase 1: 10% de cadeia com defeito; tokens por unidade; custo LangMem/HyDE | spec-pendente (medição; alimenta o ADR da Fase 1) |
| P3 | Sensor "tique parado > 60 min" agora (WARN); job durável na Fase 1 | spec-pendente (sensor) + ADR (Fase 1) |

**Lote 0 — partes, ordem e dependência** (specs em `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-N.md`):

| Ordem | Parte | O quê | Arquivos | DoD |
|---|---|---|---|---|
| 1 | part-1 | Hooks e pre-commit não escrevem nem pulam (boot grava ≤ 1×/dia; gatilho por prefixo + deleções; checks "sempre" sempre; runtime do harness fora do git) | 6 (+2 des-rastreados) | 7 |
| 2 | part-2a | Fixture de banco sintético + isolamento do runtime nos testes + marcador `vivo`; os 4 verdes decorativos viram skip declarado com gêmeo hermético | 6 | 6 |
| 3 | part-2b | Família hub/cards/EMED (5 arquivos de classe 1, incluindo as 2 asserções de registro com número fixo) mede forma ou fixture | 5 | 5 |
| 3 | part-2c | Os 3 acoplados fora do núcleo do pytest (golden t3, script `revisao_calibrada`, telemetria do day_plan) | 3 | 5 |
| 4 | part-3 | Catraca de órfãs derivada do HEAD (órfã nova = BLOCK no pre-commit), 128ª com terminal, cabeçalho do `cli_signature_check` = BLOCK | 6 | 6 |
| 5 | part-4a | Código morto sem norma por cima sai (3 arquivos + 10 funções do `db.py`), escrita em `cronograma_progresso` sai com teste de schema, alcançabilidade medida antes/depois, `reachability_check` em modo texto para de gravar | 6 (+3 deleções) | 7 |
| 6 | part-4b | Peso local: `git gc` agora; desfixar em lote e inventário de `tmp/` com dry-run pronto e apply **gated** por GO do operador | 4 | 6 |

part-2b e part-2c dependem da part-2a e podem correr em paralelo entre si.

## Success Criteria

O Lote 0 está pronto quando, cada um com o comando que o prova:

1. Depois de qualquer commit, `git status --porcelain` não lista arquivo escrito pelo pre-commit/`auto_check`.
2. Abrir sessão num dia que já tem plano não altera `plano_dia` (`COUNT(*)` e `MAX(criado_em)` do dia iguais antes e depois, consulta read-only).
3. Todo commit que toca `tools/`, `app/`, `core/`, `artifacts/`, `.claude/`, `.agents/` ou a config de teste (qualquer extensão, inclusive deleção) roda `python -m pytest tools/ -q`; nenhum commit sai sem os checks "sempre".
4. `python -m pytest tools/ -q -m "not vivo"` passa, e todo teste que lê dado do operador está marcado `vivo` e pula **com motivo** quando o dado falta. Zero `return` silencioso nos 4 casos conhecidos.
5. Órfã nova de cláusula bloqueia o commit (base = contagem no `HEAD`); a contagem de órfãs termina ≤ 127.
6. O código morto listado sai com `python tools/reachability_check.py --json` registrado antes e depois; nenhum código escreve em tabela ausente do schema (teste).
7. `git count-objects -v` mostra menos objetos soltos; poda de fixados e purga de `tmp/` só acontecem com GO, a partir de um dry-run com contagem.

## Scope v0

Lote 0 apenas, nas 7 partes da tabela acima:

- part-1 — hooks e pre-commit não escrevem nem pulam
- part-2a — fixture sintético, isolamento do runtime nos testes, marcador `vivo`, 4 verdes decorativos
- part-2b — acoplados da família hub/cards/EMED
- part-2c — acoplados fora do núcleo do pytest
- part-3 — catraca de cláusulas derivada + CLI check coerente
- part-4a — código morto + `cronograma_progresso` + teste de schema + `reachability_check` read-only
- part-4b — peso local (gc agora; fixados e `tmp/` gated)

## Anti-scope

- **Fronteira design × implementação:** o ai-eng especifica e decide em bifurcação; o medhub implementa e audita. O implementador não escreve no ai-eng; o ai-eng não escreve no medhub.
- Lotes 1–5 e P3 (só nomeados aqui), e a Fase 1 inteira: backend, banco servidor, React, deploy, CI de plataforma, `core.hooksPath`/hook versionado, job durável do tique.
- **Nada que mude conteúdo clínico** (`resumos/`, cards, questões, soluções), **FSRS** (`app/utils/fsrs*.py`, `record_review`, `fsrs_revlog`, parâmetros) **ou o hub publicado** (Artifact, `core/templates/hub.html`/`player.html`).
- Destino do RAG e da memória LangMem (`app/engine/rag.py`, `tools/eval/`, `app/memory/`): `AGENTE.md §6` cita `tools/eval/REPORT.md` como baseline do RAG — a decisão é do Lote 5.
- Módulos que [A] classificou MORTO mas que o repo declara de outra forma: `tools/calibrate_card_checks.py` e `tools/audit_fsrs.py` estão em `ISENTOS` do `reachability_check.py:75-77` como "ferramenta de mão"; `tools/backfill_review_log.py` é citado em `core/contracts/forgetting-curve-contract.md`, `AGENTE.md` e `engenharia-cli.md`. Ficam para o Lote 3 (contratos).
- `tools/_archive/migrations/` (13 migrações + README): `.agents/workflows/curar-cards.md:62` prescreve que migrações one-shot "movem para `tools/_archive/migrations/` após aplicadas", o que contradiz `AGENTE.md §3.4` ("sem `archive/`"). Apagar exige revogar a cláusula em 3 passos (`AGENTE.md §10.10`) — vai junto com as contradições de contrato do Lote 3.
- Classe 2 do P7 (≈35 funções que leem docs/registros vivos com valor fixo), exceto as 2 asserções que moram nos mesmos arquivos da classe 1 (part-2b) — Lote 3.
- Logs de sessão append-only (`history/exchange-log.jsonl`, `history/generation_log.jsonl`): são escritos por hooks de sessão e writers, não pelo commit — custo no histórico vai para o Lote 4/Fase 1.
- Reescrever o histórico do git.

## Technical Context

- **Runner:** `python -m pytest tools/ -q` com o Python 3.12.2 do sistema (pytest 9.0.1); o `.venv` não tem pytest. Coleta = 1509 testes em 105 arquivos ([E], `--collect-only`, 10/10); tempo da suíte ~210 s (número do orquestrador, não medido nesta redação).
- **Convenções do destino** (prevalecem): `.vibeflow/conventions.md` e `.vibeflow/index.md` do medhub — budget ≤ 6 arquivos por tarefa; teste novo entra no `python_files` do `pytest.ini` com parágrafo de justificativa; só `app/utils/db.py` importa `sqlite3` em `app/` (CLIs de `tools/` podem abrir conexão própria); sensores WARN-first detectam e não corrigem; skills: `.claude/commands/*.md` é a fonte, `.agents/skills/` é espelho gerado por `tools/sync_skills.py`; toda spec responde a pergunta F110 ("que fricção remove — virtuosa ou viciosa?").
- **Régua de execução** (`AGENTE.md §10.6–10.7`): teste escrito ANTES do fix, visto vermelho; COUNT-ASSERT + dry-run em toda operação mutadora; número citado só com o comando que o produziu. `§10.1`: reler o arquivo no disco antes de escrever (dois agentes editam o repo). `§10.4`: deletar é ato com raio (`git grep` do nome no repo e nos portadores de regra antes).
- **Hook:** `.git/hooks/pre-commit` = `HOOK_CONTENT` de `tools/setup_hooks.py:18-32` (fora do git) → `python -X utf8 tools/auto_check.py --staged`.
- **Conferido no código (6d0239a), com divergências dos relatórios:** ver a seção Context de cada parte. Principais: (i) o `--no-persist` literal no boot mataria a série planejado×real da `telemetria-estudo-part-1` (o boot é o único writer automático); (ii) "19 MORTOS + `_archive` (13)" conta o `_archive` duas vezes — são 6 módulos na árvore + 13 migrações (+ README); (iii) 2 dos 6 MORTOS são "ferramenta de mão" declarada; (iv) `tmp/` guarda estado vivo (`tmp/emed_figuras`, `tmp/hub`, `tmp/emed_api`), e os fixados são, por desenho (F137), nunca apagados por CLI.

## Open Questions

Perguntas fechadas ao operador (o default é o que as specs implementam se ele não responder):

- **Q1 (part-1).** O 1º boot de cada dia continua gravando o plano recomendado em `plano_dia` (a série planejado × real)? **(a) sim, só a 1ª abertura do dia grava; as seguintes nunca regravam** [default] · (b) não, o boot nunca grava; a série passa a depender de rodar `day_plan.py` à mão.
- **Q2 (part-4b).** Desfixar os backups fixados antigos, mantendo os 5 mais recentes, antes de existir backup fora desta máquina (Lote 4)? **(a) não, esperar o Lote 4** [default] · (b) sim, agora.
- **Q3 (part-4b).** Depois do inventário, apagar de `tmp/` só a classe SOLTO (sem referência em código nem em arquivo rastreado), com contagem conferida? **(a) sim** [default, executa só com o GO] · (b) não.

Decisões do arquiteto, não do operador (registradas para o Lote 3/5): destino de `calibrate_card_checks`, `audit_fsrs`, `backfill_review_log`; destino de `tools/eval/` junto com o RAG.
