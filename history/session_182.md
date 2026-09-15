# Session 182 -- ENAMED 2026: 75/100, o gabarito comentado das 100 questoes e os 25 erros com racional declarado

**Data:** 2026-09-15 (12:06 -> ~19:15) -- prova realizada em **2026-09-13** - **Ferramenta:** Claude Code (Fable 5.1) - **Continuidade:** `session_181.md` (12/09)
Sessao de **ESTUDO** (analise de prova real). Zero engenharia. O usuario trouxe o Caderno 02 e o gabarito preliminar do INEP em PDF na raiz do repo.

---

## 0. O que o usuario trouxe

- *"Fiz 75/80, bem proximo das nossas estimativas do banco"* -- a contagem real e **75/100** (25 erradas; confirmado). Pediu a analise da prova inteira ("nao temos gabarito comentado, voce tera que fazer a sua pesquisa") e depois mandou as 25 erradas **com racional declarado** (regra da s179) **e 13 acertos no chute**. Nao quis artifact para a analise dos erros.
- Leitura honesta do termometro: **62 questoes solidas, 13 no chute, 25 erradas.** Abaixo da serie S6-S9 (80-86) e do banco (79,1%).

## 1. Registro (ordem dura respeitada)

`registrar_sessao_bulk --sessao 182 --area Simulado --feitas 100 --acertos 75 --data 2026-09-13` **antes** de qualquer analise. Acumulado **7.226 -> 7.326**.

## 2. Gabarito comentado das 100 questoes -- artifact

Publicado: **https://claude.ai/artifact/TuXkndfMBRRjpErzM2fWEJ** (copia em `artifacts/enamed-2026-comentado.html`; filtro por area/veredito, busca, enunciado completo por card). Metodo: PDF extraido por coluna (`pdfplumber`, 2 colunas), 8 figuras recortadas (ECG Q37, pelve Q68, Lund-Browder Q12, RN Q82, TC Q89, US Q97, vulva Q64, impetigo Q81); **5 subagentes Opus em paralelo, 20 questoes cada**, com busca em fonte BR (MS/PCDT, sociedades) e nos gabaritos extraoficiais (Estrategia MED, Sanar, Medway). Fan-out autorizado pela regua F93 (feicao de Simulado 100q + pedido explicito).

- **94 CONCORDA / 6 CONTESTAVEIS:** Q5 (rastreio CCR: 40 anos ou 10 antes do caso -- nenhuma alternativa), Q6 (anafilaxia sob propranolol: repetir adrenalina x glucagon, A/C), **Q48** (PrEP mulher cis: "20 dias" e da versao 2022; **re-medido por mim no PDF do PCDT 2025: 7 dias**; resposta pela evidencia = D, como Estrategia e Sanar), **Q68** (pelve instavel + FAST negativo + hipotensao apos cinta: angioembolizacao, nao "estabilizacao cirurgica"), **Q75** (epiglote infantil e flacida, nao "rigida" -- anulacao), Q99 (comando ambiguo entre manejo do desastre e reducao de risco). Sinalizadas por cursinho mas sustentadas: Q71, Q88, Q94. Prazo de recurso INEP: 15-17/09; definitivo 04/12.
- **Achado didatico:** Q12 so fecha pelo **ATLS 11** (3 mL x kg x %SCQ em < 13 anos, nas primeiras **16 h**; SCQ 47% -> 2.820 mL). Parkland classico cai na alternativa B. Re-medido em 3 fontes BR (IDOMED, MedTask, MedEvo).
- **Perfil da prova:** Preventiva/APS **29 questoes**, Pediatria 14, Cirurgia 13, Psiquiatria 8, Obstetricia 7, Ginecologia 6, Infecto 6, Cardio 5, Endocrino 4. E o miolo MFC que a UERJ cobra em 20%.
- **Custo:** 5 spawns, **794k tokens**, ~25 min de relogio (paralelo). Duas afirmacoes load-bearing dos filhos foram re-medidas pelo principal (PrEP 2025, ATLS 11) -- ambas confirmadas.

## 3. Resultado por area (25 erros)

Cardiologia 3/5 (40%) · Endocrino 2/4 · Ginecologia 2/6 · Cirurgia 4/13 · Pediatria 4/14 · Obstetricia 2/7 · **Preventiva 5/29 (83%, igual ao banco)** · Psiquiatria 1/8. O bloco mais pesado da prova segurou; o estrago veio de **emergencia cardiologica (Q6, Q15, Q37)**, pediatria e cirurgia pediatrica. **8 dos 25 eram "faceis"** para o examinador (31, 52, 53, 61, 62, 69, 84, 88). **3 dos 25 sao contestaveis** (6, 68, 75): deferidos, o 75 vira 77-78.

## 4. Os 25 erros, lidos com a letra marcada e o racional dele

**Tipo (orcamento §11):** 8 diretas (40, 41, 56, 57, 69, 75, 77, 79, 84, 96), 4 fluxograma (6, 37, 53 + no de 19), 11 raciocinio.

**Padroes, na ordem do peso:**
- 🔴 **Discriminador identificado e NAO usado (novo sub-estado do padrao-mestre):** Q37 (*"circulei os 3 dias... sublinhei o hemodinamicamente estavel, mas nao os utilizei"*), Q19 (*"estranhei o beta descer, ate supus expectante, mas nao linkei a alternativa A"*), Q40 (identificou o seguimento, errou o instrumento). Nas palavras dele: *"consigo identificar em algumas questoes bem os discriminadores, mas nao os utilizo; outras vezes sequer consigo os identificar"*. Registrado no ledger com `--questao-id` (Q19, Q37). **Nao identificou:** Q31 (toxemia -> corpo estranho), Q59, Q61.
- 🔴 **Override do modal, declarado na Q69:** *"tipico erro que me refiro quando digo que quero 'inventar moda'... circulei trinta vezes 'alto risco'... fazendo mais sentido logico a A"*. Marcou C. 1 ocorrencia nomeada nesta prova (S9 foram 13/13; sem distribuicao de candidatos nao da para medir o resto).
- **Aborda pela etiqueta, ignora instabilidade:** Q15 (PA 86x53, FC 49 -> *"idosa bugada pelo estresse"*, marcou diazepam). **Pula hierarquia / escalona exame:** Q30 (TC na UBS para idoso com CRB-65 = 2). **Leitura do comando:** Q96 (*"nao li o comando direito"*).
- **Fatos FALSOS carregados, nao lacunas vazias:** Q53 (*"hernia inguinal na crianca pode fechar"* -- e a hidrocele), Q84 (*"nao se da triciclico para idoso"* -- Beers e cautela condicionada; o enunciado blindou com ECG normal). Cards escritos para desfazer a crenca.
- **Regua velha / diretriz nova:** Q77 (indicadores 2025), Q69 (protocolo nacional x guideline anabolica).
- **Lacunas puras (chute assumido):** 6, 41, 56, 57, 75, 79, 88, 97 -- e 8 dos 25 caem em tema **sem resumo**: anafilaxia, arritmias/FA, osteoporose, RAPS, HPB/PSA, oncologia pediatrica, coqueluche, TEA.
- 🔴 **Q52, o achado sobre cards:** *"fiz tantos cards de wilms x neuroblastoma e perdi uma questao de graca, por me ater mais na fixacao atomica do card do que conhecer a fundo as duas sindromes"*. Cirurgia Infantil tem 53 cards e caiu numa facil (Q53). **Card atomico nao transfere em cluster de dx diferencial** -- e a 2a evidencia (s142 foi a 1a); o remedio e aula comparativa, nao mais cards. Cunhado 1 card de **mecanismo** (por que o neuroblastoma cruza a linha media), nao de fato.
- **Reincidencia direta:** Q19 = mesmo elo de ectopica da s085 (*tratou antes de checar a comporta*). Ectopica tem 335q/80%/13 cards.
- **13 incertezas** (acertos no chute) no ledger: 13, 14, 23, 25, 32, 33, 58, 64, 66, 73, 81, 95, 100.

## 5. O que ficou no banco

- **25 erros** em `questoes_erros` (ids **1019-1043**), **3 como `banca-divergente` sem card** (Q6, Q68, Q75 -- F26). Lote em `core/simulados/_enamed26_erros_batch.json` (+ `_candidatos_full.json` e `.PROPOSTA_AGENTE.json` para o diff da triagem).
- **44 cards** (ids **1630-1673**) de **57 candidatos** redigidos por 1 subagente Opus (237k tokens, 27 min); **13 cortados por mim** pelo teste de regenerabilidade (cutoff do MTX que ele ja sabia, "RX e o exame inicial", artigo do CEM, VMA que ja tem card...). 1o card de cada erro = nucleo; alternativa marcada gravada na armadilha do nucleo (aviso `distrator-perdido`).
- 🛡️ **O gate funcionou 2x:** `resposta-embutida (titulo do erro, run>=6)` na Q77 abortou o lote inteiro com rollback (banco intacto, verificado 1016/1432 antes e depois). Pre-check com o predicado real (`card_checks.checar_resposta_embutida(card, {"titulo": ...})`) antes da 3a tentativa -> **COUNT-ASSERT batido: 1016 -> 1041 erros, 1432 -> 1476 cards, taxonomia 294 -> 302** (8 temas novos).
- **Ledger:** `--backfill` (+284 habilidades/+293 ocorrencias, estava atrasado) + 6 padroes com `--questao-id` (override Q69; discriminador nao usado Q19/Q37; etiqueta Q15; hierarquia Q30; comando Q96) + 13 `incerteza`.
- **15 resumos** ganharam 2-3 bullets 🔴/⚠️ em Armadilhas de Prova (ectopica, TB, PAC, IVAS/epiglotite, DMG, Cirurgia Infantil, Amenorreia, Parasitoses, Etica, Politrauma, Trauma, APS, DM cronicas, Vigilancia, Anexiais). `auto_check --changed` **PASSED** (2 WARN de linter, nao bloqueia).

## 6. Achados para o ledger

- **`[SEM-LASTRO]` falso por nome, de novo (classe F103):** `Infecto / Esquistossomose` acusado sem resumo -- o conteudo vive em `Parasitoses.md`. RAPS e real (zero lastro).
- **Gate `resposta-embutida` e cego ao proprio titulo do erro na hora da REDACAO:** o subagente escreveu titulo e frente com o mesmo run; so o writer pegou. Pre-check do lote com o predicado real deveria ser passo padrao antes de `--errors-file` (evita 2 rollbacks). Candidato a hotfix pequeno: `insert_questao.py --dry-run` (nao existe).
- **WARN `ERROS_ORFAOS` (F38) falso-positivo por data:** o bulk foi gravado com `--data 2026-09-13` (dia da prova) e os 25 erros levam `data_registro` de 15/09; o check cruza por janela d..d+1 e acusa "25 erros sem linha". Os 25 estao em `questoes_erros` (ids 1019-1043). Classe: prova feita num dia e analisada noutro -- o check nao le o `--obs`.
- Custo total de subagentes na sessao: **6 spawns, ~1,03M tokens, ~53 min de relogio** (5 em paralelo + 1 sequencial). Zero cadeia de subagentes.

## 7. Pendencias

1. **Recursos ate 17/09** (acao do usuario): Q68 e Q75 (as dele) + Q6; fundamentos no artifact. Q48/Q5/Q99 tambem cabem.
2. **FSRS: 78 atrasados + 28 de hoje = 106 vencidos** (blackout de 13-14/09 caiu hoje) + pool **685** (os 44 entraram). Regime de divida: teto 90.
3. **Rescope UERJ + frente MFC** (era segunda 14/09; nao aconteceu): a prova confirmou o peso do miolo APS/RAPS/indicadores. Resumos a criar: RAPS, Anafilaxia, FA/Arritmias, Osteoporose, HPB/PSA, Oncologia pediatrica, Coqueluche, TEA.
4. **Q52/Cirurgia Infantil:** aula comparativa de cluster (Wilms x neuroblastoma; hernia x hidrocele x criptorquidia), nao cards.
5. Re-sonda #787/#597 (herdada da s181) segue pendente.
