---
name: "source-command-aula-base"
description: "Contrato de RENDERIZAÇÃO da aula-base — toda aula-base entregue sai como Artifact HTML com design de verdade (skill frontend-design), não Markdown liso. Consultar antes de montar qualquer aula-base."
---

<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI.
     Edite `.claude/commands/aula-base.md` e rode `python tools/sync_skills.py`.
     Qualquer edicao feita neste arquivo e SOBRESCRITA no proximo sync. -->

# source-command-aula-base

Use this skill when the user asks to run the migrated source command `aula-base`.

## Command Template

# Skill: Aula-base (contrato de renderização)

> Portador versionado da regra de design da aula-base (migrada da memória de harness em
> `descolar part-7` / P3 — memória de harness é decorativa para qualquer IDE que não seja o
> Claude Code, então a regra load-bearing passa a viajar com o repo).
>
> **Escopo desta skill:** só a **forma** da entrega. O **gatilho** (quando a aula-base acontece)
> e a **profundidade** (cobertura como piso fixo) continuam em `AGENTE.md §1` — não duplicar aqui.

---

## 1. A regra (s149, decisão do usuário)

Toda aula-base entregue **renderiza como Artifact HTML com design de verdade** — tabelas,
listas, fluxogramas, o que ajudar a compreensão — em vez do Markdown liso. Carregar a skill
`frontend-design` antes de compor.

Palavras do usuário: *"vamos adotar este formato de renderizar a mesma via artifact, com
liberdade maior de design e composição espacial da aula... por ser em html temos mais liberdade
quanto ao /frontend-design."*

**Why (o que autoriza gastar design):** o conteúdo permanente já mora em `resumos/`; a aula é
peça de leitura de alta qualidade. ⚰️ *Até 22/09/2026 o argumento era "artifacts são efêmeros:
ele apaga os da aba do Claude web para não poluírem a conta do time de conteúdo médico". A
poluição era a CAUSA dos links mortos -- tratada na s192: a aula deixou de ser artifact avulso e
virou arquivo do MedHub HUB (seção 3).*

🔴 **Fronteira de SSOT:** o Artifact é **camada de apresentação**. O que precisa sobreviver à
aula (armadilhas, discriminações, condutas) vai para `resumos/` seguindo `/estilo-resumo` —
nunca fica só no artifact.  <!-- NAO-VERIFICAVEL: ato do agente na sessao; nada liga o artifact publicado ao resumo (revisar: 2027-03-31) -->

---

## 2. A régua de design (o que "design de verdade" significa aqui)

O modelo de referência é o artifact de autópsia de simulados, cujo HTML renderizado está
versionado em `artifacts/autopsia-simulados.html` — abrir e **ler o `<style>`** antes de
compor. O que copiar dele:

- **Tokens de cor** nomeados (papel / card / afundado / tinta em 3 pesos / 1 acento por
  função), com **dark mode espelhado** em `@media (prefers-color-scheme: dark)` **e**
  `:root[data-theme="dark"]` — as duas formas, não só a media query.
- **Tipografia com `clamp()`** (escala fluida), `tabular-nums` em qualquer número que alinhe
  em coluna.
- **Acessibilidade**: `prefers-reduced-motion` respeitado, foco visível, contraste real.
- **Separação forma × dados**: a estrutura de degraus/troncos/branches que já sai das
  aulas-base atuais em Markdown é o **dado**; o HTML é só a **forma** que a recebe.

> ⚰️ **Tombstone (s156/s160, F57/F50).** O motor determinístico que essa regra citava —
> `tools/autopsia_template.py` + `tools/autopsia_simulados.py` — **não existe mais**: o
> template foi deletado na s156 e o gerador (852 linhas, já quebrado sob um `.pyc` órfão) foi
> aposentado com lápide na `descolar part-2`. **Não recomendar nem tentar importar.** O que
> sobrou como referência é o HTML renderizado citado acima. Este tombstone é o caso-síntese
> que originou este arquivo: a regra apontava para um alvo que outro agente deletou sem ver a
> memória que dependia dele.

---

## 2b. O tema do hub (s224, pedido dele em 12/10/2026): a aula NÃO traz paleta nem fonte

Decisão dele: *"prefiro tema escuro / modo noite [...]"* (12/10/2026); desde 13/10/2026 (s227) vale o **tema v4, fosco em camadas** (o controle DualSense GTA VI que ele trouxe: preto fosco, cromado azul -> violeta, rosa nos detalhes, branco quente), sobre o princípio do v3: *"a interface deve lembrar Vice City à primeira vista, mas desaparecer em segundo plano quando o estudante estiver concentrado no conteúdo"*. Quem aplica é o **leitor do hub**: injeta `core/templates/tema.css` + `core/templates/tema-aula.css` depois do CSS da aula (e remove o `<link>` de Google Fonts dela) e mostra a aula numa **placa** (`#15151E` sobre o fundo `#0C0C12`). Uma fonte só (Atkinson Hyperlegible Next), texto `#F6EFEA`; dentro da aula, `--card` é a superfície ELEVADA (as caixas nunca têm a cor da placa). A semântica das cores é fixa e mora em [`DESIGN.md`](../../DESIGN.md) (Colors): ciano = link, navegação, progresso, ação, e o termo-chave em negrito (ciano claro, o único texto ciano da leitura); âmbar = armadilha e aviso; coral = erro e o que é proibido; roxo = numeral do degrau, marcos e "como a banca cobra"; rosa = só a marca do hub. Títulos em branco, rótulos e fontes em lavanda; neon nunca no corpo do texto.  <!-- NAO-VERIFICAVEL: paleta e escolha de design dele; nenhum gate le as cores do hub nem o uso de neon so como acento (revisar: 2027-03-31) -->
⚰️ *13/10/2026 (s227): era "desde 13/10/2026 (s225) vale o **tema v3, retrowave contido** [...] fundo `#17132E`, texto `#F8F5F2`". Motivo: a queixa dele ("chapado no fundo, sem blocos") levou ao v4 (`.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md`); a semântica das cores não mudou.*
⚰️ *13/10/2026 (s225): substituída pela v3 acima. Era: "a **Vice City** (`#0B0F2B` Ocean Night, `#00F0FF` ciano, `#FF5CA8` rosa, `#BC6CFF` roxo, `#FFB86B` pêssego) [...] fundo `#0B0F2B`, texto `#F4F1FF`; os neons só como acento (ciano = link/aba/progresso; rosa = alerta/armadilha; roxo = numeral e ícones; pêssego = "como a banca pede")". Motivo: o brief dele de 13/10 fixou rosa = marca e aviso = âmbar, e a armadilha passou a ter a mesma cor no card e na aula (`docs/UI.md` §10, achado A3).*

Para a aula nova isso muda a régua da seção 2:
- **Use os nomes de token do tema**, que as aulas já usam: `--paper --card --sunk --ink --ink2 --ink3 --line --line2 --teal* (acento) --amber* (aviso: armadilha) --plum* (roxo: banca, marcos) --carmine* (erro: o que é proibido) --on`. Os valores o tema sobrescreve; não invente cor fora dessa lista.  <!-- NAO-VERIFICAVEL: autoria do CSS proprio de cada aula; nenhum gate le as cores declaradas nas aulas (revisar: 2027-03-31) -->
- **Sem `@import`/`<link>` de fonte, sem `font-family` próprio**: o tema impõe a família única (`*{font-family:var(--fonte)!important}`).
- **Sem caixa-alta** (`text-transform`): o tema a desliga; eyebrow é texto comum.
- **Estrutura**: linhas com filete e blocos de realce, não cartões empilhados com borda e sombra; os raios do tema (`--raio` 10 px em quadro e controle, pílula só em badge); o numeral do degrau grande e leve é a única decoração; callout = filete + lavagem, pela cor do significado.
⚰️ *13/10/2026 (s225): era "um raio só (12 px)" -- o v3 padronizou os raios em tokens (`docs/UI.md` §3).*
- Dark/light continuam espelhados (`@media` **e** `[data-theme]`); o padrão agora é o **escuro**.
- Fonte única do CSS: `core/templates/tema.css` (só tokens e base de TODO o MedHub) e `tema-aula.css` (a camada de leitura de aulas e resumos). Mudou o visual do MedHub = edite lá, não em cada aula; mapa completo em `DESIGN.md` (Telas e processo). Teste visual: hub em pasta de rascunho + banco falso + Edge headless a 390, 768 e 1280 px (`python tools/ui_capturas.py`), como em `DESIGN.md` (Como conferir).
⚰️ *13/10/2026 (s225): era "`core/templates/tema.css` (shell, painel, listas, cards)" e a receita de captura só na memória -- as regras de componente saíram do `tema.css` (achado A2) e a receita passou a morar no `docs/UI.md` §8.*

---

## 3. Motor reusável: candidato, não obrigação

A ambição declarada na s149 era convergir para um **motor reusável** (um template HTML puro +
um gerador que recebe a estrutura da aula e emite a página), no lugar de redesenhar do zero a
cada sessão. Isso **continua sendo a direção**, mas é trabalho de engenharia de front-end de
verdade — **frente aberta, não passo de fim de sessão**.

**Até esse motor existir:** compor a aula-base à mão, seguindo a régua da seção 2. Quando uma
**segunda** aula-base pedir o mesmo tratamento, esse é o gatilho para construir o motor em vez de
repetir o desenho.

## 4. Onde a aula é publicada: no MedHub HUB, nunca como artifact avulso (s192)

A aula é gravada em `artifacts/aula-<slug>.html` -- o HTML da página, sem
`<!DOCTYPE>`/`<html>`/`<head>`/`<body>` próprios (o publish embrulha), com `<title>` legível: é
o nome que aparece na lista. Ela sobe como **arquivo do MedHub HUB**: `tools/hub.py --build` a
inclui na aba Teoria (`aulas/<slug>.html`, mais novas primeiro, cap de 200; concluída, fica na
Biblioteca da Teoria -- nada vai para `artifacts/arquivo/`, s216) e o agente
republica o hub na URL do HANDOFF (rito e assinatura em `/revisar` e `/engenharia-cli`). A aba
abre a aula DENTRO da página, sem sair do drill.  <!-- CHECK: test_hub -->

⚰️ *Até 22/09/2026 a regra era "publicar a aula-base como Artifact HTML direto" -- um artifact NOVO
por aula na galeria da conta compartilhada. Revogada na s192 (spec `medhub-hub-v0`): o operador
apagava por higiene e o link da aula morria no mesmo dia (a de Hérnias, em 22/09).*

## 5. A forma do texto: tópicos, períodos curtos, profundidade sem volume (s195)

Decisão do operador em 24/09/2026, depois de ler as aulas no celular: *"As aulas ainda estão muito
longas. 'A escada inteira numa respirada' em prosa é ruim, melhor seria em tópicos... Evite parágrafos
longos, preferindo períodos menores e mais concisos. D10 significa aprofundada, não necessariamente longa
e laboriosa. Precisamos valorizar cada segundo de estudos."*

- **Cada degrau = lede de 1 frase + tópicos (`<ul>`)**, não parágrafos. Um tópico = uma ideia, 1-2
  períodos curtos. O mecanismo (o porquê) entra como tópico próprio quando discrimina alternativa.
- **Cluster de diagnóstico diferencial = tabela/grade** (`.crit`, `.vs`), nunca prosa.  <!-- NAO-VERIFICAVEL: forma do conteudo da aula (grade x prosa) e julgamento de autoria; nenhum gate le o HTML da aula por cluster (revisar: 2027-03-31) -->
- **A síntese final é a grade de gatilhos** (1 linha por degrau), não um parágrafo corrido. A "escada
  inteira numa respirada" em prosa foi revogada.
- **Armadilhas: 1-2 períodos cada.** Referência densa (listas oficiais de 10/12 passos, suplementações)
  vai para `<details>` recolhido.
- **Cada fato uma vez.** Se a grade já traz o número, o tópico não o repete.
- **D10 = profundidade** (mecanismo, discriminador, banca-dependente), **não comprimento**. Régua:
  cada seção cabe numa tela de celular. Referência: `artifacts/aula-topicos-pediatria.html` (reescrita
  na s195: corpo de 6.200 para 4.200 palavras, 12 parágrafos de prosa para 0, mesmo conteúdo).

⚰️ *A memória `feedback_aula_base_prosa_enxuta` (s150: "prosa enxuta, não bullet-pilha") fica
restringida: prosa só no lede; o corpo é em tópicos. "Descomprimir" (s090/s092) significa explicar o
mecanismo, nunca escrever mais texto.*  <!-- NAO-VERIFICAVEL: 'descomprimir = mecanismo, nao comprimento' e julgamento de autoria; nao ha gate de comprimento de aula (revisar: 2027-03-31) -->

## 6. Referências no fim, como num artigo (s227)

Pedido dele em 13/10/2026: *"remover todos os 'Fonte:...' espalhados pelo texto, e concentrá-los ao final, tal como um
artigo. Preferir referências de guidelines/pcdt/ms/sociedades, tanto para os resumos quanto para as aulas."* Vale para
aula-base, Revisão Direcionada, dossiê e autópsia.

- **Nenhuma linha "Fonte:" no meio do texto** (nem em `p.src`, nem na legenda de figura). No lugar, um número
  sobrescrito discreto: `<sup class="ref"><a href="#ref-N">N</a></sup>`, no fim da frase ou da legenda que ele sustenta.
- **O documento termina em `<section class="refs" id="refs"><h2>Referências</h2><ol>`**, um `<li id="ref-N">` por
  fonte, na ordem de aparição, sem repetir a mesma fonte. Cada item: sociedade ou órgão, título curto, ano (e PMID/DOI
  quando houver), no formato do `evidence-governance` §7.
- **Ordem de preferência = a hierarquia do `core/contracts/evidence-governance.md` §2:** (1) diretrizes de sociedades
  brasileiras e Ministério da Saúde (PCDT, Cadernos de Atenção Básica, manuais, calendário PNI); (2) guidelines
  internacionais e revisões sistemáticas; (3) livro-texto. A aula cita a diretriz que sustenta o fato, não o caminho por
  onde o agente chegou a ele. Fato que só tem apoio de material de curso (a apostila do EMED) ou da banca é declarado
  assim, nunca vestido de diretriz; nada de diretriz citada de memória (§7 "nada de memória").  <!-- NAO-VERIFICAVEL: escolha da fonte que sustenta o fato e julgamento de autoria; nenhum gate le a hierarquia das referencias da aula (revisar: 2027-03-31) -->
- **A base interna NÃO é referência e NÃO aparece na aula (s236, 30/10, decisão dele: *"Não podemos referenciar
  resumos, apenas artigos, guidelines, consensos, etc."*):** o resumo do MedHub, o verso de um card e o PDF/apostila do
  curso são ponto de partida para achar a fonte, nunca entrada em Referências nem linha final. O registro da RD  <!-- CHECK: test_referencias_tiram_a_fonte_do_meio_e_montam_a_lista_no_fim -->
  (`"resumos"` no `quadro_entry`/`hub_quadro.json`, `/revisar` 8a) é o único lugar onde os resumos consultados ficam.
  ⚰️ *s227-s235: `<p class="base">Base deste documento: ...</p>` depois da lista; o leitor do hub hoje esconde esse `p.base`
  e descarta a base interna que acha no texto.*  <!-- CHECK: test_referencias_tiram_a_fonte_do_meio_e_montam_a_lista_no_fim -->
- **Figura (`figure.fig-an`, /anima) -- s236, pedido dele:** uma figura em TODA seção que tenha mecanismo, fluxo de
  decisão ou diferencial espacial (metade ou mais das seções; nunca só a 1ª). A imagem domina: rótulos de 1-3 palavras  <!-- NAO-VERIFICAVEL: forma da figura e autoria da aula; nenhum gate le o SVG (revisar: 2027-03-31) -->
  dentro do SVG; sem legenda de cores em frase; sem repetir o parágrafo; `figcaption` de uma linha curta + o número da
  referência, ou nenhuma; sem "Fonte:" na legenda. O rosa (`--rosa`) realça o elemento que decide (corte, achado que
  exclui, seta decisória) e, no texto, `strong.chave`/`span.chave` com `color:var(--rosa)` no dado que decide (1-3 por
  seção). Âmbar = armadilha; roxo = dado; ciano = interação. Regras no `DESIGN.md` (Named Rules e Leitor de aulas).  <!-- NAO-VERIFICAVEL: dose e forma das figuras sao autoria da aula; nenhum gate conta figuras por secao (revisar: 2027-03-31) -->
- **Desde 13/10/2026 o leitor do hub já faz isso nas aulas antigas** (`hub-tema-v4-part-7`): tira toda "Fonte:" do
  meio e monta as Referências no fim. Isso é a camada de apresentação; a aula NOVA nasce no formato desta seção, e as
  antigas migram na fonte junto com a reforma de estética com a /anima (decisão dele: "isso será evoluído depois").  <!-- NAO-VERIFICAVEL: autoria do HTML da aula nova; o leitor normaliza a apresentacao das antigas e nenhum gate le a ordem de preferencia das fontes (revisar: 2027-03-31) -->
