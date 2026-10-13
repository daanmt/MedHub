## Audit Report: sprint-final-uerj part-1 (a retentativa pede conexão nova ao banco)

Auditado sobre `git show a223d81` (13/10/2026, s226). Testes rodados: `python -X utf8 -m pytest tools/test_hub_render.py tools/test_hub_quadro.py -q` -> **158 passed**. Suíte inteira NÃO rodada (outro subagente edita plano/painel em paralelo; brief limitou aos 2 arquivos).

**Verdict: PARTIAL**

### DoD Checklist
- [x] 1. Reconexão da 2ª tentativa em diante e no "Tentar de novo" — `hub.html:1716` (`assinar(true)` no timer), `:1742` (`reiniciar` -> `assinar(true)`), `:1728-1736` (`window.claude.use("db")` antes de `ligar(g, db)`); `consulta(db)` em `:1722`. Os 4 chamadores com `function(db){ return db.collection(` (notas `:1637`, quadro `:1960`, listas `:2042`, lista aberta `:2201`); `QZ.db.collection(col)` sumiu. Teste de forma conta 4.
- [x] 2. `QZ.db` acompanha — `aoReconectar: function(novo){ QZ.db = novo; }` em listas (`:2045`) e lista aberta (`:2203`); teste confirma `QZ.db === _dbBom` após a reconexão.
- [x] 3. `test_retentativa_pede_conexao_nova` (`tools/test_hub_render.py:1933`) — 1ª conexão morta, 2ª boa; Listas e Teoria carregam, `usos == 2`, `esperas == [1000]`, `ativos == {listas:1}` / `{quadro:1}`. Verde.
- [ ] 4. Harness `?leitura=conexao` existe (`ui_harness.html`: `dbMorto`, `conexaoCaiu`, `use` devolve o morto até a 1ª falha) — PASS na metade de código. A metade "ui_capturas.py com ele mostra as listas a 390 px sem erro de JS" é **insuficiente para verificar**: `ui_capturas.py` não tem opção para passar `leitura=` (os `params` do plano só levam lista/num/modo) e o commit não traz evidência de corrida. Não rodei (escreveria em `tmp/`).
- [~] 5. Sem cor literal nova (nenhum CSS no diff) — ok. "Sem edição de expectativa": o commit EDITOU 2 asserts existentes (`test_leituras_das_abas_passam_pela_assinatura_resiliente`, part-1 de hub-correcoes-pos-tema-v3; `test_cards_e_painel_mostram_o_mesmo_contador`) — troca mecânica `function(){` -> `function(db){`, forçada pelo DoD 1; desvio justificável mas literal. Suíte inteira não verificada aqui.

### Focos pedidos
- **2 ouvintes vivos**: não. `assinar()` chama `soltar()` (unsub + clearTimeout) e `++st.ger` ANTES do `use("db")` assíncrono; o `then` descarta se `g !== st.ger` (reiniciar/parar no meio); `falhou` de conexão velha é descartado pelo `g`; unsub tardio do `onSnapshot` é desfeito em `ligar`. Teste: `ativos == {listas:1}`.
- **`QZ.db` trocado durante gravação**: seguro. `QZ.db.doc(...).set()` (`:2422`) resolve a referência na hora; a promessa em curso segue na conexão velha; se falhar, `_pendente` fica e o reenvio (`:2427`) usa o `QZ.db` novo.
- **Painel ao vivo (notas do lote)**: as notas do lote da aba Cards (`iniciarCardsDia`, `:1637`) reconectam (`db: db`, sem `aoReconectar` — não guarda db, ok). MAS o `painelVivo` do Painel (`:1557-1590`: notas, listas, respostas) e `marcarListasEm` (`:1491`) / quadro do Painel (`:1673`) seguem com `onSnapshot` cru, sem retentativa nem reconexão.

### Pattern Compliance
- [x] Leitura resiliente (docs/UI.md §5) — linha atualizada com `consulta(db)` / `aoReconectar`; histórico e mapa de testes (§7) atualizados.
- [x] Comentário-âncora de sessão (s226) no código e no harness.

### Critical Gate
Clean — no destructive operations detected (HTML/JS/py/md; sem eval, sem segredo, sem delete em massa).

### Defeitos
1. MÉDIO (conf. alta) `core/templates/hub.html:1951` — a Teoria guarda `colecao = db.collection("quadro")` do db da 1ª conexão; após reconexão a LEITURA vai pela nova, mas o clique "feito" grava na conexão velha (o contexto da spec cita "o db da Teoria"; DoD 2 só nomeia `QZ.db`). Fix: `aoReconectar: function(novo){ colecao = novo.collection("quadro"); }` no `quadroLeitura`.
2. MÉDIO (conf. média) `core/templates/hub.html:1557-1590` — `painelVivo` (Painel ao vivo) não reconecta; a spec chama de "Painel ao vivo" o 4º chamador, que na prática é `iniciarCardsDia`. Rótulo errado na spec ou lacuna real — decidir.
3. BAIXO `tools/ui_capturas.py` — sem meio de passar `?leitura=`; DoD 4 não reproduzível por 1 comando.
4. BAIXO `hub.html:1639` — notas do lote sem `aoMorrer`: esgotadas as 3, morre calada (pré-existente).
5. INFO — 2 asserts de testes anteriores editados (DoD 5 literal).

### Gaps / Incremental Prompt Pack
- (S) `quadroLeitura`: passar `aoReconectar` que refaz `colecao`; teste: após reconexão, clique grava no `_dbBom`.
- (S) `ui_capturas.py --leitura conexao` repassando o parâmetro ao frame; rodar `--cenas listas --larguras 390` e anexar `resultado.json` (sem erro de JS).
- (M, decidir) levar `painelVivo` para `assinarResiliente` ou corrigir o rótulo da spec.
