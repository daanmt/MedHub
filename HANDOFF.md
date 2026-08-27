# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-26 -- S157 (Ginecologia S16 57q concluída + 5 erros analisados/persistidos + Drenagem FSRS 25 cards)*

## > Proximo passo imediato

1. **Simulado ENAMED na íntegra (prova do ano passado)** -- decisão explícita do usuário para abertura da sessão 158 (treino de prova completa e calibragem de tempo/estratégia).
2. **Drenagem FSRS restante** -- bater a fila diária (31 atrasados + 40 agendados) em blocos de 5 a 10 com pipeline em voo.
3. **Auditoria ampla do banco (pendente desde s148, soma F37+F40+F41)** -- rastrear origem da escrita em lote em `taxonomia_cronograma.questoes_realizadas` (F37).
4. **`card_id=120`** (Gravidez Ectópica, achado F7 antigo) para `/pesquisar-evidencia` -- mesmo precedente metodológico do card 114 da s154.
5. **Revisão Direcionada dedicada** pro padrão "remédio certo, sequência errada" (eclâmpsia + TCE, s154) + "exame normal exclui" (>=3 temas).

## Estado por frente
- **Volume & Metas:** 6631 / 9454 (perf. ~78.8%). Hoje: 0. Ritmo-alvo ~47.8q/dia (59d p/ Cronograma EMED (grade completa)).
- **FSRS:** divida 31 atrasados + 40 p/ hoje -- pool 688 nunca introduzidos (entram <=40/dia).
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Posicao:** conteudo S16 (nominal S22, atraso 6 sem) [derivado: preparacao_estado]
- **Zona (variancia.py):** COBERTURA -- desempenho alto (média ~79%), cobertura em avanço. Simulado prescrito para a próxima sessão.
- **Dormência:** 29 de 253 temas sem revisar há >=21d (cluster Cardio/Nefro/Endócrino + Anemias Hemolíticas no topo).
- **Datas:** ENAMED 13/09/2026 (18d) -- grade fecha 25/10/2026 (59d).

## Ultima sessao -- s157 (GINECOLOGIA S16 + ANÁLISE DE ERROS + DRENAGEM FSRS)
Sessão de avanço da grade clínica e retenção. **(1) Volume & SSOT:** Registrado bloco de Ginecologia da semana S16 (57 questões feitas, 52 acertos, **91.2% de aproveitamento**). **(2) Análise de Erros & Autópsia:** 5 erros processados pelo método sequencial e persistidos via `tools/insert_questao.py` no `ipub.db`: Q1 (janela do DIU no puerpério: contraindicado entre 48h e 4 semanas / Cat 3 OMS -> implante de progestágeno indicado); Q2 (endometriose: tratamento clínico busca anovulação/amenorreia; padrão-ouro formal = videolaparoscopia); Q3 (vulvovaginites: vaginite atrófica tratada com estrogênio tópico, nunca progesterona; vaginite aeróbia = E. coli, S. aureus, GBS, E. faecalis com whiff negativo); Q4 (planejamento familiar: toque bimanual/exame pélvico é o único indispensável pré-DIU; USGTV/preventivo não mandatórios); Q5 (endometriose: USTV com preparo intestinal é método não invasivo de primeira linha para mapeamento profundo). **(3) Flashcards & FSRS:** Cunhados e integrados 5 flashcards atômicos (IDs 1442-1446) testados e aprovados pelo `card_checks.py`. Drenagem de 25 cards da fila FSRS em 5 blocos com 100% de assimilação nos erros frescos de hoje e 1 redrill agendado em trauma abdominal. **(4) Resumos & Linter:** Atualizados `Planejamento Familiar.md`, `Endometriose.md` e `Vulvovaginites.md`; `auto_check.py` PASSED (0 BLOCKs).

## Pendencias/observacoes ativas
- 📝 **Simulado ENAMED anterior completo** -- abertura da sessão 158.
- 🗓️ **Auditoria ampla do banco** -- ver Próximo passo #3 (F37 com evidência fresca, soma F40+F41).
- ⚠️ **3 flags de card pendentes** -- (1411, 283, 319).
- 🔍 **`card_id=120`** (Gravidez Ectópica) para `/pesquisar-evidencia`.
- 📌 **2 padrões reincidentes sem Revisão Direcionada dedicada**.
- 📝 **23 temas sem resumo dedicado** (achado do grafo Pediatria/GO: PTI, TCE, Kawasaki, Bronquiolite, Meningite Tuberculosa, Anafilaxia, etc.).

---
*Histórico: history/INDEX.md * Macro: ESTADO.md * Sessão: history/session_157.md*
