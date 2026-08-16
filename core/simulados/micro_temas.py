# -*- coding: utf-8 -*-
"""Peso MICRO: quanto o tema pesa DENTRO da sua especialidade, pelo Guia Estatistico.

Escala (ancorada no guia, nao em opiniao):
  3.0 = topo do TOP-10 do guia E/OU subarea dominante da especialidade
  2.5 = alto no TOP-10 ou subarea dominante
  2.0 = presente no TOP-10, subarea de peso medio
  1.5 = presente no TOP-10 em posicao baixa, ou subarea relevante fora da lista
  1.0 = subarea menor, fora do TOP-10
  0.5 = nao aparece no guia, nem como subarea nem como assunto
Cada linha traz a justificativa (posicao no TOP-10 / % da subarea).
"""

MICRO = {
 # ---- CIRURGIA (top10: 1 anestesio, 2 apendicite, 3 cir.infantil III, 4 cicatrizacao,
 #      5 temas gerais, 6 vesicula, 7 diverticulite, 8 bariatrica, 9 AA obstrutivo, 10 hernias)
 ("Cirurgia", "Princípios da Anestesiologia"): (3.0, "TOP-10 #1; subárea própria 6%"),
 ("Cirurgia", "Diverticulite Aguda"): (2.0, "TOP-10 #7; urgências abdominais 10%"),
 ("Cirurgia", "Abdome Agudo Obstrutivo"): (2.0, "TOP-10 #9; urgências abdominais 10%"),
 ("Cirurgia", "Hérnias da Parede Abdominal"): (1.5, "TOP-10 #10 (última posição)"),
 ("Cirurgia", "Complicações Pós-Operatórias"): (1.5, "encosta em 'temas gerais' (#5); sem subárea própria"),
 ("Cirurgia", "Cirurgia Vascular"): (0.5, "ausente do guia: nem subárea nem TOP-10"),
 ("Cirurgia", "Urologia"): (0.5, "ausente do guia: nem subárea nem TOP-10"),

 # ---- ORTOPEDIA (top: 1 maus tratos, 2 quadril ped., 3 onco/osteomielite,
 #      4 conceitos trauma, 5 fratura exposta)
 ("Ortopedia", "Fraturas e Luxações; Complicações do Trauma Ortopédico"): (2.5, "TOP #4/#5; trauma ortopédico 25%"),
 ("Ortopedia", "Quadril Pediátrico Politrauma Ortopédico Doenças da coluna vertebral Maus Tratos Fraturas e Luxações Complicações do trauma ortopédico"): (3.0, "cobre TOP #1, #2 e #4 num bloco só"),

 # ---- GINECOLOGIA (top10: 1 vulvovaginites, 2 rastreio CA colo, 3 planej. familiar,
 #      4 rastreio CA mama, 5 úlceras genitais, 6 amenorreia, 7 tumores anexiais,
 #      8 CA corpo útero, 9 climatério, 10 DIP)
 ("Ginecologia", "Câncer de Colo Uterino"): (3.0, "TOP-10 #2; oncologia ginecológica 22,45%"),
 ("Ginecologia", "Câncer de Mama"): (3.0, "TOP-10 #4; mastologia 20,41%"),
 ("Ginecologia", "Tumores Anexiais e Câncer de Ovário"): (2.5, "TOP-10 #7; oncologia ginecológica 22,45%"),
 ("Ginecologia", "Sangramento Uterino Anormal"): (2.5, "ginecologia endócrina 26,53% (maior subárea); vizinho do #8"),
 ("Ginecologia", "Prolapsos de Órgãos Pélvicos"): (1.0, "ginecologia geral 6,12%; fora do TOP-10"),
 ("Ginecologia", "Incontinência Urinária"): (1.0, "ginecologia geral 6,12%; fora do TOP-10"),
 ("Ginecologia", "Assistência à Vítima de Violência Sexual"): (0.5, "ausente do guia"),

 # ---- OBSTETRICIA (top10: 1 pré-natal, 2 DHEG, 3 sangramento 1a metade, 4 indução/pós-datismo,
 #      5 assistência ao parto, 6 HPP, 7 sangramento 2a metade, 8 sífilis, 9 DMG, 10 inf. congênitas)
 ("Obstetrícia", "Hemorragia Pós-Parto"): (3.0, "TOP-10 #6; intercorrências obstétricas 27,91% (maior subárea)"),
 ("Obstetrícia", "Sangramento da Segunda Metade"): (2.5, "TOP-10 #7; intercorrências obstétricas 27,91%"),
 ("Obstetrícia", "Assistência ao Parto"): (2.5, "TOP-10 #5; parto 13,95%"),
 ("Obstetrícia", "Partograma e Distocia"): (2.0, "parto 13,95%; vizinho do #4 (indução/distocia)"),
 ("Obstetrícia", "Diabetes na Gestação"): (2.0, "TOP-10 #9; doenças associadas à gestação 16,28%"),
 ("Obstetrícia", "Vitalidade Fetal"): (1.5, "medicina fetal 18,60%; fora do TOP-10"),
 ("Obstetrícia", "Gestação Múltipla"): (1.5, "intercorrências 27,91%; fora do TOP-10"),

 # ---- PEDIATRIA (top10: 1 imunizações, 2 cardiopatias congênitas, 3 pneumonias, 4 aleitamento,
 #      5 diarreia, 6 crescimento, 7 infecções congênitas, 8 bronquiolite, 9 emergências, 10 tópicos)
 ("Pediatria", "Aleitamento Materno"): (3.0, "TOP-10 #4; puericultura 27,59% (maior subárea)"),
 ("Pediatria", "Pneumonias na Infância"): (3.0, "TOP-10 #3; pneumologia pediátrica 10,34%"),
 ("Pediatria", "Crescimento"): (2.5, "TOP-10 #6; puericultura 27,59%"),
 ("Pediatria", "Diarreia"): (2.5, "TOP-10 #5; gastrologia pediátrica 8,62%"),
 ("Pediatria", "Choque em Pediatria"): (2.0, "TOP-10 #9 (emergências pediátricas)"),
 ("Pediatria", "Reanimação Neonatal"): (2.0, "neonatologia 12,07% (2a maior subárea); fora do TOP-10"),
 ("Pediatria", "Tópicos em Pediatria"): (1.5, "TOP-10 #10 (última posição)"),
 ("Pediatria", "Asma"): (1.5, "pneumologia pediátrica 10,34%; fora do TOP-10 (bronquiolite é #8)"),
 ("Pediatria", "Desnutrição na Infância"): (1.5, "puericultura 27,59%; fora do TOP-10"),
 ("Pediatria", "Alergia Alimentar"): (0.5, "ausente do guia"),
 ("Pediatria", "Obesidade Infantil e na Adolescência"): (0.5, "ausente do guia"),

 # ---- PREVENTIVA (top10: 1 ética, 2 MFC, 3 processo saúde-doença, 4 testes diagnósticos,
 #      5 APS, 6 medidas de saúde coletiva II, 7 sistemas de informação,
 #      8 pesquisa epidemiológica, 9 saúde do idoso, 10 bases saúde do trabalhador)
 ("Preventiva", "Estatística Médica"): (3.0, "epidemiologia 41,67% (maior subárea do guia inteiro); TOP-10 #4 e #8"),
 ("Preventiva", "Ética Médica"): (3.0, "TOP-10 #1; subárea própria 11,11%"),
 ("Preventiva", "Atenção Primária à Saúde no Brasil"): (3.0, "TOP-10 #5; MFC 22,22%"),
 ("Preventiva", "Princípios e Diretrizes do SUS"): (2.0, "SUS 19,44%; fora do TOP-10"),
 ("Preventiva", "Financiamento em Saúde"): (1.5, "SUS 19,44%; fora do TOP-10"),
 ("Preventiva", "Normas Regulamentadoras"): (1.0, "saúde do trabalhador 5,56%; TOP-10 #10"),

 # ---- NEFROLOGIA (top: 1 ácido-base/gasometria, 2 ITU, 3 glomerulares, 4 LRA, 5-6 DRC,
 #      7 nefrolitíase, 8 disnatremias)
 ("Nefrologia", "Distúrbios Ácido-Base; Distúrbios do Potássio"): (3.0, "TOP #1; DHE 14,29%"),
 ("Nefrologia", "Infecção do Trato Urinário"): (3.0, "TOP #2; ITU 21,43% (maior subárea)"),
 ("Nefrologia", "Doenças Glomerulares"): (2.5, "TOP #3; glomerulopatias 14,29%"),
 ("Nefrologia", "Doenças Glomerulares Infecção do Trato Urinário"): (2.5, "revisão que cobre TOP #2 e #3"),
 ("Nefrologia", "Nefrolitíase"): (1.0, "TOP #7; não figura entre as subáreas"),

 # ---- HEMATO (top: 1 leucemias crônicas/linfomas, 2 med. transfusional, 3 anemias microcíticas,
 #      4 macrocíticas, 5 mieloproliferações, 6 hemolíticas, 7 leucemias agudas)
 ("Hemato", "Anemias Microcíticas e Leucemias Agudas"): (2.5, "TOP #3 e #7 num bloco só"),
 ("Hemato", "Anemias Hemolíticas"): (2.0, "TOP #6; hemoglobinopatias 26,67% (maior subárea)"),

 # ---- PSIQUIATRIA (top: 1 dependência química, 2 intoxicações, 3 psiq. infantil,
 #      4 transtornos alimentares, 5 psicofarmacologia)
 ("Psiquiatria", "Psicofarmacologia (Teoria) Psiquiatria Infantil"): (2.5, "TOP #3 e #5; psiq. infantil 30%"),
 ("Psiquiatria", "Transtornos de Humor; Psiquiatria Social e Reforma Psiquiátrica"): (0.5, "ausente do guia"),

 # ---- REUMATO (top: 1 AR, 2 microcristalinas, 3 vasculites, 4 tec. conjuntivo II,
 #      5 espondiloartrite, 6 miopatias)
 ("Reumato", "Artrite Reumatóide"): (3.0, "TOP #1; artropatias inflamatórias 55,56%"),
 ("Reumato", "Vasculites"): (2.5, "TOP #3; vasculites 22,22%"),
 ("Reumato", "Doenças Inflamatórias do Tecido Conjuntivo"): (2.0, "TOP #4; tec. conjuntivo 22,22%"),

 # ---- PNEUMO (top: 1 asma, 2 neoplasias, 3 DPOC, 4 derrame pleural, 5 intersticiais)
 ("Pneumo", "Neoplasias Pulmonares"): (3.0, "TOP #2; câncer de pulmão 33,33% (maior subárea)"),
 ("Pneumo", "Doença Pulmonar Obstrutiva Crônica"): (2.0, "TOP #3; DPOC 11,11%"),
 ("Pneumo", "Derrame Pleural"): (2.0, "TOP #4; derrame pleural 11,11%"),
 ("Pneumo", "Pneumologia Intensiva"): (0.5, "ausente do guia"),

 # ---- HEPATO (top: 1 tumores, 2 cirrose, 3 hepatites virais, 4 complicações da cirrose)
 ("Hepato", "Complicações da Cirrose Hepática"): (2.5, "TOP #4; complicações da insuf. hepática 22,22%"),

 # ---- DERMATO / OTORRINO / OFTALMO
 ("Dermato", "Oncologia Cutânea"): (3.0, "TOP #1; câncer de pele 14,29%"),
 ("Otorrino", "Infecções das Vias Aéreas Superiores Pt. 2"): (3.0, "TOP #2; IVAS 66,67% da especialidade"),
 ("Oftalmo", "Doenças do Polo Posterior"): (0.5, "ausente: o guia só lista tumores oculares e córnea/cristalino"),

 # ---- CARDIOLOGIA (subáreas: arritmias 32,14 / HAS 25,00 / IC 17,86 / aterosclerose-DAC 10,71 /
 #      aórticas 3,57; top10: 1 HAS pt2, 2 FA/flutter, 3 IAMCSST, 4 HAS pt3, 5 taquiarritmias,
 #      6 PCR, 7 IC pt2, 8 valvopatias, 9 dislipidemia, 10 SCASSST)
 ("Cardiologia", "Fibrilação e Flutter Atrial Parada Cardiorrespiratória"): (3.0, "TOP-10 #2 e #6; arritmias 32,14% (maior subárea)"),
 ("Cardiologia", "Hipertensão Arterial Sistêmica Pt. 3"): (3.0, "TOP-10 #4 (e #1 é HAS Pt.2); HAS 25,00%"),
 ("Cardiologia", "Valvopatias"): (1.5, "TOP-10 #8; não figura entre as subáreas"),

 # ---- GASTRO (subáreas: neoplasias do sist. digestivo 39,13 / esôfago 17,39 /
 #      hemorragia digestiva 13,04 / intestinos 13,04 / pâncreas 8,70;
 #      top10 inclui: pólipos e neoplasias intestinais, neoplasias de estômago e esôfago,
 #      DUP/H.pylori, DRGE, pancreatite, DII, neoplasias pancreáticas, anatomia intestino/SII,
 #      disfagia, HDA varicosa)
 ("Gastro", "Neoplasias de Estômago e Esôfago"): (3.0, "TOP-10 #2; neoplasias do sist. digestivo 39,13% (maior subárea)"),
 ("Gastro", "Doença Inflamatória Intestinal"): (2.0, "no TOP-10; intestinos 13,04%"),
 ("Gastro", "Anatomia do Intestino e Síndrome do Intestino Irritável"): (1.5, "no TOP-10 em posição baixa; intestinos 13,04%"),
 ("Gastro", "Disfagia, Alterações Estruturais e Dist. Mort."): (1.5, "no TOP-10 em posição baixa; esôfago 17,39%"),

 # ---- ENDOCRINO (subáreas: tireoide 33,33 / diabetes 28,57 / obesidade-SM 19,05 /
 #      metab. ósseo 9,52 / adrenal ~4,76; top9: 1 DM compl. agudas, 2 DM2, 3 introdução DM,
 #      4 hipotireoidismo, 5 cir. bariátrica, 6 obesidade-SM, 7 tireotoxicose, 8 osteoporose,
 #      9 hiperprolactinemia)
 ("Endocrino", "Hipotireoidismo"): (3.0, "TOP-9 #4; tireoide 33,33% (maior subárea)"),
 ("Endocrino", "Tireotoxicose"): (2.5, "TOP-9 #7; tireoide 33,33%"),
 ("Endocrino", "Obesidade e Síndrome Metabólica (Teoria) Cirurgia Bariátrica e Metabólica"): (3.0, "TOP-9 #5 e #6; obesidade/SM 28,57% (2a maior subárea)"),
 ("Endocrino", "Osteoporose e Doença óssea de Paget"): (2.0, "TOP-9 #8; metabolismo ósseo 9,52%"),

 # ---- INFECTO (subáreas: microbiologia/antimicrobianos 20,00 / HIV-AIDS 15,00 /
 #      pneumonia 10,00 / IST 10,00 / arboviroses 10,00; top10: 1 infecção hospitalar,
 #      2 antibióticos, 3 arboviroses, 4 pneumonias bacterianas, 5 HIV, 6 parasitoses,
 #      7 animais peçonhentos, 8 sepse, 9 endocardite, 10 covid)
 ("Infecto", "Parasitoses; Infecção Hospitalar"): (2.5, "TOP-10 #1 e #6 num bloco só"),
 ("Infecto", "Parasitoses; Infecções Relacionadas à Assistência em Saúde"): (2.5, "TOP-10 #1 e #6 num bloco só"),
 ("Infecto", "Pneumonias Bacterianas"): (2.5, "TOP-10 #4; pneumonia 10,00%"),
 ("Infecto", "Animais Peçonhentos"): (2.0, "TOP-10 #7"),
 ("Infecto", "Endocardites"): (1.5, "TOP-10 #9; sem subárea própria"),
 ("Infecto", "Endocardite Bacteriana - Endocardite Infecciosa"): (1.5, "TOP-10 #9; sem subárea própria"),

 # ---- NEUROLOGIA (subáreas: AVC 18,75 / TCE 18,75 / cefaleias 12,50 /
 #      neuromusculares 6,25 / epilepsias 6,25; top10: 1 AVC, 2 TCE, 3 epilepsias,
 #      4 cefaleias, 5 distúrbios do movimento, 6 anatomia/semiologia, 7 demências,
 #      8 neuromusculares, 9 distúrbios do sono, 10 desmielinizantes)
 ("Neurologia", "Acidentes Vasculares Cerebrais"): (3.0, "TOP-10 #1; AVC 18,75% (maior subárea, empatada com TCE)"),
 ("Neurologia", "AVC Coma e alterações da consciência"): (2.5, "revisão que cobre o TOP-10 #1"),
 ("Neurologia", "Doenças Neuromusculares"): (1.5, "TOP-10 #8; neuromusculares 6,25%"),
 ("Neurologia", "Distúrbios do Movimento"): (1.5, "TOP-10 #5; não figura entre as subáreas"),
 ("Neurologia", "Coma e alterações da consciência"): (1.5, "fora do TOP-10; encosta em anatomia/semiologia (#6)"),
}

PENDENTES = []
