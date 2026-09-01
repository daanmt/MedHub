# Spec: Descolar part-5 — RAG com sensores (F48)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.

## Objective

O RAG para de servir texto desatualizado em silêncio e de depender da sorte: staleness do índice
vira sensor, o HyDE ganha timeout e determinismo de temperatura, o upsert para de deixar cauda, e
o chunker (76 linhas puras, 0 testes) ganha rede.

## Context

Medido pela s160: índice reconstruído 26/08, 3 resumos editados depois, **6 chunks servindo texto
desatualizado agora**; `rag.py:229` upsert não deleta a cauda quando o resumo encolhe (chunks
órfãos `{stem}::N`); `rag.py:167` HyDE sem timeout (pior caso ~30min pendurado) e sem
`temperature=0` — o eval já documentou swing de 17pp run-a-run; `_chunk_by_headers` sem NENHUM
teste; eval manual (15/08), fora do auto_check.

## Definition of Done

1. [ ] Check `rag_staleness` no auto_check (WARN): `mtime` máximo de `resumos/**/*.md` vs
       timestamp da última indexação (persistido pelo `index_resumos.py` num meta local) →
       resumos mais novos que o índice = WARN com contagem. Sem meta (índice antigo) = WARN
       "indexação sem carimbo — re-rode index_resumos".
2. [ ] Cliente HyDE com `timeout` explícito (30s) e `temperature=0`; falha/timeout cai no
       caminho textual existente (fallback já há — agora com teto de espera).
3. [ ] Upsert deleta a cauda: reindexar resumo que ENCOLHEU remove os `{stem}::N` além do novo
       máximo — teste unitário do cálculo de ids a deletar (collection mockada, sem Chroma real).
4. [ ] `tools/test_rag_chunker.py`: ≥3 testes de `_chunk_by_headers` (header simples, aninhado,
       arquivo sem headers) — função pura, sem rede/db.
5. [ ] Suite verde; craftsmanship: nenhuma chamada de rede em teste; `mode=ro` onde só se lê.

## Scope

`app/engine/rag.py` · `tools/index_resumos.py` (carimbo de indexação) · `tools/auto_check.py`
(check) · `tools/test_rag_chunker.py` (novo) · `pytest.ini` (≤6).

## Anti-scope

- Automatizar o eval do RAG no auto_check (o eval é honesto e caro — decisão de cadência é do
  dono; o PRD registra como candidato pós-ENAMED).
- Mudar embeddings/coleção/two-tier (removidos por decisão anterior — não ressuscitar).
- Reindexação automática (o sensor ACUSA; quem indexa é o operador/skill — WARN-first).

## Applicable Patterns

- `domain-engine-api.md` (a superfície `get_topic_context` não muda) · `warn-first-check.md`.

## Risks

- Carimbo de indexação novo pode não existir em índices antigos → o check trata ausência como
  WARN instrutivo, nunca crash (fail-open, padrão watermark).

## References

- `ai-eng/HANDOFF-MEDHUB-COLA.md` §4 F48 (números medidos) · `.vibeflow/index.md` §RAG.
