# Hotfix: prova-pdf-caso-compartilhado

origin: session
status: verified

## Symptom
Relato do operador em 03/10/2026, resolvendo a UERJ 2021 no hub (lista `t1793`): "duas questoes com
problemas, com a alternativa de uma contendo o texto do comando da seguinte".

Medido nos docs que o `prova_pdf.py` gerou (`tmp/prova_<lista>/questoes/`):

- 2021 Q22: alternativa D = `E5` + o caso clinico inteiro que pertence as Q23-24 (308 caracteres; a
  segunda maior alternativa tem 2). A Q23 ficou so com o comando ("As caracteristicas dessa lesao...").
- 2021 Q24: alternativa D termina com a linha-cabecalho "De acordo com o caso clinico a seguir,
  responda as questoes de numeros 23 e 24:".
- Mesmo desenho, sem conteudo citado aqui (provas que ele ainda vai fazer): 2022 Q16 e Q19, 2024 Q36,
  2026 Q94 e Q98. 2023 e 2025 limpas.

Total: 7 alternativas poluidas e 10 questoes sem o caso de que dependem, em 4 das 6 provas.

## Checkpoint
hypothesis: dois defeitos somados em `parse_uerj`. (1) Toda linha que nao e numero de questao nem
alternativa e colada na ultima alternativa da questao aberta; o caso compartilhado e impresso ANTES do
numero da questao seguinte, logo cai ali. (2) `ler_pdf` devolve as linhas na ordem dos blocos do
PyMuPDF, que nao e a ordem de leitura: a linha-cabecalho do caso (caixa de texto propria) sai DEPOIS
das alternativas da ultima questao do caso, com `y` menor.
falsification_test: nas 6 provas, a distancia vertical entre a ultima linha de uma alternativa e a
linha seguinte que NAO e alternativa: se continuacao e caso se sobrepusessem, o salto nao serviria de
sinal. Medido: continuacao 13,9-16,5 pt (n=316); caso >= 24,0 pt (n=8). Sem sobreposicao.
blind_spots: caso que comeca no topo de uma pagina nova (sem salto mensuravel) nao ocorre nas 6
provas; so e pego quando traz a frase "questoes de numeros X e Y". Figura dentro do caso continua
atribuida pela regra antiga.

## Preservation
- As 6 provas seguem passando no golden (`test_golden_provas_uerj_reais`): mesma contagem, mesmas
  anuladas, mesmos blocos.
- Questao sem caso compartilhado sai byte a byte igual a antes.
- Continuacao legitima de alternativa (linha seguinte a 14-17 pt) continua na alternativa.

## Eliminated / Evidence

## Root cause
`tools/prova_pdf.py::parse_uerj`. (1) O ramo final do laco colava toda linha que nao fosse numero de
questao nem alternativa na ultima alternativa da questao aberta -- sem nocao de que o caderno imprime o
caso compartilhado ANTES do numero da questao seguinte. (2) O laco lia as linhas na ordem dos blocos do
PyMuPDF; a linha-cabecalho do caso vem numa caixa de texto propria, devolvida depois das alternativas
da ultima questao do caso.

## Fix
files_changed: tools/prova_pdf.py
- As linhas de cada pagina passam a ser lidas de cima para baixo (`sorted` por `y`, estavel).
- Linha que nao e alternativa vira CASO da proxima questao quando: fica a mais de `SALTO_CASO` (20 pt)
  da ultima linha da questao aberta que ja tem alternativas; ou vem depois de um cabecalho de bloco; ou
  traz a frase "questoes de numeros X e Y" (`RX_CASO_FAIXA`); ou ja ha caso em aberto.
- Ao abrir a questao seguinte, o caso entra como 1o paragrafo do enunciado (o caso, uma linha em branco, o comando) de
  todas as questoes da faixa X-Y; sem faixa, so da seguinte.

Dado corrigido no mesmo ato (fora do diff): 17 questoes regeneradas nas 4 provas (2021: 22-24; 2022:
16-19; 2024: 36-38; 2026: 94-100), `emed_banco.py --ingerir --apply --expect 3/4/3/7` e
`ArtifactData batch update` dos 17 docs `questoes/*` do hub (so `enunciado`/`alternativas`). Os grifos
ja feitos pelo operador (Q22, so no enunciado, que nao mudou) ficaram intactos.

## DoD
- [x] `test_caso_compartilhado_vai_para_as_questoes_dele` e `test_caso_compartilhado_nas_provas_reais` vermelhos antes, verdes depois.
- [x] `tools/test_prova_pdf.py` inteiro verde (20), golden das 6 provas incluido.
- [x] Docs novos x docs antigos: so as 17 questoes do caso mudam; as outras 390 saem identicas.
- [x] Tela conferida no navegador (Edge headless, 1280 px e 390 px, claro e escuro): Q22 com D limpa, Q23 e Q24 com o caso no enunciado.

## Regression
WHEN o caderno imprime um caso antes do numero da questao (a mais de 20 pt da ultima alternativa da
questao anterior, com ou sem a frase "questoes de numeros X e Y", e com o cabecalho do caso fora de
ordem na saida do PyMuPDF) THEN a alternativa da questao anterior sai limpa e o caso vira o 1o paragrafo
do enunciado de cada questao da faixa.
test: tools/test_prova_pdf.py::test_caso_compartilhado_vai_para_as_questoes_dele, tools/test_prova_pdf.py::test_caso_compartilhado_nas_provas_reais
oracle_type: specified
reproduction: real
verification: red-green

## Deviations
- Fora do orcamento do hotfix e por isso nao feito aqui: figura dentro do caso segue atribuida pela
  regra antiga (nenhuma ocorrencia nas 6 provas).
- Achado colateral, nao corrigido aqui: os docs gerados antes de 03/10/2026 em `tmp/prova_*` ficam
  obsoletos; os vigentes sao `tmp/prova_<lista>_s212`.
