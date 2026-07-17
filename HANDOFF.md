# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-17 -- **s124: DRENAGEM FSRS (30 cards, 63% sólido, 15 frescos M4 introduzidos, 4 padrões-armadilha vivos TODOS resistidos) + PIVÔ do padrão de flashcards + CORPUS EMED (vibeflow Parts 1-3, 3 audits PASS). 275 decks EMED colhidos + padrão atômico + cunhagem religada por seleção-de-contexto. QA /workflows (35 agentes) pegou 3 bugs sistêmicos, corrigidos.***

## > Proximo passo imediato

**18.07 -- Fechar a reforja de flashcards + bloco principal S13:**
1. 🃏 **Reforjar 350/398/757/759** pelo novo fluxo EMED-fed (consulta `emed_flashcards.py --query` -> seleção por contexto -> atômico). 833/832/835/831/834 já feitos na demo da s124. **760 -> gate de evidência** (ferro 1o tri, banca-dependente).
2. 🎯 **Bloco principal (questão-first): Colecistite e Colangite (Drenagem Biliar)** -- próximo S13 E fraqueza histórica nº1 (TG18, colecistostomia x CPRE). Aula ancorada no PDF EMED -> ~100q -> cards dos erros (agora consultando o deck EMED). *Alternativa: Imunizações - Revisão (D10 onboarding).*
3. 🧭 Rodar `python tools/cronograma.py --sync-drive <xlsx>` no boot (Drive stale, pulado na s124).
4. 📊 **Volume:** ~84q/dia.

**Capacidade nova (s124):** `emed_flashcards.py --query --tema "<tema>"` retorna os pares atômicos do deck EMED do tema (275 decks em `resumos/**/Flashcards - *.pdf`, gitignored). Cunhagem consulta e puxa **só o que casa o elo** -- ver `analisar-questao §8.3` + `estilo-flashcard §Formato atômico`.

## Padroes de erro vivos -- atencao do scrum master
- 🟢 **VIRADA (s124): os 4 padrões vivos resistidos, 0 reincidência** -- bug nº1 (829 AU×USG), número-vs-faixa (828 Doppler, 830 Atalah), sobre-investigar (834 empírico, 761 hiperêmese), inversão (833 aromatase). A execução de prova está no ponto.
- 🔴 **Gargalo migrou pra CONTEÚDO:** Pré-Natal factual frio (DTN esporádico, Atalah exato, hipertermia, ferro×folato -- 4/6 caíram), FA/DRC (DRC estável NÃO contraindica FA), sítios de endometriose (#1 = ovários), fatos secos (ABC Score, LHR/HDC).
- 🩹 **Pré-Natal = cluster frio** -- Revisão Direcionada / aula-base I pendente (não drillar card cru sobre base fria).

## Estado por frente
- **Volume & Metas:** 5128 / 10000 (perf. ~79.3%). Hoje: 0. Ritmo-alvo ~84.0q/dia (58d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** dívida 0 atrasados + 1 p/ hoje -- pool 381 nunca introduzidos (entram <=30/dia). [derivado] s124 introduziu 15 frescos M4 + reforjou 831-835.
- **Conteudo:** 71 resumos em resumos/. **🆕 Corpus EMED: 275 decks de flashcards (7565 cards)** em `resumos/**/Flashcards - *.pdf` (gitignored, consultável via `emed_flashcards.py`). [derivado: glob]
- **Erros & Cards:** 831-835 reforjados v2 (atômicos, EMED-fed) + 836/837 novos (splits). 286/288 aposentados. **A reforjar (padrão novo):** 350/398/757/759.
- **Posicao cronograma:** db=S13 (nominal S16, atraso 3 sem). Drive stale -- `--sync-drive` no próximo boot.

## Pendencias ativas
🃏 Reforjar 350/398/757/759 (padrão atômico EMED-fed). 760 via gate de evidência. Bloco S13 Colecistite (question-first). Ratificar o padrão atômico após 1º uso real de cunhagem-por-erro. Aula-base de Pré-Natal I (cluster frio). Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Ledger `AUDITORIA_MEDHUB.md`: F35 (reconcile volume + seletor de suite auto_check); F8 (isolamento PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025). Banca-dependente no DITC II (belimumabe/nefrite, SAF 2023).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_124.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
