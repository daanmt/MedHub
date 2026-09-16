# Notas de implementacao -- plano-ssot-e-cards-v2 part-9 (player de cards)

Data: 2026-09-16 (s183). Agente: Coding Agent (Opus 5).

## Arquivos tocados

- `tools/fsrs_queue.py` -- 3 acoes novas (`--export-player`, `--build-player`, `--record-lote`) + 5 argumentos (`--out`, `--lote`, `--sessao`, `--apply`, `--expect`). Funcoes puras extraidas para teste: `montar_lote`, `injetar_lote`, `ler_notas`, `aplicar_notas`, `teto_do_dia`.
- `core/templates/player.html` -- NOVO. Pagina autocontida, desktop-first.
- `tools/test_fsrs_queue_player.py` -- NOVO. 19 testes, db sintetico em arquivo temporario.
- `.claude/commands/revisar.md` -- secao "DRENAR no player" (assinatura das 8 flags + rito de 7 passos).
- `core/contracts/revisao-calibrada-contract.md` -- v1.3 -> v1.4, Clausula 12.

## Decisoes tomadas dentro do espaco da spec

1. **`--record-lote` exige `--lote`** (o export). A pagina e input nao confiavel; e contra o export que `card_id` e validado e de onde sai o `selection_reason` gravado no revlog -- a pagina nunca decide a propria proveniencia. Aceita tambem o campo `lote` dentro do arquivo de notas.
2. **Erro recusa, duplicata avisa.** `card_id` fora do lote, `rating` fora de 1..4 e `defeito` sem motivo sao ERRO e recusam o `--apply` (exit 2, nada gravado). `card_id` repetido e WARN e conta uma vez (warn-first). Motivo: erro e arquivo malformado -- corrigivel; duplicata e comportamento normal do relearning.
3. **Teto do dia importado do `day_plan`** (`_teto_efetivo`, F64: `vencidos = atrasados + hoje`), nunca reimplementado. Import indisponivel degrada para 60 COM WARN em stderr (F60), nunca em silencio.
4. **`_contar_revlog` usa `db.get_connection()`** (SELECT puro). O `fsrs_queue.py` continua sem `import sqlite3` e sem nenhuma tabela na allowlist -- testado.
5. **Restauracao pos-refresh.** O `db` guarda so `rating_primeira`; ao recarregar, card com nota >= 4 ou defeito sai do lote e card com nota < 4 volta para a cauda do relearning. O relogio da sessao e reconstruido do `ts` mais antigo restaurado, evitando um documento extra so para o inicio.

## Defeito encontrado e corrigido durante a execucao

`injetar_lote` casava o marcador pela PRIMEIRA ocorrencia, e o cabecalho de comentario do template citava a propria tag `<script id="lote" ...>`. Resultado medido na 1a execucao real: a injecao comeu 4.4 KB da pagina (o `<style>` inteiro) ate o proximo `</script>`; `grep -c max-width` deu **0**. Dois remedios no mesmo commit: o comentario deixou de citar a tag, e `injetar_lote` agora **recusa** template com numero de marcadores diferente de 1. Regressao travada em `test_build_recusa_marcador_AMBIGUO`.

## Pendencias que NAO sao deste agente (fora do escopo de arquivos permitido)

1. `pytest.ini` -- inscrever `test_fsrs_queue_player.py` em `python_files` (F43; hoje a suite aparece como orfa junto de `test_cronograma_extensivo.py`, que e de outra frente).
2. `python tools/sync_skills.py` -- regenerar o espelho de `revisar` (PARITY_DRIFT + `test_espelho_gerado`).
3. `python tools/reachability_check.py --tabela` -> colar em `AGENTE.md §7.4` (G5). As novas mencoes a `reforja.py`/`cards_prune.py` na skill e no contrato mudaram a contagem de referenciadores de 4 CLIs; a linha de `cronograma.py` ja estava stale antes.
4. `AGENTE.md §6` e `§7.3` citam o contrato como **v1.3** -- atualizar para v1.4.
5. Publicar a pagina com `capabilities: {db: {}}` e medir o criterio 5 do PRD (minutos por 60 cards, 3 sessoes no chat x 3 no player) -> `history/`.

## Riscos declarados

- **A capability `db` nunca foi exercitada em runtime real.** O caminho feliz (`use("db")` -> `collection().get()` -> `doc().set()`) esta escrito contra os tipos do contrato 0.2.52, nao contra uma execucao. O fallback de texto e o que garante que a 1a sessao nao perca o lote.
- **Ordem de chegada.** A restauracao do `db` chega por promessa; se o usuario ja comecou a drillar, a fila NAO e remontada (flag `interagiu`) para nao embaralhar o card na tela -- o painel e atualizado mesmo assim.
- **`--record-lote --apply` nunca rodou contra o `ipub.db` real** (proibido para este agente). O caminho de gravacao esta coberto so por db sintetico; as duas recusas (`--expect` errado e erro no arquivo) foram exercitadas contra o banco real e nao escreveram nada.
