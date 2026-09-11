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
