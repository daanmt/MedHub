# Spec: O reconcile de volume (W1) passa a REPORTAR -- planilha x db com a IDADE da planilha (B3 / F35)

> Escrita em 2026-09-10 (s176, janela 2), item **0.5** do Tier 0. Ordem: `/ai-eng` N=78, regime D71.
> Ledger: `AUDITORIA_MEDHUB.md §3i` (F35) · inventario `docs/MEMORIA-AUDITORIA.md §11` linha 0.5.
> Toda medicao abaixo foi feita nesta sessao, com o comando registrado (D72).

## Objetivo

Tirar a condicao **W1** do `reconcile-contract` da prosa e colocar no boot uma linha que sempre sai:
quanto a planilha diz, quanto o db diz, e **ha quanto tempo a planilha foi alimentada pela ultima
vez**. Nao bloqueia nada. O que ela mata e o silencio: hoje o drift de volume so existe quando
alguem, por conta propria, resolve olhar.

## Contexto -- as tres medicoes que definem o problema

**1. Nao existe uma linha de codigo que compare a planilha com o db.**

```
grep -rniE "planilha|dashboard" --include=*.py tools/ app/   -> 0 comparacoes
```

Os unicos dois reconciles da historia do projeto viraram **script one-shot escrito a mao** e foram
para `tools/_archive/migrations/`: `fix_data_delta_075.py` (s075) e `fix_data_delta_110.py` (s110).
Duas ocorrencias, dois artefatos descartaveis, zero mecanismo. O contrato declara W1 como WARNING
com enforcement `manual`; a coluna diz a verdade.

**2. O drift de 76q da s110 foi achado pelo OPERADOR, nao pelo sistema.** A docstring do script
guarda a frase: *"Usuario reportou performance desatualizada (4660 real vs 4584 relatado)"*. O gate
que deveria ter falado eram os 76q parados entre a planilha e o db; quem falou foi ele.

**3. 🔴 O total batendo nao significa que esta reconciliado.** No mesmo s110, de 4 achados, **3 eram
mislabel de area** (`GO` -> Ginecologia; 3 linhas de `Clinica Medica` -> Infecto/Hemato/Oftalmo) e o
relabeling **nao mudou o total** -- "permanece 4584", diz a docstring. Uma comparacao so de total
teria dado verde com o defeito inteiro em pe. E por isso que o proprio W1 manda reconciliar contra
**a soma das abas por disciplina**, nunca contra o Quadro Geral (que ja teve bug de formula
confirmado em Obstetricia, s075).

**Estado medido hoje (2026-09-10):**

```
python -c "sqlite3 ipub.db: SUM(questoes_feitas), MAX(data_sessao) FROM sessoes_bulk"
  -> db: 7126 questoes, ultimo lancamento 2026-09-09, 124 linhas desde 2026-04-16
SELECT chave FROM preparacao_estado
  -> semana_conteudo · condicao_dia · cronograma_conclusao_drive   (nenhum snapshot de planilha)
```

O numero **6.288** que o `HANDOFF.md` carrega como "Dashboard EMED" **nao tem data nem comando** --
e claim que envelheceu (D67/G8). Esta spec nao o adota: ele entra como o primeiro `NAO MEDIDO`.

## Definition of Done

1. **A linha SEMPRE sai no Plano do Dia, inclusive sem dado.** Sem snapshot registrado, o boot
   imprime `NAO MEDIDO` + o comando que registra -- nunca omite a linha, nunca assume delta zero.
   Ausencia de medicao e um estado reportado, nao silencio (honest-negative, `evidence-governance
   §7`, mesma licao do F91).
2. **O snapshot da planilha e ESTADO gravado, com as duas idades separadas.** Chave
   `planilha_snapshot` em `preparacao_estado` (writer unico `db.set_preparacao`, allowlist F49
   intacta), carregando: `por_area`, `total`, `ultimo_lancamento` (data da ultima tarefa lancada
   DENTRO da planilha) e `lido_em` (quando o agente leu). As duas idades respondem perguntas
   diferentes -- *"a planilha ainda e alimentada?"* e *"minha copia dela e velha?"* -- e colapsa-las
   perde a primeira, que e a do F35.
3. 🔴 **A comparacao e POR AREA, e o estado tem nome.** `reconcile_planilha()` devolve um de
   **oito** estados nomeados: `nao_medido` · `alinhado` · `divergente_por_area` (total bate, area
   nao -- a assinatura de mislabel da s110) · `import_pendente` (planilha > db: volume lancado e
   nunca importado, o caso dos 76q) · `planilha_atrasada` (db > planilha E ultimo lancamento da
   planilha anterior ao do db) · `divergente` · `abandonada` · `sem_detalhe_area`. Teste com os
   numeros reais da s110 para `import_pendente` e para `divergente_por_area`.
4. **Reporta, nunca bloqueia.** Nenhum caminho novo levanta excecao para fora, nenhum exit code
   muda, nada entra no `auto_check` como BLOCK. Falha do proprio leitor degrada para `_warn_degradacao`
   em stderr e a linha sai dizendo que degradou. Teste: leitor que explode nao derruba `build()`.
5. **O ingestor recusa planilha internamente inconsistente.** `--total` informado junto com
   `--por-area` e divergente da soma das abas = **erro fail-loud com os dois numeros na mensagem**
   (e exatamente o bug de formula do Quadro Geral, s075). Data no futuro e total negativo tambem
   recusam. Gravar dado que ja se sabe torto e pior que nao gravar.
6. **A resposta do operador muda o PESO, nao o mecanismo.** `--abandonada "<motivo>"` registra a
   declaracao e a linha do boot passa a dizer *comparacao suspensa (declarada em DD/MM)* em vez de
   cobrar -- sem desligar o mecanismo e sem apagar o ultimo delta medido. A pergunta *"a planilha
   ainda e fonte?"* (Tier 2.4) segue aberta e esta spec **nao depende** dela.
7. **Portadores atualizados no mesmo commit:** `reconcile-contract.md` W1 troca `manual` pelo
   enforcement real; `/importar-planilha` ganha o passo do snapshot + a assinatura canonica do flag
   novo (§7.2: assinatura de CLI vive em UMA skill) + `sync_skills`. `auto_check --changed` verde e
   suite completa verde (baseline **503**).

## Escopo

- `tools/importar_sessoes.py`: `--snapshot` (grava), `--show-snapshot` (le). Nao abre `sqlite3`:
  chama `db.set_preparacao`/`db.get_preparacao`.
- `tools/day_plan.py`: `reconcile_planilha()` + a linha no `render()` + flag `--planilha`.
- `tools/test_reconcile_planilha.py` (novo).
- `core/contracts/reconcile-contract.md`: linha W1 da matriz + nota.
- `.claude/commands/importar-planilha.md` (+ espelho gerado).

## Anti-escopo

- 🔴 **Nao ler o Drive.** Codigo nunca fala com o MCP (regra da propria skill). O agente le e passa
  os numeros; o F36 (transporte de binario) nao e desta spec e nao e consertado por ela.
- 🔴 **Nao importar nem corrigir volume nenhum.** A spec mede e reporta; `--rows-file` segue sendo o
  unico caminho de escrita em `sessoes_bulk` e nada aqui o chama.
- **Nao validar vocabulario de area.** Area fantasma (`GO`, `Clinica Medica`) e o **F89**, item
  **0.6**, o proximo da fila. Aqui uma area desconhecida aparece no relatorio como divergencia com
  o nome cru -- que e justamente o sintoma que o 0.6 vai consertar na origem.
- Nao promover W1 a BLOCKING. O contrato ja diz o porque: plano/planilha nao e verdade-de-estado.

## Ponto cego DECLARADO

Quem alimenta o snapshot e o agente, lendo a planilha. **Um snapshot errado produz um relatorio
errado com a mesma confianca de um certo** -- a spec valida coerencia interna (soma das abas x
total declarado, datas no passado), nunca a fidelidade ao que esta no Drive. Nao ha, e nao se
inventa aqui, um gate que compare o snapshot com a planilha real: enquanto o F36 nao tiver
transporte proprio, a fidelidade da leitura fica declarada como **nao verificavel** (§10.8), e a
propria linha do boot exibe `lido_em` para que a idade da copia nunca passe por medicao fresca.
