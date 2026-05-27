# Session 025 — Reforma IPUB v3.0 (Estabilização Final)
**Data:** 2026-03-14
**Ferramenta:** Antigravity (Advanced Agentic Coding)
**Continuidade:** Sessão 024

---

## O que foi feito
- **Reforma Cirúrgica v3.0:** Executei a limpeza de "over-engineering" do projeto, removendo o FSRS fake e restaurando a arquitetura **Zero-DB** na UI do Streamlit.
- **Parser de Alta Fidelidade (Stateful):** Reescrita do `app/utils/parser.py` para herdar Área e Tema corretamente dos cabeçalhos MD. Implementado suporte a variantes de campos (`Armadilha / nuance`, etc.).
- **Flashcard Anti-Crash:** Refatoração do player para usar **shuffle por índices** em vez de IDs, eliminando o erro fatal de `KeyError` na regeneração do cache.
- **Simplificação do Dashboard:** Removidas métricas redundantes e sessões "hot topics" sem base real. Agora o Dashboard reflete 100% o conteúdo do `caderno_erros.md`.
- **Persistência Federada:** Novo formulário de registro de erro que escreve diretamente no Markdown, mantendo a integridade do rastro de auditoria.
- **Navegação Consolidada:** Reorganização das páginas em 5 pilares: Dashboard, Flashcards, Caderno, Resumos e Progresso.

## Artefatos criados/modificados
- `app/utils/parser.py`: Parser stateful e helper de salvamento MD.
- `app/pages/02_flashcards.py`: Novo player estável e filtrável.
- `app/pages/01_dashboard.py`: Dashboard honesto focado em lacunas.
- `app/pages/03_caderno.py`: Modo consulta e registro Zero-DB.
- `app/pages/05_progresso.py`: Consolidação de histórico e análise de área.
- `app/utils/flashcard_builder.py`: Prompt atualizado para os nomes reais dos campos.
- `streamlit_app.py`: Nova estrutura de navegação v3.0.

## Decisões tomadas
- **Single Source of Truth:** O Markdown é a fonte primária e absoluta de verdade para a interface. O SQLite permanece como motor de ML futuro, mas não dita a leitura da UI.
- **Estabilidade sobre Feature-Creep:** Removi o FSRS da interface por ser uma implementação simulada que gerava bugs; o foco agora é a retenção via flashcards manuais estáveis.

## Próximos passos
- Validar a sincronização GitHub via botão no App.
- Expandir a base de erros para bater o marco de 100 entradas.
