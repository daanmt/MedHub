---
type: architecture-reference
layer: tools
status: canonical
relates_to: ESTADO, AGENTE, roadmap
---

# Anatomia do MedHub (Infraestrutura Oficial)

*Gerado pós-auditoria em 21/03/2026.*

Esta é a documentação viva e estrutural do projeto **MedHub**, otimizada para ser indexada pelo vetor do RAG (Retrieve-Augmented Generation) e interpretada tanto por agentes lógicos (como o Antigravity) quanto pelo usuário.

---

## 🏗️ 1. Arquitetos do Sistema (Arquivos Root)

- `AGENTE.md` -> A Constituição. Define como a IA deve "dar o boot" e fechar o plantão (registrar a sessão).
- `ESTADO.md` -> O Mapa em Tempo Real. É a única Fonte de Verdade (`SSOT`) para contagem de questões, resumos e sessões.
- `HANDOFF.md` -> O Post-it. Uma nota rápida de onde o último agente parou para o próximo não ter que reler conversas longas.
- `roadmap.md` -> A Visão de Produto. Lista as grandes fases de desenvolvimento do ambiente (MVP -> Streamlit -> FSRS -> Simulador).

---

## 🗄️ 2. O Motor de Dados (Single Source of Truth)

- `ipub.db` -> O **Banco de Dados Oficial** de progresso. Armazena os erros (questões nativas), status do cronograma, flashcards base-texto (frente/verso) e o histórico de repetição espaçada (FSRS log). Assumiu o protagonismo abolindo antigos arquivos `.md` e `.xlsx` gigantescos.
- `caderno_erros.md` & `progresso.md` -> **ARQUIVADOS** (`history/legacy/`). Foram completamente substituídos pelo `ipub.db` para garantir performance.

---

## 🧠 3. O Cofre de Ensino (Diretórios Clínicos)

- `Temas/` -> O Ouro. Onde moram as dezenas de resumos clínicos de hiper-retenção, escritos exclusivamente baseados nos erros das questões ou hiper-condensados a partir de PDFs usando a regra "Zero PDF" (onde a referência é apagada após virar resumos em Markdown bullet point).
- `.agents/workflows/` -> Os "Scripts de Processo" da IA. Define passo a passo mecânico de como analisar questões (`analisar-questoes.md`), criar resumos (`criar-resumo.md`), auditar a infra ou registrar o dia (`registrar-sessao.md` - incluindo o **RAG Autopilot**).
- `Fichas/`, `Memorex/`, `Cronograma/` -> Mídia morta (PDFs intocáveis fornecidos por cursinhos paramedicinais). O agente só os acessa em modo leitura.

---

## 🛠️ 4. A Caixa de Ferramentas Ativa (`Tools/`)

Após a "Grande Faxina" de 2026, a pasta Tools foi higienizada. Só habitam nela os scripts críticos:

- `comando de analise de questao.md`: O **Prompt Metacognitivo**. Ensina a IA a quebrar erros de múltipla-escolha procurando a violação exata ("Elo Quebrado") ao invés de cuspir o gabarito cego. Gilda diretamente o SQL.
- `estilo-resumo.md`: O **Linter de Design**. Proíbe a escrita de tabelas brutas e força a formatação de ⚠️ *Armadilha de Prova* para todo fim de nota.
- `insert_questao.py`: A **Ponte CLI -> Banco**. Pega a análise de um erro tirado da IA e força a injeção disso no SQLite `ipub.db`, transformando de brinde a lição em um *Flashcard Draft*.
- `extract_pdfs.py`: O **Rasga-Arquivo**. Pega PDFs clínicos pesados, cospe Markdown puro para `%%TEMP%%` pro agente ler e destrói os rastros. (Política "Zero PDF").
- `audit_resumos.py`: O **Linter Ativo**. Varre todos os resumos na raiz e briga com quem esqueceu de usar o formato correto.
- `init_db.py` & `sync_flashcards.py`: Ferramentas nucleares do SQLite.

---

## 🖥 5. A Interface de Usuário (`app/`)

- `streamlit_app.py` & Pasta `app/` -> O Dashboard visual onde os botões rodam. Ele lê estritamente do `ipub.db` ou cruza os dados com o estado em Markdown sem precisar que a inteligência artificial altere linhas manualmente de código HTML para atualizar os números.
