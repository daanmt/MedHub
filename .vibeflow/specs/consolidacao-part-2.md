# Spec: consolidacao-part-2 — RAG: poda do pdf_raw + eval honesto

> PRD: `consolidacao-alcancabilidade.md` · Decisão "eval decide" RESOLVIDA: eval re-rodado 14/08 (HEAD `49c5512`) — gold satura antes do tier PDF contribuir (count=0 em todos os testes forçados até n=20); misses são ranking intra-gold. HyDE FICA (R@3 .778 on vs .389 off).

## Objective
O caminho morto do RAG sai (~189MB + código F17), o eval volta a rodar de verdade no repo e o REPORT reflete o presente.

## Definition of Done
1. [ ] `tools/eval/queries.json`: 2 paths corrigidos ("Síndromes Hipertensivas **na** Gestação" → "**da** Gestação"; go-003/go-004 conforme relatório do auditor).
2. [ ] `python tools/eval/run_eval.py` roda no repo SEM patch (Ollama up) e `tools/eval/REPORT.md` é regenerado com data 2026-08-14 + HEAD sha + números novos (referência do auditor: hyde=on R@1=.500 R@3=.778 R@5=.833 MRR=.638; divergência >5pp → investigar antes de gravar).
3. [ ] Morte do fork: collection `pdf_raw` deletada do Chroma + 6 diretórios UUID órfãos (~3.6MB) removidos de `data/chroma/`; `git rm tools/index_pdf_raw.py tools/test_rag_two_tier.py`; bloco F17 de `app/engine/rag.py` (~:380-613: `get_pdf_collection`, `index_pdf(s_raw)`, `search_two_tier`, `_aplica_sombreamento`, helpers) removido; `pytest.ini` sai `test_rag_two_tier.py`.
4. [ ] `emed_flashcards.py --harvest`: passo de cópia de PDFs para `resumos/` avaliado — se as cópias só existiam para o índice morto E os originais existem em outro lugar, o passo sai e as cópias órfãs são listadas (REMOÇÃO física só na part-7, com a lista); se são fonte única, ficam e o motivo é documentado no próprio harvest.
5. [ ] Cadeia HyDE honesta: fallback `llama3` (não-pulled, mascarado pela API key) removido da cadeia OU documentado como opcional com check; sem tier fantasma.
6. [ ] `grep -ri "pdf_raw\|two_tier\|search_two_tier"` (fora de history/.vibeflow/artifacts) → 0 refs vivas; `search()` gold + fallback textual INTOCADOS (smoke: `search("insuficiencia")` retorna N>0).
7. [ ] `pytest` verde; contagem documentada.

## Scope
`tools/eval/{queries.json,REPORT.md}` · `app/engine/rag.py` · `tools/index_pdf_raw.py`✝ · `tools/test_rag_two_tier.py`✝ · `tools/emed_flashcards.py` · `pytest.ini` · `data/chroma/` (delete collection + órfãos).

## Anti-scope
NÃO tocar gold/chunking/embeddings/HyDE-core; NÃO deletar PDFs (part-7 decide com a lista); NÃO tocar `index_resumos.py`.
