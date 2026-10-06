---
type: discovery
status: active
---

# Discovery -- do MedHub de um aluno a um ambiente agêntico de estudos

> Escrito em 02/10/2026 (s211), a pedido do operador, a partir da conversa do dia: painel, fila, performance, a referência do Prisma Medicina, o PRD `feedback-cadeia-declarada` e a decisão de sair do artifact.
> **Explicativo, não normativo.** Só é decisão o que está marcado **[decidido]**; o resto é análise e recomendação. Todo número tem a origem ao lado; o que não foi medido está dito como não medido.

## 1. Em uma página

- **A ideia:** um ambiente em que um agente conduz o estudo de ponta a ponta -- planeja, ensina, cobra, diagnostica o erro e devolve a revisão -- e o aluno entra com o que só ele tem: a tentativa honesta e a declaração do que sabia. A unidade de valor não é a questão, é o **elo quebrado** do raciocínio.
- **Onde estamos:** o MedHub já faz isso para UM aluno, com o Claude Code como motor, um SQLite local como banco e uma página (artifact) como tela. Funciona e está instrumentado; não é um produto.
- **O que impede escalar:** quatro coisas, nesta ordem de gravidade -- (1) conteúdo de terceiros entranhado no acervo, (2) o dado preso a um PC e espalhado em cinco lugares, (3) a tela sendo um artifact (sem login, sem backend, com teto de documentos), (4) o agente rodando numa sessão interativa de uma pessoa.
- **Recomendação:** não migrar nada antes de 01/11. Depois, três passos com portão entre eles: ambiente próprio para um usuário (paridade com o hub), conhecimento num banco único com proveniência, e só então outros usuários.
- **Risco número 1 hoje não é técnico:** nos últimos 15 dias foram 62 questões em 2 dias de estudo, contra ~84 por dia que a meta pede (`painel.py --json`, 02/10). Cada hora de engenharia até a prova sai do mesmo orçamento.

## 2. O que saiu da conversa de 02/10

| Tema | Resultado |
|---|---|
| Feedback da cadeia de raciocínio | **[decidido]** o aluno declara o estado de cada elo (Sim / Incerteza / Desatenção / Não); a página não infere a quebra pela letra. PRD + 6 specs (`.vibeflow/specs/feedback-cadeia-declarada-part-1..6`). |
| Momento do feedback | **[decidido]** modo Estudo ou Prova escolhido por lista; simulado sempre Prova. |
| Marca-texto | Grifo no enunciado e nas alternativas, gravado com a resposta (part-4). |
| Autoria | **[decidido]** a cadeia é autoral (resumos + apostilas); o comentário do EMED só para conferir em caso de dúvida. |
| Ambiente próprio | **[decidido]** sair do artifact depois do v0: frontend + backend + banco, primeiro para a gestão do conhecimento, depois multi-sessão, autenticação e usuários distintos. |
| Este documento | Onde estamos e o que falta para escalar. |

## 3. Onde estamos -- a fotografia medida

### 3.1 O produto, para um aluno

| O quê | Quanto | Origem |
|---|---|---|
| Questões feitas / acerto | 7.488 / 78,8% | `performance.py`, 02/10 |
| Erros analisados e registrados | 1.094 | `day_plan.py --handoff-block`, 02/10 |
| Cards ativos / nunca introduzidos | 1.706 / 649 | idem |
| Revisões de card gravadas | 3.886 | `learning_efficacy.py`, 02/10 |
| Retenção dos cards (7 / 14 / 30 dias) | 72,4% / 77,5% / 75,0% | `db.get_retencao_revlog`, 02/10 |
| Resumos clínicos | 136 | glob |
| Temas na taxonomia | 309 | db |
| Listas e simulados no hub | 18 listas + 5 provas UERJ | coleção `listas`, 02/10 |
| Questões com cadeia de raciocínio | 91 de 992 capturadas (4 listas de 23) | `emed_banco.py --status`, 02/10 |

O laço que já fecha: **questão -> erro -> cadeia de elos -> card -> revisão espaçada -> aula de revisão**, com plano semanal e painel derivados do banco.

### 3.2 A arquitetura de hoje

| Camada | O que é | Tamanho |
|---|---|---|
| Agente | Claude Code + 15 skills + 9 contratos + `AGENTE.md` | 211 sessões desde 01/03/2026, 752 commits |
| Domínio | `app/utils/db.py` (único dono do SQL) + FSRS (`py-fsrs`) + RAG local | `db.py` com 3.153 linhas |
| Ferramentas | CLIs e módulos em `tools/` (fila, plano, painel, banco de questões, sensores) | 59 arquivos + 109 de teste |
| Dado | `ipub.db` (SQLite local, fora do git) | 7,2 MB |
| Tela | 1 artifact (hub) com 4 abas, montado por `tools/hub.py`; estado no `db` da página | página única de ~240 KB |
| Harness | suíte de testes, gates de pre-commit, ledger de auditoria | 1.291 testes (02/10) |

### 3.3 O que é ativo de verdade (levar para o ambiente novo)

- **O modelo pedagógico nomeado:** 17 princípios com fonte e o ledger de fricções virtuosas x viciosas (`docs/FUNDAMENTOS-APRENDIZAGEM.md`). É o que impede "melhoria de produto" de virar regressão de aprendizagem.
- **A camada de domínio com dono único do SQL** e escrita só por writers com validação (`card_checks`, allowlist testada). Vira camada de serviço quase sem reescrita.
- **O que é determinístico já está fora do LLM:** FSRS, fila, teto do dia, plano, painel, ingestão de prova em PDF. O agente não é chamado onde uma função resolve.
- **Disciplina de verificação:** número só com o comando que o mediu; cláusula revogada tem rito; achado de leitura humana vira gate.
- **O dado de calibração do próprio aluno:** racional declarado, certeza antes do gabarito, alternativas riscadas e, com o v0, o estado de cada elo e os grifos.

### 3.4 Onde dói -- os limites estruturais

| Limite | Evidência |
|---|---|
| **A tela é um artifact.** Sem login (conta compartilhada: todo visitante é dono), teto de 25.000 documentos (s214; ⚰️ *dizia 5.000 até a s216*), uma página única republicada inteira. | Perda de 64 de 90 notas em 24/09 quando o `db` da página não subiu; poda manual de coleções a cada fechamento. |
| **O backend é uma sessão aberta num PC.** Sem PC acordado não há gravação de nota, fila nova nem painel atualizado. | `/hub-backend` roda em `/loop`; latência = intervalo do loop. |
| **A página não pode acionar o agente.** | O botão "pedir mais cards" foi barrado em 23/09 (agente sem supervisão acionado por página). |
| **O conhecimento vive em cinco lugares:** `ipub.db`, o `db` do hub, `resumos/*.md`, a memória do harness e `history/`. | A análise de um erro mora no `db` do hub; a cópia no SQLite envelhece (erro 1092). |
| **O dado está preso a uma máquina.** | `ipub.db` local, backup com rotação de 5. |
| **Custo de conteúdo sem medida por unidade.** | Sabe-se o total por sessão (ex.: 9 aulas de revisão = ~565 mil tokens em 01/10; varredura de 325 cards = ~2,5 milhões em 29/09), não o custo por aula, por cadeia ou por card. |
| **Acervo com conteúdo de terceiros.** | Listas do EMED, apostilas em PDF, material de terceiros sobre a UERJ; o repositório é público e o conteúdo fica fora dele por regra, não por arquitetura. |
| **Um só usuário em todas as tabelas.** | Nenhuma tabela tem dono; plano, FSRS e notas são globais. |

## 4. A ideia -- o que é um ambiente agêntico de estudos

**Definição de trabalho:** um sistema em que (a) o agente tem as ferramentas e a memória para conduzir o ciclo Aprender -> Reter -> Aplicar de cada aluno, (b) o que é regra fica em código e o que é julgamento fica com o agente, e (c) o aluno fornece o dado que nenhum modelo tem -- o que ele sabia, onde hesitou, o que grifou.

**Comparação honesta com a referência (Prisma), pelo que o vídeo mostra:**

| Eixo | Prisma | MedHub hoje |
|---|---|---|
| Habilidades por questão, declaradas pelo aluno | Tem, polido | Entrando no v0 |
| Banco de questões próprio e amplo | Tem | Não: 18 listas de terceiros + 5 provas públicas |
| Reagendar questão pela habilidade quebrada | Tem ("em 3-4 dias cai de novo") | Não (fila pós-v0) |
| Conceitos/flashcards por questão com aceitar e rejeitar | Tem | Cards nascem do erro, triados por mim |
| Interface | Produto acabado | Página única, funcional |
| Aula escrita para o buraco que o erro expôs | Comentário fixo por questão | Tem: aula-base e revisão direcionada geradas do erro do aluno |
| Plano adaptado à prova-alvo e ao ritmo real | Não aparece no vídeo | Tem: trilha gerada, meta única, painel |
| Diagnóstico de padrão de erro entre temas | Não aparece no vídeo | Tem: ledger de habilidades reincidentes |
| Fricção pedagógica protegida por regra | Não aparece no vídeo | Tem: ledger de fricções, contratos |

A aposta não é ter mais conteúdo que uma plataforma. É **fechar o laço por aluno**: o erro de hoje muda a aula, o card e a fila de amanhã, sem ninguém configurar nada.

## 5. O que precisamos para escalar -- por camada

### 5.1 Dado: um banco, um modelo de conhecimento

- **Separar o que é de todos do que é de cada um.** Compartilhado: questão, cadeia (elos, habilidade), objetivo, tema, resumo, card-modelo, aula-modelo. Por aluno: tentativa (letra, certeza, riscadas, grifos, estado de cada elo), estado FSRS, plano, notas, aulas geradas para ele.
- **Entidades de primeira classe que hoje são JSON em coluna ou prosa:** elo, habilidade, declaração por elo, grifo. O v0 guarda como JSON de propósito (part-5); o ambiente próprio é onde viram tabela.
- **Proveniência em todo item de conteúdo:** origem (prova pública / autoral / terceiros), fonte verificada, versão, quem gerou. Sem isso não há como abrir o acervo a outro usuário.
- **Migração:** `ipub.db` + coleções do hub + análises -> banco único (Postgres é o candidato natural para multiusuário; a decisão é da fase 1). A camada `app/utils/db.py` é o ponto de troca.

### 5.2 Backend: API fina + trabalhos agendados

- Os CLIs determinísticos viram endpoints e jobs (fila do dia, registro de notas, painel, plano). O rito dry-run -> apply -> COUNT-ASSERT vira transação com validação.
- O "tique" deixa de depender de PC ligado: nota grava na hora, fila do dia seguinte sai por agendamento.
- O que a página fazia com espelho local + reenvio (lição de 24/09) vira requisito: **a nota do aluno nunca se perde** (offline primeiro, confirmação explícita de gravação).

### 5.3 Agente: três cargas, três jeitos de rodar

| Carga | Exemplo | Como rodar (plataforma Claude) |
|---|---|---|
| **Sem LLM** | FSRS, fila, plano, painel, ingestão de PDF | Código. Fica como está. |
| **Geração em lote, sem pressa** | Cadeias v3 de uma prova, cards, aulas de revisão | Messages API com saída estruturada validada pelos validadores que já existem; Batches (metade do preço) + cache de prompt para o contexto fixo (brief, resumos). |
| **Agente com ferramentas, por aluno** | Analisar os erros do dia, apontar conflito, montar a revisão, responder dúvida | Loop de ferramentas hospedado por nós (Tool Runner da API) **ou** Managed Agents (beta: a Anthropic hospeda o loop e o sandbox, com sessões, agendamento e memória). O Agent SDK é o mais parecido com o que temos hoje (o motor do Claude Code como biblioteca), mas quem hospeda somos nós. |

Ordem de grandeza de preço por milhão de tokens (entrada / saída), tabela da skill `claude-api` em cache de 25/09/2026: Opus 5.5 US$ 4 / 20 · Sonnet 5.5 US$ 2 / 10 · Haiku 4.5 US$ 1 / 5 · Fable 5.1 US$ 10 / 50. Leitura de cache custa cerca de um décimo da entrada.

**Não medido e necessário antes de qualquer conta de custo por aluno:** tokens por cadeia, por card e por aula, separados em entrada e saída. A recunhagem de t40/t49 (54 questões) é a primeira oportunidade de medir.

Regras que o ambiente novo herda: ferramenta do agente com escopo mínimo; escrita destrutiva com confirmação; conteúdo vindo da web ou de página tratado como dado, nunca como instrução; o agente confirma o que o aluno declarou, não o sobrescreve.

### 5.4 Frontend: aplicativo web, celular primeiro

- As mesmas quatro superfícies (Painel, Aulas, Cards, Listas), agora como aplicativo com rota, estado e componentes -- não uma página de 240 KB republicada.
- Os tokens visuais atuais (aprovados por ele em setembro) viram o sistema de design. O v0 do feedback é o ensaio da linguagem nova: menos blocos, uma ação por tela.
- Requisitos que a página já provou: toque de 44 px, nada fixo na rolagem, texto curto, funcionamento com rede ruim.

### 5.5 Identidade e multiusuário

- Login, isolamento por aluno em toda leitura e escrita, papéis (aluno, curador de conteúdo, administrador).
- Dado de desempenho é dado pessoal: base legal, exportação e exclusão desde o primeiro usuário de fora.
- Prova-alvo, calendário e ritmo viram configuração do aluno (hoje são constantes do repositório: `core/provas.json`, `performance.MARCOS`).

### 5.6 Conteúdo e propriedade intelectual -- o bloqueio real

| Pode ir para outro usuário | Não pode |
|---|---|
| Questões de provas públicas (cadernos oficiais de banca), com gabarito oficial | Listas, comentários, fórum e apostilas do EMED |
| Cadeias, soluções, cards e aulas escritos por nós, com fonte primária | Material de terceiros sobre a banca |
| Resumos autorais **depois de auditada a proveniência** (muitos nasceram de PDF de curso) | Qualquer paráfrase de comentário de professor |

Consequências: (1) o banco de questões do produto é o de provas públicas, pelo caminho que já existe (`tools/prova_pdf.py`); (2) a integração com o curso pago de cada um, se existir, é pessoal e fica fora do acervo comum; (3) a auditoria de proveniência dos 136 resumos é pré-requisito da fase multiusuário; (4) repositório público e produto pedem uma fronteira explícita entre código aberto e acervo.

### 5.7 Qualidade: como saber se o agente ensina certo

- **Conteúdo gerado:** taxa de "cadeia com defeito" sinalizada pelo aluno (régua do PRD: até 10%), gates de card (`card_checks`), governança de evidência para afirmação clínica decisória, amostra lida por humano a cada lote.
- **Aprendizagem:** retenção por coorte de card, acerto firme por objetivo, reincidência de habilidade entre temas, acerto em simulado inteiro.
- **Produto:** nota perdida = zero; tempo entre erro e revisão; custo por aluno por mês.
- Um conjunto dourado de questões com cadeia revisada por humano é o eval de regressão de qualquer troca de modelo ou de brief.

## 6. Caminho em fases, com portões

| Fase | Quando | O que entra | Portão para a próxima |
|---|---|---|---|
| **0. Fechar o v0 e estudar** | até 01/11 | Feedback por elo declarado em uso real; medir tokens por cadeia/aula/card; anotar proveniência do que for cunhado. Nenhuma migração. | Prova feita; régua de 10% de defeito medida em t40/t49. |
| **1. Ambiente próprio, um usuário** | depois de 01/11 | Banco único + API fina sobre a camada de domínio + aplicativo web com as 4 superfícies + login de um usuário. O agente continua no Claude Code, agora falando com a API. | Paridade com o hub por 2 semanas, zero nota perdida, hub aposentado. |
| **2. Conhecimento como dado** | em seguida | Elo, habilidade, declaração e grifo como entidades; proveniência obrigatória; geração em lote com custo medido; banco de provas públicas com cadeia. | Custo por questão com cadeia conhecido; auditoria de proveniência dos resumos concluída. |
| **3. Grupo fechado** | só com 1 e 2 verdes | 5 a 10 colegas, isolamento por aluno, agente no servidor, prova-alvo configurável. | Retenção de uso e custo por aluno sustentáveis; nenhum vazamento entre contas. |
| **4. Produto** | decisão de negócio | Cobrança, suporte, crescimento do banco. | -- |

## 7. Decisões em aberto (são suas)

1. **Depois de 01/11, qual é o norte do projeto:** ferramenta pessoal para o ENAMED 2027 ou produto? A fase 1 serve aos dois; da fase 3 em diante, não.
2. **O acervo de terceiros:** manter como uso pessoal ao lado do produto, ou reconstruir tudo sobre prova pública?
3. **Repositório:** continua público? Código aberto com acervo fechado é um desenho possível, mas precisa ser escolhido.
4. **Onde o agente roda na fase 3:** hospedado por nós ou gerenciado. Depende de custo medido e do quanto de controle se quer.
5. **Quem constrói:** o mesmo par de agentes de hoje (estudo + engenharia) ou uma frente separada, para a engenharia parar de disputar a sessão de estudo.

## 8. Riscos

- **Engenharia como fuga do estudo.** O dado de ritmo já mostra isso; a fase 0 existe para conter.
- **Reescrever o que funciona.** A camada de domínio e o harness são o patrimônio; a migração troca a tela e o banco, não a lógica.
- **Custo por aluno invisível.** Sem medida por unidade de conteúdo, qualquer preço é chute.
- **Propriedade intelectual.** Um único item de terceiros no acervo comum compromete o produto inteiro.
- **Qualidade clínica em escala.** Hoje um médico lê tudo; com mais usuários, o erro clínico de uma cadeia se multiplica. O sinal de defeito e a amostra humana por lote não são opcionais.
- **Dependência de recurso em beta.** Agente gerenciado e alguns recursos da API estão em beta; a arquitetura não pode travar neles.

## 9. Estado do v0 ao fim de 02/10 (medido)

- **Entregue e no ar (hub Version 63):** as 6 specs do PRD, cada uma com relatório de auditoria PASS (`.vibeflow/audits/feedback-cadeia-declarada-part-1..6-audit.md`); suíte de 1.291 para 1.346 testes; tela conferida em navegador real (Edge headless a 390 px sobre o hub com banco falso), com 3 defeitos visuais corrigidos antes de publicar.
- **Bloqueado:** a conferência do comentário do EMED pela API (`part-1b`). O classificador de permissões negou a edição duas vezes, inclusive depois da liberação por `/permissions`; ninguém contornou. Decisão do operador.
- **Conteúdo no contrato novo:** DMG (t40, 33 questões) e Hérnias (t49, 21) recunhadas, 54/54 no validador, 2 divergentes declaradas (t49 Q10 e Q20), semeadas no hub.
- **Custo medido da geração (uso do harness, `usage` dos subagentes):** cadeia v3 = 226 mil tokens / 33 questões (t40, ~6,9 mil por questão) e 206 mil / 21 (t49, ~9,8 mil por questão), modelo Opus 5.5, sem separação entrada/saída -- é a primeira medida por unidade de conteúdo do projeto. Implementação das 6 specs: ~850 mil tokens de subagente em ~28 min de relógio, mais a conferência do principal.
- **Fora do medido:** seleção por toque no celular (só o operador valida), e a régua de 10% de "cadeia com defeito" (precisa das listas de aceitação resolvidas).
