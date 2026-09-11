# Audit Report: s177 item 1.6 -- F39, a worklist de atomicidade vira fila com lifecycle

**Data:** 2026-09-11 · **HEAD base:** `b6cf807` · **Escopo:** item 1.6 da fila selada (janela 3 de engenharia)

**Veredito: PASS**

> **Razao declarada para o formato:** item de fila de divida tecnica (`docs/MEMORIA-AUDITORIA.md §11`,
> linha 1.5), sem spec em `.vibeflow/specs/`. O DoD auditado e a decomposicao da instrucao selada --
> *"269 nao-atomicos -> fila de reforja com lifecycle, sobre o B2 do 0.3; nao WARN solto"* -- declarada
> antes da execucao. A spec do B2 (`fila-de-reforja-como-estado.md`) e a base sobre a qual este item
> constroi e foi lida como fonte de padrao, nao como DoD.

## DoD Checklist

- [x] **1. O predicado de atomicidade entra no registro VERIFICAVEL, sem 2a fonte de regex.**
  `card_checks.checar_nao_atomico` **delega** a `audit_card_atomicity.checar_front/checar_verso` --
  o teste `test_predicado_esta_no_registro_e_delega_sem_copiar_regex` troca a fonte por sentinela e
  falha se houver copia. Direcao do import (biblioteca -> CLI) declarada e justificada na docstring:
  mover os regexes arrastaria `medir_verso`/`checar_ratchet_verso`, que compartilham as constantes.
- [x] **2. A worklist vira ESTADO com lifecycle, por mecanismo generico.**
  `reforja.py --ingerir MOTIVO [--apply]` opera sobre **qualquer** predicado do registro, nao so
  atomicidade. Motivo fora do registro e **recusado com exit 1** (`test_ingerir_recusa_motivo_sem_predicado`):
  marca que maquina nenhuma sabe fechar seria fila que so cresce.
- [x] **3. Escrita em lote sob a disciplina do §10.7.**
  COUNT-ASSERT declarado antes de escrever, dry-run como default, verificacao pos-escrita
  (`escritas != len(novos)` -> exit 1). Backup do `ipub.db` tirado antes do `--apply`
  (`artifacts/backups/ipub_backup_20260911_090929.db`). Medido no real: **270 declaradas, 270 escritas**.
- [x] **4. Idempotente, e a idempotencia esta testada nos tres estados.**
  2a passada sobre o dado real declara **0 a criar** (270 em `ja ABERTAS`). Par com marca ABERTA nao
  recebe outra (re-marcar inflaria `n_marcacoes`, cujo significado e "marcado de novo e ninguem
  tocou"); **descartada** nao e reaberta (apagaria o veredito humano a cada varredura); **fechada que
  ainda acusa** e **reportada, nao re-marcada** (classe F82 -- reabrir sozinho esconderia o
  fechamento que nao valeu). Um teste por estado.
- [x] **5. O falso-positivo DECLARADO do detector e tratado pelo lifecycle, nao maquiado.**
  Card discriminador dispara `duplo-ask` e e legitimo (regra 5). Como o predicado nunca para de
  disparar nele, `--fechar` **sempre** recusa e o desfecho e `--descartar` com justificativa --
  estado diferente de "resolvi", que mantem o passivo honesto. Os dois lados tem teste
  (`test_discriminador_nao_fecha_por_fechar_e_fecha_por_descartar`), com fixture **verbatim do #857**.
- [x] **6. O WARN deixa de ser solto.**
  `auto_check` passa a imprimir `Na fila de reforja: N · FORA dela: M` -- **M** e o numero acionavel,
  e cai quando alguem tria; o total, nao. Degradacao graciosa se a fila estiver indisponivel
  (try/except, WARN nunca bloqueia). Verificado: `270 · FORA dela: 0`.
- [x] **7. Assinatura canonica e paridade command<->skill.**
  `--ingerir` e `--limit` documentados em `.claude/commands/estilo-flashcard.md` (§7.2: a assinatura
  vive em UMA skill); `sync_skills.py` rodado e `--check` **exit 0** no mesmo commit (§10.3).
- [x] **8. Suite verde e harness aprovado.**
  `pytest -q` -> **594 passed** (583 -> 594). `auto_check --changed` e `--all` -> **PASSED**.

## Pattern Compliance

- [x] **Predicado unico, nunca copiado** (licao 1.1/F79b): a delegacao e o mecanismo, e ha teste que
  a prova. Evidencia: `tools/card_checks.py::checar_nao_atomico`.
- [x] **Sensors (WARN-first) -- `.vibeflow/conventions.md`:** o sensor continua sem corrigir e sem
  bloquear; o que mudou e que ele agora aponta para onde a decisao humana e gravada.
- [x] **Db access layer:** a varredura entrou como `db.cards_ativos_para_predicado()`, read-only, no
  mesmo shape de `_card_para_predicado` -- com teste de igualdade de shape, porque varredura e
  re-verificacao lendo campos diferentes do mesmo card e como um gate passa a mentir. Nenhum
  `sqlite3` novo fora de `db.py`; `reforja.py` segue camada fina.
- [x] **Operacao em massa (`AGENTE.md §10.7`):** COUNT-ASSERT + dry-run escritos ANTES, backup antes
  do apply, verificacao depois.
- [x] **Ritual de revogacao em 3 passos (`AGENTE.md §10.10`):** ver secao propria abaixo.
- [x] **Fixture real em vez de sintetica quando existe:** o discriminador do teste e verbatim do
  corpus (#857), na linha do que `test_reforja_marks` fez com #1568/#792.

## Revogacao de clausula -- os 3 passos, no mesmo commit

A clausula *"**Um WARN dos predicados NAO vira marca sozinho.** O CLI oferece candidatos; quem marca
e gente"* (`estilo-flashcard.md`, licao do F87) e **contradita na letra** por `--ingerir`. Tratada
como revogacao, nao como reinterpretacao silenciosa:

1. **Declarada** -- no ledger (fechamento do F39) e no §11.
2. **Lapidada no portador que o agente le** -- `⚰️` com data, motivo e a redacao antiga preservada em
   `.claude/commands/estilo-flashcard.md`, substituida por *"marca e CANDIDATO; veredito e humano"*:
   a porta de **entrada** abriu, a de **saida** continua sendo gente, e a licao do F87 fica escrita
   inteira (o harness mede forma, nao rendimento).
3. **Cadastrada** -- `"NÃO vira marca sozinho"` em `_TERMOS_REVOGADOS` **e**
   `.claude/commands/estilo-flashcard.md` em `_PORTADORES_NORMA`. Cadastrar o termo sem cadastrar o
   portador repetiria o **F95** (registro alimentado, arquivo fora da varredura, gate verde com
   clausula morta em vigor). **Provado, nao presumido:** com a frase plantada numa linha ativa o
   gate acusou `('.claude/commands/estilo-flashcard.md', 341, 'prescricao', ...)`; restaurado o
   arquivo, `check_contrato_revogado()` volta a `[]`. Colisao com os 9 termos ja registrados foi
   medida antes de incluir o portador: **zero**.

## Convention Violations

Nenhuma.

## Critical Gate

Clean -- nenhuma regra do catalogo casa o diff (`git diff HEAD`).
Nota INFO, para o registro: o item introduz um caminho de **escrita em lote** no `ipub.db`
(`--ingerir --apply`, 270 linhas nesta execucao). Nao e operacao destrutiva -- e `INSERT`
append-only em `reforja_marks`, sem `UPDATE`/`DELETE`, sem tocar conteudo de card, com COUNT-ASSERT,
dry-run default e backup previo. Registrado aqui porque volume nao dispensa a declaracao.

## Limites DECLARADOS (nao maquiados)

1. **O item nao reforja um unico card.** Entrega **onde** registrar o veredito; o conserto e
   curadoria de conteudo e e do OPERADOR (regua de "card bom" = F87, Tier 2). O passivo so cai
   quando alguem triar -- e agora ele *pode* cair, que era o que faltava.
2. **Divergencia G7 viva, declarada:** `ledger_self` conta **265** `card_atomicidade` abertos
   enquanto a fila conta **270** -- dois registros da mesma pergunta no mesmo relatorio. Medem
   coisas diferentes (ocorrencia de WARN x triagem) e nenhum rotulo diz isso. Adicionado a
   **varredura unica (1.8)** como CHECK de **rotulo**, nao de igualdade.
3. **A cifra citavel saltou de 2 para 272 abertas.** E o numero honesto (o WARN ja dizia 270), mas e
   uma mudanca grande num numero que o operador le -- declarada no checkpoint, nao escondida no
   commit. O `--fila` ganhou resumo por motivo e corte no detalhe para a cifra nao voltar a ser
   "role a tela e conte".
4. **Nenhuma porta de desfazer em lote.** Um `--ingerir` errado sai por 270 `--descartar`. Nao foi
   construida porque `--descartar` **exige justificativa por linha** -- e um desfazer em lote seria
   exatamente o gesto que a fila existe para impedir (apagar veredito sem palavra humana). O que
   torna o risco aceitavel: a ingestao e **derivada** (regeneravel do detector) e **idempotente**.
5. **A precisao do detector nao foi re-medida neste item.** Os 270 herdam a calibracao da s128 (dois
   guardas, 220 -> 203 em duplo-ask) e a classe de falso-positivo declarada. Medir precisao card a
   card e triagem de conteudo -- do operador, nao deste item.

---

12 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
