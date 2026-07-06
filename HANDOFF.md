# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-06 -- **s110 parte 1: ciclo 3 pipeline-conhecimento (4 ondas, vibeflow 4/4 PASS, commit fe3f5b6) + pdf_raw indexado (14.216 chunks, RAG cobre o corpus inteiro) + MFC 19q + Vulvovaginites 51q (70q, ~80%) + 14 cards (737-750) + 2 resumos blindados. VIRADA: EU implemento agora (nao mais Fable). Dificuldade Vulvovaginites 7->6.***

## > Proximo passo imediato -- s110 PARTE 2 (ainda hoje, 06.07.26)
Ordem definida pelo operador: **(1) Imunizacoes II -> (2) Pre-Natal I** (por tema: aula-base calibrada -> questoes -> analise dos erros -> **registro de dificuldade POS-analise**, nunca pos-aula) **-> (3) macetar flashcards** (fila FSRS via `/revisar` ou `fsrs_queue`, tema-agnostico -- 3 atrasados + 9 hoje + backlog 375).
- **Arquitetura da aula (regra nova s110, Clausula 4/10 do `revisao-calibrada-contract`):** ANTES de questoes = **degraus** (escopo-arvore inteiro + doses/diferenciais + **mecanismo dos exames ABERTO**, nao so nomeado); ANTES de flashcards = **refresh curto** + contexto dos cards. Descompressao (nota) != cobertura de mecanismo.
- **Registro de dificuldade (regra nova s110, `feedback_registro_dificuldade_pos_analise`):** so APOS analise das questoes/flashcards do tema (a medicao), via `db.set_dificuldade`. Nunca a partir da aula sozinha.
- **Camada 2 (se surgir gap de cobertura):** se as questoes revelarem entidade que o resumo gold NAO cobre, expandir o resumo + armadilhas cumulativas -> `python tools/audit_resumos.py <arq>` (0 BLOCK) + reindexar (`index_resumo`). Precedente s110: matriciamento (MFC), atrofica/citolitica/aerobia/cervicite (Vulvovaginites).
- **Pendente de s109 (deprioritizado, mas vivo):** mini-drill anti-reincidencia apendicite (`python tools/fsrs_queue.py --pre-bloco "Apendicite" --janela-horas 96`, cards 729+730) + cunhar `resumos/Cirurgia/Apendicite Aguda.md` (F16 -- `cobertura_conhecimento.py` ja o prioriza; `pdf_raw` ja indexa o PDF-fonte).

## Padroes de erro vivos -- atencao do scrum master
- RED **Empilhar antibiotico / vaginite x cervicite (Vulvovaginites, s110):** o eixo e o LOCUS. Thayer-Martin negativo TIRA o ceftriaxone; VB pura (colo normal) = so metronidazol; exame vaginal normal + colo inflamado = cervicite (ceftriaxone+azitro ENTRA). Nao empilhar ATB sem achado cervical; nao esquecer quando ha cervicite.
- RED **Reflexo do antifungico / classe de farmaco (Vulvovaginites):** VB+alergia = clindamicina (nao miconazol); gestante+candidiase = azolico TOPICO (fluconazol VO CONTRAINDICADO -- reincidencia viva F25, card 743 ~ erro 416/card 665, 2x no tema).
- RED **Matriciamento como resposta-reflexo (MFC, s110):** matriciamento = entre PROFISSIONAIS; nao grupo de usuarios (terapia comunitaria) nem fenomeno emocional (contratransferencia). "Reuniao de equipe" nao basta.
- RED **Reflexo de confirmacao (apendicite / familia bug nº1):** caso classico jovem <48h -> PEDE exame em vez de operar (reincidiu 3x na s109). Isca = piuria (nao afasta). Mini-drill 729+730 pendente.
- RED **Bug nº1 / cegueira de contexto:** le exame por dado PARCIAL (pH alto -> "VB/Trico" ignorando menopausa=atrofia; LCR por 1 parametro). Ler o CONJUNTO, nao um marcador isolado.
- RED **Enunciado negativo (EXCETO / assinale a correta):** rotular cada alternativa V/F antes de marcar (reincidente em multiplas sessoes; s110 Q7/Q11 de Vulvovaginites).

## Estado por frente
- **Volume & Metas:** 4584 / 12000 (perf. ~79.0%). Hoje: 70. Ritmo-alvo ~107.5q/dia (69d p/ ENAMED). [derivado: day_plan --handoff-block] | Proximo: Imunizacoes II + Pre-Natal I (S12).
- **Conteudo:** 61 resumos (**2 blindados hoje:** MFC +matriciamento/terapia comunitaria; Vulvovaginites +atrofica/citolitica/aerobia/cervicite). **RAG agora two-tier:** gold 1048 chunks + `pdf_raw` 14.216 chunks -> corpus INTEIRO coberto (F17 resolvido). Gaps de `.md` gold: Apendicite Aguda (F16), TCE, Sistemas de Informacao em Saude. Priorizacao da fila de autoria: `python tools/cobertura_conhecimento.py`.
- **Erros & Cards:** **+14 cards de erro (737-750)** ancorados no elo (MFC 737-739; Vulvovaginites 740-750). Reincidencia viva F25: fluconazol-gestante (2x). Pendentes de reforge: 95, 120.
- **FSRS:** 3 atrasados + 9 hoje. Backlog: 375 novos. [derivado: day_plan --handoff-block] (+14 cards novos hoje.)
- **Infraestrutura:** **ciclo 3 ENTREGUE por MIM** (vibeflow gen-spec->implement->audit, 4/4 PASS; specs/audits em `.vibeflow/`). **VIRADA de papel (s110):** eu implemento as mudancas agora; `AUDITORIA_MEDHUB.md` = minha lista de trabalho/substrato (memoria `project_papel_auditor_ledger`). Contrato de revisao calibrada ganhou Clausula 10 (F18c/F21 -- cobertura=piso fixo + registro fonte='aula') + regra de arquitetura por proposito.

## Pendencias ativas
Imunizacoes II + Pre-Natal I (s110 parte 2) -> flashcards. Cunhar `resumos/Cirurgia/Apendicite Aguda.md` (F16, alta alavanca -- cobertura CLI prioriza). Mini-drill anti-reincidencia apendicite (`--pre-bloco`). Reescrever TCE.md + Sistemas de Informacao em Saude.md. Reforjar cards 95/120 (/curar-cards; 120 via gate de evidencia). **Ledger `AUDITORIA_MEDHUB.md` agora e MEU** (nao mais handoff p/ Fable): proximos achados de engenharia do uso -> eu implemento via vibeflow. **F11 EXECUTADO (historico git reescrito, blob ipub.db expurgado; repo ~2.9MB): clones/copias antigas em outras maquinas devem ser descartados e re-clonados** (SHAs mudaram; backup `C:/Users/daanm/medhub-backup-pre-expurgo.git`).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_110.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
