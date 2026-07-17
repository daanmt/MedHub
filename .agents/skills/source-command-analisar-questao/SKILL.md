---
name: "source-command-analisar-questao"
description: "Protocolo completo de análise de questão errada: habilidades sequenciais, diagnóstico do elo quebrado e inserção no ipub.db via insert_questao.py."
---

# source-command-analisar-questao

Use this skill when the user asks to run the migrated source command `analisar-questao`.

## Command Template

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

### 3.1 Calibração hard-skill x soft-skill (peso da análise)

Padrões de execução de prova já catalogados (bug nº1, enunciado negativo, ancoragem no número, etc. -- ver memória `feedback_analise_questoes`) são reais e valiosos, mas **não são o ponto de partida da análise**. Usá-los como reflexo automático encurta a investigação e limita o diagnóstico -- o erro vira "ah, é o bug nº1 de novo" antes de esgotar o que especificamente da disciplina não foi dominado.

**Regra de peso:** ~80% da análise vai para o diagnóstico técnico/clínico específico (qual mecanismo, critério, conduta ou discriminador da matéria não foi dominado -- Etapas 1-4 acima, aplicadas a fundo). Os ~20% restantes cobrem a camada de execução de prova (se um padrão já catalogado também se aplica). Diagnosticar o elo tecnicamente **primeiro**; só depois, e de forma breve, verificar se o padrão de execução se encaixa -- nunca o contrário.

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

### ⚠️ Afirmação decisória controversa → auditar a evidência

Quando a `explicacao_correta`/`verso_regra_mestre` fizer uma afirmação **decisória** (conduta de 1ª linha, dose, cutoff, score, critério, contraindicação) **e** houver controvérsia, banca-dependência ou confiança < alta, auditar pela hierarquia de `core/contracts/evidence-governance.md` (sociedades BR + MS > RCT/INT > consenso) via `/pesquisar-evidencia` ou o subagente `evidence-researcher`. Se o gabarito da banca divergir da diretriz vigente: **ensinar a resposta da banca + registrar 🔴 armadilha "banca-dependente"** (contrato §6). Citar a fonte (sociedade/ano ou PMID). Nunca fabricar fonte (honest-negative).

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
2. **Draft para o Resumo:** O texto final (⚠️ Padrão de Prova ou 🔴 Armadilha) exato para inserir em `resumos/`, seguindo bullets, sem tabelas ASCII.
3. **Cards estruturados -- consultando o deck EMED (seleção por contexto, s124):**

   Antes de cunhar, **consultar o deck de referência do EMED** do tema (275 decks atômicos colhidos em `resumos/**/Flashcards - <Tema>.pdf`):

   ```bash
   python tools/emed_flashcards.py --query --tema "<tema>" [--area <area>]
   ```

   Retorna os pares frente/verso atômicos do EMED (`match: exact|fuzzy` -> `cards`), ou `match: none` com `candidates`.

   - 🔴 **Seleção por contexto -- NUNCA o deck inteiro.** Dos pares retornados, puxar **apenas os que tocam o elo quebrado / a lacuna** do erro (o critério de match é o elo do aluno x o conteúdo do par EMED). Adaptar ao **padrão atômico** (`estilo-flashcard.md §Formato atômico`), ancorando no erro específico. O deck EMED é **molde de formulação + fonte de cobertura**, não um despejo no FSRS (a estratégia "matar os cards" e o teto de 30/dia proíbem import em massa).
   - **Fallback gracioso:** se `match: none` (tema sem deck) ou nenhum par casa o elo, cunhar do zero pelo **mesmo padrão atômico** -- sem travar.
   - Cunhar **1 a 3 cards atômicos** (frente gerativa curta, resposta de uma frase, o "porquê" fora do recall). Se o deck EMED diverge do resumo/gabarito auditado, **não copiar cego** -- herda a auditoria de evidência (`estilo-flashcard.md §Evidência`). Cada card tem os 5 campos:

```
frente_contexto: [1-2 frases do cenário clínico — sem alternativas, sem gabarito; pode ser vazio]
frente_pergunta: [a pergunta clínica direta, terminando em "?"]
verso_resposta:  [resposta direta e completa — nunca uma letra isolada]
verso_regra_mestre: [a distinção/sobreposição que previne a confusão]
verso_armadilha: [o distrator específico que pegou o aluno]
```

> A semântica de **como** escrever cada campo (atômico, sem vazamento, ancorado no resumo) é definida em `estilo-flashcard.md` — não reespecificar aqui.

4. **Comando insert_questao.py** com todos os campos, incluindo os 5 estruturados.

---

## 9. Persistir no Banco (insert_questao.py)

Após análise, registrar o erro no `ipub.db`:

```bash
python tools/insert_questao.py \
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

**Mapeamento arg → coluna em `questoes_erros` (F28 — evita criar coluna redundante):**

| Argumento | Coluna persistida |
|---|---|
| `--faltou` | **`o_que_faltou`** — coluna canônica do "elo/o que faltou" |
| `--habilidades` | `habilidades_sequenciais` |
| `--erro` | `tipo_erro` |
| `--elo` | **nenhuma coluna própria** |

🔴 **`--elo` NÃO tem coluna própria.** Apesar de obrigatório, seu texto **não é persistido** como campo — ele alimenta **apenas** o matcher de reincidência **F25** (`checar_reincidencia`, junto de `--faltou`/`--habilidades`) para sinalizar erro similar já registrado no tema. O campo canônico do elo/lacuna é **`o_que_faltou`** (via `--faltou`). Uma sessão futura **não deve** criar uma coluna `elo` — o mapeamento acima é o contrato.

**Exit code (F27):** modo single retorna `0` em sucesso e `1` em falha (simétrico ao `--errors-file`) — um wrapper/hook pode confiar no código de saída.

**Resultado:** Insere em `questoes_erros` + gera 1-2 flashcards IPUB v5.0 com campos estruturados em `flashcards` + inicializa estado FSRS em `fsrs_cards`.

> **Dica PowerShell:** Evitar caracteres especiais (emojis, unicode) nos argumentos CLI — usar apenas ASCII simples. Se o valor contiver aspas, usar apostrofos internos ou escapar com `\"`.
