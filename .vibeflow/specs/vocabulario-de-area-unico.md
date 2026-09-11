# Spec: `AREAS_VALIDAS` vira fonte unica e os writers de taxonomia param de aceitar area fantasma (F89)

> Escrita em 2026-09-10 (s176, janela 2), item **0.6** do Tier 0. Ordem: `/ai-eng` N=78, regime D71.
> Ledger: `AUDITORIA_MEDHUB.md §6q` (F89) · inventario `docs/MEMORIA-AUDITORIA.md §11` linha 0.6.
> 🔴 **A LISTA e do OPERADOR (RODADA 3, Tier 2.1). Esta spec entrega o MECANISMO, contra a lista ATUAL.**

## Objetivo

Fazer o vocabulario de area existir em **um** lugar e ser **verificado na porta de escrita**. Hoje ele
existe em duas copias divergentes, nenhuma delas consultada pelos writers que criam linha de
taxonomia -- e por isso as areas que uma migracao dissolveu voltaram sozinhas.

## Contexto -- as tres medicoes que definem o problema

**1. A dissolucao foi desfeita pelo proprio sistema.** A RODADA 1 do `normalize_taxonomia.py`
(s097) dissolveu `GO` e `Clinica Medica`. Medido no dry-run A6 (09-09): as duas existem **de novo**,
com ids novos -- `GO` 299, 301, 347, 348, 417 e `Clinica Medica` 285, 286: **7 linhas, 39 cards +
33 erros**. Nao e regressao de conteudo, e **reentrada pela porta dos writers**: operacao unica sem
gate de retorno.

**2. As duas copias do vocabulario ja divergem, e a divergencia esta documentada e nao corrigida.**

```
grep -n "AREAS_VALIDAS = " tools/registrar_sessao_bulk.py tools/performance.py
  -> registrar_sessao_bulk.py:31  (21 itens -- inclui "Simulado")
  -> performance.py:73            (20 itens -- SEM "Simulado")
```

O anexo de menores do ledger ja registrava *"`AREAS_VALIDAS` duplicada com divergencia
(performance.py sem 'Simulado')"*. Duas listas, uma delas errada, e o spec original de
`performance` previu isso como Risk #8 -- *"se surgir area nova, basta editar nos dois locais"*.
Editar nos dois locais e exatamente o que nao acontece.

**3. Nenhum dos 3 writers de taxonomia olha para lista nenhuma.**

```
insert_questao.py:208-217     SELECT ... INSERT INTO taxonomia_cronograma (area, tema, ...)
insert_card_base.py:59-68     get_or_create_tema -- idem
registrar_sessao_bulk.py:111-142  linha `[bulk] <area>` -- idem
```

Os tres criam a linha `(area, tema)` **que receberem**. `registrar()` valida `acertos <= feitas` e
nada mais; quem valida area e o `importar_sessoes`, **um nivel acima** e so no caminho da planilha.

## Definition of Done

1. **Uma fonte, e ela e DADO.** `core/areas.json` carrega o vocabulario; `app/utils/areas.py` e o
   **leitor unico**, no molde exato de `core/provas.json` + `app/utils/provas.py` (F88). A RODADA 3
   do operador passa a ser **edicao de dado**, nao de codigo -- que e o que "a lista e dele, o
   mecanismo e nosso" exige estruturalmente.
2. 🔴 **O leitor do vocabulario NAO e tolerante -- e o oposto do `provas.py`, de proposito.**
   Arquivo ausente, ilegivel ou vazio **levanta**; nunca devolve lista vazia. Um validador sem
   vocabulario ou reprova tudo ou aprova tudo, e as duas leituras sao falsas. `provas.py` pode
   degradar porque countdown ausente e cosmetico; vocabulario ausente e load-bearing (licao do F91:
   retorno degradado nao pode ser confundido com resposta valida). Teste com JSON quebrado.
3. **Duas listas nomeadas, e a diferenca deixa de ser acidente.** `AREAS_CLINICAS` (as 20) e
   `AREAS_AGREGADAS` (`Simulado` -- slot de volume, nao especialidade); `AREAS_VALIDAS` = a uniao.
   `performance.py` passa a listar gaps sobre `AREAS_CLINICAS`, preservando o comportamento atual
   **por decisao declarada** em vez de por copia desatualizada.
4. 🔴 **Fail-loud nos 3 writers de `taxonomia_cronograma`.** Area fora do vocabulario **recusa a
   escrita** com `AreaInvalida` nomeando a area recebida, a lista e o **palpite mais proximo**
   (`difflib`) -- `GO` -> *"voce quis dizer Ginecologia?"*. Vale para linha nova **e** para
   acumulo em linha fantasma ja existente: o fantasma para de crescer. Teste por writer.
5. **O passivo vira WARN, nao BLOCK.** Check novo no `auto_check` conta e nomeia as linhas de
   `taxonomia_cronograma`/`sessoes_bulk` com area fora do vocabulario -- **nasce WARN** (exit 0) e
   so vira BLOCK quando a base zerar, pela regra warning-first (s106/107). A consulta vive em
   `app/utils/db.py` (SSOT de SQL), nao no check.
6. **Nenhuma copia sobrevive.** Varredura no proprio teste: `AREAS_VALIDAS = [` literal existe em
   **zero** arquivos fora de `app/utils/areas.py`. `registrar_sessao_bulk.AREAS_VALIDAS` continua
   importavel (o `importar_sessoes` depende dele) -- passa a ser **re-export**, nao copia.
7. **Craftsmanship gate:** `auto_check --changed` verde; suite completa verde (baseline **523**);
   `sqlite3` so na camada de acesso; ASCII limpo; allowlist F49 inalterada.

## Escopo

- `core/areas.json` (novo, versionado) · `app/utils/areas.py` (novo, leitor unico).
- `app/utils/db.py`: `areas_fora_do_vocabulario()` (read-only).
- `tools/registrar_sessao_bulk.py`, `tools/insert_questao.py`, `tools/insert_card_base.py`: validacao.
- `tools/performance.py`: importa em vez de copiar.
- `tools/auto_check.py`: check WARN novo.
- `tools/test_vocabulario_area.py` (novo) + `pytest.ini`.

## Anti-escopo

- 🔴 **Nao mexer na LISTA.** O vocabulario entregue e **exatamente** o de
  `registrar_sessao_bulk.py` hoje (21 itens). Fundir, renomear ou acrescentar area e **RODADA 3**,
  decisao do operador (Tier 2.1).
- 🔴 **Nao limpar as 7 linhas fantasma.** Elas tem 39 cards + 33 erros pendurados; reclassificar e
  conteudo do operador. A spec impede o **crescimento** e **conta** o passivo. Migrar sem a decisao
  dele repetiria o erro da RODADA 1: operacao unica sem gate de retorno.
- Nao normalizar rotulo automaticamente (`GO` -> `Ginecologia` no ato da escrita). Adivinhar area e
  como o `Clinica Medica` da s110 virou 3 areas erradas. O writer **sugere** e recusa; quem decide e
  quem chamou.
- Nao promover o check a BLOCK nesta spec (a base nao zerou).

## Ponto cego DECLARADO

O gate e de **vocabulario**, nao de **verdade**: ele garante que a area existe na lista, nunca que e
a area **certa** para aquele tema. Registrar Apendicite sob `Pediatria` passa por todos os checks.
Essa camada e a RODADA 3 (conteudo, do operador) e continua **sem instrumento** -- declarado, nao
convertido em metrica (§10.8).
