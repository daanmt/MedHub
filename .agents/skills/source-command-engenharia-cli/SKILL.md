---
name: "source-command-engenharia-cli"
description: "Assinatura canônica dos CLIs de ENGENHARIA do MedHub (harness, sensores, curadoria em lote, manutenção do ipub.db) — os que não pertencem a nenhuma skill de estudo. Consultar antes de invocar qualquer tool de tools/ que não apareça nas outras skills."
---

<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI.
     Edite `.claude/commands/engenharia-cli.md` e rode `python tools/sync_skills.py`.
     Qualquer edicao feita neste arquivo e SOBRESCRITA no proximo sync. -->

# source-command-engenharia-cli

Use this skill when the user asks to run the migrated source command `engenharia-cli`.

## Command Template

# Skill: CLIs de Engenharia

> **Portador canônico da assinatura** (`AGENTE.md §7.2`: *"cada CLI em `tools/` tem assinatura
> canônica em UMA skill"*) dos CLIs que **não têm casa numa skill de estudo** — sensores do
> harness, manutenção do `ipub.db`, curadoria em lote e instrumentos de auditoria.
> O que este arquivo **não** é: orquestração. Sequência de passos é do workflow
> (`.agents/workflows/`); aqui está **o que cada flag faz**.

**Por que ele existe (D5, s177).** A regra §7.2 nunca teve instrumento. Medido em 11/09/2026,
antes deste arquivo: **65 de 168 flags (≈39%) não apareciam em skill nenhuma** e **17 CLIs não
eram citados por skill alguma** — entre eles `recurate_cards` (o reescritor in-place que **grava
no baralho**) e `normalize_taxonomia` (declaradamente **destrutivo**). O sensor que passou a medir
isso é `tools/cli_signature_check.py`, documentado aqui embaixo como qualquer outro.

🔴 **Fronteira dura de leitura:** um CLI marcado **[DESTRUTIVO]** grava no `ipub.db`. Para
qualquer um deles vale `AGENTE.md §10.7` — **`tools/backup_db.py` antes**, **dry-run é o default**,
e o COUNT esperado é **declarado antes** de `--apply`.

---

## Sensores do harness (read-only, WARN-first)

Todos seguem a mesma convenção: **detectam e reportam, nunca corrigem, nunca bloqueiam**, e
expõem `run_checks()` com a mesma assinatura para o `auto_check` consumir.

### `tools/cli_signature_check.py` — assinatura canônica de CLI × skill (D5)

| Flag | Função |
|---|---|
| `--json` | Worklist em JSON: `[{alvo, payload:{flags, orfas, donos}}]`. |
| `--limit N` | Quantos CLIs detalhar no modo texto (default 25). |

Flag órfã = declarada por `add_argument` no CLI e **ausente de toda skill que cita aquele
arquivo**. Extração pela **AST**, não por regex sobre o texto — a 1ª versão leu a própria
docstring e se acusou. Limites declarados na docstring do módulo (parser dinâmico escapa; mede
presença, não semântica; flag genérica pode colar em skill vizinha e **inflar** a cobertura).

### `tools/consistencia_check.py` — consistência entre registros (G5 · G10 · G14)

| Flag | Função |
|---|---|
| `--json` | Achados em JSON: `[{check, alvo, payload}]`. |
| `--check {todos,tabela,paths,status}` | Roda só um sub-check (default `todos`). |

Três registros que envelheciam em silêncio porque nada perguntava se ainda diziam a verdade:
**`tabela`** (a §7.4 do `AGENTE.md` é gerada e colada — cada CLI novo a deixa stale) ·
**`paths`** (`tools/*.py` inexistente citado num doc de raiz; o `MEMORY_POINTERS` só alcançava
`memory/`) · **`status`** (achado `**ABERTO**` no `AUDITORIA_MEDHUB.md` com lápide de `FEITO` no
`§11`). 🔴 Duas regras de precisão nasceram de medição: linha que **afirma a ausência** é lápide,
não ponteiro morto; e `PARCIAL` **não** é contradição — é o meio-termo declarado.

O módulo também é a casa de duas **derivações** que o `auto_check` consome no lugar de listas
digitadas: `portadores_derivados()` (F95) e `termos_revogados_do_ledger()` (o (ii') do F90, lido
dos marcadores `<!-- TERMO-REVOGADO: ... -->` do §12 do inventário).

### `tools/doc_drift.py` — drift doc-vs-código

| Flag | Função |
|---|---|
| `--json` | Achados em JSON. |
| `--mode {all,annot,refs}` | `all` (default) · `annot` = só anotações `drift-check` nos 4 docs de estado · `refs` = só referências mortas em `.claude/commands/`, `.claude/agents/`, `.agents/workflows/`, `core/contracts/`. |

### `tools/reachability_check.py` — alcançabilidade (D4)

| Flag | Função |
|---|---|
| `--json` | Achados em JSON (alvo sem nenhum referenciador vivo). |
| `--tabela` | Tabela markdown dos CLIs vivos + quem os alcança. **É a fonte da §7.4 do `AGENTE.md`** — aquela tabela é GERADA: regenerar e colar, nunca editar à mão. |

### `tools/card_self_sufficiency.py` — card que não se sustenta sozinho

| Flag | Função |
|---|---|
| `--json` | Worklist de reforja em JSON (achados = cards com dêixis/anáfora sem contexto). |

### `tools/ledger_self.py` — ledger-of-self (memória dos WARNs do harness)

| Flag | Função |
|---|---|
| `--list` | Achados **abertos** ordenados por recorrência (quantas vezes o mesmo WARN voltou). |
| `--json` | Saída machine-readable. |

⚠️ O contador de recorrência mede **quantas vezes o sensor rodou** com o achado aberto, não
tamanho de dívida. Para atomicidade, a cifra de dívida é `tools/reforja.py --fila` (ver
`estilo-flashcard.md`) — os dois números divergem por construção e isso está declarado.

### `tools/learning_efficacy.py` — eficácia de aprendizado por dimensão

| Flag | Função |
|---|---|
| `--json` | Saída JSON crua. |

### `tools/review_radar.py` — radar de dormência por TEMA

| Flag | Função |
|---|---|
| `--limit N` | Temas no ranking (default 12). |
| `--area AREA` | Filtra por área (match **exato**). |
| `--json` | Saída JSON. |
| `--all` | Ignora `--limit` (todos os temas). |

Alimenta a seleção do tema dormente; o carimbo em `review_log` é de `dormant_refresh.py`
(assinatura em `revisar.md`).

### `tools/fsrs_load.py` — carga do calendário FSRS (read-only, exceto `--blackout --apply`)

| Flag | Função |
|---|---|
| `--dias N` | Horizonte da previsão de carga. |
| `--json` | Saída JSON. |
| `--blackout` | **F71:** painel do blackout de prova (dia da prova + o seguinte, lidos de `core/provas.json`) e **re-rodada do balanceador** sobre a fila, em dry-run. |
| `--apply` | Só com `--blackout`: grava o diff **declarado** (COUNT-ASSERT). **[DESTRUTIVO]** — move `due`, nunca `stability`/`difficulty`. |

---

## Manutenção do `ipub.db` — todos **[DESTRUTIVO]**, dry-run por default

### `tools/normalize_taxonomia.py` — saneia `taxonomia_cronograma` (Fase 1 da curadoria)

| Flag | Função |
|---|---|
| `--apply` | Grava (default: dry-run). |

Resolve o que a dedup **não** pega: encoding/acento, área inválida fora de `core/areas.json`,
duplicata **conceitual** (mesmo tema, nomes diferentes), `[bulk]`/`Geral` vazios. Transação
atômica, re-aponta FKs, recria `UNIQUE(area,tema)` no fim — duplicata restante causa rollback.

### `tools/cards_prune.py` — poda de flashcards **[DESTRUTIVO]**, o único caminho de EXCLUSÃO

| Flag | Função |
|---|---|
| `--criterio {aposentados-sem-historico}` | Critério nomeado de seleção (v0: `needs_qualitative=2` sem `fsrs_revlog` e sem `reforja_marks`). Novo critério entra por nome no código, nunca por SQL livre. |
| `--ids A,B,C` | Ids explícitos (lote triado à mão); vence `--criterio`. Id inexistente é ignorado e o `--expect` denuncia. |
| `--apply` | Grava (default: dry-run imprime N + ids). Exige `--expect`. |
| `--expect N` | COUNT-ASSERT pré: N esperado; se diferir do N medido na hora, **recusa (exit 2)** sem rodar nem o backup. |
| `--db PATH` | Caminho do banco (default: `ipub.db` da raiz). |

Rito do `--apply`, nunca pulado: `backup_db.py` -> export das linhas das 4 tabelas para
`artifacts/backups/pruned_<ts>.json` -> DELETE em UMA transação (`fsrs_revlog` -> `reforja_marks`
-> `fsrs_cards` -> `flashcards`) -> COUNT-ASSERT pós (caiu exatamente N, nenhum id sobreviveu).
Não existe flag para pular o backup. Não toca `questoes_erros`, taxonomia, `review_log`, nem
`stability`/`difficulty`. Origem: PRD `plano-ssot-e-cards-v2` P5 (s183) -- lote 1 = 125 aposentados
sem histórico; os 67 com histórico ficam até triagem. Spec `.vibeflow/specs/plano-ssot-e-cards-v2-part-5.md`.

### `tools/dedup_taxonomia.py` — colapsa `(area,tema)` duplicados **exatos**

| Flag | Função |
|---|---|
| `--apply` | Grava (default: dry-run). |
| `--merge {max,sum}` | Estratégia de merge das métricas (default `max`). |

`MAX` é o default porque `taxonomia.questoes_realizadas` **não é o SSOT de volume** (esse é
`sessoes_bulk`) — somar inflaria um número que ninguém deveria ler como verdade.

### `tools/backfill_review_log.py` — semeia `review_log` com a última revisão REAL

| Flag | Função |
|---|---|
| `--apply` | Grava (default: dry-run). |

**Nunca usa a data de hoje** (falsificaria a curva): deriva de `MAX(fsrs_cards.last_review)` ou
de `taxonomia.ultima_revisao`. Tema sem sinal real é **pulado**. Idempotente. Rodar **depois** da
dedup, para não semear ids que seriam mesclados.

### `tools/index_resumos.py` — (re)indexa `resumos/` no ChromaDB

| Flag | Função |
|---|---|
| `--dir DIR` | Raiz dos resumos (default `resumos`). |
| `--clear` | Deleta a indexação antiga e recria do zero. |

Motor único de RAG = `app/engine/rag.py`, **gold-only** (indexa `.md`, não PDF).

---

## Curadoria em lote de flashcards

> A régua de autoria e a fila de reforja vivem em `estilo-flashcard.md`; a orquestração da
> curadoria, em `.agents/workflows/curar-cards.md`. Aqui está só a assinatura.

### `tools/recurate_cards.py` — o reescritor in-place CANÔNICO **[DESTRUTIVO]**

| Flag | Função |
|---|---|
| `--from SRC` | **Obrigatório.** JSON com a lista de edições. |
| `--apply` | Grava. **Dry-run é o default.** |
| `--dry-run` | Explícito e redundante (mantido para não quebrar o workflow documentado). |
| `--permitir-atomicidade` | Rebaixa o gate 4 (atomicidade) de bloqueio para aviso — **só** para card discriminador legítimo, conferido a olho. |

Preserva `card_id` e portanto o estado FSRS (`fsrs_cards`/`fsrs_revlog` intactos); incrementa
`card_version`. **ALL-OR-NOTHING**: falha de qualquer gate em qualquer item e **nada** é aplicado
— lote parcialmente aplicado deixa o baralho num estado que ninguém sabe descrever. Quatro gates:
schema · encoding (§4.5) · formulação · **atomicidade sobre o conteúdo PROPOSTO** (o remédio é
auditado pelo mesmo critério que diagnosticou a doença).

### `tools/insert_card_extra.py` — card adicional sobre um `questao_id` EXISTENTE

| Flag | Função |
|---|---|
| `--from SRC` | **Obrigatório.** JSON: `[{questao_id, tema_id, tipo?, frente_contexto?, frente_pergunta, verso_resposta, verso_regra_mestre?, verso_armadilha?, origem_card?}]`. |
| `--apply` | Grava (default: dry-run). |

Difere de `insert_questao.py`: **não** cria questão nova — herda `questao_id`/`tema_id` do
original. Idempotente por `(questao_id, frente_pergunta)`. É o CLI da **atomização**: quando
reforjar um card gera um 2º conceito do mesmo erro.

### `tools/detect_clones.py` — near-duplicates por TEMA (read-only)

| Flag | Função |
|---|---|
| `--limiar F` | Similaridade mínima 0-1 (default 0.72). |
| `--area AREA` | Filtra por área. |

Complementa o linter sintático, que é cego a clone. Compara `frente_pergunta + verso_resposta`
entre cards ativos do mesmo tema. **Não grava nada** — a fusão é curadoria.

### `tools/audit_flashcard_quality.py` — sinais sintáticos + cross-field (read-only)

| Flag | Função |
|---|---|
| `--gate-miss` | Contador de gate-miss da FRENTE (F81/B1), **com janela declarada**. |
| `--examples N` | Quantos exemplos mostrar do sinal escolhido. |
| `--signal S` | Qual sinal detalhar: `alt_letter` (default), `sobre_prefix`, `habilidade_n`, `arm_afirmacao`, `badge_rd`, `regra_vazia`, `structured_null`, `needs_qual`, `orfao_sem_andaime`. |
| `--export FILE` | Exporta os cards problemáticos para JSON. |
| `--tipo {all,elo_quebrado,armadilha}` | Filtra por tipo de card. |
| `--only-needs-qual` | Exporta **todos** os `needs_qualitative=1`, ignorando o filtro de sinais. |

⚰️ A heurística F7 (léxico de competidor) **foi revogada em 11/09/2026** — medição em
`AUDITORIA_MEDHUB.md §F7`. Não reintroduzir sem nova medição.

---

## Plano do Dia e fechamento

### `tools/day_plan.py` — o Plano do Dia (boot) e os blocos derivados

> **Assinatura canônica deste CLI.** `revisar.md` e `cronograma.md` o invocam e apontam para cá;
> a lista completa de flags vive aqui para não existir em dois lugares (§7.2). O **boot já roda**
> `day_plan.py` pelo hook `SessionStart` — `AGENTE.md §2 passo 4`: **não re-rodar** sem flag.

| Flag | Função |
|---|---|
| `--json` | Saída JSON crua do plano. |
| `--handoff-block` | **F6:** emite o bloco numérico *"Estado por frente"* derivado do db, pronto para colar no `HANDOFF.md`. É o que impede número digitado à mão de envelhecer — `AGENTE.md §3 passo 1`. |
| `--review-plan` | **F3:** clusters do dia (área/tema + contagem por bucket) derivados da fila real; com `--json`, o agregado cru. |
| `--difficulty AREA TEMA` | Nota inferida + degrau + propósito de um tema (**read-only**). É o insumo da calibração da Revisão Direcionada — ver `revisar.md`. |
| `--tempo H` | Horas disponíveis hoje (recomendador; o default usado sai declarado no output). |
| `--energia {alta,media,baixa}` | Energia do dia — modula a capacidade proposta. |
| `--no-persist` | Simulação: monta o plano **sem** gravar em `plano_dia`. |
| `--plano-de YYYY-MM-DD` | Imprime o plano **persistido** daquela data (JSON). |
| `--planilha` | **Reconcile W1** planilha × db, com a **idade** da planilha (read-only, nunca bloqueia); com `--json`, o dict cru. |
| `--aderencia` | Relatório de aderência **planejado × real** por dia, derivado do db. |
| `--semanas N` | Janela do `--aderencia` em semanas (default 1). |

🔴 O passo sugerido por `--difficulty` segue o contrato **v1.3**: `DRENAR` primeiro, ensino só na
**Revisão Direcionada de fechamento**. ⚰️ Até 11/09/2026 a string dizia *"PREPARAR ...; depois
DRENAR"* — sub-modo revogado na s170 que sobreviveu no código porque o gate `CONTRATO_REVOGADO` só
varria markdown (**F97**). `tools/day_plan.py` e `tools/dormant_refresh.py` agora estão na lista de
portadores do gate.

---

## Posição no cronograma

### `tools/preparacao.py` — posição SSOT da preparação (semana de conteúdo)

| Flag | Função |
|---|---|
| `--set-semana N` | Grava a semana de **conteúdo** atual. |
| `--show` | Exibe a posição registrada. |
| `--fonte FONTE` | Origem da atualização (default `operador`). |

`--set-semana` e `--show` são **mutuamente exclusivos e obrigatórios** (um dos dois). A distinção
que este CLI carrega: semana de **conteúdo** ≠ semana de **calendário** — o atraso entre as duas é
a posição real, e o derivador do cronograma é `tools/cronograma.py` (assinatura em `cronograma.md`).

⚰️ **`--set-semana` não move mais o boot (17/09/2026, `plano-ssot-e-cards-v2` Parte 4).** A posição do
Plano do Dia passou a ser a **semana do PLANO** (menor `semana_plano` com pendência em `plano_tarefas`),
e `day_plan._resolver_semana_conteudo`/`_semana_conteudo` foram removidos. A chave
`preparacao_estado.semana_conteudo` sobrevive com **um** leitor: `tools/cobertura_conhecimento.py`.
Gravar a posição aqui alimenta só esse check -- para mover a posição do boot, use
`python tools/plano.py --mover ID --semana N`. Norma: `cronograma-contract.md` v1.3.

### `tools/plano.py` -- o plano de estudo como DADO (`plano_tarefas`)

| Flag | Função |
|---|---|
| `--semear` | Semeia `plano_tarefas` das 3 fontes (extensivo, Reta Final pendente, custom). **Dry-run é o default.** |
| `--dry-run` | Explicita o default do `--semear`: mede, imprime o COUNT-ASSERT e **não grava**. |
| `--apply` | Grava. Exige `--expect N`. Mutuamente exclusivo com `--dry-run`. |
| `--expect N` | COUNT-ASSERT: N de linhas **NOVAS** esperadas. Difere do medido na hora -> **recusa (exit 2)** sem gravar nada. Na 2a execução o N correto é `0` (idempotência). |
| `--listar` | Lista a tabela (read-only). |
| `--semana N` | Filtro do `--listar`: semana do **plano** (não a da fonte). No `--mover`, é a semana de **destino**. |
| `--bloco {MFC,PED,CIR,GO,CM}` | Filtro do `--listar`: bloco de peso UERJ, **derivado** de `area` (`MFC`=Preventiva, `GO`=Ginecologia+Obstetrícia, `CM`=o resto). Não é coluna. |
| `--status {pendente,feita,cortada}` | Filtro do `--listar`. |
| `--fonte {extensivo,rf,custom}` | Filtro do `--listar`. |
| `--json` | Saída do `--listar` ou do `--pendencia-revisao` em JSON. |
| `--concluir ID` | Marca a tarefa como `feita`: grava `data_conclusao`, `sessao_bulk_id` e `origem_conclusao=usuario`. **Exige `--sessao`.** |
| `--sessao N` | **O `id` da linha em `sessoes_bulk`, não o `sessao_num`** (que se repete entre áreas). Sessão inexistente -> **recusa (exit 2)**; o output ecoa área/data/questões da sessão casada, que é como o id trocado se denuncia. |
| `--data AAAA-MM-DD` | Data de conclusão do `--concluir` (default: hoje). Formato diferente -> recusa. |
| `--cortar ID` | Tira a tarefa do plano (`status='cortada'`). **Exige `--motivo`.** |
| `--motivo "..."` | Por que a tarefa foi cortada. Vai **anexado** à `nota` (`corte: ...`), preservando as marcas da semeadura; corte repetido substitui o motivo anterior em vez de empilhar. |
| `--mover ID` | Regrava `semana_plano`/`ordem`. **Exige `--semana`.** Não toca em `status` nem em `origem_conclusao` -- mover é replanejar, não concluir. |
| `--ordem K` | Ordem dentro da semana no `--mover`. Omitida, **preserva** a ordem atual. |
| `--reabrir ID` | Volta a tarefa para `pendente` e **apaga** `data_conclusao`/`sessao_bulk_id` (o usuário acabou de negar aquela conclusão). |
| `--revisar-area AREA` | Lista de **conferência** da área (read-only), em blocos de <= 25 linhas: `id`, fonte + semana da fonte, status, origem, tipo, tema. Ordenada pela **fonte** (não pelo plano), que é a ordem do Dashboard/PDF contra o qual se confere. |
| `--confirmar-area AREA` | Revisão da área **em lote**. Dry-run por default; `--apply` exige `--expect N`. |
| `--feitas "1,4,9"` | Ids do `--confirmar-area` que estão **feitos**. |
| `--pendentes "2,3"` | Ids do `--confirmar-area` que estão **pendentes** (limpa o vínculo de conclusão de cada um). |
| `--pendencia-revisao` | Quantas linhas ainda têm `origem_conclusao=dashboard_2026-09-10`, **por área** (read-only), ordenado por peso de bloco UERJ. Zero = passada completa. |

As três fontes, todas versionadas em `core/cronograma/`: `grade_extensivo.json` (735 tarefas /
52 semanas, part-1) · `grade.json` (Reta Final -- entram só as **pendentes** de S17-S28) ·
`plano_custom.json` (editável à mão). O status inicial vem de `dashboard_snapshot.json`, snapshot
**congelado** do Drive (`origem_conclusao=dashboard_2026-09-10`) -- nunca se lê o Drive em runtime
(`cronograma-contract` Cláusula 5b).

🔴 **Semear nunca infere conclusão.** Nome que não casa entre o PDF e o Dashboard nasce `pendente`,
e o número de não-casados é impresso no dry-run. A `semana_plano` é decidida por duas funções
puras testadas (`ordenar_fase1`, para as 7 semanas até a prova da UERJ em 01/11, e `ordenar_fase2`,
para o extensivo S21-S48 a partir da semana 8) -- não por regra em JSON. Área fora de
`core/areas.json` é **recusada na porta** (F89); rótulo que a fonte não tem como resolver (o `Multi`
das tarefas de Radiologia) grava `area=NULL` **com a nota dizendo qual rótulo era**, que é dívida
declarada e não chute.

Escrita só por `app/utils/db.py` (`plano_upsert_tarefas`, `plano_set_status`, `plano_mover`,
`plano_confirmar_area`) -- o CLI é camada fina e não abre `sqlite3` próprio; leitura por
`plano_listar`, `plano_obter` e `plano_pendencia_revisao`. Idempotente por
`UNIQUE(fonte, ref_semana_fonte, tarefa_fonte)`: re-semear insere 0 e reescreve apenas
`CAMPOS_SEMEADOS` -- `status`, `data_conclusao`, `sessao_bulk_id` e `origem_conclusao` são
**progresso** e ficam fora do UPDATE. ⚠️ `nota` **está** em `CAMPOS_SEMEADOS`: o motivo de um
`--cortar` é reescrito por um `--semear --apply` futuro (o `status='cortada'` sobrevive) --
dívida declarada, o motivo é explicação e não o dado de controle.

**Exatamente UM modo por invocação** (`--semear` | `--listar` | `--concluir` | `--cortar` |
`--mover` | `--reabrir` | `--revisar-area` | `--confirmar-area` | `--pendencia-revisao`); dois
modos ligados -> `exit 2` nomeando os dois. Mutação de UMA linha grava direto: dry-run +
`--expect` são o rito da operação **em lote** (`--semear`, `--confirmar-area`), AGENTE.md §10.7.

🔴 **A revisão por área existe porque o status semeado é aproximado**: o usuário confessou marcar
tarefa no lugar de outra no Dashboard. O ciclo é `--revisar-area` (o agente lê os blocos com ele) ->
`--confirmar-area --dry-run` -> `--apply --expect N`, com `N` = **a área inteira**, porque a
conferência carimba `origem_conclusao=usuario` até em quem **não muda de status** -- a conferência
é a evidência, e é isso que faz o `--pendencia-revisao` chegar a zero. Id fora da área (ou
inexistente) derruba o lote **inteiro**, sem gravar nada. `--confirmar-area` é retro-confirmação:
não inventa `sessao_bulk_id` nem apaga o de um `--concluir` anterior.

🔴 **Semântica de `origem_conclusao` alargada na part-3**: até a part-2 ela só era escrita em linha
`feita`; agora responde *"quem afirmou este status"* em qualquer status (`usuario` vs.
`dashboard_2026-09-10`). É trilha de auditoria, não `status` -- uma linha pode continuar `feita` e
só trocar de origem, que é como "zero aproximadas" acontece sem reescrever histórico.

Specs `.vibeflow/specs/plano-ssot-e-cards-v2-part-2.md` (semeadura) e `-part-3.md` (progresso).

### `tools/listas.py` -- ledger de LISTAS de exercicios (`sessoes_bulk.tarefa_id`)

| Flag | Função |
|---|---|
| `--backfill` | Casa `sessoes_bulk.observacoes` com `plano_tarefas.tema` e grava o vínculo das sessões **inequívocas**. **Dry-run é o default.** |
| `--dry-run` | Explicita o default do `--backfill`: mede, imprime `N casadas / M ambíguas / K sem match` (com as três listas nominais) e **não grava**. |
| `--apply` | Grava. Exige `--expect N`. Mutuamente exclusivo com `--dry-run`. |
| `--expect N` | COUNT-ASSERT: N de sessões **casadas** esperadas. Difere do medido na hora -> **recusa (exit 2)** sem gravar nada. |
| `--progresso` | Por tarefa: `url_lista \| q_previstas \| feitas \| acertos \| %`, só das listas com sessão vinculada, com totais por bloco UERJ. Read-only. |
| `--pendentes` | As listas **previstas** que ainda não têm sessão vinculada (exclui `cortada`; marca a `feita` sem volume, que é dívida do status aproximado). Read-only. |
| `--bloco {MFC,PED,CIR,GO,CM}` | Filtro do `--progresso`/`--pendentes`: bloco de peso UERJ, **derivado** de `area` (não é coluna). |
| `--semana N` | Filtro do `--progresso`/`--pendentes`: semana do **plano**. |
| `--json` | Saída do `--progresso` ou do `--pendentes` em JSON. |

🔴 **O backfill nunca chuta.** O casamento é por normalização (casefold + sem acento, a mesma
`plano.normalizar`) e **substring exata do tema** dentro da observação, delimitada por fronteira de
palavra -- sem fuzzy, sem stemming, sem "melhor candidata". A s183 mediu 54/735 nomes divergentes
entre as fontes: fuzzy compraria falso vínculo em tema homônimo (Pneumonias na Infância x Pneumonias
Bacterianas). **2+ candidatas = ambígua**, fica `NULL` e sai na lista para o humano decidir com
`registrar_sessao_bulk.py --vincular ID --tarefa ID`. Sessão de `area='Simulado'` é **termômetro**:
não entra no casamento e é reportada à parte. Tema bundlado ("A; B") é casado inteiro, nunca por
partes -- limite declarado, não maquiado.

`feitas`/`acertos` são **sempre** derivados de `sessoes_bulk` (SSOT volumétrica, `AGENTE.md §6`);
`plano_tarefas` não carrega contagem própria, e o vínculo **não conclui** tarefa nenhuma (concluir é
`plano.py --concluir`). Os dois modos de leitura fecham com o delta contra o **orçamento da Fase 1**
(2.760 questões, semanas 1-7, `history/session_183.md §3`), medido sempre sobre o plano **inteiro** e
nunca sobre o recorte dos filtros; o `--progresso` reporta ainda o volume que ficou **sem lista**,
para que nenhuma questão suma do relatório.

Escrita só por `app/utils/db.py` (`vincular_sessao_tarefa`, o único writer de `sessoes_bulk.tarefa_id`)
-- o CLI não abre `sqlite3` próprio e não tem escrita própria; leitura por `plano_listar` e
`sessoes_bulk_listar`. Spec `.vibeflow/specs/plano-ssot-e-cards-v2-part-6.md`.

### `tools/fsrs_optimize.py` -- parâmetros pessoais do FSRS (R1, **read-only**)

| Flag | Função |
|---|---|
| `--write` | Grava `core/fsrs_params.json`. **Nunca** escreve no `ipub.db` (conexão `mode=ro`). |
| `--dry-run` | **(default)** imprime sem gravar; vence `--write` se os dois vierem juntos. |
| `--holdout F` | Fração final do revlog reservada para a métrica de hold-out (default `0.2`). |
| `--duracao-ms N` | `review_duration` sintético em ms (default `16500`): o schema não grava duração e o `compute_optimal_retention` a exige. |
| `--leech` | **R7:** painel de leech (cards com `lapses >= N` + distribuição de `difficulty`) **x2** -- contagem crua e sob o remap. Não roda o Optimizer. |
| `--limiar-lapsos N` | Limiar de lapsos do painel `--leech` (default `3`). |

Roda o `Optimizer` do py-fsrs sobre **duas visões do mesmo revlog**: **cru** (notas como
gravadas) e **remap** (`2 -> 1`, `3 -> 2`, `4 -> 3`, derivado da régua literal do passo 4 do
`/revisar`). O remap existe porque a perda do Optimizer é binária Again x não-Again
(`optimizer.py:86`) e a nota 2 do MedHub -- "recall parcial sem o alvo" -- entraria como acerto
(**F112**). 🔴 O remap acontece **só na entrada do Optimizer**: o `fsrs_revlog` é imutável e o
mapa aplicado viaja como `metadata` no JSON. Parâmetros e retenção ótima são **REPORTADOS,
nunca adotados** -- `app/utils/fsrs.py` não lê o arquivo; adotar é o item **R2** da fila e é
decisão do operador.
