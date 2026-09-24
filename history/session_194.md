# Session 194 -- Hub gravado (220 cards), Hernias #38 analisada, hub V4 (painel auditado + quadro de aulas) e o /hub-backend

**Data:** 2026-09-23 (drill do hub 22/09 23h22 -> 23/09 16h32; sessao ~17h-19h30, horario local) - **Ferramenta:** Claude Code (Opus 5.5 1M; 5 subagentes: 2 executores Opus de engenharia, 1 auditor Opus, 1 verificador de evidencia Sonnet) - **Continuidade:** `session_193.md`

---

## O que foi feito
- **hub: 170 validas gravadas · 0 rejeitadas · 0 FORA DE ORDEM · 50 defeitos marcados (origem `player`)** -- colecao `sessoes/2026-09-22h/notas` (220 docs), `--record-lote` dry-run -> `--apply --expect 170` (COUNT-ASSERT batido). Sem quarentena. Releitura as ~18h15 = 0 novas (poda da colecao liberada para o proximo fechamento de cards).
- Distribuicao das 170: nota 4 = 124 · 3 = 22 · 2 = 7 · 1 = 17. Nota 1-2 = 24 cards em 20 temas; unico cluster = Nefro (Potassio #783/#787, Acido-Base #595/#598 -- a dificuldade DECLARADA de novo). Observacao passada a ele: 73% de notas 4 sob a regua v2 (4 = "sem esforco", raro).
- **Defeitos (50):** portugues ~33, composta/dupla ~13, longo ~6, circular 3, verso incompleto 1, armadilha com alternativa inexistente 1 -> ledger **F129**. Armadilhas dos 8 cards da Autopsia UERJ 2023 (#1721-1728) refeitas no ato (`recurate_cards.py`, v1->v2, FSRS preservado).
- DoD 2 da parte 4 do hub (1 aula aberta no meio do drill): ele "nao se recorda, acredita que sim" e diz que as aulas "estao funcionando bem" -- declarado, NAO medido.
- **Bloco Hernias #38:** 25q / 21 (84%) -> `sessoes_bulk.id=131`, tarefa #38 FEITA. Solidas 18/25 (3 acertos na duvida -> `habilidades.py --add --veredito incerteza`, #3894-#3896, todos anatomia inguinal). 4 erros em `questoes_erros`, cards #1729-#1733.
- **Botao "Pedir mais cards"** (`comments.sendToClaude`, 1a opcao dele): barrado pelo classificador do modo auto ("Create Unsafe Agents"). Nao contornado; patch em `tmp/patch_s194_pedido_cards.diff` (fora do git). Substituto decidido com ele: `/loop 20m /hub-backend` numa sessao aberta no PC.
- **hub-backend, 1o tique a mao (~18h15):** lote `2026-09-22h` drenado -> lote `2026-09-23a` com 0 cards (saldo do dia = teto 90 - 159 revisoes) -> hub **Version 3**. Achado no ato: `--export-player` cortava no teto POR LOTE, nao no saldo do DIA -- corrigido (`teto_do_dia(ordered, consumo_hoje)`, teste antes do fix).
- **Auditoria de fidelidade do Painel (subagente Opus, read-only):** ENGANOSO -- semana por posicao no plano, nao calendario ("S1, 3 tarefas" x panorama S2, 21 tarefas/511q); FSRS sem saldo do dia; "do previsto" com denominador misto; simulados como tarefas de CM. DESATUALIZAVEL -- so regenerado no fechamento; constante 2760; "126" fixo (re-medido: 128 sessoes, 2 vinculadas). BATE: #38 em todas as frentes, volume/acerto por bloco, /performance, retencao, proximas 7.
- **Hub Version 4 (~19h):** painel refeito (semana pelo leitor do panorama; Hoje = cota 25/~103 + cards 159/90 + agenda 7d; ritmo real 17,9 x alvo 75,6 q/dia; simulados em linha propria) e Aulas como quadro (Aulas-base / Revisoes / Analises, "feito" riscado). Capabilities com `quadro` write interact (3 regras); leitura em `as_level interact` conferida.
- **`plano.py --concluir ID --leitura`** (decisao dele): aula riscada no quadro conclui a tarefa de aula sem bloco; tarefa com lista ou questoes previstas e recusada. O tique passa a concluir.
- Custos de subagente (harness): verificador Sonnet 75.224 tokens / 4,8 min; executor hub 1-5 Opus 270.280 / 38,1 min; auditor painel Opus 113.659 / 3,9 min; redesign painel+quadro Opus 334.401 / 35,2 min.

## Padrões de erro identificados (sessao de questoes)
- **Q1 hematoma da bainha do reto** (marcou drenagem percutanea): lacuna de ENTIDADE -- sem o nome da doenca, febre baixa/leucocitose/PCR viraram "colecao drenavel". Comporta: anticoagulante + tosse + queda de Hb = sangue; sangue em paciente estavel nao se drena.
- **Q2 limite lateral do canal femoral** (chute): direta; N-A-V-E.
- **Q3 alternativa composta** ("escroto ... o que confirmaria indireta"): EXECUCAO -- ele sabia a D; aceitou a B pela 1a metade. Reincidencia de "rotular cada alternativa V/F" (agora em versao de alternativa com duas metades).
- **Q4 femoral:** mortalidade da urgencia ~3,8% x <0,1% eletiva (HerniaSurge 2018, PMID 29330835; Saeter 2022, PMID 35641700 -- verificado). Via de acesso na urgencia SEM consenso no guideline (banca-dependente). "Nunca reduzir femoral encarcerada": SEM evidencia formal -> nao virou card.
- **Anatomia inguinal = 4 de 7 sinais do bloco** (Q2 + 3 incertezas: epigastrica inferior, anel femoral/ligamento inguinal na imagem, conteudo do cordao).

## Artefatos criados/modificados
- Hub: `core/templates/hub.html`, `core/templates/player.html`, `tools/hub.py`, `tools/painel.py`, `core/hub_quadro.json`, `artifacts/painel.html`; testes `tools/test_player_js.py`, `tools/test_hub_quadro.py` (+ hub, painel, fsrs_queue_player).
- `tools/fsrs_queue.py` (saldo do dia; `previsao` e `agenda_base` no export), `app/utils/db.py` (`agenda_revisoes`), `tools/plano.py` (`--leitura`), `tools/reachability_check.py` (ignora `.claude/worktrees`).
- `.claude/commands/hub-backend.md` (novo), `revisar.md`, `engenharia-cli.md` + espelhos; `AGENTE.md §7.4`; `AUDITORIA_MEDHUB.md` (F129).
- Banco: 170 revisoes FSRS, 50 marcas de reforja, 4 erros + 5 cards (#1729-#1733), 8 cards reforjados (#1721-1728), 3 habilidades `incerteza`, #38 feita.

## Decisoes tomadas
- Hub com Painel primeiro e sem texto de bastidor; timer = tempo ativo com pausa (P).
- Backend = sessao do Claude Code aberta no PC + `/loop /hub-backend`; a pagina nao aciona agente.
- Teto de cards e do DIA (saldo), nao do lote.
- "Feito" no quadro de aulas = confirmacao de leitura; conclui tarefa de aula pelo `--leitura`.

## Proximos passos
- 1o ato da s195: um tique do `/hub-backend` (fila de 24/09) e, se ele quiser, `/loop 20m /hub-backend`.
- Questoes: DMG #26, Topicos em Pediatria #96; Raciocinio #877 por leitura. Revisao Direcionada Nefro (aula-base D10 antes de re-drillar). 6-8 cards EMED de anatomia inguinal no proximo lote.
- F129 (acento em ~749 cards) para o `/ai-eng`; handoff-block ainda com semana por posicao.
