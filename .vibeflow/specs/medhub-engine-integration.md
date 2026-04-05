# Spec: MedHub — Study Engine Integração (Cards Contextuais + Dashboard)

> Gerado via /vibeflow:gen-spec em 2026-04-05
> Fase 3 de 3 | PRD: `.vibeflow/prds/medhub-core-simplification.md`

## Objective

Adicionar geração contextual de flashcards ancorada nos resumos do usuário, expor um
ponto de entrada para agentes externos após análise de erro, e exibir padrões de fraqueza
no dashboard — completando o loop erro → compreensão → reforço → insight.

## Context

Com o engine de consulta da Fase 2 em funcionamento, esta spec fecha o loop em 3 entregas:

1. **`generate_flashcards.py`** — substitui a heurística pura por cards ancorados no
   conteúdo do `resumos/` do próprio usuário. O card deixa de ser "pergunta genérica"
   e passa a refletir o raciocínio clínico do resumo correspondente.

2. **`analyze_error.py`** — interface simples para agentes externos: dado um tema/erro,
   retorna o contexto completo (resumo + erros relacionados + cards ativos). O agente
   ainda chama `insert_questao.py` diretamente; `analyze_error` é o "what happened"
   após a inserção.

3. **Dashboard — Padrões de Fraqueza** — expõe `weak_areas` de LangMem na UI, dando
   surface area real à memória longa que hoje é coletada mas nunca exibida.

## Definition of Done

- [ ] `generate_contextual_cards(tema, elo_quebrado, armadilha, resumo_content)` retorna `list[dict]` com campos v5 completos (`frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`); quando `resumo_content` é não-vazio, `frente_pergunta` NÃO começa com "Qual é o" ou "Descreva" (genérico demais)
- [ ] `analyze_error(tema, area)` retorna dict com `{"context": <saída de get_topic_context>, "resumo_available": bool, "can_generate_cards": bool}` sem `suggested_cards` e sem lançar exceção se tema não for encontrado
- [ ] `app/pages/1_dashboard.py` exibe seção "Padrões de Fraqueza" quando `summarize_performance()["padroes"]` não é vazio; seção está completamente ausente (sem título, sem empty state) quando lista é vazia
- [ ] `python tools/review_cli.py --limit 3` termina sem erros (core loop FSRS intacto após a integração)
- [ ] Nenhuma violação de conventions.md: sem `import sqlite3` novo fora dos CLIs, design system `COLORS`/`inject_styles` respeitado no dashboard
- [ ] `generate_contextual_cards()` retorna `quality_source='contextual'` quando resumo foi encontrado; `quality_source='heuristic'` como fallback — diferenciando as duas origens para auditoria futura

## Scope

| Arquivo | Ação |
|---|---|
| `app/engine/generate_flashcards.py` | CRIAR — geração contextual via Claude Haiku + fallback heurístico |
| `app/engine/analyze_error.py` | CRIAR — ponto de entrada para agentes pós-inserção de erro |
| `app/pages/1_dashboard.py` | EDITAR — adicionar seção "Padrões de Fraqueza" |

## Anti-scope

- NÃO modificar `tools/insert_questao.py` (preservar core loop; integração contextual é opcional, não obrigatória)
- NÃO ativar LangGraph
- NÃO construir interface conversacional no Streamlit
- NÃO usar retrieval semântico/MCP para busca de resumos
- NÃO alterar schema de `flashcards` (os campos v5 já existem)
- NÃO remover heurística atual de `insert_questao.py` — `generate_contextual_cards` é nova função paralela, não substituta forçada

## Technical Decisions

**`generate_contextual_cards()` — Claude Haiku com fallback:**
```python
def generate_contextual_cards(
    tema: str,
    elo_quebrado: str,
    armadilha: str | None,
    resumo_content: str | None = None,  # injetado pelo chamador via get_topic_context()
) -> list[dict]:
    """
    Retorna até 2 flashcards v5 para o erro.
    quality_source='contextual' se resumo_content presente, 'heuristic' caso contrário.
    """
    if resumo_content:
        # Extrai trecho relevante do resumo (keyword match no elo_quebrado)
        trecho = _extract_relevant_section(resumo_content, elo_quebrado)
        cards = _llm_generate(elo_quebrado, armadilha, trecho)  # Claude Haiku
        for c in cards:
            c["quality_source"] = "contextual"
    else:
        cards = _heuristic_generate(elo_quebrado, armadilha)  # lógica atual de insert_questao
        for c in cards:
            c["quality_source"] = "heuristic"
    return cards
```

O chamador típico (agente externo) faz:
```python
ctx = get_topic_context("Sepse Neonatal")
cards = generate_contextual_cards(
    tema="Sepse Neonatal",
    elo_quebrado="critério de SIRS em neonatos",
    armadilha="SIRS não se aplica igual a adultos",
    resumo_content=ctx["resumo_content"],
)
```

**`analyze_error()` — função de contexto, não de geração:**
```python
def analyze_error(tema: str, area: str | None = None) -> dict:
    """
    Para agentes externos: retorna contexto e sinalizadores após análise de erro.
    NÃO gera cards — use generate_contextual_cards() separadamente se necessário.
    O agente chama insert_questao.py diretamente; esta função é chamada a seguir
    para obter contexto estruturado sobre o tema.

    Retorno:
        context (dict): saída de get_topic_context()
        resumo_available (bool): True se resumo clínico foi encontrado para o tema
        can_generate_cards (bool): True se há resumo + elo_quebrado suficientes para gerar cards contextuais
    """
    ctx = get_topic_context(tema, area)
    resumo_available = ctx.get("resumo_path") is not None
    return {
        "context": ctx,
        "resumo_available": resumo_available,
        "can_generate_cards": resumo_available,  # pré-condição mínima para geração contextual
    }
```

A geração de cards fica exclusivamente em `generate_contextual_cards()`. O chamador decide
se e quando invocar a geração — `analyze_error()` apenas informa se as condições estão
presentes (`can_generate_cards: True/False`).

**Dashboard — seção condicional com `content_card`:**
```python
# app/pages/1_dashboard.py
from app.engine import summarize_performance
from app.utils.styles import content_card, COLORS

perf = summarize_performance()
if perf["padroes"]:
    st.markdown("### Padrões de Fraqueza")
    for p in perf["padroes"]:
        st.markdown(content_card(
            title=p["area"],
            body=f"{p['padrao']} — {p['error_count']} erros",
        ), unsafe_allow_html=True)
```

Sem título, sem empty state quando `padroes == []` — seção simplesmente não aparece.

**Não tocar `insert_questao.py`:**
A geração contextual é disponibilizada como função pública do engine. O `insert_questao.py`
continua usando sua heurística interna — compatível, sem risco ao core loop. A integração
entre `insert_questao.py` e `generate_contextual_cards()` é uma decisão futura (Fase 4+).

**ANTHROPIC_API_KEY:**
`generate_contextual_cards()` com `resumo_content` presente chama Claude Haiku.
Requer `ANTHROPIC_API_KEY` no ambiente. Fallback graceful: se a variável não estiver
presente ou a chamada falhar → usar heurística e retornar `quality_source='heuristic'`.

## Applicable Patterns

- **`design-system-usage.md`** — seção do dashboard usa `content_card()` e `COLORS` de `app.utils.styles`
- **`streamlit-page-structure.md`** — nova seção em `1_dashboard.py` segue o padrão: `inject_styles()` no topo (já existe), nova seção com `st.markdown` + `unsafe_allow_html=True` para cards
- **`error-insertion-pipeline.md`** — `generate_contextual_cards()` deve retornar campos no mesmo schema v5 que `insert_questao.py` já usa

## Risks

| Risco | Mitigação |
|---|---|
| `_extract_relevant_section()` extrai trecho irrelevante do resumo | Usar keyword match contra headers H3 e bullets; se sem match → retornar `resumo_content[:2000]` (primeiros 2000 chars como contexto geral) |
| LLM gera `frente_pergunta` começando com padrão genérico | Validação pós-geração: se começar com "Qual é o" / "Descreva" → rejeitar e usar heurística |
| `ANTHROPIC_API_KEY` ausente em ambientes locais | `try/except` em `_llm_generate()` com fallback explícito para heurística |
| Seção "Padrões de Fraqueza" exibe dados desatualizados (LangMem consolidado há dias) | Aceitável para v0 — adicionar data da última consolidação como subtítulo (`p["ultima_ocorrencia"]`) |
| `1_dashboard.py` pode ter `@st.cache_data` em funções que agora chamam o engine | Verificar TTL no cache — se `summarize_performance()` for chamada dentro de cache, garantir que LangMem read seja thread-safe |

## Dependencies

- `.vibeflow/specs/medhub-engine-core.md` — `analyze_error.py` chama `get_topic_context()` do engine core; dashboard chama `summarize_performance()`
