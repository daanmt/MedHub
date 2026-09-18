---
type: contract
layer: core
status: canonical
version: 1.4
relates_to: [estado-contract, handoff-contract, fsrs-management-contract, AGENTE]
---

# Contrato de Reconciliação (Reconcile Mode)
**Versão 1.4 | 2026-09-17 (plano-ssot-e-cards-v2 Parte 4) · v1.3 2026-09-10 (B3/F35) · v1.2 2026-09-01 (ciclo descolar) · v1.0 2026-06-03 (sessão 075) — adaptado do Reconcile Mode de `agente-daktus-content/core/contracts/handoff-contract.md`**

> Documento normativo. Define o protocolo de detecção e resolução de *drift* de estado no boot.
> Referenciado por: `AGENTE.md` (§2 boot), `estado-contract.md`, `handoff-contract.md`, `fsrs-management-contract.md`.

---

## Papel

O MedHub tem **quatro superfícies de estado que podem divergir**: a planilha do Drive (SSOT de volume), o `ipub.db` (`sessoes_bulk`/FSRS), o `ESTADO.md` (snapshot macro) e o `HANDOFF.md` (operacional). Este contrato define um **check de boot** que detecta divergências **antes** de qualquer trabalho — formalizando o que foi feito manualmente na sessão 075 (conciliação planilha↔db que achou 40q de delta + 2 áreas mal-rotuladas).

---

## Check de boot (rodar no início de toda sessão de estudo)

Leitura rápida, read-only. Reporta divergências; não grava sem confirmação.

> **Matriz condição→instrumento (v1.2, 2026-09-01 — F56):** a coluna "enforcement REAL" diz a
> VERDADE por linha. Linha `SEM IMPLEMENTAÇÃO` é prosa-declarada (checagem manual no boot),
> nunca promessa de check automático — um contrato que afirma BLOCKING sem instrumento treina
> o operador a ignorar o boot.

| # | Condição | Tipo declarado | Enforcement REAL |
|---|---|---|---|
| **B1** | `HANDOFF.md` > 60 linhas | BLOCKING | ✅ **BLOCK** — `auto_check::check_handoff_len`, `[BLOCK] HANDOFF_LONGO` |
| **B2** | Ponteiro do HANDOFF aponta `sessão NNN` sem `history/session_NNN.md` (exceção: NNN = max+1, a sessão em curso) OU além de max+1 | BLOCKING | ✅ **BLOCK** — `state_utils::check_session_pointer`, `[BLOCK] SESSION_POINTER` (promovida 2026-09-01; era WARN de condição aparentada) |
| **B3** | "Estado por frente" do HANDOFF contradiz o `ESTADO.md` | BLOCKING | ⚠️ **SEM IMPLEMENTAÇÃO** — cross-check manual no boot |
| **B4** | Indicador do `ESTADO.md` diverge do total de `sessoes_bulk` | BLOCKING | ⚠️ **SEM IMPLEMENTAÇÃO** — `/performance` vs ESTADO, manual |
| **W1** | Planilha Dashboard (somas das **abas por disciplina**) diverge de `sessoes_bulk` | WARNING | ✅ **REPORTA** (B3/F35, s176) — `day_plan.reconcile_planilha` emite a linha no Plano do Dia e `python tools/day_plan.py --planilha` sob demanda; nunca o Quadro Geral |
| **W2** | `history/session_NNN.md` existe mas não está no `history/INDEX.md` | WARNING | ⚠️ **SEM IMPLEMENTAÇÃO** — conferência manual |
| **W3** | Backlog FSRS (`state=0`) cresceu sem drenagem há N sessões | WARNING | ⚠️ manual — `fsrs-management-contract.md`; visível no day_plan |
| **W4** | Áreas em `sessoes_bulk` fora de `AREAS_VALIDAS` | WARNING | ⚠️ **SEM IMPLEMENTAÇÃO** — vocabulário (ver s075: `GO`, `Obstetricia`) |
| **W5** | `grade.json` defasado vs `Cronograma.pdf` (sha256 difere) | WARNING | `python tools/cronograma.py --check` |
| **W5b** | `grade_extensivo.json` defasado vs `[52 wk] Cronograma Extensivo.pdf` (sha256 difere) — é a fonte da **semeadura** de `plano_tarefas` | WARNING | `python tools/cronograma.py --check-extensivo` -> `fresh\|stale\|missing\|missing_pdf` |
| **W6** | "Próxima = SNN" (semana de conteúdo) no HANDOFF/ESTADO desatualizada vs o trabalho real | WARNING | ponteiro textual vs últimas sessões |
| **W7** | Gap de meta materializado (`acum + cronograma restante < meta`) — **fork estratégico, reporta UMA vez** | WARNING | `python tools/cronograma.py --gap` |
| ⚰️ **W8** | ~~Fronteira real do cronograma desconhecida (conclusão pelo `Realizada?` do Dashboard / ordem pelo xlsx sem snapshot fresco)~~ — **REVOGADA em 17/09/2026** (v1.4): a fronteira deixou de ser desconhecida porque virou coluna (`plano_tarefas.status`/`origem_conclusao`) | — | ⚰️ morta com `day_plan.cron.conclusao_desatualizada` e o snapshot `cronograma_conclusao_drive` (Parte 4) |

**BLOCKING** → resolver antes de iniciar trabalho novo. **WARNING** → reportar; trabalho pode seguir.
> **B1 é trava técnica, não exortação (spec `consolidacao-part-4`).** A condição existia em prosa desde a s075 e foi violada sem consequência — o HANDOFF passou de 60 linhas e nada bloqueou (achado **D3**/s144: *warning-first virou warning-only*). Agora `auto_check` (modos `--all`, `--staged`, `--changed` com `HANDOFF.md` no diff) sai com exit 1. **Conserto canônico:** migrar o excedente narrativo para `history/session_NNN.md` — nada se perde, muda de endereço. Teto = 60 linhas físicas; 60 passa, 61 bloqueia (`tools/test_handoff_teto.py`).
> **Cronograma (W5-W7, W5b) nunca é BLOCKING:** plano não é verdade-de-estado; estar atrasado é *informação de gestão*, não corrupção (`cronograma-contract.md`). **W5b nasce WARN** pelo padrão `warn-first-check`: regra nova adverte, e só vira BLOCK quando a base zerar.

---

## Resolução

```
PASSO 1 — Diagnóstico (não alterar nada)
  → Listar condições presentes. Registrar: "Boot em reconcile; BLOCKINGs: [...]".

PASSO 2 — Resolver BLOCKING
  → B1: trimmar HANDOFF para ≤ 60 linhas (mover excedente para history/).
  → B2: criar history/session_NNN.md reconstituída (marcar "reconstituída").
  → B3/B4: alinhar HANDOFF/ESTADO ao estado real (preferir o db/repositório).

PASSO 3 — Resolver WARNING (se houver)
  → W1: o boot JÁ reporta (day_plan). Ler o estado nomeado e agir pelo que ele diz:
       `nao_medido`      -> ler a planilha via MCP e gravar o snapshot:
                            tools/importar_sessoes.py --snapshot --por-area @abas.json
                            --ultimo-lancamento AAAA-MM-DD
       `import_pendente` -> planilha à frente: importar o delta via --rows-file (com confirmação).
       `divergente_por_area` / `divergente` -> conciliar aba a aba (assinatura de mislabel, s110).
       `planilha_atrasada` / `sem_detalhe_area` / `alinhado` -> informar; nada a fazer.
       `abandonada`      -> declarado pelo operador; segue reportando, suspenso.
  → W2: adicionar entry no history/INDEX.md.
  → W3: agendar onda de drenagem (ver fsrs-management-contract.md).
  → W4: normalizar rótulos (migração one-shot em tools/, nunca SQL direto inline).
  → W5: python tools/cronograma.py --rebuild (regenera o cache; grade.json é derivado do PDF).
  → W5b: python tools/cronograma.py --rebuild-extensivo (mesmo espírito; falha dura em
       735 tarefas / 52 semanas, `--expect-tasks N` só quando o PDF do EMED mudou de
       verdade). `missing_pdf` = o PDF (IP, gitignored) não está na raiz nem em data/:
       informar e seguir -- a semeadura do plano já foi feita, o WARN é sobre re-semear.
  → W6: atualizar a posição. ⚰️ *Era "o ponteiro textual `Próxima = SNN` no HANDOFF/ESTADO
       (único write da feature de cronograma)"* -- as duas metades morreram em 17/09/2026:
       `day_plan` não lê mais ponteiro textual (a posição é a semana do PLANO, derivada por
       `--handoff-block`) e o write da feature deixou de ser único (`plano_tarefas`,
       `cronograma-contract` v1.3, Cláusula 5). Conserto: `python tools/day_plan.py
       --handoff-block` e colar; divergência é medida por `POSICAO_DRIFT`.
  → W7: reportar UMA vez; registrar a decisão do usuário em ESTADO §Metas; silenciar até a premissa mudar.
       🔴 Resolução de W5-W7 NÃO grava no db (cronograma-contract.md, Cláusula 5).
  ⚰️ W8: REVOGADA em 17/09/2026 (v1.4) -- NAO executar, NAO restaurar.
       ⚰️ Era (morto): "DOIS sinais, DOIS caminhos" -- conclusao lida da coluna `Realizada?` do
       Dashboard EMED pelo agente, e ordem vinda do xlsx local pelo ritual do usuario
       (`cronograma.py --sync-drive`). Morreu porque a pergunta que ela fazia ("qual e a
       fronteira real do cronograma?") deixou de ser desconhecida: a conclusao virou
       `plano_tarefas.status` + `origem_conclusao`, e a ordem virou `semana_plano`/`ordem`,
       ambas editaveis por comando (`tools/plano.py --concluir|--cortar|--mover`).
       O que SOBREVIVE, promovido a regra geral fora da W8: (i) nenhum passo de boot pode
       exigir binario via MCP -- se a leitura precisa de bytes, ela nao e do agente; e
       (ii) caveat honesto no lugar de obrigacao impossivel. A divida que restou tem outro
       nome e outro instrumento: `python tools/plano.py --pendencia-revisao` conta as
       tarefas ainda carimbadas `dashboard_2026-09-10` (status APROXIMADO por confissao
       do usuario), e o boot emite UMA linha enquanto o numero nao zerar.
       Norma: `cronograma-contract.md` v1.3; PRD `plano-ssot-e-cards-v2`, Parte 4.

PASSO 4 — Saída
  → Condição: HANDOFF ≤ 60 linhas + header com session em history/ + HANDOFF ⟷ ESTADO ⟷ db consistentes.
  → Commitar a reconciliação como commit separado, antes do trabalho da sessão.
```

**Arquivos alteráveis no Reconcile:** `HANDOFF.md`, `ESTADO.md`, `history/`, `history/INDEX.md`, `ipub.db` (via CLIs/migração), `core/cronograma/grade.json` (cache regenerável via `--rebuild`). **Não alterar** em reconcile: `resumos/`, `skills/`, `.claude/commands/`, `Cronograma.pdf` (SSOT).

---

## Absorção de dados de performance (planilha → db)

A planilha do Drive (`Dashboard EMED 2026`) é o **SSOT de volume** e a fonte **mais fresca**: o usuário a preenche **logo após cada estudo** (lê o tema + faz exercícios), registrando as questões/performance nas linhas de tarefa do dashboard e **riscando / mudando a cor do tema no cronograma** ao concluí-lo. Consequências para o reconcile:

- **A planilha geralmente já reflete o trabalho.** Quando o usuário diz "registrei / concluí X", o esperado é **delta = 0** vs o db se já tiver sido importado nesta sessão — confirmar, não duplicar. Se o db ainda não tem, importar o delta.
- **Abas por disciplina são autoritativas.** **W1 reconcilia contra a soma das abas por disciplina** (que não dependem de fórmula de agregação), não contra o Quadro Geral. O Quadro Geral teve **um** bug de fórmula confirmado (Obstetrícia somava acertos em vez de questões — corrigido pelo usuário em s075).
- ⚠️ **Falso-positivo por delay de leitura:** a leitura via MCP (content snippet / read) pode **atrasar vs a edição ao vivo** do Google. Em s075 o QG do Infecto pareceu não somar (177 vs 217 da aba), mas era **delay de propagação** — minutos depois mostrava 217. **Re-checar após alguns minutos antes de concluir que é bug de fórmula.** Não alertar o usuário sobre "bug" sem reconfirmar.
- ⚰️ **Sinal de conclusão de tema — REVOGADO em 17/09/2026 (v1.4).** *Era: "a conclusão é lida da coluna `Realizada?` do `Dashboard EMED 2026` via `read_file_content`; o xlsx riscado fica como ritual local do usuário (`cronograma.py --sync-drive`), único portador da ordem".* Morreu com a W8: conclusão e ordem são colunas de `plano_tarefas`, declaradas pelo usuário por comando (`tools/plano.py --concluir|--cortar|--mover|--confirmar-area`). O `Realizada?` do Dashboard de 10/09 sobrevive só como **status inicial APROXIMADO** já semeado (`origem_conclusao = dashboard_2026-09-10`), que a passada de revisão por área existe para zerar — nunca como leitura recorrente de boot.
- **Delta, não total:** a planilha guarda acumulados por tarefa; importar só `(soma da aba) − (total no db)` por área — via `/importar-planilha` → `tools/importar_sessoes.py`.
- 🔴 **O reconcile W1 deixou de depender de alguém lembrar (v1.3, B3/F35).** O momento em que o agente lê a planilha é o único em que os números dela existem: ali ele grava o **snapshot** (`preparacao_estado.planilha_snapshot` via `importar_sessoes.py --snapshot`) com `por_area`, `total` e `ultimo_lancamento`. O boot compara e emite **uma linha, sempre** — inclusive `NAO MEDIDO` quando não há snapshot. **Duas idades, duas perguntas:** `ultimo_lancamento` responde *"a planilha ainda é alimentada?"*; `lido_em` responde *"minha cópia dela é velha?"*. **Total batendo não é alinhado:** na s110, 3 dos 4 achados foram mislabel de área e o relabeling não mudou o total — por isso `alinhado` exige detalhe por aba e, sem ele, o estado é `sem_detalhe_area` (declara o que não foi verificado, §10.8 do `AGENTE.md`). **Ponto cego declarado:** quem alimenta o snapshot é o agente; a validação é de coerência interna (soma das abas × total declarado, datas no passado), nunca de fidelidade ao Drive — enquanto o F36 não tiver transporte próprio, essa fidelidade fica **não verificável**.
- **Usuário relata "fiz X, acertei Y" (sem ter lançado na planilha ainda):** `tools/registrar_sessao_bulk.py` ANTES de processar erros (decisão "SSOT volumétrica" em `AGENTE.md §6`). O usuário tipicamente lança na planilha em paralelo — conciliar, não somar em dobro.
- **Cronograma (v1.4):** o plano de estudo persiste no db em **`plano_tarefas`** (`cronograma-contract.md` Cláusula 5) — semeado das três fontes e editado por `tools/plano.py`. ⚰️ *Era: "a planilha `Cronograma de Reta Final.xlsx` NÃO persiste no db — leitura sob demanda ... o agente lê conclusão pelo `Realizada?` do Dashboard (Cláusula 5b)".* A Cláusula 5b foi revogada; o xlsx segue fora do db e agora também fora do boot.

---

## Changelog

- **v1.4 (2026-09-17, s185 -- PRD `plano-ssot-e-cards-v2`, Parte 4):** ⚰️ **W8 REVOGADA.** A
  condicao perguntava "qual e a fronteira real do cronograma?" e a resposta virou coluna:
  conclusao = `plano_tarefas.status`/`origem_conclusao`, ordem = `semana_plano`/`ordem`, ambas
  editaveis por `tools/plano.py`. Com ela morreram `day_plan._conclusao_drive`,
  `_ordenar_por_drive`, o ramo calendario de `_cronograma_hoje` e o banner `Drive
  desatualizado`. Sobrevivem como regra GERAL (fora da W8): nenhum passo de boot exige binario
  via MCP, e caveat honesto no lugar de obrigacao impossivel. A divida que restou tem nome e
  instrumento proprios -- `plano.py --pendencia-revisao`, UMA linha no boot ate zerar.
  **W5b nova (WARN, `warn-first-check`):** `grade_extensivo.json` defasado vs o PDF de 52
  semanas (`cronograma.py --check-extensivo`) -- e a fonte da semeadura do plano, e ate aqui
  ninguem media o frescor dela. **W6 lapidada pela metade:** o ponteiro textual `Próxima = SNN`
  deixou de ser lido e o write da feature deixou de ser unico. Os tres passos da revogacao
  (AGENTE §10.10) no mesmo commit: declarado aqui + em `cronograma-contract` v1.3, lapidado em
  [`/cronograma`](../../.claude/commands/cronograma.md), termos cadastrados em
  `docs/MEMORIA-AUDITORIA.md §12`.
- **v1.3 (2026-09-10, s176 -- item 0.5 do Tier 0, B3/F35):** **W1 deixou de ser manual.** A matriz
  troca `manual` pelo instrumento real (`day_plan.reconcile_planilha` + `--planilha`), o PASSO 3
  ganha a acao por estado nomeado, e a secao de absorcao normatiza o **snapshot da planilha**
  (`preparacao_estado.planilha_snapshot`, gravado por `importar_sessoes.py --snapshot`). O achado
  que motivou: os dois unicos reconciles da historia do projeto (s075, s110) viraram script
  one-shot em `tools/_archive/migrations/`, e o drift de 76q da s110 foi achado **pelo operador**.
  Fronteiras declaradas: nao bloqueia, nao le o Drive, e a fidelidade do snapshot ao Drive segue
  **nao verificavel** enquanto o F36 nao tiver transporte proprio.

- **v1.2 (2026-09-01, ciclo descolar/ai-eng — F56):** **B2 promovida a BLOCKING de fato**
  (`state_utils::check_session_pointer` agora checa a condição CERTA — arquivo do ponteiro
  existe, com a exceção max+1 da sessão em curso — e o `auto_check` sai exit 1; era WARN de
  condição aparentada `>max+1`, com `success=True` fixo). **Matriz condição→instrumento**
  substitui a coluna "Como checar": cada linha declara o enforcement REAL (`BLOCK`/`manual`/
  `SEM IMPLEMENTAÇÃO`) — o changelog v1.1 declarou o rebaixamento consertado e consertou só
  a B1; a mentira estrutural (contrato afirma o que o código não faz) morre aqui. Sensor novo
  `NEEDS_QUALITATIVE_ATIVO` (WARN) cobre o invariante do contrato FSRS (F52b).
- **v1.1 (2026-08-14, s144):** **B1 promovida a BLOCKING de fato** — *a metade desta entrada sobre a W8 e o Drive está ⚰️ revogada desde 18/09/2026 (Parte 8); fica como registro:* (`tools/auto_check.py::check_handoff_len`, check 10 — era prosa desde a s075 e foi violada sem consequência: achado D3). **W8 reescrita** com o modelo de dois sinais: conclusão pelo `Realizada?` do Dashboard EMED 2026 (Sheets nativo, `read_file_content`, texto puro, agente executa) × ordem pelo xlsx local (ritual do usuário, `--sync-drive`, sem MCP); proibido exigir binário via MCP em passo de boot; caveat honesto quando faltar. Spec `.vibeflow/specs/consolidacao-part-4.md`.
- **v1.0 (2026-06-03, s075):** primeira instância; adaptado do Reconcile Mode do `agente-daktus-content`.
