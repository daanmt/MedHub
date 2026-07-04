---
type: spec
projeto: MedHub
feature: autogovernanca-proativa
part: 1
slug: autogovernanca-proativa-part-1
status: ready
relates_to:
  - .vibeflow/prds/autogovernanca-proativa.md
  - app/memory/inspect.py
  - tools/hooks/memory_boot.py
  - app/memory/manager.py
---

# Spec -- Autogovernança Proativa - Parte 1: Âncora de Fraquezas + Boot Determinístico (R1+R2)

> Deriva de `.vibeflow/prds/autogovernanca-proativa.md` (R1, R2). É a fatia de maior valor: devolve ao agente a ancoragem em fraquezas/metas logo na abertura, sem input do usuário.

## Objective
Fazer o boot da sessão injetar automaticamente as fraquezas REAIS do usuário + um plano do dia compacto + o próximo passo, e abrir oferecendo o próximo ato -- em vez dos 20 placeholders `[? / ?]` de hoje.

## Context
`app/memory/inspect.py::load_context()` (linhas 157-167) lê chaves planas (`v.get('area')`, `v.get('pattern')`, e o mesmo em `workflow_rules`), mas o LangMem grava cada memória num **envelope** `{"kind":"WeakArea","content":{...}}` (confirmado: 175/175 registros de `medhub/weak_areas` têm topo `['kind','content']`; `app/memory/manager.py:113-115` já lê aninhado -- o formato canônico é o aninhado). Resultado: todo registro renderiza `[? / ?]`. O hook `tools/hooks/memory_boot.py` apenas redireciona o stdout de `load_context()` para o `additionalContext` do SessionStart -- então a âncora de fraquezas está muda desde ~s084. Além disso o boot proativo (AGENTE.md §2.4: day_plan + próximo passo) depende de o agente lembrar de rodar -- não é mecânico.

## Definition of Done
1. **Unwrap do envelope:** `python -m app.memory.inspect --context` contra o `medhub_memory.db` atual renderiza cada fraqueza como `[area / especialidade] pattern` com valores reais e **zero ocorrências de `[? / ?]`**. O mesmo unwrap é aplicado ao bloco `workflow_rules` (mesmo bug latente nas linhas 165-167). Defensivo: `v = item.value.get("content", item.value)` (cai para plano se algum dia vier flat).
2. **Dedup + ranking read-side:** no máximo 1 linha por par `(area, especialidade)`; ordenado por `error_count` desc, depois `last_updated` desc; exibe top-N (N=8). Rodar 2x seguidas produz a mesma ordem (determinístico).
3. **Boot compacto (memory_boot.py v2):** o `additionalContext` do SessionStart passa a conter, além das fraquezas top-N: (a) resumo do `tools/day_plan.py` (<=8 linhas) obtido por subprocess com **timeout <=8s + fallback silencioso** se falhar/faltar `fsrs`; (b) **flag de drift** comparando a sessão citada no `HANDOFF.md` com o maior `history/session_NNN.md`; (c) o "Próximo passo imediato" lido do `HANDOFF.md`.
4. **Texto-contrato Presença->Expansão:** o bloco injetado termina com uma instrução curta e fixa mandando o agente **abrir oferecendo o próximo ato** ("Próximo ato: X -- sigo nele salvo redireção") e devolver o turno, sem executar a sessão inteira na abertura.
5. **Craftsmanship -- disciplina de acesso e testes:** nenhum `import sqlite3` novo fora de `app/memory/store.py` (segue `db-access-layer` e `agent-workflow-protocol`); nenhum crash quando `medhub_memory.db` não existe (mantém o `except FileNotFoundError` do hook); smoke test novo em `tools/test_memory.py` valida o unwrap sobre um store temporário com 1 registro-envelope e assere ausência de `[? / ?]`. `python tools/test_memory.py` verde.

## Scope
- `app/memory/inspect.py`: `load_context()` -- unwrap do envelope nos blocos `weak_areas` e `workflow_rules`; dedup por `(area, especialidade)`; ordenação por `error_count`/`last_updated`; top-N=8.
- `tools/hooks/memory_boot.py`: v2 com injeção compacta (fraquezas + day_plan resumido via subprocess/timeout + flag de drift + próximo passo do HANDOFF) + texto-contrato Presença->Expansão.
- `tools/test_memory.py`: smoke test do unwrap (store temporário; zero `[? / ?]`).

## Anti-scope
- **Sem** dedup/consolidação write-side do namespace (o namespace incha com keys UUID -- R1b, fora desta parte; só read-side aqui).
- **Sem** novo backend de memória; LangMem + SQLiteMemoryStore permanecem.
- **Sem** tocar `.claude/settings.local.json`/`.codex/hooks.json` (ambos já apontam para `memory_boot.py`; o mesmo script serve os dois harnesses).
- **Sem** reescrever `day_plan.py` (é consumido as-is por subprocess; seus defeitos de conteúdo são da Parte 4).
- **Sem** auto-executar a sessão na abertura (a fronteira humana da §1.1(c) permanece -- o boot OFERECE, não decide sozinho).

## Technical Decisions
- **Unwrap defensivo (`content` -> fallback plano)** em vez de assumir o envelope: sobrevive a registros legados eventualmente planos e à evolução do schema do LangMem. Trade-off: 1 `.get` extra por registro -- irrelevante.
- **day_plan por subprocess com timeout, não import direto:** isola o hook de qualquer exceção/lentidão de `day_plan` (que importa `app.utils.db` -> `fsrs`); fallback silencioso mantém o boot resiliente ("ASSUME INTERRUPTION" do ai-eng). Import direto acoplaria o boot à saúde do FSRS.
- **Drift como flag textual, não bloqueio:** o boot só sinaliza a divergência HANDOFF↔session_NNN; resolver é decisão do agente/usuário (o reconcile continua sendo o mecanismo formal). Evita boot que "sequestra" a abertura.
- **top-N=8** casa o teto visual do bloco de fraquezas do hook atual (20 linhas) sem inflar o contexto de toda sessão.

## Applicable Patterns
- `agent-workflow-protocol.md` -- boot é o passo canônico; o texto-contrato reforça a sequência sem duplicar a doutrina do AGENTE.md.
- `db-access-layer.md` -- acesso a `medhub_memory.db` só via `app/memory/store.py` (nunca `sqlite3` cru no inspect/hook).

## Risks
- **day_plan lento/quebrado trava o boot** -> mitigação: timeout <=8s + fallback silencioso (o boot nunca depende do day_plan).
- **medhub_memory.db ausente numa máquina nova** -> mitigação: o `except FileNotFoundError` do hook já cobre; o smoke test cobre o caminho vazio.
- **`error_count` uniforme em 241 (agregado global, não por área -- achado da revisão)** torna o ranking por `error_count` pouco discriminante -> mitigação: desempate por `last_updated`; a correção do `error_count` por área é write-side (R1b, fora do escopo) e fica como TODO no código.

## Dependencies
Nenhuma. É a primeira parte e a de maior prioridade.
