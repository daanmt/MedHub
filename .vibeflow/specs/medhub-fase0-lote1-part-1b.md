# Spec: medhub Fase 0 · Lote 1 — Part 1.1b: recaptura das figuras (t40 + S4-S7) e o aviso no hub

> Gerada: 2026-10-11 ~12:15 (medhub, s223, `/vibeflow:gen-spec`) | Origem: M-042 (P5), 2ª metade. Pré-requisito: **1.1a em PASS** (`sem_figura`, `figuras_alt`, `db.emed_mesclar_figuras`, `emed_banco.py --figuras` e `--so-figuras`).
> Repo-alvo: medhub. Executor: o **filho** faz só o código do hub (DoD 1). A operação (DoD 2-5) é do **orquestrador**: ela usa a credencial do EMED e escreve no `ipub.db` real e no hub. O token nunca aparece em log, relatório, mensagem ou commit.

## Objective

As questões que o operador ainda vai resolver (S4-S7) e a t40 chegam ao hub com a figura, ou com a perda declarada na tela. O antes e o depois ficam medidos por lista.

## Context

- O hub renderiza `figuras_img` do doc `questoes/<lista>_<num>` em `core/templates/hub.html`. Não há aviso para questão sem figura.
- As listas da S4-S7 no hub foram quase todas capturadas pela API em 07/10, antes da s221 (sem `figuras`). t1 e t40 são da era Chrome (26/09).
- O token do EMED é de 27/09. Se expirou, a captura recusa (401/403) e o operador renova pelo rito da skill `banco-emed`. Ninguém o lê, imprime ou move.

## Definition of Done

1. [ ] **(filho) Aviso no hub.** Doc com `sem_figura: true` mostra, acima das alternativas, 1 linha discreta: "A figura desta questão não veio na captura." Ela segue o design minimalista do hub, com tokens de cor existentes e sem layout novo. Doc com `figuras_alt` + `figuras_img_alt`, se a 1.1a/1.1b os embutir, mostra a imagem na alternativa.
   - Teste de render (arquivo existente de teste do hub, ex.: `tools/test_hub_render.py`), visto VERMELHO antes.
   - Conferido em navegador real a 390 px (`hub` em scratch + db falso), conforme a memória "tela nova só publica conferida".
2. [ ] **(orq.) Recorte declarado antes de capturar.** `tmp/lote1/part-1b-recorte.md` lista as listas do recorte, com tarefa, semana, executor/data da captura atual e nº de docs no hub. O recorte é a **t40** mais toda lista do hub cuja tarefa está PENDENTE nas semanas 4-7 (`plano.py --listar --semana N --status pendente`). Listas já resolvidas, fora a t40, ficam fora (anti-scope) e só aparecem contadas.
3. [ ] **(orq.) Antes, medido.** Por lista do recorte, lido do `ipub.db` em `mode=ro`: docs, docs com `figuras`, e suspeitos do `CITA_FIGURA` sem `figuras`. Tudo numa tabela em `tmp/lote1/part-1b-figuras.md`, com o comando de cada número e o md5 do `ipub.db` antes.
4. [ ] **(orq.) Recaptura com rito, lista a lista.**
   1. `emed_api.py --lista tX --out tmp/lote1/p1b/tX`: dry-run -> `--apply --expect N`.
   2. `emed_banco.py --figuras tmp/lote1/p1b/tX`: dry-run -> `--apply --expect M`.
   3. `--exportar --so-figuras`.
   4. `ArtifactData batch update` (nunca `set`) só dos campos de figura, com `if_version` = a `version` do doc lido nesta rodada. O join `upd` -> doc do hub é por `emed_id`.
   - Uma divergência `emed_id` x doc vira linha `ausente` no relatório, nunca doc novo.
   - Update recusado por versão = reler e refazer, nunca forçar.
   - Doc do hub > 256 KiB depois do merge = não gravar, só relatar.
   - 401/403 da API = PARAR a part e pedir ao operador a renovação do token. Não é desvio que o audit fecha: é bifurcação "credencial/token", e o ai-eng é avisado.
5. [ ] **(orq.) Depois, medido e conferido.**
   - A mesma tabela, lado a lado: com `figuras`, `sem_figura` declarado e `ausentes`.
   - Para a t40, as Q5, Q6, Q18, Q21 e Q22 nomeadas uma a uma: figura chegou ou perda declarada.
   - Precisão do `CITA_FIGURA` numa amostra de 20 `sem_figura`, lidos pelo orquestrador: quantos citam figura de verdade. Se der < 70%, o padrão é apertado num hotfix com teste, e a medição repete.
   - Lista das questões que ganharam figura e já têm Solução/cadeia escrita "pelo texto" -> linha nova no backlog (regenerar), sem regenerar aqui.
   - Republicar o hub pelo rito do `/hub-backend` passo 7 só se o build mudar (o aviso do DoD 1 está na página). Os docs de `questoes` já foram atualizados pelo `batch update`.
6. [ ] **Suíte e craftsmanship:** `python -m pytest tools/ -q` verde. O md5 do `ipub.db` muda só pelo `--figuras --apply`, com backup fixado registrado. Nenhum arquivo de captura (`tmp/lote1/p1b/`) entra no git. `BANCO_NO_RECORTE` verde.

## Scope

Código (filho): `core/templates/hub.html` e 1 arquivo de teste do hub existente. **Budget: 2 arquivos.** Operação (orquestrador): dados no `ipub.db` e no hub, relatórios em `tmp/lote1/`, linha no checkpoint e no backlog.

## Anti-scope

- Listas resolvidas fora a t40 (t26, t49, t96, t100, t530, t875, t1793...): só contadas. A recaptura delas é item de backlog.
- Não regenerar Soluções/cadeias; não reanalisar erro da t40. Se a figura mudar a leitura de uma questão errada, vira pergunta fechada a ele no hub (`analises/pendencias/itens`), sem análise por inferência.
- Não trocar o lote de cards nem mexer na aba Cards.
- Não abrir nem capturar simulado UERJ (o spoiler segue filtrado pelo `emed_api`).

## Technical Decisions

1. **Operação pelo orquestrador, não pelo filho.** Ela usa a credencial do operador e escreve no banco real e no hub compartilhado. O filho fica com o código testável.
2. **`batch update` por campo, não `batch set`.** `set` troca o doc inteiro e apagaria `solucao_medhub`/cadeia já gravados.
3. **Recorte = o que ele ainda vai resolver + a t40.** A figura serve na hora de resolver. Lista resolvida ganha pouco hoje e entra no backlog.

## Risks

- **"Token expirado no meio."** -> DoD 4: parar e pedir; as listas já mescladas ficam (cada uma fecha seu ciclo).
- **"Ele está resolvendo uma lista enquanto o update chega."** -> O `if_version` protege o doc, e as respostas moram em `respostas`, coleção separada. Mesmo assim, evitar a lista aberta no momento (ver `listas/<id>.status`).
- **"Doc estoura 256 KiB com a figura da alternativa."** -> Não gravar e relatar; a decisão de embutir ou não a alternativa fica medida.

## References

- Spec irmã `.vibeflow/specs/medhub-fase0-lote1-part-1a.md`.
- `.claude/commands/banco-emed.md:43`, `:88`, `:197-198`, `:225` (set no 1º publish, update da solução).
- Skill `hub-backend` passo 7 (publicar) e a memória "conferir tela no navegador".
