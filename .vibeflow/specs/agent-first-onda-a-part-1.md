# Spec: Onda A · Part 1 — Revisão Conversacional de Flashcards

> Gerado via /vibeflow:gen-spec em 2026-06-03
> PRD: `.vibeflow/prds/agent-first-onda-a-revisao-fsrs.md`
> Split: part 1 de 2 (por limite de DoD). Ver `agent-first-onda-a-part-2.md`.

## Objective

O agente conduz uma sessão completa de revisão de flashcards dentro da conversa do Claude Code (desktop ou celular via remote-control), puxando a fila de cards vencidos por CLI e gravando os ratings no `ipub.db`.

## Context

Hoje a revisão FSRS só existe no player Streamlit (`app/pages/2_estudo.py`), que é desktop-only e inacessível via remote-control. Já existem as peças de baixo nível: `app/utils/db.py::record_review()` (aplica FSRS + grava `fsrs_cards` e `fsrs_revlog`), a lógica de buckets atrasado/hoje/novo (`tools/review_cli.py`) e, segundo o mapeamento da codebase, uma função de leitura por bucket em `db.py` (`get_cards_by_bucket()`). Falta uma superfície limpa, **machine-readable**, para o agente consumir a fila e gravar a avaliação — e uma skill que documente o loop conversacional.

## Definition of Done

1. `python tools/fsrs_queue.py --next` imprime **um JSON** do próximo card vencido com os campos `id, area, tema, frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha, state, due, bucket`; quando a fila está vazia, imprime um JSON sinalizando vazio (ex.: `{"empty": true}`).
2. A fila honra a política existente: ordem **atrasado → hoje → novo**, filtro `needs_qualitative < 2`, `state = 0` sempre elegível, e filtros opcionais `--area` (exato) / `--tema` (LIKE), com `--limit` e `--new-limit` suportados. `--list` imprime o lote como array JSON.
3. `python tools/fsrs_queue.py --record <card_id> --rating <1-4>` grava a avaliação **delegando para `app.utils.db.record_review()`** (sem reimplementar FSRS nem SQL de escrita) e imprime confirmação com o próximo `due`.
4. A skill `.claude/commands/revisar.md` documenta: (a) a assinatura completa do `fsrs_queue.py`; (b) o protocolo do loop conversacional (apresentar frente → revelar verso só quando o usuário pedir → coletar 1-4 → gravar → próximo card); (c) a regra anti-duplo-registro (o agente rastreia `card_id` já gravados na conversa).
5. **(Quality gate — convenções)** `fsrs_queue.py` segue `conventions.md` para CLIs: `argparse` com `required` nos args obrigatórios, DB path via `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`, conexões sempre fechadas, saída forçada em **UTF-8** (evitar o erro cp1252 do console Windows). Não introduz `import sqlite3` novo — consome `app.utils.db`.
6. **(Quality gate — contrato §7.2)** A assinatura do CLI vive em **exatamente uma** skill (`revisar.md`); nenhum workflow reespecifica os flags. O player Streamlit existente continua funcionando (nada em `app/pages/` é alterado).

## Scope

- `tools/fsrs_queue.py` (novo) — CLI com subcomandos de leitura (`--next`, `--list` + filtros) e de escrita (`--record --rating`), emitindo JSON. Thin wrapper sobre `app.utils.db` (`get_cards_by_bucket` para ler, `record_review` para gravar).
- `.claude/commands/revisar.md` (novo) — skill canônica: assinatura do CLI + protocolo do loop conversacional.

## Anti-scope

- Reescrita do FSRS (é a part-2).
- Qualquer mudança em `app/pages/` (player Streamlit fica como está, desktop-only).
- Geração de cards, Google Sheets MCP, dashboard.
- Persistência remota / migração do SQLite para nuvem.
- Correção dos bugs de closure/`session_state` do player Streamlit.

## Technical Decisions

- **`fsrs_queue.py` como wrapper fino sobre `app.utils.db`, não como novo dono de SQL.** Reusa `get_cards_by_bucket()` (leitura) e `record_review()` (escrita). Trade-off: cria acoplamento CLI→app, mas é o que o pattern `db-access-layer` já autoriza para `tools/` e garante caminho de escrita único + audit trail intacto. Evita duplicar a política de buckets. *Assunção (TODO no implement): confirmar assinatura de `get_cards_by_bucket()`; se ausente/divergente, adicionar uma função de leitura mínima em `db.py` em vez de abrir `sqlite3` no CLI.*
- **Saída JSON por padrão** (consumo por agente). Opcional `--format text` para inspeção humana. `json.dumps(..., ensure_ascii=False)` + stdout em UTF-8.
- **Anti-duplo-registro é responsabilidade do loop (skill), não do CLI.** O CLI é stateless e idempotente por chamada; o agente mantém o conjunto de `card_id` já avaliados na sessão conversacional. Espelha a regra `reviewed_ids` do player Streamlit, mas no nível do agente.
- **Rating 1-4 = Novamente/Difícil/Bom/Fácil**, idêntico ao resto do sistema.

## Applicable Patterns

- `db-access-layer.md` — consumir `app.utils.db`; não abrir `sqlite3` no CLI; escrita via `record_review()`.
- `fsrs-review-flow.md` — política de buckets, filtro `needs_qualitative < 2`, semântica dos ratings, escrita dual `fsrs_cards`+`fsrs_revlog`.
- `agent-workflow-protocol.md` — skill como assinatura canônica do CLI (§7.2); a skill não reespecifica o que o CLI faz, orquestra.
- **Novo pattern (a registrar depois):** "agent-driven review loop" — o agente como player conversacional sobre um CLI JSON. Candidato a `vibeflow:teach` ao fim da Onda A.

## Risks

- **`get_cards_by_bucket()` pode não existir ou ter assinatura diferente** → no implement, verificar primeiro; se necessário, adicionar função de leitura mínima em `db.py` (não abrir sqlite3 no CLI).
- **Encoding cp1252 no console Windows** (já observado nesta sessão com emojis `🔴`/`⭐`) → forçar UTF-8 na saída do CLI; testar com um card que contenha emojis.
- **Re-disparo do agente gravando rating duplicado** → skill documenta idempotência; agente rastreia `card_id` já gravados.
- **Fila vazia / DB ausente** → CLI retorna JSON de vazio sem stacktrace (default seguro, como os count functions do `db.py`).

## Dependencies

Nenhuma. Independente da part-2 (a leitura da fila e a gravação via `record_review()` funcionam sobre o FSRS atual). Ordem de execução recomendada: **esta part-1 primeiro**, part-2 depois.
