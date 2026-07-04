# Sessão 056 -- Pipeline Flashcards v5

**Data:** 2026-03-27
**Foco:** Infraestrutura -- migração e regeneração do pipeline de flashcards

---

## Resumo

Implementação completa do plano aprovado na sessão anterior para corrigir o pipeline de flashcards degradado. O problema raiz era que `insert_questao.py` gerava perguntas por pattern matching heurístico fraco e armazenava apenas `frente`/`verso` monolíticos, sem campos semânticos estruturados.

## O que foi feito

### Novos scripts em tools/
- **`backup_db.py`**: backup com `PRAGMA integrity_check` antes de qualquer migração
- **`migrate_flashcards.py`**: adiciona 8 colunas à tabela `flashcards` (idempotente)
- **`regenerate_cards.py`**: regeneração heurística de todos os cards com questao_id; suporta `--export`/`--apply` para loop qualitativo; LEFT JOIN para orphaned tema_id; clean() para tratar N/A; fallback de resposta quando alternativa_correta < 8 chars
- **`audit_cards.py`**: relatório de qualidade (legacy/heuristic/heuristic_flagged/qualitative/UI fallback)

### Piloto qualitativo
- 20 cards `elo_quebrado` com dados ricos exportados via `--export pilot_cards.json`
- Gerado `pilot_output.json` com 5 campos estruturados de alta qualidade por card
- Aplicado via `--apply pilot_output.json` com `quality_source='qualitative'`

### Auditoria final
```
Total:           277
Legacy:          0
Heuristic OK:    219
Heuristic flagged: 38
Needs qualitative: 169
Qualitative:     20
UI fallback:     29
```

### Atualizações em arquivos existentes
- **`insert_questao.py`**: 5 novos args opcionais de campos estruturados; sem emojis no verso; INSERT atualizado para as novas colunas
- **`app/pages/2_estudo.py`**: DB_PATH absoluto (resolve bug de cwd); Tab1 query corrigida (`habilidades_sequenciais` / `o_que_faltou` vs colunas inexistentes); Tab2 render semântico em 3 blocos (`st.success`/`st.info`/`st.warning`) quando campos estruturados presentes
- **`.claude/commands/analisar-questao.md`**: Section 8 atualizada para 4 entregas (inclui 5 campos estruturados); Section 9 com novos args e aviso contra unicode/emojis no CLI

## Bugs corrigidos
1. **`N/A?` como pergunta**: heurística não tratava 'N/A' como valor vazio
2. **`resp: D` single-letter**: alternativa_correta apenas com letra -> fallback para explicacao
3. **LEFT JOIN taxonomia**: 205 cards com tema_id orphaned eram silenciosamente descartados
4. **UnicodeEncodeError no dry-run**: print usava `encode('ascii', 'replace')` para saída segura no Windows
5. **DB_PATH relativo em 2_estudo.py**: quebrava quando cwd ≠ raiz do projeto
6. **Tab1 query com colunas inexistentes**: sempre caía no fallback N/A

## Commits
- `20c70d0` -- sessao 056: pipeline flashcards v5
