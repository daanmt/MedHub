---
description: "⚰️ REVOGADA em 18/09/2026 (part-8): o Drive deixou de ser fonte de plano e progresso -- NÃO importar planilha, não pedir download. Sobrevivem só a tabela de investimento/mês (input do /performance) e o CLI importar_sessoes.py (--snapshot, --abandonada). Plano e progresso: plano.py, listas.py, painel.py."
type: skill
layer: commands
status: canonical
---

# ⚰️ Skill: Importar Planilha — **O DRIVE DEIXOU DE SER FONTE (18/09/2026)**

> **Não importar plano nem progresso do Google Drive. Não pedir ao usuário para baixar,
> preencher ou riscar planilha.** Decisão do operador em 16/09/2026, perguntado direto:
> *"Sim, banco é a fonte"*. Executada no **part-8** do PRD `plano-ssot-e-cards-v2`.

**O que esta skill descrevia e não vale mais:** o ritual de ler o `Dashboard EMED 2026` e o
`Cronograma de Reta Final.xlsx` via Google Drive MCP para saber o que estava feito, em que ordem e
quanto volume havia. As seções *Pré-requisito: Google Drive MCP*, *Planilhas canônicas*,
*Estrutura mapeada* (Dashboard e Cronograma de Reta Final) e *Fluxo* saíram no mesmo commit — o
conteúdo vive no git e em `history/session_113.md`.

**Quem responde hoje pelo que elas respondiam:**

| pergunta | portador de hoje |
|---|---|
| o que vem agora, em que ordem | `tools/plano.py --listar` (`plano_tarefas`; ordem é coluna) |
| o que já foi feito | `plano_tarefas.status`, por `plano.py --concluir ID --sessao N` |
| quanto volume por lista | `tools/listas.py --progresso` (`sessoes_bulk.tarefa_id`) |
| a visão consolidada de progresso | `tools/painel.py --html` — substituiu as 20 tabelas do Dashboard |

**O que SOBREVIVE aqui, e só isso:**

1. **A tabela de investimento/mês** — dado manual do operador, sem outra fonte, e alimenta o
   custo/questão do `/performance` (`performance.METAS_MENSAIS`). Continua sendo digitada à mão.
2. **O CLI `importar_sessoes.py`** — `--snapshot`/`--show-snapshot` (que alimentam o W1) e
   sobretudo **`--abandonada`**, o mecanismo que declarou este abandono. O `--rows-file` continua
   existindo para um lote pontual vindo de qualquer lugar; deixou de ser ritual de Drive.

🔴 **O W1 do reconcile não foi desligado — foi SUSPENSO.** `python tools/day_plan.py --planilha`
passa a imprimir *"comparação suspensa"* preservando o último delta medido (**+977**: planilha
6.349 x db 7.326, em 16/09). Nenhum check some — ele muda de estado (padrão `warn-first-check`).
Se o operador voltar a alimentar a planilha, um `--snapshot` novo a reativa.

**Os arquivos no Drive não foram tocados** — ficam lá, congelados, como histórico dele.

---

## Contrato do CLI (`importar_sessoes.py`)

```bash
python tools/importar_sessoes.py --rows-file <path.json>
python tools/importar_sessoes.py --snapshot [--total N] [--por-area '{"Pediatria": 512}'|@abas.json] --ultimo-lancamento AAAA-MM-DD
python tools/importar_sessoes.py --show-snapshot
python tools/importar_sessoes.py --abandonada "<motivo>"
```

**Importação de volume:**
- `--rows-file`: JSON com lista de linhas no shape acima (UTF-8).
- Reusa `registrar()` — mesma idempotência e validação do registro manual.
- Não aborta o lote em linha inválida: reporta e segue.

**Snapshot da planilha (alimenta o reconcile W1; não importa volume):**
- `--snapshot`: grava `preparacao_estado.planilha_snapshot`. Exige `--ultimo-lancamento`.
- `--por-area`: somas das **abas por disciplina**, inline ou `@arquivo.json`. Quando presente, o `--total` é derivado da soma.
- `--total`: total declarado. Junto com `--por-area`, é **conferido** contra a soma — divergência é recusada com os dois números na mensagem (é o bug de fórmula do Quadro Geral, s075). Sozinho, grava sem detalhe por área e o boot declara que o mislabel de área **não foi verificado**.
- `--ultimo-lancamento AAAA-MM-DD`: data da última tarefa lançada **dentro** da planilha — é a *idade* dela, e responde "a planilha ainda é alimentada?". Data no futuro é recusada. Distinta de `lido_em` (idade da nossa cópia), gravada sozinha.
- `--show-snapshot`: imprime o snapshot gravado (JSON).
- `--abandonada "<motivo>"`: registra a resposta do operador a *"a planilha ainda é fonte?"*. O boot para de cobrar e passa a dizer **comparação suspensa**, preservando o último delta medido — muda o peso, não o mecanismo.
- Leitura do reconcile: `python tools/day_plan.py --planilha` (read-only, nunca bloqueia).

---

## Notas

- **Persistência canônica** continua em `sessoes_bulk` via `registrar()`. Este fluxo não cria caminho de dados paralelo.
- **Áreas válidas** são a fonte de verdade do vocabulário; normalizar sempre antes de gravar.
- Para registro pontual (uma sessão só, sem planilha), usar `tools/registrar_sessao_bulk.py` direto (ver `AGENTE.md` decisão "SSOT volumétrica").

---

## Assinatura canônica — `tools/registrar_sessao_bulk.py`

> **Portador canônico deste CLI** (`AGENTE.md §7.2`). É o **writer da SSOT volumétrica**
> (`sessoes_bulk`): ao ouvir *"fiz X questões, acertei Y"*, o agente chama isto **antes** de
> processar erros individuais. O `importar_sessoes.py` (lote a partir da planilha) é uma camada
> por cima deste writer, não um segundo caminho de escrita.

| Flag | Função |
|---|---|
| `--sessao N` | Número da sessão (ex.: 67). |
| `--area AREA` | Área clínica. Válidas: **`core/areas.json`** via `app/utils/areas.py` (F89) — writer **recusa** área fora da lista, com o palpite mais próximo. |
| `--feitas N` | Total de questões feitas. |
| `--acertos N` | Total de acertos. Validado: `acertos <= feitas`. |
| `--data YYYY-MM-DD` | Data da sessão (default: hoje). 🔴 Quando o estudo e o registro caem em dias diferentes, informar a data **do estudo**. |
| `--obs "..."` | Observação livre (ex.: *"Bloco ATLS"*). |
| `--acumular` | **F22:** soma este bloco a um registro existente da mesma `(sessao, area)` em vez de recusar — é o 2º bloco do mesmo dia, não uma duplicata. |
| `--semana N` | Atualiza no mesmo ato a **posição SSOT** (semana de conteúdo) — ver `preparacao.py` em `engenharia-cli.md`. |
| `--tarefa ID` | **P6:** grava o **vínculo** com a lista do plano (`plano_tarefas.id`) no ato da inserção. Opcional; **só adiciona o elo** — idempotência, validação de área e o fan-out de taxonomia continuam idênticos. |
| `--vincular SESSAO_ID` | **P6:** vincula uma sessão **já registrada** (o `id` da LINHA em `sessoes_bulk`, nunca o `sessao_num`) à `--tarefa ID`. Não registra volume nenhum — é o conserto de um registro antigo ou de uma ambígua do backfill. |

🔴 **Gate do vínculo (P6):** `plano_tarefas.area` tem de ser **igual** a `sessoes_bulk.area`, e tarefa
com `area` NULL (o `Multi` declarado da part-2) é **recusada** — sem área não há o que conferir. No
caminho do `--tarefa` o gate roda **antes** de qualquer escrita: área divergente não deixa a sessão
gravada com o vínculo recusado (meia operação é a metade que ninguém vê). O vínculo **não conclui**
a tarefa — concluir é `plano.py --concluir`, decisão do usuário/agente. Escrita única:
`db.vincular_sessao_tarefa`. Leitura do ledger e backfill em massa: `tools/listas.py`
(`engenharia-cli.md`). Spec `.vibeflow/specs/plano-ssot-e-cards-v2-part-6.md`.
- O read da planilha é responsabilidade do agente via MCP; o código nunca lê o Drive sozinho.
