---
name: "source-command-hub-backend"
description: "Backend do MedHub HUB: 1 tique = conferir se o lote da aba Cards foi drenado e, se foi, gravar as notas e publicar a próxima fila do dia. Feito para rodar em /loop numa sessão do Claude Code deixada aberta no PC."
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

O rito de publicar é o do `/revisar` "DRENAR no player" (passos 1-5 e 7-8); aqui só se decide **quando** rodá-lo. Nada de prosa no chat além da linha final.

1. **Lote vivo:** o `sessao` está na linha 3 do `HANDOFF.md`; o lote é `tmp/player_<sessao>.json` (sem ele: `Artifact read` + `hub.py --extrair-lote`). `total` = nº de cards do lote.
2. **Estado:** `ArtifactData list` de `sessoes/<sessao>/notas` (limit 1000, `out_dir` em `tmp/player_<sessao>_db`). Drenado = todo `card_id` do lote tem doc (nota OU defeito).
   - **Não drenado -> no-op.** Linha `hub-backend: lote <sessao> em N/total -- nada a fazer` e fim do tique. 🔴 Nunca publicar com lote em curso: o reload no celular reapresentaria a fila no meio do drill.
3. **Gravar:** montar `tmp/player_<sessao>_notas.json` -> `fsrs_queue.py --record-lote` dry-run -> `--apply --expect N` com o N medido. Rejeitada ou FORA DE ORDEM vão para `history/quarentena/<sessao>.json` (o `--apply` arquiva) e entram no commit do passo 6.
4. **Próxima fila:** `fsrs_queue.py --export-player --sessao <AAAA-MM-DD><letra>` -- data de hoje + a próxima letra livre (`2026-09-23a`, `b`...; nunca reusar um `sessao`, é o nome da coleção). Sem `--limit`: o export corta no teto do dia. `total` 0 = teto batido -> publica mesmo assim (a aba mostra "Nenhum card para hoje").
5. **Publicar:** `Artifact list scope=files` do hub -> `hub.py --build --lote <novo> --publicado <listagem>` (`--check` OK) -> ler inteiro SÓ o que está em `files` -> `Artifact publish` na URL do HANDOFF, **sem `capabilities`** -> `hub.py --confirmar`. Publish recusado: não confirmar, relatar e parar o tique.
6. **Selar:** linha 3 do HANDOFF passa ao `sessao` novo; linha no session log do dia `hub-backend: <sessao velho> gravado (N validas · M quarentena) -> <sessao novo> no ar (K cards)`; commit + push só desses arquivos. A poda da coleção velha fica para o fechamento (`/revisar` passo 5).

## Limites declarados

- **Sem PC acordado, sem tique:** o celular vê o lote antigo até a próxima sessão abrir -- que começa pelo mesmo rito (`/revisar` passo 1).
- **Latência = intervalo do `/loop`** (20 min sugerido): não é instantâneo.
- **Permissão:** cada tique publica e grava FSRS sem o operador olhando. Se uma chamada pedir aprovação ou o classificador barrar, o tique **para e relata** -- nunca contorna.
- Tique em cima de lote que ainda recebe nota do celular: o dry-run do `--record-lote` é a janela; nota que chegar depois do `--apply` cai na coleção velha e é regravada pela releitura do fechamento (idempotente).
