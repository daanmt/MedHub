# Spec: Hub integração -- part 2: o Painel lê `listas/*` + a lista leva à aula que a prepara

> Escrita em 2026-10-05 (s216). PRD: `.vibeflow/prds/hub-integracao-cortar-passos.md` (F2 + F4). Mapa: relatório do subagente de s216.

## Objetivo

Uma lista marcada como resolvida na aba Listas aparece resolvida também no Painel, na hora e sem publish; e cada lista da aba Listas tem o atalho para a aula que a prepara.

## Contexto

`marcarListas(db)` (`hub.html:1350-1368`) é uma closure de `iniciarQuadro`: faz `onSnapshot` de `listas`, casa por id do doc `"t"+data-tarefa` e aplica o selo "resolvida · registro pendente" só no quadro da aba Aulas. O Painel é um iframe `srcdoc` de mesma origem, carregado uma vez (`carregarPainel`, `:1395-1400`); `preparar` (`:482-537`) já injeta `<style>` e liga cliques no DOM dele. `painel._html_tarefa` (`painel.py:436-447`) emite `<li class="tarefa">` sem nenhum `data-*`. `qzItemLista` (`hub.html:1465-1466`) rende `<li><button data-qzl>` e o HTML é refeito a cada snapshot.

Efeito no E01: com o Painel lendo `listas/*`, uma lista concluída deixa de precisar de republish do `index.html` para aparecer concluída (o `painel.html` continua subindo no tique, ~38 KB).

**Fricção que esta spec remove:** a mesma tarefa aparecer resolvida numa aba e aberta em outra, e abrir a aula de uma lista por outra aba -- viciosa.

## Definition of Done

1. **`li.tarefa` do Painel carrega `data-tarefa`** (id do plano) em `_html_tarefa`; `_html_docs` (`painel.py:336-341`) continua sem `data-tarefa` (seletor dos testes e do template = `li.tarefa[data-tarefa]`). `test_tarefa_de_lista_com_aula_que_prepara_tem_os_dois_links` e os regex de `test_painel.py:300,310` reescritos (armadilha A6). Teste novo: `test_tarefa_do_painel_carrega_o_id_do_plano`.
2. **`marcarListasEm(doc, db)` é função de topo** (fora de `iniciarQuadro`, extraível pelo harness node -- A5), chamada (a) por `iniciarQuadro` para o quadro da Teoria e (b) por `preparar` quando `quadro.id === "hub-painel-quadro"`, injetando o CSS do selo como já se faz com `[data-backoffice]` e chamando `medir(quadro)` depois. Casa pelo campo `tarefa` do doc, não pelo id (`t49_1` conta -- A4). Teste: `test_lista_resolvida_pinta_o_painel_sem_publish` em `tools/test_hub_quadro.py`; `test_lista_resolvida_vai_para_concluidas_com_selo_sem_gravar` e `test_sem_leitura_de_listas_o_quadro_fica_como_o_build` passam.
3. **Ligações tarefa -> aula num JSON próprio** `<script id="hub-ligacoes" type="application/json">` `{tarefa_id: [{href, titulo}]}`, derivado de `ligacoes_do_quadro`, com marcador em `LUGARES_HUB` e em `trocas` de `montar_index` (A9: não mexer no `#hub-semanas`; `test_semanas_da_aba_questoes_usam_a_regua_do_quadro` passa intacto). A `projecao` (`hub.py:726-730`) passa a incluir o hash desse JSON (aula ligada nova = republish).
4. **Lista -> aula na aba Listas.** `qzItemLista` rende, ao lado do `<button data-qzl>` (irmão, nunca filho), um `<a class="qz-aula" data-hub-aula href=… data-titulo=…>` por aula que prepara a tarefa; o clique abre a Teoria e o leitor via `abrirAula(href, titulo)` (part 1). Sobrevive ao rerender do snapshot. Teste: `test_lista_tem_atalho_para_a_aula_que_a_prepara` em `tools/test_hub_render.py`; `test_listas_recolhem_e_sobrevivem_ao_rerender` passa.
5. **Mesmo publish da part 1.** Esta part sobe no mesmo publish da part 1 (senão o P06 regride: lista resolvida sumiria da Teoria sem aparecer no Painel). Registrado no session log.
6. **Suíte e harness.** `pytest tools/ -q` verde; `auto_check --changed` PASSED; sem Don'ts; celular: nenhum `nowrap` novo, `min-width:0` nos itens de lista com dois controles.

## Scope

**Arquivos (6):** `core/templates/hub.html` · `tools/hub.py` · `tools/painel.py` · `tools/test_hub_quadro.py` · `tools/test_hub_render.py` · `tools/test_painel.py`.

## Anti-scope

- Fechar e voltar após concluir (part 4). Marcar o item recém-concluído (part 4).
- Painel ler `quadro/*`, `sessoes/*` ou `respostas/*` (part 6).
- Mudar `capabilities`; o Painel já é lido pela mesma página que já lê `listas/*`.
- Rota S5-S7 ou Documentação do Painel.

## Technical Decisions

- **DOM direto, sem `postMessage`:** o srcdoc é de mesma origem e `preparar` já o manipula; `postMessage` adicionaria protocolo para nada.
- **Casar por `tarefa`, não por id:** o id do doc tem sufixo nas listas desdobradas (`t49_1`); o campo `tarefa` é o que o plano conhece.
- **JSON próprio para ligações:** o `#hub-semanas` tem teste de igualdade exata e semântica própria (régua); misturar criaria acoplamento falso.
- **Hash do JSON na projeção:** sem isso, ligar uma aula nova a uma tarefa não republicaria. Custo: 1 linha em `projecao`.

## Applicable Patterns

- Harness node de `test_hub_render.py` (`extrair_funcao`): `marcarListasEm` como função nomeada de topo.
- `warn-first-check.md`.

## Risks

- **Selo no Painel sem o iframe medido:** o Painel cresce em altura ao pintar; chamar `medir` depois do snapshot (já existe para `toggle`).
- **Snapshot antes do Painel carregar:** `marcarListasEm` guarda o último snapshot em variável de módulo e `preparar` aplica ao carregar (ordem não importa).
- **Conta sem `db` (link compartilhado, não-dono):** `listas` tem `read: admin`; o não-dono não vê selo, e a página segue como o build (comportamento de hoje).

## Dependencies

- `.vibeflow/specs/hub-integracao-part-1.md` (a assinatura `abrirAula(href, titulo)` e a aba Teoria).
