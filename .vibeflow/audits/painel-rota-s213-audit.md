## Audit Report: Painel s213 -- rota da Fase 1 dentro do Painel (+ D4-1, D4-2, D4-3, D4-5)

> Auditado em 2026-10-04 (s213), subagente auditor. Spec: `tmp/painel_s213/PLANO.md` (D3; D4 itens 1, 2, 3, 5).
> Relato do implementador: `tmp/painel_s213/ENTREGA.md`. Diff auditado = árvore de trabalho, NÃO commitada, em `tools/plano.py`,
> `tools/painel.py`, `tools/hub.py`, `core/templates/hub.html`, `tools/test_plano.py`, `tools/test_painel.py`,
> `tools/test_hub_quadro.py`, `.claude/commands/engenharia-cli.md` (+ espelho). Fora do escopo (mudanças do principal): gabaritos,
> `test_prova_pdf.py`, `analisar-questao.md` (+ espelho), `core/hub_quadro.json`, o trecho de
> `test_registro_real_so_com_as_aulas_em_aberto_e_ligadas_ao_plano`, `artifacts/aula-*.html`, `history/*`.
> Medições em `tmp/painel_s213/audit/` (`painel.html`, `painel.json`, `panorama.json`, `panorama_atual.md`).

**Verdict: PASS** (10/10 DoD; Critical Gate limpo; 1 achado médio e 4 baixos de revisor, nenhum bloqueante)

### DoD Checklist

- [x] **1. Rota inteira, semanas futuras fechadas, corrente aberta, "Depois" só sem rota.** `plano.py:979` itera
  `range(semana + 1, max(SEMANAS_FASE1) + 1)` e pula semana sem pendente (`plano.py:980-982`). `painel.py:_html_rota` emite
  `<details class="rota-sem">` sem `open`; `_html_semana` (`painel.py:483-489`) só cai na linha "Depois" quando `d["rota"]` é vazio.
  HTML real (04/10, corrente S3): 4 `details.rota-sem` (S4-S7), `grep '<details[^>]*open'` = 0, "Depois" ausente. Testes:
  `test_rota_semana_futura_recolhida_e_corrente_aberta`, `test_sem_rota_mantem_a_linha_depois`.
- [x] **2. MESMO `<li class="tarefa">`.** Função única `_html_tarefa` (painel.py, nova) usada pela corrente (`painel.py:480`) e
  pela rota (`_html_rota`); construtor único `_tarefa` para os dois. Na rota real: 18 "resolver no hub", 47 "abrir lista",
  4 "abrir aula". Teste: `test_rota_usa_o_mesmo_li_da_semana`.
- [x] **3. Uma régua só + teste de concordância.** A rota é a chave `rota` de `plano.panorama` (`plano.py:979-990`); o painel só
  copia (`_bloco_semana`). Testes: `test_rota_concorda_com_o_panorama`, `test_rota_concorda_com_a_aba_aulas`,
  `test_panorama_rota_vai_da_semana_seguinte_ate_a_ultima_da_fase1`. (Ver achado R1: a sentinela x aba Aulas não trava a
  semana CORRENTE.)
- [x] **4. Lista no banco abre a aba Listas; EMED some; mesma precedência no quadro.** `painel.py:_acao` testa `no_hub` antes da
  URL, modo `simulados` só para área agregada, `questoes` no resto; `hub.py:510-516` idem com `AREA_SIMULADO`. Testes:
  `test_lista_no_banco_do_hub_abre_a_aba_listas_e_nao_o_emed` (painel), `test_lista_ja_no_hub_abre_a_aba_listas_e_nao_o_emed`
  (quadro), `test_acao_do_simulado_no_hub_e_atalho_e_fora_dele_e_texto` (ajustado com `area`, justificado no docstring).
- [x] **5. Aula que PREPARA aparece no Painel.** `_aulas_por_tarefa` lê `tarefa_id` E `tarefas` (só com arquivo em `artifacts/`).
  Testes: `test_aulas_por_tarefa_le_quem_cumpre_e_quem_prepara`, `test_tarefa_de_lista_com_aula_que_prepara_tem_os_dois_links`.
  No HTML real, #40 (dmg) e #100 (topicos-pediatria) trazem "abrir aula".
- [x] **6. Iframe re-mede no `toggle`.** `core/templates/hub.html:497` `doc.addEventListener("toggle", function(){ medir(quadro); }, true);`
  (captura, correto: `toggle` não borbulha). Teste: `test_painel_remede_ao_abrir_semana`. Conferência em navegador declarada
  pelo implementador (Edge headless, 1957 -> 5074 px e volta; `tmp/painel_s213/shots/`), não refeita aqui.
- [x] **7. Restrições de tela** (`python -X utf8 tools/painel.py --html --out tmp/painel_s213/audit/painel.html`, 39.154 B):
  `max-width` = 2; `position: sticky` = 0; `nowrap` = 0; `–` `—` `→` `←` `⇒` = 0; `class="wrap"` = 1 e `.wrap{` = 1.
- [x] **8. Sem flag nova; assinatura preservada; skill com CHECK; paridade.** Nenhum `add_argument` novo (só o `help` do `--json`);
  `panorama(linhas, calendario, hoje, prevalencia=None)` inalterada. `engenharia-cli.md:590-604` descreve rota, ação e
  Documentação com `<!-- CHECK: -->` para `test_rota_concorda_com_a_aba_aulas`, `test_lista_no_banco_do_hub_abre_a_aba_listas_e_nao_o_emed`,
  `test_documentacao_lista_as_analises_do_quadro_com_atalho` -- os três existem em `tools/test_painel.py`.
  `python -X utf8 tools/sync_skills.py --check` -> "Paridade ... OK", rc 0.
- [x] **9. Suíte e harness.** `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> **1360 passed**.
  `python -X utf8 tools/auto_check.py --changed` -> rc 0, zero BLOCK. WARN, todos pré-existentes: `POSICAO_DRIFT` (HANDOFF cita S2),
  `ERROS_ORFAOS` F38 (3 dias), `AREAS_FANTASMA` F89 (5 pares), `CLAUSULA_ORFA` 128/300 e `CLAUSULA_ORFA_SUBIU` 128 > 127.
  Atribuição do último medida por arquivo (`clausulas_check.extrair` em HEAD x árvore): `engenharia-cli.md` 18 -> 18,
  `analisar-questao.md` 0 -> 0 -- esta entrega não acrescenta cláusula órfã.
- [x] **10. Contagem HTML = `plano.py --panorama --json`.** S4 29/789, S5 31/836, S6 23/707, S7 9/439 nos dois lados (li por
  `details.rota-sem` e soma de `<span>N questões</span>`); total 92 / 2771 = `fase1` do panorama (abertas da S3 = 0).

### Critical Gate

Clean.
- Sem escrita em `ipub.db`, sem SQL novo: o diff só lê (`plano.panorama` pura; painel/hub leem `db.tarefas_com_questoes`, já existente).
- Boot intacto: `render_panorama` não foi tocado; a saída Markdown do `plano.py --panorama` da árvore é **byte a byte igual** à do
  `tools/plano.py` de HEAD executado em memória (974 = 974 chars, "IGUAL"); o `--json` sem a chave `rota` também é idêntico.
  `memory_boot.py` consome só o Markdown; `day_plan.py` não chama `panorama`.
- Nenhum teste removido; o único renomeado (`test_coletar_traz_os_quatro_blocos` -> `..._fixos_e_o_de_documentacao`) ganhou
  asserções e o porquê no docstring. Nada destrutivo.

### Achados do revisor

| # | Sev. | Onde | Achado | Correção mínima |
|---|---|---|---|---|
| R1 | Média | `tools/test_painel.py` `test_rota_concorda_com_a_aba_aulas` | A sentinela filtra as seções do quadro por `> s["semana"]` (a semana do PAINEL). Se `hub.semana_atual` divergir da régua do panorama (o risco D5-5 que ela diz travar), as semanas > corrente continuam iguais e o teste passa. Ela trava filtro e alcance da rota, não a semana corrente. | Acrescentar `assert hub.semana_atual(dict(CALENDARIO), HOJE, pendentes) == s["semana"]` (ou comparar a seção da semana atual do quadro com `s["tarefas"]`). 1 linha, mesmo teste. |
| R2 | Baixa | `tools/painel.py:477-493` (`_html_semana`) | Semana corrente vazia (hoje, S3 no último dia): "0 tarefa(s) em aberto, 0 questões." + `<ol class="tarefas"></ol>` vazio acima da rota. É defeito de apresentação: o número é verdadeiro, mas a linha não diz nada útil e o `<ol>` vazio sobra no DOM. | Quando `d["total"] == 0`: resumo = "Semana fechada: %d de %d tarefas feitas." (`feitas_semana`/`tarefas_semana`, já no dict) e não emitir o `<ol>`. NÃO abrir a S4 automaticamente: quebraria o DoD 1 (futuras fechadas) e só dura até a virada do calendário. |
| R3 | Baixa | `tools/painel.py` `_acao` x `tools/hub.py:514` | A regra do modo do atalho tem duas fontes: painel usa `areas.AREAS_AGREGADAS`, hub usa `plano.AREA_SIMULADO`. Hoje equivalem (`AREAS_AGREGADAS == ('Simulado',)`), mas uma área agregada nova faria as abas divergirem. | Usar a mesma constante nos dois (ou uma função `modo_da_lista(area)` no `plano.py`, que os dois já importam). Fora do escopo agora; anotar. |
| R4 | Baixa | `tools/plano.py:973` | `item = lambda l: _item_panorama(...)` (E731); há precedente no arquivo (`chave = lambda`, 965). | Cosmético; pode ficar. |
| R5 | Baixa | `tools/plano.py:979-990` x `proxima` (1006-1010) | `rota[0]` e `proxima` contam a S+1 por dois caminhos (mesma origem `pendentes`, hoje idênticos). | Aceitável: `test_concordancia_painel_x_panorama` cobre `proxima`; não deduplicar agora. |

Bordas conferidas sem defeito: semana fora do calendário (`inicio/fim` None, `_html_rota` omite a data; teste em `test_plano`);
rota vazia (corrente = S7 ou Fase 2: `range` vazio, cai no "Depois"); tarefa sem área (`_tarefa` cai para `bloco`, e `_html_tarefa`
para "?"); `no_hub` sem URL no painel é inalcançável (`classe == "lista"` exige `url_lista`, `plano.py:901`). Nomes novos em
português, no idioma do arquivo.

### Pendências fora desta entrega (para o principal)

- `HANDOFF.md:31` declara a suíte **1349**; medido **1360**. O `SUITE_HANDOFF` do pre-commit bloqueia se o HANDOFF for staged com
  o número antigo.
- O relato citava 2 falhas da suíte por `artifacts/aula-autopsia-uerj-2021.html` sem registro; com o `core/hub_quadro.json` do
  principal na árvore, a suíte fecha verde. Os dois têm de ir no MESMO commit (ou o teste de registro real volta a falhar).
- Publicar exige `painel.py --html` + `hub.py --build` + publish, e a conferência a 390 px já declarada.

### Prompt-pack incremental (opcional, R1 + R2; não bloqueia o PASS)

> Arquivos: `tools/painel.py`, `tools/test_painel.py`. Sem flag nova, sem CSS novo.
> 1. Em `_html_semana`, se `d["total"] == 0`: o resumo vira "Semana fechada: {feitas_semana} de {tarefas_semana} tarefas feitas."
>    e o `<ol class="tarefas">` não é emitido; com tarefas, nada muda.
> 2. Teste `test_semana_corrente_vazia_nao_mostra_lista_vazia` (dict sintético como `test_sem_rota_mantem_a_linha_depois`, com
>    `rota` de 1 semana): sem `<ol class="tarefas"></ol>`, sem "0 tarefa(s)", com "Semana fechada" e com `rota-sem`.
> 3. Em `test_rota_concorda_com_a_aba_aulas`, acrescentar `assert hub.semana_atual(dict(CALENDARIO), HOJE, pendentes) == s["semana"]`.
> DoD: os 2 testes verdes; suíte inteira verde; `max-width` = 2 e zero `nowrap`/`sticky` no HTML gerado.
