# Spec: hub-correcoes-pos-tema-v3 -- part 3: Semana do Painel no padrão da Teoria

> PRD: `.vibeflow/prds/hub-correcoes-pos-tema-v3.md` (item 3; decisão dele em 13/10, padrão P21). Gerada em 13/10/2026 (s226).

## Objetivo

Cada linha da Semana do Painel tem um alvo só (a linha inteira abre a lista no hub), sem "resolver no hub" e
"da semana N" repetidos em toda linha.

## Contexto

`tools/painel.py`: `_acao` escreve "resolver no hub" e "abrir aula" por tarefa; `_html_tarefa` põe
`<span class="t-atraso">da semana N</span>` em cada atrasada; a Próxima tem botão cheio por CSS
(`[data-bloco="semana"] > .tarefas > .tarefa:first-child`). Os testes de `tools/test_painel.py` casam
`<li class="tarefa" data-tarefa="N">` por regex e o hub pinta a lista resolvida por `data-tarefa` (`painelListas`).

## Definition of Done

1. Tarefa `no_hub`: a linha é um único alvo (`<a>` ou `<button>` envolvendo tema + meta, com `data-hub-aba` e
   `data-hub-modo`); o texto "resolver no hub" aparece 0 vezes no HTML da semana -- teste
   `test_semana_linha_inteira_abre_a_lista` em `tools/test_painel.py`.
2. Aula ligada vira ação pequena e secundária só quando existe (título curto ou "aula"), fora do alvo principal.
3. Atrasadas sob o subtítulo **"Atrasadas · N"** (uma vez), e "da semana N" 0 vezes por linha -- teste
   `test_atrasadas_sob_subtitulo_unico`.
4. A Próxima se distingue só pelo rótulo "Próxima" (mesmo controle das outras linhas) -- teste trava a ausência do
   estilo de botão cheio.
5. `<li class="tarefa..." data-tarefa="N">` preservado: `painelListas` segue riscando a resolvida (teste existente
   do hub verde) e a suíte `test_painel*.py` inteira verde.
6. Artesania: sem cor literal nova; `python tools/ui_capturas.py` sem rolagem horizontal a 390/768/1280; tarefa sem
   ação no hub (lista externa, PDF) mantém o comportamento atual.

## Escopo

- `tools/painel.py` (`_acao`, `_html_tarefa`, `_html_semana` e o CSS do bloco semana), `tools/test_painel.py`,
  `core/templates/hub.html` só se o clique da linha precisar do mesmo handler de `data-hub-aba` (provável que não),
  `docs/UI.md` (histórico).

## Anti-escopo

- A rota (semanas futuras em `<details>`) além do que herdar de `_html_tarefa`; o que conta como atrasada; a ordem do
  plano; a Teoria (já no padrão).

## Decisões técnicas

- **Alvo = `<a href="#questoes" data-hub-aba=...>` envolvendo o conteúdo**: reaproveita o handler existente do hub
  (sem JS novo); trade-off: aula secundária precisa ficar FORA do `<a>` (link dentro de link é inválido).
- Subtítulo "Atrasadas · N" calculado em `_html_semana` sobre as tarefas que ela já recebe.

## Padrões aplicáveis

- P21 (padrão da Teoria) e `docs/UI.md` §5 (linhas com filete, estado nunca só por cor), §7.

## Riscos

- Regex dos testes e o `painelListas` dependem da forma do `<li>` -> manter o `<li>` como raiz e mudar só o interior.
