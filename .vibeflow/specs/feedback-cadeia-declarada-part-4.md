# Spec: Feedback por elo declarado -- part 4: marca-texto no enunciado e nas alternativas

> Escrita em 2026-10-02 (s211). PRD: `.vibeflow/prds/feedback-cadeia-declarada.md` (Scope v0, item 3).

## Objetivo

Selecionar um trecho do enunciado ou de uma alternativa o destaca automaticamente; tocar no destaque remove; os grifos gravam junto com a resposta e reaparecem na revisão.

## Contexto

Hoje o enunciado entra por `textContent` (`#qz-enun`) e cada alternativa é um `<button class="qz-alt-btn">` -- texto dentro de botão não é selecionável de forma confiável, e o clique no botão marca a letra. O operador quer grifar discriminadores, comportas, cutoffs e gatilhos decisórios (referência: print 1 do Prisma, enunciado com trechos em destaque e alternativas riscadas). O padrão-mestre de erro dele é "discriminador identificado e não usado": o grifo é o registro do que ele VIU.

**Fricção que esta spec remove:** nenhuma viciosa relevante; ela ACRESCENTA um gesto virtuoso (marcar o dado que decide) e o registra.

## Definition of Done

1. **Selecionar destaca.** Uma seleção não vazia dentro de `#qz-enun` ou do texto de uma alternativa vira destaque (`<mark class="qz-grifo">`) ao soltar (mouse) ou ao estabilizar (toque), e a seleção nativa é limpa. Intervalos sobrepostos ou adjacentes se fundem. Funções puras testadas em node: `qzGrifoMesclar(intervalos, novo)` e `qzGrifoHtml(texto, intervalos)` (escapa HTML; intervalos fora do texto são descartados). Testes: `test_grifo_mescla_sobrepostos_e_adjacentes`, `test_grifo_html_escapa_e_ignora_intervalo_invalido`.
2. **Tocar remove.** Toque/clique num destaque remove aquele intervalo, sem marcar a alternativa. Teste: `test_grifo_remover_intervalo` (função pura `qzGrifoRemover(intervalos, pos)`).
3. **Alternativa continua clicável.** O corpo da alternativa deixa de ser `<button>` e vira elemento selecionável com `role="radio"`, `tabindex` e `Enter`/`Espaço`; clique SEM seleção marca a letra como hoje; soltar COM seleção só grifa. As teclas `A`-`E` e `1`-`5` seguem funcionando. O X de riscar segue botão. Teste: `test_alternativa_tem_role_radio_e_nao_e_button` (golden do HTML da alternativa).
4. **Persistência.** Os grifos vivem em `QZ.grifos[num]` = `{enun: [[ini, fim], ...], A: [...], ...}` (offsets de caractere sobre o texto puro), com rascunho em `localStorage` por lista antes de responder, e entram no doc da resposta como `grifos` ao responder (e a cada mudança depois). Reabrir a questão (antes ou depois de revelar) redesenha os grifos. Teste: `test_grifos_viajam_no_doc_da_resposta_e_voltam_na_revisao`.
5. **Harness e forma.** `pytest tools/ -q` verde; `hub.py --build` com `--check` OK. Uma cor só, derivada dos tokens existentes (`--qz-duv-fraco` com texto `--tinta`), legível nos dois temas. Nenhuma barra flutuante, menu ou seletor de cor.
6. **Limite declarado.** O comentário do bloco no template e o brief dizem em 1 linha o que NÃO foi verificado por teste: o comportamento da seleção por toque no navegador do celular (só o operador valida no aparelho). Sem isso a spec não fecha.

## Scope

- Render do enunciado e das alternativas por `qzGrifoHtml` (mantendo `white-space: pre-wrap`).
- Captura: `pointerup`/`mouseup` no desktop; no toque, `selectionchange` com espera curta (a seleção nativa por toque longo só estabiliza depois que o dedo sai) -- converter Range -> offsets relativos ao `textContent` do contêiner.
- Gravação pelo `qzGravar` existente (resposta já dada) ou rascunho local (ainda não respondida).

**Arquivos (2):** `core/templates/hub.html` · `tools/test_hub_render.py` (+ goldens).

## Anti-scope

- Tipos ou cores de grifo (discriminador, comporta, cutoff). Anotação em texto. Grifo na solução ou no comentário.
- Plano B por toque em frase: só se o operador reportar que a seleção não funciona no aparelho dele (vira hotfix com evidência).
- Ingestão dos grifos no `ipub.db` (part-5).

## Technical Decisions

- **Offsets de caractere sobre o texto puro** (não nós do DOM): sobrevivem a re-render e viajam em JSON pequeno. Trade-off: se o texto da questão for recapturado e mudar, os offsets deslocam -- aceitável (grifo é dado da tentativa, e o intervalo inválido é descartado).
- **Alternativa `role="radio"` em vez de `<button>`:** é o único jeito de ter texto selecionável; custo = reimplementar foco e teclado, coberto no DoD 3.
- **Limpar a seleção nativa depois de grifar:** evita o menu de copiar/compartilhar do celular ficar aberto sobre a questão.

## Applicable Patterns

- Funções puras extraídas e testadas em node (padrão de `tools/test_hub_render.py`).
- Espelho local antes do db (padrão do player).

## Risks

- **Seleção por toque dentro da página publicada** pode ser capturada pelo contêiner do artifact ou disputar com o scroll: é o risco aberto do PRD. Mitigação: evento duplo (`pointerup` + `selectionchange`) e o limite declarado no DoD 6; validação real = o operador, numa lista.
- **Clique que vira grifo acidental** (arrasto curto): só grifar seleção com 2+ caracteres.
- **Regressão do atalho de teclado** das alternativas: coberto por teste.

## Dependencies

- `.vibeflow/specs/feedback-cadeia-declarada-part-3.md`
