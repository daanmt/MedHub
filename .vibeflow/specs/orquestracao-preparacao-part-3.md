# Spec: Orquestracao da Preparacao -- Part 3: Pre-bloco por tema + detector de reincidencia

> Gerado via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/orquestracao-preparacao.md` (Onda 3).
> Encoding ASCII limpo. Budget: <= 6 arquivos.

## Objetivo

O loop de erro fecha em horas: cards de erro frescos do tema-alvo ganham caminho de mini-drill ANTES do proximo bloco (`fsrs_queue --pre-bloco`), e todo insert de erro cruza automaticamente contra erros/cards existentes, sinalizando `[REINCIDENCIA]` no ato.

## Contexto

Na s109 o operador reincidiu 3x no MESMO link (Q4/Q8/Q11 -> card 730) HORAS depois de o card ser cunhado: state-0 com id alto e invisivel na fila (`ORDER BY id ASC LIMIT 10` sobre 361 novos) -- F23. A deteccao da reincidencia foi cruzamento MANUAL do agente -- F25. A regra "nao tolere errar 2x pelo mesmo motivo" (analisar-questao) nao tem mecanismo. O HANDOFF da s109 pede mini-drill dos cards 729/730 antes do proximo bloco -- este e o mecanismo generico disso.

## Definition of Done

1. [ ] `python tools/fsrs_queue.py --pre-bloco "<tema>"` (4a acao mutuamente exclusiva, ao lado de --next/--list/--record) lista SOMENTE cards de erro frescos do tema (via `db.get_fresh_error_cards` da part-2; state=0, janela parametrizada default 48h, match de tema LIKE como o filtro --tema atual), no mesmo formato de emissao da fila; fila sem a flag byte-identica.
2. [ ] Rating de card servido pelo pre-bloco passa pelo caminho unico existente (`--record CARD_ID --rating N` -> `db.record_review`); NENHUM caminho novo de escrita FSRS; o card drilado sai naturalmente do bucket "novos".
3. [ ] `insert_questao.py`, apos inserir o erro, roda o matcher de reincidencia: (mesmo tema) + overlap de tokens normalizados entre `elo`/`o_que_faltou` novos e `elo`/`o_que_faltou`/`verso_regra_mestre` dos erros/cards existentes; acima do limiar, imprime `[REINCIDENCIA] elo similar ao card NNN / erro MMM (Kx no tema)` -- WARN informativo, exit code inalterado, insert NUNCA bloqueado (politica s106/107).
4. [ ] Fixture com o caso real da s109 dispara: erro novo com elo "pede US/TC no caso classico" + card 730 pre-existente ("caso classico = operar, nao pedir imagem") -> flag emitida apontando o 730; fixture negativa (elo sem relacao, mesmo tema) NAO dispara. Teste roda em copia temp do db.
5. [ ] Craftsmanship: matcher com constantes nomeadas no topo (LIMIAR_OVERLAP, STOPWORDS minimas) e funcao pura testavel; SQL do matcher dentro do insert_questao (excecao standalone ja autorizada) ou via db.py -- sem novo `import sqlite3` fora das excecoes; ASCII; `pytest` + standalone + `auto_check --staged` verdes; `--cluster`/`--review-plan`/`--next`/`--list` sem regressao.

## Escopo

- `tools/fsrs_queue.py`: acao `--pre-bloco TEMA` + `--janela-horas N` (default 48).
- `tools/insert_questao.py`: funcao `checar_reincidencia(conn, tema_id, elo, faltou) -> list` + print do WARN no fluxo de insert (single e, quando part-4 chegar, por item do lote).
- `app/utils/db.py`: ajuste/reuso de `get_fresh_error_cards` (se part-2 ja entregou, so consumir).
- `tools/test_reincidencia.py` (NOVO): fixtures caso-real-s109 (positiva), negativa, pre-bloco filtra tema/janela, rating via caminho unico.
- Bridge pytest se necessario.

## Anti-escopo

- Nao mexer no algoritmo/agenda FSRS (pre-bloco e FILTRO de selecao; o rating segue o fluxo normal e conta no teto do dia).
- Nao criar embedding/similaridade semantica para o matcher (v0 = tokens normalizados + overlap; se a precisao decepcionar em uso real, sobe para o ledger).
- Nao escrever o "padrao vivo" no HANDOFF automaticamente (o agente-coordenador promove; o WARN e o sinal).
- Nao bloquear insert por reincidencia (WARN informativo sempre).

## Decisoes tecnicas

- **Frescor via `fsrs_cards.due` de state-0** (o insert grava due=now na criacao): zero mudanca de schema; contrato fixado por teste (se um caminho futuro criar state-0 com due!=criacao, o teste acusa).
- **Matcher lexical simples** (normaliza, remove stopwords minimas, overlap de tokens com limiar): barato, explicavel, calibravel por 2 constantes; a fixture real da s109 e o teste de aceitacao. Alternativa semantica rejeitada no v0 (custo/dependencia sem evidencia de necessidade).
- **Pre-bloco como ACAO da fila** (nao CLI novo): a fila e o lugar canonico de servir cards; o agente ja conhece a interface.

## Padroes aplicaveis

- `error-insertion-pipeline.md` (ponto de extensao pos-insert; transacao intocada).
- `fsrs-review-flow.md` + `db-access-layer.md` (caminho unico record_review; state-0 semantics).
- Precedente: flag `--cluster` (F3, opt-in byte-identico sem flag).

## Riscos (premortem)

- **Falso-positivo do matcher em temas densos** (muitos cards proximos): limiar conservador de fabrica + WARN informativo (custo de falso-positivo = 1 linha impressa); calibrar com a base real (fixture 730 dispara, vizinhos nao).
- **Pre-bloco vazio frustrar o fluxo** (tema sem fresco): saida explicita "0 cards frescos p/ <tema> na janela de 48h" -- nao silencio.
- **Contagem no teto**: drill de frescos consome teto do dia; e intencional (revisao legitima) e o recomendador (part-2) ja considera o teto ao montar o mix -- documentado no contrato.

## Dependencies

- .vibeflow/specs/orquestracao-preparacao-part-2.md (funcao `get_fresh_error_cards` em db.py; recomendador cita o pre-bloco)
