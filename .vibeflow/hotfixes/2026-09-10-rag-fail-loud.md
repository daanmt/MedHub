# Hotfix: rag-fail-loud

origin: session
status: verified

## Symptom

Um subagente `evidence-researcher` escreveu num relatorio de evidencia, na s175,
que *"nao ha resumo indexado sobre HPB/LUTS"* e registrou o item como lacuna de
cobertura do corpus. **A afirmacao e falsa:** `resumos/Cirurgia/Urologia.md` tem
**39 chunks** indexados no ChromaDB (colecao com 2.353 chunks).

Reproduzido de novo agora, 2026-09-10, com o Ollama ainda fora do ar
(`WinError 10061` em `localhost:11434`):

```
from app.engine.rag import search
search('hiperplasia prostatica benigna indicacao cirurgica', n_results=3)
->  []          # zero excecao, zero WARN, zero marca de degradacao
```

O consumidor recebe uma lista vazia e nao tem como distinguir tres mundos:
(a) o indice foi consultado e nao tem nada sobre isso -- negativa honesta;
(b) o motor semantico caiu e o fallback lexico tambem nao achou;
(c) o motor caiu E o proprio fallback quebrou por dentro.
Os tres retornam o MESMO valor. Um agente leu esse valor como fato e o escreveu.

## Checkpoint

hypothesis: nao falta salvaguarda -- ela existe e esta bem desenhada. O
`_textual_fallback()` tem docstring explicita ("Fallback lexico quando o RAG
semantico esta indisponivel") e marca proveniencia em
`metadata['source'] == 'fallback_textual'` justamente para o consumidor
distinguir degradado de curado. O defeito e que a salvaguarda **falha em silencio
junto com o que ela protege**: o `except Exception: return []` no fim do proprio
fallback (`rag.py:333-334`) colapsa "o motor caiu E o fallback quebrou" no mesmo
`[]` de "o indice nao tem isso". E ha um SEGUNDO silenciador em serie, no
consumidor: `get_topic_context.py:175-179` envolve a chamada num
`except Exception: pass`, entao mesmo uma excecao vinda do RAG viraria silencio
uma camada acima.

falsification_test: derrubar o motor (monkeypatch de `get_collection` levantando
`ConnectionError`) e chamar `search()` sobre um tema que EXISTE em `resumos/`.
Se a hipotese esta certa, o retorno e indistinguivel de "nao existe": ou `[]`, ou
hits sem nenhuma marca de que a busca curada nao aconteceu.

blind_spots: (a) nao estou avaliando a QUALIDADE do fallback lexico -- so a
honestidade do seu retorno; (b) o caso "Chroma instalado mas colecao vazia"
continua sendo negativa honesta legitima e tem de seguir devolvendo `[]`;
(c) nao toco no caminho semantico feliz.

## Preservation

- O caminho semantico vivo e **inalterado**: mesma query multi-query HyDE+Raw,
  mesmo `max_distance`, mesmo shape de retorno, mesma ordenacao.
- A negativa honesta sobrevive: motor VIVO que consulta e nao acha nada continua
  devolvendo `[]`. Fail-loud nao pode virar fail-sempre.
- `metadata['source'] == 'fallback_textual'` continua sendo a marca de
  proveniencia do resultado degradado -- o contrato ja existente nao muda.

## Root cause

`search()` tem tres estados possiveis e **um unico tipo de retorno** para os
tres. Como `list` nao carrega a distincao, o valor `[]` fica sobrecarregado: e
ao mesmo tempo "procurei e nao ha" e "nao consegui procurar". A camada que
deveria desfazer a ambiguidade -- o fallback -- reusa o mesmo `[]` para o proprio
fracasso.

Isso viola `core/contracts/evidence-governance.md §7` (honest-negative) na camada
`local`: ausencia de evidencia so pode ser declarada quando a busca de fato
aconteceu. Aqui a busca **nao aconteceu** e o retorno diz que aconteceu.

E pior que a familia F79/F81 (gate cego que deixa passar): este nao e um gate que
falha em barrar, e um **leitor que produz um fato falso** e o entrega a um agente
que escreve conclusao. Irmao do F80 (relogio que mente sem avisar), com raio
maior porque o consumidor e autoral.

## Fix

files_changed: `app/engine/rag.py`, `app/engine/get_topic_context.py` (2 arquivos de codigo, no teto; + `tools/test_rag_fail_loud.py` e `pytest.ini`, que nao contam)

O tipo de retorno passa a carregar a distincao, via excecao nomeada:

- `RagIndisponivel(RuntimeError)` nova, exportada pelo modulo, com o backend e a
  causa no texto.
- `_textual_fallback` para de engolir o proprio fracasso: o `except Exception`
  final vira `raise RagIndisponivel(...) from e`. O `[]` sobrevive **so** nos dois
  caminhos honestos ("nenhum resumo casa o termo" / "o resumo nao e da area
  pedida").
- `search()` separa os tres estados: motor vivo que consulta e nao acha -> `[]`
  (negativa honesta, preservada); motor caido com fallback que acha -> hits
  marcados `fallback_textual` + **WARN em stderr nomeando o backend**; motor caido
  com fallback vazio ou quebrado -> **levanta `RagIndisponivel`**. Nunca `[]`
  silencioso quando a busca curada nao rodou.
- `get_topic_context` para de mascarar: o `except Exception: pass` em torno do RAG
  vira captura nomeada que grava `result["rag_degradado"]` com o motivo e emite o
  WARN, em vez de devolver `relevant_chunks: []` como se o corpus estivesse vazio.

A regra em uma frase: **`[]` passa a significar uma coisa so** -- procurei e nao
ha. Qualquer outro mundo tem nome.

## DoD

- [x] Motor caido + tema que existe em `resumos/` -> hits marcados
      `fallback_textual`, nunca `[]`.
- [x] Motor caido + fallback sem resultado (ou quebrado) -> `RagIndisponivel`
      levantada, com o backend nomeado; jamais `[]`.
- [x] Motor VIVO que consulta e nao acha nada -> `[]` preservado (a negativa
      honesta nao virou excecao).
- [x] `get_topic_context` declara a degradacao em vez de engoli-la.

## Regression

WHEN `get_collection()` levanta `ConnectionError("WinError 10061")` (motor fora
do ar) e a query e sobre um tema que EXISTE em `resumos/`
THEN `search()` devolve hits com `metadata['source'] == 'fallback_textual'`; e
quando nem o fallback acha, levanta `RagIndisponivel` nomeando o backend.
Sob o codigo defeituoso os dois casos devolvem `[]` -- indistinguiveis de
"o corpus nao tem o tema", que e a frase falsa que um agente escreveu.

test: `tools/test_rag_fail_loud.py`
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **O 2o silenciador so apareceu ao desenhar o teste.** O achado original (F91) nomeava um
  silenciador: o `except Exception: return []` do fallback. Ao escrever o caso do consumidor
  descobri que `get_topic_context.py:175-179` envolvia a chamada inteira num
  `except Exception: pass` -- ou seja, mesmo se o RAG tivesse levantado desde sempre, a excecao
  morreria uma camada acima e o agente veria `relevant_chunks: []` do mesmo jeito. **Consertar so
  o rag.py teria produzido um fix que parece certo e nao muda nada no caminho real.** Os dois
  entraram (2 arquivos, dentro do teto).
- **Na reproducao REAL o fallback tambem nao acha.** Pos-fix, a query exata da s175 levanta
  `RagIndisponivel` em vez de degradar com hits: `_find_resumo` casa por nome de arquivo e
  "hiperplasia prostatica benigna indicacao cirurgica" nao casa `Urologia.md`. Isso **reforca** o
  remedio em vez de enfraquece-lo -- no caso real nao existia resposta degradada para dar, so a
  escolha entre mentir (`[]`) e admitir. A qualidade do fallback lexico e outro eixo, declarado
  como blind spot e NAO tratado aqui.
- Um erro meu de autoria do teste, pego pelo proprio vermelho: o fixture de resumo era curto
  demais e `_chunk_by_headers` descarta chunk < 50 chars, entao produzia zero chunks e o teste
  mediria a coisa errada. Fixture reescrito com corpo real.

## Verificacao final

- regressao: **7 testes** -- 5 VERMELHOS antes do fix e verdes depois; os **2 de PRESERVACAO**
  (negativa honesta com motor vivo; caminho semantico feliz) verdes o tempo todo, que e a forma
  correta: eles existem para provar que o fail-loud nao virou fail-sempre.
- reproducao real pos-fix, com o Ollama ainda fora do ar -- a MESMA chamada da s175:
  ```
  search('hiperplasia prostatica benigna indicacao cirurgica')
  [WARN] RAG semantico indisponivel (ConnectionError: Failed to connect to Ollama...) -- degradando
  -> RagIndisponivel: busca NAO ACONTECEU ... nao afirme que o tema nao existe
  ```
- suite detectada: **465 passed** (458 + 7). Critical Gate limpo: nenhuma escrita, nenhum DDL,
  nenhuma operacao destrutiva -- o diff so troca silencio por excecao nomeada e WARN.
