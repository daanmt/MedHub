---
type: spec
projeto: MedHub
feature: trilha-autoridade-unica
slug: trilha-autoridade-unica
status: implemented
relates_to:
  - .vibeflow/specs/trilha-uerj-plano-como-dado.md
  - tools/day_plan.py
  - tools/plano.py
---

# Spec -- a Fase 1 com UMA autoridade, e os numeros que o operador le todo dia certos

> Sessao de ENGENHARIA s189 (madrugada de 18 -> 19/09/2026), vespera do primeiro simulado
> UERJ. Ordem e decisoes do `/ai-eng` (`ai-eng-5a`): veredito da s188
> (verbatim em `git show ec61a1b:docs/VEREDITO-AIENG-s188.md` -- o arquivo saiu no selo da s189, executado) + kickoff da noite, com errata sobre o gerador. Audit = loop
> do vibeflow, deste lado (AGENTE.md secao 10.6).
>
> 🔴 **Restricao da noite:** nada muda o CONTEUDO da trilha nem o que o boot de estudo
> entrega, exceto os numeros corrigidos. Prova: re-seed com **0 linha nova e 0 linha
> mudada** nos campos semeados. Backup do banco antes de qualquer `--apply`. Nenhum conteudo
> de questao de prova nao resolvida em saida que o operador leia.

## Objective
A Fase 1 (semanas 1-7, ate a UERJ em 01/11) passa a ter uma autoridade so, versionada e
testada -- o gerador da trilha sai do scratch para o repo, com entrada fixada, teste golden e
teste de propriedade -- e o boot passa a dar o ritmo da fase e a cota do dia com numerador e
denominador da mesma fase.

## Context (medido em 18/09/2026, antes de qualquer mudanca)
- **F123a.** `day_plan._cronograma_hoje` soma as `q_previstas` de TODAS as pendentes --
  12.027 = Fase 1 3.293 + Fase 2 5.712 + reserva 3.022 -- e divide pelos 44 dias ate
  `FIM_CONTEUDO_ALVO` (01/11): **273,3 q/dia**. O mesmo numero alimenta o recomendador
  (`restante_grade_q`), que imprime "grade atrasada (235d de deficit projetado)". O certo e
  3.293 / 44 = **74,8 q/dia**.
- **F123b.** O `day_plan` nao tem cota do dia: a distribuicao por dia saiu de script de
  scratch para o artifact da s188, que envelhece no dia 2.
- **Gerador fora do git.** `scratch/s188_trilha/` e gitignored (`.gitignore:53`); `gera_trilha`
  importa `reconcilia` e `agrega_uerj` e le `plano_all.json` (472 KB). O HANDOFF manda
  re-roda-lo a cada prova UERJ (6 vezes ate 01/11). O `_doc` do `plano_trilha.json` promete
  "editavel a mao" e o `--gravar` sobrescreve o arquivo: duas autoridades, a manual perde
  em silencio (o F120 uma camada acima).
- **Golden de partida (lente independente, antes de mover qualquer linha):** re-rodados
  numa copia fora do repo, `reconcilia.py` reproduz `temas_reconciliados.json` identico e
  `gera_trilha.py` reproduz os **115 overrides**, o calendario e os simulados do
  `plano_trilha.json` gravado.
- **Reserva.** 174 linhas pendentes com `semana_plano` NULL: 46 tiradas da fila pela
  `fase1_exclusiva` (nota `fora da trilha da Fase 1 (reserva)`) + 128 da reserva do
  extensivo S1-S20 (regra pura da part-2). Nenhum fluxo as le.
- **`--mover`** em linha da Fase 1 reporta sucesso e e desfeito pelo proximo re-seed.
- **`links_exercicios.json`**: 0 consumidores em `.py`. **`links_listas.json`**: ausencia de
  link nao distingue "nao existe lista" de "link faltando".

## Definition of Done

**Fatia 1 -- o que ele le amanha**
1. `_cronograma_hoje`: `restante_q` = pendentes das semanas da Fase 1; ritmo = restante /
   dias ate `FIM_CONTEUDO_ALVO`; alvo vencido -> ritmo `None`, nunca um divisor inventado.
   Teste com Fase 2 e reserva NO BANCO provando que nao entram no numerador.
2. `cota_do_dia` (PURA): q pendentes das semanas do plano ate a semana de CALENDARIO
   corrente / dias que faltam nela; atraso de semana anterior entra e e declarado; antes da
   semana 1 conta a partir do inicio dela; depois do calendario -> `None`. Calendario = o
   do `plano_trilha.json` (a mesma fonte que o `aplicar_trilha` consome).
3. Cada regua declara o que mede: "marco de volume" (Volume), "ritmo da Fase 1" e "cota do
   dia" (Cronograma); o rotulo `2o ciclo 12k` passa a dizer o marco real. O recomendador
   recebe os numeros da Fase 1.

**Fatia 3 -- o gerador entra no repo (peca central)**
4. Autoridade em 3 camadas, todas DADO versionado: parametros -> gerador -> `plano_trilha.json`.
   Edicao manual SO na camada custom (JSON), nunca no gerado; o gerado carrega marca de
   gerado e o `_doc` deixa de prometer "editavel a mao".
5. Entrada fixada junto: entrada + parametros + codigo = saida.
6. **GOLDEN:** o gerador do repo, com a entrada fixada, reproduz os 115 overrides, o
   calendario e os simulados do `plano_trilha.json` atual. Delta = achado, reportado ao
   `/ai-eng` ANTES de qualquer conserto.
7. **PROPRIEDADE** sobre o `plano_trilha.json` gravado: blocos CM/CIR/GO/PED dentro de
   PISO-TETO do orcamento de listas, semanas da Fase 1 dentro do calendario, 6 simulados em
   6 semanas distintas, chaves unicas, marca de gerado presente.
8. So entra o que e re-executado; o resto do scratch fica fora (registro).

**Fatia 2 -- a reserva vista uma vez**
9. `plano.py --reserva` (read-only): as linhas pendentes fora da fila, ordenadas por peso UERJ
   desc, WARN para faixa alta de `prevalencia_uerj.json`, linha SEM tema casado listada como
   tal (nunca contada como peso zero). Saida em arquivo que o HANDOFF aponta.

**Fatia 4 -- pequenos do veredito**
10. `--mover` com trilha ativa RECUSA (exit 2) linha da Fase 1 -- de onde sai OU para onde
    vai -- e aponta a camada custom.
11. `links_exercicios.json` removido (raio medido por grep em codigo, skill e command).
12. `links_listas.json` carrega o estado explicito "nao existe lista".

**Fatia 5 -- divida na fonte**
13. Clausulas novas do item 1.10 anotadas + catraca WARN (contagem de orfas nao sobe sem
    mudar a base no mesmo commit).
14. Campo de custo auto-relatado fora do template dos filhos (custo = `usage` do harness).

**Toda fatia:** suite verde, `auto_check --changed` PASSED, `selo.py` verde, commit proprio.

## Implementacao (s189, 18-19/09/2026) -- DoD item a item

| DoD | Estado | Evidencia |
|---|---|---|
| 1 ritmo da Fase 1 | FEITO | `7f311fd`; `test_ritmo_da_fase1_nao_conta_fase2_nem_reserva` (Fase 2 e reserva NO BANCO); banco real 273,3 -> 74,8 |
| 2 cota do dia | FEITO | `7f311fd`; `test_cota_do_dia_divide_o_restante_da_semana_pelos_dias`; real ~81q (19-20/09) |
| 3 reguas declaradas | FEITO | `7f311fd` + `f12c4ef` (corte do boot declarado; cota presa ao cap do hook) |
| 4 tres camadas de dado | FEITO | `342a86e`; `core/cronograma/trilha/{parametros,custom}.json`; `_doc` "NAO EDITAR A MAO" + `gerado_por` |
| 5 entrada fixada | FEITO | `core/cronograma/trilha/entrada/` + mapa UERJ versionado (identico ao do scratch) |
| 6 GOLDEN | FEITO, delta 0 | golden de PARTIDA no scratch (copia) + `test_golden_o_arquivo_gravado_e_a_saida_do_gerador`; `--semear --dry-run`: 0 nova, 0 mudaria |
| 7 PROPRIEDADE | FEITO | `test_propriedades_da_trilha_gravada` + `test_propriedade_pega_saida_adulterada`; regua do gerador (declarado) |
| 8 so o re-executado entra | FEITO | agrega/reconcilia/gera/custom portados; relatorio/selo/veredito/links/classificacao ficam no scratch |
| 9 reserva | FEITO | `83b3e50`; `docs/RESERVA-FASE1.md` (174 linhas; 13 de faixa ALTA sem cobertura na fila) |
| 10 guard do `--mover` | FEITO | `390ee43`; `test_mover_recusa_linha_da_fase1_com_a_trilha_ativa` + `test_cli_mover_le_a_trilha_do_disco`; banco real recusou |
| 11 `links_exercicios.json` | FEITO | `390ee43`; 0 consumidores; lapides |
| 12 estado "nao existe lista" | FEITO | `390ee43`; `test_links_listas_da_estado_explicito_a_toda_tarefa` (faltando = 0) |
| 13 clausulas + catraca | FEITO | `521c885`; 134 -> 127; `BASE_ORFAS` + `test_catraca_de_orfas_so_avisa_quando_a_contagem_sobe` |
| 14 custo pelo harness | FEITO | `521c885`; clausula 10 do F93 + AGENTE 1.1 |

**Achados de implementacao (fora do DoD):** F125 -- loop infinito herdado no agendamento do gerador
(corrigido, regressao com prazo); `diferenca_semeada` no dry-run (sem ela, "0 diferenca" nao tinha
prova); o "+7 orfas da s188" era atribuicao errada (medido em worktree: s187). **Nao feito:** fatia 6
(regra de recalibracao como dado + gold set de MFC) -- opcional por decisao do `/ai-eng`; a regra
estatistica vai como TEXTO no HANDOFF da s190.

## Scope
`tools/day_plan.py`, `tools/plano.py`, `tools/trilha.py` (novo), `core/cronograma/trilha/`
(novo: parametros, custom, entrada fixada), `core/cronograma/plano_trilha.json` (so `_doc`
e marca de gerado), `core/cronograma/links_listas.json`, testes, `/engenharia-cli`,
`cronograma-contract`, ledger.

## Anti-scope
Nenhuma mudanca de CONTEUDO da trilha (overrides, calendario, simulados). Nenhuma mudanca de
status no banco. Recomendador nao passa a usar a cota (so recebe os numeros corrigidos).
Fatia 6 (regra de recalibracao como dado) so se sobrar noite. Sem exportador da entrada
(re-snapshot do banco): a entrada fica fixada em 18/09 e isso e declarado.

## Technical Decisions
- **Divisor da Fase 1 continua sendo `FIM_CONTEUDO_ALVO`** (decisao da s159, travada por
  `test_ritmo_usa_alvo_de_conteudo_declarado`): o defeito do F123a era o NUMERADOR. O
  calendario da trilha entra so na cota (que precisa do fim da semana).
- **Cota por semana de CALENDARIO, com atraso somado.** "Semana corrente = menor com
  pendencia" continua sendo a POSICAO; a cota responde outra pergunta ("quanto por dia para
  fechar ate o fim desta semana"). Com a semana do plano, um atraso de 1 semana daria
  divisor zero.
- **Custom vence gerado, por chave.** A camada manual e aplicada depois do gerador; a
  duplicata de chave e resolvida la, nunca no `aplicar_trilha` (que segue recusando).

## Limites declarados
- A entrada do gerador e um snapshot de 18/09: progresso posterior nao muda a PRIORIDADE
  (muda o status, pelo re-seed). Re-snapshot exige exportador -- nao construido.
- Ritmo e cota sao aritmetica sobre `q_previstas`; tarefa de aula (q=0) nao pesa.
