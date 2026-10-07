---
type: session
layer: history
status: canonical
---

# Session 218 -- Teoria com resumos por disciplina + 22 listas no hub (o "69 questões" era defeito de tela)

**Data:** 2026-10-07 (manhã)
**Ferramenta:** Claude Code (Opus 5.5, principal) + 1 subagente Opus (Teoria). Operador presente.

## Pedido dele

*"ajustasse o bloco de teorias, considerando que a biblioteca deveria cobrir os resumos [...] de acordo com o cronograma [...] As revisões podem entrar na biblioteca [...] com a taxonomia correta, integrando os respectivos blocos de disciplinas [...] nas próximas semanas [...] temos apenas 69 questões [...] a única fonte de questões tem sido os simulados da uerj"*. Print: Teoria S4 9 tarefas · 33 questões; S5 5 · 0; S6 3 · 36; S7 1 · 0. Backlog: **P18** (Biblioteca/resumos) e **P19** (questões).

## Diagnóstico

- **O 69 era DEFEITO DE TELA:** o cabeçalho da semana da Teoria (`secoes_do_quadro`, `s["q"]`) somava só as tarefas que a Teoria mostra (aula ou com aula ligada): DMG 33 (S4) + Tópicos em Pediatria 36 (S6). O plano real pendente: S4 768 · S5 836 · S6 707 · S7 439 (`plano.py --listar --semana N --status pendente`).
- S4 já tinha 16 listas no hub (546 q) e S5 21 (624), nenhuma resolvida; ritmo real 14 d ~10 q/dia x 97 necessários. **Gargalo = execução, não oferta.**
- Buraco real 1: **22 listas com link fora do hub** (S4 t833 t376; S6/S7 as demais). Cinco eram recusadas inteiras pelo `emed_api.py` (tudo ou nada) por 1-2 questões: certo/errado (t805 Q3, t826 Q26/Q34) e alternativa só imagem (t833 Q34, t376 Q19, t110 Q34 -- `sanitized_body` vazio, `<img>` só no `body`, medido por nome de tag, sem ler texto).
- Buraco real 2: **27 tarefas sem nenhuma fonte de questão** -- aulas custom de MFC (875 881 878 876 879 5425 1796 880 1795 882), "teoria" do extensivo (530 768 590 367 811 310 777 483 740 467), 5424 imagem obstétrica, 1797 TB 360, 887/889 cadernos 20 q, 1798/1799 UERJ 2017-2020, 5426 leitura. EMED não tem lista pronta: precisa de caderno por filtro.

## Feito

- **Hotfix `tools/emed_api.py` (`FORA_DO_FORMATO`):** certo/errado (2 alternativas, gabarito único) e alternativa só com imagem saem DECLARADAS (`fora` no JSON), como a discursiva; achadas = gravadas + discursivas + fora. Texto vazio sem imagem segue recusa. 3 testes de regressão escritos ANTES do fix (32 verdes). `/banco-emed` atualizado.
- **22 listas puxadas** (contagens confirmadas por ele por AskUserQuestion): achadas 842, gravadas **796**; backup `ipub_backup_20261007_110019.db` -> `emed_banco.py --ingerir --apply --expect N` por lista (796 novas, 0 inválidas) -> `--exportar` -> `ArtifactData batch` no hub (17 lotes, 818 docs; 3.852/25.000). Conferido `as_level: interact`: questão invisível pelo link.
- **Questões no hub por semana (S4-S7):** S4 19 listas/676 · S5 22/724 · S6 17/640 · S7 6/319 = **2.359** (faltam 2.431 para 10.000).
- **Mapa resumo -> tarefas à mão:** `core/hub_resumos.json`, lote 1 = 31 resumos da S4. Os 31 lidos na íntegra pelo principal antes do publish: sem spoiler UERJ 2022-2026, sem segredo. Defeitos de forma anotados (não corrigidos): `Hipertensão Arterial Sistêmica (Parte 2) - Tratamento.md` inteiro SEM ACENTO (F113); fins sem acento em DMG (l.259-260), TB (l.283-285), APS (l.289-291); `Pré-Natal.md` l.148 frase duplicada; `[GIN] Rastreamento Colo.md` com fluxograma em bloco de código.
- **Chrome:** `switch_browser` selecionou primeiro o "PIETROLAPTOP" (colega, mesma conta) -> aba no EMED caiu no login, nada digitado; depois "Daniel Martins". O grupo de abas sumiu 3x (ele fechou 1). Endpoint de busca NÃO mapeado. Regra dele: **Chrome só na máquina danielm** (memória `feedback_chrome_so_maquina_danielm`).

## Chrome (danielm) -- Fase 1 do mapeamento do banco do EMED

Prompt inline entregue a ele (na conversa da s218); executor = Claude in Chrome na máquina danielm. Relatório (só leitura, nada salvo):
- Busca/contagem: `POST https://api.estrategia.com/bff/questions/search/batch` corpo `{"batch":[[itens]]}`; `POST .../search/count-all` corpo `{"filters":[[itens]]}`; item `{"add":true,"entity":<nome>,"entity_ids":[...],"origin"?,"filtro_includente"?}`. Entidades: `topic` (assunto, UUID; origin `questions`), `goal_id` (objetivo; catalogs), `year` (string), `answer_type` (`TRUE_OR_FALSE`, `MULTIPLE_CHOICE`), `already_answered`/`not_answered`, `include_with_text_solution`. Instituição: entity a confirmar; catálogo `GET /bff/questions/filters/classifications/63b07b3e-c200-4b3d-b9e6-742a096ae26e?q=UERJ` (o mesmo `CATALOGO_INSTITUICAO` do `emed_api.py`). Árvore: `GET /bff/questions/topics?q=` e `GET /bff/questions/filters/classifications/<uuid>`. Teste: Saúde do Idoso (geriatria) `8fb449e4-f54d-435c-9466-87bb05287bf9`, 2020-2026 = 455 q.
- Escrita (só lida no JS, nada executado): `POST /bff/questions/notebooks` e `POST /bff/questions/notebooks/questions`.
- Sem filtro de EXCLUSÃO de instituição (filtros são E). **Decisão (principal, s218):** cadernos com anos 2019-2026, objetivo Residência, só `MULTIPLE_CHOICE`; o MedHub DESCARTA UERJ 2022-2026 na importação (mudança a fazer no `emed_api.py`/`emed_banco.py` ANTES de importar, com teste) -- t1798/t1799 filtram só UERJ 2017-2018 / 2019-2020. Fase 2 (criação dos 26 cadernos) liberada por ele, em curso no Chrome ao fim da s218.

## Teoria (subagente Opus: 535.192 tokens, 163 chamadas, 58,6 min pelo `usage`)

Brief em scratch `brief_teoria.md` (+ 2 adendos: bloco de código cercado; Painel x Teoria). Relatório cru: scratch `teoria/relatorio_teoria.md`.
- Cabeçalho da semana = "N tarefas · M resumos" + linha "Questões da semana: Q, na aba Listas" (todas as pendentes da semana). **Teoria x Painel conferido no plano real: S4 768/768 · S5 836/836 · S6 707/707 · S7 439/439**; com atrasada, a corrente mostra "· com as atrasadas: Y" (= Painel). 2 testes prendem a igualdade.
- Biblioteca depois das semanas: grande área -> disciplina; resumos (A-Z), aulas, RDs; RD em cada disciplina declarada, "nova" no topo enquanto não lida. Seção "Revisões direcionadas" do topo ⚰️ morta; `bloco` das 20 RDs substituído por `disciplinas` + `resumos` em `core/hub_quadro.json`.
- Resumos: conversor md -> HTML em `tools/hub.py` (deterministico, escape total, bloco cercado em `<pre>`), 31 `resumos/*.html` no manifesto (63/247 entradas); "Citado em" no resumo, "Fontes" na RD, "Fonte:" vira link no leitor; aba Listas ganhou os resumos da tarefa. Grifo funciona no resumo (testado com seleção real).
- Conferido no Edge headless 390 px claro/escuro (shots em scratch `teoria/shots/`). Fora: marcar resumo como lido (sem estado no quadro; a assinatura grava `doc_resumo-*`).
- Suíte 1486 (era 1457 + 2 da s218 de manhã): `test_hub_resumos.py` novo; `AGENTE.md §7.4` com 4 contagens de referenciadores atualizadas (listas, hub, painel, plano -- a falha `test_repo_real_consistente` já existia antes).

## Fecho

- Publish do hub delegado a subagente (o principal não tinha contexto para ler `index.html` + 31 resumos HTML na íntegra; os 31 `.md`-fonte foram lidos pelo principal). Lote `2026-10-07a` republicado SEM gravar (ele drenou; gravação = abertura da s219).
- Custo: principal + Teoria (535 mil tokens) + publish (ver HANDOFF linha 3).
