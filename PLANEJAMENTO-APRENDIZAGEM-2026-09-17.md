---
type: report
layer: root
status: active
relates_to: [AGENTE, AUDITORIA_MEDHUB, ESTADO]
---

# PLANEJAMENTO -- Ensino e Aprendizagem do MedHub (sessao 184, 2026-09-17)

> **Sessao de PLANEJAMENTO, nao de reforma** (decisao do usuario). Este documento sintetiza **todos os achados** do dia -- duas transcricoes absorvidas, quatro varreduras de literatura por subagentes isolados, uma medicao no banco e a atualizacao do grafo de conhecimento -- e converte cada mudanca proposta em **item de fila** para a proxima janela de engenharia (GO do `/ai-eng`, `AGENTE.md §10.6`). Nada de contrato, skill ou codigo foi alterado. O portador **explicativo e duravel** (principio x mecanismo, ledger de friccoes, fontes) e `docs/FUNDAMENTOS-APRENDIZAGEM.md`; este arquivo e o **plano**, e envelhece quando a fila for consumida. Encoding ASCII limpo (`AGENTE.md §4.5`).

---

## 0. Resumo executivo

- **Veredito:** a arquitetura de ensino do MedHub e **confirmada pela literatura em 14 de 17 principios** mapeados; encontrou-se **1 tensao documental** (F109: a justificativa "cluster e pedagogicamente superior" esta errada, o default intercalado esta certo), **1 lacuna de portador** (F110: as friccoes virtuosas nunca foram declaradas), **1 buraco de plano** (F111: a Fase 2 leitura-first nao gera recall no dia da exposicao) e **1 achado de engenharia de severidade ALTA** (F112: a nota 2 e agendada como acerto pelo FSRS; a nota 4 e usada como "certo" padrao em 52% das revisoes).
- **A evidencia mais forte do dia** (Bastani et al. 2025, PNAS, N ~ 1.000): IA que entrega a resposta pronta sobe a pratica em 48% e derruba a prova sem IA em 17%; a versao socratica zera a queda. E o Invariante F, o racional declarado e a triagem humana dos cards, medidos em escala.
- **O que os videos superestimam** (10 afirmacoes, secao 3): "70% esquecido em 24h", "escrever a mao vence digitar", "66 dias para o habito", "FSRS comprovadamente superior para aprender", "Anki aumenta a nota" -- nenhuma sobrevive a fonte primaria como esta.
- **O que muda de imediato (sem reforma):** o agente passa a ler o ledger de friccoes antes de propor qualquer "reducao de atrito"; nao le a regra dos dois finalistas como "primeiro instinto"; trata o `errou` com racional declarado como o insumo mais valioso da Autopsia (hypercorrection).
- **Fila (secao 5):** 11 itens, ordenados; o primeiro e **read-only e de alto valor** (otimizar os parametros do FSRS com as 2.981 revisoes proprias); o mais caro em decisao e o F111 (intake filtrado na Fase 2), com prazo natural em 02/11/2026.
- **Custo da sessao:** 4 varreduras isoladas (~618k tokens de filho, ~49 min de filho, ~23 min de relogio) + 3 extratores do grafo (secao 6) + 1 medicao read-only no `ipub.db`. Zero spawn em cadeia; zero escrita fora do scratch pelos filhos.

---

## 1. Insumos e metodo

| Insumo | O que era | Como foi tratado |
|---|---|---|
| Video 1 -- *The Study System That Made Me A Doctor At The World's Top Hospital* (J.R. Smith) | Learn -> Retain -> Apply; Anki de manha; "estudar para o eu futuro"; efeito de teste; simplicidade | Cada afirmacao virou principio nomeado (P1-P13) e foi checada contra a fonte primaria pela varredura 1 |
| Video 2 -- *I NEVER Take Notes Anymore* (J.R. Smith) | Captura -> resumo -> organizacao por IA; um documento vivo por tema; **friccao viciosa x virtuosa** | Deu a lente do ledger de friccoes (P7, P14-P16); a afirmacao sobre anotar a mao foi derrubada pela replicacao |
| Varredura 1 -- ciencia da aprendizagem (Opus, isolado) | 13 itens: espacamento, intercalacao, curva, teste, dificuldades desejaveis, Mayer, pre-teste, habito, FSRS, Anki x USMLE, troca de resposta, anotar, relearning | 13/13 fechados com fonte primaria; 10 afirmacoes dos videos marcadas SUPERESTIMADAS |
| Varredura 2 -- agentes de IA e offloading (Sonnet, isolado) | Bastani 2025; offloading (3 estudos); tutores socraticos; MCQ por LLM; BKT/DKT/HLR/FSRS; autoexplicacao; vies diagnostico; hypercorrection; seguranca de agentes | 9/9 fechados; Khanmigo e taxa de erro de flashcard-LLM = NAO VERIFICADO |
| Varredura 3 -- engenharia de agentes (Sonnet, isolado) | memoria de agente; guias da Anthropic/Cognition; ADR/living docs; N-of-1; automation bias; friccao em produto; higiene de execucao | 8/8; 6 padroes que faltam ou desafiam o desenho (secao 4.3) |
| Varredura 4 -- GitHub `open-spaced-repetition` (Sonnet, isolado) | inventario, papers, benchmark, Optimizer, retencao-alvo, learning steps, semantica das notas, FSRS-6, leech | 9/9; gerou o F112 e 3 acoes candidatas de FSRS |
| Medicao read-only no `ipub.db` | distribuicao das notas e intervalo por nota no revlog | secao 4.1 (F112) |
| `graphify --update` escopado | 104 arquivos de codigo (AST, gratis) + 43 portadores de governanca/ensino re-extraidos; 536 docs mudados ficam pendentes no manifesto | secao 6 |

**Regra de isolamento aplicada (nova, do usuario):** varredura de web aberta roda em subagente isolado; o principal le so o destilado e o arquivo; conteudo buscado e dado, nunca instrucao. Relatorios crus versionados em `docs/research/2026-09-17-0{1,2,3,4}-*.md`.

---

## 2. O que a evidencia CONFIRMA na arquitetura atual

Cada linha: mecanismo vivo -> principio -> numero que o sustenta (fonte na secao 6 do `FUNDAMENTOS`).

1. **Questoes primeiro + cards em paralelo (60 + 60/dia).** Practice testing e distributed practice sao as duas unicas tecnicas de utilidade ALTA (Dunlosky 2013); questoes e cards sao **preditores independentes** da nota (Deng 2015: +1 ponto por ~445 questoes ou ~1.700 cards).
2. **Cards nascem do erro, nunca de deck importado.** Cards proprios predisseram a nota; o deck comercial pronto **nao** (Deng 2015). O "nunca bulk import" tem lastro empirico, nao so de politica.
3. **Revogacao do aquecimento pre-drill (s170) e recall a frio.** Reler e utilidade BAIXA e o grupo que so reestuda e o **mais confiante e o que menos retem** (Roediger & Karpicke 2006: 61% x 40%, d = 1,26).
4. **Relearning ate nota 4 dentro da sessao + redrill automatico do player.** Successive relearning: +10 pontos na prova; **>60% x <20%** retidos 24 dias depois; o ingrediente e criterio de parada + item voltar na mesma sessao (Rawson 2013).
5. **Gatilho hibrido: questoes antes da aula em tema D5-, aula antes em tema-zero/D8+.** Productive failure d = 0,36 (0,58 com fidelidade; Sinha & Kapur 2021) **desde que** a instrucao posterior use os erros -- exatamente a Revisao Direcionada ancorada nas notas 1-2 e a Autopsia.
6. **Fila intercalada por default.** Intercalar treina discriminacao (ECG 46% x 30%; radiografia 57% x 43%), e a familia nº 1 de erro do usuario e discriminacao.
7. **Invariante F, racional declarado, triagem humana dos cards.** Bastani 2025 (+48% / -17% sem guardrail; 0 de queda com guardrail socratico); Bisra 2018 (autoexplicacao g = 0,55); itens gerados por LLM tem distratores fracos (revisoes 2024-25) -- o juiz pedagogico e humano.
8. **Teto 60/dia, sprint de 120 revogado, cards primeiro no dia.** Consistencia > intensidade e FORTE pela via da memoria (pratica distribuida) e fraca pela via do habito; perder um dia nao quebra a curva (Lally 2010).
9. **Aula-base em HTML com "cada fato uma vez", tabela lado a lado, onboarding de siglas, calibracao por nota.** Coerencia, contiguidade espacial, pre-treino e a resposta ao efeito de reversao por expertise (Mayer).
10. **Curva no nivel do TEMA separada da curva do card.** Nenhum modelo (BKT, DKT, HLR, FSRS) modela esquecimento por tema; o radar de dormencia preenche uma lacuna real. A dissociacao e deduzivel do modelo de Bjork (storage x retrieval strength) e compativel com Kornell & Bjork (mesma exposicao por item, 0,61 x 0,35 em exemplares novos) -- nunca medida em paralelo em medicina.
11. **Regra dos dois finalistas.** Trocar de resposta ajuda na media (51% errada -> certa x 25% certa -> errada), e a crenca contraria piora com a experiencia; o padrao medido do usuario (13/13 na alternativa nao-modal, "facil demais") e uma meta-heuristica de segunda ordem que a literatura de populacao nao cobre -- a regra proibe a troca **sem motivo nomeado**, nao a troca.
12. **Um documento vivo por tema + Regra de Acumulo + contratos versionados.** ADR/living documentation confirmam; nenhuma arquitetura de memoria de agente pesquisada trata memoria procedimental como eixo -- os contratos do MedHub estao a frente.
13. **"Eu orquestro, subagentes varrem".** Anthropic e Cognition convergem: fan-out so para leitura independente; escrita single-threaded.
14. **Complexidade do lado do agente, tres gestos do lado do usuario.** B = MAP (Fogg) como modelo de desenho: gatilho = hook de boot; habilidade = player; frog = cards primeiro.

---

## 3. O que a evidencia CORRIGE (afirmacoes dos videos que nao se sustentam)

| Afirmacao | Veredito | Fonte que derruba |
|---|---|---|
| "70% esquecido em 24h" | erro de categoria (savings != % lembrado), silabas sem sentido, n = 1; em medicina **65-75% retidos em 1 ano** | Ebbinghaus; Murre & Dros 2015; Custers 2010 |
| "Escrever a mao vence digitar / anotar divide a atencao" | duas replicacoes diretas deram nulo | Morehead 2019; Urry 2021 |
| "66 dias para formar um habito" | mediana de faixa 18-254; modelo ajustou em 39/96 | Lally 2010 |
| "FSRS e comprovadamente superior ao SM-2 para aprender" | benchmark mede calibracao de previsao; sem RCT de prova; "20-30% menos revisoes" e simulacao | srs-benchmark (ressalvas dos proprios autores) |
| "Anki aumenta a nota" | observacional; beneficio no Step 1, **ausente no Step 2 CK** (o ENAMED se parece com o Step 2) | Deng 2015; revisao 2026 |
| "Confie no primeiro instinto" | custa pontos; a crenca piora com experiencia | Kruger 2005; Benjamin 1984 |
| "Interleaving sempre vence" | utilidade MODERADA; bloqueio vence ao extrair uma regra unica ou no nivel zero | Dunlosky 2013; Kornell & Bjork 2008 |
| "Aula multimidia bem desenhada produz retencao" | validada em transferencia imediata com novatos; principios invertem em avancados | Mayer; expertise reversal |
| "Bloom 2 sigma" (tutoria = +2 DP) como narrativa de fundo | reanalises 2023-24: g ~ 0,70 | varredura 3 |
| "Nomear o vies cognitivo reduz o erro diagnostico" | unico RCT em estudantes deu nulo; o que muda e pratica com feedback | Sherbino 2014 |

---

## 4. O que a evidencia ACRESCENTA (achados novos para o MedHub)

### 4.1 F112 -- a regua de notas esta deslocada em relacao ao FSRS (ALTA)

- **Regra do motor** (tutorial oficial + codigo instalado `fsrs` 6.3.2): Again = unico lapso; Hard = *recuperou com esforco*, nunca erro parcial; Easy = *sem esforco*; Good = acerto padrao.
- **Regua do agente** (`revisar.md` passo 4): 2 = "recall parcial/na zona **sem o alvo**"; 4 = "cravou conceito + regra-mestre" (o acerto normal). O adaptador passa a nota direto.
- **Medido (read-only, 17/09/2026, `state=2`, 2.981 revisoes):** nota 1 -> 1,0 dia; **nota 2 -> 14,2 dias (312 revisoes)**; nota 3 -> 16,7 dias; **nota 4 -> 34,3 dias (1.551 revisoes = 52%)**. Distribuicao total: 1 = 563 · 2 = 338 · 3 = 528 · 4 = 1.552.
- **Leitura:** o card que o aluno **nao lembrou** volta em duas semanas; o acerto comum ganha bonus de "facil". Causa plausivel de "consolidado 85% / erros frescos 25%" (s169) e das reincidencias de fato arbitrario (F100; #787 pela 3a vez). Limite: medido intervalo agendado, nao retencao por nota -- cruzar com a revisao seguinte e parte da spec.

### 4.2 Oportunidades do ecossistema FSRS (varredura 4)

- **Parametros pessoais:** `Optimizer(review_logs).compute_optimal_parameters()` existe no `fsrs` 6.3.2; minimo oficial 400-1.000 revisoes; o MedHub tem **2.981** (folga de 3-7x) e roda com **default**. Read-only, sem tocar o agendamento ate o operador aceitar os parametros.
- **Retencao-alvo:** 0,90 e o default, nao o otimo pessoal; `compute_optimal_retention()`/CMRR e simulador dizem onde a carga por conhecimento e minima; acima de 0,90 a carga dispara (nao-linear). Retencao de card != retencao de tema.
- **`learning_steps=()`** faz o card novo graduar direto para Review -- coerente com o relearning intra-sessao ser do agente/player, nao do motor; **`enable_fuzzing=False`** so tira o jitter de data.
- **Leech** e recurso do Anki (8 lapsos -> suspender), nao do algoritmo: o SQLite proprio precisa do proprio limiar (lapsos + Difficulty alta) alimentando a fila de reforja. Hoje: contagem de cards com `lapses >= 3` nao medida (query falhou por nome de coluna; item da spec).

### 4.3 Padroes de engenharia que faltam ou desafiam o desenho (varredura 3)

- **Gatilho algoritmico de consolidacao de memoria** (Park et al. 2023: reflection por importancia): o MEMORY.md depende de o agente lembrar de gravar; candidato = hook que acusa sessao com "CONTRATO"/"regra do usuario" sem memoria correspondente.
- **Agente autor = agente avaliador** (escreve a aula e julga se ensinou): a literatura de automation bias preve complacencia; o juiz do rendimento tem de ser o dado do aluno (drill, questao) -- ja e assim por contrato (nota 1-2 dirige a Revisao Direcionada), vale escrever como principio.
- **Desenho N-of-1** para intervencoes pedagogicas (crossover, washout, desfecho = retencao no drill + acerto em questoes novas do tema): sem isso, "aula X melhorou Y" e correlacao.
- **COUNT-ASSERT e nomenclatura local**, sem equivalente de industria para prosa-x-banco -- manter, e nao procurar ferramenta pronta.
- **Hooks deterministas** (Claude Code) confirmam o pre-commit + suite como padrao oficial do proprio fabricante.

### 4.4 Calibracoes de conduta que valem desde ja (sem reforma)

- Ler `FUNDAMENTOS §3` (ledger de friccoes) antes de propor qualquer "reducao de atrito".
- `errou` **com racional declarado e alta confianca** e o insumo mais valioso da Autopsia (hypercorrection, Metcalfe 2017) -- acima do `incerteza`.
- Playbook: a lista de vieses nao muda desempenho sozinha (Sherbino 2014); o teste do override do modal e o **proximo simulado**, nao a releitura do playbook.
- Aula de tema virgem e aula de revisao pedem designs diferentes (reversao por expertise) -- a calibracao D10/D8/D5/D2 ja faz isso; nao achatar.
- Dobrar cards para uma prova de raciocinio clinico nao tem lastro (Step 2 CK) -- o 60/60 fica.

---

## 5. Fila de reformas (planejamento; nada executado; GO do `/ai-eng` por item)

Classes: `spec` (vibeflow, DoD binario) · `doc` (portador de norma, sync obrigatorio) · `decisao` (operador) · `so-dado` (registrado; nada a fazer). Ordem = valor / risco.

| # | Item | Classe | Portador alvo | Evidencia | Esforco |
|---|---|---|---|---|---|
| R1 | **Otimizar parametros do FSRS com o revlog proprio** -- `tools/fsrs_optimize.py` read-only: `Optimizer` + `compute_optimal_retention`; dry-run; saida em `core/fsrs_params.json`; o adaptador so le o arquivo apos GO; teste de paridade default x otimizado sobre 20 cards | `spec` | `app/utils/fsrs.py`, `core/`, `/engenharia-cli` | F112; varredura 4 (d, e, h) | S-M |
| R2 | **Decidir a regua de notas** -- (a) remapear 2 -> Again no adaptador, ou (b) redefinir 3 = acerto padrao, 4 = so sem esforco, 2 = lembrou com esforco (muda `revisar.md` passo 4 e o player) | `decisao` -> `spec` | `revisar.md`, `core/templates/player.html`, `record_review` | F112, P17 | M (toca o caminho unico de escrita) |
| R3 | **Riders do F109** -- ordem intercalada = default deliberado; `--cluster` so onboarding/andaime | `doc` | `fsrs-management-contract.md` v1.4, `revisar.md` passo 1 + `sync_skills` | F109, P6 | S |
| R4 | **Regra de web aberta em subagente isolado** -- rider apos a clausula 10 do §0 (nao altera a clausula 2) | `doc` | `analisar-questao.md §0` + `sync_skills` | decisao do usuario 17/09; Willison 2025; OWASP 2025 | S |
| R5 | **Playbook: answer changing + Sherbino** -- 2 frases: a regra dos dois finalistas nao e "primeiro instinto"; medir o override no proximo simulado | `doc` | `docs/PLAYBOOK_EXECUCAO_PROVA.md` | P13 | S |
| R6 | **Ponteiro do ledger de friccoes** -- clausula curta no contrato + pergunta obrigatoria no template de spec ("qual friccao virtuosa esta spec remove?") | `doc` | `revisao-calibrada-contract.md` v1.5; `.vibeflow/` template | F110 | S |
| R7 | **Leech proprio** -- limiar de lapsos + Difficulty alta -> `reforja.py --marcar --origem leech`; medir antes (quantos cards `lapses >= 3`) | `spec` | `tools/reforja.py`, `fsrs_queue.py` | varredura 4 (i); F100 | S-M |
| R8 | **Intake por tarefa concluida na Fase 2** -- `plano.py --concluir` -> `emed_flashcards --query` -> triagem humana (regenerabilidade) -> `insert_card_base` no dia, dentro do teto | `decisao` -> `spec` | `plano.py`, `insert_card_base.py`, `registrar-sessao.md` | F111; Rawson 2013; Deng 2015 | M; prazo 02/11/2026 |
| R9 | **N-of-1 para testar a regua de notas (R2) e o intake (R8)** -- crossover em blocos equivalentes, washout 1 semana, desfecho = drill + questoes novas | `decisao` (metodo) | `orquestracao-contract` (slot) | varredura 3 (e) | M |
| R10 | **Gatilho de consolidacao de memoria** -- hook que acusa `history/session_NNN.md` com "CONTRATO"/"regra do usuario" sem arquivo de memoria correspondente | `spec` | `tools/hooks/`, `auto_check` | varredura 3 (a) | S |
| R11 | **Grafo em dia** -- `graphify --update` no fechamento de sessao com mudanca em `core/contracts` ou `.claude/commands` (os 536 docs pendentes no manifesto entram em ondas de 3 extratores) | `doc`/`hook` | `.agents/workflows/registrar-sessao.md` | secao 6 | S |

Ja abertos e reafirmados: **F107** (`insert_questao --errors-file --dry-run`, hotfix) e **F99** (`fsrs_queue --card`, read-only) -- ambos removem friccao viciosa (X1, X8).

**Ordem proposta:** R1 (read-only, alto valor) -> R3 + R4 + R5 + R6 num unico commit de docs -> R2 (decisao com o numero do R1 na mao) -> R7 -> R8 (antes de 02/11) -> R9 -> R10 -> R11.

---

## 6. Mapa do grafo (graphify --update, escopo de governanca e ensino)

*Secao preenchida ao fim da atualizacao do grafo (3 extratores Sonnet em execucao no momento da escrita): tamanho antes/depois, god nodes, comunidades que tocam a camada de ensino, conexoes surpreendentes e a posicao do `FUNDAMENTOS` no grafo.*

---

## 7. Custos da sessao (F93, clausula 10)

| Filho | Modelo | Tokens | Minutos | Buscas/tool uses |
|---|---|---|---|---|
| Varredura 1 -- ciencia da aprendizagem | Opus | 178.290 | 16 | 31 buscas / 45 tool uses |
| Varredura 2 -- agentes de IA e offloading | Sonnet | 154.674 | 14 | 25 / 35 |
| Varredura 3 -- engenharia de agentes | Sonnet | 161.177 | 12 | 34 / 39 |
| Varredura 4 -- open-spaced-repetition | Sonnet | 123.522 | 7 | 30 / 34 |
| graphify chunk 1-3 (extracao semantica) | Sonnet | *(a preencher)* | | |
| **Total de pesquisa** | | **~617.7k** | **~49 de filho / ~23 de relogio** | zero sub-delegacao; zero escrita fora do scratch |

---

## 8. Ponteiros

- Principio x mecanismo, ledger de friccoes, fontes: `docs/FUNDAMENTOS-APRENDIZAGEM.md`
- Relatorios crus das varreduras: `docs/research/2026-09-17-0{1,2,3,4}-*.md`
- Ledger: `AUDITORIA_MEDHUB.md §6y` (F108-F112) e lapide no F3
- Grafo: `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.html`
- Sessao: `history/session_184.md`; estado: `HANDOFF.md`, `ESTADO.md`
