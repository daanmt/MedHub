# Reserva da Fase 1 -- linhas pendentes FORA da fila

> Gerado por `python tools/plano.py --reserva` em 2026-09-19. Nao editar: regenerar. Para o operador ler UMA vez (fatia 2 do `/ai-eng`, s189): o gate e o olho, nao o aviso. Terminal datado: 02/11/2026, junto do F111.

**174 linha(s) pendente(s) sem semana** -- 46 fora da trilha, 128 reserva do extensivo. **22 em faixa ALTA** da UERJ (tema com >= 4 questoes em 2021-2026), das quais **13 sem NENHUMA linha na fila da Fase 1 cobrindo o tema** (o risco real: as outras tem o tema agendado por outra tarefa, coluna `tema ja na fila por`); 48 sem tema casado na prevalencia.

Como ler: `UERJ n (peso)` = questoes das provas UERJ 2021-2026 nos temas que a tarefa cobre (2021-2022 valem 0,7 no peso). `fora da trilha` = a trilha da Fase 1 nao a escolheu (`fase1_exclusiva`); `reserva do extensivo` = S1-S20 do extensivo, fora do plano por regra da part-2. `estado (18/09)` = como o gerador da trilha via o tema (ZERO nunca estudado, TOCADO, PARCIAL, FEITO) -- e o porque da exclusao: a prioridade e peso UERJ x lacuna. Para trazer uma linha para a Fase 1: entrada em `core/cronograma/trilha/custom.json` (com `racional`) + `python tools/trilha.py --gravar` + `python tools/plano.py --semear --dry-run`.

## 🔴 Faixa ALTA sem nenhuma linha na fila -- conferir primeiro

| id | grupo | area | tarefa | tipo | q | UERJ n (peso) | faixa | tema(s) UERJ | tema ja na fila por | estado (18/09) |
|---|---|---|---|---|---|---|---|---|---|---|
| #325 | reserva do extensivo | Obstetrícia | Pré-Natal \| Distúrbios Hipertensivos da Gestação \| Sífilis na Gestação e Sífilis Congênita \| Sangramento da Primeira Metade | Revisão por Questões | 56 | 14 (13.4) | alta | Distúrbios Hipertensivos da Gestação; Sangramento da Primeira Metade; Pré-Natal; Sífilis na Gestação e Sífilis Congênita | NENHUMA | FEITO/PARCIAL |
| #354 | reserva do extensivo | Pediatria | Cardiopatias Congênitas \| Cuidados Neonatais \| Asma \| Aleitamento Materno | Revisão por Questões | 43 | 10 (9.4) | alta | Aleitamento Materno; Cuidados Neonatais; Cardiopatias Congênitas | NENHUMA | FEITO |
| #393 | reserva do extensivo | Cirurgia | Apendicite Aguda \| Colecistite e Colangite Aguda \| Diverticulite Aguda | Revisão por Questões | 52 | 8 (7.4) | alta | Abdome Agudo Inflamatório - Colecistite e Colangite Aguda; Abdome Agudo Inflamatório - Apendicite Aguda | NENHUMA | PARCIAL |
| #22 | fora da trilha | Obstetrícia | Pré-Natal; Assistência ao Parto; Vitalidade Fetal | Revisão por Questões | 36 | 8 (7.1) | alta | Assistência ao Parto; Pré-Natal; Vitalidade Fetal | NENHUMA | PARCIAL/TOCADO |
| #349 | reserva do extensivo | Gastro | Doença do Refluxo Gastroesofágico, Esofagites Não-Pépticas e Ingestão de Corpo Estranho | Teoria I | 0 | 6 (5.7) | alta | Doença do Refluxo Gastroesofágico, Esofagites e Corpo Estranho | NENHUMA | PARCIAL |
| #377 | reserva do extensivo | Gastro | Doença do Refluxo Gastroesofágico, Esofagites Não-Pépticas e Ingestão de Corpo Estranho | Teoria II | 0 | 6 (5.7) | alta | Doença do Refluxo Gastroesofágico, Esofagites e Corpo Estranho | NENHUMA | PARCIAL |
| #180 | reserva do extensivo | Infecto | Arboviroses | Teoria III | 0 | 5 (5.0) | alta | Arboviroses | NENHUMA | PARCIAL |
| #358 | reserva do extensivo | Ginecologia | Endometriose | Teoria II | 0 | 5 (4.4) | alta | Endometriose | NENHUMA | PARCIAL |
| #370 | reserva do extensivo | Cirurgia | Abdome Agudo Inflamatório - Colecistite e Colangite Aguda | Teoria II | 0 | 5 (4.4) | alta | Abdome Agudo Inflamatório - Colecistite e Colangite Aguda | NENHUMA | PARCIAL |
| #293 | reserva do extensivo | Gastro | Pancreatite Aguda e Crônica | Teoria III | 0 | 4 (4.0) | alta | Pancreatite Aguda e Crônica | NENHUMA | PARCIAL |
| #320 | reserva do extensivo | Gastro | Pancreatite Aguda e Crônica | Revisão | 42 | 4 (4.0) | alta | Pancreatite Aguda e Crônica | NENHUMA | PARCIAL |
| #345 | reserva do extensivo | Obstetrícia | Assistência ao Parto | Teoria II | 0 | 4 (3.4) | alta | Assistência ao Parto | NENHUMA | PARCIAL |
| #359 | reserva do extensivo | Obstetrícia | Assistência ao Parto | Teoria III | 0 | 4 (3.4) | alta | Assistência ao Parto | NENHUMA | PARCIAL |

## ⚠️ Faixa ALTA com o tema ja na fila por outra tarefa

| id | grupo | area | tarefa | tipo | q | UERJ n (peso) | faixa | tema(s) UERJ | tema ja na fila por | estado (18/09) |
|---|---|---|---|---|---|---|---|---|---|---|
| #380 | reserva do extensivo | Infecto | Arboviroses \| HIV \| Tuberculose \| Meningites e Meningoencefalites | Revisão por Questões | 55 | 28 (26.8) | alta | Tuberculose; Meningites e Meningoencefalites; Arboviroses; HIV | #1797 (S2), #376 (S3) | FEITO/PARCIAL |
| #92 | fora da trilha | Cirurgia | Cirurgia Vascular Urologia Hérnias da Parede Abdominal Princípios da Anestesiologia | Revisão por Questões | 41 | 14 (13.4) | alta | Hérnias da Parede Abdominal; Urologia; Princípios da Anestesiologia; Cirurgia Vascular | #38 (S1), #49 (S2), #61 (S2), #65 (S2) +3 | PARCIAL/ZERO |
| #217 | reserva do extensivo | Ginecologia | Rastreamento do Câncer de Colo Uterino | Teoria II | 0 | 9 (8.4) | alta | Rastreamento do Câncer de Colo Uterino; Câncer de Colo Uterino | #74 (S5), #84 (S5) | PARCIAL/ZERO |
| #34 | fora da trilha | Gastro | Pólipos e Neoplasias Intestinais; Doença Inflamatória Intestinal; Neoplasias de Estômago e Esôfago | Revisão por Questões | 41 | 8 (6.8) | alta | Doença Inflamatória Intestinal; Neoplasias de Estômago e Esôfago | #11 (S5), #30 (S5), #494 (S5) | PARCIAL/ZERO |
| #170 | reserva do extensivo | Nefrologia | Doenças Glomerulares | Teoria I | 0 | 6 (5.4) | alta | Doenças Glomerulares | #68 (S2), #115 (S4) | ZERO |
| #195 | reserva do extensivo | Nefrologia | Doenças Glomerulares | Teoria II | 0 | 6 (5.4) | alta | Doenças Glomerulares | #68 (S2), #115 (S4) | ZERO |
| #224 | reserva do extensivo | Nefrologia | Doenças Glomerulares | Revisão | 37 | 6 (5.4) | alta | Doenças Glomerulares | #68 (S2), #115 (S4) | ZERO |
| #211 | reserva do extensivo | Hemato | Anemias Hemolíticas | Teoria II | 0 | 4 (3.7) | alta | Anemias Hemolíticas | #308 (S4) | PARCIAL |
| #253 | reserva do extensivo | Hemato | Anemias Hemolíticas | Teoria III | 0 | 4 (3.7) | alta | Anemias Hemolíticas | #308 (S4) | PARCIAL |

## Todas as casadas, por peso UERJ

| id | grupo | area | tarefa | tipo | q | UERJ n (peso) | faixa | tema(s) UERJ | tema ja na fila por | estado (18/09) |
|---|---|---|---|---|---|---|---|---|---|---|
| #380 | reserva do extensivo | Infecto | Arboviroses \| HIV \| Tuberculose \| Meningites e Meningoencefalites | Revisão por Questões | 55 | 28 (26.8) | alta | Tuberculose; Meningites e Meningoencefalites; Arboviroses; HIV | #1797 (S2), #376 (S3) | FEITO/PARCIAL |
| #92 | fora da trilha | Cirurgia | Cirurgia Vascular Urologia Hérnias da Parede Abdominal Princípios da Anestesiologia | Revisão por Questões | 41 | 14 (13.4) | alta | Hérnias da Parede Abdominal; Urologia; Princípios da Anestesiologia; Cirurgia Vascular | #38 (S1), #49 (S2), #61 (S2), #65 (S2) +3 | PARCIAL/ZERO |
| #325 | reserva do extensivo | Obstetrícia | Pré-Natal \| Distúrbios Hipertensivos da Gestação \| Sífilis na Gestação e Sífilis Congênita \| Sangramento da Primeira Metade | Revisão por Questões | 56 | 14 (13.4) | alta | Distúrbios Hipertensivos da Gestação; Sangramento da Primeira Metade; Pré-Natal; Sífilis na Gestação e Sífilis Congênita | NENHUMA | FEITO/PARCIAL |
| #354 | reserva do extensivo | Pediatria | Cardiopatias Congênitas \| Cuidados Neonatais \| Asma \| Aleitamento Materno | Revisão por Questões | 43 | 10 (9.4) | alta | Aleitamento Materno; Cuidados Neonatais; Cardiopatias Congênitas | NENHUMA | FEITO |
| #217 | reserva do extensivo | Ginecologia | Rastreamento do Câncer de Colo Uterino | Teoria II | 0 | 9 (8.4) | alta | Rastreamento do Câncer de Colo Uterino; Câncer de Colo Uterino | #74 (S5), #84 (S5) | PARCIAL/ZERO |
| #393 | reserva do extensivo | Cirurgia | Apendicite Aguda \| Colecistite e Colangite Aguda \| Diverticulite Aguda | Revisão por Questões | 52 | 8 (7.4) | alta | Abdome Agudo Inflamatório - Colecistite e Colangite Aguda; Abdome Agudo Inflamatório - Apendicite Aguda | NENHUMA | PARCIAL |
| #22 | fora da trilha | Obstetrícia | Pré-Natal; Assistência ao Parto; Vitalidade Fetal | Revisão por Questões | 36 | 8 (7.1) | alta | Assistência ao Parto; Pré-Natal; Vitalidade Fetal | NENHUMA | PARCIAL/TOCADO |
| #34 | fora da trilha | Gastro | Pólipos e Neoplasias Intestinais; Doença Inflamatória Intestinal; Neoplasias de Estômago e Esôfago | Revisão por Questões | 41 | 8 (6.8) | alta | Doença Inflamatória Intestinal; Neoplasias de Estômago e Esôfago | #11 (S5), #30 (S5), #494 (S5) | PARCIAL/ZERO |
| #241 | reserva do extensivo | Endocrino | Introdução ao Diabetes Mellitus \| Diabetes Mellitus – Insulinoterapia e Cirurgia Metabólica | Teoria | 0 | 7 (6.1) | media | Diabetes Mellitus Tipo 2; Diabetes Mellitus - Complicações Agudas; Introdução ao Diabetes Mellitus Insulinoterapia e Cirurgia Metabólica | NENHUMA | FEITO/PARCIAL |
| #58 | fora da trilha | Pediatria | Diarreia; Pneumonias na Infância; Choque em Pediatria; Alergia Alimentar | Revisão por Questões | 43 | 6 (6.0) | media | Diarreia; Pneumonias na Infância; Alergia Alimentar | NENHUMA | PARCIAL/TOCADO/ZERO |
| #93 | fora da trilha | Ginecologia | Sangramento Uterino Anormal Tumores Anexiais e Câncer de Ovário Prolapsos de Órgãos Pélvicos Câncer de Colo Uterino | Revisão por Questões | 35 | 6 (6.0) | media | Câncer de Colo Uterino; Tumores Anexiais e Câncer de Ovário; Prolapsos de Órgãos Pélvicos; Sangramento Uterino Anormal | #74 (S5), #84 (S5) | PARCIAL/TOCADO/ZERO |
| #349 | reserva do extensivo | Gastro | Doença do Refluxo Gastroesofágico, Esofagites Não-Pépticas e Ingestão de Corpo Estranho | Teoria I | 0 | 6 (5.7) | alta | Doença do Refluxo Gastroesofágico, Esofagites e Corpo Estranho | NENHUMA | PARCIAL |
| #377 | reserva do extensivo | Gastro | Doença do Refluxo Gastroesofágico, Esofagites Não-Pépticas e Ingestão de Corpo Estranho | Teoria II | 0 | 6 (5.7) | alta | Doença do Refluxo Gastroesofágico, Esofagites e Corpo Estranho | NENHUMA | PARCIAL |
| #170 | reserva do extensivo | Nefrologia | Doenças Glomerulares | Teoria I | 0 | 6 (5.4) | alta | Doenças Glomerulares | #68 (S2), #115 (S4) | ZERO |
| #195 | reserva do extensivo | Nefrologia | Doenças Glomerulares | Teoria II | 0 | 6 (5.4) | alta | Doenças Glomerulares | #68 (S2), #115 (S4) | ZERO |
| #224 | reserva do extensivo | Nefrologia | Doenças Glomerulares | Revisão | 37 | 6 (5.4) | alta | Doenças Glomerulares | #68 (S2), #115 (S4) | ZERO |
| #422 | reserva do extensivo | Endocrino | Tireotoxicose \| Diabetes Mellitus - Complicações Agudas \| Diabetes Mellitus Tipo 2 | Revisão por Questões | 43 | 6 (5.4) | media | Diabetes Mellitus Tipo 2; Diabetes Mellitus - Complicações Agudas; Tireotoxicose | NENHUMA | FEITO/PARCIAL |
| #180 | reserva do extensivo | Infecto | Arboviroses | Teoria III | 0 | 5 (5.0) | alta | Arboviroses | NENHUMA | PARCIAL |
| #23 | fora da trilha | Cardiologia | Insuficiência Cardíaca e Hipertensão Arterial Sistêmica | Revisão por Questões | 43 | 5 (4.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Insuficiência Cardíaca Pt.2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #358 | reserva do extensivo | Ginecologia | Endometriose | Teoria II | 0 | 5 (4.4) | alta | Endometriose | NENHUMA | PARCIAL |
| #370 | reserva do extensivo | Cirurgia | Abdome Agudo Inflamatório - Colecistite e Colangite Aguda | Teoria II | 0 | 5 (4.4) | alta | Abdome Agudo Inflamatório - Colecistite e Colangite Aguda | NENHUMA | PARCIAL |
| #384 | reserva do extensivo | Ginecologia | Câncer de Mama | Teoria II | 0 | 5 (4.4) | media | Câncer de Mama; Rastreamento do Câncer de Mama | NENHUMA | PARCIAL/TOCADO |
| #398 | reserva do extensivo | Ginecologia | Câncer de Mama | Teoria III | 0 | 5 (4.4) | media | Câncer de Mama; Rastreamento do Câncer de Mama | NENHUMA | PARCIAL/TOCADO |
| #7 | fora da trilha | Preventiva | Princípios e Diretrizes do SUS \| Atenção Primária à Saúde no Brasil \| Ética Médica \| Financiamento em Saúde | Revisão por Questões | 43 | 4 (4.0) | media | Atenção Primária à Saúde no Brasil; Princípios e Diretrizes do SUS | NENHUMA | FEITO/PARCIAL |
| #33 | fora da trilha | Preventiva | Princípios e Diretrizes do SUS; Atenção Primária à Saúde no Brasil; Ética Médica | Revisão por Questões | 59 | 4 (4.0) | media | Atenção Primária à Saúde no Brasil; Princípios e Diretrizes do SUS | NENHUMA | FEITO/PARCIAL |
| #293 | reserva do extensivo | Gastro | Pancreatite Aguda e Crônica | Teoria III | 0 | 4 (4.0) | alta | Pancreatite Aguda e Crônica | NENHUMA | PARCIAL |
| #320 | reserva do extensivo | Gastro | Pancreatite Aguda e Crônica | Revisão | 42 | 4 (4.0) | alta | Pancreatite Aguda e Crônica | NENHUMA | PARCIAL |
| #211 | reserva do extensivo | Hemato | Anemias Hemolíticas | Teoria II | 0 | 4 (3.7) | alta | Anemias Hemolíticas | #308 (S4) | PARCIAL |
| #253 | reserva do extensivo | Hemato | Anemias Hemolíticas | Teoria III | 0 | 4 (3.7) | alta | Anemias Hemolíticas | #308 (S4) | PARCIAL |
| #19 | fora da trilha | Cardiologia | Hipertensão Arterial Sistêmica | Revisão | 42 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #196 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 1 | Teoria II | 0 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #252 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 1 \| Hipertensão Arterial Sistêmica Pt. 2 | Revisão I | 37 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #282 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 2 | Teoria II | 0 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #305 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 3 | Teoria I | 0 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #337 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 3 | Teoria II | 0 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #345 | reserva do extensivo | Obstetrícia | Assistência ao Parto | Teoria II | 0 | 4 (3.4) | alta | Assistência ao Parto | NENHUMA | PARCIAL |
| #359 | reserva do extensivo | Obstetrícia | Assistência ao Parto | Teoria III | 0 | 4 (3.4) | alta | Assistência ao Parto | NENHUMA | PARCIAL |
| #363 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 1, 2 e 3 | Revisão | 42 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #423 | reserva do extensivo | Cardiologia | Hipertensão Arterial Sistêmica Pt. 1 \| Hipertensão Arterial Sistêmica Pt. 2 \| Hipertensão Arterial Sistêmica Pt. 3 \| Avaliação Perioperatória | Revisão por Questões | 43 | 4 (3.4) | media | Hipertensão Arterial Sistêmica Pt. 1; Hipertensão Arterial Sistêmica Pt. 2; Hipertensão Arterial Sistêmica Pt. 3 | NENHUMA | PARCIAL/TOCADO |
| #5 | fora da trilha | Preventiva | Atenção Primária à Saúde no Brasil | Teoria II | 0 | 3 (3.0) | media | Atenção Primária à Saúde no Brasil | NENHUMA | PARCIAL |
| #6 | fora da trilha | Preventiva | Atenção Primária à Saúde no Brasil | Teoria III | 0 | 3 (3.0) | media | Atenção Primária à Saúde no Brasil | NENHUMA | PARCIAL |
| #29 | fora da trilha | Cirurgia | Urologia | Revisão | 38 | 3 (3.0) | media | Urologia | NENHUMA | PARCIAL |
| #249 | reserva do extensivo | Infecto | HIV | Teoria III | 0 | 3 (3.0) | media | HIV | #1797 (S2) | PARCIAL |
| #343 | reserva do extensivo | Cirurgia | Abdome Agudo Inflamatório - Apendicite Aguda | Teoria II | 0 | 3 (3.0) | media | Abdome Agudo Inflamatório - Apendicite Aguda | NENHUMA | PARCIAL |
| #368 | reserva do extensivo | Pediatria | Diarreia | Teoria II | 0 | 3 (3.0) | media | Diarreia | NENHUMA | PARCIAL |
| #387 | reserva do extensivo | Cirurgia | Abdome Agudo Inflamatório - Diverticulite Aguda | Revisão | 48 | 3 (3.0) | media | Abdome Agudo Inflamatório - Apendicite Aguda | NENHUMA | PARCIAL |
| #154 | reserva do extensivo | Cirurgia | Cirurgia Infantil I | Teoria II | 0 | 3 (2.7) | media | Cirurgia Infantil I | NENHUMA | PARCIAL |
| #162 | reserva do extensivo | Ginecologia | Planejamento Familiar | Revisão | 41 | 3 (2.7) | media | Planejamento Familiar | NENHUMA | PARCIAL |
| #163 | reserva do extensivo | Obstetrícia | Pré-Natal | Teoria III | 0 | 3 (2.7) | media | Pré-Natal | NENHUMA | PARCIAL |
| #174 | reserva do extensivo | Cirurgia | Cirurgia Infantil II | Teoria II | 0 | 3 (2.7) | media | Cirurgia Infantil I | NENHUMA | PARCIAL |
| #203 | reserva do extensivo | Cirurgia | Cirurgia Infantil III | Teoria II | 0 | 3 (2.7) | media | Cirurgia Infantil I | NENHUMA | PARCIAL |
| #361 | reserva do extensivo | Endocrino | Diabetes Mellitus Tipo 2 | Teoria II | 0 | 3 (2.7) | media | Diabetes Mellitus Tipo 2 | NENHUMA | PARCIAL |
| #415 | reserva do extensivo | Endocrino | Diabetes Mellitus Tipo 2 \| Perioperatório - Controle Glicêmico e Manejo dos Glicocorticóides | Revisão | 43 | 3 (2.7) | media | Diabetes Mellitus Tipo 2 | NENHUMA | PARCIAL |
| #2 | fora da trilha | Preventiva | Saúde do Idoso | Teoria | 0 | 2 (2.0) | media | Saúde do Idoso | #3 (S2), #4 (S7) | ZERO |
| #13 | fora da trilha | Pediatria | Pneumonias na Infância | Teoria + Exercícios | 24 | 2 (2.0) | media | Pneumonias na Infância | NENHUMA | TOCADO |
| #21 | fora da trilha | Reumato | Doenças Inflamatórias do Tecido Conjuntivo | Revisão | 34 | 2 (2.0) | baixa | Doenças Inflamatória do Tecido Conjuntivo I; Doenças Inflamatória do Tecido Conjuntivo II | NENHUMA | PARCIAL |
| #24 | fora da trilha | Pediatria | Pneumonias na Infância | Revisão | 47 | 2 (2.0) | media | Pneumonias na Infância | NENHUMA | TOCADO |
| #25 | fora da trilha | Ginecologia | Tumores Anexiais e Câncer de Ovário | Teoria + Exercícios | 21 | 2 (2.0) | media | Tumores Anexiais e Câncer de Ovário | NENHUMA | TOCADO |
| #39 | fora da trilha | Ginecologia | Tumores Anexiais e Câncer de Ovário | Revisão | 40 | 2 (2.0) | media | Tumores Anexiais e Câncer de Ovário | NENHUMA | TOCADO |
| #296 | reserva do extensivo | Reumato | Doenças Inflamatórias do Tecido Conjuntivo I | Teoria III | 0 | 2 (2.0) | baixa | Doenças Inflamatória do Tecido Conjuntivo I; Doenças Inflamatória do Tecido Conjuntivo II | NENHUMA | PARCIAL |
| #314 | reserva do extensivo | Ginecologia | Vulvovaginites | Teoria II | 0 | 2 (2.0) | media | Vulvovaginites | NENHUMA | PARCIAL |
| #339 | reserva do extensivo | Reumato | Doenças Inflamatória do Tecido Conjuntivo I | Revisão | 34 | 2 (2.0) | baixa | Doenças Inflamatória do Tecido Conjuntivo I; Doenças Inflamatória do Tecido Conjuntivo II | NENHUMA | PARCIAL |
| #382 | reserva do extensivo | Pediatria | Pneumonias na Infância | Teoria I | 0 | 2 (2.0) | media | Pneumonias na Infância | NENHUMA | TOCADO |
| #386 | reserva do extensivo | Pediatria | Pneumonias na Infância | Teoria II | 0 | 2 (2.0) | media | Pneumonias na Infância | NENHUMA | TOCADO |
| #392 | reserva do extensivo | Reumato | Doenças Inflamatória do Tecido Conjuntivo II | Teoria II | 0 | 2 (2.0) | baixa | Doenças Inflamatória do Tecido Conjuntivo I; Doenças Inflamatória do Tecido Conjuntivo II | NENHUMA | PARCIAL |
| #395 | reserva do extensivo | Pediatria | Pneumonias na Infância | Revisão | 43 | 2 (2.0) | media | Pneumonias na Infância | NENHUMA | TOCADO |
| #44 | fora da trilha | Hemato | Anemias Microcíticas e Leucemias Agudas | Teoria + Exercícios | 27 | 2 (1.7) | baixa | Leucemias Agudas; Anemias Microcíticas | NENHUMA | ZERO |
| #104 | fora da trilha | Hemato | Anemias Microcíticas Leucemias Agudas | Revisão | 27 | 2 (1.7) | baixa | Leucemias Agudas; Anemias Microcíticas | NENHUMA | ZERO |
| #186 | reserva do extensivo | Pneumo | Introdução à Pneumologia | Teoria | 0 | 2 (1.7) | media | Introdução a Pneumologia | NENHUMA | TOCADO |
| #255 | reserva do extensivo | Otorrino | Neoplasias benignas e malignas de cabeça e pescoço, doenças congênitas cervicofaciais e traqueostomia | Teoria I | 0 | 2 (1.7) | media | Neoplasias beningas e malignas de cabeça e pescoço, doenças congênitas cervicofaciais e traqueostomia | NENHUMA | PARCIAL |
| #268 | reserva do extensivo | Pneumo | Pneumologia Intensiva | Revisão I | 15 | 2 (1.7) | media | Introdução a Pneumologia | NENHUMA | TOCADO |
| #286 | reserva do extensivo | Cirurgia | Trauma Abdominal e Pélvico | Teoria II | 0 | 2 (1.7) | media | Trauma Abdominal e Pélvico | NENHUMA | PARCIAL |
| #291 | reserva do extensivo | Cirurgia | Trauma Abdominal e Pélvico | Teoria III | 0 | 2 (1.7) | media | Trauma Abdominal e Pélvico | NENHUMA | PARCIAL |
| #302 | reserva do extensivo | Cirurgia | Trauma Abdominal e Pélvico | Teoria IV | 0 | 2 (1.7) | media | Trauma Abdominal e Pélvico | NENHUMA | PARCIAL |
| #307 | reserva do extensivo | Pneumo | Pneumologia Intensiva | Teoria III | 0 | 2 (1.7) | media | Introdução a Pneumologia | NENHUMA | TOCADO |
| #313 | reserva do extensivo | Cirurgia | Trauma Abdominal e Pélvico | Teoria V | 0 | 2 (1.7) | media | Trauma Abdominal e Pélvico | NENHUMA | PARCIAL |
| #318 | reserva do extensivo | Cirurgia | Trauma Abdominal e Pélvico | Revisão | 48 | 2 (1.7) | media | Trauma Abdominal e Pélvico | NENHUMA | PARCIAL |
| #323 | reserva do extensivo | Otorrino | Neoplasias benignas e malignas de cabeça e pescoço, doenças congênitas cervicofaciais e traqueostomia | Teoria II | 0 | 2 (1.7) | media | Neoplasias beningas e malignas de cabeça e pescoço, doenças congênitas cervicofaciais e traqueostomia | NENHUMA | PARCIAL |
| #326 | reserva do extensivo | Endocrino | Metabolismo Ósseo e Mineral - Princípios e Fisiologia \| Metabolismo Ósseo e Mineral - Hipercalcemia | Teoria | 0 | 2 (1.7) | media | Metabolismo Ósseo e Mineral - Princípios e Fisiologia Hipercalcemia | NENHUMA | ZERO |
| #351 | reserva do extensivo | Pneumo | Pneumologia Intensiva | Teoria IV | 0 | 2 (1.7) | media | Introdução a Pneumologia | NENHUMA | TOCADO |
| #353 | reserva do extensivo | Otorrino | Neoplasias Benignas e Malignas de Cabeça e Pescoço, Doenças Congênitas Cervicofaciais e Traqueostomia | Revisão | 44 | 2 (1.7) | media | Neoplasias beningas e malignas de cabeça e pescoço, doenças congênitas cervicofaciais e traqueostomia | NENHUMA | PARCIAL |
| #405 | reserva do extensivo | Pneumo | Pneumologia Intensiva | Teoria V | 0 | 2 (1.7) | media | Introdução a Pneumologia | NENHUMA | TOCADO |
| #406 | reserva do extensivo | Psiquiatria | Dependência Química | Teoria II | 0 | 2 (1.7) | media | Dependência Química | NENHUMA | PARCIAL |
| #419 | reserva do extensivo | Psiquiatria | Dependência Química | Revisão | 43 | 2 (1.7) | media | Dependência Química | NENHUMA | PARCIAL |
| #8 | fora da trilha | Cirurgia | Cirurgia Vascular | Revisão | 43 | 1 (1.0) | baixa | Cirurgia Vascular | NENHUMA | ZERO |
| #9 | fora da trilha | Obstetrícia | Vitalidade Fetal | Teoria + Exercícios | 25 | 1 (1.0) | baixa | Vitalidade Fetal | NENHUMA | TOCADO |
| #14 | fora da trilha | Ginecologia | Sangramento Uterino Anormal | Revisão | 42 | 1 (1.0) | baixa | Sangramento Uterino Anormal | NENHUMA | PARCIAL |
| #15 | fora da trilha | Obstetrícia | Vitalidade Fetal | Revisão | 36 | 1 (1.0) | baixa | Vitalidade Fetal | NENHUMA | TOCADO |
| #48 | fora da trilha | Pediatria | Alergia Alimentar | Teoria + Exercícios | 21 | 1 (1.0) | baixa | Alergia Alimentar | NENHUMA | ZERO |
| #50 | fora da trilha | Ginecologia | Prolapsos de Órgãos Pélvicos | Teoria + Exercícios | 25 | 1 (1.0) | baixa | Prolapsos de Órgãos Pélvicos | NENHUMA | ZERO |
| #52 | fora da trilha | Pediatria | Alergia Alimentar | Revisão | 38 | 1 (1.0) | baixa | Alergia Alimentar | NENHUMA | ZERO |
| #62 | fora da trilha | Ginecologia | Prolapsos de Órgãos Pélvicos | Revisão | 41 | 1 (1.0) | baixa | Prolapsos de Órgãos Pélvicos | NENHUMA | ZERO |
| #76 | fora da trilha | Pediatria | Crescimento | Teoria | 18 | 1 (1.0) | baixa | Crescimento | #119 (S6), #498 (S7) | TOCADO |
| #82 | fora da trilha | Pediatria | Crescimento | Revisão | 31 | 1 (1.0) | baixa | Crescimento | #119 (S6), #498 (S7) | TOCADO |
| #85 | fora da trilha | Obstetrícia | Partograma e Distocia | Teoria | 17 | 1 (1.0) | baixa | Partograma e Distocia | #106 (S6) | ZERO |
| #99 | fora da trilha | Obstetrícia | Partograma e Distocia | Revisão | 39 | 1 (1.0) | baixa | Partograma e Distocia | #106 (S6) | ZERO |
| #109 | fora da trilha | Pediatria | Desnutrição na Infância | Teoria | 16 | 1 (1.0) | baixa | Desnutrição na Infância | #119 (S6) | ZERO |
| #121 | fora da trilha | Pediatria | Desnutrição na Infância | Revisão | 31 | 1 (1.0) | baixa | Desnutrição na Infância | #119 (S6) | ZERO |
| #139 | fora da trilha | Obstetrícia | Hemorragia Pós-Parto | Teoria | 24 | 1 (1.0) | baixa | Hemorragia Pós-Parto | NENHUMA | TOCADO |
| #145 | fora da trilha | Obstetrícia | Hemorragia Pós-Parto | Revisão | 41 | 1 (1.0) | baixa | Hemorragia Pós-Parto | NENHUMA | TOCADO |
| #194 | reserva do extensivo | Endocrino | Tireotoxicose | Teoria II | 0 | 1 (1.0) | baixa | Tireotoxicose | NENHUMA | PARCIAL |
| #223 | reserva do extensivo | Endocrino | Tireotoxicose | Revisão | 40 | 1 (1.0) | baixa | Tireotoxicose | NENHUMA | PARCIAL |
| #352 | reserva do extensivo | Hemato | Leucemias Agudas | Teoria I | 0 | 1 (1.0) | baixa | Leucemias Agudas | NENHUMA | ZERO |
| #378 | reserva do extensivo | Hemato | Leucemias Agudas | Teoria II | 0 | 1 (1.0) | baixa | Leucemias Agudas | NENHUMA | ZERO |
| #385 | reserva do extensivo | Obstetrícia | Vitalidade Fetal | Teoria I | 0 | 1 (1.0) | baixa | Vitalidade Fetal | NENHUMA | TOCADO |
| #397 | reserva do extensivo | Cirurgia | Cirurgia Vascular | Teoria I | 0 | 1 (1.0) | baixa | Cirurgia Vascular | NENHUMA | ZERO |
| #399 | reserva do extensivo | Obstetrícia | Vitalidade Fetal | Teoria II | 0 | 1 (1.0) | baixa | Vitalidade Fetal | NENHUMA | TOCADO |
| #402 | reserva do extensivo | Obstetrícia | Vitalidade Fetal | Teoria III | 0 | 1 (1.0) | baixa | Vitalidade Fetal | NENHUMA | TOCADO |
| #411 | reserva do extensivo | Cirurgia | Cirurgia Vascular | Teoria II | 0 | 1 (1.0) | baixa | Cirurgia Vascular | NENHUMA | ZERO |
| #413 | reserva do extensivo | Obstetrícia | Vitalidade Fetal | Revisão | 43 | 1 (1.0) | baixa | Vitalidade Fetal | NENHUMA | TOCADO |
| #414 | reserva do extensivo | Infecto | Sepse | Teoria II | 0 | 1 (1.0) | baixa | Sepse | NENHUMA | PARCIAL |
| #418 | reserva do extensivo | Hemato | Leucemias Agudas | Revisão | 43 | 1 (1.0) | baixa | Leucemias Agudas | NENHUMA | ZERO |
| #35 | fora da trilha | Nefrologia | Distúrbios Ácido- Base; Distúrbios do Potássio; Nefrolitíase | Revisão por Questões | 43 | 1 (0.7) | baixa | Distúrbios Ácido-Base | NENHUMA | PARCIAL |
| #229 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. I | Revisão II | 45 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #244 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. II | Teoria II | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #258 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. II | Revisão I | 41 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #263 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. II | Teoria III | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #272 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. II | Teoria IV | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #277 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. II | Revisão | 47 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #285 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. III | Teoria I | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #290 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. III | Teoria II | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #298 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. III | Revisão I | 28 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #312 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. III | Teoria III | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #317 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. III | Teoria IV | 0 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #328 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. III | Revisão | 39 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |
| #340 | reserva do extensivo | Preventiva | Medidas de Saúde Coletiva Pt. I, II e III | Revisão por Questões | 60 | 1 (0.7) | baixa | Medidas de Saúde Coletiva Pt. I | NENHUMA | PARCIAL |

## Sem tema casado na prevalencia UERJ -- conferir a olho

O casamento e por tokens (o mesmo do gerador da trilha): linha aqui NAO tem peso zero, tem peso NAO MEDIDO.

| id | grupo | area | tarefa | tipo | q | UERJ n (peso) | faixa | tema(s) UERJ | tema ja na fila por | estado (18/09) |
|---|---|---|---|---|---|---|---|---|---|---|
| #27 | fora da trilha | Preventiva | Ética Médica | Revisão | 39 | 0 (0) | -- | -- | NENHUMA | -- |
| #28 | fora da trilha | Pediatria | Choque em Pediatria | Teoria + Exercícios | 24 | 0 (0) | -- | -- | NENHUMA | -- |
| #31 | fora da trilha | Nefrologia | Nefrolitíase | Revisão | 42 | 0 (0) | -- | -- | NENHUMA | -- |
| #36 | fora da trilha | Preventiva | Financiamento em Saúde | Teoria + Exercícios | 27 | 0 (0) | -- | -- | NENHUMA | -- |
| #37 | fora da trilha | Pediatria | Choque em Pediatria | Revisão | 36 | 0 (0) | -- | -- | NENHUMA | -- |
| #47 | fora da trilha | Preventiva | Financiamento em Saúde | Teoria + Exercícios | 15 | 0 (0) | -- | -- | NENHUMA | -- |
| #59 | fora da trilha | Preventiva | Financiamento em saúde | Revisão | 39 | 0 (0) | -- | -- | NENHUMA | -- |
| #129 | fora da trilha | Cardiologia | Fibrilação e Flutter Atrial Parada Cardiorrespiratória | Teoria | 31 | 0 (0) | -- | -- | NENHUMA | -- |
| #133 | fora da trilha | Cardiologia | Fibrilação e Flutter Atrial Parada Cardiorrespiratória | Revisão | 31 | 0 (0) | -- | -- | NENHUMA | -- |
| #158 | reserva do extensivo | Gastro | Polipose Intestinal e Câncer Colorretal | Teoria I | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #168 | reserva do extensivo | Gastro | Polipose Intestinal e Câncer Colorretal | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #181 | reserva do extensivo | Gastro | Polipose Intestinal e Câncer Colorretal | Revisão I | 34 | 0 (0) | -- | -- | NENHUMA | -- |
| #183 | reserva do extensivo | Neurologia | Coma e Alterações da Consciência | Teoria I | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #185 | reserva do extensivo | Hemato | Introdução ao Estudo das Anemias | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #193 | reserva do extensivo | Gastro | Polipose Intestinal e Câncer Colorretal | Teoria III | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #200 | reserva do extensivo | Ortopedia | Conceitos Básicos do Trauma Ortopédico | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #205 | reserva do extensivo | Obstetrícia | Doença Hipertensiva Específica da Gestação e Hipertensão Crônica | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #209 | reserva do extensivo | Gastro | Polipose Intestinal e Câncer Colorretal | Teoria IV | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #210 | reserva do extensivo | Neurologia | Coma e Alterações da Consciência | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #218 | reserva do extensivo | Obstetrícia | Doença Hipertensiva Específica da Gestação e Hipertensão Crônica | Teoria III | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #222 | reserva do extensivo | Gastro | Polipose Intestinal e Câncer Colorretal | Revisão | 42 | 0 (0) | -- | -- | NENHUMA | -- |
| #226 | reserva do extensivo | Dermato | Oncologia Cutânea (Câncer de Pele) | Teoria I | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #232 | reserva do extensivo | Obstetrícia | Doença Hipertensiva Específica da Gestação e Hipertensão Crônica | Revisão | 52 | 0 (0) | -- | -- | NENHUMA | -- |
| #239 | reserva do extensivo | Psiquiatria | Intoxicações Exógenas | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #251 | reserva do extensivo | Nefrologia | Infecção do Trato Urinário | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #267 | reserva do extensivo | Neurologia | Coma e Alterações da Consciência | Revisão | 42 | 0 (0) | -- | -- | NENHUMA | -- |
| #274 | reserva do extensivo | Ginecologia | Doenças Benignas da Mama | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #281 | reserva do extensivo | Nefrologia | Infecção do Trato Urinário | Revisão | 35 | 0 (0) | -- | -- | NENHUMA | -- |
| #283 | reserva do extensivo | Ortopedia | Quadril Pediátrico | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #294 | reserva do extensivo | Psiquiatria | Intoxicações Exógenas | Revisão | 47 | 0 (0) | -- | -- | NENHUMA | -- |
| #295 | reserva do extensivo | Hepato | Hepatites Virais | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #309 | reserva do extensivo | Dermato | Oncologia Cutânea | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #316 | reserva do extensivo | Pediatria | Asma | Teoria III | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #322 | reserva do extensivo | Hepato | Hepatites Virais | Teoria III | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #362 | reserva do extensivo | Nefrologia | Lesão Renal Aguda | Teoria III | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #364 | reserva do extensivo | Hepato | Hepatites Virais | Teoria IV | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #366 | reserva do extensivo | Ortopedia | Quadril Pediátrico | Revisão | 41 | 0 (0) | -- | -- | NENHUMA | -- |
| #379 | reserva do extensivo | Dermato | Oncologia Cutânea | Revisão | 35 | 0 (0) | -- | -- | NENHUMA | -- |
| #381 | reserva do extensivo | Ortopedia | Complicações do Trauma Ortopédico | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #388 | reserva do extensivo | Endocrino | Perioperatório - Controle Glicêmico e Manejo dos Glicocorticóides | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #390 | reserva do extensivo | Cardiologia | Avaliação Perioperatória | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #394 | reserva do extensivo | Infecto | Micoses Invasivas | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #400 | reserva do extensivo | Pediatria | Choque em Pediatria | Teoria I | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #407 | reserva do extensivo | Oftalmo | Síndrome do Olho Vermelho | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #409 | reserva do extensivo | Pediatria | Choque em Pediatria | Teoria II | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #417 | reserva do extensivo | Cardiologia | Avaliação Perioperatória | Revisão | 43 | 0 (0) | -- | -- | NENHUMA | -- |
| #420 | reserva do extensivo | Hepato | Hepatites Virais | Teoria V | 0 | 0 (0) | -- | -- | NENHUMA | -- |
| #424 | reserva do extensivo | Endocrino | Metabolismo Ósseo e Mineral - Vitamina D e Osteomalácia | Teoria | 0 | 0 (0) | -- | -- | NENHUMA | -- |

