# Spec: REFLECTION da própria execução (rito gated) — degrau 4/4

> Gerado de `.vibeflow/prds/HANDOFF-reflection-execucao.md` em 2026-07-12 (Fable/ai-eng).
> Executor: Fable/ai-eng (reforma delegada pelo operador). Implementar POR ÚLTIMO
> (consome o ledger-of-self do degrau 2).
> ⛔ Fronteira clínica: reflete sobre execução de ENGENHARIA (rotinas, drift, WARNs,
> recorrência) — nunca sobre erros clínicos do usuário nem conteúdo médico.

## Objective

No fechamento de sessão de engenharia, o MedHub produz 1 datum honesto sobre a própria
execução + (se houver sinal) uma proposta de próximo ciclo com evidência — e para aí:
o portão de execução é humano.

## Context

Degraus 1-3 fazem o sistema se LER; sem julgamento periódico, achados acumulam e nada
converte em pauta — hoje essa conversão só acontece quando o arquiteto externo audita.
Espelho da disciplina do arquiteto: REFLECTION Modo A ("(sem sinal novo)" quando não há;
nunca fabricar), datum com `verificado_contra`, gate anti-decorativo.

## Definition of Done

1. [ ] `python tools/reflect.py` com ledger-of-self vazio/estável na janela → datum
   `"(sem sinal novo)"` apendado em `history/reflection_data.jsonl`, **nenhuma proposta**,
   exit 0.
2. [ ] Com achado recorrente na janela (fixture) → datum cita `fingerprint` + contagem +
   check de origem; proposta de ciclo referencia essa evidência. **Sem evidência
   referenciável → recusa a propor** (teste: achado sem fingerprint válido → datum sim,
   proposta não).
3. [ ] O rito **escreve APENAS** `history/reflection_data.jsonl` — teste prova por
   snapshot do filesystem (nenhum doc, schema, código ou ledger tocado); nenhuma execução
   de proposta, nenhum subprocess de escrita.
4. [ ] Janela determinística: desde o timestamp do último datum (ou tudo, no 1º run) —
   dois runs consecutivos sem mudança no ledger → o 2º é "(sem sinal novo)" (idempotência
   de leitura).
5. [ ] Score de priorização v1 = recorrência pura (`occurrences` do ledger-of-self);
   documentado no próprio arquivo da tool com o **gate anti-decorativo**: se em ≤3
   execuções reais o rito não alterar nenhuma decisão de ciclo observável, REMOVER a tool
   (critério herdado do arquiteto, registrado no docstring + doc).
6. [ ] Craftsmanship: `pytest` inteiro verde + suíte do rito (sem-sinal, com-sinal,
   evidência-ausente, input corrompido → `[WARN]` + datum "(sem sinal novo)", nunca
   crash); agregação 100% determinística (zero chamada de LLM); convenções CLI e Don'ts
   respeitados.

## Scope

- `tools/reflect.py` (novo): leitura do ledger-of-self (+ aderência part-2 se disponível,
  input opcional) → datum JSONL → proposta impressa no stdout (o datum grava a proposta;
  o stdout é a entrega ao humano).
- `tools/test_reflect.py` (novo).
- Registro no fechamento: 1 linha no protocolo de closure (`agent-workflow-protocol` —
  onde o agente já atualiza ESTADO/history, adicionar "rodar reflect") — edição mínima
  no doc de workflow correspondente.

## Anti-scope

- NÃO executar a proposta (proposta ≠ mandato). NÃO rodar em commit/boot/pre-push
  (frequência errada — é rito de fechamento). NÃO LLM-judge nesta v1 (determinístico
  primeiro; probabilístico só se a v1 errar prioridade comprovadamente). NÃO refletir
  sobre erros clínicos/conteúdo. NÃO alterar contratos/invariantes do harness. NÃO
  auto-promover datum a F-NN do ledger humano.

## Technical Decisions

- **Datum JSONL na mesma família do ledger-of-self** (`history/reflection_data.jsonl`):
  consistência de formato, grep-ável, e o degrau 1 pode um dia verificar claims sobre ele.
- **Janela por último-datum** (não por dias): sessões de engenharia são irregulares;
  janela por tempo produziria "(sem sinal novo)" falsos em hiato longo.
- **Proposta dentro do datum** (não arquivo separado): 1 evento = 1 registro; o humano lê
  o stdout; ferramentas leem o JSONL. Dois artefatos para a mesma coisa = drift futuro.
- **Aderência como input opcional**: `reflect` funciona só com o ledger-of-self (dependência
  dura mínima); série de processo enriquece quando existir — degrade gracioso, mesmo padrão
  do degrau 2.

## Applicable Patterns

- `agent-workflow-protocol.md` — o rito entra no closure protocol (boot/closure é o
  gatilho determinístico; a skill não depende de memória do agente).
- `error-insertion-pipeline.md` — CLI/argparse/stdout.
- Família `warn-first-check` (candidata, 3º uso) — promover a
  `.vibeflow/patterns/warn-first-check.md` ao fechar a série, se ainda não registrada.

## Risks

- **Vira decoração** (roda, ninguém muda decisão) → mitigação: o gate anti-decorativo é
  DoD 5 — remoção é resultado aceitável e declarado.
- **Proposta genérica** ("melhorar testes") → mitigação: DoD 2 exige fingerprint/evidência;
  sem âncora, sem proposta.
- **Duplo ledger confunde** (ledger-of-self vs reflection_data) → mitigação: contratos
  distintos documentados — um registra ACHADOS brutos por run; o outro registra JULGAMENTOS
  por sessão; reflect lê o primeiro e escreve só o segundo.

## Dependencies

- `.vibeflow/specs/ledger-auto-instrumentacao.md` (obrigatória — input primário).
- `.vibeflow/specs/telemetria-estudo-part-2.md` (opcional — enriquece, não bloqueia).
