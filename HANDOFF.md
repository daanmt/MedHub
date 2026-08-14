# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-14 (madrugada) -- Sessão 143 -- Simulado 4 (66/100) + análise dos 34 erros com gabarito comentado + dashboard dos 3 simulados + DRENAR de 97 cards.*

## > Próximo passo imediato

1. **Redrill dos 42 cards nota < 4 da s143** -- lista completa em `tmp/redrill42.json` (regerar: ver query em §Sessão). Prioridade: **18 nota 1**, depois **10 nota 2**, depois 14 nota 3. O usuário não conseguiu redrillar na sessão (fechou 01h54). Estes cards já voltaram para a fila pelo FSRS (todos com due <= 14/08), então drenam naturalmente -- mas os nota 1 merecem PREPARAR antes de sondar.
2. **Revisão Direcionada -- 3 gaps que exigem matéria, não card:**
   - **AGC (colpocitologia)** -- errado 2x no MESMO dia (Q84 do simulado + card 453). Regra: AGC/AOI/ASC-H/LIE-AG -> colposcopia imediata, nunca repetir citologia; endométrio só depois e só se >=35a ou sangramento anormal. O erro é sempre pular ao 3º degrau (histeroscopia).
   - **Escores estimados em vez de somados** -- 3 erros hoje (PRAM, Caprini, Apgar) + o usuário declarou dificuldade sistêmica com escores. Não é memória, é não abrir o escore.
   - **"Diagnóstico feito != pode tratar"** -- card 538 (CCR sem estadiamento) = erro #462; mesmo mecanismo da Q34 (pulmão sem estadiamento invasivo do mediastino).
3. **Reforma do mecanismo de cunhagem e auditoria de cards** -- frente principal. Pré-auditoria interna feita nesta sessão (4 subagents); handoff técnico entregue ao ai-eng em `C:\Users\daanm\ai-eng\HANDOFF_MEDHUB_FLASHCARDS.md`. Ver §Reforma abaixo.
4. **68 cards do Simulado 4 em quarentena** (`questao_id BETWEEN 781 AND 814`, `needs_qualitative=2`) -- aguardam a reforma. São fixture real dos defeitos.

## Estado por frente
- **Volume & Metas:** 6019 / 9454 acum. Simulado 4 registrado (100q, 66 acertos, sessão 143).
- **Simulados:** S2 54/100 (02/08) -> S3 60/100 (06/08) -> **S4 66/100 (13/08)**. +6 e +6, três medidas.
- **FSRS:** 97 cards avaliados na s143 (55 nota 4 / 14 nota 3 / 10 nota 2 / 18 nota 1 -- média 3,09). Pool de nunca-introduzidos era 792 de 1209 ativos (65%) no início da sessão.
- **Erros catalogados:** 120 dos 3 simulados (S2 ids 622-667, S3 719-758, S4 781-814).
- **Posição:** conteúdo S14 (Drive desatualizado -- rodar `tools/cronograma.py --sync-drive` antes de confiar na ordem).

## Última sessão -- s143

### Simulado 4 e a análise
- 66/100. Blocos de 20: 13 / 14 / **11** / 15 / 13. O vale do bloco 3 (q41-60) não é explicado pela dificuldade populacional (~70% em todos os blocos) -- hipótese de janela de fadiga no meio da prova. **Ajuste combinado: pausas por volta das q35 e q65** (não 33/66, que deixam a faixa 41-60 longe de qualquer intervalo) + anotar horário de início de cada bloco no próximo simulado.
- Os 34 erros foram analisados com o gabarito comentado da banca e inseridos no db (`insert_questao.py --errors-file`).
- **7 reincidências do elo exato** contra o corpus, 4 delas com apenas 6 dias: PNI/pneumocócica (#736), LH basal na puberdade precoce (#726), teste do pezinho (#746), escore de Caprini (#742). Mais AGC (#264, 59d), liquor de TB (#309, 50d) e pneumoperitônio (#282, 54d).
- **Causa-raiz da reincidência: 40 de 40 cards do Simulado 3 nunca haviam sido apresentados** em 6 dias. O ciclo análise->card funciona; o que não funcionava era a fila.
- Registro `#736` corrigido (guardava a fase de transição da pneumocócica; calendário PNI 2026 é 20-valente nas 3 doses: 2, 4 e 12 meses).

### Sessão de cards (97 avaliados)
- **7+ reversões confirmadas** de erros do Simulado 2: #634 (SBC 2025 pré-hipertensão), #649 (hanseníase), #650 (TCE), #651 (DIU), #652 (IML/causa externa), #657 (ferro), #666 (endometriose), #667 (CPRE). Onde o card rodou, o erro não voltou.
- **Cluster biliar (maior área fraca histórica, ~1250 erros) veio 4/4 correto.** Diverticulite em imunossuprimido também.
- Contraste medido: cards **novos** (estreia) média ~2,7 · cards **vencidos** (já em ciclo) média **4,0**.
- Sessão atravessou a meia-noite -- ao consultar `fsrs_revlog` use `review_time >= '2026-08-13 20:00'`, não `date(review_time)='2026-08-13'`.

### Query para regerar a lista dos 42
```sql
SELECT r.card_id, r.rating, t.area, t.tema, f.frente_pergunta
FROM fsrs_revlog r JOIN flashcards f ON f.id=r.card_id
LEFT JOIN taxonomia_cronograma t ON t.id=f.tema_id
WHERE r.review_time>='2026-08-13 20:00' AND r.rating<4
ORDER BY r.rating, t.area;
```

## Reforma de flashcards (frente nova, prioritária)

### Defeitos confirmados nesta sessão
1. **Fallback heurístico silencioso** em `tools/insert_questao.py`: quando o chamador não passa `cards=[...]`, o script fabrica a pergunta por template (`fp = frente_pergunta or f"{tema}: qual a conduta/criterio correto?"`) e interpola `titulo` numa segunda pergunta -- produzindo cards em que **a pergunta contém a resposta**. Lote de 13/08: 68/68 inutilizáveis, zero avisos.
2. **Perda do distrator** -- o mais grave segundo o usuário. `questoes_erros.alternativa_marcada` existe, mas o card derivado não a carrega: treina o fato, não a discriminação que causou o erro. (Caso-tipo: card 1157, cuja decisão real era entre duas condutas, e o card só cobra uma.)
3. **Enunciado negativo órfão** -- cards "qual NÃO é" cujas alternativas não foram persistidas: irrespondíveis fora da prova original (cards 1145, 1151, 1160).
4. **Pergunta multi-parte** viola atomicidade (cards 1053, 1054, 1048) -- o usuário quer 1 card = 1 informação.
5. **Pergunta retórica** que entrega a resposta pela formulação (card 1042).
6. **Card monocontextual** -- conceito ancorado num único cenário não transfere (card 496: pneumoperitônio só existe no contexto neonatal, e por isso não transferiu para a Q81 do simulado).
7. **Vazamento de rótulo na apresentação** -- exibir `tema` acima da pergunta entrega a categoria da resposta. Corrigido no lado do agente durante a sessão; não há contrato codificado sobre isso.

### Encaminhamento
- Handoff técnico completo (schema, mapa de arquivos, modos de falha, repro) em `C:\Users\daanm\ai-eng\HANDOFF_MEDHUB_FLASHCARDS.md`. Escopo declarado como **engenharia apenas** -- o documento instrui explicitamente a não julgar conteúdo clínico.
- Pré-auditoria interna com 4 subagents (geração / detectores / motor FSRS / superfícies e contratos) rodada na s143; consolidar os achados no handoff antes de o ai-eng aprofundar.
- Política de introdução: proposta de **faixa prioritária** para cards nascidos de erro de simulado, desacoplada do intake FIFO geral. Teto diário subiu para 100 (decisão do usuário na s143).

### Cards a cunhar (pedidos do usuário na sessão)
- Critérios de elegibilidade do metotrexato na gestação ectópica (β-hCG, tamanho da massa, BCF, estabilidade).
- Par do card de pneumoperitônio fora do contexto neonatal (desmonocontextualizar).

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_143.md*
*Dashboards: Autópsia dos Simulados (120 erros, navegável por mecanismo) e A Dívida de Fixação (diagnóstico do funil) -- URLs em history/session_143.md*
