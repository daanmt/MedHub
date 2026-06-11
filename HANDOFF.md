# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-11 — s078: `/revisar` **backlog drenado (44 cards)** + contrato `/revisar` → **Camada 2 (Revisão Direcionada de fechamento)** (o card é a sonda, o resumo é a fonte; verdict: **0 deficiência de material**) + **dedup estrutural: 109 pares v1/v2 aposentados** (deck 325→216; chave `questao_id`). **Próximo: MODO SPRINT questão-first — ≥100q + ≥20 cards/dia, sem apostila (até ~13/07).***

## ▶ Próximo passo imediato — MODO SPRINT QUESTÃO-FIRST (s079+)
1. **Frente = questão pura.** Meta **≥100q/dia + ≥20 flashcards/dia** até ~13/07/2026 (final desta semana + 4 semanas). **SEM apostila** — tópico novo coberto por questões + cards. Por sessão: `registrar_sessao_bulk` ANTES → analisar erros → cards via `insert_questao`. **Não criar resumo completo por tópico novo.** Detalhe: memória `project-sprint-questoes-focado`. Scrum master cobra a cadência (100/dia > alvo ENAMED de ~92/dia).
2. **`/revisar` (contrato s078):** Camada 1 (micro-resumo na virada) + **Camada 2 (Revisão Direcionada ao fechar)** + flip + relearning. **Nota sprint:** tópico question-first pode não ter resumo de origem → a Camada 2 vira **micro-nota** focada do erro. **Re-verificar FA** (cards 401/403/389/402/405) — drillada s078, deve subir pra nota 4.
3. **Vigiar bug nº 1 (ancoragem no achado):** líquido livre / plaqueta / PaCO2 lidos contra a tabela, não o contexto. Heurística: *"o que esse achado DEVERIA significar nesse cenário?"*.
4. **7 pares divergentes** flagados no dedup (corrigir/aposentar quando der): q53 (#95/#96 HCE×T4F), q54 (#97/#98 T4F×atresia), q99 (#182/#183 insulina), q100 (#184/#185 avental branco), q40, q133, q154.

## Estado por frente
- **Volume & Metas:** 3.244/12.000 ENAMED (80,2%); ~92q/dia para o alvo (13-09). Planilha não reconciliada nesta sessão.
- **Conteúdo:** 45 resumos. **Gap ativo:** `Diabetes - Complicações Crônicas`. Resumos dos temas revisados (Arbovirose/Trauma/Asma/DM2) auditados na s078 = **padrão-ouro, sem edição**.
- **Erros & Cards:** 234 erros; **216 cards qualitativos ativos** (195 aposentados). **Dedup estrutural s078:** 109 pares v1/v2 (chave `questao_id`) aposentados via `needs_qualitative=2` (reversível; backup `ipub_backup_20260611_114134.db`).
- **FSRS:** backlog de 44 cards drenado (24×4, 5×3, 7×2, 8×1). Falhas: FA (decoreba) + trauma órgão sólido (bug nº 1). Vitória: dengue C/D consertado na sessão (Camada 1).
- **Infraestrutura:** contrato `/revisar` com **Camada 2** ativo; governança de evidência + `pubmedmcp` ativos.

## Última sessão — sessão 078
- **`/revisar` 44 cards** (backlog drenado em 8 lotes de 5). Condutas de CM/Cirurgia/Cardio sólidas; falhas concentradas em **FA (decoreba)** e **trauma de órgão sólido (bug nº 1)**.
- **Contrato `/revisar` → Camada 2 (Revisão Direcionada de fechamento):** o card é a sonda, o resumo é a fonte; reforçar matéria não-consolidada via card é infrutífero → reabordar o resumo do tema ao fechar. Encodado em `revisar.md` + memória.
- **Verdict de Camada 2 (s078): 0 deficiência de material** — FA, Trauma, Asma e DM2 têm resumo gold cobrindo o ponto errado com armadilha. Prescrição = drillar, não editar.
- **Pares contraditórios espelhados (bug nº 1):** PTI 9×10 (PFC × observação) e baço×fígado 25×26 (observação × laparoscopia).

## Pendências/observações ativas
- **Erros repetidos vigiados:** bug nº 1 — ancoragem no achado (líquido livre/plaqueta/PaCO2); FA decoreba; ATLS XABC.
- **7 pares divergentes** flagados no dedup (ver Próximo passo §3) — revisar/corrigir/aposentar.
- **Git:** commit/push da s078 nesta sessão (contrato + docs; `ipub.db` é local-only).

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
