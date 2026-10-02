# Session 211 -- Painel, fila, performance e discover do feedback por elo declarado

**Data:** 2026-10-02 (sexta, 12h20-) - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_210.md`

---

## Pedido

"Atualize o painel ... avalie como estamos na fila ... como anda minha performance ... revise o mecanismo de feedback / raciocínio lógico para solucionar as questões, pois notei diversos erros por lá, além de visualmente poluído." Referência: Prisma Medicina (vídeo de onboarding transcrito + 4 prints). Pediu um loop de `/discover`.

## Feito

1. hub-backend 12h25: republicado com o mesmo lote 2026-10-02a (painel mudou: dia virou 02/10) -- Version 62. Lote em 0/100 notas; nenhuma lista nova resolvida (t26 e t96 já registradas). Página do hub idêntica à publicada (diff = 0); só o `painel.html` subiu.
2. **Fila (medido 02/10):** 792 cards em 15 dias; 109 vencem hoje (41 atrasados), depois 42/39/39/38/31/30/17 por dia; pool 650 novos; retenção 72,4% (7d), 77,5% (14d), 75,0% (30d); falha de 44% nos novos e 39% nos erros frescos x 12-14% nos vencidos/agendados; 63 cards de baixo rendimento (6,0%); 38 marcas de reforja abertas; 8 de 9 revisões direcionadas sem ler.
3. **Performance (medido 02/10):** 7.488 questões, 78,8%; faltam 2.512 em 30 dias (~84/dia) x ritmo real 5,3/dia (7d) e 11,6/dia (14d) -- 62 questões em 15 dias, em 2 dias de estudo; zona COBERTURA (58,3% da grade), desvio 10,2 pp, simulado em débito desde 20/09; UERJ 2021 aberta no hub com 10/60 respondidas.
4. **Discover -> PRD `.vibeflow/prds/feedback-cadeia-declarada.md`.** Diagnóstico do mecanismo atual com o dado do hub: 5 das 7 análises refeitas "com o racional declarado"; a letra marcada pinta o elo errado (t96 Q17: marcou A, elo 1 firme, lacuna real no elo 2, sem alternativa apontando para ele); cadeias que são julgamentos paralelos por alternativa (t96 Q8) ou com elo que engole 3 alternativas (t96 Q14); 8 chips perguntam causa, não elo.
   - **Erros nomeados por ele:** elo quebrado errado, cadeia mal construída, alternativa no elo errado, poluição visual.
   - **Decisões dele (perguntas fechadas):** modo escolhido por lista (Estudo = feedback após cada questão; Prova = só no fim; simulado sempre Prova); declaração obrigatória em errada, dúvida e chute (certa e sólida entra como Sim, ajustável); cadeia de lista cunhada antes de abrir, simulado só erradas e não-sólidas depois da prova.
   - **Decisão dele, no meio do turno (reverte em parte a de 26/09):** "Em caso de dúvidas sobre as habilidades, você pode CONFERIR o comentário/resolução do EMED via api, bem como checar nas apostilas/resumos, e criar a nossa própria sequência - desta forma nos mantemos autorais." Entrou no PRD: cadeia autoral; comentário só como lente de conferência, nunca no hub, no git ou no texto da cadeia. Nada mudou no `emed_api.py` nesta sessão.
   - **Propostas minhas no PRD (ele ainda não vetou nem confirmou):** 4 estados por elo (Sim / Incerteza / Desatenção / Não) no lugar dos 8 chips; porquê sob a própria alternativa; marca-texto de uma cor gravado com a resposta; paleta mantida; t40 e t49 recunhadas como caso de aceitação.

## Pendente

- `gen-spec` do PRD (5 itens de escopo, um por spec) quando ele der o OK; protótipo do grifo por toque no celular antes da spec do item 3.
- Selo da s210 e desta (HANDOFF/INDEX) no fechamento.
