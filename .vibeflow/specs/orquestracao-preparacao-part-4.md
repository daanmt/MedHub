# Spec: Orquestracao da Preparacao -- Part 4: Insert em lote (errors-file) + status de questao anulada

> Gerado via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/orquestracao-preparacao.md` (Onda 4).
> Encoding ASCII limpo. Budget: <= 6 arquivos.

## Objetivo

Registrar um lote de N erros vira 1 chamada com 1 JSON (transacao unica, zero quoting de shell), e questao anulada/banca-divergente deixa de poluir a taxa real e o pipeline de cards.

## Contexto

Na s109, 11 erros exigiram driver Python ad-hoc (`run_inserts.py`) porque `insert_questao.py` e 1-por-vez com ~17 args; a 1a tentativa via shell quebrou no quoting (exit 2, ZERO inseridos) -- F24. Na mesma sessao, Q10 (gabarito oficial x EMED divergem) e Q5 ("nenhuma correta") entraram no bruto como erro limpo -- F26; mesma familia do F7 (ciclo 1), agora no nivel da questao. `--cards-file` existente so ADICIONA cards a erro ja criado.

## Definition of Done

1. [ ] `python tools/insert_questao.py --errors-file lote.json` insere N erros completos (metadados + campos de card v5.0 por item) numa UNICA transacao; sucesso imprime resumo (`N erros, M cards, ids ...`); schema do JSON documentado no help e validado antes de escrever (campos obrigatorios = os required do argparse atual).
2. [ ] Item invalido em qualquer posicao -> rollback TOTAL (zero parcial), mensagem apontando o item/campo, exit != 0. Teste cobre lote valido, lote com item 3 invalido (nada inserido) e re-execucao do MESMO lote (dedupe por hash de tema+enunciado por item: itens ja inseridos sao pulados com aviso, nao duplicados).
3. [ ] Campo `status` por item (e flag `--status` no modo single): `anulada` | `banca-divergente` | ausente (=valida). Persistido em `questoes_erros.status` via `ALTER TABLE ADD COLUMN` idempotente no proprio CLI (aditivo; DEFAULT NULL; padrao CREATE-IF-NOT-EXISTS ja usado no repo).
4. [ ] Erro com status anulada/banca-divergente: NAO gera card de erro (nem FSRS init), NAO incrementa contadores de acerto/realizadas usados na taxa (taxonomia intocada pelo item), e aparece marcado na saida (`[GATE-EVIDENCIA] Q banca-divergente registrada p/ /pesquisar-evidencia`); o registro do ERRO em si persiste (memoria do caso). `--handoff-block`/taxa real ficam limpos por construcao.
5. [ ] Detector de reincidencia (part-3) roda POR ITEM do lote (WARNs agregados no resumo final).
6. [ ] Craftsmanship: transacao unica com `conn.commit()` so no fim e `finally: conn.close()` (convencao CLI tools/); ASCII; `pytest` + standalone + `auto_check --staged` verdes; modo single sem `--status`/`--errors-file` byte-identico ao atual.

## Escopo

- `tools/insert_questao.py`: `--errors-file` (JSON array), validacao pre-transacao, dedupe por hash, coluna `status` (ALTER idempotente), gate de contadores por status, integracao do matcher part-3 por item.
- `tools/test_batch_insert.py` (NOVO): fixtures em db temp -- lote ok, rollback, dedupe, status anulada (sem card, taxa limpa), reincidencia em lote.
- Bridge pytest se necessario.
- Documentacao inline do schema JSON no `--help` (sem doc externa nova).

## Anti-escopo

- Nao redesenhar a interface single (args atuais intactos; batch e caminho paralelo).
- Nao gerar cards "neutros" para anuladas no v0 (registrar o erro basta; card neutro so se o uso pedir -- ledger).
- Nao automatizar o `/pesquisar-evidencia` (a flag MARCA; o gate continua humano/agente).
- Nao migrar dados historicos (status passado fica NULL=valida; reclassificacao retroativa e curadoria, nao engenharia).

## Decisoes tecnicas

- **JSON file > args encadeados**: elimina a classe inteira de quoting de shell (causa-raiz do F24); o agente escreve arquivo com Write (sem shell) e chama 1 comando. Alternativa stdin rejeitada (pior de debugar; arquivo fica como artefato da sessao).
- **`ALTER TABLE ADD COLUMN` idempotente** (checa PRAGMA antes): unico ponto do ciclo que toca schema existente -- aditivo, DEFAULT NULL, invisivel a todo SELECT existente. O PRD tinha nota conservadora "nenhuma tabela existente muda de schema" (escrita para a Onda 1); a alternativa fiel (tabela satelite questao_status) fragmenta o SSOT do erro por zelo formal -- decisao de spec: coluna, com esta justificativa registrada.
- **Dedupe por hash de conteudo** (tema+enunciado normalizados), nao por (sessao, area): a idempotencia certa para lote e "este ERRO ja foi registrado", pratica que o F22 apontou como o criterio correto ("a idempotencia anti-duplo deveria olhar um hash do lote").
- **Anulada registra o erro, nao o card**: o valor de memoria do caso permanece consultavel; o que se protege e a MEDIDA (taxa) e a fila (cards de nao-lacuna).

## Padroes aplicaveis

- `error-insertion-pipeline.md` (transacao atomica estendida a N itens; pontos 1-5 do pipeline preservados por item).
- `db-access-layer.md` (excecao standalone do insert_questao mantida; commit/close disciplinados).
- Convencao CLI tools/ (argparse, prints legiveis, return bool).

## Riscos (premortem)

- **JSON malformado do agente** (aspas, encoding): validacao pre-transacao com mensagem por campo + teste com JSON quebrado; UTF-8 explicito na leitura do arquivo.
- **Hash de dedupe fraco** (enunciados quase identicos legitimos, ex. Q repetida em prova diferente): hash inclui tema+enunciado inteiro normalizado -- colisao exige texto identico; aviso de skip lista os itens pulados para o agente conferir.
- **Coluna nova quebrar SELECT * antigo em codigo nao-mapeado**: risco baixo (SELECTs do repo sao por nome); grep de `SELECT \*.*questoes_erros` no implement confirma antes de mergear.

## Dependencies

- .vibeflow/specs/orquestracao-preparacao-part-3.md (matcher de reincidencia consumido por item do lote)
