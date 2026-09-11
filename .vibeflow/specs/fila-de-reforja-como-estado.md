# Spec: A fila de reforja vira ESTADO (B2 / F40+F41+G7)

> Escrita em 2026-09-10 (s176), item **0.3** do Tier 0. Ordem: `/ai-eng` N=78, regime D71.
> Ledger: `AUDITORIA_MEDHUB.md` F40 · F41 · F82 · inventário `docs/MEMORIA-AUDITORIA.md §11` (G7).
> Toda medição abaixo foi feita nesta sessão, com o comando registrado (D72).

## Objetivo

Tirar o passivo de reforja da prosa e colocá-lo num estado consultável, com **fechamento
explícito e verificado**. Hoje uma marcação de reforja é uma frase num `HANDOFF.md` ou num log de
sessão: ninguém sabe quantas estão abertas, qual já foi resolvida, nem se a resolução resolveu.

## Contexto -- as três medições que definem o problema

**1. A cifra do passivo nunca foi a mesma duas vezes.** G7 registra **12 / 13 / 15 / 38** em
sessões diferentes (uma delas com `#1424` duplicado). Quatro números para a mesma pergunta é a
assinatura de contagem que sai de leitura humana, não de ferramenta -- o mesmo defeito que o
`CONTRATO_REVOGADO` sofreu no F90.

**2. Marcar não faz nada.** `#792` foi marcado para reforja em **três sessões diferentes** e está,
medido agora, em `card_version = 1`: nunca foi tocado. A marcação viajou de HANDOFF em HANDOFF
como texto e morreu como texto.

**3. 🔴 Reforjar não prova que resolveu -- e isto é o coração da spec.** O F82 estabeleceu que
`card_version` **não é evidência de reforja feita**: `#321` está em `v2` com o defeito intacto.
Esta sessão mediu uma **segunda instância, mais recente e mais dura**: `#1568` recebeu um evento
`reforja` em 2026-09-09 (`version_antes: 1 -> version_depois: 2`, campos `frente_pergunta` e
`verso_*`) e **continua disparando o predicado P3** (`checar_contrafactual_mal_formado`,
implementado hoje no item 0.2). Alguém reescreveu a pergunta e o defeito sobreviveu à reescrita.

```
grep '"tipo": "reforja"' history/generation_log.jsonl   -> 5 eventos (todos 2026-09-09, pos-F82)
#1568: evento reforja v1->v2 em 09-09  E  checar_contrafactual_mal_formado(#1568) dispara hoje
```

Conclusão que governa o desenho: **nenhum sinal de "alguém editou" pode fechar uma marca.**
Nem `card_version`, nem o evento `reforja`, nem a palavra de quem editou. Só a **re-verificação do
defeito que motivou a marca**.

## Definition of Done

1. **`reforja_marks` é APPEND-ONLY e o estado é DERIVADO.** A tabela guarda *eventos*
   (`marcada` | `fechada` | `descartada`), nunca um campo de status mutável. Consequências
   verificadas por teste: (a) marcar o mesmo card 3× produz **3 linhas** e a fila mostra
   "3 marcações" -- o `#792` deixa de ser anedota e vira contagem; (b) não existe coluna booleana
   que alguém possa virar; (c) o histórico de uma marca sobrevive ao fechamento.
2. 🔴 **Fechamento é VERIFICADO, não declarado.** `fechar_reforja(card_id, motivo)` **re-roda o
   predicado que motivou a marca** e **recusa** o fechamento se o card ainda dispara, com mensagem
   nomeando o predicado. Fixture obrigatória: **`#1568`** -- tem evento de reforja registrado, tem
   `card_version=2`, e a tentativa de fechar sua marca de `contrafactual_mal_formado` **falha**.
   Fechar exige `--forcar` com justificativa escrita, que fica gravada na linha.
3. **`descartada` é estado de primeira classe.** Nem toda marca vira reforja: "olhei e não era
   defeito" é um desfecho legítimo e **diferente** de "resolvi". Sem ele, o operador fecha marcas
   falsas como se fossem consertos e a métrica mente. Exige motivo escrito.
4. **A cifra sai de ferramenta, nunca de leitura.** `python tools/reforja.py --fila` imprime
   abertas / fechadas / descartadas com contagem, e é a **única** fonte citável. Um número de
   passivo escrito à mão em `HANDOFF.md` passa a ser claim que envelhece (D67).
5. **Backfill da prosa = dry-run + COUNT-ASSERT, execução do OPERADOR.** `--backfill --dry-run`
   lê a lista de marcas conhecidas, declara **quantas linhas vai criar antes de criar**, e não
   escreve nada. `--backfill --apply` exige que o número observado bata com o declarado. Decisão
   de rodar é dele (Tier 2), não minha.
6. **Craftsmanship gate:** `auto_check --changed` verde; suíte completa verde (baseline **485**);
   `sqlite3` só em `app/utils/db.py` (camada de acesso, `AGENTE.md §6`); ASCII limpo.

## Escopo

- `tools/init_db.py`: +1 tabela `reforja_marks` (`CREATE TABLE IF NOT EXISTS`, padrão do arquivo).
- `app/utils/db.py`: `marcar_reforja`, `fechar_reforja`, `fila_reforja` -- os únicos que tocam a
  tabela (allowlist F49 ganha a entrada).
- `tools/reforja.py` (novo): CLI `--fila`, `--marcar`, `--fechar`, `--backfill`.
- `tools/test_reforja_marks.py` (novo).
- `.claude/commands/estilo-flashcard.md`: assinatura canônica do CLI novo (§7.2).

## Anti-escopo

- 🔴 **Não reforjar card nenhum.** Esta spec constrói a fila; encher e esvaziar é trabalho de
  conteúdo, do operador (régua de "card bom" = F87, Tier 2).
- 🔴 **Não executar o backfill.** Só o `--dry-run` roda aqui. O `--apply` é decisão do operador.
- Não tocar FSRS, `card_version`, `quality_source` ou o texto de card algum.
- Não inferir marcas automaticamente a partir dos predicados do 0.2. Um card que dispara um WARN
  **não** vira marca sozinha -- a triagem é humana (lição do F87: o harness mede forma, não
  rendimento). O CLI *oferece* os candidatos; quem marca é gente.

## Ponto cego DECLARADO

O fechamento verificado só alcança marcas cujo motivo é um **predicado existente**. Marca de
defeito que nenhum predicado mede -- "pacote de fatos", "pergunta circular", o eixo C semântico --
fecha por palavra humana, e a linha registra isso explicitamente (`evidencia: 'humana'`). Não é
falha da spec: é a fronteira do que hoje é verificável. Nunca convertida numa métrica inventada.
