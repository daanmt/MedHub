# RAG Retrieval Eval — MedHub

_Generated 2026-05-27T19:05:23Z_

- Fixture: `Tools\eval\queries.json` (sha256[:12] `f8095c1b73f3`, n=18)
- RAG impl: `app/engine/rag.py` @ git `5e36350`
- ChromaDB available: `True`

## Summary

| Config | n | Recall@1 | Recall@3 | Recall@5 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| hyde=on | 18 | 0.556 | 0.778 | 0.778 | 0.657 |
| hyde=off | 18 | 0.389 | 0.444 | 0.500 | 0.425 |

## Per-query detail

### hyde=on

| id | rank | area | query | expected | top-3 sources |
|---|---:|---|---|---|---|
| `go-001` | 2 | GO | Cancro mole vs LGV diagnóstico diferencial orifício único bico de regador | resumos/GO/Úlceras Genitais.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/Úlceras Genitais.md<br>resumos/GO/[GIN] CA de Mama.md |
| `go-002` | MISS | GO | Quando iniciar supressão de herpes na gestação 36 semanas | resumos/GO/Úlceras Genitais.md | resumos/GO/Assistência ao Parto.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md<br>resumos/GO/[OBS] Sífilis na Gestação e Congênita.md |
| `pre-001` | MISS | Preventiva | Preenchimento da DO causas de morte Parte I e Parte II | resumos/Preventiva/Sistemas de Informação em Saúde.md | resumos/Preventiva/Medidas de Saúde Coletiva.md<br>resumos/Preventiva/Epidemiologia e Estudos.md<br>resumos/Preventiva/Medidas de Saúde Coletiva.md |
| `go-003` | 1 | GO | Eclâmpsia com convulsão ativa primeira conduta via aérea ou MgSO4 | resumos/GO/Síndromes Hipertensivas na Gestação.md | resumos/GO/Síndromes Hipertensivas na Gestação.md<br>resumos/GO/[OBS] Sífilis na Gestação e Congênita.md<br>resumos/GO/[OBS] Sífilis na Gestação e Congênita.md |
| `go-004` | MISS | GO | Segunda onda trofoblástica destino anatômico zona de junção miometrial | resumos/GO/Síndromes Hipertensivas na Gestação.md | resumos/GO/[OBS] Sífilis na Gestação e Congênita.md<br>resumos/GO/[GIN] Climatério e TH.md<br>resumos/GO/[GIN] Sangramento Uterino Anormal.md |
| `ped-001` | 1 | Pediatria | Listeria monocytogenes sepse neonatal LA marrom exantema monocitose | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Cuidados Neonatais.md<br>resumos/Pediatria/Icterícia e Sepse Neonatal.md |
| `ped-002` | 3 | Pediatria | RN taquipneia isolada primeiras 6 horas conduta watchful waiting | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Emergências Pediátricas.md<br>resumos/Pediatria/Cuidados Neonatais.md<br>resumos/Pediatria/Icterícia e Sepse Neonatal.md |
| `cir-001` | 1 | Cirurgia | Pneumotórax hipertensivo punção agulhada vs dreno pleural localização 5º EIC | resumos/Cirurgia/[CIR] Trauma.md | resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[ORL] Neoplasias, Congênitas e Traqueostomia.md |
| `cir-002` | 1 | Cirurgia | Trauma pancreático AAST III conduta cirúrgica vs CPRE | resumos/Cirurgia/[CIR] Trauma.md | resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[CIR] Trauma.md |
| `cm-001` | 1 | Clínica Médica | Necrosectomia pancreática timing walled-off 4-6 semanas | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md<br>resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md<br>resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md |
| `cm-002` | 1 | Clínica Médica | Fundoplicatura Nissen vs Toupet em Barrett papel oncológico | resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md | resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md<br>resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md<br>resumos/Clínica Médica/Infectologia/Arboviroses.md |
| `cm-003` | 1 | Clínica Médica | MEEM normal 29/30 paciente alta escolaridade diagnóstico demência AVDs | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Neurologia/Demências.md<br>resumos/Clínica Médica/Neurologia/Demências.md<br>resumos/Clínica Médica/Neurologia/Demências.md |
| `cm-004` | 2 | Clínica Médica | CADASIL demência hereditária vascular AVC familiar tríade | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Nefrologia/Lesão Renal Aguda.md<br>resumos/Clínica Médica/Neurologia/Demências.md<br>resumos/Clínica Médica/Neurologia/Demências.md |
| `ped-003` | 1 | Pediatria | IOT em PCR pediátrica permite RCP contínua | resumos/Pediatria/Emergências Pediátricas.md | resumos/Pediatria/Emergências Pediátricas.md<br>resumos/Pediatria/Emergências Pediátricas.md<br>resumos/Pediatria/Emergências Pediátricas.md |
| `cm-005` | MISS | Clínica Médica | Hanseníase diagnóstico inicial estesiometria Semmes-Weinstein vs biópsia | resumos/Clínica Médica/Dermatologia/Hanseníase e Síndromes Verrucosas.md | resumos/Clínica Médica/Infectologia/Tuberculose.md<br>resumos/Clínica Médica/Neurologia/TCE.md<br>resumos/Clínica Médica/Infectologia/Tuberculose.md |
| `cm-006` | 1 | Clínica Médica | CAD transição insulina dose plena para reduzida 0.02-0.05 UI/kg/h adição SG | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus Tipo 2.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md |
| `go-005` | 2 | GO | Lesão genital maior que 4 semanas cobertura sindrômica 4 agentes | resumos/GO/Úlceras Genitais.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/Úlceras Genitais.md<br>resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md |
| `go-006` | 1 | GO | Coleta endocervical em gestante rastreamento colo do útero | resumos/GO/[GIN] Rastreamento Colo.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/Assistência ao Parto.md<br>resumos/GO/[GIN] Rastreamento Colo.md |

### hyde=off

| id | rank | area | query | expected | top-3 sources |
|---|---:|---|---|---|---|
| `go-001` | 1 | GO | Cancro mole vs LGV diagnóstico diferencial orifício único bico de regador | resumos/GO/Úlceras Genitais.md | resumos/GO/Úlceras Genitais.md |
| `go-002` | 3 | GO | Quando iniciar supressão de herpes na gestação 36 semanas | resumos/GO/Úlceras Genitais.md | resumos/GO/Síndromes Hipertensivas na Gestação.md<br>resumos/GO/[GIN] CA de Mama.md<br>resumos/GO/Úlceras Genitais.md |
| `pre-001` | MISS | Preventiva | Preenchimento da DO causas de morte Parte I e Parte II | resumos/Preventiva/Sistemas de Informação em Saúde.md | resumos/Preventiva/Medidas de Saúde Coletiva.md<br>resumos/Preventiva/Medidas de Saúde Coletiva.md<br>resumos/Preventiva/Medidas de Saúde Coletiva.md |
| `go-003` | MISS | GO | Eclâmpsia com convulsão ativa primeira conduta via aérea ou MgSO4 | resumos/GO/Síndromes Hipertensivas na Gestação.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[GIN] Doenças Benignas da Mama.md |
| `go-004` | 8 | GO | Segunda onda trofoblástica destino anatômico zona de junção miometrial | resumos/GO/Síndromes Hipertensivas na Gestação.md | resumos/GO/[GIN] Climatério e TH.md<br>resumos/GO/[GIN] Sangramento Uterino Anormal.md<br>resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md |
| `ped-001` | 1 | Pediatria | Listeria monocytogenes sepse neonatal LA marrom exantema monocitose | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Icterícia e Sepse Neonatal.md |
| `ped-002` | 1 | Pediatria | RN taquipneia isolada primeiras 6 horas conduta watchful waiting | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Cardiopatias Congênitas.md |
| `cir-001` | 1 | Cirurgia | Pneumotórax hipertensivo punção agulhada vs dreno pleural localização 5º EIC | resumos/Cirurgia/[CIR] Trauma.md | resumos/Cirurgia/[CIR] Trauma.md |
| `cir-002` | MISS | Cirurgia | Trauma pancreático AAST III conduta cirúrgica vs CPRE | resumos/Cirurgia/[CIR] Trauma.md | _(none)_ |
| `cm-001` | MISS | Clínica Médica | Necrosectomia pancreática timing walled-off 4-6 semanas | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md | _(none)_ |
| `cm-002` | MISS | Clínica Médica | Fundoplicatura Nissen vs Toupet em Barrett papel oncológico | resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md | _(none)_ |
| `cm-003` | 1 | Clínica Médica | MEEM normal 29/30 paciente alta escolaridade diagnóstico demência AVDs | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Neurologia/Demências.md<br>resumos/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md<br>resumos/Clínica Médica/Pneumologia/Asma.md |
| `cm-004` | MISS | Clínica Médica | CADASIL demência hereditária vascular AVC familiar tríade | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Hematologia/Hemostasia.md |
| `ped-003` | MISS | Pediatria | IOT em PCR pediátrica permite RCP contínua | resumos/Pediatria/Emergências Pediátricas.md | _(none)_ |
| `cm-005` | MISS | Clínica Médica | Hanseníase diagnóstico inicial estesiometria Semmes-Weinstein vs biópsia | resumos/Clínica Médica/Dermatologia/Hanseníase e Síndromes Verrucosas.md | resumos/Clínica Médica/Neurologia/Demências.md |
| `cm-006` | 1 | Clínica Médica | CAD transição insulina dose plena para reduzida 0.02-0.05 UI/kg/h adição SG | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md |
| `go-005` | 5 | GO | Lesão genital maior que 4 semanas cobertura sindrômica 4 agentes | resumos/GO/Úlceras Genitais.md | resumos/GO/[OBS] Sangramentos da Primeira Metade.md<br>resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md |
| `go-006` | 1 | GO | Coleta endocervical em gestante rastreamento colo do útero | resumos/GO/[GIN] Rastreamento Colo.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md<br>resumos/GO/[GIN] Rastreamento Colo.md |

## Honest caveats

- n=18 → ~22pp 95% binomial CI; point estimates are noisy.
- Gold set is author-defined and not blind.
- Measures file-level recall, not section-level. A correct file at the wrong chunk still counts as a hit.
- No retrieval→generation end-to-end signal. No latency, no cost.
- Cited folklore numbers (Recall@5 ≈ 0.90 / MRR ≈ 0.708) were measured against an unknown fixture by an unknown procedure; this report supersedes them, it does not confirm them.
