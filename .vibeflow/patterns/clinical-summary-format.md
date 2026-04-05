---
tags: [clinical-writing, resumo, formatting, markdown, exam-prep, armadilhas]
modules: [resumos/, .claude/commands/]
applies_to: [resumos, markdown-docs]
confidence: inferred
---
# Pattern: Clinical Summary Format

<!-- vibeflow:auto:start -->
## What
Mandatory structure and formatting rules for all clinical summaries in `resumos/`. Every file must follow the 80/20 benchmark: 80% assertiveness (condutas, scores, criteria), 20% clinical didactics. Enforced by `.claude/commands/estilo-resumo.md`.

## Where
All `.md` files under `resumos/` — organized by specialty:
- `resumos/Clínica Médica/<Specialty>/`
- `resumos/Cirurgia/`
- `resumos/GO/`
- `resumos/Pediatria/`
- `resumos/Preventiva/`

## The Pattern

**Frontmatter (required on every file):**
```yaml
---
type: knowledge
area: Clínica Médica
especialidade: Cardiologia
status: active
aliases: [IC, insuficiência cardíaca]
---
```

**Heading hierarchy:**
```markdown
# Título do Tema (H1 — one per file, no emojis)

## 1. Seção Principal (H2 — numbered sections, no emojis)

### 1.1 Subseção (H3 — optional, no emojis)
```

**Bullet style — assertions first:**
```markdown
- Critério A: valor/conduta
  - Detalhe específico com mecanismo se relevante
- **Conceito chave** em negrito quando fundamental
- ⭐ Item de alta cobrança em prova
```

**Exam traps (inline, in relevant section):**
```markdown
- Conduta X: fazer Y
  - ⚠️ Padrão de prova: perguntas costumam omitir o contexto Z para induzir ao erro
```

**Armadilhas section (always last, cumulative — never delete):**
```markdown
## N. Armadilhas e Padrões de Prova

- 🔴 Descrição da armadilha mais cobrada
- 🔴 Segunda armadilha, acumulada da sessão de análise anterior
```

## Rules
- H1/H2/H3 headers: **no emojis, no backticks**
- Bullets: `⭐` for fundamental items, `⚠️ Padrão de prova:` inline for exam traps, `🔴` only in armadilhas section
- **No `✅`/`❌` bullets** anywhere in the file
- **No `estilo:` field** in frontmatter
- **No editorial footers** (e.g., "Atualizado em sessão X")
- **No informal language** ("vamos lá", "encher balde", etc.)
- Armadilhas section is cumulative — only add/refine, never delete old ones
- 80/20 benchmark: most content is direct condutas and criteria; physiology only to explain "why" for high-yield items
- Tables permitted only for comparative data (e.g., drug dosing) — not for narrative content

## Examples from this codebase

File: `resumos/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md`
```markdown
---
type: knowledge
area: Clínica Médica
especialidade: Cardiologia
status: active
aliases: [IC, insuficiência cardíaca, heart failure]
---

# Insuficiência Cardíaca

## 1. Definição e Epidemiologia
- Síndrome clínica de débito cardíaco inadequado para demandas metabólicas
  - Causa mais comum de internação em >65 anos no Brasil
- ⭐ Prevalência: 2-3% da população geral; 10% em >70 anos

## 2. Classificação pela FEVE
- **ICFEr** (FEVE < 40%): sistólica — maior arsenal terapêutico com redução de mortalidade
- **ICFEi** (FEVE 40-49%): intermediária — conduta similar à ICFEr
- **ICFEp** (FEVE ≥ 50%): diastólica — tratamento sintomático (diurético + controle da FC)
  - ⚠️ Padrão de prova: ICFEp não tem benefício demonstrado com IECA/BRA em mortalidade

## 7. Armadilhas e Padrões de Prova
- 🔴 Confundir edema pulmonar agudo (ortopneia + B3) com derrame pleural (macicez)
- 🔴 Na IC descompensada, nunca iniciar betabloqueador — apenas manter se já em uso
```

File: `resumos/GO/Assistência ao Parto.md` (reference for GO and procedure-heavy summaries)
```markdown
## 3. Manobras do Parto Normal

### 3.1 Rotação Interna
- Occipito-anterior: rotação espontânea de 45° no plano +2
- ⭐ Indicação de manobra manual: falha de rotação após período expulsivo prolongado

### 3.2 Deflexão e Desengajamento
- Deflexão progressiva ao nível do suboccipital
- **Manobra de Ritgen modificada**: protege o períneo, evita lacerações de 3°/4° grau

## 5. Armadilhas e Padrões de Prova
- 🔴 Cardiotocografia com desacelerações tardias = insuficiência uteroplacentária, não compressão de cordão
```
<!-- vibeflow:auto:end -->

## Anti-patterns
- `✅`/`❌` bullets were found in older resumos — these violate the spec and should be replaced
- Headers with emojis (e.g. `## 🫀 Coração`) exist in a few legacy files — migrate on edit
- Some files lack frontmatter — add when touching the file
- Informal closings like "Resumo atualizado na sessão 052" — remove on sight
- **`type: resumo`** — older/legacy frontmatter value; correct is `type: knowledge` (confirmed in gold-standard IC.md and all newer files)
- **`status: completo` or `status: ativo`** — legacy values; correct is `status: active` (English, active state)
- `Demências.md` uses both deviations (`type: resumo`, `status: ativo`) — update on next edit
