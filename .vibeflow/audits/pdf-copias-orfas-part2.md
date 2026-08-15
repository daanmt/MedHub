# Auditoria: cópias órfãs de PDF em `resumos/` (Flashcards - *.pdf)

> consolidacao-part-2 (DoD 4) · 2026-08-14 · HEAD `47aad80` · gerado por script, não editado à mão.

## Pergunta

O passo de cópia em `tools/emed_flashcards.py::harvest()` (`shutil.copy2(pdf, dest_pdf)`, PDF de origem no HD externo do EMED → `resumos/<area>/Flashcards - <Tema>.pdf`) existia **só** para alimentar o tier morto de RAG sobre PDF (`pdf_raw`, F17, removido nesta mesma part) e os originais existem em outro lugar (o HD externo, `--source`)? Se sim, o passo sai e as cópias já feitas ficam órfãs (listadas abaixo, remoção física fica para a part-7).

## Veredito

**NÃO — o passo de cópia FICA.** Falso que as cópias existiam só para o índice morto: além de alimentarem o (agora removido) `pdf_raw`, elas são consumidas por dois sistemas vivos e não relacionados a RAG, ambos via scan genérico de `resumos/**/*.pdf`:

- `tools/cobertura_conhecimento.py` (F16a) — relatório read-only de cobertura, pareia PDF × `.md` por stem normalizado para achar PDFs-fonte sem resumo escrito.
- `tools/insert_questao.py::_tem_lastro` (F31, gate de inserção) — bloqueia inserção de questão/card para um tema sem lastro escrito; lastro = `.md` **OU** PDF-fonte par em `resumos/**`.

Auditoria (275 cópias `Flashcards - *.pdf` em `resumos/`, pareamento por stem normalizado — remove prefixo numérico EMED, acentos, pontuação):

- **47 cópias (108.8 MB)** não têm `.md` nem PDF-fonte tópico correspondente em `resumos/**` — são a **única** evidência que `cobertura_conhecimento.py`/`_tem_lastro` enxergam para aquele tema. **Load-bearing, não remover.**
- **228 cópias (677.3 MB)** já têm `.md` e/ou PDF-fonte tópico cobrindo o mesmo tema em `resumos/**` — a cópia é redundante para cobertura/lastro (o `.md`/PDF-fonte já supre os dois), e sua única contribuição não-redundante era alimentar `pdf_raw` (morto). **Listadas abaixo como órfãs.**

Originais: em ambos os grupos, o PDF de **autoria** (`Flashc.pdf`) vive fora do repo, no HD externo do EMED usado em `--source` — o repo nunca contém a única cópia real, `resumos/` sempre teve uma cópia *derivada*. Para o grupo órfão, além disso, o **conteúdo clínico** já está coberto dentro do próprio repo pelo `.md` cunhado e/ou pelo PDF-fonte tópico listado na coluna "backing" — a coluna aponta o arquivo que torna a cópia redundante.

**Ação nesta part:** nenhuma deleção física (part-7 decide, com esta lista). O passo de cópia em `harvest()` permanece ligado para *todos* os decks (órfãos e não-órfãos) — o motivo está documentado inline no código (`tools/emed_flashcards.py`, comentário antes do `shutil.copy2`).

## Lista de cópias órfãs (228 arquivos, 677.3 MB total)

Ordenadas por path. `backing` = arquivo em `resumos/**` que já cobre o mesmo tema (torna a cópia redundante para cobertura/lastro).

| path | tamanho (KB) | backing |
|---|---:|---|
| `resumos/Cirurgia/Flashcards - Abdome Agudo Hemorrágico.pdf` | 2,181.0 | `resumos/Cirurgia/1. Abdome Agudo Hemorrágico.pdf` |
| `resumos/Cirurgia/Flashcards - Abdome Agudo Inflamatório - Apendicite Aguda.pdf` | 4,936.0 | `resumos/Cirurgia/8. Abdome Agudo Inflamatório - Apendicite Aguda.pdf` |
| `resumos/Cirurgia/Flashcards - Abdome Agudo Inflamatório - Colecistite e Colangite Aguda.pdf` | 5,471.9 | `resumos/Cirurgia/Abdome Agudo Inflamatório - Colecistite e Colangite Aguda.md` |
| `resumos/Cirurgia/Flashcards - Abdome Agudo Inflamatório - Diverticulite Aguda.pdf` | 3,906.7 | `resumos/Cirurgia/17. Abdome Agudo Inflamatório - Diverticulite Aguda.pdf` |
| `resumos/Cirurgia/Flashcards - Abdome Agudo Obstrutivo.pdf` | 11,460.6 | `resumos/Cirurgia/16. Abdome agudo obstrutivo.pdf` |
| `resumos/Cirurgia/Flashcards - Abdome Agudo Perfurativo.pdf` | 1,659.5 | `resumos/Cirurgia/32. Abdome Agudo Perfurativo.pdf` |
| `resumos/Cirurgia/Flashcards - Abdome Agudo Vascular.pdf` | 10,732.8 | `resumos/Cirurgia/15. Abdome agudo vascular.pdf` |
| `resumos/Cirurgia/Flashcards - Cicatrização de Feridas.pdf` | 3,283.4 | `resumos/Cirurgia/31. Cicatrização de Feridas.pdf` |
| `resumos/Cirurgia/Flashcards - Cirurgia Infantil - Parte I.pdf` | 6,327.1 | `resumos/Cirurgia/12. Cirurgia Infantil - Parte I.pdf` |
| `resumos/Cirurgia/Flashcards - Cirurgia Infantil - Parte II.pdf` | 5,377.4 | `resumos/Cirurgia/13. Cirurgia Infantil - Parte II.pdf` |
| `resumos/Cirurgia/Flashcards - Cirurgia Infantil - Parte III.pdf` | 12,421.3 | `resumos/Cirurgia/14. Cirurgia Infantil - Parte III.pdf` |
| `resumos/Cirurgia/Flashcards - Cirurgia Plástica.pdf` | 1,739.6 | `resumos/Cirurgia/11. Cirurgia Plástica.pdf` |
| `resumos/Cirurgia/Flashcards - Cirurgia Torácica.pdf` | 1,236.2 | `resumos/Cirurgia/10. Cirurgia Torácica.pdf` |
| `resumos/Cirurgia/Flashcards - Complicações Pós-Operatórias.pdf` | 10,645.0 | `resumos/Cirurgia/30. Complicações Pós-Operatórias.pdf` |
| `resumos/Cirurgia/Flashcards - Neoplasias do Apêndice Cecal.pdf` | 806.1 | `resumos/Cirurgia/28. Neoplasias do apêndice cecal.pdf` |
| `resumos/Cirurgia/Flashcards - Proctologia.pdf` | 7,542.1 | `resumos/Cirurgia/26. Proctologia.pdf` |
| `resumos/Cirurgia/Flashcards - Quadril Pediátrico.pdf` | 2,475.7 | `resumos/Cirurgia/Quadril Pediátrico.md` |
| `resumos/Cirurgia/Flashcards - Queimaduras e Trauma Elétrico.pdf` | 1,918.5 | `resumos/Cirurgia/7. Queimaduras e Trauma Elétrico.pdf` |
| `resumos/Cirurgia/Flashcards - Resposta Endócrino-Metabólica ao Trauma.pdf` | 1,506.1 | `resumos/Cirurgia/25. Resposta Endócrino-Metabólica ao Trauma.pdf` |
| `resumos/Cirurgia/Flashcards - Temas Gerais em Cirurgia.pdf` | 9,003.5 | `resumos/Cirurgia/24. Temas Gerais em Cirurgia.pdf` |
| `resumos/Cirurgia/Flashcards - Trauma - Choque.pdf` | 1,816.8 | `resumos/Cirurgia/5. Trauma - Choque.pdf` |
| `resumos/Cirurgia/Flashcards - Trauma Abdominal e Pélvico.pdf` | 2,631.3 | `resumos/Cirurgia/23. Trauma Abdominal e Pélvico.pdf` |
| `resumos/Cirurgia/Flashcards - Trauma Populações Especiais (Pediátrico, Gestante e Idosos).pdf` | 1,300.5 | `resumos/Cirurgia/21. Trauma Populações Especiais (Pediátrico, Gestante e Idosos).pdf` |
| `resumos/Cirurgia/Flashcards - Trauma Vascular de Extremidades e Musculoesquelético.pdf` | 1,740.2 | `resumos/Cirurgia/20. Trauma Vascular de Extremidades e Musculoesquelético.pdf` |
| `resumos/Cirurgia/Flashcards - Trauma de Face e Cervical.pdf` | 2,573.3 | `resumos/Cirurgia/22. Trauma de Face e Cervical.pdf` |
| `resumos/Cirurgia/Flashcards - Urgências Abdominais - Abdome Agudo.pdf` | 4,021.3 | `resumos/Cirurgia/4. Urgências Abdominais Abdome Agudo.pdf` |
| `resumos/Cirurgia/Flashcards - Urologia.pdf` | 3,500.5 | `resumos/Cirurgia/3. Urologia.pdf` |
| `resumos/Cirurgia/Flashcards - Vesícula e Vias Biliares.pdf` | 6,020.2 | `resumos/Cirurgia/19. Vesícula e Vias Biliares.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Bradiarritmias.pdf` | 3,500.0 | `resumos/Clínica Médica/Cardiologia/21. Bradiarritmias.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Dislipidemia e Estratificação de Risco Cardiovascular.pdf` | 2,009.4 | `resumos/Clínica Médica/Cardiologia/13. Dislipidemia e Estratificação de Risco Cardiovascular.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Fibrilação e Flutter Atrial.pdf` | 471.6 | `resumos/Clínica Médica/Cardiologia/17. Fibrilação e Flutter Atrial.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Hipertensão Arterial Sistêmica (Parte 3)  Secundária e Crise Hipertensiva.pdf` | 494.2 | `resumos/Clínica Médica/Cardiologia/18. Hipertensão Arterial Sistêmica (Parte 3) - Secundária e Crise Hipertensiva.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - IAMCSSST (Infarto Agudo do Miocárdio com Supradesnivelamento de Segmento ST).pdf` | 2,869.5 | `resumos/Clínica Médica/Cardiologia/10. IAMCSSST (Infarto Agudo do Miocárdio com Supradesnivelamento de Segmento ST).pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Insuficiência Cardíaca (Parte 2)  Tratamento.pdf` | 470.1 | `resumos/Clínica Médica/Cardiologia/3. Insuficiência Cardíaca (Parte 2)_ Tratamento.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Parada Cardiorrespiratória (PCR).pdf` | 4,676.6 | `resumos/Clínica Médica/Cardiologia/16. Parada Cardiorrespiratória (PCR).pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Pericardiopatias.pdf` | 6,670.5 | `resumos/Clínica Médica/Cardiologia/15. Pericardiopatias.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Semiologia Cardíaca.pdf` | 463.1 | `resumos/Clínica Médica/Cardiologia/11. Semiologia Cardíaca.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Síncope.pdf` | 509.1 | `resumos/Clínica Médica/Cardiologia/19. Síncope.pdf` |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Síndromes Aórticas Agudas.pdf` | 461.2 | `resumos/Clínica Médica/Cardiologia/12. Síndromes Aórticas Agudas.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Dermatoses Eczematosas.pdf` | 3,611.8 | `resumos/Clínica Médica/Dermatologia/5. Dermatoses Eczematosas.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Dermatoses Infecciosas.pdf` | 937.8 | `resumos/Clínica Médica/Dermatologia/4. Dermatoses Infecciosas.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Dermatoses Papuloescamosas.pdf` | 936.8 | `resumos/Clínica Médica/Dermatologia/7. Dermatoses Papuloescamosas.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Dermatoses Vesicobolhosas.pdf` | 932.2 | `resumos/Clínica Médica/Dermatologia/8. Dermatoses Vesicobolhosas.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Farmacodermias.pdf` | 3,494.0 | `resumos/Clínica Médica/Dermatologia/6. Farmacodermias.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Hanseníase.pdf` | 2,192.1 | `resumos/Clínica Médica/Dermatologia/3. Hanseníase.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Histologia e Fisiologia da Pele e Lesões Elementares.pdf` | 930.8 | `resumos/Clínica Médica/Dermatologia/1. Histologia e Fisiologia da Pele e Lesões Elementares.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Oncologia Cutânea (Câncer de Pele).pdf` | 1,043.4 | `resumos/Clínica Médica/Dermatologia/2. Oncologia Cutânea (Câncer de Pele).pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Piodermites.pdf` | 2,350.9 | `resumos/Clínica Médica/Dermatologia/10. Piodermites.pdf` |
| `resumos/Clínica Médica/Dermatologia/Flashcards - Síndromes Verrucosas.pdf` | 1,194.7 | `resumos/Clínica Médica/Dermatologia/11. Síndromes Verrucosas.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Adrenal - Feocromocitoma, Hiperaldosteronismo e Incidentaloma Adrenal.pdf` | 1,274.7 | `resumos/Clínica Médica/Endocrinologia/19. Adrenal - Feocromocitoma, Hiperaldosteronismo e Incidentaloma Adrenal.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Adrenal - Morfofisiologia Adrenal.pdf` | 2,568.9 | `resumos/Clínica Médica/Endocrinologia/16. Adrenal-Morfofisiologia Adrenal.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Adrenal- Hipercortisolismo (Síndrome de Cushing).pdf` | 1,155.9 | `resumos/Clínica Médica/Endocrinologia/18. Adrenal- Hipercortisolismo (Síndrome de Cushing).pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Adrenal- Hipocortisolismo (Insuficiência Adrenal).pdf` | 1,117.5 | `resumos/Clínica Médica/Endocrinologia/17. Adrenal - Hipocortisolismo (Insuficiência Adrenal).pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Diabetes Mellitus - Complicações Agudas.pdf` | 1,792.8 | `resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Diabetes Mellitus - Complicações Crônicas.pdf` | 4,002.5 | `resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Crônicas.md` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Diabetes Mellitus - Insulinoterapia e Cirurgia Metabólica.pdf` | 2,205.4 | `resumos/Clínica Médica/Endocrinologia/3. Diabetes Mellitus_ Insulinoterapia e Cirurgia Metabólica.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Diabetes Mellitus Tipo 2.pdf` | 2,161.0 | `resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus Tipo 2.md` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Hipoglicemia no Paciente não Diabético.pdf` | 2,860.3 | `resumos/Clínica Médica/Endocrinologia/24. Hipoglicemia no Paciente não Diabético.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Hipófise - Acromegalia e Incidentaloma Hipofisário.pdf` | 1,825.0 | `resumos/Clínica Médica/Endocrinologia/21. Hipófise-Acromegalia e Incidentaloma Hipofisário.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Hipófise - Fisiologia da Hipófise e Hipopituitarismo.pdf` | 4,117.5 | `resumos/Clínica Médica/Endocrinologia/20. Hipófise - Fisiologia da Hipófise e Hipopituitarismo.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Hipófise - Hiperprolactinemia.pdf` | 2,789.3 | `resumos/Clínica Médica/Endocrinologia/22. Hipófise - Hiperprolactinemia.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Incongruência de Gênero.pdf` | 720.4 | `resumos/Clínica Médica/Endocrinologia/25. Incongruência de Gênero.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Hipercalcemia.pdf` | 1,502.8 | `resumos/Clínica Médica/Endocrinologia/10. Metabolismo Ósseo e Mineral - Hipercalcemia.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Hipocalcemia.pdf` | 2,948.7 | `resumos/Clínica Médica/Endocrinologia/11. Metabolismo Ósseo e Mineral - Hipocalcemia.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Magnésio e Fosfato.pdf` | 1,469.6 | `resumos/Clínica Médica/Endocrinologia/12. Metabolismo Ósseo e Mineral - Magnésio e Fosfato.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Osteoporose e Doença Óssea de Paget.pdf` | 2,807.0 | `resumos/Clínica Médica/Endocrinologia/15. Metabolismo Ósseo e Mineral - Osteoporose e Doença Óssea de Paget.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Vitamina D e Osteomalácia.pdf` | 1,719.9 | `resumos/Clínica Médica/Endocrinologia/13. Metabolismo Ósseo e Mineral-Vitamina D e Osteomalácia.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Neoplasias Endócrinas Múltiplas.pdf` | 1,889.8 | `resumos/Clínica Médica/Endocrinologia/23. Neoplasias Endócrinas Múltiplas.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Obesidade - Obesidade e Síndrome Metabólica.pdf` | 6,172.9 | `resumos/Clínica Médica/Endocrinologia/8. Obesidade - Obesidade e Síndrome Metabólica.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Tireoide - Hipotireoidismo.pdf` | 1,455.9 | `resumos/Clínica Médica/Endocrinologia/26. Tireoide - Hipotireoidismo.pdf` |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Tireoide - Tireotoxicose  Diagnóstico, Etiologia, Tratamento, Tireotoxicose na Gestação e Crise Tireotóxica.pdf` | 1,473.7 | `resumos/Clínica Médica/Endocrinologia/7. Tireoide - Tireotoxicose_ Diagnóstico, Etiologia, Tratamento, Tireotoxicose na Gestação e Crise Tireotóxica.pdf` |
| `resumos/Clínica Médica/Gastroenterologia/Flashcards - Hemorragia Digestiva Alta Não Varicosa.pdf` | 4,824.9 | `resumos/Clínica Médica/Gastroenterologia/1. Hemorragia Digestiva Alta Não Varicosa.pdf` |
| `resumos/Clínica Médica/Gastroenterologia/Flashcards - Hemorragia Digestiva Alta Varicosa.pdf` | 1,729.5 | `resumos/Clínica Médica/Gastroenterologia/6. Hemorragia Digestiva Alta Varicosa.pdf` |
| `resumos/Clínica Médica/Gastroenterologia/Flashcards - Hemorragia Digestiva Baixa.pdf` | 3,608.8 | `resumos/Clínica Médica/Gastroenterologia/3. Hemorragia Digestiva Baixa.pdf` |
| `resumos/Clínica Médica/Gastroenterologia/Flashcards - Pancreatite Aguda e Crônica (Pancreatites).pdf` | 3,931.1 | `resumos/Clínica Médica/Gastroenterologia/5. Pancreatite Aguda e Crônica (Pancreatites).pdf` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Anemia Associada a Condições Não Hematológicas.pdf` | 5,505.6 | `resumos/Clínica Médica/Hematologia/5. Anemia Associada a Condições Não Hematológicas.pdf` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Anemias Hemolíticas.pdf` | 12,041.9 | `resumos/Clínica Médica/Hematologia/Anemias Hemolíticas.md` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Anemias Macrocíticas.pdf` | 2,452.1 | `resumos/Clínica Médica/Hematologia/3. Anemias Macrocíticas.pdf` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Hemostasia I  Conceitos Básicos e Anticoagulantes.pdf` | 4,246.5 | `resumos/Clínica Médica/Hematologia/6. Hemostasia I_ Conceitos Básicos e Anticoagulantes.pdf` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Introdução ao Estudo das Anemias.pdf` | 6,220.0 | `resumos/Clínica Médica/Hematologia/1. Introdução ao Estudo das Anemias.pdf` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Leucemias Crônicas, Linfomas, Mielodisplasias e Mieloproliferações.pdf` | 4,225.8 | `resumos/Clínica Médica/Hematologia/9. Leucemias Crônicas, Linfomas, Mielodisplasias e Mieloproliferações.pdf` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Medicina Transfusional.pdf` | 3,870.0 | `resumos/Clínica Médica/Hematologia/Medicina Transfusional.md` |
| `resumos/Clínica Médica/Hematologia/Flashcards - Mieloma Múltiplo (Gamopatias Monoclonais).pdf` | 2,207.2 | `resumos/Clínica Médica/Hematologia/8. Mieloma Múltiplo (Gamopatias Monoclonais).pdf` |
| `resumos/Clínica Médica/Hepatologia/Flashcards - Hepatites Virais.pdf` | 2,845.9 | `resumos/Clínica Médica/Hepatologia/Hepatites Virais.md` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Animais Peçonhentos.pdf` | 2,803.2 | `resumos/Clínica Médica/Infectologia/4. Animais Peçonhentos.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Arboviroses (Dengue, Chikungunya e Zika).pdf` | 4,809.0 | `resumos/Clínica Médica/Infectologia/10. Arboviroses (Dengue, Chikungunya e Zika).pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Endocardite Bacteriana - Endocardite Infecciosa.pdf` | 1,561.6 | `resumos/Clínica Médica/Infectologia/15. Endocardite Bacteriana - Endocardite Infecciosa.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Hepatoesplenomegalias Infecciosas.pdf` | 4,532.2 | `resumos/Clínica Médica/Infectologia/17. Hepatoesplenomegalias Infecciosas.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Leptospirose.pdf` | 1,753.4 | `resumos/Clínica Médica/Infectologia/2. Leptospirose.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Malária.pdf` | 911.9 | `resumos/Clínica Médica/Infectologia/Malária.md` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Micoses Invasivas.pdf` | 10,180.0 | `resumos/Clínica Médica/Infectologia/11. Micoses Invasivas.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Neutropenia Febril e Febre de Origem Indeterminada.pdf` | 1,013.2 | `resumos/Clínica Médica/Infectologia/14. Neutropenia Febril e Febre de Origem Indeterminada.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Parasitoses.pdf` | 8,774.5 | `resumos/Clínica Médica/Infectologia/13. Parasitoses.pdf` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Raiva, Tétano, Mordedura e Arranhadura Animal.pdf` | 3,547.8 | `resumos/Clínica Médica/Infectologia/Raiva, Tétano, Mordedura e Arranhadura Animal.md` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Sepse.pdf` | 1,754.6 | `resumos/Clínica Médica/Infectologia/Sepse.md` |
| `resumos/Clínica Médica/Infectologia/Flashcards - Síndrome Febril Íctero-Hemorrágica.pdf` | 2,551.8 | `resumos/Clínica Médica/Infectologia/18. Síndrome Febril Íctero-Hemorrágica.pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Análise da Gasometria Arterial.pdf` | 722.1 | `resumos/Clínica Médica/Nefrologia/8. Análise da Gasometria Arterial.pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Distúrbios do Potássio.pdf` | 2,251.3 | `resumos/Clínica Médica/Nefrologia/Distúrbios do Potássio.md` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Distúrbios do Sódio - Disnatremias.pdf` | 1,669.3 | `resumos/Clínica Médica/Nefrologia/9. Distúrbios do Sódio - Disnatremias.pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Doença Renal Crônica (DRC) - Parte I.pdf` | 8,013.3 | `resumos/Clínica Médica/Nefrologia/2. Doença Renal Crônica (DRC) - Parte I.pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Doença Renal Crônica (DRC) - Parte II.pdf` | 8,013.3 | `resumos/Clínica Médica/Nefrologia/3. Doença Renal Crônica (DRC) - Parte II.pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Doenças Glomerulares.pdf` | 4,332.4 | `resumos/Clínica Médica/Nefrologia/4. Doenças Glomerulares.pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Lesão Renal Aguda (LRA).pdf` | 2,116.6 | `resumos/Clínica Médica/Nefrologia/1. Lesão Renal Aguda (LRA).pdf` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Nefrolitíase.pdf` | 6,324.4 | `resumos/Clínica Médica/Nefrologia/Nefrolitíase.md` |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Túbulo-Interstício Renal.pdf` | 1,806.7 | `resumos/Clínica Médica/Nefrologia/6. Túbulo Interstício Renal.pdf` |
| `resumos/Clínica Médica/Neurologia/Flashcards - Cefaleias.pdf` | 4,874.6 | `resumos/Clínica Médica/Neurologia/Cefaleias.md` |
| `resumos/Clínica Médica/Neurologia/Flashcards - Demências.pdf` | 3,668.7 | `resumos/Clínica Médica/Neurologia/Demências.md` |
| `resumos/Clínica Médica/Neurologia/Flashcards - Epilepsias.pdf` | 2,651.8 | `resumos/Clínica Médica/Neurologia/Epilepsias.md` |
| `resumos/Clínica Médica/Pneumologia/Flashcards - Asma.pdf` | 1,021.3 | `resumos/Clínica Médica/Pneumologia/Asma.md` |
| `resumos/Clínica Médica/Pneumologia/Flashcards - Derrame Pleural.pdf` | 3,269.1 | `resumos/Clínica Médica/Pneumologia/1. Derrame Pleural.pdf` |
| `resumos/Clínica Médica/Pneumologia/Flashcards - Introdução a Pneumologia.pdf` | 2,659.5 | `resumos/Clínica Médica/Pneumologia/4. Introdução à Pneumologia.pdf` |
| `resumos/Clínica Médica/Pneumologia/Flashcards - Neoplasias Pulmonares.pdf` | 7,792.3 | `resumos/Clínica Médica/Pneumologia/8. Neoplasias Pulmonares.pdf` |
| `resumos/Clínica Médica/Pneumologia/Flashcards - Tromboembolismo Pulmonar (TEP).pdf` | 6,384.2 | `resumos/Clínica Médica/Pneumologia/3. Tromboembolismo Pulmonar (TEP).pdf` |
| `resumos/Clínica Médica/Psiquiatria/Flashcards - Transtornos do Humor.pdf` | 3,349.8 | `resumos/Clínica Médica/Psiquiatria/Transtornos do Humor.md` |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Artrite Reumatoide.pdf` | 397.7 | `resumos/Clínica Médica/Reumatologia/Artrite Reumatoide.md` |
| `resumos/Clínica Médica/Reumatologia/Flashcards - DITC II.pdf` | 401.5 | `resumos/Clínica Médica/Reumatologia/DITC II.md` |
| `resumos/GO/Flashcards - Abdome Agudo em Ginecologia.pdf` | 363.8 | `resumos/GO/31. Abdome Agudo em Ginecologia.pdf` |
| `resumos/GO/Flashcards - Adenomiose.pdf` | 5,924.9 | `resumos/GO/20. Adenomiose.pdf` |
| `resumos/GO/Flashcards - Aloimunização Materna e Doença Hemolítica Perinatal.pdf` | 1,093.8 | `resumos/GO/10. Aloimunização Materna e Doença Hemolítica Perinatal.pdf` |
| `resumos/GO/Flashcards - Amenorreia.pdf` | 382.2 | `resumos/GO/3. Amenorreia.pdf` |
| `resumos/GO/Flashcards - Anatomia e Embriologia do Trato Genital Feminino.pdf` | 391.1 | `resumos/GO/26. Anatomia e Embriologia do Trato Genital Feminino.pdf` |
| `resumos/GO/Flashcards - Assistência ao Parto.pdf` | 1,084.4 | `resumos/GO/Assistência ao Parto.md` |
| `resumos/GO/Flashcards - Assistência à Vítima de Violência Sexual.pdf` | 383.1 | `resumos/GO/19. Assistência à Vítima de Violência Sexual.pdf` |
| `resumos/GO/Flashcards - Bacia Obstétrica, Pelvimetria e Estática Fetal.pdf` | 6,378.2 | `resumos/GO/6. Bacia Obstétrica, Pelvimetria e Estática Fetal.pdf` |
| `resumos/GO/Flashcards - Cervicites.pdf` | 3,268.5 | `resumos/GO/16. Cervicites.pdf` |
| `resumos/GO/Flashcards - Ciclo Menstrual.pdf` | 389.1 | `resumos/GO/1. Ciclo Menstrual.pdf` |
| `resumos/GO/Flashcards - Climatério e Terapia Hormonal.pdf` | 2,138.2 | `resumos/GO/23. Climatério e Terapia Hormonal.pdf` |
| `resumos/GO/Flashcards - Câncer de Colo Uterino.pdf` | 3,680.9 | `resumos/GO/22. Câncer de Colo Uterino.pdf` |
| `resumos/GO/Flashcards - Câncer de Mama.pdf` | 395.9 | `resumos/GO/11. Câncer de Mama.pdf` |
| `resumos/GO/Flashcards - Câncer do Corpo do Útero.pdf` | 415.6 | `resumos/GO/12. Câncer do Corpo do Útero.pdf` |
| `resumos/GO/Flashcards - Diabetes Mellitus na Gestação.pdf` | 2,307.2 | `resumos/GO/Diabetes Mellitus na Gestação.md` |
| `resumos/GO/Flashcards - Doença Inflamatória Pélvica (DIP).pdf` | 3,345.1 | `resumos/GO/17. Doença Inflamatória Pélvica (DIP).pdf` |
| `resumos/GO/Flashcards - Doenças Benignas da Mama.pdf` | 419.2 | `resumos/GO/9. Doenças benignas da Mama.pdf` |
| `resumos/GO/Flashcards - Doenças de Vulva e Vagina.pdf` | 406.5 | `resumos/GO/14. Doenças de Vulva e Vagina.pdf` |
| `resumos/GO/Flashcards - Dor Pélvica Crônica e Dismenorreia.pdf` | 368.0 | `resumos/GO/28. Dor Pélvica Crônica e Dismenorreia.pdf` |
| `resumos/GO/Flashcards - Endometriose.pdf` | 5,266.9 | `resumos/GO/Endometriose.md` |
| `resumos/GO/Flashcards - Gestação Múltipla.pdf` | 7,190.4 | `resumos/GO/4. Gestação Múltipla.pdf` |
| `resumos/GO/Flashcards - Incontinência Urinária.pdf` | 396.6 | `resumos/GO/10. Incontinência Urinária.pdf` |
| `resumos/GO/Flashcards - Indução do Parto e Pós-Datismo.pdf` | 2,426.7 | `resumos/GO/19. Indução do Parto e Pós-Datismo.pdf` |
| `resumos/GO/Flashcards - Infecção Puerperal.pdf` | 1,648.4 | `resumos/GO/7. Infecção Puerperal.pdf` |
| `resumos/GO/Flashcards - Infecções Congênitas na Gestação.pdf` | 1,097.9 | `resumos/GO/9. Infecções Congênitas na Gestação.pdf` |
| `resumos/GO/Flashcards - Infertilidade Conjugal.pdf` | 403.7 | `resumos/GO/27. Infertilidade Conjugal.pdf` |
| `resumos/GO/Flashcards - Miomatose Uterina.pdf` | 3,932.8 | `resumos/GO/24. Miomatose Uterina.pdf` |
| `resumos/GO/Flashcards - Modificações Fisiológicas da Gestação.pdf` | 1,092.4 | `resumos/GO/12. Modificações Fisiológicas da Gestação.pdf` |
| `resumos/GO/Flashcards - Parto Vaginal Operatório.pdf` | 2,437.7 | `resumos/GO/17. Parto Vaginal Operatório.pdf` |
| `resumos/GO/Flashcards - Planejamento Familiar.pdf` | 2,946.4 | `resumos/GO/Planejamento Familiar.md` |
| `resumos/GO/Flashcards - Pré-Natal.pdf` | 5,778.1 | `resumos/GO/Pré-Natal.md` |
| `resumos/GO/Flashcards - Pólipos Uterinos.pdf` | 3,397.5 | `resumos/GO/6. Pólipos Uterinos.pdf` |
| `resumos/GO/Flashcards - Rastreamento do Câncer de Colo Uterino.pdf` | 4,505.5 | `resumos/GO/21. Rastreamento do Câncer de Colo Uterino.pdf` |
| `resumos/GO/Flashcards - Rastreamento do Câncer de Mama.pdf` | 4,572.4 | `resumos/GO/7. Rastreamento do Câncer de Mama.pdf` |
| `resumos/GO/Flashcards - Restrição de Crescimento Fetal e Óbito Fetal.pdf` | 1,091.6 | `resumos/GO/20. Restrição de Crescimento Fetal e Óbito Fetal.pdf` |
| `resumos/GO/Flashcards - Rotura Prematura de Membranas (RPM).pdf` | 1,445.6 | `resumos/GO/2. Rotura Prematura de Membranas (RPM).pdf` |
| `resumos/GO/Flashcards - Sangramento da Primeira Metade.pdf` | 3,675.8 | `resumos/GO/23. Sangramento da Primeira Metade.pdf` |
| `resumos/GO/Flashcards - Sangramento da Segunda Metade.pdf` | 5,045.9 | `resumos/GO/24. Sangramento da Segunda Metade.pdf` |
| `resumos/GO/Flashcards - Sexualidade.pdf` | 384.1 | `resumos/GO/29. Sexualidade.pdf` |
| `resumos/GO/Flashcards - Sífilis na Gestação e Sífilis Congênitas.pdf` | 1,116.4 | `resumos/GO/8. Sífilis na Gestação e Sífilis Congênitas.pdf` |
| `resumos/GO/Flashcards - Síndrome Pré-Menstrual.pdf` | 341.8 | `resumos/GO/30. Síndrome Pré-Menstrual.pdf` |
| `resumos/GO/Flashcards - Síndrome dos Ovários Policísticos.pdf` | 2,878.5 | `resumos/GO/4. Síndrome dos Ovários Policísticos.pdf` |
| `resumos/GO/Flashcards - Síndromes Hipertensivas da Gestação.pdf` | 1,783.2 | `resumos/GO/Síndromes Hipertensivas da Gestação.md` |
| `resumos/GO/Flashcards - Tumores Anexiais e Câncer de Ovário.pdf` | 394.4 | `resumos/GO/13. Tumores Anexiais e Câncer de Ovário.pdf` |
| `resumos/GO/Flashcards - Ultrassom em Obstetrícia.pdf` | 777.2 | `resumos/GO/21. Ultrassom em Obstetrícia.pdf` |
| `resumos/GO/Flashcards - Vitalidade Fetal.pdf` | 1,083.8 | `resumos/GO/15. Vitalidade Fetal.pdf` |
| `resumos/GO/Flashcards - Vulvovaginites.pdf` | 5,874.1 | `resumos/GO/Vulvovaginites.md` |
| `resumos/GO/Flashcards - Úlceras Genitais.pdf` | 4,628.6 | `resumos/GO/Úlceras Genitais.md` |
| `resumos/Pediatria/Flashcards - Aleitamento Materno.pdf` | 3,415.7 | `resumos/Pediatria/18. Aleitamento Materno.pdf` |
| `resumos/Pediatria/Flashcards - Alergia Alimentar.pdf` | 1,434.1 | `resumos/Pediatria/4. Alergia Alimentar.pdf` |
| `resumos/Pediatria/Flashcards - Anafilaxia e Urticária.pdf` | 2,242.8 | `resumos/Pediatria/7. Anafilaxia e Urticária.pdf` |
| `resumos/Pediatria/Flashcards - Artrite Idiopática Juvenil (AIJ).pdf` | 4,263.6 | `resumos/Pediatria/40. Artrite Idiopática Juvenil (AIJ).pdf` |
| `resumos/Pediatria/Flashcards - Asma.pdf` | 453.1 | `resumos/Clínica Médica/Pneumologia/Asma.md` |
| `resumos/Pediatria/Flashcards - BRUE   SMSL (Brief Resolved Unexplained Events   Síndrome da Morte Súbita do Lactente).pdf` | 1,173.9 | `resumos/Pediatria/2. BRUE-SMSL (Brief Resolved Unexplained Events - Síndrome da Morte Súbita do Lactente).pdf` |
| `resumos/Pediatria/Flashcards - Bronquiolite.pdf` | 3,621.4 | `resumos/Pediatria/35. Bronquiolite.pdf` |
| `resumos/Pediatria/Flashcards - Cardiopatias Congênitas.pdf` | 5,130.4 | `resumos/Pediatria/Cardiopatias Congênitas.md` |
| `resumos/Pediatria/Flashcards - Cefaleias na Infância.pdf` | 385.8 | `resumos/Pediatria/41. Cefaleias na infância.pdf` |
| `resumos/Pediatria/Flashcards - Choque em Pediatria.pdf` | 454.6 | `resumos/Pediatria/26. Choque em Pediatria.pdf` |
| `resumos/Pediatria/Flashcards - Constipação Intestinal.pdf` | 2,123.1 | `resumos/Pediatria/9. Constipação Intestinal.pdf` |
| `resumos/Pediatria/Flashcards - Convulsão Febril.pdf` | 2,584.7 | `resumos/Pediatria/Convulsão Febril.md` |
| `resumos/Pediatria/Flashcards - Coqueluche.pdf` | 6,822.5 | `resumos/Pediatria/45. Coqueluche.pdf` |
| `resumos/Pediatria/Flashcards - Crescimento.pdf` | 388.2 | `resumos/Pediatria/Crescimento.md` |
| `resumos/Pediatria/Flashcards - Cuidados Neonatais.pdf` | 6,812.6 | `resumos/Pediatria/Cuidados Neonatais.md` |
| `resumos/Pediatria/Flashcards - Deficiências Vitamínicas e Profilaxias.pdf` | 406.8 | `resumos/Pediatria/Deficiências Vitamínicas e Profilaxias.md` |
| `resumos/Pediatria/Flashcards - Desenvolvimento Neuropsicomotor (DNPM).pdf` | 6,851.0 | `resumos/Pediatria/24. Desenvolvimento Neuropsicomotor (DNPM).pdf` |
| `resumos/Pediatria/Flashcards - Desnutrição na Infância.pdf` | 2,411.8 | `resumos/Pediatria/19. Desnutrição na Infância.pdf` |
| `resumos/Pediatria/Flashcards - Diagnóstico Nutricional.pdf` | 388.3 | `resumos/Pediatria/43. Diagnóstico Nutricional.pdf` |
| `resumos/Pediatria/Flashcards - Diarreia.pdf` | 2,170.5 | `resumos/Pediatria/48. Diarreia.pdf` |
| `resumos/Pediatria/Flashcards - Distúrbios Respiratórios do Período Neonatal.pdf` | 1,396.6 | `resumos/Pediatria/11. Distúrbios Respiratórios do Período Neonatal.pdf` |
| `resumos/Pediatria/Flashcards - Doença Celíaca em Pediatria.pdf` | 5,381.5 | `resumos/Pediatria/23. Doença Celíaca em Pediatria.pdf` |
| `resumos/Pediatria/Flashcards - Doença de Kawasaki.pdf` | 3,835.0 | `resumos/Pediatria/34. Doença de Kawasaki.pdf` |
| `resumos/Pediatria/Flashcards - Doença do Refluxo Gastroesofágico em Pediatria.pdf` | 1,429.2 | `resumos/Pediatria/47. Doença do Refluxo Gastroesofágico em Pediatria.pdf` |
| `resumos/Pediatria/Flashcards - Doenças Exantemáticas.pdf` | 4,931.4 | `resumos/Pediatria/Doenças Exantemáticas.md` |
| `resumos/Pediatria/Flashcards - Emergências Pediátricas.pdf` | 3,968.2 | `resumos/Pediatria/Emergências Pediátricas.md` |
| `resumos/Pediatria/Flashcards - Enurese Noturna.pdf` | 684.4 | `resumos/Pediatria/14. Enurese Noturna.pdf` |
| `resumos/Pediatria/Flashcards - Febre Reumática.pdf` | 4,768.5 | `resumos/Pediatria/Febre Reumática.md` |
| `resumos/Pediatria/Flashcards - Febre na Pediatria.pdf` | 537.4 | `resumos/Pediatria/39. Febre na Pediatria.pdf` |
| `resumos/Pediatria/Flashcards - Fibrose Cística.pdf` | 5,296.3 | `resumos/Pediatria/31. Fibrose Cística.pdf` |
| `resumos/Pediatria/Flashcards - Hiperplasia Adrenal Congênita.pdf` | 824.6 | `resumos/Pediatria/10. Hiperplasia Adrenal Congênita.pdf` |
| `resumos/Pediatria/Flashcards - Hipertensão Arterial na Criança e Adolescente.pdf` | 2,141.8 | `resumos/Pediatria/36. Hipertensão Arterial na Criança e Adolescente.pdf` |
| `resumos/Pediatria/Flashcards - Hipotireoidismo Congênito.pdf` | 1,604.3 | `resumos/Pediatria/16. Hipotireoidismo Congênito.pdf` |
| `resumos/Pediatria/Flashcards - Icterícia e Sepse Neonatal.pdf` | 3,668.7 | `resumos/Pediatria/Icterícia e Sepse Neonatal.md` |
| `resumos/Pediatria/Flashcards - Imunizações.pdf` | 2,082.3 | `resumos/Pediatria/Imunizações.md` |
| `resumos/Pediatria/Flashcards - Infecção de Trato Urinário em Pediatria (ITU).pdf` | 2,186.8 | `resumos/Pediatria/Infecção de Trato Urinário em Pediatria (ITU).md` |
| `resumos/Pediatria/Flashcards - Infecções Congênitas.pdf` | 5,831.0 | `resumos/Pediatria/20. Infecções Congênitas.pdf` |
| `resumos/Pediatria/Flashcards - Obesidade Infantil e na Adolescência.pdf` | 2,769.3 | `resumos/Pediatria/5. Obesidade Infantil e na Adolescência.pdf` |
| `resumos/Pediatria/Flashcards - Pneumonias na Infância.pdf` | 2,111.8 | `resumos/Pediatria/15. Pneumonias na Infância.pdf` |
| `resumos/Pediatria/Flashcards - Puberdade.pdf` | 4,114.3 | `resumos/Pediatria/1. Puberdade.pdf` |
| `resumos/Pediatria/Flashcards - Reanimação Neonatal.pdf` | 3,535.4 | `resumos/Pediatria/Reanimação Neonatal.md` |
| `resumos/Pediatria/Flashcards - Segurança em Pediatria.pdf` | 2,594.1 | `resumos/Pediatria/42. Segurança em Pediatria.pdf` |
| `resumos/Pediatria/Flashcards - Sífilis na Gestação e Sífilis Congênitas.pdf` | 6,201.2 | `resumos/GO/8. Sífilis na Gestação e Sífilis Congênitas.pdf` |
| `resumos/Pediatria/Flashcards - Tuberculose na Infância.pdf` | 3,167.4 | `resumos/Pediatria/33. Tuberculose na Infância.pdf` |
| `resumos/Pediatria/Flashcards - Tópicos em Pediatria.pdf` | 1,064.4 | `resumos/Pediatria/44. Tópicos em Pediatria.pdf` |
| `resumos/Preventiva/Flashcards - Bases de Saúde do Trabalhador e Normas Regulamentadoras.pdf` | 790.9 | `resumos/Preventiva/5. Bases de Saúde do Trabalhador e Normas Regulamentadoras.pdf` |
| `resumos/Preventiva/Flashcards - Estatística Médica.pdf` | 2,363.9 | `resumos/Preventiva/2. Estatística Médica.pdf` |
| `resumos/Preventiva/Flashcards - Financiamento em Saúde.pdf` | 1,167.5 | `resumos/Preventiva/18. Financiamento em Saúde.pdf` |
| `resumos/Preventiva/Flashcards - História do SUS.pdf` | 1,069.4 | `resumos/Preventiva/14. História do SUS.pdf` |
| `resumos/Preventiva/Flashcards - Marcos Legais do Sistema Único de Saúde.pdf` | 4,027.1 | `resumos/Preventiva/4. Marcos Legais do Sistema Único de Saúde.pdf` |
| `resumos/Preventiva/Flashcards - Medicina de Família e Comunidade.pdf` | 3,784.9 | `resumos/Preventiva/Medicina de Família e Comunidade.md` |
| `resumos/Preventiva/Flashcards - Medidas de Saúde Coletiva - Parte I  Indicadores de Morbidade.pdf` | 6,728.8 | `resumos/Preventiva/6. Medidas de Saúde Coletiva - Parte I_ Indicadores de Morbidade.pdf` |
| `resumos/Preventiva/Flashcards - Medidas de Saúde Coletiva - Parte III  Indicadores Demográficos + Transição Demográfica-Epidemiológica.pdf` | 4,377.4 | `resumos/Preventiva/8. Medidas de Saúde Coletiva - Parte III_ Indicadores Demográficos + Transição Demográfica-Epidemiológica.pdf` |
| `resumos/Preventiva/Flashcards - Pesquisa Epidemiológica e Medidas de Associação.pdf` | 5,791.7 | `resumos/Preventiva/21. Pesquisa Epidemiológica e Medidas de Associação.pdf` |
| `resumos/Preventiva/Flashcards - Políticas de Saúde.pdf` | 1,226.5 | `resumos/Preventiva/17. Políticas de Saúde.pdf` |
| `resumos/Preventiva/Flashcards - Princípios e Diretrizes do SUS.pdf` | 3,494.4 | `resumos/Preventiva/Princípios e Diretrizes do SUS.md` |
| `resumos/Preventiva/Flashcards - Processo Saúde-Doença.pdf` | 1,602.3 | `resumos/Preventiva/Processo Saúde-Doença.md` |
| `resumos/Preventiva/Flashcards - Processos Epidêmicos e Epidemiologia das Doenças Infecciosas.pdf` | 4,055.8 | `resumos/Preventiva/9. Processos Epidêmicos e Epidemiologia das Doenças Infecciosas.pdf` |
| `resumos/Preventiva/Flashcards - Processos de Descentralização e Regionalização do SUS.pdf` | 7,054.0 | `resumos/Preventiva/15. Processos de Descentralização e Regionalização do SUS.pdf` |
| `resumos/Preventiva/Flashcards - Saúde do Idoso.pdf` | 1,984.6 | `resumos/Preventiva/20. Saúde do Idoso.pdf` |
| `resumos/Preventiva/Flashcards - Sistemas de Informação em Saúde.pdf` | 3,521.4 | `resumos/Preventiva/Sistemas de Informação em Saúde.md` |
| `resumos/Preventiva/Flashcards - Testes Diagnósticos.pdf` | 4,632.9 | `resumos/Preventiva/13. Testes Diagnósticos.pdf` |
| `resumos/Preventiva/Flashcards - Vigilância em Saúde.pdf` | 1,708.5 | `resumos/Preventiva/Vigilância em Saúde.md` |
| `resumos/Preventiva/Flashcards - Ética Médica.pdf` | 1,651.8 | `resumos/Preventiva/Ética Médica.md` |

## Lista de cópias load-bearing, NÃO órfãs (47 arquivos, 108.8 MB total)

Sem `.md` nem PDF-fonte tópico correspondente — única evidência em `resumos/**` para o tema. Mantidas; não fazem parte da lista de remoção candidata.

| path | tamanho (KB) |
|---|---:|
| `resumos/Cirurgia/Flashcards - Hérnias da Parede Abdominal.pdf` | 13,561.7 |
| `resumos/Cirurgia/Flashcards - Nutrição em Cirurgia e Aceleração da Recuperação Pós-Operatória.pdf` | 4,486.9 |
| `resumos/Cirurgia/Flashcards - Trauma - Avaliação Inicial, Vias Aéreas e Trauma Torácico.pdf` | 3,285.2 |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Avaliação Perioperatoria.pdf` | 593.9 |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Doença Arterial Coronariana Estável (DAC Estável).pdf` | 3,070.8 |
| `resumos/Clínica Médica/Cardiologia/Flashcards - Hipertensão Arterial Sistêmica (Parte 1.2).pdf` | 457.5 |
| `resumos/Clínica Médica/Cardiologia/Flashcards - SCASSST - Síndrome Coronária Aguda Sem Supra do Segmento ST.pdf` | 603.1 |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Diabetes Mellitus - Hiperglicemia Hospitalar.pdf` | 363.6 |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Introdução ao Diabetes Mellitus.pdf` | 1,828.6 |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Princípios e Fisiologia.pdf` | 1,401.7 |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Metabolismo Ósseo e Mineral - Raquitismo.pdf` | 1,719.6 |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Perioperatório - Controle Glicêmico e Manejo dos Glicocorticóides.pdf` | 1,016.6 |
| `resumos/Clínica Médica/Endocrinologia/Flashcards - Tireoide - Fisiologia, Semiologia e Avaliação Diagnóstica.pdf` | 2,333.3 |
| `resumos/Clínica Médica/Hematologia/Flashcards - Hemostasia II  Doenças Hemostáticas.pdf` | 6,355.0 |
| `resumos/Clínica Médica/Infectologia/Flashcards - Infecções Relacionadas à Assistência em Saúde - Infecção do sítio cirúrgico e antibióticoprofilaxia.pdf` | 2,286.8 |
| `resumos/Clínica Médica/Nefrologia/Flashcards - Distúrbios Ácido-Básicos.pdf` | 1,986.1 |
| `resumos/Clínica Médica/Nefrologia/Flashcards - ITU (Infecção do Trato Urinário).pdf` | 2,410.9 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Acidentes Vasculares Cerebrais.pdf` | 1,962.4 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Anatomia, Fisiologia e Semiologia Neurológica.pdf` | 3,751.0 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Coma e Alterações da Consciência.pdf` | 6,608.9 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Distúrbios do Movimento.pdf` | 947.2 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Distúrbios do Sono.pdf` | 1,818.1 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Doenças Desmielinizantes e Encefalites Autoimunes.pdf` | 4,790.4 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Doenças Neuromusculares (Neuropatias Periféricas, Miopatias, Doenças da Junção Neuromuscular e Doença do Neurônio Motor).pdf` | 1,195.1 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Traumatismo Cranioencefálico - TCE.pdf` | 5,213.1 |
| `resumos/Clínica Médica/Neurologia/Flashcards - Tumores Intracranianos.pdf` | 2,931.6 |
| `resumos/Clínica Médica/Pneumologia/Flashcards - Miscelânea (Interstício, Bronquiectasias, Hipertensão Pulmonar e Pneumotórax).pdf` | 1,250.8 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Artrites Microcristalinas.pdf` | 596.5 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Artropatias Infecciosas.pdf` | 390.5 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Doenças do Osso e da Cartilagem.pdf` | 547.5 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Espondiloartrites.pdf` | 404.4 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Introdução à Reumatologia.pdf` | 391.0 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Reumatologia Pediátrica.pdf` | 392.8 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Síndromes Dolorosas Crônicas.pdf` | 399.6 |
| `resumos/Clínica Médica/Reumatologia/Flashcards - Vasculites.pdf` | 394.8 |
| `resumos/GO/Flashcards - Abortamento de Repetição.pdf` | 1,167.6 |
| `resumos/GO/Flashcards - Alteração do volume de Líquido Amniótico.pdf` | 2,442.6 |
| `resumos/GO/Flashcards - HPP - Hemorragia Pós-Parto.pdf` | 4,193.2 |
| `resumos/GO/Flashcards - Partograma e Distocias.pdf` | 775.6 |
| `resumos/GO/Flashcards - Prolapso de Órgãos Pélvicos.pdf` | 3,750.0 |
| `resumos/GO/Flashcards - Sangramento Uterino Anormal (SUA).pdf` | 3,654.4 |
| `resumos/GO/Flashcards - TPP - Prematuridade e Trabalho de Parto Prematuro.pdf` | 1,814.0 |
| `resumos/Pediatria/Flashcards - Distúrbios Metabólicos do Neonato.pdf` | 1,403.2 |
| `resumos/Pediatria/Flashcards - Púrpura de Hennoch Schonlein-Vasculite por IGA.pdf` | 4,190.4 |
| `resumos/Pediatria/Flashcards - Síndromes Genéticas e Erros Inatos do Metabolismo.pdf` | 392.6 |
| `resumos/Preventiva/Flashcards - Atenção Primária à Saúde no Brasil.pdf` | 2,901.8 |
| `resumos/Preventiva/Flashcards - Medidas de Saúde Coletiva - Parte II  Indicadores de Mortalidade.pdf` | 2,971.6 |

