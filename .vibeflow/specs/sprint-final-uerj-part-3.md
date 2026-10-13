# Spec: sprint-final-uerj -- part 3: Painel = o backlog único (Hoje · Próximos dias · Fora do sprint)

> PRD: `.vibeflow/prds/sprint-final-uerj.md` (Solution 3). Gerada em 13/10/2026 (s226).

## Objetivo

O Painel diz o que fazer hoje e nos próximos dias, por data, sem "semana", "atrasadas" ou "até a prova".

## Definition of Done

1. Função PURA `plano.agenda_sprint(linhas, hoje)` -> `{hoje: [tarefas], proximos: [{data, tarefas, q}], fora: [...],
   q_hoje}` lida só de `dia_plano`; pendente com `dia_plano` < hoje entra no `hoje` (rolou, sem rótulo de atraso). É a
   fonte única que as parts 4 e 5 também consomem. Testes em `tools/test_plano.py`.
2. `tools/painel.py`: o bloco da semana vira **"Hoje"** (tarefas do dia com a linha-alvo da part-3 de
   `hub-correcoes-pos-tema-v3`, total de questões, "+ N cards" da dose do dia, e a RD não assinada mais antiga se
   houver) + **"Próximos dias"** (uma linha por dia "qua 14/10 · 3 listas · 78 q", recolhida, abre as tarefas) +
   **"Fora do sprint · N"** (recolhido, com o motivo). Sem banco de sprint (`dia_plano` todo NULL), o Painel mostra o
   bloco antigo (degradação declarada).
3. Os textos "Atrasadas", "Desta semana", "Semana N do plano" e "Até a prova" não aparecem quando há sprint -- teste
   `test_painel_sprint_sem_semana`.
4. `<li class="tarefa" data-tarefa="N">` preservado (o hub pinta a resolvida) -- teste existente verde.
5. Artesania: sem cor literal; `ui_capturas.py` 390/768/1280 sem rolagem horizontal; suíte verde.

## Escopo

`tools/plano.py` (só `agenda_sprint`), `tools/painel.py`, `tools/test_plano.py`, `tools/test_painel.py`, `docs/UI.md`.

## Anti-escopo

Hub (Teoria/Listas), boot; o bloco Ritmo e Por bloco do Painel; FSRS.

## Dependencies

- .vibeflow/specs/sprint-final-uerj-part-2.md
