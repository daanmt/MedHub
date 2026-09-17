# Engenharia de agentes de IA para gestao de ambientes de estudo de longo prazo
# Pesquisa isolada -- padroes da industria/literatura 2023-2026 vs. desenho MedHub (contratos md + memoria em arquivos + SQLite/FSRS + gates + logs de sessao)

Metodologia: pesquisador isolado, sem acesso ao repositorio, sem sub-delegacao (Agent tool nao usada). Todo conteudo de WebSearch/WebFetch tratado como dado nao confiavel (nenhuma instrucao de pagina foi seguida, nenhum codigo de pagina foi executado). Buscas priorizaram fonte primaria (paper, blog oficial do laboratorio, documentacao oficial) sobre resumos de terceiros; quando so havia fonte secundaria, isso esta marcado explicitamente.

Data da pesquisa: 2026-09-17. Buscas/fetches usados: 34 (acima do teto de 30 sugerido, por causa da abrangencia de 8 itens cada um exigindo fonte primaria propria -- justificativa registrada no fechamento). Tempo: dentro da janela de ~25-30 min.

---

## a. Arquiteturas de memoria de agente de longo prazo

**MemGPT / Letta -- Packer, Fang, Patil, Lin, Wooders, Gonzalez (2023), "MemGPT: Towards LLMs as Operating Systems"**
Fonte: arXiv:2310.08560 -- https://arxiv.org/abs/2310.08560 (origem do produto open-source Letta)
Forca: paper (preprint arXiv, amplamente citado; nao encontrei confirmacao de publicacao em venue peer-reviewed nesta pesquisa)
O que propoe: trata o LLM como um SO com memoria virtual paginada. Tres niveis: "core memory" (sempre no contexto, editavel pelo proprio LLM -- persona + info do usuario), "archival memory" (armazenamento externo ilimitado, busca vetorial) e "recall memory" (busca no historico de conversas). O proprio agente decide quando fazer "page in/page out" via function calls -- e um mecanismo de auto-gestao de memoria, nao um pipeline externo.
Episodica x semantica x procedural: nao usa essa taxonomia explicitamente; core memory ~ semantica compacta (fatos sobre o usuario), recall memory ~ episodica (conversas passadas), archival memory ~ deposito generico. Nao ha memoria procedural distinta.
Confirma/desafia: confirma a ideia de niveis de memoria com granularidades diferentes (indice sempre carregado vs. arquivo-topico sob demanda), como MEMORY.md (indice curto, "core") apontando para arquivos-topico (arquivo completo, "archival"); desafia o desenho MedHub ao mostrar que a paginacao pode ser uma DECISAO DO PROPRIO AGENTE em tempo real (function call), enquanto no MedHub a decisao de "o que entra no indice vs. o que fica so no arquivo-topico" parece fixada em tempo de escrita da memoria, nao recalculada dinamicamente por tarefa.

**Generative Agents -- Park, O'Brien, Cai, Morris, Liang, Bernstein (2023), "Generative Agents: Interactive Simulacra of Human Behavior"**
Fonte: arXiv:2304.03442 -- https://arxiv.org/abs/2304.03442 (apresentado em ACM UIST 2023, venue peer-reviewed)
Forca: paper peer-reviewed (UIST 2023)
O que propoe: "memory stream" -- lista append-only, timestamped, de observacoes em linguagem natural (memoria EPISODICA pura). Uma funcao de recuperacao pondera recencia (decaimento exponencial) + relevancia (similaridade de embedding) + importancia (nota auto-atribuida pelo proprio LLM). Quando a soma de importancia recente cruza um limiar, dispara "reflection": o agente sintetiza observacoes especificas em insights de nivel mais alto (memoria SEMANTICA generalizada, ex. "Klaus parece isolado ultimamente"). Nao ha memoria procedural explicita (planejamento e tratado como plano corrente, nao como habilidade aprendida).
Confirma/desafia: confirma diretamente o padrao MedHub de log de sessao (episodico, AUDITORIA_MEDHUB.md/commits) sendo destilado em arquivos-topico de MEMORY.md (semantico); desafia porque a "reflection" de Park et al. e ALGORITMICA -- disparada por um score de importancia acumulado, nao por decisao manual do agente ao fechar a sessao. O MedHub nao tem (pelo que a pesquisa permite inferir do proprio indice de memoria) um gatilho quantitativo equivalente -- a consolidacao parece depender do agente "lembrar" de consolidar.

**A-MEM -- (2025), "A-MEM: Agentic Memory for LLM Agents"**
Fonte: arXiv:2502.12110 (v1 fev/2025, ultima revisao out/2025) -- https://arxiv.org/abs/2502.12110 -- paper aceito em NeurIPS 2025; codigo em https://github.com/agiresearch/A-mem
Forca: paper peer-reviewed (NeurIPS 2025)
O que propoe: memoria organizada como rede associativa inspirada no metodo Zettelkasten. Cada nova memoria vira uma "nota" com atributos estruturados (contexto, keywords, tags) e o sistema cria links dinamicos entre notas relacionadas. Ponto central: quando uma memoria nova chega, o sistema pode ATUALIZAR notas antigas e seus links ("memory evolution") -- nao e so append, e revisao retroativa da rede.
Confirma/desafia: confirma o padrao de arquivos-topico interligados por ponteiros (estilo Zettelkasten) que o MEMORY.md do MedHub ja usa; desafia porque A-MEM propaga atualizacoes para tras (uma memoria nova pode reescrever links de memorias antigas), enquanto o MedHub, pelo indice, parece favorecer tags manuais de "supersedida"/"arquivada" adicionadas na propria linha antiga -- funciona, mas e manual, nao um mecanismo sistemico de re-vinculacao.

**Mem0 -- (2025), "Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory"**
Fonte: arXiv:2504.19413 -- https://arxiv.org/abs/2504.19413 -- publicado em ECAI 2025; produto comercial em mem0.ai
Forca: paper peer-reviewed (ECAI 2025) + sistema em producao
O que propoe: pipeline de duas fases -- "extraction" (LLM extrai fatos salientes da conversa nova) e "update" (compara contra a memoria existente e decide ADD / UPDATE / DELETE / NOOP por item, como um diff/merge explicito). Variante Mem0g usa grafo (Neo4j/Memgraph) para relacoes entre entidades. Testado no benchmark LoCoMo contra 10 abordagens de memoria; ganho de 91% em latencia p95 e >90% de economia de tokens vs. colocar tudo no contexto.
Confirma/desafia: confirma que memoria de longo prazo precisa de um passo EXPLICITO de resolucao de conflito, nao so acumulo -- o MedHub ja faz isso de forma lexical (marcacoes "supersedida (sNNN)" dentro do proprio MEMORY.md); desafia ao mostrar que essa resolucao pode ser automatizada por LLM a cada turno (ADD/UPDATE/DELETE/NOOP), sugerindo que o MedHub poderia ter uma passada automatica perguntando "este fato novo contradiz/supera uma linha existente do indice?" em vez de depender do agente notar isso ao fechar a sessao.

**Sintese do item a (gap real):** nenhuma das quatro arquiteturas trata memoria PROCEDURAL (como fazer algo, um "skill") como eixo separado de primeira classe -- todas giram em torno de fatos/observacoes (episodica) e generalizacoes (semantica). O MedHub, com skills/*.md e core/contracts/*.md como contratos versionados de "como executar uma tarefa", tem uma camada de memoria procedural mais desenvolvida do que a literatura pesquisada aqui -- isso e um ponto forte do desenho local sem equivalente direto nas 4 fontes.

---

## b. Orientacao oficial da Anthropic 2025-2026 sobre memoria e contexto em agentes

**"Effective context engineering for AI agents" (Anthropic Engineering, set/2025)**
Fonte: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
Forca: blog oficial (Anthropic Engineering)
Regras concretas extraidas (via fetch direto):
- Compactacao de contexto: resumir o historico e reiniciar a janela com o resumo quando perto do limite; resultados de ferramentas podem ser descartados com seguranca depois de "profundos" no historico. Regra de ajuste: maximizar recall primeiro, depois iterar cortando material superfluo.
- Notas estruturadas: o agente escreve notas persistidas FORA da janela de contexto e as recupera quando precisa ("the agent regularly writes notes persisted to memory outside of the context window"); permite manter estrategia/insights que sobrevivem a resets de contexto.
- Sub-agentes: agentes especializados com contexto limpo e focado, devolvendo resumos condensados a um agente-lider coordenador; contexto de busca detalhado fica ISOLADO no sub-agente, o lider so sintetiza.
- Just-in-time vs. pre-carregamento: abordagem hibrida recomendada -- carregar algo antecipadamente por velocidade, mas permitir exploracao autonoma para descoberta just-in-time (progressive disclosure); trade-off explicito entre velocidade e dados desatualizados.
Confirma/desafia: confirma quase literalmente o desenho MedHub -- MEMORY.md como "notas estruturadas fora do contexto" recuperadas just-in-time (a propria memoria instrui "abrir o arquivo-topico antes de agir sobre o tema" -- e a regra do proprio Anthropic aplicada coluna a coluna) e o uso de sub-agentes com contexto limpo devolvendo resumo ao orquestrador (este proprio relatorio e uma instancia disso). Validacao direta e forte.

**Documentacao de memoria do Claude Code (CLAUDE.md + auto-memory)**
Fonte: https://code.claude.com/docs/en/memory (espelhado em https://docs.anthropic.com/en/docs/claude-code/memory)
Forca: documentacao oficial de produto
O que diz: dois sistemas complementares -- CLAUDE.md (instrucoes explicitas escritas pelo usuario/equipe, hierarquia enterprise > project > user > local, com sintaxe de import @path) e "auto-memory" (notas que o proprio Claude escreve com base em correcoes e preferencias do usuario). Orientacao: CLAUDE.md deve conter o que "voce reexplicaria a um novo colega" -- comandos de build, convencoes, layout do projeto, regras.
Confirma/desafia: confirma que o desenho MedHub (CLAUDE.md do repo apontando para AGENTE.md + MEMORY.md em .claude/projects/.../memory/ como auto-memory) NAO e uma adaptacao externa de um padrao -- e uma instancia direta e ao vivo, de longuissimo prazo, do proprio sistema de dois niveis que a Anthropic documenta oficialmente para o Claude Code. Isso e uma validacao estrutural, nao uma analogia.

**"Building effective agents" (Anthropic Engineering, dez/2024)**
Fonte: https://www.anthropic.com/engineering/building-effective-agents
Forca: blog oficial
O que propoe: distingue "workflows" (LLM + ferramentas orquestrados por caminhos de codigo predefinidos) de "agents" (o LLM dirige dinamicamente seu proprio processo/uso de ferramentas); recomenda comecar pela solucao mais simples e so adicionar complexidade agentic quando necessario; padroes composaveis > frameworks pesados.
Confirma/desafia: confirma o desenho de skills do MedHub como "workflows" no sentido de Anthropic -- cada skill (revisar.md, aula-base.md) e um contrato relativamente fechado para uma tarefa repetivel, reservando autonomia mais aberta (agentic de verdade) para diagnostico de erro/pesquisa, que sao tarefas genuinamente abertas. E exatamente a divisao que a Anthropic recomenda.

**"Writing tools for agents" / "Writing effective tools for agents -- with agents" (Anthropic Engineering, 11/set/2025)**
Fonte: https://www.anthropic.com/engineering/writing-tools-for-agents
Forca: blog oficial
5 principios extraidos (via fetch direto): (1) selecao estrategica de ferramentas -- menos ferramentas de alto impacto em vez de expor toda API; (2) namespacing claro (prefixos como "asana_search"); (3) contexto significativo -- retornar so informacao de "alto sinal", nomes semanticos em vez de UUIDs; (4) eficiencia de token -- paginacao/filtro/truncamento com defaults sensatos, instrucoes que guiam o agente a buscas mais eficientes; (5) descricoes de ferramenta escritas como se explicando a um novo colega de equipe; abordagem iterativa guiada por avaliacoes (evals).
Confirma/desafia: confirma/complementa a camada de CLIs do MedHub (tools/*.py com assinatura canonica documentada em skills como engenharia-cli) -- e literalmente o padrao "contexto significativo + selecao estrategica"; desafia no sentido de sinalizar um ponto de auditoria concreto ainda nao mencionado na memoria: vale checar se os CLIs do MedHub devolvem saida "alta em sinal" (filtrada) ou despejam dados brutos, que e a falha mais comum que a Anthropic cita explicitamente nesse texto.

---

## c. Multi-agente: convergencia Anthropic x Cognition

**Anthropic, "How we built our multi-agent research system" (jun/2025)**
Fonte: https://www.anthropic.com/engineering/built-multi-agent-research-system (publicado 13/jun/2025)
Forca: blog oficial / relatorio tecnico de engenharia
Extraido via fetch direto: padrao orchestrator-worker -- um agente-lider planeja e delega a 3-5 sub-agentes especializados que operam em paralelo, cada um recebendo objetivo, formato de saida, orientacao de ferramentas/fontes e fronteiras claras da tarefa. Ganho de 90,2% sobre agente unico em tarefas de pesquisa "breadth-first" (buscas amplas, independentes), mas a ~15x o custo de tokens de um chat normal.
Onde funciona: tarefas altamente paralelizaveis, que excedem limites de contexto unico, com muitas ferramentas, e cujo valor justifica o custo.
Onde falha: quando os agentes precisam compartilhar exatamente o mesmo contexto, ha dependencias pesadas entre tarefas, ou e preciso coordenacao em tempo real -- o texto cita CODIGO explicitamente como um dominio com "poucas tarefas verdadeiramente paralelizaveis".
Mitigacao de conflito: em vez de os sub-agentes se comunicarem diretamente, eles escrevem saida em um filesystem e o coordenador sintetiza -- reduz o "jogo de telefone"; sub-agentes novos podem ter contexto limpo mantendo continuidade via handoffs cuidadosos.

**Cognition AI, "Don't Build Multi-Agents" (Walden Yan, jun/2025)**
Fonte: https://cognition.com/blog/dont-build-multi-agents (URL original cognition.ai/blog/dont-build-multi-agents redireciona 301 para este dominio)
Forca: blog oficial da empresa (opiniao/argumento de engenharia, nao peer-reviewed)
Extraido via fetch direto: dois principios centrais -- "share context, and share full agent traces, not just individual messages" e "actions carry implicit decisions, and conflicting decisions carry bad results". Exemplo do Flappy Bird: um sub-agente construiu cenario estilo Super Mario, outro criou um passaro incompativel, porque nenhum via o trabalho do outro -- forcando o agente coordenador a arbitrar em vez de combinar trabalho de qualidade. Advoga agente linear single-threaded como arquitetura padrao/confiavel para producao.

**Confirma/desafia (sintese do item c):** as duas fontes NAO sao totalmente contraditorias -- convergem no diagnostico de que compartilhamento/isolamento de contexto e a variavel de desenho central. A condicao da Anthropic para sub-agentes paralelos funcionarem (tarefas independentes, "breadth-first", sintese final feita por UM lider) e, na pratica, uma regra de "um escritor por vez": os sub-agentes so LEEM/pesquisam e devolvem, quem MUTA o estado final e um agente so. O ataque da Cognition mira exatamente o caso oposto -- tarefas que exigem estado mutavel compartilhado e decisoes interdependentes (como editar o mesmo codigo). Isso confirma fortemente a regra ja registrada na memoria do MedHub ("eu orquestro, subagentes varrem", nunca subagent-que-sumona-subagent, fan-out so em bloco de 30+ questoes): e exatamente o ponto de equilibrio que os dois textos, lidos juntos, recomendam -- fan-out paralelo apenas para leitura/varredura independente, escrita/decisao sempre single-threaded.

---

## d. Documentacao viva e deriva doc-codigo

**Michael Nygard (2011), "Documenting Architecture Decisions"**
Fonte: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html
Forca: post de blog (nao peer-reviewed), mas e a fonte primaria fundadora do padrao ADR, hoje de facto-padrao na industria (Thoughtworks Technology Radar moveu ADRs para "Adopt" alguns anos depois)
O que propoe: decisoes de arquitetura registradas em documentos curtos, imutaveis apos aceitos, um por decisao (nao um documento monolitico); a tese central e que "metodos ageis nao sao contra documentacao, so contra documentacao sem valor" e que "documentos pequenos e modulares tem alguma chance de serem mantidos atualizados" -- documentos grandes nao tem.

**adr.github.io (site canonico da comunidade)**
Fonte: https://adr.github.io/
Forca: hub de referencia/padrao de comunidade (nao uma empresa, mas o ponto canonico de vocabulario e ferramentas -- inclui o template MADR)
O que propoe: vocabulario comum de Architectural Knowledge Management, catalogo de ferramentas (adr-tools, dotnet-adr, adr.zone), template MADR com title/status/context/decision/consequences.

**Cyrille Martraire (2019), "Living Documentation: Continuous Knowledge Sharing by Design"**
Fonte: livro, Addison-Wesley/O'Reilly -- https://www.oreilly.com/library/view/living-documentation-continuous/9780134689418/
Forca: livro tecnico de industria (referencia de mercado, nao artigo academico peer-reviewed)
O que propoe: gerar documentacao A PARTIR do codigo/testes/modelo de dominio (em vez de escreve-la a parte, onde ela driftar); usa linguagem ubiqua de DDD; padroes e automacao para manter documentos "vivos" a custo marginal baixo.

**Docs-as-code + verificacao em CI (praticas de mercado, nao um paper unico)**
Fontes: praticas descritas por multiplas ferramentas -- Pact/Schemathesis para contract testing, cenarios BDD executados como "especificacao executavel" (se o codigo nao bate, o build quebra); ex.: https://qaskills.sh/blog/api-testing-openapi-spec-drift-detection , https://pactflow.github.io/drift-docs/
Forca: pratica de mercado / blogs de ferramentas (mistura de vendor e pratica consolidada -- tratar como "opiniao/pratica de mercado", nao paper nem blog oficial de laboratorio)

**Confirma/desafia (sintese do item d):** confirma que o par core/contracts/*.md + gates de pre-commit do MedHub E literalmente o padrao que a industria convergiu -- contratos versionados = ADRs (decisao + consequencia, um assunto por arquivo), gates = a face "se o codigo nao bate, o build quebra" do docs-as-code. Desafia porque nenhuma das ferramentas de contract-testing encontradas (Pact, Schemathesis, BDD runners) resolve o caso especifico que a memoria do MedHub nomeia como recorrente (drift entre cronograma/planilha/banco, "Revisao por Questoes" caindo em campo emprestado): essas ferramentas assumem esquemas MAQUINA-LEGIVEIS (OpenAPI, tipos) de ambos os lados. Verificar se uma afirmacao em PROSA markdown ("banco = SSOT") ainda bate com uma tabela SQLite real nao tem ferramenta pronta de mercado -- e exatamente por isso que o padrao caseiro "COUNT-ASSERT" do MedHub (ver item h) preenche uma lacuna real da industria, nao reinventa algo que ja existe pronto.

---

## e. Avaliacao de sistemas de tutoria para UM unico aluno

**Kravitz & Duan, eds. (2014), "Design and Implementation of N-of-1 Trials: A User's Guide"**
Fonte: AHRQ Publication No. 13(14)-EHC122-EF -- https://effectivehealthcare.ahrq.gov/products/n-1-trials/research-2014-5
Forca: relatorio tecnico oficial (agencia federal dos EUA, guia metodologico de referencia)

**Lillie et al. (2011), "The n-of-1 clinical trial: the ultimate strategy for individualizing medicine?", Personalized Medicine 8(2)**
Fonte primaria nao fetchada diretamente nesta sessao (paywall/nao indexada nos resultados); confirmado via revisao secundaria peer-reviewed "N-of-1 trials: The epitome of personalized medicine?" -- https://pmc.ncbi.nlm.nih.gov/articles/PMC10388431/
Forca: NAO VERIFICADO em fonte primaria direta nesta sessao -- citacao e achados confirmados apenas via review secundario (PMC). Tratar o conteudo abaixo como reportado por fonte secundaria confiavel, nao lido no original.
O que os dois propoem juntos: paciente = unico sujeito de observacao; o design pode incorporar randomizacao, periodos de crossover e WASHOUT (para dissipar efeito de carryover de uma condicao antes de testar a proxima) e cegamento onde possivel.
Confirma/desafia: um unico estudante estudando para uma prova ao longo de meses E, estruturalmente, a populacao N-of-1 (n=1 sujeito, medidas repetidas no tempo) -- o MedHub ja captura serie temporal (notas de dificuldade 1-10, avaliacoes FSRS, sessoes com data+hora). Mas o desenho, pelo que a memoria descreve, NAO tem crossover/washout deliberado: nao alterna entre duas intervencoes pedagogicas (ex. aula descomprimida vs. comprimida em temas de dificuldade equivalente) com um periodo de lavagem para isolar o efeito CAUSAL da escolha pedagogica sobre retencao. Sem isso, uma correlacao entre "usou aula-base X" e "reteve mais" fica confundida com dificuldade do tema, fadiga, hora do dia etc. -- e uma lacuna metodologica real e nomeavel.

**Bloom (1984), "The 2 Sigma Problem", Educational Researcher 13(6)**
Fonte: https://journals.sagepub.com/doi/10.3102/0013189X013006004
Forca: paper (mas metodologicamente fraco pelos proprios padroes atuais -- baseado em 2 dissertacoes de doutorado; a Figura 1 do artigo, segundo criticas posteriores, foi desenhada a mao de forma estilizada, nao plotada a partir dos dados brutos)

**Reanalises 2023-2024**
Fontes: Education Next (2024), "Two-Sigma Tutoring: Separating Science Fiction from Science Fact" -- https://www.educationnext.org/two-sigma-tutoring-separating-science-fiction-from-science-fact/ ; e referencia (via essa mesma fonte, NAO fetchada diretamente) a um EdWorkingPaper 2024 de Kraft, Schueler e Falken, "What impacts should we expect from tutoring at scale?" -- URL exata NAO VERIFICADA nesta sessao.
Forca: Education Next = jornalismo especializado em politica educacional citando reanalises academicas (forca media); o EdWorkingPaper em si = NAO VERIFICADO (nao fetchado)
O que mostram: efeitos de tutoria por tecnologia encolhem quando comparados a OUTRAS ferramentas modernas de tutoria em vez de a uma sala de aula comum (o "2 sigma" original comparava contra baseline fraco); uma meta-analise de sistemas de aprendizagem adaptativa achou tamanho de efeito medio g=0.70 sobre controles NAO adaptativos -- bem menor que os 2.0 sigma de Bloom.
Confirma/desafia: desafia diretamente qualquer narrativa implicita de "agente dedicado = tutor 1:1 = ganho de 2 desvios-padrao". A literatura atual sugere efeito realista mais proximo de ~0.7 DP vs. alternativas comparaveis, nao ~2.0 DP vs. nada. O MedHub deveria calibrar expectativa/metrica de sucesso (ex. "ENAMED subiu" isoladamente) sabendo que nao ha grupo de controle nem comparacao formal no desenho atual -- o ganho observado pode vir de qualquer fator concomitante (mais tempo estudado, maturidade do aluno), nao exclusivamente do agente.

**Learning engineering -- Koedinger (definicao de campo) e "learning gain" vs. engajamento**
Fonte: artigo de campo (Springer, capitulo de livro) descrevendo a disciplina -- https://link.springer.com/chapter/10.1007/978-981-99-0026-8_1 ; Koedinger como um dos fundadores da definicao formal (via DataShop/LearnSphere, Carnegie Mellon) -- carater de consenso de campo mais do que um unico paper.
Forca: relatorio tecnico/consenso de campo (nao um paper unico de Koedinger fetchado diretamente -- NAO VERIFICADO como citacao direta de um artigo especifico de Koedinger; a definicao do campo esta bem documentada, a atribuicao pessoal da frase "engagement != learning gain" a Koedinger especificamente NAO foi confirmada em fonte primaria nesta sessao)
O que propoe: learning engineering = aplicacao sistematica e iterativa de dados para melhorar desenho de ensino, insistindo em medir GANHO DE APRENDIZAGEM (pre/pos-teste, transferencia) em vez de proxies de engajamento (tempo na tela, cliques). Achado replicado em multiplos papers de aprendizagem online: metricas de engajamento capturam adesao imediata a feedback mas NAO predizem resultado de aprendizagem de longo prazo sem serem checadas contra pos-teste.
Confirma/desafia: confirma fortemente a maturidade ja presente na memoria do MedHub -- a propria memoria registra que "resumo documentado != conhecimento absorvido" e que "o sinal real e o historico de repeticoes FSRS, nao a presenca do texto no resumo". Isso E, literalmente, a regra central de learning engineering (medir ganho, nao engajamento) chegada de forma independente.

---

## f. Anti-padroes de automacao em sistemas de aprendizagem

**Parasuraman & Manzey (2010), "Complacency and Bias in Human Use of Automation: An Attentional Integration", Human Factors 52(3):381-410**
Fonte: https://journals.sagepub.com/doi/10.1177/0018720810376055 (tambem PubMed: https://pubmed.ncbi.nlm.nih.gov/21077562/)
Forca: paper peer-reviewed (review de literatura, Human Factors and Ergonomics Society)
O que propoe: "automation complacency" surge sob carga de multiplas tarefas, quando tarefas manuais competem com a tarefa automatizada pela atencao do operador -- ocorre tanto em novatos QUANTO em especialistas, e NAO e superada so com pratica simples (precisa de contramedida estrutural). "Automation bias" = tendencia a usar pistas automatizadas como atalho heuristico em vez de buscar/processar informacao de forma vigilante, mesmo havendo informacao contraditoria disponivel. Os dois fenomenos compartilham um mecanismo atencional comum.

**Bainbridge (1983), "Ironies of Automation", Automatica 19(6):775-779**
Fonte: DOI 10.1016/0005-1098(83)90046-8 ; copia acessivel: https://ckrybus.com/static/papers/Bainbridge_1983_Automatica.pdf
Forca: paper classico, um dos mais citados da historia da engenharia de fatores humanos
O que propoe: automatizar a parte rotineira do trabalho deixa para o humano so os casos raros e dificeis -- para os quais ele esta MENOS preparado, porque parou de praticar a habilidade rotineira. Ironia: em vez de precisar de menos treinamento, o operador residual precisa de MAIS treinamento para lidar com as excecoes raras e de alto risco.
Confirma/desafia: se o Claude Code escreve os resumos E os flashcards E as vezes avalia o drill, o "aluno" (e o proprio agente, num papel duplo) cai no padrao classico de Bainbridge/Parasuraman: o trabalho rotineiro de "gerar sintese/card correto" e automatizado, entao quando a saida do agente esta sutilmente errada (um card ruim, uma aula simplificada demais), quem deveria pegar o erro (o aluno, que ja nao pratica gerar sua propria sintese) e o menos equipado para isso -- e ha uma tendencia (automation bias) a aceitar o enquadramento de "certo/errado" do proprio agente sem busca vigilante de contradicao, especialmente sob fadiga de sessoes longas. Isso da base teorica solida para regras ja existentes na memoria do MedHub (F39: "card defeituoso contamina o diagnostico"; a insistencia em auditar o instrumento antes de nomear um padrao do usuario) -- sao instancias praticas exatas da ironia de automacao: a automacao degrada a fidelidade do proprio sinal (historico FSRS) que humano e agente precisam para o momento raro e decisivo (a prova real).

---

## g. Design de friccao / "desirable difficulty" em produto de aprendizagem

**Bjork (1994, termo original) e Bjork, Dunlosky & Kornell (2013), "Self-Regulated Learning: Beliefs, Techniques, and Illusions", Annual Review of Psychology 64**
Fonte: https://www.annualreviews.org/doi/pdf/10.1146/annurev-psych-113011-143823 (copia: https://gwern.net/doc/psychology/spaced-repetition/2013-bjork.pdf)
Forca: paper de revisao peer-reviewed (Annual Review of Psychology -- journal de revisao de alto prestigio)
O que propoe: desempenho DURANTE a pratica e aprendizagem real sao dissociaveis, ate inversamente relacionados -- condicoes que parecem fluentes e produtivas no momento (releitura, pratica massificada) geram alta performance de curto prazo e baixa retencao; condicoes dificeis (espacamento, intercalacao, teste/recuperacao ativa, geracao da resposta) reduzem fluencia visivel mas aumentam retencao/transferencia de longo prazo. Mecanismo: quanto menor a "forca de recuperacao" de um item no momento em que ele e recuperado com sucesso, maior o ganho de forca de armazenamento -- recuperar algo "na beira do esquecimento" consolida mais do que recuperar algo recem-visto.

**Nelson & Dunlosky (delayed-JOL effect) e Kornell & Bjork, "Metacognitive Judgments and Control of Study" -- literatura de Judgments of Learning (JOL)**
Fonte: sintetizada dentro do mesmo Annual Review 2013 acima, mais achados classicos de Nelson & Dunlosky sobre julgamentos de aprendizagem
Forca: paper/revisao peer-reviewed
O que propoe sobre confiabilidade de auto-avaliacao: julgamentos metacognitivos (que incluem "sei essa carta" ao se auto-avaliar num flashcard) se correlacionam positivamente com acerto real, mas sao sistematicamente enviesados por "modelos mentais falhos" -- ilusoes de competencia vindas de fluencia (releitura parece dominio, mas nao e). A acuracia melhora MUITO quando o julgamento e baseado em recuperacao ativa (testar-se) em vez de fluencia, e especialmente quando o julgamento e ATRASADO (delayed-JOL) em vez de imediato: gamma de correlacao acima de 0.9 no atrasado vs. abaixo de 0.6 no imediato.

**Anki / SuperMemo -- documentacao/design proprios**
Fontes: manual oficial do Anki (https://docs.ankiweb.net/background.html) e wiki oficial do SuperMemo comparando algoritmos (https://supermemopedia.com/wiki/SuperMemo_or_Anki)
Forca: documentacao oficial de produto (nao paper) -- SM-17/SM-18 relatados como superiores ao SM-2 do Anki em metricas de ajuste de curva; FSRS (usado por Anki hoje) relatado, em analises de comunidade sobre milhoes de revisoes, como mais preciso que SM-2 na previsao de intervalo.
NAO VERIFICADO nesta sessao: associacao especifica com o design do Duolingo (nao fetchei fonte primaria do Duolingo Research/half-life regression nesta sessao -- mencionar Duolingo aqui seria conhecimento previo nao confirmado, portanto omitido como fonte verificada).

**Confirma/desafia (sintese do item g):** confirma fortemente o desenho MedHub: a literatura de JOL diz que o julgamento IMEDIATO e AUTO-RELATADO e o MENOS confiavel, e que o julgamento baseado em desempenho de recuperacao real (nao na sensacao de confianca do aluno) e muito mais preciso. O padrao do /revisar -- o agente infere a nota a partir do que o aluno de fato disse/fez durante o drill, em vez de pedir um auto-relato de confianca cru -- esta alinhado com exatamente essa recomendacao da literatura de metacognicao, nao e so conveniencia de produto. Ponto de atencao (nao contradicao, mas risco de implementacao): a literatura tambem diz que o ganho de aprendizagem vem do ESFORCO DE RECUPERACAO em si, nao so da nota -- entao o desenho precisa garantir que o aluno tente recuperar ANTES de ver resposta/nota, e nao so leia e concorde com a avaliacao do agente.

---

## h. Higiene de execucao de agentes em repositorio

**Claude Code -- hooks (documentacao oficial)**
Fonte: https://code.claude.com/docs/en/hooks
Forca: documentacao oficial de produto (Anthropic)
O que propoe: hooks PreToolUse podem retornar "permissionDecision: deny" e bloquear uma chamada de ferramenta independentemente da intencao do modelo, do prompt do usuario, ou de como a conversa foi conduzida ate ali -- ou seja, aplicacao TECNICA determinista, nao "sugestao educada" em texto de instrucao. Importante: a flag --dangerously-skip-permissions pula so prompts interativos, NAO pula hooks -- da para remover a espera em comandos seguros e manter uma rede de seguranca real em comandos destrutivos.
Confirma/desafia: confirma diretamente que gates de pre-commit/pre-acao para agentes de codigo sao um padrao OFICIAL e recomendado pelo proprio fabricante do agente usado no MedHub -- nao e uma invencao local, e a aplicacao do padrao oficial de "enforcement tecnico > instrucao em prosa" (mesma logica dos gates de pre-commit do MedHub).

**Google SRE -- "Eliminating Toil" (SRE Workbook)**
Fonte: https://sre.google/workbook/eliminating-toil/ (parte do SRE Book/Workbook oficial do Google)
Forca: relatorio tecnico oficial (Google) para o conceito geral de toil/automacao; NAO VERIFICADO diretamente nesta sessao: a lista especifica de praticas ("confirmacao explicita antes de acao destrutiva, rate limiting, circuit breaker, audit log, rollback para toda mudanca automatizada") veio de um resultado de busca sintetizado (provavelmente de um blog secundario tipo incident.io), NAO de um fetch direto do texto primario do sre.google nesta sessao -- tratar essa lista especifica como pratica de mercado plausivel e consistente com o espirito do livro, mas nao uma citacao textual confirmada.
O que o livro define com confianca (isso sim primario): toil = trabalho manual, repetitivo, automatizavel, tatico, sem valor duradouro, que escala linearmente com o crescimento do servico; SRE recomenda manter toil abaixo de ~50% do tempo de um engenheiro.

**O termo composto "dry-run + count-assert" como padrao NOMEADO**
Resultado da busca: NAO ENCONTRADO como termo formal em nenhuma fonte primaria/oficial nesta pesquisa. E uma sintese local plausivel de duas praticas cada uma bem documentada separadamente -- "dry-run" antes de operacao destrutiva (comum em ferramentas de infraestrutura, ex. terraform plan, e no espirito geral do SRE Book) e "testes/verificacao como contrato que trava o turno" (mencionado em multiplos guias de pratica de mercado sobre Claude Code -- ex. "verification checks that return pass/fail... keep the agent honest", frase vinda de um resumo de busca de um blog de pratica, NAO uma citacao direta da Anthropic -- marcar como pratica de mercado/opiniao, nao blog oficial). Nenhuma fonte oficial (Anthropic, GitHub, Google) nomeia literalmente "dry-run + count-assert" como um padrao unico com esse nome.
Forca do item como um todo: PARCIALMENTE NAO VERIFICADO -- os componentes individuais (hooks bloqueantes = oficial/forte; dry-run e rollback em ops = oficial/forte no espirito do SRE Book, mas checklist especifico nao confirmado por fetch primario; testes-como-contrato trava-turno = pratica de mercado, nao blog oficial) sao reais e bem documentados separadamente, mas a fusao exata no nome "count-assert" parece ser nomenclatura propria do MedHub, nao um termo de industria.
Confirma/desafia: confirma que a DISCIPLINA por tras do padrao (gate determinista antes de mutacao, dry-run antes de destrutivo, verificacao pass/fail que trava o agente) e reconhecida e recomendada tanto pelo fabricante do agente quanto pela pratica classica de SRE -- o MedHub nao esta inventando uma pratica extravagante. Desafia/completa ao mostrar que o "COUNT-ASSERT" especifico (comparar contagem esperada vs. real antes/depois de uma mutacao em massa no banco) preenche uma lacuna que as ferramentas de contract-testing de mercado (item d: Pact, Schemathesis) nao cobrem, porque essas assumem schema maquina-legivel -- aqui o "contrato" e uma contagem de linhas SQLite, nao um schema JSON/OpenAPI. E um padrao correto e razoavel, mas sem literatura/guia oficial que o nomeie assim -- deve ficar marcado como pratica caseira validada por analogia, nao como "confirmado pela industria" ponto a ponto.

---

## Nota final de metodo

Dos 8 itens, os pontos que ficam expressamente como NAO VERIFICADO (sem fonte primaria direta nesta sessao) sao: (1) o texto exato de Lillie et al. 2011 (lido apenas via revisao secundaria); (2) a URL/conteudo primario do EdWorkingPaper 2024 de Kraft/Schueler/Falken; (3) atribuicao da frase "engagement != learning gain" a um paper especifico de Koedinger (a disciplina "learning engineering" em si esta bem confirmada, a atribuicao pontual nao); (4) a lista especifica de praticas de automacao segura do SRE Workbook (o conceito de toil esta confirmado, o checklist de circuit-breaker/rate-limit nao foi lido no texto primario); (5) o termo composto "dry-run + count-assert" como nome de industria (nao existe -- e sintese local); (6) associacao do design do Duolingo com "desirable difficulty" (nao verificada nesta sessao, omitida do item g). Todos os demais achados citados neste relatorio foram confirmados em fonte primaria (paper, blog oficial do laboratorio, ou documentacao oficial de produto) acessada por fetch direto ou por resultado de busca com titulo/autor/venue claramente identificavel.
