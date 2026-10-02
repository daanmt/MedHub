## Audit Report: feedback-cadeia-declarada part-4 (marca-texto no enunciado e nas alternativas)

> Auditado em 2026-10-02 (s211), subagente de implementação. Spec: `.vibeflow/specs/feedback-cadeia-declarada-part-4.md`.
> Dependência: part-3 PASS (commit `4d4fa8a`).

**Verdict: PASS** (com o limite declarado que o próprio DoD 6 exige)

### DoD Checklist

- [x] **1. Selecionar destaca.** `qzGrifoCapturar()` converte a seleção (Range -> offsets sobre o `textContent` de `#qz-enun` ou
  `.qz-alt-txt`), mescla, regrava e limpa a seleção nativa (`removeAllRanges`); mouse: `pointerup` (`pointerType === "mouse"`);
  toque: `pointerup` + `selectionchange` com espera (400/700 ms) e sem dedo apertado. Arrasto < 2 caracteres não grifa.
  Funções puras: `qzGrifoMesclar` (sobrepostos e adjacentes fundem) e `qzGrifoHtml` (escapa; descarta intervalo fora do texto,
  vazio, negativo, não inteiro ou não-número). Testes: `test_grifo_mescla_sobrepostos_e_adjacentes`,
  `test_grifo_html_escapa_e_ignora_intervalo_invalido`.
- [x] **2. Tocar remove.** Clique num `mark.qz-grifo` (enunciado ou alternativa) chama `qzGrifoTocar` -> `qzGrifoRemover(intervalos,
  pos)` e retorna ANTES de marcar a letra / abrir o porquê. Teste: `test_grifo_remover_intervalo`.
- [x] **3. Alternativa continua clicável.** O corpo virou `<div class="qz-alt-btn" role="radio" tabindex="0" aria-checked>` dentro de
  `role="radiogroup"`; clique sem seleção marca (o handler aceita `.qz-alt-btn`); soltar COM seleção só grifa (`qzAcabouDeGrifar`,
  500 ms, suprime o clique que segue o `pointerup`); `Enter`/`Espaço` na alternativa a acionam; `A`-`E` e `1`-`5` seguem; o X segue
  `<button>`; revelada, `role="button"` + `aria-expanded` (com porquê) ou `aria-disabled`. Teste:
  `test_alternativa_tem_role_radio_e_nao_e_button` (golden `alternativa.html` + âncoras do teclado no template).
- [x] **4. Persistência.** `QZ.grifos[num] = {enun: [[ini, fim]], A: [...]}`; rascunho em `localStorage` (`medhub.grifos.<lista>`)
  antes de responder; `qzResponder` leva `grifos` ao doc; cada mudança depois regrava pelo `qzGravar`; reabrir (antes ou depois de
  revelar) redesenha (`qzGrifosDe`: o doc da resposta vence o rascunho). Teste:
  `test_grifos_viajam_no_doc_da_resposta_e_voltam_na_revisao` (rascunho sem gravar -> doc ao responder -> regrava na mudança ->
  outra sessão só com o db redesenha enunciado e alternativa).
- [x] **5. Harness e forma.** `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> **1336 passed**; `hub.py --build ...
  --out <scratchpad>` -> `--check: OK`; `node --check` do JS montado -> OK; `auto_check --changed` exit 0. Uma cor só
  (`.qz-grifo{background:var(--qz-duv-fraco);color:var(--tinta)}`), sem barra, menu ou seletor
  (`test_grifo_uma_cor_de_token_e_limite_declarado`).
- [x] **6. Limite declarado.** Comentário do bloco no template ("LIMITE DECLARADO: o comportamento da selecao por TOQUE no navegador
  do celular ... NAO e verificado por teste") e brief §Estado por elo, item `grifos` ("Não verificado por teste: a seleção por toque
  no navegador do celular"). Preso pelo mesmo teste do item 5.

### Pattern Compliance

- [x] Funções puras extraídas e testadas em node; golden por cenário.
- [x] Espelho local antes do db (rascunho de grifos), o db vence ao reabrir.

### Desvios

- Arquivos além dos 2 da spec: `docs/SOLUCAO-MEDHUB-BRIEF.md` (o próprio DoD 6 pede a linha no brief) e `tools/test_emed_banco.py`
  (`grifos` entrou no conjunto exato `_SEM_DESTINO_ATE_A_PART_5` do teste de propriedade F133; a coluna é da part-5).
- O stub `qzGravar` do harness passou a pôr a resposta em `QZ.resp`, como o real (o teste de persistência dependia disso).

### Decisões onde a spec deixava aberto

- Espera do toque: 400 ms depois do `pointerup` e 700 ms de `selectionchange` sem ponteiro apertado.
- Grifo continua editável depois de revelar (tocar remove, selecionar acrescenta) e regrava a resposta.
- `grifos` só vai no doc quando há ao menos um intervalo (resposta sem grifo não ganha `grifos: {}`).

### Critical Gate

Clean -- nada destrutivo; o texto grifado passa por `qzEsc` em cada fatia; `data-i` é inteiro validado.

### Não verificado

- **Seleção por toque no celular dentro do artifact** (o risco aberto do PRD): só o operador valida, numa lista real.
- Seleção por mouse num navegador real (conversão Range -> offsets, supressão do clique): sem DOM headless no ambiente (sem jsdom);
  só as funções puras e o fluxo de persistência foram exercitados.

14 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
