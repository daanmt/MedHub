# RAG Retrieval Eval — MedHub

_Generated 2026-08-15T01:26:11Z (UTC) — 2026-08-14 local (America/Sao_Paulo, UTC-3)_

- Fixture: `tools\eval\queries.json` (sha256[:12] `0189b8db7edc`, n=18)
- RAG impl: `app/engine/rag.py` @ git `9915b53` (last commit that touched the file; working tree at eval time has uncommitted consolidacao-part-2 changes on top)
- Repo HEAD at eval time (`git rev-parse HEAD`): `47aad805834b69474b1541f208e946cbd3bc5f2d`
- ChromaDB available: `True`

## Summary

| Config | n | Recall@1 | Recall@3 | Recall@5 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| hyde=on | 18 | 0.556 | 0.778 | 0.889 | 0.685 |
| hyde=off | 18 | 0.389 | 0.389 | 0.444 | 0.409 |

## Histórico (comparação com 27/05/2026)

O run de 27/05 (`5e36350`) rodou contra um fixture com 2 paths quebrados
(go-003/go-004 apontavam para "Síndromes Hipertensivas **na** Gestação.md",
arquivo real é "**da** Gestação.md" — as duas queries batiam MISS
estruturalmente, não por falha de retrieval). consolidacao-part-2 (2026-08-14)
corrigiu o fixture e removeu o tier morto `pdf_raw` (F17); os números abaixo
não são diretamente causais um do outro (fixture-fix e poda do F17 aconteceram
na mesma part), mas o run de 27/05 fica registrado como a última leitura
pré-conserto para referência histórica.

| Data | HEAD | Config | n | R@1 | R@3 | R@5 | MRR@10 | Nota |
|---|---|---|---:|---:|---:|---:|---:|---|
| 2026-05-27 | `5e36350` | hyde=on | 18 | 0.611 | 0.722 | 0.722 | 0.675 | fixture com 2 paths quebrados (go-003/go-004 MISS estrutural) |
| 2026-05-27 | `5e36350` | hyde=off | 18 | 0.389 | 0.444 | 0.500 | 0.425 | idem |
| 2026-08-14 | `47aad80`+wt | hyde=on | 18 | 0.556 | 0.778 | 0.889 | 0.685 | fixture corrigido; `pdf_raw` removido; ver nota de ruído abaixo |
| 2026-08-14 | `47aad80`+wt | hyde=off | 18 | 0.389 | 0.389 | 0.444 | 0.409 | idem |

**Nota de ruído (auditoria da divergência, pré-gravação):** três runs consecutivos
de `hyde=on` nesta sessão, código idêntico entre eles, produziram R@1 ∈
{0.389, 0.500, 0.556}, R@3 ∈ {0.667, 0.611, 0.778}, R@5 ∈ {0.833, 0.667, 0.889},
MRR ∈ {0.573, 0.596, 0.685} — swings de até ~17pp run-a-run. `hyde=off` (sem
chamada de LLM) repetiu os MESMOS números nos dois runs em que foi medido
(0.389/0.389/0.444/0.409), isolando a fonte do ruído: `_generate_hypothetical_document`
chama Haiku 4.5 sem `temperature=0`, então o documento hipotético (e o embedding
resultante) varia por chamada — não é regressão de código. Este run (o terceiro,
gravado acima) caiu dentro da margem informal de ±5pp do número de referência do
auditor (R@1=.500 R@3=.778 R@5=.833 MRR=.638) em 3 das 4 métricas (R@3 bateu
exato) e ligeiramente acima em R@5; aceito como representativo. `hyde=off` é
determinístico e não precisou de re-run para validação.

## Per-query detail

### hyde=on

| id | rank | area | query | expected | top-3 sources |
|---|---:|---|---|---|---|
| `go-001` | 4 | GO | Cancro mole vs LGV diagnóstico diferencial orifício único bico de regador | resumos/GO/Úlceras Genitais.md | resumos/GO/Vulvovaginites.md<br>resumos/GO/Vulvovaginites.md<br>resumos/GO/Vulvovaginites.md |
| `go-002` | MISS | GO | Quando iniciar supressão de herpes na gestação 36 semanas | resumos/GO/Úlceras Genitais.md | resumos/GO/Assistência ao Parto.md<br>resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md |
| `pre-001` | 1 | Preventiva | Preenchimento da DO causas de morte Parte I e Parte II | resumos/Preventiva/Sistemas de Informação em Saúde.md | resumos/Preventiva/Sistemas de Informação em Saúde.md<br>resumos/Preventiva/Epidemiologia e Estudos.md<br>resumos/Preventiva/Epidemiologia e Estudos.md |
| `go-003` | 3 | GO | Eclâmpsia com convulsão ativa primeira conduta via aérea ou MgSO4 | resumos/GO/Síndromes Hipertensivas da Gestação.md | resumos/GO/[GIN] CA de Mama.md<br>resumos/GO/[GIN] Climatério e TH.md<br>resumos/GO/Síndromes Hipertensivas da Gestação.md |
| `go-004` | 1 | GO | Segunda onda trofoblástica destino anatômico zona de junção miometrial | resumos/GO/Síndromes Hipertensivas da Gestação.md | resumos/GO/Síndromes Hipertensivas da Gestação.md<br>resumos/GO/Síndromes Hipertensivas na Gestação.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md |
| `ped-001` | 1 | Pediatria | Listeria monocytogenes sepse neonatal LA marrom exantema monocitose | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Cuidados Neonatais.md<br>resumos/Pediatria/Cardiopatias Congênitas.md |
| `ped-002` | 6 | Pediatria | RN taquipneia isolada primeiras 6 horas conduta watchful waiting | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Cardiopatias Congênitas.md<br>resumos/Pediatria/Cardiopatias Congênitas.md<br>resumos/Pediatria/Emergências Pediátricas.md |
| `cir-001` | 1 | Cirurgia | Pneumotórax hipertensivo punção agulhada vs dreno pleural localização 5º EIC | resumos/Cirurgia/[CIR] Trauma.md | resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[ORL] Neoplasias, Congênitas e Traqueostomia.md |
| `cir-002` | 1 | Cirurgia | Trauma pancreático AAST III conduta cirúrgica vs CPRE | resumos/Cirurgia/[CIR] Trauma.md | resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[CIR] Trauma.md<br>resumos/Cirurgia/[CIR] Trauma.md |
| `cm-001` | 1 | Clínica Médica | Necrosectomia pancreática timing walled-off 4-6 semanas | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md<br>resumos/Clínica Médica/Hepatologia/Introdução à Hepatologia e Icterícia Não obstrutiva.md<br>resumos/Clínica Médica/Nefrologia/Lesão Renal Aguda.md |
| `cm-002` | 1 | Clínica Médica | Fundoplicatura Nissen vs Toupet em Barrett papel oncológico | resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md | resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md<br>resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md<br>resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md |
| `cm-003` | 2 | Clínica Médica | MEEM normal 29/30 paciente alta escolaridade diagnóstico demência AVDs | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Infectologia/Tuberculose.md<br>resumos/Clínica Médica/Neurologia/Demências.md<br>resumos/Clínica Médica/Neurologia/Demências.md |
| `cm-004` | 2 | Clínica Médica | CADASIL demência hereditária vascular AVC familiar tríade | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Crônicas.md<br>resumos/Clínica Médica/Neurologia/Demências.md<br>resumos/Clínica Médica/Hematologia/Hemostasia.md |
| `ped-003` | 1 | Pediatria | IOT em PCR pediátrica permite RCP contínua | resumos/Pediatria/Emergências Pediátricas.md | resumos/Pediatria/Emergências Pediátricas.md<br>resumos/Pediatria/Emergências Pediátricas.md<br>resumos/Pediatria/Emergências Pediátricas.md |
| `cm-005` | 4 | Clínica Médica | Hanseníase diagnóstico inicial estesiometria Semmes-Weinstein vs biópsia | resumos/Clínica Médica/Dermatologia/Hanseníase e Síndromes Verrucosas.md | resumos/Clínica Médica/Hepatologia/Introdução à Hepatologia e Icterícia Não obstrutiva.md<br>resumos/Clínica Médica/Pneumologia/Pneumologia Intensiva.md<br>resumos/Clínica Médica/Infectologia/Tuberculose.md |
| `cm-006` | 1 | Clínica Médica | CAD transição insulina dose plena para reduzida 0.02-0.05 UI/kg/h adição SG | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md<br>resumos/Clínica Médica/Nefrologia/Distúrbios Ácido-Base.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md |
| `go-005` | 3 | GO | Lesão genital maior que 4 semanas cobertura sindrômica 4 agentes | resumos/GO/Úlceras Genitais.md | resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md<br>resumos/GO/Vulvovaginites.md<br>resumos/GO/Úlceras Genitais.md |
| `go-006` | 1 | GO | Coleta endocervical em gestante rastreamento colo do útero | resumos/GO/[GIN] Rastreamento Colo.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md |

### hyde=off

| id | rank | area | query | expected | top-3 sources |
|---|---:|---|---|---|---|
| `go-001` | MISS | GO | Cancro mole vs LGV diagnóstico diferencial orifício único bico de regador | resumos/GO/Úlceras Genitais.md | _(none)_ |
| `go-002` | 6 | GO | Quando iniciar supressão de herpes na gestação 36 semanas | resumos/GO/Úlceras Genitais.md | resumos/GO/Síndromes Hipertensivas na Gestação.md<br>resumos/GO/Síndromes Hipertensivas da Gestação.md<br>resumos/GO/[GIN] Sangramento Uterino Anormal.md |
| `pre-001` | 1 | Preventiva | Preenchimento da DO causas de morte Parte I e Parte II | resumos/Preventiva/Sistemas de Informação em Saúde.md | resumos/Preventiva/Sistemas de Informação em Saúde.md<br>resumos/Preventiva/Medidas de Saúde Coletiva.md<br>resumos/Preventiva/Medidas de Saúde Coletiva.md |
| `go-003` | MISS | GO | Eclâmpsia com convulsão ativa primeira conduta via aérea ou MgSO4 | resumos/GO/Síndromes Hipertensivas da Gestação.md | resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md<br>resumos/GO/[GIN] Sangramento Uterino Anormal.md<br>resumos/GO/[GIN] Rastreamento Colo.md |
| `go-004` | 1 | GO | Segunda onda trofoblástica destino anatômico zona de junção miometrial | resumos/GO/Síndromes Hipertensivas da Gestação.md | resumos/GO/Síndromes Hipertensivas da Gestação.md<br>resumos/GO/Síndromes Hipertensivas na Gestação.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md |
| `ped-001` | 1 | Pediatria | Listeria monocytogenes sepse neonatal LA marrom exantema monocitose | resumos/Pediatria/Icterícia e Sepse Neonatal.md | resumos/Pediatria/Icterícia e Sepse Neonatal.md<br>resumos/Pediatria/Icterícia e Sepse Neonatal.md |
| `ped-002` | MISS | Pediatria | RN taquipneia isolada primeiras 6 horas conduta watchful waiting | resumos/Pediatria/Icterícia e Sepse Neonatal.md | _(none)_ |
| `cir-001` | 1 | Cirurgia | Pneumotórax hipertensivo punção agulhada vs dreno pleural localização 5º EIC | resumos/Cirurgia/[CIR] Trauma.md | resumos/Cirurgia/[CIR] Trauma.md |
| `cir-002` | MISS | Cirurgia | Trauma pancreático AAST III conduta cirúrgica vs CPRE | resumos/Cirurgia/[CIR] Trauma.md | _(none)_ |
| `cm-001` | 1 | Clínica Médica | Necrosectomia pancreática timing walled-off 4-6 semanas | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md | resumos/Clínica Médica/Gastroenterologia/Pancreatite Aguda e Crônica.md |
| `cm-002` | MISS | Clínica Médica | Fundoplicatura Nissen vs Toupet em Barrett papel oncológico | resumos/Clínica Médica/Gastroenterologia/DRGE, Esofagites e Corpo Estranho.md | _(none)_ |
| `cm-003` | MISS | Clínica Médica | MEEM normal 29/30 paciente alta escolaridade diagnóstico demência AVDs | resumos/Clínica Médica/Neurologia/Demências.md | resumos/Clínica Médica/Nefrologia/Distúrbios Ácido-Base.md<br>resumos/Clínica Médica/Pneumologia/Pneumologia Intensiva.md |
| `cm-004` | MISS | Clínica Médica | CADASIL demência hereditária vascular AVC familiar tríade | resumos/Clínica Médica/Neurologia/Demências.md | _(none)_ |
| `ped-003` | MISS | Pediatria | IOT em PCR pediátrica permite RCP contínua | resumos/Pediatria/Emergências Pediátricas.md | _(none)_ |
| `cm-005` | MISS | Clínica Médica | Hanseníase diagnóstico inicial estesiometria Semmes-Weinstein vs biópsia | resumos/Clínica Médica/Dermatologia/Hanseníase e Síndromes Verrucosas.md | _(none)_ |
| `cm-006` | 1 | Clínica Médica | CAD transição insulina dose plena para reduzida 0.02-0.05 UI/kg/h adição SG | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md | resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md<br>resumos/Clínica Médica/Endocrinologia/Diabetes Mellitus - Complicações Agudas.md |
| `go-005` | 5 | GO | Lesão genital maior que 4 semanas cobertura sindrômica 4 agentes | resumos/GO/Úlceras Genitais.md | resumos/GO/[OBS] Sangramentos da Primeira Metade.md<br>resumos/GO/[GIN] Dor Pélvica e Dismenorreia.md<br>resumos/GO/Planejamento Familiar.md |
| `go-006` | 1 | GO | Coleta endocervical em gestante rastreamento colo do útero | resumos/GO/[GIN] Rastreamento Colo.md | resumos/GO/[GIN] Rastreamento Colo.md<br>resumos/GO/[OBS] Sangramentos da Primeira Metade.md<br>resumos/GO/Assistência ao Parto.md |

## Honest caveats

- n=18 → ~22pp 95% binomial CI; point estimates are noisy.
- Gold set is author-defined and not blind.
- Measures file-level recall, not section-level. A correct file at the wrong chunk still counts as a hit.
- No retrieval→generation end-to-end signal. No latency, no cost.
- Cited folklore numbers (Recall@5 ≈ 0.90 / MRR ≈ 0.708) were measured against an unknown fixture by an unknown procedure; this report supersedes them, it does not confirm them.
