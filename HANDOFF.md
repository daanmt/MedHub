# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-07 -- **s112: DM Complicacoes Cronicas 58q/51a (87,9%, melhor % recente) + 7 erros -> 7 cards (762-768). Achados de conteudo novo no resumo: pe de Charcot (mecanismo vasodilatador) e diretriz SBC/SBHCI 2017 (DM pos-ICP).***

## > Proximo passo imediato
1. **FSRS:** 3 atrasados + 6 hoje (backlog 393 novos) -- `/revisar` ou `fsrs_queue.py`.
2. **Debito aberto (arrastado):** aula-base de Pre-Natal I NUNCA foi feita (operador adiantou pra cold recall) -- resumo pronto, so falta a "escada de degraus" antes de fechar o tema de verdade.
3. **Proximo bloco de conteudo (S12, recomendado pelo day_plan):** Medicina de Familia e Comunidade (extensivo) -- cards de erro frescos (<48h) puxando reincidencia. Fila seguinte: Apendicite Aguda (F16, alta alavanca), Hipertensao Arterial Sistemica Pt.2/Cardiologia, Disturbios do Potassio, Cefaleias+Epilepsias.
4. Slot de simulado previsto ainda nesta semana (S12, ciclo de 4 semanas).

## Padroes de erro vivos -- atencao do scrum master
- RED **Enunciado negativo reincidiu 2x no MESMO bloco de novo (DM Q1+Q4)** -- 3a sessao seguida com esse padrao (s110 Pre-Natal Q1+Q3, agora DM). Padrao cronico ja mapeado (`feedback_enunciado_negativo`); sob fadiga de leitura marca alternativa VERDADEIRA como se fosse a falsa. Ritual: rotular V/F cada alternativa antes de decidir, sempre que ver "mostra-se inadequado"/"conceito inadequado"/EXCETO.
- RED **Inversao intuitiva do mecanismo (pe de Charcot):** denervacao autonomica "deveria" sugerir isquemia/vasoconstricao, mas causa VASODILATACAO em microvasos (perda do tonus simpatico) -- 57% da turma errou na mesma direcao, sinal de armadilha sistemica, nao so individual.
- RED **Vies otimista em fato de diretriz (DM pos-ICP):** assumiu que "tratar bem os fatores de risco" reduz obito/eventos no diabetico revascularizado; a diretriz SBC/SBHCI 2017 diz o oposto (nao ha reducao efetiva demonstrada) -- 72% da turma errou pro lado otimista.
- RED **Mapa de reforco instavel (Imunizacoes, arrastado):** inventa reforco onde nao existe (Hepatite B) E perde reforco onde passou a existir (Febre Amarela aos 4 anos, 2020).
- RED **Ferro x folato, direcoes opostas no 1o trimestre confundidas (arrastado):** ferro deve ser LIMITADO; folato deve ser INICIADO cedo. Mesma janela, sentidos opostos.

## Estado por frente
- **Volume & Metas:** 4765 / 12000 (perf. ~79.2%). Hoje: 0. Ritmo-alvo ~108.0q/dia (67d p/ ENAMED). [derivado: day_plan --handoff-block]
- **Conteudo:** 63 resumos. DM Complicacoes Cronicas ganhou secao nova (5.5 Neuroartropatia de Charcot) + fato de diretriz SBC/SBHCI em Doenca Macrovascular + ressalva de triciclicos em Neuropatia Autonomica + 6 novas armadilhas. Gap de alta alavanca seguinte: Apendicite Aguda (F16).
- **Erros & Cards:** +7 cards de erro hoje (762-768: DM Complicacoes Cronicas), todos ancorados no elo.
- **FSRS:** 3 atrasados + 6 hoje. Backlog: 393 novos. [derivado: day_plan --handoff-block]
- **Infraestrutura:** sem mudancas de engenharia nesta sessao (bloco de conteudo puro). Virada de papel 2 (s111) segue valendo: Opus resolve achados do ledger, agente anota.

## Pendencias ativas
Aula-base de Pre-Natal I (debito, ver acima). Apendicite Aguda ainda sem resumo (F16, cobertura ja prioriza). Reescrever TCE.md + Sistemas de Informacao em Saude.md. Reforjar cards 95/120 (120 via gate de evidencia). Ledger `AUDITORIA_MEDHUB.md`: F21 aberto (contrato de aula), F30 aberto (cronograma x resumo real) -- ambos candidatos a Opus.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_112.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
