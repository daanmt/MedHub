# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-25 -- MVP /graphify (arquitetura + resumos Pediatria/GO com overlay de ipub.db) + limpeza .vibeflow/patterns + evidencia nova em F37 (sessao 155)*

## > Proximo passo imediato

1. **Usuario decide na abertura: simulado (em debito desde 17/08) OU os 2 blocos de questoes (Pediatria 51q + Ginecologia 57q, ultimas tarefas do S16) OU flashcards -- ou combinacao.** Nao prescrever um so; oferecer as opcoes e seguir a escolha.
2. **Auditoria ampla do banco (pendente desde s148, soma F37+F40+F41)** -- **F37 ganhou evidencia fresca na s155**: `taxonomia_cronograma.questoes_realizadas` nao e so residuo da migracao antiga, algo ainda escreve o campo em lote (3 temas nao relacionados com stats byte-identicas, `ultima_revisao=2026-08-23`, 128/269 temas=48% com valor duplicado). Rastrear a origem da escrita antes de decidir reconciliar/derivar/remover a coluna -- ver `AUDITORIA_MEDHUB.md` F37 para o achado completo. **Manter este item no radar ate ser investigado.**
3. **Esclarecer 3 flags de defeito de card sem confirmacao do agente** (card_id 1411 Ca mama, 283 estenose duodenal, 319 banca-especifica) -- decidir se e um 5o subtipo de F40 ou calibracao do usuario a ajustar.
4. **`card_id=120`** (Gravidez Ectopica, achado F7 antigo) para `/pesquisar-evidencia` -- mesmo precedente metodologico do card 114 da s154.
5. **Revisao Direcionada dedicada** pro padrao "remedio certo, sequencia errada" (eclampsia + TCE, s154) + "exame normal exclui" (>=3 temas) -- as duas ainda sem sessao propria.

## Estado por frente
- **Volume & Metas:** 6523 / 9454 (perf. ~78.5%). Hoje: 0. Ritmo-alvo ~48.0q/dia (61d p/ Cronograma EMED (grade completa)).
- **FSRS:** divida 12 atrasados + 36 p/ hoje -- pool 677 nunca introduzidos (entram <=40/dia).
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Posicao:** conteudo S16 (nominal S22, atraso 6 sem) [derivado: preparacao_estado]
- **Zona (variancia.py):** COBERTURA -- desempenho alto (media 79.0%, desvio 10.1pp entre blocos), cobertura baixa (54.0% da grade). Simulado prescrito e **em debito** (ultimo 17/08, janela 7d).
- **Projecao de ritmo (nova nesta sessao):** ritmo real 49.5q/dia vs necessario pra fechar o atraso do cronograma 77.0q/dia (janela 14d) -- deficit projetado de 34 dias se nada mudar. O ritmo pra fechar a GRADE INTEIRA ate o fim (48.0q/dia) segue batendo com o real; o gap e especifico do atraso de conteudo (S16 real vs S22 nominal).
- **Dormencia:** 29 de 253 temas sem revisar ha >=21d. Cluster notavel parado ha 46-57d: Cardio/Nefro/Endocrino (Arritmias, IC, Disturbios Acido-Base/Potassio, PCR, Obesidade, Glomerulopatias, DM-Complicacoes) + Anemias Hemoliticas (topo, 57d).
- **Padrao recorrente #1 do banco inteiro:** "incorporar atualizacao recente de diretriz/protocolo (versao antiga na memoria)" -- 7 ocorrencias, 7 temas distintos (mais transversal que qualquer padrao clinico especifico).
- **/graphify MVP (nova frente exploratoria, nao versionada em git):** grafo de arquitetura (tools/+core, 1344 nos) e grafo de conteudo clinico Pediatria+GO fundido com performance real de ipub.db (1258 nos). Achados: VOP (vacina descontinuada) confirma-se estruturalmente como ima de erro; "rotular cada alternativa V/F" aparece como ponte Pediatria<->GO, nao so por tema -- valida a tese padrao-metacognitivo > conteudo-clinico por um segundo angulo. 23 temas com volume real de questoes (PTI, TCE, Kawasaki, Bronquiolite, entre outros) nao tem resumo dedicado -- candidatos a aula-base futura, sem urgencia. `graph.html` de ambos disponivel em `graphify-out/` (local, gitignored) pra exploracao visual.
- **Datas:** ENAMED 13/09/2026 (19d) -- grade fecha 25/10/2026 (61d).

## Ultima sessao -- s155 (/GRAPHIFY MVP + LIMPEZA .VIBEFLOW + EVIDENCIA F37)
Sessao de tooling/auditoria, nao de estudo direto. **(1)** `/graphify` rodado 2x: primeiro em `tools/+core/` (piloto do skill, achou `taxonomia_cronograma` como no de maior centralidade -- 3 scripts de reparo dedicados, cicatriz dos pivots do projeto); depois em `resumos/Pediatria/+GO/` (42 notas pessoais, nao os PDFs-fonte) fundido deterministicamente com `ipub.db` (erros/flashcards+FSRS/habilidades recorrentes) via schema proprio do graphify -- sem LLM na fusao, so na extracao dos conceitos clinicos. Merge feito no nivel de extracao (nao via `merge-graphs` do CLI, que derrubava arestas cujo alvo so existia do outro lado). **(2)** Limpeza de `.vibeflow/patterns/`: 3 arquivos confirmados mortos (descreviam a UI Streamlit, removida ha varias sessoes, confirmado por 3 fontes independentes) foram deletados; 6 restantes ganharam frontmatter de rastreabilidade (`status`/`canonical_source`/`last_verified`) e 2 tiveram conteudo desatualizado corrigido. **(3)** Usuario notou contagem suspeita de 428 questoes repetida em PTI/TCE/Asma -- investigacao confirmou reincidencia do achado **F37** ja aberto desde a s128 (`questoes_realizadas` inflado/orfao), com prova nova de que o campo continua sendo escrito em lote (3 dias atras). Evidencia anexada ao F37 existente em `AUDITORIA_MEDHUB.md`, nao virou achado novo. **(4)** Status de preparacao entregue a partir das fontes que o proprio F37 confirma como limpas (`sessoes_bulk`, estado FSRS) -- zona COBERTURA, simulado em debito, deficit de ritmo de 34 dias, 29 temas dormentes. Nenhuma questao ou flashcard foi respondido nesta sessao (FSRS/volume do dia seguem zerados).

## Pendencias/observacoes ativas
- 🗓️ **Auditoria ampla do banco** -- ver Proximo passo #2 (F37 com evidencia fresca, soma F40+F41).
- ⚠️ **3 flags de card pendentes** -- ver Proximo passo #3 (1411, 283, 319).
- 🔍 **`card_id=120`** (Gravidez Ectopica) para `/pesquisar-evidencia` -- ver Proximo passo #4.
- 📌 **2 padroes reincidentes sem Revisao Direcionada dedicada** -- ver Proximo passo #5.
- ⚠️ **Revisao por Questoes Pediatria (51q) e Ginecologia (57q)** -- ultimas tarefas do S16, aula de apoio pronta desde a s153; agora tambem candidata explicita do usuario pra proxima sessao (ver Proximo passo #1).
- 📝 **23 temas sem resumo dedicado** (achado do grafo Pediatria/GO: PTI, TCE, Kawasaki, Bronquiolite, Meningite Tuberculosa, Anafilaxia, entre outros) -- volume real de questoes, sem urgencia.
- 📝 **2 aulas-base candidatas antigas ainda abertas** (DRGE cirurgica+necrose pancreatica; neoplasias intestinais raras).
- `tools/fila_enamed.py` -- superado, considerar aposentar formalmente.
- Achado tecnico nao resolvido: `tools/cronograma.py` perde tema em tarefa "Revisao por Questoes" e desalinha URL em "Teoria" pura.
- Guias estatisticos de UERJ/USP (fase 2, pos-ENAMED) ainda nao existem no repo.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_155.md*
