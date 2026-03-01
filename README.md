# IPUB — Sistema de Estudos para Residência Médica

Sistema pessoal de preparação para a prova de residência médica do **IPUB (Instituto de Psiquiatria da UFRJ)**, com foco em raciocínio clínico sequencial e metacognição ativa.

---

## Princípio Central

Toda questão de prova é uma **cadeia de habilidades sequenciais**. Todo erro ocorre em um **elo específico** dessa cadeia. Identificar o elo, nomear o tipo de erro e corrigir a base — não a resposta — é o método.

---

## Componentes do Sistema

| Arquivo | Função |
|---------|--------|
| `INSTRUCOES_AGENTE.md` | Identidade do agente, 7 regras de execução, workflow |
| `Tools/comando de analise de questao.md` | Protocolo de 9 etapas (análise + diagnóstico do erro) |
| `caderno_erros.md` | Banco metacognitivo de erros (23 entradas, 6 tipos) |
| `progresso.md` | Dashboard: entradas por área, padrões, distribuição por tipo |
| `Temas/` | Resumos clínicos por área e especialidade |

---

## Estrutura

```
/
├── CLAUDE.md                  # Ponteiro de contexto para o agente
├── INSTRUCOES_AGENTE.md       # Regras e workflow do agente
├── caderno_erros.md           # Banco de erros metacognitivo
├── progresso.md               # Dashboard de progresso
│
├── Tools/
│   ├── comando de analise de questao.md  # Protocolo completo (9 etapas)
│   └── extract_pdfs.py                   # Script de extração de PDFs
│
└── Temas/
    ├── Cirurgia/
    ├── Clínica Médica/
    │   ├── Cardiologia/
    │   ├── Endocrinologia/
    │   ├── Gastroenterologia/
    │   ├── Infectologia/
    │   ├── Nefrologia/
    │   ├── Neurologia/
    │   └── Pneumologia/
    ├── GO/
    ├── Pediatria/
    └── Preventiva/
```

---

## Protocolo de Análise de Questão (9 etapas)

1. **Leitura estratégica** — eixo clínico, contexto, pedido real
2. **Mapeamento de habilidades sequenciais** — cadeia de raciocínio necessária
3. **Informações-chave** — achados determinantes para a resposta
4. **Análise de alternativas** — por que cada uma está certa ou errada
5. **Classificação de complexidade** — simples / moderada / alta
6. **Diagnóstico do erro** — classificação em 6 tipos (lacuna, parcial, aplicação, leitura, armadilha, incerteza)
7. **Extração para o caderno** — registro estruturado do erro
8. **Perspectiva do examinador** — o que a questão testa de verdade
9. **Atualização do resumo em Temas/** — inserir no ponto temático correto

---

## Estado Atual

| Área | Resumos com conteúdo | Entradas no caderno |
|------|---------------------|---------------------|
| GO | 7/7 | 0 |
| Clínica Médica | 4/8 | 1 |
| Pediatria | 2/2 | 11 |
| Preventiva | 1/2 | 7 |
| Cirurgia | 1/2 | 4 |
| **Total** | **15/21** | **23** |

**Padrão de erro dominante:** Erro de aplicação (48%) — o conteúdo é conhecido, mas a aplicação ao cenário clínico falha.

---

## Distribuição de Erros

| Tipo | N | % |
|------|---|---|
| Erro de aplicação | 11 | 48% |
| Lacuna de conhecimento | 7 | 30% |
| Conhecimento parcial | 4 | 17% |
| Incerteza sem erro de base | 1 | 4% |

---

## Operação Multi-Agente

| Agente | Responsabilidade |
|--------|-----------------|
| **Antigravity** (chat) | Análise de questões, atualização do caderno, enriquecimento de resumos |
| **Claude Code** (CLI) | Git, organização de arquivos, scripts, backup |

O sistema é **portátil**: funciona com qualquer modelo (Claude, GPT, Gemini, Cursor, Windsurf). A inteligência está nos documentos, não no modelo.
