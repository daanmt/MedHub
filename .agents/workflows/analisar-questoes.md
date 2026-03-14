---
description: Analisar questões de prova erradas e atualizar caderno e resumos
---

# Workflow: Análise de Questões

## Contexto
O usuário envia questões que errou (em qualquer formato). O agente analisa, diagnostica o erro, registra no caderno e atualiza o resumo correspondente.

## Pré-requisitos
Ler `Tools/comando de analise de questao.md` — contém o protocolo detalhado de análise por habilidades sequenciais (9 etapas).

## Passos

### 0. Preflight (Obrigatório)
Seguir o **Boot Sequence** definido em `AGENTE.md`.

### 1. Interpretar o input
O usuário envia questões em qualquer formato. Não exigir formato específico. Extrair:
- Enunciado e alternativas
- Alternativa marcada pelo usuário
- Gabarito correto
- Comentário do gabarito (se disponível)

### 2. Aplicar protocolo de análise
Seguir integralmente o protocolo de `Tools/comando de analise de questao.md` (Etapas 1-7).

### 3. Registrar no caderno de erros
- Determinar Área e Tema
- Inserir entrada em `caderno_erros.md` sob o tema correto
- Formato: seguir o padrão já existente no caderno

### 4. Atualizar progresso
Atualizar contadores em `progresso.md`.

### 5. Atualizar o resumo correspondente
- Localizar o arquivo .md em `Temas/{Área}/{Subespecialidade}/`
- Inserir no **local temático correto** (não no final)
- Usar marcadores `⚠️ Padrão de prova:` e `🔴`
- Não duplicar informação já presente

### 6. Popular Banco de Dados Relacional (Siamese Twins)
- OBJETIVO OBRIGATÓRIO: Nenhuma questão vive no Markdown sem viver no DB.
- Rodar o script CLI: `python Tools/insert_questao.py --area "..." --tema "..." --enunciado "..." --correta "..." --marcada "..." --erro "..." --elo "..." --armadilha "..."`
- Preencher os parâmetros cirurgicamente com as tipologias mapeadas no passo 2.

### 7. Responder ao usuário
Apresentar: análise + diagnóstico do erro + confirmação de registros (MD + SQLite).

### 8. Fechamento (Obrigatório)
Seguir o **Protocolo de Fechamento** em `AGENTE.md` e executar o workflow `registrar-sessao.md`.

## Regras
- Tom direto e técnico. Sem linguagem motivacional.
- A cada 10 entradas, verificar padrões recorrentes no caderno.
- Questões acertadas: analisar mesmo assim. Se houver incerteza, registrar.
- Nunca associar iDPP-4 + arGLP-1 (isso é regra médica, não do workflow 😄).
