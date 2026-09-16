# Notas de implementacao -- plano-ssot-e-cards-v2-part-3

Coding Agent, 2026-09-16. Relatorio completo no handback ao orquestrador.
Nenhuma mutacao no `ipub.db` real (896 linhas / 173 `dashboard_2026-09-10` / 1
`atualizado_em` distinto, conferido depois de todos os comandos).

## Divergencias da instrucao (declaradas, nao corrigidas por conta propria)

1. **TRES writers em `db.py`, nao dois.** O Scope da spec diz "2 writers + leitor".
   O lote da `--confirmar-area` precisa de UMA transacao (carimbo da area inteira +
   os dois lotes de status) e a regra dura e que toda escrita mora em `db.py`:
   compor o lote em `plano.py` a partir de N `plano_set_status` gastaria N commits e
   perderia a atomicidade. Entao ha `plano_set_status`, `plano_mover` e
   `plano_confirmar_area`. Os dois nomeados pelo DoD 1 existem com a assinatura pedida.

2. **`--sessao N` e o `id` da linha em `sessoes_bulk`, nao o `sessao_num`.** O DoD diz
   `sessao_bulk_id=N`, e a coluna e essa. Mas os dois numeros divergem no banco real
   (id 126 = `sessao_num` 175), entao o erro e provavel: o CLI ECOA area/data/questoes
   da sessao casada no sucesso, e a recusa nomeia a confusao. Gate no writer tambem,
   nao so no CLI -- nenhum caller escapa.

3. **`origem_conclusao` passa a ser escrita em QUALQUER status.** Ate a part-2 so linha
   `feita` levava carimbo (as outras nasciam NULL). A conferencia por area exige
   carimbar quem NAO mudou de status, senao a pendencia nunca chega a zero. A coluna
   passa a responder "quem afirmou este status". Declarado em `db.ORIGEM_USUARIO`,
   na skill e aqui.

4. **`N` do `--expect` = a AREA INTEIRA.** Nao so as linhas que mudam de status --
   todas sao tocadas (`origem_conclusao` + `atualizado_em`). Preventiva real = 115.
   Efeito colateral bom: o N e idempotente (reconfirmar a area da o mesmo numero).

5. **Motivo do `--cortar` vai para `nota`, e `nota` esta em `CAMPOS_SEMEADOS`.** Um
   `--semear --apply` futuro reescreve a nota e o motivo se perde (o
   `status='cortada'` sobrevive -- esse fica fora do UPDATE). Nao inventei coluna nova
   para uma parte que nao a pediu; divida declarada na skill. `compor_nota_corte` e
   funcao pura: ANEXA (preserva `q_estimada`/`area_fonte=`) e corte repetido
   SUBSTITUI o motivo anterior em vez de empilhar.

6. **`--mover` com `--ordem` omitida PRESERVA a ordem** (inclusive NULL). Mover nao
   toca `status` nem `origem_conclusao`: replanejar nao e confirmar.

7. **`--reabrir` APAGA `data_conclusao`/`sessao_bulk_id`** e carimba `usuario`. Trilha
   orfa apontando para uma conclusao que o usuario acabou de negar seria pior que nada.
   Ja `--confirmar-area --feitas` NAO apaga o vinculo de um `--concluir` anterior: o
   lote e retro-confirmacao, e vincular sessao e a part-6.

8. **`--revisar-area` ordena pela FONTE**, nao pela semana do plano: a conferencia e
   feita contra o Dashboard/PDF, que estao nessa ordem.

## Decisoes de craftsmanship

- **`tools/plano.py` continua sem escrever nada.** `test_writer_allowlist` verde sem
  tocar a allowlist -- o scanner nao ve SQL de escrita no CLI.
- **Um modo por invocacao.** `main()` conta os 9 modos e recusa (exit 2) com a lista
  dos ligados. Substituiu o `if args.semear == args.listar`.
- **Recusa nomeia motivo E comando corretivo** (DoD 5), em todos os caminhos:
  sessao fantasma, id inexistente, id fora da area, id nos dois lados, `--expect`
  errado, data malformada, area fora do vocabulario, semana < 1.
- **Sem flag nova onde a existente serve**: `--semana` (filtro do `--listar`) vira o
  destino do `--mover`; `--json` passa a servir tambem o `--pendencia-revisao`;
  `--dry-run`/`--apply`/`--expect` sao os mesmos do `--semear`.
- **`plano_listar` ganhou `area=`** (filtro em SQL) em vez de filtrar em Python.

## Pendencias que NAO podia executar (fora do escopo de arquivos)

Duas suites do repo ficaram vermelhas POR CAUSA desta parte -- as duas verdes de novo
com um comando cada, que a instrucao me proibiu:

- `python tools/sync_skills.py` -- espelho de `engenharia-cli` stale
  (`test_espelho_gerado`). Eu editei o canonico `.claude/commands/engenharia-cli.md`.
- `python tools/reachability_check.py --tabela` + colar em `AGENTE.md` secao 7.4 --
  a tabela gerada envelheceu porque os referenciadores de `plano.py`,
  `registrar_sessao_bulk.py`, `day_plan.py` e `init_db.py` mudaram de contagem
  (`test_consistencia_registros::test_repo_real_consistente`). `AGENTE.md` nao esta
  na minha lista de arquivos.

Verificado por `git stash`: as duas passavam antes do meu diff.

- `pytest.ini` NAO precisa mudar: `test_plano.py` ja esta em `python_files` (o gate
  F43 do `auto_check` passa).
- `history/ledger_self.jsonl` levou 2 linhas append-only ao rodar
  `auto_check --changed` (gate obrigatorio): sao os `opened` das duas pendencias
  acima. Evidencia honesta -- nao apaguei (AGENTE secao 10.2).
- A passada real de revisao (`--confirmar-area --apply`) e o commit sao atos do
  orquestrador com o usuario.
