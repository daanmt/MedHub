# Session 146 -- Cronograma recalibrado + acentos/reforja de cards + Simulado 5 (37 erros) + engenharia
**Data:** 2026-08-16/17
**Ferramenta:** Claude Code (Sonnet 5, effort max)
**Continuidade:** Sessão 145 (drenagem de 100 cards + curadoria em escala)

---

## O que foi feito

Sessão em duas frentes, seladas juntas neste log porque a primeira já tinha rodado (16/08, ver commits `aff9e63`..`60bfd46`) sem log formal -- o HANDOFF ainda apontava pra s145 quando esta conversa começou.

### Frente A -- cronograma, acentos, reforja de cards (16/08, pré-conversa)

1. **Cronograma EMED S15-S30 recalibrado** contra o blueprint medido do ENAMED (não o guia ENARE, que descreve outra prova -- CM ~40% no guia vs ~27% medido). 17 blocos entram / 15 saem na janela pré-ENAMED, saldo 32x33 slots.
2. **Correção de premissa do usuário:** ENARE == ENAMED (a nota do ENAMED é usada no ENARE) -- o guia ENARE volta a ser a fonte boa de prevalência para a fila de revisão; a camada "blueprint ENAMED medido" isolada era ruído.
3. **Acentuação do `ipub.db`:** 119/120 registros de erro dos simulados com acentos restaurados (dicionário de 2.035 palavras + passe de sonnets sob invariante `sem_diacriticos(novo)==sem_diacriticos(antigo)`). 1 registro (#808) rejeitado pela invariante, pendente reprocessar à mão.
4. **Reforja de 138 cards com defeito de formulação:** 131 refeitos in-place + 7 aposentados, via `recurate_cards.py --apply` (FSRS preservado). Defeitos no baralho inteiro: 138 -> 9.
5. **Comandos recuperados:** 53 gravados no `enunciado` (39 verbatim do PDF do S2, 14 inferidos das alternativas do S4) -- 120/120 erros dos simulados 2-4 passam a ter comando isolado.
6. Escrito `docs/handoff-s146-continuacao.md` como ponte por esgotamento de contexto -- absorvido e removido no fechamento desta sessão (pendências reais levadas pro `HANDOFF.md`).

### Frente B -- Simulado 5: correção primária, análise dos 37 erros, engenharia (17/08, esta conversa)

7. **Correção primária do Simulado 5** a partir de 5 PDFs (export "Estratégia MED", mesmo formato do S2). Bug de parsing descoberto e corrigido: o rótulo "Questão N" às vezes vaza numa linha ANTES do marcador `qid STATUS pct% ACERTARAM` (não depois, como no S2) -- resolvido com um buffer de lookahead (`parse_simulado5_v2.py`, lógica depois portada pro `autopsia_simulados.py`). Placar inicial: 61/98 confirmadas (Q20 e Q100 ausentes -- PDF truncado nas duas pontas). Usuário confirmou Q20 e Q100 = CERTA -> **placar final 63/100**.
8. **Volume registrado:** `sessoes_bulk` sessão 146 / área `Simulado`, 100 feitas / 63 acertos (dois registros: 98/61 inicial + 2/2 via `--acumular`).
9. **As 37 erradas divididas em 4 blocos** (~9 cada) e processadas por **4 subagents fork em paralelo**, cada um rodando o protocolo completo de `/analisar-questao` (habilidades sequenciais, elo quebrado, consulta ao deck EMED, `insert_questao.py`, edição de resumo quando a armadilha era nova). Resultado: **40 cards atômicos**, **`questoes_erros` #815-851**, **11 resumos tocados**.
10. **4 questões vieram sem vinheta no PDF** (bloco "Texto de apoio" colapsado no export: Q22, Q58, Q69, Q99) -- o usuário colou o texto completo no chat, que os subagents persistiram; o `autopsia_simulados.py` foi ajustado para preferir esse texto rico quando o do PDF vem curto demais (<150 chars).
11. **Reconciliação dos arquivos que o usuário reorganizou** fora desta conversa: `PLAYBOOK_EXECUCAO_PROVA.md` movido pra `docs/` (link quebrado em `ESTADO.md` corrigido); `HANDOFF_RESPOSTA_AI_ENG_FLASHCARDS.md` removido (conteúdo já absorvido no trabalho aplicado da Frente A); `AUDITORIA_MEDHUB.md` -- inicialmente removido, **restaurado a pedido do usuário** após eu sinalizar que tinha achados abertos (F21/F35/F36-ALTA/F37/F38/F39) que se perderiam.
12. **Achados técnicos resolvidos:**
    - `.venv` do projeto estava dessincronizado de `requirements.txt` -- faltavam `fsrs`, `langgraph`, `langgraph-checkpoint-sqlite`, `langmem`, `langchain-anthropic`, `anthropic`, `chromadb` (7 de 13 pacotes). Um dos subagents bateu em `ModuleNotFoundError: No module named 'fsrs'` no meio do trabalho e contornou com SQL direto (resultado final verificado como correto). Sincronizado via `pip install`.
    - `.claude/commands/analisar-questao.md` documentava `--area` como uma das "5 grandes áreas" (Cirurgia/Clinica Medica/Pediatria/GO/Preventiva), mas o banco inteiro (histórico, não só hoje) já usa ~20 subespecialidades soltas, com `GO`/`Ginecologia`/`Obstetrícia` fragmentados em 3 valores do mesmo domínio. Skill corrigida para refletir a prática real + recomendação de preferir o específico a `GO` daqui pra frente (sem reclassificar retroativamente). Espelho regenerado via `sync_skills.py`.
13. **Autópsia dos Simulados estendida de 3 para 4 provas.** `tools/autopsia_simulados.py` e `tools/autopsia_template.py` generalizados (SIMS/SIMK ganham "S5"; grid do topo fixo em 3 colunas corrigido para 4, com breakpoint 2x2 novo); republicada no artifact existente (`.../c414a4f3-...`), 157 erros mapeados.
14. **Fila de flashcards aberta** (79 cards, 46 temas: 45 atrasados + 8 erros_frescos do Simulado 5 + 16 hoje + 10 novos) e os 8 erros_frescos apresentados -- usuário adiou a avaliação pra 18/08 (**nenhum rating gravado**).

### Volume do dia
**100 questões** (Simulado 5, 63% de acerto) -- primeiro volume desde a s143 (s144/s145 foram 100% engenharia).

---

## Padrões de erro identificados (Simulado 5, 37 erros)

- **"Escala além do necessário" é o padrão dominante -- 10/37 questões** (Q8, Q14, Q18, Q34, Q45, Q52, Q68, Q69, Q72, Q87): conduta/investigação mais complexa escolhida quando o achado pedia o passo simples (ou o oposto). Duas reincidências diretas de fraquezas já catalogadas: **hipertensivas/hidralazina sem critério de gravidade** (mesmo padrão exato desde a s086) e **gravidez ectópica** (escalada pra cirurgia com critérios de MTX presentes -- top-5 do ranking de fraquezas persistentes, 46 erros).
- **"Aplica protocolo da doença vizinha sem checar o discriminador" -- 3 instâncias**: chikungunya tratada como dengue com sinal de alarme (Q46); bronquiolite tratada como crise de asma (Q98); derrame pleural confundido com atelectasia (Q74).
- **Enunciado negativo reincidiu** (Q25 -- marcou uma alternativa verdadeira como se fosse a falsa pedida).
- **Conhecimento desatualizado/nomenclatura nova**: consenso H. pylori 2025/26 (Q88); nomenclatura ESC 2025 pra miopericardite (Q99, prefixo invertido).

## Artefatos criados/modificados

- `history/session_146.md` (este arquivo), `history/INDEX.md` -- nova entrada
- `HANDOFF.md` -- rotação completa; `ESTADO.md` -- indicador/contadores/posição atualizados
- `.claude/commands/analisar-questao.md` + `.agents/skills/source-command-analisar-questao/SKILL.md` -- doc drift de área corrigido
- `.gitignore` -- padrão do cache de simulado generalizado (`_s2_questoes.json` -> `_s*_questoes.json`)
- `tools/autopsia_simulados.py`, `tools/autopsia_template.py` -- extensão pro S5 (4 provas)
- `docs/PLAYBOOK_EXECUCAO_PROVA.md` (movido da raiz pelo usuário) -- `PLAYBOOK_EXECUCAO_PROVA.md` (raiz, removido)
- `HANDOFF_RESPOSTA_AI_ENG_FLASHCARDS.md` (removido) -- `docs/handoff-s146-continuacao.md` (removido, absorvido)
- 11 `resumos/**/*.md` com armadilha nova (Colecistite/Colangite, Melanoma, Arboviroses, Raiva-Tétano, Síndromes Pleuropulmonares, Gravidez ectópica, Síndromes Hipertensivas, CA de Mama, Mastite, Cuidados Neonatais, Princípios do SUS)
- `ipub.db` (local-only): `sessoes_bulk` +100/+63; `questoes_erros` #815-851; 40 cards + estado FSRS inicial
- `core/simulados/_s5_questoes.json` (novo, gitignored -- cache do texto verbatim do S5)
- `artifacts/autopsia-simulados.html` -- regenerado e republicado (link preservado)
- `.venv/` -- 7 pacotes instalados (não versionado)
- Memória de longo prazo: `feedback_politica_cards_diaria.md` e `project_novo_norte_multi_banca.md` atualizadas (teto de cards 40 -> 80-100/dia; ritmo de questões 55 -> 100q/dia, reconciliando o drift entre a memória e o HANDOFF de s144)

## Decisões tomadas

- `--area` em `insert_questao.py` é subespecialidade real, não uma das 5 grandes -- consultar `taxonomia_cronograma` antes de escolher.
- Cache de PDF de simulado (`core/simulados/_sN_questoes.json`) é sempre gitignored, IP da plataforma de origem.
- Quando o PDF de um simulado vem com vinheta truncada ("Texto de apoio" colapsado), o texto que o usuário cola no chat vira a fonte de verdade -- o `autopsia_simulados.py` prefere o texto do banco quando o do PDF é mais curto.
- `AUDITORIA_MEDHUB.md` continua vivo -- decisão explícita do usuário após eu sinalizar os achados abertos; não interpretar silêncio futuro como autorização pra removê-lo de novo.

## Próximos passos

Ver `HANDOFF.md`. Em resumo: amanhã (18/08) puxar 100 questões da fila e avançar a S15 (confirmar ordem no Drive antes); matar a S15 até quinta 20/08; simulado novo na sexta 21/08; fila de flashcards com 79 cards abertos (8 já apresentados, nenhum avaliado) a 80-100/dia; `tools/fila_enamed.py` com narrativa desatualizada, pendente de reescrita.
