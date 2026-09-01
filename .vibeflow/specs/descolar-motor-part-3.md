# Spec: Descolar part-3 — o input do boot fica verdadeiro (F47 · F45 · F46-path)

> Gerado via /vibeflow:gen-spec em 2026-09-01, do PRD `descolar-motor-determinismo.md`.
> F47+F46 são bugs pequenos e VIVOS que corrompem o input de toda sessão (handoff §5).

## Objective

O que abre a sessão passa a ser verdade: a calibragem respeita a precedência de fonte declarada
no contrato, o ranking de fraquezas ranqueia por FRAQUEZA (não recência) com vocabulário validado,
e a camada de memória para de criar bancos-fantasma.

## Context

F47: `day_plan.py:576-579` — QUALQUER nota persistida vira soberana; `dificuldade_fonte`/`_at`
nunca decidem (Cláusulas 2/7 do `revisao-calibrada-contract` sem implementação); 12/21 temas
calibrados afetados; a mensagem "Você marcou 3..." atribui ao usuário nota que ele não deu.
F45: só 60/349 WeakAreas (17%) têm `error_count>0`; 109 duplicatas (31%, pior par 7×);
`inspect.py:158` desempata por `last_updated` → o ranking do boot mostra o mais RECENTE.
F46: `manager.py:29` `Path("ipub.db")` relativo ao cwd → 2 bancos-fantasma de 0 bytes
(`tools/ipub.db`, `data/ipub.db`) provam runs com cwd errado.

## Definition of Done

1. [ ] Precedência de fonte implementada na calibragem: `input_usuario > pergunta > inferencia`
       (`dificuldade_fonte` DECIDE; `dificuldade_at` com frescor 7d → re-inferência marca a fonte);
       teste de precedência com os 3 níveis + o caso frescor.
2. [ ] A mensagem de calibragem só diz "você marcou" quando `dificuldade_fonte == input_usuario`;
       demais fontes têm redação própria ("inferido de X").
3. [ ] `WeakArea.area` validado contra o vocabulário real da taxonomia (fora do vocabulário →
       normaliza quando mapeável, senão rejeita com WARN no log lido pelo painel part-1); upsert
       por par `(area, tema)` — consolidação NUNCA cria UUID novo para par existente; teste.
4. [ ] `inspect.load_context` ranqueia por `error_count` desc (recência só desempata); teste com
       fixture (par fraco antigo vence par forte recente).
5. [ ] `_IPUB_PATH` resolvido por `__file__` (convenção `db-access-layer`); leitores abrem
       `mode=ro`; os 2 bancos-fantasma de 0 bytes DELETADOS (verificar `st_size == 0` antes).
6. [ ] Suite verde; teste dos itens acima registrado no pytest.ini; craftsmanship: mensagens em
       pt-BR, ASCII nos logs.

## Scope

`tools/day_plan.py` · `app/memory/manager.py` · `app/memory/inspect.py` · `app/memory/schemas.py`
· testes (novo `tools/test_boot_verdadeiro.py` ou extensão dos existentes) (≤6).

## Anti-scope

- Reprocessar/limpar as 109 duplicatas históricas do `medhub_memory.db` (dado; operador no loop —
  o upsert estanca a produção de novas; a limpeza é operação separada).
- Mudar a taxonomia clínica em si (fronteira dura).
- Tocar `ipub.db` além de deletar os 2 decoys 0-byte.

## Technical Decisions

- Vocabulário da validação = derivado da taxonomia REAL no `ipub.db` em runtime (não lista
  hardcoded que drifta) com fallback conservador (sem acesso ao db → aceita e marca).
- Duplicatas históricas ficam; o ranking com upsert novo já as despriorizará naturalmente.

## Applicable Patterns

- `db-access-layer.md` (path por `__file__`, mode=ro) · `agent-workflow-protocol.md` (o boot é o
  cliente disto).

## Risks

- Endurecer `area` pode rejeitar sinônimo clínico legítimo → normalização-quando-mapeável +
  WARN-não-drop (recall-safe: fraqueza mal-rotulada > fraqueza perdida).

## References

- `core/contracts/revisao-calibrada-contract.md` Cláusulas 2/7 — a lei que o código passa a cumprir.
- `ai-eng/HANDOFF-MEDHUB-COLA.md` §4 F45/F46/F47.
