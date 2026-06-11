# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-11 — s078: `/revisar` **backlog drenado (44 cards)** + contrato `/revisar` → **Camada 2 (Revisão Direcionada de fechamento)** (o card é a sonda, o resumo é a fonte; verdict: **0 deficiência de material**) + **dedup estrutural: 109 pares v1/v2 aposentados** (deck 325→216; chave `questao_id`). **Próximo: drillar FA bruto (decoreba) + revisar 7 pares divergentes flagados.***

## ▶ Próximo passo imediato (ao retomar)
1. **Febre Amarela — DRILLADA na s078 (Anki bruto, consolidada).** O nó **incubação 3-6d × viremia ≤7d** (que o usuário colapsava em "6-10") foi quebrado: separou limpo no Round 2. Faget=relativa, vetores, vacina 9m+4a→dose única, DVA+neurotrópica: ok. **Na próxima `/revisar`, re-verificar os cards de FA** (401/403/389/402/405 etc.) — devem subir pra nota 4 e espaçar. Material: `resumos/Clínica Médica/Infectologia/Arboviroses.md §4`.
2. **Bug nº 1 (ancoragem no achado) — vigiar:** reincidiu no card 26 (trauma hepático estável + líquido livre → respondeu laparoscopia; correto = TNO). Heurística: *"o que esse achado DEVERIA significar nesse cenário?"*. Órgão sólido estável = conservador, doa o grau, doa o líquido livre.
3. **Revisar 7 pares divergentes** (flagados no dedup — NÃO são duplicatas, os 2 cards conflitam): q40 (#69/#70), q53 (#95/#96 HCE×T4F), q54 (#97/#98 T4F×atresia), q99 (#182/#183 insulina ↓×manter), q100 (#184/#185 intensificar×avental branco), q133 (#230/#231), q154 (#272/#273). Decidir: corrigir o card errado ou aposentar.
4. **Modo `/revisar` (contrato s078):** Camada 1 (micro-resumo na virada) + **Camada 2 (Revisão Direcionada ao fechar: voltar ao resumo do tema com gap, expandir/comprimir a matéria)** + flip obrigatório + relearning intra-sessão.

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
