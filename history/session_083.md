---
type: session
---

# Sessão 083 — Bloco GO + DITC (75q) + capacidade de gestão da curva de esquecimento (F1-F6)

*2026-06-15 | Claude Code (Opus 4.8)*

## Resumo

Sessão dupla: **estudo por questões** (volume recuperado após 3 sessões a 0) + **construção de uma capacidade nova** — gestão ativa da curva de esquecimento, planejada e executada ponta a ponta (F1-F6). Trilho de estudo conduzido por remote-control; trilho de engenharia sob mandato de autonomia ("terceirizar a gestão").

## Estudo (75q / 61a · 81%)

- **Bloco GO (Ginecologia) — 54q / 41a (76%)**, diretriz 2016: mama benigna, climatério/TH, rastreio colo, úlceras genitais. 13 erros → **13 cards atômicos** (ids 446-458). Consolidados Q1≡Q9 (LSIL <25 → 3 anos) e Q10≡Q12 (cancro mole × donovanose) — caíram 2× pelo mesmo motivo.
- **Bloco DITC (Reumato) — 21q / 20a (95%)**. 1 erro = DMTC (manifestações mais frequentes = Raynaud + poliartrite, não rash malar) → card 459 + **`DITC.md` ganhou §4 Doença Mista do Tecido Conjuntivo** + 2 armadilhas (DMTC; sinal × pápulas de Gottron). Gap de base, não de leitura.
- **6 padrões metacognitivos** no bloco GO (mapeados aos bugs conhecidos): flag "gestante" perdida 2× (Q4/Q8); ancoragem no "sangra-fácil" (Q12, bug nº1); regra de idade no rastreio aplicada errado 2× (fato-no-contexto-errado); ATA esquecido 2× (Q8/Q11); palpite certo abandonado por palavra/medo (Q6/Q2); **2016 × 2025** = armadilha banca-dependente (ler qual diretriz a questão cita).
- Volume acumulado **3316 → 3391**; bloco 3 (Nefro, 40q) ficou pendente (com micro-refresh de DRC já entregue).

## Capacidade nova — curva de esquecimento (F1-F6, planejada + aprovada)

Plano em `.claude/plans/que-tal-planejar-melhor-*.md` (3 Explore + 1 Plan agent; verificação contra o db ao vivo).

- **F1 — `review_log`** (SSOT do tempo-de-revisão temática) em `init_db.py` + helpers `db.py` (`log_review`, `get_theme_last_review`, `resolve_tema_id`); radar lê o log.
- **F2 — `/refrescar`** (`tools/dormant_refresh.py` `--pick/--context/--stamp` + skill): re-ensino narrativo de 1 tema dormente/dia, substrato via `get_topic_context`. **Fronteira dura: não toca o FSRS** (verificado por snapshot).
- **F3 — boot proativo "Plano do Dia"** (`AGENTE.md §2 passo 4` + `tools/day_plan.py`): cruza dormência × volume × FSRS × cronograma e lidera com plano decidido.
- **F4 — dedup da taxonomia [DESTRUTIVO]** (`tools/dedup_taxonomia.py`, backup-first + dry-run): colapsou **22 grupos duplicados (126→86 linhas, 40 deletadas)**, remap de FK antes do delete (0 órfãos, 267/456 filhos preservados, integrity ok), **`UNIQUE(area,tema)`** criado + fix de raiz em `insert_questao.py`/`insert_card_base.py` (lookup por `(area,tema)`). Achado: `taxonomia.questoes_realizadas` é legado (não o SSOT de volume — esse é `sessoes_bulk`) → merge MAX.
- **F5 — backfill** (`tools/backfill_review_log.py`): semeou **47 temas** em `review_log` de sinal real (20 fsrs + 27 taxonomia), nunca data fabricada.
- **F6 — contrato** `core/contracts/forgetting-curve-contract.md` + `AGENTE.md` §1.1 (autonomia), §6 (decisão + invariante anti-poluição), §5.5 (SSOT review_log), §7.3/§7.4 (skill + CLIs).

## Google Drive

Acesso confirmado à pasta **"Extensivo EMED"** (via `conteudo@daktus.com.br`) — metadata e leitura por ID funcionam. **Enumeração por `parentId` falha mesmo no dia seguinte** (não é só propagação; provável particularidade do compartilhamento/índice). Política definida: apostilas PDF = fonte (Zero PDF); "sugestões de flashcards" **não viram cards automaticamente** (filosofia metacognitiva). Investigar o tipo de share numa próxima.

## Decisões

- **Autonomia (AGENTE §1.1):** o agente decide o próximo passo e executa; pausa só em fork real / op destrutiva sobre SSOT / fronteira de PR / BLOCKING.
- **Identidade do tema = `(area, tema)`** com UNIQUE; re-poluição neutralizada na raiz.
- **Refresh dormente ≠ /revisar:** tema-level narrativo vs card-level; nunca toca o FSRS.
- Merge da dedup por **MAX** (não SUM) — a coluna é cosmética.

## Próximo

- **VOLUME** segue prioridade — fechar o bloco 3 (Nefro, 40q) pendente; ritmo-alvo ~94q/dia (junho não fecha; foco em 13/09).
- **Estrear o boot proativo** na próxima abertura (rodar `day_plan.py` → liderar com plano) e o 1º `/refrescar` real (radar aponta Icterícia e Sepse Neonatal, 60d).
- Re-testar os 4 refeitos da s081 (428/68/74/82) + escada de Cardiopatias via FSRS.
- Tier-3 (schema de altura) e limpeza `[bulk]`/`Geral` seguem pendentes.

*75 questões (54 GO + 21 Reumato) · 14 cards · 1 capacidade nova (F1-F6).*
