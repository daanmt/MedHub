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

### 3. Popular Banco de Dados (Caderno de Erros DB)
- **NÃO ADICIONE METRICAS TEXTUAIS!** O `caderno_erros.md` e `progresso.md` baseados em texto foram depreciados. O *Streamlit Dashboard* é a única Fonte Real da métrica.
- O Agente DEVE popular os metadados do erro diretamente no SQLite usando rigorosamente a interface CLI contida em `Tools/insert_questao.py`:
  - Execute: `python Tools/insert_questao.py --area "[Cirurgia|Pediatria|...]" --tema "[ex: Trauma]" --enunciado "[enunciado limpo]" --correta "[letra correta]" --marcada "[sua alternativa]" --erro "[tipo de erro diagnosticado]" --elo "[habilidade que faltou]" --armadilha "[explicação e resumo]"`
  - *Dica para o Agente*: Faça escape adequado das aspas internas ao formatar o comando `run_command`.

### 4. Atualizar o Resumo Clínico de Área (Temas/)
- Embora o erro de prova e as métricas residam no SQLite, o **Conteúdo** ainda é em Markdown.
- Localizar o arquivo .md do Tema falho em `Temas/{Área}/{Subespecialidade}/`.
- Inserir a explicação/armadilha no **local temático estrutural correto** daquele arquivo (não no final de forma solta).
- Usar marcadores `⚠️ Padrão de prova:` e `🔴` nas anotações cruciais da residência.
- Não duplicar informação genérica que já esteja descrita no resumo.

### 5. Responder ao usuário
Apresentar: análise + diagnóstico do erro + confirmação de inserção no SQLite (`ipub.db`) + trecho que foi salvo no Resumo da Área.

### 8. Fechamento (Obrigatório)
Seguir o **Protocolo de Fechamento** em `AGENTE.md` e executar o workflow `registrar-sessao.md`.

## Regras
- Tom direto e técnico. Sem linguagem motivacional.
- A cada 10 entradas, verificar padrões recorrentes no caderno.
- Questões acertadas: analisar mesmo assim. Se houver incerteza, registrar.
- Nunca associar iDPP-4 + arGLP-1 (isso é regra médica, não do workflow 😄).
