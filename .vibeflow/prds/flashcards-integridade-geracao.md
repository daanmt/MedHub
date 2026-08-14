# PRD: Integridade da Geração e Auditoria de Flashcards

> Gerado pelo ai-eng em 2026-08-14, a partir de `HANDOFF_RESPOSTA_AI_ENG_FLASHCARDS.md` (resposta ao handoff de flashcards; escopo = P0-P2 do plano priorizado)
> Ancorado em: pré-auditoria interna do MedHub (`HANDOFF_MEDHUB_FLASHCARDS.md` no ai-eng, §6.5) + verificação de terreno do ai-eng (HEAD `ad1ccde`)
> Relacionado: `pipeline-conhecimento.md`, `auto-suficiencia-card-e-telemetria-fila.md`, `engenharia-ledger-f1-f13.md`

## Problem

O pipeline que gera flashcards a partir de erros tem um caminho de fallback heurístico que produz artefatos inúteis **em silêncio**, e a suíte de auditoria não o detecta. Incidente real (2026-08-13): 34 registros inseridos via `--errors-file` sem `cards` → 68 cards gerados pelo template, 68/68 inutilizáveis, 0 sinalizados por qualquer auditor. Três causas independentes, todas confirmadas com `arquivo:linha`:

1. **Geração sem gate**: `insert_questao.py:172-206` fabrica pergunta por template (banido verbatim pela spec `estilo-flashcard.md:26`), embute o `titulo` na pergunta, trunca campos com slice cego e reintroduz `needs_qualitative=1` (banido pelo contrato). Os gates de qualidade existem em **um** só writer (`apply_reforja.py::_validar`) — os 4 que mais escrevem não validam nada.
2. **Detectores cegos por desenho**: `audit_flashcard_quality.py:164` exclui do agregado exatamente os sinais que pegariam o defeito; `audit_card_atomicity.py` nunca lê os campos truncados; nenhum detector compara campos entre si (os defeitos reais são todos relacionais).
3. **Harness olha código, dado vive fora do git**: `auto_check.py:239-244` só dispara checks de card quando arquivo **staged** muda; cards vivem no `ipub.db`. O dado não tem gate; só o código que o produz tem.

Agravantes de integridade confirmados: `record_review` não é idempotente (blind write, incidente card 403/s108; Invariante C do contrato sem trava técnica); `get_fresh_error_cards` não filtra `needs_qualitative` (aposentado em quarentena reaparece); 3 definições divergentes de "card ativo" em 5 arquivos (uma delas semanticamente errada); **nenhuma conexão liga `PRAGMA foreign_keys`** — todas as FKs do schema são decorativas.

## Target Audience

Primário: **o agente MedHub** — que cunha, audita e reforja cards e hoje pode produzir lixo silencioso. Secundário: **o usuário (Daniel)** — que revisa os cards via `/revisar` e cujo diagnóstico de padrões de erro é contaminado por defeito de card (F39: 5 de 6 "padrões de erro do usuário" eram defeito de card).

## Proposed Solution

Três ondas, na ordem estancar → integridade → detecção:

- **P0 Estancar**: matar o caminho heurístico (todos os callers reais são agent-first; "aposentado por convenção" já reapareceu uma vez — só remoção segura). `cards` ausente ou `[]` → erro alto com mensagem apontando a régua. Exceção única preservada: `status in (anulada, banca-divergente)` registra erro sem card (F26). Fechar o vazamento de `needs_qualitative` em `get_fresh_error_cards`, corrigir o `nq != 2` da `cards_regen_queue`, ligar `PRAGMA foreign_keys=ON` na fábrica de conexão + varredura única de órfãos (report, não delete).
- **P1 Integridade**: lock otimista em `record_review` (WHERE sobre `last_review` lido + rowcount; rollback em corrida; revlog só grava se o UPDATE pegou) — Invariante C vira trava técnica. Corrigir de passagem o caso `df.empty` (hoje o UPDATE atinge 0 linhas e a revisão se perde do estado, só fica no log). VIEW `flashcards_ativos` + helper único; migração dos consumidores por teste de equivalência de contagem. Extrair `card_checks.py` (biblioteca pura de predicados) dos gates de `apply_reforja._validar` e ligá-la nos 5 writers; `recurate_cards` sem nenhum campo válido → erro (hoje é no-op disfarçado de reforja bem-sucedida).
- **P2 Detecção**: 6 detectores cross-field na mesma biblioteca (resposta_embutida, pergunta_template, distrator_perdido, multi_parte, negativo_orfao, contexto_artefato) consumidos por write-gate e batch; fixtures **sintéticas** replicando a estrutura dos 68 do incidente (texto clínico fora do git); suíte própria para `audit_card_atomicity`; calibração ≥66/68 contra o banco real (medida, registrada no ledger). `auto_check` passa a disparar checks de card por **watermark de dado** (`MAX(id), COUNT(*), MAX(card_version)` persistidos), não por arquivo staged; os 3 sinais excluídos voltam ao agregado e ao `--export`.

## Success Criteria

1. `python tools/insert_questao.py --errors-file <lote sem cards>` **falha com erro** citando a régua; zero linhas gravadas (transação intacta). Item com `status='anulada'` continua registrando erro sem card.
2. O caminho heurístico não existe mais no código: `grep "qual a conduta/criterio correto"` e `grep "Qual o distrator tipico"` em `tools/` retornam zero; `frente_elo`/`verso_elo` não são mais computados.
3. `get_fresh_error_cards` não retorna cards com `COALESCE(needs_qualitative,0) >= 2` (teste com fixture); `cards_regen_queue` usa a definição canônica de ativo.
4. Conexões via `db.get_connection()` têm `PRAGMA foreign_keys=ON` (testável por `PRAGMA foreign_keys` == 1); relatório de órfãos pré-existentes emitido uma vez (WARN, sem delete).
5. Duas chamadas de `record_review` sobre o mesmo estado lido: a segunda falha e **não** insere linha no revlog (teste determinístico simulando a corrida); revisão de card sem linha em `fsrs_cards` cria a linha em vez de perder o estado.
6. `flashcards_ativos` (VIEW) existe; os consumidores de "ativo" divergentes usam a view/helper; contagens pré/pós-migração registradas e explicadas.
7. Os 5 writers chamam `card_checks.validar_card`; card com pergunta-template ou resposta-embutida é **recusado** na escrita (teste por writer).
8. Detectores batch atingem recall ≥ 66/68 nos cards do incidente (`questao_id 781-814`) sem tocar conteúdo clínico — número medido e registrado no `ledger_self.jsonl`.
9. `auto_check` roda os checks de card quando o watermark do banco mudou, mesmo com zero arquivos staged relevantes (teste com watermark artificialmente movido).
10. `pytest` na raiz: verde antes e depois de cada spec (baseline atual: 115 passed).

## Scope v0

- `tools/insert_questao.py`: remoção do caminho B + contrato de erro para `cards` ausente/vazio + remoção de código morto (`frente_elo`/`verso_elo`, regex de trigger, slices de truncamento).
- `app/utils/db.py`: PRAGMA na fábrica; filtro nq em `get_fresh_error_cards`; lock otimista + upsert em `record_review`; VIEW `flashcards_ativos` + helper `ativos()`.
- `tools/cards_regen_queue.py`: definição canônica de ativo.
- `tools/card_checks.py` (novo): predicados puros (gates de `apply_reforja` + 6 cross-field), sem I/O de banco no núcleo.
- Writers (`insert_questao`, `insert_card_base`, `insert_card_extra`, `recurate_cards`, `apply_reforja`): chamam a biblioteca; `recurate_cards` erro em item vazio.
- `tools/audit_flashcard_quality.py`: sinais excluídos voltam ao agregado; detectores cross-field expostos no batch.
- `tools/auto_check.py`: watermark de dado para checks de card.
- Testes: contrato do insert, predicados (fixture sintética por anti-padrão + controle), suíte do atomicity, equivalência da view, idempotência do record_review, watermark.
- Varredura única de órfãos FK (read-only, WARN).

## Anti-scope

- **NÃO tocar conteúdo clínico** de nenhum campo — todos os predicados são estruturais/relacionais; fixtures com texto dummy (fronteira dura, safeguards Fable).
- **NÃO adicionar CHECK constraints de schema** neste ciclo — exige decisão pendente do lado MedHub sobre a semântica de `needs_qualitative=1` (contrato × banco divergem) e rebuild de tabela; registrado como pendência, não como task.
- **NÃO deletar** os 139 cards `heuristic` nem os 68 do incidente — são dados/fixture de calibração.
- **NÃO implementar P3/P4**: banda prioritária no dreno, `card_version`/`selection_reason` no revlog, log de geração, preview de intervalos, optimizer FSRS, `.apkg`, benchmark RAG, drop das colunas `frente`/`verso` — próximos ciclos, com decisões próprias.
- **NÃO alterar** o algoritmo/parâmetros FSRS (`learning_steps=()` é decisão documentada e testada), o load balancer, nem o `--pre-bloco` (só herda o filtro nq corrigido).
- **NÃO mudar defaults de dry-run** dos CLIs existentes (mudaria contratos que os workflows do agente já usam); a inconsistência fica registrada para decisão do lado MedHub.
- **NÃO criar** tabela de política de fila nem tabela `card_feedback`.

## Technical Context

- **Padrões a seguir**: `patterns/db-access-layer.md` (sqlite3 só em `db.py`; exceção documentada: `insert_questao.py` standalone), `patterns/error-insertion-pipeline.md`, `patterns/warn-first-check.md` (checks novos estreiam como WARN; promoção a BLOCK é decisão posterior — exceto o gate de escrita do insert, que é erro por definição do contrato), convenções pt-BR, `finally: conn.close()`.
- **Gates existentes a extrair**: `apply_reforja.py::_validar` (`:61-105`) — schema, encoding, atomicidade. A extração não pode mudar o comportamento do `apply_reforja` (seus testes de gate continuam passando).
- **Fixture real de calibração**: 68 cards, `questao_id BETWEEN 781 AND 814`, todos `needs_qualitative=2` (confirmado 2026-08-14). Padrões estruturais: 34 perguntas `LIKE tema||':%'`; 34 com `titulo` embutido; `verso_armadilha` com `LENGTH=200` exato; contexto com "N% acertaram".
- **Watermark**: persistir em `history/` (padrão do repo para estado de harness — `ledger_self.jsonl` já vive lá). Tripla `(MAX(flashcards.id), COUNT(*), MAX(card_version))` cobre insert, delete e reforja.
- **`record_review`**: conexão única já existe; a mudança é WHERE condicional + `rowcount` + rollback + INSERT condicionado — sem schema novo. `ConcurrentReviewError` (ou retorno de erro claro) para o chamador (`fsrs_queue.py`).
- **Banco fora do git**: nenhum teste pode depender do `ipub.db` real; calibração (criterion 8) é script manual rodado uma vez contra o banco, com resultado persistido no ledger — não é teste de CI.
- **Backup**: `python tools/backup_db.py` antes de qualquer experimento que escreva (feito: `ipub_backup_20260814_163553.db`).
- **Budget**: ≤6 arquivos por task → fatiar em ~5 specs: (1) insert-contrato+P0-queries+PRAGMA; (2) record_review+view-ativos; (3) card_checks+writers; (4) detectores+fixtures+suítes; (5) watermark+agregado+calibração.

## Open Questions

1. **Semântica de `needs_qualitative=1`** (contrato proíbe, banco tem 11, fluxo usa como "sinalizado para reforja") — decisão do lado MedHub; bloqueia só o CHECK de schema (anti-scope), não este ciclo.
2. `ConcurrentReviewError`: o chamador `fsrs_queue.py` deve expor retry ao usuário ou só reportar? v0: reportar e não regravar (fail-safe).
3. Órfãos FK pré-existentes, se houver: limpar é decisão de dado do lado MedHub — este ciclo só reporta.
