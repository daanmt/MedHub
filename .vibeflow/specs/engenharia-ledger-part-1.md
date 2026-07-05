# Spec: Engenharia Ledger — Part 1: Integridade de Estado (F1 + F6 + F13)

> Gerada via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/engenharia-ledger-f1-f13.md` (Onda 1)

## Objetivo

Todo invariante de estado da camada de governança vira verificação executável e todo número do HANDOFF vira derivado da fonte viva — o drift de ponteiro (F1) e o drift numérico (F6) ficam impossíveis de passar despercebidos, e o boot determinístico sobrevive a um clone (F13).

## Contexto

O ponteiro de sessão do HANDOFF avançou sem log correspondente (s108) e nada barrou; três números do HANDOFF divergiram da fonte viva na mesma sessão. O `auto_check.py` já orquestra linter + testes + paridade com política WARN→BLOCK (s106/107), mas não conhece a invariante de ponteiro. O `day_plan.py` já computa todos os números (read-only), mas não emite o bloco pronto para o HANDOFF. Os hooks de SessionStart/PostToolUse vivem só em `.claude/settings.local.json` (não versionado, paths absolutos da máquina).

## Definition of Done

1. [ ] `python tools/auto_check.py --all` com HANDOFF apontando sessão N tal que N > max(history/session_*.md)+1 emite WARN nomeado (`SESSION_POINTER_DRIFT`); com ponteiro coerente, nenhum WARN. O check também roda em `--changed`/`--staged` quando HANDOFF.md ou history/ estão no diff. Nasce WARN — **não** rebaixa o veredito (política s106/107).
2. [ ] `python tools/day_plan.py --handoff-block` imprime bloco ASCII pronto para colar no "Estado por frente" do HANDOFF: volume acumulado, perf %, FSRS (atrasados/hoje/backlog novos), ritmo-alvo. Números idênticos aos de `day_plan.py --json` na mesma execução.
3. [ ] Hooks SessionStart/PostToolUse declarados em `.claude/settings.json` (versionado) com paths relativos ao repo (`$CLAUDE_PROJECT_DIR` ou relativo); `settings.local.json` retém apenas permissões/paths específicos da máquina. Comportamento de boot idêntico ao atual.
4. [ ] `day_plan.py` permanece estritamente read-only (nenhum write em db ou arquivos) e `auto_check.py --all` continua verde após as mudanças.
5. [ ] Craftsmanship: zero violações dos Don'ts de `conventions.md`; CLIs com argparse e stdout legível (padrão tools/); nenhum `import sqlite3` novo fora de `db.py`; docs de governança tocados mantêm ASCII limpo (AGENTE.md §4.5).

## Escopo

- `tools/auto_check.py` — nova função de invariante de ponteiro (parse do header do HANDOFF + glob de history/session_*.md, incluindo legacy/) integrada ao relatório final como WARN.
- `tools/day_plan.py` — flag `--handoff-block` (reusa `build()`; zero lógica nova de dados).
- `.claude/settings.json` — criado, com os 2 hooks migrados (paths portáveis).
- `.claude/settings.local.json` — hooks removidos (ficam permissões locais).
- `AGENTE.md` — 2 linhas no Protocolo de Fechamento: passo 1 usa `day_plan --handoff-block` para os números; invariante de ponteiro documentada.
- `HANDOFF.md` — bloco numérico regenerado uma vez via a flag nova (validação de ponta a ponta).

Budget: 6 arquivos (teto do index.md).

## Anti-escopo

- Nenhum BLOCK — a invariante nasce WARN e só endurece em ciclo futuro quando a base zerar.
- Nenhuma mudança no schema do HANDOFF além do bloco numérico (texto qualitativo continua manual).
- Nenhum hook novo — só migração dos 2 existentes.
- Não tocar `fsrs_queue.py`, contratos de `/revisar`, dashboard (ondas 2-4).
- Não reescrever `_cronograma_hint`/legados do day_plan.

## Decisões Técnicas

1. **Parse do ponteiro**: regex sobre a linha de título/"Próximo passo" do HANDOFF capturando `s(\d{2,3})`; ponteiro = maior N citado como sessão corrente/próxima. Trade-off: regex é frágil a reformatação, mas o HANDOFF tem formato estável e o custo de um parser formal não se justifica; falha de parse = check silencioso (nunca falso-positivo barulhento).
2. **Invariante**: `ponteiro <= max_session + 1` (renumeração antecipada de +1 é legítima — foi o caso real da s107→s108). Acima disso, WARN.
3. **`--handoff-block` reusa `build()`**: nenhuma query nova; formatação ASCII pura. Mantém day_plan como fonte única derivada (anti-duplicação).
4. **F13 com `$CLAUDE_PROJECT_DIR`**: paths de hook portáveis entre máquinas/clones; fallback relativo se a variável não estiver disponível na versão do harness. `settings.local.json` não é deletado — só esvaziado de hooks.

## Patterns Aplicáveis

- `agent-workflow-protocol.md` — o fechamento passa a referenciar o bloco derivado; invariante protege o passo 3 (registrar sessão).
- `db-access-layer.md` — nenhuma nova superfície SQL; day_plan continua consumindo `db.get_connection()`/funções existentes.

## Riscos

- **Regex do HANDOFF quebra com reformatação futura** → mitigação: parse defensivo (sem match = check silencioso + nota no output verbose), e o formato do header está documentado no AGENTE.md.
- **Hooks migrados não dispararem no harness local** → mitigação: testar boot real após migração (SessionStart imprime plano do dia — visível imediatamente); rollback = restaurar settings.local.json (1 arquivo).
- **`--handoff-block` divergir do render humano** → mitigação: DoD exige igualdade com `--json` na mesma execução; ambos derivam de `build()`.

## Dependencies

Nenhuma — é a primeira da série.
