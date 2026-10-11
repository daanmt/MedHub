---
tags: [clinical-writing, resumo, formatting, markdown, exam-prep, armadilhas]
modules: [resumos/, .claude/commands/]
applies_to: [resumos, markdown-docs]
confidence: inferred
status: active
canonical_source: .claude/commands/estilo-resumo.md (SSOT, enforced by tools/audit_resumos.py) —
  this pattern is a gen-spec-time mirror, not the SSOT; on conflict estilo-resumo.md wins
last_verified: 2026-08-25
---
# Pattern: Clinical Summary Format

<!-- vibeflow:auto:start -->
## What
Estrutura e formatação obrigatórias de todo resumo clínico em `resumos/`, com o benchmark 80/20 (80% assertividade: condutas, scores, critérios; 20% didática do porquê clínico). A SSOT é `.claude/commands/estilo-resumo.md`; o linter `tools/audit_resumos.py` (rodado pelo `tools/auto_check.py`) mede a estrutura e o encoding. Este pattern é espelho: em conflito, o `estilo-resumo.md` vence.

## Where
Os `.md` de `resumos/` (contagem só pelo contador canônico, `python tools/cobertura_conhecimento.py`; nunca fixar número), por grande área:
- `resumos/Clínica Médica/<Especialidade>/`
- `resumos/Cirurgia/`, `resumos/GO/`, `resumos/Pediatria/`, `resumos/Preventiva/`, `resumos/Otorrino/`
Os PDFs-fonte do EMED moram nas mesmas pastas (retidos, gitignored).

## The Pattern

**Frontmatter (`AGENTE.md` §5.2):**
```yaml
---
type: knowledge
area: Clínica Médica
especialidade: Cardiologia
status: active
aliases: [IC]
---
```

**Hierarquia:** `# Nome do Tema` (H1 único, sem metadata de fonte) -> `## 1. Seção` (H2 numerado) -> `### 1.1 Subseção` (H3) -> `**Título em negrito:**` + bullets. Separador `---` entre seções principais.

**Marcadores no corpo:** `⭐` (fundamental), `⚠️ Padrão de prova:` (armadilha inline), `🔴` (na seção final de armadilhas), blockquote `>` para alerta.

**Seção final obrigatória e cumulativa:**
```markdown
## N. Armadilhas de Prova

- 🔴 [armadilha 1]
- 🔴 [armadilha 2]
```

## Rules
- Sem tabelas, em nenhum tamanho ou formato: converter em bullets hierárquicos. O linter acusa linha `| ... | ... |`.
- Sem fluxograma ASCII em bloco de código: condicionais em texto (`-> se X:`, `-> se não:`).
- Sem LaTeX inline (`$...$`, `\rightarrow`) nem `→`, `—`, `–`: usar `->`, `--`, `-`, `<=`.
- Sem emoji em H1/H2/H3; emoji só inline como marcador.
- Sem `✅`/`❌` como bullet: `- **Conduta recomendada:**` / `- **Proscrito:**`.
- Frontmatter só com `area`, `tema`, `type`, `especialidade`, `status`, `aliases`; sem `estilo:`. O linter cobra `type`, `area`, `especialidade`, `status` (WARN).
- Sem rodapé editorial, sem header de metadata (fonte, autor, ano), sem linguagem informal, sem citar questão no texto ("Q1 na prova").
- A seção "Armadilhas de Prova" (com ou sem número) é obrigatória (BLOCK no linter) e cumulativa: nunca apagar armadilha antiga.
- Especificidade técnica: classificação oficial ou critério quantitativo em vez de descrição genérica (AAST Grau IV, não "lesão grave").
- Conteúdo decisório segue `core/contracts/evidence-governance.md`: conflito banca x evidência vira 🔴 armadilha banca-dependente com fonte.
- Antes de encerrar: `python -X utf8 tools/auto_check.py --changed` com exit 0.

## Examples from this codebase

File: `resumos/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md`
```markdown
# Insuficiência Cardíaca (IC)

## 1. Definição e Epidemiologia
- **Conceito Base:** Síndrome clínica com baixo débito cardíaco (baixo fluxo) e/ou pressões de enchimento anormais (congestão).
- **Tradição em Provas:** 1ª causa de internação no Brasil.
- **Etiologia Nacional:** Isquêmica lidera, mas Doença de Chagas chega a 40% na Região Norte.

## 2. A Bússola: Classificação por Fração de Ejeção (FEVE)
O Ecocardiograma (método de Simpson) divide a IC em três caminhos de tratamento absolutos.
- **ICFEr (Reduzida) -- FEVE < 40%:**
  - O defeito é na **contratilidade** (sístole). O músculo estirou.
```

File: `resumos/GO/Assistência ao Parto.md` (referência de obstetrícia no `estilo-resumo.md`)
```markdown
### 9.2 Prolapso de Cordão

- **Definição:** exteriorização do cordão antes da apresentação fetal -> compressão vascular -> sofrimento fetal agudo.
- **Conduta:** cesárea de emergência. Enquanto prepara: elevar manualmente a apresentação para aliviar compressão.
- ⚠️ Padrão de prova: **circular de cordão ≠ prolapso**. Circular NÃO contraindica parto vaginal.

## 12. Armadilhas de Prova

- 🔴 **Critério 1 cm/hora abandonado:** não indicar ocitocina nem cesárea apenas por não atingir 1 cm/h -- evolução do parto eutócico é heterogênea.
```
Divergência na própria referência: o frontmatter de `Assistência ao Parto.md` ainda é o legado (`type: resumo`, `status: ativo`, mais `tema:`).
<!-- vibeflow:auto:end -->

## Anti-patterns
- `✅`/`❌` bullets were found in older resumos — these violate the spec and should be replaced
- Headers with emojis (e.g. `## 🫀 Coração`) exist in a few legacy files — migrate on edit
- Some files lack frontmatter — add when touching the file
- Informal closings like "Resumo atualizado na sessão 052" — remove on sight
- **`type: resumo`** — older/legacy frontmatter value; correct is `type: knowledge` (confirmed in gold-standard IC.md and all newer files)
- **`status: completo` or `status: ativo`** — legacy values; correct is `status: active` (English, active state)
- `Demências.md` uses both deviations (`type: resumo`, `status: ativo`) — update on next edit
