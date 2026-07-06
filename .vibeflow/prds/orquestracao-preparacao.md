# PRD: Orquestracao da Preparacao -- Posicao SSOT + Recomendador do Dia + Loop de Erro em Horas

> Gerado via /vibeflow:discover em 2026-07-05 (ciclo 2 de engenharia delegada, Fable/ai-eng)
> Fonte: decisao de produto do operador (2026-07-05, pos-s109) + AUDITORIA_MEDHUB.md (ledger F16-F26, secoes 3c/3e/3f) + verificacao contra o codigo (regra do ledger secao 0.4).
> Achados verificados antes de entrar aqui: op-3 (posicao por regex: `day_plan.py::_semana_conteudo`, quebrada NESTE momento -- HANDOFF diz "Proximo: S12", regex exige "Proxima = SNN"); F22 (guarda `WHERE sessao_num=? AND area=?` em `registrar_sessao_bulk.py:56-65`); F23 (`get_cards_by_bucket`: novos = `state=0 ORDER BY id ASC LIMIT 10` -- card fresco com 361 no backlog nunca aparece); F24/F26 (verificados por uso real na s109: driver ad-hoc + quoting quebrado; anuladas no bruto de erros).
> Encoding ASCII limpo (AGENTE.md secao 4.5).

## Problema

O MedHub registra a preparacao com disciplina (volume, FSRS, erros, contratos), mas NAO orquestra. Consequencias observadas em uso real (s109, 2026-07-05):

1. **A posicao no cronograma e fragil e o custo e inaceitavel (decisao do operador).** A "semana de conteudo" e parseada por REGEX sobre texto manual do HANDOFF (`_semana_conteudo`, marca canonica "Proxima = SNN"). Neste exato momento a marca nao casa ("Proximo: S12") e o day_plan cai no fallback nominal-por-data, que assume preparacao em dia com o calendario. O operador reporta ter de REENSINAR a posicao ao agente repetidas vezes. E a mesma classe de defeito ja resolvida para numeros (F1/F6: derivado e fiel, digitado drifta) -- mas no campo mais critico do produto.
2. **O plano do dia e relatorio, nao recomendacao.** A s109 planejou ~120 questoes; o dia real teve tempo curto e cansaco -- foram 60q de tema unico + drenagem de cards. Produtivo, mas ninguem DECIDIU isso: o ambiente nao pesa "fechar a grade inteira antes da prova" (foco declarado) contra a divida FSRS crescente (backlog 361 novos), o tempo disponivel e a energia do dia. A decisao de mix (questoes x cards x descanso x simulado) fica 100% na intuicao do operador -- exatamente o que ele quer delegar.
3. **O loop de erro fecha em dias; o erro reincide em horas.** O link "caso classico jovem <48h = operar, nao pedir imagem" foi carded no 1o bloco da s109 (card 730) e o operador reincidiu 3x no MESMO link no 2o bloco, horas depois (F23). O card fresco (state 0, id alto) e estruturalmente invisivel: a fila de novos e `ORDER BY id ASC LIMIT 10` sobre 361 pendentes. A regra "nao tolere errar 2x pelo mesmo motivo" existe no papel; nada a opera (F25: reincidencia so e detectada se o agente lembrar de cruzar manualmente).
4. **O registro de volume tem friccoes que corrompem o proprio estado.** 2o bloco da mesma area no mesmo dia exige falsear `sessao_num` (F22 -- a s109 gravou "s110" que nao existe em history/); lote de N erros exige driver Python ad-hoc porque o insert e 1-por-vez com ~17 args (F24 -- 1a tentativa da s109 quebrou no quoting, ZERO inseridos); questao anulada/banca-divergente conta como erro limpo e polui a taxa real e o pipeline de cards (F26).

Quem sofre: o operador (estuda "no escuro" sobre o que rende mais; reensina posicao; taxa poluida) e o agente-coordenador (reconstroi contexto a cada boot; cruza reincidencia de memoria; escreve drivers descartaveis).

## Publico-alvo

- **Primario:** o agente-coordenador de sessao (Claude/Opus operando o MedHub via CLIs e contratos) -- consome posicao, plano, fila e registra volume/erros.
- **Secundario e beneficiario final:** o operador (Daniel), que recebe o plano do dia como RECOMENDACAO fundamentada e para de reensinar o ambiente.

## Solucao proposta

Elevar o day_plan de relatorio a ORQUESTRADOR, sobre uma posicao de cronograma que vira estado de primeira classe no db. Quatro ondas:

- **Onda 1 -- Posicao SSOT (op-3 + F22).** A posicao no cronograma (semana de conteudo) vira registro no `ipub.db` (estado de preparacao), atualizado por comando explicito e/ou no ato do registro de volume; `day_plan` LE do db -- a regex `_semana_conteudo` morre (rebaixada a fallback com WARN de deprecacao). O `--handoff-block` passa a EMITIR a posicao (derivada); o HANDOFF textual nunca mais e input. Invariante no `auto_check` (classe F1, nasce WARN): HANDOFF divergente da posicao do db e sinalizado. F22 entra aqui como integridade do registro: `--acumular` soma 2o bloco na mesma (sessao, area) preservando a guarda anti-duplo por default; falsear sessao_num deixa de ser necessario.
- **Onda 2 -- Recomendador do dia (op-1/2/4).** `day_plan` ganha a secao "Recomendacao do dia": funcao de decisao DETERMINISTICA e transparente (norma em contrato .md, mecanica no CLI -- mesmo padrao do teto dinamico F4) que consome sinais ja derivaveis do db (dias para a prova, grade restante vs ritmo real 7/14 dias, divida FSRS + teto efetivo, backlog de novos, reincidencias abertas, posicao da Onda 1) + inputs do dia (`--tempo <h>`, `--energia alta|media|baixa`; opcionais, defaults declarados no output). Emite: mix recomendado com quantidades (blocos de questoes por tema da grade, cards, mini-drill anti-reincidencia, simulado, descanso) + JUSTIFICATIVA citando os sinais + projecao ("no ritmo real de X q/dia a grade fecha em DATA; para fechar ate a prova precisa de Y q/dia; folga de Z dias"). Descanso e simulado sao saidas legitimas da funcao (regra explicita, ex.: energia baixa + slack positivo -> sessao leve/descanso; semana multiplo de N ou pre-marco -> slot simulado usando a area "Simulado" ja existente).
- **Onda 3 -- Loop de erro em horas (F23 + F25).** `fsrs_queue --pre-bloco <tema>`: seleciona cards de erro FRESCOS (state 0, cunhados ha <48h ou desde a ultima sessao) do tema-alvo para mini-drill antes do bloco -- mecanicamente um filtro de fila; rating segue o caminho unico `record_review` (e revisao legitima, conta no teto). Detector de reincidencia no `insert_questao` (F25): pos-insert, match por (tema + tipo_erro + overlap de tokens do elo/o_que_faltou) contra erros/cards existentes -> imprime flag `[REINCIDENCIA]` com card/contagem (WARN informativo, politica s106/107); o agente-coordenador promove a padrao vivo no fechamento. O recomendador (Onda 2) puxa o pre-bloco automaticamente quando ha reincidencia aberta no tema-alvo do dia.
- **Onda 4 -- Registro sem friccao (F24 + F26).** `insert_questao --errors-file <lote.json>`: N erros completos (metadados + campos de card) numa transacao unica -- elimina a classe driver-ad-hoc/quoting; JSON invalido = rollback total. Flag `--status anulada|banca-divergente` no registro do erro (F26): fora da taxa de acerto real, sem card de "erro" (card neutro opcional), marcada para o gate de evidencia (`/pesquisar-evidencia`) quando banca x diretriz divergem.

## Criterios de sucesso

Binarios e observaveis:

1. `day_plan` obtem a semana de conteudo do db; alterar a posicao e 1 comando; uma sessao NOVA (boot frio) reporta a posicao correta sem qualquer texto ensinado. (op-3)
2. Com HANDOFF textual divergente da posicao do db, `auto_check` emite WARN nomeado; coerente = silencio. A regex `_semana_conteudo` nao e mais o caminho primario (fallback com WARN de deprecacao, ou removida). (op-3/F1)
3. 2o bloco da mesma (sessao, area) com `--acumular` SOMA feitas/acertos (taxonomia consistente); sem a flag, aviso atual preservado; `sessao_num` falso deixa de ser necessario. (F22)
4. `day_plan` (secao Recomendacao) emite mix com quantidades + justificativa citando >=3 sinais derivados + projecao de fechamento da grade (data estimada no ritmo real e q/dia necessario). Numeros batem com fixtures deterministicas. (op-1/2)
5. `--tempo`/`--energia` alteram a recomendacao conforme regras do contrato; omitidos, o output declara os defaults assumidos. Descanso e simulado aparecem como recomendacao quando as regras disparam (fixtures cobrem ambos). (op-4)
6. `fsrs_queue --pre-bloco <tema>` lista SOMENTE cards state-0 frescos do tema; rating deles passa por `record_review` (caminho unico preservado); sem a flag, fila byte-identica ao atual. (F23)
7. Insert de erro cujo (tema + elo) casa com card existente imprime `[REINCIDENCIA] card NNN (Kx no tema)`; fixture com o caso real da s109 (Q4/Q8/Q11 vs card 730) dispara; caso sem relacao nao dispara. (F25)
8. `insert_questao --errors-file` com lote valido insere N erros + cards numa transacao; com item invalido, rollback total (zero parcial); a 2a execucao do mesmo lote nao duplica (idempotencia por hash/dedupe do lote). (F24)
9. Erro com `--status anulada|banca-divergente` nao entra na taxa real (percentual_acertos), nao gera card de erro, e aparece marcado para gate de evidencia; `--handoff-block` reflete a taxa limpa. (F26)
10. Regressao: `pytest` na raiz verde; scripts standalone preservados; `auto_check --staged` verde; sem a s NOVAS flags, todos os CLIs byte-identicos ao comportamento atual. (harness)

## Escopo v0

Ondas 1-4, nesta ordem (1 e pre-requisito de 2; 3 e 4 independentes entre si). Decisoes ja tomadas pelo operador (2026-07-05): foco = orquestracao da preparacao; recomendacao inclui reduzir carga/descansar/simulado; posicao errada e inaceitavel (prioridade maxima); fluxo completo delegado (discover -> gen-spec -> implement -> audit).

## Anti-escopo

Explicito e agressivo -- NADA disto entra neste ciclo:

- **ML/estatistica preditiva** para a recomendacao (v0 e deterministico: regras + projecao aritmetica; sofisticar SO depois de coletar serie de tempo/energia real).
- **F16-F18 (pipeline de conhecimento PDF -> md -> RAG)** -- ciclo 3; a decisao de arquitetura (two-tier, .md canon) ja esta registrada no ledger/parecer, nao se perde.
- **F19 (multi-prova / prova-alvo de primeira classe)** -- registrado com gate de recorrencia.
- **UI Streamlit** -- toda a entrega e CLI + contrato; o agente e a interface.
- **Gerador de simulado** -- recomendar o slot entra; gerar conteudo de simulado nao.
- **Reescrever FSRS / mudar schema fsrs_*** -- intocados; pre-bloco e filtro de fila.
- **Expurgo F11** -- trilha propria GATED (runbook pronto, aguarda go nominal do operador).
- **Reforge dos cards 95/120** -- e do agente-player via /curar-cards (120 pelo gate de evidencia).
- **Mudanca dos parametros do teto dinamico** -- validado com dados reais na rodada 1 (degrau 30/60 cobre o pior caso observado; so mexer se divida real >60 aparecer).

## Contexto tecnico

O que ja existe e a solucao REUSA (nao reconstruir):

- `tools/cronograma.py`: grade parseada (semanas, temas, total_questoes) + `semana_corrente(grade, hoje)` (nominal-por-data -- vira sinal comparativo "atraso/adiantamento", nao mais fallback silencioso).
- `tools/day_plan.py`: `_teto_efetivo` (F4, precedente de norma-no-contrato + mecanica-no-CLI), campo `divida`, `ritmo_cronograma` (restante/dias), `--handoff-block` (F6, numeros derivados), `--review-plan` (F3, clusters do dia).
- `sessoes_bulk` ja tem `data_sessao` e a area especial "Simulado" (slot dedicado, comentario no proprio codigo aponta tendencia/predicao ENAMED).
- `get_cards_by_bucket(area, tema, new_limit)` ja filtra por tema -- o pre-bloco e uma consulta nova na camada db (state=0 + created-at recente), nao um schema novo.
- `questoes_erros` carrega `elo`/`tipo_erro`/`o_que_faltou`; cards carregam tema+links -- o detector F25 e um matcher sobre dados existentes.
- Politica WARN->BLOCK (s106/107) para todo invariante novo; paridade command<->skill via `sync_skills.py` para toda edicao de contrato de fluxo.
- Padroes vibeflow aplicaveis: `db-access-layer` (sqlite3 so em db.py; excecao historica do insert_questao standalone), `error-insertion-pipeline`, `agent-workflow-protocol`, `domain-engine-api`.

Restricoes (nao violar): `import sqlite3` so em `app/utils/db.py` (excecao pre-existente: `tools/insert_questao.py` standalone); FSRS escreve so via `record_review`; encoding ASCII nos arquivos do repo; `ipub.db` e `data/chroma/` local-only; armadilhas cumulativas; nada de gradiente/emoji-em-header (nao ha UI neste ciclo, mas fica registrado).

Nota de schema: a Onda 1 introduz UMA tabela nova leve (estado de preparacao key-value com timestamp+fonte) -- justificada por ser o SSOT da posicao (a alternativa, coluna em taxonomia_cronograma, mistura grade com estado). `sessoes_bulk` ganha modo acumulativo SEM mudar chave (a guarda continua; a flag soma). Nenhuma tabela existente muda de schema.

## Perguntas em aberto

- Limiares/pesos exatos do recomendador (ex.: quantos q/dia de folga disparam "descanso permitido"; janela do ritmo real 7 vs 14 dias): a spec fixa DEFAULTS nomeados no contrato (parametros no topo do CLI, mesmo padrao TETO_BASE/CAP_MULTIPLICADOR) -- ajustaveis por uso real sem novo ciclo. Nao bloqueia.
- Persistencia de `--tempo`/`--energia` como serie historica (insumo do futuro preditivo): v0 registra junto ao estado de preparacao (opcional, barato); a decisao de USAR a serie fica para o ciclo em que houver dados. Nao bloqueia.
