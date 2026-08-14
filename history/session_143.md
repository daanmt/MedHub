# Session 143 -- Simulado 4 (66/100) + dashboard dos 3 simulados + DRENAR 97 cards + incidente de cunhagem
**Data:** 2026-08-13 (atravessou a meia-noite; parte dos registros com `review_time` em 2026-08-14)
**Ferramenta:** Claude Code (Opus 5, 1M)
**Continuidade:** Sessão 142

---

## O que foi feito

### Simulado 4 -- 66/100
- Terceiro simulado completo pós-virada multi-banca: **54 (02/08) -> 60 (06/08) -> 66 (13/08)**, +6 e +6.
  Piso de CRM do ENAMED (~60%) cruzado pela segunda vez consecutiva. Registrado em `sessoes_bulk` (sessão 143, Simulado).
- Blocos de 20: **13 / 14 / 11 / 15 / 13**. O vale do bloco 3 (q41-60) não é explicado pela dificuldade
  populacional (~70% em todos os blocos). O usuário atribuiu à "lombeira do meio da prova"; a recuperação
  espontânea para 75% no bloco 4 descarta fadiga acumulada progressiva e sustenta a hipótese de janela.
  **Combinado: pausas por volta das q35 e q65** (não 33/66, que deixariam a faixa 41-60 longe de qualquer
  intervalo) + anotar horário de início de cada bloco no próximo simulado, para separar janela-por-questão
  de janela-por-relógio.
- Os 34 erros foram analisados contra o gabarito comentado da banca e inseridos via
  `insert_questao.py --errors-file` (ids **781-814**).

### Raio-x integrado dos 3 simulados
- Corpus consolidado: **120 erros** (S2 ids 622-667, S3 719-758, S4 781-814), classificados por **mecanismo
  transversal** (11 categorias). Os 34 do S4 à mão; os 86 anteriores por heurística sobre o texto de análise
  já registrado (marcados como `auto` no dashboard -- refinar à mão é trabalho pendente).
- Distribuição: discriminador-que-exclui 30 · comporta de conduta 26 · lacuna pura 23 · diretriz desatualizada 10 ·
  fato no contexto errado 9 · escore por impressão 6 · enunciado negativo 5 · inversão 4 · categoria adjacente 4 ·
  degrau anterior 2 · par incompleto 1.
- **7 reincidências do elo exato**, 4 delas com apenas 6 dias: PNI/pneumocócica (#736), LH basal na puberdade
  precoce (#726), teste do pezinho (#746), Caprini (#742). Mais AGC (#264, 59d), liquor de TB (#309, 50d),
  pneumoperitônio (#282, 54d).
- **Causa-raiz encontrada: 40 de 40 cards do Simulado 3 nunca haviam sido apresentados** em 6 dias; pool geral
  de nunca-introduzidos era 792 de 1209 ativos (65%). O ciclo análise->card funciona; a fila é que não rodava.
- Registro `#736` corrigido (guardava a fase de transição da pneumocócica; PNI 2026 é 20-valente nas 3 doses).
- **Reformulação de padrão:** o que eu vinha chamando de "escalar sem gatilho" não tem viés direcional --
  6 casos de escalar a mais e 3 de deixar de escalar, todos com o critério objetivo escrito no enunciado.
  O problema é a comporta não ser consultada, em nenhuma das direções.
- **Padrões novos nomeados:** classifica por impressão em vez de somar o escore; termo de categoria adjacente;
  responde a pergunta do degrau anterior; a hipótese do paciente adotada como própria; fonte normativa nomeada
  no enunciado.

### Sessão de cards -- 97 avaliados
- Composição: 72 de simulado (S2/S3, nunca introduzidos) + 28 vencidos. Média **3,09**
  (4: 55 · 3: 14 · 2: 10 · 1: 18). Zero duplicatas no revlog.
- **8 reversões confirmadas** de erros do Simulado 2: #634 (SBC 2025 pré-hipertensão), #649, #650, #651,
  #652, #657, #666, #667. Mais o acerto no cluster biliar em 4 de 4 cards -- que é a maior área fraca
  histórica do radar (~1250 erros) -- e diverticulite em imunossuprimido, a fraqueza nº1.
- **Contraste medido:** cards novos (estreia) média ~2,7 · cards vencidos (já em ciclo) **4,0**. O que está
  no ciclo está consolidado; o que nunca entrou, não está.
- Gaps que exigem matéria (Revisão Direcionada, pendente): **AGC** (errado 2x no mesmo dia -- Q84 + card 453),
  **escores** (PRAM, Caprini, Apgar -- 3 erros + dificuldade declarada pelo usuário),
  **"diagnóstico feito != pode tratar"** (card 538 = erro #462, mesmo mecanismo da Q34).
- Lista dos 42 cards nota <4 persistida em `tmp/redrill42.json`.

### Incidente: cunhagem de cards defeituosos
- Os 68 cards gerados a partir do lote do S4 saíram **inutilizáveis** (34 com a resposta embutida na pergunta,
  34 com pergunta de template genérico). Detectados na abertura da sessão de cards, antes de qualquer
  avaliação; postos em quarentena (`needs_qualitative=2`, `questao_id BETWEEN 781 AND 814`).
- Causa: o lote foi inserido **sem o campo `cards`**, caindo no fallback heurístico de `insert_questao.py`,
  que fabrica a pergunta por template e interpola o `titulo` do erro. Erro de operação meu -- mas o fallback
  produz artefato ruim em silêncio, com a mesma mensagem de "Sucesso" do caminho correto.
- **Feedbacks de autoria do usuário durante a sessão** (todos registrados): card não pode pedir 2 informações;
  card perde o distrator que causou o erro (treina o fato, não a discriminação); enunciado negativo sem as
  alternativas não é respondível; pergunta retórica não mede recall; não exibir o tema no cabeçalho de card
  diagnóstico. O usuário pediu **reforma ampla do mecanismo de geração e auditoria**.

### Pré-auditoria do subsistema de flashcards (4 subagents)
Varreduras com escopos disjuntos -- geração, detectores, motor FSRS, superfícies/contratos. Achados principais:
- **O dado não tem gate; só o código que o produz tem.** O harness de qualidade roda no pre-commit do git,
  e os cards vivem no `ipub.db`, fora do git. Inserir cards ruins numa sessão que não toca arquivo versionado
  não aciona verificação nenhuma.
- **A spec bane verbatim o template que o código gera** (`estilo-flashcard.md:26` vs `insert_questao.py:206`),
  e o detector tem hardcode para os outros dois anti-padrões nomeados na mesma spec, não para esse.
- `audit_flashcard_quality.py` **exclui do agregado** os 3 sinais que pegariam o defeito (linha 164).
- `audit_card_atomicity.py` **nunca lê** `verso_regra_mestre` nem `verso_armadilha`.
- **`db.get_fresh_error_cards` já implementa a priorização por erro recente** -- existe, funciona, e está
  apenas desligada do dreno padrão. **Mas não filtra `needs_qualitative`**: os 68 cards em quarentena
  reapareceriam por esse caminho (risco não materializado -- `--pre-bloco` é opt-in e não está em uso).
- **Violação de contrato pelo próprio código:** `needs_qualitative=1` é banido desde a s075 e
  `insert_questao.py:210` o reintroduz no caminho heurístico.
- **Precedente F39 (s128):** mesmo tipo de defeito em 364 cards, 264 ainda abertos. Consequência documentada
  e decisiva para o design: **5 de 6 ocorrências do que fora catalogado como "padrão de erro do usuário" eram
  defeito de card.** Card mal cunhado não só falha em ensinar -- fabrica sinal falso no diagnóstico.
- Outros: `cards: []` grava zero cards e imprime "Sucesso"; `verso_resposta` pode entrar vazio; truncamento
  cego por slice (200/300 chars); `record_review` sem idempotência (incidente card 403, s108);
  convenção de `--dry-run` inconsistente entre CLIs; 3 definições divergentes de "card ativo".

---

## Artefatos

- **Autópsia dos Simulados** (dashboard dos 120 erros, navegável por mecanismo, com racional correto e o
  ritual que desarma cada padrão): https://claude.ai/code/artifact/c414a4f3-65b8-428a-a823-4b93057b3ff4
- **A Dívida de Fixação** (diagnóstico do funil de cards e das reincidências):
  https://claude.ai/code/artifact/7abc8441-3086-41c5-b799-8906f05d918c
- **Handoff técnico ao ai-eng** (429 linhas, escopo de engenharia apenas):
  `C:\Users\daanm\ai-eng\HANDOFF_MEDHUB_FLASHCARDS.md`

---

## Pendências (ver HANDOFF.md)

1. Redrill dos **42 cards nota <4** (`tmp/redrill42.json`) -- prioridade nos 18 nota 1.
2. **Revisão Direcionada** dos 3 gaps que exigem matéria, não card.
3. **Reforma do mecanismo de cunhagem e auditoria** -- aguarda retorno do ai-eng.
4. **68 cards do S4 em quarentena** -- servem de fixture real para calibrar os detectores novos.
5. Cards a cunhar: critérios de elegibilidade do MTX na ectópica; par do card de pneumoperitônio fora do
   contexto neonatal (hoje é monocontextual, e foi por isso que não transferiu na Q81).
6. Refinar à mão a classificação automática dos 86 erros de S2/S3 no dashboard.

---

## Nota de operação

A sessão atravessou a meia-noite. Para consultar o revlog desta sessão use
`review_time >= '2026-08-13 20:00'` -- filtrar por `date(review_time)='2026-08-13'` perde 83 dos 97 registros.
