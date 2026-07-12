# Spec: Auto-instrumentação do ledger (ledger-of-self) — degrau 2/4

> Gerado de `.vibeflow/prds/HANDOFF-ledger-auto-instrumentacao.md` em 2026-07-12 (Fable/ai-eng).
> Executor: Fable/ai-eng (reforma delegada pelo operador).
> ⛔ Fronteira clínica: só achados de execução/estado do sistema entram no ledger-of-self;
> nenhum texto clínico é gravado (achado sobre arquivo clínico = path + natureza estrutural).

## Objective

Os WARNs que o harness já emite deixam de evaporar no stdout: cada achado vira evento
estruturado com fingerprint, recorrência e ciclo de vida — memória de si que se popula
sozinha, entre sessões.

## Context

Todos os F1-F35 do `AUDITORIA_MEDHUB.md` entraram à mão. Os detectores existem (checks
3/4/5/6 do `auto_check.py`, `WARN_TOTAL` do audit_resumos, check 7 do degrau 1), todos já
isolam o achado numa variável antes do print — o ponto de instrumentação é trivial. Sem
série temporal, um WARN que recorre 20 runs pesa o mesmo que um que apareceu 1 vez.

## Definition of Done

1. [ ] Run do `auto_check` com WARN em qualquer check instrumentado (3-7) → evento em
   `history/ledger_self.jsonl` com `{ts, check, fingerprint, payload, event}`; fingerprint
   estável sob re-run (hash de check_id + alvo normalizado, sem timestamp).
2. [ ] **Dedup**: segundo run com o MESMO WARN → **zero linhas novas** no JSONL (evento
   `opened` só na transição); `history/ledger_self_state.json` (estado derivado, reescrito
   por run) incrementa `occurrences` e atualiza `last_seen`.
3. [ ] **Ciclo de vida**: run limpo num check cujo fingerprint estava aberto → evento
   `resolved` apendado (com `resolved_at`); nada é deletado; reaparição → novo `opened`
   (histórico de flapping preservado).
4. [ ] `python tools/ledger_self.py --list` imprime os abertos ordenados por recorrência
   (o "top da dívida viva"); linha JSONL corrompida → `[WARN]` e segue, nunca crash.
5. [ ] `AUDITORIA_MEDHUB.md` **intocado pela máquina**: teste prova que o módulo não abre
   o arquivo em modo escrita; diff do repo pós-run mostra apenas `history/ledger_self*`.
6. [ ] Craftsmanship: `pytest` inteiro verde + suíte nova (emissão, dedup, transição
   opened→resolved→reopened, corrupção); convenções de CLI tools respeitadas; zero
   violação dos Don'ts; nenhum conteúdo clínico em nenhum payload (teste com fixture).

## Scope

- `tools/ledger_self.py` (novo): API `record(check, findings)` + rebuild do state +
  CLI `--list`.
- `tools/auto_check.py`: chamada `record(...)` nos pontos onde os checks 3/4/5/6 (e 7,
  se mergeado) já isolam o achado — uma linha por check, sem mudar a lógica de detecção.
- `tools/test_ledger_self.py` (novo).
- `.gitignore`: decidir se `ledger_self_state.json` (derivado) entra; o `.jsonl` (fonte)
  é versionado.

## Anti-scope

- NÃO editar/reescrever entradas F-NN humanas do `AUDITORIA_MEDHUB.md` — nem seção gerada
  no .md nesta v1 (anti-decorativo: espelho legível só se houver demanda real).
- NÃO auto-commitar. NÃO promover achado a F-NN automaticamente. NÃO bloquear commit por
  achado. NÃO gravar conteúdo clínico. NÃO instrumentar checks 1/2 (suítes pytest já têm
  relatório próprio; instrumentá-las = ruído duplicado).

## Technical Decisions

- **JSONL (transições) + JSON (estado derivado)**: append-only puro não comporta
  `occurrences`/`last_seen` mutáveis — separo evento (imutável, versionado, diff-ável) de
  estado (derivado, reconstruível a partir dos eventos + run corrente). Trade-off: 2
  arquivos, mas cada um com contrato simples. Rejeitado: SQLite em `medhub_memory.db`
  (acopla o harness a um db de outra camada; grep/diff perdem).
- **`history/`** como pasta (junto de `session_NNN.md` — é memória de execução, mesma família).
- **Instrumentação por chamada explícita**, não por captura de stdout: os checks já têm o
  achado estruturado em variável; parsear o próprio print seria fragilidade gratuita.
- **Fingerprint** = `sha1(check_tag + "|" + alvo_normalizado)[:12]` — payload (valores
  divergentes) fica FORA do fingerprint para que a mesma divergência com números novos
  continue sendo o mesmo achado.

## Applicable Patterns

- `error-insertion-pipeline.md` — convenções de CLI tools.
- `agent-workflow-protocol.md` — o ledger-of-self alimenta o fechamento de sessão (degrau 4).
- Template WARN-first (checks 4/5/6) — consolida a família `warn-first-check` (2º uso;
  registrar como pattern novo em `.vibeflow/patterns/` ao fechar esta spec).

## Risks

- **Flapping** (check oscila aberto/resolvido a cada run) infla o JSONL → mitigação:
  histórico de flapping é sinal, não ruído (o degrau 4 o consome); se inflar de verdade,
  compactação é decisão futura documentada como questão aberta.
- **Latência no boot-path** (F2 Windows) → mitigação: I/O é 1 leitura + 1 append + 1
  rewrite de JSON pequeno; sem rede, sem subprocess novo.
- **Contrato do payload deriva** (cada check grava um shape diferente) → mitigação:
  `record()` valida shape mínimo e serializa o resto como `extra` opaco.

## Dependencies

- `.vibeflow/specs/sensor-drift-doc-codigo.md` (parcial — instrumenta o check 7 se
  mergeado; degrada graciosamente para checks 3-6 se não).
