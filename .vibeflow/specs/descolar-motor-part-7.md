# Spec: Descolar part-7 — portadores: regra load-bearing viaja com o repo (F57 · F59 · P7)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.
> O achado-tese com caso provado: a s156 (Antigravity) deletou o alvo de uma memória-CONTRATO
> que ela não via (F57→F50). Distinção-instrumento: docs elevam o teto do modelo fraco;
> schemas/gates limitam o dano — e memória de harness não faz NENHUM dos dois p/ outra IDE.

## Objective

Nenhuma regra load-bearing vive só na memória do harness Claude Code: as 5 memórias nomeadas são
resolvidas (migrar/indexar/deletar), o detector de ponteiro-morto passa a rodar, as permissões
ganham piso de segurança, e a disciplina de co-edição vira texto versionado.

## Context

77 memórias em `~/.claude/projects/C--Users-daanm-medhub/memory/` (51 `feedback_*`) — 100%
decorativas p/ outros harness e não-versionadas (matriz de portadores, linha 11). Handoff §6:
únicas que valem leitura direta = `feedback_aula_base_artifact_design_contract` (aponta o morto
`autopsia_template.py`), `feedback_fsrs_override_autoconfirm` + `project_semantic_architecture`
(FORA do índice MEMORY.md — uma regra ativa invisível, uma morta de s044),
`feedback_politica_cards_diaria` (modelo de memória-que-encolheu-certo) e
`project_aieng_mudancas_estruturais` (ponteiro morto p/ `reflect.py` — do próprio ai-eng).
F59: `settings.local.json` com 166 allow / 0 deny; ~40% lixo one-shot.

## Definition of Done

1. [ ] As 5 memórias nomeadas resolvidas: (a) `aula_base_artifact_design_contract` → a regra de
       design migra p/ portador repo (skill/contrato de aula-base) e a memória vira ponteiro;
       (b) `fsrs_override_autoconfirm` → regra migra p/ a skill `/revisar` versionada + entra no
       índice MEMORY.md como ponteiro; (c) `project_semantic_architecture` (morta s044) DELETADA;
       (d) `project_aieng_mudancas_estruturais` → ponteiro morto de `reflect.py` corrigido
       (protocolo de co-edição referencia o portador novo do item 4); (e) `politica_cards_diaria`
       fica (modelo certo — encolheu p/ o porquê).
2. [ ] `relearning_intrasessao` (conduta do /revisar que prosa já falhou 3×): o PASSO entra
       versionado na skill `/revisar` (portador certo); a mecanização (fila de redrill em código)
       é registrada como candidata no painel — NÃO implementada aqui (escopo).
3. [ ] Check `memory_pointers` no auto_check (WARN): paths `tools/*.py`/`app/*.py` citados em
       `memory/*.md` × disco — ponteiro morto nomeado (o detector que teria pego F57 na hora).
       (O check lê o dir de memória FORA do repo; ausente/inacessível = silêncio honesto.)
4. [ ] Disciplina de co-edição (P7) vira seção curta do `AGENTE.md` (dois agentes no repo:
       reler HANDOFF/ESTADO antes de escrever; preservar blocos alheios; quem edita skill roda
       sync_skills) — a memória correspondente vira ponteiro.
5. [ ] `settings.local.json`: bloco `deny` mínimo (rm -rf, git reset --hard, git clean -f,
       git push --force) + poda das entradas que citam arquivos/dirs inexistentes (mecânico);
       contagem antes/depois registrada no commit.
6. [ ] Suite verde; `sync_skills` rodado e `--check` exit 0 (skills editadas); craftsmanship:
       espelhos intocados à mão; skills em pt-BR.

## Scope

`~/.claude/projects/C--Users-daanm-medhub/memory/` (5 arquivos + MEMORY.md) · `.claude/commands/`
(revisar + aula-base) · `AGENTE.md` · `tools/auto_check.py` · `.claude/settings.local.json` (≤6
grupos; memória conta como 1 grupo fora-do-repo).

## Anti-scope

- Migração em massa das 77 (as famílias têm veredito no PRD; a execução além das 5 nomeadas =
  próximas sessões, com o check do item 3 vigiando).
- Fila de redrill em código (candidata registrada; ciclo 2).
- Qualquer conteúdo clínico das memórias (só portador/engenharia).

## Applicable Patterns

- `agent-workflow-protocol.md` · `warn-first-check.md` (check de ponteiros = sensor).

## Risks

- Editar skill dispara re-sync dos espelhos → rodar `sync_skills` no MESMO commit (DoD-6).
- Deny-list pode barrar operação legítima futura → lista mínima e nomeada; ampliar é 1 linha.

## References

- `ai-eng/HANDOFF-MEDHUB-COLA.md` §6 (triagem das 77 — NÃO reler uma a uma) · §4 F57/F59.
