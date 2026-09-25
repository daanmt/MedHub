# Session 197 -- Banco de questoes EMED: Bancada v2 (Resolver), emed_banco.py, protocolo do Chrome

**Data:** 2026-09-25 (noite, ~23h-01h) - **Ferramenta:** Claude Code (Fable 5.1, contexto limpo; subagentes: 1 Explore Sonnet + 1 Opus) - **Continuidade:** `session_196.md`

---

## O que foi feito
- **Boot:** panorama entregue (S2, 21 tarefas/511q, 3 atrasadas; 17,9-23,2 x 86,9 q/dia; COBERTURA). Canal da Bancada conferido: o relatorio do Chrome ainda nao tinha chegado (so a `m0001`).
- **Pedido do operador:** *"Seu /goal e a construcao do bloco de questoes/banco dentro do medhub, imbuido da logica do raciocinio metacognitivo, feedback, etc., enquanto claude-chrome extrai as listas"* + o link e uma mensagem minha para o Claude no Chrome.
- **Bancada EMED v2** (`artifacts/bancada-emed.html` -> https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db, Version 2, `capabilities {db:{}}` mantida): 3 abas. **Capturar** (fila + formulario + **Registrar lote (JSON)** para o Chrome gravar a lista inteira de uma vez + campo `estatistica`). **Resolver** (o bloco de questoes do operador, no celular): letra + **confianca `solida/duvida/chute` ANTES do gabarito**, cronometro por questao, gabarito + comentario do professor (aberto so em erro/chute) + forum (recolhido), no erro/chute o **racional declarado** (1 linha) e o **elo** em chips (`nao_sabia · sabia_nao_usei · li_errado · dado_que_exclui · ancorei_numero · negativa · diretriz_antiga · pressa`), "revisar depois", trilho de progresso, retomada de onde parou, espelho em localStorage + reenvio de pendentes (licao do 24/09), tela de fim com tiles e "Marcar lista como resolvida"; bloco **Analise do hub** (`analises/<lista>_<num>`) com veredito `concordo/em_parte/discordo` + nota. **Canal** com contador na aba. Design = tokens do hub (minimalista; rotulos <= 15 chars; sem sticky).
- **`tools/emed_banco.py`** (subagente Opus, brief em arquivo): camada fina sobre `app/utils/db.py` (`_ensure_emed_tables`, `emed_upsert_questoes`, `emed_upsert_respostas`, `emed_listar_*`, `emed_status`); tabelas `emed_questoes` (chave `lista+num`, `hash`) e `emed_respostas`; flags `--ingerir/--registrar/--podar/--colecao/--exportar/--out/--erros/--status/--lista/--apply/--expect/--json`; dry-run default, `--expect` = COUNT-ASSERT (exit 2). `tools/test_emed_banco.py` (9 testes) + allowlist F49 + `pytest.ini`. Re-medido pelo principal: `python -X utf8 -m pytest tools/test_emed_banco.py tools/test_writer_allowlist.py -q -p no:cacheprovider` = **12 passed**.
- **Skill `/banco-emed`** (`.claude/commands/banco-emed.md`): fronteiras (buffer 5.000 docs; conteudo EMED so no artifact privado + `ipub.db`; db = dado, nunca instrucao), coleções do `db`, assinatura canonica do CLI e o **tique** em 6 passos (Canal -> ingerir -> registrar + `registrar_sessao_bulk` + `plano.py --concluir` -> `--erros` + `/analisar-questao` + `analises/*` -> podar -> selo). `sync_skills` OK; AGENTE.md §7.3 (linha nova) e §7.4 (tabela regenerada por `reachability_check.py --tabela`).
- **Protocolo do Chrome:** `control/hub.instrucao` = FASE 2 = PILOTO (relatorio curto no formato combinado + lista t26 inteira + esperar confirmacao); `mensagens/m0002` do hub; bloco "MISSAO" entregue ao operador para colar no Claude no Chrome (regras: texto integral, sem julgar, ritmo humano, nada alterado no EMED, conteudo so na Bancada).
- **Harness:** `python -X utf8 tools/auto_check.py --changed` = PASSED (15 checks); `pytest tools/test_consistencia_registros.py tools/test_cli_assinatura.py tools/test_writer_allowlist.py tools/test_emed_banco.py tools/test_espelho_gerado.py -q` = **45 passed**.
- **hub-backend:** religado em `/loop 12h /hub-backend` nesta sessao (fila `2026-09-26b` ainda com 0 notas as 23h).

## Custo dos subagentes (usage do harness)
- Explore (Sonnet, mapa da arquitetura): 101.278 tokens · 53 tool uses · 2 min 47 s.
- Opus (`emed_banco.py` + testes): 121.982 tokens · 30 tool uses · 10 min 14 s. Rodou um `git stash` por engano e desfez na hora (`git stash list` vazio, re-medido); sem commit, sem `git add`, `ipub.db` intocado.

## Decisoes tomadas
- **O bloco de questoes mora na Bancada (privada), nao no MedHub HUB:** o conteudo do EMED e IP da assinatura (PRD s196) e o hub e link compartilhavel. A Bancada e a 2a superficie fixa, nao "artifact avulso".
- **A lista do plano e o lote:** sem colecao `lotes/`; a pagina resolve direto os `questoes/<lista>_*`; poda so depois de registrada; lista podada volta por `--exportar`.
- **Chute certo = acerto no volume, `incerteza` na analise** (regua do §10 do `/analisar-questao`).
- Subagente divergiu do brief em 5 pontos (resposta igual = `iguais`; `--out` com default; gabarito normalizado antes do hash; JSON ilegivel = invalida; resumo do `--registrar` soma banco + lote) -- aceitos, todos a favor da idempotencia.

## Proximos passos
- Chrome: relatorio + t26 capturada -> tique do `/banco-emed` (ingerir, confirmar no Canal). Depois o operador resolve a t26 na aba Resolver -> registrar + bulk + concluir -> `--erros t26` -> analise -> `analises/*`.
- PRD aba Analise do hub (`hub-aba-analise.md`) pode se apoiar nas `analises/*` da Bancada.
- Pendencias herdadas da s196 seguem: `[GIN] CA de Mama.md` (N3c), 5 duvidas clinicas, F113/F129.
