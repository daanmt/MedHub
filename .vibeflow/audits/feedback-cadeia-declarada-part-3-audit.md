## Audit Report: feedback-cadeia-declarada part-3 (modo Estudo/Prova + tela de fim com os elos)

> Auditado em 2026-10-02 (s211), subagente de implementação. Spec: `.vibeflow/specs/feedback-cadeia-declarada-part-3.md`.
> Dependência: part-2 PASS (commit `d52aca7`).

**Verdict: PASS**

### DoD Checklist

- [x] **1. Escolha do modo.** Lista (não simulado) sem `modo` e sem resposta mostra `#qz-modo-escolha` (Estudo: "gabarito e cadeia
  a cada questão" · Prova: "tudo no fim, como no dia") antes da 1ª questão (`qzPosicionar` + `qzEscolheModo`). A escolha grava
  `listas/<id>.modo` (`update`) e o espelho `medhub.listas.modo.<id>` (`qzEscolher`). Com `modo`, abre direto; o botão da barra
  (`#qz-modo-lista`, "Modo estudo"/"Modo prova") troca. Simulado: `qzModoDaLista` -> sempre `prova`, sem escolha e sem controle.
  Testes: `test_simulado_e_sempre_prova`, `test_modo_da_lista_vem_do_doc_e_do_espelho` (doc vence o espelho; espelho cobre db
  fora; lista antiga com respostas não pergunta).
- [x] **2. Fluxo Estudo.** `qzResponder()` (extraída do listener) grava `modo: "estudo"` e chama `qzRevelar` no lugar; em Prova grava
  `modo: "prova"` e segue `qzDepoisDe` (fluxo de hoje). `Próxima` em Estudo -> `qzDepoisDe` (a próxima não respondida, inclusive as
  puladas). Respondida em Estudo (ou lista em Estudo) reabre revelada e não editável (`qzRevelaAoAbrir` no fim de `qzMostrar`).
  Teste: `test_estudo_revela_apos_responder_e_prova_nao`.
- [x] **3. Obrigatoriedade.** `qzTrava(q, r)`: em Estudo com `qzDeclPendente`, `Próxima` desabilitada + "Declare os elos para seguir.";
  o handler de `Próxima` e o atalho `Enter` conferem `disabled`. Fim: `qzConcluirUi(n)` desabilita "Concluir lista" com
  "Faltam N declarações." (contagem de QUESTÕES pendentes). Sem cadeia nunca pendente; `cadeia_defeito` com motivo conta como
  declaração. Testes: `test_pendencia_trava_proxima_e_concluir`, `test_questao_sem_cadeia_nao_trava`.
- [x] **4. Tela de fim com os elos.** `qzResumoElos(qs, resp)` (pura: contagem por estado, presumido = Sim; itens `nao` ->
  `incerteza` -> `desatencao`, na ordem das questões; pendentes) e `qzElosFimHtml` (bloco "Elos" depois de "Por objetivo", cada linha
  `Q<num>` + frase do elo + estado, tocável -> `qzRever`). Revisão marca "· declarar" nas pendentes. Testes:
  `test_resumo_dos_elos_na_ordem_de_revisao`, `test_fim_elos_golden` (golden `fim_elos.html`).
- [x] **5. Textos.** `QZ_SUB` e o parágrafo do fim reescritos, 2 frases cada, sem "confirma o elo que quebrou"
  (`test_textos_da_aba_curtos_e_sem_o_elo_que_quebrou`).
- [x] **6. Harness e forma.** `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> **1330 passed**; `hub.py --build ... --out
  <scratchpad>` -> `--check: OK`; `node --check` do JS montado -> OK; `auto_check --changed` exit 0; `sync_skills --check` 0.
  `test_forma_da_tela_revelada` estendido às classes novas (tokens só; `.qz-modo-lista` >= 44 px; rótulos <= 15, inclusive os
  renomeados "Concluir lista", "Rever uma a uma", "Mudar resposta"; nada `sticky/fixed`).

### Pattern Compliance

- [x] Espelho em `localStorage` + doc no db (padrão do player/F130) para o `modo`.
- [x] Funções puras extraídas pelo harness node; golden por cenário.
- [x] Skill canônica + `sync_skills` (`banco-emed.md` "Na página" + linha `listas/t<tarefa>` com `modo`).

### Desvios

- `tools/test_emed_banco.py` (fora da lista): `modo` entrou no conjunto exato `_SEM_DESTINO_ATE_A_PART_5` do teste de
  propriedade F133 (a página grava `modo` na resposta; a coluna é da part-5).
- Rótulos renomeados por causa da régua <= 15 (celular): "Marcar lista como resolvida" -> "Concluir lista",
  "Rever em sequência" -> "Rever uma a uma", "Alterar resposta" -> "Mudar resposta". O DoD 3 cita o nome antigo; o botão é o mesmo
  (`#qz-concluir`) e o comportamento pedido está nele.

### Decisões onde a spec deixava aberto

- "faltam N declarações" conta QUESTÕES pendentes (cada uma é um ato de declarar), não elos.
- Doc da lista vence o espelho (troca de aparelho); espelho só quando o doc não tem `modo`.
- Trocar o modo pela barra no meio da lista: respondida em Prova passa a abrir revelada em Estudo (ele pediu feedback); respondida
  em Estudo nunca volta a ser editável.
- Trava vale em Estudo também na revisão a partir do fim (sair sem declarar = "‹ Lista").
- Legado (t26/t96 sem `elos`) conta como pendente -- essas listas já estão `resolvida`; só reabrir pede declaração.

### Critical Gate

Clean -- nada destrutivo; `update({modo, atualizado_em})` só no doc da lista aberta; valores dinâmicos novos passam por `qzEsc`.

### Não verificado

- Fluxo no navegador real (escolha -> responder -> revelar -> próxima), a trava com o teclado físico e o celular.
- Se o re-seed do `listas/*` pelo agente (`ArtifactData batch set`, que substitui o doc) apaga o `modo`; o espelho local segura
  no aparelho, mas o doc perderia o valor -- a observar no tique.

14 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
