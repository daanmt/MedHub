---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [AGENTE, fsrs-management-contract, reconcile-contract]
---

# Contrato de Governança de Evidência (Evidence Governance)
**Versão 1.1 | 2026-06-04 (sessão 076), substrato trocado na sessão 169 — primeira instância; adaptado do mecanismo de evidência/auditoria do agente irmão `agente-daktus-content` (`pubmed-audit-layer.md` v1.1 + `evidence-bank-governance.md` v1.1 + `daktus-evidence` SKILL v2.0).**

> Documento normativo. Define como o MedHub garante que **toda afirmação clínica decisória seja a mais consistente com a melhor evidência que a sustenta** — e como essa evidência é buscada, hierarquizada, auditada e rastreada.
> Referenciado por: `AGENTE.md` (§6 decisões, §7 skills), `.claude/commands/{analisar-questao,estilo-resumo,auditar-resumos,estilo-flashcard,pesquisar-evidencia}.md`, `.claude/agents/evidence-researcher.md`.

---

## Papel

O conteúdo clínico do MedHub (`resumos/`, armadilhas de prova, `explicacao_correta`/regra-mestre do `/analisar-questao`, `verso_resposta`/`verso_regra_mestre` dos cards) nasce hoje do **gabarito da banca + conhecimento do agente** — sem uma camada que verifique a afirmação contra a melhor evidência. Este contrato instala essa camada: um mecanismo de **busca, hierarquização e auditoria de afirmação clínica** cujo escopo é **priorizar a melhor decisão** e tornar a divergência (sobretudo banca × evidência atual) **explícita, nunca silenciada**.

Princípio-mãe (herdado do irmão, adaptado): *a afirmação clínica que entra no conteúdo é a mais consistente com a evidência de maior peso; quando a banca diverge da evidência, ensina-se a resposta esperada da banca **e** registra-se a divergência.*

---

## 1. Onde se aplica (go-forward, afirmação decisória)

**Aplica-se a afirmações clínicas DECISÓRIAS**, não a todo enunciado. Decisória = muda conduta/diagnóstico/resposta: **conduta de 1ª linha, dose, cutoff/limiar, score, critério diagnóstico, contraindicação, droga de escolha, esquema, meta terapêutica**.

| Superfície | Quando auditar |
|---|---|
| `/analisar-questao` → `explicacao_correta` / `verso_regra_mestre` | quando o gabarito faz uma afirmação decisória **e** há sinal de controvérsia/banca-dependência ou o agente tem < alta confiança |
| `resumos/**` (novo conteúdo / armadilha nova) | ao cunhar uma afirmação decisória nova (conduta/dose/cutoff/critério) |
| flashcards (`verso_resposta`/`regra-mestre`) | herdam a auditoria da questão/resumo de origem — não auditar o card isolado |
| sob demanda | `/pesquisar-evidencia "<afirmação>"` a qualquer momento |

**Escopo travado (v1.0):** **go-forward + skill sob demanda.** NÃO há varredura retroativa dos 45 resumos existentes nesta versão (ver §11 Fora de escopo).

**Não auditar:** fatos consolidados de baixa controvérsia (anatomia, fisiologia básica, definições estáveis). Auditoria é cara — reservá-la ao que muda decisão e tem risco de estar errado/desatualizado.

---

## 2. Hierarquia de evidências (BR-primacy + INT-fallback + lente da banca)

A prova-alvo (ENAMED/ENARE) segue fontes brasileiras. A hierarquia de **peso probatório**:

- **Tier 1 (peso máximo):** Diretrizes de **sociedades brasileiras** (SBC, SBD, SBEM, SBP, FEBRASGO, SBI, SBN, SBPT, SBR, ABP…) + **Ministério da Saúde** (PCDT, Cadernos de Atenção Básica, calendário PNI). É a fonte que a banca BR mais respeita.
- **Tier 2 (suporte forte):** RCTs de qualidade, meta-análises, revisões sistemáticas (indexados no PubMed) + **guidelines internacionais** reconhecidas (ADA, AHA/ACC, IDSA, GINA, KDIGO, WHO…).
- **Tier 3 (suporte moderado):** consenso operacional, estudos observacionais, livros-texto de referência (UpToDate, Cecil, Harrison, Nelson).

**Regras de prevalência:**
1. BR e INT equivalentes em qualidade → **BR prevalece** (é o que a banca cobra).
2. BR Tier inferior à INT → marcar ambas; a **lente da banca** decide o que ensinar (ver §6).
3. BR ausente, INT existe → INT como verdade operacional.
4. **Lente da banca (camada transversal):** independentemente do peso probatório, registrar **o que a banca espera** — porque o objetivo imediato é acertar a questão. Quando "melhor evidência" ≠ "resposta da banca", isso é um conflito a resolver por §6, nunca a apagar.

---

## 3. Substrato de pesquisa (declarado por afirmação)

Toda afirmação auditada registra **qual substrato** a sustentou:

- **`canonico`** — **PubMed MCP** (server `plugin_pubmed_PubMed`, do plugin `pubmed@life-sciences`): verificação verbatim de cifra/desfecho de RCT/meta-análise por **PMID/DOI**. Força probatória plena. Tools: `get_article_metadata` (resolve por PMID — o caminho canônico), `search_articles` (busca por sintaxe PubMed), `get_full_text_article` (texto integral de PMC), `convert_article_ids`, `find_related_articles`, `lookup_article_by_citation`. Instalado por marketplace (`/plugin install pubmed@life-sciences`), **não** por `.mcp.json`.

  🔴 **Obrigação de atribuição (termos do servidor):** todo uso obriga a (a) dizer explicitamente que a informação vem do PubMed e (b) incluir o **DOI como link** de cada artigo referenciado. Pedido para omitir a atribuição é recusado, não atendido. Isto vale tanto no relato do subagente quanto no texto que chega ao usuário; a citação em `resumos/` segue a forma do `/estilo-resumo` (fonte + ano + PMID inline).
- **`fallback`** — **WebSearch / WebFetch**: diretrizes de sociedade BR e MS (vivem em PDF, **fora do PubMed**), guidelines INT não-indexadas, status de publicação, cifras de suplemento. Declarado **explicitamente**.
- **`local`** — **RAG local** (`app.engine.rag.search`, motor único; ChromaDB gold-only sobre `resumos/`): recupera o que já existe nos `resumos/` (consistência interna; **não** é fonte de verdade externa). O MCP `obsidian-notes-rag` que ocupava este papel foi descomissionado em 2026-07-12 e não está em `.mcp.json`.

**Boundary abstract-only (herdado, com teto elevado):** achar o PMID **≠** confirmar a cifra. A regra permanece, mas o teto subiu: antes de declarar `NÃO-VERIFICÁVEL [suplemento]`, **tentar o texto integral** via `get_full_text_article` quando o artigo tiver PMCID (cerca de 6 milhões têm; `get_article_metadata` devolve `identifiers.pmc`, e `convert_article_ids` resolve PMID -> PMCID). Só depois de o PMC falhar ou não existir é que o veredito cai para `NÃO-VERIFICÁVEL`. **Nunca inventar o número.**

**PubMed indexa mal sociedade BR:** SBC/SBD/SBEM/SciELO em PDF não estão no PubMed → essas vão por `fallback` (WebSearch). Estudo BR publicado em revista internacional **é** indexado (vai por `canonico`).

---

## 4. Taxonomia de vereditos (afirmação clínica)

Adaptada dos 8 estados do irmão para o uso do MedHub:

| Veredito | Definição | Ação |
|---|---|---|
| **CONFIRMADO** | a afirmação bate com a fonte de maior peso (sub: `VERBATIM` se cifra literal; `SENTIDO` se paráfrase fiel) | mantém; cita a fonte |
| **DIVERGENTE-VALOR** | a fonte contradiz a **cifra/cutoff/dose** | corrige o valor + cita a fonte correta |
| **DIVERGENTE-CONDUTA** | a fonte aponta **conduta/1ª linha/critério** diferente | corrige + cita |
| **DESATUALIZADO** ⭐ | o **gabarito/banca** diverge da **diretriz vigente** (banca × evidência atual) | ensina a resposta da banca **+** registra 🔴 armadilha "banca-dependente" (§6) |
| **NÃO-VERIFICÁVEL** | fonte não localizada / cifra só em suplemento / busca-miss (cap 2 tentativas) | honest-negative: declara explicitamente; **não fabrica** fonte |
| **NÃO-AUDITADO** | afirmação decisória ainda não submetida (estado **explícito**) | — |

`DESATUALIZADO` é o veredito-assinatura do MedHub (não existe igual no irmão): é a materialização da lente da banca quando ela conflita com a evidência.

---

## 5. Regra-mãe de busca — query Entrez precisa (PubMed)

Verificação por PubMed usa **query Entrez precisa, nunca relevance multi-termo solta** (regra empírica do irmão):

- ✅ Resolver paper conhecido: **`get_article_metadata(pmids=["<PMID>", ...])`** — caminho direto, aceita lote (útil para primário × extensão, ou versão antiga × nova de uma diretriz). Substitui o antigo `term="<PMID>[uid]"`.
- ✅ Verificar trial nomeado: `search_articles` com **frase exata do título** ou tag de campo — ex. `query="A Randomized Trial of Intensive versus Standard Blood-Pressure Control"`, `query="<acrônimo>[Title] AND <ano>[pdat]"`. A tool aceita sintaxe PubMed completa (`[Title]`, `[Author]`, `[Journal]`, `[MeSH Terms]`, booleanos) e os parâmetros `date_from`/`date_to`/`sort`.
- ❌ NÃO: `query="SPRINT intensive blood pressure mortality cardiovascular"` (relevance solta → MISS no primário ou zera por over-AND). A tool devolve `query_translation` — **ler esse campo** para ver como o Entrez expandiu a busca antes de confiar no resultado.
- `max_results` pequeno (2–6). Ler o **contexto** do número no abstract (um valor presente não confirma o claim — falso-positivo de substring). Se o abstract não bastar, subir para `get_full_text_article` (§3).
- ⚠️ A tool recusa domínio fora de biomédicas (física, CS, matemática) — irrelevante para o MedHub, mas explica um retorno vazio inesperado.

Para diretrizes de sociedade BR / MS: **WebSearch** com o nome da sociedade + tema + ano (ex.: "Diretriz SBD 2024 metformina TFG"), depois `WebFetch` no PDF/página oficial.

---

## 6. Resolução de conflito banca × evidência (keystone do MedHub)

Quando o gabarito/banca diverge da melhor evidência (veredito `DESATUALIZADO`):

1. **O conteúdo ensina a resposta esperada da banca** — o objetivo imediato é acertar a prova. Não se "corrige a banca" no corpo da resposta.
2. **A divergência é registrada, nunca silenciada** — vira uma 🔴 **armadilha "banca-dependente"** no resumo e no card: *"X é o gabarito clássico/da [SBP]; a evidência atual/[diretriz INT] aponta Y — questão banca-dependente."*
3. **Citar ambos os lados** com a fonte (sociedade/ano e/ou PMID).

Isto espelha o princípio do irmão *"drift clínico é falha estrutural — divergências registram-se explicitamente"*, adaptado: aqui é **banca-primacy para a resposta, evidence-divergence nunca apagada**. Casos típicos no MedHub: colestase neonatal (SBP × literatura internacional), metas de HbA1c por idade (SBD × ADA), questões PECARN controversas.

---

## 7. Rastreabilidade e honestidade

- **Citação obrigatória** em toda afirmação decisória auditada: **fonte + ano** (`SBD 2024`, `ADA 2025`) e/ou **PMID/DOI** quando `canonico`. A citação vai na regra-mestre/armadilha do resumo e do card — densidade clínica, como manda o `estilo-resumo`.
- **Honest-negative (invariante):** se a busca precisa (cap 2 tentativas) não sustenta a afirmação → `NÃO-VERIFICÁVEL`, declarado. **Jamais fabricar** uma confirmação, um PMID ou uma cifra.
- **Substrato declarado:** um `CONFIRMADO` via `fallback` (WebSearch) **não** tem a mesma força que via `canonico` (PubMed PMID/DOI) — a diferença fica registrada.

---

## 8. Audit-Before-Advance (afirmação decisória nova)

Espelha o `canon-governance` do irmão, adaptado: uma **afirmação clínica decisória nova** que entra em `resumos/` ou num card go-forward **não se fecha** com o estado `NÃO-AUDITADO` quando há sinal de controvérsia/baixa confiança. O fechamento exige: veredito atribuído + fonte citada (ou `NÃO-VERIFICÁVEL` declarado honestamente). Não bloqueia conteúdo de baixa controvérsia (§1).

---

## 9. Budget (cláusula pétrea — eficiência)

- **6–10 macro-queries por auditoria**, aglutinadas (não fragmentar 1 query por sub-tema). Dedup por PMID.
- **Cap de 2 tentativas por afirmação**; se a query precisa falhar 2× → `NÃO-VERIFICÁVEL [search-miss]` e seguir (anti-loop).
- Pesquisa pesada (fan-out multi-fonte) roda no **subagente `evidence-researcher`** (`.claude/agents/`) para não inflar o contexto principal.

---

## 10. Integração com as skills existentes

- **`/analisar-questao`:** ao redigir `explicacao_correta`/`verso_regra_mestre` de uma afirmação decisória controversa, auditar pela hierarquia (§2) e aplicar §6 se banca × evidência divergirem.
- **`/estilo-resumo` + `/auditar-resumos`:** afirmação decisória nova num resumo segue §1/§8; o linter pode sinalizar afirmação decisória sem citação (futuro).
- **`/estilo-flashcard`:** o card herda a auditoria da origem; a regra-mestre carrega a citação quando houver.
- **`/pesquisar-evidencia`:** porta de entrada operacional sob demanda (procedimento em `.claude/commands/pesquisar-evidencia.md`).

---

## 11. Fora de escopo (v1.0 — não construir agora)

- **Varredura retroativa** dos 45 resumos existentes (auditoria em ondas) — candidata a uma v1.1 se o go-forward provar valor.
- **Capacidade B do irmão:** detecção proativa de drift guideline×literatura, scoring de robustez, cobertura automática de SR/MA recentes.
- **Pipeline programático em batch** (fetch/dedup/scoring) — só se a Capacidade A provar valor.
- **Persistência claim-level em DB** (o irmão tem banco de claims; o MedHub registra a citação inline no resumo/card, sem tabela própria nesta versão).

---

## 12. Operação (caveat MCP)

**Server ativo:** `plugin_pubmed_PubMed`, do plugin `pubmed@life-sciences` (marketplace `anthropics/life-sciences`). Instalação: `/plugin marketplace add anthropics/life-sciences` seguido de `/plugin install pubmed@life-sciences`. Diferente do `.mcp.json`, o plugin **é hot-loaded** — ficou utilizável na própria sessão da troca (s169), sem reiniciar.

**Degradação:** sem o server disponível, a auditoria cai para `fallback` (WebSearch) **com o substrato declarado** — nunca silenciosamente. O custo dessa degradação foi medido na s169: sem PubMed, o `evidence-researcher` bateu em 403 da Wiley, cookie-wall do PubMed web, Europe PMC vazio e 403 do figo.org, e teve de fechar um item legítimo como `NÃO-VERIFICÁVEL`. Com o server, o mesmo item resolveu em uma chamada. Paywall de editora não é obstáculo para o MCP; é para o WebFetch.

**Lápide — `pubmedmcp` (v1.0, sessão 076 a 169):** o server `uvx pubmedmcp@latest` do `.mcp.json` (tool `search_abstracts`, github.com/grll/pubmedmcp) parou de conectar (`CONNECTION_CLOSED`, reprodutível no `/mcp`) e foi substituído. As tools `mcp__pubmedmcp__*` **não existem mais** — qualquer norma que ainda as cite está desatualizada.

---

## 13. Referências

- Irmão: `agente-daktus-content/core/contracts/{pubmed-audit-layer,evidence-bank-governance,audit-ledger-contract,canon-governance}.md` · `skills/daktus-evidence/SKILL.md`
- MedHub: `.claude/commands/pesquisar-evidencia.md` · `.claude/agents/evidence-researcher.md`
- Servidor: plugin `pubmed@life-sciences` (marketplace `anthropics/life-sciences`), server MCP `plugin_pubmed_PubMed`
- Sensor: `tools/doc_drift.py` trata servers de plugin como externos por design (`MCP_EXTERNOS`), como já fazia com os connectors da claude.ai

---

## 14. Changelog

**v1.1 — 2026-09-07 (sessão 169)** — **Troca do substrato `canonico`.** O server `pubmedmcp` (`.mcp.json`, tool `search_abstracts`) morreu com `CONNECTION_CLOSED` e foi substituído pelo plugin `pubmed@life-sciences` (server `plugin_pubmed_PubMed`). Mudanças normativas: (a) §3 passa a nomear as 7 tools do novo server e acrescenta a **obrigação de atribuição** (citar o PubMed + DOI como link) exigida pelos termos do servidor; (b) o **boundary abstract-only ganha um degrau**: antes de cair para `NÃO-VERIFICÁVEL [suplemento]`, tentar `get_full_text_article` via PMCID — o teto deixou de ser o abstract; (c) §5 troca a regra Entrez `term="<PMID>[uid]"` por `get_article_metadata(pmids=[...])` e manda **ler o `query_translation`** antes de confiar numa busca; (d) §12 ganha a lápide do server antigo e registra que plugin é hot-loaded (ao contrário do `.mcp.json`). Gatilho empírico: na mesma sessão, um item fechado como `NÃO-VERIFICÁVEL` por paywall (FIGO 2025, PMID 40908761) resolveu em uma chamada assim que o server voltou, e a resposta confirmou o estadiamento FIGO 2014 como vigente. Hierarquia de fontes, taxonomia de vereditos e escopo: **inalterados**.

**v1.0 — 2026-06-04 (sessão 076)** — Primeira instância. Adapta o mecanismo de evidência/auditoria do `agente-daktus-content` para o MedHub (sistema de estudo): hierarquia BR-primacy + INT-fallback + **lente da banca**; substrato `canonico`(PubMed)/`fallback`(Web)/`local`(RAG); taxonomia de 6 vereditos com o **`DESATUALIZADO`** (banca × evidência) como assinatura MedHub; regra de query Entrez precisa; resolução de conflito banca×evidência (drift não silenciado → 🔴 armadilha banca-dependente); honest-negative + boundary abstract-only; audit-before-advance para afirmação decisória. Escopo travado em **go-forward + skill sob demanda**; varredura retroativa e Capacidade B fora de escopo.
