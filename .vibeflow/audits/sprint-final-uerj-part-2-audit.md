## Audit Report: sprint-final-uerj part-2 (`plano.py --sprint`) -- commit 5a54f17

**Verdict: PASS**

Auditado em 13/10/2026 pelo `git show 5a54f17`. Nada gravado no `ipub.db` real: idempotência medida numa CÓPIA
(`sqlite3.backup`, origem `mode=ro`) no scratchpad.

### DoD Checklist
- [x] 1. `core/sprint.json` -- forma exata da spec; `ler_sprint` valida; `test_sprint_json_e_a_unica_fonte_dos_numeros` varre o trecho do sprint em `plano.py` contra os literais (2026-10, 1798/1799, 890-892, 80).
- [x] 2. `dia_plano TEXT` -- `_ensure_plano_dia_column` (db.py ~1750) idempotente por `PRAGMA table_info`; leitor sem DDL (`_select_plano` devolve NULL); writer `plano_set_dias` só no db.py, chamado só pelo `plano.py`; comentário na allowlist; `test_writer_allowlist.py` verde. "Fora" = dia NULL + `sprint: fora (<motivo>)`.
- [x] 3. `montar_sprint` PURA -- simulado no dia fixo e sozinho (`fixos`), ordem (faixa, peso, semana, ordem, id), first-fit <= cap, tarefa > cap só em dia vazio, dias de max(inicio, hoje). Os 6 testes pedidos existem (capacidade, simulado sozinho, ordem, determinismo com 5 embaralhamentos, feita fora, 2a corrida = 0).
- [x] 4. CLI -- dry-run real: 19 dias, 44 tarefas / 1489 q no sprint, 37 fora com motivo, cortadas [1798, 1799], `--expect 83`; nenhum dia > 80 fora dos simulados (100/97/100, sozinhos). `--apply` sem `--expect` = erro de argparse (exit 2); expect divergente = exit 2.
- [x] 5. Seção em `.claude/commands/cronograma.md` + espelho; `sync_skills.py --check` OK; `cli_signature_check` 0 órfãs, exit 0.
- [x] 6. Suíte inteira 1750 passed (inclui o WIP de outro subagente no hub); `test_plano` + `test_writer_allowlist` 96 passed. `auto_check --changed` não rodado agora (a árvore hoje tem o WIP de outra spec); evidência indireta: o pre-commit roda `auto_check` e o commit entrou. SQL só no `db.py`.

### Pattern Compliance
- [x] COUNT-ASSERT medido e gravado pelo mesmo caminho (`plano_set_dias(aplicar=False/True)`), como `plano_upsert_tarefas`.
- [x] Dry-run não roda DDL (testado; confirmado na cópia: coluna ausente depois do dry-run).
- [x] Backup fixado (`backup_db.fixar_antes_do_ato`) antes do 1º write; `SemPontoDeRetorno` = recusa.

### Critical Gate
Limpo. O único DDL é `ALTER TABLE ... ADD COLUMN` (aditivo, sem regra); o UPDATE tem `WHERE id = ?`.

### Respostas pedidas
(a) **First-fit x faixa.** Nenhuma tarefa de faixa menor toma o lugar de uma de faixa maior que caberia: as maiores são encaixadas antes e a vaga só diminui. O que existe é PREENCHIMENTO DE SOBRA: no dado real, #740 (média, 10 q, 20/10) e #97 (média, 19 q, 31/10) entram enquanto #846 (alta, 47 q) fica fora porque nenhum dia tinha 47 q livres; e há 103 pares com data invertida (prioridade menor num dia mais cedo). #5426 (0 q, sem faixa) entra em 13/10 sem gastar capacidade. Aceitável (não desloca ninguém e usa capacidade que sobraria), mas vale ser dito a ele: "fora do sprint" não é estritamente "as de menor prioridade".
(b) **Idempotência.** `montar_sprint` 2x (e com a entrada invertida) = igual. Na cópia: apply 1 = 81 linhas + 2 cortes (= 83); dry-run seguinte N = 0; apply 2 com `--expect 0` = "nada a mudar", sem 2o backup.
(c) **Backup.** Fixado depois do COUNT-ASSERT e antes do 1º write (`plano.py:1735`, antes de `cortar` em :1739); com N = 0 não grava nem faz backup.
(d) **DDL fora do `--apply`.** Pelo `--sprint` não: o dry-run e os leitores não rodam DDL. Mas `_ensure_plano_table` (que agora inclui a coluna) roda em QUALQUER writer com `aplicar` (`plano_upsert_tarefas`, ou seja, `--semear --apply`). É aditivo e idempotente, e é o padrão da spec ("como as colunas anteriores"). Não é defeito.

### Defeitos (nenhum bloqueia)
- BAIXA `tools/plano.py:1739-1741` -- apply sem transação única: `cortar` grava antes de `plano_set_dias`; se o 2o falhar, os cortes ficam (o backup cobre). O resultado final não é conferido contra o N.
- BAIXA `app/utils/db.py:2088` + `plano.py:1741` -- com `inexistentes`, `plano_set_dias` volta sem gravar e o CLI imprime "OK: 0 linha(s)" (falso sucesso; só numa corrida, porque os ids vêm do banco).
- BAIXA (dívida) -- a marca `sprint: fora` e o `dia_plano` antigo ficam numa tarefa que sai do alvo (feita, cortada por fora, movida para S>7); `mudancas_do_sprint` só toca o que o sprint decide.
- INFO `tools/plano.py:1556` -- `questoes_acertadas = 0` vira -1 (descarta a prova); irrelevante na prática.
- INFO -- tarefa de 0 q (leitura #5426) não consome capacidade.

Pronto para o `--apply` real pelo principal (`--expect 83` em 13/10).
