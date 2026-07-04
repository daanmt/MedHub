---
title: "Autogovernança Proativa v1 -- Boot Determinístico, Âncora de Fraquezas e Paridade Multi-Agente"
type: prd
status: approved
author: "Claude Code (sessão 106)"
date: "2026-07-04"
relates_to:
  - core/contracts/revisao-calibrada-contract.md
  - core/contracts/forgetting-curve-contract.md
  - AGENTE.md
  - app/memory/inspect.py
  - tools/auto_check.py
---

# PRD: Autogovernança Proativa v1 -- Boot Determinístico, Âncora de Fraquezas e Paridade Multi-Agente

> Gerado via /vibeflow:discover em 2026-07-04 (sessão 106)

## Problem

O MedHub tem a **doutrina** de autonomia (AGENTE.md 1.1 postura, 2.4 boot proativo, contratos em `core/contracts/`), mas ela roda sobre **disciplina do agente, não sobre mecanismo**. A revisão s106 mediu o custo disso em quatro evidências:

1. **Protocolo sem enforcement:** as sessões s103-105 (Antigravity) entregaram o próprio harness de autonomia **violando o protocolo de fechamento** -- 0 commits, 0 session logs, HANDOFF não rotacionado -- e nada detectou até a revisão manual.
2. **Âncora de fraquezas cega:** o boot injeta "Áreas de fraqueza persistentes" com 20x `[? / ?]` há sessões. Os dados existem e são ricos (175 registros em `medhub/weak_areas`); o formatter (`app/memory/inspect.py::load_context`, linhas 157-161) lê chaves planas enquanto o LangMem grava envelope `{"kind","content":{...}}`. O sistema que deveria ancorar cada sessão nas fraquezas do usuário está mudo -- e falhou silenciosamente.
3. **Validador com efeitos colaterais e ponto cego:** o pre-commit validava a árvore INTEIRA (não o staged-set); as suítes que ele dispara **mutavam estado real** (`test_03` sobrescrevia `.git/hooks/pre-commit.bak`; round-trip escreve no `ipub.db` real); e a descoberta de arquivos era **cega a paths acentuados** (`core.quotepath` default -> path quoted -> `exists()` falha -> skip silencioso): o hook enxergava só 13 de ~57 resumos. Num corpus clínico em pt-BR, o harness validava uma fração do que prometia -- silenciosamente. *(A Fase 0 da s106 já corrigiu staged-only + quotepath-safe + testes herméticos; o restante desta cláusula permanece como escopo.)*
4. **Paridade multi-agente quebrada nas 2 direções:** `.agents/skills/source-command-revisar` está stale (pré-s096, sem PREPARAR/DRENAR -- o Codex operaria o modelo de revisão errado) enquanto `estilo-resumo` evoluiu SÓ no espelho (Deep-Researchness + Autoverificação ausentes do canônico). Regra clínica divergindo silenciosamente entre harnesses.

Agrava: a frente extensivo (s105) tem drift de 3 artefatos na regra de promoção D10 (PRD diz D10; contrato diz nota 9-10; `day_plan.py` força `nota_efetiva=7` -> degrau D8 **e sobrescreve nota explícita do usuário**, violando a precedência dura input>pergunta>inferência do `revisao-calibrada-contract.md`), além de bug duplo no matching do tema na grade (`""` casa qualquer tema; `break` só sai do loop interno).

## Target Audience

Usuário único -- médico em preparação (sprint ENAMED 13/09; alvo Psiquiatria UFRJ/IPUB; ramp 17k questões até dez/2026) -- **e os três agentes gerenciadores** (Claude Code primário, Antigravity, Codex CLI), que precisam herdar estado e operar sob as mesmas regras sem supervisão do usuário.

## Proposed Solution

Mecanizar os quatro loops de autogovernança, fazendo o back-port dos padrões que o `ai-eng` maturou a partir do próprio medhub (linhagem documentada em `ai-eng/contracts/state-handoff-contract.md`):

1. **Âncora de fraquezas real:** corrigir a leitura (envelope), deduplicar por `(area, especialidade)` na leitura e ranquear top-N por relevância -- as fraquezas voltam a abrir toda sessão.
2. **Boot determinístico em 2 fases (Presença -> Expansão):** o hook SessionStart injeta um bloco compacto e determinístico (fraquezas top-N + day_plan resumido + flag de drift + próximo passo do HANDOFF) com texto-contrato; o agente abre **oferecendo** o próximo ato ("sigo nele salvo redireção") e devolve o turno -- proativo sem sequestrar a abertura.
3. **Harness confiável:** pre-commit **staged-only** (feito na Fase 0 s106); testes herméticos (feito); regras novas em **warning-first** (frontmatter 5.2, convenção de encoding ASCII, paridade de skills) com promoção a blocking quando a base zerar; política de interpretador explícita (guard de `import fsrs` com mensagem clara).
4. **Paridade multi-agente por construção:** `.claude/commands/` é a fonte canônica; `tools/sync_skills.py` gera os espelhos `.agents/skills/` (incluindo o `cronograma.md` que ficou de fora); `auto_check` ganha check de drift. Pré-sync: portar Deep-Researchness+Autoverificação do espelho para o canônico (nada se perde).

Mais a correção dos defeitos da frente extensivo sob **uma regra única nos 3 artefatos**: material extensivo NUNCA sobrescreve nota explícita do usuário; sem nota explícita, a inferida ganha floor 9 (degrau D10 + dever de Deep-Researchness); matching de tema exato/normalizado.

## Success Criteria

1. Sessão nova (Claude Code E Codex) abre com >=5 fraquezas REAIS renderizadas (zero `[? / ?]`), plano <=8 linhas e oferta de próximo ato -- sem nenhum input do usuário.
2. Com árvore suja, commit de arquivo limpo PASSA; commit de resumo com tabela proibida BLOQUEIA -- inclusive quando o resumo tem path acentuado (`Clínica Médica/...`). *(Comprovado na Fase 0 s106.)*
3. Suítes rodadas 2x consecutivas: `ipub.db`, `.git/hooks/` e `resumos/` byte-idênticos (hermeticidade). *(test_03 já hermético; round-trip do test_revisao_calibrada ainda escreve no db real -- isolar.)*
4. Editar `.claude/commands/revisar.md` sem rodar o sync -> `auto_check` acusa drift de paridade (WARN).
5. `day_plan.py --difficulty` com nota explícita <7 em tema extensivo: nota preservada + sinal `deep_research`; sem nota explícita: degrau D10.
6. Resumo com frontmatter fora do 5.2 ou seta Unicode -> WARN visível no linter (sem bloquear até a promoção).

## Scope v0

- **R1 (âncora):** fix `load_context` (unwrap envelope; inclui bloco `workflow_rules` com o mesmo bug latente) + dedup read-side por `(area,especialidade)` + ordenação por `error_count`/`last_updated`.
- **R2 (boot 2 fases):** `tools/hooks/memory_boot.py` v2 -- injeção compacta (fraquezas top-N, day_plan resumido via subprocess com timeout + fallback silencioso, flag de drift comparando HANDOFF vs último `session_NNN` vs sujeira do git) + texto-contrato Presença->Expansão; mesmo script servindo Claude (`.claude/settings.local.json`) e Codex (`.codex/hooks.json`).
- **R3 (harness -- parcial, resto da Fase 0):** severidades no linter (BLOCK: regras vigentes / WARN: frontmatter 5.2, encoding ASCII, paridade); `audit_resumos.py` sem `errors='ignore'` (UnicodeDecodeError = erro crítico); round-trip do `test_revisao_calibrada` isolado em cópia temp (hoje escreve no `ipub.db` real); guard de interpretador `fsrs`. *(--staged, --changed quotepath-safe e test_03 hermético já entregues na Fase 0 s106.)*
- **R4 (paridade):** `tools/sync_skills.py` + check de drift no `auto_check`; pré-sync portando as adições do espelho `estilo-resumo` para o canônico; regeneração corrige o `revisar` stale; migrar `cronograma`.
- **R5 (extensivo):** regra única D10 aplicada em `day_plan.py` + `revisao-calibrada-contract.md` + AGENTE.md 1.2; fix do matching (tema normalizado, skip vazio, early-return); rever a heurística de `material_indicado` (hoje marca 79% como extensivo).
- **R6 (governança):** AGENTE.md -- 1.3 vira seção real (hoje é bullet dentro do modo aula-base 1.2); 7.4 registra `auto_check`/`setup_hooks`/`sync_skills`; 6 ganha as decisões "harness autônomo staged+warning-first" e "fonte canônica de skills + espelhos gerados".

## Anti-scope

- Motor/agendamento FSRS, Streamlit (`app/pages`), schema do `ipub.db`: intocados.
- Sem novo backend de memória; LangMem permanece; consolidação/dedup **write-side** do namespace fica fora (só read-side).
- Sem fabricar `history/session_103-105` retroativos (proibido por convenção); o gap é documentado no INDEX.
- Sem ingestão/indexação de apostilas (Zero-Upload mantido); sem re-arquitetura do `grade.json` além do já entregue.
- Sem auto-commit (fronteira humana 1.1(c) permanece); sem portar modos M-X do ai-eng (só boot 2 fases + flywheel de fraquezas + gatilho estilo alpha5 via staged hook).
- `evidence-researcher.toml` (gêmeo Codex da skill) fica fora do sync automático -- nota de manutenção manual.

## Technical Context

- Hooks existentes: SessionStart -> `tools/hooks/memory_boot.py` (chama `app.memory.inspect.load_context`); PostToolUse(Write) -> `memory_session_log.py`; espelhados em `.codex/hooks.json` (schema Claude Code). Caveat: paths com casing `MedHub/Tools` nos JSONs.
- Memória: LangMem + SQLiteMemoryStore (`medhub_memory.db`), 175 weak_areas + 257 session_insights; envelope `{"kind","content"}`; `manager.py:113-115` já lê aninhado (o formato canônico é o aninhado).
- Interpretadores: `python` global 3.12.2 TEM `fsrs` (py-fsrs); `.venv` NÃO tem. Hooks e auto_check usam o global -- formalizar.
- Harness (pós-Fase 0 s106): `auto_check.py` com `--changed`/`--staged`/`--all` quotepath-safe; `test_revisao_calibrada.py` (15 testes), `test_autonomia_hooks.py` (4 testes, test_03 hermético); pre-commit staged-only instalado.
- Padrões vibeflow aplicáveis: `agent-workflow-protocol.md`, `db-access-layer.md` (sqlite3 só em `app/utils/db.py` + CLIs standalone), `clinical-summary-format.md`.
- Referências ai-eng: `contracts/state-handoff-contract.md` (boot 2 fases, update-on-event, rotação), `.claude/boot-context.txt` (injeção determinística), `tools/reconcile.py` (drift-check no boot), `brain/feedback/preference-signal.md` (flywheel de correções).
- Budget vibeflow: <=6 arquivos por task -> o gen-spec deve fatiar R1-R6 em specs (provável: R1+R2 juntos; R3; R4; R5+R6).

## Open Questions

Nenhuma. (4 forks resolvidos na discovery de 2026-07-04: Fase 0 fora do PRD; `.claude/commands` canônica; staged-only + warning-first; boot em 2 fases.)
