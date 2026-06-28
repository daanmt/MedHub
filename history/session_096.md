# Session 096 — Implementação do PRD de Revisão Calibrada (4 partes) + sessão FSRS (32 cards) + resumo de ectópica

**Data:** 2026-06-28
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 095

---

## O que foi feito

### 1. PRD de Revisão Calibrada — IMPLEMENTADO (frente A, desbloqueada na s095)
Via `/gen-spec` (vibeflow), o PRD `docs/plans/s094-revisao-calibrada-PRD.md` foi fatiado em **4 specs** (`.vibeflow/specs/revisao-calibrada-part-{1..4}.md`) e implementado integralmente. **63 checks automatizados, 0 falhas** (`tools/test_revisao_calibrada.py`). Cobre os 10 DoD do PRD.

- **Parte 1 — Fundação de dados (DoD-1,2):** migração `tools/migrate_dificuldade.py` (3 colunas `dificuldade`/`dificuldade_fonte`/`dificuldade_at` em `taxonomia_cronograma`, idempotente); `db.set_dificuldade()`/`get_dificuldade()` (única exceção autorizada à regra "só insert_questao escreve taxonomia" — toca só as 3 colunas); fix do pré-req **`_find_resumo`** (`get_topic_context._build_index` agora indexa `path.stem.lower()`, não só frontmatter); seed `tools/seed_dificuldade.py` com as 8 notas §4.7 (4 temas criados com volume-0 por serem canônicos da S11).
- **Parte 2 — Inferência (DoD-5,6):** `infer_nota()` determinístico + `day_plan.py --difficulty "<area>" "<tema>"` (read-only); eixo 2 via `review_radar.coletar()`; divergência auto-nota×performance; mapa nota→degrau (D10/D8/D5/D2). **Bug de design corrigido:** `score_dorm` ausente era tratado como "quente" (−1) → agora `None`=eixo neutro.
- **Parte 3 — Barreiras A/B (DoD-8,9):** `dormant_refresh.py --kind {dormant_refresh,directed_review}`; testes com db temporário isolado provando Invariante A (PREPARAR não toca FSRS) e B (PREPARAR sempre carimba `review_log`) + gate estático.
- **Parte 4 — Normativo (DoD-3,4,7,10):** `core/contracts/revisao-calibrada-contract.md` (pending-ratification); `/revisar` fundido (sub-modos PREPARAR/DRENAR + Invariantes); `/refrescar` deprecado (stub→PREPARAR); `AGENTE.md` §1.2 (removido "Calibração pendente"), §6 (nova decisão), §7.3 (tabela skills).

### 2. Sessão FSRS — 32 cards tratados (de 50 puxados)
Distribuição: **16×nota4 · 6×nota3 · 5×nota2 · 4×nota1 · 1 aposentado** (#104 CIA, a pedido, via `needs_qualitative=2`). 22 sólidos / 9 frágeis. Os 31 vencidos originais drenados → restaram 6 re-aprendizados (os errados). 18 novos NÃO feitos (decisão: estreia densa de Indicadores fica p/ bloco com refresh). **Furo corrigido:** o Bloco 2 (Cardiopatias conduta #100/#108) foi narrado mas o `--record` foi esquecido; detectado via `due_check` (last_review pré-sessão) e gravado depois.

### 3. Resumo gold de ectópica criado
`resumos/GO/Gravidez ectópica.md` (não existia — era leech sem fonte). Cobre limiar discriminatório → curva → tratar; MTX (β-hCG=preditor, tamanho=elegibilidade); salpingectomia×salpingostomia. Validado: conforme `/estilo-resumo` + `_find_resumo` (Parte 1) já o resolve.

## Padrões de erro identificados (sessão FSRS)
- **Inversão de direção (#130 sífilis):** transmissão vertical é INVERSA à idade da infecção (recente=alta 70-100%; terciária=baixa 10-30%) — ele disse "alto". Mesmo padrão de TSH/VDRL/FSH (ver `feedback_inversao_direcao_marcador`).
- **Não fechar o elo causal (#69 hipoglicemia SU):** tinha o mecanismo ("metformina=sensibilidade, não secretagogo") mas concluiu errado (que potencializa). Metformina NÃO potencializa; o que potencializa = deslocamento proteico (warfarina/AAS/fenilbutazona — #70).
- **Fronteira fina (#95 HCE×TGA):** choque cardiogênico + hiperfluxo + sobrecarga D no RN dos primeiros dias = HCE (não TGA). Leech histórico do cluster shunt.
- **Lacuna de conteúdo real (ectópica):** cluster inteiro frio — resolvido criando o resumo (não era execução).
- **Ponto alto:** Trauma (7/7 sólidos: controle da fonte, MNO hepático, hiperventilação, PECARN). Nenhum bug nº1 clássico hoje.

## Artefatos criados/modificados
- **Código:** `app/utils/db.py` (helpers), `app/engine/get_topic_context.py` (_find_resumo), `tools/day_plan.py` (infer_nota+--difficulty), `tools/dormant_refresh.py` (--kind).
- **CLIs novos:** `tools/migrate_dificuldade.py`, `tools/seed_dificuldade.py`, `tools/test_revisao_calibrada.py`.
- **Specs:** `.vibeflow/specs/revisao-calibrada-part-{1,2,3,4}.md`.
- **Contrato:** `core/contracts/revisao-calibrada-contract.md` (novo).
- **Skills:** `.claude/commands/revisar.md` (fundido), `.claude/commands/refrescar.md` (deprecado).
- **Resumo:** `resumos/GO/Gravidez ectópica.md` (novo, gold).
- **Docs:** `AGENTE.md` (§1.2/§6/§7.3), `HANDOFF.md`, `ESTADO.md`, `history/INDEX.md`.
- **DB (local-only):** 3 colunas + 8 notas seed + 4 linhas de tema novas; 31 ratings FSRS; #104 aposentado.

## Decisões tomadas
- **Política de cards diária (usuário):** teto **30 cards/dia** = agendados + backlog; **15 backlog** inicial; reavaliar ao estourar (memória `feedback_politica_cards_diaria`).
- **Modelo FSRS auditado:** agendados (`state>0`, têm `due`, determinístico) × novos (`state=0`, pilha sem data, entram só por `--new-limit`). 290 novos na pilha em 28/06.
- **#104 aposentado** (soft-retire reversível) a pedido, em vez de DELETE hard.
- **Contrato fica `pending-ratification`** até validação em uso (1ª abertura de task calibrada).

## Próximos passos
- **Estudo (S11):** Medicina de Família e Comunidade, Doenças Exantemáticas (Rev), Cirurgia Infantil Pt 3 (Rev), Vulvovaginites, Imunizações, Sepse, Síndromes Hipertensivas. ≥100q/dia (meta jun: faltam 388 em 3 dias).
- **Cards:** aplicar a política (30/dia, 15 backlog priorizado pela S11, sempre PREPARAR antes). 6 re-aprendizados voltam amanhã (ectópica ×3, #70, #130, #95) + 8 agendados.
- **Revisão Calibrada:** ratificar o contrato após o 1º uso real; integrar `--difficulty` no fluxo de abertura de task do boot.
- **Pendências herdadas:** reescrever `TCE.md`; limpeza `[bulk]`/`Geral` da taxonomia; sessão dedicada de Cirurgia; integrar `/schedule`.
