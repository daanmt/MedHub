# Crítica Impeccable do HUB (`tmp/hub/index.html`), 19/10/2026 (s231)

Método: dual-agent (A: revisão de design, isolada · B: detector + navegador, isolada). A síntese foi feita depois que as duas terminaram, e o detector só foi lido após a A.

- **Comando:** `/impeccable critique tmp/hub/index.html`, plugin Impeccable 4.6.0.
- **Modo:** Operate (ferramenta de estudo diária). O leitor de aula/resumo foi avaliado em modo Read.
- **Cena de uso:** celular, sessões curtas, carga cognitiva alta, e ele precisa ver "o que fazer agora" na hora.
- **Evidência visual:** `python tools/ui_capturas.py --larguras 390,1280` (Edge headless, db falso), 11 cenas × 2 larguras em `tmp/impeccable_s231/critique/`. A medida de rolagem horizontal deu `ok` em todas.
- **Detector:** `impeccable detect --json` sobre o build, `core/templates/hub.html`, `player.html` e `artifacts/painel.html`. Também rodou a varredura por URL num servidor local com UTF-8, a 390 e a 1280. A saída bruta está em `tmp/impeccable_s231/critique/detector/`.
- **Sobreposição no navegador:** não feita. Pela regra do projeto, a extensão do Chrome é compartilhada com colegas, então não há aba [Human] com marcações.
- **Sem PRODUCT.md e sem DESIGN.md.** O contexto de produto e de design veio de `docs/UI.md` e do brief. As premissas estão no fim.
- 🔒 **Este relatório descreve só a interface.** Nenhum texto de questão, de aula ou de card foi citado.

---

## Nota de saúde do design (Nielsen)

| # | Heurística | Nota | Problema-chave |
|---|---|---|---|
| 1 | Visibilidade do estado do sistema | 3 | Anéis, cronômetro, "atualizado há N min" e o trilho funcionam bem. Porém a tela de fim de lista diz "Lista concluída" enquanto "Concluir lista" ainda está bloqueado por declarações pendentes. |
| 2 | Correspondência com o mundo real | 3 | A linguagem clínica e a do FSRS são a dele. Vaza jargão de backend: um título de simulado carrega "(filtro instituição=…, anos …)", e aparece "Fora do sprint". |
| 3 | Controle e liberdade | 3 | Há voltar, Anterior/Pular, Riscar e Pausar. O rótulo do voltar varia ("‹ Todas as listas" × "‹ Lista" × "‹ Teoria"). |
| 4 | Consistência e padrões | 2 | O nome da área muda por tela (PED/MFC no Painel, Pediatria/Preventiva em Listas). A carga do dia tem três números diferentes. O chip rosa repete em toda linha, enquanto a faixa já codifica a área. Âmbar quer dizer "Simulado" e também "aviso/atraso". |
| 5 | Prevenção de erro | 3 | Responder fica desabilitado até haver alternativa marcada, a nota exige virar o card e o Concluir tem portão. |
| 6 | Reconhecer em vez de lembrar | 3 | O fim de lista cita "Erradas: 1, 4, 5…" e "não firmes: Q5, Q13" como texto puro, então ele precisa lembrar qual questão era qual. Os Elos são tocáveis; esses números não. |
| 7 | Flexibilidade e eficiência | 3 | Cards mostram os atalhos (Espaço/P/D). A questão tem A–E, 1–5, S/D/C e Enter, mas sem dica visível. A declaração de elo não tem atalho. |
| 8 | Estética e minimalismo | 2 | O H1 repete o nome da aba ativa (cerca de 60 px a 390). O resumo do "Hoje" do Cronograma aparece duas vezes. A contagem "1:0 2:0 3:0 4:0 defeito:0" fica no topo do player. O gráfico de Flashcards da semana, quase plano, ocupa um espaço nobre. |
| 9 | Reconhecer e recuperar de erros | 3 | A leitura resiliente com "Tentar de novo" é sólida. A mensagem do portão ("Faltam N declarações") só aparece no rodapé da tela de fim. |
| 10 | Ajuda e documentação | 2 | Mínima de propósito (um usuário só). "Cadeia", "Elos" e "Fora do sprint" nunca são definidos. Hoje ele sabe, mas isso fica frágil depois de uma pausa. |
| **Total** | | **27/40** | **Aceitável** (no topo da faixa; a fundação é boa) |

---

## Veredito de especificidade do design

**Avaliação do LLM:** o hub foi, na maior parte, **feito para este produto**. Nada disto caberia num dashboard genérico:
- a Atkinson;
- a placa fosca com o fio cromado de 1 px;
- a tríade de certeza (Sólida / Dúvida / Chute);
- a declaração da cadeia em quatro estados;
- os rótulos de nota do FSRS na voz dele;
- o "mais fraco" escrito no Por bloco;
- a paleta rosa própria dos Flashcards da semana.

Duas zonas derivam para o genérico:
1. **Os quatro anéis do topo do Painel.** É o padrão de anel de app fitness, e de manhã dois deles marcam 0%.
2. **As barras de tarefa do Cronograma e de Listas.** Cada linha tem faixa colorida, fundo tingido, chip rosa e um botão ciano grande. Lê como um gerenciador de tarefas qualquer. A 1280 é a região mais ruidosa do hub.

**Varredura determinística:** 155 achados por arquivo e 4 por URL. Quase todos são falsos positivos ou decisões documentadas:

| Regra | Onde | Veredito |
|---|---|---|
| `side-tab` ×125 (4 px + raio) | `hub.html:135-137`, uma por item do backlog (`.qd-bloco`, `.qz-lista button`) | **Falso positivo por design.** A faixa de 4 px é a área (`--area`), decidida na UI.md §6, rodadas 3/4, s229, e testada em `tools/test_hub_render.py`. Mesmo assim é um "tell" conhecido de UI gerada; ver P2. |
| `side-tab` (3 px) | `.hub-aviso` (`hub.html:267`), `.hub-assina-retorno` (`hub.html:467`), aviso do `player.html:126` | Os avisos em âmbar seguem o token (UI.md §5 "Aviso"). Em `.hub-assina-retorno`, a confirmação **estática** usa filete ciano, o que dobra a regra "ciano = interação". Severidade baixa. |
| `low-contrast` 1,5:1 | aba ativa (`hub.html:76`) | **Falso positivo.** O gradiente é só o sublinhado de 2 px; o texto fica sobre o fundo escuro (cerca de 17:1). |
| `low-contrast` 4,37–4,44:1 | Painel: meta `.tarefa` em `--tinta3` sobre o fundo tingido pela área (`color-mix` 9%) | **Verdadeiro, marginal.** Fica logo abaixo de AA. O teste de contraste só cobre papel/card/afundado, não o fundo tingido. Encontro com a A (Sam). |
| `cramped-padding` ×18 | `.tarefa` / `.bl` no painel | Falso positivo: a faixa `.t-faixa` encosta na borda de propósito. |
| `flat-type-hierarchy` | painel: h3 = corpo = 14 px | Parcialmente verdadeiro. O h3 só se distingue por peso e cor. |
| `ai-color-palette` "ciano neon em fundo escuro" | marca `Hub` (`hub.html:63`) | Tensão real, mas **conflita com regra da UI.md §2 ("a marca `Med` + `Hub` em ciano, s226") — decisão dele.** |
| `ai-color-palette` "gradiente roxo" | linha do horizonte | Falso positivo. É a assinatura documentada (`--horizonte`). |

O detector **não pegou** o que mais pesa: a hierarquia do Painel, os números da carga do dia que não batem e a contradição da tela de fim. São problemas de UX que só a leitura humana (A) viu. A varredura por URL só alcançou a casca do hub: o painel cai no aviso de fallback sem a fonte de dados local. O conteúdo das abas foi coberto pelas capturas.

**Sobreposição visual:** nenhuma aba [Human] disponível (Chrome fora, regra do projeto).

---

## Impressão geral

O sistema visual é disciplinado e tem dono: cor com semântica, estado nunca só por cor, e um fluxo de questão que é o melhor pedaço do produto. O problema não é estética. É **ordem**. No celular, o Painel abre com quatro anéis (dois zerados de manhã), Por bloco e o gráfico da semana, e a próxima ação ("Próxima" → Resolver) fica cerca de 1.400 px abaixo, ou seja, umas 1,7 telas de rolagem. A maior oportunidade é fazer a primeira dobra do Painel responder "o que eu faço agora" antes de "como estou indo".

## O que funciona

1. **O sistema de cor é disciplinado e documentado.** Ciano é só interação. O estado sempre vem acompanhado de símbolo ou texto (✓ ✗ ?, "mais fraco"). O contraste é sustentado por teste. Isso dá previsibilidade a quem estuda cansado.
2. **O fluxo da questão é o núcleo do produto e está bom.**
   - A certeza é capturada antes de responder.
   - Responder fica desabilitado até haver escolha.
   - O "por quê" aparece embaixo de cada alternativa revelada.
   - A declaração de elo é alinhada à esquerda e numerada ("Elo 1 de 4").
   - Tudo isso transforma o erro em dado sem forçar texto livre.
3. **O verso do card e a Biblioteca têm calma.**
   - O verso tem camadas em degraus: Resposta, depois Regra-mestre com filete neutro, depois Armadilha com filete âmbar, sem caixa dentro do card.
   - A Teoria abre com as áreas recolhidas, sem ruído.
   - O leitor de aula tem boa medida de linha e hierarquia de títulos.

## Problemas prioritários

### [P0] A próxima ação está enterrada no Painel a 390 px
- **Por que importa:** o critério da cena dele é "ver o que fazer agora na hora". Hoje o cartão "Próxima" fica abaixo dos 4 anéis, do Por bloco e dos Flashcards da semana. Ele rola quase duas telas antes de agir, toda manhã.
- **Correção:**
  - A primeira coisa da placa "Hoje" vira uma faixa "Próxima" com título, contagem e Resolver.
  - Os anéis encolhem para uma fileira 4-up de cerca de 72 px.
  - Os Flashcards da semana descem para depois do Cronograma.
  - Os dias futuros do Cronograma ficam recolhidos.
- **Comando sugerido:** `/impeccable layout` + `/impeccable distill`
- ⚠️ **Conflita com a regra da UI.md §5 v4.1 ("o topo é UMA placa Hoje com 4 anéis", pedido dele na s227) e com a §6 (Cronograma com os dias "TODOS abertos") — decisão dele.** A mudança serve à própria regra de ordem da §6 ("o que fazer hoje" primeiro). Uma saída que preserva os anéis: a faixa "Próxima" entra dentro da placa Hoje, acima deles.

### [P1] Três números diferentes para a carga do dia
- **Por que importa:**
  - O anel de Questões diz "0 de N" com N = o plano do dia, simulado incluído.
  - O Ritmo diz "de 80 por dia".
  - Listas › Hoje soma só as listas, porque o simulado fica noutra sub-aba.
  - O Cronograma repete o total com o simulado.

  Denominadores misturados aumentam a ansiedade e corroem a confiança no número.
- **Correção:**
  - Usar um denominador por dia.
  - Mostrar o simulado como unidade à parte ("1 simulado + N q") nos dois lugares.
  - O anel de Ritmo diz explicitamente que mede a capacidade do sprint, não o dia.
- **Comando sugerido:** `/impeccable clarify`
- ⚠️ **Toca a regra da UI.md §5 ("com sprint o único por-dia é o do sprint", `q_hoje` no tile) e o `cronograma-contract` — decisão dele.**

### [P1] A tela de fim de lista se contradiz e afoga o fechamento
- **Por que importa:**
  - O título "Lista concluída" aparece com o "Concluir lista" ainda desabilitado.
  - O aviso "Faltam N declarações" fica embaixo de cerca de 30 itens de Elos.
  - O fim abre com uma parede de "Não" em coral, sem nada sobre o que ficou firme.

  Pela regra pico-fim, o fim da sessão vira a lembrança dela. Hoje é o momento mais fraco do hub.
- **Correção:**
  - Com declarações pendentes, o título vira "Falta declarar N".
  - O estado e o botão Concluir sobem para logo abaixo das métricas.
  - Mostrar os 3–5 primeiros Elos com "Ver todos (N)".
  - Abrir com uma linha do que ficou firme.
  - Os números "Q5" em Erradas e Por objetivo viram toques que levam à questão.
- **Comando sugerido:** `/impeccable clarify` + `/impeccable distill` + `/impeccable delight` (leve)
- Sem sticky nem fixo (UI.md §7, já respeitado na proposta).
- Os Elos hoje aparecem como cartões com faixa. Isso já colide com a UI.md §5 ("Linha de lista: sem fundo e sem caixa própria", que lista `.qz-cadeia li`), ou seja, é um **desvio da própria regra**, não um conflito.

### [P2] A semântica de cor deriva nas barras de tarefa e no leitor
- **Por que importa:**
  - Âmbar (faixa e fundo) quer dizer Simulado, mas âmbar também é aviso/atraso.
  - O fundo tingido de CIR lê perto do coral de erro.
  - O chip rosa repete em toda linha enquanto a faixa já diz a área; PED tem faixa roxa e chip rosa.
  - O termo-chave em negrito ciano no leitor de aula/resumo lê como link, porque ciano = interação.
  - O fundo tingido também derruba a meta `--tinta3` para 4,4:1 (detector).
- **Correção:**
  - Tirar o fundo tingido da linha e manter só a faixa de 4 px.
  - Chip neutro (`--afundado` + `tinta2`) com o nome da área.
  - Simulado ganha identidade não-âmbar (contorno ou ícone).
  - Termo-chave em branco forte.
- **Comando sugerido:** `/impeccable colorize` + `/impeccable quieter`
- ⚠️ **Conflita com a regra da UI.md §6 rodadas 3/4 (paleta por área com Simulado âmbar e chip `.t-rot` rosa no Painel, s226/s229) e com a §9 ("termo-chave em negrito ciano claro", pedido dele, s224) — decisão dele.** O problema do contraste do `--tinta3` sobre o fundo tingido não conflita com nenhuma regra: basta incluir o fundo tingido no teste de contraste ou subir a meta para `tinta2`.

### [P2] Copy e acabamento
- **Por que importa:** pequenos atritos somam numa ferramenta usada todo dia.
- **Correção:**
  - Acentos que faltam no player: "revisao vencida", "com esforco", a tecla "Espaco".
  - "Questão 1 · 1 de N" é redundante.
  - Dois simulados com título idêntico e longo, carregando o filtro técnico. Dar a cada um um título curto e distinto (ex.: "UERJ 2017-20 · parte 1/2").
  - Padronizar o rótulo do voltar.
  - Padronizar o nome da área: sigla ou nome por extenso, um só.
  - Remover o H1 que repete a aba ativa.
  - No leitor, o título do documento aparece na barra e no H1, e o botão Grifo ocupa uma linha só para ele.
- **Comando sugerido:** `/impeccable clarify` + `/impeccable polish`
- Sem conflito com a UI.md.

---

## Bandeiras vermelhas por persona

**Casey (celular, distraído, uma mão):**
- No Painel, cerca de 1,7 tela de rolagem até o primeiro Resolver.
- Nos Cards, "Virar o card" fica na placa de cima (y ≈ 305 px a 390) e as notas 1–4 ficam embaixo do card, então cada card pede o polegar subindo e descendo.
- Depois de virar o card, o layout dos controles muda (Pausar troca de lugar).
- No fim de lista, o Concluir exige rolagem longa.
- O trilho de 21 segmentos a 390 dá alvos de cerca de 15 px de largura. A UI.md fixa 26 px de toque na altura, mas a largura fica abaixo de 44.

**Alex (usuário avançado):**
- Os atalhos da questão (A–E, S/D/C, Enter) existem mas são invisíveis, enquanto os Cards mostram os seus (inconsistente).
- A declaração de elo (4 × 4 = 16 botões) não tem tecla, por exemplo 1–4 no elo em foco.
- A tela de fim não oferece "próxima lista".

**Sam (acessibilidade):**
- Os segmentos do trilho são estreitos.
- O "· por quê" é pseudo-elemento: pequeno, em `tinta3` a 0,82em e não anunciado. A alternativa inteira ser o alvo ajuda.
- O × (Riscar) desabilitado continua visível nas alternativas reveladas, o que é ruído.
- A meta em `tinta3` sobre o fundo tingido fica a 4,4:1, fora do teste.
- O "%" dentro do anel é minúsculo.
- A caixa do cronômetro parece botão.

## Observações menores

- Por bloco usa escala 0–100%, então 75% e 85% parecem quase iguais. Falta a marca do alvo (o norte de acerto) na barra.
- "tarefas 30/102" não diz se é feitas/total.
- Flashcards da semana com 7 barras quase iguais informa pouco para o destaque que tem.
- A Teoria a 390 é cerca de 60% vazia e não tem "continuar lendo" (última aula ou resumo aberto).
- O cabeçalho da questão (título, Grifo, cronômetro, trilho) custa cerca de 200 px antes do enunciado.
- A 1280, Listas deixa a metade de baixo vazia e as abas se espalham por 1.120 px.
- `.hub-assina-retorno` usa filete ciano para uma confirmação estática (ciano = interação, UI.md §2).
- Linha de base do painel: o h3 tem o mesmo corpo do texto (detector `flat-type-hierarchy`).

## Perguntas para considerar

1. Às 23h, depois de um plantão, qual é a única frase que o Painel deveria dizer? Quatro anéis dizem isso melhor do que "Próxima: <prova> · Resolver"?
2. O total de questões do dia é plano ou desejo, quando o ritmo real de 7 dias é menos da metade? O hub deveria mostrar só números que ele consegue bater?
3. O fim de uma lista deveria mostrar primeiro o que ficou firme e só depois os "Não", já que o fim da sessão é o que ele lembra dela?

---

## Ações recomendadas (proposta; ele decide a ordem)

As perguntas de prioridade e escopo do fluxo do critique não puderam ser feitas a ele nesta sessão (rodou por subagente). A ordem abaixo segue o impacto. Os itens com ⚠️ dependem de decisão dele contra uma regra da UI.md.

1. **`/impeccable layout`** — Painel a 390: faixa "Próxima" no topo da placa Hoje; Flashcards da semana abaixo do Cronograma; dias futuros recolhidos. ⚠️ UI.md §5 v4.1 / §6.
2. **`/impeccable clarify`** — um denominador do dia (simulado como unidade à parte) entre o anel, Listas › Hoje e Cronograma; o título do fim de lista coerente com o portão; títulos curtos dos simulados; acentos do player; rótulos do voltar e nome de área padronizados. ⚠️ parcial: §5 `q_hoje`.
3. **`/impeccable distill`** — fim de lista: estado + Concluir no topo, Elos resumidos com "Ver todos", Elos como linha de lista (alinha com a §5); remover o H1 duplicado da aba.
4. **`/impeccable colorize`** + **`/impeccable quieter`** — barras de tarefa sem fundo tingido, chip neutro, Simulado sem âmbar, termo-chave sem ciano; incluir o fundo tingido no teste de contraste. ⚠️ UI.md §6 rodadas 3/4 e §9.
5. **`/impeccable adapt`** — alvo do trilho a 390, Virar e notas na mesma zona do polegar no player, dica dos atalhos na questão para o desktop.
6. **`/impeccable polish`** — passada final, seguida de nova captura com `tools/ui_capturas.py` e um `/impeccable critique` para medir a nota.

---

## Premissas (sem PRODUCT.md / DESIGN.md e sem entrevista)

- O contexto de produto veio do brief do operador: usuário único, médico, prova UERJ 01/11/2026, meta de 10.000 questões, leitura no celular. O de design veio de `docs/UI.md` (tema v4 "fosco em camadas"), tratado como DESIGN.md de fato.
- Modo Operate para o hub, Read para o leitor. Personas: Casey, Alex e Sam (as do catálogo do Impeccable). Não foi gerada persona do projeto, porque não há `## Design Context` do `impeccable init`.
- Toda regra da UI.md que nasceu de pedido dele foi tratada como intencional. Quando a recomendação a contraria, está marcada como "conflita com regra X — decisão dele", sem rebaixar a nota por isso.
- As capturas usam db falso semeado de `tmp/` e só mostram a janela, não a página inteira. As posições em px a 390 são aproximadas.
- O snapshot em `.impeccable/critique/` e a trilha de tendência do Impeccable **não foram gravados**: a tarefa era só leitura e o operador fixou este caminho como destino do relatório. Esta é a primeira rodada para este alvo, sem tendência.
