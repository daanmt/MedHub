# Session 087 — Revisão FSRS profunda (46 cards) + cluster do shunt fechado + plano da semana
**Data:** 2026-06-22
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 086

---

## O que foi feito

**Sessão 100% de revisão FSRS conversacional (`/revisar`)** — abertura definida na s086 ("começar com flashcards"):
- **Fila vencida drenada: 30/30** (20 atrasados + 10 hoje) + **10 novos** estreados + **6 andaimes do shunt** ativados = **46 cards**.
- Os **6 "re-drill dos 1"** (426, 435, 84, 78, 70, 104) caíram na fila de atrasados e foram avaliados com nota honesta (não re-drill seco).
- Distribuição da fila (40): 15×nota4 · 10×nota3 · 2×nota2 · 13×nota1 (4 dos 1 são estreias a frio).

**Cluster Cardiopatias / shunt — FECHADO ao vivo:**
- Diagnóstico: o estudante crava T4F e HCE isoladas, mas **embaralha quando precisa contrastar** (errou #104, #110, #94, #96 — todos no eixo do shunt).
- **Achado de gestão:** os andaimes de mecanismo do shunt (443/444/445/474/475/476) tinham **state=0 (nunca revisados)** — venceram em 14-17/06 mas ficaram **presos atrás do limite de 10 novos/dia** (atrás dos novos de GO mais antigos). O método (s082/s084) estava feito, mas os cards nunca chegaram ao estudante.
- Ação: puxados e drillados os 6. O nó persistente = **colar "hipoplasia de VE" na T4F**. Re-ensino cirúrgico da fronteira **T4F (VE normal, HVD por estenose pulmonar) × HCE (VE hipoplásico, canal-dependente)**. **Confirmado fechado:** estudante recitou os 4 componentes corretos (CIV / EP / aorta cavalgante / HVD) + origem da HVD (estenose).

**Cluster Ectópica — mapeado** (material p/ aula-base de sex 26): o gap não é diagnóstico, é o **algoritmo certeza→conduta**. Escada: β-hCG<2000 sem imagem→observar; com imagem→curva 48h; curva anormal + cavidade vazia + imagem→tratar; saco IU + massa anexial→heterotópica/cirurgia. Estudante oscilou (tratou suspeita #116, travou no confirmado #118).

## Padrões de erro identificados (eixo de PROCESSO — o protagonista)

O conteúdo entra; **o que vaza é execução de prova.** Deslizes:
- **#140 — desprezou o discriminante escondido** ("corrimento avermelhado já cessado" = sangramento anormal = contraindicação à TH). Bug nº 1 puro.
- **#128 — leitura de titulação invertida** (leu VDRL 1/8→1/32 como QUEDA). Erro grave: inverte conduta. Regra: denominador maior = título maior.
- **#88 — interferência entre cards** (importou "aquecer" do #426 hipotermia para o choque hemorrágico). Efeito de revisão em bloco.
- **#116/#118 — timing da decisão** (fechamento precoce / trava). Mesmo motor do bug nº 1c.
- **#94 — inversão de mecanismo** (RVS/RVP trocados na HCE).

## Artefatos criados/modificados

- `ipub.db` (local) — 46 reviews FSRS gravados; verso do **#426 corrigido** (tríade letal: hipocalcemia→coagulopatia).
- `HANDOFF.md`, `ESTADO.md` — rotacionados; corrigido **drift de contadores** detectado no reconcile de boot (297 erros / 318 cards / 48 resumos).
- `history/session_087.md` (este) + `history/INDEX.md`.

## Decisões tomadas

- **Andaime vencido deve furar o new-limit da fila** (pendência de sistema / Tier-3): o radar prova que andaimes de mecanismo ficam presos atrás de novos antigos e nunca aparecem. A priorização da fila FSRS precisa elevar andaime vencido acima dos novos comuns.
- **Plano da semana (22-28/06):** ~100q/dia, foco triplo volume + execução de prova + atacar fracos (IC 54% / Hepato 57% / Dermato 67% / Hemato 72%) com aula-base "escada".

## Próximos passos

1. **Seg 22 — Cardiologia/IC** (fraco + frio): aula-base IC "escada" + refresh + **bloco ≥100q**.
2. **Curadoria pendente:** reestruturar **#104** (CIA — pedido do usuário), avaliar **#70** (sulfonilureia 1ª ger) e **#428** (HIT) — apontados como mal-formulados.
3. **Ritual anti-vazamento** em toda questão (PLAYBOOK_EXECUCAO_PROVA.md).
4. Grade completa da semana no `HANDOFF.md`.
