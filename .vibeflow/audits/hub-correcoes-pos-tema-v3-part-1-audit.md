## Audit Report: hub-correcoes-pos-tema-v3 -- part 1 (abas que se recuperam sozinhas)

> Auditado pelo DIFF do commit `d7be259` (`git show d7be259`), não pela árvore. 13/10/2026 (s226).
> Na hora da corrida, `core/templates/hub.html` da árvore = HEAD (a part-2 ainda não tinha tocado nele),
> então os testes rodaram sobre o código auditado.

**Verdict: PASS** (com 3 achados de baixa gravidade, não bloqueantes)

### Testes
- `python -X utf8 -m pytest tools/test_hub_render.py tools/test_hub_quadro.py tools/test_painel.py -q` -> **208 passed**.
- Suíte inteira não rodada nesta auditoria (fora do pedido; outro subagente edita a árvore).

### DoD Checklist
- [x] **1. UMA função resiliente, 5 assinaturas por ela** -- `assinarResiliente(consulta, onDados, opts)` (hub.html ~l.1645, 1 definição);
  `listas` (`iniciarQuestoes`), `quadro` (`iniciarQuadro`), `questoes`/`respostas`/`analises` (`qzAssinarLista` em `qzAbrir`).
  `grep onSnapshot(` no hub de d7be259: só restam l.943 (pendências), 1019 (assinatura), 1490/1561/1577/1583/1622/1629
  (`LISTAS_VIVAS`, painel ao vivo) -- todos anti-escopo. Travado por `test_leituras_das_abas_passam_pela_assinatura_resiliente`.
- [x] **2. Log + 1/2/4 s + "Carregando…" + Tentar de novo + reabrir reinicia** -- `console.warn("[hub] leitura " + nome + " falhou", code, tentativa)`;
  `ESPERAS_LEITURA = [1000, 2000, 4000]`; `aoEsperar` escreve "Carregando…"; `aoMorrer` -> `htmlRetentar` (`button.primario`).
  Reabrir: Listas via `QZ.iniciado=false` no `aoMorrer` + `iniciarQuestoes`; Teoria via `ir("aulas")` com `estado()==="morta"`.
  Testes: `test_listas_se_recuperam_da_falha_de_leitura`, `test_botao_tentar_de_novo_reassina` (esperas [1000,2000,4000], avisos 1..4).
- [x] **3. Banco falso `leitura=1x|0` + 2 testes nomeados** -- `ui_harness.html` ganhou `?leitura=1x|0` e `window.uiLeituraBoa()`;
  os dois testes existem e passam. Ressalva (achado A3): os testes usam um banco falso próprio em node que IMITA o harness;
  o parâmetro do `ui_harness.html` em si não é exercitado por nenhum teste nem pelo `ui_capturas.py`.
- [x] **4. Chip** -- `qzChip`: `capturada` -> ""; em curso -> `em curso n/total` (espelho `medhub.respostas.<lista>`); resolvida com ✓ (CSS).
  `test_chip_da_lista_so_fora_do_normal`.
- [x] **5. Marca** -- `.hub-marca{...font-size:1.375rem...}`, `.hub-marca span{color:var(--rosa)}` (mesmo teste).
- [x] **6. Artesania** -- nenhuma cor literal nova no diff (só `var(--…)`); testes de contrato de cor verdes; nenhum Don't de
  `conventions.md` tocado; `tmp/ui_capturas/s226p1/resultado.json` (11:13, antes do commit 11:21): 11 cenas x 390/768/1280,
  `rola: false`, `erros_js: []` em todas.

### Pattern Compliance
- [x] `docs/UI.md` §4: botão de ação = `.primario` (ciano); aviso âmbar reaproveitado (`hub-quadro-aviso`, `qz-aviso-lista`).
- [x] §5: componente "Leitura resiliente" registrado (diff de `docs/UI.md`); §7: linha com os 4 testes; §10: A18/A21/A22 resolvidos; §11: histórico.
- [x] Risco "2 ouvintes": geração (`st.ger`) + `soltar()` antes de reassinar + unsub tardio descartado; testes contam `ATIVOS == 1`.

### Achados (todos não bloqueantes)
- **A1 (baixa, confiança média)** `core/templates/hub.html` `qzAvisoLeitura` (~l.2131): as 3 leituras da lista aberta dividem UM aviso
  (`data-leitura` = a última). Se duas morrem (ex.: questoes e respostas), só o botão da última aparece; quando ela volta,
  o aviso some e a outra fica morta em silêncio até fechar e reabrir a lista.
- **A2 (baixa, confiança média)** DoD 2 "reabrir a aba com a assinatura morta reinicia": vale para Listas e Teoria; para as leituras da
  lista aberta, reabrir a aba Listas não reassina (`iniciarQuestoes` só olha `QZ.subListas`); só o botão ou reabrir a lista.
- **A3 (baixa, confiança alta)** `core/templates/ui_harness.html` `?leitura=` sem teste que o use (código morto até alguém conferir no navegador).
- **A4 (info)** `qzChip` lê o `localStorage` por linha a cada snapshot -- custo desprezível com ~100 listas; limite declarado no comentário
  (lista começada em outro aparelho só mostra "em curso" pelo status).
- **A5 (info)** o aviso do quadro é dividido com o "não consegui salvar": `quadroRetentar` escreve "Carregando…" por cima de um erro de gravação visível.

### Critical Gate
Clean -- no destructive operations detected. (Arquivos: html/js/py/md; nenhum SQL, segredo, `eval`, CORS, debug, PII.)

### Hotfixes
16 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.

Ready to ship. (A1/A2 cabem numa hotfix pequena se a 1ª ocorrência real do log mostrar falha nas leituras da lista aberta.)
