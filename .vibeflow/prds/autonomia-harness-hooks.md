---
title: "Autonomous Harness & Proactive Linter Hooks Engine"
type: prd
status: approved
author: "Antigravity (MedHub Agentic Team)"
date: "2026-07-02"
---

# PRD: Autonomous Harness & Proactive Linter Hooks Engine

## 1. Problem Statement
O MedHub possui um ecossistema avançado de inteligência médica e educacional — incluindo calibração D10 de dificuldade, motor FSRS de revisão de flashcards, grade de cronograma canônico e linters estruturais para resumos (`tools/audit_resumos.py`). No entanto, o sistema padece de **falta de automatismo proativo, gatilhos autônomos e independência operacional**.

Atualmente:
1. **Validação Passiva:** A execução de linters e testes de calibração depende da vontade manual do agente ou do usuário em cada sessão. Se um resumo clínico é escrito com formatação incorreta (ex.: tabelas ASCII ou ausência de armadilhas de prova), o erro só é descoberto se alguém rodar o script explicitamente.
2. **Fragilidade de Encoding:** O linter atual (`tools/audit_resumos.py`) não reconfigura o *standard output* para UTF-8 no Windows, gerando falhas (`UnicodeEncodeError`) no console e não retornando código de erro (`sys.exit(1)`) para barrar execuções em falhas críticas.
3. **Ausência de Hooks no Ciclo de Vida (Git Hooks):** Não existe um mecanismo de interdição (pre-commit ou pre-push) que garanta que arquivos modificados em `resumos/` ou `tools/` sejam validados automaticamente antes da consolidação no controle de versão.
4. **Falta de Reflexo Autônomo Contratual:** O contrato canônico do agente (`AGENTE.md` e skills associadas) ainda não exige mecanicamente a autoverificação imediata e autônoma como condição sine qua non (*Definition of Done*) para encerramento de tarefas de edição de conteúdo ou código.

## 2. Goals (Objetivos)
- **G1 (Autonomia de Execução):** Criar o orquestrador inteligente `tools/auto_check.py`, capaz de detectar arquivos modificados via git (`--changed`) ou auditar o repositório inteiro (`--all`), roteando cada arquivo ao seu respectivo motor de auditoria (linter de resumos, testes de calibração, verificação de sintaxe).
- **G2 (Robustez e Resiliência no Linter):** Refatorar `tools/audit_resumos.py` para suportar checagem pontual por lista de argumentos, garantir compatibilidade nativa com UTF-8 em consoles Windows (`sys.stdout.reconfigure(encoding='utf-8')`) e emitir exit codes estritos (`sys.exit(1)` ao detectar erros críticos).
- **G3 (Blindagem por Gatilhos Git):** Implementar o instalador de hooks `tools/setup_hooks.py` e ativar o hook de pre-commit no repositório local, barrando automaticamente qualquer commit que viole as invariantes de estilo, estrutura ou calibração do MedHub.
- **G4 (Contrato de Reflexo Autônomo):** Instituir a regra canônica em `AGENTE.md` (§1.3 Reflexo Autônomo de Validação) e nas skills editoriais, obrigando o agente a acionar o harness autônomo e exibir o relatório verde antes de concluir qualquer intervenção.

## 3. Non-Goals (Fora do Escopo)
- Não alterar a grade canônica (`grade.json`) ou o motor matemático do FSRS.
- Não modificar o conteúdo clínico dos resumos já existentes na base que estejam validados (a menos que o linter aponte falhas que exijam adequação).

## 4. User Stories & Requirements

### US-1: Verificação Inteligente de Arquivos Modificados
- **Como** agente ou desenvolvedor atuando no MedHub,
- **Quero** rodar um comando simples (`python tools/auto_check.py --changed`) que identifique apenas os arquivos modificados na minha sessão e execute as verificações cabíveis,
- **Para que** eu tenha feedback instantâneo sobre a qualidade do meu trabalho sem precisar esperar a varredura dos mais de 60 resumos e 30 scripts do projeto.

### US-2: Blindagem Automática via Pre-Commit
- **Como** curador da base canônica do MedHub,
- **Quero** que um git hook de pre-commit intercepte minhas tentativas de commit, audite os resumos estaged e barre o commit com mensagens claras em caso de regressão,
- **Para que** o repositório nunca receba conteúdos que violem o contrato de resumos ou quebrem testes unitários.

### US-3: Reflexo Autônomo do Agente de IA
- **Como** usuário interagindo com o assistente Antigravity,
- **Quero** que o próprio assistente execute as ferramentas de validação proativamente assim que concluir uma edição de texto ou código,
- **Para que** ele se autocorrija de forma independente antes de me apresentar o resultado final.

## 5. Acceptance Criteria (Critérios de Aceitação - Definition of Done)
- **DoD-1 (audit_resumos.py):** Aceita arquivos individuais via CLI (`python tools/audit_resumos.py arquivo1.md arquivo2.md`); reconfigura sys.stdout para UTF-8 sem crash no Windows; retorna `exit(1)` se houver falhas críticas e `exit(0)` em aprovação.
- **DoD-2 (auto_check.py):** Implementa `--changed` (extraindo diff e untracked via git) e `--all`; executa verificação de resumos para arquivos `.md` em `resumos/` e suítes de teste de calibração para arquivos em `tools/`; reporta resumo executivo com código de saída estrito.
- **DoD-3 (setup_hooks.py):** Cria script executável em `.git/hooks/pre-commit` que invoca `python tools/auto_check.py --changed`; suporta flag `--install` e `--uninstall`; verificado em ambiente local.
- **DoD-4 (Suíte de Testes):** Criado `tools/test_autonomia_hooks.py` testando isoladamente os exit codes do linter, a lógica do auto-check e o ciclo de vida do instalador de hooks (com 100% de aprovação).
- **DoD-5 (Contrato AGENTE.md):** Cláusula §1.3 adicionada a `AGENTE.md` formalizando o Reflexo Autônomo de Validação.
