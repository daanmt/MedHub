---
description: Analisar questões de prova erradas e atualizar caderno e resumos
---

# Workflow: Análise de Questões e Integração de Insights de Estudo

## Contexto
O usuário envia questões erradas **e/ou anotações feitas enquanto estuda** (abordagem ativa). O agente integra ambos: analisa erros de questão, diagnostica lacunas e incorpora os insights no resumo correspondente de forma natural e assertiva.

## Pré-requisitos
Ler `Tools/comando de analise de questao.md` — contém o protocolo detalhado de análise por habilidades sequenciais.

## Passos

### 0. Preflight (Obrigatório)
Seguir o **Boot Sequence** definido em `AGENTE.md`.

### 1. Interpretar o input — Duas fontes possíveis

**A. Questões erradas:** Extrair:
- Enunciado e alternativas
- Alternativa marcada pelo usuário
- Gabarito correto
- Comentário do gabarito e fórum (se disponível)
- Comentário adicional do usuário sobre o erro

**B. Insights de estudo (anotações ativas):** O usuário pode enviar anotações livres que fez durante o estudo — insights, conexões, dúvidas, consolidações. Tratar essas anotações como matéria-prima valiosa a ser incorporada no resumo. Não exigir formato específico.

### 2. Aplicar protocolo de análise (para questões erradas)
Seguir integralmente o protocolo de `Tools/comando de analise de questao.md` (Etapas 1-7).

### 3. Popular Banco de Dados (Caderno de Erros DB)
- **NÃO ADICIONE MÉTRICAS TEXTUAIS!** O `caderno_erros.md` baseado em texto está depreciado. O Streamlit Dashboard é a única Fonte Real da métrica.
- Para questões erradas, popular os metadados no SQLite via CLI:
  - Execute: `python Tools/insert_questao.py --area "[Cirurgia|Pediatria|GO|...]" --tema "[ex: Trauma]" --enunciado "[enunciado limpo]" --correta "[letra]" --marcada "[letra]" --erro "[tipo de erro]" --elo "[habilidade que faltou]" --armadilha "[explicação e resumo]"`
  - *Dica*: Evite aspas internas no PowerShell — usar nomes sem especiais entre aspas duplas.
- Para insights de estudo sem questão associada: não registrar no SQLite (não há erro mensurável).

### 4. Atualizar o Resumo Clínico de Área (Temas/)
- Localizar o arquivo `.md` do Tema em `Temas/{Área}/{Subespecialidade}/`.
- Incorporar tanto os insights do estudo ativo quanto as armadilhas identificadas nas questões, no **local temático estrutural correto** — nunca solto no final.
- Princípio de assertividade: dois focos simultâneos:
  1. **Pontos-chave da matéria** — ampliam compreensão e raciocínio clínico.
  2. **Pontos-chave de prova** — aspectos mais prevalentes em questões.
- Usar marcadores `⚠️ Padrão de prova:` e `🔴` nas anotações cruciais.
- Não duplicar informação já presente no resumo. Refinar, não inflar.
- **Meta de tamanho:** manter o resumo até ~300 linhas. Ser cirúrgico — cada linha deve ganhar seu lugar.

### 5. Responder ao usuário
Apresentar:
- Análise + diagnóstico do erro (questões erradas)
- Resumo dos insights incorporados (anotações de estudo)
- Confirmação de inserção no SQLite (se aplicável)
- Trecho relevante do resumo atualizado

### 6. Fechamento (Obrigatório)
Seguir o **Protocolo de Fechamento** em `AGENTE.md` e executar o workflow `registrar-sessao.md`.

## Regras
- Tom direto e técnico. Sem linguagem motivacional.
- Questões acertadas com incerteza: registrar mesmo assim.
- A cada 10 entradas, verificar padrões recorrentes.
- Nunca associar iDPP-4 + arGLP-1 (regra médica, não do workflow 😄).
- Nunca referenciar questões dentro do texto do resumo (ex: "na Q1", "questão 3 abordou"). O conteúdo deve ser incorporado como se sempre tivesse estado lá.
