# IPUB — Ambiente de Estudo para Residência Médica

Agente de estudo que analisa questões de prova, registra padrões de erro e mantém resumos clínicos organizados. Portável para qualquer LLM via workflows.

## Estrutura

```
IPUB/
├── ESTADO.md              ← fonte de verdade (ler primeiro)
├── CLAUDE.md              ← pointer para Claude Code
├── ipub.db                ← Banco de Dados Principal (Erros + Cronograma)
├── caderno_erros.md       ← [LEGADO] Mantido por histórico
├── progresso.md           ← [LEGADO] Mantido por histórico
│
├── .agents/workflows/     ← workflows portáveis
│   ├── criar-resumo.md
│   ├── analisar-questoes.md
│   └── registrar-sessao.md
│
├── Temas/                 ← resumos clínicos estruturados
│
├── history/               ← logs de sessão (D-0, D-1...)
│
├── Tools/                 ← scripts utilitários
│   ├── insert_questao.py  ← Inserção de diagnósticos no DB
│   ├── migrate_cronograma.py ← Sincronizador Excel -> SQLite
│   └── extract_pdfs.py    ← extrator OCR de apostilas
└── Cronograma de Reta Final.xlsx ← Planejamento Estratégia Med
```

## Para começar

1. Leia `AGENTE.md`
2. Use o workflow apropriado em `.agents/workflows/`
3. Rode o Dashboard: `streamlit run streamlit_app.py`
