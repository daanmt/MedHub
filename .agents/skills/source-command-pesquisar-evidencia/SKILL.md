---
name: "source-command-pesquisar-evidencia"
description: "Busca e auditoria de evidência para uma afirmação clínica decisória — hierarquiza fontes (sociedades BR > RCT/INT > consenso), atribui veredito e resolve conflito banca × evidência. Governado por core/contracts/evidence-governance.md."
---

# source-command-pesquisar-evidencia

Use this skill when the user asks to run the migrated source command `pesquisar-evidencia`.

## Command Template

# Skill: Pesquisar Evidência

> Operacionaliza o `core/contracts/evidence-governance.md`. A hierarquia, a taxonomia de vereditos, o substrato e a regra de conflito banca×evidência vivem **no contrato** — esta skill é o **procedimento**: como buscar, em que ordem, e o template de saída.

---

## Quando usar

- Auditar uma **afirmação clínica decisória** (conduta de 1ª linha, dose, cutoff, score, critério, contraindicação, meta) — sob demanda (`/pesquisar-evidencia "<afirmação>"`) ou dentro de `/analisar-questao` / criação de resumo quando há controvérsia ou baixa confiança.
- Decidir, entre alternativas, **qual é a conduta mais sustentada pela melhor evidência**.
- Resolver **"o gabarito diz X, mas é verdade hoje?"** (banca × diretriz vigente).

Não usar para fatos consolidados de baixa controvérsia (definições, anatomia) — auditoria é cara (contrato §1).

---

## Procedimento

### 1. Isolar a afirmação decisória
Reduzir a uma proposição testável: *"metformina é contraindicada com TFG < 30"*, *"na CAD pediátrica não se faz bolus de insulina"*. Uma afirmação por auditoria.

### 2. Buscar por tier (parar quando a de maior peso responde)
- **Tier 1 — sociedade BR / MS:** `WebSearch` "Diretriz [SBD/SBC/SBP/FEBRASGO…] [tema] [ano]" → `WebFetch` no PDF/página oficial. (Substrato `fallback` — PDFs de sociedade não estão no PubMed.)
- **Tier 2 — RCT/meta + guideline INT:** PubMed MCP do plugin `pubmed@life-sciences`, com **query precisa** (contrato §5): PMID conhecido -> `mcp__plugin_pubmed_PubMed__get_article_metadata`; trial nomeado -> `mcp__plugin_pubmed_PubMed__search_articles` com frase exata do título ou tag de campo. Ler o **contexto** do número no abstract; se não bastar e houver PMCID, `mcp__plugin_pubmed_PubMed__get_full_text_article`. (Substrato `canonico`.) 🔴 Uso obriga atribuição ao PubMed + **DOI como link**. Guidelines INT (ADA/AHA/IDSA/GINA…) por `WebSearch`.
- **Tier 3 — consenso/texto:** só se Tiers 1–2 não resolverem.
- **Consistência interna:** RAG local `app.engine.rag.search` para ver o que os `resumos/` já afirmam (substrato `local`) — `python -c "from app.engine.rag import search; [print(r) for r in search('<query>', n_results=3)]"`.

> Pesquisa pesada (várias fontes em paralelo) → delegar ao subagente **`evidence-researcher`** (`Agent` com `subagent_type: "evidence-researcher"`), que faz o fan-out e devolve o veredito estruturado — preserva o contexto principal. Budget: 6–10 macro-queries, cap 2 tentativas/afirmação (contrato §9).

### 3. Atribuir veredito (contrato §4)
`CONFIRMADO` (VERBATIM/SENTIDO) · `DIVERGENTE-VALOR` · `DIVERGENTE-CONDUTA` · `DESATUALIZADO` (banca × atual) · `NÃO-VERIFICÁVEL` (honest-negative) · `NÃO-AUDITADO`. Declarar o **substrato** (`canonico`/`fallback`/`local`).

### 4. Resolver conflito banca × evidência (contrato §6)
Se `DESATUALIZADO`: ensinar a **resposta da banca** + registrar 🔴 **armadilha "banca-dependente"** citando os dois lados. Nunca silenciar a divergência; nunca "corrigir a banca" no corpo da resposta.

### 5. Citar e persistir
Toda afirmação confirmada/corrigida carrega **fonte + ano** (e PMID/DOI se `canonico`) na regra-mestre/armadilha do resumo e do card.

---

## Template de saída

```
AFIRMAÇÃO: "<proposição decisória>"
VEREDITO: <CONFIRMADO|DIVERGENTE-VALOR|DIVERGENTE-CONDUTA|DESATUALIZADO|NÃO-VERIFICÁVEL> [substrato: canonico|fallback|local]
FONTE: <Sociedade Ano | PMID/DOI | guideline INT Ano>
O QUE A EVIDÊNCIA DIZ: <1-3 linhas, com a cifra/conduta correta>
BANCA × EVIDÊNCIA: <só se DESATUALIZADO: o que a banca espera vs a diretriz atual>
AÇÃO NO CONTEÚDO: <manter | corrigir valor/conduta | adicionar 🔴 armadilha banca-dependente>
```

---

## Invariantes (do contrato — não reespecificar)

- **Honest-negative:** busca não-sustentada = `NÃO-VERIFICÁVEL`, nunca fabricar fonte/PMID/cifra.
- **Boundary abstract-only:** achar o PMID ≠ confirmar a cifra; cifra em suplemento → `NÃO-VERIFICÁVEL [suplemento]`.
- **Query precisa:** nunca relevance multi-termo solta no PubMed — resolver por PMID quando ele existe, e ler o `query_translation` que a busca devolve antes de confiar no resultado.
- **BR-primacy + lente da banca:** contrato §2.
- **Substrato `fallback` ≠ `canonico`** em força probatória — declarar sempre.
