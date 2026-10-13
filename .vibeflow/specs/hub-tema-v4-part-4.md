# Spec: hub-tema-v4 -- part 4: questão e leitor no idioma das placas

> PRD: `.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (fatia 4). Gerada em 13/10/2026 (s227).
> 🔴 **Guarda do simulado:** esta part só vai ao ar se conferida até **qui 15/10 à noite**; senão, só **dom 18/10**, depois
> do simulado UERJ 2024 de sáb 17/10. Ele resolve o simulado nesta tela.

## Objetivo

A tela da questão e o leitor de aulas/resumos ganham as placas, sem mudar um único gesto da resolução.

## Contexto

A questão aberta (`qz-*` no `hub.html`) é hoje: barra (voltar, modo, relógio), trilho, enunciado solto no fundo,
alternativas com moldura, veredito, cadeia com a declaração dos elos, tela de fim. O leitor mostra cada aula (43, CSS
próprio + `tema-aula.css`) num iframe solto no fundo, com a assinatura de leitura embaixo; as RDs da UERJ 2022 têm a
`figure.fig-an` da anima.

## Definition of Done

1. Antes de escrever, carregar `frontend-design` (ferramenta Skill).
2. **Questão:** o enunciado (meta, texto, figuras) é uma placa; as alternativas seguem como objetos de toque dentro da
   coluna (moldura própria sobre o fundo ou elevadas, nunca caixa dentro de caixa); veredito + cadeia formam uma placa;
   a tela de fim usa placas para métricas, por bloco, Elos e revisão. Coluna da questão = `--wrap` (um `max-width` só,
   filhos 100%: o trilho e a barra do topo seguem com a mesma largura do corpo, regra s212).
3. **Interação idêntica:** mesmos botões, mesma ordem, mesmos atalhos, mesmos estados (`✓ ✗ ?`), mesma gravação; os
   testes de forma e de fluxo de hoje verdes (`test_forma_da_tela_revelada`, `test_hub_render.py` inteiro), 44 px nos
   botões, `.qz-cadeia li` com `min-width:0`.
4. **Leitor:** a aula/resumo aparece numa placa (o iframe dentro dela, documento com fundo transparente da part 1); a
   assinatura de leitura é uma placa abaixo; `tema-aula.css` alinha os callouts e a `figure.fig-an` ao idioma (lavagem
   + filete por significado, moldura da figura = `--card` + `--borda-placa`), sem reescrever nenhuma aula; a coluna de
   leitura segue 46rem (`.wrap` da aula). L1 (tabela larga rola na caixa) segue resolvido.
5. Artesania: `ui_capturas.py` nas cenas questao, revelada, fim, aula, resumo a 390/768/1280 "ok", zero erro de JS, lido
   a 390 nos dois temas (escuro padrão e `data-theme="light"`), inclusive uma RD com figura; suíte inteira verde;
   `auto_check --changed` PASSED; cor só por token.
6. `docs/UI.md` §5 (questão, leitor), §6, §9 (leitor v4 e o estado de L4/L6), §11; a guarda do simulado registrada no
   commit e no HANDOFF (publicado em DD/MM ou retido até 18/10).

## Escopo

`core/templates/hub.html` (CSS e o mínimo de markup da questão, do fim e do leitor), `core/templates/tema-aula.css`,
`tools/test_hub_render.py`, `docs/UI.md`; `core/templates/ui_harness.html` só se uma cena precisar de roteiro novo.

## Anti-escopo

Qualquer mudança de fluxo, texto, ordem ou gravação da questão; atalhos; o HTML das 43 aulas; L2/L6/L9-L15 além do que a
camada resolver; `CSS_RESUMO` (A16); figuras novas; glow.

## Decisões técnicas

- Placa envolve contêineres que já existem (`#qz-questao`, o bloco revelado, `#qz-fim`, `#hub-leitor-quadro`,
  `#hub-assina`): classe a mais, sem elemento novo onde der.
- No leitor, a placa vai no wrapper do iframe; o documento da aula fica transparente; o `--card` da aula (apelido)
  continua sendo a superfície das caixas internas dela, que agora ficam sobre a placa -- conferir que caixa interna e
  placa não têm a mesma cor (usar `--afundado` para as caixas internas na camada, se coincidir).

## Padrões aplicáveis

`docs/UI.md` §5, §6 (largura), §9 (leitor), memória `feedback_artifact_width_alignment`, a primitiva `.placa`.

## Riscos

- Mudança visual na véspera do simulado gera atrito -> guarda acima; interação congelada pelo item 3.
- Caixas das aulas antigas (`.rail`, `.spec`, `.trilho-box`) dentro da placa podem virar caixa dentro de caixa -> a
  camada tira a moldura das que duplicam a placa; conferir as 6 famílias do inventário
  (`docs/research/2026-10-13-05-ui-auditoria-aulas.md`).

## Dependencies

- `.vibeflow/specs/hub-tema-v4-part-1.md`
- `.vibeflow/specs/hub-tema-v4-part-3.md`
