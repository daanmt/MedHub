## Audit Report: feedback-cadeia-declarada part-6 (o agente confirma, não diagnostica)

> Auditado em 2026-10-02 (s211), subagente de implementação. Spec: `.vibeflow/specs/feedback-cadeia-declarada-part-6.md`.
> Dependência: part-5 PASS (commit `4d936b0`). A corrida caiu uma vez por erro de API (HTTP 403 da organização) com a part-6
> aplicada e não commitada; retomada conferindo o `git diff` antes de seguir (nada refeito em dobro).

**Verdict: PASS**

### DoD Checklist

- [x] **1. Forma nova da análise em UM lugar.** `docs/SOLUCAO-MEDHUB-BRIEF.md` §Estado por elo: "A análise do agente CONFIRMA, não
  diagnostica" -- `lista`, `num`, `veredito_hub` (1-2 frases), `conflitos` (0-based; vazio = sem conflito), `armadilha` (opcional),
  `cards[]`, `questao_erro_id`; evidência admitida: letra marcada x `descartar`, riscadas, certeza, grifos, racional -- "nunca a letra
  cai no elo". Lápide: `quebrou`, `estados`, `pedia`, `comporta` deixam de ser escritos (legado segue lido). As duas skills apontam
  para cá (linha `analises/` de `/banco-emed`; §3.3 de `/analisar-questao`).
- [x] **2. Destino de cada estado.** `/banco-emed` §"Card nasce do elo" (lista por estado: `nao` -> card de conhecimento, frente = a
  decisão do elo, verso = `chave`, via `insert_questao.py --emed`/`insert_card_extra.py`; `incerteza` -> consolidação, buscar card do
  tema antes e preferir reforço via `recurate_cards.py`; `desatencao` -> nenhum card, `habilidades.py --add ... --veredito desatencao`;
  `sim` -> nada; triagem `/estilo-flashcard` antes de cunhar) e o passo 4 do tique (mesmos destinos + forma do doc de análise).
- [x] **3. Ledger aceita `desatencao`.** Já aceitava (`VEREDITOS`); o teste prova:
  `test_veredito_desatencao_e_aceito_e_contado` (CLI `--add ... --veredito desatencao` grava; `--report` conta `- desatencao: 1`;
  `--reincidentes` `n_desatencao == 1`), com asserts nativos (as `check()` do arquivo não derrubam o pytest). Sem migração (não há
  CHECK no schema). O uso no docstring passou a citar `desatencao`.
- [x] **4. Skills apontam o brief e não redefinem.** `test_skill_e_autopsia_apontam_o_brief_e_nao_redefinem` verde sem ajuste
  (o texto novo segue citando `SOLUCAO-MEDHUB-BRIEF.md` e "Estado por elo"). Insumo do passo 4 = `--erros` + `--elos`.
- [x] **5. Rito de revogação** de "o agente declara `quebrou`/`estados`": (1) declarado no brief (lápide), (2) lapidado nas duas
  skills (§3.3 de `/analisar-questao`; linha `analises/` e passo 4 de `/banco-emed`), (3) registrado em `docs/MEMORIA-AUDITORIA.md`
  §12 (`o elo que quebrou marcado`, ``com a cadeia, o `quebrou` (0-based)``). `CONTRATO_REVOGADO` PASSED; `sync_skills --check` 0.
- [x] **6. Craftsmanship.** Cada ferramenta/flag citada existe: `emed_banco.py --erros/--elos/--defeitos`, `habilidades.py --add
  --area --tema --veredito` (`--help` lista `desatencao`), `insert_questao.py --emed --sessao`, `insert_card_extra.py`,
  `recurate_cards.py`. `python -X utf8 tools/doc_drift.py` -> 0 achados; D5 PASSED;
  `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> **1346 passed**; `auto_check --changed` exit 0.

### Pattern Compliance

- [x] Norma no portador lido no ato (skills canônicas + `sync_skills`); vocabulário com UM portador (brief).
- [x] `patterns/error-insertion-pipeline.md`: erro -> `insert_questao.py` primeiro; `--add` complementa (F38 intacto).

### Desvios

- `AGENTE.md` §7.4 (fora da lista): a tabela GERADA por `reachability_check --tabela` mudou em duas linhas e o
  `test_consistencia_registros::test_repo_real_consistente` falhou. `tools/emed_banco.py`: +2 referenciadores, porque `/analisar-questao`
  passou a citar o `--erros`/`--elos` (mudança desta part). `tools/hub.py`: +1, vindo do `docs/DISCOVERY-AMBIENTE-AGENTICO-2026-10-02.md`
  do agente principal (não rastreado, em edição paralela). As duas linhas foram copiadas da saída do gerador; a de `hub.py` só fecha com
  esse doc presente (se ele não for commitado, a linha volta a +30).
- `docs/MEMORIA-AUDITORIA.md`: passo (3) do rito.
- `history/ledger_self.jsonl` aparece modificado pelo `auto_check` (ledger-of-self); é de `history/`, não entra no commit.

### Decisões onde a spec deixava aberto

- O destino `nao` de questão CERTA (dúvida certa com elo `nao`) vai por `insert_card_extra.py` (não há erro para `insert_questao`).
- O §3.3 de `/analisar-questao` mantém a "comporta" na página de Autópsia (artefato à parte); ela só saiu do doc `analises/` do hub.

### Critical Gate

Clean -- só texto de norma, um teste novo e o docstring do CLI.

### Não verificado

- Conduta do agente na próxima análise real (seguir os destinos por estado e não voltar a inferir): é norma, sem artefato que a registre.

14 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
