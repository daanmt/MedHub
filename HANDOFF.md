# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-17 -- Simulado 5 corrigido/analisado + Autópsia estendida (4 provas) + achados técnicos resolvidos (sessão 146)*

## > Próximo passo imediato

1. **Amanhã (18/08): 100 questões da fila, avançar S15.** Objetivo do usuário: **matar a S15 até quinta 20/08** + **simulado novo na sexta 21/08** (cadência 2/semana mantida). Confirmar S14->S15 no Drive antes de assumir a ordem (dado desatualizado -- `tools/cronograma.py --sync-drive <xlsx>`).
2. **Flashcards: 80-100/dia** (subiu de 40 -- `feedback_politica_cards_diaria`, sem razão declarada, é continuidade do ritmo). **Fila aberta, não drenada:** 79 cards (45 atrasados + 8 erros_frescos do Simulado 5 + 16 hoje + 10 novos), 46 temas. Os 8 erros_frescos já foram apresentados nesta sessão mas **nenhum avaliado** -- usuário adiou p/ amanhã. Retomar por aí (`/revisar`).
3. **Pendência residual (absorvida de docs/handoff-s146-continuacao.md, removido):** `tools/fila_enamed.py` ainda narra a tese antiga ("blueprint ENAMED descalibrado"); o modelo já mudou p/ ROI-por-slot-com-o-guia. Reescrever a narrativa e republicar o artifact "A Fila Errada" (`.../8a3fcf35-...`).
4. **S15 (quando abrir):** 12 tasks / 384 questões. Destaque: HAS Pt. 3, Câncer de Mama, Assistência ao Parto, APS, Aleitamento Materno, Parasitoses.

## Estado por frente
- **Volume & Metas:** 6.119 / 9.454 (perf. ~78,2%). Hoje: 100 (Simulado 5). Ritmo-alvo ~48,3q/dia (69d p/ Cronograma EMED).
- **FSRS:** dívida 45 atrasados + 16 p/ hoje -- pool 684 nunca introduzidos. Fila de hoje NÃO drenada (adiada p/ 18/08).
- **Conteúdo:** 125 resumos em resumos/ -- 11 tocados nesta sessão com armadilha nova (nenhum criado do zero).
- **Posição:** conteúdo S14 (nominal S21, atraso 7 sem) -- S15 é o passo de amanhã.
- **Erros & Cards:** 849 erros (+37 do Simulado 5) -- 1.141 cards ativos / 1.328 total (+40 diretos, cunhados via 4 subagents em paralelo).
- **Simulados:** **S5 63/100 (17/08)** é o último -- 98/100 confirmados pelo PDF exportado (Q20/Q100 truncadas no export, confirmadas CERTA pelo usuário). Autópsia dos Simulados estendida p/ as 4 provas (157 erros, `artifacts/autopsia-simulados.html`, republicada no link existente).
- **Datas:** ENAMED **13/09** (prova) -- 27d. Grade EMED fecha **25/10**. UERJ/USP sem edital.
- **Infraestrutura:** `.venv` estava dessincronizado de `requirements.txt` (fsrs, langgraph, langmem, anthropic, chromadb e mais 2) -- sincronizado. Skill `analisar-questao.md` documentava 5 grandes áreas; corrigida p/ refletir a prática real (~20 subespecialidades já em uso no banco).

## Última sessão -- s146 (SIMULADO 5 + ENGENHARIA, dia inteiro)
Duas frentes fecharam sob este selo (a primeira já tinha rodado antes desta conversa, sem log formal -- reconciliada aqui). **Frente A** (commits aff9e63..60bfd46): cronograma EMED recalibrado contra o blueprint medido do ENAMED -> correção de premissa (ENARE==ENAMED, o guia ENARE é a fonte boa) -> acentuação de 119/120 registros do `ipub.db` -> reforja de 138 defeitos de formulação de cards -> 9. **Frente B** (esta conversa): correção primária do Simulado 5 a partir de 5 PDFs (bug de parsing "Questão N antes do MARK" corrigido; 4 questões com vinheta perdida no export recuperadas via texto colado pelo usuário) -> placar 63/100 confirmado -> 37 erradas em 4 blocos, processadas por 4 subagents `/analisar-questao` em paralelo (40 cards, 11 resumos com armadilha nova, `questoes_erros` #815-851) -> padrão dominante: "escala além do necessário" em 10/37, com 2 reincidências diretas de fraquezas já catalogadas (hipertensivas/hidralazina desde s086; gravidez ectópica, top-5 do ranking) -> reconciliação dos arquivos que o usuário reorganizou (PLAYBOOK_EXECUCAO_PROVA.md -> `docs/`, link corrigido; HANDOFF_RESPOSTA_AI_ENG_FLASHCARDS.md removido, conteúdo já aplicado; AUDITORIA_MEDHUB.md restaurado a pedido -- tinha achados abertos) -> achados técnicos resolvidos (`.venv` dessincronizado; doc drift de área na skill) -> Autópsia dos Simulados estendida de 3 p/ 4 provas.

## Pendências/observações ativas
- **AUDITORIA_MEDHUB.md** segue ledger vivo com achados abertos (F21 contrato de aula; F35/F36-ALTA/F37/F38 reconcile/Drive-MCP; F39 atomicidade, ~350 na worklist) -- nenhum endereçado nesta sessão, só preservados.
- `tools/fila_enamed.py` com narrativa desatualizada (ver Próximo passo #3).
- Ritmo é medido contra a **grade (25/10)**, nunca contra o ENAMED -- correção deliberada da s126.

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_146.md*
