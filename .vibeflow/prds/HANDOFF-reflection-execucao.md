# HANDOFF PRD: REFLECTION do MedHub sobre a própria execução (degrau 4/4 — auto-evolução)

> Gerado via M-HAND on 2026-07-12 — Fable/ai-eng (arquiteto observador).
> **Destinatário: o agente INTERNO do MedHub** (`/vibeflow:gen-spec` → `/implement` → `/audit`).
> Série: degrau 4 de 4 — o fechamento do loop. **Depende do degrau 2** (ledger-of-self é o
> input primário) e **aproveita o degrau 3** (série de sinais de processo). Implementar por último.

## ⛔ Fronteira clínica

O REFLECTION reflete sobre a **execução de engenharia** — rotinas, drift, WARNs, testes,
recorrência de achados. **NUNCA sobre os erros clínicos do usuário** (isso é FSRS/estudo,
domínio do usuário) **nem sobre conteúdo médico**. Se o datum proposto mencionar o mérito
de um card/resumo, ele está fora do escopo deste mecanismo.

## Problema

Com os degraus 1-3, o MedHub passa a se LER (sensores + ledger-of-self + série de
processo). Mas leitura sem julgamento periódico não muda decisão: os achados acumulam e
ninguém os converte em "o que o próximo ciclo de engenharia deve atacar". Hoje essa
conversão só acontece quando o arquiteto externo (ai-eng) audita — o MedHub não fecha o
próprio loop `plan → validate → execute → **reflect**` (`[aieng-book-ch06]`; `[cs230-l9]`
agentic loop).

Espelho do arquiteto: minha skill REFLECTION Modo A produz 1 datum honesto por sessão
substantiva ("(sem sinal novo)" quando não há — nunca fabricar) e o `evolution-signals.md`
agrega sinais em recomendação priorizada. É essa disciplina — não autonomia — que este
degrau transplanta.

## Público-alvo

O agente interno (que ganha pauta de engenharia derivada de evidência própria) e o
operador (que aprova ou redireciona a proposta de ciclo — o portão é dele).

## Solução proposta (WHAT, não HOW)

1. **Rito de fechamento de sessão de engenharia** (comando explícito, ex.:
   `auto_check --reflect` ou tool dedicada; gatilho determinístico > memória): consome
   ledger-of-self (degrau 2) + resultado do último `--all` + série de processo (degrau 3,
   se existir) e produz **1 datum estruturado**: o que a execução das rotinas revelou
   nesta janela (achado recorrente, check que degradou, suíte que oscilou).
2. **Honestidade obrigatória**: sem sinal novo → o datum é literalmente "(sem sinal novo)"
   e o rito PARA. Nunca fabricar insight (anti-sycophancy do arquiteto, `verificado_contra`:
   todo datum aponta o fingerprint/evidência que o sustenta — sem âncora, não entra).
3. **Proposta de próximo ciclo, GATED**: quando há sinal, o rito emite uma proposta
   priorizada (ex.: "DOC_DRIFT em ROADMAP recorreu 12 runs; propor ciclo de reconciliação")
   — **e para aí**. Nenhuma implementação, nenhum write fora do próprio datum. O humano
   (ou o agente interno com go explícito do operador) decide executar.
4. **Autonomia calibrada (`[ch06]` compound-mistakes + human-in-loop)**: o rito tem
   autonomia TOTAL na detecção e no registro do datum; ZERO autonomia em schema, força-push,
   conteúdo, ou execução da proposta. A autonomia cresce na leitura, não na escrita.

## Critérios de sucesso (o gen-spec transforma em DoD binário)

1. Rodar o rito com ledger-of-self vazio/estável → datum "(sem sinal novo)"; nenhuma
   proposta gerada; exit 0.
2. Rodar com achado recorrente injetado (fixture) → datum cita o fingerprint e a contagem;
   proposta gerada referencia a evidência.
3. O rito não escreve NADA além do próprio arquivo de datum (diff prova — nenhum doc,
   schema ou código tocado).
4. Datum é append-only e machine-readable (mesma família do ledger-of-self).
5. `pytest` verde + suíte do rito (sem-sinal, com-sinal, evidência-ausente → recusa a
   propor, corrupção de input → WARN e "(sem sinal)").
6. **Gate anti-decorativo (herdado do arquiteto)**: se em ≤3 execuções reais o rito não
   alterar nenhuma decisão de ciclo observável, REMOVER — reflexo que não muda decisão é
   decoração. Registrar este critério no próprio doc da tool.

## Anti-escopo

- **NÃO** refletir sobre erros clínicos do usuário nem sobre conteúdo médico.
- **NÃO** executar a proposta automaticamente (proposta ≠ mandato; o portão é humano).
- **NÃO** rodar em todo commit/boot (é rito de FECHAMENTO de sessão de engenharia — baixa
  frequência; rodar sempre = ruído + o gate anti-decorativo mata em 3 runs).
- **NÃO** usar LLM-judge sobre conteúdo dos achados neste degrau — agregação determinística
  primeiro (contagem/recorrência); julgamento probabilístico só se a v1 determinística
  provar insuficiente (não construir máquina antes de o sinal recorrer).
- **NÃO** alterar contratos/invariantes existentes do harness.

## Contexto técnico (para o gen-spec interno)

- Inputs: `history/ledger_self.jsonl` (degrau 2; path final = o que o gen-spec do degrau 2
  decidiu) · relatório do último `--all` · série de aderência (degrau 3, opcional).
- Referências de espelho no arquiteto (padrão, não código a copiar):
  `ai-eng/skills/REFLECTION.md` (Modo A) · `ai-eng/brain/observed-systems/evolution-signals.md`
  (agregador) · `ai-eng/brain/feedback/preference-signal.md` (datum com `verificado_contra`).
- Budget: ≤3 arquivos (tool do rito · teste · doc). É o menor degrau em código — o valor
  está na disciplina, não no volume.

## Handoff — como o MedHub toca isto

1. Fechar degraus 1-2 primeiro (sem ledger-of-self o rito não tem input honesto).
2. `/vibeflow:gen-spec .vibeflow/prds/HANDOFF-reflection-execucao.md`
3. `/vibeflow:implement` + `/vibeflow:audit`, gate de PASS.
4. Rodar o rito nas 3 sessões de engenharia seguintes e MEDIR o gate anti-decorativo antes
   de considerar a série concluída.

## Questões abertas

- Janela do rito (desde-o-último-rito vs últimos-N-dias) — gen-spec.
- A proposta priorizada usa qual função de score (recorrência pura vs recorrência×severidade) —
  começar simples: recorrência pura; severidade só se a v1 errar a prioridade.
- Quem roda o rito: o agente interno no fechamento (recomendado) vs pre-push hook (não —
  frequência errada) — confirmar com o operador no 1º uso.
