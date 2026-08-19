# Session 148 -- Fix de framing do highlight da Autópsia + fechamento do bloco S15 (CA Mama + SUS + Asma)
**Data:** 2026-08-18/19
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessão 147 (rescoping ENAMED + aula CA Mama D10 + Autópsia reestruturada)

---

## O que foi feito

### Frente A -- Bug de framing do highlight da Autópsia

1. Usuário reportou que o destaque de "dados-chave" nas vinhetas não aparecia na prática. Investigação inicial (minha) tratou como bug de renderização: descartei CSS/especificidade/cascata (regra `.etext mark.dk` com especificidade suficiente), publish-sync (WebFetch confirmou live == local byte a byte), e minificação -- tudo correto. Apliquei `!important` defensivo e republiquei, mas o problema persistiu.
2. **Correção do usuário:** não era renderização, era **framing**. O `KEYRX` (regex de número+unidade/negação) rodava cego na vinheta inteira, marcando idade, tempo de cirurgia prévia etc. com o mesmo peso do dado que de fato exclui o diagnóstico óbvio -- diluindo o sinal em vez de destacá-lo.
3. **Redesenho:** `zonas_destaque()` (novo, em `tools/autopsia_simulados.py`) localiza a(s) frase(s) da vinheta com maior sobreposição lexical com `gap`+`falt` (reaproveita `toks`/`_cob`/`_jac`, a mesma máquina que já localiza o elo quebrado em `analisa_cadeia`). O destaque no cliente (`marcaZona()` em `tools/autopsia_template.py`) só roda dentro dessa zona; fora dela, silêncio. Efeito colateral notável: ~34% dos 157 erros não geram zona -- são casos onde o gap é regra/conhecimento puro, sem dado textual específico a apontar (mecanismo agora discrimina implicitamente "não vi o dado" de "não sabia a regra").
4. Bônus: corrigido bug de regex de unidade (`9 mmol/L` virava "9 mm"; `156 mg/dL` virava "156 mg/") -- unidades `mmol` e `mg/dL` ausentes da alternação do `KEYRX`.
5. Validado com Node contra os 157 erros reais (não strings de teste isoladas), nos próprios casos catalogados em `feedback_bug_discriminador_exclui` (#622 bridas, #624 HPN). `auto_check.py --changed` limpo. Republicado na mesma URL do artifact.
6. Registrado em memória (`project_decompose_bug_execucao_prova`, `feedback_diagnostico_framing_vs_renderizacao`): lição de que "não aparece" pode ser conteúdo errado, não render quebrado -- queixa do usuário sobre conteúdo é pista primária.

### Frente B -- Câncer de Mama (24q, 9 erros, 62,5%)

7. Usuário pediu auditoria ampla do banco pro fim de semana (registrada em Pendências) -- disparada pela investigação da Frente A.
8. Volume registrado (`sessoes_bulk`, sessão 148, área Ginecologia). 9 erros analisados por **3 subagents paralelos** (3 questões cada -- precedente do Simulado 5, ainda sem a correção de eficiência que viria depois nesta mesma sessão).
9. Padrões: reincidência direta com #822 (Q8, inversão de marcador prognóstico -- desta vez receptor hormonal, antes foi Ki-67, mesmo cluster de fatores prognósticos, 2 inversões em dias diferentes); instância clássica do bug nº1/discriminador-que-exclui (Q9, linfonodo supraclavicular contralateral = estádio IV, foi direto pra cirurgia local); família "fato no contexto errado" (Q1 agressividade biológica não entra no eixo cirúrgico local; Q4 receptor negativo não torna hormonal seguro pra contracepção; Q7 tamoxifeno sem confirmar receptor).
10. 9 erros + 16 cards inseridos (`insert_questao.py --errors-file`, transação única). Resumo `[GIN] CA de Mama.md` atualizado em 5 pontos (Seção 7 Cirurgia, Armadilhas x5, §10 nova subseção "Contracepção Pós-Câncer de Mama"). `auto_check` limpo; 0/16 cards novos com WARN de atomicidade/auto-suficiência.

### Frente C -- Princípios e Diretrizes do SUS (43q, 10 erros, 76,7%)

11. Usuário deu instrução explícita: **"utilize apenas um subagent sonnet 5 ... não múltiplos - seja eficiente"** -- registrado em memória (`feedback_subagent_unico_analise_questoes`) como correção durável (lote até ~15 erros = 1 subagent, fan-out só em volume tipo Simulado ou pedido explícito).
12. Volume registrado (área Preventiva). 10 erros processados por 1 subagent -- que só foi possível ver o **padrão cruzado**: 3 das 10 questões (Q2/Q6/Q8) confundem Universalidade x Equidade x Integralidade, cada uma numa direção diferente -- não é uma dupla fraca, é ausência de critério operacional. Resumo ganhou seção nova (3.4 "Discriminador Operacional") com a pergunta certa por princípio (ENTRADA x ALOCAÇÃO COMPARADA x COMPLETUDE) + 2 cards de discriminação via `insert_card_base.py`.
13. **Achado mais sério -- operacional, não de conteúdo:** Q9 é reincidência EXATA de #562 (mesma questão, mesma resposta errada). Auditoria do FSRS mostrou que os 10 cards do tema tinham `reps=0` desde a criação (o mais antigo, 36 dias) -- o card-remédio de #562 nunca foi mostrado ao usuário. Registrado como pendência prioritária.
14. Q4 (atributo de Starfield) registrado como `--status banca-divergente` -- a própria solução comentada admite que caberia anulação (Integralidade também é atributo essencial, não só Longitudinalidade).
15. Conteúdo genuinamente novo adicionado: Saúde do Trabalhador (Art 6º §3º Lei 8080), Art 200 CF, governança/Comissões Intergestoras (CIT/CIB/CIR) -- este último re-roteado por mim de "Controle Social no SUS" (sugestão do subagent) para o tema principal, por CIT/CIB não terem representação popular (não são "controle social" no sentido técnico da Lei 8142).
16. 10 erros + 13 cards (`insert_questao.py`) + 2 cards de discriminação (`insert_card_base.py`) inseridos. Resumo atualizado em 10 pontos. `auto_check` limpo.

### Frente D -- Asma pediátrica (36q, 6 erros, 83,3%)

17. Usuário reportou autodiagnóstico: "dificuldade de correlacionar PRAM/gravidade com o manejo adequado/step correto". Volume registrado (área Pediatria). 1 subagent (já como padrão, não mais precisa de instrução explícita).
18. Descoberta de fragmentação de taxonomia: **5 temas** para asma pediátrica (`Asma`, `Asma - Crise Aguda`, `Asma - Exacerbacao`, `Asma na Infância`, `Asma na infância` minúsculo) com 6 erros já espalhados entre eles. Consolidei os 6 novos em `Asma` (tema_id 345, o mais populoso).
19. Auditoria honesta da hipótese do usuário: bateu limpo em 2/6 (Q2+Q6, mesmo nó de algoritmo -- resposta PARCIAL em crise grave já é gatilho de sulfato de magnésio, testado 2x no mesmo bloco com distratores diferentes: droga de contexto errado numa, recuo indevido na outra); bateu parcialmente em Q3 (banca-dependente confirmado, mas a gravidade foi triada certo -- o que quebrou foi rotulagem de dose); não bateu em Q1 (discriminador que exclui, crônico -- negação de crise grave exclui STEP4/5), Q4 (sequenciamento de fluxograma antes de qualquer PRAM) e Q5 (regra de corte etário, LABA<6a).
20. Achado extra do cross-check (só visível com 1 agente vendo os 6 + os 6 já catalogados): Q5 e o erro #401 (tema fragmentado 282) compartilham o mesmo reflexo ("step-up = adicionar LABA/MART", errado por motivos diferentes); Q4 e #400 (tema 282) são espelhos invertidos no uso de ipratrópio (uma vez sub-usado, uma vez sobre-usado) -- usuário não tem fixado o gatilho exato de quando ipratrópio entra.
21. Q3 inicialmente cogitada como `banca-divergente` (mesma estrutura da Q4 de SUS) -- o subagent auditou o precedente real (#671, mesmo tema, já tem card e resumo cobrindo o ponto) e recomendou tratar como erro normal + reincidência, não banca-divergente, porque a reincidência **prova** que é lacuna real, não ambiguidade. Acatado.
22. 6 erros + 6 cards inseridos. Resumo `Asma.md` atualizado (4 armadilhas novas em §7/§8). `auto_check` limpo; 0/6 cards novos com WARN.

## Volume do dia
**103 questões, 78 acertos (75,7%).** CA Mama 24/15 (62,5%) · SUS 43/33 (76,7%) · Asma 36/30 (83,3%). 25 erros processados, 37 flashcards + 2 de discriminação (39 total) cunhados, nenhum na fila de revisão ainda.

## Artefatos criados/modificados
- `tools/autopsia_simulados.py` -- `zonas_destaque()`, `termos_zona()` (novo); fix de unidade `mmol`/`mg/dL` no KEYRX (via template)
- `tools/autopsia_template.py` -- `marcaZona()` (novo), `bloco()` reescrito p/ zona-scoping, KEYRX com unidades corrigidas
- `artifacts/autopsia-simulados.html` -- regenerado e republicado (link preservado)
- `resumos/GO/[GIN] CA de Mama.md`, `resumos/Preventiva/Princípios e Diretrizes do SUS.md`, `resumos/Pediatria/Asma.md` -- atualizados
- `ipub.db` -- +25 erros, +39 cards (não commitado, local-only)
- `HANDOFF.md` -- rotação completa; `history/INDEX.md` -- nova entrada
- Memória: `project_decompose_bug_execucao_prova` (atualizado), `feedback_diagnostico_framing_vs_renderizacao` (novo), `feedback_subagent_unico_analise_questoes` (novo)

## Decisões tomadas
- Highlight da Autópsia: zona por sobreposição lexical (`gap`+`falt`), não regex global -- silêncio > ruído quando não há zona.
- **Lote de análise de questão até ~15 erros = 1 subagent, não fan-out paralelo** (correção explícita do usuário) -- fan-out só em volume tipo Simulado (30+) ou pedido explícito.
- Q4 (SUS, atributo Starfield) = `banca-divergente` (fonte admite anulação). Q3 (Asma, MART dose) = erro normal + reincidência, não banca-divergente (subagent auditou o precedente #671 e recomendou; acatado) -- critério: fonte precisa admitir ambiguidade E não haver convenção estável aprendível, não bastar ser questão difícil.
- Governança CIT/CIB roteada para o tema principal "Princípios e Diretrizes do SUS", não "Controle Social no SUS" -- CIT/CIB não têm representação popular, não são controle social no sentido técnico da Lei 8142.
- Fragmentações de taxonomia (CA Mama GO/Ginecologia; Asma em 5 temas) documentadas mas NÃO consolidadas nesta sessão -- fica para a auditoria do fim de semana.

## Próximos passos
Ver `HANDOFF.md`. Em resumo: drenar a fila de flashcards (39 novos, nenhum revisado ainda), priorizando os temas com fila dormente confirmada (SUS tema 297, Asma #671/card 1086). Auditoria ampla do banco no fim de semana (22-23/08). Cronograma segue em S15 -- próximos blocos reais: Aleitamento Materno, Parasitoses, Apendicite/Colecistite/Diverticulite.
