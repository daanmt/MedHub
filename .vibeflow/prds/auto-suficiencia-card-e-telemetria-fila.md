# PRD: Auto-suficiencia de flashcard + telemetria de fila FSRS

> Generated via /vibeflow:discover on 2026-07-15

## Problem

Auditoria do corpus de flashcards (sessao 121, 2026-07-15), disparada pelo feedback do usuario ("os cards ficaram criptograficos"), revelou dois problemas de naturezas diferentes.

**(1) Cards nao auto-suficientes.** Dos 596 cards ativos, ~6,2% (37 cards) nao sao respondiveis a frio -- so foram acertados por recencia (estudados no dia). Eles referenciam algo que nao esta no card. Tres anti-padroes:
- **opcao-anaforico (17):** cunhados de questao de enunciado negativo ("por que a alternativa X e falsa"); referenciam um conjunto de opcoes que nao esta no card.
- **deitico (15):** "neste caso / deste paciente / acima / mencionado" -- apontam pra um dado ausente do card.
- **%-fake (2):** percentuais fabricados na armadilha ("61% caem").

O linter atual (`tools/audit_flashcard_quality.py`) reporta 99,6% OK porque e **lexico/estrutural** -- e cego aos tres padroes (todos semanticos/anaforicos). Card ruim passa em silencio ate o usuario tropecar nele na revisao.

**(2) Telemetria de fila enganosa.** `insert_questao.py` grava `due = datetime.now()` na criacao, entao os 630 cards novos nascem "vencidos". O `day_plan`/HANDOFF reporta "425 novos (backlog)", empacotando num rotulo so um **pool de nunca-introduzidos** (~425) com **divida atrasada real** (~22). A contagem "nao faz sentido" pro usuario.

## Target Audience

**Primario:** o agente (autor de cards + scrum master) -- precisa do linter pra pegar card nao-auto-suficiente ANTES de entrar na fila, e de telemetria honesta pra planejar o dia. **Secundario:** o usuario (estudando) -- consome cards que se sustentam sozinhos e um plano-do-dia cujas contagens sao confiaveis.

## Proposed Solution

Duas entregas de engenharia independentes:

**Feature A -- Check de auto-suficiencia.** Integrado ao `auto_check.py`, **warn-first** (padrao `warn-first-check`), num modulo proprio testavel. Detecta os 3 anti-padroes nos cards ativos; emite WARN por achado + worklist consolidada. Essa worklist alimenta a reforja de conteudo (fora de escopo). E a peca-chave: previne a recaida E gera a lista dos 37 automaticamente.

**Feature B -- Higiene de telemetria da fila.** `day_plan --handoff-block` (e o cabecalho do plano) passam a distinguir `pool` (nunca-introduzido, state=0) de `divida` (review atrasada, state>=2 com due<now), e explicitam o teto de introducao/dia. **Sem mudanca no mecanismo `due=now()`.**

## Success Criteria

- `python tools/auto_check.py --all` imprime um bloco WARN novo listando os cards nao-auto-suficientes (>= os 37 conhecidos), agrupados/contados por padrao; **exit code inalterado** (WARN nao bloqueia).
- O check mora em modulo proprio com testes unitarios (fixtures de cada um dos 3 padroes + um card limpo que NAO pode disparar).
- `python tools/day_plan.py --handoff-block` reporta `pool` e `divida` como numeros distintos (ex.: "pool 425 / divida 22"), nunca mais um "backlog" unico.
- O usuario le o plano-do-dia e os dois numeros batem com a realidade do db (pool = ativos state=0; divida = ativos state>=2 com due<now).

## Scope v0

- Modulo novo `tools/card_self_sufficiency.py` com `run_checks()` puro devolvendo achados (id, padrao, area, tema).
- Bloco de integracao no `main()` do `auto_check.py`: warn-first, instrumentado no ledger (`_ledger_record`), com janela de relevancia (roda sempre no `--all`; no `--changed`/`--staged` so quando flashcards mudaram).
- Testes unitarios (`tools/test_*.py`) cobrindo os 3 padroes + negativos.
- `day_plan.py`: separar `pool` de `divida` no `--handoff-block` e no cabecalho; rotular o teto de introducao.
- Atualizar o contrato/pattern doc se um invariante novo for codificado.

## Anti-scope

- **A reforja de conteudo dos 37 cards** -- feita a parte, como curadoria (`/curar-cards` + `estilo-flashcard`); o linter so produz a worklist.
- **Re-arquitetar o due-at-creation** (`due=now()` em `insert_questao`) ou a logica de bucketing do `fsrs_queue`.
- Tocar nos 226 aposentados (`needs_qualitative>=2`) -- ja fora da fila.
- Qualquer mudanca no Streamlit/UI (`app/pages`).
- Julgamento semantico via LLM do "criptografico" -- v0 e regex/heuristica (proxies lexicais dos padroes anaforicos), coerente com warn-first (barato, deterministico, testavel). Grading por LLM e um tier futuro possivel.

## Technical Context

- **Padrao a seguir:** `warn-first-check.md` -- regra em modulo proprio testavel, orquestrada pelo `auto_check`, nasce WARN, instrumentada no ledger, parsing defensivo (sem dados -> silencio; malformado -> WARN, nunca crash).
- **Linter existente:** `tools/audit_flashcard_quality.py` (sinais lexicais/estruturais) -- o check novo **complementa** (auto-suficiencia semantica), nao substitui.
- **Schema de card (conventions, Flashcard v5.0):** `frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`; `quality_source`, `needs_qualitative` (0/1/2). **Ativo = `needs_qualitative<2`**.
- **Assinaturas dos anti-padroes** (do audit que produziu os 37):
  - opcao-anaforico: front casa `/(alternativa|op[cç][aã]o|afirma[cç][aã]o (falsa|incorreta|verdadeira)|est[aá] errad|est[aá] corret|enunciado negativo|assertiva|\([A-E]\))/i`
  - deitico: front casa `/(neste caso|deste paciente|nessa situa|acima|a seguir|mencionad|citad)/i`
  - %-fake: verso casa `/\d{1,3}\s*%\s*(caem|marcam|erram|escolhem|assinalam|confundem|optam)/i`
- **Contagens (2026-07-15):** 822 fsrs_cards; 226 aposentados; 596 ativos; state=0 630 (todos due<now); state=2 189 (22 atrasados); state=3 3. Pool (ativo state=0) ~425; divida ~22.
- **due gravado em** `insert_questao.py` (~linha 222): `INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, datetime.now())`.
- **Acesso a db:** tools sao CLIs standalone, abrem propria conexao sqlite3 (conventions, secao CLI); `auto_check` orquestra.

## Open Questions

- Feature A e B sao independentes; o `gen-spec` provavelmente racha em 2 specs. Confirmar o split na hora do gen-spec.
- Se o check de auto-suficiencia deve endurecer pra BLOCK depois que a base zerar (warn-first: "so endurece quando a base zerar E o operador decide") -- adiado; nasce WARN.
- Casa do check novo: modulo novo vs estender `audit_flashcard_quality.py` -- decidir no spec (inclinacao: modulo novo, por isolamento/testabilidade).
