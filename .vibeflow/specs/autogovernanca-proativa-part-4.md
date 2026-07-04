---
type: spec
projeto: MedHub
feature: autogovernanca-proativa
part: 4
slug: autogovernanca-proativa-part-4
status: ready
relates_to:
  - .vibeflow/prds/autogovernanca-proativa.md
  - tools/day_plan.py
  - tools/cronograma.py
  - core/contracts/revisao-calibrada-contract.md
  - AGENTE.md
---

# Spec -- Autogovernança Proativa - Parte 4: Defeitos da Frente Extensivo + Governança (R5+R6)

> Deriva de `.vibeflow/prds/autogovernanca-proativa.md` (R5, R6). Corrige os defeitos da frente extensivo entregues as-delivered na s106 e formaliza a governança no AGENTE.md.

## Objective
Fazer a promoção extensivo->D10 respeitar a nota explícita do usuário e casar o tema corretamente, sob uma regra única nos 3 artefatos, e formalizar no AGENTE.md o harness e a fonte-canônica-de-skills.

## Context
A frente extensivo (s105, selada as-delivered na s106) tem defeitos conhecidos e documentados: **C1** -- `tools/day_plan.py::difficulty_report` casa o tema na grade com `t.get("tema","").lower() in tema.lower()` (string vazia casa qualquer tema; o primeiro task de tema vazio "ganha") e o `break` só sai do loop interno (semanas seguintes sobrescrevem `mat`) -> `material_indicado` reportado instável. **C4** -- a heurística de `tools/cronograma.py` (`tipo==teoria OU regex /extensivo/i`) marca **279 de 352 tasks (79%)** como extensivo, esvaziando a calibração (quase tudo vira D10). **G5** -- ao ver material=extensivo, `day_plan` força `nota_efetiva>=7` (degrau D8, nem D10) e **sobrescreve nota explícita do usuário**, violando a precedência dura input>pergunta>inferência do `revisao-calibrada-contract.md`. Some-se a isso o débito de governança: a cláusula "Reflexo Autônomo §1.3" foi inserida como bullet dentro do modo aula-base §1.2 (a seção §1.3 real não existe), e os CLIs `auto_check`/`setup_hooks`/`sync_skills` não estão na tabela §7.4.

## Definition of Done
1. **C1 -- matching de tema estável:** o casamento tema↔grade usa igualdade normalizada (trim + casefold + colapso de espaços), **ignora temas vazios**, e faz early-return no primeiro match. Rodar `day_plan.py --difficulty` para o mesmo tema em runs repetidos retorna o mesmo `material_indicado`.
2. **G5 -- precedência preservada:** material extensivo **nunca** sobrescreve nota explícita do usuário (`fonte == 'usuario'`); quando não há nota explícita, a inferida recebe **floor 9** (degrau **D10**, não D8) e o retorno expõe um sinal `deep_research: true`. Um caso com nota explícita 4 em tema extensivo mantém nota 4 (degrau D5).
3. **C4 -- heurística recalibrada:** o critério de `material_indicado` em `cronograma.py` é revisto para não marcar a maioria das tasks como extensivo (documentar o novo critério no docstring); `python tools/cronograma.py --rebuild` regenera `core/cronograma/grade.json` mantendo **n_tasks=352 e total_questoes=10218** e uma distribuição extensivo/resumo mais equilibrada (extensivo < 60% das tasks).
4. **Regra única D10 nos 3 artefatos:** a regra "extensivo/inferida-sem-nota -> D10 + dever de Deep-Researchness; nota explícita sempre vence" fica idêntica em `day_plan.py`, `core/contracts/revisao-calibrada-contract.md` e `AGENTE.md §1.2` (sem divergência textual entre eles).
5. **R6 -- governança formalizada:** `AGENTE.md` ganha uma **§1.3 real** (Reflexo Autônomo de Validação, movido para fora do §1.2); a tabela §7.4 registra `auto_check.py`, `setup_hooks.py` e `sync_skills.py`; a §6 ganha as decisões "harness autônomo staged-only + warning-first" e "fonte canônica de skills = `.claude/commands` + espelhos gerados".
6. **Craftsmanship -- suíte e harness verdes:** os checks documentais de `tools/test_revisao_calibrada.py` (que verificam strings do contrato/AGENTE.md) continuam passando após as edições; `python -X utf8 tools/auto_check.py --all` continua exit 0; `day_plan.py` roda sem exceção (smoke).

## Scope
- `tools/day_plan.py`: fix do matching (C1) + precedência/floor D10 + sinal `deep_research` (G5).
- `tools/cronograma.py`: heurística de `material_indicado` recalibrada (C4) + docstring.
- `core/cronograma/grade.json`: regenerado via `--rebuild`.
- `core/contracts/revisao-calibrada-contract.md`: regra única D10.
- `AGENTE.md`: §1.3 real + §7.4 (CLIs novos) + §6 (2 decisões).

## Anti-scope
- **Sem** reprocessar/reindexar `Cronograma.pdf` além do `--rebuild` (o parser de material já existe; só o critério muda).
- **Sem** alterar o schema do `ipub.db` nem o algoritmo do FSRS.
- **Sem** tocar a inferência `infer_nota()` além da regra de floor/precedência (a matemática dos sinais frios permanece).
- **Sem** fabricar `history/session_103-105` (o gap já foi documentado na s106).

## Technical Decisions
- **Floor 9 (D10), não override 7 (D8):** a intenção do PRD é que extensivo dispare o dever de Deep-Researchness (D10); o `>=7` atual erra o degrau. Floor só se aplica à inferência -- nota explícita do usuário sempre vence (precedência dura do contrato).
- **Igualdade normalizada, não substring:** substring com string vazia é a raiz do C1; igualdade normalizada (casefold + trim + colapso de espaço) é determinística e evita o "tema vazio casa tudo". Early-return elimina o bug do `break` interno.
- **Recalibrar o critério, não removê-lo:** manter `material_indicado` como sinal, mas com gatilho mais estrito (ex.: exigir menção textual a "Extensivo"/"Livro Digital Completo" E ausência de "Resumo", em vez de `tipo==teoria` que é largo demais). O número exato de extensivos é subproduto; o DoD ancora em "< 60%".
- **§1.3 como seção real:** o Reflexo Autônomo não tem relação com o modo aula-base (§1.2); movê-lo para §1.3 corrige a estrutura e o auto-referência do próprio contrato.

## Applicable Patterns
- `agent-workflow-protocol.md` -- §7.4 e §6 do AGENTE.md são a espinha do protocolo; registrar os CLIs novos mantém a tabela como fonte fiel.
- Contrato `revisao-calibrada-contract.md` -- a regra única D10 deve casar com a Cláusula 3 (degraus D10/D8/D5/D2) e a precedência input>pergunta>inferência.

## Risks
- **Recalibrar a heurística pode sub-marcar extensivo** (falso-negativo) -> mitigação: ancorar no texto do PDF (menção explícita), não em heurística frouxa; validar a distribuição no `--rebuild` (DoD-3).
- **Editar AGENTE.md/contrato pode quebrar os checks documentais da suíte** (que fazem grep de strings específicas) -> mitigação: rodar `test_revisao_calibrada.py` após cada edição (DoD-6); preservar as strings-âncora que a suíte procura.
- **`--rebuild` depende do `Cronograma.pdf` (gitignored, IP)** -> mitigação: se o PDF não estiver presente na máquina do implementador, o `grade.json` fica como está e o DoD-3 vira TODO explícito -- o resto da parte (C1/G5/R6) não depende do rebuild.

## Dependencies
- `.vibeflow/specs/autogovernanca-proativa-part-2.md` (a §6/§7.4 documenta o harness staged+warning-first da Parte 2)
- `.vibeflow/specs/autogovernanca-proativa-part-3.md` (a §7.4 registra `sync_skills.py`, criado na Parte 3)
