---
description: "Protocolo completo de análise de questão errada: habilidades sequenciais, diagnóstico do elo quebrado e inserção no ipub.db via insert_questao.py."
type: skill
layer: commands
status: canonical
---

# Skill: Analisar Questão

> Consultar este arquivo SEMPRE antes de analisar qualquer questão de prova.
> Aplica o método de habilidades sequenciais e persiste o resultado no banco.

---

## 1. Princípio Central: Raciocínio Sequencial com Habilidades

Toda questão exige uma cadeia de **habilidades sequenciais**. Se identificar e seguir corretamente cada elo, é impossível errar a questão. O erro sempre ocorre em um elo específico — nunca "na questão toda".

---

## 2. Protocolo de Análise (Etapas 1-5)

### ETAPA 1 — Leitura Estratégica do Enunciado
- Identifique **o que a questão está pedindo** (diagnóstico? conduta? exame? mecanismo?).
- Identifique **quantas etapas intermediárias** existem entre o enunciado e a resposta.
- Perceba se a questão **omite informações propositalmente** (ex: não dá o diagnóstico, só dá o quadro clínico).

### ETAPA 2 — Mapeamento das Habilidades Sequenciais
Decomponha o raciocínio em **habilidades sequenciais numeradas**:

```
Habilidade 1: [primeiro passo cognitivo]
Habilidade 2: [segundo passo cognitivo]
Habilidade 3: [terceiro passo cognitivo]
```

Exemplos de habilidades:
- Identificar o diagnóstico a partir do quadro clínico
- Saber o padrão-ouro para confirmar o diagnóstico
- Associar duas condições a uma única etiologia
- Indicar a conduta correta para a condição identificada

### ETAPA 3 — Informações-Chave
Para cada habilidade, extraia o **conceito central** que a resolve:

```
Informação-chave 1: [conceito que resolve a Habilidade 1]
Informação-chave 2: [conceito que resolve a Habilidade 2]
```

### ETAPA 4 — Análise das Alternativas
- Identifique **por que cada alternativa incorreta está errada**, vinculando a falha a uma habilidade específica.
- Identifique **armadilhas**: alternativas que parecem corretas se falhar em um dos elos.

### ETAPA 5 — Classificação de Complexidade
- **Baixa:** 1-2 habilidades (questão direta/decoreba)
- **Média:** 3 habilidades (raciocínio estruturado)
- **Alta:** 4+ habilidades (raciocínio encadeado com nuances)

---

## 3. Metacognição: Diagnóstico do Erro

| Habilidade | Acertou? | Se errou, por quê? |
|---|---|---|
| Habilidade 1 | Sim / Não / Incerteza / Desatenção | Motivo específico |
| Habilidade 2 | ... | ... |

**Regras:**
- **Não mate formiga com bazuca**: se errou na Habilidade 1, revisar as demais não ajuda. Foque no elo que quebrou.
- **Não tolere errar duas vezes pelo mesmo motivo**: alerta crítico.
- **Diferencie "não sabia" de "sabia mas não aplicou"**: tratamentos diferentes.

---

## 4. O que Extrair para o Resumo

1. **Habilidades sequenciais**: a cadeia completa de passos lógicos
2. **Informações-chave**: os conceitos centrais de cada passo
3. **Associações clínicas relevantes**: conexões entre condições, síndromes, tratamentos
4. **Diferenciações importantes**: pistas clínicas discriminatórias
5. **Nuances e armadilhas**: detalhes que mudam a resposta
6. **Padrões de prova**: se a questão segue modelo recorrente de cobrança

### ⚠️ REGRA CRÍTICA: Como inserir no resumo

O conteúdo extraído deve ser incorporado **de forma natural e técnica** ao bloco temático correspondente, como se sempre tivesse feito parte da documentação clínica.

**NUNCA:** escrever "Foco do erro na Q1", "Q2 abordou...", ou qualquer variante.
**SEMPRE:** identificar o **bloco temático correto** e inserir como bullet integrado ao texto existente.

O resumo é um **documento técnico de referência**, não um caderno de erros.

---

## 5. Perspectiva do Examinador

O examinador:
- Vê um caso clínico real e interessante
- Constrói um **desafio** que exige raciocínio + repertório
- Garante que exista **um caminho lógico único** até a resposta correta
- Encadeia etapas intermediárias para aumentar a complexidade

Ao analisar: **"Qual desafio o examinador quis criar aqui?"**

---

## 6. Padrões Comuns de Encadeamento

| Padrão | Exemplo |
|---|---|
| Quadro clínico → Diagnóstico → Exame confirmatório | Miocardite → Biópsia endomiocárdica |
| Quadro clínico → Diagnóstico → Conduta → Detalhe técnico | Pneumotórax hipertensivo → Punção → Borda superior da costela inferior |
| Quadro clínico → Síndrome → Etiologia → Associação clássica | Edema face + fraqueza → SVCS + miastenia → Timoma |
| Tratamento → Evolução → Complicação vs. sinal esperado | IAM trombolisado → RIVA → Sinal de reperfusão → Monitorizar |

---

## 7. Checklist Rápido

- [ ] Identifiquei o que a questão pede?
- [ ] Mapeei as habilidades sequenciais?
- [ ] Extraí as informações-chave de cada habilidade?
- [ ] Analisei as alternativas vinculando cada uma a uma falha específica?
- [ ] Classifiquei a complexidade?
- [ ] Identifiquei nuances e armadilhas?
- [ ] As informações-chave estão prontas para inserir no resumo?

---

## 8. Output Final (4 entregas obrigatórias)

Após análise, entregar **exatamente** estas quatro coisas:

1. **O Diagnóstico:** Qual elo quebrou e o motivo sucinto.
2. **Draft para o Resumo:** O texto final (⚠️ Padrão de Prova ou 🔴 Armadilha) exato para inserir em `Temas/`, seguindo bullets, sem tabelas ASCII.
3. **Campos estruturados do Flashcard (5 campos):**

```
frente_contexto: [1-2 frases do cenário clínico — sem alternativas, sem gabarito]
frente_pergunta: [a pergunta clínica direta, terminando em "?"]
verso_resposta:  [resposta direta e completa — nunca uma letra isolada]
verso_regra_mestre: [regra/princípio que resolve o caso — 2-3 frases densas]
verso_armadilha: [o distrator do examinador — 1-2 frases]
```

4. **Comando insert_questao.py** com todos os campos, incluindo os 5 estruturados.

---

## 9. Persistir no Banco (insert_questao.py)

Após análise, registrar o erro no `ipub.db`:

```bash
python Tools/insert_questao.py \
  --area "[Cirurgia|Clinica Medica|Pediatria|GO|Preventiva]" \
  --tema "[ex: Trauma Abdominal]" \
  --titulo "[titulo curto do erro]" \
  --enunciado "[enunciado limpo, sem alternativas]" \
  --correta "[texto completo da alternativa correta — nunca so a letra]" \
  --marcada "[texto do que foi marcado]" \
  --erro "[tipo: Lacuna de conhecimento | Erro de aplicacao | Armadilha | Desatencao]" \
  --elo "[habilidade que faltou]" \
  --armadilha "[o que o examinador usou para induzir ao erro]" \
  --complexidade "[Baixa|Media|Alta]" \
  --habilidades "[Hab 1 -> Hab 2 -> Hab 3]" \
  --faltou "[conceito especifico que estava faltando]" \
  --explicacao "[regra mestre em 2-3 frases]" \
  --frente_contexto "[1-2 frases do cenario clinico]" \
  --frente_pergunta "[pergunta clinica direta, terminando em ?]" \
  --verso_resposta "[resposta direta e completa]" \
  --verso_regra_mestre "[principio que resolve o caso]" \
  --verso_armadilha "[distrator do examinador]"
```

**Parâmetros obrigatórios:** `--area`, `--tema`, `--enunciado`, `--correta`, `--marcada`, `--erro`, `--elo`, `--armadilha`

**Parâmetros opcionais:** `--complexidade` (default: Media), `--habilidades`, `--faltou`, `--explicacao`, `--titulo`

**Parâmetros de qualidade (sempre fornecer):** `--frente_contexto`, `--frente_pergunta`, `--verso_resposta`, `--verso_regra_mestre`, `--verso_armadilha`

**Resultado:** Insere em `questoes_erros` + gera 1-2 flashcards IPUB v5.0 com campos estruturados em `flashcards` + inicializa estado FSRS em `fsrs_cards`.

> **Dica PowerShell:** Evitar caracteres especiais (emojis, unicode) nos argumentos CLI — usar apenas ASCII simples. Se o valor contiver aspas, usar apostrofos internos ou escapar com `\"`.
