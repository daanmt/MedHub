## Audit Report: sprint-final-uerj -- part 4 (Teoria e Listas consultivas)

> Commit auditado: `8b0c4d3` (inclui o adendo do audit part-3 em `tools/painel.py`). Auditado em 13/10/2026 (s226).
> Build: `python -X utf8 tools/hub.py --build --lote tmp/player_2026-10-13a.json --out tmp/audit_p4 --quadro-estado tmp/hub_db`.

**Verdict: PARTIAL**

Suíte do commit verde; DoD 1-5 cumpridos. PARTIAL por um defeito médio de paridade (o "Fora do sprint" da aba
Listas e o do Painel não contam a mesma coisa) e dois menores.

### Suíte

- Árvore de trabalho: `1 failed` (`test_plano_dia.py::test_boot_entrega_o_panorama`) -- **contaminada** pela part-5 em
  curso (`tools/day_plan.py`, `tools/hooks/memory_boot.py`, `tools/plano.py`, `tools/painel.py` modificados, sem commit).
- Export limpo de `8b0c4d3` (`git archive` no scratchpad, cópia de `ipub.db`): `1733 passed, 10 skipped, 2 failed` =
  1745. As 2 falhas (`test_emed_api::test_token_do_repo_esta_no_gitignore`,
  `test_harness_hermetico::test_runtime_do_harness_fora_do_git`) são do export não ser repo git; no repo real passam
  (junto com test_hub*, test_painel: `279 passed`). `test_boot_entrega_o_panorama` passa no commit. **Suíte verde.**

### DoD Checklist

- [x] 1. Teoria sem semanas/atrasadas/contagem; "Revisões direcionadas · N" no topo -- `hub.html_quadro_de` passa
  `semanas=False` e `rds_nao_assinadas` (ordem `(data, slug)`); `html_rds` com `data-secao="rd"`; `aplicar` esconde a
  assinada (`hidden`) e `recontar` conta só `:not([hidden])`. Build real: "Revisões direcionadas · 5" + Biblioteca 77,
  sem "Semana"/"Atrasadas". Testes: `test_teoria_sem_semanas_com_o_backlog_de_rds_e_a_biblioteca`,
  `test_backlog_de_rds_da_mais_antiga_e_a_assinada_so_na_biblioteca`, `test_rd_assinada_some_do_backlog...`.
- [x] 2. Listas por Hoje / Próximos dias / Fora do sprint a partir de `<script id="hub-sprint">`
  (`hub.dados_sprint` = `plano.agenda_sprint`); resolvidas no fim; sem sprint, semanas -- `qzRenderSprint`,
  `test_listas_agrupam_por_hoje_proximos_dias_e_fora_do_sprint`, `test_sem_hub_sprint_as_listas_caem_nas_semanas`,
  `test_hub_sprint_no_build_e_null_sem_sprint`.
- [x] 3. Simulado com a data do sprint -- `qzQuandoSim`; `test_simulado_leva_a_data_do_sprint`.
- [x] 4. `test_listas_e_painel_mesmo_hoje` -- ids e `q_hoje` do Painel = os do hub-sprint; ordem das listas pelo `seq`.
  Build real: Hoje = #833 + #683, 76 q nos dois (o Painel tem ainda #5426, teoria de 0 q sem lista -- esperado).
- [x] 5. Artesania -- CSS novo só com tokens (`var(--tinta2)`, `--esp-5`, `--fs-legenda`), nenhuma cor literal no diff;
  `ui_capturas.py --cenas teoria,listas` em 390/768/1280: todas `ok` (sem rolagem horizontal).

### Achado 38 x 37 ("Fora do sprint")

A diferença é a **tarefa #65 "Hérnias da Parede Abdominal"** (Cirurgia, revisão, 37 q, `semana_plano = 9`,
`dia_plano NULL`, `nota NULL`), cuja lista `listas/t65` está `capturada` (aberta) no db do hub.

- `plano.montar_sprint` só considera pendentes de `SEMANAS_FASE1 = range(1, 8)` (`tools/plano.py:1614`); a #65 é
  semana 9 (Fase 2), então não recebe dia nem a marca `sprint: fora (...)`. `agenda_sprint` (`tools/plano.py:1729`)
  só põe no `fora` quem tem a marca -> a #65 some do Painel (37 = as 37 marcadas).
- A aba Listas casa listas com tarefas; lista aberta sem lugar na agenda cai no Fora com o motivo
  "sem dia no plano" (`core/templates/hub.html:2088`) -> 37 + t65 = 38.
- Unidade também difere: Listas conta LISTAS, Painel conta TAREFAS (hoje 1:1 no Fora, então não pesa no número).

Comando que mostra:

```
python -X utf8 -c "import sqlite3;c=sqlite3.connect('file:ipub.db?mode=ro',uri=True);print(c.execute('select id,tema,semana_plano,dia_plano,nota,status from plano_tarefas where id=65').fetchall())"
# + tmp/hub_db/listas/t65.json: status capturada, tarefa 65
```

**Paridade do PRD (SC2):** não viola a letra -- SC2 exige o MESMO "hoje" (tarefas e total), e o Hoje bate. Mas o
backlog diverge entre as telas e, pior, o Painel esconde uma lista aberta que ele pode resolver. A aba Listas está
mais certa; a origem está na agenda (part-3/part-5), não na part-4.

### Cobertura (1756 -> 1745)

Os testes removidos são todos de comportamento que deixou de existir: Teoria por semana (atrasadas, cabeçalho
"Semana N", contagem de questões da semana, total da Teoria = total do Painel por semana, gêmeos `_q_teoria` /
`_confere_com_o_painel`, P21 de tarefa na Teoria, resolvida mudando de grupo na Teoria). Nenhum deles cobria a aba
Listas: o agrupamento por semana das Listas nunca teve teste próprio de "Atrasadas" antes do commit. O que ainda
existe ficou coberto: `test_sem_hub_sprint_as_listas_caem_nas_semanas` (smoke: "Semana 2", sem `data-grupo`) e
`test_semana_da_vez_e_padrao_puros_seguem_para_as_listas_sem_sprint` (puras `secSemanaAtual`/`secPadraoAberta`);
`test_secoes_do_quadro_puro_segue_a_regua_da_semana` segura o ramo `semanas=True`. Sem perda real; resta um gap
fino (o fallback não afirma "Atrasadas"/`qd-atraso` nas Listas).

### Pattern Compliance

- [x] Fonte única do hoje -- `dados_sprint` reusa `plano.agenda_sprint`; motivo com a grafia do `painel._motivo_exibido`.
- [x] Tumbas ⚰️ nos testes removidos, com o porquê.
- [x] Projeção do tique inclui `html_sprint` (republica quando o dia muda) em `construir` e `decidir`.
- [x] Adendo part-3: `_rd_nao_assinada` sem a pasta do estado devolve None; datas numa chamada só de `git log`
  (`tools/painel.py`, `_datas_das_aulas`).
- [ ] INFO: `secoes_do_quadro(semanas=True)` e o ramo por semana de `html_quadro` ficaram sem chamador em produção
  (vivos só nos testes) -- código morto candidato a tumba.

### Critical Gate

Clean -- no destructive operations detected. INFO: `tools/painel.py` passa a usar `subprocess.run(["git", ...])`
(lista, sem shell, timeout 30) -- não é o padrão de SEC108 (exec dinâmico); só nota.

### Defeitos

| # | Gravidade | Confiança | Onde | O quê |
|---|---|---|---|---|
| D1 | MÉDIA | alta | `tools/plano.py:1614` / `:1729` x `core/templates/hub.html:2088` | Pendente fora da Fase 1 com lista aberta (#65) some do Painel e aparece no Fora das Listas: 37 x 38. Também a unidade (tarefas x listas). |
| D2 | BAIXA | alta | `core/templates/hub.html:2123` | Subtítulo das Listas ainda diz "As listas da semana" (resíduo de cronograma na aba consultiva). |
| D3 | BAIXA | média | `tools/test_hub_render.py:694` | O fallback sem sprint só tem smoke; nenhum assert de "Atrasadas"/`qd-atraso` nas Listas. |
| D4 | INFO | alta | `tools/hub.py:595`, `:1018` | Ramo por semana da Teoria sem chamador em produção. |

### Gaps

- D1: a agenda deve dar destino a toda pendente com lista capturada: ou `montar_sprint` marca a de semana fora da
  Fase 1 (`sprint: fora (fase 2)`) ou `agenda_sprint` a inclui no `fora` com esse motivo; e o Painel e as Listas
  contam a mesma unidade (ou o rótulo diz qual). Esforço S. Cai no escopo da part-5 (`tools/plano.py`, `tools/painel.py`).
- D2: trocar o texto de `QZ_SUB.questoes` (sem "da semana"). S.
- D3: um assert `Atrasadas` no `test_sem_hub_sprint_as_listas_caem_nas_semanas`. S.

### Incremental Prompt Pack

```
Contexto: MedHub, sprint-final-uerj. Fonte única do "hoje"/backlog = plano.agenda_sprint (PURA, lê só dia_plano e
a marca `sprint: fora (<motivo>)` da nota). Painel (painel._bloco_sprint) e aba Listas (hub.dados_sprint ->
qzGruposSprint em core/templates/hub.html) DEVEM mostrar o mesmo Fora do sprint.

1. (D1) Em tools/plano.py, toda pendente sem dia_plano que não está em SEMANAS_FASE1 entra no `fora` de
   agenda_sprint com um motivo legível (ex.: "fora da Fase 1"), ou montar_sprint/mudancas_do_sprint a marca na
   nota -- escolha a que mantém `--sprint` idempotente (2a rodada = 0 alterações). Se a marca for por nota, o
   --expect do --apply muda: medir antes. Teste: banco sintético com pendente semana 9 + lista capturada ->
   len(painel fora) == len(listas fora) e a tarefa aparece nas duas telas.
   Decidir a unidade do contador "Fora do sprint · N" (tarefas) e fazer a aba Listas contar tarefas também, ou
   rotular "N listas".
2. (D2) core/templates/hub.html QZ_SUB.questoes: tirar "da semana".
3. (D3) tools/test_hub_render.py: no teste sem hub-sprint, assert de "Atrasadas" para lista de semana passada.
Padrões: sem cor literal (tokens do tema.css); ⚰️ para comportamento removido; suíte verde; ui_capturas listas.
```

See the incremental prompt pack above. Fix the gaps and run `audit` again.
