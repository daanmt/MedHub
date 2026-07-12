# Spec: Sensor de drift doc-vs-código (check 7 do auto_check) — degrau 1/4

> Gerado de `.vibeflow/prds/HANDOFF-sensor-drift-doc-codigo.md` em 2026-07-12 (Fable/ai-eng).
> Executor: Fable/ai-eng (reforma delegada pelo operador).
> ⛔ Fronteira clínica: o sensor lê APENAS docs de estado/engenharia (allowlist) e
> código/schema — nunca `resumos/**` nem conteúdo de cards.

## Objective

O `auto_check` passa a detectar sozinho quando ROADMAP/HANDOFF/ESTADO/AUDITORIA afirmam
algo que o código/schema/estado desmentem — a classe de dívida que hoje só auditoria
externa pega (`Drift-as-Primary-Debt`).

## Context

Checks 4/5 já detectam dois drifts pontuais (ponteiro de sessão, posição SSOT). A classe
geral ficou provada na auditoria de 2026-07-12: FSRS marcado TODO já feito, símbolos
removidos ainda citados como pendência, contadores narrativos divergindo do derivável (F6).
O template WARN-first (função pura → `[WARN] TAG:` → `success=True`) está pronto nas
linhas ~281-320 do `auto_check.py`.

## Definition of Done

1. [ ] `tools/doc_drift.py` existe e verifica as **4 espécies de anotação** contra a
   realidade: `sqlite` (query escalar read-only no `ipub.db` == valor esperado), `symbol`
   (`<path>::<nome>` exists|absent via inspeção do arquivo), `path` (arquivo exists|absent),
   `unique` (constraint/índice único em tabela exists|absent via PRAGMA). Cada espécie tem
   teste true→silêncio e false→WARN.
2. [ ] `auto_check --all` executa o check 7 e o relatório final mostra a linha do check
   com contagem de WARNs; **nenhum WARN altera o exit-code** (falsificar uma anotação e
   rodar: exit continua 0, WARN aparece).
3. [ ] Anotações-seed nos docs reais: ≥3 claims anotados, incluindo
   `unique taxonomia_cronograma (area, tema) absent` (claim ABERTO do ROADMAP) e
   `symbol app/utils/db.py::get_next_due_card absent`. Semântica correta de drift:
   **WARN = doc ≠ realidade** — quando o handoff de integridade criar a constraint, o
   sensor passa a emitir WARN (doc stale) até a linha do ROADMAP ser reconciliada e a
   anotação virar `exists`. (Corrige a redação imprecisa do critério 3 do PRD.)
4. [ ] Run real pós-seed emite **0 WARN** (os docs estão verdadeiros após a reconciliação
   de 2026-07-12) — se emitir, ou o doc está stale (reconciliar) ou o sensor está errado (corrigir).
5. [ ] Anotação malformada → `[WARN] DOC_DRIFT_SYNTAX` e segue; nunca crash, nunca bloqueio.
   Allowlist de docs-alvo hardcoded = {ROADMAP.md, HANDOFF.md, ESTADO.md, AUDITORIA_MEDHUB.md};
   teste prova que nenhum arquivo fora da allowlist é aberto.
6. [ ] Craftsmanship: `pytest` inteiro verde; convenções respeitadas (CLI `argparse`
   invocável standalone, prints pt-BR legíveis, conexão sqlite read-only fechada em
   `finally` — exceção autorizada de tools/ do pattern db-access-layer); zero violação
   dos Don'ts de conventions.md.

## Scope

- `tools/doc_drift.py` (novo): parser de anotações + 4 verificadores + modo standalone
  `python tools/doc_drift.py [--json]`.
- `tools/auto_check.py`: bloco do check 7 no `main()` (import direto, padrão dos checks 4/5 —
  não subprocess), autocontido para merge trivial com o handoff de integridade.
- `tools/test_doc_drift.py` (novo): suíte com fixtures de doc sintético (tmp_path).
- `ROADMAP.md` + `HANDOFF.md`: anotações-seed (só comentários HTML; zero mudança de prosa).

## Anti-scope

- NÃO auto-corrigir docs. NÃO escrever no ledger (degrau 2). NÃO parsear prosa livre/NLP.
- NÃO transformar WARN em bloqueio. NÃO tocar `resumos/**` nem conteúdo clínico.
- NÃO cobrir os contadores `[derivado: day_plan --handoff-block]` por diff-de-bloco nesta
  v1 (fragilidade de parsing; espécie `sqlite` cobre contadores pontuais; bloco inteiro = v2
  se o sinal recorrer).
- NÃO duplicar checks 4/5.

## Technical Decisions

- **Sintaxe da anotação**: comentário HTML na linha imediatamente acima do claim —
  `<!-- drift-check: <kind> <args...> -->`. Invisível no render, grep-ável, não polui prosa.
  Kinds v1: `sqlite "<query>" == <int>` · `symbol <path>::<nome> exists|absent` ·
  `path <path> exists|absent` · `unique <tabela> (<col,col>) exists|absent`.
- **Import, não subprocess**: o check 7 chama `doc_drift.run_checks()` importado — mesma
  família dos checks 4/5 (função pura testável); subprocess é para suítes (checks 1/2).
- **Read-only por construção**: conexão sqlite aberta com `mode=ro` (URI) — o sensor não
  pode escrever nem por bug.
- **`unique` via `PRAGMA index_list` + `index_info`**: cobre tanto `CREATE UNIQUE INDEX`
  quanto constraint de tabela — não depende de como o handoff de integridade implementar.

## Applicable Patterns

- `db-access-layer.md` — tools/ como exceção autorizada; conexão própria, fechada.
- `error-insertion-pipeline.md` — convenções de CLI tools (argparse, stdout legível, bool).
- Template WARN-first dos checks 4/5/6 do `auto_check.py` (padrão local, não documentado
  em patterns/ — **candidato a pattern novo** `warn-first-check.md` se o degrau 2 confirmar a família).

## Risks

- **Anotação apodrece** (claim reconciliado, anotação esquecida) → mitigação: o próprio
  WARN aponta a anotação; DoD 4 estabelece o run-limpo como invariante de fechamento.
- **Colisão de merge com o handoff de integridade** (mesmo `auto_check.py`) → mitigação:
  bloco autocontido + coordenação já anotada nos dois PRDs; integridade primeiro se simultâneo.
- **Query sqlite lenta no boot-path** (F2 latência Windows) → mitigação: check 7 só no
  `--all` e quando docs-alvo mudam no `--changed`/`--staged`; queries escalares indexadas.

## Dependencies

- Nenhuma (primeiro da série). O handoff de integridade (`HANDOFF-integridade-harness-taxonomia.md`)
  toca o mesmo arquivo mas é independente — apenas coordenar ordem de merge.
