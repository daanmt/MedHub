# Spec: sprint-final-uerj -- part 4: Teoria e Listas consultivas

> PRD: `.vibeflow/prds/sprint-final-uerj.md` (Solution 4 e 5). Gerada em 13/10/2026 (s226).

## Objetivo

A Teoria é Biblioteca + o backlog de Revisões Direcionadas; as Listas mostram as listas na ordem do plano diário do
Painel -- nenhuma das duas tem cronograma próprio.

## Definition of Done

1. Teoria (`tools/hub.py`): saem as seções por semana (`html_semanas` / `qd-sem` atrasadas e semanas) e as contagens
   "Questões atrasadas / da semana ... na aba Listas"; entra no topo **"Revisões direcionadas · N"** (RDs não assinadas,
   da mais antiga para a mais nova, cada uma abre no leitor; assinada some do backlog e fica na Biblioteca). Biblioteca
   intocada. Teste em `tools/test_hub_quadro.py` (sem "Atrasadas"/"Semana" na Teoria; RD não assinada no backlog).
2. Listas (`core/templates/hub.html` `qzRenderListas`): agrupam por **"Hoje"**, **"Próximos dias"** (por data) e
   **"Fora do sprint"**, a partir do `<script id="hub-sprint">` que o build injeta de `plano.agenda_sprint` (a MESMA da
   part-3); resolvidas recolhidas no fim como hoje. Sem `hub-sprint`, cai no agrupamento antigo.
3. Simulados seguem na sua sub-aba, com a data do sprint ao lado ("dom 25/10").
4. Teste `test_listas_e_painel_mesmo_hoje`: do mesmo banco sintético, as tarefas de "Hoje" das Listas = as do Painel.
5. Artesania: sem cor literal; `ui_capturas.py` (cenas teoria, listas) sem rolagem horizontal; suíte verde.

## Escopo

`tools/hub.py`, `core/templates/hub.html`, `tools/test_hub_quadro.py`, `tools/test_hub_render.py`, `docs/UI.md`.

## Anti-escopo

Painel e boot; o leitor das aulas; a assinatura de leitura (já existe; a part só lê o estado).

## Dependencies

- .vibeflow/specs/sprint-final-uerj-part-3.md
