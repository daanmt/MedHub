# ESTADO — MedHub (Preparação para Residência Médica)
*Atualizado: 2026-03-18 (sessão 032) | Ferramenta: Antigravity*

---

Ambiente de estudo para residência médica. Processa questões de prova, registra padrões de erro em `caderno_erros.md`, e mantém resumos clínicos organizados por área/tema em `Temas/`. Portável para qualquer LLM via v3.0 architecture (Zero-DB).

---

## INICIO OBRIGATÓRIO DE SESSÃO

**Leia `AGENTE.md` antes de qualquer ação.** Este arquivo contém o protocolo de boot e a ordem de leitura para garantir a continuidade do projeto.

> [!IMPORTANT]
> **SINGLE SOURCE OF TRUTH (SSOT):** O Markdown (`caderno_erros.md`) é a base absoluta. O App Streamlit (`01_dashboard.py`) reflete os dados via parser stateful. Ignorar o SQLite para leitura de UI; ele serve apenas para processamento futuro de ML.

- **98 erros diagnosticados** no caderno (`caderno_erros.md`)
- **31 resumos clínicos** consolidados em `Temas/`
- **32 sessões** de estudo catalogadas em `history/`

---

## Mapa de artefatos

### Infraestrutura
| Artefato | Arquivo |
|---|---|
| Estado do projeto | `ESTADO.md` (este arquivo) |
| Dashboard Streamlit | `streamlit_app.py` |
| Parser Stateful | `app/utils/parser.py` |
| Player Flashcards | `app/pages/02_flashcards.py` |
| Session logs | `history/session_NNN.md` |

### Conteúdo
| Artefato | Arquivo |
|---|---|
| Resumos clínicos | `Temas/{Área}/{Subespecialidade}/{Tema}.md` |
| Banco Principal (DB) | `ipub.db` (Erros + Cronograma) |
| [Legado] Caderno | `caderno_erros.md` (Apenas leitura) |
| [Legado] Progresso | `progresso.md` (Deprecado) |

### Material de referência (PDFs — não editáveis)
| Artefato | Pasta |
|---|---|
| Fichas de prova | `Fichas/` (5 PDFs por área) |
| Memorex por área | `Memorex/` (6 subpastas) |
| Textos extraídos | pasta temp do sistema (`%TEMP%`) — deletados ao final de cada sessão |

---

## Áreas com mais entradas no caderno

*(Disclaimer: Valores sujeitos a desatualização. Sempre consulte o Dashboard Streamlit para ver a estatística exata)*

| Área | Entradas (Última auditoria - Sessão 024) |
|---|---|
| Clínica Médica | 24 |
| Cirurgia | 24 |
| Pediatria | 15 |
| Ginecologia e Obstetrícia | 15 |
| Medicina Preventiva | 14 |

---

## Últimas sessões

**2026-03-18 | Antigravity (sessão 032):** **Refinamento Avançado de Colo e Governança**. Revisão profunda do resumo `[GIN] Rastreamento Colo.md` com diretrizes 2025 e análise de 9 erros. Incluídos detalhes de coleta na gestação e seguimento pós-exérese por margens. Refatoração completa de tabelas para bullet points e proibição de referências explicitas a questões em resumos.
**2026-03-16 | Antigravity (sessão 031):** **Expansão em Psiquiatria e Nefrologia**. Criação dos resumos de `Dependência Química.md`, `Intoxicações Exógenas.md` e `Lesão Renal Aguda.md`. Foco em alto rendimento (CAGE, Síndromes toxicológicas, Critérios KDIGO e diferenciação Pré-renal vs NTA).
**2026-03-15 | Antigravity (sessão 030):** **Consolidação de Pancreatites**. Criação do resumo de `Pancreatite Aguda e Crônica.md` a partir de material do Estratégia MED. Foco em critérios de Atlanta 2012, sinais semiológicos (Cullen/Grey-Turner) e tríade da pancreatite crônica.
**2026-03-15 | Antigravity (sessão 029):** **UI Refresh (Aesthetic Lovable)**. Implementado sistema de design Flat com `app/utils/styles.py`. Refatoração completa de todas as páginas para visual premium clinical. Arquitetura híbrida de botões FSRS implementada com sucesso.
**2026-03-14 | Antigravity (sessão 028):** Bootstrap de contexto e rebranding concluído. Correção de erro no `streamlit_app.py` (removida referência à página inexistente `05_progresso.py` integrada ao Dashboard). Sincronização de alterações do usuário em Pediatria.


**2026-03-14 | Antigravity (sessão 027):** Expansão do resumo `Medidas de Saúde Coletiva.md` e registro de **34 acertos (100%)** nas questões da Parte III. Tripla carga de doenças e contratransição detalhadas. Limpeza concluída e banco de dados atualizado.
**2026-03-14 | Antigravity (sessão 026):** **Salto para Fase 2 (Flashcards Inteligentes).** Refatoração da página do Caderno de Erros para "Flashcards e Caderno". Implementação do algoritmo FSRS (Free Spaced Repetition) para agendamento automático de revisões. Interface de 3 blocos (Hot Topics, Player Anki e Explorador de Lacunas) implantada. Sincronização de 1.555 acertos históricos do Excel EMED.

**2026-03-14 | Antigravity (sessão 025):** Implementação do Cronograma Dinâmico (Mini-DB)...
**2026-03-14 | Antigravity (sessão 024):** Auditoria de Governança e Refinamento de UI (P0 e P1). As métricas do Dashboard Streamlit foram corrigidas usando _Top-Down parser_ para garantir a acuidade matemática (exatos 92 erros rastreados). O `ESTADO.md` foi atualizado implementando a doutrina do **Single Source of Truth** (Streamlit > Texto Markdown Fixo). Ferramentas deprecadas limpas.
**2026-03-14 | Antigravity (sessão 023):** Mudança arquitetural (Pivô). O usuário definiu o documento `IPUB_Streamlit_Plano.md` estabelecendo uma interface em Streamlit puramente baseada em parse de Markdown ("Zero DB"). O Sqlite fica isolado como motor futuro de Machine Learning. O Roadmap e Backlog foram reescritos em 5 Fases visando a construção do multipage app na subpasta `app/`.
**2026-03-14 | Antigravity (sessão 022):** Desenvolvimento prático e execução do motor ETL (`etl_markdown_to_sqlite.py`). Migração massiva de blocos de erros textuais do `caderno_erros.md` direto para relacional do SQLite. O banco `ipub.db` agora possui volume crítico.
**2026-03-14 | Antigravity (sessão 021):** Estudo da Wiki oficial do Otimizador FSRS (MLE e BPTT). O roadmap foi bifurcado para definir a fronteira arquitetural entre o Scheduler (agendamento em tempo real) e o Optimizer (script periódico de Machine Learning consumindo o histórico em lote da tabela `fsrs_revlog`).
**2026-03-14 | Antigravity (sessão 020):** Implementação da regra "Siamese Twins". Script genérico CLI `insert_questao.py` criado para salvar questões no SQLite de forma autônoma. Atualizado workflow macro `analisar-questoes.md` para embutir a fase de inserção DB.
**2026-03-14 | Antigravity (sessão 019):** Análise da planilha EMED, detalhamento do modelo matemático de DSR no Roadmap e elaboração do schema do banco criando o script base `init_db.py`. O arquivo `ipub.db` foi instanciado com 5 tabelas (Cronograma taxonomia, Erros, Flashcards, FSRS Cards e FSRS Revlog).
**2026-03-14 | Antigravity (sessão 018):** Inserção do modelo de métricas (Estratégia), lógica de aprendizado FSRS e arquitetura inicial de BD/Streamlit no Roadmap.
**2026-03-14 | Antigravity (sessão 017):** Atuação como Senior PM para estruturação do `roadmap.md` do produto IPUB, dividindo a evolução em 4 Fases (MVP, Flashcards, Streamlit/BD e Simulados).
**2026-03-14 | Antigravity (sessão 016):** Análise de 4 questões de Sífilis na Gestação. Atualização do caderno de erros, progresso e adição de armadilhas de prova no resumo `[OBS] Sífilis na Gestação e Congênita.md`.
**2026-03-13 | Antigravity (sessão 015):** Escrita do resumo clínico de Sífilis na Gestação e Congênita. Condensação profunda dos critérios de Sífilis Congênita no neonato de mães do pré-natal (NTT - Notifique, Trie e Trate) e as atualizações do Ministério da Saúde sobre exclusão do fator parceiro no berçário. O arquivo finalizou em `[OBS] Sífilis na Gestação e Congênita.md`.
**2026-03-12 | Antigravity (sessão 014):** Análise de 11 erros de Trauma (ATLS, FAST, uretra, choque pediátrico) e adição de caixa de Alertas priorizando intervenções ("A atropela C").
**2026-03-11 | Antigravity (sessão 013):** Criação da seção de Trauma Abdominal em `Cirurgia/Trauma.md`. Inclusão de condutas para trauma contuso/penetrante, damage control, órgãos maciços/ocos, e armadilhas de prova.

**2026-03-10 | Antigravity (sessão 012):** Criação do resumo de `Pediatria/Emergências Pediátricas.md` (Arrritmias, PCR, TCE, Corpo Estranho e Afogamento). Foco em critérios PECARN e algoritmos PALS/Szpilman.

**2026-03-09 | Antigravity (sessão 011):** Criação do resumo de `[GIN] Rastreamento Colo.md` integrando diretrizes 2016 (Pap) e 2025 (DNA-HPV). Mapeamento de 34 "armadilhas de prova" baseadas em questões de residência.

**2026-03-09 | Antigravity (sessão 010):** Análise de 9 questões de Saúde Coletiva (indicadores de mortalidade). Atualização massiva do resumo de Preventiva e do caderno de erros (Total 59).

**2026-03-08 | Antigravity (sessão 009):** Análise de PTI (limiares e gravidade) e implementação da nova governança do projeto (`AGENTE.md`, `HANDOFF.md`, workflows refatorados).

**2026-03-06 | Antigravity (sessão 008):** Criação do resumo de `Hemostasia.md` a partir das apostilas `Hemost.pdf` e `Hemostasia_I__Co.pdf`. Consolidação de hemostasia normal, plaquetopatias, hemofilias, vW e trombofilias (SAF e hereditárias). Limpeza de arquivos temporários e PDFs da pasta do tema realizada.

**2026-03-06 | Antigravity (sessão 007):** Expansão massiva de Infectologia (`Tuberculose.md` e `HIV.md`) a partir de 6 apostilas/flashcards. Refinamentos baseados em erros de prova (transmissão vertical, neuro-semiologia, rastreio de TB). Deletados PDFs de infectologia após consolidação.

**2026-03-05 | Antigravity (sessão 006):** Eliminação da pasta `Extracted/`; `extract_pdfs.py` agora extrai para `%TEMP%` e possui `--delete-pdfs`/`--delete-temps` para limpeza automática pós-resumo. Workflow e `.gitignore` atualizados.

**2026-03-05 | Antigravity (sessão 005):** Consolidação de ferramentas — `estilo-resumo.md` movido para `Tools/`; `referencia/` removida; `extract_asma.py` deletado; `CLAUDE.md` e workflows atualizados. Proibição de tabelas e fluxogramas ASCII adicionada ao `Tools/estilo-resumo.md`.

**2026-03-05 | Antigravity (sessão 004):** Criação e refatoração de `Temas/Clínica Médica/Pneumologia/Asma.md` com GINA 2025 integrado. Reescrita do `Tools/extract_pdfs.py` com CLI genérica.

**2026-03-04 | Antigravity Opus (sessão 002):** Reestruturação lean — criou `history/`, `.agents/workflows/` (3 workflows), `referencia/estilo-resumo.md`, reformatou ESTADO.md como fonte de verdade, absorveu INSTRUCOES_AGENTE.md nos workflows. Criou resumo DM2 e reformatou para padrão IPUB. Deletou Cronograma/.

**Pré-002 | Diversas ferramentas (sessão 001):** Histórico retroativo — 21 resumos, 36 entradas no caderno, infraestrutura inicial. Ver `history/session_001.md`.

---

## Próximos passos

1. Avançar para a **Fase 2 do Roadmap**: Estruturar conversão automatizada do Caderno de Erros em Flashcards.
2. Criar script de popularização de `SQLite` a partir dos resumos atuais.
3. Continuar alimentando a Fase 1 (mais questões/resumos de áreas com baixa cobertura).

---

## Decisões críticas (não reverter)

- **Governança via AGENTE.md**: O boot e o fechamento seguem estritamente o `AGENTE.md`.
- **Regra "Siamese Twins" (Híbrido Fase 2)**: DB (`ipub.db`) e Markdown devem ser atualizados em sincronia exata. Analisou uma questão? Ela deve figurar nos 2 lugares. **Script oficial:** `python Tools/insert_questao.py`.
- `caderno_erros.md` atualizado a CADA questão — nunca em batch.
- `progresso.md` derivado do caderno — atualizar junto.
- Protocolo de análise (`Tools/comando de analise de questao.md`) carregado ANTES de analisar qualquer questão.
- Resumos seguem spec em `Tools/estilo-resumo.md` — bullets hierárquicos, ⭐/⚠️/🔴; **sem tabelas, sem fluxogramas ASCII**.
- Sessions numeradas globalmente em `history/` — qualquer agente registra.
- `extract_pdfs.py` é CLI genérica para extração para `%TEMP%`.

---

## Para retomar: leia nesta ordem

1. **`AGENTE.md`** —— Protocolo de boot.
2. **`HANDOFF.md`** —— Onde o último agente parou.
3. **`ESTADO.md`** —— Este arquivo (visão geral).

---

## Contexto do repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
