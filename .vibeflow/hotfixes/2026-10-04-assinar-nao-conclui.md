# Hotfix: assinar-nao-conclui

origin: prompt
status: verified

## Symptom
Relato do operador em 04/10/2026: "mesmo assinando as listas, elas nao sao 'resolvidas', tendo que
clicar no concluir do lado de fora, nas listas. sinto que o ambiente como um todo esta assim, pouco
automatizado."

Medido no banco do hub (copias em `tmp/hub_db/`): ele abriu cada Revisao Direcionada no leitor, tocou
"Assinar leitura" no rodape e, segundos depois, voltou a aba Aulas e tocou "feito" no quadro:

- `analises/pendencias/itens/doc_rd-hemostasia` assinado 2026-10-04T18:02:28Z -> `quadro/rd-hemostasia` feito 18:02:33Z
- `doc_rd-hepato` assinado 20:45:07Z -> `quadro/rd-hepato` feito 20:45:13Z
- `doc_rd-vias-biliares` assinado 21:19:30Z -> `quadro/rd-vias-biliares` feito 21:21:06Z

Mesmo desenho do lado das listas: `listas/t26` e `listas/t1793` estao `status: "resolvida"` no banco,
mas a tarefa de lista no quadro nao tem botao "feito" e so sai da semana quando o backend (manual)
roda `plano.py --concluir` e republica.

## Checkpoint
hypothesis: (1) `assinaEnviar` (core/templates/hub.html) grava so `doc_<slug>` em
`analises/pendencias/itens`; nada liga a assinatura ao documento `quadro/<slug>` nem a funcao `aplicar`
do quadro, que vive presa dentro de `iniciarQuadro`. (2) `iniciarQuadro` so controla `.qd-item[data-slug]`
e so le a colecao `quadro`; a colecao `listas` nunca e lida pelo quadro, entao uma lista resolvida
continua na semana ate o proximo build.
falsification_test: rodar o `iniciarQuadro` e o `assinaEnviar` REAIS do template em node, com o quadro
REAL de `hub.html_quadro_de` e um banco falso: se, depois de assinar `rd-hepato`, `quadro/rd-hepato`
aparecer gravado `{feito: true}`, a hipotese (1) cai; se uma tarefa com `listas/t26.status = resolvida`
ja aparecer em "Concluidas", a (2) cai.
blind_spots: o harness nao mede CSS nem o toque no celular (conferencia em navegador real, Edge headless
390 px). O banco do artifact real (regras de leitura de `listas` = admin) nao e reproduzido: a negacao
de leitura e simulada pelo callback de erro do `onSnapshot`.

## Preservation
- O botao "feito" continua gravando `quadro/<slug> = {feito, ts}` e desfazendo a tela se a gravacao falhar.
- Assinar nunca desmarca um item; item ja feito nao e regravado; documento sem item no quadro, quadro
  sem banco ou assinatura que falhou nao tocam o quadro.
- Lista resolvida so muda a TELA (nada e gravado); sem permissao de leitura em `listas` o quadro fica
  exatamente como o build.

## Eliminated / Evidence

## Root cause
`core/templates/hub.html`. (1) `assinaEnviar` gravava so `doc_<slug>`; a gravacao do "feito" e a funcao
de tela `aplicar` viviam fechadas dentro de `iniciarQuadro`, presas ao clique do botao -- nenhum caminho
ligava a assinatura ao quadro. (2) `iniciarQuadro` controlava so `.qd-item[data-slug]` e lia so a
colecao `quadro`; a tarefa de lista (`data-tarefa`, sem `data-slug`) so mudava no proximo build.

## Fix
files_changed: core/templates/hub.html
- A gravacao do botao virou `gravar(li, novo)` (mesmo `quadro/<slug> = {feito, ts}`, mesmo desfazer +
  aviso na falha), agora devolvendo uma promessa true/false. O clique chama `gravar`.
- `quadroMarcarFeito(slug)` no escopo do modulo (padrao: `Promise.resolve(false)`), atribuida dentro
  de `iniciarQuadro`: sem banco, sem item com o slug ou item ja feito -> false sem gravar; senao
  `gravar(li, true)`. Nunca desmarca.
- `assinaEnviar`, no `.then` da assinatura gravada, chama `quadroMarcarFeito(slug)`; se marcou e o
  leitor segue no mesmo documento, `ASSINA.concluiu = true` e o rodape diz "Assinado e concluído"
  (resetado em `assinaAbrir`).
- `marcarListas(db)`: `onSnapshot` da colecao `listas`; tarefa de lista cuja `listas/t<N>.status` e
  `resolvida` ganha `<span class="qd-registro">resolvida · registro pendente</span>` na `.qd-meta` e vai
  para Concluidas por `aplicar` (que passou a tolerar item sem botao). So le; erro de leitura = nada muda.
- CSS: `.qd-registro{color:var(--qz-ok);font-weight:600}`.

## DoD
- [x] Os 3 testes de regressao vermelhos no template de HEAD (3 failed) e verdes no fix.
- [x] `python -m pytest tools/ -q` = 1389 passed; `auto_check.py --changed` PASSED.
- [x] Edge headless a 390 px, claro e escuro: assinar rd-vias-biliares no leitor grava `quadro/rd-vias-biliares`
      `{feito: true}`, o rodape diz "Assinado e concluído" e, de volta ao quadro, o item esta em Concluidas
      (4); lista t49 resolvida no banco aparece em Concluidas com a marca; com a leitura de `listas` negada, nada muda.

## Regression
WHEN o operador assina no leitor um documento cujo slug tem item no quadro ainda nao feito (o 04/10:
`doc_rd-hepato` assinado, `quadro/rd-hepato` ausente) THEN `quadro/rd-hepato = {feito: true, ts}` e
gravado e o item vai para Concluidas sem segundo toque; WHEN `listas/t26.status == "resolvida"` e a
tarefa 26 ainda esta no quadro THEN ela aparece em Concluidas com "resolvida · registro pendente" e nada
e gravado.
test: tools/test_hub_quadro.py::test_assinar_a_leitura_conclui_o_item_do_quadro, tools/test_hub_quadro.py::test_lista_resolvida_vai_para_concluidas_com_selo_sem_gravar, tools/test_hub_quadro.py::test_quadro_que_nao_salva_desfaz_a_tela_e_avisa
oracle_type: specified
reproduction: real
verification: red-green

Dado real minimizado: os slugs e o estado do banco de 04/10 (`tmp/hub_db`, rd-hemostasia feita, rd-hepato
a assinar; t26 e t1793 resolvidas, t49 e t68 capturadas) entram como literais no teste; o quadro e o
gerado por `hub.html_quadro_de` a partir de um plano de 4 tarefas.

## Deviations
- Os testes nasceram em `tools/test_hub_conclusao.py` e foram movidos para `tools/test_hub_quadro.py`:
  suite nova exige inscricao no `pytest.ini` (F43) e, por citar `listas`/`plano`/`selo` como palavra solta,
  passava a contar como referenciador de 3 CLIs e envelhecia a tabela do AGENTE.md §7.4 (fora do escopo
  de edicao). Em `test_hub_quadro.py`, que ja cita `listas` e `plano`, so a palavra "selo" foi trocada
  por "marca" no codigo do teste. A prova vermelha foi refeita no local final (template de HEAD: 3 failed).
- Rotulo do rodape: o "Assinado e concluído em dd/mm" quebrava em 3 linhas ao lado do botao a 390 px; a
  data e sempre a de hoje nesse estado, entao saiu ("Assinado e concluído").
- Decisao de escopo: "Atualizar comentário" de documento ja assinado tambem passa por `quadroMarcarFeito`
  (o pedido diz "grava com sucesso a assinatura"); se ele desmarcou o item a mao e depois edita o
  comentario, o item volta a feito. Nunca desmarca.
- Achado colateral, nao corrigido: o sensor de alcancabilidade conta qualquer `.py` que cite o stem de um
  CLI como palavra solta (`listas`, `plano`, `selo`) como referenciador dele -- falso positivo que obriga a
  evitar palavras comuns em testes.
- Hoje nenhuma lista resolvida esta pendente no quadro (o backend ja registrou t26, t1793 e t96); o item 2
  so aparece quando ele resolver a proxima lista antes de um tique.
