---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 7
slug: plano-ssot-e-cards-v2-part-7
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/painel.py
  - .agents/workflows/registrar-sessao.md
---

# Spec -- Parte 7: painel gerado (`tools/painel.py --html` -> Artifact fixado)

> PRD `plano-ssot-e-cards-v2`, P3 (primeira metade). Depende das Partes 4 e 6.

## Objective
Uma página fixada, regenerada a cada fechamento de sessão a partir do banco, substitui as 20 tabelas do Dashboard do Drive como visão de progresso.

## Context
Sem esta parte, o usuário perde a visão consolidada quando o Drive for congelado (Parte 8). O dado já existe: `plano_tarefas` (Partes 2-4), `sessoes_bulk` + `listas.py` (Parte 6), FSRS (`day_plan._fsrs_counts`, `fsrs_load.py`), custo/questão (`performance.py`, que já lê a tabela de investimento/mês). O contrato de renderização de Artifact do projeto (`aula-base.md`, memória `feedback_artifact_width_alignment`) já existe e vale aqui.

## Definition of Done
1. `python tools/painel.py --html [--out artifacts/painel.html]` gera uma página autocontida (sem CDN além dos permitidos, sem dado embutido de terceiros) com 5 blocos: progresso por bloco UERJ (tarefas feitas/pendentes/cortadas e questões feitas x previstas), listas da semana corrente (com link), FSRS (vencidos, pool, teto do dia, retenção 7d), custo/questão e projeção até UERJ e ENAMED 2027 (`performance.volume_vs_marco`), próximas 7 tarefas do plano. Todo número traz a fonte (`[db]`, `[plano]`, `[performance]`) no rodapé do bloco.
2. `--json` emite o mesmo dado estruturado (é o contrato testável); `tools/test_painel.py` testa o JSON com db sintético (blocos, somas, projeção) e a presença dos 5 blocos no HTML por marcadores `data-bloco="..."`.
3. Página conforme o contrato de renderização: `.wrap` único, tokens `:root` + dark via `prefers-color-scheme` guardado e `[data-theme]`, `body` com background explícito, funciona em 400px sem scroll horizontal; `grep -c "max-width" artifacts/painel.html` <= 2 (regra da memória s151).
4. `.agents/workflows/registrar-sessao.md` ganha o passo "gerar painel + publicar/atualizar o Artifact `Painel MedHub` (mesma URL, `url` no publish) + fixar uma vez"; `HANDOFF.md` carrega a URL fixa do painel na linha de Datas/Links.
5. `auto_check --changed` PASSED; flags em `/engenharia-cli` (D5); registro em `pytest.ini`.
6. Craftsmanship: read-only absoluto (nenhum write no db; `tools/painel.py` fora da allowlist), zero LaTeX/setas Unicode, nomes de arquivo e título estáveis entre redeploys (`<title>Painel MedHub</title>`).

## Scope
`tools/painel.py`, `tools/test_painel.py`, `pytest.ini`, `.claude/commands/engenharia-cli.md` (+ espelho), `.agents/workflows/registrar-sessao.md`, `artifacts/painel.html` (gerado; versionado como cópia, como os outros artifacts).

## Anti-scope
Sem exportar Google Sheet (cortado no discover). Sem gráficos com biblioteca externa no v0 (barras em CSS bastam; `dataviz` skill entra se um gráfico de série for pedido). Sem congelar o Drive aqui (Parte 8). Sem editar `performance.py` além de expor uma função já existente, se faltar.

## Technical Decisions
- **`--json` como contrato, HTML como render**: o teste prova o dado; o HTML é olhado uma vez antes de publicar (regra do skill de Artifact: escrever, olhar uma vez, publicar).
- **Publicação é ato do agente no fechamento, não do CLI**: o CLI não fala com a API de Artifact; o workflow diz "gerar e publicar com `url`", mantendo a URL fixa (o usuário fixa a página uma vez).
- **Sem estado no painel** (nenhuma capability): é leitura; interação fica para o player.

## Applicable Patterns
- `db-access-layer.md` (leitores em `db.py` ou nos CLIs já read-only), `agent-workflow-protocol.md` (passo no workflow de fechamento).

## Risks
- Página inflar com histórico -> v0 mostra só semana corrente + totais; histórico por semana fica no `--json`.
- Números divergentes entre painel e HANDOFF -> ambos derivam de `day_plan --handoff-block`/`performance`; o painel cita a função-fonte por bloco.

## Dependencies
- .vibeflow/specs/plano-ssot-e-cards-v2-part-4.md
- .vibeflow/specs/plano-ssot-e-cards-v2-part-6.md
