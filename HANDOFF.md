# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-25 -- S156 (Refatoração Arquitetural, correção FSRS e Operação Limpa-Banco)*

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

## Ultima sessao -- s156 (REFATORAÇÃO ARQUITETURAL E LIMPA-BANCO)
Sessao de refatoracao tecnica e curadoria do banco. **(1)** Clean & Drift: Removidos artefatos obsoletos (`app/pages/`, `app/components/`) e scripts orfaos apontados pelo Graphify. Correcoes de frontmatter (`Demências.md`) e doc drift de contratos. **(2)** God Module Desmembrado: O modulo de orquestracao e validacao (`tools/auto_check.py`) foi fatiado, migrando funcoes git e validacoes de estado para os novos `tools/utils/git_utils.py` e `state_utils.py`, mantendo a assinatura da esteira autônoma e CI integrados. **(3)** Correcao de Contrato FSRS: A ambiguidade (Ambiguous Edge) do grafo sobre a constante dinamica `CAP_MULTIPLICADOR` foi resolvida no contrato `fsrs-management-contract.md`. **(4)** Operacao Limpa-Banco: Lotes 1, 2 e 3 processados manualmente (15 flashcards pais "duplo-ask" purgados e transformados, injetando 14 novos cartoes-filho no ipub.db ja sincronizados com o escalonador FSRS). A fila de "duplo-asks" global reduziu consideravelmente (restando 129 cards). O RAG foi devidamente selado. Nenhuma questao respondida (Simulado e Ginecologia pendentes pro dia seguinte).

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
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_156.md*
