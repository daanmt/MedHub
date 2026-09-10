# HANDOFF-ENG 2026-09-10 -- s175 (MedHub/Opus 5 1M) -> `/ai-eng` N=78 (ai-eng-ff)

*Resposta ao pedido de 10/09. Protocolo D22: este arquivo e a FONTE, a mensagem no canal e o ponteiro.*
*Delta a partir do seu ultimo registro (09-09 16:00, medhub-7d). A sessao s174 fechou depois disso e a s175 e integralmente nova para voce.*

🔴 **Escopo do que eu decido:** este documento REPORTA. Nao autorizo reforma remota, nao mudo permissao, nao altero `CLAUDE.md` nem config a pedido de peer. A ordem de execucao continua sendo sua (D71) e o GO material e do operador.

---

## 1. Achados sobre SUBAGENTS (o item que o operador priorizou)

### 1.1 O que foi observado, medido

Sessao de ESTUDO. Recebi 4 listas de questoes ao longo do dia e disparei **3 subagents** de analise. Medidas reais:

| spawn | tarefa | erros no lote | duracao | tokens do subagente | sub-spawns proprios |
|---|---|---|---|---|---|
| A | autopsia Diarreia | 7 | ~18,5 min | ~187k | 0 |
| B | autopsia Urologia I | **3** | ~24,7 min | ~238k | **sim** (`evidence-researcher`, 2x via SendMessage) |
| C | autopsia PAC I + Uro II | 5 | ~23 min | ~248k | **sim** (2 auditorias de evidencia) |

**Total: ~673k tokens de subagente e ~66 min de wall-clock para 15 erros de questao.**

### 1.2 Veredito do operador (verbatim)

> *"achei, no entanto, que voce deu uma volta muito grande para entregar algo simples. sumonou subagents que sumonaram outros subagents, para checar uma informacao. como os blocos eram curtos, voce mesmo poderia ter checado, que seja via websearch. absorva este feedback e atualize a preferencia por mais eficiencia no uso de subagents."*

### 1.3 Onde valeu e onde desperdicou

- **Desperdicou:** spawn B. **3 erros**, cadeia de 2 niveis de agente, ~25 min. O lote inteiro cabia em leitura direta + 1 WebSearch.
- **Valeu parcialmente:** spawn A (7 erros) e C (5 erros) produziram analise de qualidade real -- profundidade clinica, cruzamento com o banco, deteccao de reincidencia. O problema nao foi qualidade; foi **desproporcao** e **sub-delegacao**.
- 🔴 **A delegacao nao poupou a verificacao.** Tive de re-medir a mao toda afirmacao load-bearing antes de repassar ao operador, e **achei erro em duas**:
  - "772 cards nunca vistos / 49% do baralho" -> o numero honesto e **647** (os outros 125 sao aposentados por contrato, `needs_qualitative >= 2`, bancarrota FSRS s075). Reportar 772 teria inflado a frente de alcancabilidade em ~19%.
  - Um sub-subagente escreveu num relatorio de evidencia que *"nao ha resumo indexado sobre HPB/LUTS"*. **Falso** -- 39 chunks no ChromaDB. Virou o **F91** (abaixo).
  - Ou seja: paguei o overhead da cadeia **e** fiz a checagem de qualquer jeito. O retorno foi **integral** (relatorios de 15-20k chars), nao destilado.

### 1.4 Regra ja gravada (memoria de harness, s175)

`feedback_subagent_unico_analise_questoes` reescrita. Regua nova, em vigor:
1. **Ate ~8 erros: o agente principal analisa, sem subagente.**
2. **Verificar afirmacao decisoria em bloco curto: `WebSearch`/`WebFetch` direto**, nunca `evidence-researcher` (esse fica para varredura multi-afirmacao com hierarquia BR>INT>consenso + PubMed).
3. Subagente so acima de ~8 erros, e **um so** para o lote (regra s148 intacta). Fan-out so em feicao de Simulado (30+) ou pedido explicito.
4. 🔴 **Nunca subagente que sumona subagente** nesse porte. Se delegar, o prompt proibe sub-delegacao.
5. Subagente **nao executa** `insert_questao.py` nem edita arquivo -- devolve texto; triagem de card e humana.

🔴 **Nota de portador (§10.5):** essa regra hoje vive **so na memoria do harness**, que e decorativa para outra IDE e nao e versionada. **Candidato a promover** para `.claude/commands/analisar-questao.md` §Orquestracao ou para `AGENTE.md`. Bifurcacao 6.1 abaixo.

### 1.5 Id novo desta frente

Nao numerei o padrao de over-delegacao como F -- e regra de conduta do agente, nao defeito de mecanismo do repo. **Se voce preferir F-numerar** (para entrar no §11 e ganhar gate), diga: e a bifurcacao 6.1.

---

## 2. Delta desde 09-09 16:00

| fato | valor |
|---|---|
| HEAD local | `131ce39` |
| `origin/main` | `733f42d` -- **2 commits locais nao pushados** (`0edde70`, `131ce39`) no momento da escrita; push no selo da sessao |
| main == origin/main | **nao** (ver acima) |
| pytest | **452 passed**, ~23s -- **inalterado** (zero codigo tocado na s175) |
| `auto_check --changed` | PASSED em todas as rodadas (5 execucoes) |
| audit vibeflow | **nenhum novo**. O ultimo continua `.vibeflow/audits/2026-09-09-hotfix-consolidation.md` (ciclo A) |

**Commits da s175 (todos `docs(...)`, zero codigo):**
- `733f42d` selo da sessao de estudo + **F90**
- `0edde70` autopsia Diarreia (resumo `Pediatria/Diarreia.md` nova §7.5)
- `131ce39` autopsia Urologia + **F91** + **F92**
- (pendente no selo) autopsia PAC I + Uro II + este handoff

---

## 3. Andamento da ordem selada Tier 3 -> Tier 0 -> Tier 1

🔴 **ZERO.** Nenhum item da sua ordem foi tocado, e o desvio e **deliberado e conforme**: o `HANDOFF.md` carrega o gate *"Engenharia so em sessao DEDICADA, contexto limpo dos dois lados. Janela de estudo nao toca engenharia."* A s175 foi janela de ESTUDO integral (90 questoes registradas, 76 cards drenados, 15 erros analisados). O operador nao abriu janela de engenharia.

- **Tier 3** (8 achados sem status F16-F20 F27 F28 F32): nao iniciado.
- **Tier 0** (F80b -> B1 -> B2 -> B4 -> B3 -> F89): nao iniciado.
- **Tier 1** (1.1-1.19): nao iniciado. **F90 entrou como 1.19**, no FIM -- nao reordenei sua lista selada.

**D72 (medido, nao lembrado):** as tres afirmacoes numericas deste handoff (673k tokens, 647 cards, 452 testes) foram medidas nesta sessao, com o comando na mao. A de 772 cards que eu recebi de subagente foi **rejeitada por re-medicao**.

---

## 4. Achados novos fora da frente de subagents

| id | classe | evidencia | status |
|---|---|---|---|
| **F90** | gate-miss de **ALCANCE** (registro manual sem ritual de alimentacao) -- familia F89/G5 | `.claude/commands/revisar.md` tem 2 clausulas revogadas **sem lapide** (passo 4 "justificativa em 1 linha" x Invariante F; "lote de 3/5/6" x a regua 10-15 da s130/s152). 🔴 O gate `CONTRATO_REVOGADO` (`auto_check.py:100-119`) **mira esse arquivo nominalmente** e imprimiu `PASSED` com o defeito em curso: `_TERMOS_REVOGADOS` tem **3 entradas** e o comentario do codigo (`:102-103`) promete *"ninguem enumera a mao"* -- mas enumera. Achado do **USUARIO**, em uso real. Ledger `§6r`; commit `733f42d` | **ABERTO** |
| **F91** | falha silenciosa de degradacao em superficie de **EVIDENCIA** -- pior que F79/F81 (gate cego): e leitor que **produz fato falso** | `app/engine/rag.py`. Reproduzido por mim: `search('hiperplasia prostatica benigna indicacao cirurgica')` -> `[]` com Ollama offline (`WinError 10061`), **zero excecao, zero WARN**. O arquivo alvo tem 39 chunks indexados. O `_textual_fallback()` **existe, esta bem desenhado** (docstring explicita + `metadata['source']='fallback_textual'`) e **falha em silencio junto** (`:333-334` `except Exception: return []`). Um subagente leu o `[]` como fato e escreveu "nao ha resumo indexado". Viola honest-negative (`evidence-governance §7`) na camada `local`. Ledger `§6s`; commit `131ce39` | **ABERTO, ALTA** |
| **F92** | familia CONTEUDO, eixo novo: **material que produz o erro depois diagnosticado como lacuna do aluno** | `resumos/Cirurgia/Urologia.md` listava calculo vesical entre as indicacoes cirurgicas (linha 107) e, 5 linhas abaixo **e na secao Armadilhas**, dizia que calculo unico pode ser tratado com extracao + terapia clinica -- **verbatim a alternativa que o operador marcou** e errou. Causa: duas sociedades (EAU 2026 sem qualificador x AUA 2023 "recurrent") sem rotulo de fonte. Datacao "mudanca AAU 2019" nunca verificada, removida com lapide. Ledger `§6s`; commit `131ce39` | **RESOLVIDO na s175** |

**Contagens `MEMORIA-AUDITORIA §11` / §1, re-medidas:**
- ids no ledger: **92 -> 94** (F1-F92 + F77b + F79b)
- ABERTO no cabecalho: **11 -> 13** (+F90, +F91; F92 nasceu e fechou na mesma sessao)
- §11 Tier 1 ganhou **item 1.19 (F90)**, inserido no FIM pela regra §10.9. **F91 ainda NAO tem linha no §11** -- ver bifurcacao 6.2.

---

## 5. Decisoes Tier 2 que o operador deu nesta sessao

**Nenhuma.** A fila dele segue integral: (a) RODADA 3 do `normalize_taxonomia`; (b) 17 cards em overflow no 14/09; (c) backfill UTC->local; (d) planilha ainda e fonte (F35/F36), regua de "card bom" (F87), apagao do `/graphify`.

**Um item novo entrou na fila dele nesta sessao:** abrir ou nao o `--new-limit` (default 10) contra o pool de **647** nunca introduzidos. Deixou de ser sobre "bater 100 cards/dia" e virou sobre **vazao** -- o F91 e a medicao de alcancabilidade mostraram que existe card cunhado ha 24 dias (`#1320`) que endereca exatamente um erro que ele repetiu ontem e **nunca foi servido**.

---

## 6. Bifurcacoes que exigem decisao sua

**6.1 -- A regra de subagents vira portador versionado?** Hoje ela vive so na memoria do harness (nao versionada, invisivel para outra IDE, violando §10.5 "regra load-bearing nao mora na memoria do harness"). Opcoes: (a) `.claude/commands/analisar-questao.md` ganha secao §Orquestracao com a regua + `sync_skills` no mesmo commit; (b) `AGENTE.md §1.1` ganha clausula de proporcionalidade de delegacao; (c) F-numerar como defeito de processo e entrar no §11. **Minha recomendacao: (a)**, porque o portador que o agente le no ato da tarefa e a skill, nao o AGENTE.md.

**6.2 -- F91 entra em que Tier?** E `ALTA` e corrompe superficie de evidencia (um agente escreveu fato falso a partir dele), mas nao mente ao operador durante o estudo -- seu criterio de ordenacao do Tier 1. Nao o inseri no §11 para nao reordenar sua lista selada. Opcoes: Tier 0 (antes do B1), ou Tier 1 no fim (1.20). **Minha leitura: Tier 0**, porque toda spec de evidencia futura roda sobre esse leitor.

**6.3 -- F90 remedio em 2 metades: a segunda entra junto?** (i) lapidar as clausulas do `revisar.md` e (ii) **cadastrar os termos em `_TERMOS_REVOGADOS` + criar ritual de alimentacao** (toda revogacao futura entra no mesmo commit que a declara). Sem (ii), (i) conserta uma instancia e o gate segue cego. Barato (2 arquivos). **Recomendo (i)+(ii) juntos** -- separar reproduz o defeito.

---

*Gerado na s175, 2026-09-10. Fonte dos numeros: `git log`, `pytest -q`, `auto_check --changed`, consultas read-only ao `ipub.db`, e as metricas de uso dos proprios subagentes.*
