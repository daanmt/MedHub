# Session 080 -- Hemostasia (37q/23a) + padrão de enunciado negativo
**Data:** 2026-06-12
**Ferramenta:** Claude Code (Fable 5)
**Continuidade:** Sessão 079

---

## O que foi feito
- **Bulk registrado:** Hemato 37q/23a (62,2%) -- `sessoes_bulk` s080. Área fraca confirmada.
- **14 erros (2 blocos de 7)** analisados -> **13 cards qualitativos** (ids 425-437) via `insert_questao.py` (tema "Hemostasia I", id 183). UTF-8 verificado.
- **Q7 (coluna defeito × sangramento) NÃO cardado:** gabarito oficial B é medicamente errado (defeito de coagulação ≠ sangramento superficial); usuário acertou (C = 3-1-2), recurso negado pela banca. Erro de banca, não do aluno.

## Padrões de erro identificados
- **vWD × FVIII/hemofilia -- erro DUPLO (Q11 e Q12):** marca o fator (FVIII) em vez do defeito primário (FvW); o FVIII baixa porque o FvW é seu carreador.
- **Grid TP/TTPa frágil:** Q10 (TP↑ isolado = FVII, marcou DvW).
- **Plasmaférese nos 2 sentidos:** Q9 aplicou demais (def. vit. K por má-absorção); Q14 não lembrou que é a base da PTT.
- **Enunciado negativo (EXCETO/ERRADA) -- 3ª vez na semana (Q14):** marca afirmação verdadeira em vez de isolar a falsa.
- **PTI tratar × observar -- REINCIDÊNCIA (Q6):** marcou 9k + mucoso como "observar" (é tratar). 2º erro pelo mesmo motivo (bug nº 1).
- Pontuais: HIT -> toda heparina sai, fondaparinux (Q4); HNF inibe IIa+Xa, meia-vida curta (Q5); uremia -> DDAVP (Q8); hipotermia/tríade letal (Q2); fibrinólise -> tranexâmico (Q13); bicitopenia macrocítica no idoso -> medula/SMD (Q1).

## Artefatos criados/modificados
- Cards 425-437 (`flashcards` + `fsrs_cards`); 13 linhas em `questoes_erros` (tema 183).
- Memória: `feedback_enunciado_negativo.md` (NOVA) + `feedback_bug_ancoragem_numero.md` (recorrência PTI s080) + pointers no MEMORY.md.

## Decisões tomadas
- Cards de PTI sob tema "Hemostasia I" (não o tema "PTI"/Pediatria) -- bloco de estudo coeso; o resumo de Hemostasia cobre PTI.
- Q7 não cardado (erro de banca; cardar ensinaria medicina errada -- governança de evidência).
- Resumos NÃO editados (sprint + verdict s078 "0 deficiência"). Hipotermia/tríade letal cabe em `Trauma.md` (backfill opcional amanhã); def. vit. K por má-absorção e fibrinólise->tranexâmico são finos no resumo (cards cobrem).

## Próximos passos
- Bloco de 8 temas do cronograma (amanhã) -- **revisão direcionada do resumo ANTES das questões**.
- Re-verificar no `/revisar`: vWD/FVIII (434/435), enunciado negativo, PTI (430).
