---
type: workflow
layer: agents
status: canonical
description: Curadoria do backlog de flashcards — saneia taxonomia, tria defeitos semânticos e reforja cards no elo do erro
---

# Workflow: Curadoria de Flashcards

## Contexto

O pipeline de geração confia 100% no agente-autor: o que entra via `insert_questao.py --cards-file` é gravado como `qualitative` **sem validação de qualidade**. Safras antigas (ex.: mar/2026) acumularam cards com defeitos **semânticos** — *fato-genérico, missing-the-point, contexto criptográfico, clone/duplicata* — que o linter sintático **não detecta** (só o olho humano / um agente-auditor). Este workflow é o processo repetível para auditar todo o backlog e devolver cada card à sua função: **pavimentar o elo de raciocínio que rompeu no erro, não testar um fato sobre o tema.**

Quando rodar: ao detectar uma safra fraca na revisão card-a-card, periodicamente (a cada N centenas de cards novos), ou após um período de geração apressada.

## Pré-requisitos

- Ler `.claude/commands/estilo-flashcard.md` — a régua dos **5 princípios** (o card ancora no erro metacognitivo). É o critério de toda a triagem e cunhagem.
- Ler `core/contracts/reconcile-contract.md` se a taxonomia estiver suspeita.
- **Backup obrigatório** antes de qualquer escrita: `python tools/backup_db.py`. Todo CLI destrutivo roda **`--dry-run` primeiro**.

## Passos

### 0. Preflight
Seguir o **Boot Sequence** do `AGENTE.md`.

### 1. Sanear a taxonomia (pré-requisito da triagem)
Cards mal-agrupados quebram a detecção de clones. Antes de auditar cards, limpar `taxonomia_cronograma`:
- `dedup_taxonomia.py` resolve duplicatas `(area, tema)` **exatas**.
- `normalize_taxonomia.py` resolve o que escapa: **encoding/acento**, **áreas fora de `AREAS_VALIDAS`** (dissolver na especialidade), **duplicatas conceituais** (mesmo tema, nomes diferentes), `[bulk]`/`Geral` vazios. Operações declarativas no topo do script; simula colisão e roda `--dry-run` por default.
- Saída esperada: `dup=0`, `órfãos=0`, todas as áreas ∈ `AREAS_VALIDAS` (`tools/registrar_sessao_bulk.py`).

### 2. Diagnóstico de qualidade
- `python tools/audit_flashcard_quality.py` — sinais **sintáticos** (alt-letter, regra vazia, órfão sem âncora). É o piso, não o teto.
- `python tools/detect_clones.py` — near-duplicates por tema (similaridade). Pega o defeito nº 1 (clone).
- ⚠️ **O linter é cego ao semântico.** Um "604/606 OK" não significa qualidade — a triagem do passo 3 é que enxerga fato-genérico / missing-the-point / cripto.

### 3. Triagem multi-agente (julgamento semântico)
Exportar o substrato e fanout por tema:
1. **Export:** para cada card ativo, `card + erro_origem` (JOIN `questoes_erros`: `tipo_erro`, `o_que_faltou`, `habilidades_sequenciais`, `alternativa_correta`/`marcada`, `armadilha_prova`), agrupado por tema em **lotes balanceados** (temas inteiros, ~20 cards/lote — clones só se enxergam dentro do tema).
2. **Workflow de triagem:** 1 agente/lote. Cada um classifica cada card contra os 5 princípios → veredito `ok | reforjar | fundir | aposentar` + `defeitos[]` + (reforjar) o **ângulo do elo** a reancorar + (fundir) o `fundir_em`.
3. **Resolver o plano:** tratar **auto-referência** de fusão (`fundir_em == self` = sobrevivente) e **cadeias**; validar cobertura 100% e ausência de sobrevivente-que-some.

### 4. Executar a curadoria (backup + dry-run sempre)
- **Aposentar/fundir:** `recurate_cards.py --from <json>` com `{card_id, aposentar:true}` para os perdedores (o sobrevivente absorve).
- **Reforjar:** **workflow de cunhagem** (1 agente/lote) re-cunha cada card ancorado no ângulo + `erro_origem` + RAG do resumo (`mcp__obsidian-notes-rag__search_notes`), seguindo os 5 princípios. Aplicar via `recurate_cards.py` (`{card_id, contexto, pergunta, resposta, regra, armadilha, tipo}`) — preserva `card_id` e estado FSRS, incrementa `card_version`.
- **Atomização:** quando um reforjar gera um 2º conceito do mesmo erro, `insert_card_extra.py --from <json> --apply` cria o card herdando o `questao_id`/`tema_id` de origem.

### 5. Validar e fechar
- Reauditar (`audit_flashcard_quality.py` + `detect_clones.py`); confirmar contagem e ausência de regressão sintática.
- Seguir o **Protocolo de Fechamento** do `AGENTE.md` (HANDOFF + `history/` + commit). `ipub.db` é local-only — commitar só os CLIs/docs.

## Regras
- **Reforjar > aposentar.** Card com `erro_origem` rico mas mal-cunhado é reforjável — re-cunhar ancorando no elo. Aposentar só duplicata, erro pontual de leitura sem conteúdo, ou redundância total.
- **O erro define o card.** Nunca re-cunhar como "pergunta de fato sobre o tema" — ancorar na distinção que quebrou (`tipo_erro` + `o_que_faltou`).
- **Andaimes (`tipo` base/mecanismo/nuance) são órfãos legítimos** (`questao_id` NULL): não tratar como sem-ancoragem.
- **Backup + dry-run antes de toda escrita** no `ipub.db`. Migrações one-shot de taxonomia movem para `tools/_archive/migrations/` após aplicadas.
- O linter **complementa** o olho humano/agente; nunca o substitui.
