# Spec: Hub integração -- part 1: Teoria só com teoria + abas na ordem Painel | Teoria | Listas | Cards

> Escrita em 2026-10-05 (s216). PRD: `.vibeflow/prds/hub-integracao-cortar-passos.md` (F1 + reordenar). Mapa de código: relatório do subagente de s216 (linhas valem para o commit `3a492b4`).

## Objetivo

A aba "Aulas" vira "Teoria" e mostra só tarefas de aula e aulas ligadas a tarefas; o cronograma inteiro passa a existir em um lugar só (Painel); as abas ficam na ordem Painel | Teoria | Listas | Cards.

## Contexto

Hoje `secoes_do_quadro` (`tools/hub.py:390-474`) rende as 92 tarefas S4-S7 na aba Aulas, as mesmas 92 do Painel; só 12 são tarefa de aula (`plano.classe_da_tarefa`, `tools/plano.py:899-909`: `lista` | `caderno` | `aula` | `sem_lista`). Os 2 itens `analise` do registro (`dossie-uerj`, `autopsia-uerj-2021`) caem em "Outras aulas" E em Documentação do Painel. O "abrir aula" do Painel depende de achar `a.hub-aula[href]` no DOM da aba Aulas (`hub.html:501-505`): se o documento sair da Teoria, o Painel troca de aba e não abre nada (armadilha A1).

**Fricção que esta spec remove:** procurar a mesma tarefa em duas abas e ler 92 blocos para achar 12 aulas -- viciosa. Nenhuma virtuosa tocada (não muda recall, nota nem racional).

## Definition of Done

1. **Teoria só com teoria.** Na aba `aulas` (id e hash intactos), as seções Atrasadas / Semana N / S5-S7 contêm apenas tarefas com `classe == "aula"` e tarefas de qualquer classe que tenham aula ligada por `ligacoes_do_quadro` (prepara ou cumpre). Tarefa de lista sem aula ligada não aparece. Itens `tipo == "analise"` não aparecem em nenhuma seção da Teoria. Teste novo: `test_teoria_so_com_tarefas_de_aula_ou_com_aula_ligada` em `tools/test_hub_quadro.py`.
2. **Régua da semana intacta.** `semana_atual` continua recebendo TODOS os pendentes (o filtro é só de exibição, armadilha A2); `test_rota_concorda_com_a_aba_aulas` (`tools/test_painel.py:258`, CHECK em `engenharia-cli.md:593`) passa reescrito como inclusão: toda tarefa da rota do Painel que seja de aula existe na Teoria com o mesmo `li`.
3. **Painel abre documento sem link no DOM.** `abrirAula` aceita `(href, titulo)` e o tratador do iframe do Painel (`hub.html:496-507`) chama-o direto com o `href`/`data-titulo` do link clicado, sem procurar `a.hub-aula` na Teoria. Dossiê e Autópsia abrem a partir de Documentação. Teste: `test_painel_fala_com_as_abas` reescrito; novo caso em `tools/test_hub_render.py` com o harness node (`extrair_funcao`).
4. **Abas na ordem Painel | Teoria | Listas | Cards.** Botões em `hub.html:294-299` nessa ordem; rótulo "Teoria" no botão, no h2 (`:307`), no subtítulo (`:308`), no voltar do leitor (`:313`, "‹ Teoria") e no `title` do iframe. `ABAS`, ids `hub-tab-*`, `data-aba`, hashes e `localStorage` intactos. Navegação por setas segue a nova ordem do DOM. `test_abas_curtas_e_com_alvo_de_toque` e `test_abas_na_ordem_*` (`tools/test_hub.py:421-445`) reescritos para a nova ordem e rótulos.
5. **Projeção e tique inalterados.** `html_quadro_de` continua o caminho único de `construir` e `decidir`; `test_plano_mudou_republica_o_mesmo_lote` e `test_o_quadro_de_partida_e_o_do_dia` passam sem mudança de semântica.
6. **Suíte e harness.** `python -m pytest tools/ -q` verde; `python -X utf8 tools/auto_check.py --changed` PASSED; nenhum Don't de `conventions.md` violado; nenhum travessão, seta Unicode ou LaTeX no HTML gerado.

## Scope

- `tools/hub.py`: `secoes_do_quadro` ganha o filtro de exibição (depois de `semana_atual`); `item_tarefa` inalterado; "Outras aulas" continua existindo nesta part (a part 3 a transforma em Biblioteca).
- `core/templates/hub.html`: ordem dos botões, rótulos "Teoria", `abrirAula(href, titulo)` com a assinatura antiga preservada por sobrecarga (elemento OU par de strings), tratador do iframe do Painel chamando direto.
- `tools/test_hub.py`, `tools/test_hub_quadro.py`, `tools/test_hub_render.py`, `tools/test_painel.py`: reescritas nomeadas na DoD + os testes listados na medição §3 que citam "Aulas"/ordem.

**Arquivos (6):** `tools/hub.py` · `core/templates/hub.html` · `tools/test_hub.py` · `tools/test_hub_quadro.py` · `tools/test_hub_render.py` · `tools/test_painel.py`.

## Anti-scope

- Biblioteca, fim do `artifacts/arquivo/` (part 3). Selo de lista resolvida no Painel (part 2). Fechar e voltar (part 4).
- Qualquer mudança em `painel.py`, `plano.py`, `ABAS`, hashes, `localStorage`, player ou teclado do drill.
- Fusão Cards + Listas. Mudar a régua de semana.

## Technical Decisions

- **Filtro de exibição, não de dado:** `semana_atual` e `secoes_do_quadro` continuam vendo todos os pendentes; o corte acontece ao montar cada seção. Trade-off: a lista de pendentes segue sendo lida inteira (barato, é JSON local) em troca de manter uma régua só de semana (A2).
- **`abrirAula(href, titulo)` por sobrecarga:** o chamador da aba Teoria passa o elemento como hoje; o do Painel passa strings. Evita tocar os 2 tratadores de `a[data-hub-aba]` (`hub.html:1477-1479` e `496-507`) em semântica, só na chamada.
- **Reordenar só o DOM:** `ABAS` só valida por `indexOf`; o CSS `:root[data-aba]` não depende de ordem; as setas percorrem o DOM. Zero mudança de estado.
- **Rótulo "Teoria" com id `aulas`:** renomear id/hash quebraria `localStorage medhub.aba` dos aparelhos dele e 20+ testes sem ganho para o usuário.

## Applicable Patterns

- `warn-first-check.md`: `auto_check --changed` antes de reportar; CHECKs citados em `engenharia-cli.md:593` e `:653` continuam apontando para testes existentes (renomear = atualizar o CHECK no mesmo commit).
- Harness node de `test_hub_render.py` (`extrair_funcao`): toda função nova no template precisa ser extraível por chaves casadas.

## Risks

- **Documento some do hub se o Painel não o abrir (A1):** mitigado pela DoD 3 com teste de harness.
- **Teoria vazia numa semana sem aula:** a seção da semana mostra o texto vazio já existente (`qd-vazio`); sem seção nova.
- **Testes de ordem presos ao literal `var ABAS`:** reescrever o teste para checar a ordem dos botões, não o literal.

## References

- `docs/MEDICAO-HUB-3-BLOCOS-2026-10-05.md` §1-3: a medição que define o alvo (92 -> 12).
- `tools/test_painel.py:258` `test_rota_concorda_com_a_aba_aulas`: o sentinela da régua de semana.
