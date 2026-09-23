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
inclui na aba Aulas (`aulas/<slug>.html`, mais novas primeiro, cap de 120) e o agente
republica o hub na URL do HANDOFF (rito e assinatura em `/revisar` e `/engenharia-cli`). A aba
abre a aula DENTRO da página, sem sair do drill.  <!-- CHECK: test_hub -->

⚰️ *Até 22/09/2026 a regra era "publicar a aula-base como Artifact HTML direto" -- um artifact NOVO
por aula na galeria da conta compartilhada. Revogada na s192 (spec `medhub-hub-v0`): o operador
apagava por higiene e o link da aula morria no mesmo dia (a de Hérnias, em 22/09).*
