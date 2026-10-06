# Spec: Hub integração -- part 6: "Hoje ao vivo" no Painel (P08, v0 = só soma)

> Escrita em 2026-10-05 (s216). PRD: `.vibeflow/prds/hub-integracao-cortar-passos.md` (F6). Decisão dele: só soma, nunca substitui; teto, saldo e registro oficial seguem do tique.

## Objetivo

Ao abrir o Painel, o operador vê o número publicado de cards e questões de hoje mais o que a própria página gravou depois do publish, sem tique e sem backend.

## Contexto

O Painel é foto do publish. A página já grava: notas do lote em `sessoes/<sessao>/notas` (`{card_id, rating_primeira, ts, ...}`, o redrill mantém o `ts` da 1ª nota), respostas em `respostas/*` (`respondido_em`), listas em `listas/*` (`status`, `resolvida_em`). A página-mãe sabe o lote no ar pelo `<script id="lote">` (`{sessao, gerado_em, total, cards}`); o painel não sabe (roda antes do export, armadilha A15). `_html_dia` (`painel.py:379-433`) desenha `<b>N</b> de teto` sem âncora. `hash_painel` ignora só o trecho `<!--gerado-->…<!--/gerado-->` (A14). Dupla contagem (A16): num `mesmo_lote` com lote já DRENADO E GRAVADO (caso de 05/10: lote 05a gravado e ainda no ar), as notas já estão no revlog e no número publicado.

**Fricção que esta spec remove:** ler "Hoje: 0" depois de 150 cards e esperar o tique para confiar no Painel -- viciosa. Protege a virtuosa: nada aqui muda nota, teto ou fila.

## Definition of Done

1. **Âncoras no painel publicado.** `_html_dia` emite `<b data-vivo="cards" data-base="N">N</b>` e `<b data-vivo="questoes" data-base="M">M</b>`; o bloco Hoje carrega `data-sessao-gravada="<sessao>"` (lida de `tmp/hub/ultima_gravacao_hub.json`; vazio se não existe) e `data-gerado-iso` (o mesmo `gerado_em`, DENTRO do trecho `<!--gerado-->…<!--/gerado-->` que `hash_painel` ignora, senão todo tique vira `mesmo_lote` -- A14). Teste em `tools/test_painel.py`: `test_hoje_tem_ancoras_para_o_ao_vivo` e `test_hash_do_painel_ignora_o_carimbo_iso`.
2. **Cards ao vivo.** Função de topo `vivoCards(notas, lote, sessaoGravada)` (extraível pelo harness): se `lote.sessao !== sessaoGravada`, conta os `card_id` distintos com `rating_primeira` em `sessoes/<lote.sessao>/notas`; se igual, 0 (já está no publicado). Nunca filtra por timestamp (A16). Rende "+K" ao lado do número publicado com `title="desde o publish"`; K = 0 não rende nada.
3. **Questões ao vivo.** `vivoQuestoes(respostas, listasPendentesDeRegistro, hojeLogico)` conta respostas com `respondido_em` no dia lógico de hoje (`Date.parse`, nunca string -- A17) cujas listas NÃO estão concluídas no plano (o Painel sabe: `li.tarefa[data-tarefa]` sem classe de concluída, part 2). Consulta por `where("lista","==",id)` só para as listas abertas ou "resolvida · registro pendente" (A18: sem consulta por faixa; N listas pequenas). Rende "+K" do mesmo jeito.
4. **Nunca substitui.** O número publicado, o teto e o saldo não mudam; o "+K" é um `<span class="vivo">` separado; sem `db` (não-dono, offline) o Painel fica igual ao publicado. Teste: `test_ao_vivo_so_soma_e_nunca_altera_o_publicado` (harness node, DOM falso).
5. **Dupla contagem coberta por teste:** `test_lote_ja_gravado_nao_conta_duas_vezes` (sessao == sessaoGravada -> +0) e `test_lista_registrada_no_plano_nao_conta_as_respostas`.
6. **Celular e harness.** "+K" não quebra a linha do número a 390 px (`white-space` só nesse span curto); `pytest tools/ -q` verde; `auto_check --changed` PASSED; conferido em navegador real com db falso antes do publish.

## Scope

**Arquivos (5):** `tools/painel.py` · `core/templates/hub.html` · `tools/hub.py` (só se `montar_index` precisar expor `sessao` à página-mãe; hoje o `<script id="lote">` já basta) · `tools/test_painel.py` · `tools/test_hub_render.py`.

## Anti-scope

- Recalcular teto, saldo ou agenda na página. Substituir o número publicado. Gravar qualquer coisa no `db` a partir do Painel.
- Contar questão feita fora do hub (EMED direto): limite declarado no PRD.
- Pendências no Painel (P10). Mudar o tique, o export, `capabilities` ou `record-lote`.

## Technical Decisions

- **Sessão gravada como dado do publish, não timestamp:** comparar `ts > publicado` subconta (notas anteriores a um republish `mesmo_lote` não estão no revlog); comparar sessão é binário e já existe no marcador.
- **Questões por "lista não registrada" e não por timestamp:** o registro no plano é o único evento que move resposta para o número publicado; o Painel já carrega esse estado por tarefa (part 2).
- **Funções puras extraíveis:** permitem testar a regra sem navegador, como nas parts da cadeia declarada.

## Applicable Patterns

- Harness node de `test_hub_render.py`; `warn-first-check.md`; `feedback_metrica_auto_confirmante` (o teste de dupla contagem é a 2ª lente).

## Risks

- **Marcador ausente no build** (`tmp/` limpo): `data-sessao-gravada=""` -> conta o lote inteiro; no pior caso soma a mais por um tique. Aceito e documentado na DoD 1.
- **`respostas` grande:** consulta por lista, não coleção inteira.

## Dependencies

- `.vibeflow/specs/hub-integracao-part-2.md` (estado por tarefa no Painel) e `part-5.md` (o número publicado já é o lógico; sem isso o "+K" somaria sobre um número errado).
