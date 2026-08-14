# Spec: flashcards-integridade-part-3 — biblioteca card_checks + gate nos writers principais

> De: `.vibeflow/prds/flashcards-integridade-geracao.md` · Gerado 2026-08-14 (ai-eng)
> Ordem: 3ª de 6. Dependencies:
> - .vibeflow/specs/flashcards-integridade-part-1.md (insert_questao já no contrato novo)

## Objective

Os gates de qualidade saem do único CLI que os tem e viram biblioteca pura (`card_checks.py`) com os 6 predicados cross-field novos, plugada nos dois writers principais (`insert_questao`, `apply_reforja`) — card com defeito estrutural é recusado na escrita.

## Context

Gates existem em UM lugar: `apply_reforja.py::_validar` (`:61-105` — schema, encoding `RE_PROIBIDO`, atomicidade via import de `audit_card_atomicity.checar_front/checar_verso`). Nenhum roda nos writers que criam a maioria dos cards. Nenhum detector existente compara campos entre si — e os defeitos reais do incidente são todos relacionais (resposta embutida na pergunta via `titulo`; template; distrator perdido). A spec de autoria (`estilo-flashcard.md`) nomeia 3 anti-padrões; só 2 têm detector.

## Definition of Done

1. [ ] `tools/card_checks.py` existe: núcleo **puro** (sem I/O de banco) — `validar_card(card: dict, contexto: dict | None = None) -> Resultado` com `erros` (bloqueiam escrita) e `avisos`; `RE_PROIBIDO` mora aqui (fonte única); atomicidade reusa `audit_card_atomicity.checar_front/checar_verso` (import, sem duplicar).
2. [ ] Predicados cross-field implementados e testados (1 fixture positiva + 1 controle cada, texto dummy): `pergunta_template` (3 anti-padrões da spec + `"Qual o distrator tipico"` + prefixo `tema + ':'` via contexto) → **erro**; `resposta_embutida` (run comum normalizado ≥ 6 tokens OU Jaccard > 0.5 entre frente e `verso_resposta`/`titulo` do contexto) → **erro**; `multi_parte` (≥2 `?` ou conectivo composto) → aviso; `negativo_orfao` (`NÃO|EXCETO` sem lista no card) → aviso; `contexto_artefato` (`N% acertaram/caem/marcam/erram/...`) → aviso; `checar_distrator(questao, cards)` (`alternativa_marcada` não-vazia ausente de todos os campos dos cards derivados) → aviso por questão.
3. [ ] `insert_questao.py` chama `validar_card` para cada card do caminho A antes do INSERT; qualquer **erro** → `ValueError` com todas as violações listadas de uma vez (padrão do repo: relatar tudo, não ping-pong), transação intacta (0 linhas — teste).
4. [ ] `apply_reforja.py::_validar` consome `card_checks` (encoding/schema de lá) com **comportamento observável idêntico**: mesmos gates, mesma semântica dry-run/`--apply`/`--permitir-atomicidade`, mesmos formatos de mensagem `[ERRO]`/`[AVISO-ATOMICIDADE]`; testes existentes passam sem edição.
5. [ ] Fixtures sintéticas replicam os padrões estruturais dos 68 do incidente (pergunta `TEMA: qual a conduta/criterio correto?`; `titulo` embutido; contexto `"78% acertaram"`) — com texto clínico dummy; nenhum conteúdo real do banco entra no repo.
6. [ ] Craftsmanship: `pytest` verde; núcleo de `card_checks` importável sem tocar banco (testável puro — teste importa e roda sem fixture de db); pt-BR; nenhuma duplicação nova de regex entre `card_checks` e `apply_reforja`.

## Scope

- `tools/card_checks.py` — novo.
- `tools/apply_reforja.py` — `_validar` consome a biblioteca (RE_PROIBIDO removido daqui).
- `tools/insert_questao.py` — gate no caminho A.
- `tools/test_card_checks.py` — novo.

## Anti-scope

- NÃO plugar nos writers restantes (part-4) nem no batch de auditoria (part-5).
- NÃO promover avisos a erro fora do contrato: só `pergunta_template` e `resposta_embutida` bloqueiam escrita neste ciclo (warn-first para o resto; endurecimento é decisão posterior com base real).
- NÃO usar similaridade semântica/embedding — só relação estrutural de strings (normalização: casefold, sem acento, sem pontuação).
- NÃO ler conteúdo clínico do banco para fixtures.

## Technical Decisions

- **Biblioteca pura + duas superfícies** (write-gate e batch) — mesma predicado-fonte elimina a assimetria spec×detector (a spec bane, o detector não via). Threshold de `resposta_embutida` (6 tokens / 0.5) é ponto de partida explícito; a calibração da part-5 mede contra os 68 e ajusta ANTES de qualquer endurecimento.
- **Severidade por contrato, não por palpite**: template e resposta-embutida são os dois padrões com incidente real e proibição verbatim na spec → erro. O resto estreia aviso (padrão warn-first do repo).
- **`checar_distrator` é por-questão** (não por-card): o dado (`alternativa_marcada`) vive em `questoes_erros`; writer que tem a questão em mãos chama; batch (part-5) faz o join.
- **Import de `audit_card_atomicity`** mantém a fonte única existente de atomicidade (o precedente do próprio `apply_reforja`).

## Applicable Patterns

- `patterns/warn-first-check.md` — regra em módulo próprio testável; aviso não bloqueia; sem swallow de exceção do sensor.
- `patterns/error-insertion-pipeline.md` — o gate entra NO pipeline, não paralelo a ele.
- Convenções: pt-BR, mensagens completas de uma vez.

## Risks

- **R1**: falso-positivo de `resposta_embutida` em card legítimo cuja pergunta repete termo técnico da resposta → mitigação: threshold em tokens *consecutivos* normalizados (não tokens soltos); calibração part-5 mede precisão nos 1138 qualitativos antes de qualquer endurecimento adicional.
- **R2**: refactor de `apply_reforja` quebrar comportamento sutil → mitigação: DoD 4 exige testes existentes intactos sem edição; diff de mensagens conferido manualmente no dry-run.
