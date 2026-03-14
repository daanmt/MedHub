# Session 018 — Ajuste de Produto (FSRS e Arquitetura UI/DB)
**Data:** 2026-03-14
**Ferramenta:** Antigravity
**Continuidade:** Sessão 017

---

## O que foi feito
- Refinamento agressivo da Fase 2 e 3 do `roadmap.md` a pedido do usuário.
- Incorporada a inteligência de acompanhamento de percentual de acertos conectada aos blocos de disciplinas do Estratégia Med.
- Inserção mandatória do algoritmo mnemônico **FSRS (Free Spaced Repetition Scheduler)** no motor de flashcards, superando o legado SM-2.
- Esboçada explicitamente a arquitetura de tabelas do futuro SQLite (`questoes`, `flashcards`, `fsrs_logs`, `metricas`).
- Desenhada a arquitetura macro das 4 interfaces principais que existirão no WebApp em Streamlit (Módulos 1 a 4).

## Artefatos criados/modificados
- `roadmap.md`
- `ESTADO.md`
- `HANDOFF.md`
- `history/session_018.md`

## Decisões tomadas
- Abandono de métricas vaidosas (ex: custo por questão) em prol da tabela fotorrealista de "Tração Teórica" (% de acerto por Tema).
- O DB será o coringa para alimentar o FSRS e Streamlit, substituindo passivamente a carga que os cadernos Markdown carregam hoje.

## Próximos passos (se houver)
- Codar o init_db.py e instanciar as tabelas SQLite.
- Integrar biblioteca/fórmula do FSRS no python backend.
