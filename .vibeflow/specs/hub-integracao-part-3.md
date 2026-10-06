# Spec: Hub integração -- part 3: Biblioteca daqui em diante

> Escrita em 2026-10-05 (s216). PRD: `.vibeflow/prds/hub-integracao-cortar-passos.md` (F3). Decisão dele: só daqui em diante; as 5 aulas em `artifacts/arquivo/` voltam sob pedido, uma a uma.

## Objetivo

Nada que foi concluído some mais do hub: "Outras aulas" e "Concluídas" viram uma seção "Biblioteca" na Teoria, e o rito de mover aula concluída para `artifacts/arquivo/` acaba.

## Contexto

O arquivamento nunca foi código: foi `git mv` manual (s195/s204), descrito no `_doc` de `core/hub_quadro.json`, na docstring `tools/hub.py:16`, no aviso "candidata a arquivo" (`hub.py:462-464`), em `.claude/commands/revisar.md:239` (passo 8a) e em `.claude/commands/aula-base.md:81-83`. `coletar_aulas` (`hub.py:877-889`) usa glob não recursivo, então `arquivo/` já fica de fora sozinho. A seção `hub-quadro-feitas` (`hub.py:569-571`, `hub.html:1267,1282`) recebe os itens marcados "feito"; desmarcar devolve o item por `.qd-sem[data-secao]` (`hub.html:1305-1306`, armadilha A7).

**Fricção que esta spec remove:** procurar no git uma aula que sumiu do hub, e o agente gastar um `git mv` por aula -- viciosa. Protege a virtuosa de reler: a aula concluída fica a um toque.

## Definition of Done

1. **Seção única "Biblioteca"** na Teoria, com o mesmo id `hub-quadro-feitas` (o `<details class="qd-feitas" id="hub-quadro-feitas">` de `test_secao_recolhivel_no_celular` fica), recolhida por padrão, contendo: itens concluídos (riscados, como hoje) e as aulas sem tarefa pendente (as antigas "Outras aulas"), ordenadas por data de criação decrescente. A seção `outras` deixa de existir como seção separada; `secPadraoAberta` e os testes que usam a chave `outras` são reescritos para `biblioteca` (A8).
2. **Desmarcar devolve o item** à seção de origem gravada em `data-secao` do próprio `li` no build; sem origem (aula de Biblioteca que nunca teve seção), o item fica na Biblioteca sem riscar e sem erro silencioso: `console.warn` + teste `test_desmarcar_sem_secao_de_origem_fica_na_biblioteca` (A7).
3. **Aviso "candidata a arquivo" sai** de `hub.py:462-464` e de `test_aula_ligada_so_a_tarefa_concluida_avisa_candidata_a_arquivo` (reescrito como `..._fica_na_biblioteca`). `test_registro_real_so_com_as_aulas_em_aberto_e_ligadas_ao_plano` deixa de exigir `artifacts/arquivo` para aula concluída.
4. **Ritos reescritos:** `_doc` de `core/hub_quadro.json`, docstring de `hub.py`, `revisar.md` passo 8a e `aula-base.md:81-83` dizem "concluída fica na Biblioteca; nada vai para `artifacts/arquivo/`". `python tools/sync_skills.py` regenera os espelhos em `.agents/skills/` (build artifact, não conta no orçamento). `CAP_AULAS` sobe de 120 para 200 (24 hoje, +5/semana).
5. **Suíte e harness.** `pytest tools/ -q` verde (reescritos: `test_secoes_atrasadas_primeiro_*`, `test_cabecalho_da_semana_*`, `test_revisao_direcionada_tem_bloco_proprio_*`, `test_feito_sai_riscado_em_concluidas_no_build` com o CHECK de `engenharia-cli.md:653` atualizado, `test_sem_plano_tudo_vai_para_outras_aulas_*`, `test_recontar_e_concluidas_*`, `test_outras_aulas_some_vazia_*`); `auto_check --changed` PASSED; `doc_drift.py` sem referência órfã a `artifacts/arquivo/`.

## Scope

**Arquivos (6):** `tools/hub.py` · `core/templates/hub.html` · `core/hub_quadro.json` (só `_doc`) · `.claude/commands/revisar.md` + `.claude/commands/aula-base.md` (contam como 1: mesma edição de rito) · `tools/test_hub_quadro.py` · `tools/test_hub_render.py`. `.claude/commands/engenharia-cli.md` só pelo CHECK renomeado.

## Anti-scope

- Reabrir as 5 aulas de `artifacts/arquivo/` (decisão dele). Busca ou filtro dentro da Biblioteca. Resumos na Teoria (P03).
- Mudar `coletar_aulas` (o glob não recursivo já exclui `arquivo/`).

## Technical Decisions

- **Mesmo id `hub-quadro-feitas`:** o estado recolhido no `localStorage` e 6 testes dependem dele; renomear não dá nada ao usuário.
- **Origem no `data-secao` do `li`:** hoje a volta depende de a seção existir no DOM; gravar a origem no item torna o desfazer determinístico.
- **CAP 200, não ilimitado:** o teto existe para o E01 (cada aula é um arquivo lido no publish); 200 cobre até 01/11 com folga.

## Applicable Patterns

- `agent-workflow-protocol.md`: rito alterado em skill = espelho regenerado por `sync_skills.py`, nunca à mão.
- `warn-first-check.md`: CHECK renomeado no mesmo commit.

## Risks

- **Biblioteca longa no celular:** `<details>` recolhida por padrão; itens com `min-width:0`.
- **Teste de CHECK órfão:** `auto_check` acusa; renomear o CHECK junto.

## Dependencies

- `.vibeflow/specs/hub-integracao-part-1.md`.
