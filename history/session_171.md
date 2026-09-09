# Session 171 -- Simulado 8 (82,1%) + 4 hotfixes de engenharia + 6o principio do contrato de card

**Data:** 2026-09-08 · **Ferramenta:** Claude Code (Opus 5) · **Co-sessao:** `/ai-eng` (Fable 5.1), N=76, encerrada em `758b7fd`

---

## 1. Simulado 8 (ENARE/ENAMED 2025) -- **78/95 = 82,1%**

78 certas · 17 erradas · 4 anuladas (Q16, Q42, Q56, Q84) · 1 nao computada (Q91, DESATUALIZADA sem resposta).

🏆 **Maior resultado do ciclo.** Media historica em simulado: **60,8%** (441q acumuladas). O gargalo n1 do
`ESTADO.md` -- "banco 78,8% x simulado 60,8%" -- **se inverteu**: o simulado passou o banco.

**Metodo de extracao (reutilizavel).** O PDF do Estrategia traz `CERTA`/`ERRADA` + "N% ACERTARAM" + o
percentual de marcacao de cada alternativa, mas **nao traz a alternativa marcada** (e estado visual, nao
texto). Achado que economiza trabalho: **a correta e a alternativa cujo percentual bate EXATAMENTE com o
"N% ACERTARAM"** -- fechou em 17/17 sem uma ambiguidade. O gabarito e derivavel; a marcacao, nao.

⚠️ **Heuristica testada e REFUTADA:** supus que a marcacao seria o distrator dominante. O primeiro exemplo
real derrubou (Q77: dominante era C com 22%, ele marcou D com 15%). Confirmado em todas: marcou B com 7%,
B com 6%, D com 18%, B com 14%. **Nunca o dominante.** Print por questao e obrigatorio, nao conveniencia.

## 2. 🔴 A correcao do operador (reincidencia da s150)

Classifiquei 3 dos 6 primeiros erros como "mesmo bug de leitura" (discriminador que exclui) em vez de lacuna
de conteudo. Correcao literal dele:

> *"essa foi uma prova bem dificil e notei diversas lacunas de conteudo. voce parte do ponto que sei as
> coisas, muitas vezes por ja ter visto o tema, ou por termos resumo, mas o aprendizado e um movimento
> circular, repetir e revisar, expandindo as nuances com o tempo -- ninguem aprende tudo de uma unica vez."*

**Mecanismo do meu erro:** usei o discriminador como PROVA de que o conteudo estava consolidado. Mas "sem
diarreia exclui C. difficile" so funciona se Ogilvie ja estiver no diferencial; "fistulizacao exclui linfoma"
pressupoe a escrofula consolidada. **Inverti a proporcao 80/20** do `analisar-questao` (80% diagnostico
clinico x 20% padrao de execucao). Reclassificar lacuna como bug de execucao e conveniente e errado -- muda
a remediacao de estudo para ritual. Registrado em `feedback_diagnostico_resumo_nao_e_conhecimento`.

## 3. 🔴 O resumo estava ensinando o erro (causa-raiz da q36)

Auditoria de evidencia (`evidence-governance`) sobre a q36 (colangite) achou o
`resumos/Cirurgia/Abdome Agudo Inflamatório - Colecistite e Colangite Aguda.md` **contradizendo a si mesmo**:

- §12.3, correto e verbatim TG18: *"Grau I (leve): antibiotico costuma ser suficiente; considerar drenagem
  se nao houver resposta nas primeiras 24 h."*
- Armadilhas de Prova, **sem qualificador**: *"Tratar colangite aguda so com antibiotico, sem drenagem"*.

A segunda anula a primeira. **Quem memoriza a armadilha marca papilotomia -- foi o que ele fez.** Provavel
causa-raiz de colangite ser a 5a area mais fraca (18 erros) e de Toquio ter saido errado 3x na s150.

**Nao ha drift banca x evidencia:** a ENARE esta alinhada ao TG18; quem diverge e o comentario do curso.
A serie que VALIDOU o TG13/18 (Kiriyama 2018, PMID 29032610) mostra ganho de mortalidade da drenagem precoce
**apenas no Grau II** -- zero no Grau I. Kill shot lexical: "urgente" no TG18 e vocabulario de **Grau III**.
Armadilha refinada (nao removida), commit `9994c78`.

## 4. Contrato de flashcard ganha o 6o principio

Decisao do operador, formulacao literal: *"mais do que treinar a distincao entre o marcado e o gabarito, a
questao incorreta e uma oportunidade de revisar os nos que conectam o tema as alternativas e ao raciocinio
mais complexo, conectando com outros temas proximos / nucleares."*

**As alternativas erradas nao sao descarte -- sao nos.** Caso que originou: na q77, as QUATRO alternativas
erradas eram todas causas de **oligo**amnio, cada uma por mecanismo distinto. Guarda contra o modo de falha
obvio: **mais cards, nunca cards maiores** -- ampliar escopo nao afrouxa atomicidade. Commits `142a96c`
(principio) e `8f714ff` (a `description` do frontmatter ficou dizendo "5 principios"; o `sync_skills --check`
e cego a drift de `description`, fraqueza ja registrada no anexo da s160).

## 5. Triagem dos cards: 85 -> 45

O 6o principio multiplicou o volume (3 subagentes, 5 cards por erro). Ordem do operador: *"Seu papel e tria-los,
e eleger os melhores e mais prevalentes."* Criterio: **nucleo do erro intocavel** (1 por questao) + **no de alto
rendimento** (reusavel fora da questao) + **corte** de trivia que so existe porque a alternativa existia.

- ⚰️ Corte mais facil: a vida do caramujo (q54) -- o proprio comentario do curso chama de *"muita maldade"*.
- ⭐ No que mais se justificou: *"por que insuficiencia uteroplacentaria, RCF e pos-datismo cursam com
  oligoamnio?"* -- um card que resolve **tres alternativas de uma vez** pelo mesmo mecanismo.
- 🔴 **Camada de prevalencia nao alcanca:** `prevalencia_enamed.json` cobre 89 temas e casou com **1 dos 17**
  (os nomes vem dos decks EMED, nao da taxonomia). Nao forcei casamento -- triagem foi por rendimento medido,
  nao por prevalencia fingida. **Achado de alcancabilidade, candidato a F-id.**

**Dois defeitos meus, achados pelos subagentes:** (a) marquei a q36 com `status: banca-divergente` no seed
ANTES da auditoria fechar -- e `insert_questao.py:147` **descarta silenciosamente todos os cards** de questao
com esse status (F26); teria perdido os 3 cards do tema onde ele tem 18 erros. (b) `status: anulada` na q50
faria o mesmo. Ambos removidos: a lacuna dele no calendario e real e independente do defeito da questao.

**Normalizacao de taxonomia (F67):** os 3 subagentes divergiram em `area`/`tema` e criariam 6 linhas novas --
incluindo `HIV/AIDS` com `(Infecto|HIV)` ja existente. Casado com o que existe antes de persistir.

## 6. Engenharia -- 4 commits com o `/ai-eng` antes do congelamento

| commit | o que |
|---|---|
| `d0d918c` | **Memoria da auditoria** entra no repo (`docs/MEMORIA-AUDITORIA.md`), 2 fios mecanicos, 13 divergencias corrigidas |
| `09ce3de` | **F82-F85** numerados + lapides de F5/F8 -- G2 e G9 fechados |
| `9db9d7d` | **Hotfix G12/G13/G11**: clausula REVOGADA que continuava prescrevendo; gate `CONTRATO_REVOGADO`, 18 achados -> 0 |
| `68efb69` | **Hotfix F86**: o gate do F43 validava por SUBSTRING -- "mencionada != inscrita" |

🔴 **O achado que mais assusta (F86):** `test_contrato_revogado.py` nasceu **fora do `python_files`** -- 12
testes escritos, ZERO executados. So percebi porque a suite ficou em 395 depois de eu adicionar 12 testes.
E o `SUITES_ORFAS`, que existe exatamente para isso, **passou verde**: valida por substring, e o nome do
arquivo aparecia numa string de WARN que eu tinha acabado de escrever. **A mencao que satisfez o verificador
foi produzida pelo proprio ato de verificar.** Suite 395 -> 413.

**Serie de contagem do dia** (por que o gate existe): leitura humana **1** -> enumeracao sobre grep truncado
em 110 colunas **10** -> grep integral **12** -> lint **18**. Nenhum humano chegou ao numero.

## 7. Estado do repo e proxima sessao

Fila de engenharia (itens 3->7: spec F81 com campo `classe` no contador · `reforja_marks` · gate de selecao
0->1 · alcancabilidade + 3 riders · hotfix F85) **CONGELADA** para sessao dedicada com contexto limpo dos dois
lados. **D71:** implement E audit sao daqui (loop vibeflow); o `/ai-eng` orquestra; silencio dele = GO.
Reencontro: 1 linha de presenca de quem chegar primeiro; o decidido sai do **ledger**, nunca da memoria.

**Pendente para a proxima sessao (contexto limpo, por decisao do operador):**
1. Inserir o lote: `python tools/insert_questao.py --errors-file core/simulados/_s8_erros_batch.json`
   (17 erros + 45 cards, transacao unica com rollback total). O corte pode ser derrubado -- os 85 candidatos
   estao em `_s8_candidatos_full.json`.
2. **Colher o feedback dele sobre os cards durante o drill e usa-lo para reajustar o contrato**
   (`estilo-flashcard.md`) -- pedido explicito. E o primeiro teste do 6o principio em producao.
3. Transcricoes de duas aulonas do Estrategia: **Obstetricia** (ele avaliou como excelente) e **Pediatria
   parte 2** (assistira amanha).

---
*Anterior: `session_170.md` · Macro: `ESTADO.md` · Ledger: `AUDITORIA_MEDHUB.md` · Auditoria: `docs/MEMORIA-AUDITORIA.md` · Trocas: `history/exchange-log.jsonl`*
