# Session 124 — Drenagem FSRS + pivô do padrão de flashcards + Corpus EMED (vibeflow Parts 1-3)

**Data:** 2026-07-17
**Ferramenta:** Claude Code (Opus 4.8 [1M])
**Continuidade:** Sessão 123 (drenagem FSRS backlog antigo)

---

## O que foi feito

### 1. Drenagem FSRS conversacional -- 30 cards / 5 blocos de 6
- Composição a dedo: dívida de hoje (13 vencidos) + **os 15 frescos M4** que a s123 não introduziu (826-827 Imunizações, 757-761/828-830 Pré-Natal, 831-835 Endometriose) + 2 de M2-GO (Hipertensivas). Os frescos não afloravam na fila por *due* -- injetados à mão.
- Distribuição: **14x nota-4 · 5x3 · 6x2 · 5x1 = 19/30 sólidos (63%)**. Os 15 frescos M4 TODOS introduzidos (pendência M4 zerada). **2 aposentados** (286 cloaca/hidrocolpos, 288 HDC/LHR -- baixo rendimento, a pedido).
- 🏆 **Os 4 padrões-armadilha "vivos" do HANDOFF -- TODOS resistidos, 0 reincidência** (contraste: s123 bug nº1 reincidiu 3x): bug nº1 (282 refluxo, 829 AU×USG), número-vs-faixa (828 Doppler, 830 Atalah), sobre-investigar (834 empírico, 761 hiperêmese), inversão de direção (833 aromatase). A execução de prova está no ponto; os erros de hoje foram **conteúdo** (Pré-Natal factual frio, FA/DRC, sítios de endometriose).

### 2. Pivô do padrão de autoria de flashcards (pedido do usuário)
- Usuário **reprovou a safra auto-cunhada**: viola o *minimum information principle* (paragraph cards: contexto+pergunta+resposta+regra+armadilha empacotados). Forneceu as **20 regras de Wozniak** + os **flashcards de referência do EMED** + mandato de websearch.
- Decodifiquei o deck EMED de Endometriose (25 cards): **atômico** (frente gerativa curta, resposta 1 frase, zero armadilha embutida; a pegadinha emerge da cobertura do deck + discriminação por adjacência).

### 3. Corpus EMED como fonte de cunhagem -- pipeline vibeflow (discover -> gen-spec -> implement -> audit, 3 partes, **3 audits PASS**)
- **Part 1 -- Colheita + extração** (`tools/emed_flashcards.py`): colheu **275 `Flashc.pdf`** de `D:\Med\Estrategia 2024 Extensivo` -> `resumos/<area>/Flashcards - <Tema>.pdf` + sidecar `.cards.json` estruturado (**7565 cards**), gitignored. CLI `--query` (exato/fuzzy token-containment/candidatos). QA via **/workflows (35 agentes)**.
- **Part 2 -- Padrão atômico** (`/estilo-flashcard`): seção "Formato atômico (referência EMED)" com 7 regras; regra/armadilha reenquadradas (saem da carga de recall); reconciliação (targeting metacognitivo mantido, formulação trocada).
- **Part 3 -- Cunhagem religada** (`analisar-questao §8.3`): passo consulta-EMED + **seleção por contexto** (nunca deck inteiro) + fallback; workflows referenciam. **Demo:** Endometriose 831-835 reforjados pelo fluxo -> 7 atômicos, FSRS preservado 5/5, + splits 836/837.

## Padrões de erro identificados (bloco FSRS)
- **Todos os 4 padrões vivos resistidos** (ver acima) -- virada de execução de prova.
- Lacunas de **conteúdo** (não execução): Pré-Natal factual (DTN esporádico, Atalah exato, hipertermia teratogênica, ferro×folato), FA/DRC (DRC estável não contraindica), sítios de endometriose (#1 = ovários), ABC Score / LHR (fato seco).
- Card 760 (ferro no 1º tri) marcado pro **gate de evidência** (nuance banca-dependente, atrita com MS).

## Artefatos criados/modificados
- **Novos:** `tools/emed_flashcards.py`; `.vibeflow/prds/emed-flashcard-corpus.md`; `.vibeflow/specs/emed-flashcard-corpus-part-{1,2,3}.md`; `.vibeflow/audits/emed-flashcard-corpus-part-{1,2,3}-audit.md`; `history/session_124.md`.
- **Modificados:** `.gitignore` (+`*.cards.json`, report); `.claude/commands/estilo-flashcard.md` + espelho; `.claude/commands/analisar-questao.md` + espelho; `.agents/workflows/analisar-questoes.md`; `.agents/workflows/gerar-reforco.md`; `HANDOFF.md`; `ESTADO.md`; `history/INDEX.md`.
- **DB (local, não commitado):** 831-835 reforjados v2 + 836/837 novos; 30 cards FSRS registrados; 286/288 aposentados; 826-835/757-761 introduzidos.
- **Disco (gitignored):** 275 decks EMED + 275 sidecars + `artifacts/emed_harvest_report.json`.

## Decisões tomadas
- **Padrão de autoria pivota:** mantém o *targeting metacognitivo* (card nasce do erro), troca a *formulação* (formato atômico EMED). Um elo quebrado -> N cards atômicos; o "porquê" sai do recall (parêntese/card discriminador).
- **Corpus EMED = biblioteca de referência + fonte de cobertura**, puxado por **seleção por contexto** (erro/tema fraco/lacuna); **NUNCA import em massa** (~6.000 cards detonariam a estratégia "matar os cards" + teto 30/dia).
- **Valor do /workflows provado:** o QA de 35 agentes pegou 3 bugs sistêmicos que o scan determinístico não via -- derivação de tema (19 decks clobbered) + ruído de tag/watermark em TODO card. Corrigidos + re-verificados sobre os 7565 cards.
- Engenharia (não estudo puro) -> reflection de fechamento roda.

## Próximos passos
- **Reforjar 350/398/757/759** pelo novo fluxo EMED-fed (o 833/832/etc já feito na demo); **760 no gate de evidência**.
- **Bloco principal S13 ainda pendente:** Colecistite e Colangite (Drenagem Biliar), question-first, aula ancorada no PDF EMED. Alternativa: Imunizações - Revisão (D10 onboarding).
- **Drive `--sync-drive` continua stale** (pulado nesta sessão -- foco estudo/engenharia); rodar no próximo boot.
- Ratificar o padrão atômico após 1º uso real de cunhagem por erro.
