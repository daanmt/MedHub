# Auditoria: reincidência na fila de "reforja" de flashcards (MedHub)

Read-only. `ipub.db` não foi escrito. Nenhum arquivo do repo foi editado.
Comandos rodados com `python -X utf8`. Repo em `C:\Users\daanm\medhub`, HEAD =
`5b1f682` (s170, sessão em andamento hoje 2026-09-08, `AUDITORIA_MEDHUB.md`
commitado às 12:19:19 local).

## 0. Onde a evidência mora (mapeamento)

Existem **dois mecanismos completamente distintos**, e o usuário está falando do
que NÃO tem estado no banco:

1. **`tools/cards_regen_queue.py`** (read-only, `--json`) — fila AUTOMÁTICA e
   queryable, mas o critério é `f.quality_source = 'heuristic' AND
   COALESCE(f.needs_qualitative,0) < 2` (`tools/cards_regen_queue.py:49`). Serve
   só cards **auto-gerados nunca revisados por humano**. TODOS os cards
   investigados nesta auditoria já têm `quality_source='qualitative'` (foram
   cunhados manualmente uma vez) — **estruturalmente invisíveis a essa fila**.
2. **A fila de "reforja" que o HANDOFF/sessões citam** — 100% prosa em
   `history/session_*.md` + `HANDOFF.md` + `AUDITORIA_MEDHUB.md`. **Não existe
   nenhuma coluna, tabela ou JSON que represente "card X foi marcado para
   reforja na sessão Y".** `flashcards.needs_qualitative` é outro eixo
   semântico (0=normal, 2=aposentado; não é "flagrado no drill").
   `PRAGMA table_info(flashcards)` confirma: sem `created_at`/`updated_at`.

O reescritor canônico (`tools/recurate_cards.py`) e o caminho alternativo
(`app/utils/db.update_flashcard_fields`, `app/utils/db.py:737-806`) **os dois
incrementam `card_version` mas nenhum chama `tools/event_log.py`** — conferido
lendo os dois arquivos inteiros; o único chamador de `event_log.registrar` é
`tools/insert_questao.py:39-41,298-299`, e só grava `tipo="generation"` /
`"reincidencia"` (cards NOVOS a partir de `questoes_erros`), evento não tem
relação com reescrita in-place. **Logo: quando uma reforja de fato acontece,
não sobra nenhum registro de QUANDO nem de QUAL flag ela resolveu — só o
`card_version` (sem timestamp) e a prosa da sessão.**

`.agents/workflows/curar-cards.md` é o workflow oficial (status: canonical) —
mas é um processo de **auditoria em lote, periódico** ("a cada N centenas de
cards"), não um dreno automático da fila per-sessão citada no HANDOFF.

## 1. Série histórica (sessão -> ids marcados para reforja, pendente ao fim da sessão)

| Sessão | Data (aprox.) | Cards marcados (fonte) |
|---|---|---|
| s134 | ~08/08 | 477,478,483,484,485,486,505,513,521 — "9 cards com defeito de autoria" (`history/session_134.md:46`) |
| s135 | — | mesmos 9, "seguem pendentes" (`history/session_135.md:42`) — carregado sem resolução |
| s140 | 08-11/08 | 15 cards sinalizados no drill; **resolvidos NA MESMA sessão** via `recurate_cards.py` (`history/session_140.md:17-21`) — inclui 175, 513, 71, 523, 477, 476, 499, 70, 284, 1126, 451, 483, 484, 485, 486 |
| s150 | ~20/08 | 1365, 649 — "autoria confusa -- reforja no fim de semana" (`history/session_150.md:21`) — **nunca mais mencionados** |
| s158 | ~30/08 | 321, 273, 293 — "Marcados para reforja de redação no backlog" (`history/session_158.md:29,49`) |
| s161 | 02/09 | 821, 702, 283, 505, 411 — "pergunta dupla" (`history/session_161.md` seção Cards para reforja) |
| s162 | 03/09 | Tabela "Fila de reforja — 15 itens" = os 5 da s161 + 570,128,705,1360,311,313,470,1415,1086,1126 (`history/session_162.md:155-166`) |
| s166 | 05-06/09 | 5 reforjados AO VIVO (245,667,741,577,311,313 — resolve 311/313 do item acima); **novos flagrados e deixados pendentes: 792, 4, 1117** (`AUDITORIA_MEDHUB.md:1372`) |
| s167 | 06-07/09 | 13 cards — 5 compostas (175,1041,1424,572,581) + 2 binárias (151,837) + 526,1112,258,910,527,513 — "Reforja pendente de todos os 12" [sic, lista tem 13] (`AUDITORIA_MEDHUB.md:1408`, `history/session_167.md:17`) |
| s168 | 07/09 | Sem novos; soma "13 da s167 + 18 anteriores" (`history/session_168.md:65`) |
| s169 | 07/09 | +7 novos (419,1424,582,583,1381,1359,367,365 — 8 ids p/ "7 cards" [sic]); soma "7 da s169 + 13 da s167 + 18 anteriores" (`history/session_169.md:71`) |
| HANDOFF.md (hoje) | 07/09 (linha ainda não girada p/ s170) | idêntico ao de s169 (`HANDOFF.md:41`) |
| **s170 (hoje, EM ANDAMENTO)** | 08/09 | 243, 792, 321 sinalizados de novo no drill; vira achado F81 (`AUDITORIA_MEDHUB.md:1469-1481`) — **ainda não entrou em nenhuma soma do HANDOFF** |

Reconciliação do "18 anteriores": bate com 13 remanescentes da fila de 15 da
s162 (15 − 311 − 313 resolvidos em s166 = 13) + 3 da s158 (321,273,293) + 2 da
s150 (1365,649) = **18**. Não é um número lido de lugar nenhum — é
contabilidade manual repassada de HANDOFF em HANDOFF.

## 2. Reincidentes confirmados (marcado pendente em ≥2 sessões distintas)

| card_id | Sessões que marcaram | Gap | `card_version` hoje | Evidência de que o MESMO defeito nunca foi corrigido |
|---|---|---|---|---|
| **#321** | s158 (flag inicial) → **s170 hoje** (F81, re-flagrado ao vivo pelo usuário) | ~12 sessões / ~9 dias | 2 | Texto ATUAL no banco (`SELECT frente_pergunta`) ainda é *"Por que um FAST com fígado aparentemente conservado não deve afastar..."* — exatamente o padrão "conclusão já asserida no enunciado" que F81 nomeia hoje (`AUDITORIA_MEDHUB.md:1474`). Defeito textualmente idêntico ao que motivou o flag em s158. |
| **#792** | s166 ("na fila de reforja", frente aberta, `AUDITORIA_MEDHUB.md:1372`) → **s170 hoje** (F81 eixo C, contexto contrafactual) | ~4 sessões / ~2-3 dias | **1** (nunca editado desde a criação) | `card_version=1` prova que NENHUMA reforja jamais rodou nesse card, apesar de 2 sinalizações distintas. |
| **#1424** | s167 (composta, `AUDITORIA_MEDHUB.md:1408`) → **HANDOFF hoje** (composta, de novo) | ~2-3 sessões | **1** | Mesmíssimo defeito ("composta"/sem resposta) citado 2x, `card_version` prova zero intervenção. |
| **#505** | s145 (reforjado — defeito "eixo único", resolvido de fato) → s161/162 (novo flag, "dupla") → carregado nos "18 anteriores" até hoje | 16+ sessões | 2 | Só 1 incremento de versão em toda a vida do card — coerente com a correção de s145 e **nenhuma** desde então; o flag de s161 nunca foi atendido. |
| **#293** | s154 (reforjado — subpadrão tautológico corrigido) → s158 (novo flag, "redação") → nunca mais citado | 4 sessões | 3 | Card já foi tocado 2x na vida, mas não há como provar (sem timestamp) se a 2ª edição atendeu ao flag de s158 ou é de outra origem — **não rastreável**. |
| **#513** | s134 (flag) → s140 (reforjado no mesmo dia) → **s167** (novo flag, "lista sem vinheta") | 33 sessões desde s134 | 2 | 1 único incremento de versão na vida inteira — coerente com o conserto de s140; o flag de s167 nunca foi atendido (ainda v2). |
| **#1126** | s140 (reforjado) → s150 → s162 (citado de novo na fila) | — | 3 | Reaparece em 3 pontos distintos da linha do tempo; sem timestamp não dá pra provar quantas dessas foram de fato atendidas — **parcialmente não rastreável**. |
| #1117 | s166 (flag, contexto contradiz pergunta) — mesmo padrão citado de novo por analogia em s167 para #1112, mas #1117 em si não foi re-flagrado nominalmente | — | **1** | Nunca editado; incluído aqui como corroboração do backlog nunca tocado, não como reincidência de flag nominal. |

**#365** também está duplicado dentro da MESMA janela s169→s170 (flag no
HANDOFF de ontem, confirmado hoje pelo scanner do F81 como o mesmo defeito
classe B) — não conto como "sessão distinta" porque é o handoff de ontem sendo
auditado hoje, mas reforça o padrão.

## 3. O loop fecha? (rastreabilidade)

**Não há nenhum sinal no banco que amarre "este card foi reforjado" a "esta
marcação específica".** `card_version` sobe, mas:
- não tem timestamp (schema confirmado, sem coluna de data);
- não tem log de evento (`recurate_cards.py` e `update_flashcard_fields` não
  chamam `event_log.registrar`);
- não referencia qual flag/sessão motivou a edição.

Para **#792, #1424, #1117, #1359, #1360, #1365, #649, #582, #583, #705, #570,
#821, #837, #910, #526, #527, #572, #581, #1041, #1112, #1086, #1381, #1415,
#419, #1537** (todos consultados, `card_version=1`) o veredito é direto:
**nunca foram reforjados desde a criação** — não é "não rastreável", é
confirmadamente zero.

Para os que têm `card_version` > 1 mas foram flagrados mais de uma vez
(#505, #293, #513, #1126), a resposta correta é **"não rastreável quando
exatamente"** — o sistema não guarda evidência de correlação entre a edição e
o flag que a motivou. Só a prosa da sessão (quando existe) resolve, e nem
sempre existe ("reforjado" sem dizer qual dos flags pendentes foi endereçado).

## 4. Tamanho do passivo hoje

- Soma literal citada no próprio `HANDOFF.md:41`: **7 (s169) + 13 (s167) + 18
  (anteriores) = 38 cards** marcados e não resolvidos.
- Essa soma **tem pelo menos 1 duplicata conhecida** (#1424 está nos "13 da
  s167" E de novo nos "7 da s169" — a lista de hoje não checou contra a de
  ontem antes de somar), então o piso real é **≤37 ids únicos**.
- **Mais 3 novos hoje (s170, em andamento)** — #243, #792 (2ª vez), #321 (2ª
  vez) — que ainda não entraram em nenhuma soma do HANDOFF porque a sessão não
  fechou. Passivo real na hora desta auditoria: **~40 cards**, sem contar o
  passivo estrutural maior que o F81 dimensiona hoje (26 cards no "eixo A" de
  contexto redundante, 10 no "eixo B", `AUDITORIA_MEDHUB.md:1474`) que ainda
  nem virou lista nominal.
- Nenhum desses 38-40 aparece em `cards_regen_queue.py` (critério errado,
  seção 0) — **não há CLI hoje que liste esse passivo de forma queryable**;
  a única fonte é grep manual em markdown, exatamente o que esta auditoria
  fez.

## 5. Diagnóstico de causa (por que o loop não fecha)

Não é falta de CLI — é um CLI que resolve bem o problema errado, mais uma
lacuna estrutural de estado:

1. **A marcação nasce e morre em prosa.** `HANDOFF.md:41`,
   `history/session_168.md:65`, `history/session_169.md:71` — o padrão
   "Reforja: N novos... Somar aos M da sessão X + K anteriores" é
   **contabilidade aditiva manual**, nunca subtrativa. Nada força o agente a
   verificar, antes de somar, se algum dos "anteriores" já foi resolvido —
   e nada IMPEDE duplicata (confirmado: #1424).
2. **O CLI automático existente filtra o bucket errado.**
   `tools/cards_regen_queue.py:49` — `WHERE f.quality_source = 'heuristic'
   AND COALESCE(f.needs_qualitative,0) < 2`. Todo card autorado manualmente
   (o que inclui 100% dos cards flagrados no drill, porque só chegam ao drill
   depois de passar pela cunhagem `qualitative`) é **invisível** a essa fila
   por desenho, não por bug.
3. **O reescritor canônico funciona, mas é invocado sob demanda, não
   automaticamente.** `tools/recurate_cards.py` é robusto (4 gates,
   all-or-nothing, `--dry-run` default) — mas exige que ALGUÉM monte
   manualmente o JSON de entrada a partir da lista em prosa. Não existe
   ponte entre "HANDOFF.md linha 41" e "arquivo JSON pronto pra
   `--from`". `.agents/workflows/curar-cards.md` é o processo formal, mas
   roda "periodicamente" (fases 0-5, multi-agente) — não por sessão, e as
   últimas ~7 sessões (163-169) não o rodaram nenhuma vez (zero menção a
   `recurate_cards --apply` fora de reforjas ao vivo pontuais).
4. **Quando a reforja acontece, não deixa rastro estruturado.**
   `tools/recurate_cards.py` (arquivo inteiro) e `app/utils/db.py:737-806`
   incrementam `card_version` mas não chamam `tools/event_log.py` e a
   tabela `flashcards` não tem coluna de timestamp
   (`PRAGMA table_info(flashcards)`, confirmado seção 0). Mesmo as reforjas
   que DE FATO aconteceram (ex.: s140, s166) só existem como prosa —
   auditável por grep, não por query.

**Conclusão:** a suspeita do usuário procede. A fila de reforja é
majoritariamente **um ritual de registro em texto** ("Reforja: N cards...
somar aos anteriores") sem gate que force o drain, sem CLI que a enxergue
automaticamente (o único CLI automático filtra por um critério que a exclui
por desenho), e sem timestamp/evento que prove execução quando ela de fato
acontece. Os casos concretos #321 (s158→s170, 9 dias) e #792 (s166→s170,
`card_version` ainda 1) mostram o card voltando a quebrar no drill com
essencialmente o mesmo defeito, exatamente como a hipótese descreve.
