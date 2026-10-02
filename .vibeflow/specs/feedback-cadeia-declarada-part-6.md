# Spec: Feedback por elo declarado -- part 6: o agente confirma, não diagnostica (análise, cards, ledger)

> Escrita em 2026-10-02 (s211). PRD: `.vibeflow/prds/feedback-cadeia-declarada.md` (Proposed Solution, item 8).

## Objetivo

As normas que o agente lê no ato (skills e brief) passam a tratar a declaração do aluno como o diagnóstico; a análise do agente vira confirmação + conflito + card, e cada estado declarado tem um destino definido.

## Contexto

Hoje o tique do `/banco-emed` (passo 4) e o `/analisar-questao` §3.3 mandam o agente escrever `analises/<lista>_<num>` com `quebrou`, `estados`, `comporta`, `armadilha`, `veredito_hub` e `cards`, usando "racional e elo declarados" como insumo -- o diagnóstico é do agente e o aluno dá veredito. O PRD inverte: o aluno declara; o agente aponta conflito e cunha. Sem mudar a norma, a tela nova (parts 2-3) receberia análises no formato velho.

**Fricção que esta spec remove:** o ciclo diagnóstico do agente -> "discordo" do aluno -> análise refeita -- viciosa.

## Definition of Done

1. **Forma nova da análise** definida em UM lugar (`docs/SOLUCAO-MEDHUB-BRIEF.md` §Estado por elo, portador único) e apontada pelas skills: `analises/<lista>_<num>` = `lista`, `num`, `veredito_hub` (1-2 frases), `conflitos` (índices 0-based dos elos em que declarado e evidência divergem; vazio = sem conflito), `armadilha` (opcional, 1 linha), `cards[]`, `questao_erro_id`. `quebrou`, `estados`, `pedia` e `comporta` deixam de ser escritos (lápide). Evidência admitida para conflito: letra marcada x elo `descartar`, riscadas, certeza, grifos e racional -- nunca "a letra cai no elo".
2. **Destino de cada estado**, escrito no passo 4 do tique do `/banco-emed` e no §"Card nasce do elo": `nao` -> card de conhecimento do elo (frente = a decisão do elo, verso = a `chave`), via `insert_questao.py`/`insert_card_extra.py`; `incerteza` -> card de consolidação do mesmo elo (ou reforço de card existente do tema: buscar antes de cunhar); `desatencao` -> NENHUM card; entra no ledger com `habilidades.py --add "<habilidade>" --area ... --tema ... --veredito desatencao`; `sim` -> nada. Triagem de regenerabilidade (`/estilo-flashcard`) segue valendo antes de cunhar.
3. **Ledger aceita `desatencao`.** `python tools/habilidades.py --add "x" --area A --tema T --veredito desatencao` grava, e o `--report` o conta. Se já aceita, o teste prova; se não, o vocabulário ganha o valor (migração idempotente se houver CHECK). Teste em `tools/test_habilidades.py`: `test_veredito_desatencao_e_aceito_e_contado`.
4. **`/analisar-questao` §3.3 e `/banco-emed`** apontam o brief e NÃO redefinem o vocabulário (o teste existente `test_skill_e_autopsia_apontam_o_brief_e_nao_redefinem` segue verde, ajustado ao texto novo). Insumo do passo 4 = `emed_banco.py --erros` + `--elos` (part-5).
5. **Rito de revogação completo** (`AGENTE.md §10.10`) para "o agente declara `quebrou`/`estados`": declarar no brief, lapidar nas duas skills, registro do gate; `CONTRATO_REVOGADO` verde; `sync_skills --check` 0.
6. **Craftsmanship.** Nenhuma cláusula nova descreve sistema que não existe (cada flag citada existe e aparece no `--help`); `doc_drift` e `cli_signature_check` verdes; suíte inteira verde; português com acentos, pontuação ASCII.

## Scope

**Arquivos (5):** `docs/SOLUCAO-MEDHUB-BRIEF.md` · `.claude/commands/banco-emed.md` · `.claude/commands/analisar-questao.md` (+ espelhos) · `tools/habilidades.py` · `tools/test_habilidades.py`.

## Anti-scope

- Importar elos para o ledger em lote (`--da-lista`): o agente usa `--add` por elo; lote só se o volume pedir.
- Reescrever as 7 análises antigas do db do hub.
- Mudar `insert_questao.py`, `card_checks.py` ou o FSRS.
- Página do hub (já entregue nas parts 2-4).

## Technical Decisions

- **Norma no portador lido no ato:** a mudança é de conduta do agente; ela só existe se estiver na skill que o agente lê ao analisar (lição do F90).
- **`desatencao` sem card:** card de fato não corrige falha de execução; o ledger de habilidades é quem acumula reincidência (bug no 1 do operador: discriminador que exclui, enunciado negativo, ancoragem no número).
- **`incerteza` busca antes de cunhar:** evita clonar card do mesmo tema (o pool já tem 650 novos).

## Applicable Patterns

- `patterns/error-insertion-pipeline.md` (erro -> db -> card).
- `patterns/agent-workflow-protocol.md`; skill canônica + `sync_skills`.

## Risks

- **Norma nova e análise antiga convivendo:** a part-2 já rende o legado; o brief diz qual forma vale a partir de 02/10/2026.
- **Agente voltar a inferir** por hábito: o `--erros` (part-5) não entrega mais a inferência para v3, e a lápide está nas duas skills.

## Dependencies

- `.vibeflow/specs/feedback-cadeia-declarada-part-5.md`
