# Session 189 -- ENGENHARIA na madrugada antes do simulado: a Fase 1 com UMA autoridade e os numeros que o operador le certos

**Data:** 2026-09-18 (23h10) -> 2026-09-19 (~01h40) - **Ferramenta:** Claude Code (Opus 5 1M) - **Continuidade:** `session_188.md`

## 0. O que ele pediu
*"A sessao de engenharia que voce adiou para depois do simulado pode ser tocada agora, de madrugada, antes do simulado. Pode pedir mais orientacao ao ai-eng."* O `/ai-eng` (`ai-eng-5a`) mandou o kickoff com errata ao proprio veredito da s188 (o gerador da trilha NAO era de uso unico: o HANDOFF mandava re-roda-lo a cada prova) e 6 fatias. Restricao da noite: nada muda o conteudo da trilha nem o que o boot entrega, exceto os numeros corrigidos; spoiler proibido.

## 1. O que foi feito (spec `.vibeflow/specs/trilha-autoridade-unica.md`, audit PASS)
- **Baseline** antes de tocar codigo: suite 933, `auto_check` PASSED, selo verde; **golden de partida** -- o scratch re-rodado numa copia fora do repo reproduziu os 115 overrides.
- **Fatia 1** (`7f311fd`, `f12c4ef`, F123): ritmo da Fase 1 (273,3 -> 74,8 q/dia em 18/09; 76,6 em 19/09) e **cota do dia** (~81q/dia na S1, semana de calendario da trilha); cada regua diz o que mede; o corte do hook de boot (8 linhas) passou a se declarar e a cota foi para o cabecalho do bloco.
- **Fatia 3** (`342a86e`, F124/F125): `tools/trilha.py` + `core/cronograma/trilha/` (parametros, camada manual com `racional`, entrada fixada); `plano_trilha.json` GERADO; golden + propriedade (`tools/test_trilha.py`); `plano.py --semear` passou a contar as linhas que MUDARIAM (`diferenca_semeada`) -- prova no banco: 0 nova, 0 mudaria.
- **Fatia 2** (`83b3e50`): `plano.py --reserva` -> `docs/RESERVA-FASE1.md` (174 fora da fila; 13 de faixa ALTA sem nenhuma tarefa na fila cobrindo o tema).
- **Fatia 4** (`390ee43`): `--mover` recusa linha da Fase 1 com a trilha ativa (F120); `links_listas.json` com estado explicito por tarefa (faltando 0; 17 com tipo de lista e sem link no PDF); `links_exercicios.json` removido.
- **Fatia 5** (`521c885`): 7 clausulas orfas anotadas (134 -> 127) + **catraca** `BASE_ORFAS`; clausula 10 do F93: custo de subagente = `usage` do harness.
- **Fechamento:** rotulo honesto de acuracia (~80-90%, consumir em faixas) no `_schema` do `prevalencia_uerj.json` (veredito do F121, que a s188 tinha revertido); `docs/VEREDITO-AIENG-s188.md` saiu (executado; verbatim em `git show ec61a1b:docs/VEREDITO-AIENG-s188.md`).

## 2. Achados que o veredito nao previa
1. O 273 **governava o recomendador** (R4); e **nunca chegou ao boot**: o hook injeta 8 linhas, a do ritmo era a 14a. O `/ai-eng` registrou como instancia dele (veredito sobre ALCANCE sem medir alcance).
2. **F125** -- loop infinito no agendamento do gerador da s188 (`vazio` zerava antes do teste de capacidade); com teto 20% o `--gravar` travava. Reproduzido isolado, corrigido, regressao com prazo.
3. **"+7 orfas da s188" era atribuicao errada**: medido com o sensor em worktree de cada commit -- 127 (s187 janela 6) -> 132 (ultimo commit da s187) -> 132 (s188, +0).
4. O WARN da reserva ficou preciso: 22 de faixa alta, mas so 13 sem cobertura na fila (coluna `tema ja na fila por`) + coluna `estado` (o porque da exclusao).
5. `plano_custom.json` guarda semana/ordem que a trilha sobrepoe em 28 de 29 tarefas custom (duas autoridades, DECLARADO).

## 3. Decisoes
- Divisor do ritmo segue `FIM_CONTEUDO_ALVO` (decisao da s159, travada por teste); a cota le o calendario da trilha.
- Piso/teto conferido na regua do gerador (GO do `/ai-eng`); lente por area declarada, com as 7 linhas divergentes nominais.
- **Recalibracao pos-prova:** regra estatistica do `/ai-eng` adotada como texto no HANDOFF (nao por UMA prova; acerto acumulado a partir da 3a). Fatia 6 (regra como DADO) NAO feita.
- `scratch/s188_trilha/` fica local (gitignored) como registro; `extrair_links.py` e a referencia do F122.
- **Fechamento do `/ai-eng` (01h50):** aceitou as 5 fatias e os 6 achados sem ressalva; registrou F125 como furo do DoD DELE (golden + propriedade certificam o PONTO, nao a vizinhanca: ferramenta de re-execucao leva >= 1 corrida perturbada com prazo) e o `--expect 0` como premissa de alcance nao medida. Duas decisoes, reversiveis pelo operador: prevalencia em FAIXAS entra junto da 1a recalibracao legitima; `plano_custom.json` x trilha + redesenho do `--mover` = mesma decisao, pos-02/11. Canal fechado do lado dele.

## 4. Custo
**ZERO subagentes** (o porte nao passava o limiar do F93). Canal com o `/ai-eng`: kickoff + 1 checkpoint (resposta dele: GO na ordem e no default do achado 3, 3 notas aplicadas) + destilado final.

## 5. Proximos passos
Sessao s190 = ESTUDO: registrar a UERJ 2023, Autopsia por bloco, conferir a reserva uma vez. Backlog de engenharia depois de 02/11 no HANDOFF.
