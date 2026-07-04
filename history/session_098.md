# Session 098 -- Simulado dominical (41q) + diagnóstico dos 16 erros + frente de predição ENAMED
**Data:** 2026-06-28
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 097 (mesmo dia)

---

## O que foi feito
Sessão curta de análise (janela de contexto). O usuário fez o simulado dominical offline; navegador interrompeu em **41/100 questões -> 25 acertos (61%)**. Trouxe as **16 erradas** com gabarito + comentário.
- **Diagnóstico dos 16 erros por eixo** (substrato completo persistido em `tmp/simulado_s098_erros.md`, local, p/ cunhar os cards na volta).
- **Slot taxonômico dedicado a simulados** criado: área `Simulado` em `AREAS_VALIDAS` (`tools/registrar_sessao_bulk.py`); volume registrado (`sessoes_bulk` sessão 98, 41/25). O usuário espelha uma linha no Quadro Geral do dashboard.
- **Frente nova registrada -- predição ENAMED** (memória `project_predicao_enamed`): usar a evolução de performance (questões + simulados) p/ projetar a nota ENAMED com IC.

## Padrões de erro identificados (o achado)
**10 dos 16 erros são EXECUÇÃO, não conteúdo:**
- 🔴 **Bug nº1 (ancorar num achado, não integrar o conjunto) -- 6:** Q3 (ETCO₂ 7≠0), Q6 (idade óssea × VC<4 -> Turner), Q8 (Coombs neg -> G6PD), Q12 (artrite × multissistêmico -> LES), Q15 (assintomático × cálculo 2,8cm), Q16 (obesidade × gastroparesia contraindica GLP-1).
- ⚙️ **Conduta fina -- 3:** Q4 (epiglotite: NÃO manipular VA -- marcou laringoscopia no leito), Q10/Q14 (asma: ipratrópio × corticoide EV; STEP 1 × MART).
- 👁️ **Enunciado negativo -- 1:** Q11 (marcou tiamina/mandatória como contraindicada; era fenitoína).
- 📚 **Lacuna de conteúdo real -- 6:** Q1 (CHC: todo cirrótico rastreia 6/6m), Q2 (Down: pé plano valgo), Q5 (tremor essencial -> propranolol), Q7 (membranosa secundária), Q9 (abscesso perianal -> drenagem), Q13 (caso-controle = doença rara).

**Veredito:** o gargalo segue sendo **processo de prova** -- integrando o conjunto nos 6 do bug nº1, 61%->~76% sem estudar nada novo. Pediatria foi a área mais batida (4 erros, 2 de asma/GINA -> refresh).

## Artefatos criados/modificados
- `tools/registrar_sessao_bulk.py` (+ área `Simulado` em `AREAS_VALIDAS`).
- `sessoes_bulk` (local): +1 linha sessão 98 / Simulado / 41-25.
- `tmp/simulado_s098_erros.md` (local, não-commitado): os 16 erros estruturados p/ cunhagem.
- Memória `project_predicao_enamed` (frente nova) + linha no MEMORY.md.

## Decisões tomadas
- **Simulado = slot agregado × erros nos temas reais.** Volume/desempenho do simulado vai p/ o slot `Simulado` (sinal de condição-de-prova p/ a predição); erros individuais vinculam aos temas clínicos (resumos/flashcards), sem dupla contagem.
- Frente de predição ENAMED aprovada (a implementar): série temporal de % -> projeção + IC; simulado pesa mais que bloco temático.

## Próximos passos
- **Hoje ainda:** usuário volta p/ **adiantar o cronograma (~60-80 questões)** -- Semana 11.
- **Cunhar os 16 cards** do simulado (substrato em `tmp/simulado_s098_erros.md`, pipeline limpo, ancorados no elo) -- priorizar os 6 do bug nº1.
- **Implementar** a análise preditiva (frente `project_predicao_enamed`).
- Acumulado: **4.112 + 41 = 4.153** (slot Simulado).
