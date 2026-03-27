---
type: bootstrap-protocol
layer: root
status: canonical
relates_to: ESTADO, HANDOFF, roadmap
---

# AGENTE.md — Protocolo de Continuidade MedHub

## 1. PRINCÍPIO CENTRAL
**Este projeto é uma jornada contínua.** Nunca comece do zero. Sua missão é herdar o estado da sessão anterior, executar a tarefa atual e preparar o terreno para a próxima.

## 2. BOOT SEQUENCE (Obrigatório ao iniciar)
Toda nova sessão DEVE seguir esta ordem de leitura para bootstrap de contexto:

1.  **[[ESTADO]]**: Visão canônica do projeto (o que é, mapa de arquivos, marcos).
2.  **[[HANDOFF]]**: Onde paramos? (tarefa atual, obstáculos, próximo passo imediato).
3.  **Workflows relevantes**: Se for analisar questões, leia `.agents/workflows/analisar-questoes.md`. Se for criar resumo, leia `.agents/workflows/criar-resumo.md`.
4.  **Último log**: `history/session_NNN.md` mais recente.
5.  **[Memory v1] Contexto de memória longa**: carregado automaticamente via hook SessionStart ao início da sessão.
    Se não aparecer no contexto inicial, executar manualmente: `python -m app.memory.inspect --context`
6.  **[RAG] Busca semântica durante a sessão**: usar `mcp__obsidian-notes-rag__search_notes` para localizar conteúdo clínico específico em `Temas/` sem ler arquivos inteiros. Útil para verificar condutas, cruzar temas e recuperar critérios de resumos existentes.

## 3. PROTOCOLO DE FECHAMENTO (Antes de terminar)
Para garantir que a próxima sessão comece sem perda de informação:

1.  **Atualizar HANDOFF.md**: Registre o que foi feito e o que falta.
2.  **Atualizar ESTADO.md**: Se houve nova área/tema ou decisão estrutural.
3.  **Registrar Sessão**: Criar novo arquivo em `history/session_NNN.md` seguindo o template.
4.  **Git (se disponível)**: `git add .` (Garantindo que `ipub.db` embarque), `git commit -m "sessao NNN: [resumo]"`, `git push`.

## 4. MENTALIDADE GOLD STANDARD (Qualidade MedHub)
Toda interação deve refletir o nível de excelência dos resumos padrão-ouro (`Trauma.md`, `Insuficiência Cardíaca.md`):

1.  **Benchmark 80/20:** 80% de assertividade objetiva (condutas, scores) + 20% de didática clínica formal (fisiopatologia densa).
2.  **Linguagem Acadêmica:** Proibição absoluta de coloquialismos, jargões de "sobrevivência de plantão" ou termos dramáticos (ex: "vai morrer", "encher balde").
3.  **Alta Especificidade:** Priorize critérios objetivos, quantitativos, definições; em vez de descrições genéricas.
4.  **Acúmulo de Conhecimento:** Jamais substitua ou remova insights prévios, especialmente na seção "Armadilhas de Prova". Novos dados devem ser **acumulados** aos existentes para evitar regressão de conhecimento.

---
*Assinado: Antigravity*
