---
type: research
status: active
relates_to: [core/templates/hub.html, core/templates/player.html, core/templates/tema.css, core/templates/tema-aula.css, tools/painel.py, DESIGN.md, docs/BACKLOG-PRODUTO.md]
---

# Auditoria interna de UI/UX do HUB (Impeccable critique + audit, s236, 30/10/2026)

⚠️ DEGRADED: single-context (o brief do agente de estudo proíbe subagente; as avaliações A, de design, e B, do detector, rodaram em sequência no mesmo contexto, e a A terminou antes de o detector ser lido).

- **Pedido do operador (30/10):** *"rodar um subagent opus com escopo dedicado de auditoria interna da UI/UX do medhub, utilizando o /impeccable"*. **Somente leitura:** nenhum arquivo do repo foi editado. Só este relatório e `tmp/ui_auditoria/` foram escritos.
- **Ferramenta:** plugin Impeccable 4.6.0, `reference/critique.md` + `reference/audit.md` + `reference/operate.md`. O `impeccable context` rodou uma vez: não há PRODUCT.md, e o DESIGN.md (raiz) é a autoridade visual.
- **Modos:** Operate (Painel, Teoria, Listas, questão, Cards) e Read (leitor de aula e de resumo).
- **Evidência renderizada:** `python tools/ui_capturas.py --larguras 390,768,1280 --out tmp/ui_auditoria` (Edge headless, db falso). Saíram 33 capturas, todas com **zero rolagem horizontal e zero erro de JS**.
  - O leitor foi recapturado em `tmp/ui_auditoria/aula2/`, porque as 5 RDs `rd-*-2910` estavam sendo reescritas durante a auditoria (arquivo de 19:17 x 19:20 x 19:25).
  - O tema claro foi capturado a 390 px em 5 cenas (painel, questão, revelada, verso, aula), em `tmp/ui_auditoria/claro/`. Para isso, um script de rascunho chamou as funções do `ui_capturas.py` com `?tema=light`.
- **Detector:** `impeccable detect --json` sobre `core/templates` + `tools/painel.py`, sobre o build `tmp/hub/index.html` e sobre `artifacts/painel.html`. A saída bruta está em `tmp/ui_auditoria/detect/{src,hub,painel}.json`.
- **Sem sobreposição no navegador.** A aba [Human] não foi aberta: o Chrome é compartilhado com colegas (regra da casa).
- **Snapshot em `.impeccable/critique/` não gravado**, porque o brief restringe a escrita a este arquivo.
- **Perguntas:** não houve como perguntar a ele, porque o subagente não tem canal com o operador. As perguntas estão na seção "Decisões dele", com opções.
- 🔒 **Nenhum conteúdo do UERJ 2026 foi aberto.** Só o título "UERJ 2026" aparece, nas listas do Painel e dos Simulados. Nenhum texto de questão foi citado além do que as capturas de listas antigas mostram (t96, t49).

---

## Sumário executivo

1. **Nenhum P0.** Nada impede de resolver uma lista, um simulado ou um lote de cards hoje. Também não há rolagem horizontal nem erro de JS em 11 cenas × 3 larguras.
2. **Saúde do design (Nielsen):** 27/40 em média, banda Aceitável, no topo dela. É o mesmo patamar de 19/10. O fluxo da questão (29) e a Teoria (29) são o melhor do hub. A tela de fim (24) segue sendo o ponto fraco.
3. **Audit técnico: 15/20 (Bom).** Desceu 1 ponto desde 19/10 (16/20). O motivo são os incrementos de 29-30/10, que deixaram pontas soltas: o P39 não chegou à RD, o P44 não chegou aos Simulados e o Virar sai do lugar.
4. **P1 nº 1, pré-existente mas exposto hoje: o Painel e as Listas discordam do "Hoje".** O Painel esconde a tarefa Tuberculose 360, porque a aula que a cumpre foi lida, mas continua contando as 20 questões dela. O Cronograma diz "80 q" e os cartões somam 60. A aba Listas mostra a lista no Hoje. É o tema nº 1 da UERJ.
5. **P1 nº 2, recente: o "‹ Listas" da questão muda de rótulo e de linha.**
   - No celular ele vira "‹ Lista", com outro destino, quando a lista está completa.
   - Ele também pula para a linha do título conforme o comprimento do título.
   - Isso contraria a regra dele de 30/10 ("posição fixa > elemento condicional").
6. **P1 nº 3, pré-existente desde 19/10: a meta em `tinta3` sobre o cartão tingido dá 4,4:1**, abaixo de AA. O teste de contraste só mede papel, card e afundado.
7. **Achados por prioridade:**
   - P0: 0.
   - P1: 4 (2 recentes ou expostos hoje, 2 herdados de 19/10).
   - P2: 14 (7 recentes, de 29-30/10).
   - P3: 7.
8. **Detector:** 342 achados. Cerca de 95% são falso-positivos sancionados pelo DESIGN.md: a faixa de área de 4 px (`side-tab` ×203 e `cramped-padding` ×77) e o sublinhado em gradiente da aba. Só 2 são verdadeiros: a meta a 4,4:1 e o "+N" do gráfico a 11,2 px.
9. **Nada aqui reverte P34-P44.** As correções propostas completam o que eles pediram e aplicam a regra dele de posição fixa onde ela ainda não chegou.
10. **Cinco quick wins cabem num tique**, sem decisão dele: acentos do player, `aria-pressed` na certeza, meta em `tinta2` no cartão tingido, título curto nos Simulados e "Resolver" apagado na RD.

---

## Achados priorizados

"Recente" = entrou em 29-30/10 (s235-s236, Versions 138-141). "Pré-existente" = já estava em 19/10 ou antes. Esforço: S (até ~30 min, 1 arquivo), M (meio tique, 2-3 arquivos ou decisão de copy), L (desenho novo).

### P0

Nenhum.

### P1

| ID | Tela | Achado | Evidência | Heurística | Correção mínima | Esf. | Origem |
|---|---|---|---|---|---|---|---|
| U1 | Painel x Listas | **O Hoje do Painel esconde uma lista pendente e conta as questões dela.** A tarefa 1797 (Tuberculose 360, rolada de 29/10) sai do Painel porque a aula `tb-360`, que a CUMPRE, foi lida. O `q_hoje` (80) continua contando as 20 questões. Os cartões visíveis somam 60 (49 + 11). A aba Listas mostra "Tuberculose 360 · 20 questões" no Hoje. A Próxima pula o tema nº 1 da UERJ. | `painel-390.png` × `listas-390.png`; `tools/painel.py:282-287` (filtro `feita` só pela aula lida); `hub-sprint` do build: `"hoje": [1797, 380, 740, 890]` | 1 Visibilidade, 4 Consistência | Só tirar do Hoje a tarefa com aula lida E sem lista pendente (a lista não resolvida mantém o cartão, com o "Abrir aula" já feito). Senão, subtrair as questões dela do `q_hoje` e tirar a lista das Listas › Hoje também. Teste em `test_painel.py` no mesmo padrão de `test_rd_lida_pela_assinatura_doc_sai_do_hoje`. | S | Pré-existente (regra s229 "concluída sai"), exposta hoje |
| U2 | Questão (celular) | **O voltar muda de nome e de lugar.** `qzBarra()` troca "‹ Listas" por "‹ Lista" quando a lista está completa, e os dois levam a destinos diferentes, separados por uma letra. A menos de 700 px, a ordem flex (`#qz-tema` 60% + relógio `order:-1`) deixa o voltar subir para a linha do título quando o título é curto ou o rótulo é menor. Em `questao-390` ele está na 2ª linha; em `revelada-390`, na 1ª. | `hub.html:583`, `:2799`, `:363-370`; `questao-390.png` × `revelada-390.png` | 4 Consistência, 3 Controle | Só CSS, sem mudar id nem ordem do DOM, que estão congelados por `test_ids_botoes_e_ordem...`. No celular, o título fica sozinho na 1ª linha e o relógio vai para o fim da 2ª (`#qz-tema{flex-basis:100%}`, sem `order:-1`). Assim o voltar fica sempre na 2ª linha, à esquerda. O rótulo do 2º destino é decisão dele (ver D2). | S | Recente (P38/P44, Version 140-141) |
| U3 | Painel (e provavelmente Listas) | **Meta a 4,4:1, abaixo de AA**: `tinta3` (#948FAA) sobre o fundo tingido pela área (`color-mix` 9%), por exemplo "49 questões". | detector `painel.json`: `4.4:1 -- #948faa on #322b30` e `on #262e35`; `tools/painel.py:1187,1204`; a mesma receita em `hub.html:291` (`.qz-meta`) | WCAG 1.4.3 (AA) | `.tarefa .t-meta{color:var(--tinta2)}` (e `.qz-lista li .qz-meta`), ou incluir o fundo tingido no `test_tema_contraste.py`. | S | Pré-existente (19/10, P2 do audit) |
| U4 | Fim de lista | **"Lista concluída" fica fixo enquanto o Concluir está travado** por declarações pendentes. O "Faltam N declarações" só aparece no rodapé, depois da parede de Elos. | `hub.html:635` (título estático), `:3233` (mensagem no pé) | 1 Visibilidade, 9 Recuperação | Com pendência, o `h2` diz "Falta declarar N" (o mesmo texto do `qz-fim-status`) e o botão continua onde está. | S | Pré-existente (19/10, P1 do critique) |

### P2

| ID | Tela | Achado | Evidência | Heurística | Correção mínima | Esf. | Origem |
|---|---|---|---|---|---|---|---|
| U5 | Listas › Simulados | **O título curto (P44) não chegou aos Simulados.** A linha usa `qzNomeSim`, que só corta em " -- ", e não `temaExibido`/`tituloCurto`. Os 2 cadernos UERJ 2017-2020 aparecem com o MESMO título técnico de 80 caracteres, "(filtro instituição=UERJ, anos 2017-2020)", porque o "parte 1/2" foi cortado. | `hub.html:2694`, `:2706`; `simulados-390.png` | 2 Mundo real, 4 Consistência | `qzNomeSim = tituloCurto(String(l.tema).split(" -- ")[0])`, preservando "parte N" quando houver irmãos. Antes, confirmar se os cadernos ainda estão no db vivo: o seed é de 29/10 23:39, e o fechamento s235 diz "cadernos 2017-2020 fora do hub". | S | Recente (P44 incompleto) |
| U6 | Painel › Cronograma | **A RD não assinada tem só "Abrir aula"; falta o "Resolver" apagado.** O P39 pede "todos devem ter os dois botões, sempre no mesmo local". | `tools/painel.py:956-963` (`_html_rd`); `painel-768.png`, `painel-1280.png` | 4 Consistência | Prefixar `_botao_apagado("Resolver", primario=True)` na `t-acao` da RD. Teste junto a `test_cartao_da_tarefa_tem_resolver_e_abrir_aula`. | S | Recente (P39 incompleto) |
| U7 | Cards (verso) | **O Virar some ao virar o card, e Pausar e Defeito deslizam para a esquerda.** A grade `auto auto auto` perde a 1ª coluna. Contraria a mesma regra de posição fixa. | `player.html:73`, `:601` (`btn-virar.hidden = true`); `cards-390.png` × `verso-390.png` | 4 Consistência | No verso, `visibility:hidden` em vez de `hidden` (o lugar fica), ou o Virar apagado. Os atalhos e a linha única do P37 continuam. | S | Recente (P37 + regra de 30/10) |
| U8 | Questão | **O relógio tem moldura de controle** (borda `linha-forte`, 44 px, raio de botão) e não é tocável. Ao lado de "Aa" e "‹ Listas", ele se lê como botão. Mostra "--:--" na revelada e "00:00" no fim. | `hub.html:359-360`, `:594`, `:2960`, `:3171` | 4 Consistência (afordância) | Tirar a borda (texto `tinta2` tabular, como era o `.qz-relogio` base) e usar um único estado parado ("--:--"). | S | Recente (P36) |
| U9 | Questão (celular) | **Os botões ‹ › do paginador têm 36 px de largura** a menos de 700 px. A regra da casa é 44 px, e 36 px só vale para os 3 compactos do card. | `hub.html:368` | Alvo de toque (DESIGN "Celular"; WCAG 2.5.5 AAA) | `min-width:44px` também no celular. A 390 ainda cabe: 44 + 40 + "de N" + 44. | S | Recente (s236) |
| U10 | Questão | **O "Responder" apagado se lê como 4ª opção da certeza**: mesma moldura `linha-forte`, fundo transparente, 44 px e vão de 8 px dos segmentos. | `hub.html:338-342`; `questao-390.png`, `questao-1280.png` | 4 Consistência, 8 Minimalismo | Vão maior antes dele (`#qz-antes{gap:var(--esp-4)}`) ou um filete vertical. Continua cinza até letra + certeza e à direita, como no P38. | S | Recente (P38) |
| U11 | Cards (player) | **Texto sem acento na tela**: "revisao vencida", "com esforco", "sem esforco", "Lote concluido", "Erro de portugues", "(Espaco)", "agendado p/ hoje". O aviso de banco fora vem em CAIXA-ALTA sem acento ("SEM CONEXAO COM O BANCO..."). | `player.html:221`, `:251-253`, `:259`, `:315`, `:318`, `:462-463`, `:791`; `verso-390.png` | 2 Mundo real, 9 Recuperação | Acentuar as strings e trocar a caixa-alta do aviso por peso/`.aviso.forte`. Conferir `test_player_js.py`, que pode casar o texto. | S | Pré-existente (19/10, P2) |
| U12 | Questão | **A certeza (Sólida/Dúvida/Chute) não tem `aria-pressed`.** O estado vive só na classe `.on`, então o leitor de tela não sabe qual foi marcada. | `hub.html:606-609`, `:343-346`; `aria-pressed` só no grifo e na declaração | WCAG 4.1.2 | `aria-pressed` nos 3 botões, alternado onde a `.on` é posta. | S | Pré-existente (19/10, audit) |
| U13 | Painel › Cronograma | **Dois resumos do Hoje com vocabulários diferentes.** A placa diz "Hoje: 3 tarefas · 80 questões + simulado (100 q)"; o dia diz "1 lista · 1 tarefa · 80 q + simulado (100 q)"; a aba Listas diz "3 listas · 80 questões". | `tools/painel.py:984-990` × `:926-947`; `painel-390.png` | 4 Consistência, 8 Minimalismo | Ficar só com o do dia (`rm-n`) e tirar o `p.sub` do Cronograma. Um vocabulário: o das Listas. | S | Pré-existente (19/10) |
| U14 | Painel x Listas | **A mesma tarefa tem área e cor diferentes nas duas abas.** "Oncologia Ortopédica" é CM/ciano no Painel (rótulo = bloco do sprint) e Ortopedia/rosa (CIR) nas Listas. Arboviroses é CM no Painel e "Infecto" nas Listas. | `tools/painel.py:151`; `hub.html:2675` (`qzGrande(l.area)`); `painel-1280.png` × `listas-1280.png` | 4 Consistência | Um rótulo só. Ver D3. | M | Pré-existente (19/10, "padronizar área") |
| U15 | Fim de lista | **"Erradas: 1, 4, 5..." e "não firmes: Q5, Q13" são texto puro.** Os Elos são tocáveis (`button[data-rev]`), mas esses números não. | `fim-390.png`; `hub.html:3206`, `:3236` | 6 Reconhecer > lembrar | Cada número vira o mesmo `button[data-rev]` dos Elos. | M | Pré-existente (19/10) |
| U16 | Leitor (RD) | **Três matizes de realce no mesmo parágrafo:** termo-chave em negrito ciano (s224), dado decisivo em rosa (s236), sobrescrito de referência em ciano (este é link) e numeral roxo. O ciano negrito, que não é link, ao lado do ciano que é link lê como link. | `aula2/aula-390.png`, `aula2/aula-1280.png` (seção 01) | 4 Consistência, 8 Minimalismo | Decisão dele, sem reverter nada (ver D4). | M | Pré-existente, ampliado pela regra Rosa Realça (s236) |
| U17 | Leitor (RD refeita hoje) | **O rótulo "coágulo" da Fig 1 colidiu com o título "TEP maciço"** no SVG, a 390 e a 1280 (captura de ~19:21). Na versão de ~19:24 (tema claro) a colisão já não aparece. | `aula2/aula-390.png`, `aula2/aula-1280.png` × `claro/aula-390-claro.png` | 8 Estética (legibilidade) | Antes de publicar, conferir as 5 `rd-*-2910` a 390 nos dois temas (`ui_capturas.py --cenas aula`, com `?doc=` de cada uma). | S | Recente (em edição hoje) |
| U18 | Cards | **"197 de 100 hoje" aparece com a barra vazia e o tally 1:0 2:0 3:0 4:0.** O topo mistura o saldo do dia (Painel) com o lote no ar. | `cards-390.png` | 1 Visibilidade | Já é o A19 do DESIGN.md (mesmo PRD do contador do dia). | M | Pré-existente (A19) |

### P3

| ID | Achado | Evidência | Correção | Origem |
|---|---|---|---|---|
| U19 | O "+12" do gráfico Flashcards da semana tem 11,2 px (`.7rem`), abaixo do degrau meta (13 px). | `tools/painel.py:1168`; detector `design-system-font-size` | `font-size:var(--fs-meta)` | Pré-existente |
| U20 | O `.t-btn-off` usa borda `--linha`, invisível sobre o cartão tingido, mas o DESIGN.md diz "contorno e texto em `tinta3`". Código e documento divergem. | `tools/painel.py:1220`; DESIGN.md §Botões de tarefa | Alinhar um dos dois. | Recente (P39) |
| U21 | O hub não tem `h1`: a marca é `<p>` e as telas começam no `h2`. | `hub.html:522` | `h1` visualmente igual na marca, ou `h1` por aba. | Pré-existente |
| U22 | Na revelada, o × de riscar segue visível (desabilitado) em toda alternativa. É ruído na tela de "no máximo 3 blocos". | `hub.html:2908`; `revelada-390.png` | Esconder `.qz-risca[disabled]` na revelada. | Pré-existente |
| U23 | O Google Fonts pede 6 pesos (300;400;500;600;650;700). O 300 e o 500 não aparecem no DESIGN.md. | `tmp/hub/index.html` e `artifacts/painel.html` (`<link>`) | Pedir `wght@400;600;650;700`. | Pré-existente |
| U24 | O título do documento aparece duas vezes no leitor (barra + H1 da aula). O resumo repete o texto exato. | `resumo-390.png`, `aula2/aula-390.png` | Fica: a barra com o título é o P44 (pedido dele). Só registrar. | Pré-existente, decisão dele |
| U25 | No mesmo 390, o leitor mostra "Aa Grifo" e a questão só "Aa". O P42 pediu "a mesma barra das Listas". | `hub.html:365` (`#qz-player .hub-grifo-rot{display:none}` só na questão) | Igualar (a regra vale para os dois ou para nenhum). | Recente (P42) |

---

## Scores do critique por tela (Nielsen, 0-4)

| # | Heurística | Painel | Teoria | Listas | Questão | Fim | Cards | Leitor |
|---|---|---|---|---|---|---|---|---|
| 1 | Visibilidade do estado | 2 | 3 | 3 | 3 | 2 | 2 | 3 |
| 2 | Mundo real | 3 | 3 | 2 | 3 | 3 | 3 | 3 |
| 3 | Controle e liberdade | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| 4 | Consistência | 2 | 3 | 2 | 2 | 3 | 2 | 3 |
| 5 | Prevenção de erro | 3 | 3 | 3 | 4 | 3 | 3 | 3 |
| 6 | Reconhecer > lembrar | 3 | 3 | 3 | 3 | 2 | 3 | 3 |
| 7 | Flexibilidade | 2 | 2 | 2 | 3 | 2 | 3 | 2 |
| 8 | Estética e minimalismo | 3 | 4 | 3 | 3 | 2 | 3 | 3 |
| 9 | Recuperar de erros | 3 | 3 | 3 | 3 | 2 | 3 | 3 |
| 10 | Ajuda | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| | **Total /40** | **26** | **29** | **26** | **29** | **24** | **27** | **28** |

**Leitura:** média de 27/40, banda Aceitável (no topo). Por tela:

- **Painel:** perde na visibilidade e na consistência (U1, U13, U14).
- **Teoria:** limpa, mas uma biblioteca de 98 itens não tem busca (heurística 7). Ele não pediu, então fica registrado e não proposto.
- **Listas:** jargão de bastidor ("Fora do sprint · 66", título técnico do caderno), e as 3 linhas do Hoje têm 3 botões primários cheios em coluna.
- **Questão:** o melhor fluxo do hub. O Responder só libera com letra + certeza, e há atalhos A-E, 1-5, S/D/C e Enter. Perde só na consistência do cabeçalho (U2, U8, U10).
- **Fim:** o pior. O título contradiz o portão (U4), os números não são tocáveis (U15) e a parede de Elos abre com o "Não". Pela regra pico-fim, é o momento de que ele mais lembra.
- **Cards:** copy sem acento (U11), controles que deslizam (U7) e o topo misturando o dia com o lote (U18).
- **Leitor:** medida boa, figura e tabela legíveis. A densidade de realce é a questão em aberto (U16).

**Carga cognitiva** (checklist de 8 itens): 3 falhas, ou seja, moderada.
- Agrupamento: a parede de Elos do fim, com ~40 itens sem corte.
- Foco único: 3 primários iguais no Hoje das Listas.
- Memória de trabalho: o "Erradas: 1, 4, 5..." pede que ele lembre qual era qual.

**Jornada emocional:**
- O pico é a revelada, com a cadeia e o veredito claros.
- O vale é o fim de lista, que fecha com o "Não" em coral e um título que mente sobre o estado.

**Veredito de especificidade:** o hub é **autoral**. Atkinson, placa fosca com fio cromado, linha do horizonte, tríade de certeza, cadeia de elos com 4 estados e notas do FSRS na voz dele não cabem em outro produto.
- As duas zonas genéricas são as mesmas de 19/10 (anéis de app fitness e barras de tarefa com faixa lateral), e ambas são decisões documentadas dele.
- O que mais erodiu a especificidade desde 19/10 não foi estético: foram regras dele aplicadas em parte (posição fixa, título curto).

### Bandeiras por persona

- **Casey (celular, entre plantões, uma mão):**
  - o voltar muda de linha entre questões (U2);
  - os ‹ › têm 36 px (U9);
  - o relógio parece botão e não faz nada (U8);
  - no Cards, depois de virar, o dedo que ia no Pausar acha o Defeito (U7).
- **Sam (leitor de tela, teclado):**
  - a certeza não anuncia o estado (U12);
  - a meta a 4,4:1 (U3);
  - o "Abrir aula" apagado é um `span` com `aria-disabled`, sem papel de botão: lido como texto, aceitável, mas sem semântica (U20);
  - sem `h1` (U21).
  - **O que funciona:** foco visível global de 2 px ciano, abas com `role=tab` e `aria-selected`, alternativas como `radio` com `aria-checked`.
- **Alex (uso intenso, sem paciência):**
  - o Painel diz 80 q e mostra 60 (U1);
  - "3 tarefas", "1 lista · 1 tarefa" e "3 listas" para o mesmo dia (U13).
  - A boa notícia: os atalhos de teclado da questão e do card seguem lá, mesmo sem a legenda.

---

## Audit técnico (0-4)

| # | Dimensão | Nota | Achado-chave |
|---|---|---|---|
| 1 | Acessibilidade | 3 | Foco 2 px global, ARIA de abas, radios e grifo ok. Faltam `aria-pressed` na certeza (U12), contraste do cartão tingido (U3) e `h1` (U21). |
| 2 | Performance | 3 | Página de 617 KB: ~205 KB de JS do hub, 32 KB de JS auxiliar, 71 KB do lote embutido, 64 KB de CSS e ~240 KB de marcação. Painel e leitor em 2 iframes. Fonte variável pedida em 6 pesos (U23). Nada patológico; o lote embutido é o maior candidato se pesar no 4G. |
| 3 | Tematização | 3 | Dois temas conferidos em captura real (claro a 390, 5 cenas, sem quebra). O fundo tingido escapa do teste de contraste (U3). Cor literal fora do `tema.css` só no `#fff` das figuras (justificável) e no fallback `#b3261e`. |
| 4 | Responsivo | 3 | Zero rolagem a 390/768/1280. O cabeçalho da questão reflui conforme o conteúdo (U2) e o paginador tem 36 px (U9). |
| 5 | Integridade | 3 | O sistema é coerente e tem dono. Os incrementos de 29-30/10 deixaram regra aplicada pela metade (U5, U6, U7, U20, U25). |
| | **Total** | **15/20** | **Bom** (atacar 1 e 5) |

**Veredito de integridade: passa.** O hub segue expressando um sistema próprio e verificável: tokens só no `tema.css`, `.placa` única, contratos travados por teste.

O risco novo é de **processo**: regra pedida por ele aplicada numa tela e não nas irmãs. A "posição fixa" foi aplicada no Painel e não no Cards, na RD nem no cabeçalho da questão. O "título curto" chegou às Listas e não aos Simulados. Vale uma varredura por regra a cada pedido, não por tela.

**Positivo, para manter:**
- leitura resiliente com "Tentar de novo";
- "estado nunca só por cor" (✓ ✗, "mais fraco", nome no botão da declaração);
- Responder travado até letra + certeza;
- zero `outline:none` em todo o código;
- `prefers-reduced-motion` respeitado;
- nenhum `sticky`, `fixed` ou `nowrap` quebrando a 390.

### Cruzamento com os "Contratos travados por teste" (DESIGN.md)

- **U2:** a correção tem que ser só CSS, porque ids, botões e ordem estão congelados por `test_ids_botoes_e_ordem_da_questao_e_do_leitor_nao_mudaram`.
- **U3:** o `test_tema_contraste.py` mede 3 superfícies, e o cartão tingido é uma 4ª. A correção certa inclui o teste.
- **U6:** o `test_cartao_da_tarefa_tem_resolver_e_abrir_aula` cobre a tarefa e não a RD. Estender.
- **U9:** o "44 px nos botões" do `test_forma_da_tela_revelada` não olha o `@media (max-width:699px)` do paginador.
- **Nenhuma correção proposta reintroduz** `sticky`, `nowrap`, sombra, caixa por número ou micro-dica.

---

## Achados do detector

| Regra | Onde | Nº | Veredito |
|---|---|---|---|
| `side-tab` | build: `.tarefa`/`.qz-lista li` (faixa de área de 4 px), `.hub-aviso` e `.aviso` (filete âmbar de 3 px), `.hub-assina-retorno` | 203 + 3 | **Falso positivo sancionado** (DESIGN.md: "Barra do Cronograma", "Aviso", "callouts usam filete à esquerda"). O `.hub-assina-retorno` usa filete CIANO numa confirmação estática, o que dobra "ciano = interação" (P3, herdado de 19/10). |
| `cramped-padding` | `painel.html` `li.tarefa` | 77 | **Falso positivo**: a `.t-faixa` encosta na borda de propósito. |
| `low-contrast` 1,5:1 | `button#hub-tab-painel` | 1 | **Falso positivo**: o gradiente é o sublinhado de 2 px; o texto fica sobre o fundo (~17:1). |
| `low-contrast` 4,4:1 | `painel.html`, `tinta3` sobre fundo tingido | 2 | **Verdadeiro**, é o U3. |
| `design-system-color` | `tema.css:50,81-84` (claro e cromado do claro) | 8 + 10 | **Drift de documento**, não de código: os hex do tema claro moram no `tema.css` (a fonte única) e só na prosa do DESIGN.md, não no frontmatter nem no sidecar. Os `background rgb(...)` do painel são o `color-mix` da área (sancionado). |
| `design-system-color` | `hub.html:463` `#fff`; `hub.html:1234` `#b3261e` | 2 | `#fff` = moldura branca da figura da questão (justificável; poderia virar token). `#b3261e` = fallback em `var(--erro,#b3261e)` (falso positivo). |
| `design-system-font-size` | marca 1,375rem, pergunta do card `clamp(1.2rem…)`, manchete da aula `clamp(30px…44px)`, anel 30 px | 15 | **Falso positivo**: todos documentados na prosa do DESIGN.md (Typography); o frontmatter não os tem. Exceção verdadeira: `.ag-mais` 0,7rem (U19). |
| `design-system-radius` | 1, 2, 3, 4 e 8 px | 11 | 2 px = segmento do trilho (documentado); 8 px = formulário injetado nos documentos (`pendEstilo`, `:where()`); o resto são resíduos de legado. Advisory. |
| `flat-type-hierarchy` | painel (h3 = corpo = 14 px) | 1 | Parcialmente verdadeiro e deliberado: o peso separa (achado de 19/10, aceito). |

**Total:** 342 achados (27 na fonte, 222 no build, 93 no painel). Verdadeiros: 3 (U3 ×2, U19). Drift de documento: ~30 (frontmatter/sidecar desatualizados em relação à prosa e ao `tema.css`; rodar `/impeccable document` quando ele puxar).

---

## Quick wins (cabem num tique, sem decisão dele)

1. **U11, acentos no player:** "revisão vencida", "com esforço", "sem esforço", "Lote concluído", "Erro de português", "(Espaço)". O aviso de banco fora vai para texto comum com `.aviso.forte`. Só strings em `player.html`, e talvez `test_player_js.py`.
2. **U12, `aria-pressed` na certeza:** markup inicial `false` nos 3 botões de `#qz-seg` e alternância onde a `.on` é posta.
3. **U3, meta legível no cartão tingido:** `.tarefa .t-meta` e `.qz-lista li .qz-meta` em `tinta2`, mais o fundo tingido no `test_tema_contraste.py`.
4. **U5, título curto nos Simulados:** `qzNomeSim` passa por `tituloCurto`, preservando "parte N". Uma linha em `hub.html` e um caso em `test_hub_render.py`.
5. **U6, "Resolver" apagado na RD:** uma chamada a `_botao_apagado` em `_html_rd` e um caso no teste do cartão.

Logo atrás, também S: U9 (paginador a 44 px), U7 (o Virar guarda o lugar) e U8 (relógio sem moldura).

---

## Decisões dele (perguntas fechadas, para o agente de estudo levar)

- **D1 (U1): tarefa com aula lida e lista pendente.**
  - (a) O cartão fica no Hoje até a lista ser resolvida, com o "Abrir aula" como feito.
  - (b) O cartão sai e as questões saem do total, das Listas e do Painel.
  - (c) Fica como está.
  - Recomendação: (a), porque o tema nº 1 da UERJ não some da Próxima.
- **D2 (U2): o voltar que leva ao fim da lista quando ela está completa.**
  - (a) Sempre "‹ Listas" (um destino, um rótulo), e o fim abre pelo paginador.
  - (b) Rótulo distinto, por exemplo "‹ Resultado".
  - (c) Fica "‹ Lista".
  - Recomendação: (a).
- **D3 (U14): rótulo da área no cartão.**
  - (a) Grande área UERJ (CM/CIR/MFC/PED/GO) nas três abas.
  - (b) Disciplina (Infecto, Ortopedia) nas três abas.
  - (c) Bloco do sprint no Painel e disciplina nas Listas (como hoje).
  - Recomendação: (a), porque a faixa colorida já é a grande área.
- **D4 (U16): realce na leitura depois do rosa.**
  - (a) Termo-chave em branco 650, e o rosa vira o único realce colorido do texto.
  - (b) Termo-chave segue ciano (s224) e o rosa entra só no dado decisivo (como hoje).
  - (c) Termo-chave em `roxo-tinta`.
  - Sem recomendação forte: (a) resolve o "ciano lê como link", mas desfaz um pedido dele de 12/10.
