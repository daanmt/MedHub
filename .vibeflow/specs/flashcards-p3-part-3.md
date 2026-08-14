# Spec: flashcards-p3-part-3 — preview dos 4 intervalos + contrato de apresentação

> De: `.vibeflow/prds/flashcards-p3-fila-proveniencia.md` · 2026-08-14 (ai-eng)
> Dependencies: .vibeflow/specs/flashcards-p3-part-2.md (fila emite selection_reason)

## Objective

O usuário vê a consequência de cada rating ANTES de clicar (Again→10m · Good→5.8d · …), e o contrato de apresentação da revisão conversacional fica codificado — não tribal.

## Definition of Done

1. [ ] `db.preview_ratings(flashcard_id) -> dict`: lê o estado FSRS (ou init p/ card novo) e roda `FSRS.evaluate` 4× sobre CÓPIAS — zero escrita (teste: contagens de revlog/fsrs_cards inalteradas); retorna por rating `{scheduled_days, due}` + rótulo humano (`<1d` → minutos/`hoje`; senão `Nd`).
2. [ ] Paridade testada: para o mesmo estado, `preview_ratings[r].due == evaluate(estado, r).due` (scheduler determinístico, `enable_fuzzing=False`); nota no retorno: intervalo é PRÉ-balanceador (`balanceado_apos_record: true` quando intervalo ≥4d — o record pode deslocar ±5%).
3. [ ] `fsrs_queue --next` embute `preview` no card servido; ação nova `--preview CARD_ID` emite só o preview (JSON); `--list` NÃO embute (custo 4×N desnecessário fora do momento de rating).
4. [ ] `.claude/commands/revisar.md` ganha seção curta "Contrato de apresentação" (marcada `part-3/P3`): mostrar o preview junto dos 4 botões/opções; gravar com `--reason` propagando o `selection_reason` servido; exibir "por que este card" ao usuário; **NÃO exibir tema/área acima da pergunta antes da revelação** (codifica o modo de falha #8, que era correção tribal).
5. [ ] Craftsmanship: `pytest` verde; nenhuma escrita nova em caminho de leitura; pt-BR.

## Scope
`app/utils/db.py` · `tools/fsrs_queue.py` · `.claude/commands/revisar.md` · `tools/test_preview_ratings.py` (novo) · `pytest.ini`. [4+config]

## Anti-scope
NÃO aplicar o balanceador no preview (mostrar a intenção do scheduler; o deslocamento é do record); NÃO cachear; NÃO UI Streamlit; NÃO reescrever `revisar.md` além da seção nova (edição mínima, marcada).

## Technical Decisions
- Preview em `db.py` (não no adapter): precisa ler estado do banco; o adapter permanece puro.
- `--list` sem preview: o preview pertence ao momento do rating (1 card), não à listagem (N cards × 4 evaluates).
- Paridade com `evaluate` como teste-contrato: se o scheduler mudar, o preview quebra JUNTO — nunca mente.

## Applicable Patterns / Risks
- db-access-layer; agent-workflow-protocol (revisar.md é contrato do agente). Risco: divergência preview×record pelo balanceador → mitigado pelo flag `balanceado_apos_record` explícito no retorno.
