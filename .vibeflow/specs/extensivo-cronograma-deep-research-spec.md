---
type: spec
projeto: MedHub
feature: extensivo-cronograma
part: 1
slug: extensivo-cronograma-deep-research-spec
status: ready
relates_to:
  - .vibeflow/prds/extensivo-cronograma-deep-research.md
  - tools/cronograma.py
  - tools/day_plan.py
  - core/contracts/revisao-calibrada-contract.md
  - core/cronograma/grade.json
---

# Spec — Cronograma Extensivo · Parte 1: Parser, Grade e Harness D10

> Deriva de `.vibeflow/prds/extensivo-cronograma-deep-research.md`. Cobre a detecção do material indicado no cronograma em PDF, evolução da grade versionada e consolidação do modo Deep-Research autônomo (Zero-Upload).

## Objective
Enriquecer o parser oficial (`tools/cronograma.py`) para capturar a indicação de material (`"extensivo"` vs `"resumo"`) no texto do PDF, expor esse dado na abertura da sessão via `tools/day_plan.py` e consolidar no contrato canônico a regra de promoção automática ao modo Extensivo (D10 / Deep-Research / Zero-Upload).

## Context
Atualmente, o parser `tools/cronograma.py` extrai apenas os metadados brutos (`tarefa`, `area`, `tema`, `tipo`, `questoes`) de `Cronograma.pdf`, ignorando as instruções sobre a utilização de Livro Digital Completo vs. Resumo Estratégico. Como `day_plan.py` consome apenas `core/cronograma/grade.json`, o agente operacional desconhece a indicação de material da tarefa. Além disso, a regra canônica de que o agente atua no modo Extensivo de forma autônoma (sem upload de PDFs) precisa ser formalizada no contrato.

## Definition of Done
1. **Parser (`tools/cronograma.py`).** A extração do texto das tarefas na função `_parse_detail()` ou equivalente detecta menções a "Extensivo", "Livro Digital Completo" ou "LDI" vs "Resumo", definindo o atributo `material_indicado` (`"extensivo"` | `"resumo"`).
2. **Grade Versionada (`core/cronograma/grade.json`).** A execução do comando `python tools/cronograma.py --rebuild` atualiza a grade com sucesso, mantendo `n_tasks: 352` e `total_questoes: 10218`, adicionando a propriedade `material_indicado` a cada objeto de tarefa.
3. **Orquestrador (`tools/day_plan.py`).** A saída no terminal e o retorno de `--difficulty` ou da abertura do dia exibem o material indicado para a tarefa selecionada, notificando o agente quando a calibração D10 (Deep-Research) for requerida.
4. **Harness / Contrato (`core/contracts/revisao-calibrada-contract.md`).** A Cláusula 3 explicitamente define que tarefas rotuladas como `Teoria + Exercícios` ou com nota inferida $\ge 7$ promovem o agente ao modo **Extensivo (D10)**, operando de forma autônoma sem solicitação de upload de arquivos PDF (Zero-Upload).

## Scope
- Modificação na extração de texto em `tools/cronograma.py` para popular `material_indicado`.
- Execução de `python tools/cronograma.py --rebuild` para atualizar `core/cronograma/grade.json`.
- Edição de `tools/day_plan.py` para incluir `material_indicado` na modelagem de saída das tarefas do dia.
- Edição de `core/contracts/revisao-calibrada-contract.md` formalizando a regra de inferência operacional Teoria -> Extensivo (D10) e o protocolo Zero-Upload.

## Anti-scope
- Alteração de schema ou manipulação do banco de dados SQLite (`ipub.db`).
- Modificação em páginas locais Streamlit (`app/`).
- Indexação ou armazenamento físico de PDFs de apostilas comerciais no repositório MedHub.

## Technical Decisions
- **Regex e Heurística de Material:** No parser `tools/cronograma.py`, verificamos se o texto da tarefa contém `extensivo` ou `Livro Digital` sem a palavra `Resumo`. Se contido ou se o tipo for `Teoria + Exercícios`, marcamos `"extensivo"`; caso contrário, `"resumo"`.
- **Zero-Upload como Norma:** A diretriz de governança assume o conhecimento inborn do modelo (calibrado via Degrau 0 e sem saltos lógicos) como equivalente ao material extensivo para fins de aula-base, solicitando upload apenas em caso de divergência institucional/banca regional.
