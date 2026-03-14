# AGENTE.md — Protocolo de Continuidade IPUB

## 1. PRINCÍPIO CENTRAL
**Este projeto é uma jornada contínua.** Nunca comece do zero. Sua missão é herdar o estado da sessão anterior, executar a tarefa atual e preparar o terreno para a próxima.

## 2. BOOT SEQUENCE (Obrigatório ao iniciar)
Toda nova sessão DEVE seguir esta ordem de leitura para bootstrap de contexto:

1.  **ESTADO.md**: Visão canônica do projeto (o que é, mapa de arquivos, marcos).
2.  **HANDOFF.md**: Onde paramos? (tarefa atual, obstáculos, próximo passo imediato).
3.  **Workflows relevantes**: Se for analisar questões, leia `.agents/workflows/analisar-questoes.md`. Se for criar resumo, leia `.agents/workflows/criar-resumo.md`.
4.  **Último log**: `history/session_NNN.md` mais recente.

## 3. PROTOCOLO DE FECHAMENTO (Antes de terminar)
Para garantir que a próxima sessão comece sem perda de informação:

1.  **Atualizar HANDOFF.md**: Registre o que foi feito e o que falta.
2.  **Atualizar ESTADO.md**: Se houve nova área/tema ou decisão estrutural.
3.  **Registrar Sessão**: Criar novo arquivo em `history/session_NNN.md` seguindo o template.
4.  **Git (se disponível)**: `git add .` (Garantindo que `ipub.db` embarque), `git commit -m "sessao NNN: [resumo]"`, `git push`.

---
*Assinado: Antigravity*
