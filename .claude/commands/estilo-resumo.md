---
description: "Spec de formatação obrigatória para resumos em Temas/. Consultar antes de criar ou editar qualquer resumo clínico."
type: skill
layer: commands
status: canonical
---

# Estilo MedHub — Spec de Formatação para Resumos

> Este documento define o padrão de formatação para todos os resumos em `Temas/`.
> Qualquer agente que criar ou editar resumos DEVE seguir estas regras.

---

## Estrutura Geral

- Título: `# Nome do Tema` (H1, sem metadata de fonte/autor)
- Seções: `## 1. Nome da Seção` (H2 numerado)
- Subseções: `### 1.1 Nome` (H3)
- Sub-sub: `**Título em negrito:**` seguido de bullets

---

## Formatação de Conteúdo

### Usar SEMPRE
- **Bullets hierárquicos** com `-` para organizar informações
- **Negrito** para termos-chave, nomes de drogas, diagnósticos
- `⭐` para conceitos fundamentais que não podem ser esquecidos
- `⚠️ Padrão de prova:` para armadilhas de examinador e nuances
- `🔴` para armadilhas na seção final "Armadilhas de Prova"
- Blocos `>` (blockquote) para destaques e alertas importantes
- Separadores `---` entre seções principais

### NUNCA usar
- **Tabelas** — em qualquer tamanho ou formato. Sempre converter para bullets hierárquicos. Sem exceções.
- Fluxogramas ou algoritmos em ASCII (blocos ` ``` `) — converter para bullets hierárquicos com condicionais em texto (`→ se X:`, `→ se não:`)
- **Emojis em headers (H1/H2/H3)** — proibido usar 🧭, 🕒, 🚨, 🟢, 🟡, 🔴, 🔵 ou qualquer emoji como prefixo de título de seção. Emojis são permitidos apenas inline no corpo do texto como marcadores (`⭐`, `⚠️`, `🔴`).
- **`✅` e `❌` como marcadores de bullet** — substituir por bullets `-` normais com negrito para destacar status (ex: `- **Conduta recomendada:**` / `- **Proscrito:**`).
- **Campo `estilo:` no frontmatter** — o frontmatter aceita apenas `area`, `tema`, `type`, `especialidade`, `status`, `aliases`. Campos como `estilo: Gold Standard` são não-padrão e devem ser removidos.
- **Rodapés editoriais** — proibido encerrar o arquivo com frases como `*Este resumo foi cristalizado a partir de...*` ou qualquer nota de origem/autoria. O arquivo termina na última armadilha de prova.
- Headers de metadata no topo (fonte, autor, ano, versão)
- **Linguagem Informal ou Coloquial** — PROIBIDO o uso de termos como "Vamos lá", "Dica de plantão", "Pulo do gato", "Se matar", "Vai morrer", "Encher balde furado", etc.
- **Termos Não-Clínicos** — Evitar metáforas dramáticas ou gírias (ex: "letal", "bizarra", "engarrafa"). Use terminologia acadêmica (ex: "potencialmente fatal", "atípica", "congestão retrógrada").
- **Referências a questões de prova dentro do texto** — nunca escrever "Foco do erro na Q1", "Q2 na prova", "Questão 3 abordou...", etc. O conteúdo aprendido com questões deve ser incorporado de forma natural ao tema, como se sempre tivesse feito parte do resumo.

---

## Tom e Benchmark MedHub 80/20

- **80% Assertividade:** Foco cirúrgico no que é cobrado em prova: condutas do ATLS 10, scores AAST, critérios diagnósticos, tabelas de choque e diretrizes oficiais.
- **20% Didática Clínica (O Padrão-Ouro):** O resumo deve explicar o *porquê* clínico de forma densa. Não é apenas "fazer X", é "fazer X porque o mecanismo Y impede Z". Use terminologia técnica acadêmica em vez de simplificações exageradas.
- **Regra da Especificidade Técnica:** Nunca use descrições genéricas se houver uma classificação oficial ou critério quantitativo disponível (ex: use AAST Grau IV, não apenas "lesão renal grave").
- **Linguagem:** 100% profissional e acadêmica. Proibição absoluta de gírias de plantão (ex: "encher balde", "vai morrer", "nuance de prova"). O leitor é um colega médico buscando excelência técnica.
- **Frases:** Curtas, densas e afirmativas.

---

## Seção Final Obrigatória

Todo resumo DEVE terminar com a seção abaixo. **IMPORTANTE:** Esta seção é **CUMULATIVA**. Jamais remova armadilhas antigas para dar lugar a novas; novos insights devem ser anexados aos existentes para garantir que o resumo evolua sem perder histórico.

```
## N. Armadilhas de Prova

- 🔴 [armadilha 1]
- 🔴 [armadilha 2]
...
```

Esta seção consolida todos os `⚠️ Padrão de prova` espalhados pelo resumo + armadilhas identificadas na análise de questões (registradas via `Tools/insert_questao.py` no `ipub.db`).

---

## Cobertura de Conteúdo — Checklist por Tipo de Tema

Além das regras de formato, o resumo deve cobrir todos os tópicos clinicamente relevantes. Lacunas de conteúdo são tão graves quanto violações de estilo. Tópicos frequentemente omitidos por área:

**Obstetrícia/GO:**
- Epidemiologia OMS (limiares numéricos específicos)
- Mecanismo de parto (tempos, ângulos de rotação, regras de restituição)
- Taquissistolia e parto taquitócico
- Indicações de cesárea emergência vs. eletiva (com nuances — ex: placenta prévia mesmo com feto morto)
- VCE: taxa de sucesso, complicação mais comum vs. mais rara, fatores favoráveis/contraindicações
- Distinção entre métodos não farmacológicos invasivos e não invasivos
- Estratificação de risco e profilaxia de HPP
- Nuances de timing (ex: dequitação 30 min vs. 60 min se paciente estável)

**Cirurgia/Trauma:**
- Scores com critérios completos e thresholds
- Condutas por grau (ex: AAST I–V)
- Indicações de exploração cirúrgica vs. conservador

**Clínica Médica:**
- Critérios diagnósticos com valores quantitativos
- Classificações funcionais (ex: NYHA, Child-Pugh)
- Alvos terapêuticos numéricos

## Referências de Estilo (exemplos reais)

- `Temas/Cirurgia/Trauma.md` — formatação de referência para trauma
- `Temas/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md` — formatação de referência para clínica
- `Temas/GO/Assistência ao Parto.md` — referência para obstetrícia: cobertura de mecanismo de parto, taquissistolia, VCE com detalhes, indicações de cesárea, HPP preventivo e armadilhas densas
