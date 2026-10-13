# Spec: painel-dashboard-sprint -- part 2: uma figura (anima) em cada RD da UERJ 2022 -- TESTE

> PRD: `.vibeflow/prds/painel-dashboard-sprint.md` (Solution 3). Gerada em 13/10/2026 (s226).
> ✅ **Desbloqueada em 13/10 (s226):** ele autorizou (*"pode instalar a skill no medhub"*); instalada no PROJETO em
> `.claude/skills/anima` (`npx skills add Garinmckayl/anima -a claude-code -y`; scanner: Gen Safe, Socket 1 alerta, Snyk Low).
> Varredura do principal: o kit é JS puro gerando SVG; só `scripts/capture.mjs`/`drive.mjs` abrem Chrome headless e falam com
> `127.0.0.1` (DevTools) -- sem rede externa achada. Pasta no `.gitignore` (13 MB de demos); versionado só o `skills-lock.json`.
> Antes de usar, ler o `SKILL.md` instalado inteiro (DoD 1).

## Objetivo

Testar se uma figura de mecanismo melhora a RD: uma por RD da UERJ 2022, no ponto da escada em que a prosa falha.

## Definition of Done

1. Skill instalada e o `SKILL.md` lido; o que ela roda (Node, rede, escrita) declarado no log da sessão antes do 1º uso.
2. Uma figura por RD, no máximo, embutida na própria `artifacts/aula-rd-<area>-1310.html` (SVG/HTML inline, sem CDN,
   sem arquivo externo), com `Fonte:` = a mesma fonte da seção; candidatas: CM PTHrP/osso blástico x lítico; CIR febre
   pós-operatória por dia; GO EGB (cortes 37 sem, 18 h, 38 graus); PED cateter umbilical -> trombose portal -> varizes;
   MFC sensível x específico. RD em que a figura não ajuda fica sem, declarado.
3. Nenhuma afirmação clínica nova na figura além do que a RD já diz (conferir texto da figura contra a seção).
4. Cores só pelos tokens do tema (a figura herda `tema.css` no leitor); legível a 390 px e no tema claro.
5. Conferido no leitor: hub de rascunho + `ui_capturas.py` (cena do leitor com a RD) a 390/768; suíte verde.

## Escopo

`artifacts/aula-rd-{cm,cir,go,ped,mfc}-1310.html`; `docs/UI.md` (nota no §9 leitor) se a figura pedir regra nova.

## Anti-escopo

Aulas-base, resumos, outras RDs (próximas sessões, decisão dele); WebGL/3D da skill; publicar o hub (é do principal).

## Riscos

- A skill gera página standalone com tema próprio -> extrair só o SVG e trocar cores por tokens.
- Figura pesada demais para o celular -> teto de ~60 KB por figura.
