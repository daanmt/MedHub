# PRD: Consolidação e Alcançabilidade

> Gerado via rito discover 2026-08-14 (ai-eng/Fable): rodadas = 4 decisões do operador (AskUser) + 3 auditorias funcionais com subagents Sonnet (memória · RAG/eval · filesystem) sobre o substrato `HANDOFF_MEDHUB_SISTEMAS.md` (7 auditores + F3 adversarial).
> Política vigente do operador: **obsoleto SAI — arquivar não é resposta** (morte exige 0 refs vivas); **auto-higiene é passo do protocolo de encerramento** (absorvido/incorporado sai).
> Estancamento já commitado (`49c5512`): norma Zero-PDF morta + `audit_db_state`/`seed_dificuldade` removidos.

## Problem

O medhub passa em toda métrica de correção (182 testes, git 2,5MiB, 0 tabelas mortas) e mesmo assim: ~189MB de índice que nenhum caminho de produção consulta (provado por eval re-rodado hoje); 514 memórias LLM write-only; contador de erros sistemicamente corrompido (25 sub-temas de Cirurgia com `error_count=1250`); 11 normas descrevendo sistemas inexistentes; boot obrigatório de ~70KB que duplica o hook e exige um sync impossível por construção; Streamlit morto há 69 sessões ainda instalado; eval com fixture quebrada há 2,5 meses sem ninguém notar. **O aparato responde "está correto?"; nada responde "alguém chega aqui?".**

## Decisões travadas (operador, 2026-08-14)

1. **Morte confirmada**: Streamlit completo + deps · `reflect.py`+teste (gate anti-decorativo cumprido) · backup externo 19MB · docs absorvidos (lista do auditor de filesystem).
2. **`pdf_raw`: MORRE** — via "eval decide": re-rodado hoje (HEAD `49c5512`), gold satura antes do tier PDF contribuir (count=0 sempre); misses são ranking intra-gold que two-tier não resolve. HyDE **fica** (R@3 .778 on vs .389 off).
3. **Memória: simplificação radical** — manter hook+`load_context`+`weak_areas` (contador CONSERTADO); matar `session_insights` (geração + purge das 514 linhas com backup único); apagar Camada 2 e os 3 namespaces fantasma da doc/schema.
4. **Provas: entidade multi-data** — ENAMED 13/09 ≠ fim-de-grade 25/10 ≠ UERJ/USP TBD; config versionada, countdown por prova, ritmo segue da grade.

## Success Criteria (do ciclo inteiro)

1. Boot: leitura obrigatória cai ≥15% (poda ESTADO/HANDOFF aos contratos) e `AGENTE.md §2 passo 4` não duplica o hook nem exige caminho impossível; Drive fora do caminho crítico (conclusão via coluna `Realizada?` do Sheets, texto do W8 reescrito).
2. Zero referência viva a: Streamlit, `obsidian-notes-rag`, Camada 2, `reflect.py`, `pdf_raw`/two-tier — verificado por grep e pelo novo check de refs.
3. `pytest` verde ao fim de cada part (baseline 182; mortes removem testes junto — contagem documentada por part).
4. Eval do RAG regenerado no repo (fixture corrigida, REPORT.md com data+HEAD) — números de hoje registrados.
5. Contador de memória correto (teste com fixture: sub-temas distintos ≠ mesmo error_count); `session_insights` nem gera nem existe.
6. `auto_check` ganha: check 10 (fk_orphans), check de refs MCP/paths mortos, **check de alcançabilidade v0** (tools/*.py sem nenhum referenciador → WARN); `doc_drift` cobre commands/workflows/contracts.
7. day_plan mostra countdown por prova (`core/provas.json`); AGENTE.md para de misturar referenciais.
8. Filesystem: ~25MB núcleo limpo + rotação keep-5 EMBUTIDA no `backup_db.py` + mirror 19MB deletado; `AGENTE.md` fechamento ganha passo de auto-higiene.

## Anti-scope

NÃO tocar conteúdo clínico (strings opacas) · NÃO tocar o subsistema de flashcards reformado hoje (parts 1-6 + P3) além do wiring já previsto · NÃO deletar PDFs-fonte EMED (política s086) · NÃO reimplementar Camada 2 · NÃO construir UI nova · NÃO otimizar HyDE/embeddings (eval diz que funciona) · NÃO mexer no algoritmo FSRS.

## Execução

7 specs (`consolidacao-part-{1..7}`), implementadas SEQUENCIALMENTE por subagents (Sonnet p/ mecânicas, Opus p/ as de protocolo/lógica), auditadas por mim (Fable) entre cada uma, commit por part. Ordem: 1 morte-código → 2 RAG → 3 memória → 4 boot/protocolo+provas → 5 normas+sensores → 6 wiring/alcançabilidade → 7 filesystem+rito. Fontes de evidência por part: os 3 relatórios dos auditores desta sessão + `HANDOFF_MEDHUB_SISTEMAS.md` §4-§8.
