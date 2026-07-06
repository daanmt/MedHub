# Spec: Pipeline de Conhecimento -- Parte 1: Relatorio de Cobertura (Onda 1 / F16a)

> Derivado de `.vibeflow/prds/pipeline-conhecimento.md` (Onda 1). Encoding ASCII (AGENTE 4.5).
> Parte 1 de 4. Independente das demais -- pode ser implementada e auditada sozinha.

## Objetivo

Dar ao agente-coordenador um CLI que revela quais temas de alto rendimento NAO tem SSOT
`.md`, ordenados por prioridade, para que a cegueira de cobertura (270+ temas invisiveis ao
RAG) deixe de aparecer so quando o operador tropeca nela em prova.

## Contexto

Censo 2026-07-05 (confirmado nesta sessao): **333 PDFs-fonte vs 62 `.md` cunhados** em
`resumos/`. O RAG (`app/engine/rag.py`) indexa APENAS `*.md`; os PDFs sao IP retido sem
retorno de busca. Nao existe check sistematico de que temas cobrados tem SSOT. O sinal de
"rendimento" de um tema e derivavel de duas fontes ja presentes: a grade do cronograma
(`tools/cronograma.py`) e a `taxonomia_cronograma` no `ipub.db` (volume/erros por tema).

## Definition of Done

Binarios (pass/fail):

1. `python tools/cobertura_conhecimento.py` roda e imprime: total de PDFs, total de `.md`,
   e a lista de PDFs-orfaos (sem `.md` pareado) ORDENADA por sinal de rendimento (grade da
   semana corrente > presenca na grade > volume/erros na taxonomia > alfabetica).
2. O pareamento PDF<->`.md` tolera diferencas de naming: prefixo numerico do EMED, acentos e
   case sao normalizados no match (stem normalizado + fuzzy leve); um par verdadeiro com
   nomes diferentes e reconhecido como coberto, um nao-par permanece orfao.
3. Os temas da SEMANA CORRENTE (via `cronograma.py`) sem `.md` sao destacados no topo do
   relatorio (secao propria), separados dos demais orfaos.
4. Teste `tools/test_cobertura.py` cobre, com fixture (arvore temp + db temp): (a) par
   verdadeiro com nomes divergentes reconhecido, (b) nao-par mantido orfao, (c) ordenacao
   por rendimento respeitada. `pytest tools/test_cobertura.py` verde.
5. **Craftsmanship:** CLI segue o padrao `db-access-layer` (zero `import sqlite3` fora de
   `db.py`; qualquer leitura de taxonomia passa por funcao de `db.py`) e o padrao de CLIs de
   `tools/` (argparse, `--dir` default `resumos`, path via `os.path.dirname`, saida legivel,
   exit 0/1). Sem dependencia nova. ASCII limpo.
6. Read-only: o CLI NAO cria, move ou deleta nenhum `.md`/`.pdf`; apenas relata.

## Escopo

- `tools/cobertura_conhecimento.py` (novo): varre `resumos/**/*.pdf` e `resumos/**/*.md`,
  normaliza stems, pareia, prioriza orfaos, imprime relatorio + secao "semana corrente".
- `tools/test_cobertura.py` (novo): fixtures de pareamento e ordenacao.
- Se necessario para leitura de taxonomia/rendimento: uma funcao de leitura em
  `app/utils/db.py` (read-only, retorna dict/DataFrame) -- so se ainda nao existir equivalente.

## Anti-escopo

- **Autoria de qualquer `.md` clinico** -- e trilha do coordenador via `criar-resumo`; este
  CLI apenas PRIORIZA a fila.
- **WARN no `auto_check --all`** -- fica para a Parte 3/uso posterior; nesta parte o
  relatorio e standalone (evita acoplar a Onda 1 ao hook antes da cobertura existir).
- **Indexar PDF no RAG** -- e a Parte 2.
- **Mudar schema** -- nenhuma coluna nova.
- **Deletar/mover arquivos** -- read-only estrito.

## Decisoes tecnicas

- **Match por stem normalizado + fuzzy leve, nao exato.** O pareamento exato e pessimista
  (332/333 orfaos no censo cru, por causa do prefixo numerico EMED e acentos). Normalizacao:
  strip de prefixo numerico, `unicodedata` para tirar acento, lower, colapso de espaco.
  Fuzzy leve (ex.: `difflib.SequenceMatcher` acima de um limiar) so como desempate -- sem
  dependencia nova (`difflib` e stdlib). Trade-off: fuzzy pode gerar falso-par; mitigado por
  limiar conservador e pelo fato de o output ser uma FILA priorizada revisada por humano,
  nao uma acao automatica.
- **Rendimento derivado, nao novo estado.** Prioridade lida de `cronograma.py` (grade/semana)
  + `taxonomia_cronograma` (volume/erros). Zero persistencia nova.
- **Sinal da semana corrente reusa `cronograma.py`/`preparacao_estado`** (posicao SSOT do
  ciclo 2) -- nao reimplementar deteccao de semana.

## Applicable patterns

- `patterns/db-access-layer.md` -- toda leitura de db via `db.py`; `sqlite3` so em `db.py`.
- Padrao de CLIs `tools/` (conventions.md secao "CLI tools"): argparse, exit codes, saida
  legivel, `finally: conn.close()`.
- Reuso de `tools/cronograma.py` (contrato `cronograma-contract.md`) para grade/semana.

## Riscos

- **Fuzzy gera falso-par (tema marcado coberto sem estar).** Mitigacao: limiar conservador;
  o relatorio lista tambem os pares fuzzy de baixa confianca numa coluna/secao "revisar
  pareamento" em vez de silenciar.
- **Cronograma indisponivel/sem semana corrente.** Mitigacao: degradar gracioso -- se
  `cronograma.py` nao retorna semana, a secao "semana corrente" sai vazia com aviso e o
  relatorio geral (ordenado por taxonomia/alfabetica) ainda funciona.
- **Performance da varredura de 333 PDFs.** Mitigacao: varredura le apenas nomes de arquivo
  (stat), nao abre PDFs -- custo desprezivel.
