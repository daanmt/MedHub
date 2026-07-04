---
title: "Technical Specification: Autonomous Harness & Proactive Linter Hooks Engine"
type: spec
status: ready
relates_to: ["autonomia-harness-hooks.md"]
author: "Antigravity"
date: "2026-07-02"
---

# Technical Specification: Autonomous Harness & Proactive Linter Hooks Engine

## 1. Architectural Overview
A arquitetura do motor de autonomia proativa é composta por 4 camadas interconectadas que garantem validação em tempo real, interdição pré-commit e reflexo autônomo nas operações do agente:

```
[Agente / Usuário (Edição)]
       │
       ▼ (Reflexo Autônomo / Git Commit)
[tools/setup_hooks.py -> .git/hooks/pre-commit]
       │
       ▼
[tools/auto_check.py --changed / --all]
       │
       ├─► Arquivos resumos/**/*.md ─► [tools/audit_resumos.py <file1> <file2>]
       └─► Arquivos tools/**/*.py   ─► [tools/test_revisao_calibrada.py & test_autonomia_hooks.py]
       │
       ▼
[Exit Code 0 (Verde/Aprovado) vs Exit Code 1 (Interdição/Erro)]
```

## 2. Component Design & Detailed Specifications

### A. Refatoração do Linter de Resumos (`tools/audit_resumos.py`)
1. **Blindagem de Encoding (Windows Compat):**
   - No bloco inicial, aplicar `sys.stdout.reconfigure(encoding='utf-8')` (ou encapsulamento `io.TextIOWrapper` se Python $<3.7$, embora o ambiente use Python 3.12).
2. **Suporte a Argumentos na CLI:**
   - O `sys.argv[1:]` será verificado. Se fornecido, o linter validará apenas os arquivos listados nos argumentos (cujo caminho seja um `.md` existente).
   - Se nenhum argumento for fornecido, manter o comportamento original de varrer `resumos/**/*.md` recursivamente via `glob`.
3. **Mecanismo de Exit Code:**
   - O contador de `erros_encontrados` monitora falhas críticas (Seção "Armadilhas de Prova" ausente, Tabelas ASCII detectadas, Emojis em headers, Bullets proibidos).
   - Ao término da execução, se `erros_encontrados > 0`, executar `sys.exit(1)`. Caso contrário, executar `sys.exit(0)`. (Nota: avisos de estilo como ausência de marcadores visuais não geram `sys.exit(1)` para não bloquear commits em esboços, mas são reportados com destaque no terminal).

### B. Orquestrador Unificado de Autonomia (`tools/auto_check.py`)
1. **Modos de Operação (CLI Flags):**
   - `--changed`: Executa verificação incremental. Descobre arquivos modificados ou untracked utilizando subcomandos git:
     - `git diff --name-only HEAD` (arquivos modificados/estaged no commit atual).
     - `git ls-files --others --exclude-standard` (arquivos untracked novos).
   - `--all`: Executa varredura integral (todos os resumos + suítes centrais de testes).
2. **Roteamento Inteligente (Dispatch Logic):**
   - Filtrar a lista de arquivos alvo:
     - **Grupo Resumos:** Arquivos com extensão `.md` contidos no diretório `resumos/`. Se não vazio, disparar sub-processo: `python -X utf8 tools/audit_resumos.py <lista_de_resumos>`.
     - **Grupo Ferramentas/Core:** Arquivos com extensão `.py` contidos em `tools/` ou `core/`. Se não vazio (ou se modo `--all`), disparar a suíte central de calibração: `python -X utf8 tools/test_revisao_calibrada.py`.
3. **Consolidação de Relatório e Exit Code:**
   - Consolidar a saída no formato executivo:
     - `[AUTO-CHECK] Analisando X arquivos modificados...`
     - Status por módulo com ícones (`✅ PASSED` ou `❌ FAILED`).
   - Se qualquer um dos sub-processos disparados retornar código diferente de zero, o `auto_check.py` finaliza com `sys.exit(1)`.

### C. Instalador de Git Hooks (`tools/setup_hooks.py`)
1. **Lógica de Instalação (`--install` / padrão):**
   - Identificar a pasta do repositório `.git/hooks/`.
   - Gerar (ou sobrescrever com backup) o arquivo de hook `.git/hooks/pre-commit`.
   - Conteúdo do hook (plataforma híbrida bash/cmd ou chamador python):
     ```bash
     #!/bin/sh
     echo "[MedHub Hook] Executando auto-validação antes do commit..."
     python -X utf8 tools/auto_check.py --changed
     if [ $? -ne 0 ]; then
         echo "[MedHub Hook] ❌ Commit bloqueado! Corrija os erros acima antes de prosseguir."
         exit 1
     fi
     ```
   - No Linux/macOS ou Git Bash, aplicar permissão de execução (`chmod +x .git/hooks/pre-commit` via `os.chmod`).
2. **Lógica de Remoção (`--uninstall`):**
   - Remove o hook ou restaura o backup anterior se existir.

### D. Suíte de Testes do Harness (`tools/test_autonomia_hooks.py`)
Suíte automatizada com `unittest` verificando as invariantes:
- `test_linter_exit_code_failure`: Cria um arquivo `.md` temporário com tabela ASCII em `resumos/_test_tmp.md`, invoca `audit_resumos.py` sobre ele e assere que o return code é `1`.
- `test_linter_exit_code_success`: Invoca o linter sobre `resumos/Cirurgia/Quadril Pediátrico.md` (recém adequado) e assere return code `0`.
- `test_auto_check_routing`: Assere o roteamento de arquivos e a consolidação correta de exit codes no `auto_check.py`.
- `test_setup_hooks`: Verifica a criação real do arquivo `.git/hooks/pre-commit` e sua estrutura executável.

### E. Evolução do Contrato Canônico (`AGENTE.md`)
Acrescentar o artigo §1.3 ao contrato raiz do projeto:
> **§1.3 Reflexo Autônomo de Validação (Auto-Linter Reflex)**
> O agente é contratualmente proibido de encerrar uma sessão de trabalho em que tenha editado ou criado resumos clínicos (`resumos/*.md`) ou scripts estruturais (`tools/*.py`) sem antes executar o verificador proativo:
> `python -X utf8 tools/auto_check.py --changed`
> A obtenção do status verde (`✅ PASSED`) é condição indispensável para a consideração de entrega concluída (*Definition of Done*).

## 3. Implementation Steps
1. Editar `tools/audit_resumos.py` (adicionando encoding reconfigure, suporte a `sys.argv[1:]` e `sys.exit(1)`).
2. Criar `tools/auto_check.py`.
3. Criar `tools/setup_hooks.py` e rodar `--install` para ativar o git hook no ambiente local.
4. Criar e executar `tools/test_autonomia_hooks.py`.
5. Atualizar `AGENTE.md` e a skill `source-command-estilo-resumo/SKILL.md`.
6. Auditar a execução pontual e global no terminal para certificar a autonomia mecânica.
