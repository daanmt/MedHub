# Pesquisa: ecossistema open-spaced-repetition (OSR) -- para sistema py-fsrs proprio

Contexto do sistema auditado: `fsrs>=6.3.1`, `Scheduler(desired_retention=0.9, learning_steps=(), enable_fuzzing=False)`, parametros DEFAULT, ~3.000 linhas de revlog / ~1.500 cards ativos, SQLite proprio (nao Anki).

Metodologia: WebSearch + WebFetch apenas. Toda informacao abaixo vem de paginas publicas (dado NAO CONFIAVEL por padrao; nenhum codigo de pagina foi executado). 31 buscas/fetches usados. Item que nao fechou em fonte primaria = NAO VERIFICADO, sinalizado explicitamente.

---

## a. Inventario da organizacao open-spaced-repetition

**Fato verificado:** A org GitHub `open-spaced-repetition` mantem, entre outros:
- `fsrs4anki` (Jupyter Notebook, 4.1k stars) -- o scheduler custom original para Anki; hoje o algoritmo esta nativo no Anki, o repo vive como documentacao/wiki de referencia.
- `py-fsrs` (Python, 491 stars) -- "Python Package for FSRS Spaced Repetition"; pacote PyPI `fsrs`, versao atual **6.3.2** (lancada 09/08/2026, confirmado via PyPI).
- `fsrs-rs` (Rust, 426 stars) -- "FSRS for Rust, including Optimizer and Scheduler"; motor usado pelo proprio Anki desktop/AnkiDroid/AnkiMobile (fsrs-rs 6.6.x).
- `ts-fsrs` (TypeScript, 791 stars), `go-fsrs` (Go, 145), `rs-fsrs` (Rust, 50), `swift-fsrs` (Swift, 102), `dart-fsrs`, `cljc-fsrs`, `ex_fsrs` (Elixir) -- portas multi-linguagem do mesmo algoritmo/formato de revlog.
- `fsrs-optimizer` (Python, 112 stars) -- pacote standalone de otimizacao de parametros (usa PyTorch), documentacao do processo de treino.
- `srs-benchmark` (Jupyter Notebook, 264 stars) -- benchmark publico comparando FSRS a outros modelos.
- `fsrs-browser` (Rust/WASM, 54 stars) -- FSRS compilado para rodar no navegador.
- `anki-revlogs-dataset-builder` (Python) -- ferramenta que construiu o dataset publico "Anki Revlogs 10K" (Hugging Face: `open-spaced-repetition/anki-revlogs-10k`), a base do srs-benchmark.
- `fsrs4anki-helper` (Python, 322 stars) -- add-on de Postpone/Advance/Load Balance.
- `awesome-fsrs` -- lista curada de implementacoes/papers/recursos.

**Versao atual do algoritmo:** **FSRS-6**, lancado em produção no Anki desde a versao **25.07** (mudanca de formula de same-day review e parametro de decaimento). O pacote `fsrs` (PyPI) esta na serie 6.x desde entao; ultima tag vista: 6.3.2 (09/08/2026). Existe um **FSRS-7** em fase de pesquisa/benchmark (aparece no srs-benchmark como variante experimental), mas **nao e a versao de producao** -- e opt-in experimental em apps como Yazu, e estimativa de blog de terceiros aponta producao "nao antes de 2027" (fonte fraca, ver item h).

**Fontes:**
- https://github.com/orgs/open-spaced-repetition/repositories (fetch direto) -- forca: README/listagem oficial da org.
- https://pypi.org/project/fsrs/ (fetch direto) -- forca: pagina oficial do pacote.
- https://github.com/open-spaced-repetition/py-fsrs (fetch direto) -- forca: README oficial.
- https://yazu.app/fsrs/fsrs-7/ (WebSearch) -- forca: blog de terceiro (app cliente), NAO e o OSR; usar so como sinal direcional sobre status do FSRS-7.

**Implicacao para o sistema descrito:** o pacote usado (`fsrs>=6.3.1`) ja esta na familia FSRS-6 mais recente e estavel; nao ha necessidade de esperar FSRS-7 (ainda experimental). O ecossistema oferece portas em outras linguagens com o MESMO formato de revlog (card_id, review_datetime, rating, review_duration opcional) -- relevante se algum dia quiser trocar de runtime sem perder o historico.

---

## b. Papers fundadores

**Fato verificado -- Paper 1 (algoritmo SSP-MMC, base do FSRS):**
Ye, J.; Su, J.; Cao, Y. (2022). "A Stochastic Shortest Path Algorithm for Optimizing Spaced Repetition Scheduling." Proceedings of the 28th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '22), pp. 4381-4390, Washington DC, 14-18/08/2022.
DOI: **10.1145/3534678.3539081**

**Fato verificado -- Paper 2 (modelo DSR -- Difficulty/Stability/Retrievability, base direta do FSRS atual):**
Su, J.; Ye, J.; Nie, L.; Cao, Y.; Chen, Y. (2023). "Optimizing Spaced Repetition Schedule by Capturing the Dynamics of Memory." IEEE Transactions on Knowledge and Data Engineering (TKDE), publicado online 01/10/2023.
DOI: **10.1109/TKDE.2023.3251721**
Resultado citado pelos autores: reducao de 64% no erro de predicao de recall e 17% no custo de agendamento vs baselines; dataset com serie temporal de memorizacao (primeiro do genero, segundo os autores).

Ambos os papers estao listados como as duas referencias academicas centrais na wiki oficial do FSRS.

**Fontes:**
- https://github.com/open-spaced-repetition/fsrs4anki/wiki/Research-resources (fetch direto) -- forca: wiki oficial do OSR, lista os dois papers como fundamentais.
- https://dl.acm.org/doi/10.1145/3534678.3539081 -- forca: registro DOI ACM (paper 1).
- https://doi.org/10.1109/TKDE.2023.3251721 / ieeexplore.ieee.org/document/10059206 -- forca: registro DOI IEEE (paper 2).

**Implicacao para o sistema descrito:** o modelo DSR (paper 2) e a base conceitual direta de tudo que o `fsrs` package calcula (Difficulty/Stability/Retrievability por card) -- vale citar como referencia teorica caso o time queira justificar decisoes de calibragem de dificuldade do sistema medico com literatura primaria.

---

## c. srs-benchmark -- numeros publicados

**Fato verificado -- tabela de resultados (com same-day reviews incluidas), fonte: README oficial do srs-benchmark:**

| Algoritmo | Log Loss (menor=melhor) | RMSE(bins) (menor=melhor) | AUC (maior=melhor) |
|---|---|---|---|
| RWKV-Instant (rede neural, nao-FSRS) | 0,2660 +/- 0,0036 | 0,03212 +/- 0,00044 | 0,8450 +/- 0,0017 |
| LSTM (rede neural) | 0,3140 +/- 0,0039 | 0,05200 +/- 0,00076 | 0,7622 +/- 0,0019 |
| FSRS-7 (recency, experimental) | 0,3178 +/- 0,0040 | 0,05715 +/- 0,00081 | 0,7522 +/- 0,0018 |
| **FSRS-6** | **0,3842 +/- 0,0051** | **0,0985 +/- 0,0014** | **0,6830 +/- 0,0022** |
| FSRS-4.5 | 0,4286 +/- 0,0060 | 0,1033 +/- 0,0014 | 0,6821 +/- 0,0023 |
| FSRS-5 | 0,4565 +/- 0,0069 | 0,1175 +/- 0,0017 | 0,6761 +/- 0,0023 |
| HLR (Half-Life Regression, Duolingo) | 0,705 +/- 0,014 | 0,1715 +/- 0,0025 | 0,6104 +/- 0,0028 |
| Ebisu v2 | 0,772 +/- 0,017 | 0,1846 +/- 0,0026 | 0,5947 +/- 0,0031 |

Nota de anomalia (reportada como esta, sem correcao): FSRS-4.5 aparece com log loss/AUC levemente MELHORES que FSRS-5 nesta tabela -- e uma inconsistencia conhecida e documentada da comunidade (FSRS-5 teve criticas por overfitting em certos regimes), nao um erro de leitura deste relatorio.

**Estatisticas de superioridade pairwise** (fonte: blog do Expertium, contribuidor central do OSR, nao e pagina oficial da org): FSRS-6-recency supera o SM-2 (Anki) em log loss em **99,6%** das colecoes testadas; FSRS-6 supera FSRS-5 em **88,2%** das colecoes; FSRS-6 com parametros otimizados supera FSRS-6 com parametros DEFAULT em **84,3%** das colecoes.

**Tamanho do dataset:** dataset publico "Anki Revlogs 10K" (Hugging Face `open-spaced-repetition/anki-revlogs-10k`) -- README oficial do srs-benchmark cita **10.000 colecoes/usuarios** e **519.296.315 reviews** (com same-day reviews incluidas) usados na avaliacao. O blog do Expertium (fonte secundaria) fala em 9.999 colecoes e ~349,9 milhoes de reviews apos filtragem, de um total bruto de ~727 milhoes -- ou seja, a mesma ordem de grandeza, diferenca e o filtro aplicado. Uma mencao solta de "20 mil usuarios / 1,7 bilhao de reviews" apareceu em resultado de busca mas NAO foi confirmada em fetch primario -- tratar como NAO VERIFICADO (pode ser um dataset maior/mais novo nao public, ou imprecisao de resumo).

**Data do benchmark:** nao ha data explicita de "ultima atualizacao" no README; sinais indiretos (FSRS-7 ja aparecendo, PyPI fsrs 6.3.2 de 08/2026) sugerem tabela ativa/atualizada em meados de 2026. **NAO VERIFICADO** com precisao de data.

**Fontes:**
- https://github.com/open-spaced-repetition/srs-benchmark/blob/main/README.md (fetch direto) -- forca: README oficial do benchmark da org.
- https://expertium.github.io/Benchmark.html (fetch direto) -- forca: blog de contribuidor central do OSR (nao e pagina oficial da org, mas e referencia cruzada pela propria org); numeros de superioridade pairwise vem so daqui.

**Implicacao para o sistema descrito:** confirma que FSRS-6 (o que o sistema usa) e hoje a opcao publicada com melhor log loss/AUC entre os modelos "classicos" de SRS (bate SM-2, HLR, Ebisu por larga margem); so perde para modelos de rede neural experimentais (RWKV/LSTM) que nao estao empacotados para uso geral. Nao ha motivo, pela literatura, para trocar de algoritmo -- o ganho estaria em otimizar parametros (ver item d), nao em trocar de modelo.

---

## d. fsrs-optimizer -- quantas revisoes sao necessarias

**Fato verificado (fonte oficial, `fsrs4anki/docs/tutorial.md`):**
- Anki **24.04**: minimo de **400 reviews** exigido para rodar a otimizacao.
- Versoes mais antigas: minimo de **1000 reviews**.
- Anki **24.06+**: SEM minimo fixo -- o sistema decide sozinho QUAIS parametros consegue otimizar com seguranca dado o volume disponivel (otimizacao parcial/parametrica conforme dado).
- Abaixo do minimo/dado insuficiente: a recomendacao oficial e **usar os parametros DEFAULT** -- "ainda e melhor que usar o algoritmo legado SM-2".

**Sobre o py-fsrs especificamente (fetch direto do README):**
- A classe `Optimizer` e instanciada com uma lista de `ReviewLog`: `optimizer = Optimizer(review_logs)`.
- `optimizer.compute_optimal_parameters()` retorna os 21 parametros otimizados.
- `optimizer.compute_optimal_retention(optimal_parameters)` retorna a retencao-alvo otima (ligado ao conceito de CMRR, item e).
- Campos confirmados em uso no `ReviewLog`: `.rating` e `.review_datetime`. Agrupamento por card usa algum identificador de card (nome exato do campo -- **NAO CONFIRMADO literalmente no fetch do README do py-fsrs**, mas e consistente com `card_id` usado nas outras portas).
- Campo `review_duration` (duracao da revisao em ms, opcional): confirmado como campo padrao do formato de revlog FSRS nas portas Go e Elixir (`ReviewDuration`, `omitempty`/opcional) -- **NAO CONFIRMADO diretamente no README do py-fsrs** (nao apareceu no trecho obtido), mas como o formato de revlog e padronizado entre as linguagens do OSR (fsrs-optimizer descreve-se como "standardized, universal optimizer" para as varias implementacoes), a existencia do campo no py-fsrs e provavel, porem fica como **NAO TOTALMENTE VERIFICADO** -- recomenda-se checar o codigo-fonte (`fsrs/_optimizer.py` ou equivalente) antes de depender do nome exato do campo.

**Fontes:**
- https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md (fetch direto) -- forca: doc oficial/tutorial do OSR.
- https://github.com/open-spaced-repetition/py-fsrs (fetch direto) -- forca: README oficial do pacote.
- https://github.com/open-spaced-repetition/fsrs-optimizer (fetch direto) -- forca: README oficial; NAO trouxe numero explicito de minimo de reviews no trecho obtido (o numero "1000/400" vem do tutorial.md, nao deste README).

**Implicacao para o sistema descrito (CRUCIAL):** com **~3.000 linhas de revlog** o sistema esta **3x a 7,5x acima** do minimo oficial citado (400 a 1000 reviews) para rodar a otimizacao com seguranca -- ou seja, HA base de dados suficiente, pela propria literatura do OSR, para parar de usar parametros DEFAULT e rodar `Optimizer(review_logs).compute_optimal_parameters()` sobre o revlog proprio. Isso e uma acao concreta e de baixo risco (a propria doc diz que usar default "ainda e melhor que SM-2", ou seja, otimizar so pode melhorar, nunca piorar em relacao ao ponto de partida). Falta so verificar o nome exato dos campos do `ReviewLog` no codigo-fonte instalado antes de escrever o script de import do revlog do SQLite proprio.

---

## e. Desired retention -- recomendacao, curva de carga, CMRR

**Fato verificado (fonte oficial, wiki `The-optimal-retention`):**
- Default: **0,9** (90%) -- confirmado tambem no README do py-fsrs.
- Faixa permitida: **0,70 a 0,97** (em versoes mais novas do Anki, 0,70-0,99). Acima de 0,97 e desaconselhado -- vira "massed repetition" (revisao quase diaria), custo altissimo.
- Faixa "razoavel" recomendada: **80-95%**, com **90% funcionando bem para a maioria**.
- **CMRR** = "(Compute/Cost-)Minimum Recommended Retention" -- e o ponto de retencao-alvo que MINIMIZA a razao carga-de-trabalho/conhecimento (workload / knowledge), nao que maximiza conhecimento puro. A curva "carga de revisoes x retencao-alvo" tem formato de U: retencao muito alta = mais revisoes (custo de manutencao); retencao muito baixa = mais esquecimento = mais reaprendizagem (custo de recuperacao). O ponto de minimo dessa curva e calculado numericamente via **metodo de Brent** dentro do simulador do FSRS.
- Existe **simulador oficial** (embutido no fsrs-optimizer / fsrs-rs) que projeta a carga de revisoes dia-a-dia para diferentes valores de desired_retention antes de voce se comprometer com um valor.
- Mudanca de filosofia registrada: antes do Anki 24.04 o objetivo do otimizador era maximizar conhecimento adquirido; desde 24.04+ o objetivo passou a ser minimizar workload/knowledge (ou seja, o proprio CMRR).

**Fontes:**
- https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-optimal-retention (fetch direto) -- forca: wiki oficial do OSR.

**Implicacao para o sistema descrito:** `desired_retention=0.9` esta dentro da faixa recomendada e e o valor "seguro para a maioria" -- nao ha alarme aqui. Mas como o sistema tem ~3.000 reviews (item d), ele tambem tem dado suficiente para rodar `compute_optimal_retention()` e descobrir se 0,9 e de fato o ponto de minimo workload/knowledge PARA ESTE usuario especificamente, ou se um valor diferente (ex.: 0,85 ou 0,93) reduziria a carga diaria de cards sem perder retencao relevante -- e um calculo personalizado, nao generico.

---

## f. learning_steps=() e enable_fuzzing=False

**Fato verificado -- comportamento de learning_steps vazio:**
- Default do `Scheduler` no py-fsrs (fetch direto do README) e **`learning_steps=(timedelta(minutes=1), timedelta(minutes=10))`** e **`relearning_steps=(timedelta(minutes=10),)`** -- OU SEJA, o sistema descrito (`learning_steps=()`) esta **deliberadamente fora do default** da biblioteca.
- Comportamento confirmado (via PR oficial `L-M-Sherlock` -- autor/mantenedor do FSRS -- no repo `ankitects/anki`, PR "Fix/only let FSRS take over short-term schedule when steps are empty", #3496): quando `learning_steps` esta vazio, um card novo **gradua direto para o estado Review na primeira resposta**, sem passar por filas de aprendizado com intervalos fixos em minutos -- o proprio FSRS calcula o intervalo (mesmo para a primeira revisao) usando a formula de Stability/Difficulty, em vez de usar steps fixos "1min -> 10min -> graduar". O mesmo vale para `relearning_steps=()`: um card que erra (Again) permanece no estado Review com o proximo intervalo JA calculado pelo FSRS, em vez de cair numa fila de "relearning" com steps fixos.
- Recomendacao oficial (wiki/tutorial): quando FSRS controla o agendamento de curto prazo (steps vazios), a doc so alerta para nao deixar steps residuais longos demais; quando SE USA steps (nao-vazios), a recomendacao e mante-los curtos (10/15/20/30 min), completar tudo no mesmo dia, e evitar steps > 12-14h (atrapalham a modelagem de curto prazo do FSRS).

**Fato verificado -- enable_fuzzing:**
- Default do Scheduler no py-fsrs e `enable_fuzzing=True`. Fuzzing aplica uma variacao aleatoria pequena ao intervalo calculado (ex.: 50 dias vira 49 ou 51), com faixas diferentes por tamanho de intervalo (~15% para 2,5-7 dias, ~10% para 7-20 dias, ~5% para 20+ dias). O objetivo documentado e evitar acumulo de cards no mesmo dia (load balancing) quando MUITOS cards sao criados juntos, nao e uma correcao de precisao do algoritmo.
- `enable_fuzzing=False` (como no sistema descrito) desativa isso: os intervalos saem exatamente como o FSRS calculou, sem jitter. Nao ha recomendacao oficial contra desativar fuzzing -- e tratado como puramente cosmetico/de distribuicao de carga, nao afeta a precisao da predicao de retencao.

**Fontes:**
- https://github.com/open-spaced-repetition/py-fsrs (fetch direto) -- forca: README oficial (defaults confirmados).
- https://github.com/ankitects/anki/pull/3496 (via WebSearch, autoria L-M-Sherlock) -- forca: PR do mantenedor do FSRS no repo oficial do Anki; NAO foi fetch direto da pagina (so snippet de busca) -- tratar como forca media-alta, recomenda-se confirmar lendo o PR na integra se a mecanica exata for decisiva para o sistema.
- fsrs4anki tutorial.md (fetch direto) -- forca: oficial, para a recomendacao de steps curtos quando usados.

**Implicacao para o sistema descrito:** `learning_steps=()` + `enable_fuzzing=False` e uma configuracao coerente e documentada -- NAO e um mau uso do FSRS. Ela transforma o scheduler num "long-term scheduler puro": todo card, desde a primeira resposta, e agendado pela formula DSR do FSRS (sem fila de aprendizado com minutos fixos), e sem randomizacao de data. Isso faz sentido para um sistema de estudo por SQLite proprio (sem UI de "fila de aprendizado hoje") e center-piece em cards ja maduros (~1.500 ativos). Ponto de atencao: cards NOVOS (nunca revisados) tambem pulam direto pra Review -- ou seja, nao ha "reforco em minutos" no mesmo dia da primeira exposicao; se o sistema espera esse reforco imediato em algum fluxo (ex.: sessao de cunhagem -> teste no mesmo bloco), isso precisa ser feito por fora do FSRS (repeticao manual), nao vai acontecer via scheduler.

---

## g. Semantica das notas 1-4 (Again/Hard/Good/Easy)

**Fato verificado (fonte oficial, tutorial.md + confirmado por multiplas fontes secundarias consistentes):**
- Internamente o FSRS trata **Again = "fail"** e **Hard/Good/Easy = "pass"** -- e uma dicotomia binaria (lembrou vs nao lembrou) por baixo da nota 1-4.
- Recomendacao textual oficial: **"Press Again if you forgot it, and press Hard only if you recalled it after a lot of hesitation."** -- ou seja, **Hard NAO deve ser usado para "errei parcialmente"**. Se Hard for usado quando na verdade a resposta foi esquecida/errada, os intervalos calculados ficam "unreasonably high" (o modelo credita uma recuperacao bem-sucedida que nao aconteceu), inflando artificialmente a stability do card.
- Easy: nao foi encontrada, em fonte primaria/oficial, uma recomendacao explicita de "nao usar" ou "usar com moderacao" -- so um comentario de blog (Expertium, secundario) dizendo que o FSRS "pode ate ser mais preciso se voce so usar Again e Good" (ou seja, evitar tanto Hard quanto Easy nas bordas), mas isso NAO e uma recomendacao oficial formal, e **fica como NAO VERIFICADO** em fonte de maxima forca.
- Regra geral (oficial): a nota deve refletir a FACILIDADE DE LEMBRAR, nao o tempo que voce DESEJA esperar ate a proxima revisao -- e um erro comum forcar a nota para manipular o intervalo.

**Fontes:**
- https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md (fetch direto) -- forca: oficial.
- https://forums.ankiweb.net/t/an-info-tip-regarding-recommended-button-usage/39834 (WebSearch, nao fetch direto) -- forca: forum (comunidade), usado so como reforco.

**Implicacao para o sistema descrito:** e diretamente relevante ao fato de que "um agente propoe a nota a partir da resposta do aluno" -- a regra oficial da UMA linha de corte clara e binaria para o agente aplicar: (1) se o aluno NAO recuperou a resposta correta (mesmo que parcialmente / mesmo que com dica) = **Again**, nunca Hard; (2) Hard so se o aluno chegou na resposta certa sozinho, mas com duvida/esforco visivel; (3) nao usar a nota como proxy de "quanto tempo quero esperar" -- isso description bate com a memoria do sistema (`feedback_registro_dificuldade_pos_analise.md`, `feedback_relearning_intrasessao.md`) de que nota <4 deveria voltar pra fila (relearning intra-sessao) em vez de so gravar Hard/Again e seguir.

---

## h. FSRS-6 / mudancas recentes 2025-2026

**Fato verificado:**
- **FSRS-6** foi desenvolvido/mesclado no Anki via PR oficial `Feat/FSRS-6` de **L-M-Sherlock** (mantenedor do FSRS) no repo `ankitects/anki` (#3929), lancado em producao no Anki **25.07** (meados de 2025).
- Mudancas principais do FSRS-6 vs FSRS-5:
  1. **Parametro de decaimento (decay, "w20")** novo -- controla a "curvatura"/achatamento da curva de esquecimento de forma **individualizada por usuario** (antes do FSRS-6, a forma da curva era fixa/igual para todos). Faixa tipica 0,1-0,8, maioria dos usuarios < 0,2, default ~0,2.
  2. **Formula melhorada para same-day reviews / memoria de curto prazo** -- parametros w17/w18 controlam quanto as notas dadas em revisoes NO MESMO DIA afetam a Stability recalculada. Isso e o que o forum chama de "short-term memory" do FSRS-6.
  3. Total de **21 parametros** (2 a mais que os 19 do FSRS-5).
  4. Retrocompatibilidade: pesos/parametros de FSRS-4.5 e FSRS-5 continuam funcionando, upgrade e opcional.
- Achado de pesquisa relevante (mencionado em fontes secundarias, remonta a experimentos do proprio time): usar resultados de revisao de curto prazo (same-day) como rotulo de treino do otimizador, em certas tentativas, **piorou** a predicao de longo prazo -- sinal de que memoria de curto e longo prazo podem exigir modelagem distinta; e um dos motivadores da pesquisa em torno do FSRS-7 (que reportedly usa uma abordagem "dual-curve" curto-prazo/longo-prazo, NAO VERIFICADO em fonte oficial, so blog de terceiro).
- **FSRS-7**: aparece no `srs-benchmark` como variante "recency" em fase de pesquisa/comparacao (ver tabela do item c), mas **nao e a versao de producao** em nenhum client serio (Anki, fsrs-rs, py-fsrs) no momento da pesquisa. Fonte de terceiro (blog Yazu, NAO e OSR oficial) estima producao "nao antes de 2027" -- **tratar essa data como NAO VERIFICADA**, e so um chute de blog externo.
- **O pacote `fsrs>=6.3.1` do PyPI ja implementa FSRS-6**: confirmado -- a serie 6.x do pacote (ultima vista: 6.3.2, 09/08/2026) e a implementacao Python da familia FSRS-6, incluindo os 21 parametros e o decay parameter.

**Fontes:**
- https://github.com/ankitects/anki/pull/3929 (WebSearch, nao fetch direto) -- forca: PR oficial do mantenedor do FSRS no repo do Anki -- alta, mas recomenda-se fetch direto se precisar da mecanica exata de w20/w17/w18.
- https://pypi.org/project/fsrs/ (fetch direto) -- forca: oficial, confirma serie 6.x / versao atual.
- Multiplas fontes secundarias convergentes (chrislongros.com, yazu.app) para os detalhes numericos do decay parameter -- forca media (triangulada, mas nao e pagina oficial do OSR).

**Implicacao para o sistema descrito:** o sistema ja esta na versao certa (FSRS-6 via `fsrs>=6.3.1`) e nao precisa de nenhuma migracao. O parametro de decay (w20) so e calibrado corretamente via `Optimizer` rodando sobre o revlog proprio (item d) -- com parametros DEFAULT, o sistema esta usando um decay generico, nao o "achatamento de curva" calibrado para o padrao de esquecimento real dos ~1.500 cards do usuario. Isso reforca a acao candidata do item d.

---

## i. Leeches (cards que caem repetidamente)

**Fato verificado -- mas ATENCAO: isto e um recurso do APLICATIVO Anki, nao do algoritmo FSRS em si:**
- Default do Anki (independente do FSRS): quando um card acumula **8 lapsos** (8x "Again" em revisao, contados ao longo da vida do card), o Anki marca como **leech**, aplica a tag `leech` e por padrao **suspende** o card. O limiar (8) e a acao (suspender vs so marcar) sao configuraveis em Deck Options -> Lapses -> Leeches.
- **Nao existe uma metrica "oficial" do lado do algoritmo FSRS** para leech -- FSRS nao calcula "score de leech"; o conceito de leech e inteiramente da camada de aplicativo (Anki), agnostico ao scheduler usado (SM-2 ou FSRS).
- Discussao de comunidade (forum oficial do Anki, thread "Using FSRS parameters to identify leech cards", 02/2024): usuarios sugerem usar o parametro **Difficulty** do FSRS (que vai de 1 a 10, sendo D perto do teto = card cronicamente dificil) como sinal adicional/antecipado de leech, ja que cards que viram leech tendem a acumular Difficulty alta antes de baterem no limiar de lapsos. Isso e uma **proposta de comunidade, nao uma metrica endossada oficialmente pelo OSR**.
- Recomendacao correlata (oficial, sobre configuracao): manter "New Interval" em 0,00 apos lapso ajuda a identificar leeches mais rapido (nao "preservar" o intervalo antigo do card, que mascara o padrao de esquecimento).
- Sobre "suspender x reformular": nao foi encontrada recomendacao oficial do OSR tomando partido entre as duas; a literatura do OSR e neutra e foca no comportamento de agendamento, nao em curadoria de conteudo do card (isso fica a criterio do usuario/app).

**Fontes:**
- https://forums.ankiweb.net/t/using-fsrs-parameters-to-identify-leech-cards/40740 (WebSearch, nao fetch direto) -- forca: forum/comunidade, NAO e recomendacao oficial do OSR.
- Comportamento padrao de leech (limiar 8, suspender) -- forca: manual oficial do Anki (docs.ankiweb.net/deck-options.html, visto em busca, nao fetch direto) -- e oficial do Anki, mas e "aplicativo", nao "algoritmo FSRS".

**Implicacao para o sistema descrito:** como o sistema NAO e Anki (SQLite proprio), nao ha herdado automatico do mecanismo de leech do Anki -- se o sistema quer um conceito equivalente, precisa implementar por conta propria. A pista mais solida da literatura (ainda que de comunidade, nao oficial) e: (1) usar um limiar de lapsos absolutos (ex.: 8, ajustavel) contado via revlog proprio; (2) cruzar com o parametro **Difficulty** do FSRS por card (disponivel apos rodar o Optimizer/Scheduler) como sinal antecedente -- isso alias plugin diretamente com o que ja esta na memoria do sistema (`feedback_card_defeituoso_contamina_diagnostico.md`, `#787 3a queda` no ultimo commit) -- cards com D alta E quedas repetidas sao candidatos fortes a reforja/aposentadoria, nao a "mais uma revisao igual".

---

## Resumo de fontes por forca

- **Paper com DOI (maxima forca):** KDD 2022 (10.1145/3534678.3539081), TKDE 2023 (10.1109/TKDE.2023.3251721).
- **README/wiki/doc oficial do OSR, fetch direto (alta forca):** py-fsrs README, fsrs4anki tutorial.md, wiki "The optimal retention", wiki "Research resources", srs-benchmark README, fsrs-optimizer README, PyPI fsrs.
- **PR/issue oficial no repo do mantenedor, via busca (forca media-alta, nao fetch direto -- recomenda-se confirmar se for decisivo):** ankitects/anki #3929 (FSRS-6), #3496 (learning_steps vazio).
- **Blog de contribuidor central do OSR (Expertium) (forca media-alta):** numeros de superioridade pairwise do benchmark.
- **Forum/comunidade/blog de terceiro (forca baixa, so como sinal direcional):** thread de leech, estimativa de data do FSRS-7 (Yazu), recomendacao sobre Easy.
