---
type: onboarding
layer: root
status: canonical
---

# MedHub — Ambiente de Estudo para Residência Médica

Workspace state-driven de estudos médicos. Processa questões de prova, registra padrões de erro no banco SQLite (`ipub.db`) e mantém resumos clínicos estruturados em `Temas/`. Portável para qualquer LLM via workflows em `.agents/`.

## Para começar

1. Leia `AGENTE.md` — protocolo de boot obrigatório
2. Leia `ESTADO.md` — snapshot canônico do projeto
3. Leia `HANDOFF.md` — onde a última sessão parou
4. Use o workflow apropriado em `.agents/workflows/`
5. Dashboard: `streamlit run streamlit_app.py`

## Arquitetura do projeto

```
MedHub/
│
├── AGENTE.md              ← bootstrap protocol (ler primeiro)
├── ESTADO.md              ← snapshot canônico (fonte de verdade documental)
├── HANDOFF.md             ← estado operacional curto (próximo passo)
├── roadmap.md             ← direção evolutiva do produto
│
├── ipub.db                ← SSOT de dados (erros, FSRS, cronograma) — não commitar
├── flashcards_cache.json  ← cache de flashcards gerados por LLM
│
├── .agents/workflows/     ← workflows portáveis por tarefa
│   ├── analisar-questoes.md
│   ├── criar-resumo.md
│   ├── registrar-sessao.md
│   └── gerar-reforco.md
│
├── Temas/                 ← base de conhecimento clínica (resumos por área)
│   ├── Cirurgia/
│   ├── Clínica Médica/
│   ├── GO/
│   ├── Pediatria/
│   └── Preventiva/
│
├── history/               ← logs de sessão (session_NNN.md)
│   └── legacy/            ← arquivos arquivados (caderno_erros, progresso, planos antigos)
│
├── Tools/                 ← scripts utilitários e specs de qualidade
│   ├── estilo-resumo.md   ← spec de formatação obrigatória
│   ├── comando de analise de questao.md  ← protocolo de análise (9 etapas)
│   ├── insert_questao.py  ← CLI: insere erro no ipub.db
│   └── extract_pdfs.py    ← CLI: extrai PDF para %TEMP%, política Zero PDF
│
├── app/                   ← Streamlit multipage app
├── Fichas/                ← PDFs de fichas (leitura apenas)
└── Memorex/               ← PDFs Memorex por área (leitura apenas)
```

## Camadas do sistema

| Camada | Artefatos |
|---|---|
| Bootstrap / protocolo | `AGENTE.md`, `CLAUDE.md` |
| Estado e snapshot | `ESTADO.md`, `HANDOFF.md` |
| Dados operacionais | `ipub.db`, `flashcards_cache.json` |
| Base de conhecimento | `Temas/**` |
| Workflows portáveis | `.agents/workflows/**` |
| Specs de qualidade | `Tools/estilo-resumo.md`, `Tools/comando de analise de questao.md` |
| Interface | `streamlit_app.py`, `app/**` |
| Histórico | `history/session_NNN.md` |
