# Spec: Descolar part-4 — contrato só afirma o que um teste prova (F56 · F53 · F52)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.
> F53 e F56 são a MESMA assinatura ("contrato declara enforcement que o código rebaixou") em dois
> alvos — a correção estrutural é única (handoff §5). Definiteness (law-contracts-geis): promessa
> sem enforcement não é lei.

## Objective

Zero cláusula de contrato afirmando BLOCKING/derivado sem o código correspondente: ou o código
sobe, ou o contrato desce COM changelog — e a divergência futura tem sensor.

## Context

F56: `reconcile-contract` declara B2 BLOCKING; `auto_check.py:267` implementa WARN com
`success=True` fixo E checa condição aparentada (ponteiro>max+1), não a escrita; B3/B4/W1/W3/W4
não têm implementação nenhuma (a coluna "como checar" é prosa) — a mesma falha que o changelog
v1.1 declarou consertada. F53: só o cap de 60 linhas físicas segura o HANDOFF; caps estruturais
todos violados; `render_handoff_block` não deriva "Erros & Cards"; `ESTADO.md:36` rotula
"derivados" contadores digitados. F52: o balanceador (`fsrs_balance.py`, muta `due` em toda
gravação state==2) está FORA do contrato FSRS que se declara governante; `needs_qualitative=1`
violado em 6 cards NA FILA ATIVA sem sensor; `state=3` fora do vocabulário.

## Definition of Done

1. [ ] B2 vira BLOCK REAL checando a condição CERTA (a escrita do ponteiro de sessão, não
       ponteiro>max+1) — com teste; OU, se a checagem real for inviável barata, o contrato é
       re-ratificado com o rebaixamento EXPLÍCITO e datado (nunca a mentira). Decisão default da
       spec: implementar o BLOCK (a condição é verificável por leitura do HANDOFF + history/).
2. [ ] `reconcile-contract` ganha matriz condição→instrumento com status VERDADEIRO por linha
       (`BLOCK auto_check#<id>` / `WARN auto_check#<id>` / `SEM IMPLEMENTAÇÃO — prosa`), changelog
       datado. Nenhuma linha afirmando enforcement inexistente.
3. [ ] `render_handoff_block` deriva a frente "Erros & Cards" (do `ipub.db`); os contadores do
       `ESTADO.md` rotulados "derivados" ou passam a ser derivados ou mudam de rótulo ("digitados").
4. [ ] Contrato FSRS absorve o balanceador (cláusula com os params estáveis + referência ao
       módulo) e `state=3` entra no vocabulário; check WARN `needs_qualitative=1 em fila ativa`
       no auto_check (nasce WARN, política s106/107) — os 6 cards atuais aparecem no painel.
5. [ ] Frontmatter `version` == título nos 4/9 contratos divergentes (menor do anexo — 1 linha
       cada, mesma família de drift).
6. [ ] Suite verde; testes novos registrados; craftsmanship: contratos em pt-BR, changelog datado,
       espelhos não tocados à mão.

## Scope

`tools/auto_check.py` · `core/contracts/reconcile-contract*.md` · `core/contracts/fsrs-management-contract*.md`
· `tools/day_plan.py` (render_handoff_block) · `ESTADO.md` (rótulo) · teste (≤6).

## Anti-scope

- Implementar B3/B4/W1/W3/W4 (viram linhas "SEM IMPLEMENTAÇÃO" honestas; implementação = demanda
  futura com prioridade própria).
- Mudar o COMPORTAMENTO do balanceador (só a lei absorve o fato).
- Reconciliar os 6 cards needs_qualitative (dado; aparece no painel, dono decide).

## Applicable Patterns

- `warn-first-check.md` · `agent-workflow-protocol.md` (HANDOFF/ESTADO são o contrato de boot).

## Risks

- B2-BLOCK pode travar commit legítimo se a condição real tiver borda → nasce com teste de
  fixture dos DOIS lados (viola/não-viola) e mensagem com instrução de reparo.

## References

- `ai-eng/HANDOFF-MEDHUB-COLA.md` §4 F52/F53/F56 · `AUDITORIA_MEDHUB.md §3o` (âncoras exatas).
