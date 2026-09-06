# Hotfix: cronograma-pdf-path

origin: session
status: partial

## Symptom
`python -X utf8 tools/cronograma.py --check` (instrumento da condicao W5 do `reconcile-contract.md`) aborta com `FileNotFoundError: [Errno 2] No such file or directory: 'C:\Users\daanm\medhub\Cronograma.pdf'` (observado 2026-09-06, s166, durante a revisao do README). O PDF-fonte existe no disco em `data/Cronograma.pdf` (mtime 2026-03-24), ao lado dos outros PDFs de dados (edital, guias estatisticos). `core/cronograma/grade.json` existe e foi derivado dele. Resultado: o check de frescor da grade esta morto ha um tempo indeterminado sem que nada acuse -- W5 e "manual, WARNING", entao ninguem rodava.

## Checkpoint
hypothesis: `tools/cronograma.py:44` fixa `PDF_PATH = os.path.join(ROOT, "Cronograma.pdf")` (raiz do repo), sem fallback; o arquivo real vive em `data/`. `check()` chama `sha256_file(pdf_path)` direto e explode em vez de degradar para `status: "missing_pdf"`.
falsification_test: com um `Cronograma.pdf` sintetico colocado so em `<root>/data/` (raiz vazia), `resolve_pdf_path()` deve devolver o caminho em `data/`; na versao atual a funcao nao existe e `check()` levanta FileNotFoundError.
blind_spots: por que o PDF foi parar em `data/` (mudanca manual do usuario ou limpeza de sessao anterior) -- nao investigado, nao muda o fix; `--sync-drive` recebe o xlsx por argumento e nao depende deste caminho.

## Preservation
- `--rebuild` continua derivando `grade.json` do mesmo PDF (sha256 registrado em `_meta.fonte_sha256`).
- A raiz do repo continua sendo o local canonico (contrato); `data/` e fallback, nao substituto.
- Zero write no `ipub.db` (fronteira dura do derivador).

## Eliminated / Evidence

## Root cause
`tools/cronograma.py` resolvia o PDF-fonte num unico caminho fixo (`ROOT/Cronograma.pdf`) e `check()` chamava `sha256_file` sem testar existencia. O arquivo real esta em `data/Cronograma.pdf`; o instrumento W5 morria em traceback e, por ser check manual/WARNING, ninguem notava.

## Fix
files_changed: tools/cronograma.py, tools/test_cronograma_pdf_path.py (novo), pytest.ini (registro F43), .claude/commands/cronograma.md (+ espelho gerado por sync_skills)
`resolve_pdf_path(root)`: raiz primeiro (canonico), `data/` como fallback, caminho canonico quando nenhum existe (para a mensagem nomear o lugar certo). `check()` devolve `{"status": "missing_pdf", ...}` em vez de levantar. `--rebuild`/`extrai_paginas` intocados na logica (so consomem o `PDF_PATH` resolvido).


## DoD
- [x] `tools/test_cronograma_pdf_path.py` vermelho antes (FileNotFoundError / AttributeError), verde depois.
- [x] `python -X utf8 tools/cronograma.py --check` sobre o repo real: `status: fresh`, sha256 do PDF em `data/` == `_meta.fonte_sha256` da grade ("grade em dia").
- [x] Sem PDF, `check()` devolve `status: "missing_pdf"` (teste 2). Suites `test_preparacao` e `test_orquestrador` verdes (27 passed).

## Regression
WHEN so `data/Cronograma.pdf` existe sob a raiz THEN `resolve_pdf_path(raiz)` devolve esse caminho; WHEN os dois existem THEN a raiz vence; WHEN nenhum existe THEN `check()` devolve `status: missing_pdf` com a mensagem citando `Cronograma.pdf`, sem excecao.
test: tools/test_cronograma_pdf_path.py
oracle_type: specified
reproduction: synthetic
verification: red-green

## Deviations
- `reproduction: synthetic` (tmp_path) por politica do projeto; o `--check` real foi rodado apos o fix e voltou `fresh`. Status `partial` pela regra do skill, nao por duvida sobre o fix.
- Nao investigado (deferido): quando e por que o PDF saiu da raiz. O contrato `cronograma-contract.md` segue dizendo "raiz"; o fallback nao muda a norma.
