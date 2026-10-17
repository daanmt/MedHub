# Session 230

**Data:** 2026-10-17 (sábado; tique da noite de 16/10 já commitado em `4cb0790`)
**Ferramenta:** Claude Code (Opus 5.5)

- hub-backend: 2026-10-16a gravado (4 válidas · 0 quarentena) -> 2026-10-17a no ar (100 cards) -- Version 127
- banco-emed: t393 registrada 50 · acerto 72,0% (sessao 230, bulk #147, contada em 16/10 por decisão dele -- "o dia de hoje começa do zero"; respostas de 14-17/10); #393 concluída
- análise t393 (1 subagente Opus): erros #1240-#1253, cards #2134-#2156 (23; Q51 banca-divergente sem card do erro, card #2156 McBurney x Blumberg), desatenção #3946-#3948, 25 docs `analises/t393_*`. Achado: 5 das 14 erradas eram questões já erradas antes (Q30=#570, Q23=#712, Q3/Q43/Q49 de 21/08) com cards passando no FSRS -> cards novos miram o elo não coberto. Grifos: a ORDEM é o código (último bloco = comando), não a cor
- sprint recalculado (pré-autorizado por ele): 36 linhas; hoje = só o simulado UERJ 2024; listas de hoje deslizaram (18/10: #144, #651, #879, #5426)
- evidence-researcher (2): Meckel incidental no adulto = não ressecar de rotina (Zani 2008, Park 2005) -> armadilha em `Cirurgia Infantil.md` §14; t393 Q40 gabarito D se sustenta (TG18 grau I, apto) -> colecistite: timing sem teto TG18, ASA E Charlson, Tokyo III CCI <= 3, via aberta sem vídeo
- hub: RDs lidas recolhidas atrás de "Ver lidas (N)" e RD aberta 1x só no grupo Revisões direcionadas (pedido dele, print) -- conferido em Edge 390/1280; `test_rds_lidas_saem_da_frente_das_abertas`; Version 128-129; suíte 1812
- referências das 5 RDs 1510 completadas (subagente): AAP Down 2011/2022, Csendes 1989, ATLS 10, AO Spine 2017, SSC 2021, PCDT-IST 2022 -- commitado (`3b558e7`), NÃO publicado (ele em simulado); vai no próximo publish. 3 divergências (Wilms mediana 3 a; ADA > 10% ou >= 300; clamídia azitro x doxi) NÃO corrigidas por decisão dele (RD é descartável) -> ir para o resumo canônico depois de 01/11
- backlog de produto: P29 (lista/cards atravessando o dia), P30 (discriminadores pré-destacados + elo de descarte p/ toda alternativa), P31 (resumo canônico por tema EMED, RD descartável, registro único de referências; DECIDIDO "resumo = canônico"); P27/P28 marcados no ar
- memória: recalcular rota = pré-autorizado; referências sagradas (+ banco de evidências do daktus-content; hierarquia pela bibliografia do edital de cada bloco)
- custo: 4 subagentes (análise t393 Opus ~262k tok/9 min; 2 evidence-researcher Sonnet ~49k + ~77k; refs RD Opus ~131k)
