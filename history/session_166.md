# Session 166 -- Bloco 1 drenado (62 cards) + engenharia curta: README, 2 hotfixes, drift F75
**Data:** 2026-09-05 (noite) -> 2026-09-06 (tarde) -- sessao cruzou a meia-noite; o estudo (cards) foi majoritariamente em 06/09
**Ferramenta:** Claude Code (Fable 5.1) -- effort max; 2 subagentes (Opus: README; Sonnet: drift)
**Continuidade:** Sessao 165 (Claude Code / Fable 5.1)

---

## O que aconteceu

### Estudo -- DRENAR, bloco 1 (62 cards, regra do sprint 120/dia s165)
1. **Boot** limpo (nada BLOCKING; Drive 41d sem sync = W8 conhecido). Fila: 57 atrasados + 52 hoje + 8 fresh do S6; 54 do redrill ja vencidos.
2. **Sub-bloco 1.1 (15):** Epilepsias 11 (redrill s164, 27%) + TCE #540 (3a passagem) + #4, #244, #245. Tronco D5 comprimido (familia "ABC antes do neuro", classificacao, West/Lennox, EME). Resultado 10x4 / 4x3 / 1x1. Epilepsias 11/11 no nucleo; #788/#789/#540 (familia ABC) cairam pela 1a vez em 4 passagens. #245 reforjado a pedido (frente circular -> janela do Kasai < 60d).
3. **Sub-bloco 1.2 (15):** Vulvovaginites 9 + Ulceras 3 + Planejamento 3. Tronco D10 no mecanismo (estrogenio -> glicogenio -> lactobacilo -> pH; barreira em pe x caida; especiais; locus antes de agente); `review_log` 113. Resultado 9x4 / 1x3 / 2x2 / 3x1. #744 (atrofia, fraqueza nº 6) caiu. Lacunas: #740 (tirou azitromicina; Thayer-Martin negativo tira o ceftriaxone), #1478 (Gram do cancro mole). #667 = padrao-mestre em faceta nova (ancorou na cor acinzentada + odor, ignorou o prurido que EXCLUI vaginose); reforjado com pH/aminas/hiperemia. #741 reforjado (vinheta real, par contrastante). #577 reforjado (regra tinha erro "primaria = anovulacao"; banca-dependente registrado).
4. **Sub-bloco 1.3 (16):** Colecistite 6 + Apendicite 5 + `[bulk]` 3 + Polipos 2. Tronco D10 (escada biliar = uma doenca mudando de andar; "quem manda no timing"; investigacao; apendicite como corrida contra a perfuracao); `review_log` 114/115. Resultado 10x4 / 1x3 / 1x2 / 4x1. #1089 (timing pancreatite, fraqueza nº 7) caiu. **Erro repetido:** #1381 alitiasica (fechou pelo cenario, pulou Tokyo A+B, igual a s164). #736 2a queda. #311/#313 clones confirmados (mesma resposta aos dois) -> reforjados com frentes distintas.
5. **Sub-bloco 1.4 (16 singletons GO/Ped/Prev/Reumato):** 11x4 / 2x3 / 3x1. **Erro repetido:** #1270 AGC (colposcopia no lugar da avaliacao endometrial = USGTV). #1473 (VNI: pre-requisito e consciencia/drive, nao hipoxemia), #1474 (MgSO4 > 2 anos). SUS/universalidade (fraqueza nº 4), ectopica x2, DTG com mecanismo, idade ossea x2: ok.
6. **Redrill dos 1-2 (13, pela frente, sem gravar):** 11 sairam; ficam #245 (Kasai) e #741 (respondeu a flora AEROBIA do card vizinho #1444 -- par novo a fixar: aminas + = anaerobio/vaginose; aminas - = aerobia). #709: conduta certa, mas "obstrucao = Hartmann" e regra de colon, reto deriva.
7. **Totais do bloco 1: 62 cards, 40x4 / 8x3 / 3x2 / 11x1 = 77% retencao, 65% perfeito** (s164: 54% / 43%). Dos 11 "1": 2 erros repetidos (#1381, #1270), 2 defeitos de card (#245, #741), 7 lacunas limpas. Zero questoes nos 2 dias (o usuario fez o Simulado 7 fora da sessao, em 06/09).
8. **Decisao do usuario para a s167:** 90 cards a noite de 06/09 (matar a fila do dia + novos por prevalencia); receber o Simulado 7 primeiro. Minha proposta inicial (bloco 2 de 40 so divida) foi redirecionada: "aumentar os flashcards ajuda a tocar temas prevalentes e hibernantes".

### Engenharia (pedido do usuario: "inconsistencias no seu motor", README defasado)
9. **Orquestracao:** 2 subagentes em paralelo (Opus: README verificado afirmacao-a-afirmacao; Sonnet: varredura de drift doc-vs-codigo com `--help` de 16 CLIs), eu no hotfix + ledger + fechamento.
10. **Hotfix F70** (vibeflow:hotfix): `[FSRS_BALANCE]`/`[WARN]` do balanceador iam para stdout e quebravam o JSON do `fsrs_queue --record` (3 de 14 records do 1.1 falharam no `json.load`; gravacao persistia). `file=sys.stderr` nos 2 sitios; `tools/test_fsrs_balance_stdout.py` vermelho -> verde; conferido read-only no banco real.
11. **Hotfix F73:** `cronograma.py --check` (W5) morria em `FileNotFoundError` -- PDF em `data/`, codigo na raiz. `resolve_pdf_path()` (raiz -> `data/`), `check()` degrada p/ `missing_pdf`; `tools/test_cronograma_pdf_path.py`; skill `/cronograma` + espelho. `--check` real: `fresh`.
12. **README.md reescrito** (210 linhas, ASCII): agent-first, py-fsrs + balanceador, RAG gold-only com fallback lexical, harness (365 testes), contratos/skills/workflows, SSOTs, como rodar, limitacoes honestas. 30 afirmacoes obsoletas removidas (F74).
13. **Varredura de drift (F75):** 12 achados (6 ALTA). Corrigidos na hora: D1 excecao do sprint no `fsrs-management-contract`; D2 tabela §7.4 regenerada pelo gerador; D3 enum `veredito` (5 valores) em `analisar-questao.md`; D4 clausula no §7.2 (protocolo cognitivo numerado e permitido; orquestracao de CLI nao); D6 `--sync-drive` em `cronograma.md`, `--pre-bloco`/`--janela-horas` em `revisar.md`; D7 AGENTS.md (contagem de gates); D8 workflow `registrar-sessao` (nao escrever "Ultimas sessoes" no ESTADO); D9/D12 ROADMAP (numeros do eval; Streamlit FEITO); D10 `.vibeflow/index.md`. Abertos: D5 (skills `day-plan`/`curar-cards`), D11 (escopo do `doc_drift`).
14. **Ledger:** F70-F75 + evidencias novas p/ F40 (9 defeitos de card em 62 = 14,5%), F65 (#297 EM em `[bulk] Cirurgia`), F67 (pares duplicados vistos no `--cluster`), F71 (balanceador empurrou #381/#823 de 13/09 p/ 14/09, dia seguinte a prova), F72 (day_plan recomenda tema de snapshot que ele mesmo declara stale -- a contradicao que o usuario apontou).
15. `auto_check --all` e `--changed` PASSED; `sync_skills --check` OK.

## Padroes de erro (estudo)
- **Padrao-mestre (ancorar no saliente, ignorar o que exclui)** em 3 cards: #667 (cor/odor x prurido), #1381 (cenario x Tokyo A+B, repetido), #1475 (mioma x endometrio 8 mm -- este acertou).
- **Fato do vizinho no contexto errado:** #741 redrill (aerobia x anaerobia), #1270 (colposcopia x endometrio, repetido), #577 (combinado x SIU).
- **Pergunta composta, para na 1a metade:** #4 (adrenalina sem concentracao).
- **Categoria/framework no lugar do ato:** #709 (neoadjuvancia x colostomia em alca), #1473 (indicacao x pre-requisito).

## Artefatos
- Codigo: `app/utils/db.py`, `tools/cronograma.py`, `tools/test_fsrs_balance_stdout.py` (novo), `tools/test_cronograma_pdf_path.py` (novo), `pytest.ini`.
- Docs: `README.md` (reescrito), `AGENTE.md` (§7.2 clausula, §7.4 regenerada), `AGENTS.md`, `ROADMAP.md`, `ESTADO.md`, `HANDOFF.md`, `AUDITORIA_MEDHUB.md` (§4p: F70-F75), `core/contracts/fsrs-management-contract.md`, `.agents/workflows/registrar-sessao.md`, `.vibeflow/index.md`, `.vibeflow/hotfixes/2026-09-06-{fsrs-balance-stdout,cronograma-pdf-path}.md`.
- Skills + espelhos: `analisar-questao.md`, `cronograma.md`, `revisar.md` (+ `.agents/skills/source-command-*`).
- Banco (local): 62 revlogs; 5 cards reforjados (v+1); `review_log` 113-115.

## Decisoes
- Sprint 120/dia ate 13/09 ganhou ponteiro no contrato FSRS (excecao datada, expira 14/09).
- §7.2 do AGENTE: protocolo cognitivo numerado em skill e permitido; orquestracao de CLI segue so no workflow.
- Reforja in-place (id + FSRS preservados) > merge de cards vizinhos: #667/#741 viraram par contrastante em vez de um card composto.
- Cards com nota 1-2 que voltam ao `--list` no mesmo dia nao sao regravados (1 record por card por sessao); o CLI ainda nao distingue (candidato de DIVIDA "mecanizar o redrill").

## Proximos passos
Ver `HANDOFF.md`: Simulado 7 (registrar + autopsia) -> 90 cards a noite (fila do dia + Cirurgia Infantil com tronco D10) -> cunhagem fraco-primeiro -> S17 roxos. Engenharia: F71, F72, D5, D11.
