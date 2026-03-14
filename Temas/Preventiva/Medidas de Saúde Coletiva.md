# Medidas de Saúde Coletiva

### Principais tópicos
- Indicadores de morbidade (50,44%)
- Indicadores de mortalidade (33,33%)
- Indicadores demográficos (7,33%)
- Outros (8,90%)

---

# Indicadores de morbidade
- Morbidade = doença, ou seja: medidas que contabilizam as doenças e/ou agravos à saúde na população
    - Morbidade geral: todos os indivíduos que estão doentes, independente da causa, naquela localidade e período
    - Morbidade específica: podemos contar os casos novos (incidência) ou os casos já existentes (prevalência)
- Coeficiente de morbidade geral = número de pessoas doentes / número de habitantes
    - Exemplo: em uma cidade com 100.000 habitantes, 5.000 estão doentes. O coeficiente de morbidade geral é 5.000 / 100.000 = 0,05 ou 5%.
    - Não informa o risco de adoecimento, apenas informa a fração que está doente no local, independentemente da causa.
- Coeficiente de morbidade específica pode ser mensurada pela incidência (adicionados) e pela prevalência (existentes)

---

### Incidência
- Incidência = número de casos novos / número de habitantes em risco
    - Verifica quantos indivíduos mudaram seu status de saudáveis para doentes em relação ao total de indivíduos expostos ao adoecimento
    - **= risco absoluto** (probabilidade de um indivíduo contrair a doença naquela localidade)
    - Exige avaliação em **dois momentos distintos** na linha do tempo (excluir quem já tem o desfecho no início, acompanhar os sadios)
    - Tipos de incidência:
        - **Incidência acumulada** = calculada para populações **estáticas**; informa o risco médio de adoecer durante um intervalo de tempo (o tempo delimita o período, mas não entra no denominador)
        - **Densidade de incidência** = calculada para populações **dinâmicas**; conta perdas de seguimento (migração, óbito, cura, etc.)
            - Denominador = **tempo-pessoa** (soma do tempo em que cada indivíduo ficou exposto ao risco)
            - Informa a **velocidade de propagação** da doença no grupo — expressa em unidade de tempo (ex.: casos/pessoa-dia)
            - Não informa o risco individual de adoecimento
        - **Coeficiente de ataque** = incidência acumulada quando o fenômeno é um surto | casos novos / indivíduos susceptíveis × 100
            - Exemplo: em um casamento com 100 convidados, 20 comeram bolo e 10 adoeceram. Coeficiente de ataque = 10/20 = 50%.

---

### Prevalência
- Prevalência = número de casos existentes / número de habitantes em determinado momento
    - Contabiliza todos os casos existentes, sem distinção de novos ou antigos
    - É uma análise **pontual** — não afere risco
    - **Prevalência de período** = prevalência pontual + incidência no período
        - Se dividirmos pela metade do período, teremos a proporção de prevalência do período
    - Fatores que influenciam a prevalência: P = (↑1 + ↑2) − (↓3 + ↓4 + ↓5)
        - 1 — Incidência da doença: quanto maior, maior a prevalência
        - 2 — Imigração de doentes: quanto maior, maior a prevalência
        - 3 — Número de curados / percentual de cura: quanto maior, menor a prevalência
        - 4 — Número de óbitos / letalidade: quanto maior, menor a prevalência
        - 5 — Emigração de doentes: quanto maior, menor a prevalência
    - Prevalência de doenças crônicas
        - Doença crônica não tem cura → decai apenas por letalidade + emigração → prevalência mais elevada
        - Estratégias que aumentam sobrevida, mas não curam → aumentam ainda mais a prevalência
        - A incidência permanece inalterada nesse cenário

---

### Incidência × Prevalência
- Prevalência = Incidência × Duração da doença (P = I × D)
    - Alta incidência + curta duração = baixa prevalência (ex.: resfriado)
    - Baixa incidência + longa duração = alta prevalência (ex.: HIV)
- Usos:
    - **Incidência** → estudos etiológicos, morbidade em situações agudas, doenças de curta duração
    - **Prevalência** → planejamento em saúde, dimensionamento de recursos, doenças crônicas

> ⚠️ **Armadilha de prova — prevalência vs incidência:**
> Pesquisador colhe 3 hemoculturas com intervalo de 1 hora, no mesmo dia de admissão. Que medida obtém?
> **Prevalência.** As 3 coletas no mesmo dia aumentam a sensibilidade do exame (hemocultura tem baixa sensibilidade individual), mas representam **um único ponto** na linha do tempo. Para medir incidência, seria necessário avaliar o paciente em dois momentos distintos — excluindo bacteremia na admissão e acompanhando para ver casos novos.

---

### Risco Absoluto, Relativo e Atribuível

- **Risco absoluto (RA)** = a própria incidência; probabilidade de adoecer em uma população específica
    - Ex.: 10 casos em 20 idosos → RA = 50%
- **Risco relativo (RR)** = Incidência nos expostos / Incidência nos não expostos
    - RR = 1 → sem associação; RR > 1 → fator de risco; RR < 1 → fator protetor
- **Risco atribuível (diferença de riscos)** = Incidência nos expostos − Incidência nos não expostos
    - Fração da incidência atribuível exclusivamente à exposição

---

### Índices × Indicadores

- **Indicador** → medida que expressa a frequência de um evento de saúde
    - Pode ser expresso como proporção (incidência acumulada) **ou** por unidade de tempo (densidade de incidência)
    - Pode ser calculado a partir de números brutos
- **Índice** → sintetiza em **uma única medida** várias dimensões de um mesmo parâmetro
    - Exemplos: Índice de Apgar (FC, respiração, tônus, reflexos, cor), Escala de Glasgow, Índice de Vulnerabilidade Social

> ⚠️ Apgar é um **índice**, não um indicador — reúne múltiplas dimensões em uma medida final combinada.

---

### Valores Preditivos e Prevalência

- **VPP (Valor Preditivo Positivo):** probabilidade de teste positivo realmente indicar doença
- **VPN (Valor Preditivo Negativo):** probabilidade de teste negativo realmente indicar ausência de doença
- **A variável mais importante para os valores preditivos é a prevalência** (probabilidade pré-teste)
    - ↑ Prevalência → ↑ VPP · ↓ VPN
    - ↓ Prevalência → ↓ VPP · ↑ VPN
- Sensibilidade e especificidade são propriedades **intrínsecas** do teste — fixadas pelo ponto de corte, **não mudam com a população**
    - Influenciam os valores preditivos, mas de forma constante; a prevalência tem maior impacto por ser mutável
- Razão de verossimilhança: **não** influencia diretamente os valores preditivos

---

### Tipos de Estudo Epidemiológico

#### Os 4 eixos de classificação

- **Tipo de dado:** individual · agregado
- **Posição do pesquisador:** observacional · experimental
- **Estratégia de observação:** transversal · longitudinal
- **Direção temporal:** prospectivo · retrospectivo

#### Tipo de dado

- **Individual** → coleta de cada participante separadamente
    - Pista de prova: *"todos os indivíduos foram avaliados..."*, *"ninguém tinha a doença no início..."*
    - Exemplos: Transversal, Coorte, Caso-controle, Ensaios
- **Agregado** → dados de grupos (cidade, estado, país), não de cada pessoa
    - Pista de prova: taxas/prevalências de municípios, estados, países
    - Exemplos: Estudo ecológico, Intervenção comunitária

#### Posição do pesquisador

- **Observacional** → não interfere na exposição; apenas observa
    - Exemplos: Transversal, Ecológico, Coorte, Caso-controle
    - Comum em estudos de fator de risco/etiologia (impor exposições seria antiético)
- **Experimental** → define e oferece a intervenção/exposição
    - Exemplos: Ensaio clínico, Ensaio de campo, Ensaio comunitário

#### Estratégia de observação

- **Transversal ("fotografia 📷")** → avalia em um único momento → mede **prevalência**
    - Exemplos: Estudo transversal, Ecológico
- **Longitudinal ("filme 🎬")** → acompanha ao longo do tempo → mede **incidência** (exceto caso-controle)
    - Exemplos: Coorte, Caso-controle, Experimentais

#### Direção temporal (estudos longitudinais)

- **Prospectivo** → presente → futuro → pode medir incidência
    - Exemplos: Coorte prospectiva, Ensaios
- **Retrospectivo** → usa dados do passado
    - Exemplos: Caso-controle, Coorte histórica
    - ⚠️ **Caso-controle** é retrospectivo e **não mede incidência**
    - ⚠️ **Coorte retrospectiva** usa dados passados, mas **pode medir incidência** (lógica exposição → desfecho se mantém)

#### Principais desenhos epidemiológicos

- **Estudo Transversal**
    - Observacional · dados individuais · único momento
    - ✅ Mede prevalência | ❌ Fraco para causalidade (temporalidade incerta)

- **Estudo de Coorte**
    - Observacional · longitudinal · dividido por **exposição** (expostos vs não expostos)
    - Sem desfecho no início → acompanha para ver quem desenvolve a doença
    - ✅ Mede incidência | ✅ Calcula RR | ✅ Bom para etiologia e temporalidade
    - Pistas de prova: *"seguida por X anos"*, *"ninguém apresentava a doença no início"*, avalia fator de risco

- **Estudo Caso-controle**
    - Observacional · longitudinal · **retrospectivo** · dividido por **desfecho** (casos vs controles)
    - Investiga exposição passada dos grupos
    - ✅ Medida típica: OR | ❌ Não mede incidência | ❌ Não calcula RR diretamente
    - 🎯 Ideal para doenças raras e desfechos com longa latência

- **Estudo Ecológico**
    - Observacional · dados agregados · geralmente transversal
    - ✅ Útil para gerar hipóteses
    - ⚠️ Limitação: **falácia ecológica** (não se pode inferir comportamento individual a partir de dado populacional)

- **Estudos Experimentais**
    - Pesquisador define a intervenção/exposição
    - Ensaio clínico (pacientes) · Ensaio de campo (saudáveis, ex.: vacinas) · Ensaio comunitário (grupos)
    - ✅ Mede incidência | ✅ Calcula RR | ✅ Forte evidência para causalidade (especialmente com randomização)

#### Macete: Coorte vs Caso-controle

- **Coorte** → começa pela **exposição** → "expostos vs não expostos" → acompanha desfecho → mede **incidência** → calcula **RR**
- **Caso-controle** → começa pelo **desfecho** → "casos vs controles" → busca exposição passada → não mede incidência → calcula **OR**

#### Medidas por tipo de estudo

- **Prevalência** → Transversal
- **Incidência** → Coorte, Experimentais, Coorte retrospectiva
- **RR** → Coorte, Experimental
- **OR** → Caso-controle

---

# Indicadores de Mortalidade

Indicadores de mortalidade medem a frequência com que ocorrem óbitos em uma população. Diferem dos de morbidade por tratarem do "desfecho final", sendo essenciais para o planejamento de saúde e análise de gravidade.

- **Coeficiente Geral de Mortalidade (CGM):** Mede o risco total de morte na população (`Nº total de óbitos / População residente x 1.000`).
    - **Nuance:** É influenciado pela **estrutura etária**. Populações mais idosas (ex: Europa) podem ter CGM alto sem que isso signifique piores condições de saúde. Para comparar regiões, é necessário **padronizar por idade**.

- **Padronização de Coeficientes:**
    - **Método Direto**: Populações grandes; aplica as taxas de mortalidade da população local a uma população "padrão" (teórica).
    - **Método Indireto:** Usado para **populações pequenas** (onde as taxas locais são instáveis). Aplica-se a taxa da população "padrão" à população local observada para calcular a Razão de Mortalidade Padronizada (RMP).

> ⚠️ **Padrão de prova — comparação inter-regional:** Para comparar mortalidade entre estados/municípios com estruturas etárias diferentes → usar **taxa padronizada/ajustada por idade**. A taxa bruta é confundida pela estrutura etária (país desenvolvido = taxa bruta maior pela idade avançada).

---

- **Mortalidade Específica:** Mede o risco em subgrupos (por idade, gênero ou causa).
    - **Por Causa:** O denominador é a **população sob risco** de contrair a doença, não a população doente.
    - **Regra de Gênero:** Para doenças como câncer de ovário ou próstata, o denominador deve ser restrito ao gênero específico.

> ⚠️ **Padrão de prova — denominador da mortalidade específica:** Se a questão fornece apenas a população total do município (sem separar homens e mulheres) e pede o coeficiente por CA de colo de útero → resposta = **impossível calcular**. O denominador correto é o número de mulheres do município, não a população total.

## Letalidade vs. Mortalidade

- **Letalidade:** Mede a **gravidade/agressividade** da doença (`Nº de óbitos pela doença / Nº de casos confirmados da mesma doença x 100`).
    - Informa o risco de morrer **uma vez que se está doente**.
    - **Nuance:** Testagem em massa reduz a letalidade (aumenta o denominador com casos leves/assintomáticos).
- **Mortalidade Específica por Causa:** Mede o risco de morrer pela doença na **população saudável**. Envolve a probabilidade de adoecer e, então, morrer.

## Mortalidade Proporcional

Informa a **contribuição** (peso) de uma característica no total de óbitos. **Não mede risco**.
- **Mortalidade Proporcional por Causa:** Qual o % de mortes por causas circulatórias no total de óbitos?
- **Pizza de 100%:** Se uma causa diminui sua proporção (ex: infecciosas), outra obrigatoriamente aumenta seu peso relativo, mesmo que o risco real (mortalidade específica) não tenha mudado.

### Índices Especiais (Proporcionalidade por Idade)
- **Índice de Swaroop-Uemura (ISU):** Porcentagem de óbitos em indivíduos com **50 anos ou mais** sobre o total de óbitos.
    - **ISU ≥ 75%:** Elevado nível de saúde (países desenvolvidos).

> ⚠️ **Padrão de prova — ISU é proporção:** ISU = óbitos em ≥50 anos / total de óbitos × 100. O numerador é subconjunto do denominador → **proporção** (não taxa, não coeficiente). Taxa teria como denominador a população em risco (vivos), não subconjunto dos próprios óbitos.

- **Curvas de Nelson Moraes (Curvas de Mortalidade Proporcional):**
    - **Tipo I (N ou "J" invertido):** Nível de saúde **muito baixo** (muita morte infantil, pouca em idosos).
    - **Tipo II (L ou "U"):** Nível de saúde **baixo**.
    - **Tipo III (V ou "U" invertido):** Nível de saúde **regular**.
    - **Tipo IV (J):** Nível de saúde **bom** (maioria dos óbitos em idosos).

## Anos Potenciais de Vida Perdidos (APVP)

- **Definição:** Indicador que quantifica o impacto das mortes prematuras, somando os anos que cada indivíduo "deixou de viver" até uma idade de referência (geralmente 65-70 anos).
    - Fórmula: APVP = Σ (idade de referência − idade do óbito), para cada óbito ocorrido antes da idade de referência
    - Quanto mais jovem o óbito, **maior** o APVP individual
- **Para que serve:** Identificar doenças e causas que afetam **preferencialmente jovens** — independentemente do volume absoluto de mortes
    - Alta mortalidade proporcional por uma causa ≠ alto APVP (causa pode matar muitos, mas em idosos)
    - APVP alto = causa que rouba anos de vida = prioritária para políticas de saúde
- **No Brasil:** Causas externas (homicídios, acidentes) têm altíssimo APVP por atingirem jovens
- **Diferença-chave:**

> ⚠️ **Padrão de prova — APVP vs Proporcional:**
> - APVP alto + Mortalidade Proporcional baixa = Causa que atinge **JOVENS** (ex: Causas Externas).
> - APVP baixo + Mortalidade Proporcional alta = Causa que atinge **IDOSOS** (ex: Doenças Cardiovasculares).

---

## Causa Básica da Morte e a Declaração de Óbito

- **Declaração de Óbito (DO)** — Parte I: cadeia causal direta
    - **Linha a:** Causa imediata/terminal — o que o paciente morreu no momento final (ex: EAP, PCR)
    - **Linha b/c:** Causas intermediárias — consequências da causa básica
    - **Linha d:** **Causa básica** — a doença que INICIOU toda a cadeia de eventos
- **Parte II:** Condições contribuintes — não fazem parte da cadeia direta mas contribuíram para o óbito

### Causa Básica
- É a causa que orienta **políticas de prevenção** — o ponto onde intervir evita toda a cadeia
- Selecionada pela **Regra de Seleção da CID-10** para fins estatísticos
- Exemplos:
    - Eclampsia → EAP → óbito: **causa básica = eclampsia**
    - Tabagismo → DPOC → IRA → óbito: **causa básica = tabagismo**
    - HAS → AVC → pneumonia aspirativa → óbito: **causa básica = HAS**

> ⚠️ **Padrão de prova — causa básica vs imediata:** O examinador descreve um caso com desfecho terminal grave (EAP, PCR, sepse) e pergunta a causa básica. A resposta é sempre o evento INICIAL da cadeia, não o evento final. "O que matou" ≠ "causa básica".

---

## Morbimortalidade Materna e Infantil

### Mortalidade Materna - cai muito pouco
Morte durante a gestação ou até **42 dias** após o parto por causas ligadas à gravidez (exceto causas acidentais).
- **Razão de Mortalidade Materna (RMM):** `(Óbitos Maternos / Nascidos Vivos) x 100.000`.
- **Tendência no Brasil:** A queda desacelerou recentemente. **Causa:** Estratégia de redução de óbitos por causa mal definida (investigação ativa de óbitos em mulheres em idade fértil). Melhora na notificação "aumenta" o numerador e mascara a queda real.
- **Near Miss Materno:** Mulher que quase morreu (teve falência orgânica), mas sobreviveu. É um indicador de qualidade do pré-natal e emergência.
- **Causas no Brasil:** 1. Hipertensão (Eclâmpsia/Pré-eclâmpsia); 2. Hemorragia; 3. Infecção Puerperal.
- **Mortalidade Materna Tardia:** Ocorre entre o **43º e 365º dia** pós-parto.

### Mortalidade Infantil - despenca nas provas
- **Evolução:** Redução universal em todas as 27 UFs do Brasil (atingiu metas do milênio).
- **Componentes:**
    - **Pós-Neonatal (28 dias a < 1 ano):** Foi o componente que apresentou a **maior redução** histórica (melhora de saneamento, vacinas, aleitamento).
    - **Neonatal Precoce (0-6 dias):** Mais frequente no Brasil atual; reflete causas biológicas e assistência ao parto.
- **Saúde da Criança na APS:**
    - Consultas de puericultura: devem ser intercaladas entre médico e enfermeiro (mesmo no baixo risco).
    - Coordenação do Cuidado: A APS nunca abandona a criança, mesmo se houver acompanhamento especializado de alto risco.

### Mortalidade em Escolares (5-9 anos)
- **Ranking das causas (ordem decrescente):**
    1. Causas Externas (líder absoluto após 1 ano de idade).
    2. Neoplasias (tumores).
    3. Doenças do Sistema Nervoso.

# Indicadores Demográficos

- **Taxa de Fecundidade:** `Nascidos vivos / Mulheres de 15 a 49 anos`. É o melhor indicador para analisar a dinâmica de crescimento, pois independe da estrutura etária.
- **Razão de Dependência:** `(Menores de 15 anos + Idosos ≥ 60 anos) / Adultos (15 a 59 anos)`.
- **Esperança de Vida ao Nascer:** Média de anos que se espera viver. No Brasil, as mulheres vivem ~7 anos a mais que os homens (fenômeno da **sobremortalidade masculina** por causas externas em jovens).
- **IDH (Indicador ÉPICO):** **E**scolaridade + **P**IB (renda) + **E**xpectativa de vida (**C**ondução).

# Transições em Saúde

## Transição Demográfica
Mudança de altos coeficientes de natalidade/mortalidade para coeficientes baixos.
- **Fase 1:** Natalidade e Mortalidade altas (Crescimento lento).
- **Fase 2 (Explosão):** Queda da Mortalidade, Natalidade continua alta.
- **Fase 3 (Envelhecimento):** Queda da Natalidade (Convergência). **Brasil está aqui**.
- **Fase 4:** Estabilização em níveis baixos.

> 🔴 **Armadilha de Prova — Morbimortalidade no Trânsito:**
> A morbi-mortalidade por acidentes é **inversamente proporcional ao nível de desenvolvimento econômico**. Países pobres/renda média morrem mais apesar de terem frotas menores (falta de segurança veicular e infraestrutura).

## Transição Epidemiológica
Mudança no padrão de doenças: Infecciosas (DIP) dando lugar a Crônicas (DCNT) e Causas Externas.
- **Brasil (Transição Polarizada e Prolongada):** Não completamos o ciclo. Vivemos uma **Tripla Carga de Doenças**:
    1.  DCNT (Circulatórias e Neoplasias - principais causas de morte).
    2.  Causas Externas (Homicídios/Acidentes - principal causa em jovens).
    3.  Agenda não concluída de Infecciosas/Parasitárias (Dengue, Tuberculose, Hanseníase).

## Análise do Perfil Brasileiro
- **Mortalidade Proporcional (Ranking):** 1. Aparelho Circulatório; 2. Neoplasias; 3. Aparelho Respiratório; 4. Causas Externas.
- **Causas Externas:** Em questões, se unificados os acidentes, eles superam as agressões. Porém, se separados, as **agressões** (homicídios) costumam ocupar o 1º lugar.

# Indicadores Demográficos

⭐ **Esperança ou Expectativa de Vida ao Nascer**
- **Definição**: Número esperado de anos a serem vividos por uma coorte (grupo que nasce no mesmo ano).
- **Cálculo**: Baseado na média de idade com que a população morre naquele ano.
- **Brasil (Dados 2019/2020)**:
    - Média nacional: **76,6 anos**.
    - Mulheres vivem ~7 anos a mais que homens (80,1 vs 73,1).
    - Diferença Regional: SC (~80 anos) vs MA (~71 anos).
- ⚠️ **Independe da estrutura etária**: Pode ser usado para comparar regiões sem padronização.
- 🔴 **Sobremortalidade Masculina**: Principal causa entre 15-25 anos são as **Causas Externas**, o que reduz a esperança de vida dos homens.

**Taxas de Fecundidade**
- **Taxa de Fecundidade Geral (TFG)**: Média de nascidos vivos por mulheres em idade fértil (15-49 anos).
    - ⚠️ **Pegadinha**: O denominador é apenas mulheres de 15-49 anos, NÃO a população total.
- **Taxa de Fecundidade Total (TFT)**: Somatório das taxas específicas por idade. É o indicador mais acurado (não precisa padronizar).
- **Brasil**: Em queda franca (1,76 filhos por mulher em 2015).

**Crescimento Populacional**
- **Crescimento Absoluto (Demográfico)**: (Nascimentos + Imigrações) - (Óbitos + Emigrações).
- **Crescimento Vegetativo**: Nascimentos - Óbitos (desconsidera fluxos migratórios).

**Estrutura Etária e Indicadores de Envelhecimento**
- **Pirâmides Etárias**:
    - **Base Larga + Ápice Estreito**: População jovem (baixa mediana de idade).
    - **Estreitamento da Base + Alargamento do Ápice**: Envelhecimento populacional (aumento da mediana).
- **Índice de Envelhecimento**: (Idosos ≥ 60 anos / Jovens < 15 anos) x 100.
    - ⭐ **Destaque UNIFESP**: Banca que mais cobra este indicador.
- **Razão de Dependência**: (Populares < 15 anos + Idosos ≥ 60 anos) / População de 15-59 anos (PEA).
    - Reflete o encargo econômico sobre a parcela produtiva. No Brasil, tende a aumentar pelo crescimento da parcela idosa.

# Indicadores Socioeconômicos

⭐ **IDH (Índice de Desenvolvimento Humano)**
- Mnemônico: **O IDH É ÉPICO!**
    - **E**xpectativa de Vida (Longevidade).
    - **E**scolaridade (Educação).
    - **P** renda **I** **C**apita (**O** PIB per capita).
- Varia de 0 a 1 (1 é o melhor).

**IVS (Índice de Vulnerabilidade Social)**
- Mede a ausência/insuficiência de ativos que deveriam ser providos pelo Estado.
- **Dimensões**: Infraestrutura Urbana, Capital Humano e Renda/Trabalho.
- Varia de 0 a 1 (1 é a vulnerabilidade máxima).
- ⚠️ **Relação com IDH**: Inversamente proporcional.

# Transições em Saúde

**Transição Demográfica**
- Passagem de altos coeficientes de mortalidade e natalidade para valores reduzidos.
- **Fases (Medronho)**:
    - **Fase 1 (Pré-transicional)**: Natalidade e Mortalidade altas (crescimento lento).
    - **Fase 2 (Explosão Demográfica)**: Queda rápida da mortalidade (especialmente infantil), natalidade continua alta.
    - **Fase 3 (Convergência)**: Natalidade começa a cair rápido. Inicia o envelhecimento populacional.
    - **Fase 4 (Estabilização)**: Novo equilíbrio com taxas baixas. Pirâmide em forma de "Urna".
- 🔴 **Brasil**: Transição acelerada. Atualmente na Fase 3 (convergência), caminhando para a 4.

**Transição Epidemiológica (Omran)**
- Substituição de Doenças Infectoparasitárias (DIP) por Doenças Crônicas Não Transmissíveis (DCNT) e Causas Externas.
- 🔴 **Brasil: Transição Polarizada Prolongada**:
    - **Tripla Carga de Doenças**: Coexistência de DIP, DCNT e Causas Externas.
    - **Contratransição**: Retrocessos com reemergência de doenças (ex: Sarampo, Febre Amarela).

# Perfil de Saúde no Brasil (Atualizado)

**Mortalidade Proporcional por Grupos (Ranking)**
1. **1º Aparelho Circulatório** (~27%).
    - ⭐ Principal causa absoluta: **IAM** (1º) e **AVE** (2º).
2. **2º Neoplasias** (~17%).
3. **3º Aparelho Respiratório** (~12%).
4. **4º Causas Externas** (~10,5%).

**Causas Externas**
- Ranking: **1º Agressões** > 2º Acidentes de Transporte > 3º Quedas/Traumatismos.
- Perfil: Afeta majoritariamente **homens jovens (15-39 anos)**. É a principal causa de morte em adolescentes.

**Mortalidade Infantil**
- Coeficiente de Mortalidade Infantil (CMI) no Brasil: ~11,9 por 1.000 NV (2019).
- **Componente Prevalente**: **Neonatal Precoce** (0-6 dias), refletindo problemas na assistência ao pré-natal e parto.
- Redução mais acelerada ocorreu no Nordeste (Alagoas foi destaque).

**Mortalidade Materna**
- Razão de Mortalidade Materna (RMM): ~59,1 por 100 mil NV (2018). Limite OMS é 20.
- **Causas Principais**: **Hipertensão** (1ª), Hemorragias, Infecção Puerperal e Aborto.
- ⚠️ **Falha na Redução**: Devido à má qualidade do pré-natal/parto, excesso de cesarianas (Brasil 45-55%) e ilegalidade do aborto.

**Atenção à Saúde**
- O sistema brasileiro é **Fragmentado e Reativo** (foco em agudos).
- Solução: **Redes de Atenção à Saúde (RAS)** com a **APS** como coordenadora e ordenadora do cuidado, visando o acompanhamento longitudinal das doenças crônicas.
