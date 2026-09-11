# Audit Report: deixis-sem-contexto (F79b, item 1.1 -- abertura do Tier 1)

**Verdict: PASS**

> Spec: `.vibeflow/specs/deixis-sem-contexto.md` · sessao **s176 janela 2** (2026-09-10).
> Suite: `python -m pytest tools/ -q` -> **550 passed** (baseline da spec: 540; +10 do suite novo).
> Harness: `python -X utf8 tools/auto_check.py --changed` -> **PASSED**, 0 BLOCK (16 checks verdes).

## DoD Checklist

- [x] **1. Predicado unico, na biblioteca unica.** `checar_deixis_sem_contexto` em
  `tools/card_checks.py`; `card_self_sufficiency.py` **importa o mesmo objeto** -- provado por
  identidade, nao por semelhanca: `assert css._deixis_sem_contexto is cc.checar_deixis_sem_contexto`
  (`test_a_varredura_do_corpus_enxerga_o_predicado`). O predicado entra ali como `PREDICADOS`, e nao
  como 4a linha de `PADROES`, porque `PADROES` casa regex sobre `front` **concatenado** -- o que
  apagaria exatamente a distincao contexto x pergunta de que o achado trata.
- [x] **2. Dispara so na CONJUNCAO.** `card_checks.py:363-366`: sai cedo se a pergunta e vazia ou se
  `len(contexto) >= CORTE_CONTEXTO_MINIMO`. Teste do par simetrico:
  `test_contexto_curto_demais_conta_como_vazio_e_longo_nao` (mesma pergunta, 9 chars dispara,
  46 chars nao) e `test_a_mesma_deixis_COM_vinheta_e_legitima`.
- [x] **3. Nasce BLOCK, com a medicao ao lado.** Entra em `erros` de `validar_card`
  (`test_dispara_como_BLOCK_e_nao_como_aviso` exige `erros` **e** exige ausencia em `avisos`). O
  comentario de proveniencia no codigo carrega os tres candidatos e seus numeros, e um teste
  (`test_corte_e_parametrizado_com_proveniencia`) **falha se essa medicao for apagada** -- numero
  sem proveniencia e claim que envelhece.
- [x] **4. Os falsos-positivos medidos viraram fixture negativa.**
  `test_classe_generica_nao_e_deixis` (5 perguntas **vivas** do banco, do candidato amplo que deu 26
  falsos) e `test_caso_epidemiologico_nao_e_vinheta` (#620 + 2 variantes). Se o predicado alargar, a
  suite acusa antes do usuario.
- [x] **5. Sentinela de populacao.** `test_passivo_no_banco_real_continua_zero` re-mede contra o
  `ipub.db` e exige `[]`, com a leitura escrita no proprio assert: cair significa *predicado alargou*
  **ou** *entrou card defeituoso*, e **nenhuma das duas** autoriza afrouxar o corte (licao do 0.2).
  Degrada para no-op sem banco, em vez de falhar em CI sem `ipub.db`.
- [x] **6. Portador de autoria atualizado.** `/estilo-flashcard` ganhou o **4o defeito nomeado**,
  marcado como o **unico BLOCK** da serie, com o conserto em uma frase ("ou a vinheta entra, ou a
  pergunta perde a referencia anaforica") e a distincao **deixis x classe** escrita -- que e
  precisamente o erro que o candidato amplo cometia. `sync_skills --check` exit 0.
- [x] **7. Craftsmanship gate.** 550 passed; `auto_check --changed` PASSED; ASCII limpo; `sqlite3`
  so onde ja vivia.

## Pattern Compliance

- [x] **Biblioteca unica de predicados** (`AGENTE.md §6`, "todo write passa por `card_checks`") --
  o novo predicado entra em `validar_card`, que e o caminho por onde os 7 writers passam.
- [x] **Warning-first (s106/107)** -- a regra diz "nasce WARN, vira BLOCK **quando a base zerar**".
  Aqui a base nasceu zerada e **isso foi medido**, nao assumido; a promocao imediata e a aplicacao
  da politica, nao a excecao dela. O audit registra a tensao porque o ledger dizia "nasce WARN": o
  proprio ledger pedia a varredura (remedio M) **antes** de decidir, e a varredura decidiu.
- [x] **Sensors** -- a varredura do corpus continua WARN e read-only; so o **gate de escrita** e
  BLOCK. As duas superficies compartilham implementacao.
- [x] **File naming / testes** -- suite inscrita no `pytest.ini` com nota de 7 linhas.

## Convention Violations

Nenhuma.

## Critical Gate

Clean — no destructive operations detected.

Diff: 3 arquivos de codigo (+1 predicado, +3 regex, +1 constante, +12 linhas de fiacao), 1 suite
nova, 1 skill (+ espelho), `pytest.ini`, spec, ledger. Zero SQL de escrita, zero migration, zero
`DROP`/`DELETE`/`eval`/segredo. A unica mudanca de comportamento e **recusar** uma escrita que antes
passava -- e o passivo medido de escritas afetadas hoje e **zero**.

## Incidente de processo (registrado, nao escondido)

Ao escrever o predicado por heredoc, 13 sequencias `\\b` foram emitidas como **byte de backspace
literal** (`\x08`) dentro das regex. O efeito era silencioso e perfeito para enganar: `sed` e
`grep` **nao mostram** o byte, o arquivo importava sem erro, a suite ficava verde -- e o predicado
**nunca casava nada**. So apareceu porque o smoke test manual rodou antes de qualquer commit e
devolveu `None` nos tres casos, inclusive no positivo. Consertado (`\x08` -> `\b`) e verificado por
`git diff --stat`: **72 insercoes, 0 remocoes** -- nenhuma regex preexistente foi tocada pela
limpeza. Licao operacional: *predicado que nao casa o proprio caso-teste positivo e
indistinguivel de predicado que nao existe*, e nenhum gate do repo pegaria isso -- foi o smoke
test manual, nao o harness.

## Fronteiras DECLARADAS (nao ler PASS como cobertura completa)

1. 🔴 **O fixture da ordem cicatrizou.** O `#367` da s169 foi **reforjado**: hoje tem vinheta
   completa e outra pergunta. O texto original sobrevive como **fixture sintetico, rotulado como
   tal**. Isso nao revoga a classe -- mas quem ler "F79b fechado" precisa saber que o card que o
   originou **ja estava consertado** antes do gate existir.
2. **Mede ausencia de vinheta, nao suficiencia dela.** Vinheta de 20 chars que nao carrega o dado
   pedido passa no corte e segue sendo card ruim -- isso e o eixo A do F81, outro predicado, tambem
   incompleto.
3. **O corte de 15 e convencao declarada, nao fronteira medida.** A distribuicao e **bimodal**:
   vazio **468** · 1-14 chars **0** · 15-29 **5** · >= 30 **946**. Como ninguem vive na faixa 1-14,
   qualquer valor entre 1 e 15 daria o mesmo resultado hoje; o numero exato **nunca foi testado
   contra dado real** e nao se finge que foi.
4. **BLOCK sobre corpus futuro e extrapolacao.** FP 0 vale para os **1419 cards que existem**. Um
   card futuro pode acionar o predicado por engano -- nesse caso a escrita e recusada e o autor ve a
   mensagem com o conserto. E o trade-off aceito de um BLOCK; esta declarado, nao minimizado.

---

**Ready to ship.**
