# Session 168 -- Aula-base do Sprint S17-S20 (13 temas) + precificacao da grade + revogacao do sprint de cards
**Data:** 2026-09-07
**Ferramenta:** Claude Code (Opus 5, 1M)
**Continuidade:** Sessao 167 (90 cards drenados + Simulado 7 autopsiado)

---

## O que foi feito

### 1. Decisao do mix 07-13/09 (item 1 do HANDOFF, pendente desde a s167)
O usuario aceitou a proposta: **cards de volta ao teto de 60/dia, tardes de volta as questoes**. Argumentos que fecharam a decisao, na ordem do peso: (a) o sprint de 120 cards/dia existia para pagar divida e a divida zerou na s167; (b) o gargalo nº 1 declarado e execucao de prova (banco 78,8% x simulado 60,8%), e **card nao treina execucao** -- 8 dos 18 erros do S7 foram execucao pura; (c) setembro estava em ~32q/dia contra os ~62 que a meta do mes pede.

### 2. Aula-base do sprint -- artifact expandido de 4 para 13 temas
Entregue como Artifact HTML (`artifacts/aula-s17.html`, mesma URL da 1a publicacao). Comecou como "A Escada da S17" (4 temas: Diarreia, SUA, Urologia, Pneumonias Bacterianas) e virou **"Sprint S17-20"** (13 temas, 310 KB, 2.377 linhas) depois que o usuario homologou o recorte verde das 4 semanas.

Temas novos (9), todos ancorados no PDF-fonte do EMED, com profundidade calibrada pelo degrau do `day_plan --difficulty`:
APS no Brasil (D10) · Etica Medica (D10) · Principios e Diretrizes do SUS (D5) · Financiamento em Saude (D10) · Pneumonias na Infancia (D10) · Pre-Natal/Assistencia ao Parto/Vitalidade Fetal (D5/D5/D10) · Tumores Anexiais e Cancer de Ovario (D10) · DM na Gestacao (D2) · IC e HAS (D5/D2).

Cunhado por **1 subagent fable** (60 tool uses, ~646k tokens), com o brief carregando as travas: editar no lugar (URL amarrada ao path), nao publicar, preservar as 4 secoes originais verbatim, reusar os tokens de cor existentes, **um unico `max-width`**, ASCII limpo. Verificacao independente antes de publicar: title, 1 `max-width` (linha 57) + 3 media queries, **zero caracteres nao-ASCII**, tags balanceadas, 15 ancoras da rail batendo 1:1 com os `id`, e as 4 frases-assinatura das secoes originais intactas.

**Alvo prioritario atendido:** o bloco do SUS ganhou a tabela discriminadora operacional **ENTRADA (Universalidade) x ALOCACAO COMPARADA (Equidade) x COMPLETUDE (Integralidade)** com verbos-gatilho e "o que NAO e" -- e a 4a fraqueza persistente do usuario (19 erros, padrao cruzado em 3 questoes) e nao era lacuna de conteudo, era ausencia de discriminador.

### 3. Precificacao da grade -- achado de instrumento
O usuario pediu a contagem de questoes dos temas. Descoberta: **`core/cronograma/grade.json` nao guarda contagem por tarefa** -- so o total da semana. O contrato (`cronograma.py`, comentario no `parse_grade`) manda o consumidor **ratear igual** (`total_questoes / n_tasks`), o que na S17 daria 26,6q para tarefas que valem de 16 a 50. A contagem real veio de extrair `_parse_detail` direto do PDF. Validacao: a soma das tarefas bate **exatamente** com o total em todas as 4 semanas (293/380/449/301).

Anomalia levantada e depois **resolvida**: APS (Teoria III) da S17 saiu com 0q, o que tinha a forma de uma atribuicao trocada -- o screenshot do xlsx mostrou a mesma linha **riscada** pelo usuario. Os dois sinais concordam; nao era bug de parse.

### 4. Escopo do sprint homologado
Tres iteracoes ate acertar: minha 1a leitura de cor do xlsx errou (incluiu Cirurgia Vascular 43q, excluiu os blocos "Revisao por Questoes"); o usuario trocou a cor para verde; a 2a leitura ainda errou nas bordas; ele mandou as listas em texto e fecharam.

| Semana | Tarefas verdes | Questoes |
|---|---|---|
| S17 | 6 | 172 |
| S18 | 7 | 195 |
| S19 | 7 | 244 |
| S20 | 4 | 114 |
| **Total** | **24** | **725** |

**Decisao do usuario:** mirar na **S20 completa (725q) ate 12/09**; o pior caso aceito e nao chegar com a S20 inteira. Piso garantido S17+S18 = 367q (61q/dia). A aula cobre 267 das 725 (37%) -- e 194 das 367 do piso (53%).

### 5. Higiene de contrato
O usuario decidiu "manter o teto de 60 cards e subir se estourar", o que **revoga antes do prazo** a excecao datada do sprint de 120 cards/dia (s165, valida ate 13/09). Gravado com lapide em `core/contracts/fsrs-management-contract.md` e a linha correspondente do `ESTADO.md` corrigida. Registrado que o "subimos se estourar" e o `CAP_MULTIPLICADOR` ja vigente, nao uma segunda excecao. Nenhuma mudanca de codigo: `TETO_BASE`/`CAP_MULTIPLICADOR` nunca foram tocados. `auto_check --changed` PASSED, exit 0.

## Padroes de erro identificados
Nenhum bloco de questoes foi resolvido nesta sessao. O que se confirmou por leitura de dado, nao por drill:
- **Execucao segue como gargalo nº 1:** 8/18 erros do S7 foram execucao; corrigir so isso levaria 82 -> ~90. O ritual de 3 gestos ("qual dado EXCLUI?", "a pergunta pede X *e* Y?", rotular V/F no enunciado negativo) foi para o fechamento do artifact.
- **Dois dos tres blocos "Revisao por Questoes" do verde drillam frio:** Pre-Natal/Parto/Vitalidade Fetal (Vitalidade Fetal T e R ficaram fora do verde) e IC/HAS (HAS Revisao fora, IC ausente das 4 semanas). Sinalizado no `.scope` de cada bloco. O terceiro (SUS/APS/Etica) esta lastreado.

## Artefatos criados/modificados
- `artifacts/aula-s17.html` -- 4 -> 13 temas, `<title>` "Sprint S17-20", 310 KB (publicado, mesma URL)
- `core/contracts/fsrs-management-contract.md` -- lapide da excecao de 120 cards/dia
- `ESTADO.md` -- linha FSRS corrigida (excecao revogada + numeros da s167)
- `HANDOFF.md`, `history/session_168.md`, `history/INDEX.md`

## Decisoes tomadas
1. **Sprint S17-S20, 725q, mira na S20 completa ate 12/09.** Piso S17+S18 (367q). Nao chegar na S20 inteira e resultado aceito.
2. **Teto de cards volta a 60/dia** (max. 90 em divida). Excecao de 120/dia revogada 6 dias antes do prazo.
3. **Aula-base do sprint entregue de uma vez**, cobrindo os 13 temas -- em vez de uma aula por bloco ao longo da semana.

## Proximos passos
- Receber as primeiras questoes do sprint (registrar volume em `sessoes_bulk` ANTES de processar erros) e analisar os erros.
- Depois: 60 cards (47 na fila -- 15 atrasados, 14 agendados, **8 erros frescos do S7**, 10 novos -- + ~13 novos por prevalencia).
- Atencao ao **09/09: 34 cards agendados**, o pico da semana. Puxar menos novos nesse dia.
- Reforja pendente: 13 da s167 + 18 anteriores.
