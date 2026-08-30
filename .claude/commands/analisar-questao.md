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

🔴 **Escreva a habilidade para ser REUTILIZÁVEL entre questões.** Ela alimenta o **Ledger de Habilidades** (§10), cujo produto é responder *"qual habilidade eu falho em temas diferentes"*. Uma habilidade redigida como frase única daquela questão nunca reincide e não gera sinal.
- ✅ `Reconhecer enunciado negativo e rotular cada alternativa V/F`
- ❌ `Reconhecer que nesta questão de 2019 sobre PTI o enunciado pedia a EXCETO`
- Nunca usar `N/A`, `Diagnóstico`, `Terapêutica`, `Conduta` isolados — são rótulos de categoria, não elos de raciocínio, e o ledger os descarta.
- **Marque qual habilidade QUEBROU.** Numa cadeia de 4, tipicamente só 1 falhou; as outras 3 o usuário executou bem. Registrar a cadeia toda como erro envenena a métrica.

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
  --area "[subespecialidade real -- ver tabela abaixo]" \
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

🔴 **`--area` é a subespecialidade real, não uma macro-área (achado s146).** O banco inteiro (`taxonomia_cronograma`, todo o histórico de `questoes_erros`) já usa ~20 valores — `Cardiologia`, `Nefrologia`, `Neurologia`, `Endocrino`, `Gastro`, `Hepato`, `Hemato`, `Reumato`, `Pneumo`, `Dermato`, `Psiquiatria`, `Otorrino`, `Ortopedia`, além de `Cirurgia`/`Pediatria`/`Preventiva`/`Ginecologia`/`Obstetrícia` — não as 5 grandes áreas do exemplo antigo acima. **Antes de escolher, consulte `select distinct area from taxonomia_cronograma`** e reuse o valor exato já existente para o domínio; só crie um valor novo se genuinamente não houver nenhum próximo. `GO`/`Ginecologia`/`Obstetrícia` coexistem como 3 valores fragmentados do mesmo domínio amplo — preferir `Ginecologia` ou `Obstetrícia` (o específico) a `GO` daqui em diante, sem reclassificar retroativamente sem pedido explícito.

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

---

## 10. Ledger de Habilidades (`tools/habilidades.py`)

> **Assinatura canônica deste CLI** (AGENTE.md §7.2: a assinatura completa vive em UMA skill). Spec: `.vibeflow/specs/ledger-de-habilidades.md`.

**Por que existe:** na faixa dos 75-80% o gargalo deixa de ser conteúdo e passa a ser **direcionamento**. "Área fraca = Colecistite" é a granularidade dos 60%; nesta faixa a pergunta útil é *qual habilidade eu falho, através de temas diferentes*. O ledger promove `habilidades_sequenciais` (prosa) a entidade consultável, sem migrar o campo de origem.

| Comando | Função |
|---|---|
| `--backfill [--dry-run]` | Popula o ledger a partir de `questoes_erros`. **Read-only na origem**, idempotente. |
| `--report` | Panorama: catálogo, ocorrências, distribuição de vereditos, fila de curadoria. |
| `--reincidentes [--limit N] [--min-temas N]` | Habilidades por reincidência + nº de temas distintos. |
| `--add "texto" --area A --tema T [--veredito V] [--questao-id N]` | Registra habilidade avulsa. |

**Vereditos (enum fechado):** `acertou` · `incerteza` · `errou` · `indefinido`. Valor fora do conjunto levanta `ValueError`.

🔴 **`incerteza` é estado de primeira classe.** "Acertei na dúvida" não é acerto — é uma bomba-relógio que a prova detona. Quando o usuário sinalizar hesitação numa questão que acertou, registrar `--veredito incerteza`, não deixar passar como acerto.

🔴 **Questão ACERTADA também rende registro.** Uma questão pode ter a habilidade-alvo correta e ainda expor 2-3 lacunas colaterais que o usuário não percebeu. Hoje esse sinal morreria: `insert_questao.py` só é chamado para questão errada. Use `--add` — ele **não** escreve em `questoes_erros` nem em `sessoes_bulk` (não vira erro nem volume).

🔴 **`temas_distintos >= 3` separa padrão de raciocínio de lacuna de conteúdo.** A mesma habilidade falhando em 3 temas diferentes não é desconhecer os temas — é desconhecer a habilidade. Esses casos são candidatos diretos à família do bug nº 1 e devem ser tratados como tal (playbook de execução de prova), não com mais leitura do tema.

**Fronteira dura:** este CLI escreve **apenas** em `habilidades` e `questao_habilidades`. Nunca toca FSRS, `flashcards`, `questoes_erros` ou `sessoes_bulk`.

🔴 **`--add` COMPLEMENTA `insert_questao.py` — nunca o substitui (F38).** É o defeito mais caro já registrado neste pipeline e ele é **silencioso**: a s127 analisou 6 erros em profundidade, gravou 7 habilidades aqui e **zero** linhas em `questoes_erros`. Consequência: os cards nasceram sem âncora (`questao_id=NULL`) e o substrato canônico (`tipo_erro`, `alternativa_marcada`, `explicacao_correta`) ficou só em prosa no log da sessão — invisível para áreas fracas, armadilhas de resumo e reincidência.

- **Erro de questão de bloco → SEMPRE `insert_questao.py` primeiro.** O `--add` entra depois, se você quiser promover a habilidade avulsa.
- **`--add` sozinho só é correto quando não há erro**: questão acertada com lacuna colateral, ou `incerteza`.
- A CLI **avisa em stderr** quando recebe `--veredito errou` sem `--questao-id`, e o `auto_check` levanta `[WARN] ERROS_ORFAOS` para qualquer dia-bloco com erros em `sessoes_bulk` e nenhuma linha em `questoes_erros` (janela d..d+1). Nenhum dos dois bloqueia — quem decide é você, mas agora em voz alta.

---

## 11. Taxonomia da questão e ORÇAMENTO de correção

> Origem: Pedro Martins, "o método mais rápido para corrigir questões". O tempo de correção é recurso finito — gastar 20 min numa questão direta rouba o tempo de outra que renderia mais, e derruba o volume.

🔴 **Antes de analisar, classifique o TIPO. O tipo define quanto esforço a questão merece.**

| Tipo | Assinatura | Orçamento de correção |
|---|---|---|
| **Direta** (decoreba) | "ou você sabe ou não sabe"; sem etapa intermediária | **1 aprendizado, 2-4 linhas.** NÃO reler a resolução inteira, NÃO revisar o tema. Extrair o fato, cunhar 1 card, seguir. |
| **Fluxograma** | decisão estruturada por nós (sífilis congênita, reanimação neonatal, ACLS, cálculo renal) | **Identificar em QUAL NÓ errou.** O aprendizado é o nó, não o fluxograma inteiro. Reapresentar o fluxograma fechado + marcar o nó. |
| **Raciocínio** | 3+ etapas encadeadas; enunciado omite o diagnóstico de propósito | **Análise completa** (Etapas 1-5 + metacognição). É aqui que o orçamento longo se paga. |

**Exemplos de calibração:**
- "Qual o tempo máximo de armazenamento do leite materno ordenhado?" -> **Direta**. Errou = não sabia 12h/15 dias. Um card. Fim. Não reler aleitamento.
- "Cálculo de 2 cm em polo inferior, qual conduta?" -> **Fluxograma**. Errou = ou não sabia que tamanho e local são os nós decisores, ou errou o valor de corte. O card é o nó específico.
- "Lúpus + cefaleia súbita + anticardiolipina, qual conduta?" -> **Raciocínio**. Duas etapas (identificar trombose venosa cerebral -> indicar anticoagulação). Vale a análise cheia.

🔴 **A crítica que sustenta a regra:** errar uma questão de nefrolitíase **não** significa "estudar nefrolitíase". Significa que faltou **uma regra específica**. Mandar mais questões do tema é matar formiga com bazuca — é justamente o que o [[ledger de habilidades]] (§10) existe para evitar. O reforço deve mirar a **habilidade**, não o tema.

### Verificar habilidades mesmo quando ACERTOU

Acerto não encerra a análise. Pergunte: *executei todas as etapas, ou acertei por intuição/eliminação?* Habilidade resolvida "na sorte" registra-se com **`--veredito incerteza`** (§10) — e uma questão acertada pode expor 2-3 lacunas colaterais que valem `--add`. É o sinal que o pipeline de erro descartaria inteiro.

**Os 4 estados por habilidade** (não 2): `acertou` · `incerteza` (sabia mais ou menos, hesitou) · `desatencao` (sabia e escorregou na leitura/marcação) · `errou` (não sabia). Separar `desatencao` de `errou` importa porque o tratamento é oposto: desatenção pede ritual de execução (rotular V/F, reler o comando), erro pede conteúdo.
