---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [reconcile-contract, forgetting-curve-contract, estado-contract, AGENTE]
---

# Contrato do Cronograma (Sync Cronograma ↔ Performance ↔ FSRS)
**Versão 1.0 | 2026-06-27 (sessão 095) — primeira instância. Materializa o ultraplan `docs/plans/s094-ultraplan.md §c/§d`.**

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

- Leitura **sob demanda** no boot/CLI; **sem cron**, sem daemon. Coerente com **Zero-DB no Cloud** (Streamlit não persiste; a grade é local + git).
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
  - `cronograma_conclusao_drive` — snapshot da fronteira real de conclusão (tema riscado no xlsx do Drive) **e da ordem real das tarefas por semana** (`ordem` = linha da célula no xlsx, que é onde o usuário reordena à mão), gravado por `python tools/cronograma.py --sync-drive <xlsx>` (specs `cronograma-sync-conclusao-drive` + `boot-cronograma-drive-confiavel-part-1`, W8/`reconcile-contract.md`). Cada task do snapshot: `{semana, tarefa, area_norm, tema, tipo_norm, concluido, ordem}` (`ordem=None` quando o tema não casa nenhuma célula do xlsx). Frescor = dia-calendário de `atualizado_em`; `day_plan.py` degrada pro comportamento calendário puro (semana inteira, ordem do PDF) quando o snapshot está ausente, de dia anterior, ou em formato antigo sem `ordem`. Snapshot velho **nunca é silencioso**: o `day_plan` emite banner `Drive desatualizado` e o boot trata o sync como ação obrigatória-de-tentativa (AGENTE §2 passo 4).

## Cláusula 6 — Lente estratégica (dono do gap = fork)

- O cronograma não governa a meta; **a meta governa** (ultraplan §b.1). `--gap` reporta o gap honesto de volume (acum + cronograma restante vs meta), separando **gap de volume** (falta banco extra) de **gap de execução** (cobertura de conteúdo) — são grandezas distintas.
- O **fork estratégico** (meta 10k vs 12k) tem dono = usuário (decidido s093: **10.000 + gatilho S13**; 12k = teto). O reconcile reporta o gap materializado **uma vez** (W7), registra a decisão em `ESTADO §Metas`, e silencia até a premissa mudar.

## Cláusula 7 — Calibração de aula por `tipo`

- `tipo_norm` calibra a profundidade da aula/refresh por bloco (validado s092): `teoria` (bloco novo denso) → **aula descomprimida** (escada de degraus); `revisao`/`revisao_questoes` → **refresh comprimido** (gatilhos + armadilhas). Conecta com o PRD de **Revisão Calibrada** (`docs/plans/s094-revisao-calibrada-PRD.md`): o `tipo` modula a **largura**, a nota 1-10 modula a **profundidade**.

---

## Integração

- **Boot (`AGENTE §2 passo 4`):** `day_plan.py` importa `cronograma.py` e renderiza semana de conteúdo vs nominal, q previstas, próximos temas e **dois ritmos-alvo** (terminar a grade vs meta-prova). É a 4ª fonte do Plano do Dia (dormência × volume × FSRS × **cronograma**).
- **Reconcile:** condições **W5/W6/W7** (sempre WARNING, nunca BLOCKING — ver `reconcile-contract.md`). Travar boot por estar atrasado seria hostil.
- **`/performance`, `/refrescar`, `/revisar`:** consumidores opcionais (bloco "Cronograma vs Meta"; tie-break de dormência a favor do tema da semana; filtro de cards da semana). Nenhum altera política FSRS.

---

## Fora de escopo (v1.0)

- ~~Reconciliar PDF × xlsx do Drive (R8)~~ — **implementado v1.1** (marcador de conclusão/tema riscado, `--sync-drive`). Segue fora de escopo: alinhamento fino `questoes_por_lista[i] ↔ tasks[i]` (linha abaixo) — R8 cobriu só o booleano concluído/pendente por tema, não contagem por task.
- Migração destrutiva de rótulos sujos no `sessoes_bulk` (fork à parte — só normalização na leitura).
- Alinhamento exato `questoes_por_lista[i] ↔ tasks[i]` (v1.1; hoje rateio igual).
- Resolução robusta tema→resumo por nome de arquivo em `get_topic_context._find_resumo` (hoje indexa só `especialidade`/`area`/`aliases` → fuzzy frágil). **Pré-requisito do `infer_nota` do PRD de Revisão Calibrada** — fix aditivo = indexar `path.stem.lower()`.

---

## Changelog

- **v1.1 (2026-07-08):** implementa R8 (marcador de conclusão real do xlsx do Drive) — `tools/cronograma.py --sync-drive` (parse `cell.font.strike` + matching `(semana,tema,tipo_norm)` contra `grade.json`) grava snapshot em `preparacao_estado.cronograma_conclusao_drive`; `day_plan.py` filtra "próximos temas" pela fronteira real quando o snapshot é do dia-calendário corrente (W8, `reconcile-contract.md`). Corrige a Cláusula 5, que estava desatualizada desde a migração do ponteiro de posição para `preparacao_estado` (PRD `orquestracao-preparacao`, 2026-07-06) — achado **F33** (`AUDITORIA_MEDHUB.md`), spec `.vibeflow/specs/cronograma-sync-conclusao-drive.md`.
- **v1.0 (2026-06-27, s095):** primeira instância. F1 `tools/cronograma.py` (derivador + `AREA_PDF_TO_CANON`) + `core/cronograma/grade.json` (30 sem · 352 tasks · 10218q; validado S10=273, S11-28=6689/222); F2 `--radar` (cobertura × performance, fronteira pré/pós-ENAMED); F3 integração no `day_plan.py` (conteúdo×calendário, ponteiro `Próxima=SNN`); F4 este contrato + patches reconcile/AGENTE/forgetting-curve + skill. Adaptado da arquitetura contract-driven do irmão `agente-daktus-content`.
