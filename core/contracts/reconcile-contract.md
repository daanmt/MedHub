---
type: contract
layer: core
status: canonical
version: 1.2
relates_to: [estado-contract, handoff-contract, fsrs-management-contract, AGENTE]
---

# Contrato de Reconciliação (Reconcile Mode)
**Versão 1.2 | 2026-09-01 (ciclo descolar) · v1.0 2026-06-03 (sessão 075) — adaptado do Reconcile Mode de `agente-daktus-content/core/contracts/handoff-contract.md`**

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
| **W1** | Planilha Dashboard (somas das **abas por disciplina**) diverge de `sessoes_bulk` | WARNING | ⚠️ manual — `/importar-planilha` (verificar); nunca o Quadro Geral |
| **W2** | `history/session_NNN.md` existe mas não está no `history/INDEX.md` | WARNING | ⚠️ **SEM IMPLEMENTAÇÃO** — conferência manual |
| **W3** | Backlog FSRS (`state=0`) cresceu sem drenagem há N sessões | WARNING | ⚠️ manual — `fsrs-management-contract.md`; visível no day_plan |
| **W4** | Áreas em `sessoes_bulk` fora de `AREAS_VALIDAS` | WARNING | ⚠️ **SEM IMPLEMENTAÇÃO** — vocabulário (ver s075: `GO`, `Obstetricia`) |
| **W5** | `grade.json` defasado vs `Cronograma.pdf` (sha256 difere) | WARNING | `python tools/cronograma.py --check` |
| **W6** | "Próxima = SNN" (semana de conteúdo) no HANDOFF/ESTADO desatualizada vs o trabalho real | WARNING | ponteiro textual vs últimas sessões |
| **W7** | Gap de meta materializado (`acum + cronograma restante < meta`) — **fork estratégico, reporta UMA vez** | WARNING | `python tools/cronograma.py --gap` |
| **W8** | Fronteira real do cronograma desconhecida — **conclusão** (coluna `Realizada?` do Dashboard) não lida hoje, e/ou **ordem** (xlsx reordenado à mão) sem snapshot fresco | WARNING (nunca BLOCKING) | `day_plan.py`/`cron.conclusao_desatualizada` — snapshot `preparacao_estado.cronograma_conclusao_drive` ausente, de dia-calendário anterior, ou sem `ordem` |

**BLOCKING** → resolver antes de iniciar trabalho novo. **WARNING** → reportar; trabalho pode seguir.
> **B1 é trava técnica, não exortação (spec `consolidacao-part-4`).** A condição existia em prosa desde a s075 e foi violada sem consequência — o HANDOFF passou de 60 linhas e nada bloqueou (achado **D3**/s144: *warning-first virou warning-only*). Agora `auto_check` (modos `--all`, `--staged`, `--changed` com `HANDOFF.md` no diff) sai com exit 1. **Conserto canônico:** migrar o excedente narrativo para `history/session_NNN.md` — nada se perde, muda de endereço. Teto = 60 linhas físicas; 60 passa, 61 bloqueia (`tools/test_handoff_teto.py`).
> **Cronograma (W5-W7) nunca é BLOCKING:** plano não é verdade-de-estado; estar atrasado é *informação de gestão*, não corrupção (`cronograma-contract.md`).

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
  → W1: rodar a conciliação planilha↔db; importar delta via tools/importar_sessoes.py (com confirmação).
  → W2: adicionar entry no history/INDEX.md.
  → W3: agendar onda de drenagem (ver fsrs-management-contract.md).
  → W4: normalizar rótulos (migração one-shot em tools/, nunca SQL direto inline).
  → W5: python tools/cronograma.py --rebuild (regenera o cache; grade.json é derivado do PDF).
  → W6: atualizar o ponteiro textual "Próxima = SNN" no HANDOFF/ESTADO (único write da feature de cronograma).
  → W7: reportar UMA vez; registrar a decisão do usuário em ESTADO §Metas; silenciar até a premissa mudar.
       🔴 Resolução de W5-W7 NÃO grava no db (cronograma-contract.md, Cláusula 5).
  → W8: DOIS sinais, DOIS caminhos (nunca um só passo, nunca binário via MCP):
       (a) CONCLUSÃO — ler a planilha "Dashboard EMED 2026" (Google Sheets NATIVO,
           fileId em `.claude/commands/importar-planilha.md:32`) via MCP `read_file_content`:
           volta TEXTO puro (tabelas markdown), a coluna `Realizada?` já diz tarefa a tarefa
           o que foi feito. Barato, 1x por dia-calendário. É a ação que o agente PODE fazer.
       (b) ORDEM — a reordenação manual só existe no `Cronograma de Reta Final.xlsx` (binário,
           sem substituto textual). É RITUAL DO USUÁRIO: ele tem o arquivo local e roda
           `python tools/cronograma.py --sync-drive <path-local>`. O agente pode PEDIR; não executa.
       Sem (b) fresco -> apresentar os `próximos temas` COM caveat explícito ("ordem pode
       estar desatualizada"), nunca em silêncio. Sem (a) -> caveat de conclusão. Nunca BLOCKING.
       🔴 PROIBIDO: baixar binário do Drive via MCP para satisfazer este check. `read_file_content`
       devolve base64 em xlsx e `--sync-drive` exige o arquivo real — o caminho não fecha, e
       tentá-lo foi o que produziu o boot de ~15 chamadas da s144 (D5).

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
- **Sinal de conclusão de tema (v1.1 — caminho trocado):** a conclusão é lida da coluna **`Realizada?`** do `Dashboard EMED 2026` (Sheets nativo) via `read_file_content` — **texto puro, sem base64, sem openpyxl**. O caminho antigo (`download_file_content` + openpyxl sobre o xlsx riscado) exigia binário via MCP e **não fecha**: fica como ritual local do usuário (`cronograma.py --sync-drive`), que é também o único portador da **ordem**. Ver `cronograma-contract.md` Cláusula 5b.
- **Delta, não total:** a planilha guarda acumulados por tarefa; importar só `(soma da aba) − (total no db)` por área — via `/importar-planilha` → `tools/importar_sessoes.py`.
- **Usuário relata "fiz X, acertei Y" (sem ter lançado na planilha ainda):** `tools/registrar_sessao_bulk.py` ANTES de processar erros (decisão "SSOT volumétrica" em `AGENTE.md §6`). O usuário tipicamente lança na planilha em paralelo — conciliar, não somar em dobro.
- **Cronograma:** a planilha `Cronograma de Reta Final.xlsx` NÃO persiste no db — leitura sob demanda para guiar prioridades e ler os marcadores de conclusão (decisão sessão 075). **v1.1:** a leitura do xlsx é do **usuário** (ritual local); o agente lê conclusão pelo `Realizada?` do Dashboard (Sheets nativo, texto) — ver `cronograma-contract.md` Cláusula 5b.

---

## Changelog

- **v1.2 (2026-09-01, ciclo descolar/ai-eng — F56):** **B2 promovida a BLOCKING de fato**
  (`state_utils::check_session_pointer` agora checa a condição CERTA — arquivo do ponteiro
  existe, com a exceção max+1 da sessão em curso — e o `auto_check` sai exit 1; era WARN de
  condição aparentada `>max+1`, com `success=True` fixo). **Matriz condição→instrumento**
  substitui a coluna "Como checar": cada linha declara o enforcement REAL (`BLOCK`/`manual`/
  `SEM IMPLEMENTAÇÃO`) — o changelog v1.1 declarou o rebaixamento consertado e consertou só
  a B1; a mentira estrutural (contrato afirma o que o código não faz) morre aqui. Sensor novo
  `NEEDS_QUALITATIVE_ATIVO` (WARN) cobre o invariante do contrato FSRS (F52b).
- **v1.1 (2026-08-14, s144):** **B1 promovida a BLOCKING de fato** (`tools/auto_check.py::check_handoff_len`, check 10 — era prosa desde a s075 e foi violada sem consequência: achado D3). **W8 reescrita** com o modelo de dois sinais: conclusão pelo `Realizada?` do Dashboard EMED 2026 (Sheets nativo, `read_file_content`, texto puro, agente executa) × ordem pelo xlsx local (ritual do usuário, `--sync-drive`, sem MCP); proibido exigir binário via MCP em passo de boot; caveat honesto quando faltar. Spec `.vibeflow/specs/consolidacao-part-4.md`.
- **v1.0 (2026-06-03, s075):** primeira instância; adaptado do Reconcile Mode do `agente-daktus-content`.
