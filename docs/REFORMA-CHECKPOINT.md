# REFORMA-CHECKPOINT — 10/10/2026 15:25 · sessão s223 · mantido pelo medhub, conferido pelo ai-eng a cada relatório

> Protocolo: `C:/Users/daanm/ai-eng/artifacts/protocolo-retomada-reforma-medhub-2026-10-10.md`. O chat não é estado: retomar por este arquivo.

## Estado
Fase 0 (preparar o ambiente) · Lote 0 · part em curso: 0.3 (a lançar) · clear-safe: **sim** (G-part 0.2c fechado). O log `history/session_223.md` segue EM ABERTO: depois de /clear, continuar nele.

## Parts (Lote 0 → 5)
| id | spec (path no repo) | status | commit | suíte (n/falhas/s) | desvio declarado |
|---|---|---|---|---|---|
| 0.1 | `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-1.md` | PASS | 7d5948a | 1513/0/169 | §7.4 regenerada (classe -> Lote 3) |
| 0.2a | `…-part-2a.md` | PASS | 74eed0e | 1518/0/174 | §7.4 regenerada (GO ai-eng: parte do commit) |
| 0.2b | `…-part-2b.md` | PASS | 5887631 | 1535/0/158 | audit tirou a regra "toda aula liga a tarefa" (aula sem tarefa = "Outras aulas", estado previsto) |
| 0.2c | `…-part-2c.md` | PASS | e294651 | 1536/0/178 | §7.4 regenerada; sentinela em `sqlite3.connect` no script (achou `DB_PATH` próprio em `review_radar` e `variancia`); M-120 -> Lote 3 |
| 0.3 | `…-part-3.md` | pendente -- lançar COMO ESTÁ + restrição do ai-eng: a catraca BLOCK entra no conjunto "sempre" da part-1 (sem early-return, sem gatilho por extensão); o DoD "órfã nova = BLOCK" se prova no fluxo real (commit de teste com cláusula órfã sintética, revertido) | | | |
| 0.4a | `…-part-4a.md` | pendente | | | |
| 0.4b dry-run | `…-part-4b.md` | pendente | | | |
| 0.4b apply | `…-part-4b.md` | pendente (G-op dado, condicionado à 1.4) | | | |
| 1.0 RAG/LangMem fora do caminho crítico · 1.1 P5 · 1.2 P2 · 1.3 P6 · 1.4 cópia off-machine (Drive + git privado) | gen-spec do medhub após G-lote 0 | pendente | | | |
| 2.x P1 · 3.x hub+contratos · 4.x dados (multi-tenant) · 5.x medições | idem | pendente | | | |

## Próximo ato (1 linha)
medhub lê SÓ a spec `…-part-3.md` e lança 1 subagente -> audit do DoD -> commit + push -> linha aqui -> msg ao ai-eng (G-part 0.3); depois 0.4a e 0.4b dry-run -> G-lote 0.

## Gates abertos
- G-part 0.3 (medhub).
- G-op: apply da 0.4b só depois da 1.4 (cópia off-machine).
- (fechado 10/10 ~13:55) i e ii confirmadas por ele no chat do medhub: *"já foi respondido no ai-eng. se alinhem."* -- decisão dada no canal do ai-eng com verbatim vale; não re-perguntar.

## Decisões do operador (data · verbatim curto)
10/10 (no canal do ai-eng): i RAG/LangMem fora do caminho crítico SIM · ii purga/poda/gc SIM (após cópia off-machine) · iii cópia `ipub.db` = Drive + git privado ("drive e git") · iv ADR-006 ACEITO, opção A · v DISC §7: (1) produto, validado com ele primeiro -> infra product-ready, schema multi-tenant no Lote 4 · (2) terceiros "irrelevante": produto = provas públicas + cunhagem própria; cards = erros dos usuários; M-002 fecha como uso pessoal · (3) repo público por ora (conta Daktus), privado depois · (4) agente hospedado por ele, aditável; sem Managed Agents · (5) "não irei estudar hoje mais, portanto pode tocar nessa" -> tique desligado hoje, engenharia contínua.
10/10 (no chat do medhub): tique a 50 min só enquanto ele estuda; > 60 min com sessão ociosa sai mais caro (medição em `tmp/aieng/custo-tique-2026-10-10.md`).

## Regras de retomada
🔴 **Depois de /clear, PRIMEIRO ato:** o /clear renomeia a sessão -- mandar 1 mensagem de presença ao `ai-eng-51` (SendMessage; achar o nome por `ListAgents`) citando este checkpoint e o último commit; ele passa a responder ao nome novo. Registrar `in`/`out` no exchange-log.
boot = este arquivo + `HANDOFF.md` 8 linhas -> abrir SÓ a spec da part em curso -> 1 subagente implementa (teste antes, vermelho visto; sem índice nem commit) -> audit do DoD pelo medhub -> regenerar §7.4 (`python -X utf8 tools/reachability_check.py --tabela`) se o teste de consistência acusar -> commit + push -> linha aqui -> msg ao ai-eng (`uds` do ai-eng-51; registrar `in`/`out` no `history/exchange-log.jsonl`) -> G-part (pode /clear).
`/clear` só em G-part. Tique: religar a 50 min só em dia de estudo (memória `feedback_tique_registra_e_analisa`).
