## Audit Report: painel-dashboard-sprint part-1 (dashboard no topo do Painel, uma meta na tela)

> 13/10/2026 (s226). Auditado pelo mesmo subagente que implementou, com olhar adversarial, sobre o diff do commit
> `aca66f6` (`git show aca66f6`). Suíte: `python -X utf8 -m pytest tools/ -q` = **1755 passed** (o hook do commit rodou a
> mesma suíte inteira: 1755 passed); `auto_check --changed` PASSED.

**Verdict: PASS**

### DoD Checklist
- [x] **1. Skills `dataviz` e `artifact-design` carregadas antes de escrever; forma/cor/tiles dentro dos tokens.** Ambas
  carregadas pela ferramenta Skill antes do 1º Edit. Forma: tiles de KPI (um número por tile, barra fina, rótulo curto),
  barra empilhada para a parte-de-um-todo da projeção, barras horizontais para o acerto por bloco. Marcas: 2 px de fundo
  entre trechos (`.proj-barra{gap:2px}`), extremidades arredondadas, `title` em cada trecho e linha (dica ao passar o
  mouse), `role="img"` + `aria-label` com os números, legenda sempre presente (3 itens) e identidade nunca só por cor
  (contorno sólido x tracejado; rótulo "mais fraco"). Cor: só tokens -- `test_html_obedece_o_contrato_de_render` (sem
  literal no CSS do painel) segue verde; `--horizonte` não aparece no CSS do painel (assert novo em
  `test_barra_de_projecao_feito_sprint_meta`).
- [x] **2. Com sprint: Questões = feitas de `q_hoje`; Ritmo = real 7 d contra `capacidade_q` ("abaixo de 80/dia" / "em
  dia"), real 14 d, acerto; "por dia até a prova" e `alvo_marco` fora. Sem sprint: o de antes.** `painel.py`
  `coletar` (q_hoje do `_bloco_sprint`), `_html_dia`, `_html_ritmo`, `_bloco_ritmo` (`capacidade_q` por
  `plano.ler_sprint`). Testes `test_dashboard_questoes_usa_o_q_hoje_do_sprint` e `test_dashboard_sem_sprint_volta_a_meta`.
  Real, 13/10: "0 de 76"; "35,4 · abaixo de 80/dia"; "114,9" e "por dia até a prova" ausentes da página (medido no
  `tmp/dash_p1/painel.html`).
- [x] **3. Barra de projeção até 01/11 com os 3 números e o fora do sprint (997 q) como trecho que falta; acessível.**
  `_html_projecao`: 78,2% feito · 14,9% sprint · 6,9% fora; `aria-label` com 7.817, 9.306, 10.000, 997 e 694; "fora"
  em `--linha` + tracejado `--tinta3`. Teste `test_barra_de_projecao_feito_sprint_meta` (inclui o caso em que o sprint
  passa a meta e o sem-sprint = "").
- [x] **4. Por bloco em linhas com barra 0-100% + feitas/total; o mais fraco com rótulo; Simulados por último; sem
  `<table>`; "Fora da tabela" não volta.** `_html_blocos`; teste `test_por_bloco_em_linhas_com_barra_e_o_mais_fraco_rotulado`.
  Real: CM 77,2% "mais fraco" (Simulados 69,1% fora da disputa, de propósito: termômetro, não bloco).
- [x] **5. Nenhum `p.nota` no dashboard; Revisões 7 dias dentro dele sem mudar o gráfico; paridade do `q_hoje`.**
  `_html_dash` + `_html_agenda` (mesmo markup `.ag-barras`); asserts de `class="nota"` nos dois testes do DoD 2;
  `test_plano_dia.py::test_boot_painel_listas_mesmo_hoje` ganhou o tile (render com o `q_hoje` do `_bloco_sprint` = 50)
  e o `test_painel` amarra `dia.questoes.q_hoje == sprint.q_hoje == plano.agenda_sprint(...).q_hoje`.
- [x] **6. Contrato: regra s203 suspensa para a TELA com sprint (§10.10).** `cronograma-contract` v1.7 (frontmatter e
  corpo), redação nova na linha ativa da Integração, entrada v1.7 com a lápide ⚰️ em linha própria; termo
  `o único "por dia" do boot, do painel` cadastrado na §12 do `docs/MEMORIA-AUDITORIA.md`; `AGENTE.md §2` passo 4
  reescrito. Gate `CONTRATO_REVOGADO` e `Registro de termo revogado derivado (ii')` PASSED.
- [x] **7. Artesania.** `ui_capturas.py --hub tmp/hub_dash_p1 --cenas painel` a 390/768/1280: medida "ok" (sem rolagem
  horizontal) nas três; a de 390 lida (Read) duas vezes -- a 1ª mostrou o Ritmo em 2+1, corrigido (gap) e recapturado
  em 3 numa linha. Suíte 1755 verde; `auto_check --changed` PASSED; `docs/UI.md` §5 (componente "Dashboard"), §2, §6,
  §7 (travas) e §11 (histórico).

### Pattern Compliance
- [x] Leitor-fonte único (docstring do `painel.py`): o `q_hoje` vem do `_bloco_sprint` (`plano.agenda_sprint`), a
  capacidade do `plano.ler_sprint`, a projeção do `day_plan._cronograma_hoje` (que já usa `linhas_com_q_hub`, a mesma
  régua do Plano de hoje). Nenhuma regra nova de número no painel.
- [x] `docs/UI.md`: cor literal só no `tema.css`; um `.wrap`; `min-width:0` nos filhos de grid; nada `sticky`/`nowrap`;
  semântica (ciano = progresso, âmbar = aviso com texto, neutro para o que não é erro).
- [x] `--json` é o contrato: `dia.questoes.q_hoje` e `ritmo.sprint.capacidade_q` entraram no JSON e são testados.
- [x] Testes nunca tocam o `ipub.db` real (fixture `db_sintetico`; `plano.ler_sprint` monkeypatchado no teste do sprint).
- [x] §10.10 (declarar, lapidar em linha própria, cadastrar) no mesmo commit.

### Convention Violations
- Nenhuma.

### Achados (adversariais, todos registrados; nenhum médio ou alto)
1. **BAIXO / confiança alta -- só pós-31/10.** Sem sprint o Ritmo tem 4 números e, a 390 px, a grade `minmax(6.5rem)`
   os põe em 3+1 (um órfão). Cosmético, só volta quando o sprint acabar. Não corrigido (fica para quando o bloco sem
   sprint voltar a ser a tela viva).
2. **BAIXO / confiança média.** `.claude/commands/performance.md` linha 31 diz que o ritmo necessário do relatório é "o
   MESMO da linha Meta do boot e do painel"; com sprint o painel não mostra mais esse número. Não prescreve conduta
   (descreve o relatório do /performance), e o arquivo está fora do escopo da spec; o termo cadastrado não casa com essa
   redação. Fica declarado para o principal decidir se lapida.
3. **BAIXO / confiança média.** `ESTADO.md` linha 26 narra a decisão s203 ("todo por dia do boot, do painel, do HANDOFF
   e do recomendador sai dela"). É registro histórico do macro, fora do escopo; não casa o termo cadastrado.
4. **INFO.** Tema claro não capturado: o `ui_capturas.py` não tem opção de tema. Conferido pelos tokens: os textos do
   dashboard usam `tinta`/`tinta2`/`tinta3`/`aviso`/`ok`, todos >= 4,8:1 no claro (`docs/UI.md` §3); os trechos da
   barra têm contorno (`--acento`, `--tinta3`) além do preenchimento.
5. **INFO.** O tile de Cards perdeu as palavras "agora" e "esperando" ("176 vencidos · 733 novos · retenção 89,1% em 7
   dias"): encurtado para caber no tile de meia largura; nenhum teste dependia do texto antigo.
6. **INFO (processo).** A 1ª tentativa de commit foi bloqueada pelo hook: a linha de docstring "(cronograma v1.7)" fez o
   `painel.py` contar como referenciador de `tools/cronograma.py` (casamento pelo stem cru em `.py`) e a tabela gerada do
   `AGENTE.md §7.4` ficou desatualizada (`test_repo_real_consistente`). Reescrita para "(s226, contrato v1.7)"; o commit
   passou com a suíte inteira.

### Critical Gate
Clean -- no destructive operations detected (diff só de render, testes e docs; nenhuma escrita em banco, nenhum
`subprocess`/`eval` novo, nenhuma proteção removida).

### Paridade e bordas conferidas
- `q_hoje` = 0 com sprint: tile "N feitas" + "nenhuma lista no plano de hoje" (sem divisão por zero, barra 0).
- Feitas >= `q_hoje`: "dose do dia cumprida ✓" (texto + símbolo, não só cor).
- `ler_sprint` ilegível: `capacidade_q` None, o tile do real fica sem rótulo de comparação (sem inventar 80).
- Sprint que passa a meta: sem o trecho "fora" na barra e "o sprint chega à meta" no texto.
- Hub: o regex `_RE_CARDS_PAINEL` (`<b data-vivo="cards" ...>N</b> de T`) e o `data-sessao-gravada` seguem iguais
  (`test_hub.py::test_build_injeta_o_contador_do_dia_do_painel` e os testes do "ao vivo" verdes).

Ready to ship.
