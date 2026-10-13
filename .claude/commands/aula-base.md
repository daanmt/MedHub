---
description: "Contrato de RENDERIZAÇÃO da aula-base — toda aula-base entregue sai como Artifact HTML com design de verdade (skill frontend-design), não Markdown liso. Consultar antes de montar qualquer aula-base."
type: skill
layer: commands
status: canonical
---

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

Decisão dele: *"prefiro tema escuro / modo noite [...]"* (12/10/2026); desde 13/10/2026 (s225) vale o **tema v3, retrowave contido**, do brief dele: *"a interface deve lembrar Vice City à primeira vista, mas desaparecer em segundo plano quando o estudante estiver concentrado no conteúdo"*. Quem aplica é o **leitor do hub**: injeta `core/templates/tema.css` + `core/templates/tema-aula.css` depois do CSS da aula (e remove o `<link>` de Google Fonts dela). Uma fonte só (Atkinson Hyperlegible Next), fundo `#17132E`, texto `#F8F5F2`. A semântica das cores é fixa e mora em [`docs/UI.md`](../../docs/UI.md) §4: ciano = link, navegação, progresso, ação, e o termo-chave em negrito (ciano claro, o único texto ciano da leitura); âmbar = armadilha e aviso; coral = erro e o que é proibido; roxo = numeral do degrau, marcos e "como a banca cobra"; rosa = só a marca do hub. Títulos em branco, rótulos e fontes em lavanda; neon nunca no corpo do texto.  <!-- NAO-VERIFICAVEL: paleta e escolha de design dele; nenhum gate le as cores do hub nem o uso de neon so como acento (revisar: 2027-03-31) -->
⚰️ *13/10/2026 (s225): substituída pela v3 acima. Era: "a **Vice City** (`#0B0F2B` Ocean Night, `#00F0FF` ciano, `#FF5CA8` rosa, `#BC6CFF` roxo, `#FFB86B` pêssego) [...] fundo `#0B0F2B`, texto `#F4F1FF`; os neons só como acento (ciano = link/aba/progresso; rosa = alerta/armadilha; roxo = numeral e ícones; pêssego = "como a banca pede")". Motivo: o brief dele de 13/10 fixou rosa = marca e aviso = âmbar, e a armadilha passou a ter a mesma cor no card e na aula (`docs/UI.md` §10, achado A3).*

Para a aula nova isso muda a régua da seção 2:
- **Use os nomes de token do tema**, que as aulas já usam: `--paper --card --sunk --ink --ink2 --ink3 --line --line2 --teal* (acento) --amber* (aviso: armadilha) --plum* (roxo: banca, marcos) --carmine* (erro: o que é proibido) --on`. Os valores o tema sobrescreve; não invente cor fora dessa lista.  <!-- NAO-VERIFICAVEL: autoria do CSS proprio de cada aula; nenhum gate le as cores declaradas nas aulas (revisar: 2027-03-31) -->
- **Sem `@import`/`<link>` de fonte, sem `font-family` próprio**: o tema impõe a família única (`*{font-family:var(--fonte)!important}`).
- **Sem caixa-alta** (`text-transform`): o tema a desliga; eyebrow é texto comum.
- **Estrutura**: linhas com filete e blocos de realce, não cartões empilhados com borda e sombra; os raios do tema (`--raio` 10 px em quadro e controle, pílula só em badge); o numeral do degrau grande e leve é a única decoração; callout = filete + lavagem, pela cor do significado.
⚰️ *13/10/2026 (s225): era "um raio só (12 px)" -- o v3 padronizou os raios em tokens (`docs/UI.md` §3).*
- Dark/light continuam espelhados (`@media` **e** `[data-theme]`); o padrão agora é o **escuro**.
- Fonte única do CSS: `core/templates/tema.css` (só tokens e base de TODO o MedHub) e `tema-aula.css` (a camada de leitura de aulas e resumos). Mudou o visual do MedHub = edite lá, não em cada aula; mapa completo em `docs/UI.md` §2. Teste visual: hub em pasta de rascunho + banco falso + Edge headless a 390, 768 e 1280 px, como em `docs/UI.md` §8.
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
