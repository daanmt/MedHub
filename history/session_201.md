# Session 201 -- ordem do /ai-eng fechada (F133-F137, objetivos, render, estados), caminho PDF e a aba Listas dividida em Questões | Simulados

**Data:** 2026-09-26 (sábado, ~14h50 -> em curso) - **Ferramenta:** Claude Code (Opus 5.5 1M) - **Continuidade:** `session_200.md` - **Observada pelo /ai-eng** (`ai-eng-59`, presença e checkpoints no `history/exchange-log.jsonl`)

---

## O que foi feito (na ordem do veredito do /ai-eng)
1. **Ledger F133 / F134 / F135** antes de qualquer código (`e0e1ea1`). De passagem: `/banco-emed` ainda dizia que o conteúdo do professor das 4 listas da s197 "não se apaga" -- morto pela decisão (e); lápide + TERMO-REVOGADO.
2. **F134** teste de PERTURBAÇÃO (`DROP COLUMN` -> `--exportar` mantém 3/3 soluções) e **F133** teste de PROPRIEDADE (chaves lidas do `hub.html`, doc pelo `--registrar` real, controle negativo); os dois provados VERMELHOS contra o código de `da62e95^` (`3217bff`).
3. **#5** lista fechada de objetivo = `core/objetivos.json`, lida pelo brief e por `db.solucao_v2_problemas`; o writer valida v1 e v2; os 91 objetivos do banco cabem (`cc30c57`).
4. **#6** `tools/test_hub_render.py`: `qzSolucao` extraída do template e rodada em node, 1 golden por estado + PROVISÓRIA (`42b7bfe`).
5. **#7** amostra de leitura no `--solucoes` (divergentes + 2 aleatórias estáveis); **#8** estado por elo = só o brief §Estado por elo, gate de paridade com a página; **#4** autoridade do diagnóstico = `analises/*`; **#9** as 7 órfãs fechadas, catraca 134 -> 127 (`6b33f94`).
6. **F136** (numerado pelo /ai-eng): HANDOFF no commit dispara a suíte no pre-commit e o `suite **N**` tem de ser o medido (`0661b2b`).
7. **Pedido do operador (~15h40):** *"o bloco de listas precisa ser dividido entre questões e simulados. já temos as questões da semana, bem como já temos os simulados da uerj"* -> **caminho PDF** `tools/prova_pdf.py` (caderno UERJ -> `questoes/*`, tudo ou nada; golden das 6 provas, perturbado, timeout, figuras 3/3 contra o mapa, mutação 3/3) + aba Listas com o seletor **Questões | Simulados** (fim do simulado por bloco + tempo total, aviso de figura) + Chrome REVOGADO pelos 3 passos (F135 RESOLVIDO) (`d2e2bcf`).
8. **F137** (achado no backup antes de ingerir): a suíte fazia backup REAL a cada rodada (`backup_db.py --help` sem argparse) e a rotação keep-5 apagou os pontos de retorno do dia -- fix + propriedade na varredura de CLIs (`1f42d9d`).
9. **Dados:** 5 simulados pendentes (UERJ 2021, 2022, 2024, 2025, 2026 = 417 questões; 2025 sem as 3 anuladas) ingeridos com dry-run + `--expect` e semeados no hub (9 lotes, 970/5000 docs); privacidade conferida com `as_level: interact`. Atalho "resolver no hub" no painel e no quadro para simulado que já está no banco (`ecdbe32`). **Hub Version 33** (copiado do resultado da tool).
10. **Gates do operador** (worktrees órfãos + resíduo do conteúdo do professor em `tmp/`): feitos com o OK dele.

## Decisões
- Simulado = tarefa do plano com `area = Simulado`; lista no hub = `t<tarefa>` (t1793 2021, t1794 2022, t892 2024, t891 2025, t890 2026). O mesmo pipeline das listas (`emed_questoes`, `listas/*`, `questoes/*`) -- sem modelo novo.
- Figura: sinalizada com a página do caderno, não desenhada (afeta 2025 Q52 e 2026 Q58). Anulada: sai da prova, declarada.
- O mapa temático da UERJ é SPOILER: não entra no hub; abre só na Autópsia, depois da prova.
- Simulado resolvido = UMA linha `--area Simulado` com o acerto por bloco na observação (formato da UERJ 2023, sessão 190).

## Achados de engenharia (ledger)
- F133 RESOLVIDO · F134 RESOLVIDO · F135 RESOLVIDO · F136 RESOLVIDO · **F137 RESOLVIDO com dano irreversível**: sumiram `ipub_backup_20260926_143813.db` (antes do apagamento (e) -- a única cópia local restante do conteúdo do professor das 91 do piloto) e `..._140307.db` (antes da reforja da s200).

## Erros meus
- O 1o patch do F136 foi por heredoc: o transporte colapsou `\\` em `\` (`\b` virou 0x08, uma f-string partiu). É a lição da memória ("regex em string RAW, patch longo = arquivo"); refeito por script no scratchpad, que passou a ser o padrão da sessão.
- O `prova_pdf.py` nasceu de protótipo medido e os testes vieram depois (declarado no commit); compensado por mutação 3/3.
- Um `rm -rf` no laço de reexecução foi barrado pelo classificador; não insisti -- pastas novas no scratchpad, sem apagar nada.

## Custo dos subagentes
Nenhum subagente nesta sessão (tudo no principal).

## Fechamento (~16h40, ordem do /ai-eng)
- F137 spec GO + 3 ALTERA: parte 1 feita (`backup_db.py --fixar`, `FIXADOS.json` com sha256; 1o fixado `ipub_fixado_20260926_162622_*`, sha256 f03b9450...); F137 volta a PARCIAL. A decisão (e) passou a "apagado SEM ponto de retorno local".
- Amostra EMED (`idoso pt1/pt2.pdf`, 31 q) SEM gabarito -> nenhum parser escrito; decisões (a)/(b) do /ai-eng viram o item 0 da s202.

## Pendências
- **Estudo:** o simulado da vez é a **UERJ 2021** (60q, ~3 h), agora na aba Listas -> Simulados. Listas da semana 2: t49 Hérnias, t40 DMG (v2 no hub).
- Nota de UX para o operador: a leitura diz "ficou entre A e C e D" com 3 letras.
- Figura desenhada (2025 Q52, 2026 Q58) quando chegar a vez; formato de lista EMED em PDF espera a 1a amostra dele.
- Proposta ao /ai-eng (`spec`): backup de antes de ato destrutivo FIXADO fora da rotação keep-5 (F137).
- (ii) advisories lote5/lote6 -- reconciliar lendo.

banco-emed: 5 simulados UERJ ingeridos (60+60+100+97+100 = 417) e semeados no hub · soluções lidas 0/0 (simulado ainda sem Solução MedHub)
