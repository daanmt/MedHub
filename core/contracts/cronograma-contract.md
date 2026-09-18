---
type: contract
layer: core
status: canonical
version: 1.3
relates_to: [reconcile-contract, forgetting-curve-contract, estado-contract, AGENTE]
---

# Contrato do Cronograma (Sync Cronograma ↔ Performance ↔ FSRS)
**Versão 1.3 | 2026-06-27 (sessão 095), primeira instância; v1.1-1.3 nas sessões seguintes.**
**Origem: Materializa o ultraplan `docs/plans/s094-ultraplan.md §c/§d`.**

> Documento normativo. Governa a **camada derivada do cronograma de Reta Final** (EMED) e seu sync com os SSOTs de estado. O cronograma é um **plano**, não verdade-de-estado: divergência plano↔realidade é *informação de gestão*, nunca corrupção. Referenciado por: `AGENTE.md` (§2 passo 4, §6, §7.3/§7.4), `reconcile-contract.md` (W5-W7), `forgetting-curve-contract.md` (Boot).

---

## Papel

O estudante segue um cronograma de 30 semanas (EMED), mas **por conteúdo**, atrás do calendário nominal (s095: conteúdo na S11 × calendário na S13). O sistema precisava (a) de uma fonte estruturada do plano que não dependa de prosa, (b) cruzar o plano com a performance real (`sessoes_bulk`) e a curva (FSRS) **sem escrever no db**, e (c) alimentar o boot com semana/temas/ritmos. Este contrato normatiza a derivação, o sync read-on-demand e as fronteiras duras.

---

## Cláusula 1 — Fonte e SSOT

- **SSOT = `Cronograma.pdf`** (raiz). É IP do EMED → **gitignored** (`*.pdf`), nunca commitar.
- O **`Cronograma de Reta Final.xlsx`** do Drive é fonte futura (editável pelo usuário); reconciliar PDF×xlsx é **fora de escopo v1.0** (evita dependência de MCP no boot).
- A grade NÃO persiste no `ipub.db` (herda a decisão s075). Zero INSERT/UPDATE no db originado do plano.

## Cláusula 2 — Derivação e camada versionada

- **`core/cronograma/grade.json`** é a camada derivada **versionável** (commitada): é estrutural (semana/área/tipo/contagem/datas), **sem texto clínico do EMED** → seguro commitar; o `git diff` quando o PDF muda É o valor de auditoria.
- Schema: `_meta` (`fonte`, `fonte_sha256`, `fonte_mtime`, `extraido_em`, `semana_1_inicio`, `n_semanas`, `n_tasks`, `total_questoes`, `areas_canon`) + `semanas[]` (`semana`, `inicio`, `fim`, `total_questoes`, `n_tasks`, `tasks[]`). Cada task: `area_pdf` (verbatim, auditoria), **`area_norm`** (canônico — a chave de JOIN), `multi_area`, `tema`, `tipo` (verbatim) + `tipo_norm` ∈ `{teoria, revisao, revisao_questoes, outro}`.
- **Datas por âncora + ordinal** (`semana_1_inicio` + (n−1)·7), NUNCA do ano da string do PDF (tem typo). Âncora v1.0 = `2026-03-30`, derivada do fato documentado "26/06 calendário na S13" (ESTADO); ajustável regravando a grade.
- **Contagem por SEMANA é confiável** (soma de `Link - NN questões`; validado S10=273, S11-28=6689). **Não se atribui contagem por task** (o PDF não amarra `link[i]↔task[i]`) → o consumidor **rateia igual** (`total_questoes / n_tasks`).

## Cláusula 3 — Sync read-on-demand

- Leitura **sob demanda** no boot/CLI; **sem cron**, sem daemon. A grade é **local + git** — não há serviço hospedado guardando estado dela.
- `--check` compara `sha256(PDF)` vs `grade._meta.fonte_sha256`; defasagem → `--rebuild`. A grade é **cache regenerável** do PDF: editá-la à mão é defeito (regenerar, não corrigir).

## Cláusula 4 — Derivador único

- **`tools/cronograma.py`** detém TODO o parse + a lógica de gap/radar. `day_plan.py`/`performance.py` **consomem** (importam), **não reparseiam** o PDF (anti-duplo-parser). Subcomandos: `--rebuild`/`--check`/`--json`/`--gap`/`--radar`/`--validate`.
- **Linchpin = `AREA_PDF_TO_CANON`** (constante única): os nomes longos do PDF (`Hepatologia`, `Oftalmologia`…) → as 20 áreas canônicas (`AREAS_VALIDAS`). É o coração do JOIN cronograma↔`sessoes_bulk`. Tasks multi-disciplina (Rev. por Questões abrangente) → `area_norm="Multi"`.

## Cláusula 5 — 🔴 Fronteiras duras (invariantes)

- **Zero write em `taxonomia_cronograma`** (tabela de desempenho-por-tema, `UNIQUE(area,tema)`, alimentada SÓ por `insert_questao.py`). Tasks repetem o mesmo tema em várias semanas com `tipo` diferente → escrevê-las quebraria o UNIQUE/a dedup s083 e furaria o resolver `(area,tema)`. O elo cronograma↔desempenho é **em memória** (join por nome normalizado), nunca por escrita.
- **Zero write em `sessoes_bulk`, FSRS (`fsrs_cards`/`fsrs_revlog`) e `review_log`.** O derivador é read-only.
- **Rótulos sujos (W4: `GO`, mojibake `Obstetrícia`) são normalizados NA LEITURA, com WARNING** — o db **não** é tocado. A migração destrutiva que limpa o db de fato é fork à parte.
- **Writes permitidos pela feature de cronograma (v1.1, corrigido): a tabela `preparacao_estado`** (`ipub.db`, chave/valor/`atualizado_em`/`fonte` — PRD `orquestracao-preparacao` part-1, 2026-07-06), NUNCA `taxonomia_cronograma`/`sessoes_bulk`/FSRS. Duas chaves hoje:
  - `semana_conteudo` — posição SSOT (semana de conteúdo), gravada por `python tools/preparacao.py --set-semana N`. **Substitui** o antigo "ponteiro de texto `Próxima = SNN` em `HANDOFF.md`/`ESTADO.md`" (v1.0 desta cláusula) — esse caminho está **deprecado**: `day_plan.py::_resolver_semana_conteudo()` só cai nele quando `preparacao_estado` está vazio, e emite `[WARN] POSICAO_VIA_TEXTO (deprecado)` em stderr quando isso acontece. Não editar mais o texto do HANDOFF/ESTADO como fonte — é saída derivada, não input.
  - ⚰️ **REVOGADA em 17/09/2026 (v1.3, PRD `plano-ssot-e-cards-v2` Parte 4)** — a chave `cronograma_conclusao_drive` deixou de ser fonte do boot, e com ela morreram `day_plan._conclusao_drive`, `_ordenar_por_drive`, o ramo calendário de `_cronograma_hoje` e o banner `Drive desatualizado`. *Motivo:* o snapshot envelhecia em silêncio útil-zero (42 dias no boot medido de 06/09) e a ordem que o usuário reordenava à mão nunca chegava ao agente — três fontes para uma pergunta, nenhuma delas verdade-de-estado. A conclusão e a ordem passaram a viver em `plano_tarefas` (bullet abaixo). ⚰️ **`cronograma.py --sync-drive` também está revogado em 17/09/2026** — não é invocado pelo agente nem pedido ao usuário, pelo mesmo motivo: o snapshot que ele grava não tem mais leitor. O **código** segue vivo e ainda escreve a chave; a remoção é a **Parte 8**, junto do congelamento do Drive, e está bloqueada até o operador confirmar que não faz mais o ritual de reordenação manual do xlsx — lápide, não deleção. Lápide operacional (a que o agente lê no ato) em [`/cronograma`](../../.claude/commands/cronograma.md). Texto original em `git show HEAD~:core/contracts/cronograma-contract.md`.
  - **`plano_tarefas` — a tabela da feature (v1.3).** É a **única exceção** ao read-only desta Cláusula, e a exceção é declarada com os **writers nomeados**: `db.plano_upsert_tarefas` (semeadura), `db.plano_set_status` (`--concluir`/`--cortar`/`--reabrir`), `db.plano_mover` e `db.plano_confirmar_area` — todos em `app/utils/db.py`, todos acionados por `tools/plano.py`, que não abre `sqlite3` próprio. Leitores: `db.plano_listar`, `db.plano_obter`, `db.plano_pendencia_revisao`; `day_plan.py` só lê. Uma linha por tarefa, com a `fonte` declarada (`extensivo`/`rf`/`custom`) e `origem_conclusao` como trilha de auditoria — `dashboard_2026-09-10` é status APROXIMADO por confissão do usuário, e zerá-lo é a passada de revisão por área (`--revisar-area`/`--confirmar-area`). 🔴 A fronteira do resto da Cláusula 5 continua intacta: `taxonomia_cronograma`, `sessoes_bulk`, FSRS e `review_log` seguem proibidos para esta feature. Norma de origem: PRD `plano-ssot-e-cards-v2`, partes 2-4. A tabela legada `cronograma_progresso` (escrita por `insert_questao`) fica como **legado lido por ninguém** — lápide, não deleção.

## ⚰️ Cláusula 5b — REVOGADA (Sync do Drive: dois sinais, dois donos) — v1.2, morta em 17/09/2026

> ⚰️ **Revogada em 17/09/2026 pela v1.3** (PRD `plano-ssot-e-cards-v2`, Parte 4). **Motivo:** a
> cláusula separava dois sinais do Drive — **conclusão** (coluna `Realizada?` do Dashboard EMED,
> lida pelo agente) e **ordem** (o xlsx reordenado à mão, ritual do usuário via `--sync-drive`) —
> e ambos deixaram de alimentar o boot: a conclusão e a ordem agora são colunas de `plano_tarefas`
> (`status`/`origem_conclusao` e `semana_plano`/`ordem`), editáveis por comando. O que **sobrevive
> como princípio geral**, e por isso continua valendo fora desta cláusula: *nenhum passo de boot
> pode exigir binário via MCP* e *caveat honesto no lugar de obrigação impossível*. O texto abaixo
> fica como registro histórico — **não é prescrição**; o `--sync-drive` segue existindo em código
> até a Parte 8, mas nada no boot o pede.

O sync era um passo único e **impossível**: mandava o agente baixar o xlsx via MCP no boot. `read_file_content` devolve xlsx como **base64** e `--sync-drive` precisa do arquivo binário real — o caminho não fecha. Tentá-lo foi o que produziu o boot de ~15 chamadas da s144 (defeito **D5**). Os dois sinais que estavam acoplados no xlsx se separam:

| Sinal | Fonte | Formato | Quem executa | Cadência |
|---|---|---|---|---|
| **Conclusão** (tarefa feita?) | planilha **"Dashboard EMED 2026"** — Google Sheets **nativo**, fileId em `.claude/commands/importar-planilha.md:32` | **texto puro** (`read_file_content` devolve tabelas markdown; coluna **`Realizada?`** por tarefa, 20 tabelas por disciplina) | **agente**, em runtime | 1x por dia-calendário |
| **Ordem** (sequência que o usuário reordenou) | `Cronograma de Reta Final.xlsx` (binário, sem substituto textual) | xlsx local | **usuário** — `python tools/cronograma.py --sync-drive <path-local>`, sem MCP nenhum | quando ele reordenar |

- **Nenhum passo de boot pode exigir binário via MCP.** Regra dura: se a leitura precisa de bytes, ela não é do agente. O agente pode **pedir** o ritual ao usuário; nunca ficar preso nele.
- **Caveat honesto substitui a obrigação impossível.** Sem conclusão fresca -> apresentar os temas dizendo que podem conter tarefas já feitas. Sem ordem fresca -> dizer que a ordem pode não ser a do usuário. **Nunca em silêncio, nunca bloqueando** (Cláusula 6: plano não é verdade-de-estado).
- O `Realizada?` é sinal de **conclusão declarada pelo usuário** na planilha que ele já preenche após cada estudo (`reconcile-contract.md §Absorção`) — não substitui `sessoes_bulk` como SSOT de volume, só responde "esta tarefa saiu da fila?".

## Cláusula 6 — Lente estratégica (dono do gap = fork)

- O cronograma não governa a meta; **a meta governa** (ultraplan §b.1). `--gap` reporta o gap honesto de volume (acum + cronograma restante vs meta), separando **gap de volume** (falta banco extra) de **gap de execução** (cobertura de conteúdo) — são grandezas distintas.
- O **fork estratégico** (meta 10k vs 12k) tem dono = usuário (decidido s093: **10.000 + gatilho S13**; 12k = teto). O reconcile reporta o gap materializado **uma vez** (W7), registra a decisão em `ESTADO §Metas`, e silencia até a premissa mudar.

## Cláusula 7 — Calibração de aula por `tipo`

- `tipo_norm` calibra a profundidade da aula/refresh por bloco (validado s092): `teoria` (bloco novo denso) → **aula descomprimida** (escada de degraus); `revisao`/`revisao_questoes` → **refresh comprimido** (gatilhos + armadilhas). Conecta com o PRD de **Revisão Calibrada** (`docs/plans/s094-revisao-calibrada-PRD.md`): o `tipo` modula a **largura**, a nota 1-10 modula a **profundidade**.

---

## Integração

- **Boot (`AGENTE §2 passo 4`) — v1.3:** `day_plan.py` deriva o bloco `🧭 Cronograma` de **`plano_tarefas`**: semana do plano corrente (menor `semana_plano` com pendência), fase (1 até 01/11 / 2 daí em diante), X/Y tarefas feitas da semana, as próximas 3-5 tarefas pendentes em ordem (`fonte`, `tema`, `tipo`, `q_previstas`, `url_lista`) e o ritmo-alvo. É a 4ª fonte do Plano do Dia (dormência × volume × FSRS × **plano**). ⚰️ *Era "importa `cronograma.py` e renderiza semana de conteúdo vs nominal ... próximos temas"* — o ramo calendário morreu em 17/09/2026 (Parte 4). `cronograma.py` segue sendo o derivador do PDF (Cláusula 4) e a fonte da **semeadura** do plano; deixou de ser a fonte do "o que vem agora".
- **Reconcile:** condições **W5/W6/W7** (sempre WARNING, nunca BLOCKING — ver `reconcile-contract.md`). Travar boot por estar atrasado seria hostil.
- **`/performance`, `/refrescar`, `/revisar`:** consumidores opcionais (bloco "Cronograma vs Meta"; tie-break de dormência a favor do tema da semana; filtro de cards da semana). Nenhum altera política FSRS.

---

## Fora de escopo (v1.0)

- ~~Reconciliar PDF × xlsx do Drive (R8)~~ — implementado na v1.1 e ⚰️ **REMOVIDO em 18/09/2026** (Parte 8: o Drive deixou de ser fonte; `--sync-drive` e as 4 funções saíram do código). Segue fora de escopo: alinhamento fino `questoes_por_lista[i] ↔ tasks[i]` (linha abaixo) — R8 cobriu só o booleano concluído/pendente por tema, não contagem por task.
- Migração destrutiva de rótulos sujos no `sessoes_bulk` (fork à parte — só normalização na leitura).
- Alinhamento exato `questoes_por_lista[i] ↔ tasks[i]` (v1.1; hoje rateio igual).
- Resolução robusta tema→resumo por nome de arquivo em `get_topic_context._find_resumo` (hoje indexa só `especialidade`/`area`/`aliases` → fuzzy frágil). **Pré-requisito do `infer_nota` do PRD de Revisão Calibrada** — fix aditivo = indexar `path.stem.lower()`.

---

## Changelog

- **v1.3 (2026-09-17, s185 — PRD `plano-ssot-e-cards-v2`, Parte 4):** **o plano vira dado e o
  Drive sai do boot.** (a) **`plano_tarefas` declarada como a tabela da feature** na Cláusula 5 —
  a única exceção ao read-only, com os quatro writers nomeados (`plano_upsert_tarefas`,
  `plano_set_status`, `plano_mover`, `plano_confirmar_area`, todos em `app/utils/db.py`); as
  fronteiras sobre `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log` ficam intactas.
  (b) ⚰️ **Cláusula 5b revogada** e o bullet `cronograma_conclusao_drive` da Cláusula 5 lapidado:
  conclusão e ordem passaram a ser colunas do plano. (c) ⚰️ **`--sync-drive` lapidado na skill**
  [`/cronograma`](../../.claude/commands/cronograma.md) — o CLI continua existindo (remoção =
  Parte 8, com o congelamento do Drive), mas nenhum passo de boot o pede. (d) Espelhado em
  `reconcile-contract.md` (**W8 revogado**, **W5b novo** = `--check-extensivo`) e em
  `AGENTE.md §2 passo 4`/§6. (e) Termos cadastrados em `docs/MEMORIA-AUDITORIA.md §12` —
  ⚰️ revogados: `Drive desatualizado`, `conclusao_desatualizada`, `dois sinais, dois donos` —,
  fechando os três passos de AGENTE §10.10 no mesmo commit (declarar + lapidar + cadastrar).
- ⚰️ **v1.2 (2026-08-14, s144)** — *tudo nesta entrada foi revogado nas Partes 4 e 8 (17-18/09/2026); fica como registro:* **Cláusula 5b** — o sync do Drive deixa de ser passo único e impossível. Conclusão migra para a coluna `Realizada?` do **Dashboard EMED 2026** (Sheets nativo, texto puro via `read_file_content`), executável pelo agente; ordem vira **ritual do usuário** com o xlsx local (`--sync-drive`, sem MCP). Proibido exigir binário via MCP em passo de boot; caveat honesto quando faltar qualquer um dos dois sinais. Origem: achado §8 da auditoria de sistemas (s144, defeito D5 — boot de ~15 chamadas); spec `.vibeflow/specs/consolidacao-part-4.md`. Espelhado em `reconcile-contract.md` W8 e `AGENTE.md §2 passo 4` (reescrito de 272 para 56 palavras).
- ⚰️ **v1.1 (2026-07-08)** — *revogada em 18/09/2026 (Parte 8); fica como registro:* implementa R8 (marcador de conclusão real do xlsx do Drive) — `tools/cronograma.py --sync-drive` (parse `cell.font.strike` + matching `(semana,tema,tipo_norm)` contra `grade.json`) grava snapshot em `preparacao_estado.cronograma_conclusao_drive`; `day_plan.py` filtra "próximos temas" pela fronteira real quando o snapshot é do dia-calendário corrente (W8, `reconcile-contract.md`). Corrige a Cláusula 5, que estava desatualizada desde a migração do ponteiro de posição para `preparacao_estado` (PRD `orquestracao-preparacao`, 2026-07-06) — achado **F33** (`AUDITORIA_MEDHUB.md`), spec `.vibeflow/specs/cronograma-sync-conclusao-drive.md`.
- **v1.0 (2026-06-27, s095):** primeira instância. F1 `tools/cronograma.py` (derivador + `AREA_PDF_TO_CANON`) + `core/cronograma/grade.json` (30 sem · 352 tasks · 10218q; validado S10=273, S11-28=6689/222); F2 `--radar` (cobertura × performance, fronteira pré/pós-ENAMED); F3 integração no `day_plan.py` (conteúdo×calendário, ponteiro `Próxima=SNN`); F4 este contrato + patches reconcile/AGENTE/forgetting-curve + skill. Adaptado da arquitetura contract-driven do irmão `agente-daktus-content`.
