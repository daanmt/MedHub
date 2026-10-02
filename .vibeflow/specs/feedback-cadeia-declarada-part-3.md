# Spec: Feedback por elo declarado -- part 3: modo Estudo/Prova por lista + tela de fim com os elos

> Escrita em 2026-10-02 (s211). PRD: `.vibeflow/prds/feedback-cadeia-declarada.md` (Scope v0, itens 2 e 4, parte de tela).

## Objetivo

Ao abrir uma lista o aluno escolhe ver o feedback depois de cada questão (Estudo) ou só no fim (Prova); a tela de fim passa a mostrar o que revisar, elo por elo, e só deixa concluir a lista com as declarações obrigatórias feitas.

## Contexto

Desde 26/09 a aba Listas é só "modo prova": `qz-responder` grava e pula para a próxima; gabarito, solução e análise só na tela de fim (`qzFim`), que mostra tiles, "Por objetivo" e a lista de revisão. Decisão do operador em 02/10 (pergunta fechada): **modo escolhido por lista; simulado sempre Prova**; declaração **obrigatória em errada, dúvida e chute**.

**Fricção que esta spec remove:** esperar o fim de 30 questões para ver por que errou a 3a -- viciosa quando o objetivo é estudar o tema; virtuosa em simulado, e por isso o simulado não ganha o modo Estudo.

## Definition of Done

1. **Escolha do modo.** Abrir uma lista (não simulado) sem `modo` definido e sem respostas mostra a escolha: `Estudo` (feedback após cada questão) · `Prova` (feedback só no fim). A escolha grava `listas/<id>.modo` (`estudo | prova`) e um espelho em `localStorage`. Lista com `modo` abre direto; um controle na barra da lista permite trocar. Simulado (`area === "Simulado"`) nunca mostra a escolha nem o controle. Teste: `test_simulado_e_sempre_prova` e `test_modo_da_lista_vem_do_doc_e_do_espelho` (função pura `qzModoDaLista(l, espelho)`).
2. **Fluxo Estudo.** Em `estudo`, `Responder` grava a resposta (com `modo: "estudo"`) e revela a MESMA tela da part-2 no lugar; `Próxima` leva à próxima não respondida. Questão já respondida em Estudo reabre revelada (não editável). Em `prova` o fluxo é o de hoje e a resposta grava `modo: "prova"`. Teste: `test_estudo_revela_apos_responder_e_prova_nao`.
3. **Obrigatoriedade.** Com `qzDeclPendente(q, r)` verdadeiro, `Próxima` (e o `Enter`) fica desabilitado em Estudo, com a dica "declare os elos para seguir". Na tela de fim, `Marcar lista como resolvida` fica desabilitado enquanto houver pendência, com a contagem ("faltam N declarações"). Questão sem cadeia nunca gera pendência. Teste: `test_pendencia_trava_proxima_e_concluir` e `test_questao_sem_cadeia_nao_trava`.
4. **Tela de fim com os elos.** Novo bloco "Elos" depois de "Por objetivo": contagem por estado e a lista dos elos `Não`, `Incerteza` e `Desatenção` (nessa ordem), cada linha `Q<num> · <frase do elo>`, tocável (abre a questão revelada). Função pura `qzResumoElos(qs, resp)`. Na lista de revisão, questão com pendência ganha a marca "declarar". Golden `fim_elos.html`.
5. **Textos da aba.** `QZ_SUB` e o parágrafo da tela de fim reescritos para o desenho novo (sem "a análise do hub confirma o elo que quebrou"); cada um com no máximo 2 frases.
6. **Harness e forma.** `pytest tools/ -q` verde; `hub.py --build` com `--check` OK; teclado: `Enter` não fura a trava; craftsmanship igual à part-2 (tokens existentes, toque >= 44 px, rótulo <= 15 caracteres, `min-width:0`, nada fixo na rolagem).

## Scope

- `qzAbrir`: tela de escolha do modo (2 botões grandes, 1 linha de descrição cada) antes da 1a questão quando couber.
- `qz-responder` e `qzMostrar`: ramificam por modo; em Estudo, voltar pelo trilho a uma respondida chama a revelação.
- `qzFim`: bloco "Elos", pendências, trava do concluir.
- Cada resposta grava `modo`.

**Arquivos (2-3):** `core/templates/hub.html` · `tools/test_hub_render.py` (+ goldens) · `.claude/commands/banco-emed.md` se o texto "modo prova" da skill precisar de lápide (+ espelho).

## Anti-scope

- Modo Estudo em simulado. Cronômetro por modo. Estatística comparando modos.
- Ingestão de `modo` no `ipub.db` (part-5).
- Marca-texto (part-4).
- Mudar o que "resolvida" dispara no tique do `/hub-backend`.

## Technical Decisions

- **`modo` no doc da lista + espelho local:** a escolha sobrevive a troca de aparelho; o espelho cobre o db fora do ar (padrão do F130).
- **Estudo não deixa alterar resposta:** depois de ver o gabarito, alterar a letra falsificaria o acerto registrado.
- **Trava no concluir, não no responder:** em Prova ele resolve a lista inteira sem interrupção e declara na autópsia; a trava mora onde o dado é exigido.

## Applicable Patterns

- Espelho em `localStorage` + reenvio (padrão do player, s195).
- Goldens e funções puras extraídas pelo harness node.

## Risks

- **Lista antiga sem `modo` e já com respostas** (t1793 em curso, t26/t96 resolvidas): tratada como `prova`, sem tela de escolha. Coberto por teste.
- **Trava prender lista com cadeia defeituosa:** "cadeia com defeito" (part-2) conta como declaração para efeito de pendência -- incluir no `qzDeclPendente` e testar.

## Dependencies

- `.vibeflow/specs/feedback-cadeia-declarada-part-2.md`
