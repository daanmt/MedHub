# Spec: Feedback por elo declarado -- part 2: a tela de revelação (declaração, porquê sob a alternativa, linha do agente)

> Escrita em 2026-10-02 (s211). PRD: `.vibeflow/prds/feedback-cadeia-declarada.md` (Scope v0, item 2).

## Objetivo

Depois de revelar uma questão, o aluno declara o estado de cada elo com 4 botões e lê o porquê de cada alternativa embaixo dela; a página não infere mais nenhuma quebra e a tela cai de 5 blocos empilhados para 3.

## Contexto

`core/templates/hub.html` hoje (`qzRevelar`, `qzSolucao`, `qzAnalise`, `#qz-meta-erro`):

- Solução com 4 seções: "Pede", a linha "Você: riscou ... · marcou ...", a cadeia pintada pela letra marcada ("provável quebra: a sua letra cai neste elo", "evidência: você riscou ...") e a lista "Alternativas" com "falha no elo N";
- textarea "O que te levou à letra marcada?" + 8 chips "Onde quebrou?" (categorias de causa);
- caixa "Análise do hub" com Pedia / Comporta / Armadilha / Veredito / Cards + 3 botões de veredito + textarea.

Defeitos nomeados pelo operador (02/10): elo quebrado errado, alternativa no elo errado, poluição visual. Referência: Prisma (prints da sessão: "Habilidade N de M" com Sim / Incerteza / Desatenção / Não; explicação sob cada alternativa).

**Fricção que esta spec remove:** escrever em campo livre "elo 1 acertei, quebrei no 2" e corrigir o diagnóstico da página -- viciosa. Protege a virtuosa: a declaração honesta por elo passa a ser obrigatória onde importa.

## Definition of Done

1. **Declaração por elo.** Cada elo da cadeia (v2 ou v3) mostra 4 botões: `Sim` · `Incerteza` · `Desatenção` · `Não`. O toque grava `elos` (array alinhado à cadeia, valores `sim | incerteza | desatencao | nao | ""`) no doc `respostas/<lista>_<num>`, pelo mesmo `qzGravar` (espelho local + reenvio). Certa e sólida: os 4 botões aparecem com `Sim` presumido (marcado, rotulado "presumido") e NADA é gravado até ele tocar. Teste: `test_declaracao_grava_o_array_alinhado_a_cadeia` + golden `declarada.html` e `presumida.html`.
2. **Zero inferência.** O HTML produzido não contém mais "provável quebra", "a sua letra cai", "evidência: você riscou", "leitura provisória" nem "falha no elo"; nenhum elo ganha classe de estado sem declaração (exceção única: o item 5). Teste: `test_pagina_nao_infere_quebra_pela_letra` (errada, sem declaração, sem análise -> todos os elos neutros).
3. **Porquê sob a alternativa.** Revelada a questão, o `porque` da letra do gabarito e o da letra marcada aparecem embaixo da própria alternativa; as demais abrem no toque. A seção "Alternativas" separada e a linha "Você: ..." deixam de existir. Teste: `test_porque_aparece_sob_o_gabarito_e_a_marcada`.
4. **Linha do agente.** `analises/<lista>_<num>` rende no máximo: `veredito_hub` (1 parágrafo curto), `armadilha` se houver (1 linha) e os cards `#id`. Os 3 botões de veredito + nota só aparecem quando a análise traz `conflitos` não vazio. Saem "Pedia" e "Comporta" da tela. Teste: `test_linha_do_agente_sem_conflito_nao_pede_veredito` e `test_linha_do_agente_com_conflito_pede_veredito`.
5. **Conflito determinístico e legado.** (a) Elo `descartar` com `letra` igual à letra marcada e declaração `sim` ganha o rótulo "conflito: você marcou a alternativa que este elo descarta" (`qzConflitos(q, r)`, função pura, testada). (b) Resposta SEM `elos` e análise antiga COM `estados` (t26/t96): a página mostra os estados convertidos (`ok` -> Sim, `quebrou` -> Não, `nao_usou` -> Desatenção, `nao_avaliado` -> sem marca) com o rótulo "da análise de <data>", sem gravar. Golden `conflito.html` e `legado.html`.
6. **Cadeia com defeito + limpeza.** Um controle discreto "cadeia com defeito" abre um campo de motivo curto e grava `cadeia_defeito: {motivo, ts}` na resposta. Saem os 8 chips e a obrigatoriedade do racional: sobra UMA linha opcional ("Algo a acrescentar? (opcional)"), que continua gravando `racional`. O campo `elo` (chip antigo) deixa de ser escrito. Teste: `test_defeito_de_cadeia_grava_motivo` e `test_chips_de_causa_sairam`.
7. **Vocabulário, harness e forma.** `docs/SOLUCAO-MEDHUB-BRIEF.md` §Estado por elo passa a definir o vocabulário DECLARADO (portador único) com lápide no vocabulário antigo, e `test_vocabulario_de_estados_do_brief_e_o_da_pagina` compara o novo; "Na página" do `/banco-emed` atualizado com lápide (rito `AGENTE.md §10.10`: "leitura provisória pelas letras" revogada). Goldens antigos substituídos de propósito (diff no commit). `pytest tools/ -q` verde, `hub.py --build` com `--check` OK, `sync_skills --check` 0. Craftsmanship: nenhuma cor fora dos tokens existentes; todo botão >= 44 px de toque; nenhum rótulo de botão com mais de 15 caracteres; grid item com `min-width:0`; nada `position: sticky/fixed`.

## Scope

**Estrutura da tela revelada (3 blocos, nesta ordem):**

1. **Alternativas** (as mesmas `.qz-alt`, agora com o `porque` dentro) + a faixa de veredito (Certa/Errada, letra, certeza, tempo).
2. **Cadeia:** "Pede" como subtítulo de 1 linha; cada elo = número + frase do elo + `chave` (a chave aparece depois de declarar, ou sempre que a questão foi errada -- decidir pelo que ficar mais limpo e fixar em teste) + os 4 botões. Objetivo da questão como chip no título do bloco. Cores dos estados pelos tokens que já existem: Sim `--qz-ok`, Incerteza `--qz-duv`, Desatenção `--qz-chute`, Não `--alerta`.
3. **Linha do agente** (só quando há análise).

Rodapé discreto, fora dos blocos: linha opcional de racional, "cadeia com defeito", `Conferir:` e fontes da solução (quando houver), "Comentário do professor" e "Fórum" só para docs antigos que ainda os tenham.

**Funções puras novas** (extraíveis pelo harness node de `tools/test_hub_render.py`): `qzPrecisaDeclarar(q, r)` (tem cadeia E (errada OU certeza != sólida)), `qzDeclPendente(q, r)` (precisa e falta algum elo), `qzConflitos(q, r)`.

**Arquivos (5):** `core/templates/hub.html` · `tools/test_hub_render.py` (+ `tools/goldens/hub_render/*`) · `docs/SOLUCAO-MEDHUB-BRIEF.md` (só §Estado por elo) · `.claude/commands/banco-emed.md` (+ espelho) · `tools/test_hub.py` se algum teste de lá citar o texto removido.

## Anti-scope

- Modo Estudo/Prova e tela de fim (part-3). Nesta part a revelação continua acontecendo só no fim, como hoje.
- Marca-texto (part-4). Ingestão no `ipub.db` dos campos novos (part-5).
- Paleta nova, fonte nova, qualquer mudança nas abas Painel, Aulas e Cards ou no player.
- Conceitos/flashcards na página; caderno de erros.
- Reescrever as análises antigas no db do hub.

## Technical Decisions

- **`elos` dentro do doc de resposta:** a página já escreve `respostas/*` (regra `admin`, owner); nenhuma mudança de `capabilities`. Trade-off: o doc cresce alguns bytes; aceitável.
- **Presumido não grava:** evita 4 escritas por questão certa e separa "declarou Sim" de "não tocou". A part-5 lê ausente como presumido.
- **Legado por conversão de exibição, sem migração:** 7 docs; migrar exigiria escrever no db do hub por dado que ele já validou ("concordo").
- **Veredito só em conflito:** com a declaração como dado primário, pedir "concordo/discordo" em toda análise era a página perguntando duas vezes a mesma coisa.

## Applicable Patterns

- Padrão de design do hub (memória `feedback_design_hub_minimalista`, `feedback_artifact_celular_nowrap_sticky`): minimalista, celular primeiro, formatação flexível em vez de prosa.
- Goldens por cenário em `tools/goldens/hub_render/` (padrão já em uso).
- Skill canônica + `sync_skills`.

## Risks

- **Lista em curso no hub** (UERJ 2021 com 10/60 respondidas; respostas antigas sem `elos`): a tela tem de abrir resposta antiga sem erro -- coberto pelo golden `legado.html` e por um teste com resposta sem os campos novos.
- **Teclado:** `Enter` hoje avança; com declaração pendente não pode pular a obrigatoriedade (a trava em si é da part-3; aqui só não quebrar o atalho).
- **Poluição de volta por acréscimo:** o DoD 2 e 6 prendem por teste o que saiu.

## Dependencies

- `.vibeflow/specs/feedback-cadeia-declarada-part-1.md`
