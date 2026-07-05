# PRD: Engenharia de Estado e Medida -- Ledger F1-F13

> Gerado via /vibeflow:discover em 2026-07-05
> Fonte: AUDITORIA_MEDHUB.md (ledger vivo, F1-F9, s108) + scan de arquitetura do agente de engenharia (F10-F13, 2026-07-05).
> Todos os achados F1/F3/F6/F8/F9/F10 foram VERIFICADOS contra o codigo antes de entrar aqui (regra do ledger secao 0.4). F2 nao reproduziu no scan. Encoding ASCII limpo (AGENTE.md secao 4.5).

## Problema

O MedHub tem governanca madura (contratos em core/contracts/, harness auto_check.py, HANDOFF/ESTADO, history/), mas os invariantes vivem em TEXTO e DISCIPLINA, nao em VERIFICACAO EXECUTAVEL. Consequencias observadas em uso real (s108):

1. **Drift de estado silencioso.** O ponteiro de sessao do HANDOFF avancou sem log correspondente (F1); os numeros do HANDOFF (volume, FSRS, backlog) divergiram da fonte viva em 3 pontos distintos (F6: 4418 vs 4454; 322 vs 351; 27+13 vs 40+4). A fonte derivada (day_plan/db) e fiel; o texto digitado drifta. Nada barra a dessincronia.
2. **Contradicoes de contrato dormentes.** O contrato de /revisar permite "sobrepor a nota" e ao mesmo tempo proibe duplo --record; a contradicao dormiu de s075 ate s108, quando um override real (card 403, Paget->Faget) gravou 2 linhas de revlog e recalculou FSRS a partir de estado ja mutado (F9). O PREPARAR contamina o trial de recall por 3 canais verificados (F8).
3. **Friccao de fila.** A fila FSRS entrega cards com temas intercalados; a conducao por cluster (pedagogicamente superior, prevista na Camada 0) exige re-agrupamento manual do agente a cada sessao, e a contagem manual errou 3x na s108 (F3).
4. **Divida FSRS sem politica.** 44 cards agendados ja excediam o teto diario de 30 antes de qualquer card novo; sem estrategia explicita, ou o teto e violado todo dia ou o backlog nunca drena (F4).
5. **SSOT furado e harness nao-portavel.** app/pages/1_dashboard.py bypassa a camada db.py com sqlite3 cru e path relativo (F10, viola db-access-layer.md); ipub.db persiste como blob no historico git ate s058 (F11); os 4 test_*.py sao scripts avulsos sem harness pytest (F12); os hooks de boot vivem so em settings.local.json, nao versionado -- o boot deterministico nao sobrevive a um clone (F13).

Quem sofre: o operador (numeros errados no plano do dia, notas FSRS corrompidas por override mal-gravado, revisao fragmentada) e o agente-coordenador de sessao (re-trabalho manual de clusterizacao, reconcile manual de drift, contratos ambiguos).

## Publico-alvo

- **Primario:** o agente-coordenador de sessao (Claude/Opus operando o MedHub via CLIs e contratos) -- consumidor direto de fila, plano do dia, HANDOFF e harness.
- **Secundario:** o operador (Daniel), que le o plano do dia e confia nos numeros e nas notas FSRS.

## Solucao proposta

Transplantar o padrao **Executable-State-Reconcile** (validado em 3 sistemas do portfolio ai-eng) para o harness do MedHub: todo invariante de estado que hoje e disciplina textual vira **check executavel** no auto_check/day_plan; todo numero que hoje e digitado vira **derivado** da fonte viva; toda aresta de contrato exposta pelo uso vira **clausula explicita** com protocolo que a previne. Cinco ondas:

- **Onda 1 -- Integridade de estado (F1, F6, F13):** invariante de ponteiro de sessao no auto_check (ponteiro do HANDOFF <= max(session_NNN)+1; nasce WARN, politica s106/107); bloco numerico do HANDOFF gerado por `day_plan.py --handoff-block` (numeros derivados, texto qualitativo continua manual); hooks de boot movidos para settings.json versionado.
- **Onda 2 -- Fila e plano (F3, F4):** flag `--cluster` em fsrs_queue.py (preserva prioridade de bucket, ordena secundariamente por area/tema, cards do mesmo tema contiguos); `day_plan.py --review-plan` emite os clusters do dia com contagem derivada; metrica de divida de atrasados como cidada de primeira classe no day_plan; **politica de teto dinamico** (decisao do operador, 2026-07-05): em regime de divida (atrasados acima de limiar), o teto diario sobe automaticamente ate drenar, com cap de seguranca -- parametros fixados na spec.
- **Onda 3 -- Contratos de medida (F9, F8):** protocolo de /revisar muda para gravar `--record` SOMENTE apos a janela de override (apresenta nota proposta -> espera confirmacao/correcao -> grava uma vez; casa com o modo lote existente; zero mudanca de schema); clausula de isolamento do PREPARAR (aquece conceitos/mecanismos, nunca o par pergunta-resposta dos cards do bloco; cards de fato puro = refresh contraindicado; regras formuladas como tendencia, nunca absoluto). Edicoes de contrato respeitam a paridade command<->skill via sync_skills.py.
- **Onda 4 -- Higiene SSOT (F10, F12, F11):** 1_dashboard.py volta para a camada db.py (funcao dedicada se necessario; some o sqlite3 cru e o path relativo); harness pytest minimo (conftest/pytest.ini) preservando a execucao standalone dos 4 test_*.py que o auto_check invoca; expurgo do blob ipub.db do historico git (operacao dedicada, GATED pelo operador -- reescreve historico).
- **Onda 5 -- Sinal e curadoria (F5, F7, F2):** PREPARAR proativo no fluxo DRENAR (ao abrir cluster, checa sinal de frieza via review_radar/stability e OFERECE o aquecimento; depende da Onda 2 entregue); heuristica experimental no audit_flashcard_quality.py (verso_armadilha que nomeia competidor de categoria diferente da resposta sem nomear nenhum da mesma categoria -- sinal fraco, nasce WARN); instrumentacao de latencia dos hooks (F2 NAO reproduziu no scan -- medir antes de consertar; cronometrar auto_check --staged e day_plan isolados e registrar no ledger).

## Criterios de sucesso

Binarios e observaveis, por onda:

1. `auto_check.py` com HANDOFF apontando sessao inexistente em history/ emite WARN nomeado; com ponteiro coerente, silencio. (F1)
2. `python tools/day_plan.py --handoff-block` imprime o bloco "Estado por frente" numerico pronto para colar; os numeros batem com o db no momento da emissao. (F6)
3. Hooks de SessionStart/PostToolUse funcionam num clone fresco do repo sem depender de settings.local.json. (F13)
4. `python tools/fsrs_queue.py --list --cluster` retorna a fila com buckets preservados e temas contiguos dentro de cada bucket; sem a flag, comportamento atual intacto. (F3)
5. `python tools/day_plan.py --review-plan` lista os clusters do dia com contagem por tema; a contagem bate com a fila real. (F3/F6)
6. day_plan expoe divida de atrasados e teto efetivo do dia; com atrasados acima do limiar, o teto efetivo sobe conforme a formula da spec e nunca excede o cap. (F4)
7. Contrato de /revisar (canonico + espelho em paridade) contem: janela de override antes do --record; clausula de isolamento do PREPARAR; distincao raciocinio vs fato puro. `sync_skills.py --check` passa. (F9/F8)
8. `grep "import sqlite3" app/pages/` retorna vazio; dashboard le via db.py com path resolvido pela raiz. (F10)
9. `pytest` na raiz roda os 4 test_*.py e passa; `python tools/test_X.py` continua funcionando; auto_check continua verde. (F12)
10. Pos-expurgo (quando o operador liberar): `git log --all -- ipub.db` vazio e clone do repo nao contem o blob. (F11)
11. Numeros de latencia de auto_check/day_plan registrados no ledger com metodo reproduzivel. (F2)
12. Ao abrir cluster frio no DRENAR, o agente OFERECE o PREPARAR sem ser pedido (clausula no contrato + sinal exposto pelo CLI). (F5)

## Escopo v0

Ondas 1-5 acima, nesta ordem. Cada onda e entregavel e auditavel isoladamente; a ordem respeita dependencias (F5 depende de F3; F4-metrica depende do day_plan tocado na Onda 1). Decisoes ja tomadas pelo operador: escopo = ledger completo; F4 = teto dinamico.

## Anti-escopo

Explicito e agressivo -- NADA disto entra:

- **Reescrever o FSRS** para fidelidade ao v4 de referencia (debito conhecido, projeto separado; F9/F8 protegem a medida sem tocar o algoritmo).
- **Mudanca de schema do banco** para F9 (o caminho e protocolo, nao --amend; decisao do ledger mantida).
- **Reforge dos cards 95/120** e qualquer curadoria de conteudo clinico -- e dominio, fica com o agente-player (Opus) via /curar-cards e gate de evidencia. Este PRD entrega no maximo a heuristica de linter (F7).
- **Reviver BM25 / mexer no RAG** (ChromaDB/Ollama/HyDE intocados).
- **API grounded-QA** (PRD F0 de 2026-06-17 -- nao adotado, permanece morto).
- **UI Streamlit** alem do necessario para F10 (nenhum redesign, nenhum componente novo).
- **Deploy/cloud/CI remoto** -- o MedHub e local-first por design; ipub.db continua local-only.
- **Maquina nova de observabilidade** (dashboards, telemetria, protocolo de sessao novo) -- o ledger F10+ alimentado pelo agente-player JA E o loop de observacao; este PRD torna os invariantes executaveis, que e a observabilidade de maior alavancagem. Maquina so quando o sinal recorrer.
- **Politica de drenagem alem do teto dinamico** (modo mutirao etc.) -- decisao tomada, alternativas descartadas.

## Contexto tecnico

O que ja existe e o PRD reusa (nao reconstruir):

- **Harness:** tools/auto_check.py (modos --changed/--staged/--all; orquestra audit_resumos, test_revisao_calibrada, test_autonomia_hooks, sync_skills --check; quotepath-safe). O invariante F1 entra como check novo aqui. Politica WARN->BLOCK (s106/107): regra nova nasce WARN, so bloqueia quando a base zera.
- **Fonte viva:** tools/day_plan.py (read-only, ja computa _fsrs_counts, volume, cronograma; hospeda infer_nota/difficulty_report). --handoff-block, --review-plan e teto dinamico entram aqui. day_plan NAO escreve estado (preservar).
- **Fila:** tools/fsrs_queue.py e camada fina sobre app/utils/db.py::get_cards_by_bucket, que JA retorna area/tema por card -- F3 e ordenacao local, zero mudanca de query.
- **Escrita FSRS:** unico caminho = db.record_review() (UPDATE fsrs_cards + INSERT fsrs_revlog, append-only). NENHUMA mudanca aqui; F9 e mudanca de protocolo no contrato.
- **Contratos:** core/contracts/revisao-calibrada-contract.md (norma) + .claude/commands/revisar.md (canonico) + .agents/skills/ (espelho gerado). Toda edicao passa por sync_skills.py --check (paridade e WARN no auto_check).
- **Padroes .vibeflow a seguir:** db-access-layer.md (sqlite3 so em db.py -- F10 e a correcao de uma violacao dele), agent-workflow-protocol.md (boot/fechamento), conventions.md (CLIs com argparse, path do db relativo a raiz, conn.close() explicito, pt-BR).
- **Restricoes duras:** encoding ASCII nos docs de governanca (AGENTE.md 4.5); ipub.db e medhub_memory.db nunca commitados; armadilhas de resumo cumulativas; agentes nao fazem SQL direto.
- **Fora do codigo:** o ledger AUDITORIA_MEDHUB.md continua vivo e acumulando F14+ (fase de questoes do agente-player); este PRD snapshota F1-F13 -- achados novos entram no proximo ciclo, nao neste.

## Questoes abertas

1. **F4 -- parametros do teto dinamico:** limiar de regime de divida (proposta: atrasados > teto_base), formula (proposta: teto_efetivo = teto_base + min(atrasados, cap_extra)) e cap de seguranca (proposta: 2x teto_base). Fixar na spec com aval do operador na revisao.
2. **F11 -- janela do expurgo:** operacao reescreve historico; executar num momento sem clones divergentes e com backup. Gate explicito do operador antes de rodar (Tier 3).
3. **F13 -- fronteira settings.json vs settings.local.json:** hooks e permissoes genericas versionam; paths/permissoes especificos da maquina ficam no local. Mapear na spec o que migra.
