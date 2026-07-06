# PRD: Pipeline de Conhecimento -- Cobertura, RAG Two-Tier e Piso de Cobertura (Ciclo 3)

> Gerado via /vibeflow:discover em 2026-07-06 (ciclo 3 de engenharia delegada, Fable/ai-eng).
> Fonte: ledger F16-F19 (s109, secao 3c) + F21 (secao 3e) + F27/F28 (audits do ciclo 2, secao 3g)
> + parecer arquitetural batido com o operador no chat (2026-07-05/06). O operador leu o parecer
> e mandou gerar o PRD -- as decisoes recomendadas entram como base; redirecionamento e possivel
> ate o gen-spec. Encoding ASCII limpo (AGENTE.md secao 4.5).
> **STATUS: PRD pronto; gen-spec -> implement -> audit AGUARDAM go do operador.**

## Problema

O conhecimento clinico do MedHub tem um degrau manual invisivel no meio do pipeline:
`PDF-fonte -> [extracao manual] -> .md -> RAG -> aula efemera`. Consequencias verificadas:

1. **Cobertura cega (F16).** 333 PDFs-fonte vs 62 `.md` cunhados (censo 2026-07-05). O RAG
   (ChromaDB + nomic-embed-text) indexa APENAS os `.md` -- ~270 temas invisiveis a busca.
   Apendicite ("um dos temas mais cobrados de Cirurgia") so foi coberta porque a s109
   extraiu o PDF a mao. Nao existe check sistematico de que temas de alto rendimento tem
   SSOT; o gap so aparece quando o operador tropeca nele em prova.
2. **Intencao sem wiring (F17).** A decisao s086 reteve os PDFs "para alimentar o RAG",
   mas `index_resumos.py` so gloga `*.md` -- o PDF e IP retido sem retorno de busca.
   F17 e a causa-sistemica de F16 existir silenciosamente.
3. **Sinal caro descartado (F18).** A aula-base e artefato validado (cobertura 53%->75%)
   e caro de produzir; hoje e chat-only -- re-forjada do zero a cada vez -- e a nota de
   dificuldade que a calibrou nao e registrada (`taxonomia_cronograma.dificuldade`
   intocada), desperdicando o insumo da Revisao Calibrada.
4. **Compressao que corta ponto de prova (F21).** O degrau de descompressao (D10->D7)
   ELIMINOU um ponto de decisao testavel (ileotiflectomia) em vez de encurta-lo -- e a Q2
   da s109 caiu exatamente ali. A regra "profundidade calibra, cobertura nao" existe em
   memoria/AGENTE mas nao esta operacionalizada no render da aula.
5. **Residuos do ciclo 2 (F27/F28).** Modo single do `insert_questao` sai com exit 0 em
   falha (docstring promete 1); o arg `--elo` (required) nao tem coluna propria -- o campo
   canonico de fato e `o_que_faltou`, mas isso nao esta documentado em lugar nenhum.

Quem sofre: o operador (estuda com RAG cego a 80% das fontes; perde ponto de prova por
corte de compressao) e o agente-coordenador (re-extrai PDF a mao; re-forja aula; calibra
sem registrar).

## Publico-alvo

- **Primario:** o agente-coordenador de sessao (consome RAG/get_topic_context para aulas,
  refresh e curadoria; conduz o fluxo de aula calibrada).
- **Secundario e beneficiario final:** o operador (Daniel) -- busca que cobre o corpus
  inteiro, aula que nunca corta ponto de prova, calibracao que acumula.

## Solucao proposta

Fechar o pipeline com o `.md` como CANON e o PDF como tier bruto marcado -- mesma
epistemologia do pipeline web do ai-eng (quarentena nunca vira canon por existir). Quatro ondas:

- **Onda 1 -- Relatorio de cobertura (F16a).** CLI `tools/cobertura_conhecimento.py`
  (nome indicativo): cruza `resumos/**/*.pdf` contra `resumos/**/*.md` (match por stem
  normalizado + fuzzy leve; o pareamento exato e pessimista -- 332/333 orfaos no censo cru),
  prioriza os orfaos por sinal de rendimento (presenca na grade do cronograma via
  `cronograma.py` + `taxonomia_cronograma` volume/erros) e emite a fila de autoria
  ordenada. Opcional: WARN agregado no `auto_check --all` (politica s106/107) quando um
  tema da SEMANA CORRENTE nao tem `.md`.
- **Onda 2 -- RAG two-tier (F17).** Extracao automatica do texto dos PDFs (reusa
  `extract_pdfs.py`/pdfplumber) -> collection SEPARADA no Chroma (`pdf_raw`) com metadado
  de origem; `rag.search` (ou wrapper no engine) consulta o gold primeiro e cai no tier
  bruto como **fallback marcado** (`source=pdf_raw` visivel no resultado; o agente trata
  como nao-curado). O `.md` cunhado passa a sombrear o PDF do mesmo tema (dedupe por tema
  no fallback). Indexacao incremental (so PDFs novos/mudados) + `--clear` por collection.
  NADA no gold muda: chunking, collection e qualidade atuais intocados.
- **Onda 3 -- Materializar o sinal da aula (F18c + F21).** (a) Clausula no fluxo de aula
  (AGENTE/skill correspondente + contrato): a nota 1-10 usada para calibrar a descompressao
  e REGISTRADA no ato via `db.set_dificuldade` (schema ja existe; fonte='aula'). (b) Clausula
  F21 no `revisao-calibrada-contract` (+ espelho command<->skill via sync_skills): a nota
  calibra descompressao/prosa; a COBERTURA de pontos de decisao de alto rendimento e piso
  fixo por tema, derivado do sumario da fonte (precedente s089) -- mesmo em D2 o render
  passa pelo checklist antes de fechar. Operacionalizacao mecanica do checklist amadurece
  com a cobertura da Onda 1-2 (sem `.md`/sumario nao ha de onde derivar o piso -- registrar
  a dependencia, nao bloquear a clausula).
- **Onda 4 -- Residuos (F27 + F28).** `sys.exit(0 if ok else 1)` no modo single do
  `insert_questao` (conferindo antes se algum chamador/hook depende do exit 0 atual);
  documentar no workflow `analisar-questao` que o campo canonico do elo e `o_que_faltou`
  (o arg `--elo` permanece -- e consumido pelo matcher F25 -- SEM coluna nova).

## Criterios de sucesso

Binarios e observaveis:

1. O CLI de cobertura emite: total de PDFs, total de `.md`, lista de orfaos ORDENADA por
   rendimento, e os temas da semana corrente sem `.md` destacados. Numeros batem com
   fixture (db+arvore temp) e com o censo real na primeira execucao. (F16a)
2. Match de pareamento tolera diferencas de naming (numero-prefixo do EMED, acentos,
   case); fixture cobre par verdadeiro com nomes diferentes e nao-par. (F16a)
3. Pos-indexacao da Onda 2: busca por tema SEM `.md` (ex.: um tema orfao real) retorna
   chunks com `source=pdf_raw` marcado; busca por tema COM `.md` retorna o gold SEM
   contaminacao do tier bruto (dedupe/sombreamento verificado). (F17)
4. `index_resumos.py` (ou CLI dedicado) indexa o tier bruto de forma incremental; re-rodar
   sem mudancas nao re-embedda (custo zero na re-execucao); `--clear` limpa so a collection
   alvo. Gold byte-identico ao atual. (F17)
5. Fluxo de aula registra a dificuldade no ato: apos uma aula calibrada, `taxonomia_cronograma
   .dificuldade` reflete a nota com fonte rastreavel; teste cobre o caminho de registro. (F18c)
6. Clausula F21 presente no contrato canonico + espelho em paridade (`sync_skills --check`
   passa); o texto separa explicitamente descompressao (calibravel) de cobertura (piso fixo)
   e aponta o sumario da fonte como origem do checklist. (F21)
7. `insert_questao` modo single: falha -> exit 1 (teste); sucesso -> exit 0; nenhum chamador
   existente quebra (grep de invocacoes + auto_check verde). (F27)
8. Workflow `analisar-questao` documenta `o_que_faltou` como campo canonico do elo; nenhum
   schema alterado. (F28)
9. Regressao: `pytest` verde (36+ passed), standalone preservados, `auto_check --staged`
   verde; RAG gold e fila FSRS byte-identicos sem as flags/CLIs novos.

## Escopo v0

Ondas 1-4 acima. Ordem: 1 -> 2 -> 3 -> 4 (a Onda 3b depende conceitualmente da cobertura
para o checklist mecanico, mas a CLAUSULA entra ja; Onda 4 e independente/carona).
Decisoes ja tomadas (parecer 07-06, base deste PRD): two-tier com `.md` canon (nao indexar
PDF como fonte primaria); aula = render efemero do `.md` (nao persistir aula como artefato);
F28 = documentacao, nao coluna.

## Anti-escopo

Explicito e agressivo -- NADA disto entra neste ciclo:

- **Autoria de conteudo clinico** (ex.: `Apendicite Aguda.md`) -- e trilha do coordenador
  via `criar-resumo` (a aula-base da s109 e o insumo); o CLI da Onda 1 apenas PRIORIZA.
- **F19 (prova-alvo de primeira classe)** -- mantido com gate de recorrencia (2a prova
  paralela formal -> vira PRD proprio). Antecipar so por decisao explicita do operador.
- **Mudar o chunking/collection/qualidade do RAG gold** -- o tier bruto e ADITIVO.
- **Embeddings/modelos novos ou dependencias novas** -- usa nomic-embed-text + ChromaDB +
  pdfplumber ja presentes. (Ollama vivo e pre-condicao operacional da Onda 2.)
- **Coluna nova de schema** (F28 resolvido por documentacao; unica mudanca de schema do
  ciclo 2 -- `status` -- permanece a unica).
- **UI Streamlit** -- tudo CLI/contrato/engine.
- **Persistir a aula como artefato proprio** -- decisao F18: o `.md` e a forma duravel.
- **Reforge dos cards 95/120** -- agente-player (/curar-cards; 120 via gate de evidencia,
  pode usar `--status banca-divergente`).

## Contexto tecnico

O que ja existe e a solucao REUSA:

- `tools/extract_pdfs.py` (pdfplumber; politica Zero PDF do fluxo antigo -- aqui a extracao
  vira insumo de indexacao, sem deletar a fonte) · `app/engine/rag.py` (`index_all`, `search`,
  `_CHROMA_AVAILABLE`, fallback silencioso se Ollama offline) · `tools/index_resumos.py`
  (CLI de indexacao gold) · `data/chroma/` local-only.
- `tools/cronograma.py` (grade/semana) + `preparacao_estado` (posicao SSOT, ciclo 2) --
  sinal de "tema da semana sem .md" e derivavel.
- `db.set_dificuldade` + campos `dificuldade/dificuldade_fonte/dificuldade_at` (Revisao
  Calibrada, ja em producao) -- Onda 3a e clausula + chamada, zero schema.
- `core/contracts/revisao-calibrada-contract.md` + `sync_skills.py --check` (paridade
  command<->skill; precedente do ciclo 1 Onda 3).
- Padroes vibeflow: `db-access-layer`, `domain-engine-api` (RAG via engine), `brain-query`
  -- e a epistemologia two-tier do ai-eng (ADR-002: bruto/quarentena nunca vira canon
  por existir; promocao e ato curado).
- Restricoes: sqlite3 confinado; ASCII; `data/chroma/` e `ipub.db` local-only; armadilhas
  cumulativas; encoding AGENTE 4.5.

## Perguntas em aberto

- **Volume da 1a indexacao pdf_raw** (333 PDFs x chunks x embedding local): medir tempo na
  spec (estimativa: minutos, one-shot); se custoso, indexar por area sob demanda comecando
  pela semana corrente. Nao bloqueia o design.
- **Limiar do WARN de cobertura no auto_check** (so semana corrente vs top-N rendimento):
  default conservador (semana corrente) na spec; ajustavel por uso.
- **F19 antecipado?** Default: gate mantido. Se UERJ/USP/IPUB virarem alvos formais antes
  da recorrencia, operador sinaliza e vira +1 spec.
