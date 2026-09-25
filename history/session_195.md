# Session 195 -- Lote de 24/09 gravado (72 notas, 18 defeitos), 90 notas perdidas no celular (F130), hub V5 (quadro por semanas), fila retem defeito marcado (F132), export de vespera honesto (F131)

**Data:** 2026-09-24 (drill do hub: hospital, de manha, PERDIDO; refeito 19:58-20:5x; sessao ~12h50 tique + 20h-21h30, horario local) - **Ferramenta:** Claude Code (Opus 5.5 1M ate ~20h, depois Fable 5.1; 1 fork Opus/Fable para o quadro do hub) - **Continuidade:** `session_194.md`

---

## O que foi feito
- **Tique 12:58:** `--precisa-publicar` = `mesmo_lote` (painel de 24/09 + Hernias feita no quadro) -> hub Version 7 com o mesmo lote `2026-09-24a`. Publish recusado na 1a tentativa (sessao nao tinha lido a versao viva) -> `Artifact read` -> aceito. `--confirmar`, commit `a56262c`.
- **Incidente (F130):** ele fez os 90 cards no celular no hospital e perdeu tudo ao recarregar. O db nao tinha NENHUM doc com carimbo do hospital (so as 26 refeitas a noite, 19:58-20:07) -> o `db` nao subiu no aparelho e a pagina ficou em memoria com aviso miudo. Backend desligado NAO tem relacao (o tique so le). 64 revisoes perdidas, sem recuperacao.
- **Lote `2026-09-24a` drenado (refeito a noite): 72 validas gravadas · 0 rejeitadas · 0 FORA DE ORDEM · 18 defeitos** (`--record-lote --apply --expect 72`, revlog 3241 -> 3313, `marcas_reforja=18`). Distribuicao: 4 = 51 · 3 = 13 · 2 = 4 · 1 = 8 (vs 26 cards: 4 = 21). Nota 1: hernias novas #1720/#1723/#1729/#1730/#1731, Nefro #598, #827, #1456. Ele: *"os cards novos de hernia ficaram espetaculares"* (#1729-#1733 = regua nova: contexto 1 frase, 1 pergunta, verso 15-150 chars).
- **Defeitos (18) com o motivo dele:** composta 4 (#596, #1424, #637, #1623), dupla 1 (#91), circular 1 (#89), aberta/ampla 1 (#469), longo 3 (#40, #1089, #1139), contexto longo 1 (#741), estruturalmente ruim 2 (#65, #81), portugues 3 (#83, #829, #350), "marcar para exclusao" 2 (#720, #1059). #65/#81/#83/#89/#91 ja tinham marca do `2026-09-22h` -> **F132**.
- **"Agendado no mesmo dia da drenagem" (print dele) decomposto:** coluna qui 24 = 18 defeitos sem nota (vencidos de verdade) + 8 notas 1 (relearning, legitimo) + 6 notas 4 com previsao "24/09" = cards D~9,5-9,9 com 2-5 lapsos rated 4 < 24h depois de um 1 (formula de curto prazo do py-fsrs, S x 2,2 sobre S~0,5 d) -- gravados em 24/09 viraram due 25/09: o grafico andava 1 dia para tras porque a previsao e do dia do EXPORT (23/09 23h). **F131.** Parametros do FSRS NAO mexidos.
- **Engenharia (175 testes verdes no perimetro tocado):**
  - `core/templates/player.html`: espelho das notas em `localStorage` por sessao ANTES do db, `restaurarLocal()` no boot, `reenviarPendentes(docs)` quando o db abre, aviso FORTE (`.aviso.forte`) com o que fazer; `ts` por `Date.now()` (testavel); `deslocamento(n)` = dias entre `gerado_em` e a nota (ate 14, so para frente) aplicado a cada previsao.
  - `app/utils/db.py`: `RETIDO_REFORJA_SUBQUERY` + `retido_reforja_where(conn)` + `ids_retidos_por_reforja()`; aplicado em `get_cards_by_bucket` e `agenda_revisoes`; `preview_ratings(quando=)`. `tools/day_plan.py::_fsrs_counts` replica a clausula (painel: 104 -> 24 vencidos). Marca de detector NAO retem.
  - `tools/fsrs_queue.py`: `--export-player --para AAAA-MM-DD` (`relogio_para`: `db.agora` -> 06:00 do dia; `consumo_do_dia` por `db.hoje()`; `anexar_agenda(quando=)`; `gerado_em`/`sessao` = o dia); saida com `retidos_reforja` e `para`.
  - `tools/hub.py` + `core/templates/hub.html` + `core/hub_quadro.json` (fork): aba Aulas = `secoes_do_quadro` por semana (Atrasadas -> S2..S7) lendo `db.plano_listar` + `calendario_trilha` (read-only, fallback declarado), bloco = tema · peso · questoes · acao; `tarefas: [ids]` liga aula -> tarefas que prepara (dmg [26, 40]; topicos-pediatria [96, 100]); "feito" so em aula com `tarefa_id`. Aulas concluidas: `git mv` para `artifacts/arquivo/` (s17, cancer-de-mama, hernias, autopsia-uerj-2023) -> `null` no manifesto.
  - Testes: `test_player_js.py` (+4; harness com db falso sincrono; node por ARQUIVO -- `node -e` estourava 32 KB no Windows e derrubava os 14 testes com `FileNotFoundError`), `test_fila_prioritaria.py` (+2), `test_fsrs_queue_player.py` (+1), `test_hub*.py` (fork).
- **Tique 21:2x:** `nova_fila` -> fila de vespera `2026-09-25a` (`--para 2026-09-25`: 60 cards = 24 vencidos + 29 agendados p/ 25/09 + 7 novos; pool 63; retidos 63) -> hub **Version 8** (5 entradas: pagina + painel + 3 aulas) -> `--confirmar`.

## Padrões de erro identificados (sessao de questoes)
- Sem bloco de questoes hoje (0 q registradas em 24/09). Nos cards: o cluster Nefro (Acido-Base/Potassio) deu 4 em 24h depois do 1 de ontem -- curto prazo, nao consolidacao; a aula-base D10 continua devida antes do re-drill.

## Artefatos criados/modificados
- Hub https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr: Version 7 (12:58, mesmo lote) e **Version 8** (21:2x, quadro por semanas + fila 25/09; 4 aulas removidas do ar).
- `AUDITORIA_MEDHUB.md`: **F130, F131, F132** (RESOLVIDOS); F129 atualizado (+18 defeitos, veredito de comprimento).
- `.claude/commands/hub-backend.md` passo 6: fila de vespera = `--para`, nunca `--limit`.
- Memorias: `feedback_conteudo_curto_carga_cognitiva` (nova), `feedback_aula_descomprimida_preferencia` (restringida), `project_medhub_hub_pagina_unica` (V5 + incidente + backend manual).
- `tmp/player_2026-09-24a_notas.json` (90 notas), `tmp/player_2026-09-25a.json` (lote vivo).

## Decisoes tomadas
- **Dele:** backend do hub MANUAL ("manual, por hora"); aulas concluidas saem do hub (ficam so ped, dmg, mfc e as seguintes); aba Aulas por semanas com n de questoes por bloco; **conteudo mais curto em tudo** (cards, aulas, analises, reports).
- **Minhas (autonomia):** card com marca de reforja HUMANA aberta fica fora da fila ate fechar (63 cards); export de vespera so com `--para`; parametros do FSRS intocados (o intervalo de 1 dia apos 4 em card com 5 lapsos e o modelo, nao defeito); Autopsia UERJ 2023 arquivada junto (ele listou so ped/dmg/mfc como abertas).

## Proximos passos
- Ele drena o `2026-09-25a` de manha -> avisa -> tique.
- Reforja dos 63 retidos (padroes dele; regua = hernias #1729-#1733); acento para o `/ai-eng`.
- Aula-base D10 Acido-Base + Potassio (curta) antes do re-drill do cluster Nefro.
- Poda da colecao `sessoes/2026-09-24a/notas` no fechamento de cards.

## hub-backend (tiques)
- 2026-09-24 12:58 -- hub-backend: republicado com o mesmo lote 2026-09-24a (painel do dia 24/09; quadro: hernias feita) -> Version 7
- 2026-09-24 21:25 -- hub-backend: 2026-09-24a gravado (72 validas · 0 quarentena · 18 defeitos) -> 2026-09-25a no ar (60 cards, `--para 2026-09-25`) -> Version 8 (quadro por semanas; s17, cancer-de-mama, hernias e autopsia fora do ar)
