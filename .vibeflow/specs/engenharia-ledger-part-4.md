# Spec: Engenharia Ledger — Part 4: Higiene SSOT (F10 + F12 + F11)

> Gerada via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/engenharia-ledger-f1-f13.md` (Onda 4)

## Objetivo

O SSOT declarado volta a ser verdadeiro: nenhuma página Streamlit fala SQL (F10), os testes rodam sob harness pytest sem perder a execução standalone (F12), e o expurgo do blob `ipub.db` do histórico git ganha runbook executável — gated pelo operador (F11).

## Contexto

`app/pages/1_dashboard.py:14` importa `sqlite3` e resolve `DB_PATH='ipub.db'` relativo ao cwd — bypassa a camada `db.py` (violação direta do pattern `db-access-layer.md`) e quebra silenciosamente se o Streamlit rodar de outro diretório. Os 4 `test_*.py` de `tools/` são scripts avulsos (sem pytest.ini/conftest); funcionam, mas não escalam com as ondas 1-3 adicionando lógica nova. `ipub.db` está gitignored hoje, porém persiste como blob no histórico até s058 (~1.6MB por clone, dado local-only versionado por engano).

## Definition of Done

1. [ ] `grep -r "import sqlite3" app/pages/` retorna vazio; `1_dashboard.py` consome exclusivamente funções de `app/utils/db.py` (criando lá a função de leitura que faltar), com path resolvido pela raiz do repo.
2. [ ] Dashboard renderiza os mesmos KPIs de antes (validação: valores idênticos para o mesmo `ipub.db` antes/depois da mudança).
3. [ ] `pytest` na raiz coleta e passa os 4 `test_*.py` de `tools/`; `python tools/test_X.py` (standalone) continua funcionando para os 4; `auto_check.py --all` continua verde sem editar seus comandos.
4. [ ] Runbook do expurgo F11 escrito em `docs/runbook-expurgo-ipub-git.md`: pré-condições (backup, sem clones divergentes), comando (`git filter-repo` ou equivalente), verificação pós (`git log --all -- ipub.db` vazio; clone fresco sem o blob), rollback. Marcado **GATED — executar somente com aval explícito do operador**. O expurgo NÃO é executado nesta entrega.
5. [ ] Craftsmanship: mudanças no dashboard seguem `db-access-layer.md` (retorno tipado, `conn.close()` explícito, SQL parametrizado, pós-processamento em Python) e `streamlit-page-structure.md` (inject_styles, cache_data ttl=60); zero violações dos Don'ts.

## Escopo

- `app/pages/1_dashboard.py` — remove sqlite3/path relativo; consome db.py.
- `app/utils/db.py` — função(ões) de leitura que o dashboard precisar e ainda não existam.
- `pytest.ini` (ou `[tool:pytest]` mínimo) — raiz; testpaths=tools, padrão `test_*.py`.
- `conftest.py` — raiz; garante `sys.path` do repo para `import app.utils...` sob pytest.
- `docs/runbook-expurgo-ipub-git.md` — runbook F11 (novo).

Budget: 5 arquivos (≤6 OK).

## Anti-escopo

- **NÃO executar o expurgo do histórico git** — runbook apenas; execução é Tier 3 do operador.
- Não converter os 4 testes para idioma pytest (fixtures/asserts) — só torná-los coletáveis; reescrita é ciclo futuro.
- Não adicionar testes novos além do mínimo para o DoD (cobertura ampla é outro projeto).
- Não tocar `2_estudo.py` tab1 (fallback sqlite3 legado documentado nas conventions — fora do escopo F10, que é o dashboard).
- Nenhum redesign do dashboard (mesmos KPIs, mesma UI).
- Não adicionar dependências novas (pytest já está no ambiente — verificar; se não estiver, entra em requirements.txt e isso é sinalizado no commit).

## Decisões Técnicas

1. **Dashboard via db.py com função dedicada** (ex.: `get_dashboard_kpis()`): mantém a página burra e a query testável. Trade-off: mais uma função em db.py (485 linhas) — aceitável; modularizar db.py é refactor futuro, não agora.
2. **Coletabilidade pytest com guarda `if __name__ == "__main__"`**: os scripts mantêm o main standalone; pytest coleta as funções `test_*` diretamente. conftest.py na raiz resolve o `sys.path.insert` que cada script faz hoje por conta própria.
3. **Runbook antes de execução (F11)**: reescrever histórico invalida clones — a operação precisa de janela coordenada; o runbook transforma decisão futura do operador em execução de 10 minutos sem re-investigação.
4. **`2_estudo.py` tab1 fica de fora**: as conventions já o documentam como legado tolerado ("last resort"); incluí-lo dobraria o risco da onda por um débito já cercado.

## Patterns Aplicáveis

- `db-access-layer.md` — o coração da onda (F10 é a correção de uma violação dele).
- `streamlit-page-structure.md` — estrutura da página preservada (tabs, inject_styles, cache).

## Riscos

- **Divergência de KPI pós-migração** (query nova ≠ query antiga) → mitigação: DoD 2 exige igualdade de valores; migrar a query literal, não "melhorá-la".
- **pytest colidir com side-effects dos scripts** (prints, sys.path hacks) → mitigação: conftest centraliza path; se um teste não for coletável sem refactor invasivo, marcar com nota e coletar os demais (DoD ajustado é sinalizado no audit, não silenciado).
- **Runbook F11 executado por engano** → mitigação: título GATED em caixa alta no topo, sem one-liner copiável de execução direta (passos exigem confirmação manual).

## Dependencies

- Nenhuma — independente das ondas 1-3 (pode rodar em paralelo, mas a série mantém a ordem do PRD).
