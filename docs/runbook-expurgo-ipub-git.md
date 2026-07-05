---
type: runbook
layer: docs
status: GATED
relates_to: [AUDITORIA_MEDHUB]
---

# RUNBOOK -- Expurgo do blob ipub.db do historico git (F11)

> **GATED -- NAO EXECUTAR SEM AVAL EXPLICITO DO OPERADOR.**
> Reescreve o historico do repositorio: todo clone existente diverge e precisa
> ser re-clonado. Operacao Tier 3. Este runbook transforma a decisao futura em
> execucao de ~10 minutos, sem re-investigacao.

## Contexto (verificado 2026-07-05)

- `ipub.db` (SQLite local-only, ~1.6 MB) foi versionado por engano ate a
  sessao 058 (ultimo blob no commit `d99ff02`). Hoje esta no `.gitignore` e
  untracked, mas o blob persiste no historico -- todo clone carrega ~1.6 MB
  de dado local-only que nunca deveria ter subido.
- Verificacao do estado atual: `git log --all --oneline -- ipub.db`
  (lista os commits que tocaram o arquivo).

## Pre-condicoes (todas obrigatorias)

1. Aval explicito do operador NESTA janela (nao vale aval antigo).
2. Working tree limpo (`git status --porcelain` vazio) e tudo pushado.
3. Backup fisico do repo: copiar a pasta inteira (ou `git clone --mirror` para
   um caminho de backup) ANTES de qualquer passo.
4. Nenhum clone divergente ativo em outra maquina (confirmar com o operador).
5. `git filter-repo` instalado (`pip show git-filter-repo`; instalar e uma
   dependencia nova -> tambem gated).

## Passos

1. Backup: `git clone --mirror . ../medhub-backup-pre-expurgo.git`
2. Expurgo: `git filter-repo --invert-paths --path ipub.db --force`
3. Conferir: `git log --all --oneline -- ipub.db` deve sair VAZIO.
4. Re-adicionar o remote (filter-repo remove): `git remote add origin <url>`
5. Push forcado (reescreve o remote): `git push --force --all` e
   `git push --force --tags`
6. Validar num clone fresco: clonar em pasta temporaria e conferir tamanho +
   `git log --all -- ipub.db` vazio.
7. Descartar/re-clonar qualquer copia antiga do repo em outras maquinas.

## Rollback

O backup do passo 1 e o repo integro pre-expurgo. Para reverter:
restaurar o mirror (`git clone ../medhub-backup-pre-expurgo.git`) e forcar
push do estado antigo.

## Pos-execucao

- Registrar no ledger `AUDITORIA_MEDHUB.md` (F11 -> RESOLVIDO, com data).
- Registrar em `history/session_NNN.md` da sessao que executar.
