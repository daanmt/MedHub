---
description: "Linter de qualidade para resumos em Temas/. Verifica conformidade com o padrão MedHub: seção Armadilhas de Prova, ausência de tabelas, presença de marcadores visuais."
type: skill
layer: commands
status: canonical
---

# Skill: Auditar Resumos

Executa o linter `Tools/audit_resumos.py` sobre todos os arquivos `.md` em `Temas/`.

---

## Invocação

```bash
python Tools/audit_resumos.py
```

Não requer argumentos. Varre `Temas/**/*.md` recursivamente.

---

## O que é verificado

| Verificação | Severidade | Critério |
|---|---|---|
| Seção "Armadilhas de Prova" | **Crítico** | Deve existir um heading `## N. Armadilhas de Prova` |
| Tabelas ASCII | **Crítico** | Linhas com padrão `\|.*\|.*\|` são proibidas |
| Emojis em headers | **Crítico** | Headings H1/H2/H3 não podem iniciar com emoji (🧭🕒🚨🟢🟡🔵 etc.) |
| Bullets `✅`/`❌` | **Crítico** | Marcadores de bullet não podem ser `✅` ou `❌` — usar `-` com negrito |
| Campo `estilo:` no frontmatter | **Crítico** | Frontmatter não deve conter campo `estilo:` |
| Rodapé editorial | **Crítico** | Arquivo não deve terminar com linhas em itálico de origem/autoria (`*Este resumo...`) |
| Marcadores visuais | Aviso | Pelo menos um de: `⚠️`, `🔴`, `⭐` |

---

## Interpretando o output

```
❌ Clínica Médica/Cardiologia/Insuficiência Cardíaca.md
   ↳ [FALTA ESTRUTURA] Seção 'Armadilhas de Prova' ausente.
   ↳ [ANTI-PATTERN] Tabela ASCII detectada (Proibido pelo estilo-resumo.md)

✅ AUDITORIA PERFEITA! Todos os resumos seguem o padrão MedHub.
⚠️  RESULTADO: 2 erro(s) crítico(s) em 1 arquivo(s).
```

- **❌ + [FALTA ESTRUTURA]** — resumo sem seção de armadilhas (crítico, corrigir)
- **❌ + [ANTI-PATTERN]** — tabela proibida presente (crítico, converter para bullets)
- **❌ + [AVISO STYLE]** — sem marcadores visuais (não crítico, mas indica resumo "passivo")

---

## Quando usar

- Após criar ou editar um resumo — confirmar conformidade
- Antes de um commit de sessão — garantir que nenhum resumo novo viola o padrão
- Periodicamente como manutenção do vault

---

## Corrigindo erros encontrados

- **Sem "Armadilhas de Prova":** adicionar seção ao final do arquivo com pelo menos um `🔴`
- **Tabela ASCII:** converter para bullets hierárquicos (ver `/estilo-resumo` para o padrão)
- **Emojis em headers:** remover o emoji do título, mantê-lo apenas no corpo do texto se necessário
- **Bullets `✅`/`❌`:** substituir por `- **Recomendado:**` / `- **Proscrito:**` ou equivalente com negrito
- **Campo `estilo:` no frontmatter:** remover a linha `estilo: ...`
- **Rodapé editorial:** remover última(s) linha(s) em itálico de origem/autoria
- **Sem marcadores:** revisar se o resumo tem highlights com `⭐`, `⚠️` ou `🔴`
