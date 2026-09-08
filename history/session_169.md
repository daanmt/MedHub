# Session 169 -- 95 questoes + 60 cards + 10 resumos do sprint + troca do substrato PubMed
**Data:** 2026-09-07
**Ferramenta:** Claude Code (Opus 5, 1M)
**Continuidade:** Sessao 168 (sprint S17-S20 decidido + aula-base de 13 temas)

---

## O que foi feito

### 1. Questoes -- 95 em 3 blocos (87,4%)
| Bloco | Area | | |
|---|---|---|---|
| Diarreia | Pediatria | 22q | 86,4% |
| SUA | Ginecologia | 23q | 69,6% |
| APS no Brasil | Preventiva | 50q | **96,0%** |

Volume registrado em `sessoes_bulk` ANTES de processar erros nos 3 blocos (AGENTE §6). Acumulado: **6.916q**.
Os 10 erros foram analisados por **1 subagent unico por lote** (nao fan-out) e persistidos: **#961-#963** (Diarreia), **#964-#970** (SUA), **#971-#972** (APS). 21 cards cunhados (#1526-#1546). Tema novo na taxonomia: `Ginecologia / Sangramento Uterino Anormal`.

### 2. Resumos -- 10 cunhados/expandidos, cobertura do sprint de ~30% para 100%
Inventario cruzando as 24 tarefas verdes (725q) contra o acervo: **7 temas sem resumo + 2 stubs declarados**, cobrindo 508 das 725q. Fan-out de **10 subagentes Sonnet em paralelo**, brief travado (spec de estilo, retencao de PDF, fronteiras).

Urologia (470 linhas) · Pneumonias na Infancia (347) · Diarreia (289) · Tumores Anexiais e CA de Ovario (409) · Etica Medica (**37 -> 364**) · DM na Gestacao (**44 -> 258**) · Pneumonias Bacterianas (302) · HAS Parte 1 (237) · HAS Parte 3 (257) · Vitalidade Fetal (328).

**Regra de Acumulo verificada nos 2 stubs** por busca de string: as 2 armadilhas antigas da Etica e as 4 do DMG intactas, com o texto clinico original preservado.
**Estadiamento FIGO preenchido com fonte auditada** (documento oficial FIGO 2014 verbatim + update FIGO 2021; espelho SBP 2019) apos o `evidence-researcher` declarar a lacuna. Achado: a figura do EMED nao estava so ausente, estava **desatualizada** (lista o estadio IIC, extinto em 2014).
Resumos de SUA e APS receberam as licoes dos erros do dia (Siamese Twins) -- SUA 226->248 linhas e 3->15 armadilhas; APS ganhou a escada de territorios e o SMED, ambos ausentes do acervo inteiro.

### 3. Cards -- 60 drenados, divida FSRS zerada
| Bucket | n | Retencao |
|---|---|---|
| Atrasados | 15 | **87%** |
| Hoje | 14 | 79% |
| **Erros frescos** | 8 | **25%** |
| Novos (estreia) | 23 | 22% |

Retencao sem estreia: **70%**. Distribuicao: 31x4, 6x3, 6x2, 17x1. Atrasados remanescentes: **1**.
Os 10 relearning travados desde a s166 destravaram e saíram a 90%.
**Achado central:** o consolidado segura a ~85%, mas os erros analisados horas antes voltaram a **25%** -- analise + resumo + card cunhado nao sao retencao.
Revisao Direcionada de fechamento em 3 eixos (a pedido do usuario): SUA/PALM-COEIN + manejo do sangramento · o paciente etilista (16 erros do historico) · inversao Wilms x neuroblastoma.

### 4. Engenharia
- **Substrato `canonico` da governanca de evidencia trocado.** O `pubmedmcp` do `.mcp.json` morreu (`CONNECTION_CLOSED`); o usuario instalou o plugin `pubmed@life-sciences`. `evidence-governance.md` para **v1.1**: 7 tools nomeadas, **obrigacao de atribuicao** (PubMed + DOI como link), **boundary abstract-only com teto elevado** (tentar `get_full_text_article` via PMCID antes de fechar NAO-VERIFICAVEL), regra-mae de busca reescrita (`get_article_metadata` no lugar de `term="<PMID>[uid]"`, ler `query_translation`), lapide do server antigo. Agente `evidence-researcher`, skill `/pesquisar-evidencia`, espelho e AGENTE.md §6 atualizados. `.mcp.json` limpo (gitignored).
- **Teste do plugin fechou duas questoes reais:** o FIGO 2025 (PMID 40908761) que o `evidence-researcher` nao conseguira ler por paywall -- confirmando que o estadiamento 2014 segue vigente -- e a auditoria da afirmacao "ATB contraindicado em STEC" (metanalise Freedman 2016, `10.1093/cid/ciw099`: OR 1,33 no conjunto total, **2,24** so nos estudos de baixo risco de vies), registrada como nuance no resumo de Diarreia.
- **F79 RESOLVIDO:** check 6 `[SPEC]` em `audit_resumos.py` (5 proibicoes duras que o linter era cego a ver) + `tools/test_audit_resumos.py` inscrita em `pytest.ini`. Passivo medido: 22 arquivos, nascendo WARN.
- `doc_drift.py`: prefixo `plugin_` em `MCP_EXTERNOS` + teste de regressao.

## Padroes de erro identificados
- 🔴 **O no do fluxograma nao e lido -- 3 disparos no mesmo dia** (SUA agudo: estabilidade APOS o volume). Conectado por evidencia ao erro #947 (Trauma, TC antes da via aerea) e a fraqueza nº 3 (Sindromes Hipertensivas). **3 areas**, e os erros em direcoes opostas (escalar demais / de menos) provam que nao e vies de escalada, e leitura do no.
- 🔴 **Achado saliente sequestra o diagnostico -- 4 disparos** (Salmonella, APLV, macula rubra, "cruza a linha media").
- 🔴 **Inversao cristalizada Wilms x neuroblastoma** -- 2 cards independentes, mesma direcao errada.
- 🔴 **Carbamazepina como "a proibida" na SAA pela 3a vez** (#335, #847, card #560).
- **Pergunta composta:** parou na 1a metade em 4 cards.
- 🃏 **7 cards com defeito de autoria** identificados no drill, 4 sinalizados pelo proprio usuario.

## Artefatos criados/modificados
- 10 resumos novos/expandidos + `resumos/GO/[GIN] Sangramento Uterino Anormal.md` + `resumos/Preventiva/Atencao Primaria a Saude no Brasil.md`
- `core/contracts/evidence-governance.md` (v1.1) · `.claude/agents/evidence-researcher.md` · `.claude/commands/pesquisar-evidencia.md` + espelho · `AGENTE.md` §6
- `tools/audit_resumos.py` (check 6) · `tools/test_audit_resumos.py` (novo) · `pytest.ini` · `tools/doc_drift.py` · `tools/test_doc_drift_refs.py`
- `AUDITORIA_MEDHUB.md` (F78, F79, F79b, F80) · `HANDOFF.md` · `history/session_169.md` + `INDEX.md`

## Decisoes tomadas
1. **Mix de cards 08-13/09:** agendado + intake DIRIGIDO a Cirurgia Infantil (~40-50 cards), nao os 190 que a folga permitiria -- estreia rendeu 22% de retencao e volume indiscriminado infla a fila.
2. **ENAMED 13/09 nao pede taper** de carga; e termometro desde a s159.
3. **Server `pubmedmcp` removido do `.mcp.json`** (autorizado pelo usuario), com lapide no contrato.
4. **Regra nova do linter nasce WARN** (politica warning-first mantida) -- 22 arquivos ficam visiveis como divida.

## Proximos passos
- Drillar os 41 cards de 08/09 cedo (23 sao os erros desta sessao).
- Seguir o sprint: faltam ~630 das 725q ate 12/09.
- Reforja acumulada: 7 da s169 + 13 da s167 + 18 anteriores.
- F80 (fuso) e F79b (dexis) abertos no ledger.
