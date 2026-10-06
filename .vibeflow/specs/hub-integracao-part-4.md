# Spec: Hub integração -- part 4: concluir = fechar e voltar à origem (P14)

> Escrita em 2026-10-05 (s216). PRD: `.vibeflow/prds/hub-integracao-cortar-passos.md` (F5). Pedido dele: *"ao marcar/assinar uma lista, feedback, etc, automaticamente aquela página fosse fechada e voltássemos para a página anterior"*.

## Objetivo

Assinar um documento ou marcar uma lista como resolvida fecha a página e devolve o operador à aba de onde ele veio, com o item recém-concluído visível e marcado.

## Contexto

`abrirAula`/`fecharAula` (`hub.html:566-588`) só alternam `#hub-aulas-lista` e `#hub-leitor`; não trocam de aba nem guardam origem. O Painel abre um documento por `preparar` (`:496-507`): `ir("aulas", true)` (grava `medhub.aba`) e depois `abrirAula`. `assinaEnviar` (`:892-923`) grava por `pendGravar` e, no `.then`, chama `quadroMarcarFeito(slug)` (assíncrono, `:1342-1346`) antes de pintar "Assinado e concluído". `qz-concluir` (`:1919-1924`) grava `status: resolvida` e só troca a mensagem. `qz-voltar` (`:1532-1535`) chama `qzFim`/`qzFecharLista`. Armadilha A10: se `fecharAula` rodar logo após `pendGravar`, `assinaAbrir("")` zera `ASSINA.slug` e a guarda falha; `test_quadro_que_nao_salva_desfaz_a_tela_e_avisa` exige a página ABERTA quando o quadro falha.

**Fricção que esta spec remove:** o toque extra de "voltar" depois de cada conclusão e cair na aba errada -- viciosa. Protege a virtuosa: a assinatura continua um gesto explícito; nada é assinado por fechar.

## Definition of Done

1. **Origem registrada ao abrir.** `abrirAula` guarda `LEITOR.origem = {aba, scrollY}` (aba ativa ANTES de qualquer `ir`), nos dois tratadores de `a[data-hub-aba]` (`:1477-1479` e `:496-507`) e nos links `a.hub-aula` da Teoria. Função de topo `voltarOrigem()` (extraível pelo harness) faz `fecharAula()` + `ir(origem.aba)` + restaura o scroll; sem origem, volta para a Teoria como hoje.
2. **Assinar fecha e volta só depois do quadro responder.** Em `assinaEnviar`, `voltarOrigem()` roda dentro do `.then` de `quadroMarcarFeito` quando `ok === true`, após pintar "Assinado e concluído" (A10). Documento fora do quadro (`ok === false`, ex.: Dossiê): fecha e volta do mesmo jeito, após 600 ms com a mensagem "Assinado" visível. Falha de `pendGravar` ou do quadro: página aberta, mensagem como hoje. `test_quadro_que_nao_salva_desfaz_a_tela_e_avisa`, `test_assinar_a_leitura_conclui_o_item_do_quadro` e `test_assinar_nao_regrava_nem_inventa` passam; o harness ganha o stub de `voltarOrigem` (A11). Teste novo: `test_assinar_fecha_e_volta_para_a_aba_de_origem`.
3. **Lista resolvida fecha e volta.** Em `qz-concluir`, no `.then` do `update`, a página fecha a lista (`qzFecharLista`) e a aba Listas mostra a lista recém-resolvida com classe `qz-recente` por 1 rerender (`QZ.recente = lista`, A12) rolada para a vista. Falha: fica na tela de fim com a mensagem de erro, como hoje. `test_pendencia_trava_proxima_e_concluir` passa. Teste novo: `test_concluir_lista_fecha_e_marca_a_recente`.
4. **Item recém-concluído marcado na origem.** Na Teoria: o item `feito` já vai para a Biblioteca (part 3); ao voltar, a Biblioteca abre e o item recebe `qd-recente`. No Painel: `li.tarefa[data-tarefa]` da lista resolvida já recebe o selo (part 2); documento assinado recebe `qd-assinado` lido de `quadro/<slug>` quando existir, e de `analises/pendencias/itens/doc_<slug>` (status `assinado`) quando não (só o dono lê; falha silenciosa para não-dono -- A13). Teste: `test_documento_assinado_pinta_o_painel`.
5. **Celular:** o voltar restaura o scroll da aba de origem; sem `nowrap` novo. Conferido em navegador real a 390 px antes do publish (regra s211), com registro no session log.
6. **Suíte e harness.** `pytest tools/ -q` verde; `auto_check --changed` PASSED; sem Don'ts.

## Scope

**Arquivos (4):** `core/templates/hub.html` · `tools/test_hub_quadro.py` · `tools/test_hub_render.py` · `tools/test_hub_pendencias.py`.

## Anti-scope

- Fechar ao responder uma pergunta de documento (a resposta não conclui o documento; só a assinatura).
- Auto-assinar ao rolar até o fim. Fechar o player de cards ao fim do lote (fica como está).
- Mudar `pendGravar`, `quadroMarcarFeito`, `capabilities` ou qualquer coleção.

## Technical Decisions

- **Fechar só após o quadro responder:** a alternativa (fechar na hora e marcar depois) deixa a tela de origem sem o item marcado por até 1 s e quebra o teste do quadro que falha. 600 ms para documento fora do quadro = tempo de ler "Assinado".
- **Origem capturada antes do `ir`:** o Painel grava `medhub.aba = aulas` ao abrir; sem capturar antes, a origem seria sempre a Teoria.
- **`qz-recente` por estado, não por DOM:** o snapshot refaz o HTML; marcar no DOM se perde.

## Applicable Patterns

- Harness node (`extrair_funcao`, stubs em `test_hub_quadro.py:740-770`).
- `project_conferir_tela_no_navegador`: hub em scratch + db falso + Edge a 390 px.

## Risks

- **Scroll restaurado antes do iframe medir:** restaurar no `requestAnimationFrame` após `medir`.
- **Dono x não-dono em `analises/`:** try/catch e sem selo para quem não lê.

## Dependencies

- `.vibeflow/specs/hub-integracao-part-2.md` (selo no Painel) e `part-3.md` (Biblioteca).
