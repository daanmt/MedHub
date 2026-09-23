# Session 192 -- MedHub HUB v0: uma pagina so, fixada, com o Claude Code como motor

**Data:** 2026-09-22 (~19h30 -> ~23h) - **Ferramenta:** Claude Code (Opus 5.5 1M; 2 subagentes) - **Continuidade:** `session_191.md`

## 0. O que foi pedido
Sessao de ENGENHARIA re-bootada pelo `/ai-eng` (ai-eng-9c), com o veredito da reforma: GO no artifact runtime; 3 ALTERA (player INLINE no index, RD como arquivo derivado de `history/`, comandos por `db`); spec direto, sem discover. Fechamento, nas palavras do operador: *"Achei simplesmente excelente. O que esta em aberto ainda? Podemos encerrar a sessao e definir este o padrao a partir de agora?"*

## 1. O que foi feito
- **1o ato do HANDOFF:** o player de 22/09 tinha 1 nota (card #92 -> 1, 07:17 local). Gravada (`--record-lote --apply --expect 1`, revlog 3.070 -> 3.071) e o doc marcado `gravado_em` no `db` da pagina. **O #92 e card DEFEITUOSO:** a vinheta e CoAo critica (pulsos femorais ausentes, sopro interescapular, cianose so em MMII por canal D-E) e o card atribui a cianose a TGA, cuja cianose diferencial e REVERSA (MMSS > MMII); a regra-mestre diz que CoAo nao cianosa (falso no RN com canal). Marcado para reforja (`reforja.py --marcar 92`).
- **PRD sem discover** (`.vibeflow/prds/medhub-hub-2026-09-22.md`) = brief + as decisoes do `/ai-eng` casadas por conteudo + fatos do runtime lidos nos `.d.ts` do harness. **4 specs** (`medhub-hub-v0-part-1..4`), budget <= 6 arquivos.
- **Parte 1 (`c299eb4`):** `tools/hub.py` (nucleo puro + CLI `--build/--check/--extrair-lote`), `core/templates/hub.html` (3 abas), `player.html` com marcadores de regiao (fonte UNICA do player) e teclado so na aba Cards. 26 testes (golden do manifesto, propriedade de href, perturbacao aula removida -> null, cap 130 -> 120, celular sem sticky/nowrap).
- **Parte 3 (`d42a0af`):** F90 num commit -- `revisar.md`, `registrar-sessao.md` §6 (lapide de 22/09 REVERTIDA: mesma URL volta a ser invariante), `aula-base.md` §4, contrato `revisao-calibrada` **v1.7** (Clausula 15), 3 `TERMO-REVOGADO`, HANDOFF com a URL na linha 3.
- **Hub no ar:** https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr (fixado, description "NAO apagar", titulo "MedHub"). Lote `2026-09-22h` = 220 cards (210 vencidos + 10 novos; o teto do dia estava sobrescrito pelo operador em 22/09), 6 aulas, painel regenerado. 8/247 entradas.
- **DoD 7 provada por comando:** `ArtifactData` com `as_level: interact` escreve em `sessoes/*/notas` e e RECUSADO em `comandos` e `rd`; doc de teste apagado, re-list vazio. O servidor confirmou o teto: "1 of 5000 documents used".
- **Suite 960 -> 986; `auto_check --changed` PASSED** (16 checks; orfas do 1.10 seguem 127).

## 2. Decisoes (reportadas ao `/ai-eng`; ele deu GO nas 4 e acrescentou 3 notas)
- **A.** Aulas entram no v0 (eram v1a); RD segue v1a.
- **B.** `--record-lote` idempotente -- revista pelo `/ai-eng`: o revlog passa a gravar o MOMENTO DA REVISAO (ts da nota), porque com o relogio da gravacao `review_time >= ts` engoliria uma 2a nota em silencio e o FSRS calcularia o intervalo da hora errada (a nota das 07:17 gravada as 19:37 deslocou o due do #92 em 12h). Idempotencia por igualdade; revisao mais nova = FORA DE ORDEM, reportada; quarentena de doc estranho no writer.
- **C.** Poda do `db` no rito (teto de 5.000 docs): so a sessao que SAIU da aba, depois de releitura com 0 novas e 0 rejeitadas.
- **D.** "The owner meets every level": na conta compartilhada quem abre e OWNER; a regra do `db` protege de membro da org, e a fronteira real e o writer.
- **F (ao carregar o contrato de pagina).** O contrato documenta `fetch()` relativo de arquivo publicado junto, e nao navegacao do frame: aulas e painel abrem DENTRO da aba (iframe `srcdoc`), sem copia e sem link de volta.

## 3. O que ficou PENDENTE (e por que)
- **Parte 2 NAO entrou.** O subagente Opus rodou ~1h, fez ~30% e deixou o `record_review` QUEBRADO no meio (`quando` indefinido em `_aplicar_review`, o unico caminho de escrita do FSRS). Parei o filho, salvei o parcial em `tmp/medhub-hub-v0-part-2-wip.patch` (o leitor `estado_gravacao_player` + `ts` em `ler_notas`) e devolvi `db.py`/`fsrs_queue.py` ao HEAD (24 testes verdes). Decisao: nao terminar no fim de uma sessao longa -- mexe no caminho critico. **Gate no rito:** notas do hub nao sao gravadas, o lote nao e trocado e nada e podado ate ela entrar; esperar nao custa, porque com ela cada nota entra no FSRS no momento em que foi dada.
- **Parte 4 (medicao):** sessao nova (read -> list -> build -> publish), drill de >= 20 no celular com 1 aula aberta no meio, 2 fechamentos sobrevivendo.
- `/vibeflow:audit` formal: PARTIAL por construcao ate a parte 4; roda junto da parte 2.

## 4. Custo dos subagentes (fonte: `usage` do harness)
- Leitura integral das 6 aulas antes do publish (regra da ferramenta: nada e distribuido sem leitura INTEIRA), Sonnet: **378.575 tokens / 22 tool uses / 2,6 min** -- 5.338 linhas, 0 achados.
- Parte 2, Opus: **custo nao reportado** (morto por `TaskStop` depois de ~1h; a notificacao de kill nao traz `usage`).

## 5. Artefatos
`tools/hub.py`, `tools/test_hub.py`, `core/templates/hub.html`, `core/templates/player.html`, `pytest.ini`, `.claude/commands/{engenharia-cli,revisar,aula-base}.md` (+ espelhos), `.agents/workflows/registrar-sessao.md`, `core/contracts/revisao-calibrada-contract.md`, `docs/MEMORIA-AUDITORIA.md`, `AGENTE.md` (tabela 7.4), `artifacts/painel.html`, PRD + 4 specs, `HANDOFF.md`, `ESTADO.md`, este log.

## 6. Proximos passos
1. **Parte 2 antes de qualquer gravacao de nota do hub** (spec `medhub-hub-v0-part-2`; parcial em `tmp/`).
2. Operador: abrir o hub no celular, drenar, abrir 1 aula e voltar; SO DEPOIS apagar os artifacts avulsos (player P8qi... e as 4 aulas de 22/09).
3. Parte 4 nas proximas sessoes; v1a (RD como arquivo) antes de 01/11; v1b (comandos) depois.
4. Reforja do #92 (conteudo clinico invertido).
