---
type: session
layer: history
status: canonical
---

# Session 217 -- fila de 06/10 no hub + revisão dos ajustes da s216 com ele

**Data:** 2026-10-06 (manhã)
**Ferramenta:** Claude Code (Opus 5.5, principal). Operador presente.

## Hub

- hub-backend: lote `2026-10-05a` já gravado na s215 (150/150; releitura de 06/10: notas do db idênticas às gravadas, nada a regravar) -> `2026-10-06a` no ar (100 cards = teto do dia, consumo 0; 36 retidos p/ reforja). Hub **Version 75** (publish só de `painel.html` + página; 25 aulas intocadas). Listas: nenhuma resolvida nova (t26, t49, t96, t1793 já registradas). Pendências: nenhuma `respondida` (rd-hernias_q4/q20 seguem abertas).

## Revisão da s216

- A pergunta "F141-A" deixada para ele na s216 (card falhado só volta amanhã?) **já tinha resposta dele desde 28/09** (F140, s204) e está no código (`relearning_steps=()`); F141 e F142 (lado do hub) fechados na s207. A triagem E10 do /ai-eng re-derivou mecanismo resolvido (gate-miss de leitura, série 10.8: o ledger de resolvidos não foi consultado). Lápide em `docs/BACKLOG-PRODUTO.md` E10; resta só a guarda de mesmo dia no `--record` do chat.

## Pedidos dele (06/10, manhã)

- **Semana 2 sem exercício?** Nenhuma lista vazia: contadas no `questoes` do hub, todas com enunciado, alternativas e gabarito. Abaixo do previsto por motivo conhecido: t1 47/50 e t3 30/32 (discursivas ficam fora por regra do `emed_api`, número pula -- t3 Q24 conferida), t651 30/43 (a lista do EMED tem 30; 43 era estimativa).
- **Biblioteca por grande área (P17):** subagente Opus (365.349 tokens, 131 chamadas, 34,9 min pelo `usage`). `tools/hub.py` (`AREAS_BIBLIOTECA`, `grande_area()`, `data-area`, `html_biblioteca()`, aviso de item sem área no `--build`/`--check`), `core/templates/hub.html` (grupos recolhíveis, o "feito" do cliente cai no grupo certo, grupo vazio some), `bloco` nas 16 RDs de `core/hub_quadro.json`, `revisar.md` passo 8a (RD nasce com `bloco`) + `engenharia-cli.md`, espelhos regenerados. +10 testes. Ordem dele: CM, CIR, MFC, PED, GO; "Várias áreas" (pílulas) no fim. Conferido no Edge (iframe a 390 px, claro e escuro).
- **Aula TB 360 (#1797):** subagente Opus (328.854 tokens, 64 chamadas, 14,4 min), `artifacts/aula-tb-360.html`, 20 degraus nas 4 portas (CM, PED, CIR, MFC), ancorada nas apostilas EMED Inf/12 e Ped/33 + resumo TB; registrada com `tarefa_id: 1797`. O autor rodou `taskkill /F /IM msedge.exe` filtrado por título "about:blank" para fechar o Edge headless (avisado ao operador).
- **Evidência (6 divergências):** `evidence-researcher` Opus (428.836 tokens, 43 chamadas, 7,5 min); relatório cru em scratch `evidencia_tb.md`. **Aprovado por ele ("Aula + resumo"):** escore pediátrico <= 25 e desnutrição grave < p0,1/escore-z < -3 (Guia VS 2024); 4 meses na TB não grave da criança como banca-dependente (NI 5/2024); isoniazida 5-10 mg/kg máx 300 na ILTB (Guia 2024; NI 15/2024); IGRA no SUS desde 2020 para grupos (Portaria SCTIE 50/2020; NI 1/2023); TB-MDR = BPaL 6 meses, longo para não elegíveis, banca-dependente (Portaria SECTICS 49/2023; NI 1/2025, lida por fonte secundária). 1HP mantido como OMS. Aplicado na aula e em `Tuberculose.md` (+5 armadilhas; ALTEPE lapidado como gabarito antigo). Cards: varridos os 45 cards ativos de TB (`db.cards_ativos_para_predicado`), nenhum ensina a versão antiga -> 0 marcas de reforja.
- 🔴 **Spoiler achado:** `resumos/Pediatria/33. Tuberculose na Infância.pdf` p13 traz questão resolvida da UERJ 2022 (simulado de sábado). Avisado; a aula não a usa.
- Hub **Version 76** (`aulas/tb-360.html` + `painel.html`; 25 aulas intocadas); `hub.py --confirmar`. Suíte **1457** (`python -X utf8 -m pytest tools/ -q`); `auto_check --changed` PASSED.
