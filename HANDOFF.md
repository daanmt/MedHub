# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-06 -- **s111 (fecha s110 parte 2): F29 RESOLVIDO (drift planilha-db de 76q, achado e corrigido ao vivo) + Imunizacoes II (29q/24a, dificuldade 9->7) + Pre-Natal I tema-zero (18q/13a cold recall, resumo criado do zero de 90 paginas, dificuldade 9) + F30 registrado. Dia: 117q/93a (79,5%).***

## > Proximo passo imediato
1. **FSRS:** 3 atrasados + 9 hoje (backlog 386 novos) -- `/revisar` ou `fsrs_queue.py`.
2. **Debito aberto:** aula-base de Pre-Natal I NUNCA foi feita (operador adiantou pra cold recall) -- resumo pronto, so falta a "escada de degraus" antes de fechar o tema de verdade.
3. **Proximo bloco de conteudo (S12, candidatos):** Apendicite Aguda (F16, alta alavanca -- fecha gap de RAG antigo), Hipertensao Arterial Sistemica Pt.2/Cardiologia (confirmado nesta semana, area fraca 67%), Disturbios do Potassio, Cefaleias+Epilepsias (ambos extensivo, ainda intocados).

## Padroes de erro vivos -- atencao do scrum master
- RED **Mapa de reforco instavel (Imunizacoes):** inventa reforco onde nao existe (Hepatite B completa nao reforca, confundido com logica de dT) E perde reforco onde passou a existir (Febre Amarela ganhou reforco aos 4 anos em 2020 -- errou 2x no mesmo bloco, Q4+Q5).
- RED **Enunciado negativo reincidiu 2x no MESMO bloco (Pre-Natal Q1+Q3)** -- padrao cronico ja mapeado (`feedback_enunciado_negativo`); sob fadiga de leitura marca alternativa VERDADEIRA como se fosse a falsa. Ritual: rotular V/F cada alternativa antes de decidir, sempre que ver "assinale a incorreta"/EXCETO.
- RED **Ferro x folato, direcoes opostas no 1o trimestre confundidas:** ferro deve ser LIMITADO (estresse oxidativo trofoblastico); folato deve ser INICIADO cedo (reduz DTN). Mesma janela, sentidos opostos.
- RED **Bug no1 (emese x hiperemese):** achado negativo explicito no enunciado ("sem perda de peso") foi ignorado, escalou pra internacao sem criterio objetivo de hiperemese.
- RED **Imunoglobulina antitetanica nao e automatica no ferimento de alto risco** -- exige checklist proprio (esquema desconhecido/incompleto OU populacao especial OU >10a mal cuidado), nao reflexo "ferimento feio = vacina+soro".

## Estado por frente
- **Volume & Metas:** 4707 / 12000 (perf. ~79.1%). Hoje: 117. Ritmo-alvo ~105.7q/dia (69d p/ ENAMED). [derivado: day_plan --handoff-block]
- **Conteudo:** 63 resumos (**+2 hoje:** Imunizacoes MUITO expandido -- composicao de vacinas/coadministracao/calendarios adulto-idoso-gestante-prematuro-CRIE/BCG+HepB+DTP+Hib+Polio aprofundados; Pre-Natal CRIADO DO ZERO, tema-zero, 90 paginas do LDI condensadas). Gap de alta alavanca seguinte: Apendicite Aguda (F16).
- **Erros & Cards:** +10 cards de erro hoje (751-761: 6 Imunizacoes, 5 Pre-Natal), todos ancorados no elo.
- **FSRS:** 3 atrasados + 9 hoje. Backlog: 386 novos. [derivado: day_plan --handoff-block]
- **Infraestrutura:** **F29 RESOLVIDO** (drift planilha-db de 76q -- 4 relabels + 2 registros de volume faltante, tudo com backup e validacao 1:1 contra a planilha) + **F30 registrado** (`material_indicado` do cronograma nao verifica se o resumo existe de verdade -- mesmo buraco do F16). **Virada de papel (definida pelo operador nesta sessao):** eu sigo anotando/registrando achados no ledger; **Opus** assume o papel de reconciliar/resolver os proximos achados de engenharia -- eu nao implemento mais sozinho esse tipo de item.

## Pendencias ativas
Aula-base de Pre-Natal I (debito, ver acima). Apendicite Aguda ainda sem resumo (F16, cobertura ja prioriza). Reescrever TCE.md + Sistemas de Informacao em Saude.md. Reforjar cards 95/120 (120 via gate de evidencia). Ledger `AUDITORIA_MEDHUB.md`: F21 aberto (contrato de aula), F30 aberto (cronograma x resumo real) -- ambos candidatos a Opus.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_111.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
