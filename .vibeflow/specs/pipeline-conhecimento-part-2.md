# Spec: Pipeline de Conhecimento -- Parte 2: RAG Two-Tier (Onda 2 / F17)

> Derivado de `.vibeflow/prds/pipeline-conhecimento.md` (Onda 2). Encoding ASCII (AGENTE 4.5).
> Parte 2 de 4. Independente das demais. Ollama vivo e pre-condicao operacional.

## Objetivo

Fazer a busca semantica cobrir o corpus INTEIRO: temas que so tem PDF-fonte (sem `.md`)
passam a retornar chunks marcados como nao-curados (`source=pdf_raw`), sem contaminar o
tier gold e sem tocar em nada da qualidade atual do RAG.

## Contexto

`app/engine/rag.py` indexa `resumos/**/*.md` na collection `resumos` (ChromaDB +
nomic-embed-text via Ollama). A decisao s086 reteve os PDFs "para alimentar o RAG", mas o
wiring nunca existiu (F17) -- causa-sistemica de F16. `tools/extract_pdfs.py` (pdfplumber +
PyPDF2 fallback) ja extrai texto de PDF. A epistemologia alvo e a two-tier do ai-eng
(ADR-002): o bruto/quarentena NUNCA vira canon por existir -- o `.md` cunhado e a promocao
curada e deve SOMBREAR o PDF do mesmo tema.

## Definition of Done

Binarios (pass/fail):

1. Existe indexacao do tier bruto numa collection SEPARADA (`pdf_raw`) no mesmo
   `data/chroma/`, com metadado `source=pdf_raw` e origem do PDF em cada chunk. O gold
   (collection `resumos`) permanece byte-identico: chunking, IDs, metadados e qualidade
   intocados.
2. Indexacao incremental: re-rodar sem PDFs novos/alterados NAO re-embedda (custo zero na
   re-execucao); `--clear` limpa SOMENTE a collection `pdf_raw`, nunca o gold.
3. A busca do engine consulta o gold primeiro e cai no `pdf_raw` como **fallback marcado**:
   quando o resultado vem do tier bruto, o chamador ve `source=pdf_raw` (agente trata como
   nao-curado). Busca por tema COM `.md` retorna o gold SEM chunks do tier bruto do mesmo
   tema (dedupe/sombreamento por tema).
4. Teste (`tools/test_rag_two_tier.py`) cobre: (a) busca por tema orfao retorna chunk
   marcado `pdf_raw`; (b) busca por tema com `.md` nao traz `pdf_raw` do mesmo tema
   (sombreamento); (c) incremental nao re-embedda PDF inalterado. Verde com fallback quando
   Chroma/Ollama offline (skip/gracioso, nunca raise).
5. **Craftsmanship:** o tier bruto e ADITIVO -- nenhuma assinatura publica existente de
   `rag.py` (`search`, `index_all`, `_CHROMA_AVAILABLE`) muda comportamento no caminho gold;
   sem dependencia nova (reusa pdfplumber/ChromaDB/nomic ja presentes); fallback silencioso
   mantido (Ollama offline -> `[]`, nunca excecao); ASCII limpo.
6. `data/chroma/` permanece local-only (gitignored); nenhum PDF e deletado pela indexacao.

## Escopo

- `app/engine/rag.py`: funcoes de indexacao do tier bruto (nova collection `pdf_raw`,
  extracao via `extract_pdfs`, chunking reusando `_chunk_by_headers` ou equivalente simples
  para texto plano) + wrapper de busca two-tier (gold-primeiro, fallback marcado, dedupe por
  tema). Caminho gold existente nao muda.
- CLI de indexacao do tier bruto: novo `tools/index_pdf_raw.py` (espelha o padrao de
  `index_resumos.py`: argparse, `--dir`, `--clear`, exit codes, saida legivel).
- `tools/test_rag_two_tier.py` (novo).

## Anti-escopo

- **Mudar chunking / collection / qualidade do gold** -- proibido; tier bruto e paralelo.
- **Embeddings ou modelos novos** -- nomic-embed-text + ChromaDB + pdfplumber, nada mais.
- **Promover PDF a canon** -- `pdf_raw` nunca vira gold por existir; promocao e o ato de
  cunhar o `.md` (trilha do coordenador, fora deste ciclo).
- **UI Streamlit / biblioteca** -- tudo engine/CLI.
- **Deletar PDFs** -- a fonte permanece (politica revertida s086).

## Decisoes tecnicas

- **Collection separada `pdf_raw`, nao flag de metadado na mesma collection.** Isola o bruto
  fisicamente: `--clear` do bruto nao arrisca o gold, e o gold-primeiro e uma consulta
  ordenada de duas collections em vez de um filtro dentro de uma. Trade-off: duas queries no
  fallback vs isolamento forte -- o isolamento vence (protege o ativo curado).
- **Sombreamento por tema no fallback, nao no indice.** O PDF continua indexado mesmo com
  `.md` presente; o dedupe acontece na LEITURA (se o tema tem gold, descarta o `pdf_raw`
  daquele tema). Assim, cunhar/renomear um `.md` nao exige reindexar o bruto. Chave de tema:
  stem normalizado (mesma normalizacao da Parte 1, se disponivel; senao, local a este modulo).
- **Extracao reusa `extract_pdfs.extract_pdf`** para arquivo temp, le, indexa, limpa o temp
  (nao o PDF). Incremental por mtime/hash do PDF registrado no metadado do chunk -> pular
  PDFs inalterados.
- **Fallback so quando o gold nao satisfaz.** Definir o gatilho do fallback (ex.: gold
  retorna 0 hits acima do limiar, ou abaixo de N) na implementacao; default conservador:
  fallback complementa ate `n_results` quando o gold nao preenche.

## Applicable patterns

- `patterns/domain-engine-api.md` -- RAG via engine; assinaturas estaveis; fallback seguro.
- Conventions "RAG": sistema canonico `app/engine/rag.py` + `data/chroma/`; reindex via CLI.
- Padrao `index_resumos.py` para o novo CLI (`--clear` por collection, exit codes).
- Epistemologia two-tier do ai-eng (ADR-002): bruto nunca vira canon por existir.

## Riscos

- **Contaminacao do gold (pdf_raw vaza para busca de tema com `.md`).** E o risco central.
  Mitigacao: DoD #3 e o teste de sombreamento sao o gate; dedupe por tema testado
  explicitamente com par gold+bruto do mesmo tema.
- **Custo da 1a indexacao (333 PDFs x chunks x embedding local).** Mitigacao: medir na
  implementacao; se custoso, `--dir`/`--area` permite indexar sob demanda comecando pela
  semana corrente. Incremental garante que so a 1a rodada e cara.
- **PDF ruim (scan/imagem) sem texto extraivel.** Mitigacao: pdfplumber->PyPDF2 fallback ja
  existe; PDF sem texto e pulado com aviso, nao quebra a indexacao.
- **Ollama offline durante indexacao.** Mitigacao: CLI detecta (mesmo padrao de
  `index_resumos.py`) e sai com mensagem clara + exit 1; busca continua com fallback `[]`.
