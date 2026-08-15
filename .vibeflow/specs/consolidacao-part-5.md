# Spec: consolidacao-part-5 — normas que mentem + sensores que olham para o lado certo

> PRD: `consolidacao-alcancabilidade.md` · D1/D2/D3 do handoff (consertos 4/5). A doença: decisão tomada e não propagada; sensores calibrados para não incomodar.

## Objective
Nenhuma norma viva instrui chamar sistema morto; os sensores passam a cobrir exatamente onde as normas mentem.

## Definition of Done
1. [ ] **Refs a `obsidian-notes-rag` (10 arquivos)**: substituídas por `app.engine.rag.search()` ou removidas — prioridade `.claude/agents/evidence-researcher.md` (frontmatter `tools:` quebra o subagent hoje). Lista-fonte: handoff §3-D1 + grep fresco. `gerar-reforco.md:14-15,26` corrigido (player Streamlit + MCP mortos).
2. [ ] **Normas mentirosas restantes do §4/D2** corrigidas: `evidence-governance.md:64` · `revisar.md:131,150` · `pesquisar-evidencia.md:33` · `curar-cards.md:46` · `ESTADO.md:52` (o que a part-4 não cobriu) — cada uma: ou a norma passa a descrever o real, ou a seção morre.
3. [ ] **`.vibeflow/index.md`+`conventions.md` regenerados/corrigidos**: fora "4 pages"/"FSRS v4 custom"/"obsidian-notes-rag MCP"/frente-verso-fallback — reflete o repo pós-reforma (flashcards parts 1-6+P3 + este ciclo).
4. [ ] **`doc_drift.py` cobre onde a doença mora**: escopo estendido a `.claude/commands/`, `.agents/workflows/`, `core/contracts/` — modo novo barato: além das anotações drift-check, varre REFERÊNCIAS (paths de arquivo citados existem? nomes `mcp__X__*` existem em `.mcp.json`?) e WARNa; allowlist antiga preservada.
5. [ ] **`sync_skills.py`**: espelho regenerado (PARITY_DRIFT `revisar` zerado — as ~20 linhas de proveniência de hoje entram) e o check continua no auto_check.
6. [ ] `pytest` verde + `python tools/doc_drift.py` roda e pega uma ref morta plantada em fixture de teste (teste novo do modo refs).

## Scope
Os 10+ arquivos de norma citados · `tools/doc_drift.py` · `tools/sync_skills.py` (regen) · `.vibeflow/{index,conventions}.md` · teste novo (allowlist).

## Anti-scope
NÃO criar linter genérico de markdown; NÃO tocar contratos além das linhas que mentem; NÃO reordenar/reescrever normas vivas corretas.
