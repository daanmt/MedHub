# HANDOFF PRD: Telemetria de comportamento de estudo — metadado, não conteúdo (degrau 3/4 — auto-evolução)

> Gerado via M-HAND on 2026-07-12 — Fable/ai-eng (arquiteto observador).
> **Destinatário: o agente INTERNO do MedHub** (`/vibeflow:gen-spec` → `/implement` → `/audit`).
> Série: degrau 3 de 4. Independente dos degraus 1-2 (pode rodar em paralelo), mas o
> degrau 4 consumirá os sinais daqui.

## ⛔ Fronteira clínica — CRÍTICA neste degrau (ler duas vezes)

Este é o degrau com maior risco de deriva de escopo. A regra:

- **Permitido**: sinais de PROCESSO de estudo — timestamps, contadores, aderência
  (planejado × real), ratings FSRS como número, blocos pulados, posição no cronograma,
  tempo/energia declarados como flags. IDs e FKs de cards/temas são permitidos (referência
  opaca).
- **PROIBIDO**: o conteúdo do que foi estudado. Nenhuma estrutura nova armazena texto de
  pergunta/resposta, trecho de resumo, ou juízo sobre mérito clínico. Nenhuma métrica
  responde "o que o usuário sabe de medicina" — só "como o processo de estudo se comportou".
- **Linha de teste**: se para computar a métrica você precisaria LER o card/resumo, PARE —
  está fora. Se basta o revlog/agenda/estado, segue.

## Problema

A tese do produto (D54, definida pelo operador) é **orquestração da preparação**: distribuir
carga cognitiva pelo follow-up; posição errada no cronograma = inaceitável. Mas os sinais de
processo que alimentariam essa orquestração são hoje **de segunda classe**:

- Aderência (planejado × real) não é computada em lugar nenhum — o `day_plan` planeja,
  o revlog registra, ninguém compara.
- `--tempo`/`--energia` são consumidos no momento do plano e descartados — não há série.
- Blocos pulados/adiados só aparecem como prosa no HANDOFF (não-queryável).
- Drift de posição É detectado (`POSICAO_DRIFT`, check 5) — o único sinal de processo já
  de 1ª classe; é o precedente a generalizar.

Sem série desses sinais, o recomendador do dia (R1-R5) decide sempre a partir do estado
instantâneo, nunca do padrão de comportamento — e a "orquestração da preparação" fica
reativa em vez de preditiva.

## Público-alvo

O recomendador do dia (`day_plan`) como consumidor primário; o degrau 4 (REFLECTION) como
consumidor secundário; o operador via relatório de aderência.

## Solução proposta (WHAT, não HOW)

1. **Elevar sinais de processo a 1ª classe no schema**: estrutura(s) para plano-do-dia
   materializado (o que foi planejado, com timestamp) e flags de contexto (`--tempo`/
   `--energia` do run). O realizado JÁ existe (`fsrs_revlog`, `review_log`, `sessoes_bulk`,
   `preparacao_estado`) — não duplicar; a novidade é persistir o PLANEJADO para a comparação
   existir.
2. **Métrica de aderência computável**: planejado × real por dia/bloco, derivada só do db.
   Inclui: blocos cumpridos/pulados, volume planejado vs drenado, atraso de posição (reusa
   o cálculo do check 5).
3. **Superfície de leitura**: relatório (ex.: `day_plan --aderencia [--semanas N]`) que
   qualquer sessão/agente pode puxar — números, nunca prosa fabricada.
4. **Trava anti-sycophancy (`[aieng-book-ch08]`/`[ch10]`, espelho do `verificado_contra`
   do arquiteto)**: aderência e desempenho de processo aferem-se contra o MEDIDO (revlog,
   contadores), nunca contra auto-relato. `--energia` declarado é INPUT de contexto
   (dimensão do plano), jamais evidência de cumprimento.

## Critérios de sucesso (o gen-spec transforma em DoD binário)

1. Para uma semana real do db, o relatório de aderência produz planejado × real por dia
   sem nenhuma edição manual (derivável, no padrão dos números `[derivado: ...]`).
2. Rodar `day_plan` persiste o plano (com flags de contexto) de forma idempotente —
   re-rodar no mesmo dia não duplica (padrão F22/`--acumular` é o precedente).
3. Nenhuma estrutura nova contém coluna de texto clínico (schema prova: ids, timestamps,
   contadores, enums de status apenas).
4. Um bloco planejado e não-drenado aparece como "pulado" no relatório do dia seguinte —
   sem qualquer input humano.
5. `pytest` verde + suíte nova (persistência do plano, idempotência, aderência com fixture
   sintética — a fixture NÃO usa conteúdo real de cards, só ids).
6. Migração de schema no padrão `cleanup_db.py` (backup → validação → DDL), como no
   handoff de integridade.

## Anti-escopo

- **NÃO** armazenar ou processar texto de card/resumo em nenhuma estrutura nova.
- **NÃO** computar métricas de acerto CLÍNICO por tema como juízo de conhecimento — rating
  FSRS agregado é sinal de processo; interpretação de mérito médico fica com o usuário.
- **NÃO** mudar o comportamento do recomendador R1-R5 neste degrau (ele CONSOME a série em
  ciclo futuro; aqui só se constrói a série — contrato de paridade do recomendador intocado).
- **NÃO** notificar/alertar o usuário automaticamente (sem push, sem nag — orquestração é
  oferta no boot, decisão é dele).
- **NÃO** inferir estado emocional/energia a partir de comportamento (energia = flag
  declarada, ponto).

## Contexto técnico (para o gen-spec interno)

- Tabelas vivas: `preparacao_estado` (posição SSOT, op-3), `fsrs_revlog`, `review_log`,
  `sessoes_bulk`, `questoes_erros`, `taxonomia_cronograma`. `medhub_memory.db` existe à parte —
  decidir onde a série mora (recomendação: `ipub.db`, junto do que ela mede).
- `day_plan --tempo/--energia` já parseia os flags; o gancho de persistência entra ali.
- `db.py` é a única camada com `import sqlite3` (convenção — respeitar).
- Budget: ≤6 arquivos; provável split em 2 partes (part-1 persistir plano+flags; part-2
  relatório de aderência). O gen-spec decide.

## Handoff — como o MedHub toca isto

1. `/vibeflow:gen-spec .vibeflow/prds/HANDOFF-telemetria-comportamento-estudo.md` (decidir split).
2. `/vibeflow:implement` + `/vibeflow:audit` por parte, gate de PASS entre elas.
3. Ao fechar: reconciliar ROADMAP (linha de orquestração) e registrar F-entry da capacidade.

## Questões abertas

- Quais métricas o OPERADOR quer ver primeiro no relatório (aderência bruta? atraso série?
  taxa de blocos pulados por dia-da-semana?) — colher no 1º uso real, não especular (anti-decorativo).
- Retenção da série (tudo para sempre vs janela) — gen-spec; o db é local e pequeno, tudo-para-sempre é ok.
- `--pre-bloco`/reincidência entram na aderência (bloco anti-reincidência planejado conta como bloco?) — gen-spec.
