# PRD: Plano estável como SSOT, ledger de listas, Autópsia diária e cards rápidos (v2)

> Escrito em 2026-09-16 (s183) a partir do pedido textual do usuário; substitui o fluxo "usuário preenche o Drive -> agente importa".
> Permit: *"Preciso de um planejamento mais estável, orquestrado por você, que tem mais contexto sobre mim do que as planilhas."*

## Problem

1. **O plano não tem SSOT.** O detalhamento vive no `Cronograma.pdf` (30 sem), a ordem no xlsx do Drive, a conclusão no `Dashboard EMED 2026` -- que cataloga as **707 tarefas do EXTENSIVO**, não as 352 da Reta Final (s183). O usuário fazia tarefas que não existiam no Dashboard e marcava outras no lugar: a coluna `Realizada?` é aproximada. O `grade.json` nunca casou 1:1 com a conclusão real (família F72).
2. **As listas de exercícios não têm ledger.** `links_exercicios.json` guarda URL + nº de questões só para S15-S30 da Reta Final; `sessoes_bulk` (126 sessões) não referencia tarefa nem link (0 linhas com `http`). Não dá para responder "qual lista fiz, quantas, quantos acertos" sem ler prosa em `observacoes`.
3. **O banco de cards acumula defeito declarado.** 1.668 cards: 1.476 ativos, **192 aposentados** (`needs_qualitative=2`), 810 nunca introduzidos; 278 WARN de atomicidade, 11 de auto-suficiência, 283 marcas de reforja. Não existe CLI de exclusão -- só reescrita in-place (`recurate_cards.py`).
4. **Fazer cards é lento.** O `/revisar` conversacional (card a card no chat, nota digitada) custa tempo e contexto; o usuário pede UI mais amigável e mais rápida.
5. **A análise de questão do dia é mais rasa que a do ENAMED.** A s182 entregou cadeia + comporta + armadilha + fonte verificada + veredito por questão numa página; o bloco diário não.

## Target audience

Usuário único (médico, foco nº1 Psiquiatria/IPUB via ENAMED 2027, alvo 95%; plano B UERJ/MFC 01/11/2026), regime 60q + 60 cards/dia, operando por chat (desktop/celular) e Artifacts.

## Proposed solution -- 6 partes, nesta ordem de dependência

### P1 -- Plano como SSOT no `ipub.db` (`plano_tarefas`)
- Tabela `plano_tarefas`: `id, fonte ('extensivo'|'rf'|'custom'), ref_semana_fonte, tarefa_fonte, semana_plano, ordem, area, tema, tipo, url_lista, q_previstas, status ('pendente'|'feita'|'cortada'), data_conclusao, sessao_bulk_id, origem_conclusao, nota`.
- Derivador `tools/cronograma.py --rebuild-extensivo` -> `core/cronograma/grade_extensivo.json` (parser prototipado na s183: 52 semanas, 735 tarefas, páginas do Livro Digital, links de lista quando houver).
- Semeadura: RF S17-S28 pendente (139 tarefas) + extensivo S21-S48 (425) + tarefas `custom` (7 resumos MFC-UERJ, 8 temas sem resumo, termômetros INEP). `status` inicial = `Realizada?` do Dashboard de 10/09 com `origem_conclusao='dashboard_2026-09-10'` (sinal aproximado, **revisado por área com o usuário** numa passada única -- ele corrige, o agente grava).
- `semana_plano`/`ordem` são do AGENTE (Fase 1 por peso UERJ; Fase 2 extensivo reordenado), editáveis por CLI (`tools/plano.py --mover ID --semana N`, `--cortar`, `--concluir ID --sessao N`). Reordenar deixa de ser ritual no xlsx.
- `day_plan.py` passa a ler `plano_tarefas` (não mais calendário do PDF); W8 do reconcile morre; W5 vira "grade_extensivo em dia vs PDF".
- 🔴 Fronteira: `taxonomia_cronograma`, FSRS e `review_log` intocados.

### P2 -- Ledger de listas de exercícios
- `sessoes_bulk.tarefa_id` (FK nullable) + `registrar_sessao_bulk.py --tarefa ID`; o writer valida que `area` bate com a tarefa.
- Backfill único das 104 sessões com `observacoes` por casamento de nome de tema (dry-run + COUNT-ASSERT; sem match fica NULL, nunca chute).
- `tools/listas.py` (read-only): por tarefa `url | q previstas | feitas | acertos | %`, por bloco UERJ, por semana; `--pendentes`, `--progresso`. Substitui as 20 tabelas do Dashboard.

### P3 -- Painel gerado (o Drive deixa de ser SSOT)
- `tools/painel.py --html` gera `artifacts/painel.html` (progresso por bloco, listas feitas, FSRS, custo/Q, próximas 7 tarefas) -> publicado como Artifact fixado; regenerado no fechamento de sessão.
- Opcional: `--sheet` exporta o mesmo dado como Google Sheet gerado via MCP (`create_file`), **nunca editado à mão**. A tabela de investimento/mês continua manual no Drive (é input, não derivado) e é lida pelo `/performance`.
- O `Cronograma de Reta Final.xlsx` e o `Dashboard EMED 2026` viram histórico: `--sync-drive` e `importar-planilha` ganham lápide; `--abandonada` no snapshot W1.

### P4 -- Player de cards como Artifact (rápido e UI-friendly)
- Página `Cards do dia`: fila do `fsrs_queue.py` embutida no publish (frente/verso/regra-mestre/armadilha), teclado `1-4` e toque, relearning intra-sessão na própria página (nota < 4 volta ao fim do lote), botões `defeito` (-> fila de reforja com motivo) e `aposentar`; contador e tally.
- Estado gravado pela capability de dados do Artifact (`artifact-capabilities`: carregar o skill antes de escrever a página); no fechamento o agente lê o estado e grava em lote via `fsrs_queue.py --record` (**o caminho único de escrita do FSRS não muda**; Invariante A/C preservados; só a 1ª nota de cada card grava).
- Revisão Direcionada de fechamento continua no chat (v1.3 do contrato). O `/revisar` conversacional fica como fallback (celular sem página).

### P5 -- Curadoria e poda do banco
- `tools/cards_prune.py --dry-run|--apply --criterio aposentados|--ids ...`: exige `backup_db.py` no mesmo comando, exporta as linhas (flashcards + fsrs_cards + fsrs_revlog + reforja_marks) para `artifacts/backups/pruned_<data>.json` antes de apagar, COUNT-ASSERT declarado. Nada é perdido; só sai do banco vivo.
- Lote 1 (decisão do usuário, lista gerada na s183): os 192 aposentados -- **poda os sem revlog e sem marca de reforja**; os com histórico ficam até triagem.
- Regra permanente de intake: **card nunca introduzido só entra na fila depois de passar pelo teste de regenerabilidade feito pelo agente** (60/dia inclui a triagem); WARN de atomicidade/auto-suficiência é resolvido **no toque** (quando o card sobe na fila), nunca em lote cego.
- Erros: `banca-divergente`/`anulada` ficam (são dado); erros sem card (21) ganham card ou lápide na próxima Autópsia do tema.

### P6 -- Autópsia diária na profundidade do ENAMED
- Cláusula nova em `analisar-questao.md`: todo bloco de questões gera **uma página Autópsia** (Artifact + cópia em `artifacts/autopsia-AAAA-MM-DD.html`) com, por questão errada ou chutada: enunciado, cadeia de habilidades e o elo que quebrou, comporta/discriminador, armadilha, fonte verificada (WebSearch/PubMed, com URL), veredito (CONCORDA/CONTESTÁVEL), racional declarado do usuário e os cards cunhados (com o teste de regenerabilidade explícito). Template = estrutura de `artifacts/enamed-2026-comentado.html`.
- Régua F93 inalterada: <= 8 erros o principal faz; acima, um subagente por bloco, `model` explícito, retorno <= 3k + arquivo.

## Success criteria

1. `python tools/day_plan.py` lidera com a próxima tarefa vinda de `plano_tarefas` (fonte, link, q previstas) e o boot não emite mais `Drive desatualizado`.
2. `python tools/listas.py --progresso` responde, por bloco UERJ, listas feitas x previstas com acertos -- sem ler o Drive.
3. `python tools/cards_prune.py --dry-run --criterio aposentados` imprime N; `--apply` remove exatamente N, com backup + export verificáveis; `check_fk_orphans.py` limpo depois.
4. Uma sessão de 60 cards fecha na página em menos tempo que no chat (medir: minutos por 60 cards, hoje ~6 blocos conversacionais) e grava 60 revisões via `--record`.
5. Toda sessão de questões desde 17/09 tem `artifacts/autopsia-<data>.html`.
6. Painel publicado e fixado; Dashboard do Drive com lápide.

## Scope v0 (ordem de execução)

P6 (protocolo + template, 17/09) -> P5 lote 1 (poda dos aposentados, após aprovação da lista) -> P1 (grade_extensivo + plano_tarefas + revisão por área) -> P2 (ledger + backfill) -> P3 (painel) -> P4 (player). Uma spec por parte; audit por `/vibeflow:audit`; GO do `/ai-eng` por silêncio (AGENTE §10.6).

## Anti-scope

- Editar à mão o Dashboard/xlsx do Drive; scraping de listas do Estratégia; import em massa dos Medcards; migrar o FSRS para Anki; reintroduzir Streamlit; mudar `stability`/`difficulty` de qualquer card.

## Open questions (para o usuário)

1. Drive deixa de ser SSOT (P3) -- confirma? Alternativa: o agente gera um Sheet novo por semana e o antigo fica congelado.
2. Poda lote 1: aprovar a lista dos aposentados sem histórico (número no dry-run da s183).
3. Player (P4): desktop-first com teclado, ou celular-first com toque? Define o layout.
