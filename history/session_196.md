# Session 196 -- Aula #877 em topicos, reforja dos 63 cards marcados, teto 90, aulas enxutas, backend em /loop

**Data:** 2026-09-25 (sessao ~06h30-, horario local; ele fora, no hospital) - **Ferramenta:** Claude Code (Opus 5.5 1M; subagentes: 1 fork + 3 reforja + 3 aulas) - **Continuidade:** `session_195.md`

---

## O que foi feito
- **Boot:** panorama entregue (S2, 21 tarefas/511q, 3 atrasadas; ritmo 23,2 x 86,9 q/dia; zona COBERTURA). Ele: foco em DMG #26 + Pediatria #96 + aula #877.
- **Aula #877 (Raciocinio diagnostico) em topicos** (fork): corpo 6.057 -> 3.560 palavras, prosa 32 -> 0. Commit `1760dae`.
- **Backend ligado a pedido dele** ("a ideia e que o progresso fique salvo"): `CronCreate 7,37 * * * * /hub-backend` (job `55e890bf`, sessao-only, expira em 7 dias).
- **Teto de cards 60 -> 90/dia** (*"pode subir o limite para 90 cards tambem"*): `TETO_BASE = 90`, `CAP_MULTIPLICADOR = 1.0` (135 em divida reinstalaria o pico-e-queda). Contrato `fsrs-management-contract.md` + 2 testes reescalados. Suite 1088 verde. Commit `91c438f`.
- **Reforja dos 63 cards de marca humana** (3 subagentes, regua `feedback_conteudo_curto_carga_cognitiva`): `recurate_cards.py --apply` = **61 refeitos, 2 aposentados** (#720, #1059: "marcar para exclusao" dele); `insert_card_extra.py --apply` = **15 extras** (2o conceito de card empacotado; 1 pulado: #469 e andaime sem questao). Extras DESCARTADOS por fato incerto: #81 (limiar de FC do CRASH-2), #65 (corte de albuminuria diverge da KDIGO), #784 (gabaritos contraditorios sobre QRS). Correcao de conteudo: #91/#92 (vinheta = CoAo critica; TGA = cianose diferencial reversa). 83 marcas fechadas/descartadas; marcas humanas abertas = **0** (restam 294 de detector: nao_atomico/comprimento_total). Backup antes (`backup_db.py`).
- **Duvidas clinicas registradas (nao resolvidas):** #1113 (eco fetal 28 sem x AHA 18-24), #1176 (queda de beta-hCG 53% x 35%), #373 (notificacao semanal de CJD), #65 (amputacao contraindica a classe?), #55 (idade de rastreio SBD). Arquivos em `tmp/reforja_s196/duvidas_*.json`.
- **Aulas enxutas no padrao da Pediatria** (3 subagentes): DMG 4.052 -> 3.017 · Hernias 6.128 -> 3.442 · Cancer de mama 3.770 -> 2.107 (commit `9fb153b`; corrigido cN3 supraclavicular ipsilateral = N3c/estadio III, nao IV; Klinefelter 47,XXY) · Autopsia UERJ 2023 40.054 -> 25.803 (`9250aa2`) · S17 (em andamento neste registro).
- **hub-backend:** tique 06:37 = `mesmo_lote` (painel) -> Version 13 (aula #877). Lote `2026-09-25a` trocado com **0 notas** por `2026-09-25b` (90 cards, teto novo, texto reforjado; `retidos_reforja` 0) -> **Version 14** -> `--confirmar`.

## Pendencias
- `resumos/[GIN] CA de Mama.md` ainda diz "supraclavicular ipsilateral = estadio IV" (errado; AJCC 8 = N3c).
- 5 duvidas clinicas acima -> `/pesquisar-evidencia` quando houver folga.
