## Audit Report: sprint-final-uerj part-5 (boot e recomendador falam o hoje do sprint)

> Commit auditado: `70b1109`. Auditor: subagente (s226, 13/10/2026). Escopo extra pedido pelo principal:
> frase do Ritmo do Painel conta o sprint (`tools/painel.py`) -- fora do anti-escopo original, declarado
> no commit, aceito como acréscimo do principal.

**Verdict: PARTIAL**

### DoD Checklist
- [x] 1. `day_plan` bloco Cronograma com sprint -- `_linhas_sprint` (tools/day_plan.py ~L1235) via
  `plano.resumo_sprint`; `--panorama` idem (`plano.render_panorama_sprint`). Execução real:
  "Hoje (13/10): 3 tarefa(s) · 76 questoes", cada tarefa com "aba Listas do hub"/aula-base, "Amanha (14/10)"
  em 1 linha, "Fora do sprint: 37 tarefa(s) · 997q". Sem `dia_plano` -> bloco antigo (`elif c:`).
- [x] 2. Recomendador -- ramo `sprint is not None` em `recomendar_dia`: simulado do dia pela agenda, questões =
  soma das tarefas de hoje; R3/R4-fórmula só no `else`; R5 (fsrs 150) segue. Real: "questoes 76 ... 3 tarefa(s)
  do plano de hoje do sprint". Teste `test_recomendador_com_sprint_le_o_dia_da_agenda`.
- [x] 3. `test_boot_painel_listas_mesmo_hoje` (tools/test_plano_dia.py:424) -- ids e ordem iguais em
  `day_plan._cronograma_hoje`, `painel._bloco_sprint`, `hub.dados_sprint`, texto do boot e do panorama.
- [x] 4. `_CONTRATO` pede "HOJE DO SPRINT" (tools/hooks/memory_boot.py:~199); `test_boot_entrega_o_panorama`
  atualizado e verde (assert "ONDE ESTAMOS" not in).
- [~] 5. Suíte verde: `pytest tools/ -q` = 1750 passed. cronograma-contract v1.6 com cláusula + lápide em linha
  própria + changelog; termo cadastrado em MEMORIA-AUDITORIA §12. `auto_check --changed` NÃO re-rodado por
  este auditor (fora do perímetro autorizado) -- conferir pelo principal.

### Foco (a) §10.10
- cronograma-contract: declarar (Integração "Boot com sprint" + changelog v1.6) OK; lapidar (⚰️ em linha
  própria, "Suspensa ... 13/10 -> 31/10") OK; cadastrar (`TERMO-REVOGADO: ONDE ESTAMOS — semana do plano`) OK.
  Portador lido no ato (`memory_boot._CONTRATO`) lapidado em comentário ⚰️. AGENTE §2 passo 4 atualizado.
- orquestracao-contract: declara "R3/R4 com sprint" (L56-59) como SUSPENSÃO condicional, não revogação --
  lápide/termo não exigidos. Falta bump de versão (segue 1.0) e changelog. LOW.
- Tensão: a lápide diz "13/10 -> 31/10", mas o código não tem data de fim (ver b) -- a lápide afirma o que o
  código não faz.

### Foco (b) "depois de 31/10 o dia_plano fica e tudo rola para hoje"
Gravidade real: **MÉDIA-ALTA a partir de 02/11** (01/11 é a prova). `plano.agenda_sprint` (tools/plano.py
~L1704) só devolve None se NENHUMA linha tiver `dia_plano`; nada olha `sprint.json.fim`. Efeitos, todos pela
mesma fonte (boot, Painel "Plano de hoje", aba Listas, recomendador, Ritmo):
1. toda pendente com `dia_plano` <= hoje vira "hoje" sem teto (sobra do sprint inteira num dia; recomendador
   manda fazê-la toda, sem capacidade);
2. a Fase 2 / extensivo (sem `dia_plano`, sem marca "fora") some do boot e das telas -- o "hoje" fica cego ao
   plano real pós-prova;
3. R3/R4 seguem suspensos indefinidamente; o Ritmo continua dizendo "Cumprindo o sprint, você chega a X em
   01/11" com 01/11 no passado;
4. as tarefas "fora do sprint" seguem rotuladas assim.
Remédio mínimo: em `agenda_sprint`, tratar como sem sprint quando `hoje > fim` (param `fim=None`, os chamadores
passam `fim_do_sprint(linhas)`; ilegível = comportamento atual), mantendo a função pura. Um guarda cobre as 4
telas. Teste: banco sintético com `dia_plano` e `hoje=2026-11-02` -> `agenda_sprint is None`, boot volta ao
bloco da semana. Esforço S. Alternativa operacional (pior): um `--sprint --limpar` no dia 01/11.

### Foco (c) conta 9.306
Confere. Acumulado 7.817 (`performance.py` e linha Meta do boot); `q_sprint` = 76 (hoje) + 1.413 (14/10-31/10,
18 dias, somados à mão do `--panorama --json`) = 1.489, dos quais 297 simulados (100+97+100); 7.817 + 1.489 =
9.306; 10.000 - 9.306 = 694 abaixo. Painel: "1.192 nas listas e 297 nos simulados ... 9.306 em 01/11 (694 abaixo)".
Ressalva: a tarefa #5426 (MFC, leitura) conta 0q -- correto; a prova de 01/11 em si não entra.

### Pattern Compliance
- [x] Fonte única do "hoje" (`agenda_sprint`) -- reusada, não duplicada; `resumo_sprint` PURA.
- [x] Degradação declarada (None = bloco antigo) com teste.
- [x] Lápides ⚰️ em comentário/linha própria (day_plan `_linhas_sprint`, memory_boot, recomendador).
- [ ] Pequena duplicação: `_comparar_com_meta` (day_plan) e `_comparacao_meta` (painel) e
  `_linha_tarefa_sprint` (plano) vs o laço de `_linhas_sprint` (day_plan) -- dois renders quase iguais. LOW.

### Critical Gate
Clean -- nenhuma operação destrutiva, segredo, exec dinâmico ou PII no diff.

### Defeitos
1. tools/plano.py:~1717 (`agenda_sprint`) -- sem corte por `fim` do sprint; pós-31/10 tudo rola para hoje e a
   Fase 2 some (foco b). MÉDIA-ALTA (latente até 02/11).
2. core/contracts/cronograma-contract.md:94 -- lápide promete "13/10 -> 31/10" que o código não cumpre. MÉDIA
   (fecha junto com o 1).
3. tools/day_plan.py:~880 -- recomendador com sprint soma o "hoje" sem teto de capacidade; se o `--sprint` não
   for re-rodado, a rolagem acumula. BAIXA (declarado: "até o próximo --sprint").
4. core/contracts/orquestracao-contract.md:5 -- sem bump/changelog para a cláusula nova. BAIXA.
5. INFO: durante esta auditoria `artifacts/painel.html` apareceu modificado (14:43:28, só carimbo + frase do
   Ritmo nova), com o pytest rodando; day_plan/plano/performance não escrevem esse arquivo. Possível teste
   que regenera o painel real -- conferir e restaurar (`git checkout artifacts/painel.html`) se indesejado.
   Não tocado por este auditor.
6. INFO: worktrees velhas em `.claude/worktrees/agent-*` ainda com o termo revogado (fora do gate? conferir).

### Gaps / Incremental Prompt Pack
- Gap 1 (S): `agenda_sprint(linhas, hoje, fim=None)`: `if fim and hoje.isoformat() > fim: return None`;
  chamadores (`resumo_sprint`, `painel._bloco_sprint`, `hub.dados_sprint`) passam `fim_do_sprint(linhas)`.
  Teste `test_sprint_vencido_volta_ao_bloco_da_semana` (hoje=02/11). Manter PURA; ajustar a lápide do
  cronograma-contract para citar o guarda.
- Gap 2 (S): orquestracao-contract v1.1 + changelog.
- Gap 3: rodar `python tools/auto_check.py --changed` e anexar o PASSED.
