---
name: "source-command-hub-backend"
description: "Backend do MedHub HUB: 1 tique = conferir (hub.py --precisa-publicar) se o lote da aba Cards foi drenado -- e aí gravar as notas e publicar a próxima fila do dia -- ou se o painel/quadro mudou, e aí republicar com o mesmo lote. Feito para rodar em /loop numa sessão do Claude Code deixada aberta no PC."
---

<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI.
     Edite `.claude/commands/hub-backend.md` e rode `python tools/sync_skills.py`.
     Qualquer edicao feita neste arquivo e SOBRESCRITA no proximo sync. -->

# source-command-hub-backend

Use this skill when the user asks to run the migrated source command `hub-backend`.

## Command Template

# Skill: Hub backend (tique do `/loop`)

> **Uso:** `/loop 20m /hub-backend` numa sessão do Claude Code aberta no PC, com o PC acordado. Cada disparo é UM tique, idempotente. Origem: s194, decisão do operador em 23/09/2026 -- *"um hook que checa o estado da sessão de flashcards no player e, se pronta, já prepara a próxima fila do dia"*.
>
> ⚰️ **Por que não é o botão "Pedir mais cards" (`comments.sendToClaude`):** foi a 1ª opção do operador. O classificador do modo automático barrou a construção ("Create Unsafe Agents"): uma página acionando um agente que grava e publica sem supervisão. O tique é o mesmo rito, disparado por um `/loop` que o operador liga, sobre um sinal que a página já produz (o lote drenado) -- sem capability nova no hub. O patch do botão ficou em `tmp/patch_s194_pedido_cards.diff` (fora do git).

## O tique

O rito de publicar é o do `/revisar` "DRENAR no player" (passos 1-5 e 7-8); aqui só se decide **quando** rodá-lo -- e quem decide é o CLI, não raciocínio ad hoc. Nada de prosa no chat além da linha final.

1. **Lote vivo:** o `sessao` está na linha 3 do `HANDOFF.md`; o lote é `tmp/player_<sessao>.json` (sem ele: `Artifact read` + `hub.py --extrair-lote`).
2. **Estado no `db`:** `ArtifactData list` de `sessoes/<sessao>/notas` (limit 1000, `out_dir` em `tmp/player_<sessao>_db`) e da coleção `quadro` (`out_dir` em `tmp/hub_db`).
3. **Painel fresco:** `python tools/painel.py --html` (a hora de geração não conta na comparação).
4. **Decidir:** `python tools/hub.py --precisa-publicar --lote tmp/player_<sessao>.json --notas tmp/player_<sessao>_db --quadro-estado tmp/hub_db` -> `sim|nao`, a `acao` e o motivo:
   - **`nada`** -> linha `hub-backend: lote <sessao> em N/total, projeção igual -- nada a fazer` e fim do tique.
   - **`mesmo_lote`** (lote em curso, mas o painel ou o quadro mudou) -> passo 7 com o **MESMO** `tmp/player_<sessao>.json`: mesmo `sessao`, mesmos cards; as notas já dadas voltam do `db` no reload do celular. A linha 3 do HANDOFF **não** muda. 🔴 Nunca trocar lote em curso: o reload reapresentaria a fila no meio do drill.
   - **`nova_fila`** (lote drenado, ou vazio) -> passos 5-7.
   - **Aula feita com tarefa pendente** (linha `aula feita no quadro com tarefa pendente: #N`): `python tools/plano.py --concluir N --leitura` (decisão do operador, s194: o "feito" do quadro É a confirmação de leitura). O CLI recusa tarefa com lista ou questões previstas -- recusa = relatar no session log e seguir, nunca forçar com `--sessao` inventado. Concluir muda o painel: o próximo tique republica.
5. **Gravar:** montar `tmp/player_<sessao>_notas.json` -> `fsrs_queue.py --record-lote` dry-run -> `--apply --expect N` com o N medido. Rejeitada ou FORA DE ORDEM vão para `history/quarentena/<sessao>.json` (o `--apply` arquiva) e entram no commit do passo 8. Lote vazio: nada a gravar. Depois de gravar, **`painel.py --html` de novo** (o saldo de cards mudou).
6. **Próxima fila:** `fsrs_queue.py --export-player --sessao <AAAA-MM-DD><letra>` -- data de hoje + a próxima letra livre (`2026-09-23a`, `b`...; nunca reusar um `sessao`, é o nome da coleção). Sem `--limit`: o export corta no SALDO do dia (teto menos as revisões já gravadas hoje -- `consumo_hoje` na saída). **Fila de véspera** (saldo de hoje zerado e ele vai drenar de manhã sem o PC): `--export-player --para <amanhã> --sessao <amanhã>a` -- o relógio anda para as 06:00 de amanhã (buckets, teto, consumo 0, previsões), NUNCA `--limit` de véspera: o lote de hoje-à-noite não vê o que vence amanhã e a agenda da tela de fim sai deslocada (F131). A saída traz `retidos_reforja` (cards com defeito marcado que a fila segura até a reforja, F132). `total` 0 = saldo zerado: se o lote da aba também está vazio, apagar o export e seguir com o lote **atual** (vazio) -- publicar só se o `--precisa-publicar` tinha apontado painel ou quadro mudado; senão, no-op. No dia seguinte o saldo volta e o 1o tique publica a fila nova.
7. **Publicar:** `Artifact list scope=files` do hub -> `hub.py --build --lote <lote do passo 4 ou 6> --publicado <listagem> --quadro-estado tmp/hub_db` (`--check` OK) -> ler inteiro SÓ o que está em `files` -> `Artifact publish` na URL do HANDOFF, **sem `capabilities`** -> `hub.py --confirmar` (grava também a projeção publicada: é a base do próximo `--precisa-publicar`). Publish recusado: não confirmar, relatar e parar o tique.
8. **Selar:** lote novo -> a linha 3 do HANDOFF passa ao `sessao` novo; linha no session log do dia (`hub-backend: <sessao velho> gravado (N validas · M quarentena) -> <sessao novo> no ar (K cards)` ou `hub-backend: republicado com o mesmo lote <sessao> (<motivo>)`); commit + push só desses arquivos. A poda da coleção velha fica para o fechamento (`/revisar` passo 5).

**Declaração de capabilities do hub (s194, com o quadro; s197, com a aba Questões):** `{db: {rules: [{path: "", read: "view", write: "admin"}, {path: "sessoes", write: "interact"}, {path: "quadro", write: "interact"}, {path: "listas", read: "admin", write: "admin"}, {path: "questoes", read: "admin", write: "admin"}, {path: "respostas", read: "admin", write: "admin"}, {path: "analises", read: "admin", write: "admin"}]}}` -- as 4 coleções do EMED só o dono lê (o hub é compartilhado por link). O tique **nunca** a passa (publica sem `capabilities`, que mantém a declarada); quem a publica é o agente principal, uma vez. Se o publish do tique voltar sem a regra `quadro` (o controle "feito" desabilitado no hub), o tique relata -- não declara.

## Limites declarados

- **Sem PC acordado, sem tique:** o celular vê o lote antigo até a próxima sessão abrir -- que começa pelo mesmo rito (`/revisar` passo 1).
- **Latência = intervalo do `/loop`** (20 min sugerido): não é instantâneo.
- **Permissão:** cada tique publica e grava FSRS sem o operador olhando. Se uma chamada pedir aprovação ou o classificador barrar, o tique **para e relata** -- nunca contorna.
- Tique em cima de lote que ainda recebe nota do celular: o dry-run do `--record-lote` é a janela; nota que chegar depois do `--apply` cai na coleção velha e é regravada pela releitura do fechamento (idempotente).
