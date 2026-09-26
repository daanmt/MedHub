# Session 200 -- Listas no hub: t96 e t26 resolvidas, Solução MedHub vira CADEIA de elos, objetivo por questão, riscadas na análise

**Data:** 2026-09-26 (sábado, ~08h -> 14h local) - **Ferramenta:** Claude Code (Opus 5.5 1M) - **Continuidade:** `session_199.md`

---

## O que foi feito
- **Estudo (as 2 primeiras listas resolvidas na aba do hub):**
  - **t96 · Tópicos em Pediatria · 13/18 (72%)** -- sólidas 7/9, dúvidas 4/5, chutes 2/4; firmes 11/18; mediana 62 s/q. `sessoes_bulk` 132 (sessão 200), tarefa #96 FEITA. Erros Q8, Q12, Q14, Q15, Q17 = puericultura normativa (4 de 5) + IDP.
  - **t26 · Diabetes na Gestação · 17/19 (89%)** -- sólidas 12/12, dúvidas 4/5, chutes 1/2; firmes 16/19. `sessoes_bulk` 133, tarefa #26 FEITA. Erros Q8 (intervalo da USG de crescimento) e Q15 (HbA1c >= 6,5% = DM prévio).
  - **Cards:** 11 notas do lote `2026-09-26b` gravadas (`--record-lote --apply --expect 11`; revlog 3432 -> 3443).
  - **7 erros registrados** (`insert_questao --errors-file`, ids 1090-1096, cards #1749-1755, ligados a `--sessao` e `--emed`) + 3 chutes certos no ledger (`habilidades --add incerteza`: t26 Q13, t96 Q11, Q18). Depois do racional declarado da t96: #1751, #1753, #1755 **reforjados** para o elo que ele declarou (`recurate_cards --apply`, backup antes) e **#1756** novo no elo 1 da Q12 (`insert_card_extra`).
  - Vereditos do operador no hub: t26 Q8/Q15 concordo; t96 Q12/Q14/Q15 concordo, Q17 em parte, **Q8 discordo** ("acertei o elo 1, errei o 2") -- análise revista com o racional.
- **Hub (Versions 23-28), pedidos do operador na ordem em que vieram:**
  1. Linha da questão = banca + ano e área > tema (parser testado nas 257 grafias de banca capturadas) (`2e56694`).
  2. Tempo da tela de fim = mediana (a Q12 ficou aberta ~10 h e levava a média a 2.039 s).
  3. Listas agrupadas por semana do plano (Atrasadas / Semana N · datas (esta)), na ordem do plano; resolvidas recolhidas; o hub embute o calendário (`<!-- @hub:semanas -->`, mesma régua do quadro) (entrou no commit `da62e95`: o 1o commit ficou barrado pelo F38 até os erros da sessão 200 serem registrados).
  4. Aba "Questões" -> **"Listas"** (quebrava a barra no celular).
  5. **Solução MedHub v2 = cadeia de elos** ("muito pobre ... elencando cada elo e apontando onde quebrou ... fundamental"): `pede` + `cadeia [{elo, chave}]` + `alternativas` (cada errada aponta o elo em que cai) + `objetivo`. A página rotula "Cadeia de raciocínio / Elo N" e acende o elo da letra; a análise (`analises/*`, `quebrou` 0-based) move a marca. 91 questões re-cunhadas (t26, t40, t49, t96).
  6. **Objetivo por questão** ("DMG com objetivos diferentes ... aponta fragilidade"): lista fechada por tema, `emed_solucoes.objetivo`, `--status --por-objetivo`, "Por objetivo" na tela de fim. O objetivo só aparece DEPOIS de responder (antes seria pista) -- dito ao operador, sem objeção.
  7. **Riscadas + par da dúvida** ("não sei se estamos aproveitando"): a página gravava, o registro DESCARTAVA; agora `emed_respostas.riscadas` + `leitura_metacognitiva` (elos executados, par da dúvida, riscou a certa) no `--erros` e na página.
  8. Navegação: o botão de cima é contextual -- "‹ Lista" dentro de questão de lista terminada, "‹ Todas as listas" no resultado (o botão extra que eu tinha posto saiu, a pedido) (`e1843ab`).
- **Evidência:** intervalo da USG de crescimento no DM = 3-4 semanas, confirmado no SENTIDO (evidence-researcher; trecho primário BR não localizado, confiança média) -> card #1749.

## Decisões / regras novas
- Solução = cadeia (memória `feedback_solucao_cadeia_elos`; skill `/banco-emed` §Solução MedHub; brief versionado em `docs/SOLUCAO-MEDHUB-BRIEF.md` com as listas fechadas de objetivo de DMG, hérnias e puericultura).
- **Card nasce do elo que quebrou; o declarado vence o inferido** -- racional que move a quebra = reforja in-place (operador: *"o refino na cadeia de raciocínio lógico é fundamental para refinar inclusive os cards"*).
- `_emed_ler` tolera coluna nova em banco não migrado (`NULL AS col`): antes um SELECT com coluna ausente virava `[]` silencioso -- o export teria perdido todas as soluções.

## Leitura metacognitiva que as riscadas renderam (t96)
- Q14 e Q15: sólidas SEM riscar nada = crença firme no lugar errado (suco não coado "pode"; esquema de ferro do termo aplicado ao baixo peso).
- Q18: marcou "chute" mas riscou as 4 erradas = subconfiança.
- Q8: dúvida B x D; o elo 1 firme excluía a D sozinho -- o padrão-mestre "o dado que EXCLUI" (`feedback_bug_discriminador_exclui`) de novo.

## Custo dos subagentes (usage do harness)
| Filho | Modelo | Tokens | Tools | Tempo |
|---|---|---|---|---|
| Solução v1 t96 | Opus | 152.634 | 31 | 10,7 min |
| Solução v1 t26 | Opus | 135.245 | 24 | 7,4 min |
| Solução v1 t49 | Opus | 148.169 | 32 | 11,0 min |
| Solução v1 t40 | Opus | 205.898 | 40 | 12,5 min |
| Evidência (intervalo USG) | Sonnet | 70.449 | 11 | 2,0 min |
| Solução v2 t49 | Opus | 130.309 | 13 | 7,2 min |
| Solução v2 t26+t96 (27 q) | Opus | 138.344 | 14 | 8,1 min |
| Solução v2 t40 | Opus | 171.510 | 13 | 8,7 min |
| **Total** | | **1.152.558** | 178 | ~67,6 min |

A v1 das 4 listas (642k) foi superada no mesmo dia pela v2 (440k): o formato deveria ter nascido em cadeia -- a autópsia já era o molde.

## Pendências
- 8 listas no hub ainda em v1 (t1, t65, t68, t100, t3, t61, t651, t141): re-cunhar em v2 por lista, quando entrar na vez (brief em `docs/`; t65/t61 usam a lista de hérnias; t100 a de puericultura; as outras pedem lista fechada nova).
- `questoes_erros.o_que_faltou` do erro 1092 (t96 Q8) ficou com a inferência antiga (elo 1); não há CLI de correção de linha de erro -- o registro vivo é a análise do hub.
- t40 Q5, Q6, Q18, Q21, Q22 sem tabela/figura na captura (a solução avisa; abrir no EMED).
- Não há resumo local de Hérnias da Parede Abdominal (4 listas no plano).
- Herdadas da s199: captura PAUSADA (incidente do clique na t65); gabaritos suspeitos t100 Q8, t68 Q13, t1 Q21, t65 Q18.

banco-emed: t96 registrada 18 (13 acertos) · t26 registrada 19 (17) · erros analisados 7 (+3 incertezas) · Solução v2 em 91 questões
