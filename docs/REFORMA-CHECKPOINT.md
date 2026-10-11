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
| 1.4 cópia off-machine (PRIMEIRO no Lote 1) | `.vibeflow/specs/medhub-fase0-lote1-part-4.md` | PASS (código); a cópia real espera o G-op | 3f53136 | 1585/0/188 | adições (A) e (B) do ai-eng dentro; dry-run real N=49, 352,5 MB, backups + `ipub.db` idênticos, destino não criado; recusa `--dest` no repo público (até com caixa trocada); gate `BANCO_NO_RECORTE` no fluxo real: o `git add` foi recusado pelo gitignore e o commit com `-f` BLOQUEADO só por ele, HEAD intacto, revertido; §7.4 regenerada (1 linha + 6 contadores) |
| 1.0 RAG/LangMem fora do caminho crítico | `.vibeflow/specs/medhub-fase0-lote1-part-0.md` | PASS | bcb02bf | 1587/0/190 | baseline em `tmp/lote1/part-0-baseline.md`: boot 3,111 -> 2,538 s (mediana de 5, banco sintético); import 635 -> 84 ms (langgraph 546 ms saiu; langmem/chromadb/ollama/anthropic já não entravam); contexto 11.883 -> 8.885 bytes (o bloco = 25%); última consolidação 07/10 (selo da s220) x 182 sessões. `settings.json`: só a entrada Write saiu (diff conferido). Revogação em 3 passos (AGENTE §2.7 e §8 + 2 termos); desvio: 7 arquivos, com `registrar-sessao.md` §4/§5 lapidados no mesmo commit (§10.10) |
| 1.1 P5 figuras · 1.2 P2 `versao` + gate · 1.3 P6 âncora | gen-spec do medhub | pendente | | | |
| 2.x P1 · 3.x hub+contratos · 4.x dados (multi-tenant) · 5.x medições | idem | pendente | | | |

## Próximo ato (1 linha)
operador: criar o repo git PRIVADO e o clone local fora de `C:/Users/daanm/medhub` (G-op 1.4) -> medhub roda `python tools/backup_offmachine.py --dest <clone> --apply --expect 49`; em paralelo, medhub gera a spec da 1.1 (P5 figuras) e manda ao ai-eng.

## Dívida nascida no Lote 0 (dono medhub, -> Lote 3; linhas em `docs/BACKLOG-UNICO-MEDHUB.md`)
- **M-120** leitor do `ipub.db` real em `mode=ro` para os testes `vivo` (audit da 2a).
- **M-121** inventário dos módulos com `DB_PATH` próprio: `review_radar`, `variancia` e os que o sentinela achar (audit da 2c; confirmado pelo ai-eng 10/10).
- **M-128** `get_caderno_erros`, a 11ª função morta do `db.py`, fora da lista da 0.4a (fecho).
- **M-131** `tmp/` SOLTO (17.189 arquivos, 40,2 MB): inventário + regra de vida do `tmp/`.
- **M-132** Pattern Registry do `.vibeflow/index.md` x frontmatter de 5 patterns: o registry vira DERIVADO do frontmatter por ferramenta, com sensor (achado do 1.pre).
- **M-133** Anti-patterns manuais velhos (`domain-engine-api:106`, `agent-workflow-protocol:91-92`, `error-insertion-pipeline:137`), mesma classe do M-127.
- **M-137** `.agents/workflows/` fora dos portadores que o `CONTRATO_REVOGADO` vigia (classe do M-122: o sensor existe, o caminho não chega).
- **M-138** flag `--delete-pdfs` viva no `extract_pdfs.py`: remédio preferido = recusar salvo `--confirmo-apagar` explícito (não remover).
- **M-135** frontmatter legado de `resumos/GO/Assistência ao Parto.md` (quando a referência for tocada ou no inventário de frontmatter).
- (Lote 4 / Fase 1) **M-136** retenção do repo privado: cada cópia off-machine pesa ~352 MB, e a recorrência ficou fora da 1.4 (ex.: 1 cópia por semana depois de 30 dias).
- **M-134** FECHADO em `55d1144` (11/10): a deleção do PDF-fonte saiu do fluxo (`criar-resumo` passo 8, skill `/extrair-pdf`, `AGENTE.md` §6 e §7.3) pelo §10.10 em 3 passos; termo `--delete-pdfs` vigiado pelo `CONTRATO_REVOGADO`. Default não destrutivo do operador (retenção da s086). Achado: o `.agents/workflows/` não está entre os 31 portadores que o gate vigia.
- (fora do Lote 3) **M-129** = condição do G-op da 0.4b (a rotação pós-apply apaga 49 de uma vez); **M-130** `tmp/alca_s213` (268,8 MB, CITADO só por 1 audit) = decisão do OPERADOR, quem pergunta é o ai-eng; não tocar.

## Gates abertos
- G-op 0.4b apply: só depois da 1.4 com md5 dos 48 conferido (M-129). 🔴 Medido no dry-run: os 5 backups de rotação são de 26/09 a 07/10, mais velhos que os fixados de 09/10 que voltariam à rotação. Depois do apply, o próximo `backup()` guarda o novo + 4 desfixados de 09/10 e apaga 49 de uma vez, inclusive os 5 de rotação de hoje. No disco ficam só pontos de 09/10 e 10/10. Comando: `python tools/backup_db.py --desfixar-lote --manter 5 --motivo "..." --apply --expect 48`.
- G-op 1.4: criar o repo git PRIVADO e a credencial (operador).
- G-op `tmp/`: limpeza só da classe SOLTO, depois do GO (inventário em `tmp/lote0/part-4b-tmp-inventario.md`); `alca_s213/` = M-130.
- (fechado 10/10 ~13:55) i e ii confirmadas por ele no chat do medhub: *"já foi respondido no ai-eng. se alinhem."* -- decisão dada no canal do ai-eng com verbatim vale; não re-perguntar.
- (fechado no `beebc04`) Achados do audit da 0.3 com GO do ai-eng (10/10 21:17) para o hotfix **0.3h**, antes da 0.4a: **M-122** = `gate_inexistente`/`nv_sem_data` imprimem `[BLOCK]` mas nunca fazem `all_passed=False`, então não bloqueiam o commit desde `9ea675a` (s187); medido antes do fix: 0 e 0 no HEAD. **M-123** = `GIT_INDEX_FILE` herdado do pre-commit na suíte (exposto `tools/test_emed_api.py` ~383) -> fixture de sessão no `conftest.py` + regressão empírica. Novos membros da classe "`[BLOCK]` que não zera `all_passed`" -> M-125.

## Limites conhecidos (aceitos pelo ai-eng; revisar na data)
- 0.3 DoD 4: `banco-emed.md:154` (Figura, s221) com `NAO-VERIFICAVEL`. O teste da figura prova só a URL em `figuras`; "nunca este script baixa" não tem sensor. Revisar **2026-12-31** (P5 do Lote 1). D83, 3º destino.
- Fecho do Lote 0: `conventions.md:54` (dentro de `auto`) saiu no 1.pre (`4300bed`); `.vibeflow/index.md:177` (era a 169) é registro riscado de achado resolvido e fica: é o único resto do doc_drift em `.vibeflow/`.

## Notas de design para a Fase 1 (sem agir agora)
- (ai-eng, 11/10 00:45) O panorama do boot NÃO carrega erros por tema do banco. Na plataforma-alvo, fraqueza = query sobre o Postgres (sinal determinístico, como o `db.get_erros_por_tema`), nunca memória de LLM.

## Decisões do operador (data · verbatim curto)
10/10 (no canal do ai-eng): i RAG/LangMem fora do caminho crítico SIM · ii purga/poda/gc SIM (após cópia off-machine) · iii cópia `ipub.db` = Drive + git privado ("drive e git") · iv ADR-006 ACEITO, opção A · v DISC §7: (1) produto, validado com ele primeiro -> infra product-ready, schema multi-tenant no Lote 4 · (2) terceiros "irrelevante": produto = provas públicas + cunhagem própria; cards = erros dos usuários; M-002 fecha como uso pessoal · (3) repo público por ora (conta Daktus), privado depois · (4) agente hospedado por ele, aditável; sem Managed Agents · (5) "não irei estudar hoje mais, portanto pode tocar nessa" -> tique desligado hoje, engenharia contínua.
10/10 (no chat do medhub): tique a 50 min só enquanto ele estuda; > 60 min com sessão ociosa sai mais caro (medição em `tmp/aieng/custo-tique-2026-10-10.md`).

## Regras de retomada
🔴 **Depois de /clear, PRIMEIRO ato:** o /clear renomeia a sessão -- mandar 1 mensagem de presença ao `ai-eng-51` (SendMessage; achar o nome por `ListAgents`) citando este checkpoint e o último commit; ele passa a responder ao nome novo. Registrar `in`/`out` no exchange-log.
boot = este arquivo + `HANDOFF.md` 8 linhas -> abrir SÓ a spec da part em curso -> 1 subagente implementa (teste antes, vermelho visto; sem índice nem commit) -> audit do DoD pelo medhub -> regenerar §7.4 (`python -X utf8 tools/reachability_check.py --tabela`) se o teste de consistência acusar -> commit + push -> linha aqui -> msg ao ai-eng (`uds` do ai-eng-51; registrar `in`/`out` no `history/exchange-log.jsonl`) -> G-part (pode /clear).
`/clear` só em G-part. Tique: religar a 50 min só em dia de estudo (memória `feedback_tique_registra_e_analisa`).
