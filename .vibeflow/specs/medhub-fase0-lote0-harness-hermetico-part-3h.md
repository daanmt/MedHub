# Spec: medhub Fase 0 · Lote 0 — Part 3h (hotfix): o BLOCK do check 29 passa a bloquear + git hermético na suíte

> Gerada: 2026-10-10 21:20 (medhub, s223) | Origem: audit da part-3 (`tmp/lote0/part-3-implement.md`, "Para auditar"); GO do ai-eng em 10/10 ~21:17 (`history/exchange-log.jsonl`, `in`), com o DoD abaixo ditado por ele.
> Ids: **M-122** (a) e **M-123** (b), ambos fecham no commit desta part. Membros novos da classe (DoD 5) -> **M-125**.
> Repo-alvo: medhub. HEAD de partida: `78d2e50`.

## Objective

O `[BLOCK]` que o check 29 imprime para `gate_inexistente`/`nv_sem_data` passa a barrar o commit, e a suíte, que roda dentro do pre-commit, deixa de herdar o ambiente `GIT_*` do commit em curso.

## Context

- **(a) BLOCK que ninguém alcança.** Em `tools/auto_check.py`, o ramo `if graves_clau:` do check 29 faz `clau_ok = False`, e o resumo final mostra `❌ FAILED`. Mas não faz `all_passed = False`, e o exit code sai de `all_passed` (`if all_passed: return 0`). Desde `9ea675a` (s187), uma anotação com gate inexistente ou sem data passa no commit com "Todos os checks passaram!". A catraca da part-3, logo abaixo, já faz `all_passed = False`: é o modelo.
- **(b) `GIT_INDEX_FILE` herdado.** Desde a part-1, a suíte roda em todo pre-commit. Em `git commit -a` / `git commit <caminhos>`, o git exporta para o hook um `GIT_INDEX_FILE` absoluto (o índice temporário do commit em curso). Um teste que roda `git -C <repo sintético> add` com esse ambiente escreveria no índice do repo real. Exposto hoje: `tools/test_emed_api.py` ~383 (`git add -f .emed_token`). Os testes da part-3 já se blindam com a fixture `git_isolado` (`tools/test_clausulas_check.py:188`), mas só eles.
- **Medido pelo orquestrador antes desta spec** (`python -B -X utf8 tools/clausulas_check.py --json` -> Counter dos `tipo`): `{'orfa': 127}`, ou seja, **0** `gate_inexistente` e **0** `nv_sem_data`. Ligar o bloqueio não trava nenhum commit seguinte.

## Definition of Done

1. [ ] **Medir antes de ligar.** O relatório traz a contagem de `gate_inexistente` e de `nv_sem_data` no **HEAD**, com o comando. Esperado: 0 e 0, e aí o fix é direto. Se der diferente, PARE e reporte sem ligar o bloqueio (1-5 = corrigir os dados no mesmo commit; > 5 = catraca "não sobe" + M-124; quem decide é o orquestrador).
2. [ ] **Fix (M-122).** No ramo `if graves_clau:`, `all_passed = False` (1 linha, com comentário curto citando o M-122 e o `9ea675a`). Regressão **in-process** em `tools/test_clausulas_check.py`: `auto_check.main()` com `run_checks` devolvendo um achado sintético `gate_inexistente` (e outro com `nv_sem_data`), por monkeypatch, sai **1**; sem achado grave, sai 0. Nada de commit em subprocesso dentro do teste (recursão do pre-commit, lição da part-1).
3. [ ] **Prova no fluxo real (do orquestrador, não do implementador).** Commit com um `<!-- CHECK: gate_que_nao_existe -->` sintético num portador é BLOQUEADO pelo pre-commit, com o HEAD intacto; depois o orquestrador reverte o portador e o espelho em `.agents/`.
4. [ ] **Git hermético na suíte (M-123).** Uma fixture `autouse`, de escopo `session`, no `conftest.py` da raiz remove `GIT_INDEX_FILE`, `GIT_DIR`, `GIT_WORK_TREE`, `GIT_PREFIX` e `GIT_OBJECT_DIRECTORY` do `os.environ` e restaura no teardown (`monkeypatch` é de função e não serve para escopo de sessão). Regressão empírica, sem hook:
   - **(i) reprodução:** um índice VÁLIDO como sentinela, num caminho absoluto em `tmp_path` (ex.: o `.git/index` de um 2º repo sintético depois de um `add`, copiado; um arquivo qualquer daria "index corrupt" e um falso "não reproduz"). Um subprocesso `git -C <repo A> add x`, com `env` explícito contendo `GIT_INDEX_FILE=<sentinela>`, muda ou não o md5 do sentinela? Registre o resultado, qualquer que seja.
   - **(ii) a defesa:** com o `os.environ` da suíte (fixture ativa), mesmo que o processo pai tenha `GIT_INDEX_FILE`, `git -C <repo A> add x` não toca o sentinela. Para simular o pai, ponha a variável no ambiente ANTES da fixture rodar, ou teste a função de limpeza da fixture diretamente.
   - Se (i) não reproduzir, (b) vira "limite conhecido: não reproduz" no relatório, e a fixture fica como defesa em profundidade.
5. [ ] **Inventário da classe (só leitura, no relatório).** Para cada `[BLOCK]` impresso em `tools/auto_check.py`: linha, tipo e se o caminho zera `all_passed` (sim/não, com a linha). Membro além do (a) -> listar como candidato a **M-125**; não consertar.

**Gerais:** `python -m pytest tools/ -q` verde; md5 do `ipub.db` real igual antes e depois; nada no índice nem no HEAD do repo real.

## Scope

`tools/auto_check.py` (só o ramo `if graves_clau:`), `conftest.py` (raiz), `tools/test_clausulas_check.py` e, se preciso, mais 1 arquivo de teste EXISTENTE (arquivo novo exige registro no `pytest.ini` e estoura o budget). **Budget: 4 arquivos.** A §7.4 do AGENTE.md, se acusar, é do orquestrador e fica fora do budget.

## Anti-scope

- Não mudar a regra de `gate_inexistente`/`nv_sem_data` (o que é BLOCK), a catraca da part-3, o check 26 nem outro `[BLOCK]` do inventário.
- Não mexer em `tools/test_emed_api.py`: a fixture de sessão já cobre o teste dele, e é isso que o DoD 4 prova.
- Nada clínico, nada de FSRS, nada no hub.

## Risks

- **Algum teste precisa do `GIT_INDEX_FILE` do pai?** Antes de ligar a fixture, `grep -rn "GIT_INDEX_FILE\|GIT_DIR\|GIT_WORK_TREE" tools/ app/ conftest.py`, e cite o resultado no relatório. Um teste que leia o índice do repo real dentro do pre-commit lê `.git/index` sem a variável: diga se algum depende disso.
- **Escopo `session` x `tmp_path`:** a fixture de sessão não recebe `tmp_path`; ela só limpa o ambiente. Quem cria o sentinela é o teste.
