# Mapeamento de Skills e Workflows do MedHub

*Data da auditoria: 2026-03-21 | Gerado por: Antigravity via RAG/MCP*

Esta nota documenta a inteligência embutida no cofre do projeto **MedHub**, categorizando as capacidades explícitas do assistente e os fluxos de trabalho implícitos que regem o ecossistema de estudos para a residência médica.

---

## 1. Skills Explícitas (Framework GSD)
O ambiente possui um extenso ecossistema de comandos focados em desenvolvimento ágil e gerenciamento de projeto (GSD - *Get Shit Done*). Estas skills permitem que o assistente atue como um gerente de produto e engenheiro autônomo. 

**Exemplos Notáveis:**
- **Planejamento e Execução:** `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-autonomous` (para tocar fases do roadmap de ponta a ponta).
- **Gestão de Backlog e Roadmap:** `/gsd-add-backlog`, `/gsd-add-todo`, `/gsd-new-milestone`.
- **Auditoria e Qualidade:** `/gsd-audit-uat`, `/gsd-ui-review`, `/gsd-validate-phase`.
- **Contexto e Continuidade:** `/gsd-pause-work`, `/gsd-resume-work`, `/gsd-session-report`.

---

## 2. Workflows Indiretos (O Ambiente de Estudos)

Para além das ferramentas de engenharia, o projeto possui uma arquitetura altamente sofisticada de **estudo ativo e metodológico** contida nos arquivos de configuração do `=AGENTE` (como `ESTADO.md`, `HANDOFF.md` e a pasta `.agents/workflows/`).

Estes são os três pilares que regem a interação entre o usuário e a IA no MedHub:

### A. Análise Ativa de Questões e "Siamese Twins"
*(Registrado em `.agents/workflows/analisar-questoes.md`)*
O usuário não foca em ler passivamente. O fluxo é construído em torno da **resolução de questões e insights de estudo**:
- O usuário envia questões erradas ou anotações brutas.
- A IA aplica um diagnóstico estruturado (`Tools/comando de analise de questao.md`).
- A IA aplica a doutrina **"Siamese Twins"**: o erro é registrado simultaneamente no banco de dados (`ipub.db` via script Python autônomo) e atualizado no arquivo Markdown correspondente.
- A anotação no resumo é inserida cirurgicamente, marcada com ícones de alerta (⚠️ *Padrão de prova* ou 🔴 *Armadilhas*), respeitando um teto rígido de ~300 linhas de limite de hipercondensação.

### B. Criação de Resumos "Zero PDF"
*(Registrado em `.agents/workflows/criar-resumo.md`)*
O cofre é mantido limpo e focado com um pipeline automatizado de extração:
- A IA invoca um script Python local (`extract_pdfs.py`) para ler apostilas brutas na pasta temporária.
- Um resumo estrutural (bullet points, sem tabelas ASCII) é gerado, integrando os pontos cegos com a fisiopatologia clínica.
- Ao final, uma etapa de **limpeza automática** entra em ação, deletando permanentemente os PDFs de origem e os arquivos temporários gerados. O conhecimento bruto se converte puramente em Markdown limpo.

### C. Protocolo de Continuidade (Boot & Fechamento)
*(Registrado em `AGENTE.md` e `HANDOFF.md`)*
Para evitar a "amnésia" comum entre sessões de IA, o MedHub trata o contexto como sagrado:
- **Boot Sequence:** Toda nova sessão inicia com a leitura compulsória do `ESTADO.md` (a única Fonte da Verdade do projeto) e do `HANDOFF.md` (onde o agente anterior parou).
- **Fechamento:** Ao concluir uma etapa, o agente atualiza o Handoff, escreve o relatório em `history/session_NNN.md` e sincroniza o Git, garantindo passagem de bastão orgânica.

---
> [!NOTE]
> Esta nota demonstra a eficácia do MCP / RAG integrado. A IA é capaz não apenas de ler vetorialmente a sua base de dados, mas também de atuar escrevendo diretamente em seu cofre do Obsidian, consolidando o aprendizado com zero fricção.
