# Spec: Check de auto-suficiencia de flashcard (Part 1)

> Gerado via /vibeflow:gen-spec on 2026-07-15 -- de `.vibeflow/prds/auto-suficiencia-card-e-telemetria-fila.md`

## Objective

`python tools/auto_check.py --all` passa a acusar (WARN, sem bloquear) os flashcards ativos que nao sao respondiveis a frio, listando-os por anti-padrao -- fechando o ponto cego semantico do linter lexico atual.

## Context

Auditoria da sessao 121 (2026-07-15): dos 596 cards ativos, ~37 (6,2%) nao se sustentam sozinhos, em 3 anti-padroes -- **opcao-anaforico** (17: "por que a alternativa X e falsa", referencia opcoes ausentes do card), **deitico** (15: "neste caso/deste paciente/acima"), **%-fake** (2: "61% caem" na armadilha). O linter `audit_flashcard_quality.py` da 99,6% OK porque e lexico/estrutural -- cego aos tres (todos semanticos/anaforicos). Card ruim entra na fila em silencio e so aparece quando o usuario tropeca nele. Este check e a prevencao duravel E gera a worklist dos 37 pra reforja de conteudo.

## Definition of Done

1. Existe `tools/card_self_sufficiency.py` com funcao pura `run_checks(...)` que retorna uma lista de achados `{id, padrao, area, tema}` cobrindo os 3 anti-padroes, sobre cards ativos (`needs_qualitative < 2`).
2. `python tools/auto_check.py --all` imprime um bloco WARN com tag dedicada (ex.: `CARD_AUTOSUFICIENCIA`), agrupado/contado por padrao, e **o exit code permanece 0** quando esse check e o unico achado (WARN nunca rebaixa o veredito).
3. No `--changed`/`--staged` o check so roda quando arquivos-gatilho de flashcard mudaram (janela de relevancia); no `--all` roda sempre.
4. O detector reproduz o conjunto real de nao-auto-suficientes apos o aperto de precisao (fase de implementacao, aprovado): **24 cards ativos** (11 deitico + 11 opcao-anaforico + 2 %-fake); os 11 falso-positivos do regex cru do audit (alternativa/opcao terapeutica, "acima" comparador, "ressuscitada") **NAO** disparam, e um card-controle auto-suficiente (fixture) **NAO** dispara. (O ">= 37" original era inflado por esses 11 FPs + o tag manual safra-SUS; nao e piso valido.)
5. `tools/test_card_self_sufficiency.py` cobre >= 1 fixture por padrao + >= 1 negativo, todos verdes; roda no `auto_check`.
6. **[craftsmanship]** Segue o padrao `warn-first-check`: regra no modulo proprio (o `auto_check` so orquestra), instrumentada via `_ledger_record`, parsing defensivo (sem dados -> silencio; malformado -> WARN, nunca crash), nasce WARN. Zero violacao dos Don'ts de `conventions.md`.

## Scope

- Modulo novo `tools/card_self_sufficiency.py`: regex/heuristica dos 3 padroes + `run_checks()` puro + `main()` standalone (invocavel `python tools/card_self_sufficiency.py` pra ver a worklist).
- Bloco de integracao no `main()` do `auto_check.py` (warn-first, ledger, janela de relevancia).
- Testes unitarios com fixtures dos 3 padroes + negativo.
- A saida do `main()` do modulo serve de **worklist** (id/padrao/area/tema) pra reforja de conteudo posterior.

## Anti-scope

- A reforja de conteudo dos 37 cards (curadoria via `/curar-cards` + `estilo-flashcard`; fora daqui).
- Julgamento por LLM do "criptografico" -- v0 e regex deterministica (tier futuro possivel).
- Editar `audit_flashcard_quality.py` (o check novo **complementa**, nao substitui).
- Endurecer pra BLOCK -- nasce WARN; endurece so quando a base zerar E o operador decidir.
- Feature B (telemetria de fila) -- Part 2.

## Technical Decisions

- **Regex deterministica, nao LLM (v0).** Barato, testavel, reproduzivel, coerente com warn-first. Trade-off: pode ter falso-positivo (ex.: "afirmacao" numa pergunta legitima). Mitigacao: ancorar as regex nas assinaturas exatas do audit + card-controle negativo nos testes; falso-positivo em WARN e tolerado (nao bloqueia; o agente cura).
- **Modulo novo, nao estender `audit_flashcard_quality.py`.** Isolamento e testabilidade; o linter existente e lexico-estrutural (responsabilidade distinta). Alinha com warn-first ("a regra mora num modulo proprio, testavel").
- **Campo por padrao:** opcao-anaforico e deitico aplicam so no FRONT (`frente_contexto` + `frente_pergunta`); %-fake so no verso (`verso_armadilha` + `verso_regra_mestre`). Evita casar campo errado.
- **Acesso ao db:** CLI standalone abrindo propria conexao sqlite3 (conventions, secao CLI); filtro `needs_qualitative < 2`.
- **Assinaturas (audit apertado com guarda de contexto anaforico -- fix da fase de implementacao):** a prosa clinica reusa "opcao/alternativa" (terapeutica) e "acima" (comparador) em sentido nao-MCQ; os regex crus do audit exploratorio davam ~30% de falso-positivo (#641/#665/#742/#796 "alternativa/opcao terapeutica"; #60/#510/#626/#704/#713 "acima" de valor; #426 "ressuscitada" via substring "citad"). Assinaturas finais:
  - opcao-anaforico (front): `\([A-E]\)` | `enunciado negativo` | `assertiva` | `assinal\w* a (alternativa|afirmativa|assertiva|op[cç][aã]o|frase)` | `(alternativa|afirmativa|assertiva|op[cç][aã]o|frase|afirma[cç][aã]o) (correta|incorreta|errada|falsa|verdadeira)` | `por que\b.{0,60}?(errad|fals[ao]|incorret)` | `(op[cç][aã]o|alternativa) '...'`. Nao dispara em "opcao/alternativa terapeutica" nem "esta correto?" clinico.
  - deitico (front): `neste caso` | `deste paciente` | `nessa situa` | `a seguir` | `\bmencionad` | `\bcitad` | `(quadro|caso|paciente|figura|imagem|tabela|texto|enunciado) acima` | `acima (descrit|cit|mencion|expost|apresentad|referid|relatad)`. `acima` cru dropado (era comparador de valor).
  - %-fake (verso): `\d{1,3}\s*%\s*(caem|marcam|erram|escolhem|assinalam|confundem|optam)` (inalterado; 2/2 sem ruido).

## Applicable Patterns

- **`warn-first-check.md`** (OBRIGATORIO) -- estrutura do check, WARN-first, ledger, parsing defensivo.
- **`error-insertion-pipeline.md`** -- schema de card v5.0 (campos estruturados, `needs_qualitative`).
- **`db-access-layer.md`** -- CLI standalone com sqlite3 proprio.

## Risks

- **Falso-positivo barulhento** -> WARN-first (nao bloqueia) + card-controle negativo + regex ancorada nas assinaturas do audit.
- **Regex casar o campo errado** (ex.: "acima" numa resposta legitima) -> aplicar cada padrao so no campo certo (front vs verso); testes garantem.
- **Encoding de acentos em Windows** (á/ç nas regex) -> usar classes `[aá]`/`[cç]` e rodar com `-X utf8`; incluir fixture acentuada.
- **Contagem divergir do audit** (37) -> teste ancora o piso (`>= 37`) contra o db real no `--all`; se divergir, e sinal, nao falha silenciosa.

## Dependencies

Nenhuma. Independente da Part 2. Ordem sugerida de execucao: Part 1 -> Part 2.
