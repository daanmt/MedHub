# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-14 (noite) -- Sessão 144 -- ENGENHARIA: auditoria de arquitetura dos 7 sistemas não-flashcard.*

## > Próximo passo imediato

1. **Novo boot como teste de aceitação.** O usuário pediu explicitamente para aferir se a arquitetura
   melhorou depois dos ajustes do ai-eng. Medir: quantas chamadas de ferramenta até o primeiro ato útil.
   Baseline desta sessão = **~15**. Alvo do desenho proposto = **0-1** (o hook `SessionStart` já entrega
   o Plano do Dia antes do primeiro turno).
2. **Dívida de estudo herdada da s143, intocada** (a s144 foi 100% engenharia, volume do dia = 0):
   redrill dos **42 cards nota < 4** (`tmp/redrill42.json`; 18 nota 1 -> 10 nota 2 -> 14 nota 3) e os
   3 gaps de Revisão Direcionada: **AGC/colpocitologia** (card 453, na fila), **escores estimados em vez
   de somados** (PRAM/Caprini/Apgar), **"diagnóstico feito != pode tratar"** (card 538, na fila).
3. **GO pendente do operador** sobre a lista de morte/consertos da auditoria -- ver `ai-eng/HANDOFF_MEDHUB_SISTEMAS.md`.
   O ai-eng já estancou os 3 itens de perda irreversível (`49c5512`); o resto aguarda.
4. **Fork aberto, precisa de decisão:** collection `pdf_raw` do Chroma (14.216 chunks, ~192MB, 93% de
   `data/`) -- conectar (1 linha em `get_topic_context.py:177`) ou deletar. Pré-requisito: re-rodar
   `tools/eval/run_eval.py` (o `REPORT.md` é de 27/05, anterior ao two-tier).

## Estado por frente
- **Volume & Metas:** 6019 / 9454 (perf. ~78.4%). Hoje: 0. Ritmo-alvo ~47.7q/dia (72d p/ Cronograma EMED (grade completa)).
- **FSRS:** divida 3 atrasados + 40 p/ hoje -- pool 554 nunca introduzidos (entram <=40/dia).
- **Conteudo:** 125 resumos em resumos/. [derivado: glob]
- **Posicao:** conteudo S14 (nominal S20, atraso 6 sem) [derivado: preparacao_estado]
- **Simulados:** S2 54/100 (02/08) -> S3 60/100 (06/08) -> S4 66/100 (13/08). Próximo pendente.
- **Datas:** ENAMED **13/09** (prova). Grade EMED fecha ~25/10. UERJ/USP ~out-dez, sem edital.

## Última sessão -- s144 (ENGENHARIA)

Auditoria de arquitetura dos 7 sistemas não-flashcard, disparada pela crítica do usuário ao boot caro.
Loop de 5 fases: scout inline -> 7 subagents Sonnet 5 em paralelo -> cross-check -> verificação
adversarial dos `MATAR` por grep -> síntese. Regra imposta: **arquivar não é resposta; fica ou morre,
e morrer exige prova de zero referência viva.**

**Tese:** a acumulação não é desleixo. O git tem 2,55 MiB, o expurgo de julho foi validado, 182 testes
passam, 12/12 tabelas do `ipub.db` estão vivas e o `.vibeflow/` é mecanismo ativo. O que se acumulou são
**artefatos que funcionam e que nenhum caminho de execução alcança**: 192MB de índice RAG desconectado
por 1 linha, 514 `session_insights` write-only, 11 normas descrevendo sistemas mortos, 2 scripts que
corrompiam dado, 1 sensor pronto e não plugado. Tudo passou pelos gates -- **os gates verificam se está
correto, nada verifica se alguém chega lá.**

**6 defeitos estruturais (D1-D6)**, com `arquivo:linha` no handoff ao ai-eng. Os dois que importam aqui:
**D5** -- o hook `SessionStart` já roda `day_plan.py` antes do primeiro turno e o `AGENTE.md §2 passo 4`
manda rodar de novo, além de exigir um sync do Drive por caminho impossível; 272 palavras do passo
duplicam verbatim o W8 do `reconcile-contract.md`. **D3 -- warning-first virou warning-only:**
`doc_drift.py` reporta "0 achados" olhando 4 arquivos onde as normas mortas não estão; B1 do reconcile
estava ativo e não bloqueou; `sync_skills --check` falha desde 17/07 sem ação.

**Bug aberto:** o `(1250 erros)` do boot vem de `app/memory/manager.py:91-128` (`GROUP BY area` sozinho +
substring com `break`); 25 registros com o mesmo número em 8 áreas. Conserto ~15 linhas, sem schema.

**Correções registradas:** o ritmo medido contra 25/10 e não contra o ENAMED **não é bug** (correção
deliberada da s126, `day_plan.py:508-509`); `history/legacy/` não é lixo; a Camada 3 da memória está viva,
e quem escreve é `tools/hooks/memory_session_log.py`, não o nome citado no `AGENTE.md §8`. A reforma de
flashcards de hoje mais cedo (`8006471`..`cb5d9e2`) não foi selada; rastro dentro de `session_144.md`.

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_144.md*
*Auditoria: ai-eng/HANDOFF_MEDHUB_SISTEMAS.md * Relatório: artifact 5d536604*
