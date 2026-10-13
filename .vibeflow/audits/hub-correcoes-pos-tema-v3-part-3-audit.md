## Audit Report: hub-correcoes-pos-tema-v3 -- part 3 (Semana do Painel no padrão da Teoria)

> Auditado pelo DIFF do commit `20d6d38` (`git show 20d6d38`), não pela árvore. 13/10/2026 (s226).

**Verdict: PASS** (com 2 achados de baixa gravidade)

### Testes
- `python -X utf8 -m pytest tools/test_hub_render.py tools/test_hub_quadro.py tools/test_painel.py -q` -> **208 passed**;
  `tools/test_painel*.py` (painel + painel_divida) -> **57 passed**.

### DoD Checklist
- [x] **1. Linha = um alvo** -- `_html_tarefa`: `no_hub` envolve tema+meta em `<a class="t-alvo" href="#questoes" data-hub-aba="questoes" data-hub-modo=…>`
  (`_modo_hub`); "resolver no hub" removido de `_acao`. `test_semana_linha_inteira_abre_a_lista` (inclui "nada clicável dentro do alvo").
  O hub já liga `a[data-hub-aba]` no documento do painel (hub.html l.564) -- sem JS novo, como a decisão técnica previa.
- [x] **2. Aula secundária fora do alvo** -- `<p class="t-acao t-sec">…aula</a></p>` depois do `</a>`; só quando existe (li2 sem `t-acao`).
- [x] **3. "Atrasadas · N" uma vez** -- `_html_semana` agrupa (`h3.t-grupo.atrasadas`), `t-atraso` e "vêm atrasadas" removidos.
  `test_atrasadas_sob_subtitulo_unico` (contagem 1, ordem, corte `VISIVEIS_SEMANA` e `start`).
- [x] **4. Próxima só pelo rótulo** -- classe `.proxima` na 1ª tarefa; CSS de botão cheio (`:first-child .t-acao a:first-child`, `var(--sobre)`) removido.
  `test_proxima_so_pelo_rotulo_sem_botao_cheio`.
- [x] **5. `<li class="tarefa…" data-tarefa>` preservado** -- raiz intacta; `painelListas`/`LISTAS_VIVAS` usam `li.tarefa[data-tarefa]` e `.t-meta`
  (ainda presentes, agora dentro do `<a>`); testes do hub verdes.
- [x] **6. Artesania** -- sem cor literal nova (só tokens); `tmp/ui_capturas/s226p3/resultado.json` (10:34): painel a 390/768/1280 `rola: false`,
  sem erro de JS; tarefa fora do hub mantém `<p class="t-acao">abrir lista` (li3 do teste) e o PDF segue texto.

### Pattern Compliance
- [x] P21 / `docs/UI.md` §5: linha com filete, estado nunca só por cor (âmbar + a palavra "Atrasadas"); foco visível de 3 px em `.t-alvo`; 44 px.
- [x] §7/§11: travas e histórico registrados no `docs/UI.md`.
- [ ] §10 (achados): **A20 segue "pendente"** em `docs/UI.md:206` -- a part-3 escreveu o histórico mas não fechou o achado.

### Achados
- **B1 (baixa, confiança alta)** `docs/UI.md:206` -- A20 marcado "pendente"; deveria ser "resolvido (s226, part-3)".
- **B2 (baixa/estilo, confiança alta)** `tools/painel.py:384-385` -- `if no_hub: pass` antes do `elif`: ramo vazio; mais legível `if not no_hub and …`
  ou um comentário-guarda. Sem efeito de comportamento.
- **B3 (info)** `_html_semana` acrescenta "Desta semana · N" quando há atrasadas -- não pedido no DoD, coerente com o padrão; ok.

### Critical Gate
Clean -- no destructive operations detected.

### Hotfixes
16 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.

Ready to ship (B1 é uma linha de doc).
