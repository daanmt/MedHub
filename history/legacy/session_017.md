# Session 017 — Elaboração de Roadmap do Sistema IPUB
**Data:** 2026-03-14
**Ferramenta:** Antigravity
**Continuidade:** Sessão 016

---

## O que foi feito
- Atuei como Senior PM para estruturar e desenhar o ciclo de vida do ambiente de estudos IPUB.
- Criei o artefato `roadmap.md` separando o produto em 4 Fases claras.
- Detalhamento: Fase 1 (MVP atual via IDE), Fase 2 (Retenção via Flashcards), Fase 3 (Frontend Streamlit + DB Relacional) e Fase 4 (Analytics e Simulados Direcionados).
- Definição dos próximos passos imediatos (Action Items) conectando a infra do Caderno de Erros à geração de flashcards e banco SQLite.

## Artefatos criados/modificados
- `roadmap.md` (Criado/Preenchido)
- `ESTADO.md`
- `HANDOFF.md`
- `history/session_017.md`

## Decisões tomadas
- Definido a transição futura do uso de `.md` puro (limitação escalável) para um banco `SQLite` nas Fases 2/3.

## Próximos passos (se houver)
- Definir template estruturado de Conversão de entrada de Erro -> Flashcard.
- Criar script python para ler o caderno de erros atual e inserir no SQLite.
