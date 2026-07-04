---
type: spec
projeto: MedHub
feature: autogovernanca-proativa
part: 3
slug: autogovernanca-proativa-part-3
status: ready
relates_to:
  - .vibeflow/prds/autogovernanca-proativa.md
  - .claude/commands/
  - .agents/skills/
  - tools/auto_check.py
---

# Spec -- Autogovernança Proativa - Parte 3: Paridade Multi-Agente (R4)

> Deriva de `.vibeflow/prds/autogovernanca-proativa.md` (R4). Elege uma fonte canônica única para as skills e gera os espelhos, acabando com o drift silencioso entre Claude e Codex.

## Objective
Fazer `.claude/commands/` ser a fonte canônica única das skills e gerar os espelhos `.agents/skills/` por script, com o `auto_check` acusando quando alguém edita o canônico sem regenerar.

## Context
As skills existem em duas superfícies: `.claude/commands/*.md` (11 arquivos) e `.agents/skills/source-command-*/SKILL.md` (10 espelhos). A migração foi "corpo copiado + frontmatter reescrito + wrapper de 3 linhas", e o drift **já se materializou nas duas direções**: `source-command-revisar` está stale (pré-s096, sem os sub-modos PREPARAR/DRENAR -- o Codex operaria o modelo de revisão errado), enquanto `source-command-estilo-resumo` está À FRENTE do canônico (ganhou "Deep-Researchness em Resumos D10" + a seção "Autoverificação Obrigatória" que o `.claude/commands/estilo-resumo.md` não tem). E `cronograma` nunca foi migrado (11 commands x 10 skills). Sem gerador, a regra clínica diverge silenciosamente entre harnesses.

## Definition of Done
1. **Gerador `tools/sync_skills.py`:** produz cada `.agents/skills/source-command-<x>/SKILL.md` a partir de `.claude/commands/<x>.md` (frontmatter de agent-skill: `name`+`description`; wrapper "# source-command-<x>" + nota "Use this skill when the user asks to run the migrated source command <x>." + "## Command Template"; depois o corpo verbatim do command). Cobre **todas** as skills, incluindo `cronograma` (que faltava).
2. **Pré-sync sem perda:** antes de gerar, as adições que só existem no espelho `estilo-resumo` (bullet "Deep-Researchness em Resumos D10 / Extensivo" + seção "Autoverificação Obrigatória") são portadas para o canônico `.claude/commands/estilo-resumo.md`. Depois do sync, nenhum conteúdo dessas adições se perde (verificável por grep no espelho gerado).
3. **`revisar` deixa de estar stale:** após rodar o sync, `.agents/skills/source-command-revisar/SKILL.md` contém "PREPARAR" e "DRENAR" (herdados do canônico s096).
4. **Check de drift no `auto_check`:** rodar `auto_check` com um `.claude/commands/*.md` editado e o espelho não-regenerado emite **WARN de paridade** nomeando o(s) arquivo(s) fora de sync (comparação canônico↔corpo-do-espelho). Não bloqueia (warning-first).
5. **Craftsmanship -- idempotência e fonte única:** rodar `python tools/sync_skills.py` duas vezes seguidas deixa `git diff` vazio na segunda; o script não introduz duplicação semântica além do wrapper (o corpo é cópia verbatim); nenhuma edição manual nos `SKILL.md` gerados (eles passam a ser artefato de build).

## Scope
- `tools/sync_skills.py` (NOVO): gerador determinístico command -> SKILL.md; flag `--check` (retorna não-zero se algum espelho está fora de sync, para o auto_check consumir) e modo default (regenera).
- `.claude/commands/estilo-resumo.md`: recebe as adições portadas do espelho (Deep-Researchness + Autoverificação) -- pré-sync.
- `tools/auto_check.py`: chama `sync_skills.py --check` e reporta drift de paridade como WARN.
- `.agents/skills/source-command-*/SKILL.md` (+ `source-command-cronograma/` novo): **saída gerada** pelo script (não editada à mão).

## Anti-scope
- **Sem** inverter a fonte para `.agents/skills` (a decisão do usuário é `.claude/commands` canônica).
- **Sem** deletar `.agents/skills` (a intenção agent-agnostic é mantida; vira saída gerada).
- **Sem** sincronizar `.codex/agents/evidence-researcher.toml` (gêmeo Codex da skill `pesquisar-evidencia`) -- fica como nota de manutenção manual (anti-scope explícito do PRD).
- **Sem** promover o WARN de paridade a BLOCK.

## Technical Decisions
- **Command -> SKILL.md (não o inverso):** `.claude/commands` é onde as skills reais do agente primário (Claude Code) vivem e evoluem; gerar o espelho agent-agnostic a partir dele minimiza churn e corrige o `revisar` stale na primeira execução.
- **`--check` no próprio gerador, consumido pelo auto_check:** mantém a regra de paridade em UM lugar (o gerador sabe o que "em sync" significa); o auto_check só orquestra -- espelha a disciplina "cada CLI tem assinatura canônica em UMA skill" do AGENTE.md §7.2.
- **Comparar corpo, não bytes:** o espelho tem frontmatter + wrapper diferentes por construção; o check compara o **corpo** (pós-wrapper) do espelho com o corpo do command, ignorando o frontmatter/wrapper esperados.
- **Espelhos como build artifact:** commitados (para o Codex consumir sem rodar o gerador), mas nunca editados à mão -- o `--check` é a rede que pega edição manual.

## Applicable Patterns
- `agent-workflow-protocol.md` + AGENTE.md §7.2 ("cada CLI tem assinatura canônica em UMA skill; workflows referenciam, não copiam") -- esta parte estende o mesmo princípio para o par command↔skill.

## Risks
- **Divergência de frontmatter entre harnesses** (agent-skill quer `name`; command quer `type`/`layer`) -> mitigação: o gerador é a única autoridade sobre o frontmatter do espelho; o `--check` ignora frontmatter.
- **Portar as adições de `estilo-resumo` pode conflitar com a estrutura do canônico** -> mitigação: inserir as seções em pontos claros (fim do corpo), fora de marcadores auto-gerados, e validar por grep no DoD-2.
- **Alguém edita o SKILL.md à mão e o sync sobrescreve** -> mitigação: o `--check` no auto_check acusa a divergência ANTES do commit (WARN), sinalizando "edite o command, não o espelho".

## Dependencies
Nenhuma para implementar. (Toca `tools/auto_check.py`, assim como a Parte 2 -- coordenar a ordem de merge para evitar conflito textual, mas são hunks distintos: Parte 2 = apresentação WARN/BLOCK; Parte 3 = chamada ao `sync_skills --check`.)
