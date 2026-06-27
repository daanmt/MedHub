---
type: roadmap
layer: root
status: decided
relates_to: [ESTADO, AGENTE, reconcile-contract]
---

# S094 — Ultraplan: Cronograma Comprimido + Sistema de Sync + Governança

**Data-base:** 2026-06-27 · **ENAMED:** 2026-09-13 · **Autor:** scrum master / arquiteto-chefe
**Insumos:** Projeto A (cronograma comprimido), Projeto B (arquitetura de sync), Projeto C (governança).
**Veredito-síntese:** os três são adotáveis, mas o Projeto A contém um **erro de horizonte** que infla a viabilidade (corrigido na §a); B e C **convergem** numa mesma arquitetura com nomes diferentes (unificada na §c). A decisão estratégica central (meta 12000 vs recalibrar) é um **fork do usuário** — exposta na §f.

---

## a. Diagnóstico — matemática do cronograma e gap de meta

### a.1 Números confirmados contra a fonte (não estimados)

Rodei os três insumos contra `crono_dados.json` (parse real do PDF) e contra `ipub.db`:

- **Cronograma S11–S28 = 6689 questões / 222 tasks / 18 semanas.** ✔ Bate exatamente com o CONTEXTO e com o Projeto A (todas as 18 semanas conferem questão a questão).
- **Estado real (DB, hoje):** 3986 questões acumuladas · 79,8% de acerto geral · faltam 8014 para ENAMED 12000.
- **Áreas fracas (DB ao vivo):** Hepato 57% (14q) · Dermato 67% (24q) · Cardiologia 67% (79q) · Otorrino 68% (19q) · Hemato 72% (57q). Gaps absolutos: **Ortopedia, Oftalmo** (0q). ✔ Bate com o CONTEXTO.

### a.2 🔴 ERRO DE HORIZONTE no Projeto A (corrigido)

O Projeto A construiu **toda** a aritmética sobre **98 dias úteis** e **fator de compressão 1,29×**. Isso está **errado para a sprint**:

- O Projeto A mede até a **formatura (~14 semanas)**. Mas a sprint declarada é **FOCO TOTAL ENAMED até 13/09**.
- De hoje (27/06) até ENAMED há **78–79 dias**, não 98. São **~11,1 semanas-calendário**, não 14.
- Logo o fator de compressão **para a prova** é **18 ÷ 11,1 = 1,62×**, não 1,29×. O Projeto A mediu a compressão até a formatura e a vendeu como se fosse até a prova.

**Consequência direta (recalculado para o horizonte real de 79 dias):**

- **Cronograma "puro" a 7 dias/sem = 84,7 q/dia** (não 68,3). O número baixo do Projeto A só existe porque ele diluiu 6689q em 98 dias; mas S25–S28 (1507q) caem **depois** da prova. Diluído nos 79 dias reais, o ritmo do cronograma sobe.
- **Para 12000 até ENAMED = 101 q/dia sustentados, 79 dias seguidos, sem zerar um dia.** (`performance.py` já reporta exatamente ~101q/dia — está correto; o Projeto A é que destoou.)
- A 6 dias/sem (≈68 dias úteis): cronograma = **98 q/dia**; meta-ENAMED = **118 q/dia**.

### a.3 🔴 ERRO CONCEITUAL do "gap real ≈ 4400q" (corrigido)

O Projeto A escreveu: "no aproveitamento histórico (54%), o cronograma rende ~3612q efetivas → gap real ≈ 4400q." **Isso mistura duas grandezas diferentes:**

- A meta 12000 conta **`questoes_feitas` (volume bruto)** — é o que `sessoes_bulk` registra. Não conta acertos.
- O "54%" do S10 (147 de 273 disponíveis) é **taxa de execução do cronograma** (quantas das questões ofertadas foram feitas), e o "79,8%" é a **taxa de acerto**. Nenhum dos dois desconta do volume-meta.
- Portanto **não existe** um "gap real de 4400q por causa do aproveitamento". O 54% não reduz o 12000 — ele reduz **quanto do cronograma você cobre**, o que é um problema de *cobertura de conteúdo*, não de *contagem para a meta*.

**O gap honesto, então, é duplo e deve ser nomeado separado:**

1. **Gap de volume (para a meta 12000):** mesmo fazendo 100% do cronograma, `3986 + 6689 = 10675 < 12000` → **faltam 1325q** de banco extra além do cronograma. Real, confirmado.
2. **Gap de execução (cobertura de conteúdo):** se só ~54% do cronograma é efetivamente feito (padrão S10), você cobre ~3600q de conteúdo planejado e **deixa metade do cronograma sem tocar** — o que é grave para *aprender*, mas é ortogonal ao número 12000.

### a.4 Cenários de acúmulo até ENAMED (79 dias, ritmo sustentado)

- 60 q/dia → **8 726** (73% de 12000) — piso
- 70 q/dia → **9 516** (79%)
- 80 q/dia → **10 306** (86%)
- 90 q/dia → **11 096** (92%)
- 100 q/dia → **11 886** (99%) — encosta na meta
- 120 q/dia → **13 466** (112%) — teto improvável de sustentar 79 dias

**Leitura honesta:** 12000 até a prova exige **~101 q/dia TODO dia por 79 dias** — acima da meta histórica de ≥100 e muito acima do ritmo realizado em junho (816q em 26 dias ≈ **31 q/dia**). O mês corrente está a **128 q/dia necessários** só para fechar a meta de junho (déficit 514q em 4 dias) — sinal de que o ritmo real ainda não chegou nem perto do alvo.

> ⚠️ **Fragilidade estatística das áreas fracas:** Hepato "57%" são 14q; Otorrino "68%" são 19q; Dermato "67%" são 24q. São amostras minúsculas — o percentual é ruído. O sinal acionável NÃO é "estude porque está em 57%", é "**tem volume quase zero**" (Hepato, Otorrino, Dermato, + os zeros Ortopedia/Oftalmo). Tratar como **gaps de volume**, não como buracos de proficiência medida.

---

## b. Cronograma comprimido recomendado

### b.1 Princípio: a meta governa, não o cronograma

O cronograma puro (84,7 q/dia) **não chega** a 12000. O plano é construído pela **meta + áreas-zero**, com o cronograma como espinha de conteúdo. Três eixos:

### b.2 Split pré/pós-ENAMED (front-load)

- **Pré-ENAMED (até 13/09 ≈ S11–~S23/S24):** tudo que tem densidade de prova. ~11 content-weeks reais cabem antes da prova sob compressão 1,62×.
- **Pós-ENAMED (S24/S25–S28, rumo à formatura/UERJ/USP):** **1507q** que podem escorregar sem prejuízo de ENAMED — Leucemias(rev) S25, Cirrose(rev) S26, **Fraturas/Luxações/Quadril Pediátrico S28**, e parte das `Revisão`/`Revisão por Questões` de S25–S27.
- **🔴 Antecipar para antes da prova:** **FA/Flutter (S27) e PCR** — arritmia é alto-rendimento ENAMED e está tarde demais. Puxar para a janela pré-prova (encaixar como bloco extra de Cardiologia em ~S18–S21).

### b.3 Compressão de tempo-por-questão (não cortar tema — regra s088)

Caber 18→11 semanas **sem cortar tema** depende de comprimir o *tempo de estudo por questão*, calibrado pelo `tipo` da task (validado s092):

- `Teoria + Exercícios` (bloco novo denso) → **aula descomprimida** (escada de degraus, mecanismo > fato).
- `Revisão` / `Revisão por Questões` → **refresh comprimido** (só gatilhos + armadilhas; rendeu 86% no S10).
- Tasks de baixo peso (sub-temas <20q, IVAS isolado) → **lote de questões + 1 card-âncora**, sem resumo novo.

### b.4 Banco extra obrigatório — onde moram os +q além do cronograma

Os ~1325q de gap de volume (mínimo) **devem** ir prioritariamente para os buracos que o cronograma **não cobre**:

- 🔴 **Oftalmo (0q)** — bloco mínimo ~30q (olho vermelho, glaucoma agudo, trauma ocular). Altíssimo custo-benefício por ser zero.
- 🔴 **Otorrino** — bloco dedicado ~50q (otite, sinusite, vertigem); cronograma só toca como IVAS.
- 🔴 **Dermato** — ~60q distribuídas S14–S18; cronograma cobre raso/tarde (S14 rev, S27).
- 🔴 **Ortopedia (0q)** — Trauma (S21) é pré-prova OK; Fraturas/Luxações (S28) aceita adiar pós-ENAMED. Bloco extra ~40q de trauma se sobrar banco.
- **Hepato** (a mais fraca, 14q) — reforço +40q em S13/S19 já cobertos pelo cronograma.
- Resto do banco extra → **simulados mistos** para hábito de prova.

Prioridade do banco extra pré-prova: **Oftalmo(30) + Otorrino(50) + Dermato(60) + Hepato(40) = ~180q** dirigidas; o excedente em simulado.

### b.5 Maior alavanca de compressão

Jogar **os ~1507q de S25–S28 + as revisões duplicadas para pós-ENAMED** é a maior alavanca isolada — libera a janela pré-prova para densidade de prova + banco extra dos buracos.

---

## c. Arquitetura do sistema de sync (B e C unificados)

Os Projetos B e C descrevem **o mesmo sistema com vocabulário divergente**. Unifico aqui e marco onde divergem.

### c.1 Convergências (ambos concordam — adotar)

- **Cronograma NÃO persiste no `ipub.db`** (decisão s075). Zero INSERT/UPDATE no db originado do plano.
- **Camada derivada versionável** (JSON fora do db) + **CLIs read-only** que cruzam com SSOTs em tempo de leitura — exatamente como `review_radar.py` deriva temperatura sem persistir.
- **Um único derivador** (`tools/cronograma*.py`) detém todo o parse + lógica de gap; `day_plan.py`/`performance.py` **consomem**, não reparseiam. (Risco R4 de C / R4 de B — duplo parser.)
- **Linchpin = normalização de área:** o PDF usa nomes longos (`Hepatologia`, `Gastroenterologia`, `Oftalmologia`…), o DB usa curtos (`Hepato`, `Gastro`, `Oftalmo`…). O JOIN cronograma↔`sessoes_bulk` depende de um mapa `AREA_PDF_TO_CANON`. **Este é o coração técnico do sync.**
- **Acoplamento frouxo por DATA, não por task-id.** `sessoes_bulk` registra por *área*, não por sub-task; o usuário faz ~54% e foge da ordem. Amarrar 1:1 task→sessão geraria drift permanente. Progresso = `SELECT SUM(questoes_feitas) WHERE data BETWEEN inicio_semana AND fim_semana`, agregado por área.
- **🔴 NÃO escrever em `taxonomia_cronograma`.** Confirmado ao vivo: é tabela de *desempenho por tema* (107 linhas, `UNIQUE(area,tema) = ux_taxonomia_area_tema`), alimentada só por `insert_questao.py`. Tasks (que carregam `tipo` e repetem o mesmo tema em várias semanas: HAS em S12/S15/S18) **nunca** viram linhas de taxonomia — ou o UNIQUE rejeita (perda silenciosa) ou alguém sufixa `"HAS (Rev) S15"` e explode a cardinalidade, desfazendo a dedup s083 e furando o resolver `(area,tema)` de `insert_questao`/`insert_card_base`. O elo cronograma↔desempenho é **em memória** (join por nome, fuzzy), nunca por escrita.

### c.2 Divergências entre B e C (decididas aqui)

| Ponto | Projeto B | Projeto C | **Decisão** |
|---|---|---|---|
| **Fonte SSOT** | `Cronograma.pdf` (raiz) | `Cronograma de Reta Final.xlsx` (Drive) vence; PDF é fallback | **PDF da raiz é a fonte v1.0** (offline, já parseado, determinístico). O xlsx do Drive é fonte futura — reconciliar os dois é **fora de escopo v1.0** (risco R8 de C). Evita dependência de MCP no boot. |
| **Artefato derivado: commitar?** | `grade.json` **versionado** (commit; diff legível) | `crono_dados.json` **cache descartável** gitignored | **Versionar** (Projeto B vence). A grade é estrutural (semana/área/tipo/contagem), sem texto clínico do EMED → seguro commitar, e o `git diff` quando o PDF muda é exatamente o valor de auditoria. Local: `core/cronograma/grade.json`. |
| **Nome do derivador** | `cronograma_lib.py` + `cronograma_radar.py` + `cronograma_extract.py` (3 arquivos) | `tools/cronograma.py` (1 arquivo) | **Começar com 1 (`tools/cronograma.py`)** com subcomandos (`--rebuild`/`--check`/`--gap`/`--json`/`--radar`); extrair lib/radar como módulos só se crescer. Menos superfície, menos contratos de skill. |
| **`crono_dados.json` é canônico?** | promover a `grade.json` | é cache | **Promover** o shape de `crono_dados.json` a `grade.json` adicionando `area_norm`, datas inicio/fim de semana, e `_meta` (sha256 + mtime do PDF). |

### c.3 Schema canônico de `core/cronograma/grade.json`

Promove o shape real de `crono_dados.json` (já validado: 18 semanas, `total_questoes`/`questoes_por_lista`/`tasks[]`) acrescentando o que falta para o sync:

- `_meta`: `fonte`, `fonte_sha256`, `fonte_mtime`, `extraido_em`, `semana_1_inicio` (âncora de datas), `total_questoes`, `n_semanas`.
- Por semana: `inicio`/`fim` (derivadas da âncora + ordinal — **não** do ano da string, que tem typo "25" na planilha — risco R6 de C), `total_questoes`, `tasks[]`.
- Por task: `area_pdf` (verbatim, auditoria), **`area_norm`** (canônico — a chave de JOIN), `tema`, `tipo` (verbatim) + `tipo_norm` ∈ `{teoria, revisao, revisao_questoes}` (calibra a aula por bloco).

### c.4 Mapa de normalização (o linchpin) + limpeza de rótulos sujos

`AREA_PDF_TO_CANON` (constante única em `tools/cronograma.py`): `Hepatologia→Hepato`, `Gastroenterologia→Gastro`, `Hematologia→Hemato`, `Oftalmologia→Oftalmo`, `Pneumologia→Pneumo`, `Reumatologia→Reumato`, `Infectologia→Infecto`, `Otorrinolaringologia→Otorrino`, `Dermatologia→Dermato`, `Medicina Preventiva→Preventiva`, etc. (identidade para os que já batem).

🔴 **Achado ao vivo (confirma W4 do reconcile):** `sessoes_bulk` tem rótulos sujos — `Obstetr�cia` (mojibake, 277q) e `GO` (30q, 90%) coexistindo com `Ginecologia`+`Obstetrícia`. O derivador **normaliza na leitura** (`mojibake→Obstetrícia`; `GO`→sinalizar, split não-trivial), emite **WARNING**, e **não** toca o db. A migração que limpa o db de fato é destrutiva sobre SSOT → fica fora do v1.0 (fork — ver §f).

> Nota factual: o Projeto B disse que `cronograma_progresso` é "tabela vazia/legada". **Ela não existe no schema atual** (confirmado: `no such table`). Nenhuma ação — só registro para não procurá-la.

### c.5 Tracking de progresso (view computada, zero duplicação)

`progresso_semana(con, grade, semana)` responde, on-read: `feitas_total / alvo_total (%)`, `por_area` (feitas vs alvo rateado `total_questoes/n_tasks`), e `areas_previstas_nao_tocadas`. Sem tabela nova, sem INSERT. O rateio igual por task é aproximação honesta v1.0 (o PDF não amarra `questoes_por_lista[i]` ↔ `tasks[i]` de forma garantida — alinhamento exato é v1.1, depende de validação empírica da ordem).

---

## d. Integração e governança

### d.1 Boot — dentro do passo 4, sem passo novo (B e C concordam)

O cronograma entra **dentro do §2 passo 4** (Plano do Dia), substituindo o `_cronograma_hint()` atual — que faz regex no `## Próximos passos` do `ESTADO.md` e pega a 1ª linha numerada (frágil, prosa-dependente, não sabe semana/déficit). O `day_plan.py` passa a importar `cronograma.py` (como já importa `dormant_refresh`/`performance`) e renderiza:

- semana corrente (ordinal vs hoje) · q previstas vs feitas na semana · próximo tema · **os dois ritmos-alvo** (cronograma ~85/dia vs ENAMED ~101/dia) nomeando o gap.
- linha de área-fraca-que-cai-agora (refresh pré-bloco) + linha "fora do cronograma no horizonte" (Otorrino/Oftalmo → banco extra).

**Nenhuma mudança no protocolo de boot** — só no que o passo 4 renderiza.

### d.2 Fechamento — gatilho de leitura condicional, sem escrita de cronograma

Fechamento **não** grava números de cronograma. Único write permitido: espelhar **1 ponteiro de texto** ("Semana corrente: SNN") em `ESTADO.md`/`HANDOFF.md` quando a semana vira. Regra dura: só estado real (`sessoes_bulk`) é gravado.

### d.3 Contrato novo: `core/contracts/cronograma-contract.md` v1.0 — **SIM**

Justificativa (C): há duas decisões graváveis que uma feature de cronograma viola silenciosamente (não-persistência + `UNIQUE(area,tema)`), uma fonte derivada nova sem ciclo de vida normatizado, e um fork estratégico (gap de meta) sem dono. Cláusulas: fonte/SSOT · derivação/cache · sync (read-on-demand, sem cron, Zero-DB no Cloud) · derivador único · **fronteiras duras** (🔴 zero write em `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log`; único write = ponteiro textual) · lente estratégica (dono do gap = fork) · calibração de aula por `tipo`. `relates_to: [reconcile, forgetting-curve, estado, AGENTE]`.

### d.4 Reconcile — novas condições WARNING (nunca BLOCKING)

Plano não é verdade-de-estado; divergência plano↔realidade é *informação de gestão*, não corrupção. Travar boot por estar atrasado seria hostil.

- **W5** — `grade.json` defasado vs `Cronograma.pdf` (sha256 difere) → `cronograma.py --check`; resolução = `--rebuild`.
- **W6** — semana atrás do ritmo, OU "Semana corrente" no ESTADO ≠ calculada por data → ajusta ponteiro textual.
- **W7 (fork estratégico, reporta UMA vez)** — gap de meta materializado (`acum + crono < 12000`). Reporta uma vez, registra a decisão do usuário em `ESTADO.md §Metas`, silencia até a premissa mudar (espelha o tratamento "uma-vez" do W3 do fsrs-management). **Resolução de W5–W7 NÃO grava no db.**

### d.5 Impacto nas skills existentes

- **`/performance`** (impacto médio, alto valor): bloco 6 "Cronograma vs Meta" — confronta oferta do cronograma (6689q) com déficit ENAMED (8014q) e anota, ao lado de cada área fraca, se o cronograma a cobre. Importa o número de `cronograma.py` (não reparseia). **Fechar pendência stale:** `ESTADO.md` ainda lista "corrigir ramp de metas" como pendência, mas `performance.py` **já tem** o ramp correto (3000→17000, confirmado ao ler o código) — a nota está obsoleta.
- **`/refrescar`** (impacto baixo, fronteira intacta): cronograma pode **desempatar** o radar de dormência a favor de um tema dormente que **também cai na semana corrente**. Só ordenação opt-in; a curva manda, o cronograma sugere. **NÃO toca FSRS.**
- **`/revisar`** (impacto baixo): filtro adicional para priorizar cards `--area`/`--tema` da semana corrente quando a fila comporta. Não muda política FSRS; cap `--new-limit 10` e "honestidade > generosidade" intactos.

### d.6 Riscos de governança herdados (de C, confirmados)

R1 persistir cronograma no db (ALTA, mitigação: fronteira dura) · R2 task→taxonomia quebra dedup s083 (ALTA, confirmado ao vivo, mitigação: join em memória) · R3 cache editado à mão (MÉDIA) · R4 duplo parser (MÉDIA, mitigação: derivador único) · R5 W6/W7 viram BLOCKING/ruído (MÉDIA) · R6 typo de ano na planilha (MÉDIA, mitigação: ordinal+âncora) · R8 PDF vs xlsx divergem (BAIXA, fora de escopo v1.0).

---

## e. Plano faseado de implementação (frente s094)

Ordenado por dependência. Esforço relativo: **P** (pequeno, <1 sessão), **M** (médio, ~1 sessão), **G** (grande, >1 sessão).

### Fase 0 — Decisão estratégica (BLOQUEIA tudo que é "meta") · esforço P
- **Entregável:** usuário responde as DECISÕES PENDENTES (§f), em especial meta 12000 vs recalibrar, e horas/dia + fim-de-semana.
- **Dependência:** nenhuma. **É pré-requisito de Fase 4** (o gap-meta precisa de dono antes de virar W7). As fases técnicas 1–3 **não** dependem disto e podem começar em paralelo.

### Fase 1 — Derivador + grade.json · esforço M
- **Entregáveis:** `tools/cronograma.py` (funde `crono_extract.py` + `cronograma_grade.py` do scratch: o 1º pega área+tipo+contagem, o 2º pega o nome do tema via regex `Tema (Tipo)`); `core/cronograma/grade.json` gerado e **commitado**; `AREA_PDF_TO_CANON`; subcomandos `--rebuild`/`--check`/`--json`/`--gap`/`--radar`.
- **Validação:** S10 = 273q contra o real; mapa de área cobre as 20 de `AREAS_VALIDAS`; `--check` detecta PDF trocado.
- **Dependência:** nenhuma (scratch já funciona).

### Fase 2 — Radar área-fraca × cobertura · esforço M
- **Entregáveis:** `cronograma.py --radar` (gêmeo do `review_radar.py`): cruza `performance.get_por_area()` × grade futura; flags 🔴 `FRACA_SEM_COBERTURA` / 🟡 tarde / 🟢 já / ⚪ gap. Normaliza rótulos sujos (`GO`/mojibake) na leitura com WARNING.
- **Validação:** Otorrino/Oftalmo saem como 🔴/⚪; Cardio/Hepato como 🟢.
- **Dependência:** Fase 1 (consome grade) + `performance.py` (reúso).

### Fase 3 — Integração no day_plan · esforço M
- **Entregáveis:** `day_plan.py` troca `_cronograma_hint()` (regex ESTADO) por `_cronograma_hoje()` (importa `cronograma.py`); renderiza semana + previsto/feito + **dois ritmos-alvo** + linha de banco-extra. Deprecar a leitura textual (risco R7).
- **Validação:** boot mostra "S11 · 412q · feitas 0/412 · cronograma 85/dia vs ENAMED 101/dia".
- **Dependência:** Fases 1–2.

### Fase 4 — Governança/contratos · esforço M
- **Entregáveis:** `core/contracts/cronograma-contract.md` v1.0 (7 cláusulas); patch `reconcile-contract.md` (+W5/W6/W7 + nota "arquivos alteráveis: cache regenerável, cronograma altera só ponteiro textual"); patch `AGENTE.md` (§2 passo 4 + §6 decisão + §7.4 CLI + §7.3 skill); skill `.claude/commands/cronograma.md` (assinatura canônica, contrato §7.2); patch `forgetting-curve-contract.md §Boot` (cronograma = 4ª fonte do day_plan); registrar a decisão da Fase 0 em `ESTADO.md §Metas`.
- **Dependência:** Fase 0 (W7 precisa do dono do fork) + Fases 1–3 (documenta o que existe).

### Fase 5 — Refinos opcionais (baixa prioridade) · esforço P cada
- **Entregáveis:** bloco 6 "Cronograma vs Meta" em `/performance`; tie-break de semana em `/refrescar`; filtro de semana em `/revisar`; fechar nota stale "ramp de metas" no `ESTADO.md`.
- **Dependência:** Fases 1–4. Não bloqueiam o uso diário.

> **Caminho crítico:** Fase 1 → 2 → 3 entrega o valor operacional (boot enriquecido) em ~2–3 sessões. Fase 4 formaliza. Fase 0 corre em paralelo mas trava só a parte de *meta* (W7 + recalibração), não o sync.

---

## f. DECISÕES PENDENTES (forks — só o usuário decide)

Listadas em ordem de impacto. As 3 primeiras são **bloqueantes** do plano de meta.

1. **Meta 12000 vs recalibrar.** 🔴 Fork central. Mesmo 100% do cronograma = 10675 (faltam 1325 de banco extra); 12000 exige **~101 q/dia por 79 dias seguidos**, vs ritmo real de junho ~31 q/dia. **Opções:** (a) manter 12000 como stretch e bater ≥101/dia; (b) **adotar ~10000 como meta-prova realista** (~62 q/dia para 9866) e tratar 12000 como teto; (c) gatilho automático — revisar em S13 (~12/07): se acúmulo <5200, descer para 10000; se ≥5600, manter 12000. **Recomendação: (b)+(c).**

2. **Quantas horas/dia reais disponíveis para questões?** Sem isso o ritmo-alvo é abstrato. ~101 q/dia exige bloco de estudo consistente — é factível na sua rotina atual? Defina o piso honesto (ex.: 80 q/dia) que você consegue **sustentar 79 dias**, não o teto de um dia bom.

3. **Fim de semana conta no ritmo?** O Projeto A oferece 7 dias (84,7 q/dia cronograma) vs 6 dias (98 q/dia). 6 dias deixa um dia de folga mas sobe o ritmo diário em ~16%. **Decida o calendário de trabalho** — muda todos os números do day_plan.

4. **Cortar Otorrino/Ortopedia/Oftalmo do sprint ENAMED, ou suplementar com banco extra?** Cobertura rasa/tardia/zero no cronograma. **Opções:** (a) banco extra dirigido pré-prova (~30/50/40q — recomendado para Oftalmo+Otorrino, alto custo-benefício por serem ~zero); (b) aceitar o gap e focar nas áreas de alto volume ENAMED; (c) Ortopedia: aceitar adiar Fraturas/Luxações (S28) para pós-prova. **Recomendação: suplementar Oftalmo+Otorrino+Dermato; adiar Ortopedia-S28.**

5. **Antecipar FA/Flutter/PCR (S27) para antes da prova?** Arritmia é alto-rendimento ENAMED e está agendada tarde demais (pós-prova efetivamente). **Recomendação: sim, puxar para ~S18–S21.** Confirma?

6. **Datas exatas de UERJ, USP e formatura.** Hoje só ENAMED (13/09) é firme. As outras provas e a formatura definem a janela pós-ENAMED (S25–S28) e o "2º ciclo 17000". **Fornecer as datas** para o day_plan calcular os marcos pós-prova.

7. **Limpeza dos rótulos sujos em `sessoes_bulk` (`GO` 30q, `Obstetr�cia` 277q).** É operação destrutiva sobre SSOT (W4 do reconcile). **Opções:** (a) v1.0 normaliza só na leitura (não-destrutivo, recomendado agora); (b) autorizar migração one-shot que limpa o db de fato (precisa do seu "go"). **Recomendação: (a) agora, agendar (b) à parte.**

8. **Fonte do cronograma: PDF da raiz (v1.0) ou xlsx do Drive?** v1.0 usa o PDF (offline, determinístico). O xlsx do Drive é editável por você (risca/recolore) mas exige MCP no boot e reconciliar dois números. **Recomendação: PDF v1.0; migrar para xlsx só se você passar a editar o plano você mesmo.** Confirma manter o PDF como fonte?

---

## g. Decisões tomadas (s093 — 2026-06-27)

Forks resolvidos pelo usuário — fecham as DECISÕES PENDENTES da §f:

1. **Meta:** 🎯 **10.000 + gatilho S13** (12/07: acúmulo ≥5.600 → volta a 12.000; <5.200 → confirma 10.000). 12.000 vira teto/stretch.
2. **Ritmo:** **ciclo 3 dias sprint + 1 folga + simulado dominical**; ~90-100q nos dias de conteúdo (3+1 a 100/dia → 10.086 no ENAMED; a 80/dia → 9.086, gatilho decide se força).
3. **Volume extra:** **14 simulados × 100q**, 1 por domingo (11 pré-ENAMED = 1.100q; 3 pós, rumo a UERJ/USP).
4. **Áreas órfãs (Oftalmo/Otorrino/Dermato/Ortopedia):** **focar no alto volume** — cobertas pelos simulados (mix), sem bloco dedicado.
5. **Arritmia (FA/Flutter/PCR):** **antecipar S27 → ~S18-S21.**
6. **Datas:** só ENAMED (13/09) firme; UERJ/USP/formatura a confirmar (definem a janela pós-prova).
7. **Rótulos sujos (`GO`/`Obstetrícia` mojibake):** **normalizar só na leitura** no v1.0; migração destrutiva = fork futuro.
8. **Fonte:** **PDF v1.0** (offline, determinístico); xlsx do Drive fora de escopo.

**Frente nova derivada 1:** **Sessão dedicada de Cirurgia** — varrer todo o eixo cirúrgico (resumos + PDFs de Ortop/Otorrino/outros já na pasta) e avaliar ajustes no cronograma dentro da margem/metas.

**Frente nova derivada 2 (s093):** integrar **`/schedule` (routines)** ao sistema de sync — gestão **proativa** do calendário: lembretes de metas diárias/semanais/mensais, tema do dia e os **gatilhos** (ex.: reavaliação da meta em S13). Routine inicial criada para o gatilho S13 (12/07). Caveat de arquitetura: o agente cloud do `/schedule` não tem o `ipub.db` local (Zero-DB no Cloud) → as routines servem como **trigger/lembrete** que abre a reavaliação localmente, não como executor com acesso ao estado.

**Status:** plano APROVADO → implementar a Fase 1 (`tools/cronograma.py` + `core/cronograma/grade.json`).
