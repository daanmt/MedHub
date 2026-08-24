# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-08-24 -- drenagem de 100 cards FSRS + 7 reforjas de card + correcao de conteudo via evidence-researcher (sessao 154)*

## > Proximo passo imediato

1. **Revisao por Questoes Pediatria (51q) e Ginecologia (57q)** -- ultimas tarefas confirmadas do S16, aula-base de apoio publicada desde a s153. Usuario decide quando fazer.
2. **Esclarecer 3 flags de defeito de card sem confirmacao do agente** (card_id 1411 Ca mama, 283 estenose duodenal, 319 banca-especifica) -- decidir se e um 5o subtipo de F40 ou calibracao do usuario a ajustar. Perguntar diretamente na abertura da proxima sessao.
3. **`card_id=120`** (Gravidez Ectopica, achado F7 antigo) para `/pesquisar-evidencia` -- mesmo precedente metodologico do card 114 desta sessao.
4. **Auditoria ampla do banco (pendente desde s148, 5a convocacao)** -- escopo agora soma F40 + F41 (achados de hoje: 6 novas instancias + subpadrao tautologico em cards `[bulk]` + reincidencia do padrao F7 em Gravidez Ectopica).
5. **Revisao Direcionada dedicada** pro padrao "remedio certo, sequencia errada" (confirmado hoje fora de Epilepsias -- eclampsia e TCE) + "exame normal exclui" (>=3 temas) -- as duas ainda sem sessao propria.

## Estado por frente
- **Volume & Metas:** 6523 / 9454 (perf. ~78.5%). Hoje: 0 (sessao 100% FSRS, sem volume de questoes novo). Ritmo-alvo ~47.3q/dia (62d p/ Cronograma EMED).
- **FSRS:** divida 1 atrasado + 11 p/ hoje -- pool 677 nunca introduzidos (+5 cards novos cunhados hoje). **100 cards drenados nesta sessao** em 10 blocos de 10 (pipeline de 2 blocos em voo): 58 nota 4, 13 nota 3, 10 nota 2, 13 nota 1 (94 avaliados; 6 forjados/divididos em vez de respondidos). 20 cards residuais surgiram depois do dreno (11 hoje + 8 erros_frescos + 1 atrasado) -- resíduo natural além do lote pedido, nao divida deixada pra tras.
- **Calibracao nova do usuario (salva em memoria):** no DRENAR de blocos grandes, feedback explicativo e so pra notas 1-2 -- notas 3/4 entram em tally compacto, sem prosa. Defeito de CARD (formulacao/conteudo) continua sempre reportado -- e outro eixo, nao desempenho do usuario.
- **7 cards reforjados + 5 novos hoje** (defeito de formulacao, familia F40): 1053 (tricomoniase, pergunta composta), 553->4 cards atomicos de HAS/cortes, 155->2 cards de puericultura (baixo/alto risco), 576->2 cards de DIU de cobre/NIC1, 293 e 325 (**subpadrao tautologico novo**: "por que X e mais provavel" respondido com reafirmacao de X sem mecanismo -- ambos de tema `[bulk]`, import em lote).
- **🔴 Card 114 corrigido via evidence-researcher (beta-hCG/gravidez ectopica):** usuario contestou a nota 1 dada a resposta "ectopica" ("voce pergunta o diagnostico MAIS PROVAVEL"). Veredito do evidence-researcher: **PRECISA AJUSTE** -- nem o card antigo ("gestacao topica normal", certeza que nem FEBRASGO nem ACOG sustentam) nem a contestacao do usuario estavam corretos. O quadro e uma "pregnancy of unknown location" (PUL): falha da gestacao (~50%) e o desfecho isolado mais provavel, mais que IUP evolutiva (~36%) ou ectopica (~11%). Card reformulado com a moldura de PUL + conduta de beta-hCG seriado em 48h (nao mais "repetir USG em 15 dias"). Fontes: ACOG Practice Bulletin 193 (PMID 29470343), Connolly et al. 2013 Obstet Gynecol (PMID 23262929), FEBRASGO.
- **Achado F41 registrado em `AUDITORIA_MEDHUB.md`:** conecta o card 114 a um achado antigo nunca auditado (F7, s108, `card_id=120`, mesmo tema Gravidez Ectopica, mesmo padrao de calibracao de probabilidade pre-teste). Proximos achados comecam em F42.
- **Datas:** ENAMED 13/09/2026 (20d) -- grade fecha 25/10/2026 (62d).

## Ultima sessao -- s154 (DRENAGEM DE 100 CARDS FSRS + 7 REFORJAS + EVIDENCE-RESEARCHER)
Sessao longa, 2 arcos. **(1) Drenagem de 100 cards em 10 blocos de 10**, pipeline de 2 blocos em voo (protocolo da s152): feedback do bloco N entregue junto com as perguntas do N+2. No meio da sessao (apos bloco 3), o usuario calibrou o comportamento do agente -- "feedback so das notas 1 e 2" -- corrigindo um excesso de prosa explicativa mesmo em acertos parciais (nota 3); ajustado e salvo em memoria. Distribuicao final: 58 nota 4, 13 nota 3, 10 nota 2, 13 nota 1. Dois clusters de erro levantados na Revisao Direcionada de fechamento: (a) "remedio certo, sequencia errada" -- o mesmo padrao ja nomeado pra Epilepsias apareceu em eclampsia (MgSO4 antes do ABC) e TCE (parou em IOT+suporte clinico sem chegar na craniotomia de urgencia); (b) inversao de pareamento hormonal em cancer de mama (aromatase pre/pos-menopausa; obesidade->mama x anovulacao->endometrio), 2x no mesmo bloco. **(2) Curadoria de card ao vivo:** o usuario flagrou 9 cards como defeituosos durante a drenagem. 6 confirmados e reforjados/divididos (mesma familia F40 -- pacote-de-fatos/composta/circular), incluindo um subpadrao NOVO (tautologia em cards de tema `[bulk]`, ex.: "por que X e mais provavel" respondido so reafirmando X). 1 card (114, beta-hCG/ectopica) foi auditado via `evidence-researcher` porque a contestacao do usuario era uma alegacao clinica decisoria, nao um defeito estrutural -- veredito: nem o card nem o usuario estavam certos, o quadro real e PUL. 3 flags (1411, 283, 319) nao tiveram defeito confirmado pelo agente e ficaram pendentes de esclarecimento direto com o usuario. Todo achado de card viraram registro F41 em `AUDITORIA_MEDHUB.md`, incluindo a reincidencia notavel: o mesmo padrao de calibracao de probabilidade em Gravidez Ectopica ja tinha sido flagrado ha dezenas de sessoes (F7, `card_id=120`) e nunca foi auditado.

## Pendencias/observacoes ativas
- 🗓️ **Auditoria ampla do banco** -- ver Proximo passo #4 (agora com F41 somado).
- 📌 **2 padroes reincidentes sem Revisao Direcionada dedicada** -- ver Proximo passo #5: "remedio certo, sequencia errada" (transversal, novo hoje) + "exame normal exclui" (>=3 temas, mais antigo).
- ⚠️ **3 flags de card pendentes** -- ver Proximo passo #2 (1411, 283, 319).
- 🔍 **`card_id=120`** (Gravidez Ectopica) para `/pesquisar-evidencia` -- ver Proximo passo #3.
- ⚠️ **Revisao por Questoes Pediatria (51q) e Ginecologia (57q)** -- unicas tarefas do S16 ainda nao iniciadas, aula de apoio pronta desde a s153.
- 📝 **2 aulas-base candidatas antigas ainda abertas** (DRGE cirurgica+necrose pancreatica; neoplasias intestinais raras).
- `tools/fila_enamed.py` -- superado, considerar aposentar formalmente.
- Achado tecnico nao resolvido: `tools/cronograma.py` perde tema em tarefa "Revisao por Questoes" e desalinha URL em "Teoria" pura.
- Guias estatisticos de UERJ/USP (fase 2, pos-ENAMED) ainda nao existem no repo.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_154.md*
