# PRD: Des-colar o motor — o passo load-bearing acontece ou PARA ruidosamente, em qualquer IDE

> Gerado via /vibeflow:discover em 2026-09-01 (modo autônomo delegado; discovery = `ai-eng/HANDOFF-MEDHUB-COLA.md` [s160, dossiê F45-F60 com âncoras verificadas 30/08 no HEAD `9e3785a`] + `AUDITORIA_MEDHUB.md §3o` [tabela, matriz de portadores, swap test] + tese-mãe `ai-eng/HANDOFF-AUDITORIA-PERICIA.md` Parte I — que não se re-litiga).
> Âncoras do brain (ai-eng): `arxiv-codeact`/`web-agent-evals` (código como interface; migração de modelo = A/B com regressão), `aieng-book-ch02` (structured output), `law-contracts-geis` (definiteness — contrato que declara BLOCKING sem teste é promessa, não lei), papers validados 2026-09-01 em `ai-eng/brain/research/`: *LLM-as-Code* ("a stronger model reduces the per-step error without eliminating its compounding"), *What makes a harness a harness* (T4: "eficácia que não depende de o modelo escolher cooperar"), *Code as Agent Harness* (verification stack: cada gate declara o que verifica E o que não verifica).

## Problem

O MedHub tem **duas dívidas simultâneas que se alimentam** (handoff §1):

**Ponta A** — o modelo tapa gaps determinísticos em silêncio: writer gates são prosa (F49: 5 arquivos violam a cláusula do `AGENTE.md:170`, e `test_writer_gates.py` testa OUTRA coisa); qualquer nota persistida vira soberana na calibragem (F47: `dificuldade_fonte`/`_at` nunca decidem — Cláusulas 2/7 do contrato sem implementação); o contrato declara B2 BLOCKING e o código faz WARN com `success=True` (F56). O swap test s156-s158 (Antigravity/Gemini) mediu o custo: **5 divergências estruturais, todas classe 2/3, NENHUMA travou ruidosamente** — inclusive a deleção do alvo de uma memória-CONTRATO invisível (F57→F50: 852 linhas mortas-que-parecem-vivas por 5 dias).

**Ponta B** — o harness cresce mais rápido que a capacidade de consumi-lo: **342 WARNs num run verde**; ledger-of-self com **279 achados abertos, o mesmo WARN visto 102× em 36 dias, zero leitores em código** (F54); e o `tools/reflect.py` que o próprio ai-eng construiu morreu na lista-de-morte da consolidação com 0 refs — *um mecanismo do arquiteto morreu da doença que este PRD trata*. Adicionar sensor sem leitor é fabricar a próxima camada de ruído com carimbo.

Consequência: as propostas F45-F60 da s160 são **hipóteses enviesadas para a Ponta A** ("adicione um check") e este PRD as julga uma a uma — para vários achados a resposta é REMOVER superfície, não somar.

## Target Audience

- **O agente de estudo** (qualquer IDE/modelo — Claude Code hoje; Antigravity/Codex no swap): o registro, a precedência, o carimbo e o escopo de escrita acontecem por código, não por leitura voluntária de prosa.
- **O operador (Daniel)**: abre a sessão com o ranking de fraquezas CERTO (F45/F47 corrompem o input do boot hoje) e UM painel de dívida em vez de 6 superfícies sem leitor.
- **O ai-eng**: o medhub vira o segundo plugue dos padrões (Deterministic-Scaffold; painel-de-dívida) que depois voltam para o próprio arquiteto.

## Decisões do discovery — as 7 perguntas de política (P1-P7) respondidas

- **P1 (orçamento do harness):** SLO informativo, não gate: `auto_check` passa a IMPRIMIR o tempo por bloco e o total; a dupla execução real (test_revisao_calibrada e test_autonomia_hooks rodam 2× no mesmo run — direto + via pytest/bridge) é eliminada (**F61**, achado novo deste discovery). Bloquear por tempo seria gate flaky (anti-T4); medir e podar é engenharia.
- **P2 (catraca):** a política já existe ("regra nasce WARN, bloqueia quando a base zera", s106/107) — o que falta é o CONSUMIDOR que faz a base zerar. Decisão: construir o consumo (painel, F54) e NÃO construir promoção automática WARN→BLOCK neste ciclo (um BLOCK que ninguém pactuou vira ack-por-hábito — a corrosão A11/A19 do irmão). Aposentadoria de sensor: sensor sem leitor há N sessões entra no próprio painel como candidato a morte.
- **P3 (portador canônico por família):** adotar os vereditos da s160 (§Entregável-2): conduta do `/revisar` → skill versionada (+ redrill vira código); aula-base → contrato versionado + gate barato; padrões de erro do usuário → DADO (`weak_areas` como SSOT único — conecta F45); números → constante+teste; flashcards → régua em `estilo-flashcard.md` + ponteiros; processo → `AGENTE.md`/workflows. Memória de harness que sobrar = ponteiro + porquê, nunca a regra.
- **P4 (fronteira modelo/código DESTE repo):** o critério não é "headless com modelo fraco" (o MedHub é interativo por design) — é **"o passo load-bearing acontece ou PARA ruidosamente, em qualquer IDE"**. Legitimamente discricionário (fica com o modelo): didática, tom, profundidade, escolha de exemplo clínico. Nunca discricionário (vira código/gate/teste/schema): registro, precedência, carimbo, escopo de escrita, encoding, exit code.
- **P5 (painel único):** SIM — um consumidor no fim do `auto_check` (e ecoado no boot) imprime o TOPO da dívida: top-N do ledger (idade × ocorrências), tail do `memory_errors.log`, contagem do reachability, delta de tamanho da AUDITORIA. Os 6 produtores continuam; passa a existir UM leitor obrigatório.
- **P6 (golden do output de estudo):** LACUNA DECLARADA E FECHADA neste ciclo — criar ratchet de aula-base exige homologação do operador (custo de tempo de estudo em ano de ENAMED). Pendência nomeada para depois da prova (13/09): 5 aulas homologadas como semente. Nenhuma spec agora.
- **P7 (co-edição):** a disciplina existente vira seção curta versionada no `AGENTE.md` (família "processo" do P3); mecanizar (locks/guards) = não construir — dois agentes disciplinados + git resolvem.

## Proposed Solution (7 frentes → specs)

1. **Painel de dívida + consumo do ledger** (F54 · P5 · P1/F61 · F46-log): `auto_check` ganha bloco `DÍVIDA` no fim de todo run (top-N `ledger_self` por idade×ocorrências, tail de `memory_errors.log`, reachability count); dupla execução de suites eliminada; tempo por bloco impresso.
2. **Escopo de escrita vira teste** (F49 · blinda F51 e F52b): teste estático allowlist tabela→writers (grep INSERT/UPDATE/DELETE sobre tools/+app/, padrão já provado em `test_revisao_calibrada.py:127-149`); **F51 morre** (aposentar `auto_recurate_duplo_ask.py`: 0 refs, dep fantasma, bypassa card_checks — lápide no lugar); **F50 morre** (deletar `autopsia_simulados.py`, 852 linhas quebradas, 0 refs) + **import-check (`compileall`) dos CLIs no auto_check** — mata a classe "morto-que-parece-vivo".
3. **O input do boot fica verdadeiro** (F47 + F45 + F46-path): precedência de fonte na calibragem (input do usuário > pergunta > inferência; frescor 7d re-infere) com teste de precedência; `WeakArea.area` validado contra a taxonomia real + upsert por par (fim das 109 duplicatas / ranking por recência); paths de memória por `__file__` + leitores `mode=ro` (fim dos bancos-fantasma).
4. **Contrato só afirma o que um teste prova** (F56 + F53 + F52): B2 vira BLOCK real OU o contrato é re-ratificado com o rebaixamento EXPLÍCITO (definiteness — nunca a mentira); matriz condição→instrumento no reconcile-contract; `render_handoff_block` deriva a frente "Erros & Cards" (números derivados, não digitados); contrato FSRS absorve o balanceador (params estáveis) + check `needs_qualitative=1` + `state=3` no vocabulário.
5. **RAG com sensores** (F48): staleness do índice (mtime resumos × chroma) vira check; HyDE ganha `timeout` + `temperature=0`; upsert deleta a cauda quando o resumo encolhe; `_chunk_by_headers` ganha teste (76L puras, 0 testes hoje).
6. **Exit codes e integridade de escrita** (F60 + F58): exit simétrico nos writers críticos (`backup_db` "CORROMPIDO"→exit≠0; `importar_sessoes` 100% rejeitado→exit≠0; padrão F27 generalizado); `[WARN]` impresso nas degradações do day_plan; check de encoding/estrutura mínima de `history/session_NNN.md` novo.
7. **Portadores: migração das memórias + higiene do harness** (F57 + F59 + P7): famílias migradas por veredito P3 (regra load-bearing → portador repo; memória vira ponteiro); 2 memórias fora do índice reconciliadas (1 regra ativa invisível, 1 morta deletada); check barato: paths `tools/*.py` citados em `memory/*.md` × disco; `settings.local.json` ganha bloco deny mínimo (rm -rf, git reset --hard, push --force, git clean) + poda das entradas mortas; disciplina de co-edição versionada no `AGENTE.md`.

## Success Criteria

1. Suite pytest do medhub verde antes e depois de cada spec; `auto_check --all` sem NENHUM check rodado 2× (medido pelo tempo impresso).
2. O run do `auto_check` termina com o bloco `DÍVIDA` (top-N + idade); `ledger_self.abertos()` ganha ≥1 chamador em código.
3. Teste allowlist tabela→writers FALHA se um writer novo tocar tabela fora da lista (sabotagem verificada) — e passa hoje só com os writers declarados.
4. `python -m compileall` (ou equivalente) dos CLIs roda no auto_check: reintroduzir um import dangling = check vermelho no mesmo commit.
5. Calibragem: teste de precedência input>pergunta>inferência passa; boot ranqueia por `error_count` real (não recência) com vocabulário validado.
6. Zero contrato afirmando BLOCKING sem teste-espelho (F56/F53): ou o código sobe, ou o contrato desce — com changelog.
7. Craftsmanship: zero violação das convenções (db só via `db.py`, sensores WARN-first detectam-não-corrigem, espelhos nunca editados à mão, encoding ASCII em session logs); F1-F60 NÃO renumerados (novo = F61+).

## Scope v0

As 7 frentes acima (≈7 specs, budget ≤6 files cada). Ordem de execução = ordem das frentes (F54 é upstream de tudo; o painel primeiro evita que cada conserto vire o próximo WARN dormido).

## Anti-scope

- **Promoção automática WARN→BLOCK** (P2 — a política existente decide, com base zerada; automação = ciclo 2 com dados do painel).
- **Golden-set de aula-base/card** (P6 — pendência nomeada pós-ENAMED 13/09).
- **F55** (validar o índice staged via stash/worktree — mecânica frágil no Windows; ciclo 2 com desenho próprio).
- **Reescrever `auto_recurate_duplo_ask`** sob card_checks — morre sem substituto (renasce por demanda real, sob gate).
- **Rotação/higiene da AUDITORIA_MEDHUB.md** (99→115KB) — política de ledger é decisão do dono do doc; registrada como candidata F62 no painel, sem spec.
- **`ipub.db` intocado** sem o operador no loop (F37-dado-histórico segue pendente com ele); zero mudança de schema de dados clínicos.
- **Funções-monstro** (auto_check.main 488L, insert_questao 198L) — refactor sem mudança de comportamento fica p/ quando um fix os tocar.
- **Conteúdo clínico**: nenhum resumo, card ou taxonomia MÉDICA alterada por este ciclo (fronteira dura; conteúdo = dado que as estruturas transportam).

## Technical Context

- Budget ≤6 files/task (`.vibeflow/index.md`); pt-BR; testes registrados em `pytest.ini::python_files`.
- Padrões a seguir: `warn-first-check.md` (sensores detectam, não corrigem; WARN-first), `db-access-layer.md` (sqlite3 só em `db.py`), `agent-workflow-protocol.md`; espelhos `.agents/skills/` são build artifacts (`sync_skills.py`).
- Âncoras de código verificadas pela s160 (30/08) e ZERO commits de código desde então (só o doc da auditoria) — as âncoras valem; ainda assim, `git log --oneline -- <arquivo>` antes de specar cada alvo (regra de vigência do handoff).
- O que está sólido e NÃO se toca sem motivo: suite 317/~65s; lock otimista FSRS; watermark de dado; ordem destrutiva do backup_db; eval do RAG honesto; reachability/suites_orfas; densidade de rationale.

## Open Questions

Nenhuma bloqueante. Três pendências nomeadas fora do ciclo: (1) golden de aula-base pós-ENAMED (P6); (2) decisão do operador sobre F37-dado-histórico; (3) política de rotação da AUDITORIA (F62 candidata, dono decide).
