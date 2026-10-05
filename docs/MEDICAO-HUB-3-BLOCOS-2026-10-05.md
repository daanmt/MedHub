---
type: discovery
status: active
---

# Medição -- o hub em 3 blocos sem redundância (P13)

> s215, 05/10/2026. Pedido do operador: *"painel = performance + cronograma + ritmo, bloco teoria = revisões + aulas do cronograma/tarefas pré-lista e bloco cards/questões de mão-na-massa"*, para *"evitar a redundância que ocorre hoje, de informação solta em tudo que é lugar"*. Medição só de leitura (subagente Opus, 291 mil tokens, 61 chamadas, 11,5 min pelo `usage` do harness) sobre o build de 05/10 06:21 (`tmp/hub/index.html` 341.294 bytes; `artifacts/painel.html` 37.796 bytes). As contagens da §1 foram conferidas pelo principal com `grep` nos dois arquivos (94 / 92 / 12 / 43 / 43). Linhas de código citadas valem para o commit `80830ad`.

## 1. Redundância medida

| # | Informação | Painel | Aulas | Cards | Listas |
|---|---|---|---|---|---|
| 1 | Tarefas da semana e atrasadas, com ação | sim (`painel.py:470`) | sim (`hub.py:441`) | -- | só as listas |
| 2 | Rota S5-S7 | sim (`painel.py:450`) | sim (seções 5-7) | -- | parcial |
| 3 | Lista com questões no hub | 43 links | 43 links | -- | as mesmas listas no `db` |
| 4 | Aula ligada à tarefa | `painel.py:96`, `:368` | `hub.py:375`, `:523` | -- | falta |
| 5 | Documento de análise | Documentação | Outras aulas | -- | -- |
| 6 | Semana atual e datas | `plano.py:952` | `hub.py:365` | -- | `hub.html:1208` |
| 7 | Saldo de cards do dia | 62 de 100 (relógio) | -- | 150 no lote | -- |
| 8 | Agenda de 7 dias | `db.agenda_revisoes` | -- | `agenda_base` (mesmo leitor) | -- |
| 9 | Simulado da vez | semana/rota | quadro | -- | "a da vez" |

- O cronograma aparece inteiro duas vezes: 92 tarefas S4-S7 no Painel (94 `li.tarefa` com os 2 documentos) e as mesmas 92 na aba Aulas. Só 12 delas são tarefa de aula.
- A mesma regra mora em dois ou três lugares: 2 leitores de `core/hub_quadro.json` (`painel._aulas_por_tarefa`, `hub.ligacoes_do_quadro`), 2 renderizadores de ação (`painel._acao`, `hub._html_item`), 3 réguas de semana (`plano.panorama`, `hub.semana_atual`, `secSemanaAtual`).
- Linha 7 diverge de verdade: o Painel conta pelo relógio (`realizado_do_dia`, `painel.py:181`) e o lote saiu com `--limit 150` pela decisão do dia de estudo (P09).

## 2. Desconexão

- O Painel é foto do publish (`painel.py:25-27`) e o hub o carrega uma vez por abertura (`hub.html:1395-1400`).
- O que a página já sabe ao vivo e o Painel ignora: `listas/*.status` (o quadro usa em `hub.html:1352`; a mesma tarefa aparece resolvida em Aulas e aberta no Painel), `sessoes/<sessao>/notas`, `respostas/*` de hoje, `quadro/*`, `analises/pendencias/itens` (P10).
- Atalhos que faltam: a aba Listas não leva à aula que prepara a lista (`qzItemLista`, `hub.html:1465`); o fim do lote de Cards não leva a nada; o "voltar" do leitor sempre volta para Aulas, mesmo quando o documento foi aberto pelo Painel.

## 3. v0 em 4 fatias (reorganização e fiação; nenhum dado novo, nenhuma regra nova de `capabilities`)

| Fatia | O que muda | Código | Testes | Risco |
|---|---|---|---|---|
| F1 Teoria só com teoria | `secoes_do_quadro` (`hub.py:390-474`) mantém só tarefa de aula e tarefa com aula ligada; rótulo "Teoria", `data-aba="aulas"` intacto (não mexe em `ABAS`, hash, `localStorage`) | ~45 linhas | 15 reescritos | médio |
| F2 Painel lê `listas/*` | `_html_tarefa` emite `data-tarefa`/`data-slug`; `marcarListas` sai de `iniciarQuadro` e é aplicado ao iframe do Painel em `preparar()` | ~45 linhas | 4 | médio; **sai no mesmo publish da F1**, senão o P06 regride |
| F3 Biblioteca daqui em diante | acaba o `git mv` para `artifacts/arquivo/`; "Outras aulas" + "Concluídas" viram "Biblioteca" (mesmo id `hub-quadro-feitas`); ritos `revisar.md:239`, `aula-base.md:82`, `_doc` do registro | ~30 linhas | 1-2 | baixo |
| F4 Listas -> aula que prepara | JSON derivado de `ligacoes_do_quadro` (tarefa -> aulas) num `<script>` próprio; `qzItemLista` ganha "abrir aula" | ~25 linhas | 0-1 | baixo |

Total: ~145 linhas de código, ~20 testes reescritos e ~5 novos, uma sessão de engenharia. Efeito no E01: lista concluída deixa de mudar o `index.html`; no `mesmo_lote` sobe só o `painel.html` (~38 KB em vez de ~341 KB).

Testes que caem (nomes sem o prefixo `test_`): `test_hub`: abas_curtas. `test_hub_quadro`: secoes_atrasadas_primeiro, cabecalho_da_semana, bloco_da_tarefa, feito_sai_riscado (CHECK `engenharia-cli.md:653`), simulado_ja_no_hub, lista_ja_no_hub, plano_mudou_republica, o_quadro_de_partida, lista_resolvida_vai_para_concluidas, sem_leitura_de_listas, aula_ligada_so_a_tarefa_concluida (F3), semanas_da_aba_questoes (F4, se o JSON crescer). `test_hub_render`: padrao_abre, semana_atual_vazia, toque_e_teclado, sem_storage, recontar. `test_painel`: rota_concorda_com_a_aba_aulas (CHECK `:593`, vira inclusão), rota_usa_o_mesmo_li, tarefa_de_lista_com_aula_que_prepara (regex).

## 4. Depois do v0

- **Hoje ao vivo** (P08, opção B de 28/09; dono /ai-eng): dado novo (o Painel embute a sessão do lote no ar; a página soma notas não gravadas e respostas de hoje, com regra contra dupla contagem). ~120 linhas + ~150 de teste; risco alto, interage com o P09.
- **Pendências no Painel** (P10): conta `analises/pendencias/itens`. ~60 linhas.
- **Fusão Cards + Listas** numa aba "Mão na massa": ~150 linhas de template, ~9 testes, mexe no teclado e no estado do drill. Risco alto no player.
- **Resumos na Teoria** (P03): conteúdo novo; lote S4 = 32 resumos, ~160 mil tokens de leitura no publish.
- **Higiene**: unificar os leitores do registro e as ações (a duplicação encolhe sozinha depois da F1).

## 5. Decisões do operador

1. 4 abas renomeadas (Painel | Teoria | Cards | Listas) ou 3 com Cards e Listas fundidas. Recomendação: 4 até 01/11.
2. Documentação (Dossiê, Autópsias) no Painel, como ele pediu em 03/10, ou na Teoria. Recomendação: só no Painel (análise de prova é performance).
3. Biblioteca reabre as 5 aulas arquivadas (712.744 bytes, ~200 mil tokens de leitura única, estimativa pela proporção do E01) ou vale só daqui em diante. Recomendação: daqui em diante; reabrir uma aula arquivada sob pedido.

Dependência externa: o "Hoje" de cards conta pelo relógio (teto 100) ou pelo dia de estudo (lote de 150)? É o P09, com o /ai-eng.
