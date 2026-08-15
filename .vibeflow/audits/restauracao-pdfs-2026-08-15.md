# Auditoria -- restauracao dos 180 PDFs-fonte deletados por engano

> Data: 2026-08-15 | Agente: Coding Agent | Repo: `C:\Users\daanm\medhub` | **sem commit, sem push**
> Conteudo clinico **opaco**: nenhum PDF foi aberto ou lido -- so `shutil.copy2`.
> Nada foi movido nem deletado em `G:` ou `D:` -- as fontes so foram lidas.

## 1. Regra de mapeamento aplicada

| # | Regra |
|---|---|
| 1 | Destino `resumos/<Area>/[<Subarea>/]<N>. <Tema>.pdf` casa com o tema **normalizado** (casefold, sem acento, `_` equivale a espaco, pontuacao equivale a espaco), descartando o prefixo numerico `N. ` |
| 2 | Indice das fontes construido em **profundidade 2 e 3** (`<Area>/<Tema>` e `<Area>/<Tema>/<Subtema>`). Necessario: o Google Drive **trunca** o nome da pasta externa (`IAMCSSST`, `Leucemias_Cronicas`) e o nome integral do tema vive na subpasta interna |
| 3 | Precedencia entre candidatos: **G: antes de D:**, depois menor profundidade, depois ordem alfabetica do path |
| 4 | Dentro da pasta: desce em subpasta homonima, ou em subpasta unica sem PDFs (wrappers `1\` de deduplicacao do Drive) |
| 5 | Arquivo canonico = **maior `.pdf` cujo nome nao comeca com `Flashc` nem `Mapa`** (regra do dono) |

**Os 180 casaram pela regra exata (R1). Zero aproximacao, zero fuzzy-match, zero chute.**
Um segundo criterio (rotulo de parte) chegou a ser implementado como rede de seguranca e **nao foi acionado por nenhuma linha**.

## 2. COUNT-ASSERTs (todos antes de qualquer escrita)

- **#1 integridade do conjunto**: 180 mapeados + 0 nao-mapeados == **180** -- OK
- **#2 origens**: 180 existem em disco, **unicas** (0 origens servindo 2 destinos), todas com bytes > 0 -- OK
- **#3 regra do dono**: 0 origens comecando por `Flashc` ou `Mapa` -- OK
- **#4 destinos**: 0 duplicados na lista e 0 ja existentes no repo antes da copia -- OK
- **#5 pos-copia**: 180/180 destinos com bytes > 0 **e** tamanho identico a origem -- OK

Regressao entre as duas versoes do mapeador (v1 profundidade 2, v2 profundidade 2+3): **0 linhas mudaram de origem**; a v2 so acrescentou os 6 que a v1 nao achava.

## 3. Resumo

| Metrica | Valor |
|---|---|
| Deletados por engano | 180 |
| Mapeados | **180/180** |
| Restaurados e verificados | **180/180** |
| Nao-mapeados | 0 |
| Origem G: (Drive, canonica) | 163 |
| Origem D: (HD, fallback) | 17 |
| Volume copiado | 3.58 GB |
| Total de `.pdf` em `resumos/**` apos a restauracao | 395 |

Por area: Cirurgia 26 | Clínica Médica 70 | GO 40 | Pediatria 31 | Preventiva 13

### Por que 17 vieram do HD (D:)

- **Infectologia (9)**: `G:` nao tem pasta `Infectologia`. O HD e a unica fonte.
- **Preventiva (8)**: em `G:` esses temas estao consolidados numa pasta-mae sem separacao por parte (a pasta `Medidas_de_Saude_Coletiva` guarda Partes I a XI juntas, e a regra do maior PDF entregaria a parte errada). No HD existe a pasta por parte com o nome integral, entao o casamento e exato e o arquivo e inequivoco.

## 4. Tabela de mapeamento (180 linhas)

`destino <- origem escolhida <- candidatos descartados na mesma pasta`

| # | Destino (repo) | Fonte | Origem escolhida | Bytes | Descartados |
|---|---|---|---|---|---|
| 1 | `resumos/Cirurgia/1. Abdome Agudo Hemorrágico.pdf` | G | `...\Abdome_Agudo_Hemorrágico\Abdome_Agudo_Hem.pdf` | 25,628,627 | `Mapa_M.pdf` (1,832,865b, regra Flashc/Mapa); `Flashc.pdf` (2,233,362b, regra Flashc/Mapa); `Abdome.pdf` (25,326,575b, menor que o escolhido) |
| 2 | `resumos/Cirurgia/10. Cirurgia Torácica.pdf` | G | `...\Cirurgia_Torácica\Cirurg.pdf` | 32,288,804 | `Flashc.pdf` (1,265,819b, regra Flashc/Mapa); `Cirurgia_Torácica.pdf` (30,114,540b, menor que o escolhido) |
| 3 | `resumos/Cirurgia/11. Cirurgia Plástica.pdf` | G | `...\Cirurgia_Plástica\Cirurg.pdf` | 25,074,727 | `Mapa_M.pdf` (9,287,519b, regra Flashc/Mapa); `Flashc.pdf` (1,781,381b, regra Flashc/Mapa); `Cirurgia_Plástica.pdf` (24,698,040b, menor que o escolhido) |
| 4 | `resumos/Cirurgia/12. Cirurgia Infantil - Parte I.pdf` | G | `...\Cirurgia_Infantil_-_Parte_I\Cirurgia Infantil - Apostila.pdf` | 31,876,401 | `Cirurgia Infantil - Slides.pdf` (10,387,701b, menor que o escolhido); `Cirurgia Infantil - Mapa Mental.pdf` (6,829,373b, menor que o escolhido); `Cirurgia Infantil - Flashcards.pdf` (6,478,928b, menor que o escolhido) |
| 5 | `resumos/Cirurgia/13. Cirurgia Infantil - Parte II.pdf` | G | `...\Cirurgia_Infantil_-_Parte_II\Cirurg.pdf` | 24,687,161 | `Flashc.pdf` (5,506,470b, regra Flashc/Mapa); `Mapa_M.pdf` (5,551,370b, regra Flashc/Mapa); `Cirurgia_Infanti.pdf` (24,107,365b, menor que o escolhido) |
| 6 | `resumos/Cirurgia/14. Cirurgia Infantil - Parte III.pdf` | G | `...\Cirurgia_Infantil_-_Parte_III\Cirurg.pdf` | 23,707,146 | `Mapa_M.pdf` (3,956,729b, regra Flashc/Mapa); `Flashc.pdf` (12,719,454b, regra Flashc/Mapa); `Cirurgia_Infanti.pdf` (23,267,102b, menor que o escolhido); `Cirurgia_Infantil_Parte_III_-_Slide_2.pdf` (5,337,124b, menor que o escolhido); `Cirurgia_Infantil_Parte_II.pdf` (3,085,838b, menor que o escolhido) |
| 7 | `resumos/Cirurgia/15. Abdome agudo vascular.pdf` | G | `...\Abdome_Agudo_Vascular\Abdome.pdf` | 34,759,966 | `Flashc.pdf` (10,990,352b, regra Flashc/Mapa); `Mapa_M.pdf` (1,076,673b, regra Flashc/Mapa); `Abdome_Agudo_Vas.pdf` (29,743,597b, menor que o escolhido) |
| 8 | `resumos/Cirurgia/16. Abdome agudo obstrutivo.pdf` | G | `...\Abdome_Agudo_Obstrutivo\Abdome.pdf` | 46,561,422 | `Flashc.pdf` (11,735,636b, regra Flashc/Mapa); `Mapa_M.pdf` (3,451,221b, regra Flashc/Mapa); `Abdome_Agudo_Obs.pdf` (37,006,091b, menor que o escolhido); `Abdome_Agudo_Obstrutivo_-_.pdf` (5,095,668b, menor que o escolhido); `Aula_R.pdf` (4,276,987b, menor que o escolhido); `Abdome_Agudo_Obstrutivo_-_Parte_II_e_III.pdf` (4,239,555b, menor que o escolhido) |
| 9 | `resumos/Cirurgia/17. Abdome Agudo Inflamatório - Diverticulite Aguda.pdf` | G | `...\Abdome_Agudo_Inflamatório_-_Diverticulite_Aguda\Abdome_Agudo_Inf.pdf` | 22,119,101 | `Mapa_M.pdf` (1,443,612b, regra Flashc/Mapa); `Flashc.pdf` (4,000,410b, regra Flashc/Mapa); `Abdome.pdf` (20,841,106b, menor que o escolhido) |
| 10 | `resumos/Cirurgia/19. Vesícula e Vias Biliares.pdf` | G | `...\Vesícula_e_Vias_Biliares\Vesícu.pdf` | 41,456,183 | `Mapa_M.pdf` (7,104,180b, regra Flashc/Mapa); `Flashc.pdf` (6,164,658b, regra Flashc/Mapa); `Vesícula_e_Vias_.pdf` (27,774,856b, menor que o escolhido); `Aula_R.pdf` (8,292,315b, menor que o escolhido); `Vesícula_e_Vias_Biliares_-_Parte_II.pdf` (4,721,779b, menor que o escolhido); `Vesícula_e_Vias_Biliares_-.pdf` (4,372,705b, menor que o escolhido) |
| 11 | `resumos/Cirurgia/20. Trauma Vascular de Extremidades e Musculoesquelético.pdf` | G | `...\Trauma_Vascular_de_Extremidades_e_Musculoesquelético\Trauma.pdf` | 26,486,760 | `Flashc.pdf` (1,781,938b, regra Flashc/Mapa); `Trauma_Vascular_e_Musculoe.pdf` (1,734,105b, menor que o escolhido) |
| 12 | `resumos/Cirurgia/21. Trauma Populações Especiais (Pediátrico, Gestante e Idosos).pdf` | G | `...\1\Trauma_Populações_Especiais_(Pediátrico,_Gesta.pdf` | 25,451,852 | `Flashc.pdf` (1,331,667b, regra Flashc/Mapa); `Trauma_Populaçõe.pdf` (25,382,839b, menor que o escolhido); `Trauma.pdf` (22,773,126b, menor que o escolhido) |
| 13 | `resumos/Cirurgia/22. Trauma de Face e Cervical.pdf` | G | `...\Trauma_de_Face_e_Cervical\Trauma_de_Face_e.pdf` | 25,218,052 | `Mapa_M.pdf` (6,587,274b, regra Flashc/Mapa); `Flashc.pdf` (2,635,033b, regra Flashc/Mapa); `Trauma.pdf` (3,397,853b, menor que o escolhido) |
| 14 | `resumos/Cirurgia/23. Trauma Abdominal e Pélvico.pdf` | G | `...\Trauma_Abdominal_e_Pélvico\Trauma.pdf` | 41,016,541 | `Mapa_M.pdf` (13,236,680b, regra Flashc/Mapa); `Flashc.pdf` (2,694,468b, regra Flashc/Mapa); `Trauma_abdominal.pdf` (33,657,567b, menor que o escolhido); `Trauma Vascular .pdf` (29,950,188b, menor que o escolhido); `Trauma de Face e.pdf` (24,888,546b, menor que o escolhido); `Aula_R.pdf` (6,150,605b, menor que o escolhido) |
| 15 | `resumos/Cirurgia/24. Temas Gerais em Cirurgia.pdf` | G | `...\Temas_Gerais_em_Cirurgia\Temas_.pdf` | 31,955,038 | `Flashc.pdf` (9,219,622b, regra Flashc/Mapa); `Temas .pdf` (31,577,740b, menor que o escolhido) |
| 16 | `resumos/Cirurgia/25. Resposta Endócrino-Metabólica ao Trauma.pdf` | G | `...\Resposta_Endócrino-Metabólica_ao_Trauma\Respos.pdf` | 23,752,703 | `Flashc.pdf` (1,542,196b, regra Flashc/Mapa); `Resposta_Endócri.pdf` (23,086,482b, menor que o escolhido); `Resposta_Endócrino_-_Metab.pdf` (1,967,399b, menor que o escolhido) |
| 17 | `resumos/Cirurgia/26. Proctologia.pdf` | G | `...\Proctologia\Procto.pdf` | 27,805,780 | `Mapa_M.pdf` (4,435,404b, regra Flashc/Mapa); `Flashc.pdf` (7,723,156b, regra Flashc/Mapa); `Proctologia.pdf` (25,404,707b, menor que o escolhido); `Aula_R.pdf` (2,653,899b, menor que o escolhido) |
| 18 | `resumos/Cirurgia/28. Neoplasias do apêndice cecal.pdf` | G | `...\Neoplasias_do_Apêndice_Cecal\Neoplasias_do_Ap.pdf` | 22,101,473 | `Flashc.pdf` (825,420b, regra Flashc/Mapa); `Neopla.pdf` (20,055,119b, menor que o escolhido) |
| 19 | `resumos/Cirurgia/3. Urologia.pdf` | G | `...\Urologia\Urolog.pdf` | 28,957,376 | `Mapa_M.pdf` (3,464,983b, regra Flashc/Mapa); `Flashc.pdf` (3,584,506b, regra Flashc/Mapa); `Urologia.pdf` (25,158,592b, menor que o escolhido) |
| 20 | `resumos/Cirurgia/30. Complicações Pós-Operatórias.pdf` | G | `...\Complicações_Pós-Operatórias\Compli.pdf` | 26,884,008 | `Flashc.pdf` (10,900,479b, regra Flashc/Mapa); `Mapa_M.pdf` (1,057,485b, regra Flashc/Mapa); `Complicações_Pós.pdf` (9,488,918b, menor que o escolhido) |
| 21 | `resumos/Cirurgia/31. Cicatrização de Feridas.pdf` | G | `...\Cicatrização_de_Feridas\Cicatr.pdf` | 26,372,962 | `Mapa_M.pdf` (4,909,801b, regra Flashc/Mapa); `Flashc.pdf` (3,362,251b, regra Flashc/Mapa); `Cicatrização_de_.pdf` (25,680,534b, menor que o escolhido) |
| 22 | `resumos/Cirurgia/32. Abdome Agudo Perfurativo.pdf` | G | `...\Abdome_Agudo_Perfurativo\Abdome.pdf` | 26,144,451 | `Mapa_M.pdf` (2,216,954b, regra Flashc/Mapa); `Flashc.pdf` (1,699,318b, regra Flashc/Mapa); `Abdome_Agudo_Per.pdf` (25,471,438b, menor que o escolhido) |
| 23 | `resumos/Cirurgia/4. Urgências Abdominais Abdome Agudo.pdf` | G | `...\Urgências_Abdominais_-_Abdome_Agudo\Urgências_Abdomi.pdf` | 27,770,790 | `Flashc.pdf` (4,117,803b, regra Flashc/Mapa); `Urgênc.pdf` (26,640,342b, menor que o escolhido) |
| 24 | `resumos/Cirurgia/5. Trauma - Choque.pdf` | G | `...\Trauma_-_Choque\Trauma.pdf` | 22,489,264 | `Mapa_M.pdf` (3,340,348b, regra Flashc/Mapa); `Flashc.pdf` (1,860,397b, regra Flashc/Mapa) |
| 25 | `resumos/Cirurgia/7. Queimaduras e Trauma Elétrico.pdf` | G | `...\Queimaduras_e_Trauma_Elétrico\Queimaduras_e_Tr.pdf` | 23,214,250 | `Mapa_M.pdf` (5,869,458b, regra Flashc/Mapa); `Flashc.pdf` (1,964,507b, regra Flashc/Mapa); `Queima.pdf` (22,414,901b, menor que o escolhido); `Aula_R.pdf` (2,799,980b, menor que o escolhido) |
| 26 | `resumos/Cirurgia/8. Abdome Agudo Inflamatório - Apendicite Aguda.pdf` | G | `...\Abdome_Agudo_Inflamatório_-_Apendicite_Aguda\Abdome_Agudo_Inf.pdf` | 24,316,355 | `Mapa_M.pdf` (2,645,881b, regra Flashc/Mapa); `Flashcards_-_Apendicite_Ag.pdf` (5,054,468b, regra Flashc/Mapa); `Flashc.pdf` (5,054,468b, regra Flashc/Mapa); `Abdome.pdf` (23,248,874b, menor que o escolhido); `Aula_R.pdf` (2,662,295b, menor que o escolhido) |
| 27 | `resumos/Clínica Médica/Cardiologia/10. IAMCSSST (Infarto Agudo do Miocárdio com Supradesnivelamento de Segmento ST).pdf` | G | `...\IAMCSSST_(Infarto_Agudo_do_Miocárdio_com_Supradesnivelamento_de_Segmento_ST)\IAMCSS.pdf` | 25,736,510 | `Mapa_M.pdf` (12,489,144b, regra Flashc/Mapa); `IAMCSSST_(Infarto_Agudo_do_Miocárdio_com_Supra.pdf` (25,669,716b, menor que o escolhido) |
| 28 | `resumos/Clínica Médica/Cardiologia/11. Semiologia Cardíaca.pdf` | G | `...\Semiologia_Cardíaca\Semiologia_Cardíaca_.pdf` | 26,467,041 | `Flashc.pdf` (474,171b, regra Flashc/Mapa); `Semiol.pdf` (22,258,212b, menor que o escolhido); `Semiologia_Cardíaca.pdf` (3,484,538b, menor que o escolhido) |
| 29 | `resumos/Clínica Médica/Cardiologia/12. Síndromes Aórticas Agudas.pdf` | G | `...\Síndromes_Aórticas_Agudas\Síndromes_Aórtic.pdf` | 26,663,422 | `Mapa_M.pdf` (5,462,025b, regra Flashc/Mapa); `Flashc.pdf` (472,263b, regra Flashc/Mapa); `Síndro.pdf` (19,963,803b, menor que o escolhido) |
| 30 | `resumos/Clínica Médica/Cardiologia/13. Dislipidemia e Estratificação de Risco Cardiovascular.pdf` | G | `...\Dislipidemia_e_Estratificação_de_Risco_Cardiovascular\Dislipidemia_e_E.pdf` | 24,198,437 | `Mapa_M.pdf` (1,684,328b, regra Flashc/Mapa); `Flashc.pdf` (2,057,602b, regra Flashc/Mapa); `Dislip.pdf` (20,208,135b, menor que o escolhido) |
| 31 | `resumos/Clínica Médica/Cardiologia/15. Pericardiopatias.pdf` | G | `...\Pericardiopatias\Pericardiopatias.pdf` | 30,184,233 | `Mapa_M.pdf` (3,917,902b, regra Flashc/Mapa); `Flashc.pdf` (6,830,589b, regra Flashc/Mapa); `Perica.pdf` (26,407,410b, menor que o escolhido) |
| 32 | `resumos/Clínica Médica/Cardiologia/16. Parada Cardiorrespiratória (PCR).pdf` | G | `...\Parada_Cardiorrespiratória_(PCR)\Parada_Cardiorrespiratória_PCR.pdf` | 28,110,464 | `Mapa_M.pdf` (4,533,086b, regra Flashc/Mapa); `Flashc.pdf` (4,788,809b, regra Flashc/Mapa); `Parada_Cardiorre.pdf` (27,162,385b, menor que o escolhido); `Parada_Cardiorrespiratória.pdf` (26,199,504b, menor que o escolhido); `Parada.pdf` (2,479,637b, menor que o escolhido); `Parada_Cardiorrespiratória_(PCR).pdf` (2,247,320b, menor que o escolhido) |
| 33 | `resumos/Clínica Médica/Cardiologia/17. Fibrilação e Flutter Atrial.pdf` | G | `...\Fibrilação_e_Flutter_Atrial\Fibrilação_e_Flu.pdf` | 30,857,850 | `Mapa_M.pdf` (2,820,624b, regra Flashc/Mapa); `Flashc.pdf` (482,924b, regra Flashc/Mapa); `Fibril.pdf` (30,325,774b, menor que o escolhido) |
| 34 | `resumos/Clínica Médica/Cardiologia/18. Hipertensão Arterial Sistêmica (Parte 3) - Secundária e Crise Hipertensiva.pdf` | G | `...\1\Hipertensão_Arte.pdf` | 22,848,411 | `Mapa_Mental_-_Hipertensão_Arterial_Sistêmica_(.pdf` (5,462,479b, regra Flashc/Mapa); `Mapa_M.pdf` (5,495,799b, regra Flashc/Mapa); `Flashc.pdf` (506,063b, regra Flashc/Mapa); `Hipertensão_Arterial_Sistêmica_(Parte_3)__Secu.pdf` (22,669,340b, menor que o escolhido); `Hipert.pdf` (16,487,847b, menor que o escolhido); `Hipertensão_Arterial_Sistêmica_(Parte_1.pdf` (2,375,369b, menor que o escolhido); `Hipertensão_Arterial_Sistêmica_(Parte_3)_-_Sec.pdf` (2,332,504b, menor que o escolhido) |
| 35 | `resumos/Clínica Médica/Cardiologia/19. Síncope.pdf` | G | `...\Síncope\Sincop.pdf` | 23,757,362 | `Flashc.pdf` (521,318b, regra Flashc/Mapa); `Síncop.pdf` (17,875,655b, menor que o escolhido); `Síncope.pdf` (4,903,476b, menor que o escolhido) |
| 36 | `resumos/Clínica Médica/Cardiologia/21. Bradiarritmias.pdf` | G | `...\Bradiarritmias\Bradia.pdf` | 18,834,746 | `Mapa_M.pdf` (4,161,536b, regra Flashc/Mapa); `Flashc.pdf` (3,584,031b, regra Flashc/Mapa); `Bradiarritmias.pdf` (1,334,468b, menor que o escolhido) |
| 37 | `resumos/Clínica Médica/Cardiologia/3. Insuficiência Cardíaca (Parte 2)_ Tratamento.pdf` | G | `...\Insuficiência_Cardíaca_(Parte_2)__Tratamento\Insufi.pdf` | 22,737,855 | `Mapa_M.pdf` (6,110,536b, regra Flashc/Mapa); `Flashc.pdf` (481,380b, regra Flashc/Mapa); `Aula_R.pdf` (6,856,596b, menor que o escolhido) |
| 38 | `resumos/Clínica Médica/Dermatologia/1. Histologia e Fisiologia da Pele e Lesões Elementares.pdf` | G | `...\Histologia_e_Fisiologia_da_Pele_e_Lesões_Elementares\Histologia_e_Fisiologia_da_Pele_e_Lesões_Eleme.pdf` | 23,557,800 | `Flashc.pdf` (953,104b, regra Flashc/Mapa); `Histol.pdf` (23,127,168b, menor que o escolhido); `Histologia_e_fisiologia_da_pele_e_lesoes_eleme.pdf` (19,526,339b, menor que o escolhido); `Lesões.pdf` (4,731,777b, menor que o escolhido); `Histologia_e_Fis.pdf` (1,898,083b, menor que o escolhido) |
| 39 | `resumos/Clínica Médica/Dermatologia/10. Piodermites.pdf` | G | `...\Piodermites\Pioder.pdf` | 20,399,424 | `Flashc.pdf` (2,407,332b, regra Flashc/Mapa); `Piodermites.pdf` (3,019,088b, menor que o escolhido) |
| 40 | `resumos/Clínica Médica/Dermatologia/11. Síndromes Verrucosas.pdf` | G | `...\Síndromes_Verrucosas\Síndro.pdf` | 18,500,465 | `Flashc.pdf` (1,223,412b, regra Flashc/Mapa); `Síndromes_Verrucosas.pdf` (2,977,240b, menor que o escolhido) |
| 41 | `resumos/Clínica Médica/Dermatologia/2. Oncologia Cutânea (Câncer de Pele).pdf` | G | `...\Oncologia_Cutânea_(Câncer_de_Pele)\Oncolo.pdf` | 22,970,666 | `Flashc.pdf` (1,068,443b, regra Flashc/Mapa); `Mapa_M.pdf` (7,323,621b, regra Flashc/Mapa); `Oncologia_Cutâne.pdf` (19,126,462b, menor que o escolhido); `Aula_r.pdf` (4,026,390b, menor que o escolhido) |
| 42 | `resumos/Clínica Médica/Dermatologia/3. Hanseníase.pdf` | G | `...\Hanseníase\Hansen.pdf` | 19,498,427 | `Mapa_M.pdf` (4,699,448b, regra Flashc/Mapa); `Flashc.pdf` (2,244,717b, regra Flashc/Mapa) |
| 43 | `resumos/Clínica Médica/Dermatologia/4. Dermatoses Infecciosas.pdf` | G | `...\Dermatoses_Infecciosas\Dermat.pdf` | 30,742,979 | `Mapa_M.pdf` (8,287,557b, regra Flashc/Mapa); `Flashc.pdf` (960,313b, regra Flashc/Mapa); `Dermatoses_Infec.pdf` (18,788,164b, menor que o escolhido); `Aula_R.pdf` (5,274,724b, menor que o escolhido) |
| 44 | `resumos/Clínica Médica/Dermatologia/5. Dermatoses Eczematosas.pdf` | G | `...\Dermatoses_Eczematosas\Dermat.pdf` | 19,152,995 | `Flashc.pdf` (3,698,515b, regra Flashc/Mapa); `Dermatoses_Eczem.pdf` (17,298,755b, menor que o escolhido) |
| 45 | `resumos/Clínica Médica/Dermatologia/6. Farmacodermias.pdf` | G | `...\Farmacodermias\Farmac.pdf` | 17,707,843 | `Flashc.pdf` (3,577,839b, regra Flashc/Mapa); `Farmacodermias.pdf` (16,655,784b, menor que o escolhido) |
| 46 | `resumos/Clínica Médica/Dermatologia/7. Dermatoses Papuloescamosas.pdf` | G | `...\Dermatoses_Papuloescamosas\Dermat.pdf` | 18,918,586 | `Flashc.pdf` (959,303b, regra Flashc/Mapa); `Dermatoses_Papul.pdf` (17,580,705b, menor que o escolhido) |
| 47 | `resumos/Clínica Médica/Dermatologia/8. Dermatoses Vesicobolhosas.pdf` | G | `...\Dermatoses_Vesicobolhosas\Dermat.pdf` | 20,409,288 | `Flashc.pdf` (954,624b, regra Flashc/Mapa); `Dermatoses_Vesic.pdf` (5,004,456b, menor que o escolhido) |
| 48 | `resumos/Clínica Médica/Endocrinologia/10. Metabolismo Ósseo e Mineral - Hipercalcemia.pdf` | G | `...\Metabolismo_Ósseo_e_Mineral_-_Hipercalcemia\Metabo.pdf` | 12,957,902 | `Mapa_M.pdf` (3,247,572b, regra Flashc/Mapa); `Flashc.pdf` (1,538,848b, regra Flashc/Mapa); `Metabolismo_Ósse.pdf` (5,407,560b, menor que o escolhido) |
| 49 | `resumos/Clínica Médica/Endocrinologia/11. Metabolismo Ósseo e Mineral - Hipocalcemia.pdf` | G | `...\Metabolismo_Ósseo_e_Mineral_-_Hipocalcemia\Metabo.pdf` | 13,800,887 | `Mapa_M.pdf` (1,964,968b, regra Flashc/Mapa); `Flashc.pdf` (3,019,498b, regra Flashc/Mapa); `Metabolismo_Ósse.pdf` (12,824,615b, menor que o escolhido) |
| 50 | `resumos/Clínica Médica/Endocrinologia/12. Metabolismo Ósseo e Mineral - Magnésio e Fosfato.pdf` | G | `...\1\Metabolismo_Ósse.pdf` | 12,948,980 | `Flashc.pdf` (1,504,837b, regra Flashc/Mapa); `Metabo.pdf` (12,818,581b, menor que o escolhido) |
| 51 | `resumos/Clínica Médica/Endocrinologia/13. Metabolismo Ósseo e Mineral-Vitamina D e Osteomalácia.pdf` | G | `...\Metabolismo_Ósseo_e_Mineral_-_Vitamina_D_e_Osteomalácia\Metabolismo_Ósse.pdf` | 12,955,570 | `Flashc.pdf` (1,761,226b, regra Flashc/Mapa); `Metabo.pdf` (12,482,337b, menor que o escolhido) |
| 52 | `resumos/Clínica Médica/Endocrinologia/15. Metabolismo Ósseo e Mineral - Osteoporose e Doença Óssea de Paget.pdf` | G | `...\1\Metabo.pdf` | 19,384,282 | `Mapa_M.pdf` (3,356,961b, regra Flashc/Mapa); `Flashc.pdf` (2,874,321b, regra Flashc/Mapa); `Metabolismo_Ósse.pdf` (5,358,369b, menor que o escolhido) |
| 53 | `resumos/Clínica Médica/Endocrinologia/16. Adrenal-Morfofisiologia Adrenal.pdf` | G | `...\Adrenal_-_Morfofisiologia_Adrenal\Adrenal_-_Morfof.pdf` | 14,724,503 | `Flashc.pdf` (2,630,547b, regra Flashc/Mapa); `Adrena.pdf` (14,004,888b, menor que o escolhido) |
| 54 | `resumos/Clínica Médica/Endocrinologia/17. Adrenal - Hipocortisolismo (Insuficiência Adrenal).pdf` | G | `...\Adrenal-_Hipocortisolismo_(Insuficiência_Adrenal)\Adrenal-_Hipocor.pdf` | 14,998,861 | `Flashc.pdf` (1,144,337b, regra Flashc/Mapa); `Mapa_M.pdf` (786,960b, regra Flashc/Mapa); `Adrena.pdf` (14,967,285b, menor que o escolhido); `Adrenal_-_Hipoco.pdf` (2,940,493b, menor que o escolhido) |
| 55 | `resumos/Clínica Médica/Endocrinologia/18. Adrenal- Hipercortisolismo (Síndrome de Cushing).pdf` | G | `...\Adrenal-_Hipercortisolismo_(Síndrome_de_Cushing)\Adrenal-_Hiperco.pdf` | 16,340,760 | `Mapa_M.pdf` (3,192,174b, regra Flashc/Mapa); `Flashc.pdf` (1,183,630b, regra Flashc/Mapa); `Adrena.pdf` (16,187,134b, menor que o escolhido); `Adrenal_-_Hiperc.pdf` (5,856,489b, menor que o escolhido) |
| 56 | `resumos/Clínica Médica/Endocrinologia/19. Adrenal - Feocromocitoma, Hiperaldosteronismo e Incidentaloma Adrenal.pdf` | G | `...\1\Adrena.pdf` | 16,594,588 | `Mapa_M.pdf` (2,979,468b, regra Flashc/Mapa); `Mapa_Mental_-_Adrenal_-_Feocromocitoma,_Hipera.pdf` (2,907,423b, regra Flashc/Mapa); `Flashc.pdf` (1,305,258b, regra Flashc/Mapa); `Adrenal_-_Feocro.pdf` (3,593,943b, menor que o escolhido) |
| 57 | `resumos/Clínica Médica/Endocrinologia/20. Hipófise - Fisiologia da Hipófise e Hipopituitarismo.pdf` | G | `...\Hipófise_-_Fisiologia_da_Hipófise_e_Hipopituitarismo\Hipófi.pdf` | 17,191,908 | `Flashc.pdf` (4,216,350b, regra Flashc/Mapa); `Hipófise_-_Fisio.pdf` (15,844,693b, menor que o escolhido) |
| 58 | `resumos/Clínica Médica/Endocrinologia/21. Hipófise-Acromegalia e Incidentaloma Hipofisário.pdf` | G | `...\Hipófise_-_Acromegalia_e_Incidentaloma_Hipofisário\Hipófise_-_Acrom.pdf` | 16,695,803 | `Flashc.pdf` (1,868,756b, regra Flashc/Mapa); `Hipófi.pdf` (16,326,245b, menor que o escolhido) |
| 59 | `resumos/Clínica Médica/Endocrinologia/22. Hipófise - Hiperprolactinemia.pdf` | G | `...\Hipófise_-_Hiperprolactinemia\Hipófi.pdf` | 16,282,358 | `Mapa_M.pdf` (2,586,942b, regra Flashc/Mapa); `Flashc.pdf` (2,856,254b, regra Flashc/Mapa); `Hipófise_-_Hiper.pdf` (15,815,339b, menor que o escolhido) |
| 60 | `resumos/Clínica Médica/Endocrinologia/23. Neoplasias Endócrinas Múltiplas.pdf` | G | `...\Neoplasias_Endócrinas_Múltiplas\Neopla.pdf` | 14,881,966 | `Flashc.pdf` (1,935,127b, regra Flashc/Mapa); `Neoplasias_Endóc.pdf` (13,773,769b, menor que o escolhido) |
| 61 | `resumos/Clínica Médica/Endocrinologia/24. Hipoglicemia no Paciente não Diabético.pdf` | G | `...\Hipoglicemia_no_Paciente_não_Diabético\Hipogl.pdf` | 14,175,675 | `Flashc.pdf` (2,928,908b, regra Flashc/Mapa); `Hipoglicemia_no_.pdf` (2,113,758b, menor que o escolhido) |
| 62 | `resumos/Clínica Médica/Endocrinologia/25. Incongruência de Gênero.pdf` | G | `...\Incongruência_de_Gênero\Incong.pdf` | 14,043,733 | `Flashc.pdf` (737,656b, regra Flashc/Mapa); `Incongruência_de.pdf` (1,376,424b, menor que o escolhido) |
| 63 | `resumos/Clínica Médica/Endocrinologia/26. Tireoide - Hipotireoidismo.pdf` | G | `...\Tireoide_-_Hipotireoidismo\Tireoi.pdf` | 13,407,882 | `Flashc.pdf` (1,490,871b, regra Flashc/Mapa); `Mapa_M.pdf` (2,862,133b, regra Flashc/Mapa); `Tireoide_-_Hipot.pdf` (1,047,803b, menor que o escolhido) |
| 64 | `resumos/Clínica Médica/Endocrinologia/3. Diabetes Mellitus_ Insulinoterapia e Cirurgia Metabólica.pdf` | G | `...\1\Diabet.pdf` | 16,505,072 | `Mapa_M.pdf` (4,018,864b, regra Flashc/Mapa); `Flashc.pdf` (2,258,356b, regra Flashc/Mapa); `Diabetes_Mellitu.pdf` (3,719,804b, menor que o escolhido) |
| 65 | `resumos/Clínica Médica/Endocrinologia/7. Tireoide - Tireotoxicose_ Diagnóstico, Etiologia, Tratamento, Tireotoxicose na Gestação e Crise Tireotóxica.pdf` | G | `...\Tireoide_-_Tireotoxicose__Diagnóstico,_Etiologia,_Tratamento,_Tireotoxicose_na_Gestação_e_Crise_Tireotóxica\Tireoi.pdf` | 21,454,882 | `Mapa_M.pdf` (4,672,155b, regra Flashc/Mapa); `Flashc.pdf` (1,509,117b, regra Flashc/Mapa) |
| 66 | `resumos/Clínica Médica/Endocrinologia/8. Obesidade - Obesidade e Síndrome Metabólica.pdf` | G | `...\Obesidade_-_Obesidade_e_Síndrome_Metabólica\Obesid.pdf` | 16,983,040 | `Flashc.pdf` (6,321,045b, regra Flashc/Mapa); `Obesidade_e_Sínd.pdf` (13,976,822b, menor que o escolhido); `Obesidade_-_Obes.pdf` (3,489,909b, menor que o escolhido); `Obesidade_e_Sind.pdf` (2,761,094b, menor que o escolhido) |
| 67 | `resumos/Clínica Médica/Gastroenterologia/1. Hemorragia Digestiva Alta Não Varicosa.pdf` | G | `...\Hemorragia_Digestiva_Alta_Não_Varicosa\Hemorragia_Diges.pdf` | 24,289,636 | `Flashc.pdf` (4,940,676b, regra Flashc/Mapa); `Hemorr.pdf` (16,110,606b, menor que o escolhido); `Hemorragia_Digestiva_Alta_Não_Varicosa_-_Parte.pdf` (4,898,642b, menor que o escolhido); `Hemorragia_Digestiva_Alta_Não_Varicosa_-_Parte_II.pdf` (4,517,033b, menor que o escolhido); `Aula_R.pdf` (3,527,673b, menor que o escolhido) |
| 68 | `resumos/Clínica Médica/Gastroenterologia/3. Hemorragia Digestiva Baixa.pdf` | G | `...\Hemorragia_Digestiva_Baixa\Hemorragia_Diges.pdf` | 24,589,898 | `Mapa_M.pdf` (30,750,476b, regra Flashc/Mapa); `Flashc.pdf` (3,695,372b, regra Flashc/Mapa); `Hemorr.pdf` (18,525,907b, menor que o escolhido); `Aula_R.pdf` (2,904,900b, menor que o escolhido) |
| 69 | `resumos/Clínica Médica/Gastroenterologia/5. Pancreatite Aguda e Crônica (Pancreatites).pdf` | G | `...\Pancreatite_Aguda_e_Crônica_(Pancreatites)\Pancreatite_Agud.pdf` | 22,257,913 | `Flashc.pdf` (4,025,427b, regra Flashc/Mapa); `Mapa_M.pdf` (1,307,822b, regra Flashc/Mapa); `Pancre.pdf` (18,234,349b, menor que o escolhido); `Aula_R.pdf` (8,881,693b, menor que o escolhido) |
| 70 | `resumos/Clínica Médica/Gastroenterologia/6. Hemorragia Digestiva Alta Varicosa.pdf` | G | `...\Hemorragia_Digestiva_Alta_Varicosa\Hemorragia_Diges.pdf` | 24,585,431 | `Mapa_M.pdf` (30,750,476b, regra Flashc/Mapa); `Flashc.pdf` (1,771,030b, regra Flashc/Mapa); `Hemorr.pdf` (20,080,685b, menor que o escolhido); `Aula_R.pdf` (3,454,758b, menor que o escolhido) |
| 71 | `resumos/Clínica Médica/Hematologia/1. Introdução ao Estudo das Anemias.pdf` | G | `...\Introdução_ao_Estudo_das_Anemias\Introd.pdf` | 10,976,027 | `Flashc.pdf` (6,369,232b, regra Flashc/Mapa); `Introdução_ao_Es.pdf` (1,435,349b, menor que o escolhido) |
| 72 | `resumos/Clínica Médica/Hematologia/3. Anemias Macrocíticas.pdf` | G | `...\Anemias_Macrocíticas\Anemia.pdf` | 16,653,121 | `Flashc.pdf` (2,510,951b, regra Flashc/Mapa); `Anemias_Macrocíticas.pdf` (1,862,820b, menor que o escolhido) |
| 73 | `resumos/Clínica Médica/Hematologia/5. Anemia Associada a Condições Não Hematológicas.pdf` | G | `...\Anemia_Associada_a_Condições_Não_Hematológicas\Anemia.pdf` | 14,102,380 | `Flashc.pdf` (5,637,774b, regra Flashc/Mapa); `Anemia_Associada.pdf` (2,356,189b, menor que o escolhido) |
| 74 | `resumos/Clínica Médica/Hematologia/6. Hemostasia I_ Conceitos Básicos e Anticoagulantes.pdf` | G | `...\Hemostasia I - Conceitos Básicos e Anticoagulantes\Hemostasia_I__Co.pdf` | 27,184,744 | `Mapa_M.pdf` (8,535,116b, regra Flashc/Mapa); `Flashc.pdf` (4,348,443b, regra Flashc/Mapa); `Hemost.pdf` (20,549,596b, menor que o escolhido) |
| 75 | `resumos/Clínica Médica/Hematologia/8. Mieloma Múltiplo (Gamopatias Monoclonais).pdf` | G | `...\Mieloma_Múltiplo_(Gamopatias_Monoclonais)\Mielom.pdf` | 16,698,466 | `Flashc.pdf` (2,260,157b, regra Flashc/Mapa); `Mapa_M.pdf` (3,226,751b, regra Flashc/Mapa); `Gamopa.pdf` (3,184,963b, menor que o escolhido) |
| 76 | `resumos/Clínica Médica/Hematologia/9. Leucemias Crônicas, Linfomas, Mielodisplasias e Mieloproliferações.pdf` | G | `...\Leucemias_Crônicas,_Linfomas,_Mielodisplasias_e_Mieloproliferações\Leucemias_Crônic.pdf` | 27,366,836 | `Mapa_Mental_-_Leucemias_Crônicas,_Linfomas,__M.pdf` (11,888,243b, regra Flashc/Mapa); `Mapa_M.pdf` (12,038,422b, regra Flashc/Mapa); `Flashc.pdf` (4,327,213b, regra Flashc/Mapa); `Leucemias_Crônicas,_Linfomas,_Mielodisplasias_e_Mieloproliferações_.pdf` (27,273,499b, menor que o escolhido); `Leucem.pdf` (22,143,923b, menor que o escolhido); `Leucemias_Crônicas,_Linfomas,_Mielodisplasias_e_Mie_1.pdf` (10,506,982b, menor que o escolhido); `Leucemias_Crônicas,_Linfomas,_Mielodisplasias_.pdf` (10,384,730b, menor que o escolhido) |
| 77 | `resumos/Clínica Médica/Infectologia/10. Arboviroses (Dengue, Chikungunya e Zika).pdf` | D | `...\Arboviroses_(Dengue,_Chikungunya_e_Zika)\Arboviroses_(Den.pdf` | 23,901,433 | `Flashc.pdf` (4,924,407b, regra Flashc/Mapa); `Mapa_M.pdf` (7,894,089b, regra Flashc/Mapa); `Arbovi.pdf` (13,363,877b, menor que o escolhido) |
| 78 | `resumos/Clínica Médica/Infectologia/11. Micoses Invasivas.pdf` | D | `...\Micoses_Invasivas\Micoses_Invasivas.pdf` | 30,576,652 | `Flashc.pdf` (10,424,346b, regra Flashc/Mapa); `Micose.pdf` (21,789,696b, menor que o escolhido) |
| 79 | `resumos/Clínica Médica/Infectologia/13. Parasitoses.pdf` | D | `...\Parasitoses\Parasitoses.pdf` | 21,748,947 | `Flashc.pdf` (8,985,071b, regra Flashc/Mapa); `Mapa_M.pdf` (2,513,321b, regra Flashc/Mapa); `parasi.pdf` (12,022,257b, menor que o escolhido) |
| 80 | `resumos/Clínica Médica/Infectologia/14. Neutropenia Febril e Febre de Origem Indeterminada.pdf` | D | `...\Neutropenia_Febril_e_Febre_de_Origem_Indeterminada\Neutro.pdf` | 12,847,427 | `Flashc.pdf` (1,037,487b, regra Flashc/Mapa); `Mapa_M.pdf` (4,459,474b, regra Flashc/Mapa); `Neutropenia_Febr.pdf` (11,956,619b, menor que o escolhido) |
| 81 | `resumos/Clínica Médica/Infectologia/15. Endocardite Bacteriana - Endocardite Infecciosa.pdf` | D | `...\Endocardite_Bacteriana_-_Endocardite_Infecciosa\Endocardite_Bact.pdf` | 13,833,888 | `Flashc.pdf` (1,599,065b, regra Flashc/Mapa); `Mapa_M.pdf` (9,581,947b, regra Flashc/Mapa); `Endoca.pdf` (12,809,366b, menor que o escolhido); `Endocardite_-_Co.pdf` (6,923,826b, menor que o escolhido) |
| 82 | `resumos/Clínica Médica/Infectologia/17. Hepatoesplenomegalias Infecciosas.pdf` | D | `...\Hepatoesplenomegalias_Infecciosas\Hepatoesplenomegalias_Crônicas_.pdf` | 26,208,301 | `Flashc.pdf` (4,640,998b, regra Flashc/Mapa); `Mapa_M.pdf` (7,480,929b, regra Flashc/Mapa); `Hepato.pdf` (26,145,840b, menor que o escolhido); `Hepatoesplenomegalias_Crôn.pdf` (10,170,950b, menor que o escolhido) |
| 83 | `resumos/Clínica Médica/Infectologia/18. Síndrome Febril Íctero-Hemorrágica.pdf` | D | `...\Síndrome_Febril_Íctero-Hemorrágica\Síndro.pdf` | 17,743,550 | `Flashc.pdf` (2,613,053b, regra Flashc/Mapa); `Mapa_M.pdf` (2,573,938b, regra Flashc/Mapa); `Síndrome_Febril_.pdf` (11,634,717b, menor que o escolhido) |
| 84 | `resumos/Clínica Médica/Infectologia/2. Leptospirose.pdf` | D | `...\Leptospirose\Leptospirose.pdf` | 22,824,705 | `Flashc.pdf` (1,795,477b, regra Flashc/Mapa); `Mapa_M.pdf` (2,162,875b, regra Flashc/Mapa); `Leptos.pdf` (9,713,994b, menor que o escolhido) |
| 85 | `resumos/Clínica Médica/Infectologia/4. Animais Peçonhentos.pdf` | D | `...\Animais_Peçonhentos\Animai.pdf` | 13,744,176 | `Flashc.pdf` (2,870,519b, regra Flashc/Mapa); `Mapa_M.pdf` (6,172,194b, regra Flashc/Mapa); `Animais_Peçonhentos.pdf` (2,099,519b, menor que o escolhido) |
| 86 | `resumos/Clínica Médica/Nefrologia/1. Lesão Renal Aguda (LRA).pdf` | G | `...\Lesão_Renal_Aguda_(LRA)\Lesão_Renal_Aguda.pdf` | 27,942,764 | `Mapa_M.pdf` (1,944,957b, regra Flashc/Mapa); `Flashc.pdf` (2,167,438b, regra Flashc/Mapa); `Lesão .pdf` (19,586,642b, menor que o escolhido); `Aula_R.pdf` (2,213,619b, menor que o escolhido) |
| 87 | `resumos/Clínica Médica/Nefrologia/2. Doença Renal Crônica (DRC) - Parte I.pdf` | G | `...\Doença_Renal_Crônica_(DRC)_-_Parte_I\Doença_Crônica_R.pdf` | 25,376,195 | `Mapa_M.pdf` (4,893,929b, regra Flashc/Mapa); `Flashc.pdf` (8,205,621b, regra Flashc/Mapa); `Doença.pdf` (17,764,187b, menor que o escolhido); `Doença_Renal_Crô.pdf` (3,163,171b, menor que o escolhido) |
| 88 | `resumos/Clínica Médica/Nefrologia/3. Doença Renal Crônica (DRC) - Parte II.pdf` | G | `...\Doença_Renal_Crônica_(DRC)_-_Parte_II\Doença_Renal_Crô.pdf` | 26,206,976 | `Mapa_M.pdf` (4,893,929b, regra Flashc/Mapa); `Flashc.pdf` (8,205,621b, regra Flashc/Mapa); `Doença.pdf` (16,661,853b, menor que o escolhido) |
| 89 | `resumos/Clínica Médica/Nefrologia/4. Doenças Glomerulares.pdf` | G | `...\Doenças_Glomerulares\Doenças_Glomerulares.pdf` | 28,634,974 | `Mapa_M.pdf` (8,186,796b, regra Flashc/Mapa); `Flashc.pdf` (4,436,373b, regra Flashc/Mapa); `Doença.pdf` (23,052,001b, menor que o escolhido) |
| 90 | `resumos/Clínica Médica/Nefrologia/6. Túbulo Interstício Renal.pdf` | G | `...\Túbulo-Interstício_Renal\Túbulo-Interstício_Renal.pdf` | 27,004,483 | `Flashc.pdf` (1,850,101b, regra Flashc/Mapa); `Túbulo.pdf` (17,816,513b, menor que o escolhido); `Fisiol.pdf` (4,726,132b, menor que o escolhido); `Tubulo.pdf` (2,193,645b, menor que o escolhido); `Nefrit.pdf` (1,878,076b, menor que o escolhido) |
| 91 | `resumos/Clínica Médica/Nefrologia/8. Análise da Gasometria Arterial.pdf` | G | `...\Análise_da_Gasometria_Arterial\Análise_da_Gasom.pdf` | 24,445,926 | `Mapa_M.pdf` (1,567,217b, regra Flashc/Mapa); `Flashc.pdf` (739,393b, regra Flashc/Mapa); `Anális.pdf` (15,457,794b, menor que o escolhido) |
| 92 | `resumos/Clínica Médica/Nefrologia/9. Distúrbios do Sódio - Disnatremias.pdf` | G | `...\Distúrbios_do_Sódio_-_Disnatremias\Distúr.pdf` | 21,387,945 | `Mapa_M.pdf` (5,520,903b, regra Flashc/Mapa); `Flashc.pdf` (1,709,397b, regra Flashc/Mapa); `Distúrbios_do_Só.pdf` (10,717,802b, menor que o escolhido); `Distúrbios_do_Sódio_-_Disnatremias_-_Aula_Resu.pdf` (4,784,421b, menor que o escolhido) |
| 93 | `resumos/Clínica Médica/Pneumologia/1. Derrame Pleural.pdf` | G | `...\Derrame_Pleural\Derrame_Pleural.pdf` | 31,384,448 | `Mapa_M.pdf` (6,511,953b, regra Flashc/Mapa); `Flashc.pdf` (3,347,554b, regra Flashc/Mapa); `Derram.pdf` (25,624,212b, menor que o escolhido); `Derrame_Pleural_.pdf` (3,284,918b, menor que o escolhido) |
| 94 | `resumos/Clínica Médica/Pneumologia/3. Tromboembolismo Pulmonar (TEP).pdf` | G | `...\Tromboembolismo_Pulmonar_(TEP)\Trombo.pdf` | 32,124,339 | `Flashc.pdf` (6,537,464b, regra Flashc/Mapa); `Mapa_M.pdf` (9,009,483b, regra Flashc/Mapa); `Tromboembolismo_.pdf` (30,424,172b, menor que o escolhido); `Tromboembolismo_Pulmonar_(.pdf` (3,181,334b, menor que o escolhido) |
| 95 | `resumos/Clínica Médica/Pneumologia/4. Introdução à Pneumologia.pdf` | G | `...\Introdução_a_Pneumologia\Introdução_a_Pne.pdf` | 32,819,891 | `Flashc.pdf` (2,723,369b, regra Flashc/Mapa); `Introd.pdf` (32,819,891b, menor que o escolhido) |
| 96 | `resumos/Clínica Médica/Pneumologia/8. Neoplasias Pulmonares.pdf` | G | `...\Neoplasias_Pulmonares\Neopla.pdf` | 33,292,942 | `Mapa_M.pdf` (4,198,837b, regra Flashc/Mapa); `Flashc.pdf` (7,979,283b, regra Flashc/Mapa); `Neoplasias_Pulmo.pdf` (14,185,032b, menor que o escolhido) |
| 97 | `resumos/GO/1. Ciclo Menstrual.pdf` | G | `...\Ciclo_Menstrual\Ciclo_.pdf` | 25,033,306 | `Mapa_M.pdf` (5,535,569b, regra Flashc/Mapa); `Flashc.pdf` (398,470b, regra Flashc/Mapa); `Ciclo .pdf` (18,079,357b, menor que o escolhido); `Aula_R.pdf` (2,946,270b, menor que o escolhido) |
| 98 | `resumos/GO/10. Aloimunização Materna e Doença Hemolítica Perinatal.pdf` | G | `...\Aloimunização_Materna_e_Doença_Hemolítica_Perinatal\Aloimu.pdf` | 19,437,538 | `Flashc.pdf` (1,120,018b, regra Flashc/Mapa); `Aloimunização_Ma.pdf` (3,944,795b, menor que o escolhido) |
| 99 | `resumos/GO/10. Incontinência Urinária.pdf` | G | `...\Incontinência_Urinária\Incontinência_Ur.pdf` | 21,370,564 | `Mapa_M.pdf` (2,676,209b, regra Flashc/Mapa); `Flashc.pdf` (406,117b, regra Flashc/Mapa); `Incont.pdf` (14,680,809b, menor que o escolhido); `Aula_R.pdf` (2,119,792b, menor que o escolhido) |
| 100 | `resumos/GO/11. Câncer de Mama.pdf` | G | `...\Câncer_de_Mama\Câncer_de_Mama.pdf` | 22,456,459 | `Mapa_M.pdf` (8,493,980b, regra Flashc/Mapa); `Flashc.pdf` (405,399b, regra Flashc/Mapa); `Câncer.pdf` (16,040,314b, menor que o escolhido); `Aula_R.pdf` (3,175,366b, menor que o escolhido) |
| 101 | `resumos/GO/12. Câncer do Corpo do Útero.pdf` | G | `...\Câncer_do_Corpo_do_Útero\Câncer.pdf` | 21,403,308 | `Mapa_M.pdf` (2,441,281b, regra Flashc/Mapa); `Flashc.pdf` (425,579b, regra Flashc/Mapa); `Aula_R.pdf` (3,431,451b, menor que o escolhido) |
| 102 | `resumos/GO/12. Modificações Fisiológicas da Gestação.pdf` | G | `...\Modificações_Fisiológicas_da_Gestação\Modificações_Fis.pdf` | 29,456,482 | `Flashc.pdf` (1,118,605b, regra Flashc/Mapa); `Mapa_M.pdf` (4,159,793b, regra Flashc/Mapa); `Modifi.pdf` (28,718,899b, menor que o escolhido) |
| 103 | `resumos/GO/13. Tumores Anexiais e Câncer de Ovário.pdf` | G | `...\Tumores_Anexiais_e_Câncer_de_Ovário\Tumores_Anexiais.pdf` | 21,442,416 | `Mapa_M.pdf` (7,110,482b, regra Flashc/Mapa); `Flashc.pdf` (403,856b, regra Flashc/Mapa); `Tumore.pdf` (13,333,625b, menor que o escolhido); `Aula_E.pdf` (5,451,853b, menor que o escolhido); `Aula_R.pdf` (1,513,776b, menor que o escolhido) |
| 104 | `resumos/GO/14. Doenças de Vulva e Vagina.pdf` | G | `...\Doenças_de_Vulva_e_Vagina\Doenças__da_Vulv.pdf` | 21,690,916 | `Flashc.pdf` (416,258b, regra Flashc/Mapa); `Doença.pdf` (13,351,071b, menor que o escolhido); `Doenças_da_Vulva.pdf` (3,200,349b, menor que o escolhido); `Aula_R.pdf` (2,575,231b, menor que o escolhido) |
| 105 | `resumos/GO/15. Vitalidade Fetal.pdf` | G | `...\Vitalidade_Fetal\Vitalidade_Fetal.pdf` | 32,031,864 | `Mapa_M.pdf` (3,467,187b, regra Flashc/Mapa); `Flashc.pdf` (1,109,850b, regra Flashc/Mapa); `Vitali.pdf` (30,972,640b, menor que o escolhido) |
| 106 | `resumos/GO/16. Cervicites.pdf` | G | `...\Cervicites\Cervicites.pdf` | 22,952,211 | `Flashc.pdf` (3,346,914b, regra Flashc/Mapa); `Mapa_M.pdf` (2,071,700b, regra Flashc/Mapa); `Cervic.pdf` (13,355,686b, menor que o escolhido) |
| 107 | `resumos/GO/17. Doença Inflamatória Pélvica (DIP).pdf` | G | `...\Doença_Inflamatória_Pélvica_(DIP)\Doença_Inflamató.pdf` | 23,198,965 | `Flashc.pdf` (3,425,367b, regra Flashc/Mapa); `Mapa_M.pdf` (4,096,401b, regra Flashc/Mapa); `Doença.pdf` (15,260,104b, menor que o escolhido); `Aula_R.pdf` (1,374,400b, menor que o escolhido) |
| 108 | `resumos/GO/17. Parto Vaginal Operatório.pdf` | G | `...\Parto_Vaginal_Operatório\Parto .pdf` | 20,927,996 | `Flashc.pdf` (2,496,156b, regra Flashc/Mapa); `Parto_.pdf` (3,747,085b, menor que o escolhido) |
| 109 | `resumos/GO/19. Assistência à Vítima de Violência Sexual.pdf` | G | `...\Assistência_à_Vítima_de_Violência_Sexual\Assistência_à_Ví.pdf` | 22,169,321 | `Flashc.pdf` (392,315b, regra Flashc/Mapa); `Mapa_M.pdf` (558,537b, regra Flashc/Mapa); `Assist.pdf` (12,865,777b, menor que o escolhido); `Aula_R.pdf` (1,995,963b, menor que o escolhido) |
| 110 | `resumos/GO/19. Indução do Parto e Pós-Datismo.pdf` | G | `...\Indução_do_Parto_e_Pós-Datismo\Induçã.pdf` | 18,885,669 | `Flashc.pdf` (2,484,958b, regra Flashc/Mapa); `Indução_do_Parto.pdf` (2,914,542b, menor que o escolhido) |
| 111 | `resumos/GO/2. Rotura Prematura de Membranas (RPM).pdf` | G | `...\Rotura_Prematura_de_Membranas_(RPM)\Rotura_Prematura.pdf` | 24,048,020 | `Mapa_M.pdf` (3,193,978b, regra Flashc/Mapa); `Flashc.pdf` (1,480,332b, regra Flashc/Mapa); `Rotura.pdf` (17,665,645b, menor que o escolhido); `Rotura_Prematura_de_Membrana_(RPM).pdf` (3,756,084b, menor que o escolhido) |
| 112 | `resumos/GO/20. Adenomiose.pdf` | G | `...\Adenomiose\Adenom.pdf` | 16,540,987 | `Mapa_M.pdf` (1,886,944b, regra Flashc/Mapa); `Flashc.pdf` (6,067,122b, regra Flashc/Mapa); `Aula_R.pdf` (5,475,827b, menor que o escolhido); `Adenomiose.pdf` (2,073,230b, menor que o escolhido) |
| 113 | `resumos/GO/20. Restrição de Crescimento Fetal e Óbito Fetal.pdf` | G | `...\Restrição_de_Crescimento_Fetal_e_Óbito_Fetal\Restri.pdf` | 19,908,439 | `Mapa_M.pdf` (5,245,457b, regra Flashc/Mapa); `Flashc.pdf` (1,117,766b, regra Flashc/Mapa); `Restrição_de_Cre.pdf` (4,100,782b, menor que o escolhido) |
| 114 | `resumos/GO/21. Rastreamento do Câncer de Colo Uterino.pdf` | G | `...\Rastreamento_do_Câncer_de_Colo_Uterino\Rastreamento_do_.pdf` | 28,545,041 | `Mapa_M.pdf` (17,508,143b, regra Flashc/Mapa); `Flashc.pdf` (4,613,626b, regra Flashc/Mapa); `Rastre.pdf` (25,951,814b, menor que o escolhido); `Rastreamento_Cân.pdf` (7,140,028b, menor que o escolhido); `Aula_R.pdf` (4,875,079b, menor que o escolhido); `Rastreamento_de_.pdf` (3,918,278b, menor que o escolhido) |
| 115 | `resumos/GO/21. Ultrassom em Obstetrícia.pdf` | G | `...\Ultrassom_em_Obstetrícia\Ultras.pdf` | 29,263,484 | `Mapa_M.pdf` (2,783,234b, regra Flashc/Mapa); `Flashc.pdf` (795,873b, regra Flashc/Mapa) |
| 116 | `resumos/GO/22. Câncer de Colo Uterino.pdf` | G | `...\Câncer_de_Colo_Uterino\Câncer_de_Colo_U.pdf` | 23,400,974 | `Mapa_M.pdf` (2,744,135b, regra Flashc/Mapa); `Flashc.pdf` (3,769,223b, regra Flashc/Mapa); `Câncer.pdf` (15,289,117b, menor que o escolhido); `Câncer do Corpo .pdf` (14,325,009b, menor que o escolhido); `Câncer_de_colo.pdf` (2,684,855b, menor que o escolhido); `Aula_R.pdf` (2,362,856b, menor que o escolhido) |
| 117 | `resumos/GO/23. Climatério e Terapia Hormonal.pdf` | G | `...\Climatério_e_Terapia_Hormonal\Climatério_e_Ter.pdf` | 23,001,739 | `Flashc.pdf` (2,189,533b, regra Flashc/Mapa); `Mapa_M.pdf` (751,202b, regra Flashc/Mapa); `Climat.pdf` (15,998,634b, menor que o escolhido); `Aula_R.pdf` (1,139,415b, menor que o escolhido) |
| 118 | `resumos/GO/23. Sangramento da Primeira Metade.pdf` | G | `...\Sangramento_da_Primeira_Metade\Sangramento_da_P.pdf` | 31,682,934 | `Flashc.pdf` (3,763,977b, regra Flashc/Mapa); `Mapa_M.pdf` (3,153,135b, regra Flashc/Mapa); `Sangra.pdf` (26,998,087b, menor que o escolhido) |
| 119 | `resumos/GO/24. Miomatose Uterina.pdf` | G | `...\Miomatose_Uterina\Miomatose_Uterina.pdf` | 24,475,905 | `Mapa_M.pdf` (3,713,382b, regra Flashc/Mapa); `Flashc.pdf` (4,027,202b, regra Flashc/Mapa); `Miomat.pdf` (20,125,190b, menor que o escolhido) |
| 120 | `resumos/GO/24. Sangramento da Segunda Metade.pdf` | G | `...\Sangramento_da_Segunda_Metade\Sangra.pdf` | 24,003,631 | `Mapa_M.pdf` (7,348,489b, regra Flashc/Mapa); `Flashc.pdf` (5,167,001b, regra Flashc/Mapa); `Sangramento_da_S.pdf` (5,789,742b, menor que o escolhido) |
| 121 | `resumos/GO/26. Anatomia e Embriologia do Trato Genital Feminino.pdf` | G | `...\Anatomia_e_Embriologia_do_Trato_Genital_Feminino\Anatomia_e_Embri.pdf` | 25,428,016 | `Flashc.pdf` (400,487b, regra Flashc/Mapa); `Anatom.pdf` (20,441,599b, menor que o escolhido); `Anatomia_do_Trat.pdf` (5,541,345b, menor que o escolhido); `Embrio.pdf` (4,259,246b, menor que o escolhido) |
| 122 | `resumos/GO/27. Infertilidade Conjugal.pdf` | G | `...\Infertilidade_Conjugal\Infert.pdf` | 17,696,061 | `Mapa_M.pdf` (4,866,420b, regra Flashc/Mapa); `Flashc.pdf` (413,439b, regra Flashc/Mapa); `Infertilidade_Co.pdf` (4,225,666b, menor que o escolhido); `Aula_R.pdf` (3,035,408b, menor que o escolhido) |
| 123 | `resumos/GO/28. Dor Pélvica Crônica e Dismenorreia.pdf` | G | `...\Dor_Pélvica_Crônica_e_Dismenorreia\Dor_Pé.pdf` | 22,574,097 | `Flashc.pdf` (376,800b, regra Flashc/Mapa); `Dor Pé.pdf` (13,337,335b, menor que o escolhido); `Dor_Pélvica_Crônica.pdf` (3,173,553b, menor que o escolhido); `Dismen.pdf` (2,828,226b, menor que o escolhido) |
| 124 | `resumos/GO/29. Sexualidade.pdf` | G | `...\Sexualidade\Sexual.pdf` | 13,314,647 | `Flashc.pdf` (393,296b, regra Flashc/Mapa); `Sexualidade.pdf` (3,000,421b, menor que o escolhido) |
| 125 | `resumos/GO/3. Amenorreia.pdf` | G | `...\Amenorreia\Amenorreia.pdf` | 24,651,420 | `Mapa_M.pdf` (8,109,791b, regra Flashc/Mapa); `Flashc.pdf` (391,421b, regra Flashc/Mapa); `Amenor.pdf` (18,188,549b, menor que o escolhido); `Amenorreia_-_Aul.pdf` (2,375,582b, menor que o escolhido) |
| 126 | `resumos/GO/30. Síndrome Pré-Menstrual.pdf` | G | `...\Síndrome_Pré-Menstrual\Síndro.pdf` | 12,836,386 | `Flashc.pdf` (349,999b, regra Flashc/Mapa); `Síndrome_Pré-Men.pdf` (2,886,457b, menor que o escolhido) |
| 127 | `resumos/GO/31. Abdome Agudo em Ginecologia.pdf` | G | `...\Abdome_Agudo_em_Ginecologia\Abdome_Agudo_em_.pdf` | 14,536,766 | `Flashc.pdf` (372,533b, regra Flashc/Mapa); `Abdome.pdf` (14,235,902b, menor que o escolhido) |
| 128 | `resumos/GO/4. Gestação Múltipla.pdf` | G | `...\Gestação_Múltipla\Gestação_Múltipla.pdf` | 24,316,244 | `Mapa_M.pdf` (3,495,989b, regra Flashc/Mapa); `Flashc.pdf` (7,362,929b, regra Flashc/Mapa); `Gestaç.pdf` (17,329,508b, menor que o escolhido) |
| 129 | `resumos/GO/4. Síndrome dos Ovários Policísticos.pdf` | G | `...\Síndrome_dos_Ovários_Policísticos\Síndrome_dos_Ová.pdf` | 25,860,254 | `Mapa_M.pdf` (2,773,563b, regra Flashc/Mapa); `Flashc.pdf` (2,947,549b, regra Flashc/Mapa); `Síndro.pdf` (18,472,644b, menor que o escolhido); `Aula_R.pdf` (2,872,704b, menor que o escolhido) |
| 130 | `resumos/GO/6. Bacia Obstétrica, Pelvimetria e Estática Fetal.pdf` | G | `...\Bacia_Obstétrica,_Pelvimetria_e_Estática_Fetal\Bacia_.pdf` | 26,364,771 | `Mapa_M.pdf` (8,726,641b, regra Flashc/Mapa); `Flashc.pdf` (6,531,266b, regra Flashc/Mapa); `Bacia .pdf` (21,347,834b, menor que o escolhido) |
| 131 | `resumos/GO/6. Pólipos Uterinos.pdf` | G | `...\Pólipos_Uterinos\Pólipo.pdf` | 12,117,278 | `Flashc.pdf` (3,479,070b, regra Flashc/Mapa); `Pólipos_Uterinos.pdf` (3,991,935b, menor que o escolhido) |
| 132 | `resumos/GO/7. Infecção Puerperal.pdf` | G | `...\Infecção_Puerperal\Infecç.pdf` | 16,200,968 | `Mapa_M.pdf` (1,713,331b, regra Flashc/Mapa); `Flashc.pdf` (1,687,976b, regra Flashc/Mapa); `Infecção_Puerperal.pdf` (2,149,800b, menor que o escolhido) |
| 133 | `resumos/GO/7. Rastreamento do Câncer de Mama.pdf` | G | `...\Rastreamento_do_Câncer_de_Mama\Rastreamento_do_.pdf` | 22,652,305 | `Flashc.pdf` (4,682,152b, regra Flashc/Mapa); `Mapa_M.pdf` (1,480,287b, regra Flashc/Mapa); `Rastre.pdf` (14,521,609b, menor que o escolhido); `Aula_R.pdf` (3,280,035b, menor que o escolhido) |
| 134 | `resumos/GO/8. Sífilis na Gestação e Sífilis Congênitas.pdf` | G | `...\Sífilis_na_Gestação_e_Sífilis_Congênitas\Sífili.pdf` | 14,229,502 | `Mapa_M.pdf` (6,739,746b, regra Flashc/Mapa); `Flashc.pdf` (1,143,172b, regra Flashc/Mapa); `Resumo Estratégico.pdf` (11,904,872b, menor que o escolhido) |
| 135 | `resumos/GO/9. Doenças benignas da Mama.pdf` | G | `...\Doenças_Benignas_da_Mama\Doenças_Benignas.pdf` | 23,444,596 | `Doença.pdf` (15,883,180b, menor que o escolhido); `DBM - Mapa Mental.pdf` (5,998,358b, menor que o escolhido); `DBM - Flashcards.pdf` (429,214b, menor que o escolhido) |
| 136 | `resumos/GO/9. Infecções Congênitas na Gestação.pdf` | G | `...\Infecções_Congênitas_na_Gestação\Infecções_Congênitas.pdf` | 16,175,898 | `Mapa_Mental_-_In.pdf` (6,135,770b, regra Flashc/Mapa); `Flashc.pdf` (1,124,299b, regra Flashc/Mapa); `Mapa_M.pdf` (481,114b, regra Flashc/Mapa); `Infecç.pdf` (15,429,571b, menor que o escolhido); `Infecções_Congên.pdf` (2,087,738b, menor que o escolhido) |
| 137 | `resumos/Pediatria/1. Puberdade.pdf` | G | `...\Puberdade\Puberd.pdf` | 16,601,167 | `Mapa_m.pdf` (3,443,818b, regra Flashc/Mapa); `Flashc.pdf` (4,213,006b, regra Flashc/Mapa); `Puberdade.pdf` (13,554,012b, menor que o escolhido); `Aula_R.pdf` (2,515,640b, menor que o escolhido) |
| 138 | `resumos/Pediatria/10. Hiperplasia Adrenal Congênita.pdf` | G | `...\Hiperplasia_Adrenal_Congênita\Hiperplasia_Adre.pdf` | 14,316,018 | `Mapa_M.pdf` (1,738,020b, regra Flashc/Mapa); `Flashc.pdf` (844,381b, regra Flashc/Mapa); `Hiperp.pdf` (14,316,018b, menor que o escolhido) |
| 139 | `resumos/Pediatria/11. Distúrbios Respiratórios do Período Neonatal.pdf` | G | `...\Distúrbios_Respiratórios_do_Período_Neonatal\Distúr.pdf` | 15,687,143 | `Mapa_m.pdf` (4,018,154b, regra Flashc/Mapa); `Flashc.pdf` (1,430,124b, regra Flashc/Mapa) |
| 140 | `resumos/Pediatria/14. Enurese Noturna.pdf` | G | `...\Enurese_Noturna\Enures.pdf` | 12,173,276 | `Flashc.pdf` (700,814b, regra Flashc/Mapa); `Enurese_Noturna.pdf` (10,930,683b, menor que o escolhido); `Enurese_Noturna_.pdf` (1,837,631b, menor que o escolhido) |
| 141 | `resumos/Pediatria/15. Pneumonias na Infância.pdf` | G | `...\Pneumonias_na_Infância\Pneumo.pdf` | 15,371,302 | `Flashc.pdf` (2,162,436b, regra Flashc/Mapa); `Pneumonias_na_In.pdf` (9,801,301b, menor que o escolhido); `Aula_R.pdf` (2,846,970b, menor que o escolhido) |
| 142 | `resumos/Pediatria/16. Hipotireoidismo Congênito.pdf` | G | `...\Hipotireoidismo_Congênito\Hipoti.pdf` | 10,801,744 | `Mapa_M.pdf` (1,745,939b, regra Flashc/Mapa); `Flashc.pdf` (1,642,822b, regra Flashc/Mapa); `Hipotireoidismo_.pdf` (9,590,894b, menor que o escolhido) |
| 143 | `resumos/Pediatria/18. Aleitamento Materno.pdf` | G | `...\Aleitamento_Materno\Aleita.pdf` | 12,636,864 | `Flashc.pdf` (3,497,721b, regra Flashc/Mapa); `Aula_R.pdf` (2,208,106b, menor que o escolhido); `Aleitamento_Materno.pdf` (2,014,323b, menor que o escolhido) |
| 144 | `resumos/Pediatria/19. Desnutrição na Infância.pdf` | G | `...\Desnutrição_na_Infância\Desnut.pdf` | 13,703,890 | `Flashc.pdf` (2,469,722b, regra Flashc/Mapa); `Desnutrição_na_I.pdf` (3,867,703b, menor que o escolhido); `Aula_R.pdf` (2,435,939b, menor que o escolhido) |
| 145 | `resumos/Pediatria/2. BRUE-SMSL (Brief Resolved Unexplained Events - Síndrome da Morte Súbita do Lactente).pdf` | G | `...\BRUE___SMSL_(Brief_Resolved_Unexplained_Events___Síndrome_da_Morte_Súbita_do_Lactente)\BRUE  .pdf` | 12,307,093 | `Flashc.pdf` (1,202,098b, regra Flashc/Mapa); `Mapa_m.pdf` (3,034,492b, regra Flashc/Mapa); `Brief_.pdf` (10,854,660b, menor que o escolhido); `BRUE__.pdf` (1,281,247b, menor que o escolhido); `Aula_R.pdf` (1,243,401b, menor que o escolhido) |
| 146 | `resumos/Pediatria/20. Infecções Congênitas.pdf` | G | `...\Infecções_Congênitas\Infecções_Congênitas.pdf` | 16,175,898 | `Flashc.pdf` (5,970,951b, regra Flashc/Mapa); `Infecç.pdf` (15,429,571b, menor que o escolhido) |
| 147 | `resumos/Pediatria/23. Doença Celíaca em Pediatria.pdf` | G | `...\Doença_Celíaca_em_Pediatria\Doença.pdf` | 15,525,429 | `Flashc.pdf` (5,510,616b, regra Flashc/Mapa); `Doença_Celíaca_e.pdf` (12,239,484b, menor que o escolhido); `Doença_Celíaca.pdf` (1,529,528b, menor que o escolhido) |
| 148 | `resumos/Pediatria/24. Desenvolvimento Neuropsicomotor (DNPM).pdf` | G | `...\Desenvolvimento_Neuropsicomotor_(DNPM)\Desenv.pdf` | 25,412,424 | `Flashc.pdf` (7,015,464b, regra Flashc/Mapa); `Desenvolvimento_.pdf` (19,210,377b, menor que o escolhido); `Desenvolvimento_Neuropsicomotor_(DNPM.pdf` (5,701,574b, menor que o escolhido); `Desenvolvimento_Neuropsicomotor_(DNPM)_-_Aula_.pdf` (4,229,044b, menor que o escolhido) |
| 149 | `resumos/Pediatria/26. Choque em Pediatria.pdf` | G | `...\Choque_em_Pediatria\Choque.pdf` | 14,421,214 | `Flashc.pdf` (465,462b, regra Flashc/Mapa); `Choque_em_Pediatria.pdf` (11,183,509b, menor que o escolhido); `Aula_R.pdf` (3,772,495b, menor que o escolhido) |
| 150 | `resumos/Pediatria/31. Fibrose Cística.pdf` | G | `...\Fibrose_Cística\Fibros.pdf` | 15,052,199 | `Flashc.pdf` (5,423,396b, regra Flashc/Mapa); `Fibrose_Cística.pdf` (2,879,155b, menor que o escolhido); `Aula_R.pdf` (2,741,214b, menor que o escolhido) |
| 151 | `resumos/Pediatria/33. Tuberculose na Infância.pdf` | G | `...\Tuberculose_na_Infância\Tuberc.pdf` | 21,801,561 | `Flashc.pdf` (3,243,417b, regra Flashc/Mapa); `Tuberculose_na_I.pdf` (14,639,665b, menor que o escolhido); `Aula_R.pdf` (3,795,335b, menor que o escolhido) |
| 152 | `resumos/Pediatria/34. Doença de Kawasaki.pdf` | G | `...\Doença_de_Kawasaki\Doença.pdf` | 14,885,994 | `Mapa_m.pdf` (2,471,832b, regra Flashc/Mapa); `Flashc.pdf` (3,927,091b, regra Flashc/Mapa); `Doença_de_Kawasaki.pdf` (12,374,904b, menor que o escolhido); `Doença_de_Kawasa.pdf` (2,784,447b, menor que o escolhido) |
| 153 | `resumos/Pediatria/35. Bronquiolite.pdf` | G | `...\Bronquiolite\Bronqu.pdf` | 13,683,929 | `Mapa_M.pdf` (2,096,997b, regra Flashc/Mapa); `Flashc.pdf` (3,708,266b, regra Flashc/Mapa); `Bronquiolite.pdf` (12,476,894b, menor que o escolhido); `Aula_R.pdf` (2,497,765b, menor que o escolhido) |
| 154 | `resumos/Pediatria/36. Hipertensão Arterial na Criança e Adolescente.pdf` | G | `...\Hipertensão_Arterial_na_Criança_e_Adolescente\Hipert.pdf` | 14,511,168 | `Flashc.pdf` (2,193,177b, regra Flashc/Mapa); `Hipertensão_Arte.pdf` (11,530,999b, menor que o escolhido); `Aula_R.pdf` (2,329,305b, menor que o escolhido) |
| 155 | `resumos/Pediatria/39. Febre na Pediatria.pdf` | G | `...\Febre_na_Pediatria\Febre .pdf` | 13,561,013 | `Flashc.pdf` (550,270b, regra Flashc/Mapa); `Febre_.pdf` (11,840,256b, menor que o escolhido) |
| 156 | `resumos/Pediatria/4. Alergia Alimentar.pdf` | G | `...\Alergia_Alimentar\Alergi.pdf` | 12,320,543 | `Mapa_m.pdf` (2,418,655b, regra Flashc/Mapa); `Flashc.pdf` (1,468,495b, regra Flashc/Mapa); `Alergia_Alimentar.pdf` (2,986,204b, menor que o escolhido) |
| 157 | `resumos/Pediatria/40. Artrite Idiopática Juvenil (AIJ).pdf` | G | `...\Artrite_Idiopática_Juvenil_(AIJ)\Artrit.pdf` | 15,357,293 | `Flashc.pdf` (4,365,947b, regra Flashc/Mapa); `Artrite_Idiopáti.pdf` (12,506,936b, menor que o escolhido); `Aula_R.pdf` (1,178,647b, menor que o escolhido) |
| 158 | `resumos/Pediatria/41. Cefaleias na infância.pdf` | G | `...\Cefaleias_na_Infância\Cefale.pdf` | 12,293,792 | `Flashc.pdf` (395,020b, regra Flashc/Mapa); `Cefaleias_na_Inf.pdf` (10,882,076b, menor que o escolhido); `Cefaleias_na_Infância_-_Au.pdf` (1,764,922b, menor que o escolhido) |
| 159 | `resumos/Pediatria/42. Segurança em Pediatria.pdf` | G | `...\Segurança_em_Pediatria\Segura.pdf` | 14,889,468 | `Flashc.pdf` (2,656,356b, regra Flashc/Mapa); `Mapa_M.pdf` (1,760,622b, regra Flashc/Mapa); `Segurança_em_Ped.pdf` (14,107,147b, menor que o escolhido) |
| 160 | `resumos/Pediatria/43. Diagnóstico Nutricional.pdf` | G | `...\Diagnóstico_Nutricional\Diagnó.pdf` | 15,098,496 | `Mapa_M.pdf` (5,355,976b, regra Flashc/Mapa); `Flashc.pdf` (397,604b, regra Flashc/Mapa); `Diagnóstico_Nutr.pdf` (2,955,186b, menor que o escolhido); `Aula_R.pdf` (2,484,922b, menor que o escolhido) |
| 161 | `resumos/Pediatria/44. Tópicos em Pediatria.pdf` | G | `...\Tópicos_em_Pediatria\Tópico.pdf` | 13,132,365 | `Flashc.pdf` (1,089,945b, regra Flashc/Mapa); `Tópicos_em_Pediatria.pdf` (11,794,489b, menor que o escolhido); `Tópicos_em_pedia.pdf` (1,823,386b, menor que o escolhido) |
| 162 | `resumos/Pediatria/45. Coqueluche.pdf` | G | `...\Coqueluche\Coquel.pdf` | 17,306,717 | `Flashc.pdf` (6,986,218b, regra Flashc/Mapa); `Mapa_M.pdf` (1,891,002b, regra Flashc/Mapa); `Coqueluche.pdf` (12,567,412b, menor que o escolhido); `Coqueluche_-_Aul.pdf` (1,991,378b, menor que o escolhido) |
| 163 | `resumos/Pediatria/47. Doença do Refluxo Gastroesofágico em Pediatria.pdf` | G | `...\Doença_do_Refluxo_Gastroesofágico_em_Pediatria\Doença.pdf` | 12,514,797 | `Mapa_M.pdf` (1,683,138b, regra Flashc/Mapa); `Flashc.pdf` (1,463,551b, regra Flashc/Mapa); `Doença_do_Reflux.pdf` (11,047,012b, menor que o escolhido) |
| 164 | `resumos/Pediatria/48. Diarreia.pdf` | G | `...\Diarreia\Diarre.pdf` | 14,756,751 | `Flashc.pdf` (2,222,541b, regra Flashc/Mapa); `Diarreia.pdf` (12,828,969b, menor que o escolhido); `Diarré.pdf` (7,232,687b, menor que o escolhido) |
| 165 | `resumos/Pediatria/5. Obesidade Infantil e na Adolescência.pdf` | G | `...\Obesidade_Infantil_e_na_Adolescência\Obesid.pdf` | 13,843,854 | `Mapa_M.pdf` (1,861,735b, regra Flashc/Mapa); `Flashc.pdf` (2,835,802b, regra Flashc/Mapa); `Obesidade_Infant.pdf` (10,157,729b, menor que o escolhido); `Aula_R.pdf` (2,569,988b, menor que o escolhido) |
| 166 | `resumos/Pediatria/7. Anafilaxia e Urticária.pdf` | G | `...\Anafilaxia_e_Urticária\Anafilaxia_e_Urticária.pdf` | 17,292,209 | `Flashc.pdf` (2,296,660b, regra Flashc/Mapa); `Anafil.pdf` (17,235,428b, menor que o escolhido); `Anafilaxia_e_Urt.pdf` (1,086,614b, menor que o escolhido) |
| 167 | `resumos/Pediatria/9. Constipação Intestinal.pdf` | G | `...\Constipação_Intestinal\Constipação_Inte.pdf` | 13,904,078 | `Flashc.pdf` (2,174,010b, regra Flashc/Mapa); `Consti.pdf` (13,904,078b, menor que o escolhido) |
| 168 | `resumos/Preventiva/13. Testes Diagnósticos.pdf` | G | `...\Testes_Diagnósticos\Testes.pdf` | 9,045,957 | `Mapa_M.pdf` (3,381,069b, regra Flashc/Mapa) |
| 169 | `resumos/Preventiva/14. História do SUS.pdf` | D | `...\História_do_SUS\História_do_SUS.pdf` | 23,913,959 | `Flashc.pdf` (1,095,075b, regra Flashc/Mapa); `Histór.pdf` (19,342,079b, menor que o escolhido) |
| 170 | `resumos/Preventiva/15. Processos de Descentralização e Regionalização do SUS.pdf` | G | `...\Processos_de_Descentralização_e_Regionalização_do_SUS\Proces.pdf` | 2,345,466 | `Mapa_M.pdf` (2,403,102b, regra Flashc/Mapa) |
| 171 | `resumos/Preventiva/17. Políticas de Saúde.pdf` | D | `...\Políticas_de_Saúde\Políticas_de_Saúde.pdf` | 26,846,630 | `Flashc.pdf` (1,255,890b, regra Flashc/Mapa); `Políti.pdf` (21,290,943b, menor que o escolhido) |
| 172 | `resumos/Preventiva/18. Financiamento em Saúde.pdf` | G | `...\Financiamento_em_Saúde\Resumo.pdf` | 6,932,572 | `Mapa_M.pdf` (412,685b, regra Flashc/Mapa); `Financ.pdf` (1,606,811b, menor que o escolhido) |
| 173 | `resumos/Preventiva/2. Estatística Médica.pdf` | D | `...\Estatística_Médica\Estatística_Médica.pdf` | 27,879,072 | `Flashc.pdf` (2,420,627b, regra Flashc/Mapa); `Estatí.pdf` (26,920,623b, menor que o escolhido) |
| 174 | `resumos/Preventiva/20. Saúde do Idoso.pdf` | D | `...\Saúde_do_Idoso\Saúde .pdf` | 21,875,435 | `Flashc.pdf` (2,032,271b, regra Flashc/Mapa); `Saúde_.pdf` (5,450,138b, menor que o escolhido) |
| 175 | `resumos/Preventiva/21. Pesquisa Epidemiológica e Medidas de Associação.pdf` | G | `...\Pesquisa_Epidemiológica_e_Medidas_de_Associação\Resumo.pdf` | 29,541,308 | `Mapa_M.pdf` (5,242,123b, regra Flashc/Mapa); `Pesqui.pdf` (11,964,843b, menor que o escolhido) |
| 176 | `resumos/Preventiva/4. Marcos Legais do Sistema Único de Saúde.pdf` | G | `...\Marcos_legais_do_Sistema_Único_de_Saúde\Marcos_legais_do_SUS.pdf` | 17,320,173 | `Mapa_M.pdf` (1,851,526b, regra Flashc/Mapa); `Marcos.pdf` (3,102,088b, menor que o escolhido) |
| 177 | `resumos/Preventiva/5. Bases de Saúde do Trabalhador e Normas Regulamentadoras.pdf` | D | `...\1\Bases .pdf` | 27,133,366 | `Flashc.pdf` (809,842b, regra Flashc/Mapa); `Flashcards_-_Nor.pdf` (1,339,833b, regra Flashc/Mapa); `Bases_.pdf` (8,071,765b, menor que o escolhido) |
| 178 | `resumos/Preventiva/6. Medidas de Saúde Coletiva - Parte I_ Indicadores de Morbidade.pdf` | D | `...\Medidas_de_Saúde_Coletiva_-_Parte_I__Indicadores_de_Morbidade\Medida.pdf` | 29,205,617 | `Flashc.pdf` (6,890,271b, regra Flashc/Mapa); `Mapa_M.pdf` (9,023,359b, regra Flashc/Mapa); `Medidas_de_Saúde_Coletiva_.pdf` (28,058,230b, menor que o escolhido); `Medidas_de_Saúde.pdf` (27,985,499b, menor que o escolhido); `Medidas_de_Saúde_Coletiva_-_Parte_I__Indicadores_de_Morbidade.pdf` (17,099,157b, menor que o escolhido); `Medidas_de_Saúde_Coletiva_-_Parte_I__Indicador.pdf` (17,026,053b, menor que o escolhido) |
| 179 | `resumos/Preventiva/8. Medidas de Saúde Coletiva - Parte III_ Indicadores Demográficos + Transição Demográfica-Epidemiológica.pdf` | D | `...\Medidas_de_Saúde_Coletiva_-_Parte_III__Indicadores_Demográficos_+_Transição_Demográfica-Epidemiológica\Medidas_de_Saúde_Coletiva_.pdf` | 29,083,029 | `Flashc.pdf` (4,482,431b, regra Flashc/Mapa); `Mapa_M.pdf` (7,780,575b, regra Flashc/Mapa); `Medida.pdf` (2,629,528b, menor que o escolhido) |
| 180 | `resumos/Preventiva/9. Processos Epidêmicos e Epidemiologia das Doenças Infecciosas.pdf` | D | `...\Processos_Epidêmicos_e_Epidemiologia_das_Doenças_Infecciosas\Proces.pdf` | 24,098,624 | - |

## 5. Nao-mapeados

**Nenhum.** Os 180 destinos tiveram origem exata identificada e copiada.

## 6. Ambiguidades registradas (resolvidas por precedencia declarada, nao por chute)

176 destinos tinham mais de uma pasta candidata. Na quase totalidade e o **mesmo tema presente em G: e em D:**, resolvido pela precedencia G: > D:. Casos com duplicata **dentro do proprio G:** (153):

- `resumos/Cirurgia/1. Abdome Agudo Hemorrágico.pdf`
  - candidatos G:: `G:Cirurgia/Abdome_Agudo_Hemorrágico(d2)`, `G:Cirurgia/Abdome_Agudo_Hemorrágico(d3)`
  - escolhido: `Abdome_Agudo_Hem.pdf` (25,628,627b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/10. Cirurgia Torácica.pdf`
  - candidatos G:: `G:Cirurgia/Cirurgia_Torácica(d2)`, `G:Cirurgia/Cirurgia_Torácica(d3)`
  - escolhido: `Cirurg.pdf` (32,288,804b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/11. Cirurgia Plástica.pdf`
  - candidatos G:: `G:Cirurgia/Cirurgia_Plástica(d2)`, `G:Cirurgia/Cirurgia_Plástica(d3)`
  - escolhido: `Cirurg.pdf` (25,074,727b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/12. Cirurgia Infantil - Parte I.pdf`
  - candidatos G:: `G:Cirurgia/Cirurgia_Infantil_-_Parte_I(d2)`, `G:Cirurgia/Cirurgia_Infantil_-_Parte_I(d3)`
  - escolhido: `Cirurgia Infantil - Apostila.pdf` (31,876,401b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/13. Cirurgia Infantil - Parte II.pdf`
  - candidatos G:: `G:Cirurgia/Cirurgia_Infantil_-_Parte_II(d2)`, `G:Cirurgia/Cirurgia_Infantil_-_Parte_II(d3)`
  - escolhido: `Cirurg.pdf` (24,687,161b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/14. Cirurgia Infantil - Parte III.pdf`
  - candidatos G:: `G:Cirurgia/Cirurgia_Infantil_-_Parte_III(d2)`, `G:Cirurgia/Cirurgia_Infantil_-_Parte_III(d3)`
  - escolhido: `Cirurg.pdf` (23,707,146b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/15. Abdome agudo vascular.pdf`
  - candidatos G:: `G:Cirurgia/Abdome_Agudo_Vascular(d2)`, `G:Cirurgia/Abdome_Agudo_Vascular(d3)`
  - escolhido: `Abdome.pdf` (34,759,966b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/16. Abdome agudo obstrutivo.pdf`
  - candidatos G:: `G:Cirurgia/Abdome_Agudo_Obstrutivo(d2)`, `G:Cirurgia/Abdome_Agudo_Obstrutivo(d3)`
  - escolhido: `Abdome.pdf` (46,561,422b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/17. Abdome Agudo Inflamatório - Diverticulite Aguda.pdf`
  - candidatos G:: `G:Cirurgia/Abdome_Agudo_Inflamatório_-_Diverticulite_Aguda(d2)`, `G:Cirurgia/Abdome_Agudo_Inflamatório_-_Diverticulite_Aguda(d3)`
  - escolhido: `Abdome_Agudo_Inf.pdf` (22,119,101b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/19. Vesícula e Vias Biliares.pdf`
  - candidatos G:: `G:Cirurgia/Vesícula_e_Vias_Biliares(d2)`, `G:Cirurgia/Vesícula_e_Vias_Biliares(d3)`
  - escolhido: `Vesícu.pdf` (41,456,183b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/20. Trauma Vascular de Extremidades e Musculoesquelético.pdf`
  - candidatos G:: `G:Cirurgia/Trauma_Vascular_de_Extremidades_e_Musculoesquelético(d2)`, `G:Cirurgia/Trauma_Vascular_de_Extremidades_e_Musculoesquelético(d3)`
  - escolhido: `Trauma.pdf` (26,486,760b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/22. Trauma de Face e Cervical.pdf`
  - candidatos G:: `G:Cirurgia/Trauma_de_Face_e_Cervical(d2)`, `G:Cirurgia/Trauma_de_Face_e_Cervical(d3)`
  - escolhido: `Trauma_de_Face_e.pdf` (25,218,052b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/23. Trauma Abdominal e Pélvico.pdf`
  - candidatos G:: `G:Cirurgia/Trauma_Abdominal_e_Pélvico(d2)`, `G:Cirurgia/Trauma_Abdominal_e_Pélvico(d3)`
  - escolhido: `Trauma.pdf` (41,016,541b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/24. Temas Gerais em Cirurgia.pdf`
  - candidatos G:: `G:Cirurgia/Temas_Gerais_em_Cirurgia(d2)`, `G:Cirurgia/Temas_Gerais_em_Cirurgia(d3)`
  - escolhido: `Temas_.pdf` (31,955,038b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/25. Resposta Endócrino-Metabólica ao Trauma.pdf`
  - candidatos G:: `G:Cirurgia/Resposta_Endócrino-Metabólica_ao_Trauma(d2)`, `G:Cirurgia/Resposta_Endócrino-Metabólica_ao_Trauma(d3)`
  - escolhido: `Respos.pdf` (23,752,703b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/26. Proctologia.pdf`
  - candidatos G:: `G:Cirurgia/Proctologia(d2)`, `G:Cirurgia/Proctologia(d3)`
  - escolhido: `Procto.pdf` (27,805,780b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/28. Neoplasias do apêndice cecal.pdf`
  - candidatos G:: `G:Cirurgia/Neoplasias_do_Apêndice_Cecal(d2)`, `G:Cirurgia/Neoplasias_do_Apêndice_Cecal(d3)`
  - escolhido: `Neoplasias_do_Ap.pdf` (22,101,473b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/3. Urologia.pdf`
  - candidatos G:: `G:Cirurgia/Urologia(d2)`, `G:Cirurgia/Urologia(d3)`
  - escolhido: `Urolog.pdf` (28,957,376b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/30. Complicações Pós-Operatórias.pdf`
  - candidatos G:: `G:Cirurgia/Complicações_Pós-Operatórias(d2)`, `G:Cirurgia/Complicações_Pós-Operatórias(d3)`
  - escolhido: `Compli.pdf` (26,884,008b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/31. Cicatrização de Feridas.pdf`
  - candidatos G:: `G:Cirurgia/Cicatrização_de_Feridas(d2)`, `G:Cirurgia/Cicatrização_de_Feridas(d3)`
  - escolhido: `Cicatr.pdf` (26,372,962b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/32. Abdome Agudo Perfurativo.pdf`
  - candidatos G:: `G:Cirurgia/Abdome_Agudo_Perfurativo(d2)`, `G:Cirurgia/Abdome_Agudo_Perfurativo(d3)`
  - escolhido: `Abdome.pdf` (26,144,451b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/4. Urgências Abdominais Abdome Agudo.pdf`
  - candidatos G:: `G:Cirurgia/Urgências_Abdominais_-_Abdome_Agudo(d2)`, `G:Cirurgia/Urgências_Abdominais_-_Abdome_Agudo(d3)`
  - escolhido: `Urgências_Abdomi.pdf` (27,770,790b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/5. Trauma - Choque.pdf`
  - candidatos G:: `G:Cirurgia/Trauma_-_Choque(d2)`, `G:Cirurgia/Trauma_-_Choque(d3)`
  - escolhido: `Trauma.pdf` (22,489,264b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/7. Queimaduras e Trauma Elétrico.pdf`
  - candidatos G:: `G:Cirurgia/Queimaduras_e_Trauma_Elétrico(d2)`, `G:Cirurgia/Queimaduras_e_Trauma_Elétrico(d3)`
  - escolhido: `Queimaduras_e_Tr.pdf` (23,214,250b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Cirurgia/8. Abdome Agudo Inflamatório - Apendicite Aguda.pdf`
  - candidatos G:: `G:Cirurgia/Abdome_Agudo_Inflamatório_-_Apendicite_Aguda(d2)`, `G:Cirurgia/Abdome_Agudo_Inflamatório_-_Apendicite_Aguda(d3)`
  - escolhido: `Abdome_Agudo_Inf.pdf` (24,316,355b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/10. IAMCSSST (Infarto Agudo do Miocárdio com Supradesnivelamento de Segmento ST).pdf`
  - candidatos G:: `G:Cardiologia/IAMCSSST_(Infarto_Agudo_do_Miocárdio_com_Supradesnivelamento_de_Segmento_ST)(d3)`, `G:Cardiologia/IAMCSSST_(Infarto_Agudo_do_Miocárdio_com_Supradesnivelamento_de_Segmento_ST)(d3)`
  - escolhido: `IAMCSS.pdf` (25,736,510b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/11. Semiologia Cardíaca.pdf`
  - candidatos G:: `G:Cardiologia/Semiologia_Cardíaca(d2)`, `G:Cardiologia/Semiologia_Cardíaca(d3)`
  - escolhido: `Semiologia_Cardíaca_.pdf` (26,467,041b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/12. Síndromes Aórticas Agudas.pdf`
  - candidatos G:: `G:Cardiologia/Síndromes_Aórticas_Agudas(d2)`, `G:Cardiologia/Síndromes_Aórticas_Agudas(d3)`
  - escolhido: `Síndromes_Aórtic.pdf` (26,663,422b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/13. Dislipidemia e Estratificação de Risco Cardiovascular.pdf`
  - candidatos G:: `G:Cardiologia/Dislipidemia_e_Estratificação_de_Risco_Cardiovascular(d2)`, `G:Cardiologia/Dislipidemia_e_Estratificação_de_Risco_Cardiovascular(d3)`
  - escolhido: `Dislipidemia_e_E.pdf` (24,198,437b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/15. Pericardiopatias.pdf`
  - candidatos G:: `G:Cardiologia/Pericardiopatias(d2)`, `G:Cardiologia/Pericardiopatias(d3)`
  - escolhido: `Pericardiopatias.pdf` (30,184,233b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/16. Parada Cardiorrespiratória (PCR).pdf`
  - candidatos G:: `G:Cardiologia/Parada_Cardiorrespiratória_(PCR)(d2)`, `G:Cardiologia/Parada_Cardiorrespiratória_(PCR)(d3)`
  - escolhido: `Parada_Cardiorrespiratória_PCR.pdf` (28,110,464b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/17. Fibrilação e Flutter Atrial.pdf`
  - candidatos G:: `G:Cardiologia/Fibrilação_e_Flutter_Atrial(d2)`, `G:Cardiologia/Fibrilação_e_Flutter_Atrial(d3)`
  - escolhido: `Fibrilação_e_Flu.pdf` (30,857,850b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/19. Síncope.pdf`
  - candidatos G:: `G:Cardiologia/Síncope(d2)`, `G:Cardiologia/Síncope(d3)`
  - escolhido: `Sincop.pdf` (23,757,362b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/21. Bradiarritmias.pdf`
  - candidatos G:: `G:Cardiologia/Bradiarritmias(d2)`, `G:Cardiologia/Bradiarritmias(d3)`
  - escolhido: `Bradia.pdf` (18,834,746b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Cardiologia/3. Insuficiência Cardíaca (Parte 2)_ Tratamento.pdf`
  - candidatos G:: `G:Cardiologia/Insuficiência_Cardíaca_(Parte_2)__Tratamento(d2)`, `G:Cardiologia/Insuficiência_Cardíaca_(Parte_2)__Tratamento(d3)`
  - escolhido: `Insufi.pdf` (22,737,855b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/1. Histologia e Fisiologia da Pele e Lesões Elementares.pdf`
  - candidatos G:: `G:Dermatologia/Histologia_e_Fisiologia_da_Pele_e_Lesões_Elementares(d2)`, `G:Dermatologia/Histologia_e_Fisiologia_da_Pele_e_Lesões_Elementares(d3)`
  - escolhido: `Histologia_e_Fisiologia_da_Pele_e_Lesões_Eleme.pdf` (23,557,800b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/10. Piodermites.pdf`
  - candidatos G:: `G:Dermatologia/Piodermites(d2)`, `G:Dermatologia/Piodermites(d3)`
  - escolhido: `Pioder.pdf` (20,399,424b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/11. Síndromes Verrucosas.pdf`
  - candidatos G:: `G:Dermatologia/Síndromes_Verrucosas(d2)`, `G:Dermatologia/Síndromes_Verrucosas(d3)`
  - escolhido: `Síndro.pdf` (18,500,465b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/2. Oncologia Cutânea (Câncer de Pele).pdf`
  - candidatos G:: `G:Dermatologia/Oncologia_Cutânea_(Câncer_de_Pele)(d2)`, `G:Dermatologia/Oncologia_Cutânea_(Câncer_de_Pele)(d3)`
  - escolhido: `Oncolo.pdf` (22,970,666b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/3. Hanseníase.pdf`
  - candidatos G:: `G:Dermatologia/Hanseníase(d2)`, `G:Dermatologia/Hanseníase(d3)`
  - escolhido: `Hansen.pdf` (19,498,427b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/4. Dermatoses Infecciosas.pdf`
  - candidatos G:: `G:Dermatologia/Dermatoses_Infecciosas(d2)`, `G:Dermatologia/Dermatoses_Infecciosas(d3)`
  - escolhido: `Dermat.pdf` (30,742,979b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/5. Dermatoses Eczematosas.pdf`
  - candidatos G:: `G:Dermatologia/Dermatoses_Eczematosas(d2)`, `G:Dermatologia/Dermatoses_Eczematosas(d3)`
  - escolhido: `Dermat.pdf` (19,152,995b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/6. Farmacodermias.pdf`
  - candidatos G:: `G:Dermatologia/Farmacodermias(d2)`, `G:Dermatologia/Farmacodermias(d3)`
  - escolhido: `Farmac.pdf` (17,707,843b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/7. Dermatoses Papuloescamosas.pdf`
  - candidatos G:: `G:Dermatologia/Dermatoses_Papuloescamosas(d2)`, `G:Dermatologia/Dermatoses_Papuloescamosas(d3)`
  - escolhido: `Dermat.pdf` (18,918,586b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Dermatologia/8. Dermatoses Vesicobolhosas.pdf`
  - candidatos G:: `G:Dermatologia/Dermatoses_Vesicobolhosas(d2)`, `G:Dermatologia/Dermatoses_Vesicobolhosas(d3)`
  - escolhido: `Dermat.pdf` (20,409,288b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/10. Metabolismo Ósseo e Mineral - Hipercalcemia.pdf`
  - candidatos G:: `G:Endocrinologia/Metabolismo_Ósseo_e_Mineral_-_Hipercalcemia(d2)`, `G:Endocrinologia/Metabolismo_Ósseo_e_Mineral_-_Hipercalcemia(d3)`
  - escolhido: `Metabo.pdf` (12,957,902b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/11. Metabolismo Ósseo e Mineral - Hipocalcemia.pdf`
  - candidatos G:: `G:Endocrinologia/Metabolismo_Ósseo_e_Mineral_-_Hipocalcemia(d2)`, `G:Endocrinologia/Metabolismo_Ósseo_e_Mineral_-_Hipocalcemia(d3)`
  - escolhido: `Metabo.pdf` (13,800,887b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/13. Metabolismo Ósseo e Mineral-Vitamina D e Osteomalácia.pdf`
  - candidatos G:: `G:Endocrinologia/Metabolismo_Ósseo_e_Mineral_-_Vitamina_D_e_Osteomalácia(d2)`, `G:Endocrinologia/Metabolismo_Ósseo_e_Mineral_-_Vitamina_D_e_Osteomalácia(d3)`
  - escolhido: `Metabolismo_Ósse.pdf` (12,955,570b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/16. Adrenal-Morfofisiologia Adrenal.pdf`
  - candidatos G:: `G:Endocrinologia/Adrenal_-_Morfofisiologia_Adrenal(d2)`, `G:Endocrinologia/Adrenal_-_Morfofisiologia_Adrenal(d3)`
  - escolhido: `Adrenal_-_Morfof.pdf` (14,724,503b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/17. Adrenal - Hipocortisolismo (Insuficiência Adrenal).pdf`
  - candidatos G:: `G:Endocrinologia/Adrenal-_Hipocortisolismo_(Insuficiência_Adrenal)(d2)`, `G:Endocrinologia/Adrenal-_Hipocortisolismo_(Insuficiência_Adrenal)(d3)`
  - escolhido: `Adrenal-_Hipocor.pdf` (14,998,861b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/18. Adrenal- Hipercortisolismo (Síndrome de Cushing).pdf`
  - candidatos G:: `G:Endocrinologia/Adrenal-_Hipercortisolismo_(Síndrome_de_Cushing)(d2)`, `G:Endocrinologia/Adrenal-_Hipercortisolismo_(Síndrome_de_Cushing)(d3)`
  - escolhido: `Adrenal-_Hiperco.pdf` (16,340,760b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/20. Hipófise - Fisiologia da Hipófise e Hipopituitarismo.pdf`
  - candidatos G:: `G:Endocrinologia/Hipófise_-_Fisiologia_da_Hipófise_e_Hipopituitarismo(d2)`, `G:Endocrinologia/Hipófise_-_Fisiologia_da_Hipófise_e_Hipopituitarismo(d3)`
  - escolhido: `Hipófi.pdf` (17,191,908b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/21. Hipófise-Acromegalia e Incidentaloma Hipofisário.pdf`
  - candidatos G:: `G:Endocrinologia/Hipófise_-_Acromegalia_e_Incidentaloma_Hipofisário(d2)`, `G:Endocrinologia/Hipófise_-_Acromegalia_e_Incidentaloma_Hipofisário(d3)`
  - escolhido: `Hipófise_-_Acrom.pdf` (16,695,803b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/22. Hipófise - Hiperprolactinemia.pdf`
  - candidatos G:: `G:Endocrinologia/Hipófise_-_Hiperprolactinemia(d2)`, `G:Endocrinologia/Hipófise_-_Hiperprolactinemia(d3)`
  - escolhido: `Hipófi.pdf` (16,282,358b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/23. Neoplasias Endócrinas Múltiplas.pdf`
  - candidatos G:: `G:Endocrinologia/Neoplasias_Endócrinas_Múltiplas(d2)`, `G:Endocrinologia/Neoplasias_Endócrinas_Múltiplas(d3)`
  - escolhido: `Neopla.pdf` (14,881,966b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/24. Hipoglicemia no Paciente não Diabético.pdf`
  - candidatos G:: `G:Endocrinologia/Hipoglicemia_no_Paciente_não_Diabético(d2)`, `G:Endocrinologia/Hipoglicemia_no_Paciente_não_Diabético(d3)`
  - escolhido: `Hipogl.pdf` (14,175,675b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/25. Incongruência de Gênero.pdf`
  - candidatos G:: `G:Endocrinologia/Incongruência_de_Gênero(d2)`, `G:Endocrinologia/Incongruência_de_Gênero(d3)`
  - escolhido: `Incong.pdf` (14,043,733b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/26. Tireoide - Hipotireoidismo.pdf`
  - candidatos G:: `G:Endocrinologia/Tireoide_-_Hipotireoidismo(d2)`, `G:Endocrinologia/Tireoide_-_Hipotireoidismo(d3)`
  - escolhido: `Tireoi.pdf` (13,407,882b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Endocrinologia/8. Obesidade - Obesidade e Síndrome Metabólica.pdf`
  - candidatos G:: `G:Endocrinologia/Obesidade_-_Obesidade_e_Síndrome_Metabólica(d2)`, `G:Endocrinologia/Obesidade_-_Obesidade_e_Síndrome_Metabólica(d3)`
  - escolhido: `Obesid.pdf` (16,983,040b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Gastroenterologia/1. Hemorragia Digestiva Alta Não Varicosa.pdf`
  - candidatos G:: `G:Gastroenterologia/Hemorragia_Digestiva_Alta_Não_Varicosa(d2)`, `G:Gastroenterologia/Hemorragia_Digestiva_Alta_Não_Varicosa(d3)`
  - escolhido: `Hemorragia_Diges.pdf` (24,289,636b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Gastroenterologia/3. Hemorragia Digestiva Baixa.pdf`
  - candidatos G:: `G:Gastroenterologia/Hemorragia_Digestiva_Baixa(d2)`, `G:Gastroenterologia/Hemorragia_Digestiva_Baixa(d3)`
  - escolhido: `Hemorragia_Diges.pdf` (24,589,898b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Gastroenterologia/5. Pancreatite Aguda e Crônica (Pancreatites).pdf`
  - candidatos G:: `G:Gastroenterologia/Pancreatite_Aguda_e_Crônica_(Pancreatites)(d2)`, `G:Gastroenterologia/Pancreatite_Aguda_e_Crônica_(Pancreatites)(d3)`
  - escolhido: `Pancreatite_Agud.pdf` (22,257,913b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Gastroenterologia/6. Hemorragia Digestiva Alta Varicosa.pdf`
  - candidatos G:: `G:Gastroenterologia/Hemorragia_Digestiva_Alta_Varicosa(d2)`, `G:Gastroenterologia/Hemorragia_Digestiva_Alta_Varicosa(d3)`
  - escolhido: `Hemorragia_Diges.pdf` (24,585,431b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Hematologia/1. Introdução ao Estudo das Anemias.pdf`
  - candidatos G:: `G:Hematologia/Introdução_ao_Estudo_das_Anemias(d2)`, `G:Hematologia/Introdução_ao_Estudo_das_Anemias(d3)`
  - escolhido: `Introd.pdf` (10,976,027b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Hematologia/3. Anemias Macrocíticas.pdf`
  - candidatos G:: `G:Hematologia/Anemias_Macrocíticas(d2)`, `G:Hematologia/Anemias_Macrocíticas(d3)`
  - escolhido: `Anemia.pdf` (16,653,121b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Hematologia/5. Anemia Associada a Condições Não Hematológicas.pdf`
  - candidatos G:: `G:Hematologia/Anemia_Associada_a_Condições_Não_Hematológicas(d2)`, `G:Hematologia/Anemia_Associada_a_Condições_Não_Hematológicas(d3)`
  - escolhido: `Anemia.pdf` (14,102,380b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Hematologia/8. Mieloma Múltiplo (Gamopatias Monoclonais).pdf`
  - candidatos G:: `G:Hematologia/Mieloma_Múltiplo_(Gamopatias_Monoclonais)(d2)`, `G:Hematologia/Mieloma_Múltiplo_(Gamopatias_Monoclonais)(d3)`
  - escolhido: `Mielom.pdf` (16,698,466b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/1. Lesão Renal Aguda (LRA).pdf`
  - candidatos G:: `G:Nefrologia/Lesão_Renal_Aguda_(LRA)(d2)`, `G:Nefrologia/Lesão_Renal_Aguda_(LRA)(d3)`
  - escolhido: `Lesão_Renal_Aguda.pdf` (27,942,764b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/2. Doença Renal Crônica (DRC) - Parte I.pdf`
  - candidatos G:: `G:Nefrologia/Doença_Renal_Crônica_(DRC)_-_Parte_I(d2)`, `G:Nefrologia/Doença_Renal_Crônica_(DRC)_-_Parte_I(d3)`
  - escolhido: `Doença_Crônica_R.pdf` (25,376,195b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/3. Doença Renal Crônica (DRC) - Parte II.pdf`
  - candidatos G:: `G:Nefrologia/Doença_Renal_Crônica_(DRC)_-_Parte_II(d2)`, `G:Nefrologia/Doença_Renal_Crônica_(DRC)_-_Parte_II(d3)`
  - escolhido: `Doença_Renal_Crô.pdf` (26,206,976b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/4. Doenças Glomerulares.pdf`
  - candidatos G:: `G:Nefrologia/Doenças_Glomerulares(d2)`, `G:Nefrologia/Doenças_Glomerulares(d3)`
  - escolhido: `Doenças_Glomerulares.pdf` (28,634,974b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/6. Túbulo Interstício Renal.pdf`
  - candidatos G:: `G:Nefrologia/Túbulo-Interstício_Renal(d2)`, `G:Nefrologia/Túbulo-Interstício_Renal(d3)`
  - escolhido: `Túbulo-Interstício_Renal.pdf` (27,004,483b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/8. Análise da Gasometria Arterial.pdf`
  - candidatos G:: `G:Nefrologia/Análise_da_Gasometria_Arterial(d2)`, `G:Nefrologia/Análise_da_Gasometria_Arterial(d3)`
  - escolhido: `Análise_da_Gasom.pdf` (24,445,926b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Nefrologia/9. Distúrbios do Sódio - Disnatremias.pdf`
  - candidatos G:: `G:Nefrologia/Distúrbios_do_Sódio_-_Disnatremias(d2)`, `G:Nefrologia/Distúrbios_do_Sódio_-_Disnatremias(d3)`
  - escolhido: `Distúr.pdf` (21,387,945b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Pneumologia/1. Derrame Pleural.pdf`
  - candidatos G:: `G:Pneumologia/Derrame_Pleural(d2)`, `G:Pneumologia/Derrame_Pleural(d3)`
  - escolhido: `Derrame_Pleural.pdf` (31,384,448b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Pneumologia/3. Tromboembolismo Pulmonar (TEP).pdf`
  - candidatos G:: `G:Pneumologia/Tromboembolismo_Pulmonar_(TEP)(d2)`, `G:Pneumologia/Tromboembolismo_Pulmonar_(TEP)(d3)`
  - escolhido: `Trombo.pdf` (32,124,339b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Pneumologia/4. Introdução à Pneumologia.pdf`
  - candidatos G:: `G:Pneumologia/Introdução_a_Pneumologia(d2)`, `G:Pneumologia/Introdução_a_Pneumologia(d3)`
  - escolhido: `Introdução_a_Pne.pdf` (32,819,891b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Clínica Médica/Pneumologia/8. Neoplasias Pulmonares.pdf`
  - candidatos G:: `G:Pneumologia/Neoplasias_Pulmonares(d2)`, `G:Pneumologia/Neoplasias_Pulmonares(d3)`
  - escolhido: `Neopla.pdf` (33,292,942b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/1. Ciclo Menstrual.pdf`
  - candidatos G:: `G:Ginecologia/Ciclo_Menstrual(d2)`, `G:Ginecologia/Ciclo_Menstrual(d3)`
  - escolhido: `Ciclo_.pdf` (25,033,306b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/10. Aloimunização Materna e Doença Hemolítica Perinatal.pdf`
  - candidatos G:: `G:Obstetrícia/Aloimunização_Materna_e_Doença_Hemolítica_Perinatal(d2)`, `G:Obstetrícia/Aloimunização_Materna_e_Doença_Hemolítica_Perinatal(d3)`
  - escolhido: `Aloimu.pdf` (19,437,538b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/10. Incontinência Urinária.pdf`
  - candidatos G:: `G:Ginecologia/Incontinência_Urinária(d2)`, `G:Ginecologia/Incontinência_Urinária(d3)`
  - escolhido: `Incontinência_Ur.pdf` (21,370,564b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/11. Câncer de Mama.pdf`
  - candidatos G:: `G:Ginecologia/Câncer_de_Mama(d2)`, `G:Ginecologia/Câncer_de_Mama(d3)`
  - escolhido: `Câncer_de_Mama.pdf` (22,456,459b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/12. Câncer do Corpo do Útero.pdf`
  - candidatos G:: `G:Ginecologia/Câncer_do_Corpo_do_Útero(d2)`, `G:Ginecologia/Câncer_do_Corpo_do_Útero(d3)`
  - escolhido: `Câncer.pdf` (21,403,308b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/12. Modificações Fisiológicas da Gestação.pdf`
  - candidatos G:: `G:Obstetrícia/Modificações_Fisiológicas_da_Gestação(d2)`, `G:Obstetrícia/Modificações_Fisiológicas_da_Gestação(d3)`
  - escolhido: `Modificações_Fis.pdf` (29,456,482b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/13. Tumores Anexiais e Câncer de Ovário.pdf`
  - candidatos G:: `G:Ginecologia/Tumores_Anexiais_e_Câncer_de_Ovário(d2)`, `G:Ginecologia/Tumores_Anexiais_e_Câncer_de_Ovário(d3)`
  - escolhido: `Tumores_Anexiais.pdf` (21,442,416b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/14. Doenças de Vulva e Vagina.pdf`
  - candidatos G:: `G:Ginecologia/Doenças_de_Vulva_e_Vagina(d2)`, `G:Ginecologia/Doenças_de_Vulva_e_Vagina(d3)`
  - escolhido: `Doenças__da_Vulv.pdf` (21,690,916b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/15. Vitalidade Fetal.pdf`
  - candidatos G:: `G:Obstetrícia/Vitalidade_Fetal(d2)`, `G:Obstetrícia/Vitalidade_Fetal(d3)`
  - escolhido: `Vitalidade_Fetal.pdf` (32,031,864b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/16. Cervicites.pdf`
  - candidatos G:: `G:Ginecologia/Cervicites(d2)`, `G:Ginecologia/Cervicites(d3)`
  - escolhido: `Cervicites.pdf` (22,952,211b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/17. Doença Inflamatória Pélvica (DIP).pdf`
  - candidatos G:: `G:Ginecologia/Doença_Inflamatória_Pélvica_(DIP)(d2)`, `G:Ginecologia/Doença_Inflamatória_Pélvica_(DIP)(d3)`
  - escolhido: `Doença_Inflamató.pdf` (23,198,965b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/17. Parto Vaginal Operatório.pdf`
  - candidatos G:: `G:Obstetrícia/Parto_Vaginal_Operatório(d2)`, `G:Obstetrícia/Parto_Vaginal_Operatório(d3)`
  - escolhido: `Parto .pdf` (20,927,996b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/19. Assistência à Vítima de Violência Sexual.pdf`
  - candidatos G:: `G:Ginecologia/Assistência_à_Vítima_de_Violência_Sexual(d2)`, `G:Ginecologia/Assistência_à_Vítima_de_Violência_Sexual(d3)`
  - escolhido: `Assistência_à_Ví.pdf` (22,169,321b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/19. Indução do Parto e Pós-Datismo.pdf`
  - candidatos G:: `G:Obstetrícia/Indução_do_Parto_e_Pós-Datismo(d2)`, `G:Obstetrícia/Indução_do_Parto_e_Pós-Datismo(d3)`
  - escolhido: `Induçã.pdf` (18,885,669b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/2. Rotura Prematura de Membranas (RPM).pdf`
  - candidatos G:: `G:Obstetrícia/Rotura_Prematura_de_Membranas_(RPM)(d2)`, `G:Obstetrícia/Rotura_Prematura_de_Membranas_(RPM)(d3)`
  - escolhido: `Rotura_Prematura.pdf` (24,048,020b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/20. Adenomiose.pdf`
  - candidatos G:: `G:Ginecologia/Adenomiose(d2)`, `G:Ginecologia/Adenomiose(d3)`
  - escolhido: `Adenom.pdf` (16,540,987b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/20. Restrição de Crescimento Fetal e Óbito Fetal.pdf`
  - candidatos G:: `G:Obstetrícia/Restrição_de_Crescimento_Fetal_e_Óbito_Fetal(d2)`, `G:Obstetrícia/Restrição_de_Crescimento_Fetal_e_Óbito_Fetal(d3)`
  - escolhido: `Restri.pdf` (19,908,439b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/21. Rastreamento do Câncer de Colo Uterino.pdf`
  - candidatos G:: `G:Ginecologia/Rastreamento_do_Câncer_de_Colo_Uterino(d2)`, `G:Ginecologia/Rastreamento_do_Câncer_de_Colo_Uterino(d3)`
  - escolhido: `Rastreamento_do_.pdf` (28,545,041b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/21. Ultrassom em Obstetrícia.pdf`
  - candidatos G:: `G:Obstetrícia/Ultrassom_em_Obstetrícia(d2)`, `G:Obstetrícia/Ultrassom_em_Obstetrícia(d3)`
  - escolhido: `Ultras.pdf` (29,263,484b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/22. Câncer de Colo Uterino.pdf`
  - candidatos G:: `G:Ginecologia/Câncer_de_Colo_Uterino(d2)`, `G:Ginecologia/Câncer_de_Colo_Uterino(d3)`
  - escolhido: `Câncer_de_Colo_U.pdf` (23,400,974b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/23. Climatério e Terapia Hormonal.pdf`
  - candidatos G:: `G:Ginecologia/Climatério_e_Terapia_Hormonal(d2)`, `G:Ginecologia/Climatério_e_Terapia_Hormonal(d3)`
  - escolhido: `Climatério_e_Ter.pdf` (23,001,739b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/23. Sangramento da Primeira Metade.pdf`
  - candidatos G:: `G:Obstetrícia/Sangramento_da_Primeira_Metade(d2)`, `G:Obstetrícia/Sangramento_da_Primeira_Metade(d3)`
  - escolhido: `Sangramento_da_P.pdf` (31,682,934b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/24. Miomatose Uterina.pdf`
  - candidatos G:: `G:Ginecologia/Miomatose_Uterina(d2)`, `G:Ginecologia/Miomatose_Uterina(d3)`
  - escolhido: `Miomatose_Uterina.pdf` (24,475,905b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/24. Sangramento da Segunda Metade.pdf`
  - candidatos G:: `G:Obstetrícia/Sangramento_da_Segunda_Metade(d2)`, `G:Obstetrícia/Sangramento_da_Segunda_Metade(d3)`
  - escolhido: `Sangra.pdf` (24,003,631b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/26. Anatomia e Embriologia do Trato Genital Feminino.pdf`
  - candidatos G:: `G:Ginecologia/Anatomia_e_Embriologia_do_Trato_Genital_Feminino(d2)`, `G:Ginecologia/Anatomia_e_Embriologia_do_Trato_Genital_Feminino(d3)`
  - escolhido: `Anatomia_e_Embri.pdf` (25,428,016b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/27. Infertilidade Conjugal.pdf`
  - candidatos G:: `G:Ginecologia/Infertilidade_Conjugal(d2)`, `G:Ginecologia/Infertilidade_Conjugal(d3)`
  - escolhido: `Infert.pdf` (17,696,061b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/28. Dor Pélvica Crônica e Dismenorreia.pdf`
  - candidatos G:: `G:Ginecologia/Dor_Pélvica_Crônica_e_Dismenorreia(d2)`, `G:Ginecologia/Dor_Pélvica_Crônica_e_Dismenorreia(d3)`
  - escolhido: `Dor_Pé.pdf` (22,574,097b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/29. Sexualidade.pdf`
  - candidatos G:: `G:Ginecologia/Sexualidade(d2)`, `G:Ginecologia/Sexualidade(d3)`
  - escolhido: `Sexual.pdf` (13,314,647b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/3. Amenorreia.pdf`
  - candidatos G:: `G:Ginecologia/Amenorreia(d2)`, `G:Ginecologia/Amenorreia(d3)`
  - escolhido: `Amenorreia.pdf` (24,651,420b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/30. Síndrome Pré-Menstrual.pdf`
  - candidatos G:: `G:Ginecologia/Síndrome_Pré-Menstrual(d2)`, `G:Ginecologia/Síndrome_Pré-Menstrual(d3)`
  - escolhido: `Síndro.pdf` (12,836,386b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/31. Abdome Agudo em Ginecologia.pdf`
  - candidatos G:: `G:Ginecologia/Abdome_Agudo_em_Ginecologia(d2)`, `G:Ginecologia/Abdome_Agudo_em_Ginecologia(d3)`
  - escolhido: `Abdome_Agudo_em_.pdf` (14,536,766b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/4. Gestação Múltipla.pdf`
  - candidatos G:: `G:Obstetrícia/Gestação_Múltipla(d2)`, `G:Obstetrícia/Gestação_Múltipla(d3)`
  - escolhido: `Gestação_Múltipla.pdf` (24,316,244b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/4. Síndrome dos Ovários Policísticos.pdf`
  - candidatos G:: `G:Ginecologia/Síndrome_dos_Ovários_Policísticos(d2)`, `G:Ginecologia/Síndrome_dos_Ovários_Policísticos(d3)`
  - escolhido: `Síndrome_dos_Ová.pdf` (25,860,254b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/6. Bacia Obstétrica, Pelvimetria e Estática Fetal.pdf`
  - candidatos G:: `G:Obstetrícia/Bacia_Obstétrica,_Pelvimetria_e_Estática_Fetal(d2)`, `G:Obstetrícia/Bacia_Obstétrica,_Pelvimetria_e_Estática_Fetal(d3)`
  - escolhido: `Bacia_.pdf` (26,364,771b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/6. Pólipos Uterinos.pdf`
  - candidatos G:: `G:Ginecologia/Pólipos_Uterinos(d2)`, `G:Ginecologia/Pólipos_Uterinos(d3)`
  - escolhido: `Pólipo.pdf` (12,117,278b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/7. Infecção Puerperal.pdf`
  - candidatos G:: `G:Obstetrícia/Infecção_Puerperal(d2)`, `G:Obstetrícia/Infecção_Puerperal(d3)`
  - escolhido: `Infecç.pdf` (16,200,968b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/7. Rastreamento do Câncer de Mama.pdf`
  - candidatos G:: `G:Ginecologia/Rastreamento_do_Câncer_de_Mama(d2)`, `G:Ginecologia/Rastreamento_do_Câncer_de_Mama(d3)`
  - escolhido: `Rastreamento_do_.pdf` (22,652,305b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/8. Sífilis na Gestação e Sífilis Congênitas.pdf`
  - candidatos G:: `G:Obstetrícia/Sífilis_na_Gestação_e_Sífilis_Congênitas(d2)`, `G:Pediatria/Sífilis_na_Gestação_e_Sífilis_Congênitas(d2)`, `G:Obstetrícia/Sífilis_na_Gestação_e_Sífilis_Congênitas(d3)`, `G:Pediatria/Sífilis_na_Gestação_e_Sífilis_Congênitas(d3)`
  - escolhido: `Sífili.pdf` (14,229,502b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/9. Doenças benignas da Mama.pdf`
  - candidatos G:: `G:Ginecologia/Doenças Benignas da Mama(d2)`, `G:Ginecologia/Doenças_Benignas_da_Mama(d3)`
  - escolhido: `Doenças_Benignas.pdf` (23,444,596b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/GO/9. Infecções Congênitas na Gestação.pdf`
  - candidatos G:: `G:Obstetrícia/Infecções_Congênitas_na_Gestação(d2)`, `G:Obstetrícia/Infecções_Congênitas_na_Gestação(d3)`
  - escolhido: `Infecções_Congênitas.pdf` (16,175,898b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/1. Puberdade.pdf`
  - candidatos G:: `G:Pediatria/Puberdade(d2)`, `G:Pediatria/Puberdade(d3)`
  - escolhido: `Puberd.pdf` (16,601,167b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/10. Hiperplasia Adrenal Congênita.pdf`
  - candidatos G:: `G:Pediatria/Hiperplasia_Adrenal_Congênita(d2)`, `G:Pediatria/Hiperplasia_Adrenal_Congênita(d3)`
  - escolhido: `Hiperplasia_Adre.pdf` (14,316,018b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/11. Distúrbios Respiratórios do Período Neonatal.pdf`
  - candidatos G:: `G:Pediatria/Distúrbios_Respiratórios_do_Período_Neonatal(d2)`, `G:Pediatria/Distúrbios_Respiratórios_do_Período_Neonatal(d3)`
  - escolhido: `Distúr.pdf` (15,687,143b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/14. Enurese Noturna.pdf`
  - candidatos G:: `G:Pediatria/Enurese_Noturna(d2)`, `G:Pediatria/Enurese_Noturna(d3)`
  - escolhido: `Enures.pdf` (12,173,276b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/15. Pneumonias na Infância.pdf`
  - candidatos G:: `G:Pediatria/Pneumonias_na_Infância(d2)`, `G:Pediatria/Pneumonias_na_Infância(d3)`
  - escolhido: `Pneumo.pdf` (15,371,302b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/16. Hipotireoidismo Congênito.pdf`
  - candidatos G:: `G:Pediatria/Hipotireoidismo_Congênito(d2)`, `G:Pediatria/Hipotireoidismo_Congênito(d3)`
  - escolhido: `Hipoti.pdf` (10,801,744b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/18. Aleitamento Materno.pdf`
  - candidatos G:: `G:Pediatria/Aleitamento_Materno(d2)`, `G:Pediatria/Aleitamento_Materno(d3)`
  - escolhido: `Aleita.pdf` (12,636,864b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/19. Desnutrição na Infância.pdf`
  - candidatos G:: `G:Pediatria/Desnutrição_na_Infância(d2)`, `G:Pediatria/Desnutrição_na_Infância(d3)`
  - escolhido: `Desnut.pdf` (13,703,890b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/20. Infecções Congênitas.pdf`
  - candidatos G:: `G:Pediatria/Infecções_Congênitas(d2)`, `G:Pediatria/Infecções_Congênitas(d3)`
  - escolhido: `Infecções_Congênitas.pdf` (16,175,898b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/23. Doença Celíaca em Pediatria.pdf`
  - candidatos G:: `G:Pediatria/Doença_Celíaca_em_Pediatria(d2)`, `G:Pediatria/Doença_Celíaca_em_Pediatria(d3)`
  - escolhido: `Doença.pdf` (15,525,429b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/24. Desenvolvimento Neuropsicomotor (DNPM).pdf`
  - candidatos G:: `G:Pediatria/Desenvolvimento_Neuropsicomotor_(DNPM)(d2)`, `G:Pediatria/Desenvolvimento_Neuropsicomotor_(DNPM)(d3)`
  - escolhido: `Desenv.pdf` (25,412,424b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/26. Choque em Pediatria.pdf`
  - candidatos G:: `G:Pediatria/Choque_em_Pediatria(d2)`, `G:Pediatria/Choque_em_Pediatria(d3)`
  - escolhido: `Choque.pdf` (14,421,214b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/31. Fibrose Cística.pdf`
  - candidatos G:: `G:Pediatria/Fibrose_Cística(d2)`, `G:Pediatria/Fibrose_Cística(d3)`
  - escolhido: `Fibros.pdf` (15,052,199b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/33. Tuberculose na Infância.pdf`
  - candidatos G:: `G:Pediatria/Tuberculose_na_Infância(d2)`, `G:Pediatria/Tuberculose_na_Infância(d3)`
  - escolhido: `Tuberc.pdf` (21,801,561b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/34. Doença de Kawasaki.pdf`
  - candidatos G:: `G:Pediatria/Doença_de_Kawasaki(d2)`, `G:Pediatria/Doença_de_Kawasaki(d3)`
  - escolhido: `Doença.pdf` (14,885,994b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/35. Bronquiolite.pdf`
  - candidatos G:: `G:Pediatria/Bronquiolite(d2)`, `G:Pediatria/Bronquiolite(d3)`
  - escolhido: `Bronqu.pdf` (13,683,929b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/36. Hipertensão Arterial na Criança e Adolescente.pdf`
  - candidatos G:: `G:Pediatria/Hipertensão_Arterial_na_Criança_e_Adolescente(d2)`, `G:Pediatria/Hipertensão_Arterial_na_Criança_e_Adolescente(d3)`
  - escolhido: `Hipert.pdf` (14,511,168b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/39. Febre na Pediatria.pdf`
  - candidatos G:: `G:Pediatria/Febre_na_Pediatria(d2)`, `G:Pediatria/Febre_na_Pediatria(d3)`
  - escolhido: `Febre .pdf` (13,561,013b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/4. Alergia Alimentar.pdf`
  - candidatos G:: `G:Pediatria/Alergia_Alimentar(d2)`, `G:Pediatria/Alergia_Alimentar(d3)`
  - escolhido: `Alergi.pdf` (12,320,543b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/40. Artrite Idiopática Juvenil (AIJ).pdf`
  - candidatos G:: `G:Pediatria/Artrite_Idiopática_Juvenil_(AIJ)(d2)`, `G:Pediatria/Artrite_Idiopática_Juvenil_(AIJ)(d3)`
  - escolhido: `Artrit.pdf` (15,357,293b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/41. Cefaleias na infância.pdf`
  - candidatos G:: `G:Pediatria/Cefaleias_na_Infância(d2)`, `G:Pediatria/Cefaleias_na_Infância(d3)`
  - escolhido: `Cefale.pdf` (12,293,792b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/42. Segurança em Pediatria.pdf`
  - candidatos G:: `G:Pediatria/Segurança_em_Pediatria(d2)`, `G:Pediatria/Segurança_em_Pediatria(d3)`
  - escolhido: `Segura.pdf` (14,889,468b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/43. Diagnóstico Nutricional.pdf`
  - candidatos G:: `G:Pediatria/Diagnóstico_Nutricional(d2)`, `G:Pediatria/Diagnóstico_Nutricional(d3)`
  - escolhido: `Diagnó.pdf` (15,098,496b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/44. Tópicos em Pediatria.pdf`
  - candidatos G:: `G:Pediatria/Tópicos_em_Pediatria(d2)`, `G:Pediatria/Tópicos_em_Pediatria(d3)`
  - escolhido: `Tópico.pdf` (13,132,365b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/45. Coqueluche.pdf`
  - candidatos G:: `G:Pediatria/Coqueluche(d2)`, `G:Pediatria/Coqueluche(d3)`
  - escolhido: `Coquel.pdf` (17,306,717b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/47. Doença do Refluxo Gastroesofágico em Pediatria.pdf`
  - candidatos G:: `G:Pediatria/Doença_do_Refluxo_Gastroesofágico_em_Pediatria(d2)`, `G:Pediatria/Doença_do_Refluxo_Gastroesofágico_em_Pediatria(d3)`
  - escolhido: `Doença.pdf` (12,514,797b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/48. Diarreia.pdf`
  - candidatos G:: `G:Pediatria/Diarreia(d2)`, `G:Pediatria/Diarreia(d3)`
  - escolhido: `Diarre.pdf` (14,756,751b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/5. Obesidade Infantil e na Adolescência.pdf`
  - candidatos G:: `G:Pediatria/Obesidade_Infantil_e_na_Adolescência(d2)`, `G:Pediatria/Obesidade_Infantil_e_na_Adolescência(d3)`
  - escolhido: `Obesid.pdf` (13,843,854b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/7. Anafilaxia e Urticária.pdf`
  - candidatos G:: `G:Pediatria/Anafilaxia_e_Urticária(d2)`, `G:Pediatria/Anafilaxia_e_Urticária(d3)`
  - escolhido: `Anafilaxia_e_Urticária.pdf` (17,292,209b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Pediatria/9. Constipação Intestinal.pdf`
  - candidatos G:: `G:Pediatria/Constipação_Intestinal(d2)`, `G:Pediatria/Constipação_Intestinal(d3)`
  - escolhido: `Constipação_Inte.pdf` (13,904,078b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Preventiva/13. Testes Diagnósticos.pdf`
  - candidatos G:: `G:Preventiva/Testes_Diagnósticos(d2)`, `G:Preventiva/Testes_Diagnósticos(d3)`
  - escolhido: `Testes.pdf` (9,045,957b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Preventiva/15. Processos de Descentralização e Regionalização do SUS.pdf`
  - candidatos G:: `G:Preventiva/Processos_de_Descentralização_e_Regionalização_do_SUS(d2)`, `G:Preventiva/Processos_de_Descentralização_e_Regionalização_do_SUS(d3)`
  - escolhido: `Proces.pdf` (2,345,466b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Preventiva/18. Financiamento em Saúde.pdf`
  - candidatos G:: `G:Preventiva/Financiamento_em_Saúde(d2)`, `G:Preventiva/Financiamento_em_Saúde(d3)`
  - escolhido: `Resumo.pdf` (6,932,572b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Preventiva/21. Pesquisa Epidemiológica e Medidas de Associação.pdf`
  - candidatos G:: `G:Preventiva/Pesquisa_Epidemiológica_e_Medidas_de_Associação(d2)`, `G:Preventiva/Pesquisa_Epidemiológica_e_Medidas_de_Associação(d3)`
  - escolhido: `Resumo.pdf` (29,541,308b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.
- `resumos/Preventiva/4. Marcos Legais do Sistema Único de Saúde.pdf`
  - candidatos G:: `G:Preventiva/Marcos_legais_do_Sistema_Único_de_Saúde(d2)`, `G:Preventiva/Marcos_legais_do_Sistema_Único_de_Saúde(d3)`
  - escolhido: `Marcos_legais_do_SUS.pdf` (17,320,173b). As pastas irmas sao duplicatas do Drive do **mesmo tema** (mesmos videos, mesmo material); venceu a de maior PDF elegivel.

## 7. Execucao e verificacao pos-copia

- `shutil.copy2` executado em **180/180** destinos. Falhas: **0**.
- Verificacao arquivo a arquivo: **180/180** destinos existem, com `bytes > 0` **e** `tamanho == tamanho da origem`.
- Divergencias: **0**.
- Nenhuma escrita, movimentacao ou delecao em `G:` ou `D:`.

## 8. Licao registrada

A delecao de ontem foi possivel porque a operacao em massa nao tinha conjunto-alvo declarado nem conferencia de cardinalidade. Nesta restauracao, toda etapa calculou o alvo, **assertou o tamanho esperado antes de executar** e abortaria com relatorio se divergisse; a copia rodou depois de um dry-run com tabela auditavel das 180 linhas. Mesma disciplina agora vive no codigo: `tools/backup_db.py` purga com COUNT-ASSERT e tem `dry_run`.
