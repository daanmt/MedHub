---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO -- MedHub

*Atualizado: 2026-08-30 (sessão 160 -- auditoria de engenharia do motor: F45-F60, matriz de portadores, handoff p/ /ai-eng) | Ferramenta: Claude Code (Fable 5)*
*Anterior: 2026-08-25 (sessão 156). Narrativa por sessão: [`history/INDEX.md`](history/INDEX.md) -- o header aqui é 1 linha por contrato.*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) -> [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

> **🎯 VIRADA s159 (2026-08-30) -- o norte passa a ser UERJ/MFC.** O usuário reavaliou a aposta em Psiquiatria via ENAMED 2026: sem o bônus de 10% do RQE, seria preciso ~90-95% para uma vaga, e **há mais inscritos com o bônus de MFC do que vagas de Psiquiatria no Brasil inteiro**. A rota passa a ser **UERJ/MFC (01/11/2026) → R1/R2 MFC (mar/2027-fev/2029) → RQE → ENAMED com +10% para Psiquiatria**. O objetivo Psiquiatria/IPUB não morreu: ganhou 2 anos de lastro e um bônus. Detalhe em `project_norte_uerj_mfc` na memória. *(Supersede a virada multi-banca da s126: USP saiu do radar, ENAMED foi rebaixado.)*

- **ENAMED deixa de ser piso de CRM.** O usuário leu a legislação: **o registro no CRM é automático**, independente de proficiência no ENAMED. O ENAMED de 13/09 continua sendo prestado (com Psiquiatria escolhida na inscrição) e vale como **termômetro da preparação e ensaio geral de execução** 7 semanas antes da UERJ — mas não organiza mais o planejamento nem é alvo de volume. *(Supersede o refinamento da s134.)*
- **🔄 MARCOS REFEITOS na s159** (`tools/performance.py`):
  - **Marco 1: UERJ/MFC = 10.400 @ 01/11.** Não é número arbitrário: 6.631 (acumulado em 30/08) + 60q/dia × 63 dias. `MARCOS[0]` dirige o ritmo-alvo do `day_plan`, que passa a reportar **~59,8q/dia** — o ritmo que o próprio usuário declarou sustentável.
  - **Marco 2: Ciclo 2026 = 12.500 @ 31/12** (mantido; vira piso, será batido ~25/11 no ritmo novo).
  - **Marco 3: stretch 15.000** (sem data).
  - **Marco aposentado:** "Cronograma EMED (grade completa) = 9.454 @ 25/10". A grade deixa de ser o alvo e vira **insumo**: a 60q/dia com a frente MFC aberta ela não fecha inteira, e a cauda de baixo rendimento UERJ sai no rescope de 14/09.
- **🔄 RITMO REDEFINIDO na s159: 60 questões/dia + 60 flashcards/dia**, em média sustentável. Decisão textual do usuário: *"as metas devem ser realistas, pois de nada adianta fazer 500 questões em 5 dias e depois passar 2~3 dias sem estudar, por excesso de cansaço."* `TETO_BASE` do FSRS sobe 40 → **60**; `CAP_MULTIPLICADOR` cai 2 → **1,5** no mesmo movimento (dobrar o teto em regime de dívida daria 120/dia e reinstalaria o pico-e-queda rejeitado). Norma em `core/contracts/fsrs-management-contract.md`.
- **A prova (Edital 15/2026 Cepuerj, PDF em `data/Edital_UERJ_2027_Acesso_Direto.pdf`):** 100 questões objetivas, **20 por conteúdo** — Clínica Médica, Cirurgia Geral, GO, Pediatria e **Medicina de Família e Comunidade**. **Etapa única**, sem prova prática nem análise curricular, **5 horas**. Aprovação ≥50 pontos e não zerar nenhum conteúdo. Desempate: CM → Cirurgia → Pediatria → MFC. **20 vagas de MFC, 15 de ampla concorrência.** Bibliografia do bloco MFC = Gusso & Lopes + Duncan (**MFC clínica, não saúde coletiva** — hipótese contrária refutada na s159).
- **🔴 Reponderação de conteúdo (cruzamento do `Guia_Estatístico_-_UERJ.pdf` com o formato novo):** Clínica Médica cai de ~42% para 20%; **MFC sobe de ~6,7% para 20%**; Cirurgia (13,9%) e Pediatria (13,2%) sobem para 20%; GO fica estável (~19% → 20%). Consequência: a cauda longa (Ortopedia 0,36% · Oftalmo 0,48% · Dermato 1,20% · Otorrino 1,32% · Psiquiatria 1,44% · Pneumo 1,56% · Hepato 1,68%) hoje vive **dentro** das 20 questões de CM e vale ~2 questões somada. É de onde sai o corte.
- **Custo/Q atual:** **R$ 0,91** (jun/2026, acumulado = investimento ÷ questões), em queda; alvo no fim do plano ≈ R$ 0,26.
- **Indicador Atual:** **6.631 / 10.400** — **63,8%** do marco da UERJ · perf. **78,8%** · ritmo-alvo **~59,8q/dia** (63d p/ 01/11). *(derivado: `python tools/day_plan.py --handoff-block`)*
- **Performance Geral:** **78,8%**. Por bloco UERJ: **Preventiva 834q/84,9%** · **Pediatria 809q/84,5%** · GO 1.176q/79,8% · Cirurgia 823q/79,1% · **Clínica Médica 2.548q/77,4%** · Simulado 441q/60,8%. **Gargalo nº1 = EXECUÇÃO DE PROVA** (banco 78,8% × simulado 60,8% = 18pp). Numa seleção de etapa única isso *é* o jogo — e as 5h para 100q dizem que o problema é fechamento precoce, não pressa: `PLAYBOOK_EXECUCAO_PROVA.md` precisa ser recalibrado.
- **Contadores (derivados):** **128 resumos** · **903 erros** · **1.213 cards ativos** (`needs_qualitative<2`) · **pool FSRS 684** · **taxonomia 244 temas** · **RAG gold-only**.
- **Cronograma -- DOIS SSOTs (achado s114, modelo revisto na s144):** detalhamento de cada tarefa = `Cronograma.pdf` (SSOT, derivado para `core/cronograma/grade.json`); **conclusão** = coluna `Realizada?` do `Dashboard EMED 2026`; **ordem** = `Cronograma de Reta Final.xlsx` reordenado à mão. Norma: `cronograma-contract.md` Cláusula 5b. Datas em `core/provas.json` (ENAMED 13/09 · fim-grade 25/10 · **UERJ/MFC 01/11**). **A grade tem 30 semanas, mas as S29-S30 (12/10-25/10) têm ZERO questões novas** — são "Diversos Assuntos" e "Questões Erradas". O último conteúdo novo é a **S28 (05-11/10)**, cuja sexta é **09/10 = fim do internato + colação**. Ou seja: a grade de conteúdo e o internato terminam juntos, e 12/10→01/11 já é reta final por construção.

---

## Estado por frente (macro)

- **Volume & Metas:** 6.631 / **10.400 (UERJ @ 01/11)** · ritmo-alvo **~59,8q/dia** (63d) · zona **COBERTURA** · desvio 10,2pp entre blocos -> simulado prescrito (**em débito, 7d sem**).
- **Conteúdo:** 128 resumos em `resumos/`. Gaps abertos: `TCE.md`, `Sistemas de Informação em Saúde.md`, aula-base de Pré-Natal I. **🔴 Gap estrutural novo (s159): o bloco MFC da UERJ (20% da prova) tem lastro ZERO** — as 834q de Preventiva cobrem a minoria SUS/epi do bloco, não o miolo clínico (Gusso + Duncan). Frente abre 14/09. Corpus EMED (275 decks) via `tools/emed_flashcards.py`.
- **Erros & Cards:** 903 erros · 1.213 cards ativos · ~280 não-atômicos na worklist (WARN, `audit_card_atomicity.py`, cifra pré-s146). Régua de autoria: `estilo-flashcard.md` (um critério de acerto; teste eixo × pacote; **s151: reforja por "confuso" mira a frente, não o verso**).
- **FSRS:** dívida 24 atrasados + 45 devidos hoje · pool 684 nunca introduzidos · **teto 60/dia** (s159; regime de dívida sobe até 90). Projeção sob 60/dia: **o pool zera ~29/09** e a carga cai p/ ~25/dia de manutenção antes da reta final. Invariante C = trava técnica em `record_review` desde a s144.
- **Posição:** conteúdo S16 (nominal S22, atraso ~6 sem) *(derivado: `preparacao_estado`)*. **Ordem do cronograma congelada até 13/09** por decisão do usuário; rescope pró-UERJ em 14/09. Ver `HANDOFF.md`.
- **Infraestrutura:** contratos em `core/contracts/`; harness `auto_check` (8 BLOCK + 11 WARN desde a s159, pytest incluso); watermark de dado nos writers; `core/provas.json` (multi-prova). **s160: motor auditado ponta a ponta -- 16 achados F45-F60 abertos em `AUDITORIA_MEDHUB.md §3o` (zero patch, salvaguarda) e dossie entregue ao /ai-eng (`~/ai-eng/HANDOFF-MEDHUB-COLA.md`) p/ o PRD da des-colagem; frente aguarda o retorno dele.**

> Narrativa de cada frente (s121-s144: atomicidade medida, pivô atômico, loop reforjar/split, curva de esquecimento, autogovernança) vive em `history/` -- ver `history/session_144.md §Anexo` e `history/INDEX.md`. Esta seção é **1 linha por frente**, por contrato.

---

## Próximos passos

> **🗄️ MODO SPRINT QUESTION-FIRST -- ENCERRADO (s126, sepultado de vez na s159).** A meta de ≥100q/dia está **morta**: o regime vigente é **60q/dia + 60 flashcards/dia em média sustentável** (s159). O que sobrevive do sprint: estudo por questões + flashcards com **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0). Detalhe: [[project_norte_uerj_mfc]] e [[feedback_politica_cards_diaria]] na memória.

> **🎯 REGIME s159 -- 3 fases até a UERJ (01/11):**
> 1. **30/08 → 13/09 (15d, ~900q):** grade EMED **na ordem atual** (congelada por decisão do usuário) + ensaio ENAMED sob playbook.
> 2. **14/09 → 09/10 (26d, ~1.560q):** rescope do cronograma pro formato UERJ + **abertura da frente MFC** (Gusso + Duncan). Fim do internato e fim do conteúdo da grade coincidem em 09/10.
> 3. **12/10 → 31/10 (20d, ~1.200q):** reta final já formado, dedicação integral. As S29-S30 do EMED ("Diversos Assuntos" + "Questões Erradas") são exatamente isso por construção.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Abertura da próxima:** **60 flashcards** (fila FSRS) -> **60 questões**. Aula-base + refresh Camada 0 antes de cada bloco.
2. **PRIORIDADE ESTRATÉGICA -- execução de prova:** o gargalo migrou de conteúdo para processo de resolução, e numa seleção de **etapa única** ele é decisivo. Treinar o **ritual anti-vazamento** (default-to-C + fechamento precoce) via [`PLAYBOOK_EXECUCAO_PROVA.md`](docs/PLAYBOOK_EXECUCAO_PROVA.md). **🔄 s159 -- recalibrar o playbook:** a UERJ dá **5h para 100 questões (3 min/q)**, então a instrução de ritmo se inverte em relação ao treino ENAMED — o erro a combater é fechar cedo, não demorar. (bug nº 1c segue ativo.)
3. **Aulas-base = CONTRATO** (AGENTE §1.2): cunhar aula "escada de degraus" antes de cada bloco novo; calibrar descompressão para pontos operacionais que a banca cobra. **🔄 s149:** entrega passa a ser via **Artifact HTML com design real** (skill `frontend-design`), modelo = motor reusável da Autópsia (`tools/autopsia_template.py`) -- `tools/aula_template.py` equivalente ainda não existe, frente aberta (`HANDOFF.md`). Bundles que compartilham mecanismo (ex.: abdome agudo cirúrgico) estruturam-se em árvore (tronco -> branches), não capítulos paralelos (`feedback_bundled_cronograma_task_content`).
4. **Gaps de resumo:** `Diabetes - Complicações Crônicas`; candidatos: ectópica, icterícia neonatal (só andaime). PDFs do EMED agora MANTIDOS (gitignored) p/ RAG -- GO/Gastro/Dermato/Pediatria despejados.
5. **Revisão Calibrada -- IMPLEMENTADA (s096):** schema + `infer_nota` + fusão `/revisar` + contrato + 63 testes. Resta **ratificar o contrato** após o 1º uso real e **integrar `day_plan --difficulty`** na abertura de task do boot. **Pendentes:** Tier-3 (schema de altura), limpeza `[bulk]`/`Geral` da taxonomia, re-drill dos bug-nº1 (#70 reincidiu na s096), sessão dedicada de Cirurgia, integrar `/schedule` no calendário.

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
