# PRD: Hub depois do tema v3 -- abas que não carregam, contador de cards e repetições

> Generated via discover on 2026-10-13 (s225), a partir do feedback dele ao avaliar o hub Version 104 (tema v3).
> Correção na próxima sessão. Regras de UI: `docs/UI.md`.

## Problem

Ao avaliar o tema v3 ("Ficou lindo, parabéns") ele apontou quatro problemas, três deles de uso diário:

1. **Aba que não carrega.** Às vezes, ao tocar em **Listas** (e às vezes **Teoria**), a tela fica em "Não consegui ler
   as listas. Recarregue a página." Fechar e abrir o artifact, já na aba, carrega o conteúdo. Causa provável, lida no
   código: `iniciarQuestoes` (`core/templates/hub.html`) assina a coleção `listas` **uma vez só** (`QZ.iniciado = true`);
   o callback de erro do `onSnapshot` escreve a mensagem e nada tenta de novo -- tocar na aba outra vez não refaz a
   assinatura. A Teoria tem o mesmo desenho na leitura do quadro. Gatilho provável (não medido): falha momentânea do
   banco ou a troca de versão do artifact com a página aberta (o hub foi republicado 3 vezes na s225).
2. **Cards divergentes.** O Painel mostra **"0 +3 de 150"** (o saldo do dia: teto 150, 178 vencidos) e a aba Cards
   mostra **"3/100 feitos · fila 98"**. O Painel é o referencial (palavra dele). A causa não é rótulo: o lote no ar é o
   `2026-10-10a` (100 cards, exportado em 10/10) e o backend do hub está manual -- nenhuma fila nova foi publicada
   desde então, então a aba Cards drena uma fila de 3 dias atrás com o tamanho daquele dia.
3. **Repetição e quebra de padrão.** Na Semana do Painel, "resolver no hub" (e "abrir aula") se repetem em toda linha
   e "da semana 4" em cada tarefa atrasada; a 1ª linha (Próxima) tem botão cheio e as outras, links. Nas Listas, o chip
   "pronta" aparece em todas as linhas: informação nula repetida 70 vezes.
4. **Marca pequena.** "MedHub" no topo (1,125rem) pode ser um pouco maior.

Achado relacionado (subagente da ferramenta de capturas, lido no código, não medido no hub real): sem o espelho local
`medhub.respostas.<lista>`, o 1º snapshot de `questoes` chega antes do de `respostas`; com o modo já escolhido, a Q1
aparece como nova mesmo respondida. Mesma família do item 1 (ordem e falha das assinaturas).

## Target Audience

Ele: abre o hub no celular, entre plantões, como a única superfície de estudo, a 19 dias da UERJ (01/11). Cada tela
que não carrega ou número que não bate custa confiança no instrumento.

## Proposed Solution

1. **Abas resilientes.** Toda leitura do banco que alimenta uma aba (listas, quadro da Teoria, respostas, notas dos
   cards) refaz a assinatura sozinha quando falha, com espera crescente, e também ao reabrir a aba. Enquanto tenta, a
   tela diz que está carregando; esgotadas as tentativas, a mensagem diz o que fazer e oferece **Tentar de novo**.
2. **Cards = contador do dia + fila diária** (decisão dele, 13/10). O bloco Cards mostra o **mesmo contador do Painel**
   (feitos hoje de saldo do dia, ex.: "3 de 150"); a fila do dia é renovada quando o dia vira -- o lote de um dia
   anterior nunca fica no ar como fila de hoje.
3. **Semana do Painel no padrão da Teoria** (decisão dele, 13/10; padrão P21): a linha inteira abre a lista no hub; a
   aula vira ação pequena, só quando existe; as atrasadas ficam sob o subtítulo **"Atrasadas · N"** (o aviso aparece
   uma vez, sem "da semana N" por linha); a Próxima se destaca pelo rótulo, sem controle de tipo diferente.
4. **Listas: estado só quando foge do normal** (decisão dele, 13/10). Sem chip para "pronta"; "em andamento" com
   respondidas/total; "resolvida" com ✓.
5. **Marca maior**: por volta de 1,375rem, mantendo "Hub" em rosa.

## Success Criteria

- Com o banco falso forçando erro no 1º `onSnapshot` (`leitura=1x`), a aba Listas e a Teoria se recuperam sozinhas em
  até ~5 s, sem recarregar; com erro permanente (`leitura=0`), aparece **Tentar de novo** e o botão funciona.
- No 1º acesso de um dia novo, a aba Cards e o Painel mostram o mesmo número (ex.: "0 de 150"), e a fila é a do dia.
- Semana do Painel: um alvo principal por linha; "resolver no hub" não aparece como texto repetido; "da semana N"
  aparece 0 vezes por linha; a Próxima segue o padrão das outras linhas.
- Listas: nenhum "pronta" visível; "em andamento" e "resolvida" continuam visíveis com texto.
- Conferido em navegador real com `python tools/ui_capturas.py` (390, 768 e 1280 px) e nas suítes do hub e do painel.

## Scope v0

1. Retentativa das assinaturas do hub (listas, quadro, respostas, notas) + estado de carregamento + Tentar de novo.
2. Bloco Cards com o contador do dia (mesma conta do Painel) e renovação da fila no 1º tique do dia.
3. Semana do Painel: linha clicável, aula como ação secundária, subtítulo "Atrasadas · N", Próxima só pelo rótulo.
4. Listas: chip só nos estados fora do normal.
5. Marca "MedHub" maior.

## Anti-scope

- Algoritmo FSRS, teto do dia, regra P09 (o lote conta no dia da 1ª nota) e o caminho de escrita (`--record-lote`).
- Botão na página que dispara backend ou agente (barrado pelo classificador na s194, "Create Unsafe Agents").
- Paleta, tipografia e outras telas (o tema v3 fica como está); a camada de leitura das aulas (outra frente).
- Reescrever o banco falso ou a ferramenta de capturas (já versionados na s225).
- Mudar o que conta como "atrasada" ou a ordem do plano.

## Technical Context

- **Assinaturas** (`core/templates/hub.html`): `iniciarQuestoes` (~l.1903, `listas`, uma vez só por `QZ.iniciado`);
  leitura do quadro da Teoria (~l.1831); `claude.use("db")` das pendências (~l.814) e dos grifos (~l.1193);
  `painelListas` / `painelVivo` (~l.1490-1550) somam o "+K" ao vivo no Painel; o espelho local das respostas é
  `qzChave()` = `medhub.respostas.<lista>`. O banco falso do `core/templates/ui_harness.html` já simula falha de leitura
  (`leitura=0` / `1x`, herdado do harness da s213).
- **Contador de cards**: Painel = `tools/painel.py` `_html_dia` (`consumo_hoje`, `teto`, `vencidos`) + `vivoCards` no hub;
  aba Cards = `core/templates/player.html` (`#feitos`, `#total`, `#pendentes`, do lote injetado). Fila do dia =
  `fsrs_queue.py --export-player` (saldo do dia, P09) e o rito do `/hub-backend` (`hub.py --precisa-publicar` decide
  `nova_fila` | `mesmo_lote`); o tique só roda com uma sessão do Claude Code aberta no PC (backend manual).
- **Semana do Painel**: `tools/painel.py` `_html_semana`, `_html_tarefa`, `_acao` (os links "resolver no hub" /
  "abrir aula"); o destaque da Próxima é CSS (`[data-bloco="semana"] > .tarefas > .tarefa:first-child`). Os testes de
  `test_painel.py` casam `<li class="tarefa" data-tarefa="N">` por regex -- manter essa forma. O hub marca no Painel a
  lista resolvida por `data-tarefa` (`painelListas`).
- **Chip das listas**: `qzItem` / `qzItemSim` e `ROT_QZ` no hub; CSS `.qz-chip` (a "pronta" já está quieta desde o v3).
- **Marca**: `.hub-marca` no `hub.html`.
- **Regras**: `docs/UI.md` (semântica de cor, contratos travados por teste §7, coluna única); conferência em navegador
  real antes de publicar (`docs/UI.md` §8, `tools/ui_capturas.py`).

## Open Questions

- Gatilho real da falha de leitura: medir antes do fix (log no console do erro do `onSnapshot`, com o código) ou já
  entrar com a retentativa genérica? Proposta: as duas coisas na mesma spec.
- Quem renova a fila no dia em que o PC não liga: hoje só o tique (sessão aberta). Opções a decidir na spec: fila de
  véspera (`--export-player --para <amanhã>`) publicada no fechamento do dia, ou a aba Cards mostrar "fila de hoje
  ainda não publicada" ao lado do contador do Painel.
- O que a aba Cards mostra quando a fila do dia ainda não saiu: o contador do Painel + aviso, ou a fila velha marcada
  como "de ontem"?
