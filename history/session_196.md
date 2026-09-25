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
- **Aulas enxutas no padrao da Pediatria** (3 subagentes): DMG 4.052 -> 3.017 · Hernias 6.128 -> 3.442 · Cancer de mama 3.770 -> 2.107 (commit `9fb153b`; corrigido cN3 supraclavicular ipsilateral = N3c/estadio III, nao IV; Klinefelter 47,XXY) · Autopsia UERJ 2023 40.054 -> 25.803 (`9250aa2`) · S17 34.361 -> 21.385 (`894c368`; 7 duvidas herdadas do original, ver relatorio -- ex.: CRB-65 "8,15%", IP do ducto venoso >1 x >1,5, Previne 1.000-4.000 x PNAB).
- **hub-backend:** tique 06:37 = `mesmo_lote` (painel) -> Version 13 (aula #877). Lote `2026-09-25a` trocado com **0 notas** por `2026-09-25b` (90 cards, teto novo, texto reforjado; `retidos_reforja` 0) -> **Version 14** -> `--confirmar`.

## Pendencias
- `resumos/[GIN] CA de Mama.md` ainda diz "supraclavicular ipsilateral = estadio IV" (errado; AJCC 8 = N3c).
- 5 duvidas clinicas acima -> `/pesquisar-evidencia` quando houver folga.
- hub-backend 13:10: republicado com o mesmo lote 2026-09-25b (painel: retencao 7d 89,4 -> 89,3) -> Version 15. Loop passou a 1/1h (job 1bf17f69, :07).
- hub-backend 18:1x: `2026-09-25b` gravado (78 validas · 0 quarentena · 13 defeitos: 10 "erro de portugues", 3 "card longo"; notas 4=55 3=4 2=2 1=17) -> fila de vespera `2026-09-26a` (56 cards, retidos 13) -> Version 16.
- **Teto 90 -> 100/dia, CAP 1.5 (150 em divida)** por decisao dele: *"podemos estipular 100 card/dia, com margem ate 150 em divida. esta muito prazeroso fazer os cards e efetivamente mais rapido."*
- Loop passou a 12/12h (`7 6,18 * * *`, job `f17aac11`): a sessao fica aberta como backend do hub.
- `2026-09-26a` drenado na mesma noite: 41 gravadas · 17 defeitos (10 portugues, 5 longos, 1 composta, 1 "excluir card" #601).
- **Revisao de portugues de TODOS os cards ativos** (8 subagentes x ~197 cards, so ortografia; + 2 subagentes de reforja p/ os 19 marcados): `recurate_cards.py --permitir-atomicidade --apply` = **996 refeitos, 1 aposentado (#601)**; ~8.500 correcoes (acento, crase, til/cedilha, digitacao). Diffs em `tmp/portugues_s196/diff_*.txt`. Marcas humanas abertas = 0 (restam 294 de detector).
- 🔴 **Bug meu (corrigido):** fechar marca via pipe do Git Bash gravou o motivo em mojibake ("portuguÃªs") -> 84 linhas `fechada` que nao casavam com a `marcada`; apagadas e refechadas com `PYTHONUTF8=1`. Licao: motivo com acento nunca passa por pipe do shell no Windows.
- Fila `2026-09-26b` (51 cards, texto revisado) -> Version 17.
- **PRD `.vibeflow/prds/hub-aba-analise.md`** (aba Analise: cartao por sessao, cadeia em degraus, veredito concordo/discordo/em parte; entrada pelo chat; so daqui para frente). Proximo passo: gen-spec + implementar.
- **Bancada EMED** (artifact privado, `db`): https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db, fonte `artifacts/bancada-emed.html`, modelo da *Bancada Reumato MedFlow*. Semeada: `control/hub` (instrucao de EXPLORAR + relatorio), `mensagens/m0001`, 48 listas pendentes S2-S5. PRD `.vibeflow/prds/banco-questoes-emed.md` para a s197 (Fable, contexto limpo). 🔴 limite de 5.000 docs por artifact = bancada e buffer; 🔒 conteudo EMED so no artifact privado e no `ipub.db`.
- **Fechamento formal** pedido pelo operador (~22h40): HANDOFF rotacionado para a s197; backend `/loop` 12/12h segue enquanto esta sessao ficar aberta.
