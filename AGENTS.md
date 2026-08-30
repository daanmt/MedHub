---
type: onboarding
layer: root
status: canonical
relates_to: [AGENTE]
---

# AGENTS.md

Leia [`AGENTE.md`](AGENTE.md) antes de qualquer ação. Convenções, workflows, skills, scripts e arquitetura de memória estão lá.

Este arquivo existe para ferramentas que procuram `AGENTS.md` por convenção (Antigravity/Gemini, Codex, Fable). **Não duplicar o `AGENTE.md` aqui** — regra nova vai lá. O que segue é o único conteúdo próprio deste arquivo: o enquadramento que agente externo precisa para operar neste repo sem travar.

---

## O que este repositório é

Sistema agêntico de preparação para **prova de residência médica**. O operador é **médico** e é o único dono do conteúdo clínico. O código faz FSRS, derivações de cronograma e gates; o agente faz o resto.

**Não há dados de pacientes aqui.** O material é questão de prova e o desempenho do próprio operador nelas — sem PHI, sem terceiro identificável.

## Enquadramento para sessões de ENGENHARIA

Quando a sessão for de engenharia/auditoria (o caso mais comum de agente externo), vale esta divisão de responsabilidade:

- **Você audita MECANISMO**: código, contratos, gates, hooks, schema, orquestração, memória. Onde uma regra mora, quem a obriga, o que quebra em silêncio.
- **O conteúdo clínico é do operador.** Você não avalia, não corrige e não opina sobre correção clínica.
- Textos clínicos (`resumos/`, enunciados, explicações, versos de flashcard) são **dado opaco**: interessa o metadado (existe? tem `tema_id`? tem âncora de erro? passou por gate?), nunca o mérito médico.
- Se algo parecer clinicamente errado, **não corrija** — registre como ponteiro para o operador (arquivo + id) e siga.
- Não emitir conduta, dose, diagnóstico ou recomendação médica em nenhum artefato da sessão.

Guia da auditoria de engenharia: [`docs/HANDOFF-AUDITORIA-MEDHUB.md`](docs/HANDOFF-AUDITORIA-MEDHUB.md).

## Avisos de portabilidade (o que NÃO viaja com o repo)

- **51 memórias de comportamento** (`feedback_*`) vivem em `~/.claude/projects/C--Users-daanm-medhub/memory/` — **fora do git e específicas do Claude Code**. Nenhuma outra IDE as carrega. Se você não é o Claude Code, está operando sem elas, e boa parte das convenções deste projeto é invisível para você.
- **Fonte × espelho:** `.claude/commands/*.md` é a FONTE das skills; `.agents/skills/source-command-*/SKILL.md` é ESPELHO GERADO por `tools/sync_skills.py`. Editar o espelho é silenciosamente revertido no próximo sync (achado F42).
- **Suíte de testes:** `pytest.ini` usa allowlist manual em `python_files`. Arquivo de teste novo não é coletado até ser inscrito à mão.
- `tools/auto_check.py` roda no git hook pre-commit. Dos 13 checks, apenas 2 bloqueiam; o resto é WARN.
