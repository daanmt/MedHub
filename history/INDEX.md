# MedHub — Session Chronicle

Chronological index of every work session on this project. The session log files themselves carry the detail (what was analyzed, what changed, what was decided); this index is the table of contents.

**Reading order:** newest-first below. Active sessions live in `history/`; pre-modernization sessions (≤028, when the project still relied on `caderno_erros.md`, `HANDOFF.md`, and `progresso.md`) have been archived to [`legacy/`](legacy/) — see [`legacy/README.md`](legacy/README.md) for the deprecation context.

Gaps in the sequence (026, 047, 050, 053, 057, 058, 064, 072) are sessions that happened but whose dedicated log file was absorbed into adjacent ones or never written separately.

---

## Active sessions (029 onward)

| # | Date | Tool | Topic |
|---:|---|---|---|
| 085 | 2026-06-19 | Claude Code | **Sessão gigante.** Pediatria 38/23 (icterícia/sepse — radar de dormência cravou 63d frio). **`/revisar`: fila vencida ZERADA (52 cards)** + conserto de deck (435 recurado + **15 andaimes**: Hemostasia/Trauma/Ectópica/Icterícia). Neonatologia: 15 erros → **algoritmo das 3 comportas** + 8 andaimes (review_log #50); Q7 banca-dependente. **Decompose do bug nº 1c → `PLAYBOOK_EXECUCAO_PROVA.md`** (disparou em **6 temas** = eixo metacognitivo central). **`Cirurgia Infantil.md` expandido** (+12 seções das Partes 2+3 + 14 armadilhas, Zero PDF). Distribuição FSRS 25×4/12×3/8×2/7×1 |
| 084 | 2026-06-17 | Claude Code | **`Doença Renal Crônica.md` construído** (stub→padrão-ouro, da apostila Estratégia/Zero PDF) + `LRA.md` auditado (Cairo-Bishop, cardiorrenal 5 tipos, escada hipercalemia). Bloco Nefro 40/31 + SOAP/RCOP 26/24 = **+66q**; 11 erros→cards (460-468, 477-479) + **8 andaimes** (DMO, Hemostasia, Cardiopatias). `/revisar` **35/50 — 1ª alimentação real da curva**; andaime destravou Hemostasia em tempo real (lote 4→5). Reconcile db↔Dashboard EMED **0 divergência (3457=3457)**; metas alinhadas (plano 17k/dez, Custo/Q R$0,91). Padrão: **bug nº 1c (fato/contexto) reincidente 2×** |
| 083 | 2026-06-15 | Claude Code | Bloco GO (54q/41a) + DITC (21q/20a) = **75q**, 14 cards (446-459) + §DMTC no `DITC.md` · **capacidade nova: gestão da curva de esquecimento (F1-F6)** — `review_log` + `/refrescar` (`dormant_refresh.py`) + boot proativo `day_plan.py` (§2 passo 4) + **dedup taxonomia 126→86 + `UNIQUE(area,tema)`** + backfill 47 temas + contrato `forgetting-curve` + autonomia §1.1. 6 padrões metacognitivos em GO; 2016×2025 banca-dependente |
| 082 | 2026-06-14 | Claude Code | Revisão de Cardiopatias Congênitas (12 cards-alvo) → diagnóstico **grounding, não material** (o resumo já era gold; "tema zero" da s081 era falso). Evolução de método **cards de altura graduada** (base→mecanismo→nuance→topo): CLI `insert_card_base.py` + 8 cards de andaime (5 base 438-442, 3 mecanismo 443-445) + Camada 0 do `/revisar` (refresh dirigido + compressão calibrada) + decisão AGENTE §6. Gap fino do estudante = **causalidade, não fato**. 0 questões (revisão + engenharia de método) |
| 081 | 2026-06-13 | Claude Code | Revisão pós-pausa (**49 cards**: 28 fila + 13 Hemato + 8 misto) + auditoria do deck (239 ativos, 0 heurísticos, fila regen vazia; 181 não-vistos) + **rotina de curadoria `recurate_cards.py`** (428/68/82/74 refeitos, 92 aposentado) + **`Hemostasia.md` expandido** (coagulopatias adquiridas, PTT, HNF, PTI criança). Achados: safra mar/2026 fraca; **cardiopatia congênita = tema zero** (resumo p/ próxima). 0 questões (re-grounding pós ~2-3 meses parado) |
| 080 | 2026-06-12 | Claude Code | Hemostasia (37q/23a, 62%) — 14 erros (2 blocos) → 13 cards (425-437); Q7 = erro de banca (gabarito oficial B medicamente errado, não cardado). **vWD × FVIII duplo** (Q11/Q12), grid TP/TTPa frágil (Q10), plasmaférese nos 2 sentidos (Q9/Q14), **enunciado negativo 3ª vez** → memória `feedback_enunciado_negativo`; PTI tratar×observar reincidiu (bug nº 1) |
| 079 | 2026-06-11 | Claude Code | Lesão Renal Aguda (35q/27a, 77%) — 8 erros → 10 cards (415-424); **bug nº 1b: ancoragem no fármaco** (rabdo→AINE, pré-renal→nimesulida, renovascular→estatina; 3/8) → memória `feedback_bug_ancoragem_farmaco`. Revisão direcionada pré-questões de LRA + Hemostasia |
| 078 | 2026-06-11 | Claude Code | `/revisar` **backlog drenado (44 cards)** + contrato `/revisar` → **Camada 2 — Revisão Direcionada de fechamento** (o card é a sonda, o resumo é a fonte; verdict: **0 deficiência de material**, FA/Trauma/Asma/DM2 com resumo gold) + **dedup estrutural: 109 pares duplicados v1/v2 aposentados** (deck 325→216; chave `questao_id`; 7 pares divergentes flagados). Falhas: FA decoreba + trauma órgão sólido (bug nº 1, card 26 espelho do 25) |
| 077 | 2026-06-05 | Claude Code | `/revisar` ~34 cards + re-drills + **dissecação metacognitiva** (bug nº 1: ancoragem no número, transferível PTI/asma/trauma) + evolução do contrato `/revisar` (flip obrigatório + relearning intra-sessão) + **limpeza estrutural do deck**: 15 pares dedup, 5 option-dependent reescritos, **re-fil de 291 cards `[bulk]`** (Cirurgia 216→57, Pediatria 4→65) + fix `insert_questao.py` (card heurístico fantasma) |
| 076 | 2026-06-04 | Claude Code | CAD/EHH (34q, 7 erros → 7 cards + resumo turbinado) + **regeneração completa dos 87 cards heurísticos órfãos** da bankruptcy s075 (4 ondas, FSRS preservado → 0 heurísticos) + fix do critério órfão da `cards_regen_queue.py` + `/revisar` 15 cards (fantasma Dengue C/D resolvido); achado: temas `[bulk]` mal-rotulados |
| 075 | 2026-06-03 | Claude Code | Conexão Google Drive (planilhas conciliadas) + marco ENAMED no `/performance` + ciclo completo Arboviroses (15 erros → 19 cards → resumo) + **camada de estado contract-driven** (4 contratos `core/`, HANDOFF+ESTADO, bankruptcy FSRS) espelhada do `agente-daktus-content` |
| 074 | 2026-06-03 | Claude Code | Pivot Agent-First fechado — Onda D completada (Streamlit Encolhe: FSRS Player removido, Caderno read-only via `get_caderno_detalhado`; audit PASS) + commits atômicos das Ondas A-D herdadas da sessão interrompida |
| 073 | 2026-05-27 | Claude Code | Consolidação do harness em fluxo único — contrato §7.2 em AGENTE + 7 commits (workflows delegam CLI canônica em vez de copiar, vibeflow `domain-engine-api` staleness fix 5→2 exports, 4 module docstrings, `Temas/`→`resumos/` em 7 arquivos) |
| 071 | 2026-04-23 | Claude Code | Análise de Úlceras Genitais (43q / 38a, 5 erros, 3 eixos metacognitivos) + criação da skill `/performance` via ciclo vibeflow completo (discover→spec→implement→audit) |
| 070 | 2026-04-16 | Antigravity | Análise de Preventiva (23q / 18a, 5 erros, armadilhas DO e notificações compulsórias) + bulk register |
| 069 | 2026-04-16 | Gemini 3.1 Pro | Resumo `Sistemas de Informação em Saúde` (Preventiva): SIM, SINAN, SINASC, SISAB |
| 068 | 2026-04-16 | Gemini 3.1 Pro | Cirurgia Infantil (44q / 40a, 4 erros) + fix de 197 FKs órfãs + `data_sessao` + idempotência bulk |
| 067 | 2026-04-16 | Antigravity | Arquitetura `sessoes_bulk` + migração histórica (3.020q, 2.413a, 79,9%) + dashboard reescrito |
| 066 | 2026-04-10 | Antigravity | Análise Síndromes Hipertensivas na Gestação (6 erros, IDs 349-359) + correção de bugs em insert_questao.py |
| 065 | 2026-04-09 | Antigravity | Resumo `Síndromes Hipertensivas na Gestação` (Gold Standard 80/20, ZUSPAN/PRITCHARD) |
| 064 | 2026-04-07 | Antigravity | RAG v2: multi-query (Raw + HyDE), ThreadPoolExecutor, BM25 estrutural (depois desabilitado), `.env` via python-dotenv |
| 063 | 2026-04-05 | Antigravity | Auditoria dos 2 ChromaDB coexistentes (canônico em `data/chroma/` + MCP obsidian-notes-rag); decisão arquitetural |
| 062 | 2026-04-05 | Antigravity | Análise Sepse Neonatal (3 erros: Listeria, exceção SBP, ampicilina) |
| 061 | 2026-04-01 | Antigravity | Análise massiva Trauma/ATLS (14 erros) — peritonites, eviscerações, choque |
| 060 | 2026-03-29 | Antigravity | Gastroenterologia: DRGE + Pancreatite (8 erros) — padrão "Ansiedade de Intervenção" nomeado |
| 059 | 2026-03-29 | Antigravity | Demências e EM (4 erros): CADASIL, Binswanger, MEEM falso-negativo em alta escolaridade |
| 058b| 2026-03-28 | Claude Code | Faxina de artefatos: `artifacts/{llm_runs/058,backups,legacy}/` + .gitignore + README rewrite + HANDOFF.md aposentado |
| 058 | 2026-03-28 | Claude Code | Passe qualitativo LLM em 189 cards + `fix_taxonomy_bridge.py` (21 órfãos) + filtro `needs_qualitative<2` |
| 057b| 2026-03-27 | Claude Code | Refatoração qualidade flashcards (Fases 1-4): baseline 277/277 ruins → 31/277 |
| 057 | 2026-03-27 | Claude Code | FSRS operacional: `record_review()` real + `review_cli.py` + `audit_fsrs.py`; ROADMAP reescrito (4 trilhos) |
| 056 | 2026-03-27 | Claude Code | Pipeline flashcards v5: schema migrado (8 novos campos) + 277 cards regenerados (heuristic) |
| 055 | 2026-03-25 | Claude Code | Automação de memória via hooks (SessionStart + PostToolUse Write) + correção do manager.py |
| 051 | 2026-03-25 | Antigravity | Resumo Cirurgia Infantil (HDC → defeitos de parede); 80/20 + Zero PDF |
| 049 | 2026-03-25 | Antigravity | Resumo Icterícia e Sepse Neonatal (Pediatria); Gold Standard 80/20 |
| 048 | 2026-03-25 | Antigravity | Resumo Trauma Abdominal e Pélvico (Cirurgia) |
| 046 | 2026-03-25 | Claude Code | Memory v1: LangGraph + LangMem + `SQLiteMemoryStore`; `app/memory/` + `tools/test_memory.py` (4/4 smokes) |
| 045 | 2026-03-24 | Antigravity | Sífilis Congênita e reinfecção materna (análise + refinamento NTT) |
| 044 | 2026-03-24 | Antigravity | Resumo Úlceras Genitais (GO) + 3 erros (Herpes gestacional, fluxograma > 4 sem) |
| 043 | 2026-03-23 | Antigravity | Auditoria arquitetural completa: alinhamento de ESTADO/README/HANDOFF/roadmap + wikilinks Obsidian |
| 042 | 2026-03-23 | Antigravity | Resumo Vigilância em Saúde (PNVS 2018, Saúde Única, ANVISA) |
| 041 | 2026-03-23 | Antigravity | Análise Pediatria (46q / 42a) — IOT em PCR, pneumotórax, adrenalina precoce |
| 040 | 2026-03-23 | Antigravity | Análise Dermatologia (24q / 16a) — Hanseníase + PLECT, estesiometria, Sabouraud |
| 039 | 2026-03-22 | Antigravity | Refinamento Otorrino (19q / 13a) — cisto dermoide, hemangioma subglótico, HPV orofaringe |
| 038 | 2026-03-22 | Antigravity | Resumo Hanseníase e Síndromes Verrucosas (PLECT, 80/20, Zero PDF) |
| 037 | 2026-03-22 | Antigravity | Resumo Otorrino Cirúrgica (cisto tireoglosso → esvaziamento cervical) |
| 036 | 2026-03-22 | Antigravity | Resumo Arboviroses (Dengue/Chikungunya/Zika) + Zero PDF |
| 035 | 2026-03-21 | Antigravity | Reestruturação Sífilis na Gestação: LCR + STORCH + fluxogramas |
| 034 | 2026-03-20 | Antigravity | Análise DM (CAD, manejo) + audit do resumo + marca histórica de 100 erros |
| 033 | 2026-03-20 | Antigravity | Resumo Diabetes Mellitus — Complicações Agudas (CAD adulto/ped, EHH, hipoglicemia) |
| 032 | 2026-03-18 | Antigravity | Refinamento Rastreamento Colo (diretrizes 2025) + análise de 9 erros |
| 031 | 2026-03-16 | Antigravity | Resumos Psiquiatria (Dependência Química, Intoxicações Exógenas) + Nefrologia (LRA) |
| 030 | 2026-03-15 | Antigravity | Resumo Pancreatite Aguda e Crônica (Atlanta 2012) |
| 029 | 2026-03-15 | Antigravity | UI Refresh: design Flat com `app/utils/styles.py` + arquitetura híbrida de botões FSRS |

## Legacy sessions (001–028, archived)

Pre-modernization era. Workflows referenced `caderno_erros.md`, `HANDOFF.md`, `progresso.md` — all retired during sessão 058. Files moved to [`legacy/`](legacy/). See [`legacy/README.md`](legacy/README.md) for deprecation context.

| # | Date | Tool | Topic |
|---:|---|---|---|
| 028 | 2026-03-14 | Antigravity | Rebranding IPUB → MedHub; revisão Pediatria/Emergências |
| 027 | 2026-03-14 | Antigravity | Expansão Saúde Coletiva III |
| 025 | 2026-03-14 | Antigravity | Reforma IPUB v3.0 — estabilização final |
| 024 | 2026-03-14 | Antigravity | Upgrade pedagógico Flashcards v3.8 Expert |
| 023 | 2026-03-14 | Antigravity | Streamlit Web App + pivô arquitetural (Zero DB) |
| 022 | 2026-03-14 | Antigravity | ETL + migração massiva de dados históricos |
| 021 | 2026-03-14 | Antigravity | FSRS Optimizer e algoritmos de ML |
| 020 | 2026-03-14 | Antigravity | Workflows híbridos + regra Siamese Twins |
| 019 | 2026-03-14 | Antigravity | Arquitetura de banco FSRS + planilha Estratégia Med |
| 018 | 2026-03-14 | Antigravity | Ajuste de produto (FSRS + arquitetura UI/DB) |
| 017 | 2026-03-14 | Antigravity | Elaboração do roadmap do sistema IPUB |
| 016 | 2026-03-14 | Antigravity | Análise Sífilis na Gestação |
| 015 | 2026-03-13 | Antigravity | Resumo Sífilis na Gestação e Congênita |
| 014 | 2026-03-12 | Antigravity | Análise Trauma Abdominal / ATLS |
| 013 | 2026-03-11 | Antigravity | Resumo Trauma Abdominal e Pélvico |
| 012 | 2026-03-10 | Antigravity | Resumo Emergências Pediátricas |
| 011 | 2026-03-09 | Antigravity | Resumo Rastreamento CCU (diretrizes 2016 + 2025 DNA-HPV) |
| 010 | 2026-03-09 | Antigravity | Análise Public Health Measures (Saúde Coletiva) |
| 009 | 2026-03-08 | Antigravity | Análise PTI + refatoração de governança |
| 008 | 2026-03-06 | Antigravity | Resumo Hemostasia |
| 007 | 2026-03-06 | Antigravity | Expansão Infectologia (TB + HIV) |
| 006 | 2026-03-05 | Antigravity | Eliminação do `Extracted/` + limpeza automática pós-resumo (Zero PDF) |
| 005 | 2026-03-05 | Antigravity | Consolidação de Tools + refatoração Asma.md |
| 004 | 2026-03-04 | Antigravity (Gemini 2.5 Pro) | Análise DM2 (continuação — 4 questões) |
| 003 | 2026-03-04 | Antigravity (Gemini 2.5 Pro) | Análise DM2 (9 questões) |
| 002 | 2026-03-04 | Antigravity (Opus) | Reestruturação lean do IPUB |
| 001 | 2025-02 → 2026-03-03 | Mixed (retroativo) | Histórico pré-reestruturação consolidado |
