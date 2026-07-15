# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-15 -- **s120: S13 conversacional (SUS/Imunizações/Colecistite) + pendências quentes -- 4 dias, 65q, 15 cards (811-825), 1 resumo gold novo (SUS). Padrão de ouro do dia: aula ancorada no PDF do EMED (a de SUS de memória cortou os Atributos da APS -- usuário pegou). Imunizações recalibrado D10 (dificuldade absoluta). Enunciado negativo SUSPENSO como foco (erros eram de conteúdo). Acumulado 5.026.***

## > Proximo passo imediato

**PLANO 15.07 (energia ALTA, ~6h -- capacidade ~90q + 30 FSRS):**

**A. Flashcards (FSRS) -- PRIORIZAÇÃO (`/revisar` DRENAR):**
1. **22 atrasados PRIMEIRO** (dívida vencida) -- limpar antes que o backlog cresça.
2. **Cards frescos de hoje (811-825)** via `--new-limit` -- consolidam A FRIO o que foi errado na s120 (SUS/Imuniza/Colecistite); reforço no mesmo dia.
3. Resto do backlog (425 novos) até o teto de **30/dia**.

**B. Questões -- PRIORIZAÇÃO (~90q, aula-base ancorada no PDF -> questões -> análise):**
1. 🔴 **Imunizações - Revisão (D10 onboarding COMPLETO)** -- maior alavanca da área mais fraca, e a Teoria III está fresca. Foco no "fora da normalidade": eventos adversos, timing de reforços, quando aplicar/não imunoglobulina, intervalos, contraindicações ([[feedback_imunizacoes_d10_onboarding]], tema_id 265).
2. **Tema NOVO da S13** para volume: Endometriose, DII, Pré-Natal II, Pneumo Intensiva II, Transtornos de Humor (os "próximos temas" do day_plan ainda listam SUS/Imuniza/Colecistite -- JÁ FEITOS; ignorar, é o Drive stale).
3. Blocos de revisão da S13: Hepatologia/Icterícia; Arboviroses/Meningites/Sepse (rev. por questões).

**Regra permanente:** antes de CADA aula-base, buscar o PDF-fonte do EMED em `resumos/` (INCLUINDO `.pdf`) e ancorar -- nunca só da memória ([[feedback_aula_base_ancorar_pdf_emed]]).
**Pendência de conteúdo:** backfill do resumo de Imunizações (Raiva pós-exposição, COVID, Dengue, Herpes-Zóster sem seção própria).

## Padroes de erro vivos -- atencao do scrum master
- 🟢 **Enunciado negativo SUSPENSO como foco (s120):** o usuário mostrou que os erros recentes eram de CONTEÚDO, não da estrutura da pergunta. O agente estava deixando o padrão virar reflexo e blindar o mergulho clínico -- reforça [[feedback_analise_hard_soft_skill]] (80% técnico / 20% padrão). Não reintroduzir sem sinal real.
- 🔴 **Imunizações = dificuldade ABSOLUTA (D10):** 7/25 erros; 3 foram recall fresco do que foi ensinado 2h antes (palivizumabe não interfere, antitérmico só MenB, influenza >= 6m). O tema não consolida num passe -- exige onboarding.
- 🔴 **Colecistite × Colangite -- eixo da drenagem:** Q1 drenou a estrutura errada (CPRE numa colecistite). Regra: cístico/vesícula -> colecistostomia; colédoco/via biliar -> CPRE. Card 823.
- Carregado: discriminações de princípio SUS (igualdade×universalidade, integralidade×equidade); atributos da APS (essenCIAL + derivados).

## Estado por frente
- **Volume & Metas:** 5026 / 10000 (perf. ~79.1%). Hoje: 18. Ritmo-alvo ~82.9q/dia (60d p/ ENAMED). [derivado: day_plan --handoff-block]
- **FSRS:** 22 atrasados + 4 hoje + 425 novos (backlog). Cards s120: 811-825 (15 de erro) + urocultura + reforge 209.
- **Conteudo:** 70 resumos em resumos/ (+SUS `Princípios e Diretrizes do SUS.md`, gold, auto_check PASS). [derivado: glob]
- **Erros & Cards:** +15 erros s120 (SUS 811-815, Imuniza 816-822, Colecistite 823-825). `review_log` 87-91 (Icterícia, Intoxicações, + PREPARAR de SUS/Imuniza/Colecistite). Dificuldades: SUS=5, Imunizações=10, Colecistite=10 (usuario); Icterícia/Sepse Neonatal=8 (aula).
- **Posicao cronograma:** db=S12 (nominal S16, atraso 4 sem); **REAL=S13** (usuário fechou S12). Drive stale (6d) -- `--sync-drive` quando houver xlsx local.
- **Infraestrutura:** ai-eng -- `day_plan --aderencia` ESTREADO no boot (telemetria planejado×real). `reflect.py` = só sessão de engenharia (esta foi de estudo). RAG reformado disponível.

## Pendencias ativas
🔴 Imunizações - Revisão D10 (diretriz). Backfill resumo Imunizações (Raiva/COVID/Dengue/Zóster). Colecistite: tema nasceu (298, D10). Reforjar `TCE.md` + `Sistemas de Informação em Saúde.md`. Aula-base de Pré-Natal I/II. Reforjar cards 95/120 (120 via gate de evidência). Ledger `AUDITORIA_MEDHUB.md`: F35 (reconcile volume + seletor de suite auto_check); F8 (isolamento PREPARAR D8+). Ano da diretriz de HAS (2020 x SBC 2025). Banca-dependente no DITC II (belimumabe/nefrite, SAF 2023).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_120.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
