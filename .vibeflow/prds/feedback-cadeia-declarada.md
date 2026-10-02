# PRD: Feedback da cadeia de raciocínio declarado pelo aluno (aba Listas do hub)

> Generated via discover on 2026-10-02 (s211). Referência de produto: Prisma Medicina (vídeo de onboarding + 4 prints trazidos pelo operador).

## Problem

O feedback pós-questão da aba Listas erra o diagnóstico e polui a tela. O operador nomeou quatro defeitos (02/10/2026): **elo quebrado errado**, **cadeia mal construída**, **alternativa no elo errado** e **poluição visual**. A evidência do banco confirma os quatro:

- **A página adivinha a quebra pela letra marcada.** Cada alternativa errada carrega um `elo` e a letra marcada pinta esse elo como "provável quebra". Das 7 análises gravadas (t26, t96), 5 foram refeitas "com o racional declarado" e na t96 Q8 o veredito dele foi "discordo". O modelo confunde "por que esta alternativa está errada" com "onde a cadeia do aluno quebrou": na t96 Q17 ele marcou A (que cai no elo 1), tinha o elo 1 firme e a lacuna real era o elo 2, para o qual nenhuma alternativa aponta.
- **A cadeia nem sempre é uma cadeia.** Na t96 Q8 os 4 elos são 4 julgamentos paralelos, um por alternativa, em ordem arbitrária. Na t96 Q14 um único elo ("aplicar os vetos do 1o ano") engole três alternativas e não localiza a crença errada (suco). Os elos são escritos como habilidade abstrata ("Situar o corte do açúcar"), difícil de autoavaliar.
- **A pergunta de coleta é a errada.** Os 8 chips de "Onde quebrou?" pedem a causa, não o elo. Em 6 dos 8 erros com chip ele marcou "Não sabia" e usou o campo livre para declarar elo a elo ("elo 1 acertei, quebrei no 2, o 3 acertei também").
- **A tela empilha blocos.** Solução (pede, leitura das letras, cadeia, alternativas), campo de racional, 8 chips e a caixa de Análise (5 campos, veredito de 3 botões, nota).

Além disso, o feedback só existe no fim da lista (modo prova, decisão de 26/09) e não há como grifar o enunciado, que é onde moram os discriminadores, comportas e cutoffs que os elos cobram.

## Target Audience

O operador, único usuário: resolve listas e simulados no hub, quase sempre no celular, e usa o diagnóstico por elo para decidir o que revisar e de onde nascem os cards.

## Proposed Solution

O aluno declara o estado de cada elo; a página não infere nada.

1. **Declaração por elo, 4 estados:** `Sim` (executei com segurança) · `Incerteza` (cheguei sem firmeza) · `Desatenção` (sabia e não apliquei, ou li errado) · `Não` (não sabia). Obrigatória em errada, dúvida e chute; em certa e sólida os elos entram como `Sim` e um toque abre para ajustar.
2. **Cadeia que é sequência de raciocínio**, no molde do Prisma: identificar o cenário pelo dado do enunciado -> recordar o critério que decide -> descartar o distrator forte pelo dado que o exclui. Cada elo é uma frase sobre ESTA questão que ele consegue responder ("Identificou ...", "Recordou ...", "Descartou ..."), com um rótulo de habilidade reutilizável por trás, para o ledger. **A sequência é autoral** (decisão do operador, 02/10/2026): nasce dos resumos e das apostilas; em caso de dúvida sobre as habilidades, o comentário/resolução do EMED pode ser CONFERIDO pela API -- como lente de verificação, nunca como texto-fonte.
3. **Alternativa explica a si mesma:** o porquê de cada letra aparece embaixo da própria alternativa. A alternativa deixa de apontar elo na tela e de alimentar qualquer diagnóstico.
4. **Marca-texto:** selecionar um trecho do enunciado ou de uma alternativa destaca; tocar no destaque remove. Uma cor só. Os grifos gravam com a resposta e reaparecem na revisão.
5. **Dois momentos, a mesma tela:** ao abrir a lista ele escolhe `Estudo` (feedback depois de cada questão) ou `Prova` (feedback só no fim). Simulado é sempre `Prova`. A autópsia do fim continua existindo nos dois modos.
6. **Autópsia do fim com os elos:** além do resultado por objetivo, a contagem por estado e a lista dos elos `Não`, `Incerteza` e `Desatenção` da lista: o que revisar, em ordem.
7. **Sinal de cadeia com defeito:** um toque + motivo curto (mesmo padrão do defeito de card no player) manda a cadeia daquela questão para a minha fila de correção.
8. **O agente passa a confirmar, não a diagnosticar:** a análise vira uma linha sob a cadeia (conflito entre declarado e evidência, card criado). `Não` gera card de conhecimento; `Incerteza`, card de consolidação; `Desatenção` não gera card e soma no contador de execução do ledger de habilidades.

Identidade visual: a paleta do hub fica; o que muda é a diagramação da tela de questão.

## Success Criteria

- Nas duas listas de aceitação (t40 DMG e t49 Hérnias, 54 questões), **nenhuma análise é refeita por racional declarado** e ele não usa mais campo livre para dizer qual elo quebrou.
- Tela pós-resposta de uma questão errada com **no máximo 3 blocos** (alternativas com o porquê, cadeia com a declaração, linha do agente), sem caixa dentro de caixa e sem rolagem horizontal a 360 px.
- **Cadeia com defeito em até 10% das questões** das listas de aceitação (5 de 54). Acima disso, o contrato de conteúdo volta para revisão antes de cunhar a próxima lista.
- Grifos feitos no celular dele em uma lista real persistem e aparecem na revisão.
- As declarações chegam ao `ipub.db` e o mapa de fragilidade lista os elos `Não` e `Incerteza` por tema.

## Scope v0

Em ordem de entrega (cada item cabe em uma spec):

1. **Contrato de conteúdo da cadeia** (brief + validador): sequência identificar -> recordar -> descartar, elo declarável + rótulo de habilidade, alternativa só com o porquê. t40 e t49 recunhadas nesse contrato.
2. **Tela de questão:** declaração por elo, porquê sob a alternativa, linha do agente, sinal de cadeia com defeito, seletor Estudo/Prova. Saem os 8 chips, a leitura "Você: riscou...", a seção Alternativas, a leitura provisória e a caixa de 5 campos; o racional vira uma linha opcional.
3. **Marca-texto** no enunciado e nas alternativas, gravado com a resposta.
4. **Ingestão e autópsia:** declaração, grifos e sinais de defeito entram no `ipub.db` pelo registro que já existe; a tela de fim ganha o resumo por elo; cards e ledger consomem os estados.
5. **Cobertura:** cada lista ganha a cadeia antes de ele abrir, na ordem do plano; no simulado, só as erradas e não-sólidas ganham cadeia, depois da prova, no chat.

## Anti-scope

- Conceitos/flashcards por questão com aceitar e rejeitar na página, caderno de erros, quiz interativo e "ponto de atenção" do Prisma.
- Reagendar questões por habilidade quebrada.
- Paleta ou identidade nova; qualquer mudança nas abas Painel, Aulas e Cards.
- Aba Análise separada e faixa de padrões entre sessões (o resto do PRD `hub-aba-analise`).
- Migrar t26, t96 e os 1.094 erros antigos para o contrato novo.
- Grifo com tipos ou cores (discriminador, comporta, cutoff).
- Análise disparada pela página ou pelo tique (barrado pelo classificador na s194; a análise segue no chat).
- Cadeia prévia para as 417 questões dos simulados.
- Comentário do professor e fórum: ficam como estão.

## Technical Context

- **Tela:** `core/templates/hub.html` -- `qzRevelar`, `qzSolucao`, `qzAnalise`, `qzSalvarMeta`, `qzFim`, bloco `#qz-meta-erro` e os estilos `.qz-*`. Montagem e checagem por `tools/hub.py --build`; publish sempre na URL do HANDOFF, sem `capabilities` (os campos novos viajam no doc `respostas/<lista>_<num>`, que a página já escreve).
- **Contrato atual da cadeia:** `docs/SOLUCAO-MEDHUB-BRIEF.md` (portador único do vocabulário de estados), validado por `db.solucao_v2_problemas` (exige `elo` em toda alternativa errada) e por `core/objetivos.json`.
- **Gates que vão mudar junto:** `tools/test_hub_render.py` (um golden por estado + leitura provisória) e `test_vocabulario_de_estados_do_brief_e_o_da_pagina`.
- **Fontes da cadeia:** `resumos/**/*.md` e as apostilas do EMED em PDF dentro de `resumos/` (gitignored). A conferência do comentário pela API reverte em parte a decisão de 26/09 ("comentário do professor fica fora"): hoje o brief tem a REGRA DURA "sem ler o comentário do professor" e `tools/emed_api.py` tem whitelist na fronteira (o comentário não chega ao disco). O que muda é só a leitura para conferir; segue valendo que o comentário não entra no hub, no git nem no texto da cadeia.
- **Ingestão:** `tools/emed_banco.py --registrar` / `--erros` (hoje lê riscadas e o elo da letra) sobre `db.emed_upsert_respostas`; `tools/habilidades.py` é o ledger de habilidades reincidentes.
- **Skills que citam o mecanismo:** `/banco-emed` §Solução MedHub e `/analisar-questao` §3.3 (editar o canônico e rodar `sync_skills`).
- **Regras da casa:** revogar cláusula tem 3 passos no mesmo commit (declarar, lapidar no portador lido no ato, cadastrar em `_TERMOS_REVOGADOS`) -- vale para "leitura provisória pelas letras" e "alternativa errada aponta o elo"; conteúdo do EMED nunca no git; elo e porquê em 1 linha; celular primeiro (toque >= 44 px, `min-width:0`, nada fixo na rolagem, rótulo <= 15 caracteres); orçamento de 6 arquivos por tarefa.
- **PRD relacionado:** `hub-aba-analise.md` (s196). Os itens 3 e 4 dele (cadeia por erro e veredito) já vivem na aba Listas e são redesenhados aqui; a aba separada e a faixa de padrões seguem em backlog.

## Open Questions

- **Seleção por toque dentro do artifact:** o grifo depende de a seleção de texto funcionar no celular dele dentro da página publicada. Validar com um protótipo antes de fechar a spec do item 3; se falhar, o plano B é grifar por toque em frase.
- **Mecânica da conferência pela API:** proposta é leitura sob demanda, só da questão em dúvida, para `tmp/` (nunca em lote, nunca gravada em `questoes/*`), com o token dele (`.emed_token`, válido até 26/10). Fechar na spec do item 1, com a lápide da REGRA DURA do brief no mesmo commit.
- **Análises antigas (t26, t96):** render legado ou conversão de exibição (`ok` -> Sim, `quebrou` -> Não, `nao_usou` -> Desatenção, `nao_avaliado` -> sem declaração). Decidir na spec do item 2.
- **Veredito de 3 botões:** proposta é mostrá-lo só quando o agente apontar conflito com a declaração. Confirmar com o operador na primeira lista de aceitação.
