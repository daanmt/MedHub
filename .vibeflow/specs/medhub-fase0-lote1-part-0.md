# Spec: medhub Fase 0 · Lote 1 — Part 1.0: RAG/Chroma e LangMem fora do caminho crítico (medir antes)

> Gerada: 2026-10-11 ~01:00 (medhub, s223, `/vibeflow:gen-spec`) | Origem: decisão i do operador (10/10, no canal do ai-eng: "RAG/LangMem fora do caminho crítico SIM") e o GO do Lote 1 do ai-eng (10/10 23:32): "1º DoD é MEDIR antes de desligar (tempo de boot e tamanho do que os hooks injetam, com e sem) — é a baseline que o Lote 5 vai querer e que some depois; hooks/boot deixam de chamá-los; dados ficam; teste que o boot não importa os módulos".
> Repo-alvo: medhub. HEAD de partida: `5a968ec`.

## Objective

Abrir sessão e escrever o log de sessão deixam de depender de LangGraph, LangMem, Chroma e da API: o boot não importa esses módulos e nenhum hook dispara a consolidação. Os dados e o código continuam no disco, e o custo de antes fica medido como baseline do Lote 5.

## Context

Lido no código em 11/10 (só leitura):
- **Boot (`SessionStart` -> `tools/hooks/memory_boot.py`):** `_memory_context()` importa `app.memory.inspect.load_context` -> `app/memory/store.py`, que importa `langgraph.store.base` no topo. Ou seja, todo boot carrega LangGraph para injetar o bloco "Áreas de fraqueza persistentes (top 8)", lido do `medhub_memory.db`.
- **`PostToolUse(Write)` -> `tools/hooks/memory_session_log.py`:** a cada `history/session_NNN.md` escrito, dispara em background (`DETACHED_PROCESS`) `python -m app.memory.manager NNN`. A consolidação usa LangMem + `claude-haiku-4-5` quando há `ANTHROPIC_API_KEY`; sem a chave, só o sync de `error_count` roda (`AGENTE.md §8`). O `history/memory_errors.log` tem **1460 linhas de falha**, a última de 11/09 (`wa_vocab/sink FileNotFoundError`): o caminho falha calado há um mês.
- **RAG no boot:** o `memory_boot` roda o `tools/day_plan.py`, que importa `app.engine.get_topic_context` em dois pontos (`~651`, `~724`), só para o `_find_resumo` (resolver de arquivo). Esse módulo importa só `app.utils.db` no topo, e o `rag.py` (que importa `chromadb`) entra preguiçoso. Hipótese a CONFIRMAR pela medição: o Chroma não está no caminho do boot.
- **Quem lê o que o boot injeta:** o agente, não o operador. O contrato do boot (`memory_boot._CONTRATO`, preso por `test_boot_entrega_o_panorama`) é Plano do Dia + Panorama. As Áreas de fraqueza não fazem parte dele.
- Citam o bloco ou a consolidação: `AGENTE.md` (§2 passo 7, §8), `core/contracts/forgetting-curve-contract.md`, `tools/test_boot_verdadeiro.py`, `tools/test_memory.py`, `tools/test_memory_counter.py` e `tools/test_plano_dia.py`.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: cada boot paga o import de uma dependência pesada para injetar um bloco que vai envelhecer, e cada selo de sessão dispara um processo que falha calado. Nenhuma fricção de estudo é tocada.

## Definition of Done

1. [ ] **MEDIR ANTES, sem escrever no banco real.** `tmp/lote1/part-0-baseline.md` traz, com o comando de cada número:
   - (a) tempo de parede do boot (mediana de 5);
   - (b) bytes e linhas do `additionalContext` injetado, no total e só no bloco de Áreas de fraqueza;
   - (c) `python -X importtime` do boot: se `langgraph`, `langmem`, `chromadb`, `ollama` e `anthropic` entram, e o tempo cumulativo de cada um;
   - (d) o hook `PostToolUse(Write)`: tempo e se dispara a consolidação; mais a contagem de linhas do `memory_errors.log`.
   Desde a part-1, o boot grava o plano na 1ª abertura do dia, então a medição NÃO pode rodar o boot contra o `ipub.db` real se isso gravar. Meça sobre o banco sintético (`db.DB_PATH` repontado) ou meça as peças em separado (`_memory_context()` em processo, `day_plan.py --no-persist`, `-X importtime -c "import app.memory.inspect"`). O md5 do `ipub.db` e o do `medhub_memory.db` ficam iguais. As mesmas medidas DEPOIS, lado a lado no relatório.
2. [ ] **O boot não importa os módulos.** Novo teste em `tools/test_boot_verdadeiro.py` (arquivo existente), visto VERMELHO antes do fix: depois de rodar o caminho do boot (o `memory_boot` sobre banco sintético, em subprocesso com `-X importtime` ou com inspeção de `sys.modules`), nenhum de `langgraph`, `langmem`, `chromadb`, `app.memory` ou `app.engine.rag` foi carregado.
3. [ ] **O bloco de Áreas de fraqueza sai do boot** (default; ver TODO). O `memory_boot` deixa de chamar o `_memory_context()`, e o panorama e o Plano do Dia ficam intactos (`test_boot_entrega_o_panorama` verde). O bloco continua sob demanda: `python -m app.memory.inspect --context`. <!-- TODO(ai-eng/operador): (a) sai do boot [default: sem a consolidação, os dados envelhecem, e injetar fraqueza congelada como "persistente" engana o agente; o contrato do panorama não inclui o bloco] · (b) fica com leitor sqlite em mode=ro, sem LangGraph, e a data da última consolidação no cabeçalho -->
4. [ ] **Nenhum hook dispara a consolidação.** Sai de `.claude/settings.json` só a entrada `PostToolUse` matcher `Write` -> `memory_session_log.py`. `SessionStart` e `PostToolUse` matcher `SendMessage` -> `exchange_log.py` ficam iguais. Teste: os hooks do `settings.json` não citam `memory_session_log`, e os outros dois continuam lá. O script e o `app/memory/` ficam no disco, e a consolidação segue chamável à mão (`python -m app.memory.manager NNN`).
5. [ ] **Os dados ficam.** `medhub_memory.db`, `data/chroma/`, `app/memory/` e `app/engine/` sem nenhuma mudança: `git diff --stat` não os lista, e o md5 do `medhub_memory.db` fica igual. Nenhum `pip uninstall`; `requirements.txt` intocado (as deps mortas são Lote 3/Fase 1).
6. [ ] **Norma lida no ato acompanha.**
   - `AGENTE.md §2` passo 7 e `§8`: o bloco deixa de ser carregado pelo boot, e a consolidação passa a ser manual; o resto do modelo de memória fica.
   - `core/contracts/forgetting-curve-contract.md`: onde ele prescreve o hook ou o bloco no boot.
   - Cláusula prescritiva revogada segue o §10.10 nos 3 passos e no mesmo commit (declarar, lapidar no portador com `⚰️` + data + motivo, cadastrar o termo em `_TERMOS_REVOGADOS` do `tools/auto_check.py`). Os testes que citam o bloco (`test_memory`, `test_memory_counter`, `test_plano_dia`) são conferidos um a um; o que testa o MÓDULO (`app.memory`) fica, e o que testava o BOOT muda.
7. [ ] **Suíte e craftsmanship:** `python -m pytest tools/ -q` verde, `python tools/sync_skills.py --check` exit 0 (se alguma skill citar o bloco), e nenhuma violação dos Don'ts de `.vibeflow/conventions.md`. A §7.4 do `AGENTE.md`, se acusar, é regenerada pelo orquestrador, fora do budget.

## Scope

`tools/hooks/memory_boot.py`, `.claude/settings.json` (só a entrada do `memory_session_log`), `tools/test_boot_verdadeiro.py`, `AGENTE.md` (§2 passo 7 e §8), `core/contracts/forgetting-curve-contract.md` e `tools/auto_check.py` (só `_TERMOS_REVOGADOS`, se houver revogação). **Budget: 6 arquivos.** Se os testes de `test_memory`/`test_memory_counter`/`test_plano_dia` precisarem mudar e estourar o budget, PARE e reporte a divisão (1.0a = medir + boot; 1.0b = hook + normas), em vez de passar do limite.

## Anti-scope

- Não apagar `medhub_memory.db`, `data/chroma/`, `app/memory/`, `app/engine/rag.py`, `tools/hooks/memory_session_log.py` nem `tools/index_resumos.py`. O "fica ou morre" deles é do Lote 5 (com a baseline desta part) ou do Lote 3.
- Não mexer no RAG sob demanda: `get_topic_context()`, a degradação F91 e as skills que o usam (`/aula-base`, Revisão Direcionada) continuam iguais.
- Não mexer no check `RAG_STALE` do `auto_check` (só lê carimbo; é WARN).
- Não tocar `requirements.txt`, `.mcp.json` nem permissões do `settings.json`.
- Não mudar o Plano do Dia, o panorama nem o `_CONTRATO` do boot.

## Technical Decisions

1. **Medir antes e depois sobre peças, não sobre o boot real.** O boot real grava `plano_dia` na 1ª abertura do dia (part-1); medir contra o banco real mudaria o estado que se mede. Custo: a medida do boot inteiro é feita sobre banco sintético e pode subestimar o I/O real. Fica declarado no relatório.
2. **Tirar o bloco em vez de trocar o leitor (default a).** Sem a consolidação, o `weak_areas` congela: um leitor sem LangGraph manteria o import fora do boot, mas injetaria dado envelhecendo como "persistente". O caminho (b) segue aberto via TODO.
3. **Remover a entrada do hook no `settings.json`, em vez de deixar um no-op no script.** O hook deixa de rodar, e o script fica chamável à mão. Um no-op seria código vivo que não faz nada, a classe que o Lote 0 acabou de limpar.

## Applicable Patterns

- Lote 0 part-2a/2c: banco sintético + sentinela que recusa o `ipub.db` real nos testes.
- `AGENTE.md §10.10`: revogação em 3 passos no mesmo commit (F90).
- `.vibeflow/patterns/agent-workflow-protocol.md`: o boot pelo `AGENTE.md §2`.

## Risks

- **"Um teste ou skill depende do bloco no boot."** -> O DoD 6 confere os 4 testes e as normas; se estourar o budget, a part se divide (Scope).
- **"A medição do boot grava no banco real."** -> Decisão Técnica 1 + md5 antes e depois.
- **"Editar `.claude/settings.json` passa pelo classificador."** -> É caminho protegido. Se a edição for negada, PARE e reporte: o operador aplica a remoção da entrada; não contornar.
- **"Alguém sente falta do bloco."** -> `python -m app.memory.inspect --context` continua; o TODO (b) volta com o bloco sem LangGraph.

## References

- `tools/hooks/memory_boot.py` (`_memory_context`, `_CONTRATO`) e `tools/hooks/memory_session_log.py`: o caminho de hoje.
- `app/memory/store.py:18` (`from langgraph.store.base import ...`): o import que entra no boot.
- `history/memory_errors.log` (1460 linhas): baseline de falha do caminho de consolidação.
