# Session 110 — Ciclo 3 (pipeline de conhecimento, 4 ondas) + MFC/Vulvovaginites + VIRADA do papel (eu implemento)

**Data:** 2026-07-06 (parte 1 do dia)
**Ferramenta:** Claude Code (Opus 4.8 1M)
**Continuidade:** Sessão 109 (apendicite + abertura do ledger F16-F26). Boot ofereceu o mini-drill anti-reincidência; operador redirecionou para o ciclo 3 vibeflow.

---

## O que foi feito

**Trilha ENGENHARIA — Ciclo 3 do pipeline de conhecimento (implementado por MIM, via vibeflow):**
- PRD `pipeline-conhecimento.md` splitado em **4 specs** (gen-spec) → **implement** → **audit**, **4/4 PASS** (`.vibeflow/audits/pipeline-conhecimento-part-1..4-audit.md`). Commit **`fe3f5b6`** na main (hook autônomo aprovou).
  - **Onda 1 (F16a):** `tools/cobertura_conhecimento.py` — relatório read-only de cobertura (333 PDFs × 61 `.md`, 298 órfãos priorizados por rendimento; semana de conteúdo/posição SSOT destacada) + `db.get_taxonomia_rendimento`.
  - **Onda 2 (F17):** RAG two-tier — collection `pdf_raw` ADITIVA (gold `resumos` intocado, 1048 chunks), fallback marcado `source=pdf_raw` + sombreamento por tema, incremental por mtime; `tools/index_pdf_raw.py`; `search_two_tier` em `app/engine/rag.py`. **Indexação real executada: 333 PDFs → 14.216 chunks.** O RAG deixou de ser cego a ~270 temas órfãos.
  - **Onda 3 (F18c/F21):** Cláusula 10 + Invariante E no `revisao-calibrada-contract` (descompressão calibrável × cobertura=piso fixo) + registro `fonte='aula'`. Espelho revisar em paridade.
  - **Onda 4 (F27/F28):** `insert_questao` modo single com exit 0/1 simétrico; doc do mapeamento arg→coluna em `analisar-questao` (`o_que_faltou` canônico; `--elo` alimenta só o matcher F25).
- Testes: **50 passed** (36 → 50, +14). Um bug real de fixture caçado pelo próprio live-test da Onda 2 (gold de 0 chunks) → corrigido.

**Trilha ESTUDO A — MFC (19q, 3 erros, 84%):**
- Gap central = **matriciamento/apoio matricial como resposta-reflexo** (Q1 terapia comunitária, Q2 contratransferência) + estimativa rápida×visita domiciliar / orientação comunitária×integralidade (Q3). Cards **737-739** ancorados no elo.
- Resumo `Medicina de Família e Comunidade.md` **blindado**: +4 armadilhas cumulativas (matriciamento entre profissionais; terapia comunitária×grupo operativo×Balint; contratransferência×transferência; estimativa rápida/orientação comunitária). Lint 0/0, reindexado.

**Trilha ESTUDO B — Vulvovaginites (51q, 11 erros, 78%):**
- **Aula-base D5** entregue, criticada pelo operador (compressão errada), **refeita** na arquitetura certa (degraus + escopo-árvore + mecanismo dos exames ABERTO: whiff/KOH/clue cells destrinchados).
- 11 erros → cards **740-750**. F25 detectou reincidência viva: **fluconazol-na-gestante** (2× no tema, similar erro 416/card 665).
- **Dificuldade registrada 7 → 6** (`fonte='aula'`, medida pós-questões, não predita).
- Resumo `Vulvovaginites.md` **expandido**: +§6 (vaginite atrófica/SGM, vaginose citolítica, vaginite aeróbia), +§7 (vaginite×cervicite — quando o ceftriaxone entra/sai), +6 armadilhas. Lint 0/0, reindexado. Fecha o buraco de cobertura que gerou 5 dos 11 erros.

## Padrões de erro — DELE (conteúdo)

- 🔴 **"Empilhar antibiótico" / vaginite×cervicite (Q1, Q8, Q9):** o eixo é o LOCUS. Thayer-Martin negativo TIRA o ceftriaxone (Q1); VB pura (colo normal) = só metronidazol (Q9); exame vaginal normal + colo inflamado = cervicite, ceftriaxone+azitro ENTRA (Q8, espelho).
- 🔴 **Cegueira de contexto / bug nº1 (Q5, Q10):** pH alto + menopausa/sem lactobacilos = atrofia (estrogênio), não metronidazol; bolhoso+pH alto+aminas+ = pensar Trico (IST).
- 🔴 **Classe de fármaco (Q3, Q4):** VB+alergia = clindamicina (não miconazol); gestante+candidíase = tópico (fluconazol VO contraindicado).
- 🔴 **Entidades fora do trio (Q5 atrófica, Q6 citolítica, Q7 aeróbia):** o resumo não as cobria — agora cobre.
- **MFC:** matriciamento-reflexo (2×), estimativa rápida/atributos APS.

## Padrões — MEUS (processo, "aprimorar a si mesmo")

- 🔴 **Sobre-compressão da aula D5 (recorrência do F21, agora do meu lado):** nomeei os discriminadores (whiff/KOH/clue cells) em vez de destrinchá-los — profundidade D2 disfarçada de D5 — e comprimi o escopo (doses, DIP, cervicite) que uma aula ANTES de questões exige. Corrigido: contrato + `revisar.md` ganharam a regra **"Arquitetura por propósito"** (antes de questões = degraus + escopo + mecanismo aberto; antes de flashcards = refresh curto).
- **Em-dash proibido:** meti `—`/`→` nos resumos (linter ENCODING pegou); troquei por `--`/`->`. Aprendizado: rodar `audit_resumos` sempre após editar resumo.

## VIRADA de contrato (operador, s110)

1. **Eu implemento agora.** O operador redefiniu o papel: a partir de s110 **eu** toco as mudanças (não mais Fable/ai-eng); o `AUDITORIA_MEDHUB.md` vira substrato de contexto para mim. Prova: o ciclo 3 inteiro foi meu. Memória `project_papel_auditor_ledger` atualizada.
2. **Registro de dificuldade = pós-análise.** A nota `set_dificuldade` vem SEMPRE após análise de questões/flashcards (a medição), NUNCA após a aula (predição). Refina o timing do F18c. Memória `feedback_registro_dificuldade_pos_analise`.
3. **Arquitetura da aula por propósito** (acima). Memória `feedback_aula_base_arquitetura_proposito`.

## Volume & números

- **70q hoje (s110):** Preventiva/MFC 19/16 (84%), Ginecologia/Vulvovaginites 51/40 (78%). Volume **4.514 → 4.584** (46% da meta-prova 10k). Ritmo-alvo ~107,5q/dia (69d p/ ENAMED).
- **14 cards de erro novos (737-750).** Backlog FSRS 361 → 375.
- **2 resumos blindados** (MFC, Vulvovaginites) + reindexados. Posição: conteúdo S12 (atraso 3 sem vs calendário S15).

## Próxima sessão (s110 parte 2 — ainda hoje, 06.07.26)

Ordem definida pelo operador: **(1) Imunizações II · (2) Pré-Natal I** (aula-base → questões → análise → registro de dificuldade por tema, pós-análise) · **(3) macetar flashcards** (fila FSRS, tema-agnóstico). Pendência (b): expandir o resumo tocado se surgir gap de cobertura, como fizemos aqui.
