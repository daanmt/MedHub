---
type: session
sessao: 185
data: 2026-09-17/18
modo: ENGENHARIA DEDICADA (janela 4)
---

# Sessao 185 -- Janela de engenharia: ondas 0, 1 e 2

**Regime:** D71 -- o MedHub implementa E audita; o `/ai-eng` ordena e decide em bifurcacao.
Permit do operador (verbatim, 17/09): *"esta e uma oportunidade para varrer todo o ledger e
corrigir tudo que for possivel do medhub. Em suma, e um projeto que nao pode ficar com o
backlog longo, haja vista que erros afetam a performance no estudo e tempo e um bem escasso."*
GO material dado pelo operador na abertura, com operacao destrutiva autorizada **sob o rito**
(dry-run + snapshot + COUNT-ASSERT), sem parar a cada lote.

## Placar

**11 commits, harness verde em cada um. Suite 714 -> 811.**

| id | estado | o que era |
|---|---|---|
| F102 | ✅ RESOLVIDO | drift falso em todo boot -- eram **3** defeitos, nao 1 |
| F107 | ✅ RESOLVIDO | `--errors-file` sem pre-check; 2 rollbacks totais medidos na s184 |
| F103 | ✅ RESOLVIDO | `[SEM-LASTRO]` falso por nome de arquivo |
| F106 | ❌ **RETRATADO** | achado FALSO -- o `[SEM-LASTRO]` original estava certo |
| F101 | ✅ RESOLVIDO | pendencia-fantasma no HANDOFF (gate novo) |
| F113 | ⚠️ PARCIAL | acentuacao: 1.796 correcoes, residuo irregular declarado |
| F98 | ✅ RESOLVIDO | card em relearning sumia do painel de blackout |
| F37 | ✅ RESOLVIDO no consumidor | ranking de resumo guiado por campo inflado 5,4x |
| R1 | ✅ entregue | otimizador read-only sob 2 visoes do revlog |
| R3-R6 | ✅ entregues | riders de doc |
| part-4 / part-6 | ✅ entregues | boot le `plano_tarefas`; ledger de listas |

## O que esta sessao aprendeu (vale mais que os fixes)

### 1. A familia "o sensor alcanca o caso real, ou so o que ele sabe ver?"

Tres gate-misses da mesma classe fecharam aqui, e nomea-los e o ativo:

- **presenca != cobertura** (`cli_signature_check`): deu `--dry-run` de `insert_questao`
  como coberto porque a string existia numa skill -- pertencendo a **outro CLI**.
- **escopo de intencao** (F113): o gate pergunta *"a reforja resolveu o defeito?"* para
  uma edicao so-acento, que nunca mirou defeito nenhum. Travou 125 cards.
- **escopo de consulta** (F98): a varredura do blackout filtrava `state = 2` e nao via o
  card em **relearning** -- que e exatamente o que a sessao de estudo produz.

### 2. Metrica auto-confirmante: o "0%" que eu reportei era falso

Depois do 1o lote do F113 reportei **875 -> 0**. Falso: medidor e corretor compartilhavam a
mesma lista de ~110 palavras, entao o medidor **so procurava o que o corretor sabia
consertar**. Um detector independente por sufixo mediu **897 cards (60,8%)** ainda sem acento.
🔴 **Quando o sensor e o remedio nascem do mesmo insumo, o verde nao e evidencia.**

### 3. "So-acento" nao e "semanticamente nulo" -- eu corrompi o baralho e reverti

A regra de sufixo `-encia` transformou **verbo em substantivo**: *"Como se diferencia, na
pratica, pancreas anular..."* virou uma palavra que nao existe. O invariante que eu usei
(`unidecode(antes) == unidecode(depois)`) prova **mesmas letras, NAO mesmo sentido** --
portugues tem pares minimos separados por acento. Sufixo NOMINAL (`-cao`, `-sao`, `-avel`,
`-orio`) e seguro; `-encia`/`-ancia` colidem com verbos em `-enciar`. **Quem pegou foi
leitura a olho de uma amostra aleatoria de 4 cards; nenhum gate meu teria pego.** Revertido
em 23 cards, com criterio limpo (a forma acentuada nao existe em portugues).

### 4. Achado de leitura humana tambem envelhece

O **F106** afirmava que "a esquistossomose vive em `Parasitoses.md`". Verificado: **uma
linha**, numa armadilha sobre a forma hepatoesplenica **dentro de um diferencial de cirrose**.
E o controle estava invertido -- o **RAPS**, registrado como verdadeiro-positivo, tinha
`## 4. Rede de Atencao Psicossocial (RAPS)` dedicado e estava na fila como tarefa de criar
resumo: **teria produzido o duplicado que o proprio F103 alerta**. A frase "vive em X.md"
saiu de um `grep -l`, que responde *"o arquivo contem a palavra"*, nao *"o arquivo cobre o
tema"* -- a mesma confusao presenca-x-cobertura que o achado pretendia denunciar.

### 5. Duas vezes o enunciado do achado estava errado sobre a propria causa

- **F98:** culpava a clausula de folga. A causa era o filtro `state = 2` da consulta.
  Minha 1a tentativa de remedio **quebrou 4 testes do F71 -- e eles estavam certos**: o
  contrato manda o card **ficar** e virar overflow declarado, que e a mitigacao que o
  operador aceitou. Eu ia trocar um gate-miss por violacao de contrato; a suite me segurou.
- **F37:** propunha recomputar a coluna a partir de `sessoes_bulk`. **Inexecutavel** --
  `sessoes_bulk` e por (area, sessao), sem tema. O dano real nao era o numero: era que ele
  **dirigia a prioridade de qual resumo escrever**, errando por duas ordens de grandeza
  (`[bulk] Neurologia` 149 x 1 real; `[bulk] Simulado` 270 x **0**).

## R1 -- a medicao que o R2 pedia

Cauda temporal hold-out, n=384, py-fsrs 6.3.1, 3.067 revisoes:

| | CRU | REMAP |
|---|---|---|
| ganho ao otimizar (log-loss) | +0,0019 = **nenhum** | **-0,0129 = real** |
| retencao otima | 0,70 | 0,80 |
| leech (`lapses >= 3`) | 18 | **44** |

Sobre as notas cruas, otimizar nao compra nada -- o delta e ruido em n=384 e o fit persegue
o rotulo errado. Sob o remap, o mesmo revlog da ganho uma ordem de grandeza maior. **F112
medido, nao argumentado.** Nao comparar log-loss ENTRE visoes (base rate diferente).
**26 cards leech estao invisiveis hoje.** Limites declarados: `compute_optimal_retention`
exige `review_duration` e o schema nao grava -- constante de 16.500 ms, entao o numero
minimiza **numero de revisoes**, nao tempo, e sai de grade de 6 valores.

## Decisoes do operador (17/09)

1. **R2 = opcao (b)** -- regua nativa do FSRS (`1 falhou · 2 lembrou com esforco · 3 lembrou ·
   4 sem esforco`). Municao que fechou a decisao: a regua do passo 4 **nao tem degrau de "sem
   esforco"**, entao `4 = cravou conceito + regra-mestre` e Good, e sob o remap **Easy fica
   vazio** -- a regua esta literalmente deslocada um degrau. Implementacao = onda 3, e **nao
   pousa sem mostrar a tela do player a ele antes**.
2. **F35 = part-8 DESTRAVADO** -- ele confirmou que nao reordena mais o xlsx a mao. Remocao do
   `--sync-drive` liberada, sob snapshot reversivel, nunca delecao seca.

## Numeros da janela

- **Onda 1:** 3 filhos Opus 5 em paralelo, ~820k tokens, ~45 min de parede, arquivos disjuntos.
- **F113:** 5 lotes, 1.796 correcoes, 4 snapshots do banco. FSRS preservado em todos
  (flashcards 1543 / fsrs_revlog 3067 / fsrs_cards 1543, identicos do inicio ao fim).
- **part-6 backfill (dry-run, nao aplicado):** 1 casada / 37 ambiguas / 78 sem match.
  34 das 37 ambiguidades sao o extensivo repetindo Teoria/Revisao do mesmo tema -- informacao,
  nao defeito do matcher.

## Fronteiras declaradas (nao ler verde de gate como limpeza)

- **F113 PARCIAL:** o residuo e irregular e **nao fecha por regra** -- `apendicite`, `artrite`,
  `abortaria` estao CERTAS sem acento; `arteria`, `bacteria`, `etaria` precisam; nenhum sufixo
  distingue. Exemplos vivos: **#685** e **#689**. Exige lexico ou olho humano.
- **F110** segue sem gate, por construcao (declarado na Clausula 13).
- **`db.get_db_metrics`** soma o campo inflado do F37 e **nao tem chamador vivo** -- superficie
  orfa, candidata a lapide.
- **R1:** nada adotado. `app/utils/fsrs.py` com `git diff` vazio; o adaptador nao le o JSON.
- 🔴 **CORRIGIDO EM 18/09 -- eu respondi errado ao `/ai-eng`.** Declarei que "1.9a/1.10 ja
  estavam FEITOS desde a s177". **A numeracao diverge entre os dois inventarios.** O
  `~~1.9~~`/`~~1.10~~` do nosso `§11` sao G5/varredura e `check_session_pointer`, esses sim
  fechados. Os dele, do handoff de 10-09, sao outros: **1.9(a)** = refactor `db.py ->
  tools/card_checks` por `__file__` (por spec, raio > 7 writers) e **1.10** = toda clausula
  normativa vira CHECK nomeado ou marca literal "nao-verificavel" + data de revisao. **Os dois
  NAO foram iniciados** -- o smell do 1.9(a) segue vivo em `app/utils/db.py:1046`, e o 1.10
  depende de GO do operador. Licao: **ao responder item numerado do `/ai-eng`, casar por
  CONTEUDO, nunca por numero** -- os inventarios sao independentes e o numero colide.

## Rito e higiene

Todo fix nasceu com **teste antes do codigo** (AGENTE 10.6); em tres casos o teste pegou
defeito meu antes do commit (referencia orfa a `gate_avisos` que derrubava todo insert; shape
errado de fixture; sentinela `None` caindo no leitor real). Toda operacao em lote passou pelo
rito 10.7. Nenhum hook foi burlado.
