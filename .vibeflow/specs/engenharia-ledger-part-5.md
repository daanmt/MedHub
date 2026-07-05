# Spec: Engenharia Ledger — Part 5: Sinal e Curadoria (F5 + F7 + F2)

> Gerada via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/engenharia-ledger-f1-f13.md` (Onda 5)

## Objetivo

O agente passa a OFERECER o PREPARAR quando o cluster está frio (F5, gatilho sai do operador), o linter de cards ganha a heurística experimental de discriminação incompleta (F7), e a latência de tooling é medida com método reproduzível antes de qualquer conserto (F2 não reproduziu no scan — medir, não chutar).

## Contexto

Na s108 o PREPARAR só disparou quando o operador pediu; o sinal de frieza (score de dormência, stability média) já existe em `review_radar.py`/db, mas não chega ao fluxo DRENAR. Os cards 95/120 mostraram a classe "armadilha defende-se do competidor errado" — um linter sintático não pega o caso semântico completo, mas uma heurística barata com léxico curado pode dar WARN útil. A latência de shell reportada na s108 (timeout 120s em git/ls) não reproduziu no scan de 2026-07-05 (git <5s) — falta instrumentação, não correção.

## Definition of Done

1. [ ] `day_plan.py --review-plan` (da part-2) passa a incluir sinal de frieza por cluster (score de dormência via `review_radar`, com fallback silencioso se indisponível) — o dado que o DRENAR usa para ofertar aquecimento.
2. [ ] Contrato de `/revisar`: ao abrir um cluster no DRENAR com sinal frio (limiar documentado na cláusula), o agente OFERECE o PREPARAR ("cluster X está frio — aqueço antes?") sem esperar pedido; a fronteira dura permanece (PREPARAR não toca FSRS; oferta ≠ execução automática).
3. [ ] `tools/audit_flashcard_quality.py` ganha heurística F7 com léxico opcional em `tools/data/competidores_categorias.json` (pares de categorias opostas, curado pelo agente-player): armadilha que nomeia só competidor de categoria oposta à da resposta → WARN (nunca BLOCK); sem léxico ou sem match → silêncio (degradação graciosa). Caso de calibração: card 95 dispara o WARN com o léxico exemplo.
4. [ ] Latência medida e registrada: cronometragem reproduzível (comando + N execuções + mediana) de `auto_check.py --staged` e `day_plan.py`, apendada ao ledger `AUDITORIA_MEDHUB.md` como verificação do F2 (achado atualizado, não removido — ledger é vivo e append-only por seção).
5. [ ] Craftsmanship: WARN não rebaixa veredito (política s106/107); paridade `sync_skills --check` PASS após edição de contrato; zero violações dos Don'ts; heurística F7 nasce com **gate anti-decorativo documentado** (se em 3 execuções reais não sinalizar nada acionável, remover — registrado na própria seção do ledger).

## Escopo

- `tools/day_plan.py` — score de frieza por cluster no `--review-plan`.
- `.claude/commands/revisar.md` + `core/contracts/revisao-calibrada-contract.md` — cláusula do PREPARAR proativo (+ espelho via sync_skills).
- `tools/audit_flashcard_quality.py` — heurística F7 (WARN).
- `tools/data/competidores_categorias.json` — léxico exemplo mínimo (1-2 pares para calibração; curadoria contínua é do agente-player).
- `AUDITORIA_MEDHUB.md` — números de latência F2 (append na seção do achado).

Budget: 6 arquivos (teto).

## Anti-escopo

- PREPARAR **não** dispara automaticamente — oferta conversacional; a decisão é do operador.
- Léxico F7 não vira dependência dura — ausência = check silencioso; a curadoria do léxico é conteúdo (agente-player), não engenharia.
- Nenhum conserto de latência nesta onda — só medição (conserto só se os números reproduzirem o problema, e aí vira achado novo no ledger).
- Não reforjar os cards 95/120 (curadoria de domínio, fica com o Opus via /curar-cards + gate de evidência).
- Nenhum campo novo no schema de flashcards (altura/tipo formal aguarda sinal recorrente).

## Decisões Técnicas

1. **Sinal de frieza reusa `review_radar.coletar()`** (mesmo caminho que `montar_sinais` do day_plan já usa) — nenhuma fonte nova de verdade; try/except com fallback silencioso preserva o day_plan read-only e resiliente.
2. **Limiar de frieza na cláusula do contrato, não hardcoded no CLI**: o CLI expõe o score cru; o julgamento (frio/quente) é do agente com limiar documentado — mantém o CLI estável quando a política mudar.
3. **Heurística F7 com léxico externo**: a única forma barata de aproximar o sinal semântico (categoria oposta) sem LLM no linter; nasce experimental com gate anti-decorativo explícito — padrão que evita linter decorativo acumulando WARN ignorado.
4. **F2 como instrumentação**: mediana de 3+ execuções cronometradas, método colado no ledger — se reproduzir, o achado F2 reabre com dados; se não, fecha com evidência.

## Patterns Aplicáveis

- `agent-workflow-protocol.md` — edições de contrato seguem o rito de paridade e fechamento.
- `db-access-layer.md` — sinal de frieza via módulos existentes, sem SQL novo.

## Riscos

- **Oferta proativa virar ruído** (ofertar em todo cluster) → mitigação: limiar conservador na cláusula (ex.: score_dorm >= 25) + o operador pode recusar de uma vez ("hoje sem PREPARAR") e a sessão respeita.
- **Léxico F7 enviesar a curadoria** (WARN em card correto) → mitigação: WARN nunca bloqueia; gate anti-decorativo mata a heurística se não render em 3 execuções.
- **Medição F2 não-representativa** (máquina ociosa vs sessão real) → mitigação: registrar condições da medição no ledger junto dos números; comparável com a próxima sessão de uso real.

## Dependencies

- `.vibeflow/specs/engenharia-ledger-part-2.md` (o `--review-plan` que recebe o sinal de frieza).
- `.vibeflow/specs/engenharia-ledger-part-3.md` (o texto do contrato já reestruturado — a cláusula F5 entra no lugar certo).
