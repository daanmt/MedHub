# HANDOFF — MedHub (Sessão 056 → 057)

## Onde paramos
Finalizada a **Sessão 056** focada em **infraestrutura do pipeline de flashcards (v5)**.

## Estado Técnico — Pipeline Flashcards v5

### Schema atualizado (`flashcards`)
- 8 novas colunas: `frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`, `quality_source`, `card_version`, `needs_qualitative`
- Rollback disponível via `ipub_backup_20260327_215403.db`

### Auditoria final
- **Total:** 277 cards
- **Heuristic OK:** 219 | **Heuristic flagged:** 38 | **Qualitative:** 20 | **UI fallback:** 29
- **Legacy:** 0 (todos regenerados)
- **Needs qualitative:** 169 (armadilhas + cards com pergunta fraca)

### Arquivos novos
- `Tools/backup_db.py` — backup com integrity_check antes de migrações
- `Tools/migrate_flashcards.py` — ALTER TABLE idempotente
- `Tools/regenerate_cards.py` — regeneração heurística + aplicação de piloto qualitativo
- `Tools/audit_cards.py` — relatório de qualidade

### Arquivos atualizados
- `Tools/insert_questao.py` — 5 novos args estruturados (`--frente_pergunta`, etc.), sem emojis, INSERT atualizado
- `app/pages/2_estudo.py` — DB_PATH absoluto, Tab1 query corrigida, Tab2 render semântico com 3 blocos
- `.claude/commands/analisar-questao.md` — Section 8 com 4 entregas obrigatórias (inclui 5 campos estruturados)

## Próximos Passos (Sessão 057)
1. Continuar meta volumétrica (~369 questões para meta de Março de 3.000 q)
2. Próximo tema sugerido: **Assistência ao Puerpério** ou **DIP / Sangramentos na Gestação** (GO)
3. Fase qualitativa futura: processar os 169 cards `needs_qualitative=1` em lotes via `--export`/`--apply`

---
*Assinado: Claude Code (2026-03-27)*
