# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-05 — s077: `/revisar` ~34 cards + dissecação metacognitiva + **limpeza estrutural do deck** (dedup 15 pares, re-fil 291 `[bulk]`, fix `insert_questao.py`) + contrato `/revisar` evoluído. **Próximo: drenar backlog FSRS por área fraca (FA, PTI, arritmia ped., trauma) — fila agora filtrável por área.***

## ▶ Próximo passo imediato (ao retomar) — REVISÃO POR ÁREA FRACA
1. **Re-rodar `/revisar`** focando os clusters fracos diagnosticados na s077:
   - ⚠️ **Febre Amarela** (bug nº 3, decoreba): vetores (Haemagogus+Sabethes silvestre / Aedes urbano), Faget (bradicardia relativa), viremia <7d, incubação 3-6d. Anki bruto, recall repetido.
   - ⚠️ **Bug nº 1 — ancoragem no número/achado** (transferível, maior alavancagem): lê o lab/achado contra a tabela, não contra o contexto. Pegou PTI (plaquetas + PFC), asma (PaCO2 42 = falência) e **trauma** (grau anatômico/líquido livre × estabilidade). Heurística: *"o que esse número/achado DEVERIA ser nesse cenário?"*.
   - ⚠️ **Arritmia ped.** (bug nº 2): garfo "cadê a onda P?". E **ATLS XABC** (não pular o A pro C).
2. **Modo `/revisar` (contrato s077):** flip obrigatório (revelar verso de todo card) + **relearning intra-sessão** (card <4 re-aparece como drill, **sem** regravar no FSRS) + micro-resumo ao errar.
3. **Filtrar por área agora funciona** — usar `--area "Pediatria"` etc. (re-fil concluído).
4. **Evidência LIVE:** `pubmedmcp` conectado → `/pesquisar-evidencia` se card banca-dependente.

## Estado por frente
- **Volume & Metas:** 3.244/12.000 ENAMED (80,2%); ~86q/dia para o alvo (13-09). Planilha não reconciliada nesta sessão.
- **Conteúdo:** 45 resumos. **Gap ativo:** `Diabetes - Complicações Crônicas`.
- **Erros & Cards:** 234 erros; **325 cards qualitativos ativos** (86 aposentados). Deck **limpo**: 0 duplicatas, 0 option-dependent, 0 `[bulk]`.
- **FSRS:** fila 100% qualitativa. s077 revisou ~34 cards; falha alta em FA/PTI/arritmia/trauma (re-drillados em sessão). Backlog state=0 a drenar por área.
- **Infraestrutura:** governança de evidência ativa; `pubmedmcp` conectado; **`insert_questao.py` corrigido** (sem card heurístico fantasma); contrato `/revisar` com flip + relearning.

## Última sessão — sessão 077
- **`/revisar` ~34 cards + re-drills:** condutas de CM/Infecto/Cirurgia sólidas; falhas em FA (decoreba), PTI, arritmia ped., trauma. Re-drills consolidaram em sessão.
- **Dissecação metacognitiva (core do feedback):** erros por *elo quebrado* — **bug nº 1 ancoragem no número/achado** (PTI/asma/trauma, transferível), bug nº 2 entidades espelhadas (TSV×sinusal), bug nº 3 decoreba FA. Memória `feedback_bug_ancoragem_numero.md`.
- **Contrato `/revisar` evoluído:** flip obrigatório + relearning intra-sessão (não regrava FSRS).
- **Limpeza estrutural do deck:** 15 pares duplicados mergeados + 5 option-dependent reescritos + **291 cards `[bulk]` re-categorizados** (Cirurgia 216→57, Pediatria 4→65, Endocrino 3→35; 16 temas novos). Card-síntese **#413** (PTI). `insert_questao.py` corrigido.

## Pendências/observações ativas
- **Erros repetidos vigiados:** (1) **bug nº 1 — ancoragem no número/achado** (PTI/asma/trauma); (2) sinusal × TSV; (3) ATLS XABC (pular o A). Dengue=extravasamento resolvido ✅.
- **Baixa prioridade:** 2ª passada de consolidação fina de temas (Obstetrícia trofoblástica/abortamento; esporotricose Dermato×Infecto).
- **Git:** commit/push da s077 nesta sessão.

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
