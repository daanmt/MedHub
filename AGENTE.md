---
type: bootstrap-protocol
layer: root
status: canonical
relates_to: ESTADO, roadmap
---

# AGENTE.md — Protocolo de Continuidade MedHub

## 1. PRINCÍPIO CENTRAL
**Este projeto é uma jornada contínua.** Nunca comece do zero. Sua missão é herdar o estado da sessão anterior, executar a tarefa atual e preparar o terreno para a próxima.

## 2. BOOT SEQUENCE (Obrigatório ao iniciar)
Toda nova sessão DEVE seguir esta ordem de leitura para bootstrap de contexto:

1.  **[[ESTADO]]**: Documento único de estado — visão canônica do projeto, mapa de arquivos, marcos e seção "Últimas sessões" (onde paramos).
2.  **Workflows relevantes**: Se for analisar questões, leia `.agents/workflows/analisar-questoes.md`. Se for criar resumo, leia `.agents/workflows/criar-resumo.md`.
3.  **Último log**: `history/session_NNN.md` mais recente.
4.  **[Memory v1] Contexto de memória longa**: carregado automaticamente via hook SessionStart ao início da sessão.
    Se não aparecer no contexto inicial, executar manualmente: `python -m app.memory.inspect --context`
5.  **[RAG] Busca semântica durante a sessão**: usar `mcp__obsidian-notes-rag__search_notes` para localizar conteúdo clínico específico em `resumos/` sem ler arquivos inteiros. Útil para verificar condutas, cruzar temas e recuperar critérios de resumos existentes.

> **Nota:** `HANDOFF.md` foi aposentado na sessão 058. `ESTADO.md` é o único documento de estado/handoff do projeto.

## 3. PROTOCOLO DE FECHAMENTO (Antes de terminar)
Para garantir que a próxima sessão comece sem perda de informação:

1.  **Atualizar ESTADO.md**: Adicionar entrada em "Últimas sessões" com o que foi feito e o que falta.
2.  **Registrar Sessão**: Criar novo arquivo em `history/session_NNN.md` seguindo o template.
3.  **Git (se disponível)**: Fazer `git add` nos arquivos modificados (nunca `git add .` — `ipub.db` não deve ser commitado), `git commit -m "sessao NNN: [resumo]"`, `git push`.

## 4. MENTALIDADE GOLD STANDARD (Qualidade MedHub)
Toda interação deve refletir o nível de excelência dos resumos padrão-ouro (`Trauma.md`, `Insuficiência Cardíaca.md`):

1.  **Benchmark 80/20:** 80% de assertividade objetiva (condutas, scores) + 20% de didática clínica formal (fisiopatologia densa).
2.  **Linguagem Acadêmica:** Proibição absoluta de coloquialismos, jargões de "sobrevivência de plantão" ou termos dramáticos (ex: "vai morrer", "encher balde").
3.  **Alta Especificidade:** Priorize critérios objetivos, quantitativos, definições; em vez de descrições genéricas.
4.  **Acúmulo de Conhecimento:** Jamais substitua ou remova insights prévios, especialmente na seção "Armadilhas de Prova". Novos dados devem ser **acumulados** aos existentes para evitar regressão de conhecimento.

---
*Assinado: Antigravity*
