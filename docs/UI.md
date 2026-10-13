---
type: reference
status: active
relates_to: [core/templates/tema.css, core/templates/hub.html, core/templates/player.html, tools/painel.py, core/templates/tema-aula.css]
---

# UI do MedHub -- design system, mapa e achados

> Porta de entrada de qualquer trabalho visual no MedHub. Criado na s225 (13/10/2026), na rodada "refinamento visual,
> design system e simplificação do frontend" pedida pelo operador. Regra que muda aqui muda junto no código e no teste
> que a trava (§7). Memória do harness sobre UI é só ponteiro para este arquivo.

## 1. Direção

**Retrowave contido**: Vaporwave/Retrowave inspirado em GTA Vice City, reinterpretado como ferramenta de estudo
médico. Princípio (do brief dele, 13/10/2026): *"a interface deve lembrar Vice City à primeira vista, mas desaparecer
em segundo plano quando o estudante estiver concentrado no conteúdo."*

Prioridade, nesta ordem: (1) clareza e baixa carga cognitiva; (2) legibilidade e acessibilidade; (3) hierarquia e
consistência entre telas; (4) minimalismo funcional; (5) identidade retrowave deliberada e contida; (6) código simples.

Ele lê **no celular (390 px), à noite, entre plantões**. Toda decisão é conferida primeiro a 390 px.

A identidade mora em poucos lugares: a marca (`Med` + `Hub` em rosa), a **linha do horizonte** sob as abas (o único
gradiente da UI: rosa -> roxo -> ciano) e o roxo do gráfico de previsão do Painel. O resto é tipografia, filete e
espaço.

## 2. Onde mora cada coisa

| Camada | Arquivo | O que tem | Quem recebe |
|---|---|---|---|
| Tokens + base | `core/templates/tema.css` | as duas paletas (escuro padrão, claro por `data-theme="light"`), escalas de espaço, raio e tipo, apelidos legados e das aulas, base comum (fonte, foco, seleção, movimento) | shell do hub, painel, player standalone, leitor de aulas e resumos |
| Casca, Teoria, Listas, leitor | `core/templates/hub.html` (bloco `<style>`, depois de `/* @hub:player-css */`) | abas, Teoria (`qd-*`), Listas e questão (`qz-*`), barra do leitor, assinatura de leitura (`hub-assina*`) | o hub |
| Cards | `core/templates/player.html` (região `@player:css`) | o player FSRS e a tela de fim | o hub (aba Cards) e o standalone do `fsrs_queue.py --build-player` |
| Painel | `tools/painel.py` (constante `CSS`) | Hoje, Ritmo, Semana, Blocos, Documentação | `artifacts/painel.html` (iframe no hub) |
| Leitor de aulas e resumos | `core/templates/tema-aula.css` | a camada de leitura sobre o CSS próprio de cada aula (43 em `artifacts/aula-*.html`) e da página de resumo | só o leitor (injetada depois do `tema.css`) |
| Página de resumo | `tools/hub.py` (constante `CSS_RESUMO`) | paleta e estrutura próprias da página de resumo publicada | a página aberta fora do leitor; no leitor o tema vem por cima |
| CSS injetado pelo JS do hub | `core/templates/hub.html`: `painelListas` (selos e "+N" no painel), `pendEstilo` (formulário de pergunta nos documentos), `grifoEstilo` (marca-texto no leitor) | estilos que o hub põe dentro dos iframes | painel e leitor |

Como entra: o `tools/hub.py --build` injeta o `tema.css` no fim do `<style>` do shell (marcador `/* @hub:tema-css */`)
e, junto com o `tema-aula.css`, no leitor (`"@hub:tema-js"`, aplicado no `srcdoc` de cada aula/resumo); o
`tools/painel.py` embute o `tema.css` depois do próprio CSS; o `--build-player` embute antes do `</head>`
(`fsrs_queue.embutir_tema`).

**Regra de casa:** cor literal só no `tema.css`. Componente mora no arquivo da tela, nunca no `tema.css`. Trocar a
paleta = trocar os dois blocos de cor do `tema.css`, montar o hub em scratch e conferir (§8) antes de publicar.

## 3. Tokens

Seletores `:root:not([data-theme="light"]),:root[data-theme="dark"]` (escuro) e `:root[data-theme="light"]` (claro), de
especificidade (0,2,0) de propósito: vencem o `@media` escuro que cada aula traz no próprio CSS.

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `--papel` | `#17132E` | `#F7F5FB` | fundo da página |
| `--card` | `#211C3A` | `#FFFFFF` | superfície secundária: card do player, alternativa, assinatura |
| `--afundado` | `#29233F` | `#EFEBF7` | superfície elevada/selecionada; trilho vazio; badge |
| `--linha` | `#403858` | `#DCD5E8` | divisória e filete (decorativo) |
| `--linha-forte` | `#776E99` | `#8E87AD` | borda de controle (campo, botão secundário): >= 3:1 |
| `--tinta` | `#F8F5F2` | `#1C1733` | texto principal, títulos, pergunta |
| `--tinta2` | `#B8B3CC` | `#4B4466` | texto secundário, rótulos |
| `--tinta3` | `#9C96B6` | `#625B7E` | metadados |
| `--acento` / `-tinta` / `-fraco` | `#00D9E8` / `#7DE8F0` / `#13334C` | `#00737D` / `#005A62` / `#DDF1F4` | ciano: interação |
| `--rosa` / `-fraco` | `#FF4FA3` / `#3C1D41` | `#C2176F` / `#F8E1EE` | marca e destaque pontual |
| `--roxo` / `-tinta` / `-fraco` | `#AA71E8` / `#BE95F0` / `#2F224C` | `#7443B8` / `#5E3596` / `#ECE3F8` | decoração, dado visual, desatenção e chute |
| `--ok` / `-fraco` | `#79D6A5` / `#273241` | `#1E7348` / `#E2F2E8` | sucesso |
| `--erro` / `-fraco` | `#FF7C87` / `#3C243C` | `#B8303E` / `#FBE5E8` | erro (coral) |
| `--aviso` / `-fraco` | `#FFBE72` / `#3C2E39` | `#8F5200` / `#FAEBD7` | aviso e atraso (âmbar) |
| `--sobre` | `#17132E` | `#FFFFFF` | texto sobre preenchimento (botão primário, declaração ligada) |
| `--qz-grifo` / `-tinta` | `#FFD447` / `#17132E` | `#FFE066` / `#1C1733` | marca-texto (literal: o hub lê o valor computado para o leitor) |
| `--horizonte` | rosa -> roxo -> ciano | idem, escuros | a linha sob as abas |

Contraste medido (WCAG 2.x) no escuro, sobre `papel` / `card` / `afundado`: `tinta` 16,5 / 15,0 / 13,8; `tinta2`
8,9 / 8,0 / 7,4; `tinta3` 6,4 / 5,8 / 5,3; `acento` 10,3 / 9,4 / 8,6; `erro` 7,3 / 6,6 / 6,0; `aviso` 11,0 / 9,9 / 9,1;
`ok` 10,2 / 9,3 / 8,5; `rosa` 5,9 / 5,3 / 4,9. O `roxo` puro fica em 4,4 sobre `afundado`: texto roxo usa `--roxo-tinta`
(6,2+). `--sobre` sobre os preenchimentos: 5,3 (roxo) a 11,0 (aviso). No claro, todos os textos >= 4,8 sobre
`afundado`, exceto `acento` sobre `acento-fraco` (4,4): texto sobre a lavagem ciano usa `--acento-tinta`.

Apelidos: `--alerta` = `--erro` (nome antigo); `--qz-ok/-duv/-chute` = ok/aviso/roxo-tinta; `--suave` = roxo. As aulas
usam nomes próprios em inglês: `--paper --ink --ink2 --ink3 --line --line2 --sunk --card --on`, `--teal*` (= acento),
`--amber*` (= aviso), `--plum*` (= roxo), `--carmine*` (= erro).

Escalas (em `:root`, valem nos dois temas):
- espaço: `--esp-1` 4 · `--esp-2` 8 · `--esp-3` 12 · `--esp-4` 16 · `--esp-5` 24 · `--esp-6` 32 · `--esp-7` 48 px;
- raio: `--raio` 10 px (cartões e controles) · `--raio-p` 6 px (kbd, grifo, aviso) · `--raio-pilula` (só badge e chip);
- tipo: `--fs-pagina` 1,5rem · `--fs-secao` 1,125rem · `--fs-item` 1rem · `--fs-legenda` .875rem · `--fs-meta` .8125rem ·
  `--fs-numero` 2rem;
- coluna: `--wrap` 46rem (um `.wrap` só por página; ~85 caracteres por linha no desktop).

Tipo: **Atkinson Hyperlegible Next**, uma família só (decisão dele, s224: 0/O e 1/l distintos em dose e corte), com
algarismos tabulares e sem caixa-alta (`text-transform:none` global).

## 4. Semântica das cores

- **Ciano**: navegação ativa (aba, segmento), foco, progresso (barras, trilho atual, o "necessário por dia"), ação
  primária (botão `.primario`), o rótulo "Próxima" do Painel e link. Nunca título nem rótulo.
- **Rosa**: a marca e destaque pontual (`nova` na Biblioteca). Nunca estado.
- **Roxo**: decoração e dado visual (gráfico de previsão, número do degrau das aulas) e os estados chute/desatenção.
- **Amarelo**: marca-texto (grifo).
- **Verde / coral / âmbar**: sucesso, erro, aviso. Atraso é aviso (âmbar), não erro.
- **Branco suave**: pergunta, resposta, títulos, conteúdo. **Lavanda**: secundário e metadado.
- Estado nunca só por cor: gabarito `✓`, errada `✗`, chute `?`, resolvida `✓`, "abaixo do necessário" por extenso,
  declaração com o nome do estado no botão.
- A declaração dos elos (`Sim / Incerteza / Desatenção / Não`) e a nota do card (`1 falhei / 2 com esforço /
  3 lembrei / 4 sem esforço`) seguem a mesma escala: ok, aviso, roxo, erro / erro, aviso, ok, acento.

## 5. Componentes

| Padrão | Onde | Forma |
|---|---|---|
| Linha de lista | Teoria (`.qd-bloco`), Listas (`.qz-lista button`), Painel (`.tarefa`), revisão (`.qz-rev`), por bloco (`.qz-porobj li`), cadeia (`.qz-cadeia li`) | sem fundo e sem caixa; filete de baixo (`--linha`); título 600 em `tinta`, meta em `tinta3` |
| Moldura | card do player, alternativa da questão, campo, assinatura de leitura | só o que é objeto de toque ou o foco da tela; `--card` + `--linha` + `--raio`; sem sombra |
| Badge | área (`.qd-bl`, `.t-rot`), objetivo (`.qz-obj`), "Próxima" | pílula, `--afundado` + `tinta2` (o "Próxima" em ciano) |
| Chip de estado | lista (`.qz-chip`, `qzChip`) | só fora do normal: "pronta" não tem chip; em curso = aviso com respondidas/total (espelho do aparelho); resolvida = ok + `✓` |
| Botão | global (`player.html`) | secundário: contorno `--linha-forte`, fundo transparente; `.primario`: ciano com texto `--sobre`; `.fantasma`: tracejado; 44 px de altura |
| Segmentado | Questões/Simulados (`.qz-modo`), certeza (`.qz-seg`), declaração (`.qz-decl`) | raio de controle; ligado = cor do estado + lavagem |
| Abas | `.hub-aba` | texto; ativa em `tinta` com sublinhado ciano de 2 px; o filete de baixo é o horizonte |
| Métricas | fim da lista (`.qz-tiles`), fim do lote (`.fim-grade`), Ritmo (`.fig`) | uma faixa entre dois filetes, número 700 + rótulo `tinta3`; sem uma caixa por número |
| Aviso | `.hub-aviso`, `.aviso` (player) | filete âmbar de 3 px + lavagem âmbar; `.aviso.forte` (banco fora) com borda inteira |
| Trilho | `.qz-trilho i` | 10 px visíveis, 26 px de toque; respondida = `--linha-forte`, atual = ciano, marcada para revisar = base âmbar (`flag`), vazia = `--afundado` |
| Barra de progresso | painel (`.barra`), player (`.barra`, `.dist-barra`) | 6-8 px, trilho `--afundado`, preenchimento sólido ciano |
| Leitura resiliente | `assinarResiliente(consulta, onDados, opts)` no `hub.html`: listas, quadro da Teoria, questões/respostas/análises da lista aberta, notas do lote | `consulta(db)` monta a referência sobre o `db` recebido (1ª tentativa = `opts.db`; da 2ª em diante e no "Tentar de novo", conexão nova por `claude.use("db")`, avisada em `opts.aoReconectar` -- o `QZ.db`); erro = `console.warn("[hub] leitura <coleção> falhou", código, tentativa)` + nova assinatura em 1/2/4 s com "Carregando…"; esgotadas, a mensagem + botão `.primario` **Tentar de novo** (`htmlRetentar`); reabrir a aba com ela morta reassina; um estado por assinatura, nunca 2 ouvintes. Aba nova lê por ela |
| Secções do card | `.bloco` (regra-mestre), `.bloco.alerta` (armadilha) | filete à esquerda (neutro / âmbar), nunca caixa dentro do card |

## 6. Telas: o que cada uma prioriza

- **Painel**: responde, nesta ordem, o que fazer hoje (Hoje), quanto avancei (Ritmo, Blocos) e o que vem depois.
  Com o sprint gravado (s226, `plano.agenda_sprint`, a fonte única do "hoje" do Painel, da aba Listas e do boot), o
  bloco das tarefas é **Hoje** (as tarefas do dia, a que rolou de um dia passado sem rótulo de atraso, o total de
  questões, "+ N cards" que faltam da dose do dia e a RD não assinada mais antiga, a linha inteira abrindo o leitor)
  + **Próximos dias** (um dia por linha, "qua 14/10 · 2 listas · 72 q", recolhido) + **Fora do sprint · N**
  (recolhido, agrupado pelo motivo). Sem "Semana", "Atrasadas", "Desta semana" nem "Até a prova". Sem sprint
  (`dia_plano` todo NULL), a semana antiga: o subtítulo "Atrasadas · N" em âmbar, uma vez, nunca por linha. Nos
  dois, a 1ª tarefa leva só o rótulo "Próxima", `li.tarefa.proxima`, o mesmo controle das outras. Na Semana, a tarefa com questões no
  hub é UM alvo (`a.t-alvo` com `data-hub-aba`: a linha inteira abre a lista); a aula ligada fica fora dele, pequena
  ("aula"). Fora do hub (lista externa, PDF), a coluna de ação de antes. O Ritmo fica logo abaixo de Hoje (pedido
  dele, s221).
- **Teoria**: linhas; o aviso de atraso aparece uma vez, no título da seção "Atrasadas"; a linha inteira abre a aula.
- **Listas e simulados**: o trilho é navegação; a questão revelada tem no máximo 3 blocos (alternativas com o porquê,
  veredito, cadeia com a declaração); a tela de fim mostra a faixa de métricas, o por bloco, o bloco Elos e a revisão.
- **Leitor de aulas**: uma coluna só (`.wrap` de 46rem; a aula antiga com trilho lateral usa o `main` de 38rem);
  títulos brancos, rótulos lavanda; termo-chave em negrito ciano claro (pedido dele, s224: o único texto ciano da
  leitura); callouts por significado (§9).

**Largura (regra dele, reprovada duas vezes quando quebrou):** UM `max-width` no contêiner (`.wrap`) e todos os
filhos herdam 100% dele. Nunca `max-width` por elemento (parágrafo, lede, lista) ao lado de quadro com fundo ou
borda: as bordas direitas fazem zigue-zague. Exceção: manchete sem caixa (`.top h1`).
- **Cards**: o card é o único objeto com moldura; pergunta > resposta > regra/armadilha > assunto.

## 7. Contratos travados por teste

| Contrato | Teste |
|---|---|
| nada `sticky`/`fixed`, nada `nowrap`, um `.wrap` só | `test_hub.py::test_celular_sem_sticky_sem_nowrap_e_um_wrap_so`, `test_painel.py::test_celular_sem_sticky_sem_nowrap_e_grid_item_encolhe`, `test_hub_render.py::test_forma_da_tela_revelada` |
| abas com rótulo curto e 44 px; `.qd-tema` com `min-width:0` | `test_hub.py::test_abas_curtas_e_com_alvo_de_toque` |
| tela revelada sem cor literal; 44 px nos botões; `.qz-cadeia li` com `min-width:0` | `test_hub_render.py::test_forma_da_tela_revelada` |
| player e painel sem cor literal (a cor mora no `tema.css`); tema escuro/claro presente na página pronta | `test_fsrs_queue_player.py::test_template_real_e_injetavel_e_tem_wrap_unico`, `test_painel.py::test_html_obedece_o_contrato_de_render` |
| standalone do player recebe o tema | `test_fsrs_queue_player.py::test_embutir_tema_entra_antes_do_head_e_e_idempotente` |
| linha da Teoria acessível (foco de 3 px, sem-aula sem cara de botão) | `test_hub_quadro.py::test_p21_cartao_alvo_e_acessivel_e_o_sem_aula_nao_parece_botao` |
| Painel com sprint: Hoje / Próximos dias / Fora do sprint, sem semana nem atraso; sem sprint, a semana antiga | `test_painel.py::test_painel_sprint_sem_semana`, `test_hoje_do_sprint_soma_os_cards_do_dia_e_a_rd_nao_assinada`, `test_sem_sprint_o_painel_mostra_a_semana_antiga` |
| painel sem jargão de bastidor (inclusive nos comentários do `tema.css`, que viaja embutido) | `test_painel.py::test_html_sem_jargao` |
| leituras das abas pela assinatura resiliente (retentativa, botão, 1 ouvinte); chip só fora do normal; marca 1,375rem | `test_hub_render.py::test_listas_se_recuperam_da_falha_de_leitura`, `test_botao_tentar_de_novo_reassina`, `test_leituras_das_abas_passam_pela_assinatura_resiliente`, `test_chip_da_lista_so_fora_do_normal` |
| a retentativa pede conexão nova ao banco (e o `QZ.db` passa a ser ela) | `test_hub_render.py::test_retentativa_pede_conexao_nova` |
| o `max-width` aparece no máximo 2 vezes na página do player e na do painel | os dois testes de contrato acima |

## 8. Como conferir (obrigatório antes de publicar tela nova)

Regra da casa: tela nova do hub só publica conferida em navegador real, a 390 px. Caminho:
1. `python tools/painel.py --html` e `python tools/hub.py --build --lote <lote vivo> --publicado <listagem> --quadro-estado tmp/hub_db`.
2. Capturas com banco falso no Edge headless, a 390, 768 e 1280 px: `python tools/ui_capturas.py` (11 cenas: painel,
   teoria, listas, simulados, questao, revelada, fim, cards, verso, aula, resumo; mede rolagem horizontal e erro de JS;
   assinatura e limites em `/engenharia-cli`). Saída em `tmp/ui_capturas/<data>/`. O seed vem dos dumps locais do db do hub em `tmp/` (conteúdo do EMED: nunca no git).
3. Ler as capturas (ferramenta Read) e conferir: hierarquia, rolagem horizontal, estados e contraste.
4. Rodar as suítes `tools/test_hub*.py tools/test_painel.py tools/test_fsrs_queue_player.py`.

## 9. Leitor de aulas (`tema-aula.css`)

Inventário completo das 43 aulas (s225, medido com parser + Edge): `docs/research/2026-10-13-05-ui-auditoria-aulas.md`
(6 famílias de classe: EN15 com `.nav`/`.stats` sem `<main>`, ER6 com `.rail` + `main`, RS13, RG7, dossiê, autópsia). Achados
L1-L15 (§14 de lá; medidos na camada ANTIGA, def2fdd) e o estado na camada v3:
- **L1** `.tw` cortada pelo `overflow:hidden` (até 424 px a 390): **resolvido** (hub v105; a tabela rola na caixa).
- **L3** espaçamento de caixa-alta nos rótulos: **resolvido** nos rótulos citados (`.eye .kick .dstage .rlab .albl th .tag .tk`, `h3/h5` de `.vs`).
- **L5** negrito ciano com exceções por descendente: **resolvido** (mesma especificidade das aulas).
- **L7** `h4.sub` e **L8** `.dtitle h3`: **resolvidos**.
- **L4** callouts sem critério único: **parcial** (trap = âmbar, banca = roxo, nota = neutro); faltam `.key`, `div.note`, `.disc`, `.fonte`, `.ext`, `.star`.
- **L6** h3/h4/h5 como rótulo dentro de `.vs .tgrp .blk .cmap .if3`: **pendente**.
- **L9** outliers de paleta (autópsia: 18 tokens próprios; neuromusculares: `--acc*`): **pendente** (mapeamento no §8.3 do inventário).
- **L2, L10-L15**: **pendentes** (ver o inventário).

## 10. Achados da varredura s225 (13/10/2026)

| # | Achado | Onde | Estado |
|---|---|---|---|
| A1 | Três paletas sobrepostas: tokens claros/escuros antigos (verde-água) no `player.html`, uma cópia no `painel.py` e o `tema.css` por cima | player, painel, tema | **resolvido**: paleta só no `tema.css`; player e painel só estrutura; o standalone embute o tema; teste trava cor literal |
| A2 | O `tema.css` misturava regras do hub, do painel, do player e das aulas, sobrescrevendo a regra-base por especificidade (duas definições por componente) | `tema.css` | **resolvido**: cada regra voltou ao arquivo da tela; o `tema.css` tem só tokens e base |
| A3 | Rosa servia de alerta e de identidade; `--alerta` servia erro e aviso | todas | **resolvido**: rosa = marca; erro = coral; aviso = âmbar; `--alerta` é apelido de `--erro` |
| A4 | Títulos, rótulos e cabeçalhos todos em ciano (v2.4) | hub, painel, aulas | **resolvido**: títulos em branco, hierarquia por tamanho e peso; ciano só na interação |
| A5 | Caixas preenchidas em série: tiles do fim, por bloco, revisão com faixa lateral, cadeia em caixas centralizadas, regra-mestre e armadilha como caixas dentro do card, números do Ritmo, fim do lote | hub, player, painel | **resolvido**: linhas com filete; métricas numa faixa; cadeia alinhada à esquerda e numerada |
| A6 | Estado só por cor: gabarito/errada, revisão certa/errada/chute, ritmo abaixo, lista recém-concluída | hub, painel | **resolvido**: `✓ ✗ ?` e "abaixo do necessário" por extenso |
| A7 | Trilho com todos os segmentos no mesmo brilho; "revisar depois" invisível nele; alvo de 14 px | Listas | **resolvido**: respondida, atual, marcada e vazia distintas; classe `flag` no JS; 26 px de toque |
| A8 | Controles em pílula (declaração, Questões/Simulados) com o formato reservado a badge | Listas | **resolvido**: raio de controle |
| A9 | Borda de campo e de botão a 1,6:1 (invisível) | hub, player | **resolvido**: `--linha-forte` (3,2 a 3,8:1) |
| A10 | Brilho no título da aula e gradiente nas barras de progresso | tema, painel, player | **resolvido**: barras sólidas; sem `text-shadow` |
| A11 | Vermelho literal `#b3261e` no erro do formulário de pergunta dentro dos documentos (ilegível no escuro) | `hub.html` (`pendEstilo`) | **resolvido**: `var(--erro, #b3261e)` |
| A12 | O kit de conferência visual (banco falso, montagem do site, capturas) existia só em `tmp/` (gitignorado) | `tmp/design`, `tmp/alca_s213` | **resolvido**: `tools/ui_capturas.py` + `core/templates/ui_harness.html` (11 cenas, rolagem horizontal medida; §8) |
| A13 | `.qz-lista button` (0,1,1) vencia `.qz-rev` (0,1,0) e espremia a revisão em 2 colunas | `hub.html` | **resolvido**: `.qz-lista .qz-rev` |
| A14 | Coluna de 58rem: ~110 caracteres por linha no desktop | `--wrap` | **resolvido**: 46rem |
| A15 | O "próximo passo" não existia como elemento no Painel | painel | **resolvido**: a 1ª tarefa da Semana leva "Próxima" e a ação como botão primário |
| A16 | Página de resumo publicada tem paleta própria (verde-água antigo) para quando abre fora do leitor | `hub.py` `CSS_RESUMO` | **pendente** (baixo impacto: no leitor o tema vem por cima; mudar republica 31 resumos) |
| A17 | Tema claro só por `data-theme="light"`; o hub ignora `prefers-color-scheme: light` de propósito | `tema.css` | **decisão dele** (s224: escuro por padrão); o claro foi refeito na mesma semântica |
| A18 | Aba que não carrega ("Não consegui ler as listas"): a assinatura de `listas` (e a do quadro da Teoria) é feita uma vez só e não tenta de novo depois de uma falha | `hub.html` `iniciarQuestoes` | **resolvido** (s226, part-1): `assinarResiliente` (1/2/4 s + Tentar de novo) e log no console com o código para medir o gatilho real |
| A19 | Cards: o Painel conta o saldo do dia (X de 150) e a aba Cards o lote no ar (3/100), que é de 10/10 (backend manual) | `painel.py`, `player.html`, `/hub-backend` | **pendente**: mesmo PRD (decisão dele: contador do dia + fila diária) |
| A20 | Semana do Painel: "resolver no hub"/"abrir aula" repetidos por linha, "da semana N" em cada atrasada, a Próxima com controle de outro tipo | `painel.py` | **pendente**: mesmo PRD (linha clicável, aviso uma vez) |
| A21 | Listas: chip "pronta" repetido em toda linha (informação nula) | `hub.html` `qzItem` | **resolvido** (s226, part-1): `qzChip` |
| A22 | Marca "MedHub" pequena no topo | `hub.html` `.hub-marca` | **resolvido** (s226, part-1): 1,375rem, "Hub" em rosa |
| A23 | Sem o espelho local `medhub.respostas.<lista>`, o 1º snapshot de `questoes` chega antes do de `respostas` e a Q1 aparece como nova mesmo respondida (lido no código pelo subagente, não medido) | `hub.html` | **pendente**: mesmo PRD (família do A18) |

## 11. Histórico de decisões

- **v1 (12/10/2026, s224)**: escuro índigo sobre preto, Atkinson, cartões viram linhas -- *"prefiro tema escuro / modo
  noite, pode ser assim por default"* (commit `1d71743`).
- **v2 Vice City (12/10)**: fundo Ocean Night `#0B0F2B`, acento ciano -- *"essa paleta me parece melhor"* (`95d4a38`).
- **v2.1-v2.3 (12/10)**: rosa crescente em ação, títulos, seleção e grifo.
- **v2.4 (12/10, noite)**: *"agora temos muito rosa; preferia a UI com mais ciano"*: ciano em tudo, rosa só alerta (`730d884`).
- **v3 retrowave contido (13/10, s225)**: o brief dele (paleta de referência `#17132E #211C3A #29233F #403858`, ciano
  `#00D9E8`, rosa `#FF4FA3`, roxo `#AA71E8`, amarelo `#FFD447`, verde `#79D6A5`, coral `#FF7C87`, âmbar `#FFBE72`) com
  semântica fixa por cor, hierarquia por tipo e menos caixas. Este arquivo nasce aqui.
- **Semana do Painel no padrão da Teoria (13/10, s226, P21)**: a linha inteira abre a lista no hub ("resolver no
  hub" saiu), a aula vira ação pequena fora do alvo, o atraso sobe para o subtítulo "Atrasadas · N" ("da semana N"
  saiu da linha) e a "Próxima" perde o botão cheio, fica só o rótulo. Travas: `test_painel.py::
  test_semana_linha_inteira_abre_a_lista`, `test_atrasadas_sob_subtitulo_unico`, `test_proxima_so_pelo_rotulo_sem_botao_cheio`.

- **Abas que se recuperam sozinhas (13/10, s226, part-1, A18/A21/A22)**: leitura de Listas, Teoria e lista aberta pela
  assinatura resiliente (1/2/4 s, depois "Tentar de novo"); o chip "pronta" saiu (em curso mostra respondidas/total);
  marca em 1,375rem. O banco falso do `ui_harness.html` ganhou `?leitura=1x|0` (falha de leitura de coleção).
- **A retentativa pede conexão nova (13/10, s226, sprint-final-uerj part-1)**: a v108 publicada com a página aberta
  deixou Listas em "Não consegui ler as listas" até ele sair do artifact e voltar -- as 3 tentativas reusavam o `db`
  morto. Da 2ª tentativa em diante a assinatura pede `claude.use("db")` de novo e a consulta recebe o `db` novo
  (`consulta(db)`); `QZ.db` acompanha. O harness ganhou `?leitura=conexao` (a 1ª conexão falha em toda leitura).

Ele muda de ideia rápido: trocar paleta é trocar os dois blocos de cor do `tema.css`; nada além disso deve ser preciso.
