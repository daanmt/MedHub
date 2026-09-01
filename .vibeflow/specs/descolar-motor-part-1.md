# Spec: Descolar part-1 — painel de DÍVIDA + consumo do ledger (F54 · P5 · F61 · F46-log)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.
> **Upstream de todo o ciclo** (relação §5 do handoff): sem loop de consumo, cada conserto novo
> vira o próximo WARN dormido.

## Objective

Todo run do `auto_check` termina com UM painel de dívida legível — o leitor obrigatório que as 6
superfícies de sinal não têm — e o run para de pagar suítes em dobro.

## Context

`ledger_self.jsonl`: 462 fingerprints, 279 abertos, mesmo WARN visto 102× em 36 dias, **zero
chamadores de `ledger_self.abertos()` em código** (F54). `history/memory_errors.log` com 7 falhas
no dia da auditoria e nenhum check lê o arquivo (F46-log). A política WARN→BLOCK existente
("bloqueia quando a base zera", s106/107) está desarmada porque a base é invisível. E o
`auto_check` roda `test_revisao_calibrada` e `test_autonomia_hooks` DUAS vezes no mesmo run
(direto + via pytest/bridge) — **F61**, achado novo do discovery (P1).

## Definition of Done

1. [ ] `auto_check` (qualquer modo) termina com bloco `== DIVIDA ==`: top-5 do ledger aberto
       ordenado por (idade × ocorrências) com família/contagem/idade-dias; contagem do
       `memory_errors.log` + tail(2); contagem de reachability aberta; tamanho atual de
       `AUDITORIA_MEDHUB.md` em KB. Painel DETECTA e reporta — zero correção, zero BLOCK novo
       (warn-first-check).
2. [ ] `ledger_self.abertos()` (ou equivalente) ganha ≥1 chamador em código: o painel.
3. [ ] F61 morto: cada suíte roda no MÁXIMO 1× por run do `auto_check --all` (eliminar a execução
       direta OU a via bridge — a que preservar mais sinal); tempo por bloco de check impresso
       (`[12.3s]`), habilitando o SLO informativo do P1.
4. [ ] Teste novo (registrado em `pytest.ini::python_files`): painel renderiza de um ledger
       sintético com a ordenação correta; run com log de erros sintético mostra a contagem.
5. [ ] Suite pytest do medhub verde; craftsmanship: saída ASCII; sensores nunca escrevem;
       `import sqlite3` continua só em `db.py`.

## Scope

`tools/auto_check.py` · `tools/ledger_self.py` (API de leitura, se faltar) · `tools/test_painel_divida.py` (novo) · `pytest.ini` (4 arquivos).

## Anti-scope

- Promoção automática WARN→BLOCK (decisão P2 do PRD — a política existente decide com base zerada).
- Corrigir/fechar os 279 abertos (o painel dá visibilidade; a drenagem é decisão do dono).
- Delta-de-tamanho da AUDITORIA entre runs (exigiria estado persistido — ciclo 2 se o painel pegar).

## Technical Decisions

- Painel imprime SEMPRE (mesmo run verde) — dívida invisível em run verde é exatamente o modo de
  falha F54; 8 linhas de output custam nada.
- Ordenação idade×ocorrências (não só contagem): o WARN de 102× E o de 36 dias sobem juntos.

## Applicable Patterns

- `warn-first-check.md` — o painel é sensor: detecta, reporta, nunca corrige/bloqueia.

## Risks

- Painel vira papel de parede (a doença que ele trata) → mitigação: top-5 fixo e curto; se em 3
  sessões ninguém agir sobre o topo, o próprio painel é candidato a F62 (anti-decorativo).

## References

- `ai-eng/HANDOFF-MEDHUB-COLA.md` §1 Ponta B, §4 F54/F46 — números medidos.
