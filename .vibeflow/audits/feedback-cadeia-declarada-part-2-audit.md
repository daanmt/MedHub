## Audit Report: feedback-cadeia-declarada part-2 (a tela de revelação)

> Auditado em 2026-10-02 (s211), subagente de implementação. Spec: `.vibeflow/specs/feedback-cadeia-declarada-part-2.md`.
> Dependência: part-1 PASS (`.vibeflow/audits/feedback-cadeia-declarada-part-1-audit.md`, commit `78f8c45`).

**Verdict: PASS**

### DoD Checklist

- [x] **1. Declaração por elo.** `qzSolucao` (`core/templates/hub.html`) rende 4 botões por elo (`QZ_DECL`: Sim · Incerteza ·
  Desatenção · Não) para cadeia v2 e v3; o toque chama `qzDeclarar(i, st)`, que grava `elos` alinhado à cadeia pelo `qzGravar`
  (espelho local + reenvio). Certa e sólida: `Sim` marcado com classe `presumido`, `title="Sim (presumido)"` e a linha
  "Certa e sólida: Sim presumido em cada elo. Toque para ajustar."; NADA gravado no render. Testes:
  `test_declaracao_grava_o_array_alinhado_a_cadeia`, `test_render_da_declaracao[declarada|presumida]` (goldens
  `declarada.html`, `presumida.html`; `gravados == []` em todo render), `test_presumida_rotula_e_nao_grava_e_legado_rotula_a_data`.
- [x] **2. Zero inferência.** `test_pagina_nao_infere_quebra_pela_letra[v2|v3]` (errada, riscou B, sem declaração, sem análise ->
  todos os `li` sem classe e sem botão marcado, mesmo na v2 que ainda tem `elo` nas alternativas) e
  `test_template_nao_carrega_a_inferencia` (nenhuma das frases "provável quebra", "a sua letra cai", "evidência: você riscou",
  "leitura provisória", "falha no elo", "Você: riscou" no template inteiro).
- [x] **3. Porquê sob a alternativa.** `qzAltsHtml(q, r, revelada)` (pura): revelada, o `porque` do gabarito e o da marcada abertos,
  os demais `hidden` e abertos no toque (handler de `#qz-alts`). Seção "Alternativas" e linha "Você: ..." removidas.
  Testes: `test_porque_aparece_sob_o_gabarito_e_a_marcada`, `test_secao_alternativas_e_linha_voce_sairam_da_solucao`.
- [x] **4. Linha do agente.** `qzAgenteHtml(a)` (pura): `veredito_hub`, `armadilha`, `Cards #id`; botões de veredito + nota só com
  `conflitos` não vazio; "Pedia" e "Comporta" fora. Testes: `test_linha_do_agente_sem_conflito_nao_pede_veredito`,
  `test_linha_do_agente_com_conflito_pede_veredito`.
- [x] **5. Conflito e legado.** (a) `qzConflitos(q, r)` (pura): só `descartar` com `letra` = marcada e declarado `sim`
  (`test_conflitos_so_no_descartar_da_letra_marcada_declarado_sim`; golden `conflito.html` com o rótulo exato). (b) resposta sem
  `elos` + análise com `estados` -> convertidos (`ok`->sim, `quebrou`->nao, `nao_usou`->desatencao, `nao_avaliado`->sem marca), rótulo
  "Estados da análise de 26/09", sem gravar (golden `legado.html`).
- [x] **6. Cadeia com defeito + limpeza.** "Erro na cadeia" abre o motivo; `qzDefeito` grava `cadeia_defeito: {motivo, ts}`
  (`test_defeito_de_cadeia_grava_motivo`). Os 8 chips, a caixa de 5 campos e o textarea saíram; sobra a linha
  "Algo a acrescentar? (opcional)" gravando `racional`; `elo` não é mais escrito (`test_chips_de_causa_sairam`).
  Resposta antiga sem os campos novos abre sem erro (`test_resposta_antiga_sem_campos_novos_abre_sem_erro`).
- [x] **7. Vocabulário, harness e forma.** Brief §Estado por elo define o vocabulário DECLARADO (linha "Vocabulário declarado:")
  com lápide na leitura provisória e no vocabulário antigo; `test_vocabulario_de_estados_do_brief_e_o_da_pagina` compara com
  `QZ_DECL`. `/banco-emed` "Na página" reescrito com lápide; rito §10.10 completo no mesmo commit: (1) brief, (2) skill,
  (3) `docs/MEMORIA-AUDITORIA.md` §12 (`a sua letra cai neste elo`, `leitura provisória pelas letras`, `chips da aba Resolver`).
  Goldens antigos (`ok`, `quebrou`, `nao_usou`, `nao_avaliado`, `provisoria`, `conflito` v2) removidos e os 4 novos gravados de
  propósito. Rodado: `python -X utf8 -m pytest tools/ -q -p no:cacheprovider` -> **1322 passed**; `hub.py --build --lote
  tmp/player_2026-10-02a.json --out <scratchpad>` + `--check` -> `OK`; `node --check` do JS da página montada -> OK;
  `sync_skills --check` -> 0; `auto_check --changed` -> exit 0 (CONTRATO_REVOGADO PASSED).
  Forma: `test_forma_da_tela_revelada` (sem cor literal nas regras novas, só tokens; `min-height:44px` nos botões novos; rótulos
  <= 15; `min-width:0` no `li`; nenhum `position: sticky/fixed` no template). Cores dos estados: Sim `--qz-ok`, Incerteza `--qz-duv`,
  Desatenção `--qz-chute`, Não `--alerta`.

### Pattern Compliance

- [x] Design do hub (minimalista, celular primeiro): 3 blocos (alternativas com porquê + veredito; cadeia; linha do agente) +
  rodapé discreto; o porquê é seção do mesmo cartão (filete), não caixa aninhada; pílulas 4 por linha, 2x2 abaixo de 400 px.
- [x] Goldens por cenário em `tools/goldens/hub_render/`.
- [x] Skill canônica + `sync_skills`.

### Convention Violations / desvios de orçamento

- 6 arquivos: `core/templates/hub.html`, `tools/test_hub_render.py` (+ goldens), `docs/SOLUCAO-MEDHUB-BRIEF.md`,
  `.claude/commands/banco-emed.md` (+ espelho), `tools/test_emed_banco.py`, `docs/MEMORIA-AUDITORIA.md`. Fora da lista da spec:
  `test_emed_banco.py` -- o teste de propriedade F133 lê do template toda chave que a página grava e acusaria `elos` e
  `cadeia_defeito` (sem coluna até a part-5); entrou um conjunto EXATO `_SEM_DESTINO_ATE_A_PART_5` (chave nova fora dele
  continua acusando; a part-5 o esvazia). `MEMORIA-AUDITORIA.md` = passo (3) do rito. `tools/test_hub.py` não precisou mudar.

### Decisões onde a spec deixava aberto (fixadas em teste)

- **Chave só depois de declarar** (e no legado), nunca no presumido: recall antes do verso (fricção virtuosa). Golden + `_Cadeia`.
- **Presumido**: o 1º toque materializa o `Sim` que ele via nos outros elos; **legado**: o 1º toque começa do zero (estado do agente
  nunca vira declaração dele). Tocar de novo no mesmo estado desmarca.
- "Como foi cada elo?" só enquanto houver pendência.
- Data do legado: `analisado_em` | `atualizado_em` | `veredito_em` (a análise antiga não tem data própria); sem nenhuma, "do hub".
- `qzDeclPendente` não considera o legado (resposta t26/t96 sem `elos` segue pendente) -- a trava é da part-3, que decide.
- Rótulo do controle: "Erro na cadeia" (o nome "cadeia com defeito" passa de 15 caracteres).
- `Enter` com foco num botão deixa a ativação nativa (antes, avançava a questão em vez de declarar).

### Critical Gate

Clean -- nada destrutivo; todo valor dinâmico novo no `innerHTML` passa por `qzEsc` (estados e índices vêm de constantes).

### Não verificado

- Render real no navegador e no celular (CSS, temas claro/escuro, pílulas a 360 px) -- o harness mede o HTML, não o desenho.
- O toque que abre/fecha o porquê das outras alternativas e o atalho `Enter` (handlers de DOM, fora do harness node).
- Rótulos > 15 pré-existentes FORA desta tela ("Alterar resposta", "Marcar lista como resolvida", "Rever em sequência").

14 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
