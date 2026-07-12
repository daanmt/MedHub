# HANDOFF PRD: Auto-instrumentação do ledger (degrau 2/4 — auto-evolução)

> Gerado via M-HAND on 2026-07-12 — Fable/ai-eng (arquiteto observador).
> **Destinatário: o agente INTERNO do MedHub** (`/vibeflow:gen-spec` → `/implement` → `/audit`).
> Série: degrau 2 de 4. **Depende parcialmente do degrau 1** (`HANDOFF-sensor-drift-doc-codigo.md`):
> instrumenta qualquer sensor existente; degrada graciosamente se o degrau 1 ainda não mergeou
> (instrumenta os checks 3-6 que já existem).

## ⛔ Fronteira clínica

Só **achados de execução/estado do sistema** entram no ledger-of-self: drift, WARN de
paridade, falha de suíte. Nenhum conteúdo clínico (texto de card/resumo, mérito médico)
é gravado. Achados sobre *arquivos* clínicos referenciam path e natureza estrutural do
problema, nunca o conteúdo.

## Problema

O MedHub já **detecta** inconsistências de si mesmo em runtime — `SESSION_POINTER_DRIFT`
(check 4), `POSICAO_DRIFT` (check 5), cobertura de semana (check 6), paridade
command↔skill (check 3), `WARN_TOTAL` do audit_resumos, e (degrau 1) `DOC_DRIFT` — mas os
achados **evaporam no stdout do run**. O que sobrevive é só o que um humano/agente copia à
mão para `AUDITORIA_MEDHUB.md` (todas as entradas F1-F35 entraram assim). Consequências:

- Achado recorrente não acumula evidência (um WARN que aparece 20 runs seguidos pesa o
  mesmo que um que apareceu 1 vez — não há série temporal).
- O ledger humano só cresce quando há sessão de engenharia; entre sessões, o sistema é
  cego para a própria degradação.

Espelho do padrão do arquiteto: meu ledger de observability se popula **por evento**
(update-on-event), não por memória de fim de sessão. Âncora: `[aieng-book-ch06]` —
reflection/error-correction como passo de 1ª classe do loop agêntico, não como cerimônia.

## Público-alvo

O agente interno do MedHub (que ganha memória estruturada dos próprios WARNs entre
sessões) e o degrau 4 (REFLECTION), que consumirá este ledger-of-self como input.

## Solução proposta (WHAT, não HOW)

1. **Ledger-of-self append-only, machine-readable** (ex.: `history/ledger_self.jsonl` —
   path/formato: gen-spec). Cada WARN emitido por check instrumentado gera um evento
   estruturado: timestamp, check de origem, fingerprint do achado, payload mínimo
   (valores divergentes, path afetado).
2. **Dedup por fingerprint**: o mesmo achado em runs consecutivos NÃO gera entradas
   duplicadas — atualiza `last_seen` + contador de ocorrências (é isso que cria a série
   temporal sem inflar o arquivo).
3. **Ciclo de vida**: quando um run passa limpo num check cujo fingerprint estava aberto,
   o evento é marcado resolvido (`resolved_at`). Aberto → resolvido é transição, nunca deleção.
4. **Superfície de leitura**: um comando (ex.: `auto_check --ledger-self` ou tool dedicada)
   lista abertos ordenados por recorrência — o "top da dívida viva" sem auditoria externa.

O ledger humano (`AUDITORIA_MEDHUB.md`, prosa F-NN) **permanece humano**: a máquina não
edita as entradas F-NN. Se o gen-spec decidir espelhar um resumo no .md, que seja em seção
dedicada gerada (padrão do check 3: a regra mora no gerador), nunca tocando prosa existente.

## Critérios de sucesso (o gen-spec transforma em DoD binário)

1. Run com WARN → evento aparece no ledger-of-self com fingerprint, origem e timestamp.
2. Segundo run com o MESMO WARN → zero entradas novas; `occurrences` incrementa.
3. Run limpo no check → fingerprint aberto transiciona para resolvido (com `resolved_at`);
   nada é deletado.
4. `AUDITORIA_MEDHUB.md` intocado pela máquina fora de seção gerada (diff prova).
5. A superfície de leitura lista abertos por recorrência em <1s (é boot-path adjacente;
   F2/latência-Windows é dívida conhecida — não piorá-la).
6. `pytest` verde + suíte nova (emissão, dedup, transição, corrupção de linha JSONL não
   derruba o harness — linha inválida = WARN e segue).

## Anti-escopo

- **NÃO** editar/reescrever entradas F-NN humanas do `AUDITORIA_MEDHUB.md`.
- **NÃO** auto-commitar o ledger-of-self (o run escreve o arquivo; commit segue o fluxo normal).
- **NÃO** promover achado a "F-NN oficial" automaticamente — promoção é julgamento
  (humano ou degrau 4 gated).
- **NÃO** gravar conteúdo clínico em nenhum evento.
- **NÃO** bloquear commit por achado no ledger-of-self (WARN-first preservado).

## Contexto técnico (para o gen-spec interno)

- Pontos de instrumentação hoje: `auto_check.py` checks 3/4/5/6 (todos já isolam o achado
  numa variável antes do print — instrumentar ali) + `_warn_total()` do audit_resumos +
  o check 7 do degrau 1 quando mergear.
- Fingerprint: estável sob re-run (ex.: hash de `check_id + alvo normalizado`, sem timestamp).
- JSONL append-only espelha o padrão do arquiteto (`brain/observability/usage.jsonl`).
- Budget: ≤4 arquivos (módulo ledger_self · auto_check.py · teste · doc curto no README das tools).

## Handoff — como o MedHub toca isto

1. Fechar o degrau 1 primeiro (ou declarar explicitamente que instrumenta só checks 3-6).
2. `/vibeflow:gen-spec .vibeflow/prds/HANDOFF-ledger-auto-instrumentacao.md`
3. `/vibeflow:implement` + `/vibeflow:audit`, gate de PASS.
4. Ao fechar: F-entry manual no ledger humano registrando a capacidade nova (a última
   entrada manual desta classe, se tudo der certo).

## Questões abertas

- Path/formato do ledger-of-self (`history/` vs `data/`; JSONL vs SQLite `medhub_memory.db`
  que já existe) — gen-spec; JSONL é a recomendação do arquiteto (grep-ável, diff-ável, zero DDL).
- Retenção: resolvidos ficam para sempre (série histórica) ou compactam após N dias — gen-spec.
- Espelho legível no .md: fazer já ou esperar demanda real (anti-decorativo) — recomendação: esperar.
