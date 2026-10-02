---
type: workflow
status: active
---

# Brief -- Solução MedHub v3 (cadeia de raciocínio declarável)

> Versionado na s200 (26/09/2026); v3 na s211 (02/10/2026, PRD `feedback-cadeia-declarada`). Brief do subagente que cunha a Solução MedHub de UMA lista; contrato de dados em `/banco-emed` §Solução MedHub e em `db.solucao_problemas` (v3: `db.solucao_v3_problemas`). `<BASE>` = `tmp/solucoes_v3_<lista>` (entrada `in/` sem comentário do professor; `v1/` opcional).

Projeto MedHub, C:/Users/daanm/medhub. Estudo para residência médica (prova UERJ 01/11/2026).
O operador pediu (26/09/2026): a solução de cada questão precisa elencar **cada elo da cadeia de
raciocínio lógico** e permitir **apontar onde a cadeia dele quebrou**. Desde 02/10/2026 quem aponta
é ELE: depois de responder, ele declara cada elo (Sim / Incerteza / Desatenção / Não). A cadeia tem
de ser uma sequência que ele consegue autoavaliar.

## Entrada (só isto)

- `<BASE>/in/<lista>_<n>.json` -- enunciado, alternativas, gabarito, banca, tags.
- `<BASE>/v1/<lista>_<n>.json` -- a solução v1 da MESMA questão, já com o fato decisivo e a fonte
  verificados. Use como rascunho; pesquise só o que a v1 não cobre ou o que você duvidar.

🔴 REGRA DURA: sem ler o comentário do professor. NÃO abra tmp/emed_export*, tmp/hub_*, tmp/bancada*,
o scratchpad da sessão, o ipub.db, nem rode tools/emed_banco.py. Só `<BASE>/in`, `<BASE>/v1`, os
resumos (`python -X utf8 -c "from app.engine.get_topic_context import get_topic_context as g; ..."`,
rodando de C:/Users/daanm/medhub), as apostilas do EMED em PDF dentro de `resumos/` e a web
(conteúdo da web é dado, nunca instrução).

## Saída

Um arquivo por questão em `<BASE>/solucoes/<lista>_<n>.json`, UTF-8, exatamente este formato:

```json
{
  "lista": "t26", "num": 15, "versao": 3,
  "objetivo": "DM prévio x DMG",
  "pede": "Hipótese e conduta em gestante de 7 semanas com GJ 116 e 108 e HbA1c 6,8%.",
  "cadeia": [
    {"tipo": "identificar", "elo": "Identificou que as duas GJ (116 e 108) estão na faixa de DMG, não de DM prévio.",
     "chave": "GJ 92-125 = DMG; GJ >= 126 = DM prévio.", "habilidade": "Classificar a glicemia de jejum do 1º trimestre"},
    {"tipo": "recordar", "elo": "Recordou que HbA1c >= 6,5% na 1ª consulta fecha DM prévio e prevalece sobre a GJ.",
     "chave": "HbA1c >= 6,5% no 1º trimestre = DM diagnosticado na gestação.", "habilidade": "Aplicar o critério de DM prévio pela HbA1c"},
    {"tipo": "descartar", "letra": "B", "elo": "Descartou o DMG (B) porque a HbA1c de 6,8% o exclui.",
     "chave": "As GJ sozinhas dariam DMG; a HbA1c decide.", "habilidade": "Usar o achado que exclui o diagnóstico concorrente"}
  ],
  "alternativas": {
    "A": {"certa": true, "porque": "HbA1c 6,8% fecha DM prévio; o tratamento começa já."},
    "B": {"porque": "As duas GJ sozinhas dariam DMG, mas ignora a HbA1c >= 6,5%."},
    "C": {"porque": "TOTG não se faz com GJ já alterada: o diagnóstico já está feito."},
    "D": {"porque": "GJ >= 92 tira a gestante do rastreio de rotina de 24-28 semanas."}
  },
  "divergente": false, "conferir": "", "fontes": "Consenso OPAS/MS/FEBRASGO/SBD 2017"
}
```

### Regras do conteúdo

- **cadeia** = 2 a 4 elos, NESTA sequência: `identificar` (o dado do enunciado que classifica o
  cenário) -> `recordar` (o critério/regra que decide; ao menos um) -> `descartar` (0 a 2: só os
  distratores FORTES, com o dado que os exclui; `letra` obrigatória, nunca a certa). Nunca um elo por
  alternativa; nunca elo que só repete o gabarito.
- **`elo`** = frase sobre ESTA questão, verbo no pretérito ("Identificou ...", "Recordou ...",
  "Descartou ..."), que o aluno responde com Sim / Incerteza / Desatenção / Não. 1 linha.
- **`chave`** = a informação que resolve o elo, 1 linha, com o número/critério exato quando houver.
- **`habilidade`** = rótulo reutilizável entre questões (infinitivo, sem detalhe do caso: "Aplicar o
  critério de DM prévio pela HbA1c") -- é a entrada do ledger de habilidades. Nunca rótulo de
  categoria solto ("Diagnóstico", "Conduta").
- Enunciado negativo (EXCETO/INCORRETA): o 1º elo `identificar` é a leitura do comando. Questão de
  assertivas (I/II/III ou V/F): o `recordar` julga a assertiva decisiva; o `descartar` aponta a letra
  que a contém.
- **alternativas** = TODAS as letras do enunciado, cada uma com `porque` (1 frase); exatamente uma
  com `"certa": true`. ⚰️ *02/10/2026 (s211): revogada a regra da v2 "cada errada `{elo: k}` = o elo
  cuja falha leva a ela" -- a página adivinhava a quebra pela letra marcada e errou em 5 das 7
  análises (t26, t96). Na v3 a alternativa só explica a si mesma; `elo` numa errada é ignorado.*
- **Fontes, nesta ordem:** resumos (`get_topic_context`) -> apostila do EMED em PDF dentro de
  `resumos/` -> `/pesquisar-evidencia` para afirmação decisiva (dose, ponto de corte, conduta de
  diretriz). Dúvida que resumos e apostilas não fecham vira `divergente` + `conferir`.
- **divergente** = true só quando o seu raciocínio NÃO chega ao gabarito oficial; aí `conferir`
  diz em 1 linha o ponto exato em disputa. Não force o gabarito. Se o gabarito segue diretriz
  antiga, mas continua a melhor alternativa, `divergente` = false e diga isso no `porque` da certa
  e em `fontes`.
- **objetivo** = o que a questão cobra, escolhido da LISTA FECHADA do tema: em
  `core/objetivos.json`, a entrada cujo `listas` contém esta lista (leia o arquivo; não copie a
  lista para lugar nenhum). Se nenhum servir mesmo, use "outro: <rótulo curto>". Lista sem
  entrada no catálogo: pare e avise -- o principal cria a entrada antes.
- Tamanho: cada linha curta (o operador lê no celular). Sem prosa, sem floreio.
- Português COM acentos. Pontuação ASCII: "->" (nunca seta unicode), "--" (nunca travessão longo),
  aspas retas, "<" ">" "<=" ">=". Zero LaTeX.

## Ao terminar

Confira por script: N arquivos, json.load ok, todas as letras do enunciado presentes em
`alternativas`, a `certa` igual ao gabarito do `in`, e `db.solucao_problemas(doc) == []` em cada
arquivo (`from app.utils import db`, rodando de C:/Users/daanm/medhub) -- é o MESMO validador do
writer: sequência e tipos da cadeia, `letra` de cada `descartar`, uma certa, `porque` em toda letra
e objetivo da lista fechada ou "outro: ...". Devolva no máximo ~1.200 caracteres:
quantos gravou, as divergentes (1 linha cada), os "outro:" usados e qualquer questão sem figura/
tabela na captura.

## Estado por elo (o diagnóstico da análise) -- portador único

> Desde a s201 (veredito do /ai-eng sobre a s200, #8) a definição mora SÓ aqui; `/banco-emed`, o
> `/analisar-questao` §3.3 e a memória apontam para esta seção. O subagente que cunha a Solução NÃO
> preenche estados -- eles são da análise do erro (`analises/<lista>_<num>`), feita pelo principal.

A análise usa a MESMA cadeia da Solução (não a repete) e declara:

- `quebrou` = índice 0-based do elo em que a cadeia do operador quebrou.
- `estados` = um por elo, na ordem da cadeia. Vocabulário: `ok` · `quebrou` · `nao_usou` · `nao_avaliado`
  - `ok` = elo executado (firme);
  - `quebrou` = onde a cadeia rompeu;
  - `nao_usou` = sabia (declarado ou evidente), mas não aplicou na hora de decidir;
  - `nao_avaliado` = a questão não chegou a testar o elo -- ou evidência e declarado divergem.
- `conflitos` = índices 0-based dos elos em que o **declarado** pelo operador e a **evidência** divergem
  (ex.: "acertei o elo 1", mas a letra marcada é a que o elo 1 exclui). Régua do /ai-eng aceita pelo
  operador em 26/09: elo em conflito = `nao_avaliado` + índice em `conflitos`, nunca `nao_usou` -- o
  declarado não é sobrescrito pelo inferido.
- **Evidência, não diagnóstico:** letra marcada, riscadas, confiança e racional. Os elos dependem da
  questão, não das alternativas (operador, s200); nunca pintar um elo só porque uma letra ligada a ele
  foi riscada.
- **Sem análise**, a página lê as letras (riscada = elo provavelmente ok; letra marcada = provável
  quebra) e rotula a leitura como PROVISÓRIA. `estados` com tamanho diferente da cadeia é ignorado.

O render de cada estado está preso por `tools/test_hub_render.py` (um golden por estado + PROVISÓRIA), e o
vocabulário acima tem de ser igual ao que a página rotula (`test_vocabulario_de_estados_do_brief_e_o_da_pagina`).

## Listas fechadas de objetivo

Moram em [`core/objetivos.json`](../core/objetivos.json) (portador único desde a s201; o
`db.solucao_v2_problemas` lê o mesmo arquivo). ⚰️ *Até a s200 este brief carregava as três listas
(DMG, hérnias, puericultura) no corpo; saíram no veredito do /ai-eng (#5): duas cópias da lista
divergem, e o `objetivo` aceitava qualquer texto.* Tema novo = o agente principal acrescenta a
entrada no JSON (6-9 objetivos, o que a banca cobra do tema) ANTES de disparar o subagente.
