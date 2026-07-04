---
type: spec
projeto: MedHub
feature: autogovernanca-proativa
part: 2
slug: autogovernanca-proativa-part-2
status: ready
relates_to:
  - .vibeflow/prds/autogovernanca-proativa.md
  - tools/audit_resumos.py
  - tools/auto_check.py
  - tools/test_revisao_calibrada.py
---

# Spec -- Autogovernança Proativa - Parte 2: Harness Confiável (R3, resto)

> Deriva de `.vibeflow/prds/autogovernanca-proativa.md` (R3). A Fase 0 da s106 já entregou `--staged`, descoberta quotepath-safe e `test_03` hermético; esta parte fecha o resto do R3.

## Objective
Tornar o harness honesto: separar o que BLOQUEIA de um commit do que só ADVERTE, parar de mascarar corrupção de encoding, e impedir que as suítes de teste mutem o `ipub.db` real.

## Context
O linter `tools/audit_resumos.py` hoje: (a) trata todo `ANTI_PATTERN` e "Armadilhas ausente" como erro crítico e trata "sem marcadores" como aviso -- mas não tem canal para regras NOVAS (frontmatter §5.2, convenção de encoding ASCII) que precisam nascer como WARN e virar BLOCK depois; (b) lê com `errors='ignore'` (linha 47), o que **mascara `UnicodeDecodeError`** -- ironia numa base cuja s103 foi justamente uma convenção de encoding. A suíte `tools/test_revisao_calibrada.py::test_roundtrip` **escreve no `ipub.db` real** (set_dificuldade 99 -> restaura) -- auto-restaurador, mas um crash entre os dois writes deixa o db real sujo. E as suítes exigem `py-fsrs`, instalado só no python global (não no `.venv`); rodar no venv explode com `ImportError` cru.

## Definition of Done
1. **Duas severidades no linter:** `audit_resumos.py` classifica cada achado em BLOCK (exit 1) ou WARN (exit 0, mas reportado com destaque). BLOCK preserva as regras vigentes (seção "Armadilhas de Prova" ausente; tabela ASCII de 3+ pipes; emoji em header). WARN cobre as regras novas: frontmatter §5.2 incompleto (`type`/`area`/`especialidade`/`status`) e presença de caractere de encoding não-ASCII proibido (`→`, `—`, `–`, `$\rightarrow$`).
2. **Encoding deixa de ser mascarado:** `errors='ignore'` removido da leitura; `UnicodeDecodeError` num resumo vira **BLOCK** com mensagem do arquivo, não silêncio.
3. **Nenhuma regra vigente rebaixada:** `python -X utf8 tools/auto_check.py --all` continua exit 0 na base atual (as regras que já eram BLOCK seguem BLOCK; as novas nascem WARN, então não quebram a base que ainda tem débito de frontmatter/encoding legado).
4. **Suíte isolada do db real:** `test_revisao_calibrada.py::test_roundtrip` opera sobre uma **cópia temp** do `ipub.db` (padrão já usado em `test_barreiras_preparar`), restaurada/removida no `finally`. Rodar a suíte 2x seguidas deixa o `ipub.db` real **byte-idêntico** (verificável por hash antes/depois).
5. **Craftsmanship -- guard de interpretador + convenções:** ao faltar `fsrs`, a suíte central emite mensagem clara ("rode com o python global que tem py-fsrs; o .venv não tem") em vez de `ImportError` cru; nenhuma violação nova de `db-access-layer` (writes de teste só na cópia temp); o relatório do `auto_check` distingue visualmente WARN de BLOCK.

## Scope
- `tools/audit_resumos.py`: modelo de 2 severidades (BLOCK/WARN); remoção de `errors='ignore'`; checagem de frontmatter §5.2 (WARN) e de encoding ASCII (WARN); UnicodeDecodeError -> BLOCK.
- `tools/test_revisao_calibrada.py`: `test_roundtrip` isolado em cópia temp; guard de `import fsrs` com mensagem clara.
- `tools/auto_check.py`: apresentação de WARN vs BLOCK no relatório final (o exit code continua vindo dos sub-processos; auto_check não reimplementa a regra).

## Anti-scope
- **Sem** promover as regras novas (frontmatter, encoding) a BLOCK nesta parte -- warning-first é a decisão do usuário; a promoção acontece "quando a base zerar", fora daqui.
- **Sem** reescrever o motor do FSRS nem migrar toda a suíte para db temporário (só o `test_roundtrip`, que é o único write no db real; os demais são read-only).
- **Sem** mexer no pre-commit hook (já staged-only + quotepath-safe da Fase 0).
- **Sem** paridade de skills (Parte 3) nem checagem de drift no auto_check (Parte 3).

## Technical Decisions
- **Severidade como atributo do achado, não do arquivo:** cada issue carrega `sev in {BLOCK, WARN}`; `erros_encontrados` conta só BLOCK. Mais simples que dois passes; permite o mesmo arquivo ter WARN e BLOCK.
- **Cópia temp só no `test_roundtrip`:** migrar a suíte inteira seria refactor grande e desnecessário (os outros testes são read-only). Menor superfície de mudança, mesmo ganho de invariante ("suíte não muta db real").
- **Guard de fsrs na suíte, não no auto_check:** o ponto de falha é o `import app.utils.db` -> `fsrs`; a mensagem clara pertence a quem importa. auto_check apenas propaga o exit code.
- **Encoding como WARN, não BLOCK:** a base tem `←`/`…` legítimos preservados e pode ter débito legado; WARN evita travar commits não relacionados (decisão staged+warning-first).

## Applicable Patterns
- `clinical-summary-format.md` -- as regras BLOCK (Armadilhas, sem tabelas, sem emoji em header) são a materialização executável desse padrão; frontmatter §5.2 e encoding entram como WARN.
- `db-access-layer.md` -- writes de teste só em cópia temp; `import sqlite3` permanece restrito.

## Risks
- **WARN vira ruído se a base tiver muito débito legado** -> mitigação: reportar contagem agregada de WARN por tipo (não linha-a-linha) e deixar claro que não bloqueia.
- **Remover `errors='ignore'` pode BLOQUEAR um resumo com byte inválido preexistente** -> mitigação: rodar `auto_check --all` antes de fechar; se algum arquivo real quebrar, corrigir o encoding dele (é exatamente o defeito que o linter deveria pegar).
- **Guard de fsrs mascarar um erro real de import** -> mitigação: o guard só dispara em `ModuleNotFoundError: fsrs`, re-levanta o resto.

## Dependencies
Nenhuma. Independente das Partes 1, 3 e 4.
