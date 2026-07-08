# Spec: Sync de conclusão real do cronograma (xlsx do Drive → boot)

> Gerado via /vibeflow:gen-spec a partir de `.vibeflow/prds/cronograma-sync-conclusao-drive.md` em 2026-07-08

## Objective

O boot diário para de recomendar como "próximo tema" algo que o usuário já marcou como concluído (riscado) na planilha `Cronograma de Reta Final.xlsx` do Drive, passando a usar a fronteira real de conclusão em vez de só a posição calendário do `Cronograma.pdf`.

## Context

`day_plan.py::_cronograma_hoje()` deriva "próximos temas" só de `core/cronograma/grade.json` (estático, do `Cronograma.pdf`), cruzado com a semana de conteúdo (`db.get_semana_conteudo()`, tabela `preparacao_estado`). Nunca lê o marcador de conclusão real (tema riscado) que o usuário mantém no xlsx do Drive — gap já documentado como fora de escopo v1.0 em `cronograma-contract.md` (item R8) e nunca mecanizado. Materializou-se ao vivo em 2026-07-08 (achado **F33**, `AUDITORIA_MEDHUB.md`): o boot recomendou MFC/Imunizações/Apendicite como pendentes quando já estavam feitos; o pendente real (DITC II, Distúrbios do Potássio, Cefaleias+Epilepsias, HAS Pt.2 + 2 blocos de Revisão por Questões) ficou invisível até o usuário contestar.

**Descoberta durante este gen-spec que atualiza a premissa do PRD:** já existe um SSOT genérico em `ipub.db` (tabela `preparacao_estado`, chave/valor/`atualizado_em`/`fonte`, via `db.get_preparacao`/`set_preparacao` — PRD `orquestracao-preparacao` part-1, 2026-07-06) que **já substituiu** o "ponteiro de texto `Próxima = SNN`" descrito na Cláusula 5 do `cronograma-contract.md` v1.0. `day_plan.py::_resolver_semana_conteudo()` já trata a leitura por regex de texto como **caminho deprecado** (emite `[WARN] POSICAO_VIA_TEXTO (deprecado)` em stderr). Ou seja: o `cronograma-contract.md` está desatualizado nesse ponto — este spec corrige isso como parte do trabalho, e reaproveita `preparacao_estado` em vez de criar um arquivo `.json` novo (desvio deliberado do mecanismo literal proposto no PRD; justificativa em Technical Decisions).

## Definition of Done

1. `python tools/cronograma.py --sync-drive <path-para-xlsx-baixado>` lê o xlsx (mesma aba/estrutura documentada em `importar-planilha.md`), extrai `cell.font.strike` por task, casa cada task com `grade.json` por `(semana, tema normalizado)` e grava um snapshot JSON em `preparacao_estado` (nova chave `cronograma_conclusao_drive`) via `db.set_preparacao`. Verificação: rodar contra uma cópia real do xlsx baixada nesta sessão e confirmar via `db.get_preparacao('cronograma_conclusao_drive')` que o snapshot contém MFC/Imunizações(I-II)/Apendicite/DITC-I como concluídos e DITC-II/Distúrbios do Potássio/Cefaleias+Epilepsias/HAS Pt.2 como pendentes (mesmo resultado já confirmado manualmente nesta sessão).
2. `day_plan.py::_cronograma_hoje()` (ou função equivalente), quando o snapshot existe e é do dia-calendário corrente, filtra `temas`/`temas_material` da semana de conteúdo para excluir tasks marcadas `concluido=true`. Verificação: `python tools/day_plan.py --json` no estado real de hoje não lista MFC/Imunizações/Apendicite entre os temas do bloco `cronograma`.
3. Quando o snapshot está ausente ou desatualizado (`atualizado_em` de dia-calendário anterior), `day_plan.py` cai no comportamento atual (posição calendário pura, sem filtro) **e** o dict retornado por `_cronograma_hoje()` inclui um campo `conclusao_desatualizada: true` que `render()` imprime como um aviso de uma linha no Plano do Dia (nunca falha silenciosamente). Verificação: teste unitário em `tools/test_orquestrador.py` com `atualizado_em` de ontem confirma fallback + flag.
4. `reconcile-contract.md` ganha a condição **W8** ("posição calendário de `grade.json` diverge da fronteira real do xlsx") na tabela de boot check + passo de resolução em "PASSO 3", seguindo o padrão WARNING-nunca-BLOCKING já estabelecido para W5-W7 (mesma seção/formatação).
5. `cronograma-contract.md` Cláusula 5 é corrigida: remove a alegação de que o ponteiro de texto é o "único write permitido" (obsoleta) e documenta os dois writes hoje permitidos — `preparacao_estado.semana_conteudo` (já existente, órfão de documentação) e `preparacao_estado.cronograma_conclusao_drive` (novo, este spec).
6. `AGENTE.md §2 passo 4` ganha uma instrução mecânica explícita: se `day_plan` sinalizar `conclusao_desatualizada`, buscar o xlsx via MCP Drive (fileId já registrado em `importar-planilha.md`) e rodar `--sync-drive` antes de montar o plano do dia — substitui a dependência de o agente "lembrar" manualmente.

## Scope

- `tools/cronograma.py`: subcomando `--sync-drive <xlsx_path>` — parse de strike/fill por task (reaproveitando a mecânica já prototipada ad-hoc nesta sessão: `openpyxl`, linha 2 = datas por semana, linhas 4-16 = slots), normalização de tema (lowercase + strip de acentos via `unicodedata` + colapso de whitespace, inclusive através de quebras de linha internas da célula), matching contra `grade.json` por `(semana, tema)`, escrita via `db.set_preparacao('cronograma_conclusao_drive', json.dumps(...), fonte='drive_sync')`.
- `tools/day_plan.py`: `_cronograma_hoje()` lê `db.get_preparacao('cronograma_conclusao_drive')`, valida frescor (mesmo dia-calendário), filtra tasks concluídas do resultado; `render()` imprime o aviso de desatualização quando aplicável.
- `tools/test_orquestrador.py`: testes para normalização de tema, matching semana+tema, e fallback de frescor (snapshot ausente / de ontem / de hoje).
- `core/contracts/reconcile-contract.md`: nova linha W8 + resolução.
- `core/contracts/cronograma-contract.md`: correção da Cláusula 5.
- `AGENTE.md`: instrução no passo 4 da seção 2.

## Anti-scope

- **Sem cron/daemon** — o gatilho é sempre um passo explícito do boot do agente (Cláusula 3 do `cronograma-contract.md`, sync read-on-demand).
- **Sem arquivo `core/cronograma/conclusao_drive.json`** — desvio do PRD original; usa `preparacao_estado` (ver Technical Decisions). Não criar o arquivo.
- **Sem alterar `Cronograma.pdf`/`grade.json` como SSOT estrutural** — o xlsx é só a camada de conclusão, nunca substitui o PDF (Cláusula 1).
- **Sem escrita em `taxonomia_cronograma`, `sessoes_bulk`, FSRS** (`fsrs_cards`/`fsrs_revlog`) a partir desta feature — fronteiras duras da Cláusula 5 continuam valendo para essas tabelas especificamente.
- **Sem reimportar volume/questões** a partir do xlsx — isso já é o fluxo W1/F29 (`/importar-planilha`); este spec cobre só o marcador de conclusão de tema.
- **Sem alinhar `questoes_por_lista[i] ↔ tasks[i]`** — já fora de escopo v1.0 do cronograma-contract, não é o problema deste spec.
- **Sem fechar F33 no `AUDITORIA_MEDHUB.md` como parte deste spec** — isso é um passo de fechamento pós-`/vibeflow:audit`, não um arquivo do orçamento de implementação.
- **Sem tornar `day_plan.py` capaz de MCP** — ele só lê o que já está em `preparacao_estado`; quem busca no Drive é sempre o agente.

## Technical Decisions

- **`preparacao_estado` (chave nova) em vez de arquivo `.json` gitignored — desvio do PRD original.** Descoberto neste gen-spec: já existe exatamente esse mecanismo (chave/valor + `atualizado_em` nativo para checar frescor + `fonte` para rastrear origem), criado pelo PRD `orquestracao-preparacao` part-1 e já em uso para `semana_conteudo`. Reaproveitar evita duplicar lógica de cache/staleness (o PRD original teria reimplementado isso à mão num JSON) e mantém um único padrão de "estado de preparação" no repo. Trade-off aceito: acopla esse dado ao `ipub.db` (não versionável em git) em vez de um arquivo — mas isso é exatamente o mesmo trade-off que o time já aceitou para `semana_conteudo`, e é consistente com a decisão do discovery (snapshot gitignored de qualquer forma).
- **Matching por `(semana, tema normalizado substring)`, não por índice de task.** O xlsx bundla múltiplos temas por célula ("Tema A; Tema B; Tema C (Revisão por Questões)") enquanto `grade.json` tem 1 task = 1 tema — índice posicional não bate 1:1 entre as duas fontes (confirmado ad-hoc: comparar `tools/cronograma.py::parse_grade` com a estrutura real do xlsx lida nesta sessão). Normalização usa `unicodedata.normalize('NFKD', ...)` + strip de combining chars, porque a extração via MCP retorna acentuação corrompida (mojibake, confirmado nesta sessão: `"Doen�as"`).
- **Sem match = `concluido: false` (conservador).** Um tema de `grade.json` que não aparece em nenhuma célula do xlsx da mesma semana fica pendente por default — nunca assume concluído sem confirmação positiva do tachado. Prioriza falso-negativo (mostra tema já feito como pendente) sobre falso-positivo (esconde tema pendente como feito), porque o segundo é exatamente o bug que originou este spec.
- **Frescor = dia-calendário, não TTL de horas.** Decisão do discovery: 1 sync por dia-calendário. Comparar só a parte de data (`YYYY-MM-DD`) de `atualizado_em` vs `date.today()`, não um TTL rolante — simples e previsível (1 chamada MCP no primeiro boot do dia, zero nos seguintes).
- **Contratos atualizados junto com o código, não depois.** `cronograma-contract.md` já estava desatualizado em relação ao `orquestracao-contract.md`/`preparacao_estado` antes mesmo deste spec (Cláusula 5 nunca foi corrigida quando o SSOT migrou pra db em 2026-07-06) — esse é o mesmo tipo de drift documentação↔código que gerou o F33 original. Corrigir os dois contratos (`reconcile-contract.md` + `cronograma-contract.md`) faz parte do DoD, não é follow-up opcional.

## Applicable Patterns

- **`agent-workflow-protocol.md`** — o novo passo de sync entra na sequência de boot já normatizada (`AGENTE.md §2`); não inventa uma sequência paralela.
- **CLI conventions (`.vibeflow/conventions.md §CLI tools`)** — `--sync-drive` segue o mesmo estilo de subcomando `argparse` de `--rebuild`/`--check`/`--gap` já existentes em `cronograma.py`; imprime resumo humano em stdout, `sys.exit` não-zero em erro de parsing do xlsx.
- **`cronograma-contract.md` Cláusula 3/4** — sync read-on-demand, sem cron; derivador único (`cronograma.py` ganha a nova responsabilidade em vez de um script solto).

## Risks

- **MCP do Drive indisponível/falha de auth (sessão headless, schedule/cron do Claude Code).** Mitigação: `--sync-drive` só roda dentro do passo do agente (que já lida com falha de MCP tentando/reportando); ausência de snapshot fresco sempre degrada pro comportamento calendário atual (DoD item 3), nunca bloqueia o boot.
- **Falso-negativo de matching** (nome do tema no xlsx difere o suficiente do `grade.json` mesmo após normalização — ex. abreviação diferente). Mitigação: `--sync-drive` loga no stdout a lista de temas de `grade.json` da semana atual que NÃO casaram com nenhuma célula do xlsx, para o agente revisar manualmente quando a taxa de "sem match" for alta; não é um erro fatal (cai no default conservador `concluido:false`).
- **Estrutura do xlsx muda** (usuário reorganiza linhas/colunas). Mitigação: `--sync-drive` valida que a linha 2 contém datas no formato esperado antes de prosseguir; aborta com erro claro em vez de gravar snapshot incorreto.
- **Regressão do drift contrato↔código que originou o F33.** Mitigação: DoD itens 4-6 exigem que os contratos sejam corrigidos no mesmo spec, não depois.
