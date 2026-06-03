# PRD: Onda B — Flashcards Ancorados no Erro Metacognitivo

> Gerado via /vibeflow:discover em 2026-06-03 (régua fechada na sessão 074)
> ROADMAP.md Linha Evolutiva 8 (MedHub Agent-First)

## Problem

Os flashcards atuais foram cunhados pela geração heurística (`tools/regenerate_cards.py`), que achatou o ouro metacognitivo da tabela `questoes_erros` em perguntas genéricas. Validado na sessão 074 com o erro #211: um card colou `habilidades_sequenciais` cru com um "?" no fim (vazando a resposta) e o outro usou o template "Qual o distrator típico do examinador em...?". O usuário lê, concorda e não reforça nada. Isso viola a tese central do MedHub — ser o "segundo cérebro agêntico" da preparação, cujo valor está em reforçar exatamente o ponto onde o raciocínio rompeu, não em decorar fatos genéricos.

## Target Audience

Usuário único (candidato a residência).

## Proposed Solution

O **agente** gera os flashcards (não o código), seguindo a régua de 5 princípios validada na sessão 074, e persiste via `insert_questao.py`. A geração heurística é aposentada. Dois fluxos: **go-forward** (novo erro → cards pela régua dentro de `/analisar-questao`) e **backfill** (refazer os cards legados ruins, flagged `needs_qualitative=1`).

**Régua de 5 princípios (caso-âncora: erro #211, Úlceras Genitais):**
1. Card = conteúdo clínico **atômico** (1 conceito/card; decompor em vez de combinar — ex.: "agentes de úlcera" e "agentes de corrimento" como cards separados), não meta-raciocínio.
2. O **erro define o alvo**: `tipo_erro` + `o_que_faltou` apontam *qual* conteúdo drilar e *qual distinção/sobreposição* tornar central; o card é recall limpo.
3. Pergunta direta — **nunca vaza a resposta** nem cola `habilidades_sequenciais` cru.
4. **Regra-mestre = a distinção/sobreposição** que previne a confusão (ex.: Chlamydia L1-L3 = úlcera vs D-K = corrimento).
5. **Armadilha = o distrator específico** que pegou o usuário (ex.: Trichomonas como falso agente de úlcera), ancorada no resumo correspondente.

## Success Criteria

- Para um erro dado, os cards gerados satisfazem os 5 princípios (atômico, recall de conteúdo, sem vazar resposta, regra-mestre = distinção, armadilha = distrator específico, ancorado em resumo).
- `/analisar-questao` passa a produzir cards por essa régua (go-forward).
- `tools/regenerate_cards.py` + `regenerate_cards_llm.py` aposentados.
- Cards legados flagged podem ser regenerados pelo agente preservando (ou conscientemente reiniciando) o estado FSRS.

## Scope v0

- **Contrato de autoria de card** — skill canônica (análoga a `estilo-resumo.md`): os 5 princípios + exemplos bom/ruim (caso 211).
- **Go-forward**: amarrar o contrato ao fluxo `/analisar-questao`.
- **Backfill**: caminho para regenerar cards de erros existentes (listar erro + cards atuais para o agente reprocessar; persistir os novos cards).
- **Aposentar** `regenerate_cards.py` + `regenerate_cards_llm.py`.

## Anti-scope

- FSRS fiel (part-2 da Onda A).
- Google Sheets MCP (Onda C).
- Streamlit / dashboard (Onda D).
- Mudança de schema da tabela `flashcards`.
- Geração automática sem o agente no loop (é justamente a heurística que estamos matando).
- Reescrever resumos (apenas consumi-los como âncora via RAG).

## Technical Context

- `questoes_erros` guarda o substrato metacognitivo: `tipo_erro`, `habilidades_sequenciais`, `o_que_faltou`, `alternativa_correta`, `alternativa_marcada`, `explicacao_correta`, `armadilha_prova`.
- `insert_questao.py` já aceita `--frente_contexto/--frente_pergunta/--verso_resposta/--verso_regra_mestre/--verso_armadilha` e marca `quality_source='qualitative'` quando os campos estruturados são passados.
- Schema v5: `flashcards` (1:1 com `fsrs_cards` via `id`→`card_id`), `tipo` ∈ {elo_quebrado, armadilha}, `needs_qualitative` ∈ {0,1,2}.
- RAG local (`app/engine/rag.py`) ancora o card no resumo correspondente (decisão da sessão 074: RAG local vence o obsidian MCP).
- A skill `/revisar` + `tools/fsrs_queue.py` (Onda A part-1) servem os cards regenerados sem qualquer mudança.
- Convenções: `import sqlite3` só em `db.py`/CLIs standalone; assinatura de CLI em uma skill (§7.2); `ipub.db` local-only.

## Open Questions

- **Backfill — UPDATE in-place vs aposentar+recriar?** UPDATE preserva `card_id` (logo o estado FSRS em `fsrs_cards`/`fsrs_revlog`); aposentar+recriar (`needs_qualitative=2` no velho, novo card) zera o histórico FSRS daquele card. Inclinação: UPDATE in-place via caminho dedicado, preservando `card_id`.
- **Granularidade — quantos cards por erro?** A régua pede atômico; varia por erro (1 a 3). Definir um teto.
- **O contrato vira skill nova (`estilo-flashcard.md`) ou seção em `analisar-questao.md`?** Inclinação: skill própria (referência atômica, contrato §7.2).
- **Volume do backfill** — ~200+ erros; processar tudo de uma vez ou em lotes priorizados pelas áreas fracas?
