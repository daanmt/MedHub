# MedHub — Infraestrutura de Aprendizagem com Loop Fechado

## Resumo

MedHub é uma infraestrutura de aprendizagem com estado persistente para preparação à residência médica. Cada erro de questão é tratado como evento diagnóstico estruturado: registrado em banco relacional com metadados clínicos, incorporado à base de conhecimento de forma cumulativa e encaminhado ao motor de revisão espaçada. O resultado é um loop fechado entre falha, diagnóstico, conhecimento e retenção — contínuo e auditável entre sessões.

Estado atual: 61 sessões documentadas, 2.931 questões processadas, 200+ erros estruturados, 277 flashcards baseador em key-points dos erros detectados, 37 resumos clínicos em 5 áreas.

---

## Problema

A preparação para residência médica no Brasil exige processar entre 15.000 e 25.000 questões por ciclo de estudo. O gargalo não é acesso a questões — é a qualidade do processamento. A prática convencional — rever o gabarito, eventualmente anotar algo — é artesanal e não escala cognitivamente. O erro retorna porque nunca foi diagnosticado com estrutura. O padrão não é identificado. O conhecimento não é retido. O estudante acumula horas sem acumular aprendizagem efetiva.

---

## Por que importa

Uma questão errada contém ao menos três informações utilizáveis: o elo cognitivo que falhou, a armadilha semântica que induziu o erro e o conceito clínico que precisa ser ancorado. Ignorar qualquer uma delas é deixar a informação mais valiosa do processo de estudo sem uso.

Multiplicado por milhares de questões ao longo de meses, a diferença entre processar erros com estrutura ou sem ela é a diferença entre um processo de aprendizagem que converge e um que recicla as mesmas lacunas.

---

## Tese

O valor de um sistema de estudo está menos em fornecer conteúdo e mais em capturar, estruturar e reter o que o estudante ainda não sabe. O erro é o dado primário. Um sistema que o trata como evento diagnóstico — e não como feedback descartável — transforma o estudo de prática episódica em processo cumulativo.

---

## Solução

MedHub converte cada erro processado em três operações simultâneas e acopladas:

**1. Registro diagnóstico estruturado.** O erro é inserido em banco relacional com metadados clínicos: área, tema, elo cognitivo quebrado, armadilha identificada, complexidade e tipo de habilidade ausente. Isso cria um inventário auditável de lacunas, não um log de respostas erradas.

**2. Atualização da base de conhecimento.** O resumo clínico correspondente recebe o padrão identificado na seção de armadilhas. Essa seção é arquiteturalmente irreversível: só acumula, nunca perde registros. A cada sessão, os resumos ficam mais densos em termos de padrões de falha reais de prova.

**3. Geração de flashcard para revisão espaçada.** O elo cognitivo quebrado é convertido em flashcard e entra no motor FSRS v4, que agenda revisões pelo algoritmo de esquecimento — não por conveniência ou intuição do estudante.

Os três eixos são inseparáveis por design. Diagnóstico sem retenção é log. Retenção sem diagnóstico é decoreba. O sistema exige os dois, sempre juntos.

---

## Operação em alto nível

Cada sessão herda o estado exato da anterior via protocolo de inicialização em Markdown — agnóstico a modelo de linguagem. O agente lê o documento de estado canônico do projeto, verifica o histórico de sessões e opera dentro de fluxos estruturados por tipo de tarefa: análise de erros, criação de resumo, revisão FSRS, auditoria de qualidade.

O banco relacional centraliza tudo: erros, flashcards, estado algorítmico de revisão, cronograma de temas. Um segundo banco gerencia memória persistente entre sessões — padrões de fraqueza e sínteses clínicas — independente do banco operacional. O dashboard expõe métricas de desempenho, player de revisão e biblioteca clínica. A interface primária de revisão é uma CLI com política de três filas: atrasados, devidos hoje, novos.

---

## Diferenciais

**Continuidade de estado como fundação arquitetural.** O protocolo de bootstrap elimina o custo de reinstalação de contexto que afeta sistemas dependentes de memória de conversa. Qualquer agente compatível herda o estado completo do projeto sem reconfiguração. Isso permite operar indefinidamente sem degradação.

**Base de conhecimento adversarialmente refinada.** Os 37 resumos clínicos não são notas expositivas. São documentos construídos a partir de erros reais de prova, densificados a cada sessão via regra de acúmulo inviolável. A qualidade de um resumo é diretamente proporcional ao volume de erros processados na área.

**Qualidade de flashcards auditada em dois eixos independentes.** O pipeline distingue sinais objetivos de artefato (gabarito embutido no conteúdo, prefixos indesejados) e qualidade semântica. Uma revisão qualitativa via API de linguagem reescreveu 189 dos 277 cards ativos. Estado atual: sem defeitos críticos detectados nos 277 cards.

**Portabilidade arquitetural.** O protocolo de sessão é Markdown puro — não depende de modelo ou plataforma específica. Qualquer agente compatível opera dentro do mesmo ambiente sem adaptação.

---

## Estado atual

O sistema está em uso diário operacional. Indicadores em 2026-04-03:

| Indicador | Valor |
|---|---|
| Questões processadas | 2.631 (meta: 17.000 até outubro / 23.000 até dezembro) |
| Erros estruturados no banco | 200+ |
| Flashcards ativos (sem defeitos críticos) | 277 |
| Resumos clínicos | 37 (5 áreas) |
| Sessões documentadas | 61 |
| Desempenho médio | 79,74% |

A fundação está consolidada. As três camadas centrais — registro, conhecimento e retenção — estão operacionais e integradas.

---

## Riscos e limitações

**Persistência local.** O banco de dados opera localmente por design — não é replicado para nuvem. Backups dependem de rotina manual. Não há redundância automática.

**Fricção de inserção.** A interface primária de registro de erros é uma CLI. Em volume elevado de questões diárias, esse ponto de entrada pode se tornar um gargalo operacional.

**Geração de flashcards sem contexto clínico.** O pipeline atual não injeta o conteúdo dos resumos clínicos na geração de flashcards. Isso limita a profundidade semântica dos cards e representa a principal lacuna técnica pendente.

**Escopo de usuário único.** O sistema não foi projetado para múltiplos usuários e não está no horizonte de evolução atual.

---

## Próximos passos

**Injeção de contexto clínico na geração de flashcards.** Conectar a base de resumos ao pipeline de geração eleva a revisão de "lembrar a resposta" para "compreender o raciocínio clínico". É a evolução de maior impacto imediato na qualidade de retenção.

**Simulados orientados por fraqueza.** O banco já contém os dados necessários. A próxima camada é a interface que seleciona questões e temas pela lacuna real identificada no banco — não por área ou data.

**Planejador de sessão agêntico.** O agente lê o banco, identifica prioridades e propõe o plano de sessão, eliminando a etapa de decisão manual sobre o que estudar e em que ordem.

**Dashboard metacognitivo.** A camada de análise que vai além de "você errou X vezes" e chega em "você sistematicamente aplica o diagnóstico mais prevalente em vez do critério do fluxograma" — informação acionável para mudar comportamento de estudo, não apenas monitorar performance.
