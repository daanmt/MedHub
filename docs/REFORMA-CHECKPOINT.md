# REFORMA-CHECKPOINT — 11/10/2026 00:45 · sessão s223 · mantido pelo medhub, conferido pelo ai-eng a cada relatório

> Protocolo: `C:/Users/daanm/ai-eng/artifacts/protocolo-retomada-reforma-medhub-2026-10-10.md`. O chat não é estado: retomar por este arquivo.

## Estado
Fase 0 (preparar o ambiente) · **Lote 0 completo, G-lote 0 ACEITO** (ai-eng, 10/10 23:32; detalhe por part no `history/session_223.md`). Lote 1: 1.pre PASS (`4300bed`), **1.4 PASS (`3f53136`)**, M-134 fechado (`55d1144`), **1.0 PASS (`bcb02bf`)**; agora espera o **G-op do operador** (repo git privado -> apply -> push -> clone fresco + `--conferir` -> Drive + md5), e em paralelo seguem as specs 1.1 -> 1.2 -> 1.3. clear-safe: **sim** depois do push deste commit. O log `history/session_223.md` segue EM ABERTO: depois de /clear, continuar nele.

## Parts (Lote 0 → 5)
| id | spec (path no repo) | status | commit | suíte (n/falhas/s) | desvio declarado |
|---|---|---|---|---|---|
| 0.1 · 0.2a · 0.2b · 0.2c · 0.3 · 0.3h · 0.4a · 0.4b dry-run · fecho | `…-lote0-harness-hermetico-part-{1,2a,2b,2c,3,3h,4a,4b}.md` | PASS | 7d5948a · 74eed0e · 5887631 · e294651 · bb6ebd3 · beebc04 · a240f94 · 836f635 · 17f8e0f | 1513 -> 1554/0 | desvios aceitos pelo ai-eng (0.3 DoD 4 NV; 0.3h prova com backstop; 0.4b `gc --no-prune`; fecho com 2 restos do doc_drift); detalhe por part no `history/session_223.md` |
| 0.4b apply | `…-part-4b.md` | pendente (G-op do operador, só depois da 1.4 com md5 dos 48 conferido: M-129) | | | |
| **G-lote 0** | — | ACEITO pelo ai-eng (10/10 23:32) | 8479d7e | 1554/0/178 | — |
| 1.pre `/vibeflow:analyze` (resto do M-127) | — | PASS | 4300bed | 1554/0/177 (do filho, `python -m pytest tools/ -q`; commit de `.vibeflow/` não dispara a suíte) | 7 docs; fora dos marcadores idêntico ao HEAD (script); doc_drift 2 -> 1 (`index.md:177`, o histórico); fatos novos conferidos no código (`questoes_realizadas` intocado, fallback heurístico removido, `fsrs>=6.3.2`, módulos e funções citados existem). Achados não corrigidos ao ai-eng: registry x frontmatter em 5 patterns; Anti-patterns manuais velhos (`domain-engine-api:106`, `agent-workflow-protocol:91-92`, `error-insertion-pipeline:137`); `criar-resumo.md` passo 8 (`--delete-pdfs`) e `AGENTE.md:208` ("Zero PDF") x retenção s086; frontmatter legado de `Assistência ao Parto.md` |
| 1.4 cópia off-machine (PRIMEIRO no Lote 1) | `.vibeflow/specs/medhub-fase0-lote1-part-4.md` | PASS; cópia real feita e conferida em 11/10 | 3f53136 | 1585/0/188 | adições (A) e (B) do ai-eng dentro; dry-run real N=49, 352,5 MB, backups + `ipub.db` idênticos, destino não criado; recusa `--dest` no repo público (até com caixa trocada); gate `BANCO_NO_RECORTE` no fluxo real: o `git add` foi recusado pelo gitignore e o commit com `-f` BLOQUEADO só por ele, HEAD intacto, revertido; §7.4 regenerada (1 linha + 6 contadores) |
| 1.0 RAG/LangMem fora do caminho crítico | `.vibeflow/specs/medhub-fase0-lote1-part-0.md` | PASS | bcb02bf | 1587/0/190 | baseline em `tmp/lote1/part-0-baseline.md`: boot 3,111 -> 2,538 s (mediana de 5, banco sintético); import 635 -> 84 ms (langgraph 546 ms saiu; langmem/chromadb/ollama/anthropic já não entravam); contexto 11.883 -> 8.885 bytes (o bloco = 25%); última consolidação 07/10 (selo da s220) x 182 sessões. `settings.json`: só a entrada Write saiu (diff conferido). Revogação em 3 passos (AGENTE §2.7 e §8 + 2 termos); desvio: 7 arquivos, com `registrar-sessao.md` §4/§5 lapidados no mesmo commit (§10.10) |
| 1.1a P5 figuras (código) · 1.1b (recaptura t40 + S4-S7, aviso no hub) + hotfix de precisão do `CITA_FIGURA` | `.vibeflow/specs/medhub-fase0-lote1-part-1{a,b}.md` | PASS | 164cd7a · ebc13c2 · (este) | 1603 -> 1626/0 | 77 listas recapturadas; banco: 52 mescladas + 34 `sem_figura` retirados (2 fixados); hub: 52 updates + 34 `__delete__`, hub V91; t40 Q5/6/18/21/22 com figura; precisão 0/20 -> hotfix (1 falso residual t325_45); relatório `tmp/lote1/part-1b-figuras.md`; M-143..M-145 |
| 1.2 P2 gate de cadeia no `--exportar` · 1.3 P6 âncora `emed_card_ancora` | `C:/Users/daanm/ai-eng/.vibeflow/specs/medhub-fase0-lote1-part-{2,3}.md` (do ai-eng; DoD 1 MEDE antes) | pendente: depois da 1.1b (o gate da 1.2 toca o `--exportar` que a 1.1b usa) | | | |
| 2.1-2.3 P1 fontes estruturadas (schema `referencia`, evidence-governance v1.2, amostra 62) · 3.x hub+contratos · 4.x dados · 5.x medições | 2.x: `C:/Users/daanm/ai-eng/.vibeflow/specs/medhub-fase0-lote2-fontes-part-{1,2,3}.md` (só depois do G-lote 1; reler o disco; apply do migrador = G-op; triagem dos 62 = ai-eng) | pendente | | | |

## Próximo ato (1 linha)
1.1 FECHADA -> esperar do ai-eng a vez da 1.2 (spec dele, `C:/Users/daanm/ai-eng/.vibeflow/specs/medhub-fase0-lote1-part-2.md`) e depois a 1.3.

## Dívida nascida no Lote 0 (dono medhub, -> Lote 3; linhas em `docs/BACKLOG-UNICO-MEDHUB.md`)
- **M-120** leitor do `ipub.db` real em `mode=ro` para os testes `vivo` (audit da 2a).
- **M-121** inventário dos módulos com `DB_PATH` próprio: `review_radar`, `variancia` e os que o sentinela achar (audit da 2c; confirmado pelo ai-eng 10/10).
- **M-128** `get_caderno_erros`, a 11ª função morta do `db.py`, fora da lista da 0.4a (fecho).
- **M-131** `tmp/` SOLTO (17.189 arquivos, 40,2 MB): inventário + regra de vida do `tmp/`.
- **M-132** Pattern Registry do `.vibeflow/index.md` x frontmatter de 5 patterns: o registry vira DERIVADO do frontmatter por ferramenta, com sensor (achado do 1.pre).
- **M-133** Anti-patterns manuais velhos (`domain-engine-api:106`, `agent-workflow-protocol:91-92`, `error-insertion-pipeline:137`), mesma classe do M-127. · **M-135** frontmatter legado de `resumos/GO/Assistência ao Parto.md` (quando a referência for tocada ou no inventário de frontmatter).
- **M-137** `.agents/workflows/` fora dos portadores que o `CONTRATO_REVOGADO` vigia (classe do M-122: o sensor existe, o caminho não chega). · **M-138** flag `--delete-pdfs` viva no `extract_pdfs.py`: remédio preferido = recusar salvo `--confirmo-apagar` explícito (não remover).
- **M-139** resíduos descritivos da era "LangMem no boot" (`README.md:169`, `ROADMAP.md:83`, `.vibeflow/patterns/agent-workflow-protocol.md:36`, comentário falso em `app/engine/get_topic_context.py:153`), classe do M-127/M-133, por lista.
- (ambiente local, sem commit) **M-140** `.codex/hooks.json` (gitignored) ainda dispara a consolidação se o Codex rodar: 1 linha no arquivo local. 🔴 Pendente de confirmação do OPERADOR, porque é configuração de harness e o pedido veio do ai-eng; o medhub não edita config a pedido de par.
- (1.4b, data do operador) **M-141** PDFs (491, 6,2 GB) + `decks/cards.json` (379 MB) fora de qualquer cópia -> cópia direta ao Drive, fora do git.
- (Lote 4 / Fase 1) **M-136** retenção do repo privado: cada cópia off-machine pesa ~352 MB, e a recorrência ficou fora da 1.4 (ex.: 1 cópia por semana depois de 30 dias).
- **M-134** FECHADO em `55d1144` (11/10): a deleção do PDF-fonte saiu do fluxo (`criar-resumo` passo 8, skill `/extrair-pdf`, `AGENTE.md` §6 e §7.3) pelo §10.10 em 3 passos; termo `--delete-pdfs` vigiado pelo `CONTRATO_REVOGADO`. Default não destrutivo do operador (retenção da s086). Achado: o `.agents/workflows/` não está entre os 31 portadores que o gate vigia.
- (fora do Lote 3) **M-129** = condição do G-op da 0.4b (a rotação pós-apply apaga 49 de uma vez); **M-130** `tmp/alca_s213` (268,8 MB, CITADO só por 1 audit) = decisão do OPERADOR, quem pergunta é o ai-eng; não tocar.

## Gates abertos
- G-op 0.4b apply: só depois da 1.4 com md5 dos 48 conferido (M-129). 🔴 Medido no dry-run: os 5 backups de rotação são de 26/09 a 07/10, mais velhos que os fixados de 09/10 que voltariam à rotação. Depois do apply, o próximo `backup()` guarda o novo + 4 desfixados de 09/10 e apaga 49 de uma vez, inclusive os 5 de rotação de hoje. No disco ficam só pontos de 09/10 e 10/10. Comando: `python tools/backup_db.py --desfixar-lote --manter 5 --motivo "..." --apply --expect 48`.
- G-op 1.4: FECHADO (11/10 ~13:40). Cópia `20261011_123917` no repo PRIVADO `daanmt/backup-medhub` (clone em `C:/Users/daanm/backup-medhub`): N=49, 352,5 MB, md5 `ipub.db` 1f5f357f…; clone fresco + `--conferir` = 49/49. Drive = 2ª cópia opcional. Destrava o pedido do apply da 0.4b (quem pede ao operador é o ai-eng).
- G-op `tmp/`: limpeza só da classe SOLTO, depois do GO (inventário em `tmp/lote0/part-4b-tmp-inventario.md`); `alca_s213/` = M-130.
- (fechado 10/10 ~13:55) i e ii confirmadas por ele no chat do medhub: *"já foi respondido no ai-eng. se alinhem."* -- decisão dada no canal do ai-eng com verbatim vale; não re-perguntar.

## Limites conhecidos (aceitos pelo ai-eng; revisar na data)
- 0.3 DoD 4: `banco-emed.md:154` (Figura, s221) com `NAO-VERIFICAVEL`. O teste da figura prova só a URL em `figuras`; "nunca este script baixa" não tem sensor. Revisar **2026-12-31** (P5 do Lote 1). D83, 3º destino.
- Fecho do Lote 0: `conventions.md:54` (dentro de `auto`) saiu no 1.pre (`4300bed`); `.vibeflow/index.md:177` (era a 169) é registro riscado de achado resolvido e fica: é o único resto do doc_drift em `.vibeflow/`.

## Notas de design para a Fase 1 (sem agir agora)
- (ai-eng, 11/10 00:45) O panorama do boot NÃO carrega erros por tema do banco. Na plataforma-alvo, fraqueza = query sobre o Postgres (sinal determinístico, como o `db.get_erros_por_tema`), nunca memória de LLM. · (ai-eng, 11/10 ~13h) PRD da Fase 1 pronto em `C:/Users/daanm/ai-eng/.vibeflow/prds/medhub-fase1-ambiente-proprio-product-ready.md` (F1.0-F1.5); vira gen-spec meu só depois do G-fase. Consome da Fase 0: 1.4 (backup), Lote 2 (fontes estruturadas), Lote 4 (fuso, ids congelados, `cards_prune` sem DELETE), Lote 5 (custo por unidade).

## Decisões do operador (data · verbatim curto)
10/10 (no canal do ai-eng): i RAG/LangMem fora do caminho crítico SIM · ii purga/poda/gc SIM (após cópia off-machine) · iii cópia `ipub.db` = Drive + git privado ("drive e git") · iv ADR-006 ACEITO, opção A · v DISC §7: (1) produto, validado com ele primeiro -> infra product-ready, schema multi-tenant no Lote 4 · (2) terceiros "irrelevante": produto = provas públicas + cunhagem própria; cards = erros dos usuários; M-002 fecha como uso pessoal · (3) repo público por ora (conta Daktus), privado depois · (4) agente hospedado por ele, aditável; sem Managed Agents · (5) "não irei estudar hoje mais, portanto pode tocar nessa" -> tique desligado hoje, engenharia contínua.
10/10 (no chat do medhub): tique a 50 min só enquanto ele estuda; > 60 min com sessão ociosa sai mais caro (medição em `tmp/aieng/custo-tique-2026-10-10.md`).
11/10 ~13h (no canal do ai-eng): (1) repo privado `daanmt/backup-medhub` criado, "faça o que quiser com ele" -> G-op 1.4 destravado · (2) "PRDs e specs todas com o ai-eng; o medhub é o executor": a 1.1 fecha como está; da 1.2 em diante a spec vem do ai-eng · (3) migração só após 01/11; tique "não vamos mexer por hora"; limpeza AUTORIZADA "com o LangMem e afins" (RAG/Chroma/LangMem e módulos mortos saem, dados incluídos) num lote após a cópia off-machine conferida.

## Regras de retomada
🔴 **Depois de /clear, PRIMEIRO ato:** o /clear renomeia a sessão -- mandar 1 mensagem de presença ao `ai-eng-51` (SendMessage; achar o nome por `ListAgents`) citando este checkpoint e o último commit; ele passa a responder ao nome novo. Registrar `in`/`out` no exchange-log.
boot = este arquivo + `HANDOFF.md` 8 linhas -> abrir SÓ a spec da part em curso -> 1 subagente implementa (teste antes, vermelho visto; sem índice nem commit) -> audit do DoD pelo medhub -> regenerar §7.4 (`python -X utf8 tools/reachability_check.py --tabela`) se o teste de consistência acusar -> commit + push -> linha aqui -> msg ao ai-eng (`uds` do ai-eng-51; registrar `in`/`out` no `history/exchange-log.jsonl`) -> G-part (pode /clear).
`/clear` só em G-part. Tique: religar a 50 min só em dia de estudo (memória `feedback_tique_registra_e_analisa`).
