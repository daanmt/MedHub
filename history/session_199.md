# Session 199 -- Banco de questoes: Claude Code dirigindo o Chrome, elo erro -> card, Solucao MedHub

**Data:** 2026-09-26 (madrugada, ~00h40 -> 05h40 local; em curso) - **Ferramenta:** Claude Code (Opus 5.5 1M, `claude --chrome`) - **Continuidade:** `session_198.md`

---

## O que foi feito
- **Boot:** HANDOFF/AGENTE/s198 lidos; tools `mcp__claude-in-chrome__*` presentes (condicao (a) da s198); Bancada: t100 `em_curso` no executor da extensao com 0 questoes e sem mensagem nova; hub com so a t40 e 0 respostas. Operador pediu: *"continuar a sessao de engenharia, em que estamos ampliando o medhub para ter um bloco de questoes"*.
- **Piloto do Claude Code dirigindo o Chrome (t68, 21 q):** subagente isolado (web aberta = filho) leu a lista pela UI e gravou JSON local em `tmp/chrome/questoes/` -> `emed_banco.py --ingerir --apply --expect 21`. Funcionou; o painel da extensao fechado antes (1 piloto por vez). t100 devolvida a `pendente` e recapturada depois pelo mesmo caminho.
- **Elo erro -> card (`6dd7707`):** `insert_questao.py --sessao ID` grava `questoes_erros.sessao_bulk_id` (ALTER idempotente) e `--emed LISTA_NUM` grava `emed_respostas.questao_erro_id` pelo writer novo `db.emed_ligar_erro`, na MESMA transacao do erro (resposta inexistente, ja ligada ou certa-e-solida = nada gravado); lote aceita `sessao`/`emed`; `--erros` marca `JA REGISTRADA`. 13 testes escritos antes (`test_insert_questao_vinculo.py`).
- **API do EMED (pergunta do operador):** recusada por mim com o porque -- ler o token da sessao no navegador e credencial; seria o contorno da camada da extensao que o executor ja recusou; risco na conta dele; e a captura nao e o gargalo (91 capturadas, 0 respondidas). Ele concordou.
- **Solucao MedHub (decisao do operador, 26/09):** a solucao de cada questao e cunhada pelo hub, SEM ler o comentario do professor: 3-4 linhas (Pede / Decide / Gabarito / Cai), `divergente` + linha "Conferir" quando o raciocinio nao chega ao gabarito, diretriz so em afirmacao decisiva. Tabela `emed_solucoes` + `emed_banco.py --solucoes` + `--exportar` levando `solucao_medhub/divergente/fontes_medhub` fora do hash (`209c870`). Aba Questoes mostra o bloco "Solucao MedHub" com a etiqueta "conferir no professor"; comentario/forum somem quando vazios (`00e5ec0`).
- **Hub semeado e publicado (Version 22, `9ef7f88`):** o operador autorizou semear ("pode semear as listas no hub e publicar") depois de eu conferir, com `as_level: interact`, que quem abre o hub pelo link NAO le `listas/questoes`. Semeadas t26, t96, t49 (t49 10-21 ja existiam identicas), t68, t100, t3, t61. Publish pelo rito do `/hub-backend` (`--precisa-publicar` = `mesmo_lote`; lote `2026-09-26b` intocado; 7 regras mantidas). A 1a exportacao para semear foi NEGADA pelo classificador (continha `rm -rf`); nao reenquadrei -- perguntei e ele autorizou.
- **Fila de captura (semanas 2 e 3):** brief v2 -> v3.2 no scratchpad (gravar por questao; clique por ref; X do painel de solucao por coordenada quando o ref some -- o painel parece iframe; "Ver solucao" abre no 2o clique e antes mostra a questao ANTERIOR; discursiva nao entra; "(ADAPTADA)" com banca entra).
- **Tique `/banco-emed` religado** (`CronCreate` 4,19,34,49, job `b29d818c`, morre com a sessao): registrou 11 respostas da t96 (10/11; 5 solidas, 5 duvidas, 1 chute; erro Q8). Respostas do teste da t40 na s197 (ja fora do hub) tiradas da pasta local para nao registrar resposta inexistente.
- **Verificacao de evidencia:** a solucao da t100 citou "SBP mar/2026 unificada com o PNSF: ferro profilatico a partir dos 6 meses, 10-12,5 mg/dia em ciclos" -- confirmado no SENTIDO por evidence-researcher (pagina oficial da SBP, ~17/03/2026; PDF nao lido; confianca media). Banca-dependente para a UERJ 2026 (SBP 2018 = 3 meses, 1 mg/kg/dia).

## Listas (banco local / hub)
- t68 21 · t100 36 · t3 30 (+Q24 discursiva fora, `tmp/chrome_discursivas/`) · t61 15 · t651 30 (caderno tem 30, plano previa 43) -- capturadas nesta sessao; todas com Solucao MedHub exceto t651 (em curso). No hub: t26, t96, t40, t49, t68, t100, t3, t61 (362/5000 docs).
- Divergentes: t68 Q1, Q13 · t100 Q8, Q18, Q29, Q34 · t3 nenhuma · t61 Q11.
- Depois do 1o registro: t651 com solucao (1 divergente, Q20) e t141 capturada (24) + solucao (0 divergentes) semeadas no hub (10 listas, 418/5000 docs). t1 (MFC, 50 previstas) EM CURSO ao fechar o log (38 gravadas). Tique `/banco-emed` DESLIGADO as ~07h (cada disparo injeta ~5k tokens de skill; contexto em 78%). Suspeitos de gabarito requentado: t100 Q8, t68 Q13.
- `banco-emed: t68 ingerida 21 · t100 36 · t3 30 · t61 15 · t651 30; t96 registrada 11 (lista nao resolvida)`.

## Custo dos subagentes (usage do harness)
| Filho | Modelo | Tokens | Tools | Tempo |
|---|---|---|---|---|
| Captura t68 (piloto) | Sonnet | 358.241 | 182 | 30,6 min |
| Solucao t68 | Opus | 120.448 | 39 | 6,3 min |
| Captura t100 (v2) | Sonnet | 782.912 | 728 | 114,6 min |
| Solucao t100 | Opus | 168.009 | 41 | 12,3 min |
| Verificacao SBP 2026 (evidence-researcher) | Sonnet | 43.098 | 9 | 1,9 min |
| Captura t3 (v3) | Sonnet | 583.321 | 310 | 61,0 min |
| Solucao t3 | Opus | 117.985 | 16 | 6,1 min |
| Captura t61 (v3.1) | Sonnet | 282.639 | 212 | 28,9 min |
| Solucao t61 | Opus | 98.914 | 10 | 4,3 min |
| Captura t651 (v3.2) | Sonnet | 478.708 | 354 | 51,2 min |
| Solucao t651 | Opus | 161.152 | 28 | 9,4 min |
| Captura t141 | Sonnet | 438.491 | 325 | 48,0 min |
| Solucao t141 | Opus | 108.111 | 10 | 5,3 min |
Captura ~16-22k tokens por questao, 10-20 chamadas por questao (o modal de solucao e o custo). Solucao ~3-5k por questao. Alternativa de custo ~zero proposta ao operador (sem resposta ainda): PDF do caderno com gabarito, se o EMED oferecer.

## Incidente (t65)
- Durante a captura da t65 um clique por coordenada (painel de solucao fechando) marcou uma alternativa na conta do operador 2x; o subagente desmarcou na hora e o "Responder" nunca foi acionado. Captura PAUSADA ate ele decidir (regra dura no brief ou PDF com gabarito). Custo t65: 702.073 tokens · 600 tools · 85,8 min. t1: 523.992 · 396 · 45,3 min (47 q; Q23/24/46 discursivas); solucao t1: 146.682 · 21 · 8,2 min.

## Decisoes tomadas
- **Claude Code dirigindo o Chrome = caminho padrao da captura** (subagente isolado por lista, escopo publico, JSON local). A extensao com painel proprio sai do fluxo.
- **API interna do EMED: nao** (credencial do navegador + contorno da camada que recusou + risco da conta). Operador concordou.
- **Solucao MedHub sem o comentario do professor** (operador: "pode seguir sem ler o comentario").
- **Semear o hub:** autorizado explicitamente pelo operador; privacidade conferida por `as_level: interact`.
- **Discursivas ficam fora** da aba Questoes (o modo prova e por letra).

## Erros meus
- Horarios inventados (15:10Z, 16:00Z) em 2 updates da fila da Bancada; corrigidos com o `ingerido_em` real do banco.
- 2 commits bloqueados pelo hook: a tabela GERADA do AGENTE.md §7.4 (`reachability_check --tabela`) muda quando uma skill passa a citar mais CLIs; regenerar ANTES de commitar mudanca em skill.

## Proximos passos
- Seguir a fila: t141 (em curso) -> t1 -> t65 -> t819 -> t146 -> t63 (S2) -> S3 (t833, t112, t710, t832, t683, t75, t577, t376, t743, t122, t124, t127). Solucao + semeadura de cada uma.
- Quando ele marcar uma lista como resolvida: tique registra (bulk + `plano.py --concluir`) e analisa os erros com `insert_questao --sessao --emed` -> `analises/*` no hub. Ainda nao exercitado com dado real.
- Depois da fila: rodada de UI do hub com o feedback dele (listas, analises, experiencia).
- Card/resumo: ferro profilatico SBP 2026 x 2018 (banca-dependente); resumo de Pediatria.
