# Session 210 -- Plano do dia + hub atualizado; loop do backend 1/1h

**Data:** 2026-10-01 (quinta, 08h30-) - **Ferramenta:** Claude Code (Opus 5.5) - **Continuidade:** `session_209.md`

---

## Pedido

"atualize o plano do dia e o artifact. hoje, finalmente, pego algo para estudar. mantenha o loop de 1/1h do backend."

## Feito

1. hub-backend: republicado com o mesmo lote 2026-09-30a (painel mudou: dia virou 01/10) -- Version 54. Lote 30a em 0/150 notas.
2. `/loop` do backend religado: cron de hora em hora (:07), sessao-only, expira em 7 dias.
3. hub-backend: 2026-09-30a gravado (138 validas · 0 quarentena · 12 marcas de reforja: 1404 774 214 522 1727 341 595 810 936 614 311 718) -> saldo do dia zerado (teto 100, consumo 138; divida 165 -> 30 vencidos); hub republicado com o mesmo lote drenado -- Version 55. Lote drenado entre 09h27 e 10h03 (36 min): 68x4 · 8x3 · 23x2 · 39x1.
4. hub-backend 11h09: lote drenado, saldo do dia zerado, painel igual -- no-op.
5. **Bug do player "volta no tempo"** (relato dele, com a copia JSON das 150 notas): db tinha 150/150, 149 identicas; o 714 tinha defeito so no aparelho. Marca do 714 gravada a mao (`--record-lote` da copia, `--expect 0`, marcas_reforja=1 -> 13 na fila de reforja). Hotfix `.vibeflow/hotfixes/2026-10-01-player-volta-no-tempo.md` (status partial: reproducao sintetica): mesclar aparelho+db (defeito vence, 1a nota fica), reenviar o que o db tem a menos, remontar a fila sempre que o db chega (o `if(!interagiu)` congelava a fila velha), ressincronizar ao voltar a aba. 3 testes red->green em `tools/test_player_js.py` (harness ganhou db ADIADO); suite 1289. Hub republicado com o player novo -- Version 56. Blind spot aberto: por que o set() do defeito do 714 nao chegou ao db.
6. **Bug 2 do player: redrill nao persistia** (relato dele: 61 cards na fila depois do redrill feito; 61 = todas as notas < 3 sem defeito). O hotfix 1 ampliou o alcance (a volta da aba passou a remontar a fila). Hotfix `.vibeflow/hotfixes/2026-10-01-player-redrill-nao-persiste.md`: redrill resolvido grava `redrill_ok` (aparelho + db), `montarFila` o pula. 1 teste red->green; suite 1290. Os 61 do lote 30a marcados `redrill_ok` no db do hub. Hub Version 57. Prova real do hotfix 1: o 714 chegou ao db em version 2 (reenvio do aparelho).
7. **Revisões direcionadas na aba Aulas** (pedido dele: "publicar como aula, dentro de um bloco especifico de revisoes direcionadas a partir dos erros nas listas/cards"). `hub.py`: tipo `revisao` sem tarefa pendente ganha a secao "Revisoes direcionadas" no topo do quadro (com "feito"); teste novo + 4 ajustados. 9 aulas `aula-rd-*` (3 subagentes em paralelo, ~565 mil tokens) cobrindo os 62 cards de nota 1-2 do lote 30a + erros recentes de questoes dos mesmos temas: vias biliares, hemostasia, lupus/SAF, hepato, DII/polipos, intensiva/sepse, pediatria, ortopedia/cirurgia, pilulas. Lidas inteiras antes do publish. Hub Version 58. `revisar.md` ganhou o passo 8a. Carimbo de `review_log` (Invariante B) NAO feito: a leitura e dele no hub; carimbar quando ele marcar "feito" fica como pendencia (o tique nao cobre revisao).
   - **Divergencias clinicas achadas (fora das aulas; decisao DELE):** (1) HBV imunotolerante: card "nao tratar" x resumo §3.8 ">30 anos HBeAg+ trata (PCDT)"; (2) card 868 "INR>2 dispensa encefalopatia" e regra PEDIATRICA (resumo §7.1 so adulto); (3) TGA: resumo Cardiopatias l.245 diz MMII > MMSS -- na TGA a cianose diferencial e REVERSA (proposta do subagente, fonte Park/Nelson); (4) hiperoxia: card 935 ">150" x resumo ">250"; (5) rastreio FIGO: resumo SHG l.30 sem PA media/fatores maternos (aula seguiu o card = FIGO 2019); (6) AAS: resumo "12-36 sem" x questao UERJ "antes de 16"; (7) West: questao ACTH x resumo vigabatrina.
   - **Resumos omissos:** sem resumo de Cirrose, DII, Cicatrizacao; criterios Kehr x biliodigestiva; PBE/albumina.
8. hub-backend 17h18: rd-dii-polipos marcada FEITA no quadro -> republicado com o mesmo lote 2026-09-30a (quadro mudou) -- Version 59. review_log carimbado (directed_review) nos temas 302 (DII) e 167 (Polipos).
9. hub-backend 19h09: fila de VESPERA 2026-10-02a no ar (100 cards, teto 100, 13 retidos p/ reforja) -- Version 60. Linha 3 do HANDOFF atualizada.
10. hub-backend 20h09: republicado com o mesmo lote 2026-10-02a (painel mudou: vencidos-agora subiu) -- Version 61.
