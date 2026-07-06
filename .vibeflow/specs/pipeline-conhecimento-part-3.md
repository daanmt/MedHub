# Spec: Pipeline de Conhecimento -- Parte 3: Materializar o Sinal da Aula (Onda 3 / F18c + F21)

> Derivado de `.vibeflow/prds/pipeline-conhecimento.md` (Onda 3). Encoding ASCII (AGENTE 4.5).
> Parte 3 de 4. Independente das demais na implementacao; a operacionalizacao mecanica do
> checklist F21 amadurece com a cobertura das Partes 1-2, mas a CLAUSULA entra ja.

## Objetivo

Parar de desperdicar o sinal caro da aula-base: a nota de dificuldade que calibra a
descompressao passa a ser REGISTRADA no ato (alimenta a Revisao Calibrada), e o contrato
passa a separar explicitamente descompressao (calibravel) de cobertura de pontos de prova
(piso fixo), fechando a brecha que fez a Q2 da s109 cair (ponto de decisao eliminado por
compressao, nao encurtado).

## Contexto

A aula-base e artefato validado (cobertura 53%->75%, s088/s089) e caro de produzir, mas hoje
e chat-only e a nota que a calibrou nao e persistida -- `taxonomia_cronograma.dificuldade`
fica intocada (F18). Ja existe o wiring de dados: `db.set_dificuldade(area, tema, nota,
fonte)` + colunas `dificuldade/dificuldade_fonte/dificuldade_at` (Revisao Calibrada, s096,
em producao) -- zero schema novo. O F21 e a regra "profundidade calibra, cobertura nao":
existe em memoria/AGENTE mas NAO esta operacionalizada no contrato de render. O contrato
canonico e `core/contracts/revisao-calibrada-contract.md` (clausulas 1-9); a fonte da skill
`revisar` e `.claude/commands/revisar.md`, espelhada em `.agents/skills/source-command-revisar/`
via `tools/sync_skills.py --check`.

## Definition of Done

Binarios (pass/fail):

1. **F18c -- registro no ato.** Existe caminho testavel que, ao fechar uma aula/revisao
   calibrada, grava a nota via `db.set_dificuldade(..., fonte='aula')`; apos executa-lo,
   `get_dificuldade(area, tema)` retorna a nota com `fonte='aula'` e `at` preenchido. Teste
   cobre o caminho de registro (db temp).
2. **F18c -- clausula.** O fluxo de aula (contrato + `.claude/commands/revisar.md`) instrui,
   como passo de fechamento, registrar a nota 1-10 usada na calibracao com `fonte='aula'`.
3. **F21 -- clausula no contrato.** `revisao-calibrada-contract.md` ganha clausula que separa
   explicitamente: a nota calibra DESCOMPRESSAO/prosa (elastico); a COBERTURA de pontos de
   decisao de alto rendimento e PISO FIXO por tema, derivado do sumario da fonte -- mesmo em
   D2 o render passa pelo checklist de cobertura antes de fechar. Aponta o sumario da fonte
   como origem do checklist e registra a dependencia da cobertura mecanica nas Partes 1-2
   (sem `.md`/sumario, deriva do que houver; nao bloqueia a clausula).
4. **Paridade.** A clausula F18c/F21 que toca `.claude/commands/revisar.md` esta espelhada:
   `python tools/sync_skills.py --check` passa (exit 0).
5. **Craftsmanship:** zero schema novo (reusa `set_dificuldade` + colunas existentes);
   `import sqlite3` so em `db.py`; armadilhas/clausulas sao CUMULATIVAS (nova clausula
   ADICIONADA, nenhuma existente deletada); ASCII limpo; a clausula F21 respeita as
   fronteiras duras ja no contrato (nao toca volume/acertos/perf).

## Escopo

- `core/contracts/revisao-calibrada-contract.md`: nova clausula F21 (descompressao x
  cobertura-piso) + reforco na Clausula 5 (invariantes) de que a cobertura de pontos de
  prova e barreira inviolavel; clausula F18c (registro no ato com `fonte='aula'`).
- `.claude/commands/revisar.md`: passo de fechamento (registrar nota via `set_dificuldade`)
  + a regra de cobertura-piso no render da aula.
- `.agents/skills/source-command-revisar/SKILL.md`: regenerado por `sync_skills.py` (build
  artifact -- nao editar a mao).
- `app/utils/db.py`: SOMENTE se `set_dificuldade` validar/rejeitar `fonte='aula'` hoje --
  admitir 'aula' no conjunto de fontes rastreaveis (docstring + qualquer guard). Se ja
  aceita valor livre, apenas atualizar a docstring.
- Teste: estender `tools/test_revisao_calibrada.py` (ou novo `tools/test_aula_registro.py`)
  cobrindo o registro `fonte='aula'`.

## Anti-escopo

- **Persistir a aula como artefato proprio** -- decisao F18: o `.md` e a forma duravel; a
  aula continua render efemero.
- **Implementar o checklist de cobertura mecanico end-to-end** -- a CLAUSULA entra; a
  automacao do checklist depende da cobertura (Partes 1-2). Registrar dependencia, nao
  construir o motor aqui.
- **Coluna nova / mudanca de schema** -- proibido.
- **Mudar a escala 1-10, `infer_nota`, ou os sub-modos PREPARAR/DRENAR** -- a Revisao
  Calibrada (s096) esta em producao; aqui so ADICIONA registro + clausula.
- **UI Streamlit.**

## Decisoes tecnicas

- **`fonte='aula'` como terceiro valor rastreavel** (ao lado de 'usuario' e
  'agente_inferida'). Distingue a nota nascida da forja da aula das outras origens -- util
  para auditoria futura de qual sinal calibrou o tema. `set_dificuldade` hoje escreve `fonte`
  sem enum rigido no SQL; a mudanca e documental + teste, salvo se houver guard a relaxar.
- **F21 como clausula, nao como codigo, nesta parte.** O render da aula e agent-driven
  (contrato + skill markdown). A operacionalizacao mecanica (derivar o piso do sumario da
  fonte) exige a cobertura das Partes 1-2; forcar codigo aqui seria acoplar ondas. A
  clausula fixa a regra AGORA e o motor vem quando a cobertura existir.
- **Registro no fechamento, nao no meio.** O passo de `set_dificuldade` e o ultimo ato da
  aula/revisao -- a nota so e definitiva depois da calibracao, e um registro precoce gravaria
  ruido.

## Applicable patterns

- `patterns/db-access-layer.md` -- `set_dificuldade` ja e a via canonica; sem `sqlite3` fora
  de `db.py`.
- `patterns/agent-workflow-protocol.md` -- clausula de fechamento no fluxo de sessao/aula.
- Contrato `revisao-calibrada-contract.md` (precedente do ciclo 1 Onda 3) + `sync_skills.py`
  para paridade command<->skill.
- Convencao "armadilhas/clausulas cumulativas": nunca deletar, so adicionar/refinar.

## Riscos

- **Espelho fora de sync apos editar o command** (esquecer de rodar `sync_skills.py`).
  Mitigacao: DoD #4 e `--check` sao o gate; rodar `sync_skills.py` (sem `--check`) para
  regenerar antes de auditar.
- **Clausula F21 vira letra morta sem o motor.** Mitigacao: aceitavel e explicito -- a
  clausula e a barreira de conduta do agente AGORA (mesmo valor das outras clausulas
  agent-driven do contrato); a automacao e trabalho das Partes 1-2 + follow-up.
- **`set_dificuldade` com guard de fonte que rejeita 'aula'.** Mitigacao: DoD #5 verifica;
  se houver guard, relaxa-lo (admitir 'aula') e a unica mudanca de codigo em `db.py`.
