---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO -- MedHub

*Atualizado: 2026-08-22 (sessão 151 -- 3 aula-base publicadas via forks + nova cláusula de contrato: reforja de card mira a frente, não o verso, `estilo-flashcard.md`) | Ferramenta: Claude Code (Sonnet 5)*
*Anterior: 2026-08-19 (sessão 149). Narrativa por sessão: [`history/INDEX.md`](history/INDEX.md) -- o header aqui é 1 linha por contrato.*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) -> [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

> **🔄 RAMP REFEITO na s126 (virada multi-banca):** ramp mensal 3.000 (mai) -> **12.500 (dez/2026)** [3000·4500·5500·7000·8300·9600·11000·12500]; stretch 15.000. O ramp antigo de 17.000 foi **aposentado** -- exigia ~29q/dia acima do plano e reinstalava a sobrecarga que o usuário decidiu sair. Custo-alvo recalibrado p/ R$ 0,35/q (4.410/12.500); investimento R$ 2.940 -> R$ 4.410 (R$ 210/mês). **Reconcile db↔dashboard: batem por área e no total (3.457 = 3.457, 0 divergência).** *(Supersede a antiga "Meta Final 23.000" -- confirmar com o usuário se o stretch de 23k permanece.)*

- **🔄 MARCOS REFEITOS na s126 (o foco deixou de ser só o ENAMED):** o usuário reavaliou -- concorrência alta em Psiquiatria, retorno incerto -- e o norte passou a **multi-banca**: ENAMED (13/09) + **UERJ + USP (nov-dez, sem edital)**, sob regime de **constância > pico**.
  - **Marco 1: Cronograma EMED (grade completa) = 9.454 @ 25/10.** 🔑 **Achado que derruba o marco antigo:** a grade tem 30 semanas e a S30 fecha ~**25/10**, ~6 semanas DEPOIS da prova de 13/09. Perseguir 10.000 até 13/09 comprimia 13 semanas de grade em 50 dias e produzia o ritmo-alvo fictício de ~96q/dia. **A meta estava errada, não o ritmo do usuário.** Bug correspondente corrigido em `day_plan._cronograma_hoje` (dividia a grade inteira pelos dias até o ENAMED).
  - **Marco 2: 2º ciclo UERJ/USP = 12.500 @ 31/12.** Não é número arbitrário: é a soma do próprio plano (5.232 + 4.263 de grade + ~300 de simulado ENAMED + ~2.700 de banca).
  - **Marco 3: stretch 15.000** (sem data).
  - **ENAMED deixa de ser corrida de volume e vira aferição.** Continua sendo prestado; só não organiza mais o planejamento sozinho. **Simulado volta a CONTAR no volume** (reverte s099), em bloco dedicado -- cadência **2/semana** (subiu de 1, decisão s134).
- **🔄 REFINADO em s134 (2026-08-03):** ENAMED também é **piso de registro no CRM** (~60% em simulado), condição anterior a qualquer competição por vaga de residência -- reordena a prioridade imediata, não reverte os marcos acima. Cadência da semana: 2 simulados (qua/qui + dom) + 30-50 cards/dia. Detalhe em `history/session_134.md`.
- **Plano de fim de ano:** **12.500** questões até 12/2026 (stretch 15.000). Ver `project_novo_norte_multi_banca`.
- **Custo/Q atual:** **R$ 0,91** (jun/2026, acumulado = investimento ÷ questões), em queda; alvo no fim do plano ≈ R$ 0,26.
- **Indicador Atual:** **6.432 / 9.454** -- **68,0%** do marco da grade · 51,5% do 2º ciclo (12.500) · perf. **78,4%** · ritmo-alvo **~47,2q/dia** (64d p/ 25/10). *(derivado: `python tools/day_plan.py --handoff-block`; histórico do indicador em `history/INDEX.md`)*
- **Performance Geral:** **78,4%** (`sessoes_bulk`). Fracos: Oftalmo 50% (pouco lastro) · Cardiologia 68,7% (99q, volume real) · Hemato 71% · GO 72% · Hepato 73% · Otorrino 74%. **Gargalo nº1 = EXECUÇÃO DE PROVA, não conteúdo** (default-to-C, fechamento precoce, não fechar a conduta) -- confirmado de novo pelo Simulado 5 (10 das 37 erradas = "escala além do necessário", ver `history/session_146.md`).
- **Contadores (derivados):** **128 resumos** · **903 erros** · **1.213 cards ativos** (`needs_qualitative<2`) · **pool FSRS 676** · **taxonomia 244 temas** · **RAG gold-only** (`pdf_raw` deletada na consolidação part-2, ~130MB liberados).
- **Cronograma -- DOIS SSOTs (achado s114, modelo revisto na s144):** detalhamento de cada tarefa = `Cronograma.pdf` (SSOT, derivado para `core/cronograma/grade.json`); **conclusão** = coluna `Realizada?` do `Dashboard EMED 2026` (Sheets nativo, texto puro, o agente lê); **ordem** = `Cronograma de Reta Final.xlsx` reordenado à mão (ritual do usuário, `--sync-drive` local). Norma: `cronograma-contract.md` Cláusula 5b. Datas em `core/provas.json` (ENAMED 13/09 = prova · fim-grade 25/10 = grade).

---

## Estado por frente (macro)

- **Volume & Metas:** 6.432 / 9.454 (grade @ 25/10) · ritmo-alvo ~47,2q/dia (64d) · zona **COBERTURA** (avançar a grade, não refinar) · desvio 10,1pp entre blocos -> simulado prescrito (em dia, 1/7d).
- **Conteúdo:** 128 resumos em `resumos/`. Gaps abertos: `TCE.md`, `Sistemas de Informação em Saúde.md`, aula-base de Pré-Natal I. Corpus EMED (275 decks) consultável via `tools/emed_flashcards.py`.
- **Erros & Cards:** 903 erros · 1.213 cards ativos · ~280 não-atômicos na worklist (WARN, `audit_card_atomicity.py`, cifra pré-s146). Régua de autoria: `estilo-flashcard.md` (um critério de acerto; teste eixo × pacote; **s151: reforja por "confuso" mira a frente, não o verso**).
- **FSRS:** dívida 45 atrasados + 53 p/ hoje · pool 676 nunca introduzidos (entram <=80-100/dia, teto sobe em regime de dívida -- ver `feedback_politica_cards_diaria`). Invariante C = trava técnica em `record_review` desde a s144.
- **Posição:** conteúdo S16 (nominal S21, atraso ~5 sem) *(derivado: `preparacao_estado`)*. Ver `HANDOFF.md` para o detalhe das tarefas confirmadas.
- **Infraestrutura:** contratos em `core/contracts/`; harness `auto_check` (B1 do reconcile = BLOCKING real desde a s144); watermark de dado nos writers; `core/provas.json` (multi-prova). `.venv` resincronizado com `requirements.txt` na s146 (7 pacotes faltando, incl. `fsrs`).

> Narrativa de cada frente (s121-s144: atomicidade medida, pivô atômico, loop reforjar/split, curva de esquecimento, autogovernança) vive em `history/` -- ver `history/session_144.md §Anexo` e `history/INDEX.md`. Esta seção é **1 linha por frente**, por contrato.

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 -> ~13/07/2026):** atrasado -> estudo só por **questões + flashcards, SEM apostila corrida**. Exceção produtiva: **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0 -- leitura calibrada ao nível do estudante). Meta **≥100 questões/dia + ≥20 flashcards/dia**. **Não criar resumo completo** de tópico neste período. Detalhe: [[project_sprint_questoes_focado]] e [[cards-altura-graduada]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Abertura da próxima:** começa com **flashcards** (17 cards operacionais da s086 vencem cedo no FSRS) -> **≥100 questões**. Aula-base + refresh Camada 0 antes de cada bloco.
2. **PRIORIDADE ESTRATÉGICA -- execução de prova:** o gargalo migrou de conteúdo para processo de resolução. Treinar o **ritual anti-vazamento** (default-to-C + fechamento precoce) via [`PLAYBOOK_EXECUCAO_PROVA.md`](docs/PLAYBOOK_EXECUCAO_PROVA.md). Maior alavanca da preparação. (bug nº 1c segue ativo; default-to-C é o novo sub-padrão dominante.)
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
