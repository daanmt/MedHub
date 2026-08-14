# PRD: P3 — Fila Priorizada, Proveniência de Revisão e Eficácia de Aprendizado

> Gerado pelo ai-eng em 2026-08-14, continuação direta do ciclo `flashcards-integridade-geracao.md` (parts 1-6, PASS 6/6, `34d712e`). GO do operador para P3; P4 segue data-gated (optimizer só com revlog limpo em volume; `.apkg` sob demanda).
> Ancorado em: `HANDOFF_RESPOSTA_AI_ENG_FLASHCARDS.md` §C.7/C.8 + ideias sobreviventes do anexo GPT (§18/20/22/23/41-43) + gap residual do audit (bypass `update_flashcard_fields`).

## Problem

O ciclo anterior estancou a geração de lixo e deu detecção — mas a dor do **usuário** segue: (1) cards de erro recente esperam semanas no FIFO enquanto o mesmo erro se repete (a priorização existe em `get_fresh_error_cards` e está fora do dreno padrão); (2) o sistema não registra **qual versão** do card o usuário viu nem **por que** o card foi servido — perguntas como "cards v3 têm mais Again que v2?" e "a curadoria funcionou?" são irrespondíveis, e a onda de curadoria das worklists (385+14+278) ficará imensurável se acontecer antes destas colunas existirem; (3) o rating é dado às cegas — o usuário não vê a consequência (intervalos) antes de escolher; (4) a geração não deixa evento persistido (quality_source é autodeclarado) e a reincidência (métrica central de um sistema error-driven) é só um print; (5) `db.update_flashcard_fields` é um caminho de escrita documentado (docstring da regen queue) que contorna o gate de qualidade.

## Target Audience

Primário: **Daniel estudando** (fila que ataca reincidência; rating informado). Secundário: **o agente MedHub** (evidência de eficácia por versão/tipo para orientar curadoria; eventos de geração/reincidência consultáveis).

## Proposed Solution

- **Banda prioritária no dreno padrão**: ordem `vencidos → erros_frescos (janela 48h, cap) → agendados_hoje → novos FIFO`, como bucket novo em `get_cards_by_bucket` (sem duplicar com `novos`), constantes simples (sem tabela de política), `--pre-bloco` intacto. Cada card servido carrega `selection_reason`.
- **Proveniência no revlog**: colunas `card_version` (a versão que o usuário viu, capturada no ato do record) e `selection_reason` (ALTER idempotente, padrão `_ensure_status_column` do repo); `fsrs_queue --record` ganha `--reason`.
- **Preview dos 4 intervalos**: `db.preview_ratings(card_id)` (adapter determinístico, 4× evaluate sem persistir; intervalo pré-balanceador, documentado); exposto no `--next` e em `--preview`; contrato de apresentação codificado em `revisar.md` (inclui a regra anti-vazamento do modo de falha #8).
- **Eventos persistidos**: `history/generation_log.jsonl` append-only (eventos `generation` e `reincidencia` do F25) — ledger_self.record NÃO serve aqui (semântica opened/resolved auto-resolveria eventos passados; decisão consciente contra o C.8.1 original).
- **Eficácia consultável**: `tools/learning_efficacy.py` read-only — rates por `tipo × card_version × quality_source × selection_reason` + reincidência por questão-cardada. Gate anti-decorativo: se em 3 ciclos nenhum número alterar decisão de curadoria/política, remover.
- **Fechar o bypass**: gate ERRO-level (campos presentes) dentro de `update_flashcard_fields`, com degradação anunciada se `card_checks` indisponível.

## Success Criteria

1. Fila padrão serve card de erro fresco ANTES de novos FIFO, com cap e sem duplicata entre buckets (teste); `selection_reason` presente em cada card servido; `--pre-bloco` inalterado.
2. Toda revisão nova grava `card_version` e (quando informado) `selection_reason` no revlog — teste incluindo pós-reforja (v2 vista → revlog registra 2).
3. `--next` traz preview dos 4 ratings; `--preview` idem sob demanda; valores batem com o scheduler determinístico (teste de paridade com `evaluate`).
4. Inserir erro+cards gera evento `generation` no JSONL; hit F25 gera evento `reincidencia`; falha de log NUNCA derruba o insert (teste).
5. `learning_efficacy.py` roda read-only e emite rates por dimensão + reincidência (teste com fixture; execução real é manual).
6. `update_flashcard_fields` recusa card com template/encoding proibido (teste); caminho válido intacto.
7. `pytest` verde (baseline 168) em cada part.

## Scope v0 / Anti-scope

Scope: os 6 itens acima, fatiados em 4 specs (part-1 revlog · part-2 fila · part-3 preview+revisar.md · part-4 eventos+eficácia+bypass).
Anti-scope: **NÃO** tabela de política de fila; **NÃO** optimizer/.apkg/Note→Card (P4/nunca); **NÃO** retro-preencher `card_version` em revlog antigo (proveniência começa agora — honesto); **NÃO** mudar algoritmo/parâmetros FSRS nem o balanceador; **NÃO** UI Streamlit nova; **NÃO** tocar conteúdo clínico; **NÃO** CHECK de schema (segue bloqueado pela decisão nq=1 do lado MedHub).

## Technical Context

- `get_cards_by_bucket` (`db.py:563`) usa `nq < 2` sem COALESCE — migrar para `ativo_where('f.')` na part-2 (consumidor que escapou do censo original).
- Preview: `FSRS.evaluate` é puro/determinístico (`enable_fuzzing=False`); preview mostra intervalo do scheduler PRÉ-balanceador (o record aplica balanceamento ±5% em intervalos ≥4d — documentar no output).
- `_ensure_status_column` (`insert_questao.py:70`) é o padrão de ALTER idempotente do repo — replicar para o revlog em `db.py`.
- Harness: novos test files entram no allowlist `python_files` do `pytest.ini`; CLIs que mexem em stdout no import exigem o guard de import nos testes (lição do ciclo anterior).
- Budget ≤6 arquivos por part.
