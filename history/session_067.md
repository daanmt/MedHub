# Session 067 — Correção de Dados e Arquitetura de Rastreamento (Bulk)
**Data:** 2026-04-16
**Ferramenta:** Antigravity
**Continuidade:** Sessão 066

---

## O que foi feito
- Auditoria e correção da defasagem de dados, descobrindo que o `insert_questao.py` incrementava `questoes_realizadas` apenas nos erros.
- Criação e migração da tabela `sessoes_bulk` (`migrar_sessoes_bulk.py`) como Single Source of Truth para volume de questões realizadas/acertadas.
- Migração histórica de 3.020 questões e 2.413 acertos a partir da base do `dashboard-emed.xlsx`.
- População da `taxonomia_cronograma` com os subtemas reais do Excel (`popular_subtemas.py`).
- Reescrita do Dashboard Streamlit (`1_dashboard.py`) para ler da tabela `sessoes_bulk` exibindo Gráficos coloridos, badges de tendência e Foco Crítico.
- Atualização do `insert_questao.py` para isolamento de responsabilidades (não incrementa volume, apenas registra o erro e gera a taxa daquele erro no flashcard FSRS auxiliar).

## Artefatos criados/modificados
- `tools/migrar_sessoes_bulk.py`
- `tools/popular_subtemas.py`
- `tools/registrar_sessao_bulk.py`
- `app/pages/1_dashboard.py`
- `tools/insert_questao.py`
- `ESTADO.md`

## Decisões tomadas
- SSOT alterada: Total de questões aglutinado/global é referenciado doravante pela tabela `sessoes_bulk`.
- Protocolo alterado: `registrar_sessao_bulk.py` deve ser usado explicitamente ao fim de estudo de um bloco de questões de qualquer área.
