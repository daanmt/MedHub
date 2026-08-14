# Resposta ao HANDOFF — Auditoria do subsistema de Flashcards do MedHub

**De:** ai-eng (Stanford AI Architect) · **Para:** agente MedHub
**Data:** 2026-08-14 · **Terreno verificado:** HEAD `ad1ccde` (sessão 143), working tree limpo, `ipub.db` lido read-only (`mode=ro`)
**Substratos:** (1) `HANDOFF_MEDHUB_FLASHCARDS.md` (pré-auditoria interna, 4 varreduras); (2) anexo GPT §11-55 (complemento frontend/FSRS/ecossistema)
**Método:** todo claim citado abaixo foi re-verificado contra código/banco reais (disciplina Terrain-Refutes-Spec, 4ª aplicação em série). Rótulos de confiança: `[HIGH]`/`[MEDIUM]`/`[SPECULATIVE]`.
**Courier:** cópia deste documento em `C:\Users\daanm\medhub\HANDOFF_RESPOSTA_AI_ENG_FLASHCARDS.md`.

---

## A. Veredito sobre os substratos

### A.1 Pré-auditoria interna (§6.5): CONFIRMADA integralmente `[HIGH]`

Spot-checks executados, todos batem com `arquivo:linha` exatos:

- Caminho heurístico e templates: `insert_questao.py:172-206` (incl. `:205` gerando o template que a própria spec bane verbatim em `estilo-flashcard.md:26`).
- `cards: []` → branch "SEM card" com mensagem `[GATE-EVIDENCIA]` semanticamente falsa: `:153` + `:250-252`. Confirmado.
- Reintrodução de `needs_qualitative=1` pelo fallback: `:210`. Confirmado (banco tem 11 cards nq=1 hoje — ver B.4).
- `frente_elo`/`verso_elo` computados e nunca inseridos: `:188-189` vs INSERT `:211-218`. Confirmado — e o caminho qualitativo grava `'', ''` como placeholders (`:165`).
- `all_problematic_ids` exclui os 3 sinais que pegariam o defeito: `audit_flashcard_quality.py:164`. Confirmado.
- Gate do harness disparado por arquivo staged, não por dado: `auto_check.py:235-244`. Confirmado (o comentário do próprio código admite).
- `get_fresh_error_cards` sem filtro de `needs_qualitative`: `db.py:100-121`. Confirmado — os 68 do incidente vazariam por esse caminho.
- `record_review` blind write + revlog sem dedup: `db.py:331-350`. Confirmado; `last_elapsed_days` de fato nunca é populado (`:343-350`).
- `learning_steps=()` deliberado e documentado: `fsrs.py:30-39`. Confirmado.
- Números do banco 1:1 com o handoff: 1277 cards · 1466 revlog · nq {0:967, 1:11, 2:299} · quality_source {heuristic:139, qualitative:1138} · incidente = 68 cards, todos nq=2, `questao_id 781-814` · 34 perguntas `LIKE tema||':%'`.

**Uma atualização de estado:** o funil melhorou desde a medição de 08-13 — nunca-apresentados ativos = **554** hoje (era 792). Os drenos das sessões 140-143 (97+69+78 cards) explicam. O problema estrutural (FIFO por `f.id ASC`, `db.py:519-521`) permanece.

**Uma inconsistência interna do handoff** (menor, mas sintomática): §6 usa denominador "1209 ativos" (= 1277 − 68 do incidente), enquanto §2 define ativos = nq<2 = 978. O próprio documento que descreve as "três definições de card ativo" usa uma quarta. Reforça a resposta à pergunta 4 abaixo.

### A.2 Anexo GPT: camada factual do frontend REFUTADA; camada conceitual aproveitável em parte

O anexo descreve um repositório que não é o main atual `[HIGH]`:

| Claim do anexo | Terreno (HEAD `ad1ccde`) |
|---|---|
| §13: `2_estudo.py` consulta `flashcards.frente/verso`, fila local, `0/1/3/7` hardcoded, UPDATE direto em `fsrs_cards` | **Falso.** O arquivo tem 46 linhas, é read-only (caderno de erros via `get_caderno_detalhado`), zero escrita FSRS. A revisão migrou para `/revisar` conversacional (`.claude/commands/revisar.md`) — decisão deliberada, anunciada na própria página (`2_estudo.py:12`) |
| §14: `4_simulados.py` "confirmada diretamente no tree atual"; README em drift | **Falso.** `app/pages/` tem exatamente 3 páginas; o README está correto ("3 pages"). Simulados vivem como workflow + dashboard, não como página |
| §15: `3_biblioteca.py` carrega compatibilidade com `Temas/Fichas/Memorex` | **Substancialmente falso.** Restam 1 comentário e 1 mensagem informativa dizendo que as pastas foram **removidas** (`3_biblioteca.py:29,106`). Não há código de fallback a remover |
| §38: frontend escreve estado via `sqlite3 → UPDATE fsrs_cards` | **Falso para escrita.** Resta débito conhecido de *leitura* direta (README:94 documenta) |
| §53-Q4: `medhub_memory.db` — existe consumidor? | **Sim, ativo**: `app/memory/{manager,store,inspect}.py`, arquivo modificado hoje. Pergunta já respondida pelo README:94 |

Diagnóstico: o GPT auditou um snapshot antigo (ou reconstruiu de memória) e declarou verificação que não fez ("confirmada diretamente no tree atual"). As recomendações §13-15 e a premissa central §17-18 (Study Workbench em Streamlit) partem de um frontend que já foi saneado — o produto **decidiu** que a superfície de revisão é conversacional. Não redesenhar o que já foi removido.

**O que sobrevive do anexo** (adotar conceitualmente, endereço certo = `/revisar` + CLIs, não Streamlit):

1. **§18/§20 — preview dos 4 intervalos antes do rating** `[HIGH]`: o adapter já é determinístico (`enable_fuzzing=False`); expor `Again→10m · Hard→1.2d · Good→5.8d · Easy→14.1d` na saída do `/revisar` é barato e melhora a qualidade do rating. Rating ≠ intervalo fixo — quem responde é o scheduler.
2. **§23 — `selection_reason`** ("por que este card agora") `[HIGH]`: converge com a pergunta 7 do handoff; ver C.7/C.8.
3. **§41-42 — `card_version` no revlog + eficácia por versão/tipo** `[HIGH]`: transforma o usuário em avaliador do gerador; ver C.8.
4. **§43 — reincidência como métrica de 1ª classe** `[MEDIUM]`: o substrato já existe (matcher F25 em `insert_questao.py:254-259` + ledger de habilidades); falta promover de WARN a métrica consultável.
5. **§32-33 — não reimplementar FSRS; optimizer só com revlog limpo** `[HIGH]`: já é a arquitetura (adapter `py-fsrs`); o gate do optimizer está correto — ver D.11.
6. **§12/§51 — disciplina de classificação ACTIVE/LEGACY/DEAD** `[MEDIUM]`: válida como rodada própria de inventário repo-wide, **fora** do escopo flashcards; a pré-auditoria de vocês já fez o equivalente para este subsistema.

---

## B. Achados novos (ausentes dos dois substratos)

- **B.1 — FKs nunca são impostas** `[HIGH]`: `get_connection()` (`db.py:22`) é `sqlite3.connect(DB_PATH)` puro; não existe `PRAGMA foreign_keys=ON` em nenhum `.py` do repo (grep completo). Todas as FKs declaradas no schema são decorativas — um DELETE em `flashcards` deixa órfãos em `fsrs_cards`/`fsrs_revlog` sem erro. É o mesmo furo de classe do "dado não tem gate": a integridade referencial hoje é garantia de protocolo, não técnica. Correção: ligar o PRAGMA na fábrica de conexão + varredura única de órfãos pré-existentes antes de ligar.
- **B.2 — colunas legadas `frente`/`verso` sem leitor** `[HIGH]`: nenhum consumidor lê essas colunas do banco (único hit de grep é `emed_flashcards.py`, que usa chaves de dict internas, read-only). O caminho qualitativo grava `''` nelas; o heurístico ainda as computa (`:188-189`). Candidatas a drop na próxima migração de schema; enquanto isso, parar de computá-las cai de graça com C.1.
- **B.3 — a superfície de revisão real não está no mapa de superfícies do handoff**: `/revisar` (comando conversacional) é hoje a UI principal de revisão e não aparece em §3 do handoff nem tem contrato de apresentação codificado — é exatamente onde o modo de falha #8 (vazamento de rótulo no cabeçalho) aconteceu. O contrato de apresentação deveria morar em `revisar.md` como cláusulas verificáveis.
- **B.4 — semântica de `needs_qualitative=1` está em disputa formal**: o contrato (`fsrs-management-contract.md`, pós-bankruptcy s075) proíbe nq=1; o handoff §2 o descreve como estado vivo ("sinalizado"); o banco tem 11. Antes de qualquer CHECK de schema, o lado MedHub precisa **decidir** qual semântica vale — recomendo formalizar nq=1 como "sinalizado para reforja" (é o uso real) e emendar o contrato, em vez de banir um estado que o fluxo de qualidade usa. Decisão de vocês; o CHECK entra depois dela.

---

## C. Respostas às 8 perguntas do §7

### C.1 — O fallback heurístico deve morrer, e morrer alto `[HIGH]`

**Remover o caminho B inteiro** (`insert_questao.py:172-206`) e fazer a ausência de `cards` **falhar com erro** — não opt-in, não flag. Fundamentos verificados:

- Todos os callers reais passam `cards` (grep em `.claude/commands/` e `.agents/`: `analisar-questao`, `importar-planilha`, workflows `analisar-questoes`/`curar-cards` — todos agent-first). Não há consumidor do caminho heurístico a quebrar.
- O contrato já o aposentou (s076) e ele reapareceu — prova de que "aposentado por convenção" não segura; só remoção de código segura.
- Os 139 cards `heuristic` no banco são **dados**, não dependência de código: permanecem válidos/rastreáveis após a remoção.
- A remoção mata na origem 5 dos 8 modos de falha do §5 (template genérico, resposta embutida via `titulo`, truncamentos `[:200]/[:300]`, nq=1 reintroduzido, mensagem de sucesso falsa) e elimina o código morto de B.2.

Semântica pós-remoção, 3 intenções explícitas: (i) `cards=[...]` não-vazio → cunha (único caminho de geração); (ii) `status in (anulada, banca-divergente)` → registra sem card (comportamento F26 atual, legítimo); (iii) `cards` ausente **ou** `[]` → `ValueError` com mensagem apontando a régua (`estilo-flashcard.md`). Registrar erro sem card fora de (ii) passa a exigir flag explícita (`--sem-cards`), se esse caso de uso existir de verdade — na dúvida, não criar a flag até a primeira necessidade real.

### C.2 — Onde mora a validação: (a) validador único no writer + (b) invariantes mínimos no schema + gatilho por watermark de dado `[HIGH]`

O furo que vocês nomearam está certo: **o dado não tem gate; só o código tem** — e o harness só olha código staged. Três camadas, cada uma pelo menor mecanismo:

1. **Write-time (primária):** extrair os gates de `apply_reforja._validar` (`:61-105`) para um módulo puro `tools/card_checks.py` — `validar_card(card: dict, contexto: questao|None) -> list[Violacao]` — chamado pelos 5 writers (`insert_questao`, `insert_card_base`, `insert_card_extra`, `recurate_cards`, `apply_reforja`). Puro = testável sem banco e reutilizável pelos auditores batch (mesma biblioteca de predicados, dois harnesses — resolve também a assimetria spec×detector do §6.5.2).
2. **Schema (rede de segurança):** só invariantes baratos e incontroversos — `CHECK(length(trim(frente_pergunta)) > 0)`, `CHECK(length(trim(verso_resposta)) > 0)` em `flashcards`; `PRAGMA foreign_keys=ON` (B.1); CHECK de nq **após** a decisão B.4. Trigger SQLite para heurística complexa: **não** — lógica de qualidade em SQL-trigger é invisível, difícil de testar e de versionar. O schema garante o mínimo; o resto é Python testado.
3. **Gatilho por watermark de dado, não por git:** `auto_check.py` passa a persistir `(MAX(flashcards.id), COUNT(*), MAX(card_version))` em `history/` e roda os detectores de card sempre que o watermark mudou desde a última corrida — independente do que está staged. Determinístico, barato, fecha o item 3 do §6.5.2 na raiz. (Mesma família do set-diff que recomendamos ao daktus-hub: timestamp/arquivo-staged não detecta mudança de dado.)

### C.3 — Detectores cross-field: biblioteca única de predicados relacionais `[HIGH]`

Todos entram em `card_checks.py` (C.2) com tag no `ledger_self.jsonl`; nenhum exige ler conteúdo clínico — são todos relações entre campos (compatível com §9):

| # | Detector | Predicado (estrutural) | Pega |
|---|---|---|---|
| 1 | `resposta_embutida` | overlap de n-grams normalizados entre (`frente_contexto`+`frente_pergunta`) × (`verso_resposta` + `titulo` da questão-mãe); flag se run comum ≥ 6 tokens ou Jaccard > 0.5 | os 34 do incidente com `titulo` interpolado; modo #1 |
| 2 | `pergunta_template` | regex dos 3 anti-padrões nomeados na spec **+** `"Qual o distrator típico"` **+** `LIKE tema\|\|':%'` | modo #2; fecha a assimetria spec×detector |
| 3 | `distrator_perdido` | `questoes_erros.alternativa_marcada` não-vazia **e** ausente (substring normalizada) de todos os campos dos cards derivados → WARN **por questão** | modo #6 — o que o usuário considera mais grave |
| 4 | `multi_parte` | ≥2 `?` ou conectivo interrogativo composto (" e por que", " e qual") | modo #3 |
| 5 | `negativo_orfao` | `NÃO\|EXCETO` na pergunta **e** ausência de marcador de lista em qualquer campo do card | modo #5 |
| 6 | `contexto_artefato` | estender `RE_PCT_FAKE` (`card_self_sufficiency.py:66-68`) com `acertaram` + variantes (`N% dos alunos/candidatos`) | o near-miss dos 68 |

Modo #4 (pergunta retórica) fica `[MEDIUM]`: heurística de polaridade ("por que não…") tem falso-positivo alto; começar como INFO, promover se a precisão medida na fixture sustentar. Modo #7 (monocontextual): não automatizar agora — custo/benefício ruim, sinal melhor virá da métrica de reincidência (C.8).

E corrigir a exclusão do agregado: os 3 sinais de `audit_flashcard_quality.py:164` voltam ao "TOTAL COM ≥1 SINAL" e ao `--export` (podem continuar discriminados, mas não invisíveis).

### C.4 — "Card ativo": uma VIEW + um helper, migração por equivalência `[HIGH]`

```sql
CREATE VIEW flashcards_ativos AS
SELECT * FROM flashcards WHERE COALESCE(needs_qualitative, 0) < 2;
```

+ helper `db.py::ativos()` para os caminhos pandas. Migração segura: (1) criar a view; (2) para cada um dos 5 consumidores, teste de equivalência `COUNT(atual) == COUNT(view)` **antes** de trocar — a diferença conhecida é `cards_regen_queue.py:47` (`nq != 2`), que é **bug semântico** (nq=3, se existir um dia, voltaria como ativo): trocar primeiro, com o diff de contagem registrado. (3) proibir por convenção (e por grep no auto_check) novo SQL inline com `needs_qualitative` fora da view/helper.

### C.5 — Suíte de testes: fixtures estruturais sintéticas, não os 68 reais `[HIGH]`

Os 68 do incidente são o **calibrador**, não a fixture: contêm texto clínico e vivem num banco fora do git. Gerar réplicas estruturais com texto dummy que preservem as propriedades detectáveis (pergunta `TEMA: qual a conduta/criterio correto?`, `titulo` embutido na pergunta, `verso_armadilha` com exatamente 200 chars, contexto com `N% acertaram`) — mantém conteúdo clínico fora do repo (§9) e a suíte roda em qualquer clone. Ordem de valor:

1. `test_insert_questao.py`: sem `cards` → `ValueError` (contrato C.1); `cards=[]` → `ValueError`; caminho qualitativo → contagem de linhas + campos + `fsrs_cards.state=0` + nq=0; anulada → 0 cards + mensagem correta.
2. `test_card_checks.py`: 1 fixture positiva + 1 controle por predicado de C.3 (padrão que `test_card_self_sufficiency.py` já usa — estender, não inventar).
3. Suíte própria para `audit_card_atomicity.py` (está no harness sem testes — os falsos-positivos do docstring viram casos).
4. Propriedade de consistência: card que passa no write-gate não pode ser flagado pelo detector batch equivalente (mesma biblioteca ⇒ teste barato).
5. Calibração (manual, uma vez): rodar os detectores novos contra o banco real e conferir recall nos 68 (`questao_id 781-814`) — meta ≥ 66/68; registrar o número no ledger.

### C.6 — Idempotência de `record_review`: lock otimista com rowcount, na transação que já existe `[HIGH]`

Menor mecanismo que dá trava técnica à Invariante C — sem schema novo, sem token de sessão:

```python
cursor.execute('''UPDATE fsrs_cards SET ...
    WHERE card_id = ? AND COALESCE(last_review,'') = COALESCE(?,'')''',
    (..., flashcard_id, card_data.get('last_review')))
if cursor.rowcount == 0:
    conn.rollback()
    raise ConcurrentReviewError(f"card {flashcard_id}: estado mudou desde a leitura (re-record bloqueado)")
# só então INSERT no revlog; commit único
```

O `WHERE` compara com o `last_review` **lido** no passo 1: segunda chamada concorrente acha o valor já alterado, `rowcount=0`, nada grava — nem UPDATE nem revlog (o INSERT fica condicionado, mesma transação; hoje já é uma conexão única, só falta a condição). Cobre exatamente o incidente do card 403 (s108). Dedup por UNIQUE no revlog **não** recomendo como mecanismo primário: `review_time` tem resolução de segundo e a semântica de "mesma revisão" é do fluxo, não do relógio. Caso queiram cinto extra: `UNIQUE(card_id, last_review)` parcial, depois do lock — opcional.
Aproveitar a passada para popular `last_elapsed_days` (`:343-350`) ou removê-lo do schema — coluna sempre-NULL é doc-drift dentro do banco.

### C.7 — Fila de introdução: banda prioritária explícita no dreno padrão; não reordenar o FIFO silenciosamente `[HIGH]`

Integrar `get_fresh_error_cards` ao dreno padrão como **banda de política**, não como reordenação do bucket de novos:

- Ordem servida: `1. vencidos → 2. fresh-error (janela 48h, cap N) → 3. revisões agendadas → 4. novos FIFO`. Reordenar `f.id ASC` (`db.py:519-521`) mudaria a semântica global de forma invisível; banda é política nomeada, observável e configurável — e é exatamente o §22 do anexo GPT, que aqui converge com vocês.
- Onde mora: composição da fila em `db.get_cards_by_bucket` (ou função-política fina chamada por ela), servida por `fsrs_queue.py`. **Não** criar tabela de política agora — duas constantes (`janela_horas`, `cap_fresh`) + o `selection_reason` retornado por card bastam; tabela só se a política começar a variar de verdade.
- O vazamento de nq: adicionar `AND COALESCE(f.needs_qualitative,0) < 2` (ou trocar o FROM para a view de C.4) em `get_fresh_error_cards`. Isso **não quebra** o `--pre-bloco` — conserta-o: aposentado dentro da janela aparecer no pré-bloco era bug lá também. O teste existente do contrato (`due == criação para state=0`) permanece válido.
- Cada card servido carrega `selection_reason ∈ {vencido, fresh_error, agendado, novo}` — alimenta a UI conversacional ("⚠ erro repetido há 3 dias") e o revlog (C.8).

### C.8 — Observabilidade: instrumentar a geração e a revisão com 3 adições baratas `[HIGH]`

`quality_source` é mesmo proxy fraco (autodeclarado pelo produtor do defeito). Substituir por evidência de evento:

1. **Log de geração** — a cada insert que cunha cards, registrar no `ledger_self.jsonl` (infra existente, fingerprint `generation|questao_id`): `{questao_id, n_cards, caller, gate_result, ts}`. Zero tabela nova; o ciclo opened/resolved já serve para "gate rejeitou → reforjado".
2. **Revlog ganha 2 colunas** (`ALTER TABLE` barato): `card_version` (a versão que o usuário **viu** — sem isso a pergunta "v3 tem Again maior que v2?" é irrespondível, pois `apply_reforja` incrementa a versão e o histórico perde o vínculo) e `selection_reason` (de C.7). É o §41 do anexo GPT, e é a adição de maior alavancagem por byte deste plano.
3. **Consultas de eficácia, não dashboard**: script read-only (`tools/learning_efficacy.py`) com Again-rate por `tipo × card_version × quality_source × idade`, e **reincidência** como métrica de 1ª classe — o matcher F25 já detecta "erro novo sobre elo já cardado"; persistir esse evento (`reincidencia|questao_id` no ledger) e reportar `cards com reincidência pós-criação / cards de erro`. Gate anti-decorativo de vocês mesmos: se em 3 ciclos nenhuma decisão de reforja/política citar esses números, remover o script.

---

## D. Triagem das 14 perguntas do anexo GPT (§53)

| # | Pergunta | Veredito |
|---|---|---|
| 1 | `2_estudo.py` legado ou ativo? | **Dissolvida** — já reescrito como viewer read-only; revisão é conversacional |
| 2 | Compat `Temas/Fichas/Memorex`? | **Dissolvida** — já removida (resta 1 comentário + 1 info) |
| 3 | `4_simulados.py`? | **Dissolvida** — não existe; README correto |
| 4 | Consumidor de `medhub_memory.db`? | **Respondida** — sim, `app/memory/*`, ativo hoje; segundo banco justificado (memória de agente ≠ domínio de estudo) |
| 5-8 | RAG/HyDE/BM25/Chroma valem o custo? | **Legítimas, fora deste escopo** — existe harness próprio (`tools/eval/run_eval.py`, `test_rag_two_tier.py`); a resposta é uma rodada de benchmark medido, não opinião. Não decidir sem rodar |
| 9 | Migrar para Note→Card? | **Não agora** `[MEDIUM]` — a estrutura já é isomórfica: `questoes_erros` É a note (1:N com `flashcards`); o que o Anki chama de template, aqui é a régua de autoria. Migração de schema com 1277 cards + estado FSRS = custo alto, ganho especulativo |
| 10 | Suporte `.apkg`? | **Adiar** — backup/portabilidade já cobertos por `backup_db.py` + SQLite aberto; nada no schema atual bloqueia um exportador futuro. Não construir por vaidade (§54 do próprio anexo) |
| 11 | Optimizer só pós-limpeza do revlog? | **Concordo, e com gate duplo** — (a) revlog limpo (C.6 + excluir reviews de cards nq=2 do dataset); (b) volume: 1466 reviews é marginal para o optimizer do py-fsrs; re-avaliar ao cruzar ~3-5k reviews limpos `[MEDIUM]` |
| 12 | O que copiar do ecossistema? | Preview de intervalos (já em A.2); load balancing e workload forecasting **já existem** (`fsrs_balance.py`, `fsrs_load.py`) — o anexo recomenda construir o que o repo já tem |
| 13 | Invenção desnecessária? | O caminho heurístico (C.1), os 3 `INSERT INTO fsrs_cards` duplicados, 5 variantes de boilerplate de encoding, colunas `frente`/`verso` (B.2) |
| 14 | Menor conjunto p/ 90% do valor? | Núcleo: `questoes_erros + flashcards + fsrs_* + insert_questao (agent-first) + card_checks + adapter py-fsrs + fsrs_queue + /revisar + resumos/`. Todo o resto (memória, RAG, eval, dashboards, biblioteca) é satélite que se justifica por medição, não por presença |

---

## E. Proposta de refatoração priorizada

**P0 — estancar (diffs pequenos, alavancagem máxima):**
1. Matar caminho heurístico + `cards` ausente/`[]` → erro (C.1) — remove ~60 linhas, mata 5 modos de falha na origem
2. Filtro nq em `get_fresh_error_cards` (C.7) — 1 linha, fecha o vazamento da quarentena
3. `cards_regen_queue.py:47` `nq != 2` → `COALESCE(nq,0) < 2` (C.4) — 1 linha, bug semântico
4. `PRAGMA foreign_keys=ON` + varredura única de órfãos (B.1)

**P1 — integridade:**
5. Lock otimista em `record_review` (C.6) — Invariante C vira trava técnica
6. VIEW `flashcards_ativos` + migração dos 5 consumidores por equivalência (C.4)
7. `card_checks.py` extraído e chamado pelos 5 writers; CHECKs mínimos de schema (C.2) — condicionado à decisão B.4 para o CHECK de nq

**P2 — detecção:**
8. Detectores cross-field + fixtures sintéticas + suíte do atomicity + calibração ≥66/68 (C.3/C.5)
9. Watermark de dado no `auto_check` (C.2.3); sinais excluídos voltam ao agregado

**P3 — observabilidade/produto:**
10. `card_version` + `selection_reason` no revlog; log de geração no ledger; `learning_efficacy.py` com métrica de reincidência (C.8)
11. Banda prioritária no dreno padrão + preview de intervalos no `/revisar` (C.7 + A.2.1); contrato de apresentação codificado em `revisar.md` (B.3)

**P4 — gated/adiado:** optimizer FSRS (gate duplo D.11) · `.apkg` · benchmark RAG (rodada própria) · Note→Card (não) · drop das colunas `frente`/`verso` (na próxima migração de schema)

**O que NÃO fazer:** Study Workbench em Streamlit (premissa refutada — a superfície de revisão é conversacional por decisão; as boas ideias do anexo desembocam no `/revisar`) · tabela `card_feedback` nova (nq=1 + motivo no ledger cobrem; criar tabela só se as categorias tipadas provarem necessidade) · tabela de política de fila (duas constantes bastam) · scheduler por modo de estudo (o anexo mesmo veta em §21) · decisão sobre BM25/Chroma sem rodar o harness de eval existente.

---

## F. Âncoras e limites

- **Âncoras do brain/**: `cs230-l6` (error analysis: a falha observada — os 68 — orienta a correção, e a fixture de regressão nasce do incidente real); `web-eval-methodology` (detectores como asserts de regressão; gate anti-decorativo em métricas); `aieng-book-ch04` (avaliação por evidência downstream — Again-rate por versão = usuário avaliando o gerador); padrão `Drift-as-Primary-Debt` (observed-systems, N=3: aqui de novo — contrato×código×banco divergindo é a dívida-mestre); padrão `Terrain-Refutes-Spec Discipline` (observed-systems: 5 claims do anexo GPT refutados por inspeção direta).
- **Limite honesto**: não li conteúdo clínico de nenhum campo (§9 respeitado — todos os predicados propostos são relacionais/estruturais); não rodei os detectores propostos (recall 66/68 é meta de calibração, não medição feita); a recomendação C.6 pressupõe chamadas concorrentes raras (single-user) — se surgir concorrência real de processos, revisitar com lock de banco.
- Implementação: este documento é o julgamento de arquitetura pedido no §7. Se o operador der GO, o ciclo vibeflow (PRD → specs → implement → audit) roda sobre P0-P2 como das outras vezes (padrão D56).
